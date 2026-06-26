#!/usr/bin/env python3
"""Проверка анимаций движения И атаки: авто-бой, логируем move/atk состояния, снимаем кадр атаки."""
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
    print("авто-бой; ловлю движение+атаку...")
    aMA = bstate.addr("BattleMoveActive"); aAA = bstate.addr("BattleAtkActive")
    aAP = bstate.addr("BattleAtkProg"); aAU = bstate.addr("BattleAtkUnit")
    st = bstate.addr("BattleUnitState")
    nmove = natk = caps = 0
    for t in range(140):
        d = bstate.dump_a8()
        ma, aa, ap, au = d[aMA], d[aAA], d[aAP], d[aAU]
        res = d[bstate.addr("BattleResult")]
        cnts = [d[st + i*5 + 3] | (d[st + i*5 + 4] << 8) for i in range(4)]
        if ma: nmove += 1
        if aa:
            natk += 1
            if caps < 3 and ap in (4, 6, 8):
                Image.open(str(U/"ft812_dump.bmp")).convert("RGB").save(str(DIAG/f"atk_mid{caps}.png"))
                print(f"  СНЯТ кадр АТАКИ: unit={au} prog={ap} counts={cnts}")
                caps += 1
            print(f"  t{t:3} ATK unit={au} prog={ap} counts={cnts}")
        if res != 0:
            print(f"  бой окончен res={res}"); break
        time.sleep(0.05)
    print(f"\nкадров движения={nmove} кадров атаки={natk} снимков атаки={caps}")
    print("ДВИЖЕНИЕ:", "ДА" if nmove else "нет", "| АТАКА-анимация:", "ДА" if natk else "нет")

if __name__ == "__main__":
    main()
