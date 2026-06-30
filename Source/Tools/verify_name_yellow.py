import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image
U=Path(r"C:/Users/Администратор/Desktop/unreal_x64"); DIAG=Path(__file__).resolve().parents[2]/"Diagnostics"
def gm(): return R.read_state()[5]
def clk(x,y):
    R.set_pos(x,y); time.sleep(0.45)
    for _ in range(12): R.write_vm(1,1,0,0); time.sleep(0.02)
    for _ in range(8): R.write_vm(1,0,0,0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.2)
def move_to(c,r,s=3.5):
    cx,cy=R.find_tile_pixel(c,r); clk(cx,cy); time.sleep(0.3); clk(cx,cy); time.sleep(s)
subprocess.Popen([str(U/"Unreal.exe"),"hmm2_vdac2.spg"],cwd=str(U)); time.sleep(16)
for a in range(6):
    clk(522,232); time.sleep(6)
    if gm()!=3: break
move_to(24,15); move_to(24,13)
for _ in range(16):
    if gm()==1: break
    time.sleep(0.4)
print("enter gm=",gm(), flush=True)
clk(520,150); time.sleep(0.8)     # open Cathedral (Paladin)
Image.open(str(U/"ft812_dump.bmp")).convert("RGB").crop((300,160,724,210)).save(str(DIAG/"name_yellow.png"))
print("snapped", flush=True)
