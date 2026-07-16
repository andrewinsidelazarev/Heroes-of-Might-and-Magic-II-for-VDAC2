#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from agg_tools import read_agg_index
from object_atlas import ICN_BY_OBJECT_TYPE, agg_entry, read_icn
from terrain_preview import VIEW_H, VIEW_W, read_map


ROOT = Path(__file__).resolve().parents[2]
SCREEN_W = VIEW_W + 1
SCREEN_H = VIEW_H + 1


def pack_origin_max(width: int, height: int) -> tuple[int, int]:
    return width - VIEW_W, height - VIEW_H


def add_part(parts: list[dict], tile_x: int, tile_y: int, layer: int, object_name: int, index: int, top: bool) -> None:
    icn_type = object_name >> 2
    icn_name = ICN_BY_OBJECT_TYPE.get(icn_type)
    if icn_name and index != 0xFF:
        parts.append(
            {
                "tile_x": tile_x,
                "tile_y": tile_y,
                "icn": icn_name,
                "index": index,
                "type": icn_type,
                "layer": layer,
                "top": top,
            }
        )


def object_parts_for_screen(width: int, height: int, map_data, origin_x: int, origin_y: int) -> list[dict]:
    tiles, addons = map_data if isinstance(map_data, tuple) else (map_data, [])
    parts = []
    for sy in range(SCREEN_H):
        y = origin_y + sy
        if y >= height:
            continue
        for sx in range(SCREEN_W):
            x = origin_x + sx
            if x >= width:
                continue
            tile = tiles[y * width + x]
            add_part(parts, sx, sy, tile["quantity1"] & 0x03, tile["object_name1"], tile["bottom_icn"], False)
            add_part(parts, sx, sy, 0, tile["object_name2"], tile["top_icn"], True)
            addon_index = tile.get("next_addon", 0)
            guard = 0
            while addon_index > 0 and addon_index < len(addons) and guard < 128:
                addon = addons[addon_index]
                add_part(parts, sx, sy, addon["quantity"] & 0x03, addon["object_name1"], addon["bottom_icn"], False)
                add_part(parts, sx, sy, 0, addon["object_name2"], addon["top_icn"], True)
                addon_index = addon["next_addon"]
                guard += 1
    ground = [part for part in parts if not part["top"]]
    top = [part for part in parts if part["top"]]
    ground.sort(key=lambda item: item["layer"], reverse=True)
    return ground + top


def sprite_sizes(agg_data: bytes, entries) -> dict[tuple[str, int], int]:
    sizes = {}
    icn_cache = {}
    for icn_name in sorted(set(ICN_BY_OBJECT_TYPE.values())):
        try:
            icn_cache[icn_name] = read_icn(agg_entry(agg_data, entries, icn_name))
        except ValueError:
            continue
    for icn_name, sprites in icn_cache.items():
        for index, (header, _encoded) in enumerate(sprites):
            sizes[(icn_name, index)] = header["w"] * header["h"]
    return sizes


def main() -> int:
    parser = argparse.ArgumentParser(description="Посчитать RAM_G-бюджет object sprites для каждого экрана карты.")
    parser.add_argument("--agg", type=Path, default=ROOT / "Assets" / "Original" / "DATA" / "HEROES2.AGG")
    parser.add_argument("--map", type=Path, default=ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.map.bin")
    parser.add_argument("--budget", type=int, default=0x40000, help="Бюджет object cache в RAM_G, байт.")
    parser.add_argument("--object-cache", type=int, default=0x40000, help="Планируемый object cache текущего экрана.")
    parser.add_argument("--actor-budget", type=int, default=0x10000, help="Резерв ARGB4 под героев/врагов/нейтралов поверх карты.")
    parser.add_argument("--overlay-budget", type=int, default=0x4000, help="Резерв под cursor/debug/path/HUD overlay.")
    parser.add_argument("--palette-budget", type=int, default=512, help="Палитра PALETTED4444 в RAM_G.")
    parser.add_argument("--top", type=int, default=12, help="Сколько худших экранов вывести.")
    args = parser.parse_args()

    width, height, map_data = read_map(args.map)
    agg_data, entries = read_agg_index(args.agg)
    sizes = sprite_sizes(agg_data, entries)
    max_x, max_y = pack_origin_max(width, height)

    rows = []
    missing = set()
    for oy in range(max_y + 1):
        for ox in range(max_x + 1):
            parts = object_parts_for_screen(width, height, map_data, ox, oy)
            unique = sorted({(part["icn"], part["index"]) for part in parts})
            total = 0
            for key in unique:
                size = sizes.get(key)
                if size is None:
                    missing.add(key)
                    continue
                total += size
            rows.append(
                {
                    "origin": (ox, oy),
                    "parts": len(parts),
                    "unique": len(unique),
                    "bytes": total,
                    "over": total > args.budget,
                    "sprites": unique,
                }
            )

    rows.sort(key=lambda item: (item["bytes"], item["parts"]), reverse=True)
    worst = rows[0]
    over_count = sum(1 for row in rows if row["over"])

    print(f"карта: {width}x{height}, экран: {SCREEN_W}x{SCREEN_H}, положений: {len(rows)}")
    print(f"object cache budget: {args.budget} байт")
    print(f"worst: origin={worst['origin'][0]},{worst['origin'][1]} parts={worst['parts']} unique={worst['unique']} bytes={worst['bytes']}")
    print(f"over budget screens: {over_count}")
    if missing:
        print(f"missing sprite sizes: {len(missing)}")
        for icn, index in sorted(missing)[:args.top]:
            print(f"  missing {icn}#{index}")

    print("")
    terrain_budget = 450560
    total_plan = terrain_budget + args.object_cache + args.actor_budget + args.overlay_budget + args.palette_budget
    print("RAM_G plan:")
    print(f"  terrain atlas:  {terrain_budget:6d}")
    print(f"  palette:        {args.palette_budget:6d}")
    print(f"  object cache:   {args.object_cache:6d}")
    print(f"  actor ARGB4:    {args.actor_budget:6d}")
    print(f"  overlay reserve:{args.overlay_budget:6d}")
    print(f"  total:          {total_plan:6d} / 1048576")
    print(f"  free:           {1048576 - total_plan:6d}")
    if worst["bytes"] > args.object_cache:
        print(f"  ERROR: worst object screen exceeds planned object cache by {worst['bytes'] - args.object_cache} bytes")
    if total_plan > 1048576:
        print(f"  ERROR: RAM_G plan exceeds limit by {total_plan - 1048576} bytes")

    print("")
    print("top screens:")
    for row in rows[:args.top]:
        mark = " OVER" if row["over"] else ""
        ox, oy = row["origin"]
        print(f"  {ox:02d},{oy:02d}: parts={row['parts']:3d} unique={row['unique']:3d} bytes={row['bytes']:6d}{mark}")

    print("")
    print("worst screen sprites:")
    sprite_rows = []
    for key in worst["sprites"]:
        sprite_rows.append((sizes.get(key, 0), key[0], key[1]))
    for size, icn, index in sorted(sprite_rows, reverse=True)[:args.top]:
        print(f"  {size:6d}  {icn}#{index}")

    return 1 if over_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
