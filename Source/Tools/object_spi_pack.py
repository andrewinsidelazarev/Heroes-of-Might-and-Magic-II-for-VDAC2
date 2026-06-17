#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

from agg_tools import read_agg_index, read_agg_index_with_expansion
from object_atlas import ICN_BY_OBJECT_TYPE, agg_entry, decode_icn_sprite, read_icn, read_palette
from terrain_preview import TILE_PX, VIEW_H, VIEW_W, read_map


ROOT = Path(__file__).resolve().parents[2]
SCREEN_W = VIEW_W + 1
SCREEN_H = VIEW_H + 1
OBJECT_CACHE_RAMG = 0x070000
OBJECT_DL_RAMG = 0x0E0FC0
OBJECT_TRANSPARENT_INDEX = 0
OBJECT_PALETTE_SIZE = 512
DYNAMIC_VISUAL_ICNS = {
    "FLAG32.ICN",
    "OBJNARTI.ICN",
    "OBJNRSRC.ICN",
    "MONS32.ICN",
}
DISPLAY_SCALE_NUM = 8
DISPLAY_SCALE_DEN = 5
DISPLAY_BITMAP_TRANSFORM = (256 * DISPLAY_SCALE_DEN) // DISPLAY_SCALE_NUM

FT_BITMAPS = 1
FT_ARGB4 = 6
FT_NEAREST = 0
FT_BORDER = 0
FT_ONE = 1
FT_SRC_ALPHA = 2
FT_ONE_MINUS_SRC_ALPHA = 4


def cmd(value: int) -> bytes:
    return struct.pack("<I", value & 0xFFFFFFFF)


def c_display() -> bytes:
    return cmd(0 << 24)


def c_bitmap_source(addr: int) -> bytes:
    return cmd((1 << 24) | (addr & 0xFFFFF))


def c_color_rgb(r: int, g: int, b: int) -> bytes:
    return cmd((4 << 24) | ((r & 255) << 16) | ((g & 255) << 8) | (b & 255))


def c_bitmap_handle(handle: int) -> bytes:
    return cmd((5 << 24) | (handle & 31))


def c_cell(cell: int) -> bytes:
    return cmd((6 << 24) | (cell & 127))


def c_bitmap_layout(fmt: int, stride: int, height: int) -> bytes:
    return cmd((7 << 24) | ((fmt & 31) << 19) | ((stride & 1023) << 9) | (height & 511))


def c_bitmap_size(width: int, height: int) -> bytes:
    return cmd((8 << 24) | ((FT_NEAREST & 1) << 20) | ((FT_BORDER & 1) << 19) | ((FT_BORDER & 1) << 18) | ((width & 511) << 9) | (height & 511))


def c_blend_func(src: int, dst: int) -> bytes:
    return cmd((11 << 24) | ((src & 7) << 3) | (dst & 7))


def c_color_a(alpha: int) -> bytes:
    return cmd((16 << 24) | (alpha & 255))


def c_bitmap_transform_a(value: int) -> bytes:
    return cmd((21 << 24) | (value & 0x1FFFF))


def c_bitmap_transform_e(value: int) -> bytes:
    return cmd((25 << 24) | (value & 0x1FFFF))


def c_begin(prim: int) -> bytes:
    return cmd((31 << 24) | (prim & 15))


def c_end() -> bytes:
    return cmd(33 << 24)


def c_palette_source(addr: int) -> bytes:
    return cmd((42 << 24) | (addr & 0x3FFFFF))


def c_vertex2f(x: int, y: int) -> bytes:
    return cmd((64 << 24) | ((x & 32767) << 15) | (y & 32767))


def align(value: int, step: int) -> int:
    return (value + step - 1) & ~(step - 1)


def scaled_vertex2f_units(value: int) -> int:
    return (value * DISPLAY_SCALE_NUM * 16 + DISPLAY_SCALE_DEN // 2) // DISPLAY_SCALE_DEN


def scaled_size(value: int) -> int:
    return (value * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN


def palette_argb4444(palette) -> bytes:
    out = bytearray()
    for i, (r, g, b) in enumerate(palette):
        alpha = 0 if i == OBJECT_TRANSPARENT_INDEX else 15
        value = ((alpha & 15) << 12) | ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4)
        out.extend((value & 0xFF, value >> 8))
    return bytes(out)


def decode_icn_indices(header, data: bytes) -> bytes:
    w = header["w"]
    h = header["h"]
    pixels = [OBJECT_TRANSPARENT_INDEX] * (w * h)
    pos_x = 0
    row = 0
    p = 0
    mono = bool(header["frames"] & 0x20)
    while p < len(data) and row < h:
        code = data[p]
        p += 1
        if code == 0x00:
            row += 1
            pos_x = 0
            continue
        if code == 0x80:
            break
        base = row * w + pos_x
        if mono:
            if code < 0x80:
                for i in range(code):
                    if 0 <= base + i < len(pixels):
                        pixels[base + i] = 1
                pos_x += code
            else:
                pos_x += code - 0x80
            continue
        if code < 0x80:
            count = code
            chunk = data[p:p + count]
            p += len(chunk)
            for i, pix in enumerate(chunk):
                if 0 <= base + i < len(pixels):
                    pixels[base + i] = pix
            pos_x += count
        elif code < 0xC0:
            pos_x += code - 0x80
        elif code == 0xC0:
            if p >= len(data):
                break
            transform = data[p]
            p += 1
            count = transform & 0x03
            if count == 0:
                if p >= len(data):
                    break
                count = data[p]
                p += 1
            pos_x += count
        else:
            if code == 0xC1:
                if p >= len(data):
                    break
                count = data[p]
                p += 1
            else:
                count = code - 0xC0
            if p >= len(data):
                break
            pix = data[p]
            p += 1
            for i in range(count):
                if 0 <= base + i < len(pixels):
                    pixels[base + i] = pix
            pos_x += count
    return bytes(pixels)


def add_part(parts: list[dict], tile_x: int, tile_y: int, layer: int, uid: int, object_name: int, index: int, top: bool) -> None:
    icn_type = object_name >> 2
    icn_name = ICN_BY_OBJECT_TYPE.get(icn_type)
    if icn_name and index != 0xFF:
        parts.append({"tile_x": tile_x, "tile_y": tile_y, "icn": icn_name, "index": index, "object_name": object_name, "layer": layer, "uid": uid, "top": top})


def dynamic_object_parts(parts: list[dict]) -> list[dict]:
    return [part for part in parts if part["icn"].upper() in DYNAMIC_VISUAL_ICNS]


def object_parts_for_origin(width: int, height: int, map_data, origin_x: int, origin_y: int) -> list[dict]:
    tiles, addons = map_data if isinstance(map_data, tuple) else (map_data, [])
    parts: list[dict] = []
    for sy in range(SCREEN_H):
        my = origin_y + sy
        if my >= height:
            continue
        for sx in range(SCREEN_W):
            mx = origin_x + sx
            if mx >= width:
                continue
            tile = tiles[my * width + mx]
            add_part(parts, sx, sy, tile["quantity1"] & 0x03, tile["uid1"], tile["object_name1"], tile["bottom_icn"], False)
            add_part(parts, sx, sy, 0, tile["uid2"], tile["object_name2"], tile["top_icn"], True)
            addon_index = tile.get("next_addon", 0)
            guard = 0
            while addon_index > 0 and addon_index < len(addons) and guard < 128:
                addon = addons[addon_index]
                add_part(parts, sx, sy, addon["quantity"] & 0x03, addon["uid1"], addon["object_name1"], addon["bottom_icn"], False)
                add_part(parts, sx, sy, 0, addon["uid2"], addon["object_name2"], addon["top_icn"], True)
                addon_index = addon["next_addon"]
                guard += 1
    ground = [part for part in parts if not part["top"]]
    top = [part for part in parts if part["top"]]
    ground.sort(key=lambda item: item["layer"], reverse=True)
    return dynamic_object_parts(ground + top)


def build_origin_pack(agg_data: bytes, entries, palette, icn_cache: dict, width: int, height: int, map_data, origin_x: int, origin_y: int):
    parts = object_parts_for_origin(width, height, map_data, origin_x, origin_y)
    sprite_cache: dict[tuple[str, int], dict] = {}
    sprite_blob = bytearray()
    placements = []
    for part in parts:
        key = (part["icn"], part["index"])
        if key not in sprite_cache:
            if part["icn"] not in icn_cache:
                icn_cache[part["icn"]] = read_icn(agg_entry(agg_data, entries, part["icn"]))
            sprites = icn_cache[part["icn"]]
            if part["index"] >= len(sprites):
                continue
            header, encoded = sprites[part["index"]]
            if header["w"] == 0 or header["h"] == 0:
                continue
            offset = align(len(sprite_blob), 4)
            while len(sprite_blob) < offset:
                sprite_blob.append(0)
            raw = decode_icn_sprite(header, encoded, palette)
            sprite_blob.extend(raw)
            sprite_cache[key] = {"offset": offset, "w": header["w"], "h": header["h"], "ox": header["ox"], "oy": header["oy"], "stride": header["w"] * 2}
        sprite = sprite_cache.get(key)
        if not sprite:
            continue
        placements.append({
            **sprite,
            "x": part["tile_x"] * TILE_PX + sprite["ox"],
            "y": part["tile_y"] * TILE_PX + sprite["oy"],
        })

    dl = bytearray()
    if placements:
        dl.extend(c_color_rgb(255, 255, 255))
        dl.extend(c_color_a(255))
        dl.extend(c_blend_func(FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA))
        dl.extend(c_bitmap_handle(2))
        dl.extend(c_cell(0))
        dl.extend(c_begin(FT_BITMAPS))
        for item in placements:
            dl.extend(c_bitmap_source(OBJECT_CACHE_RAMG + item["offset"]))
            dl.extend(c_bitmap_layout(FT_ARGB4, item["stride"], item["h"]))
            dl.extend(c_bitmap_size(scaled_size(item["w"]), scaled_size(item["h"])))
            dl.extend(c_bitmap_transform_a(DISPLAY_BITMAP_TRANSFORM))
            dl.extend(c_bitmap_transform_e(DISPLAY_BITMAP_TRANSFORM))
            dl.extend(c_vertex2f(scaled_vertex2f_units(item["x"]), scaled_vertex2f_units(item["y"])))
        dl.extend(c_end())
        dl.extend(c_blend_func(FT_ONE, 0))

    header = struct.pack("<4sHHHHHIIHH", b"H2OB", 1, origin_x, origin_y, len(parts), len(sprite_cache), len(sprite_blob), len(dl), OBJECT_CACHE_RAMG & 0xFFFF, OBJECT_DL_RAMG & 0xFFFF)
    return header + bytes(sprite_blob) + bytes(dl), {
        "origin": [origin_x, origin_y],
        "parts": len(parts),
        "unique_sprites": len(sprite_cache),
        "sprite_bytes": len(sprite_blob),
        "dl_bytes": len(dl),
        "total_bytes": len(header) + len(sprite_blob) + len(dl),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Собрать SPI object packs для adventure map HMM2.")
    parser.add_argument("--agg", type=Path, default=ROOT / "Assets" / "Original" / "DATA" / "HEROES2.AGG")
    parser.add_argument("--map", type=Path, default=ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.map.bin")
    parser.add_argument("--out", type=Path, default=ROOT / "Assets" / "Converted" / "ObjectPacks" / "SKIRMISH_OBJECTS_SPI.pack")
    parser.add_argument("--manifest", type=Path, default=ROOT / "Assets" / "Converted" / "ObjectPacks" / "SKIRMISH_OBJECTS_SPI.json")
    args = parser.parse_args()

    agg_data, entries = read_agg_index_with_expansion(args.agg)
    palette = read_palette(agg_entry(agg_data, entries, "KB.PAL"))
    width, height, map_data = read_map(args.map)
    count_x = width - VIEW_W + 1
    count_y = height - VIEW_H + 1
    entries_table = []
    packs = bytearray()
    rows = []
    icn_cache = {}

    for oy in range(count_y):
        for ox in range(count_x):
            pack, info = build_origin_pack(agg_data, entries, palette, icn_cache, width, height, map_data, ox, oy)
            entries_table.append((len(packs), len(pack)))
            packs.extend(pack)
            rows.append(info)

    header_size = 32
    table_size = len(entries_table) * 8
    data_offset = header_size + table_size
    out = bytearray()
    out.extend(struct.pack("<4sHHHHHIIII", b"H2OP", 1, width, height, count_x, count_y, len(entries_table), data_offset, OBJECT_CACHE_RAMG, OBJECT_DL_RAMG))
    for offset, size in entries_table:
        out.extend(struct.pack("<II", data_offset + offset, size))
    out.extend(packs)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(out)
    worst = max(rows, key=lambda item: item["total_bytes"])
    args.manifest.write_text(json.dumps({
        "pack": args.out.as_posix(),
        "map_size": [width, height],
        "origin_count": [count_x, count_y],
        "entry_count": len(entries_table),
        "total_bytes": len(out),
        "object_cache_ramg": OBJECT_CACHE_RAMG,
        "object_dl_ramg": OBJECT_DL_RAMG,
        "format": "dynamic object sprites ARGB4",
        "worst": worst,
        "entries": rows,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"object SPI pack: {args.out} bytes={len(out)} entries={len(entries_table)}")
    print(f"worst origin={worst['origin'][0]},{worst['origin'][1]} parts={worst['parts']} unique={worst['unique_sprites']} sprites={worst['sprite_bytes']} dl={worst['dl_bytes']} total={worst['total_bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
