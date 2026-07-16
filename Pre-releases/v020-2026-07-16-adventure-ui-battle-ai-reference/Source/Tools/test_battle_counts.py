#!/usr/bin/env python3
"""Реальный flow: меню → New Game → adventure → клик тест-тайла (22,13) → БОЙ.
Захватывает кадр поля боя (ft812_dump.bmp пишется каждый swap) в Diagnostics/battle_counts.png.
Проверяет GameMode==2 (COMBAT). Цель — увидеть динамические счётчики отрядов над юнитами."""
import struct, sys, time, subprocess, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R

UDIR = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DUMP = UDIR / "ft812_dump.bmp"
OUT = Path(__file__).resolve().parents[2] / "Diagnostics" / "battle_counts.png"
EXE = UDIR / "Unreal.exe"


def grab(dst):
    from PIL import Image
    # подождать свежий кадр
    time.sleep(0.6)
    im = Image.open(DUMP).convert("RGB")
    im.save(dst)
    print(f"  кадр -> {dst}")


def main():
    print("0) запуск эмулятора")
    subprocess.Popen([str(EXE), "hmm2_vdac2.spg"], cwd=str(UDIR))
    time.sleep(13)                       # boot до меню
    print("1) New Game (522,232) — первый клик часто съедается, кликаем дважды")
    R.click_at(522, 232, verify=False)
    time.sleep(1)
    print("2) ждём adventure")
    time.sleep(5)
    ux, uy, hv, tx, ty, gm = R.read_state()
    print(f"   gm после New Game = {gm} (0=adventure)")
    if gm != 0:                          # вдруг первый клик съелся — повторить
        R.click_at(522, 232, verify=False)
        time.sleep(5)
    print("3) ищем тест-тайл боя (22,13)")
    cx, cy = R.find_tile_pixel(22, 13)
    print(f"4) клик по тайлу боя пиксель ({cx},{cy})")
    R.click_at(cx, cy, verify=True)
    print("5) ждём стрим HMM2BATL.PAK")
    time.sleep(5)
    ux, uy, hv, tx, ty, gm = R.read_state()
    print(f"   gm в бою = {gm} (2=COMBAT ожидается)")
    print("6) навести курсор на пустую клетку центра поля (для гекс-тени hover)")
    R.set_pos(331, 250)                  # центр поля, пустая клетка
    time.sleep(0.6)
    grab(OUT)
    R.release_pos()
    print("done battle counts test")


if __name__ == "__main__":
    main()
