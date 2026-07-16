#!/usr/bin/env python3
"""Живая инспекция боя: вход → дампы страницы (проба форматов) → Auto → дожать до финала →
прочитать BattleUnitState/BattleStartCnt/BattleCasK0 прямо из дампа."""
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

# оффсеты в оверлее боя (#C000-based → смещение в дампе страницы)
ADDR = {"BattleUnitState": 0xD5BC, "BattleStartCnt": 0xD5EC, "BattleResult": 0xD6D4, "BattleCasK0": 0xD774}


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


def battle_state(tag):
    """Зеркало боя DbgBattleMirror (#AB5C, page6) в dump b'5' @ 0x6B5C."""
    d = dump_req(b"5")
    if not d:
        print(f"[{tag}] нет дампа")
        return
    us = 0x6B5C
    sc = us + 20
    br = sc + 8
    units = []
    for i in range(4):
        o = us + i * 5
        t, c, s = d[o], d[o + 1], d[o + 2]
        cnt = d[o + 3] | (d[o + 4] << 8)
        units.append(f"u{i}(t{t} c{c} s{s} n{cnt})")
    starts = [d[sc + i * 2] | (d[sc + i * 2 + 1] << 8) for i in range(4)]
    k0 = d[br + 1] | (d[br + 2] << 8)
    k1 = d[br + 3] | (d[br + 4] << 8)
    print(f"[{tag}] result={d[br]} units={' '.join(units)} startCnt={starts} CasK0={k0} CasK1={k1}", flush=True)


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
# сравнить контент дампов '5' vs '168' — вообще разный ли
d5 = dump_req(b"5")
d168 = dump_req(b"168")
same = d5 == d168 if (d5 and d168) else None
print("dump'5'==dump'168':", same, flush=True)
clk(304, 400)
time.sleep(0.5)
clk(304, 400)
for t in range(25):
    time.sleep(1)
    if gm() == 2:
        break
print("battle ok", flush=True)
time.sleep(6)
battle_state("start")
clk(40, 457)                     # Auto
for k in range(20):
    time.sleep(4)
    battle_state(f"t{k*4}s")
    d = dump_req(b"5")
    if d and d[0x6B5C + 28] != 0:
        print("RESULT SET — финал", flush=True)
        break
battle_state("final")
for _ in range(3):
    try:
        im = Image.open(str(U / "ft812_dump.bmp")).convert("RGB")
        im.save(str(DIAG / "snap_final.png"))
        break
    except Exception:
        time.sleep(0.3)
subprocess.run(["taskkill", "/F", "/IM", "Unreal.exe"], capture_output=True)
print("CLOSED", flush=True)
