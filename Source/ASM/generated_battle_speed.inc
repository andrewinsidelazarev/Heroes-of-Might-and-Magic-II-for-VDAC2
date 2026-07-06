; ==== АВТОГЕНЕРАЦИЯ battle_pack.py — НЕ ПРАВИТЬ (выносы боя в GlobalData #91) ====
; Battle_ApplySpeed копирует набор в рабочий блок BattleAnimTicks..BattleArrowSteps.
GDBattleSpeedSets:                      ; [speed−1] → 21Б (Game::ApplyBattleSpeed k=(10−s)/6, s10=1/18)
                DEFB 9, 4, 4, 9, 9, 63, 54, 27, 36, 27, 45, 63, 81, 63, 81, 54, 99, 63, 72, 32, 48   ; speed 1
                DEFB 8, 4, 4, 8, 8, 56, 48, 24, 32, 24, 40, 56, 72, 56, 72, 48, 88, 56, 64, 36, 43   ; speed 2
                DEFB 7, 3, 3, 7, 7, 49, 42, 21, 28, 21, 35, 49, 63, 49, 63, 42, 77, 49, 56, 41, 37   ; speed 3
                DEFB 6, 3, 3, 6, 6, 42, 36, 18, 24, 18, 30, 42, 54, 42, 54, 36, 66, 42, 48, 48, 32   ; speed 4
                DEFB 5, 2, 2, 5, 5, 35, 30, 15, 20, 15, 25, 35, 45, 35, 45, 30, 55, 35, 40, 58, 27   ; speed 5
                DEFB 4, 2, 2, 4, 4, 28, 24, 12, 16, 12, 20, 28, 36, 28, 36, 24, 44, 28, 32, 72, 21   ; speed 6
                DEFB 3, 1, 1, 3, 3, 21, 18, 9, 12, 9, 15, 21, 27, 21, 27, 18, 33, 21, 24, 96, 16   ; speed 7
                DEFB 2, 1, 1, 2, 2, 14, 12, 6, 8, 6, 10, 14, 18, 14, 18, 12, 22, 14, 16, 144, 11   ; speed 8
                DEFB 1, 1, 1, 1, 1, 7, 6, 3, 4, 3, 5, 7, 9, 7, 9, 6, 11, 7, 8, 255, 5   ; speed 9
                DEFB 1, 1, 1, 1, 1, 7, 6, 3, 4, 3, 5, 7, 9, 7, 9, 6, 11, 7, 8, 255, 2   ; speed 10
GDBattleFrameOfs0_0:                ; (ofsX,ofsY) DEFW ×кадры (4Б/кадр)
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
GDBattleFrameOfs0_1:                ; (ofsX,ofsY) DEFW ×кадры (4Б/кадр)
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
GDBattleFrameOfs1_0:                ; (ofsX,ofsY) DEFW ×кадры (4Б/кадр)
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
GDBattleFrameOfs1_1:                ; (ofsX,ofsY) DEFW ×кадры (4Б/кадр)
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
GDBattleCellAnchor:                     ; 99 × (ax,ay) DEFW — якорь спрайта клетки
                DEFW 2842, 2688
                DEFW 3968, 2688
                DEFW 5094, 2688
                DEFW 6221, 2688
                DEFW 7347, 2688
                DEFW 8474, 2688
                DEFW 9600, 2688
                DEFW 10726, 2688
                DEFW 11853, 2688
                DEFW 12979, 2688
                DEFW 14106, 2688
                DEFW 2278, 3763
                DEFW 3405, 3763
                DEFW 4531, 3763
                DEFW 5658, 3763
                DEFW 6784, 3763
                DEFW 7910, 3763
                DEFW 9037, 3763
                DEFW 10163, 3763
                DEFW 11290, 3763
                DEFW 12416, 3763
                DEFW 13542, 3763
                DEFW 2842, 4838
                DEFW 3968, 4838
                DEFW 5094, 4838
                DEFW 6221, 4838
                DEFW 7347, 4838
                DEFW 8474, 4838
                DEFW 9600, 4838
                DEFW 10726, 4838
                DEFW 11853, 4838
                DEFW 12979, 4838
                DEFW 14106, 4838
                DEFW 2278, 5914
                DEFW 3405, 5914
                DEFW 4531, 5914
                DEFW 5658, 5914
                DEFW 6784, 5914
                DEFW 7910, 5914
                DEFW 9037, 5914
                DEFW 10163, 5914
                DEFW 11290, 5914
                DEFW 12416, 5914
                DEFW 13542, 5914
                DEFW 2842, 6989
                DEFW 3968, 6989
                DEFW 5094, 6989
                DEFW 6221, 6989
                DEFW 7347, 6989
                DEFW 8474, 6989
                DEFW 9600, 6989
                DEFW 10726, 6989
                DEFW 11853, 6989
                DEFW 12979, 6989
                DEFW 14106, 6989
                DEFW 2278, 8064
                DEFW 3405, 8064
                DEFW 4531, 8064
                DEFW 5658, 8064
                DEFW 6784, 8064
                DEFW 7910, 8064
                DEFW 9037, 8064
                DEFW 10163, 8064
                DEFW 11290, 8064
                DEFW 12416, 8064
                DEFW 13542, 8064
                DEFW 2842, 9139
                DEFW 3968, 9139
                DEFW 5094, 9139
                DEFW 6221, 9139
                DEFW 7347, 9139
                DEFW 8474, 9139
                DEFW 9600, 9139
                DEFW 10726, 9139
                DEFW 11853, 9139
                DEFW 12979, 9139
                DEFW 14106, 9139
                DEFW 2278, 10214
                DEFW 3405, 10214
                DEFW 4531, 10214
                DEFW 5658, 10214
                DEFW 6784, 10214
                DEFW 7910, 10214
                DEFW 9037, 10214
                DEFW 10163, 10214
                DEFW 11290, 10214
                DEFW 12416, 10214
                DEFW 13542, 10214
                DEFW 2842, 11290
                DEFW 3968, 11290
                DEFW 5094, 11290
                DEFW 6221, 11290
                DEFW 7347, 11290
                DEFW 8474, 11290
                DEFW 9600, 11290
                DEFW 10726, 11290
                DEFW 11853, 11290
                DEFW 12979, 11290
                DEFW 14106, 11290
GDBattleSeq0_STATIC: DEFB 1, 0
GDBattleSeq0_IDLE1: DEFB 1, 1
GDBattleSeq0_IDLE2: DEFB 1, 2
GDBattleSeq0_IDLE3: DEFB 1, 3
GDBattleSeq0_MOVE_MAIN: DEFB 8, 4, 5, 6, 7, 8, 9, 10, 11
GDBattleSeq0_ATTACK2: DEFB 7, 15, 16, 17, 18, 19, 20, 21
GDBattleSeq0_ATTACK2_END: DEFB 2, 22, 23
GDBattleSeq0_DEATH: DEFB 7, 12, 13, 14, 24, 25, 26, 27
GDBattleSeq0_WINCE_UP: DEFB 3, 12, 13, 14
GDBattleSeq0_WINCE_END: DEFB 1, 13
GDBattleSeq1_STATIC: DEFB 1, 0
GDBattleSeq1_IDLE1: DEFB 4, 1, 2, 3, 2
GDBattleSeq1_IDLE2: DEFB 2, 1, 2
GDBattleSeq1_IDLE3: DEFB 3, 2, 3, 2
GDBattleSeq1_MOVE_MAIN: DEFB 8, 4, 5, 6, 7, 8, 9, 10, 11
GDBattleSeq1_ATTACK2: DEFB 6, 23, 24, 25, 26, 27, 28
GDBattleSeq1_ATTACK2_END: DEFB 5, 27, 26, 25, 24, 23
GDBattleSeq1_SHOOT2: DEFB 7, 15, 16, 17, 18, 19, 20, 21
GDBattleSeq1_SHOOT2_END: DEFB 1, 22
GDBattleSeq1_DEATH: DEFB 6, 29, 30, 31, 32, 33, 34
GDBattleSeq1_WINCE_UP: DEFB 3, 12, 13, 14
GDBattleSeq1_WINCE_END: DEFB 2, 13, 12
GDBattleWinTextTab:                     ; записи надписей окна итога (11Б)
                DEFB #CC, #2E, #05, 34, 22, 1
                DEFW 6224, 4812
                DEFB 1      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #B8, #31, #05, 114, 27, 1
                DEFW 6768, 4812
                DEFB 1      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #C0, #3D, #05, 99, 27, 1
                DEFW 8592, 4812
                DEFB 1      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #34, #48, #05, 54, 14, 0
                DEFW 5600, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #28, #4B, #05, 64, 14, 0
                DEFW 6464, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #A8, #4E, #05, 66, 14, 0
                DEFW 7488, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #44, #52, #05, 18, 14, 0
                DEFW 8544, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #40, #53, #05, 61, 14, 0
                DEFW 8832, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #98, #56, #05, 61, 14, 0
                DEFW 9808, 4812
                DEFB 2      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #F0, #59, #05, 102, 14, 0
                DEFW 6608, 7270
                DEFB 0      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #84, #5F, #05, 96, 14, 0
                DEFW 8240, 7270
                DEFB 0      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #C4, #64, #05, 85, 14, 0
                DEFW 7520, 7654
                DEFB 0      ; видимость: 0=всегда, 1=победа, 2=поражение
                DEFB #6C, #69, #05, 85, 14, 0
                DEFW 7520, 9190
                DEFB 0      ; видимость: 0=всегда, 1=победа, 2=поражение
