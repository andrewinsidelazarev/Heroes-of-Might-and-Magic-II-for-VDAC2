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

MENU_LANTERN_FRAMES EQU 10
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
                FT_BITMAP_SOURCE #0A0480
                FT_BITMAP_LAYOUT FT_PALETTED4444, 136, 125
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 218, 200
                FT_VERTEX2F 1229, 6093
MenuSettingsZone:    DEFW 63, 202, 171, 362   ; зона настроек (door highlight)

; Подменю NEW GAME (ориг. HoMM2, геометрия fheroes2 1.0.0 drawButtonPanel)
MenuNgPanel_DL:
                FT_BITMAP_SOURCE #0A46E8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 227, 472
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 364, 756
                FT_BITMAP_SIZE_H 364, 756
                FT_VERTEX2F 10368, 205
                FT_BITMAP_SIZE_H 0, 0             ; сброс (ловушка &511)
MenuNgPanel_DL_SIZE EQU $ - MenuNgPanel_DL
MenuNgBtn_STANDARD_REL_DL:
                FT_BITMAP_SOURCE #0BE970
                FT_BITMAP_LAYOUT FT_PALETTED4444, 132, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 212, 100
                FT_VERTEX2F 11699, 1178
MenuNgBtn_STANDARD_PRS_DL:
                FT_BITMAP_SOURCE #0C0968
                FT_BITMAP_LAYOUT FT_PALETTED4444, 132, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 212, 100
                FT_VERTEX2F 11699, 1178
MenuNgBtn_CAMPAIGN_REL_DL:
                FT_BITMAP_SOURCE #0C2960
                FT_BITMAP_LAYOUT FT_PALETTED4444, 132, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 212, 100
                FT_VERTEX2F 11699, 2867
MenuNgBtn_CAMPAIGN_PRS_DL:
                FT_BITMAP_SOURCE #0C4958
                FT_BITMAP_LAYOUT FT_PALETTED4444, 132, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 212, 100
                FT_VERTEX2F 11699, 2867
MenuNgBtn_MULTI_REL_DL:
                FT_BITMAP_SOURCE #0C6950
                FT_BITMAP_LAYOUT FT_PALETTED4444, 132, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 212, 100
                FT_VERTEX2F 11699, 4557
MenuNgBtn_MULTI_PRS_DL:
                FT_BITMAP_SOURCE #0C8948
                FT_BITMAP_LAYOUT FT_PALETTED4444, 132, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 212, 100
                FT_VERTEX2F 11699, 4557
MenuNgBtn_CANCEL_REL_DL:
                FT_BITMAP_SOURCE #0CA940
                FT_BITMAP_LAYOUT FT_PALETTED4444, 132, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 212, 100
                FT_VERTEX2F 11699, 9626
MenuNgBtn_CANCEL_PRS_DL:
                FT_BITMAP_SOURCE #0CC938
                FT_BITMAP_LAYOUT FT_PALETTED4444, 132, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 212, 100
                FT_VERTEX2F 11699, 9626
MENU_NG_BUTTON_COUNT EQU 4
MenuNgBtnTab:                        ; на кнопку 2 указателя: released, pressed
                DEFW MenuNgBtn_STANDARD_REL_DL, MenuNgBtn_STANDARD_PRS_DL
                DEFW MenuNgBtn_CAMPAIGN_REL_DL, MenuNgBtn_CAMPAIGN_PRS_DL
                DEFW MenuNgBtn_MULTI_REL_DL, MenuNgBtn_MULTI_PRS_DL
                DEFW MenuNgBtn_CANCEL_REL_DL, MenuNgBtn_CANCEL_PRS_DL
MenuNgZones:                         ; зоны hit-test (x0,y0,x1,y1 логич.)
                DEFW 457, 46, 589, 108   ; STANDARD
                DEFW 457, 112, 589, 174   ; CAMPAIGN
                DEFW 457, 178, 589, 240   ; MULTI
                DEFW 457, 376, 589, 438   ; CANCEL

; запись: x0,y0,x1,y1 (4×2б). Индекс зоны = индекс кнопки (0=New Game).
MenuButtonZones:
                DEFW 482, 176, 563, 289   ; [ 1] NEW_GAME
                DEFW 195, 180, 275, 257   ; [ 5] LOAD_GAME
                DEFW 408, 107, 488, 183   ; [ 9] HIGH_SCORES
                DEFW 303, 137, 379, 180   ; [13] CREDITS
                DEFW 0, 425, 86, 469   ; [17] QUIT

; Экран сценария (ChooseNewMap) = ОКНО-ПОВЕРХ меню: фон = MenuBg_DL, база фонаря =
; MenuLanternBase_DL; панель @ #064840 (область кадров фонаря). Тень = глоб. Render_WindowShadowDL.
ScenPanel_DL:
                FT_PALETTE_SOURCE #000000
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #064840
                FT_BITMAP_LAYOUT FT_PALETTED4444, 319, 319
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 511, 511
                FT_VERTEX2F 2816, 666
                FT_BITMAP_SOURCE #07D5C4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 101, 319
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 162, 511
                FT_VERTEX2F 10982, 666
                FT_BITMAP_SOURCE #0853A0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 319, 108
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 511, 173
                FT_VERTEX2F 2816, 8832
                FT_BITMAP_SOURCE #08DA34
                FT_BITMAP_LAYOUT FT_PALETTED4444, 101, 108
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 162, 173
                FT_VERTEX2F 10982, 8832
                FT_END
ScenPanel_DL_SIZE EQU $ - ScenPanel_DL
ScenSpritesProlog_DL:
                FT_PALETTE_SOURCE #000000
                FT_BEGIN FT_BITMAPS
ScenSpritesProlog_DL_SIZE EQU $ - ScenSpritesProlog_DL
ScenSpritesEnd_DL:
                FT_END
ScenSpritesEnd_DL_SIZE EQU $ - ScenSpritesEnd_DL
ScenCursor0_DL:
                FT_BITMAP_SOURCE #0904D0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 71, 71
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 114, 114
                FT_VERTEX2F 3277, 2918
ScenCursor1_DL:
                FT_BITMAP_SOURCE #0904D0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 71, 71
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 114, 114
                FT_VERTEX2F 5248, 2918
ScenCursor2_DL:
                FT_BITMAP_SOURCE #0904D0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 71, 71
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 114, 114
                FT_VERTEX2F 7194, 2918
ScenCursor3_DL:
                FT_BITMAP_SOURCE #0904D0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 71, 71
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 114, 114
                FT_VERTEX2F 9165, 2918
ScenCursor4_DL:
                FT_BITMAP_SOURCE #0904D0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 71, 71
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 114, 114
                FT_VERTEX2F 11136, 2918
ScenCursorTab:                       ; [difficulty] → DL-блок рамки
                DEFW ScenCursor0_DL
                DEFW ScenCursor1_DL
                DEFW ScenCursor2_DL
                DEFW ScenCursor3_DL
                DEFW ScenCursor4_DL
ScenOkPressed_DL:
                FT_BITMAP_SOURCE #091884
                FT_BITMAP_LAYOUT FT_PALETTED4444, 95, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 152, 40
                FT_VERTEX2F 3610, 10394
ScenCancelPressed_DL:
                FT_BITMAP_SOURCE #0921CC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 95, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 152, 40
                FT_VERTEX2F 10163, 10394
ScenRating0_DL:
                FT_BITMAP_SOURCE #092B14
                FT_BITMAP_LAYOUT FT_PALETTED4444, 89, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 143, 26
                FT_VERTEX2F 7040, 10522
ScenRating1_DL:
                FT_BITMAP_SOURCE #0930A4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 95, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 152, 26
                FT_VERTEX2F 6963, 10522
ScenRating2_DL:
                FT_BITMAP_SOURCE #093694
                FT_BITMAP_LAYOUT FT_PALETTED4444, 94, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 151, 26
                FT_VERTEX2F 6989, 10522
ScenRating3_DL:
                FT_BITMAP_SOURCE #093C74
                FT_BITMAP_LAYOUT FT_PALETTED4444, 95, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 152, 26
                FT_VERTEX2F 6963, 10522
ScenRating4_DL:
                FT_BITMAP_SOURCE #094264
                FT_BITMAP_LAYOUT FT_PALETTED4444, 94, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 151, 26
                FT_VERTEX2F 6989, 10522
ScenRatingTab:                       ; [difficulty] → DL-блок «Rating N%»
                DEFW ScenRating0_DL
                DEFW ScenRating1_DL
                DEFW ScenRating2_DL
                DEFW ScenRating3_DL
                DEFW ScenRating4_DL
MENU_SCEN_DIFF_COUNT EQU 5
ScenDiffZones:                       ; зоны иконок сложности (x0,y0,x1,y1 логич.)
                DEFW 131, 117, 202, 188
                DEFW 208, 117, 279, 188
                DEFW 284, 117, 355, 188
                DEFW 361, 117, 432, 188
                DEFW 438, 117, 509, 188
ScenOkZone:     DEFW 141, 406, 236, 431
ScenCancelZone: DEFW 397, 406, 492, 431
SCEN_PAYLOAD_SECTORS EQU 385
SCEN_BODY_SECTOR     EQU 1654

SCEN_HELP_AREA       EQU #090BC4   ; свободная зона стрима справка-окна
MENU_SCEN_HELP_COUNT EQU 7
ScenHelpSecTab: DEFW 2039, 2147, 2311, 2447, 2555, 2663, 2827
ScenHelpSecN:   DEFB 108, 164, 136, 108, 108, 164, 164
ScenHelpPre_DL:                       ; общий пролог всех окон справок (transp — фон вокруг рамки прозрачен)
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_PALETTE_SOURCE MENU_TRANSPARENT_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE SCEN_HELP_AREA
ScenHelpPre_DL_SIZE EQU $ - ScenHelpPre_DL
ScenHelp0_DL:                       ; LAYOUT/SIZE/VERTEX окна 0 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 288
                FT_BITMAP_SIZE_H 489, 288
                FT_VERTEX2F 4275, 3840
ScenHelp1_DL:                       ; LAYOUT/SIZE/VERTEX окна 1 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 274
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 438
                FT_BITMAP_SIZE_H 489, 438
                FT_VERTEX2F 4275, 2636
ScenHelp2_DL:                       ; LAYOUT/SIZE/VERTEX окна 2 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 226
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 361
                FT_BITMAP_SIZE_H 489, 361
                FT_VERTEX2F 4275, 3251
ScenHelp3_DL:                       ; LAYOUT/SIZE/VERTEX окна 3 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 288
                FT_BITMAP_SIZE_H 489, 288
                FT_VERTEX2F 4275, 3840
ScenHelp4_DL:                       ; LAYOUT/SIZE/VERTEX окна 4 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 288
                FT_BITMAP_SIZE_H 489, 288
                FT_VERTEX2F 4275, 3840
ScenHelp5_DL:                       ; LAYOUT/SIZE/VERTEX окна 5 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 274
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 438
                FT_BITMAP_SIZE_H 489, 438
                FT_VERTEX2F 4275, 2636
ScenHelp6_DL:                       ; LAYOUT/SIZE/VERTEX окна 6 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 274
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 438
                FT_BITMAP_SIZE_H 489, 438
                FT_VERTEX2F 4275, 2636
SCEN_HELP_DL_SIZE EQU $ - ScenHelp6_DL   ; per-окно размер одинаков (4 команды)
ScenHelpDLTab:  DEFW ScenHelp0_DL, ScenHelp1_DL, ScenHelp2_DL, ScenHelp3_DL, ScenHelp4_DL, ScenHelp5_DL, ScenHelp6_DL
ScenHelpZones:                       ; [idx] → x0,y0,x1,y1 (логич.) для right-click
                DEFW 419, 71, 499, 90
                DEFW 131, 117, 509, 188
                DEFW 260, 411, 380, 427
                DEFW 141, 406, 236, 431
                DEFW 397, 406, 492, 431
                DEFW 289, 223, 351, 281
                DEFW 289, 307, 351, 352

MENU_RAMG_BASE       EQU #000000
MENU_PAYLOAD_BYTES   EQU 846128
MENU_PAYLOAD_SECTORS EQU 1653
MENU_BODY_SECTOR     EQU 1   ; payload начинается с этого сектора файла
MenuPakName:         DEFB "HMM2MENU.PAK", 0

                endif