#!/usr/bin/env python3
"""Ассеты главного меню (зеркалит game_mainmenu.cpp / drawMainMenuScreen):

  - фон  ICN::HEROES[0]    — полноэкранный арт 640×480;
  - кнопки ICN::BTNSHNGL[1/5/9/13/17] (New Game / Load / High Scores / Credits / Quit),
    pressed = +2; позиция каждой — из её offset (ox,oy) в ICN (вписаны в арт).

Фон превышает FT812-лимит размера bitmap (~319) → раскрой на куски ≤319 (как UI-полосы
в viewport_pack). Палитра KB.PAL → ARGB4444: opaque для фона (без дыр), прозрачная для
кнопок (index 0 = прозрачность).

RAM_G меню (переиспользуется — на момент меню adventure-ассеты ещё не загружены):
  base 0 → [transparent pal][opaque pal][куски фона][кнопки released].
Запекается в SPG-страницы 0xE0.., грузится Menu_LoadAssets (DMA) в Menu_Enter.

Эмитит Source/ASM/generated_menu.inc (адреса/DL/зоны/загрузчик) + SPG bin.
  --preview PATH — PNG-реконструкция меню (фон+кнопки) для визуальной сверки.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from agg_tools import read_agg_index_with_expansion
from object_atlas import agg_entry, read_icn, read_palette
from pak_builder import build_pak, TYPE_RAMG_BLOB, SECTOR
from viewport_pack import (
    align,
    crop_indices,
    decode_icn_indices,
    palette_argb4444,
    palette_argb4444_opaque,
    scaled_screen_pixels,
    scaled_vertex2f_units,
    split_ui_blits,
)

ROOT = Path(__file__).resolve().parents[2]
AGG_PATH = ROOT / "Assets" / "Original" / "DATA" / "HEROES2.AGG"
MENU_INC = ROOT / "Source" / "ASM" / "generated_menu.inc"
MENU_PAK_PATH = ROOT / "Build" / "HMM2MENU.PAK"   # грузится загрузчиком с SD (не SPG)

MENU_BG_ICN = "HEROES.ICN"
MENU_BTN_ICN = "BTNSHNGL.ICN"
MENU_BTN_RELEASED = [1, 5, 9, 13, 17]           # released; pressed = +2
MENU_BTN_NAME = ["NEW_GAME", "LOAD_GAME", "HIGH_SCORES", "CREDITS", "QUIT"]
TRANSPARENT = 0                                  # OBJECT_TRANSPARENT_INDEX
MENU_RAMG_BASE = 0x000000                        # меню-payload грузится в RAM_G base 0
PALETTE_BYTES = 512                              # 256 цветов × ARGB4444


def load_menu_sources():
    agg, entries = read_agg_index_with_expansion(AGG_PATH)
    palette = read_palette(agg_entry(agg, entries, "KB.PAL"))

    hero = read_icn(agg_entry(agg, entries, MENU_BG_ICN))
    bg_header, bg_encoded = hero[0]
    bg = {"w": bg_header["w"], "h": bg_header["h"], "raw": decode_icn_indices(bg_header, bg_encoded)}

    btn_icn = read_icn(agg_entry(agg, entries, MENU_BTN_ICN))
    buttons = []
    for name, rel in zip(MENU_BTN_NAME, MENU_BTN_RELEASED):
        h0, e0 = btn_icn[rel]
        buttons.append({
            "name": name, "index": rel,
            "ox": h0["ox"], "oy": h0["oy"], "w": h0["w"], "h": h0["h"],
            "released": decode_icn_indices(h0, e0),
        })
    return palette, bg, buttons


def background_tiles(bg):
    """Раскрой фона на куски ≤319 (FT812-совместимые)."""
    return [
        {"indices": crop_indices(bg["raw"], bg["w"], sx, sy, w, h), "w": w, "h": h, "dx": dx, "dy": dy}
        for sx, sy, w, h, dx, dy in split_ui_blits([(0, 0, bg["w"], bg["h"], 0, 0)])
    ]


def build_payload(palette, tiles, buttons):
    """RAM_G-payload меню (base 0). Возвращает (payload, addrs)."""
    payload = bytearray()

    def put(raw: bytes) -> int:
        addr = MENU_RAMG_BASE + align(len(payload), 4)
        while MENU_RAMG_BASE + len(payload) < addr:
            payload.append(0)
        payload.extend(raw)
        return addr

    transparent_addr = put(palette_argb4444(palette))        # index 0 → alpha 0 (кнопки)
    opaque_addr = put(palette_argb4444_opaque(palette))      # index 0 непрозрачный (фон)
    for t in tiles:
        t["addr"] = put(t["indices"])
    for b in buttons:
        b["addr"] = put(b["released"])
    return payload, {"transparent": transparent_addr, "opaque": opaque_addr}


def emit_inc(addrs, tiles, buttons, pak):
    L = []
    L.append("; Сгенерировано Source/Tools/menu_pack.py — ассеты главного меню.")
    L.append("                ifndef _HMM2_GENERATED_MENU_")
    L.append("                define _HMM2_GENERATED_MENU_")
    L.append("")
    L.append(f"MENU_TRANSPARENT_PAL_RAMG EQU #{addrs['transparent']:06X}")
    L.append(f"MENU_OPAQUE_PAL_RAMG      EQU #{addrs['opaque']:06X}")
    L.append("")

    # --- готовый DL-блок сцены меню (копируется в CMD-буфер в Render_Menu) ---
    L.append("MenuScene_DL:")
    L.append("                FT_CLEAR_COLOR_RGB 0, 0, 0")
    L.append("                FT_CLEAR 1, 1, 1")
    L.append("                FT_SCISSOR_XY 0, 0")
    L.append("                FT_SCISSOR_SIZE 1024, 768")
    L.append("                FT_COLOR_RGB 255, 255, 255")
    L.append("                FT_COLOR_A 255")
    L.append("                FT_BITMAP_HANDLE 0")
    L.append("                FT_CELL 0")
    L.append("                FT_BITMAP_TRANSFORM_A 160")     # ×1.6 (8/5)
    L.append("                FT_BITMAP_TRANSFORM_E 160")
    L.append("                FT_BITMAP_TRANSFORM_C 0")
    L.append("                FT_VERTEX_TRANSLATE_X 0")
    L.append("                FT_VERTEX_TRANSLATE_Y 0")
    L.append("                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA")
    L.append("                FT_BITMAP_LAYOUT_H 0, 0")
    L.append("                FT_BITMAP_SIZE_H 0, 0")
    # фон — opaque-палитра
    L.append("                FT_PALETTE_SOURCE MENU_OPAQUE_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    for t in tiles:
        L.append(f"                FT_BITMAP_SOURCE #{t['addr']:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {t['w']}, {t['h']}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {scaled_screen_pixels(t['w'])}, {scaled_screen_pixels(t['h'])}")
        L.append(f"                FT_VERTEX2F {scaled_vertex2f_units(t['dx'])}, {scaled_vertex2f_units(t['dy'])}")
    L.append("                FT_END")
    # кнопки — прозрачная палитра
    L.append("                FT_PALETTE_SOURCE MENU_TRANSPARENT_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    for b in buttons:
        L.append(f"                FT_BITMAP_SOURCE #{b['addr']:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {b['w']}, {b['h']}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {scaled_screen_pixels(b['w'])}, {scaled_screen_pixels(b['h'])}")
        L.append(f"                FT_VERTEX2F {scaled_vertex2f_units(b['ox'])}, {scaled_vertex2f_units(b['oy'])}")
    L.append("                FT_END")
    L.append("                FT_DISPLAY")
    L.append("MenuScene_DL_SIZE EQU $ - MenuScene_DL")
    L.append("")

    # --- зоны кнопок для hit-test (ЛОГИЧЕСКИЕ координаты 640×480) ---
    L.append(f"MENU_BUTTON_COUNT EQU {len(buttons)}")
    L.append("; запись: x0,y0,x1,y1 (4×2б). Индекс зоны = индекс кнопки (0=New Game).")
    L.append("MenuButtonZones:")
    for b in buttons:
        x0, y0, x1, y1 = b["ox"], b["oy"], b["ox"] + b["w"], b["oy"] + b["h"]
        L.append(f"                DEFW {x0}, {y0}, {x1}, {y1}   ; [{b['index']:2d}] {b['name']}")
    L.append("")

    # --- метаданные HMM2MENU.PAK (грузится загрузчиком с SD в Menu_Enter) ---
    # PAK: сектор 0 = HPAK header+каталог (1 RAM_G-blob @ MENU_RAMG_BASE); далее payload.
    L.append(f"MENU_RAMG_BASE       EQU #{MENU_RAMG_BASE:06X}")
    L.append(f"MENU_PAYLOAD_BYTES   EQU {pak['payload_bytes']}")
    L.append(f"MENU_PAYLOAD_SECTORS EQU {pak['payload_sectors']}")
    L.append(f"MENU_BODY_SECTOR     EQU {pak['body_start_sector']}   ; payload начинается с этого сектора файла")
    L.append('MenuPakName:         DEFB "HMM2MENU.PAK", 0')
    L.append("")
    L.append("                endif")
    MENU_INC.write_text("\n".join(L), encoding="utf-8")


def render_preview(palette, bg, buttons, out_path: Path) -> None:
    from PIL import Image

    img = Image.new("RGB", (bg["w"], bg["h"]))
    px = img.load()
    raw = bg["raw"]
    for y in range(bg["h"]):
        for x in range(bg["w"]):
            px[x, y] = palette[raw[y * bg["w"] + x]]
    for b in buttons:
        bw, bh, ox, oy, rel = b["w"], b["h"], b["ox"], b["oy"], b["released"]
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
    ap = argparse.ArgumentParser(description="Ассеты главного меню HMM2.")
    ap.add_argument("--preview", type=Path, default=None, help="PNG-реконструкция меню для сверки")
    args = ap.parse_args()

    palette, bg, buttons = load_menu_sources()
    tiles = background_tiles(bg)

    if args.preview:
        render_preview(palette, bg, buttons, args.preview)
        print(f"preview: {args.preview}")
        return 0

    payload, addrs = build_payload(palette, tiles, buttons)
    # HMM2MENU.PAK: сектор 0 = HPAK header+каталог (1 RAM_G-blob @ MENU_RAMG_BASE),
    # payload — с сектора body_start. Грузится загрузчиком с SD в Menu_Enter (НЕ SPG).
    summary = build_pak(
        [{"type": TYPE_RAMG_BLOB, "target": MENU_RAMG_BASE, "data": bytes(payload)}],
        MENU_PAK_PATH,
    )
    pak = {
        "payload_bytes": len(payload),
        "payload_sectors": (len(payload) + SECTOR - 1) // SECTOR,
        "body_start_sector": summary["body_start_sector"],
    }
    emit_inc(addrs, tiles, buttons, pak)
    print(f"menu pack -> {MENU_PAK_PATH.name}: фон {len(tiles)} кусков + {len(buttons)} кнопок, "
          f"payload={len(payload)} байт ({pak['payload_sectors']} сект), "
          f"PAK={summary['total_bytes']} байт, blob с сектора {pak['body_start_sector']}")
    print(f"  inc: {MENU_INC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
