#!/usr/bin/env python3
"""Дамп переменных оверлея города (page #A6) во время удержания клика по жилищу.
TownExitLatch@0x1514, TownHoverIdx@0x1515, TownInfoIdx@0x1516, TownRecruitIdx@0x1519."""
import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DUMP = U / "dump.req"
SD = U / "statedump.bin"

def clk(x, y):
    R.set_pos(x, y); time.sleep(0.45)
    for _ in range(12): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(8):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.2)

def move_to(c, r, s=3.5):
    cx, cy = R.find_tile_pixel(c, r); clk(cx, cy); time.sleep(0.3); clk(cx, cy); time.sleep(s)

def dump_a6():
    if SD.exists(): SD.unlink()
    DUMP.write_bytes(b"A6")
    for _ in range(40):
        time.sleep(0.05)
        if SD.exists(): break
    time.sleep(0.05)
    d = SD.read_bytes()
    return dict(latch=d[0x1514], hover=d[0x1515], info=d[0x1516], recruit=d[0x1519])

def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(15)
    clk(522, 232); time.sleep(7)
    move_to(24, 15); move_to(24, 13)
    for _ in range(16):
        if R.read_state()[5] == 1: break
        time.sleep(0.4)
    print("город gm =", R.read_state()[5])
    # дамп при ПРОСТОМ наведении (без клика)
    R.set_pos(520, 150); time.sleep(1.0)
    print("hover (520,150):", dump_a6())
    # дамп ВО ВРЕМЯ удержания ЛКМ над жилищем
    R.set_pos(520, 150); time.sleep(0.3)
    for _ in range(10): R.write_vm(1, 1, 0, 0); time.sleep(0.03)   # держим ЛКМ
    st = dump_a6()
    for _ in range(8): R.write_vm(1, 1, 0, 0); time.sleep(0.03)    # продолжаем держать
    print("hold LMB (520,150):", st)
    for _ in range(6): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.5)
    print("after release:", dump_a6())

if __name__ == "__main__":
    main()
