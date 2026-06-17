; Сгенерировано Source/Tools/menu_pack.py — ассеты главного меню.
                ifndef _HMM2_GENERATED_MENU_
                define _HMM2_GENERATED_MENU_

MENU_TRANSPARENT_PAL_RAMG EQU #000000
MENU_OPAQUE_PAL_RAMG      EQU #000200

MenuScene_DL:
                FT_CLEAR_COLOR_RGB 0, 0, 0
                FT_CLEAR 1, 1, 1
                FT_SCISSOR_XY 0, 0
                FT_SCISSOR_SIZE 1024, 768
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
                FT_BITMAP_HANDLE 0
                FT_CELL 0
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_C 0
                FT_VERTEX_TRANSLATE_X 0
                FT_VERTEX_TRANSLATE_Y 0
                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE MENU_OPAQUE_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #000400
                FT_BITMAP_LAYOUT FT_PALETTED4444, 319, 319
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 511, 511
                FT_VERTEX2F 0, 0
                FT_BITMAP_SOURCE #019184
                FT_BITMAP_LAYOUT FT_PALETTED4444, 319, 319
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 511, 511
                FT_VERTEX2F 8166, 0
                FT_BITMAP_SOURCE #031F08
                FT_BITMAP_LAYOUT FT_PALETTED4444, 2, 319
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 4, 511
                FT_VERTEX2F 16333, 0
                FT_BITMAP_SOURCE #032188
                FT_BITMAP_LAYOUT FT_PALETTED4444, 319, 161
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 511, 258
                FT_VERTEX2F 0, 8166
                FT_BITMAP_SOURCE #03EA28
                FT_BITMAP_LAYOUT FT_PALETTED4444, 319, 161
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 511, 258
                FT_VERTEX2F 8166, 8166
                FT_BITMAP_SOURCE #04B2C8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 2, 161
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 4, 258
                FT_VERTEX2F 16333, 8166
                FT_END
                FT_PALETTE_SOURCE MENU_TRANSPARENT_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #04B40C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 81, 113
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 130, 181
                FT_VERTEX2F 12339, 4506
                FT_BITMAP_SOURCE #04D7D0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 80, 77
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 128, 124
                FT_VERTEX2F 4992, 4608
                FT_BITMAP_SOURCE #04EFE0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 80, 76
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 128, 122
                FT_VERTEX2F 10445, 2739
                FT_BITMAP_SOURCE #0507A0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 76, 43
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 122, 69
                FT_VERTEX2F 7757, 3507
                FT_BITMAP_SOURCE #051464
                FT_BITMAP_LAYOUT FT_PALETTED4444, 86, 44
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 138, 71
                FT_VERTEX2F 0, 10880
                FT_END
MenuScene_DL_SIZE EQU $ - MenuScene_DL

MENU_BUTTON_COUNT EQU 5
; запись: x0,y0,x1,y1 (4×2б). Индекс зоны = индекс кнопки (0=New Game).
MenuButtonZones:
                DEFW 482, 176, 563, 289   ; [ 1] NEW_GAME
                DEFW 195, 180, 275, 257   ; [ 5] LOAD_GAME
                DEFW 408, 107, 488, 183   ; [ 9] HIGH_SCORES
                DEFW 303, 137, 379, 180   ; [13] CREDITS
                DEFW 0, 425, 86, 469   ; [17] QUIT

MENU_RAMG_BASE       EQU #000000
MENU_PAYLOAD_BYTES   EQU 336684
MENU_PAYLOAD_SECTORS EQU 658
MENU_BODY_SECTOR     EQU 1   ; payload начинается с этого сектора файла
MenuPakName:         DEFB "HMM2MENU.PAK", 0

                endif