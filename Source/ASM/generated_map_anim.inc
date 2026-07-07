; Сгенерировано Source/Tools/viewport_pack.py — анимация adventure-объектов.
; Кадры-дельты (PALETTED4444) поверх базы; формула fheroes2:
;   frame = base + (MapAnimPhase % N) + 1; шаг ~250мс (MAPS_DELAY).
MAP_ANIM_COUNT          EQU 18
MAP_ANIM_PALETTE_RAMG   EQU OBJECT_PALETTE_RAMG
MapAnimTable:
                DEFB 28, 2, 6
                DEFB #98, #FF, #0D, #01   ; SOURCE #DFF98
                DEFB #07, #18, #78, #07   ; LAYOUT pal4444 12x7
                DEFB #0C, #28, #00, #08   ; SIZE
                DEFB 20, 14   ; ox,oy (signed)
                DEFB #EC, #FF, #0D, #01   ; SOURCE #DFFEC
                DEFB #09, #18, #78, #07   ; LAYOUT pal4444 12x9
                DEFB #0F, #28, #00, #08   ; SIZE
                DEFB 20, 14   ; ox,oy (signed)
                DEFB #58, #00, #0E, #01   ; SOURCE #E0058
                DEFB #09, #1C, #78, #07   ; LAYOUT pal4444 14x9
                DEFB #0F, #2E, #00, #08   ; SIZE
                DEFB 18, 13   ; ox,oy (signed)
                DEFB #D8, #00, #0E, #01   ; SOURCE #E00D8
                DEFB #0A, #1A, #78, #07   ; LAYOUT pal4444 13x10
                DEFB #10, #2A, #00, #08   ; SIZE
                DEFB 19, 14   ; ox,oy (signed)
                DEFB #5C, #01, #0E, #01   ; SOURCE #E015C
                DEFB #0A, #1E, #78, #07   ; LAYOUT pal4444 15x10
                DEFB #10, #30, #00, #08   ; SIZE
                DEFB 17, 13   ; ox,oy (signed)
                DEFB #F4, #01, #0E, #01   ; SOURCE #E01F4
                DEFB #0B, #1E, #78, #07   ; LAYOUT pal4444 15x11
                DEFB #12, #30, #00, #08   ; SIZE
                DEFB 17, 14   ; ox,oy (signed)
                DEFB 29, 2, 6
                DEFB #9C, #02, #0E, #01   ; SOURCE #E029C
                DEFB #11, #3A, #78, #07   ; LAYOUT pal4444 29x17
                DEFB #1C, #5E, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #8C, #04, #0E, #01   ; SOURCE #E048C
                DEFB #10, #3C, #78, #07   ; LAYOUT pal4444 30x16
                DEFB #1A, #60, #00, #08   ; SIZE
                DEFB 0, 16   ; ox,oy (signed)
                DEFB #6C, #06, #0E, #01   ; SOURCE #E066C
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #6C, #08, #0E, #01   ; SOURCE #E086C
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #6C, #0A, #0E, #01   ; SOURCE #E0A6C
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #6C, #0C, #0E, #01   ; SOURCE #E0C6C
                DEFB #10, #3A, #78, #07   ; LAYOUT pal4444 29x16
                DEFB #1A, #5E, #00, #08   ; SIZE
                DEFB 0, 16   ; ox,oy (signed)
                DEFB 31, 2, 6
                DEFB #3C, #0E, #0E, #01   ; SOURCE #E0E3C
                DEFB #0E, #22, #78, #07   ; LAYOUT pal4444 17x14
                DEFB #17, #38, #00, #08   ; SIZE
                DEFB 9, 0   ; ox,oy (signed)
                DEFB #2C, #0F, #0E, #01   ; SOURCE #E0F2C
                DEFB #0E, #1C, #78, #07   ; LAYOUT pal4444 14x14
                DEFB #17, #2E, #00, #08   ; SIZE
                DEFB 12, 0   ; ox,oy (signed)
                DEFB #F0, #0F, #0E, #01   ; SOURCE #E0FF0
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #A8, #10, #0E, #01   ; SOURCE #E10A8
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #60, #11, #0E, #01   ; SOURCE #E1160
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #18, #12, #0E, #01   ; SOURCE #E1218
                DEFB #0E, #1E, #78, #07   ; LAYOUT pal4444 15x14
                DEFB #17, #30, #00, #08   ; SIZE
                DEFB 8, 0   ; ox,oy (signed)
                DEFB 15, 10, 6
                DEFB #EC, #12, #0E, #01   ; SOURCE #E12EC
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #1C, #15, #0E, #01   ; SOURCE #E151C
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #4C, #17, #0E, #01   ; SOURCE #E174C
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #7C, #19, #0E, #01   ; SOURCE #E197C
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #AC, #1B, #0E, #01   ; SOURCE #E1BAC
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #DC, #1D, #0E, #01   ; SOURCE #E1DDC
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB 19, 26, 3
                DEFB #0C, #20, #0E, #01   ; SOURCE #E200C
                DEFB #05, #16, #78, #07   ; LAYOUT pal4444 11x5
                DEFB #08, #24, #00, #08   ; SIZE
                DEFB 12, 27   ; ox,oy (signed)
                DEFB #44, #20, #0E, #01   ; SOURCE #E2044
                DEFB #07, #18, #78, #07   ; LAYOUT pal4444 12x7
                DEFB #0C, #28, #00, #08   ; SIZE
                DEFB 20, 25   ; ox,oy (signed)
                DEFB #98, #20, #0E, #01   ; SOURCE #E2098
                DEFB #05, #06, #78, #07   ; LAYOUT pal4444 3x5
                DEFB #08, #0A, #00, #08   ; SIZE
                DEFB 29, 27   ; ox,oy (signed)
                DEFB 20, 26, 3
                DEFB #A8, #20, #0E, #01   ; SOURCE #E20A8
                DEFB #01, #02, #78, #07   ; LAYOUT pal4444 1x1
                DEFB #02, #04, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #AC, #20, #0E, #01   ; SOURCE #E20AC
                DEFB #04, #02, #78, #07   ; LAYOUT pal4444 1x4
                DEFB #07, #04, #00, #08   ; SIZE
                DEFB 0, 28   ; ox,oy (signed)
                DEFB #B0, #20, #0E, #01   ; SOURCE #E20B0
                DEFB #05, #12, #78, #07   ; LAYOUT pal4444 9x5
                DEFB #08, #1E, #00, #08   ; SIZE
                DEFB 0, 27   ; ox,oy (signed)
                DEFB 17, 27, 3
                DEFB #E0, #20, #0E, #01   ; SOURCE #E20E0
                DEFB #03, #1C, #78, #07   ; LAYOUT pal4444 14x3
                DEFB #05, #2E, #00, #08   ; SIZE
                DEFB 14, 29   ; ox,oy (signed)
                DEFB #0C, #21, #0E, #01   ; SOURCE #E210C
                DEFB #04, #1A, #78, #07   ; LAYOUT pal4444 13x4
                DEFB #07, #2A, #00, #08   ; SIZE
                DEFB 19, 28   ; ox,oy (signed)
                DEFB #40, #21, #0E, #01   ; SOURCE #E2140
                DEFB #02, #04, #78, #07   ; LAYOUT pal4444 2x2
                DEFB #04, #08, #00, #08   ; SIZE
                DEFB 30, 29   ; ox,oy (signed)
                DEFB 18, 27, 3
                DEFB #44, #21, #0E, #01   ; SOURCE #E2144
                DEFB #01, #02, #78, #07   ; LAYOUT pal4444 1x1
                DEFB #02, #04, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #48, #21, #0E, #01   ; SOURCE #E2148
                DEFB #02, #06, #78, #07   ; LAYOUT pal4444 3x2
                DEFB #04, #0A, #00, #08   ; SIZE
                DEFB 0, 30   ; ox,oy (signed)
                DEFB #50, #21, #0E, #01   ; SOURCE #E2150
                DEFB #03, #1C, #78, #07   ; LAYOUT pal4444 14x3
                DEFB #05, #2E, #00, #08   ; SIZE
                DEFB 0, 29   ; ox,oy (signed)
                DEFB 19, 27, 3
                DEFB #7C, #21, #0E, #01   ; SOURCE #E217C
                DEFB #20, #38, #78, #07   ; LAYOUT pal4444 28x32
                DEFB #34, #5A, #00, #08   ; SIZE
                DEFB 4, 0   ; ox,oy (signed)
                DEFB #FC, #24, #0E, #01   ; SOURCE #E24FC
                DEFB #20, #3C, #78, #07   ; LAYOUT pal4444 30x32
                DEFB #34, #60, #00, #08   ; SIZE
                DEFB 2, 0   ; ox,oy (signed)
                DEFB #BC, #28, #0E, #01   ; SOURCE #E28BC
                DEFB #20, #38, #78, #07   ; LAYOUT pal4444 28x32
                DEFB #34, #5A, #00, #08   ; SIZE
                DEFB 4, 0   ; ox,oy (signed)
                DEFB 20, 27, 3
                DEFB #3C, #2C, #0E, #01   ; SOURCE #E2C3C
                DEFB #1E, #22, #78, #07   ; LAYOUT pal4444 17x30
                DEFB #30, #38, #00, #08   ; SIZE
                DEFB 0, 2   ; ox,oy (signed)
                DEFB #3C, #2E, #0E, #01   ; SOURCE #E2E3C
                DEFB #15, #26, #78, #07   ; LAYOUT pal4444 19x21
                DEFB #22, #3E, #00, #08   ; SIZE
                DEFB 0, 11   ; ox,oy (signed)
                DEFB #CC, #2F, #0E, #01   ; SOURCE #E2FCC
                DEFB #20, #22, #78, #07   ; LAYOUT pal4444 17x32
                DEFB #34, #38, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 17, 28, 3
                DEFB #EC, #31, #0E, #01   ; SOURCE #E31EC
                DEFB #0B, #1C, #78, #07   ; LAYOUT pal4444 14x11
                DEFB #12, #2E, #00, #08   ; SIZE
                DEFB 18, 0   ; ox,oy (signed)
                DEFB #88, #32, #0E, #01   ; SOURCE #E3288
                DEFB #0B, #1A, #78, #07   ; LAYOUT pal4444 13x11
                DEFB #12, #2A, #00, #08   ; SIZE
                DEFB 19, 0   ; ox,oy (signed)
                DEFB #18, #33, #0E, #01   ; SOURCE #E3318
                DEFB #07, #24, #78, #07   ; LAYOUT pal4444 18x7
                DEFB #0C, #3A, #00, #08   ; SIZE
                DEFB 14, 0   ; ox,oy (signed)
                DEFB 18, 28, 3
                DEFB #98, #33, #0E, #01   ; SOURCE #E3398
                DEFB #12, #40, #78, #07   ; LAYOUT pal4444 32x18
                DEFB #1D, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #D8, #35, #0E, #01   ; SOURCE #E35D8
                DEFB #12, #40, #78, #07   ; LAYOUT pal4444 32x18
                DEFB #1D, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #18, #38, #0E, #01   ; SOURCE #E3818
                DEFB #13, #40, #78, #07   ; LAYOUT pal4444 32x19
                DEFB #1F, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 19, 28, 3
                DEFB #78, #3A, #0E, #01   ; SOURCE #E3A78
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #98, #3D, #0E, #01   ; SOURCE #E3D98
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #B8, #40, #0E, #01   ; SOURCE #E40B8
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 20, 28, 3
                DEFB #D8, #43, #0E, #01   ; SOURCE #E43D8
                DEFB #08, #14, #78, #07   ; LAYOUT pal4444 10x8
                DEFB #0D, #20, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #28, #44, #0E, #01   ; SOURCE #E4428
                DEFB #08, #08, #78, #07   ; LAYOUT pal4444 4x8
                DEFB #0D, #0E, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #48, #44, #0E, #01   ; SOURCE #E4448
                DEFB #08, #18, #78, #07   ; LAYOUT pal4444 12x8
                DEFB #0D, #28, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 28, 29, 6
                DEFB #A8, #44, #0E, #01   ; SOURCE #E44A8
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #14, #45, #0E, #01   ; SOURCE #E4514
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #80, #45, #0E, #01   ; SOURCE #E4580
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #EC, #45, #0E, #01   ; SOURCE #E45EC
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #58, #46, #0E, #01   ; SOURCE #E4658
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #C4, #46, #0E, #01   ; SOURCE #E46C4
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB 29, 29, 6
                DEFB #30, #47, #0E, #01   ; SOURCE #E4730
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #A8, #48, #0E, #01   ; SOURCE #E48A8
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #20, #4A, #0E, #01   ; SOURCE #E4A20
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #98, #4B, #0E, #01   ; SOURCE #E4B98
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #10, #4D, #0E, #01   ; SOURCE #E4D10
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #88, #4E, #0E, #01   ; SOURCE #E4E88
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB 28, 30, 6
                DEFB #00, #50, #0E, #01   ; SOURCE #E5000
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #AC, #51, #0E, #01   ; SOURCE #E51AC
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #58, #53, #0E, #01   ; SOURCE #E5358
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #04, #55, #0E, #01   ; SOURCE #E5504
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #B0, #56, #0E, #01   ; SOURCE #E56B0
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #5C, #58, #0E, #01   ; SOURCE #E585C
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB 29, 30, 6
                DEFB #08, #5A, #0E, #01   ; SOURCE #E5A08
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #AC, #5C, #0E, #01   ; SOURCE #E5CAC
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #50, #5F, #0E, #01   ; SOURCE #E5F50
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #F4, #61, #0E, #01   ; SOURCE #E61F4
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #98, #64, #0E, #01   ; SOURCE #E6498
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #3C, #67, #0E, #01   ; SOURCE #E673C
                DEFB #1A, #36, #78, #07   ; LAYOUT pal4444 27x26
                DEFB #2A, #58, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
MAP_ANIM_ENTRY_HEADER   EQU 3
MAP_ANIM_FRAME_SIZE     EQU 14
