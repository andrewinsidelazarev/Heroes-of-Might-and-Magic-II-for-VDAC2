#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import os
import struct
from pathlib import Path

from agg_tools import read_agg_index
from terrain_preview import TILE_PX, VIEW_H, VIEW_W, read_map


PAGE_SIZE = 0x4000
RAMG_OBJECT_BASE = 0x03A800
OBJECT_PAGE_BASE = 0x30
ENABLE_OBJECT_LAYER = os.environ.get("HMM2_OBJECT_LAYER", "1") == "1"
ENABLE_DECORATION_LAYER = os.environ.get("HMM2_OBJECT_DECOR", "0") == "1"

ICN_BY_OBJECT_TYPE = {
    6: "BOAT32.ICN",
    10: "OBJNHAUN.ICN",
    11: "OBJNARTI.ICN",
    12: "MONS32.ICN",
    14: "FLAG32.ICN",
    20: "MINIMON.ICN",
    21: "MINIHERO.ICN",
    22: "MTNSNOW.ICN",
    23: "MTNSWMP.ICN",
    24: "MTNLAVA.ICN",
    25: "MTNDSRT.ICN",
    26: "MTNDIRT.ICN",
    27: "MTNMULT.ICN",
    29: "EXTRAOVR.ICN",
    30: "ROAD.ICN",
    31: "MTNCRCK.ICN",
    32: "MTNGRAS.ICN",
    33: "TREJNGL.ICN",
    34: "TREEVIL.ICN",
    35: "OBJNTOWN.ICN",
    36: "OBJNTWBA.ICN",
    37: "OBJNTWSH.ICN",
    38: "OBJNTWRD.ICN",
    39: "OBJNXTRA.ICN",
    40: "OBJNWAT2.ICN",
    41: "OBJNMUL2.ICN",
    42: "TRESNOW.ICN",
    43: "TREFIR.ICN",
    44: "TREFALL.ICN",
    45: "STREAM.ICN",
    46: "OBJNRSRC.ICN",
    48: "OBJNGRA2.ICN",
    49: "TREDECI.ICN",
    50: "OBJNWATR.ICN",
    51: "OBJNGRAS.ICN",
    52: "OBJNSNOW.ICN",
    53: "OBJNSWMP.ICN",
    54: "OBJNLAVA.ICN",
    55: "OBJNDSRT.ICN",
    56: "OBJNDIRT.ICN",
    57: "OBJNCRCK.ICN",
    58: "OBJNLAV3.ICN",
    59: "OBJNMULT.ICN",
    60: "OBJNLAV2.ICN",
    61: "X_LOC1.ICN",   # объекты дополнения PoL (в HEROES2X.AGG)
    62: "X_LOC2.ICN",
    63: "X_LOC3.ICN",
}

SEMANTIC_ICNS = {
    "OBJNARTI.ICN",
    "MONS32.ICN",
    "FLAG32.ICN",
    "MINIHERO.ICN",
    "OBJNTOWN.ICN",
    "OBJNTWRD.ICN",
    "OBJNRSRC.ICN",
}

DECORATION_ICNS = {
    "MTNSNOW.ICN",
    "MTNSWMP.ICN",
    "MTNLAVA.ICN",
    "MTNDSRT.ICN",
    "MTNDIRT.ICN",
    "MTNMULT.ICN",
    "MTNCRCK.ICN",
    "MTNGRAS.ICN",
    "TREJNGL.ICN",
    "TREEVIL.ICN",
    "TRESNOW.ICN",
    "TREFIR.ICN",
    "TREFALL.ICN",
    "OBJNGRAS.ICN",
    "OBJNSNOW.ICN",
    "OBJNSWMP.ICN",
    "OBJNLAVA.ICN",
    "OBJNDSRT.ICN",
    "OBJNDIRT.ICN",
    "OBJNCRCK.ICN",
}


def agg_entry(data: bytes, entries, name: str) -> bytes:
    name_u = name.upper()
    for entry in entries:
        if entry["name"].upper() != name_u:
            continue
        if not entry["hash_ok"]:
            raise ValueError(f"{name}: ошибка хэша AGG")
        start = entry["offset"]
        return data[start:start + entry["size"]]
    raise ValueError(f"{name}: нет в AGG")


def read_palette(raw: bytes):
    if len(raw) != 768:
        raise ValueError(f"KB.PAL: неверный размер {len(raw)}")
    return [(min(raw[i] << 2, 255), min(raw[i + 1] << 2, 255), min(raw[i + 2] << 2, 255)) for i in range(0, 768, 3)]


def read_icn(raw: bytes):
    if len(raw) < 6:
        raise ValueError("ICN слишком короткий")
    count, total_size = struct.unpack_from("<HI", raw, 0)
    headers = []
    off = 6
    for _ in range(count):
        if off + 13 > len(raw):
            raise ValueError("ICN: обрезана таблица заголовков")
        ox, oy, w, h, frames, data_off = struct.unpack_from("<hhHHBI", raw, off)
        headers.append({"ox": ox, "oy": oy, "w": w, "h": h, "frames": frames, "data_off": data_off})
        off += 13
    begin = 6
    sprites = []
    for i, header in enumerate(headers):
        start = begin + header["data_off"]
        next_off = headers[i + 1]["data_off"] if i + 1 < len(headers) else total_size
        end = begin + next_off
        if start > len(raw) or end > len(raw) or end < start:
            raise ValueError("ICN: неверный диапазон данных")
        sprites.append((header, raw[start:end]))
    return sprites


def decode_icn_planes(header, data: bytes):
    """RLE-декод ICN-кадра в (pixels, alpha): pixels — индексы палитры (0=прозр.),
    alpha — 0/15. Общая основа для ARGB4 (decode_icn_sprite) и paletted-выдачи
    (decode_icn_paletted). Логика идентична прежней decode_icn_sprite."""
    w = header["w"]
    h = header["h"]
    pixels = [0] * (w * h)
    alpha = [0] * (w * h)
    pos_x = 0
    row = 0
    p = 0
    mono = bool(header["frames"] & 0x20)
    while p < len(data) and row < h:
        cmd = data[p]
        p += 1
        if cmd == 0x00:
            row += 1
            pos_x = 0
            continue
        if cmd == 0x80:
            break
        base = row * w + pos_x
        if mono:
            if cmd < 0x80:
                count = cmd
                for i in range(count):
                    if 0 <= base + i < len(pixels):
                        pixels[base + i] = 0
                        alpha[base + i] = 15
                pos_x += count
            else:
                pos_x += cmd - 0x80
            continue
        if cmd < 0x80:
            count = cmd
            chunk = data[p:p + count]
            p += len(chunk)
            for i, pix in enumerate(chunk):
                if 0 <= base + i < len(pixels):
                    pixels[base + i] = pix
                    alpha[base + i] = 0 if pix == 0 else 15
            pos_x += count
        elif cmd < 0xC0:
            pos_x += cmd - 0x80
        elif cmd == 0xC0:
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
            if cmd == 0xC1:
                if p >= len(data):
                    break
                count = data[p]
                p += 1
            else:
                count = cmd - 0xC0
            if p >= len(data):
                break
            pix = data[p]
            p += 1
            for i in range(count):
                if 0 <= base + i < len(pixels):
                    pixels[base + i] = pix
                    alpha[base + i] = 0 if pix == 0 else 15
            pos_x += count

    return pixels, alpha


def decode_icn_sprite(header, data: bytes, palette):
    """ARGB4444 (2 байта/px) — формат оверлей-спрайтов объектов/актёра."""
    pixels, alpha = decode_icn_planes(header, data)
    out = bytearray()
    for pix, a in zip(pixels, alpha):
        r, g, b = palette[pix]
        value = ((a & 15) << 12) | ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4)
        out.extend((value & 0xFF, value >> 8))
    return bytes(out)


def decode_icn_paletted(header, data: bytes):
    """PALETTED4444 (1 байт/px = индекс палитры) для анимир. кадров объектов.
    Прозрачность через палитру (index 0 = alpha 0), как у ARGB4-декода
    (там alpha=0 ⟺ pix==0). mono-кадры (тень, frames&0x20) тут не поддержаны:
    они pixels=0/alpha=15 → стали бы прозрачными; вызывающий обязан отсеять mono.
    Возвращает (bytes(indices), is_mono)."""
    is_mono = bool(header["frames"] & 0x20)
    pixels, alpha = decode_icn_planes(header, data)
    idx = bytes(pix if a else 0 for pix, a in zip(pixels, alpha))
    return idx, is_mono


def add_part(out, tile_x, tile_y, layer, uid, object_name, index, allowed_icns):
    icn_type = object_name >> 2
    icn_name = ICN_BY_OBJECT_TYPE.get(icn_type)
    if not icn_name or index == 0xFF:
        return
    active_icns = SEMANTIC_ICNS | (DECORATION_ICNS if ENABLE_DECORATION_LAYER else set())
    if icn_name not in active_icns:
        return
    if layer > 1:
        return
    if allowed_icns is not None and icn_name not in allowed_icns:
        return
    out.append({"tile_x": tile_x, "tile_y": tile_y, "icn": icn_name, "index": index, "type": icn_type, "layer": layer, "uid": uid})


def tile_object_parts(tile, addons, tile_x, tile_y, allowed_icns):
    ground = []
    top = []
    add_part(ground, tile_x, tile_y, tile["quantity1"] & 0x03, tile["uid1"], tile["object_name1"], tile["bottom_icn"], allowed_icns)
    add_part(top, tile_x, tile_y, 0, tile["uid2"], tile["object_name2"], tile["top_icn"], allowed_icns)

    addon_index = tile.get("next_addon", 0)
    guard = 0
    while addon_index > 0 and addon_index < len(addons) and guard < 128:
        addon = addons[addon_index]
        add_part(ground, tile_x, tile_y, addon["quantity"] & 0x03, addon["uid1"], addon["object_name1"], addon["bottom_icn"], allowed_icns)
        add_part(top, tile_x, tile_y, 0, addon["uid2"], addon["object_name2"], addon["top_icn"], allowed_icns)
        addon_index = addon["next_addon"]
        guard += 1

    ground.sort(key=lambda item: item["layer"], reverse=True)
    return ground + top


def visible_objects(width: int, height: int, map_data, origin_x: int, origin_y: int):
    if not ENABLE_OBJECT_LAYER:
        return []
    allow = os.environ.get("HMM2_OBJECT_ICNS")
    allowed_icns = None
    if allow:
        allowed_icns = {item.strip().upper() if item.strip().upper().endswith(".ICN") else item.strip().upper() + ".ICN" for item in allow.split(",") if item.strip()}
    if isinstance(map_data, tuple):
        tiles, addons = map_data
    else:
        tiles, addons = map_data, []
    objects = []
    for y in range(VIEW_H):
        my = origin_y + y
        if my >= height:
            continue
        for x in range(VIEW_W):
            mx = origin_x + x
            if mx >= width:
                continue
            tile = tiles[my * width + mx]
            objects.extend(tile_object_parts(tile, addons, x, y, allowed_icns))
    return objects


def align(value: int, step: int) -> int:
    return (value + step - 1) & ~(step - 1)


def write_chunks(out_dir: Path, payload: bytes):
    out_dir.mkdir(parents=True, exist_ok=True)
    for old_chunk in out_dir.glob("SKIRMISH_OBJECTS_p*.bin"):
        old_chunk.unlink()
    chunks = []
    for i in range(math.ceil(len(payload) / PAGE_SIZE)):
        chunk = payload[i * PAGE_SIZE:(i + 1) * PAGE_SIZE]
        padded = chunk + b"\0" * (PAGE_SIZE - len(chunk))
        path = out_dir / f"SKIRMISH_OBJECTS_p{i:02d}.bin"
        path.write_bytes(padded)
        chunks.append((path, len(chunk)))
    return chunks


def write_objects_inc(path: Path, chunks, total_size: int):
    lines = [
        "; Сгенерировано Source/Tools/object_atlas.py",
        "",
        f"OBJECT_ATLAS_RAMG       EQU #{RAMG_OBJECT_BASE:06X}",
        f"OBJECT_ATLAS_PAGE_BASE  EQU #{OBJECT_PAGE_BASE:02X}",
        f"OBJECT_ATLAS_PAGE_COUNT EQU {len(chunks)}",
        f"OBJECT_ATLAS_SIZE       EQU {total_size}",
        "",
        "Objects_Upload:",
        "                GetPage3",
        "                LD   (.RestorePage), A",
    ]
    ramg = RAMG_OBJECT_BASE
    for i, (_, real_size) in enumerate(chunks):
        lines.extend(
            [
                f"                SetPage3 #{OBJECT_PAGE_BASE + i:02X}",
                "                LD   HL, #C000",
                f"                LD   A, #{(ramg >> 16) & 0xFF:02X}",
                f"                LD   DE, #{ramg & 0xFFFF:04X}",
                f"                LD   BC, {real_size}",
                "                CALL FT.WriteMem",
            ]
        )
        ramg += real_size
    lines.extend(
        [
            ".RestorePage    EQU $+1",
            "                LD   A, #00",
            "                SetPage3_A",
            "                RET",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def patch_display_list(path: Path, placements):
    text = path.read_text(encoding="utf-8")
    if "                FT_DISPLAY" not in text:
        raise ValueError("generated_adventure_dl.inc: нет FT_DISPLAY")
    head = text.split("                FT_DISPLAY", 1)[0].rstrip()
    lines = [head, "", "; Объектный слой: реальные ICN-спрайты HMM2 в ARGB4."]
    if placements:
        lines.extend(
            [
                "                FT_COLOR_RGB 255, 255, 255",
                "                FT_COLOR_A 255",
                "                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA",
                "                FT_BEGIN FT_BITMAPS",
            ]
        )
        for item in placements:
            lines.extend(
                [
                    f"                FT_BITMAP_SOURCE #{item['addr']:06X}",
                    f"                FT_BITMAP_LAYOUT FT_ARGB4, {item['w'] * 2}, {item['h']}",
                    f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {item['w']}, {item['h']}",
                    f"                FT_VERTEX2F {item['x'] * 16}, {item['y'] * 16}",
                ]
            )
        lines.append("                FT_END")
        lines.append("                FT_BLEND_FUNC FT_ONE, FT_ZERO")
    lines.extend(["                FT_DISPLAY", "ADVENTURE_DL_SIZE EQU $ - ADVENTURE_DL", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def update_spgbld(path: Path, chunks):
    text = path.read_text(encoding="utf-8")
    text = text.split("; Страницы object atlas.", 1)[0].rstrip()
    lines = [text, "", "; Страницы object atlas."]
    for i, (chunk_path, _) in enumerate(chunks):
        lines.append(f"Block = #0000, #{OBJECT_PAGE_BASE + i:02X}, {chunk_path.as_posix()}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_preview(path: Path, terrain_preview: Path, placements, payload: bytes):
    try:
        from PIL import Image
    except ImportError:
        return
    base = Image.open(terrain_preview).convert("RGBA") if terrain_preview.exists() else Image.new("RGBA", (VIEW_W * TILE_PX, VIEW_H * TILE_PX), (0, 0, 0, 255))
    for item in placements:
        sprite = Image.new("RGBA", (item["w"], item["h"]))
        pixels = []
        off = item["addr"] - RAMG_OBJECT_BASE
        for i in range(item["w"] * item["h"]):
            value = payload[off + i * 2] | (payload[off + i * 2 + 1] << 8)
            a = ((value >> 12) & 15) * 17
            r = ((value >> 8) & 15) * 17
            g = ((value >> 4) & 15) * 17
            b = (value & 15) * 17
            pixels.append((r, g, b, a))
        sprite.putdata(pixels)
        base.alpha_composite(sprite, (item["x"], item["y"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(path)


def main():
    parser = argparse.ArgumentParser(description="Собрать объектный слой HMM2 ICN для FT812.")
    parser.add_argument("--agg", type=Path, default=Path("Assets/Original/DATA/HEROES2.AGG"))
    parser.add_argument("--map", type=Path, default=Path("Assets/Converted/Maps/SKIRMISH.map.bin"))
    parser.add_argument("--out-dir", type=Path, default=Path("Assets/Converted/Objects"))
    parser.add_argument("--objects-inc", type=Path, default=Path("Source/ASM/generated_objects.inc"))
    parser.add_argument("--dl-inc", type=Path, default=Path("Source/ASM/generated_adventure_dl.inc"))
    parser.add_argument("--spgbld", type=Path, default=Path("spgbld_vdac2.ini"))
    parser.add_argument("--preview", type=Path, default=Path("Diagnostics/objects_preview.png"))
    parser.add_argument("--terrain-preview", type=Path, default=Path("Diagnostics/terrain_ground32_preview.png"))
    parser.add_argument("--origin-x", type=int, default=0)
    parser.add_argument("--origin-y", type=int, default=0)
    args = parser.parse_args()

    agg_data, entries = read_agg_index(args.agg)
    palette = read_palette(agg_entry(agg_data, entries, "KB.PAL"))
    width, height, map_data = read_map(args.map)
    objects = visible_objects(width, height, map_data, args.origin_x, args.origin_y)

    icn_cache = {}
    payload = bytearray()
    sprite_cache = {}
    placements = []
    for obj in objects:
        key = (obj["icn"], obj["index"])
        if key not in sprite_cache:
            if obj["icn"] not in icn_cache:
                icn_cache[obj["icn"]] = read_icn(agg_entry(agg_data, entries, obj["icn"]))
            sprites = icn_cache[obj["icn"]]
            if obj["index"] >= len(sprites):
                continue
            header, encoded = sprites[obj["index"]]
            if header["w"] == 0 or header["h"] == 0:
                continue
            addr = RAMG_OBJECT_BASE + align(len(payload), 4)
            while RAMG_OBJECT_BASE + len(payload) < addr:
                payload.append(0)
            raw = decode_icn_sprite(header, encoded, palette)
            payload.extend(raw)
            sprite_cache[key] = {"addr": addr, "w": header["w"], "h": header["h"], "ox": header["ox"], "oy": header["oy"]}
        sprite = sprite_cache[key]
        placements.append(
            {
                **sprite,
                "x": obj["tile_x"] * TILE_PX + sprite["ox"],
                "y": obj["tile_y"] * TILE_PX + sprite["oy"],
                "icn": obj["icn"],
                "index": obj["index"],
            }
        )

    chunks = write_chunks(args.out_dir, bytes(payload)) if payload else []
    write_objects_inc(args.objects_inc, chunks, len(payload))
    patch_display_list(args.dl_inc, placements)
    update_spgbld(args.spgbld, chunks)
    write_preview(args.preview, args.terrain_preview, placements, bytes(payload))

    print(f"объекты viewport: {len(objects)}, размещено: {len(placements)}, уникальных спрайтов: {len(sprite_cache)}")
    print(f"object atlas: {len(payload)} байт, страниц: {len(chunks)}, базовая page: #{OBJECT_PAGE_BASE:02X}")
    print(f"предпросмотр: {args.preview}")


if __name__ == "__main__":
    main()
