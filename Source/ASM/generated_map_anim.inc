; Сгенерировано Source/Tools/viewport_pack.py — анимация adventure-объектов.
; Кадры-дельты (PALETTED4444) поверх базы; формула fheroes2:
;   frame = base + (MapAnimPhase % N) + 1; шаг ~250мс (MAPS_DELAY).
MAP_ANIM_COUNT          EQU 18
MAP_ANIM_PALETTE_RAMG   EQU OBJECT_PALETTE_RAMG
MapAnimTable:
                DEFB 28, 2, 6
                DEFB #E0, #F3, #0D, #01   ; SOURCE #DF3E0
                DEFB #07, #18, #78, #07   ; LAYOUT pal4444 12x7
                DEFB #0C, #28, #00, #08   ; SIZE
                DEFB 20, 14   ; ox,oy (signed)
                DEFB #34, #F4, #0D, #01   ; SOURCE #DF434
                DEFB #09, #18, #78, #07   ; LAYOUT pal4444 12x9
                DEFB #0F, #28, #00, #08   ; SIZE
                DEFB 20, 14   ; ox,oy (signed)
                DEFB #A0, #F4, #0D, #01   ; SOURCE #DF4A0
                DEFB #09, #1C, #78, #07   ; LAYOUT pal4444 14x9
                DEFB #0F, #2E, #00, #08   ; SIZE
                DEFB 18, 13   ; ox,oy (signed)
                DEFB #20, #F5, #0D, #01   ; SOURCE #DF520
                DEFB #0A, #1A, #78, #07   ; LAYOUT pal4444 13x10
                DEFB #10, #2A, #00, #08   ; SIZE
                DEFB 19, 14   ; ox,oy (signed)
                DEFB #A4, #F5, #0D, #01   ; SOURCE #DF5A4
                DEFB #0A, #1E, #78, #07   ; LAYOUT pal4444 15x10
                DEFB #10, #30, #00, #08   ; SIZE
                DEFB 17, 13   ; ox,oy (signed)
                DEFB #3C, #F6, #0D, #01   ; SOURCE #DF63C
                DEFB #0B, #1E, #78, #07   ; LAYOUT pal4444 15x11
                DEFB #12, #30, #00, #08   ; SIZE
                DEFB 17, 14   ; ox,oy (signed)
                DEFB 29, 2, 6
                DEFB #E4, #F6, #0D, #01   ; SOURCE #DF6E4
                DEFB #11, #3A, #78, #07   ; LAYOUT pal4444 29x17
                DEFB #1C, #5E, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #D4, #F8, #0D, #01   ; SOURCE #DF8D4
                DEFB #10, #3C, #78, #07   ; LAYOUT pal4444 30x16
                DEFB #1A, #60, #00, #08   ; SIZE
                DEFB 0, 16   ; ox,oy (signed)
                DEFB #B4, #FA, #0D, #01   ; SOURCE #DFAB4
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #B4, #FC, #0D, #01   ; SOURCE #DFCB4
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #B4, #FE, #0D, #01   ; SOURCE #DFEB4
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #B4, #00, #0E, #01   ; SOURCE #E00B4
                DEFB #10, #3A, #78, #07   ; LAYOUT pal4444 29x16
                DEFB #1A, #5E, #00, #08   ; SIZE
                DEFB 0, 16   ; ox,oy (signed)
                DEFB 31, 2, 6
                DEFB #84, #02, #0E, #01   ; SOURCE #E0284
                DEFB #0E, #22, #78, #07   ; LAYOUT pal4444 17x14
                DEFB #17, #38, #00, #08   ; SIZE
                DEFB 9, 0   ; ox,oy (signed)
                DEFB #74, #03, #0E, #01   ; SOURCE #E0374
                DEFB #0E, #1C, #78, #07   ; LAYOUT pal4444 14x14
                DEFB #17, #2E, #00, #08   ; SIZE
                DEFB 12, 0   ; ox,oy (signed)
                DEFB #38, #04, #0E, #01   ; SOURCE #E0438
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #F0, #04, #0E, #01   ; SOURCE #E04F0
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #A8, #05, #0E, #01   ; SOURCE #E05A8
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #60, #06, #0E, #01   ; SOURCE #E0660
                DEFB #0E, #1E, #78, #07   ; LAYOUT pal4444 15x14
                DEFB #17, #30, #00, #08   ; SIZE
                DEFB 8, 0   ; ox,oy (signed)
                DEFB 15, 10, 6
                DEFB #34, #07, #0E, #01   ; SOURCE #E0734
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #64, #09, #0E, #01   ; SOURCE #E0964
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #94, #0B, #0E, #01   ; SOURCE #E0B94
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #C4, #0D, #0E, #01   ; SOURCE #E0DC4
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #F4, #0F, #0E, #01   ; SOURCE #E0FF4
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #24, #12, #0E, #01   ; SOURCE #E1224
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB 19, 26, 3
                DEFB #54, #14, #0E, #01   ; SOURCE #E1454
                DEFB #05, #16, #78, #07   ; LAYOUT pal4444 11x5
                DEFB #08, #24, #00, #08   ; SIZE
                DEFB 12, 27   ; ox,oy (signed)
                DEFB #8C, #14, #0E, #01   ; SOURCE #E148C
                DEFB #07, #18, #78, #07   ; LAYOUT pal4444 12x7
                DEFB #0C, #28, #00, #08   ; SIZE
                DEFB 20, 25   ; ox,oy (signed)
                DEFB #E0, #14, #0E, #01   ; SOURCE #E14E0
                DEFB #05, #06, #78, #07   ; LAYOUT pal4444 3x5
                DEFB #08, #0A, #00, #08   ; SIZE
                DEFB 29, 27   ; ox,oy (signed)
                DEFB 20, 26, 3
                DEFB #F0, #14, #0E, #01   ; SOURCE #E14F0
                DEFB #01, #02, #78, #07   ; LAYOUT pal4444 1x1
                DEFB #02, #04, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #F4, #14, #0E, #01   ; SOURCE #E14F4
                DEFB #04, #02, #78, #07   ; LAYOUT pal4444 1x4
                DEFB #07, #04, #00, #08   ; SIZE
                DEFB 0, 28   ; ox,oy (signed)
                DEFB #F8, #14, #0E, #01   ; SOURCE #E14F8
                DEFB #05, #12, #78, #07   ; LAYOUT pal4444 9x5
                DEFB #08, #1E, #00, #08   ; SIZE
                DEFB 0, 27   ; ox,oy (signed)
                DEFB 17, 27, 3
                DEFB #28, #15, #0E, #01   ; SOURCE #E1528
                DEFB #03, #1C, #78, #07   ; LAYOUT pal4444 14x3
                DEFB #05, #2E, #00, #08   ; SIZE
                DEFB 14, 29   ; ox,oy (signed)
                DEFB #54, #15, #0E, #01   ; SOURCE #E1554
                DEFB #04, #1A, #78, #07   ; LAYOUT pal4444 13x4
                DEFB #07, #2A, #00, #08   ; SIZE
                DEFB 19, 28   ; ox,oy (signed)
                DEFB #88, #15, #0E, #01   ; SOURCE #E1588
                DEFB #02, #04, #78, #07   ; LAYOUT pal4444 2x2
                DEFB #04, #08, #00, #08   ; SIZE
                DEFB 30, 29   ; ox,oy (signed)
                DEFB 18, 27, 3
                DEFB #8C, #15, #0E, #01   ; SOURCE #E158C
                DEFB #01, #02, #78, #07   ; LAYOUT pal4444 1x1
                DEFB #02, #04, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #90, #15, #0E, #01   ; SOURCE #E1590
                DEFB #02, #06, #78, #07   ; LAYOUT pal4444 3x2
                DEFB #04, #0A, #00, #08   ; SIZE
                DEFB 0, 30   ; ox,oy (signed)
                DEFB #98, #15, #0E, #01   ; SOURCE #E1598
                DEFB #03, #1C, #78, #07   ; LAYOUT pal4444 14x3
                DEFB #05, #2E, #00, #08   ; SIZE
                DEFB 0, 29   ; ox,oy (signed)
                DEFB 19, 27, 3
                DEFB #C4, #15, #0E, #01   ; SOURCE #E15C4
                DEFB #20, #38, #78, #07   ; LAYOUT pal4444 28x32
                DEFB #34, #5A, #00, #08   ; SIZE
                DEFB 4, 0   ; ox,oy (signed)
                DEFB #44, #19, #0E, #01   ; SOURCE #E1944
                DEFB #20, #3C, #78, #07   ; LAYOUT pal4444 30x32
                DEFB #34, #60, #00, #08   ; SIZE
                DEFB 2, 0   ; ox,oy (signed)
                DEFB #04, #1D, #0E, #01   ; SOURCE #E1D04
                DEFB #20, #38, #78, #07   ; LAYOUT pal4444 28x32
                DEFB #34, #5A, #00, #08   ; SIZE
                DEFB 4, 0   ; ox,oy (signed)
                DEFB 20, 27, 3
                DEFB #84, #20, #0E, #01   ; SOURCE #E2084
                DEFB #1E, #22, #78, #07   ; LAYOUT pal4444 17x30
                DEFB #30, #38, #00, #08   ; SIZE
                DEFB 0, 2   ; ox,oy (signed)
                DEFB #84, #22, #0E, #01   ; SOURCE #E2284
                DEFB #15, #26, #78, #07   ; LAYOUT pal4444 19x21
                DEFB #22, #3E, #00, #08   ; SIZE
                DEFB 0, 11   ; ox,oy (signed)
                DEFB #14, #24, #0E, #01   ; SOURCE #E2414
                DEFB #20, #22, #78, #07   ; LAYOUT pal4444 17x32
                DEFB #34, #38, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 17, 28, 3
                DEFB #34, #26, #0E, #01   ; SOURCE #E2634
                DEFB #0B, #1C, #78, #07   ; LAYOUT pal4444 14x11
                DEFB #12, #2E, #00, #08   ; SIZE
                DEFB 18, 0   ; ox,oy (signed)
                DEFB #D0, #26, #0E, #01   ; SOURCE #E26D0
                DEFB #0B, #1A, #78, #07   ; LAYOUT pal4444 13x11
                DEFB #12, #2A, #00, #08   ; SIZE
                DEFB 19, 0   ; ox,oy (signed)
                DEFB #60, #27, #0E, #01   ; SOURCE #E2760
                DEFB #07, #24, #78, #07   ; LAYOUT pal4444 18x7
                DEFB #0C, #3A, #00, #08   ; SIZE
                DEFB 14, 0   ; ox,oy (signed)
                DEFB 18, 28, 3
                DEFB #E0, #27, #0E, #01   ; SOURCE #E27E0
                DEFB #12, #40, #78, #07   ; LAYOUT pal4444 32x18
                DEFB #1D, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #20, #2A, #0E, #01   ; SOURCE #E2A20
                DEFB #12, #40, #78, #07   ; LAYOUT pal4444 32x18
                DEFB #1D, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #60, #2C, #0E, #01   ; SOURCE #E2C60
                DEFB #13, #40, #78, #07   ; LAYOUT pal4444 32x19
                DEFB #1F, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 19, 28, 3
                DEFB #C0, #2E, #0E, #01   ; SOURCE #E2EC0
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #E0, #31, #0E, #01   ; SOURCE #E31E0
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #00, #35, #0E, #01   ; SOURCE #E3500
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 20, 28, 3
                DEFB #20, #38, #0E, #01   ; SOURCE #E3820
                DEFB #08, #14, #78, #07   ; LAYOUT pal4444 10x8
                DEFB #0D, #20, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #70, #38, #0E, #01   ; SOURCE #E3870
                DEFB #08, #08, #78, #07   ; LAYOUT pal4444 4x8
                DEFB #0D, #0E, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #90, #38, #0E, #01   ; SOURCE #E3890
                DEFB #08, #18, #78, #07   ; LAYOUT pal4444 12x8
                DEFB #0D, #28, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 28, 29, 6
                DEFB #F0, #38, #0E, #01   ; SOURCE #E38F0
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #5C, #39, #0E, #01   ; SOURCE #E395C
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #C8, #39, #0E, #01   ; SOURCE #E39C8
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #34, #3A, #0E, #01   ; SOURCE #E3A34
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #A0, #3A, #0E, #01   ; SOURCE #E3AA0
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #0C, #3B, #0E, #01   ; SOURCE #E3B0C
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB 29, 29, 6
                DEFB #78, #3B, #0E, #01   ; SOURCE #E3B78
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #F0, #3C, #0E, #01   ; SOURCE #E3CF0
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #68, #3E, #0E, #01   ; SOURCE #E3E68
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #E0, #3F, #0E, #01   ; SOURCE #E3FE0
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #58, #41, #0E, #01   ; SOURCE #E4158
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #D0, #42, #0E, #01   ; SOURCE #E42D0
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB 28, 30, 6
                DEFB #48, #44, #0E, #01   ; SOURCE #E4448
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #F4, #45, #0E, #01   ; SOURCE #E45F4
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #A0, #47, #0E, #01   ; SOURCE #E47A0
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #4C, #49, #0E, #01   ; SOURCE #E494C
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #F8, #4A, #0E, #01   ; SOURCE #E4AF8
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #A4, #4C, #0E, #01   ; SOURCE #E4CA4
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB 29, 30, 6
                DEFB #50, #4E, #0E, #01   ; SOURCE #E4E50
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #F4, #50, #0E, #01   ; SOURCE #E50F4
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #98, #53, #0E, #01   ; SOURCE #E5398
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #3C, #56, #0E, #01   ; SOURCE #E563C
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #E0, #58, #0E, #01   ; SOURCE #E58E0
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #84, #5B, #0E, #01   ; SOURCE #E5B84
                DEFB #1A, #36, #78, #07   ; LAYOUT pal4444 27x26
                DEFB #2A, #58, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
MAP_ANIM_ENTRY_HEADER   EQU 3
MAP_ANIM_FRAME_SIZE     EQU 14
