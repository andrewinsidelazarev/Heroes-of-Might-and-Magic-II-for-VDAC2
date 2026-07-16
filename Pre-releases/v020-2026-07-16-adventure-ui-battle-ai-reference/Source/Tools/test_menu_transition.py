#!/usr/bin/env python3
"""Регрессия диспетчера сцен: старт в ГЛАВНОМ МЕНЮ, переход New Game -> adventure.

Проверяет:
  1. Game_Init стартует в GAME_MODE_MENU (3), а не сразу в adventure.
  2. Клик ВНЕ зоны New Game не вызывает перехода.
  3. Клик В зоне New Game (логич. 440..610 × 200..250) переключает на adventure
     (GAME_MODE_ADVENTURE=0) через Adventure_Enter (ленивая загрузка карты).
"""
from __future__ import annotations

import sys

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT, attach_hmm2_shadow

MOUSE_LMB = 0x01          # порт #FADF: бит LBUTTON установлен = ОТПУЩЕНА (линия инверсна)
MOUSE_PRESS = 0x00        # бит сброшен = НАЖАТА
GAME_MODE_ADVENTURE = 0
GAME_MODE_MENU = 3


def fail(msg: str) -> None:
    print(f"ОШИБКА: {msg}")
    sys.exit(1)


def click_at(emu, x: int, y: int) -> None:
    """Полный клик: отпущено (сброс latch) -> нажато в точке -> Game_Update."""
    emu.input.mouse_buttons = MOUSE_LMB
    emu.set_word(emu.sym["Input.Mouse.PositionX"], x)
    emu.set_word(emu.sym["Input.Mouse.PositionY"], y)
    emu.call(emu.sym["Game_Update"], max_steps=2_000_000)   # отпущено -> latch=0
    emu.input.mouse_buttons = MOUSE_PRESS
    emu.call(emu.sym["Game_Update"], max_steps=14_000_000)  # нажато -> hit-test (+ возможный Adventure_Enter)


def main() -> int:
    emu = HMM2FullZ80Emulator(ROOT)
    attach_hmm2_shadow(emu)
    emu.call(emu.sym["Platform_Init"], max_steps=4_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=600_000_000)  # включает стрим HMM2MENU.PAK с SD (payload ~730КБ)

    gm = emu.get_byte(emu.sym["GameMode"])
    if gm != GAME_MODE_MENU:
        fail(f"старт не в меню: GameMode={gm} (ожидалось {GAME_MODE_MENU})")
    print("OK: Game_Init стартует в главном меню")

    # Клик ВНЕ зоны New Game (левый верх) — перехода быть не должно.
    click_at(emu, 100, 100)
    gm = emu.get_byte(emu.sym["GameMode"])
    if gm != GAME_MODE_MENU:
        fail(f"клик вне зоны не должен переключать сцену: GameMode={gm}")
    print("OK: клик вне зоны New Game не вызывает перехода")

    # Клик В зоне New Game (центр зоны 440..610 × 200..250) -> adventure.
    click_at(emu, 525, 225)
    gm = emu.get_byte(emu.sym["GameMode"])
    if gm != GAME_MODE_ADVENTURE:
        fail(f"клик New Game не переключил на adventure: GameMode={gm}")
    print("OK: клик New Game -> adventure (Adventure_Enter)")

    # Sanity: карта загружена (HeroTileX выставлен Adventure_Enter/Hero_InitPosition).
    hero_x = emu.get_byte(emu.sym["HeroTileX"])
    if hero_x == 0:
        fail("Adventure_Enter не инициализировал героя (HeroTileX=0)")
    print(f"OK: adventure инициализирован (HeroTileX={hero_x})")
    print("=== test_menu_transition: PASS ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
