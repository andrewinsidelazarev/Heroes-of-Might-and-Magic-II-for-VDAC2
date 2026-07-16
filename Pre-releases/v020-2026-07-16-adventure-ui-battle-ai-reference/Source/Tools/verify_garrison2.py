import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image
U=Path(r"C:/Users/Администратор/Desktop/unreal_x64"); DUMP=U/"dump.req"; SD=U/"statedump.bin"; DIAG=Path(__file__).resolve().parents[2]/"Diagnostics"
def gm(): return R.read_state()[5]
def clk(x,y):
    R.set_pos(x,y); time.sleep(0.45)
    for _ in range(12): R.write_vm(1,1,0,0); time.sleep(0.02)
    for _ in range(8): R.write_vm(1,0,0,0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.2)
def move_to(c,r,s=3.5):
    cx,cy=R.find_tile_pixel(c,r); clk(cx,cy); time.sleep(0.3); clk(cx,cy); time.sleep(s)
def slottypes():
    if SD.exists(): SD.unlink()
    DUMP.write_bytes(b"A6")
    for _ in range(40):
        time.sleep(0.05)
        if SD.exists(): break
    time.sleep(0.05); d=SD.read_bytes()
    return d[0x163E],d[0x163F],d[0x1640]   # GarSlotType[0..2] (slots 2,3,4)
def snap(tag):
    Image.open(str(U/"ft812_dump.bmp")).convert("RGB").crop((160,415,900,575)).save(str(DIAG/f"rgar2_{tag}.png"))
subprocess.Popen([str(U/"Unreal.exe"),"hmm2_vdac2.spg"],cwd=str(U)); time.sleep(16)
for a in range(6):
    clk(522,232); time.sleep(6)
    if gm()!=3: break
move_to(24,15); move_to(24,13)
for _ in range(16):
    if gm()==1: break
    time.sleep(0.4)
print("enter gm=",gm(),"GarSlotType BEFORE=",slottypes(), flush=True)
snap("before")
clk(276,204); time.sleep(0.7)     # open Blacksmith (Pikeman, новый тип idx2)
clk(442,255); time.sleep(0.4)     # MAX
clk(272,343); time.sleep(0.7)     # OKAY recruit
print("GarSlotType AFTER=",slottypes(),"(ожидаю [2,255,255] = Pikeman в слоте2)", flush=True)
snap("after")
print("done", flush=True)
