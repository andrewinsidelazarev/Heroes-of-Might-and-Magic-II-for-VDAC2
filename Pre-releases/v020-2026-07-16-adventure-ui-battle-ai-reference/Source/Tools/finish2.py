#!/usr/bin/env python3
"""Умный финишер боя по ОЗУ (учёт соседства melee): доводит до победы → экран результата.
Атакующий: стрелок бьёт защитника издали; ближний — если сосед, бьёт, иначе идёт к нему вплотную.
Защитник: паркуется. Цикл до BattleResult!=0, потом снимает кадр итога."""
import sys, time, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
import bstate as B

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
WC, HC = 11, 9


def neighbors(idx):
    x, y = idx % WC, idx // WC
    odd = y % 2
    out = []
    out.append(idx - (WC + 1 if odd else WC) if not (y == 0 or (x == 0 and odd)) else -1)
    out.append(idx - (WC if odd else WC - 1) if not (y == 0 or (x == WC - 1 and not odd)) else -1)
    out.append(idx - 1 if x != 0 else -1)
    out.append(idx + 1 if x != WC - 1 else -1)
    out.append(idx + (WC - 1 if odd else WC) if not (y == HC - 1 or (x == 0 and odd)) else -1)
    out.append(idx + (WC if odd else WC + 1) if not (y == HC - 1 or (x == WC - 1 and not odd)) else -1)
    return [n for n in out if n >= 0]


def cellxy(c):
    row, col = c // WC, c % WC
    return 89 - (22 if row % 2 else 0) + 44 * col + 22, 62 + 42 * row + 26


def clk(x, y):
    R.set_pos(x, y); time.sleep(0.4)
    for _ in range(5): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(20): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    time.sleep(0.35)


def result():
    return B.battle_result()


def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(13)
    clk(522, 232); time.sleep(6)
    if R.read_state()[5] != 0: clk(522, 232); time.sleep(6)
    cx, cy = R.find_tile_pixel(22, 13); clk(cx, cy); time.sleep(5)
    print("в бою gm", R.read_state()[5])
    for step in range(30):
        res = result()
        if res != 0:
            print(f"=== ИТОГ: BattleResult={res} ({'Victory' if res == 1 else 'Defeat'}) ===")
            break
        a, u = B.bstate()
        occ = {u[i]["cell"] for i in range(4) if u[i]["count"] > 0}
        defs = [i for i in (2, 3) if u[i]["count"] > 0]
        if not defs:
            break
        au = u[a]
        line = " ".join(f"{B.NAMES[i]}={u[i]['count']}@{u[i]['cell']}" for i in range(4))
        if au["side"] == 0:                                   # атакующий
            tgt = (3 if u[3]["count"] > 0 else 2) if a == 0 else (2 if u[2]["count"] > 0 else 3)
            tc = u[tgt]["cell"]
            ranged = (au["type"] == 1)
            if ranged or tc in neighbors(au["cell"]):
                print(f"шаг{step} [{line}] {B.NAMES[a]} бьёт {B.NAMES[tgt]}@{tc}")
                x, y = cellxy(tc); clk(x, y)
            else:                                             # melee не сосед → встать вплотную
                free = [n for n in neighbors(tc) if n not in occ]
                dest = free[0] if free else au["cell"]
                print(f"step{step} [{line}] {B.NAMES[a]} -> cell{dest} (vplotnuyu k {B.NAMES[tgt]})")
                x, y = cellxy(dest); clk(x, y)
        else:                                                 # защитник → парк
            park = next((c for c in (5, 6, 7, 16, 17) if c not in occ), 5)
            print(f"шаг{step} [{line}] {B.NAMES[a]}(защ) парк@{park}")
            x, y = cellxy(park); clk(x, y)
    R.set_pos(331, 400); time.sleep(0.6)
    from PIL import Image; Image.open(U / "ft812_dump.bmp").convert("RGB").save("Diagnostics/result.png")
    R.release_pos()
    print("кадр снят, gm", R.read_state()[5])


if __name__ == "__main__":
    main()
