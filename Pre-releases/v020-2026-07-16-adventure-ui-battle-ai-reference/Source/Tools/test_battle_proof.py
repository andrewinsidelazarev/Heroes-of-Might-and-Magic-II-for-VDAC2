#!/usr/bin/env python3
"""PROOF на реальном bt8xxemu: баг-фикс урона КАДРАМИ + подтверждение наведения перед кликом.
Сценарий: вход → навёл A2 (cell43) → клик (P40 убивает A2, ход→A4) →
навёл P20 (cell32) → клик (A4 бьёт P20 = 20-8 = 12, partial). Кадр перед каждым кликом
показывает, на ТУ ли клетку легла гекс-тень."""
import sys, time, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R

UDIR = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DUMP = UDIR / "ft812_dump.bmp"
DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"
EXE = UDIR / "Unreal.exe"


def grab(tag):
    from PIL import Image
    time.sleep(0.6)
    Image.open(DUMP).convert("RGB").save(DIAG / f"proof_{tag}.png")
    print(f"  кадр -> proof_{tag}.png")


def hover(x, y):
    R.set_pos(x, y); time.sleep(0.7)          # навести и держать (uipos.req)


def press():                                   # клик БЕЗ смены позиции (курсор уже наведён)
    for _ in range(4): R.write_vm(1, 0, 0, 0); time.sleep(0.02)   # гарантир. «отпущено» (сброс latch)
    for _ in range(20): R.write_vm(1, 1, 0, 0); time.sleep(0.02)  # ЛКМ нажата
    for _ in range(12): R.write_vm(1, 0, 0, 0); time.sleep(0.02)  # отпущена
    time.sleep(0.5)


def main():
    print("0) запуск"); subprocess.Popen([str(EXE), "hmm2_vdac2.spg"], cwd=str(UDIR)); time.sleep(13)
    print("1) New Game"); hover(522, 232); press(); time.sleep(6)
    if R.read_state()[5] != 0:
        hover(522, 232); press(); time.sleep(6)
    print("2) вход в бой"); cx, cy = R.find_tile_pixel(22, 13); hover(cx, cy); press(); time.sleep(5)
    print(f"   gm={R.read_state()[5]} (2=бой)")
    hover(331, 250); grab("0_enter")                    # старт 40,4 | 20,2
    print("3) навожу на A2 (cell43, 529,214)"); hover(529, 214); grab("1_hover_a2")
    print("   клик -> P40 убивает A2"); R.set_pos(529, 214); time.sleep(0.4); press()
    hover(331, 250); grab("2_after_atk1")               # A2 исчез
    print("4) навожу на P20 (cell32, 551,172)"); hover(551, 172); grab("3_hover_p20")
    print("   клик -> A4 бьёт P20 (=12)"); R.set_pos(551, 172); time.sleep(0.4); press()
    hover(331, 250); grab("4_after_atk2")               # P20 = 12 (ДОКАЗАТЕЛЬСТВО)
    R.release_pos()
    print(f"   итог gm={R.read_state()[5]}"); print("done proof")


if __name__ == "__main__":
    main()
