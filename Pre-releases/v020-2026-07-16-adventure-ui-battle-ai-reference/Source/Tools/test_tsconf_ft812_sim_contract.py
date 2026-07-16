#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from tsconf_ft812_sim import (
    PAGE_SIZE,
    RAM_CMD_WRITE_BASE,
    REG_ID,
    TSConfFT812Machine,
)
from shadow_ft812 import FT812Registers, FT812VideoTiming, REG_HSIZE, REG_VSIZE


def make_machine(tmp: Path | None = None, *, load_spg: bool = False) -> TSConfFT812Machine:
    root = tmp if tmp is not None else Path(".")
    spgbld = root / "sim_image.ini"
    return TSConfFT812Machine(root, spgbld_path=spgbld, load_spg=load_spg, init_cpu=False)


def ft_spi_addr(machine: TSConfFT812Machine, addr: int, *, write: bool) -> None:
    machine.out_port(0x0077, 0)
    machine.out_port(0x0057, ((addr >> 16) & 0x3F) | (0x80 if write else 0x00))
    machine.out_port(0x0057, (addr >> 8) & 0xFF)
    machine.out_port(0x0057, addr & 0xFF)


def out_ts(machine: TSConfFT812Machine, reg: int, value: int) -> None:
    machine.out_port(((reg & 0xFF) << 8) | 0xAF, value)


def test_spg_blocks_cross_page() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "payload.bin").write_bytes(b"ABCDEF")
        (root / "sim_image.ini").write_text(
            "Start = 0x5000\n"
            "Stack = 0xBFFF\n"
            "Block = #3FFE, #20, payload.bin\n",
            encoding="utf-8",
        )
        machine = make_machine(root, load_spg=True)
        base = 0x20 * PAGE_SIZE
        assert machine.mem.physical[base + 0x3FFE:base + 0x4004] == b"ABCDEF"


def test_page_mapping_and_fmaddr_gate() -> None:
    machine = make_machine()
    machine.mem.write_physical(0x33, 0x0000, b"\xA5")

    out_ts(machine, 0x11, 0x33)
    assert machine.mem.pages[1] == 0x33
    assert machine.get_byte(0x4000) == 0xA5

    machine.cpu_write(0x0413, 0x44)
    assert machine.mem.pages[3] != 0x44
    out_ts(machine, 0x15, 0x10)
    machine.cpu_write(0x0413, 0x44)
    assert machine.mem.pages[3] == 0x44


def test_ft812_spi_write_and_read() -> None:
    machine = make_machine()
    ft_spi_addr(machine, 0x001234, write=True)
    for value in b"TS":
        machine.out_port(0x0057, value)
    assert machine.ft.ram_g[0x1234:0x1236] == b"TS"

    ft_spi_addr(machine, REG_ID, write=False)
    assert machine.in_port(0x0057) == 0x00
    assert machine.in_port(0x0057) == 0x7C


def test_dma_ram_spi_writes_ft812_ram_g_and_advances_source() -> None:
    machine = make_machine()
    machine.mem.write_physical(0x22, 0x1234, bytes(range(8)))
    ft_spi_addr(machine, 0x004000, write=True)

    out_ts(machine, 0x1A, 0x34)
    out_ts(machine, 0x1B, 0x12)
    out_ts(machine, 0x1C, 0x22)
    out_ts(machine, 0x26, 0x03)
    out_ts(machine, 0x28, 0x00)
    out_ts(machine, 0x27, 0x82)

    assert machine.ft.ram_g[0x4000:0x4008] == bytes(range(8))
    assert (machine.dma.src_x, machine.dma.src_h, machine.dma.src_l) == (0x22, 0x12, 0x3C)
    assert machine.errors == []


def test_cmd_append_builds_ram_dl_without_project_code() -> None:
    machine = make_machine()
    dl_bytes = b"\x11\x22\x33\x44\x55\x66\x77\x88"
    machine.ft.ram_g[0x0200:0x0208] = dl_bytes
    words = [
        0xFFFFFF00,  # CMD_DLSTART
        0xFFFFFF1E,  # CMD_APPEND
        0x00000200,
        len(dl_bytes),
        0x00000000,  # DISPLAY
    ]
    stream = b"".join(word.to_bytes(4, "little") for word in words)
    for i, value in enumerate(stream):
        machine._write_ft_addr(RAM_CMD_WRITE_BASE + i, value)

    assert machine.ft.ram_dl[: len(dl_bytes)] == dl_bytes
    assert machine.ft.ram_dl[len(dl_bytes):len(dl_bytes) + 4] == b"\x00\x00\x00\x00"
    assert machine.ft.cmd_read_ptr == len(stream)
    assert machine.ft.int_flags & 0x01


def test_z80_call_preserves_registers_unless_explicit() -> None:
    machine = TSConfFT812Machine(Path("."), load_spg=False, init_cpu=True)
    machine.mem.write_physical(0x05, 0x1000, b"\xC9")  # RET at #5000.

    machine.reg.A = 0x12
    machine.reg.B = 0x56
    machine.call(0x5000)
    assert machine.reg.A == 0x12
    assert machine.reg.B == 0x56

    machine.call(0x5000, a=0x34)
    assert machine.reg.A == 0x34
    assert machine.reg.B == 0x56


def test_ft812_shadow_has_no_project_video_default() -> None:
    regs = FT812Registers()
    assert regs._get32(REG_HSIZE) == 0
    assert regs._get32(REG_VSIZE) == 0

    regs = FT812Registers(FT812VideoTiming(hsize=321, vsize=123))
    assert regs._get32(REG_HSIZE) == 321
    assert regs._get32(REG_VSIZE) == 123


def main() -> int:
    tests = [
        test_spg_blocks_cross_page,
        test_page_mapping_and_fmaddr_gate,
        test_ft812_spi_write_and_read,
        test_dma_ram_spi_writes_ft812_ram_g_and_advances_source,
        test_cmd_append_builds_ram_dl_without_project_code,
        test_z80_call_preserves_registers_unless_explicit,
        test_ft812_shadow_has_no_project_video_default,
    ]
    for test in tests:
        test()
        print(f"ok {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
