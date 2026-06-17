#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from agg_tools import read_agg_index
from object_atlas import agg_entry, read_icn
from terrain_preview import read_map
from viewport_pack import build_object_transfer_plan, validate_object_transfer_plan


ROOT = Path(__file__).resolve().parents[2]
RANDOM_MARKER_INDICES = {66, 67, 68, 69, 70}


def fail(message: str) -> None:
    raise SystemExit(f"ОШИБКА: {message}")


def main() -> None:
    width, height, map_data = read_map(ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.map.bin")
    plan = build_object_transfer_plan(width, height, map_data)
    validate_object_transfer_plan(plan)

    markers = []
    converted = []
    for y in range(plan.height):
        for x in range(plan.width):
            for part in plan.dynamic_at(x, y):
                icn = part["icn"].upper()
                if icn == "MONS32.ICN" and part["index"] in RANDOM_MARKER_INDICES:
                    markers.append((x, y, part["index"]))
                if icn == "MINIMON.ICN" and part.get("source_icn", "").upper() == "MONS32.ICN":
                    converted.append((x, y, part["index"]))

    if converted:
        fail(f"random monster markers were converted to MINIMON: {converted[:8]}")
    if len(markers) != 13:
        fail(f"expected 13 visible MONS32 random markers, got {len(markers)}: {markers[:8]}")

    agg_data, entries = read_agg_index(ROOT / "Assets" / "Original" / "DATA" / "HEROES2.AGG")
    mons32_count = len(read_icn(agg_entry(agg_data, entries, "MONS32.ICN")))
    for _, _, index in markers:
        if index >= mons32_count:
            fail(f"MONS32 marker index out of range: {index} >= {mons32_count}")

    print(f"OK: runtime keeps {len(markers)} original MONS32 random monster markers")


if __name__ == "__main__":
    main()
