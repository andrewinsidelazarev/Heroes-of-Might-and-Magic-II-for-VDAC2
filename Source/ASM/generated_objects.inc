; Сгенерировано Source/Tools/viewport_pack.py

OBJECT_ATLAS_RAMG       EQU #079000
OBJECT_PALETTE_RAMG     EQU #079000
OBJECT_OPAQUE_PALETTE_RAMG EQU #079200
OBJECT_PALETTE_SIZE     EQU 512
OBJECT_OPAQUE_PALETTE_SIZE EQU 512
OBJECT_ATLAS_PAGE_BASE  EQU #07
OBJECT_ATLAS_PAGE_COUNT EQU 24
OBJECT_ATLAS_SIZE       EQU 386414
HERO_SPRITE_RAMG        EQU #0B3E0C
HERO_SPRITE_W           EQU 32
HERO_SPRITE_H           EQU 50
HERO_SPRITE_OX          EQU 0
HERO_SPRITE_OY          EQU 0
CURSOR_SPRITE_RAMG      EQU #0E0000
CURSOR_SPRITE_W         EQU 15
CURSOR_SPRITE_H         EQU 21
CURSOR_SPRITE_OX        EQU 0
CURSOR_SPRITE_OY        EQU 0
CURSOR_SPRITE_STRIDE    EQU 30
CURSOR_SPRITE_SIZE_W    EQU 24
CURSOR_SPRITE_SIZE_H    EQU 34
CURSOR_SPRITE_COUNT     EQU 17
CURSOR_POINTER_INDEX    EQU 0
CURSOR_MOVE_BASE_INDEX  EQU 1
CURSOR_SCROLL_BASE_INDEX EQU 9
CURSOR_TABLE_ENTRY_SIZE EQU 12
UI_BORDER_W             EQU 640
UI_BORDER_H             EQU 480
UI_RADAR_RAMG           EQU #0CB9F4
UI_RADAR_PALETTE_RAMG   EQU #0D0AF4
UI_RADAR_W              EQU 144
UI_RADAR_H              EQU 144
UI_RADAR_STRIDE         EQU 144
UI_RADAR_X              EQU 480
UI_RADAR_Y              EQU 16
MINIMAP_TILE_PX         EQU 4
MINIMAP_RECT_LOGICAL    EQU 56
UI_RADAR_X16            EQU 12288
UI_RADAR_Y16            EQU 410
UI_BUTTON_X             EQU 480
UI_BUTTON_Y             EQU 320
UI_BUTTON_W             EQU 36
UI_BUTTON_H             EQU 36
UI_BUTTON_COLS          EQU 4
UI_BUTTON_GRID_W        EQU 144
UI_BUTTON_GRID_H        EQU 72
UI_BUTTON_COUNT         EQU 8
UI_STATUS_X             EQU 480
UI_STATUS_Y             EQU 392
UI_STATUS_W             EQU 144
UI_STATUS_H             EQU 72
ROUTE_SPRITE_COUNT      EQU 145
ROUTE_PALETTE_RAMG      EQU OBJECT_PALETTE_RAMG
ROUTE_RED_PALETTE_RAMG  EQU #0B3C0C
ROUTE_TABLE_PAGE        EQU #8A
ROUTE_TABLE_ADDR        EQU #0000
ROUTE_TABLE_ENTRY_SIZE  EQU 12

CursorSpriteTable:
                DEFB #0E, #00, #00, 21, 30, 24, 34, 0
                DEFW #0000
                DEFW #0000
                DEFB #0E, #78, #02, 25, 60, 48, 40, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #54, #08, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #3C, #0F, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #24, #16, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #0C, #1D, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #F4, #23, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #DC, #2A, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #C4, #31, 26, 76, 61, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #7C, #39, 32, 16, 13, 52, 0
                DEFW #FFFC
                DEFW #FFF0
                DEFB #0E, #7C, #3B, 24, 48, 39, 39, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0E, #FC, #3F, 8, 64, 52, 13, 0
                DEFW #FFF0
                DEFW #FFFC
                DEFB #0E, #FC, #41, 24, 48, 39, 39, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0E, #7C, #46, 32, 16, 13, 52, 0
                DEFW #FFFC
                DEFW #FFF0
                DEFB #0E, #7C, #48, 24, 48, 39, 39, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0E, #FC, #4C, 8, 64, 52, 13, 0
                DEFW #FFF0
                DEFW #FFFC
                DEFB #0E, #FC, #4E, 24, 48, 39, 39, 0
                DEFW #FFF4
                DEFW #FFF4

MINIMAP_MAP_W           EQU 36
MINIMAP_MAP_H           EQU 36
MinimapTileColorTable:
                DEFB 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2
                DEFB 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 4, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 5
                DEFB 5, 5, 5, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 4, 4, 4, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
                DEFB 1, 1, 2, 5, 5, 5, 5, 5, 5, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 2, 4, 4, 2, 2, 1, 1, 1, 1, 1, 1, 1
                DEFB 1, 1, 1, 1, 1, 1, 2, 2, 5, 5, 5, 5, 5, 5, 2, 1, 1, 1, 2, 2, 4, 4, 2, 1, 2, 2, 2, 2, 1, 1, 2, 2
                DEFB 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 5, 5, 5, 5, 2, 1, 1, 1, 2, 4, 4, 4, 2, 2, 1, 1, 1, 1
                DEFB 2, 2, 2, 6, 6, 6, 6, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 5, 7, 2, 2, 1, 1, 1, 2, 4, 4, 4, 3, 2
                DEFB 1, 1, 1, 2, 2, 6, 6, 6, 8, 6, 6, 6, 6, 2, 2, 2, 6, 6, 6, 6, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 2, 4
                DEFB 4, 4, 4, 2, 1, 1, 1, 2, 6, 6, 8, 8, 8, 6, 6, 6, 6, 2, 2, 6, 6, 6, 6, 6, 6, 2, 2, 2, 1, 1, 1, 1
                DEFB 1, 1, 2, 2, 4, 4, 2, 2, 1, 1, 2, 2, 8, 8, 8, 6, 6, 6, 6, 6, 6, 6, 6, 6, 8, 8, 6, 8, 6, 6, 6, 2
                DEFB 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 2, 9, 9, 6, 6, 6, 6, 6, 8, 8, 8, 8, 8, 6, 6, 8, 8, 6
                DEFB 6, 6, 6, 6, 6, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 10, 10, 10, 10, 6, 6, 8, 8, 8, 8, 8, 8, 8
                DEFB 6, 6, 6, 6, 8, 8, 8, 8, 6, 6, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 10, 10, 10, 10, 9, 9, 9, 9, 8, 6
                DEFB 6, 6, 6, 6, 6, 6, 6, 6, 8, 6, 6, 8, 8, 6, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 10, 10, 10, 10, 9, 9
                DEFB 9, 9, 8, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 8, 8, 8, 6, 2, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 10, 10, 10
                DEFB 10, 10, 9, 9, 9, 9, 9, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 8, 6, 6, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 10
                DEFB 9, 9, 10, 10, 10, 10, 10, 10, 10, 9, 9, 8, 6, 6, 6, 6, 6, 6, 6, 8, 8, 8, 6, 6, 6, 2, 1, 1, 1, 1, 1, 1
                DEFB 1, 2, 2, 9, 9, 9, 10, 10, 10, 9, 10, 10, 10, 9, 8, 6, 6, 6, 6, 6, 6, 6, 8, 8, 8, 8, 8, 2, 2, 2, 1, 1
                DEFB 1, 1, 2, 2, 2, 2, 10, 9, 9, 9, 10, 10, 9, 9, 10, 10, 9, 9, 6, 6, 6, 6, 6, 6, 6, 6, 8, 8, 8, 6, 2, 2
                DEFB 1, 1, 1, 1, 1, 1, 2, 10, 10, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 9, 9, 9, 10, 8, 8, 6, 6, 8, 8, 6, 8, 8
                DEFB 6, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 10, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 8, 8, 8, 8, 8
                DEFB 8, 8, 6, 6, 6, 2, 2, 1, 1, 1, 1, 1, 2, 2, 10, 10, 10, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 8
                DEFB 8, 8, 8, 8, 8, 8, 6, 8, 6, 8, 2, 1, 1, 1, 1, 1, 2, 10, 10, 10, 10, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10
                DEFB 10, 9, 9, 9, 8, 8, 8, 8, 8, 6, 6, 6, 6, 8, 2, 1, 1, 1, 1, 1, 2, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10
                DEFB 10, 10, 10, 10, 9, 9, 9, 9, 8, 6, 6, 6, 6, 6, 6, 6, 6, 8, 2, 1, 1, 1, 1, 1, 2, 2, 10, 10, 10, 10, 10, 10
                DEFB 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 6, 6, 6, 6, 6, 6, 6, 6, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 10
                DEFB 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 10, 6, 6, 6, 6, 8, 8, 2, 2, 2, 1, 1, 1, 1, 1, 1
                DEFB 1, 2, 2, 10, 10, 10, 9, 9, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9, 10, 10, 10, 8, 8, 6, 8, 8, 2, 2, 1, 1, 1, 1
                DEFB 1, 1, 1, 1, 1, 2, 10, 10, 10, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 9, 9, 9, 10, 10, 9, 8, 8, 6, 6, 8, 2, 1
                DEFB 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 10, 10, 10, 9, 9, 9, 9, 9, 9, 10, 9, 9, 10, 10, 10, 10, 10, 10, 10, 8, 6, 6
                DEFB 6, 6, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 10, 10, 10, 9, 9, 9, 9, 9, 10, 10, 9, 9, 9, 10, 10, 10, 10
                DEFB 10, 6, 6, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 10, 10, 9, 9, 9, 9, 2, 2, 2, 10, 10, 9
                DEFB 9, 10, 10, 10, 10, 10, 2, 2, 1, 1, 1, 2, 2, 2, 10, 10, 2, 2, 1, 1, 1, 1, 1, 2, 2, 9, 9, 9, 9, 9, 2, 1
                DEFB 2, 2, 2, 10, 10, 9, 10, 10, 10, 10, 2, 1, 1, 1, 2, 2, 10, 10, 10, 10, 10, 2, 1, 1, 1, 1, 1, 1, 2, 10, 10, 9
                DEFB 9, 2, 2, 1, 1, 2, 2, 10, 10, 10, 10, 10, 10, 10, 2, 2, 2, 2, 2, 9, 9, 10, 10, 10, 10, 2, 1, 1, 1, 1, 1, 1
                DEFB 2, 2, 10, 10, 2, 2, 2, 2, 2, 2, 9, 10, 10, 10, 10, 10, 10, 10, 2, 2, 10, 9, 10, 10, 10, 10, 10, 10, 2, 2, 1, 1
                DEFB 1, 1, 1, 1, 1, 2, 2, 2, 2, 1, 2, 10, 10, 10, 10, 10, 9, 9, 10, 10, 10, 10, 10, 10, 10, 9, 9, 10, 10, 10, 10, 10
                DEFB 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 9, 9, 9, 9, 9, 9, 9, 10, 9, 9, 10, 10, 10, 10, 10, 10, 10
                DEFB 10, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 9, 9, 10, 9, 9, 2, 2, 2, 9, 9, 10, 10
                DEFB 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 1, 2
                DEFB 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1

RESOURCE_ICON_ENTRY     EQU 5
DIGIT_ENTRY             EQU 5
ResourceIconTable:
                DEFB #0C, #95, #0C, 39, 23
                DEFB #90, #98, #0C, 37, 30
                DEFB #E8, #9C, #0C, 39, 25
                DEFB #B8, #A0, #0C, 39, 26
                DEFB #B0, #A4, #0C, 39, 32
                DEFB #90, #A9, #0C, 36, 27
                DEFB #5C, #AD, #0C, 68, 25
DigitTable:
                DEFB #00, #B4, #0C, 5, 10
                DEFB #34, #B4, #0C, 3, 10
                DEFB #54, #B4, #0C, 5, 10
                DEFB #88, #B4, #0C, 5, 10
                DEFB #BC, #B4, #0C, 5, 10
                DEFB #F0, #B4, #0C, 5, 10
                DEFB #24, #B5, #0C, 5, 10
                DEFB #58, #B5, #0C, 5, 10
                DEFB #8C, #B5, #0C, 5, 10
                DEFB #C0, #B5, #0C, 5, 10
RESOURCE_PANEL_RAMG     EQU #0CB5F4

AdventureUI_DL:
                FT_SCISSOR_XY 0, 0
                FT_SCISSOR_SIZE 1024, 768
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
                FT_BITMAP_HANDLE 3
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
                FT_PALETTE_SOURCE OBJECT_OPAQUE_PALETTE_RAMG
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0B4A8C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 12288, 4506
                FT_BITMAP_SOURCE #0B538C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 12288, 5325
                FT_BITMAP_SOURCE #0B538C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 12288, 6144
                FT_BITMAP_SOURCE #0B5C8C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 12288, 6963
                FT_BITMAP_SOURCE #0B4A8C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 14131, 4506
                FT_BITMAP_SOURCE #0B538C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 14131, 5325
                FT_BITMAP_SOURCE #0B538C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 14131, 6144
                FT_BITMAP_SOURCE #0B5C8C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 14131, 6963
                FT_BITMAP_SOURCE #0B658C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 72
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 231, 116
                FT_VERTEX2F 12288, 10035
                FT_END
                FT_PALETTE_SOURCE OBJECT_PALETTE_RAMG
                FT_BEGIN FT_BITMAPS
                FT_END
                FT_BLEND_FUNC FT_ONE, FT_ZERO
                FT_PALETTE_SOURCE UI_RADAR_PALETTE_RAMG
                FT_BITMAP_SOURCE #0CB9F4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 144
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 231, 231
                FT_BEGIN FT_BITMAPS
                FT_VERTEX2F 12288, 410
                FT_END
                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA
                FT_PALETTE_SOURCE OBJECT_PALETTE_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_BITMAP_SOURCE #0B8E0C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 193, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 309, 26
                FT_VERTEX2F 0, 0
                FT_BITMAP_SOURCE #0B9A1C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 6, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 10, 26
                FT_VERTEX2F 4941, 0
                FT_BITMAP_SOURCE #0B9A7C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 24, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 39, 26
                FT_VERTEX2F 5094, 0
                FT_BITMAP_SOURCE #0B9BFC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 26
                FT_VERTEX2F 5709, 0
                FT_BITMAP_SOURCE #0B9DFC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 25, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 26
                FT_VERTEX2F 6528, 0
                FT_BITMAP_SOURCE #0B9F8C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 6, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 10, 26
                FT_VERTEX2F 7168, 0
                FT_BITMAP_SOURCE #0B9FEC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 319, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 511, 26
                FT_VERTEX2F 7322, 0
                FT_BITMAP_SOURCE #0BB3DC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 35, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 56, 26
                FT_VERTEX2F 15488, 0
                FT_BITMAP_SOURCE #0BB60C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 239
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 383
                FT_VERTEX2F 0, 410
                FT_BITMAP_SOURCE #0BC4FC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 0, 6528
                FT_BITMAP_SOURCE #0BC6FC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 125
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 200
                FT_VERTEX2F 0, 7347
                FT_BITMAP_SOURCE #0BCECC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 4
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 7
                FT_VERTEX2F 0, 10547
                FT_BITMAP_SOURCE #0BCF0C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 48
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 77
                FT_VERTEX2F 0, 10650
                FT_BITMAP_SOURCE #0BD20C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 239
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 383
                FT_VERTEX2F 11878, 410
                FT_BITMAP_SOURCE #0BE0FC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 11878, 6528
                FT_BITMAP_SOURCE #0BE2FC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 50
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 80
                FT_VERTEX2F 11878, 7347
                FT_BITMAP_SOURCE #0BE61C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 11878, 8627
                FT_BITMAP_SOURCE #0BE81C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 43
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 69
                FT_VERTEX2F 11878, 9446
                FT_BITMAP_SOURCE #0BEACC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 8
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 13
                FT_VERTEX2F 11878, 10547
                FT_BITMAP_SOURCE #0BEB4C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 44
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 71
                FT_VERTEX2F 11878, 10752
                FT_BITMAP_SOURCE #0BEE0C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 239
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 383
                FT_VERTEX2F 15974, 410
                FT_BITMAP_SOURCE #0BFCFC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 15974, 6528
                FT_BITMAP_SOURCE #0BFEFC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 50
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 80
                FT_VERTEX2F 15974, 7347
                FT_BITMAP_SOURCE #0C021C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 15974, 8627
                FT_BITMAP_SOURCE #0C041C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 43
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 69
                FT_VERTEX2F 15974, 9446
                FT_BITMAP_SOURCE #0C06CC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 4
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 7
                FT_VERTEX2F 15974, 10547
                FT_BITMAP_SOURCE #0C070C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 48
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 77
                FT_VERTEX2F 15974, 10650
                FT_BITMAP_SOURCE #0C0A0C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 193, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 309, 26
                FT_VERTEX2F 0, 11878
                FT_BITMAP_SOURCE #0C161C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 6, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 10, 26
                FT_VERTEX2F 4941, 11878
                FT_BITMAP_SOURCE #0C167C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 24, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 39, 26
                FT_VERTEX2F 5094, 11878
                FT_BITMAP_SOURCE #0C17FC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 26
                FT_VERTEX2F 5709, 11878
                FT_BITMAP_SOURCE #0C19FC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 25, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 26
                FT_VERTEX2F 6528, 11878
                FT_BITMAP_SOURCE #0C1B8C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 6, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 10, 26
                FT_VERTEX2F 7168, 11878
                FT_BITMAP_SOURCE #0C1BEC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 319, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 511, 26
                FT_VERTEX2F 7322, 11878
                FT_BITMAP_SOURCE #0C2FDC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 35, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 56, 26
                FT_VERTEX2F 15488, 11878
                FT_BITMAP_SOURCE #0C320C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 231, 26
                FT_VERTEX2F 12288, 4096
                FT_BITMAP_SOURCE #0C3B0C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 231, 26
                FT_VERTEX2F 12288, 7782
                FT_END
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
AdventureUI_DL_SIZE EQU $ - AdventureUI_DL

@UI_BtnNormalTab:
                DEFW UI_BtnNormal_0_DL
                DEFW UI_BtnNormal_1_DL
                DEFW UI_BtnNormal_2_DL
                DEFW UI_BtnNormal_3_DL
                DEFW UI_BtnNormal_4_DL
                DEFW UI_BtnNormal_5_DL
                DEFW UI_BtnNormal_6_DL
                DEFW UI_BtnNormal_7_DL
UI_BtnNormal_0_DL:
                FT_BITMAP_SOURCE #0C440C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 8192
UI_BtnNormal_1_DL:
                FT_BITMAP_SOURCE #0C4E2C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 8192
UI_BtnNormal_2_DL:
                FT_BITMAP_SOURCE #0C584C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 8192
UI_BtnNormal_3_DL:
                FT_BITMAP_SOURCE #0C626C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 15053, 8192
UI_BtnNormal_4_DL:
                FT_BITMAP_SOURCE #0C6C8C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 9114
UI_BtnNormal_5_DL:
                FT_BITMAP_SOURCE #0C76AC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 9114
UI_BtnNormal_6_DL:
                FT_BITMAP_SOURCE #0C80CC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 9114
UI_BtnNormal_7_DL:
                FT_BITMAP_SOURCE #0C8AEC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 15053, 9114
@UI_BtnNormal_DL_SIZE EQU UI_BtnNormal_1_DL - UI_BtnNormal_0_DL
@UI_BtnPressedTab:
                DEFW UI_BtnPressed_0_DL
                DEFW UI_BtnPressed_1_DL
                DEFW UI_BtnPressed_2_DL
                DEFW UI_BtnPressed_3_DL
                DEFW UI_BtnPressed_4_DL
                DEFW UI_BtnPressed_5_DL
                DEFW UI_BtnPressed_6_DL
                DEFW UI_BtnPressed_7_DL
UI_BtnPressed_0_DL:
                FT_BITMAP_SOURCE #0C491C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 8192
UI_BtnPressed_1_DL:
                FT_BITMAP_SOURCE #0C533C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 8192
UI_BtnPressed_2_DL:
                FT_BITMAP_SOURCE #0C5D5C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 8192
UI_BtnPressed_3_DL:
                FT_BITMAP_SOURCE #0C677C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 15053, 8192
UI_BtnPressed_4_DL:
                FT_BITMAP_SOURCE #0C719C
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 9114
UI_BtnPressed_5_DL:
                FT_BITMAP_SOURCE #0C7BBC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 9114
UI_BtnPressed_6_DL:
                FT_BITMAP_SOURCE #0C85DC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 9114
UI_BtnPressed_7_DL:
                FT_BITMAP_SOURCE #0C8FFC
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 15053, 9114
@UI_BtnPressed_DL_SIZE EQU UI_BtnPressed_1_DL - UI_BtnPressed_0_DL

Objects_Upload:
                GetPage3
                LD   (.RestorePage), A
                SetPage3 #72
                LD   HL, #C000
                LD   A, #07
                LD   DE, #9000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #73
                LD   HL, #C000
                LD   A, #07
                LD   DE, #D000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #74
                LD   HL, #C000
                LD   A, #08
                LD   DE, #1000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #75
                LD   HL, #C000
                LD   A, #08
                LD   DE, #5000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #76
                LD   HL, #C000
                LD   A, #08
                LD   DE, #9000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #77
                LD   HL, #C000
                LD   A, #08
                LD   DE, #D000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #78
                LD   HL, #C000
                LD   A, #09
                LD   DE, #1000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #79
                LD   HL, #C000
                LD   A, #09
                LD   DE, #5000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #7A
                LD   HL, #C000
                LD   A, #09
                LD   DE, #9000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #7B
                LD   HL, #C000
                LD   A, #09
                LD   DE, #D000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #7C
                LD   HL, #C000
                LD   A, #0A
                LD   DE, #1000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #7D
                LD   HL, #C000
                LD   A, #0A
                LD   DE, #5000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #7E
                LD   HL, #C000
                LD   A, #0A
                LD   DE, #9000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #7F
                LD   HL, #C000
                LD   A, #0A
                LD   DE, #D000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #80
                LD   HL, #C000
                LD   A, #0B
                LD   DE, #1000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #81
                LD   HL, #C000
                LD   A, #0B
                LD   DE, #5000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #82
                LD   HL, #C000
                LD   A, #0B
                LD   DE, #9000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #83
                LD   HL, #C000
                LD   A, #0B
                LD   DE, #D000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #84
                LD   HL, #C000
                LD   A, #0C
                LD   DE, #1000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #85
                LD   HL, #C000
                LD   A, #0C
                LD   DE, #5000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #86
                LD   HL, #C000
                LD   A, #0C
                LD   DE, #9000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #87
                LD   HL, #C000
                LD   A, #0C
                LD   DE, #D000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #88
                LD   HL, #C000
                LD   A, #0D
                LD   DE, #1000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #89
                LD   HL, #C000
                LD   A, #0D
                LD   DE, #5000
                LD   BC, 9582
                CALL FT.WriteMem
.RestorePage    EQU $+1
                LD   A, #00
                SetPage3_A
                RET

Cursor_GlobalUpload:
                GetPage3
                LD   (.CurRestore), A
                SetPage3 #A2
                LD   HL, #C000
                LD   A, #0E
                LD   DE, #0000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #A3
                LD   HL, #C000
                LD   A, #0E
                LD   DE, #4000
                LD   BC, 4988
                CALL FT.WriteMem
.CurRestore     EQU $+1
                LD   A, #00
                SetPage3_A
                RET
