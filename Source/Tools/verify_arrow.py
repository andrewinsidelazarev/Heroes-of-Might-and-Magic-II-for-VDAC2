#!/usr/bin/env python3
"""Авто-бой: ловим летящую стрелу лучника (BattleArrowActive=1), снимаем кадр."""
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
    if R.read_state()[5] != 2:
        print("!! в бой не вошли"); return
    clk(48, 457)
    aA = bstate.addr("BattleArrowActive"); aR = bstate.addr("BattleResult")
    caps = nactive = 0
    for t in range(320):
        d = bstate.dump_a8()
        if d[aA]:
            nactive += 1
            if caps < 4:
                Image.open(str(U / "ft812_dump.bmp")).convert("RGB").save(str(DIAG / f"arrow_{caps}.png"))
                print(f"  t{t}: СТРЕЛА В ПОЛЁТЕ → снято arrow_{caps}.png")
                caps += 1
        if d[aR]:
            print(f"  бой окончен (res={d[aR]})"); break
        time.sleep(0.04)
    print(f"\nстрела-активных проб: {nactive}, снимков: {caps}")
    print("СТРЕЛА:", "ЛЕТАЕТ" if nactive else "не поймана")

if __name__ == "__main__":
    main()
