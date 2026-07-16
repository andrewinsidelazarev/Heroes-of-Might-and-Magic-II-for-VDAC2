#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from terrain_preview import TILE_PX, read_map


ROOT = Path(__file__).resolve().parents[2]


def terrain_color(terrain: int) -> tuple[int, int, int]:
    if terrain < 30:
        return (36, 80, 128)
    if terrain < 92:
        return (38, 118, 44)
    if terrain < 146:
        return (180, 184, 190)
    if terrain < 208:
        return (74, 98, 62)
    if terrain < 262:
        return (112, 54, 38)
    if terrain < 321:
        return (150, 106, 54)
    if terrain < 361:
        return (120, 74, 38)
    if terrain < 415:
        return (92, 82, 70)
    return (180, 158, 92)


def pass_color(mask: int) -> tuple[int, int, int, int]:
    if mask == 0x00:
        return (220, 30, 30, 190)
    if mask == 0xFF:
        return (30, 200, 70, 150)
    return (255, 210, 0, 190)


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    grid_color = (0, 0, 0, 55)
    for x in range(width + 1):
        sx = x * TILE_PX
        draw.line((sx, 0, sx, height * TILE_PX), fill=grid_color)
    for y in range(height + 1):
        sy = y * TILE_PX
        draw.line((0, sy, width * TILE_PX, sy), fill=grid_color)


def main() -> None:
    parser = argparse.ArgumentParser(description="Сгенерировать PNG фона карты и карты проходимости.")
    parser.add_argument("--map", type=Path, default=ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.map.bin")
    parser.add_argument("--passability", type=Path, default=ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.pass.bin")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "Diagnostics" / "passability")
    args = parser.parse_args()

    width, height, map_data = read_map(args.map)
    tiles = map_data[0] if isinstance(map_data, tuple) else map_data
    masks = args.passability.read_bytes()
    if len(masks) != width * height:
        raise ValueError(f"{args.passability}: размер {len(masks)} не равен {width * height}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    size = (width * TILE_PX, height * TILE_PX)

    background = Image.new("RGB", size)
    draw_bg = ImageDraw.Draw(background, "RGBA")
    for y in range(height):
        for x in range(width):
            tile = tiles[y * width + x]
            color = terrain_color(tile["terrain"])
            box = (x * TILE_PX, y * TILE_PX, (x + 1) * TILE_PX - 1, (y + 1) * TILE_PX - 1)
            draw_bg.rectangle(box, fill=color)
    draw_grid(draw_bg, width, height)

    pass_img = Image.new("RGBA", size, (0, 0, 0, 255))
    draw_pass = ImageDraw.Draw(pass_img, "RGBA")
    for y in range(height):
        for x in range(width):
            mask = masks[y * width + x]
            box = (x * TILE_PX, y * TILE_PX, (x + 1) * TILE_PX - 1, (y + 1) * TILE_PX - 1)
            draw_pass.rectangle(box, fill=pass_color(mask))
            if mask not in (0x00, 0xFF):
                draw_pass.text((x * TILE_PX + 4, y * TILE_PX + 8), f"{mask:02X}", fill=(0, 0, 0, 255))
    draw_grid(draw_pass, width, height)

    overlay = background.convert("RGBA")
    overlay.alpha_composite(pass_img)

    background_path = args.out_dir / "skirmish_background.png"
    pass_path = args.out_dir / "skirmish_passability.png"
    overlay_path = args.out_dir / "skirmish_passability_overlay.png"
    background.save(background_path)
    pass_img.convert("RGB").save(pass_path)
    overlay.convert("RGB").save(overlay_path)

    print(f"фон: {background_path}")
    print(f"проходимость: {pass_path}")
    print(f"overlay: {overlay_path}")
    print("легенда: зеленый=FF полностью, красный=00 нельзя, желтый=частичная маска направления")


if __name__ == "__main__":
    main()
