#!/usr/bin/env python3
"""Проверка HOVER-статуса (реальные строки fheroes2): навожу курсор на разные клетки, снимаю
статус-бар. Пустая достижимая -> 'Move Peasants here'; враг стрелком -> 'Shoot Peasants';
иначе -> 'Turn N'. Без кликов где можно (hover = set_pos)."""
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


def bar(tag, x, y):
    from PIL import Image
    R.set_pos(x, y); time.sleep(0.7)              # навести и держать (hover)
    im = Image.open(U / "ft812_dump.bmp").convert("RGB")
    Wd, Hd = im.size
    c = im.crop((int(150 / 640 * Wd), int(442 / 480 * Hd), int(510 / 640 * Wd), int(474 / 480 * Hd)))
    c = c.resize((c.width * 3, c.height * 3))
    c.save(DIAG / ("hov_" + tag + ".png"))
    print("bar ->", "hov_" + tag + ".png")


def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(13)
    clk(522, 232); time.sleep(6)
    if R.read_state()[5] != 0:
        clk(522, 232); time.sleep(6)
    cx, cy = R.find_tile_pixel(22, 13); clk(cx, cy); time.sleep(5)
    print("gm", R.read_state()[5])
    bar("0_move", 155, 172)            # пустая достижимая клетка рядом с P40 -> "Move Peasants here"
    bar("1_turn", 551, 172)            # далёкий враг, P40 melee не дотянется -> "Turn 1"
    print("move P40 -> turn to A4 (shooter)")
    clk(155, 172)                      # P40 двигается -> ход A4
    bar("2_shoot", 551, 172)           # враг P20, A4 стрелок -> "Shoot Peasants"
    R.release_pos()
    print("done")


if __name__ == "__main__":
    main()
