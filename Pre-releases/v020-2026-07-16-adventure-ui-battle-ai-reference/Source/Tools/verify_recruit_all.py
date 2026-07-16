#!/usr/bin/env python3
"""Проверка ВСЕХ жилищ: переиспользую УЖЕ запущенный Unreal (в городе). Грид-скан хит-карты
(dump A6 → TownHoverIdx), для каждого уникального жилища: открыть найм → снять заголовок."""
import time, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"
DUMP = U / "dump.req"; SD = U / "statedump.bin"
DWELL = {9, 13, 14, 15, 16, 17}     # building idx жилищ

def clk(x, y):
    R.set_pos(x, y); time.sleep(0.4)
    for _ in range(12): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(8):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.2)

def hover_idx(x, y):
    R.set_pos(x, y); time.sleep(0.5)
    if SD.exists(): SD.unlink()
    DUMP.write_bytes(b"A6")
    for _ in range(40):
        time.sleep(0.05)
        if SD.exists(): break
    time.sleep(0.05)
    return SD.read_bytes()[0x1515]    # TownHoverIdx

def main():
    print("gm =", R.read_state()[5], "(1=город)")
    found = {}
    for y in range(80, 230, 25):
        for x in range(60, 610, 45):
            idx = hover_idx(x, y)
            if idx in DWELL and idx not in found:
                found[idx] = (x, y)
                print(f"  жилище idx={idx} @ ({x},{y})")
            if len(found) == len(DWELL):
                break
        if len(found) == len(DWELL):
            break
    print(f"найдено жилищ: {len(found)}/{len(DWELL)} -> {sorted(found)}")
    for idx, (x, y) in sorted(found.items()):
        clk(x, y); time.sleep(0.8)                                  # открыть найм
        Image.open(str(U / "ft812_dump.bmp")).convert("RGB").crop((255, 160, 769, 320)).save(
            str(DIAG / f"recruit_b{idx}.png"))                       # верх окна (заголовок+спрайт+цена)
        print(f"  idx={idx} -> recruit_b{idx}.png")
        clk(x, y); time.sleep(0.6)                                  # закрыть

if __name__ == "__main__":
    main()
