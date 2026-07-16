#!/usr/bin/env python3
"""PROOF соседства на реальном bt8xxemu. P40 (ближний, cell22) кликает далёкого P20 (cell32) —
ЗАБЛОКИРОВАНО (P20 цел, ход НЕ потрачен). Затем P40 двигается на пустую cell23 (клик РАБОТАЕТ,
ход→A4). A4 (стрелок) бьёт P20 → 12. Кадры: enter | после блок+ход | после выстрела."""
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
    Image.open(DUMP).convert("RGB").save(DIAG / f"adj_{tag}.png")
    print(f"  кадр -> adj_{tag}.png")


def hover(x, y):
    R.set_pos(x, y); time.sleep(0.7)


def press():
    for _ in range(4): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(20): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    time.sleep(0.5)


def click(x, y):
    hover(x, y); press()


def main():
    print("0) запуск"); subprocess.Popen([str(EXE), "hmm2_vdac2.spg"], cwd=str(UDIR)); time.sleep(13)
    print("1) New Game"); click(522, 232); time.sleep(6)
    if R.read_state()[5] != 0:
        click(522, 232); time.sleep(6)
    print("2) вход в бой"); cx, cy = R.find_tile_pixel(22, 13); click(cx, cy); time.sleep(5)
    print(f"   gm={R.read_state()[5]}")
    hover(331, 250); grab("0_enter")                    # P40 cell22 слева, P20=20 справа
    print("3) P40(ближний) кликает ДАЛЁКОГО P20 (551,172) — заблокировано")
    click(551, 172)
    print("4) P40 двигается на пустую cell23 (155,172) — клик работает, ход→A4")
    click(155, 172)
    hover(331, 250); grab("1_after_block_move")         # P40 сместился, P20 ВСЁ ЕЩЁ 20
    print("5) A4(стрелок) бьёт P20 (551,172) → 12")
    click(551, 172)
    hover(331, 250); grab("2_after_ranged")             # P20 = 12
    R.release_pos()
    print(f"   итог gm={R.read_state()[5]}"); print("done adj proof")


if __name__ == "__main__":
    main()
