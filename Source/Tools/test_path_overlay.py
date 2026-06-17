#!/usr/bin/env python3
from __future__ import annotations

import re

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT
from shadow_ft812 import disasm_dl


PATH_STATE_SEARCH = 0x01


def vertex_scaled(value: int) -> int:
    return (value * 8 * 16) // 5


def fail(message: str) -> None:
    raise SystemExit(f"ОШИБКА: {message}")


def update_frame(emu: HMM2FullZ80Emulator, max_steps: int = 600_000) -> None:
    emu.call(emu.sym["Game_Update"], max_steps=max_steps)


def route_sprite_sources() -> set[str]:
    text = (ROOT / "Source" / "ASM" / "generated_objects.inc").read_text(encoding="utf-8")

    def equ(name: str) -> int:
        match = re.search(rf"^\s*{name}\s+EQU\s+(.+?)\s*$", text, re.MULTILINE)
        if not match:
            fail(f"нет EQU {name}")
        value = match.group(1)
        return int(value[1:], 16) if value.startswith("#") else int(value)

    count = equ("ROUTE_SPRITE_COUNT")
    entry_size = equ("ROUTE_TABLE_ENTRY_SIZE")
    if entry_size != 12:
        fail(f"неожиданный ROUTE_TABLE_ENTRY_SIZE={entry_size}")

    payload = (ROOT / "Assets" / "Converted" / "Objects" / "SKIRMISH_ROUTE_TABLE.bin").read_bytes()
    if len(payload) < count * entry_size:
        fail("SKIRMISH_ROUTE_TABLE.bin короче ROUTE_SPRITE_COUNT")
    sources = set()
    for index in range(count):
        off = index * entry_size
        hi = payload[off]
        lo = payload[off + 1]
        mid = payload[off + 2]
        sources.add(f"#{(hi << 16) | (mid << 8) | lo:06X}")
    if not sources:
        fail("RouteSpriteTable пустой")
    return sources


def read_terrain_equ(name: str) -> int:
    text = (ROOT / "Source" / "ASM" / "generated_terrain.inc").read_text(encoding="utf-8")
    match = re.search(rf"^\s*{name}\s+EQU\s+(.+?)\s*$", text, re.MULTILINE)
    if not match:
        fail(f"нет EQU {name}")
    value = match.group(1)
    return int(value[1:], 16) if value.startswith("#") else int(value)


def render_ops(emu: HMM2FullZ80Emulator):
    emu.call(emu.sym["Render_Frame"], max_steps=8_000_000)
    return disasm_dl(bytes(emu.ft.ram_dl), max_ops=4096)


def assert_no_debug_points(ops, label: str) -> None:
    if any(op.name == "POINT_SIZE" for op in ops):
        fail(f"debug POINT_SIZE остался в DL для {label}")
    if any(op.name == "BEGIN" and op.fields.get("prim") == "POINTS" for op in ops):
        fail(f"debug BEGIN(POINTS) остался в DL для {label}")


def assert_route_sprites(ops, sources: set[str], label: str) -> None:
    used = [op.fields.get("addr") for op in ops if op.name == "BITMAP_SOURCE"]
    if not any(addr in sources for addr in used):
        fail(f"в DL нет ROUTE.ICN bitmap source для {label}")


def route_vertices(ops, sources: set[str]) -> list[tuple[int, int]]:
    out = []
    pending = False
    tx = 0
    ty = 0
    for op in ops:
        if op.name == "VERTEX_TRANSLATE_X":
            tx = int(op.fields["x"])
            continue
        if op.name == "VERTEX_TRANSLATE_Y":
            ty = int(op.fields["y"])
            continue
        if op.name == "BITMAP_SOURCE" and op.fields.get("addr") in sources:
            pending = True
            continue
        if pending and op.name == "VERTEX2F":
            out.append((int(op.fields["x"]) + tx, int(op.fields["y"]) + ty))
            pending = False
        elif pending and op.name in ("END", "DISPLAY"):
            pending = False
    return out


def wait_for_search_frame(emu: HMM2FullZ80Emulator, max_frames: int = 64) -> None:
    for _ in range(max_frames):
        update_frame(emu)
        if emu.get_byte(emu.sym["PathState"]) == PATH_STATE_SEARCH:
            return
    fail(
        "не пойман кадр постепенного поиска: "
        f"PathState={emu.get_byte(emu.sym['PathState'])}"
    )


def wait_for_path_ready(emu: HMM2FullZ80Emulator, max_frames: int = 1024) -> int:
    for _ in range(max_frames):
        update_frame(emu)
        path_len = emu.get_byte(emu.sym["HeroPathLen"])
        if emu.get_byte(emu.sym["PathState"]) == 0 and path_len != 0:
            return path_len
    fail(
        "поиск пути не завершился: "
        f"PathState={emu.get_byte(emu.sym['PathState'])}, "
        f"HeroPathLen={emu.get_byte(emu.sym['HeroPathLen'])}, "
        f"PathDebugLen={emu.get_word(emu.sym['PathDebugLen'])}"
    )


def find_land_target(width: int, start_x: int, start_y: int) -> tuple[int, int]:
    passability = (ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.pass.bin").read_bytes()
    visible_w = read_terrain_equ("GAME_VIEW_TILE_W")
    visible_h = read_terrain_equ("GAME_VIEW_TILE_H")
    candidates = [
        (start_x - 3, start_y),
        (start_x, start_y - 3),
        (start_x - 2, start_y),
        (start_x - 1, start_y + 1),
        (start_x + 3, start_y),
        (start_x, start_y + 3),
        (start_x - 4, start_y - 2),
        (start_x + 4, start_y + 2),
    ]
    for x, y in candidates:
        if x < 0 or y < 0:
            continue
        if x >= visible_w or y >= visible_h:
            continue
        if passability[y * width + x] != 0:
            return x, y
    fail("не найдена сухопутная тестовая цель рядом с героем")


def main() -> None:
    sources = route_sprite_sources()
    emu = HMM2FullZ80Emulator(ROOT)
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Adventure_Enter"], max_steps=12_000_000)  # Game_Init стартует в меню; входим в adventure

    start_x = emu.get_byte(emu.sym["HeroTileX"])
    start_y = emu.get_byte(emu.sym["HeroTileY"])
    target_x, target_y = find_land_target(36, start_x, start_y)

    emu.reg.B = target_x
    emu.reg.C = target_y
    emu.call(emu.sym["Hero_SetTargetIfPassable"], max_steps=4_000_000)

    if emu.get_byte(emu.sym["PathState"]) != PATH_STATE_SEARCH:
        fail(f"Hero_SetTargetIfPassable не запустил поиск: PathState={emu.get_byte(emu.sym['PathState'])}")

    wait_for_search_frame(emu)
    ops = render_ops(emu)
    assert_no_debug_points(ops, "постепенного поиска")

    path_len = wait_for_path_ready(emu)
    ops = render_ops(emu)
    assert_no_debug_points(ops, "готового пути")
    assert_route_sprites(ops, sources, "готового пути")
    vertices0 = route_vertices(ops, sources)
    if not vertices0:
        fail("не найдены ROUTE.ICN vertex для готового пути")

    emu.set_word(emu.sym["ViewportPixelX"], 5)
    emu.call(emu.sym["Viewport_UpdateOriginFromPixel"], max_steps=200_000)
    ops_scrolled = render_ops(emu)
    vertices1 = route_vertices(ops_scrolled, sources)
    if len(vertices1) != len(vertices0):
        fail(f"при скролле изменилось число ROUTE vertex: {len(vertices0)} -> {len(vertices1)}")
    dx = vertices0[0][0] - vertices1[0][0]
    dy = vertices1[0][1] - vertices0[0][1]
    if dx != vertex_scaled(5) or dy != 0:
        fail(f"ROUTE vertex несинхронен со scroll: dx={dx}, dy={dy}, ожидалось {vertex_scaled(5)},0")
    emu.set_word(emu.sym["ViewportPixelX"], 0)
    emu.call(emu.sym["Viewport_UpdateOriginFromPixel"], max_steps=200_000)

    emu.set_byte(emu.sym["HeroTileX"], target_x)
    emu.set_byte(emu.sym["HeroTileY"], target_y)
    emu.set_byte(emu.sym["HeroStepX"], target_x)
    emu.set_byte(emu.sym["HeroStepY"], target_y)
    emu.set_word(emu.sym["HeroPixelX"], target_x * 32)
    emu.set_word(emu.sym["HeroPixelY"], target_y * 32)
    update_frame(emu)

    if emu.get_byte(emu.sym["HeroPathLen"]) != 0:
        fail("после достижения цели HeroPathLen не очищен")

    print(
        "OK: path overlay без POINTS и с оригинальными ROUTE.ICN arrows, "
        f"path_len={path_len}, цель={target_x},{target_y}"
    )


if __name__ == "__main__":
    main()
