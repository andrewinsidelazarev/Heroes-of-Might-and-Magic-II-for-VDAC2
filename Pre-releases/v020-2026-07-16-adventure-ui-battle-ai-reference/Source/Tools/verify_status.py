#!/usr/bin/env python3
"""Чистая проверка СМЕНЫ статус-сообщения (без RAM-цикла, фикс.клики, ascii-логи).
Вход -> ход P40 (Peasant move = 'Peasants move') -> A4 атакует P20 (Archer shoot = 'Archers shoot').
Снимает статус-бар после каждого -> сравниваем: разные = меняется, одинаковые = баг."""
import sys, time, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"


def clk(x, y):
    R.set_pos(x, y); time.sleep(0.45)
    for _ in range(5): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(20): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    time.sleep(0.4)


def grab_bar(tag):
    from PIL import Image
    R.set_pos(331, 400); time.sleep(0.6)
    im = Image.open(U / "ft812_dump.bmp").convert("RGB")
    Wd, Hd = im.size
    c = im.crop((int(180 / 640 * Wd), int(442 / 480 * Hd), int(500 / 640 * Wd), int(474 / 480 * Hd)))
    c = c.resize((c.width * 3, c.height * 3))
    c.save(DIAG / ("vbar_" + tag + ".png"))
    print("bar ->", "vbar_" + tag + ".png")


def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(13)
    clk(522, 232); time.sleep(6)
    if R.read_state()[5] != 0:
        clk(522, 232); time.sleep(6)
    cx, cy = R.find_tile_pixel(22, 13); clk(cx, cy); time.sleep(5)
    print("gm", R.read_state()[5])
    grab_bar("0_enter")                 # после входа: сообщения нет
    print("action1: P40 move (click 331,250 empty)")
    clk(331, 250)
    grab_bar("1_move")                  # ожид 'Peasants move'
    print("action2: A4 shoot P20 (click 551,172)")
    clk(551, 172)
    grab_bar("2_shoot")                 # ожид 'Archers shoot' (ДОЛЖНО ОТЛИЧАТЬСЯ)
    R.release_pos()
    print("done")


if __name__ == "__main__":
    main()
