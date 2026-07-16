#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from agg_tools import read_agg_index
from object_atlas import ICN_BY_OBJECT_TYPE, agg_entry, read_icn, read_palette
from terrain_preview import read_map
from viewport_pack import (
    object_info_for_part,
    object_type_for_part,
    part_is_dynamic,
    split_static_dynamic_parts,
    tile_object_parts_original,
)


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    width, height, map_data = read_map(ROOT / "Assets/Converted/Maps/SKIRMISH.map.bin")
    tiles, addons = map_data
    _agg_data, _entries = read_agg_index(ROOT / "Assets/Original/DATA/HEROES2.AGG")
    for y in range(height):
        for x in range(width):
            parts = tile_object_parts_original(tiles[y * width + x], addons, x, y)
            if not parts:
                continue
            names = [part["icn"] for part in parts]
            if not any("X_LOC" in name or "OBJN" in name or "MTN" in name or "SPH" in name.upper() for name in names):
                continue
            static_parts, dynamic_parts = split_static_dynamic_parts(parts)
            for part in parts:
                if "SPH" not in part["icn"].upper() and part["index"] not in range(0, 256):
                    continue
                info = object_info_for_part(part)
                print(
                    f"tile={x},{y} icn={part['icn']} idx={part['index']} uid={part['uid']} "
                    f"obj_name={part['object_name']} type={object_type_for_part(part)} "
                    f"info={info} dynamic={part in dynamic_parts} static={part in static_parts}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
