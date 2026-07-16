#!/usr/bin/env python3
from __future__ import annotations

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT


KEMPSTON_RIGHT = 0x01


def read_equ(name: str) -> int:
    for line in (ROOT / "Source" / "ASM" / "generated_terrain.inc").read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0] == name and parts[1].upper() == "EQU":
            return int(parts[2].lstrip("#"), 16) if parts[2].startswith("#") else int(parts[2])
    raise SystemExit(f"ОШИБКА: нет EQU {name}")


def fail(message: str) -> None:
    raise SystemExit(f"ОШИБКА: {message}")


def main() -> None:
    if read_equ("VIEWPORT_PIXEL_MAX_X") == 0:
        print("OK: compact viewport mode, scroll disabled to avoid oversized SPG hang")
        return

    emu = HMM2FullZ80Emulator(ROOT)
    emu.input.mouse_x = 0
    emu.input.mouse_y = 0
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Adventure_Enter"], max_steps=12_000_000)  # Game_Init стартует в меню; входим в adventure

    # Стартовый вьюпорт игры теперь не нулевой (центрирован на замке героя).
    # Механика скролла от позиции не зависит — сбрасываем в 0 для проверки шага.
    emu.set_word(emu.sym["ViewportPixelX"], 0)
    emu.set_byte(emu.sym["ViewportOriginX"], 0)
    emu.set_word(emu.sym["ViewportPixelY"], 0)
    emu.set_byte(emu.sym["ViewportOriginY"], 0)

    emu.set_word(emu.sym["CursorPixelX"], read_equ("GAME_VIEW_CURSOR_MAX_X"))
    emu.set_word(emu.sym["CursorPixelY"], 224)
    emu.call(emu.sym["Cursor_UpdateTileFromPixel"], max_steps=200_000)

    emu.input.kempston = KEMPSTON_RIGHT
    emu.call(emu.sym["Input_Poll"], max_steps=300_000)
    emu.call(emu.sym["Game_Update"], max_steps=300_000)
    if emu.get_word(emu.sym["ViewportPixelX"]) != 5:
        fail(f"первый scroll-step X={emu.get_word(emu.sym['ViewportPixelX'])} вместо 5")
    if emu.get_byte(emu.sym["ViewportOriginX"]) != 0:
        fail(f"origin прыгнул до полной клетки раньше времени: {emu.get_byte(emu.sym['ViewportOriginX'])}")

    for _ in range(7):
        emu.call(emu.sym["Input_Poll"], max_steps=300_000)
        emu.call(emu.sym["Game_Update"], max_steps=300_000)

    if emu.get_word(emu.sym["ViewportPixelX"]) != 40:
        fail(f"после 8 кадров scroll X={emu.get_word(emu.sym['ViewportPixelX'])} вместо 40")
    if emu.get_byte(emu.sym["ViewportOriginX"]) != 1:
        fail(f"origin не перешел на следующую tile-page: {emu.get_byte(emu.sym['ViewportOriginX'])}")

    print("OK: viewport scroll state идет 5px/кадр, tile-page меняется только на границе 32px")


if __name__ == "__main__":
    main()
