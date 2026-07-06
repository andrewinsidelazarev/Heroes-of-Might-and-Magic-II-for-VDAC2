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

# Боевые юниты — ДИНАМИЧЕСКИЕ: спрайты в RAM_G (отдельно от фона), Render_Battle рисует по
# таблице состояния. ★АНИМАЦИЯ ПО ОРИГИНАЛУ (BIN <MON>_FRM.BIN, парсинг = fheroes2 bin_info.cpp):
# кадры ТРИМЛЕНЫ по факт. bbox (полные faithful-наборы 280К < прежних прорежённых паддед 415К),
# per-кадр запись (addrN, addrR, w, h, size, ox/oy в 1/16 суперпикселей) + таблицы
# последовательностей per (тип, группа). Позиция кадра = anchor клетки (центр-X, низ+cellYOffset)
# + кадровые ox/oy (GetTroopPosition, battle_interface.cpp:502; reflect: x=cx−w−ox+1).
# ТАЙМИНГИ (дефолт BattleSpeed=4 → как в BIN): общий тик 120мс=6 кадров@48.83Гц;
# движение moveSpeed/8 (465/8≈58мс=3к); стрельба shootSpeed/len (850/7≈121мс=6к);
# idle: STATIC + раз в idleDelay×(75..125%) один вариант по priorities.
UNIT_TYPES = [("PEASANT.ICN", 1), ("ARCHER.ICN", 1)]   # 0=Peasant, 1=Archer
UNIT_BIN = ["PEAS_FRM.BIN", "ARCHRFRM.BIN"]
BIN_ANIM_NAMES = ["MOVE_START", "MOVE_TILE_START", "MOVE_MAIN", "MOVE_TILE_END", "MOVE_STOP",
                  "MOVE_ONE", "TEMPORARY", "STATIC", "IDLE1", "IDLE2", "IDLE3", "IDLE4", "IDLE5",
                  "DEATH", "WINCE_UP", "WINCE_END", "ATTACK1", "ATTACK1_END", "DOUBLEHEX1",
                  "DOUBLEHEX1_END", "ATTACK2", "ATTACK2_END", "DOUBLEHEX2", "DOUBLEHEX2_END",
                  "ATTACK3", "ATTACK3_END", "DOUBLEHEX3", "DOUBLEHEX3_END",
                  "SHOOT1", "SHOOT1_END", "SHOOT2", "SHOOT2_END", "SHOOT3", "SHOOT3_END"]
FRAME_MS = 1000.0 / 48.828            # кадр TS-Config ≈ 20.48мс
BATTLE_FRAME_DELAY_MS = 120           # game_delays.cpp:114 (idle/атака/смерть/wince кадр)
CELL_Y_OFFSET = -9                    # battle_interface.cpp:91


def parse_frm_bin(data):
    """BIN → dict групп (bin_info.cpp:236: count@243+idx, кадры@277+idx*16) + тайминги/приоритеты."""
    import struct as _s
    seqs = {}
    for idx, name in enumerate(BIN_ANIM_NAMES):
        cnt = data[243 + idx]
        if 0 < cnt <= 16:
            seqs[name] = [data[277 + idx * 16 + f] for f in range(cnt)]
    idle_n = min(data[117], 5)
    return {
        "seqs": seqs,
        "idle_n": idle_n,
        "idle_priorities": [_s.unpack_from("<f", data, 118 + i * 4)[0] for i in range(idle_n)],
        "idle_delay_ms": _s.unpack_from("<I", data, 158)[0],
        "move_ms": _s.unpack_from("<I", data, 162)[0],
        "shoot_ms": _s.unpack_from("<I", data, 166)[0],
    }


# Группы, используемые нашим аниматором (компромисс: атака/выстрел — ЦЕНТР-угол ATTACK2/SHOOT2;
# верх/низ по углу цели — с расширением RAM_G). Порядок = коды групп для Z80.
ANIM_GROUPS = ["STATIC", "IDLE1", "IDLE2", "IDLE3", "MOVE_MAIN",
               "ATTACK2", "ATTACK2_END", "SHOOT2", "SHOOT2_END",
               "DEATH", "WINCE_UP", "WINCE_END"]
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


def _crop_icn_frame(agg, ent, name, fr, put):
    """ICN-кадр с кропом (2,0,w−2,h−1) — как fheroes2 agg_image.cpp:1198 для малых кнопок
    (срезает запечённую тень). Возврат (addr, w, h) через put()."""
    h, e = read_icn(agg_entry(agg, ent, name))[fr]
    idx = decode_icn_indices(h, e)
    w, hh = h["w"], h["h"]
    cw, ch = w - 2, hh - 1
    out = bytearray(cw * ch)
    for y in range(ch):
        out[y * cw:(y + 1) * cw] = idx[y * w + 2:y * w + 2 + cw]
    return (put(bytes(out)), cw, ch)


def load_units(agg, ent):
    # ★ПО ОРИГИНАЛУ: тримленные кадры (свой bbox из ICN — ox/oy = якорные смещения fheroes2)
    # + зеркала + BIN-последовательности групп + тайминги. Возврат: список per ТИП:
    #   {order: [icnIdx...], slot: {icn→номер}, frames: {icn: (blobN, blobR, w, h, ox, oy)},
    #    seqs: {группа: [icnIdx...]}, info: тайминги BIN}
    out = []
    for ti, (name, _stand) in enumerate(UNIT_TYPES):
        icn = read_icn(agg_entry(agg, ent, name))
        info = parse_frm_bin(agg_entry(agg, ent, UNIT_BIN[ti]))
        seqs = {g: info["seqs"][g] for g in ANIM_GROUPS if g in info["seqs"]}
        order = sorted({f for s in seqs.values() for f in s})
        frames = {}
        for fr in order:
            h, e = icn[fr]
            blob = bytes(decode_icn_indices(h, e))
            w, hh = h["w"], h["h"]
            m = bytearray(w * hh)                                  # зеркало (горизонт. флип)
            for y in range(hh):
                row = blob[y * w:(y + 1) * w]
                m[y * w:(y + 1) * w] = row[::-1]
            frames[fr] = (blob, bytes(m), w, hh, h.get("ox", 0), h.get("oy", 0))
        out.append({"order": order, "slot": {f: i for i, f in enumerate(order)},
                    "frames": frames, "seqs": seqs, "info": info})
    return out


# Статус-сообщения нижней панели — РЕАЛЬНЫЕ строки fheroes2 (battle_interface.cpp:2889/2914/2928/3009):
# подсказка по наведению. %{monster} = имя отряда (Peasant/Archer plural). BattleStatusMsg (1-based):
# 1=Move Peasants here, 2=Move Archers here, 3=Attack Peasants, 4=Attack Archers,
# 5=Shoot Peasants (...shots), 6=Shoot Archers (...shots), 7=View Peasants info, 8=View Archers info.
# msg=0 → "Turn N" (рендерится "Turn "+номер раунда).
# Shoot: оригинал append " (%{count} shots left)"; в нашей безгеройной модели shots Archer=12 фикс
# (не вычитается → аппаратно-упрощённая модель), поэтому строка статична "(12 shots left)".
# View: оригинал GetMultiName() (plural) + "View %{monster} info" (battle_interface.cpp:2889).
# Shoot-подсказка — СОСТАВНАЯ с живым остатком выстрелов (ориг.: «Shoot X (%{count} shots left)»,
# «(1 shot left)» в единственном): head[type] + число (evt-цифры) + tail. Слоты 5/6 в
# STATUS_MESSAGES — заглушки (индексация 1..8 сохраняется, ASM рисует Shoot своей веткой).
# 9..11 — hover-подсказки КНОПОК панели (ориг. battle_interface.cpp:3277/3290/3304).
STATUS_MESSAGES = ["Move Peasants here", "Move Archers here",
                   "Attack Peasants", "Attack Archers",
                   "Shoot", "Shoot",
                   "View Peasants info", "View Archers info",
                   "Automatic combat modes", "Customize system options", "Skip this unit"]
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
    Один PALETTED-спрайт глоб.палитры (всё непрозрачно). Рамка — faithful render_standard_window
    (dithering-переходы бордюр↔фон, точно по ui_window.cpp). Аппаратная уступка: статичный кадр
    вместо looped-анимации; внешняя тень — глобальная рантайм-процедура Render_WindowShadowDL."""
    from standard_window import render_standard_window
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
    # ★Рамка окна = faithful StandardWindow (dithering-переходы, углы/бордюры/фон точно по
    # ui_window.cpp render()). Возвращает paletted-буфер _windowArea; контент рисуем поверх @ (16,16).
    _fb, CW, CH, _bo = render_standard_window(agg, ent, activeW, activeH, True)
    cv = bytearray(_fb)
    # регион анимации WINLOSE[0]{43,32,231,133} + кадр WINCMBT/CMBTLOS
    V, VW, VH, _, _ = spr("WINLOSE.ICN")
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


# --- ПКМ-попап инфо отряда (Dialog::ArmyInfo, dialog_armyinfo.cpp:516, flags=ZERO) ---
# Жёлтый шрифт fheroes2 = CopyICNWithPalette(FONT, PAL::YELLOW_FONT) = индекс-ремап yellowTextTable
# (engine/pal.cpp:31): глиф-индексы 10..36 → жёлтые оттенки KB.PAL 114..130.
YELLOW_TEXT_TABLE = {
    10: 114, 11: 115, 12: 115, 13: 116, 14: 117, 15: 117, 16: 118, 17: 119, 18: 119,
    19: 120, 20: 121, 21: 121, 22: 122, 23: 123, 24: 123, 25: 124, 26: 125, 27: 125,
    28: 126, 29: 127, 30: 127, 31: 128, 32: 129, 33: 129, 34: 130, 35: 130, 36: 130,
}
AI_SPEED_STR = ["Standing", "Crawling", "Very Slow", "Slow", "Average", "Fast",
                "Very Fast", "Ultra Fast", "Blazing", "Instant"]     # Speed::String (speed.cpp:84)
AI_NAMES = ["Peasants", "Archers"]   # Troop::GetName=GetPluralName(count); ед.число при count==1 —
                                     # отклонение (имя запечено; TODO при свободном RAM_G)
AI_STATS = {0: dict(atk=1, dfn=1, dmin=1, dmax=1, hp=1, spd=2, shots=0),      # из monster_info.cpp
            1: dict(atk=5, dfn=3, dmin=2, dmax=3, hp=10, spd=2, shots=12)}


def compose_armyinfo(agg, ent, unit_type):
    """Попап ПКМ-инфо отряда: ГОТОВЫЙ спрайт VIEWARMY[0] + имя (normalYellow, ремап) + статы
    (DrawMonsterStats @ (x+400,y+37): лейбл право-выровнен к x+397, ':' на x+397, значение от
    x+406, шаг 16, normalWhite=глифы FONT.ICN как есть) + описания способностей (у Peasant/Archer
    пусты). ДИНАМИКУ (Count в боксе 80/223/125×23, Hit Points Left, Shots Left) и спрайт монстра
    (атлас юнитов боя, reflect по стороне) рисует РАНТАЙМ. Возврат (buf, W, H, hpl_y, shots_y)."""
    h, e = read_icn(agg_entry(agg, ent, "VIEWARMY.ICN"))[0]
    W, H = h["w"], h["h"]
    cv = bytearray(decode_icn_indices(h, e))
    st = AI_STATS[unit_type]
    fnt = read_icn(agg_entry(agg, ent, "FONT.ICN"))
    fsm = read_icn(agg_entry(agg, ent, "SMALFONT.ICN"))
    SPACE_W = {"FONT.ICN": 6, "SMALFONT.ICN": 4}

    def glyphs_w(f, fname, text):
        return sum(SPACE_W[fname] if c == " " else f[ord(c) - 32][0]["w"] for c in text)

    def draw(f, fname, text, x, y, remap=None):
        """Faithful-блит глифов ИНДЕКСАМИ (не одноцветно): белый = как есть, жёлтый = remap."""
        cx = x
        for c in text:
            if c == " ":
                cx += SPACE_W[fname]
                continue
            gh, ge = f[ord(c) - 32]
            gi = decode_icn_indices(gh, ge)
            gw, gy, goy = gh["w"], gh["h"], gh.get("oy", 0)
            for yy in range(gy):
                py = y + goy + yy
                if not (0 <= py < H):
                    continue
                for xx in range(gw):
                    v = gi[yy * gw + xx]
                    if v == TRANSPARENT:
                        continue
                    if remap is not None:
                        v = remap.get(v, v)
                    if 0 <= cx + xx < W:
                        cv[py * W + cx + xx] = v
            cx += gw
        return cx

    # имя: normalYellow @ (29 + (227−w)/2, 37+2)
    name = AI_NAMES[unit_type]
    nw = glyphs_w(fnt, "FONT.ICN", name)
    draw(fnt, "FONT.ICN", name, 29 + (227 - nw) // 2, 37 + 2, remap=YELLOW_TEXT_TABLE)
    # статы (DrawMonsterStats @ dst=(400,37)): колонки эталона
    dstX, dstY = 400, 37
    right_x = dstX - 3                    # ':' и правый край лейбла
    left_x = dstX + 6                     # значения
    y = dstY + 2
    hpl_y = shots_y = 0xFF

    def stat_row(label, value, yrow, dynamic=False):
        draw(fnt, "FONT.ICN", ":", right_x, yrow)
        lw = glyphs_w(fnt, "FONT.ICN", label)
        draw(fnt, "FONT.ICN", label, max(right_x - lw, dstX - 123), yrow)
        if not dynamic:
            draw(fnt, "FONT.ICN", value, left_x, yrow)

    stat_row("Attack Skill", str(st["atk"]), y);              y += 16
    stat_row("Defense Skill", str(st["dfn"]), y);             y += 16
    if st["shots"] > 0:
        stat_row("Shots Left", "", y, dynamic=True)           # значение — рантайм (трекинг шотов)
        shots_y = y;                                          y += 16
    dmg = str(st["dmin"]) if st["dmin"] == st["dmax"] else f"{st['dmin']}-{st['dmax']}"
    stat_row("Damage", dmg, y);                               y += 16
    stat_row("Hit Points", str(st["hp"]), y);                 y += 16
    stat_row("Hit Points Left", "", y, dynamic=True)          # в бою count>0 всегда; значение — рантайм
    hpl_y = y;                                                y += 16
    stat_row("Speed", AI_SPEED_STR[st["spd"]], y);            y += 16
    stat_row("Morale", "Normal", y);                          y += 16   # без героя мораль/удача Normal
    stat_row("Luck", "Normal", y)
    # описания способностей (getMonsterPropertiesDescription): у Peasant/Archer abilities пусты →
    # блок пуст (для будущих типов — smallWhite @ (37,185), 3 строки по 210px).
    return bytes(cv), W, H, hpl_y, shots_y


H2D_PATH = ROOT.parent / "OpenHMM2" / "files" / "data" / "resurrection.h2d"


def _read_h2d_image(name):
    """Мини-ридер fheroes2 resurrection.h2d (h2d_file.cpp): магия H2D\\x02 + count, записи
    (offset,size,LE32-длина имени,имя); файл = zlib; image = LE32 w,h,x,y + isSingleLayer +
    индексы KB.PAL [+ transform-слой: 0=пиксель, иначе прозрачный]."""
    import struct as _s
    import zlib as _z
    data = H2D_PATH.read_bytes()
    assert data[:4] == b"H2D\x02", "не resurrection.h2d v2"
    (count,) = _s.unpack_from("<I", data, 4)
    pos = 8
    for _ in range(count):
        off, size, nlen = _s.unpack_from("<III", data, pos)
        pos += 12
        nm = data[pos:pos + nlen].decode()
        pos += nlen
        if nm == name:
            raw = _z.decompress(data[off:off + size])
            w, h, _x, _y = _s.unpack_from("<iiii", raw, 0)
            single = raw[16] != 0
            pix = bytes(raw[17:17 + w * h])
            if not single:
                tr = raw[17 + w * h:17 + 2 * w * h]
                pix = bytes(p if t == 0 else TRANSPARENT for p, t in zip(pix, tr))
            return pix, w, h
    raise KeyError(name)


def compose_battle_settings(agg, ent):
    """Окно настроек боя (openBattleOptionDialog, battle_dialogs.cpp:260): StandardWindow
    289×272 + 5 опций (ui_option_item drawOption: иконка 65×65, титул smallWhite над иконкой
    (y−12, поле 87 c переносом и подъёмом строк), значение под (y+65+6)) + OKAY BOTTOM_CENTER
    {0,5}. Ряд1 (y=31): Speed CSPANEL[0] @x20, Interface SPANEL[16] @x112, Auto Spell Casting
    CSPANEL[6] @x204; ряд2 (y=141): Audio SPANEL[1] @x53, Hot Keys hotkeys_icon (h2d) @x171.
    ДИНАМИКА рантайм: иконка Speed (вбейкан кадр 0; кадры 1/2 поверх на bg-подложке), строка
    «Speed: N» (маски ×1.6), OKAY pressed. Отступления: тени иконок (addGradientShadow)
    опущены; Auto Spell Casting = Off статично (спеллов в порте нет); подменю Interface/
    Audio/Hot Keys не открываются (Audio/HotKeys — новоделы fheroes2, у нас нечего настраивать).
    Возврат (buf, CW, CH, meta)."""
    from standard_window import render_standard_window
    fb, CW, CH, _bo = render_standard_window(agg, ent, 289, 272, True)
    cv = bytearray(fb)
    fsm = read_icn(agg_entry(agg, ent, "SMALFONT.ICN"))
    SPACE = 4

    def s_tw(t):
        return sum(SPACE if c == " " else fsm[ord(c) - 32][0]["w"] for c in t)

    def draw_str(t, x, y):
        cx = x
        for c in t:
            if c == " ":
                cx += SPACE
                continue
            gh, ge = fsm[ord(c) - 32]
            gi = decode_icn_indices(gh, ge)
            gw, gg, goy = gh["w"], gh["h"], gh.get("oy", 0)
            for yy in range(gg):
                py = y + goy + yy
                if not (0 <= py < CH):
                    continue
                for xx in range(gw):
                    v = gi[yy * gw + xx]
                    if v != TRANSPARENT and 0 <= cx + xx < CW:
                        cv[py * CW + cx + xx] = v
            cx += gw

    def draw_field(t, cx_center, y_last, field=87):
        """Перенос по словам в поле field px, построчный центр; последняя строка на y_last
        (title.height()−title.height(maxWidth) подъёмом, lineH=11)."""
        words, lines, cur = t.split(" "), [], ""
        for wd in words:
            cand = wd if not cur else cur + " " + wd
            if not cur or s_tw(cand) <= field:
                cur = cand
            else:
                lines.append(cur)
                cur = wd
        lines.append(cur)
        y0 = y_last - (len(lines) - 1) * 11
        for i, ln in enumerate(lines):
            draw_str(ln, cx_center - s_tw(ln) // 2, y0 + i * 11)

    def spr(name, fr):
        h, e = read_icn(agg_entry(agg, ent, name))[fr]
        return decode_icn_indices(h, e), h["w"], h["h"]

    def blit(src, sw, sh, dx, dy):
        for yy in range(sh):
            for xx in range(sw):
                v = src[yy * sw + xx]
                if v != TRANSPARENT:
                    cv[(dy + yy) * CW + dx + xx] = v

    def grab(dx, dy, gw, gh):
        return bytes(cv[(dy + yy) * CW + dx + xx] for yy in range(gh) for xx in range(gw))

    OPTS = [(20, 31, "CSPANEL.ICN", 0, "Speed", None),           # value «Speed: N» — рантайм
            (112, 31, "SPANEL.ICN", 16, "Interface", "Settings"),
            (204, 31, "CSPANEL.ICN", 6, "Auto Spell Casting", "Off"),
            (53, 141, "SPANEL.ICN", 1, "Audio", "Settings"),
            (171, 141, None, 0, "Hot Keys", "Configure")]        # иконка из h2d
    speed_bg = None
    for ox, oy, icn, fr, title, value in OPTS:
        bx, by = 16 + ox, 16 + oy
        if icn is None:
            ic, iw, ih = _read_h2d_image("hotkeys_icon.image")
        else:
            ic, iw, ih = spr(icn, fr)
        if title == "Speed":
            speed_bg = grab(bx, by, 65, 65)     # подложка под рантайм-иконки CSPANEL[1]/[2]
        blit(ic, iw, ih, bx, by)
        cxc = bx + 32
        draw_field(title, cxc, by - 12)
        if value is not None:
            draw_field(value, cxc, by + 65 + 6)
    ok, okw, okh = spr("SYSTEM.ICN", 1)          # BUTTON_SMALL_OKAY_GOOD → ориг. SYSTEM OKAY
    okx, oky = 16 + (289 - okw) // 2, 16 + 272 - okh - 5
    okay_bg = grab(okx, oky, okw, okh)           # подложка под pressed-кадр
    blit(ok, okw, okh, okx, oky)
    meta = {"speed_icon": (36, 47), "speed_bg": speed_bg,
            "okay": (okx, oky, okw, okh), "okay_bg": okay_bg,
            "speed_val_c": 36 + 32, "speed_val_y": 47 + 65 + 6}
    return bytes(cv), CW, CH, meta


def build_payload(palette, img, units, agg, ent):
    payload = bytearray()

    def put(raw: bytes) -> int:
        addr = BATTLE_RAMG_BASE + align(len(payload), 4)
        while BATTLE_RAMG_BASE + len(payload) < addr:
            payload.append(0)
        payload.extend(raw)
        return addr

    def put_sector(raw: bytes) -> int:
        """Выровнять на 512 = границу СЕКТОРА PAK (payload-entry сама на границе сектора) —
        кусок можно РЕстримить по сектору: sec = body_start + (addr−BASE)//512 (попап↔финал)."""
        addr = BATTLE_RAMG_BASE + align(len(payload), SECTOR)
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
    # Hover-подсказки — ЕДИНЫЙ шрифт статус-бара по оригиналу (battle_interface.cpp:1149/1158:
    # ОБЕ строки normalWhite = FONT.ICN) → FONT ×1.6 гладко, как строка событий. RAM_G позволяет
    # после тримленного атласа юнитов (−135КБ).
    status_msgs = []                              # 8 hover-подсказок (Move/Attack/Shoot/View X)
    for text in STATUS_MESSAGES:
        m, w, h = render_text_mask(agg, ent, text)
        status_msgs.append((put(m), w, h))
    turn_msgs = []                                # «Turn N» убран (battle-no-turn-n-label) — пусто
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
        # --- СТРОКА ДВИЖЕНИЯ (fheroes2 RedrawActionMove, battle_interface.cpp:4448):
        #     «Moved %{monster}: from [%{src}] to [%{dst}].» где src/dst = «row+1, col+1».
        #     ЕДИНЫЙ шрифт статус-бара (normalWhite=FONT ×1.6, как события) — RAM_G позволяет
        #     после тримленного атласа юнитов. Дробим на узкие фрагменты (<255px). ---
        "mvhead": bake("Moved "),
        "mvname": [bake(t) for t in ("Peasants: ", "Archers: ")],
        "mvfrom": bake("from ["),
        "mvmid": bake("] to ["),
        "mvend": bake("]."),
        "comma": bake(", "),
        "ndigit": [bake(str(d)) for d in range(10)],   # цифры координат движения (тот же шрифт)
        # Shoot-hover: «Shoot X (» + N + « shot(s) left)» (живой _shotsLeft, ориг. GetBattleCursor)
        "sh_head": [bake(t) for t in ("Shoot Peasants (", "Shoot Archers (")],
        "sh_tail_pl": bake(" shots left)"),
        "sh_tail_sg": bake(" shot left)"),
        # Кнопка EXIT модального ArmyInfo (ЛКМ-вариант, Dialog::BUTTONS): VIEWARMY[3]=отжата,
        # [4]=нажата; кроп (2,0,w−2,h−1) как agg_image.cpp:1198 (своя тень не нужна — окно с тенью)
        "ai_exit": [_crop_icn_frame(agg, ent, "VIEWARMY.ICN", fr, put) for fr in (3, 4)],
    }
    wdlg, wdw, wdh, wtexts, cas_atk_ly, cas_def_ly = compose_win_dialog(agg, ent)  # окно итога БЕЗ текста
    win_dlg = (put_sector(wdlg), wdw, wdh)    # НА ГРАНИЦЕ СЕКТОРА: область делится с ПКМ-попапом
                                              # ArmyInfo (попап стримится сюда, финал РЕстримится)
    # Цифры для ДИНАМИКИ попапа ArmyInfo (Count/Hit Points Left/Shots Left): FONT.ICN ×1.6
    # ГЛАДКО (антиалиас-маска, как статус-тексты) — рисуются со status_pal (белая с альфой),
    # transform 256. Статика попапа запечена в композит (растёт с окном согласованно).
    ai_digits = []
    for dd in range(10):
        m_, w_, h_ = render_text_mask(agg, ent, str(dd))     # дефолт: FONT.ICN, TEXT_SCALE=1.6
        ai_digits.append((put(m_), w_, h_))
    # --- Динамика окна НАСТРОЕК боя (композит окна — отдельная PAK-entry, см. main):
    #     иконки Speed CSPANEL[1]/[2] на bg-подложке (прозрачные пиксели кадра показывают фон
    #     окна — как restore→drawOptions в оригинале), OKAY pressed на подложке,
    #     строки «Speed: N» (SMALFONT ×1.6 антиалиас, рисуются status_pal) ---
    set_buf, set_w, set_h, set_meta = compose_battle_settings(agg, ent)
    csp = read_icn(agg_entry(agg, ent, "CSPANEL.ICN"))
    set_icons = []
    for fr in (1, 2):
        ih_, ie_ = csp[fr]
        pix = decode_icn_indices(ih_, ie_)
        iw_, ihh_ = ih_["w"], ih_["h"]
        cnv = bytearray(set_meta["speed_bg"])                # 65×65 фон под иконкой
        for yy in range(min(65, ihh_)):
            for xx in range(min(65, iw_)):
                v = pix[yy * iw_ + xx]
                if v != TRANSPARENT:
                    cnv[yy * 65 + xx] = v
        set_icons.append((put(bytes(cnv)), 65, 65))
    okh_, oke_ = read_icn(agg_entry(agg, ent, "SYSTEM.ICN"))[2]
    okp = decode_icn_indices(okh_, oke_)
    okw_, okhh_ = okh_["w"], okh_["h"]
    _, _, mow, moh = set_meta["okay"]
    cnv = bytearray(set_meta["okay_bg"])                     # подложка под pressed
    for yy in range(min(moh, okhh_)):
        for xx in range(min(mow, okw_)):
            v = okp[yy * okw_ + xx]
            if v != TRANSPARENT:
                cnv[yy * mow + xx] = v
    set_okay1 = (put(bytes(cnv)), mow, moh)
    set_vals = []
    for n in range(1, 11):
        m_, w_, h_ = render_text_mask(agg, ent, f"Speed: {n}", font="SMALFONT.ICN")
        set_vals.append((put(m_), w_, h_))
    set_dyn = {"icons": set_icons, "okay1": set_okay1, "vals": set_vals,
               "buf": set_buf, "W": set_w, "H": set_h, "meta": set_meta}
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
    # Стрела лучника (faithful ICN::ARCH_MSL[4] = горизонтальный снаряд; RedrawMissileAnimation).
    # Пред-масштаб ×1.6 NEAREST (как поле/юниты), палитра ЮНИТОВ. Нормаль (выстрел вправо) + зеркало (влево).
    from PIL import Image as _Img
    _amh, _ame = read_icn(agg_entry(agg, ent, "ARCH_MSL.ICN"))[4]
    _abase = _Img.frombytes("L", (_amh["w"], _amh["h"]), bytes(decode_icn_indices(_amh, _ame)))
    _asw, _ash = round(_amh["w"] * 1.6), round(_amh["h"] * 1.6)
    _ascaled = _abase.resize((_asw, _ash), _Img.NEAREST)
    arrow_sprites = [(put(_ascaled.tobytes()), _asw, _ash),
                     (put(_ascaled.transpose(_Img.FLIP_LEFT_RIGHT).tobytes()), _asw, _ash)]
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
    casualties = (casualty_icons, none_sprite, cas_atk_vy, cas_def_vy, arrow_sprites)
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
    # Тримленные кадры юнитов: per тип, per кадр (по order) — normal + mirror подряд.
    # unit_addrs[type][slot] = (addrN, addrR).
    unit_addrs = []
    for u in units:
        rows = []
        for fr in u["order"]:
            blob, mblob, _w, _h, _ox, _oy = u["frames"][fr]
            rows.append((put(blob), put(mblob)))
        unit_addrs.append(rows)
    return (payload, pal_addr, unit_pal_addr, shadow_pal_addr, shadow_addr, contour_pal_addr,
            status_pal_addr, status_msgs, turn_msgs, win_dlg, top_addr, bot_addr, unit_addrs, evt,
            yellow_pal_addr, win_texts, count_digits, casualties, ai_digits, set_dyn)


def emit_inc(pal_addr, unit_pal_addr, shadow_pal_addr, shadow_addr, contour_pal_addr,
             status_pal_addr, status_msgs, turn_msgs, win_dlg, top_addr, bot_addr, unit_addrs, evt,
             yellow_pal_addr, win_texts, count_digits, casualties, units, pak, ai, set_dyn):
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
    # --- СТАТУС-СООБЩЕНИЯ панели (как fheroes2): ОБЕ строки normalWhite (FONT ×1.6 гладко,
    #     нативный блит). Hover — НИЖНЯЯ строка бара (TEXTBAR9 @463); события — верхняя (448).
    #     BattleStatusMsg (1-based) → Pre[idx] (SOURCE/LAYOUT/SIZE) + Vert[idx]. ---
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
    L.append("BattleStatusVertTab:                   ; hover = НИЖНЯЯ строка бара (лог.Y≈465), центр X=512")
    for (addr, w, h) in status_msgs:
        lx = 512 - w // 2                            # физ-центр 320×1.6=512, минус полуширина маски
        L.append(f"                FT_VERTEX2F {lx * 16}, {465 * 256 // 10}")
    L.append(f"BATTLE_STATUS_COUNT EQU {len(status_msgs)}")
    L.append("")
    # («Turn N» УБРАН по правилу battle-no-turn-n-label: игрок в оригинале его в статус-баре
    #  НЕ видит — только события боя и hover-подсказки; msg==0 → пустая строка.)
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
    # --- ФРАГМЕНТЫ СТРОКИ ДВИЖЕНИЯ (Battle_RenderMoveLine): «Moved <m>: from [r, c] to [r, c].». ---
    L.append("BattleEvtMoveHead:                     ; «Moved »")
    L.append(ee(evt["mvhead"]))
    L.append("BattleEvtMoveNameTab:                  ; «Peasants: »/«Archers: » idx=type")
    for e in evt["mvname"]:
        L.append(ee(e))
    L.append("BattleEvtMoveFrom:                     ; «from [»")
    L.append(ee(evt["mvfrom"]))
    L.append("BattleEvtMoveMid:                      ; «] to [»")
    L.append(ee(evt["mvmid"]))
    L.append("BattleEvtMoveEnd:                      ; «].»")
    L.append(ee(evt["mvend"]))
    L.append("BattleEvtComma:                        ; «, » (между row и col)")
    L.append(ee(evt["comma"]))
    L.append("BattleEvtMoveDigitTab:                 ; нативные цифры «0».. «9» для координат движения")
    for e in evt["ndigit"]:
        L.append(ee(e))
    # --- Shoot-hover С ЖИВЫМ остатком (GetBattleCursor: «Shoot X (%{count} shots left)») ---
    L.append("BattleShootHeadTab:                    ; «Shoot Peasants (»/«Shoot Archers (» idx=target.type")
    for e in evt["sh_head"]:
        L.append(ee(e))
    L.append("BattleShootTailPl:                     ; « shots left)»")
    L.append(ee(evt["sh_tail_pl"]))
    L.append("BattleShootTailSg:                     ; « shot left)» (N==1)")
    L.append(ee(evt["sh_tail_sg"]))
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
    # ★FAITHFUL-АНИМАЦИЯ (BIN): тримленные per-кадр DL-фрагменты + смещения от якоря клетки +
    #   последовательности групп + тайминги оригинала (см. шапку файла).
    NG = len(ANIM_GROUPS)
    L.append(f"BATTLE_NGROUPS EQU {NG}")
    for gi, g in enumerate(ANIM_GROUPS):
        L.append(f"BATTLE_GRP_{g} EQU {gi}")
    L.append("BattleFrameSrcTab:                      ; [вариант=type*2+side] → FT_BITMAP_SOURCE ×кадры (4Б)")
    L.append("                DEFW " + ", ".join(
        f"BattleFrameSrc{t}_{s}" for t in range(len(units)) for s in range(2)))
    for t, u in enumerate(units):
        for s in range(2):
            L.append(f"BattleFrameSrc{t}_{s}:")
            for fr in u["order"]:
                addrN, addrR = unit_addrs[t][u["slot"][fr]]
                L.append(f"                FT_BITMAP_SOURCE #{(addrR if s else addrN):06X}   ; ICN {fr}")
    L.append("BattleFrameLayTab:                      ; [тип] → LAYOUT+SIZE ×кадры (8Б; общие для зеркала)")
    L.append("                DEFW " + ", ".join(f"BattleFrameLay{t}" for t in range(len(units))))
    for t, u in enumerate(units):
        L.append(f"BattleFrameLay{t}:")
        for fr in u["order"]:
            _b, _m, w, h, _ox, _oy = u["frames"][fr]
            L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {w}, {h}")
            L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {w * 16 // 10}, {h * 16 // 10}")
    # Смещение кадра от якоря (vertex 1/16 физ.px, знаковое): GetTroopPosition (battle_interface.cpp:502):
    #   x = ox (side0) / 1−w−ox (side1, reflect); y = oy. Якорь = (центр клетки, низ клетки−9).
    # ДАННЫЕ — в GlobalData #91 (вынос: оверлей у потолка); указатели-таблица в оверлее (#91-адреса).
    L.append("BattleFrameOfsTab:                      ; [вариант] → &GD-таблицы (ofsX,ofsY)×кадры в #91")
    L.append("                DEFW " + ", ".join(
        f"GDBattleFrameOfs{t}_{s}" for t in range(len(units)) for s in range(2)))
    frameofs_lines = []
    for t, u in enumerate(units):
        for s in range(2):
            frameofs_lines.append(f"GDBattleFrameOfs{t}_{s}:                ; (ofsX,ofsY) DEFW ×кадры (4Б/кадр)")
            for fr in u["order"]:
                _b, _m, w, h, ox, oy = u["frames"][fr]
                lx = (1 - w - ox) if s else ox
                frameofs_lines.append(f"                DEFW {round(lx * 25.6)}, {round(oy * 25.6)}   ; ICN {fr}")
    # якоря клеток — в GlobalData #91 (вынос: оверлей боя у потолка); доступ Battle_CellAnchorAddr
    anchor_lines = frameofs_lines + [
        "GDBattleCellAnchor:                     ; 99 × (ax,ay) DEFW — якорь спрайта клетки"]
    for idx in range(WIDTH_IN_CELLS * 9):
        row, col = idx // WIDTH_IN_CELLS, idx % WIDTH_IN_CELLS
        px = CELL_OX - (CELL_W // 2 if row % 2 else 0) + CELL_W * col
        py = CELL_OY + ROW_STEP * row
        anchor_lines.append(f"                DEFW {round((px + CELL_W / 2) * 25.6)}, "
                            f"{round((py + CELL_H + CELL_Y_OFFSET) * 25.6)}")
    # Последовательности групп: [type*NGROUPS+грп] → DEFW seq {DEFB len, слоты...}; 0 = группы нет.
    L.append("BattleSeqPtrTab:")
    for t, u in enumerate(units):
        L.append("                DEFW " + ", ".join(
            (f"BattleSeq{t}_{g}" if g in u["seqs"] else "0") for g in ANIM_GROUPS))
    for t, u in enumerate(units):
        for g in ANIM_GROUPS:
            if g in u["seqs"]:
                slots = [u["slot"][f] for f in u["seqs"][g]]
                L.append(f"BattleSeq{t}_{g}: DEFB {len(slots)}, " + ", ".join(map(str, slots)))
    # --- Тайминги (в кадрах @48.83Гц): БАЗА BIN = BattleSpeed 4 (дефолт fheroes2). Per-speed
    #     наборы по Game::ApplyBattleSpeed (game_delays.cpp:224): k(s)=(10−s)/6, s=10 → 1/18;
    #     мс-величина ×k ДО деления на кадры (как ApplyBattleSpeed(...)/animationLength). ---
    def _speed_k(s):
        return (10 - s) / 6.0 if s < 10 else 1.0 / 18.0

    def _timings(k):
        def _ticks(ms):
            return max(1, round(ms * k / FRAME_MS))
        a_t = _ticks(BATTLE_FRAME_DELAY_MS)
        mv_t, sh_t, dd_t, wc_t, at_t = [], [], [], [], []
        for u in units:
            info, seqs = u["info"], u["seqs"]
            mv_t.append(_ticks(info["move_ms"] / max(1, len(seqs["MOVE_MAIN"]))))
            st = _ticks(info["shoot_ms"] / len(seqs["SHOOT2"])) if "SHOOT2" in seqs else a_t
            sh_t.append(st)
            dd_t.append(min(255, len(seqs["DEATH"]) * a_t))
            wu = len(seqs.get("WINCE_UP", [])) * a_t
            wc_t.append((wu, min(255, wu + len(seqs.get("WINCE_END", [])) * a_t)))
            mp = len(seqs["ATTACK2"]) * a_t                   # пик мили = конец ATTACK2 (контакт)
            mtot = mp + len(seqs.get("ATTACK2_END", [])) * a_t
            if "SHOOT2" in seqs:
                sp = len(seqs["SHOOT2"]) * st
                stot = sp + len(seqs.get("SHOOT2_END", [])) * st
            else:
                sp, stot = mp, mtot
            at_t.append((mp, min(255, mtot), sp, min(255, stot)))
        vel = min(255, max(1, round(48 / k)))                 # 48 в-ед/тик @ k=1 → дефолт бит-в-бит
        arrow = min(255, max(1, round(32 * k)))               # полёт стрелы (32 тика @ дефолт)
        return a_t, mv_t, sh_t, dd_t, wc_t, at_t, vel, arrow

    anim_t, move_t, shoot_t, death_d, wince_tim, atk_tim, _dvel, _darw = _timings(1.0)
    idle_min, idle_thr, static_slot, corpse_slot = [], [], [], []
    for t, u in enumerate(units):
        info, seqs = u["info"], u["seqs"]
        idle_min.append(round(info["idle_delay_ms"] * 0.75 / FRAME_MS))   # мин.пауза = 75% delay
        pr = info["idle_priorities"][:3]                      # пороги rand8 выбора idle-варианта
        tot = sum(pr) or 1.0
        acc, thr = 0.0, []
        for p in pr[:-1]:
            acc += p
            thr.append(min(255, round(acc / tot * 256)))
        while len(thr) < 2:
            thr.append(255)
        idle_thr.append((len(pr), thr[0], thr[1]))
        static_slot.append(u["slot"][seqs["STATIC"][0]])
        corpse_slot.append(u["slot"][seqs["DEATH"][-1]])       # труп = последний DEATH-кадр
    L.append("; --- РАБОЧИЕ тик-таблицы: 21 байт ПОДРЯД (layout = набор BattleSpeedSets);")
    L.append(";     Battle_ApplySpeed копирует сюда набор выбранной скорости (LDIR 21) ---")
    L.append(f"BattleAnimTicks:     DEFB {anim_t}          ; BATTLE_FRAME_DELAY (120мс @ speed4)")
    L.append("BattleMoveTickTab:   DEFB " + ", ".join(map(str, move_t)) + "   ; тиков/кадр MOVE_MAIN (moveSpeed/8)")
    L.append("BattleShootTickTab:  DEFB " + ", ".join(map(str, shoot_t)) + "   ; тиков/кадр SHOOT (shootSpeed/len)")
    L.append("BattleDeathTicksTab: DEFB " + ", ".join(map(str, death_d)) + " ; длительность смерти (len(DEATH)×тик)")
    L.append("BattleWinceTimTab:                      ; [type] → DEFB up_тиков, всего_тиков")
    for wu, wt in wince_tim:
        L.append(f"                DEFB {wu}, {wt}")
    L.append("BattleAtkTimTab:                        ; [type] → DEFB мили_пик, мили_всего, выстрел_пик, выстрел_всего")
    for mp, mtot, sp, stot in atk_tim:
        L.append(f"                DEFB {mp}, {mtot}, {sp}, {stot}")
    L.append(f"BattleMoveVel:       DEFB {_dvel}         ; vertex-ед/тик (клетка 44px ≈ 23 тика @ speed4)")
    L.append(f"BattleArrowSteps:    DEFB {_darw}         ; тиков полёта стрелы (шаг = дельта/steps)")
    L.append("BATTLE_SPEED_SET_LEN EQU 21")
    # выносы боя в GlobalData #91 (оверлей боя у потолка 16К); чтение GData_ReadByte
    LS = ["; ==== АВТОГЕНЕРАЦИЯ battle_pack.py — НЕ ПРАВИТЬ (выносы боя в GlobalData #91) ====",
          "; Battle_ApplySpeed копирует набор в рабочий блок BattleAnimTicks..BattleArrowSteps.",
          "GDBattleSpeedSets:                      ; [speed−1] → 21Б (Game::ApplyBattleSpeed k=(10−s)/6, s10=1/18)"]
    for s in range(1, 11):
        a, mv, sh, dd, wc, at, vl, ar = _timings(_speed_k(s))
        row = [a] + mv + sh + dd + [b for p in wc for b in p] + [b for q in at for b in q] + [vl, ar]
        assert len(row) == 21
        LS.append("                DEFB " + ", ".join(map(str, row)) + f"   ; speed {s}")
    LS.extend(anchor_lines)
    (BATTLE_INC.parent / "generated_battle_speed.inc").write_text("\n".join(LS) + "\n", encoding="utf-8")
    L.append("BattleIdleWaitMinTab: DEFW " + ", ".join(map(str, idle_min)) + " ; мин. пауза STATIC (тиков; от speed НЕ зависит — BIN idleDelay)")
    L.append("BATTLE_IDLE_RND_MASK EQU 127            ; пауза = min + (rand8 & mask) ≈ ×(75..125%)")
    L.append("BattleIdleThreshTab:                    ; [type] → DEFB n_вариантов, порог1, порог2 (rand8)")
    for n, t1, t2 in idle_thr:
        L.append(f"                DEFB {n}, {t1}, {t2}")
    L.append("BattleStaticSlotTab: DEFB " + ", ".join(map(str, static_slot)) + "     ; слот кадра стойки")
    L.append("BattleCorpseSlotTab: DEFB " + ", ".join(map(str, corpse_slot)) + "   ; слот трупа (посл. DEATH)")
    L.append("BATTLE_ARROW_YOFS EQU -768              ; стрела на высоте груди (−30 лог.px от якоря-ног)")
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
    cas_icons, none_spr, cas_atk_vy, cas_def_vy, arrow_spr = casualties
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
    L.append("BattleArrowSrcTab:                     ; стрела ARCH_MSL[4] ×1.6 [lo,mid,hi,w,h]; [0]=вправо [1]=влево")
    for (addr, w, h) in arrow_spr:
        L.append(f"                DEFB #{addr & 0xFF:02X}, #{(addr >> 8) & 0xFF:02X}, "
                 f"#{(addr >> 16) & 0xFF:02X}, {w}, {h}")
    # Бар/перо счётчика отряда — СМЕЩЕНИЯ от якоря клетки (BattleCellAnchor), таблицы 99×
    # не нужны (экономия оверлея ~1.2КБ): бар (cx−13, py+36)-(cx+13, py+49); перо = центр, y бара+5.4.
    L.append("BATTLE_CNTBAR_DX  EQU 333               ; 13 лог.px ×25.6 (полуширина бара)")
    L.append("BATTLE_CNTBAR_DY0 EQU -179              ; верх бара = якорьY − 7 лог.px")
    L.append("BATTLE_CNTBAR_DY1 EQU 154               ; низ бара = якорьY + 6 лог.px")
    L.append("BATTLE_CNTPEN_DY  EQU -93               ; перо числа = якорьY − 3.6 лог.px (центр бара)")
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
    # --- ПКМ-попап ArmyInfo (dialog_armyinfo.cpp): стримится в ОБЛАСТЬ ФИНАЛА, финал рестримится ---
    L.append("; ПКМ-попап инфо отряда (Dialog::ArmyInfo): 2 композита по типу в PAK; RAM_G-адрес =")
    L.append("; ОБЛАСТЬ ФИНАЛЬНОГО ОКНА (не живут одновременно; при конце боя финал РЕстримится).")
    aiw, aih = ai["W"], ai["H"]
    L.append(f"ARMYINFO_W           EQU {aiw}")
    L.append(f"ARMYINFO_H           EQU {aih}")
    L.append(f"ARMYINFO_BYTES       EQU {ai['bytes']}")
    L.append(f"ARMYINFO_SECTORS     EQU {ai['sectors']}")
    L.append(f"ArmyInfoSecTab:      DEFW {ai['sec'][0]}, {ai['sec'][1]}   ; сектор попапа по типу (в PAK)")
    L.append(f"WINDLG_SEC           EQU {ai['win_sec']}      ; сектор финала внутри payload (рестрим)")
    L.append(f"WINDLG_SECTORS       EQU {ai['win_sectors']}")
    # позиции ДИНАМИКИ (лог. коорд. внутри окна; экранный X окна = (640−W)/2, Y = (480−H)/2):
    aix, aiy = (640 - aiw) // 2, (480 - aih) // 2
    L.append(f"ARMYINFO_X           EQU {aix}      ; экранное лево окна (лог.640×480)")
    L.append(f"ARMYINFO_Y           EQU {aiy}")
    L.append("; значения статов: value @ x+406; Hit Points Left/Shots Left по типу (#FF=нет строки):")
    L.append(f"ArmyInfoHplYTab:     DEFB {ai['hpl_y'][0]}, {ai['hpl_y'][1]}   ; лок.Y строки Hit Points Left")
    L.append(f"ArmyInfoShotYTab:    DEFB {ai['shots_y'][0] if ai['shots_y'][0] != 0xFF else 255}, "
             f"{ai['shots_y'][1] if ai['shots_y'][1] != 0xFF else 255} ; лок.Y Shots Left (255=нет)")
    L.append("ARMYINFO_VAL_X       EQU 406    ; лок.X значений статов")
    L.append("; бокс счётчика (dialog_armyinfo.cpp:64): (80,223) 125×23, число по центру, normalWhite")
    L.append("ARMYINFO_CNT_X       EQU 80")
    L.append("ARMYINFO_CNT_Y       EQU 223")
    L.append("ARMYINFO_CNT_W       EQU 125")
    L.append("ARMYINFO_CNT_H       EQU 23")
    L.append("; точка ног монстра (x+520/4+16, y+175); спрайт из атласа юнитов, reflect по стороне")
    L.append("ARMYINFO_MON_X       EQU 146")
    L.append("ARMYINFO_MON_Y       EQU 175")
    L.append("; цифры '0'-'9' динамики: антиалиас-маски FONT ×1.6 (рисовать со status_pal, transform 256):")
    L.append("ArmyInfoDigitTab:                     ; 5 байт: addr24, w, h")
    for (a_, w_, h_) in ai["digits"]:
        L.append(f"                DEFB #{a_ & 0xFF:02X}, #{(a_ >> 8) & 0xFF:02X}, #{(a_ >> 16) & 0xFF:02X}, {w_}, {h_}")
    dig_h = ai["digits"][0][2]
    # --- DL-фрагмент окна попапа (палитра юнитов idx0-прозр.; W×1.6=882>511 → SIZE_H;
    #     сброс SIZE_H в конце — ловушка &511-маски для следующих битмапов) ---
    sw16, sh16 = aiw * 16 // 10, aih * 16 // 10
    L.append("Battle_ArmyInfo_DL:")
    L.append("                FT_BITMAP_TRANSFORM_A 160")
    L.append("                FT_BITMAP_TRANSFORM_E 160")
    L.append("                FT_PALETTE_SOURCE BATTLE_UNIT_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("                FT_BITMAP_SOURCE BATTLE_WIN_DLG_RAMG")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {aiw}, {aih}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {sw16}, {sh16}")
    L.append(f"                FT_BITMAP_SIZE_H {sw16}, {sh16}")   # макрос САМ маскирует &511 / >>9!
    L.append(f"                FT_VERTEX2F {aix * 256 // 10}, {aiy * 256 // 10}")
    L.append("Battle_ArmyInfo_DL_SIZE EQU $ - Battle_ArmyInfo_DL")
    L.append("Battle_ArmyInfo_Post_DL:              ; после окна: сброс SIZE_H (ловушка &511)")
    L.append("                FT_BITMAP_SIZE_H 0, 0")
    L.append("Battle_ArmyInfo_Post_DL_SIZE EQU $ - Battle_ArmyInfo_Post_DL")
    # --- якорь монстра попапа (точка ног (146,175) в окне): вершина = якорь + смещение кадра
    #     стойки (тот же Battle_EmitUnitVertex, что и поле) ---
    L.append("ArmyInfoMonAnchor:                    ; [type] → (ax,ay) DEFW — якорь ног монстра")
    for t in range(len(UNIT_TYPES)):
        L.append(f"                DEFW {round((aix + 146) * 25.6)}, {round((aiy + 175) * 25.6)}")
    # --- Кнопка EXIT МОДАЛЬНОГО ArmyInfo (ЛКМ по своему юниту, Dialog::BUTTONS):
    #     позиция ориг. (dialog_armyinfo.cpp:599): x = W−58−94+18 = 417, y = 221 (лок. окна).
    #     Готовые DL-фрагменты (×1.6 как окно, палитра юнитов уже в прологе окна). ---
    bx, by = aix + 417, aiy + 221
    for i, (ba, bw, bh) in enumerate(evt["ai_exit"]):
        L.append(f"Battle_AIExitBtn{i}_DL:               ; {'нажата' if i else 'отжата'}")
        L.append(f"                FT_BITMAP_SOURCE #{ba:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {bw}, {bh}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {bw * 16 // 10}, {bh * 16 // 10}")
        L.append(f"                FT_VERTEX2F {bx * 256 // 10}, {by * 256 // 10}")
        L.append(f"Battle_AIExitBtn{i}_DL_SIZE EQU $ - Battle_AIExitBtn{i}_DL")
    _bw = evt["ai_exit"][0][1]
    _bh = evt["ai_exit"][0][2]
    L.append(f"AIEXIT_X0            EQU {bx}     ; hit-зона кнопки EXIT (лог. 640×480)")
    L.append(f"AIEXIT_X1            EQU {bx + _bw}")
    L.append(f"AIEXIT_Y0            EQU {by}")
    L.append(f"AIEXIT_Y1            EQU {by + _bh}")
    # --- готовые экранные константы динамики (1/16px супер-экрана 1024): ---
    #     count: центр бокса (aix+80+62, aiy+223+11), «+2» как text.draw в эталоне;
    #     значения статов: лево (aix+406, aiy+hpl_y/shots_y).
    cnt_cx16 = (aix + 80 + 62) * 256 // 10                      # центр по X (вычесть tw×8 в ASM)
    cnt_cy16 = ((aiy + 223 + 11 + 2) * 256 // 10) - dig_h * 8   # верх маски: центрY − h/2 (маска уже ×1.6)
    L.append(f"ARMYINFO_CNT_CX16    EQU {cnt_cx16}   ; центр бокса счётчика ×16 (минус tw×8)")
    L.append(f"ARMYINFO_CNT_Y16     EQU {cnt_cy16}   ; верх цифр счётчика ×16")
    L.append(f"ARMYINFO_VALX16      EQU {(aix + 406) * 256 // 10}  ; лево значений статов ×16")
    hy0 = (aiy + ai['hpl_y'][0]) * 256 // 10
    hy1 = (aiy + ai['hpl_y'][1]) * 256 // 10
    L.append(f"ArmyInfoHplY16Tab:   DEFW {hy0}, {hy1}   ; Y строки Hit Points Left ×16 (по типу)")
    sy0 = (aiy + ai['shots_y'][0]) * 256 // 10 if ai['shots_y'][0] != 0xFF else 0
    sy1 = (aiy + ai['shots_y'][1]) * 256 // 10 if ai['shots_y'][1] != 0xFF else 0
    L.append(f"ArmyInfoShotY16Tab:  DEFW {sy0}, {sy1}   ; Y строки Shots Left ×16 (0=нет строки)")
    # --- ОКНО НАСТРОЕК боя (openBattleOptionDialog): стримится в ОБЛАСТЬ ФИНАЛА по кнопке
    #     Settings панели (TEXTBAR[6] @ (0,461) 49×19); финал рестримится при конце боя.
    #     Рабочий Speed: клик по зоне → speed%10+1 → Battle_ApplySpeed + динамика (иконка/строка). ---
    stw, sth = set_dyn["W"], set_dyn["H"]
    stx, sty = (BATTLE_W - stw) // 2, (BATTLE_H - sth) // 2
    sm = set_dyn["meta"]
    L.append("")
    L.append("; Окно настроек боя (стрим в область финала, как ArmyInfo)")
    L.append(f"SETTINGS_SEC         EQU {set_dyn['sec']}      ; сектор композита окна в PAK")
    L.append(f"SETTINGS_SECTORS     EQU {set_dyn['sectors']}")
    L.append(f"SETTINGS_BYTES       EQU {stw * sth}")
    L.append(f"SETTINGS_X           EQU {stx}      ; экранное лево окна (лог.640×480)")
    L.append(f"SETTINGS_Y           EQU {sty}")
    ssw16, ssh16 = stw * 16 // 10, sth * 16 // 10
    L.append("Battle_Settings_DL:")
    L.append("                FT_BITMAP_TRANSFORM_A 160")
    L.append("                FT_BITMAP_TRANSFORM_E 160")
    L.append("                FT_PALETTE_SOURCE BATTLE_UNIT_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("                FT_BITMAP_SOURCE BATTLE_WIN_DLG_RAMG")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {stw}, {sth}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {ssw16}, {ssh16}")
    L.append(f"                FT_BITMAP_SIZE_H {ssw16}, {ssh16}")
    L.append(f"                FT_VERTEX2F {stx * 256 // 10}, {sty * 256 // 10}")
    L.append("Battle_Settings_DL_SIZE EQU $ - Battle_Settings_DL")
    L.append("Battle_Settings_Post_DL:              ; сброс SIZE_H (ловушка &511)")
    L.append("                FT_BITMAP_SIZE_H 0, 0")
    L.append("Battle_Settings_Post_DL_SIZE EQU $ - Battle_Settings_Post_DL")
    # динамика: иконка Speed (кадры 1/2 на bg-подложке; вбейкан кадр 0 «speed<5»)
    six, siy = stx + sm["speed_icon"][0], sty + sm["speed_icon"][1]
    for i, (ia, iw_, ih_) in enumerate(set_dyn["icons"]):
        L.append(f"Battle_SetSpdIcon{i + 1}_DL:              ; CSPANEL[{i + 1}] (speed {'≥8' if i else '5..7'})")
        L.append(f"                FT_BITMAP_SOURCE #{ia:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {iw_}, {ih_}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {iw_ * 16 // 10}, {ih_ * 16 // 10}")
        L.append(f"                FT_VERTEX2F {six * 256 // 10}, {siy * 256 // 10}")
        L.append(f"Battle_SetSpdIcon{i + 1}_DL_SIZE EQU $ - Battle_SetSpdIcon{i + 1}_DL")
    # OKAY pressed (на подложке; released вбейкан)
    okx, oky, okw_, okh_ = sm["okay"]
    oa, ow_, oh_ = set_dyn["okay1"]
    L.append("Battle_SetOkay1_DL:                   ; OKAY нажата (подложка вбейкана)")
    L.append(f"                FT_BITMAP_SOURCE #{oa:06X}")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {ow_}, {oh_}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {ow_ * 16 // 10}, {oh_ * 16 // 10}")
    L.append(f"                FT_VERTEX2F {(stx + okx) * 256 // 10}, {(sty + oky) * 256 // 10}")
    L.append("Battle_SetOkay1_DL_SIZE EQU $ - Battle_SetOkay1_DL")
    # строки «Speed: N» — маски ×1.6 (рисовать status-прологом: TRANSFORM 256 + STATUS_PAL);
    # вершина X = SETVAL_CX16 − w×8 (центр по иконке Speed), Y фикс.
    L.append("BattleSetValTab:                      ; [speed−1] → адрес24, w, h (маска «Speed: N» ×1.6)")
    for va, vw_, vh_ in set_dyn["vals"]:
        L.append(f"                DEFB #{va & 0xFF:02X}, #{(va >> 8) & 0xFF:02X}, #{va >> 16:02X}, {vw_}, {vh_}")
    L.append(f"SETVAL_CX16          EQU {(stx + sm['speed_val_c']) * 256 // 10}  ; центр строки значения ×16")
    L.append(f"SETVAL_Y16           EQU {(sty + sm['speed_val_y']) * 256 // 10}")
    # клик-зоны (лог. 640×480): кнопка панели, зона Speed-опции, OKAY
    L.append("BTLSET_BTN_X0        EQU 0        ; кнопка Settings панели (TEXTBAR[6] @ 0,461)")
    L.append("BTLSET_BTN_X1        EQU 49")
    L.append("BTLSET_BTN_Y0        EQU 461")
    L.append("BTLSET_BTN_Y1        EQU 480")
    L.append(f"BTLSET_SPEED_X0      EQU {six}    ; зона опции Speed (65×65)")
    L.append(f"BTLSET_SPEED_X1      EQU {six + 65}")
    L.append(f"BTLSET_SPEED_Y0      EQU {siy}")
    L.append(f"BTLSET_SPEED_Y1      EQU {siy + 65}")
    L.append(f"BTLSET_OK_X0         EQU {stx + okx}    ; зона кнопки OKAY")
    L.append(f"BTLSET_OK_X1         EQU {stx + okx + okw_}")
    L.append(f"BTLSET_OK_Y0         EQU {sty + oky}")
    L.append(f"BTLSET_OK_Y1         EQU {sty + oky + okh_}")
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
     yellow_pal_addr, win_texts, count_digits, casualties, ai_digits, set_dyn) = build_payload(palette, img, units, agg, ent)
    # --- ПКМ-попапы ArmyInfo (по типу) — отдельные entries PAK (в RAM_G НЕ живут постоянно:
    #     стримятся в ОБЛАСТЬ ФИНАЛЬНОГО ОКНА по ПКМ; финал рестримится при конце боя) ---
    ai0, aiW, aiH, hpl0, sh0 = compose_armyinfo(agg, ent, 0)
    ai1, aiW1, aiH1, hpl1, sh1 = compose_armyinfo(agg, ent, 1)
    assert (aiW, aiH) == (aiW1, aiH1)
    assert aiW * aiH <= win_dlg[1] * win_dlg[2], \
        f"попап {aiW}x{aiH} больше области финала {win_dlg[1]}x{win_dlg[2]}"
    set_buf = set_dyn["buf"]
    assert set_dyn["W"] * set_dyn["H"] <= win_dlg[1] * win_dlg[2], \
        f"окно настроек {set_dyn['W']}x{set_dyn['H']} больше области финала"
    summary = build_pak(
        [{"type": TYPE_RAMG_BLOB, "target": BATTLE_RAMG_BASE, "data": bytes(payload)},
         {"type": TYPE_RAMG_BLOB, "target": 0, "data": bytes(ai0)},   # target 0: грузим вручную
         {"type": TYPE_RAMG_BLOB, "target": 0, "data": bytes(ai1)},
         {"type": TYPE_RAMG_BLOB, "target": 0, "data": bytes(set_buf)}],  # окно настроек (в обл. финала)
        BATTLE_PAK_PATH,
    )
    body = summary["body_start_sector"]
    pay_secs = (len(payload) + SECTOR - 1) // SECTOR
    ai_secs = (len(ai0) + SECTOR - 1) // SECTOR
    set_dyn["sec"] = body + pay_secs + 2 * ai_secs           # entries подряд, каждая с сектора
    set_dyn["sectors"] = (len(set_buf) + SECTOR - 1) // SECTOR
    win_off = win_dlg[0] - BATTLE_RAMG_BASE
    assert win_off % SECTOR == 0
    pak = {
        "payload_bytes": len(payload),
        "payload_sectors": pay_secs,
        "body_start_sector": body,
    }
    ai = {
        "W": aiW, "H": aiH,
        "hpl_y": (hpl0, hpl1), "shots_y": (sh0, sh1),
        "sec": (body + pay_secs, body + pay_secs + ai_secs),   # entries подряд, каждая с сектора
        "sectors": ai_secs,
        "bytes": len(ai0),
        "win_sec": body + win_off // SECTOR,                   # РЕстрим финала из payload-куска
        "win_sectors": (win_dlg[1] * win_dlg[2] + SECTOR - 1) // SECTOR,
        "digits": ai_digits,
    }
    emit_inc(pal_addr, unit_pal_addr, shadow_pal_addr, shadow_addr, contour_pal_addr,
             status_pal_addr, status_msgs, turn_msgs, win_dlg, top_addr, bot_addr, unit_addrs, evt,
             yellow_pal_addr, win_texts, count_digits, casualties, units, pak, ai, set_dyn)
    print(f"battle pack -> {BATTLE_PAK_PATH.name}: payload={len(payload)} байт "
          f"({pak['payload_sectors']} сект), попапы 2x{len(ai0)} ({ai_secs} сект), PAK={summary['total_bytes']} байт")
    print(f"  armyinfo: {aiW}x{aiH} @ область финала #{win_dlg[0]:06X} (sec {ai['win_sec']}), "
          f"popup sec {ai['sec'][0]}/{ai['sec'][1]}")
    print(f"  inc: {BATTLE_INC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
