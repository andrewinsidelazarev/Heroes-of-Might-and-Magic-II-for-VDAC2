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
import os
from pathlib import Path

from agg_tools import read_agg_index_with_expansion
from object_atlas import agg_entry, read_icn, read_palette
from pak_builder import build_pak, TYPE_RAMG_BLOB, SECTOR
from battle_pack import compose_help_window       # переиспользуем генератор ПКМ-справки (BUYBUILD-рамка)
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

# --- Экран выбора сценария (game_scenarioinfo.cpp ChooseNewMap, геометрия fheroes2 1.0.0):
#     панель NGHSBKG[0] 420×427 центрирована → rt = ((640−420)/2, (480−427)/2) = (110, 26).
#     Иконки сложности + кнопки OKAY/CANCEL уже ВБЕЙКАНЫ в панель. Наша карта = SKIRMISH
#     («Skirmish», map-difficulty Normal). Экран — отдельная сцена (composite 640×480 в base 0,
#     эксклюзивно с меню-payload; переход = пере-стрим, как город). ---
SCEN_BG_ICN = "HEROES.ICN"
SCEN_PANEL_ICN = "NGHSBKG.ICN"
SCEN_CURSOR_ICN = "NGEXTRA.ICN"                  # [62] = рамка выбора сложности 71×71
SCEN_BTN_ICN = "SYSTEM.ICN"                      # [2]=OKAY pressed, [4]=CANCEL pressed 95×25
SCEN_RT = (110, 26)                              # позиция панели
SCEN_MAP_NAME = "Skirmish"
SCEN_DIFF_NAMES = ["Easy", "Normal", "Hard", "Expert", "Impossible"]
SCEN_DIFF_X = [21, 98, 174, 251, 328]           # coordDifficulty[i].x − rt.x
SCEN_DIFF_Y = 91                                 # coordDifficulty.y − rt.y
# rating = 50 + mapDiffBonus(Normal=+20) + gameDiffBonus(Easy0/Normal30/Hard50/Expert70/Imp90)
SCEN_RATINGS = [70, 100, 120, 140, 160]
SCEN_OK_XY = (31, 380)                           # buttonOk − rt (pressed overlay)
SCEN_CANCEL_XY = (287, 380)

# ПКМ-справки экрана сценария (showStandardTextMessage, Dialog::ZERO — показ пока ПКМ зажат).
# Тексты ТОЧНО из game_scenarioinfo.cpp:442-463 (SELECT/Difficulty/Rating/Okay/Cancel) и
# player_info.cpp QueueEventProcessing:286-308 (Opponents/Class). Индекс = зона (см. ScenHelpZones).
SCEN_HELP_WINDOWS = [
    ("Scenario", "Click here to select which scenario to play."),
    ("Game Difficulty",
     "This lets you change the starting difficulty at which you will play. Higher difficulty levels "
     "start you off with fewer resources, and at the higher settings, give extra resources to the computer."),
    ("Difficulty Rating",
     "The difficulty rating reflects a combination of various settings for your game. This number will "
     "be applied to your final score."),
    ("Okay", "Click to accept these settings and start a new game."),
    ("Cancel", "Click to return to the main menu."),
    ("Opponents",
     "This lets you change player starting positions and colors. A particular color will always start in "
     "a particular location. Some positions may only be played by a computer player or only by a human player."),
    ("Class",
     "This lets you change the class of a player. Classes are not always changeable. Depending on the "
     "scenario, a player may receive additional towns and/or heroes not of their primary alignment."),
]


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


def build_scenario(agg, entries, palette, bg):
    """Экран выбора сценария (ChooseNewMap): composite 640×480 (фон HEROES + панель NGHSBKG[0] +
    статичные тексты Scenario/имя карты/Game Difficulty + 5 названий сложности) → тайлы ≤319;
    хвост-спрайты (transparent): курсор-рамка NGEXTRA[62], OKAY/CANCEL pressed, 5 текстов рейтинга.
    Отдельная PAK-entry, стрим в base 0 (эксклюзивно с меню). Возврат (payload, meta)."""
    W, H = bg["w"], bg["h"]
    cv_bg = bytearray(bg["raw"])                 # СЛОЙ 1: фон HEROES 640×480 (opaque) → ScenBg_DL
    cv = bytearray([TRANSPARENT]) * (W * H)      # СЛОЙ 2: панель+контент (transparent) → ScenPanel_DL
    rt = SCEN_RT                                 # отдельный DL → глоб. Render_WindowShadowDL (тень как в бою)
    pnl = _frame(read_icn(agg_entry(agg, entries, SCEN_PANEL_ICN)), 0)
    fnt = read_icn(agg_entry(agg, entries, "FONT.ICN"))
    smf = read_icn(agg_entry(agg, entries, "SMALFONT.ICN"))
    SPW = {"n": 6, "s": 4}

    def tw(font, t):
        f = fnt if font == "n" else smf
        return sum(SPW[font] if c == " " else f[ord(c) - 32][0]["w"] for c in t)

    def blit(indices, sw, sh, dx, dy, transp=False):
        for y in range(sh):
            yy = dy + y
            if not (0 <= yy < H):
                continue
            for x in range(sw):
                xx = dx + x
                if not (0 <= xx < W):
                    continue
                v = indices[y * sw + x]
                if transp and v == TRANSPARENT:
                    continue
                cv[yy * W + xx] = v

    def text(font, t, x, y):
        f = fnt if font == "n" else smf
        cx = x
        for c in t:
            if c == " ":
                cx += SPW[font]
                continue
            gh, ge = f[ord(c) - 32]
            gi = decode_icn_indices(gh, ge)
            gw, gg, goy = gh["w"], gh["h"], gh.get("oy", 0)
            for yy in range(gg):
                py = y + goy + yy
                if 0 <= py < H:
                    for xx in range(gw):
                        if gi[yy * gw + xx] != TRANSPARENT and 0 <= cx + xx < W:
                            cv[py * W + cx + xx] = gi[yy * gw + xx]
            cx += gw

    # Панель на прозрачном слое (тень окна рисует глоб. Render_WindowShadowDL в MenuScen_Render)
    blit(pnl["indices"], pnl["w"], pnl["h"], rt[0], rt[1], transp=True)
    # SELECT: оригинал перерисовывает NGEXTRA[64] поверх (в панели она в неверной позиции)
    _sel = _frame(read_icn(agg_entry(agg, entries, "NGEXTRA.ICN")), 64)
    blit(_sel["indices"], _sel["w"], _sel["h"], rt[0] + 309, rt[1] + 45, transp=True)

    def ctext(s, y):                                 # оригинал: text.draw(rt.x, y, rt.width) → ЦЕНТР
        text("n", s, rt[0] + (pnl["w"] - tw("n", s)) // 2, y)   # ui_text.cpp:486 offsetX=(W-w)/2

    ctext("Scenario:", rt[1] + 25)
    ctext(SCEN_MAP_NAME, rt[1] + 48)
    ctext("Game Difficulty:", rt[1] + 75)
    for i, nm in enumerate(SCEN_DIFF_NAMES):        # названия сложности под иконками (smallWhite)
        off = 1 if i == 1 else 0                     # Normal: +1 (иррегулярный интервал ориг.)
        dx = rt[0] + 24 + 31 + 77 * i + off - tw("s", nm) // 2
        text("s", nm, dx, rt[1] + 95 + 69)

    # --- Opponents / Class секции (playersInfo.RedrawInfo, 1.0.0) — НЕ выкидывать! ---
    # Скирмиш: 1 игрок Knight (Hampshire), human Blue. Статичен (в скирмише не меняется) → бейк в панель.
    ng = read_icn(agg_entry(agg, entries, "NGEXTRA.ICN"))
    def _gs4p(w):                                     # Game::GetStep4Player(0, w, 1) = 2.5w
        return (w * 5) // 2
    # Opponents: текст @ rt.y+180 (ЦЕНТР), портрет @ (rt.x+24, rt.y+197) + GetStep4Player
    ctext("Opponents:", rt[1] + 180)
    p_ref = _frame(ng, 3)                             # playerTypeImage (ширина/высота для roi)
    prx, pry = rt[0] + 24 + _gs4p(p_ref["w"]), rt[1] + 197
    psh, pic = _frame(ng, 60), _frame(ng, 33)         # тень + портрет human Blue (9+GetIndex(BLUE=0)+24)
    blit(psh["indices"], psh["w"], psh["h"], prx - 5, pry + 3, transp=True)
    blit(pic["indices"], pic["w"], pic["h"], prx, pry, transp=True)
    pname = "Blue"                                    # имя игрока (Color::String)
    _mw = pic["w"] - 4
    text("s", pname, prx + 2 + (_mw - tw("s", pname)) // 2, pry + p_ref["h"] - 1)
    # Class: текст @ rt.y+264 (ЦЕНТР), класс @ (rt.x+24, rt.y+281) + GetStep4Player
    ctext("Class:", rt[1] + 264)
    c_ref = _frame(ng, 51)                            # classImage
    cx, cy = rt[0] + 24 + _gs4p(c_ref["w"]), rt[1] + 281
    csh, cic = _frame(ng, 61), _frame(ng, 51)         # тень + класс KNGT active (51)
    blit(csh["indices"], csh["w"], csh["h"], cx - 5, cy + 3, transp=True)
    blit(cic["indices"], cic["w"], cic["h"], cx, cy, transp=True)
    rname = "Knight"                                  # Race::String(KNGT), playerCount<=4
    text("s", rname, cx + (cic["w"] - tw("s", rname)) // 2, cy + cic["h"] + 4)
    # Handicap: human NONE = NGEXTRA[0] @ (classOffset.x, classOffset.y+69)
    h_ref = _frame(ng, 0)
    hx, hy = rt[0] + 24 + _gs4p(h_ref["w"]), cy + 69
    hsh, hic = _frame(ng, 59), _frame(ng, 0)
    blit(hsh["indices"], hsh["w"], hsh["h"], hx - 5, hy + 3, transp=True)
    blit(hic["indices"], hic["w"], hic["h"], hx, hy, transp=True)

    # Фон HEROES НЕ включается в scenario payload — берётся из меню (MenuBg_DL, base 0).
    # Панель+контент (transparent) — только bbox панели (rt + размеры NGHSBKG[0]).
    PX, PY, PW, PH = rt[0], rt[1], pnl["w"], pnl["h"]
    panel_tiles = [{"indices": crop_indices(bytes(cv), W, sx, sy, w, h), "w": w, "h": h, "dx": dx, "dy": dy}
                   for sx, sy, w, h, dx, dy in split_ui_blits([(PX, PY, PW, PH, PX, PY)])]
    _pv = os.environ.get("SCEN_PREVIEW")
    if _pv:
        from PIL import Image
        _comp = bytearray(cv_bg)                       # совместить слои (тень рисует ASM, тут только сверка позиций)
        for _i, _v in enumerate(cv):
            if _v != TRANSPARENT:
                _comp[_i] = _v
        _flat = [c for rgb in palette for c in rgb]
        im = Image.new("P", (W, H)); im.putpalette(_flat); im.putdata(bytes(_comp)); im.convert("RGB").save(_pv)
        print(f"scenario preview -> {_pv}")

    cur = _frame(read_icn(agg_entry(agg, entries, SCEN_CURSOR_ICN)), 62)
    sysfr = read_icn(agg_entry(agg, entries, SCEN_BTN_ICN))
    ok = _frame(sysfr, 2)
    cancel = _frame(sysfr, 4)

    def rating_sprite(n):                            # «Rating N%» normalWhite на transparent-канве
        s = f"Rating {n}%"
        w = tw("n", s)
        h = 16
        buf = bytearray([TRANSPARENT]) * (w * h)
        cx = 0
        for c in s:
            if c == " ":
                cx += SPW["n"]
                continue
            gh, ge = fnt[ord(c) - 32]
            gi = decode_icn_indices(gh, ge)
            gw, gg, goy = gh["w"], gh["h"], gh.get("oy", 0)
            for yy in range(gg):
                py = goy + yy
                if 0 <= py < h:
                    for xx in range(gw):
                        if gi[yy * gw + xx] != TRANSPARENT and cx + xx < w:
                            buf[py * w + cx + xx] = gi[yy * gw + xx]
            cx += gw
        return {"indices": bytes(buf), "w": w, "h": h}

    ratings = [rating_sprite(n) for n in SCEN_RATINGS]

    # Scenario = ОКНО-ПОВЕРХ меню: панель+хвост стримятся в область КАДРОВ ФОНАРЯ (#064840),
    # эксклюзивно с ними (фонарь замирает на базе, пока открыто окно — в подменю он и так статичен).
    # Фон HEROES, ОБЕ палитры и база фонаря берутся из МЕНЮ (не дублируются) → переход показывает
    # только фон+базу (не читает область кадров), панель стримится «за кадром» → без чёрного/мусора.
    SCEN_PANEL_BASE = 0x064840                       # = MenuLantern_0 (первый кадр фонаря)
    payload = bytearray()

    def put(raw):
        addr = SCEN_PANEL_BASE + align(len(payload), 4)
        while SCEN_PANEL_BASE + len(payload) < addr:
            payload.append(0)
        payload.extend(raw)
        return addr

    for t in panel_tiles:                            # панель+контент (transp), палитра МЕНЮ #000000
        t["addr"] = put(t["indices"])
    cur["addr"] = put(cur["indices"])
    ok["addr"] = put(ok["indices"])
    cancel["addr"] = put(cancel["indices"])
    for r in ratings:
        r["addr"] = put(r["indices"])
    assert SCEN_PANEL_BASE + len(payload) <= 0x0A0340, \
        f"scenario окно {len(payload)}Б за #064840 вылезло за кадры фонаря (#0A0340)"
    meta = {"transp": 0x000000, "panel_tiles": panel_tiles, "panel_base": SCEN_PANEL_BASE,
            "cursor": cur, "ok": ok, "cancel": cancel, "ratings": ratings, "rt": rt}
    return bytes(payload), meta


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

    # --- ЭКРАН ВЫБОРА СЦЕНАРИЯ (2-я PAK-entry, стрим в base 0 эксклюзивно с меню) ---
    sc = pak["scen"]
    L.append("; Экран сценария (ChooseNewMap) = ОКНО-ПОВЕРХ меню: фон = MenuBg_DL, база фонаря =")
    L.append("; MenuLanternBase_DL; панель @ #064840 (область кадров фонаря). Тень = глоб. Render_WindowShadowDL.")
    # Панель+контент (transp #000000, палитра МЕНЮ) — ОТДЕЛЬНЫЙ DL, копируется дважды: тень + сам.
    L.append("ScenPanel_DL:")
    L.append(f"                FT_PALETTE_SOURCE #{sc['transp']:06X}")
    L.append("                FT_BEGIN FT_BITMAPS")
    for t in sc["panel_tiles"]:
        _sprite_dl(L, t["addr"], t["w"], t["h"], t["dx"], t["dy"])
    L.append("                FT_END")
    L.append("ScenPanel_DL_SIZE EQU $ - ScenPanel_DL")
    L.append("ScenSpritesProlog_DL:")
    L.append(f"                FT_PALETTE_SOURCE #{sc['transp']:06X}")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("ScenSpritesProlog_DL_SIZE EQU $ - ScenSpritesProlog_DL")
    L.append("ScenSpritesEnd_DL:")
    L.append("                FT_END")
    L.append("ScenSpritesEnd_DL_SIZE EQU $ - ScenSpritesEnd_DL")
    rt = sc["rt"]
    cur = sc["cursor"]
    for i, dx in enumerate(SCEN_DIFF_X):            # 5 позиций курсор-рамки (по сложности)
        L.append(f"ScenCursor{i}_DL:")                # ориг: levelCursor @ coordDifficulty − levelCursorOffset(3)
        _sprite_dl(L, cur["addr"], cur["w"], cur["h"], rt[0] + dx - 3, rt[1] + SCEN_DIFF_Y - 3)
    L.append("ScenCursorTab:                       ; [difficulty] → DL-блок рамки")
    for i in range(5):
        L.append(f"                DEFW ScenCursor{i}_DL")
    ok, cancel = sc["ok"], sc["cancel"]
    L.append("ScenOkPressed_DL:")
    _sprite_dl(L, ok["addr"], ok["w"], ok["h"], rt[0] + SCEN_OK_XY[0], rt[1] + SCEN_OK_XY[1])
    L.append("ScenCancelPressed_DL:")
    _sprite_dl(L, cancel["addr"], cancel["w"], cancel["h"], rt[0] + SCEN_CANCEL_XY[0], rt[1] + SCEN_CANCEL_XY[1])
    for i, r in enumerate(sc["ratings"]):           # рейтинг центрирован по панели, y=rt+385
        rx = rt[0] + (420 - r["w"]) // 2
        L.append(f"ScenRating{i}_DL:")
        _sprite_dl(L, r["addr"], r["w"], r["h"], rx, rt[1] + 385)
    L.append("ScenRatingTab:                       ; [difficulty] → DL-блок «Rating N%»")
    for i in range(5):
        L.append(f"                DEFW ScenRating{i}_DL")
    L.append("MENU_SCEN_DIFF_COUNT EQU 5")
    L.append("ScenDiffZones:                       ; зоны иконок сложности (x0,y0,x1,y1 логич.)")
    for dx in SCEN_DIFF_X:
        zx, zy = rt[0] + dx, rt[1] + SCEN_DIFF_Y
        L.append(f"                DEFW {zx}, {zy}, {zx + cur['w']}, {zy + cur['h']}")
    okx, oky = rt[0] + SCEN_OK_XY[0], rt[1] + SCEN_OK_XY[1]
    cnx, cny = rt[0] + SCEN_CANCEL_XY[0], rt[1] + SCEN_CANCEL_XY[1]
    L.append(f"ScenOkZone:     DEFW {okx}, {oky}, {okx + ok['w']}, {oky + ok['h']}")
    L.append(f"ScenCancelZone: DEFW {cnx}, {cny}, {cnx + cancel['w']}, {cny + cancel['h']}")
    L.append(f"SCEN_PAYLOAD_SECTORS EQU {sc['sectors']}")
    L.append(f"SCEN_BODY_SECTOR     EQU {sc['body_sector']}")
    L.append("")
    # --- ПКМ-справки scenario: [idx] → сектор/размер PAK; окно центрируется на экране ---
    hlp = sc["helps"]
    L.append(f"SCEN_HELP_AREA       EQU #{sc['help_area']:06X}   ; свободная зона стрима справка-окна")
    L.append(f"MENU_SCEN_HELP_COUNT EQU {len(hlp)}")
    L.append("ScenHelpSecTab: DEFW " + ", ".join(str(hm["sec"]) for hm in hlp))
    L.append("ScenHelpSecN:   DEFB " + ", ".join(str(hm["sectors"]) for hm in hlp))
    L.append("ScenHelpPre_DL:                       ; общий пролог всех окон справок (transp — фон вокруг рамки прозрачен)")
    L.append("                FT_BITMAP_TRANSFORM_A 160")
    L.append("                FT_BITMAP_TRANSFORM_E 160")
    L.append("                FT_PALETTE_SOURCE MENU_TRANSPARENT_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("                FT_BITMAP_SOURCE SCEN_HELP_AREA")
    L.append("ScenHelpPre_DL_SIZE EQU $ - ScenHelpPre_DL")
    for i, hm in enumerate(hlp):
        hw, hh = hm["W"], hm["H"]
        hx, hy = (640 - hw) // 2, (480 - hh) // 2
        L.append(f"ScenHelp{i}_DL:                       ; LAYOUT/SIZE/VERTEX окна {i} (пролог общий)")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {hw}, {hh}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {hw * 16 // 10}, {hh * 16 // 10}")
        L.append(f"                FT_BITMAP_SIZE_H {hw * 16 // 10}, {hh * 16 // 10}")
        L.append(f"                FT_VERTEX2F {hx * 256 // 10}, {hy * 256 // 10}")
    L.append(f"SCEN_HELP_DL_SIZE EQU $ - ScenHelp{len(hlp) - 1}_DL   ; per-окно размер одинаков (4 команды)")
    L.append("ScenHelpDLTab:  DEFW " + ", ".join(f"ScenHelp{i}_DL" for i in range(len(hlp))))
    # Зоны ПКМ-справок (логич. 640×480): [idx] → x0,y0,x1,y1. rt=(110,26).
    rtx, rty = rt[0], rt[1]
    ok_w, ok_h = sc["ok"]["w"], sc["ok"]["h"]
    cn_w, cn_h = sc["cancel"]["w"], sc["cancel"]["h"]
    st = rtx + 24 + (62 * 5) // 2                     # GetStep4Player центр портрета/класса (=289)
    zones = [
        (rtx + 309, rty + 45, rtx + 309 + 80, rty + 45 + 19),                        # 0 Scenario (SELECT)
        (rtx + 21, rty + 91, rtx + 328 + 71, rty + 91 + 71),                         # 1 Game Difficulty (bbox 5)
        (rtx + 150, rty + 385, rtx + 270, rty + 385 + 16),                           # 2 Difficulty Rating
        (rtx + SCEN_OK_XY[0], rty + SCEN_OK_XY[1], rtx + SCEN_OK_XY[0] + ok_w, rty + SCEN_OK_XY[1] + ok_h),      # 3 Okay
        (rtx + SCEN_CANCEL_XY[0], rty + SCEN_CANCEL_XY[1], rtx + SCEN_CANCEL_XY[0] + cn_w, rty + SCEN_CANCEL_XY[1] + cn_h),  # 4 Cancel
        (st, rty + 197, st + 62, rty + 197 + 58),                                    # 5 Opponents (portrait)
        (st, rty + 281, st + 62, rty + 281 + 45),                                    # 6 Class
    ]
    L.append("ScenHelpZones:                       ; [idx] → x0,y0,x1,y1 (логич.) для right-click")
    for z in zones:
        L.append(f"                DEFW {z[0]}, {z[1]}, {z[2]}, {z[3]}")
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
    agg, entries = read_agg_index_with_expansion(AGG_PATH)
    scen_payload, scen_meta = build_scenario(agg, entries, palette, bg)
    assert len(scen_payload) <= 0x0E0000, f"scenario payload {len(scen_payload)} превышает #0E0000"
    # ПКМ-справки scenario: 7 окон (BUYBUILD-рамка), стрим по idx в зону @ #090BC4 (сразу за
    # панелью-окном #064840+179340). Справка перекрывает хвост кадров фонаря и кнопки меню — в
    # scenario они не рисуются, а при выходе ngcancel рестримит меню целиком. Потолок = курсор #0E0000.
    SCEN_HELP_AREA = 0x090BC4
    scen_helps = [compose_help_window(agg, entries, t, b) for t, b in SCEN_HELP_WINDOWS]
    for hb, hw, hh in scen_helps:
        assert hw * hh <= 0x0E0000 - SCEN_HELP_AREA, \
            f"справка {hw}x{hh}={hw * hh}Б не влезает в зону #090BC4..#0E0000 ({0x0E0000 - SCEN_HELP_AREA}Б)"
    summary = build_pak(
        [{"type": TYPE_RAMG_BLOB, "target": MENU_RAMG_BASE, "data": bytes(payload)},
         {"type": TYPE_RAMG_BLOB, "target": MENU_RAMG_BASE, "data": bytes(scen_payload)}]
        + [{"type": TYPE_RAMG_BLOB, "target": 0, "data": bytes(hb)} for hb, _, _ in scen_helps],
        MENU_PAK_PATH,
    )
    body = summary["body_start_sector"]
    menu_secs = (len(payload) + SECTOR - 1) // SECTOR
    scen_meta["sectors"] = (len(scen_payload) + SECTOR - 1) // SECTOR
    scen_meta["body_sector"] = body + menu_secs   # 2-я entry идёт сразу за меню-payload
    hsec = scen_meta["body_sector"] + scen_meta["sectors"]   # справки подряд после scenario payload
    help_meta = []
    for hb, hw, hh in scen_helps:
        hs = (len(hb) + SECTOR - 1) // SECTOR
        help_meta.append({"sec": hsec, "sectors": hs, "W": hw, "H": hh})
        hsec += hs
    scen_meta["helps"] = help_meta
    scen_meta["help_area"] = SCEN_HELP_AREA
    pak = {
        "payload_bytes": len(payload),
        "payload_sectors": menu_secs,
        "body_start_sector": body,
        "scen": scen_meta,
    }
    emit_inc(addrs, tiles, buttons, lantern, door, newgame, pak)
    print(f"menu pack -> {MENU_PAK_PATH.name}: фон {len(tiles)} кусков + {len(buttons)} кнопок x3 кадра "
          f"+ фонарь(база+{len(lantern['frames'])} кадров), payload={len(payload)} байт "
          f"({pak['payload_sectors']} сект); сценарий {len(scen_payload)} байт "
          f"({scen_meta['sectors']} сект, с сектора {scen_meta['body_sector']}); PAK={summary['total_bytes']} байт")
    print(f"  inc: {MENU_INC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
