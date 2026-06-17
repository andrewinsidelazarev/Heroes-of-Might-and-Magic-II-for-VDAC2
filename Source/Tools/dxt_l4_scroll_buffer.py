#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import struct
from pathlib import Path

from agg_tools import read_agg_index
from terrain_atlas import agg_entry, read_palette, read_til, transform_tile
from terrain_preview import TILE_PX, read_map


PAGE_SIZE = 0x4000
SCROLL_TILES_W = 28
SCROLL_TILES_H = 22
SCROLL_W = SCROLL_TILES_W * TILE_PX
SCROLL_H = SCROLL_TILES_H * TILE_PX
BLOCK_PX = 4
BG_DXT_RAMG = 0x000000
BG_DXT_PAGE_BASE = 0xD0
PACK_MAGIC = b"H2BG"
PACK_VERSION = 1


def rgb565_value(rgb: tuple[int, int, int]) -> int:
    r, g, b = rgb
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def rgb565_to_rgb(value: int) -> tuple[int, int, int]:
    r = ((value >> 11) & 31) << 3
    g = ((value >> 5) & 63) << 2
    b = (value & 31) << 3
    return r, g, b


def render_scroll_rgb(width: int, height: int, map_data, ground_tiles, palette, origin_x: int, origin_y: int) -> bytearray:
    tiles = map_data[0] if isinstance(map_data, tuple) else map_data
    out = bytearray(SCROLL_W * SCROLL_H * 3)
    black = (0, 0, 0)
    tile_cache: dict[tuple[int, int], bytes] = {}

    for ty in range(SCROLL_TILES_H):
        my = origin_y + ty
        for tx in range(SCROLL_TILES_W):
            mx = origin_x + tx
            if mx >= width or my >= height:
                pixels = bytes([0]) * (TILE_PX * TILE_PX)
                colors = [black] * 256
            else:
                tile = tiles[my * width + mx]
                key = (tile["terrain"], tile["terrain_flags"] & 3)
                pixels = tile_cache.get(key)
                if pixels is None:
                    if key[0] >= len(ground_tiles):
                        raise ValueError(f"terrain {key[0]} вне GROUND32.TIL")
                    pixels = transform_tile(ground_tiles[key[0]], key[1])
                    tile_cache[key] = pixels
                colors = palette

            dst_x = tx * TILE_PX
            dst_y = ty * TILE_PX
            for py in range(TILE_PX):
                row = ((dst_y + py) * SCROLL_W + dst_x) * 3
                src = py * TILE_PX
                for px in range(TILE_PX):
                    r, g, b = colors[pixels[src + px]]
                    off = row + px * 3
                    out[off + 0] = r
                    out[off + 1] = g
                    out[off + 2] = b
    return out


def block_pixels(rgb: bytes, bx: int, by: int) -> list[tuple[int, int, int]]:
    pixels = []
    base_x = bx * BLOCK_PX
    base_y = by * BLOCK_PX
    for y in range(BLOCK_PX):
        row = ((base_y + y) * SCROLL_W + base_x) * 3
        for x in range(BLOCK_PX):
            off = row + x * 3
            pixels.append((rgb[off], rgb[off + 1], rgb[off + 2]))
    return pixels


def choose_endpoints(pixels: list[tuple[int, int, int]]) -> tuple[int, int, tuple[int, int, int], tuple[int, int, int]]:
    def lum(c: tuple[int, int, int]) -> int:
        return c[0] * 30 + c[1] * 59 + c[2] * 11

    lo = min(pixels, key=lum)
    hi = max(pixels, key=lum)
    c0 = rgb565_value(lo)
    c1 = rgb565_value(hi)
    return c0, c1, rgb565_to_rgb(c0), rgb565_to_rgb(c1)


def selector_for(color: tuple[int, int, int], c0_rgb: tuple[int, int, int], c1_rgb: tuple[int, int, int]) -> int:
    vx = c1_rgb[0] - c0_rgb[0]
    vy = c1_rgb[1] - c0_rgb[1]
    vz = c1_rgb[2] - c0_rgb[2]
    denom = vx * vx + vy * vy + vz * vz
    if denom <= 0:
        return 0
    wx = color[0] - c0_rgb[0]
    wy = color[1] - c0_rgb[1]
    wz = color[2] - c0_rgb[2]
    value = (wx * vx + wy * vy + wz * vz) * 15 / denom
    return max(0, min(15, int(value + 0.5)))


def encode_d1l4_raw(rgb: bytes) -> bytes:
    blocks_x = SCROLL_W // BLOCK_PX
    blocks_y = SCROLL_H // BLOCK_PX
    c0_layer = bytearray()
    c1_layer = bytearray()
    mask = bytearray((SCROLL_W // 2) * SCROLL_H)

    for by in range(blocks_y):
        for bx in range(blocks_x):
            pixels = block_pixels(rgb, bx, by)
            c0, c1, c0_rgb, c1_rgb = choose_endpoints(pixels)
            c0_layer.extend(struct.pack("<H", c0))
            c1_layer.extend(struct.pack("<H", c1))
            for py in range(BLOCK_PX):
                y = by * BLOCK_PX + py
                row = y * (SCROLL_W // 2)
                for px in range(BLOCK_PX):
                    x = bx * BLOCK_PX + px
                    sel = selector_for(pixels[py * BLOCK_PX + px], c0_rgb, c1_rgb)
                    dst = row + (x // 2)
                    if x & 1:
                        mask[dst] = (mask[dst] & 0xF0) | sel
                    else:
                        mask[dst] = (mask[dst] & 0x0F) | (sel << 4)

    return bytes(c0_layer + c1_layer + mask)


def write_pages(out_dir: Path, raw: bytes) -> list[tuple[Path, int, int]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("SKIRMISH_BG_DXT_L4_p*.bin"):
        old.unlink()
    pages = []
    for index in range(math.ceil(len(raw) / PAGE_SIZE)):
        part = raw[index * PAGE_SIZE:(index + 1) * PAGE_SIZE]
        path = out_dir / f"SKIRMISH_BG_DXT_L4_p{index:02d}.bin"
        path.write_bytes(part + bytes(PAGE_SIZE - len(part)))
        pages.append((path, BG_DXT_PAGE_BASE + index, len(part)))
    return pages


def write_inc(path: Path, pages: list[tuple[Path, int, int]], raw_size: int) -> None:
    blocks_x = SCROLL_W // BLOCK_PX
    blocks_y = SCROLL_H // BLOCK_PX
    color_size = blocks_x * blocks_y * 2
    mask_offset = color_size * 2
    lines = [
        "; Сгенерировано Source/Tools/dxt_l4_scroll_buffer.py",
        "; Pseudo-DXT L4 фон текущего экрана карты: c0 RGB565 + c1 RGB565 + L4 mask.",
        "",
        f"BG_DXT_RAMG          EQU #{BG_DXT_RAMG:06X}",
        f"BG_DXT_PAGE_BASE     EQU #{BG_DXT_PAGE_BASE:02X}",
        f"BG_DXT_PAGE_COUNT    EQU {len(pages)}",
        "BG_DXT_FULLMAP       EQU 0",
        f"BG_DXT_RAW_SIZE      EQU {raw_size}",
        f"BG_DXT_W             EQU {SCROLL_W}",
        f"BG_DXT_H             EQU {SCROLL_H}",
        f"BG_DXT_BLOCKS_X      EQU {blocks_x}",
        f"BG_DXT_BLOCKS_Y      EQU {blocks_y}",
        "BG_DXT_C0_OFFSET     EQU 0",
        f"BG_DXT_C1_OFFSET     EQU {color_size}",
        f"BG_DXT_MASK_OFFSET   EQU {mask_offset}",
        f"BG_DXT_COLOR_STRIDE  EQU {blocks_x * 2}",
        f"BG_DXT_COLOR_H       EQU {blocks_y}",
        f"BG_DXT_MASK_STRIDE   EQU {SCROLL_W // 2}",
        "",
        "BG_DXT_MASK_A        EQU 160",
        "BG_DXT_COLOR_A       EQU 40",
        "",
        "BackgroundDxt_Upload:",
        "                GetPage3",
        "                LD   (.RestorePage), A",
    ]
    ramg = BG_DXT_RAMG
    for _path, page, size in pages:
        lines.extend(
            [
                f"                SetPage3 #{page:02X}",
                "                LD   HL, #C000",
                f"                LD   A, #{(ramg >> 16) & 0xFF:02X}",
                f"                LD   DE, #{ramg & 0xFFFF:04X}",
                f"                LD   BC, {size}",
                "                CALL FT.WriteMem",
            ]
        )
        ramg += size
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


def write_disabled_inc(path: Path) -> None:
    lines = [
        "; Сгенерировано Source/Tools/dxt_l4_scroll_buffer.py --disable",
        "; Pseudo-DXT L4 фон отключён для безопасной сборки.",
        "",
        "BG_DXT_RAW_SIZE      EQU 0",
        "BG_DXT_FULLMAP       EQU 0",
        "",
        "BackgroundDxt_Upload:",
        "                RET",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_dl_inc(path: Path) -> None:
    lines = [
        "; Сгенерировано Source/Tools/dxt_l4_scroll_buffer.py",
        "; DL-шаблон вывода pseudo-DXT L4 фона 672x512 в физическое окно 1024x768.",
        "; Значения *_C/*_F патчатся из ViewportPixelX/Y & 31.",
        "",
        "BG_DXT_PHYS_W       EQU 1024",
        "BG_DXT_PHYS_H       EQU 768",
        "",
        "BackgroundDxt_DL:",
        "                FT_SAVE_CONTEXT",
        "                FT_CLEAR_COLOR_RGB 0, 0, 0",
        "                FT_CLEAR_COLOR_A 0",
        "                FT_CLEAR 1, 1, 1",
        "                FT_VERTEX_FORMAT 4",
        "                FT_SCISSOR_XY 0, 0",
        "                FT_SCISSOR_SIZE BG_DXT_PHYS_W, BG_DXT_PHYS_H",
        "",
        "                ; Pass 1: L4 mask -> destination alpha.",
        "                FT_COLOR_MASK 0, 0, 0, 1",
        "                FT_COLOR_RGB 255, 255, 255",
        "                FT_COLOR_A 255",
        "                FT_BLEND_FUNC FT_ONE, FT_ZERO",
        "                FT_BITMAP_HANDLE 1",
        "                FT_BITMAP_SOURCE BG_DXT_RAMG + BG_DXT_MASK_OFFSET",
        "                FT_BITMAP_LAYOUT_H BG_DXT_MASK_STRIDE, BG_DXT_H",
        "                FT_BITMAP_LAYOUT FT_L4, BG_DXT_MASK_STRIDE, BG_DXT_H",
        "                FT_BITMAP_SIZE_H BG_DXT_PHYS_W, BG_DXT_PHYS_H",
        "                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, BG_DXT_PHYS_W, BG_DXT_PHYS_H",
        "                FT_BITMAP_TRANSFORM_A BG_DXT_MASK_A",
        "                FT_BITMAP_TRANSFORM_B 0",
        "BG_DXT_MASK_C_LOW:",
        "                DEFW 0",
        "BG_DXT_MASK_C_HIGH:",
        "                DEFW #1700",
        "                FT_BITMAP_TRANSFORM_D 0",
        "                FT_BITMAP_TRANSFORM_E BG_DXT_MASK_A",
        "BG_DXT_MASK_F_LOW:",
        "                DEFW 0",
        "BG_DXT_MASK_F_HIGH:",
        "                DEFW #1A00",
        "                FT_BEGIN FT_BITMAPS",
        "                FT_VERTEX2F 0, 0",
        "                FT_END",
        "",
        "                ; Pass 2: c1 * destination alpha.",
        "                FT_COLOR_MASK 1, 1, 1, 0",
        "                FT_BLEND_FUNC FT_DST_ALPHA, FT_ZERO",
        "                FT_BITMAP_HANDLE 0",
        "                FT_CELL 0",
        "                FT_BITMAP_SOURCE BG_DXT_RAMG + BG_DXT_C1_OFFSET",
        "                FT_BITMAP_LAYOUT FT_RGB565, BG_DXT_COLOR_STRIDE, BG_DXT_COLOR_H",
        "                FT_BITMAP_SIZE_H BG_DXT_PHYS_W, BG_DXT_PHYS_H",
        "                ; NEAREST обязателен: BILINEAR смешивает цвета СОСЕДНИХ 4x4-блоков",
        "                ; до применения маски-селектора, и с дробной фазой offset/4 при",
        "                ; скролле границы блоков рябят (фикс от соседа Zuma VDAC2).",
        "                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, BG_DXT_PHYS_W, BG_DXT_PHYS_H",
        "                FT_BITMAP_TRANSFORM_A BG_DXT_COLOR_A",
        "                FT_BITMAP_TRANSFORM_B 0",
        "BG_DXT_COLOR_C_LOW:",
        "                DEFW 0",
        "BG_DXT_COLOR_C_HIGH:",
        "                DEFW #1700",
        "                FT_BITMAP_TRANSFORM_D 0",
        "                FT_BITMAP_TRANSFORM_E BG_DXT_COLOR_A",
        "BG_DXT_COLOR_F_LOW:",
        "                DEFW 0",
        "BG_DXT_COLOR_F_HIGH:",
        "                DEFW #1A00",
        "                FT_BEGIN FT_BITMAPS",
        "                FT_VERTEX2F 0, 0",
        "                FT_END",
        "",
        "                ; Pass 3: c0 * (1 - destination alpha) + destination.",
        "                FT_BLEND_FUNC FT_ONE_MINUS_DST_ALPHA, FT_ONE",
        "                FT_CELL 0",
        "                FT_BITMAP_SOURCE BG_DXT_RAMG + BG_DXT_C0_OFFSET",
        "                FT_BEGIN FT_BITMAPS",
        "                FT_VERTEX2F 0, 0",
        "                FT_END",
        "",
        "                FT_COLOR_MASK 1, 1, 1, 1",
        "                FT_BLEND_FUNC FT_ONE, FT_ZERO",
        "                FT_SCISSOR_XY 0, 0",
        "                FT_SCISSOR_SIZE 1024, 768",
        "                FT_RESTORE_CONTEXT",
        "BackgroundDxt_DL_SIZE EQU $ - BackgroundDxt_DL",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_disabled_dl_inc(path: Path) -> None:
    lines = [
        "; Сгенерировано Source/Tools/dxt_l4_scroll_buffer.py --disable",
        "",
        "BackgroundDxt_DL:",
        "BackgroundDxt_DL_SIZE EQU 0",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def update_spgbld(path: Path, pages: list[tuple[Path, int, int]]) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "; Страницы terrain atlas."
    if marker not in text:
        raise ValueError(f"{path}: не найден marker '{marker}'")
    head, tail = text.split(marker, 1)
    head = head.split("; Страницы pseudo-DXT L4 background текущего экрана.", 1)[0].rstrip()
    lines = [head]
    if pages:
        lines.extend(["", "; Страницы pseudo-DXT L4 background текущего экрана."])
        for page_path, page, _size in pages:
            lines.append(f"Block = #0000, #{page:02X}, {page_path.as_posix()}")
    lines.extend(["", marker + tail])
    path.write_text("\n".join(lines), encoding="utf-8")


def pack_origin_max(width: int, height: int) -> tuple[int, int]:
    return max(0, width - 20), max(0, height - 15)


def write_all_origin_pack(
    path: Path,
    width: int,
    height: int,
    map_data,
    ground_tiles,
    palette,
) -> None:
    max_x, max_y = pack_origin_max(width, height)
    entries: list[tuple[int, int, int, int]] = []
    payloads: list[bytes] = []
    offset = 16 + (max_x + 1) * (max_y + 1) * 16

    for oy in range(max_y + 1):
        for ox in range(max_x + 1):
            rgb = render_scroll_rgb(width, height, map_data, ground_tiles, palette, ox, oy)
            raw = encode_d1l4_raw(rgb)
            entries.append((ox, oy, offset, len(raw)))
            payloads.append(raw)
            offset += len(raw)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fp:
        fp.write(
            struct.pack(
                "<4sHHHHHH",
                PACK_MAGIC,
                PACK_VERSION,
                max_x + 1,
                max_y + 1,
                SCROLL_W,
                SCROLL_H,
                len(entries),
            )
        )
        for ox, oy, off, size in entries:
            fp.write(struct.pack("<HHII", ox, oy, off, size))
        for raw in payloads:
            fp.write(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description="Собрать 672x512 pseudo-DXT L4 фон текущего экрана HMM2.")
    parser.add_argument("--agg", type=Path, default=Path("Assets/Original/DATA/HEROES2.AGG"))
    parser.add_argument("--map", type=Path, default=Path("Assets/Converted/Maps/SKIRMISH.map.bin"))
    parser.add_argument("--origin-x", type=int, default=0)
    parser.add_argument("--origin-y", type=int, default=0)
    parser.add_argument("--raw", type=Path, default=Path("Assets/Converted/Background/SKIRMISH_BG_DXT_L4.raw"))
    parser.add_argument("--out-dir", type=Path, default=Path("Assets/Converted/Background"))
    parser.add_argument("--inc", type=Path, default=Path("Source/ASM/generated_dxt_background.inc"))
    parser.add_argument("--dl-inc", type=Path, default=Path("Source/ASM/generated_dxt_scroll_dl.inc"))
    parser.add_argument("--spgbld", type=Path, default=Path("spgbld_vdac2.ini"))
    parser.add_argument("--disable", action="store_true", help="Отключить active DXT background и убрать его страницы из SPG.")
    parser.add_argument("--pack-all", type=Path, help="Собрать отдельный H2BG pack всех DXT-окон карты.")
    args = parser.parse_args()

    if args.disable:
        write_disabled_inc(args.inc)
        write_disabled_dl_inc(args.dl_inc)
        update_spgbld(args.spgbld, [])
        print("DXT L4 background disabled")
        return 0

    agg_data, entries = read_agg_index(args.agg)
    ground_tiles = read_til(agg_entry(agg_data, entries, "GROUND32.TIL"))
    palette = read_palette(agg_entry(agg_data, entries, "KB.PAL"))
    width, height, map_data = read_map(args.map)

    if args.pack_all:
        write_all_origin_pack(args.pack_all, width, height, map_data, ground_tiles, palette)
        print(f"pack-all={args.pack_all}")
        print(f"origins={(pack_origin_max(width, height)[0] + 1) * (pack_origin_max(width, height)[1] + 1)}")
        return 0

    if args.origin_x < 0 or args.origin_y < 0:
        raise ValueError("origin не может быть отрицательным")
    if args.origin_x >= width or args.origin_y >= height:
        raise ValueError(f"origin {args.origin_x},{args.origin_y} вне карты {width}x{height}")

    rgb = render_scroll_rgb(width, height, map_data, ground_tiles, palette, args.origin_x, args.origin_y)
    raw = encode_d1l4_raw(rgb)
    expected = (SCROLL_W // 4) * (SCROLL_H // 4) * 2 * 2 + (SCROLL_W // 2) * SCROLL_H
    if len(raw) != expected:
        raise AssertionError(f"raw size {len(raw)} != {expected}")
    args.raw.parent.mkdir(parents=True, exist_ok=True)
    args.raw.write_bytes(raw)
    pages = write_pages(args.out_dir, raw)
    write_inc(args.inc, pages, len(raw))
    write_dl_inc(args.dl_inc)
    update_spgbld(args.spgbld, pages)
    print(f"origin={args.origin_x},{args.origin_y}")
    print(f"scroll-buffer={SCROLL_W}x{SCROLL_H}, raw={len(raw)} bytes")
    print(f"pages={len(pages)}, page_base=#{BG_DXT_PAGE_BASE:02X}")
    print(f"raw={args.raw}")
    print(f"inc={args.inc}")
    print(f"dl_inc={args.dl_inc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
