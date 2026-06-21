#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


REG_DLSWAP = "#302054"
REG_INT_FLAGS = "#3020A8"
REG_CMD_READ = "#3020F8"
REG_CMD_WRITE = "#3020FC"


def hxbyte(text: str | None) -> int | None:
    if not isinstance(text, str) or not text.startswith("#"):
        return None
    return int(text[1:], 16)


def hxdword(text: str | None) -> int | None:
    if not isinstance(text, str) or not text.startswith("#"):
        return None
    return int(text[1:], 16)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_summary(path: Path) -> dict[str, Any]:
    counts = Counter()
    regions = Counter()
    reg_writes: list[tuple[int, str, int]] = []
    reg_reads: list[tuple[int, str, int]] = []
    cmd_bytes = bytearray()
    ramg_ranges: list[tuple[int, int]] = []
    current_ramg: tuple[int, int] | None = None
    cs_depth = 0
    errors: list[str] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            event = item.get("event")
            counts[str(event)] += 1
            region = item.get("region")
            if isinstance(region, str):
                regions[region] += 1

            if event == "FT_CS":
                active = bool(item.get("active"))
                cs_depth += 1 if active else -1
                if cs_depth not in (0, 1):
                    errors.append(f"bad CS depth {cs_depth} at seq={item.get('seq')}")

            if event == "FT_XFER_OUT":
                addr = hxdword(item.get("write_addr"))
                value = hxbyte(item.get("mosi"))
                if addr is None or value is None:
                    continue
                if region == "RAM_CMD_WRITE":
                    cmd_bytes.append(value)
                elif region == "REG":
                    reg_writes.append((int(item["seq"]), f"#{addr:06X}", value))
                elif region == "RAM_G":
                    if current_ramg is None:
                        current_ramg = (addr, addr + 1)
                    elif current_ramg[1] == addr:
                        current_ramg = (current_ramg[0], addr + 1)
                    else:
                        ramg_ranges.append(current_ramg)
                        current_ramg = (addr, addr + 1)
            else:
                if current_ramg is not None:
                    ramg_ranges.append(current_ramg)
                    current_ramg = None

            if event == "FT_XFER_IN":
                addr = hxdword(item.get("read_addr"))
                value = hxbyte(item.get("returned"))
                if addr is not None and value is not None and region == "REG":
                    reg_reads.append((int(item["seq"]), f"#{addr:06X}", value))

    if current_ramg is not None:
        ramg_ranges.append(current_ramg)

    return {
        "path": str(path),
        "events": sum(counts.values()),
        "counts": dict(sorted(counts.items())),
        "regions": dict(sorted(regions.items())),
        "errors": errors[:32],
        "cmd_bytes": len(cmd_bytes),
        "cmd_sha256": sha(bytes(cmd_bytes)),
        "cmd_tail": bytes(cmd_bytes[-64:]).hex(" ").upper(),
        "ramg_range_count": len(ramg_ranges),
        "ramg_ranges_head": [
            {"start": f"#{a:06X}", "end": f"#{b:06X}", "bytes": b - a}
            for a, b in ramg_ranges[:16]
        ],
        "ramg_ranges_tail": [
            {"start": f"#{a:06X}", "end": f"#{b:06X}", "bytes": b - a}
            for a, b in ramg_ranges[-16:]
        ],
        "reg_writes_tail": [
            {"seq": seq, "addr": addr, "value": f"#{value:02X}"}
            for seq, addr, value in reg_writes[-32:]
        ],
        "reg_write_counts": dict(sorted(Counter(addr for _, addr, _ in reg_writes).items())),
        "reg_read_counts": dict(sorted(Counter(addr for _, addr, _ in reg_reads).items())),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize HMM2 FT812 bus JSONL traces.")
    ap.add_argument("trace", type=Path, nargs="+")
    args = ap.parse_args()

    summaries = [load_summary(path) for path in args.trace]
    print(json.dumps(summaries, indent=2, ensure_ascii=False, sort_keys=True))
    if len(summaries) == 2:
        a, b = summaries
        print()
        print("COMPARE")
        print(f"cmd_bytes_delta={b['cmd_bytes'] - a['cmd_bytes']}")
        print(f"events_delta={b['events'] - a['events']}")
        for key in sorted(set(a["regions"]) | set(b["regions"])):
            print(f"region_delta {key}: {b['regions'].get(key, 0) - a['regions'].get(key, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
