#!/usr/bin/env python3
"""Добить ЖИВОЙ бой кликами до выбивания стороны -> окно WINLOSE.
Каждый ход: активный бьёт ближайшего врага (стрелок стреляет; мили шагает к врагу, в упор бьёт).
Проверка по RAM после каждого клика. Снимок финального кадра."""
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


def colrow(c):
    return c % 11, c // 11


def clk(x, y):
    R.set_pos(x, y); time.sleep(0.35)
    for _ in range(5):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(18): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(10): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    time.sleep(0.3)


def grab(name):
    Image.open(U / "ft812_dump.bmp").convert("RGB").save(DIAG / name)


def sig(a, u):
    return (a,) + tuple((x["cell"], x["count"]) for x in u)


def main():
    stall = 0
    for step in range(60):
        res = B.battle_result()
        if res != 0:
            print(f"*** БОЙ ОКОНЧЕН: BattleResult={res} ({'Victory' if res==1 else 'Defeat'}) на шаге {step}")
            break
        a, u = B.bstate()
        au = u[a]
        foes = [(i, x) for i, x in enumerate(u) if x["side"] != au["side"] and x["count"] > 0]
        if not foes:
            print("врагов нет"); break
        ac, ar = colrow(au["cell"])
        foes.sort(key=lambda t: max(abs(colrow(t[1]["cell"])[0] - ac), abs(colrow(t[1]["cell"])[1] - ar)))
        ti, tu = foes[0]
        fc, fr = colrow(tu["cell"])
        cheb = max(abs(fc - ac), abs(fr - ar))
        shooter = (au["type"] == 1)
        before = sig(a, u)
        if shooter or cheb <= 1:
            x, y = cellxy(tu["cell"]); what = f"бьёт idx{ti}({B.NAMES[ti]}) cell{tu['cell']}"
        else:
            dc = 1 if fc > ac else (-1 if fc < ac else 0)
            dr = 1 if fr > ar else (-1 if fr < ar else 0)
            step_cell = (ar + dr) * 11 + (ac + dc)
            x, y = cellxy(step_cell); what = f"шаг к idx{ti} -> cell{step_cell}"
        clk(x, y); R.release_pos()
        a2, u2 = B.bstate()
        after = sig(a2, u2)
        ch = "ИЗМ" if after != before else "—"
        print(f"#{step:2} акт idx{a}({B.NAMES[a]}) {what:28} | "
              + " ".join(f"{B.NAMES[i]}={u2[i]['count']:2}" for i in range(4)) + f"  {ch}")
        if after == before:
            stall += 1
            if stall >= 4:
                print("СТОП: 4 хода без изменений"); break
        else:
            stall = 0
    grab("winlose_final.png")
    print("кадр -> winlose_final.png ; BattleResult =", B.battle_result())


if __name__ == "__main__":
    main()
