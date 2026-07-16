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
subprocess.Popen([str(U/"Unreal.exe"),"hmm2_vdac2.spg"],cwd=str(U)); time.sleep(18)
print("menu gm=",gm(), flush=True)
g0=gm()
for t in range(6):
    clk(448,145); time.sleep(1.5)      # High Scores зона
    if gm()!=g0: break
    print(f"  HiScores try {t}: gm={gm()}", flush=True)
time.sleep(2)
img=Image.open(str(U/"ft812_dump.bmp")).convert("RGB"); img.save(str(DIAG/"scn_hisc.png"))
ex=img.resize((40,30)); px=list(ex.getdata()); nonblack=sum(1 for r,g,b in px if r+g+b>60)
print(f"FINAL gm={gm()} (было {g0}) nonblack={nonblack}/{len(px)}", flush=True)
