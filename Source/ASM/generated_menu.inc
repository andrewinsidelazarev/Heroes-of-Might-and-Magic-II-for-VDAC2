; Сгенерировано Source/Tools/menu_pack.py — ассеты главного меню (hover/pressed + фонарь).
                ifndef _HMM2_GENERATED_MENU_
                define _HMM2_GENERATED_MENU_

MENU_TRANSPARENT_PAL_RAMG EQU #000000
MENU_OPAQUE_PAL_RAMG      EQU #000200
MENU_SPRITE_DL_SIZE       EQU 16

MenuBg_DL:
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
MenuBg_DL_SIZE EQU $ - MenuBg_DL

MenuSpritesProlog_DL:
                FT_PALETTE_SOURCE MENU_TRANSPARENT_PAL_RAMG
                FT_BEGIN FT_BITMAPS
MenuSpritesProlog_DL_SIZE EQU $ - MenuSpritesProlog_DL
MenuSpritesEnd_DL:
                FT_END
MenuSpritesEnd_DL_SIZE EQU $ - MenuSpritesEnd_DL

MenuLanternBase_DL:
                FT_BITMAP_SOURCE #06011C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 139, 131
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 223, 210
                FT_VERTEX2F 1178, 4506

MenuLantern_0_DL:
                FT_BITMAP_SOURCE #064840
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685
MenuLantern_1_DL:
                FT_BITMAP_SOURCE #06A7E0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685
MenuLantern_2_DL:
                FT_BITMAP_SOURCE #070780
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685
MenuLantern_3_DL:
                FT_BITMAP_SOURCE #076720
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685
MenuLantern_4_DL:
                FT_BITMAP_SOURCE #07C6C0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685
MenuLantern_5_DL:
                FT_BITMAP_SOURCE #082660
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685
MenuLantern_6_DL:
                FT_BITMAP_SOURCE #088600
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685
MenuLantern_7_DL:
                FT_BITMAP_SOURCE #08E5A0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685
MenuLantern_8_DL:
                FT_BITMAP_SOURCE #094540
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685
MenuLantern_9_DL:
                FT_BITMAP_SOURCE #09A4E0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685
MenuLantern_10_DL:
                FT_BITMAP_SOURCE #0A0480
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685
MenuLantern_11_DL:
                FT_BITMAP_SOURCE #0A6420
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685
MenuLantern_12_DL:
                FT_BITMAP_SOURCE #0AC3C0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 288
                FT_VERTEX2F 1229, 4685

MENU_LANTERN_FRAMES EQU 13
MENU_LANTERN_SHIFT  EQU 2
MenuLanternFrameTab:
                DEFW MenuLantern_0_DL
                DEFW MenuLantern_1_DL
                DEFW MenuLantern_2_DL
                DEFW MenuLantern_3_DL
                DEFW MenuLantern_4_DL
                DEFW MenuLantern_5_DL
                DEFW MenuLantern_6_DL
                DEFW MenuLantern_7_DL
                DEFW MenuLantern_8_DL
                DEFW MenuLantern_9_DL
                DEFW MenuLantern_10_DL
                DEFW MenuLantern_11_DL
                DEFW MenuLantern_12_DL

MenuBtn_NEW_GAME_REL_DL:
                FT_BITMAP_SOURCE #04B40C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 81, 113
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 130, 181
                FT_VERTEX2F 12339, 4506
MenuBtn_NEW_GAME_HOVER_DL:
                FT_BITMAP_SOURCE #04D7D0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 81, 113
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 130, 181
                FT_VERTEX2F 12339, 4506
MenuBtn_NEW_GAME_PRESSED_DL:
                FT_BITMAP_SOURCE #04FB94
                FT_BITMAP_LAYOUT FT_PALETTED4444, 81, 113
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 130, 181
                FT_VERTEX2F 12339, 4506
MenuBtn_LOAD_GAME_REL_DL:
                FT_BITMAP_SOURCE #051F58
                FT_BITMAP_LAYOUT FT_PALETTED4444, 80, 77
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 128, 124
                FT_VERTEX2F 4992, 4608
MenuBtn_LOAD_GAME_HOVER_DL:
                FT_BITMAP_SOURCE #053768
                FT_BITMAP_LAYOUT FT_PALETTED4444, 80, 77
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 128, 124
                FT_VERTEX2F 4992, 4608
MenuBtn_LOAD_GAME_PRESSED_DL:
                FT_BITMAP_SOURCE #054F78
                FT_BITMAP_LAYOUT FT_PALETTED4444, 80, 77
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 128, 124
                FT_VERTEX2F 4992, 4608
MenuBtn_HIGH_SCORES_REL_DL:
                FT_BITMAP_SOURCE #056788
                FT_BITMAP_LAYOUT FT_PALETTED4444, 80, 76
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 128, 122
                FT_VERTEX2F 10445, 2739
MenuBtn_HIGH_SCORES_HOVER_DL:
                FT_BITMAP_SOURCE #057F48
                FT_BITMAP_LAYOUT FT_PALETTED4444, 80, 76
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 128, 122
                FT_VERTEX2F 10445, 2739
MenuBtn_HIGH_SCORES_PRESSED_DL:
                FT_BITMAP_SOURCE #059708
                FT_BITMAP_LAYOUT FT_PALETTED4444, 80, 75
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 128, 120
                FT_VERTEX2F 10445, 2739
MenuBtn_CREDITS_REL_DL:
                FT_BITMAP_SOURCE #05AE78
                FT_BITMAP_LAYOUT FT_PALETTED4444, 76, 43
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 122, 69
                FT_VERTEX2F 7757, 3507
MenuBtn_CREDITS_HOVER_DL:
                FT_BITMAP_SOURCE #05BB3C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 76, 43
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 122, 69
                FT_VERTEX2F 7757, 3507
MenuBtn_CREDITS_PRESSED_DL:
                FT_BITMAP_SOURCE #05C800
                FT_BITMAP_LAYOUT FT_PALETTED4444, 76, 43
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 122, 69
                FT_VERTEX2F 7757, 3507
MenuBtn_QUIT_REL_DL:
                FT_BITMAP_SOURCE #05D4C4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 86, 44
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 138, 71
                FT_VERTEX2F 0, 10880
MenuBtn_QUIT_HOVER_DL:
                FT_BITMAP_SOURCE #05E38C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 86, 44
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 138, 71
                FT_VERTEX2F 0, 10880
MenuBtn_QUIT_PRESSED_DL:
                FT_BITMAP_SOURCE #05F254
                FT_BITMAP_LAYOUT FT_PALETTED4444, 86, 44
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 138, 71
                FT_VERTEX2F 0, 10880

MENU_BUTTON_COUNT EQU 5
; на кнопку 3 указателя на 16-байтные DL-блоки: released, hover, pressed.
MenuBtnFrameTab:
                DEFW MenuBtn_NEW_GAME_REL_DL, MenuBtn_NEW_GAME_HOVER_DL, MenuBtn_NEW_GAME_PRESSED_DL
                DEFW MenuBtn_LOAD_GAME_REL_DL, MenuBtn_LOAD_GAME_HOVER_DL, MenuBtn_LOAD_GAME_PRESSED_DL
                DEFW MenuBtn_HIGH_SCORES_REL_DL, MenuBtn_HIGH_SCORES_HOVER_DL, MenuBtn_HIGH_SCORES_PRESSED_DL
                DEFW MenuBtn_CREDITS_REL_DL, MenuBtn_CREDITS_HOVER_DL, MenuBtn_CREDITS_PRESSED_DL
                DEFW MenuBtn_QUIT_REL_DL, MenuBtn_QUIT_HOVER_DL, MenuBtn_QUIT_PRESSED_DL

MenuDoor_DL:
                FT_BITMAP_SOURCE #0B2360
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 125
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 200
                FT_VERTEX2F 1229, 6093
MenuSettingsZone:    DEFW 63, 202, 171, 362   ; зона настроек (door highlight)

; запись: x0,y0,x1,y1 (4×2б). Индекс зоны = индекс кнопки (0=New Game).
MenuButtonZones:
                DEFW 482, 176, 563, 289   ; [ 1] NEW_GAME
                DEFW 195, 180, 275, 257   ; [ 5] LOAD_GAME
                DEFW 408, 107, 488, 183   ; [ 9] HIGH_SCORES
                DEFW 303, 137, 379, 180   ; [13] CREDITS
                DEFW 0, 425, 86, 469   ; [17] QUIT

MENU_RAMG_BASE       EQU #000000
MENU_PAYLOAD_BYTES   EQU 746952
MENU_PAYLOAD_SECTORS EQU 1459
MENU_BODY_SECTOR     EQU 1   ; payload начинается с этого сектора файла
MenuPakName:         DEFB "HMM2MENU.PAK", 0

                endif