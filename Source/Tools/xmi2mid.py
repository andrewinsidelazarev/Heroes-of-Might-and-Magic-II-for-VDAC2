#!/usr/bin/env python3
"""XMI → MIDI (SMF type 0) конвертер. Точный порт fheroes2 engine/audio_xmi2mid.cpp.

Оригинальная музыка HMM2 хранится в HEROES2.AGG как XMI (Miles/AIL формат), нечитаемый
стандартными MIDI-плеерами. Здесь — распаковка XMI в стандартный SMF type 0, который
играет MIDI-синтезатор SAM2695 (на MIDI-порту AY port A bit2 ZX Evolution) и принимает
zx-midiplayer.

Особенности XMI vs SMF (как в fheroes2):
  - delay в XMI = сумма подряд идущих байт < 128 (не VLQ!);
  - note-off отсутствует — у note-on (0x9x) после 2 байт идёт VLQ-длительность, из неё
    генерируется note-off (status-0x10, key, velocity 0x7F) на time+duration;
  - все события собираются с АБСОЛЮТНЫМ временем, стабильно сортируются, затем дельты
    кодируются VLQ;
  - XMI играет на фиксированных 120 Гц; ppqn = tempo*3/25000 (или 60 по умолчанию).

Использование:
  python Source/Tools/xmi2mid.py Music/HEROES2/MIDI0042.XMI [-o out.mid]
  python Source/Tools/xmi2mid.py --all          # конвертировать все XMI в Music/ рядом
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read_vlq(data: bytes, i: int) -> tuple[int, int]:
    """Стандартный MIDI VLQ (7 бит/байт, старший бит = продолжение). Возвращает (value, length)."""
    value = 0
    length = 0
    while i + length < len(data) and data[i + length] > 127:
        if length >= 4:
            raise ValueError("VLQ: поле превышает 4 байта")
        value |= data[i + length] & 0x7F
        value <<= 7
        length += 1
    if i + length < len(data):
        value += data[i + length]
    length += 1
    return value, length


def _pack_vlq(delta: int) -> bytes:
    c1 = delta & 0x7F
    c2 = (delta >> 7) & 0x7F
    c3 = (delta >> 14) & 0x7F
    c4 = (delta >> 21) & 0x7F
    if c4:
        return bytes([c4 | 0x80, c3 | 0x80, c2 | 0x80, c1])
    if c3:
        return bytes([c3 | 0x80, c2 | 0x80, c1])
    if c2:
        return bytes([c2 | 0x80, c1])
    return bytes([c1])


def _find_evnt(buf: bytes):
    """Пройти IFF-структуру XMI и вернуть (start, end) данных EVNT-чанка (трек-события)."""
    def be32(i):
        return struct.unpack_from(">I", buf, i)[0]

    # FORM <len> XDIR
    if buf[0:4] != b"FORM" or buf[8:12] != b"XDIR":
        raise ValueError("XMI: не FORM:XDIR")
    pos = 12
    # INFO <len=2> <numTracks LE16>
    if buf[pos:pos + 4] != b"INFO":
        raise ValueError("XMI: нет INFO")
    info_len = be32(pos + 4)
    pos += 8
    if info_len != 2:
        raise ValueError("XMI: INFO length != 2")
    num_tracks = struct.unpack_from("<H", buf, pos)[0]
    pos += 2
    if num_tracks != 1:
        raise ValueError(f"XMI: numTracks={num_tracks} (ожидается 1 для SMF format 0)")
    # CAT  <len> XMID
    if buf[pos:pos + 4] != b"CAT " or buf[pos + 8:pos + 12] != b"XMID":
        raise ValueError("XMI: нет CAT:XMID")
    pos += 12
    # FORM <len> XMID
    if buf[pos:pos + 4] != b"FORM" or buf[pos + 8:pos + 12] != b"XMID":
        raise ValueError("XMI: нет FORM:XMID")
    pos += 12
    # далее IFF-чанки: [TIMB][RBRN] EVNT
    while pos + 8 <= len(buf):
        cid = buf[pos:pos + 4]
        clen = be32(pos + 4)
        pos += 8
        if cid == b"EVNT":
            return pos, pos + clen
        pos += clen
        if clen & 1:        # IFF padding до чётности
            pos += 1
    raise ValueError("XMI: EVNT не найден")


def _parse_events(data: bytes):
    """EVNT → список (time, [bytes]) абсолютных событий + tempo (микросек/четверть)."""
    events = []
    tempo = 0
    i = 0
    time = 0
    n = len(data)
    while i < n:
        b = data[i]
        if b < 128:                      # XMI delay = сумма 7-бит значений
            time += b
            i += 1
            continue
        if b == 0xFF:                    # meta
            i += 1
            if data[i] == 0x2F:          # End of Track
                events.append((time, bytes([0xFF, 0x2F, 0x00])))
                break
            meta_type = data[i]; i += 1
            meta_len = data[i]; i += 1
            events.append((time, bytes([0xFF, meta_type, meta_len]) + data[i:i + meta_len]))
            if meta_type == 0x51 and meta_len == 3:
                tempo = (data[i] << 16) | (data[i + 1] << 8) | data[i + 2]
            i += meta_len
            continue
        hi = b >> 4
        if hi in (0x0A, 0x0B, 0x0E):     # aftertouch / control change / pitch wheel (3 байта)
            events.append((time, bytes([b, data[i + 1], data[i + 2]])))
            i += 3
        elif hi == 0x09:                 # note on (+ VLQ длительность → note off)
            events.append((time, bytes([b, data[i + 1], data[i + 2]])))
            dur, dlen = _read_vlq(data, i + 3)
            events.append((time + dur, bytes([b - 0x10, data[i + 1], 0x7F])))
            i += 3 + dlen
        elif hi == 0x0C:                 # program change (2 байта)
            events.append((time, bytes([b, data[i + 1]])))
            i += 2
        elif hi == 0x0D:                 # channel pressure (2 байта)
            events.append((time, bytes([b, data[i + 1]])))
            i += 2
        else:
            raise ValueError(f"XMI: неизвестная команда {b:#04x} на байте {i}")
    return events, tempo


def xmi_to_mid(buf: bytes) -> bytes:
    start, end = _find_evnt(buf)
    events, tempo = _parse_events(buf[start:end])
    events.sort(key=lambda e: e[0])      # стабильная сортировка по абсолютному времени

    track = bytearray()
    prev = 0
    for t, payload in events:
        track += _pack_vlq(t - prev)
        track += payload
        prev = t

    ppqn = (tempo * 3 // 25000) if tempo > 0 else 60
    out = bytearray()
    out += b"MThd" + struct.pack(">IHHH", 6, 0, 1, ppqn)     # format 0, 1 трек, ppqn
    out += b"MTrk" + struct.pack(">I", len(track)) + track
    return bytes(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="XMI → MIDI (SMF type 0).")
    ap.add_argument("xmi", nargs="?", type=Path, help="входной .XMI")
    ap.add_argument("-o", "--out", type=Path, default=None, help="выходной .mid")
    ap.add_argument("--all", action="store_true", help="конвертировать все Music/**/*.XMI рядом в .mid")
    args = ap.parse_args()

    if args.all:
        xmis = sorted((ROOT / "Music").rglob("*.XMI"))
        if not xmis:
            print("нет Music/**/*.XMI — сначала извлечь из AGG (agg_tools --extract-xmi)")
            return 1
        total = 0
        for x in xmis:
            mid = xmi_to_mid(x.read_bytes())
            out = x.with_suffix(".mid")
            out.write_bytes(mid)
            total += 1
            print(f"  {x.relative_to(ROOT)} -> {out.name} ({len(mid)} байт)")
        print(f"конвертировано XMI→MID: {total}")
        return 0

    if not args.xmi:
        ap.error("укажите .XMI или --all")
    mid = xmi_to_mid(args.xmi.read_bytes())
    out = args.out or args.xmi.with_suffix(".mid")
    out.write_bytes(mid)
    print(f"{args.xmi.name} -> {out} ({len(mid)} байт)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
