"""HMM2SCN.PAK — потоковые ОВЕРЛЕИ сцен (код город/бой/хайскоры) для загрузчика.

SPG = только загрузчик+меню+переменные (см. [[hmm2-spg-loader-streaming-architecture]]).
Код сцен (town.asm/battle.asm/hiscores.asm) собирается в overlay-страницы slot3 (#A6/#A8/#A5),
РАНЬШЕ запекался в SPG. Выносим в HMM2SCN.PAK; резидентные Enter-трамплины стримят нужный
оверлей в его страницу перед запуском (как карта в HMM2MAP.PAK).

Каждый оверлей ПАДДИТСЯ до 16КБ (1 страница = 32 сектора) → раскладка ДЕТЕРМИНИРОВАНА
(town@сектор1, battle@33, hiscores@65) независимо от размера кода → .inc стабилен, порядок
сборки не циклический (assemble использует .inc, scn_pack пакует .bin'ы ПОСЛЕ сборки).

Запускать ПОСЛЕ ассемблера (нужны Build/*_ovl.bin = SAVEBIN-выходы main.asm).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Source/Tools"))
from pak_builder import build_pak, TYPE_Z80_PAGE, SECTOR

OUT_PAK = ROOT / "Build/HMM2SCN.PAK"
OUT_INC = ROOT / "Source/ASM/generated_scn_stream.inc"
PAGE_BYTES = 16384                                  # 1 TS-страница = 32 сектора

# (имя константы сектора, страница slot3, файл оверлея). Порядок = раскладка в PAK.
OVERLAYS = [
    ("SCN_TOWN_SECTOR",  0xA6, "Build/town_ovl.bin"),
    ("SCN_BATTLE_SECTOR", 0xA8, "Build/battle_ovl.bin"),
    ("SCN_HISC_SECTOR",  0xA5, "Build/hiscores_ovl.bin"),
]


def main() -> int:
    entries = []
    for _, page, fn in OVERLAYS:
        p = ROOT / fn
        if not p.exists():
            print(f"scn_pack: НЕТ {fn} — собери main.asm сначала (SAVEBIN)", file=sys.stderr)
            return 1
        data = p.read_bytes()
        if len(data) > PAGE_BYTES:
            print(f"scn_pack: {fn} = {len(data)}б > 16КБ (не влезает в страницу)", file=sys.stderr)
            return 1
        data = data + b"\x00" * (PAGE_BYTES - len(data))    # паддинг до полной страницы
        entries.append({"type": TYPE_Z80_PAGE, "target": page, "data": data})

    summary = build_pak(entries, OUT_PAK)

    # sec_off каждой записи детерминирован (body_start + i*32). Перечитываем из каталога
    # для надёжности.
    from pak_builder import read_pak_catalog
    cat = read_pak_catalog(OUT_PAK)["entries"]

    L = []
    L.append("; Сгенерировано Source/Tools/scn_pack.py — стрим оверлеев сцен (HMM2SCN.PAK).")
    L.append("                ifndef _HMM2_GENERATED_SCN_STREAM_")
    L.append("                define _HMM2_GENERATED_SCN_STREAM_")
    L.append('ScnPakName:          DEFB "HMM2SCN.PAK", 0')
    L.append(f"SCN_OVL_SECTORS      EQU {PAGE_BYTES // SECTOR}   ; 32 = полная страница 16КБ")
    for (name, _, _), e in zip(OVERLAYS, cat):
        L.append(f"{name:<20} EQU {e['sec_off']}")
    L.append("                endif")
    OUT_INC.write_text("\n".join(L) + "\n", encoding="utf-8")

    secs = [e["sec_off"] for e in cat]
    print(f"scn pack -> HMM2SCN.PAK: {len(entries)} оверлея, секторы {secs}, "
          f"{summary['total_bytes']//1024} КБ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
