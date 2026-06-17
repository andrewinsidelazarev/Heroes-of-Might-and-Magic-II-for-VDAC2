#!/usr/bin/env python3
"""Извлечение ассетов главного меню (зеркалит game_mainmenu.cpp / drawMainMenuScreen):

  - фон  ICN::HEROES[0]    — полноэкранный арт 640×480;
  - кнопки ICN::BTNSHNGL[1/5/9/13/17] (New Game / Load / High Scores / Credits / Quit),
    pressed = +2; позиция каждой — из её собственного offset (ox,oy) в ICN.

Фон превышает FT812-лимит размера bitmap (~319) → раскрой на куски ≤319 (как UI-полосы
в viewport_pack). Палитра KB.PAL → ARGB4444 (прозрачная для кнопок + opaque для фона).

Режимы:
  --preview PATH   — собрать PNG-реконструкцию меню (фон+кнопки) для визуальной сверки;
  (по умолчанию)   — эмит generated_menu.inc + SPG-страницы (MENU_*.bin)  [TODO далее].
"""
from __future__ import annotations

import argparse
from pathlib import Path

from agg_tools import read_agg_index_with_expansion
from object_atlas import agg_entry, read_icn, read_palette
from viewport_pack import (
    align,
    crop_indices,
    decode_icn_indices,
    palette_argb4444,
    palette_argb4444_opaque,
    split_ui_blits,
    DISPLAY_SCALE_NUM,
    DISPLAY_SCALE_DEN,
)

ROOT = Path(__file__).resolve().parents[2]
AGG_PATH = ROOT / "Assets" / "Original" / "DATA" / "HEROES2.AGG"

MENU_BG_ICN = "HEROES.ICN"
MENU_BTN_ICN = "BTNSHNGL.ICN"
# released-индексы кнопок главного меню (drawMainMenuScreen), pressed = +2.
MENU_BTN_RELEASED = [1, 5, 9, 13, 17]
MENU_BG_W = 640
MENU_BG_H = 480
TRANSPARENT = 0          # OBJECT_TRANSPARENT_INDEX из decode_icn_indices


def load_menu_sources():
    agg, entries = read_agg_index_with_expansion(AGG_PATH)
    palette = read_palette(agg_entry(agg, entries, "KB.PAL"))

    hero = read_icn(agg_entry(agg, entries, MENU_BG_ICN))
    bg_header, bg_encoded = hero[0]
    bg_raw = decode_icn_indices(bg_header, bg_encoded)
    bg = {"w": bg_header["w"], "h": bg_header["h"], "raw": bg_raw}

    btn_icn = read_icn(agg_entry(agg, entries, MENU_BTN_ICN))
    buttons = []
    for rel in MENU_BTN_RELEASED:
        h0, e0 = btn_icn[rel]
        hp, ep = btn_icn[rel + 2]
        buttons.append({
            "index": rel,
            "ox": h0["ox"], "oy": h0["oy"],
            "w": h0["w"], "h": h0["h"],
            "released": decode_icn_indices(h0, e0),
            "pressed": decode_icn_indices(hp, ep),
            "pw": hp["w"], "ph": hp["h"],
            "pox": hp["ox"], "poy": hp["oy"],
        })
    return palette, bg, buttons


def background_tiles(bg):
    """Раскрой фона на куски ≤319 (FT812-совместимые), как split_ui_blits для UI."""
    tiles = []
    for sx, sy, w, h, dx, dy in split_ui_blits([(0, 0, bg["w"], bg["h"], 0, 0)]):
        tiles.append({
            "indices": crop_indices(bg["raw"], bg["w"], sx, sy, w, h),
            "w": w, "h": h, "dx": dx, "dy": dy,
        })
    return tiles


def render_preview(palette, bg, buttons, out_path: Path) -> None:
    from PIL import Image

    img = Image.new("RGB", (bg["w"], bg["h"]))
    px = img.load()
    raw = bg["raw"]
    for y in range(bg["h"]):
        for x in range(bg["w"]):
            r, g, b = palette[raw[y * bg["w"] + x]]
            px[x, y] = (r, g, b)
    # кнопки поверх (released), пропуская прозрачный индекс 0
    for btn in buttons:
        bw, bh, ox, oy = btn["w"], btn["h"], btn["ox"], btn["oy"]
        rel = btn["released"]
        for y in range(bh):
            for x in range(bw):
                idx = rel[y * bw + x]
                if idx == TRANSPARENT:
                    continue
                dx, dy = ox + x, oy + y
                if 0 <= dx < bg["w"] and 0 <= dy < bg["h"]:
                    px[dx, dy] = palette[idx]
    img.save(out_path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Извлечение ассетов главного меню HMM2.")
    ap.add_argument("--preview", type=Path, default=None, help="PNG-реконструкция меню для сверки")
    args = ap.parse_args()

    palette, bg, buttons = load_menu_sources()
    tiles = background_tiles(bg)

    print(f"фон {MENU_BG_ICN}[0]: {bg['w']}×{bg['h']}, кусков ≤319: {len(tiles)}")
    for i, t in enumerate(tiles):
        print(f"  кусок[{i}] {t['w']}×{t['h']} @ ({t['dx']},{t['dy']})")
    print(f"кнопки {MENU_BTN_ICN} (released {MENU_BTN_RELEASED}):")
    for btn in buttons:
        print(f"  [{btn['index']:2d}] {btn['w']}×{btn['h']} @ ({btn['ox']},{btn['oy']})  pressed[{btn['index']+2}] {btn['pw']}×{btn['ph']} @ ({btn['pox']},{btn['poy']})")

    if args.preview:
        render_preview(palette, bg, buttons, args.preview)
        print(f"preview: {args.preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
