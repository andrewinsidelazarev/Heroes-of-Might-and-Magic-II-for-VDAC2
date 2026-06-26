#!/usr/bin/env python3
"""Быстрый захват кадров авто-боя для визуальной проверки анимации СМЕРТИ (падение отряда)."""
import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
import bstate
from PIL import Image

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"

def clk(x, y):
    R.set_pos(x, y); time.sleep(0.45)
    for _ in range(6):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(8):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.15)

def move_to(x, y): clk(x, y); time.sleep(0.25); clk(x, y)

def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(14)
    clk(522, 232); time.sleep(7)
    move_to(288, 384)
    for _ in range(18):
        if R.read_state()[5] == 2: break
        time.sleep(0.4)
    clk(48, 457)
    da = bstate.addr("BattleDeathActive")
    deaths = []
    frames = []
    for i in range(90):                                # ~11с быстрого захвата
        im = Image.open(str(U / "ft812_dump.bmp")).convert("RGB")
        frames.append(im.crop((90, 250, 560, 480)))
        # лёгкая проба death-флага (раз в 5 кадров — дамп медленный)
        if i % 4 == 0:
            d = bstate.dump_a8()
            if d[da]:
                deaths.append(i)
        time.sleep(0.12)
    print("кадры с death-флагом (проба):", deaths)
    # монтаж каждого 6-го кадра
    sel = frames[::6][:14]
    cols = 7
    rows = (len(sel) + cols - 1) // cols
    cw, ch = sel[0].size
    mon = Image.new("RGB", (cw * cols, ch * rows), (0, 0, 0))
    for k, im in enumerate(sel):
        mon.paste(im, ((k % cols) * cw, (k // cols) * ch))
    mon = mon.resize((min(1900, mon.width), int(mon.height * min(1900, mon.width) / mon.width)), Image.NEAREST)
    mon.save(str(DIAG / "death_montage.png"))
    print("монтаж → death_montage.png", "death-кадров:", len(deaths))

if __name__ == "__main__":
    main()
