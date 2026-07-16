#!/usr/bin/env python3
"""Бой с БРОДЯЧИМ МОНСТРОМ: клик на Peasant×80 (25,17) → бой → Auto → финал → возврат на карту
(герой сохраняет позицию!) → повторный клик на труп (боя нет)."""
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
            im.save(str(DIAG / f"mon_{tag}.png"))
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
snap("0_map")                        # монстры на карте (реальные MONS32-иконки)
clk(304, 400)                        # МОНСТР Peasant×80 на тайле (25,17)
time.sleep(0.5)
clk(304, 400)
ok = False
for t in range(25):
    time.sleep(1)
    if gm() == 2:
        ok = True
        break
print("battle vs monster:", ok, flush=True)
if not ok:
    snap("nav_fail")
    subprocess.run(["taskkill", "/F", "/IM", "Unreal.exe"], capture_output=True)
    raise SystemExit(1)
time.sleep(6)
snap("1_battle")                     # армия защитника = Peasant×80 (один стек)
clk(40, 457)                         # Auto — доиграть
res = None
for k in range(40):
    time.sleep(3)
    g = gm(timeout=1.0)
    if k % 5 == 0:
        snap(f"2_auto_{k:02d}")
    if g == 0:
        res = "map"
        break
print("auto done, gm:", gm(), flush=True)
snap("3_final_or_map")
# если ещё на финальном экране (gm=2) — клик для выхода
if gm() == 2:
    clk(320, 240)
    time.sleep(4)
snap("4_back_map")                   # герой ДОЛЖЕН стоять у монстра (не на старте!)
clk(304, 400)                        # повторный клик на труп: боя быть НЕ должно
time.sleep(4)
g = gm()
print("re-click corpse gm:", g, "(0=ok, 2=БАГ повторный бой)", flush=True)
snap("5_after_reclick")
subprocess.run(["taskkill", "/F", "/IM", "Unreal.exe"], capture_output=True)
print("CLOSED", flush=True)
