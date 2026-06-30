import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
U=Path(r"C:/Users/Администратор/Desktop/unreal_x64"); DUMP=U/"dump.req"; SD=U/"statedump.bin"
def gm(): return R.read_state()[5]
def clk(x,y):
    R.set_pos(x,y); time.sleep(0.45)
    for _ in range(12): R.write_vm(1,1,0,0); time.sleep(0.02)
    for _ in range(8): R.write_vm(1,0,0,0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.2)
def move_to(c,r,s=3.5):
    cx,cy=R.find_tile_pixel(c,r); clk(cx,cy); time.sleep(0.3); clk(cx,cy); time.sleep(s)
def dump():
    if SD.exists(): SD.unlink()
    DUMP.write_bytes(b"A6")
    for _ in range(40):
        time.sleep(0.05)
        if SD.exists(): break
    time.sleep(0.05); d=SD.read_bytes()
    return int.from_bytes(d[0x1618:0x161A],"little"), int.from_bytes(d[0x161A:0x161C],"little")
subprocess.Popen([str(U/"Unreal.exe"),"hmm2_vdac2.spg"],cwd=str(U)); time.sleep(16)
for a in range(6):
    clk(522,232); time.sleep(6)
    if gm()!=3: break
    print(f"retry NewGame {a}", flush=True)
print("after NewGame gm=",gm(), flush=True)
move_to(24,15); move_to(24,13)            # ПРОВЕРЕННАЯ навигация (bl6z136fp открыл город)
for _ in range(16):
    if gm()==1: break
    time.sleep(0.4)
print("after enter gm=",gm(), flush=True)
print("BEFORE gold,avail =", dump(), flush=True)
clk(212,196); time.sleep(0.8)
clk(442,255); time.sleep(0.5)             # MAX -> count=avail
clk(272,343); time.sleep(0.8)             # OKAY -> recruit
print("AFTER  gold,avail =", dump(), flush=True)
