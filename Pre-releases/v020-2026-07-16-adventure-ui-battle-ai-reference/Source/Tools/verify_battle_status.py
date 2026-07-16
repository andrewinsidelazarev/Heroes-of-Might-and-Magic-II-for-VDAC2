import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image
U=Path(r"C:/Users/Администратор/Desktop/unreal_x64"); DIAG=Path(__file__).resolve().parents[2]/"Diagnostics"
def gm(): return R.read_state()[5]
def clk(x,y):
    R.set_pos(x,y); time.sleep(0.45)
    for _ in range(6): R.write_vm(1,0,0,0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1,1,0,0); time.sleep(0.02)
    for _ in range(8): R.write_vm(1,0,0,0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.15)
def move_to(x,y): clk(x,y); time.sleep(0.25); clk(x,y)
def snap_status(tag):
    R.set_pos(*tag[1]); time.sleep(1.0)
    Image.open(str(U/"ft812_dump.bmp")).convert("RGB").crop((0,700,1024,768)).save(str(DIAG/f"bst_{tag[0]}.png"))
    print("  snap", tag[0], "@", tag[1], flush=True)
subprocess.Popen([str(U/"Unreal.exe"),"hmm2_vdac2.spg"],cwd=str(U)); time.sleep(15)
clk(522,232); time.sleep(7)
print("gm после NewGame=",gm(), flush=True)
move_to(288,384)
for i in range(18):
    if gm()==2: break
    time.sleep(0.4)
print("gm после подхода=",gm(),"(2=бой)", flush=True)
if gm()!=2:
    print("!! в бой не вошли"); sys.exit(0)
for tag in [("own",(150,250)),("mid",(330,210)),("enemy",(520,250)),("corner",(60,60))]:
    snap_status(tag)
print("done", flush=True)
