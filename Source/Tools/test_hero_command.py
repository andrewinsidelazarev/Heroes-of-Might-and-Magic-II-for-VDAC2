#!/usr/bin/env python3
from __future__ import annotations

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT


KEMPSTON_FIRE = 0x10
MOUSE_LMB = 0x01
PATH_STATE_SEARCH = 0x01
GAME_VIEW_X = 16
GAME_VIEW_Y = 16
GAME_VIEW_X16 = 410
GAME_VIEW_Y16 = 410


def vertex_scaled(value: int) -> int:
    return (value * 8 * 16) // 5


def runtime_view_translate(view_pos: int, view_origin: int, view_offset16: int) -> int:
    return view_offset16 - vertex_scaled(view_pos - view_origin * 32)


def fail(message: str) -> None:
    raise SystemExit(f"ОШИБКА: {message}")


def update_frame(emu: HMM2FullZ80Emulator, max_steps: int = 600_000) -> None:
    emu.call(emu.sym["Input_Poll"], max_steps=300_000)
    emu.call(emu.sym["Game_Update"], max_steps=max_steps)


def wait_for_path_ready(emu: HMM2FullZ80Emulator, max_frames: int = 1024) -> int:
    path_state = emu.sym["PathState"]
    path_len = emu.sym["HeroPathLen"]
    debug_len = emu.sym["PathDebugLen"]
    for _ in range(max_frames):
        update_frame(emu)
        if emu.get_byte(path_state) == 0 and emu.get_byte(path_len) != 0:
            return emu.get_byte(path_len)
    fail(
        "поиск пути не завершился: "
        f"PathState={emu.get_byte(path_state)}, "
        f"HeroPathLen={emu.get_byte(path_len)}, "
        f"PathDebugLen={emu.get_word(debug_len)}"
    )


def wait_for_hero_at(emu: HMM2FullZ80Emulator, tile_x: int, tile_y: int, max_frames: int = 512) -> None:
    hero_x = emu.sym["HeroTileX"]
    hero_y = emu.sym["HeroTileY"]
    hero_px = emu.sym["HeroPixelX"]
    hero_py = emu.sym["HeroPixelY"]
    for _ in range(max_frames):
        if (
            emu.get_byte(hero_x) == tile_x
            and emu.get_byte(hero_y) == tile_y
            and emu.get_word(hero_px) == tile_x * 32
            and emu.get_word(hero_py) == tile_y * 32
        ):
            return
        update_frame(emu)
    fail(
        f"hero не дошел до target: tile={emu.get_byte(hero_x)},{emu.get_byte(hero_y)} "
        f"pixel={emu.get_word(hero_px)},{emu.get_word(hero_py)} вместо {tile_x},{tile_y}"
    )


def init_game() -> HMM2FullZ80Emulator:
    emu = HMM2FullZ80Emulator(ROOT)
    emu.input.mouse_x = 0
    emu.input.mouse_y = 0
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Adventure_Enter"], max_steps=12_000_000)  # Game_Init стартует в меню; входим в adventure
    return emu


def assert_blocked_target_is_not_snapped() -> None:
    emu = init_game()

    emu.reg.B = 9
    emu.reg.C = 11
    emu.call(emu.sym["Hero_SetTargetIfPassable"], max_steps=4_000_000)
    if emu.get_byte(emu.sym["PathState"]) != 0 or emu.get_byte(emu.sym["HeroPathLen"]) != 0:
        fail(
            "заблокированная цель запустила путь: "
            f"PathState={emu.get_byte(emu.sym['PathState'])}, HeroPathLen={emu.get_byte(emu.sym['HeroPathLen'])}"
        )
    hero_target = (emu.get_byte(emu.sym["HeroTargetX"]), emu.get_byte(emu.sym["HeroTargetY"]))
    if hero_target != (13, 9):
        fail(f"заблокированная цель была подменена: HeroTarget={hero_target}")


def main() -> None:
    assert_blocked_target_is_not_snapped()
    emu = init_game()

    hero_x = emu.sym["HeroTileX"]
    hero_y = emu.sym["HeroTileY"]
    target_x = emu.sym["HeroTargetX"]
    target_y = emu.sym["HeroTargetY"]
    hero_px = emu.sym["HeroPixelX"]
    hero_py = emu.sym["HeroPixelY"]
    cursor_x = emu.sym["CursorTileX"]
    cursor_y = emu.sym["CursorTileY"]
    cursor_px = emu.sym["CursorPixelX"]
    cursor_py = emu.sym["CursorPixelY"]

    if (emu.get_byte(hero_x), emu.get_byte(hero_y)) != (13, 9):
        fail(f"старт hero tile {emu.get_byte(hero_x)},{emu.get_byte(hero_y)} вместо 13,9")
    if (emu.get_byte(cursor_x), emu.get_byte(cursor_y)) != (9, 6):
        fail(f"старт cursor tile {emu.get_byte(cursor_x)},{emu.get_byte(cursor_y)} вместо 9,6")

    command_x = 12
    command_y = 9
    emu.set_byte(cursor_x, command_x)
    emu.set_byte(cursor_y, command_y)
    emu.set_word(cursor_px, GAME_VIEW_X + command_x * 32)
    emu.set_word(cursor_py, GAME_VIEW_Y + command_y * 32)

    update_frame(emu)
    if (emu.get_byte(target_x), emu.get_byte(target_y)) != (13, 9):
        fail(f"на старте сработал ложный fire: target={emu.get_byte(target_x)},{emu.get_byte(target_y)}")

    emu.input.kempston = KEMPSTON_FIRE
    update_frame(emu)
    if emu.get_byte(emu.sym["PathState"]) != PATH_STATE_SEARCH:
        fail(f"Fire не запустил поиск пути: PathState={emu.get_byte(emu.sym['PathState'])}")
    emu.input.kempston = 0
    wait_for_path_ready(emu)
    if (emu.get_byte(target_x), emu.get_byte(target_y)) != (command_x, command_y):
        fail(f"Fire не поставил target после поиска: {emu.get_byte(target_x)},{emu.get_byte(target_y)}")

    wait_for_hero_at(emu, command_x, command_y)

    emu.call(emu.sym["Render_Frame"], max_steps=4_000_000)
    marker_tx = emu.get_word(emu.sym["HERO_MARKER_TRANSLATE_X"])
    marker_ty = emu.get_word(emu.sym["HERO_MARKER_TRANSLATE_Y"])
    view_x = emu.get_word(emu.sym["ViewportPixelX"])
    view_y = emu.get_word(emu.sym["ViewportPixelY"])
    origin_x = emu.get_byte(emu.sym["ViewportOriginX"])
    origin_y = emu.get_byte(emu.sym["ViewportOriginY"])
    expected_marker_x = (
        vertex_scaled(command_x * 32 - origin_x * 32)
        + runtime_view_translate(view_x, origin_x, GAME_VIEW_X16)
    )
    expected_marker_y = (
        vertex_scaled(command_y * 32 - origin_y * 32 - 18)
        + runtime_view_translate(view_y, origin_y, GAME_VIEW_Y16)
    )
    if marker_tx != expected_marker_x or marker_ty != expected_marker_y:
        fail(
            "hero marker translate неверный: "
            f"x={marker_tx}, y={marker_ty}, ожидалось x={expected_marker_x}, y={expected_marker_y}, "
            f"viewport={view_x},{view_y}, origin={origin_x},{origin_y}"
        )

    emu.input.kempston = 0
    emu.input.mouse_buttons = MOUSE_LMB
    update_frame(emu)

    mouse_target_x = 11
    mouse_target_y = 10
    emu.input.mouse_buttons = 0
    emu.set_word(emu.sym["Input.Mouse.PositionX"], GAME_VIEW_X + mouse_target_x * 32)
    emu.set_word(emu.sym["Input.Mouse.PositionY"], GAME_VIEW_Y + mouse_target_y * 32)
    update_frame(emu)
    expected_mouse_x = (emu.get_word(emu.sym["Input.Mouse.PositionX"]) - GAME_VIEW_X) // 32
    expected_mouse_y = (emu.get_word(emu.sym["Input.Mouse.PositionY"]) - GAME_VIEW_Y) // 32
    if (expected_mouse_x, expected_mouse_y) != (mouse_target_x, mouse_target_y):
        fail(f"mouse tile расчет неверный: {expected_mouse_x},{expected_mouse_y} вместо {mouse_target_x},{mouse_target_y}")
    if emu.get_byte(emu.sym["PathState"]) != PATH_STATE_SEARCH:
        fail(f"ЛКМ не запустила поиск пути: PathState={emu.get_byte(emu.sym['PathState'])}")
    wait_for_path_ready(emu)
    if (emu.get_byte(target_x), emu.get_byte(target_y)) != (expected_mouse_x, expected_mouse_y):
        fail(
            "ЛКМ не поставила target после поиска: "
            f"target={emu.get_byte(target_x)},{emu.get_byte(target_y)} "
            f"mouse={expected_mouse_x},{expected_mouse_y}"
        )

    emu.input.mouse_buttons = MOUSE_LMB
    emu.call(emu.sym["Game_Update"], max_steps=600_000)
    emu.set_word(emu.sym["Input.Mouse.PositionX"], GAME_VIEW_X + mouse_target_x * 32 + 31)
    emu.set_word(emu.sym["Input.Mouse.PositionY"], GAME_VIEW_Y + mouse_target_y * 32 + 31)
    emu.input.mouse_buttons = 0
    emu.call(emu.sym["Game_Update"], max_steps=600_000)
    wait_for_path_ready(emu)
    if (emu.get_byte(target_x), emu.get_byte(target_y)) != (mouse_target_x, mouse_target_y):
        fail(
            f"клик около границы дал неверный target: {emu.get_byte(target_x)},{emu.get_byte(target_y)} "
            f"вместо {mouse_target_x},{mouse_target_y}"
        )

    print("OK: Fire/ЛКМ запускают постепенный поиск, hero state и marker идут к target")


if __name__ == "__main__":
    main()
