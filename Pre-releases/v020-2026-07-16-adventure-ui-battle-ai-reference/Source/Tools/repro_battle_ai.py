#!/usr/bin/env python3
"""Вход в бой → Skip (ход к AI) → наблюдение: виснет ли ход AI (новый Z80-код)."""
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


def gm(timeout=2.0):
    try:
        if STATEDUMP.exists():
            STATEDUMP.unlink()
        DUMPREQ.write_bytes(b"5")
        t0 = time.time()
        while time.time() - t0 < timeout:
            time.sleep(0.05)
            if STATEDUMP.exists():
                time.sleep(0.05)
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
            im.save(str(DIAG / f"ai_{tag}.png"))
            print(f"== snap {tag}", flush=True)
            return
        except Exception:
            time.sleep(0.3)
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
print("adventure gm:", gm(), flush=True)
# вход в бой: клики по MON-точкам с ретраями (движение героя недетерминированно)
entered = False
for (mx, my) in ((312, 414), (312, 414), (318, 410), (308, 418), (312, 414), (316, 414)):
    clk(mx, my)
    time.sleep(1)
    clk(mx, my)
    for t in range(10):
        time.sleep(1.5)
        g = gm(timeout=1.5)
        if g == 2:
            entered = True
            break
    if entered:
        break
    snap("nav_dbg")
print("battle entered:", entered, "gm:", gm(), flush=True)
if not entered:
    subprocess.run(["taskkill", "/F", "/IM", "Unreal.exe"], capture_output=True)
    print("NAV FAILED — смотри ai_nav_dbg.png", flush=True)
    raise SystemExit(1)
time.sleep(2)
snap("1_battle")                     # проверка: Turn убран, поле цело
# Ход человека → Skip: передать ход (следующим должен пойти AI-юнит защитника)
clk(592, 457)                        # зона Skip (552-632 × 440-474)
time.sleep(1)
snap("2_after_skip")
# AI должен ходить (гейт 32 кадра ≈ 0.6с на ход) — серия наблюдений
for k in range(10):
    time.sleep(2.5)
    g = gm(timeout=1.5)
    snap(f"3_ai_{k:02d}")
    print(f"  t={k*2.5:.0f}s gm={g}", flush=True)
    if g is None:
        print("  !!! эмулятор/Z80 не отвечает", flush=True)
        break
subprocess.run(["taskkill", "/F", "/IM", "Unreal.exe"], capture_output=True)
print("CLOSED", flush=True)
