#!/usr/bin/env python3
"""Дамп армий героев и гарнизонов замков из MP2/MX2 (эталон fheroes2 world_loadmap.cpp).

Формат блока героя (76 байт, MP2_HEROES_STRUCTURE_SIZE):
  [0]   unused
  [1]   customArmy flag (0 => дефолтная армия класса, армии в блоке НЕТ)
  [2..6] 5 типов монстров (engine id = byte+1; MONS32.ICN index = byte)
  [7..16] 5 кол-в (uint16 LE)
  [17]  customPortrait flag, [18] portrait id, [60] race (для jail)
Блоки сопоставляются тайлам в порядке row-major скана объектных тайлов (vec_object).
"""
import struct, sys
from pathlib import Path

MP2_MAP_INFO_SIZE = 428
MP2_TILE = 20
MP2_ADDON = 15
CASTLE_COUNT, CAP_COUNT, POS = 72, 144, 3
HERO_SZ, CASTLE_SZ = 76, 70

RACE = {0: "Knight", 1: "Barbarian", 2: "Sorceress", 3: "Warlock", 4: "Wizard", 5: "Necromancer", 6: "Neutral"}
# MONS32.ICN индекс -> имя (id = idx+1). Список монстров HMM2 по fheroes2 Monster enum (без UNKNOWN).
MON = ["Peasant","Archer","Ranger","Pikeman","Veteran Pikeman","Swordsman","Master Swordsman",
       "Cavalry","Champion","Paladin","Crusader","Goblin","Orc","Orc Chief","Wolf","Ogre","Ogre Lord",
       "Troll","War Troll","Cyclops","Sprite","Dwarf","Battle Dwarf","Elf","Grand Elf","Druid",
       "Greater Druid","Unicorn","Phoenix","Centaur","Gargoyle","Griffin","Minotaur","Minotaur King",
       "Hydra","Green Dragon","Red Dragon","Black Dragon","Halfling","Boar","Iron Golem","Steel Golem",
       "Roc","Mage","Archmage","Giant","Titan","Skeleton","Zombie","Mutant Zombie","Mummy","Royal Mummy",
       "Vampire","Vampire Lord","Lich","Power Lich","Bone Dragon","Rogue","Nomad","Ghost","Genie","Medusa",
       "Earth Elemental","Air Elemental","Fire Elemental","Water Elemental"]

def mon_name(b):
    return MON[b] if 0 <= b < len(MON) else f"#{b}"

def parse(path):
    data = Path(path).read_bytes()
    # MP2 header: [0..3] sig 5C 00 00 00, [4..5] difficulty, [6] width, [7] height
    width, height = data[6], data[7]
    world = width * height
    tiles_end = MP2_MAP_INFO_SIZE + world * MP2_TILE
    addon_count = struct.unpack_from("<I", data, tiles_end)[0]
    after_addon = tiles_end + 4 + addon_count * MP2_ADDON
    print(f"map {width}x{height} world={world} addons={addon_count} afterAddon=0x{after_addon:X} size={len(data)}")

    off = after_addon
    castles = []
    for i in range(CASTLE_COUNT):
        px, py, ct = data[off], data[off+1], data[off+2]; off += 3
        if px == 0xFF and py == 0xFF:
            continue
        race = RACE.get(ct & 0x7F if (ct & 0x7F) <= 6 else ct, f"?{ct}")
        castles.append((px, py, ct))
    cap_off = off
    off += CAP_COUNT * POS  # capture objects, не нужны
    obelisk = data[off]; off += 1
    print(f"castles(coords): {castles}")
    print(f"obeliskCount={obelisk}")

    # infoBlockCount discovery: пары (l,h) до (0,0); count = 256*h+l-1 от последней ненулевой пары
    info_count = 0
    while True:
        l = data[off]; h = data[off+1]; off += 2
        if l == 0 and h == 0:
            break
        info_count = 256*h + l - 1
    print(f"infoBlockCount={info_count}  firstBlockAt=0x{off:X}")

    # читаем блоки
    heroes = []
    castle_blocks = []
    for i in range(info_count):
        if off + 2 > len(data):
            break
        size = struct.unpack_from("<H", data, off)[0]; off += 2
        block = data[off:off+size]; off += size
        if size == HERO_SZ:
            custom = block[1]
            army = []
            if custom:
                types = block[2:7]
                counts = struct.unpack_from("<5H", block, 7)
                for t, c in zip(types, counts):
                    if c > 0 and t != 0xFF:
                        army.append((t, c))
            heroes.append((i, custom, army, block[17], block[18]))
        elif size == CASTLE_SZ:
            castle_blocks.append((i, block))

    print(f"\n=== HEROES ({len(heroes)}) ===")
    for idx, custom, army, cp, pid in heroes:
        a = ", ".join(f"{cnt}x {mon_name(t)}(MONS32[{t}])" for t, cnt in army) if army else "(default army for class)"
        print(f"  block#{idx} custom={custom} portrait={'yes#'+str(pid) if cp else 'no'} :: {a}")

    print(f"\n=== CASTLE BLOCKS ({len(castle_blocks)}) garrison army ===")
    for idx, block in castle_blocks:
        # гарнизон замка: байт1 customArmy, типы[2..6], кол-ва[7..16] (тот же layout начала)
        custom = block[1]
        army = []
        if custom:
            types = block[2:7]
            counts = struct.unpack_from("<5H", block, 7)
            for t, c in zip(types, counts):
                if c > 0 and t != 0xFF:
                    army.append((t, c))
        a = ", ".join(f"{cnt}x {mon_name(t)}(MONS32[{t}])" for t, cnt in army) if army else "(empty/default)"
        print(f"  block#{idx} custom={custom} :: {a}")

if __name__ == "__main__":
    parse(sys.argv[1] if len(sys.argv) > 1 else "Assets/Original/MAPS/SKIRMISH.MX2")
