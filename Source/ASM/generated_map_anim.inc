; Сгенерировано Source/Tools/viewport_pack.py — анимация adventure-объектов.
; Кадры-дельты (PALETTED4444) поверх базы; формула fheroes2:
;   frame = base + (MapAnimPhase % N) + 1; шаг ~250мс (MAPS_DELAY).
MAP_ANIM_COUNT          EQU 18
MAP_ANIM_PALETTE_RAMG   EQU OBJECT_PALETTE_RAMG
MapAnimTable:
                DEFB 28, 2, 6
                DEFB #8C, #E2, #0C, #01   ; SOURCE #CE28C
                DEFB #07, #18, #78, #07   ; LAYOUT pal4444 12x7
                DEFB #0C, #28, #00, #08   ; SIZE
                DEFB 20, 14   ; ox,oy (signed)
                DEFB #E0, #E2, #0C, #01   ; SOURCE #CE2E0
                DEFB #09, #18, #78, #07   ; LAYOUT pal4444 12x9
                DEFB #0F, #28, #00, #08   ; SIZE
                DEFB 20, 14   ; ox,oy (signed)
                DEFB #4C, #E3, #0C, #01   ; SOURCE #CE34C
                DEFB #09, #1C, #78, #07   ; LAYOUT pal4444 14x9
                DEFB #0F, #2E, #00, #08   ; SIZE
                DEFB 18, 13   ; ox,oy (signed)
                DEFB #CC, #E3, #0C, #01   ; SOURCE #CE3CC
                DEFB #0A, #1A, #78, #07   ; LAYOUT pal4444 13x10
                DEFB #10, #2A, #00, #08   ; SIZE
                DEFB 19, 14   ; ox,oy (signed)
                DEFB #50, #E4, #0C, #01   ; SOURCE #CE450
                DEFB #0A, #1E, #78, #07   ; LAYOUT pal4444 15x10
                DEFB #10, #30, #00, #08   ; SIZE
                DEFB 17, 13   ; ox,oy (signed)
                DEFB #E8, #E4, #0C, #01   ; SOURCE #CE4E8
                DEFB #0B, #1E, #78, #07   ; LAYOUT pal4444 15x11
                DEFB #12, #30, #00, #08   ; SIZE
                DEFB 17, 14   ; ox,oy (signed)
                DEFB 29, 2, 6
                DEFB #90, #E5, #0C, #01   ; SOURCE #CE590
                DEFB #11, #3A, #78, #07   ; LAYOUT pal4444 29x17
                DEFB #1C, #5E, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #80, #E7, #0C, #01   ; SOURCE #CE780
                DEFB #10, #3C, #78, #07   ; LAYOUT pal4444 30x16
                DEFB #1A, #60, #00, #08   ; SIZE
                DEFB 0, 16   ; ox,oy (signed)
                DEFB #60, #E9, #0C, #01   ; SOURCE #CE960
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #60, #EB, #0C, #01   ; SOURCE #CEB60
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #60, #ED, #0C, #01   ; SOURCE #CED60
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #60, #EF, #0C, #01   ; SOURCE #CEF60
                DEFB #10, #3A, #78, #07   ; LAYOUT pal4444 29x16
                DEFB #1A, #5E, #00, #08   ; SIZE
                DEFB 0, 16   ; ox,oy (signed)
                DEFB 31, 2, 6
                DEFB #30, #F1, #0C, #01   ; SOURCE #CF130
                DEFB #0E, #22, #78, #07   ; LAYOUT pal4444 17x14
                DEFB #17, #38, #00, #08   ; SIZE
                DEFB 9, 0   ; ox,oy (signed)
                DEFB #20, #F2, #0C, #01   ; SOURCE #CF220
                DEFB #0E, #1C, #78, #07   ; LAYOUT pal4444 14x14
                DEFB #17, #2E, #00, #08   ; SIZE
                DEFB 12, 0   ; ox,oy (signed)
                DEFB #E4, #F2, #0C, #01   ; SOURCE #CF2E4
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #9C, #F3, #0C, #01   ; SOURCE #CF39C
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #54, #F4, #0C, #01   ; SOURCE #CF454
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #0C, #F5, #0C, #01   ; SOURCE #CF50C
                DEFB #0E, #1E, #78, #07   ; LAYOUT pal4444 15x14
                DEFB #17, #30, #00, #08   ; SIZE
                DEFB 8, 0   ; ox,oy (signed)
                DEFB 15, 10, 6
                DEFB #E0, #F5, #0C, #01   ; SOURCE #CF5E0
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #10, #F8, #0C, #01   ; SOURCE #CF810
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #40, #FA, #0C, #01   ; SOURCE #CFA40
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #70, #FC, #0C, #01   ; SOURCE #CFC70
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #A0, #FE, #0C, #01   ; SOURCE #CFEA0
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #D0, #00, #0D, #01   ; SOURCE #D00D0
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB 19, 26, 3
                DEFB #00, #03, #0D, #01   ; SOURCE #D0300
                DEFB #05, #16, #78, #07   ; LAYOUT pal4444 11x5
                DEFB #08, #24, #00, #08   ; SIZE
                DEFB 12, 27   ; ox,oy (signed)
                DEFB #38, #03, #0D, #01   ; SOURCE #D0338
                DEFB #07, #18, #78, #07   ; LAYOUT pal4444 12x7
                DEFB #0C, #28, #00, #08   ; SIZE
                DEFB 20, 25   ; ox,oy (signed)
                DEFB #8C, #03, #0D, #01   ; SOURCE #D038C
                DEFB #05, #06, #78, #07   ; LAYOUT pal4444 3x5
                DEFB #08, #0A, #00, #08   ; SIZE
                DEFB 29, 27   ; ox,oy (signed)
                DEFB 20, 26, 3
                DEFB #9C, #03, #0D, #01   ; SOURCE #D039C
                DEFB #01, #02, #78, #07   ; LAYOUT pal4444 1x1
                DEFB #02, #04, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #A0, #03, #0D, #01   ; SOURCE #D03A0
                DEFB #04, #02, #78, #07   ; LAYOUT pal4444 1x4
                DEFB #07, #04, #00, #08   ; SIZE
                DEFB 0, 28   ; ox,oy (signed)
                DEFB #A4, #03, #0D, #01   ; SOURCE #D03A4
                DEFB #05, #12, #78, #07   ; LAYOUT pal4444 9x5
                DEFB #08, #1E, #00, #08   ; SIZE
                DEFB 0, 27   ; ox,oy (signed)
                DEFB 17, 27, 3
                DEFB #D4, #03, #0D, #01   ; SOURCE #D03D4
                DEFB #03, #1C, #78, #07   ; LAYOUT pal4444 14x3
                DEFB #05, #2E, #00, #08   ; SIZE
                DEFB 14, 29   ; ox,oy (signed)
                DEFB #00, #04, #0D, #01   ; SOURCE #D0400
                DEFB #04, #1A, #78, #07   ; LAYOUT pal4444 13x4
                DEFB #07, #2A, #00, #08   ; SIZE
                DEFB 19, 28   ; ox,oy (signed)
                DEFB #34, #04, #0D, #01   ; SOURCE #D0434
                DEFB #02, #04, #78, #07   ; LAYOUT pal4444 2x2
                DEFB #04, #08, #00, #08   ; SIZE
                DEFB 30, 29   ; ox,oy (signed)
                DEFB 18, 27, 3
                DEFB #38, #04, #0D, #01   ; SOURCE #D0438
                DEFB #01, #02, #78, #07   ; LAYOUT pal4444 1x1
                DEFB #02, #04, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #3C, #04, #0D, #01   ; SOURCE #D043C
                DEFB #02, #06, #78, #07   ; LAYOUT pal4444 3x2
                DEFB #04, #0A, #00, #08   ; SIZE
                DEFB 0, 30   ; ox,oy (signed)
                DEFB #44, #04, #0D, #01   ; SOURCE #D0444
                DEFB #03, #1C, #78, #07   ; LAYOUT pal4444 14x3
                DEFB #05, #2E, #00, #08   ; SIZE
                DEFB 0, 29   ; ox,oy (signed)
                DEFB 19, 27, 3
                DEFB #70, #04, #0D, #01   ; SOURCE #D0470
                DEFB #20, #38, #78, #07   ; LAYOUT pal4444 28x32
                DEFB #34, #5A, #00, #08   ; SIZE
                DEFB 4, 0   ; ox,oy (signed)
                DEFB #F0, #07, #0D, #01   ; SOURCE #D07F0
                DEFB #20, #3C, #78, #07   ; LAYOUT pal4444 30x32
                DEFB #34, #60, #00, #08   ; SIZE
                DEFB 2, 0   ; ox,oy (signed)
                DEFB #B0, #0B, #0D, #01   ; SOURCE #D0BB0
                DEFB #20, #38, #78, #07   ; LAYOUT pal4444 28x32
                DEFB #34, #5A, #00, #08   ; SIZE
                DEFB 4, 0   ; ox,oy (signed)
                DEFB 20, 27, 3
                DEFB #30, #0F, #0D, #01   ; SOURCE #D0F30
                DEFB #1E, #22, #78, #07   ; LAYOUT pal4444 17x30
                DEFB #30, #38, #00, #08   ; SIZE
                DEFB 0, 2   ; ox,oy (signed)
                DEFB #30, #11, #0D, #01   ; SOURCE #D1130
                DEFB #15, #26, #78, #07   ; LAYOUT pal4444 19x21
                DEFB #22, #3E, #00, #08   ; SIZE
                DEFB 0, 11   ; ox,oy (signed)
                DEFB #C0, #12, #0D, #01   ; SOURCE #D12C0
                DEFB #20, #22, #78, #07   ; LAYOUT pal4444 17x32
                DEFB #34, #38, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 17, 28, 3
                DEFB #E0, #14, #0D, #01   ; SOURCE #D14E0
                DEFB #0B, #1C, #78, #07   ; LAYOUT pal4444 14x11
                DEFB #12, #2E, #00, #08   ; SIZE
                DEFB 18, 0   ; ox,oy (signed)
                DEFB #7C, #15, #0D, #01   ; SOURCE #D157C
                DEFB #0B, #1A, #78, #07   ; LAYOUT pal4444 13x11
                DEFB #12, #2A, #00, #08   ; SIZE
                DEFB 19, 0   ; ox,oy (signed)
                DEFB #0C, #16, #0D, #01   ; SOURCE #D160C
                DEFB #07, #24, #78, #07   ; LAYOUT pal4444 18x7
                DEFB #0C, #3A, #00, #08   ; SIZE
                DEFB 14, 0   ; ox,oy (signed)
                DEFB 18, 28, 3
                DEFB #8C, #16, #0D, #01   ; SOURCE #D168C
                DEFB #12, #40, #78, #07   ; LAYOUT pal4444 32x18
                DEFB #1D, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #CC, #18, #0D, #01   ; SOURCE #D18CC
                DEFB #12, #40, #78, #07   ; LAYOUT pal4444 32x18
                DEFB #1D, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #0C, #1B, #0D, #01   ; SOURCE #D1B0C
                DEFB #13, #40, #78, #07   ; LAYOUT pal4444 32x19
                DEFB #1F, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 19, 28, 3
                DEFB #6C, #1D, #0D, #01   ; SOURCE #D1D6C
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #8C, #20, #0D, #01   ; SOURCE #D208C
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #AC, #23, #0D, #01   ; SOURCE #D23AC
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 20, 28, 3
                DEFB #CC, #26, #0D, #01   ; SOURCE #D26CC
                DEFB #08, #14, #78, #07   ; LAYOUT pal4444 10x8
                DEFB #0D, #20, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #1C, #27, #0D, #01   ; SOURCE #D271C
                DEFB #08, #08, #78, #07   ; LAYOUT pal4444 4x8
                DEFB #0D, #0E, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #3C, #27, #0D, #01   ; SOURCE #D273C
                DEFB #08, #18, #78, #07   ; LAYOUT pal4444 12x8
                DEFB #0D, #28, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 28, 29, 6
                DEFB #9C, #27, #0D, #01   ; SOURCE #D279C
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #08, #28, #0D, #01   ; SOURCE #D2808
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #74, #28, #0D, #01   ; SOURCE #D2874
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #E0, #28, #0D, #01   ; SOURCE #D28E0
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #4C, #29, #0D, #01   ; SOURCE #D294C
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #B8, #29, #0D, #01   ; SOURCE #D29B8
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB 29, 29, 6
                DEFB #24, #2A, #0D, #01   ; SOURCE #D2A24
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #9C, #2B, #0D, #01   ; SOURCE #D2B9C
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #14, #2D, #0D, #01   ; SOURCE #D2D14
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #8C, #2E, #0D, #01   ; SOURCE #D2E8C
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #04, #30, #0D, #01   ; SOURCE #D3004
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #7C, #31, #0D, #01   ; SOURCE #D317C
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB 28, 30, 6
                DEFB #F4, #32, #0D, #01   ; SOURCE #D32F4
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #A0, #34, #0D, #01   ; SOURCE #D34A0
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #4C, #36, #0D, #01   ; SOURCE #D364C
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #F8, #37, #0D, #01   ; SOURCE #D37F8
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #A4, #39, #0D, #01   ; SOURCE #D39A4
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #50, #3B, #0D, #01   ; SOURCE #D3B50
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB 29, 30, 6
                DEFB #FC, #3C, #0D, #01   ; SOURCE #D3CFC
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #A0, #3F, #0D, #01   ; SOURCE #D3FA0
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #44, #42, #0D, #01   ; SOURCE #D4244
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #E8, #44, #0D, #01   ; SOURCE #D44E8
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #8C, #47, #0D, #01   ; SOURCE #D478C
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #30, #4A, #0D, #01   ; SOURCE #D4A30
                DEFB #1A, #36, #78, #07   ; LAYOUT pal4444 27x26
                DEFB #2A, #58, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
MAP_ANIM_ENTRY_HEADER   EQU 3
MAP_ANIM_FRAME_SIZE     EQU 14
