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
print("adventure gm=",gm(), flush=True)
# к монстру/бою левее замка — обходим замок снизу: (23,14)->(22,14)->(22,13)
for tile in [(23,14),(22,14),(22,13),(22,13)]:
    move_to(*tile)
    if gm()==2: break
for t in range(16):
    if gm()==2: print(f"  БОЙ gm=2", flush=True); break
    time.sleep(0.5)
time.sleep(1.5)
img=Image.open(str(U/"ft812_dump.bmp")).convert("RGB"); img.save(str(DIAG/"scn_battle.png"))
ex=img.resize((40,30)); px=list(ex.getdata()); nonblack=sum(1 for r,g,b in px if r+g+b>60)
print(f"FINAL gm={gm()} nonblack={nonblack}/{len(px)}", flush=True)
