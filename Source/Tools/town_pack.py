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
from viewport_pack import align, decode_icn_indices, palette_argb4444_opaque

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


def build_payload(palette, town_img, strip_img, names_masks):
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
    return payload, pal_addr, img_addr, strip_addr, name_pal_addr, name_addrs


def emit_inc(pal_addr, img_addr, strip_addr, name_pal_addr, name_addrs, block_hit, pak):
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
    L.append("                FT_PALETTE_SOURCE TOWN_NAME_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("Town_Name_Begin_DL_SIZE EQU $ - Town_Name_Begin_DL")
    L.append("Town_Name_End_DL:")
    L.append("                FT_END")
    L.append("Town_Name_End_DL_SIZE EQU $ - Town_Name_End_DL")
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
    payload, pal_addr, img_addr, strip_addr, name_pal_addr, name_addrs = build_payload(
        palette, town_img, strip_img, names_masks)
    summary = build_pak(
        [{"type": TYPE_RAMG_BLOB, "target": TOWN_RAMG_BASE, "data": bytes(payload)}],
        TOWN_PAK_PATH,
    )
    pak = {
        "payload_bytes": len(payload),
        "payload_sectors": (len(payload) + SECTOR - 1) // SECTOR,
        "body_start_sector": summary["body_start_sector"],
    }
    emit_inc(pal_addr, img_addr, strip_addr, name_pal_addr, name_addrs, block_hit, pak)
    print(f"town pack -> {TOWN_PAK_PATH.name}: {len(placed)} построек, "
          f"payload={len(payload)} байт ({pak['payload_sectors']} сект), PAK={summary['total_bytes']} байт")
    print(f"  inc: {TOWN_INC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
