# Verify строительства по оригиналу: окно стройки (живые статусы) → построить Archery Range
# (DW2, 1000 злт) → остальные слоты NOT_TODAY (красные, 1 стройка/день) → EXIT → панорама
# показывает НОВОЕ здание → клик по нему (runtime bbox hit) → диалог найма Archers.
import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
from PIL import Image
U = Path(r"C:/Users/Администратор/Desktop/unreal_x64"); DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"
DUMPREQ = U / "dump.req"; STATEDUMP = U / "statedump.bin"
def gm():
    if STATEDUMP.exists(): STATEDUMP.unlink()
    DUMPREQ.write_bytes(b"5")
    for _ in range(40):
        time.sleep(0.05)
        if STATEDUMP.exists(): break
    time.sleep(0.05)
    return STATEDUMP.read_bytes()[0x203]
def vm(a, b):
    for _ in range(20):
        try: R.write_vm(a, b, 0, 0); return
        except PermissionError: time.sleep(0.03)
def clk(x, y):
    R.set_pos(x, y); time.sleep(0.4)
    for _ in range(14): vm(1, 1); time.sleep(0.02)
    for _ in range(8): vm(1, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.35)
def snap(tag):
    for _ in range(30):                          # эмулятор перезаписывает BMP покадрово — ретрай гонки
        try:
            Image.open(str(U / "ft812_dump.bmp")).convert("RGB").save(str(DIAG / f"wb_{tag}.png"))
            print("== snap", tag, flush=True)
            return
        except OSError:
            time.sleep(0.1)
    print("!! snap FAILED", tag, flush=True)
subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(18)
for t in range(8):
    if gm() != 3: break
    clk(522, 232); time.sleep(2)               # New Game
for t in range(20):
    if gm() == 0: break
    time.sleep(1)
cx, cy = R.find_tile_pixel(24, 13); clk(cx, cy); clk(cx, cy)   # в замок
for t in range(30):
    if gm() == 1: break
    time.sleep(0.4)
snap("1_town")                                  # город (панорама: только keep + Thatched Hut)
clk(150, 80); time.sleep(1.8)                   # клик по замку → окно строительства (патчи статусов стримятся)
snap("2_construct_live")                        # живые статусы: DW1 галочка, зелёные ALLOW, красные REQUIRES
clk(217, 37); time.sleep(1.8)                   # построить Archery Range (DW2, ALLOW, 1000 злт)
snap("3_built_dw2")                             # DW2 галочка; ВСЕ прочие NOT_TODAY (красные) — 1 стройка/день
clk(593, 440); time.sleep(1.2)                  # EXIT → город
snap("4_pano_new_building")                     # ★панорама с ПОСТРОЕННЫМ Archery Range
clk(178, 174); time.sleep(1.0)                  # клик по НОВОМУ зданию (runtime bbox) → найм
snap("5_recruit_archers")                       # диалог найма Archers
print("done", flush=True)
