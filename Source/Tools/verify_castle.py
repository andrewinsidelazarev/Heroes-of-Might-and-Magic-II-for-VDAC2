#!/usr/bin/env python3
"""Проверка фикса: клик по замку ВЕДЁТ героя (вход по прибытии), а не мгновенный город.
adventure → отвести героя от гейта → кликнуть замок → gm должен остаться 0 (идёт), потом 1 (город)."""
import sys, time, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")


def clk(x, y):
    R.set_pos(x, y); time.sleep(0.4)
    for _ in range(5):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(18): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(10): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.2)


def gm():
    return R.read_state()[5]


def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(13)
    clk(522, 232); time.sleep(6)                       # New Game → adventure
    print("gm после New Game:", gm(), "(ожидаю 0=adventure)")
    # отвести героя от гейта (24,13) вниз на ~3 тайла
    cx, cy = R.find_tile_pixel(24, 16); clk(cx, cy); time.sleep(3.0)
    print("gm после хода вниз:", gm(), "(ожидаю 0=adventure, герой ушёл с гейта)")
    # кликнуть ЗАМОК (24,13) издалека
    cx, cy = R.find_tile_pixel(24, 13); clk(cx, cy)
    seq = []
    for _ in range(22):                                # сэмплируем gm ~3.3с
        seq.append(gm()); time.sleep(0.15)
    print("gm после клика по замку:", seq)
    first = seq[0]
    print("ВЕРДИКТ:", "ФИКС РАБОТАЕТ — герой шёл (gm=0), потом вошёл (gm=1)"
          if (first == 0 and 1 in seq) else
          ("МГНОВЕННЫЙ ВХОД (баг не исправлен)" if first == 1 else f"странно: first={first}"))


if __name__ == "__main__":
    main()
