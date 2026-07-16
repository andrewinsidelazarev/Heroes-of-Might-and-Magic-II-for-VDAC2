"""Faithful-компоновщик fheroes2 StandardWindow (gui/ui_window.cpp render()) → paletted index-буфер.

Переиспользуемо для ВСЕХ окон-диалогов fheroes2 (финал боя, будущие диалоги). Аппаратная уступка
FT812: процедурную рамку пред-композим в спрайт (по решению из спеки боя) — но композиция ТОЧНАЯ:
углы/верт.бордюры WINLOSE[0], гориз.бордюры SURDRBKG[0], фон STONEBAK[0], dithering-переходы
(engine/image.cpp CreateDitheringTransition). Тень окна — отдельная ГЛОБАЛЬНАЯ рантайм-процедура
Render_WindowShadowDL, здесь НЕ печём.

Константы (ui_window.cpp): borderSize=16, borderEdgeOffset=43, transitionSize=10, backgroundOffset=22.
Все opaque single-layer (STONEBAK/WINLOSE/SURDRBKG непрозрачны в теле) → dither = пиксель-копии;
idx0 в WINLOSE (углы) трактуем прозрачным при Blit (как fheroes2 Blit пропускает transform==1).
"""
from object_atlas import agg_entry, read_icn
from viewport_pack import decode_icn_indices

TRANSPARENT = 0
BORDER = 16
BORDER_EDGE = 43
TRANSITION = 10
BG_OFFSET = 22


def _icn(agg, ent, name, frame=0):
    h, e = read_icn(agg_entry(agg, ent, name))[frame]
    return decode_icn_indices(h, e), h["w"], h["h"]


def _copy(dst, dw, src, sw, sx, sy, dx, dy, w, h):
    """Copy региона src→dst (ВСЕ пиксели, как fheroes2 Copy)."""
    for r in range(h):
        so = (sy + r) * sw + sx
        do = (dy + r) * dw + dx
        dst[do:do + w] = src[so:so + w]


def _blit(dst, dw, src, sw, sh, sx, sy, dx, dy, w, h):
    """Blit региона src→dst с пропуском idx0 (прозрачность, как fheroes2 Blit)."""
    for r in range(h):
        so = (sy + r) * sw + sx
        do = (dy + r) * dw + dx
        for c in range(w):
            v = src[so + c]
            if v != TRANSPARENT:
                dst[do + c] = v


def _dither(inb, inw, inX, inY, out, outw, outX, outY, width, height, is_vertical, is_reverse):
    """CreateDitheringTransition (engine/image.cpp:1530), opaque single-layer случай:
    симметричный ordered-dither перенос inb→out по полосе width×height. Степень 2^p убывает к центру."""
    if is_vertical:
        half = width // 2
        # смещения левой/правой «точек» + shift на 1 при нечётной ширине
        lin, lout = 0, 0                       # индекс столбца от левого края
        rin, rout = width - 1, width - 1       # от правого края
        if width % 2 == 1:
            if is_reverse:
                rin -= 1; rout -= 1
            else:
                lin += 1; lout += 1
        for x in range(half):
            step_pow = min(30, (half - x) // 2 + 1)
            stepY = 1 << step_pow
            pattern = (stepY // 2) * ((x + half) % 2)
            for y in range(height):
                offY = y % stepY
                if is_reverse == (pattern != offY):
                    out[(outY + y) * outw + outX + lout] = inb[(inY + y) * inw + inX + lin]
                else:
                    out[(outY + y) * outw + outX + rout] = inb[(inY + y) * inw + inX + rin]
            lin += 1; lout += 1; rin -= 1; rout -= 1
    else:
        half = height // 2
        tin, tout = 0, 0                       # верхняя строка-точка
        bin_, bout = height - 1, height - 1    # нижняя
        if height % 2 == 1:
            if is_reverse:
                bin_ -= 1; bout -= 1
            else:
                tin += 1; tout += 1
        for y in range(half):
            step_pow = min(30, (half - y) // 2 + 1)
            stepX = 1 << step_pow
            pattern = (stepX // 2) * ((y + half) % 2)
            for x in range(width):
                offX = x % stepX
                if is_reverse == (pattern != offX):
                    out[(outY + tout) * outw + outX + x] = inb[(inY + tin) * inw + inX + x]
                else:
                    out[(outY + bout) * outw + outX + x] = inb[(inY + bin_) * inw + inX + x]
            tin += 1; tout += 1; bin_ -= 1; bout -= 1


def _render_background(out, ow, oh, roi_x, roi_y, roi_w, roi_h, bg, bgw, bgh):
    """renderBackgroundImage (ui_window.cpp:593): STONEBAK[0] тайлится с dither-переходами."""
    bw = roi_w - BG_OFFSET * 2
    bh = roi_h - BG_OFFSET * 2
    hcopies = (bw - 1 - TRANSITION) // (bgw - TRANSITION)
    vcopies = (bh - 1 - TRANSITION) // (bgh - TRANSITION)
    cw = min(bgw, bw)
    ch = min(bgh, bh)
    ox = roi_x + BG_OFFSET
    oy = roi_y + BG_OFFSET
    _copy(out, ow, bg, bgw, 0, 0, ox, oy, cw, ch)
    if hcopies > 0:
        toX = BG_OFFSET + bgw
        _dither(bg, bgw, 0, 0, out, ow, roi_x + toX - TRANSITION, oy, TRANSITION, ch, True, False)
        stepX = bgw - TRANSITION
        fromX = BG_OFFSET + TRANSITION
        for _ in range(hcopies):
            w = min(bgw, roi_w - BG_OFFSET - toX)
            _copy(out, ow, out, ow, roi_x + fromX, oy, roi_x + toX, oy, w, ch)
            toX += stepX
    if vcopies > 0:
        toY = BG_OFFSET + bgh
        _dither(out, ow, ox, oy, out, ow, ox, roi_y + toY - TRANSITION, bw, TRANSITION, False, False)
        stepY = bgh - TRANSITION
        fromY = BG_OFFSET + TRANSITION
        for _ in range(vcopies):
            h = min(bgh, roi_h - BG_OFFSET - toY)
            _copy(out, ow, out, ow, ox, roi_y + fromY, ox, roi_y + toY, bw, h)
            toY += stepY


def render_standard_window(agg, ent, active_w, active_h, has_background=True):
    """StandardWindow(active_w, active_h, has_background). Возвращает (index_buf, W, H, border_off)
    где W,H = размер _windowArea (= active + 2*BORDER), border_off = смещение activeArea внутри
    буфера (= BORDER). Содержимое диалога рисовать поверх со сдвигом (BORDER, BORDER)."""
    vert, vw, vh = _icn(agg, ent, "WINLOSE.ICN", 0)      # углы + верт.бордюры
    horiz, hw, hh = _icn(agg, ent, "SURDRBKG.ICN", 0)    # гориз.бордюры (16px тень слева/снизу)
    bg, bgw, bgh = _icn(agg, ent, "STONEBAK.ICN", 0)     # фон

    W = active_w + 2 * BORDER
    H = active_h + 2 * BORDER
    out = bytearray(W * H)                               # _windowArea @ (0,0) в буфере
    wx, wy = 0, 0
    corner = BG_OFFSET if has_background else BORDER
    hSpriteW = hw - BORDER
    hSpriteH = hh - BORDER
    rightCornerX = wx + W - corner
    bottomCornerY = wy + H - corner
    rightCornerSpriteX = vw - corner
    bottomCornerSpriteY = vh - corner
    # углы (все из vert)
    _blit(out, W, vert, vw, vh, 0, 0, wx, wy, corner, corner)
    _blit(out, W, vert, vw, vh, rightCornerSpriteX, 0, rightCornerX, wy, corner, corner)
    _blit(out, W, vert, vw, vh, 0, bottomCornerSpriteY, wx, bottomCornerY, corner, corner)
    _blit(out, W, vert, vw, vh, rightCornerSpriteX, bottomCornerSpriteY, rightCornerX, bottomCornerY, corner, corner)
    # доп. часть углов (не тайлится)
    extra = BORDER_EDGE - corner
    coX, coY = wx + corner, wy + corner
    rightEdge = vw - BORDER_EDGE
    bottomEdge = vh - BORDER_EDGE
    _blit(out, W, vert, vw, vh, corner, 0, coX, wy, extra, corner)
    _blit(out, W, vert, vw, vh, 0, corner, wx, coY, corner, extra)
    _blit(out, W, vert, vw, vh, rightEdge, 0, rightCornerX - extra, wy, extra, corner)
    _blit(out, W, vert, vw, vh, rightCornerSpriteX, corner, rightCornerX, coY, corner, extra)
    _blit(out, W, vert, vw, vh, corner, bottomCornerSpriteY, coX, bottomCornerY, extra, corner)
    _blit(out, W, vert, vw, vh, 0, bottomEdge, wx, bottomCornerY - extra, corner, extra)
    _blit(out, W, vert, vw, vh, rightEdge, bottomCornerSpriteY, rightCornerX - extra, bottomCornerY, extra, corner)
    _blit(out, W, vert, vw, vh, rightCornerSpriteX, bottomEdge, rightCornerX, bottomCornerY - extra, corner, extra)

    if has_background:
        _render_background(out, W, H, wx, wy, W, H, bg, bgw, bgh)
        # переходы углов в фон
        _dither(vert, vw, corner, corner, out, W, coX, coY, extra, TRANSITION, False, True)
        _dither(vert, vw, corner, corner, out, W, coX, coY, TRANSITION, extra, True, True)
        _dither(vert, vw, rightEdge, corner, out, W, rightCornerX - extra, coY, extra, TRANSITION, False, True)
        _dither(vert, vw, rightCornerSpriteX - TRANSITION, corner, out, W, rightCornerX - TRANSITION, coY, TRANSITION, extra, True, False)
        _dither(vert, vw, corner, bottomCornerSpriteY - TRANSITION, out, W, coX, bottomCornerY - TRANSITION, extra, TRANSITION, False, False)
        _dither(vert, vw, corner, bottomEdge, out, W, coX, bottomCornerY - extra, TRANSITION, extra, True, True)
        _dither(vert, vw, rightEdge, bottomCornerSpriteY - TRANSITION, out, W, rightCornerX - extra, bottomCornerY - TRANSITION, extra, TRANSITION, False, False)
        _dither(vert, vw, rightCornerSpriteX - TRANSITION, bottomEdge, out, W, rightCornerX - TRANSITION, bottomCornerY - extra, TRANSITION, extra, True, False)

    # верт.бордюры
    dbl = BORDER_EDGE * 2
    vCopyH = min(H, vh) - dbl
    vCopies = (H - dbl - 1 - TRANSITION) // (bottomEdge - BORDER_EDGE - TRANSITION)
    topEdgeY = wy + BORDER_EDGE
    _blit(out, W, vert, vw, vh, 0, BORDER_EDGE, wx, topEdgeY, corner, vCopyH)
    _blit(out, W, vert, vw, vh, rightCornerSpriteX, BORDER_EDGE, rightCornerX, topEdgeY, corner, vCopyH)
    if has_background:
        _dither(vert, vw, corner, BORDER_EDGE, out, W, coX, topEdgeY, TRANSITION, vCopyH, True, True)
        _dither(vert, vw, rightCornerSpriteX - TRANSITION, BORDER_EDGE, out, W, rightCornerX - TRANSITION, topEdgeY, TRANSITION, vCopyH, True, False)
    if vCopies > 0:
        toY = BORDER_EDGE + vCopyH
        outY = wy + toY - TRANSITION
        _dither(vert, vw, 0, BORDER_EDGE, out, W, wx, outY, corner, TRANSITION, False, False)
        _dither(vert, vw, rightCornerSpriteX, BORDER_EDGE, out, W, rightCornerX, outY, corner, TRANSITION, False, False)
        stepY = vCopyH - TRANSITION
        fromY = BORDER_EDGE + TRANSITION
        for _ in range(vCopies):
            ch = min(vCopyH, H - BORDER_EDGE - toY)
            toYY = wy + toY
            _blit(out, W, vert, vw, vh, 0, fromY, wx, toYY, corner, ch)
            _blit(out, W, vert, vw, vh, rightCornerSpriteX, fromY, rightCornerX, toYY, corner, ch)
            if has_background:
                _dither(vert, vw, corner, fromY, out, W, coX, toYY, TRANSITION, ch, True, True)
                _dither(vert, vw, rightCornerSpriteX - TRANSITION, fromY, out, W, rightCornerX - TRANSITION, toYY, TRANSITION, ch, True, False)
            toY += stepY
    vBotEdgeY = bottomEdge - TRANSITION
    outBotEdgeY = wy + H - BORDER_EDGE - TRANSITION
    _dither(vert, vw, 0, vBotEdgeY, out, W, wx, outBotEdgeY, corner, TRANSITION, False, False)
    _dither(vert, vw, rightCornerSpriteX, vBotEdgeY, out, W, rightCornerX, outBotEdgeY, corner, TRANSITION, False, False)

    # гориз.бордюры (SURDRBKG: 16px тень слева/снизу — НИЖНИЙ бордюр резать ВЫШЕ тени
    # (hSpriteH = hh − BORDER), иначе в композит попадает полоса тени вместо каменной кромки)
    hCopyW = min(W, hSpriteW) - dbl
    hCopies = (W - dbl - 1 - TRANSITION) // (hSpriteW - dbl - TRANSITION)
    botSpriteY = hSpriteH - corner
    hStartX = BORDER_EDGE + BORDER
    leftEdgeX = wx + BORDER_EDGE
    _blit(out, W, horiz, hw, hh, hStartX, 0, leftEdgeX, wy, hCopyW, corner)
    _blit(out, W, horiz, hw, hh, hStartX, botSpriteY, leftEdgeX, bottomCornerY, hCopyW, corner)
    if has_background:
        _dither(horiz, hw, hStartX, corner, out, W, leftEdgeX, coY, hCopyW, TRANSITION, False, True)
        _dither(horiz, hw, hStartX, botSpriteY - TRANSITION, out, W, leftEdgeX, bottomCornerY - TRANSITION, hCopyW, TRANSITION, False, False)
    if hCopies > 0:
        toX = BORDER_EDGE + hCopyW
        outX = wx + toX - TRANSITION
        _dither(horiz, hw, hStartX, 0, out, W, outX, wy, TRANSITION, corner, True, False)
        _dither(horiz, hw, hStartX, botSpriteY, out, W, outX, bottomCornerY, TRANSITION, corner, True, False)
        stepX = hCopyW - TRANSITION
        fromX = hStartX + TRANSITION
        for _ in range(hCopies):
            cw = min(hCopyW, W - BORDER_EDGE - toX)
            toXX = wx + toX
            _blit(out, W, horiz, hw, hh, fromX, 0, toXX, wy, cw, corner)
            _blit(out, W, horiz, hw, hh, fromX, botSpriteY, toXX, bottomCornerY, cw, corner)
            if has_background:
                _dither(horiz, hw, fromX, corner, out, W, toXX, coY, cw, TRANSITION, False, True)
                _dither(horiz, hw, fromX, botSpriteY - TRANSITION, out, W, toXX, bottomCornerY - TRANSITION, cw, TRANSITION, False, False)
            toX += stepX
    hRightEdgeX = hw - BORDER_EDGE - TRANSITION
    outRightEdgeX = wx + W - BORDER_EDGE - TRANSITION
    _dither(horiz, hw, hRightEdgeX, 0, out, W, outRightEdgeX, wy, TRANSITION, corner, True, False)
    _dither(horiz, hw, hRightEdgeX, botSpriteY, out, W, outRightEdgeX, bottomCornerY, TRANSITION, corner, True, False)
    return bytes(out), W, H, BORDER


if __name__ == "__main__":
    # Самотест: отрендерить StandardWindow 335×424 в PNG для визуальной сверки.
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from agg_tools import read_agg_index_with_expansion
    from object_atlas import read_palette
    from PIL import Image
    ROOT = Path(__file__).resolve().parents[2]
    agg, ent = read_agg_index_with_expansion(ROOT / "Assets" / "Original" / "DATA" / "HEROES2.AGG")
    pal = read_palette(agg_entry(agg, ent, "KB.PAL"))
    buf, W, H, bo = render_standard_window(agg, ent, 335, 424, True)
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        for x in range(W):
            px[x, y] = pal[buf[y * W + x]]
    out = ROOT / "Diagnostics" / "stdwindow_335x424.png"
    im.save(str(out))
    print(f"saved {out}  ({W}x{H}, border_off={bo})")
