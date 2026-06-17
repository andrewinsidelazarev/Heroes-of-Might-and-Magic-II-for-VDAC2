#!/usr/bin/env python3
from __future__ import annotations

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT, attach_hmm2_shadow
from shadow_ft812 import REG_PCLK


def main() -> int:
    emu = HMM2FullZ80Emulator(ROOT)
    regs = attach_hmm2_shadow(emu)
    writes = []
    orig = emu._write_ft_addr

    def hooked(addr: int, value: int) -> None:
        if addr == REG_PCLK:
            writes.append((emu.reg.PC, value & 0xFF))
        orig(addr, value)

    emu._write_ft_addr = hooked
    emu.call(emu.sym["Platform_Init"], max_steps=4_000_000)
    print("записи REG_PCLK:")
    for pc, value in writes:
        print(f"  PC=#{pc:04X} value=#{value:02X}")
    print(f"итог REG_PCLK={regs._get32(REG_PCLK)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
