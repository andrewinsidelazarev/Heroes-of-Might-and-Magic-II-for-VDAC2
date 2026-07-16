#!/usr/bin/env python3
"""Доводит ТЕКУЩИЙ бой (эмулятор уже в бою) до победы по ОЗУ. Без запуска эмулятора.
Прицеливание: P40(ближний, ваншот) → A2 (только он его берёт); A4(стрелок) → P20.
Цикл до BattleResult!=0, печать каждого шага, потом снимок кадра итога."""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
import bstate as B

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
WC, HC = 11, 9


def nb(idx):
    x, y = idx % WC, idx // WC
    o = y % 2
    r = [
        idx - (WC + 1 if o else WC) if not (y == 0 or (x == 0 and o)) else -1,
        idx - (WC if o else WC - 1) if not (y == 0 or (x == WC - 1 and not o)) else -1,
        idx - 1 if x else -1,
        idx + 1 if x != WC - 1 else -1,
        idx + (WC - 1 if o else WC) if not (y == HC - 1 or (x == 0 and o)) else -1,
        idx + (WC if o else WC + 1) if not (y == HC - 1 or (x == WC - 1 and not o)) else -1,
    ]
    return [n for n in r if n >= 0]


def xy(c):
    row, col = c // WC, c % WC
    return 89 - (22 if row % 2 else 0) + 44 * col + 22, 62 + 42 * row + 26


def clk(x, y):
    R.set_pos(x, y); time.sleep(0.4)
    for _ in range(5): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(20): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    time.sleep(0.35)


def main():
    for step in range(28):
        res = B.battle_result()
        if res:
            print("ИТОГ BattleResult =", res, "(1=Victory, 2=Defeat)")
            break
        a, u = B.bstate()
        if a >= 4:
            print("active мусор", a)
            break
        occ = {u[i]["cell"] for i in range(4) if u[i]["count"] > 0}
        defs = [i for i in (2, 3) if u[i]["count"] > 0]
        if not defs:
            print("защитники выбиты")
            break
        au = u[a]
        ln = " ".join(B.NAMES[i] + "=" + str(u[i]["count"]) + "@" + str(u[i]["cell"]) for i in range(4))
        if au["side"] == 0:                                    # атакующий
            tgt = 3 if (a == 0 and u[3]["count"] > 0) else (2 if u[2]["count"] > 0 else 3)
            tc = u[tgt]["cell"]
            ranged = (au["type"] == 1)
            if ranged or tc in nb(au["cell"]):
                print(step, "[" + ln + "]", B.NAMES[a], "бьёт", B.NAMES[tgt], "@" + str(tc))
                x, y = xy(tc); clk(x, y)
            else:
                free = [n for n in nb(tc) if n not in occ]
                d = free[0] if free else au["cell"]
                print(step, "[" + ln + "]", B.NAMES[a], "-> cell" + str(d), "вплотную к", B.NAMES[tgt])
                x, y = xy(d); clk(x, y)
        else:                                                  # защитник
            park = next((c for c in (5, 6, 7, 16, 17, 18) if c not in occ), 5)
            print(step, "[" + ln + "]", B.NAMES[a], "парк @" + str(park))
            x, y = xy(park); clk(x, y)
    R.set_pos(331, 400); time.sleep(0.6)
    from PIL import Image
    Image.open(U / "ft812_dump.bmp").convert("RGB").save("Diagnostics/result.png")
    R.release_pos()
    print("кадр снят, gm", R.read_state()[5], "BattleResult", B.battle_result())


if __name__ == "__main__":
    main()
