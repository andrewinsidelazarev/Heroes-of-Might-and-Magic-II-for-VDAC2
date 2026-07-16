#!/usr/bin/env python3
"""Регресс: индекс объектной таблицы рантайма == stride упаковки генератора.

Баг, который это ловит: Render_ObjectViewTableEntry индексировал таблицу с
зашитым ×17, а viewport_pack упаковывает пакеты со stride (max_x+1)=23. При
originY=0 совпадало (поэтому test_sprite_scroll_sync с X-скроллом был зелёным),
а при originY>0 грузился ЧУЖОЙ пакет объектов → спрайты «в воде/где попало»,
хуже к нижнему/правому краю карты.

Тест прогоняет настоящую Render_ObjectViewTableEntry для набора origin (включая
originY>0 и правый-нижний угол) и сверяет возвращённый HL с эталоном
ObjectViewDL_Table + (originY*STRIDE + originX)*ENTRY_SIZE.
"""
from __future__ import annotations

import re

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT

# DEFB page + DEFW off + DEFW bottom_size + DEFW top_size (z-слои); читаем из inc


def fail(msg: str) -> None:
    raise SystemExit(f"ОШИБКА: {msg}")


def equ(path, name: str) -> int:
    text = (ROOT / "Source" / "ASM" / path).read_text(encoding="utf-8")
    m = re.search(rf"^\s*{re.escape(name)}\s+EQU\s+(.+?)\s*$", text, re.MULTILINE)
    if not m:
        fail(f"нет EQU {name} в {path}")
    v = m.group(1).strip()
    return int(v[1:], 16) if v.startswith("#") else int(v)


def main() -> None:
    emu = HMM2FullZ80Emulator(ROOT)
    table = emu.sym["ObjectViewDL_Table"]
    stride = emu.sym["OBJECT_VIEW_STRIDE"]
    entry_size = emu.sym.get("OBJECT_VIEW_ENTRY_SIZE", 7)

    width = equ("generated_map.inc", "MAP0_W")
    view_w = equ("generated_terrain.inc", "GAME_VIEW_TILE_W")
    view_h = equ("generated_terrain.inc", "GAME_VIEW_TILE_H")
    max_x = width - view_w
    max_y = width - view_h  # карта квадратная; height==width для SKIRMISH

    expected_stride = max_x + 1
    if stride != expected_stride:
        fail(f"OBJECT_VIEW_STRIDE={stride} != (max_x+1)={expected_stride} "
             f"(width={width}, VIEW_W={view_w})")

    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)

    cases = [
        (0, 0), (1, 0), (max_x, 0),         # originY=0 — даже со старым багом было ок
        (0, 1), (0, 4), (0, max_y),         # originY>0 — баг тут
        (5, 3), (max_x, max_y),             # диагональ и правый-нижний угол
    ]
    for ox, oy in cases:
        emu.set_byte(emu.sym["ViewportOriginX"], ox)
        emu.set_byte(emu.sym["ViewportOriginY"], oy)
        emu.call(emu.sym["Render_ObjectViewTableEntry"], max_steps=200_000)
        hl = (emu.reg.H << 8) | emu.reg.L
        expect = table + (oy * stride + ox) * entry_size
        if hl != expect:
            idx_got = (hl - table) // entry_size
            fail(f"origin=({ox},{oy}): таблица-индекс HL=#{hl:04X} != #{expect:04X}; "
                 f"рантайм взял запись {idx_got} вместо {oy*stride+ox} "
                 f"(stride рантайма похоже {(idx_got-ox)//oy if oy else '?'}, а таблицы {stride})")

    print(f"OK: объектная таблица индексируется со stride={stride} согласованно с упаковкой "
          f"(проверено {len(cases)} origin, включая originY>0 и угол {max_x},{max_y})")


if __name__ == "__main__":
    main()
