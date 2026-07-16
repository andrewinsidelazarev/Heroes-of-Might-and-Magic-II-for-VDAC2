#!/usr/bin/env python3
"""Извлечь РЕАЛЬНЫЕ данные замков из MP2/MX2-карты (имя, раса, построенные здания, маг.гильдия,
капитан, замок/город) — по world_loadmap.cpp + Castle::LoadFromMP2 (castle.cpp:102).

Данные — «кровь»: окно строительства/город должны идти от них, а не от «всё построено».

Хвост MP2 (после tiles+addons):
  координаты замков (72×3) → координаты captureobj (144×3) → obeliskCount(1) →
  цикл версии (пары l,h до 0,0; infoBlockCount = 256*h+l-1) → infoBlockCount блоков (uint16 size + data).
Блок замка = 70 байт (MP2_CASTLE_STRUCTURE_SIZE). Раса замка берётся из списка координат (тип 0x00/0x80=KNGT…).
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

MP2_MAP_INFO_SIZE = 428
MP2_TILE_SIZE = 20
MP2_ADDON_SIZE = 15
MP2_CASTLE_COUNT = 72
MP2_CASTLE_POSITION_SIZE = 3
MP2_CAPTURE_OBJECT_COUNT = 144
MP2_CAPTURE_OBJECT_POSITION_SIZE = 3
MP2_CASTLE_STRUCTURE_SIZE = 70

RACE_NAMES = {0: "KNGT", 1: "BARB", 2: "SORC", 3: "WRLK", 4: "WZRD", 5: "NECR", 6: "RAND"}

# Биты «common buildings» (castle.cpp:121-134)
COMMON_BUILDINGS = [
    (0x0002, "Thieves' Guild"), (0x0004, "Tavern"), (0x0008, "Shipyard"), (0x0010, "Well"),
    (0x0080, "Statue"), (0x0100, "Left Turret"), (0x0200, "Right Turret"), (0x0400, "Marketplace"),
    (0x0800, "Farm/WEL2"), (0x1000, "Moat"), (0x2000, "Fortifications/SPEC"),
]
# Биты жилищ (castle.cpp:137-147)
DWELLINGS = [
    (0x0008, "Dwelling 1"), (0x0010, "Dwelling 2"), (0x0020, "Dwelling 3"), (0x0040, "Dwelling 4"),
    (0x0080, "Dwelling 5"), (0x0100, "Dwelling 6"), (0x0200, "Upg 2"), (0x0400, "Upg 3"),
    (0x0800, "Upg 4"), (0x1000, "Upg 5"), (0x2000, "Upg 6"),
]


def c_string(raw: bytes) -> str:
    z = raw.find(b"\x00")
    return raw[: z if z >= 0 else len(raw)].decode("cp1252", errors="replace")


def parse_castle_block(b: bytes) -> dict:
    """MP2_CASTLE_STRUCTURE_SIZE (70). Раскладка — Castle::LoadFromMP2 (castle.cpp:102-211)."""
    owner = b[0]
    custom_buildings = b[1]
    common = struct.unpack_from("<H", b, 2)[0]
    dwellings = struct.unpack_from("<H", b, 4)[0]
    mage_guild = b[6]
    has_captain = b[23]
    has_name = b[24]
    name = c_string(b[25:25 + 13])
    race = b[38]
    is_castle = b[39]
    allow_castle = b[40]
    return {
        "owner": owner, "custom_buildings": custom_buildings,
        "common_bits": common, "dwelling_bits": dwellings, "mage_guild": mage_guild,
        "has_captain": has_captain, "has_name": has_name, "name": name,
        "race_byte": race, "is_castle": bool(is_castle), "allow_castle": bool(allow_castle),
    }


def extract(path: Path) -> dict:
    data = path.read_bytes()
    if data[:4] != bytes([0x5C, 0x00, 0x00, 0x00]):
        raise ValueError(f"{path}: неверная сигнатура MP2")
    width, height = data[6], data[7]
    tiles_off = MP2_MAP_INFO_SIZE
    tiles_end = tiles_off + width * height * MP2_TILE_SIZE
    addon_count = struct.unpack_from("<I", data, tiles_end)[0]
    pos = tiles_end + 4 + addon_count * MP2_ADDON_SIZE       # afterAddonInfoPos

    # 1) координаты замков (72×3): x,y,type → раса
    castle_pos = []
    for _ in range(MP2_CASTLE_COUNT):
        x, y, ctype = data[pos], data[pos + 1], data[pos + 2]; pos += 3
        if x == 0xFF and y == 0xFF:
            continue
        race = ctype & 0x7F                                 # 0x00/0x80=0=KNGT …
        castle_pos.append({"x": x, "y": y, "type": ctype, "race": race, "is_castle": ctype >= 0x80})

    # 2) координаты captureobj (144×3) — пропустить
    pos += MP2_CAPTURE_OBJECT_COUNT * MP2_CAPTURE_OBJECT_POSITION_SIZE
    # 3) obeliskCount (1)
    pos += 1
    # 4) цикл версии: пары (l,h) пока не (0,0); infoBlockCount = последнее 256*h+l-1
    info_block_count = 0
    while True:
        l = data[pos]; h = data[pos + 1]; pos += 2
        if l == 0 and h == 0:
            break
        info_block_count = 256 * h + l - 1
    # 5) info-блоки: (uint16 size + data). Замок = 70 байт.
    castles = []
    for _ in range(info_block_count):
        size = struct.unpack_from("<H", data, pos)[0]; pos += 2
        block = data[pos:pos + size]; pos += size
        if size == MP2_CASTLE_STRUCTURE_SIZE:
            castles.append(parse_castle_block(block))
    return {"width": width, "height": height, "castle_pos": castle_pos, "castles": castles}


GRASS_START_IMAGE_INDEX = 30                      # terrain idx < 30 = вода (ground.h)


def _tile_terrain(data: bytes, width: int, x: int, y: int) -> int:
    off = MP2_MAP_INFO_SIZE + (y * width + x) * MP2_TILE_SIZE
    return struct.unpack_from("<H", data, off)[0]


def has_sea_access(mx2: Path, cx: int, cy: int) -> bool:
    """Castle::HasSeaAccess (castle.cpp): вода на одном из 3 тайлов (cx-1/cx/cx+1, cy+2)?"""
    data = mx2.read_bytes()
    width, height = data[6], data[7]
    if cy + 2 >= height:
        return False
    for dx in (0, -1, 1):
        x = cx + dx
        if 0 <= x < width and _tile_terrain(data, width, x, cy + 2) < GRASS_START_IMAGE_INDEX:
            return True
    return False


def knight_castle(mx2: Path) -> dict:
    """Данные ЗАМКА ИГРОКА (первый Knight по списку координат) из MX2 — имя/раса/здания/капитан/море."""
    r = extract(mx2)
    # раса структуры может быть RAND (6) — тогда берём расу из списка координат по позиции.
    knight = next((c for c in r["castles"] if c["race_byte"] == 0), None)
    if knight is None:
        # fallback: первая координата Knight → её структура (по порядку)
        knight = r["castles"][0] if r["castles"] else {}
    pos = next((p for p in r["castle_pos"] if p["race"] == 0), None)
    if pos:
        knight = {**knight, "x": pos["x"], "y": pos["y"], "is_castle": pos["is_castle"]}
    cx, cy = knight.get("x", 24), knight.get("y", 13)
    knight["has_sea"] = has_sea_access(mx2, cx, cy)              # вода рядом → Shipyard разрешён
    return knight


# Биты MP2 → ключи слотов окна строительства (town_pack.CONSTRUCT_SLOTS). Раскладка = castle.cpp:121-147.
_COMMON_KEY = [(0x0002, "THIEVES"), (0x0004, "TAVERN"), (0x0008, "SHIPYARD"), (0x0010, "WELL"),
               (0x0080, "STATUE"), (0x0100, "LTUR"), (0x0200, "RTUR"), (0x0400, "MARKET"),
               (0x0800, "WEL2"), (0x1000, "MOAT"), (0x2000, "SPEC")]
_DWELL_KEY = [(0x0008, "DW1"), (0x0010, "DW2"), (0x0020, "DW3"), (0x0040, "DW4"),
              (0x0080, "DW5"), (0x0100, "DW6")]


# --- Статусы построек Knight-замка (Castle::CheckBuyBuilding, castle.cpp:1137) ---
# Стоимость KNGT/ALL (gold,wood,mercury,ore,sulfur,crystal,gems) — BuildingInfo::GetCost (buildinginfo.cpp).
KNGT_COST = {
    "DW1": (200, 0, 0, 0, 0, 0, 0),
    "DW2": (1000, 0, 0, 0, 0, 0, 0),  "DW3": (1000, 0, 0, 5, 0, 0, 0),  "DW4": (2000, 10, 0, 10, 0, 0, 0),
    "DW5": (3000, 20, 0, 0, 0, 0, 0), "DW6": (5000, 20, 0, 0, 0, 20, 0),
    "MAGE": (2000, 5, 0, 5, 0, 0, 0), "TAVERN": (500, 5, 0, 0, 0, 0, 0), "THIEVES": (750, 5, 0, 0, 0, 0, 0),
    "SHIPYARD": (2000, 20, 0, 0, 0, 0, 0), "STATUE": (1250, 0, 0, 5, 0, 0, 0), "MARKET": (500, 5, 0, 0, 0, 0, 0),
    "WELL": (500, 0, 0, 0, 0, 0, 0), "WEL2": (1000, 0, 0, 0, 0, 0, 0), "SPEC": (1500, 5, 0, 15, 0, 0, 0),
    "LTUR": (1500, 0, 0, 5, 0, 0, 0), "RTUR": (1500, 0, 0, 5, 0, 0, 0), "MOAT": (750, 0, 0, 0, 0, 0, 0),
}
# Prereq KNGT (getBuildingRequirement, castle_building_info.cpp:1097) — ключи слотов, что должны быть построены.
KNGT_REQ = {
    "DW2": ["DW1"], "DW3": ["DW1", "WELL"], "DW4": ["DW1", "TAVERN"],
    "DW5": ["DW2", "DW3", "DW4"], "DW6": ["DW2", "DW3", "DW4"],
}
FUND_KEYS = ("gold", "wood", "mercury", "ore", "sulfur", "crystal", "gems")


def build_statuses(castle: dict, funds: dict, has_sea: bool = False) -> dict:
    """{key: статус} для 18 слотов Knight-окна строительства по Castle::CheckBuyBuilding.
    Статусы: BUILT / ALLOW / REQUIRES / DISABLE / LACK. funds = казна королевства."""
    built = default_built_keys(castle)
    out = {}
    for key, cost in KNGT_COST.items():
        if key in built:
            out[key] = "BUILT"; continue
        if key == "SHIPYARD" and not has_sea:
            out[key] = "DISABLE"; continue                   # SHIPYARD_NOT_ALLOWED (нет выхода к морю)
        req = KNGT_REQ.get(key, [])
        if any(r not in built for r in req):
            out[key] = "REQUIRES"; continue                  # REQUIRES_BUILD (не построены prereq)
        if any(cost[i] > funds.get(FUND_KEYS[i], 0) for i in range(7)):
            out[key] = "LACK"; continue                      # LACK_RESOURCES (не хватает казны)
        out[key] = "ALLOW"                                   # ALLOW_BUILD
    out["DW1"] = "BUILT" if "DW1" in built else "ALLOW"
    return out


def default_built_keys(castle: dict) -> set:
    """РЕАЛЬНО построенные здания замка (ключи слотов окна строительства). По Castle::LoadFromMP2:
    custom_bld!=0 → парсим битовые поля; custom_bld==0 → _setDefaultBuildings (только DWELLING_MONSTER1;
    DWELLING_MONSTER2 рандомна 50% на NORMAL — детерминированно НЕ строим). Castle keep/tent — не слот сетки."""
    if castle.get("custom_buildings"):
        keys = set()
        common, dw = castle.get("common_bits", 0), castle.get("dwelling_bits", 0)
        for bit, k in _COMMON_KEY:
            if common & bit:
                keys.add(k)
        for bit, k in _DWELL_KEY:
            if dw & bit:
                keys.add(k)
        if castle.get("mage_guild", 0) > 0:
            keys.add("MAGE")
        return keys
    return {"DW1"}                                            # _setDefaultBuildings: DWELLING_MONSTER1


def panorama_built_keys(castle: dict) -> set:
    """Построенные здания для ПАНОРАМЫ города (redrawCastleBuildings рисует только их). Grid built-set
    + CASTLE keep (если is_castle) — keep рисуется всегда при замке (не слот сетки)."""
    keys = set(default_built_keys(castle))
    if castle.get("is_castle"):
        keys.add("CASTLE")
    return keys


def emit_inc(mx2: Path, out: Path) -> None:
    """Эмит generated_castle.inc: реальные данные замка игрока (кровь) — имя, раса, флаги, битмаски."""
    c = knight_castle(mx2)
    L = ["; Сгенерировано Source/Tools/dump_mp2_castles.py — РЕАЛЬНЫЕ данные замка игрока из MX2.",
         "                ifndef _HMM2_GENERATED_CASTLE_",
         "                define _HMM2_GENERATED_CASTLE_", ""]
    name = c.get("name", "") or "Castle"
    L.append(f'CastleName:      DEFB "{name}", 0        ; имя замка игрока (MP2 custom name)')
    L.append(f"CASTLE_NAME_LEN  EQU {len(name)}")
    L.append(f"CASTLE_RACE      EQU {c.get('race_byte', 0)}          ; 0=KNGT")
    L.append(f"CASTLE_IS_CASTLE EQU {1 if c.get('is_castle') else 0}")
    L.append(f"CASTLE_POS_X     EQU {c.get('x', 24)}")
    L.append(f"CASTLE_POS_Y     EQU {c.get('y', 13)}")
    L.append(f"CASTLE_HAS_CAPTAIN EQU {c.get('has_captain', 0)}")
    L.append(f"CASTLE_MAGEGUILD EQU {c.get('mage_guild', 0)}")
    L.append(f"CASTLE_CUSTOM_BLD EQU {c.get('custom_buildings', 0)}   ; 0 = дефолтные постройки (_setDefaultBuildings)")
    L.append(f"CASTLE_COMMON_BITS EQU #{c.get('common_bits', 0):04X}")
    L.append(f"CASTLE_DWELL_BITS  EQU #{c.get('dwelling_bits', 0):04X}")
    L.append("                endif")
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"castle inc -> {out}: name='{name}' race={RACE_NAMES.get(c.get('race_byte',0),'?')} "
          f"custom_bld={c.get('custom_buildings',0)}")


def main() -> int:
    if len(sys.argv) > 2 and sys.argv[1] == "--inc":
        emit_inc(Path("Assets/Original/MAPS/SKIRMISH.MX2"), Path(sys.argv[2]))
        return 0
    mx2 = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Assets/Original/MAPS/SKIRMISH.MX2")
    r = extract(mx2)
    print(f"map {r['width']}x{r['height']}: {len(r['castle_pos'])} замков (координаты), "
          f"{len(r['castles'])} структур замков")
    for c in r["castle_pos"]:
        print(f"  @({c['x']},{c['y']}) race={RACE_NAMES.get(c['race'],'?')} castle={c['is_castle']}")
    for i, c in enumerate(r["castles"]):
        common = [n for (bit, n) in COMMON_BUILDINGS if c["common_bits"] & bit]
        dw = [n for (bit, n) in DWELLINGS if c["dwelling_bits"] & bit]
        print(f"  [{i}] name='{c['name']}' race={RACE_NAMES.get(c['race_byte'],'?')} "
              f"castle={c['is_castle']} captain={c['has_captain']} mageGuild={c['mage_guild']} "
              f"custom_bld={c['custom_buildings']}")
        print(f"       common={common}")
        print(f"       dwellings={dw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
