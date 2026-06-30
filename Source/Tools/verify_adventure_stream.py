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
print("boot gm=",gm(), flush=True)        # ждём меню (3)
# клик New Game с ретраем пока в меню
for t in range(8):
    if gm()!=3: break
    clk(522,232); time.sleep(2)
    print(f"  NewGame try {t}: gm={gm()}", flush=True)
# ждём выхода в adventure (gm=0) — идёт стрим карты 2.3МБ
for t in range(30):
    g=gm()
    if g==0: print(f"  adventure через ~{18+t}s, gm=0", flush=True); break
    time.sleep(1.5)
time.sleep(2)
img=Image.open(str(U/"ft812_dump.bmp")).convert("RGB")
ex=img.resize((40,30)); px=list(ex.getdata()); nonblack=sum(1 for r,g,b in px if r+g+b>60)
# зелёный террейн? (G>R и G>B у заметной доли)
green=sum(1 for r,g,b in px if g>r+10 and g>b+10)
img.save(str(DIAG/"adv_stream.png"))
print(f"FINAL gm={gm()} nonblack={nonblack}/{len(px)} green={green}", flush=True)
