#!/usr/bin/env python3
"""Проверка idle-анимации бойцов: войти в бой, снять N кадров с интервалом, сравнить регион юнита.
Меняются пиксели спрайта между кадрами → бойцы анимируются (дыхание)."""
import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image, ImageChops

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"

def clk(x, y):
    R.set_pos(x, y); time.sleep(0.45)
    for _ in range(6):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(8):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.15)

def move_to(x, y):
    clk(x, y); time.sleep(0.25); clk(x, y)

def snap(name):
    Image.open(str(U / "ft812_dump.bmp")).convert("RGB").save(str(DIAG / name))
    return Image.open(str(DIAG / name)).convert("RGB")

def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(14)
    clk(522, 232); time.sleep(7)                       # New Game → adventure
    move_to(288, 384)                                  # → тайл боя (24,16)
    for _ in range(18):
        if R.read_state()[5] == 2:
            break
        time.sleep(0.4)
    if R.read_state()[5] != 2:
        print("!! в бой не вошли"); return
    print("в бою, снимаю кадры анимации...")
    frames = []
    for i in range(6):
        frames.append(snap(f"anim_f{i}.png"))
        time.sleep(0.22)                               # > 8 гейм-кадров (кадр idle сменится)
    # дифф боевого поля (y<700 физ; исключаем панель/курсор) между последовательными кадрами
    print("changed-pixels (поле боя) между кадрами:")
    for i in range(1, len(frames)):
        d = ImageChops.difference(frames[i-1].crop((0, 80, 1024, 690)),
                                  frames[i].crop((0, 80, 1024, 690)))
        bbox = d.getbbox()
        changed = sum(1 for p in d.getdata() if p != (0, 0, 0))
        print(f"  f{i-1}->f{i}: changed={changed} bbox={bbox}")
    # склейка кропа одного бойца (левый Peasant ~cell22) для глаз
    crop = []
    for i in range(6):
        crop.append(frames[i].crop((150, 250, 320, 470)))
    strip = Image.new("RGB", (170*6, 220))
    for i, c in enumerate(crop):
        strip.paste(c, (170*i, 0))
    strip.resize((170*6*2, 440), Image.NEAREST).save(str(DIAG / "anim_strip.png"))
    print("полоска кадров бойца → anim_strip.png")

if __name__ == "__main__":
    main()
