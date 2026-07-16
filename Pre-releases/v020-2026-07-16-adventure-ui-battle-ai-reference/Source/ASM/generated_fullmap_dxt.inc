; Сгенерировано Source/Tools/dxt_l4_fullmap_source.py
; Полный pseudo-DXT L4 terrain хранится в Z80/SPG страницах как источник.
; В FT812 RAM_G копируется только якорное окно текущей карты.

BG_FULL_DXT_PAGE_BASE     EQU #90
BG_FULL_DXT_TABLE_PAGE    EQU #8F
BG_FULL_DXT_PAGE_COUNT    EQU 61
BG_FULL_DXT_RAW_SIZE      EQU 995328
BG_FULL_DXT_W             EQU 1152
BG_FULL_DXT_H             EQU 1152
BG_FULL_DXT_C0_OFFSET     EQU 0
BG_FULL_DXT_C1_OFFSET     EQU 165888
BG_FULL_DXT_MASK_OFFSET   EQU 331776
BG_FULL_DXT_COLOR_STRIDE  EQU 576
BG_FULL_DXT_MASK_STRIDE   EQU 576
BG_DXT_ANCHORED_WINDOW    EQU 1
BG_DXT_ANCHOR_MAX_X       EQU 8
BG_DXT_ANCHOR_MAX_Y       EQU 14

BackgroundDxt_UploadWindow:
                if BG_DXT_RAW_SIZE
                GetPage3
                LD   (BackgroundDxt_RestorePage), A
                CALL BackgroundDxt_UpdateAnchor
                LD   A, (BackgroundDxtAnchorChanged)
                OR   A
                JR   NZ, BackgroundDxt_DoUpload
                JP   BackgroundDxt_RestorePage

BackgroundDxt_DoUpload:
                SetPage3 BG_FULL_DXT_TABLE_PAGE

                LD   A, (BackgroundDxtOriginY)
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE
                LD   A, (BackgroundDxtOriginX)
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                LD   DE, #C000
                ADD  HL, DE
                LD   (BackgroundDxt_TablePtr), HL

                CALL BackgroundDxt_LoadEntry
                LD   A, BG_DXT_RAMG >> 16
                LD   (BackgroundDxt_DstHigh), A
                LD   HL, BG_DXT_RAMG & #FFFF
                LD   (BackgroundDxt_DstLow), HL
                LD   HL, BG_FULL_DXT_COLOR_STRIDE
                LD   (BackgroundDxt_SrcStride), HL
                LD   HL, BG_DXT_COLOR_STRIDE
                LD   (BackgroundDxt_DstStride), HL
                LD   HL, BG_DXT_COLOR_H
                LD   (BackgroundDxt_Rows), HL
                LD   HL, BG_DXT_COLOR_STRIDE
                LD   (BackgroundDxt_RowBytes), HL
                CALL BackgroundDxt_CopyRows

                CALL BackgroundDxt_LoadEntry
                LD   A, (BG_DXT_RAMG + BG_DXT_C1_OFFSET) >> 16
                LD   (BackgroundDxt_DstHigh), A
                LD   HL, (BG_DXT_RAMG + BG_DXT_C1_OFFSET) & #FFFF
                LD   (BackgroundDxt_DstLow), HL
                LD   HL, BG_FULL_DXT_COLOR_STRIDE
                LD   (BackgroundDxt_SrcStride), HL
                LD   HL, BG_DXT_COLOR_STRIDE
                LD   (BackgroundDxt_DstStride), HL
                LD   HL, BG_DXT_COLOR_H
                LD   (BackgroundDxt_Rows), HL
                LD   HL, BG_DXT_COLOR_STRIDE
                LD   (BackgroundDxt_RowBytes), HL
                CALL BackgroundDxt_CopyRows

                CALL BackgroundDxt_LoadEntry
                LD   A, (BG_DXT_RAMG + BG_DXT_MASK_OFFSET) >> 16
                LD   (BackgroundDxt_DstHigh), A
                LD   HL, (BG_DXT_RAMG + BG_DXT_MASK_OFFSET) & #FFFF
                LD   (BackgroundDxt_DstLow), HL
                LD   HL, BG_FULL_DXT_MASK_STRIDE
                LD   (BackgroundDxt_SrcStride), HL
                LD   HL, BG_DXT_MASK_STRIDE
                LD   (BackgroundDxt_DstStride), HL
                LD   HL, BG_DXT_H
                LD   (BackgroundDxt_Rows), HL
                LD   HL, BG_DXT_MASK_STRIDE
                LD   (BackgroundDxt_RowBytes), HL
                CALL BackgroundDxt_CopyRows

                JP   BackgroundDxt_RestorePage

BackgroundDxt_UpdateAnchor:
                XOR  A
                LD   (BackgroundDxtAnchorChanged), A

                LD   A, (ViewportOriginX)
                AND  #F8
                CP   BG_DXT_ANCHOR_MAX_X + 1
                JR   C, BackgroundDxt_AnchorXOk
                LD   A, BG_DXT_ANCHOR_MAX_X
BackgroundDxt_AnchorXOk:
                LD   B, A
                LD   A, (BackgroundDxtOriginX)
                CP   B
                JR   Z, BackgroundDxt_AnchorY
                LD   A, B
                LD   (BackgroundDxtOriginX), A
                LD   A, 1
                LD   (BackgroundDxtAnchorChanged), A

BackgroundDxt_AnchorY:
                LD   A, (ViewportOriginY)
                CP   14
                JR   C, BackgroundDxt_AnchorYCheck7
                LD   A, 14
                JR   BackgroundDxt_AnchorYHave
BackgroundDxt_AnchorYCheck7:
                CP   7
                JR   C, BackgroundDxt_AnchorYZero
                LD   A, 7
                JR   BackgroundDxt_AnchorYHave
BackgroundDxt_AnchorYZero:
                XOR  A
BackgroundDxt_AnchorYHave:
                LD   B, A
                LD   A, (BackgroundDxtOriginY)
                CP   B
                RET  Z
                LD   A, B
                LD   (BackgroundDxtOriginY), A
                LD   A, 1
                LD   (BackgroundDxtAnchorChanged), A
                RET

BackgroundDxt_ResetAnchor:
                LD   A, #FF
                LD   (BackgroundDxtOriginX), A
                LD   (BackgroundDxtOriginY), A
                RET

BackgroundDxt_RestorePage EQU $+1
                LD   A, #00
                SetPage3_A
                endif
                RET

BackgroundDxt_LoadEntry:
                LD   HL, (BackgroundDxt_TablePtr)
                LD   A, (HL)
                LD   (BackgroundDxt_SourcePage), A
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   (BackgroundDxt_SourceAddr), DE
                LD   (BackgroundDxt_TablePtr), HL
                RET

BackgroundDxt_CopyRows:
                LD   HL, (BackgroundDxt_Rows)
                LD   A, H
                OR   L
                RET  Z
                CALL BackgroundDxt_CopyRow

                LD   HL, (BackgroundDxt_SourceAddr)
                LD   BC, (BackgroundDxt_SrcStride)
                ADD  HL, BC
                JR   NC, BackgroundDxt_SourceNoCarry
                LD   A, H
                OR   #C0
                LD   H, A
                LD   A, (BackgroundDxt_SourcePage)
                INC  A
                LD   (BackgroundDxt_SourcePage), A
BackgroundDxt_SourceNoCarry:
                LD   (BackgroundDxt_SourceAddr), HL

                LD   HL, (BackgroundDxt_DstLow)
                LD   BC, (BackgroundDxt_DstStride)
                ADD  HL, BC
                LD   (BackgroundDxt_DstLow), HL
                JR   NC, BackgroundDxt_DstNoCarry
                LD   A, (BackgroundDxt_DstHigh)
                INC  A
                LD   (BackgroundDxt_DstHigh), A
BackgroundDxt_DstNoCarry:

                LD   HL, (BackgroundDxt_Rows)
                DEC  HL
                LD   (BackgroundDxt_Rows), HL
                JR   BackgroundDxt_CopyRows

BackgroundDxt_CopyRow:
                LD   HL, (BackgroundDxt_SourceAddr)
                LD   BC, (BackgroundDxt_RowBytes)
                ADD  HL, BC
                JR   C, BackgroundDxt_CopyRowSplit
                LD   A, (BackgroundDxt_SourcePage)
                LD   (Render_DmaSourcePage), A
                LD   HL, (BackgroundDxt_SourceAddr)
                LD   A, (BackgroundDxt_DstHigh)
                LD   DE, (BackgroundDxt_DstLow)
                LD   BC, (BackgroundDxt_RowBytes)
                CALL Render_WriteMem_DMA
                RET

BackgroundDxt_CopyRowSplit:
                LD   HL, (BackgroundDxt_SourceAddr)
                LD   DE, 0
                EX   DE, HL
                OR   A
                SBC  HL, DE
                LD   (BackgroundDxt_FirstLen), HL
                LD   HL, (BackgroundDxt_RowBytes)
                LD   DE, (BackgroundDxt_FirstLen)
                OR   A
                SBC  HL, DE
                LD   (BackgroundDxt_SecondLen), HL

                LD   A, (BackgroundDxt_SourcePage)
                LD   (Render_DmaSourcePage), A
                LD   HL, (BackgroundDxt_SourceAddr)
                LD   A, (BackgroundDxt_DstHigh)
                LD   DE, (BackgroundDxt_DstLow)
                LD   BC, (BackgroundDxt_FirstLen)
                CALL Render_WriteMem_DMA

                LD   HL, (BackgroundDxt_DstLow)
                LD   BC, (BackgroundDxt_FirstLen)
                ADD  HL, BC
                LD   (BackgroundDxt_TempDstLow), HL
                LD   A, (BackgroundDxt_DstHigh)
                JR   NC, BackgroundDxt_TempDstNoCarry
                INC  A
BackgroundDxt_TempDstNoCarry:
                LD   (BackgroundDxt_TempDstHigh), A

                LD   A, (BackgroundDxt_SourcePage)
                INC  A
                LD   (Render_DmaSourcePage), A
                LD   HL, #C000
BackgroundDxt_TempDstHigh EQU $+1
                LD   A, #00
BackgroundDxt_TempDstLow EQU $+1
                LD   DE, #0000
                LD   BC, (BackgroundDxt_SecondLen)
                CALL Render_WriteMem_DMA
                RET

BackgroundDxt_TablePtr:    DEFW 0
BackgroundDxt_SourceAddr:  DEFW 0
BackgroundDxt_SourcePage:  DEFB 0
BackgroundDxt_DstLow:      DEFW 0
BackgroundDxt_DstHigh:     DEFB 0
BackgroundDxt_SrcStride:   DEFW 0
BackgroundDxt_DstStride:   DEFW 0
BackgroundDxt_RowBytes:    DEFW 0
BackgroundDxt_Rows:        DEFW 0
BackgroundDxt_FirstLen:    DEFW 0
BackgroundDxt_SecondLen:   DEFW 0
BackgroundDxtOriginX:      DEFB 0
BackgroundDxtOriginY:      DEFB 0
BackgroundDxtAnchorChanged: DEFB 0
