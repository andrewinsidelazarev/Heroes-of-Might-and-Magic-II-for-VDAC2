#!/usr/bin/env python3
"""Регрессия MIDI-плеера (music.asm): UART bit-bang на AY → SAM2695 + покадровый плеер.

Эмулятор декодирует поток битов на AY port A bit2 (UART 31250) обратно в MIDI-байты
(tsconf_ft812_sim._decode_midi_bit). Тайминг (31250 бод) проверяется НЕ здесь — только на
железе; здесь проверяется КОРРЕКТНОСТЬ потока байт (логика плеера и bit-bang-кодирования).

  1. Music_GMReset → ровно GM System On SysEx (F0 7E 7F 09 01 F7) — UART кодирует байты верно.
  2. Music_Tick проигрывает покадровый поток: WAIT-паузы и MIDI-события в правильном порядке.
"""
from __future__ import annotations

import sys

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT, attach_hmm2_shadow

GM_ON = bytes([0xF0, 0x7E, 0x7F, 0x09, 0x01, 0xF7])

# Резидентные адреса состояния плеера (main.asm EQU).
MUSIC_ACTIVE = 0x426B
MUSIC_WAIT = 0x426C
MUSIC_PTR = 0x426D
MUSIC_START = 0x426F


def fail(msg: str) -> None:
    print(f"ОШИБКА: {msg}")
    sys.exit(1)


def reset_midi(emu):
    emu.midi_bytes = bytearray()
    emu._midi_state = 0


def main() -> int:
    emu = HMM2FullZ80Emulator(ROOT)
    attach_hmm2_shadow(emu)
    emu.call(emu.sym["Platform_Init"], max_steps=4_000_000)
    emu.call(emu.sym["Music_InitPort"], max_steps=200_000)   # AY port A → выход (иначе MIDI не идёт)

    # 1) GM System On через UART.
    reset_midi(emu)
    emu.call(emu.sym["Music_GMReset"], max_steps=2_000_000)
    got = bytes(getattr(emu, "midi_bytes", b""))
    if got != GM_ON:
        fail(f"GM On: декодировано {got.hex()} != {GM_ON.hex()}")
    print("OK: Music_GMReset → GM System On (UART bit-bang кодирует байты верно)")

    # 2) Покадровый плеер на рукотворном потоке.
    # WAIT 2 | note-on ch0 (90 3C 64) | WAIT 3 | note-off ch0 (80 3C 00) | END
    stream = bytes([0xF8, 2, 0x90, 0x3C, 0x64, 0xF8, 3, 0x80, 0x3C, 0x00, 0xFF])
    PAGE = 0xA4
    BASE = 0xC000
    emu.out_port(0x13AF, PAGE)                 # slot3 (#C000) → свободная страница #A4
    for i, b in enumerate(stream):
        emu.set_byte(BASE + i, b)

    emu.set_byte(MUSIC_ACTIVE, 1)
    emu.set_byte(MUSIC_WAIT, 0)
    emu.set_word(MUSIC_PTR, BASE)
    emu.set_word(MUSIC_START, BASE)
    reset_midi(emu)

    # WAIT 2 → два тика-паузы, на третьем шлётся note-on; затем WAIT 3, потом note-off.
    for _ in range(8):
        emu.call(emu.sym["Music_Tick"], max_steps=500_000)

    got = bytes(emu.midi_bytes)
    exp = bytes([0x90, 0x3C, 0x64, 0x80, 0x3C, 0x00])
    if got != exp:
        fail(f"плеер: декодировано {got.hex()} != ожидалось {exp.hex()}")
    if emu.get_byte(MUSIC_ACTIVE) != 1:
        fail("после END плеер должен оставаться активным (зацикливание)")
    print("OK: Music_Tick — поток проигран (WAIT-паузы + note-on/off в порядке)")

    # 3) Интеграция: Game_Init (GM reset + Music_Start) + кадры меню → музыка реально играет.
    emu2 = HMM2FullZ80Emulator(ROOT)
    attach_hmm2_shadow(emu2)
    emu2.call(emu2.sym["Platform_Init"], max_steps=4_000_000)
    emu2.call(emu2.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu2.call(emu2.sym["Input_Init"], max_steps=200_000)
    reset_midi(emu2)
    emu2.call(emu2.sym["Game_Init"], max_steps=600_000_000)   # GM reset + меню + Music_Start
    got = bytes(getattr(emu2, "midi_bytes", b""))
    if got[:6] != GM_ON:
        fail(f"Game_Init: музыка не инициализирована GM On (начало {got[:6].hex()})")
    for _ in range(180):                                       # ~3 сек кадров меню
        emu2.call(emu2.sym["Game_Update"], max_steps=3_000_000)
    got = bytes(emu2.midi_bytes)
    after = got[6:]
    midi_events = sum(1 for b in after if 0x80 <= b <= 0xEF)
    if midi_events < 8:
        fail(f"музыка не играет в меню: после GM On только {midi_events} status-байт")
    print(f"OK: интеграция — музыка играет в меню (GM On + {midi_events} MIDI-событий MIDI0042)")

    print("=== test_music: PASS ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
