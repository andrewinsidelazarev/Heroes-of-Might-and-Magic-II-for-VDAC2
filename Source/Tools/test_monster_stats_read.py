#!/usr/bin/env python3
"""Проверка резидентного MonsterStats_Read: читает 8 байт статов монстра из глоб-страницы #91
(GLOBAL_DATA_PAGE) в MonsterStatBuf. Эталон — generated_monsters.inc (из monster_info.cpp).
SetPage3 требует FMADDR → сперва Platform_Init."""
from __future__ import annotations

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT

# Эталон (generated_monsters.inc): atk, def, dmgMin, dmgMax, hpLo, hpHi, speed, shots.
EXPECTED = {
    0: [0, 0, 0, 0, 0, 0, 2, 0],        # Unknown
    1: [1, 1, 1, 1, 1, 0, 2, 0],        # Peasant
    2: [5, 3, 2, 3, 10, 0, 2, 12],      # Archer
    10: [11, 12, 10, 20, 50, 0, 5, 0],  # Paladin
}


def fail(msg: str) -> None:
    raise SystemExit(f"ОШИБКА: {msg}")


def main() -> None:
    emu = HMM2FullZ80Emulator(ROOT)
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)  # включает FMADDR (нужно SetPage3)
    if not emu.fmaddr_enabled:
        fail("FMADDR не включён после Platform_Init")
    buf = emu.sym["MonsterStatBuf"]
    for idx, exp in EXPECTED.items():
        emu.reg.B = idx
        emu.call(emu.sym["MonsterStats_Read"], max_steps=200_000)
        got = [emu.get_byte(buf + i) for i in range(8)]
        if got != exp:
            fail(f"монстр[{idx}]: статы {got}, ожидалось {exp}")
        print(f"  OK монстр[{idx}]: atk={got[0]} def={got[1]} dmg={got[2]}-{got[3]} "
              f"hp={got[4] | (got[5] << 8)} spd={got[6]} sh={got[7]}")
    print("OK: MonsterStats_Read читает статы монстров из #91 (резидентный доступ к глоб-данным)")


if __name__ == "__main__":
    main()
