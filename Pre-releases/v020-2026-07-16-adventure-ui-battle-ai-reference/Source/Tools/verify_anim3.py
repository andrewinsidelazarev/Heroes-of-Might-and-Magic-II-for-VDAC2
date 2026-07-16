#!/usr/bin/env python3
"""Авто-бой: ловим атаку И смерть, снимаем кадры."""
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
        print("!! не вошли"); return
    clk(48, 457)
    aAA = bstate.addr("BattleAtkActive"); aDA = bstate.addr("BattleDeathActive"); aDP = bstate.addr("BattleDeathProg")
    natk = ndeath = capA = capD = 0
    for t in range(160):
        d = bstate.dump_a8()
        aa, da, dp = d[aAA], d[aDA], d[aDP]
        res = d[bstate.addr("BattleResult")]
        if aa:
            natk += 1
            if capA < 1:
                Image.open(str(U/"ft812_dump.bmp")).convert("RGB").save(str(DIAG/"anim_attack.png")); capA += 1
        if da:
            ndeath += 1
            if capD < 2 and dp in (8, 14):
                Image.open(str(U/"ft812_dump.bmp")).convert("RGB").save(str(DIAG/f"anim_death{capD}.png"))
                print(f"  СНЯТ СМЕРТЬ prog={dp}"); capD += 1
            print(f"  t{t:3} DEATH prog={dp}")
        if res != 0:
            print(f"res={res}"); break
        time.sleep(0.05)
    print(f"\nатака={natk} смерть={ndeath} (снимков атаки={capA} смерти={capD})")
    print("АТАКА:", "ДА" if natk else "нет", "| СМЕРТЬ:", "ДА" if ndeath else "нет")

if __name__ == "__main__":
    main()
