#!/usr/bin/env python3
"""Один оптимальный ход активного юнита на ЖИВОМ эмуляторе.
Стрелок -> стреляет ближайшего врага (счётчик падает). Мили -> бьёт соседа, иначе шаг к врагу.
Проверка по RAM (count/cell сменились), снимок кадра."""
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


def colrow(c):
    return c % 11, c // 11


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "act"
    a, u = B.bstate()
    au = u[a]
    foes = [(i, x) for i, x in enumerate(u) if x["side"] != au["side"] and x["count"] > 0]
    if not foes:
        print("врагов нет"); return
    ac, ar = colrow(au["cell"])
    foes.sort(key=lambda t: abs(colrow(t[1]["cell"])[0] - ac) + abs(colrow(t[1]["cell"])[1] - ar))
    ti, tu = foes[0]
    before_cnt = tu["count"]; before_cell = au["cell"]
    print(f"активный idx{a} {B.NAMES[a]} type{au['type']} cell{au['cell']} -> цель idx{ti} {B.NAMES[ti]} cell{tu['cell']} count{before_cnt}")
    shooter = (au["type"] == 1)
    fc, fr = colrow(tu["cell"])
    adj = abs(fc - ac) <= 1 and abs(fr - ar) <= 1
    if shooter or adj:
        x, y = cellxy(tu["cell"])                 # атака: клик по врагу
        print("АТАКА клеткой врага", tu["cell"])
    else:
        step = au["cell"] + (1 if fc > ac else -1)  # шаг к врагу
        x, y = cellxy(step)
        print("ШАГ к врагу, клетка", step)
    clk(x, y); R.release_pos(); time.sleep(0.6)
    a2, u2 = B.bstate()
    Image.open(U / "ft812_dump.bmp").convert("RGB").save(DIAG / (tag + ".png"))
    print(f"ПОСЛЕ: цель count {before_cnt}->{u2[ti]['count']}, активный cell {before_cell}->{u2[a]['cell']}, новый ход idx{a2}")
    print("результат боя:", B.battle_result())


if __name__ == "__main__":
    main()
