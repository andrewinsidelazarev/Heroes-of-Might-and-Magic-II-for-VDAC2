#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


TILE_PX = 32
BLOCK_PX = 4
VIEW_TILES_W = 21
VIEW_TILES_H = 16
VIEW_W = VIEW_TILES_W * TILE_PX
VIEW_H = VIEW_TILES_H * TILE_PX


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def layout(width: int, height: int) -> dict[str, int]:
    blocks_x = width // BLOCK_PX
    blocks_y = height // BLOCK_PX
    color_stride = blocks_x * 2
    color_h = blocks_y
    c_size = color_stride * color_h
    mask_stride = width // 2
    mask_size = mask_stride * height
    return {
        "blocks_x": blocks_x,
        "blocks_y": blocks_y,
        "color_stride": color_stride,
        "color_h": color_h,
        "c0_offset": 0,
        "c1_offset": c_size,
        "mask_offset": c_size * 2,
        "mask_stride": mask_stride,
        "raw_size": c_size * 2 + mask_size,
    }


def copy_rect(src: bytes, src_off: int, src_stride: int, dst_stride: int, x_bytes: int, y: int, h: int) -> bytes:
    out = bytearray(dst_stride * h)
    for row in range(h):
        s = src_off + (y + row) * src_stride + x_bytes
        d = row * dst_stride
        out[d:d + dst_stride] = src[s:s + dst_stride]
    return bytes(out)


def extract_window(full_raw: bytes, full_w: int, full_h: int, origin_x: int, origin_y: int) -> bytes:
    if full_w % BLOCK_PX or full_h % BLOCK_PX:
        raise ValueError("полный DXT размер должен быть кратен 4")
    if origin_x < 0 or origin_y < 0:
        raise ValueError("origin не может быть отрицательным")

    pixel_x = origin_x * TILE_PX
    pixel_y = origin_y * TILE_PX
    if pixel_x + VIEW_W > full_w or pixel_y + VIEW_H > full_h:
        raise ValueError(f"окно {origin_x},{origin_y} выходит за full map {full_w}x{full_h}")

    full = layout(full_w, full_h)
    view = layout(VIEW_W, VIEW_H)
    if len(full_raw) != full["raw_size"]:
        raise ValueError(f"full raw size {len(full_raw)} != {full['raw_size']}")

    block_x = pixel_x // BLOCK_PX
    block_y = pixel_y // BLOCK_PX
    color_x_bytes = block_x * 2
    color_y = block_y
    color_h = VIEW_H // BLOCK_PX
    color_stride = view["color_stride"]

    mask_x_bytes = pixel_x // 2
    mask_y = pixel_y
    mask_stride = view["mask_stride"]

    c0 = copy_rect(
        full_raw,
        full["c0_offset"],
        full["color_stride"],
        color_stride,
        color_x_bytes,
        color_y,
        color_h,
    )
    c1 = copy_rect(
        full_raw,
        full["c1_offset"],
        full["color_stride"],
        color_stride,
        color_x_bytes,
        color_y,
        color_h,
    )
    mask = copy_rect(
        full_raw,
        full["mask_offset"],
        full["mask_stride"],
        mask_stride,
        mask_x_bytes,
        mask_y,
        VIEW_H,
    )
    raw = c0 + c1 + mask
    if len(raw) != view["raw_size"]:
        raise AssertionError(f"window raw size {len(raw)} != {view['raw_size']}")
    return raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Вырезать 672x512 DXT L4 окно из полного DXT-фона карты.")
    parser.add_argument("--full", type=Path, default=Path("Assets/Converted/Background/SKIRMISH_FULLMAP_DXT_L4.raw"))
    parser.add_argument("--full-w", type=int, default=1152)
    parser.add_argument("--full-h", type=int, default=1152)
    parser.add_argument("--origin-x", type=int, default=0)
    parser.add_argument("--origin-y", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("Assets/Converted/Background/SKIRMISH_BG_DXT_L4_from_full.raw"))
    parser.add_argument("--compare", type=Path, help="Сравнить результат с готовым window raw.")
    args = parser.parse_args()

    raw = extract_window(args.full.read_bytes(), args.full_w, args.full_h, args.origin_x, args.origin_y)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(raw)
    print(f"origin={args.origin_x},{args.origin_y}")
    print(f"window={VIEW_W}x{VIEW_H}, raw={len(raw)} bytes")
    print(f"sha256={sha256(raw)}")
    print(f"out={args.out}")
    if args.compare:
        expected = args.compare.read_bytes()
        print(f"compare={args.compare}")
        print(f"compare sha256={sha256(expected)}")
        if raw != expected:
            for i, (a, b) in enumerate(zip(raw, expected)):
                if a != b:
                    print(f"DIFF offset=#{i:06X}: extracted=#{a:02X}, compare=#{b:02X}")
                    return 1
            print("DIFF length")
            return 1
        print("OK: extracted window byte-for-byte matches compare")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
