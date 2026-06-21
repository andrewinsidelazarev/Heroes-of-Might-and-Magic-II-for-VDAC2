#!/usr/bin/env python3
from __future__ import annotations

import argparse
import atexit
import ctypes
import json
import os
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UNREAL_ROOT = HERE / "UnrealSpeccyRef" / "zx-evo" / "pentevo" / "unreal" / "Unreal"
DEFAULT_DLL = UNREAL_ROOT / "cfg" / "bt8xxemu_x64.dll"

BT8XXEMU_VERSION_API = 12
BT8XXEMU_EMULATOR_FT812 = 0x0812

BT8XXEMU_EMULATOR_ENABLE_AUDIO = 0x02
BT8XXEMU_EMULATOR_ENABLE_COPROCESSOR = 0x04
BT8XXEMU_EMULATOR_ENABLE_GRAPHICS_MULTITHREAD = 0x20
BT8XXEMU_EMULATOR_ENABLE_DYNAMIC_DEGRADE = 0x40
BT8XXEMU_EMULATOR_ENABLE_REG_PWM_DUTY_EMULATION = 0x100

BT8XXEMU_FRAME_BUFFER_COMPLETE = 0x02
BT8XXEMU_FRAME_CHANGED = 0x04
BT8XXEMU_FRAME_SWAP = 0x08

REG_ID = 0x302000
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
REG_DITHER = 0x302060
REG_SWIZZLE = 0x302064
REG_CSPREAD = 0x302068
REG_PCLK_POL = 0x30206C
REG_PCLK = 0x302070
REG_INT_FLAGS = 0x3020A8
RAM_DL = 0x300000
RAM_G_SIZE = 1024 * 1024
RAM_DL_SIZE = 0x2000
RAM_CMD_WRITE_BASE = 0x302578
RAM_CMD_BASE = 0x308000
RAM_CMD_SIZE = 0x1000
REG_SIZE = 0x1000
FT_TRACE_RANGE_LIMIT = 4096
FT_REG_TRACE_LIMIT = 4096


class UnrealVDAC2Error(RuntimeError):
    pass


class BT8XXEMU_EmulatorParameters(ctypes.Structure):
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


GraphicsCallback = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_int,
)
LogCallback = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_char_p,
)
CloseCallback = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)


@dataclass
class VDAC2Frame:
    width: int
    height: int
    flags: int
    argb8888: bytes


class UnrealVDAC2:
    """VDAC2/FT812 backend из Unreal Speccy.

    Здесь нет модели Spectrum-клонов. Это тонкий мост к тем же функциям
    `BT8XXEMU_chipSelect` и `BT8XXEMU_transfer`, которые вызывает Unreal
    в `ft812.cpp`.
    """

    def __init__(self, dll_path: Path = DEFAULT_DLL, *, capture_frame: bool = True) -> None:
        self.dll_path = Path(dll_path)
        self.capture_frame = capture_frame
        self._dll_dir_cookie = None
        self._dll: Optional[ctypes.CDLL] = None
        self._emu = ctypes.c_void_p()
        self._lock = threading.RLock()
        self._last_frame: Optional[VDAC2Frame] = None
        self._frame_count = 0
        self._has_irq = False
        self._old_irq = False
        self._frame_changed_pending = False
        self._ss_int = False
        self._addr_cnt = 0
        self._data_cnt = 0
        self._addr_int = 0
        self._log_messages: list[str] = []
        self._graphics_callback_count = 0
        self._graphics_complete_count = 0
        self._graphics_output_zero_count = 0
        self._last_graphics_output = 0
        self._last_graphics_flags = 0
        self._last_graphics_width = 0
        self._last_graphics_height = 0

        self._graphics_cb = GraphicsCallback(self._graphics)
        self._log_cb = LogCallback(self._log)
        self._close_cb = CloseCallback(self._close)

    @property
    def version(self) -> str:
        if self._dll is None:
            self.open()
        assert self._dll is not None
        raw = self._dll.BT8XXEMU_version()
        return raw.decode("ascii", errors="replace") if raw else ""

    @property
    def frame_count(self) -> int:
        with self._lock:
            return self._frame_count

    @property
    def last_frame(self) -> Optional[VDAC2Frame]:
        with self._lock:
            return self._last_frame

    @property
    def log_messages(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._log_messages)

    @property
    def graphics_stats(self) -> dict[str, int]:
        with self._lock:
            return {
                "callback_count": self._graphics_callback_count,
                "complete_count": self._graphics_complete_count,
                "output_zero_count": self._graphics_output_zero_count,
                "last_output": self._last_graphics_output,
                "last_flags": self._last_graphics_flags,
                "last_width": self._last_graphics_width,
                "last_height": self._last_graphics_height,
            }

    def open(self) -> None:
        if self._dll is not None:
            return
        if not self.dll_path.exists():
            raise UnrealVDAC2Error(f"VDAC2 DLL not found: {self.dll_path}")
        if hasattr(os, "add_dll_directory"):
            self._dll_dir_cookie = os.add_dll_directory(str(self.dll_path.parent))
        self._dll = ctypes.CDLL(str(self.dll_path))
        self._bind()

        params = BT8XXEMU_EmulatorParameters()
        self._dll.BT8XXEMU_defaults(
            BT8XXEMU_VERSION_API,
            ctypes.byref(params),
            BT8XXEMU_EMULATOR_FT812,
        )
        params.Graphics = ctypes.cast(self._graphics_cb, ctypes.c_void_p).value
        params.Log = ctypes.cast(self._log_cb, ctypes.c_void_p).value
        params.Close = ctypes.cast(self._close_cb, ctypes.c_void_p).value
        params.Flags = (
            BT8XXEMU_EMULATOR_ENABLE_AUDIO
            | BT8XXEMU_EMULATOR_ENABLE_COPROCESSOR
            | BT8XXEMU_EMULATOR_ENABLE_GRAPHICS_MULTITHREAD
        )
        params.Flags &= ~BT8XXEMU_EMULATOR_ENABLE_DYNAMIC_DEGRADE
        params.Flags &= ~BT8XXEMU_EMULATOR_ENABLE_REG_PWM_DUTY_EMULATION

        self._dll.BT8XXEMU_run(
            BT8XXEMU_VERSION_API,
            ctypes.byref(self._emu),
            ctypes.byref(params),
        )
        if not self._emu.value or not self._dll.BT8XXEMU_isRunning(self._emu):
            self.close()
            raise UnrealVDAC2Error("BT8XXEMU FT812 did not start")
        atexit.register(self.close)

    def close(self) -> None:
        if self._dll is not None and self._emu.value:
            self._dll.BT8XXEMU_destroy(self._emu)
        self._emu = ctypes.c_void_p()
        self._dll = None
        if self._dll_dir_cookie is not None:
            self._dll_dir_cookie.close()
            self._dll_dir_cookie = None

    def chip_select(self, active: bool) -> None:
        self.open()
        assert self._dll is not None
        self._dll.BT8XXEMU_chipSelect(self._emu, 1 if active else 0)
        with self._lock:
            self._ss_int = active
            if not active:
                self._addr_cnt = 0
                self._data_cnt = 0
                self._addr_int = 0

    def transfer(self, value: int) -> int:
        self.open()
        assert self._dll is not None
        value &= 0xFF
        result = int(self._dll.BT8XXEMU_transfer(self._emu, value)) & 0xFF
        return self._xfer_int(result, value)

    def is_interrupt(self) -> bool:
        with self._lock:
            rc = self._has_irq and not self._old_irq
            self._old_irq = self._has_irq
            return rc

    def wait_frame(self, previous_count: int = 0, timeout_s: float = 3.0) -> Optional[VDAC2Frame]:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            with self._lock:
                if self._frame_count > previous_count:
                    return self._last_frame
            time.sleep(0.002)
        return None

    def read_reg8(self, addr: int) -> int:
        return self.read_mem(addr, 1)[0]

    def read_reg16(self, addr: int) -> int:
        data = self.read_mem(addr, 2)
        return data[0] | (data[1] << 8)

    def read_reg32(self, addr: int) -> int:
        data = self.read_mem(addr, 4)
        return data[0] | (data[1] << 8) | (data[2] << 16) | (data[3] << 24)

    def read_mem(self, addr: int, size: int) -> bytes:
        self.chip_select(True)
        try:
            self.transfer((addr >> 16) & 0x3F)
            self.transfer((addr >> 8) & 0xFF)
            self.transfer(addr & 0xFF)
            self.transfer(0x00)
            return bytes(self.transfer(0xFF) for _ in range(size))
        finally:
            self.chip_select(False)

    def _bind(self) -> None:
        assert self._dll is not None
        self._dll.BT8XXEMU_version.argtypes = []
        self._dll.BT8XXEMU_version.restype = ctypes.c_char_p
        self._dll.BT8XXEMU_defaults.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(BT8XXEMU_EmulatorParameters),
            ctypes.c_int,
        ]
        self._dll.BT8XXEMU_defaults.restype = None
        self._dll.BT8XXEMU_run.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(BT8XXEMU_EmulatorParameters),
        ]
        self._dll.BT8XXEMU_run.restype = None
        self._dll.BT8XXEMU_destroy.argtypes = [ctypes.c_void_p]
        self._dll.BT8XXEMU_destroy.restype = None
        self._dll.BT8XXEMU_isRunning.argtypes = [ctypes.c_void_p]
        self._dll.BT8XXEMU_isRunning.restype = ctypes.c_int
        self._dll.BT8XXEMU_chipSelect.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._dll.BT8XXEMU_chipSelect.restype = None
        self._dll.BT8XXEMU_transfer.argtypes = [ctypes.c_void_p, ctypes.c_uint8]
        self._dll.BT8XXEMU_transfer.restype = ctypes.c_uint8
        if hasattr(self._dll, "BT8XXEMU_hasInterrupt"):
            self._dll.BT8XXEMU_hasInterrupt.argtypes = [ctypes.c_void_p]
            self._dll.BT8XXEMU_hasInterrupt.restype = ctypes.c_int

    def _xfer_int(self, result: int, data: int) -> int:
        with self._lock:
            if not self._ss_int:
                return result
            if self._addr_cnt < 3:
                self._addr_int = ((self._addr_int << 8) | data) & 0xFFFFFF
                self._addr_cnt += 1
                return result
            if self._data_cnt < 2:
                if self._data_cnt == 1 and self._addr_int == REG_INT_FLAGS:
                    result = 1 if self._has_irq else 0
                    self._has_irq = False
                self._data_cnt += 1
        return result & 0xFF

    def _graphics(
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
        with self._lock:
            self._graphics_callback_count += 1
            self._last_graphics_output = int(output)
            self._last_graphics_flags = int(flags)
            self._last_graphics_width = int(hsize)
            self._last_graphics_height = int(vsize)
            if flags & (BT8XXEMU_FRAME_CHANGED | BT8XXEMU_FRAME_SWAP):
                self._frame_changed_pending = True
            if self._frame_changed_pending and (flags & BT8XXEMU_FRAME_BUFFER_COMPLETE):
                self._frame_changed_pending = False
                self._has_irq = True
                self._frame_count += 1
                self._graphics_complete_count += 1
                if not output:
                    self._graphics_output_zero_count += 1
                if self.capture_frame and output and buffer and hsize and vsize:
                    size = int(hsize) * int(vsize) * 4
                    data = ctypes.string_at(buffer, size)
                    self._last_frame = VDAC2Frame(int(hsize), int(vsize), int(flags), data)
        return 1

    def _log(self, sender: int, context: int, log_type: int, message: bytes) -> None:
        del sender, context
        if log_type == 2:
            return
        text = message.decode("utf-8", errors="replace") if message else ""
        with self._lock:
            self._log_messages.append(text)
            if len(self._log_messages) > 64:
                del self._log_messages[: len(self._log_messages) - 64]

    def _close(self, sender: int, context: int) -> None:
        del sender, context


class UnrealVDAC2ZController:
    """Узкий Z-Controller: только TS-Config SPI для VDAC2 через #77/#57."""

    def __init__(self, vdac2: UnrealVDAC2) -> None:
        self.vdac2 = vdac2
        self.cfg = 3
        self.status = 0
        self.rd_buff = 0xFF

    def reset(self) -> None:
        self.cfg = 3
        self.status = 0
        self.rd_buff = 0xFF
        self.vdac2.chip_select(False)

    def write(self, port: int, value: int) -> None:
        value &= 0xFF
        low = port & 0xFF
        if low == 0x77:
            value &= 0x1F
            if (self.cfg & 4) != (value & 4):
                self.vdac2.chip_select(bool(value & 4))
            self.cfg = value
            return
        if low != 0x57:
            return
        if self.cfg & 4:
            self.rd_buff = self.vdac2.transfer(value)
        else:
            self.rd_buff = 0xFF

    def read(self, port: int) -> int:
        low = port & 0xFF
        if low == 0x77:
            return self.status
        if low != 0x57:
            return 0xFF
        value = self.rd_buff
        if self.cfg & 4:
            self.rd_buff = self.vdac2.transfer(0xFF)
        else:
            self.rd_buff = 0xFF
        return value & 0xFF


try:
    from hmm2_ft812_snapshot import HMM2FullZ80Emulator  # noqa: E402
    from tsconf_ft812_sim import PAGE_SIZE  # noqa: E402
except Exception as exc:  # pragma: no cover - harness reports this.
    HMM2FullZ80Emulator = None  # type: ignore
    PAGE_SIZE = 0x4000
    HMM2_IMPORT_ERROR: Optional[BaseException] = exc
else:
    HMM2_IMPORT_ERROR = None


class HMM2UnrealVDAC2Machine(HMM2FullZ80Emulator):  # type: ignore[misc, valid-type]
    """HMM2 harness backend: Z80/TS-Config из проекта, VDAC2 из Unreal."""

    def __init__(self, root: Path = ROOT, *, trace: bool = False) -> None:
        if HMM2_IMPORT_ERROR is not None:
            raise UnrealVDAC2Error(f"HMM2 harness imports failed: {HMM2_IMPORT_ERROR}") from HMM2_IMPORT_ERROR
        super().__init__(root, trace=trace)
        self.vdac2 = UnrealVDAC2()
        self.vdac2.open()
        self.zc_cfg = 3
        self.zc_status = 0
        self.zc_rd_buff = 0xFF
        self.ft_reg_writes: list[tuple[int, int]] = []
        self.ft_write_counts: dict[str, int] = {}
        self.ft_write_ranges: list[tuple[str, int, int]] = []
        self.ft_write_ranges_dropped = 0
        self.ft_bus_trace_enabled = False
        self.ft_bus_trace: list[dict[str, object]] = []
        self.ft_bus_trace_dropped = 0
        self.ft_bus_trace_limit = 1_000_000
        self._ft_bus_seq = 0
        self.vdac2.chip_select(False)

    def close(self) -> None:
        self.vdac2.close()

    def clear_ft_write_trace(self) -> None:
        self.ft_reg_writes.clear()
        self.ft_write_counts.clear()
        self.ft_write_ranges.clear()
        self.ft_write_ranges_dropped = 0

    def enable_ft_bus_trace(self, *, limit: int = 1_000_000) -> None:
        self.ft_bus_trace_enabled = True
        self.ft_bus_trace = []
        self.ft_bus_trace_dropped = 0
        self.ft_bus_trace_limit = limit
        self._ft_bus_seq = 0

    def disable_ft_bus_trace(self) -> None:
        self.ft_bus_trace_enabled = False

    def _ft_addr_region(self, addr: int | None) -> str | None:
        if addr is None:
            return None
        region = self._ft_write_region(addr)
        return region[0] if region is not None else None

    def _record_ft_bus(self, event: str, **fields: object) -> None:
        if not self.ft_bus_trace_enabled:
            return
        if len(self.ft_bus_trace) >= self.ft_bus_trace_limit:
            self.ft_bus_trace_dropped += 1
            return
        pc = getattr(self.reg, "PC", None)
        item: dict[str, object] = {
            "seq": self._ft_bus_seq,
            "event": event,
            "tstates": int(getattr(self, "tstates", 0)),
            "frame_irqs": int(getattr(self, "frame_interrupts", 0)),
            "pc": f"#{pc:04X}" if isinstance(pc, int) else None,
            "zc_cfg": self.zc_cfg,
            "spi_target": self.spi_target,
            "ft_mode": self.ft.spi_mode,
            "ft_phase": self.ft.spi_phase,
            "ft_addr": f"#{(self.ft.spi_addr or 0) & 0x3FFFFF:06X}" if self.ft.spi_addr is not None else None,
        }
        item.update(fields)
        self.ft_bus_trace.append(item)
        self._ft_bus_seq += 1

    def dump_ft_bus_trace(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as f:
            for item in self.ft_bus_trace:
                f.write(json.dumps(item, sort_keys=True, separators=(",", ":")))
                f.write("\n")

    def ft_bus_trace_summary(self) -> dict[str, object]:
        counts: dict[str, int] = {}
        regions: dict[str, int] = {}
        for item in self.ft_bus_trace:
            event = str(item.get("event"))
            counts[event] = counts.get(event, 0) + 1
            region = item.get("region")
            if isinstance(region, str):
                regions[region] = regions.get(region, 0) + 1
        return {
            "enabled": self.ft_bus_trace_enabled,
            "events": len(self.ft_bus_trace),
            "dropped": self.ft_bus_trace_dropped,
            "counts_by_event": dict(sorted(counts.items())),
            "counts_by_region": dict(sorted(regions.items())),
        }

    def _ft_write_region(self, addr: int) -> tuple[str, int] | None:
        addr &= 0x3FFFFF
        if 0 <= addr < RAM_G_SIZE:
            return ("RAM_G", addr)
        if RAM_DL <= addr < RAM_DL + RAM_DL_SIZE:
            return ("RAM_DL", addr - RAM_DL)
        if RAM_CMD_WRITE_BASE <= addr < RAM_CMD_WRITE_BASE + RAM_CMD_SIZE:
            return ("RAM_CMD_WRITE", addr - RAM_CMD_WRITE_BASE)
        if REG_BASE <= addr < REG_BASE + REG_SIZE:
            return ("REG", addr - REG_BASE)
        if RAM_CMD_BASE <= addr < RAM_CMD_BASE + RAM_CMD_SIZE:
            return ("RAM_CMD", addr - RAM_CMD_BASE)
        return None

    def _trace_ft_write(self, addr: int, value: int) -> None:
        region = self._ft_write_region(addr)
        if region is None:
            return
        name, off = region
        value &= 0xFF
        self.ft_write_counts[name] = self.ft_write_counts.get(name, 0) + 1
        if name == "REG":
            self.ft_reg_writes.append((addr & 0x3FFFFF, value))
            if len(self.ft_reg_writes) > FT_REG_TRACE_LIMIT:
                del self.ft_reg_writes[: len(self.ft_reg_writes) - FT_REG_TRACE_LIMIT]

        end = off + 1
        if self.ft_write_ranges:
            last_name, last_start, last_end = self.ft_write_ranges[-1]
            if last_name == name and last_end == off:
                self.ft_write_ranges[-1] = (last_name, last_start, end)
                return
        if len(self.ft_write_ranges) < FT_TRACE_RANGE_LIMIT:
            self.ft_write_ranges.append((name, off, end))
        else:
            self.ft_write_ranges_dropped += 1

    def ft_write_summary(self) -> dict[str, object]:
        def pack_range(item: tuple[str, int, int]) -> dict[str, object]:
            region, start, end = item
            return {
                "region": region,
                "start": start,
                "end_exclusive": end,
                "bytes": end - start,
                "start_hex": f"#{start:06X}",
                "end_inclusive_hex": f"#{end - 1:06X}",
            }

        ranges_head = self.ft_write_ranges[:128]
        ranges_tail = self.ft_write_ranges[-128:] if len(self.ft_write_ranges) > 128 else []
        return {
            "total_writes": sum(self.ft_write_counts.values()),
            "counts_by_region": dict(sorted(self.ft_write_counts.items())),
            "range_count_kept": len(self.ft_write_ranges),
            "range_count_dropped": self.ft_write_ranges_dropped,
            "ranges_head": [pack_range(item) for item in ranges_head],
            "ranges_tail": [pack_range(item) for item in ranges_tail],
            "reg_writes_tail": [
                {
                    "addr": addr,
                    "addr_hex": f"#{addr:06X}",
                    "offset_hex": f"#{addr - REG_BASE:03X}",
                    "value": value,
                    "value_hex": f"#{value:02X}",
                }
                for addr, value in self.ft_reg_writes[-128:]
            ],
        }

    def in_port(self, port: int) -> int:
        low = port & 0xFF
        if low == 0x77:
            return self.zc_status
        if low == 0x57:
            return self._zc_read_data(port)
        return super().in_port(port)

    def out_port(self, port: int, value: int) -> None:
        low = port & 0xFF
        value &= 0xFF
        if low == 0x77:
            self._zc_write_cfg(value)
            return
        if low == 0x57:
            self._zc_write_data(port, value)
            return
        super().out_port(port, value)

    def _zc_write_cfg(self, value: int) -> None:
        value &= 0x1F
        old_cfg = self.zc_cfg
        old_sd = not (self.zc_cfg & 2)
        new_sd = not (value & 2)

        if (self.zc_cfg & 4) != (value & 4):
            self._record_ft_bus(
                "FT_CS",
                active=bool(value & 4),
                old_cfg=f"#{old_cfg:02X}",
                new_cfg=f"#{value:02X}",
            )
            self.vdac2.chip_select(bool(value & 4))
        if old_sd and not new_sd:
            self.sd.deselect()
        elif (not old_sd) and new_sd:
            self.sd.select()

        self.zc_cfg = value
        self.spi_target = "sd" if new_sd else ("ft" if value & 4 else "idle")
        self._record_ft_bus(
            "ZC_CFG",
            old_cfg=f"#{old_cfg:02X}",
            new_cfg=f"#{value:02X}",
            target=self.spi_target,
        )
        super()._write_ft_spi(0x77, value)

    def _zc_write_data(self, port: int, value: int) -> None:
        del port
        value &= 0xFF
        if not (self.zc_cfg & 2):
            self.zc_rd_buff = self.sd.spi_in()
            self.sd.spi_out(value)
        elif self.zc_cfg & 4:
            phase = self.ft.spi_phase
            mode = self.ft.spi_mode
            addr_before = self.ft.spi_addr
            addr = addr_before if mode == "write" and phase >= 3 else None
            self.zc_rd_buff = self.vdac2.transfer(value)
            self._record_ft_bus(
                "FT_XFER_OUT",
                mosi=f"#{value:02X}",
                miso=f"#{self.zc_rd_buff:02X}",
                phase_before=phase,
                mode_before=mode,
                addr_before=f"#{(addr_before or 0) & 0x3FFFFF:06X}" if addr_before is not None else None,
                write_addr=f"#{addr & 0x3FFFFF:06X}" if addr is not None else None,
                region=self._ft_addr_region(addr),
            )
            if addr is not None:
                self._trace_ft_write(addr, value)
            super()._write_ft_spi(0x57, value)
        else:
            self.zc_rd_buff = 0xFF

    def _zc_read_data(self, port: int) -> int:
        value = self.zc_rd_buff
        if not (self.zc_cfg & 2):
            self.zc_rd_buff = self.sd.spi_in()
            self.sd.spi_out(0xFF)
        elif self.zc_cfg & 4:
            phase = self.ft.spi_phase
            mode = self.ft.spi_mode
            addr_before = self.ft.spi_addr
            self.zc_rd_buff = self.vdac2.transfer(0xFF)
            self._record_ft_bus(
                "FT_XFER_IN",
                returned=f"#{value:02X}",
                mosi=f"#FF",
                next_miso=f"#{self.zc_rd_buff:02X}",
                phase_before=phase,
                mode_before=mode,
                addr_before=f"#{(addr_before or 0) & 0x3FFFFF:06X}" if addr_before is not None else None,
                read_addr=f"#{addr_before & 0x3FFFFF:06X}" if addr_before is not None and mode == "read" and phase >= 3 else None,
                region=self._ft_addr_region(addr_before if mode == "read" and phase >= 3 else None),
            )
            super()._read_ft_spi()
        else:
            self.zc_rd_buff = 0xFF
        return value & 0xFF

    def _dma_ram_spi(self) -> None:
        if (self.zc_cfg & 4) and (
            self.ft.spi_mode != "write" or self.ft.spi_phase < 3 or self.ft.spi_addr is None
        ):
            self.errors.append("DMA_RAM_SPI started without active FT812 SPI write transaction")
            return
        src_off = ((self.dma.src_h << 8) | self.dma.src_l) & (PAGE_SIZE - 1)
        src = ((self.dma.src_x & 0xFF) * PAGE_SIZE) + src_off
        words = (self.dma.number + 1) * (self.dma.length + 1)
        byte_count = words * 2
        end = min(src + byte_count, len(self.mem.physical))
        if end - src != byte_count:
            self.errors.append(f"DMA_RAM_SPI source overflow src=#{src:06X} bytes={byte_count}")
        dst_addr = self.ft.spi_addr & 0x3FFFFF if self.ft.spi_addr is not None else None
        self._record_ft_bus(
            "DMA_RAM_SPI_BEGIN",
            src=f"#{src:06X}",
            bytes=end - src,
            requested_bytes=byte_count,
            dst=f"#{dst_addr:06X}" if dst_addr is not None else None,
            region=self._ft_addr_region(dst_addr),
        )
        for value in self.mem.physical[src:end]:
            self._zc_write_data(0x10057, value)
        dst_after = self.ft.spi_addr & 0x3FFFFF if self.ft.spi_addr is not None else None
        self._record_ft_bus(
            "DMA_RAM_SPI_END",
            src_end=f"#{end:06X}",
            dst=f"#{dst_after:06X}" if dst_after is not None else None,
            bytes=end - src,
        )
        self._advance_dma_source(src + (end - src))


def _spi_read_reg_via_zc(zc: UnrealVDAC2ZController, addr: int, reads: int = 4) -> list[int]:
    zc.write(0x77, 0x07)
    zc.write(0x57, (addr >> 16) & 0x3F)
    zc.write(0x57, (addr >> 8) & 0xFF)
    zc.write(0x57, addr & 0xFF)
    out = [zc.read(0x57) for _ in range(reads)]
    zc.write(0x77, 0x03)
    return out


def _spi_write_bytes_via_zc(zc: UnrealVDAC2ZController, addr: int, data: bytes) -> None:
    zc.write(0x77, 0x07)
    zc.write(0x57, 0x80 | ((addr >> 16) & 0x3F))
    zc.write(0x57, (addr >> 8) & 0xFF)
    zc.write(0x57, addr & 0xFF)
    for value in data:
        zc.write(0x57, value)
    zc.write(0x77, 0x03)


def _spi_write8_via_zc(zc: UnrealVDAC2ZController, addr: int, value: int) -> None:
    _spi_write_bytes_via_zc(zc, addr, bytes((value & 0xFF,)))


def _spi_write16_via_zc(zc: UnrealVDAC2ZController, addr: int, value: int) -> None:
    _spi_write_bytes_via_zc(zc, addr, int(value & 0xFFFF).to_bytes(2, "little"))


def _spi_write32_via_zc(zc: UnrealVDAC2ZController, addr: int, value: int) -> None:
    _spi_write_bytes_via_zc(zc, addr, int(value & 0xFFFFFFFF).to_bytes(4, "little"))


def _dl_clear_color_rgb(r: int, g: int, b: int) -> int:
    return 0x02000000 | ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)


def _dl_clear(color: bool = True, stencil: bool = True, tag: bool = True) -> int:
    return 0x26000000 | (0x04 if color else 0) | (0x02 if stencil else 0) | (0x01 if tag else 0)


def _configure_1024x768_via_zc(zc: UnrealVDAC2ZController) -> None:
    _spi_write16_via_zc(zc, REG_HCYCLE, 1344)
    _spi_write16_via_zc(zc, REG_HOFFSET, 320)
    _spi_write16_via_zc(zc, REG_HSIZE, 1024)
    _spi_write16_via_zc(zc, REG_HSYNC0, 24)
    _spi_write16_via_zc(zc, REG_HSYNC1, 160)
    _spi_write16_via_zc(zc, REG_VCYCLE, 806)
    _spi_write16_via_zc(zc, REG_VOFFSET, 37)
    _spi_write16_via_zc(zc, REG_VSIZE, 768)
    _spi_write16_via_zc(zc, REG_VSYNC0, 2)
    _spi_write16_via_zc(zc, REG_VSYNC1, 8)
    _spi_write8_via_zc(zc, REG_DITHER, 1)
    _spi_write8_via_zc(zc, REG_SWIZZLE, 0)
    _spi_write8_via_zc(zc, REG_CSPREAD, 0)
    _spi_write8_via_zc(zc, REG_PCLK_POL, 0)
    _spi_write8_via_zc(zc, REG_PCLK, 8)


def frame_test(out_path: Path) -> int:
    vdac2 = UnrealVDAC2()
    zc = UnrealVDAC2ZController(vdac2)
    try:
        vdac2.open()
        zc.reset()
        _configure_1024x768_via_zc(zc)
        dl_words = (
            _dl_clear_color_rgb(16, 48, 96),
            _dl_clear(),
            0x00000000,
        )
        dl = b"".join(word.to_bytes(4, "little") for word in dl_words)
        before = vdac2.frame_count
        _spi_write_bytes_via_zc(zc, RAM_DL, dl)
        _spi_write8_via_zc(zc, REG_DLSWAP, 2)
        frame = vdac2.wait_frame(before, timeout_s=5.0)
        print(f"dll: {vdac2.dll_path}")
        print(f"version: {vdac2.version.splitlines()[0] if vdac2.version else ''}")
        print(f"frame_count: {vdac2.frame_count}")
        if frame is None:
            print("frame: none")
            return 1
        print(f"frame: {frame.width}x{frame.height} flags=#{frame.flags:02X}")
        try:
            from PIL import Image
        except Exception as exc:
            print(f"png: skipped ({exc})")
            return 0
        raw = frame.argb8888
        rgba = bytearray(len(raw))
        for i in range(0, len(raw), 4):
            b, g, r, a = raw[i], raw[i + 1], raw[i + 2], raw[i + 3]
            rgba[i:i + 4] = bytes((r, g, b, a))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        Image.frombytes("RGBA", (frame.width, frame.height), bytes(rgba)).save(out_path)
        print(f"png: {out_path}")
        return 0
    finally:
        vdac2.close()


def self_test() -> int:
    vdac2 = UnrealVDAC2()
    zc = UnrealVDAC2ZController(vdac2)
    try:
        vdac2.open()
        zc.reset()
        samples = _spi_read_reg_via_zc(zc, REG_ID, reads=6)
        print(f"dll: {vdac2.dll_path}")
        print(f"version: {vdac2.version}")
        print("REG_ID read pipeline:", " ".join(f"{b:02X}" for b in samples))
        if 0x7C not in samples:
            raise UnrealVDAC2Error("REG_ID 0x7C was not observed through #77/#57 SPI")
        print("ok: TS-Config #77/#57 -> Unreal BT8XXEMU FT812 works")
        return 0
    finally:
        vdac2.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Focused TS-Config VDAC2 bridge backed by Unreal Speccy BT8XXEMU.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--frame-test", action="store_true")
    parser.add_argument("--out", type=Path, default=ROOT / "Diagnostics" / "vdac2_frame_probe.png")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()
    if args.frame_test:
        return frame_test(args.out)
    print("Use --self-test")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
