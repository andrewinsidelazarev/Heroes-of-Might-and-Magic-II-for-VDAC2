#!/usr/bin/env python3
from __future__ import annotations

import re

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT
from shadow_ft812 import disasm_dl


def fail(message: str) -> None:
    raise SystemExit(f"ОШИБКА: {message}")


def vertex_scaled(value: int) -> int:
    return (value * 8 * 16) // 5


def expected_scroll_dx(x0: int, x1: int) -> int:
    return -(vertex_scaled(x1) - vertex_scaled(x0))


def read_equ(path, name: str) -> int:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"^\s*{re.escape(name)}\s+EQU\s+(.+?)\s*$", text, re.MULTILINE)
    if not match:
        fail(f"нет EQU {name}")
    value = match.group(1).strip()
    return int(value[1:], 16) if value.startswith("#") else int(value)


OBJECT_INC = ROOT / "Source" / "ASM" / "generated_objects.inc"
OBJECT_ATLAS_RAMG = read_equ(OBJECT_INC, "OBJECT_ATLAS_RAMG")
HERO_SPRITE_RAMG = read_equ(OBJECT_INC, "HERO_SPRITE_RAMG")
CURSOR_SPRITE_RAMG = read_equ(OBJECT_INC, "CURSOR_SPRITE_RAMG")
TERRAIN_INC = ROOT / "Source" / "ASM" / "generated_terrain.inc"
GAME_VIEW_X16 = read_equ(TERRAIN_INC, "GAME_VIEW_X16")
GAME_VIEW_Y16 = read_equ(TERRAIN_INC, "GAME_VIEW_Y16")
GAME_VIEW_SCREEN_W16 = read_equ(TERRAIN_INC, "GAME_VIEW_SCREEN_W") * 16
GAME_VIEW_SCREEN_H16 = read_equ(TERRAIN_INC, "GAME_VIEW_SCREEN_H") * 16
TILE_EDGE_MARGIN16 = vertex_scaled(32)


def parse_addr(value) -> int | None:
    if not isinstance(value, str) or not value.startswith("#"):
        return None
    return int(value[1:], 16)


def render_ops(emu: HMM2FullZ80Emulator, viewport_x: int):
    emu.set_word(emu.sym["ViewportPixelX"], viewport_x)
    emu.set_byte(emu.sym["ViewportOriginX"], viewport_x // 32)
    emu.call(emu.sym["Render_Frame"], max_steps=12_000_000)
    return disasm_dl(bytes(emu.ft.ram_dl), max_ops=4096)


def object_vertices(ops) -> list[tuple[int, int, int]]:
    out: list[tuple[int, int, int]] = []
    tx = 0
    ty = 0
    current_source: int | None = None
    translate_pairs = 0
    saw_translate_x = False
    in_object_layer = False
    object_bitmaps_started = False
    for op in ops:
        if op.name == "VERTEX_TRANSLATE_X":
            tx = int(op.fields["x"])
            saw_translate_x = True
            continue
        if op.name == "VERTEX_TRANSLATE_Y":
            ty = int(op.fields["y"])
            if saw_translate_x:
                translate_pairs += 1
                if translate_pairs == 2:
                    in_object_layer = True
            saw_translate_x = False
            continue
        saw_translate_x = False
        if not in_object_layer:
            continue
        if op.name == "BEGIN" and op.fields.get("prim") == "BITMAPS":
            object_bitmaps_started = True
            continue
        if op.name == "END" and object_bitmaps_started:
            break
        if op.name == "BITMAP_SOURCE":
            addr = parse_addr(op.fields.get("addr"))
            if addr == HERO_SPRITE_RAMG:
                break
            current_source = addr if addr is not None and OBJECT_ATLAS_RAMG <= addr < HERO_SPRITE_RAMG else None
            continue
        if op.name == "VERTEX2F" and current_source is not None:
            out.append((current_source, int(op.fields["x"]) + tx, int(op.fields["y"]) + ty))
            continue
        if op.name in ("END", "DISPLAY"):
            current_source = None
    if not out:
        fail("object-layer vertices не найдены")
    return out


def terrain_vertices(ops) -> list[tuple[tuple[int, int], int, int]]:
    out: list[tuple[tuple[int, int], int, int]] = []
    tx = 0
    ty = 0
    handle: int | None = None
    cell: int | None = None
    saw_translate_x = False
    translate_pairs = 0
    in_terrain_layer = False
    for op in ops:
        if op.name == "VERTEX_TRANSLATE_X":
            tx = int(op.fields["x"])
            saw_translate_x = True
            continue
        if op.name == "VERTEX_TRANSLATE_Y":
            ty = int(op.fields["y"])
            if saw_translate_x:
                translate_pairs += 1
                if translate_pairs == 1:
                    in_terrain_layer = True
                elif translate_pairs == 2:
                    break
            saw_translate_x = False
            continue
        saw_translate_x = False
        if not in_terrain_layer:
            continue
        if op.name == "BITMAP_HANDLE":
            handle = int(op.fields["handle"])
            continue
        if op.name == "CELL":
            cell = int(op.fields["cell"])
            continue
        if op.name == "VERTEX2F" and handle is not None and cell is not None:
            out.append(((handle, cell), int(op.fields["x"]) + tx, int(op.fields["y"]) + ty))
            continue
    if not out:
        fail("terrain-layer vertices не найдены")
    return out


def source_vertices(ops, source: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    tx = 0
    ty = 0
    pending = False
    for op in ops:
        if op.name == "VERTEX_TRANSLATE_X":
            tx = int(op.fields["x"])
            continue
        if op.name == "VERTEX_TRANSLATE_Y":
            ty = int(op.fields["y"])
            continue
        if op.name == "BITMAP_SOURCE":
            pending = parse_addr(op.fields.get("addr")) == source
            continue
        if pending and op.name == "VERTEX2F":
            out.append((int(op.fields["x"]) + tx, int(op.fields["y"]) + ty))
            pending = False
            continue
        if pending and op.name in ("END", "DISPLAY"):
            pending = False
    if not out:
        fail(f"vertices для source #{source:06X} не найдены")
    return out


def assert_layer_scroll(
    name: str,
    a: list[tuple[object, int, int]],
    b: list[tuple[object, int, int]],
    expected_dx: int,
    x0: int,
    x1: int,
    allow_edge_turnover: bool = False,
) -> None:
    unmatched = b.copy()
    matched = 0
    misses: list[tuple[object, int, int]] = []
    for key0, ax, ay in a:
        hit = False
        for index, (key1, bx, by) in enumerate(unmatched):
            if key0 == key1 and bx - ax == expected_dx and by == ay:
                unmatched.pop(index)
                matched += 1
                hit = True
                break
        if not hit:
            misses.append((key0, ax + expected_dx, ay))
    def is_edge_turnover(item: tuple[object, int, int]) -> bool:
        _, x, y = item
        right = GAME_VIEW_X16 + GAME_VIEW_SCREEN_W16
        bottom = GAME_VIEW_Y16 + GAME_VIEW_SCREEN_H16
        return (
            x < GAME_VIEW_X16
            or y < GAME_VIEW_Y16
            or x >= right - TILE_EDGE_MARGIN16
            or y >= bottom - TILE_EDGE_MARGIN16
        )

    relevant_misses = misses
    relevant_unmatched = unmatched
    if allow_edge_turnover:
        relevant_misses = [item for item in misses if not is_edge_turnover(item)]
        relevant_unmatched = [item for item in unmatched if not is_edge_turnover(item)]

    if relevant_misses or relevant_unmatched or (not allow_edge_turnover and matched != min(len(a), len(b))):
        def fmt_key(key: object) -> str:
            if isinstance(key, tuple):
                return "/".join(str(part) for part in key)
            if isinstance(key, int):
                return f"#{key:06X}"
            return str(key)

        def sample(items: list[tuple[object, int, int]]) -> str:
            return ", ".join(f"{fmt_key(key)}@{x},{y}" for key, x, y in items[:4])

        fail(
            f"{name} несинхронен на {x0}->{x1}: "
            f"matched={matched}, left={len(a)}, right={len(b)}, ожидалось dx={expected_dx}; "
            f"missing={sample(relevant_misses)}; extra={sample(relevant_unmatched)}"
        )


def assert_scroll_pair(emu: HMM2FullZ80Emulator, x0: int, x1: int) -> None:
    ops0 = render_ops(emu, x0)
    ops1 = render_ops(emu, x1)

    expected_dx = expected_scroll_dx(x0, x1)
    assert_layer_scroll("terrain-layer", terrain_vertices(ops0), terrain_vertices(ops1), expected_dx, x0, x1, allow_edge_turnover=True)
    assert_layer_scroll("object-layer", object_vertices(ops0), object_vertices(ops1), expected_dx, x0, x1, allow_edge_turnover=True)

    hero0 = source_vertices(ops0, HERO_SPRITE_RAMG)[0]
    hero1 = source_vertices(ops1, HERO_SPRITE_RAMG)[0]
    if hero1[0] - hero0[0] != expected_dx or hero1[1] != hero0[1]:
        fail(
            f"hero sprite несинхронен на {x0}->{x1}: "
            f"dx={hero1[0] - hero0[0]}, dy={hero1[1] - hero0[1]}, ожидалось dx={expected_dx}, dy=0"
        )

    cursor0 = source_vertices(ops0, CURSOR_SPRITE_RAMG)[0]
    cursor1 = source_vertices(ops1, CURSOR_SPRITE_RAMG)[0]
    if cursor1 != cursor0:
        fail(f"cursor дергается от viewport scroll на {x0}->{x1}: {cursor0} -> {cursor1}")


def main() -> None:
    emu = HMM2FullZ80Emulator(ROOT)
    emu.input.mouse_x = 0
    emu.input.mouse_y = 0
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Adventure_Enter"], max_steps=12_000_000)  # Game_Init стартует в меню; входим в adventure

    assert_scroll_pair(emu, 0, 5)
    assert_scroll_pair(emu, 31, 32)
    assert_scroll_pair(emu, 32, 33)
    assert_scroll_pair(emu, 63, 64)
    print("OK: map sprites scroll in sync; screen cursor is stable")


if __name__ == "__main__":
    main()
