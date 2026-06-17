#!/usr/bin/env python3
import argparse
import csv
import struct
from pathlib import Path


AGG_NAME_LEN = 15


def agg_hash(name: str) -> int:
    h = 0
    total = 0
    for ch in reversed(name.upper()):
        c = ord(ch)
        h = ((h << 5) + (h >> 25)) & 0xFFFFFFFF
        total = (total + c) & 0xFFFFFFFF
        h = (h + total + c) & 0xFFFFFFFF
    return h


def read_agg_index(path: Path):
    data = path.read_bytes()
    if len(data) < 2:
        raise ValueError(f"{path}: файл слишком короткий")

    count = struct.unpack_from("<H", data, 0)[0]
    table_offset = 2
    table_size = count * 12
    names_offset = len(data) - count * AGG_NAME_LEN

    if names_offset <= table_offset + table_size:
        raise ValueError(f"{path}: неверная структура таблицы AGG")

    entries = []
    for i in range(count):
        item_hash, offset, size = struct.unpack_from("<III", data, table_offset + i * 12)
        raw_name = data[names_offset + i * AGG_NAME_LEN:names_offset + (i + 1) * AGG_NAME_LEN]
        name = raw_name.split(b"\0", 1)[0].decode("ascii", errors="replace")
        expected_hash = agg_hash(name)
        entries.append(
            {
                "name": name,
                "hash": item_hash,
                "expected_hash": expected_hash,
                "hash_ok": item_hash == expected_hash,
                "offset": offset,
                "size": size,
            }
        )

    return data, entries


def read_agg_index_with_expansion(base_path: Path):
    """Базовый AGG + (если рядом) HEROES2X.AGG дополнения PoL, объединённые в
    один (data, entries). Офсеты записей дополнения сдвинуты в конкатенированный
    буфер; базовые записи идут первыми (приоритет по имени при коллизиях).

    Карты PoL ссылаются на тайлсеты X_LOC1/2/3.ICN (icn_type 61/62/63), которых
    нет в базовом HEROES2.AGG — без слияния эти объекты молча теряются."""
    data, entries = read_agg_index(base_path)
    x_path = base_path.with_name("HEROES2X.AGG")
    if x_path.exists():
        x_data, x_entries = read_agg_index(x_path)
        base_len = len(data)
        merged = bytearray(data)
        merged.extend(x_data)
        for e in x_entries:
            shifted = dict(e)
            shifted["offset"] = e["offset"] + base_len
            entries.append(shifted)
        data = bytes(merged)
    return data, entries


def write_manifest(path: Path, entries):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=["name", "size", "offset", "hash", "expected_hash", "hash_ok"],
        )
        writer.writeheader()
        for entry in sorted(entries, key=lambda x: x["name"].lower()):
            writer.writerow(entry)


def extract_matching(data: bytes, entries, out_dir: Path, suffixes):
    out_dir.mkdir(parents=True, exist_ok=True)
    extracted = []
    suffixes = tuple(s.upper() for s in suffixes)

    for entry in entries:
        name = entry["name"]
        if not name.upper().endswith(suffixes):
            continue
        if not entry["hash_ok"]:
            raise ValueError(f"{name}: ошибка хэша")

        start = entry["offset"]
        end = start + entry["size"]
        if start < 0 or end > len(data) or end < start:
            raise ValueError(f"{name}: неверный диапазон {start}..{end}")

        target = out_dir / name.upper()
        target.write_bytes(data[start:end])
        extracted.append(target)

    return extracted


def main():
    parser = argparse.ArgumentParser(description="Проверить и извлечь ресурсы Heroes II AGG.")
    parser.add_argument("agg", nargs="+", type=Path, help="Входные AGG-файлы")
    parser.add_argument("--manifest-dir", type=Path, default=Path("Assets/Converted/Manifest"))
    parser.add_argument("--extract-xmi", action="store_true", help="Извлечь музыкальные ресурсы *.XMI")
    parser.add_argument("--xmi-dir", type=Path, default=Path("Assets/Converted/Music/XMI"))
    args = parser.parse_args()

    total_extracted = 0
    for agg_path in args.agg:
        data, entries = read_agg_index(agg_path)
        bad = [e for e in entries if not e["hash_ok"]]
        manifest = args.manifest_dir / f"{agg_path.stem}.csv"
        write_manifest(manifest, entries)

        print(f"{agg_path.name}: записей {len(entries)}, ошибок хэша {len(bad)}, манифест: {manifest}")

        if args.extract_xmi:
            out_dir = args.xmi_dir / agg_path.stem
            extracted = extract_matching(data, entries, out_dir, [".XMI"])
            total_extracted += len(extracted)
            print(f"{agg_path.name}: извлечено XMI-файлов {len(extracted)} в {out_dir}")

    if args.extract_xmi:
        print(f"Итого извлечено XMI: {total_extracted}")


if __name__ == "__main__":
    main()
