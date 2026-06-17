#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


HERE = Path(__file__).resolve().parent
Z80_LIB = HERE / "_z80_lib_cburbridge" / "src"
if Z80_LIB.exists():
    sys.path.insert(0, str(Z80_LIB))

try:
    from z80 import instructions, registers, util  # type: ignore
except Exception as exc:  # pragma: no cover - reported by require_z80().
    instructions = None
    registers = None
    util = None
    Z80_IMPORT_ERROR: Optional[BaseException] = exc
else:
    Z80_IMPORT_ERROR = None


RETURN_MARKER = 0xFFFE
PAGE_SIZE = 0x4000
NUM_PAGES = 256
RAM_G_SIZE = 1024 * 1024
RAM_DL_SIZE = 0x2000
RAM_CMD_SIZE = 0x1000

RAM_DL_BASE = 0x300000
REG_BASE = 0x302000
RAM_CMD_WRITE_BASE = 0x302578
RAM_CMD_BASE = 0x308000

REG_ID = 0x302000
REG_CPURESET = 0x302020
REG_DLSWAP = 0x302054
REG_INT_FLAGS = 0x3020A8
REG_CMD_READ = 0x3020F8
REG_CMD_WRITE = 0x3020FC


def require_z80() -> None:
    if Z80_IMPORT_ERROR is not None:
        raise RuntimeError(
            f"local Z80 core is unavailable: {Z80_IMPORT_ERROR}. "
            f"Expected package under {Z80_LIB}"
        ) from Z80_IMPORT_ERROR


def parse_num(text: str) -> int:
    text = text.strip()
    if text.startswith("#"):
        return int(text[1:], 16)
    if text.lower().startswith("0x"):
        return int(text[2:], 16)
    return int(text, 10)


def parse_sym(path: Path) -> Dict[str, int]:
    syms: Dict[str, int] = {}
    if not path.exists():
        return syms
    rx = re.compile(r"^\s*([\w.]+):\s+EQU\s+([#$0-9A-Fa-fx]+)\s*$")
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = rx.match(line)
            if m:
                syms[m.group(1)] = parse_num(m.group(2))
    return syms


def ini_scalar(ini: Optional[Path], key: str, default: str) -> str:
    if ini is None or not ini.exists():
        return default
    rx = re.compile(rf"^\s*{re.escape(key)}\s*=\s*(.+?)\s*$", re.I)
    with ini.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = rx.match(line)
            if m:
                return m.group(1).strip()
    return default


@dataclass(frozen=True)
class SPGBlock:
    offset: int
    page: int
    rel_path: str


def parse_spg_blocks(ini: Path) -> List[SPGBlock]:
    blocks: List[SPGBlock] = []
    if not ini.exists():
        return blocks
    rx = re.compile(r"^\s*Block\s*=\s*([^,]+),\s*([^,]+),\s*(.+?)\s*$", re.I)
    with ini.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = rx.match(line)
            if not m:
                continue
            blocks.append(
                SPGBlock(
                    offset=parse_num(m.group(1)) & (PAGE_SIZE - 1),
                    page=parse_num(m.group(2)) & 0xFF,
                    rel_path=m.group(3).strip(),
                )
            )
    return blocks


@dataclass
class InputState:
    mouse_x: int = 0
    mouse_y: int = 0
    mouse_buttons: int = 0x03
    kempston: int = 0x00
    keyboard_rows: Dict[int, int] = field(default_factory=dict)
    rtc_seconds_bcd: int = 0x17


@dataclass
class FT812State:
    ram_g: bytearray = field(default_factory=lambda: bytearray(RAM_G_SIZE))
    ram_dl: bytearray = field(default_factory=lambda: bytearray(RAM_DL_SIZE))
    ram_cmd: bytearray = field(default_factory=lambda: bytearray(RAM_CMD_SIZE))
    int_flags: int = 0x01
    dlswap: int = 0
    cmd_write_ptr: int = 0
    cmd_read_ptr: int = 0
    spi_addr: Optional[int] = None
    spi_mode: str = "idle"
    spi_phase: int = 0
    spi_read_dummy: bool = False


@dataclass
class TSConfigDMAState:
    src_l: int = 0
    src_h: int = 0
    src_x: int = 0
    dst_l: int = 0
    dst_h: int = 0
    dst_x: int = 0
    length: int = 0
    number: int = 0
    status: int = 0


class TSConfigMemory:
    def __init__(self, pages: Optional[Iterable[int]] = None) -> None:
        self.physical = bytearray(NUM_PAGES * PAGE_SIZE)
        self.pages = list(pages if pages is not None else (0x00, 0x05, 0x06, 0x04))
        if len(self.pages) != 4:
            raise ValueError("TSConfigMemory needs exactly 4 mapped pages")
        self.pages = [p & 0xFF for p in self.pages]

    def map_addr(self, addr: int) -> int:
        addr &= 0xFFFF
        slot = addr >> 14
        return (self.pages[slot] * PAGE_SIZE) + (addr & (PAGE_SIZE - 1))

    def read(self, addr: int) -> int:
        return self.physical[self.map_addr(addr)]

    def write(self, addr: int, value: int) -> None:
        self.physical[self.map_addr(addr)] = value & 0xFF

    def read_block(self, addr: int, length: int) -> bytes:
        return bytes(self.read(addr + i) for i in range(length))

    def write_block_linear(self, addr: int, data: bytes) -> None:
        for i, b in enumerate(data):
            self.write(addr + i, b)

    def load_page_block(self, page: int, offset: int, data: bytes) -> None:
        start = ((page & 0xFF) * PAGE_SIZE) + (offset & (PAGE_SIZE - 1))
        end = min(start + len(data), len(self.physical))
        self.physical[start:end] = data[: end - start]

    def read_physical(self, page: int, offset: int, length: int) -> bytes:
        start = ((page & 0xFF) * PAGE_SIZE) + (offset & (PAGE_SIZE - 1))
        return bytes(self.physical[start:start + length])

    def write_physical(self, page: int, offset: int, data: bytes) -> None:
        self.load_page_block(page, offset, data)


class TSConfFT812Machine:
    """Project-agnostic Z80 + TS-Config paging/DMA + FT812 memory model.

    The class deliberately knows nothing about game symbols or frame
    routines. A project wrapper supplies root/spgbld/sym paths and then calls
    project code through generic Z80 entry points.
    """

    def __init__(
        self,
        root: Path,
        *,
        spgbld_path: Optional[Path] = None,
        sym_path: Optional[Path] = None,
        trace: bool = False,
        load_spg: bool = False,
        init_cpu: bool = True,
        default_start: str = "0x5C00",
        default_stack: str = "0x7FFF",
        initial_pages: Optional[Iterable[int]] = None,
        fmaddr_requires_enable: bool = True,
    ) -> None:
        self.root = Path(root)
        self.spgbld_path = Path(spgbld_path) if spgbld_path is not None else None
        self.sym = parse_sym(Path(sym_path)) if sym_path is not None else {}
        self.mem = TSConfigMemory(initial_pages)
        self.input = InputState()
        self.ft = FT812State()
        self.dma = TSConfigDMAState()
        self.trace = trace
        self.ports_out: List[Tuple[int, int]] = []
        self.ports_in: List[Tuple[int, int]] = []
        self.errors: List[str] = []
        self.tstates = 0
        self.fmaddr_enabled = False
        self.fmaddr_requires_enable = fmaddr_requires_enable

        if load_spg:
            if self.spgbld_path is None:
                raise ValueError("spgbld_path must be provided when load_spg=True")
            self.load_spg_blocks()

        self.reg = None
        self.ins = None
        if init_cpu:
            require_z80()
            self.reg = registers.Registers()
            with contextlib.redirect_stdout(io.StringIO()):
                self.ins = instructions.InstructionSet(self.reg)
            self.reg.SP = parse_num(ini_scalar(self.spgbld_path, "Stack", default_stack))
            self.reg.PC = parse_num(ini_scalar(self.spgbld_path, "Start", default_start))

    def load_spg_blocks(self) -> None:
        for block in parse_spg_blocks(self.spgbld_path):
            rel = block.rel_path.replace("/", os.sep)
            path = self.root / rel
            if not path.exists():
                self.errors.append(f"missing SPG block file: {block.rel_path}")
                continue
            self.mem.load_page_block(block.page, block.offset, path.read_bytes())

    def get_byte(self, addr: int) -> int:
        return self.mem.read(addr)

    def set_byte(self, addr: int, value: int) -> None:
        self.mem.write(addr, value)

    def cpu_write(self, addr: int, value: int) -> None:
        self._write_ref(addr & 0xFFFF, value)

    def get_word(self, addr: int) -> int:
        return self.get_byte(addr) | (self.get_byte(addr + 1) << 8)

    def set_word(self, addr: int, value: int) -> None:
        self.set_byte(addr, value)
        self.set_byte(addr + 1, value >> 8)

    def get_memory(self, addr: int, length: int) -> bytes:
        return self.mem.read_block(addr, length)

    def step(self) -> int:
        if self.reg is None or self.ins is None:
            raise RuntimeError("CPU was not initialized")
        pc0 = self.reg.PC
        ins, args = False, ()
        try:
            while not ins:
                op = self.mem.read(self.reg.PC)
                ins, args = self.ins << op
                self.reg.PC = util.inc16(self.reg.PC)
        except Exception as exc:
            raise RuntimeError(f"Z80 decode failed at PC=#{pc0:04X}: {exc}") from exc

        reads = ins.get_read_list(args)
        data = [self._read_ref(ref) for ref in reads]
        writes = ins.execute(data, args)
        for ref, value in writes:
            self._write_ref(ref, value)
        self.tstates += getattr(ins, "tstates", 0)
        if self.trace:
            print(f"{pc0:04X}: {ins.assembler(args)}")
        return getattr(ins, "tstates", 0)

    def run_until_pc(self, pc: int, max_steps: int = 2_000_000) -> int:
        if self.reg is None:
            raise RuntimeError("CPU was not initialized")
        steps = 0
        while self.reg.PC != pc:
            if steps >= max_steps:
                raise TimeoutError(f"timeout at PC=#{self.reg.PC:04X}, target=#{pc:04X}")
            op = self.mem.read(self.reg.PC)
            if op == 0x76:
                self.reg.PC = (self.reg.PC + 1) & 0xFFFF
            else:
                self.step()
            steps += 1
        return steps

    def call(
        self,
        addr: int,
        *,
        a: Optional[int] = None,
        b: Optional[int] = None,
        c: Optional[int] = None,
        d: Optional[int] = None,
        e: Optional[int] = None,
        h: Optional[int] = None,
        l: Optional[int] = None,
        max_steps: int = 2_000_000,
    ) -> int:
        if self.reg is None:
            raise RuntimeError("CPU was not initialized")
        if a is not None:
            self.reg.A = a & 0xFF
        if b is not None:
            self.reg.B = b & 0xFF
        if c is not None:
            self.reg.C = c & 0xFF
        if d is not None:
            self.reg.D = d & 0xFF
        if e is not None:
            self.reg.E = e & 0xFF
        if h is not None:
            self.reg.H = h & 0xFF
        if l is not None:
            self.reg.L = l & 0xFF
        sp = (self.reg.SP - 2) & 0xFFFF
        self.set_word(sp, RETURN_MARKER)
        self.reg.SP = sp
        self.reg.PC = addr & 0xFFFF
        return self.run_until_pc(RETURN_MARKER, max_steps=max_steps)

    def _read_ref(self, ref: int) -> int:
        if ref >= 0x10000:
            value = self.in_port(ref & 0xFFFF)
            self.ports_in.append((ref & 0xFFFF, value))
            return value
        return self.mem.read(ref)

    def _write_ref(self, ref: int, value: int) -> None:
        value &= 0xFF
        if ref >= 0x10000:
            self.out_port(ref & 0xFFFF, value)
            self.ports_out.append((ref & 0xFFFF, value))
            return
        if 0x0410 <= ref <= 0x0413 and (self.fmaddr_enabled or not self.fmaddr_requires_enable):
            self.mem.pages[ref - 0x0410] = value
        self.mem.write(ref, value)

    def in_port(self, port: int) -> int:
        low = port & 0xFF
        high = (port >> 8) & 0xFF
        if low == 0xAF:
            if high == 0x27:
                return self.dma.status & 0xFF
            return 0x07 if high == 0x00 else 0x00
        if low == 0x57:
            return self._read_ft_spi()
        if port == 0xBFF7:
            return self.input.rtc_seconds_bcd & 0xFF
        if low == 0x1F:
            return self.input.kempston & 0xFF
        if port == 0xFADF:
            return self.input.mouse_buttons & 0xFF
        if port == 0xFBDF:
            return self.input.mouse_x & 0xFF
        if port == 0xFFDF:
            return self.input.mouse_y & 0xFF
        if low == 0xFE:
            return self.input.keyboard_rows.get(high, 0xFF)
        return 0xFF

    def out_port(self, port: int, value: int) -> None:
        low = port & 0xFF
        high = (port >> 8) & 0xFF
        value &= 0xFF
        if low == 0xAF:
            self._write_tsconf_register(high, value)
        elif low in (0x57, 0x77):
            self._write_ft_spi(low, value)

    def _write_tsconf_register(self, reg: int, value: int) -> None:
        value &= 0xFF
        if reg == 0x15:
            self.fmaddr_enabled = bool(value & 0x10)
            return
        if 0x10 <= reg <= 0x13:
            slot = reg - 0x10
            self.mem.pages[slot] = value
            self.mem.write(0x0410 + slot, value)
            return
        if reg == 0x1A:
            self.dma.src_l = value
        elif reg == 0x1B:
            self.dma.src_h = value
        elif reg == 0x1C:
            self.dma.src_x = value
        elif reg == 0x1D:
            self.dma.dst_l = value
        elif reg == 0x1E:
            self.dma.dst_h = value
        elif reg == 0x1F:
            self.dma.dst_x = value
        elif reg == 0x26:
            self.dma.length = value
        elif reg == 0x28:
            self.dma.number = value
        elif reg == 0x27:
            self._start_dma(value)

    def _start_dma(self, mode: int) -> None:
        self.dma.status = 0x80
        if mode == 0x82:
            self._dma_ram_spi()
        else:
            self.errors.append(f"unsupported DMA mode #{mode:02X}")
        self.dma.status = 0

    def _dma_ram_spi(self) -> None:
        if self.ft.spi_mode != "write" or self.ft.spi_phase < 3 or self.ft.spi_addr is None:
            self.errors.append("DMA_RAM_SPI started without active FT812 SPI write transaction")
            return
        src_off = ((self.dma.src_h << 8) | self.dma.src_l) & (PAGE_SIZE - 1)
        src = ((self.dma.src_x & 0xFF) * PAGE_SIZE) + src_off
        words = (self.dma.number + 1) * (self.dma.length + 1)
        byte_count = words * 2
        end = min(src + byte_count, len(self.mem.physical))
        if end - src != byte_count:
            self.errors.append(f"DMA_RAM_SPI source overflow src=#{src:06X} bytes={byte_count}")
        for value in self.mem.physical[src:end]:
            addr = self.ft.spi_addr & 0x3FFFFF
            self._write_ft_addr(addr, value)
            self.ft.spi_addr = (addr + 1) & 0x3FFFFF
        self._advance_dma_source(src + (end - src))

    def _advance_dma_source(self, absolute_src: int) -> None:
        self.dma.src_x = (absolute_src // PAGE_SIZE) & 0xFF
        src_off = absolute_src & (PAGE_SIZE - 1)
        self.dma.src_l = src_off & 0xFF
        self.dma.src_h = (src_off >> 8) & 0xFF

    def _write_ft_spi(self, low_port: int, value: int) -> None:
        value &= 0xFF
        if low_port == 0x77:
            self.ft.spi_phase = 0
            self.ft.spi_addr = 0
            self.ft.spi_mode = "idle"
            self.ft.spi_read_dummy = False
            return
        if self.ft.spi_addr is None:
            self.ft.spi_addr = 0
        if self.ft.spi_phase == 0:
            self.ft.spi_mode = "write" if value & 0x80 else "read"
            self.ft.spi_addr = value & 0x3F
            self.ft.spi_phase += 1
            return
        if self.ft.spi_phase < 3:
            self.ft.spi_addr = ((self.ft.spi_addr << 8) | value) & 0x3FFFFF
            self.ft.spi_phase += 1
            if self.ft.spi_phase == 3 and self.ft.spi_mode == "read":
                self.ft.spi_read_dummy = True
            return
        if self.ft.spi_mode != "write":
            return
        addr = self.ft.spi_addr & 0x3FFFFF
        self._write_ft_addr(addr, value)
        self.ft.spi_addr = (addr + 1) & 0x3FFFFF

    def _read_ft_spi(self) -> int:
        if self.ft.spi_phase < 3 or self.ft.spi_addr is None:
            return 0
        if self.ft.spi_read_dummy:
            self.ft.spi_read_dummy = False
            return 0
        addr = self.ft.spi_addr & 0x3FFFFF
        value = self._read_ft_addr(addr)
        self.ft.spi_addr = (addr + 1) & 0x3FFFFF
        return value

    def _read_ft_addr(self, addr: int) -> int:
        addr &= 0x3FFFFF
        if addr == REG_ID:
            return 0x7C
        if addr == REG_CPURESET:
            return 0
        if addr in (0x302574, 0x302575):
            return 0xFF
        if addr in (0x302576, 0x302577):
            return 0x0F if addr == 0x302577 else 0xFC
        if addr == REG_CMD_READ:
            return self.ft.cmd_read_ptr & 0xFF
        if addr == REG_CMD_READ + 1:
            return (self.ft.cmd_read_ptr >> 8) & 0xFF
        if addr == REG_CMD_WRITE:
            return self.ft.cmd_write_ptr & 0xFF
        if addr == REG_CMD_WRITE + 1:
            return (self.ft.cmd_write_ptr >> 8) & 0xFF
        if addr == REG_DLSWAP:
            return self.ft.dlswap & 0xFF
        if addr == REG_INT_FLAGS:
            value = self.ft.int_flags & 0xFF
            self.ft.int_flags = 0
            return value
        if 0x000000 <= addr < RAM_DL_BASE:
            return self.ft.ram_g[addr & (RAM_G_SIZE - 1)]
        if RAM_DL_BASE <= addr < RAM_DL_BASE + RAM_DL_SIZE:
            return self.ft.ram_dl[addr - RAM_DL_BASE]
        if RAM_CMD_BASE <= addr < RAM_CMD_BASE + RAM_CMD_SIZE:
            return self.ft.ram_cmd[addr - RAM_CMD_BASE]
        return 0

    def _write_ft_addr(self, addr: int, value: int) -> None:
        addr &= 0x3FFFFF
        value &= 0xFF
        if addr == REG_DLSWAP:
            self.ft.dlswap = 0
            if value:
                self.ft.int_flags |= 0x01
            return
        if addr == REG_INT_FLAGS:
            self.ft.int_flags &= ~value
            return
        if 0x000000 <= addr < RAM_DL_BASE:
            self.ft.ram_g[addr & (RAM_G_SIZE - 1)] = value
        elif RAM_DL_BASE <= addr < RAM_DL_BASE + RAM_DL_SIZE:
            self.ft.ram_dl[addr - RAM_DL_BASE] = value
        elif RAM_CMD_WRITE_BASE <= addr < RAM_CMD_WRITE_BASE + RAM_CMD_SIZE:
            off = self.ft.cmd_write_ptr & (RAM_CMD_SIZE - 1)
            self.ft.ram_cmd[off] = value
            self.ft.cmd_write_ptr = (off + 1) & (RAM_CMD_SIZE - 1)
            self._process_cmd_fifo()
        elif RAM_CMD_BASE <= addr < RAM_CMD_BASE + RAM_CMD_SIZE:
            off = addr - RAM_CMD_BASE
            self.ft.ram_cmd[off] = value
            self.ft.cmd_write_ptr = (off + 1) & (RAM_CMD_SIZE - 1)

    def _process_cmd_fifo(self) -> None:
        read = self.ft.cmd_read_ptr & (RAM_CMD_SIZE - 1)
        write = self.ft.cmd_write_ptr & (RAM_CMD_SIZE - 1)
        available = (write - read) & (RAM_CMD_SIZE - 1)
        if available < 4:
            return

        def cmd_bytes(pos: int, size: int) -> bytes:
            return bytes(self.ft.ram_cmd[(pos + i) & (RAM_CMD_SIZE - 1)] for i in range(size))

        def cmd_word(pos: int) -> int:
            return int.from_bytes(cmd_bytes(pos, 4), "little")

        # This simulator executes DLSTART command streams. Unknown co-processor
        # commands are drained so project wait loops cannot hang forever.
        if cmd_bytes(read, 4) != b"\x00\xff\xff\xff":
            self.ft.cmd_read_ptr = write
            return
        if available & 3:
            return
        if cmd_word((write - 4) & (RAM_CMD_SIZE - 1)) not in (0x00000000, 0xFFFFFF01):
            return

        dl_ptr = 0
        pos = (read + 4) & (RAM_CMD_SIZE - 1)
        remaining = available - 4
        while remaining >= 4:
            word = cmd_word(pos)
            pos = (pos + 4) & (RAM_CMD_SIZE - 1)
            remaining -= 4
            if word == 0x00000000:
                if dl_ptr + 4 <= len(self.ft.ram_dl):
                    self.ft.ram_dl[dl_ptr:dl_ptr + 4] = word.to_bytes(4, "little")
                self.ft.int_flags |= 0x01
                self.ft.cmd_read_ptr = pos
                return
            if word == 0xFFFFFF01:
                self.ft.int_flags |= 0x01
                self.ft.cmd_read_ptr = pos
                return
            if word == 0xFFFFFF1E and remaining >= 8:
                src = cmd_word(pos) & 0x3FFFFF
                size = cmd_word((pos + 4) & (RAM_CMD_SIZE - 1))
                pos = (pos + 8) & (RAM_CMD_SIZE - 1)
                remaining -= 8
                if src < RAM_DL_BASE and size > 0:
                    size = min(size, RAM_G_SIZE - (src & (RAM_G_SIZE - 1)), len(self.ft.ram_dl) - dl_ptr)
                    if size > 0:
                        real_src = src & (RAM_G_SIZE - 1)
                        self.ft.ram_dl[dl_ptr:dl_ptr + size] = self.ft.ram_g[real_src:real_src + size]
                        dl_ptr += size
                continue
            if dl_ptr + 4 <= len(self.ft.ram_dl):
                self.ft.ram_dl[dl_ptr:dl_ptr + 4] = word.to_bytes(4, "little")
                dl_ptr += 4
