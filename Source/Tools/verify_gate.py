#!/usr/bin/env python3
"""Проверка adjacency-гейта НА РЕАЛЬНОМ bt8xxemu (не харнессом), управление по ОЗУ.
(1) P40(ближний)@22 бьёт ДАЛЁКОГО A2@43 → BLOCKED (P40 остаётся активным, A2 цел).
(2) P40 → cell31 (сосед P20@32); крутим ход до P40; P40 бьёт СОСЕДНЕГО P20 → урон проходит.
Печатает состояние ОЗУ на каждом шаге."""
import sys, time, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
import bstate as B

UDIR = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
EXE = UDIR / "Unreal.exe"


def cellxy(cell):
    row, col = cell // 11, cell % 11
    return 89 - (22 if row % 2 else 0) + 44 * col + 22, 62 + 42 * row + 26


def click(x, y):
    R.set_pos(x, y); time.sleep(0.45)
    for _ in range(5): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(20): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    time.sleep(0.4)


def st_line(units):
    return " | ".join(f"{B.NAMES[i]}={units[i]['count']}@{units[i]['cell']}" for i in range(4))


def main():
    print("launch"); subprocess.Popen([str(EXE), "hmm2_vdac2.spg"], cwd=str(UDIR)); time.sleep(13)
    print("New Game"); click(522, 232); time.sleep(6)
    if R.read_state()[5] != 0:
        click(522, 232); time.sleep(6)
    cx, cy = R.find_tile_pixel(22, 13); click(cx, cy); time.sleep(5)
    print(f"gm={R.read_state()[5]}")

    a, u = B.bstate()
    print(f"СТАРТ: active={B.NAMES[a]} [{st_line(u)}]")
    a2c = u[3]["cell"]; p40c = u[0]["cell"]

    # (1) НЕГАТИВ: P40(active, ближний)@22 кликает далёкого A2@43
    print(f"\n(1) P40@{p40c} (ближний) бьёт ДАЛЁКОГО A2@{a2c}:")
    x, y = cellxy(a2c); click(x, y)
    a, u = B.bstate()
    blocked = (a == 0 and u[3]["count"] == 2)
    print(f"    после: active={B.NAMES[a]} A2={u[3]['count']}  => {'BLOCKED ✓ (гейт держит)' if blocked else 'НЕ блокировано ✗'}")

    # (2) ПОЗИТИВ: двигаем P40 на cell31 (сосед P20@32), крутим до хода P40, бьём P20
    print(f"\n(2) P40 → cell31 (сосед P20@{u[2]['cell']}), потом бьёт соседнего P20:")
    x, y = cellxy(31); click(x, y)
    p20_before = None
    for step in range(16):
        a, u = B.bstate()
        if R.read_state()[5] != 2:
            print("    бой неожиданно кончился"); break
        if a == 0:                                  # P40 активен → бьём соседнего P20
            p20_before = u[2]["count"]
            print(f"    P40@{u[0]['cell']} бьёт СОСЕДНЕГО P20@{u[2]['cell']} (P20 было {p20_before})")
            x, y = cellxy(u[2]["cell"]); click(x, y)
            a2, u2 = B.bstate()
            ok = u2[2]["count"] < p20_before
            print(f"    после: P20={u2[2]['count']}  => {'УРОН ПРОШЁЛ ✓ (ближняя атака соседа работает)' if ok else 'урона нет ✗'}")
            break
        # не P40: продвинуть ход, не ломая позиции. защитник@рядом с P40 → бьёт P40 (стоит); иначе move-park
        if u[a]["side"] == 1 and u[a]["cell"] in (24, 30, 32, 33, 42, 43):
            x, y = cellxy(u[0]["cell"]);
            print(f"    {B.NAMES[a]}(защ) бьёт P40 (стоит на месте)"); click(x, y)
        else:
            park = 5 if a == 1 else (6 if a == 2 else 7)
            x, y = cellxy(park)
            print(f"    {B.NAMES[a]} паркуется @{park}"); click(x, y)
    R.release_pos()
    print("\ndone verify_gate")


if __name__ == "__main__":
    main()
