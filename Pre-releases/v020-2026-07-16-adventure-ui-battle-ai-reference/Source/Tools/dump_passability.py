#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from map_tools import read_mp2


ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "Assets" / "Original" / "MAPS" / "SKIRMISH.MX2"
PASS = ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.pass.bin"


def main() -> None:
    header, tiles, _addons = read_mp2(MAP)
    masks = PASS.read_bytes()
    width = header["width"]
    origin_x = 8
    origin_y = 0
    view_w = 16
    view_h = 13

    print(f"viewport origin={origin_x},{origin_y} size={view_w}x{view_h}")
    print("mask grid: 00=нельзя, FF=полностью, F8/F* = вход только снизу/сбоку как у крупных объектов")
    for y in range(origin_y, origin_y + view_h):
        row = []
        for x in range(origin_x, origin_x + view_w):
            row.append(f"{masks[y * width + x]:02X}")
        print(f"{y:02d}: " + " ".join(row))

    print()
    print("неполностью проходимые тайлы в этом окне:")
    for y in range(origin_y, origin_y + view_h):
        for x in range(origin_x, origin_x + view_w):
            index = y * width + x
            mask = masks[index]
            if mask == 0xFF:
                continue
            tile = tiles[index]
            print(
                f"{x:02d},{y:02d}: mask={mask:02X} terrain={tile['terrain']} "
                f"map_object={tile['map_object']} obj1={tile['object_name1'] >> 2}:{tile['bottom_icn']} "
                f"layer1={tile['quantity1'] & 3} obj2={tile['object_name2'] >> 2}:{tile['top_icn']}"
            )


if __name__ == "__main__":
    main()
