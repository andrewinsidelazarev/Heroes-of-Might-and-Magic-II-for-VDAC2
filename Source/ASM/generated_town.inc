; Сгенерировано Source/Tools/town_pack.py — экран города (Knight, потоковый HMM2TOWN.PAK).
                ifndef _HMM2_GENERATED_TOWN_
                define _HMM2_GENERATED_TOWN_

TOWN_PAL_RAMG        EQU #000000
TOWN_IMG_RAMG        EQU #000200
TOWN_IMG_W           EQU 640
TOWN_IMG_H           EQU 256

Town_DL:
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
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE TOWN_IMG_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 640, 256
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 1024, 409
                FT_VERTEX2F 0, 0
                FT_BITMAP_SOURCE #028200
                FT_BITMAP_LAYOUT FT_PALETTED4444, 640, 224
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 1024, 358
                FT_VERTEX2F 0, 6553
                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG
                FT_BITMAP_SOURCE #0D5624
                FT_BITMAP_LAYOUT FT_PALETTED4444, 179, 14
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 286, 22
                FT_VERTEX2F 5913, 6348
                FT_END
Town_DL_SIZE EQU $ - Town_DL

CASTLE_CONSTRUCT_RAMG EQU #088600
Castle_Construct_DL:
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
                FT_BITMAP_SIZE_H 1024, 768
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE CASTLE_CONSTRUCT_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 640, 480
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 1024, 768
                FT_VERTEX2F 0, 0
                FT_END
Castle_Construct_DL_SIZE EQU $ - Castle_Construct_DL
CONSTRUCT_EXIT_X0    EQU 553
CONSTRUCT_EXIT_X1    EQU 633
CONSTRUCT_EXIT_Y0    EQU 428
CONSTRUCT_EXIT_Y1    EQU 453
CONSTRUCT_CHK_RAMG   EQU #0D3600
ConstructChkRec: DEFB #00, #36, #0D, 25, 24
ConstructCostGold:                     ; [slot] → стоимость золота (BuyBuilding KNGT)
                DW 200
                DW 1000
                DW 1000
                DW 2000
                DW 3000
                DW 5000
                DW 2000
                DW 500
                DW 750
                DW 2000
                DW 1250
                DW 500
                DW 500
                DW 1000
                DW 1500
                DW 1500
                DW 1500
                DW 750
ConstructBuildable:                    ; [slot] → 1 если можно строить сразу (ALLOW), иначе 0
                DEFB 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1
ConstructInitBuilt:                    ; [slot] → 1 если построено на старте (BUILT) — копир. в BuiltRuntime
                DEFB 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
ConstructDisable:                      ; [slot] → 1 = вечный DISABLE (запечён серым, рантайм пропускает)
                DEFB 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0
ConstructHitX:                         ; [slot] → левый X ячейки (native=логич.)
                DW 5, 149, 293, 5, 149, 293, 5, 149, 293, 5, 149, 293, 5, 149, 293, 5, 149, 293
ConstructHitY:                         ; [slot] → верхний Y ячейки
                DW 2, 2, 2, 77, 77, 77, 157, 157, 157, 232, 232, 232, 307, 307, 307, 387, 387, 387
ConstructChkVX:                        ; [slot] → X галочки (vertex ×1.6)
                DW 3104, 6784, 10464, 3104, 6784, 10464, 3104, 6784, 10464, 3104, 6784, 10464, 3104, 6784, 10464, 3104, 6784, 10464
ConstructChkVY:                        ; [slot] → Y галочки (vertex ×1.6)
                DW 1104, 1104, 1104, 3024, 3024, 3024, 5072, 5072, 5072, 6992, 6992, 6992, 8912, 8912, 8912, 10960, 10960, 10960
CONSTRUCT_INIT_MASK  EQU #00001         ; начально построенные слоты (BUILT)
CONSTRUCT_SLOT_W     EQU 137
CONSTRUCT_SLOT_H     EQU 70
CONSTRUCT_GOLD_CX    EQU 949
CONSTRUCT_GOLD_VY    EQU 10544

ConstructCostFull:                     ; [slot*14] → 7×DW (gold,wood,merc,ore,sulf,cryst,gems)
                DW 200, 0, 0, 0, 0, 0, 0
                DW 1000, 0, 0, 0, 0, 0, 0
                DW 1000, 0, 0, 5, 0, 0, 0
                DW 2000, 10, 0, 10, 0, 0, 0
                DW 3000, 20, 0, 0, 0, 0, 0
                DW 5000, 20, 0, 0, 0, 20, 0
                DW 2000, 5, 0, 5, 0, 0, 0
                DW 500, 5, 0, 0, 0, 0, 0
                DW 750, 5, 0, 0, 0, 0, 0
                DW 2000, 20, 0, 0, 0, 0, 0
                DW 1250, 0, 0, 5, 0, 0, 0
                DW 500, 5, 0, 0, 0, 0, 0
                DW 500, 0, 0, 0, 0, 0, 0
                DW 1000, 0, 0, 0, 0, 0, 0
                DW 1500, 5, 0, 15, 0, 0, 0
                DW 1500, 0, 0, 5, 0, 0, 0
                DW 1500, 0, 0, 5, 0, 0, 0
                DW 750, 0, 0, 0, 0, 0, 0
ConstructReqMask:                      ; [slot*3] → 3Б маска prereq-слотов (LE)
                DEFB #00, #00, #00
                DEFB #01, #00, #00
                DEFB #01, #10, #00
                DEFB #81, #00, #00
                DEFB #0E, #00, #00
                DEFB #0E, #00, #00
                DEFB #00, #00, #00
                DEFB #00, #00, #00
                DEFB #00, #00, #00
                DEFB #00, #00, #00
                DEFB #00, #00, #00
                DEFB #00, #00, #00
                DEFB #00, #00, #00
                DEFB #00, #00, #00
                DEFB #00, #00, #00
                DEFB #00, #00, #00
                DEFB #00, #00, #00
                DEFB #00, #00, #00
SlotToPano:                            ; [slot] → z-индекс панорамы (255=нет)
                DEFB 14, 8, 15, 16, 12, 13, 11, 10, 9, 255, 18, 7, 17, 0, 2, 4, 5, 6
PanoToSlot:                            ; [z] → слот стройки (255=нет: CASTLE/CAPTAIN)
                DEFB 13, 255, 14, 255, 15, 16, 17, 11, 1, 8, 7, 6, 4, 5, 0, 2, 3, 12, 10
PanoBBoxX0:     DW 286, 0, 0, 288, 8, 131, 0, 219, 134, 0, 152, 148, 0, 148, 176, 200, 217, 159, 478
PanoBBoxY0:     DW 102, 36, 81, 109, 19, 22, 137, 136, 152, 128, 109, 124, 174, 75, 164, 164, 164, 217, 193
PanoBBoxX1:     DW 400, 378, 253, 375, 66, 189, 357, 369, 223, 136, 497, 544, 180, 640, 321, 373, 470, 243, 547
PanoBBoxY1:     DW 128, 175, 97, 143, 152, 144, 256, 171, 197, 203, 212, 218, 256, 218, 241, 256, 256, 256, 256
PATCH_BASE_SEC       EQU 1847
PanoPatchSec:                          ; [z] → сектор ран-патча спрайта здания
                DW 1847, 1852, 1915, 1921, 1926, 1941, 1953, 1965, 1973, 1978, 1989, 2006, 2025, 2044, 2098, 2109, 2126, 2145, 2150
BandPatchSec:                          ; [slot*3 + вариант] 0=plain(BUILT) 1=green(ALLOW) 2=red
                DW 2155, 2159, 2163
                DW 2167, 2171, 2175
                DW 2179, 2183, 2187
                DW 2191, 2195, 2199
                DW 2203, 2207, 2211
                DW 2215, 2219, 2223
                DW 2227, 2231, 2235
                DW 2239, 2243, 2247
                DW 2251, 2255, 2259
                DW 2263, 2267, 2271
                DW 2275, 2279, 2283
                DW 2287, 2291, 2295
                DW 2299, 2303, 2307
                DW 2311, 2315, 2319
                DW 2323, 2327, 2331
                DW 2335, 2339, 2343
                DW 2347, 2351, 2355
                DW 2359, 2363, 2367
CornerPatchSec:                        ; [slot*4 + вариант] 0=clean 1=check 2=deny 3=money
                DW 2371, 2372, 2373, 2374
                DW 2375, 2376, 2377, 2378
                DW 2379, 2380, 2381, 2382
                DW 2383, 2384, 2385, 2386
                DW 2387, 2388, 2389, 2390
                DW 2391, 2392, 2393, 2394
                DW 2395, 2396, 2397, 2398
                DW 2399, 2400, 2401, 2402
                DW 2403, 2404, 2405, 2406
                DW 2407, 2408, 2409, 2410
                DW 2411, 2412, 2413, 2414
                DW 2415, 2416, 2417, 2418
                DW 2419, 2420, 2421, 2422
                DW 2423, 2424, 2425, 2426
                DW 2427, 2428, 2429, 2430
                DW 2431, 2432, 2433, 2434
                DW 2435, 2436, 2437, 2438
                DW 2439, 2440, 2441, 2442
TownResCX:                             ; [res] центр колонки (экран px), город
                DW 916, 982, 916, 982, 916, 982
TownResVY:                             ; [res] vertex Y, город (панель @256)
                DW 7552, 8656, 9632, 7552, 8656, 9632
ConResCX:                              ; [res] центр колонки, окно стройки
                DW 916, 982, 916, 982, 916, 982
ConResVY:                              ; [res] vertex Y, окно стройки (панель @262)
                DW 7552, 8656, 9632, 7552, 8656, 9632
StartRes6:                             ; стартовые 6 ресурсов (Resources_InitStart порядок res6)
                DW 20, 5, 20, 5, 5, 5
CONSTRUCT_STATUE_SLOT EQU 10
CONSTRUCT_WELL_SLOT  EQU 12
CONSTRUCT_WEL2_SLOT  EQU 13
RecruitToSlot:                         ; [recruit idx 0..5] → слот стройки DW1..DW6
                DEFB 0, 1, 2, 3, 4, 5

TOWN_RAMG_BASE       EQU #000000
TOWN_PAYLOAD_BYTES   EQU 945105
TOWN_PAYLOAD_SECTORS EQU 1846
TOWN_BODY_SECTOR     EQU 1
TownPakName:         DEFB "HMM2TOWN.PAK", 0

TOWN_HIT_BLK         EQU 8
TOWN_HIT_W           EQU 80
TOWN_HIT_H           EQU 32
TOWN_NAME_PAL_RAMG   EQU #04B200
Town_Name_Begin_DL:                    ; пролог имени: нативно (имя ×1.6-пред-масштаб), белая-альфа
                FT_BITMAP_TRANSFORM_A 256
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 256
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE TOWN_NAME_PAL_RAMG
                FT_BEGIN FT_BITMAPS
Town_Name_Begin_DL_SIZE EQU $ - Town_Name_Begin_DL
Town_Name_End_DL:
                FT_END
Town_Name_End_DL_SIZE EQU $ - Town_Name_End_DL

FontGlyphTab:                          ; [char-32] → глиф SMALFONT [lo,mid,hi,w,h] (Render_DrawString)
                DEFB #00, #B4, #04, 6, 4
                DEFB #18, #B4, #04, 3, 14
                DEFB #44, #B4, #04, 6, 8
                DEFB #74, #B4, #04, 3, 14
                DEFB #A0, #B4, #04, 9, 17
                DEFB #3C, #B5, #04, 12, 14
                DEFB #E4, #B5, #04, 10, 14
                DEFB #70, #B6, #04, 3, 8
                DEFB #88, #B6, #04, 6, 16
                DEFB #E8, #B6, #04, 6, 16
                DEFB #48, #B7, #04, 3, 14
                DEFB #74, #B7, #04, 9, 12
                DEFB #E0, #B7, #04, 4, 17
                DEFB #24, #B8, #04, 9, 10
                DEFB #80, #B8, #04, 3, 14
                DEFB #AC, #B8, #04, 8, 16
                DEFB #2C, #B9, #04, 8, 14
                DEFB #9C, #B9, #04, 4, 14
                DEFB #D4, #B9, #04, 8, 14
                DEFB #44, #BA, #04, 8, 14
                DEFB #B4, #BA, #04, 8, 14
                DEFB #24, #BB, #04, 8, 14
                DEFB #94, #BB, #04, 8, 14
                DEFB #04, #BC, #04, 8, 14
                DEFB #74, #BC, #04, 8, 14
                DEFB #E4, #BC, #04, 8, 14
                DEFB #54, #BD, #04, 3, 14
                DEFB #80, #BD, #04, 4, 17
                DEFB #C4, #BD, #04, 3, 14
                DEFB #F0, #BD, #04, 9, 11
                DEFB #54, #BE, #04, 3, 14
                DEFB #80, #BE, #04, 9, 14
                DEFB #00, #BF, #04, 3, 14
                DEFB #2C, #BF, #04, 14, 14
                DEFB #F0, #BF, #04, 10, 14
                DEFB #7C, #C0, #04, 10, 14
                DEFB #08, #C1, #04, 12, 14
                DEFB #B0, #C1, #04, 12, 14
                DEFB #58, #C2, #04, 12, 14
                DEFB #00, #C3, #04, 12, 14
                DEFB #A8, #C3, #04, 14, 14
                DEFB #6C, #C4, #04, 6, 14
                DEFB #C0, #C4, #04, 10, 14
                DEFB #4C, #C5, #04, 14, 14
                DEFB #10, #C6, #04, 12, 14
                DEFB #B8, #C6, #04, 16, 14
                DEFB #98, #C7, #04, 15, 14
                DEFB #6C, #C8, #04, 12, 14
                DEFB #14, #C9, #04, 12, 14
                DEFB #BC, #C9, #04, 12, 16
                DEFB #7C, #CA, #04, 14, 14
                DEFB #40, #CB, #04, 10, 14
                DEFB #CC, #CB, #04, 12, 14
                DEFB #74, #CC, #04, 15, 14
                DEFB #48, #CD, #04, 15, 14
                DEFB #1C, #CE, #04, 20, 14
                DEFB #34, #CF, #04, 14, 14
                DEFB #F8, #CF, #04, 14, 14
                DEFB #BC, #D0, #04, 10, 14
                DEFB #48, #D1, #04, 6, 16
                DEFB #A8, #D1, #04, 3, 14
                DEFB #D4, #D1, #04, 6, 16
                DEFB #34, #D2, #04, 3, 14
                DEFB #60, #D2, #04, 9, 14
                DEFB #E0, #D2, #04, 3, 8
                DEFB #F8, #D2, #04, 10, 14
                DEFB #84, #D3, #04, 10, 14
                DEFB #10, #D4, #04, 9, 14
                DEFB #90, #D4, #04, 10, 14
                DEFB #1C, #D5, #04, 9, 14
                DEFB #9C, #D5, #04, 8, 14
                DEFB #0C, #D6, #04, 10, 17
                DEFB #B8, #D6, #04, 12, 14
                DEFB #60, #D7, #04, 6, 14
                DEFB #B4, #D7, #04, 8, 17
                DEFB #3C, #D8, #04, 12, 14
                DEFB #E4, #D8, #04, 6, 14
                DEFB #38, #D9, #04, 18, 14
                DEFB #34, #DA, #04, 12, 14
                DEFB #DC, #DA, #04, 9, 14
                DEFB #5C, #DB, #04, 10, 17
                DEFB #08, #DC, #04, 10, 17
                DEFB #B4, #DC, #04, 10, 14
                DEFB #40, #DD, #04, 9, 14
                DEFB #C0, #DD, #04, 8, 14
                DEFB #30, #DE, #04, 12, 14
                DEFB #D8, #DE, #04, 12, 14
                DEFB #80, #DF, #04, 18, 14
                DEFB #7C, #E0, #04, 10, 14
                DEFB #08, #E1, #04, 12, 17
                DEFB #D4, #E1, #04, 9, 14
                DEFB #54, #E2, #04, 3, 14
                DEFB #80, #E2, #04, 3, 14
                DEFB #AC, #E2, #04, 3, 14
                DEFB #D8, #E2, #04, 3, 14
                DEFB #04, #E3, #04, 3, 14
BigFontGlyphTab:                       ; [char-32] → глиф FONT 14px [lo,mid,hi,w,h] (заголовок)
                DEFB #30, #E3, #04, 6, 4
                DEFB #48, #E3, #04, 4, 20
                DEFB #98, #E3, #04, 10, 10
                DEFB #FC, #E3, #04, 4, 22
                DEFB #54, #E4, #04, 14, 20
                DEFB #6C, #E5, #04, 18, 20
                DEFB #D4, #E6, #04, 16, 20
                DEFB #14, #E8, #04, 4, 10
                DEFB #3C, #E8, #04, 8, 23
                DEFB #F4, #E8, #04, 8, 23
                DEFB #AC, #E9, #04, 18, 24
                DEFB #5C, #EB, #04, 14, 17
                DEFB #4C, #EC, #04, 6, 23
                DEFB #D8, #EC, #04, 15, 14
                DEFB #AC, #ED, #04, 4, 22
                DEFB #04, #EE, #04, 12, 23
                DEFB #18, #EF, #04, 14, 22
                DEFB #4C, #F0, #04, 8, 22
                DEFB #FC, #F0, #04, 12, 22
                DEFB #04, #F2, #04, 12, 22
                DEFB #0C, #F3, #04, 14, 22
                DEFB #40, #F4, #04, 12, 22
                DEFB #48, #F5, #04, 12, 22
                DEFB #50, #F6, #04, 12, 22
                DEFB #58, #F7, #04, 12, 22
                DEFB #60, #F8, #04, 12, 22
                DEFB #68, #F9, #04, 4, 20
                DEFB #B8, #F9, #04, 6, 22
                DEFB #3C, #FA, #04, 4, 22
                DEFB #94, #FA, #04, 15, 17
                DEFB #94, #FB, #04, 4, 22
                DEFB #EC, #FB, #04, 14, 22
                DEFB #20, #FD, #04, 4, 22
                DEFB #78, #FD, #04, 22, 22
                DEFB #5C, #FF, #04, 16, 22
                DEFB #BC, #00, #05, 20, 22
                DEFB #74, #02, #05, 18, 22
                DEFB #00, #04, #05, 16, 22
                DEFB #60, #05, #05, 16, 22
                DEFB #C0, #06, #05, 21, 22
                DEFB #90, #08, #05, 18, 22
                DEFB #1C, #0A, #05, 10, 22
                DEFB #F8, #0A, #05, 15, 22
                DEFB #44, #0C, #05, 18, 22
                DEFB #D0, #0D, #05, 16, 22
                DEFB #30, #0F, #05, 24, 22
                DEFB #40, #11, #05, 22, 22
                DEFB #24, #13, #05, 20, 22
                DEFB #DC, #14, #05, 16, 22
                DEFB #3C, #16, #05, 22, 23
                DEFB #38, #18, #05, 18, 22
                DEFB #C4, #19, #05, 15, 22
                DEFB #10, #1B, #05, 18, 22
                DEFB #9C, #1C, #05, 18, 22
                DEFB #28, #1E, #05, 20, 22
                DEFB #E0, #1F, #05, 26, 22
                DEFB #1C, #22, #05, 24, 22
                DEFB #2C, #24, #05, 21, 22
                DEFB #FC, #25, #05, 16, 22
                DEFB #5C, #27, #05, 9, 22
                DEFB #24, #28, #05, 4, 22
                DEFB #7C, #28, #05, 9, 22
                DEFB #44, #29, #05, 4, 22
                DEFB #9C, #29, #05, 14, 22
                DEFB #D0, #2A, #05, 4, 10
                DEFB #F8, #2A, #05, 15, 22
                DEFB #44, #2C, #05, 16, 22
                DEFB #A4, #2D, #05, 14, 22
                DEFB #D8, #2E, #05, 15, 22
                DEFB #24, #30, #05, 14, 22
                DEFB #58, #31, #05, 12, 22
                DEFB #60, #32, #05, 15, 26
                DEFB #E8, #33, #05, 15, 22
                DEFB #34, #35, #05, 8, 22
                DEFB #E4, #35, #05, 12, 26
                DEFB #1C, #37, #05, 15, 22
                DEFB #68, #38, #05, 8, 22
                DEFB #18, #39, #05, 22, 22
                DEFB #FC, #3A, #05, 15, 22
                DEFB #48, #3C, #05, 14, 22
                DEFB #7C, #3D, #05, 15, 26
                DEFB #04, #3F, #05, 16, 26
                DEFB #A4, #40, #05, 14, 22
                DEFB #D8, #41, #05, 12, 22
                DEFB #E0, #42, #05, 10, 22
                DEFB #BC, #43, #05, 15, 22
                DEFB #08, #45, #05, 14, 22
                DEFB #3C, #46, #05, 20, 22
                DEFB #F4, #47, #05, 15, 22
                DEFB #40, #49, #05, 16, 26
                DEFB #E0, #4A, #05, 14, 22
                DEFB #14, #4C, #05, 4, 22
                DEFB #6C, #4C, #05, 4, 22
                DEFB #C4, #4C, #05, 4, 22
                DEFB #1C, #4D, #05, 4, 22
                DEFB #74, #4D, #05, 4, 22
TownNameStrTab:                        ; [idx-1] → &имя (null-term, для заголовка попапа)
                DW TownNameStr_0
                DW TownNameStr_1
                DW TownNameStr_2
                DW TownNameStr_3
                DW TownNameStr_4
                DW TownNameStr_5
                DW TownNameStr_6
                DW TownNameStr_7
                DW TownNameStr_8
                DW TownNameStr_9
                DW TownNameStr_10
                DW TownNameStr_11
                DW TownNameStr_12
                DW TownNameStr_13
                DW TownNameStr_14
                DW TownNameStr_15
                DW TownNameStr_16
                DW TownNameStr_17
                DW TownNameStr_18
TownNameStr_0: DEFB "Farm", 0
TownNameStr_1: DEFB "Castle", 0
TownNameStr_2: DEFB "Fortifications", 0
TownNameStr_3: DEFB "Captain's Quarters", 0
TownNameStr_4: DEFB "Castle", 0
TownNameStr_5: DEFB "Castle", 0
TownNameStr_6: DEFB "Moat", 0
TownNameStr_7: DEFB "Marketplace", 0
TownNameStr_8: DEFB "Archery Range", 0
TownNameStr_9: DEFB "Thieves Guild", 0
TownNameStr_10: DEFB "Tavern", 0
TownNameStr_11: DEFB "Mage Guild", 0
TownNameStr_12: DEFB "Jousting Arena", 0
TownNameStr_13: DEFB "Cathedral", 0
TownNameStr_14: DEFB "Thatched Hut", 0
TownNameStr_15: DEFB "Blacksmith", 0
TownNameStr_16: DEFB "Armory", 0
TownNameStr_17: DEFB "Well", 0
TownNameStr_18: DEFB "Statue", 0
TownDescTab:                           ; [idx-1] → &блок строк описания (null-term; пустая строка = конец)
                DW TownDescBlk_0
                DW TownDescBlk_1
                DW TownDescBlk_2
                DW TownDescBlk_3
                DW TownDescBlk_4
                DW TownDescBlk_5
                DW TownDescBlk_6
                DW TownDescBlk_7
                DW TownDescBlk_8
                DW TownDescBlk_9
                DW TownDescBlk_10
                DW TownDescBlk_11
                DW TownDescBlk_12
                DW TownDescBlk_13
                DW TownDescBlk_14
                DW TownDescBlk_15
                DW TownDescBlk_16
                DW TownDescBlk_17
                DW TownDescBlk_18
TownDescBlk_0:
                DEFB "The Farm increases production", 0
                DEFB "of Peasants by 8 per week.", 0
                DEFB 0
TownDescBlk_1:
                DEFB "The Castle improves the town's", 0
                DEFB "defense and increases its", 0
                DEFB "income to 1000 gold per day.", 0
                DEFB 0
TownDescBlk_2:
                DEFB "The Fortifications increase the", 0
                DEFB "toughness of the walls,", 0
                DEFB "increasing the number of turns", 0
                DEFB "it takes to knock them down.", 0
                DEFB 0
TownDescBlk_3:
                DEFB "The Captain's Quarters", 0
                DEFB "provides a captain to assist in", 0
                DEFB "the castle's defense when no", 0
                DEFB "hero is present.", 0
                DEFB 0
TownDescBlk_4:
                DEFB "The Left Turret provides extra", 0
                DEFB "firepower during castle", 0
                DEFB "combat.", 0
                DEFB 0
TownDescBlk_5:
                DEFB "The Right Turret provides", 0
                DEFB "extra firepower during castle", 0
                DEFB "combat.", 0
                DEFB 0
TownDescBlk_6:
                DEFB "The Moat slows and weakens", 0
                DEFB "attacking units. Any walking", 0
                DEFB "unit entering the moat must end", 0
                DEFB "its turn there and can only", 0
                DEFB "move within the moat one hex at", 0
                DEFB "a time. Any creature present in", 0
                DEFB "the moat will have its defense", 0
                DEFB "skill reduced by 3.", 0
                DEFB 0
TownDescBlk_7:
                DEFB "The Marketplace can be used to", 0
                DEFB "convert one type of resource", 0
                DEFB "into another. The more", 0
                DEFB "marketplaces you control, the", 0
                DEFB "better the exchange rate.", 0
                DEFB 0
TownDescBlk_8:
                DEFB "Recruit Archer.", 0
                DEFB 0
TownDescBlk_9:
                DEFB "The Thieves' Guild provides", 0
                DEFB "information on enemy players.", 0
                DEFB "Thieves' Guilds can also provide", 0
                DEFB "scouting information on enemy", 0
                DEFB "towns. Additional Guilds", 0
                DEFB "provide more information.", 0
                DEFB 0
TownDescBlk_10:
                DEFB "The Tavern increases morale", 0
                DEFB "for troops defending the castle.", 0
                DEFB 0
TownDescBlk_11:
                DEFB "The Mage Guild allows heroes", 0
                DEFB "to learn spells and replenish", 0
                DEFB "their spell points.", 0
                DEFB 0
TownDescBlk_12:
                DEFB "Recruit Cavalry.", 0
                DEFB 0
TownDescBlk_13:
                DEFB "Recruit Paladin.", 0
                DEFB 0
TownDescBlk_14:
                DEFB "Recruit Peasant.", 0
                DEFB 0
TownDescBlk_15:
                DEFB "Recruit Pikeman.", 0
                DEFB 0
TownDescBlk_16:
                DEFB "Recruit Swordsman.", 0
                DEFB 0
TownDescBlk_17:
                DEFB "The Well increases the growth", 0
                DEFB "rate of all dwellings by 2", 0
                DEFB "creatures per week.", 0
                DEFB 0
TownDescBlk_18:
                DEFB "The Statue increases the town's", 0
                DEFB "income by 250 gold per day.", 0
                DEFB 0
TownInfoDL_0:                        ; попап BUYBUILD, middleH=0
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0DDEB0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 160, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 256, 158
                FT_VERTEX2F 4096, 3616
                FT_BITMAP_SOURCE #0D5FF0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 158
                FT_VERTEX2F 8192, 3616
                FT_BITMAP_SOURCE #0E38E0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 130
                FT_VERTEX2F 4064, 6144
                FT_BITMAP_SOURCE #0DB120
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 130
                FT_VERTEX2F 8192, 6144
                FT_END
TownInfoDL_0_SIZE EQU $ - TownInfoDL_0
TownInfoDL_1:                        ; попап BUYBUILD, middleH=14
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0DDEB0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 160, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 256, 159
                FT_VERTEX2F 4096, 3424
                FT_BITMAP_SOURCE #0D5FF0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 159
                FT_VERTEX2F 8192, 3424
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 22
                FT_VERTEX2F 4064, 5968
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 22
                FT_VERTEX2F 8192, 5968
                FT_BITMAP_SOURCE #0E38E0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 130
                FT_VERTEX2F 4064, 6320
                FT_BITMAP_SOURCE #0DB120
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 130
                FT_VERTEX2F 8192, 6320
                FT_END
TownInfoDL_1_SIZE EQU $ - TownInfoDL_1
TownInfoDL_2:                        ; попап BUYBUILD, middleH=30
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0DDEB0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 160, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 256, 158
                FT_VERTEX2F 4096, 3232
                FT_BITMAP_SOURCE #0D5FF0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 158
                FT_VERTEX2F 8192, 3232
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 48
                FT_VERTEX2F 4064, 5760
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 48
                FT_VERTEX2F 8192, 5760
                FT_BITMAP_SOURCE #0E38E0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 130
                FT_VERTEX2F 4064, 6528
                FT_BITMAP_SOURCE #0DB120
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 130
                FT_VERTEX2F 8192, 6528
                FT_END
TownInfoDL_2_SIZE EQU $ - TownInfoDL_2
TownInfoDL_3:                        ; попап BUYBUILD, middleH=94
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0DDEB0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 160, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 256, 159
                FT_VERTEX2F 4096, 2400
                FT_BITMAP_SOURCE #0D5FF0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 159
                FT_VERTEX2F 8192, 2400
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 4944
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 4944
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 5840
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 5840
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 38
                FT_VERTEX2F 4064, 6736
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 38
                FT_VERTEX2F 8192, 6736
                FT_BITMAP_SOURCE #0E38E0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 130
                FT_VERTEX2F 4064, 7344
                FT_BITMAP_SOURCE #0DB120
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 130
                FT_VERTEX2F 8192, 7344
                FT_END
TownInfoDL_3_SIZE EQU $ - TownInfoDL_3
TownInfoDL_4:                        ; попап BUYBUILD, middleH=46
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0DDEB0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 160, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 256, 158
                FT_VERTEX2F 4096, 3024
                FT_BITMAP_SOURCE #0D5FF0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 158
                FT_VERTEX2F 8192, 3024
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 5552
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 5552
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 18
                FT_VERTEX2F 4064, 6448
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 18
                FT_VERTEX2F 8192, 6448
                FT_BITMAP_SOURCE #0E38E0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 129
                FT_VERTEX2F 4064, 6736
                FT_BITMAP_SOURCE #0DB120
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 129
                FT_VERTEX2F 8192, 6736
                FT_END
TownInfoDL_4_SIZE EQU $ - TownInfoDL_4
TownInfoDL_5:                        ; попап BUYBUILD, middleH=62
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0DDEB0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 160, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 256, 158
                FT_VERTEX2F 4096, 2816
                FT_BITMAP_SOURCE #0D5FF0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 158
                FT_VERTEX2F 8192, 2816
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 5344
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 5344
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 44
                FT_VERTEX2F 4064, 6240
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 44
                FT_VERTEX2F 8192, 6240
                FT_BITMAP_SOURCE #0E38E0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 129
                FT_VERTEX2F 4064, 6944
                FT_BITMAP_SOURCE #0DB120
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 129
                FT_VERTEX2F 8192, 6944
                FT_END
TownInfoDL_5_SIZE EQU $ - TownInfoDL_5
TownInfoDLTab:                         ; [idx-1] → DW addr, DW size (окно по высоте текста)
                DW TownInfoDL_0, TownInfoDL_0_SIZE
                DW TownInfoDL_1, TownInfoDL_1_SIZE
                DW TownInfoDL_2, TownInfoDL_2_SIZE
                DW TownInfoDL_2, TownInfoDL_2_SIZE
                DW TownInfoDL_1, TownInfoDL_1_SIZE
                DW TownInfoDL_1, TownInfoDL_1_SIZE
                DW TownInfoDL_3, TownInfoDL_3_SIZE
                DW TownInfoDL_4, TownInfoDL_4_SIZE
                DW TownInfoDL_0, TownInfoDL_0_SIZE
                DW TownInfoDL_5, TownInfoDL_5_SIZE
                DW TownInfoDL_0, TownInfoDL_0_SIZE
                DW TownInfoDL_1, TownInfoDL_1_SIZE
                DW TownInfoDL_0, TownInfoDL_0_SIZE
                DW TownInfoDL_0, TownInfoDL_0_SIZE
                DW TownInfoDL_0, TownInfoDL_0_SIZE
                DW TownInfoDL_0, TownInfoDL_0_SIZE
                DW TownInfoDL_0, TownInfoDL_0_SIZE
                DW TownInfoDL_1, TownInfoDL_1_SIZE
                DW TownInfoDL_0, TownInfoDL_0_SIZE
TownInfoTitleVY:                       ; [idx-1] → vertex Y заголовка (area.y+10)
                DW 5504, 5325, 5120, 5120, 5325, 5325, 4301, 4915, 5504, 4710, 5504, 5325, 5504, 5504, 5504, 5504, 5504, 5325, 5504
TownInfoLine0VY:                       ; [idx-1] → vertex Y первой строки (заголовок+26)
                DW 6170, 5990, 5786, 5786, 5990, 5990, 4966, 5581, 6170, 5376, 6170, 5990, 6170, 6170, 6170, 6170, 6170, 5990, 6170
TOWN_INFO_LINE_H     EQU 410          ; шаг строк (16 native ×1.6, vertex)

TavernIntroBlk:                        ; вступление (константа, FONT белый)
                DEFB "A generous tip for the barkeep", 0
                DEFB "yields the following rumor:", 0
                DEFB 0
TavernRumorTab:                        ; [неделя mod 7] → блок строк слуха
                DW TavernRumBlk_0
                DW TavernRumBlk_1
                DW TavernRumBlk_2
                DW TavernRumBlk_3
                DW TavernRumBlk_4
                DW TavernRumBlk_5
                DW TavernRumBlk_6
TavernRumBlk_0:
                DEFB "The truth is out there.", 0
                DEFB 0
TavernRumBlk_1:
                DEFB "The dark side is stronger.", 0
                DEFB 0
TavernRumBlk_2:
                DEFB "The end of the world is near.", 0
                DEFB 0
TavernRumBlk_3:
                DEFB "The bones of Lord Slayer are", 0
                DEFB "buried in the foundation of the", 0
                DEFB "arena.", 0
                DEFB 0
TavernRumBlk_4:
                DEFB "A Black Dragon will take out a", 0
                DEFB "Titan any day of the week.", 0
                DEFB 0
TavernRumBlk_5:
                DEFB "He told her: Yada yada yada...", 0
                DEFB "and then she said: Blah, blah,", 0
                DEFB "blah...", 0
                DEFB 0
TavernRumBlk_6:
                DEFB "An unknown force is being", 0
                DEFB "resurrected...", 0
                DEFB 0
TavernDL_0:                        ; окно таверны, middleH=173
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0DDEB0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 160, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 256, 159
                FT_VERTEX2F 4096, 1376
                FT_BITMAP_SOURCE #0D5FF0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 159
                FT_VERTEX2F 8192, 1376
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 3920
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 3920
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 4816
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 4816
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 5712
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 5712
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 6608
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 6608
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 53
                FT_VERTEX2F 4064, 7504
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 53
                FT_VERTEX2F 8192, 7504
                FT_BITMAP_SOURCE #0E38E0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 129
                FT_VERTEX2F 4064, 8352
                FT_BITMAP_SOURCE #0DB120
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 129
                FT_VERTEX2F 8192, 8352
                FT_BITMAP_SOURCE #0F8000
                FT_BITMAP_LAYOUT FT_PALETTED4444, 188, 100
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 301, 160
                FT_VERTEX2F 5786, 3942
                FT_BITMAP_SOURCE #0FC970
                FT_BITMAP_LAYOUT FT_PALETTED4444, 95, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 152, 40
                FT_VERTEX2F 6989, 8602
                FT_END
TavernDL_0_SIZE EQU $ - TavernDL_0
TavernDL_0_OkPress:
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0FD2B8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 95, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 152, 40
                FT_VERTEX2F 6989, 8602
                FT_END
TavernDL_0_OkPress_SIZE EQU $ - TavernDL_0_OkPress
TavernDL_1:                        ; окно таверны, middleH=205
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0DDEB0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 160, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 256, 158
                FT_VERTEX2F 4096, 976
                FT_BITMAP_SOURCE #0D5FF0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 158
                FT_VERTEX2F 8192, 976
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 3504
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 3504
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 4400
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 4400
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 5296
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 5296
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 6192
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 6192
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 7088
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 7088
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 48
                FT_VERTEX2F 4064, 7984
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 48
                FT_VERTEX2F 8192, 7984
                FT_BITMAP_SOURCE #0E38E0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 130
                FT_VERTEX2F 4064, 8752
                FT_BITMAP_SOURCE #0DB120
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 130
                FT_VERTEX2F 8192, 8752
                FT_BITMAP_SOURCE #0F8000
                FT_BITMAP_LAYOUT FT_PALETTED4444, 188, 100
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 301, 160
                FT_VERTEX2F 5786, 3533
                FT_BITMAP_SOURCE #0FC970
                FT_BITMAP_LAYOUT FT_PALETTED4444, 95, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 152, 40
                FT_VERTEX2F 6989, 9011
                FT_END
TavernDL_1_SIZE EQU $ - TavernDL_1
TavernDL_1_OkPress:
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0FD2B8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 95, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 152, 40
                FT_VERTEX2F 6989, 9011
                FT_END
TavernDL_1_OkPress_SIZE EQU $ - TavernDL_1_OkPress
TavernDL_2:                        ; окно таверны, middleH=189
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0DDEB0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 160, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 256, 158
                FT_VERTEX2F 4096, 1184
                FT_BITMAP_SOURCE #0D5FF0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 158
                FT_VERTEX2F 8192, 1184
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 3712
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 3712
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 4608
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 4608
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 5504
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 5504
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 6400
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 6400
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 7296
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 7296
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 22
                FT_VERTEX2F 4064, 8192
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 22
                FT_VERTEX2F 8192, 8192
                FT_BITMAP_SOURCE #0E38E0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 130
                FT_VERTEX2F 4064, 8544
                FT_BITMAP_SOURCE #0DB120
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 130
                FT_VERTEX2F 8192, 8544
                FT_BITMAP_SOURCE #0F8000
                FT_BITMAP_LAYOUT FT_PALETTED4444, 188, 100
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 301, 160
                FT_VERTEX2F 5786, 3738
                FT_BITMAP_SOURCE #0FC970
                FT_BITMAP_LAYOUT FT_PALETTED4444, 95, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 152, 40
                FT_VERTEX2F 6989, 8806
                FT_END
TavernDL_2_SIZE EQU $ - TavernDL_2
TavernDL_2_OkPress:
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0FD2B8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 95, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 152, 40
                FT_VERTEX2F 6989, 8806
                FT_END
TavernDL_2_OkPress_SIZE EQU $ - TavernDL_2_OkPress
TavernDLTab:                           ; [неделя mod 7] → DW DL, DW size, DW press, DW psize
                DW TavernDL_0, TavernDL_0_SIZE, TavernDL_0_OkPress, TavernDL_0_OkPress_SIZE
                DW TavernDL_0, TavernDL_0_SIZE, TavernDL_0_OkPress, TavernDL_0_OkPress_SIZE
                DW TavernDL_0, TavernDL_0_SIZE, TavernDL_0_OkPress, TavernDL_0_OkPress_SIZE
                DW TavernDL_1, TavernDL_1_SIZE, TavernDL_1_OkPress, TavernDL_1_OkPress_SIZE
                DW TavernDL_2, TavernDL_2_SIZE, TavernDL_2_OkPress, TavernDL_2_OkPress_SIZE
                DW TavernDL_1, TavernDL_1_SIZE, TavernDL_1_OkPress, TavernDL_1_OkPress_SIZE
                DW TavernDL_2, TavernDL_2_SIZE, TavernDL_2_OkPress, TavernDL_2_OkPress_SIZE
TavernTitleVY:                         ; [rumor] → vertex Y заголовка «Tavern»
                DW 3277, 3277, 3277, 2867, 3072, 2867, 3072
TavernIntroVY:                         ; [rumor] → vertex Y первой строки вступления
                DW 6707, 6707, 6707, 6298, 6502, 6298, 6502
TavernRumorVY:                         ; [rumor] → vertex Y первой строки слуха
                DW 7936, 7936, 7936, 7526, 7731, 7526, 7731
TavernOkHitY0:                         ; [rumor] → лог. Y верх кнопки OKAY (hit-зона, DW)
                DW 336, 336, 336, 352, 344, 352, 344
TAVERN_OK_X0         EQU 273   ; hit-зона OKAY (лог.)
TAVERN_OK_X1         EQU 368
TAVERN_OK_H          EQU 25
TAVERN_RUMOR_COUNT   EQU 7
TAV_TAIL_SECTOR      EQU 3025   ; хвост (TAVWIN+OKAY) в PAK
TAV_TAIL_SECTORS     EQU 51
TAV_TAIL_BASE        EQU #0F8000 ; RAM_G ЗА курсором (#F8000..#100000)

MK_SECTOR            EQU 3076     ; ассеты рынка в PAK (стрим в область найма)
MK_SECTORS           EQU 50
RECR_SECTOR          EQU 680   ; RECRBKG в payload (рестрим после рынка)
RECR_SECTORS         EQU 191
Market_DL:                             ; окно рынка: рамка + сетки + кнопки (отжатые)
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0DDEB0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 160, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 256, 159
                FT_VERTEX2F 4096, 224
                FT_BITMAP_SOURCE #0D5FF0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 99
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 159
                FT_VERTEX2F 8192, 224
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 2768
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 2768
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 3664
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 3664
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 4560
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 4560
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 5456
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 5456
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 6352
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 6352
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 7248
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 7248
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 56
                FT_VERTEX2F 4064, 8144
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 56
                FT_VERTEX2F 8192, 8144
                FT_BITMAP_SOURCE #0E22DA
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 29
                FT_VERTEX2F 4064, 9040
                FT_BITMAP_SOURCE #0D9D4A
                FT_BITMAP_LAYOUT FT_PALETTED4444, 145, 45
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 232, 29
                FT_VERTEX2F 8192, 9040
                FT_BITMAP_SOURCE #0E38E0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 161, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 258, 129
                FT_VERTEX2F 4064, 9504
                FT_BITMAP_SOURCE #0DB120
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 81
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 230, 129
                FT_VERTEX2F 8192, 9504
                FT_BITMAP_SOURCE #056728
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 5069, 6733
                FT_BITMAP_SOURCE #056728
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 8550, 6733
                FT_BITMAP_SOURCE #056BAC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 6016, 6733
                FT_BITMAP_SOURCE #056BAC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 9498, 6733
                FT_BITMAP_SOURCE #057030
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 6963, 6733
                FT_BITMAP_SOURCE #057030
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 10445, 6733
                FT_BITMAP_SOURCE #0574B4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 5069, 7680
                FT_BITMAP_SOURCE #0574B4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 8550, 7680
                FT_BITMAP_SOURCE #057938
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 6016, 7680
                FT_BITMAP_SOURCE #057938
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 9498, 7680
                FT_BITMAP_SOURCE #057DBC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 6963, 7680
                FT_BITMAP_SOURCE #057DBC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 10445, 7680
                FT_BITMAP_SOURCE #058240
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 6016, 8627
                FT_BITMAP_SOURCE #058240
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
                FT_VERTEX2F 9498, 8627
                FT_BITMAP_SOURCE #056418
                FT_BITMAP_LAYOUT FT_PALETTED4444, 14, 14
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 22, 22
                FT_VERTEX2F 5350, 5171
                FT_BITMAP_SOURCE #0565A0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 14, 14
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 22, 22
                FT_VERTEX2F 10701, 5171
                FT_BITMAP_SOURCE #058C68
                FT_BITMAP_LAYOUT FT_PALETTED4444, 96, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 154, 40
                FT_VERTEX2F 6963, 5709
                FT_BITMAP_SOURCE #059F28
                FT_BITMAP_LAYOUT FT_PALETTED4444, 96, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 154, 40
                FT_VERTEX2F 8704, 8832
                FT_END
Market_DL_SIZE EQU $ - Market_DL
Market_MkArrLPress_DL:
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0564DC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 14, 14
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 22, 22
                FT_VERTEX2F 5350, 5171
                FT_END
Market_MkArrLPress_DL_SIZE EQU $ - Market_MkArrLPress_DL
Market_MkArrRPress_DL:
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #056664
                FT_BITMAP_LAYOUT FT_PALETTED4444, 14, 14
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 22, 22
                FT_VERTEX2F 10701, 5171
                FT_END
Market_MkArrRPress_DL_SIZE EQU $ - Market_MkArrRPress_DL
Market_MkTradePress_DL:
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0595C8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 96, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 154, 40
                FT_VERTEX2F 6963, 5709
                FT_END
Market_MkTradePress_DL_SIZE EQU $ - Market_MkTradePress_DL
Market_MkExitPress_DL:
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #05A888
                FT_BITMAP_LAYOUT FT_PALETTED4444, 96, 25
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 154, 40
                FT_VERTEX2F 8704, 8832
                FT_END
Market_MkExitPress_DL_SIZE EQU $ - Market_MkExitPress_DL
Market_MkSel_DL:                       ; SOURCE+LAYOUT+SIZE (vertex добавляет Z80)
                FT_BITMAP_SOURCE #0586C4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 38, 38
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 61, 61
Market_MkSel_DL_SIZE EQU $ - Market_MkSel_DL
Market_MkFromTo_DL:                       ; SOURCE+LAYOUT+SIZE (vertex добавляет Z80)
                FT_BITMAP_SOURCE #054E00
                FT_BITMAP_LAYOUT FT_PALETTED4444, 43, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 69, 26
Market_MkFromTo_DL_SIZE EQU $ - Market_MkFromTo_DL
Market_MkBar_DL:                       ; SOURCE+LAYOUT+SIZE (vertex добавляет Z80)
                FT_BITMAP_SOURCE #0550B0
                FT_BITMAP_LAYOUT FT_PALETTED4444, 230, 21
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 368, 34
Market_MkBar_DL_SIZE EQU $ - Market_MkBar_DL
Market_MkSlider_DL:                       ; SOURCE+LAYOUT+SIZE (vertex добавляет Z80)
                FT_BITMAP_SOURCE #056390
                FT_BITMAP_LAYOUT FT_PALETTED4444, 17, 8
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 27, 13
Market_MkSlider_DL_SIZE EQU $ - Market_MkSlider_DL
Market_ResIconLay_DL:
                FT_BITMAP_LAYOUT FT_PALETTED4444, 34, 34
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 54, 54
Market_ResIconLay_DL_SIZE EQU $ - Market_ResIconLay_DL
MarketResSrcTab:                       ; [res] → DW адрес иконки TRADPOST[7+res]
                DW #6728, #6BAC, #7030, #74B4, #7938, #7DBC, #8240
MarketResSrcHiTab:                     ; [res] → DB старший байт адреса
                DB #05, #05, #05, #05, #05, #05, #05
MK_TITLE_VY          EQU 2125   ; «Marketplace» жёлтым, центр 320
MK_GRID_FROM_X       EQU 198
MK_GRID_TO_X         EQU 334
MK_GRID_Y            EQU 263
MarketGridOfs:                         ; 7 × (dx, dy) DEFB — раскладка 3×3
                DEFB 0, 0
                DEFB 37, 0
                DEFB 74, 0
                DEFB 0, 37
                DEFB 37, 37
                DEFB 74, 37
                DEFB 37, 74
MK_QTY_VY            EQU 4787 ; число qty над слайдером (центр 320)
MK_MSG_VY            EQU 2688   ; строка «I can offer you …»
MK_MSG2_VY           EQU 3098
MK_ICON_FROM_VX      EQU 5965  ; иконка from (низ y+115)
MK_ICON_TO_VX        EQU 9549
MK_ICON_VY           EQU 3942
MK_FROMTO_VX         EQU 7629   ; обмен-стрелки [0] 43×16 @ y+90
MK_FROMTO_VY         EQU 4173
MK_BAR_VX            EQU 5197 ; слайдер-полоса @ y+128
MK_BAR_VY            EQU 5146
MK_SLIDER_Y          EQU 207   ; лог. Y ползунка (по центру полосы)
MK_BAR_Y0            EQU 201   ; лог. Y полосы (клик по полосе = set qty)
MK_MSG_X0            EQU 200   ; лево offer-текста
MK_SLIDER_X0         EQU 206  ; лог. X начала хода (187px)
MK_SELL_VX           EQU 5837   ; «-N (M)» под иконкой from (центр)
MK_BUY_VX            EQU 10547  ; «+N (M)» под иконкой to
MK_INFO_VY           EQU 4838
MK_TRADE_X0          EQU 272
MK_TRADE_Y0          EQU 223
MK_EXIT_X0           EQU 340
MK_EXIT_Y0           EQU 345
MK_BTN_W             EQU 96
MK_BTN_H             EQU 25
MK_ARRL_X0           EQU 209
MK_ARRR_X0           EQU 418
MK_ARR_Y0            EQU 202
MK_ARR_WH            EQU 14
MK_MAX_Y0            EQU 153    ; «Max» кнопка-текст (центр−5, шир~30)
MK_MIN_Y0            EQU 176
MK_MAXMIN_X0         EQU 300
MK_MAXMIN_X1         EQU 340
MK_MAXMIN_H          EQU 12
MarketRateTab:                         ; [from*7+to] → DW курс (1 рынок; 0 = same)
                DW 0, 20, 10, 20, 20, 20, 25
                DW 5, 0, 5, 10, 10, 10, 50
                DW 10, 20, 0, 20, 20, 20, 25
                DW 5, 10, 5, 0, 10, 10, 50
                DW 5, 10, 5, 10, 0, 10, 50
                DW 5, 10, 5, 10, 10, 0, 50
                DW 2500, 5000, 2500, 5000, 5000, 5000, 0

WELL_SECTOR          EQU 3126   ; база well в PAK (стрим в construct-область)
WELL_SECTORS         EQU 600
CONSTRUCT_SECTOR     EQU 1092   ; рестрим construct после well
CONSTRUCT_SECTORS    EQU 600
WellSecPatchSec:                       ; [DW1..DW6] → сектор патча секции
                DW 2443, 2538, 2633, 2728, 2827, 2926
WellAvailCX:                           ; [i] → физ. центр числа Available
                DW 206, 206, 206, 709, 709, 709
WellAvailVY:                           ; [i] → vertex Y числа Available
                DW 3123, 6963, 10803, 3123, 6963, 10803
WellExit0_DL:
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0FDC00
                FT_BITMAP_LAYOUT FT_PALETTED4444, 61, 19
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 98, 30
                FT_VERTEX2F 14822, 11802
                FT_END
WellExit0_DL_SIZE EQU $ - WellExit0_DL
WellExit1_DL:
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0FE088
                FT_BITMAP_LAYOUT FT_PALETTED4444, 61, 19
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 98, 30
                FT_VERTEX2F 14822, 11802
                FT_END
WellExit1_DL_SIZE EQU $ - WellExit1_DL
WELL_EXIT_X0         EQU 579
WELL_EXIT_Y0         EQU 461
WELL_EXIT_W          EQU 61
WELL_EXIT_H          EQU 19
WellBarStr:          DEFB "Town Population Information and Statistics", 0

RECRUIT_WIN_RAMG     EQU #054E00
Recruit_Win_DL:                        ; окно найма RECRBKG ×1.6 по центру (тень — Render_WindowShadowDL)
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE RECRUIT_WIN_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 321, 304
                FT_BITMAP_SIZE_H 513, 486
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 513, 486
                FT_VERTEX2F 4080, 2256
                FT_END
Recruit_Win_DL_SIZE EQU $ - Recruit_Win_DL
RECR_NAME_VY         EQU 2944
RECR_AVAIL_VY        EQU 5792
RECR_NUMBUY_VY       EQU 6480
RECR_COST_VY         EQU 8144
RECR_COUNT_VY        EQU 6432
RECR_AVAIL_CX        EQU 383
RECR_NUMBUY_RX       EQU 452
RECR_TOTAL_CX        EQU 511
RECR_COUNT_CX        EQU 522
RECR_PT_CX           EQU 583
RECR_TOTGOLD_VX      EQU 7408
RECR_TOTGOLD_VY      EQU 7376
TownDwellingMap:                       ; [idx-1] → recruit idx (0..5); 255 = не жилище
                DEFB 255, 255, 255, 255, 255, 255, 255, 255, 1, 255, 255, 255, 4, 5, 0, 2, 3, 255, 255
RecruitNameTab:
                DW RecruitNameTab_0
                DW RecruitNameTab_1
                DW RecruitNameTab_2
                DW RecruitNameTab_3
                DW RecruitNameTab_4
                DW RecruitNameTab_5
RecruitNameTab_0: DEFB "Recruit Peasants", 0
RecruitNameTab_1: DEFB "Recruit Archers", 0
RecruitNameTab_2: DEFB "Recruit Pikemen", 0
RecruitNameTab_3: DEFB "Recruit Swordsmen", 0
RecruitNameTab_4: DEFB "Recruit Cavalries", 0
RecruitNameTab_5: DEFB "Recruit Paladins", 0
RecruitAvailTab:
                DW RecruitAvailTab_0
                DW RecruitAvailTab_1
                DW RecruitAvailTab_2
                DW RecruitAvailTab_3
                DW RecruitAvailTab_4
                DW RecruitAvailTab_5
RecruitAvailTab_0: DEFB "Available: 12", 0
RecruitAvailTab_1: DEFB "Available: 8", 0
RecruitAvailTab_2: DEFB "Available: 5", 0
RecruitAvailTab_3: DEFB "Available: 4", 0
RecruitAvailTab_4: DEFB "Available: 3", 0
RecruitAvailTab_5: DEFB "Available: 2", 0
RecruitCostTab:
                DW RecruitCostTab_0
                DW RecruitCostTab_1
                DW RecruitCostTab_2
                DW RecruitCostTab_3
                DW RecruitCostTab_4
                DW RecruitCostTab_5
RecruitCostTab_0: DEFB "Cost: 20 gold", 0
RecruitCostTab_1: DEFB "Cost: 150 gold", 0
RecruitCostTab_2: DEFB "Cost: 200 gold", 0
RecruitCostTab_3: DEFB "Cost: 250 gold", 0
RecruitCostTab_4: DEFB "Cost: 300 gold", 0
RecruitCostTab_5: DEFB "Cost: 600 gold", 0
RecruitCountTab:
                DW RecruitCountTab_0
                DW RecruitCountTab_1
                DW RecruitCountTab_2
                DW RecruitCountTab_3
                DW RecruitCountTab_4
                DW RecruitCountTab_5
RecruitCountTab_0: DEFB "12", 0
RecruitCountTab_1: DEFB "8", 0
RecruitCountTab_2: DEFB "5", 0
RecruitCountTab_3: DEFB "4", 0
RecruitCountTab_4: DEFB "3", 0
RecruitCountTab_5: DEFB "2", 0
RECRUIT_SPR_PAL_RAMG EQU #06CC00
Recruit_Mon_Begin_DL:                  ; пролог спрайта монстра: native (×1.6 пред-масштаб), палитра прозрачная idx0
                FT_BITMAP_TRANSFORM_A 256
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 256
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE RECRUIT_SPR_PAL_RAMG
                FT_BEGIN FT_BITMAPS
Recruit_Mon_Begin_DL_SIZE EQU $ - Recruit_Mon_Begin_DL
RecruitMonSprTab:                      ; [recruit idx] → спрайт монстра [lo,mid,hi,w,h]
                DEFB #00, #CE, #06, 57, 102
                DEFB #B8, #E4, #06, 54, 105
                DEFB #E0, #FA, #06, 68, 118
                DEFB #38, #1A, #07, 59, 113
                DEFB #44, #34, #07, 115, 155
                DEFB #E8, #79, #07, 78, 139
RecruitMonPosTab:                      ; [recruit idx] → позиция спрайта (vertex) [Xlo,Xhi,Ylo,Yhi]
                DEFB #30, #16, #F0, #0F
                DEFB #40, #16, #C0, #0F
                DEFB #D0, #15, #F0, #0E
                DEFB #20, #16, #40, #0F
                DEFB #60, #14, #A0, #0C
                DEFB #80, #15, #A0, #0D
RECRUIT_GOLD_RAMG    EQU #07A444
RecruitGoldRec:                        ; запись иконки золота [lo,mid,hi,w,h] для DrawSpriteEntry
                DEFB #44, #A4, #07, 108, 40
RECR_GOLD_VX         EQU 8560
RECR_GOLD_VY         EQU 4176
RECR_PT_VX           EQU 9328
RECR_PT_VY           EQU 4944
RecruitPerTroopTab:
                DW RecruitPerTroopTab_0
                DW RecruitPerTroopTab_1
                DW RecruitPerTroopTab_2
                DW RecruitPerTroopTab_3
                DW RecruitPerTroopTab_4
                DW RecruitPerTroopTab_5
RecruitPerTroopTab_0: DEFB "20", 0
RecruitPerTroopTab_1: DEFB "150", 0
RecruitPerTroopTab_2: DEFB "200", 0
RecruitPerTroopTab_3: DEFB "250", 0
RecruitPerTroopTab_4: DEFB "300", 0
RecruitPerTroopTab_5: DEFB "600", 0
RecruitAvailNum:                       ; [recruit idx] → доступно (DW), кламп счётчика
                DW 12
                DW 8
                DW 5
                DW 4
                DW 3
                DW 2
RecruitCostNum:                        ; [recruit idx] → цена-за-1 (DW), для total
                DW 20
                DW 150
                DW 200
                DW 250
                DW 300
                DW 600
RecruitNumBuy:  DEFB "Number to buy:", 0
RecruitAvailPfx: DEFB "Available: ", 0
START_GOLD           EQU 7500
GOLD_PANEL_CX        EQU 949
GOLD_PANEL_VX        EQU 14992
GOLD_PANEL_VY        EQU 10560
RecruitMonhTab:                        ; [recruit idx] → MONH-портрет ×1.6 [lo,mid,hi,w,h]
                DEFB #24, #B5, #07, 57, 102
                DEFB #DC, #CB, #07, 54, 105
                DEFB #04, #E2, #07, 68, 118
                DEFB #5C, #01, #08, 59, 113
                DEFB #68, #1B, #08, 115, 142
                DEFB #34, #5B, #08, 78, 139
ArmyMonhX:      DW 3920, 6176, 8416, 10672, 12928, 3920, 6176, 8416, 10672, 12928
ArmyMonhY:      DW 9088, 9088, 9088, 9088, 9088, 11632, 11632, 11632, 11632, 11632
ArmyCntX:       DW 306, 446, 587, 728, 869, 306, 446, 587, 728, 869
ArmyCntY:       DW 8768, 8768, 8768, 8768, 8768, 11296, 11296, 11296, 11296, 11296
HighlightDL_0:
                FT_BEGIN FT_RECTS
                FT_COLOR_RGB 255, 255, 0
                FT_COLOR_A 90
                FT_VERTEX2F 2864, 6704
                FT_VERTEX2F 4960, 9088
                FT_END
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
HighlightDL_0_SIZE EQU $ - HighlightDL_0
HighlightDL_1:
                FT_BEGIN FT_RECTS
                FT_COLOR_RGB 255, 255, 0
                FT_COLOR_A 90
                FT_VERTEX2F 5120, 6704
                FT_VERTEX2F 7216, 9088
                FT_END
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
HighlightDL_1_SIZE EQU $ - HighlightDL_1
HighlightDL_2:
                FT_BEGIN FT_RECTS
                FT_COLOR_RGB 255, 255, 0
                FT_COLOR_A 90
                FT_VERTEX2F 7376, 6704
                FT_VERTEX2F 9472, 9088
                FT_END
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
HighlightDL_2_SIZE EQU $ - HighlightDL_2
HighlightDL_3:
                FT_BEGIN FT_RECTS
                FT_COLOR_RGB 255, 255, 0
                FT_COLOR_A 90
                FT_VERTEX2F 9632, 6704
                FT_VERTEX2F 11728, 9088
                FT_END
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
HighlightDL_3_SIZE EQU $ - HighlightDL_3
HighlightDL_4:
                FT_BEGIN FT_RECTS
                FT_COLOR_RGB 255, 255, 0
                FT_COLOR_A 90
                FT_VERTEX2F 11872, 6704
                FT_VERTEX2F 13968, 9088
                FT_END
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
HighlightDL_4_SIZE EQU $ - HighlightDL_4
HighlightDL_5:
                FT_BEGIN FT_RECTS
                FT_COLOR_RGB 255, 255, 0
                FT_COLOR_A 90
                FT_VERTEX2F 2864, 9248
                FT_VERTEX2F 4960, 11632
                FT_END
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
HighlightDL_5_SIZE EQU $ - HighlightDL_5
HighlightDL_6:
                FT_BEGIN FT_RECTS
                FT_COLOR_RGB 255, 255, 0
                FT_COLOR_A 90
                FT_VERTEX2F 5120, 9248
                FT_VERTEX2F 7216, 11632
                FT_END
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
HighlightDL_6_SIZE EQU $ - HighlightDL_6
HighlightDL_7:
                FT_BEGIN FT_RECTS
                FT_COLOR_RGB 255, 255, 0
                FT_COLOR_A 90
                FT_VERTEX2F 7376, 9248
                FT_VERTEX2F 9472, 11632
                FT_END
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
HighlightDL_7_SIZE EQU $ - HighlightDL_7
HighlightDL_8:
                FT_BEGIN FT_RECTS
                FT_COLOR_RGB 255, 255, 0
                FT_COLOR_A 90
                FT_VERTEX2F 9632, 9248
                FT_VERTEX2F 11728, 11632
                FT_END
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
HighlightDL_8_SIZE EQU $ - HighlightDL_8
HighlightDL_9:
                FT_BEGIN FT_RECTS
                FT_COLOR_RGB 255, 255, 0
                FT_COLOR_A 90
                FT_VERTEX2F 11872, 9248
                FT_VERTEX2F 13968, 11632
                FT_END
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
HighlightDL_9_SIZE EQU $ - HighlightDL_9
HighlightDLTab:                        ; [slot] → DW addr, DW size
                DW HighlightDL_0, HighlightDL_0_SIZE
                DW HighlightDL_1, HighlightDL_1_SIZE
                DW HighlightDL_2, HighlightDL_2_SIZE
                DW HighlightDL_3, HighlightDL_3_SIZE
                DW HighlightDL_4, HighlightDL_4_SIZE
                DW HighlightDL_5, HighlightDL_5_SIZE
                DW HighlightDL_6, HighlightDL_6_SIZE
                DW HighlightDL_7, HighlightDL_7_SIZE
                DW HighlightDL_8, HighlightDL_8_SIZE
                DW HighlightDL_9, HighlightDL_9_SIZE
ARMY_PLATE_RAMG      EQU #0D3858
ArmyPlateDL_0:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE ARMY_PLATE_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 82, 93
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 131, 149
                FT_VERTEX2F 2867, 6707
                FT_END
ArmyPlateDL_0_SIZE EQU $ - ArmyPlateDL_0
ArmyPlateDL_1:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE ARMY_PLATE_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 82, 93
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 131, 149
                FT_VERTEX2F 5120, 6707
                FT_END
ArmyPlateDL_1_SIZE EQU $ - ArmyPlateDL_1
ArmyPlateDL_2:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE ARMY_PLATE_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 82, 93
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 131, 149
                FT_VERTEX2F 7373, 6707
                FT_END
ArmyPlateDL_2_SIZE EQU $ - ArmyPlateDL_2
ArmyPlateDL_3:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE ARMY_PLATE_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 82, 93
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 131, 149
                FT_VERTEX2F 9626, 6707
                FT_END
ArmyPlateDL_3_SIZE EQU $ - ArmyPlateDL_3
ArmyPlateDL_4:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE ARMY_PLATE_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 82, 93
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 131, 149
                FT_VERTEX2F 11878, 6707
                FT_END
ArmyPlateDL_4_SIZE EQU $ - ArmyPlateDL_4
ArmyPlateDL_5:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE ARMY_PLATE_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 82, 93
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 131, 149
                FT_VERTEX2F 2867, 9241
                FT_END
ArmyPlateDL_5_SIZE EQU $ - ArmyPlateDL_5
ArmyPlateDL_6:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE ARMY_PLATE_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 82, 93
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 131, 149
                FT_VERTEX2F 5120, 9241
                FT_END
ArmyPlateDL_6_SIZE EQU $ - ArmyPlateDL_6
ArmyPlateDL_7:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE ARMY_PLATE_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 82, 93
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 131, 149
                FT_VERTEX2F 7373, 9241
                FT_END
ArmyPlateDL_7_SIZE EQU $ - ArmyPlateDL_7
ArmyPlateDL_8:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE ARMY_PLATE_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 82, 93
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 131, 149
                FT_VERTEX2F 9626, 9241
                FT_END
ArmyPlateDL_8_SIZE EQU $ - ArmyPlateDL_8
ArmyPlateDL_9:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_B 0
                FT_BITMAP_TRANSFORM_C 0
                FT_BITMAP_TRANSFORM_D 0
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_F 0
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_PALETTE_SOURCE TOWN_PAL_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE ARMY_PLATE_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, 82, 93
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 131, 149
                FT_VERTEX2F 11878, 9241
                FT_END
ArmyPlateDL_9_SIZE EQU $ - ArmyPlateDL_9
ArmyPlateDLTab:                        ; [slot] → DW addr, DW size
                DW ArmyPlateDL_0, ArmyPlateDL_0_SIZE
                DW ArmyPlateDL_1, ArmyPlateDL_1_SIZE
                DW ArmyPlateDL_2, ArmyPlateDL_2_SIZE
                DW ArmyPlateDL_3, ArmyPlateDL_3_SIZE
                DW ArmyPlateDL_4, ArmyPlateDL_4_SIZE
                DW ArmyPlateDL_5, ArmyPlateDL_5_SIZE
                DW ArmyPlateDL_6, ArmyPlateDL_6_SIZE
                DW ArmyPlateDL_7, ArmyPlateDL_7_SIZE
                DW ArmyPlateDL_8, ArmyPlateDL_8_SIZE
                DW ArmyPlateDL_9, ArmyPlateDL_9_SIZE

                endif