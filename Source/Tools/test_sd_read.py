#!/usr/bin/env python3
"""Узел 0 / шаг 1: изолированный тест sd_zc + SD-модель эмулятора.
Читает сектор 0 (BPB FAT32) с backing-образа Diagnostics/sd.img и проверяет подпись."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tsconf_ft812_sim import TSConfFT812Machine

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    emu = TSConfFT812Machine(
        ROOT,
        sym_path=ROOT / "Build" / "sdtest.sym",
        load_spg=False,
        init_cpu=True,
        default_start="0x6000",
    )
    code = (ROOT / "Build" / "sdtest.bin").read_bytes()
    for i, b in enumerate(code):
        emu.mem.write(0x6000 + i, b)
    emu.load_sd_image(ROOT / "Diagnostics" / "sd.img")

    emu.call(emu.sym["SdTest"], max_steps=20_000_000)

    buf = emu.get_memory(0x8000, 512)
    sig = buf[510:512]
    bps = buf[0x0B] | (buf[0x0C] << 8)
    spc = buf[0x0D]
    print(f"sector0[0:16]: {buf[:16].hex()}")
    print(f"OEM/jump:      {buf[:3].hex()} ('{bytes(buf[3:11]).decode(chr(39)+'ascii'+chr(39),'replace')}')")
    print(f"boot signature [510:512]: {sig.hex()} (ожид 55aa)")
    print(f"bytes/sector: {bps}, sectors/cluster: {spc}")

    if sig != b"\x55\xaa":
        print("ОШИБКА: нет boot-подписи 0x55AA — SD-чтение не сработало")
        return 1
    if bps != 512:
        print(f"ОШИБКА: bytes/sector={bps} != 512")
        return 1
    if spc == 0:
        print("ОШИБКА: sectors/cluster=0 — не похоже на валидный BPB")
        return 1
    print("=== test_sd_read: PASS (сектор 0 прочитан, BPB валиден) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
