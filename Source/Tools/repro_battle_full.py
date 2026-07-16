#!/usr/bin/env python3
"""Полный тест боя: вход (24,16) → Skip (ход AI!) → серия ходов → ПКМ-попап отряда → Auto → финал."""
import struct
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
VM = U / "vmouse.bin"


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


def rmb_hold(x, y, secs):
    """ПКМ: buttons bit1, удержание secs."""
    R.set_pos(x, y)
    time.sleep(0.5)
    t0 = time.time()
    while time.time() - t0 < secs:
        vm(1, 2)
        time.sleep(0.03)


def rmb_release():
    for _ in range(10):
        vm(1, 0)
        time.sleep(0.03)
    R.release_pos()


def snap(tag):
    for _ in range(10):
        try:
            im = Image.open(str(U / "ft812_dump.bmp")).convert("RGB")
            im.save(str(DIAG / f"bf_{tag}.png"))
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
clk(272, 368)
time.sleep(0.5)
clk(272, 368)
ok = False
for t in range(25):
    time.sleep(1)
    if gm() == 2:
        ok = True
        break
print("battle:", ok, flush=True)
time.sleep(6)                        # дождаться конца стрима + первые кадры
snap("1_battle_start")
# --- Skip: передать ход (активный человек → AI пойдёт следом) ---
clk(592, 457)
time.sleep(2)                        # AI-гейт 32 кадра + анимации
snap("2_after_skip")
time.sleep(3)
snap("3_ai_moved")
# --- ещё Skip×2 → второй раунд, AI-ходы (мили должен идти в подход) ---
clk(592, 457)
time.sleep(3)
snap("4_round2")
clk(592, 457)
time.sleep(3)
snap("5_round2b")
# --- ПКМ-попап: зажать ПКМ на своём Peasant (лог ~94,190) ---
rmb_hold(94, 190, 2.5)
snap("6_popup_peasant")              # снап ВО ВРЕМЯ удержания
rmb_release()
time.sleep(1)
snap("7_popup_closed")
# --- ПКМ по вражескому Archer (лог ~572,165) ---
rmb_hold(572, 165, 2.5)
snap("8_popup_enemy_archer")
rmb_release()
time.sleep(1)
# --- Auto: доиграть бой AI vs AI до финала ---
clk(40, 457)
print("auto on", flush=True)
for k in range(30):
    time.sleep(3)
    g = gm(timeout=1.0)
    if g is None:
        print("  !!! не отвечает", flush=True)
        snap(f"9_auto_dead_{k:02d}")
        break
    if k % 4 == 0:
        snap(f"9_auto_{k:02d}")
    print(f"  t={k*3}s gm={g}", flush=True)
snap("A_final")
subprocess.run(["taskkill", "/F", "/IM", "Unreal.exe"], capture_output=True)
print("CLOSED", flush=True)
