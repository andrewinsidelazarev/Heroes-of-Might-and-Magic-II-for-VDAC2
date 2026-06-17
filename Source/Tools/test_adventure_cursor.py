#!/usr/bin/env python3
from __future__ import annotations

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT
from shadow_ft812 import disasm_dl


PATH_STATE_SEARCH = 0x01


def fail(message: str) -> None:
    raise SystemExit(f"ОШИБКА: {message}")


def cursor_source(emu: HMM2FullZ80Emulator, index: int) -> str:
    base = emu.sym["CursorSpriteTable"] + index * emu.sym["CURSOR_TABLE_ENTRY_SIZE"]
    hi = emu.get_byte(base)
    lo = emu.get_byte(base + 1)
    mid = emu.get_byte(base + 2)
    return f"#{(hi << 16) | (mid << 8) | lo:06X}"


def render_sources(emu: HMM2FullZ80Emulator) -> list[str]:
    emu.call(emu.sym["Render_Frame"], max_steps=8_000_000)
    ops = disasm_dl(bytes(emu.ft.ram_dl), max_ops=4096)
    return [op.fields.get("addr") for op in ops if op.name == "BITMAP_SOURCE"]


def set_cursor_tile(emu: HMM2FullZ80Emulator, x: int, y: int) -> None:
    emu.set_byte(emu.sym["CursorTileX"], x)
    emu.set_byte(emu.sym["CursorTileY"], y)
    emu.set_word(emu.sym["CursorPixelX"], min(x * 32, 624))
    emu.set_word(emu.sym["CursorPixelY"], min(y * 32, 464))


def build_path_to(emu: HMM2FullZ80Emulator, x: int, y: int, max_frames: int = 1024) -> None:
    emu.reg.B = x
    emu.reg.C = y
    emu.call(emu.sym["Hero_SetTargetIfPassable"], max_steps=4_000_000)
    for _ in range(max_frames):
        if emu.get_byte(emu.sym["PathState"]) != PATH_STATE_SEARCH:
            return
        emu.call(emu.sym["Hero_PathSearchUpdate"], max_steps=600_000)
    fail(f"поиск пути не завершился для {x},{y}")


def assert_cursor_index(emu: HMM2FullZ80Emulator, expected: int, label: str) -> None:
    emu.call(emu.sym["Cursor_UpdateTheme"], max_steps=100_000)
    actual = emu.get_byte(emu.sym["CursorSpriteIndex"])
    if actual != expected:
        fail(f"{label}: CursorSpriteIndex={actual}, ожидался {expected}")


def main() -> None:
    emu = HMM2FullZ80Emulator(ROOT)
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Adventure_Enter"], max_steps=12_000_000)  # Game_Init стартует в меню; входим в adventure

    pointer_index = emu.sym["CURSOR_POINTER_INDEX"]
    move_index = emu.sym["CURSOR_MOVE_BASE_INDEX"]
    pointer_addr = cursor_source(emu, pointer_index)
    move_addr = cursor_source(emu, move_index)
    if pointer_addr == move_addr:
        fail("pointer и move cursor используют один bitmap source")

    assert_cursor_index(emu, pointer_index, "старт")
    sources = render_sources(emu)
    if pointer_addr not in sources:
        fail(f"стартовый DL не использует ADVMCO pointer {pointer_addr}")

    build_path_to(emu, 9, 13)
    if emu.get_byte(emu.sym["HeroPathLen"]) == 0 or emu.get_byte(emu.sym["PathFound"]) == 0:
        fail("достижимый путь 9,13 не найден")
    set_cursor_tile(emu, 9, 13)
    assert_cursor_index(emu, move_index, "достижимая цель")
    sources = render_sources(emu)
    if move_addr not in sources:
        fail(f"DL для достижимой цели не использует COLOR_CURSOR_ADVENTURE_MAP move {move_addr}")

    build_path_to(emu, 6, 16)
    if emu.get_byte(emu.sym["HeroPathLen"]) != 0 or emu.get_byte(emu.sym["PathFound"]) != 0:
        fail("недостижимый путь 6,16 оставил найденный маршрут")
    set_cursor_tile(emu, 6, 16)
    assert_cursor_index(emu, pointer_index, "недостижимая цель")
    sources = render_sources(emu)
    if pointer_addr not in sources or move_addr in sources:
        fail("DL для недостижимой цели должен использовать pointer, а не move cursor")

    print("OK: adventure cursor переключается pointer/move/pointer по найденному и недостижимому пути")


if __name__ == "__main__":
    main()
