#!/usr/bin/env python3
"""Драйвер cycle-accurate физ-сима: гоняет реальный MainLoop HMM2 со скриптовым
скроллом и снимает то, что ФИЗИЧЕСКИ на экране (с учётом гонки RAM_DL/RAM_G vs
сканаут луча). Сохраняет PNG отображаемых кадров и отчёт о рассинхроне/tearing.

Пример:
    python -u Source/Tools/phys_ft812_capture.py --frames 12 --scroll right \
        --out Diagnostics/phys_ft812
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from phys_ft812_sim import PhysFT812Machine, ROOT, reconstruct_frames


def boot(emu: PhysFT812Machine) -> None:
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)


_KEMP = {"right": 0x01, "left": 0x02, "down": 0x08, "up": 0x10,
         "br": 0x01 | 0x08, "bl": 0x02 | 0x08, "tr": 0x01 | 0x10, "tl": 0x02 | 0x10}


def setup_scroll(emu: PhysFT812Machine, direction: str) -> None:
    right = "r" in direction or direction == "right"
    down = "d" in direction or direction in ("down", "br", "bl")
    emu.set_word(emu.sym["CursorPixelX"], 624 if right else 16)
    emu.set_word(emu.sym["CursorPixelY"], 460 if down else 224)
    emu.call(emu.sym["Cursor_UpdateTileFromPixel"], max_steps=200_000)
    # Kempston: bit0=right, bit1=left, bit3=down, bit4=up (как в Input).
    emu.input.kempston = _KEMP.get(direction, 0x01)


def position_and_settle(emu: PhysFT812Machine, px: int, py: int) -> None:
    """Прыжок viewport к (px,py) и один кадр без лога, чтобы залить пакет тайлов/
    объектов для этого origin (RuntimeLastOrigin синхронизируется)."""
    emu.set_word(emu.sym["ViewportPixelX"], px)
    emu.set_word(emu.sym["ViewportPixelY"], py)
    emu.call(emu.sym["Viewport_UpdateOriginFromPixel"], max_steps=200_000)
    emu.call(emu.sym["Render_Frame"], max_steps=30_000_000)


def run_mainloop(emu: PhysFT812Machine, frames: int) -> tuple[float, float, list[float]]:
    t0 = emu.clock
    iter_clocks: list[float] = []
    for _ in range(frames):
        emu.call(emu.sym["Input_Poll"], max_steps=400_000)
        emu.call(emu.sym["Game_Update"], max_steps=400_000)
        emu.call(emu.sym["Render_Frame"], max_steps=20_000_000)
        iter_clocks.append(emu.clock)
    return t0, emu.clock, iter_clocks


def diff_count(a, b) -> int:
    if a is None or b is None:
        return -1
    pa = a.load()
    pb = b.load()
    w, h = a.size
    n = 0
    # быстрый сэмплированный диф по сетке (точная попиксельная разница дорога)
    step = 2
    for y in range(0, h, step):
        for x in range(0, w, step):
            if pa[x, y] != pb[x, y]:
                n += 1
    return n * step * step


def main() -> int:
    ap = argparse.ArgumentParser(description="Физический захват кадров HMM2 FT812.")
    ap.add_argument("--frames", type=int, default=12, help="сколько игровых кадров прокрутить")
    ap.add_argument("--scroll", choices=["right", "left", "up", "down", "br", "bl", "tr", "tl"], default="right")
    ap.add_argument("--out", type=Path, default=ROOT / "Diagnostics" / "phys_ft812")
    ap.add_argument("--z80-mhz", type=float, default=14.0)
    ap.add_argument("--dma-mbps", type=float, default=2.14)
    ap.add_argument("--start-x", type=int, default=None, help="прыгнуть viewport к ViewportPixelX перед скроллом")
    ap.add_argument("--start-y", type=int, default=None, help="прыгнуть viewport к ViewportPixelY перед скроллом")
    ap.add_argument("--save-all", action="store_true", help="сохранять PNG всех кадров, не только рваных")
    args = ap.parse_args()

    emu = PhysFT812Machine(
        ROOT,
        z80_hz=int(args.z80_mhz * 1e6),
        dma_bytes_per_sec=args.dma_mbps * 1e6,
    )
    boot(emu)
    timing = emu.display_timing()
    print(f"тайминг: fps={timing.fps:.3f} Гц, строка={timing.line_seconds*1e6:.2f} мкс, "
          f"кадр={timing.frame_seconds*1e3:.2f} мс")

    if args.start_x is not None or args.start_y is not None:
        sx = args.start_x if args.start_x is not None else emu.get_word(emu.sym["ViewportPixelX"])
        sy = args.start_y if args.start_y is not None else emu.get_word(emu.sym["ViewportPixelY"])
        position_and_settle(emu, sx, sy)
        print(f"позиционирование к ViewportPixel=({sx},{sy}), "
              f"origin=({emu.get_byte(emu.sym['ViewportOriginX'])},{emu.get_byte(emu.sym['ViewportOriginY'])})")

    # базовые снимки на момент старта захвата
    base_dl = bytes(emu.ft.ram_dl[:0x2000])
    base_g = bytes(emu.ft.ram_g)
    emu.begin_logging()

    setup_scroll(emu, args.scroll)
    t0, t1, iter_clocks = run_mainloop(emu, args.frames)
    print(f"прогон: {args.frames} кадров, t={t0*1e3:.2f}..{t1*1e3:.2f} мс "
          f"(~{(t1-t0)/timing.frame_seconds:.1f} disp-кадров), записей в лог: {len(emu.write_log)}")

    # диапазон отображаемых кадров (без частичных краёв)
    k_lo = timing.frame_index(t0) + 1
    k_hi = timing.frame_index(t1)
    frame_ids = list(range(k_lo, k_hi))
    if not frame_ids:
        print("ОШИБКА: не набралось целых disp-кадров — увеличь --frames")
        return 1
    print(f"реконструкция disp-кадров {k_lo}..{k_hi-1} ({len(frame_ids)})")

    W, H = timing.hsize, timing.vsize
    physical = reconstruct_frames(timing, emu.write_log, base_dl, base_g, frame_ids, W, H)
    coherent = reconstruct_frames(timing, emu.write_log, base_dl, base_g, frame_ids, W, H, coherent=True)

    args.out.mkdir(parents=True, exist_ok=True)
    torn = []
    for k in frame_ids:
        # сколько записей попало в видимую область этого кадра
        fstart = k * timing.frame_seconds
        vis_lo = fstart + timing.voffset * timing.line_seconds
        vis_hi = fstart + (timing.voffset + H) * timing.line_seconds
        rows = sorted({
            max(0, min(H, math.ceil((t - fstart) / timing.line_seconds) - timing.voffset))
            for (t, _r, _o, _d) in emu.write_log if vis_lo <= t < vis_hi
        })
        d = diff_count(physical[k], coherent[k])
        is_torn = d > 0
        if is_torn:
            torn.append((k, d, rows[:1] + rows[-1:] if rows else []))
        if args.save_all or is_torn:
            physical[k].save(args.out / f"phys_frame_{k:04d}.png")
        if is_torn:
            coherent[k].save(args.out / f"coherent_frame_{k:04d}.png")
        print(f"  кадр {k}: diff(physical,coherent)={d} px; записей-в-видимой={len(rows)} "
              f"{'<-- TEAR/рассинхрон' if is_torn else ''}")

    print()
    if torn:
        print(f"ВОСПРОИЗВЕДЕНО: {len(torn)} рваных/рассинхронных кадров из {len(frame_ids)}.")
        for k, d, rng in torn[:8]:
            seam = f"строки {rng[0]}..{rng[-1]}" if rng else "?"
            print(f"  кадр {k}: {d} px расходятся, {seam}; "
                  f"phys: {args.out / f'phys_frame_{k:04d}.png'}")
    else:
        print("Рассинхрон НЕ воспроизведён в этом прогоне (все кадры когерентны).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
