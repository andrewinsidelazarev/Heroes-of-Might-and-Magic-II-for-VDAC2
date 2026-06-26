                ifndef _HMM2_RENDER_
                define _HMM2_RENDER_

RUNTIME_DL_LEFT_RAMG   EQU #0F0000
RUNTIME_DL_RIGHT_RAMG  EQU RUNTIME_DL_LEFT_RAMG + RUNTIME_LEFT_DL_BYTES
RUNTIME_DL_OBJECT_RAMG EQU RUNTIME_DL_RIGHT_RAMG + RUNTIME_RIGHT_DL_BYTES
HERO_PATH_ROUTE_DL     EQU 1
ROUTE_DIR_UNKNOWN      EQU #FF
HERO_SPRITE_MIRROR_C   EQU (HERO_SPRITE_W - 1) * 256

Render_Frame:
                LD   A, (GameMode)
                CP   GAME_MODE_MENU
                JP   Z, Render_Menu_Tramp
                CP   GAME_MODE_HIGHSCORES_STANDARD
                JP   Z, Render_HiScores_Tramp
                CP   GAME_MODE_HIGHSCORES_CAMPAIGN
                JP   Z, Render_HiScores_Tramp
                CP   GAME_MODE_TOWN
                JP   Z, Render_Town_Tramp
                CP   GAME_MODE_COMBAT
                JP   Z, Render_Battle_Tramp
                if RUNTIME_TILEMAP_RENDER
                CALL Render_RuntimeFrameCmd
                else
                CALL Render_WaitSafeDL
                if VIEWPORT_DL_PACK
                CALL Render_ViewportPack
                else
                LD   HL, ADVENTURE_DL
                LD   BC, ADVENTURE_DL_SIZE
                LD   DE, 0
                CALL FT.WriteDL
                endif
                CALL Render_HeroMarker
                CALL Render_Actor
                CALL Render_Cursor
                FT_WR_REG8 FT_REG_DLSWAP, FT_DLSWAP_FRAME
                endif
                RET

Render_BeginFrameSync:
                FT_RD_REG8 FT_REG_INT_FLAGS
                AND  FT_INT_SWAP
                JR   Z, Render_BeginFrameSync
                FT_WR_REG8 FT_REG_INT_FLAGS, FT_INT_SWAP
.WaitDLSwap:   FT_RD_REG8 FT_REG_DLSWAP
                AND  3
                JR   NZ, .WaitDLSwap
                RET

Render_WaitSafeDL:
                CALL Render_BeginFrameSync
                RET

Render_RuntimeFrameCmd:
                if RUNTIME_TILEMAP_RENDER
                CALL Runtime_UpdateTranslate
                ; RAM_G не буферизуется FT812. Любую заливку тайлов/объектов
                ; делаем только сразу после VSYNC, до сборки нового DL.
                CALL Render_BeginFrameSync
                CALL Runtime_UploadStaticIfDirty
                CALL Render_WaterCycle
                CALL RuntimeDL_UpdateTerrainSources
                FT_CMD_Start
                if BG_DXT_RAW_SIZE
                LD   HL, #FFFF
                LD   DE, #FF00
                CALL Render_CmdBufWrite32
                CALL Render_DxtUpdateScrollMatrix
                LD   HL, BackgroundDxt_DL
                LD   BC, BackgroundDxt_DL_SIZE
                CALL Render_CmdBufCopy
                else
                LD   HL, #FFFF
                LD   DE, #FF00
                CALL Render_CmdBufWrite32
                LD   HL, RuntimeDL_Header
                LD   BC, RuntimeDL_Header_SIZE
                CALL Render_CmdBufCopy
                LD   A, (RUNTIME_DL_LEFT_RAMG >> 16) & #FF
                LD   DE, RUNTIME_DL_LEFT_RAMG & #FFFF
                LD   BC, RUNTIME_LEFT_DL_BYTES
                CALL Render_CmdAppend
                LD   HL, RuntimeDL_RightBand
                LD   BC, RuntimeDL_RightBand_SIZE
                CALL Render_CmdBufCopy
                LD   BC, RUNTIME_RIGHT_DL_BYTES
                LD   A, B
                OR   C
                JR   Z, .skip_right_append
                LD   A, (RUNTIME_DL_RIGHT_RAMG >> 16) & #FF
                LD   DE, RUNTIME_DL_RIGHT_RAMG & #FFFF
                CALL Render_CmdAppend
.skip_right_append:
                LD   HL, RuntimeDL_Tail
                LD   BC, RuntimeDL_Tail_SIZE - 4
                CALL Render_CmdBufCopy
                endif
                CALL Render_RuntimeObjectsCmd
                if HERO_PATH_ROUTE_DL
                CALL Render_HeroPathCmd
                endif
                CALL Render_HeroMarkerCmd
                CALL Render_ActorCmd
                CALL Render_RuntimeTopObjectsCmd   ; top-слой ПОВЕРХ актёра (z-слои)
                CALL Render_MapAnimCmd             ; анимир. объекты (кадр-дельта), до тумана
                CALL Render_FogCmd
                CALL Render_AdventureUICmd
                CALL Render_ResourcePanelCmd
                CALL Render_MinimapRectCmd
                CALL Render_MinimapHeroDotCmd
                CALL Render_AdvButtonsCmd          ; все кнопки поверх UI
                CALL Render_RightPanelCmd
                CALL Render_CursorCmd
                ; БЕЗ CMD_SWAP в потоке! Свап — ТОЛЬКО ручным REG_DLSWAP после
                ; WaitFlush (как в Zuma VDAC2). CMD_SWAP + ручной DLSWAP = два
                ; механизма свапа: если свап копроцессора исполнится ровно на
                ; границе кадра, ручная запись армирует ВТОРОЙ свап обратно на
                ; старый DL → периодический «кадр назад» = дёргание.
                ; VSYNC уже был в начале кадра перед изменением RAM_G.
                ; Здесь только отправляем CMD и армируем ручной DLSWAP.
                CALL Render_SubmitFrameDMA
                endif
                RET

Render_CmdBufCopy:
                LD   DE, (FT.Coprocessor.BufferPtr)
                LDIR
                LD   (FT.Coprocessor.BufferPtr), DE
                RET

Render_CmdBufWrite32:
                PUSH HL
                LD   HL, (FT.Coprocessor.BufferPtr)
                LD   (HL), E
                INC  HL
                LD   (HL), D
                INC  HL
                POP  DE
                LD   (HL), E
                INC  HL
                LD   (HL), D
                INC  HL
                LD   (FT.Coprocessor.BufferPtr), HL
                RET

Render_CmdAppend:
                LD   (.AppendAddrHigh), A
                LD   (.AppendAddrLow), DE
                LD   (.AppendSize), BC
                LD   HL, #FFFF
                LD   DE, #FF1E
                CALL Render_CmdBufWrite32
.AppendAddrHigh EQU $+1
                LD   HL, #0000
.AppendAddrLow EQU $+1
                LD   DE, #0000
                CALL Render_CmdBufWrite32
                LD   HL, #0000
.AppendSize    EQU $+1
                LD   DE, #0000
                CALL Render_CmdBufWrite32
                RET

Render_SwapFrameDMA:
                CALL Render_BeginFrameSync
Render_SubmitFrameDMA:
                CALL Render_CMD_Write_DMA
                CALL FT.Coprocessor.WaitFlush
                FT_WR_REG8 FT_REG_DLSWAP, FT_DLSWAP_FRAME
                RET

; ----------------------------------------------------------------------------
; Render_BlackFrame — ГЛОБАЛЬНЫЙ межсценный чёрный кадр.
; ПРАВИЛО: любой переход между сценами (смена GameMode + загрузка ассетов в RAM_G)
; ОБЯЗАН начинаться с Render_BlackFrame. Свопает DL БЕЗ ссылок на RAM_G (чистый CLEAR)
; и ДОЖИДАЕТСЯ фактического показа (REG_DLSWAP==0), чтобы FT812 перестал читать старый
; RAM_G ДО того, как новая сцена начнёт его перезаписывать. Иначе — яркий мусор
; перерисовки (старый DL по уже частично перезаписанным битмапам). См. Чат.txt
; 2026-06-11 («свопни кадр-без-ссылок и дождись показа ДО загрузки»).
; Ждём REG_DLSWAP==0, а НЕ FT_INT_SWAP (clear-on-read нельзя поллить вторым местом,
; Чат.txt 2026-06-17 DrawBlackTransitionFrame).
Render_BlackFrame:
                FT_CMD_Start
                LD   HL, #FFFF                    ; CMD_DLSTART (0xFFFFFF00)
                LD   DE, #FF00
                CALL Render_CmdBufWrite32
                LD   HL, BlackScene_DL
                LD   BC, BlackScene_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Render_SubmitFrameDMA       ; DMA + WaitFlush + DLSWAP_FRAME
.waitShown:    FT_RD_REG8 FT_REG_DLSWAP          ; дождаться ФАКТИЧЕСКОГО показа чёрного
                AND  3
                JR   NZ, .waitShown
                RET

BlackScene_DL:  FT_CLEAR_COLOR_RGB 0, 0, 0
                FT_CLEAR 1, 1, 1
                FT_DISPLAY
BlackScene_DL_SIZE EQU $ - BlackScene_DL

Render_CMD_Write_DMA:
                FT_CMD_Count
                LD   A, B
                OR   C
                RET  Z
                SRL  B
                RR   C
                LD   A, B
                LD   (Render_CmdDmaWordsHi), A
                LD   A, C
                LD   (Render_CmdDmaWordsLo), A

                FT_ON
                LD   A, ((FT_REG_CMDB_WRITE >> 16) & #FF) | #80
                OUT  (SPI_DATA), A
                LD   A, (FT_REG_CMDB_WRITE >> 8) & #FF
                OUT  (SPI_DATA), A
                LD   A, FT_REG_CMDB_WRITE & #FF
                OUT  (SPI_DATA), A

                LD   A, LOW (CMD_ADDRESS_PTR & #3FFF)
                LD   BC, DMASADDRL
                OUT  (C), A
                LD   A, HIGH (CMD_ADDRESS_PTR & #3FFF)
                LD   BC, DMASADDRH
                OUT  (C), A
                LD   A, CorePage + 1
                LD   BC, DMASADDRX
                OUT  (C), A

                LD   A, (Render_CmdDmaWordsHi)
                OR   A
                JR   Z, .tail
                DEC  A
                LD   BC, DMANUM
                OUT  (C), A
                LD   A, #FF
                LD   BC, DMALEN
                OUT  (C), A
                LD   A, DMA_RAM_SPI
                LD   BC, DMACTR
                OUT  (C), A
.wait_full:     LD   BC, DMASTATUS
                IN   A, (C)
                AND  DMA_WNR
                JR   NZ, .wait_full

.tail:          LD   A, (Render_CmdDmaWordsLo)
                OR   A
                JR   Z, .done
                DEC  A
                LD   BC, DMALEN
                OUT  (C), A
                XOR  A
                LD   BC, DMANUM
                OUT  (C), A
                LD   A, DMA_RAM_SPI
                LD   BC, DMACTR
                OUT  (C), A
.wait_tail:     LD   BC, DMASTATUS
                IN   A, (C)
                AND  DMA_WNR
                JR   NZ, .wait_tail

.done:          FT_OFF
                RET

Render_CmdDmaWordsHi:
                DEFB 0
Render_CmdDmaWordsLo:
                DEFB 0

Runtime_UploadStaticIfDirty:
                if RUNTIME_TILEMAP_RENDER
                LD   A, (ViewportOriginX)
                LD   B, A
                LD   A, (RuntimeLastOriginX)
                CP   B
                JR   NZ, .upload
                LD   A, (ViewportOriginY)
                LD   B, A
                LD   A, (RuntimeLastOriginY)
                CP   B
                RET  Z
.upload:        LD   A, (ViewportOriginX)
                if BG_DXT_RAW_SIZE
                LD   (RuntimeLastOriginX), A
                LD   A, (ViewportOriginY)
                LD   (RuntimeLastOriginY), A
                CALL BackgroundDxt_UploadWindow
                CALL Runtime_UploadObjectStatic
                else
                if COMPOSITE_STATIC_TILEMAP
                CALL CompositeTiles_UploadForScroll
                endif
                LD   A, (ViewportOriginX)
                LD   (RuntimeLastOriginX), A
                LD   A, (ViewportOriginY)
                LD   (RuntimeLastOriginY), A
                CALL Render_RuntimeTilemapBuffer
                LD   A, CorePage + 1
                LD   (Render_DmaSourcePage), A
                LD   HL, RUNTIME_DL_BUFFER + RuntimeDL_Header_SIZE
                LD   A, (RUNTIME_DL_LEFT_RAMG >> 16) & #FF
                LD   DE, RUNTIME_DL_LEFT_RAMG & #FFFF
                LD   BC, RUNTIME_LEFT_DL_BYTES
                CALL Render_WriteMem_DMA
                LD   BC, RUNTIME_RIGHT_DL_BYTES
                LD   A, B
                OR   C
                JR   Z, .skip_right_dma
                LD   HL, RUNTIME_DL_BUFFER + RuntimeDL_Header_SIZE + RUNTIME_LEFT_DL_BYTES + RuntimeDL_RightBand_SIZE
                LD   A, (RUNTIME_DL_RIGHT_RAMG >> 16) & #FF
                LD   DE, RUNTIME_DL_RIGHT_RAMG & #FFFF
                CALL Render_WriteMem_DMA
.skip_right_dma:
                CALL Runtime_UploadObjectStatic
                endif
                endif
                RET

Runtime_UploadObjectStatic:
                if RUNTIME_TILEMAP_RENDER
                GetPage3
                LD   (.RestorePage), A
                CALL Render_ObjectViewTableEntry
                LD   A, (HL)
                LD   (.ObjectPage), A
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   C, (HL)
                INC  HL
                LD   B, (HL)
                ; BC = bottom_size; прибавляем top_size (байты 5-6) → заливаем
                ; весь blob [низ][верх] одной DMA. off остаётся в DE.
                INC  HL
                LD   A, C
                ADD  A, (HL)
                LD   C, A
                INC  HL
                LD   A, B
                ADC  A, (HL)
                LD   B, A
                LD   (.ObjectSize), BC
                EX   DE, HL
                LD   DE, #C000
                ADD  HL, DE
                LD   (.ObjectSrc), HL
.ObjectPage    EQU $+1
                LD   A, #00
                LD   (Render_DmaSourcePage), A
                SetPage3_A
.ObjectSrc     EQU $+1
                LD   HL, #C000
                LD   A, (RUNTIME_DL_OBJECT_RAMG >> 16) & #FF
                LD   DE, RUNTIME_DL_OBJECT_RAMG & #FFFF
.ObjectSize    EQU $+1
                LD   BC, #0000
                CALL Render_WriteMem_DMA
.RestorePage   EQU $+1
                LD   A, #00
                SetPage3_A
                endif
                RET

Render_WriteMem_DMA:
                LD   (Render_DmaDstHigh), A
                LD   (Render_DmaDstLow), DE
                SRL  B
                RR   C
                LD   A, B
                LD   (Render_DmaWordsHi), A
                LD   A, C
                LD   (Render_DmaWordsLo), A

                FT_ON
Render_DmaDstHigh EQU $+1
                LD   A, #00
                OR   #80
                OUT  (SPI_DATA), A
Render_DmaDstLow EQU $+1
                LD   DE, #0000
                LD   A, D
                OUT  (SPI_DATA), A
                LD   A, E
                OUT  (SPI_DATA), A

                LD   A, L
                LD   BC, DMASADDRL
                OUT  (C), A
                LD   A, H
                AND  #3F
                LD   BC, DMASADDRH
                OUT  (C), A
Render_DmaSourcePage EQU $+1
                LD   A, #00
                LD   BC, DMASADDRX
                OUT  (C), A

                LD   A, (Render_DmaWordsHi)
                OR   A
                JR   Z, .tail
                DEC  A
                LD   BC, DMANUM
                OUT  (C), A
                LD   A, #FF
                LD   BC, DMALEN
                OUT  (C), A
                LD   A, DMA_RAM_SPI
                LD   BC, DMACTR
                OUT  (C), A
.wait_full:     LD   BC, DMASTATUS
                IN   A, (C)
                AND  DMA_WNR
                JR   NZ, .wait_full

.tail:          LD   A, (Render_DmaWordsLo)
                OR   A
                JR   Z, .done
                DEC  A
                LD   BC, DMALEN
                OUT  (C), A
                XOR  A
                LD   BC, DMANUM
                OUT  (C), A
                LD   A, DMA_RAM_SPI
                LD   BC, DMACTR
                OUT  (C), A
.wait_tail:     LD   BC, DMASTATUS
                IN   A, (C)
                AND  DMA_WNR
                JR   NZ, .wait_tail

.done:          FT_OFF
                RET

Render_DmaWordsHi:
                DEFB 0
Render_DmaWordsLo:
                DEFB 0

Render_RuntimeTilemap:
                if RUNTIME_TILEMAP_RENDER
                CALL Render_RuntimeTilemapBuffer
                LD   HL, RUNTIME_DL_BUFFER
                LD   BC, RUNTIME_BASE_DL_SIZE
                LD   DE, 0
                CALL FT.WriteDL
                CALL Render_RuntimeObjects
                endif
                RET

Render_RuntimeTilemapBuffer:
                if RUNTIME_TILEMAP_RENDER
                CALL Runtime_UpdateTranslate
                CALL RuntimeDL_UpdateTerrainSources
                LD   HL, RuntimeDL_Header
                LD   DE, RUNTIME_DL_BUFFER
                LD   BC, RuntimeDL_Header_SIZE
                LDIR
                LD   HL, RUNTIME_DL_BUFFER + RuntimeDL_Header_SIZE
                LD   (RuntimeDestPtr), HL
                GetPage3
                LD   (.RestoreMapCellsPage), A
                SetPage3 MAP_TERRAIN_CELLS_PAGE
                CALL Runtime_MapIXFromOrigin
                LD   B, RUNTIME_VIEW_H
.left_row:      PUSH BC
                LD   B, RUNTIME_LEFT_VIEW_W
.left_col:      PUSH BC
                CALL Runtime_CopyVertex
                LD   BC, MAP_TERRAIN_CELL_ENTRY_SIZE
                ADD  IX, BC
                POP  BC
                DJNZ .left_col
                LD   BC, (MAP_TERRAIN_CELL_STRIDE - RUNTIME_LEFT_VIEW_W) * MAP_TERRAIN_CELL_ENTRY_SIZE
                ADD  IX, BC
                POP  BC
                DJNZ .left_row
                LD   HL, RuntimeDL_RightBand
                LD   DE, (RuntimeDestPtr)
                LD   BC, RuntimeDL_RightBand_SIZE
                LDIR
                LD   (RuntimeDestPtr), DE
                LD   A, RUNTIME_RIGHT_VIEW_W
                OR   A
                JR   Z, .right_done
                CALL Runtime_MapIXFromOrigin
                LD   BC, RUNTIME_LEFT_VIEW_W * MAP_TERRAIN_CELL_ENTRY_SIZE
                ADD  IX, BC
                LD   B, RUNTIME_VIEW_H
.right_row:     PUSH BC
                LD   B, RUNTIME_RIGHT_VIEW_W
.right_col:     PUSH BC
                CALL Runtime_CopyVertex
                LD   BC, MAP_TERRAIN_CELL_ENTRY_SIZE
                ADD  IX, BC
                POP  BC
                DJNZ .right_col
                LD   BC, (MAP_TERRAIN_CELL_STRIDE - RUNTIME_RIGHT_VIEW_W) * MAP_TERRAIN_CELL_ENTRY_SIZE
                ADD  IX, BC
                POP  BC
                DJNZ .right_row
.right_done:
                LD   HL, RuntimeDL_Tail
                LD   DE, (RuntimeDestPtr)
                LD   BC, RuntimeDL_Tail_SIZE
                LDIR
.RestoreMapCellsPage EQU $+1
                LD   A, #00
                SetPage3_A
                endif
                RET

Render_RuntimeObjectsCmd:
                if RUNTIME_TILEMAP_RENDER
                LD   HL, RuntimeDL_ObjectTranslate
                LD   BC, RuntimeDL_ObjectTranslate_SIZE
                CALL Render_CmdBufCopy
                CALL Render_ObjectViewTableEntry
                INC  HL
                INC  HL
                INC  HL
                LD   C, (HL)
                INC  HL
                LD   B, (HL)
                LD   A, (RUNTIME_DL_OBJECT_RAMG >> 16) & #FF
                LD   DE, RUNTIME_DL_OBJECT_RAMG & #FFFF
                CALL Render_CmdAppend
                endif
                RET

; top-слой (level2): CMD_APPEND ПОСЛЕ актёра. blob уже залит в
; RUNTIME_DL_OBJECT_RAMG (низ+верх). Верх лежит со смещением bottom_size,
; размер top_size. Адрес = RUNTIME_DL_OBJECT_RAMG + bottom_size.
Render_RuntimeTopObjectsCmd:
                if RUNTIME_TILEMAP_RENDER
                CALL Render_ObjectViewTableEntry   ; HL -> запись origin (7 байт)
                INC  HL                            ; page
                INC  HL                            ; off lo
                INC  HL                            ; off hi -> HL у bottom_size
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = bottom_size
                INC  HL
                LD   C, (HL)
                INC  HL
                LD   B, (HL)                       ; BC = top_size
                LD   A, B
                OR   C
                RET  Z                             ; нет top-объектов на этом origin
                ; переустановить object VERTEX_TRANSLATE (актёр/маркер могли сбить)
                PUSH BC                            ; top_size
                PUSH DE                            ; bottom_size
                LD   HL, RuntimeDL_ObjectTranslate
                LD   BC, RuntimeDL_ObjectTranslate_SIZE
                CALL Render_CmdBufCopy
                ; СБРОС BITMAP_TRANSFORM на handle 2: актёр-флип ВЛЕВО (HeroFacingRight=0)
                ; оставляет A=-160/C=7936 (зеркало) → иначе top-объекты/замки рисуются
                ; зеркально = вертикальные артефакты на фоне (только при движении влево).
                LD   HL, #1500
                LD   DE, #00A0
                CALL Render_CmdBufWrite32          ; BITMAP_TRANSFORM_A 160 (×1.6, без флипа)
                LD   HL, #1700
                LD   DE, #0000
                CALL Render_CmdBufWrite32          ; BITMAP_TRANSFORM_C 0
                POP  DE                            ; bottom_size
                POP  BC                            ; top_size
                LD   HL, RUNTIME_DL_OBJECT_RAMG & #FFFF
                ADD  HL, DE                        ; + bottom_size (может перенести)
                LD   A, (RUNTIME_DL_OBJECT_RAMG >> 16) & #FF
                ADC  A, 0                          ; перенос в старший байт адреса
                EX   DE, HL                        ; DE = addr lo16, A = addr hi
                CALL Render_CmdAppend              ; A:DE = addr, BC = top_size
                endif
                RET

Render_RuntimeObjects:
                if RUNTIME_TILEMAP_RENDER
                GetPage3
                LD   (.RestorePage), A
                CALL Render_ObjectViewTableEntry
                LD   A, (HL)
                LD   (.ObjectPage), A
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   C, (HL)
                INC  HL
                LD   B, (HL)
                ; BC = bottom_size; прибавляем top_size (байты 5-6) → заливаем
                ; весь blob [низ][верх] одной DMA. off остаётся в DE.
                INC  HL
                LD   A, C
                ADD  A, (HL)
                LD   C, A
                INC  HL
                LD   A, B
                ADC  A, (HL)
                LD   B, A
                LD   (.ObjectSize), BC
                EX   DE, HL
                LD   DE, #C000
                ADD  HL, DE
                LD   (.ObjectSrc), HL
.ObjectPage    EQU $+1
                LD   A, #00
                SetPage3_A
.ObjectSrc     EQU $+1
                LD   HL, #C000
.ObjectSize    EQU $+1
                LD   BC, #0000
                LD   DE, RUNTIME_BASE_DL_SIZE + RuntimeDL_ObjectTranslate_SIZE - 4
                CALL FT.WriteDL
                LD   HL, RuntimeDL_ObjectTranslate
                LD   BC, RuntimeDL_ObjectTranslate_SIZE
                LD   DE, RUNTIME_BASE_DL_SIZE - 4
                CALL FT.WriteDL
.RestorePage   EQU $+1
                LD   A, #00
                SetPage3_A
                endif
                RET

Render_HeroPathCmd:
                LD   A, (PathState)
                CP   PATH_STATE_SEARCH
                RET  Z
                LD   A, (HeroPathLen)
                OR   A
                RET  Z
                LD   (RenderPathIndex), A
                LD   A, (HeroPathIndex)
                LD   (RenderPathIndex), A
                ; маршрут целиком, но «за этот ход» (после HeroMovePoints тайлов) рисуем
                ; затемнённо (fheroes2: видно, докуда дойдёшь этим ходом и куда дальше).
                LD   A, (HeroMovePoints)
                LD   (RenderPathRemaining), A
                XOR  A
                LD   (RenderPathDimmed), A
                LD   A, (HeroStepX)
                LD   (RenderPathPrevX), A
                LD   A, (HeroStepY)
                LD   (RenderPathPrevY), A
                CALL Render_RouteBeginCmd

.loop:          LD   A, (RenderPathRemaining)
                OR   A
                JR   NZ, .tile                ; ещё в пределах хода (ярко)
                LD   A, (RenderPathDimmed)
                OR   A
                JR   NZ, .tile                ; уже затемнено
                LD   A, 1
                LD   (RenderPathDimmed), A
                LD   HL, ((#2A000000 | ROUTE_RED_PALETTE_RAMG) >> 16) & #FFFF
                LD   DE, (#2A000000 | ROUTE_RED_PALETTE_RAMG) & #FFFF
                CALL Render_CmdBufWrite32     ; PALETTE_SOURCE красная — «следующий ход» красным
.tile:          CALL Render_LoadCurrentPathTile
                CALL Render_PathTileVisible
                OR   A
                JR   Z, .advance_prev

                LD   A, (RenderPathIndex)
                OR   A
                JR   Z, .target_marker

                DEC  A
                LD   E, A
                LD   D, 0
                LD   HL, HeroPathXBuf
                ADD  HL, DE
                LD   A, (HL)
                LD   (RenderPathNextX), A
                LD   A, (RenderPathIndex)
                DEC  A
                LD   E, A
                LD   D, 0
                LD   HL, HeroPathYBuf
                ADD  HL, DE
                LD   A, (HL)
                LD   (RenderPathNextY), A

                CALL Render_DirectionPrevToCurrent
                CP   ROUTE_DIR_UNKNOWN
                JR   Z, .target_marker
                LD   (RenderPathFromDir), A
                CALL Render_DirectionCurrentToNext
                CP   ROUTE_DIR_UNKNOWN
                JR   Z, .target_marker
                LD   (RenderPathToDir), A
                CALL Render_RouteSpriteIndex
                JR   .draw
.target_marker: XOR  A
.draw:          LD   (RenderRouteSpriteIndex), A
                CALL Render_WriteRouteSpriteCmd

.advance_prev:  LD   A, (RenderPathTileX)
                LD   (RenderPathPrevX), A
                LD   A, (RenderPathTileY)
                LD   (RenderPathPrevY), A
                LD   A, (RenderPathIndex)
                OR   A
                JR   Z, .done
                DEC  A
                LD   (RenderPathIndex), A
                LD   A, (RenderPathRemaining)
                OR   A
                JP   Z, .loop                 ; запас исчерпан — счётчик стоит на 0 (дальше тускло)
                DEC  A
                LD   (RenderPathRemaining), A
                JP   .loop
.done:          JP   Render_RouteEndCmd

Render_LoadCurrentPathTile:
                LD   A, (RenderPathIndex)
                LD   E, A
                LD   D, 0
                LD   HL, HeroPathXBuf
                ADD  HL, DE
                LD   A, (HL)
                LD   (RenderPathTileX), A
                LD   A, (RenderPathIndex)
                LD   E, A
                LD   D, 0
                LD   HL, HeroPathYBuf
                ADD  HL, DE
                LD   A, (HL)
                LD   (RenderPathTileY), A
                RET

Render_RouteBeginCmd:
                LD   HL, #04FF
                LD   DE, #FFFF
                CALL Render_CmdBufWrite32
                LD   HL, #1000
                LD   DE, #00FF
                CALL Render_CmdBufWrite32
                LD   HL, #0B00
                LD   DE, #0014
                CALL Render_CmdBufWrite32
                LD   HL, #0500
                LD   DE, #0002
                CALL Render_CmdBufWrite32     ; BITMAP_HANDLE 2
                LD   HL, ((#2A000000 | ROUTE_PALETTE_RAMG) >> 16) & #FFFF
                LD   DE, (#2A000000 | ROUTE_PALETTE_RAMG) & #FFFF
                CALL Render_CmdBufWrite32     ; PALETTE_SOURCE — норм. палитра (этот ход)
                LD   HL, #0600
                LD   DE, #0000
                CALL Render_CmdBufWrite32
                LD   HL, #1500
                LD   DE, #00A0
                CALL Render_CmdBufWrite32
                LD   HL, #1700
                LD   DE, #0000
                CALL Render_CmdBufWrite32
                LD   HL, #1900
                LD   DE, #00A0
                CALL Render_CmdBufWrite32
                LD   HL, #1F00
                LD   DE, #0001
                CALL Render_CmdBufWrite32
                RET

Render_RouteEndCmd:
                LD   HL, #2100
                LD   DE, #0000
                CALL Render_CmdBufWrite32
                LD   HL, #0B00
                LD   DE, #0008
                CALL Render_CmdBufWrite32
                RET

Render_WriteRouteSpriteCmd:
                CALL Render_LoadRouteSprite
                LD   A, (RenderRouteAddrHigh)
                LD   H, #01
                LD   L, A
                LD   DE, (RenderRouteAddrLow)
                CALL Render_CmdBufWrite32

                LD   A, (RenderRouteStride)
                ADD  A, A
                LD   D, A
                LD   A, (RenderRouteHeight)
                LD   E, A
                LD   HL, #0778                ; LAYOUT PALETTED4444 (fmt 15) — route paletted
                CALL Render_CmdBufWrite32

                LD   A, (RenderRouteSizeW)
                ADD  A, A
                LD   D, A
                LD   A, (RenderRouteSizeH)
                LD   E, A
                LD   HL, #0800
                CALL Render_CmdBufWrite32

                LD   A, (RenderPathTileX)
                CALL Tile_MulA32ToHL
                LD   DE, (RenderRouteDrawOX)
                ADD  HL, DE
                if VIEWPORT_DL_PACK
                if RUNTIME_TILEMAP_RENDER
                else
                LD   A, (ViewportOriginX)
                CALL Render_WorldXToViewportHL
                endif
                endif
                CALL Render_ScaleHL_8_5_ToVertex
                if VIEWPORT_DL_PACK
                if RUNTIME_TILEMAP_RENDER
                LD   DE, (RuntimeOriginBaseX16)
                OR   A
                SBC  HL, DE
                endif
                endif
                LD   (RenderPathVertexX), HL

                LD   A, (RenderPathTileY)
                CALL Tile_MulA32ToHL
                LD   DE, (RenderRouteDrawOY)
                ADD  HL, DE
                if VIEWPORT_DL_PACK
                if RUNTIME_TILEMAP_RENDER
                else
                LD   A, (ViewportOriginY)
                CALL Render_WorldYToViewportHL
                endif
                endif
                CALL Render_ScaleHL_8_5_ToVertex
                if VIEWPORT_DL_PACK
                if RUNTIME_TILEMAP_RENDER
                LD   DE, (RuntimeOriginBaseY16)
                OR   A
                SBC  HL, DE
                endif
                endif
                LD   (RenderPathVertexY), HL
                JP   Render_WriteVertex2FCmd

Render_LoadRouteSprite:
                LD   A, (RenderRouteSpriteIndex)
                LD   E, A
                LD   D, 0
                LD   H, D
                LD   L, E
                ADD  HL, HL
                ADD  HL, HL
                PUSH HL
                ADD  HL, HL
                POP  DE
                ADD  HL, DE
                LD   DE, #C000 + ROUTE_TABLE_ADDR
                ADD  HL, DE
                PUSH HL
                GetPage3
                LD   (.RestorePage), A
                SetPage3 ROUTE_TABLE_PAGE
                POP  HL
                LD   A, (HL)
                LD   (RenderRouteAddrHigh), A
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   (RenderRouteAddrLow), DE
                LD   A, (HL)
                LD   (RenderRouteHeight), A
                INC  HL
                LD   A, (HL)
                LD   (RenderRouteStride), A
                INC  HL
                LD   A, (HL)
                LD   (RenderRouteSizeW), A
                INC  HL
                LD   A, (HL)
                LD   (RenderRouteSizeH), A
                INC  HL
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   (RenderRouteDrawOX), DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (RenderRouteDrawOY), DE
.RestorePage   EQU $+1
                LD   A, #00
                SetPage3_A
                RET

Render_RouteSpriteIndex:
                CALL Render_RouteTurnOffset
                CP   ROUTE_DIR_UNKNOWN
                JR   Z, .bad
                LD   (RenderRouteTurnOffset), A
                LD   A, (RenderPathTileX)
                LD   B, A
                LD   A, (RenderPathTileY)
                LD   C, A
                CALL Render_RouteCostBase
                LD   HL, RenderRouteTurnOffset
                ADD  A, (HL)
                RET
.bad:           XOR  A
                RET

Render_RouteTurnOffset:
                LD   A, (RenderPathFromDir)
                ADD  A, A
                ADD  A, A
                ADD  A, A
                LD   E, A
                LD   A, (RenderPathToDir)
                ADD  A, E
                LD   E, A
                LD   D, 0
                LD   HL, RouteTurnOffsetTable
                ADD  HL, DE
                LD   A, (HL)
                RET

Render_RouteCostBase:
                PUSH BC
                CALL Map_GetTilePathFlags
                POP  BC
                AND  PATH_FLAG_ROAD
                JR   Z, .ground
                LD   A, 1
                RET
.ground:        CALL Map_GetTilePathCost
                CP   200
                JR   Z, .cost200
                CP   175
                JR   Z, .cost175
                CP   150
                JR   Z, .cost150
                CP   125
                JR   Z, .cost125
                CP   100
                JR   Z, .cost100
                LD   A, 1
                RET
.cost200:       LD   A, 121
                RET
.cost175:       LD   A, 97
                RET
.cost150:       LD   A, 73
                RET
.cost125:       LD   A, 49
                RET
.cost100:       LD   A, 25
                RET

Render_DirectionPrevToCurrent:
                LD   A, (RenderPathPrevX)
                LD   B, A
                LD   A, (RenderPathPrevY)
                LD   C, A
                LD   A, (RenderPathTileX)
                LD   D, A
                LD   A, (RenderPathTileY)
                LD   E, A
                JP   Render_DirectionFromBCToDE

Render_DirectionCurrentToNext:
                LD   A, (RenderPathTileX)
                LD   B, A
                LD   A, (RenderPathTileY)
                LD   C, A
                LD   A, (RenderPathNextX)
                LD   D, A
                LD   A, (RenderPathNextY)
                LD   E, A

Render_DirectionFromBCToDE:
                LD   A, D
                CP   B
                JR   C, .left_col
                JR   Z, .same_col
.right_col:     LD   A, E
                CP   C
                JR   C, .top_right
                JR   Z, .right
                LD   A, 4
                RET
.top_right:     LD   A, 2
                RET
.right:         LD   A, 3
                RET
.same_col:      LD   A, E
                CP   C
                JR   C, .top
                JR   Z, .unknown
                LD   A, 5
                RET
.top:           LD   A, 1
                RET
.left_col:      LD   A, E
                CP   C
                JR   C, .top_left
                JR   Z, .left
                LD   A, 6
                RET
.top_left:      XOR  A
                RET
.left:          LD   A, 7
                RET
.unknown:       LD   A, ROUTE_DIR_UNKNOWN
                RET

Render_WriteVertex2FCmd:
                LD   HL, (RenderPathVertexX)
                SRL  H
                RR   L
                LD   A, H
                OR   #40
                LD   B, A
                LD   C, L
                LD   DE, (RenderPathVertexY)
                LD   A, (RenderPathVertexX)
                AND  1
                JR   Z, .low_ok
                LD   A, D
                OR   #80
                LD   D, A
.low_ok:        LD   H, B
                LD   L, C
                JP   Render_CmdBufWrite32

Render_PathTileVisible:
                LD   A, (RenderPathTileX)
                LD   B, A
                INC  B
                LD   A, (ViewportOriginX)
                CP   B
                JR   Z, .x_min_ok
                JR   C, .x_min_ok
                XOR  A
                RET
.x_min_ok:      LD   A, (ViewportOriginX)
                ADD  A, GAME_VIEW_TILE_W
                CP   B
                JR   NC, .x_ok
                XOR  A
                RET
.x_ok:          LD   A, (RenderPathTileY)
                LD   B, A
                INC  B
                LD   A, (ViewportOriginY)
                CP   B
                JR   Z, .y_min_ok
                JR   C, .y_min_ok
                XOR  A
                RET
.y_min_ok:      LD   A, (ViewportOriginY)
                ADD  A, GAME_VIEW_TILE_H
                CP   B
                JR   NC, .visible
                XOR  A
                RET
.visible:       LD   A, 1
                OR   A
                RET

RouteTurnOffsetTable:
                ; from: TL,T,TR,R,BR,B,BL,L; to: TL,T,TR,R,BR,B,BL,L.
                DEFB 15, 16, 17, 18, ROUTE_DIR_UNKNOWN, 4, 5, 6
                DEFB 7, 8, 17, 18, 19, ROUTE_DIR_UNKNOWN, 5, 6
                DEFB 7, 0, 9, 18, 19, 20, ROUTE_DIR_UNKNOWN, 6
                DEFB 7, 0, 1, 10, 19, 20, 21, ROUTE_DIR_UNKNOWN
                DEFB ROUTE_DIR_UNKNOWN, 0, 1, 2, 11, 20, 21, 22
                DEFB 16, ROUTE_DIR_UNKNOWN, 1, 2, 3, 12, 21, 22
                DEFB 23, 16, ROUTE_DIR_UNKNOWN, 2, 3, 4, 13, 22
                DEFB 23, 16, 17, ROUTE_DIR_UNKNOWN, 3, 4, 5, 14

Render_TileCenterAToViewportVertexX:
                CALL Tile_MulA32ToHL
                LD   DE, 16
                ADD  HL, DE
                if VIEWPORT_DL_PACK
                if RUNTIME_TILEMAP_RENDER
                else
                LD   A, (ViewportOriginX)
                CALL Render_WorldXToViewportHL
                endif
                endif
                CALL Render_ScaleHL_8_5_ToVertex
                if RUNTIME_TILEMAP_RENDER
                LD   DE, (RuntimeOriginBaseX16)
                OR   A
                SBC  HL, DE
                endif
                RET

Render_TileCenterAToViewportVertexY:
                CALL Tile_MulA32ToHL
                LD   DE, 16
                ADD  HL, DE
                if VIEWPORT_DL_PACK
                if RUNTIME_TILEMAP_RENDER
                else
                LD   A, (ViewportOriginY)
                CALL Render_WorldYToViewportHL
                endif
                endif
                CALL Render_ScaleHL_8_5_ToVertex
                if RUNTIME_TILEMAP_RENDER
                LD   DE, (RuntimeOriginBaseY16)
                OR   A
                SBC  HL, DE
                endif
                RET

Render_ObjectViewTableEntry:
                if RUNTIME_TILEMAP_RENDER
                ; index = originY * OBJECT_VIEW_STRIDE + originX, entry size 5.
                ; STRIDE = число origin по X (max_x+1). Раньше тут был зашит ×17,
                ; а таблица упакована со stride OBJECT_VIEW_STRIDE → при originY>0
                ; читался чужой пакет объектов (спрайты «в воде/где попало»).
                LD   A, (ViewportOriginY)
                LD   HL, 0
                LD   DE, OBJECT_VIEW_STRIDE
                OR   A
                JR   Z, .add_x
.mul_stride:    ADD  HL, DE
                DEC  A
                JR   NZ, .mul_stride
.add_x:         LD   A, (ViewportOriginX)
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                ; HL = index; запись OBJECT_VIEW_ENTRY_SIZE=7 байт → HL*7
                ; (page1 + off2 + bottom_size2 + top_size2). Раньше было ×5.
                PUSH HL          ; ×1
                ADD  HL, HL      ; ×2
                PUSH HL          ; ×2
                ADD  HL, HL      ; ×4
                POP  DE          ; DE = ×2
                ADD  HL, DE      ; ×6
                POP  DE          ; DE = ×1
                ADD  HL, DE      ; ×7
                LD   DE, ObjectViewDL_Table
                ADD  HL, DE
                endif
                RET

Runtime_UpdateTranslate:
                if RUNTIME_TILEMAP_RENDER
                LD   A, (ViewportOriginX)
                CALL Runtime_OriginTileToVertexHL
                LD   (RuntimeOriginBaseX16), HL
                PUSH HL
                LD   HL, (ViewportPixelX)
                CALL Render_ScaleHL_8_5_ToVertex
                EX   DE, HL
                POP  HL
                OR   A
                SBC  HL, DE
                LD   DE, GAME_VIEW_X16
                ADD  HL, DE
                LD   (RuntimeDL_TranslateX_Low), HL
                LD   (RuntimeDL_ObjectTranslateX_Low), HL
                PUSH HL
                CALL Runtime_WriteTranslateXHigh
                POP  HL
                LD   DE, RUNTIME_LEFT_SCREEN_X16
                ADD  HL, DE
                LD   (RuntimeDL_TranslateXRight_Low), HL
                CALL Runtime_WriteTranslateXRightHigh
                LD   A, (ViewportOriginY)
                CALL Runtime_OriginTileToVertexHL
                LD   (RuntimeOriginBaseY16), HL
                PUSH HL
                LD   HL, (ViewportPixelY)
                CALL Render_ScaleHL_8_5_ToVertex
                EX   DE, HL
                POP  HL
                OR   A
                SBC  HL, DE
                LD   DE, GAME_VIEW_Y16
                ADD  HL, DE
                LD   (RuntimeDL_TranslateY_Low), HL
                LD   (RuntimeDL_ObjectTranslateY_Low), HL
                CALL Runtime_WriteTranslateYHigh
                endif
                RET

Runtime_WriteTranslateXHigh:
                if RUNTIME_TILEMAP_RENDER
                LD   A, H
                AND  #80
                LD   HL, #2B00
                JR   Z, .store
                INC  L
.store:         LD   (RuntimeDL_TranslateX_High), HL
                LD   (RuntimeDL_ObjectTranslateX_High), HL
                endif
                RET

Runtime_WriteTranslateXRightHigh:
                if RUNTIME_TILEMAP_RENDER
                LD   A, H
                AND  #80
                LD   HL, #2B00
                JR   Z, .store
                INC  L
.store:         LD   (RuntimeDL_TranslateXRight_High), HL
                endif
                RET

Runtime_WriteTranslateYHigh:
                if RUNTIME_TILEMAP_RENDER
                LD   A, H
                AND  #80
                LD   HL, #2C00
                JR   Z, .store
                INC  L
.store:         LD   (RuntimeDL_TranslateY_High), HL
                LD   (RuntimeDL_ObjectTranslateY_High), HL
                endif
                RET

Runtime_OriginTileToVertexHL:
                if RUNTIME_TILEMAP_RENDER
                CALL Tile_MulA32ToHL
                CALL Render_ScaleHL_8_5_ToVertex
                endif
                RET

Runtime_NegativePixelToHL:
                if RUNTIME_TILEMAP_RENDER
                CALL Render_ScaleHL_8_5_ToVertex
                EX   DE, HL
                LD   HL, 0
                OR   A
                SBC  HL, DE
                endif
                RET

RuntimeOriginBaseX16:
                DEFW 0
RuntimeOriginBaseY16:
                DEFW 0
RuntimeVertexX16:
                DEFW 0

Render_DxtUpdateScrollMatrix:
                if BG_DXT_RAW_SIZE
                if BG_DXT_ANCHORED_WINDOW
                CALL Render_DxtViewportXFromAnchor
                else
                LD   HL, (ViewportPixelX)
                if BG_DXT_FULLMAP
                else
                LD   A, L
                AND  31
                LD   L, A
                LD   H, 0
                endif
                endif
                XOR  A
                LD   (BG_DXT_MASK_C_LOW), A
                LD   (BG_DXT_MASK_C_LOW + 1), HL
                CALL Render_DxtMulHLBy64ToAHL
                LD   (BG_DXT_COLOR_C_LOW), HL
                LD   (BG_DXT_COLOR_C_LOW + 2), A

                if BG_DXT_ANCHORED_WINDOW
                CALL Render_DxtViewportYFromAnchor
                else
                LD   HL, (ViewportPixelY)
                if BG_DXT_FULLMAP
                else
                LD   A, L
                AND  31
                LD   L, A
                LD   H, 0
                endif
                endif
                XOR  A
                LD   (BG_DXT_MASK_F_LOW), A
                LD   (BG_DXT_MASK_F_LOW + 1), HL
                CALL Render_DxtMulHLBy64ToAHL
                LD   (BG_DXT_COLOR_F_LOW), HL
                LD   (BG_DXT_COLOR_F_LOW + 2), A
                endif
                RET

Render_DxtViewportXFromAnchor:
                if BG_DXT_RAW_SIZE
                LD   A, (BackgroundDxtOriginX)
                CALL Render_DxtTileMul32ToDE
                LD   HL, (ViewportPixelX)
                OR   A
                SBC  HL, DE
                endif
                RET

Render_DxtViewportYFromAnchor:
                if BG_DXT_RAW_SIZE
                LD   A, (BackgroundDxtOriginY)
                CALL Render_DxtTileMul32ToDE
                LD   HL, (ViewportPixelY)
                OR   A
                SBC  HL, DE
                endif
                RET

Render_DxtTileMul32ToDE:
                if BG_DXT_RAW_SIZE
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                EX   DE, HL
                endif
                RET

Render_DxtMulHLBy64ToAHL:
                if BG_DXT_RAW_SIZE
                LD   A, H
                ADD  A, A
                SBC  A, A
                ADD  HL, HL
                RLA
                ADD  HL, HL
                RLA
                ADD  HL, HL
                RLA
                ADD  HL, HL
                RLA
                ADD  HL, HL
                RLA
                ADD  HL, HL
                RLA
                endif
                RET

Runtime_MapIXFromOrigin:
                if RUNTIME_TILEMAP_RENDER
                LD   HL, 0
                LD   A, (ViewportOriginY)
                LD   B, A
                LD   DE, MAP_TERRAIN_CELL_STRIDE * MAP_TERRAIN_CELL_ENTRY_SIZE
                OR   A
                JR   Z, .x
.yloop:         ADD  HL, DE
                DJNZ .yloop
.x:             LD   A, (ViewportOriginX)
                PUSH HL
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                LD   E, L
                LD   D, H
                ADD  HL, HL
                ADD  HL, DE
                EX   DE, HL
                POP  HL
                ADD  HL, DE
                LD   DE, #C000 + MAP_TERRAIN_CELLS_ADDR
                ADD  HL, DE
                PUSH HL
                POP  IX
                endif
                RET

Runtime_CopyVertex:
                if RUNTIME_TILEMAP_RENDER
RuntimeDestPtr EQU $+1
                LD   DE, #0000
                LD   A, (IX + 0)
                LD   C, A
                AND  #7F
                LD   B, A
                LD   A, C
                RLCA
                AND  #01
                LD   C, A
                LD   A, (IX + 1)
                AND  #0F
                ADD  A, A
                OR   C
                LD   (DE), A
                INC  DE
                XOR  A
                LD   (DE), A
                INC  DE
                LD   (DE), A
                INC  DE
                LD   A, #05
                LD   (DE), A
                INC  DE
                LD   A, B
                LD   (DE), A
                INC  DE
                XOR  A
                LD   (DE), A
                INC  DE
                LD   (DE), A
                INC  DE
                LD   A, #06
                LD   (DE), A
                INC  DE
                LD   (RuntimeDestPtr), DE
                LD   L, (IX + 2)
                LD   H, (IX + 3)
                LD   DE, (RuntimeOriginBaseX16)
                OR   A
                SBC  HL, DE
                LD   (RuntimeVertexX16), HL
                LD   L, (IX + 4)
                LD   H, (IX + 5)
                LD   DE, (RuntimeOriginBaseY16)
                OR   A
                SBC  HL, DE
                LD   A, H
                AND  #7F
                LD   H, A
                LD   A, (RuntimeVertexX16)
                AND  #01
                JR   Z, .xbit_done
                SET  7, H
.xbit_done:     LD   DE, (RuntimeDestPtr)
                LD   A, L
                LD   (DE), A
                INC  DE
                LD   A, H
                LD   (DE), A
                INC  DE
                LD   HL, (RuntimeVertexX16)
                SRL  H
                RR   L
                SET  6, H
                LD   A, L
                LD   (DE), A
                INC  DE
                LD   A, H
                LD   (DE), A
                INC  DE
                LD   (RuntimeDestPtr), DE
                endif
                RET

Render_ViewportPack:
                if VIEWPORT_DL_PACK
                GetPage3
                LD   (.RestorePage), A
                CALL Render_ViewportTableEntry
                LD   A, (HL)
                LD   (.ViewportPage), A
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   DE, #C000
                ADD  HL, DE
                LD   (.ViewportSrc), HL
.ViewportPage  EQU $+1
                LD   A, #00
                SetPage3_A
.ViewportSrc   EQU $+1
                LD   HL, #C000
                LD   BC, VIEWPORT_DL_SIZE
                LD   DE, 0
                CALL FT.WriteDL
.RestorePage   EQU $+1
                LD   A, #00
                SetPage3_A
                endif
                RET

Render_ViewportTableEntry:
                if VIEWPORT_DL_PACK
                LD   A, (ViewportOriginY)
                LD   E, A
                LD   D, 0
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE
                LD   A, (ViewportOriginX)
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                PUSH HL
                ADD  HL, HL
                POP  DE
                ADD  HL, DE
                LD   DE, ViewportDL_Table
                ADD  HL, DE
                endif
                RET

Render_HeroMarker:
                CALL HeroMarker_UpdateDLPosition
                LD   HL, HERO_MARKER_DL
                LD   BC, HERO_MARKER_DL_SIZE
                if VIEWPORT_DL_PACK
                if RUNTIME_TILEMAP_RENDER
                LD   DE, RUNTIME_OBJECT_DL_SIZE - 4
                else
                LD   DE, VIEWPORT_DL_SIZE - 4
                endif
                else
                LD   DE, ADVENTURE_DL_SIZE - 4
                endif
                CALL FT.WriteDL
                RET

Render_HeroMarkerCmd:
                CALL HeroMarker_UpdateDLPosition
                LD   HL, HERO_MARKER_DL
                LD   BC, HERO_MARKER_DL_SIZE - 4
                CALL Render_CmdBufCopy
                RET

Render_Actor:
                ifdef DYNAMIC_ACTOR_RAMG
                CALL Actor_UpdateDLPosition
                LD   HL, ACTOR_DL
                LD   BC, ACTOR_DL_SIZE
                if VIEWPORT_DL_PACK
                if RUNTIME_TILEMAP_RENDER
                LD   DE, RUNTIME_OBJECT_DL_SIZE + HERO_MARKER_DL_SIZE - 8
                else
                LD   DE, VIEWPORT_DL_SIZE + HERO_MARKER_DL_SIZE - 8
                endif
                else
                LD   DE, ADVENTURE_DL_SIZE + HERO_MARKER_DL_SIZE - 8
                endif
                CALL FT.WriteDL
                endif
                RET

Render_ActorCmd:
                ifdef DYNAMIC_ACTOR_RAMG
                CALL Actor_UpdateDLPosition
                LD   HL, ACTOR_DL
                LD   BC, ACTOR_DL_SIZE - 4
                CALL Render_CmdBufCopy
                endif
                RET

Render_Cursor:
                CALL Cursor_UpdateDLPosition
                LD   HL, CURSOR_DL
                LD   BC, CURSOR_DL_SIZE
                if VIEWPORT_DL_PACK
                ifdef DYNAMIC_ACTOR_RAMG
                if RUNTIME_TILEMAP_RENDER
                LD   DE, RUNTIME_OBJECT_DL_SIZE + HERO_MARKER_DL_SIZE + ACTOR_DL_SIZE - 12
                else
                LD   DE, VIEWPORT_DL_SIZE + HERO_MARKER_DL_SIZE + ACTOR_DL_SIZE - 12
                endif
                else
                if RUNTIME_TILEMAP_RENDER
                LD   DE, RUNTIME_OBJECT_DL_SIZE + HERO_MARKER_DL_SIZE - 8
                else
                LD   DE, VIEWPORT_DL_SIZE + HERO_MARKER_DL_SIZE - 8
                endif
                endif
                else
                ifdef DYNAMIC_ACTOR_RAMG
                LD   DE, ADVENTURE_DL_SIZE + HERO_MARKER_DL_SIZE + ACTOR_DL_SIZE - 12
                else
                LD   DE, ADVENTURE_DL_SIZE + HERO_MARKER_DL_SIZE - 8
                endif
                endif
                CALL FT.WriteDL
                RET

Render_CursorCmd:
                CALL Cursor_UpdateDLPosition
                LD   HL, CURSOR_DL
                LD   BC, CURSOR_DL_SIZE
                CALL Render_CmdBufCopy
                RET

Render_AdventureUICmd:
                LD   HL, AdventureUI_DL
                LD   BC, AdventureUI_DL_SIZE
                CALL Render_CmdBufCopy
                RET

Render_RightPanelCmd:
                LD   A, (ActiveHeroIndex)
                ; TODO: выбор MINIPORT в зависимости от героя. Пока статичный 0-й кадр

                ; Вычисление кадра MOBILITY (0..25)
                ; В Z80 HeroMovePoints = 0..16.
                ; Кадр = HeroMovePoints * 1.5 (A + A/2). Для 16 будет 24 (макс 25).
                LD   A, (HeroMovePoints)
                SRL  A
                LD   B, A
                LD   A, (HeroMovePoints)
                ADD  A, B
                CP   26
                JR   C, .ok
                LD   A, 25
.ok:
                ; A содержит индекс кадра (0..25)
                ; Читаем адрес из MobilityFrameTable (3 байта на запись)
                LD   B, A
                ADD  A, A                      ; A = A * 2
                ADD  A, B                      ; A = A * 3
                LD   C, A
                LD   B, 0
                LD   HL, MobilityFrameTable
                ADD  HL, BC                    ; HL указывает на 3 байта адреса
                
                ; Читаем 3 байта адреса
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   A, (HL)
                
                ; Пишем в DL (младшие 3 байта FT_BITMAP_SOURCE)
                LD   (UI_RightPanelMobilityAddr + 0), DE
                LD   (UI_RightPanelMobilityAddr + 2), A

                LD   HL, UI_RightPanel_DL
                LD   BC, UI_RightPanel_DL_SIZE
                CALL Render_CmdBufCopy
                RET

Render_AdvButtonsCmd:
                LD   HL, UI_BtnStateInit_DL
                LD   BC, UI_BtnStateInit_DL_SIZE
                CALL Render_CmdBufCopy

                LD   B, 8
                LD   C, 0                       ; индекс кнопки (0..7)
.loop:
                PUSH BC
                ; Проверка, нажата ли эта кнопка сейчас
                LD   A, (UI_ButtonPressed)
                CP   C
                JR   Z, .is_pressed
                
                ; Не нажата, проверяем состояние логики
                LD   HL, UI_ButtonStates
                LD   B, 0
                ADD  HL, BC                     ; HL = UI_ButtonStates + i
                LD   A, (HL)
                JR   .get_color

.is_pressed:
                ; Кнопка визуально зажата
                LD   HL, UI_ButtonStates
                LD   B, 0
                ADD  HL, BC
                LD   A, (HL)
                CP   2
                JR   Z, .inactive_pressed
                CP   3
                JR   Z, .get_color               ; Disabled кнопки не получают pressed-стейт
                LD   A, 1
                JR   .get_color

.inactive_pressed:
                LD   A, 4

.get_color:
                ; Затемнить disabled/inactive кнопки как в оригинале: FT_COLOR_RGB UI_BtnColors[A]
                ; перед отрисовкой (A = индекс состояния 0..4). +4Б/кнопку CMD-FIFO.
                PUSH AF
                CALL Render_AdvBtnColor
                POP  AF
                POP  BC
                PUSH BC
                CP   1
                JR   Z, .use_pressed
                CP   4
                JR   Z, .use_pressed

.use_normal:
                LD   HL, UI_BtnNormalTab
                LD   B, UI_BtnNormal_DL_SIZE
                JR   .draw

.use_pressed:
                LD   HL, UI_BtnPressedTab
                LD   B, UI_BtnPressed_DL_SIZE

.draw:
                ; HL = Tab_Base, B = size
                LD   A, C
                ADD  A, A
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL                     ; HL = адрес DL-блока
                LD   C, B
                LD   B, 0
                CALL Render_CmdBufCopy
                
                POP  BC
                INC  C
                DJNZ .loop
                
                LD   DE, 0
                LD   HL, #2100                  ; FT_END
                CALL Render_CmdBufWrite32
                RET

; A = индекс состояния (0..4) → эмит FT_COLOR_RGB UI_BtnColors[A] в CMD-буфер.
; Затемняет disabled(3)/inactive(2/4) кнопки как в оригинале (active/pressed = белый).
Render_AdvBtnColor:
                LD   L, A
                LD   H, 0
                LD   E, L
                LD   D, H
                ADD  HL, HL                     ; 2A
                ADD  HL, DE                     ; 3A
                LD   DE, UI_BtnColors
                ADD  HL, DE                     ; HL → {r,g,b}
                LD   A, (HL)                    ; r
                INC  HL
                LD   B, (HL)                    ; g
                INC  HL
                LD   C, (HL)                    ; b
                LD   H, #04
                LD   L, A                        ; HL = #0400|r  (FT_COLOR_RGB high16)
                LD   D, B
                LD   E, C                        ; DE = (g<<8)|b (low16)
                JP   Render_CmdBufWrite32        ; эмит 32-бит COLOR_RGB + RET

UI_BtnColors:
                DEFB 255, 255, 255 ; 0: normal
                DEFB 255, 255, 255 ; 1: pressed
                DEFB 160, 160, 160 ; 2: inactive
                DEFB  96,  96,  96 ; 3: disabled
                DEFB 160, 160, 160 ; 4: inactive_pressed

Math_Div8:
                ; A = A / C
                ; Возвращает A = частное
                ; Простейшее деление вычитанием (A < 255)
                LD   B, 0
.div_loop:
                CP   C
                JR   C, .div_done
                SUB  C
                INC  B
                JR   .div_loop
.div_done:
                LD   A, B
                RET

UI_RightPanel_DL:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_PALETTE_SOURCE OBJECT_PALETTE_RAMG
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
                FT_BEGIN FT_BITMAPS

                ; 1. Подложка-рамка hero-иконки (PORTXTRA, 46×22): слоты mobility(лев)/портрет/mana(прав).
                ; Сажаем в ячейку 0 героев: фон ячейки ADVBORD @ (480,176), контент инсет +5,+5 → (485,181).
                ; (Было (488,168) — на 13px выше ячейки, налезало на ICON-border разделитель.)
                FT_BITMAP_SOURCE UI_PORTXTRA_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, UI_PORTXTRA_STRIDE, UI_PORTXTRA_H
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, UI_PORTXTRA_W * 16 / 10, UI_PORTXTRA_H * 16 / 10
                FT_VERTEX2F 485 * 256 / 10, 181 * 256 / 10

                ; 2. Портрет героя (MINIPORT, 30×22) — инсет +7 от левого края PORTXTRA-бара (heroes.cpp barw=7):
                ; X = 485 + 7 = 492; Y = 181 (выровнен по верху рамки).
                FT_BITMAP_SOURCE UI_MINIPORT_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, UI_MINIPORT_STRIDE, UI_MINIPORT_H
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, UI_MINIPORT_W * 16 / 10, UI_MINIPORT_H * 16 / 10
                FT_VERTEX2F 492 * 256 / 10, 181 * 256 / 10

                ; 3. Мана (MANA) — убрана из покадрового DL (всегда пустой 0-кадр, ел бюджет
                ;    CMD-FIFO). Вернуть при реализации очков заклинаний.

                ; 4. Мувпоинты (MOBILITY, 7×22) — левый слот PORTXTRA-рамки, тот же сдвиг → (485,181).
UI_RightPanelMobilityAddr:
                FT_BITMAP_SOURCE UI_MOBILITY_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, UI_MOBILITY_STRIDE, UI_MOBILITY_H
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, UI_MOBILITY_W * 16 / 10, UI_MOBILITY_H * 16 / 10
                FT_VERTEX2F 485 * 256 / 10, 181 * 256 / 10

UI_RightPanel_DL_SIZE EQU $ - UI_RightPanel_DL

UI_BtnStateInit_DL:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_PALETTE_SOURCE OBJECT_PALETTE_RAMG
                FT_COLOR_RGB 255, 255, 255      ; белый один раз (per-button COLOR_RGB убран — бюджет FIFO)
                FT_BEGIN FT_BITMAPS
UI_BtnStateInit_DL_SIZE EQU $ - UI_BtnStateInit_DL

; Глобальный курсор мыши (резидент, для ЛЮБОЙ сцены) — настоящий POINTER-спрайт
; (ADVMCO[0], ARGB4444) из ПОСТОЯННОЙ зоны RAM_G (#0E0000), резидентно загруженной
; Cursor_GlobalUpload. Позиция из мыши; спрайт 0 = pointer. Переиспользует тот же
; Render_CursorCmd, что и adventure (единый драйвер). CURSOR_DL содержит FT_DISPLAY —
; вызывать ПОСЛЕДНИМ в кадре сцены (отдельный DISPLAY не нужен).
Render_GlobalCursor:
                CALL Input_MouseX
                LD   (CursorPixelX), HL
                CALL Input_MouseY
                LD   (CursorPixelY), HL
                XOR  A
                LD   (CursorSpriteIndex), A      ; 0 = pointer (стрелка)
                JP   Render_CursorCmd

; Прямоугольник текущего вьюпорта на мини-карте (как RedrawCursor в fheroes2):
; рамка LINE_STRIP цвета RADARCOLOR 0xB5 = RGB(216,124,124) в логических коорд.
;   x0 = UI_RADAR_X + originX*MINIMAP_TILE_PX, ширина = MINIMAP_RECT_LOGICAL,
; отмасштабированных в физические vertex-единицы. Двигается при скролле.
; ОРИГИНАЛ рисует пунктир (DrawBorder skipFactor=6, 5px/1пропуск), но пунктир =
; ~40 сегментов LINES ≈ +280 байт FIFO, а запас всего 124 (3972/4096). Поэтому
; СПЛОШНАЯ — пунктир не влезает и съел бы бюджет тумана. По решению пользователя.
Render_MinimapRectCmd:
                LD   A, (ViewportOriginX)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                  ; originX * 4 (MINIMAP_TILE_PX)
                LD   DE, UI_RADAR_X
                ADD  HL, DE
                PUSH HL
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (MinimapRectX0), HL
                POP  HL
                LD   DE, MINIMAP_RECT_LOGICAL
                ADD  HL, DE
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (MinimapRectX1), HL
                LD   A, (ViewportOriginY)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                  ; originY * 4
                LD   DE, UI_RADAR_Y
                ADD  HL, DE
                PUSH HL
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (MinimapRectY0), HL
                POP  HL
                LD   DE, MINIMAP_RECT_LOGICAL
                ADD  HL, DE
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (MinimapRectY1), HL

                LD   HL, #04D8
                LD   DE, #7C7C
                CALL Render_CmdBufWrite32     ; COLOR_RGB 216,124,124 (RADARCOLOR 0xB5)
                LD   HL, #1000
                LD   DE, #00FF
                CALL Render_CmdBufWrite32     ; COLOR_A 255
                LD   HL, #0E00
                LD   DE, #000D
                CALL Render_CmdBufWrite32     ; LINE_WIDTH 13 (полуширина → ~1px радара, как DrawBorder 1px)
                LD   HL, #1F00
                LD   DE, #0004
                CALL Render_CmdBufWrite32     ; BEGIN LINE_STRIP
                CALL .v_x0y0
                CALL .v_x1y0
                CALL .v_x1y1
                CALL .v_x0y1
                CALL .v_x0y0
                LD   HL, #2100
                LD   DE, #0000
                CALL Render_CmdBufWrite32     ; END
                RET
.v_x0y0:        LD   HL, (MinimapRectX0)
                LD   (RenderPathVertexX), HL
                LD   HL, (MinimapRectY0)
                LD   (RenderPathVertexY), HL
                JP   Render_WriteVertex2FCmd
.v_x1y0:        LD   HL, (MinimapRectX1)
                LD   (RenderPathVertexX), HL
                LD   HL, (MinimapRectY0)
                LD   (RenderPathVertexY), HL
                JP   Render_WriteVertex2FCmd
.v_x1y1:        LD   HL, (MinimapRectX1)
                LD   (RenderPathVertexX), HL
                LD   HL, (MinimapRectY1)
                LD   (RenderPathVertexY), HL
                JP   Render_WriteVertex2FCmd
.v_x0y1:        LD   HL, (MinimapRectX0)
                LD   (RenderPathVertexX), HL
                LD   HL, (MinimapRectY1)
                LD   (RenderPathVertexY), HL
                JP   Render_WriteVertex2FCmd

MinimapRectX0:  DEFW 0
MinimapRectX1:  DEFW 0
MinimapRectY0:  DEFW 0
MinimapRectY1:  DEFW 0

; Цветная точка героя на мини-карте (как RedrawObjects в fheroes2): закрашенный
; квадрат размером с тайл мини-карты в позиции HeroTileX/Y, цвет игрока.
Render_MinimapHeroDotCmd:
                LD   A, (HeroTileX)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                  ; HeroTileX * 4
                LD   DE, UI_RADAR_X
                ADD  HL, DE
                PUSH HL
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (MinimapRectX0), HL
                POP  HL
                LD   DE, MINIMAP_TILE_PX
                ADD  HL, DE
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (MinimapRectX1), HL
                LD   A, (HeroTileY)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                  ; HeroTileY * 4
                LD   DE, UI_RADAR_Y
                ADD  HL, DE
                PUSH HL
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (MinimapRectY0), HL
                POP  HL
                LD   DE, MINIMAP_TILE_PX
                ADD  HL, DE
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (MinimapRectY1), HL

                LD   HL, #04A8
                LD   DE, #2020
                CALL Render_CmdBufWrite32     ; COLOR_RGB 168,32,32 = RED 0xBD (палитра владельца, interface_radar.cpp)
                LD   HL, #1F00
                LD   DE, #0009
                CALL Render_CmdBufWrite32     ; BEGIN RECTS
                LD   HL, (MinimapRectX0)
                LD   (RenderPathVertexX), HL
                LD   HL, (MinimapRectY0)
                LD   (RenderPathVertexY), HL
                CALL Render_WriteVertex2FCmd
                LD   HL, (MinimapRectX1)
                LD   (RenderPathVertexX), HL
                LD   HL, (MinimapRectY1)
                LD   (RenderPathVertexY), HL
                CALL Render_WriteVertex2FCmd
                LD   HL, #2100
                LD   DE, #0000
                CALL Render_CmdBufWrite32     ; END
                RET

; ================= Шрифт SMALFONT: вывод чисел спрайтами =================
; ПЕРЕИСПОЛЬЗУЕМЫЙ примитив (числа: ресурсы, дата, армия, цены). Спрайты цифр/
; иконок — PALETTED4444, scaled ×1.6. Кодировка как Render_WriteRouteSpriteCmd.
ResPenX:        DEFW 0          ; перо в vertex-units
ResPenY:        DEFW 0
NumVal:         DEFW 0
NumStarted:     DEFB 0
NumDivisors:    DEFW 10000, 1000, 100, 10, 1, 0

; A = A*8/5 (масштаб байта в экранные px). A до ~76 → результат до ~121.
Render_ScaleByte_8_5:
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                   ; HL = A*8
                LD   C, 0
.d:             LD   A, H
                OR   A
                JR   NZ, .sub
                LD   A, L
                CP   5
                JR   C, .done
.sub:           LD   A, L
                SUB  5
                LD   L, A
                JR   NC, .nb
                DEC  H
.nb:            INC  C
                JR   .d
.done:          LD   A, C
                RET

; Нарисовать спрайт из записи таблицы (HL → [lo,mid,hi,w,h]) пером (ResPenX,ResPenY),
; сдвинуть ResPenX вправо на scaled(w). Состояние (transform/palette/blend) — от
; предыдущего блока (Render_AdventureUICmd: transform 160, palette object, BITMAPS).
Render_DrawSpriteEntry:
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   A, (HL)
                INC  HL
                LD   C, (HL)                  ; w
                INC  HL
                LD   B, (HL)                  ; h
                LD   H, #01
                LD   L, A
                PUSH BC
                CALL Render_CmdBufWrite32     ; BITMAP_SOURCE (#01:hi : mid:lo)
                POP  BC
                LD   A, C
                ADD  A, A
                LD   D, A                     ; stride*2 = w<<9 в слове
                LD   E, B
                LD   HL, #0778
                PUSH BC
                CALL Render_CmdBufWrite32     ; BITMAP_LAYOUT PALETTED4444 stride=w h
                POP  BC
                LD   A, C
                ADD  A, A
                LD   D, A                     ; w*2 (native, без апскейла — компактно)
                LD   E, B                     ; h
                LD   HL, #0800
                PUSH BC
                CALL Render_CmdBufWrite32     ; BITMAP_SIZE w h (native, transform 256)
                POP  BC
                LD   HL, (ResPenX)
                LD   (RenderPathVertexX), HL
                LD   HL, (ResPenY)
                LD   (RenderPathVertexY), HL
                PUSH BC
                CALL Render_WriteVertex2FCmd
                POP  BC
                LD   A, C
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                   ; HL = w*16 vertex (native)
                EX   DE, HL
                LD   HL, (ResPenX)
                ADD  HL, DE
                LD   (ResPenX), HL
                RET

; Нарисовать цифру A (0-9) пером.
Render_DrawDigit:
                LD   L, A
                LD   H, 0
                LD   D, 0
                LD   E, A
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                   ; A*5
                LD   DE, DigitTable
                ADD  HL, DE
                JP   Render_DrawSpriteEntry

; Нарисовать 16-битное число HL пером (десятичное, без ведущих нулей).
Render_Number16:
                LD   (NumVal), HL
                LD   IX, NumDivisors
                XOR  A
                LD   (NumStarted), A
.loop:          LD   E, (IX+0)
                LD   D, (IX+1)
                LD   A, D
                OR   E
                JR   Z, .end                  ; divisor 0 → конец
                LD   HL, (NumVal)
                LD   B, 0
.sub:           OR   A
                SBC  HL, DE
                JR   C, .donesub
                INC  B
                JR   .sub
.donesub:       ADD  HL, DE                   ; вернуть остаток
                LD   (NumVal), HL
                LD   A, B
                OR   A
                JR   NZ, .draw
                LD   A, (NumStarted)
                OR   A
                JR   Z, .next                 ; ведущий ноль — пропуск
.draw:          LD   A, 1
                LD   (NumStarted), A
                LD   A, B
                PUSH IX
                CALL Render_DrawDigit
                POP  IX
.next:          INC  IX
                INC  IX
                JR   .loop
.end:           LD   A, (NumStarted)
                OR   A
                RET  NZ
                XOR  A
                JP   Render_DrawDigit          ; число было 0 → нарисовать "0"

; Число значащих цифр HL → A (минимум 1). Портит NumVal/IX/HL/DE/BC.
Num_DigitCount: LD   (NumVal), HL
                LD   IX, NumDivisors
                LD   C, 0                     ; счётчик
                LD   B, 0                     ; флаг started
.dc_loop:       LD   E, (IX+0)
                LD   D, (IX+1)
                LD   A, D
                OR   E
                JR   Z, .dc_end
                LD   HL, (NumVal)
                XOR  A
.dc_sub:        SBC  HL, DE                   ; (carry=0 после XOR A)
                JR   C, .dc_done
                INC  A
                OR   A                         ; сброс carry для след. SBC
                JR   .dc_sub
.dc_done:       ADD  HL, DE
                LD   (NumVal), HL
                OR   A
                JR   NZ, .dc_count
                LD   A, B
                OR   A
                JR   Z, .dc_next              ; ведущий ноль
.dc_count:      LD   B, 1
                INC  C
.dc_next:       INC  IX
                INC  IX
                JR   .dc_loop
.dc_end:        LD   A, C
                OR   A
                RET  NZ
                LD   A, 1
                RET

; Нарисовать HL центрированным относительно ResPenX (≈ как оригинал x − width/2).
; Прибл. ширина = digit_count × 5px native → сдвиг ResPenX влево на count×40 vertex-units.
Render_Number16C:
                PUSH HL
                CALL Num_DigitCount           ; A = число цифр
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L                     ; DE = count
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                   ; HL = count*5
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                   ; HL = count*40
                EX   DE, HL                   ; DE = смещение
                LD   HL, (ResPenX)
                OR   A
                SBC  HL, DE
                LD   (ResPenX), HL
                POP  HL
                JP   Render_Number16

; Ресурсная панель — RAM_G-композит (правило компромисса: панель статична, динамика
; не важна). Полный DL панели собирается в RAM_G ОДИН раз при изменении ресурсов
; (Resources_BuildPanelDL), а в кадре добавляется ОДНИМ CMD_APPEND (малый FIFO).
ResourcePanelDLSize: DEFW 0
ResourceValueAddrs: DEFW ResWood, ResMercury, ResOre, ResSulfur, ResCrystal, ResGems, ResGold
; Kingdom-вид (interface_status.cpp _drawKingdomInfo): логич. X/Y чисел в окне статуса.
; Порядок = ResourceValueAddrs: wood/mercury/ore/sulfur/crystal/gems (нижний ряд) + gold (верхний).
ResKPosX:       DEFW 495, 517, 540, 564, 588, 610, 602
ResKPosY:       DEFW 452, 452, 452, 452, 452, 452, 422
; Метки даты (SMALFONT-спрайты) + вычисленные день-недели/неделя/месяц.
DateGap:        LD   HL, (ResPenX)
                LD   DE, 80                   ; ~5px пробел между словом и числом
                ADD  HL, DE
                LD   (ResPenX), HL
                RET
; HL = запись метки [lo,mid,hi,w,h], A = число-байт → метка + пробел + число пером.
DrawLblNum:     PUSH AF
                CALL Render_DrawSpriteEntry
                CALL DateGap
                POP  AF
                LD   L, A
                LD   H, 0
                JP   Render_Number16
DateLblTable:   DEFB UI_LBL_MONTH_RAMG & #FF, (UI_LBL_MONTH_RAMG >> 8) & #FF, (UI_LBL_MONTH_RAMG >> 16) & #FF, UI_LBL_MONTH_W, UI_LBL_MONTH_H
                DEFB UI_LBL_WEEK_RAMG & #FF, (UI_LBL_WEEK_RAMG >> 8) & #FF, (UI_LBL_WEEK_RAMG >> 16) & #FF, UI_LBL_WEEK_W, UI_LBL_WEEK_H
                DEFB UI_LBL_DAY_RAMG & #FF, (UI_LBL_DAY_RAMG >> 8) & #FF, (UI_LBL_DAY_RAMG >> 16) & #FF, UI_LBL_DAY_W, UI_LBL_DAY_H
DateDow:        DEFB 0
DateWeek:       DEFB 0
DateMonth:      DEFB 0
; Блоки статус-окна (×1.6) для RAM_G-композита (НЕ покадровый DL — бюджет 4096).
; STONBACK — общий фон 144×72 @ (480,392). Оставляет TRANSFORM A=160,E=160 для следующего блока.
UI_StatusStone_DL:
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE UI_STONBACK_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, UI_STONBACK_STRIDE, UI_STONBACK_H
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, UI_STONBACK_W * 16 / 10, UI_STONBACK_H * 16 / 10
                FT_VERTEX2F 480 * 256 / 10, 392 * 256 / 10
                FT_END
UI_StatusStone_DL_SIZE EQU $ - UI_StatusStone_DL
; FUNDS: иконки RESSMALL 133×56 @ (486,395). A уже 160 от stone; в конце вернуть native A=256.
UI_StatusRessmall_DL:
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE UI_RESSMALL_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, UI_RESSMALL_STRIDE, UI_RESSMALL_H
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, UI_RESSMALL_W * 16 / 10, UI_RESSMALL_H * 16 / 10
                FT_VERTEX2F 486 * 256 / 10, 395 * 256 / 10
                FT_END
                FT_BITMAP_TRANSFORM_A 256
UI_StatusRessmall_DL_SIZE EQU $ - UI_StatusRessmall_DL
; DATE: баннер солнца/луны SUNMOON 144×25 @ (480,393). A уже 160; в конце native A=256.
UI_StatusSun_DL:
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE UI_SUNMOON_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, UI_SUNMOON_STRIDE, UI_SUNMOON_H
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, UI_SUNMOON_W * 16 / 10, UI_SUNMOON_H * 16 / 10
                FT_VERTEX2F 480 * 256 / 10, 393 * 256 / 10
                FT_END
                FT_BITMAP_TRANSFORM_A 256
UI_StatusSun_DL_SIZE EQU $ - UI_StatusSun_DL
; ARMY: спрайты монстров армии фокус-героя (MONS32 ×1.6). A уже 160 от stone; в конце native A=256.
; Раскладка ПИКСЕЛЬ-В-ПИКСЕЛЬ по fheroes2 drawMultipleMonsterLines→drawMiniMonsters (compact):
; pos=(480,392), army@(484,393,w=138); 2 стека (<3): chunk=46, cy=409; стеки posX=507(Peasant)/553(Archer);
; фигура left=posX+offset, top=cy+(37-h); общий baseline y=446. Спрайт 32×32 padded (content@ox,oy):
; Peasant w17 ox1 → box vertex (514,417); Archer w22 ox0 → box vertex (562,415). Счётчики — в .nums_army.
UI_StatusArmy_DL:
                FT_BEGIN FT_BITMAPS
                FT_BITMAP_SOURCE UI_ARMY0_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, UI_ARMY0_STRIDE, UI_ARMY0_H
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, UI_ARMY0_W * 16 / 10, UI_ARMY0_H * 16 / 10
                FT_VERTEX2F 515 * 256 / 10, 417 * 256 / 10
                FT_BITMAP_SOURCE UI_ARMY1_RAMG
                FT_BITMAP_LAYOUT FT_PALETTED4444, UI_ARMY1_STRIDE, UI_ARMY1_H
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, UI_ARMY1_W * 16 / 10, UI_ARMY1_H * 16 / 10
                FT_VERTEX2F 562 * 256 / 10, 415 * 256 / 10
                FT_END
                FT_BITMAP_TRANSFORM_A 256
UI_StatusArmy_DL_SIZE EQU $ - UI_StatusArmy_DL

; В кадре: добавить готовый DL панели (иконки + числа SMALFONT) из RAM_G композита.
Render_ResourcePanelCmd:
                LD   HL, (ResourcePanelDLSize)
                LD   A, H
                OR   L
                RET  Z                         ; панель ещё не собрана
                LD   B, H
                LD   C, L
                LD   A, (RESOURCE_PANEL_RAMG >> 16) & #FF
                LD   DE, RESOURCE_PANEL_RAMG & #FFFF
                JP   Render_CmdAppend

; Пересобрать DL панели в RAM_G. Вызывать при изменении ресурсов (Init/EndTurn/подбор).
; Перенаправляем BufferPtr копроцессора на CMD-staging (#A200, свободен вне рендера
; кадра), собираем там DL переиспользуемыми примитивами, копируем в RAM_G (FT.WriteMem).
Resources_BuildPanelDL:
                LD   HL, (FT.Coprocessor.BufferPtr)
                PUSH HL
                LD   HL, CMD_ADDRESS_PTR
                LD   (FT.Coprocessor.BufferPtr), HL
                ; --- содержимое панели ---
                LD   HL, #04FF
                LD   DE, #FFFF
                CALL Render_CmdBufWrite32     ; COLOR_RGB 255,255,255
                LD   HL, #1000
                LD   DE, #00FF
                CALL Render_CmdBufWrite32     ; COLOR_A 255
                LD   HL, #2A00 | ((OBJECT_PALETTE_RAMG >> 16) & #FF)
                LD   DE, OBJECT_PALETTE_RAMG & #FFFF
                CALL Render_CmdBufWrite32     ; PALETTE_SOURCE object
                ; Общий каменный фон STONBACK (×1.6).
                LD   HL, UI_StatusStone_DL
                LD   BC, UI_StatusStone_DL_SIZE
                CALL Render_CmdBufCopy
                ; Иконки по виду: ARMY → MONS32-спрайты, FUNDS → RESSMALL, DATE → SUNMOON.
                LD   A, (StatusState)
                CP   STATUS_DATE
                JR   Z, .icons_date
                CP   STATUS_FUNDS
                JR   Z, .icons_funds
                LD   HL, UI_StatusArmy_DL          ; ARMY (дефолт)
                LD   BC, UI_StatusArmy_DL_SIZE
                JR   .icons_copy
.icons_funds:   LD   HL, UI_StatusRessmall_DL
                LD   BC, UI_StatusRessmall_DL_SIZE
                JR   .icons_copy
.icons_date:    LD   HL, UI_StatusSun_DL
                LD   BC, UI_StatusSun_DL_SIZE
.icons_copy:    CALL Render_CmdBufCopy
                ; TRANSFORM native + BEGIN (числа поверх).
                LD   HL, #1500
                LD   DE, #0100
                CALL Render_CmdBufWrite32     ; TRANSFORM_A 256
                LD   HL, #1700
                LD   DE, #0100
                CALL Render_CmdBufWrite32     ; (как было)
                LD   HL, #1600
                LD   DE, #0000
                CALL Render_CmdBufWrite32     ; (как было)
                LD   HL, #1F00
                LD   DE, #0001
                CALL Render_CmdBufWrite32     ; BEGIN BITMAPS
                LD   A, (StatusState)
                CP   STATUS_DATE
                JP   Z, .nums_date
                CP   STATUS_FUNDS
                JP   Z, .nums_funds
                ; ARMY (дефолт): счётчики войск у правого края чанка, baseline y=432 (по drawMiniMonsters).
                ; «40» центр≈539 (чанк Peasant правый край), «4» центр≈587 (чанк Archer). Render_Number16C центрирует.
                LD   HL, 432
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (ResPenY), HL
                LD   HL, 538
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (ResPenX), HL
                LD   HL, UI_ARMY0_COUNT
                CALL Render_Number16C
                LD   HL, 587
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (ResPenX), HL
                LD   HL, UI_ARMY1_COUNT
                CALL Render_Number16C
                JP   .panel_end
.nums_funds:    ; FUNDS: 7 чисел ресурсов/золота на позициях ResKPos.
                LD   B, 0
.res_loop:      PUSH BC
                LD   A, B
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, ResKPosX
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (ResPenX), HL
                POP  BC
                PUSH BC
                LD   A, B
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, ResKPosY
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (ResPenY), HL
                POP  BC
                PUSH BC
                LD   A, B
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, ResourceValueAddrs
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   A, (DE)
                LD   L, A
                INC  DE
                LD   A, (DE)
                LD   H, A
                CALL Render_Number16C
                POP  BC
                INC  B
                LD   A, B
                CP   7
                JP   C, .res_loop
                ; Замки/города (верхний ряд RESSMALL, центрировано). Старт: 1 замок, 0 городов.
                LD   HL, 506
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (ResPenX), HL
                LD   HL, 422
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (ResPenY), HL
                LD   HL, 1                    ; замков (TODO: счётчик замков королевства)
                CALL Render_Number16C
                LD   HL, 558
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (ResPenX), HL
                LD   HL, 0                    ; городов
                CALL Render_Number16C
                JP   .panel_end
.nums_date:     ; DATE (как оригинал): "Month: M Week: W" + "Day: D" из GameDay.
                ; d=GameDay-1; dow=d mod7 +1; q=d/7; week=q mod4 +1; month=q/4 +1.
                LD   HL, (GameDay)
                DEC  HL
                LD   BC, 0                     ; q = d/7
.d7:            LD   A, H
                OR   A
                JR   NZ, .d7s
                LD   A, L
                CP   7
                JR   C, .d7done
.d7s:           LD   DE, 7
                OR   A
                SBC  HL, DE
                INC  BC
                JR   .d7
.d7done:        LD   A, L
                INC  A
                LD   (DateDow), A
                LD   A, C
                AND  3
                INC  A
                LD   (DateWeek), A
                LD   A, C
                SRL  A
                SRL  A
                INC  A
                LD   (DateMonth), A
                ; строка "Month: M  Week: W" @ y=424 (центр окна ~552)
                LD   HL, 512
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (ResPenX), HL
                LD   HL, 424
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (ResPenY), HL
                LD   HL, DateLblTable
                LD   A, (DateMonth)
                CALL DrawLblNum
                CALL DateGap
                LD   HL, DateLblTable + 5
                LD   A, (DateWeek)
                CALL DrawLblNum
                ; строка "Day: D" @ y=440
                LD   HL, 538
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (ResPenX), HL
                LD   HL, 440
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (ResPenY), HL
                LD   HL, DateLblTable + 10
                LD   A, (DateDow)
                CALL DrawLblNum
.panel_end:     LD   HL, #2100
                LD   DE, #0000
                CALL Render_CmdBufWrite32     ; END
                ; размер = BufferPtr - CMD_ADDRESS_PTR
                LD   HL, (FT.Coprocessor.BufferPtr)
                LD   DE, CMD_ADDRESS_PTR
                OR   A
                SBC  HL, DE
                LD   (ResourcePanelDLSize), HL
                ; копировать собранный DL в RAM_G
                LD   B, H
                LD   C, L                      ; BC = size
                POP  HL
                LD   (FT.Coprocessor.BufferPtr), HL   ; восстановить BufferPtr
                LD   HL, CMD_ADDRESS_PTR        ; src Z80
                LD   A, (RESOURCE_PANEL_RAMG >> 16) & #FF
                LD   DE, RESOURCE_PANEL_RAMG & #FFFF
                CALL FT.WriteMem
                RET

; ============================ Fog of war =============================
; explored-битмап карты (бит = MAP0_W*tileY + tileX), 0 = туман. Каждый кадр
; раскрываем квадрат радиуса вокруг героя (накопительно при движении). Рисуем
; СПЛОШНОЙ чёрный туман над неразведанными видимыми тайлами (как в fheroes2:
; под туманом не видно ничего), полосами RECTS по строкам, выровненными по
; скроллу через object VERTEX_TRANSLATE.
FOG_REVEAL_RADIUS EQU 5
FogExplored:    DEFS (MAP0_W * MAP0_W + 7) / 8
FogRowsLeft:    DEFB 0
FogColsLeft:    DEFB 0
FogSX:          DEFB 0
FogSY:          DEFB 0
FogRunStart:    DEFB #FF

; in: D=worldX, E=worldY  out: HL=адрес байта в FogExplored, B=маска бита
Fog_BitPtr:     LD   L, E
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                  ; E*4
                LD   B, H
                LD   C, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                  ; E*32
                ADD  HL, BC                  ; E*36
                LD   C, D
                LD   B, 0
                ADD  HL, BC                  ; + worldX = индекс бита
                LD   A, L
                AND  7
                LD   B, 1
                OR   A
                JR   Z, .have_mask
.mk:            SLA  B
                DEC  A
                JR   NZ, .mk
.have_mask:     SRL  H
                RR   L
                SRL  H
                RR   L
                SRL  H
                RR   L
                LD   DE, FogExplored
                ADD  HL, DE
                RET

; in: D=worldX, E=worldY  out: A != 0 если разведан
Fog_TileExplored:
                CALL Fog_BitPtr
                LD   A, (HL)
                AND  B
                RET

Fog_RevealHero:
                LD   A, (HeroTileY)
                SUB  FOG_REVEAL_RADIUS
                LD   E, A
                LD   A, FOG_REVEAL_RADIUS * 2 + 1
                LD   (FogRowsLeft), A
.row:           LD   A, E
                CP   MAP0_W
                JR   NC, .row_next
                LD   A, (HeroTileX)
                SUB  FOG_REVEAL_RADIUS
                LD   D, A
                LD   A, FOG_REVEAL_RADIUS * 2 + 1
                LD   (FogColsLeft), A
.col:           LD   A, D
                CP   MAP0_W
                JR   NC, .col_next
                PUSH DE
                CALL Fog_BitPtr
                LD   A, (HL)
                AND  B
                JR   NZ, .col_seen       ; бит уже стоял → тайл не новый
                LD   A, (HL)
                OR   B
                LD   (HL), A             ; пометить разведанным
                POP  DE
                PUSH DE
                CALL Minimap_RevealTile  ; впервые разведан → раскрыть на мини-карте
                POP  DE
                JR   .col_next
.col_seen:      POP  DE
.col_next:      INC  D
                LD   A, (FogColsLeft)
                DEC  A
                LD   (FogColsLeft), A
                JR   NZ, .col
.row_next:      INC  E
                LD   A, (FogRowsLeft)
                DEC  A
                LD   (FogRowsLeft), A
                JR   NZ, .row
                RET

; Раскрыть тайл на мини-карте (туман радара, как fheroes2): записать 4x4 блок
; цвета тайла в RAM_G текстуры радара (UI_RADAR_RAMG). Вызывается из Fog_RevealHero
; ТОЛЬКО для впервые разведанных тайлов → после старта 0 записей, при ходьбе край.
; Цвет — MinimapTileColorTable[worldY*36 + worldX]. Запись прямой SPI (FT.WriteMem),
; 0 нагрузки на CMD-FIFO. in: D=worldX, E=worldY. Корраптит A,BC,DE,HL.
Minimap_RevealTile:
                LD   L, E
                LD   H, 0                ; HL = worldY
                ADD  HL, HL
                ADD  HL, HL              ; *4
                LD   B, H
                LD   C, L                ; BC = worldY*4
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL              ; *32
                ADD  HL, BC              ; *36 (= MINIMAP_MAP_W)
                LD   C, D
                LD   B, 0
                ADD  HL, BC              ; + worldX → индекс тайла
                LD   BC, MinimapTileColorTable
                ADD  HL, BC
                LD   A, (HL)             ; A = индекс цвета палитры
                LD   (MinimapPixBuf + 0), A
                LD   (MinimapPixBuf + 1), A
                LD   (MinimapPixBuf + 2), A
                LD   (MinimapPixBuf + 3), A
                ; offset(16) = (UI_RADAR_RAMG & #FFFF) + worldY*576 + worldX*4
                LD   L, E
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL              ; *64
                LD   B, H
                LD   C, L                ; BC = worldY*64
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL              ; *512
                ADD  HL, BC              ; *576 = worldY * (4*144)
                LD   A, D
                ADD  A, A
                ADD  A, A                ; worldX*4 (<=140, 8-bit)
                LD   C, A
                LD   B, 0
                ADD  HL, BC
                LD   BC, UI_RADAR_RAMG & #FFFF
                ADD  HL, BC              ; HL = 16-bit offset в RAM_G
                LD   B, MINIMAP_TILE_PX  ; 4 строки по 4 байта
.mrow:          PUSH BC
                PUSH HL
                EX   DE, HL              ; DE = offset
                LD   A, (UI_RADAR_RAMG >> 16) & #FF
                LD   HL, MinimapPixBuf
                LD   BC, MINIMAP_TILE_PX
                CALL FT.WriteMem
                POP  HL
                LD   BC, UI_RADAR_STRIDE
                ADD  HL, BC              ; следующая строка (+144)
                POP  BC
                DJNZ .mrow
                RET
MinimapPixBuf:  DEFS 4

; Туман примитивами FT812: сглаженный (anti-aliased) чёрный POINT-круг на каждом
; неразведанном видимом тайле. Перекрывающиеся круги дают сплошную внутренность,
; а их AA-края (через SRC_ALPHA) — мягкую облачную границу. Без спрайтов/атласа.
Render_FogCmd:
                CALL Fog_RevealHero
                LD   HL, RuntimeDL_ObjectTranslate
                LD   BC, RuntimeDL_ObjectTranslate_SIZE
                CALL Render_CmdBufCopy
                LD   HL, #0400
                LD   DE, #0000
                CALL Render_CmdBufWrite32     ; COLOR_RGB 0,0,0
                LD   HL, #1000
                LD   DE, #00FF
                CALL Render_CmdBufWrite32     ; COLOR_A 255
                LD   HL, #0B00
                LD   DE, #0014
                CALL Render_CmdBufWrite32     ; BLEND_FUNC SRC_ALPHA, ONE_MINUS (мягкие края)
                LD   HL, #0D00
                LD   DE, #0266
                CALL Render_CmdBufWrite32     ; POINT_SIZE 614 (~24px радиус, круги перекрываются)
                LD   HL, #1F00
                LD   DE, #0002
                CALL Render_CmdBufWrite32     ; BEGIN POINTS
                XOR  A
                LD   (FogSY), A
.row:           XOR  A
                LD   (FogSX), A
.col:           LD   A, (FogSX)
                LD   D, A
                LD   A, (ViewportOriginX)
                ADD  A, D
                LD   D, A
                LD   A, (FogSY)
                LD   E, A
                LD   A, (ViewportOriginY)
                ADD  A, E
                LD   E, A
                CALL Fog_TileExplored
                OR   A
                JR   NZ, .skip
                LD   A, (FogSX)
                CALL Fog_TileCenter
                LD   (RenderPathVertexX), HL
                LD   A, (FogSY)
                CALL Fog_TileCenter
                LD   (RenderPathVertexY), HL
                CALL Render_WriteVertex2FCmd
.skip:          LD   A, (FogSX)
                INC  A
                LD   (FogSX), A
                CP   GAME_VIEW_TILE_W + 1
                JR   C, .col
                LD   A, (FogSY)
                INC  A
                LD   (FogSY), A
                CP   GAME_VIEW_TILE_H + 1
                JR   C, .row
                LD   HL, #2100
                LD   DE, #0000
                CALL Render_CmdBufWrite32     ; END
                RET

; in A=экранный тайл → HL = scale(tile*32 + 16) (центр тайла)
Fog_TileCenter: LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL              ; *32
                LD   DE, 16
                ADD  HL, DE
                JP   Render_ScaleHL_8_5_ToVertex

; Анимация воды palette-cycle (родной DOS-метод HMM2): каждый кадр вращаем 7
; записей палитры WATER_CYCLE_INDEX..+6 и пишем напрямую в RAM_G палитру обоих
; банков composite-фона. Дёшево (14 байт SPI/банк), мерцает вся вода, ноль DL.
Render_WaterCycle:
                LD   A, (WaterCycleCounter)
                INC  A
                LD   (WaterCycleCounter), A
                SRL  A
                SRL  A
                SRL  A                       ; шаг = counter / 8 (скорость)
.mod:           CP   WATER_CYCLE_COUNT
                JR   C, .got
                SUB  WATER_CYCLE_COUNT
                JR   .mod
.got:           LD   C, A                    ; стартовый src-индекс
                LD   B, WATER_CYCLE_COUNT
                LD   IX, WaterCycleBuf
.fill:          LD   A, C
                ADD  A, A
                LD   E, A
                LD   D, 0
                LD   HL, WaterCycleOriginal
                ADD  HL, DE
                LD   A, (HL)
                LD   (IX + 0), A
                INC  HL
                LD   A, (HL)
                LD   (IX + 1), A
                INC  IX
                INC  IX
                INC  C
                LD   A, C
                CP   WATER_CYCLE_COUNT
                JR   C, .nowrap
                LD   C, 0
.nowrap:        DJNZ .fill
                LD   HL, WaterCycleBuf
                LD   A, (WATER_CYCLE_BANK0_RAMG >> 16) & #FF
                LD   D, (WATER_CYCLE_BANK0_RAMG >> 8) & #FF
                LD   E, WATER_CYCLE_BANK0_RAMG & #FF
                LD   BC, WATER_CYCLE_COUNT * 2
                CALL FT.WriteMem
                LD   HL, WaterCycleBuf
                LD   A, (WATER_CYCLE_BANK1_RAMG >> 16) & #FF
                LD   D, (WATER_CYCLE_BANK1_RAMG >> 8) & #FF
                LD   E, WATER_CYCLE_BANK1_RAMG & #FF
                LD   BC, WATER_CYCLE_COUNT * 2
                CALL FT.WriteMem
                RET

WaterCycleCounter: DEFB 0
WaterCycleBuf:     DEFS WATER_CYCLE_COUNT * 2

; Анимация adventure-объектов (костры/мельницы/лава/водяные колёса).
; Для каждого ВИДИМОГО анимир. объекта рисуем текущий кадр-дельту (PALETTED4444)
; ПОВЕРХ запечённой/оверлейной базы — точно как fheroes2 (BlitBase, затем BlitFrame).
; Кадр = MapAnimPhase % N; фаза шагает раз в MAP_ANIM_TICK_FRAMES кадров (~250мс,
; MAPS_DELAY). Позиция — screen-relative через тот же scale+writer, что и Render_FogCmd
; (совпадает с базой суб-пиксельно). Вставлено ПОСЛЕ top-объектов и ДО тумана:
; анимир. объекты непроходимы (герой на них не стоит), туман их скрывает.
MAP_ANIM_TICK_FRAMES EQU 15           ; 250мс при ~59Гц (тюнится)
MAP_ANIM_PHASE_PERIOD EQU 60          ; период счётчика фазы (кратен 3,4,5,6,10,12,15 → без скачка на wrap)
MAP_ANIM_CENTER_LO   EQU 3            ; центральная зона вьюпорта: tile в [LO .. GVTW-LO]
MAP_ANIM_CENTER_SPAN EQU GAME_VIEW_TILE_W - 2 * MAP_ANIM_CENTER_LO

Render_MapAnimCmd:
                if RUNTIME_TILEMAP_RENDER
                ; MAP_ANIM_COUNT определён в generated_map_anim.inc (включается ПОСЛЕ
                ; render.asm) → нельзя ассемблерный if; рантайм-guard для 0-частей.
                LD   A, MAP_ANIM_COUNT
                OR   A
                RET  Z
                LD   A, (MapAnimFrameDiv)
                INC  A
                CP   MAP_ANIM_TICK_FRAMES
                JR   C, .nostep
                LD   HL, MapAnimPhase
                LD   A, (HL)
                INC  A
                CP   MAP_ANIM_PHASE_PERIOD         ; wrap кратно 60 (делится на 3,4,5,6,10,12,15)
                JR   C, .phstore                   ; → mod-N непрерывен на стыке, без скачка фазы
                XOR  A
.phstore:       LD   (HL), A
                XOR  A
.nostep:        LD   (MapAnimFrameDiv), A
                ; --- настройка прохода (один раз) ---
                ; VERTEX_TRANSLATE не выставляем: object-проход (Render_RuntimeObjectsCmd)
                ; копирует RuntimeDL_ObjectTranslate в FIFO КАЖДЫЙ кадр до нас — переиспользуем.
                XOR  A
                LD   (MapAnimEmitted), A            ; счётчик эмитнутых (кап)
                LD   HL, #04FF
                LD   DE, #FFFF
                CALL Render_CmdBufWrite32          ; COLOR_RGB 255,255,255
                LD   HL, #1000
                LD   DE, #00FF
                CALL Render_CmdBufWrite32          ; COLOR_A 255
                LD   HL, #0B00
                LD   DE, #0014
                CALL Render_CmdBufWrite32          ; BLEND_FUNC SRC_ALPHA, ONE_MINUS
                LD   HL, #0500
                LD   DE, #0002
                CALL Render_CmdBufWrite32          ; BITMAP_HANDLE 2
                LD   HL, ((#2A000000 | MAP_ANIM_PALETTE_RAMG) >> 16) & #FFFF
                LD   DE, (#2A000000 | MAP_ANIM_PALETTE_RAMG) & #FFFF
                CALL Render_CmdBufWrite32          ; PALETTE_SOURCE (прозрачная объектная)
                LD   HL, #1500
                LD   DE, #00A0
                CALL Render_CmdBufWrite32          ; BITMAP_TRANSFORM_A 160 (×1.6)
                LD   HL, #1700
                LD   DE, #0000
                CALL Render_CmdBufWrite32          ; BITMAP_TRANSFORM_C 0 (СБРОС: актёр-флип
                                                   ; оставляет C=7936 → иначе кадры за краем source)
                LD   HL, #1900
                LD   DE, #00A0
                CALL Render_CmdBufWrite32          ; BITMAP_TRANSFORM_E 160
                LD   HL, #0600
                LD   DE, #0000
                CALL Render_CmdBufWrite32          ; CELL 0
                LD   HL, #1F00
                LD   DE, #0001
                CALL Render_CmdBufWrite32          ; BEGIN BITMAPS
                ; Приоритет ЦЕНТРАЛЬНЫМ при кап-фризе: проход 1 эмитит объекты в центре
                ; вьюпорта, проход 2 — периферию (что осталось от капа). Кап общий →
                ; периферийные фризятся первыми (как просил пользователь). Множества
                ; «центр»/«край» не пересекаются → без двойной отрисовки.
                LD   A, 1
                LD   (MapAnimPassCentral), A
                CALL .walk
                XOR  A
                LD   (MapAnimPassCentral), A
                CALL .walk
                LD   HL, #2100
                LD   DE, #0000
                CALL Render_CmdBufWrite32          ; END
                RET
.walk:          LD   IX, MapAnimTable
                LD   A, MAP_ANIM_COUNT
                LD   (MapAnimRemaining), A
.entry:         LD   A, (ViewportOriginX)
                LD   B, A
                LD   A, (IX+0)                     ; map_x
                SUB  B
                JP   C, .skip                      ; map_x < originX
                CP   GAME_VIEW_TILE_W + 2
                JP   NC, .skip
                LD   C, A                          ; sx
                LD   A, (ViewportOriginY)
                LD   B, A
                LD   A, (IX+1)                     ; map_y
                SUB  B
                JP   C, .skip
                CP   GAME_VIEW_TILE_H + 2
                JP   NC, .skip
                LD   B, A                          ; sy
                ; central-gate: is_central = sx,sy в [LO..HI]. Эмитим только если
                ; is_central == MapAnimPassCentral (проход 1=центр, проход 2=край).
                LD   A, C
                SUB  MAP_ANIM_CENTER_LO
                JR   C, .edge
                CP   MAP_ANIM_CENTER_SPAN + 1
                JR   NC, .edge
                LD   A, B
                SUB  MAP_ANIM_CENTER_LO
                JR   C, .edge
                CP   MAP_ANIM_CENTER_SPAN + 1
                JR   NC, .edge
                LD   A, 1                          ; центр
                JR   .gate
.edge:          XOR  A                             ; край
.gate:          LD   HL, MapAnimPassCentral
                CP   (HL)
                JP   NZ, .skip                     ; не наш проход → не эмитим (но IX двигаем)
                ; кап: сверх MAP_ANIM_MAX_PER_FRAME объектов в кадре — фриз (база без кадра)
                LD   A, (MapAnimEmitted)
                CP   MAP_ANIM_MAX_PER_FRAME
                JP   NC, .skip
                INC  A
                LD   (MapAnimEmitted), A
                PUSH BC                            ; сохранить sx(C),sy(B)
                ; f = MapAnimPhase mod N
                LD   A, (MapAnimPhase)
                LD   E, (IX+2)                     ; N
.mod:           CP   E
                JR   C, .gotf
                SUB  E
                JR   .mod
.gotf:          ; HL = f*14
                LD   L, A
                LD   H, 0
                ADD  HL, HL                        ; 2f
                LD   D, H
                LD   E, L
                ADD  HL, HL                        ; 4f
                ADD  HL, HL                        ; 8f
                ADD  HL, HL                        ; 16f
                OR   A
                SBC  HL, DE                        ; 14f
                PUSH IX
                POP  DE
                ADD  HL, DE                        ; IX + 14f
                LD   DE, 3
                ADD  HL, DE                        ; frame_ptr = IX+3+14f
                LD   BC, 12
                CALL Render_CmdBufCopy             ; SOURCE+LAYOUT+SIZE → HL=frame_ptr+12
                LD   A, (HL)
                LD   (.frameox), A                 ; ox (signed)
                INC  HL
                LD   A, (HL)
                LD   (.frameoy), A                 ; oy (signed)
                POP  BC                            ; sx(C),sy(B)
                ; world_screen_x = sx*32 + ox
                LD   L, C
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                        ; sx*32
                LD   A, (.frameox)
                CALL .addsigned
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (RenderPathVertexX), HL
                ; world_screen_y = sy*32 + oy
                LD   L, B
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                        ; sy*32
                LD   A, (.frameoy)
                CALL .addsigned
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (RenderPathVertexY), HL
                CALL Render_WriteVertex2FCmd
.skip:          ; advance IX += 3 + N*14
                LD   A, (IX+2)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                OR   A
                SBC  HL, DE                        ; N*14
                LD   DE, 3
                ADD  HL, DE
                PUSH IX
                POP  DE
                ADD  HL, DE
                PUSH HL
                POP  IX
                LD   A, (MapAnimRemaining)
                DEC  A
                LD   (MapAnimRemaining), A
                JP   NZ, .entry
                RET                                ; конец .walk (END/blend — в оркестрации выше)
                endif
                RET                                ; путь при RUNTIME_TILEMAP_RENDER=0
.addsigned:     LD   E, A                          ; HL += sign-extend(A)
                ADD  A, A
                SBC  A, A
                LD   D, A
                ADD  HL, DE
                RET
.frameox:       DEFB 0
.frameoy:       DEFB 0
MapAnimPhase:        DEFB 0
MapAnimFrameDiv:     DEFB 0
MapAnimRemaining:    DEFB 0
MapAnimEmitted:      DEFB 0
MapAnimPassCentral:  DEFB 0

HeroMarker_UpdateDLPosition:
                LD   HL, (HeroPixelX)
                if VIEWPORT_DL_PACK
                if RUNTIME_TILEMAP_RENDER
                else
                LD   A, (ViewportOriginX)
                CALL Render_WorldXToViewportHL
                endif
                endif
                CALL Render_ScaleHL_8_5_ToVertex
                if RUNTIME_TILEMAP_RENDER
                LD   DE, (RuntimeOriginBaseX16)
                OR   A
                SBC  HL, DE
                LD   DE, (RuntimeDL_ObjectTranslateX_Low)
                ADD  HL, DE
                endif
                CALL HeroMarker_ApplyFacingX
                LD   (HERO_MARKER_TRANSLATE_X), HL

                LD   HL, (HeroPixelY)
                if VIEWPORT_DL_PACK
                if RUNTIME_TILEMAP_RENDER
                else
                LD   A, (ViewportOriginY)
                CALL Render_WorldYToViewportHL
                endif
                endif
                LD   DE, 18
                OR   A
                SBC  HL, DE
                CALL Render_ScaleHL_8_5_ToVertex
                if RUNTIME_TILEMAP_RENDER
                LD   DE, (RuntimeOriginBaseY16)
                OR   A
                SBC  HL, DE
                LD   DE, (RuntimeDL_ObjectTranslateY_Low)
                ADD  HL, DE
                endif
                LD   (HERO_MARKER_TRANSLATE_Y), HL
                RET

Actor_UpdateDLPosition:
                ifdef DYNAMIC_ACTOR_RAMG
                LD   HL, (HeroPixelX)
                if VIEWPORT_DL_PACK
                if RUNTIME_TILEMAP_RENDER
                else
                LD   A, (ViewportOriginX)
                CALL Render_WorldXToViewportHL
                endif
                endif
                CALL Render_ScaleHL_8_5_ToVertex
                if RUNTIME_TILEMAP_RENDER
                LD   DE, (RuntimeOriginBaseX16)
                OR   A
                SBC  HL, DE
                LD   DE, (RuntimeDL_ObjectTranslateX_Low)
                ADD  HL, DE
                endif
                LD   (ACTOR_TRANSLATE_X), HL

                LD   HL, (HeroPixelY)
                if VIEWPORT_DL_PACK
                if RUNTIME_TILEMAP_RENDER
                else
                LD   A, (ViewportOriginY)
                CALL Render_WorldYToViewportHL
                endif
                endif
                CALL Render_ScaleHL_8_5_ToVertex
                if RUNTIME_TILEMAP_RENDER
                LD   DE, (RuntimeOriginBaseY16)
                OR   A
                SBC  HL, DE
                LD   DE, (RuntimeDL_ObjectTranslateY_Low)
                ADD  HL, DE
                endif
                LD   (ACTOR_TRANSLATE_Y), HL
                endif
                RET

HeroMarker_ApplyFacingX:
                LD   A, (HeroFacingRight)
                OR   A
                JR   NZ, .face_right
                PUSH HL
                LD   HL, #FF60
                LD   (HERO_MARKER_TRANSFORM_A_LOW), HL
                LD   HL, #1501
                LD   (HERO_MARKER_TRANSFORM_A_HIGH), HL
                LD   HL, HERO_SPRITE_MIRROR_C & #FFFF
                LD   (HERO_MARKER_TRANSFORM_C_LOW), HL
                LD   HL, #1700 | ((HERO_SPRITE_MIRROR_C >> 16) & #00FF)
                LD   (HERO_MARKER_TRANSFORM_C_HIGH), HL
                POP  HL
                RET
.face_right:    PUSH HL
                LD   HL, 160
                LD   (HERO_MARKER_TRANSFORM_A_LOW), HL
                LD   HL, #1500
                LD   (HERO_MARKER_TRANSFORM_A_HIGH), HL
                LD   HL, 0
                LD   (HERO_MARKER_TRANSFORM_C_LOW), HL
                LD   HL, #1700
                LD   (HERO_MARKER_TRANSFORM_C_HIGH), HL
                POP  HL
                RET

Render_WorldXToViewportHL:
                if VIEWPORT_DL_PACK
                PUSH HL
                CALL Tile_MulA32ToHL
                EX   DE, HL
                POP  HL
                OR   A
                SBC  HL, DE
                JR   C, .offscreen
                PUSH HL
                LD   DE, GAME_VIEW_W
                OR   A
                SBC  HL, DE
                POP  HL
                JR   NC, .offscreen
                RET
.offscreen:    LD   HL, 2048
                endif
                RET

Render_WorldYToViewportHL:
                if VIEWPORT_DL_PACK
                PUSH HL
                CALL Tile_MulA32ToHL
                EX   DE, HL
                POP  HL
                OR   A
                SBC  HL, DE
                JR   C, .offscreen
                PUSH HL
                LD   DE, GAME_VIEW_H
                OR   A
                SBC  HL, DE
                POP  HL
                JR   NC, .offscreen
                RET
.offscreen:    LD   HL, 2048
                endif
                RET

Cursor_UpdateDLPosition:
                CALL Render_LoadCursorSprite
                LD   A, (RenderCursorAddrHigh)
                LD   H, #01
                LD   L, A
                LD   (CURSOR_BITMAP_SOURCE_HIGH), HL
                LD   HL, (RenderCursorAddrLow)
                LD   (CURSOR_BITMAP_SOURCE_LOW), HL

                LD   A, (RenderCursorStride)
                ADD  A, A
                LD   D, A
                LD   A, (RenderCursorHeight)
                LD   E, A
                LD   (CURSOR_BITMAP_LAYOUT_LOW), DE
                LD   HL, #0730
                LD   (CURSOR_BITMAP_LAYOUT_HIGH), HL

                LD   A, (RenderCursorSizeW)
                ADD  A, A
                LD   D, A
                LD   A, (RenderCursorSizeH)
                LD   E, A
                LD   (CURSOR_BITMAP_SIZE_LOW), DE
                LD   HL, #0800
                LD   (CURSOR_BITMAP_SIZE_HIGH), HL

                LD   HL, (CursorPixelX)
                LD   DE, (RenderCursorDrawOX)
                CALL Render_AddSignedOffsetClamp0
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (CURSOR_TRANSLATE_X), HL

                LD   HL, (CursorPixelY)
                LD   DE, (RenderCursorDrawOY)
                CALL Render_AddSignedOffsetClamp0
                CALL Render_ScaleHL_8_5_ToVertex
                LD   (CURSOR_TRANSLATE_Y), HL
                RET

Render_LoadCursorSprite:
                LD   A, (CursorSpriteIndex)
                CP   CURSOR_SPRITE_COUNT
                JR   C, .valid
                XOR  A
.valid:         LD   E, A
                LD   D, 0
                LD   H, D
                LD   L, E
                ADD  HL, HL
                ADD  HL, HL
                PUSH HL
                ADD  HL, HL
                POP  DE
                ADD  HL, DE
                LD   DE, CursorSpriteTable
                ADD  HL, DE
                LD   A, (HL)
                LD   (RenderCursorAddrHigh), A
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   (RenderCursorAddrLow), DE
                LD   A, (HL)
                LD   (RenderCursorHeight), A
                INC  HL
                LD   A, (HL)
                LD   (RenderCursorStride), A
                INC  HL
                LD   A, (HL)
                LD   (RenderCursorSizeW), A
                INC  HL
                LD   A, (HL)
                LD   (RenderCursorSizeH), A
                INC  HL
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   (RenderCursorDrawOX), DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (RenderCursorDrawOY), DE
                RET

Render_AddSignedOffsetClamp0:
                ADD  HL, DE
                BIT  7, H
                RET  Z
                LD   HL, 0
                RET

Render_ScaleHL_8_5_ToVertex:
                LD   A, H
                CP   #08
                JR   C, .lookup
                LD   HL, 30000
                RET
.lookup:        ADD  HL, HL
                LD   DE, #C000
                ADD  HL, DE
                PUSH HL
                GetPage3
                LD   (.RestorePage), A
                SetPage3 ScaleTablePage
                POP  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
.RestorePage   EQU $+1
                LD   A, #00
                SetPage3_A
                EX   DE, HL
                RET

                include "generated_dxt_scroll_dl.inc"
                include "generated_adventure_dl.inc"

HERO_MARKER_DL:
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA
                FT_BITMAP_HANDLE 2
                FT_CELL 0
                FT_BITMAP_SOURCE HERO_SPRITE_RAMG
                FT_BITMAP_LAYOUT FT_ARGB4, HERO_SPRITE_W * 2, HERO_SPRITE_H
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, (HERO_SPRITE_W * 8 + 4) / 5, (HERO_SPRITE_H * 8 + 4) / 5
HERO_MARKER_TRANSFORM_A_LOW:
                DEFW 160
HERO_MARKER_TRANSFORM_A_HIGH:
                DEFW #1500
HERO_MARKER_TRANSFORM_C_LOW:
                DEFW 0
HERO_MARKER_TRANSFORM_C_HIGH:
                DEFW #1700
HERO_MARKER_TRANSLATE_X:
                DEFW 0
                DEFW #2B00
HERO_MARKER_TRANSLATE_Y:
                DEFW 0
                DEFW #2C00
                FT_BEGIN FT_BITMAPS
                ; Реальный adventure hero sprite из MINIHERO.ICN.
                FT_VERTEX2F 0, 0
                FT_END
                FT_DISPLAY
HERO_MARKER_DL_SIZE EQU $ - HERO_MARKER_DL

                ifdef DYNAMIC_ACTOR_RAMG
ACTOR_DL:
                FT_COLOR_MASK 1, 1, 1, 1
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA
                FT_BITMAP_HANDLE 2
                FT_CELL 0
                FT_BITMAP_SOURCE DYNAMIC_ACTOR_RAMG
                FT_BITMAP_LAYOUT FT_ARGB4, DYNAMIC_ACTOR_W * 2, DYNAMIC_ACTOR_H
                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, (DYNAMIC_ACTOR_W * 8 + 4) / 5, (DYNAMIC_ACTOR_H * 8 + 4) / 5
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
ACTOR_TRANSLATE_X:
                DEFW 0
                DEFW #2B00
ACTOR_TRANSLATE_Y:
                DEFW 0
                DEFW #2C00
                FT_BEGIN FT_BITMAPS
                FT_VERTEX2F 0, 0
                FT_END
                FT_BLEND_FUNC FT_ONE, FT_ZERO
                FT_DISPLAY
ACTOR_DL_SIZE EQU $ - ACTOR_DL
                endif

CURSOR_DL:
                FT_COLOR_RGB 255, 255, 255
                FT_COLOR_A 255
                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA
                FT_BITMAP_HANDLE 4
                FT_CELL 0
CURSOR_BITMAP_SOURCE_LOW:
                DEFW CURSOR_SPRITE_RAMG & #FFFF
CURSOR_BITMAP_SOURCE_HIGH:
                DEFW #0100 | ((CURSOR_SPRITE_RAMG >> 16) & #00FF)
CURSOR_BITMAP_LAYOUT_LOW:
                DEFW (CURSOR_SPRITE_STRIDE * 2) * 256 + CURSOR_SPRITE_H
CURSOR_BITMAP_LAYOUT_HIGH:
                DEFW #0730
CURSOR_BITMAP_SIZE_LOW:
                DEFW (CURSOR_SPRITE_SIZE_W * 2) * 256 + CURSOR_SPRITE_SIZE_H
CURSOR_BITMAP_SIZE_HIGH:
                DEFW #0800
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_TRANSFORM_C 0
CURSOR_TRANSLATE_X:
                DEFW 0
                DEFW #2B00
CURSOR_TRANSLATE_Y:
                DEFW 0
                DEFW #2C00
                FT_BEGIN FT_BITMAPS
                ; Adventure cursor sprite из ADVMCO/COLOR_CURSOR_ADVENTURE_MAP.
                FT_VERTEX2F 0, 0
                FT_END
                FT_DISPLAY
CURSOR_DL_SIZE EQU $ - CURSOR_DL

RuntimeLastOriginX:
                DEFB #FF
RuntimeLastOriginY:
                DEFB #FF
RenderPathIndex:
                DEFB 0
RenderPathRemaining:
                DEFB 0
RenderPathDimmed:
                DEFB 0
RenderPathVertexX:
                DEFW 0
RenderPathVertexY:
                DEFW 0
RenderPathTileX:
                DEFB 0
RenderPathTileY:
                DEFB 0
RenderPathPrevX:
                DEFB 0
RenderPathPrevY:
                DEFB 0
RenderPathNextX:
                DEFB 0
RenderPathNextY:
                DEFB 0
RenderPathFromDir:
                DEFB 0
RenderPathToDir:
                DEFB 0
RenderRouteSpriteIndex:
                DEFB 0
RenderRouteTurnOffset:
                DEFB 0
RenderRouteAddrHigh:
                DEFB 0
RenderRouteAddrLow:
                DEFW 0
RenderRouteHeight:
                DEFB 0
RenderRouteStride:
                DEFB 0
RenderRouteSizeW:
                DEFB 0
RenderRouteSizeH:
                DEFB 0
RenderRouteDrawOX:
                DEFW 0
RenderRouteDrawOY:
                DEFW 0
RenderCursorAddrHigh:
                DEFB 0
RenderCursorAddrLow:
                DEFW 0
RenderCursorHeight:
                DEFB 0
RenderCursorStride:
                DEFB 0
RenderCursorSizeW:
                DEFB 0
RenderCursorSizeH:
                DEFB 0
RenderCursorDrawOX:
                DEFW 0
RenderCursorDrawOY:
                DEFW 0

; Маршрут целиком: PALETTE_SOURCE (норма) в начале + одна PALETTE_SOURCE (красная) на
; границе хода (недостижимое — красным, как fheroes2 ROUTERED).
HERO_PATH_CMD_MAX EQU 64 + HERO_PATH_MAX * 16
; minimap overlay: рамка вьюпорта (40 байт) + точка героя RECTS (20 байт)
MINIMAP_RECT_CMD_BYTES EQU 60
; ресурсная панель: RAM_G-композит (иконки+числа) → в кадре только CMD_APPEND
RESOURCE_PANEL_CMD_BYTES EQU 12
; fog: object-translate + хедер(24) + 1 POINT(4 байта) на каждый видимый тайл (+margin)
FOG_CMD_BYTES EQU RuntimeDL_ObjectTranslate_SIZE + 24 + (GAME_VIEW_TILE_W + 1) * (GAME_VIEW_TILE_H + 1) * 4
; Anim-проход: CMD-FIFO (4096) тугой, поэтому кап на число анимир. объектов в кадре.
; Сверх капа — фризятся (рисуется база без кадра-дельты). Вода НЕ затронута (palette-
; cycle, 0 DL). setup=40 (10 команд×4; БЕЗ translate — он уже выставлен object-проходом
; каждый кадр; БЕЗ blend-restore — fog ставит свой blend сразу после). На объект 16.
MAP_ANIM_MAX_PER_FRAME EQU 10         ; целиком вмещает мельницу (10 частей)
MAP_ANIM_CMD_BYTES EQU 44 + MAP_ANIM_MAX_PER_FRAME * 16
                if BG_DXT_RAW_SIZE
RUNTIME_CMD_FRAME_MAX EQU 4 + BackgroundDxt_DL_SIZE + RuntimeDL_ObjectTranslate_SIZE + 12 + RuntimeDL_ObjectTranslate_SIZE + 12 + HERO_PATH_CMD_MAX + (HERO_MARKER_DL_SIZE - 4) + MAP_ANIM_CMD_BYTES + FOG_CMD_BYTES + AdventureUI_DL_SIZE + 152 + UI_RightPanel_DL_SIZE + MINIMAP_RECT_CMD_BYTES + RESOURCE_PANEL_CMD_BYTES + CURSOR_DL_SIZE
                else
RUNTIME_CMD_FRAME_MAX EQU 4 + RuntimeDL_Header_SIZE + 12 + RuntimeDL_RightBand_SIZE + 12 + (RuntimeDL_Tail_SIZE - 4) + RuntimeDL_ObjectTranslate_SIZE + 12 + RuntimeDL_ObjectTranslate_SIZE + 12 + HERO_PATH_CMD_MAX + (HERO_MARKER_DL_SIZE - 4) + MAP_ANIM_CMD_BYTES + FOG_CMD_BYTES + AdventureUI_DL_SIZE + 152 + UI_RightPanel_DL_SIZE + MINIMAP_RECT_CMD_BYTES + RESOURCE_PANEL_CMD_BYTES + CURSOR_DL_SIZE
                endif
                ifdef DYNAMIC_ACTOR_RAMG
RUNTIME_CMD_FRAME_MAX_WITH_ACTOR EQU RUNTIME_CMD_FRAME_MAX + (ACTOR_DL_SIZE - 4)
                ASSERT RUNTIME_CMD_FRAME_MAX_WITH_ACTOR <= 4096
                ASSERT ((CMD_ADDRESS_PTR & #C000) == ((CMD_ADDRESS_PTR + RUNTIME_CMD_FRAME_MAX_WITH_ACTOR - 1) & #C000))
                else
                ASSERT RUNTIME_CMD_FRAME_MAX <= 4096
                ASSERT ((CMD_ADDRESS_PTR & #C000) == ((CMD_ADDRESS_PTR + RUNTIME_CMD_FRAME_MAX - 1) & #C000))
                endif
                ASSERT RUNTIME_DL_BUFFER + RUNTIME_BASE_DL_SIZE <= StackTop

                endif
