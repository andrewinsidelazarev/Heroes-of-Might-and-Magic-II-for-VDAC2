#!/usr/bin/env python3
"""Показать окно WINLOSE: дебаг форсит BattleResult=1 на входе в бой, окно появляется сразу.
Запуск эмулятора -> New Game -> клик по тайлу боя -> снять кадр."""
import sys, time, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"


def clk(x, y):
    R.set_pos(x, y); time.sleep(0.45)
    for _ in range(5):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(20): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    time.sleep(0.4)


def main():
    from PIL import Image
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(13)
    clk(522, 232); time.sleep(6)                       # New Game
    if R.read_state()[5] != 0:
        clk(522, 232); time.sleep(6)
    cx, cy = R.find_tile_pixel(22, 13); clk(cx, cy); time.sleep(5)  # войти в бой
    print("gm", R.read_state()[5])
    R.release_pos(); time.sleep(0.6)
    im = Image.open(U / "ft812_dump.bmp").convert("RGB")
    im.save(DIAG / "winlose_now.png")
    print("SAVED winlose_now.png", im.size)


if __name__ == "__main__":
    main()
