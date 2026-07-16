"""Единый порт примитивов рендера fheroes2 → paletted indexed canvas (8-bit, TRANSPARENT=0).

ФИЛОСОФИЯ: перенос диалога = ДОСЛОВНАЯ трансляция его Redraw-функции (C++) в вызовы этого
модуля, строка-в-строку, ничего не пропуская и не выдумывая. Каждый примитив воспроизводит
ровно поведение движка — баг правится ОДИН раз здесь и исчезает во всех окнах сразу.

СООТВЕТСТВИЯ ДВИЖКУ (левое → правое):
  ТЕНЬ ОКНА (обязательна!)                    ОКНО = ОТДЕЛЬНЫЙ DL (transp-слой) + ASM Render_WindowShadowDL(окно_DL) — ОДНА формула на ВСЕ окна
                                              (меню/город/бой): COLOR_A 80, сдвиг −8/+8, полупрозрачная. НЕ спрайт-тень в композит (тонет).
  fheroes2::Blit(spr, dst, x, y)              gui.blit(spr, x, y)                 image.cpp:1213 (offset спрайта НЕ добавляется)
  fheroes2::Copy(spr, 0,0, dst, roi)          gui.blit(spr, x, y, transp=False)
  fheroes2::addGradientShadow(...)            gui.blit(shadow_spr, x-5, y+3)      готовый shadow-спрайт AGG (NGEXTRA 59/60/61)
  Text(s, font).draw(x, y, dst)               gui.text(s, font, x, y)             ЛЕВЫЙ край
  Text(s, font).draw(x, y, maxWidth, dst)     gui.text(s, font, x, y, maxWidth)   ЦЕНТР строки в maxWidth (ui_text.cpp:486)  ← ГЛАВНАЯ ГРАБЛЯ
  Text(s, font).fitToOneRow(maxWidth)         gui.fit_to_one_row(s, font, maxW)   обрезка «…» (ui_text.cpp:495)
  Game::GetStep4Player(i, w, total)           step4player(i, w, total)            позиция игрока в 6-слотовой сетке
  playerIcon = NGEXTRA[9/15/3 + colorIdx +24] portrait_ngextra(colorIdx, ...)     player_info.cpp RedrawInfo
  classIcon  = NGEXTRA[51..58 / 70..76]        class_ngextra(race, active)

ЧЕК-ЛИСТ переноса окна (следовать строго):
  0. ТЕНЬ ОКНА — НЕ ЗАБЫВАТЬ. Любое окно/панель отбрасывает тень. ВСЕГДА: держи ОКНО отдельным
     DL (transp-слой поверх фона-DL) и рисуй тень глоб. ASM Render_WindowShadowDL(окно_DL) —
     ОДНА формула на все окна (меню/город/бой). НЕ спрайт-тень в композит (на тёмном фоне тонет).
     Забыть тень = «плоское», не как оригинал.
  1. Открыть Redraw*-функцию C++ ЦЕЛИКОМ (напр. RedrawScenarioStaticInfo + playersInfo.RedrawInfo).
  2. Транслировать КАЖДЫЙ вызов рендера построчно — не решать «это для скирмиша не нужно».
     Частые пропуски: тень окна, перерисованные поверх кнопки (SELECT), тени спрайтов, handicap.
  3. Координаты — буквально из кода (rt.x+N). Выравнивание/шрифт/тень — через примитивы.
     ГЛАВНАЯ ГРАБЛЯ: text.draw(x,y,rt.width) ЦЕНТРИРУЕТ, а не рисует по левому краю.
  4. gui.to_png() → сверить с оригиналом (или fheroes2-скрин). Затем эмулятор (реальный FT812).
"""
from object_atlas import agg_entry, read_icn
from viewport_pack import decode_icn_indices

TRANSPARENT = 0                                  # OBJECT_TRANSPARENT_INDEX

# fheroes2 FontType → ICN шрифта + ширина глифа пробела (пробел в ICN пустой, ширина отдельно)
FONT_BIG = "FONT.ICN"                            # normalWhite/Yellow/Gray (индексы глифов общие)
FONT_SMALL = "SMALFONT.ICN"                      # smallWhite
_SPACE = {FONT_BIG: 6, FONT_SMALL: 4}
# fheroes2 getFontHeight (ui_font.cpp): межстрочная высота
_ROW_H = {FONT_BIG: 16, FONT_SMALL: 8}


def frame(icn, idx=0):
    """ICN[idx] → dict спрайта (ox/oy/w/h + декодированные indices)."""
    h, e = icn[idx]
    return {"ox": h["ox"], "oy": h["oy"], "w": h["w"], "h": h["h"], "indices": decode_icn_indices(h, e)}


class Gui:
    """Indexed-канва W×H + примитивы рендера fheroes2. base=фон (bytearray) или None (прозрачная)."""

    def __init__(self, agg, entries, w, h, base=None, palette=None):
        self.agg, self.entries = agg, entries
        self.W, self.H = w, h
        self.pal = palette
        self.cv = bytearray(base) if base is not None else bytearray([TRANSPARENT]) * (w * h)
        self._icn_cache = {}

    # ---- загрузка ассетов ----
    def _icn_raw(self, name):
        if name not in self._icn_cache:
            self._icn_cache[name] = read_icn(agg_entry(self.agg, self.entries, name))
        return self._icn_cache[name]

    def icn(self, name, idx=0):
        """Спрайт ICN[idx] (для blit/copy)."""
        return frame(self._icn_raw(name), idx)

    # ---- Blit / Copy (image.cpp:1213 — рисует @ (x,y), внутренний offset спрайта не добавляется) ----
    def blit(self, spr, x, y, transparent=True):
        cv, W, H = self.cv, self.W, self.H
        iw, ih, ind = spr["w"], spr["h"], spr["indices"]
        for yy in range(ih):
            py = y + yy
            if not (0 <= py < H):
                continue
            row, srow = py * W, yy * iw
            for xx in range(iw):
                px = x + xx
                if not (0 <= px < W):
                    continue
                v = ind[srow + xx]
                if transparent and v == TRANSPARENT:
                    continue
                cv[row + px] = v

    def copy(self, spr, x, y):
        """fheroes2::Copy — все пиксели, без прозрачности."""
        self.blit(spr, x, y, transparent=False)

    def window_shadow(self, shadow_spr, x, y, border=6):
        """[устаревший приём] спрайт-тень в композит. НЕ использовать для окна-в-сцене: на
        indexed FT812 спрайт-тень сплошная/тонет на тёмном фоне. ПРАВИЛЬНО (2026-07-06): любое
        ОКНО (панель) держать ОТДЕЛЬНЫМ DL (transp-слой поверх фона-DL) и рисовать тень
        глобальной ASM Render_WindowShadowDL(окно_DL) — ОДНА формула на ВСЕ окна (меню/город/бой):
        COLOR_A 80, сдвиг −8/+8, полупрозрачная. Так сделан scenario: ScenBg_DL(фон) +
        Render_WindowShadowDL(ScenPanel_DL) + ScenPanel_DL. НЕ ЗАБЫВАТЬ — см. чек-лист п.0."""
        self.blit(shadow_spr, x - border, y + border, transparent=True)

    # ---- Text (ui_text.cpp) ----
    def text_width(self, s, font):
        f = self._icn_raw(font)
        sp = _SPACE[font]
        return sum(sp if c == " " else f[ord(c) - 32][0]["w"] for c in s)

    def _draw_line(self, s, font, x, y):
        f = self._icn_raw(font)
        sp = _SPACE[font]
        cv, W, H = self.cv, self.W, self.H
        cx = x
        for c in s:
            if c == " ":
                cx += sp
                continue
            gh, ge = f[ord(c) - 32]
            gi = decode_icn_indices(gh, ge)
            gw, gg, goy = gh["w"], gh["h"], gh.get("oy", 0)
            for yy in range(gg):
                py = y + goy + yy
                if not (0 <= py < H):
                    continue
                base = py * W
                grow = yy * gw
                for xx in range(gw):
                    v = gi[grow + xx]
                    if v != TRANSPARENT and 0 <= cx + xx < W:
                        cv[base + cx + xx] = v
            cx += gw

    def text(self, s, font, x, y, max_width=0):
        """Text::draw. max_width>0 → КАЖДАЯ строка центрируется в max_width (ui_text.cpp:486:
        offsetX = (maxWidth - lineWidth)/2). max_width<=0 → по левому краю от x."""
        if max_width <= 0:
            self._draw_line(s, font, x, y)
            return
        for line, lw, ly in self._wrap(s, font, max_width):
            self._draw_line(line, font, x + (max_width - lw) // 2, y + ly)

    def _wrap(self, s, font, max_width):
        """Перенос по словам ≤ max_width → [(line, width, y_offset)]. Одна строка, если влезает."""
        row_h = _ROW_H[font]
        words = s.split(" ")
        lines, cur = [], ""
        for w in words:
            trial = w if not cur else cur + " " + w
            if not cur or self.text_width(trial, font) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return [(ln, self.text_width(ln, font), i * row_h) for i, ln in enumerate(lines)]

    def fit_to_one_row(self, s, font, max_width):
        """Text::fitToOneRow — обрезать с многоточием, если шире max_width (ui_text.cpp:495)."""
        if self.text_width(s, font) <= max_width:
            return s
        ell = "..."
        while s and self.text_width(s + ell, font) > max_width:
            s = s[:-1]
        return s + ell

    # ---- вывод ----
    def to_png(self, path):
        """Индекс-канва → RGB PNG (для сверки с оригиналом). Требует palette."""
        from PIL import Image
        flat = [c for rgb in self.pal for c in rgb]
        im = Image.new("P", (self.W, self.H))
        im.putpalette(flat)
        im.putdata(bytes(self.cv))
        im.convert("RGB").save(path)


# ==== fheroes2 game-логика: точные формулы/индексы (не выдумывать в каждом окне) ====

def step4player(i, width, total, max_players=6):
    """Game::GetStep4Player — горизонт. позиция игрока i из total в сетке max_players слотов."""
    return i * width * max_players // total + width * (max_players - total) // (2 * total)


# Color::GetIndex: BLUE=0, GREEN=1, RED=2, YELLOW=3, ORANGE=4, PURPLE=5
COLOR_INDEX = {"BLUE": 0, "GREEN": 1, "RED": 2, "YELLOW": 3, "ORANGE": 4, "PURPLE": 5}


def portrait_ngextra(color_index, is_human_current, is_comp_only=False):
    """NGEXTRA-индекс портрета игрока (player_info.cpp RedrawInfo): human=9+ci, comp-only=15+ci,
    either=3+ci; всегда +24 (wide sprite)."""
    if is_human_current:
        base = 9 + color_index
    elif is_comp_only:
        base = 15 + color_index
    else:
        base = 3 + color_index
    return base + 24


# NGEXTRA class icon: (active, inactive) по расе (player_info.cpp 1.0.0)
_CLASS_ICN = {"KNGT": (51, 70), "BARB": (52, 71), "SORC": (53, 72),
              "WRLK": (54, 73), "WZRD": (55, 74), "NECR": (56, 75), "RAND": (58, 76)}


def class_ngextra(race, active=True):
    a, ina = _CLASS_ICN[race]
    return a if active else ina
