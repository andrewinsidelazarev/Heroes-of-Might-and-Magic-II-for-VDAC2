import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image
U=Path(r"C:/Users/Администратор/Desktop/unreal_x64"); DIAG=Path(__file__).resolve().parents[2]/"Diagnostics"
DUMPREQ=U/"dump.req"; STATEDUMP=U/"statedump.bin"
def gm():
    if STATEDUMP.exists(): STATEDUMP.unlink()
    DUMPREQ.write_bytes(b"5")
    for _ in range(40):
        time.sleep(0.05)
        if STATEDUMP.exists(): break
    time.sleep(0.05)
    return STATEDUMP.read_bytes()[0x203]
def vm(a,b):
    for _ in range(20):
        try: R.write_vm(a,b,0,0); return
        except PermissionError: time.sleep(0.03)
def clk(x,y):
    R.set_pos(x,y); time.sleep(0.4)
    for _ in range(14): vm(1,1); time.sleep(0.02)
    for _ in range(8): vm(1,0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.35)
def snap(tag):
    im=Image.open(str(U/"ft812_dump.bmp")).convert("RGB"); im.save(str(DIAG/f"wt_{tag}.png"))
    black = im.getbbox() is None                # полностью чёрный кадр = провал, говорим честно
    print(f"== snap {tag}{' [BLACK FRAME!]' if black else ''}", flush=True)
subprocess.Popen([str(U/"Unreal.exe"),"hmm2_vdac2.spg"],cwd=str(U)); time.sleep(18)
for t in range(8):
    if gm()!=3: break
    clk(522,232); time.sleep(2)          # New Game
for t in range(20):
    if gm()==0: break
    time.sleep(1)
snap("1_adventure")                       # карта приключений
cx,cy=R.find_tile_pixel(24,13)
for attempt in range(6):                  # вход в замок: клик-клик + ЖДАТЬ gm=1, иначе ретрай
    clk(cx,cy); clk(cx,cy)
    ok=False
    for t in range(20):
        if gm()==1: ok=True; break
        time.sleep(0.4)
    print(f"== castle entry attempt {attempt}: gm={'1 OK' if ok else gm()}", flush=True)
    if ok: break
else:
    snap("FAIL_no_town")
    raise SystemExit("FAILED: не вошёл в замок (gm!=1)")
snap("2_town")                            # экран города: портрет героя, имя, армия
clk(185,185); clk(185,185); time.sleep(0.6)   # клик по хижине → диалог найма
snap("3_recruit")                         # диалог найма Peasants
clk(270,344); time.sleep(0.6)             # OKAY (нанять)
clk(150,80); time.sleep(0.6)              # клик по замку → окно строительства
snap("4_construction")                    # окно строительства (статусы)
clk(73,342); time.sleep(0.6)              # построить Well
snap("5_built_well")                      # Well построен (галочка + золото)
clk(593,440); time.sleep(0.6)             # EXIT → назад в город
snap("6_town_after")                      # город: гарнизон с нанятыми
print("done", flush=True)
