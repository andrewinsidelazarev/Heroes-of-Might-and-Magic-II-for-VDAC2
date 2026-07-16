#!/usr/bin/env python3
"""Диагностика «мили не рубятся»: бой с монстром → Auto → плотные кадры 0.7с (двигаются ли
Peasant'ы) + проба dump.req с номером страницы боя (#A8=168) для чтения BattleRound/State."""
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


def dump_req(payload: bytes, timeout=1.5):
    try:
        if STATEDUMP.exists():
            STATEDUMP.unlink()
        DUMPREQ.write_bytes(payload)
        t0 = time.time()
        while time.time() - t0 < timeout:
            time.sleep(0.04)
            if STATEDUMP.exists():
                time.sleep(0.04)
                return STATEDUMP.read_bytes()
    except Exception:
        pass
    return None


def gm():
    d = dump_req(b"5")
    return d[0x203] if d else None


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
            im.save(str(DIAG / f"ml_{tag}.png"))
            return
        except Exception:
            time.sleep(0.2)


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
clk(304, 400)
time.sleep(0.5)
clk(304, 400)
for t in range(25):
    time.sleep(1)
    if gm() == 2:
        break
print("battle ok", flush=True)
time.sleep(6)
# --- проба дампа страницы боя (#A8=168): пробуем разные форматы запроса ---
for pl in (b"168", b"\xa8", b"A8", b"a8"):
    d = dump_req(pl)
    print(f"dump.req={pl!r} -> {len(d) if d else None} bytes", flush=True)
# --- Auto + плотные кадры ---
clk(40, 457)
for k in range(24):
    time.sleep(0.7)
    snap(f"t{k:02d}")
print("frames done", flush=True)
subprocess.run(["taskkill", "/F", "/IM", "Unreal.exe"], capture_output=True)
print("CLOSED", flush=True)
