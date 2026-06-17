#!/usr/bin/env python3
"""Контракт cycle-accurate физ-сима phys_ft812_sim.py.

Проверяет:
  1. Тайминг: запрограммированные прошивкой HCYCLE/VCYCLE/PCLK дают ~59 Гц,
     корректные время строки/кадра/vblank.
  2. Статический пейсинг: без скролла главный цикл идёт ровно ~1 disp-кадр на
     игровую итерацию (свап армируется и латчится через 1 vblank).
  3. Паритет на статике: физическая реконструкция статического кадра совпадает с
     абстрактным растром render_dl_png (gnd-truth) — модели эквивалентны, когда
     гонок нет.
  4. Физический эффект под скроллом: большая RAM_G-заливка не укладывается в
     кадровый бюджет → итерация занимает >1 disp-кадра (просадка частоты),
     чего абстрактный sim (мгновенный DMA) показать не может.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from phys_ft812_sim import PhysFT812Machine, ROOT, reconstruct_frames
from hmm2_ft812_snapshot import render_dl_into
from shadow_ft812 import disasm_dl


def fail(msg: str) -> None:
    raise SystemExit(f"ОШИБКА: {msg}")


def boot(emu: PhysFT812Machine) -> None:
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Adventure_Enter"], max_steps=12_000_000)  # Game_Init стартует в меню; входим в adventure


def run_iters(emu: PhysFT812Machine, n: int) -> list[float]:
    """Возвращает длительность каждой итерации MainLoop в disp-кадрах."""
    fr = emu.frame_seconds()
    durs = []
    for _ in range(n):
        t0 = emu.clock
        emu.call(emu.sym["Input_Poll"], max_steps=400_000)
        emu.call(emu.sym["Game_Update"], max_steps=400_000)
        emu.call(emu.sym["Render_Frame"], max_steps=20_000_000)
        durs.append((emu.clock - t0) / fr)
    return durs


def test_timing(emu: PhysFT812Machine) -> None:
    t = emu.display_timing()
    if not (58.0 <= t.fps <= 60.0):
        fail(f"fps={t.fps:.3f} вне 58..60 (HCYCLE={t.hcycle} VCYCLE={t.vcycle} PCLK={t.pclk_hz})")
    if t.hcycle != 1344 or t.vcycle != 806:
        fail(f"тайминг не VM_1024_768_59Hz: HCYCLE={t.hcycle} VCYCLE={t.vcycle}")
    if abs(t.line_seconds * 1e6 - 21.0) > 0.1:
        fail(f"время строки {t.line_seconds*1e6:.3f} мкс != 21.0")
    print(f"  [1] тайминг OK: fps={t.fps:.3f} Гц, строка={t.line_seconds*1e6:.2f} мкс, кадр={t.frame_seconds*1e3:.2f} мс")


def test_static_pacing(emu: PhysFT812Machine) -> None:
    emu.input.kempston = 0x00  # без скролла
    durs = run_iters(emu, 6)
    durs = durs[1:]  # первый кадр прогрева отбросить
    mean = sum(durs) / len(durs)
    if not (0.8 <= mean <= 1.25):
        fail(f"статический пейсинг {mean:.2f} кадр/итер (ожид ~1.0): {[f'{d:.2f}' for d in durs]}")
    print(f"  [2] статический пейсинг OK: {mean:.2f} disp-кадр/итерация (59 Гц)")


def test_static_parity(emu: PhysFT812Machine) -> None:
    from PIL import Image

    t = emu.display_timing()
    W, H = t.hsize, t.vsize
    # текущий статический кадр уже на экране; снимем базу и один disp-кадр
    base_dl = bytes(emu.ft.ram_dl[:0x2000])
    base_g = bytes(emu.ft.ram_g)
    emu.begin_logging()
    # один спокойный кадр без скролла
    emu.input.kempston = 0x00
    emu.call(emu.sym["Input_Poll"], max_steps=400_000)
    emu.call(emu.sym["Game_Update"], max_steps=400_000)
    t0 = emu.clock
    emu.call(emu.sym["Render_Frame"], max_steps=20_000_000)
    k = t.frame_index(t0) + 1
    if t.frame_index(emu.clock) < k:
        k = t.frame_index(t0)
    phys = reconstruct_frames(t, emu.write_log, base_dl, base_g, [k], W, H)[k]

    # абстрактный gnd-truth: латченный DL кадра k + RAM_G на тот же vblank
    dl = bytearray(base_dl)
    g = bytearray(base_g)
    fstart = k * t.frame_seconds
    for (tt, region, off, data) in sorted(emu.write_log, key=lambda e: e[0]):
        if tt <= fstart:
            (dl if region == "DL" else g)[off:off + len(data)] = data
    ref = Image.new("RGB", (W, H), (0, 0, 0))
    ref_alpha = Image.new("L", (W, H), 0)
    render_dl_into(ref, ref_alpha, disasm_dl(bytes(dl), max_ops=4096), bytes(g), W, H)

    if phys is None:
        fail("статическая реконструкция вернула None")
    pa, pb = phys.load(), ref.load()
    diff = sum(1 for y in range(0, H, 2) for x in range(0, W, 2) if pa[x, y] != pb[x, y])
    if diff != 0:
        out = ROOT / "Diagnostics" / "phys_ft812"
        out.mkdir(parents=True, exist_ok=True)
        phys.save(out / "parity_phys.png")
        ref.save(out / "parity_ref.png")
        fail(f"паритет на статике нарушен: {diff} расхождений (см. {out})")
    print("  [3] паритет на статике OK: физ.реконструкция == абстрактный растр")


def test_scroll_overrun() -> None:
    emu = PhysFT812Machine(ROOT)
    boot(emu)
    # разогрев: один кадр без скролла снимает стартовый #FF-upload композит-тайлов,
    # чтобы дальнейшая просадка была именно эффектом СКРОЛЛА, а не старта.
    emu.input.kempston = 0x00
    run_iters(emu, 1)
    emu.set_word(emu.sym["CursorPixelX"], 624)
    emu.set_word(emu.sym["CursorPixelY"], 224)
    emu.call(emu.sym["Cursor_UpdateTileFromPixel"], max_steps=200_000)
    emu.input.kempston = 0x01  # держим вправо; за 10 итераций origin пересечётся
    durs = run_iters(emu, 10)
    mean = sum(durs) / len(durs)
    worst = max(durs)
    if worst <= 2.0:
        fail(f"под скроллом ожидался stall >2 disp-кадра на пересечении origin, "
             f"worst={worst:.2f} ({[f'{d:.1f}' for d in durs]}) — заливка укладывается в бюджет?")
    print(f"  [4] физический эффект OK: устойчивый скролл mean={mean:.2f} кадр/итер, "
          f"worst stall={worst:.1f} кадра (~{worst*16.93:.0f} мс фриз на перезаливке 225КБ тайлов); "
          f"абстрактный sim показал бы ровно 59 Гц")


def main() -> int:
    print("Контракт phys_ft812_sim:")
    emu = PhysFT812Machine(ROOT)
    boot(emu)
    test_timing(emu)
    test_static_pacing(emu)
    test_static_parity(emu)
    test_scroll_overrun()
    print("OK: cycle-accurate физ-сим валиден (тайминг, пейсинг, паритет, физ-эффект)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
