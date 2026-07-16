import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image
U=Path(r"C:/Users/Администратор/Desktop/unreal_x64"); DIAG=Path(__file__).resolve().parents[2]/"Diagnostics"
subprocess.Popen([str(U/"Unreal.exe"),"hmm2_vdac2.spg"],cwd=str(U)); time.sleep(18)
gm=R.read_state()[5]
img=Image.open(str(U/"ft812_dump.bmp")).convert("RGB")
# не чёрный?
ex=img.resize((32,24)); px=list(ex.getdata()); nonblack=sum(1 for r,g,b in px if r+g+b>60)
img.save(str(DIAG/"loader_boot.png"))
print("gm=",gm," ненулевых_пикселей=",nonblack,"/",len(px), flush=True)
print("MENU" if gm==3 else f"gm={gm}", flush=True)
