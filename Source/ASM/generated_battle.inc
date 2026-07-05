; Сгенерировано Source/Tools/battle_pack.py — экран боя (Grass, потоковый HMM2BATL.PAK).
                ifndef _HMM2_GENERATED_BATTLE_
                define _HMM2_GENERATED_BATTLE_

BATTLE_PAL_RAMG      EQU #000000
BATTLE_TOP_RAMG      EQU #051264
BATTLE_BOT_RAMG      EQU #076A64
BATTLE_SHADOW_PAL_RAMG EQU #000580
BATTLE_SHADOW_RAMG   EQU #0005A0
BATTLE_CONTOUR_PAL_RAMG EQU #000E90

Battle_DL:
                FT_CLEAR_COLOR_RGB 0, 0, 0
                FT_CLEAR 1, 1, 1
                FT_SCISSOR_XY 0, 0
                FT_SCISSOR_SIZE 1024, 768
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
                FT_BITMAP_HANDLE 0
                FT_CELL 0
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_VERTEX_TRANSLATE_X 0
                FT_VERTEX_TRANSLATE_Y 0
                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE BATTLE_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE BATTLE_TOP_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 640, 240
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 1024, 384
                FT_VERTEX2F 0, 0
                FT_BITMAP_SOURCE BATTLE_BOT_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 640, 240
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 1024, 384
                FT_VERTEX2F 0, 6144
                FT_END
Battle_DL_SIZE EQU $ - Battle_DL

Battle_HL_Pre_DL:
                FT_COLOR_RGB 255, 255, 0
                FT_COLOR_A 90
                FT_LINE_WIDTH 16
                FT_BEGIN FT_RECTS
Battle_HL_Pre_DL_SIZE EQU $ - Battle_HL_Pre_DL
Battle_HL_Active_Pre_DL:
                FT_COLOR_RGB 0, 255, 0
                FT_COLOR_A 90
                FT_LINE_WIDTH 16
                FT_BEGIN FT_RECTS
Battle_HL_Active_Pre_DL_SIZE EQU $ - Battle_HL_Active_Pre_DL
Battle_HL_Post_DL:
                FT_END
                FT_COLOR_A 255
                FT_COLOR_RGB 255, 255, 255
Battle_HL_Post_DL_SIZE EQU $ - Battle_HL_Post_DL
BattleCellVerts:                       ; 99 ячеек × 2 FT_VERTEX2F (8Б/ячейка), физ.×1.6
                FT_VERTEX2F 2278, 1587
                FT_VERTEX2F 3404, 2918
                FT_VERTEX2F 3404, 1587
                FT_VERTEX2F 4531, 2918
                FT_VERTEX2F 4531, 1587
                FT_VERTEX2F 5657, 2918
                FT_VERTEX2F 5657, 1587
                FT_VERTEX2F 6784, 2918
                FT_VERTEX2F 6784, 1587
                FT_VERTEX2F 7910, 2918
                FT_VERTEX2F 7910, 1587
                FT_VERTEX2F 9036, 2918
                FT_VERTEX2F 9036, 1587
                FT_VERTEX2F 10163, 2918
                FT_VERTEX2F 10163, 1587
                FT_VERTEX2F 11289, 2918
                FT_VERTEX2F 11289, 1587
                FT_VERTEX2F 12416, 2918
                FT_VERTEX2F 12416, 1587
                FT_VERTEX2F 13542, 2918
                FT_VERTEX2F 13542, 1587
                FT_VERTEX2F 14668, 2918
                FT_VERTEX2F 1715, 2662
                FT_VERTEX2F 2841, 3993
                FT_VERTEX2F 2841, 2662
                FT_VERTEX2F 3968, 3993
                FT_VERTEX2F 3968, 2662
                FT_VERTEX2F 5094, 3993
                FT_VERTEX2F 5094, 2662
                FT_VERTEX2F 6220, 3993
                FT_VERTEX2F 6220, 2662
                FT_VERTEX2F 7347, 3993
                FT_VERTEX2F 7347, 2662
                FT_VERTEX2F 8473, 3993
                FT_VERTEX2F 8473, 2662
                FT_VERTEX2F 9600, 3993
                FT_VERTEX2F 9600, 2662
                FT_VERTEX2F 10726, 3993
                FT_VERTEX2F 10726, 2662
                FT_VERTEX2F 11852, 3993
                FT_VERTEX2F 11852, 2662
                FT_VERTEX2F 12979, 3993
                FT_VERTEX2F 12979, 2662
                FT_VERTEX2F 14105, 3993
                FT_VERTEX2F 2278, 3737
                FT_VERTEX2F 3404, 5068
                FT_VERTEX2F 3404, 3737
                FT_VERTEX2F 4531, 5068
                FT_VERTEX2F 4531, 3737
                FT_VERTEX2F 5657, 5068
                FT_VERTEX2F 5657, 3737
                FT_VERTEX2F 6784, 5068
                FT_VERTEX2F 6784, 3737
                FT_VERTEX2F 7910, 5068
                FT_VERTEX2F 7910, 3737
                FT_VERTEX2F 9036, 5068
                FT_VERTEX2F 9036, 3737
                FT_VERTEX2F 10163, 5068
                FT_VERTEX2F 10163, 3737
                FT_VERTEX2F 11289, 5068
                FT_VERTEX2F 11289, 3737
                FT_VERTEX2F 12416, 5068
                FT_VERTEX2F 12416, 3737
                FT_VERTEX2F 13542, 5068
                FT_VERTEX2F 13542, 3737
                FT_VERTEX2F 14668, 5068
                FT_VERTEX2F 1715, 4812
                FT_VERTEX2F 2841, 6144
                FT_VERTEX2F 2841, 4812
                FT_VERTEX2F 3968, 6144
                FT_VERTEX2F 3968, 4812
                FT_VERTEX2F 5094, 6144
                FT_VERTEX2F 5094, 4812
                FT_VERTEX2F 6220, 6144
                FT_VERTEX2F 6220, 4812
                FT_VERTEX2F 7347, 6144
                FT_VERTEX2F 7347, 4812
                FT_VERTEX2F 8473, 6144
                FT_VERTEX2F 8473, 4812
                FT_VERTEX2F 9600, 6144
                FT_VERTEX2F 9600, 4812
                FT_VERTEX2F 10726, 6144
                FT_VERTEX2F 10726, 4812
                FT_VERTEX2F 11852, 6144
                FT_VERTEX2F 11852, 4812
                FT_VERTEX2F 12979, 6144
                FT_VERTEX2F 12979, 4812
                FT_VERTEX2F 14105, 6144
                FT_VERTEX2F 2278, 5888
                FT_VERTEX2F 3404, 7219
                FT_VERTEX2F 3404, 5888
                FT_VERTEX2F 4531, 7219
                FT_VERTEX2F 4531, 5888
                FT_VERTEX2F 5657, 7219
                FT_VERTEX2F 5657, 5888
                FT_VERTEX2F 6784, 7219
                FT_VERTEX2F 6784, 5888
                FT_VERTEX2F 7910, 7219
                FT_VERTEX2F 7910, 5888
                FT_VERTEX2F 9036, 7219
                FT_VERTEX2F 9036, 5888
                FT_VERTEX2F 10163, 7219
                FT_VERTEX2F 10163, 5888
                FT_VERTEX2F 11289, 7219
                FT_VERTEX2F 11289, 5888
                FT_VERTEX2F 12416, 7219
                FT_VERTEX2F 12416, 5888
                FT_VERTEX2F 13542, 7219
                FT_VERTEX2F 13542, 5888
                FT_VERTEX2F 14668, 7219
                FT_VERTEX2F 1715, 6963
                FT_VERTEX2F 2841, 8294
                FT_VERTEX2F 2841, 6963
                FT_VERTEX2F 3968, 8294
                FT_VERTEX2F 3968, 6963
                FT_VERTEX2F 5094, 8294
                FT_VERTEX2F 5094, 6963
                FT_VERTEX2F 6220, 8294
                FT_VERTEX2F 6220, 6963
                FT_VERTEX2F 7347, 8294
                FT_VERTEX2F 7347, 6963
                FT_VERTEX2F 8473, 8294
                FT_VERTEX2F 8473, 6963
                FT_VERTEX2F 9600, 8294
                FT_VERTEX2F 9600, 6963
                FT_VERTEX2F 10726, 8294
                FT_VERTEX2F 10726, 6963
                FT_VERTEX2F 11852, 8294
                FT_VERTEX2F 11852, 6963
                FT_VERTEX2F 12979, 8294
                FT_VERTEX2F 12979, 6963
                FT_VERTEX2F 14105, 8294
                FT_VERTEX2F 2278, 8038
                FT_VERTEX2F 3404, 9369
                FT_VERTEX2F 3404, 8038
                FT_VERTEX2F 4531, 9369
                FT_VERTEX2F 4531, 8038
                FT_VERTEX2F 5657, 9369
                FT_VERTEX2F 5657, 8038
                FT_VERTEX2F 6784, 9369
                FT_VERTEX2F 6784, 8038
                FT_VERTEX2F 7910, 9369
                FT_VERTEX2F 7910, 8038
                FT_VERTEX2F 9036, 9369
                FT_VERTEX2F 9036, 8038
                FT_VERTEX2F 10163, 9369
                FT_VERTEX2F 10163, 8038
                FT_VERTEX2F 11289, 9369
                FT_VERTEX2F 11289, 8038
                FT_VERTEX2F 12416, 9369
                FT_VERTEX2F 12416, 8038
                FT_VERTEX2F 13542, 9369
                FT_VERTEX2F 13542, 8038
                FT_VERTEX2F 14668, 9369
                FT_VERTEX2F 1715, 9113
                FT_VERTEX2F 2841, 10444
                FT_VERTEX2F 2841, 9113
                FT_VERTEX2F 3968, 10444
                FT_VERTEX2F 3968, 9113
                FT_VERTEX2F 5094, 10444
                FT_VERTEX2F 5094, 9113
                FT_VERTEX2F 6220, 10444
                FT_VERTEX2F 6220, 9113
                FT_VERTEX2F 7347, 10444
                FT_VERTEX2F 7347, 9113
                FT_VERTEX2F 8473, 10444
                FT_VERTEX2F 8473, 9113
                FT_VERTEX2F 9600, 10444
                FT_VERTEX2F 9600, 9113
                FT_VERTEX2F 10726, 10444
                FT_VERTEX2F 10726, 9113
                FT_VERTEX2F 11852, 10444
                FT_VERTEX2F 11852, 9113
                FT_VERTEX2F 12979, 10444
                FT_VERTEX2F 12979, 9113
                FT_VERTEX2F 14105, 10444
                FT_VERTEX2F 2278, 10188
                FT_VERTEX2F 3404, 11520
                FT_VERTEX2F 3404, 10188
                FT_VERTEX2F 4531, 11520
                FT_VERTEX2F 4531, 10188
                FT_VERTEX2F 5657, 11520
                FT_VERTEX2F 5657, 10188
                FT_VERTEX2F 6784, 11520
                FT_VERTEX2F 6784, 10188
                FT_VERTEX2F 7910, 11520
                FT_VERTEX2F 7910, 10188
                FT_VERTEX2F 9036, 11520
                FT_VERTEX2F 9036, 10188
                FT_VERTEX2F 10163, 11520
                FT_VERTEX2F 10163, 10188
                FT_VERTEX2F 11289, 11520
                FT_VERTEX2F 11289, 10188
                FT_VERTEX2F 12416, 11520
                FT_VERTEX2F 12416, 10188
                FT_VERTEX2F 13542, 11520
                FT_VERTEX2F 13542, 10188
                FT_VERTEX2F 14668, 11520

Battle_Shadow_Pre_DL:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_PALETTE_SOURCE BATTLE_SHADOW_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE BATTLE_SHADOW_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 44, 52
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 70, 83
Battle_Shadow_Pre_DL_SIZE EQU $ - Battle_Shadow_Pre_DL
Battle_Shadow_Post_DL:
                FT_END
Battle_Shadow_Post_DL_SIZE EQU $ - Battle_Shadow_Post_DL

Battle_Contour_Begin_DL:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_PALETTE_SOURCE BATTLE_CONTOUR_PAL_RAMG
                FT_BEGIN FT_BITMAPS
Battle_Contour_Begin_DL_SIZE EQU $ - Battle_Contour_Begin_DL
Battle_Contour_End_DL:
                FT_VERTEX_TRANSLATE_X 0
                FT_VERTEX_TRANSLATE_Y 0
                FT_END
Battle_Contour_End_DL_SIZE EQU $ - Battle_Contour_End_DL
Battle_Contour_Ofs0_DL:
                FT_VERTEX_TRANSLATE_X 32
                FT_VERTEX_TRANSLATE_Y 0
Battle_Contour_Ofs1_DL:
                FT_VERTEX_TRANSLATE_X -32
                FT_VERTEX_TRANSLATE_Y 0
Battle_Contour_Ofs2_DL:
                FT_VERTEX_TRANSLATE_X 0
                FT_VERTEX_TRANSLATE_Y 32
Battle_Contour_Ofs3_DL:
                FT_VERTEX_TRANSLATE_X 0
                FT_VERTEX_TRANSLATE_Y -32
BATTLE_CONTOUR_OFS_SIZE EQU Battle_Contour_Ofs1_DL - Battle_Contour_Ofs0_DL
BattleContourOfsTab:
                DEFW Battle_Contour_Ofs0_DL, Battle_Contour_Ofs1_DL
                DEFW Battle_Contour_Ofs2_DL, Battle_Contour_Ofs3_DL

BATTLE_STATUS_PAL_RAMG EQU #001090
Battle_Status_Begin_DL:
                FT_BITMAP_TRANSFORM_A 256   ; НАТИВНО (×1): ×1.6 NEAREST рвёт глифы (см. fonts-native-no-1p6-upscale)
                FT_BITMAP_TRANSFORM_E 256
                FT_PALETTE_SOURCE BATTLE_STATUS_PAL_RAMG
                FT_BEGIN FT_BITMAPS
Battle_Status_Begin_DL_SIZE EQU $ - Battle_Status_Begin_DL
Battle_Status_End_DL:
                FT_END
Battle_Status_End_DL_SIZE EQU $ - Battle_Status_End_DL
BattleStatusPreTab:
                DEFW Battle_Status_Pre_0, Battle_Status_Pre_1, Battle_Status_Pre_2, Battle_Status_Pre_3, Battle_Status_Pre_4, Battle_Status_Pre_5, Battle_Status_Pre_6, Battle_Status_Pre_7, Battle_Status_Pre_8, Battle_Status_Pre_9, Battle_Status_Pre_10
Battle_Status_Pre_0:
                FT_BITMAP_SOURCE #001290
                FT_BITMAP_LAYOUT FT_PALETTED4444, 264, 22
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 264, 22
Battle_Status_Pre_1:
                FT_BITMAP_SOURCE #002940
                FT_BITMAP_LAYOUT FT_PALETTED4444, 258, 22
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 22
Battle_Status_Pre_2:
                FT_BITMAP_SOURCE #003F6C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 219, 22
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 219, 22
Battle_Status_Pre_3:
                FT_BITMAP_SOURCE #005240
                FT_BITMAP_LAYOUT FT_PALETTED4444, 213, 22
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 213, 22
Battle_Status_Pre_4:
                FT_BITMAP_SOURCE #006490
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 22
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 72, 22
Battle_Status_Pre_5:
                FT_BITMAP_SOURCE #006AC0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 22
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 72, 22
Battle_Status_Pre_6:
                FT_BITMAP_SOURCE #0070F0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 251, 22
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 251, 22
Battle_Status_Pre_7:
                FT_BITMAP_SOURCE #008684
                FT_BITMAP_LAYOUT FT_PALETTED4444, 245, 22
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 245, 22
Battle_Status_Pre_8:
                FT_BITMAP_SOURCE #009B94
                FT_BITMAP_LAYOUT FT_PALETTED4444, 338, 22
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 338, 22
Battle_Status_Pre_9:
                FT_BITMAP_SOURCE #00B8A0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 341, 27
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 341, 27
Battle_Status_Pre_10:
                FT_BITMAP_SOURCE #00DC98
                FT_BITMAP_LAYOUT FT_PALETTED4444, 174, 27
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 174, 27
BATTLE_STATUS_PRE_SIZE EQU Battle_Status_Pre_1 - Battle_Status_Pre_0
BattleStatusVertTab:                   ; hover = НИЖНЯЯ строка бара (лог.Y≈465), центр X=512
                FT_VERTEX2F 6080, 11904
                FT_VERTEX2F 6128, 11904
                FT_VERTEX2F 6448, 11904
                FT_VERTEX2F 6496, 11904
                FT_VERTEX2F 7616, 11904
                FT_VERTEX2F 7616, 11904
                FT_VERTEX2F 6192, 11904
                FT_VERTEX2F 6240, 11904
                FT_VERTEX2F 5488, 11904
                FT_VERTEX2F 5472, 11904
                FT_VERTEX2F 6800, 11904
BATTLE_STATUS_COUNT EQU 11

EVT_ENTRY_SIZE EQU 5
BattleEvtAtkTab:                       ; «<atk> do/does » idx=type×2+(count==1)
                DEFB #F4, #EE, #00, 166, 22
                DEFB #38, #FD, #00, 181, 22
                DEFB #C8, #0C, #01, 160, 22
                DEFB #88, #1A, #01, 174, 22
BattleEvtDmgSfx:                       ; « damage.»
                DEFB #7C, #29, #01, 117, 27
BattleEvtSpace:                        ; « » (между damage. и числом гибели)
                DEFB #D4, #35, #01, 10, 2
BattleEvtPerishTab:                    ; « <def> perish(es).» idx=type×2+(killed==1)
                DEFB #E8, #35, #01, 222, 27
                DEFB #54, #4D, #01, 237, 27
                DEFB #54, #66, #01, 216, 27
                DEFB #1C, #7D, #01, 230, 27
BattleEvtDigitTab:                     ; «0».. «9» (тот же шрифт, что слова)
                DEFB #60, #95, #01, 14, 22
                DEFB #94, #96, #01, 8, 22
                DEFB #44, #97, #01, 13, 22
                DEFB #64, #98, #01, 13, 22
                DEFB #84, #99, #01, 14, 22
                DEFB #B8, #9A, #01, 13, 22
                DEFB #D8, #9B, #01, 13, 22
                DEFB #F8, #9C, #01, 13, 22
                DEFB #18, #9E, #01, 13, 22
                DEFB #38, #9F, #01, 13, 22
BattleEvtMoveHead:                     ; «Moved »
                DEFB #58, #A0, #01, 94, 22
BattleEvtMoveNameTab:                  ; «Peasants: »/«Archers: » idx=type
                DEFB #6C, #A8, #01, 131, 22
                DEFB #B0, #B3, #01, 125, 22
BattleEvtMoveFrom:                     ; «from [»
                DEFB #70, #BE, #01, 85, 22
BattleEvtMoveMid:                      ; «] to [»
                DEFB #C0, #C5, #01, 64, 22
BattleEvtMoveEnd:                      ; «].»
                DEFB #40, #CB, #01, 14, 22
BattleEvtComma:                        ; «, » (между row и col)
                DEFB #74, #CC, #01, 16, 24
BattleEvtMoveDigitTab:                 ; нативные цифры «0».. «9» для координат движения
                DEFB #F4, #CD, #01, 14, 22
                DEFB #28, #CF, #01, 8, 22
                DEFB #D8, #CF, #01, 13, 22
                DEFB #F8, #D0, #01, 13, 22
                DEFB #18, #D2, #01, 14, 22
                DEFB #4C, #D3, #01, 13, 22
                DEFB #6C, #D4, #01, 13, 22
                DEFB #8C, #D5, #01, 13, 22
                DEFB #AC, #D6, #01, 13, 22
                DEFB #CC, #D7, #01, 13, 22
BattleShootHeadTab:                    ; «Shoot Peasants (»/«Shoot Archers (» idx=target.type
                DEFB #EC, #D8, #01, 216, 24
                DEFB #2C, #ED, #01, 210, 24
BattleShootTailPl:                     ; « shots left)»
                DEFB #DC, #00, #02, 141, 24
BattleShootTailSg:                     ; « shot left)» (N==1)
                DEFB #14, #0E, #02, 128, 24

BATTLE_YELLOW_PAL_RAMG EQU #04D11C
Battle_WinTitle_Begin_DL:              ; пролог заголовка победы (жёлтая палитра, нативно)
                FT_BITMAP_TRANSFORM_A 256
                FT_BITMAP_TRANSFORM_E 256
                FT_PALETTE_SOURCE BATTLE_YELLOW_PAL_RAMG
                FT_BEGIN FT_BITMAPS
Battle_WinTitle_Begin_DL_SIZE EQU $ - Battle_WinTitle_Begin_DL
WIN_TEXT_REC EQU 11
BATTLE_WIN_TEXT_COUNT EQU 13
BattleWinTextTab:
                DEFB #1C, #D3, #04, 34, 22, 1
                DEFW 6224, 4812
                DEFB 1      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #08, #D6, #04, 114, 27, 1
                DEFW 6768, 4812
                DEFB 1      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #10, #E2, #04, 99, 27, 1
                DEFW 8592, 4812
                DEFB 1      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #84, #EC, #04, 54, 14, 0
                DEFW 5600, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #78, #EF, #04, 64, 14, 0
                DEFW 6464, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #F8, #F2, #04, 66, 14, 0
                DEFW 7488, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #94, #F6, #04, 18, 14, 0
                DEFW 8544, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #90, #F7, #04, 61, 14, 0
                DEFW 8832, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #E8, #FA, #04, 61, 14, 0
                DEFW 9808, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #40, #FE, #04, 102, 14, 0
                DEFW 6608, 7270
                DEFB 0      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #D4, #03, #05, 96, 14, 0
                DEFW 8240, 7270
                DEFB 0      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #14, #09, #05, 85, 14, 0
                DEFW 7520, 7654
                DEFB 0      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #BC, #0D, #05, 85, 14, 0
                DEFW 7520, 9190
                DEFB 0      ; видимость: 0=всегда, 1=победа, 2=поражение

BATTLE_WIN_DLG_RAMG EQU #022E00
Battle_WinDlg_DL:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 587, 729
                FT_PALETTE_SOURCE BATTLE_UNIT_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE BATTLE_WIN_DLG_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 367, 456
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 587, 729
                FT_VERTEX2F 3481, 307
                FT_BITMAP_SIZE_H 0, 0
                FT_END
Battle_WinDlg_DL_SIZE EQU $ - Battle_WinDlg_DL

BATTLE_UNIT_PAL_RAMG EQU #000200
Battle_Units_Begin_DL:
                FT_PALETTE_SOURCE BATTLE_UNIT_PAL_RAMG
                FT_BEGIN FT_BITMAPS
Battle_Units_Begin_DL_SIZE EQU $ - Battle_Units_Begin_DL
Battle_Units_End_DL:
                FT_END
Battle_Units_End_DL_SIZE EQU $ - Battle_Units_End_DL
BATTLE_NGROUPS EQU 12
BATTLE_GRP_STATIC EQU 0
BATTLE_GRP_IDLE1 EQU 1
BATTLE_GRP_IDLE2 EQU 2
BATTLE_GRP_IDLE3 EQU 3
BATTLE_GRP_MOVE_MAIN EQU 4
BATTLE_GRP_ATTACK2 EQU 5
BATTLE_GRP_ATTACK2_END EQU 6
BATTLE_GRP_SHOOT2 EQU 7
BATTLE_GRP_SHOOT2_END EQU 8
BATTLE_GRP_DEATH EQU 9
BATTLE_GRP_WINCE_UP EQU 10
BATTLE_GRP_WINCE_END EQU 11
BattleFrameSrcTab:                      ; [вариант=type*2+side] → FT_BITMAP_SOURCE ×кадры (4Б)
                DEFW BattleFrameSrc0_0, BattleFrameSrc0_1, BattleFrameSrc1_0, BattleFrameSrc1_1
BattleFrameSrc0_0:
                FT_BITMAP_SOURCE #09C264   ; ICN 1
                FT_BITMAP_SOURCE #09D464   ; ICN 2
                FT_BITMAP_SOURCE #09E664   ; ICN 3
                FT_BITMAP_SOURCE #09F864   ; ICN 4
                FT_BITMAP_SOURCE #0A0A64   ; ICN 5
                FT_BITMAP_SOURCE #0A1BD4   ; ICN 6
                FT_BITMAP_SOURCE #0A2EBC   ; ICN 7
                FT_BITMAP_SOURCE #0A42C4   ; ICN 8
                FT_BITMAP_SOURCE #0A55D4   ; ICN 9
                FT_BITMAP_SOURCE #0A660C   ; ICN 10
                FT_BITMAP_SOURCE #0A7734   ; ICN 11
                FT_BITMAP_SOURCE #0A8B3C   ; ICN 12
                FT_BITMAP_SOURCE #0A9D2C   ; ICN 13
                FT_BITMAP_SOURCE #0AB31C   ; ICN 14
                FT_BITMAP_SOURCE #0AC50C   ; ICN 15
                FT_BITMAP_SOURCE #0AD34C   ; ICN 16
                FT_BITMAP_SOURCE #0AE51C   ; ICN 17
                FT_BITMAP_SOURCE #0AF4DC   ; ICN 18
                FT_BITMAP_SOURCE #0B0964   ; ICN 23
                FT_BITMAP_SOURCE #0B1DEC   ; ICN 24
                FT_BITMAP_SOURCE #0B3274   ; ICN 25
                FT_BITMAP_SOURCE #0B4A5C   ; ICN 26
                FT_BITMAP_SOURCE #0B6864   ; ICN 27
                FT_BITMAP_SOURCE #0B830C   ; ICN 28
                FT_BITMAP_SOURCE #0B9CBC   ; ICN 34
                FT_BITMAP_SOURCE #0BA70C   ; ICN 35
                FT_BITMAP_SOURCE #0BAF8C   ; ICN 36
                FT_BITMAP_SOURCE #0BB684   ; ICN 37
BattleFrameSrc0_1:
                FT_BITMAP_SOURCE #09CB64   ; ICN 1
                FT_BITMAP_SOURCE #09DD64   ; ICN 2
                FT_BITMAP_SOURCE #09EF64   ; ICN 3
                FT_BITMAP_SOURCE #0A0164   ; ICN 4
                FT_BITMAP_SOURCE #0A131C   ; ICN 5
                FT_BITMAP_SOURCE #0A2548   ; ICN 6
                FT_BITMAP_SOURCE #0A38C0   ; ICN 7
                FT_BITMAP_SOURCE #0A4C4C   ; ICN 8
                FT_BITMAP_SOURCE #0A5DF0   ; ICN 9
                FT_BITMAP_SOURCE #0A6EA0   ; ICN 10
                FT_BITMAP_SOURCE #0A8138   ; ICN 11
                FT_BITMAP_SOURCE #0A9434   ; ICN 12
                FT_BITMAP_SOURCE #0AA824   ; ICN 13
                FT_BITMAP_SOURCE #0ABC14   ; ICN 14
                FT_BITMAP_SOURCE #0ACC2C   ; ICN 15
                FT_BITMAP_SOURCE #0ADC34   ; ICN 16
                FT_BITMAP_SOURCE #0AECFC   ; ICN 17
                FT_BITMAP_SOURCE #0AFF20   ; ICN 18
                FT_BITMAP_SOURCE #0B13A8   ; ICN 23
                FT_BITMAP_SOURCE #0B2830   ; ICN 24
                FT_BITMAP_SOURCE #0B3E68   ; ICN 25
                FT_BITMAP_SOURCE #0B5960   ; ICN 26
                FT_BITMAP_SOURCE #0B75B8   ; ICN 27
                FT_BITMAP_SOURCE #0B8FE4   ; ICN 28
                FT_BITMAP_SOURCE #0BA1E4   ; ICN 34
                FT_BITMAP_SOURCE #0BAB4C   ; ICN 35
                FT_BITMAP_SOURCE #0BB308   ; ICN 36
                FT_BITMAP_SOURCE #0BB9F0   ; ICN 37
BattleFrameSrc1_0:
                FT_BITMAP_SOURCE #0BBD5C   ; ICN 1
                FT_BITMAP_SOURCE #0BCEE4   ; ICN 2
                FT_BITMAP_SOURCE #0BDFEC   ; ICN 3
                FT_BITMAP_SOURCE #0BF0F4   ; ICN 4
                FT_BITMAP_SOURCE #0C0174   ; ICN 5
                FT_BITMAP_SOURCE #0C11F4   ; ICN 6
                FT_BITMAP_SOURCE #0C2234   ; ICN 7
                FT_BITMAP_SOURCE #0C3664   ; ICN 8
                FT_BITMAP_SOURCE #0C4624   ; ICN 9
                FT_BITMAP_SOURCE #0C55E4   ; ICN 10
                FT_BITMAP_SOURCE #0C679C   ; ICN 11
                FT_BITMAP_SOURCE #0C7954   ; ICN 12
                FT_BITMAP_SOURCE #0C8AD4   ; ICN 13
                FT_BITMAP_SOURCE #0C995C   ; ICN 14
                FT_BITMAP_SOURCE #0CA79C   ; ICN 15
                FT_BITMAP_SOURCE #0CB484   ; ICN 16
                FT_BITMAP_SOURCE #0CC404   ; ICN 17
                FT_BITMAP_SOURCE #0CD304   ; ICN 18
                FT_BITMAP_SOURCE #0CE55C   ; ICN 19
                FT_BITMAP_SOURCE #0CF9DC   ; ICN 24
                FT_BITMAP_SOURCE #0D156C   ; ICN 25
                FT_BITMAP_SOURCE #0D2DB4   ; ICN 26
                FT_BITMAP_SOURCE #0D43A4   ; ICN 27
                FT_BITMAP_SOURCE #0D5674   ; ICN 32
                FT_BITMAP_SOURCE #0D6824   ; ICN 34
                FT_BITMAP_SOURCE #0D7464   ; ICN 35
                FT_BITMAP_SOURCE #0D8264   ; ICN 39
                FT_BITMAP_SOURCE #0D9064   ; ICN 40
                FT_BITMAP_SOURCE #0DA864   ; ICN 41
                FT_BITMAP_SOURCE #0DC474   ; ICN 45
                FT_BITMAP_SOURCE #0DD534   ; ICN 46
                FT_BITMAP_SOURCE #0DE584   ; ICN 47
                FT_BITMAP_SOURCE #0DF1E4   ; ICN 48
                FT_BITMAP_SOURCE #0DFACC   ; ICN 49
                FT_BITMAP_SOURCE #0E033C   ; ICN 50
BattleFrameSrc1_1:
                FT_BITMAP_SOURCE #0BC620   ; ICN 1
                FT_BITMAP_SOURCE #0BD768   ; ICN 2
                FT_BITMAP_SOURCE #0BE870   ; ICN 3
                FT_BITMAP_SOURCE #0BF934   ; ICN 4
                FT_BITMAP_SOURCE #0C09B4   ; ICN 5
                FT_BITMAP_SOURCE #0C1A14   ; ICN 6
                FT_BITMAP_SOURCE #0C2C4C   ; ICN 7
                FT_BITMAP_SOURCE #0C3E44   ; ICN 8
                FT_BITMAP_SOURCE #0C4E04   ; ICN 9
                FT_BITMAP_SOURCE #0C5EC0   ; ICN 10
                FT_BITMAP_SOURCE #0C7078   ; ICN 11
                FT_BITMAP_SOURCE #0C8214   ; ICN 12
                FT_BITMAP_SOURCE #0C9218   ; ICN 13
                FT_BITMAP_SOURCE #0CA07C   ; ICN 14
                FT_BITMAP_SOURCE #0CAE10   ; ICN 15
                FT_BITMAP_SOURCE #0CBC44   ; ICN 16
                FT_BITMAP_SOURCE #0CCB84   ; ICN 17
                FT_BITMAP_SOURCE #0CDC30   ; ICN 18
                FT_BITMAP_SOURCE #0CEF9C   ; ICN 19
                FT_BITMAP_SOURCE #0D07A4   ; ICN 24
                FT_BITMAP_SOURCE #0D2190   ; ICN 25
                FT_BITMAP_SOURCE #0D38AC   ; ICN 26
                FT_BITMAP_SOURCE #0D4D0C   ; ICN 27
                FT_BITMAP_SOURCE #0D5F4C   ; ICN 32
                FT_BITMAP_SOURCE #0D6E44   ; ICN 34
                FT_BITMAP_SOURCE #0D7B64   ; ICN 35
                FT_BITMAP_SOURCE #0D8964   ; ICN 39
                FT_BITMAP_SOURCE #0D9C64   ; ICN 40
                FT_BITMAP_SOURCE #0DB66C   ; ICN 41
                FT_BITMAP_SOURCE #0DCCD4   ; ICN 45
                FT_BITMAP_SOURCE #0DDD5C   ; ICN 46
                FT_BITMAP_SOURCE #0DEBB4   ; ICN 47
                FT_BITMAP_SOURCE #0DF658   ; ICN 48
                FT_BITMAP_SOURCE #0DFF04   ; ICN 49
                FT_BITMAP_SOURCE #0E0698   ; ICN 50
BattleFrameLayTab:                      ; [тип] → LAYOUT+SIZE ×кадры (8Б; общие для зеркала)
                DEFW BattleFrameLay0, BattleFrameLay1
BattleFrameLay0:
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 57, 102
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 57, 102
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 57, 102
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 57, 102
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 57, 99
                FT_BITMAP_LAYOUT FT_PALETTED4444, 39, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 62, 99
                FT_BITMAP_LAYOUT FT_PALETTED4444, 42, 61
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 67, 97
                FT_BITMAP_LAYOUT FT_PALETTED4444, 40, 61
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 64, 97
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 61
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 97
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 61
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 57, 97
                FT_BITMAP_LAYOUT FT_PALETTED4444, 42, 61
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 67, 97
                FT_BITMAP_LAYOUT FT_PALETTED4444, 37, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 59, 99
                FT_BITMAP_LAYOUT FT_PALETTED4444, 46, 61
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 73, 97
                FT_BITMAP_LAYOUT FT_PALETTED4444, 41, 56
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 65, 89
                FT_BITMAP_LAYOUT FT_PALETTED4444, 38, 48
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 60, 76
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 67
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 107
                FT_BITMAP_LAYOUT FT_PALETTED4444, 28, 72
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 44, 115
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 73
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 57, 116
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 73
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 57, 116
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 73
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 57, 116
                FT_BITMAP_LAYOUT FT_PALETTED4444, 45, 68
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 72, 108
                FT_BITMAP_LAYOUT FT_PALETTED4444, 63, 61
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 100, 97
                FT_BITMAP_LAYOUT FT_PALETTED4444, 55, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 88, 99
                FT_BITMAP_LAYOUT FT_PALETTED4444, 53, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 84, 99
                FT_BITMAP_LAYOUT FT_PALETTED4444, 33, 40
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 64
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 51, 54
                FT_BITMAP_LAYOUT FT_PALETTED4444, 33, 27
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 43
                FT_BITMAP_LAYOUT FT_PALETTED4444, 35, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 56, 40
BattleFrameLay1:
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 66
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 105
                FT_BITMAP_LAYOUT FT_PALETTED4444, 33, 66
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 105
                FT_BITMAP_LAYOUT FT_PALETTED4444, 33, 66
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 105
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 66
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 51, 105
                FT_BITMAP_LAYOUT FT_PALETTED4444, 33, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 102
                FT_BITMAP_LAYOUT FT_PALETTED4444, 33, 63
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 100
                FT_BITMAP_LAYOUT FT_PALETTED4444, 41, 63
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 65, 100
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 63
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 51, 100
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 63
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 51, 100
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 63
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 57, 100
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 63
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 57, 100
                FT_BITMAP_LAYOUT FT_PALETTED4444, 35, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 56, 102
                FT_BITMAP_LAYOUT FT_PALETTED4444, 30, 62
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 48, 99
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 57
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 51, 91
                FT_BITMAP_LAYOUT FT_PALETTED4444, 30, 55
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 48, 88
                FT_BITMAP_LAYOUT FT_PALETTED4444, 31, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 49, 102
                FT_BITMAP_LAYOUT FT_PALETTED4444, 30, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 48, 102
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 69
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 110
                FT_BITMAP_LAYOUT FT_PALETTED4444, 41, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 65, 102
                FT_BITMAP_LAYOUT FT_PALETTED4444, 49, 72
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 78, 115
                FT_BITMAP_LAYOUT FT_PALETTED4444, 45, 69
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 72, 110
                FT_BITMAP_LAYOUT FT_PALETTED4444, 39, 72
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 62, 115
                FT_BITMAP_LAYOUT FT_PALETTED4444, 37, 65
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 59, 104
                FT_BITMAP_LAYOUT FT_PALETTED4444, 39, 58
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 62, 92
                FT_BITMAP_LAYOUT FT_PALETTED4444, 27, 58
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 43, 92
                FT_BITMAP_LAYOUT FT_PALETTED4444, 28, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 44, 102
                FT_BITMAP_LAYOUT FT_PALETTED4444, 28, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 44, 102
                FT_BITMAP_LAYOUT FT_PALETTED4444, 48, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 76, 102
                FT_BITMAP_LAYOUT FT_PALETTED4444, 57, 63
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 91, 100
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 63
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 100
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 58
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 57, 92
                FT_BITMAP_LAYOUT FT_PALETTED4444, 31, 51
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 49, 81
                FT_BITMAP_LAYOUT FT_PALETTED4444, 30, 38
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 48, 60
                FT_BITMAP_LAYOUT FT_PALETTED4444, 40, 27
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 64, 43
                FT_BITMAP_LAYOUT FT_PALETTED4444, 39, 22
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 62, 35
BattleFrameOfsTab:                      ; [вариант] → (ofsX,ofsY) DEFW ×кадры (4Б/кадр)
                DEFW BattleFrameOfs0_0, BattleFrameOfs0_1, BattleFrameOfs1_0, BattleFrameOfs1_1
BattleFrameOfs0_0:
                DEFW -384, -1613   ; ICN 1
                DEFW -384, -1613   ; ICN 2
                DEFW -410, -1613   ; ICN 3
                DEFW -384, -1613   ; ICN 4
                DEFW -358, -1587   ; ICN 5
                DEFW -333, -1587   ; ICN 6
                DEFW -333, -1562   ; ICN 7
                DEFW -51, -1587   ; ICN 8
                DEFW 205, -1587   ; ICN 9
                DEFW 256, -1587   ; ICN 10
                DEFW 307, -1562   ; ICN 11
                DEFW 614, -1587   ; ICN 12
                DEFW -435, -1562   ; ICN 13
                DEFW -461, -1434   ; ICN 14
                DEFW -486, -1229   ; ICN 15
                DEFW -358, -1715   ; ICN 16
                DEFW -333, -1843   ; ICN 17
                DEFW -589, -1869   ; ICN 18
                DEFW -512, -1869   ; ICN 23
                DEFW -333, -1869   ; ICN 24
                DEFW -307, -1741   ; ICN 25
                DEFW -307, -1562   ; ICN 26
                DEFW -307, -1587   ; ICN 27
                DEFW -333, -1587   ; ICN 28
                DEFW -486, -1050   ; ICN 34
                DEFW -435, -947   ; ICN 35
                DEFW -461, -819   ; ICN 36
                DEFW -512, -717   ; ICN 37
BattleFrameOfs0_1:
                DEFW -512, -1613   ; ICN 1
                DEFW -512, -1613   ; ICN 2
                DEFW -486, -1613   ; ICN 3
                DEFW -512, -1613   ; ICN 4
                DEFW -538, -1587   ; ICN 5
                DEFW -640, -1587   ; ICN 6
                DEFW -717, -1562   ; ICN 7
                DEFW -947, -1587   ; ICN 8
                DEFW -1050, -1587   ; ICN 9
                DEFW -1152, -1587   ; ICN 10
                DEFW -1357, -1562   ; ICN 11
                DEFW -1536, -1587   ; ICN 12
                DEFW -717, -1562   ; ICN 13
                DEFW -563, -1434   ; ICN 14
                DEFW -461, -1229   ; ICN 15
                DEFW -486, -1715   ; ICN 16
                DEFW -358, -1843   ; ICN 17
                DEFW -307, -1869   ; ICN 18
                DEFW -384, -1869   ; ICN 23
                DEFW -563, -1869   ; ICN 24
                DEFW -819, -1741   ; ICN 25
                DEFW -1280, -1562   ; ICN 26
                DEFW -1075, -1587   ; ICN 27
                DEFW -998, -1587   ; ICN 28
                DEFW -333, -1050   ; ICN 34
                DEFW -358, -947   ; ICN 35
                DEFW -358, -819   ; ICN 36
                DEFW -358, -717   ; ICN 37
BattleFrameOfs1_0:
                DEFW -461, -1664   ; ICN 1
                DEFW -435, -1664   ; ICN 2
                DEFW -435, -1664   ; ICN 3
                DEFW -410, -1664   ; ICN 4
                DEFW -435, -1638   ; ICN 5
                DEFW -384, -1613   ; ICN 6
                DEFW -307, -1613   ; ICN 7
                DEFW 26, -1638   ; ICN 8
                DEFW 102, -1638   ; ICN 9
                DEFW 154, -1638   ; ICN 10
                DEFW 384, -1613   ; ICN 11
                DEFW 538, -1638   ; ICN 12
                DEFW -384, -1613   ; ICN 13
                DEFW -486, -1485   ; ICN 14
                DEFW -538, -1408   ; ICN 15
                DEFW -410, -1638   ; ICN 16
                DEFW -384, -1638   ; ICN 17
                DEFW -410, -1766   ; ICN 18
                DEFW -512, -1638   ; ICN 19
                DEFW -384, -1843   ; ICN 24
                DEFW -282, -1766   ; ICN 25
                DEFW -282, -1843   ; ICN 26
                DEFW -410, -1664   ; ICN 27
                DEFW -333, -1485   ; ICN 32
                DEFW -333, -1485   ; ICN 34
                DEFW -435, -1638   ; ICN 35
                DEFW -435, -1638   ; ICN 39
                DEFW -410, -1638   ; ICN 40
                DEFW -384, -1613   ; ICN 41
                DEFW -435, -1638   ; ICN 45
                DEFW -410, -1510   ; ICN 46
                DEFW -358, -1357   ; ICN 47
                DEFW -358, -1050   ; ICN 48
                DEFW -486, -768   ; ICN 49
                DEFW -486, -640   ; ICN 50
BattleFrameOfs1_1:
                DEFW -384, -1664   ; ICN 1
                DEFW -384, -1664   ; ICN 2
                DEFW -384, -1664   ; ICN 3
                DEFW -384, -1664   ; ICN 4
                DEFW -384, -1638   ; ICN 5
                DEFW -435, -1613   ; ICN 6
                DEFW -717, -1613   ; ICN 7
                DEFW -819, -1638   ; ICN 8
                DEFW -896, -1638   ; ICN 9
                DEFW -1050, -1638   ; ICN 10
                DEFW -1280, -1613   ; ICN 11
                DEFW -1408, -1638   ; ICN 12
                DEFW -358, -1613   ; ICN 13
                DEFW -307, -1485   ; ICN 14
                DEFW -205, -1408   ; ICN 15
                DEFW -358, -1638   ; ICN 16
                DEFW -358, -1638   ; ICN 17
                DEFW -435, -1766   ; ICN 18
                DEFW -512, -1638   ; ICN 19
                DEFW -845, -1843   ; ICN 24
                DEFW -845, -1766   ; ICN 25
                DEFW -691, -1843   ; ICN 26
                DEFW -512, -1664   ; ICN 27
                DEFW -640, -1485   ; ICN 32
                DEFW -333, -1485   ; ICN 34
                DEFW -256, -1638   ; ICN 35
                DEFW -256, -1638   ; ICN 39
                DEFW -794, -1638   ; ICN 40
                DEFW -1050, -1613   ; ICN 41
                DEFW -410, -1638   ; ICN 45
                DEFW -486, -1510   ; ICN 46
                DEFW -410, -1357   ; ICN 47
                DEFW -384, -1050   ; ICN 48
                DEFW -512, -768   ; ICN 49
                DEFW -486, -640   ; ICN 50
BattleSeqPtrTab:
                DEFW BattleSeq0_STATIC, BattleSeq0_IDLE1, BattleSeq0_IDLE2, BattleSeq0_IDLE3, BattleSeq0_MOVE_MAIN, BattleSeq0_ATTACK2, BattleSeq0_ATTACK2_END, 0, 0, BattleSeq0_DEATH, BattleSeq0_WINCE_UP, BattleSeq0_WINCE_END
                DEFW BattleSeq1_STATIC, BattleSeq1_IDLE1, BattleSeq1_IDLE2, BattleSeq1_IDLE3, BattleSeq1_MOVE_MAIN, BattleSeq1_ATTACK2, BattleSeq1_ATTACK2_END, BattleSeq1_SHOOT2, BattleSeq1_SHOOT2_END, BattleSeq1_DEATH, BattleSeq1_WINCE_UP, BattleSeq1_WINCE_END
BattleSeq0_STATIC: DEFB 1, 0
BattleSeq0_IDLE1: DEFB 1, 1
BattleSeq0_IDLE2: DEFB 1, 2
BattleSeq0_IDLE3: DEFB 1, 3
BattleSeq0_MOVE_MAIN: DEFB 8, 4, 5, 6, 7, 8, 9, 10, 11
BattleSeq0_ATTACK2: DEFB 7, 15, 16, 17, 18, 19, 20, 21
BattleSeq0_ATTACK2_END: DEFB 2, 22, 23
BattleSeq0_DEATH: DEFB 7, 12, 13, 14, 24, 25, 26, 27
BattleSeq0_WINCE_UP: DEFB 3, 12, 13, 14
BattleSeq0_WINCE_END: DEFB 1, 13
BattleSeq1_STATIC: DEFB 1, 0
BattleSeq1_IDLE1: DEFB 4, 1, 2, 3, 2
BattleSeq1_IDLE2: DEFB 2, 1, 2
BattleSeq1_IDLE3: DEFB 3, 2, 3, 2
BattleSeq1_MOVE_MAIN: DEFB 8, 4, 5, 6, 7, 8, 9, 10, 11
BattleSeq1_ATTACK2: DEFB 6, 23, 24, 25, 26, 27, 28
BattleSeq1_ATTACK2_END: DEFB 5, 27, 26, 25, 24, 23
BattleSeq1_SHOOT2: DEFB 7, 15, 16, 17, 18, 19, 20, 21
BattleSeq1_SHOOT2_END: DEFB 1, 22
BattleSeq1_DEATH: DEFB 6, 29, 30, 31, 32, 33, 34
BattleSeq1_WINCE_UP: DEFB 3, 12, 13, 14
BattleSeq1_WINCE_END: DEFB 2, 13, 12
; --- РАБОЧИЕ тик-таблицы: 21 байт ПОДРЯД (layout = набор BattleSpeedSets);
;     Battle_ApplySpeed копирует сюда набор выбранной скорости (LDIR 21) ---
BattleAnimTicks:     DEFB 6          ; BATTLE_FRAME_DELAY (120мс @ speed4)
BattleMoveTickTab:   DEFB 3, 3   ; тиков/кадр MOVE_MAIN (moveSpeed/8)
BattleShootTickTab:  DEFB 6, 6   ; тиков/кадр SHOOT (shootSpeed/len)
BattleDeathTicksTab: DEFB 42, 36 ; длительность смерти (len(DEATH)×тик)
BattleWinceTimTab:                      ; [type] → DEFB up_тиков, всего_тиков
                DEFB 18, 24
                DEFB 18, 30
BattleAtkTimTab:                        ; [type] → DEFB мили_пик, мили_всего, выстрел_пик, выстрел_всего
                DEFB 42, 54, 42, 54
                DEFB 36, 66, 42, 48
BattleMoveVel:       DEFB 48         ; vertex-ед/тик (клетка 44px ≈ 23 тика @ speed4)
BattleArrowSteps:    DEFB 32         ; тиков полёта стрелы (шаг = дельта/steps)
BATTLE_SPEED_SET_LEN EQU 21
BattleIdleWaitMinTab: DEFW 214, 280 ; мин. пауза STATIC (тиков; от speed НЕ зависит — BIN idleDelay)
BATTLE_IDLE_RND_MASK EQU 127            ; пауза = min + (rand8 & mask) ≈ ×(75..125%)
BattleIdleThreshTab:                    ; [type] → DEFB n_вариантов, порог1, порог2 (rand8)
                DEFB 3, 85, 171
                DEFB 3, 51, 154
BattleStaticSlotTab: DEFB 0, 0     ; слот кадра стойки
BattleCorpseSlotTab: DEFB 27, 34   ; слот трупа (посл. DEATH)
BATTLE_ARROW_YOFS EQU -768              ; стрела на высоте груди (−30 лог.px от якоря-ног)
Battle_CountBar_Pre_DL:
                FT_COLOR_RGB 0, 0, 0
                FT_COLOR_A 150
                FT_LINE_WIDTH 16
                FT_BEGIN FT_RECTS
Battle_CountBar_Pre_DL_SIZE EQU $ - Battle_CountBar_Pre_DL
Battle_CountBar_Post_DL:
                FT_END
                FT_COLOR_A 255
                FT_COLOR_RGB 255, 255, 255
Battle_CountBar_Post_DL_SIZE EQU $ - Battle_CountBar_Post_DL
Battle_Count_Begin_DL:
                FT_BITMAP_TRANSFORM_A 256
                FT_BITMAP_TRANSFORM_E 256
                FT_PALETTE_SOURCE BATTLE_UNIT_PAL_RAMG
                FT_BEGIN FT_BITMAPS
Battle_Count_Begin_DL_SIZE EQU $ - Battle_Count_Begin_DL
BattleCountDigitTab:                   ; нативные цифры '0'-'9' В battle-PAK [lo,mid,hi,w,h]
                DEFB #00, #04, #00, 5, 8
                DEFB #28, #04, #00, 3, 8
                DEFB #40, #04, #00, 5, 8
                DEFB #68, #04, #00, 5, 8
                DEFB #90, #04, #00, 5, 8
                DEFB #B8, #04, #00, 5, 8
                DEFB #E0, #04, #00, 5, 8
                DEFB #08, #05, #00, 5, 8
                DEFB #30, #05, #00, 5, 8
                DEFB #58, #05, #00, 5, 8
Battle_Count_End_DL:
                FT_END
Battle_Count_End_DL_SIZE EQU $ - Battle_Count_End_DL
BattleCasualtyIconTab:                 ; иконы MONS32 type 0/1 [lo,mid,hi,w,h] (палитра юнитов)
                DEFB #B0, #C6, #04, 17, 29
                DEFB #A0, #C8, #04, 22, 31
BattleNoneSprite:                      ; «None» ×1.6 бел. [lo,mid,hi,w,h] (статус-палитра)
                DEFB #4C, #CB, #04, 48, 14
BATTLE_CAS_ATK_Y     EQU 8140
BATTLE_CAS_DEF_Y     EQU 9676
BattleArrowSrcTab:                     ; стрела ARCH_MSL[4] ×1.6 [lo,mid,hi,w,h]; [0]=вправо [1]=влево
                DEFB #EC, #CD, #04, 51, 8
                DEFB #84, #CF, #04, 51, 8
BATTLE_CNTBAR_DX  EQU 333               ; 13 лог.px ×25.6 (полуширина бара)
BATTLE_CNTBAR_DY0 EQU -179              ; верх бара = якорьY − 7 лог.px
BATTLE_CNTBAR_DY1 EQU 154               ; низ бара = якорьY + 6 лог.px
BATTLE_CNTPEN_DY  EQU -93               ; перо числа = якорьY − 3.6 лог.px (центр бара)
BattleAdjTab:                          ; 99 ячеек × 6 соседей (#FF=нет)
                DEFB 255, 255, 255, 1, 11, 12
                DEFB 255, 255, 0, 2, 12, 13
                DEFB 255, 255, 1, 3, 13, 14
                DEFB 255, 255, 2, 4, 14, 15
                DEFB 255, 255, 3, 5, 15, 16
                DEFB 255, 255, 4, 6, 16, 17
                DEFB 255, 255, 5, 7, 17, 18
                DEFB 255, 255, 6, 8, 18, 19
                DEFB 255, 255, 7, 9, 19, 20
                DEFB 255, 255, 8, 10, 20, 21
                DEFB 255, 255, 9, 255, 21, 255
                DEFB 255, 0, 255, 12, 255, 22
                DEFB 0, 1, 11, 13, 22, 23
                DEFB 1, 2, 12, 14, 23, 24
                DEFB 2, 3, 13, 15, 24, 25
                DEFB 3, 4, 14, 16, 25, 26
                DEFB 4, 5, 15, 17, 26, 27
                DEFB 5, 6, 16, 18, 27, 28
                DEFB 6, 7, 17, 19, 28, 29
                DEFB 7, 8, 18, 20, 29, 30
                DEFB 8, 9, 19, 21, 30, 31
                DEFB 9, 10, 20, 255, 31, 32
                DEFB 11, 12, 255, 23, 33, 34
                DEFB 12, 13, 22, 24, 34, 35
                DEFB 13, 14, 23, 25, 35, 36
                DEFB 14, 15, 24, 26, 36, 37
                DEFB 15, 16, 25, 27, 37, 38
                DEFB 16, 17, 26, 28, 38, 39
                DEFB 17, 18, 27, 29, 39, 40
                DEFB 18, 19, 28, 30, 40, 41
                DEFB 19, 20, 29, 31, 41, 42
                DEFB 20, 21, 30, 32, 42, 43
                DEFB 21, 255, 31, 255, 43, 255
                DEFB 255, 22, 255, 34, 255, 44
                DEFB 22, 23, 33, 35, 44, 45
                DEFB 23, 24, 34, 36, 45, 46
                DEFB 24, 25, 35, 37, 46, 47
                DEFB 25, 26, 36, 38, 47, 48
                DEFB 26, 27, 37, 39, 48, 49
                DEFB 27, 28, 38, 40, 49, 50
                DEFB 28, 29, 39, 41, 50, 51
                DEFB 29, 30, 40, 42, 51, 52
                DEFB 30, 31, 41, 43, 52, 53
                DEFB 31, 32, 42, 255, 53, 54
                DEFB 33, 34, 255, 45, 55, 56
                DEFB 34, 35, 44, 46, 56, 57
                DEFB 35, 36, 45, 47, 57, 58
                DEFB 36, 37, 46, 48, 58, 59
                DEFB 37, 38, 47, 49, 59, 60
                DEFB 38, 39, 48, 50, 60, 61
                DEFB 39, 40, 49, 51, 61, 62
                DEFB 40, 41, 50, 52, 62, 63
                DEFB 41, 42, 51, 53, 63, 64
                DEFB 42, 43, 52, 54, 64, 65
                DEFB 43, 255, 53, 255, 65, 255
                DEFB 255, 44, 255, 56, 255, 66
                DEFB 44, 45, 55, 57, 66, 67
                DEFB 45, 46, 56, 58, 67, 68
                DEFB 46, 47, 57, 59, 68, 69
                DEFB 47, 48, 58, 60, 69, 70
                DEFB 48, 49, 59, 61, 70, 71
                DEFB 49, 50, 60, 62, 71, 72
                DEFB 50, 51, 61, 63, 72, 73
                DEFB 51, 52, 62, 64, 73, 74
                DEFB 52, 53, 63, 65, 74, 75
                DEFB 53, 54, 64, 255, 75, 76
                DEFB 55, 56, 255, 67, 77, 78
                DEFB 56, 57, 66, 68, 78, 79
                DEFB 57, 58, 67, 69, 79, 80
                DEFB 58, 59, 68, 70, 80, 81
                DEFB 59, 60, 69, 71, 81, 82
                DEFB 60, 61, 70, 72, 82, 83
                DEFB 61, 62, 71, 73, 83, 84
                DEFB 62, 63, 72, 74, 84, 85
                DEFB 63, 64, 73, 75, 85, 86
                DEFB 64, 65, 74, 76, 86, 87
                DEFB 65, 255, 75, 255, 87, 255
                DEFB 255, 66, 255, 78, 255, 88
                DEFB 66, 67, 77, 79, 88, 89
                DEFB 67, 68, 78, 80, 89, 90
                DEFB 68, 69, 79, 81, 90, 91
                DEFB 69, 70, 80, 82, 91, 92
                DEFB 70, 71, 81, 83, 92, 93
                DEFB 71, 72, 82, 84, 93, 94
                DEFB 72, 73, 83, 85, 94, 95
                DEFB 73, 74, 84, 86, 95, 96
                DEFB 74, 75, 85, 87, 96, 97
                DEFB 75, 76, 86, 255, 97, 98
                DEFB 77, 78, 255, 89, 255, 255
                DEFB 78, 79, 88, 90, 255, 255
                DEFB 79, 80, 89, 91, 255, 255
                DEFB 80, 81, 90, 92, 255, 255
                DEFB 81, 82, 91, 93, 255, 255
                DEFB 82, 83, 92, 94, 255, 255
                DEFB 83, 84, 93, 95, 255, 255
                DEFB 84, 85, 94, 96, 255, 255
                DEFB 85, 86, 95, 97, 255, 255
                DEFB 86, 87, 96, 98, 255, 255
                DEFB 87, 255, 97, 255, 255, 255

BATTLE_UNIT_COUNT    EQU 4
BATTLE_UNIT_STATE_SIZE EQU 5            ; {тип, cell, side, count_lo, count_hi}
BattleUnitStateInit:                   ; read-only старт; Battle_Enter → BattleUnitState
                DEFB 0, 22, 0
                DEFW 40
                DEFB 1, 33, 0
                DEFW 4
                DEFB 0, 32, 1
                DEFW 20
                DEFB 1, 43, 1
                DEFW 2

BATTLE_RAMG_BASE     EQU #000000
BATTLE_PAYLOAD_BYTES EQU 920050
BATTLE_PAYLOAD_SECTORS EQU 1797
BATTLE_BODY_SECTOR   EQU 1
BattlePakName:       DEFB "HMM2BATL.PAK", 0

; ПКМ-попап инфо отряда (Dialog::ArmyInfo): 2 композита по типу в PAK; RAM_G-адрес =
; ОБЛАСТЬ ФИНАЛЬНОГО ОКНА (не живут одновременно; при конце боя финал РЕстримится).
ARMYINFO_W           EQU 551
ARMYINFO_H           EQU 283
ARMYINFO_BYTES       EQU 155933
ARMYINFO_SECTORS     EQU 305
ArmyInfoSecTab:      DEFW 1798, 2103   ; сектор попапа по типу (в PAK)
WINDLG_SEC           EQU 280      ; сектор финала внутри payload (рестрим)
WINDLG_SECTORS       EQU 327
ARMYINFO_X           EQU 44      ; экранное лево окна (лог.640×480)
ARMYINFO_Y           EQU 98
; значения статов: value @ x+406; Hit Points Left/Shots Left по типу (#FF=нет строки):
ArmyInfoHplYTab:     DEFB 103, 119   ; лок.Y строки Hit Points Left
ArmyInfoShotYTab:    DEFB 255, 71 ; лок.Y Shots Left (255=нет)
ARMYINFO_VAL_X       EQU 406    ; лок.X значений статов
; бокс счётчика (dialog_armyinfo.cpp:64): (80,223) 125×23, число по центру, normalWhite
ARMYINFO_CNT_X       EQU 80
ARMYINFO_CNT_Y       EQU 223
ARMYINFO_CNT_W       EQU 125
ARMYINFO_CNT_H       EQU 23
; точка ног монстра (x+520/4+16, y+175); спрайт из атласа юнитов, reflect по стороне
ARMYINFO_MON_X       EQU 146
ARMYINFO_MON_Y       EQU 175
; цифры '0'-'9' динамики: антиалиас-маски FONT ×1.6 (рисовать со status_pal, transform 256):
ArmyInfoDigitTab:                     ; 5 байт: addr24, w, h
                DEFB #B8, #BB, #04, 14, 22
                DEFB #EC, #BC, #04, 8, 22
                DEFB #9C, #BD, #04, 13, 22
                DEFB #BC, #BE, #04, 13, 22
                DEFB #DC, #BF, #04, 14, 22
                DEFB #10, #C1, #04, 13, 22
                DEFB #30, #C2, #04, 13, 22
                DEFB #50, #C3, #04, 13, 22
                DEFB #70, #C4, #04, 13, 22
                DEFB #90, #C5, #04, 13, 22
Battle_ArmyInfo_DL:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_PALETTE_SOURCE BATTLE_UNIT_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE BATTLE_WIN_DLG_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 551, 283
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 881, 452
                FT_BITMAP_SIZE_H 881, 452
                FT_VERTEX2F 1126, 2508
Battle_ArmyInfo_DL_SIZE EQU $ - Battle_ArmyInfo_DL
Battle_ArmyInfo_Post_DL:              ; после окна: сброс SIZE_H (ловушка &511)
                FT_BITMAP_SIZE_H 0, 0
Battle_ArmyInfo_Post_DL_SIZE EQU $ - Battle_ArmyInfo_Post_DL
ArmyInfoMonAnchor:                    ; [type] → (ax,ay) DEFW — якорь ног монстра
                DEFW 4864, 6989
                DEFW 4864, 6989
Battle_AIExitBtn0_DL:               ; отжата
                FT_BITMAP_SOURCE #021A14
                FT_BITMAP_LAYOUT FT_PALETTED4444, 94, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 150, 40
                FT_VERTEX2F 11801, 8166
Battle_AIExitBtn0_DL_SIZE EQU $ - Battle_AIExitBtn0_DL
Battle_AIExitBtn1_DL:               ; нажата
                FT_BITMAP_SOURCE #022344
                FT_BITMAP_LAYOUT FT_PALETTED4444, 94, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 150, 40
                FT_VERTEX2F 11801, 8166
Battle_AIExitBtn1_DL_SIZE EQU $ - Battle_AIExitBtn1_DL
AIEXIT_X0            EQU 461     ; hit-зона кнопки EXIT (лог. 640×480)
AIEXIT_X1            EQU 555
AIEXIT_Y0            EQU 319
AIEXIT_Y1            EQU 344
ARMYINFO_CNT_CX16    EQU 4761   ; центр бокса счётчика ×16 (минус tw×8)
ARMYINFO_CNT_Y16     EQU 8374   ; верх цифр счётчика ×16
ARMYINFO_VALX16      EQU 11520  ; лево значений статов ×16
ArmyInfoHplY16Tab:   DEFW 5145, 5555   ; Y строки Hit Points Left ×16 (по типу)
ArmyInfoShotY16Tab:  DEFW 0, 4326   ; Y строки Shots Left ×16 (0=нет строки)

                endif