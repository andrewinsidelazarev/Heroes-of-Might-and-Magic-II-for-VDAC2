#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image

from terrain_preview import TILE_PX, VIEW_H, VIEW_W, read_map
from viewport_pack import (
    COMPOSITE_BG_PALETTE_SIZE,
    COMPOSITE_BG_TILE_OFFSET,
    COMPOSITE_TILE_BYTES,
    PACK_VIEW_H,
    PACK_VIEW_W,
    composite_slot_for_tile,
)


ROOT = Path(__file__).resolve().parents[2]


def read_chunks(folder: Path, pattern: str, size: int) -> bytes:
    out = bytearray()
    for path in sorted(folder.glob(pattern)):
        out.extend(path.read_bytes())
        if len(out) >= size:
            break
    return bytes(out[:size])


def palette_rgb(payload: bytes) -> list[tuple[int, int, int]]:
    out = []
    for i in range(0, COMPOSITE_BG_PALETTE_SIZE, 2):
        value = payload[i] | (payload[i + 1] << 8)
        out.append((((value >> 8) & 15) * 17, ((value >> 4) & 15) * 17, (value & 15) * 17))
    return out


def tile_bytes(payload: bytes, mx: int, my: int, width: int) -> bytes:
    index = my * width + mx
    start = COMPOSITE_BG_TILE_OFFSET + index * COMPOSITE_TILE_BYTES
    return payload[start:start + COMPOSITE_TILE_BYTES]


def upload_rect(cache: list[bytes | None], payload: bytes, width: int, height: int, x0: int, y0: int, w: int, h: int) -> None:
    for y in range(y0, min(y0 + h, height)):
        for x in range(x0, min(x0 + w, width)):
            cache[composite_slot_for_tile(x, y)] = tile_bytes(payload, x, y, width)


def render_cache(cache: list[bytes | None], payload: bytes, width: int, ox: int, oy: int, out_path: Path) -> None:
    pal = palette_rgb(payload)
    img = Image.new("RGB", (VIEW_W * TILE_PX, VIEW_H * TILE_PX), (255, 0, 255))
    for vy in range(VIEW_H):
        for vx in range(VIEW_W):
            mx = ox + vx
            my = oy + vy
            slot = composite_slot_for_tile(mx, my)
            raw = cache[slot]
            if raw is None:
                continue
            for py in range(TILE_PX):
                for px in range(TILE_PX):
                    img.putpixel((vx * TILE_PX + px, vy * TILE_PX + py), pal[raw[py * TILE_PX + px]])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def render_full_map(payload: bytes, width: int, height: int, out_path: Path) -> None:
    pal = palette_rgb(payload)
    img = Image.new("RGB", (width * TILE_PX, height * TILE_PX), (255, 0, 255))
    for my in range(height):
        for mx in range(width):
            raw = tile_bytes(payload, mx, my, width)
            for py in range(TILE_PX):
                for px in range(TILE_PX):
                    img.putpixel((mx * TILE_PX + px, my * TILE_PX + py), pal[raw[py * TILE_PX + px]])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def main() -> int:
    width, height, _map_data = read_map(ROOT / "Assets/Converted/Maps/SKIRMISH.map.bin")
    payload_size = COMPOSITE_BG_TILE_OFFSET + width * height * COMPOSITE_TILE_BYTES
    payload = read_chunks(ROOT / "Assets/Converted/Terrain", "SKIRMISH_GROUND32_p*.bin", payload_size)

    render_full_map(payload, width, height, ROOT / "Diagnostics/composite_full_map_preview.png")
    cache: list[bytes | None] = [None] * (PACK_VIEW_W * PACK_VIEW_H)
    upload_rect(cache, payload, width, height, 0, 0, PACK_VIEW_W, PACK_VIEW_H)
    upload_rect(cache, payload, width, height, 1 + PACK_VIEW_W - 1, 0, 1, PACK_VIEW_H)
    render_cache(cache, payload, width, 1, 0, ROOT / "Diagnostics/composite_incremental_x40_expected.png")
    print("png: Diagnostics\\composite_full_map_preview.png")
    print("png: Diagnostics\\composite_incremental_x40_expected.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
