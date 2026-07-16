#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def main() -> int:
    path = Path("Source/ASM/generated_background.inc")
    lines = [
        "; Сгенерировано Source/Tools/tile_map_mode.py",
        "; Tile-map mode: фон строится из terrain atlas, не из baked pseudo-DXT.",
        "",
        "BG_DXT_RAW_SIZE      EQU 0",
        "",
        "Background_Upload:",
        "                CALL Terrain_Upload",
        "                RET",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    print("tile-map mode: Background_Upload -> Terrain_Upload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
