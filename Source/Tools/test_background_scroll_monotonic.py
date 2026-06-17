#!/usr/bin/env python3
from __future__ import annotations

import re

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT


KEMPSTON_RIGHT = 0x01


def fail(message: str) -> None:
    raise SystemExit(f"ОШИБКА: {message}")


def u24_at(emu: HMM2FullZ80Emulator, addr: int) -> int:
    lo = emu.get_word(addr)
    hi = emu.get_byte(addr + 2)
    return lo | (hi << 16)


def signed_word(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


def scaled_vertex_units(pixel: int) -> int:
    return (pixel * 128) // 5


def read_equ(path, name: str) -> int:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"^\s*{re.escape(name)}\s+EQU\s+(.+?)\s*$", text, re.MULTILINE)
    if not match:
        fail(f"нет EQU {name}")
    value = match.group(1).strip()
    return int(value[1:], 16) if value.startswith("#") else int(value)


TERRAIN_INC = ROOT / "Source" / "ASM" / "generated_terrain.inc"
GAME_VIEW_X16 = read_equ(TERRAIN_INC, "GAME_VIEW_X16")
GAME_VIEW_Y16 = read_equ(TERRAIN_INC, "GAME_VIEW_Y16")


def expected_object_translate(viewport_pixel: int, origin_tile: int, game_view16: int) -> int:
    return game_view16 + scaled_vertex_units(origin_tile * 32) - scaled_vertex_units(viewport_pixel)


def main() -> None:
    emu = HMM2FullZ80Emulator(ROOT)
    emu.input.mouse_x = 0
    emu.input.mouse_y = 0
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Adventure_Enter"], max_steps=12_000_000)  # Game_Init стартует в меню; входим в adventure

    emu.set_word(emu.sym["CursorPixelX"], 624)
    emu.set_word(emu.sym["CursorPixelY"], 224)
    emu.call(emu.sym["Cursor_UpdateTileFromPixel"], max_steps=200_000)
    emu.input.kempston = KEMPSTON_RIGHT

    last_world = None
    for frame in range(160):
        emu.call(emu.sym["Input_Poll"], max_steps=300_000)
        emu.call(emu.sym["Game_Update"], max_steps=300_000)
        emu.call(emu.sym["Render_Frame"], max_steps=12_000_000)

        viewport_x = emu.get_word(emu.sym["ViewportPixelX"])
        if "BG_DXT_MASK_C_LOW" in emu.sym:
            anchor = emu.get_byte(emu.sym["BackgroundDxtOriginX"]) * 32
            mask_c = u24_at(emu, emu.sym["BG_DXT_MASK_C_LOW"])
            local = mask_c >> 8
            world = anchor + local
        else:
            origin = emu.get_byte(emu.sym["ViewportOriginX"]) * 32
            # В тайловой модели фон привязан к origin-тайлу, а pixel remainder
            # уходит в FT812 VERTEX_TRANSLATE с nearest upscale 8/5.
            local = viewport_x & 31
            world = origin + local

        if world != viewport_x:
            fail(f"frame {frame}: фон смотрит world_x={world}, камера={viewport_x}")
        origin_x = emu.get_byte(emu.sym["ViewportOriginX"])
        obj_tx = signed_word(emu.get_word(emu.sym["RuntimeDL_ObjectTranslateX_Low"]))
        expected_tx = expected_object_translate(viewport_x, origin_x, GAME_VIEW_X16)
        if obj_tx != expected_tx:
            fail(f"frame {frame}: object translate X={obj_tx}, ожидается {expected_tx}")

        viewport_y = emu.get_word(emu.sym["ViewportPixelY"])
        origin_y = emu.get_byte(emu.sym["ViewportOriginY"])
        obj_ty = signed_word(emu.get_word(emu.sym["RuntimeDL_ObjectTranslateY_Low"]))
        expected_ty = expected_object_translate(viewport_y, origin_y, GAME_VIEW_Y16)
        if obj_ty != expected_ty:
            fail(f"frame {frame}: object translate Y={obj_ty}, ожидается {expected_ty}")

        if last_world is not None and world < last_world:
            fail(f"frame {frame}: фон пошёл назад {last_world}->{world}")
        last_world = world

    print("OK: background scroll transform монотонен и совпадает с ViewportPixelX")


if __name__ == "__main__":
    main()
