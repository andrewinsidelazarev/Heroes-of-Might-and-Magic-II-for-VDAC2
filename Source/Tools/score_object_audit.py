#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DIAG = ROOT / "Diagnostics" / "object_group_audit"
BASELINE = ROOT / "Diagnostics" / "hmm2_ft812_snapshot.png"


def components(mask, w, h):
    seen = bytearray(w * h)
    out = []
    for y in range(h):
        for x in range(w):
            pos = y * w + x
            if seen[pos] or not mask[pos]:
                continue
            stack = [(x, y)]
            seen[pos] = 1
            count = 0
            min_x = max_x = x
            min_y = max_y = y
            while stack:
                cx, cy = stack.pop()
                count += 1
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if nx < 0 or ny < 0 or nx >= w or ny >= h:
                        continue
                    npos = ny * w + nx
                    if seen[npos] or not mask[npos]:
                        continue
                    seen[npos] = 1
                    stack.append((nx, ny))
            out.append((count, min_x, min_y, max_x - min_x + 1, max_y - min_y + 1))
    return out


def main() -> int:
    from PIL import Image

    base = Image.open(BASELINE).convert("RGB")
    w, h = base.size
    base_px = list(base.getdata())
    lines = []
    for path in sorted(DIAG.glob("*.png")):
        img = Image.open(path).convert("RGB")
        px = list(img.getdata())
        mask = bytearray(1 if a != b else 0 for a, b in zip(base_px, px))
        comps = components(mask, w, h)
        total = sum(c[0] for c in comps)
        bad = []
        for count, x, y, cw, ch in comps:
            if count < 4:
                continue
            fill = count / float(cw * ch)
            # Длинные плотные горизонтальные/вертикальные плашки обычно являются
            # ошибочным fragment overlay без addon/layer контекста.
            if (cw >= 16 and ch <= 8 and fill > 0.45) or (ch >= 16 and cw <= 8 and fill > 0.45):
                bad.append((count, x, y, cw, ch, fill))
        verdict = "BAD" if bad else "OK"
        worst = max(bad, default=(0, 0, 0, 0, 0, 0), key=lambda item: item[0])
        lines.append(f"{path.stem}: {verdict} diff={total} comps={len(comps)} worst={worst}")
    report = "\n".join(lines) + "\n"
    (DIAG / "score.txt").write_text(report, encoding="utf-8")
    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
