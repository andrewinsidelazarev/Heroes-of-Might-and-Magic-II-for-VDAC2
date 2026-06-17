#!/usr/bin/env python3
from __future__ import annotations

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT


KEMPSTON_RIGHT = 0x01
KEMPSTON_DOWN = 0x04
GAME_VIEW_X = 16
GAME_VIEW_Y = 16


def vertex_scaled(value: int) -> int:
    return (value * 8 * 16) // 5


def fail(message: str) -> None:
    raise SystemExit(f"ОШИБКА: {message}")


def main() -> None:
    emu = HMM2FullZ80Emulator(ROOT)
    emu.input.mouse_x = 0
    emu.input.mouse_y = 0
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Adventure_Enter"], max_steps=12_000_000)  # Game_Init стартует в меню; входим в adventure

    x_addr = emu.sym["CursorTileX"]
    y_addr = emu.sym["CursorTileY"]
    px_addr = emu.sym["CursorPixelX"]
    py_addr = emu.sym["CursorPixelY"]
    delay_addr = emu.sym["CursorMoveCooldown"]
    mouse_x_addr = emu.sym["Input.Mouse.PositionX"]
    mouse_y_addr = emu.sym["Input.Mouse.PositionY"]

    if emu.get_byte(x_addr) != 9 or emu.get_byte(y_addr) != 6:
        fail(f"старт tile cursor {emu.get_byte(x_addr)},{emu.get_byte(y_addr)} вместо 9,6")
    if emu.get_word(px_addr) != 320 or emu.get_word(py_addr) != 224:
        fail(f"старт pixel cursor {emu.get_word(px_addr)},{emu.get_word(py_addr)} вместо 320,224")
    emu.input.mouse_x = 96
    emu.input.mouse_y = 192
    emu.call(emu.sym["Input_Poll"], max_steps=300_000)
    emu.call(emu.sym["Game_Update"], max_steps=300_000)
    if emu.get_word(px_addr) != 416 or emu.get_word(py_addr) != 304:
        fail(
            "мышь не обновила pixel cursor: "
            f"pixel={emu.get_word(px_addr)},{emu.get_word(py_addr)} "
            f"tile={emu.get_byte(x_addr)},{emu.get_byte(y_addr)} "
            f"mouse_pos={emu.get_word(mouse_x_addr)},{emu.get_word(mouse_y_addr)} "
            f"mouse_ports={[p for p in emu.ports_in if p[0] in (0xFBDF, 0xFFDF, 0xFADF)]} "
            f"ports_in={emu.ports_in[-16:]}"
        )
    if emu.get_byte(x_addr) != 12 or emu.get_byte(y_addr) != 9:
        fail(f"мышь дала неверный tile: {emu.get_byte(x_addr)},{emu.get_byte(y_addr)}")
    emu.input.mouse_x = 0
    emu.input.mouse_y = 0
    emu.call(emu.sym["Input_Poll"], max_steps=300_000)
    emu.call(emu.sym["Game_Update"], max_steps=300_000)
    if emu.get_word(px_addr) != 320 or emu.get_word(py_addr) != 240:
        fail(f"мышь не вернула pixel cursor в центр: {emu.get_word(px_addr)},{emu.get_word(py_addr)}")
    if emu.get_byte(x_addr) != 9 or emu.get_byte(y_addr) != 7:
        fail(f"мышь не вернула tile cursor в центр: {emu.get_byte(x_addr)},{emu.get_byte(y_addr)}")
    emu.input.mouse_x = 32
    emu.input.kempston = KEMPSTON_RIGHT
    emu.call(emu.sym["Input_Poll"], max_steps=200_000)
    emu.call(emu.sym["Game_Update"], max_steps=200_000)
    if emu.get_word(px_addr) != 325 or emu.get_word(py_addr) != 240:
        fail(
            "right не сдвинул pixel cursor на 5px или был перебит мышью: "
            f"{emu.get_word(px_addr)},{emu.get_word(py_addr)}"
        )
    if emu.get_byte(x_addr) != 9 or emu.get_byte(y_addr) != 7:
        fail(f"right ошибочно прыгнул tile cursor: {emu.get_byte(x_addr)},{emu.get_byte(y_addr)}")
    if emu.get_byte(delay_addr) != 0:
        fail(f"right выставил неверный cooldown: {emu.get_byte(delay_addr)}")

    emu.input.mouse_x = 0
    emu.input.kempston = 0
    emu.call(emu.sym["Input_Poll"], max_steps=200_000)
    emu.call(emu.sym["Game_Update"], max_steps=200_000)
    if emu.get_byte(delay_addr) != 0:
        fail(f"cooldown не сброшен после отпускания: {emu.get_byte(delay_addr)}")

    emu.input.kempston = KEMPSTON_DOWN
    emu.call(emu.sym["Input_Poll"], max_steps=200_000)
    emu.call(emu.sym["Game_Update"], max_steps=200_000)
    if emu.get_word(px_addr) != 325 or emu.get_word(py_addr) != 245:
        fail(f"down не сдвинул pixel cursor на 5px: {emu.get_word(px_addr)},{emu.get_word(py_addr)}")
    if emu.get_byte(x_addr) != 9 or emu.get_byte(y_addr) != 7:
        fail(f"down ошибочно прыгнул tile cursor: {emu.get_byte(x_addr)},{emu.get_byte(y_addr)}")
    if emu.get_byte(delay_addr) != 0:
        fail(f"down выставил неверный cooldown: {emu.get_byte(delay_addr)}")

    emu.call(emu.sym["Render_Frame"], max_steps=4_000_000)
    tx = emu.get_word(emu.sym["CURSOR_TRANSLATE_X"])
    ty = emu.get_word(emu.sym["CURSOR_TRANSLATE_Y"])
    if tx != vertex_scaled(325) or ty != vertex_scaled(245):
        fail(f"translate неверный: x={tx}, y={ty}")
    print("OK: Kempston Mouse двигает пиксельно, cursor FT812 translate совпадает")


if __name__ == "__main__":
    main()
