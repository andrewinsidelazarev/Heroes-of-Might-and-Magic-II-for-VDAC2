#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from inject_zuma_to_wc_img import ATTR_DIRECTORY, Fat32Image


DEFAULT_IMG = Path(r"\\tsclient\D\Работа.Андрей\unreal_x64\wc.img")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser(description="Добавить или заменить один файл внутри существующего FAT32 wc.img.")
    parser.add_argument("--img", type=Path, default=DEFAULT_IMG)
    parser.add_argument("--src", type=Path, required=True)
    parser.add_argument("--dir", nargs="+", required=True)
    parser.add_argument("--name", default=None)
    args = parser.parse_args()

    if not args.img.exists():
        raise SystemExit(f"image not found: {args.img}")
    if not args.src.exists():
        raise SystemExit(f"source not found: {args.src}")

    image = Fat32Image(args.img)
    cluster = image.root_cluster
    for part in args.dir:
        cluster = image.ensure_dir(cluster, part)

    target_name = args.name or args.src.name
    image.write_file(cluster, target_name, args.src)
    image.save()

    check = Fat32Image(args.img)
    check_cluster = check.root_cluster
    for part in args.dir:
        entry = check.find_entry(check_cluster, part)
        if entry is None or not (entry["attr"] & ATTR_DIRECTORY):
            raise SystemExit(f"ОШИБКА: после записи нет папки: {part}")
        check_cluster = entry["cluster"]
    entry = check.find_entry(check_cluster, target_name)
    if entry is None or (entry["attr"] & ATTR_DIRECTORY):
        raise SystemExit(f"ОШИБКА: после записи нет файла: {target_name}")

    src_data = args.src.read_bytes()
    img_data = check.read_chain(entry["cluster"])[: entry["size"]]
    if src_data != img_data:
        raise SystemExit("ОШИБКА: файл в образе не совпадает с локальным источником")

    print(f"образ: {args.img} (изменен на месте)")
    print(f"папка: /{'/'.join(args.dir)}/")
    print(f"файл: {target_name} {args.src.stat().st_size}")
    print(f"sha256: {sha(src_data)}")
    print("OK: файл в образе совпадает с локальным источником")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
