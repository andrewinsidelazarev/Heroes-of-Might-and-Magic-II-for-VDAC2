; Сгенерировано Source/Tools/viewport_pack.py

OBJECT_ATLAS_RAMG       EQU #079000
OBJECT_PALETTE_RAMG     EQU #079000
OBJECT_OPAQUE_PALETTE_RAMG EQU #079200
OBJECT_PALETTE_SIZE     EQU 512
OBJECT_OPAQUE_PALETTE_SIZE EQU 512
OBJECT_ATLAS_PAGE_BASE  EQU #07
OBJECT_ATLAS_PAGE_COUNT EQU 24
OBJECT_ATLAS_SIZE       EQU 390762
HERO_SPRITE_RAMG        EQU #0B3E0C
HERO_SPRITE_W           EQU 32
HERO_SPRITE_H           EQU 50
HERO_SPRITE_OX          EQU 0
HERO_SPRITE_OY          EQU 0
CURSOR_SPRITE_RAMG      EQU #0B4A8C
CURSOR_SPRITE_W         EQU 15
CURSOR_SPRITE_H         EQU 21
CURSOR_SPRITE_OX        EQU 0
CURSOR_SPRITE_OY        EQU 0
CURSOR_SPRITE_STRIDE    EQU 30
CURSOR_SPRITE_SIZE_W    EQU 24
CURSOR_SPRITE_SIZE_H    EQU 34
CURSOR_SPRITE_COUNT     EQU 9
CURSOR_POINTER_INDEX    EQU 0
CURSOR_MOVE_BASE_INDEX  EQU 1
CURSOR_TABLE_ENTRY_SIZE EQU 12
UI_BORDER_W             EQU 640
UI_BORDER_H             EQU 480
UI_RADAR_RAMG           EQU #0CCAF0
UI_RADAR_PALETTE_RAMG   EQU #0D1BF0
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
                DEFB #0B, #8C, #4A, 21, 30, 24, 34, 0
                DEFW #0000
                DEFW #0000
                DEFB #0B, #04, #4D, 25, 60, 48, 40, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0B, #E0, #52, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0B, #C8, #59, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0B, #B0, #60, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0B, #98, #67, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0B, #80, #6E, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0B, #68, #75, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0B, #50, #7C, 26, 76, 61, 42, 0
                DEFW #FFF1
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
                DEFB #08, #A6, #0C, 39, 23
                DEFB #8C, #A9, #0C, 37, 30
                DEFB #E4, #AD, #0C, 39, 25
                DEFB #B4, #B1, #0C, 39, 26
                DEFB #AC, #B5, #0C, 39, 32
                DEFB #8C, #BA, #0C, 36, 27
                DEFB #58, #BE, #0C, 68, 25
DigitTable:
                DEFB #FC, #C4, #0C, 5, 10
                DEFB #30, #C5, #0C, 3, 10
                DEFB #50, #C5, #0C, 5, 10
                DEFB #84, #C5, #0C, 5, 10
                DEFB #B8, #C5, #0C, 5, 10
                DEFB #EC, #C5, #0C, 5, 10
                DEFB #20, #C6, #0C, 5, 10
                DEFB #54, #C6, #0C, 5, 10
                DEFB #88, #C6, #0C, 5, 10
                DEFB #BC, #C6, #0C, 5, 10
RESOURCE_PANEL_RAMG     EQU #0CC6F0

AdventureUI_DL:
                FT_SCISSOR_XY 0, 0
                FT_SCISSOR_SIZE 1024, 768
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
                FT_BITMAP_HANDLE 3
                FT_CELL 0
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_C 0
                FT_VERTEX_TRANSLATE_X 0
                FT_VERTEX_TRANSLATE_Y 0
                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA
                FT_PALETTE_SOURCE OBJECT_OPAQUE_PALETTE_RAMG
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0B8408
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 12288, 4506
                FT_BITMAP_SOURCE #0B8D08
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 12288, 5325
                FT_BITMAP_SOURCE #0B8D08
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 12288, 6144
                FT_BITMAP_SOURCE #0B9608
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 12288, 6963
                FT_BITMAP_SOURCE #0B8408
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 14131, 4506
                FT_BITMAP_SOURCE #0B8D08
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 14131, 5325
                FT_BITMAP_SOURCE #0B8D08
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 14131, 6144
                FT_BITMAP_SOURCE #0B9608
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 14131, 6963
                FT_BITMAP_SOURCE #0B9F08
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 72
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 231, 116
                FT_VERTEX2F 12288, 10035
                FT_END
                FT_PALETTE_SOURCE OBJECT_PALETTE_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE #0C7D88
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 8192
                FT_BITMAP_SOURCE #0C8298
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 8192
                FT_BITMAP_SOURCE #0C87A8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 8192
                FT_BITMAP_SOURCE #0C8CB8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 15053, 8192
                FT_BITMAP_SOURCE #0C91C8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 9114
                FT_BITMAP_SOURCE #0C96D8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 9114
                FT_BITMAP_SOURCE #0C9BE8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 9114
                FT_BITMAP_SOURCE #0CA0F8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 15053, 9114
                FT_END
                FT_BLEND_FUNC FT_ONE, FT_ZERO
                FT_PALETTE_SOURCE UI_RADAR_PALETTE_RAMG
                FT_BITMAP_SOURCE #0CCAF0
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
                FT_BITMAP_SOURCE #0BC788
                FT_BITMAP_LAYOUT FT_PALETTED4444, 193, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 309, 26
                FT_VERTEX2F 0, 0
                FT_BITMAP_SOURCE #0BD398
                FT_BITMAP_LAYOUT FT_PALETTED4444, 6, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 10, 26
                FT_VERTEX2F 4941, 0
                FT_BITMAP_SOURCE #0BD3F8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 24, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 39, 26
                FT_VERTEX2F 5094, 0
                FT_BITMAP_SOURCE #0BD578
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 26
                FT_VERTEX2F 5709, 0
                FT_BITMAP_SOURCE #0BD778
                FT_BITMAP_LAYOUT FT_PALETTED4444, 25, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 26
                FT_VERTEX2F 6528, 0
                FT_BITMAP_SOURCE #0BD908
                FT_BITMAP_LAYOUT FT_PALETTED4444, 6, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 10, 26
                FT_VERTEX2F 7168, 0
                FT_BITMAP_SOURCE #0BD968
                FT_BITMAP_LAYOUT FT_PALETTED4444, 319, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 511, 26
                FT_VERTEX2F 7322, 0
                FT_BITMAP_SOURCE #0BED58
                FT_BITMAP_LAYOUT FT_PALETTED4444, 35, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 56, 26
                FT_VERTEX2F 15488, 0
                FT_BITMAP_SOURCE #0BEF88
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 239
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 383
                FT_VERTEX2F 0, 410
                FT_BITMAP_SOURCE #0BFE78
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 0, 6528
                FT_BITMAP_SOURCE #0C0078
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 125
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 200
                FT_VERTEX2F 0, 7347
                FT_BITMAP_SOURCE #0C0848
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 4
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 7
                FT_VERTEX2F 0, 10547
                FT_BITMAP_SOURCE #0C0888
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 48
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 77
                FT_VERTEX2F 0, 10650
                FT_BITMAP_SOURCE #0C0B88
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 239
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 383
                FT_VERTEX2F 11878, 410
                FT_BITMAP_SOURCE #0C1A78
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 11878, 6528
                FT_BITMAP_SOURCE #0C1C78
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 50
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 80
                FT_VERTEX2F 11878, 7347
                FT_BITMAP_SOURCE #0C1F98
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 11878, 8627
                FT_BITMAP_SOURCE #0C2198
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 43
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 69
                FT_VERTEX2F 11878, 9446
                FT_BITMAP_SOURCE #0C2448
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 8
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 13
                FT_VERTEX2F 11878, 10547
                FT_BITMAP_SOURCE #0C24C8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 44
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 71
                FT_VERTEX2F 11878, 10752
                FT_BITMAP_SOURCE #0C2788
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 239
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 383
                FT_VERTEX2F 15974, 410
                FT_BITMAP_SOURCE #0C3678
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 15974, 6528
                FT_BITMAP_SOURCE #0C3878
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 50
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 80
                FT_VERTEX2F 15974, 7347
                FT_BITMAP_SOURCE #0C3B98
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 15974, 8627
                FT_BITMAP_SOURCE #0C3D98
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 43
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 69
                FT_VERTEX2F 15974, 9446
                FT_BITMAP_SOURCE #0C4048
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 4
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 7
                FT_VERTEX2F 15974, 10547
                FT_BITMAP_SOURCE #0C4088
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 48
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 77
                FT_VERTEX2F 15974, 10650
                FT_BITMAP_SOURCE #0C4388
                FT_BITMAP_LAYOUT FT_PALETTED4444, 193, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 309, 26
                FT_VERTEX2F 0, 11878
                FT_BITMAP_SOURCE #0C4F98
                FT_BITMAP_LAYOUT FT_PALETTED4444, 6, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 10, 26
                FT_VERTEX2F 4941, 11878
                FT_BITMAP_SOURCE #0C4FF8
                FT_BITMAP_LAYOUT FT_PALETTED4444, 24, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 39, 26
                FT_VERTEX2F 5094, 11878
                FT_BITMAP_SOURCE #0C5178
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 26
                FT_VERTEX2F 5709, 11878
                FT_BITMAP_SOURCE #0C5378
                FT_BITMAP_LAYOUT FT_PALETTED4444, 25, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 26
                FT_VERTEX2F 6528, 11878
                FT_BITMAP_SOURCE #0C5508
                FT_BITMAP_LAYOUT FT_PALETTED4444, 6, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 10, 26
                FT_VERTEX2F 7168, 11878
                FT_BITMAP_SOURCE #0C5568
                FT_BITMAP_LAYOUT FT_PALETTED4444, 319, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 511, 26
                FT_VERTEX2F 7322, 11878
                FT_BITMAP_SOURCE #0C6958
                FT_BITMAP_LAYOUT FT_PALETTED4444, 35, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 56, 26
                FT_VERTEX2F 15488, 11878
                FT_BITMAP_SOURCE #0C6B88
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 231, 26
                FT_VERTEX2F 12288, 4096
                FT_BITMAP_SOURCE #0C7488
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 231, 26
                FT_VERTEX2F 12288, 7782
                FT_END
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
AdventureUI_DL_SIZE EQU $ - AdventureUI_DL

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
                LD   BC, 13930
                CALL FT.WriteMem
.RestorePage    EQU $+1
                LD   A, #00
                SetPage3_A
                RET
