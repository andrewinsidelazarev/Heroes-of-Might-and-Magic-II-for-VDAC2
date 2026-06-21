#!/usr/bin/env python3
"""Собрать C-оверлей HiScores в Build/hiscores_ovl.bin.

Запускается после sjasmplus: адреса ABI-обвязок берутся из Build/hmm2.sym.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "Build"
SRC = ROOT / "Source" / "C"
SYM = BUILD / "hmm2.sym"
ABI_HEADER = SRC / "hiscores_abi_autogen.h"
OUT_IHX = BUILD / "hiscores.ihx"
OUT_BIN_RAW = BUILD / "hiscores_raw.bin"
OUT_BIN = BUILD / "hiscores_ovl.bin"
OUT_DATA_BIN = BUILD / "hiscores_data.bin"

REQUIRED_SYMBOLS = [
    "HscAbi_RenderBegin",
    "HscAbi_RenderEnd",
    "HscAbi_WaitFrame",
    "HscAbi_EmitSprite",
    "HscAbi_SetPalette",
    "HscAbi_PollInput",
    "HscAbi_GoMenu",
    "HscAbi_SetGameMode",
    "HscAbi_ReadHgs",
    "HscAbi_WriteHgsSlot",
    "HsAbiCmd",
    "HsAbiStatus",
    "HsAbiSlot",
    "HsAbiPtr",
    "HsAbiAddrLo",
    "HsAbiAddrHi",
    "HsAbiW",
    "HsAbiH",
    "HsAbiSizeW",
    "HsAbiSizeH",
    "HsAbiVX",
    "HsAbiVY",
    "HsAbiInputX",
    "HsAbiInputY",
    "HsAbiInputLmb",
    "HsAbiInputEsc",
    "HsAbiMode",
]


def parse_sym(path: Path) -> dict[str, int]:
    pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_.]*):\s+EQU\s+0x([0-9A-Fa-f]+)")
    out: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = pattern.match(line.strip())
        if m:
            out[m.group(1)] = int(m.group(2), 16)
    return out


def emit_header(symbols: dict[str, int]) -> None:
    missing = [name for name in REQUIRED_SYMBOLS if name not in symbols]
    if missing:
        raise RuntimeError("missing ABI symbols in hmm2.sym: " + ", ".join(missing))

    lines = [
        "/* Сгенерировано Source/Tools/build_hiscores_c.py. */",
        "#ifndef HMM2_HISCORES_ABI_AUTOGEN_H",
        "#define HMM2_HISCORES_ABI_AUTOGEN_H",
        "",
    ]
    for name in REQUIRED_SYMBOLS:
        lines.append(f"#define HMM2_{name} 0x{symbols[name] & 0xFFFF:04X}")
    lines.append("")
    lines.append("#endif")
    ABI_HEADER.write_text("\n".join(lines), encoding="utf-8")


def run(cmd: list[str]) -> None:
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build SDCC HiScores overlay.")
    parser.add_argument("--sdcc", default=os.environ.get("SDCC", r"C:\Program Files\SDCC\bin\sdcc.exe"))
    parser.add_argument("--sdasz80", default=os.environ.get("SDASZ80", r"C:\Program Files\SDCC\bin\sdasz80.exe"))
    parser.add_argument("--makebin", default=os.environ.get("MAKEBIN", r"C:\Program Files\SDCC\bin\makebin.exe"))
    args = parser.parse_args()

    if not SYM.exists():
        raise SystemExit(f"{SYM} not found; run sjasmplus first")

    BUILD.mkdir(parents=True, exist_ok=True)
    symbols = parse_sym(SYM)
    emit_header(symbols)

    crt_rel = BUILD / "hiscores_crt0.rel"
    src_rel_prefix = BUILD / "hiscores"

    run([args.sdasz80, "-o", str(crt_rel), str(SRC / "hiscores_crt0.s")])
    run(
        [
            args.sdcc,
            "-mz80",
            "--std-sdcc11",
            "--opt-code-speed",
            "--no-std-crt0",
            "--code-loc",
            "0xC050",
            "--data-loc",
            "0x4000",
            "-I",
            str(SRC),
            str(crt_rel),
            str(SRC / "hiscores.c"),
            "-o",
            str(OUT_IHX),
        ]
    )
    run([args.makebin, "-s", "65536", str(OUT_IHX), str(OUT_BIN_RAW)])

    raw = OUT_BIN_RAW.read_bytes()
    start = 0xC000
    end = len(raw)
    if len(raw) >= 0x10000:
        # makebin -p обычно дает полный 64K образ. Берем страницу #C000..#FFFF.
        page = raw[start:0x10000]
    else:
        page = raw
    page = page.rstrip(b"\x00")
    if len(page) > 0x4000:
        raise RuntimeError(f"HiScores C overlay is {len(page)} bytes, slot3 limit is 16384")
    OUT_BIN.write_bytes(page)
    data_page = raw[0x4000:0x8000].rstrip(b"\x00")
    if len(data_page) > 0x4000:
        raise RuntimeError(f"HiScores C data page is {len(data_page)} bytes, slot1 limit is 16384")
    OUT_DATA_BIN.write_bytes(data_page)
    print(f"hiscores C overlay -> {OUT_BIN}: {len(page)} bytes")
    print(f"hiscores C data    -> {OUT_DATA_BIN}: {len(data_page)} bytes")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
