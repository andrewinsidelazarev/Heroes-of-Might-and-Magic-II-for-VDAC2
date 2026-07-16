#!/usr/bin/env python3
"""Город: наведение на здание → имя в статус-баре. Снимаю кадры при разных hover-позициях."""
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

def snap_statusbar(tag):
    im = Image.open(str(U / "ft812_dump.bmp")).convert("RGB")
    im.crop((0, 700, 1024, 768)).save(str(DIAG / f"town_status_{tag}.png"))   # нижний статус-бар

def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(15)
    clk(522, 232); time.sleep(7)
    move_to(24, 15); move_to(24, 13)
    for _ in range(16):
        if R.read_state()[5] == 1: break
        time.sleep(0.4)
    if R.read_state()[5] != 1:
        print("!! город не открылся"); return
    print("город открыт")
    for tag, (hx, hy) in [("castle", (320, 110)), ("left", (140, 150)), ("right", (520, 150)), ("bg", (320, 250))]:
        R.set_pos(hx, hy); time.sleep(1.2)
        snap_statusbar(tag)
        print(f"  hover ({hx},{hy}) → town_status_{tag}.png")
    print("снимки статус-бара сняты")

if __name__ == "__main__":
    main()
