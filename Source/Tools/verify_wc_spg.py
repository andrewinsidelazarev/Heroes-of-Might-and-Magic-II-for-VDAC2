#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "ZumaRef"))

from inject_zuma_to_wc_img import ATTR_DIRECTORY, Fat32Image  # noqa: E402


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def read_file_from_image(img: Path, dirs: list[str], name: str) -> bytes:
    fat = Fat32Image(img)
    cluster = fat.root_cluster
    for part in dirs:
        entry = fat.find_entry(cluster, part)
        if entry is None or not (entry["attr"] & ATTR_DIRECTORY):
            raise SystemExit(f"ОШИБКА: нет папки в образе: {part}")
        cluster = entry["cluster"]
    entry = fat.find_entry(cluster, name)
    if entry is None or (entry["attr"] & ATTR_DIRECTORY):
        raise SystemExit(f"ОШИБКА: нет файла в образе: {name}")
    return fat.read_chain(entry["cluster"])[: entry["size"]]


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверить SPG внутри wc.img по SHA256.")
    parser.add_argument("--img", type=Path, required=True)
    parser.add_argument("--src", type=Path, default=Path("Build/hmm2_vdac2.spg"))
    parser.add_argument("--dir", nargs="+", default=["GAMES", "HEROES 2"])
    parser.add_argument("--name", default="HMM2VD2.SPG")
    args = parser.parse_args()

    local = args.src.read_bytes()
    image_file = read_file_from_image(args.img, args.dir, args.name)
    local_sha = sha(local)
    image_sha = sha(image_file)
    print(f"локальный SPG: {args.src} размер={len(local)} sha256={local_sha}")
    print(f"SPG в образе: /{'/'.join(args.dir)}/{args.name} размер={len(image_file)} sha256={image_sha}")
    if local != image_file:
        print("ОШИБКА: файл в wc.img не совпадает с локальной сборкой")
        return 1
    print("OK: SPG в wc.img совпадает с локальной сборкой")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
