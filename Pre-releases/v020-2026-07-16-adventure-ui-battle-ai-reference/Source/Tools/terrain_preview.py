#!/usr/bin/env python3
import argparse
import struct
from pathlib import Path


HEADER_SIZE = 10
TILE_SIZE = 8
HEADER_SIZE_V2 = 14
TILE_SIZE_V2 = 20
ADDON_SIZE_V2 = 16
VIEW_W = 20
VIEW_H = 15
TILE_PX = 32


TERRAIN_COLORS = [
    (72, 128, 40),
    (32, 120, 168),
    (184, 160, 72),
    (96, 96, 96),
    (168, 168, 184),
    (48, 112, 72),
    (88, 56, 32),
    (24, 96, 112),
    (136, 72, 40),
    (104, 88, 56),
    (152, 128, 72),
    (64, 104, 48),
]


def read_map(path: Path):
    data = path.read_bytes()
    if len(data) < HEADER_SIZE or data[:4] != b"H2MP":
        raise ValueError(f"{path}: неверный формат compact map")

    version, width, height, _difficulty, tile_count = struct.unpack_from("<BBBBH", data, 4)
    if version not in (1, 2):
        raise ValueError(f"{path}: неподдерживаемая версия {version}")
    if tile_count != width * height:
        raise ValueError(f"{path}: неверное число тайлов")

    tiles = []
    if version == 1:
        if len(data) < HEADER_SIZE + tile_count * TILE_SIZE:
            raise ValueError(f"{path}: файл короче таблицы тайлов")
        offset = HEADER_SIZE
        addons = []
        for _ in range(tile_count):
            terrain, object_name1, bottom_icn, object_name2, top_icn, terrain_flags, map_object = struct.unpack_from("<HBBBBBB", data, offset)
            tiles.append(
                {
                    "terrain": terrain,
                    "object_name1": object_name1,
                    "bottom_icn": bottom_icn,
                    "quantity1": 0,
                    "quantity2": 0,
                    "object_name2": object_name2,
                    "top_icn": top_icn,
                    "terrain_flags": terrain_flags,
                    "map_object": map_object,
                    "next_addon": 0,
                    "uid1": 0,
                    "uid2": 0,
                }
            )
            offset += TILE_SIZE
    else:
        addon_count = struct.unpack_from("<I", data, 10)[0]
        tiles_offset = HEADER_SIZE_V2
        addons_offset = tiles_offset + tile_count * TILE_SIZE_V2
        if len(data) < addons_offset + addon_count * ADDON_SIZE_V2:
            raise ValueError(f"{path}: файл короче таблицы v2")
        offset = tiles_offset
        for _ in range(tile_count):
            terrain, object_name1, bottom_icn, quantity1, quantity2, object_name2, top_icn, terrain_flags, map_object, next_addon, uid1, uid2 = struct.unpack_from(
                "<HBBBBBBBBHII", data, offset
            )
            tiles.append(
                {
                    "terrain": terrain,
                    "object_name1": object_name1,
                    "bottom_icn": bottom_icn,
                    "quantity1": quantity1,
                    "quantity2": quantity2,
                    "object_name2": object_name2,
                    "top_icn": top_icn,
                    "terrain_flags": terrain_flags,
                    "map_object": map_object,
                    "next_addon": next_addon,
                    "uid1": uid1,
                    "uid2": uid2,
                }
            )
            offset += TILE_SIZE_V2
        addons = []
        offset = addons_offset
        for _ in range(addon_count):
            next_addon, object_name1, bottom_icn, quantity, object_name2, top_icn, uid1, uid2 = struct.unpack_from("<HHBBBBII", data, offset)
            addons.append(
                {
                    "next_addon": next_addon,
                    "object_name1": object_name1,
                    "bottom_icn": bottom_icn,
                    "quantity": quantity,
                    "object_name2": object_name2,
                    "top_icn": top_icn,
                    "uid1": uid1,
                    "uid2": uid2,
                }
            )
            offset += ADDON_SIZE_V2

    return width, height, tiles if version == 1 else (tiles, addons)


def color_for_terrain(terrain: int):
    return TERRAIN_COLORS[terrain % len(TERRAIN_COLORS)]


def write_dl(path: Path, width: int, height: int, tiles, origin_x: int, origin_y: int):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "; Сгенерировано Source/Tools/terrain_preview.py",
        "; Первый экран карты: реальные тайлы SKIRMISH, пока цветовой terrain-pass.",
        "",
        "ADVENTURE_DL:",
        "                FT_CLEAR_COLOR_RGB 8, 12, 16",
        "                FT_CLEAR 1, 1, 1",
        "                FT_BEGIN FT_RECTS",
    ]

    for y in range(VIEW_H):
        map_y = origin_y + y
        if map_y >= height:
            continue
        for x in range(VIEW_W):
            map_x = origin_x + x
            if map_x >= width:
                continue
            tile = tiles[map_y * width + map_x]
            red, green, blue = color_for_terrain(tile["terrain"])
            sx = x * TILE_PX
            sy = y * TILE_PX
            ex = sx + TILE_PX - 1
            ey = sy + TILE_PX - 1
            lines.extend(
                [
                    f"                FT_COLOR_RGB {red}, {green}, {blue}",
                    f"                FT_VERTEX2F {sx * 16}, {sy * 16}",
                    f"                FT_VERTEX2F {ex * 16}, {ey * 16}",
                ]
            )

    lines.extend(
        [
            "                FT_END",
            "                FT_COLOR_RGB 224, 208, 152",
            "                FT_BEGIN FT_LINE_STRIP",
            "                FT_VERTEX2F 0, 0",
            f"                FT_VERTEX2F {VIEW_W * TILE_PX * 16}, 0",
            f"                FT_VERTEX2F {VIEW_W * TILE_PX * 16}, {VIEW_H * TILE_PX * 16}",
            f"                FT_VERTEX2F 0, {VIEW_H * TILE_PX * 16}",
            "                FT_VERTEX2F 0, 0",
            "                FT_END",
            "                FT_DISPLAY",
            "ADVENTURE_DL_SIZE EQU $ - ADVENTURE_DL",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Сгенерировать FT812 display list для первого viewport карты HMM2.")
    parser.add_argument("--map", type=Path, default=Path("Assets/Converted/Maps/SKIRMISH.map.bin"))
    parser.add_argument("--out", type=Path, default=Path("Source/ASM/generated_adventure_dl.inc"))
    parser.add_argument("--origin-x", type=int, default=0)
    parser.add_argument("--origin-y", type=int, default=0)
    args = parser.parse_args()

    width, height, map_data = read_map(args.map)
    tiles = map_data[0] if isinstance(map_data, tuple) else map_data
    write_dl(args.out, width, height, tiles, args.origin_x, args.origin_y)
    print(f"{args.out}: viewport {VIEW_W}x{VIEW_H} из {args.map.name}, начало={args.origin_x},{args.origin_y}")


if __name__ == "__main__":
    main()
