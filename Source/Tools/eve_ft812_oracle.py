#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, attach_hmm2_shadow  # noqa: E402
from shadow_ft812 import RAM_DL_SIZE, RAM_G_SIZE  # noqa: E402


BT8XXEMU_VERSION_API = 12
BT8XXEMU_EMULATOR_FT812 = 0x0812

BT8XXEMU_FRAME_BUFFER_COMPLETE = 0x02
BT8XXEMU_FRAME_CHANGED = 0x04
BT8XXEMU_FRAME_SWAP = 0x08

BT8XXEMU_ENABLE_DYNAMIC_DEGRADE = 0x40
BT8XXEMU_ENABLE_REG_PWM_DUTY_EMULATION = 0x100
BT8XXEMU_ENABLE_BACKGROUND_PERFORMANCE = 0x800

RAM_DL_BASE = 0x300000
REG_BASE = 0x302000

REG_HCYCLE = 0x30202C
REG_HOFFSET = 0x302030
REG_HSIZE = 0x302034
REG_HSYNC0 = 0x302038
REG_HSYNC1 = 0x30203C
REG_VCYCLE = 0x302040
REG_VOFFSET = 0x302044
REG_VSIZE = 0x302048
REG_VSYNC0 = 0x30204C
REG_VSYNC1 = 0x302050
REG_DLSWAP = 0x302054
REG_OUTBITS = 0x30205C
REG_DITHER = 0x302060
REG_SWIZZLE = 0x302064
REG_CSPREAD = 0x302068
REG_PCLK_POL = 0x30206C
REG_PCLK = 0x302070
REG_GPIOX_DIR = 0x302098
REG_GPIOX = 0x30209C
REG_INT_EN = 0x3020AC
REG_INT_MASK = 0x3020B0
REG_PWM_DUTY = 0x3020D4
REG_CMD_READ = 0x3020F8
REG_CMD_WRITE = 0x3020FC
REG_CMDB_SPACE = 0x302574

DLSWAP_FRAME = 2

FT_CMD_ACTIVE = 0x00
FT_CMD_SLEEP = 0x42
FT_CMD_PWRDOWN_ = 0x50
FT_CMD_CLKEXT = 0x44
FT_CMD_CLKSEL = 0x61
FT_CMD_RST_PULSE = 0x68

GRAPHICS_CB = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_int,
)


class EmulatorParameters(ctypes.Structure):
    _fields_ = [
        ("Main", ctypes.c_void_p),
        ("Flags", ctypes.c_int),
        ("Mode", ctypes.c_int),
        ("MousePressure", ctypes.c_uint32),
        ("ExternalFrequency", ctypes.c_uint32),
        ("ReduceGraphicsThreads", ctypes.c_uint32),
        ("MCUSleep", ctypes.c_void_p),
        ("RomFilePath", ctypes.c_wchar * 260),
        ("OtpFilePath", ctypes.c_wchar * 260),
        ("CoprocessorRomFilePath", ctypes.c_wchar * 260),
        ("Graphics", ctypes.c_void_p),
        ("Log", ctypes.c_void_p),
        ("Close", ctypes.c_void_p),
        ("UserContext", ctypes.c_void_p),
        ("Flash", ctypes.c_void_p),
    ]


@dataclass
class EveFrame:
    width: int
    height: int
    flags: int
    argb: bytes


@dataclass
class CapturedEveFrame:
    serial: int
    swap_serial: int
    timestamp: float
    frame: EveFrame


@dataclass
class HMM2FrameState:
    viewport_x: int
    ram_g: bytes
    ram_dl: bytes
    regs: bytes


class EveFT812Oracle:
    def __init__(self, eve_bin: Path | None = None) -> None:
        if eve_bin is None:
            eve_bin = ROOT.parent / "EveApps" / "common" / "eve_hal" / "Bin" / "Simulation" / "x64"
        self.eve_bin = Path(eve_bin)
        if not (self.eve_bin / "bt8xxemu.dll").exists():
            raise FileNotFoundError(f"bt8xxemu.dll not found in {self.eve_bin}")
        os.add_dll_directory(str(self.eve_bin))
        self.lib = ctypes.CDLL(str(self.eve_bin / "bt8xxemu.dll"))
        self._bind_api()
        self._graphics_cb = GRAPHICS_CB(self._on_graphics)
        self._params = EmulatorParameters()
        self._emu = ctypes.c_void_p()
        self._last_frame: EveFrame | None = None
        self._complete_serial = 0
        self._swap_serial = 0
        self._prev_ram_g: bytes | None = None
        self._capture_enabled = False
        self._capture_limit = 80
        self.captured_frames: list[CapturedEveFrame] = []

    def _bind_api(self) -> None:
        self.lib.BT8XXEMU_version.argtypes = []
        self.lib.BT8XXEMU_version.restype = ctypes.c_char_p
        self.lib.BT8XXEMU_defaults.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(EmulatorParameters),
            ctypes.c_int,
        ]
        self.lib.BT8XXEMU_defaults.restype = None
        self.lib.BT8XXEMU_run.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(EmulatorParameters),
        ]
        self.lib.BT8XXEMU_run.restype = None
        self.lib.BT8XXEMU_stop.argtypes = [ctypes.c_void_p]
        self.lib.BT8XXEMU_stop.restype = None
        self.lib.BT8XXEMU_destroy.argtypes = [ctypes.c_void_p]
        self.lib.BT8XXEMU_destroy.restype = None
        self.lib.BT8XXEMU_isRunning.argtypes = [ctypes.c_void_p]
        self.lib.BT8XXEMU_isRunning.restype = ctypes.c_int
        self.lib.BT8XXEMU_transfer.argtypes = [ctypes.c_void_p, ctypes.c_uint8]
        self.lib.BT8XXEMU_transfer.restype = ctypes.c_uint8
        self.lib.BT8XXEMU_chipSelect.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.lib.BT8XXEMU_chipSelect.restype = None

    def __enter__(self) -> "EveFT812Oracle":
        self.lib.BT8XXEMU_defaults(
            BT8XXEMU_VERSION_API,
            ctypes.byref(self._params),
            BT8XXEMU_EMULATOR_FT812,
        )
        self._params.Flags &= ~BT8XXEMU_ENABLE_DYNAMIC_DEGRADE
        self._params.Flags &= ~BT8XXEMU_ENABLE_REG_PWM_DUTY_EMULATION
        self._params.Flags |= BT8XXEMU_ENABLE_BACKGROUND_PERFORMANCE
        self._params.Graphics = ctypes.cast(self._graphics_cb, ctypes.c_void_p).value
        self.lib.BT8XXEMU_run(BT8XXEMU_VERSION_API, ctypes.byref(self._emu), ctypes.byref(self._params))
        if not self._emu.value:
            raise RuntimeError("BT8XXEMU_run returned NULL emulator")
        self.boot()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._emu.value:
            self.lib.BT8XXEMU_stop(self._emu)
            self.lib.BT8XXEMU_destroy(self._emu)
            self._emu = ctypes.c_void_p()

    def _on_graphics(
        self,
        sender: int,
        context: int,
        output: int,
        buffer: ctypes.POINTER(ctypes.c_uint32),
        hsize: int,
        vsize: int,
        flags: int,
    ) -> int:
        del sender, context
        if output and buffer and (flags & BT8XXEMU_FRAME_BUFFER_COMPLETE):
            nbytes = int(hsize) * int(vsize) * 4
            self._last_frame = EveFrame(int(hsize), int(vsize), int(flags), ctypes.string_at(buffer, nbytes))
            self._complete_serial += 1
            if flags & BT8XXEMU_FRAME_SWAP:
                self._swap_serial += 1
            if self._capture_enabled and len(self.captured_frames) < self._capture_limit:
                if not self.captured_frames or self.captured_frames[-1].frame.argb != self._last_frame.argb:
                    self.captured_frames.append(
                        CapturedEveFrame(
                            serial=self._complete_serial,
                            swap_serial=self._swap_serial,
                            timestamp=time.monotonic(),
                            frame=self._last_frame,
                        )
                    )
        return 1

    @property
    def version(self) -> str:
        raw = self.lib.BT8XXEMU_version()
        return raw.decode("ascii", errors="replace") if raw else "unknown"

    def cs(self, value: int) -> None:
        self.lib.BT8XXEMU_chipSelect(self._emu, int(value))

    def transfer(self, value: int) -> int:
        return int(self.lib.BT8XXEMU_transfer(self._emu, value & 0xFF))

    def host_command(self, command: int, param: int = 0) -> None:
        self.cs(1)
        self.transfer(command)
        self.transfer(param)
        self.transfer(0)
        self.cs(0)

    def write(self, addr: int, data: bytes | bytearray | memoryview) -> None:
        self.cs(1)
        self.transfer(((addr >> 16) & 0xFF) | 0x80)
        self.transfer((addr >> 8) & 0xFF)
        self.transfer(addr & 0xFF)
        for value in data:
            self.transfer(int(value))
        self.cs(0)

    def write8(self, addr: int, value: int) -> None:
        self.write(addr, bytes((value & 0xFF,)))

    def write16(self, addr: int, value: int) -> None:
        self.write(addr, int(value & 0xFFFF).to_bytes(2, "little"))

    def read(self, addr: int, size: int) -> bytes:
        self.cs(1)
        self.transfer((addr >> 16) & 0xFF)
        self.transfer((addr >> 8) & 0xFF)
        self.transfer(addr & 0xFF)
        self.transfer(0)
        out = bytearray()
        for _ in range(size):
            out.append(self.transfer(0))
        self.cs(0)
        return bytes(out)

    def read8(self, addr: int) -> int:
        return self.read(addr, 1)[0]

    def boot(self) -> None:
        self.host_command(FT_CMD_PWRDOWN_)
        time.sleep(0.003)
        self.host_command(FT_CMD_CLKEXT)
        time.sleep(0.003)
        self.host_command(FT_CMD_CLKSEL, 0xC0)
        self.host_command(FT_CMD_ACTIVE)
        time.sleep(0.015)
        self.wait_reg_id()

        self.host_command(FT_CMD_RST_PULSE)
        time.sleep(0.018)
        self.host_command(FT_CMD_CLKEXT)
        time.sleep(0.006)
        self.host_command(FT_CMD_SLEEP)
        time.sleep(0.006)
        self.host_command(FT_CMD_CLKSEL, 0xC8)
        self.host_command(FT_CMD_ACTIVE)
        self.host_command(FT_CMD_ACTIVE)
        time.sleep(0.006)
        self.wait_reg_id()

    def wait_reg_id(self) -> None:
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if self.read8(REG_BASE) == 0x7C:
                return
            time.sleep(0.005)
        raise TimeoutError("FT812 REG_ID did not become 0x7C")

    def write_hmm2_regs(self, regs: bytes) -> None:
        for addr in (
            REG_PCLK_POL,
            REG_SWIZZLE,
            REG_CSPREAD,
            REG_DITHER,
            REG_OUTBITS,
            REG_HSYNC0,
            REG_HSYNC1,
            REG_HOFFSET,
            REG_HSIZE,
            REG_HCYCLE,
            REG_VSYNC0,
            REG_VSYNC1,
            REG_VOFFSET,
            REG_VSIZE,
            REG_VCYCLE,
            REG_GPIOX_DIR,
            REG_GPIOX,
            REG_INT_MASK,
            REG_INT_EN,
            REG_PWM_DUTY,
            REG_PCLK,
        ):
            off = addr - REG_BASE
            self.write(addr, regs[off : off + 4])

    def write_probe_regs_1024(self) -> None:
        self.write8(REG_PCLK, 0)
        self.write8(REG_PCLK_POL, 0)
        self.write8(REG_SWIZZLE, 0)
        self.write16(REG_CSPREAD, 0)
        self.write16(REG_DITHER, 1)
        self.write16(REG_OUTBITS, 0)
        self.write16(REG_HSYNC0, 24)
        self.write16(REG_HSYNC1, 160)
        self.write16(REG_HOFFSET, 320)
        self.write16(REG_HSIZE, 1024)
        self.write16(REG_HCYCLE, 1344)
        self.write16(REG_VSYNC0, 2)
        self.write16(REG_VSYNC1, 8)
        self.write16(REG_VOFFSET, 37)
        self.write16(REG_VSIZE, 768)
        self.write16(REG_VCYCLE, 806)
        self.write16(REG_GPIOX_DIR, 0xFFFF)
        self.write16(REG_GPIOX, 0xFFFF)
        self.write8(REG_PCLK, 2)

    def upload_ram_g(self, ram_g: bytes, page_size: int = 4096) -> tuple[int, int]:
        if len(ram_g) != RAM_G_SIZE:
            raise ValueError(f"RAM_G snapshot size must be {RAM_G_SIZE}, got {len(ram_g)}")
        pages = 0
        bytes_written = 0
        previous = self._prev_ram_g
        for offset in range(0, RAM_G_SIZE, page_size):
            chunk = ram_g[offset : offset + page_size]
            if previous is None:
                changed = any(chunk)
            else:
                changed = chunk != previous[offset : offset + page_size]
            if changed:
                self.write(offset, chunk)
                pages += 1
                bytes_written += len(chunk)
        self._prev_ram_g = bytes(ram_g)
        return pages, bytes_written

    def upload_frame_state(self, state: HMM2FrameState, out_png: Path) -> EveFrame:
        self.write8(REG_PCLK, 0)
        self.write_hmm2_regs(state.regs)
        pages, bytes_written = self.upload_ram_g(state.ram_g)
        self.write(RAM_DL_BASE, state.ram_dl)
        before_swap = self._swap_serial
        before_complete = self._complete_serial
        self.write8(REG_DLSWAP, DLSWAP_FRAME)
        frame = self.wait_frame(before_swap, before_complete)
        save_argb_png(frame, out_png)
        print(
            f"EVE frame x={state.viewport_x}: {frame.width}x{frame.height} "
            f"flags=0x{frame.flags:02X} ramg_pages={pages} ramg_bytes={bytes_written} png={out_png}"
        )
        return frame

    def render_probe(self, out_png: Path) -> EveFrame:
        self.write_probe_regs_1024()
        dl = bytearray()
        for word in (0x02002050, 0x26000007, 0x00000000):
            dl.extend(word.to_bytes(4, "little"))
        self.write(RAM_DL_BASE, dl)
        before_swap = self._swap_serial
        before_complete = self._complete_serial
        self.write8(REG_DLSWAP, DLSWAP_FRAME)
        frame = self.wait_frame(before_swap, before_complete)
        save_argb_png(frame, out_png)
        return frame

    def wait_frame(
        self,
        before_swap: int,
        before_complete: int,
        timeout: float = 5.0,
        *,
        require_swap: bool = False,
    ) -> EveFrame:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            frame = self._last_frame
            if frame is not None and self._swap_serial > before_swap:
                return frame
            if require_swap:
                time.sleep(0.005)
                continue
            if frame is not None and self._complete_serial > before_complete and (
                frame.flags & (BT8XXEMU_FRAME_SWAP | BT8XXEMU_FRAME_CHANGED)
            ):
                return frame
            time.sleep(0.005)
        raise TimeoutError(
            f"Timed out waiting for EVE frame; complete={self._complete_serial}, swap={self._swap_serial}"
        )

    def begin_capture(self, limit: int = 80) -> None:
        self._capture_limit = limit
        self.captured_frames.clear()
        self._capture_enabled = True

    def end_capture(self) -> list[CapturedEveFrame]:
        self._capture_enabled = False
        return list(self.captured_frames)


class EveSPIMirror:
    """Mirror TS-Config FT812 SPI traffic from the Z80 simulator into bt8xxemu."""

    def __init__(self, emu: HMM2FullZ80Emulator, oracle: EveFT812Oracle) -> None:
        self.emu = emu
        self.oracle = oracle
        self._orig_out_port = emu.out_port
        self._orig_in_port = emu.in_port
        self._orig_dma_ram_spi = emu._dma_ram_spi
        self.spi_out_bytes = 0
        self.spi_in_bytes = 0
        self.dma_bytes = 0
        self.cs_on = 0
        self.cs_off = 0

    def __enter__(self) -> "EveSPIMirror":
        emu = self.emu
        oracle = self.oracle

        def mirrored_out_port(port: int, value: int) -> None:
            low = port & 0xFF
            value &= 0xFF
            if low == 0x77:
                if value & 0x04:
                    oracle.cs(1)
                    self.cs_on += 1
                else:
                    oracle.cs(0)
                    self.cs_off += 1
            elif low == 0x57:
                oracle.transfer(value)
                self.spi_out_bytes += 1
            self._orig_out_port(port, value)

        def mirrored_in_port(port: int) -> int:
            value = self._orig_in_port(port)
            if (port & 0xFF) == 0x57:
                oracle.transfer(0)
                self.spi_in_bytes += 1
            return value

        def mirrored_dma_ram_spi() -> None:
            data = b""
            if emu.ft.spi_mode == "write" and emu.ft.spi_phase >= 3 and emu.ft.spi_addr is not None:
                src_off = ((emu.dma.src_h << 8) | emu.dma.src_l) & 0x3FFF
                src = ((emu.dma.src_x & 0xFF) * 0x4000) + src_off
                byte_count = (emu.dma.number + 1) * (emu.dma.length + 1) * 2
                end = min(src + byte_count, len(emu.mem.physical))
                data = bytes(emu.mem.physical[src:end])
            self._orig_dma_ram_spi()
            for b in data:
                oracle.transfer(b)
            self.dma_bytes += len(data)

        emu.out_port = mirrored_out_port
        emu.in_port = mirrored_in_port
        emu._dma_ram_spi = mirrored_dma_ram_spi
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.emu.out_port = self._orig_out_port
        self.emu.in_port = self._orig_in_port
        self.emu._dma_ram_spi = self._orig_dma_ram_spi


def save_argb_png(frame: EveFrame, out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    img = Image.frombuffer("RGBA", (frame.width, frame.height), frame.argb, "raw", "BGRA", 0, 1)
    img.convert("RGB").save(out_png)


def image_from_frame(frame: EveFrame) -> Image.Image:
    return Image.frombuffer("RGBA", (frame.width, frame.height), frame.argb, "raw", "BGRA", 0, 1).convert("RGB")


def diff_summary(a: EveFrame, b: EveFrame, box: tuple[int, int, int, int]) -> tuple[tuple[int, int, int, int] | None, int]:
    from PIL import ImageChops

    ia = image_from_frame(a).crop(box)
    ib = image_from_frame(b).crop(box)
    diff = ImageChops.difference(ia, ib)
    bbox = diff.getbbox()
    pixels = diff.get_flattened_data() if hasattr(diff, "get_flattened_data") else diff.getdata()
    changed = sum(1 for px in pixels if px != (0, 0, 0))
    return bbox, changed


def eve_reg32(oracle: EveFT812Oracle, addr: int) -> int:
    return int.from_bytes(oracle.read(addr, 4), "little")


def print_eve_debug(oracle: EveFT812Oracle, mirror: EveSPIMirror, label: str) -> None:
    print(
        f"EVE DEBUG {label}: "
        f"hsize={eve_reg32(oracle, REG_HSIZE)} vsize={eve_reg32(oracle, REG_VSIZE)} "
        f"pclk={eve_reg32(oracle, REG_PCLK)} dlswap={eve_reg32(oracle, REG_DLSWAP)} "
        f"cmd_read={eve_reg32(oracle, REG_CMD_READ)} cmd_write={eve_reg32(oracle, REG_CMD_WRITE)} "
        f"cmdb_space={eve_reg32(oracle, REG_CMDB_SPACE)} "
        f"complete={oracle._complete_serial} swap={oracle._swap_serial} "
        f"spi_out={mirror.spi_out_bytes} spi_in={mirror.spi_in_bytes} dma={mirror.dma_bytes} "
        f"cs={mirror.cs_on}/{mirror.cs_off}"
    )


def read_equ(path: Path, name: str) -> int:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"^\s*{re.escape(name)}\s+EQU\s+(.+?)\s*$", text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"нет EQU {name} в {path}")
    value = match.group(1).strip()
    return int(value[1:], 16) if value.startswith("#") else int(value)


def set_camera(emu: HMM2FullZ80Emulator, x: int, y: int) -> tuple[int, int]:
    map_inc = ROOT / "Source" / "ASM" / "generated_map.inc"
    runtime_inc = ROOT / "Source" / "ASM" / "generated_runtime_map.inc"
    map_w = read_equ(map_inc, "MAP0_W")
    map_h = read_equ(map_inc, "MAP0_H")
    runtime_w = read_equ(runtime_inc, "RUNTIME_VIEW_W")
    runtime_h = read_equ(runtime_inc, "RUNTIME_VIEW_H")
    ox = min(max(x // 32, 0), map_w - runtime_w + 1)
    oy = min(max(y // 32, 0), map_h - runtime_h + 1)
    emu.set_word(emu.sym["ViewportPixelX"], x)
    emu.set_word(emu.sym["ViewportPixelY"], y)
    emu.set_byte(emu.sym["ViewportOriginX"], ox)
    emu.set_byte(emu.sym["ViewportOriginY"], oy)
    return ox, oy


def render_transition_near_bottom_right(args: argparse.Namespace) -> None:
    emu = HMM2FullZ80Emulator(ROOT)
    regs = attach_hmm2_shadow(emu)

    with EveFT812Oracle(args.eve_bin) as oracle:
        print(f"bt8xxemu: {oracle.version}; params_size={ctypes.sizeof(EmulatorParameters)}")
        with EveSPIMirror(emu, oracle) as mirror:
            emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
            emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
            emu.call(emu.sym["Input_Init"], max_steps=200_000)
            emu.call(emu.sym["Game_Init"], max_steps=12_000_000)
            oracle.write_probe_regs_1024()
            print_eve_debug(oracle, mirror, "after-video-sync")

            ox0, oy0 = set_camera(emu, args.from_x, args.from_y)
            regs.tick_frame(emu.ft.ram_dl)
            before_swap = oracle._swap_serial
            before_complete = oracle._complete_serial
            emu.call(emu.sym["Render_Frame"], max_steps=30_000_000)
            try:
                pre = oracle.wait_frame(before_swap, before_complete, timeout=8.0, require_swap=True)
            except Exception:
                print_eve_debug(oracle, mirror, "pre-timeout")
                raise
            args.out_dir.mkdir(parents=True, exist_ok=True)
            save_argb_png(pre, args.out_dir / "transition_pre.png")

            ox1, oy1 = set_camera(emu, args.to_x, args.to_y)
            before_swap = oracle._swap_serial
            before_complete = oracle._complete_serial
            oracle.begin_capture(limit=args.capture_limit)
            t0 = time.monotonic()
            regs.tick_frame(emu.ft.ram_dl)
            emu.call(emu.sym["Render_Frame"], max_steps=30_000_000)
            try:
                final = oracle.wait_frame(before_swap, before_complete, timeout=8.0, require_swap=True)
            except Exception:
                print_eve_debug(oracle, mirror, "transition-timeout")
                raise
            time.sleep(args.post_wait_ms / 1000.0)
            captured = oracle.end_capture()
            save_argb_png(final, args.out_dir / "transition_final.png")

            for index, item in enumerate(captured):
                save_argb_png(item.frame, args.out_dir / f"transition_{index:03d}_s{item.serial:04d}_f{item.frame.flags:02X}.png")

            viewport_box = (
                read_equ(ROOT / "Source" / "ASM" / "generated_terrain.inc", "GAME_VIEW_SCREEN_X"),
                read_equ(ROOT / "Source" / "ASM" / "generated_terrain.inc", "GAME_VIEW_SCREEN_Y"),
                read_equ(ROOT / "Source" / "ASM" / "generated_terrain.inc", "GAME_VIEW_SCREEN_X")
                + read_equ(ROOT / "Source" / "ASM" / "generated_terrain.inc", "GAME_VIEW_SCREEN_W"),
                read_equ(ROOT / "Source" / "ASM" / "generated_terrain.inc", "GAME_VIEW_SCREEN_Y")
                + read_equ(ROOT / "Source" / "ASM" / "generated_terrain.inc", "GAME_VIEW_SCREEN_H"),
            )
            print(
                f"transition camera: ({args.from_x},{args.from_y}) origin=({ox0},{oy0}) -> "
                f"({args.to_x},{args.to_y}) origin=({ox1},{oy1})"
            )
            print(
                f"mirror: spi_out={mirror.spi_out_bytes} spi_in={mirror.spi_in_bytes} "
                f"dma_bytes={mirror.dma_bytes} cs={mirror.cs_on}/{mirror.cs_off}"
            )
            print(
                f"EVE capture: frames={len(captured)} duration_ms={(time.monotonic() - t0) * 1000:.1f} "
                f"pre={args.out_dir / 'transition_pre.png'} final={args.out_dir / 'transition_final.png'}"
            )
            intermediate = [
                (index, item)
                for index, item in enumerate(captured)
                if item.frame.argb != pre.argb and item.frame.argb != final.argb
            ]
            for index, item in enumerate(captured[:12]):
                pre_bbox, pre_changed = diff_summary(pre, item.frame, viewport_box)
                final_bbox, final_changed = diff_summary(final, item.frame, viewport_box)
                print(
                    f"  frame[{index:02d}] serial={item.serial} swap={item.swap_serial} flags=0x{item.frame.flags:02X} "
                    f"pre_diff_bbox={pre_bbox} pre_changed={pre_changed} "
                    f"final_diff_bbox={final_bbox} final_changed={final_changed}"
                )
            if args.assert_no_tearing and intermediate:
                index, item = intermediate[0]
                pre_bbox, pre_changed = diff_summary(pre, item.frame, viewport_box)
                final_bbox, final_changed = diff_summary(final, item.frame, viewport_box)
                raise SystemExit(
                    "ОШИБКА: EVE transition содержит промежуточный кадр между pre/final: "
                    f"frame[{index}] serial={item.serial} flags=0x{item.frame.flags:02X} "
                    f"pre_bbox={pre_bbox} pre_changed={pre_changed} "
                    f"final_bbox={final_bbox} final_changed={final_changed}"
                )
            if args.assert_no_tearing:
                print("OK: EVE transition has no intermediate/torn frames")


def make_hmm2_frame_states(viewport_xs: Iterable[int]) -> list[HMM2FrameState]:
    emu = HMM2FullZ80Emulator(ROOT)
    regs = attach_hmm2_shadow(emu)

    def render_frame(max_steps: int = 30_000_000) -> None:
        regs.tick_frame(emu.ft.ram_dl)
        emu.call(emu.sym["Render_Frame"], max_steps=max_steps)

    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)

    states: list[HMM2FrameState] = []
    for viewport_x in viewport_xs:
        emu.set_word(emu.sym["ViewportPixelX"], viewport_x)
        set_camera(emu, viewport_x, emu.get_word(emu.sym["ViewportPixelY"]))
        render_frame(12_000_000)
        states.append(
            HMM2FrameState(
                viewport_x=viewport_x,
                ram_g=bytes(emu.ft.ram_g),
                ram_dl=bytes(emu.ft.ram_dl[:RAM_DL_SIZE]),
                regs=bytes(regs.bytes),
            )
        )
    return states


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render HMM2 FT812 snapshots through real Bridgetek bt8xxemu.")
    parser.add_argument("--probe", action="store_true", help="Render a simple clear-frame through EVE first.")
    parser.add_argument("--transition", action="store_true", help="Mirror Z80 SPI into EVE and capture the frame transition.")
    parser.add_argument("--from-x", type=int, default=700)
    parser.add_argument("--from-y", type=int, default=700)
    parser.add_argument("--to-x", type=int, default=704)
    parser.add_argument("--to-y", type=int, default=704)
    parser.add_argument("--capture-limit", type=int, default=80)
    parser.add_argument("--post-wait-ms", type=int, default=120)
    parser.add_argument("--assert-no-tearing", action="store_true")
    parser.add_argument("--scroll-xs", nargs="+", type=int, default=[31, 32], help="ViewportPixelX states to render.")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "Diagnostics" / "eve_ft812")
    parser.add_argument("--eve-bin", type=Path, default=None, help="Folder containing bt8xxemu.dll.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.transition:
        render_transition_near_bottom_right(args)
        return 0
    with EveFT812Oracle(args.eve_bin) as oracle:
        print(f"bt8xxemu: {oracle.version}; params_size={ctypes.sizeof(EmulatorParameters)}")
        if args.probe:
            out = args.out_dir / "probe.png"
            frame = oracle.render_probe(out)
            print(f"EVE probe: {frame.width}x{frame.height} flags=0x{frame.flags:02X} png={out}")
        states = make_hmm2_frame_states(args.scroll_xs)
        for state in states:
            oracle.upload_frame_state(state, args.out_dir / f"hmm2_x{state.viewport_x:04d}.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
