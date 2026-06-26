#!/usr/bin/env python3
"""Авто-бой до финала → снимок окна итога (потери MONS32+счёт / заголовок победы/поражения)."""
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
    clk(522, 232); time.sleep(7)                       # New Game → adventure
    move_to(288, 384)                                  # вход в бой (тайл боя)
    for _ in range(18):
        if R.read_state()[5] == 2: break
        time.sleep(0.4)
    if R.read_state()[5] != 2:
        print("!! в бой не вошли"); return
    clk(48, 457)                                       # кнопка Auto → авто-бой до конца
    aRes = bstate.addr("BattleResult")
    res = 0
    for t in range(220):                               # до ~22с (round-cap=60 + анимации)
        res = bstate.dump_a8()[aRes]
        if res != 0:
            print(f"  t{t}: БОЙ ОКОНЧЕН, BattleResult={res} ({'Victory' if res==1 else 'Defeat'})")
            break
        time.sleep(0.1)
    if res == 0:
        print("!! бой не закончился за лимит"); return
    time.sleep(1.2)                                    # дать окну итога отрисоваться (+потери+заголовок)
    im = Image.open(str(U / "ft812_dump.bmp")).convert("RGB")
    im.save(str(DIAG / "winsummary_full.png"))
    # центр-кроп окна (StandardWindow ×1.6 ≈ 536×678 по центру 1024×768)
    im.crop((240, 60, 790, 720)).save(str(DIAG / "winsummary_dialog.png"))
    print(f"снимки → winsummary_full.png + winsummary_dialog.png (итог={res})")

if __name__ == "__main__":
    main()
