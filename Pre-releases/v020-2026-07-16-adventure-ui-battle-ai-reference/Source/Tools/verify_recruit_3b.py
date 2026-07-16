#!/usr/bin/env python3
"""3b live-счётчик: открыть Peasant (avail 12) → Dn ×3 (→9) → MAX (→12). Снимки счётчика+total."""
import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"

def clk(x, y):
    R.set_pos(x, y); time.sleep(0.4)
    for _ in range(12): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(8):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.2)

def move_to(c, r, s=3.5):
    cx, cy = R.find_tile_pixel(c, r); clk(cx, cy); time.sleep(0.3); clk(cx, cy); time.sleep(s)

def snap(tag):
    im = Image.open(str(U / "ft812_dump.bmp")).convert("RGB")
    im.crop((420, 380, 760, 610)).save(str(DIAG / f"r3b_{tag}.png"))   # счётчик+стрелки+MAX+total
    print(f"  -> r3b_{tag}.png")

def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(15)
    clk(522, 232); time.sleep(7)
    move_to(24, 15); move_to(24, 13)
    for _ in range(16):
        if R.read_state()[5] == 1: break
        time.sleep(0.4)
    print("город gm =", R.read_state()[5])
    clk(212, 196); time.sleep(0.8)        # открыть Peasant (avail 12)
    snap("open12")
    clk(373, 262); clk(373, 262); clk(373, 262); time.sleep(0.5)   # Dn ×3 → 9
    snap("dn9")
    clk(442, 255); time.sleep(0.5)        # MAX → 12
    snap("max12")
    print("done")

if __name__ == "__main__":
    main()
