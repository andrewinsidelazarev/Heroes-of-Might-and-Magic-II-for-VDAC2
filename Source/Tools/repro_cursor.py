#!/usr/bin/env python3
"""Проверка faithful-курсоров боя: WAR_POINTER на панели, направленный МЕЧ на враге-соседе.
Скипаем ходы, пока монстр не подойдёт вплотную (клетка из DbgBattleMirror), затем hover."""
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
MIRROR = 0xABA4 - 0x4000            # DbgBattleMirror в дампе page5 (окно #4000)
CELL_W, CELL_H, CELL_OX, CELL_OY, ROW_STEP, WIC = 44, 52, 89, 62, 42, 11


def dump(timeout=1.5):
    try:
        if STATEDUMP.exists():
            STATEDUMP.unlink()
        DUMPREQ.write_bytes(b"5")
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
    d = dump()
    return d[0x203] if d else None


def units():
    d = dump()
    if not d:
        return []
    out = []
    for i in range(8):
        t, c, s, lo, hi = d[MIRROR + i * 5: MIRROR + i * 5 + 5]
        out.append((t, c, s, lo | (hi << 8)))
    return out


def cell_center(cell):
    # ЛОГИЧЕСКИЕ координаты 640×480 (vmouse/uipos работают в них)
    row, col = cell // WIC, cell % WIC
    px = CELL_OX - (CELL_W // 2 if row % 2 else 0) + CELL_W * col
    py = CELL_OY + ROW_STEP * row
    return px + CELL_W // 2, py + CELL_H // 2


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
            im.save(str(DIAG / f"cur_{tag}.png"))
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
clk(304, 400)
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
    subprocess.run(["taskkill", "/F", "/IM", "Unreal.exe"], capture_output=True)
    raise SystemExit(1)
time.sleep(5)
R.set_pos(400, 465)                  # ПАНЕЛЬ (вне поля, лог.) → обычная стрелка WAR_POINTER
time.sleep(2)
snap("1_pointer_panel")
us0 = units()
mons0 = [c for (t, c, s, cnt) in us0 if s == 1 and cnt > 0]
if mons0:
    hx, hy = cell_center(mons0[0])   # hover на дальнего врага (актив — лучник) → «Shoot X (N shots left)»
    R.set_pos(hx, hy)
    time.sleep(2)
    snap("1b_shoot_hover")
    d = dump()
    if d:
        print(f"  dbg 1b: mouse_log=({hx},{hy}) msg={d[MIRROR + 33]} sprite={d[0x23F]}", flush=True)
R.release_pos()
# скипаем ходы, пока монстр (side=1) не станет соседом нашего Peasant (side=0, type=0)
sword_done = False
for rnd in range(14):
    us = units()
    mine = [(t, c) for (t, c, s, cnt) in us if s == 0 and cnt > 0]
    mons = [(t, c) for (t, c, s, cnt) in us if s == 1 and cnt > 0]
    print("rnd", rnd, "mine", mine, "mons", mons, flush=True)
    if not mons or not mine:
        break
    mc = mons[0][1]
    # сосед ли монстр какого-то нашего? (гекс-смежность приближённо: |dr|<=1 и колонки рядом)
    def adjacent(a, b):
        ra, ca = a // WIC, a % WIC
        rb, cb = b // WIC, b % WIC
        if ra == rb:
            return abs(ca - cb) == 1
        if abs(ra - rb) == 1:
            odd = ra % 2
            return cb in ((ca - 1, ca) if odd else (ca, ca + 1))
        return False
    if any(adjacent(c, mc) for (_t, c) in mine):
        x, y = cell_center(mc)       # лог. центр клетки монстра
        for tag, (hx, hy) in (("2_sword_left", (x - 12, y)), ("3_sword_tl", (x - 10, y - 14)),
                              ("4_sword_bl", (x - 10, y + 14))):
            R.set_pos(hx, hy)
            time.sleep(2)
            snap(tag)
            d = dump()
            if d:
                import struct
                msg = d[MIRROR + 33]
                dx = struct.unpack_from("<h", d, MIRROR + 34)[0]
                dy = struct.unpack_from("<h", d, MIRROR + 36)[0]
                dirc, hov, act = d[MIRROR + 38], d[MIRROR + 39], d[MIRROR + 40]
                spr = d[0x23F]       # CursorSpriteIndex (#423F, page5-окно #4000)
                print(f"  dbg {tag}: mouse_log=({hx},{hy}) msg={msg} cell={hov} act={act} "
                      f"dx={dx} dy={dy} dirC={dirc} sprite={spr}", flush=True)
        R.release_pos()
        sword_done = True
        break
    clk(612, 460)                    # SKIP (лог.) — пропустить наш ход (монстр подойдёт сам)
    time.sleep(3)
print("sword hover done:", sword_done, flush=True)
subprocess.run(["taskkill", "/F", "/IM", "Unreal.exe"], capture_output=True)
print("CLOSED", flush=True)
