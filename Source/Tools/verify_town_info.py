#!/usr/bin/env python3
"""Город: правый клик (ПКМ-удержание) по зданию → инфо-попап (рамка + имя + описание).
Снимаю полный кадр при удержании ПКМ над разными зданиями. Реальный Unreal (bt8xxemu)."""
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

def rclick_capture(tag, hx, hy):
    R.set_pos(hx, hy); time.sleep(0.6)               # курсор над зданием (uipos держит)
    for _ in range(24): R.write_vm(1, 2, 0, 0); time.sleep(0.03)  # ПКМ зажата (buttons bit1)
    Image.open(str(U / "ft812_dump.bmp")).convert("RGB").save(str(DIAG / f"town_info_{tag}.png"))
    for _ in range(4): R.write_vm(1, 0, 0, 0); time.sleep(0.02)   # отпустить ПКМ
    R.release_pos(); time.sleep(0.3)
    print(f"  ПКМ ({hx},{hy}) → town_info_{tag}.png")

def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(15)
    clk(522, 232); time.sleep(7)                     # New Game → adventure
    move_to(24, 15); move_to(24, 13)                 # отойти/вернуться на гейт → город
    for _ in range(16):
        if R.read_state()[5] == 1: break
        time.sleep(0.4)
    if R.read_state()[5] != 1:
        print("!! город не открылся"); return
    print("город открыт — снимаю инфо-попапы")
    rclick_capture("castle", 140, 150)               # здание с описанием (Castle/башня)
    rclick_capture("cathedral", 520, 150)            # жилище справа (Cathedral → Recruit Paladin)
    rclick_capture("center", 320, 110)               # центральный замок (Farm/Castle)
    print("снимки инфо-попапов сняты")

if __name__ == "__main__":
    main()
