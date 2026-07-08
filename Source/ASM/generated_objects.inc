; Сгенерировано Source/Tools/viewport_pack.py

OBJECT_ATLAS_RAMG       EQU #079000
OBJECT_PALETTE_RAMG     EQU #079000
OBJECT_OPAQUE_PALETTE_RAMG EQU #079200
OBJECT_PALETTE_SIZE     EQU 512
OBJECT_OPAQUE_PALETTE_SIZE EQU 512
OBJECT_ATLAS_PAGE_BASE  EQU #07
OBJECT_ATLAS_PAGE_COUNT EQU 28
OBJECT_ATLAS_SIZE       EQU 449018
HERO_SPRITE_RAMG        EQU #0B273C
HERO_SPRITE_W           EQU 30
HERO_SPRITE_H           EQU 50
HERO_SPRITE_OX          EQU 0
HERO_SPRITE_OY          EQU 0
SORC_SPRITE_RAMG        EQU #0B32F4
SORC_SPRITE_W           EQU 32
SORC_SPRITE_H           EQU 50
SORC_SPRITE_OX          EQU 0
SORC_SPRITE_OY          EQU 0
CURSOR_SPRITE_RAMG      EQU #0E8000
CURSOR_SPRITE_W         EQU 15
CURSOR_SPRITE_H         EQU 21
CURSOR_SPRITE_OX        EQU 0
CURSOR_SPRITE_OY        EQU 0
CURSOR_SPRITE_STRIDE    EQU 30
CURSOR_SPRITE_SIZE_W    EQU 24
CURSOR_SPRITE_SIZE_H    EQU 34
CURSOR_SPRITE_COUNT     EQU 46
CURSOR_POINTER_INDEX    EQU 0
CURSOR_MOVE_BASE_INDEX  EQU 1
CURSOR_FIGHT_BASE_INDEX EQU 9
CURSOR_ACTION_BASE_INDEX EQU 17
CURSOR_HEROES_INDEX    EQU 25
CURSOR_CASTLE_INDEX    EQU 26
CURSOR_SCROLL_BASE_INDEX EQU 38
CURSOR_BATTLE_BASE_INDEX EQU 27
CURSOR_TABLE_ENTRY_SIZE EQU 12
UI_BORDER_W             EQU 640
UI_BORDER_H             EQU 480
UI_RADAR_RAMG           EQU #0DAE80
UI_RADAR_PALETTE_RAMG   EQU #0DFF80
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
ROUTE_RED_PALETTE_RAMG  EQU #0B253C
ROUTE_TABLE_PAGE        EQU #8E
ROUTE_TABLE_ADDR        EQU #0000
ROUTE_TABLE_ENTRY_SIZE  EQU 12

CursorSpriteTable:
                DEFB #0E, #00, #80, 21, 30, 24, 34, 0
                DEFW #0000
                DEFW #0000
                DEFB #0E, #78, #82, 25, 60, 48, 40, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #54, #88, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #3C, #8F, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #24, #96, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #0C, #9D, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #F4, #A3, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #DC, #AA, 26, 68, 55, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #C4, #B1, 26, 76, 61, 42, 0
                DEFW #FFF1
                DEFW #FFF4
                DEFB #0E, #7C, #B9, 24, 48, 39, 39, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0E, #FC, #BD, 25, 62, 50, 40, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0E, #0C, #C4, 25, 62, 50, 40, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0E, #1C, #CA, 25, 62, 50, 40, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0E, #2C, #D0, 25, 62, 50, 40, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0E, #3C, #D6, 25, 62, 50, 40, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0E, #4C, #DC, 25, 62, 50, 40, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0E, #5C, #E2, 25, 70, 56, 40, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0E, #34, #E9, 30, 60, 48, 48, 0
                DEFW #FFF1
                DEFW #FFF1
                DEFB #0E, #3C, #F0, 31, 60, 48, 50, 0
                DEFW #FFF1
                DEFW #FFF1
                DEFB #0E, #80, #F7, 31, 60, 48, 50, 0
                DEFW #FFF1
                DEFW #FFF1
                DEFB #0E, #C4, #FE, 31, 60, 48, 50, 0
                DEFW #FFF1
                DEFW #FFF1
                DEFB #0F, #08, #06, 31, 60, 48, 50, 0
                DEFW #FFF1
                DEFW #FFF1
                DEFB #0F, #4C, #0D, 31, 60, 48, 50, 0
                DEFW #FFF1
                DEFW #FFF1
                DEFB #0F, #90, #14, 31, 60, 48, 50, 0
                DEFW #FFF1
                DEFW #FFF1
                DEFB #0F, #D4, #1B, 31, 68, 55, 50, 0
                DEFW #FFF1
                DEFW #FFF1
                DEFB #0F, #10, #24, 20, 48, 39, 32, 0
                DEFW #FFF4
                DEFW #FFF6
                DEFB #0F, #D0, #27, 24, 48, 39, 39, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0F, #50, #2C, 20, 40, 32, 32, 0
                DEFW #FFF6
                DEFW #FFF6
                DEFB #0F, #70, #2F, 23, 36, 29, 37, 0
                DEFW #FFF7
                DEFW #FFF5
                DEFB #0F, #AC, #32, 24, 48, 39, 39, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0F, #2C, #37, 18, 22, 18, 29, 0
                DEFW #FFFB
                DEFW #FFF7
                DEFB #0F, #B8, #38, 13, 26, 21, 21, 0
                DEFW #FFFA
                DEFW #FFFA
                DEFB #0F, #0C, #3A, 22, 44, 36, 36, 0
                DEFW #FFF5
                DEFW #FFF5
                DEFB #0F, #D4, #3D, 14, 62, 50, 23, 0
                DEFW #FFF1
                DEFW #FFF9
                DEFB #0F, #38, #41, 22, 44, 36, 36, 0
                DEFW #FFF5
                DEFW #FFF5
                DEFB #0F, #00, #45, 22, 44, 36, 36, 0
                DEFW #FFF5
                DEFW #FFF5
                DEFB #0F, #C8, #48, 14, 62, 50, 23, 0
                DEFW #FFF1
                DEFW #FFF9
                DEFB #0F, #2C, #4C, 22, 44, 36, 36, 0
                DEFW #FFF5
                DEFW #FFF5
                DEFB #0F, #F4, #4F, 32, 16, 13, 52, 0
                DEFW #FFFC
                DEFW #FFF0
                DEFB #0F, #F4, #51, 24, 48, 39, 39, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0F, #74, #56, 8, 64, 52, 13, 0
                DEFW #FFF0
                DEFW #FFFC
                DEFB #0F, #74, #58, 24, 48, 39, 39, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0F, #F4, #5C, 32, 16, 13, 52, 0
                DEFW #FFFC
                DEFW #FFF0
                DEFB #0F, #F4, #5E, 24, 48, 39, 39, 0
                DEFW #FFF4
                DEFW #FFF4
                DEFB #0F, #74, #63, 8, 64, 52, 13, 0
                DEFW #FFF0
                DEFW #FFFC
                DEFB #0F, #74, #65, 24, 48, 39, 39, 0
                DEFW #FFF4
                DEFW #FFF4

MINIMAP_MAP_W           EQU 36
MINIMAP_MAP_H           EQU 36

UI_STONBACK_RAMG        EQU #0D52D8
UI_STONBACK_W           EQU 144
UI_STONBACK_H           EQU 72
UI_STONBACK_STRIDE      EQU 144
UI_RESSMALL_RAMG        EQU #0D7B58
UI_RESSMALL_W           EQU 133
UI_RESSMALL_H           EQU 56
UI_RESSMALL_STRIDE      EQU 133
UI_SUNMOON_RAMG         EQU #0D9870
UI_SUNMOON_W            EQU 144
UI_SUNMOON_H            EQU 25
UI_SUNMOON_STRIDE       EQU 144
UI_LBL_MONTH_RAMG       EQU #0C8BE8
UI_LBL_MONTH_W          EQU 45
UI_LBL_MONTH_H          EQU 10
UI_LBL_MONTH_STRIDE     EQU 45
UI_LBL_WEEK_RAMG       EQU #0C8DAC
UI_LBL_WEEK_W          EQU 39
UI_LBL_WEEK_H          EQU 10
UI_LBL_WEEK_STRIDE     EQU 39
UI_LBL_DAY_RAMG       EQU #0C8F34
UI_LBL_DAY_W          EQU 28
UI_LBL_DAY_H          EQU 12
UI_LBL_DAY_STRIDE     EQU 28
UI_ARMY_COUNT           EQU 2
UI_ARMY0_RAMG           EQU #0DA680
UI_ARMY0_W              EQU 32
UI_ARMY0_H              EQU 32
UI_ARMY0_STRIDE         EQU 32
UI_ARMY0_COUNT          EQU 40
UI_ARMY1_RAMG           EQU #0DAA80
UI_ARMY1_W              EQU 32
UI_ARMY1_H              EQU 32
UI_ARMY1_STRIDE         EQU 32
UI_ARMY1_COUNT          EQU 4
UI_PORTXTRA_RAMG        EQU #0C9484
UI_PORTXTRA_W           EQU 46
UI_PORTXTRA_H           EQU 22
UI_PORTXTRA_STRIDE      EQU 46
UI_MOBILITY_RAMG        EQU #0C9878
UI_MOBILITY_W           EQU 7
UI_MOBILITY_H           EQU 22
UI_MOBILITY_STRIDE      EQU 7
UI_MOBILITY_FRAMES      EQU 26
MobilityFrameTable:
                DEFB #78, #98, #0C
                DEFB #14, #99, #0C
                DEFB #B0, #99, #0C
                DEFB #4C, #9A, #0C
                DEFB #E8, #9A, #0C
                DEFB #84, #9B, #0C
                DEFB #20, #9C, #0C
                DEFB #BC, #9C, #0C
                DEFB #58, #9D, #0C
                DEFB #F4, #9D, #0C
                DEFB #90, #9E, #0C
                DEFB #2C, #9F, #0C
                DEFB #C8, #9F, #0C
                DEFB #64, #A0, #0C
                DEFB #00, #A1, #0C
                DEFB #9C, #A1, #0C
                DEFB #38, #A2, #0C
                DEFB #D4, #A2, #0C
                DEFB #70, #A3, #0C
                DEFB #0C, #A4, #0C
                DEFB #A8, #A4, #0C
                DEFB #44, #A5, #0C
                DEFB #E0, #A5, #0C
                DEFB #7C, #A6, #0C
                DEFB #18, #A7, #0C
                DEFB #B4, #A7, #0C
UI_MANA_RAMG            EQU #0CA850
UI_MANA_W               EQU 7
UI_MANA_H               EQU 22
UI_MANA_STRIDE          EQU 7
UI_MANA_FRAMES          EQU 26
ManaFrameTable:
                DEFB #50, #A8, #0C
                DEFB #EC, #A8, #0C
                DEFB #88, #A9, #0C
                DEFB #24, #AA, #0C
                DEFB #C0, #AA, #0C
                DEFB #5C, #AB, #0C
                DEFB #F8, #AB, #0C
                DEFB #94, #AC, #0C
                DEFB #30, #AD, #0C
                DEFB #CC, #AD, #0C
                DEFB #68, #AE, #0C
                DEFB #04, #AF, #0C
                DEFB #A0, #AF, #0C
                DEFB #3C, #B0, #0C
                DEFB #D8, #B0, #0C
                DEFB #74, #B1, #0C
                DEFB #10, #B2, #0C
                DEFB #AC, #B2, #0C
                DEFB #48, #B3, #0C
                DEFB #E4, #B3, #0C
                DEFB #80, #B4, #0C
                DEFB #1C, #B5, #0C
                DEFB #B8, #B5, #0C
                DEFB #54, #B6, #0C
                DEFB #F0, #B6, #0C
                DEFB #8C, #B7, #0C
UI_MINIPORT_RAMG        EQU #0CB828
UI_MINIPORT_W           EQU 30
UI_MINIPORT_H           EQU 22
UI_MINIPORT_STRIDE      EQU 30
UI_MINIPORT_FRAMES      EQU 60

DIGIT_ENTRY             EQU 5
DigitTable:
                DEFB #F4, #89, #0C, 5, 10
                DEFB #28, #8A, #0C, 3, 10
                DEFB #48, #8A, #0C, 5, 10
                DEFB #7C, #8A, #0C, 5, 10
                DEFB #B0, #8A, #0C, 5, 10
                DEFB #E4, #8A, #0C, 5, 10
                DEFB #18, #8B, #0C, 5, 10
                DEFB #4C, #8B, #0C, 5, 10
                DEFB #80, #8B, #0C, 5, 10
                DEFB #B4, #8B, #0C, 5, 10
RESOURCE_PANEL_RAMG     EQU #0C9084

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
                FT_BITMAP_SOURCE #0B3F74
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 12288, 4506
                FT_BITMAP_SOURCE #0B4874
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 12288, 5325
                FT_BITMAP_SOURCE #0B4874
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 12288, 6144
                FT_BITMAP_SOURCE #0B5174
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 12288, 6963
                FT_BITMAP_SOURCE #0B3F74
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 14131, 4506
                FT_BITMAP_SOURCE #0B4874
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 14131, 5325
                FT_BITMAP_SOURCE #0B4874
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 14131, 6144
                FT_BITMAP_SOURCE #0B5174
                FT_BITMAP_LAYOUT FT_PALETTED4444, 72, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 116, 52
                FT_VERTEX2F 14131, 6963
                FT_BITMAP_SOURCE #0B5A74
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 72
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 231, 116
                FT_VERTEX2F 12288, 10035
                FT_END
                FT_PALETTE_SOURCE OBJECT_PALETTE_RAMG
                FT_BEGIN FT_BITMAPS
                FT_END
                FT_BLEND_FUNC FT_ONE, FT_ZERO
                FT_PALETTE_SOURCE UI_RADAR_PALETTE_RAMG
                FT_BITMAP_SOURCE #0DAE80
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 144
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 231, 231
                FT_BEGIN FT_BITMAPS
                FT_VERTEX2F 12288, 410
                FT_END
                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA
                FT_PALETTE_SOURCE OBJECT_OPAQUE_PALETTE_RAMG
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_LAYOUT_H 0, 0
                FT_BITMAP_SIZE_H 0, 0
                FT_BITMAP_SOURCE #0B82F4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 193, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 309, 26
                FT_VERTEX2F 0, 0
                FT_BITMAP_SOURCE #0B8F04
                FT_BITMAP_LAYOUT FT_PALETTED4444, 6, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 10, 26
                FT_VERTEX2F 4941, 0
                FT_BITMAP_SOURCE #0B8F64
                FT_BITMAP_LAYOUT FT_PALETTED4444, 24, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 39, 26
                FT_VERTEX2F 5094, 0
                FT_BITMAP_SOURCE #0B90E4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 26
                FT_VERTEX2F 5709, 0
                FT_BITMAP_SOURCE #0B92E4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 25, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 26
                FT_VERTEX2F 6528, 0
                FT_BITMAP_SOURCE #0B9474
                FT_BITMAP_LAYOUT FT_PALETTED4444, 6, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 10, 26
                FT_VERTEX2F 7168, 0
                FT_BITMAP_SOURCE #0B94D4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 319, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 511, 26
                FT_VERTEX2F 7322, 0
                FT_BITMAP_SOURCE #0BA8C4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 35, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 56, 26
                FT_VERTEX2F 15488, 0
                FT_BITMAP_SOURCE #0BAAF4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 239
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 383
                FT_VERTEX2F 0, 410
                FT_BITMAP_SOURCE #0BB9E4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 0, 6528
                FT_BITMAP_SOURCE #0BBBE4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 125
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 200
                FT_VERTEX2F 0, 7347
                FT_BITMAP_SOURCE #0BC3B4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 4
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 7
                FT_VERTEX2F 0, 10547
                FT_BITMAP_SOURCE #0BC3F4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 48
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 77
                FT_VERTEX2F 0, 10650
                FT_BITMAP_SOURCE #0BC6F4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 239
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 383
                FT_VERTEX2F 11878, 410
                FT_BITMAP_SOURCE #0BD5E4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 11878, 6528
                FT_BITMAP_SOURCE #0BD7E4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 50
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 80
                FT_VERTEX2F 11878, 7347
                FT_BITMAP_SOURCE #0BDB04
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 11878, 8627
                FT_BITMAP_SOURCE #0BDD04
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 43
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 69
                FT_VERTEX2F 11878, 9446
                FT_BITMAP_SOURCE #0BDFB4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 8
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 13
                FT_VERTEX2F 11878, 10547
                FT_BITMAP_SOURCE #0BE034
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 44
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 71
                FT_VERTEX2F 11878, 10752
                FT_BITMAP_SOURCE #0BE2F4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 239
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 383
                FT_VERTEX2F 15974, 410
                FT_BITMAP_SOURCE #0BF1E4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 15974, 6528
                FT_BITMAP_SOURCE #0BF3E4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 50
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 80
                FT_VERTEX2F 15974, 7347
                FT_BITMAP_SOURCE #0BF704
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 52
                FT_VERTEX2F 15974, 8627
                FT_BITMAP_SOURCE #0BF904
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 43
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 69
                FT_VERTEX2F 15974, 9446
                FT_BITMAP_SOURCE #0BFBB4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 4
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 7
                FT_VERTEX2F 15974, 10547
                FT_BITMAP_SOURCE #0BFBF4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 16, 48
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 26, 77
                FT_VERTEX2F 15974, 10650
                FT_BITMAP_SOURCE #0BFEF4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 193, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 309, 26
                FT_VERTEX2F 0, 11878
                FT_BITMAP_SOURCE #0C0B04
                FT_BITMAP_LAYOUT FT_PALETTED4444, 6, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 10, 26
                FT_VERTEX2F 4941, 11878
                FT_BITMAP_SOURCE #0C0B64
                FT_BITMAP_LAYOUT FT_PALETTED4444, 24, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 39, 26
                FT_VERTEX2F 5094, 11878
                FT_BITMAP_SOURCE #0C0CE4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 52, 26
                FT_VERTEX2F 5709, 11878
                FT_BITMAP_SOURCE #0C0EE4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 25, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 40, 26
                FT_VERTEX2F 6528, 11878
                FT_BITMAP_SOURCE #0C1074
                FT_BITMAP_LAYOUT FT_PALETTED4444, 6, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 10, 26
                FT_VERTEX2F 7168, 11878
                FT_BITMAP_SOURCE #0C10D4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 319, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 511, 26
                FT_VERTEX2F 7322, 11878
                FT_BITMAP_SOURCE #0C24C4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 35, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 56, 26
                FT_VERTEX2F 15488, 11878
                FT_BITMAP_SOURCE #0C26F4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 144, 16
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 231, 26
                FT_VERTEX2F 12288, 4096
                FT_BITMAP_SOURCE #0C2FF4
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
                FT_BITMAP_SOURCE #0C38F4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 8192
UI_BtnNormal_1_DL:
                FT_BITMAP_SOURCE #0C4314
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 8192
UI_BtnNormal_2_DL:
                FT_BITMAP_SOURCE #0C4D34
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 8192
UI_BtnNormal_3_DL:
                FT_BITMAP_SOURCE #0C5754
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 15053, 8192
UI_BtnNormal_4_DL:
                FT_BITMAP_SOURCE #0C6174
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 9114
UI_BtnNormal_5_DL:
                FT_BITMAP_SOURCE #0C6B94
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 9114
UI_BtnNormal_6_DL:
                FT_BITMAP_SOURCE #0C75B4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 9114
UI_BtnNormal_7_DL:
                FT_BITMAP_SOURCE #0C7FD4
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
                FT_BITMAP_SOURCE #0C3E04
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 8192
UI_BtnPressed_1_DL:
                FT_BITMAP_SOURCE #0C4824
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 8192
UI_BtnPressed_2_DL:
                FT_BITMAP_SOURCE #0C5244
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 8192
UI_BtnPressed_3_DL:
                FT_BITMAP_SOURCE #0C5C64
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 15053, 8192
UI_BtnPressed_4_DL:
                FT_BITMAP_SOURCE #0C6684
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 9114
UI_BtnPressed_5_DL:
                FT_BITMAP_SOURCE #0C70A4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 9114
UI_BtnPressed_6_DL:
                FT_BITMAP_SOURCE #0C7AC4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 9114
UI_BtnPressed_7_DL:
                FT_BITMAP_SOURCE #0C84E4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 15053, 9114
@UI_BtnPressed_DL_SIZE EQU UI_BtnPressed_1_DL - UI_BtnPressed_0_DL

Objects_Upload:
                GetPage3
                LD   (.RestorePage), A
                LD   A, #72
                LD   (.CurPage), A
                LD   A, #07
                LD   (.DHi), A
                LD   HL, #9000
                LD   (.DLo), HL
                LD   A, 27
                LD   (.Remain), A
.upl:           LD   A, (.CurPage)
                SetPage3_A
                LD   HL, #C000
                LD   A, (.DHi)
                LD   DE, (.DLo)
                LD   BC, 16384
                CALL FT.WriteMem
                LD   A, (.CurPage)
                INC  A
                LD   (.CurPage), A
                LD   HL, (.DLo)
                LD   DE, #4000
                ADD  HL, DE
                LD   (.DLo), HL
                JR   NC, .noc
                LD   A, (.DHi)
                INC  A
                LD   (.DHi), A
.noc:           LD   A, (.Remain)
                DEC  A
                LD   (.Remain), A
                JR   NZ, .upl
                LD   A, (.CurPage)
                SetPage3_A
                LD   HL, #C000
                LD   A, (.DHi)
                LD   DE, (.DLo)
                LD   BC, 6650
                CALL FT.WriteMem
                LD   A, (.RestorePage)
                SetPage3_A
                RET
.CurPage:       DEFB 0
.DHi:           DEFB 0
.DLo:           DEFW 0
.Remain:        DEFB 0
.RestorePage:   DEFB 0

Cursor_GlobalUpload:
                GetPage3
                LD   (.CurRestore), A
                SetPage3 #A2
                LD   HL, #C000
                LD   A, #0E
                LD   DE, #8000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #A3
                LD   HL, #C000
                LD   A, #0E
                LD   DE, #C000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #A4
                LD   HL, #C000
                LD   A, #0F
                LD   DE, #0000
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #A5
                LD   HL, #C000
                LD   A, #0F
                LD   DE, #4000
                LD   BC, 10740
                CALL FT.WriteMem
.CurRestore     EQU $+1
                LD   A, #00
                SetPage3_A
                RET
