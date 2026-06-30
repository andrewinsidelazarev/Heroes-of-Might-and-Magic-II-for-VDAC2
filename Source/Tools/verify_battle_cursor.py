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
def snapcur(tag,hx,hy):
    R.set_pos(hx,hy); time.sleep(1.1)
    sx,sy=int(hx*1.6),int(hy*1.6)
    Image.open(str(U/"ft812_dump.bmp")).convert("RGB").crop((sx-6,sy-6,sx+64,sy+64)).save(str(DIAG/f"bcur_{tag}.png"))
    print("  cur",tag,"@",(hx,hy), flush=True)
subprocess.Popen([str(U/"Unreal.exe"),"hmm2_vdac2.spg"],cwd=str(U)); time.sleep(15)
clk(522,232); time.sleep(7)
move_to(288,384)
for i in range(18):
    if gm()==2: break
    time.sleep(0.4)
print("gm бой=",gm(), flush=True)
if gm()!=2: print("!! не в бою"); sys.exit(0)
for tag,hx,hy in [("move",150,250),("own",90,250),("enemy",540,250),("empty",330,140)]:
    snapcur(tag,hx,hy)
print("done", flush=True)
