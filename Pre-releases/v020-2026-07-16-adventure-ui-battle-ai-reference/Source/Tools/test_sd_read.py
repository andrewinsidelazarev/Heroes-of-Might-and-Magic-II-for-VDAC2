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

    # --- шаг 1: чтение сектора 0 (BPB) ---
    emu.call(emu.sym["SdReadSector"], max_steps=20_000_000)
    buf = emu.get_memory(0x8000, 512)
    sig = buf[510:512]
    bps = buf[0x0B] | (buf[0x0C] << 8)
    spc = buf[0x0D]
    print(f"[шаг1] sector0[0:16]: {buf[:16].hex()}")
    print(f"[шаг1] boot sig: {sig.hex()} (ожид 55aa), bps={bps}, spc={spc}")
    if sig != b"\x55\xaa" or bps != 512 or spc == 0:
        print("ОШИБКА: невалидный BPB — SD-чтение не сработало")
        return 1
    print("[шаг1] PASS: сектор 0 прочитан, BPB валиден")

    # --- шаг 2: RawPak_Mount + RawPak_OpenFile(HMM2_VD2.SPG) ---
    emu.call(emu.sym["SdMountOpen"], max_steps=200_000_000)
    res = emu.get_byte(emu.sym["TestResult"])
    fsz = emu.get_memory(emu.sym["RawPak_FoundSize"], 4)
    found_size = fsz[0] | (fsz[1] << 8) | (fsz[2] << 16) | (fsz[3] << 24)
    clus = emu.get_memory(emu.sym["RawPak_FileStartClus"], 4)
    start_clus = clus[0] | (clus[1] << 8) | (clus[2] << 16) | (clus[3] << 24)
    def u32(name):
        b = emu.get_memory(emu.sym[name], 4)
        return b[0] | (b[1] << 8) | (b[2] << 16) | (b[3] << 24)
    stage = {0: "OK", 1: "MOUNT FAIL", 2: "OPENFILE FAIL"}.get(res, f"?{res:#04x}")
    print(f"[шаг2] стадия={stage}, FoundSize={found_size}, startClus={start_clus}")
    print(f"[шаг2] raw_pak: Spc={emu.get_byte(emu.sym['RawPak_Spc'])} "
          f"RootClus={u32('RawPak_RootClus')} FatStart={u32('RawPak_FatStart')} "
          f"DataStart={u32('RawPak_DataStart')}")
    if res != 0:
        print(f"ОШИБКА: RawPak шаг2 не прошёл (стадия={stage})")
        return 1
    if found_size == 0:
        print("ОШИБКА: FoundSize=0 — файл найден, но размер нулевой")
        return 1
    print("[шаг2] PASS: HMM2_VD2.SPG найден, run-table построена")

    # --- шаг 3: RawPak_ReadSectors — прочитать данные файла через run-table ---
    emu.call(emu.sym["SdReadData"], max_steps=200_000_000)
    res3 = emu.get_byte(emu.sym["TestResult"])
    PAGE = 0x07
    data = bytes(emu.mem.physical[PAGE * 0x4000: PAGE * 0x4000 + 2048])
    real = (ROOT / "Build" / "hmm2_vdac2.spg").read_bytes()[:2048]
    match = data == real
    print(f"[шаг3] TestResult={res3:#04x} (0=ok), первые 2КБ совпадают с SPG: {match}")
    print(f"[шаг3] data[0:16]={data[:16].hex()}  spg[0:16]={real[:16].hex()}")
    if res3 != 0:
        print("ОШИБКА: RawPak_ReadSectors вернул ошибку")
        return 1
    if not match:
        diff = next((i for i in range(2048) if data[i] != real[i]), -1)
        print(f"ОШИБКА: данные расходятся с offset {diff} (сектор {diff//512}, в секторе {diff%512})")
        lo = (diff // 16) * 16
        print(f"  got : {data[lo:lo+16].hex()}")
        print(f"  real: {real[lo:lo+16].hex()}")
        return 1
    print("[шаг3] PASS: данные файла прочитаны через run-table корректно")

    # --- шаг 4: открыть HMM2MENU.PAK и проверить blob (gate PAK-генератора) ---
    emu.call(emu.sym["SdReadMenuPak"], max_steps=200_000_000)
    res4 = emu.get_byte(emu.sym["TestResult"])
    PAGE = 0x07
    base = PAGE * 0x4000
    header = bytes(emu.mem.physical[base: base + 16])
    blob = bytes(emu.mem.physical[base + 512: base + 1024])   # сектор 1 = начало payload
    pak = (ROOT / "Build" / "HMM2MENU.PAK").read_bytes()
    pak_blob = pak[512:1024]                                  # body с сектора 1
    print(f"[шаг4] TestResult={res4:#04x} (0=ok), HPAK magic={header[:4]!r}")
    print(f"[шаг4] blob[0:16]={blob[:16].hex()}  pak[512:528]={pak_blob[:16].hex()}")
    if res4 != 0:
        print("ОШИБКА: RawPak не открыл/прочитал HMM2MENU.PAK")
        return 1
    if header[:4] != b"HPAK":
        print("ОШИБКА: сектор 0 PAK не HPAK header")
        return 1
    if blob != pak_blob:
        print("ОШИБКА: blob HMM2MENU.PAK прочитан неверно")
        return 1
    print("[шаг4] PASS: HMM2MENU.PAK открыт, HPAK header + blob читаются корректно")
    print("=== test_sd_read: PASS (загрузчик читает HMM2MENU.PAK с SD) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
