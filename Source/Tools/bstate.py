#!/usr/bin/env python3
"""Чтение состояния боя ПРЯМО ИЗ ОЗУ эмулятора (быстро, надёжно — без чтения пикселей).
dump.req="A8" → instrumented Unreal пишет физ.страницу #A8 (battle-оверлей) в statedump.bin.
Адреса берём ДИНАМИЧЕСКИ из Build/hmm2.sym (иначе устаревают при сдвиге переменных!)."""
import re, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UDIR = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
SD = UDIR / "statedump.bin"
DREQ = UDIR / "dump.req"
BASE = 0xC000
TYPES = {0: "Peasant", 1: "Archer"}
NAMES = ["P40", "A4", "P20", "A2"]


def load_sym():
    sym = {}
    for line in (ROOT / "Build" / "hmm2.sym").read_text(errors="ignore").splitlines():
        m = re.match(r"\s*([A-Za-z_]\w*):\s*EQU\s*(0x[0-9A-Fa-f]+|\d+)", line)
        if m:
            sym[m.group(1)] = int(m.group(2), 0)
    return sym


SYM = load_sym()


def addr(name):
    return SYM[name] - BASE


def dump_a8():
    if SD.exists():
        SD.unlink()
    DREQ.write_bytes(b"A8")
    for _ in range(60):
        time.sleep(0.05)
        if SD.exists():
            break
    time.sleep(0.08)
    return SD.read_bytes()


def bstate():
    d = dump_a8()
    st = addr("BattleUnitState")
    units = []
    for i in range(4):
        o = st + i * 5
        units.append({"type": d[o], "cell": d[o + 1], "side": d[o + 2],
                      "count": d[o + 3] | (d[o + 4] << 8)})
    active = d[addr("BattleActiveUnit")]
    return active, units


def battle_result():
    return dump_a8()[addr("BattleResult")]


def show():
    active, units = bstate()
    print(f"АКТИВНЫЙ: idx{active} = {NAMES[active] if active < 4 else '?'}")
    for i, u in enumerate(units):
        alive = "ЖИВ" if u["count"] > 0 else "МЁРТВ"
        mark = " <== ХОД" if i == active else ""
        print(f"  idx{i} {NAMES[i]:4} {TYPES.get(u['type'], '?'):8} side{u['side']} "
              f"cell={u['cell']:3} count={u['count']:3} {alive}{mark}")
    return active, units


if __name__ == "__main__":
    show()
