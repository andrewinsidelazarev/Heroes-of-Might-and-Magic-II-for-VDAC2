#!/usr/bin/env python3
"""Построчный аудит стоимости рендера FT812 по кадровому DL adventure.

FT812 рендерит DL ПОСТРОЧНО в line-buffer: бюджет строки ≈ такты строки развёртки
(59Гц × 806 строк → ~21мкс → ~1262 такта @ 60МГц). Каждый видимый пиксель битмапа
стоит тактов (PALETTED ≈ 2: чтение индекса + lookup; ARGB4/RGB565 ≈ 1). Превышение
копится → срыв строк с некоторой высоты («экран целый только в верхней четверти»).

Модель ОТНОСИТЕЛЬНАЯ (scissor игнорируем, CLEAR-фон константа) — для сравнения
профилей и поиска перегруженных строк, не абсолютного предсказания.
"""
from __future__ import annotations

import struct
import sys
from collections import defaultdict

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT, attach_hmm2_shadow

VSIZE = 768
# такты/пиксель по формату битмапа (NEAREST, без bilinear)
FMT_COST = {15: 2.0, 6: 1.0, 7: 1.0, 1: 0.125}   # PALETTED4444, ARGB4, RGB565, L1
LINE_BUDGET = 1262  # ~59Гц, 806 строк, 60МГц — ориентир


def main() -> int:
    emu = HMM2FullZ80Emulator(ROOT)
    regs = attach_hmm2_shadow(emu)

    def render_frame(max_steps: int = 30_000_000) -> None:
        regs.tick_frame(emu.ft.ram_dl)
        emu.call(emu.sym["Render_Frame"], max_steps=max_steps)

    emu.call(emu.sym["Platform_Init"], max_steps=4_000_000)
    emu.call(emu.sym["Game_Init"], max_steps=250_000_000)
    emu.ft.ram_g[:] = b"\x00" * len(emu.ft.ram_g)
    emu.call(emu.sym["Adventure_Enter"], max_steps=12_000_000)
    for _ in range(2):
        render_frame()

    dl = bytes(emu.ft.ram_dl[:0x2000])
    cost = [0.0] * VSIZE                      # такты на строку
    contrib = defaultdict(lambda: [0.0] * VSIZE)  # по источникам

    fmt = 15
    size_w = size_h = 0
    lw = 16                                    # LINE_WIDTH (1/16 px радиус)
    prim = 0
    src = 0
    handle = 0
    tag = "?"
    last_line_vertex = None

    for off in range(0, len(dl), 4):
        (word,) = struct.unpack_from("<I", dl, off)
        op = word >> 24
        if word >> 30 == 1:                    # VERTEX2F
            x = (word >> 15) & 0x7FFF
            y = word & 0x7FFF
            if x & 0x4000:
                x -= 0x8000
            if y & 0x4000:
                y -= 0x8000
            xpx, ypx = x / 16.0, y / 16.0
            if prim == 1:                      # BITMAPS
                w = size_w if size_w else 1
                h = size_h if size_h else 1
                c = FMT_COST.get(fmt, 2.0)
                y0 = max(0, int(ypx))
                y1 = min(VSIZE, int(ypx) + h)
                key = f"bmp@{src:06X}({w}x{h})"
                for yy in range(y0, y1):
                    cost[yy] += w * c
                    contrib[key][yy] += w * c
            elif prim in (3, 4):               # LINES / LINE_STRIP
                if prim == 4 and last_line_vertex is not None:
                    x0, y0f = last_line_vertex
                    wpx = max(1.0, lw / 8.0)   # диаметр в px
                    ymin = max(0, int(min(y0f, ypx) - wpx))
                    ymax = min(VSIZE, int(max(y0f, ypx) + wpx) + 1)
                    seg_w = abs(x0 - xpx) + wpx * 2
                    for yy in range(ymin, ymax):
                        cost[yy] += seg_w
                        contrib["line-strip"][yy] += seg_w
                last_line_vertex = (xpx, ypx)
            continue
        if op == 0x01:
            src = word & 0xFFFFF
        elif op == 0x07:
            fmt = (word >> 19) & 31
        elif op == 0x08:
            size_w = (word >> 9) & 511
            size_h = word & 511
        elif op == 0x1F:
            prim = word & 15
            last_line_vertex = None
        elif op == 0x21:
            prim = 0
            last_line_vertex = None
        elif op == 0x0E:
            lw = word & 4095
        elif op == 0x05:
            handle = word & 31
        elif op == 0x00 and word == 0:
            break                              # DISPLAY

    worst = sorted(range(VSIZE), key=lambda y: -cost[y])[:12]
    print(f"бюджет строки ~{LINE_BUDGET} тактов (59Гц/806строк/60МГц), модель относительная")
    print("зоны (среднее/макс тактов):")
    for z0 in range(0, VSIZE, 96):
        zc = cost[z0:z0 + 96]
        print(f"  y={z0:3d}..{z0+95:3d}: avg={sum(zc)/len(zc):7.0f} max={max(zc):7.0f}")
    print("топ-12 тяжёлых строк:")
    for y in worst:
        print(f"  y={y}: {cost[y]:.0f}")
    # разбор состава: строка из «целой» зоны (100) vs строка из битой (300)
    for probe in (100, 200, 300, 460, 650):
        parts = sorted(((contrib[k][probe], k) for k in contrib if contrib[k][probe] > 0), reverse=True)
        total = cost[probe]
        print(f"строка {probe}: всего {total:.0f}")
        for v, k in parts[:8]:
            print(f"    {v:7.0f}  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
