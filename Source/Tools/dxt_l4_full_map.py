#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

from agg_tools import read_agg_index
from terrain_atlas import agg_entry, read_palette, read_til, transform_tile
from terrain_preview import TILE_PX, read_map


BLOCK_PX = 4


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def rgb565_value(rgb: tuple[int, int, int]) -> int:
    r, g, b = rgb
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def rgb565_to_rgb(value: int) -> tuple[int, int, int]:
    return ((value >> 11) & 31) << 3, ((value >> 5) & 63) << 2, (value & 31) << 3


def render_full_map_rgb(width_tiles: int, height_tiles: int, map_data, ground_tiles, palette) -> bytearray:
    tiles = map_data[0] if isinstance(map_data, tuple) else map_data
    width = width_tiles * TILE_PX
    height = height_tiles * TILE_PX
    out = bytearray(width * height * 3)
    tile_cache: dict[tuple[int, int], bytes] = {}

    for ty in range(height_tiles):
        for tx in range(width_tiles):
            tile = tiles[ty * width_tiles + tx]
            key = (tile["terrain"], tile["terrain_flags"] & 3)
            pixels = tile_cache.get(key)
            if pixels is None:
                if key[0] >= len(ground_tiles):
                    raise ValueError(f"terrain {key[0]} вне GROUND32.TIL")
                pixels = transform_tile(ground_tiles[key[0]], key[1])
                tile_cache[key] = pixels

            dst_x = tx * TILE_PX
            dst_y = ty * TILE_PX
            for py in range(TILE_PX):
                row = ((dst_y + py) * width + dst_x) * 3
                src = py * TILE_PX
                for px in range(TILE_PX):
                    r, g, b = palette[pixels[src + px]]
                    off = row + px * 3
                    out[off + 0] = r
                    out[off + 1] = g
                    out[off + 2] = b
    return out


def block_pixels(rgb: bytes, width: int, bx: int, by: int) -> list[tuple[int, int, int]]:
    pixels = []
    base_x = bx * BLOCK_PX
    base_y = by * BLOCK_PX
    for y in range(BLOCK_PX):
        row = ((base_y + y) * width + base_x) * 3
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


def encode_d1l4_raw(rgb: bytes, width: int, height: int) -> bytes:
    if width % BLOCK_PX or height % BLOCK_PX:
        raise ValueError("DXT L4 требует размеры, кратные 4")
    blocks_x = width // BLOCK_PX
    blocks_y = height // BLOCK_PX
    c0_layer = bytearray()
    c1_layer = bytearray()
    mask = bytearray((width // 2) * height)

    for by in range(blocks_y):
        for bx in range(blocks_x):
            pixels = block_pixels(rgb, width, bx, by)
            c0, c1, c0_rgb, c1_rgb = choose_endpoints(pixels)
            c0_layer.extend(struct.pack("<H", c0))
            c1_layer.extend(struct.pack("<H", c1))
            for py in range(BLOCK_PX):
                y = by * BLOCK_PX + py
                row = y * (width // 2)
                for px in range(BLOCK_PX):
                    x = bx * BLOCK_PX + px
                    sel = selector_for(pixels[py * BLOCK_PX + px], c0_rgb, c1_rgb)
                    dst = row + (x // 2)
                    if x & 1:
                        mask[dst] = (mask[dst] & 0xF0) | sel
                    else:
                        mask[dst] = (mask[dst] & 0x0F) | (sel << 4)

    return bytes(c0_layer + c1_layer + mask)


def main() -> int:
    parser = argparse.ArgumentParser(description="Собрать pseudo-DXT L4 фон всей карты HMM2.")
    parser.add_argument("--agg", type=Path, default=Path("Assets/Original/DATA/HEROES2.AGG"))
    parser.add_argument("--map", type=Path, default=Path("Assets/Converted/Maps/SKIRMISH.map.bin"))
    parser.add_argument("--out", type=Path, default=Path("Assets/Converted/Background/SKIRMISH_FULLMAP_DXT_L4.raw"))
    args = parser.parse_args()

    agg_data, entries = read_agg_index(args.agg)
    ground_tiles = read_til(agg_entry(agg_data, entries, "GROUND32.TIL"))
    palette = read_palette(agg_entry(agg_data, entries, "KB.PAL"))
    width_tiles, height_tiles, map_data = read_map(args.map)
    width = width_tiles * TILE_PX
    height = height_tiles * TILE_PX

    rgb = render_full_map_rgb(width_tiles, height_tiles, map_data, ground_tiles, palette)
    raw = encode_d1l4_raw(rgb, width, height)
    blocks_x = width // BLOCK_PX
    blocks_y = height // BLOCK_PX
    expected = blocks_x * blocks_y * 2 * 2 + (width // 2) * height
    if len(raw) != expected:
        raise AssertionError(f"raw size {len(raw)} != {expected}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(raw)
    c_size = blocks_x * blocks_y * 2
    print(f"map={width_tiles}x{height_tiles} tiles, pixels={width}x{height}")
    print(f"c0={c_size} bytes, c1={c_size} bytes, mask={(width // 2) * height} bytes")
    print(f"raw={len(raw)} bytes ({len(raw) / 1024:.1f} KiB)")
    print(f"sha256={sha256(raw)}")
    print(f"out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
