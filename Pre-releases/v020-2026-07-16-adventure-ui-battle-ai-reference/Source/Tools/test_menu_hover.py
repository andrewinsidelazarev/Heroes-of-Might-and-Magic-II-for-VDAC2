#!/usr/bin/env python3
"""Регрессия hover/pressed/анимации главного меню (по game_mainmenu.cpp).

Проверяет, что DL главного меню строится динамически по состоянию мыши:
  1. База (мышь вне кнопок): каждая кнопка рисуется released-кадром; фонарь — кадр 0.
  2. Hover (мышь над New Game, ЛКМ отпущена): New Game рисуется hover-кадром (base+1),
     остальные — released; MenuHoverIndex=0; перехода в adventure НЕТ.
  3. Pressed (мышь над Quit, ЛКМ нажата): Quit рисуется pressed-кадром (base+2); Quit —
     заглушка (аппаратно неактивен), перехода НЕТ, GameMode остаётся MENU.
  4. Анимация фонаря: после нескольких Game_Update кадр фонаря (BITMAP_SOURCE) меняется.

Сверка идёт по адресам BITMAP_SOURCE в собранном RAM_DL — детерминированно, без
растеризации. Адреса/зоны парсятся из generated_menu.inc.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT, attach_hmm2_shadow
from shadow_ft812 import disasm_dl

MOUSE_RELEASED = 0x01     # порт #FADF: бит LBUTTON установлен = ОТПУЩЕНА (линия инверсна)
MOUSE_PRESSED = 0x00      # бит сброшен = НАЖАТА
GAME_MODE_MENU = 3
INC = ROOT / "Source" / "ASM" / "generated_menu.inc"


def fail(msg: str) -> None:
    print(f"ОШИБКА: {msg}")
    sys.exit(1)


def parse_inc():
    """Адреса DL-блоков кнопок (rel/hover/pressed) и зоны кнопок из generated_menu.inc."""
    text = INC.read_text(encoding="utf-8")
    btn = {}
    for name in ("NEW_GAME", "LOAD_GAME", "HIGH_SCORES", "CREDITS", "QUIT"):
        addrs = {}
        for state in ("REL", "HOVER", "PRESSED"):
            m = re.search(rf"MenuBtn_{name}_{state}_DL:\s*\n\s*FT_BITMAP_SOURCE\s+#([0-9A-Fa-f]+)", text)
            if not m:
                fail(f"нет адреса MenuBtn_{name}_{state}_DL в inc")
            addrs[state] = int(m.group(1), 16)
        btn[name] = addrs
    # зоны: строки DEFW x0,y0,x1,y1 после MenuButtonZones (по порядку кнопок)
    zones = []
    in_zones = False
    for line in text.splitlines():
        if line.strip().startswith("MenuButtonZones:"):
            in_zones = True
            continue
        if in_zones:
            m = re.match(r"\s*DEFW\s+(\d+),\s*(\d+),\s*(\d+),\s*(\d+)", line)
            if m:
                zones.append(tuple(int(g) for g in m.groups()))
            elif line.strip() and not line.strip().startswith(";"):
                break
    # адрес базового кадра фонаря
    m = re.search(r"MenuLanternBase_DL:\s*\n\s*FT_BITMAP_SOURCE\s+#([0-9A-Fa-f]+)", text)
    lantern_base = int(m.group(1), 16) if m else None
    # адреса кадров анимации фонаря
    lantern_frames = [int(a, 16) for a in re.findall(r"MenuLantern_\d+_DL:\s*\n\s*FT_BITMAP_SOURCE\s+#([0-9A-Fa-f]+)", text)]
    # подсветка двери + зона настроек
    m = re.search(r"MenuDoor_DL:\s*\n\s*FT_BITMAP_SOURCE\s+#([0-9A-Fa-f]+)", text)
    door_addr = int(m.group(1), 16) if m else None
    m = re.search(r"MenuSettingsZone:\s*DEFW\s+(\d+),\s*(\d+),\s*(\d+),\s*(\d+)", text)
    settings_zone = tuple(int(g) for g in m.groups()) if m else None
    return btn, zones, lantern_base, lantern_frames, door_addr, settings_zone


def zone_center(zone):
    x0, y0, x1, y1 = zone
    return ((x0 + x1) // 2, (y0 + y1) // 2)


def dl_bitmap_sources(emu):
    """Список адресов BITMAP_SOURCE в собранном RAM_DL (после Render_Frame)."""
    ops = disasm_dl(bytes(emu.ft.ram_dl[:0x2000]), max_ops=4096)
    srcs = []
    for op in ops:
        if op.name == "BITMAP_SOURCE":
            addr = op.fields["addr"]
            srcs.append(int(addr.lstrip("#"), 16) if isinstance(addr, str) else int(addr))
    return srcs


def render(emu, regs):
    regs.tick_frame(emu.ft.ram_dl)
    emu.call(emu.sym["Render_Frame"], max_steps=8_000_000)
    return dl_bitmap_sources(emu)


def set_mouse(emu, x, y, pressed):
    emu.input.mouse_buttons = MOUSE_PRESSED if pressed else MOUSE_RELEASED
    emu.set_word(emu.sym["Input.Mouse.PositionX"], x)
    emu.set_word(emu.sym["Input.Mouse.PositionY"], y)


def main() -> int:
    btn, zones, lantern_base, lantern_frames, door_addr, settings_zone = parse_inc()
    names = ["NEW_GAME", "LOAD_GAME", "HIGH_SCORES", "CREDITS", "QUIT"]

    emu = HMM2FullZ80Emulator(ROOT)
    regs = attach_hmm2_shadow(emu)
    emu.call(emu.sym["Platform_Init"], max_steps=4_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=600_000_000)   # стрим HMM2MENU.PAK (~730КБ)

    if emu.get_byte(emu.sym["GameMode"]) != GAME_MODE_MENU:
        fail("старт не в меню")

    # 1) База: мышь вне кнопок (угол), ЛКМ отпущена.
    set_mouse(emu, 5, 5, pressed=False)
    emu.call(emu.sym["Game_Update"], max_steps=2_000_000)
    if emu.get_byte(emu.sym["MenuHoverIndex"]) != 0xFF:
        fail(f"вне кнопок MenuHoverIndex={emu.get_byte(emu.sym['MenuHoverIndex'])} (ожидалось 0xFF)")
    srcs = render(emu, regs)
    for name in names:
        if btn[name]["REL"] not in srcs:
            fail(f"база: нет released-кадра {name} (#{btn[name]['REL']:06X}) в DL")
        if btn[name]["HOVER"] in srcs:
            fail(f"база: hover-кадр {name} не должен присутствовать")
    base_lantern = [s for s in srcs if s == lantern_base or s in lantern_frames]
    print(f"OK: база — все 5 кнопок released; фонарь-источников в DL: {len(base_lantern)}")

    # 2) Hover над New Game (ЛКМ отпущена) → New Game hover, остальные released, без перехода.
    cx, cy = zone_center(zones[0])
    set_mouse(emu, cx, cy, pressed=False)
    emu.call(emu.sym["Game_Update"], max_steps=2_000_000)
    if emu.get_byte(emu.sym["MenuHoverIndex"]) != 0:
        fail(f"над New Game MenuHoverIndex={emu.get_byte(emu.sym['MenuHoverIndex'])} (ожидалось 0)")
    if emu.get_byte(emu.sym["GameMode"]) != GAME_MODE_MENU:
        fail("hover без нажатия не должен переходить в adventure")
    srcs = render(emu, regs)
    if btn["NEW_GAME"]["HOVER"] not in srcs:
        fail("hover: нет hover-кадра New Game в DL")
    if btn["NEW_GAME"]["REL"] in srcs:
        fail("hover: released-кадр New Game не должен присутствовать при наведении")
    for name in names[1:]:
        if btn[name]["REL"] not in srcs:
            fail(f"hover: {name} должен оставаться released")
    print("OK: hover над New Game — кадр base+1, остальные released, перехода нет")

    # 3) Pressed над Load Game (заглушка, НЕ Quit) → Load pressed-кадр, без перехода.
    lx, ly = zone_center(zones[1])
    set_mouse(emu, lx, ly, pressed=False)
    emu.call(emu.sym["Game_Update"], max_steps=2_000_000)   # отпущено → latch=0
    set_mouse(emu, lx, ly, pressed=True)
    emu.call(emu.sym["Game_Update"], max_steps=2_000_000)   # нажато над Load → pressed, без перехода
    if emu.get_byte(emu.sym["GameMode"]) != GAME_MODE_MENU:
        fail("нажатие Load Game не должно переходить (экрана пока нет)")
    if emu.get_byte(emu.sym["MenuLmbDown"]) != 1:
        fail("MenuLmbDown должен быть 1 при зажатой ЛКМ")
    srcs = render(emu, regs)
    if btn["LOAD_GAME"]["PRESSED"] not in srcs:
        fail("pressed: нет pressed-кадра Load Game в DL")
    if btn["LOAD_GAME"]["REL"] in srcs or btn["LOAD_GAME"]["HOVER"] in srcs:
        fail("pressed: Load Game не должен быть released/hover при нажатии")
    print("OK: pressed над Load Game — кадр base+2, перехода нет (заглушка)")

    # 3.1) Quit БЕЗ подсветки (аппаратно неактивен): наведение и нажатие → всегда released.
    qx, qy = zone_center(zones[4])
    set_mouse(emu, qx, qy, pressed=False)
    emu.call(emu.sym["Game_Update"], max_steps=2_000_000)
    if emu.get_byte(emu.sym["MenuHoverIndex"]) == 4:
        fail("Quit не должен попадать в hover (исключён)")
    set_mouse(emu, qx, qy, pressed=True)
    emu.call(emu.sym["Game_Update"], max_steps=2_000_000)
    if emu.get_byte(emu.sym["GameMode"]) != GAME_MODE_MENU:
        fail("нажатие Quit не должно ничего делать (аппаратно неактивен)")
    srcs = render(emu, regs)
    if btn["QUIT"]["REL"] not in srcs:
        fail("Quit должен рисоваться released всегда")
    if btn["QUIT"]["HOVER"] in srcs or btn["QUIT"]["PRESSED"] in srcs:
        fail("Quit НЕ должен подсвечиваться (hover/pressed) — аппаратное ограничение")
    print("OK: Quit без подсветки — всегда released, нажатие без эффекта")

    # 3.5) Подсветка двери: наведение на зону настроек → MenuDoorHover=1, door-спрайт в DL;
    #      увод мыши → 0, спрайт исчезает (зеркалит highlightDoor по settingsArea).
    scx = (settings_zone[0] + settings_zone[2]) // 2
    scy = (settings_zone[1] + settings_zone[3]) // 2
    set_mouse(emu, scx, scy, pressed=False)
    emu.call(emu.sym["Game_Update"], max_steps=2_000_000)
    if emu.get_byte(emu.sym["MenuDoorHover"]) != 1:
        fail(f"над зоной настроек MenuDoorHover={emu.get_byte(emu.sym['MenuDoorHover'])} (ожидалось 1)")
    srcs = render(emu, regs)
    if door_addr not in srcs:
        fail("door: нет спрайта подсветки двери в DL при наведении на зону настроек")
    set_mouse(emu, 5, 5, pressed=False)
    emu.call(emu.sym["Game_Update"], max_steps=2_000_000)
    if emu.get_byte(emu.sym["MenuDoorHover"]) != 0:
        fail("door: MenuDoorHover должен сброситься при уводе мыши")
    srcs = render(emu, regs)
    if door_addr in srcs:
        fail("door: спрайт двери не должен присутствовать вне зоны настроек")
    print("OK: подсветка двери — появляется над зоной настроек, исчезает при уводе")

    # 4) Анимация фонаря: прогнать кадры, источник кадра фонаря должен смениться.
    set_mouse(emu, 5, 5, pressed=False)
    idx0 = emu.get_byte(emu.sym["MenuLanternIdx"])
    src0 = [s for s in render(emu, regs) if s in lantern_frames]
    for _ in range(8):
        emu.call(emu.sym["Game_Update"], max_steps=2_000_000)
    idx1 = emu.get_byte(emu.sym["MenuLanternIdx"])
    src1 = [s for s in render(emu, regs) if s in lantern_frames]
    if idx1 == idx0:
        fail(f"кадр фонаря не сменился за 8 апдейтов (idx={idx0})")
    if not src1 or src1 == src0:
        fail(f"BITMAP_SOURCE фонаря не сменился: {src0} -> {src1}")
    print(f"OK: анимация фонаря — idx {idx0}->{idx1}, источник {src0}->{src1}")

    print("=== test_menu_hover: PASS ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
