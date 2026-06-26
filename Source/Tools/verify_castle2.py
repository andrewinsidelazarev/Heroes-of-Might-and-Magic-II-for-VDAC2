#!/usr/bin/env python3
"""Чистая проверка фикса входа в замок на РЕАЛЬНОМ эмуляторе.
Шаги: New Game→adventure(gm=0) → курсор реально двигается? → герой реально ИДЁТ вниз? →
клик по замку ИЗДАЛЕКА → вход ТОЛЬКО по прибытии (gm:0→1), не мгновенно.
Читаем настоящие HeroTile/CursorPixel/walk/#51F6 из стейтдампа, не курсорный тайл."""
import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")

def dump():
    sd = U / "statedump.bin"
    if sd.exists(): sd.unlink()
    (U / "dump.req").write_bytes(b"5")
    for _ in range(60):
        time.sleep(0.05)
        if sd.exists(): break
    time.sleep(0.05)
    d = sd.read_bytes()
    w = lambda o: int.from_bytes(d[o:o + 2], "little")
    return dict(gm=d[0x203], curTile=(d[0x204], d[0x205]), curPix=(w(0x20B), w(0x20D)),
                heroTile=(d[0x213], d[0x214]), target=(d[0x215], d[0x216]),
                walk=d[0x27C], m5176=(w(0x1F6), w(0x1F8)))

def clk(x, y):
    """released(гасит залипший latch)→press→released. uipos держит позицию во время нажатия."""
    R.set_pos(x, y); time.sleep(0.45)
    for _ in range(6):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)   # released: сбросить старый HeroFireLatch
    for _ in range(12): R.write_vm(1, 1, 0, 0); time.sleep(0.02)   # press
    for _ in range(8):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)   # release
    R.release_pos(); time.sleep(0.15)

def move_to(x, y):
    """Двухкликовая модель fheroes2: 1-й клик — маршрут, 2-й по той же цели — пойти (walk=1)."""
    clk(x, y); time.sleep(0.25)
    clk(x, y)

def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(14)
    clk(522, 232); time.sleep(7)                                   # New Game → adventure
    s = dump(); print("1) после New Game:", s)
    if s["gm"] != 0:
        print("   !! не вошли в adventure (gm!=0) — стоп"); return

    # 2) курсор реально двигается за uipos? две точки, читаем CursorPixel
    R.set_pos(160, 200); time.sleep(0.5); a = dump()
    R.set_pos(400, 360); time.sleep(0.5); b = dump()
    print("2) курсор: set(160,200)->curPix", a["curPix"], "#5176", a["m5176"],
          "| set(400,360)->curPix", b["curPix"], "#5176", b["m5176"])
    moved = a["curPix"] != b["curPix"]
    print("   курсор ДВИГАЕТСЯ:" , moved)

    # 3) увести героя ВНИЗ: ДВОЙНОЙ клик (288,416)=тайл(24,17). Поллим РЕАЛЬНЫЙ heroTile
    h0 = dump()["heroTile"]
    move_to(288, 416)
    print("3) move_to вниз (24,17), стартовый heroTile", h0)
    walked = False
    for i in range(20):
        s = dump()
        print(f"   t{i}: heroTile={s['heroTile']} target={s['target']} walk={s['walk']} gm={s['gm']}")
        if s["heroTile"] != h0:
            walked = True
        if s["heroTile"] == (24, 17) or s["gm"] != 0:
            break
        time.sleep(0.4)
    print("   герой СДВИНУЛСЯ:", walked)

    # 4) клик по ЗАМКУ (24,13)=пиксель(288,288) ИЗДАЛЕКА → вход по прибытии (двойной клик = пойти)
    move_to(288, 288)
    print("4) move_to замок (24,13) ИЗДАЛЕКА")
    seq = []
    for i in range(26):
        s = dump(); seq.append(s["gm"])
        if i % 4 == 0:
            print(f"   t{i}: gm={s['gm']} heroTile={s['heroTile']} target={s['target']} walk={s['walk']}")
        if s["gm"] == 1:
            break
        time.sleep(0.18)
    print("   gm-seq:", seq)
    first = seq[0]
    if first == 0 and 1 in seq:
        print("ВЕРДИКТ: ФИКС РАБОТАЕТ — герой ШЁЛ (gm=0), вошёл (gm=1) ПО ПРИБЫТИИ")
    elif first == 1:
        print("ВЕРДИКТ: МГНОВЕННЫЙ ВХОД — баг жив")
    else:
        print(f"ВЕРДИКТ: неясно (вход не случился) first={first}; герой_шёл={walked} курсор_двигался={moved}")

if __name__ == "__main__":
    main()
