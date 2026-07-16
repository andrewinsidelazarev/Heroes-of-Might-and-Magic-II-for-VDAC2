import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image
U=Path(r"C:/Users/Администратор/Desktop/unreal_x64"); DIAG=Path(__file__).resolve().parents[2]/"Diagnostics"
def gm(): return R.read_state()[5]
def clk(x,y):
    R.set_pos(x,y); time.sleep(0.4)
    for _ in range(12): R.write_vm(1,1,0,0); time.sleep(0.02)
    for _ in range(8): R.write_vm(1,0,0,0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.2)
def move_to(c,r,s=3.5):
    cx,cy=R.find_tile_pixel(c,r); clk(cx,cy); time.sleep(0.3); clk(cx,cy); time.sleep(s)
subprocess.Popen([str(U/"Unreal.exe"),"hmm2_vdac2.spg"],cwd=str(U)); time.sleep(18)
for t in range(8):
    if gm()!=3: break
    clk(522,232); time.sleep(2)
for t in range(20):
    if gm()==0: break
    time.sleep(1)
move_to(24,15); move_to(24,13)
for t in range(60):
    if gm()==1: break
    time.sleep(0.5)
print("town gm=",gm(), flush=True)
clk(520,150); time.sleep(1.0)      # Cathedral → Paladin recruit
Image.open(str(U/"ft812_dump.bmp")).convert("RGB").crop((250,135,775,630)).save(str(DIAG/"recruit_fix.png"))
print("snapped", flush=True)
