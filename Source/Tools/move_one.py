#!/usr/bin/env python3
"""Один реальный ход на ЖИВОМ эмуляторе: кликаю пустую клетку справа от P40 -> он туда идёт.
Проверяю по RAM что cell сменился (клик реально сработал), снимаю кадр до/после."""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
import bstate as B
from PIL import Image

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"


def cellxy(c):
    row, col = c // 11, c % 11
    return 89 - (22 if row % 2 else 0) + 44 * col + 22, 62 + 42 * row + 26


def clk(x, y):
    R.set_pos(x, y); time.sleep(0.4)
    for _ in range(5):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(20): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    time.sleep(0.4)


def grab(name):
    Image.open(U / "ft812_dump.bmp").convert("RGB").save(DIAG / name)


def main():
    a0, u0 = B.bstate()
    print("ДО:   активный idx", a0, "P40.cell", u0[0]["cell"])
    grab("turn_before.png")
    tgt = u0[a0]["cell"] + 1                  # одна клетка вправо от активного
    x, y = cellxy(tgt)
    print("кликаю клетку", tgt, "пиксель", x, y)
    clk(x, y)
    R.release_pos(); time.sleep(0.6)
    a1, u1 = B.bstate()
    grab("turn_after.png")
    print("ПОСЛЕ: активный idx", a1, "P40.cell", u1[0]["cell"])
    print("СДВИГ:", "ДА" if u1[0]["cell"] != u0[0]["cell"] else "НЕТ — клик не сработал")


if __name__ == "__main__":
    main()
