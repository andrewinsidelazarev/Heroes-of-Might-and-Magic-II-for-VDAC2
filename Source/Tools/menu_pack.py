#!/usr/bin/env python3
"""Ассеты главного меню (зеркалит game_mainmenu.cpp / drawMainMenuScreen + MainMenu loop):

  - фон   ICN::HEROES[0]    — полноэкранный арт 640×480;
  - кнопки ICN::BTNSHNGL: на кнопку 3 состояния — released (base), hover (base+1),
    pressed (base+2). База New Game/Load/HighScores/Credits/Quit = 1/5/9/13/17.
    В оригинале hover = ++frame при наведении (game_mainmenu.cpp), pressed = base+2.
    Все 3 кадра одной кнопки имеют один offset (ox,oy) → рисуются в ту же позицию.
  - фонарь ICN::SHNGANIM: кадр 0 = статичная база (lantern10) @ (46,176);
    кадры 1..39 = анимация (getAnimatedIcnIndex → 1+frame%39) @ (48,183) 136×180.

АППАРАТНАЯ ОГОВОРКА (RAM_G 1 МБ): 39 кадров фонаря 136×180 = ~932 КБ — вместе с фоном
не помещаются в RAM_G (до зоны курсора #0E0000 ≈ 917 КБ). Поэтому анимация фонаря
ПРОРЕЖЕНА (каждый LANTERN_STRIDE-й кадр). Полный цикл сохраняется визуально (мерцание).

Фон превышает FT812-лимит размера bitmap (~319) → раскрой на куски ≤319. Палитра
KB.PAL → ARGB4444: opaque для фона (без дыр), прозрачная для спрайтов (index 0 = alpha 0).

RAM_G меню (base 0, переиспользуется — adventure-ассеты грузятся позже, в Adventure_Enter):
  [transparent pal][opaque pal][куски фона][кнопки rel/hover/pressed][фонарь база+кадры].
Стримится с SD из HMM2MENU.PAK загрузчиком в Menu_Enter (НЕ SPG).

Эмитит Source/ASM/generated_menu.inc:
  - MenuBg_DL          — статический DL фона (пролог + opaque-палитра + тайлы), без DISPLAY;
  - MenuSpritesProlog_DL / MenuSpritesEnd_DL — transparent-палитра+BEGIN / END для спрайтов;
  - MenuLanternBase_DL + MenuLanternFrameTab (MENU_LANTERN_FRAMES блоков по 16Б);
  - MenuBtnFrameTab    — на кнопку 3 указателя (rel/hover/pressed) на 16-байтные DL-блоки;
  - MenuButtonZones    — зоны hit-test (логич. 640×480);
  - метаданные HMM2MENU.PAK.
  --preview PATH — PNG-реконструкция меню (фон + released-кнопки + база фонаря).
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
MENU_BTN_RELEASED = [1, 5, 9, 13, 17]            # released; hover = +1, pressed = +2
MENU_BTN_NAME = ["NEW_GAME", "LOAD_GAME", "HIGH_SCORES", "CREDITS", "QUIT"]

# --- Подменю NEW GAME (оригинальный вид HoMM2; геометрия = fheroes2 1.0.0 drawButtonPanel,
#     game_newgame.cpp: панель REDBACK @ (640−227−8, 480−472)=(405,8); кнопки BTNNEWGM 132×62:
#     x = 405+16+(227−16)/2 − 132/2 − 3 = 457 (SHADOWWIDTH=16, 3=тень кнопки), y = 46 + 66·i;
#     Cancel в 6-м слоте (y = 46+330 = 376). Кадры: Standard 0/1, Campaign 2/3, Multi 4/5,
#     Cancel 6/7 (released/pressed; hover-кадров у BTNNEWGM нет — по оригиналу). ---
NG_PANEL_ICN = "REDBACK.ICN"
NG_BTN_ICN = "BTNNEWGM.ICN"
NG_PANEL_POS = (405, 8)
NG_BTN_X = 457
NG_BTN_Y = [46, 112, 178, 376]                   # Standard, Campaign, Multi-Player, Cancel
NG_BTN_NAME = ["STANDARD", "CAMPAIGN", "MULTI", "CANCEL"]

MENU_LANTERN_ICN = "SHNGANIM.ICN"
MENU_LANTERN_BASE_FRAME = 0                       # SHNGANIM[0] — статичная база фонаря
MENU_LANTERN_ANIM_FIRST = 1                       # анимация: кадры 1..39 (getAnimatedIcnIndex)
MENU_LANTERN_ANIM_LAST = 39
MENU_LANTERN_STRIDE = 4                           # прореживание под RAM_G (39 → 10 кадров;
                                                  # шаг 3 не влезает с ассетами подменю NEW GAME)
MENU_LANTERN_SHIFT = 2                            # смена кадра каждые 1<<SHIFT гейм-кадров

# Подсветка двери (settingsArea hover): highlightDoor = SHNGANIM[18] + ApplyPalette(.,8),
# рисуется субрегионом с doorOffsetY (game_mainmenu.cpp). settingsArea (логич. scale=1,
# offset=0): x,y,w,h. PAL8 — блок 8 transformTable (NO_CYCLE) из engine/image.cpp.
MENU_DOOR_FRAME = 18
MENU_DOOR_OFFSET_Y = 55                           # doorOffsetY: срез источника + сдвиг вниз
SETTINGS_AREA = (63, 202, 108, 160)               # x, y, w, h (логич. 640×480)
PAL8 = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 11, 11, 12, 13, 14, 14, 15, 16, 17, 17, 18, 19, 20, 20,
    21, 22, 23, 24, 24, 25, 26, 26, 27, 28, 29, 29, 37, 37, 38, 39, 40, 40, 41, 42, 42, 43, 44,
    44, 45, 46, 46, 47, 47, 48, 48, 49, 50, 50, 27, 28, 28, 28, 63, 63, 64, 65, 65, 66, 67, 67,
    68, 69, 69, 69, 70, 70, 70, 244, 71, 244, 244, 244, 244, 245, 16, 85, 85, 86, 87, 87, 88,
    88, 89, 90, 90, 91, 91, 91, 92, 93, 93, 93, 29, 29, 29, 29, 29, 37, 109, 109, 110, 111, 111,
    112, 113, 112, 112, 203, 203, 203, 44, 45, 46, 47, 47, 47, 48, 48, 49, 50, 131, 131, 132,
    133, 133, 134, 135, 136, 136, 137, 137, 139, 139, 139, 141, 141, 141, 143, 143, 245, 245,
    152, 152, 153, 154, 155, 155, 156, 157, 158, 158, 159, 160, 161, 162, 163, 163, 164, 165,
    165, 166, 26, 26, 27, 175, 13, 176, 177, 178, 178, 179, 180, 181, 181, 182, 182, 183, 183,
    183, 184, 184, 185, 185, 50, 50, 52, 52, 109, 109, 198, 199, 200, 201, 201, 202, 202, 44,
    45, 46, 47, 48, 48, 49, 204, 205, 185, 185, 112, 112, 204, 47, 112, 113, 88, 89, 91, 92, 93,
    93, 25, 66, 68, 69, 69, 68, 69, 69, 153, 159, 68, 71, 18, 242, 243, 24, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0,
]

TRANSPARENT = 0                                  # OBJECT_TRANSPARENT_INDEX
MENU_RAMG_BASE = 0x000000                        # меню-payload грузится в RAM_G base 0
SPRITE_DL_SIZE = 16                              # 4 команды × 4Б (SOURCE/LAYOUT/SIZE/VERTEX2F)


def _frame(icn, idx):
    h, e = icn[idx]
    return {"ox": h["ox"], "oy": h["oy"], "w": h["w"], "h": h["h"],
            "indices": decode_icn_indices(h, e)}


def load_menu_sources():
    agg, entries = read_agg_index_with_expansion(AGG_PATH)
    palette = read_palette(agg_entry(agg, entries, "KB.PAL"))

    hero = read_icn(agg_entry(agg, entries, MENU_BG_ICN))
    bg_header, bg_encoded = hero[0]
    bg = {"w": bg_header["w"], "h": bg_header["h"], "raw": decode_icn_indices(bg_header, bg_encoded)}

    btn_icn = read_icn(agg_entry(agg, entries, MENU_BTN_ICN))
    buttons = []
    for name, rel in zip(MENU_BTN_NAME, MENU_BTN_RELEASED):
        r = _frame(btn_icn, rel)          # released
        hov = _frame(btn_icn, rel + 1)    # hover  (++frame в оригинале)
        prs = _frame(btn_icn, rel + 2)    # pressed (base+2)
        buttons.append({
            "name": name, "index": rel,
            "ox": r["ox"], "oy": r["oy"], "w": r["w"], "h": r["h"],
            "released": r["indices"],
            "hover": {"ox": hov["ox"], "oy": hov["oy"], "w": hov["w"], "h": hov["h"], "indices": hov["indices"]},
            "pressed": {"ox": prs["ox"], "oy": prs["oy"], "w": prs["w"], "h": prs["h"], "indices": prs["indices"]},
        })

    shn = read_icn(agg_entry(agg, entries, MENU_LANTERN_ICN))
    base = _frame(shn, MENU_LANTERN_BASE_FRAME)
    frames = [_frame(shn, i)
              for i in range(MENU_LANTERN_ANIM_FIRST, MENU_LANTERN_ANIM_LAST + 1, MENU_LANTERN_STRIDE)]
    lantern = {"base": base, "frames": frames}

    # Подсветка двери: SHNGANIM[18], срез строк [doorOffsetY:h] + переиндексация палитрой 8.
    dfull = _frame(shn, MENU_DOOR_FRAME)
    dw, dh = dfull["w"], dfull["h"]
    cropped = dfull["indices"][MENU_DOOR_OFFSET_Y * dw: dh * dw]
    door = {
        "ox": dfull["ox"], "oy": dfull["oy"] + MENU_DOOR_OFFSET_Y,
        "w": dw, "h": dh - MENU_DOOR_OFFSET_Y,
        "indices": bytes(PAL8[i] for i in cropped),
    }
    # Подменю NEW GAME: панель REDBACK + 4 кнопки BTNNEWGM (released/pressed)
    rb = read_icn(agg_entry(agg, entries, NG_PANEL_ICN))
    ng_panel = _frame(rb, 0)
    ngb = read_icn(agg_entry(agg, entries, NG_BTN_ICN))
    ng_buttons = []
    for i, name in enumerate(NG_BTN_NAME):
        r = _frame(ngb, i * 2)
        p = _frame(ngb, i * 2 + 1)
        ng_buttons.append({"name": name, "released": r, "pressed": p,
                           "x": NG_BTN_X, "y": NG_BTN_Y[i]})
    newgame = {"panel": ng_panel, "buttons": ng_buttons}
    return palette, bg, buttons, lantern, door, newgame


def background_tiles(bg):
    """Раскрой фона на куски ≤319 (FT812-совместимые)."""
    return [
        {"indices": crop_indices(bg["raw"], bg["w"], sx, sy, w, h), "w": w, "h": h, "dx": dx, "dy": dy}
        for sx, sy, w, h, dx, dy in split_ui_blits([(0, 0, bg["w"], bg["h"], 0, 0)])
    ]


def build_payload(palette, tiles, buttons, lantern, door, newgame):
    """RAM_G-payload меню (base 0). Проставляет addr на каждый блок. Возвращает (payload, addrs)."""
    payload = bytearray()

    def put(raw: bytes) -> int:
        addr = MENU_RAMG_BASE + align(len(payload), 4)
        while MENU_RAMG_BASE + len(payload) < addr:
            payload.append(0)
        payload.extend(raw)
        return addr

    transparent_addr = put(palette_argb4444(palette))        # index 0 → alpha 0 (спрайты)
    opaque_addr = put(palette_argb4444_opaque(palette))      # index 0 непрозрачный (фон)
    for t in tiles:
        t["addr"] = put(t["indices"])
    for b in buttons:
        b["rel_addr"] = put(b["released"])
        b["hover"]["addr"] = put(b["hover"]["indices"])
        b["pressed"]["addr"] = put(b["pressed"]["indices"])
    lantern["base"]["addr"] = put(lantern["base"]["indices"])
    for f in lantern["frames"]:
        f["addr"] = put(f["indices"])
    door["addr"] = put(door["indices"])
    newgame["panel"]["addr"] = put(newgame["panel"]["indices"])
    for b in newgame["buttons"]:
        b["released"]["addr"] = put(b["released"]["indices"])
        b["pressed"]["addr"] = put(b["pressed"]["indices"])
    return payload, {"transparent": transparent_addr, "opaque": opaque_addr}


def _sprite_dl(L, addr, w, h, dx, dy):
    """4 команды DL одного спрайта (16Б): SOURCE/LAYOUT/SIZE/VERTEX2F. Позиция dx,dy в логич. px."""
    L.append(f"                FT_BITMAP_SOURCE #{addr:06X}")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {w}, {h}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {scaled_screen_pixels(w)}, {scaled_screen_pixels(h)}")
    L.append(f"                FT_VERTEX2F {scaled_vertex2f_units(dx)}, {scaled_vertex2f_units(dy)}")


def emit_inc(addrs, tiles, buttons, lantern, door, newgame, pak):
    L = []
    L.append("; Сгенерировано Source/Tools/menu_pack.py — ассеты главного меню (hover/pressed + фонарь).")
    L.append("                ifndef _HMM2_GENERATED_MENU_")
    L.append("                define _HMM2_GENERATED_MENU_")
    L.append("")
    L.append(f"MENU_TRANSPARENT_PAL_RAMG EQU #{addrs['transparent']:06X}")
    L.append(f"MENU_OPAQUE_PAL_RAMG      EQU #{addrs['opaque']:06X}")
    L.append(f"MENU_SPRITE_DL_SIZE       EQU {SPRITE_DL_SIZE}")
    L.append("")

    # --- статический фон: пролог состояния FT812 + opaque-палитра + тайлы (без DISPLAY) ---
    L.append("MenuBg_DL:")
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
    L.append("                FT_PALETTE_SOURCE MENU_OPAQUE_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    for t in tiles:
        _sprite_dl(L, t["addr"], t["w"], t["h"], t["dx"], t["dy"])
    L.append("                FT_END")
    L.append("MenuBg_DL_SIZE EQU $ - MenuBg_DL")
    L.append("")

    # --- пролог/эпилог спрайтов (фонарь + кнопки): transparent-палитра + BEGIN / END ---
    L.append("MenuSpritesProlog_DL:")
    L.append("                FT_PALETTE_SOURCE MENU_TRANSPARENT_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("MenuSpritesProlog_DL_SIZE EQU $ - MenuSpritesProlog_DL")
    L.append("MenuSpritesEnd_DL:")
    L.append("                FT_END")
    L.append("MenuSpritesEnd_DL_SIZE EQU $ - MenuSpritesEnd_DL")
    L.append("")

    # --- фонарь: статичная база + прорежённые кадры анимации (16Б каждый) ---
    lb = lantern["base"]
    L.append("MenuLanternBase_DL:")
    _sprite_dl(L, lb["addr"], lb["w"], lb["h"], lb["ox"], lb["oy"])
    L.append("")
    for i, f in enumerate(lantern["frames"]):
        L.append(f"MenuLantern_{i}_DL:")
        _sprite_dl(L, f["addr"], f["w"], f["h"], f["ox"], f["oy"])
    L.append("")
    L.append(f"MENU_LANTERN_FRAMES EQU {len(lantern['frames'])}")
    L.append(f"MENU_LANTERN_SHIFT  EQU {MENU_LANTERN_SHIFT}")
    L.append("MenuLanternFrameTab:")
    for i in range(len(lantern["frames"])):
        L.append(f"                DEFW MenuLantern_{i}_DL")
    L.append("")

    # --- кнопки: на кнопку 3 блока (rel/hover/pressed) по 16Б + таблица указателей ---
    for b in buttons:
        L.append(f"MenuBtn_{b['name']}_REL_DL:")
        _sprite_dl(L, b["rel_addr"], b["w"], b["h"], b["ox"], b["oy"])
        L.append(f"MenuBtn_{b['name']}_HOVER_DL:")
        hov = b["hover"]
        _sprite_dl(L, hov["addr"], hov["w"], hov["h"], hov["ox"], hov["oy"])
        L.append(f"MenuBtn_{b['name']}_PRESSED_DL:")
        prs = b["pressed"]
        _sprite_dl(L, prs["addr"], prs["w"], prs["h"], prs["ox"], prs["oy"])
    L.append("")
    L.append(f"MENU_BUTTON_COUNT EQU {len(buttons)}")
    L.append("; на кнопку 3 указателя на 16-байтные DL-блоки: released, hover, pressed.")
    L.append("MenuBtnFrameTab:")
    for b in buttons:
        L.append(f"                DEFW MenuBtn_{b['name']}_REL_DL, MenuBtn_{b['name']}_HOVER_DL, MenuBtn_{b['name']}_PRESSED_DL")
    L.append("")

    # --- подсветка двери (settingsArea hover) — 16-байтный DL-блок + зона настроек ---
    L.append("MenuDoor_DL:")
    _sprite_dl(L, door["addr"], door["w"], door["h"], door["ox"], door["oy"])
    sx, sy, sw, sh = SETTINGS_AREA
    L.append(f"MenuSettingsZone:    DEFW {sx}, {sy}, {sx + sw}, {sy + sh}   ; зона настроек (door highlight)")
    L.append("")

    # --- Подменю NEW GAME: панель REDBACK (472 лог → физ >511: SIZE_H + сброс) + 4 кнопки ---
    pn = newgame["panel"]
    px, py = NG_PANEL_POS
    pw16, ph16 = scaled_screen_pixels(pn["w"]), scaled_screen_pixels(pn["h"])
    L.append("; Подменю NEW GAME (ориг. HoMM2, геометрия fheroes2 1.0.0 drawButtonPanel)")
    L.append("MenuNgPanel_DL:")
    L.append(f"                FT_BITMAP_SOURCE #{pn['addr']:06X}")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {pn['w']}, {pn['h']}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {pw16}, {ph16}")
    L.append(f"                FT_BITMAP_SIZE_H {pw16}, {ph16}")
    L.append(f"                FT_VERTEX2F {scaled_vertex2f_units(px)}, {scaled_vertex2f_units(py)}")
    L.append("                FT_BITMAP_SIZE_H 0, 0             ; сброс (ловушка &511)")
    L.append("MenuNgPanel_DL_SIZE EQU $ - MenuNgPanel_DL")
    for b in newgame["buttons"]:
        L.append(f"MenuNgBtn_{b['name']}_REL_DL:")
        _sprite_dl(L, b["released"]["addr"], b["released"]["w"], b["released"]["h"], b["x"], b["y"])
        L.append(f"MenuNgBtn_{b['name']}_PRS_DL:")
        _sprite_dl(L, b["pressed"]["addr"], b["pressed"]["w"], b["pressed"]["h"], b["x"], b["y"])
    L.append(f"MENU_NG_BUTTON_COUNT EQU {len(newgame['buttons'])}")
    L.append("MenuNgBtnTab:                        ; на кнопку 2 указателя: released, pressed")
    for b in newgame["buttons"]:
        L.append(f"                DEFW MenuNgBtn_{b['name']}_REL_DL, MenuNgBtn_{b['name']}_PRS_DL")
    L.append("MenuNgZones:                         ; зоны hit-test (x0,y0,x1,y1 логич.)")
    for b in newgame["buttons"]:
        bw, bh = b["released"]["w"], b["released"]["h"]
        L.append(f"                DEFW {b['x']}, {b['y']}, {b['x'] + bw}, {b['y'] + bh}   ; {b['name']}")
    L.append("")

    # --- зоны кнопок для hit-test (ЛОГИЧЕСКИЕ координаты 640×480) ---
    L.append("; запись: x0,y0,x1,y1 (4×2б). Индекс зоны = индекс кнопки (0=New Game).")
    L.append("MenuButtonZones:")
    for b in buttons:
        x0, y0, x1, y1 = b["ox"], b["oy"], b["ox"] + b["w"], b["oy"] + b["h"]
        L.append(f"                DEFW {x0}, {y0}, {x1}, {y1}   ; [{b['index']:2d}] {b['name']}")
    L.append("")

    # --- метаданные HMM2MENU.PAK (грузится загрузчиком с SD в Menu_Enter) ---
    L.append(f"MENU_RAMG_BASE       EQU #{MENU_RAMG_BASE:06X}")
    L.append(f"MENU_PAYLOAD_BYTES   EQU {pak['payload_bytes']}")
    L.append(f"MENU_PAYLOAD_SECTORS EQU {pak['payload_sectors']}")
    L.append(f"MENU_BODY_SECTOR     EQU {pak['body_start_sector']}   ; payload начинается с этого сектора файла")
    L.append('MenuPakName:         DEFB "HMM2MENU.PAK", 0')
    L.append("")
    L.append("                endif")
    MENU_INC.write_text("\n".join(L), encoding="utf-8")


def _blit(px, img_w, img_h, palette, sprite, ox, oy):
    indices, w, h = sprite["indices"], sprite["w"], sprite["h"]
    for y in range(h):
        for x in range(w):
            idx = indices[y * w + x]
            if idx == TRANSPARENT:
                continue
            dx, dy = ox + x, oy + y
            if 0 <= dx < img_w and 0 <= dy < img_h:
                px[dx, dy] = palette[idx]


def render_preview(palette, bg, buttons, lantern, out_path: Path) -> None:
    from PIL import Image

    img = Image.new("RGB", (bg["w"], bg["h"]))
    px = img.load()
    raw = bg["raw"]
    for y in range(bg["h"]):
        for x in range(bg["w"]):
            px[x, y] = palette[raw[y * bg["w"] + x]]
    _blit(px, bg["w"], bg["h"], palette, lantern["base"], lantern["base"]["ox"], lantern["base"]["oy"])
    for b in buttons:
        _blit(px, bg["w"], bg["h"], palette,
              {"indices": b["released"], "w": b["w"], "h": b["h"]}, b["ox"], b["oy"])
    img.save(out_path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Ассеты главного меню HMM2 (hover/pressed + фонарь).")
    ap.add_argument("--preview", type=Path, default=None, help="PNG-реконструкция меню для сверки")
    args = ap.parse_args()

    palette, bg, buttons, lantern, door, newgame = load_menu_sources()
    tiles = background_tiles(bg)

    if args.preview:
        render_preview(palette, bg, buttons, lantern, args.preview)
        print(f"preview: {args.preview}")
        return 0

    payload, addrs = build_payload(palette, tiles, buttons, lantern, door, newgame)
    assert len(payload) <= 0x0E0000, f"menu payload {len(payload)} превышает зону курсора #0E0000"
    summary = build_pak(
        [{"type": TYPE_RAMG_BLOB, "target": MENU_RAMG_BASE, "data": bytes(payload)}],
        MENU_PAK_PATH,
    )
    pak = {
        "payload_bytes": len(payload),
        "payload_sectors": (len(payload) + SECTOR - 1) // SECTOR,
        "body_start_sector": summary["body_start_sector"],
    }
    emit_inc(addrs, tiles, buttons, lantern, door, newgame, pak)
    print(f"menu pack -> {MENU_PAK_PATH.name}: фон {len(tiles)} кусков + {len(buttons)} кнопок x3 кадра "
          f"+ фонарь(база+{len(lantern['frames'])} кадров), payload={len(payload)} байт "
          f"({pak['payload_sectors']} сект), PAK={summary['total_bytes']} байт, blob с сектора {pak['body_start_sector']}")
    print(f"  inc: {MENU_INC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
