#!/usr/bin/env python3
from __future__ import annotations

from test_hero_command import (
    KEMPSTON_FIRE,
    find_passable_target,
    init_game,
    release_inputs,
    screen_for_tile,
    update_frame,
    wait_for_path_ready,
)


STATE_KEYS_BYTE = (
    "HeroTileX",
    "HeroTileY",
    "HeroStepX",
    "HeroStepY",
    "HeroTargetX",
    "HeroTargetY",
    "HeroMoveActive",
    "HeroPathLen",
    "HeroPathIndex",
    "PathFound",
    "PathState",
    "HeroMovePoints",
    "UI_HeroMoveButtonState",
    "CursorTileX",
    "CursorTileY",
    "CursorSpriteIndex",
)
STATE_KEYS_WORD = (
    "HeroPixelX",
    "HeroPixelY",
    "CursorPixelX",
    "CursorPixelY",
    "ViewportPixelX",
    "ViewportPixelY",
)


def dump_state(emu, frame: str) -> None:
    byte_part = " ".join(f"{k}={emu.get_byte(emu.sym[k])}" for k in STATE_KEYS_BYTE)
    word_part = " ".join(f"{k}={emu.get_word(emu.sym[k])}" for k in STATE_KEYS_WORD)
    print(f"{frame}: {byte_part} {word_part}")


def main() -> int:
    emu = init_game()
    start_x = emu.get_byte(emu.sym["HeroTileX"])
    start_y = emu.get_byte(emu.sym["HeroTileY"])
    target_x, target_y = find_passable_target(emu, start_x, start_y)
    sx, sy = screen_for_tile(emu, target_x, target_y)
    print(f"start={start_x},{start_y} target={target_x},{target_y} screen={sx},{sy}")

    release_inputs(emu)
    emu.set_byte(emu.sym["CursorTileX"], target_x)
    emu.set_byte(emu.sym["CursorTileY"], target_y)
    emu.set_word(emu.sym["CursorPixelX"], sx)
    emu.set_word(emu.sym["CursorPixelY"], sy)
    emu.input.kempston = KEMPSTON_FIRE
    update_frame(emu)
    emu.input.kempston = 0
    path_len = wait_for_path_ready(emu, max_frames=128)
    dump_state(emu, "path-ready")
    print(f"path_len={path_len}")

    release_inputs(emu)
    emu.set_byte(emu.sym["CursorTileX"], target_x)
    emu.set_byte(emu.sym["CursorTileY"], target_y)
    emu.set_word(emu.sym["CursorPixelX"], sx)
    emu.set_word(emu.sym["CursorPixelY"], sy)
    emu.input.kempston = KEMPSTON_FIRE
    update_frame(emu)
    emu.input.kempston = 0
    dump_state(emu, "move-start")

    previous = None
    stuck_frames = 0
    for frame in range(1, 96):
        update_frame(emu)
        current = (
            emu.get_word(emu.sym["HeroPixelX"]),
            emu.get_word(emu.sym["HeroPixelY"]),
            emu.get_byte(emu.sym["HeroMoveActive"]),
            emu.get_byte(emu.sym["HeroPathLen"]),
            emu.get_byte(emu.sym["PathFound"]),
        )
        dump_state(emu, f"move-{frame:03d}")
        if current == previous:
            stuck_frames += 1
        else:
            stuck_frames = 0
        previous = current
        if emu.get_byte(emu.sym["HeroMoveActive"]) == 0:
            print(f"movement-stopped frame={frame}")
            break
        if stuck_frames >= 8:
            print(f"movement-stuck frame={frame}")
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
