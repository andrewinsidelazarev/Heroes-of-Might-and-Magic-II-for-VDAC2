"""HPAK — формат PAK-файла для потоковой загрузки ассетов HMM2 с SD.

Файл читается loader'ом (raw_pak.asm) посекторно (CMD17), поэтому каждый блок
данных выровнен на границу сектора (512 Б) — чтобы грузить сразу в цель одним
SD-burst без копирования.

Формат:
  Header (16 Б):
    +0  magic 'HPAK' (4)
    +4  version  (u16 LE)
    +6  entries  (u16 LE)
    +8  reserved (8)
  Каталог (entries × 12 Б), на запись:
    +0  type     (u8)   1=RAM_G blob, 2=Z80 page, 3=palette RAM_G
    +1  target   (u24 LE) RAM_G-адрес (type 1/3) ИЛИ номер страницы (type 2, в младшем байте)
    +4  sec_off  (u16 LE) смещение блока от начала файла, В СЕКТОРАХ
    +6  byte_off (u16 LE) смещение внутри сектора (обычно 0)
    +8  size     (u32 LE) размер блока в байтах
  Тело: блоки данных, каждый выровнен на 512.

Loader: OpenFile(name) → прочитать header+каталог (сектор 0) → по каждой записи
RawPak-seek к sec_off и читать ceil(size/512) секторов в target (RAM_G через
FT.WriteMem или Z80-страницу).
"""

import struct
from pathlib import Path

HPAK_MAGIC = b"HPAK"
HPAK_VERSION = 1
SECTOR = 512
ENTRY_SIZE = 12
HEADER_SIZE = 16

TYPE_RAMG_BLOB = 1   # target = RAM_G-адрес (24 бита)
TYPE_Z80_PAGE = 2    # target = номер страницы (младший байт)
TYPE_PALETTE = 3     # target = RAM_G-адрес палитры


def _align_up(n: int, a: int) -> int:
    return (n + a - 1) // a * a


def build_pak(entries, out_path: Path) -> dict:
    """entries: список dict {type, target, data:bytes}. Возвращает сводку.

    Каждый блок данных выровнен на сектор. Каталог идёт сразу после header;
    тело начинается с первого сектора после header+каталога.
    """
    catalog_bytes = HEADER_SIZE + len(entries) * ENTRY_SIZE
    body_start = _align_up(catalog_bytes, SECTOR)

    catalog = bytearray()
    body = bytearray()
    cur = body_start
    for e in entries:
        data = e["data"]
        if cur % SECTOR != 0:                      # выровнять блок на сектор
            pad = SECTOR - (cur % SECTOR)
            body.extend(b"\x00" * pad)
            cur += pad
        sec_off = cur // SECTOR
        assert sec_off <= 0xFFFF, "файл > 32 МБ — sec_off не влезает в u16"
        target = e["target"] & 0xFFFFFF
        catalog += struct.pack("<B", e["type"] & 0xFF)
        catalog += bytes(((target) & 0xFF, (target >> 8) & 0xFF, (target >> 16) & 0xFF))
        catalog += struct.pack("<H", sec_off)
        catalog += struct.pack("<H", 0)            # byte_off (блоки на границе сектора)
        catalog += struct.pack("<I", len(data))
        body.extend(data)
        cur += len(data)

    header = HPAK_MAGIC + struct.pack("<HH", HPAK_VERSION, len(entries)) + b"\x00" * 8
    pre = bytearray(header) + catalog
    pre.extend(b"\x00" * (body_start - len(pre)))   # дополнить до начала тела
    if len(body) % SECTOR != 0:                     # хвост файла — на границу сектора
        body.extend(b"\x00" * (SECTOR - len(body) % SECTOR))

    out = bytes(pre) + bytes(body)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(out)
    return {
        "path": str(out_path),
        "entries": len(entries),
        "body_start_sector": body_start // SECTOR,
        "total_bytes": len(out),
        "total_sectors": len(out) // SECTOR,
    }


def read_pak_catalog(path: Path):
    """Распарсить header+каталог (для верификации/тестов). Возвращает список записей."""
    raw = Path(path).read_bytes()
    assert raw[:4] == HPAK_MAGIC, f"не HPAK: {raw[:4]!r}"
    version, count = struct.unpack_from("<HH", raw, 4)
    out = []
    off = HEADER_SIZE
    for _ in range(count):
        etype = raw[off]
        target = raw[off + 1] | (raw[off + 2] << 8) | (raw[off + 3] << 16)
        sec_off, byte_off = struct.unpack_from("<HH", raw, off + 4)
        size = struct.unpack_from("<I", raw, off + 8)[0]
        out.append({"type": etype, "target": target, "sec_off": sec_off, "byte_off": byte_off, "size": size})
        off += ENTRY_SIZE
    return {"version": version, "entries": out, "raw": raw}


if __name__ == "__main__":
    # Самотест: собрать PAK из двух блоков, перечитать каталог, проверить данные на
    # секторных границах и совпадение содержимого.
    import sys

    a = bytes(range(256)) * 3        # 768 Б
    b = b"\xAB" * 500                # 500 Б
    test_path = Path("Build/_pak_selftest.pak")
    summary = build_pak(
        [
            {"type": TYPE_RAMG_BLOB, "target": 0x0CA608, "data": a},
            {"type": TYPE_PALETTE, "target": 0x079000, "data": b},
        ],
        test_path,
    )
    print("build:", summary)
    cat = read_pak_catalog(test_path)
    assert cat["version"] == HPAK_VERSION
    assert len(cat["entries"]) == 2
    raw = cat["raw"]
    for entry, original in zip(cat["entries"], (a, b)):
        start = entry["sec_off"] * SECTOR + entry["byte_off"]
        assert start % SECTOR == 0, "блок не на границе сектора"
        assert raw[start:start + entry["size"]] == original, "содержимое блока не совпало"
    assert cat["entries"][0]["target"] == 0x0CA608
    assert cat["entries"][1]["target"] == 0x079000
    print("OK: HPAK self-test passed (выравнивание секторов + каталог + данные)")
    sys.exit(0)
