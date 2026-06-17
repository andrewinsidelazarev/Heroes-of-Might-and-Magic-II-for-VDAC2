#!/usr/bin/env python3
from __future__ import annotations

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT, attach_hmm2_shadow
from shadow_ft812 import REG_HSIZE, REG_PCLK, REG_VSIZE


def run_call(name: str) -> None:
    emu = HMM2FullZ80Emulator(ROOT)
    regs = attach_hmm2_shadow(emu)
    emu.call(emu.sym[name], max_steps=4_000_000)
    print(
        f"{name}: fmaddr={emu.fmaddr_enabled} "
        f"pages={[hex(x) for x in emu.mem.pages]} "
        f"hsize={regs._get32(REG_HSIZE)} vsize={regs._get32(REG_VSIZE)} pclk={regs._get32(REG_PCLK)}"
    )


def main() -> int:
    run_call("Init_Video")
    run_call("Platform_Init")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
