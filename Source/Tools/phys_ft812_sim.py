#!/usr/bin/env python3
"""Cycle-accurate физический ко-симулятор тракта Z80 → TS-Config DMA → SPI → FT812.

В отличие от tsconf_ft812_sim.py (функциональный, ВНЕ времени: DMA мгновенный,
swap мгновенный и когерентный) — этот модуль вводит ось времени и моделирует:

  * глобальные часы (секунды), продвигаемые тактами Z80 (tstate / f_z80);
  * TS-Config DMA с физической длительностью: `DMASTATUS` держит busy, пока
    спин-цикл Z80 не «доедет» до момента завершения; байты пишутся в лог с
    интерполированными метками времени;
  * дисплейный движок FT812: PCLK/HCYCLE/VCYCLE → момент сканирования каждой
    строки; `DLSWAP_FRAME` латчится на vblank; `INT_SWAP`/`REG_DLSWAP`/`REG_FRAMES`
    вычисляются из часов (пейсинг главного цикла к ~59 Гц);
  * лог записей RAM_G/RAM_DL (с метками времени) + реконструкцию отображаемого
    кадра ПО ПОЛОСАМ: дисплей читает память ВЖИВУЮ на момент прохода луча, поэтому
    перезапись RAM_DL/RAM_G в середине кадра даёт рваный/рассинхронный кадр —
    физический эффект, который абстрактный sim воспроизвести не может.

Источник истины таймингов — регистры, которые сама прошивка программирует в
FT_RESOLUTION (VM_1024_768_59Hz): PCLK=64МГц, HCYCLE=1344, VCYCLE=806.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from tsconf_ft812_sim import (  # noqa: E402
    PAGE_SIZE,
    RAM_CMD_SIZE,
    RAM_DL_SIZE,
    RAM_G_SIZE,
)
from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT, render_dl_band  # noqa: E402
from shadow_ft812 import (  # noqa: E402
    REG_BASE,
    REG_CLOCK,
    REG_CPURESET,
    REG_DLSWAP,
    REG_FRAMES,
    REG_HCYCLE,
    REG_HOFFSET,
    REG_HSIZE,
    REG_ID,
    REG_INT_FLAGS,
    REG_PCLK,
    REG_VCYCLE,
    REG_VOFFSET,
    REG_VSIZE,
    INT_SWAP,
    disasm_dl,
)

RAM_DL_BASE = 0x300000
REG_SIZE = 0x1000

# Дефолтные тайминги VM_1024_768_59Hz (если регистры ещё/не запрограммированы).
DEFAULT_HCYCLE = 1344
DEFAULT_VCYCLE = 806
DEFAULT_HSIZE = 1024
DEFAULT_VSIZE = 768
DEFAULT_HOFFSET = 320
DEFAULT_VOFFSET = 37
DEFAULT_PCLK_DIV = 8
BOARD_PIXCLK_BASE_HZ = 8_000_000   # VDAC2: PCLK = 8 МГц × REG_PCLK (F_MUL)

DEFAULT_Z80_HZ = 14_000_000        # TS-Conf turbo
# Калибровка пропускной способности DMA→SPI (учебник: ~150 КБ ≈ 70 мс на 14 МГц).
DEFAULT_DMA_BYTES_PER_SEC = 2_140_000


def _is_cmd_addr(addr: int) -> bool:
    return (
        addr in (0x3020F8, 0x3020F9, 0x3020FC, 0x3020FD)
        or 0x302574 <= addr <= 0x302577
        or 0x302578 <= addr < 0x303578
    )


@dataclass
class DisplayTiming:
    hcycle: int
    vcycle: int
    hsize: int
    vsize: int
    hoffset: int
    voffset: int
    pclk_hz: float

    @property
    def line_seconds(self) -> float:
        return self.hcycle / self.pclk_hz

    @property
    def frame_seconds(self) -> float:
        return self.hcycle * self.vcycle / self.pclk_hz

    @property
    def fps(self) -> float:
        return 1.0 / self.frame_seconds

    def frame_index(self, t: float) -> int:
        return int(t / self.frame_seconds)

    def row_time(self, frame_k: int, y: int) -> float:
        """Момент (с), когда луч начинает сканировать видимую строку y кадра k."""
        return frame_k * self.frame_seconds + (self.voffset + y) * self.line_seconds


class PhysFT812Machine(HMM2FullZ80Emulator):
    def __init__(
        self,
        root: Path = ROOT,
        *,
        z80_hz: int = DEFAULT_Z80_HZ,
        dma_bytes_per_sec: float = DEFAULT_DMA_BYTES_PER_SEC,
        board_pixclk_base_hz: int = BOARD_PIXCLK_BASE_HZ,
        trace: bool = False,
    ) -> None:
        super().__init__(root, trace=trace)
        self.z80_hz = float(z80_hz)
        self.dma_sec_per_byte = 1.0 / float(dma_bytes_per_sec)
        self.board_pixclk_base_hz = board_pixclk_base_hz

        self.clock = 0.0                 # глобальные часы, секунды
        self.dma_busy_until = 0.0        # до этого момента DMASTATUS = busy

        self._reg = bytearray(REG_SIZE)  # сырое хранилище регистров FT812
        self.swap_pending_boundary: Optional[float] = None
        self.dlswap_value = 0
        self.swap_writes = 0
        self.int_flags_reads = 0

        # Лог записей в видимую память FT (RAM_G/RAM_DL) с метками времени.
        # Элемент: (t_seconds, region 'G'|'DL', offset, data:bytes)
        self.logging_enabled = False
        self.write_log: List[Tuple[float, str, int, bytes]] = []
        self._cur_write_time: Optional[float] = None

    # ---- часы --------------------------------------------------------------
    def step(self) -> int:
        t = super().step()
        self.clock += t / self.z80_hz
        return t

    def _reg32(self, reg_addr: int) -> int:
        o = reg_addr - REG_BASE
        return self._reg[o] | (self._reg[o + 1] << 8) | (self._reg[o + 2] << 16) | (self._reg[o + 3] << 24)

    def pclk_hz(self) -> float:
        div = self._reg32(REG_PCLK) or DEFAULT_PCLK_DIV
        return float(self.board_pixclk_base_hz * div)

    def frame_seconds(self) -> float:
        hc = self._reg32(REG_HCYCLE) or DEFAULT_HCYCLE
        vc = self._reg32(REG_VCYCLE) or DEFAULT_VCYCLE
        return hc * vc / self.pclk_hz()

    def frame_index(self, t: float) -> int:
        return int(t / self.frame_seconds())

    def display_timing(self) -> DisplayTiming:
        return DisplayTiming(
            hcycle=self._reg32(REG_HCYCLE) or DEFAULT_HCYCLE,
            vcycle=self._reg32(REG_VCYCLE) or DEFAULT_VCYCLE,
            hsize=self._reg32(REG_HSIZE) or DEFAULT_HSIZE,
            vsize=self._reg32(REG_VSIZE) or DEFAULT_VSIZE,
            hoffset=self._reg32(REG_HOFFSET) or DEFAULT_HOFFSET,
            voffset=self._reg32(REG_VOFFSET) or DEFAULT_VOFFSET,
            pclk_hz=self.pclk_hz(),
        )

    # ---- лог записей -------------------------------------------------------
    def _log(self, region: str, offset: int, data: bytes) -> None:
        if not self.logging_enabled:
            return
        t = self._cur_write_time if self._cur_write_time is not None else self.clock
        self.write_log.append((t, region, offset, bytes(data)))

    def begin_logging(self) -> None:
        self.logging_enabled = True
        self.write_log = []

    # ---- порты: DMASTATUS гейтится часами ---------------------------------
    def in_port(self, port: int) -> int:
        if (port & 0xFF) == 0xAF and ((port >> 8) & 0xFF) == 0x27:
            return 0x80 if self.clock < self.dma_busy_until else 0
        return super().in_port(port)

    # ---- DMA с физическим временем ----------------------------------------
    def _start_dma(self, mode: int) -> None:
        if mode == 0x82:
            self._dma_ram_spi()
        else:
            self.errors.append(f"unsupported DMA mode #{mode:02X}")

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
        data = self.mem.physical[src:end]
        n = len(data)
        start_t = self.clock
        dur = n * self.dma_sec_per_byte
        self.dma_busy_until = max(self.dma_busy_until, start_t + dur)
        for i, value in enumerate(data):
            addr = self.ft.spi_addr & 0x3FFFFF
            self._cur_write_time = start_t + (dur * (i + 1) / n) if n else start_t
            self._write_ft_addr(addr, value)
            self.ft.spi_addr = (addr + 1) & 0x3FFFFF
        self._cur_write_time = None
        self._advance_dma_source(src + n)

    # ---- адресное пространство FT812 --------------------------------------
    def _read_ft_addr(self, addr: int) -> int:
        addr &= 0x3FFFFF
        if REG_BASE <= addr < REG_BASE + REG_SIZE:
            if _is_cmd_addr(addr):
                return super()._read_ft_addr(addr)
            if addr == REG_ID:
                return 0x7C
            if REG_CPURESET <= addr < REG_CPURESET + 4:
                return 0
            if REG_INT_FLAGS <= addr < REG_INT_FLAGS + 4:
                return self._read_int_flags_byte(addr)
            if REG_DLSWAP <= addr < REG_DLSWAP + 4:
                return self._read_dlswap_byte(addr)
            if REG_FRAMES <= addr < REG_FRAMES + 4:
                fi = self.frame_index(self.clock)
                return (fi >> (8 * (addr - REG_FRAMES))) & 0xFF
            if REG_CLOCK <= addr < REG_CLOCK + 4:
                ticks = int(self.clock * 60_000_000)
                return (ticks >> (8 * (addr - REG_CLOCK))) & 0xFF
            return self._reg[addr - REG_BASE]
        return super()._read_ft_addr(addr)

    def _write_ft_addr(self, addr: int, value: int) -> None:
        addr &= 0x3FFFFF
        value &= 0xFF
        if addr < RAM_DL_BASE:                       # RAM_G
            self.ft.ram_g[addr & (RAM_G_SIZE - 1)] = value
            self._log("G", addr & (RAM_G_SIZE - 1), bytes([value]))
            return
        if RAM_DL_BASE <= addr < RAM_DL_BASE + RAM_DL_SIZE:
            off = addr - RAM_DL_BASE
            self.ft.ram_dl[off] = value
            self._log("DL", off, bytes([value]))
            return
        if REG_BASE <= addr < REG_BASE + REG_SIZE and not _is_cmd_addr(addr):
            if REG_DLSWAP <= addr < REG_DLSWAP + 4:
                self._reg[addr - REG_BASE] = value
                if addr == REG_DLSWAP:
                    self._arm_swap(value)
                return
            if REG_INT_FLAGS <= addr < REG_INT_FLAGS + 4:
                self._clear_int_flags(value)
                return
            self._reg[addr - REG_BASE] = value
            return
        super()._write_ft_addr(addr, value)          # CMD region и пр.

    # ---- swap/INT таймингом из часов --------------------------------------
    def _arm_swap(self, value: int) -> None:
        mode = value & 3
        if mode in (1, 2):  # DLSWAP_LINE / DLSWAP_FRAME
            fi = self.frame_index(self.clock)
            self.swap_pending_boundary = (fi + 1) * self.frame_seconds()
            self.dlswap_value = mode
            self.swap_writes += 1

    def _read_int_flags_byte(self, addr: int) -> int:
        b = addr - REG_INT_FLAGS
        if b != 0:
            return 0
        self.int_flags_reads += 1
        if self.swap_pending_boundary is None:
            return INT_SWAP                          # нет ожидающего swap — не висим
        return INT_SWAP if self.clock >= self.swap_pending_boundary else 0

    def _clear_int_flags(self, value: int) -> None:
        if value & INT_SWAP and self.swap_pending_boundary is not None and self.clock >= self.swap_pending_boundary:
            self.swap_pending_boundary = None        # swap состоялся и учтён

    def _read_dlswap_byte(self, addr: int) -> int:
        if addr - REG_DLSWAP != 0:
            return 0
        if self.swap_pending_boundary is not None and self.clock < self.swap_pending_boundary:
            return self.dlswap_value                 # ещё не свапнулось
        return 0                                     # DLSWAP_DONE

    # ---- логируемый co-processor CMD-FIFO ---------------------------------
    def _dl_write(self, dl_ptr: int, data: bytes) -> None:
        end = min(dl_ptr + len(data), len(self.ft.ram_dl))
        if end <= dl_ptr:
            return
        self.ft.ram_dl[dl_ptr:end] = data[: end - dl_ptr]
        self._log("DL", dl_ptr, data[: end - dl_ptr])

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
                self._dl_write(dl_ptr, word.to_bytes(4, "little"))
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
                        self._dl_write(dl_ptr, bytes(self.ft.ram_g[real_src:real_src + size]))
                        dl_ptr += size
                continue
            self._dl_write(dl_ptr, word.to_bytes(4, "little"))
            dl_ptr += 4


# =============================================================================
# Реконструкция отображаемых кадров по полосам (forward-replay лога записей)
# =============================================================================
def reconstruct_frames(
    timing: DisplayTiming,
    write_log: List[Tuple[float, str, int, bytes]],
    base_dl: bytes,
    base_g: bytes,
    frame_indices: List[int],
    width: int,
    height: int,
    coherent: bool = False,
):
    """Возвращает {frame_index: PIL.Image} — то, что физически НА ЭКРАНЕ во время
    сканаута кадра, с учётом живого чтения RAM_DL/RAM_G лучом.

    Модель FT81x:
      * RAM_DL ДВОЙНО БУФЕРИЗИРОВАН — DLSWAP_FRAME латчит когерентную копию на
        vblank. Поэтому переписывание RAM_DL копроцессором НЕ рвёт показываемый
        кадр: для кадра k берётся снимок RAM_DL на vblank k*frame (после
        завершённой сборки прошлого кадра).
      * RAM_G НЕ буферизирован — луч читает битмапы (тайлы/спрайты) ВЖИВУЮ.
        Перезапись RAM_G во время сканаута рвёт содержимое под когерентной
        геометрией = тонкий рассинхрон слоёв.

    coherent=True — эталон «как если бы RAM_G тоже был когерентен»: RAM_G берётся
    одним снимком на момент vblank кадра. Сравнение physical vs coherent выявляет
    именно RAM_G-tearing (рассинхрон тайлов/спрайтов)."""
    dl_log = sorted([e for e in write_log if e[1] == "DL"], key=lambda e: e[0])
    g_log = sorted([e for e in write_log if e[1] == "G"], key=lambda e: e[0])
    dl = bytearray(base_dl)
    g = bytearray(base_g)
    dci = 0
    gci = 0

    def adv_dl(t: float) -> None:
        nonlocal dci
        while dci < len(dl_log) and dl_log[dci][0] <= t:
            _t, _r, off, data = dl_log[dci]
            dl[off:off + len(data)] = data
            dci += 1

    def adv_g(t: float) -> None:
        nonlocal gci
        while gci < len(g_log) and g_log[gci][0] <= t:
            _t, _r, off, data = g_log[gci]
            g[off:off + len(data)] = data
            gci += 1

    vsize = timing.vsize
    line_s = timing.line_seconds
    images = {}
    for k in sorted(frame_indices):
        fstart = k * timing.frame_seconds
        vis_lo = fstart + timing.voffset * line_s
        vis_hi = fstart + (timing.voffset + vsize) * line_s
        # DL латчится на vblank k → когерентен для всего кадра
        adv_dl(fstart)
        ops = disasm_dl(bytes(dl), max_ops=4096)
        # RAM_G читается вживую: границы полос = строки, где G-запись впервые видна
        boundaries = {0, vsize}
        if not coherent:
            for (t, _r, _o, _d) in g_log:
                if vis_lo <= t < vis_hi:
                    row = math.ceil((t - fstart) / line_s) - timing.voffset
                    boundaries.add(max(0, min(vsize, row)))
        bands = sorted(boundaries)
        img = alpha = None
        for bi in range(len(bands) - 1):
            y0, y1 = bands[bi], bands[bi + 1]
            adv_g(timing.row_time(k, y0) if not coherent else fstart)
            img, alpha = render_dl_band(ops, bytes(g), width, height, y0, y1, img, alpha)
        adv_g(timing.row_time(k, vsize - 1))
        images[k] = img
    return images


# =============================================================================
# Smoke / самопроверка таймингов и калибровки DMA
# =============================================================================
def _boot(emu: PhysFT812Machine) -> None:
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)


def main() -> int:
    emu = PhysFT812Machine(ROOT)
    _boot(emu)
    t = emu.display_timing()
    print(f"PCLK={t.pclk_hz/1e6:.3f} МГц HCYCLE={t.hcycle} VCYCLE={t.vcycle} "
          f"HSIZE={t.hsize} VSIZE={t.vsize} HOFFSET={t.hoffset} VOFFSET={t.voffset}")
    print(f"fps={t.fps:.3f} Гц; строка={t.line_seconds*1e6:.3f} мкс; "
          f"кадр={t.frame_seconds*1e3:.3f} мс; vblank≈{(t.vcycle-t.vsize)*t.line_seconds*1e3:.3f} мс")
    if not (58.0 <= t.fps <= 60.0):
        print(f"ОШИБКА: fps={t.fps:.3f} вне 58..60")
        return 1
    # калибровка DMA: измерим время известной заливки
    nbytes = 8192
    expected_ms = nbytes * emu.dma_sec_per_byte * 1e3
    print(f"DMA-калибровка: {nbytes} байт ≈ {expected_ms:.3f} мс "
          f"≈ {expected_ms / (t.frame_seconds*1e3):.2f} кадра, "
          f"≈ {expected_ms*1e-3 / t.line_seconds:.0f} сканлайнов")
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
