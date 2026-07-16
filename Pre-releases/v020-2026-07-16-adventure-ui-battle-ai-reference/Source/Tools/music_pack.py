#!/usr/bin/env python3
"""SMF (.mid) → компактный HMM2-музыкальный поток для Z80-плеера (music.asm).

Вся «тяжёлая» музыкальная математика (ppqn, tempo, тики→реальное время) делается ЗДЕСЬ,
чтобы Z80-плеер остался тривиальным: он лишь отсчитывает кадры и шлёт байты MIDI на
синтезатор SAM2695 (через AY-порт). Целевой темп кадра — частота FT812 (VM_1024_768_59Hz).

Формат потока (байты):
  0xF8 nn      — ждать nn кадров (1..255); для больших пауз — несколько подряд;
  0xFF         — конец трека (плеер зацикливает на начало);
  0x80..0xEF … — MIDI-событие: status + данные. Длина данных по старшему ниблу status:
                 0xC_/0xD_ → 1 байт данных, остальные (8/9/A/B/E) → 2 байта. БЕЗ running
                 status (status явный каждый раз — проще для Z80). Meta/SysEx вырезаны
                 (tempo учтён в таймингах, GM-reset шлёт сам плеер).

Использование:
  python Source/Tools/music_pack.py Music/HEROES2/MIDI0042.mid -o Build/MIDI0042.h2m
  python Source/Tools/music_pack.py Music/HEROES2/MIDI0042.mid --inc Source/ASM/generated_music.inc --label Music_MainMenu
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

FPS = 64_000_000 / (1344 * 806)        # VM_1024_768_59Hz = 59.08 Гц (как в hmm2_ft812_snapshot)
US_PER_FRAME = 1_000_000.0 / FPS

WAIT = 0xF8
END = 0xFF


def _read_vlq(data: bytes, i: int) -> tuple[int, int]:
    value = 0
    length = 0
    while data[i + length] > 127:
        value = (value | (data[i + length] & 0x7F)) << 7
        length += 1
    return value + data[i + length], length + 1


def parse_smf(buf: bytes):
    """→ (events[(abs_tick, bytes)], ppqn, tempo_us). Только канальные события."""
    assert buf[0:4] == b"MThd", "не SMF"
    fmt, ntrk, ppqn = struct.unpack_from(">HHH", buf, 8)
    p = buf.find(b"MTrk")
    tlen = struct.unpack_from(">I", buf, p + 4)[0]
    i = p + 8
    end = i + tlen
    events = []
    tempo = 500_000               # дефолт 120 BPM
    abs_tick = 0
    status = 0
    while i < end:
        delta, dl = _read_vlq(buf, i)
        i += dl
        abs_tick += delta
        c = buf[i]
        if c == 0xFF:             # meta
            mt = buf[i + 1]
            ml, mll = _read_vlq(buf, i + 2)
            data_at = i + 2 + mll
            if mt == 0x51 and ml == 3:
                tempo = (buf[data_at] << 16) | (buf[data_at + 1] << 8) | buf[data_at + 2]
            i = data_at + ml
            status = 0
            continue
        if c in (0xF0, 0xF7):     # SysEx — пропустить
            ml, mll = _read_vlq(buf, i + 1)
            i = i + 1 + mll + ml
            status = 0
            continue
        if c & 0x80:
            status = c
            i += 1
        # data по running status
        hi = status >> 4
        if hi in (0xC, 0xD):
            events.append((abs_tick, bytes([status, buf[i]])))
            i += 1
        else:
            events.append((abs_tick, bytes([status, buf[i], buf[i + 1]])))
            i += 2
    return events, ppqn, tempo


def build_stream(buf: bytes) -> bytes:
    events, ppqn, tempo = parse_smf(buf)
    # tempo может меняться, но HMM2-треки используют один set_tempo в начале — берём первый
    # (parse_smf вернул последний; для главного меню это один и тот же). Пересчёт тиков в кадры:
    us_per_tick = tempo / ppqn
    out = bytearray()
    prev_frame = 0
    for abs_tick, payload in events:
        frame = round(abs_tick * us_per_tick / US_PER_FRAME)
        wait = frame - prev_frame
        prev_frame = frame
        while wait > 0:
            n = min(255, wait)
            out += bytes([WAIT, n])
            wait -= n
        out += payload
    out.append(END)
    return bytes(out)


def emit_inc(stream: bytes, label: str, inc_path: Path) -> None:
    lines = [f"; Сгенерировано Source/Tools/music_pack.py — поток MIDI для Z80-плеера.",
             f"{label}:"]
    for i in range(0, len(stream), 16):
        row = ", ".join(f"#{b:02X}" for b in stream[i:i + 16])
        lines.append(f"                DEFB {row}")
    lines.append(f"{label}_SIZE EQU $ - {label}")
    inc_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="SMF → HMM2 music stream.")
    ap.add_argument("mid", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=None, help="бинарный .h2m поток")
    ap.add_argument("--inc", type=Path, default=None, help="ASM .inc с DEFB-таблицей")
    ap.add_argument("--label", default="Music_Track", help="метка для --inc")
    args = ap.parse_args()

    stream = build_stream(args.mid.read_bytes())
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(stream)
        print(f"{args.mid.name} -> {args.out} ({len(stream)} байт потока)")
    if args.inc:
        emit_inc(stream, args.label, args.inc)
        print(f"{args.mid.name} -> {args.inc} (метка {args.label}, {len(stream)} байт)")
    if not args.out and not args.inc:
        print(f"{args.mid.name}: поток {len(stream)} байт (укажите -o или --inc для записи)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
