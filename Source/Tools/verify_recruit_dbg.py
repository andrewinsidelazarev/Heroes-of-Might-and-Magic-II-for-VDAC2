#!/usr/bin/env python3
"""Фокус-отладка найма: (1) hover (520,150) → статус-бар (какой hover-idx?); (2) ЗАЖАТЬ ЛКМ и снять
кадр ВО ВРЕМЯ удержания (открылся ли диалог найма на первом фрейме нажатия?)."""
import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"

def clk(x, y):
    R.set_pos(x, y); time.sleep(0.45)
    for _ in range(6):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(8):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.2)

def move_to(col, row, settle=3.5):
    cx, cy = R.find_tile_pixel(col, row)
    clk(cx, cy); time.sleep(0.3); clk(cx, cy); time.sleep(settle)

def snap(tag):
    Image.open(str(U / "ft812_dump.bmp")).convert("RGB").save(str(DIAG / f"rdbg_{tag}.png"))
    print(f"  → rdbg_{tag}.png")

def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(15)
    clk(522, 232); time.sleep(7)
    move_to(24, 15); move_to(24, 13)
    for _ in range(16):
        if R.read_state()[5] == 1: break
        time.sleep(0.4)
    print("город gm =", R.read_state()[5])
    # (1) hover статус-бар
    R.set_pos(520, 150); time.sleep(1.2)
    snap("hover_statusbar")
    R.set_pos(520, 150); time.sleep(0.3)
    # (2) ЗАЖАТЬ ЛКМ (без отпускания) и снять кадр во время удержания
    for _ in range(30): R.write_vm(1, 1, 0, 0); time.sleep(0.03)   # держим ~0.9с
    snap("hold_press")                                             # найм должен быть открыт
    for _ in range(6): R.write_vm(1, 0, 0, 0); time.sleep(0.02)    # отпустить
    R.release_pos(); time.sleep(0.8)
    snap("after_release")                                          # после отпускания (должен остаться открыт)
    print("готово")

if __name__ == "__main__":
    main()
