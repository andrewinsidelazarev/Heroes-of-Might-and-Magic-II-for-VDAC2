#!/usr/bin/env python3
"""Превью окна итога боя ПО ИСХОДНИКУ fheroes2 StandardWindow::render (ui_window.cpp:139)
+ DialogBattleSummary (battle_dialogs.cpp:474). Реальные спрайты: углы/верт.края WINLOSE[0],
гориз.края SURDRBKG[0], тайл-фон STONEBAK[0]. Регион анимации WINLOSE[0]{43,32,231,133} + WINCMBT.
ПРИБЛИЖЕНИЕ (помечено): дизеринг-переходы (10px-бленды на швах) и внешняя градиент-тень опущены.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from agg_tools import read_agg_index_with_expansion
from object_atlas import agg_entry, read_icn, read_palette
from viewport_pack import decode_icn_indices
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
AGG = ROOT / "Assets" / "Original" / "DATA" / "HEROES2.AGG"
TRANSPARENT = 0

# Константы StandardWindow (ui_window.cpp:35-44)
borderSize = 16
borderEdgeOffset = 43
transitionSize = 10
backgroundOffset = 22
# DialogBattleSummary (battle_dialogs.cpp:79-80,490,495,498-499)
bsTextWidth = 303

agg, ent = read_agg_index_with_expansion(AGG)
PAL = read_palette(agg_entry(agg, ent, "KB.PAL"))


def spr(name, fr=0):
    h, e = read_icn(agg_entry(agg, ent, name))[fr]
    return decode_icn_indices(h, e), h["w"], h["h"], h.get("ox", 0), h.get("oy", 0)


def blit(canvas, CW, CH, src, sw, sx, sy, dx, dy, w, h, opaque=True):
    """Копия региона src[sx,sy,w,h] -> canvas[dx,dy]. opaque=False пропускает TRANSPARENT."""
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
            canvas[yy * CW + xx] = v


def make_standard_window(activeW, activeH):
    V, VW, VH, _, _ = spr("WINLOSE.ICN")        # vertical border (+ углы)
    Hs, HW, HH, _, _ = spr("SURDRBKG.ICN")      # horizontal border
    S, SW, SH, _, _ = spr("STONEBAK.ICN")       # фон
    waW = activeW + 2 * borderSize
    waH = activeH + 2 * borderSize
    CW, CH = waW, waH
    cv = bytearray([TRANSPARENT]) * (CW * CH)
    cornerSize = backgroundOffset                      # hasBackground -> 22
    hsW = HW - borderSize
    hsH = HH - borderSize
    rcoX = waW - cornerSize
    bcoY = waH - cornerSize
    rcsX = VW - cornerSize
    bcsY = VH - cornerSize
    # 1) фон STONEBAK (renderBackgroundImage), borderOffset=22, тайлинг копиями
    bw = waW - backgroundOffset * 2
    bh = waH - backgroundOffset * 2
    yy = 0
    while yy < bh:
        xx = 0
        ch = min(SH, bh - yy)
        while xx < bw:
            cwid = min(SW, bw - xx)
            blit(cv, CW, CH, S, SW, 0, 0, backgroundOffset + xx, backgroundOffset + yy, cwid, ch)
            xx += SW
        yy += SH
    # 2) углы (verticalSprite WINLOSE)
    blit(cv, CW, CH, V, VW, 0, 0, 0, 0, cornerSize, cornerSize)
    blit(cv, CW, CH, V, VW, rcsX, 0, rcoX, 0, cornerSize, cornerSize)
    blit(cv, CW, CH, V, VW, 0, bcsY, 0, bcoY, cornerSize, cornerSize)
    blit(cv, CW, CH, V, VW, rcsX, bcsY, rcoX, bcoY, cornerSize, cornerSize)
    extra = borderEdgeOffset - cornerSize              # 21
    coX, coY = cornerSize, cornerSize
    rbe = VW - borderEdgeOffset
    bbe = VH - borderEdgeOffset
    blit(cv, CW, CH, V, VW, cornerSize, 0, coX, 0, extra, cornerSize)
    blit(cv, CW, CH, V, VW, 0, cornerSize, 0, coY, cornerSize, extra)
    blit(cv, CW, CH, V, VW, rbe, 0, rcoX - extra, 0, extra, cornerSize)
    blit(cv, CW, CH, V, VW, rcsX, cornerSize, rcoX, coY, cornerSize, extra)
    blit(cv, CW, CH, V, VW, cornerSize, bcsY, coX, bcoY, extra, cornerSize)
    blit(cv, CW, CH, V, VW, 0, bbe, 0, bcoY - extra, cornerSize, extra)
    blit(cv, CW, CH, V, VW, rbe, bcsY, rcoX - extra, bcoY, extra, cornerSize)
    blit(cv, CW, CH, V, VW, rcsX, bbe, rcoX, bcoY - extra, cornerSize, extra)
    # 3) вертикальные края (WINLOSE), повтор копиями
    dbe = borderEdgeOffset * 2
    vch = min(waH, VH) - dbe
    tbe = borderEdgeOffset
    blit(cv, CW, CH, V, VW, 0, borderEdgeOffset, 0, tbe, cornerSize, vch)
    blit(cv, CW, CH, V, VW, rcsX, borderEdgeOffset, rcoX, tbe, cornerSize, vch)
    vcopies = (waH - dbe - 1 - transitionSize) // (bbe - borderEdgeOffset - transitionSize)
    toY = borderEdgeOffset + vch
    stepY = vch - transitionSize
    fromY = borderEdgeOffset + transitionSize
    for _ in range(max(0, vcopies)):
        chh = min(vch, waH - borderEdgeOffset - toY)
        if chh <= 0:
            break
        blit(cv, CW, CH, V, VW, 0, fromY, 0, toY, cornerSize, chh)
        blit(cv, CW, CH, V, VW, rcsX, fromY, rcoX, toY, cornerSize, chh)
        toY += stepY
    # 4) горизонтальные края (SURDRBKG), повтор копиями
    hcw = min(waW, hsW) - dbe
    hcsX = borderEdgeOffset + borderSize
    lbe = borderEdgeOffset
    bbso = hsH - cornerSize
    blit(cv, CW, CH, Hs, HW, hcsX, 0, lbe, 0, hcw, cornerSize)
    blit(cv, CW, CH, Hs, HW, hcsX, bbso, lbe, bcoY, hcw, cornerSize)
    hcopies = (waW - dbe - 1 - transitionSize) // (hsW - dbe - transitionSize)
    toX = borderEdgeOffset + hcw
    stepX = hcw - transitionSize
    fromX = hcsX + transitionSize
    for _ in range(max(0, hcopies)):
        cwid = min(hcw, waW - borderEdgeOffset - toX)
        if cwid <= 0:
            break
        blit(cv, CW, CH, Hs, HW, fromX, 0, toX, 0, cwid, cornerSize)
        blit(cv, CW, CH, Hs, HW, fromX, bbso, toX, bcoY, cwid, cornerSize)
        toX += stepX
    return cv, CW, CH


def nearest(rgb):
    best, bi = 1 << 30, 0
    for i, p in enumerate(PAL):
        d = (p[0] - rgb[0]) ** 2 + (p[1] - rgb[1]) ** 2 + (p[2] - rgb[2]) ** 2
        if d < best:
            best, bi = d, i
    return bi


def text_w(font, text):
    f = read_icn(agg_entry(agg, ent, font))
    return sum(f[ord(c) - 32][0]["w"] for c in text)


def text_into(cv, CW, CH, font, text, x, y, color):
    """Глифы шрифта font -> canvas сплошным индексом color (непрозрачные пиксели глифа)."""
    f = read_icn(agg_entry(agg, ent, font))
    cx = x
    for c in text:
        h, e = f[ord(c) - 32]
        gi = decode_icn_indices(h, e)
        gw, gh, goy = h["w"], h["h"], h.get("oy", 0)
        for yy in range(gh):
            py = y + goy + yy
            if not (0 <= py < CH):
                continue
            for xx in range(gw):
                if gi[yy * gw + xx] != TRANSPARENT:
                    px = cx + xx
                    if 0 <= px < CW:
                        cv[py * CW + px] = color
        cx += gw


def main():
    activeW, activeH = bsTextWidth + 32, 424
    cv, CW, CH = make_standard_window(activeW, activeH)
    # регион анимации: WINLOSE[0]{43,32,231,133} -> (animRoi.x-4, animRoi.y-4)
    roiX, roiY = borderSize, borderSize
    animX = roiX + (activeW - 231) // 2 + 4
    animY = roiY + 21
    V, VW, VH, _, _ = spr("WINLOSE.ICN")
    blit(cv, CW, CH, V, VW, 43, 32, animX - 4, animY - 4, 231, 133)
    # WINCMBT кадр внутри региона анимации (sky + парад). Кадр 0 + один кадр поверх.
    for fr in (0, 1):
        a, aw, ah, aox, aoy = spr("WINCMBT.ICN", fr)
        print("WINCMBT", fr, "wh", aw, ah, "ox/oy", aox, aoy)
        blit(cv, CW, CH, a, aw, 0, 0, animX + aox, animY + aoy, aw, ah, opaque=(fr != 0))
    # --- Тексты DialogBattleSummary (battle_dialogs.cpp:538-600), наш случай = победа no-hero ---
    YELLOW = nearest((255, 255, 0))
    WHITE = nearest((255, 255, 255))
    sx = roiX + 11                                  # summaryRoi.x
    sw = activeW - 22                               # summaryRoi.width
    sy = roiY + 160                                 # summaryRoi.y (bsTextYOffset)
    # Заголовок жёлтым по центру (normalYellow «A glorious victory!»)
    title = "A glorious victory!"
    text_into(cv, CW, CH, "FONT.ICN", title, sx + (sw - text_w("FONT.ICN", title)) // 2, sy, YELLOW)
    # Блок потерь (smallWhite), casualtiesOffsetY = sy+96
    cofs = sy + 96
    for label, dy in (("Battlefield Casualties", 0), ("Attacker", 15), ("Defender", 75)):
        text_into(cv, CW, CH, "SMALFONT.ICN", label,
                  sx + (sw - text_w("SMALFONT.ICN", label)) // 2, cofs + dy, WHITE)
    # потери None по умолчанию (нет убитых) — позже линии войск drawSingleDetailedMonsterLine
    for dy in (30, 30 + 75):
        text_into(cv, CW, CH, "SMALFONT.ICN", "None",
                  sx + (sw - text_w("SMALFONT.ICN", "None")) // 2, cofs + dy, WHITE)
    # Кнопка OK (BUTTON_SMALL_OKAY_GOOD -> ориг. SYSTEM.ICN OKAY), BOTTOM_CENTER, поля {0,5}
    for okfr in (1,):
        ok, okw, okh, okox, okoy = spr("SYSTEM.ICN", okfr)
        print("SYSTEM.ICN", okfr, "wh", okw, okh)
        bx = roiX + (activeW - okw) // 2
        by = roiY + activeH - okh - 5
        blit(cv, CW, CH, ok, okw, 0, 0, bx, by, okw, okh, opaque=False)
    img = Image.new("RGB", (CW, CH))
    px = img.load()
    for y in range(CH):
        for x in range(CW):
            px[x, y] = PAL[cv[y * CW + x]]
    out = ROOT / "Diagnostics" / "winwnd.png"
    img.save(out)
    print("WINLOSE", VW, VH, "-> окно", CW, CH, "->", out)


if __name__ == "__main__":
    main()
