; Сгенерировано Source/Tools/battle_pack.py — экран боя (Grass, потоковый HMM2BATL.PAK).
                ifndef _HMM2_GENERATED_BATTLE_
                define _HMM2_GENERATED_BATTLE_

BATTLE_PAL_RAMG      EQU #000000
BATTLE_TOP_RAMG      EQU #03D9CC
BATTLE_BOT_RAMG      EQU #0631CC
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
                DEFW Battle_Status_Pre_0, Battle_Status_Pre_1, Battle_Status_Pre_2, Battle_Status_Pre_3, Battle_Status_Pre_4, Battle_Status_Pre_5, Battle_Status_Pre_6, Battle_Status_Pre_7
Battle_Status_Pre_0:
                FT_BITMAP_SOURCE #001290
                FT_BITMAP_LAYOUT FT_PALETTED4444, 119, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 119, 9
Battle_Status_Pre_1:
                FT_BITMAP_SOURCE #0016C0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 115, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 115, 9
Battle_Status_Pre_2:
                FT_BITMAP_SOURCE #001ACC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 97, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 97, 9
Battle_Status_Pre_3:
                FT_BITMAP_SOURCE #001E38
                FT_BITMAP_LAYOUT FT_PALETTED4444, 93, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 93, 9
Battle_Status_Pre_4:
                FT_BITMAP_SOURCE #002180
                FT_BITMAP_LAYOUT FT_PALETTED4444, 168, 10
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 168, 10
Battle_Status_Pre_5:
                FT_BITMAP_SOURCE #002810
                FT_BITMAP_LAYOUT FT_PALETTED4444, 164, 10
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 164, 10
Battle_Status_Pre_6:
                FT_BITMAP_SOURCE #002E78
                FT_BITMAP_LAYOUT FT_PALETTED4444, 116, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 9
Battle_Status_Pre_7:
                FT_BITMAP_SOURCE #00328C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 112, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 112, 9
BATTLE_STATUS_PRE_SIZE EQU Battle_Status_Pre_1 - Battle_Status_Pre_0
BattleStatusVertTab:                   ; центр физ. (512, y=717); текст НАТИВНЫЙ (без ×1.6)
                FT_VERTEX2F 7248, 11468
                FT_VERTEX2F 7280, 11468
                FT_VERTEX2F 7424, 11468
                FT_VERTEX2F 7456, 11468
                FT_VERTEX2F 6848, 11468
                FT_VERTEX2F 6880, 11468
                FT_VERTEX2F 7264, 11468
                FT_VERTEX2F 7296, 11468
BATTLE_STATUS_COUNT EQU 8

BattleTurnPreTab:
                DEFW Battle_Turn_Pre_0, Battle_Turn_Pre_1, Battle_Turn_Pre_2, Battle_Turn_Pre_3, Battle_Turn_Pre_4, Battle_Turn_Pre_5, Battle_Turn_Pre_6, Battle_Turn_Pre_7, Battle_Turn_Pre_8, Battle_Turn_Pre_9
Battle_Turn_Pre_0:
                FT_BITMAP_SOURCE #00367C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 38, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 38, 9
Battle_Turn_Pre_1:
                FT_BITMAP_SOURCE #0037D4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 40, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 9
Battle_Turn_Pre_2:
                FT_BITMAP_SOURCE #00393C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 40, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 9
Battle_Turn_Pre_3:
                FT_BITMAP_SOURCE #003AA4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 40, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 9
Battle_Turn_Pre_4:
                FT_BITMAP_SOURCE #003C0C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 40, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 9
Battle_Turn_Pre_5:
                FT_BITMAP_SOURCE #003D74
                FT_BITMAP_LAYOUT FT_PALETTED4444, 40, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 9
Battle_Turn_Pre_6:
                FT_BITMAP_SOURCE #003EDC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 40, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 9
Battle_Turn_Pre_7:
                FT_BITMAP_SOURCE #004044
                FT_BITMAP_LAYOUT FT_PALETTED4444, 40, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 9
Battle_Turn_Pre_8:
                FT_BITMAP_SOURCE #0041AC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 40, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 9
Battle_Turn_Pre_9:
                FT_BITMAP_SOURCE #004314
                FT_BITMAP_LAYOUT FT_PALETTED4444, 43, 9
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 43, 9
BATTLE_TURN_PRE_SIZE EQU Battle_Turn_Pre_1 - Battle_Turn_Pre_0
BattleTurnVertTab:                     ; центр физ. (512, y=717); текст НАТИВНЫЙ (без ×1.6)
                FT_VERTEX2F 7888, 11468
                FT_VERTEX2F 7872, 11468
                FT_VERTEX2F 7872, 11468
                FT_VERTEX2F 7872, 11468
                FT_VERTEX2F 7872, 11468
                FT_VERTEX2F 7872, 11468
                FT_VERTEX2F 7872, 11468
                FT_VERTEX2F 7872, 11468
                FT_VERTEX2F 7872, 11468
                FT_VERTEX2F 7856, 11468
BATTLE_TURN_MAX EQU 10

EVT_ENTRY_SIZE EQU 5
BattleEvtAtkTab:                       ; «<atk> do/does » idx=type×2+(count==1)
                DEFB #98, #44, #00, 166, 22
                DEFB #DC, #52, #00, 181, 22
                DEFB #6C, #62, #00, 160, 22
                DEFB #2C, #70, #00, 174, 22
BattleEvtDmgSfx:                       ; « damage.»
                DEFB #20, #7F, #00, 117, 27
BattleEvtSpace:                        ; « » (между damage. и числом гибели)
                DEFB #78, #8B, #00, 10, 2
BattleEvtPerishTab:                    ; « <def> perish(es).» idx=type×2+(killed==1)
                DEFB #8C, #8B, #00, 222, 27
                DEFB #F8, #A2, #00, 237, 27
                DEFB #F8, #BB, #00, 216, 27
                DEFB #C0, #D2, #00, 230, 27
BattleEvtDigitTab:                     ; «0».. «9» (тот же шрифт, что слова)
                DEFB #04, #EB, #00, 14, 22
                DEFB #38, #EC, #00, 8, 22
                DEFB #E8, #EC, #00, 13, 22
                DEFB #08, #EE, #00, 13, 22
                DEFB #28, #EF, #00, 14, 22
                DEFB #5C, #F0, #00, 13, 22
                DEFB #7C, #F1, #00, 13, 22
                DEFB #9C, #F2, #00, 13, 22
                DEFB #BC, #F3, #00, 13, 22
                DEFB #DC, #F4, #00, 13, 22
BattleEvtMoveHead:                     ; «Moved »
                DEFB #FC, #F5, #00, 42, 9
BattleEvtMoveNameTab:                  ; «Peasants: »/«Archers: » idx=type
                DEFB #78, #F7, #00, 59, 9
                DEFB #8C, #F9, #00, 55, 9
BattleEvtMoveFrom:                     ; «from [»
                DEFB #7C, #FB, #00, 38, 10
BattleEvtMoveMid:                      ; «] to [»
                DEFB #F8, #FC, #00, 27, 10
BattleEvtMoveEnd:                      ; «].»
                DEFB #08, #FE, #00, 6, 10
BattleEvtComma:                        ; «, » (между row и col)
                DEFB #44, #FE, #00, 7, 11
BattleEvtMoveDigitTab:                 ; нативные цифры «0».. «9» для координат движения
                DEFB #94, #FE, #00, 5, 9
                DEFB #C4, #FE, #00, 3, 9
                DEFB #E0, #FE, #00, 5, 9
                DEFB #10, #FF, #00, 5, 9
                DEFB #40, #FF, #00, 5, 9
                DEFB #70, #FF, #00, 5, 9
                DEFB #A0, #FF, #00, 5, 9
                DEFB #D0, #FF, #00, 5, 9
                DEFB #00, #00, #01, 5, 9
                DEFB #30, #00, #01, 5, 9

BATTLE_YELLOW_PAL_RAMG EQU #039884
Battle_WinTitle_Begin_DL:              ; пролог заголовка победы (жёлтая палитра, нативно)
                FT_BITMAP_TRANSFORM_A 256
                FT_BITMAP_TRANSFORM_E 256
                FT_PALETTE_SOURCE BATTLE_YELLOW_PAL_RAMG
                FT_BEGIN FT_BITMAPS
Battle_WinTitle_Begin_DL_SIZE EQU $ - Battle_WinTitle_Begin_DL
WIN_TEXT_REC EQU 11
BATTLE_WIN_TEXT_COUNT EQU 13
BattleWinTextTab:
                DEFB #84, #9A, #03, 34, 22, 1
                DEFW 6224, 4812
                DEFB 1      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #70, #9D, #03, 114, 27, 1
                DEFW 6768, 4812
                DEFB 1      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #78, #A9, #03, 99, 27, 1
                DEFW 8592, 4812
                DEFB 1      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #EC, #B3, #03, 54, 14, 0
                DEFW 5600, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #E0, #B6, #03, 64, 14, 0
                DEFW 6464, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #60, #BA, #03, 66, 14, 0
                DEFW 7488, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #FC, #BD, #03, 18, 14, 0
                DEFW 8544, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #F8, #BE, #03, 61, 14, 0
                DEFW 8832, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #50, #C2, #03, 61, 14, 0
                DEFW 9808, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #A8, #C5, #03, 102, 14, 0
                DEFW 6608, 7270
                DEFB 0      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #3C, #CB, #03, 96, 14, 0
                DEFW 8240, 7270
                DEFB 0      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #7C, #D0, #03, 85, 14, 0
                DEFW 7520, 7654
                DEFB 0      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #24, #D5, #03, 85, 14, 0
                DEFW 7520, 9190
                DEFB 0      ; видимость: 0=всегда, 1=победа, 2=поражение

BATTLE_WIN_DLG_RAMG EQU #010060
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
BATTLE_UNIT_FRAME_COUNT EQU 16
BattleUnitSrcTab:                       ; [вариант*N+кадр] → FT_BITMAP_SOURCE (4Б)
                FT_BITMAP_SOURCE #0889CC
                FT_BITMAP_SOURCE #08A010
                FT_BITMAP_SOURCE #08B654
                FT_BITMAP_SOURCE #08CC98
                FT_BITMAP_SOURCE #08E2DC
                FT_BITMAP_SOURCE #08F920
                FT_BITMAP_SOURCE #090F64
                FT_BITMAP_SOURCE #0925A8
                FT_BITMAP_SOURCE #093BEC
                FT_BITMAP_SOURCE #095230
                FT_BITMAP_SOURCE #096874
                FT_BITMAP_SOURCE #097EB8
                FT_BITMAP_SOURCE #0994FC
                FT_BITMAP_SOURCE #09AB40
                FT_BITMAP_SOURCE #09C184
                FT_BITMAP_SOURCE #09D7C8
                FT_BITMAP_SOURCE #09EE0C
                FT_BITMAP_SOURCE #0A0450
                FT_BITMAP_SOURCE #0A1A94
                FT_BITMAP_SOURCE #0A30D8
                FT_BITMAP_SOURCE #0A471C
                FT_BITMAP_SOURCE #0A5D60
                FT_BITMAP_SOURCE #0A73A4
                FT_BITMAP_SOURCE #0A89E8
                FT_BITMAP_SOURCE #0AA02C
                FT_BITMAP_SOURCE #0AB670
                FT_BITMAP_SOURCE #0ACCB4
                FT_BITMAP_SOURCE #0AE2F8
                FT_BITMAP_SOURCE #0AF93C
                FT_BITMAP_SOURCE #0B0F80
                FT_BITMAP_SOURCE #0B25C4
                FT_BITMAP_SOURCE #0B3C08
                FT_BITMAP_SOURCE #0B524C
                FT_BITMAP_SOURCE #0B675C
                FT_BITMAP_SOURCE #0B7C6C
                FT_BITMAP_SOURCE #0B917C
                FT_BITMAP_SOURCE #0BA68C
                FT_BITMAP_SOURCE #0BBB9C
                FT_BITMAP_SOURCE #0BD0AC
                FT_BITMAP_SOURCE #0BE5BC
                FT_BITMAP_SOURCE #0BFACC
                FT_BITMAP_SOURCE #0C0FDC
                FT_BITMAP_SOURCE #0C24EC
                FT_BITMAP_SOURCE #0C39FC
                FT_BITMAP_SOURCE #0C4F0C
                FT_BITMAP_SOURCE #0C641C
                FT_BITMAP_SOURCE #0C792C
                FT_BITMAP_SOURCE #0C8E3C
                FT_BITMAP_SOURCE #0CA34C
                FT_BITMAP_SOURCE #0CB85C
                FT_BITMAP_SOURCE #0CCD6C
                FT_BITMAP_SOURCE #0CE27C
                FT_BITMAP_SOURCE #0CF78C
                FT_BITMAP_SOURCE #0D0C9C
                FT_BITMAP_SOURCE #0D21AC
                FT_BITMAP_SOURCE #0D36BC
                FT_BITMAP_SOURCE #0D4BCC
                FT_BITMAP_SOURCE #0D60DC
                FT_BITMAP_SOURCE #0D75EC
                FT_BITMAP_SOURCE #0D8AFC
                FT_BITMAP_SOURCE #0DA00C
                FT_BITMAP_SOURCE #0DB51C
                FT_BITMAP_SOURCE #0DCA2C
                FT_BITMAP_SOURCE #0DDF3C
BATTLE_UNIT_SRC_SIZE EQU 4
BattleUnitLayTab:                       ; [вариант] → LAYOUT+SIZE (общий канвас кадров, 8Б)
                FT_BITMAP_LAYOUT FT_PALETTED4444, 77, 74
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 123, 118
                FT_BITMAP_LAYOUT FT_PALETTED4444, 77, 74
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 123, 118
                FT_BITMAP_LAYOUT FT_PALETTED4444, 70, 77
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 112, 123
                FT_BITMAP_LAYOUT FT_PALETTED4444, 70, 77
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 112, 123
BATTLE_UNIT_LAY_SIZE EQU 8
BattleUnitVertsTab:
                DEFW BattleUnitVerts0, BattleUnitVerts1
BattleUnitVerts0:                    ; спрайт top-left @ каждой из 99 ячеек (тип 0)
                FT_VERTEX2F 1843, 1024
                FT_VERTEX2F 2969, 1024
                FT_VERTEX2F 4096, 1024
                FT_VERTEX2F 5222, 1024
                FT_VERTEX2F 6348, 1024
                FT_VERTEX2F 7475, 1024
                FT_VERTEX2F 8601, 1024
                FT_VERTEX2F 9728, 1024
                FT_VERTEX2F 10854, 1024
                FT_VERTEX2F 11980, 1024
                FT_VERTEX2F 13107, 1024
                FT_VERTEX2F 1280, 2099
                FT_VERTEX2F 2406, 2099
                FT_VERTEX2F 3532, 2099
                FT_VERTEX2F 4659, 2099
                FT_VERTEX2F 5785, 2099
                FT_VERTEX2F 6912, 2099
                FT_VERTEX2F 8038, 2099
                FT_VERTEX2F 9164, 2099
                FT_VERTEX2F 10291, 2099
                FT_VERTEX2F 11417, 2099
                FT_VERTEX2F 12544, 2099
                FT_VERTEX2F 1843, 3174
                FT_VERTEX2F 2969, 3174
                FT_VERTEX2F 4096, 3174
                FT_VERTEX2F 5222, 3174
                FT_VERTEX2F 6348, 3174
                FT_VERTEX2F 7475, 3174
                FT_VERTEX2F 8601, 3174
                FT_VERTEX2F 9728, 3174
                FT_VERTEX2F 10854, 3174
                FT_VERTEX2F 11980, 3174
                FT_VERTEX2F 13107, 3174
                FT_VERTEX2F 1280, 4249
                FT_VERTEX2F 2406, 4249
                FT_VERTEX2F 3532, 4249
                FT_VERTEX2F 4659, 4249
                FT_VERTEX2F 5785, 4249
                FT_VERTEX2F 6912, 4249
                FT_VERTEX2F 8038, 4249
                FT_VERTEX2F 9164, 4249
                FT_VERTEX2F 10291, 4249
                FT_VERTEX2F 11417, 4249
                FT_VERTEX2F 12544, 4249
                FT_VERTEX2F 1843, 5324
                FT_VERTEX2F 2969, 5324
                FT_VERTEX2F 4096, 5324
                FT_VERTEX2F 5222, 5324
                FT_VERTEX2F 6348, 5324
                FT_VERTEX2F 7475, 5324
                FT_VERTEX2F 8601, 5324
                FT_VERTEX2F 9728, 5324
                FT_VERTEX2F 10854, 5324
                FT_VERTEX2F 11980, 5324
                FT_VERTEX2F 13107, 5324
                FT_VERTEX2F 1280, 6400
                FT_VERTEX2F 2406, 6400
                FT_VERTEX2F 3532, 6400
                FT_VERTEX2F 4659, 6400
                FT_VERTEX2F 5785, 6400
                FT_VERTEX2F 6912, 6400
                FT_VERTEX2F 8038, 6400
                FT_VERTEX2F 9164, 6400
                FT_VERTEX2F 10291, 6400
                FT_VERTEX2F 11417, 6400
                FT_VERTEX2F 12544, 6400
                FT_VERTEX2F 1843, 7475
                FT_VERTEX2F 2969, 7475
                FT_VERTEX2F 4096, 7475
                FT_VERTEX2F 5222, 7475
                FT_VERTEX2F 6348, 7475
                FT_VERTEX2F 7475, 7475
                FT_VERTEX2F 8601, 7475
                FT_VERTEX2F 9728, 7475
                FT_VERTEX2F 10854, 7475
                FT_VERTEX2F 11980, 7475
                FT_VERTEX2F 13107, 7475
                FT_VERTEX2F 1280, 8550
                FT_VERTEX2F 2406, 8550
                FT_VERTEX2F 3532, 8550
                FT_VERTEX2F 4659, 8550
                FT_VERTEX2F 5785, 8550
                FT_VERTEX2F 6912, 8550
                FT_VERTEX2F 8038, 8550
                FT_VERTEX2F 9164, 8550
                FT_VERTEX2F 10291, 8550
                FT_VERTEX2F 11417, 8550
                FT_VERTEX2F 12544, 8550
                FT_VERTEX2F 1843, 9625
                FT_VERTEX2F 2969, 9625
                FT_VERTEX2F 4096, 9625
                FT_VERTEX2F 5222, 9625
                FT_VERTEX2F 6348, 9625
                FT_VERTEX2F 7475, 9625
                FT_VERTEX2F 8601, 9625
                FT_VERTEX2F 9728, 9625
                FT_VERTEX2F 10854, 9625
                FT_VERTEX2F 11980, 9625
                FT_VERTEX2F 13107, 9625
BattleUnitVerts1:                    ; спрайт top-left @ каждой из 99 ячеек (тип 1)
                FT_VERTEX2F 1945, 947
                FT_VERTEX2F 3072, 947
                FT_VERTEX2F 4198, 947
                FT_VERTEX2F 5324, 947
                FT_VERTEX2F 6451, 947
                FT_VERTEX2F 7577, 947
                FT_VERTEX2F 8704, 947
                FT_VERTEX2F 9830, 947
                FT_VERTEX2F 10956, 947
                FT_VERTEX2F 12083, 947
                FT_VERTEX2F 13209, 947
                FT_VERTEX2F 1382, 2022
                FT_VERTEX2F 2508, 2022
                FT_VERTEX2F 3635, 2022
                FT_VERTEX2F 4761, 2022
                FT_VERTEX2F 5888, 2022
                FT_VERTEX2F 7014, 2022
                FT_VERTEX2F 8140, 2022
                FT_VERTEX2F 9267, 2022
                FT_VERTEX2F 10393, 2022
                FT_VERTEX2F 11520, 2022
                FT_VERTEX2F 12646, 2022
                FT_VERTEX2F 1945, 3097
                FT_VERTEX2F 3072, 3097
                FT_VERTEX2F 4198, 3097
                FT_VERTEX2F 5324, 3097
                FT_VERTEX2F 6451, 3097
                FT_VERTEX2F 7577, 3097
                FT_VERTEX2F 8704, 3097
                FT_VERTEX2F 9830, 3097
                FT_VERTEX2F 10956, 3097
                FT_VERTEX2F 12083, 3097
                FT_VERTEX2F 13209, 3097
                FT_VERTEX2F 1382, 4172
                FT_VERTEX2F 2508, 4172
                FT_VERTEX2F 3635, 4172
                FT_VERTEX2F 4761, 4172
                FT_VERTEX2F 5888, 4172
                FT_VERTEX2F 7014, 4172
                FT_VERTEX2F 8140, 4172
                FT_VERTEX2F 9267, 4172
                FT_VERTEX2F 10393, 4172
                FT_VERTEX2F 11520, 4172
                FT_VERTEX2F 12646, 4172
                FT_VERTEX2F 1945, 5248
                FT_VERTEX2F 3072, 5248
                FT_VERTEX2F 4198, 5248
                FT_VERTEX2F 5324, 5248
                FT_VERTEX2F 6451, 5248
                FT_VERTEX2F 7577, 5248
                FT_VERTEX2F 8704, 5248
                FT_VERTEX2F 9830, 5248
                FT_VERTEX2F 10956, 5248
                FT_VERTEX2F 12083, 5248
                FT_VERTEX2F 13209, 5248
                FT_VERTEX2F 1382, 6323
                FT_VERTEX2F 2508, 6323
                FT_VERTEX2F 3635, 6323
                FT_VERTEX2F 4761, 6323
                FT_VERTEX2F 5888, 6323
                FT_VERTEX2F 7014, 6323
                FT_VERTEX2F 8140, 6323
                FT_VERTEX2F 9267, 6323
                FT_VERTEX2F 10393, 6323
                FT_VERTEX2F 11520, 6323
                FT_VERTEX2F 12646, 6323
                FT_VERTEX2F 1945, 7398
                FT_VERTEX2F 3072, 7398
                FT_VERTEX2F 4198, 7398
                FT_VERTEX2F 5324, 7398
                FT_VERTEX2F 6451, 7398
                FT_VERTEX2F 7577, 7398
                FT_VERTEX2F 8704, 7398
                FT_VERTEX2F 9830, 7398
                FT_VERTEX2F 10956, 7398
                FT_VERTEX2F 12083, 7398
                FT_VERTEX2F 13209, 7398
                FT_VERTEX2F 1382, 8473
                FT_VERTEX2F 2508, 8473
                FT_VERTEX2F 3635, 8473
                FT_VERTEX2F 4761, 8473
                FT_VERTEX2F 5888, 8473
                FT_VERTEX2F 7014, 8473
                FT_VERTEX2F 8140, 8473
                FT_VERTEX2F 9267, 8473
                FT_VERTEX2F 10393, 8473
                FT_VERTEX2F 11520, 8473
                FT_VERTEX2F 12646, 8473
                FT_VERTEX2F 1945, 9548
                FT_VERTEX2F 3072, 9548
                FT_VERTEX2F 4198, 9548
                FT_VERTEX2F 5324, 9548
                FT_VERTEX2F 6451, 9548
                FT_VERTEX2F 7577, 9548
                FT_VERTEX2F 8704, 9548
                FT_VERTEX2F 9830, 9548
                FT_VERTEX2F 10956, 9548
                FT_VERTEX2F 12083, 9548
                FT_VERTEX2F 13209, 9548
BATTLE_UNIT_IDLE_BASE EQU 0
BATTLE_UNIT_WALK_BASE EQU 4
BATTLE_UNIT_WALK_N EQU 4
BATTLE_UNIT_ATK_BASE EQU 8
BATTLE_UNIT_ATK_N EQU 4
BATTLE_UNIT_DEATH_BASE EQU 12
BATTLE_UNIT_DEATH_N EQU 4
BattleUnitPixTab:                       ; [тип] → 99×(x,y) DEFW (top-left спрайта в клетке)
                DEFW BattleUnitPix0, BattleUnitPix1
BattleUnitPix0:
                DEFW 1843, 1024
                DEFW 2969, 1024
                DEFW 4096, 1024
                DEFW 5222, 1024
                DEFW 6348, 1024
                DEFW 7475, 1024
                DEFW 8601, 1024
                DEFW 9728, 1024
                DEFW 10854, 1024
                DEFW 11980, 1024
                DEFW 13107, 1024
                DEFW 1280, 2099
                DEFW 2406, 2099
                DEFW 3532, 2099
                DEFW 4659, 2099
                DEFW 5785, 2099
                DEFW 6912, 2099
                DEFW 8038, 2099
                DEFW 9164, 2099
                DEFW 10291, 2099
                DEFW 11417, 2099
                DEFW 12544, 2099
                DEFW 1843, 3174
                DEFW 2969, 3174
                DEFW 4096, 3174
                DEFW 5222, 3174
                DEFW 6348, 3174
                DEFW 7475, 3174
                DEFW 8601, 3174
                DEFW 9728, 3174
                DEFW 10854, 3174
                DEFW 11980, 3174
                DEFW 13107, 3174
                DEFW 1280, 4249
                DEFW 2406, 4249
                DEFW 3532, 4249
                DEFW 4659, 4249
                DEFW 5785, 4249
                DEFW 6912, 4249
                DEFW 8038, 4249
                DEFW 9164, 4249
                DEFW 10291, 4249
                DEFW 11417, 4249
                DEFW 12544, 4249
                DEFW 1843, 5324
                DEFW 2969, 5324
                DEFW 4096, 5324
                DEFW 5222, 5324
                DEFW 6348, 5324
                DEFW 7475, 5324
                DEFW 8601, 5324
                DEFW 9728, 5324
                DEFW 10854, 5324
                DEFW 11980, 5324
                DEFW 13107, 5324
                DEFW 1280, 6400
                DEFW 2406, 6400
                DEFW 3532, 6400
                DEFW 4659, 6400
                DEFW 5785, 6400
                DEFW 6912, 6400
                DEFW 8038, 6400
                DEFW 9164, 6400
                DEFW 10291, 6400
                DEFW 11417, 6400
                DEFW 12544, 6400
                DEFW 1843, 7475
                DEFW 2969, 7475
                DEFW 4096, 7475
                DEFW 5222, 7475
                DEFW 6348, 7475
                DEFW 7475, 7475
                DEFW 8601, 7475
                DEFW 9728, 7475
                DEFW 10854, 7475
                DEFW 11980, 7475
                DEFW 13107, 7475
                DEFW 1280, 8550
                DEFW 2406, 8550
                DEFW 3532, 8550
                DEFW 4659, 8550
                DEFW 5785, 8550
                DEFW 6912, 8550
                DEFW 8038, 8550
                DEFW 9164, 8550
                DEFW 10291, 8550
                DEFW 11417, 8550
                DEFW 12544, 8550
                DEFW 1843, 9625
                DEFW 2969, 9625
                DEFW 4096, 9625
                DEFW 5222, 9625
                DEFW 6348, 9625
                DEFW 7475, 9625
                DEFW 8601, 9625
                DEFW 9728, 9625
                DEFW 10854, 9625
                DEFW 11980, 9625
                DEFW 13107, 9625
BattleUnitPix1:
                DEFW 1945, 947
                DEFW 3072, 947
                DEFW 4198, 947
                DEFW 5324, 947
                DEFW 6451, 947
                DEFW 7577, 947
                DEFW 8704, 947
                DEFW 9830, 947
                DEFW 10956, 947
                DEFW 12083, 947
                DEFW 13209, 947
                DEFW 1382, 2022
                DEFW 2508, 2022
                DEFW 3635, 2022
                DEFW 4761, 2022
                DEFW 5888, 2022
                DEFW 7014, 2022
                DEFW 8140, 2022
                DEFW 9267, 2022
                DEFW 10393, 2022
                DEFW 11520, 2022
                DEFW 12646, 2022
                DEFW 1945, 3097
                DEFW 3072, 3097
                DEFW 4198, 3097
                DEFW 5324, 3097
                DEFW 6451, 3097
                DEFW 7577, 3097
                DEFW 8704, 3097
                DEFW 9830, 3097
                DEFW 10956, 3097
                DEFW 12083, 3097
                DEFW 13209, 3097
                DEFW 1382, 4172
                DEFW 2508, 4172
                DEFW 3635, 4172
                DEFW 4761, 4172
                DEFW 5888, 4172
                DEFW 7014, 4172
                DEFW 8140, 4172
                DEFW 9267, 4172
                DEFW 10393, 4172
                DEFW 11520, 4172
                DEFW 12646, 4172
                DEFW 1945, 5248
                DEFW 3072, 5248
                DEFW 4198, 5248
                DEFW 5324, 5248
                DEFW 6451, 5248
                DEFW 7577, 5248
                DEFW 8704, 5248
                DEFW 9830, 5248
                DEFW 10956, 5248
                DEFW 12083, 5248
                DEFW 13209, 5248
                DEFW 1382, 6323
                DEFW 2508, 6323
                DEFW 3635, 6323
                DEFW 4761, 6323
                DEFW 5888, 6323
                DEFW 7014, 6323
                DEFW 8140, 6323
                DEFW 9267, 6323
                DEFW 10393, 6323
                DEFW 11520, 6323
                DEFW 12646, 6323
                DEFW 1945, 7398
                DEFW 3072, 7398
                DEFW 4198, 7398
                DEFW 5324, 7398
                DEFW 6451, 7398
                DEFW 7577, 7398
                DEFW 8704, 7398
                DEFW 9830, 7398
                DEFW 10956, 7398
                DEFW 12083, 7398
                DEFW 13209, 7398
                DEFW 1382, 8473
                DEFW 2508, 8473
                DEFW 3635, 8473
                DEFW 4761, 8473
                DEFW 5888, 8473
                DEFW 7014, 8473
                DEFW 8140, 8473
                DEFW 9267, 8473
                DEFW 10393, 8473
                DEFW 11520, 8473
                DEFW 12646, 8473
                DEFW 1945, 9548
                DEFW 3072, 9548
                DEFW 4198, 9548
                DEFW 5324, 9548
                DEFW 6451, 9548
                DEFW 7577, 9548
                DEFW 8704, 9548
                DEFW 9830, 9548
                DEFW 10956, 9548
                DEFW 12083, 9548
                DEFW 13209, 9548
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
                DEFB #18, #8E, #03, 17, 29
                DEFB #08, #90, #03, 22, 31
BattleNoneSprite:                      ; «None» ×1.6 бел. [lo,mid,hi,w,h] (статус-палитра)
                DEFB #B4, #92, #03, 48, 14
BATTLE_CAS_ATK_Y     EQU 8140
BATTLE_CAS_DEF_Y     EQU 9676
BattleArrowSrcTab:                     ; стрела ARCH_MSL[4] ×1.6 [lo,mid,hi,w,h]; [0]=вправо [1]=влево
                DEFB #54, #95, #03, 51, 8
                DEFB #EC, #96, #03, 51, 8
BattleCountBarVerts:                   ; 99 ячеек × 2 FT_VERTEX2F (тёмный бар под числом)
                FT_VERTEX2F 2508, 2508
                FT_VERTEX2F 3174, 2841
                FT_VERTEX2F 3635, 2508
                FT_VERTEX2F 4300, 2841
                FT_VERTEX2F 4761, 2508
                FT_VERTEX2F 5427, 2841
                FT_VERTEX2F 5888, 2508
                FT_VERTEX2F 6553, 2841
                FT_VERTEX2F 7014, 2508
                FT_VERTEX2F 7680, 2841
                FT_VERTEX2F 8140, 2508
                FT_VERTEX2F 8806, 2841
                FT_VERTEX2F 9267, 2508
                FT_VERTEX2F 9932, 2841
                FT_VERTEX2F 10393, 2508
                FT_VERTEX2F 11059, 2841
                FT_VERTEX2F 11520, 2508
                FT_VERTEX2F 12185, 2841
                FT_VERTEX2F 12646, 2508
                FT_VERTEX2F 13312, 2841
                FT_VERTEX2F 13772, 2508
                FT_VERTEX2F 14438, 2841
                FT_VERTEX2F 1945, 3584
                FT_VERTEX2F 2611, 3916
                FT_VERTEX2F 3072, 3584
                FT_VERTEX2F 3737, 3916
                FT_VERTEX2F 4198, 3584
                FT_VERTEX2F 4864, 3916
                FT_VERTEX2F 5324, 3584
                FT_VERTEX2F 5990, 3916
                FT_VERTEX2F 6451, 3584
                FT_VERTEX2F 7116, 3916
                FT_VERTEX2F 7577, 3584
                FT_VERTEX2F 8243, 3916
                FT_VERTEX2F 8704, 3584
                FT_VERTEX2F 9369, 3916
                FT_VERTEX2F 9830, 3584
                FT_VERTEX2F 10496, 3916
                FT_VERTEX2F 10956, 3584
                FT_VERTEX2F 11622, 3916
                FT_VERTEX2F 12083, 3584
                FT_VERTEX2F 12748, 3916
                FT_VERTEX2F 13209, 3584
                FT_VERTEX2F 13875, 3916
                FT_VERTEX2F 2508, 4659
                FT_VERTEX2F 3174, 4992
                FT_VERTEX2F 3635, 4659
                FT_VERTEX2F 4300, 4992
                FT_VERTEX2F 4761, 4659
                FT_VERTEX2F 5427, 4992
                FT_VERTEX2F 5888, 4659
                FT_VERTEX2F 6553, 4992
                FT_VERTEX2F 7014, 4659
                FT_VERTEX2F 7680, 4992
                FT_VERTEX2F 8140, 4659
                FT_VERTEX2F 8806, 4992
                FT_VERTEX2F 9267, 4659
                FT_VERTEX2F 9932, 4992
                FT_VERTEX2F 10393, 4659
                FT_VERTEX2F 11059, 4992
                FT_VERTEX2F 11520, 4659
                FT_VERTEX2F 12185, 4992
                FT_VERTEX2F 12646, 4659
                FT_VERTEX2F 13312, 4992
                FT_VERTEX2F 13772, 4659
                FT_VERTEX2F 14438, 4992
                FT_VERTEX2F 1945, 5734
                FT_VERTEX2F 2611, 6067
                FT_VERTEX2F 3072, 5734
                FT_VERTEX2F 3737, 6067
                FT_VERTEX2F 4198, 5734
                FT_VERTEX2F 4864, 6067
                FT_VERTEX2F 5324, 5734
                FT_VERTEX2F 5990, 6067
                FT_VERTEX2F 6451, 5734
                FT_VERTEX2F 7116, 6067
                FT_VERTEX2F 7577, 5734
                FT_VERTEX2F 8243, 6067
                FT_VERTEX2F 8704, 5734
                FT_VERTEX2F 9369, 6067
                FT_VERTEX2F 9830, 5734
                FT_VERTEX2F 10496, 6067
                FT_VERTEX2F 10956, 5734
                FT_VERTEX2F 11622, 6067
                FT_VERTEX2F 12083, 5734
                FT_VERTEX2F 12748, 6067
                FT_VERTEX2F 13209, 5734
                FT_VERTEX2F 13875, 6067
                FT_VERTEX2F 2508, 6809
                FT_VERTEX2F 3174, 7142
                FT_VERTEX2F 3635, 6809
                FT_VERTEX2F 4300, 7142
                FT_VERTEX2F 4761, 6809
                FT_VERTEX2F 5427, 7142
                FT_VERTEX2F 5888, 6809
                FT_VERTEX2F 6553, 7142
                FT_VERTEX2F 7014, 6809
                FT_VERTEX2F 7680, 7142
                FT_VERTEX2F 8140, 6809
                FT_VERTEX2F 8806, 7142
                FT_VERTEX2F 9267, 6809
                FT_VERTEX2F 9932, 7142
                FT_VERTEX2F 10393, 6809
                FT_VERTEX2F 11059, 7142
                FT_VERTEX2F 11520, 6809
                FT_VERTEX2F 12185, 7142
                FT_VERTEX2F 12646, 6809
                FT_VERTEX2F 13312, 7142
                FT_VERTEX2F 13772, 6809
                FT_VERTEX2F 14438, 7142
                FT_VERTEX2F 1945, 7884
                FT_VERTEX2F 2611, 8217
                FT_VERTEX2F 3072, 7884
                FT_VERTEX2F 3737, 8217
                FT_VERTEX2F 4198, 7884
                FT_VERTEX2F 4864, 8217
                FT_VERTEX2F 5324, 7884
                FT_VERTEX2F 5990, 8217
                FT_VERTEX2F 6451, 7884
                FT_VERTEX2F 7116, 8217
                FT_VERTEX2F 7577, 7884
                FT_VERTEX2F 8243, 8217
                FT_VERTEX2F 8704, 7884
                FT_VERTEX2F 9369, 8217
                FT_VERTEX2F 9830, 7884
                FT_VERTEX2F 10496, 8217
                FT_VERTEX2F 10956, 7884
                FT_VERTEX2F 11622, 8217
                FT_VERTEX2F 12083, 7884
                FT_VERTEX2F 12748, 8217
                FT_VERTEX2F 13209, 7884
                FT_VERTEX2F 13875, 8217
                FT_VERTEX2F 2508, 8960
                FT_VERTEX2F 3174, 9292
                FT_VERTEX2F 3635, 8960
                FT_VERTEX2F 4300, 9292
                FT_VERTEX2F 4761, 8960
                FT_VERTEX2F 5427, 9292
                FT_VERTEX2F 5888, 8960
                FT_VERTEX2F 6553, 9292
                FT_VERTEX2F 7014, 8960
                FT_VERTEX2F 7680, 9292
                FT_VERTEX2F 8140, 8960
                FT_VERTEX2F 8806, 9292
                FT_VERTEX2F 9267, 8960
                FT_VERTEX2F 9932, 9292
                FT_VERTEX2F 10393, 8960
                FT_VERTEX2F 11059, 9292
                FT_VERTEX2F 11520, 8960
                FT_VERTEX2F 12185, 9292
                FT_VERTEX2F 12646, 8960
                FT_VERTEX2F 13312, 9292
                FT_VERTEX2F 13772, 8960
                FT_VERTEX2F 14438, 9292
                FT_VERTEX2F 1945, 10035
                FT_VERTEX2F 2611, 10368
                FT_VERTEX2F 3072, 10035
                FT_VERTEX2F 3737, 10368
                FT_VERTEX2F 4198, 10035
                FT_VERTEX2F 4864, 10368
                FT_VERTEX2F 5324, 10035
                FT_VERTEX2F 5990, 10368
                FT_VERTEX2F 6451, 10035
                FT_VERTEX2F 7116, 10368
                FT_VERTEX2F 7577, 10035
                FT_VERTEX2F 8243, 10368
                FT_VERTEX2F 8704, 10035
                FT_VERTEX2F 9369, 10368
                FT_VERTEX2F 9830, 10035
                FT_VERTEX2F 10496, 10368
                FT_VERTEX2F 10956, 10035
                FT_VERTEX2F 11622, 10368
                FT_VERTEX2F 12083, 10035
                FT_VERTEX2F 12748, 10368
                FT_VERTEX2F 13209, 10035
                FT_VERTEX2F 13875, 10368
                FT_VERTEX2F 2508, 11110
                FT_VERTEX2F 3174, 11443
                FT_VERTEX2F 3635, 11110
                FT_VERTEX2F 4300, 11443
                FT_VERTEX2F 4761, 11110
                FT_VERTEX2F 5427, 11443
                FT_VERTEX2F 5888, 11110
                FT_VERTEX2F 6553, 11443
                FT_VERTEX2F 7014, 11110
                FT_VERTEX2F 7680, 11443
                FT_VERTEX2F 8140, 11110
                FT_VERTEX2F 8806, 11443
                FT_VERTEX2F 9267, 11110
                FT_VERTEX2F 9932, 11443
                FT_VERTEX2F 10393, 11110
                FT_VERTEX2F 11059, 11443
                FT_VERTEX2F 11520, 11110
                FT_VERTEX2F 12185, 11443
                FT_VERTEX2F 12646, 11110
                FT_VERTEX2F 13312, 11443
                FT_VERTEX2F 13772, 11110
                FT_VERTEX2F 14438, 11443
BattleCountPen:                        ; 99 ячеек × {DEFW penX, DEFW penY} центр-низ (vertex)
                DEFW 2841, 2595
                DEFW 3968, 2595
                DEFW 5094, 2595
                DEFW 6220, 2595
                DEFW 7347, 2595
                DEFW 8473, 2595
                DEFW 9600, 2595
                DEFW 10726, 2595
                DEFW 11852, 2595
                DEFW 12979, 2595
                DEFW 14105, 2595
                DEFW 2278, 3670
                DEFW 3404, 3670
                DEFW 4531, 3670
                DEFW 5657, 3670
                DEFW 6784, 3670
                DEFW 7910, 3670
                DEFW 9036, 3670
                DEFW 10163, 3670
                DEFW 11289, 3670
                DEFW 12416, 3670
                DEFW 13542, 3670
                DEFW 2841, 4745
                DEFW 3968, 4745
                DEFW 5094, 4745
                DEFW 6220, 4745
                DEFW 7347, 4745
                DEFW 8473, 4745
                DEFW 9600, 4745
                DEFW 10726, 4745
                DEFW 11852, 4745
                DEFW 12979, 4745
                DEFW 14105, 4745
                DEFW 2278, 5820
                DEFW 3404, 5820
                DEFW 4531, 5820
                DEFW 5657, 5820
                DEFW 6784, 5820
                DEFW 7910, 5820
                DEFW 9036, 5820
                DEFW 10163, 5820
                DEFW 11289, 5820
                DEFW 12416, 5820
                DEFW 13542, 5820
                DEFW 2841, 6896
                DEFW 3968, 6896
                DEFW 5094, 6896
                DEFW 6220, 6896
                DEFW 7347, 6896
                DEFW 8473, 6896
                DEFW 9600, 6896
                DEFW 10726, 6896
                DEFW 11852, 6896
                DEFW 12979, 6896
                DEFW 14105, 6896
                DEFW 2278, 7971
                DEFW 3404, 7971
                DEFW 4531, 7971
                DEFW 5657, 7971
                DEFW 6784, 7971
                DEFW 7910, 7971
                DEFW 9036, 7971
                DEFW 10163, 7971
                DEFW 11289, 7971
                DEFW 12416, 7971
                DEFW 13542, 7971
                DEFW 2841, 9046
                DEFW 3968, 9046
                DEFW 5094, 9046
                DEFW 6220, 9046
                DEFW 7347, 9046
                DEFW 8473, 9046
                DEFW 9600, 9046
                DEFW 10726, 9046
                DEFW 11852, 9046
                DEFW 12979, 9046
                DEFW 14105, 9046
                DEFW 2278, 10121
                DEFW 3404, 10121
                DEFW 4531, 10121
                DEFW 5657, 10121
                DEFW 6784, 10121
                DEFW 7910, 10121
                DEFW 9036, 10121
                DEFW 10163, 10121
                DEFW 11289, 10121
                DEFW 12416, 10121
                DEFW 13542, 10121
                DEFW 2841, 11196
                DEFW 3968, 11196
                DEFW 5094, 11196
                DEFW 6220, 11196
                DEFW 7347, 11196
                DEFW 8473, 11196
                DEFW 9600, 11196
                DEFW 10726, 11196
                DEFW 11852, 11196
                DEFW 12979, 11196
                DEFW 14105, 11196
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
BATTLE_PAYLOAD_BYTES EQU 914506
BATTLE_PAYLOAD_SECTORS EQU 1787
BATTLE_BODY_SECTOR   EQU 1
BattlePakName:       DEFB "HMM2BATL.PAK", 0

                endif