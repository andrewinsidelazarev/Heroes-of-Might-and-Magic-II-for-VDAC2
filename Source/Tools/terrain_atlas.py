#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import struct
from pathlib import Path

from agg_tools import read_agg_index
from terrain_preview import HEADER_SIZE, TILE_SIZE, TILE_PX, VIEW_H, VIEW_W, read_map


PAGE_SIZE = 0x4000
RAMG_TERRAIN_BASE = 0x000000
TERRAIN_PAGE_BASE = 0x20


def agg_entry(data: bytes, entries, name: str) -> bytes:
    name_u = name.upper()
    for entry in entries:
        if entry["name"].upper() != name_u:
            continue
        if not entry["hash_ok"]:
            raise ValueError(f"{name}: ошибка хэша AGG")
        start = entry["offset"]
        end = start + entry["size"]
        return data[start:end]
    raise ValueError(f"{name}: нет в AGG")


def read_til(raw: bytes):
    if len(raw) < 6:
        raise ValueError("GROUND32.TIL слишком короткий")
    count, width, height = struct.unpack_from("<HHH", raw, 0)
    size = width * height
    expected = 6 + count * size
    if width != TILE_PX or height != TILE_PX:
        raise ValueError(f"ожидался TIL 32x32, получен {width}x{height}")
    if len(raw) < expected:
        raise ValueError("GROUND32.TIL обрезан")
    tiles = []
    off = 6
    for _ in range(count):
        tiles.append(raw[off:off + size])
        off += size
    return tiles


def read_palette(raw: bytes):
    if len(raw) != 768:
        raise ValueError(f"KB.PAL: неверный размер {len(raw)}")
    return [(min(raw[i] << 2, 255), min(raw[i + 1] << 2, 255), min(raw[i + 2] << 2, 255)) for i in range(0, 768, 3)]


def rgb565_le(rgb):
    r, g, b = rgb
    value = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
    return bytes((value & 0xFF, value >> 8))


def transform_tile(tile: bytes, shape: int) -> bytes:
    # В MP2/fheroes2: bit0 = vertical flip, bit1 = horizontal flip.
    vflip = bool(shape & 1)
    hflip = bool(shape & 2)
    out = bytearray(TILE_PX * TILE_PX)
    for y in range(TILE_PX):
        sy = TILE_PX - 1 - y if vflip else y
        for x in range(TILE_PX):
            sx = TILE_PX - 1 - x if hflip else x
            out[y * TILE_PX + x] = tile[sy * TILE_PX + sx]
    return bytes(out)


def to_rgb565(tile: bytes, palette) -> bytes:
    out = bytearray()
    for pix in tile:
        out.extend(rgb565_le(palette[pix]))
    return bytes(out)


def visible_cells(width: int, height: int, tiles, origin_x: int, origin_y: int):
    cells = []
    for y in range(VIEW_H):
        my = origin_y + y
        if my >= height:
            continue
        for x in range(VIEW_W):
            mx = origin_x + x
            if mx >= width:
                continue
            tile = tiles[my * width + mx]
            cells.append((x, y, tile["terrain"], tile["terrain_flags"] & 3))
    return cells


def write_preview_png(path: Path, atlas: bytes, cells, remap, palette=None, tile_bytes: int | None = None, tile_base: int = 0):
    try:
        from PIL import Image
    except ImportError:
        return
    img = Image.new("RGB", (VIEW_W * TILE_PX, VIEW_H * TILE_PX), (0, 0, 0))
    for x, y, terrain, shape in cells:
        cell = remap[(terrain, shape)]
        if tile_bytes is None:
            tile_bytes = TILE_PX * TILE_PX * 2
        off = tile_base + cell * tile_bytes
        pix = []
        if tile_bytes == TILE_PX * TILE_PX and palette is not None:
            for i in range(TILE_PX * TILE_PX):
                pix.append(palette[atlas[off + i]])
        else:
            for i in range(TILE_PX * TILE_PX):
                value = atlas[off + i * 2] | (atlas[off + i * 2 + 1] << 8)
                r = ((value >> 11) & 31) << 3
                g = ((value >> 5) & 63) << 2
                b = (value & 31) << 3
                pix.append((r, g, b))
        tile_img = Image.new("RGB", (TILE_PX, TILE_PX))
        tile_img.putdata(pix)
        img.paste(tile_img, (x * TILE_PX, y * TILE_PX))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def write_chunks(out_dir: Path, atlas: bytes):
    out_dir.mkdir(parents=True, exist_ok=True)
    chunks = []
    for i in range(math.ceil(len(atlas) / PAGE_SIZE)):
        chunk = atlas[i * PAGE_SIZE:(i + 1) * PAGE_SIZE]
        padded = chunk + b"\0" * (PAGE_SIZE - len(chunk))
        path = out_dir / f"SKIRMISH_GROUND32_p{i:02d}.bin"
        path.write_bytes(padded)
        chunks.append((path, len(chunk)))
    return chunks


def write_terrain_inc(path: Path, chunks, atlas_size: int):
    lines = [
        "; Сгенерировано Source/Tools/terrain_atlas.py",
        "",
        f"TERRAIN_ATLAS_RAMG      EQU #{RAMG_TERRAIN_BASE:06X}",
        f"TERRAIN_ATLAS_PAGE_BASE EQU #{TERRAIN_PAGE_BASE:02X}",
        f"TERRAIN_ATLAS_PAGE_COUNT EQU {len(chunks)}",
        f"TERRAIN_ATLAS_SIZE      EQU {atlas_size}",
        "TERRAIN_TILE_W          EQU 32",
        "TERRAIN_TILE_H          EQU 32",
        "TERRAIN_TILE_STRIDE     EQU 64",
        "",
        "Terrain_Upload:",
        "                GetPage3",
        "                LD   (.RestorePage), A",
    ]
    ramg = RAMG_TERRAIN_BASE
    for i, (_, real_size) in enumerate(chunks):
        lines.extend(
            [
                f"                SetPage3 #{TERRAIN_PAGE_BASE + i:02X}",
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


def write_dl(path: Path, cells, remap):
    lines = [
        "; Сгенерировано Source/Tools/terrain_atlas.py",
        "; Первый экран карты SKIRMISH: реальные тайлы GROUND32.TIL в RAM_G FT812.",
        "",
        "ADVENTURE_DL:",
        "                FT_CLEAR_COLOR_RGB 0, 0, 0",
        "                FT_CLEAR 1, 1, 1",
        "                FT_COLOR_RGB 255, 255, 255",
        "                FT_COLOR_A 255",
        "                FT_BLEND_FUNC FT_ONE, FT_ZERO",
        "                FT_BITMAP_HANDLE 0",
        "                FT_BITMAP_SOURCE TERRAIN_ATLAS_RAMG",
        "                FT_BITMAP_LAYOUT FT_RGB565, TERRAIN_TILE_STRIDE, TERRAIN_TILE_H",
        "                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, TERRAIN_TILE_W, TERRAIN_TILE_H",
        "                FT_BEGIN FT_BITMAPS",
    ]
    for x, y, terrain, shape in cells:
        cell = remap[(terrain, shape)]
        if cell > 127:
            raise ValueError("для FT_CELL нужно не больше 128 видимых cell")
        lines.append(f"                FT_CELL {cell}")
        lines.append(f"                FT_VERTEX2F {x * TILE_PX * 16}, {y * TILE_PX * 16}")
    lines.extend(
        [
            "                FT_END",
            "                FT_DISPLAY",
            "ADVENTURE_DL_SIZE EQU $ - ADVENTURE_DL",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def update_spgbld(path: Path, chunks):
    text = path.read_text(encoding="utf-8")
    marker = "; Страницы terrain atlas."
    head = text.split("; Terrain atlas pages.", 1)[0]
    head = head.split(marker, 1)[0].rstrip()
    lines = [head, "", marker]
    for i, (chunk_path, _) in enumerate(chunks):
        rel = chunk_path.as_posix()
        lines.append(f"Block = #0000, #{TERRAIN_PAGE_BASE + i:02X}, {rel}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Собрать первый terrain atlas HMM2 для FT812 RAM_G.")
    parser.add_argument("--agg", type=Path, default=Path("Assets/Original/DATA/HEROES2.AGG"))
    parser.add_argument("--map", type=Path, default=Path("Assets/Converted/Maps/SKIRMISH.map.bin"))
    parser.add_argument("--out-dir", type=Path, default=Path("Assets/Converted/Terrain"))
    parser.add_argument("--terrain-inc", type=Path, default=Path("Source/ASM/generated_terrain.inc"))
    parser.add_argument("--dl-inc", type=Path, default=Path("Source/ASM/generated_adventure_dl.inc"))
    parser.add_argument("--spgbld", type=Path, default=Path("spgbld_vdac2.ini"))
    parser.add_argument("--preview", type=Path, default=Path("Diagnostics/terrain_ground32_preview.png"))
    parser.add_argument("--origin-x", type=int, default=0)
    parser.add_argument("--origin-y", type=int, default=0)
    args = parser.parse_args()

    agg_data, entries = read_agg_index(args.agg)
    ground_tiles = read_til(agg_entry(agg_data, entries, "GROUND32.TIL"))
    palette = read_palette(agg_entry(agg_data, entries, "KB.PAL"))
    width, height, map_data = read_map(args.map)
    map_tiles = map_data[0] if isinstance(map_data, tuple) else map_data
    cells = visible_cells(width, height, map_tiles, args.origin_x, args.origin_y)

    unique = []
    for _, _, terrain, shape in cells:
        key = (terrain, shape)
        if key not in unique:
            unique.append(key)
    if len(unique) > 128:
        raise ValueError(f"видимый экран требует {len(unique)} cells, лимит FT_CELL = 128")

    remap = {key: i for i, key in enumerate(unique)}
    atlas = bytearray()
    for terrain, shape in unique:
        if terrain >= len(ground_tiles):
            raise ValueError(f"индекс terrain {terrain} вне GROUND32.TIL")
        atlas.extend(to_rgb565(transform_tile(ground_tiles[terrain], shape), palette))

    chunks = write_chunks(args.out_dir, bytes(atlas))
    write_terrain_inc(args.terrain_inc, chunks, len(atlas))
    write_dl(args.dl_inc, cells, remap)
    update_spgbld(args.spgbld, chunks)
    write_preview_png(args.preview, bytes(atlas), cells, remap)

    print(f"видимые тайлы: {len(cells)}, уникальные cells: {len(unique)}")
    print(f"atlas: {len(atlas)} байт, страниц: {len(chunks)}, базовая page: #{TERRAIN_PAGE_BASE:02X}")
    print(f"предпросмотр: {args.preview}")


if __name__ == "__main__":
    main()
