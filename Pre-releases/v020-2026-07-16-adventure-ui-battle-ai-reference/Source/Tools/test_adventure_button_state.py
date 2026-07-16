#!/usr/bin/env python3
from __future__ import annotations

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT
from shadow_ft812 import disasm_dl


MOUSE_LMB = 0x01
PATH_STATE_SEARCH = 0x01
UI_HEROMOVE_BTN_MOVE = 0
UI_HEROMOVE_BTN_INACTIVE = 2
UI_HEROMOVE_BTN_DISABLED = 3


def fail(message: str) -> None:
    raise SystemExit(f"ОШИБКА: {message}")


def update_frame(emu: HMM2FullZ80Emulator, max_steps: int = 600_000) -> None:
    emu.call(emu.sym["Input_Poll"], max_steps=300_000)
    emu.call(emu.sym["Game_Update"], max_steps=max_steps)


def release_inputs(emu: HMM2FullZ80Emulator) -> None:
    emu.input.kempston = 0
    emu.input.mouse_buttons = 0
    update_frame(emu)


def init_game() -> HMM2FullZ80Emulator:
    emu = HMM2FullZ80Emulator(ROOT)
    emu.input.mouse_x = 0
    emu.input.mouse_y = 0
    emu.input.mouse_buttons = 0
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Adventure_Enter"], max_steps=12_000_000)
    release_inputs(emu)
    return emu


def passability() -> tuple[bytes, int]:
    data = (ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.pass.bin").read_bytes()
    width = int(len(data) ** 0.5)
    if width * width != len(data):
        fail(f"не квадратная passability-карта: {len(data)} байт")
    return data, width


def find_passable_target(start_x: int, start_y: int) -> tuple[int, int]:
    data, width = passability()
    candidates = [
        (start_x, start_y + 1),
        (start_x - 1, start_y),
        (start_x + 1, start_y),
        (start_x, start_y - 1),
        (start_x - 1, start_y + 1),
        (start_x + 1, start_y + 1),
        (start_x, start_y + 2),
    ]
    for x, y in candidates:
        if 0 <= x < width and 0 <= y < width and data[y * width + x] != 0:
            return x, y
    fail(f"не найдена проходимая цель рядом с {start_x},{start_y}")


def build_path_to(emu: HMM2FullZ80Emulator, x: int, y: int, max_frames: int = 1024) -> None:
    emu.reg.B = x
    emu.reg.C = y
    emu.call(emu.sym["Hero_SetTargetIfPassable"], max_steps=4_000_000)
    for _ in range(max_frames):
        if emu.get_byte(emu.sym["PathState"]) != PATH_STATE_SEARCH:
            break
        emu.call(emu.sym["Hero_PathSearchUpdate"], max_steps=600_000)
    if emu.get_byte(emu.sym["PathState"]) == PATH_STATE_SEARCH:
        fail(f"поиск пути не завершился для {x},{y}")
    if emu.get_byte(emu.sym["HeroPathLen"]) == 0 or emu.get_byte(emu.sym["PathFound"]) == 0:
        fail(f"путь к {x},{y} не найден")
    emu.call(emu.sym["UI_ButtonsStateUpdate"], max_steps=100_000)


def source_from_table(emu: HMM2FullZ80Emulator, label: str, index: int) -> str:
    base = emu.sym[label] + index * 4
    lo = emu.get_word(base)
    hi = emu.get_word(base + 2)
    addr = ((hi & 0x00FF) << 16) | lo
    return f"#{addr:06X}"


def render_ops(emu: HMM2FullZ80Emulator):
    emu.call(emu.sym["Render_Frame"], max_steps=8_000_000)
    return disasm_dl(bytes(emu.ft.ram_dl), max_ops=4096)


def render_btn_colors(emu: HMM2FullZ80Emulator) -> dict[str, str]:
    ops = render_ops(emu)
    colors = {}
    current_color = "255, 255, 255"
    for op in ops:
        if op.name == "COLOR_RGB":
            current_color = f"{op.fields['r']}, {op.fields['g']}, {op.fields['b']}"
        elif op.name == "BITMAP_SOURCE":
            addr_val = 0
            addr_str = str(op.fields['addr'])
            if addr_str.startswith("#"):
                addr_val = int(addr_str[1:], 16)
            elif addr_str.startswith("0x"):
                addr_val = int(addr_str, 16)
            else:
                addr_val = int(addr_str)
            addr = f"#{addr_val:06X}"
            colors[addr] = current_color
    return colors


def assert_adventure_ui_transform_reset(emu: HMM2FullZ80Emulator) -> None:
    ops = render_ops(emu)
    expected = {
        "BITMAP_TRANSFORM_A": 160,
        "BITMAP_TRANSFORM_B": 0,
        "BITMAP_TRANSFORM_C": 0,
        "BITMAP_TRANSFORM_D": 0,
        "BITMAP_TRANSFORM_E": 160,
        "BITMAP_TRANSFORM_F": 0,
    }
    for i, op in enumerate(ops):
        if op.name != "BITMAP_HANDLE" or int(op.fields.get("handle", -1)) != 3:
            continue
        values: dict[str, int] = {}
        for next_op in ops[i + 1:]:
            if next_op.name == "BEGIN":
                break
            if next_op.name in expected:
                values[next_op.name] = int(next_op.fields.get("v", -1))
        if values == expected:
            return
    fail(f"AdventureUI_DL не сбрасывает полную bitmap-transform матрицу: ожидалось {expected}")


def assert_state(emu: HMM2FullZ80Emulator, expected: int, label: str) -> None:
    actual = emu.get_byte(emu.sym["UI_HeroMoveButtonState"])
    if actual != expected:
        fail(f"{label}: UI_HeroMoveButtonState={actual}, ожидалось {expected}")


def assert_color_present(colors: dict[str, str], source: str, expected_color: str, label: str) -> None:
    actual = colors.get(source.upper())
    if actual != expected_color:
        fail(f"{label}: для BITMAP_SOURCE {source} ожидался цвет {expected_color}, но получен {actual}")


def assert_color_absent(colors: dict[str, str], source: str, absent_color: str, label: str) -> None:
    actual = colors.get(source.upper())
    if actual == absent_color:
        fail(f"{label}: BITMAP_SOURCE {source} не должен иметь цвет {absent_color}")


def poll_hero_movement_pressed(emu: HMM2FullZ80Emulator) -> None:
    button_x = emu.sym["UI_BUTTON_X"] + emu.sym["UI_BUTTON_W"] + emu.sym["UI_BUTTON_W"] // 2
    button_y = emu.sym["UI_BUTTON_Y"] + emu.sym["UI_BUTTON_H"] // 2
    emu.set_word(emu.sym["Input.Mouse.PositionX"], button_x)
    emu.set_word(emu.sym["Input.Mouse.PositionY"], button_y)
    emu.input.mouse_buttons = MOUSE_LMB
    emu.call(emu.sym["Input_Poll"], max_steps=100_000)
    emu.set_byte(emu.sym["UI_ActiveButton"], 1) # Hero movement is index 1
    print("Calling UI_ButtonsStateUpdate")
    emu.call(emu.sym["UI_ButtonsStateUpdate"], max_steps=100_000)
    print("Calling UI_ButtonsPressedUpdate")
    emu.call(emu.sym["UI_ButtonsPressedUpdate"], max_steps=100_000)
    print("Finished UI_ButtonsPressedUpdate")


def get_sprite_source(emu: HMM2FullZ80Emulator, tab_label: str, index: int) -> str:
    # Ищем BITMAP_SOURCE команду внутри DL блока.
    # Таблица содержит DEFW указатели на DL блоки.
    tab_addr = emu.sym[tab_label]
    dl_addr = emu.get_word(tab_addr + index * 2)
    # Ищем внутри DL-блока команду BITMAP_SOURCE (0x01....)
    for offset in range(0, 256, 4):
        lo = emu.get_word(dl_addr + offset)
        hi = emu.get_word(dl_addr + offset + 2)
        if (hi & 0xFF00) == 0x0100:
            addr = ((hi & 0x00FF) << 16) | lo
            return f"#{addr:06X}"
    fail(f"Не найден BITMAP_SOURCE в блоке {dl_addr:04X}")
    return ""


def main() -> None:
    print("Starting init_game...")
    emu = init_game()
    print("Finished init_game!")
    assert_adventure_ui_transform_reset(emu)
    # Поскольку мы используем сопроцессор для обесцвечивания, исходный спрайт один и тот же!
    # Ищем BITMAP_SOURCE для нормального (released) и нажатого (pressed) состояний.
    normal_src = get_sprite_source(emu, "UI_BtnNormalTab", 1)
    pressed_src = get_sprite_source(emu, "UI_BtnPressedTab", 1)
    
    color_disabled = "96, 96, 96"
    color_inactive = "160, 160, 160"
    color_normal = "255, 255, 255"

    assert_state(emu, UI_HEROMOVE_BTN_DISABLED, "старт без маршрута")
    colors = render_btn_colors(emu)
    assert_color_present(colors, normal_src, color_disabled, "старт без маршрута")

    poll_hero_movement_pressed(emu)
    if emu.get_byte(emu.sym["UI_ButtonPressed"]) != 0xFF:
        fail("disabled Hero Movement не должен получать pressed-состояние")
    colors = render_btn_colors(emu)
    assert_color_present(colors, normal_src, color_disabled, "нажатие disabled")
    assert_color_absent(colors, pressed_src, color_inactive, "нажатие disabled")
    release_inputs(emu)

    start_x = emu.get_byte(emu.sym["HeroTileX"])
    start_y = emu.get_byte(emu.sym["HeroTileY"])
    target_x, target_y = find_passable_target(start_x, start_y)
    build_path_to(emu, target_x, target_y)
    assert_state(emu, UI_HEROMOVE_BTN_MOVE, "готовый маршрут с запасом хода")
    colors = render_btn_colors(emu)
    assert_color_present(colors, normal_src, color_normal, "готовый маршрут")
    assert_color_absent(colors, normal_src, color_disabled, "готовый маршрут")
    assert_color_absent(colors, normal_src, color_inactive, "готовый маршрут")

    poll_hero_movement_pressed(emu)
    actual_btn = emu.get_byte(emu.sym["UI_ButtonPressed"])
    if actual_btn != 1:
        fail(f"move Hero Movement должен получать pressed-состояние, получено: {actual_btn}")
    colors = render_btn_colors(emu)
    assert_color_present(colors, pressed_src, color_normal, "нажатие move")
    release_inputs(emu)

    emu.set_byte(emu.sym["HeroMovePoints"], 0)
    emu.call(emu.sym["UI_ButtonsStateUpdate"], max_steps=100_000)
    assert_state(emu, UI_HEROMOVE_BTN_INACTIVE, "готовый маршрут без запаса хода")
    colors = render_btn_colors(emu)
    assert_color_present(colors, normal_src, color_inactive, "готовый маршрут без запаса хода")

    poll_hero_movement_pressed(emu)
    if emu.get_byte(emu.sym["UI_ButtonPressed"]) != 1:
        fail("inactive Hero Movement должен получать pressed-состояние")
    colors = render_btn_colors(emu)
    assert_color_present(colors, pressed_src, color_inactive, "нажатие inactive")

    print("OK: Hero Movement переключает disabled/move/inactive визуальные кадры и pressed-состояние")


if __name__ == "__main__":
    main()
