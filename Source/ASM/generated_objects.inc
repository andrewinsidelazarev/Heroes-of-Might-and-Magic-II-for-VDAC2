; Сгенерировано Source/Tools/viewport_pack.py

OBJECT_ATLAS_RAMG       EQU #079000
OBJECT_PALETTE_RAMG     EQU #079000
OBJECT_OPAQUE_PALETTE_RAMG EQU #079200
OBJECT_PALETTE_SIZE     EQU 512
OBJECT_OPAQUE_PALETTE_SIZE EQU 512
OBJECT_ATLAS_PAGE_BASE  EQU #07
OBJECT_ATLAS_PAGE_COUNT EQU 28
OBJECT_ATLAS_SIZE       EQU 451322
HERO_SPRITE_RAMG        EQU #0F6A00
HERO_SPRITE_W           EQU 47
HERO_SPRITE_H           EQU 54
HERO_SPRITE_OX          EQU -8
HERO_SPRITE_OY          EQU -49
HERO_ANIM_FRAME_BYTES   EQU 5076   ; байт/кадр walk
HERO_ANIM_COUNT         EQU 8          ; кадров/направление
HERO_DIR_COUNT          EQU 5          ; направлений
HERO_BUF_A_RAMG         EQU #0F6A00
HERO_BUF_B_RAMG         EQU #0F7DD4
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
UI_RADAR_RAMG           EQU #0DB780
UI_RADAR_PALETTE_RAMG   EQU #0E0880
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

UI_STONBACK_RAMG        EQU #0D5BD8
UI_STONBACK_W           EQU 144
UI_STONBACK_H           EQU 72
UI_STONBACK_STRIDE      EQU 144
UI_RESSMALL_RAMG        EQU #0D8458
UI_RESSMALL_W           EQU 133
UI_RESSMALL_H           EQU 56
UI_RESSMALL_STRIDE      EQU 133
UI_SUNMOON_RAMG         EQU #0DA170
UI_SUNMOON_W            EQU 144
UI_SUNMOON_H            EQU 25
UI_SUNMOON_STRIDE       EQU 144
UI_LBL_MONTH_RAMG       EQU #0C94E8
UI_LBL_MONTH_W          EQU 45
UI_LBL_MONTH_H          EQU 10
UI_LBL_MONTH_STRIDE     EQU 45
UI_LBL_WEEK_RAMG       EQU #0C96AC
UI_LBL_WEEK_W          EQU 39
UI_LBL_WEEK_H          EQU 10
UI_LBL_WEEK_STRIDE     EQU 39
UI_LBL_DAY_RAMG       EQU #0C9834
UI_LBL_DAY_W          EQU 28
UI_LBL_DAY_H          EQU 12
UI_LBL_DAY_STRIDE     EQU 28
UI_ARMY_COUNT           EQU 2
UI_ARMY0_RAMG           EQU #0DAF80
UI_ARMY0_W              EQU 32
UI_ARMY0_H              EQU 32
UI_ARMY0_STRIDE         EQU 32
UI_ARMY0_COUNT          EQU 40
UI_ARMY1_RAMG           EQU #0DB380
UI_ARMY1_W              EQU 32
UI_ARMY1_H              EQU 32
UI_ARMY1_STRIDE         EQU 32
UI_ARMY1_COUNT          EQU 4
UI_PORTXTRA_RAMG        EQU #0C9D84
UI_PORTXTRA_W           EQU 46
UI_PORTXTRA_H           EQU 22
UI_PORTXTRA_STRIDE      EQU 46
UI_MOBILITY_RAMG        EQU #0CA178
UI_MOBILITY_W           EQU 7
UI_MOBILITY_H           EQU 22
UI_MOBILITY_STRIDE      EQU 7
UI_MOBILITY_FRAMES      EQU 26
MobilityFrameTable:
                DEFB #78, #A1, #0C
                DEFB #14, #A2, #0C
                DEFB #B0, #A2, #0C
                DEFB #4C, #A3, #0C
                DEFB #E8, #A3, #0C
                DEFB #84, #A4, #0C
                DEFB #20, #A5, #0C
                DEFB #BC, #A5, #0C
                DEFB #58, #A6, #0C
                DEFB #F4, #A6, #0C
                DEFB #90, #A7, #0C
                DEFB #2C, #A8, #0C
                DEFB #C8, #A8, #0C
                DEFB #64, #A9, #0C
                DEFB #00, #AA, #0C
                DEFB #9C, #AA, #0C
                DEFB #38, #AB, #0C
                DEFB #D4, #AB, #0C
                DEFB #70, #AC, #0C
                DEFB #0C, #AD, #0C
                DEFB #A8, #AD, #0C
                DEFB #44, #AE, #0C
                DEFB #E0, #AE, #0C
                DEFB #7C, #AF, #0C
                DEFB #18, #B0, #0C
                DEFB #B4, #B0, #0C
UI_MANA_RAMG            EQU #0CB150
UI_MANA_W               EQU 7
UI_MANA_H               EQU 22
UI_MANA_STRIDE          EQU 7
UI_MANA_FRAMES          EQU 26
ManaFrameTable:
                DEFB #50, #B1, #0C
                DEFB #EC, #B1, #0C
                DEFB #88, #B2, #0C
                DEFB #24, #B3, #0C
                DEFB #C0, #B3, #0C
                DEFB #5C, #B4, #0C
                DEFB #F8, #B4, #0C
                DEFB #94, #B5, #0C
                DEFB #30, #B6, #0C
                DEFB #CC, #B6, #0C
                DEFB #68, #B7, #0C
                DEFB #04, #B8, #0C
                DEFB #A0, #B8, #0C
                DEFB #3C, #B9, #0C
                DEFB #D8, #B9, #0C
                DEFB #74, #BA, #0C
                DEFB #10, #BB, #0C
                DEFB #AC, #BB, #0C
                DEFB #48, #BC, #0C
                DEFB #E4, #BC, #0C
                DEFB #80, #BD, #0C
                DEFB #1C, #BE, #0C
                DEFB #B8, #BE, #0C
                DEFB #54, #BF, #0C
                DEFB #F0, #BF, #0C
                DEFB #8C, #C0, #0C
UI_MINIPORT_RAMG        EQU #0CC128
UI_MINIPORT_W           EQU 30
UI_MINIPORT_H           EQU 22
UI_MINIPORT_STRIDE      EQU 30
UI_MINIPORT_FRAMES      EQU 60

DIGIT_ENTRY             EQU 5
DigitTable:
                DEFB #F4, #92, #0C, 5, 10
                DEFB #28, #93, #0C, 3, 10
                DEFB #48, #93, #0C, 5, 10
                DEFB #7C, #93, #0C, 5, 10
                DEFB #B0, #93, #0C, 5, 10
                DEFB #E4, #93, #0C, 5, 10
                DEFB #18, #94, #0C, 5, 10
                DEFB #4C, #94, #0C, 5, 10
                DEFB #80, #94, #0C, 5, 10
                DEFB #B4, #94, #0C, 5, 10
RESOURCE_PANEL_RAMG     EQU #0C9984

AdventureUI_DL:
                DEFB #00, #00, #00, #1B, #00, #03, #40, #1C, #FF, #FF, #FF, #04, #FF, #00, #00, #10
                DEFB #03, #00, #00, #05, #00, #00, #00, #06, #A0, #00, #00, #15, #00, #00, #00, #16
                DEFB #00, #00, #00, #17, #00, #00, #00, #18, #A0, #00, #00, #19, #00, #00, #00, #1A
                DEFB #00, #00, #00, #2B, #00, #00, #00, #2C, #14, #00, #00, #0B, #00, #92, #07, #2A
                DEFB #00, #00, #00, #28, #00, #00, #00, #29, #01, #00, #00, #1F, #74, #3F, #0B, #01
                DEFB #20, #90, #78, #07, #34, #E8, #00, #08, #9A, #11, #00, #58, #74, #3F, #0B, #01
                DEFB #20, #90, #78, #07, #34, #E8, #00, #08, #9A, #91, #99, #5B, #74, #48, #0B, #01
                DEFB #20, #90, #78, #07, #34, #E8, #00, #08, #CD, #14, #00, #58, #74, #48, #0B, #01
                DEFB #20, #90, #78, #07, #34, #E8, #00, #08, #CD, #94, #99, #5B, #74, #51, #0B, #01
                DEFB #20, #90, #78, #07, #34, #E8, #00, #08, #00, #18, #00, #58, #74, #51, #0B, #01
                DEFB #20, #90, #78, #07, #34, #E8, #00, #08, #00, #98, #99, #5B, #74, #5A, #0B, #01
                DEFB #20, #90, #78, #07, #34, #E8, #00, #08, #33, #1B, #00, #58, #74, #5A, #0B, #01
                DEFB #20, #90, #78, #07, #34, #E8, #00, #08, #33, #9B, #99, #5B, #74, #63, #0B, #01
                DEFB #48, #20, #79, #07, #74, #CE, #01, #08, #33, #27, #00, #58, #00, #00, #00, #21
                DEFB #00, #90, #07, #2A, #01, #00, #00, #1F, #00, #00, #00, #21, #08, #00, #00, #0B
                DEFB #80, #08, #0E, #2A, #80, #B7, #0D, #01, #90, #20, #79, #07, #E7, #CE, #01, #08
                DEFB #01, #00, #00, #1F, #9A, #01, #00, #58, #00, #00, #00, #21, #14, #00, #00, #0B
                DEFB #00, #92, #07, #2A, #01, #00, #00, #1F, #00, #00, #00, #28, #00, #00, #00, #29
                DEFB #F4, #8B, #0B, #01, #10, #82, #79, #07, #1A, #6A, #02, #08, #00, #00, #00, #40
                DEFB #04, #98, #0B, #01, #10, #0C, #78, #07, #1A, #14, #00, #08, #00, #80, #A6, #49
                DEFB #64, #98, #0B, #01, #10, #30, #78, #07, #1A, #4E, #00, #08, #00, #00, #F3, #49
                DEFB #E4, #99, #0B, #01, #10, #40, #78, #07, #1A, #68, #00, #08, #00, #80, #26, #4B
                DEFB #E4, #9B, #0B, #01, #10, #32, #78, #07, #1A, #50, #00, #08, #00, #00, #C0, #4C
                DEFB #74, #9D, #0B, #01, #10, #0C, #78, #07, #1A, #14, #00, #08, #00, #00, #00, #4E
                DEFB #D4, #9D, #0B, #01, #10, #7E, #7A, #07, #1A, #FE, #03, #08, #00, #00, #4D, #4E
                DEFB #C4, #B1, #0B, #01, #10, #46, #78, #07, #1A, #70, #00, #08, #00, #00, #40, #5E
                DEFB #F4, #B3, #0B, #01, #EF, #20, #78, #07, #7F, #35, #00, #08, #9A, #01, #00, #40
                DEFB #E4, #C2, #0B, #01, #20, #20, #78, #07, #34, #34, #00, #08, #80, #19, #00, #40
                DEFB #E4, #C4, #0B, #01, #7D, #20, #78, #07, #C8, #34, #00, #08, #B3, #1C, #00, #40
                DEFB #B4, #CC, #0B, #01, #04, #20, #78, #07, #07, #34, #00, #08, #33, #29, #00, #40
                DEFB #F4, #CC, #0B, #01, #30, #20, #78, #07, #4D, #34, #00, #08, #9A, #29, #00, #40
                DEFB #F4, #CF, #0B, #01, #EF, #20, #78, #07, #7F, #35, #00, #08, #9A, #01, #33, #57
                DEFB #E4, #DE, #0B, #01, #20, #20, #78, #07, #34, #34, #00, #08, #80, #19, #33, #57
                DEFB #E4, #E0, #0B, #01, #32, #20, #78, #07, #50, #34, #00, #08, #B3, #1C, #33, #57
                DEFB #04, #E4, #0B, #01, #20, #20, #78, #07, #34, #34, #00, #08, #B3, #21, #33, #57
                DEFB #04, #E6, #0B, #01, #2B, #20, #78, #07, #45, #34, #00, #08, #E6, #24, #33, #57
                DEFB #B4, #E8, #0B, #01, #08, #20, #78, #07, #0D, #34, #00, #08, #33, #29, #33, #57
                DEFB #34, #E9, #0B, #01, #2C, #20, #78, #07, #47, #34, #00, #08, #00, #2A, #33, #57
                DEFB #F4, #EB, #0B, #01, #EF, #20, #78, #07, #7F, #35, #00, #08, #9A, #01, #33, #5F
                DEFB #E4, #FA, #0B, #01, #20, #20, #78, #07, #34, #34, #00, #08, #80, #19, #33, #5F
                DEFB #E4, #FC, #0B, #01, #32, #20, #78, #07, #50, #34, #00, #08, #B3, #1C, #33, #5F
                DEFB #04, #00, #0C, #01, #20, #20, #78, #07, #34, #34, #00, #08, #B3, #21, #33, #5F
                DEFB #04, #02, #0C, #01, #2B, #20, #78, #07, #45, #34, #00, #08, #E6, #24, #33, #5F
                DEFB #B4, #04, #0C, #01, #04, #20, #78, #07, #07, #34, #00, #08, #33, #29, #33, #5F
                DEFB #F4, #04, #0C, #01, #30, #20, #78, #07, #4D, #34, #00, #08, #9A, #29, #33, #5F
                DEFB #F4, #07, #0C, #01, #10, #82, #79, #07, #1A, #6A, #02, #08, #66, #2E, #00, #40
                DEFB #04, #14, #0C, #01, #10, #0C, #78, #07, #1A, #14, #00, #08, #66, #AE, #A6, #49
                DEFB #64, #14, #0C, #01, #10, #30, #78, #07, #1A, #4E, #00, #08, #66, #2E, #F3, #49
                DEFB #E4, #15, #0C, #01, #10, #40, #78, #07, #1A, #68, #00, #08, #66, #AE, #26, #4B
                DEFB #E4, #17, #0C, #01, #10, #32, #78, #07, #1A, #50, #00, #08, #66, #2E, #C0, #4C
                DEFB #74, #19, #0C, #01, #10, #0C, #78, #07, #1A, #14, #00, #08, #66, #2E, #00, #4E
                DEFB #D4, #19, #0C, #01, #10, #7E, #7A, #07, #1A, #FE, #03, #08, #66, #2E, #4D, #4E
                DEFB #C4, #2D, #0C, #01, #10, #46, #78, #07, #1A, #70, #00, #08, #66, #2E, #40, #5E
                DEFB #F4, #2F, #0C, #01, #10, #20, #79, #07, #1A, #CE, #01, #08, #00, #10, #00, #58
                DEFB #F4, #38, #0C, #01, #10, #20, #79, #07, #1A, #CE, #01, #08, #66, #1E, #00, #58
                DEFB #00, #00, #00, #21, #00, #00, #00, #28, #00, #00, #00, #29
AdventureUI_DL_SIZE EQU 892
UIADV_ICONSDYN_RAMG     EQU #0FE050   ; мини-DL динамики списка (замок+маркер)
UIADV_ICONSDYN_SIZE     EQU 72

; --- Списки героев/замков (interface_icons.cpp): динамика UIADV-блока ---
; (пустые ячейки LOCATORS[2,3,4] и SCROLL вбейканы в фоновые полосы — 0 тактов/строку)
; LOCATORS замка: [9]=Knight castle, [15]=Knight town [lo,mid,hi,w,h]
UIAdvLocatorsTab:
                DEFB #00, #92, #0F, 46, 22  ; LOCATORS[9]
                DEFB #F4, #95, #0F, 47, 22  ; LOCATORS[15]
UIADV_SUNMOON_RAMG      EQU #0F9A00   ; 5 кадров фикс-слотами (кадр по дню)
UIADV_SUNMOON_SLOT      EQU 3600
UIADV_SUNMOON_W         EQU 144
UIADV_SUNMOON_H         EQU 25

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
                FT_BITMAP_SOURCE #0C41F4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 8192
UI_BtnNormal_1_DL:
                FT_BITMAP_SOURCE #0C4C14
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 8192
UI_BtnNormal_2_DL:
                FT_BITMAP_SOURCE #0C5634
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 8192
UI_BtnNormal_3_DL:
                FT_BITMAP_SOURCE #0C6054
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 15053, 8192
UI_BtnNormal_4_DL:
                FT_BITMAP_SOURCE #0C6A74
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 9114
UI_BtnNormal_5_DL:
                FT_BITMAP_SOURCE #0C7494
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 9114
UI_BtnNormal_6_DL:
                FT_BITMAP_SOURCE #0C7EB4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 9114
UI_BtnNormal_7_DL:
                FT_BITMAP_SOURCE #0C88D4
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
                FT_BITMAP_SOURCE #0C4704
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 8192
UI_BtnPressed_1_DL:
                FT_BITMAP_SOURCE #0C5124
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 8192
UI_BtnPressed_2_DL:
                FT_BITMAP_SOURCE #0C5B44
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 8192
UI_BtnPressed_3_DL:
                FT_BITMAP_SOURCE #0C6564
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 15053, 8192
UI_BtnPressed_4_DL:
                FT_BITMAP_SOURCE #0C6F84
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 12288, 9114
UI_BtnPressed_5_DL:
                FT_BITMAP_SOURCE #0C79A4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 13210, 9114
UI_BtnPressed_6_DL:
                FT_BITMAP_SOURCE #0C83C4
                FT_BITMAP_LAYOUT FT_PALETTED4444, 36, 36
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, 58, 58
                FT_VERTEX2F 14131, 9114
UI_BtnPressed_7_DL:
                FT_BITMAP_SOURCE #0C8DE4
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
                LD   BC, 8954
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

UIAdv_Upload:
                GetPage3
                LD   (.UARestore), A
                SetPage3 #BF
                LD   HL, #C000
                LD   A, #0F
                LD   DE, #9200
                LD   BC, 16384
                CALL FT.WriteMem
                SetPage3 #C0
                LD   HL, #C000
                LD   A, #0F
                LD   DE, #D200
                LD   BC, 3736
                CALL FT.WriteMem
.UARestore      EQU $+1
                LD   A, #00
                SetPage3_A
                RET

HERO_ANIM_BASE_PAGE  EQU #AB
HERO_FRAME_SLOT      EQU 8192          ; 2 кадра/страницу (без straddle)
HeroBufSel:      DEFB 0                          ; 0=A показан→грузить B; 1=B показан→грузить A
; HeroAnim_Upload: старт — кадр HORIZ(dir2,f0)=индекс 16 в буфер B, SOURCE на него.
HeroAnim_Upload:
                XOR  A
                LD   (HeroBufSel), A
                LD   A, 16
; HeroAnim_StreamFrame: A=индекс кадра (dir*COUNT+f). Грузит кадр в НЕВИДИМЫЙ буфер
; (луч читает ДРУГОЙ → запись без разрыва при любом тайминге), затем SOURCE в DL →
; этот буфер (атомарно на DLSWAP). Разрыва спрайта физически быть не может.
HeroAnim_StreamFrame:
                LD   B, A
                SRL  B                            ; B = индекс/2 = дельта страницы
                AND  1                            ; A = индекс&1 (0→окно #C000, 1→#E000)
                LD   HL, #C000
                OR   A
                JR   Z, .sfoff0
                LD   HL, #E000
.sfoff0:        LD   (.SfSrc), HL
                LD   A, B
                ADD  A, HERO_ANIM_BASE_PAGE
                LD   (.SfPage), A
                LD   A, (HeroBufSel)              ; целевой = НЕВИДИМЫЙ буфер
                OR   A
                JR   NZ, .sftgtA
                LD   HL, #7DD4         ; sel0 → грузить B
                JR   .sftgts
.sftgtA:        LD   HL, #6A00         ; sel1 → грузить A
.sftgts:        LD   (.SfDst), HL
                GetPage3
                LD   (.SfRestore), A
                LD   A, (.SfPage)
                SetPage3_A
                LD   HL, (.SfSrc)
                LD   A, #0F
                LD   DE, (.SfDst)
                LD   BC, HERO_ANIM_FRAME_BYTES
                CALL FT.WriteMem
                LD   A, (.SfRestore)
                SetPage3_A
                LD   HL, (.SfDst)                 ; SOURCE в DL → загруженный буфер
                LD   (HERO_MARKER_SRC_LOW), HL
                LD   A, (HeroBufSel)              ; переключить «показанный» буфер
                XOR  1
                LD   (HeroBufSel), A
                RET
.SfSrc:         DEFW 0
.SfDst:         DEFW 0
.SfPage:        DEFB 0
.SfRestore:     DEFB 0
