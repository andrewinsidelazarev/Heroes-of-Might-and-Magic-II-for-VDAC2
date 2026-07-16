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
import struct
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

# Ключ здания (для сверки с built-set) — СТРОГО параллельно KNIGHT_BUILDINGS. Панорама рисует только
# построенные (redrawCastleBuildings: if !isBuild → continue). CASTLE = keep (рисуется если is_castle).
KNIGHT_BUILDING_KEYS = [
    "WEL2", "CASTLE", "SPEC", "CAPTAIN", "LTUR", "RTUR", "MOAT", "MARKET", "DW2", "THIEVES",
    "TAVERN", "MAGE", "DW5", "DW6", "DW1", "DW3", "DW4", "WELL", "STATUE",
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
# Окно попапа = Dialog::NonFixedFrameBox (BUYBUILD-куски) — геометрия считается в emit_inc
# из высоты текста (dialog_box.cpp); прежний плоский INFO_BOX удалён (был выдумкой).
INFO_WRAP_PX = 390                 # обёртка описаний: boxAreaWidthPx 244 native × 1.6 (экранные px)

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
RECR_MON_ANCHOR = (64, 119)        # центр X / низ Y спрайта = C: pos.x+64 / pos.y+119 (Available сразу под ним)
# Гарнизон: MONH-портрет монстра (monster.ICNMonh()[0], ui_monster.cpp). MONH idx = monster_id-1:
# Peasant1→0, Archer2→1, Pikeman4→3, Swordsman6→5, Cavalry8→7, Paladin10→9 (recruit idx порядок).
GARRISON_MONH = ["MONH0000.ICN", "MONH0001.ICN", "MONH0003.ICN", "MONH0005.ICN", "MONH0007.ICN", "MONH0009.ICN"]
# building idx (1-based, параллельно KNIGHT_BUILDINGS) → recruit idx (0..5); прочее = 255 (не жилище).
DWELLING_MAP = {9: 1, 13: 4, 14: 5, 15: 0, 16: 2, 17: 3}
RECR_W, RECR_H = 321, 304          # размер RECRBKG[0] (native)
# Координаты dialog_recruit.cpp даны относительно activeArea (внутр. область StandardWindow).
# RECRBKG-native (я использую RECRBKG целиком как фон) = activeArea + RECR_BORDER: подтверждено измерением
# запечённых боксов (счётчик RECRBKG(134,159), исходник рисует на (118,143) = −16,−16; рамка стоимости
# RECRBKG(138,54)). Применяю +RECR_BORDER единообразно в эмите к КАЖДОЙ activeArea-координате.
RECR_BORDER   = 16
RECR_COUNT_XY = (151, 147)         # число-счётчик (result) — x+151 центр, y+147 (стр.106)
RECR_NAME_Y   = 11                 # заголовок "Recruit X" центр — y+11 (стр.165); +BORDER в эмите
RECR_AVAIL_X  = 64                 # "Available: N" smallWhite — центр x+64 (центр спрайта); y+120+max(extra,2)
RECR_AVAIL_Y  = 122                # (стр.215; monsterExtraOffsetY=0 для всех 6 Knight-спрайтов ≤96px)
RECR_NUMBUY_X = 107                # "Number to buy:" smallWhite — ПРАВЫЙ край x+107, y+149 (стр.219)
RECR_NUMBUY_Y = 149
RECR_TOTAL_X  = 144                # итог "N (остаток)" smallWhite — центр x+144, y+214 (стр.124)
RECR_TOTAL_Y  = 214
RECR_TOTGOLD_XY = (114, 184)       # икона золота итога — (px1-45, py1+125) = (159-45, 59+125) (стр.151, без offsetX)


def load_town(palette, built_keys=None, castle_name="Castle"):
    """Панорама города. built_keys = построенные здания (redrawCastleBuildings рисует только их;
    непостроенные — пустая площадка/фон). castle_name — плашка имени (drawCastleName). None = всё построено."""
    if built_keys is None:
        built_keys = set(KNIGHT_BUILDING_KEYS)
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
        if KNIGHT_BUILDING_KEYS[bidx_i - 1] not in built_keys:
            continue                        # НЕ построено → не рисуем (пустая площадка)
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
    # Плашка имени замка (drawCastleName ui_castle.cpp:303) вынесена в ОТДЕЛЬНЫЙ оверлей
    # (bake_castle_name_banner → 3-й битмап Town_DL): при запекании в панораму (H=256) низ баннера
    # @248..262 обрезался швом панорамы/панели на y=256 — «затёрт рамкой». Оверлей рисуется поверх.
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
    # 4) Нижний ряд С героем (RedrawIcons castle_dialog.cpp:147): есть герой → PortraitRedraw PORT_BIG
    #    @ rectSign2 (5,361)->strip(5,105). Стартовый Knight-герой = Lord Kilburn (PORT0000, дефолт).
    #    ★STRIP[3]+STRIP[11] рисуются ТОЛЬКО в else-ветке (героя НЕТ, стр.149-155) — плоский плейсхолдер
    #    БЕЗ рамок слотов. Я его ошибочно пёк @ (112,105) поверх строки → он ЗАТИРАЛ золотые рамки слотов
    #    из STRIP[0] (панель, рамки есть и на y105+). Убрано: строка героя = STRIP[0] + пустые STRIP[2].
    port, w, h, ox, oy = icn("PORT0000.ICN", 0)
    _blit_icn(buf, port, w, h, ox, oy, 5, 105, TOWN_W, STRIP_H)
    # 5) ГАРНИЗОН (верхний ArmyBar=_army) @ (112,262)->y6. ArmyBar non-mini (army_bar.cpp):
    #    пустая ячейка = STRIP[2] (82×93, шаг 88); ЗАПОЛНЕННАЯ = renderMonsterFrame:
    #    плита расы Knight STRIP[4] + БОЛЬШОЙ спрайт MONH[0] (@ ox/oy ICN) + счётчик. НЕ MONS32!
    # Пустые ячейки обоих рядов (STRIP[2] 82×93, шаг 88). Портреты/счётчики — ДИНАМИЧЕСКИ поверх
    # (единая слот-модель ArmyType/ArmyCnt): гарнизон стартует ПУСТ, армия у героя.
    s2, sw, sh, _, _ = icn("STRIP.ICN", 2)
    for i in range(5):
        _blit_icn(buf, s2, sw, sh, 0, 0, 112 + i * 88, 6, TOWN_W, STRIP_H)     # ряд гарнизона (top)
        _blit_icn(buf, s2, sw, sh, 0, 0, 112 + i * 88, 105, TOWN_W, STRIP_H)   # ряд героя (bottom)
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
    # ★ЧИСЛА ресурсов НЕ запекаются (все 7): постройка списывает ресурсы по оригиналу —
    # значения рисуются ЖИВЫМИ (KingdomGold + KingdomRes6 @ TOWN_RES_CX/VY).
    # 8) Кнопка EXIT (castle_dialog.cpp:379 BUTTON_EXIT_TOWN → useOriginalResources()=TREASURY[1],
    #    agg_image.cpp:910). 80×25 @ dialog(553,428)->strip(553,172).
    ex, w, h, ox, oy = icn("TREASURY.ICN", 1)
    _blit_icn(buf, ex, w, h, ox, oy, 553, 172, TOWN_W, STRIP_H)
    return bytes(buf)

def render_name_mask(agg, ent, name, font_icn="SMALFONT.ICN", scale=1.0):
    """Строка → маска (idx 15=глиф / 0=прозрачно) шрифтом font_icn. Палитра белая-альфа (idx0 прозрачен).
    (mask, W, H). SMALFONT (h9) для подписей, FONT (h14) для заголовка. scale — пред-масштаб NEAREST
    (весь экран города ×1.6, шрифты обязаны масштабироваться ВМЕСТЕ с ним — пропорции оригинала)."""
    sf = read_icn(agg_entry(agg, ent, font_icn))
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
    if scale != 1.0:
        from PIL import Image
        W1, H1 = max(1, round(W0 * scale)), max(1, round(H0 * scale))
        im = Image.frombytes("L", (W0, H0), bytes(base)).resize((W1, H1), Image.NEAREST)
        return im.tobytes(), W1, H1
    return bytes(base), W0, H0


def bake_font(agg, ent, pad=2, font_icn="SMALFONT.ICN", scale=1.0):
    """Атлас глифов font_icn для Render_DrawString: ASCII 32..127 → (маска 1Б/px idx15, w, h+pad).
    Тот же формат, что render_name_mask (проверен на железе). Низ паддится pad прозрачных строк —
    реальный FT812 режет ~2px низа мелкого глифа (см. память ft812-small-glyph-bottom-padding).
    scale — пред-масштаб глифов (экран города ×1.6 → шрифты ×1.6, пропорции оригинала)."""
    sf = read_icn(agg_entry(agg, ent, font_icn))
    out = []
    for c in range(32, 128):
        idx = c - 32
        try:
            ch = " " if (c == 32 or idx >= len(sf)) else chr(c)
            m, w, h = render_name_mask(agg, ent, ch, font_icn, scale=scale)
        except Exception:
            m, w, h = render_name_mask(agg, ent, " ", font_icn, scale=scale)
        out.append((m + bytes(w * pad), w, h + pad))   # +pad прозрачных строк снизу
    return out


# --- ТАВЕРНА (castle_tavern.cpp:_openTavern): окно-слух недели. Слухи 2..8 fheroes2
# (world.cpp:676-688). Слухи 0/1 (ultimate artifact) требуют механики артефакта — в порте её
# нет → 7 статичных слухов, выбор по неделе (GetWeekSeed → у нас (day−1)/7 mod 7). ---
TAVERN_INTRO = "A generous tip for the barkeep yields the following rumor:"
TAVERN_RUMORS = [
    "The truth is out there.",
    "The dark side is stronger.",
    "The end of the world is near.",
    "The bones of Lord Slayer are buried in the foundation of the arena.",
    "A Black Dragon will take out a Titan any day of the week.",
    "He told her: Yada yada yada... and then she said: Blah, blah, blah...",
    "An unknown force is being resurrected...",
]


def bake_tavern(agg, ent):
    """TAVWIN: рамка[0] + сцена[1]@(3,3) + СТАТИЧНЫЙ кадр бармена[2] (ox/oy в кадре; анимация
    2..21 — компромисс RAM_G: один кадр). Возврат (blob, w, h) в индексах KB."""
    icn = read_icn(agg_entry(agg, ent, "TAVWIN.ICN"))
    fh, fe = icn[0]
    W, H = fh["w"], fh["h"]
    canvas = bytearray(decode_icn_indices(fh, fe))

    def blit(fr, dx, dy):
        h, e = icn[fr]
        idx = decode_icn_indices(h, e)
        ox, oy = dx + h.get("ox", 0), dy + h.get("oy", 0)
        for y in range(h["h"]):
            for x in range(h["w"]):
                v = idx[y * h["w"] + x]
                if v:
                    canvas[(oy + y) * W + ox + x] = v
    blit(1, 3, 3)
    blit(2, 3, 3)
    return bytes(canvas), W, H


SPEED_STRINGS = {1: "Crawling", 2: "Very Slow", 3: "Slow", 4: "Average", 5: "Fast",
                 6: "Very Fast", 7: "Ultra Fast", 8: "Blazing", 9: "Instant"}
KNIGHT_WELL_MONSTERS = ["Peasant", "Archer", "Pikeman", "Swordsman", "Cavalry", "Paladin"]
KNIGHT_WELL_PLURALS = ["Peasants", "Archers", "Pikemen", "Swordsmen", "Cavalries", "Paladins"]
KNIGHT_WELL_DWELLS = ["Thatched Hut", "Archery Range", "Blacksmith", "Armory",
                      "Jousting Arena", "Cathedral"]
WELL_SECT_OFS = [(0, 1), (0, 151), (0, 301), (314, 1), (314, 151), (314, 301)]


def _knight_monster_rows():
    """Статы 6 Knight-монстров из ЭТАЛОНА monster_info.cpp (парс как monster_stats.py)."""
    import monster_stats as ms
    text = ms.SRC.read_text(encoding="utf-8", errors="replace")
    rows, started = {}, False
    for line in text.splitlines():
        if "attack | defence | damageMin" in line:
            started = True
            continue
        if not started:
            continue
        m = ms.ROW.match(line.strip().rstrip(","))
        if m:
            atk, dfn, dmin, dmax, hp, spd, shots, name = m.groups()
            rows[name] = (int(atk), int(dfn), int(dmin), int(dmax), int(hp), ms.SPEED[spd])
        elif rows and "}" in line and ";" in line:
            break
    return [rows[n] for n in KNIGHT_WELL_MONSTERS]


def bake_well(agg, ent):
    """Well (castle_well.cpp): база 640×461 (WELLBKG, секции ПУСТЫ) + 6 секций-пиксельров
    (жилище CSTLKNGT[19+i] @(+21,+35), имя жилища smallWhite centered (+86,+104), имя
    монстра (+122,+19), статы centered X=+269 от Y=+22 (Attack/Defense/Damage/HP/
    [пропуск]/Speed:/строка/[пропуск]/Growth), СТАТИЧНЫЙ монстр-кадр, Available-подпись
    (+20+24,+121+2; ЧИСЛО — динамика Z80)). MAX не делаем — в HoMM2 её нет. Возврат
    (base 640×461, [6×(pix, w, h, ox, oy)], exit0, exit1) — EXIT = WELLXTRA[0]/[1] 61×19."""
    smalfont = read_icn(agg_entry(agg, ent, "SMALFONT.ICN"))

    def text_w(s):
        return sum(4 if c == " " else smalfont[ord(c) - 32][0]["w"] for c in s)

    def put_text(buf, W, H, s, x, y):
        for c in s:
            if c == " ":
                x += 4
                continue
            gh, ge = smalfont[ord(c) - 32]
            gi = decode_icn_indices(gh, ge)
            _blit_icn(buf, gi, gh["w"], gh["h"], gh.get("ox", 0), gh.get("oy", 0), x, y, W, H)
            x += gh["w"]

    wb_h, wb_e = read_icn(agg_entry(agg, ent, "WELLBKG.ICN"))[0]
    full = bytearray(decode_icn_indices(wb_h, wb_e))   # 640×480
    W, HGT = 640, CONSTRUCT_H                          # ПОЛНАЯ область construct (низ включая бар)
    base = bytearray(W * HGT)
    base[:W * min(480, HGT)] = full[:W * min(480, HGT)]
    # низ: SMALLBAR-полоса + подпись + вбейканная ОТЖАТАЯ кнопка EXIT (нажатая — оверлей Z80)
    def _bl(name, fr, x, y):
        h2, e2 = read_icn(agg_entry(agg, ent, name))[fr]
        _blit_icn(base, decode_icn_indices(h2, e2), h2["w"], h2["h"], 0, 0, x, y, W, HGT)
    _bl("SMALLBAR.ICN", 1, 0, 461)
    _bl("SMALLBAR.ICN", 0, 21, 461)
    _bl("SMALLBAR.ICN", 3, 619, 461)
    ttl = "Town Population Information and Statistics"
    put_text(base, W, HGT, ttl, 320 - text_w(ttl) // 2, 466)
    _bl("WELLXTRA.ICN", 0, 579, 461)
    knights = read_icn(agg_entry(agg, ent, "CSTLKNGT.ICN"))
    mon_rows = _knight_monster_rows()
    sections = []
    for i, (ox, oy) in enumerate(WELL_SECT_OFS):
        sw = 314 if ox == 0 else W - 314
        sh = 150
        sect = bytearray(base[0:0])                    # соберём на копии базы, потом вырежем
        canvas = bytearray(base)                       # рисуем секцию на копии базы
        dh, de = knights[19 + i]
        di = decode_icn_indices(dh, de)
        _blit_icn(canvas, di, dh["w"], dh["h"], 0, 0, ox + 21, oy + 35, W, HGT)
        s = KNIGHT_WELL_DWELLS[i]
        put_text(canvas, W, HGT, s, ox + 86 - text_w(s) // 2, oy + 104)
        s = KNIGHT_WELL_PLURALS[i]
        put_text(canvas, W, HGT, s, ox + 122 - text_w(s) // 2, oy + 19)
        atk, dfn, dmin, dmax, hp, spd = mon_rows[i]
        LINE = 11
        yy = oy + 22
        for s in (f"Attack: {atk}", f"Defense: {dfn}",
                  f"Damage: {dmin}" + (f"-{dmax}" if dmin != dmax else ""), f"HP: {hp}"):
            put_text(canvas, W, HGT, s, ox + 269 - text_w(s) // 2, yy)
            yy += LINE
        yy += LINE                                     # пропуск строки
        put_text(canvas, W, HGT, "Speed:", ox + 269 - text_w("Speed:") // 2, yy)
        yy += LINE
        s = SPEED_STRINGS[spd]
        put_text(canvas, W, HGT, s, ox + 269 - text_w(s) // 2, yy)
        yy += 2 * LINE
        put_text(canvas, W, HGT, "Growth", ox + 269 - text_w("Growth") // 2, yy)
        yy += LINE
        s = f"+{RECRUIT_AVAIL[i]} / week"
        put_text(canvas, W, HGT, s, ox + 269 - text_w(s) // 2, yy)
        put_text(canvas, W, HGT, "Available: ", ox + 20 + 24, oy + 121 + 2)
        # статичный монстр (боевой ICN, кадр стойки) — низ по линии ~+112, центр ~+187
        mh, me = read_icn(agg_entry(agg, ent, ("PEASANT.ICN", "ARCHER.ICN", "PIKEMAN.ICN",
                                               "SWORDSMN.ICN", "CAVALRYR.ICN", "PALADIN.ICN")[i]))[1]
        mi = decode_icn_indices(mh, me)
        _blit_icn(canvas, mi, mh["w"], mh["h"], 0, 0, ox + 187 - mh["w"] // 2,
                  oy + 118 - mh["h"], W, HGT)
        # вырез секции
        pix = bytearray(sw * sh)
        for r in range(sh):
            pix[r * sw:(r + 1) * sw] = canvas[(oy + r) * W + ox:(oy + r) * W + ox + sw]
        sections.append((bytes(pix), sw, sh, ox, oy))
    ex = read_icn(agg_entry(agg, ent, "WELLXTRA.ICN"))
    exit0 = (bytes(decode_icn_indices(*ex[0])), ex[0][0]["w"], ex[0][0]["h"])
    exit1 = (bytes(decode_icn_indices(*ex[1])), ex[1][0]["w"], ex[1][0]["h"])
    return bytes(base), sections, exit0, exit1


def bake_market(agg, ent):
    """Рынок (Dialog::Marketplace): ВСЕ кадры TRADPOST.ICN 0..18 (обмен-стрелки[0],
    слайдер[1]/[2], стрелки L/R[3..6], иконки ресурсов[7..13] 34×34, рамка выбора[14],
    TRADE[15]/[16], EXIT[17]/[18]). Возврат [(blob,w,h)×19]."""
    icn = read_icn(agg_entry(agg, ent, "TRADPOST.ICN"))
    out = []
    for fr in range(19):
        h, e = icn[fr]
        out.append((bytes(decode_icn_indices(h, e)), h["w"], h["h"]))
    return out


def bake_okay_button(agg, ent):
    """Кнопка OKAY текст-диалогов = SYSTEM.ICN[1] (отжата) / [2] (нажата) — ориг. ресурсы
    fheroes2 BUTTON_SMALL_OKAY_GOOD. Возврат [(blob,w,h)×2]."""
    icn = read_icn(agg_entry(agg, ent, "SYSTEM.ICN"))
    out = []
    for fr in (1, 2):
        h, e = icn[fr]
        out.append((bytes(decode_icn_indices(h, e)), h["w"], h["h"]))
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
    _blit_icn(buf, gi, h["w"], h["h"], 0, 0, 0, 0, RECR_W, RECR_H)  # ox=0: окно заполняет буфер целиком (иначе левая рамка обрезается)
    return bytes(buf)


# --- Окно строительства замка (Castle::_openConstructionDialog, castle_town.cpp) ---
# Фон CASLWIND.ICN[0] (640×461). Сетка 6×3 слотов BuildingInfo (135×70). Замок застроен полностью →
# каждый слот статичен: рамка BLDGXTRA[0] + иконка CSTLKNGT[index] (+1,+1) + галочка TOWNWIND[11]
# (ALREADY_BUILT) + имя smallWhite (центр area.x+68, area.y+61). Композлю всё в Python → статичный
# кадр 640×461 (замок всегда полностью построен → окно не меняется). Позиции window-local (cur_pt).
CONSTRUCT_W, CONSTRUCT_H = 640, 480   # CASLWIND 640×461 + нижний статус-бар 19 (castle_town.cpp:447)
# (slot_x, slot_y, CSTLKNGT idx, имя, key) — раскладка/индексы ТОЧНО по castle_town.cpp:220-332 +
# getIndexBuildingSprite (castle_building_info.cpp:1373) + getBuildingName (:836,445).
# key = идентификатор здания для сверки с реальным built-set (dump_mp2_castles.default_built_keys).
CONSTRUCT_SLOTS = [
    (5,   2, 19, "Thatched Hut","DW1"), (149,  2, 20, "Archery Range","DW2"),(293,  2, 21, "Blacksmith","DW3"),
    (5,  77, 22, "Armory","DW4"),       (149, 77, 23, "Jousting Arena","DW5"),(293, 77, 24, "Cathedral","DW6"),
    (5, 157,  0, "Mage Guild","MAGE"),  (149,157,  2, "Tavern","TAVERN"),    (293,157,  1, "Thieves' Guild","THIEVES"),
    (5, 232,  3, "Shipyard","SHIPYARD"),(149,232,  7, "Statue","STATUE"),    (293,232, 10, "Marketplace","MARKET"),
    (5, 307,  4, "Well","WELL"),        (149,307, 11, "Farm","WEL2"),        (293,307, 13, "Fortifications","SPEC"),
    (5, 387,  8, "Left Turret","LTUR"), (149,387,  9, "Right Turret","RTUR"),(293,387, 12, "Moat","MOAT"),
]
CONSTRUCT_EXIT = (553, 428, 80, 25)   # BUTTON_EXIT_TOWN native (castle_town.cpp:468) — хит-рект закрытия
# Палитры-ремапы PAL::GRAY + PAL::DARKENING (engine/pal.cpp) — для DISABLE-зданий (серятся). Точные 256-таблицы.
PAL_GRAY = [36,36,36,36,36,36,36,36,36,36,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,10,11,12,12,13,14,15,16,17,18,18,19,20,20,21,22,22,23,24,25,26,26,27,28,29,31,14,16,17,18,20,21,22,24,25,26,28,28,29,30,31,32,32,33,33,33,34,34,16,17,18,20,21,22,23,24,25,26,27,28,30,31,32,32,33,34,35,35,36,36,36,11,11,11,11,11,12,12,12,13,13,14,15,16,17,18,19,20,21,21,22,23,24,25,12,13,14,16,17,18,19,20,21,22,24,24,25,26,27,28,29,31,32,32,33,11,12,12,13,14,14,16,16,17,18,18,19,20,21,22,23,24,25,26,27,29,30,32,10,11,11,12,12,12,13,13,14,14,15,15,16,16,17,18,19,20,21,22,23,24,26,10,10,11,11,11,12,12,12,12,14,16,17,18,20,22,24,17,10,12,15,19,10,10,15,17,18,20,21,22,23,25,26,27,27,24,21,22,26,26,27,36,12,18,25,19,21,24,26,36,36,36,36,36,36,36,36,36,36]
PAL_DARK = [0,0,0,0,0,0,0,0,0,0,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,36,36,36,36,36,36,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,62,62,62,62,62,62,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,84,84,84,84,84,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,107,107,107,107,107,107,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,130,130,130,130,130,130,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,151,151,151,151,151,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,174,174,174,174,174,174,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,197,197,197,197,197,202,203,204,205,206,207,208,209,210,211,212,213,213,213,213,213,214,215,216,217,218,219,220,221,225,226,227,228,229,230,230,230,230,73,75,77,79,81,76,78,74,76,78,80,244,245,245,245,0,0,0,0,0,0,0,0,0,0]


def _gray_idx(i):
    """PAL::GRAY затем PAL::DARKENING (buildinginfo.cpp:364-365). idx0 (прозрачно) сохраняем."""
    return 0 if i == 0 else PAL_DARK[PAL_GRAY[i]]


def _draw_smalfont(buf, W, H, agg, ent, text, x, y):
    """Нарисовать строку SMALFONT (реальные индексы KB.PAL, белый глиф) в indexed-буфер по перу (x,y=верх)."""
    sf = read_icn(agg_entry(agg, ent, "SMALFONT.ICN"))
    cx = x
    for ch in text:
        if ch == " ":
            cx += 4; continue
        gi_idx = ord(ch) - 32
        if gi_idx < 0 or gi_idx >= len(sf):
            cx += 4; continue
        gh, ge = sf[gi_idx]
        gi = decode_icn_indices(gh, ge)
        _blit_icn(buf, gi, gh["w"], gh["h"], gh.get("ox", 0), gh.get("oy", 0), cx, y, W, H)
        cx += gh["w"]


def _smalfont_width(agg, ent, text):
    sf = read_icn(agg_entry(agg, ent, "SMALFONT.ICN"))
    w = 0
    for ch in text:
        if ch == " ":
            w += 4; continue
        gi_idx = ord(ch) - 32
        w += 4 if (gi_idx < 0 or gi_idx >= len(sf)) else sf[gi_idx][0]["w"]
    return w


def _draw_castle_image(buf, agg, ent, pt_x, pt_y):
    """DrawImageCastle (castle.cpp:1326): земля OBJNTWBA + замок OBJNTOWN на pt. Knight, DIRT, построен.
    Земля под замком (24,13) = DIRT (terrain idx 339 ∈ [321,361) по getGroundByImageIndex) → OBJNTWBA idx 50."""
    tw = read_icn(agg_entry(agg, ent, "OBJNTWBA.ICN"))
    tn = read_icn(agg_entry(agg, ent, "OBJNTOWN.ICN"))
    def blit(icn, frame, dx, dy):
        hh, ee = icn[frame]
        gi = decode_icn_indices(hh, ee)
        _blit_icn(buf, gi, hh["w"], hh["h"], hh.get("ox", 0), hh.get("oy", 0), dx, dy, CONSTRUCT_W, CONSTRUCT_H)
    g = 50                                                         # DIRT ground base (DrawImageCastle switch)
    for i in range(5):                                            # земля: 2 ряда по 5 (y=3*32, 4*32)
        blit(tw, g + i,     pt_x + i * 32, pt_y + 3 * 32)
        blit(tw, g + 5 + i, pt_x + i * 32, pt_y + 4 * 32)
    c = 0                                                         # Knight построен: OBJNTOWN base 0
    blit(tn, c,             pt_x + 2 * 32, pt_y)                  # верхушка (sprite2)
    for ii in range(5):                                          # 3 ряда башен/стен (y=32,64,96)
        blit(tn, c + 1 + ii,  pt_x + ii * 32, pt_y + 32)
        blit(tn, c + 6 + ii,  pt_x + ii * 32, pt_y + 2 * 32)
        blit(tn, c + 11 + ii, pt_x + ii * 32, pt_y + 3 * 32)


def _draw_resource_panel(buf, agg, ent):
    """drawResourcePanel (ui_castle.cpp:242): ROI (552,262,82,192) — 6 ресурсов в 2 колонки + золото.
    Значения = START_FUNDS (в нашем движке ресурсы не тратятся, кроме золота; золото START=7500)."""
    res = read_icn(agg_entry(agg, ent, "RESOURCE.ICN"))
    rx, ry, rw, rh = 552, 262, 82, 192
    for y in range(ry, ry + rh):                                  # Fill ROI чёрным (idx 0)
        for x in range(rx, rx + rw):
            buf[y * CONSTRUCT_W + x] = 0
    maxW, maxH = 39, 32
    lc, rc = rx + 1, rx + 1 + maxW + 2
    fh = 9                                                        # SMALL font height (SMALFONT)
    offY = [0, maxH + fh + 2, (maxH + fh) * 2 - 1, (maxH + fh) * 3 + 1]
    def icon(fi, cx_base, oy_i):                                  # RESOURCE[fi] по низу ячейки, центр колонки
        hh, ee = res[fi]; gi = decode_icn_indices(hh, ee); w, h = hh["w"], hh["h"]
        _blit_icn(buf, gi, w, h, 0, 0, cx_base + (maxW - w) // 2, ry + offY[oy_i] + maxH - h, CONSTRUCT_W, CONSTRUCT_H)
    def val(s, cx_base, oy_i):
        w = _smalfont_width(agg, ent, s)
        _draw_smalfont(buf, CONSTRUCT_W, CONSTRUCT_H, agg, ent, s, cx_base + (maxW - w) // 2, ry + offY[oy_i] + maxH + 1)
    icon(0, lc, 0); icon(3, rc, 0)                               # wood | sulfur
    icon(4, lc, 1); icon(1, rc, 1)                               # crystal | mercury
    icon(2, lc, 2); icon(5, rc, 2)                               # ore | gems
    # ★ЧИСЛА ресурсов НЕ запекаются (ни одно): постройка списывает 7 ресурсов по оригиналу —
    # все значения рисуются ЖИВЫМИ (KingdomGold + KingdomRes6, CON_RES_CX/VY).
    gh, ge = res[6]; ggi = decode_icn_indices(gh, ge); gw, ghh = gh["w"], gh["h"]  # золото по центру
    _blit_icn(buf, ggi, gw, ghh, 0, 0, rx + (rw - gw) // 2, ry + offY[3], CONSTRUCT_W, CONSTRUCT_H)


def bake_castle_construction(agg, ent, castle_name="Castle", statuses=None):
    """Статичный кадр окна строительства → 640×461 KB.PAL. РЕАЛЬНЫЕ данные (кровь):
    castle_name из MX2, statuses = {key: BUILT/ALLOW/REQUIRES/DISABLE/LACK} (dump_mp2_castles.build_statuses,
    по Castle::CheckBuyBuilding). Рендер статуса точно по BuildingInfo::Redraw (buildinginfo.cpp:349)."""
    if statuses is None:
        statuses = {s[4]: "BUILT" for s in CONSTRUCT_SLOTS}       # fallback: всё построено
    h, e = read_icn(agg_entry(agg, ent, "CASLWIND.ICN"))[0]
    buf = bytearray(decode_icn_indices(h, e))                      # фон CASLWIND[0] (opaque, 640×461)
    buf.extend(bytes(CONSTRUCT_W * (CONSTRUCT_H - h["h"])))        # + нижний бар до 480 (castle_town.cpp:447)
    def _icn(name, frame):
        hh, ee = read_icn(agg_entry(agg, ent, name))[frame]
        return decode_icn_indices(hh, ee), hh["w"], hh["h"]
    # --- нижний статус-бар @ y461: prev SMALLBAR[1] @x0 + бар SMALLBAR[0] @x21 + next SMALLBAR[3] @x619 ---
    g, w, hh2 = _icn("SMALLBAR.ICN", 1); _blit_icn(buf, g, w, hh2, 0, 0, 0, 461, CONSTRUCT_W, CONSTRUCT_H)
    g, w, hh2 = _icn("SMALLBAR.ICN", 0); _blit_icn(buf, g, w, hh2, 0, 0, 21, 461, CONSTRUCT_W, CONSTRUCT_H)
    g, w, hh2 = _icn("SMALLBAR.ICN", 3); _blit_icn(buf, g, w, hh2, 0, 0, 619, 461, CONSTRUCT_W, CONSTRUCT_H)
    # Текст статус-бара (defaultTitle castle_town.cpp:494; календарь не тикает → день 1) по центру бара.
    title = "Castle Options. Month: 1, Week: 1, Day: 1"
    tw2 = _smalfont_width(agg, ent, title)
    _draw_smalfont(buf, CONSTRUCT_W, CONSTRUCT_H, agg, ent, title, 320 - tw2 // 2, 466)
    # --- капитан не построен → STONEBAK-заглушка области опций (530,163,110,84) (castle_town.cpp:198-207) ---
    sb, sbw, sbh = _icn("STONEBAK.ICN", 0)
    for yy in range(84):
        row = (163 + yy) * sbw
        drow = (163 + yy) * CONSTRUCT_W
        for xx in range(110):
            buf[drow + 530 + xx] = sb[row + 530 + xx]
    # --- клетка капитана BUILD_CAPTAIN @ (444,165): CSTLCAPK[0] (Knight, не построен) ---
    g, w, hh2 = _icn("CSTLCAPK.ICN", 0); _blit_icn(buf, g, w, hh2, 0, 0, 444, 165, CONSTRUCT_W, CONSTRUCT_H)
    # --- слоты героев найма: героев-рекрутов в порте нет → STRIP[3] «нет героя» + deny X
    #     (castle_town.cpp:415-445; hero1 @443,260 102×93, hero2 @443,363) ---
    s3, s3w, s3h = _icn("STRIP.ICN", 3)
    dny, dnw, dnh = _icn("TOWNWIND.ICN", 12)
    for hy in (260, 363):
        for yy in range(min(93, s3h)):
            srow = yy * s3w
            drow = (hy + yy) * CONSTRUCT_W
            for xx in range(min(102, s3w)):
                buf[drow + 443 + xx] = s3[srow + xx]
        _blit_icn(buf, dny, dnw, dnh, 0, 0, 443 + 102 - 4 + 1 - dnw, hy + 93 - 2 - dnh, CONSTRUCT_W, CONSTRUCT_H)
    _draw_castle_image(buf, agg, ent, 459, 6)                     # спрайт замка справа-вверху (castle_town.cpp:210-212)
    _draw_resource_panel(buf, agg, ent)                          # панель ресурсов внизу-справа (ui_castle.cpp:242)
    # --- кнопка EXIT = TREASURY[1] @ (553,428) (BUTTON_EXIT_TOWN, castle_town.cpp:468) — ПОСЛЕ панели
    #     (её Fill ROI y262..454 иначе зальёт кнопку чёрным) ---
    g, w, hh2 = _icn("TREASURY.ICN", 1); _blit_icn(buf, g, w, hh2, 0, 0, 553, 428, CONSTRUCT_W, CONSTRUCT_H)
    nw = _smalfont_width(agg, ent, castle_name)                  # имя замка центр x=538, y=2 (castle_town.cpp:216)
    _draw_smalfont(buf, CONSTRUCT_W, CONSTRUCT_H, agg, ent, castle_name, 538 - nw // 2, 2)
    frame_h, frame_e = read_icn(agg_entry(agg, ent, "BLDGXTRA.ICN"))[0]
    frame_gi = decode_icn_indices(frame_h, frame_e)
    fw, fh = frame_h["w"], frame_h["h"]
    cstl = read_icn(agg_entry(agg, ent, "CSTLKNGT.ICN"))
    tw = read_icn(agg_entry(agg, ent, "TOWNWIND.ICN"))
    chk_h, chk_e = tw[11]                                          # галочка «построено» (ALREADY_BUILT)
    chk_gi = decode_icn_indices(chk_h, chk_e); cw, ch = chk_h["w"], chk_h["h"]
    deny_h, deny_e = tw[12]                                        # «нельзя» (REQUIRES/DISABLE)
    deny_gi = decode_icn_indices(deny_h, deny_e); dw, dh = deny_h["w"], deny_h["h"]
    mon_h, mon_e = tw[13]                                          # «нет ресурсов» (LACK)
    mon_gi = decode_icn_indices(mon_h, mon_e); mw, mh = mon_h["w"], mon_h["h"]
    cx = read_icn(agg_entry(agg, ent, "CASLXTRA.ICN"))
    allow_h, allow_e = cx[1]                                       # полоса имени «allow build» (зелёная)
    allow_gi = decode_icn_indices(allow_h, allow_e); aw, ah = allow_h["w"], allow_h["h"]
    deny_bg_h, deny_bg_e = cx[2]                                   # полоса имени «нельзя/нет ресурсов»
    deny_bg_gi = decode_icn_indices(deny_bg_h, deny_bg_e); dbw, dbh = deny_bg_h["w"], deny_bg_h["h"]
    for (sx, sy, idx, name, key) in CONSTRUCT_SLOTS:
        st = statuses.get(key, "ALLOW")
        _blit_icn(buf, frame_gi, fw, fh, 0, 0, sx, sy, CONSTRUCT_W, CONSTRUCT_H)       # рамка слота
        bh, be = cstl[idx]
        bgi = decode_icn_indices(bh, be)
        _blit_icn(buf, bgi, bh["w"], bh["h"], 0, 0, sx + 1, sy + 1, CONSTRUCT_W, CONSTRUCT_H)  # иконка здания (+1,+1)
        # ★Статус-визуалы (полоса+имя+марка) НЕ запекаются — их приносит рантайм-патч
        # (Construct_Recalc → band/corner из PAK): статусы ЖИВЫЕ (постройка открывает
        # зависимые, тратит ресурсы, NOT_TODAY). Исключение — вечный DISABLE (Shipyard
        # без моря): серая полоса+deny+имя запечены, рантайм слот пропускает.
        if st == "DISABLE":
            for yy in range(12):                                   # gray name-bar рамки (6,59,125,12)
                for xx in range(125):
                    v = frame_gi[(59 + yy) * fw + (6 + xx)]
                    buf[(sy + 59 + yy) * CONSTRUCT_W + (sx + 6 + xx)] = _gray_idx(v)
            for yy in range(dh):                                   # серый deny TOWNWIND[12]
                for xx in range(dw):
                    v = deny_gi[yy * dw + xx]
                    if v != TRANSPARENT:
                        buf[(sy + 58 - 2 - dh + yy) * CONSTRUCT_W + (sx + fw - 5 + 1 - dw + xx)] = _gray_idx(v)
            nw = _smalfont_width(agg, ent, name)
            _draw_smalfont(buf, CONSTRUCT_W, CONSTRUCT_H, agg, ent, name, sx + 68 - nw // 2, sy + 61)
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


def bake_recruit_gold(agg, ent):
    """Иконка золота RESOURCE[6] (цена-за-1 в рамке «Cost per troop»), пред-масштаб ×1.6, прозрачная idx0."""
    h, e = read_icn(agg_entry(agg, ent, "RESOURCE.ICN"))[6]
    gi = decode_icn_indices(h, e)
    return _prescale16(gi, h["w"], h["h"])         # (bytes, nw, nh)


# Тень окна — ГЛОБАЛЬНАЯ рантайм-процедура Render_WindowShadowDL (render.asm, одна формула на все окна).

# ============================================================================
# ПАТЧ-СЕКЦИЯ PAK (строительство по оригиналу): рантайм-обновление композитов
# RAM_G стримом с SD (спрайты зданий/полосы статусов НЕ влезают в RAM_G резидентно).
# Патч = поток «ранов», сектор-локальные записи:
#   [len u16 LE][addr u24 LE][len байт]  — записать len байт в RAM_G @ addr
#   len = 0x0000 → конец данных сектора (перейти к следующему)
#   len = 0xFFFF → конец патча
# Запись НЕ пересекает границу сектора (паддинг) — блиттер Z80 тривиален.
# ============================================================================

def _pack_patch(runs):
    """runs: [(ramg_addr, bytes)] → патч-поток, выровненный на сектора."""
    out = bytearray()
    cur = bytearray()
    def flush(end_marker):
        nonlocal cur
        cur += b"\xFF\xFF" if end_marker else b"\x00\x00"
        cur += b"\x00" * (SECTOR - len(cur))
        out.extend(cur)
        cur = bytearray()
    for addr, data in runs:
        data = bytes(data)
        while data:
            room = SECTOR - 2 - len(cur)              # −2 на маркер конца сектора
            if room < 6:                              # заголовок 5 + хотя бы 1 байт
                flush(False)
                continue
            chunk = min(len(data), room - 5)
            cur += struct.pack("<H", chunk) + addr.to_bytes(3, "little") + data[:chunk]
            addr += chunk
            data = data[chunk:]
    flush(True)
    return bytes(out)


def _rect_runs(pix, w, h, dst_base, x, y, stride=640):
    """Прямоугольник (все пиксели) → раны-строки (пред-композиция против статичного фона)."""
    return [(dst_base + (y + r) * stride + x, pix[r * w:(r + 1) * w]) for r in range(h)]


def build_pano_patches(agg, ent, img_addr):
    """Панорамные патчи: [z] → патч-поток спрайта здания (НЕпрозрачные раны → композиция
    как Blit в TOWN_IMG_RAMG). Порядок KNIGHT_BUILDINGS = z-порядок (redrawCastleBuildings);
    рантайм применяет построенные в z-порядке — перекрытия честны. Возвращает (patches, bboxes)."""
    out = []
    bboxes = []
    for icn_name, frame in KNIGHT_BUILDINGS:
        hdr, enc = read_icn(agg_entry(agg, ent, icn_name))[frame]
        gi = decode_icn_indices(hdr, enc)
        w, h = hdr["w"], hdr["h"]
        ox = hdr.get("ox", 0)
        oy = hdr.get("oy", 0)
        runs = []
        for yy in range(h):
            dy = oy + yy
            if not (0 <= dy < TOWN_H):                 # клип канвой панорамы 640×256
                continue
            row = yy * w
            x = 0
            while x < w:
                if gi[row + x] == TRANSPARENT:
                    x += 1
                    continue
                x0 = x
                while x < w and gi[row + x] != TRANSPARENT:
                    x += 1
                xa, xb = max(0, ox + x0), min(TOWN_W, ox + x)
                if xb > xa:
                    s = row + x0 + (xa - (ox + x0))
                    runs.append((img_addr + dy * TOWN_W + xa, gi[s:s + (xb - xa)]))
        out.append(_pack_patch(runs))
        bboxes.append((max(0, ox), max(0, oy), min(TOWN_W, ox + w), min(TOWN_H, oy + h)))
    return out, bboxes


def build_status_patches(agg, ent, construct_addr):
    """Патчи статусов слотов стройки (BuildingInfo::Redraw, buildinginfo.cpp:349):
    band [slot][0=plain(BUILT) 1=green(ALLOW) 2=red(прочее)] = полоса CASLXTRA/рамки + ИМЯ;
    corner [slot][0=clean 1=check(TW11) 2=deny(TW12) 3=money(TW13)] на чистой иконке.
    Пред-композиция против статичного чистого кадра (frame+icon) → rect-раны. Возвращает
    (band_patches, corner_patches, (corner_x0, corner_y0))."""
    frame_h, frame_e = read_icn(agg_entry(agg, ent, "BLDGXTRA.ICN"))[0]
    frame_gi = decode_icn_indices(frame_h, frame_e)
    fw, fh = frame_h["w"], frame_h["h"]
    cstl = read_icn(agg_entry(agg, ent, "CSTLKNGT.ICN"))
    cx = read_icn(agg_entry(agg, ent, "CASLXTRA.ICN"))
    tw = read_icn(agg_entry(agg, ent, "TOWNWIND.ICN"))
    mdim = {}
    for k, fi in ((1, 11), (2, 12), (3, 13)):          # check / deny / money
        mh_, me_ = tw[fi]
        mdim[k] = (decode_icn_indices(mh_, me_), mh_["w"], mh_["h"])
    bnd = {}
    for k, fi in ((1, 1), (2, 2)):                     # green / red
        bh_, be_ = cx[fi]
        bnd[k] = (decode_icn_indices(bh_, be_), bh_["w"], bh_["h"])
    bw, bh = bnd[1][1], bnd[1][2]                      # полоса имени (CASLXTRA)
    # union-rect угловых марок (позиции buildinginfo.cpp:380-399)
    x1 = fw - 4 + 1
    x0 = min(fw - 5 - mdim[1][1], fw - 5 + 1 - mdim[2][1], fw - 5 + 1 - mdim[3][1]) - 1
    y1 = 58
    y0 = min(58 - 2 - mdim[1][2], 58 - 2 - mdim[2][2], 58 - 3 - mdim[3][2]) - 1
    cw_, ch_ = x1 - x0, y1 - y0
    band_patches, corner_patches = [], []
    for (sx, sy, idx, name, key) in CONSTRUCT_SLOTS:
        cell = bytearray(frame_gi)                     # чистая клетка: frame + иконка (+1,+1)
        bh_i, be_i = cstl[idx]
        bgi = decode_icn_indices(bh_i, be_i)
        biw, bih = bh_i["w"], bh_i["h"]
        for r in range(bih):
            for c in range(biw):
                v = bgi[r * biw + c]
                if v != TRANSPARENT and r + 1 < fh and c + 1 < fw:
                    cell[(r + 1) * fw + (c + 1)] = v
        nw = _smalfont_width(agg, ent, name)
        variants = []
        for var in (0, 1, 2):
            strip = bytearray(bw * bh)
            if var == 0:                               # plain = полоса самой рамки (BUILT)
                for r in range(bh):
                    strip[r * bw:(r + 1) * bw] = cell[(58 + r) * fw + 0:(58 + r) * fw + bw]
            else:
                ggi, gw_, gh_ = bnd[var]
                for r in range(min(bh, gh_)):
                    strip[r * bw:(r + 1) * bw] = ggi[r * gw_:r * gw_ + bw]
            _draw_smalfont(strip, bw, bh, agg, ent, name, 68 - nw // 2, 3)   # имя y+61 = полоса+3
            variants.append(_pack_patch(_rect_runs(bytes(strip), bw, bh, construct_addr, sx, sy + 58)))
        band_patches.append(variants)
        cvars = []
        for var in (0, 1, 2, 3):
            crect = bytearray(cw_ * ch_)
            for r in range(ch_):
                crect[r * cw_:(r + 1) * cw_] = cell[(y0 + r) * fw + x0:(y0 + r) * fw + x1]
            if var:
                mg, mw_, mh_ = mdim[var]
                if var == 1:
                    px_, py_ = fw - 5 - mw_, 58 - 2 - mh_
                elif var == 2:
                    px_, py_ = fw - 5 + 1 - mw_, 58 - 2 - mh_
                else:
                    px_, py_ = fw - 5 + 1 - mw_, 58 - 3 - mh_
                for r in range(mh_):
                    for c in range(mw_):
                        v = mg[r * mw_ + c]
                        if v != TRANSPARENT:
                            crect[(py_ - y0 + r) * cw_ + (px_ - x0 + c)] = v
            cvars.append(_pack_patch(_rect_runs(bytes(crect), cw_, ch_, construct_addr, sx + x0, sy + y0)))
        corner_patches.append(cvars)
    return band_patches, corner_patches, (x0, y0)


def bake_buybuild(agg, ent):
    """Куски рамки диалога-попапа BUYBUILD.ICN (Dialog::NonFixedFrameBox, dialog_box.cpp:127):
    [0]=верх-право 144×99, [1]=середина-право 145×45 (тайл, crop y=10), [2]=низ-право 144×81,
    [4]=верх-лево 160×99, [5]=середина-лево 161×45, [6]=низ-лево 161×81. ICN-тень декодер
    выкидывает (0xC0→прозрачно) — тень рисуется АППАРАТНО (полупрозрачный rect, по решению юзера).
    Возвращает {frame: (bytes,w,h)}."""
    fr = read_icn(agg_entry(agg, ent, "BUYBUILD.ICN"))
    out = {}
    for i in (0, 1, 2, 4, 5, 6):
        h, e = fr[i]
        out[i] = (bytes(decode_icn_indices(h, e)), h["w"], h["h"])
    return out


def bake_army_plate(agg, ent):
    """Плита STRIP[4] (82×93, Knight, горы) под занятым слотом армбара — renderMonsterFrame (ui_monster.cpp:35).
    Native paletted (рисуется ×1.6 в DL через opaque-палитру). Возвращает (bytes, w, h)."""
    h, e = read_icn(agg_entry(agg, ent, "STRIP.ICN"))[4]
    gi = decode_icn_indices(h, e)
    return bytes(gi), h["w"], h["h"]


def bake_castle_name_banner(agg, ent, castle_name):
    """Плашка названия замка (drawCastleName ui_castle.cpp:303) как ОТДЕЛЬНЫЙ оверлей: TOWNNAME[0] (179×14)
    + имя smallWhite поверх (локальный y=2, т.к. баннер @248 / текст @250). Раньше пёкся в композит
    панорамы (640×256) и обрезался швом на y=256 («затёрт рамкой»); теперь — 3-й битмап Town_DL поверх
    панели, БЕЗ клипа. Прозрачная палитра (углы свитка idx0). Возвращает (bytes, w, h)."""
    tn_h, tn_e = read_icn(agg_entry(agg, ent, "TOWNNAME.ICN"))[0]
    tn_gi = decode_icn_indices(tn_h, tn_e)
    bw, bh = tn_h["w"], tn_h["h"]
    buf = bytearray([TRANSPARENT]) * (bw * bh)
    _blit_icn(buf, tn_gi, bw, bh, 0, 0, 0, 0, bw, bh)
    tnw = _smalfont_width(agg, ent, castle_name)
    _draw_smalfont(buf, bw, bh, agg, ent, castle_name, bw // 2 - tnw // 2, 2)
    return bytes(buf), bw, bh


def bake_construct_check(agg, ent):
    """Галочка TOWNWIND[11] ×1.6 прозрачная — оверлей «построено» на слот окна строительства (рантайм-постройка)."""
    h, e = read_icn(agg_entry(agg, ent, "TOWNWIND.ICN"))[11]
    gi = decode_icn_indices(h, e)
    return _prescale16(gi, h["w"], h["h"])         # (bytes, nw, nh)


def bake_garrison_monh(agg, ent):
    """6 MONH-портретов (recruit idx порядок), кадр 0, пред-масштаб ×1.6, прозрачная idx0. Для динам.слотов 2-4."""
    out = []
    for icn in GARRISON_MONH:
        h, e = read_icn(agg_entry(agg, ent, icn))[0]
        gi = decode_icn_indices(h, e)
        spr, nw, nh = _prescale16(gi, h["w"], h["h"])
        assert nw < 128, f"{icn} ×1.6 width {nw} >= 128"
        out.append((spr, nw, nh))
    return out


def build_payload(palette, town_img, strip_img, names_masks, font_masks, font_masks_big, recruit_win, monster_sprites, gold_icon, monh_sprites, construct_img, construct_check, army_plate, name_banner, buybuild):
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
    name_addrs = []                                              # маски имён удалены (hover = строки)
    font_addrs = [(put(m), w, h) for (m, w, h) in font_masks]    # [char-32]=(addr,w,h) SMALFONT
    big_font_addrs = [(put(m), w, h) for (m, w, h) in font_masks_big]  # [char-32]=(addr,w,h) FONT 14px (заголовок)
    while (TOWN_RAMG_BASE + len(payload)) % SECTOR:              # ★область найма — СЕКТОР-выровнена
        payload.append(0)                                        # с обеих сторон: в неё стримится РЫНОК,
    recruit_addr = put(recruit_win)                              # окно найма RECRBKG (один на все жилища)
    while (TOWN_RAMG_BASE + len(payload)) % SECTOR:              # рестрим RECRBKG идёт целыми секторами
        payload.append(0)
    spr_pal_addr = put(palette_argb4444(palette))                # палитра спрайтов: idx0 ПРОЗРАЧЕН
    mon_addrs = [(put(s), w, h) for (s, w, h) in monster_sprites]  # [recruit idx]=(addr,w,h)
    gs, gw, gh = gold_icon
    gold_addr = (put(gs), gw, gh)                                # иконка золота (цена-за-1)
    monh_addrs = [(put(s), w, h) for (s, w, h) in monh_sprites]  # [recruit idx]=(addr,w,h) MONH-портреты гарнизона
    while (TOWN_RAMG_BASE + len(payload)) % SECTOR:              # construct-область СЕКТОР-выровнена:
        payload.append(0)                                        # в неё стримится WELL, рестрим
    construct_addr = put(construct_img)                          # окно строительства (статичный кадр 640×461)
    while (TOWN_RAMG_BASE + len(payload)) % SECTOR:
        payload.append(0)
    cs, cw, ch = construct_check
    chk_addr = (put(cs), cw, ch)                                 # галочка «построено» (рантайм-оверлей)
    aps, apw, aph = army_plate
    plate_addr = (put(aps), apw, aph)                            # плита STRIP[4] под занятым слотом армбара
    nbs, nbw, nbh = name_banner
    banner_addr = (put(nbs), nbw, nbh)                           # плашка названия замка (оверлей поверх шва)
    bb_addrs = {i: (put(s), w, h) for i, (s, w, h) in buybuild.items()}  # куски рамки попапа BUYBUILD
    # (сюда же спец-ключами попадают "tav"/"ok0"/"ok1" — таверна, добавляются в buybuild в main)
    return (payload, pal_addr, img_addr, strip_addr, name_pal_addr, name_addrs, font_addrs, big_font_addrs,
            recruit_addr, spr_pal_addr, mon_addrs, gold_addr, monh_addrs, construct_addr, chk_addr, plate_addr, banner_addr, bb_addrs)


def emit_inc(pal_addr, img_addr, strip_addr, name_pal_addr, name_addrs, font_addrs, big_font_addrs, block_hit, pak,
             wrapped_descs, recruit_addr, spr_pal_addr, mon_addrs, gold_addr, monh_addrs, construct_addr, chk_addr, plate_addr, banner_addr, bb_addrs, statuses, cdata):
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
    # Плашка названия замка (drawCastleName рисуется ПОСЛЕДНИМ) — 3-й битмап ПОВЕРХ шва панорама/панель,
    # @ логич.(320-w/2, 248), БЕЗ клипа. Прозрачная палитра (углы свитка idx0 → просвет фона).
    (banner_a, nbw, nbh) = banner_addr
    L.append("                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG")
    L.append(f"                FT_BITMAP_SOURCE #{banner_a:06X}")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {nbw}, {nbh}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {nbw * 16 // 10}, {nbh * 16 // 10}")
    L.append(f"                FT_VERTEX2F {(320 - nbw // 2) * 256 // 10}, {248 * 256 // 10}")
    L.append("                FT_END")
    L.append("Town_DL_SIZE EQU $ - Town_DL")
    L.append("")
    # --- Окно строительства замка: статичный кадр CASLWIND-композита ×1.6 на весь экран ---
    L.append(f"CASTLE_CONSTRUCT_RAMG EQU #{construct_addr:06X}")
    L.append("Castle_Construct_DL:")
    L.append("                FT_CLEAR_COLOR_RGB 0, 0, 0")
    L.append("                FT_CLEAR 1, 1, 1")
    L.append("                FT_SCISSOR_XY 0, 0")
    L.append("                FT_SCISSOR_SIZE 1024, 768")
    L.append("                FT_COLOR_RGB 255, 255, 255")
    L.append("                FT_COLOR_A 255")
    L.append("                FT_BITMAP_HANDLE 0")
    L.append("                FT_CELL 0")
    L.append("                FT_BITMAP_TRANSFORM_A 160")
    L.append("                FT_BITMAP_TRANSFORM_B 0")
    L.append("                FT_BITMAP_TRANSFORM_C 0")
    L.append("                FT_BITMAP_TRANSFORM_D 0")
    L.append("                FT_BITMAP_TRANSFORM_E 160")
    L.append("                FT_BITMAP_TRANSFORM_F 0")
    L.append("                FT_VERTEX_TRANSLATE_X 0")
    L.append("                FT_VERTEX_TRANSLATE_Y 0")
    L.append("                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA")
    L.append("                FT_BITMAP_LAYOUT_H 0, 0")
    # CASLWIND 640×461: ширина 640>511 → нужны высокие биты SIZE_H (иначе клип в &511)
    L.append(f"                FT_BITMAP_SIZE_H {CONSTRUCT_W * 16 // 10}, {CONSTRUCT_H * 16 // 10}")
    L.append("                FT_PALETTE_SOURCE TOWN_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    L.append("                FT_BITMAP_SOURCE CASTLE_CONSTRUCT_RAMG")
    L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {CONSTRUCT_W}, {CONSTRUCT_H}")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {CONSTRUCT_W * 16 // 10}, {CONSTRUCT_H * 16 // 10}")
    L.append("                FT_VERTEX2F 0, 0")
    L.append("                FT_END")
    L.append("Castle_Construct_DL_SIZE EQU $ - Castle_Construct_DL")
    # Хит-рект EXIT окна строительства (native ×1.6 → логич.640×480 клик-координаты Input_Mouse)
    cex, cey, cew, ceh = CONSTRUCT_EXIT
    L.append(f"CONSTRUCT_EXIT_X0    EQU {cex}")
    L.append(f"CONSTRUCT_EXIT_X1    EQU {cex + cew}")
    L.append(f"CONSTRUCT_EXIT_Y0    EQU {cey}")
    L.append(f"CONSTRUCT_EXIT_Y1    EQU {cey + ceh}")
    # --- Рантайм-постройка зданий (BuyBuilding): на слот — стоимость золота, флаг «доступно»,
    # хит-рект (native=логич.), позиция галочки. Начальная маска = построенные (BUILT). ---
    ca, cw_, ch_ = chk_addr
    L.append(f"CONSTRUCT_CHK_RAMG   EQU #{ca:06X}")
    L.append("ConstructChkRec: DEFB "
             f"#{ca & 0xFF:02X}, #{(ca >> 8) & 0xFF:02X}, #{(ca >> 16) & 0xFF:02X}, {cw_}, {ch_}")
    # slot i: cost(DW), buildable(DB 1=ALLOW), hitX(DW native), hitY(DW), chkVX/chkVY (vertex ×1.6)
    import dump_mp2_castles
    fw_c = 137
    init_mask = 0
    L.append("ConstructCostGold:                     ; [slot] → стоимость золота (BuyBuilding KNGT)")
    for i, (sx, sy, idx, name, key) in enumerate(CONSTRUCT_SLOTS):
        gold = 0
        if key in dump_mp2_castles.KNGT_COST:
            gold = dump_mp2_castles.KNGT_COST[key][0]
        L.append(f"                DW {gold}")
        if statuses.get(key) == "BUILT":
            init_mask |= (1 << i)
    L.append("ConstructBuildable:                    ; [slot] → 1 если можно строить сразу (ALLOW), иначе 0")
    L.append("                DEFB " + ", ".join(("1" if statuses.get(s[4]) == "ALLOW" else "0") for s in CONSTRUCT_SLOTS))
    L.append("ConstructInitBuilt:                    ; [slot] → 1 если построено на старте (BUILT) — копир. в BuiltRuntime")
    L.append("                DEFB " + ", ".join(("1" if statuses.get(s[4]) == "BUILT" else "0") for s in CONSTRUCT_SLOTS))
    L.append("ConstructDisable:                      ; [slot] → 1 = вечный DISABLE (запечён серым, рантайм пропускает)")
    L.append("                DEFB " + ", ".join(("1" if statuses.get(s[4]) == "DISABLE" else "0") for s in CONSTRUCT_SLOTS))
    L.append("ConstructHitX:                         ; [slot] → левый X ячейки (native=логич.)")
    L.append("                DW " + ", ".join(str(s[0]) for s in CONSTRUCT_SLOTS))
    L.append("ConstructHitY:                         ; [slot] → верхний Y ячейки")
    L.append("                DW " + ", ".join(str(s[1]) for s in CONSTRUCT_SLOTS))
    # галочка (native 16×15): area.x+fw-5-16, area.y+58-2-15 (buildinginfo.cpp:382) → ×1.6 vertex
    L.append("ConstructChkVX:                        ; [slot] → X галочки (vertex ×1.6)")
    L.append("                DW " + ", ".join(str(round((s[0] + fw_c - 5 - 16) * 1.6) * 16) for s in CONSTRUCT_SLOTS))
    L.append("ConstructChkVY:                        ; [slot] → Y галочки (vertex ×1.6)")
    L.append("                DW " + ", ".join(str(round((s[1] + 58 - 2 - 15) * 1.6) * 16) for s in CONSTRUCT_SLOTS))
    L.append(f"CONSTRUCT_INIT_MASK  EQU #{init_mask:05X}         ; начально построенные слоты (BUILT)")
    L.append(f"CONSTRUCT_SLOT_W     EQU {fw_c}")
    L.append(f"CONSTRUCT_SLOT_H     EQU 70")
    # Живое золото в панели ресурсов окна строительства (drawResourcePanel: rx552, offY[3]=124, goldH~25).
    L.append(f"CONSTRUCT_GOLD_CX    EQU {round(593 * 1.6)}")      # центр ячейки золота (rx552+41, центрируется)
    L.append(f"CONSTRUCT_GOLD_VY    EQU {round(412 * 1.6) * 16}")
    L.append("")
    # ============================================================
    # СТРОИТЕЛЬСТВО ПО ОРИГИНАЛУ: полные стоимости (7 ресурсов), prereq-маски,
    # сектора патчей (панорама/бенды/углы), live-позиции чисел ресурсов.
    # ============================================================
    # Полная стоимость BuyBuilding (PaymentConditions, buildinginfo.cpp:139+):
    # 7×DW на слот в порядке gold,wood,mercury,ore,sulfur,crystal,gems.
    L.append("ConstructCostFull:                     ; [slot*14] → 7×DW (gold,wood,merc,ore,sulf,cryst,gems)")
    for (sx, sy, idx, name, key) in CONSTRUCT_SLOTS:
        cost = dump_mp2_castles.KNGT_COST.get(key, (0,) * 7)
        L.append("                DW " + ", ".join(str(c) for c in cost))
    # Prereq-маска (getBuildingRequirement): бит i = CONSTRUCT_SLOTS[i] должен быть построен.
    key2slot = {s[4]: i for i, s in enumerate(CONSTRUCT_SLOTS)}
    L.append("ConstructReqMask:                      ; [slot*3] → 3Б маска prereq-слотов (LE)")
    for (sx, sy, idx, name, key) in CONSTRUCT_SLOTS:
        m = 0
        for r in dump_mp2_castles.KNGT_REQ.get(key, []):
            m |= 1 << key2slot[r]
        L.append(f"                DEFB #{m & 0xFF:02X}, #{(m >> 8) & 0xFF:02X}, #{(m >> 16) & 0xFF:02X}")
    # Слот стройки → z-индекс панорамного здания (KNIGHT_BUILDING_KEYS), 255 = нет спрайта.
    pano_of_key = {k: z for z, k in enumerate(KNIGHT_BUILDING_KEYS)}
    L.append("SlotToPano:                            ; [slot] → z-индекс панорамы (255=нет)")
    L.append("                DEFB " + ", ".join(str(pano_of_key.get(s[4], 255)) for s in CONSTRUCT_SLOTS))
    L.append("PanoToSlot:                            ; [z] → слот стройки (255=нет: CASTLE/CAPTAIN)")
    L.append("                DEFB " + ", ".join(str(key2slot.get(k, 255)) for k in KNIGHT_BUILDING_KEYS))
    # BBox панорамных зданий (native, клип 640×256) — runtime hit-test построенных в рантайме
    # (TownHitMap запечён только для стартовых; новые здания ловятся bbox-ами в ОБРАТНОМ z).
    L.append("PanoBBoxX0:     DW " + ", ".join(str(b[0]) for b in cdata["pano_bboxes"]))
    L.append("PanoBBoxY0:     DW " + ", ".join(str(b[1]) for b in cdata["pano_bboxes"]))
    L.append("PanoBBoxX1:     DW " + ", ".join(str(b[2]) for b in cdata["pano_bboxes"]))
    L.append("PanoBBoxY1:     DW " + ", ".join(str(b[3]) for b in cdata["pano_bboxes"]))
    # Сектора патчей (АБСОЛЮТНЫЕ от начала HMM2TOWN.PAK; патч читается до маркера #FFFF).
    pb = cdata["patch_base"]
    L.append(f"PATCH_BASE_SEC       EQU {pb}")
    L.append("PanoPatchSec:                          ; [z] → сектор ран-патча спрайта здания")
    L.append("                DW " + ", ".join(str(pb + s) for s in cdata["pano_sec"]))
    L.append("BandPatchSec:                          ; [slot*3 + вариант] 0=plain(BUILT) 1=green(ALLOW) 2=red")
    for vs in cdata["band_sec"]:
        L.append("                DW " + ", ".join(str(pb + s) for s in vs))
    L.append("CornerPatchSec:                        ; [slot*4 + вариант] 0=clean 1=check 2=deny 3=money")
    for vs in cdata["corner_sec"]:
        L.append("                DW " + ", ".join(str(pb + s) for s in vs))
    # Live-числа 6 ресурсов (кроме золота) на панелях: центр колонки native → экранные px/vertex.
    # Порядок = KingdomRes6: wood,mercury,ore,sulfur,crystal,gems. Town: колонки 553/594 (strip),
    # ряды strip-y 6+offY+33; Construct: те же колонки, ряды 262+offY+33 (оба native-набора идентичны
    # по X; town Y в координатах экрана = 256+strip-y).
    offY = [0, 32 + 9 + 2, (32 + 9) * 2 - 1, (32 + 9) * 3 + 1]
    lc, rc = 553, 594
    res_pos = {"wood": (lc, 0), "mercury": (rc, 1), "ore": (lc, 2),
               "sulfur": (rc, 0), "crystal": (lc, 1), "gems": (rc, 2)}
    order = ("wood", "mercury", "ore", "sulfur", "crystal", "gems")
    L.append("TownResCX:                             ; [res] центр колонки (экран px), город")
    L.append("                DW " + ", ".join(str(round((res_pos[r][0] + 19.5) * 1.6)) for r in order))
    L.append("TownResVY:                             ; [res] vertex Y, город (панель @256)")
    L.append("                DW " + ", ".join(str(round((256 + 6 + offY[res_pos[r][1]] + 33) * 1.6) * 16) for r in order))
    L.append("ConResCX:                              ; [res] центр колонки, окно стройки")
    L.append("                DW " + ", ".join(str(round((res_pos[r][0] + 19.5) * 1.6)) for r in order))
    L.append("ConResVY:                              ; [res] vertex Y, окно стройки (панель @262)")
    L.append("                DW " + ", ".join(str(round((262 + offY[res_pos[r][1]] + 33) * 1.6) * 16) for r in order))
    L.append("StartRes6:                             ; стартовые 6 ресурсов (Resources_InitStart порядок res6)")
    L.append("                DW " + ", ".join(str(START_FUNDS[r]) for r in order))
    # Индексы слотов для экономики дня (доход Statue, рост жилищ Well/Wel2) + recruit→слот.
    L.append(f"CONSTRUCT_STATUE_SLOT EQU {key2slot['STATUE']}")
    L.append(f"CONSTRUCT_WELL_SLOT  EQU {key2slot['WELL']}")
    L.append(f"CONSTRUCT_WEL2_SLOT  EQU {key2slot['WEL2']}")
    L.append("RecruitToSlot:                         ; [recruit idx 0..5] → слот стройки DW1..DW6")
    L.append("                DEFB " + ", ".join(str(key2slot[f"DW{i}"]) for i in range(1, 7)))
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
    # TownHitMap (2.5К) — НА DATA-СТРАНИЦУ #91 (оверлей города упёрся в 16К): отдельный inc,
    # включается в GlobalData-блок main.asm; чтение — резидентный GData_ReadByte.
    HL = ["; Сгенерировано town_pack.py — хит-карта города для GLOBAL_DATA-страницы (#91).",
          "GDTownHitMap:                          ; блок 8x8 → индекс здания (1-based; 0=фон)"]
    for r in range(bh_n):
        row = block_hit[r * bw_n:(r + 1) * bw_n]
        HL.append("                DEFB " + ", ".join(str(b) for b in row))
    (TOWN_INC.parent / "generated_town_hit.inc").write_text("\n".join(HL), encoding="utf-8")
    # (Пре-рендер масок имён удалён: hover-имя рисуется динамически строкой TownNameStrTab —
    #  экономия ~28КБ RAM_G; маски >127px ломали DrawSpriteEntry.)
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
    L.append("BigFontGlyphTab:                       ; [char-32] → глиф FONT 14px [lo,mid,hi,w,h] (заголовок)")
    for (addr, w, h) in big_font_addrs:
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
    # --- Окно инфо-попапа = ТОЧНО Dialog::NonFixedFrameBox (dialog_box.cpp): куски BUYBUILD
    # (верх 4|0, середина-тайл 5|1 crop y=10 чанками ≤35, низ 6|2), стык x=320, windowWidth 288,
    # интерьер boxAreaWidthPx 244 @ x=198, textOffsetY=10. Заголовок normalYellow, тело normalWhite
    # (оба FONT/BigFont). Высота = 26(header)+bodyH+10; middleH=max(0,h-70). Тень — АППАРАТНАЯ
    # (полупрозр. rect, сдвиг −5,+5 native, как у окна найма; ICN-тень декодер выкидывает).
    # DL-блоки ДЕДУП по уникальной высоте (bodyH), [idx]→блок через таблицу.
    V = lambda v: round(v * 1.6 * 16)                 # native → суб-пиксельный vertex (урок выравнивания)
    INFO_LINEH_N = 16                                 # шаг строк FONT (native)
    hdrH = INFO_LINEH_N + 10                          # headerHeight (ui_dialog.cpp:104)
    tw0, th0 = bb_addrs[0][1], bb_addrs[0][2]         # верх-право 144×99
    bw2, bh2 = bb_addrs[2][1], bb_addrs[2][2]         # низ-право 144×81
    uniq = {}                                          # midH → (метка, pos_y, midH)
    per_idx = []                                       # [idx] → (метка, titleVY, line0VY, shadY0, shadY1)
    for lines in wrapped_descs:
        bodyH = max(1, len(lines)) * INFO_LINEH_N
        overall = hdrH + bodyH + 10                   # overallTextHeight (без кнопок)
        midH = 0 if overall <= 70 else overall - 70
        pos_y = (480 - midH) // 2 - th0
        area_y = pos_y + th0 - 35
        key = midH
        if key not in uniq:
            uniq[key] = (f"TownInfoDL_{len(uniq)}", pos_y, midH)
        lbl, _, _ = uniq[key]
        per_idx.append((lbl, V(area_y + 10), V(area_y + 10 + hdrH)))
    for key, (lbl, pos_y, midH) in uniq.items():
        y_bot = pos_y + th0 + midH
        # ★Куски тайлятся ВСТЫК по ЦЕЛЫМ экранным швам (высота куска = шов_след − шов_этот):
        # суб-пиксельное округление высот давало щель 0.4px («чёрная горизонтальная линия»).
        pieces = []                                    # (fi, right_side, ys, hs, src_off)
        s_top = round(pos_y * 1.6)
        s_mid = round((pos_y + th0) * 1.6)
        pieces.append((4, False, s_top, s_mid - s_top, 0))
        pieces.append((0, True, s_top, s_mid - s_top, 0))
        y = pos_y + th0
        ys = s_mid
        rem = midH
        while rem > 0:                                  # середина чанками ≤35 (crop src y=10)
            ch = min(35, rem)
            ye = round((y + ch) * 1.6)
            pieces.append((5, False, ys, ye - ys, 10 * bb_addrs[5][1]))
            pieces.append((1, True, ys, ye - ys, 10 * bb_addrs[1][1]))
            y += ch
            ys = ye
            rem -= ch
        s_end = round((y_bot + bh2) * 1.6)
        pieces.append((6, False, ys, s_end - ys, 0))
        pieces.append((2, True, ys, s_end - ys, 0))

        def emit_piece(fi, right_side, ys, hs, src_off):
            a, w, h = bb_addrs[fi]
            sw = round(w * 1.6)
            xs = 512 if right_side else 512 - sw          # стык половин ровно на 512 (=320 native)
            L.append(f"                FT_BITMAP_SOURCE #{a + src_off:06X}")
            L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {w}, {h}")
            L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {sw}, {hs}")
            L.append(f"                FT_VERTEX2F {xs * 16}, {ys * 16}")
        # ОДИН проход кусков; тень рисуется ГЛОБАЛЬНОЙ Render_WindowShadowDL (этот же DL чёрным
        # со сдвигом −8,+8 через VERTEX_TRANSLATE — силуэт из alpha кусков, резной гребень честно).
        L.append(f"{lbl}:                        ; попап BUYBUILD, middleH={midH}")
        L.append("                FT_BITMAP_TRANSFORM_A 160")
        L.append("                FT_BITMAP_TRANSFORM_B 0")
        L.append("                FT_BITMAP_TRANSFORM_C 0")
        L.append("                FT_BITMAP_TRANSFORM_D 0")
        L.append("                FT_BITMAP_TRANSFORM_E 160")
        L.append("                FT_BITMAP_TRANSFORM_F 0")
        L.append("                FT_BITMAP_LAYOUT_H 0, 0")
        L.append("                FT_BITMAP_SIZE_H 0, 0")
        L.append("                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG")
        L.append("                FT_BEGIN FT_BITMAPS")
        for p in pieces:
            emit_piece(*p)
        L.append("                FT_END")
        L.append(f"{lbl}_SIZE EQU $ - {lbl}")
    L.append("TownInfoDLTab:                         ; [idx-1] → DW addr, DW size (окно по высоте текста)")
    for rec in per_idx:
        L.append(f"                DW {rec[0]}, {rec[0]}_SIZE")
    L.append("TownInfoTitleVY:                       ; [idx-1] → vertex Y заголовка (area.y+10)")
    L.append("                DW " + ", ".join(str(r[1]) for r in per_idx))
    L.append("TownInfoLine0VY:                       ; [idx-1] → vertex Y первой строки (заголовок+26)")
    L.append("                DW " + ", ".join(str(r[2]) for r in per_idx))
    L.append(f"TOWN_INFO_LINE_H     EQU {V(INFO_LINEH_N)}          ; шаг строк (16 native ×1.6, vertex)")
    L.append("")
    # --- ТАВЕРНА (castle_tavern.cpp:_openTavern = showStandardTextMessage OK):
    #     NonFixedFrameBox + заголовок «Tavern» + TAVWIN-композит + intro + слух недели +
    #     кнопка OKAY (SYSTEM 1/2). Высота per слух (те же куски BUYBUILD). ---
    tav_a, tav_w, tav_h = bb_addrs["tav"]
    ok_a0, ok_w, ok_h = bb_addrs["ok0"]
    ok_a1, _, _ = bb_addrs["ok1"]
    intro_lines = pak["tavern_intro"]
    rum_wrapped = pak["tavern_rumors"]
    L.append("TavernIntroBlk:                        ; вступление (константа, FONT белый)")
    for ln in intro_lines:
        L.append(f'                DEFB "{ln}", 0')
    L.append("                DEFB 0")
    L.append("TavernRumorTab:                        ; [неделя mod 7] → блок строк слуха")
    for i in range(len(rum_wrapped)):
        L.append(f"                DW TavernRumBlk_{i}")
    for i, lines in enumerate(rum_wrapped):
        L.append(f"TavernRumBlk_{i}:")
        for ln in lines:
            L.append(f'                DEFB "{ln}", 0')
        L.append("                DEFB 0")
    tuniq = {}
    tav_per = []                                       # per rumor: (lbl, titleVY, introVY, rumVY, okHitY0)
    for lines in rum_wrapped:
        bodyH = tav_h + 8 + (len(intro_lines) + 1 + len(lines)) * INFO_LINEH_N
        overall = hdrH + bodyH + 10 + ok_h + 10        # + кнопка OKAY
        midH = 0 if overall <= 70 else overall - 70
        pos_y = (480 - midH) // 2 - th0
        area_y = pos_y + th0 - 35
        tav_y = area_y + 10 + hdrH                     # верх TAVWIN
        intro_y = tav_y + tav_h + 8
        rum_y = intro_y + (len(intro_lines) + 1) * INFO_LINEH_N
        ok_y = rum_y + len(lines) * INFO_LINEH_N + 10
        if midH not in tuniq:
            lbl = f"TavernDL_{len(tuniq)}"
            tuniq[midH] = (lbl, pos_y, midH, tav_y, ok_y)
        tav_per.append((tuniq[midH][0], V(area_y + 10), V(intro_y), V(rum_y), ok_y))
    for midH, (lbl, pos_y, midH_, tav_y, ok_y) in tuniq.items():
        y_bot = pos_y + th0 + midH_
        pieces = []
        s_top = round(pos_y * 1.6)
        s_mid = round((pos_y + th0) * 1.6)
        pieces.append((4, False, s_top, s_mid - s_top, 0))
        pieces.append((0, True, s_top, s_mid - s_top, 0))
        y = pos_y + th0
        ys = s_mid
        rem = midH_
        while rem > 0:
            ch = min(35, rem)
            ye = round((y + ch) * 1.6)
            pieces.append((5, False, ys, ye - ys, 10 * bb_addrs[5][1]))
            pieces.append((1, True, ys, ye - ys, 10 * bb_addrs[1][1]))
            y += ch
            ys = ye
            rem -= ch
        s_end = round((y_bot + bh2) * 1.6)
        pieces.append((6, False, ys, s_end - ys, 0))
        pieces.append((2, True, ys, s_end - ys, 0))
        L.append(f"{lbl}:                        ; окно таверны, middleH={midH_}")
        L.append("                FT_BITMAP_TRANSFORM_A 160")
        L.append("                FT_BITMAP_TRANSFORM_B 0")
        L.append("                FT_BITMAP_TRANSFORM_C 0")
        L.append("                FT_BITMAP_TRANSFORM_D 0")
        L.append("                FT_BITMAP_TRANSFORM_E 160")
        L.append("                FT_BITMAP_TRANSFORM_F 0")
        L.append("                FT_BITMAP_LAYOUT_H 0, 0")
        L.append("                FT_BITMAP_SIZE_H 0, 0")
        L.append("                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG")
        L.append("                FT_BEGIN FT_BITMAPS")
        for p in pieces:
            a, w, h = bb_addrs[p[0]]
            sw = round(w * 1.6)
            xs = 512 if p[1] else 512 - sw
            L.append(f"                FT_BITMAP_SOURCE #{a + p[4]:06X}")
            L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {w}, {h}")
            L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {sw}, {p[3]}")
            L.append(f"                FT_VERTEX2F {xs * 16}, {p[2] * 16}")
        # TAVWIN-композит (центр) + кнопка OKAY (отжата; нажатая — отдельный оверлей-фрагмент)
        tvx = 320 - tav_w // 2
        L.append(f"                FT_BITMAP_SOURCE #{tav_a:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {tav_w}, {tav_h}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {round(tav_w * 1.6)}, {round(tav_h * 1.6)}")
        L.append(f"                FT_VERTEX2F {V(tvx)}, {V(tav_y)}")
        okx = 320 - ok_w // 2
        L.append(f"                FT_BITMAP_SOURCE #{ok_a0:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {ok_w}, {ok_h}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {round(ok_w * 1.6)}, {round(ok_h * 1.6)}")
        L.append(f"                FT_VERTEX2F {V(okx)}, {V(ok_y)}")
        L.append("                FT_END")
        L.append(f"{lbl}_SIZE EQU $ - {lbl}")
        # нажатое состояние кнопки — фрагмент поверх (копируется при удержании ЛКМ в зоне)
        L.append(f"{lbl}_OkPress:")
        L.append("                FT_BEGIN FT_BITMAPS")
        L.append(f"                FT_BITMAP_SOURCE #{ok_a1:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {ok_w}, {ok_h}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {round(ok_w * 1.6)}, {round(ok_h * 1.6)}")
        L.append(f"                FT_VERTEX2F {V(okx)}, {V(ok_y)}")
        L.append("                FT_END")
        L.append(f"{lbl}_OkPress_SIZE EQU $ - {lbl}_OkPress")
    L.append("TavernDLTab:                           ; [неделя mod 7] → DW DL, DW size, DW press, DW psize")
    for rec in tav_per:
        L.append(f"                DW {rec[0]}, {rec[0]}_SIZE, {rec[0]}_OkPress, {rec[0]}_OkPress_SIZE")
    L.append("TavernTitleVY:                         ; [rumor] → vertex Y заголовка «Tavern»")
    L.append("                DW " + ", ".join(str(r[1]) for r in tav_per))
    L.append("TavernIntroVY:                         ; [rumor] → vertex Y первой строки вступления")
    L.append("                DW " + ", ".join(str(r[2]) for r in tav_per))
    L.append("TavernRumorVY:                         ; [rumor] → vertex Y первой строки слуха")
    L.append("                DW " + ", ".join(str(r[3]) for r in tav_per))
    L.append("TavernOkHitY0:                         ; [rumor] → лог. Y верх кнопки OKAY (hit-зона, DW)")
    L.append("                DW " + ", ".join(str(r[4]) for r in tav_per))
    L.append(f"TAVERN_OK_X0         EQU {320 - ok_w // 2}   ; hit-зона OKAY (лог.)")
    L.append(f"TAVERN_OK_X1         EQU {320 - ok_w // 2 + ok_w}")
    L.append(f"TAVERN_OK_H          EQU {ok_h}")
    L.append(f"TAVERN_RUMOR_COUNT   EQU {len(rum_wrapped)}")
    L.append(f"TAV_TAIL_SECTOR      EQU {pak['tav_tail_sector']}   ; хвост (TAVWIN+OKAY) в PAK")
    L.append(f"TAV_TAIL_SECTORS     EQU {pak['tav_tail_sectors']}")
    L.append(f"TAV_TAIL_BASE        EQU #{pak['tav_tail_base']:06X} ; RAM_G ЗА курсором (#F8000..#100000)")
    L.append("")
    # --- РЫНОК (Dialog::Marketplace, dialog_marketplace.cpp): FrameBox 297 + сетки from/to +
    #     торг-зона + TRADE/EXIT. Ассеты TRADPOST стримятся в область найма (mk_addrs).
    #     GIFT не рисуем: дизейблнута при <2 игроках (у нас всегда) — совместимо с ориг. ---
    mk = pak["mk_addrs"]
    MK_BODY = 297
    mk_overall = hdrH + MK_BODY + 10
    mk_midH = mk_overall - 70
    mk_pos_y = (480 - mk_midH) // 2 - th0
    mk_area_y = mk_pos_y + th0 - 35
    MKX = 198                                          # area x (интерьер 244)
    L.append(f"MK_SECTOR            EQU {pak['mk_sector']}     ; ассеты рынка в PAK (стрим в область найма)")
    L.append(f"MK_SECTORS           EQU {pak['mk_sectors']}")
    L.append(f"RECR_SECTOR          EQU {pak['recruit_sector']}   ; RECRBKG в payload (рестрим после рынка)")
    L.append(f"RECR_SECTORS         EQU {pak['recruit_sectors']}")
    grid = [(0, 0), (37, 0), (74, 0), (0, 37), (37, 37), (74, 37), (37, 74)]
    y_bot = mk_pos_y + th0 + mk_midH
    pieces = []
    s_top = round(mk_pos_y * 1.6)
    s_mid = round((mk_pos_y + th0) * 1.6)
    pieces.append((4, False, s_top, s_mid - s_top, 0))
    pieces.append((0, True, s_top, s_mid - s_top, 0))
    y = mk_pos_y + th0
    ys = s_mid
    rem = mk_midH
    while rem > 0:
        ch = min(35, rem)
        ye = round((y + ch) * 1.6)
        pieces.append((5, False, ys, ye - ys, 10 * bb_addrs[5][1]))
        pieces.append((1, True, ys, ye - ys, 10 * bb_addrs[1][1]))
        y += ch
        ys = ye
        rem -= ch
    s_end = round((y_bot + bh2) * 1.6)
    pieces.append((6, False, ys, s_end - ys, 0))
    pieces.append((2, True, ys, s_end - ys, 0))
    L.append("Market_DL:                             ; окно рынка: рамка + сетки + кнопки (отжатые)")
    L.append("                FT_BITMAP_TRANSFORM_A 160")
    L.append("                FT_BITMAP_TRANSFORM_B 0")
    L.append("                FT_BITMAP_TRANSFORM_C 0")
    L.append("                FT_BITMAP_TRANSFORM_D 0")
    L.append("                FT_BITMAP_TRANSFORM_E 160")
    L.append("                FT_BITMAP_TRANSFORM_F 0")
    L.append("                FT_BITMAP_LAYOUT_H 0, 0")
    L.append("                FT_BITMAP_SIZE_H 0, 0")
    L.append("                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG")
    L.append("                FT_BEGIN FT_BITMAPS")
    for p in pieces:
        a, w, h = bb_addrs[p[0]]
        sw = round(w * 1.6)
        xs = 512 if p[1] else 512 - sw
        L.append(f"                FT_BITMAP_SOURCE #{a + p[4]:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {w}, {h}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {sw}, {p[3]}")
        L.append(f"                FT_VERTEX2F {xs * 16}, {p[2] * 16}")

    def mkspr(fr, nx, ny):
        a, w, h = mk[fr]
        L.append(f"                FT_BITMAP_SOURCE #{a:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {w}, {h}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {round(w * 1.6)}, {round(h * 1.6)}")
        L.append(f"                FT_VERTEX2F {V(nx)}, {V(ny)}")
    for i, (gx, gy) in enumerate(grid):                # обе сетки ресурсов (иконки статичны)
        mkspr(7 + i, MKX + gx, mk_area_y + 190 + gy)
        mkspr(7 + i, MKX + 136 + gx, mk_area_y + 190 + gy)
    mkspr(3, MKX + 11, mk_area_y + 129)                # стрелка влево (отжата)
    mkspr(5, MKX + 220, mk_area_y + 129)               # стрелка вправо (отжата)
    mkspr(15, MKX + 74, mk_area_y + 150)               # TRADE (отжата)
    mkspr(17, MKX + 68 + 74, mk_area_y + MK_BODY - 25) # EXIT (отжата)
    L.append("                FT_END")
    L.append("Market_DL_SIZE EQU $ - Market_DL")
    # нажатые состояния кнопок — мини-фрагменты поверх
    for lbl, fr, nx, ny in (("MkArrLPress", 4, MKX + 11, mk_area_y + 129),
                            ("MkArrRPress", 6, MKX + 220, mk_area_y + 129),
                            ("MkTradePress", 16, MKX + 74, mk_area_y + 150),
                            ("MkExitPress", 18, MKX + 68 + 74, mk_area_y + MK_BODY - 25)):
        L.append(f"Market_{lbl}_DL:")
        L.append("                FT_BEGIN FT_BITMAPS")
        mkspr(fr, nx, ny)
        L.append("                FT_END")
        L.append(f"Market_{lbl}_DL_SIZE EQU $ - Market_{lbl}_DL")
    # рамка выбора [14] 38×38 (на rect−2), торг-зона: обмен-стрелки [0], слайдер [1]/[2]
    for lbl, fr in (("MkSel", 14), ("MkFromTo", 0), ("MkBar", 1), ("MkSlider", 2)):
        a, w, h = mk[fr]
        L.append(f"Market_{lbl}_DL:                       ; SOURCE+LAYOUT+SIZE (vertex добавляет Z80)")
        L.append(f"                FT_BITMAP_SOURCE #{a:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {w}, {h}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {round(w * 1.6)}, {round(h * 1.6)}")
        L.append(f"Market_{lbl}_DL_SIZE EQU $ - Market_{lbl}_DL")
    # иконка ресурса торг-зоны: LAYOUT/SIZE 34×34 общие (SOURCE пишет Z80 по ресурсу)
    L.append("Market_ResIconLay_DL:")
    L.append("                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34")
    L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {round(34 * 1.6)}, {round(34 * 1.6)}")
    L.append("Market_ResIconLay_DL_SIZE EQU $ - Market_ResIconLay_DL")
    L.append("MarketResSrcTab:                       ; [res] → DW адрес иконки TRADPOST[7+res]")
    L.append("                DW " + ", ".join(f"#{mk[7 + i][0] & 0xFFFF:04X}" for i in range(7)))
    L.append("MarketResSrcHiTab:                     ; [res] → DB старший байт адреса")
    L.append("                DB " + ", ".join(f"#{mk[7 + i][0] >> 16:02X}" for i in range(7)))
    # --- позиции/зоны (лог. коорд.) ---
    L.append(f"MK_TITLE_VY          EQU {V(mk_area_y + 10)}   ; «Marketplace» жёлтым, центр 320")
    L.append(f"MK_GRID_FROM_X       EQU {MKX}")
    L.append(f"MK_GRID_TO_X         EQU {MKX + 136}")
    L.append(f"MK_GRID_Y            EQU {mk_area_y + 190}")
    L.append("MarketGridOfs:                         ; 7 × (dx, dy) DEFB — раскладка 3×3")
    for gx, gy in grid:
        L.append(f"                DEFB {gx}, {gy}")
    L.append(f"MK_QTY_VY            EQU {V(mk_area_y + 128 - 14)} ; число qty над слайдером (центр 320)")
    L.append(f"MK_MSG_VY            EQU {V(mk_area_y + 32)}   ; строка «I can offer you …»")
    L.append(f"MK_MSG2_VY           EQU {V(mk_area_y + 32 + 16)}")
    L.append(f"MK_ICON_FROM_VX      EQU {V(MKX + (244 - 34 + 1) // 2 - 70)}  ; иконка from (низ y+115)")
    L.append(f"MK_ICON_TO_VX        EQU {V(MKX + (244 - 34 + 1) // 2 + 70)}")
    L.append(f"MK_ICON_VY           EQU {V(mk_area_y + 115 - 34)}")
    L.append(f"MK_FROMTO_VX         EQU {V(MKX + (244 - 43) // 2)}   ; обмен-стрелки [0] 43×16 @ y+90")
    L.append(f"MK_FROMTO_VY         EQU {V(mk_area_y + 90)}")
    L.append(f"MK_BAR_VX            EQU {V(MKX + (244 - 230) // 2 - 2)} ; слайдер-полоса @ y+128")
    L.append(f"MK_BAR_VY            EQU {V(mk_area_y + 128)}")
    L.append(f"MK_SLIDER_Y          EQU {mk_area_y + 128 + 6}   ; лог. Y ползунка (по центру полосы)")
    L.append(f"MK_BAR_Y0            EQU {mk_area_y + 128}   ; лог. Y полосы (клик по полосе = set qty)")
    L.append(f"MK_MSG_X0            EQU {MKX + 2}   ; лево offer-текста")
    L.append(f"MK_SLIDER_X0         EQU {MKX + (244 - 230) // 2 - 2 + 3}  ; лог. X начала хода (187px)")
    L.append(f"MK_SELL_VX           EQU {V(MKX + 30)}   ; «-N (M)» под иконкой from (центр)")
    L.append(f"MK_BUY_VX            EQU {V(MKX + 214)}  ; «+N (M)» под иконкой to")
    L.append(f"MK_INFO_VY           EQU {V(mk_area_y + 116)}")
    # hit-зоны (лог.)
    L.append(f"MK_TRADE_X0          EQU {MKX + 74}")
    L.append(f"MK_TRADE_Y0          EQU {mk_area_y + 150}")
    L.append(f"MK_EXIT_X0           EQU {MKX + 68 + 74}")
    L.append(f"MK_EXIT_Y0           EQU {mk_area_y + MK_BODY - 25}")
    L.append("MK_BTN_W             EQU 96")
    L.append("MK_BTN_H             EQU 25")
    L.append(f"MK_ARRL_X0           EQU {MKX + 11}")
    L.append(f"MK_ARRR_X0           EQU {MKX + 220}")
    L.append(f"MK_ARR_Y0            EQU {mk_area_y + 129}")
    L.append("MK_ARR_WH            EQU 14")
    L.append(f"MK_MAX_Y0            EQU {mk_area_y + 80}    ; «Max» кнопка-текст (центр−5, шир~30)")
    L.append(f"MK_MIN_Y0            EQU {mk_area_y + 103}")
    L.append("MK_MAXMIN_X0         EQU 300")
    L.append("MK_MAXMIN_X1         EQU 340")
    L.append("MK_MAXMIN_H          EQU 12")
    # --- КУРСЫ (resource_trading.cpp, 1 рынок): [from7][to7] → DW (0=same). Ресурсы:
    #     0=wood 1=mercury 2=ore 3=sulfur 4=crystal 5=gems 6=gold (порядок сеток/иконок). ---
    common = {0, 2}
    rare = {1, 3, 4, 5}
    rate = [[0] * 7 for _ in range(7)]
    for f in range(7):
        for t in range(7):
            if f == t:
                continue
            if f == 6:
                rate[f][t] = 2500 if t in common else 5000
            elif t == 6:
                rate[f][t] = 25 if f in common else 50
            elif (f in common) == (t in common):
                rate[f][t] = 10
            elif f in common:
                rate[f][t] = 20
            else:
                rate[f][t] = 5
    L.append("MarketRateTab:                         ; [from*7+to] → DW курс (1 рынок; 0 = same)")
    for f in range(7):
        L.append("                DW " + ", ".join(str(rate[f][t]) for t in range(7)))
    L.append("")
    # --- WELL (castle_well.cpp): база в construct-область + патчи секций построенных +
    #     Available-числа (динамика) + EXIT (WELLXTRA) + подпись в статус-бар. ---
    L.append(f"WELL_SECTOR          EQU {pak['well_sector']}   ; база well в PAK (стрим в construct-область)")
    L.append(f"WELL_SECTORS         EQU {pak['well_sectors']}")
    L.append(f"CONSTRUCT_SECTOR     EQU {pak['construct_sector']}   ; рестрим construct после well")
    L.append(f"CONSTRUCT_SECTORS    EQU {pak['construct_sectors']}")
    pb_ = cdata["patch_base"]
    L.append("WellSecPatchSec:                       ; [DW1..DW6] → сектор патча секции")
    L.append("                DW " + ", ".join(str(pb_ + s) for s in pak["well_sec_secs"]))
    L.append("WellAvailCX:                           ; [i] → физ. центр числа Available")
    L.append("                DW " + ", ".join(str(round((ox + 129) * 1.6)) for ox, oy in WELL_SECT_OFS))
    L.append("WellAvailVY:                           ; [i] → vertex Y числа Available")
    L.append("                DW " + ", ".join(str(V(oy + 121)) for ox, oy in WELL_SECT_OFS))
    wx0a, ww_, wh_ = bb_addrs["wex0"]
    wx1a, _, _ = bb_addrs["wex1"]
    WEX_X, WEX_Y = 579, 461                            # EXIT в баре (отжатая ВБЕЙКАНА в базу)
    for lbl, a_ in (("WellExit0", wx0a), ("WellExit1", wx1a)):
        L.append(f"{lbl}_DL:")
        L.append("                FT_BEGIN FT_BITMAPS")
        L.append(f"                FT_BITMAP_SOURCE #{a_:06X}")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {ww_}, {wh_}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {round(ww_ * 1.6)}, {round(wh_ * 1.6)}")
        L.append(f"                FT_VERTEX2F {V(WEX_X)}, {V(WEX_Y)}")
        L.append("                FT_END")
        L.append(f"{lbl}_DL_SIZE EQU $ - {lbl}_DL")
    L.append(f"WELL_EXIT_X0         EQU {WEX_X}")
    L.append(f"WELL_EXIT_Y0         EQU {WEX_Y}")
    L.append(f"WELL_EXIT_W          EQU {ww_}")
    L.append(f"WELL_EXIT_H          EQU {wh_}")
    L.append('WellBarStr:          DEFB "Town Population Information and Statistics", 0')
    L.append("")
    # --- Диалог найма (Dialog::RecruitMonster): окно RECRBKG + статичные строки на монстра ---
    rsx = (1024 - round(RECR_W * 1.6)) // 2          # экран X окна (центр по горизонтали)
    rsy = (768 - round(RECR_H * 1.6)) // 2           # экран Y окна
    L.append(f"RECRUIT_WIN_RAMG     EQU #{recruit_addr:06X}")
    L.append("Recruit_Win_DL:                        ; окно найма RECRBKG ×1.6 по центру (тень — Render_WindowShadowDL)")
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
    B = RECR_BORDER
    L.append(f"RECR_NAME_VY         EQU {(rsy + round((RECR_NAME_Y + B) * 1.6)) * 16}")
    L.append(f"RECR_AVAIL_VY        EQU {(rsy + round((RECR_AVAIL_Y + B) * 1.6)) * 16}")
    L.append(f"RECR_NUMBUY_VY       EQU {(rsy + round((RECR_NUMBUY_Y + B) * 1.6)) * 16}")
    L.append(f"RECR_COST_VY         EQU {(rsy + round((RECR_TOTAL_Y + B) * 1.6)) * 16}")    # итог "N" (центр)
    L.append(f"RECR_COUNT_VY        EQU {(rsy + round((RECR_COUNT_XY[1] + B) * 1.6)) * 16}")
    L.append(f"RECR_AVAIL_CX        EQU {rsx + round((RECR_AVAIL_X + B) * 1.6)}")            # центр Available (экран px)
    L.append(f"RECR_NUMBUY_RX       EQU {rsx + round((RECR_NUMBUY_X + B) * 1.6)}")           # правый край Number to buy (px)
    L.append(f"RECR_TOTAL_CX        EQU {rsx + round((RECR_TOTAL_X + B) * 1.6)}")            # центр итога (px)
    L.append(f"RECR_COUNT_CX        EQU {rsx + round((RECR_COUNT_XY[0] + B) * 1.6)}")        # центр счётчика (px, бокс)
    L.append(f"RECR_PT_CX           EQU {rsx + round((189 + B) * 1.6)}")                     # центр цены-за-1 (px)
    L.append(f"RECR_TOTGOLD_VX      EQU {(rsx + round((RECR_TOTGOLD_XY[0] + B) * 1.6)) * 16}")  # икона золота итога
    L.append(f"RECR_TOTGOLD_VY      EQU {(rsy + round((RECR_TOTGOLD_XY[1] + B) * 1.6)) * 16}")
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
    ax = rsx + round((RECR_MON_ANCHOR[0] + RECR_BORDER) * 1.6)     # экран X центра монстра (+бордюр)
    ayb = rsy + round((RECR_MON_ANCHOR[1] + RECR_BORDER) * 1.6)    # экран Y низа монстра (+бордюр)
    L.append("RecruitMonPosTab:                      ; [recruit idx] → позиция спрайта (vertex) [Xlo,Xhi,Ylo,Yhi]")
    for (addr, w, h) in mon_addrs:
        px = (ax - w // 2) * 16
        py = (ayb - h) * 16
        L.append(f"                DEFB #{px & 0xFF:02X}, #{(px >> 8) & 0xFF:02X}, "
                 f"#{py & 0xFF:02X}, #{(py >> 8) & 0xFF:02X}")
    # --- цена-за-1 (gold-иконка + число) в рамке «Cost per troop» (RedrawMonsterInfo, gold-only 159,59/189,89 +offsetX10) ---
    g_addr, g_w, g_h = gold_addr
    L.append(f"RECRUIT_GOLD_RAMG    EQU #{g_addr:06X}")
    L.append("RecruitGoldRec:                        ; запись иконки золота [lo,mid,hi,w,h] для DrawSpriteEntry")
    L.append(f"                DEFB #{g_addr & 0xFF:02X}, #{(g_addr >> 8) & 0xFF:02X}, "
             f"#{(g_addr >> 16) & 0xFF:02X}, {g_w}, {g_h}")
    # Иконка золота цены-за-1 (RedrawResourceInfo gold-only px1=159,py1=59 / число px2=189,py2=89).
    # БЕЗ offsetX (+10) — он в оригинале компенсирует сдвиг рамки в StandardWindow; у меня рамка на
    # native-месте RECRBKG(138,54). RECRBKG-native = window + RECR_BORDER. Центрируется в боксе (центр 203).
    gx = (rsx + round((159 + RECR_BORDER) * 1.6)) * 16   # иконка золота @ RECRBKG(175,75)
    gy = (rsy + round((59 + RECR_BORDER) * 1.6)) * 16
    ptx = (rsx + round((189 + RECR_BORDER) * 1.6)) * 16  # число per-troop @ RECRBKG(205,105)
    pty = (rsy + round((89 + RECR_BORDER) * 1.6)) * 16
    L.append(f"RECR_GOLD_VX         EQU {gx}")
    L.append(f"RECR_GOLD_VY         EQU {gy}")
    L.append(f"RECR_PT_VX           EQU {ptx}")
    L.append(f"RECR_PT_VY           EQU {pty}")
    strtab("RecruitPerTroopTab", lambda i: str(RECRUIT_COST[i]))   # цена за 1 (число)
    # --- числовые таблицы для live-счётчика (3b): доступно + цена-за-1 ---
    L.append("RecruitAvailNum:                       ; [recruit idx] → доступно (DW), кламп счётчика")
    for i in range(len(RECRUIT_AVAIL)):
        L.append(f"                DW {RECRUIT_AVAIL[i]}")
    L.append("RecruitCostNum:                        ; [recruit idx] → цена-за-1 (DW), для total")
    for i in range(len(RECRUIT_COST)):
        L.append(f"                DW {RECRUIT_COST[i]}")
    L.append('RecruitNumBuy:  DEFB "Number to buy:", 0')   # smallWhite, право-выр. (dialog_recruit.cpp:218)
    L.append('RecruitAvailPfx: DEFB "Available: ", 0')
    L.append(f"START_GOLD           EQU {START_FUNDS['gold']}")   # стартовая казна (kingdom funds, 3c)
    # Позиция живого золота на панели (3d): центр ячейки золота strip-local (593,156), панель ×1.6 @ screen y0.
    panel_y0 = round(TOWN_H * 1.6)
    gold_cx = round(593 * 1.6)                                    # центр ячейки на экране
    L.append(f"GOLD_PANEL_CX        EQU {gold_cx}")               # центр (ui_castle.cpp:295 — число центрируется)
    gold_y = panel_y0 + round(156 * 1.6)
    L.append(f"GOLD_PANEL_VX        EQU {(gold_cx - 12) * 16}")   # лево-выр. (≈центр для 4 цифр)
    L.append(f"GOLD_PANEL_VY        EQU {gold_y * 16}")
    # --- Единая слот-модель армии (ArmyBar castle_dialog.cpp): 10 слотов, 0-4=гарнизон(top), 5-9=герой(bottom).
    # Оба ряда рисуются ДИНАМИЧЕСКИ (портрет MONH + счётчик), портреты НЕ запечены. Строки: гарнизон
    # strip-local y=6, герой y=105 (rectSign1/2, castle_dialog.cpp:351-352). MONH bottom-anchor y=99/198,
    # счётчик y=86/185. Слот i: cellx=112+(i%5)*88 (ArmyBar offset 112, шаг 88), центр +41, счётчик +64.
    L.append("RecruitMonhTab:                        ; [recruit idx] → MONH-портрет ×1.6 [lo,mid,hi,w,h]")
    for (addr, w, h) in monh_addrs:
        L.append(f"                DEFB #{addr & 0xFF:02X}, #{(addr >> 8) & 0xFF:02X}, "
                 f"#{(addr >> 16) & 0xFF:02X}, {w}, {h}")
    monh_yg = (panel_y0 + round(99 * 1.6)) * 16       # низ ячейки MONH: гарнизон / герой
    monh_yh = (panel_y0 + round((99 + 99) * 1.6)) * 16
    cnt_yg = (panel_y0 + round(86 * 1.6)) * 16        # счётчик: гарнизон / герой
    cnt_yh = (panel_y0 + round((86 + 99) * 1.6)) * 16

    def slot_cx(i):    return round((112 + (i % 5) * 88 + 41) * 1.6) * 16
    # Счётчик армии право-выровнен к правому-нижнему углу ячейки (army_bar.cpp:297:
    # x = pos.x+pos.width-tw-3). ArmyCntX = ПРАВЫЙ край в экранных px (без ×16); ASM вычтет ширину числа.
    def slot_cntrx(i): return round((112 + (i % 5) * 88 + 82 - 3) * 1.6)
    L.append("ArmyMonhX:      DW " + ", ".join(str(slot_cx(i)) for i in range(10)))    # X-центр портрета
    L.append("ArmyMonhY:      DW " + ", ".join(str(monh_yg if i < 5 else monh_yh) for i in range(10)))
    L.append("ArmyCntX:       DW " + ", ".join(str(slot_cntrx(i)) for i in range(10))) # ПРАВЫЙ край счётчика (px)
    L.append("ArmyCntY:       DW " + ", ".join(str(cnt_yg if i < 5 else cnt_yh) for i in range(10)))
    # Подсветка выбранного слота (ArmyBar isSelected): полупрозрачный жёлтый прямоугольник над ячейкой.
    # 10 статичных DL-блоков (по одному на слот) — ASM копирует нужный по ArmySel. Ячейка 82×93 @ (112+col*88, ряд).
    for i in range(10):
        cellx = round((112 + (i % 5) * 88) * 1.6) * 16
        celly = round((262 if i < 5 else 361) * 1.6) * 16
        cx1 = cellx + round(82 * 1.6) * 16
        cy1 = celly + round(93 * 1.6) * 16
        L.append(f"HighlightDL_{i}:")
        L.append("                FT_BEGIN FT_RECTS")
        L.append("                FT_COLOR_RGB 255, 255, 0")
        L.append("                FT_COLOR_A 90")
        L.append(f"                FT_VERTEX2F {cellx}, {celly}")
        L.append(f"                FT_VERTEX2F {cx1}, {cy1}")
        L.append("                FT_END")
        L.append("                FT_COLOR_RGB 255, 255, 255")
        L.append("                FT_COLOR_A 255")
        L.append(f"HighlightDL_{i}_SIZE EQU $ - HighlightDL_{i}")
    L.append("HighlightDLTab:                        ; [slot] → DW addr, DW size")
    for i in range(10):
        L.append(f"                DW HighlightDL_{i}, HighlightDL_{i}_SIZE")
    # --- Плита STRIP[4] (Knight, заснеженные горы) под ЗАНЯТЫМ слотом армбара (renderMonsterFrame,
    # ui_monster.cpp): оригинал кладёт эту плиту ПОД портрет монстра; я её выронил при динамизации
    # армбара → войска сидели на коричневой пустой STRIP[2]. 10 self-contained битмап-блоков (opaque
    # палитра ×1.6, как RECRBKG) + таблица; ASM копирует блок для каждого слота ArmyType!=0 ДО MONH.
    (plate_a, pw, ph) = plate_addr
    L.append(f"ARMY_PLATE_RAMG      EQU #{plate_a:06X}")
    dpw, dph = round(pw * 1.6), round(ph * 1.6)
    # ★Плита выравнивается ТОЧНО к сетке композита-панели (иначе край плиты налезает на золотую рамку
    # STRIP[0], «битые рамки»): та же вершина strip-панели (STRIP_Y*256//10, как в Town_DL) + strip-локальный
    # сдвиг ячейки, ВСЁ в суб-пиксельных 1/16 (round(v*1.6*16)), НЕ округляя до целого px заранее.
    strip_y_v = STRIP_Y * 256 // 10
    for i in range(10):
        cellx = round((112 + (i % 5) * 88) * 1.6 * 16)
        celly = strip_y_v + round((6 if i < 5 else 105) * 1.6 * 16)
        L.append(f"ArmyPlateDL_{i}:")
        L.append("                FT_BITMAP_TRANSFORM_A 160")
        L.append("                FT_BITMAP_TRANSFORM_B 0")
        L.append("                FT_BITMAP_TRANSFORM_C 0")
        L.append("                FT_BITMAP_TRANSFORM_D 0")
        L.append("                FT_BITMAP_TRANSFORM_E 160")
        L.append("                FT_BITMAP_TRANSFORM_F 0")
        L.append("                FT_BITMAP_LAYOUT_H 0, 0")
        L.append("                FT_BITMAP_SIZE_H 0, 0")
        L.append("                FT_PALETTE_SOURCE TOWN_PAL_RAMG")
        L.append("                FT_BEGIN FT_BITMAPS")
        L.append("                FT_BITMAP_SOURCE ARMY_PLATE_RAMG")
        L.append(f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {pw}, {ph}")
        L.append(f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {dpw}, {dph}")
        L.append(f"                FT_VERTEX2F {cellx}, {celly}")
        L.append("                FT_END")
        L.append(f"ArmyPlateDL_{i}_SIZE EQU $ - ArmyPlateDL_{i}")
    L.append("ArmyPlateDLTab:                        ; [slot] → DW addr, DW size")
    for i in range(10):
        L.append(f"                DW ArmyPlateDL_{i}, ArmyPlateDL_{i}_SIZE")
    L.append("")
    L.append("                endif")
    TOWN_INC.write_text("\n".join(L), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="HMM2TOWN.PAK — экран города Knight (стрим-PAK).")
    ap.add_argument("--preview", type=Path, default=None, help="PNG-реконструкция города для сверки")
    args = ap.parse_args()

    agg, ent = read_agg_index_with_expansion(AGG_PATH)
    palette = read_palette(agg_entry(agg, ent, "KB.PAL"))
    import dump_mp2_castles                                                # РЕАЛЬНЫЕ данные замка из MX2 (кровь)
    castle = dump_mp2_castles.knight_castle(AGG_PATH.parents[1] / "MAPS" / "SKIRMISH.MX2")
    pano_built = dump_mp2_castles.panorama_built_keys(castle)              # что реально построено в панораме
    print(f"  панорама '{castle.get('name')}' построено: {sorted(pano_built)}")
    town_img, placed, block_hit = load_town(palette, pano_built, castle.get("name") or "Castle")
    # ★Шрифты пред-масштабируются ВМЕСТЕ с экраном (экран ×1.6): NEAREST в Python (transform рвёт
    # глифы). Множитель 1.5 (не 1.6) — по решению пользователя: ×1.5 даёт ровный пиксельный паттерн
    # (каждый второй столбец дублируется), ×1.6 — рваный.
    FONT_SCALE = 1.5
    names_masks = []                                                        # hover-имена = строки (маски удалены)
    font_masks = bake_font(agg, ent, scale=FONT_SCALE)                          # атлас SMALFONT (подписи)
    font_masks_big = bake_font(agg, ent, font_icn="FONT.ICN", scale=FONT_SCALE)  # атлас FONT 14px (normal)
    # Описания попапа = normalWhite (FONT, ui_dialog.cpp:325) → врап BIG-шрифтом по интерьеру
    # boxAreaWidthPx 244 native (INFO_WRAP_PX = 390 экранных px).
    glyph_w_big = {chr(32 + i): font_masks_big[i][1] for i in range(len(font_masks_big))}
    wrapped_descs = [wrap_desc(d, glyph_w_big) for d in KNIGHT_DESCS]      # описания → строки

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
    gold_icon = bake_recruit_gold(agg, ent)
    monh_sprites = bake_garrison_monh(agg, ent)
    funds = {"gold": START_FUNDS["gold"], "wood": START_FUNDS["wood"], "mercury": START_FUNDS["mercury"],
             "ore": START_FUNDS["ore"], "sulfur": START_FUNDS["sulfur"], "crystal": START_FUNDS["crystal"],
             "gems": START_FUNDS["gems"]}
    statuses = dump_mp2_castles.build_statuses(castle, funds, has_sea=castle.get("has_sea", False))  # статусы (CheckBuyBuilding)
    print(f"  замок '{castle.get('name')}' статусы: {statuses}")
    construct_img = bake_castle_construction(agg, ent, castle.get("name") or "Castle", statuses)
    construct_check = bake_construct_check(agg, ent)                       # галочка «построено» (рантайм)
    army_plate = bake_army_plate(agg, ent)                                 # плита STRIP[4] под занятым слотом армбара
    name_banner = bake_castle_name_banner(agg, ent, castle.get("name") or "Castle")  # плашка названия (оверлей)
    buybuild = bake_buybuild(agg, ent)                                     # куски рамки попапа (NonFixedFrameBox)
    (payload, pal_addr, img_addr, strip_addr, name_pal_addr, name_addrs, font_addrs, big_font_addrs,
     recruit_addr, spr_pal_addr, mon_addrs, gold_addr, monh_addrs, construct_addr, chk_addr, plate_addr, banner_addr, bb_addrs) = build_payload(
        palette, town_img, strip_img, names_masks, font_masks, font_masks_big, recruit_win, monster_sprites, gold_icon, monh_sprites, construct_img, construct_check, army_plate, name_banner, buybuild)
    # --- ПАТЧ-СЕКЦИЯ (строительство): панорамные раны + бенды/углы статусов, вторым HPAK-entry ---
    pano_patches, pano_bboxes = build_pano_patches(agg, ent, img_addr)
    band_patches, corner_patches, corner_org = build_status_patches(agg, ent, construct_addr)
    patch_blob = bytearray()
    def add_patch(stream):
        sec = len(patch_blob) // SECTOR
        patch_blob.extend(stream)
        return sec
    pano_sec = [add_patch(p) for p in pano_patches]
    band_sec = [[add_patch(v) for v in vs] for vs in band_patches]
    corner_sec = [[add_patch(v) for v in vs] for vs in corner_patches]
    # WELL: база (в construct-область) + 6 патчей секций построенных жилищ (в patch_blob)
    well_base, well_sects, wexit0, wexit1 = bake_well(agg, ent)
    well_sec_secs = [add_patch(_pack_patch(_rect_runs(pix, w, h, construct_addr, ox, oy)))
                     for (pix, w, h, ox, oy) in well_sects]
    payload_secs = (len(payload) + SECTOR - 1) // SECTOR
    patch_base = 1 + payload_secs                      # body_start=1 (каталог 40Б) + payload (выровнен)
    # ★ЖЁСТКИЙ ПОТОЛОК: город НЕ должен доставать до резидентных курсор-спрайтов (#0E8000) —
    # перебор тихо давал «мусор от курсора» (город затирал спрайты в RAM_G).
    assert len(payload) <= 0x0E8000, \
        f"город payload {len(payload)} байт перелез в зону курсора #0E8000 ({len(payload) - 0x0E8000} лишних)"
    # Хвост таверны (TAVWIN-композит + кнопка OKAY) — ЗА курсором (#F8000..#100000, 32К):
    # отдельная entry, догружается вторым стримом в Town_LoadFromPak.
    TAV_TAIL_BASE = 0x0F8000
    tail = bytearray()

    def tput(raw):
        while len(tail) % 4:
            tail.append(0)
        addr = TAV_TAIL_BASE + len(tail)
        tail.extend(raw)
        return addr
    tb, tw_, th_ = bake_tavern(agg, ent)
    bb_addrs["tav"] = (tput(tb), tw_, th_)
    for k, v in zip(("ok0", "ok1"), bake_okay_button(agg, ent)):
        bb_addrs[k] = (tput(v[0]), v[1], v[2])
    bb_addrs["wex0"] = (tput(wexit0[0]), wexit0[1], wexit0[2])   # EXIT Well (WELLXTRA 0/1)
    bb_addrs["wex1"] = (tput(wexit1[0]), wexit1[1], wexit1[2])
    assert TAV_TAIL_BASE + len(tail) <= 0x100000, f"хвост таверны перелез за 1МБ RAM_G ({len(tail)})"
    patch_secs = (len(patch_blob) + SECTOR - 1) // SECTOR
    tav_tail_sector = patch_base + patch_secs
    # ★РЫНОК: ассеты (все кадры TRADPOST) — отдельная entry; стримятся В ОБЛАСТЬ найма
    # (RECRBKG, сектор-выровнена; рынок и найм не живут одновременно). Адреса от recruit_addr.
    market = bytearray()
    mk_addrs = []
    for blob, w_, h_ in bake_market(agg, ent):
        while len(market) % 4:
            market.append(0)
        mk_addrs.append((recruit_addr + len(market), w_, h_))
        market.extend(blob)
    assert len(market) <= len(recruit_win), \
        f"рынок {len(market)} байт больше области найма {len(recruit_win)} — рестрим не покроет"
    tav_tail_secs = (len(tail) + SECTOR - 1) // SECTOR
    market_sector = tav_tail_sector + tav_tail_secs
    summary = build_pak(
        [{"type": TYPE_RAMG_BLOB, "target": TOWN_RAMG_BASE, "data": bytes(payload)},
         {"type": TYPE_RAMG_BLOB, "target": 0, "data": bytes(patch_blob)},   # target 0: стример города НЕ льёт
         {"type": TYPE_RAMG_BLOB, "target": TAV_TAIL_BASE, "data": bytes(tail)},
         {"type": TYPE_RAMG_BLOB, "target": 0, "data": bytes(market)},       # рынок: стрим вручную
         {"type": TYPE_RAMG_BLOB, "target": 0, "data": bytes(well_base)}],    # well: стрим вручную
        TOWN_PAK_PATH,
    )
    assert summary["body_start_sector"] == 1, "каталог вылез за сектор — patch_base сломан"
    from pak_builder import read_pak_catalog
    cat = read_pak_catalog(TOWN_PAK_PATH)
    assert cat["entries"][1]["sec_off"] == patch_base, f"patch_base {patch_base} != каталог {cat['entries'][1]['sec_off']}"
    pak = {
        "payload_bytes": len(payload),
        "payload_sectors": payload_secs,
        "body_start_sector": summary["body_start_sector"],
        # Таверна: перенос текстов шрифтом FONT (интерьер 244 native, как инфо-попапы)
        "tavern_intro": wrap_desc(TAVERN_INTRO, glyph_w_big),
        "tavern_rumors": [wrap_desc(r, glyph_w_big) for r in TAVERN_RUMORS],
        "tav_tail_sector": tav_tail_sector,
        "tav_tail_sectors": (len(tail) + SECTOR - 1) // SECTOR,
        "tav_tail_base": TAV_TAIL_BASE,
        # рынок: стрим в область найма + рестрим RECRBKG (сектор внутри главного payload)
        "mk_sector": market_sector,
        "mk_sectors": (len(market) + SECTOR - 1) // SECTOR,
        "mk_addrs": mk_addrs,
        "recruit_sector": 1 + recruit_addr // SECTOR,
        "recruit_sectors": (len(recruit_win) + SECTOR - 1) // SECTOR,
        # well: база в construct-область, рестрим construct, патчи секций
        "well_sector": market_sector + (len(market) + SECTOR - 1) // SECTOR,
        "well_sectors": (len(well_base) + SECTOR - 1) // SECTOR,
        "well_sec_secs": well_sec_secs,
        "construct_sector": 1 + construct_addr // SECTOR,
        "construct_sectors": (len(construct_img) + SECTOR - 1) // SECTOR,
    }
    cdata = {
        "patch_base": patch_base,
        "pano_sec": pano_sec,
        "band_sec": band_sec,
        "corner_sec": corner_sec,
        "corner_org": corner_org,
        "pano_bboxes": pano_bboxes,
    }
    emit_inc(pal_addr, img_addr, strip_addr, name_pal_addr, name_addrs, font_addrs, big_font_addrs, block_hit, pak,
             wrapped_descs, recruit_addr, spr_pal_addr, mon_addrs, gold_addr, monh_addrs, construct_addr, chk_addr, plate_addr, banner_addr, bb_addrs, statuses, cdata)
    print(f"town pack -> {TOWN_PAK_PATH.name}: {len(placed)} построек, "
          f"payload={len(payload)} байт ({pak['payload_sectors']} сект), патчи={len(patch_blob)} байт, PAK={summary['total_bytes']} байт")
    print(f"  inc: {TOWN_INC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
