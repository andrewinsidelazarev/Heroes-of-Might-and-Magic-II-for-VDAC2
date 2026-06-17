#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DUMP = ROOT / "111"
CORE = ROOT / "Build" / "Core.bin"
SYM = ROOT / "Build" / "hmm2.sym"
DL_INC = ROOT / "Source" / "ASM" / "generated_adventure_dl.inc"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def read_sym() -> dict[str, int]:
    out = {}
    rx = re.compile(r"^([^:]+):\s+EQU\s+0x([0-9A-Fa-f]+)")
    for line in SYM.read_text(encoding="utf-8", errors="replace").splitlines():
        m = rx.match(line)
        if m:
            out[m.group(1)] = int(m.group(2), 16)
    return out


def read_expected_dl_words() -> list[int]:
    # Минимальная проверка по реально собранному Core.bin надежнее, чем парсить ASM.
    return []


def hx(data: bytes) -> str:
    return " ".join(f"{b:02X}" for b in data)


def main() -> int:
    dump = DUMP.read_bytes()
    core = CORE.read_bytes()
    sym = read_sym()
    print(f"dump: {DUMP} размер={len(dump)} sha256={sha(dump)}")
    print(f"core: {CORE} размер={len(core)} sha256={sha(core)}")
    if len(dump) != 65536:
        print("ОШИБКА: дамп не 64К")
        return 1

    entry = 0x5C00
    core_in_dump = dump[entry:entry + len(core)]
    print(f"core-in-dump sha256={sha(core_in_dump)}")
    if core_in_dump == core:
        print("OK: в дампе по #5C00 лежит текущий Build/Core.bin")
    else:
        print("ОШИБКА: дамп по #5C00 не совпадает с текущим Build/Core.bin")
        for i, (a, b) in enumerate(zip(core, core_in_dump)):
            if a != b:
                print(f"первое отличие core offset=#{i:04X} addr=#{entry+i:04X}: build=#{a:02X} dump=#{b:02X}")
                break

    for name in ("Start", "Terrain_Upload", "Game_Init", "Render_Frame", "ADVENTURE_DL", "CoreEnd"):
        addr = sym.get(name)
        if addr is None:
            continue
        print(f"{name} #{addr:04X}: {hx(dump[addr:addr+24])}")

    # Проверяем, что текущий DL в дампе содержит CELL+VERTEX2F, а не старый VERTEX2II.
    dl = sym["ADVENTURE_DL"]
    dl_bytes = dump[dl:dl + 128]
    print(f"DL первые 128 байт sha256={sha(dl_bytes)}")
    print(f"DL первые 64 байта: {hx(dl_bytes[:64])}")
    has_vertex2ii = any((dl_bytes[i + 3] & 0xC0) == 0x80 for i in range(0, len(dl_bytes) - 3, 4))
    if has_vertex2ii:
        print("ОШИБКА: в первых командах DL дампа похожий VERTEX2II")
    else:
        print("OK: в первых командах DL дампа нет VERTEX2II")

    print(f"FrameCounter dump=#{dump[0x4100] | (dump[0x4101] << 8):04X}")
    print(f"GameMode dump=#{dump[0x4103]:02X}")
    print(
        "page-регистры dump: "
        f"PAGE0=#{dump[0x0410]:02X} PAGE1=#{dump[0x0411]:02X} "
        f"PAGE2=#{dump[0x0412]:02X} PAGE3=#{dump[0x0413]:02X}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
