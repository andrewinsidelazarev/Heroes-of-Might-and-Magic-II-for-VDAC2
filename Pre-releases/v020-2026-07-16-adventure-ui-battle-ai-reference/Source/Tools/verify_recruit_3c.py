#!/usr/bin/env python3
"""3c реальный найм: дамп казны/доступного → открыть Peasant → Dn×5 → OKAY (найм) →
дамп (золото и DwellAvail[0] списаны) → переоткрыть (Available уменьшилось). bt8xxemu."""
import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"
DUMP = U / "dump.req"; SD = U / "statedump.bin"

def clk(x, y):
    R.set_pos(x, y); time.sleep(0.4)
    for _ in range(12): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(8):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.2)

def move_to(c, r, s=3.5):
    cx, cy = R.find_tile_pixel(c, r); clk(cx, cy); time.sleep(0.3); clk(cx, cy); time.sleep(s)

def dump():
    if SD.exists(): SD.unlink()
    DUMP.write_bytes(b"A6")
    for _ in range(40):
        time.sleep(0.05)
        if SD.exists(): break
    time.sleep(0.05)
    d = SD.read_bytes()
    gold = int.from_bytes(d[0x1618:0x161A], "little")
    av0  = int.from_bytes(d[0x161A:0x161C], "little")     # DwellAvail[0] = Peasant
    return gold, av0

def snap(tag):
    Image.open(str(U / "ft812_dump.bmp")).convert("RGB").crop((255, 380, 769, 620)).save(str(DIAG / f"r3c_{tag}.png"))

def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(15)
    clk(522, 232); time.sleep(7)
    move_to(24, 15); move_to(24, 13)
    for _ in range(16):
        if R.read_state()[5] == 1: break
        time.sleep(0.4)
    print("город gm =", R.read_state()[5])
    print("ДО:   gold, Peasant avail =", dump())
    clk(212, 196); time.sleep(0.8)                 # открыть Peasant
    snap("open")
    for _ in range(5): clk(373, 262)               # Dn ×5
    time.sleep(0.3); snap("after_dn")
    clk(272, 343); time.sleep(0.8)                 # OKAY → найм
    print("ПОСЛЕ: gold, Peasant avail =", dump())
    clk(212, 196); time.sleep(0.8)                 # переоткрыть Peasant
    snap("reopen")
    clk(440, 345)                                  # закрыть (CANCEL)
    print("done")

if __name__ == "__main__":
    main()
