#!/usr/bin/env python3
"""Проверка ЕДИНОГО шрифта статус-бара (normalWhite ×1.6): hover-подсказка (нижняя строка)
+ строка событий (верхняя) должны быть ОДНИМ шрифтом FONT.ICN."""
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"
DUMPREQ = U / "dump.req"
STATEDUMP = U / "statedump.bin"


def gm(timeout=1.5):
    try:
        if STATEDUMP.exists():
            STATEDUMP.unlink()
        DUMPREQ.write_bytes(b"5")
        t0 = time.time()
        while time.time() - t0 < timeout:
            time.sleep(0.04)
            if STATEDUMP.exists():
                time.sleep(0.04)
                return STATEDUMP.read_bytes()[0x203]
    except Exception:
        pass
    return None


def vm(a, b):
    for _ in range(20):
        try:
            R.write_vm(a, b, 0, 0)
            return
        except PermissionError:
            time.sleep(0.03)


def clk(x, y):
    R.set_pos(x, y)
    time.sleep(0.4)
    for _ in range(14):
        vm(1, 1)
        time.sleep(0.02)
    for _ in range(8):
        vm(1, 0)
        time.sleep(0.02)
    R.release_pos()
    time.sleep(0.35)


def snap(tag):
    for _ in range(10):
        try:
            im = Image.open(str(U / "ft812_dump.bmp")).convert("RGB")
            im.save(str(DIAG / f"sf_{tag}.png"))
            print(f"== snap {tag}", flush=True)
            return
        except Exception:
            time.sleep(0.25)
    print(f"== snap {tag} FAILED", flush=True)


proc = subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U))
time.sleep(18)
for t in range(8):
    if gm() != 3:
        break
    clk(522, 232)
    time.sleep(2)
for t in range(25):
    if gm() == 0:
        break
    time.sleep(1)
print("adventure ok", flush=True)
clk(304, 400)                        # монстр Peasant×80 (25,17)
time.sleep(0.5)
clk(304, 400)
ok = False
for t in range(25):
    time.sleep(1)
    if gm() == 2:
        ok = True
        break
print("battle:", ok, flush=True)
if not ok:
    snap("nav_fail")
    subprocess.run(["taskkill", "/F", "/IM", "Unreal.exe"], capture_output=True)
    raise SystemExit(1)
time.sleep(5)
R.set_pos(880, 290)                  # hover на вражеский стек → «Attack Peasants» в нижней строке
time.sleep(2)
snap("1_hover_attack")
R.set_pos(500, 400)                  # hover на пустую достижимую клетку → «Move ... here»
time.sleep(2)
snap("2_hover_move")
R.release_pos()
clk(40, 457)                         # Auto → события
for k in range(12):
    time.sleep(3)
    snap(f"3_evt_{k:02d}")
    if gm(timeout=1.0) != 2:
        break
subprocess.run(["taskkill", "/F", "/IM", "Unreal.exe"], capture_output=True)
print("CLOSED", flush=True)
