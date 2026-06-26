#!/usr/bin/env python3
"""Экстрактор боевых статов монстров из ЭТАЛОНА fheroes2 (monster/monster_info.cpp).

Таблица monsterData[].battleStats, поля (monster_info.h:163):
  attack, defense, damageMin, damageMax, hp, speed(enum Speed), shots, baseStrength, abilities, weaknesses
Индекс строки = enum Monster (0=Unknown, 1=Peasant, 2=Archer, ...; MONS32.ICN-кадр = id-1).

Эмитит Source/ASM/generated_monsters.inc: MONSTER_COUNT + MonsterStats (8 байт/монстр:
attack, defense, dmgMin, dmgMax, hpLo, hpHi, speed, shots). Это ФУНДАМЕНТ данных боя/найма.
Включать в оверлей боя (резидентное ядро полно).
"""
import re, sys
from pathlib import Path

SRC = Path(r"C:/Users/Администратор/Desktop/OpenHMM2/src/fheroes2/monster/monster_info.cpp")
OUT = Path(__file__).resolve().parents[2] / "Source" / "ASM" / "generated_monsters.inc"

SPEED = {"STANDING": 0, "CRAWLING": 1, "VERYSLOW": 2, "SLOW": 3, "AVERAGE": 4,
         "FAST": 5, "VERYFAST": 6, "ULTRAFAST": 7, "BLAZING": 8, "INSTANT": 9}

# { atk, def, dMin, dMax, hp, Speed::NAME, shots, baseStrength, {...}, {...} }, // Name
ROW = re.compile(
    r"\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*Speed::(\w+),\s*(\d+),"
    r".*//\s*(.+?)\s*$")


def main() -> int:
    text = SRC.read_text(encoding="utf-8", errors="replace").splitlines()
    rows = []
    started = False
    for line in text:
        if "attack | defence | damageMin" in line:   # шапка таблицы
            started = True
            continue
        if not started:
            continue
        m = ROW.match(line.strip().rstrip(","))
        if m:
            atk, dfn, dmin, dmax, hp, spd, shots, name = m.groups()
            rows.append((int(atk), int(dfn), int(dmin), int(dmax), int(hp),
                         SPEED[spd], int(shots), name))
        elif rows and "}" in line and ";" in line:    # конец инициализатора массива
            break

    L = ["; Сгенерировано Source/Tools/monster_stats.py из ЭТАЛОНА monster_info.cpp — боевые статы.",
         "; Индекс = enum Monster (0=Unknown). MONS32.ICN-кадр = id-1.",
         "                ifndef _HMM2_GENERATED_MONSTERS_",
         "                define _HMM2_GENERATED_MONSTERS_", "",
         f"MONSTER_COUNT        EQU {len(rows)}",
         "; на монстра 8 байт: attack, defense, dmgMin, dmgMax, hpLo, hpHi, speed, shots",
         "MONSTER_STAT_SIZE    EQU 8",
         "MonsterStats:"]
    for i, (atk, dfn, dmin, dmax, hp, spd, shots, name) in enumerate(rows):
        L.append(f"                DB {atk},{dfn},{dmin},{dmax},{hp & 0xFF},{(hp >> 8) & 0xFF},{spd},{shots}"
                 f"   ; [{i}] {name} (atk{atk}/def{dfn}/dmg{dmin}-{dmax}/hp{hp}/spd{spd}/sh{shots})")
    L.append("                endif")
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"monster stats -> {OUT.name}: {len(rows)} монстров, {len(rows)*8} байт таблицы")
    # контроль: первые/ключевые
    for idx in (1, 2, 4, 35, 38, 47):
        if idx < len(rows):
            r = rows[idx]
            print(f"  [{idx}] {r[7]}: atk{r[0]} def{r[1]} dmg{r[2]}-{r[3]} hp{r[4]} spd{r[5]} sh{r[6]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
