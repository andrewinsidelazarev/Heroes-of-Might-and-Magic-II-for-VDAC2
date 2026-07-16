#!/usr/bin/env python3
"""Проверка HP-пула (узел N1): init hp = count×maxHP; атака уменьшает пул, count=ceil(hp/maxHP).
Вход в бой → дамп count+hp → несколько ходов (стрелок бьёт, мили шагает) с показом count+hp."""
import sys, time, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
import bstate as B

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")


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


def hp_pool():
    d = B.dump_a8()
    base = B.addr("BattleUnitHP")
    return [d[base + i * 2] | (d[base + i * 2 + 1] << 8) for i in range(4)]


def show(tag):
    a, u = B.bstate()
    hp = hp_pool()
    line = " | ".join(f"{B.NAMES[i]} c={u[i]['count']:2} hp={hp[i]:3}" for i in range(4))
    an = B.NAMES[a] if a < 4 else f"?{a}"
    print(f"{tag:10} акт={an:3}  {line}")
    return a, u


def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(13)
    clk(522, 232); time.sleep(6)
    if R.read_state()[5] != 0:
        clk(522, 232); time.sleep(6)
    cx, cy = R.find_tile_pixel(22, 13); clk(cx, cy); time.sleep(5)
    print("=== INIT (ожидаю hp = count×maxHP: P40=40 A4=40 P20=20 A2=20) ===")
    show("init")
    print("=== ходы (стрелок бьёт ближайшего; мили шагает к врагу; ждём мили → ответка N2c) ===")
    for step in range(18):
        a, u = B.bstate()
        if a >= 4:                       # плохой active (гонка дампа?) — перечитать
            a, u = B.bstate()
        if a >= 4:
            print(f"#{step} плохой active={a} (пропуск)"); continue
        au = u[a]
        foes = [(i, x) for i, x in enumerate(u) if x["side"] != au["side"] and x["count"] > 0]
        if not foes:
            break
        ac, ar = colrow(au["cell"])
        foes.sort(key=lambda t: max(abs(colrow(t[1]["cell"])[0] - ac), abs(colrow(t[1]["cell"])[1] - ar)))
        ti, tu = foes[0]
        fc, fr = colrow(tu["cell"])
        shooter = (au["type"] == 1)
        if shooter or max(abs(fc - ac), abs(fr - ar)) <= 1:
            x, y = cellxy(tu["cell"])
        else:
            dc = 1 if fc > ac else (-1 if fc < ac else 0)
            dr = 1 if fr > ar else (-1 if fr < ar else 0)
            x, y = cellxy((ar + dr) * 11 + (ac + dc))
        clk(x, y); R.release_pos()
        show(f"#{step}")
    res = B.battle_result()
    print("результат:", res)
    if res != 0:                                   # финал на экране → снять кадр
        time.sleep(0.6)
        from PIL import Image
        Image.open(U / "ft812_dump.bmp").convert("RGB").save(
            Path(__file__).resolve().parents[2] / "Diagnostics" / "finale_now.png")
        print("финал → finale_now.png")


if __name__ == "__main__":
    main()
