#!/usr/bin/env python3
"""Извлекает таблицу анимации adventure-объектов из OpenHMM2/fheroes2.

fheroes2 хранит число кадров анимации в `map_object_info.cpp`:
    object...emplace_back( MP2::OBJ_ICN_TYPE_XXX, <index>U, ... );
    object...back().animationFrames = N;
Анимированная часть рисуется кадрами icnIndex+1 .. icnIndex+N (см.
maps_tiles_render.cpp: secondaryFrameIndex = icnIndex + (anim % N) + 1).

В порте этих данных нет (CSV object-info не несёт animationFrames), поэтому
вытаскиваем их парсингом оригинала. Выход: CSV (icn, index, frames) — список
анимированных (icn,index) и число кадров.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "OpenHMM2" / "src" / "fheroes2" / "maps" / "map_object_info.cpp"
OUT = ROOT / "Assets" / "Converted" / "Maps" / "object_animation.csv"

# part: emplace_back( MP2::OBJ_ICN_TYPE_<ICN>, <index>U|<index>, ... )
PART_RE = re.compile(r"emplace_back\(\s*MP2::OBJ_ICN_TYPE_([A-Z0-9]+)\s*,\s*(\d+)\s*[Uu]?\b")
ANIM_RE = re.compile(r"\.animationFrames\s*=\s*(\d+)")


def main() -> int:
    if not SRC.exists():
        raise SystemExit(f"ОШИБКА: нет {SRC} (нужен чек-аут OpenHMM2)")
    text = SRC.read_text(encoding="utf-8", errors="replace")

    # (icn, index) -> max frames (часть может встречаться в нескольких объектах)
    anim: dict[tuple[str, int], int] = {}
    last_part: tuple[str, int] | None = None
    for line in text.splitlines():
        m = PART_RE.search(line)
        if m:
            last_part = (f"{m.group(1)}.ICN", int(m.group(2)))
        a = ANIM_RE.search(line)
        if a and last_part is not None:
            frames = int(a.group(1))
            key = last_part
            if frames > anim.get(key, 0):
                anim[key] = frames

    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(anim.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["icn", "index", "frames"])
        for (icn, idx), frames in rows:
            w.writerow([icn, idx, frames])

    icns = sorted({icn for (icn, _idx) in anim})
    print(f"анимированных частей: {len(anim)}; ICN: {len(icns)}")
    print("по ICN:", {icn: sum(1 for (i, _x) in anim if i == icn) for icn in icns})
    print(f"записано: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
