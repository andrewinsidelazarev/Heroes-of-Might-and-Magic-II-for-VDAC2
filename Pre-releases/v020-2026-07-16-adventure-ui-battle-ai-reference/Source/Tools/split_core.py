from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "Build"
CORE = BUILD / "Core.bin"
PAGE1 = BUILD / "Core_p05.bin"
PAGE2 = BUILD / "Core_p06.bin"

ENTRY_OFFSET = 0x1000
PAGE_SIZE = 0x4000
FIRST_PART_SIZE = PAGE_SIZE - ENTRY_OFFSET


def main() -> int:
    data = CORE.read_bytes()
    page1 = data[:FIRST_PART_SIZE]
    page2 = data[FIRST_PART_SIZE:]

    if len(page2) > PAGE_SIZE:
        print(
            f"ERROR: Core.bin tail is {len(page2)} bytes, "
            f"slot2 limit is {PAGE_SIZE} bytes"
        )
        return 1

    PAGE1.write_bytes(page1)
    PAGE2.write_bytes(page2)
    print(f"Core split: p05={len(page1)} bytes, p06={len(page2)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
