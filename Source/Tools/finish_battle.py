#!/usr/bin/env python3
"""Доводит бой до конца, управляя ПО СОСТОЯНИЮ ИЗ ОЗУ (bstate) — не вслепую.
Каждый шаг: читает активного юнита и счётчики, выбирает действие (атакующий бьёт живого
защитника; защитник паркуется), кликает реальным инжектом. До разгрома стороны (gm→adventure).
Печатает состояние на каждом шаге."""
import sys, time, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
import bstate as B

UDIR = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
EXE = UDIR / "Unreal.exe"
DUMP = UDIR / "ft812_dump.bmp"
DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"


def cellxy(cell):
    row, col = cell // 11, cell % 11
    x = 89 - (22 if row % 2 else 0) + 44 * col + 22
    y = 62 + 42 * row + 26
    return x, y


def click(x, y):
    R.set_pos(x, y); time.sleep(0.45)
    for _ in range(5): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(20): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    time.sleep(0.4)


def grab(tag):
    from PIL import Image
    time.sleep(0.5)
    Image.open(DUMP).convert("RGB").save(DIAG / f"fin_{tag}.png")


def main():
    print("launch"); subprocess.Popen([str(EXE), "hmm2_vdac2.spg"], cwd=str(UDIR)); time.sleep(13)
    print("New Game"); click(522, 232); time.sleep(6)
    if R.read_state()[5] != 0:
        click(522, 232); time.sleep(6)
    print("enter battle"); cx, cy = R.find_tile_pixel(22, 13); click(cx, cy); time.sleep(5)
    gm = R.read_state()[5]
    print(f"gm={gm}")
    grab("0_start")
    for step in range(40):
        gm = R.read_state()[5]
        if gm != 2:
            print(f"=== БОЙ ОКОНЧЕН, gm={gm} (0=adventure) ===")
            break
        active, units = B.bstate()
        defs = [i for i in (2, 3) if units[i]["count"] > 0]
        if not defs:
            print("=== защитники выбиты ==="); break
        u = units[active]
        st = " | ".join(f"{B.NAMES[i]}={units[i]['count']}@{units[i]['cell']}" for i in range(4))
        if u["side"] == 0:                          # атакующий → бьёт живого защитника
            tgt = (3 if units[3]["count"] > 0 else 2) if active == 0 else (2 if units[2]["count"] > 0 else 3)
            x, y = cellxy(units[tgt]["cell"])
            print(f"шаг{step}: [{st}]  {B.NAMES[active]}(атак) бьёт {B.NAMES[tgt]}@{units[tgt]['cell']}")
            click(x, y)
        else:                                       # защитник → паркуется (не помогаем)
            park = 5 if active == 2 else 6
            x, y = cellxy(park)
            print(f"шаг{step}: [{st}]  {B.NAMES[active]}(защ) паркуется @{park}")
            click(x, y)
    R.release_pos()
    grab("1_end")
    print(f"итог gm={R.read_state()[5]}")


if __name__ == "__main__":
    main()
