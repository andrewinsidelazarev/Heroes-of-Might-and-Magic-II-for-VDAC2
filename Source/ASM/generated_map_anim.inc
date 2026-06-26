; Сгенерировано Source/Tools/viewport_pack.py — анимация adventure-объектов.
; Кадры-дельты (PALETTED4444) поверх базы; формула fheroes2:
;   frame = base + (MapAnimPhase % N) + 1; шаг ~250мс (MAPS_DELAY).
MAP_ANIM_COUNT          EQU 18
MAP_ANIM_PALETTE_RAMG   EQU OBJECT_PALETTE_RAMG
MapAnimTable:
                DEFB 28, 2, 6
                DEFB #B0, #0A, #0E, #01   ; SOURCE #E0AB0
                DEFB #07, #18, #78, #07   ; LAYOUT pal4444 12x7
                DEFB #0C, #28, #00, #08   ; SIZE
                DEFB 20, 14   ; ox,oy (signed)
                DEFB #04, #0B, #0E, #01   ; SOURCE #E0B04
                DEFB #09, #18, #78, #07   ; LAYOUT pal4444 12x9
                DEFB #0F, #28, #00, #08   ; SIZE
                DEFB 20, 14   ; ox,oy (signed)
                DEFB #70, #0B, #0E, #01   ; SOURCE #E0B70
                DEFB #09, #1C, #78, #07   ; LAYOUT pal4444 14x9
                DEFB #0F, #2E, #00, #08   ; SIZE
                DEFB 18, 13   ; ox,oy (signed)
                DEFB #F0, #0B, #0E, #01   ; SOURCE #E0BF0
                DEFB #0A, #1A, #78, #07   ; LAYOUT pal4444 13x10
                DEFB #10, #2A, #00, #08   ; SIZE
                DEFB 19, 14   ; ox,oy (signed)
                DEFB #74, #0C, #0E, #01   ; SOURCE #E0C74
                DEFB #0A, #1E, #78, #07   ; LAYOUT pal4444 15x10
                DEFB #10, #30, #00, #08   ; SIZE
                DEFB 17, 13   ; ox,oy (signed)
                DEFB #0C, #0D, #0E, #01   ; SOURCE #E0D0C
                DEFB #0B, #1E, #78, #07   ; LAYOUT pal4444 15x11
                DEFB #12, #30, #00, #08   ; SIZE
                DEFB 17, 14   ; ox,oy (signed)
                DEFB 29, 2, 6
                DEFB #B4, #0D, #0E, #01   ; SOURCE #E0DB4
                DEFB #11, #3A, #78, #07   ; LAYOUT pal4444 29x17
                DEFB #1C, #5E, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #A4, #0F, #0E, #01   ; SOURCE #E0FA4
                DEFB #10, #3C, #78, #07   ; LAYOUT pal4444 30x16
                DEFB #1A, #60, #00, #08   ; SIZE
                DEFB 0, 16   ; ox,oy (signed)
                DEFB #84, #11, #0E, #01   ; SOURCE #E1184
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #84, #13, #0E, #01   ; SOURCE #E1384
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #84, #15, #0E, #01   ; SOURCE #E1584
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #84, #17, #0E, #01   ; SOURCE #E1784
                DEFB #10, #3A, #78, #07   ; LAYOUT pal4444 29x16
                DEFB #1A, #5E, #00, #08   ; SIZE
                DEFB 0, 16   ; ox,oy (signed)
                DEFB 31, 2, 6
                DEFB #54, #19, #0E, #01   ; SOURCE #E1954
                DEFB #0E, #22, #78, #07   ; LAYOUT pal4444 17x14
                DEFB #17, #38, #00, #08   ; SIZE
                DEFB 9, 0   ; ox,oy (signed)
                DEFB #44, #1A, #0E, #01   ; SOURCE #E1A44
                DEFB #0E, #1C, #78, #07   ; LAYOUT pal4444 14x14
                DEFB #17, #2E, #00, #08   ; SIZE
                DEFB 12, 0   ; ox,oy (signed)
                DEFB #08, #1B, #0E, #01   ; SOURCE #E1B08
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #C0, #1B, #0E, #01   ; SOURCE #E1BC0
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #78, #1C, #0E, #01   ; SOURCE #E1C78
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #30, #1D, #0E, #01   ; SOURCE #E1D30
                DEFB #0E, #1E, #78, #07   ; LAYOUT pal4444 15x14
                DEFB #17, #30, #00, #08   ; SIZE
                DEFB 8, 0   ; ox,oy (signed)
                DEFB 15, 10, 6
                DEFB #04, #1E, #0E, #01   ; SOURCE #E1E04
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #34, #20, #0E, #01   ; SOURCE #E2034
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #64, #22, #0E, #01   ; SOURCE #E2264
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #94, #24, #0E, #01   ; SOURCE #E2494
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #C4, #26, #0E, #01   ; SOURCE #E26C4
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #F4, #28, #0E, #01   ; SOURCE #E28F4
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB 19, 26, 3
                DEFB #24, #2B, #0E, #01   ; SOURCE #E2B24
                DEFB #05, #16, #78, #07   ; LAYOUT pal4444 11x5
                DEFB #08, #24, #00, #08   ; SIZE
                DEFB 12, 27   ; ox,oy (signed)
                DEFB #5C, #2B, #0E, #01   ; SOURCE #E2B5C
                DEFB #07, #18, #78, #07   ; LAYOUT pal4444 12x7
                DEFB #0C, #28, #00, #08   ; SIZE
                DEFB 20, 25   ; ox,oy (signed)
                DEFB #B0, #2B, #0E, #01   ; SOURCE #E2BB0
                DEFB #05, #06, #78, #07   ; LAYOUT pal4444 3x5
                DEFB #08, #0A, #00, #08   ; SIZE
                DEFB 29, 27   ; ox,oy (signed)
                DEFB 20, 26, 3
                DEFB #C0, #2B, #0E, #01   ; SOURCE #E2BC0
                DEFB #01, #02, #78, #07   ; LAYOUT pal4444 1x1
                DEFB #02, #04, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #C4, #2B, #0E, #01   ; SOURCE #E2BC4
                DEFB #04, #02, #78, #07   ; LAYOUT pal4444 1x4
                DEFB #07, #04, #00, #08   ; SIZE
                DEFB 0, 28   ; ox,oy (signed)
                DEFB #C8, #2B, #0E, #01   ; SOURCE #E2BC8
                DEFB #05, #12, #78, #07   ; LAYOUT pal4444 9x5
                DEFB #08, #1E, #00, #08   ; SIZE
                DEFB 0, 27   ; ox,oy (signed)
                DEFB 17, 27, 3
                DEFB #F8, #2B, #0E, #01   ; SOURCE #E2BF8
                DEFB #03, #1C, #78, #07   ; LAYOUT pal4444 14x3
                DEFB #05, #2E, #00, #08   ; SIZE
                DEFB 14, 29   ; ox,oy (signed)
                DEFB #24, #2C, #0E, #01   ; SOURCE #E2C24
                DEFB #04, #1A, #78, #07   ; LAYOUT pal4444 13x4
                DEFB #07, #2A, #00, #08   ; SIZE
                DEFB 19, 28   ; ox,oy (signed)
                DEFB #58, #2C, #0E, #01   ; SOURCE #E2C58
                DEFB #02, #04, #78, #07   ; LAYOUT pal4444 2x2
                DEFB #04, #08, #00, #08   ; SIZE
                DEFB 30, 29   ; ox,oy (signed)
                DEFB 18, 27, 3
                DEFB #5C, #2C, #0E, #01   ; SOURCE #E2C5C
                DEFB #01, #02, #78, #07   ; LAYOUT pal4444 1x1
                DEFB #02, #04, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #60, #2C, #0E, #01   ; SOURCE #E2C60
                DEFB #02, #06, #78, #07   ; LAYOUT pal4444 3x2
                DEFB #04, #0A, #00, #08   ; SIZE
                DEFB 0, 30   ; ox,oy (signed)
                DEFB #68, #2C, #0E, #01   ; SOURCE #E2C68
                DEFB #03, #1C, #78, #07   ; LAYOUT pal4444 14x3
                DEFB #05, #2E, #00, #08   ; SIZE
                DEFB 0, 29   ; ox,oy (signed)
                DEFB 19, 27, 3
                DEFB #94, #2C, #0E, #01   ; SOURCE #E2C94
                DEFB #20, #38, #78, #07   ; LAYOUT pal4444 28x32
                DEFB #34, #5A, #00, #08   ; SIZE
                DEFB 4, 0   ; ox,oy (signed)
                DEFB #14, #30, #0E, #01   ; SOURCE #E3014
                DEFB #20, #3C, #78, #07   ; LAYOUT pal4444 30x32
                DEFB #34, #60, #00, #08   ; SIZE
                DEFB 2, 0   ; ox,oy (signed)
                DEFB #D4, #33, #0E, #01   ; SOURCE #E33D4
                DEFB #20, #38, #78, #07   ; LAYOUT pal4444 28x32
                DEFB #34, #5A, #00, #08   ; SIZE
                DEFB 4, 0   ; ox,oy (signed)
                DEFB 20, 27, 3
                DEFB #54, #37, #0E, #01   ; SOURCE #E3754
                DEFB #1E, #22, #78, #07   ; LAYOUT pal4444 17x30
                DEFB #30, #38, #00, #08   ; SIZE
                DEFB 0, 2   ; ox,oy (signed)
                DEFB #54, #39, #0E, #01   ; SOURCE #E3954
                DEFB #15, #26, #78, #07   ; LAYOUT pal4444 19x21
                DEFB #22, #3E, #00, #08   ; SIZE
                DEFB 0, 11   ; ox,oy (signed)
                DEFB #E4, #3A, #0E, #01   ; SOURCE #E3AE4
                DEFB #20, #22, #78, #07   ; LAYOUT pal4444 17x32
                DEFB #34, #38, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 17, 28, 3
                DEFB #04, #3D, #0E, #01   ; SOURCE #E3D04
                DEFB #0B, #1C, #78, #07   ; LAYOUT pal4444 14x11
                DEFB #12, #2E, #00, #08   ; SIZE
                DEFB 18, 0   ; ox,oy (signed)
                DEFB #A0, #3D, #0E, #01   ; SOURCE #E3DA0
                DEFB #0B, #1A, #78, #07   ; LAYOUT pal4444 13x11
                DEFB #12, #2A, #00, #08   ; SIZE
                DEFB 19, 0   ; ox,oy (signed)
                DEFB #30, #3E, #0E, #01   ; SOURCE #E3E30
                DEFB #07, #24, #78, #07   ; LAYOUT pal4444 18x7
                DEFB #0C, #3A, #00, #08   ; SIZE
                DEFB 14, 0   ; ox,oy (signed)
                DEFB 18, 28, 3
                DEFB #B0, #3E, #0E, #01   ; SOURCE #E3EB0
                DEFB #12, #40, #78, #07   ; LAYOUT pal4444 32x18
                DEFB #1D, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #F0, #40, #0E, #01   ; SOURCE #E40F0
                DEFB #12, #40, #78, #07   ; LAYOUT pal4444 32x18
                DEFB #1D, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #30, #43, #0E, #01   ; SOURCE #E4330
                DEFB #13, #40, #78, #07   ; LAYOUT pal4444 32x19
                DEFB #1F, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 19, 28, 3
                DEFB #90, #45, #0E, #01   ; SOURCE #E4590
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #B0, #48, #0E, #01   ; SOURCE #E48B0
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #D0, #4B, #0E, #01   ; SOURCE #E4BD0
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 20, 28, 3
                DEFB #F0, #4E, #0E, #01   ; SOURCE #E4EF0
                DEFB #08, #14, #78, #07   ; LAYOUT pal4444 10x8
                DEFB #0D, #20, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #40, #4F, #0E, #01   ; SOURCE #E4F40
                DEFB #08, #08, #78, #07   ; LAYOUT pal4444 4x8
                DEFB #0D, #0E, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #60, #4F, #0E, #01   ; SOURCE #E4F60
                DEFB #08, #18, #78, #07   ; LAYOUT pal4444 12x8
                DEFB #0D, #28, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 28, 29, 6
                DEFB #C0, #4F, #0E, #01   ; SOURCE #E4FC0
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #2C, #50, #0E, #01   ; SOURCE #E502C
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #98, #50, #0E, #01   ; SOURCE #E5098
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #04, #51, #0E, #01   ; SOURCE #E5104
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #70, #51, #0E, #01   ; SOURCE #E5170
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #DC, #51, #0E, #01   ; SOURCE #E51DC
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB 29, 29, 6
                DEFB #48, #52, #0E, #01   ; SOURCE #E5248
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #C0, #53, #0E, #01   ; SOURCE #E53C0
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #38, #55, #0E, #01   ; SOURCE #E5538
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #B0, #56, #0E, #01   ; SOURCE #E56B0
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #28, #58, #0E, #01   ; SOURCE #E5828
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #A0, #59, #0E, #01   ; SOURCE #E59A0
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB 28, 30, 6
                DEFB #18, #5B, #0E, #01   ; SOURCE #E5B18
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #C4, #5C, #0E, #01   ; SOURCE #E5CC4
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #70, #5E, #0E, #01   ; SOURCE #E5E70
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #1C, #60, #0E, #01   ; SOURCE #E601C
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #C8, #61, #0E, #01   ; SOURCE #E61C8
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #74, #63, #0E, #01   ; SOURCE #E6374
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB 29, 30, 6
                DEFB #20, #65, #0E, #01   ; SOURCE #E6520
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #C4, #67, #0E, #01   ; SOURCE #E67C4
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #68, #6A, #0E, #01   ; SOURCE #E6A68
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #0C, #6D, #0E, #01   ; SOURCE #E6D0C
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #B0, #6F, #0E, #01   ; SOURCE #E6FB0
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #54, #72, #0E, #01   ; SOURCE #E7254
                DEFB #1A, #36, #78, #07   ; LAYOUT pal4444 27x26
                DEFB #2A, #58, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
MAP_ANIM_ENTRY_HEADER   EQU 3
MAP_ANIM_FRAME_SIZE     EQU 14
