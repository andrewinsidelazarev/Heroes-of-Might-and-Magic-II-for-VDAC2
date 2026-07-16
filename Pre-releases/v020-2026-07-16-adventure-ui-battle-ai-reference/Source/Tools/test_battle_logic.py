#!/usr/bin/env python3
"""Быстрая ДЕТЕРМИНИРОВАННАЯ проверка боевой логики через Z80-харнесс (без boot/кликов Unreal).
Маппит slot3 → battle-страницу (#A8) и зовёт функции оверлея напрямую. Статы монстров из #91.
Проверяет: порядок хода (самый быстрый первым), атаку (урон по #91), передачу хода, конец боя."""
from __future__ import annotations
from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT

BATTLE_PAGE = 0xA8
N, SZ = 4, 5     # юнитов, байт на юнита {type,cell,side,count_lo,count_hi}


def fail(msg):
    raise SystemExit(f"ОШИБКА: {msg}")


def main():
    emu = HMM2FullZ80Emulator(ROOT)
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)        # FMADDR (нужно SetPage3/MonsterStats)
    if not emu.fmaddr_enabled:
        fail("FMADDR не включён после Platform_Init")
    # slot3 → battle-страница. FMADDR-регистр page3 = #0413: запись через cpu_write и маппит slot3,
    # и сохраняет значение по #0413 (GetPage3 в MonsterStats_Read прочитает верную страницу).
    emu.cpu_write(0x0413, BATTLE_PAGE)

    st = emu.sym["BattleUnitState"]
    init = emu.sym["BattleUnitStateInit"]
    acted = emu.sym["BattleActed"]
    A_active = emu.sym["BattleActiveUnit"]
    A_target = emu.sym["BattleTargetUnit"]

    def reinit():
        for i in range(N * SZ):
            emu.set_byte(st + i, emu.get_byte(init + i))
        for i in range(N):
            emu.set_byte(acted + i, 0)

    def count(i):
        a = st + i * SZ
        return emu.get_byte(a + 3) | (emu.get_byte(a + 4) << 8)

    # 1) Порядок хода: первый ход = самый быстрый отряд. Peasant/Archer оба speed=2 → idx0.
    reinit()
    emu.call(emu.sym["Battle_NextTurn"], max_steps=500_000)
    av = emu.get_byte(A_active)
    if av != 0:
        fail(f"NextTurn(старт): active={av}, ожид 0 (самый быстрый, тай→первый индекс)")
    if emu.get_byte(acted + 0) != 1:
        fail("активный должен быть помечен 'ходил'")
    print(f"  OK порядок хода: первый ход = idx{av} (быстрейший)")

    # 2) Атака: P40(idx0, dmg1) бьёт A2(idx3, hp10, count2) → losses=40/10=4 ≥ 2 → гибнет.
    reinit()
    emu.set_byte(A_active, 0)
    emu.set_byte(A_target, 3)
    emu.call(emu.sym["Battle_Attack"], max_steps=500_000)
    if count(3) != 0:
        fail(f"атака P40→A2: A2.count={count(3)}, ожид 0 (мёртв)")
    if count(0) != 40:
        fail(f"атакующий не должен терять: P40.count={count(0)}")
    print(f"  OK атака сильным: A2 {2}→{count(3)} (убит, урон по статам #91)")

    # 3) Атака слабым: A4(idx1, dmg avg2, count4) бьёт P20(idx2, hp1) → 4*2/1=8 → 20-8=12 (выживает).
    reinit()
    emu.set_byte(A_active, 1)
    emu.set_byte(A_target, 2)
    emu.call(emu.sym["Battle_Attack"], max_steps=500_000)
    if count(2) != 12:
        fail(f"атака A4→P20: P20.count={count(2)}, ожид 12 (20-8)")
    print(f"  OK атака слабым: P20 20→{count(2)} (частичный урон виден)")

    # 4) Передача хода: пометить idx0 'ходил' → NextTurn даёт следующий живой (idx1).
    reinit()
    emu.set_byte(acted + 0, 1)
    emu.call(emu.sym["Battle_NextTurn"], max_steps=500_000)
    av = emu.get_byte(A_active)
    if av != 1:
        fail(f"NextTurn(после acted[0]): active={av}, ожид 1")
    print(f"  OK передача хода: idx0 отходил → следующий active=idx{av}")

    # 5) Конец боя: обе стороны живы → CheckEnd A=0; убить защитников (idx2,3) → A=1.
    reinit()
    emu.call(emu.sym["Battle_CheckEnd"], max_steps=500_000)
    if emu.reg.A != 0:
        fail(f"обе стороны живы → CheckEnd={emu.reg.A}, ожид 0 (продолжать)")
    for d in (2, 3):
        emu.set_byte(st + d * SZ + 3, 0)
        emu.set_byte(st + d * SZ + 4, 0)
    emu.call(emu.sym["Battle_CheckEnd"], max_steps=500_000)
    if emu.reg.A != 1:
        fail(f"защитники выбиты → CheckEnd={emu.reg.A}, ожид 1 (выход)")
    print("  OK конец боя: обе живы→продолжать; сторона выбита→выход (A=1)")

    # 6) Соседство ближнего боя: P40(melee,cell22) по P20(cell32,далеко)=нельзя; A4(стрелок)=можно;
    #    P40 на соседней клетке (cell31)=можно. shots из #91 (Peasant 0=melee, Archer 12=стрелок).
    reinit()
    emu.set_byte(A_active, 0); emu.set_byte(A_target, 2)
    emu.call(emu.sym["Battle_AttackAllowed"], max_steps=500_000)
    if emu.reg.A != 0:
        fail(f"P40(melee) по далёкому P20: AttackAllowed={emu.reg.A}, ожид 0 (нельзя)")
    emu.set_byte(A_active, 1); emu.set_byte(A_target, 2)
    emu.call(emu.sym["Battle_AttackAllowed"], max_steps=500_000)
    if emu.reg.A == 0:
        fail("A4(стрелок) по P20: должно быть можно (A!=0)")
    emu.set_byte(st + 0 * SZ + 1, 31)        # P40.cell = 31 (LEFT-сосед P20 cell32)
    emu.set_byte(A_active, 0); emu.set_byte(A_target, 2)
    emu.call(emu.sym["Battle_AttackAllowed"], max_steps=500_000)
    if emu.reg.A == 0:
        fail("P40(melee) по СОСЕДНЕМУ P20 (cell31→cell32): должно быть можно")
    print("  OK соседство: melee только сосед, стрелок везде")

    print("OK: battle-логика верна — порядок хода / атака (#91) / передача хода / конец боя / соседство")


if __name__ == "__main__":
    main()
