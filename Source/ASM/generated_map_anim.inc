; Сгенерировано Source/Tools/viewport_pack.py — анимация adventure-объектов.
; Кадры-дельты (PALETTED4444) поверх базы; формула fheroes2:
;   frame = base + (MapAnimPhase % N) + 1; шаг ~250мс (MAPS_DELAY).
MAP_ANIM_COUNT          EQU 18
MAP_ANIM_PALETTE_RAMG   EQU OBJECT_PALETTE_RAMG
MapAnimTable:
                DEFB 28, 2, 6
                DEFB #0C, #0B, #0D, #01   ; SOURCE #D0B0C
                DEFB #07, #18, #78, #07   ; LAYOUT pal4444 12x7
                DEFB #0C, #28, #00, #08   ; SIZE
                DEFB 20, 14   ; ox,oy (signed)
                DEFB #60, #0B, #0D, #01   ; SOURCE #D0B60
                DEFB #09, #18, #78, #07   ; LAYOUT pal4444 12x9
                DEFB #0F, #28, #00, #08   ; SIZE
                DEFB 20, 14   ; ox,oy (signed)
                DEFB #CC, #0B, #0D, #01   ; SOURCE #D0BCC
                DEFB #09, #1C, #78, #07   ; LAYOUT pal4444 14x9
                DEFB #0F, #2E, #00, #08   ; SIZE
                DEFB 18, 13   ; ox,oy (signed)
                DEFB #4C, #0C, #0D, #01   ; SOURCE #D0C4C
                DEFB #0A, #1A, #78, #07   ; LAYOUT pal4444 13x10
                DEFB #10, #2A, #00, #08   ; SIZE
                DEFB 19, 14   ; ox,oy (signed)
                DEFB #D0, #0C, #0D, #01   ; SOURCE #D0CD0
                DEFB #0A, #1E, #78, #07   ; LAYOUT pal4444 15x10
                DEFB #10, #30, #00, #08   ; SIZE
                DEFB 17, 13   ; ox,oy (signed)
                DEFB #68, #0D, #0D, #01   ; SOURCE #D0D68
                DEFB #0B, #1E, #78, #07   ; LAYOUT pal4444 15x11
                DEFB #12, #30, #00, #08   ; SIZE
                DEFB 17, 14   ; ox,oy (signed)
                DEFB 29, 2, 6
                DEFB #10, #0E, #0D, #01   ; SOURCE #D0E10
                DEFB #11, #3A, #78, #07   ; LAYOUT pal4444 29x17
                DEFB #1C, #5E, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #00, #10, #0D, #01   ; SOURCE #D1000
                DEFB #10, #3C, #78, #07   ; LAYOUT pal4444 30x16
                DEFB #1A, #60, #00, #08   ; SIZE
                DEFB 0, 16   ; ox,oy (signed)
                DEFB #E0, #11, #0D, #01   ; SOURCE #D11E0
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #E0, #13, #0D, #01   ; SOURCE #D13E0
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #E0, #15, #0D, #01   ; SOURCE #D15E0
                DEFB #11, #3C, #78, #07   ; LAYOUT pal4444 30x17
                DEFB #1C, #60, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #E0, #17, #0D, #01   ; SOURCE #D17E0
                DEFB #10, #3A, #78, #07   ; LAYOUT pal4444 29x16
                DEFB #1A, #5E, #00, #08   ; SIZE
                DEFB 0, 16   ; ox,oy (signed)
                DEFB 31, 2, 6
                DEFB #B0, #19, #0D, #01   ; SOURCE #D19B0
                DEFB #0E, #22, #78, #07   ; LAYOUT pal4444 17x14
                DEFB #17, #38, #00, #08   ; SIZE
                DEFB 9, 0   ; ox,oy (signed)
                DEFB #A0, #1A, #0D, #01   ; SOURCE #D1AA0
                DEFB #0E, #1C, #78, #07   ; LAYOUT pal4444 14x14
                DEFB #17, #2E, #00, #08   ; SIZE
                DEFB 12, 0   ; ox,oy (signed)
                DEFB #64, #1B, #0D, #01   ; SOURCE #D1B64
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #1C, #1C, #0D, #01   ; SOURCE #D1C1C
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #D4, #1C, #0D, #01   ; SOURCE #D1CD4
                DEFB #0E, #1A, #78, #07   ; LAYOUT pal4444 13x14
                DEFB #17, #2A, #00, #08   ; SIZE
                DEFB 11, 0   ; ox,oy (signed)
                DEFB #8C, #1D, #0D, #01   ; SOURCE #D1D8C
                DEFB #0E, #1E, #78, #07   ; LAYOUT pal4444 15x14
                DEFB #17, #30, #00, #08   ; SIZE
                DEFB 8, 0   ; ox,oy (signed)
                DEFB 15, 10, 6
                DEFB #60, #1E, #0D, #01   ; SOURCE #D1E60
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #90, #20, #0D, #01   ; SOURCE #D2090
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #C0, #22, #0D, #01   ; SOURCE #D22C0
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #F0, #24, #0D, #01   ; SOURCE #D24F0
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #20, #27, #0D, #01   ; SOURCE #D2720
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB #50, #29, #0D, #01   ; SOURCE #D2950
                DEFB #1C, #28, #78, #07   ; LAYOUT pal4444 20x28
                DEFB #2D, #40, #00, #08   ; SIZE
                DEFB 1, 0   ; ox,oy (signed)
                DEFB 19, 26, 3
                DEFB #80, #2B, #0D, #01   ; SOURCE #D2B80
                DEFB #05, #16, #78, #07   ; LAYOUT pal4444 11x5
                DEFB #08, #24, #00, #08   ; SIZE
                DEFB 12, 27   ; ox,oy (signed)
                DEFB #B8, #2B, #0D, #01   ; SOURCE #D2BB8
                DEFB #07, #18, #78, #07   ; LAYOUT pal4444 12x7
                DEFB #0C, #28, #00, #08   ; SIZE
                DEFB 20, 25   ; ox,oy (signed)
                DEFB #0C, #2C, #0D, #01   ; SOURCE #D2C0C
                DEFB #05, #06, #78, #07   ; LAYOUT pal4444 3x5
                DEFB #08, #0A, #00, #08   ; SIZE
                DEFB 29, 27   ; ox,oy (signed)
                DEFB 20, 26, 3
                DEFB #1C, #2C, #0D, #01   ; SOURCE #D2C1C
                DEFB #01, #02, #78, #07   ; LAYOUT pal4444 1x1
                DEFB #02, #04, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #20, #2C, #0D, #01   ; SOURCE #D2C20
                DEFB #04, #02, #78, #07   ; LAYOUT pal4444 1x4
                DEFB #07, #04, #00, #08   ; SIZE
                DEFB 0, 28   ; ox,oy (signed)
                DEFB #24, #2C, #0D, #01   ; SOURCE #D2C24
                DEFB #05, #12, #78, #07   ; LAYOUT pal4444 9x5
                DEFB #08, #1E, #00, #08   ; SIZE
                DEFB 0, 27   ; ox,oy (signed)
                DEFB 17, 27, 3
                DEFB #54, #2C, #0D, #01   ; SOURCE #D2C54
                DEFB #03, #1C, #78, #07   ; LAYOUT pal4444 14x3
                DEFB #05, #2E, #00, #08   ; SIZE
                DEFB 14, 29   ; ox,oy (signed)
                DEFB #80, #2C, #0D, #01   ; SOURCE #D2C80
                DEFB #04, #1A, #78, #07   ; LAYOUT pal4444 13x4
                DEFB #07, #2A, #00, #08   ; SIZE
                DEFB 19, 28   ; ox,oy (signed)
                DEFB #B4, #2C, #0D, #01   ; SOURCE #D2CB4
                DEFB #02, #04, #78, #07   ; LAYOUT pal4444 2x2
                DEFB #04, #08, #00, #08   ; SIZE
                DEFB 30, 29   ; ox,oy (signed)
                DEFB 18, 27, 3
                DEFB #B8, #2C, #0D, #01   ; SOURCE #D2CB8
                DEFB #01, #02, #78, #07   ; LAYOUT pal4444 1x1
                DEFB #02, #04, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #BC, #2C, #0D, #01   ; SOURCE #D2CBC
                DEFB #02, #06, #78, #07   ; LAYOUT pal4444 3x2
                DEFB #04, #0A, #00, #08   ; SIZE
                DEFB 0, 30   ; ox,oy (signed)
                DEFB #C4, #2C, #0D, #01   ; SOURCE #D2CC4
                DEFB #03, #1C, #78, #07   ; LAYOUT pal4444 14x3
                DEFB #05, #2E, #00, #08   ; SIZE
                DEFB 0, 29   ; ox,oy (signed)
                DEFB 19, 27, 3
                DEFB #F0, #2C, #0D, #01   ; SOURCE #D2CF0
                DEFB #20, #38, #78, #07   ; LAYOUT pal4444 28x32
                DEFB #34, #5A, #00, #08   ; SIZE
                DEFB 4, 0   ; ox,oy (signed)
                DEFB #70, #30, #0D, #01   ; SOURCE #D3070
                DEFB #20, #3C, #78, #07   ; LAYOUT pal4444 30x32
                DEFB #34, #60, #00, #08   ; SIZE
                DEFB 2, 0   ; ox,oy (signed)
                DEFB #30, #34, #0D, #01   ; SOURCE #D3430
                DEFB #20, #38, #78, #07   ; LAYOUT pal4444 28x32
                DEFB #34, #5A, #00, #08   ; SIZE
                DEFB 4, 0   ; ox,oy (signed)
                DEFB 20, 27, 3
                DEFB #B0, #37, #0D, #01   ; SOURCE #D37B0
                DEFB #1E, #22, #78, #07   ; LAYOUT pal4444 17x30
                DEFB #30, #38, #00, #08   ; SIZE
                DEFB 0, 2   ; ox,oy (signed)
                DEFB #B0, #39, #0D, #01   ; SOURCE #D39B0
                DEFB #15, #26, #78, #07   ; LAYOUT pal4444 19x21
                DEFB #22, #3E, #00, #08   ; SIZE
                DEFB 0, 11   ; ox,oy (signed)
                DEFB #40, #3B, #0D, #01   ; SOURCE #D3B40
                DEFB #20, #22, #78, #07   ; LAYOUT pal4444 17x32
                DEFB #34, #38, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 17, 28, 3
                DEFB #60, #3D, #0D, #01   ; SOURCE #D3D60
                DEFB #0B, #1C, #78, #07   ; LAYOUT pal4444 14x11
                DEFB #12, #2E, #00, #08   ; SIZE
                DEFB 18, 0   ; ox,oy (signed)
                DEFB #FC, #3D, #0D, #01   ; SOURCE #D3DFC
                DEFB #0B, #1A, #78, #07   ; LAYOUT pal4444 13x11
                DEFB #12, #2A, #00, #08   ; SIZE
                DEFB 19, 0   ; ox,oy (signed)
                DEFB #8C, #3E, #0D, #01   ; SOURCE #D3E8C
                DEFB #07, #24, #78, #07   ; LAYOUT pal4444 18x7
                DEFB #0C, #3A, #00, #08   ; SIZE
                DEFB 14, 0   ; ox,oy (signed)
                DEFB 18, 28, 3
                DEFB #0C, #3F, #0D, #01   ; SOURCE #D3F0C
                DEFB #12, #40, #78, #07   ; LAYOUT pal4444 32x18
                DEFB #1D, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #4C, #41, #0D, #01   ; SOURCE #D414C
                DEFB #12, #40, #78, #07   ; LAYOUT pal4444 32x18
                DEFB #1D, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #8C, #43, #0D, #01   ; SOURCE #D438C
                DEFB #13, #40, #78, #07   ; LAYOUT pal4444 32x19
                DEFB #1F, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 19, 28, 3
                DEFB #EC, #45, #0D, #01   ; SOURCE #D45EC
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #0C, #49, #0D, #01   ; SOURCE #D490C
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #2C, #4C, #0D, #01   ; SOURCE #D4C2C
                DEFB #19, #40, #78, #07   ; LAYOUT pal4444 32x25
                DEFB #28, #68, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 20, 28, 3
                DEFB #4C, #4F, #0D, #01   ; SOURCE #D4F4C
                DEFB #08, #14, #78, #07   ; LAYOUT pal4444 10x8
                DEFB #0D, #20, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #9C, #4F, #0D, #01   ; SOURCE #D4F9C
                DEFB #08, #08, #78, #07   ; LAYOUT pal4444 4x8
                DEFB #0D, #0E, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #BC, #4F, #0D, #01   ; SOURCE #D4FBC
                DEFB #08, #18, #78, #07   ; LAYOUT pal4444 12x8
                DEFB #0D, #28, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB 28, 29, 6
                DEFB #1C, #50, #0D, #01   ; SOURCE #D501C
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #88, #50, #0D, #01   ; SOURCE #D5088
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #F4, #50, #0D, #01   ; SOURCE #D50F4
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #60, #51, #0D, #01   ; SOURCE #D5160
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #CC, #51, #0D, #01   ; SOURCE #D51CC
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB #38, #52, #0D, #01   ; SOURCE #D5238
                DEFB #0F, #0E, #78, #07   ; LAYOUT pal4444 7x15
                DEFB #18, #18, #00, #08   ; SIZE
                DEFB 25, 17   ; ox,oy (signed)
                DEFB 29, 29, 6
                DEFB #A4, #52, #0D, #01   ; SOURCE #D52A4
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #1C, #54, #0D, #01   ; SOURCE #D541C
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #94, #55, #0D, #01   ; SOURCE #D5594
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #0C, #57, #0D, #01   ; SOURCE #D570C
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #84, #58, #0D, #01   ; SOURCE #D5884
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB #FC, #59, #0D, #01   ; SOURCE #D59FC
                DEFB #11, #2C, #78, #07   ; LAYOUT pal4444 22x17
                DEFB #1C, #48, #00, #08   ; SIZE
                DEFB 0, 15   ; ox,oy (signed)
                DEFB 28, 30, 6
                DEFB #74, #5B, #0D, #01   ; SOURCE #D5B74
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #20, #5D, #0D, #01   ; SOURCE #D5D20
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #CC, #5E, #0D, #01   ; SOURCE #D5ECC
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #78, #60, #0D, #01   ; SOURCE #D6078
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #24, #62, #0D, #01   ; SOURCE #D6224
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB #D0, #63, #0D, #01   ; SOURCE #D63D0
                DEFB #19, #22, #78, #07   ; LAYOUT pal4444 17x25
                DEFB #28, #38, #00, #08   ; SIZE
                DEFB 15, 0   ; ox,oy (signed)
                DEFB 29, 30, 6
                DEFB #7C, #65, #0D, #01   ; SOURCE #D657C
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #20, #68, #0D, #01   ; SOURCE #D6820
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #C4, #6A, #0D, #01   ; SOURCE #D6AC4
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #68, #6D, #0D, #01   ; SOURCE #D6D68
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #0C, #70, #0D, #01   ; SOURCE #D700C
                DEFB #1A, #34, #78, #07   ; LAYOUT pal4444 26x26
                DEFB #2A, #54, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
                DEFB #B0, #72, #0D, #01   ; SOURCE #D72B0
                DEFB #1A, #36, #78, #07   ; LAYOUT pal4444 27x26
                DEFB #2A, #58, #00, #08   ; SIZE
                DEFB 0, 0   ; ox,oy (signed)
MAP_ANIM_ENTRY_HEADER   EQU 3
MAP_ANIM_FRAME_SIZE     EQU 14
