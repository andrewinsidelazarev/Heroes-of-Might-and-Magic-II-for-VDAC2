#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DL_INC = ROOT / "Source" / "ASM" / "generated_adventure_dl.inc"
ATLAS_DIR = ROOT / "Assets" / "Converted" / "Terrain"
OUT = ROOT / "Diagnostics" / "hmm2_direct_atlas.png"
ATLAS_SIZE = 239616
TILE_W = 32
TILE_H = 32
STRIDE = 64
SCREEN_W = 640
SCREEN_H = 480


def read_atlas() -> bytes:
    out = bytearray()
    for path in sorted(ATLAS_DIR.glob("SKIRMISH_GROUND32_p*.bin")):
        out.extend(path.read_bytes())
    return bytes(out[:ATLAS_SIZE])


def rgb565(data: bytes, off: int) -> tuple[int, int, int]:
    value = data[off] | (data[off + 1] << 8)
    return (((value >> 11) & 31) << 3, ((value >> 5) & 63) << 2, (value & 31) << 3)


def parse_draws():
    draws = []
    cell = 0
    cell_re = re.compile(r"FT_CELL\s+(\d+)")
    v_re = re.compile(r"FT_VERTEX2F\s+(\d+),\s*(\d+)")
    for line in DL_INC.read_text(encoding="utf-8").splitlines():
        m = cell_re.search(line)
        if m:
            cell = int(m.group(1))
            continue
        m = v_re.search(line)
        if m:
            draws.append((cell, int(m.group(1)), int(m.group(2))))
    return draws


def main() -> int:
    atlas = read_atlas()
    img = Image.new("RGB", (SCREEN_W, SCREEN_H), (0, 0, 0))
    draws = parse_draws()
    for cell, x, y in draws:
        src = cell * STRIDE * TILE_H
        for py in range(TILE_H):
            for px in range(TILE_W):
                img.putpixel((x + px, y + py), rgb565(atlas, src + py * STRIDE + px * 2))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"png напрямую из atlas: {OUT}")
    print(f"команд отрисовки: {len(draws)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
