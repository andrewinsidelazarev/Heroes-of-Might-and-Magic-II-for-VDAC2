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
                FT_END
Town_DL_SIZE EQU $ - Town_DL

TOWN_RAMG_BASE       EQU #000000
TOWN_PAYLOAD_BYTES   EQU 481268
TOWN_PAYLOAD_SECTORS EQU 940
TOWN_BODY_SECTOR     EQU 1
TownPakName:         DEFB "HMM2TOWN.PAK", 0

TOWN_HIT_BLK         EQU 8
TOWN_HIT_W           EQU 80
TOWN_HIT_H           EQU 32
TOWN_NAME_PAL_RAMG   EQU #04B200
TOWN_NAME_COUNT      EQU 19
TownHitMap:                            ; блок 8x8 → индекс здания (1-based; 0=фон), Z80-читаемая
                DEFB 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 0, 5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 6, 6, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 0, 5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 6, 6, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 0, 5, 5, 5, 5, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 6, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 0, 5, 5, 5, 5, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 0, 6, 6, 6, 6, 6, 6, 6, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 0, 5, 5, 5, 5, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 6, 6, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 0, 5, 5, 5, 5, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 6, 6, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 0, 0, 0, 0, 0
                DEFB 3, 5, 5, 5, 5, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 3, 3, 6, 6, 6, 6, 6, 6, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 0, 0, 0, 0
                DEFB 3, 5, 5, 5, 5, 5, 5, 5, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 0, 0
                DEFB 2, 5, 5, 5, 5, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 0, 0
                DEFB 2, 5, 5, 5, 5, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 11, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 0, 0, 0
                DEFB 2, 5, 5, 5, 5, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 4, 4, 4, 4, 4, 4, 1, 11, 11, 11, 11, 11, 11, 11, 11, 11, 0, 0, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14
                DEFB 2, 5, 5, 5, 5, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 4, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 0, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14
                DEFB 2, 5, 5, 5, 5, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 4, 11, 4, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14
                DEFB 10, 10, 10, 10, 5, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8, 8, 7, 7, 4, 4, 4, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14
                DEFB 10, 10, 10, 10, 10, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8, 8, 7, 7, 8, 8, 8, 8, 8, 8, 7, 8, 8, 8, 7, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14
                DEFB 10, 10, 10, 10, 10, 10, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 9, 9, 9, 7, 9, 9, 7, 7, 7, 8, 8, 7, 7, 8, 8, 8, 8, 8, 8, 7, 8, 8, 8, 8, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14
                DEFB 10, 10, 10, 10, 10, 10, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 9, 7, 9, 9, 9, 9, 9, 9, 9, 15, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14
                DEFB 10, 10, 10, 10, 10, 10, 7, 7, 7, 7, 7, 7, 7, 7, 10, 10, 7, 9, 9, 9, 9, 9, 9, 9, 9, 15, 15, 15, 15, 15, 16, 16, 8, 8, 8, 8, 8, 16, 16, 16, 11, 17, 17, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14
                DEFB 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 15, 15, 15, 15, 15, 16, 16, 14, 14, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 12, 12, 12, 12, 12, 12, 12, 12, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14
                DEFB 10, 10, 10, 10, 10, 10, 13, 13, 13, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 14, 9, 14, 14, 14, 15, 15, 15, 15, 15, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 12, 12, 12, 12, 12, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14
                DEFB 13, 0, 10, 10, 10, 10, 13, 13, 13, 10, 10, 10, 10, 0, 0, 0, 0, 0, 13, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14
                DEFB 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 0, 0, 0, 0, 0, 0, 13, 13, 13, 13, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 14, 14, 14, 14, 14, 14, 14, 14, 19, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 0, 0, 0, 0
                DEFB 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 14, 15, 15, 15, 15, 15, 15, 15, 16, 16, 15, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 14, 14, 14, 19, 19, 19, 19, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 18, 15, 15, 18, 15, 15, 15, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 0, 0, 19, 19, 19, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 18, 18, 18, 15, 15, 18, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 0, 0, 19, 19, 19, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 18, 18, 18, 18, 18, 18, 18, 16, 16, 16, 16, 16, 16, 16, 16, 16, 0, 0, 0, 0, 0, 0, 0, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 0, 19, 19, 19, 19, 19, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 18, 18, 18, 18, 18, 18, 18, 18, 18, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 0, 0, 0, 0, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 0, 0, 0, 19, 19, 19, 19, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                DEFB 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 18, 18, 18, 18, 18, 18, 18, 18, 18, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 0, 0, 0, 0, 0, 0, 0, 0, 19, 19, 19, 19, 19, 19, 19, 19, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
TownBuildingNameTab:                   ; [idx-1] → имя SMALFONT ×1.6 [lo,mid,hi,w,h]
                DEFB #00, #B4, #04, 34, 8
                DEFB #10, #B5, #04, 35, 8
                DEFB #28, #B6, #04, 81, 8
                DEFB #B0, #B8, #04, 111, 10
                DEFB #08, #BD, #04, 35, 8
                DEFB #20, #BE, #04, 35, 8
                DEFB #38, #BF, #04, 29, 8
                DEFB #20, #C0, #04, 74, 10
                DEFB #04, #C3, #04, 92, 10
                DEFB #9C, #C6, #04, 81, 8
                DEFB #24, #C9, #04, 44, 8
                DEFB #84, #CA, #04, 66, 10
                DEFB #18, #CD, #04, 92, 10
                DEFB #B0, #D0, #04, 58, 8
                DEFB #80, #D2, #04, 81, 8
                DEFB #08, #D5, #04, 67, 8
                DEFB #20, #D7, #04, 49, 10
                DEFB #0C, #D9, #04, 27, 8
                DEFB #E4, #D9, #04, 38, 8
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
                DEFB #14, #DB, #04, 4, 3
                DEFB #20, #DB, #04, 2, 10
                DEFB #34, #DB, #04, 4, 6
                DEFB #4C, #DB, #04, 2, 10
                DEFB #60, #DB, #04, 6, 12
                DEFB #A8, #DB, #04, 8, 10
                DEFB #F8, #DB, #04, 7, 10
                DEFB #40, #DC, #04, 2, 6
                DEFB #4C, #DC, #04, 4, 11
                DEFB #78, #DC, #04, 4, 11
                DEFB #A4, #DC, #04, 2, 10
                DEFB #B8, #DC, #04, 6, 9
                DEFB #F0, #DC, #04, 3, 12
                DEFB #14, #DD, #04, 6, 7
                DEFB #40, #DD, #04, 2, 10
                DEFB #54, #DD, #04, 5, 11
                DEFB #8C, #DD, #04, 5, 10
                DEFB #C0, #DD, #04, 3, 10
                DEFB #E0, #DD, #04, 5, 10
                DEFB #14, #DE, #04, 5, 10
                DEFB #48, #DE, #04, 5, 10
                DEFB #7C, #DE, #04, 5, 10
                DEFB #B0, #DE, #04, 5, 10
                DEFB #E4, #DE, #04, 5, 10
                DEFB #18, #DF, #04, 5, 10
                DEFB #4C, #DF, #04, 5, 10
                DEFB #80, #DF, #04, 2, 10
                DEFB #94, #DF, #04, 3, 12
                DEFB #B8, #DF, #04, 2, 10
                DEFB #CC, #DF, #04, 6, 8
                DEFB #FC, #DF, #04, 2, 10
                DEFB #10, #E0, #04, 6, 10
                DEFB #4C, #E0, #04, 2, 10
                DEFB #60, #E0, #04, 9, 10
                DEFB #BC, #E0, #04, 7, 10
                DEFB #04, #E1, #04, 7, 10
                DEFB #4C, #E1, #04, 8, 10
                DEFB #9C, #E1, #04, 8, 10
                DEFB #EC, #E1, #04, 8, 10
                DEFB #3C, #E2, #04, 8, 10
                DEFB #8C, #E2, #04, 9, 10
                DEFB #E8, #E2, #04, 4, 10
                DEFB #10, #E3, #04, 7, 10
                DEFB #58, #E3, #04, 9, 10
                DEFB #B4, #E3, #04, 8, 10
                DEFB #04, #E4, #04, 11, 10
                DEFB #74, #E4, #04, 10, 10
                DEFB #D8, #E4, #04, 8, 10
                DEFB #28, #E5, #04, 8, 10
                DEFB #78, #E5, #04, 8, 11
                DEFB #D0, #E5, #04, 9, 10
                DEFB #2C, #E6, #04, 7, 10
                DEFB #74, #E6, #04, 8, 10
                DEFB #C4, #E6, #04, 10, 10
                DEFB #28, #E7, #04, 10, 10
                DEFB #8C, #E7, #04, 13, 10
                DEFB #10, #E8, #04, 9, 10
                DEFB #6C, #E8, #04, 9, 10
                DEFB #C8, #E8, #04, 7, 10
                DEFB #10, #E9, #04, 4, 11
                DEFB #3C, #E9, #04, 2, 10
                DEFB #50, #E9, #04, 4, 11
                DEFB #7C, #E9, #04, 2, 10
                DEFB #90, #E9, #04, 6, 10
                DEFB #CC, #E9, #04, 2, 6
                DEFB #D8, #E9, #04, 7, 10
                DEFB #20, #EA, #04, 7, 10
                DEFB #68, #EA, #04, 6, 10
                DEFB #A4, #EA, #04, 7, 10
                DEFB #EC, #EA, #04, 6, 10
                DEFB #28, #EB, #04, 5, 10
                DEFB #5C, #EB, #04, 7, 12
                DEFB #B0, #EB, #04, 8, 10
                DEFB #00, #EC, #04, 4, 10
                DEFB #28, #EC, #04, 5, 12
                DEFB #64, #EC, #04, 8, 10
                DEFB #B4, #EC, #04, 4, 10
                DEFB #DC, #EC, #04, 12, 10
                DEFB #54, #ED, #04, 8, 10
                DEFB #A4, #ED, #04, 6, 10
                DEFB #E0, #ED, #04, 7, 12
                DEFB #34, #EE, #04, 7, 12
                DEFB #88, #EE, #04, 7, 10
                DEFB #D0, #EE, #04, 6, 10
                DEFB #0C, #EF, #04, 5, 10
                DEFB #40, #EF, #04, 8, 10
                DEFB #90, #EF, #04, 8, 10
                DEFB #E0, #EF, #04, 12, 10
                DEFB #58, #F0, #04, 7, 10
                DEFB #A0, #F0, #04, 8, 12
                DEFB #00, #F1, #04, 6, 10
                DEFB #3C, #F1, #04, 2, 10
                DEFB #50, #F1, #04, 2, 10
                DEFB #64, #F1, #04, 2, 10
                DEFB #78, #F1, #04, 2, 10
                DEFB #8C, #F1, #04, 2, 10
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
                DEFB "The Farm increases production of Peasants by 8 per week.", 0
                DEFB 0
TownDescBlk_1:
                DEFB "The Castle improves the town's defense and increases its income to", 0
                DEFB "1000 gold per day.", 0
                DEFB 0
TownDescBlk_2:
                DEFB "The Fortifications increase the toughness of the walls, increasing", 0
                DEFB "the number of turns it takes to knock them down.", 0
                DEFB 0
TownDescBlk_3:
                DEFB "The Captain's Quarters provides a captain to assist in the castle's", 0
                DEFB "defense when no hero is present.", 0
                DEFB 0
TownDescBlk_4:
                DEFB "The Left Turret provides extra firepower during castle combat.", 0
                DEFB 0
TownDescBlk_5:
                DEFB "The Right Turret provides extra firepower during castle combat.", 0
                DEFB 0
TownDescBlk_6:
                DEFB "The Moat slows and weakens attacking units. Any walking unit", 0
                DEFB "entering the moat must end its turn there and can only move", 0
                DEFB "within the moat one hex at a time. Any creature present in the", 0
                DEFB "moat will have its defense skill reduced by 3.", 0
                DEFB 0
TownDescBlk_7:
                DEFB "The Marketplace can be used to convert one type of resource into", 0
                DEFB "another. The more marketplaces you control, the better the", 0
                DEFB "exchange rate.", 0
                DEFB 0
TownDescBlk_8:
                DEFB "Recruit Archer.", 0
                DEFB 0
TownDescBlk_9:
                DEFB "The Thieves' Guild provides information on enemy players.", 0
                DEFB "Thieves' Guilds can also provide scouting information on enemy", 0
                DEFB "towns. Additional Guilds provide more information.", 0
                DEFB 0
TownDescBlk_10:
                DEFB "The Tavern increases morale for troops defending the castle.", 0
                DEFB 0
TownDescBlk_11:
                DEFB "The Mage Guild allows heroes to learn spells and replenish their", 0
                DEFB "spell points.", 0
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
                DEFB "The Well increases the growth rate of all dwellings by 2 creatures", 0
                DEFB "per week.", 0
                DEFB 0
TownDescBlk_18:
                DEFB "The Statue increases the town's income by 250 gold per day.", 0
                DEFB 0
Town_Info_Box_DL:                      ; рамка попапа (faithful Dialog::Message окно)
                FT_COLOR_RGB 176, 140, 92
                FT_COLOR_A 255
                FT_LINE_WIDTH 16
                FT_BEGIN FT_RECTS
                FT_VERTEX2F 4672, 4608
                FT_VERTEX2F 11712, 7552
                FT_COLOR_RGB 28, 20, 10
                FT_COLOR_A 244
                FT_VERTEX2F 4720, 4656
                FT_VERTEX2F 11664, 7504
                FT_END
                FT_COLOR_A 255
                FT_COLOR_RGB 255, 255, 255
Town_Info_Box_DL_SIZE EQU $ - Town_Info_Box_DL
TOWN_INFO_TITLE_Y    EQU 300 * 16
TOWN_INFO_LINE0_Y    EQU 322 * 16
TOWN_INFO_LINE_H     EQU 12 * 16

RECRUIT_WIN_RAMG     EQU #04F1A0
Recruit_Win_DL:                        ; окно найма RECRBKG ×1.6 по центру экрана
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
RECR_NAME_VY         EQU 2768
RECR_AVAIL_VY        EQU 6992
RECR_COST_VY         EQU 8448
RECR_COUNT_VY        EQU 6400
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
RECRUIT_SPR_PAL_RAMG EQU #066ED0
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
                DEFB #D0, #70, #06, 57, 102
                DEFB #88, #87, #06, 54, 105
                DEFB #B0, #9D, #06, 68, 118
                DEFB #08, #BD, #06, 59, 113
                DEFB #14, #D7, #06, 115, 155
                DEFB #B8, #1C, #07, 78, 139
RecruitMonPosTab:                      ; [recruit idx] → позиция спрайта (vertex) [Xlo,Xhi,Ylo,Yhi]
                DEFB #90, #14, #70, #0F
                DEFB #A0, #14, #40, #0F
                DEFB #30, #14, #70, #0E
                DEFB #80, #14, #C0, #0E
                DEFB #C0, #12, #20, #0C
                DEFB #E0, #13, #20, #0D
RECRUIT_GOLD_RAMG    EQU #074714
RecruitGoldRec:                        ; запись иконки золота [lo,mid,hi,w,h] для DrawSpriteEntry
                DEFB #14, #47, #07, 108, 40
RECR_GOLD_VX         EQU 8816
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
RecruitCostPfx: DEFB "Cost: ", 0
RecruitGoldSfx: DEFB " gold", 0
RecruitAvailPfx: DEFB "Available: ", 0
START_GOLD           EQU 7500

                endif