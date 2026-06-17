#!/usr/bin/env python3
from __future__ import annotations

import argparse


LOGICAL_W = 640
LOGICAL_H = 480
PHYSICAL_W = 1024
PHYSICAL_H = 768
SCROLL_W = 672
SCROLL_H = 512
TILE_PX = 32


def ft_signed24(value: int) -> int:
    return value & 0xFFFFFF


def params(rem_x: int, rem_y: int) -> dict[str, int]:
    if not 0 <= rem_x < TILE_PX:
        raise ValueError(f"rem_x должен быть 0..{TILE_PX - 1}, получено {rem_x}")
    if not 0 <= rem_y < TILE_PX:
        raise ValueError(f"rem_y должен быть 0..{TILE_PX - 1}, получено {rem_y}")

    # FT812 bitmap matrix maps destination pixels to source texels:
    # source = (A * dst + C) / 256.
    # Physical 1024x768 is logical 640x480 scaled by 8/5.
    mask_a = 256 * 5 // 8
    color_a = 256 * 5 // (8 * 4)
    return {
        "mask_a": mask_a,
        "mask_e": mask_a,
        "mask_c": rem_x * 256,
        "mask_f": rem_y * 256,
        "color_a": color_a,
        "color_e": color_a,
        "color_c": rem_x * 64,
        "color_f": rem_y * 64,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Расчёт FT812 BITMAP_TRANSFORM для скролла pseudo-DXT L4 фона HMM2."
    )
    parser.add_argument("--rem-x", type=int, default=0, help="остаток ViewportPixelX внутри 32px тайла")
    parser.add_argument("--rem-y", type=int, default=0, help="остаток ViewportPixelY внутри 32px тайла")
    args = parser.parse_args()

    p = params(args.rem_x, args.rem_y)
    print(f"logical={LOGICAL_W}x{LOGICAL_H}, physical={PHYSICAL_W}x{PHYSICAL_H}, scroll-buffer={SCROLL_W}x{SCROLL_H}")
    print(f"rem_x={args.rem_x}, rem_y={args.rem_y}")
    print("L4 mask:")
    print(f"  A/E={p['mask_a']}  C=#{ft_signed24(p['mask_c']):06X}  F=#{ft_signed24(p['mask_f']):06X}")
    print("RGB565 endpoints:")
    print(f"  A/E={p['color_a']}  C=#{ft_signed24(p['color_c']):06X}  F=#{ft_signed24(p['color_f']):06X}")
    print("ASM constants:")
    print(f"  DXT_SCROLL_MASK_A   EQU {p['mask_a']}")
    print(f"  DXT_SCROLL_COLOR_A  EQU {p['color_a']}")
    print(f"  DXT_SCROLL_MASK_C   EQU #{ft_signed24(p['mask_c']):06X}")
    print(f"  DXT_SCROLL_MASK_F   EQU #{ft_signed24(p['mask_f']):06X}")
    print(f"  DXT_SCROLL_COLOR_C  EQU #{ft_signed24(p['color_c']):06X}")
    print(f"  DXT_SCROLL_COLOR_F  EQU #{ft_signed24(p['color_f']):06X}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
