#!/usr/bin/env python3
"""Город: вход → клик по ЗДАНИЮ не выходит (gm=1) → клик по кнопке EXIT выходит (gm=0). Реальный Unreal."""
import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")

def clk(x, y):
    R.set_pos(x, y); time.sleep(0.45)
    for _ in range(6):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(8):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.2)

def move_to(col, row, settle=3.5):
    cx, cy = R.find_tile_pixel(col, row)
    clk(cx, cy); time.sleep(0.3); clk(cx, cy); time.sleep(settle)

def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(14)
    clk(522, 232); time.sleep(7)                    # New Game → adventure
    move_to(24, 15)                                  # отойти на безопасный тайл
    move_to(24, 13)                                  # вернуться на гейт → город
    for _ in range(16):
        if R.read_state()[5] == 1: break
        time.sleep(0.4)
    gm = R.read_state()[5]
    print("1) вход в город gm =", gm, "→", "ОТКРЫТ ✓" if gm == 1 else "НЕ открыт ✗")
    if gm != 1:
        return
    clk(300, 120)                                    # клик по ЗДАНИЮ замка (не Exit) → должны остаться
    g2 = R.read_state()[5]
    print("2) клик по зданию (300,120): gm =", g2, "→", "ОСТАЛИСЬ ✓" if g2 == 1 else "вышли ✗ (баг)")
    clk(593, 440)                                    # клик по кнопке EXIT (центр 553-633×428-453) → выход
    for _ in range(10):
        if R.read_state()[5] == 0: break
        time.sleep(0.3)
    g3 = R.read_state()[5]
    print("3) клик по EXIT (593,440): gm =", g3, "→", "ВЫШЛИ ✓" if g3 == 0 else "не вышли ✗")

if __name__ == "__main__":
    main()
