#!/usr/bin/env python3
"""HMM2BATL.PAK — потоковый PAK экрана БОЯ (battle). Категория стрим-архитектуры
(spg-загрузчик + PAK по категориям: карты/города/бои/музыка/SFX). Стримится с SD в
Battle_Enter (НЕ SPG), как HMM2TOWN/MENU.PAK.

Поле боя по оригиналу fheroes2 (battle_interface.cpp / battle_cell.cpp / monster_info.cpp):
- фон по грунту CBKG* (640×443; здесь Grass = CBKGGRMT) базовым слоем @ (0,0);
- гекс-сетка board 11×9: cell 44×52, origin area+(89,62), шаг ряда 42, нечёт.ряд −22;
- боевой спрайт монстра = monsterIcnIds[id] (Peasant=PEASANT.ICN, Archer=ARCHER.ICN, …),
  кадр СТОЙКИ = [1] (кадр 0 — пустышка 1×1); защитник зеркалится (смотрит влево);
- армия атакующего в левой колонке (cells 11/22/33), защитника — в правой (21/32/43).

Композлю 640×480 (поле 443 + панель 37), режу на 2 битмапа (640×256 + 640×224) — оба ×1.6 ≤511.
Эмитит Source/ASM/generated_battle.inc: BATTLE_PAL_RAMG, Battle_DL (×1.6), метаданные PAK.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from agg_tools import read_agg_index_with_expansion
from object_atlas import agg_entry, read_icn, read_palette
from pak_builder import build_pak, TYPE_RAMG_BLOB, SECTOR
from viewport_pack import align, decode_icn_indices, palette_argb4444_opaque

ROOT = Path(__file__).resolve().parents[2]
AGG_PATH = ROOT / "Assets" / "Original" / "DATA" / "HEROES2.AGG"
BATTLE_INC = ROOT / "Source" / "ASM" / "generated_battle.inc"
BATTLE_PAK_PATH = ROOT / "Build" / "HMM2BATL.PAK"

BATTLE_RAMG_BASE = 0x000000         # сцена эксклюзивна (menu|adventure|town|battle) → общий base 0
BATTLE_W, BATTLE_H = 640, 480
# Разрез 640×480 на два битмапа (>511 при ×1.6). y=240: 240×1.6=384 ЦЕЛОЕ → 384+384=768
# ровно, без округления → НЕТ шва (на y=256: 256×1.6=409.6 дробное → 0.6px щель = чёрная линия).
BATTLE_SPLIT = 240
TRANSPARENT = 0
BACKDROP = 0

BG_NAME = "CBKGGRMT.ICN"            # Grass+Mountains (грунт по умолчанию)

# Гекс-сетка (battle_cell.cpp:258-259; battle_cell.h widthPx=44 heightPx=52, cellHeightVerSide=32).
WIDTH_IN_CELLS = 11
CELL_W, CELL_H = 44, 52
CELL_OX, CELL_OY = 89, 62
ROW_STEP = CELL_H - (CELL_H - 32) // 2   # 52 - 10 = 42

def cell_pos(idx):
    row, col = idx // WIDTH_IN_CELLS, idx % WIDTH_IN_CELLS
    x = CELL_OX - (CELL_W // 2 if row % 2 else 0) + CELL_W * col
    y = CELL_OY + ROW_STEP * row
    return x, y                       # верх-лево ячейки (44×52)


# Гекс-тень наведённой клетки — РЕПЛИКА fheroes2 DrawHexagonShadow (battle_interface.cpp:478):
# полупрозрачная ТЁМНАЯ шестиугольная тень (не яркий прямоугольник!). Маска: index1=тень, 0=прозр.
# Объединение симметрично сужающихся (по 2px с боков) и растущих (по 2px ввысь) прямоугольников
# вокруг центра ячейки → шестиугольник. horizSpace=1 (как курсорная тень _hexagonCursorShadow).
SHADOW_ALPHA = 4                       # ЗОНА ХОДА = fheroes2 DrawHexagonShadow(4) = СВЕТЛАЯ тень
                                       # (image.cpp:841 тени-таблицы 2..5, 2=тёмная/5=светлая; 4=светлая).
                                       # Было 9 (≈60% черноты) — выдуманные тёмные блоки, НЕ по оригиналу.

def make_hex_shadow_mask(horiz_space=1):
    l = 13
    w, h = CELL_W, CELL_H
    mask = bytearray(w * h)            # 0=прозрачно, 1=тень
    rx, ry, rw, rh = horiz_space, l - 1, w + 1 - horiz_space * 2, 2 * l + 4
    i = 0
    while i < w // 2:
        for x in range(rw):
            for y in range(rh):
                px, py = rx + x, ry + y
                if 0 <= px < w and 0 <= py < h:
                    mask[py * w + px] = 1
        ry -= 1
        rh += 2
        rx += 1 if i == 0 else 2
        rw -= 2 if i == 0 else 4
        i += 2
    return bytes(mask)

# Боевые юниты — ДИНАМИЧЕСКИЕ: спрайты-стойки в RAM_G (отдельно от фона), Render_Battle
# рисует их по таблице состояния → можно двигать. Типы (боевой ICN, кадр СТОЙКИ=[1]):
UNIT_TYPES = [("PEASANT.ICN", 1), ("ARCHER.ICN", 1)]   # 0=Peasant, 1=Archer
# Анимация по BIN PEAS_FRM/ARCHRFRM. ЕДИНАЯ раскладка 12 кадров/вариант (фикс. смещения групп):
#   idle@0 (4 кадра, дыхание), walk@4 (8 кадров MOVE_MAIN 5-12). Все паддятся до ОБЩЕГО канваса
#   (union bbox idle+walk → тело монстра на месте при любом кадре). Атака — следующим шагом.
# Кадры по BIN (КОРРЕКТНЫЕ индексы enum с TEMPORARY=6/DOUBLEHEX-дырами):
#   Peasant: STATIC1 IDLE2/3, MOVE_MAIN5-12, ATTACK2(мили)=16,18,24,26, DEATH=13,15,35,37.
#   Archer:  STATIC1 IDLE2-4,  MOVE_MAIN5-12, SHOOT2(стрельба)=16,18,20,22, DEATH=45,47,49,50.
# 16 кадров/вариант (по 4 на группу) — компромисс RAM_G (1МБ, аппаратный предел): ходьба прорежена 8→4.
UNIT_IDLE_FRAMES = [[1, 2, 3, 2], [1, 2, 3, 4]]
UNIT_WALK_FRAMES = [[5, 7, 9, 11], [5, 7, 9, 11]]
UNIT_ATTACK_FRAMES = [[16, 18, 24, 26], [16, 18, 20, 22]]
UNIT_DEATH_FRAMES = [[13, 15, 35, 37], [45, 47, 49, 50]]
UNIT_ANIM_FRAMES = [UNIT_IDLE_FRAMES[t] + UNIT_WALK_FRAMES[t] + UNIT_ATTACK_FRAMES[t] + UNIT_DEATH_FRAMES[t] for t in range(2)]  # 16/тип
UNIT_FRAME_COUNT = 16
UNIT_IDLE_BASE, UNIT_IDLE_N = 0, 4
UNIT_WALK_BASE, UNIT_WALK_N = 4, 4
UNIT_ATK_BASE, UNIT_ATK_N = 8, 4
UNIT_DEATH_BASE, UNIT_DEATH_N = 12, 4
# Состояние юнитов: (тип, cell, side, count). Раскладка fheroes2 battle_army.cpp:85 GROUPED:
# атак. Peasant×40@22/Archer×4@33 (вправо, side0), защ. Peasant×20@32/Archer×2@43 (зеркало side1).
UNIT_STATE = [(0, 22, 0, 40), (1, 33, 0, 4), (0, 32, 1, 20), (1, 43, 1, 2)]

STAND_FRAME = 1                       # кадр стойки (STATIC); [0] пустышка 1×1


def _blit(canvas, idx, w, h, dx, dy, reflect=False, cw=BATTLE_W, ch=BATTLE_H):
    for y in range(h):
        yy = dy + y
        if not (0 <= yy < ch):
            continue
        for x in range(w):
            v = idx[y * w + (w - 1 - x) if reflect else y * w + x]
            if v == TRANSPARENT:
                continue
            xx = dx + x
            if 0 <= xx < cw:
                canvas[yy * cw + xx] = v


def load_battle(palette):
    agg, ent = read_agg_index_with_expansion(AGG_PATH)
    canvas = bytearray([BACKDROP]) * (BATTLE_W * BATTLE_H)

    def icn_frame(name, frame):
        h, e = read_icn(agg_entry(agg, ent, name))[frame]
        return decode_icn_indices(h, e), h["w"], h["h"], h.get("ox", 0), h.get("oy", 0)

    # 1) Фон поля CBKG* (640×443) @ (0,0).
    bg, bw, bh, _, _ = icn_frame(BG_NAME, 0)
    for y in range(min(bh, BATTLE_H)):
        for x in range(min(bw, BATTLE_W)):
            canvas[y * BATTLE_W + x] = bg[y * bw + x]

    # 1b) COVR (большой грунт-декор, battle_interface.cpp:2448) — ВРЕМЕННО УБРАН: запечённый в сплит-фон
    #     ×1.6 он бьётся на шве y=240 (сдвиг строк). Переделать отдельным ×1.6-спрайтом поверх, не в фон.

    # 2) Боевые юниты в композит НЕ вшиваются — они ДИНАМИЧЕСКИЕ (спрайты в RAM_G, рисуются
    #    Render_Battle по таблице состояния; см. extract_units/emit_inc). Так юниты можно двигать.

    # 3) Нижняя панель боя (battle_interface.cpp:1482-1499) — band y[443..480) 37px:
    #    Auto(TEXTBAR4 49×18)@(0,443) над Settings(TEXTBAR6 49×19)@(0,461) — низ-лево;
    #    статус-бар Status_upper(TEXTBAR8 543×20)@(49,443)+Status_lower(TEXTBAR9 543×17)@(49,463);
    #    Skip(TEXTBAR0 49×37)@(591,443) — низ-право. (TEXTBAR ox/oy=0.)
    panel = [(4, 0, 443), (6, 0, 461), (8, 49, 443), (9, 49, 463), (0, 591, 443)]
    for frame, dx, dy in panel:
        s, w, h, _ox, _oy = icn_frame("TEXTBAR.ICN", frame)
        _blit(canvas, s, w, h, dx, dy)
    return bytes(canvas)


def load_units(agg, ent):
    # 4 варианта × N кадров idle: [Peasant_n, Peasant_m, Archer_n, Archer_m]. mirror = горизонт. флип.
    # Кадры типа паддятся до ОБЩЕГО канваса (union bbox по ox/oy → тело монстра на месте при свапе).
    # Возврат: per variant (frame_blobs[N], w, h).
    out = []
    for ti, (name, _stand) in enumerate(UNIT_TYPES):
        icn = read_icn(agg_entry(agg, ent, name))
        raw = []
        for fr in UNIT_ANIM_FRAMES[ti]:
            h, e = icn[fr]
            raw.append((decode_icn_indices(h, e), h["w"], h["h"], h.get("ox", 0), h.get("oy", 0)))
        min_ox = min(ox for _, _, _, ox, _ in raw)
        min_oy = min(oy for _, _, _, _, oy in raw)
        CW = max(ox + w for _, w, _, ox, _ in raw) - min_ox
        CH = max(oy + h for _, _, h, _, oy in raw) - min_oy
        frames = []
        for idx, w, h, ox, oy in raw:                              # положить кадр в общий канвас
            cv = bytearray(CW * CH)
            dx, dy = ox - min_ox, oy - min_oy
            for y in range(h):
                for x in range(w):
                    cv[(dy + y) * CW + (dx + x)] = idx[y * w + x]
            frames.append(bytes(cv))
        out.append((frames, CW, CH))                              # normal (вправо)
        mir = []
        for blob in frames:                                       # mirror (защитник влево)
            m = bytearray(CW * CH)
            for y in range(CH):
                for x in range(CW):
                    m[y * CW + x] = blob[y * CW + (CW - 1 - x)]
            mir.append(bytes(m))
        out.append((mir, CW, CH))                                 # mirror (влево)
    return out                                                     # [P_n, P_m, A_n, A_m], each (frames[N],w,h)


# Статус-сообщения нижней панели — РЕАЛЬНЫЕ строки fheroes2 (battle_interface.cpp:2914/2928/3009):
# подсказка по наведению. %{monster} = имя отряда (Peasant/Archer plural). BattleStatusMsg (1-based):
# 1=Move Peasants here, 2=Move Archers here, 3=Attack Peasants, 4=Attack Archers,
# 5=Shoot Peasants, 6=Shoot Archers. msg=0 → "Turn N" (рендерится "Turn "+номер раунда).
STATUS_MESSAGES = ["Move Peasants here", "Move Archers here",
                   "Attack Peasants", "Attack Archers",
                   "Shoot Peasants", "Shoot Archers"]
STATUS_TURN_MAX = 10                 # предрендер "Turn 1".."Turn 10" (номер раунда, fheroes2 "Turn %{turn}")


TEXT_FONT = "FONT.ICN"               # нормальный шрифт fheroes2 (FontType::normalWhite), как статус-бар
TEXT_SCALE = 1.6                     # пред-масштаб глифов под ×1.6-UI, ГЛАДКО (антиалиас) — не FT812-NEAREST
TEXT_SPACE_W = {"FONT.ICN": 6, "SMALFONT.ICN": 4}

def render_text_mask(agg, ent, text, font=None, scale=None):
    """Строка → антиалиас-маска (idx 0..15 = уровень альфы белого) шрифтом FONT.ICN, пред-масштаб
    ×1.6 ГЛАДКО (PIL BILINEAR) → НЕ рвётся аппаратным NEAREST (см. fonts-native-no-1p6-upscale).
    На FT812 блитится НАТИВНО (transform 256). Возврат (mask, W, H) уже масштабированного размера."""
    from PIL import Image
    font = font or TEXT_FONT
    scale = scale or TEXT_SCALE
    space_w = TEXT_SPACE_W.get(font, 6)
    fn = read_icn(agg_entry(agg, ent, font))
    glyphs, total_w, max_h = [], 0, 0
    for c in text:
        if c == " ":
            glyphs.append((None, space_w, 0, 0)); total_w += space_w; continue
        h, e = fn[ord(c) - 32]
        gi = decode_icn_indices(h, e)
        gw, gh, goy = h["w"], h["h"], h.get("oy", 0)
        glyphs.append((gi, gw, gh, goy)); total_w += gw
        max_h = max(max_h, gh + goy)
    W0, H0 = max(1, total_w), max_h + 1
    base = Image.new("L", (W0, H0), 0)
    bp = base.load()
    x = 0
    for gi, gw, gh, goy in glyphs:
        if gi is not None:
            for yy in range(gh):
                py = goy + yy
                if 0 <= py < H0:
                    for xx in range(gw):
                        if gi[yy * gw + xx] != TRANSPARENT:
                            bp[x + xx, py] = 255
        x += gw
    W, H = max(1, round(W0 * scale)), max(1, round(H0 * scale))
    sc = base.resize((W, H), Image.BILINEAR).load()
    mask = bytearray(W * H)
    for yy in range(H):
        for xx in range(W):
            mask[yy * W + xx] = sc[xx, yy] >> 4          # 0..15 (4-бит индекс альфы)
    return bytes(mask), W, H


# Окно итога боя — ПО ИСХОДНИКУ fheroes2 StandardWindow::render (ui_window.cpp:139) +
# DialogBattleSummary (battle_dialogs.cpp:474). Константы StandardWindow (ui_window.cpp:35-44):
WIN_BORDER = 16            # borderSize = borderWidthPx
WIN_EDGE = 43             # borderEdgeOffset
WIN_TRANS = 10            # transitionSize (10px дизеринг-бленды — ОПУЩЕНЫ, аппаратно незначимо)
WIN_BGOFS = 22            # backgroundOffset (= cornerSize при hasBackground)
WIN_TEXTW = 303          # bsTextWidth; активная область = +32 ширина, 424 высота
WIN_TEXTY = 160          # bsTextYOffset


def _wblit(cv, CW, CH, src, sw, sx, sy, dx, dy, w, h, opaque=True):
    for y in range(h):
        yy = dy + y
        if not (0 <= yy < CH):
            continue
        for x in range(w):
            xx = dx + x
            if not (0 <= xx < CW):
                continue
            v = src[(sy + y) * sw + (sx + x)]
            if not opaque and v == TRANSPARENT:
                continue
            cv[yy * CW + xx] = v


def compose_win_dialog(agg, ent, victory=True):
    """Окно итога боя строго по DialogBattleSummary: StandardWindow (углы/верт.края WINLOSE[0],
    гориз.края SURDRBKG[0], тайл-фон STONEBAK[0]) + регион анимации WINLOSE[0]{43,32,231,133}
    с кадром WINCMBT (победа)/CMBTLOS (поражение) + заголовок + блок потерь + кнопка OK.
    Один PALETTED-спрайт глоб.палитры (всё непрозрачно). Аппаратная уступка: статичный кадр
    вместо looped-анимации; дизеринг-швы/внешняя тень опущены."""
    PAL = read_palette(agg_entry(agg, ent, "KB.PAL"))

    def spr(name, fr=0):
        h, e = read_icn(agg_entry(agg, ent, name))[fr]
        return decode_icn_indices(h, e), h["w"], h["h"], h.get("ox", 0), h.get("oy", 0)

    def nearest(rgb):
        best, bi = 1 << 30, 0
        for i, p in enumerate(PAL):
            d = (p[0]-rgb[0])**2 + (p[1]-rgb[1])**2 + (p[2]-rgb[2])**2
            if d < best:
                best, bi = d, i
        return bi

    SPACE_W = {"FONT.ICN": 6, "SMALFONT.ICN": 4}

    def tw(font, text):
        f = read_icn(agg_entry(agg, ent, font))
        return sum(SPACE_W[font] if c == " " else f[ord(c)-32][0]["w"] for c in text)

    def txt(cv, CW, CH, font, text, x, y, color):
        f = read_icn(agg_entry(agg, ent, font))
        cx = x
        for c in text:
            if c == " ":
                cx += SPACE_W[font]
                continue
            h, e = f[ord(c)-32]
            gi = decode_icn_indices(h, e)
            gw, gh, goy = h["w"], h["h"], h.get("oy", 0)
            for yy in range(gh):
                py = y + goy + yy
                if 0 <= py < CH:
                    for xx in range(gw):
                        if gi[yy*gw+xx] != TRANSPARENT:
                            if 0 <= cx+xx < CW:
                                cv[py*CW + cx+xx] = color
            cx += gw

    activeW, activeH = WIN_TEXTW + 32, 424
    V, VW, VH, _, _ = spr("WINLOSE.ICN")
    Hs, HW, HH, _, _ = spr("SURDRBKG.ICN")
    S, SW, SH, _, _ = spr("STONEBAK.ICN")
    cs = WIN_BGOFS
    waW, waH = activeW + 2*WIN_BORDER, activeH + 2*WIN_BORDER
    CW, CH = waW, waH
    cv = bytearray([BACKDROP]) * (CW*CH)
    rcoX, bcoY = waW-cs, waH-cs
    rcsX, bcsY = VW-cs, VH-cs
    # фон STONEBAK тайлами (renderBackgroundImage, borderOffset=22)
    bw, bh = waW-WIN_BGOFS*2, waH-WIN_BGOFS*2
    yy = 0
    while yy < bh:
        xx = 0
        chh = min(SH, bh-yy)
        while xx < bw:
            _wblit(cv, CW, CH, S, SW, 0, 0, WIN_BGOFS+xx, WIN_BGOFS+yy, min(SW, bw-xx), chh)
            xx += SW
        yy += SH
    # углы + расширения краёв (verticalSprite WINLOSE)
    for sX, sY, dX, dY in ((0, 0, 0, 0), (rcsX, 0, rcoX, 0), (0, bcsY, 0, bcoY), (rcsX, bcsY, rcoX, bcoY)):
        _wblit(cv, CW, CH, V, VW, sX, sY, dX, dY, cs, cs)
    ex = WIN_EDGE-cs
    rbe, bbe = VW-WIN_EDGE, VH-WIN_EDGE
    _wblit(cv, CW, CH, V, VW, cs, 0, cs, 0, ex, cs)
    _wblit(cv, CW, CH, V, VW, 0, cs, 0, cs, cs, ex)
    _wblit(cv, CW, CH, V, VW, rbe, 0, rcoX-ex, 0, ex, cs)
    _wblit(cv, CW, CH, V, VW, rcsX, cs, rcoX, cs, cs, ex)
    _wblit(cv, CW, CH, V, VW, cs, bcsY, cs, bcoY, ex, cs)
    _wblit(cv, CW, CH, V, VW, 0, bbe, 0, bcoY-ex, cs, ex)
    _wblit(cv, CW, CH, V, VW, rbe, bcsY, rcoX-ex, bcoY, ex, cs)
    _wblit(cv, CW, CH, V, VW, rcsX, bbe, rcoX, bcoY-ex, cs, ex)
    # вертикальные края WINLOSE (повтор)
    dbe = WIN_EDGE*2
    vch = min(waH, VH)-dbe
    _wblit(cv, CW, CH, V, VW, 0, WIN_EDGE, 0, WIN_EDGE, cs, vch)
    _wblit(cv, CW, CH, V, VW, rcsX, WIN_EDGE, rcoX, WIN_EDGE, cs, vch)
    vcop = (waH-dbe-1-WIN_TRANS)//(bbe-WIN_EDGE-WIN_TRANS)
    toY, stepY, frY = WIN_EDGE+vch, vch-WIN_TRANS, WIN_EDGE+WIN_TRANS
    for _ in range(max(0, vcop)):
        chh = min(vch, waH-WIN_EDGE-toY)
        if chh <= 0:
            break
        _wblit(cv, CW, CH, V, VW, 0, frY, 0, toY, cs, chh)
        _wblit(cv, CW, CH, V, VW, rcsX, frY, rcoX, toY, cs, chh)
        toY += stepY
    # горизонтальные края SURDRBKG (повтор)
    hsW, hsH = HW-WIN_BORDER, HH-WIN_BORDER
    hcw = min(waW, hsW)-dbe
    hcsX = WIN_EDGE+WIN_BORDER
    bbso = hsH-cs
    _wblit(cv, CW, CH, Hs, HW, hcsX, 0, WIN_EDGE, 0, hcw, cs)
    _wblit(cv, CW, CH, Hs, HW, hcsX, bbso, WIN_EDGE, bcoY, hcw, cs)
    hcop = (waW-dbe-1-WIN_TRANS)//(hsW-dbe-WIN_TRANS)
    toX, stepX, frX = WIN_EDGE+hcw, hcw-WIN_TRANS, hcsX+WIN_TRANS
    for _ in range(max(0, hcop)):
        cwid = min(hcw, waW-WIN_EDGE-toX)
        if cwid <= 0:
            break
        _wblit(cv, CW, CH, Hs, HW, frX, 0, toX, 0, cwid, cs)
        _wblit(cv, CW, CH, Hs, HW, frX, bbso, toX, bcoY, cwid, cs)
        toX += stepX
    # регион анимации WINLOSE[0]{43,32,231,133} + кадр WINCMBT/CMBTLOS
    roiX, roiY = WIN_BORDER, WIN_BORDER
    animX, animY = roiX + (activeW-231)//2 + 4, roiY + 21
    _wblit(cv, CW, CH, V, VW, 43, 32, animX-4, animY-4, 231, 133)
    anim_icn = "WINCMBT.ICN" if victory else "CMBTLOS1.ICN"
    # fheroes2-анимация = Blit(база) + Blit(оверлей), ОБА ПРОЗРАЧНО (respect index0). WINCMBT:
    # кадр0 = полная база (небо+древко+тёмный силуэт, 223×125 ox0), кадры1+ = узкий оверлей машущего
    # флага (146×125 ox32) → накладываем ОДИН оверлей прозрачно. CMBTLOS: все кадры полноразмерны →
    # только кадр0 (наложение двух полных фаз = смаз/ореол — прежний баг был opaque-кадром 1).
    a0, aw0, ah0, aox0, aoy0 = spr(anim_icn, 0)
    ag0 = a0
    _wblit(cv, CW, CH, a0, aw0, 0, 0, animX+aox0, animY+aoy0, aw0, ah0, opaque=False)
    a1, aw1, ah1, aox1, aoy1 = spr(anim_icn, 1)
    if aw1 < aw0:                                   # кадр1 уже базы → это оверлей (машущая часть)
        _wblit(cv, CW, CH, a1, aw1, 0, 0, animX+aox1, animY+aoy1, aw1, ah1, opaque=False)
    # Залить остаточные ПРОЗРАЧНЫЕ пиксели региона анимации непрозрачным небом: иначе на оверлее
    # поверх живого боя сквозь дыры (края флага / незакрытая дыра неба) просвечивает поле с гекс-тенями.
    sky = next((p for p in ag0 if p != TRANSPARENT), nearest((40, 60, 110)))
    for yy in range(133):
        ry = animY - 4 + yy
        if not (0 <= ry < CH):
            continue
        for xx in range(231):
            rx = animX - 4 + xx
            if 0 <= rx < CW and cv[ry * CW + rx] == TRANSPARENT:
                cv[ry * CW + rx] = sky
    # кнопка OK (BUTTON_SMALL_OKAY_GOOD -> ориг. SYSTEM.ICN OKAY), BOTTOM_CENTER, поля {0,5}
    ok, okw, okh, _, _ = spr("SYSTEM.ICN", 1)
    _wblit(cv, CW, CH, ok, okw, 0, 0, roiX+(activeW-okw)//2, roiY+activeH-okh-5, okw, okh, opaque=False)
    # ТЕКСТ окна НЕ запекаем в ×1.6-битмап (рвёт глифы) — возвращаем список надписей, рисуются
    # отдельными НАТИВНЫМИ спрайтами поверх (см. Battle_RenderWinText). y = ЛОКАЛЬНЫЙ в диалоге.
    sy = roiY + WIN_TEXTY
    cofs = sy + 96
    #  Заголовок faithful по BattleResult (battle_dialogs.cpp:507-527): победа=yellow «A glorious victory!»,
    #  поражение=white «Your forces suffer a bitter defeat.». Тег видимости: 1=победа, 2=поражение, 0=всегда.
    #  АППАРАТНОЕ ОГРАНИЧЕНИЕ: defeat-заголовок — SMALFONT ×1.6 (FONT.ICN ×1.6 ~20КБ не влезает в RAM_G);
    #  баннер CMBTLOS поражения (~30КБ) тоже не влезает → рамка WINLOSE[0] общая, анимация остаётся WINCMBT.
    #  Строки потерь (Attacker/Defender) — ДИНАМИЧНЫ (Battle_RenderCasualties); здесь только заголовки секции.
    texts = [("A glorious victory!", "yellow", sy, "FONT.ICN", 1),
             ("Your forces suffer a bitter defeat.", "white", sy, "SMALFONT.ICN", 2),
             ("Battlefield Casualties", "white", cofs, "SMALFONT.ICN", 0),
             ("Attacker", "white", cofs + 15, "SMALFONT.ICN", 0),
             ("Defender", "white", cofs + 75, "SMALFONT.ICN", 0)]
    #  Локальные Y линий потерь (под «Attacker»/«Defender»); faithful +36/+96 (battle_dialogs.cpp:591/603).
    cas_atk_ly = cofs + 34
    cas_def_ly = cofs + 94
    return bytes(cv), CW, CH, texts, cas_atk_ly, cas_def_ly


def build_payload(palette, img, units, agg, ent):
    payload = bytearray()

    def put(raw: bytes) -> int:
        addr = BATTLE_RAMG_BASE + align(len(payload), 4)
        while BATTLE_RAMG_BASE + len(payload) < addr:
            payload.append(0)
        payload.extend(raw)
        return addr

    pal_addr = put(palette_argb4444_opaque(palette))
    # Палитра для ЮНИТОВ-спрайтов: как фоновая, но индекс 0 = ПРОЗРАЧНЫЙ (ARGB4444 0x0000),
    # иначе фон-бокс спрайта (индекс 0) рисуется непрозрачным чёрным поверх травы.
    unit_pal = bytearray(palette_argb4444_opaque(palette))
    unit_pal[0:2] = b"\x00\x00"
    unit_pal_addr = put(bytes(unit_pal))
    # Нативные цифры счётчика отрядов (SMALFONT '0'-'9') В battle-PAK: глобальный DigitTable (#0C95xx)
    # и палитра #079200 затираются выросшим battle-payload (RAM_G-коллизия) → рисуем своими (палитра юнитов).
    sf_digits = read_icn(agg_entry(agg, ent, "SMALFONT.ICN"))
    count_digits = []
    for dd in range(10):
        h, e = sf_digits[ord("0") - 32 + dd]
        count_digits.append((put(bytes(decode_icn_indices(h, e))), h["w"], h["h"]))
    # Палитра гекс-тени: idx0 = прозрачный (0x0000), idx1 = полупрозрачный чёрный (A<<12).
    shadow_pal = bytearray(2 * 16)
    sval = SHADOW_ALPHA << 12          # ARGB4444: A=SHADOW_ALPHA, RGB=0 (чёрный)
    shadow_pal[2:4] = bytes((sval & 0xFF, sval >> 8))
    shadow_pal_addr = put(bytes(shadow_pal))
    shadow_addr = put(make_hex_shadow_mask(1))   # 44×52 PALETTED4444 (index 0/1)
    # Палитра-СИЛУЭТ для контура активного отряда: idx0 прозрачный, ВСЕ прочие → яркий циан
    # (ARGB4444 0xF0FF). Спрайт юнита с этой палитрой = сплошной циан-силуэт его формы.
    contour_pal = bytearray(2 * 256)
    for i in range(1, 256):
        contour_pal[i * 2] = 0xFF
        contour_pal[i * 2 + 1] = 0xF0
    contour_pal_addr = put(bytes(contour_pal))
    # Палитра статус-текста (антиалиас): idx i = БЕЛЫЙ с альфой i (ARGB4444 0xiFFF); idx0 прозрачен.
    status_pal = bytearray(2 * 256)
    for i in range(16):
        v = ((i << 12) | 0x0FFF) if i else 0
        status_pal[i * 2] = v & 0xFF
        status_pal[i * 2 + 1] = (v >> 8) & 0xFF
    status_pal_addr = put(bytes(status_pal))
    status_msgs = []                              # 6 hover-подсказок (Move/Attack/Shoot X)
    for text in STATUS_MESSAGES:
        m, w, h = render_text_mask(agg, ent, text)
        status_msgs.append((put(m), w, h))
    turn_msgs = []                                # "Turn 1".."Turn N" (номер раунда, fheroes2 "Turn %{turn}")
    for i in range(1, STATUS_TURN_MAX + 1):
        m, w, h = render_text_mask(agg, ent, "Turn " + str(i))
        turn_msgs.append((put(m), w, h))
    # --- ФРАГМЕНТЫ СТРОКИ СОБЫТИЙ (fheroes2 RedrawActionAttackPart2, battle_interface.cpp:4157):
    #     «%{atk} do %{dmg} damage.» (+ при гибели « %{n} %{def} perish.»). idx = type×2 + (count==1). ---
    def bake(t):
        m, w, h = render_text_mask(agg, ent, t)
        return (put(m), w, h)
    evt = {
        "atk": [bake(t) for t in ("Peasants do ", "Peasant does ", "Archers do ", "Archer does ")],
        "dmg": bake(" damage."),
        "space": bake(" "),
        "perish": [bake(t) for t in (" Peasants perish.", " Peasant perishes.",
                                     " Archers perish.", " Archer perishes.")],
        "digit": [bake(str(d)) for d in range(10)],
    }
    wdlg, wdw, wdh, wtexts, cas_atk_ly, cas_def_ly = compose_win_dialog(agg, ent)  # окно итога БЕЗ текста
    win_dlg = (put(wdlg), wdw, wdh)
    # Потери (faithful battle_dialogs.cpp:587 GetKilledTroops → drawSingleDetailedMonsterLine): иконка
    # MONS32 типа + счёт убитых. MONS32-индекс = монстр.id-1 → наш type (0=Peasant=MONS32[0], 1=Archer[1]).
    # Иконы — нативно, палитра ЮНИТОВ (idx0 прозрачный, KB.PAL-цвета); счёт — нативные BattleCountDigitTab.
    mons32 = read_icn(agg_entry(agg, ent, "MONS32.ICN"))
    casualty_icons = []
    for t in range(2):
        ih, ie = mons32[t]
        casualty_icons.append((put(bytes(decode_icn_indices(ih, ie))), ih["w"], ih["h"]))
    none_m, none_w, none_h = render_text_mask(agg, ent, "None", font="SMALFONT.ICN")  # ×1.6 бел., статус-пал.
    none_sprite = (put(none_m), none_w, none_h)
    # Y линий потерь в vertex 1/16px (×1.6): wty = верх окна на экране 480 (ниже).
    # Жёлтая палитра заголовка победы (антиалиас): idx i = ЖЁЛТЫЙ (0x0FF0) с альфой i.
    yellow_pal = bytearray(2 * 256)
    for i in range(16):
        v = ((i << 12) | 0x0FF0) if i else 0
        yellow_pal[i * 2] = v & 0xFF
        yellow_pal[i * 2 + 1] = (v >> 8) & 0xFF
    yellow_pal_addr = put(bytes(yellow_pal))
    # Надписи окна — НАТИВНЫЕ спрайты (full-size антиалиас). Длинные строки БЬЁМ НА СЛОВА (каждое
    # < 255px — поле ширины байт), кладём подряд центрированно. y=(wty+ly)×1.6 в vertex 1/16px.
    wty = (480 - wdh) // 2
    cas_atk_vy = (wty + cas_atk_ly) * 256 // 10        # Y линий потерь (×1.6, 1/16px)
    cas_def_vy = (wty + cas_def_ly) * 256 // 10
    casualties = (casualty_icons, none_sprite, cas_atk_vy, cas_def_vy)
    win_texts = []
    for text, color, ly, font, result in wtexts:
        words = text.split(" ")
        sprites, total = [], 0
        for k, word in enumerate(words):
            t = word + (" " if k < len(words) - 1 else "")
            m, w, h = render_text_mask(agg, ent, t, font=font)
            sprites.append((m, w, h)); total += w
        sx = 512 - total // 2                         # центр по X (диалог центрирован)
        vy = (wty + ly) * 256 // 10
        for (m, w, h) in sprites:
            win_texts.append((put(m), w, h, 1 if color == "yellow" else 0, sx * 16, vy, result))
            sx += w
    top = img[: BATTLE_W * BATTLE_SPLIT]         # 640×240
    bot = img[BATTLE_W * BATTLE_SPLIT:]          # 640×240
    top_addr = put(top)
    bot_addr = put(bot)
    unit_addrs = [[put(blob) for blob in frames] for frames, _w, _h in units]  # [variant][frame]=addr
    return (payload, pal_addr, unit_pal_addr, shadow_pal_addr, shadow_addr, contour_pal_addr,
            status_pal_addr, status_msgs, turn_msgs, win_dlg, top_addr, bot_addr, unit_addrs, evt,
            yellow_pal_addr, win_texts, count_digits, casualties)


def emit_inc(pal_addr, unit_pal_addr, shadow_pal_addr, shadow_addr, contour_pal_addr,
             status_pal_addr, status_msgs, turn_msgs, win_dlg, top_addr, bot_addr, unit_addrs, evt,
             yellow_pal_addr, win_texts, count_digits, casualties, units, pak):
    L = []
    L.append("; Сгенерировано Source/Tools/battle_pack.py — экран боя (Grass, потоковый HMM2BATL.PAK).")
    L.append("                ifndef _HMM2_GENERATED_BATTLE_")
    L.append("                define _HMM2_GENERATED_BATTLE_")
    L.append("")
    L.append(f"BATTLE_PAL_RAMG      EQU #{pal_addr:06X}")
    L.append(f"BATTLE_TOP_RAMG      EQU #{top_addr:06X}")
    L.append(f"BATTLE_BOT_RAMG      EQU #{bot_addr:06X}")
    L.append(f"BATTLE_SHADOW_PAL_RAMG EQU #{shadow_pal_addr:06X}")
    L.append(f"BATTLE_SHADOW_RAMG   EQU #{shadow_addr:06X}")
    L.append(f"BATTLE_CONTOUR_PAL_RAMG EQU #{contour_pal_addr:06X}")
    L.append("")
    L.append("Battle_DL:")
    L.append("                FT_CLEAR_COLOR_RGB 0, 0, 0")
    L.append("                FT_CLEAR 1, 1, 1")
    L.append("                FT_SCISSOR_XY 0, 0")
    L.append("                FT_SCISSOR_SIZE 1024, 768")
    L.append("                FT_COLOR_RGB 255, 255, 255")
    L.append("                FT_COLOR_A 255")
    L.append("                FT_BITMAP_HANDLE 0")
    L.append("                FT_CELL 0")
    L.append("                FT_BITMAP_TRANSFORM_A 160")
    L.append("                FT_BITMAP_TRANSFORM_B 0")    # СБРОС skew (протекает из adventure-флипа актёра;
    L.append("                FT_BITMAP_TRANSFORM_C 0")    #   ненулевой B → tex_x+=B·y/256 на строку = диагональный
    L.append("                FT_BITMAP_TRANSFORM_D 0")    #   перекос текста окна, копящийся по высоте. Как hiscores.asm)
    L.append("                FT_BITMAP_TRANSFORM_E 160")
    L.append("                FT_BITMAP_TRANSFORM_F 0")
    L.append("                FT_VERTEX_TRANSLATE_X 0")
    L.append("                FT_VERTEX_TRANSLATE_Y 0")
    L.append("                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA")
    L.append("                FT_BITMAP_LAYOUT_H 0, 0")
    L.append("                FT_BITMAP_SIZE_H 0, 0")
    L.append("                FT_PALETTE_SOURCE BATTLE_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    _bot_h = BATTLE_H - BATTLE_SPLIT
    L.append("                FT_BITMAP_SOURCE BATTLE_TOP_RAMG")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {BATTLE_W}, {BATTLE_SPLIT}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {BATTLE_W * 16 // 10}, {BATTLE_SPLIT * 16 // 10}")
    L.append("                FT_VERTEX2F 0, 0")
    L.append("                FT_BITMAP_SOURCE BATTLE_BOT_RAMG")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {BATTLE_W}, {_bot_h}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {BATTLE_W * 16 // 10}, {_bot_h * 16 // 10}")
    L.append(f"                FT_VERTEX2F 0, {BATTLE_SPLIT * 256 // 10}")
    L.append("                FT_END")
    L.append("Battle_DL_SIZE EQU $ - Battle_DL")
    L.append("")
    # --- Подсветка наведённой гекс-ячейки (B-логика): префикс/суффикс DL + таблица вершин. ---
    # Render_Battle по индексу ячейки копирует BattleCellVerts[cell*8] (2× FT_VERTEX2F) между
    # префиксом (полупрозрачный жёлтый RECTS) и суффиксом (END + восстановление цвета для курсора).
    L.append("Battle_HL_Pre_DL:")                  # жёлтая подсветка наведённой курсором ячейки
    L.append("                FT_COLOR_RGB 255, 255, 0")
    L.append("                FT_COLOR_A 90")
    L.append("                FT_LINE_WIDTH 16")
    L.append("                FT_BEGIN FT_RECTS")
    L.append("Battle_HL_Pre_DL_SIZE EQU $ - Battle_HL_Pre_DL")
    L.append("Battle_HL_Active_Pre_DL:")           # зелёная подсветка ячейки активного юнита (чей ход)
    L.append("                FT_COLOR_RGB 0, 255, 0")
    L.append("                FT_COLOR_A 90")
    L.append("                FT_LINE_WIDTH 16")
    L.append("                FT_BEGIN FT_RECTS")
    L.append("Battle_HL_Active_Pre_DL_SIZE EQU $ - Battle_HL_Active_Pre_DL")
    L.append("Battle_HL_Post_DL:")
    L.append("                FT_END")
    L.append("                FT_COLOR_A 255")
    L.append("                FT_COLOR_RGB 255, 255, 255")
    L.append("Battle_HL_Post_DL_SIZE EQU $ - Battle_HL_Post_DL")
    L.append("BattleCellVerts:                       ; 99 ячеек × 2 FT_VERTEX2F (8Б/ячейка), физ.×1.6")
    for idx in range(WIDTH_IN_CELLS * 9):
        row, col = idx // WIDTH_IN_CELLS, idx % WIDTH_IN_CELLS
        px = CELL_OX - (CELL_W // 2 if row % 2 else 0) + CELL_W * col
        py = CELL_OY + ROW_STEP * row
        L.append(f"                FT_VERTEX2F {px * 256 // 10}, {py * 256 // 10}")
        L.append(f"                FT_VERTEX2F {(px + CELL_W) * 256 // 10}, {(py + CELL_H) * 256 // 10}")
    L.append("")
    # --- ГЕКС-ТЕНЬ наведённой клетки (faithful, как fheroes2 _hexagonCursorShadow): спрайт-маска
    #     ×1.6 на клетке (вершина = top-left из BattleCellVerts[cell*8], 4Б). Под юнитами. ---
    L.append("Battle_Shadow_Pre_DL:")
    L.append("                FT_BITMAP_TRANSFORM_A 160")     # ×1.6 как фон
    L.append("                FT_BITMAP_TRANSFORM_E 160")
    L.append("                FT_PALETTE_SOURCE BATTLE_SHADOW_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("                FT_BITMAP_SOURCE BATTLE_SHADOW_RAMG")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {CELL_W}, {CELL_H}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {CELL_W * 16 // 10}, {CELL_H * 16 // 10}")
    L.append("Battle_Shadow_Pre_DL_SIZE EQU $ - Battle_Shadow_Pre_DL")
    L.append("Battle_Shadow_Post_DL:")
    L.append("                FT_END")
    L.append("Battle_Shadow_Post_DL_SIZE EQU $ - Battle_Shadow_Post_DL")
    L.append("")
    # --- КОНТУР активного отряда (как fheroes2 — подсветка контура спрайта): силуэт спрайта
    #     палитрой-циан, смещённый ±2px в 4 стороны ПОД реальным спрайтом → 2px-обводка. ---
    L.append("Battle_Contour_Begin_DL:")
    L.append("                FT_BITMAP_TRANSFORM_A 160")
    L.append("                FT_BITMAP_TRANSFORM_E 160")
    L.append("                FT_PALETTE_SOURCE BATTLE_CONTOUR_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("Battle_Contour_Begin_DL_SIZE EQU $ - Battle_Contour_Begin_DL")
    L.append("Battle_Contour_End_DL:")
    L.append("                FT_VERTEX_TRANSLATE_X 0")
    L.append("                FT_VERTEX_TRANSLATE_Y 0")
    L.append("                FT_END")
    L.append("Battle_Contour_End_DL_SIZE EQU $ - Battle_Contour_End_DL")
    # 4 смещения силуэта (±2px = 32 в 1/16) для обводки + и −, X и Y. Render_Battle копирует
    # [смещение_i] + [вершина активного юнита] ×4.
    for i, (dx, dy) in enumerate([(32, 0), (-32, 0), (0, 32), (0, -32)]):
        L.append(f"Battle_Contour_Ofs{i}_DL:")
        L.append(f"                FT_VERTEX_TRANSLATE_X {dx}")
        L.append(f"                FT_VERTEX_TRANSLATE_Y {dy}")
    L.append("BATTLE_CONTOUR_OFS_SIZE EQU Battle_Contour_Ofs1_DL - Battle_Contour_Ofs0_DL")
    L.append("BattleContourOfsTab:")
    L.append("                DEFW Battle_Contour_Ofs0_DL, Battle_Contour_Ofs1_DL")
    L.append("                DEFW Battle_Contour_Ofs2_DL, Battle_Contour_Ofs3_DL")
    L.append("")
    # --- СТАТУС-СООБЩЕНИЯ нижней панели (как fheroes2): белый текст SMALFONT, ×1.6, центрирован
    #     в статус-баре. BattleStatusMsg (1-based) → Pre[idx] (SOURCE/LAYOUT/SIZE) + Vert[idx]. ---
    L.append(f"BATTLE_STATUS_PAL_RAMG EQU #{status_pal_addr:06X}")
    L.append("Battle_Status_Begin_DL:")
    L.append("                FT_BITMAP_TRANSFORM_A 256   ; НАТИВНО (×1): ×1.6 NEAREST рвёт глифы (см. fonts-native-no-1p6-upscale)")
    L.append("                FT_BITMAP_TRANSFORM_E 256")
    L.append("                FT_PALETTE_SOURCE BATTLE_STATUS_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("Battle_Status_Begin_DL_SIZE EQU $ - Battle_Status_Begin_DL")
    L.append("Battle_Status_End_DL:")
    L.append("                FT_END")
    L.append("Battle_Status_End_DL_SIZE EQU $ - Battle_Status_End_DL")
    L.append("BattleStatusPreTab:")
    L.append("                DEFW " + ", ".join(f"Battle_Status_Pre_{i}" for i in range(len(status_msgs))))
    for i, (addr, w, h) in enumerate(status_msgs):
        L.append(f"Battle_Status_Pre_{i}:")
        L.append(f"                FT_BITMAP_SOURCE #{addr:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {w}, {h}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {w}, {h}")  # НАТИВНО (×1)
    L.append("BATTLE_STATUS_PRE_SIZE EQU Battle_Status_Pre_1 - Battle_Status_Pre_0")
    L.append("BattleStatusVertTab:                   ; центр физ. (512, y=717); текст НАТИВНЫЙ (без ×1.6)")
    for (addr, w, h) in status_msgs:
        lx = 512 - w // 2                            # физ-центр 320×1.6=512, минус нативная полуширина
        L.append(f"                FT_VERTEX2F {lx * 16}, {448 * 256 // 10}")
    L.append(f"BATTLE_STATUS_COUNT EQU {len(status_msgs)}")
    L.append("")
    # --- "Turn N" (fheroes2 "Turn %{turn}"): предрендер Turn 1..MAX, выбор по номеру раунда.
    #     Тот же статус-бар (Battle_Status_Begin_DL), центрировано как hover-подсказки. ---
    L.append("BattleTurnPreTab:")
    L.append("                DEFW " + ", ".join(f"Battle_Turn_Pre_{i}" for i in range(len(turn_msgs))))
    for i, (addr, w, h) in enumerate(turn_msgs):
        L.append(f"Battle_Turn_Pre_{i}:")
        L.append(f"                FT_BITMAP_SOURCE #{addr:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {w}, {h}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {w}, {h}")  # НАТИВНО (×1)
    L.append("BATTLE_TURN_PRE_SIZE EQU Battle_Turn_Pre_1 - Battle_Turn_Pre_0")
    L.append("BattleTurnVertTab:                     ; центр физ. (512, y=717); текст НАТИВНЫЙ (без ×1.6)")
    for (addr, w, h) in turn_msgs:
        lx = 512 - w // 2
        L.append(f"                FT_VERTEX2F {lx * 16}, {448 * 256 // 10}")
    L.append(f"BATTLE_TURN_MAX EQU {len(turn_msgs)}")
    L.append("")
    # --- ФРАГМЕНТЫ СТРОКИ СОБЫТИЙ: записи [lo,mid,hi,w,h] для Render_DrawSpriteEntry (перо ResPenX,
    #     нативный блит ×1, антиалиас-палитра статуса). Сборка строки — Battle_RenderEventLine. ---
    def ee(e):
        a, w, h = e
        return f"                DEFB #{a & 0xFF:02X}, #{(a >> 8) & 0xFF:02X}, #{(a >> 16) & 0xFF:02X}, {w}, {h}"
    L.append("EVT_ENTRY_SIZE EQU 5")
    L.append("BattleEvtAtkTab:                       ; «<atk> do/does » idx=type×2+(count==1)")
    for e in evt["atk"]:
        L.append(ee(e))
    L.append("BattleEvtDmgSfx:                       ; « damage.»")
    L.append(ee(evt["dmg"]))
    L.append("BattleEvtSpace:                        ; « » (между damage. и числом гибели)")
    L.append(ee(evt["space"]))
    L.append("BattleEvtPerishTab:                    ; « <def> perish(es).» idx=type×2+(killed==1)")
    for e in evt["perish"]:
        L.append(ee(e))
    L.append("BattleEvtDigitTab:                     ; «0».. «9» (тот же шрифт, что слова)")
    for e in evt["digit"]:
        L.append(ee(e))
    L.append("")
    # --- НАДПИСИ ОКНА ИТОГА: нативные спрайты поверх ×1.6-диалога (не рвутся). Запись (10б):
    #     [lo,mid,hi,w,h] + палитра(0=белая/1=жёлтая) + vx(2) + vy(2). Рендер — Battle_RenderWinText. ---
    L.append(f"BATTLE_YELLOW_PAL_RAMG EQU #{yellow_pal_addr:06X}")
    L.append("Battle_WinTitle_Begin_DL:              ; пролог заголовка победы (жёлтая палитра, нативно)")
    L.append("                FT_BITMAP_TRANSFORM_A 256")
    L.append("                FT_BITMAP_TRANSFORM_E 256")
    L.append("                FT_PALETTE_SOURCE BATTLE_YELLOW_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("Battle_WinTitle_Begin_DL_SIZE EQU $ - Battle_WinTitle_Begin_DL")
    L.append("WIN_TEXT_REC EQU 11")                  # +0..2 addr, +3 w, +4 h, +5 палитра, +6 vx, +8 vy, +10 результат
    L.append(f"BATTLE_WIN_TEXT_COUNT EQU {len(win_texts)}")
    L.append("BattleWinTextTab:")
    for (addr, w, h, ye, vx, vy, result) in win_texts:
        L.append(f"                DEFB #{addr & 0xFF:02X}, #{(addr >> 8) & 0xFF:02X}, "
                 f"#{(addr >> 16) & 0xFF:02X}, {w}, {h}, {ye}")
        L.append(f"                DEFW {vx}, {vy}")
        L.append(f"                DEFB {result}      ; видимость: 0=всегда, 1=победа, 2=поражение")
    L.append("")
    # --- ОКНО ИТОГА (faithful, как fheroes2 DialogBattleSummary): WINLOSE рамка + баннер,
    #     центрировано ×1.6, палитра юнитов (idx0 прозрачный → поле видно вокруг окна). ---
    wda, wdw, wdh = win_dlg
    wlx, wty = (640 - wdw) // 2, (480 - wdh) // 2
    L.append(f"BATTLE_WIN_DLG_RAMG EQU #{wda:06X}")
    ndw, ndh = wdw * 16 // 10, wdh * 16 // 10        # native размер ×1.6 (>511 → нужны старшие биты!)
    L.append("Battle_WinDlg_DL:")
    L.append("                FT_BITMAP_TRANSFORM_A 160")
    L.append("                FT_BITMAP_TRANSFORM_E 160")
    L.append("                FT_BITMAP_LAYOUT_H 0, 0")
    L.append(f"                FT_BITMAP_SIZE_H {ndw}, {ndh}")   # старшие биты ширины/высоты (>511)
    L.append("                FT_PALETTE_SOURCE BATTLE_UNIT_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("                FT_BITMAP_SOURCE BATTLE_WIN_DLG_RAMG")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {wdw}, {wdh}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {ndw}, {ndh}")
    L.append(f"                FT_VERTEX2F {wlx * 256 // 10}, {wty * 256 // 10}")
    L.append("                FT_BITMAP_SIZE_H 0, 0")            # сброс старших бит (иначе курсор/др. поедут)
    L.append("                FT_END")
    L.append("Battle_WinDlg_DL_SIZE EQU $ - Battle_WinDlg_DL")
    L.append("")
    # --- ДИНАМИЧЕСКИЕ ЮНИТЫ: BEGIN/END + per-variant префикс (SOURCE/LAYOUT/SIZE) + вершины
    #     per-type (спрайт top-left @ ячейке) + таблица состояния {тип,cell,side}. ---
    L.append(f"BATTLE_UNIT_PAL_RAMG EQU #{unit_pal_addr:06X}")
    L.append("Battle_Units_Begin_DL:")
    L.append("                FT_PALETTE_SOURCE BATTLE_UNIT_PAL_RAMG")   # прозрачная палитра юнитов (idx0=alpha0)
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("Battle_Units_Begin_DL_SIZE EQU $ - Battle_Units_Begin_DL")
    L.append("Battle_Units_End_DL:")
    L.append("                FT_END")
    L.append("Battle_Units_End_DL_SIZE EQU $ - Battle_Units_End_DL")
    # idle-анимация: SOURCE свапается по кадру [вариант×N+кадр]; LAYOUT/SIZE общий по варианту.
    L.append(f"BATTLE_UNIT_FRAME_COUNT EQU {UNIT_FRAME_COUNT}")
    L.append("BattleUnitSrcTab:                       ; [вариант*N+кадр] → FT_BITMAP_SOURCE (4Б)")
    for v in range(len(units)):
        for f in range(UNIT_FRAME_COUNT):
            L.append(f"                FT_BITMAP_SOURCE #{unit_addrs[v][f]:06X}")
    L.append("BATTLE_UNIT_SRC_SIZE EQU 4")            # FT_BITMAP_SOURCE = 1 команда = 4Б
    L.append("BattleUnitLayTab:                       ; [вариант] → LAYOUT+SIZE (общий канвас кадров, 8Б)")
    for v, (_frames, w, h) in enumerate(units):
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {w}, {h}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {w * 16 // 10}, {h * 16 // 10}")
    L.append("BATTLE_UNIT_LAY_SIZE EQU 8")            # LAYOUT+SIZE = 2 команды = 8Б
    L.append("BattleUnitVertsTab:")
    L.append("                DEFW BattleUnitVerts0, BattleUnitVerts1")
    for t in range(len(UNIT_TYPES)):
        _frames, w, h = units[t * 2]
        L.append(f"BattleUnitVerts{t}:                    ; спрайт top-left @ каждой из 99 ячеек (тип {t})")
        for idx in range(WIDTH_IN_CELLS * 9):
            row, col = idx // WIDTH_IN_CELLS, idx % WIDTH_IN_CELLS
            px = CELL_OX - (CELL_W // 2 if row % 2 else 0) + CELL_W * col + (CELL_W - w) // 2
            py = CELL_OY + ROW_STEP * row + (CELL_H - h)
            L.append(f"                FT_VERTEX2F {px * 256 // 10}, {py * 256 // 10}")
    # Группы кадров анимации (раскладка 12 кадров/вариант: idle@0×4, walk@4×8)
    L.append(f"BATTLE_UNIT_IDLE_BASE EQU {UNIT_IDLE_BASE}")
    L.append(f"BATTLE_UNIT_WALK_BASE EQU {UNIT_WALK_BASE}")
    L.append(f"BATTLE_UNIT_WALK_N EQU {UNIT_WALK_N}")
    L.append(f"BATTLE_UNIT_ATK_BASE EQU {UNIT_ATK_BASE}")
    L.append(f"BATTLE_UNIT_ATK_N EQU {UNIT_ATK_N}")
    L.append(f"BATTLE_UNIT_DEATH_BASE EQU {UNIT_DEATH_BASE}")
    L.append(f"BATTLE_UNIT_DEATH_N EQU {UNIT_DEATH_N}")
    # Сырые пиксельные позиции спрайта в клетке (vertex 1/16px) для ИНТЕРПОЛЯЦИИ движущегося юнита.
    L.append("BattleUnitPixTab:                       ; [тип] → 99×(x,y) DEFW (top-left спрайта в клетке)")
    L.append("                DEFW BattleUnitPix0, BattleUnitPix1")
    for t in range(len(UNIT_TYPES)):
        _frames, w, h = units[t * 2]
        L.append(f"BattleUnitPix{t}:")
        for idx in range(WIDTH_IN_CELLS * 9):
            row, col = idx // WIDTH_IN_CELLS, idx % WIDTH_IN_CELLS
            px = CELL_OX - (CELL_W // 2 if row % 2 else 0) + CELL_W * col + (CELL_W - w) // 2
            py = CELL_OY + ROW_STEP * row + (CELL_H - h)
            L.append(f"                DEFW {px * 256 // 10}, {py * 256 // 10}")
    # --- СЧЁТЧИКИ ОТРЯДОВ (fheroes2 RedrawTroopCount): тёмный бар + белое число над юнитом.
    #     Бар — полупрозрачный чёрный RECTS (контраст на траве); число — DigitTable
    #     (резидентный Render_Number16C, палитра OBJECT_OPAQUE_PALETTE, цифры native 1:1).
    L.append("Battle_CountBar_Pre_DL:")
    L.append("                FT_COLOR_RGB 0, 0, 0")
    L.append("                FT_COLOR_A 150")
    L.append("                FT_LINE_WIDTH 16")
    L.append("                FT_BEGIN FT_RECTS")
    L.append("Battle_CountBar_Pre_DL_SIZE EQU $ - Battle_CountBar_Pre_DL")
    L.append("Battle_CountBar_Post_DL:")
    L.append("                FT_END")
    L.append("                FT_COLOR_A 255")
    L.append("                FT_COLOR_RGB 255, 255, 255")
    L.append("Battle_CountBar_Post_DL_SIZE EQU $ - Battle_CountBar_Post_DL")
    L.append("Battle_Count_Begin_DL:")
    L.append("                FT_BITMAP_TRANSFORM_A 256")    # цифры 1:1 native (не апскейл фона ×1.6)
    L.append("                FT_BITMAP_TRANSFORM_E 256")
    L.append("                FT_PALETTE_SOURCE BATTLE_UNIT_PAL_RAMG")  # своя палитра боя (idx0 прозр) — OBJECT_OPAQUE затёрт payload'ом
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("Battle_Count_Begin_DL_SIZE EQU $ - Battle_Count_Begin_DL")
    L.append("BattleCountDigitTab:                   ; нативные цифры '0'-'9' В battle-PAK [lo,mid,hi,w,h]")
    for (addr, w, h) in count_digits:
        L.append(f"                DEFB #{addr & 0xFF:02X}, #{(addr >> 8) & 0xFF:02X}, "
                 f"#{(addr >> 16) & 0xFF:02X}, {w}, {h}")
    L.append("Battle_Count_End_DL:")
    L.append("                FT_END")
    L.append("Battle_Count_End_DL_SIZE EQU $ - Battle_Count_End_DL")
    # --- Потери боя (faithful battle_dialogs.cpp): иконы MONS32 типов (нативно, палитра юнитов) + ---
    # --- «None» (×1.6 бел., статус-палитра). Y линий потерь — vertex 1/16px. ---
    cas_icons, none_spr, cas_atk_vy, cas_def_vy = casualties
    L.append("BattleCasualtyIconTab:                 ; иконы MONS32 type 0/1 [lo,mid,hi,w,h] (палитра юнитов)")
    for (addr, w, h) in cas_icons:
        L.append(f"                DEFB #{addr & 0xFF:02X}, #{(addr >> 8) & 0xFF:02X}, "
                 f"#{(addr >> 16) & 0xFF:02X}, {w}, {h}")
    na, nw, nh = none_spr
    L.append("BattleNoneSprite:                      ; «None» ×1.6 бел. [lo,mid,hi,w,h] (статус-палитра)")
    L.append(f"                DEFB #{na & 0xFF:02X}, #{(na >> 8) & 0xFF:02X}, "
             f"#{(na >> 16) & 0xFF:02X}, {nw}, {nh}")
    L.append(f"BATTLE_CAS_ATK_Y     EQU {cas_atk_vy}")
    L.append(f"BATTLE_CAS_DEF_Y     EQU {cas_def_vy}")
    L.append("BattleCountBarVerts:                   ; 99 ячеек × 2 FT_VERTEX2F (тёмный бар под числом)")
    for idx in range(WIDTH_IN_CELLS * 9):
        row, col = idx // WIDTH_IN_CELLS, idx % WIDTH_IN_CELLS
        px = CELL_OX - (CELL_W // 2 if row % 2 else 0) + CELL_W * col
        py = CELL_OY + ROW_STEP * row
        cx = px + CELL_W // 2
        bx0, bx1 = cx - 13, cx + 13
        by0, by1 = py + CELL_H - 16, py + CELL_H - 3
        L.append(f"                FT_VERTEX2F {bx0 * 256 // 10}, {by0 * 256 // 10}")
        L.append(f"                FT_VERTEX2F {bx1 * 256 // 10}, {by1 * 256 // 10}")
    L.append("BattleCountPen:                        ; 99 ячеек × {DEFW penX, DEFW penY} центр-низ (vertex)")
    for idx in range(WIDTH_IN_CELLS * 9):
        row, col = idx // WIDTH_IN_CELLS, idx % WIDTH_IN_CELLS
        px = CELL_OX - (CELL_W // 2 if row % 2 else 0) + CELL_W * col
        py = CELL_OY + ROW_STEP * row
        cx = px + CELL_W // 2
        penx = cx * 256 // 10
        peny = int(((py + CELL_H - 16) * 1.6 + 5.4) * 16)   # 10px native цифра по центру 13px бара
        L.append(f"                DEFW {penx}, {peny}")
    # --- ГЕКС-СОСЕДСТВО (fheroes2 battle_board.cpp GetIndexDirection/isValidDirection, 11×9):
    #     6 соседей на клетку {TL,TR,L,R,BL,BR} или #FF. Для гейта ближнего боя (melee→только сосед). ---
    L.append("BattleAdjTab:                          ; 99 ячеек × 6 соседей (#FF=нет)")
    Wc, Hc = WIDTH_IN_CELLS, 9
    for idx in range(Wc * Hc):
        x, y = idx % Wc, idx // Wc
        odd = y % 2
        n = []
        n.append(idx - (Wc + 1 if odd else Wc) if not (y == 0 or (x == 0 and odd)) else 0xFF)            # TL
        n.append(idx - (Wc if odd else Wc - 1) if not (y == 0 or (x == Wc - 1 and not odd)) else 0xFF)   # TR
        n.append(idx - 1 if x != 0 else 0xFF)                                                            # L
        n.append(idx + 1 if x != Wc - 1 else 0xFF)                                                       # R
        n.append(idx + (Wc - 1 if odd else Wc) if not (y == Hc - 1 or (x == 0 and odd)) else 0xFF)       # BL
        n.append(idx + (Wc if odd else Wc + 1) if not (y == Hc - 1 or (x == Wc - 1 and not odd)) else 0xFF)  # BR
        L.append("                DEFB " + ", ".join(str(v) for v in n))
    L.append("")
    L.append(f"BATTLE_UNIT_COUNT    EQU {len(UNIT_STATE)}")
    L.append("BATTLE_UNIT_STATE_SIZE EQU 5            ; {тип, cell, side, count_lo, count_hi}")
    L.append("BattleUnitStateInit:                   ; read-only старт; Battle_Enter → BattleUnitState")
    for (t, c, s, cnt) in UNIT_STATE:
        L.append(f"                DEFB {t}, {c}, {s}")
        L.append(f"                DEFW {cnt}")
    L.append("")
    L.append(f"BATTLE_RAMG_BASE     EQU #{BATTLE_RAMG_BASE:06X}")
    L.append(f"BATTLE_PAYLOAD_BYTES EQU {pak['payload_bytes']}")
    L.append(f"BATTLE_PAYLOAD_SECTORS EQU {pak['payload_sectors']}")
    L.append(f"BATTLE_BODY_SECTOR   EQU {pak['body_start_sector']}")
    L.append('BattlePakName:       DEFB "HMM2BATL.PAK", 0')
    L.append("")
    L.append("                endif")
    BATTLE_INC.write_text("\n".join(L), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="HMM2BATL.PAK — экран боя (стрим-PAK).")
    ap.add_argument("--preview", type=Path, default=None, help="PNG-реконструкция поля для сверки")
    args = ap.parse_args()

    agg, ent = read_agg_index_with_expansion(AGG_PATH)
    palette = read_palette(agg_entry(agg, ent, "KB.PAL"))
    img = load_battle(palette)

    if args.preview:
        from PIL import Image
        im = Image.new("RGB", (BATTLE_W, BATTLE_H))
        px = im.load()
        for y in range(BATTLE_H):
            for x in range(BATTLE_W):
                px[x, y] = palette[img[y * BATTLE_W + x]]
        im.save(args.preview)
        print(f"preview: {args.preview}")
        return 0

    units = load_units(agg, ent)
    (payload, pal_addr, unit_pal_addr, shadow_pal_addr, shadow_addr, contour_pal_addr,
     status_pal_addr, status_msgs, turn_msgs, win_dlg, top_addr, bot_addr, unit_addrs, evt,
     yellow_pal_addr, win_texts, count_digits, casualties) = build_payload(palette, img, units, agg, ent)
    summary = build_pak(
        [{"type": TYPE_RAMG_BLOB, "target": BATTLE_RAMG_BASE, "data": bytes(payload)}],
        BATTLE_PAK_PATH,
    )
    pak = {
        "payload_bytes": len(payload),
        "payload_sectors": (len(payload) + SECTOR - 1) // SECTOR,
        "body_start_sector": summary["body_start_sector"],
    }
    emit_inc(pal_addr, unit_pal_addr, shadow_pal_addr, shadow_addr, contour_pal_addr,
             status_pal_addr, status_msgs, turn_msgs, win_dlg, top_addr, bot_addr, unit_addrs, evt,
             yellow_pal_addr, win_texts, count_digits, casualties, units, pak)
    print(f"battle pack -> {BATTLE_PAK_PATH.name}: payload={len(payload)} байт "
          f"({pak['payload_sectors']} сект), PAK={summary['total_bytes']} байт")
    print(f"  inc: {BATTLE_INC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
