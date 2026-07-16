#!/usr/bin/env python3
"""Экстрактор боевых статов монстров из ЭТАЛОНА fheroes2 (monster/monster_info.cpp).

Таблица monsterData[].battleStats, поля (monster_info.h:163):
  attack, defense, damageMin, damageMax, hp, speed(enum Speed), shots, baseStrength, abilities, weaknesses
Индекс строки = enum Monster (0=Unknown, 1=Peasant, 2=Archer, ...; MONS32.ICN-кадр = id-1).

+ СИЛА МОНСТРА (для AI analyzeBattleState): GetMonsterStrength = (1 + atk·0.1 + def·0.05) ×
  monsterBaseStrength, где monsterBaseStrength = sqrt(damagePotential × effectiveHP) × monsterSpecial —
  ТОЧНО по getMonsterBaseStrength (monster_info.cpp:45-132) с учётом abilities (парсятся из
  emplace_back-строк populateMonsterData + enum Monster из monster.h). Unit::GetStrength = это × count.
  Храним фикс-точкой ×16 (DW) в записи монстра.

Эмитит Source/ASM/generated_monsters.inc: MONSTER_COUNT + MonsterStats (10 байт/монстр:
attack, defense, dmgMin, dmgMax, hpLo, hpHi, speed, shots, strLo, strHi). ФУНДАМЕНТ данных боя/найма.
Страница GLOBAL_DATA_PAGE #91; читает резидентный MonsterStats_Read (B=id → MonsterStatBuf 10Б).
"""
import math
import re
import sys
from pathlib import Path

OPENHMM2 = Path(r"C:/Users/Администратор/Desktop/OpenHMM2")
SRC = OPENHMM2 / "src/fheroes2/monster/monster_info.cpp"
HDR = OPENHMM2 / "src/fheroes2/monster/monster.h"
OUT = Path(__file__).resolve().parents[2] / "Source" / "ASM" / "generated_monsters.inc"

SPEED = {"STANDING": 0, "CRAWLING": 1, "VERYSLOW": 2, "SLOW": 3, "AVERAGE": 4,
         "FAST": 5, "VERYFAST": 6, "ULTRAFAST": 7, "BLAZING": 8, "INSTANT": 9}
SPEED_AVERAGE = SPEED["AVERAGE"]
STR_FP_SHIFT = 4          # сила ×16 (4.4… бита дробной части хватает: шаг 0.0625)

# { atk, def, dMin, dMax, hp, Speed::NAME, shots, baseStrength, {...}, {...} }, // Name
ROW = re.compile(
    r"\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*Speed::(\w+),\s*(\d+),"
    r".*//\s*(.+?)\s*$")
# monsterData[Monster::NAME].battleStats.abilities.emplace_back( fheroes2::MonsterAbilityType::ABIL[, pct[, Spell::X | 0]] );
ABIL = re.compile(
    r"monsterData\[Monster::(\w+)\]\.battleStats\.abilities\.emplace_back\(\s*"
    r"fheroes2::MonsterAbilityType::(\w+)"
    r"(?:\s*,\s*(\d+)\s*(?:,\s*(?:Spell::(\w+)|\d+)\s*)?)?\s*\)")


def parse_enum_monsters(text: str) -> list[str]:
    """enum MonsterType в monster.h: порядок имён = индекс таблицы."""
    m = re.search(r"enum\s+MonsterType\s*:\s*int32_t\s*\{(.*?)\}", text, re.S)
    if not m:
        raise SystemExit("enum MonsterType не найден в monster.h")
    body = re.sub(r"//[^\n]*", "", m.group(1))   # комментарии ДО split (иначе съедают следующий токен)
    names = []
    for tok in body.split(","):
        tok = tok.split("=")[0].strip()          # алиасы со значением — пропустить
        if not re.fullmatch(r"[A-Z_0-9]+", tok):
            continue
        names.append(tok)
    if names and names[-1] == "MONSTER_COUNT":   # счётчик — не запись
        names.pop()
    return names


def base_strength(stats, abils) -> float:
    """getMonsterBaseStrength (monster_info.cpp:45-132) — ТОЧНО по эталону."""
    atk, dfn, dmin, dmax, hp, spd, shots = stats
    names = {a[0] for a in abils}
    effective_hp = hp * (1.4 if "NO_ENEMY_RETALIATION" in names else 1)
    is_archers = shots > 0

    dmg = (dmin + dmax) / 2.0
    if "DOUBLE_SHOOTING" in names:
        dmg *= 2
    elif "DOUBLE_MELEE_ATTACK" in names:
        dmg *= 2 if "NO_ENEMY_RETALIATION" in names else 1.75
    if "DOUBLE_DAMAGE_TO_UNDEAD" in names:
        dmg *= 1.15
    if "TWO_CELL_MELEE_ATTACK" in names:
        dmg *= 1.2
    if "UNLIMITED_RETALIATION" in names:
        dmg *= 1.25
    if "ALL_ADJACENT_CELL_MELEE_ATTACK" in names or "AREA_SHOT" in names:
        dmg *= 1.3

    special = 1.0
    if is_archers:
        special += 0.5 if "NO_MELEE_PENALTY" in names else 0.4
    if "FLYING" in names:
        special += 0.3
    if "ENEMY_HALVING" in names:
        special += 1
    if "SOUL_EATER" in names:
        special += 2
    if "HP_DRAIN" in names:
        special += 0.3
    for name, pct, spell in abils:               # std::find → ПЕРВЫЙ SPELL_CASTER
        if name != "SPELL_CASTER":
            continue
        if spell in ("PARALYZE", "BLIND", "PETRIFY"):
            special += pct / 100.0
        elif spell in ("DISPEL", "CURSE"):
            special += pct / 100.0 / 10.0
        else:
            raise SystemExit(f"SPELL_CASTER c неучтённым спеллом {spell} — обнови формулу (см. monster_info.cpp)")
        break

    speed_diff = spd - SPEED_AVERAGE
    special += speed_diff * (0.1 if speed_diff < 0 else 0.05)

    return math.sqrt(dmg * effective_hp) * special


def main() -> int:
    text = SRC.read_text(encoding="utf-8", errors="replace")
    rows = []
    started = False
    for line in text.splitlines():
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

    enum_names = parse_enum_monsters(HDR.read_text(encoding="utf-8", errors="replace"))
    if len(enum_names) < len(rows):
        raise SystemExit(f"enum Monster ({len(enum_names)}) короче таблицы ({len(rows)})")

    abilities: dict[str, list] = {}
    for m in ABIL.finditer(text):
        mon, abil, pct, spell = m.groups()
        abilities.setdefault(mon, []).append((abil, int(pct) if pct else 0, spell or ""))

    # сила: GetMonsterStrength = (1 + atk·0.1 + def·0.05) × baseStrength, фикс-точка ×16
    strengths = []
    for i, r in enumerate(rows):
        abils = abilities.get(enum_names[i], [])
        base = base_strength(r[:7], abils)
        strength = (1.0 + r[0] * 0.1 + r[1] * 0.05) * base
        fp = round(strength * (1 << STR_FP_SHIFT))
        assert fp <= 0xFFFF, f"{r[7]}: strength_fp {fp} не влезает в DW"
        strengths.append((strength, fp))

    L = ["; Сгенерировано Source/Tools/monster_stats.py из ЭТАЛОНА monster_info.cpp — боевые статы.",
         "; Индекс = enum Monster (0=Unknown). MONS32.ICN-кадр = id-1.",
         "; strength = GetMonsterStrength×16 (фикс-точка) = (1+atk·0.1+def·0.05)×getMonsterBaseStrength;",
         ";   Unit::GetStrength = strength×count (AI analyzeBattleState). Эталон monster_info.cpp:45-132.",
         "                ifndef _HMM2_GENERATED_MONSTERS_",
         "                define _HMM2_GENERATED_MONSTERS_", "",
         f"MONSTER_COUNT        EQU {len(rows)}",
         "; на монстра 10 байт: attack, defense, dmgMin, dmgMax, hpLo, hpHi, speed, shots, strLo, strHi",
         "MONSTER_STAT_SIZE    EQU 10",
         f"MONSTER_STR_FP_SHIFT EQU {STR_FP_SHIFT}     ; сила хранится ×16",
         "MonsterStats:"]
    for i, (atk, dfn, dmin, dmax, hp, spd, shots, name) in enumerate(rows):
        s, fp = strengths[i]
        L.append(f"                DB {atk},{dfn},{dmin},{dmax},{hp & 0xFF},{(hp >> 8) & 0xFF},{spd},{shots}"
                 f" : DW {fp}"
                 f"   ; [{i}] {name} (atk{atk}/def{dfn}/dmg{dmin}-{dmax}/hp{hp}/spd{spd}/sh{shots} str{s:.1f})")
    L.append("                endif")
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"monster stats -> {OUT.name}: {len(rows)} монстров, {len(rows)*10} байт таблицы")
    # контроль: первые/ключевые (+ сила float vs фикс-точка)
    for idx in (1, 2, 4, 10, 35, 38, 47, 66):
        if idx < len(rows):
            r = rows[idx]
            s, fp = strengths[idx]
            ab = ",".join(a[0] for a in abilities.get(enum_names[idx], [])) or "-"
            print(f"  [{idx}] {r[7]}: atk{r[0]} def{r[1]} dmg{r[2]}-{r[3]} hp{r[4]} spd{r[5]} sh{r[6]}"
                  f" str={s:.2f} fp={fp} ({fp/16:.2f}) [{ab}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
