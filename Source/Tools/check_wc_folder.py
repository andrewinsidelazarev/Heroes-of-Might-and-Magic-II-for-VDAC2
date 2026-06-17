#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ZUMA_TOOLS = Path(r"C:\Users\Администратор\Desktop\Zuma Deluxe VDAC2\Source\OTHER")
sys.path.insert(0, str(ZUMA_TOOLS))

from inject_zuma_to_wc_img import ATTR_DIRECTORY, Fat32Image


def main() -> int:
    parser = argparse.ArgumentParser(description="List a folder inside a FAT32 wc.img.")
    parser.add_argument("--img", type=Path, required=True)
    parser.add_argument("--dir", nargs="+", required=True)
    args = parser.parse_args()

    image = Fat32Image(args.img)
    cluster = image.root_cluster
    for part in args.dir:
        entry = image.find_entry(cluster, part)
        if entry is None:
            raise SystemExit(f"missing directory: {part}")
        if not (entry["attr"] & ATTR_DIRECTORY):
            raise SystemExit(f"not a directory: {part}")
        cluster = entry["cluster"]

    print(f"image: {args.img}")
    print(f"folder: /{'/'.join(args.dir)}/ cluster={cluster}")
    for entry in image.parse_dir(cluster):
        kind = "dir" if entry["attr"] & ATTR_DIRECTORY else "file"
        print(f"{entry['name']}\t{kind}\t{entry['size']}\tcluster={entry['cluster']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
