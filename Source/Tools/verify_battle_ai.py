#!/usr/bin/env python3
"""Проверка AI боя + авто-режима на РЕАЛЬНОМ эмуляторе (bt8xxemu).
New Game → герой на тайл боя (22,13) → бой → клик кнопки Auto → AI доигрывает ОБЕ стороны
до результата. Печатает клетки/счётчики каждый тик (без моих кликов) + кадр финала."""
import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R
import bstate

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")

def clk(x, y):
    R.set_pos(x, y); time.sleep(0.45)
    for _ in range(6):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(8):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.15)

def move_to(x, y):
    clk(x, y); time.sleep(0.25); clk(x, y)

def gm():
    return R.read_state()[5]

def auto_flag():
    d = bstate.dump_a8()
    return d[bstate.addr("BattleAutoMode")]

def snap(tag):
    from PIL import Image
    Image.open(str(U / "ft812_dump.bmp")).convert("RGB").save(str(Path(__file__).resolve().parents[2] / "Diagnostics" / tag))

def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(14)
    clk(522, 232); time.sleep(7)                       # New Game → adventure
    print("gm после New Game:", gm())
    move_to(288, 384)                                  # герой → тайл боя (24,16) (3 ниже гейта, открытое поле)
    print("веду героя к тайлу боя (24,16)...")
    for i in range(18):
        g = gm()
        if g == 2:
            break
        time.sleep(0.4)
    print("gm после подхода:", gm(), "(2=бой ожидается)")
    if gm() != 2:
        print("!! в бой не вошли — стоп"); return
    print("\n--- состояние боя ДО Auto ---")
    bstate.show()
    snap("battle_before_auto.png")                     # ход человека: статус «Turn N» (нативный текст)
    # клик по кнопке Auto (нижняя панель, лог. зона 8..88 × 440..474)
    clk(48, 457)
    time.sleep(0.3)
    print("\nBattleAutoMode после клика Auto:", auto_flag(), "(1=включён)")
    print("\n--- AI доигрывает бой (без моих кликов) ---")
    res = 0
    for t in range(40):
        d = bstate.dump_a8()
        res = d[bstate.addr("BattleResult")]
        rnd = d[bstate.addr("BattleRound")]
        st = bstate.addr("BattleUnitState")
        cells = [d[st + i*5 + 1] for i in range(4)]
        cnts = [d[st + i*5 + 3] | (d[st + i*5 + 4] << 8) for i in range(4)]
        print(f"  t{t:2} раунд={rnd} res={res} | P40 c{cells[0]}={cnts[0]} A4 c{cells[1]}={cnts[1]} "
              f"| P20 c{cells[2]}={cnts[2]} A2 c{cells[3]}={cnts[3]}")
        if t == 2:
            snap("battle_during_auto.png")             # авто-ход: «Turn N» НЕ должно висеть
        if res != 0:
            break
        time.sleep(0.7)
    snap("battle_ai_finale.png")
    verdict = {0: "НЕ ЗАВЕРШИЛСЯ (зависание?)", 1: "Victory (защитник выбит)",
               2: "Defeat (атакующий выбит)"}.get(res, f"res={res}")
    print("\nВЕРДИКТ:", verdict)

if __name__ == "__main__":
    main()
