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
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_C 0
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
TOWN_PAYLOAD_BYTES   EQU 307712
TOWN_PAYLOAD_SECTORS EQU 601
TOWN_BODY_SECTOR     EQU 1
TownPakName:         DEFB "HMM2TOWN.PAK", 0

                endif