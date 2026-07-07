; Сгенерировано Source/Tools/battle_pack.py — экран боя (Grass, потоковый HMM2BATL.PAK).
                ifndef _HMM2_GENERATED_BATTLE_
                define _HMM2_GENERATED_BATTLE_

BATTLE_PAL_RAMG      EQU #000000
BATTLE_TOP_RAMG      EQU #0571D4
BATTLE_BOT_RAMG      EQU #07C9D4
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

BATTLE_YELLOW_PAL_RAMG EQU #05308C
Battle_WinTitle_Begin_DL:              ; пролог заголовка победы (жёлтая палитра, нативно)
                FT_BITMAP_TRANSFORM_A 256
                FT_BITMAP_TRANSFORM_E 256
                FT_PALETTE_SOURCE BATTLE_YELLOW_PAL_RAMG
                FT_BEGIN FT_BITMAPS
Battle_WinTitle_Begin_DL_SIZE EQU $ - Battle_WinTitle_Begin_DL
WIN_TEXT_REC EQU 11
BATTLE_WIN_TEXT_COUNT EQU 13

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
                DEFW BattleFrameSrc0_0, BattleFrameSrc0_1, BattleFrameSrc1_0, BattleFrameSrc1_1, BattleFrameSrc2_0, BattleFrameSrc2_1, BattleFrameSrc3_0, BattleFrameSrc3_1
BattleFrameSrc0_0:
                FT_BITMAP_SOURCE #0A21D4   ; ICN 1
                FT_BITMAP_SOURCE #0A33D4   ; ICN 2
                FT_BITMAP_SOURCE #0A45D4   ; ICN 5
                FT_BITMAP_SOURCE #0A5744   ; ICN 6
                FT_BITMAP_SOURCE #0A6A2C   ; ICN 7
                FT_BITMAP_SOURCE #0A7E34   ; ICN 8
                FT_BITMAP_SOURCE #0A9144   ; ICN 9
                FT_BITMAP_SOURCE #0AA17C   ; ICN 10
                FT_BITMAP_SOURCE #0AB2A4   ; ICN 11
                FT_BITMAP_SOURCE #0AC6AC   ; ICN 12
                FT_BITMAP_SOURCE #0AD89C   ; ICN 13
                FT_BITMAP_SOURCE #0AEE8C   ; ICN 14
                FT_BITMAP_SOURCE #0B007C   ; ICN 15
                FT_BITMAP_SOURCE #0B0EBC   ; ICN 16
                FT_BITMAP_SOURCE #0B208C   ; ICN 17
                FT_BITMAP_SOURCE #0B304C   ; ICN 18
                FT_BITMAP_SOURCE #0B44D4   ; ICN 23
                FT_BITMAP_SOURCE #0B595C   ; ICN 24
                FT_BITMAP_SOURCE #0B6DE4   ; ICN 25
                FT_BITMAP_SOURCE #0B85CC   ; ICN 26
                FT_BITMAP_SOURCE #0BA3D4   ; ICN 27
                FT_BITMAP_SOURCE #0BBE7C   ; ICN 28
                FT_BITMAP_SOURCE #0BD82C   ; ICN 34
                FT_BITMAP_SOURCE #0BE27C   ; ICN 35
                FT_BITMAP_SOURCE #0BEAFC   ; ICN 36
                FT_BITMAP_SOURCE #0BF1F4   ; ICN 37
BattleFrameSrc0_1:
                FT_BITMAP_SOURCE #0A2AD4   ; ICN 1
                FT_BITMAP_SOURCE #0A3CD4   ; ICN 2
                FT_BITMAP_SOURCE #0A4E8C   ; ICN 5
                FT_BITMAP_SOURCE #0A60B8   ; ICN 6
                FT_BITMAP_SOURCE #0A7430   ; ICN 7
                FT_BITMAP_SOURCE #0A87BC   ; ICN 8
                FT_BITMAP_SOURCE #0A9960   ; ICN 9
                FT_BITMAP_SOURCE #0AAA10   ; ICN 10
                FT_BITMAP_SOURCE #0ABCA8   ; ICN 11
                FT_BITMAP_SOURCE #0ACFA4   ; ICN 12
                FT_BITMAP_SOURCE #0AE394   ; ICN 13
                FT_BITMAP_SOURCE #0AF784   ; ICN 14
                FT_BITMAP_SOURCE #0B079C   ; ICN 15
                FT_BITMAP_SOURCE #0B17A4   ; ICN 16
                FT_BITMAP_SOURCE #0B286C   ; ICN 17
                FT_BITMAP_SOURCE #0B3A90   ; ICN 18
                FT_BITMAP_SOURCE #0B4F18   ; ICN 23
                FT_BITMAP_SOURCE #0B63A0   ; ICN 24
                FT_BITMAP_SOURCE #0B79D8   ; ICN 25
                FT_BITMAP_SOURCE #0B94D0   ; ICN 26
                FT_BITMAP_SOURCE #0BB128   ; ICN 27
                FT_BITMAP_SOURCE #0BCB54   ; ICN 28
                FT_BITMAP_SOURCE #0BDD54   ; ICN 34
                FT_BITMAP_SOURCE #0BE6BC   ; ICN 35
                FT_BITMAP_SOURCE #0BEE78   ; ICN 36
                FT_BITMAP_SOURCE #0BF560   ; ICN 37
BattleFrameSrc1_0:
                FT_BITMAP_SOURCE #0BF8CC   ; ICN 1
                FT_BITMAP_SOURCE #0C0A54   ; ICN 2
                FT_BITMAP_SOURCE #0C1B5C   ; ICN 3
                FT_BITMAP_SOURCE #0C2C64   ; ICN 4
                FT_BITMAP_SOURCE #0C3CE4   ; ICN 5
                FT_BITMAP_SOURCE #0C4D64   ; ICN 6
                FT_BITMAP_SOURCE #0C5DA4   ; ICN 7
                FT_BITMAP_SOURCE #0C71D4   ; ICN 8
                FT_BITMAP_SOURCE #0C8194   ; ICN 9
                FT_BITMAP_SOURCE #0C9154   ; ICN 10
                FT_BITMAP_SOURCE #0CA30C   ; ICN 11
                FT_BITMAP_SOURCE #0CB4C4   ; ICN 12
                FT_BITMAP_SOURCE #0CC644   ; ICN 13
                FT_BITMAP_SOURCE #0CD4CC   ; ICN 14
                FT_BITMAP_SOURCE #0CE30C   ; ICN 15
                FT_BITMAP_SOURCE #0CEFF4   ; ICN 16
                FT_BITMAP_SOURCE #0CFF74   ; ICN 17
                FT_BITMAP_SOURCE #0D0E74   ; ICN 18
                FT_BITMAP_SOURCE #0D20CC   ; ICN 19
                FT_BITMAP_SOURCE #0D354C   ; ICN 24
                FT_BITMAP_SOURCE #0D50DC   ; ICN 25
                FT_BITMAP_SOURCE #0D6924   ; ICN 26
                FT_BITMAP_SOURCE #0D7F14   ; ICN 27
                FT_BITMAP_SOURCE #0D91E4   ; ICN 32
                FT_BITMAP_SOURCE #0DA394   ; ICN 34
                FT_BITMAP_SOURCE #0DAFD4   ; ICN 35
                FT_BITMAP_SOURCE #0DBDD4   ; ICN 39
                FT_BITMAP_SOURCE #0DCBD4   ; ICN 40
                FT_BITMAP_SOURCE #0DE3D4   ; ICN 41
                FT_BITMAP_SOURCE #0DFFE4   ; ICN 45
                FT_BITMAP_SOURCE #0E10A4   ; ICN 46
                FT_BITMAP_SOURCE #0E20F4   ; ICN 47
                FT_BITMAP_SOURCE #0E2D54   ; ICN 48
                FT_BITMAP_SOURCE #0E363C   ; ICN 49
                FT_BITMAP_SOURCE #0E3EAC   ; ICN 50
BattleFrameSrc1_1:
                FT_BITMAP_SOURCE #0C0190   ; ICN 1
                FT_BITMAP_SOURCE #0C12D8   ; ICN 2
                FT_BITMAP_SOURCE #0C23E0   ; ICN 3
                FT_BITMAP_SOURCE #0C34A4   ; ICN 4
                FT_BITMAP_SOURCE #0C4524   ; ICN 5
                FT_BITMAP_SOURCE #0C5584   ; ICN 6
                FT_BITMAP_SOURCE #0C67BC   ; ICN 7
                FT_BITMAP_SOURCE #0C79B4   ; ICN 8
                FT_BITMAP_SOURCE #0C8974   ; ICN 9
                FT_BITMAP_SOURCE #0C9A30   ; ICN 10
                FT_BITMAP_SOURCE #0CABE8   ; ICN 11
                FT_BITMAP_SOURCE #0CBD84   ; ICN 12
                FT_BITMAP_SOURCE #0CCD88   ; ICN 13
                FT_BITMAP_SOURCE #0CDBEC   ; ICN 14
                FT_BITMAP_SOURCE #0CE980   ; ICN 15
                FT_BITMAP_SOURCE #0CF7B4   ; ICN 16
                FT_BITMAP_SOURCE #0D06F4   ; ICN 17
                FT_BITMAP_SOURCE #0D17A0   ; ICN 18
                FT_BITMAP_SOURCE #0D2B0C   ; ICN 19
                FT_BITMAP_SOURCE #0D4314   ; ICN 24
                FT_BITMAP_SOURCE #0D5D00   ; ICN 25
                FT_BITMAP_SOURCE #0D741C   ; ICN 26
                FT_BITMAP_SOURCE #0D887C   ; ICN 27
                FT_BITMAP_SOURCE #0D9ABC   ; ICN 32
                FT_BITMAP_SOURCE #0DA9B4   ; ICN 34
                FT_BITMAP_SOURCE #0DB6D4   ; ICN 35
                FT_BITMAP_SOURCE #0DC4D4   ; ICN 39
                FT_BITMAP_SOURCE #0DD7D4   ; ICN 40
                FT_BITMAP_SOURCE #0DF1DC   ; ICN 41
                FT_BITMAP_SOURCE #0E0844   ; ICN 45
                FT_BITMAP_SOURCE #0E18CC   ; ICN 46
                FT_BITMAP_SOURCE #0E2724   ; ICN 47
                FT_BITMAP_SOURCE #0E31C8   ; ICN 48
                FT_BITMAP_SOURCE #0E3A74   ; ICN 49
                FT_BITMAP_SOURCE #0E4208   ; ICN 50
BattleFrameSrc2_0:
                FT_BITMAP_SOURCE #0E4564   ; ICN 1
BattleFrameSrc2_1:
                FT_BITMAP_SOURCE #0E4DE8   ; ICN 1
BattleFrameSrc3_0:
                FT_BITMAP_SOURCE #0E566C   ; ICN 1
BattleFrameSrc3_1:
                FT_BITMAP_SOURCE #0E602C   ; ICN 1
BattleFrameLayTab:                      ; [тип] → LAYOUT+SIZE ×кадры (8Б; общие для зеркала)
                DEFW BattleFrameLay0, BattleFrameLay1, BattleFrameLay2, BattleFrameLay3
BattleFrameLay0:
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
BattleFrameLay2:
                FT_BITMAP_LAYOUT FT_PALETTED4444, 33, 66
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 105
BattleFrameLay3:
                FT_BITMAP_LAYOUT FT_PALETTED4444, 39, 64
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 62, 102
BattleFrameOfsTab:                      ; [вариант] → &GD-таблицы (ofsX,ofsY)×кадры в #91
                DEFW GDBattleFrameOfs0_0, GDBattleFrameOfs0_1, GDBattleFrameOfs1_0, GDBattleFrameOfs1_1, GDBattleFrameOfs2_0, GDBattleFrameOfs2_1, GDBattleFrameOfs3_0, GDBattleFrameOfs3_1
; --- РАБОЧИЕ тик-таблицы: 21 байт ПОДРЯД (layout = набор BattleSpeedSets);
;     Battle_ApplySpeed копирует сюда набор выбранной скорости (LDIR 21) ---
BattleAnimTicks:     DEFB 6          ; BATTLE_FRAME_DELAY (120мс @ speed4)
BattleMoveTickTab:   DEFB 3, 3, 17, 34   ; тиков/кадр MOVE_MAIN (moveSpeed/8)
BattleShootTickTab:  DEFB 6, 6, 6, 6   ; тиков/кадр SHOOT (shootSpeed/len)
BattleDeathTicksTab: DEFB 42, 36, 6, 6 ; длительность смерти (len(DEATH)×тик)
BattleWinceTimTab:                      ; [type] → DEFB up_тиков, всего_тиков
                DEFB 18, 24
                DEFB 18, 30
                DEFB 0, 0
                DEFB 0, 0
BattleAtkTimTab:                        ; [type] → DEFB мили_пик, мили_всего, выстрел_пик, выстрел_всего
                DEFB 42, 54, 42, 54
                DEFB 36, 66, 42, 48
                DEFB 6, 6, 6, 6
                DEFB 6, 6, 6, 6
BattleMoveVel:       DEFB 48         ; vertex-ед/тик (клетка 44px ≈ 23 тика @ speed4)
BattleArrowSteps:    DEFB 32         ; тиков полёта стрелы (шаг = дельта/steps)
BATTLE_SPEED_SET_LEN EQU 39
BattleIdleWaitMinTab: DEFW 214, 280, 330, 330 ; мин. пауза STATIC (тиков; от speed НЕ зависит — BIN idleDelay)
BATTLE_IDLE_RND_MASK EQU 127            ; пауза = min + (rand8 & mask) ≈ ×(75..125%)
BattleIdleThreshTab:                    ; [type] → DEFB n_вариантов, порог1, порог2 (rand8)
                DEFB 3, 85, 171
                DEFB 3, 51, 154
                DEFB 3, 85, 171
                DEFB 3, 77, 192
BattleStaticSlotTab: DEFB 0, 0, 0, 0     ; слот кадра стойки
BattleCorpseSlotTab: DEFB 25, 34, 0, 0   ; слот трупа (посл. DEATH)
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
                DEFB #60, #22, #05, 17, 29
                DEFB #50, #24, #05, 22, 31
                DEFB #FC, #26, #05, 14, 27
                DEFB #78, #28, #05, 20, 29
BattleNoneSprite:                      ; «None» ×1.6 бел. [lo,mid,hi,w,h] (статус-палитра)
                DEFB #BC, #2A, #05, 48, 14
BATTLE_CAS_ATK_Y     EQU 8140
BATTLE_CAS_DEF_Y     EQU 9676
BattleArrowSrcTab:                     ; стрела ARCH_MSL[4] ×1.6 [lo,mid,hi,w,h]; [0]=вправо [1]=влево
                DEFB #5C, #2D, #05, 51, 8
                DEFB #F4, #2E, #05, 51, 8
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
                DEFB 2, 32, 1
                DEFW 15
                DEFB 3, 43, 1
                DEFW 8

BATTLE_RAMG_BASE     EQU #000000
BATTLE_PAYLOAD_BYTES EQU 944620
BATTLE_PAYLOAD_SECTORS EQU 1845
BATTLE_BODY_SECTOR   EQU 1
BattlePakName:       DEFB "HMM2BATL.PAK", 0

; ПКМ-попап инфо отряда (Dialog::ArmyInfo): 2 композита по типу в PAK; RAM_G-адрес =
; ОБЛАСТЬ ФИНАЛЬНОГО ОКНА (не живут одновременно; при конце боя финал РЕстримится).
ARMYINFO_W           EQU 551
ARMYINFO_H           EQU 283
ARMYINFO_BYTES       EQU 155933
ARMYINFO_SECTORS     EQU 305
ArmyInfoSecTab:      DEFW 1846, 2151, 2456, 2761   ; сектор попапа по типу (в PAK)
WINDLG_SEC           EQU 280      ; сектор финала внутри payload (рестрим)
WINDLG_SECTORS       EQU 327
ARMYINFO_X           EQU 44      ; экранное лево окна (лог.640×480)
ARMYINFO_Y           EQU 98
; значения статов: value @ x+406; Hit Points Left/Shots Left по типу (#FF=нет строки):
ArmyInfoHplYTab:     DEFB 103, 119, 103, 103   ; лок.Y строки Hit Points Left
ArmyInfoShotYTab:    DEFB 255, 71, 255, 255   ; лок.Y Shots Left (255=нет)
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
ArmyInfoHplY16Tab:   DEFW 5145, 5555, 5145, 5145   ; Y строки Hit Points Left ×16 (по типу)
ArmyInfoShotY16Tab:  DEFW 0, 4326, 0, 0   ; Y строки Shots Left ×16 (0=нет строки)

; Окно настроек боя (стрим в область финала, как ArmyInfo)
SETTINGS_SEC         EQU 3066      ; сектор композита окна в PAK
SETTINGS_SECTORS     EQU 191
SETTINGS_BYTES       EQU 97584
SETTINGS_X           EQU 159      ; экранное лево окна (лог.640×480)
SETTINGS_Y           EQU 88
Battle_Settings_DL:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_PALETTE_SOURCE BATTLE_UNIT_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE BATTLE_WIN_DLG_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 321, 304
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 513, 486
                FT_BITMAP_SIZE_H 513, 486
                FT_VERTEX2F 4070, 2252
Battle_Settings_DL_SIZE EQU $ - Battle_Settings_DL
Battle_Settings_Post_DL:              ; сброс SIZE_H (ловушка &511)
                FT_BITMAP_SIZE_H 0, 0
Battle_Settings_Post_DL_SIZE EQU $ - Battle_Settings_Post_DL
Battle_SetSpdIcon1_DL:              ; CSPANEL[1] (speed 5..7)
                FT_BITMAP_SOURCE #04C6B0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 65, 65
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 104, 104
                FT_VERTEX2F 4992, 3456
Battle_SetSpdIcon1_DL_SIZE EQU $ - Battle_SetSpdIcon1_DL
Battle_SetSpdIcon2_DL:              ; CSPANEL[2] (speed ≥8)
                FT_BITMAP_SOURCE #04D734
                FT_BITMAP_LAYOUT FT_PALETTED4444, 65, 65
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 104, 104
                FT_VERTEX2F 4992, 3456
Battle_SetSpdIcon2_DL_SIZE EQU $ - Battle_SetSpdIcon2_DL
Battle_SetOkay1_DL:                   ; OKAY нажата (подложка вбейкана)
                FT_BITMAP_SOURCE #04E7B8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 95, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 152, 40
                FT_VERTEX2F 6963, 8857
Battle_SetOkay1_DL_SIZE EQU $ - Battle_SetOkay1_DL
BattleSetValTab:                      ; [speed−1] → адрес24, w, h (маска «Speed: N» ×1.6)
                DEFB #00, #F1, #04, 67, 18
                DEFB #B8, #F5, #04, 70, 18
                DEFB #A4, #FA, #04, 70, 18
                DEFB #90, #FF, #04, 70, 18
                DEFB #7C, #04, #05, 70, 18
                DEFB #68, #09, #05, 70, 18
                DEFB #54, #0E, #05, 70, 18
                DEFB #40, #13, #05, 70, 18
                DEFB #2C, #18, #05, 70, 18
                DEFB #18, #1D, #05, 75, 18
SETVAL_CX16          EQU 5811  ; центр строки значения ×16
SETVAL_Y16           EQU 5273
BTLSET_BTN_X0        EQU 0        ; кнопка Settings панели (TEXTBAR[6] @ 0,461)
BTLSET_BTN_X1        EQU 49
BTLSET_BTN_Y0        EQU 461
BTLSET_BTN_Y1        EQU 480
BTLSET_SPEED_X0      EQU 195    ; зона опции Speed (65×65)
BTLSET_SPEED_X1      EQU 260
BTLSET_SPEED_Y0      EQU 135
BTLSET_SPEED_Y1      EQU 200
BTLSET_OK_X0         EQU 272    ; зона кнопки OKAY
BTLSET_OK_X1         EQU 367
BTLSET_OK_Y0         EQU 346
BTLSET_OK_Y1         EQU 371

; ПКМ-справки: [idx] → сектор/размер в PAK; DL-фрагмент на окно (центр экрана)
BattleHelpSecTab:    DEFW 3257, 3383, 3491, 3617, 3725, 3833, 3988, 4096, 4204
BattleHelpSecN:      DEFB 126, 108, 126, 108, 108, 155, 108, 108, 108
Battle_HelpPre_DL:                    ; общий пролог всех окон справок
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_PALETTE_SOURCE BATTLE_UNIT_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE BATTLE_WIN_DLG_RAMG
Battle_HelpPre_DL_SIZE EQU $ - Battle_HelpPre_DL
Battle_Help0_DL:                     ; LAYOUT/SIZE/VERTEX окна 0 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 210
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 336
                FT_BITMAP_SIZE_H 489, 336
                FT_VERTEX2F 4275, 3456
Battle_Help1_DL:                     ; LAYOUT/SIZE/VERTEX окна 1 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 288
                FT_BITMAP_SIZE_H 489, 288
                FT_VERTEX2F 4275, 3840
Battle_Help2_DL:                     ; LAYOUT/SIZE/VERTEX окна 2 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 210
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 336
                FT_BITMAP_SIZE_H 489, 336
                FT_VERTEX2F 4275, 3456
Battle_Help3_DL:                     ; LAYOUT/SIZE/VERTEX окна 3 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 288
                FT_BITMAP_SIZE_H 489, 288
                FT_VERTEX2F 4275, 3840
Battle_Help4_DL:                     ; LAYOUT/SIZE/VERTEX окна 4 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 288
                FT_BITMAP_SIZE_H 489, 288
                FT_VERTEX2F 4275, 3840
Battle_Help5_DL:                     ; LAYOUT/SIZE/VERTEX окна 5 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 258
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 412
                FT_BITMAP_SIZE_H 489, 412
                FT_VERTEX2F 4275, 2841
Battle_Help6_DL:                     ; LAYOUT/SIZE/VERTEX окна 6 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 288
                FT_BITMAP_SIZE_H 489, 288
                FT_VERTEX2F 4275, 3840
Battle_Help7_DL:                     ; LAYOUT/SIZE/VERTEX окна 7 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 288
                FT_BITMAP_SIZE_H 489, 288
                FT_VERTEX2F 4275, 3840
Battle_Help8_DL:                     ; LAYOUT/SIZE/VERTEX окна 8 (пролог общий)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 306, 180
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 489, 288
                FT_BITMAP_SIZE_H 489, 288
                FT_VERTEX2F 4275, 3840
BATTLE_HELP_DL_SIZE EQU $ - Battle_Help8_DL   ; per-окно размер одинаков (4 команды)
BattleHelpDLTab:                      ; [idx] → DEFW ptr (размер общий)
                DEFW Battle_Help0_DL
                DEFW Battle_Help1_DL
                DEFW Battle_Help2_DL
                DEFW Battle_Help3_DL
                DEFW Battle_Help4_DL
                DEFW Battle_Help5_DL
                DEFW Battle_Help6_DL
                DEFW Battle_Help7_DL
                DEFW Battle_Help8_DL
BattleSetHelpRects:                   ; 6 × DEFW X0,X1,Y0,Y1 (окна справок 3..8)
                DEFW 195, 260, 135, 200
                DEFW 287, 352, 135, 200
                DEFW 379, 444, 135, 200
                DEFW 228, 293, 245, 310
                DEFW 346, 411, 245, 310
                DEFW 272, 367, 346, 371

                endif