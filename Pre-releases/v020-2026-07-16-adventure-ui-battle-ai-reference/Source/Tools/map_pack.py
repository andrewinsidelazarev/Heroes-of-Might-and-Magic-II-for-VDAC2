"""HMM2MAP.PAK — потоковая карта adventure (террейн/объекты/вьюпорты/структура).

Балласт, который РАНЬШЕ запекался прямо в SPG (≈2.3 МБ, 144 страницы) → выносим в
PAK и стримим загрузчиком в Z80-страницы на входе в adventure (Adventure_Enter).
SPG остаётся загрузчиком (см. spgbld_loader.ini).

Источник списка страниц — spgbld_vdac2.ini (раздутый dev-конфиг): берём все Block'и,
КРОМЕ резидента/загрузчика/меню/музыки/переменных/курсора и оверлеев сцен (город/бой/
хайскоры — у них свой стрим). Каждая страница → запись TYPE_Z80_PAGE (target = № страницы).

Loader читает тело PAK ПОСЛЕДОВАТЕЛЬНО (Loader_ReadSectors с текущей позиции). Блоки
уложены подряд, выровнены на сектор → читаем ceil(size/512) секторов в свою страницу,
позиция сама встаёт на начало следующего блока. ASM-цикл ведёт MapStreamTable (page,sectors).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Source/Tools"))
from pak_builder import build_pak, TYPE_Z80_PAGE, SECTOR

SPG_INI = ROOT / "spgbld_vdac2.ini"
OUT_PAK = ROOT / "Build/HMM2MAP.PAK"
OUT_INC = ROOT / "Source/ASM/generated_map_stream.inc"

# Страницы, которые ОСТАЮТСЯ в SPG-загрузчике (не стримим). Резидент/загрузчик/меню/
# музыка/переменные/курсор + оверлеи сцен (свой стрим позже) + СТРУКТУРА карты
# (#10 map / #11 path / #14 pass): map.bin=32КБ укладывается spgbld'ом особым образом
# через 2 страницы — оставляем как в рабочем dev-SPG (мелкая, ~36КБ, без головоломки).
# Стримим ТОЛЬКО битмапы террейна/объектов/вьюпортов (#20-8F/#96-99/#C4 — 2.2МБ, по 1 стр).
NON_MAP_PAGES = {0x05, 0x06, 0x10, 0x11, 0x12, 0x14, 0x91,
                 0xA0, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8}


def parse_blocks(ini_path: Path):
    """[(page:int, file:Path)] из строк 'Block = #addr, #page, file'."""
    out = []
    for line in ini_path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s.startswith("Block"):
            continue
        rhs = s.split("=", 1)[1]
        addr_s, page_s, file_s = (p.strip() for p in rhs.split(",", 2))
        page = int(page_s.lstrip("#"), 16)
        out.append((page, ROOT / file_s))
    return out


def main() -> int:
    blocks = parse_blocks(SPG_INI)
    map_blocks = [(pg, fn) for (pg, fn) in blocks if pg not in NON_MAP_PAGES]
    if not map_blocks:
        print("map_pack: НЕТ страниц карты — проверь фильтр", file=sys.stderr)
        return 1

    entries = []
    table = []   # (page, sector_count) в порядке тела PAK
    for page, fn in map_blocks:
        data = fn.read_bytes()
        entries.append({"type": TYPE_Z80_PAGE, "target": page, "data": data})
        sectors = (len(data) + SECTOR - 1) // SECTOR
        if sectors > 255:
            print(f"map_pack: страница #{page:02X} = {sectors} секторов >255 (B 8-бит)", file=sys.stderr)
            return 1
        table.append((page, sectors))

    summary = build_pak(entries, OUT_PAK)

    L = []
    L.append("; Сгенерировано Source/Tools/map_pack.py — стрим карты adventure (HMM2MAP.PAK).")
    L.append("                ifndef _HMM2_GENERATED_MAP_STREAM_")
    L.append("                define _HMM2_GENERATED_MAP_STREAM_")
    L.append('MapPakName:          DEFB "HMM2MAP.PAK", 0')
    L.append(f"MAP_BODY_SECTOR      EQU {summary['body_start_sector']}   ; первый сектор тела (пропустить header+каталог)")
    L.append(f"MAP_STREAM_COUNT     EQU {len(table)}")
    L.append("MapStreamTable:      ; на запись: DEFB страница, число_секторов")
    for page, sectors in table:
        L.append(f"                DEFB #{page:02X}, {sectors}")
    L.append("                endif")
    OUT_INC.write_text("\n".join(L) + "\n", encoding="utf-8")

    total_kb = summary["total_bytes"] // 1024
    print(f"map pack -> HMM2MAP.PAK: {len(table)} страниц, {summary['total_sectors']} секторов, "
          f"{total_kb} КБ (body_sector={summary['body_start_sector']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
