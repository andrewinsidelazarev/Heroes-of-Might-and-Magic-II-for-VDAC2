#!/usr/bin/env python3
"""HMM2TOWN.PAK — потоковый PAK экрана города (cities). Первая новая категория стрим-архитектуры
(spg-загрузчик + PAK по категориям: карты/города/бои/музыка/SFX — всё в один SPG не влезает).

Стримится с SD загрузчиком в Town_Enter (НЕ SPG), как HMM2MENU.PAK. Knight-город: фон-постройки
TWNK* самопозиционируются по ox/oy ICN-хедера (TWNKCSTL@0,36; башни LTUR/RTUR; TVRN/MAGE/WEL2/THIE).
Композлю их в одно плоское 640×256 PALETTED4444-изображение → один RAM_G-blob + палитра.

Эмитит Source/ASM/generated_town.inc: TOWN_PAL_RAMG, Town_DL (рендер ×1.6), метаданные PAK.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from agg_tools import read_agg_index_with_expansion
from object_atlas import agg_entry, read_icn, read_palette
from pak_builder import build_pak, TYPE_RAMG_BLOB, SECTOR
from viewport_pack import align, decode_icn_indices, palette_argb4444_opaque, palette_argb4444

ROOT = Path(__file__).resolve().parents[2]
AGG_PATH = ROOT / "Assets" / "Original" / "DATA" / "HEROES2.AGG"
TOWN_INC = ROOT / "Source" / "ASM" / "generated_town.inc"
TOWN_PAK_PATH = ROOT / "Build" / "HMM2TOWN.PAK"

TOWN_RAMG_BASE = 0x000000          # сцена эксклюзивна (меню|adventure|town) → общий base 0
TOWN_W, TOWN_H = 640, 256          # область содержимого экрана замка (логич.)
TRANSPARENT = 0                    # индекс 0 = прозрачность в ICN-спрайтах
BACKDROP = 0                       # фон композита (чёрный) — позже CASTBKGK

# Knight-город: (ICN, frame). Порядок СТРОГО = getBuildingDrawingPriorities(KNGT)
# (castle_building_info.cpp:1446), back→front. Позиция каждого = ox/oy ICN-хедера
# (drawCastleDialogBuilding рисует по image.x()/y(), ui_castle.cpp:318). TENT НЕ рисуем —
# он уже впечатан в TOWNBKG0 (castle_dialog.cpp:153). Полностью застроенный замок.
# building→ICN сверен по getKnightBuildingArea (castle_building_info.cpp:32).
KNIGHT_BUILDINGS = [
    ("TWNKWEL2.ICN", 0),   # WEL2 — ферма (за замком, рисуется первой)
    ("TWNKCSTL.ICN", 0),   # CASTLE — центральный замок
    ("TWNKSPEC.ICN", 0),   # SPEC — спецсооружение (стена)
    ("TWNKCAPT.ICN", 0),   # CAPTAIN — покои капитана
    ("TWNKLTUR.ICN", 0),   # LEFTTURRET — левая башня
    ("TWNKRTUR.ICN", 0),   # RIGHTTURRET — правая башня
    ("TWNKMOAT.ICN", 0),   # MOAT — ров
    ("TWNKMARK.ICN", 0),   # MARKETPLACE — рынок
    ("TWNKDW_1.ICN", 0),   # DWELLING_MONSTER2
    ("TWNKTHIE.ICN", 0),   # THIEVESGUILD — гильдия воров
    ("TWNKTVRN.ICN", 0),   # TAVERN — таверна
    ("TWNKMAGE.ICN", 0),   # MAGEGUILD1 — гильдия магов (кадр 0 = ур.1)
    ("TWNKDW_4.ICN", 0),   # DWELLING_MONSTER5
    ("TWNKDW_5.ICN", 0),   # DWELLING_MONSTER6 (большое жилище, справа)
    ("TWNKDW_0.ICN", 0),   # DWELLING_MONSTER1
    ("TWNKDW_2.ICN", 0),   # DWELLING_MONSTER3
    ("TWNKDW_3.ICN", 0),   # DWELLING_MONSTER4
    ("TWNKWELL.ICN", 0),   # WELL — колодец
    ("TWNKSTAT.ICN", 0),   # STATUE — статуя (front)
]

# Имена зданий Knight (castle_building_info.cpp getBuildingName / GetStringBuilding) —
# СТРОГО параллельно KNIGHT_BUILDINGS (для hover-подсказки по зданию). Башни/ров — часть замка.
KNIGHT_NAMES = [
    "Farm", "Castle", "Fortifications", "Captain's Quarters", "Castle", "Castle",
    "Moat", "Marketplace", "Archery Range", "Thieves Guild", "Tavern", "Mage Guild",
    "Jousting Arena", "Cathedral", "Thatched Hut", "Blacksmith", "Armory", "Well", "Statue",
]
HIT_BLOCK = 8                      # хит-карта: 1 байт на блок 8x8 (640x256 -> 80x32 = 2560Б)

# Описания зданий (getBuildingDescription / getKnightBuildingDescription, castle_building_info.cpp).
# %{count} разрешены значениями GameStatic/profit: Well=2, Wel2(Farm)=8, Moat=-3, Castle=1000,
# Statue=250. Жилища (assert в исходнике → показывают монстра): "Recruit <Monster>" (Knight база:
# DW1..6 = Peasant/Archer/Pikeman/Swordsman/Cavalry/Paladin). СТРОГО параллельно KNIGHT_BUILDINGS.
KNIGHT_DESCS = [
    "The Farm increases production of Peasants by 8 per week.",                                 # WEL2
    "The Castle improves the town's defense and increases its income to 1000 gold per day.",    # CASTLE
    "The Fortifications increase the toughness of the walls, increasing the number of turns it takes to knock them down.",  # SPEC
    "The Captain's Quarters provides a captain to assist in the castle's defense when no hero is present.",  # CAPTAIN
    "The Left Turret provides extra firepower during castle combat.",                           # LEFTTURRET
    "The Right Turret provides extra firepower during castle combat.",                          # RIGHTTURRET
    "The Moat slows and weakens attacking units. Any walking unit entering the moat must end its turn there and can only move within the moat one hex at a time. Any creature present in the moat will have its defense skill reduced by 3.",  # MOAT
    "The Marketplace can be used to convert one type of resource into another. The more marketplaces you control, the better the exchange rate.",  # MARKETPLACE
    "Recruit Archer.",                                                                          # DW_1 = MONSTER2
    "The Thieves' Guild provides information on enemy players. Thieves' Guilds can also provide scouting information on enemy towns. Additional Guilds provide more information.",  # THIEVESGUILD
    "The Tavern increases morale for troops defending the castle.",                             # TAVERN
    "The Mage Guild allows heroes to learn spells and replenish their spell points.",           # MAGEGUILD1
    "Recruit Cavalry.",                                                                         # DW_4 = MONSTER5
    "Recruit Paladin.",                                                                         # DW_5 = MONSTER6
    "Recruit Peasant.",                                                                         # DW_0 = MONSTER1
    "Recruit Pikeman.",                                                                         # DW_2 = MONSTER3
    "Recruit Swordsman.",                                                                       # DW_3 = MONSTER4
    "The Well increases the growth rate of all dwellings by 2 creatures per week.",             # WELL
    "The Statue increases the town's income by 250 gold per day.",                              # STATUE
]
# Геометрия инфо-попапа (экран 1024×768, screen px). Рамка по центру.
INFO_BOX = (292, 288, 732, 472)    # x1,y1,x2,y2
INFO_TITLE_Y = 300                 # верх заголовка (имя)
INFO_LINE0_Y = 322                 # верх первой строки описания
INFO_LINE_H  = 12                  # межстрочный шаг (native SMALFONT)
INFO_WRAP_PX = 404                 # ширина обёртки текста (≈ внутренняя ширина рамки − поля)

# Диалог найма (Dialog::RecruitMonster). Окно = RECRBKG[0] (321×304, оригинал, с рамками/полем
# счётчика). 6 базовых Knight-монстров (monster_info.cpp: имя | прирост | цена золота).
# Заголовок = "Recruit %{name}" с мн.ч. (dialog_recruit.cpp:162 GetMultiName, monster_info.cpp plural).
RECRUIT_NAMES = ["Recruit Peasants", "Recruit Archers", "Recruit Pikemen",
                 "Recruit Swordsmen", "Recruit Cavalries", "Recruit Paladins"]
RECRUIT_COST  = [20, 150, 200, 250, 300, 600]     # золото за 1 (GetCost().gold)
RECRUIT_AVAIL = [12, 8, 5, 4, 3, 2]               # базовый прирост = доступно в свежем жилище
# Боевой спрайт монстра (GetMonsterSprite, monster_info.cpp:137), статик-кадр = 1 (battle_pack STATIC1).
RECRUIT_ICN   = ["PEASANT.ICN", "ARCHER.ICN", "PIKEMAN.ICN", "SWORDSMN.ICN", "CAVALRYR.ICN", "PALADIN.ICN"]
RECR_MON_FRAME = 1
RECR_MON_ANCHOR = (64, 130)        # window-local: центр X / низ Y спрайта монстра (левая зона)
# building idx (1-based, параллельно KNIGHT_BUILDINGS) → recruit idx (0..5); прочее = 255 (не жилище).
DWELLING_MAP = {9: 1, 13: 4, 14: 5, 15: 0, 16: 2, 17: 3}
RECR_W, RECR_H = 321, 304          # размер RECRBKG[0] (native)
# Поле счётчика на RECRBKG — (134,159) 68×19 (dialog_recruit.cpp:286). Центр = (168,164).
RECR_COUNT_XY = (168, 162)
RECR_NAME_Y   = 20                 # имя монстра (центр сверху)
RECR_AVAIL_Y  = 185               # "Available: N" (центр)
RECR_COST_Y   = 242               # "Cost: N gold" (центр, наша строка под полем)


def load_town(palette):
    agg, ent = read_agg_index_with_expansion(AGG_PATH)
    canvas = bytearray([BACKDROP]) * (TOWN_W * TOWN_H)
    placed = []
    # Базовый слой — панорама замка Рыцаря TOWNBKG0 (640×256, заполняет область целиком).
    bkg_icn = read_icn(agg_entry(agg, ent, "TOWNBKG0.ICN"))
    bhdr, benc = bkg_icn[0]
    bidx = decode_icn_indices(bhdr, benc)
    bw, bh = bhdr["w"], bhdr["h"]
    for y in range(min(bh, TOWN_H)):
        for x in range(min(bw, TOWN_W)):
            canvas[y * TOWN_W + x] = bidx[y * bw + x]
    placed.append(("TOWNBKG0.ICN(bg)", bw, bh, 0, 0))
    hit = bytearray(TOWN_W * TOWN_H)        # пер-пиксель индекс здания (1-based; 0=фон) для hover
    for bidx_i, (icn_name, frame) in enumerate(KNIGHT_BUILDINGS, start=1):
        icn = read_icn(agg_entry(agg, ent, icn_name))
        hdr, enc = icn[frame]
        idx = decode_icn_indices(hdr, enc)
        w, h = hdr["w"], hdr["h"]
        ox = hdr.get("ox", hdr.get("offset_x", 0))
        oy = hdr.get("oy", hdr.get("offset_y", 0))
        for y in range(h):
            yy = oy + y
            if not (0 <= yy < TOWN_H):
                continue
            row = yy * TOWN_W
            srow = y * w
            for x in range(w):
                v = idx[srow + x]
                if v == TRANSPARENT:
                    continue
                xx = ox + x
                if 0 <= xx < TOWN_W:
                    canvas[row + xx] = v
                    hit[row + xx] = bidx_i     # front-most здание (рисуется back→front)
        placed.append((icn_name, w, h, ox, oy))
    # Даунсэмпл хит-карты в блоки HIT_BLOCK×HIT_BLOCK: индекс = МОДА ненулевых в блоке (надёжнее центра).
    from collections import Counter
    bw_n, bh_n = TOWN_W // HIT_BLOCK, TOWN_H // HIT_BLOCK
    block_hit = bytearray(bw_n * bh_n)
    for by in range(bh_n):
        for bx in range(bw_n):
            cnt = Counter()
            for yy in range(by * HIT_BLOCK, by * HIT_BLOCK + HIT_BLOCK):
                base = yy * TOWN_W + bx * HIT_BLOCK
                for xx in range(HIT_BLOCK):
                    v = hit[base + xx]
                    if v:
                        cnt[v] += 1
            block_hit[by * bw_n + bx] = cnt.most_common(1)[0][0] if cnt else 0
    return bytes(canvas), placed, bytes(block_hit)


STRIP_H = 224          # нижняя панель замка: y[256..480) (STRIP[0] 205 + статус-бар 19)
STRIP_Y = 256

# Раскладка панели замка ВСЯ из исходника fheroes2 (castle_dialog.cpp / ui_castle.cpp /
# army_bar.cpp), координаты dialogRoi=(0,0), пересчитаны в strip-локальные (вычесть 256 по Y).
def _blit_icn(canvas, idx, w, h, ox, oy, dx, dy, cw, ch):
    for y in range(h):
        yy = dy + oy + y
        if 0 <= yy < ch:
            for x in range(w):
                v = idx[y * w + x]
                if v == TRANSPARENT:
                    continue
                xx = dx + ox + x
                if 0 <= xx < cw:
                    canvas[yy * cw + xx] = v

# Стартовые ресурсы королевства (game_state.asm Resources_InitStart) — для значений в панели.
START_FUNDS = {"wood": 20, "mercury": 5, "ore": 20, "sulfur": 5, "crystal": 5, "gems": 5, "gold": 7500}

# Гарнизон Knight (верхний ArmyBar = _army). Слот→(MONH-файл, счётчик). renderMonsterFrame
# (ui_monster.cpp:57) рисует monster.ICNMonh()[0]: Peasant=MONH0000, Archer=MONH0001 (большие).
GARRISON = [("MONH0000.ICN", "40"), ("MONH0001.ICN", "4")]

def load_strip(palette):
    agg, ent = read_agg_index_with_expansion(AGG_PATH)
    def icn(name, frame=0):
        h, e = read_icn(agg_entry(agg, ent, name))[frame]
        return decode_icn_indices(h, e), h["w"], h["h"], h.get("ox", 0), h.get("oy", 0)
    buf = bytearray([BACKDROP]) * (TOWN_W * STRIP_H)
    # SMALFONT: цифра '0'..'9' = кадр ord-32 = 16..25 (ui_castle: значения SMALL white).
    smalfont = read_icn(agg_entry(agg, ent, "SMALFONT.ICN"))
    def num_w(s):
        return sum(smalfont[ord(c) - 32][0]["w"] for c in s)
    def put_num(s, x, y):                              # x = левый край, y = верх (по oy глифа)
        for c in s:
            gh, ge = smalfont[ord(c) - 32]
            gi = decode_icn_indices(gh, ge)
            _blit_icn(buf, gi, gh["w"], gh["h"], gh.get("ox", 0), gh.get("oy", 0), x, y, TOWN_W, STRIP_H)
            x += gh["w"]

    # 1) STRIP[0] — деревянная подложка панели (640×205) @ strip-y 0.
    s0, w, h, _, _ = icn("STRIP.ICN", 0)
    _blit_icn(buf, s0, w, h, 0, 0, 0, 0, TOWN_W, STRIP_H)
    # 2) Нижняя строка @ (·,461)->strip-y 205: кнопка prev-замка SMALLBAR[1] (21×19) @x0,
    #    бар SMALLBAR[0] (598×19) @x21, кнопка next-замка SMALLBAR[3] (21×19) @x619.
    #    (castle_dialog.cpp:330,337,345 — стрелки переключения замков по краям.)
    sb1, w, h, _, _ = icn("SMALLBAR.ICN", 1)
    _blit_icn(buf, sb1, w, h, 0, 0, 0, 205, TOWN_W, STRIP_H)
    sb0, w, h, _, _ = icn("SMALLBAR.ICN", 0)
    _blit_icn(buf, sb0, w, h, 0, 0, 21, 205, TOWN_W, STRIP_H)
    sb3, w, h, _, _ = icn("SMALLBAR.ICN", 3)
    _blit_icn(buf, sb3, w, h, 0, 0, 619, 205, TOWN_W, STRIP_H)
    # 3) Герб CREST[BLUE=0] (101×93) @ (5,262)->strip (5,6).  (castle_dialog.cpp:144,350)
    cr, w, h, ox, oy = icn("CREST.ICN", 0)
    _blit_icn(buf, cr, w, h, ox, oy, 5, 6, TOWN_W, STRIP_H)
    # 4) Нижний ряд БЕЗ героя (RedrawIcons castle_dialog.cpp:151-154): STRIP[3] корона/знак
    #    @ rectSign2 (5,361)->strip(5,105) + STRIP[11] фон ряда армии героя (434×100) @ (112,105).
    s3, w, h, ox, oy = icn("STRIP.ICN", 3)
    _blit_icn(buf, s3, w, h, ox, oy, 5, 105, TOWN_W, STRIP_H)
    s11, w, h, ox, oy = icn("STRIP.ICN", 11)
    _blit_icn(buf, s11, w, h, ox, oy, 112, 105, TOWN_W, STRIP_H)
    # 5) ГАРНИЗОН (верхний ArmyBar=_army) @ (112,262)->y6. ArmyBar non-mini (army_bar.cpp):
    #    пустая ячейка = STRIP[2] (82×93, шаг 88); ЗАПОЛНЕННАЯ = renderMonsterFrame:
    #    плита расы Knight STRIP[4] + БОЛЬШОЙ спрайт MONH[0] (@ ox/oy ICN) + счётчик. НЕ MONS32!
    s2, sw, sh, _, _ = icn("STRIP.ICN", 2)
    s4, p4w, p4h, _, _ = icn("STRIP.ICN", 4)
    for i in range(5):
        _blit_icn(buf, s2, sw, sh, 0, 0, 112 + i * 88, 6, TOWN_W, STRIP_H)
    for slot, (monh, cnt) in enumerate(GARRISON):
        cellx = 112 + slot * 88
        _blit_icn(buf, s4, p4w, p4h, 0, 0, cellx, 6, TOWN_W, STRIP_H)       # плита расы под монстром
        m, mw, mh, mox, moy = icn(monh, 0)
        _blit_icn(buf, m, mw, mh, mox, moy, cellx, 6, TOWN_W, STRIP_H)      # MONH[0] @ cell + ox/oy
        put_num(cnt, cellx + 82 - num_w(cnt) - 3, 6 + 93 - 13)             # счётчик низ-право
    # 7) Ресурс-панель @ ROI(552,262)->strip(552,6). ui_castle.cpp:242. RESOURCE[0..6], 2 колонки.
    res = [icn("RESOURCE.ICN", k) for k in range(7)]   # wood,mercury,ore,sulfur,crystal,gems,gold
    rx = 552; maxW = 39; maxH = 32; fh = 9
    leftX = rx + 1; rightX = rx + 1 + maxW + 2
    offY = [0, maxH + fh + 2, (maxH + fh) * 2 - 1, (maxH + fh) * 3 + 1]
    def put_res(k, colx, oy_idx):
        m, w, h, mox, moy = res[k]
        _blit_icn(buf, m, w, h, mox, moy, colx + (maxW - w) // 2, 6 + offY[oy_idx] + maxH - h, TOWN_W, STRIP_H)
    put_res(0, leftX, 0); put_res(3, rightX, 0)        # wood | sulfur
    put_res(4, leftX, 1); put_res(1, rightX, 1)        # crystal | mercury
    put_res(2, leftX, 2); put_res(5, rightX, 2)        # ore | gems
    g, gw, gh, gox, goy = res[6]
    _blit_icn(buf, g, gw, gh, gox, goy, rx + (82 - gw) // 2, 6 + offY[3], TOWN_W, STRIP_H)   # gold центр
    # Значения ресурсов (SMALL white) под иконками — позиции из ui_castle.cpp:277-296.
    def val(name, colx, oy_idx):
        s = str(START_FUNDS[name])
        put_num(s, colx + (maxW - num_w(s)) // 2, 6 + offY[oy_idx] + maxH + 1)
    val("wood", leftX, 0); val("sulfur", rightX, 0)
    val("crystal", leftX, 1); val("mercury", rightX, 1)
    val("ore", leftX, 2); val("gems", rightX, 2)
    gs = str(START_FUNDS["gold"])
    put_num(gs, rx + (82 - num_w(gs)) // 2, 6 + offY[3] + gh + 1)
    # 8) Кнопка EXIT (castle_dialog.cpp:379 BUTTON_EXIT_TOWN → useOriginalResources()=TREASURY[1],
    #    agg_image.cpp:910). 80×25 @ dialog(553,428)->strip(553,172).
    ex, w, h, ox, oy = icn("TREASURY.ICN", 1)
    _blit_icn(buf, ex, w, h, ox, oy, 553, 172, TOWN_W, STRIP_H)
    return bytes(buf)

def render_name_mask(agg, ent, name):
    """Имя здания → маска (idx 15=глиф / 0=прозрачно) шрифтом SMALFONT, НАТИВНО (≤108px<128 для
    резидентного Render_DrawSpriteEntry). Палитра белая-альфа (idx0 прозрачен). (mask, W, H)."""
    sf = read_icn(agg_entry(agg, ent, "SMALFONT.ICN"))
    glyphs, tw, maxbot = [], 0, 0
    for c in name:
        if c == " ":
            glyphs.append((None, 4, 0, 0)); tw += 4; continue
        h, e = sf[ord(c) - 32]
        gi = decode_icn_indices(h, e); oy = h.get("oy", 0)
        glyphs.append((gi, h["w"], h["h"], oy)); tw += h["w"]; maxbot = max(maxbot, oy + h["h"])
    W0, H0 = max(1, tw), max(1, maxbot)
    base = bytearray(W0 * H0)
    x = 0
    for gi, gw, gh, oy in glyphs:
        if gi is not None:
            for yy in range(gh):
                py = oy + yy
                if 0 <= py < H0:
                    for xx in range(gw):
                        if gi[yy * gw + xx] != TRANSPARENT:
                            base[py * W0 + x + xx] = 15
        x += gw
    return bytes(base), W0, H0


def bake_font(agg, ent, pad=2):
    """Атлас глифов SMALFONT для Render_DrawString: ASCII 32..127 → (маска 1Б/px idx15, w, h+pad).
    Тот же формат, что render_name_mask (проверен на железе). Низ паддится pad прозрачных строк —
    реальный FT812 режет ~2px низа мелкого глифа (см. память ft812-small-glyph-bottom-padding)."""
    sf = read_icn(agg_entry(agg, ent, "SMALFONT.ICN"))
    out = []
    for c in range(32, 128):
        idx = c - 32
        try:
            ch = " " if (c == 32 or idx >= len(sf)) else chr(c)
            m, w, h = render_name_mask(agg, ent, ch)
        except Exception:
            m, w, h = render_name_mask(agg, ent, " ")
        out.append((m + bytes(w * pad), w, h + pad))   # +pad прозрачных строк снизу
    return out


def wrap_desc(text, glyph_w):
    """Жадная обёртка по словам до INFO_WRAP_PX (ширины глифов из атласа)."""
    def line_px(s):
        return sum(glyph_w.get(ch, 4) for ch in s)
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word) if cur else word
        if line_px(trial) <= INFO_WRAP_PX:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def bake_recruit_window(agg, ent):
    """Окно найма = RECRBKG[0] (321×304, оригинал HMM2: рамки + 'Cost per troop:' + поле счётчика
    уже baked). Индексы в палитру KB (как town). TRANSPARENT→0 (окно непрозрачно)."""
    h, e = read_icn(agg_entry(agg, ent, "RECRBKG.ICN"))[0]
    gi = decode_icn_indices(h, e)
    buf = bytearray(RECR_W * RECR_H)
    _blit_icn(buf, gi, h["w"], h["h"], h.get("ox", 0), h.get("oy", 0), 0, 0, RECR_W, RECR_H)
    return bytes(buf)


def _prescale16(gi, w, h):
    """Nearest ×1.6 (×16/10) апскейл индексного буфера (1Б/px) → (bytes, nw, nh)."""
    nw, nh = w * 16 // 10, h * 16 // 10
    out = bytearray(nw * nh)
    for oy in range(nh):
        srow = (oy * 10 // 16) * w
        orow = oy * nw
        for ox in range(nw):
            out[orow + ox] = gi[srow + ox * 10 // 16]
    return bytes(out), nw, nh


def bake_recruit_monsters(agg, ent):
    """6 боевых спрайтов Knight (статик-кадр), пред-масштаб ×1.6, индексы KB.PAL (idx0=прозрачно).
    → [(sprite, W, H)]; W<128 (лимит Render_DrawSpriteEntry: stride=W*2 в байте)."""
    out = []
    for icn in RECRUIT_ICN:
        h, e = read_icn(agg_entry(agg, ent, icn))[RECR_MON_FRAME]
        gi = decode_icn_indices(h, e)              # idx0=прозрачно, 1..255=KB.PAL
        spr, nw, nh = _prescale16(gi, h["w"], h["h"])
        assert nw < 128, f"{icn} ×1.6 width {nw} >= 128"
        out.append((spr, nw, nh))
    return out


def build_payload(palette, town_img, strip_img, names_masks, font_masks, recruit_win, monster_sprites):
    payload = bytearray()

    def put(raw: bytes) -> int:
        addr = TOWN_RAMG_BASE + align(len(payload), 4)
        while TOWN_RAMG_BASE + len(payload) < addr:
            payload.append(0)
        payload.extend(raw)
        return addr

    pal_addr = put(palette_argb4444_opaque(palette))   # экран замка непрозрачен → opaque-палитра
    img_addr = put(town_img)
    strip_addr = put(strip_img)
    # Палитра имён зданий: idx i = БЕЛЫЙ с альфой i (ARGB4444 0xiFFF); idx0 прозрачен (текст поверх панели).
    name_pal = bytearray(2 * 256)
    for i in range(16):
        v = ((i << 12) | 0x0FFF) if i else 0
        name_pal[i * 2] = v & 0xFF; name_pal[i * 2 + 1] = (v >> 8) & 0xFF
    name_pal_addr = put(bytes(name_pal))
    name_addrs = [(put(m), w, h) for (m, w, h) in names_masks]   # [имя]=(addr,w,h)
    font_addrs = [(put(m), w, h) for (m, w, h) in font_masks]    # [char-32]=(addr,w,h)
    recruit_addr = put(recruit_win)                              # окно найма RECRBKG (один на все жилища)
    spr_pal_addr = put(palette_argb4444(palette))                # палитра спрайтов: idx0 ПРОЗРАЧЕН
    mon_addrs = [(put(s), w, h) for (s, w, h) in monster_sprites]  # [recruit idx]=(addr,w,h)
    return (payload, pal_addr, img_addr, strip_addr, name_pal_addr, name_addrs, font_addrs,
            recruit_addr, spr_pal_addr, mon_addrs)


def emit_inc(pal_addr, img_addr, strip_addr, name_pal_addr, name_addrs, font_addrs, block_hit, pak,
             wrapped_descs, recruit_addr, spr_pal_addr, mon_addrs):
    L = []
    L.append("; Сгенерировано Source/Tools/town_pack.py — экран города (Knight, потоковый HMM2TOWN.PAK).")
    L.append("                ifndef _HMM2_GENERATED_TOWN_")
    L.append("                define _HMM2_GENERATED_TOWN_")
    L.append("")
    L.append(f"TOWN_PAL_RAMG        EQU #{pal_addr:06X}")
    L.append(f"TOWN_IMG_RAMG        EQU #{img_addr:06X}")
    L.append(f"TOWN_IMG_W           EQU {TOWN_W}")
    L.append(f"TOWN_IMG_H           EQU {TOWN_H}")
    L.append("")
    # Рендер города: пролог состояния FT812 + opaque-палитра + одно изображение ×1.6 (8/5).
    L.append("Town_DL:")
    L.append("                FT_CLEAR_COLOR_RGB 0, 0, 0")
    L.append("                FT_CLEAR 1, 1, 1")
    L.append("                FT_SCISSOR_XY 0, 0")
    L.append("                FT_SCISSOR_SIZE 1024, 768")
    L.append("                FT_COLOR_RGB 255, 255, 255")
    L.append("                FT_COLOR_A 255")
    L.append("                FT_BITMAP_HANDLE 0")
    L.append("                FT_CELL 0")
    L.append("                FT_BITMAP_TRANSFORM_A 160")
    L.append("                FT_BITMAP_TRANSFORM_B 0")    # сброс skew B/D/F (FT812 протекают между сценами)
    L.append("                FT_BITMAP_TRANSFORM_C 0")
    L.append("                FT_BITMAP_TRANSFORM_D 0")
    L.append("                FT_BITMAP_TRANSFORM_E 160")
    L.append("                FT_BITMAP_TRANSFORM_F 0")
    L.append("                FT_VERTEX_TRANSLATE_X 0")
    L.append("                FT_VERTEX_TRANSLATE_Y 0")
    L.append("                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA")
    L.append("                FT_BITMAP_LAYOUT_H 0, 0")
    L.append("                FT_BITMAP_SIZE_H 0, 0")
    L.append("                FT_PALETTE_SOURCE TOWN_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append(f"                FT_BITMAP_SOURCE TOWN_IMG_RAMG")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {TOWN_W}, {TOWN_H}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {TOWN_W * 16 // 10}, {TOWN_H * 16 // 10}")
    L.append(f"                FT_VERTEX2F 0, 0")
    # Нижняя панель замка STRIP[0] (640×205) вторым битмапом @ логич.(0,256).
    L.append(f"                FT_BITMAP_SOURCE #{strip_addr:06X}")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {TOWN_W}, {STRIP_H}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {TOWN_W * 16 // 10}, {STRIP_H * 16 // 10}")
    L.append(f"                FT_VERTEX2F 0, {STRIP_Y * 256 // 10}")
    L.append("                FT_END")
    L.append("Town_DL_SIZE EQU $ - Town_DL")
    L.append("")
    L.append(f"TOWN_RAMG_BASE       EQU #{TOWN_RAMG_BASE:06X}")
    L.append(f"TOWN_PAYLOAD_BYTES   EQU {pak['payload_bytes']}")
    L.append(f"TOWN_PAYLOAD_SECTORS EQU {pak['payload_sectors']}")
    L.append(f"TOWN_BODY_SECTOR     EQU {pak['body_start_sector']}")
    L.append('TownPakName:         DEFB "HMM2TOWN.PAK", 0')
    L.append("")
    # --- Hover-имена зданий (faithful castle_dialog.cpp: наведение/клик → имя здания) ---
    bw_n, bh_n = TOWN_W // HIT_BLOCK, TOWN_H // HIT_BLOCK
    L.append(f"TOWN_HIT_BLK         EQU {HIT_BLOCK}")
    L.append(f"TOWN_HIT_W           EQU {bw_n}")
    L.append(f"TOWN_HIT_H           EQU {bh_n}")
    L.append(f"TOWN_NAME_PAL_RAMG   EQU #{name_pal_addr:06X}")
    L.append(f"TOWN_NAME_COUNT      EQU {len(name_addrs)}")
    L.append("TownHitMap:                            ; блок 8x8 → индекс здания (1-based; 0=фон), Z80-читаемая")
    for r in range(bh_n):
        row = block_hit[r * bw_n:(r + 1) * bw_n]
        L.append("                DEFB " + ", ".join(str(b) for b in row))
    L.append("TownBuildingNameTab:                   ; [idx-1] → имя SMALFONT ×1.6 [lo,mid,hi,w,h]")
    for (addr, w, h) in name_addrs:
        L.append(f"                DEFB #{addr & 0xFF:02X}, #{(addr >> 8) & 0xFF:02X}, "
                 f"#{(addr >> 16) & 0xFF:02X}, {w}, {h}")
    L.append("Town_Name_Begin_DL:                    ; пролог имени: нативно (имя ×1.6-пред-масштаб), белая-альфа")
    L.append("                FT_BITMAP_TRANSFORM_A 256")
    L.append("                FT_BITMAP_TRANSFORM_B 0")
    L.append("                FT_BITMAP_TRANSFORM_D 0")
    L.append("                FT_BITMAP_TRANSFORM_E 256")
    L.append("                FT_BITMAP_TRANSFORM_F 0")
    L.append("                FT_BITMAP_LAYOUT_H 0, 0")    # сброс высоких бит (после окна найма SIZE_H≠0)
    L.append("                FT_BITMAP_SIZE_H 0, 0")      # иначе мелкие глифы получат +512 к ширине
    L.append("                FT_PALETTE_SOURCE TOWN_NAME_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("Town_Name_Begin_DL_SIZE EQU $ - Town_Name_Begin_DL")
    L.append("Town_Name_End_DL:")
    L.append("                FT_END")
    L.append("Town_Name_End_DL_SIZE EQU $ - Town_Name_End_DL")
    L.append("")
    # --- Динамический рендер текста: атлас глифов SMALFONT + строки имён/описаний ---
    L.append("FontGlyphTab:                          ; [char-32] → глиф SMALFONT [lo,mid,hi,w,h] (Render_DrawString)")
    for (addr, w, h) in font_addrs:
        L.append(f"                DEFB #{addr & 0xFF:02X}, #{(addr >> 8) & 0xFF:02X}, "
                 f"#{(addr >> 16) & 0xFF:02X}, {w}, {h}")
    # Заголовок попапа = имя здания (строкой). Описание = блок обёрнутых строк, пустая = конец.
    L.append("TownNameStrTab:                        ; [idx-1] → &имя (null-term, для заголовка попапа)")
    for i in range(len(KNIGHT_NAMES)):
        L.append(f"                DW TownNameStr_{i}")
    for i, nm in enumerate(KNIGHT_NAMES):
        L.append(f'TownNameStr_{i}: DEFB "{nm}", 0')
    L.append("TownDescTab:                           ; [idx-1] → &блок строк описания (null-term; пустая строка = конец)")
    for i in range(len(wrapped_descs)):
        L.append(f"                DW TownDescBlk_{i}")
    for i, lines in enumerate(wrapped_descs):
        L.append(f"TownDescBlk_{i}:")
        for ln in lines:
            L.append(f'                DEFB "{ln}", 0')
        L.append("                DEFB 0")            # пустая строка = терминатор блока
    # Рамка инфо-попапа (RECTS): внешний прямоугольник (рамка) + внутренний (заливка).
    bx1, by1, bx2, by2 = INFO_BOX
    L.append("Town_Info_Box_DL:                      ; рамка попапа (faithful Dialog::Message окно)")
    L.append("                FT_COLOR_RGB 176, 140, 92")
    L.append("                FT_COLOR_A 255")
    L.append("                FT_LINE_WIDTH 16")
    L.append("                FT_BEGIN FT_RECTS")
    L.append(f"                FT_VERTEX2F {bx1 * 16}, {by1 * 16}")
    L.append(f"                FT_VERTEX2F {bx2 * 16}, {by2 * 16}")
    L.append("                FT_COLOR_RGB 28, 20, 10")
    L.append("                FT_COLOR_A 244")
    L.append(f"                FT_VERTEX2F {(bx1 + 3) * 16}, {(by1 + 3) * 16}")
    L.append(f"                FT_VERTEX2F {(bx2 - 3) * 16}, {(by2 - 3) * 16}")
    L.append("                FT_END")
    L.append("                FT_COLOR_A 255")
    L.append("                FT_COLOR_RGB 255, 255, 255")
    L.append("Town_Info_Box_DL_SIZE EQU $ - Town_Info_Box_DL")
    L.append(f"TOWN_INFO_TITLE_Y    EQU {INFO_TITLE_Y} * 16")
    L.append(f"TOWN_INFO_LINE0_Y    EQU {INFO_LINE0_Y} * 16")
    L.append(f"TOWN_INFO_LINE_H     EQU {INFO_LINE_H} * 16")
    L.append("")
    # --- Диалог найма (Dialog::RecruitMonster): окно RECRBKG + статичные строки на монстра ---
    rsx = (1024 - round(RECR_W * 1.6)) // 2          # экран X окна (центр по горизонтали)
    rsy = (768 - round(RECR_H * 1.6)) // 2           # экран Y окна
    L.append(f"RECRUIT_WIN_RAMG     EQU #{recruit_addr:06X}")
    L.append("Recruit_Win_DL:                        ; окно найма RECRBKG ×1.6 по центру экрана")
    L.append("                FT_BITMAP_TRANSFORM_A 160")
    L.append("                FT_BITMAP_TRANSFORM_B 0")
    L.append("                FT_BITMAP_TRANSFORM_C 0")
    L.append("                FT_BITMAP_TRANSFORM_D 0")
    L.append("                FT_BITMAP_TRANSFORM_E 160")
    L.append("                FT_BITMAP_TRANSFORM_F 0")
    L.append("                FT_PALETTE_SOURCE TOWN_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("                FT_BITMAP_SOURCE RECRUIT_WIN_RAMG")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {RECR_W}, {RECR_H}")
    # FT_BITMAP_SIZE маскирует ширину &511 → для >511 нужны высокие биты через SIZE_H (иначе клип в width&511)
    L.append(f"                FT_BITMAP_SIZE_H {RECR_W * 16 // 10}, {RECR_H * 16 // 10}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {RECR_W * 16 // 10}, {RECR_H * 16 // 10}")
    L.append(f"                FT_VERTEX2F {rsx * 16}, {rsy * 16}")
    L.append("                FT_END")
    L.append("Recruit_Win_DL_SIZE EQU $ - Recruit_Win_DL")
    L.append(f"RECR_NAME_VY         EQU {(rsy + round(RECR_NAME_Y * 1.6)) * 16}")
    L.append(f"RECR_AVAIL_VY        EQU {(rsy + round(RECR_AVAIL_Y * 1.6)) * 16}")
    L.append(f"RECR_COST_VY         EQU {(rsy + round(RECR_COST_Y * 1.6)) * 16}")
    L.append(f"RECR_COUNT_VY        EQU {(rsy + round(RECR_COUNT_XY[1] * 1.6)) * 16}")
    # building idx (1-based) → recruit idx (0..5) или 255 (не жилище)
    dmap = [DWELLING_MAP.get(i, 255) for i in range(1, len(KNIGHT_BUILDINGS) + 1)]
    L.append("TownDwellingMap:                       ; [idx-1] → recruit idx (0..5); 255 = не жилище")
    L.append("                DEFB " + ", ".join(str(b) for b in dmap))
    # Статичные строки на монстра (фаза 1: счётчик = доступно, без live +/-)
    def strtab(label, fn):
        L.append(f"{label}:")
        for i in range(len(RECRUIT_NAMES)):
            L.append(f"                DW {label}_{i}")
        for i in range(len(RECRUIT_NAMES)):
            L.append(f'{label}_{i}: DEFB "{fn(i)}", 0')
    strtab("RecruitNameTab", lambda i: RECRUIT_NAMES[i])
    strtab("RecruitAvailTab", lambda i: f"Available: {RECRUIT_AVAIL[i]}")
    strtab("RecruitCostTab", lambda i: f"Cost: {RECRUIT_COST[i]} gold")
    strtab("RecruitCountTab", lambda i: str(RECRUIT_AVAIL[i]))
    # --- спрайт монстра (боевой статик-кадр ×1.6) в окне найма ---
    L.append(f"RECRUIT_SPR_PAL_RAMG EQU #{spr_pal_addr:06X}")
    L.append("Recruit_Mon_Begin_DL:                  ; пролог спрайта монстра: native (×1.6 пред-масштаб), палитра прозрачная idx0")
    L.append("                FT_BITMAP_TRANSFORM_A 256")
    L.append("                FT_BITMAP_TRANSFORM_B 0")
    L.append("                FT_BITMAP_TRANSFORM_D 0")
    L.append("                FT_BITMAP_TRANSFORM_E 256")
    L.append("                FT_BITMAP_TRANSFORM_F 0")
    L.append("                FT_BITMAP_LAYOUT_H 0, 0")
    L.append("                FT_BITMAP_SIZE_H 0, 0")
    L.append("                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("Recruit_Mon_Begin_DL_SIZE EQU $ - Recruit_Mon_Begin_DL")
    L.append("RecruitMonSprTab:                      ; [recruit idx] → спрайт монстра [lo,mid,hi,w,h]")
    for (addr, w, h) in mon_addrs:
        L.append(f"                DEFB #{addr & 0xFF:02X}, #{(addr >> 8) & 0xFF:02X}, "
                 f"#{(addr >> 16) & 0xFF:02X}, {w}, {h}")
    ax = rsx + round(RECR_MON_ANCHOR[0] * 1.6)     # экран X центра монстра
    ayb = rsy + round(RECR_MON_ANCHOR[1] * 1.6)    # экран Y низа монстра
    L.append("RecruitMonPosTab:                      ; [recruit idx] → позиция спрайта (vertex) [Xlo,Xhi,Ylo,Yhi]")
    for (addr, w, h) in mon_addrs:
        px = (ax - w // 2) * 16
        py = (ayb - h) * 16
        L.append(f"                DEFB #{px & 0xFF:02X}, #{(px >> 8) & 0xFF:02X}, "
                 f"#{py & 0xFF:02X}, #{(py >> 8) & 0xFF:02X}")
    L.append("")
    L.append("                endif")
    TOWN_INC.write_text("\n".join(L), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="HMM2TOWN.PAK — экран города Knight (стрим-PAK).")
    ap.add_argument("--preview", type=Path, default=None, help="PNG-реконструкция города для сверки")
    args = ap.parse_args()

    agg, ent = read_agg_index_with_expansion(AGG_PATH)
    palette = read_palette(agg_entry(agg, ent, "KB.PAL"))
    town_img, placed, block_hit = load_town(palette)
    names_masks = [render_name_mask(agg, ent, nm) for nm in KNIGHT_NAMES]  # hover-имена зданий
    font_masks = bake_font(agg, ent)                                       # атлас глифов для текста
    glyph_w = {chr(32 + i): font_masks[i][1] for i in range(len(font_masks))}
    wrapped_descs = [wrap_desc(d, glyph_w) for d in KNIGHT_DESCS]          # описания → строки

    if args.preview:
        from PIL import Image
        strip_img = load_strip(palette)
        im = Image.new("RGB", (TOWN_W, 480))
        px = im.load()
        for y in range(TOWN_H):                       # верх: город 640×256
            for x in range(TOWN_W):
                px[x, y] = palette[town_img[y * TOWN_W + x]]
        for y in range(STRIP_H):                       # низ: панель 640×224 @ y=256
            for x in range(TOWN_W):
                px[x, 256 + y] = palette[strip_img[y * TOWN_W + x]]
        im.save(args.preview)
        print(f"preview: {args.preview}  ({len(placed)} buildings + panel)")
        return 0

    strip_img = load_strip(palette)
    recruit_win = bake_recruit_window(agg, ent)
    monster_sprites = bake_recruit_monsters(agg, ent)
    (payload, pal_addr, img_addr, strip_addr, name_pal_addr, name_addrs, font_addrs,
     recruit_addr, spr_pal_addr, mon_addrs) = build_payload(
        palette, town_img, strip_img, names_masks, font_masks, recruit_win, monster_sprites)
    summary = build_pak(
        [{"type": TYPE_RAMG_BLOB, "target": TOWN_RAMG_BASE, "data": bytes(payload)}],
        TOWN_PAK_PATH,
    )
    pak = {
        "payload_bytes": len(payload),
        "payload_sectors": (len(payload) + SECTOR - 1) // SECTOR,
        "body_start_sector": summary["body_start_sector"],
    }
    emit_inc(pal_addr, img_addr, strip_addr, name_pal_addr, name_addrs, font_addrs, block_hit, pak,
             wrapped_descs, recruit_addr, spr_pal_addr, mon_addrs)
    print(f"town pack -> {TOWN_PAK_PATH.name}: {len(placed)} построек, "
          f"payload={len(payload)} байт ({pak['payload_sectors']} сект), PAK={summary['total_bytes']} байт")
    print(f"  inc: {TOWN_INC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
