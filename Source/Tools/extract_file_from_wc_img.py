#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "ZumaRef"))

from inject_zuma_to_wc_img import ATTR_DIRECTORY, Fat32Image  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Извлечь файл из FAT32 wc.img для проверки.")
    parser.add_argument("--img", type=Path, required=True)
    parser.add_argument("--dir", nargs="+", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    fat = Fat32Image(args.img)
    cluster = fat.root_cluster
    for part in args.dir:
        entry = fat.find_entry(cluster, part)
        if entry is None or not (entry["attr"] & ATTR_DIRECTORY):
            raise SystemExit(f"нет папки: {part}")
        cluster = entry["cluster"]
    entry = fat.find_entry(cluster, args.name)
    if entry is None or (entry["attr"] & ATTR_DIRECTORY):
        raise SystemExit(f"нет файла: {args.name}")

    data = fat.read_chain(entry["cluster"])[: entry["size"]]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(f"извлечено: {args.out}")
    print(f"размер: {len(data)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
