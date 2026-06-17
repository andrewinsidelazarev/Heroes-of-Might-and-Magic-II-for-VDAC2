#!/usr/bin/env python3
from __future__ import annotations

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT, attach_hmm2_shadow


REG_FREQUENCY = 0x30200C


def main() -> int:
    emu = HMM2FullZ80Emulator(ROOT)
    attach_hmm2_shadow(emu)
    writes = []
    orig = emu._write_ft_addr

    def hooked(addr: int, value: int) -> None:
        if addr == REG_FREQUENCY:
            writes.append((emu.reg.PC, value & 0xFFFFFFFF))
        orig(addr, value)

    emu._write_ft_addr = hooked
    timed_out = None
    try:
        emu.call(emu.sym["Platform_Init"], max_steps=4_000_000)
        emu.call(emu.sym["Game_Init"], max_steps=12_000_000)
        emu.call(emu.sym["Render_Frame"], max_steps=4_000_000)
    except TimeoutError as exc:
        timed_out = str(exc)

    if not writes:
        print("записей REG_FREQUENCY нет")
        if timed_out:
            print(f"таймаут модели: {timed_out}")
        return 0
    print("записи REG_FREQUENCY:")
    for pc, value in writes:
        print(f"  PC=#{pc:04X} value=#{value:08X}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
