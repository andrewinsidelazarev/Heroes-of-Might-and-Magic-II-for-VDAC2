                ifndef _HMM2_GAME_STATE_
                define _HMM2_GAME_STATE_

GAME_MODE_ADVENTURE EQU 0
GAME_MODE_TOWN      EQU 1
GAME_MODE_COMBAT    EQU 2
GAME_MODE_MENU      EQU 3

CURSOR_STEP_PIXELS  EQU 5
; Логический viewport игры: 640×480, поверх физического FT812 1024×768.
; Не пересчитывать эти границы под физический режим.
CURSOR_MAX_X        EQU 624
CURSOR_MAX_Y        EQU 464
; Старт как в ОРИГИНАЛЕ: герой рекрутируется в ПЕРВОМ замке (startWithHeroInFirstCastle),
; ставится на гейт замка (GetCenter). Первый замок игрока — OBJNTOWN-гейт (24,13).
; Гейт сделан проходимым (CASTLE_ENTRANCE_OBJECTS) → герой выходит вниз.
HERO_START_TILE_X   EQU 24
HERO_START_TILE_Y   EQU 13
HERO_STEP_PIXELS    EQU 2
HERO_MOVE_FRAME_MASK EQU 0
HERO_PATH_MAX       EQU 88            ; буфер пути (< 96: буферы #4300/#4360 врозь на 96); под бюджет рендера полного маршрута + полоски MP
PATH_DEBUG_MAX      EQU MAP0_TILES
PATH_NODES_PER_FRAME EQU 8
PATH_STATE_IDLE     EQU 0
PATH_STATE_SEARCH   EQU 1
HERO_MOVE_TILES_MAX EQU 16            ; дневной запас хода героя в тайлах (End Turn пополняет)
PATH_PARENT_BUF     EQU #C000
PATH_COST_LO_BUF    EQU PATH_PARENT_BUF + MAP0_TILES
PATH_COST_HI_BUF    EQU PATH_COST_LO_BUF + MAP0_TILES
PATH_QUEUE_X_BUF    EQU PATH_COST_HI_BUF + MAP0_TILES
PATH_QUEUE_CAPACITY EQU #1000
PATH_QUEUE_Y_BUF    EQU PATH_QUEUE_X_BUF + PATH_QUEUE_CAPACITY
PATH_DEBUG_X_BUF    EQU PATH_QUEUE_Y_BUF + PATH_QUEUE_CAPACITY
PATH_DEBUG_Y_BUF    EQU PATH_DEBUG_X_BUF + MAP0_TILES
PATH_WORK_END       EQU PATH_DEBUG_Y_BUF + MAP0_TILES
                ASSERT PATH_WORK_END <= #10000
PATH_FLAG_WATER     EQU #01
PATH_FLAG_STOP      EQU #02
PATH_FLAG_ROAD      EQU #04
MAP_MAX_TILE_X      EQU MAP0_W - 1
MAP_MAX_TILE_Y      EQU MAP0_H - 1

; Общая инициализация игры. Стартуем в ГЛАВНОМ МЕНЮ (диспетчер сцен), а не
; сразу в adventure: загрузка карты (Background/Objects_Upload) ленивая —
; в Adventure_Enter по кнопке New Game.
Game_Init:
                XOR  A
                LD   (FrameCounter), A
                LD   (FrameCounter + 1), A
                LD   (MenuClickLatch), A
                LD   (MenuLmbDown), A             ; pressed-состояние кнопок меню
                LD   (MenuLanternIdx), A          ; кадр анимации фонаря
                LD   A, #FF
                LD   (MenuHoverIndex), A          ; нет наведённой кнопки
                CALL Cursor_GlobalUpload          ; глобальный курсор в постоянную RAM_G (раз)
                CALL Menu_Enter
                RET

; Вход в adventure-сцену: загрузка карты в RAM_G + инициализация состояния.
; Вызывается из Menu_Update по клику New Game (ленивая загрузка карты).
Adventure_Enter:
                CALL Render_BlackFrame            ; межсценный чёрный кадр ДО перезаписи RAM_G
                CALL Background_Upload            ; (иначе старый меню-DL покажет мусор поверх
                CALL Objects_Upload              ;  частично загруженных adventure-битмапов)
                LD   A, GAME_MODE_ADVENTURE
                LD   (GameMode), A
                ; стартовый вьюпорт на замок (origin 16,5 → видно замок 22-26,11-13
                ; и героя у входа 24,14)
                LD   A, 16
                LD   (ViewportOriginX), A
                LD   HL, 16 * 32
                LD   (ViewportPixelX), HL
                LD   A, 5
                LD   (ViewportOriginY), A
                LD   HL, 5 * 32
                LD   (ViewportPixelY), HL
                LD   HL, 320
                LD   (CursorPixelX), HL
                LD   HL, 224
                LD   (CursorPixelY), HL
                CALL Cursor_UpdateTileFromPixel
                CALL Hero_InitPosition
                LD   A, HERO_MOVE_TILES_MAX     ; полный дневной запас хода
                LD   (HeroMovePoints), A
                LD   HL, 1                       ; день 1
                LD   (GameDay), HL
                CALL Resources_InitStart
                CALL Resources_BuildPanelDL      ; собрать DL панели в RAM_G
                XOR  A
                LD   (CursorMoveCooldown), A
                LD   (CursorSpriteIndex), A
                CALL Cursor_StoreMousePos
                ; Клик по New Game ещё «зажат»: погасить его для adventure, чтобы
                ; не превратился в команду движения героя до следующего нажатия.
                LD   A, 1
                LD   (HeroFireLatch), A
                RET

Game_Update:
                LD   HL, (FrameCounter)          ; общий счётчик кадров (анимация)
                INC  HL
                LD   (FrameCounter), HL
                LD   A, (GameMode)
                CP   GAME_MODE_MENU
                JP   Z, Menu_Update
                CALL Cursor_Update
                CALL Viewport_UpdateScroll
                CALL Hero_Update
                CALL Cursor_UpdateTheme
                RET

Hero_InitPosition:
                LD   A, HERO_START_TILE_X
                LD   (HeroTileX), A
                LD   (HeroTargetX), A
                CALL Tile_MulA32ToHL
                LD   (HeroPixelX), HL
                LD   A, HERO_START_TILE_Y
                LD   (HeroTileY), A
                LD   (HeroTargetY), A
                CALL Tile_MulA32ToHL
                LD   (HeroPixelY), HL
                XOR  A
                LD   (HeroMoveCooldown), A
                LD   (HeroFireLatch), A
                LD   (HeroMoveFrameGate), A
                LD   A, (HeroTileX)
                LD   (HeroStepX), A
                LD   A, (HeroTileY)
                LD   (HeroStepY), A
                XOR  A
                LD   (HeroFacingRight), A
                LD   (HeroPathLen), A
                LD   (HeroPathIndex), A
                LD   (PathState), A
                LD   (PathDebugLen), A
                LD   (PathDebugLen + 1), A
                RET

Hero_Update:
                CALL Hero_CommandFromFire
                CALL Hero_PathSearchUpdate
                CALL Hero_MoveTowardTarget
                RET

Hero_CommandFromFire:
                CALL Input_MouseLMB
                JR   NZ, .pressed_mouse
                CALL Input_FireKey
                JR   Z, .released
                LD   A, (HeroFireLatch)
                OR   A
                RET  NZ
                LD   A, 1
                LD   (HeroFireLatch), A
                CALL Cursor_CheckGameArea
                RET  Z
                LD   A, (CursorTileX)
                LD   B, A
                LD   A, (CursorTileY)
                LD   C, A
                CALL Hero_SetTargetIfPassable
                RET
.pressed_mouse: LD   A, (HeroFireLatch)
                OR   A
                RET  NZ
                LD   A, 1
                LD   (HeroFireLatch), A
                CALL UI_DispatchClick
                RET
.released:      XOR  A
                LD   (HeroFireLatch), A
                RET

; Диспетчер клика LMB по зонам экрана:
;   x < UI_RADAR_X (480)         → игровая зона → команда герою (как было)
;   мини-карта [480..624)×[16..160)  → навигация (центрировать вьюпорт)
;   кнопки     [480..624)×[320..392) → действие кнопки (UI_ButtonClick)
;   иначе (правая панель, статус)    → игнор
UI_DispatchClick:
                CALL Input_MouseX
                LD   (UIClickX), HL
                CALL Input_MouseY
                LD   (UIClickY), HL
                ; x < UI_RADAR_X → игровая зона
                LD   HL, (UIClickX)
                LD   DE, UI_RADAR_X
                OR   A
                SBC  HL, DE                  ; x - 480
                JP   C, Hero_CommandTargetFromMouse
                ; x в [480..624)?
                PUSH HL
                LD   DE, UI_RADAR_W
                OR   A
                SBC  HL, DE
                POP  HL
                RET  NC                       ; x >= 624 → за панелью, игнор
                ; правая панель. классифицируем по Y.
                LD   HL, (UIClickY)
                LD   DE, UI_RADAR_Y           ; 16
                OR   A
                SBC  HL, DE                   ; y - 16
                JR   C, .try_buttons          ; y < 16
                PUSH HL
                LD   DE, UI_RADAR_H           ; 144
                OR   A
                SBC  HL, DE
                POP  HL
                JR   NC, .try_buttons         ; y >= 160
                JP   UI_MinimapNav            ; мини-карта
.try_buttons:   LD   HL, (UIClickY)
                LD   DE, UI_BUTTON_Y          ; 320
                OR   A
                SBC  HL, DE                   ; y - 320
                RET  C                        ; y < 320 → игнор (между картой и кнопками)
                PUSH HL
                LD   DE, UI_BUTTON_GRID_H     ; 72 (2 ряда × 36)
                OR   A
                SBC  HL, DE
                POP  HL
                RET  NC                       ; y >= 392 → игнор
                JP   UI_ButtonClick

; Клик по мини-карте → центрировать вьюпорт на тайле (tx,ty) = (click-radar)/4.
UI_MinimapNav:
                LD   HL, (UIClickX)
                LD   DE, UI_RADAR_X
                OR   A
                SBC  HL, DE                   ; 0..143
                SRL  H
                RR   L
                SRL  H
                RR   L                        ; /MINIMAP_TILE_PX(4) → tx (0..35)
                LD   A, L
                LD   B, MAP0_W - GAME_VIEW_TILE_W   ; max originX = 22
                CALL UI_CenterOrigin
                LD   (ViewportOriginX), A
                CALL UI_TileToPixelHL
                LD   (ViewportPixelX), HL
                LD   HL, (UIClickY)
                LD   DE, UI_RADAR_Y
                OR   A
                SBC  HL, DE
                SRL  H
                RR   L
                SRL  H
                RR   L                        ; ty (0..35)
                LD   A, L
                LD   B, MAP0_H - GAME_VIEW_TILE_H
                CALL UI_CenterOrigin
                LD   (ViewportOriginY), A
                CALL UI_TileToPixelHL
                LD   (ViewportPixelY), HL
                RET

; in: A=целевой тайл (центр), B=max origin → out: A=origin (A-полвьюпорта, клампнут [0..B])
UI_CenterOrigin:
                SUB  GAME_VIEW_TILE_W / 2     ; A - 7 (полширины вьюпорта)
                JR   NC, .clamp_hi
                XOR  A                         ; <0 → 0
.clamp_hi:      CP   B
                RET  C
                RET  Z
                LD   A, B                      ; > max → max
                RET
; in: A=tile → out: HL = tile*32
UI_TileToPixelHL:
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                RET

; Клик по кнопке: индекс = row*4 + col (сетка 4×2). fheroes2 ADVBTNS:
;   0 NextHero 1 HeroMovement 2 Kingdom 3 Spell / 4 EndTurn 5 Adventure 6 File 7 System.
; Реализован End Turn (4); остальные требуют подсистем (стоп).
UI_ButtonClick:
                LD   HL, (UIClickX)
                LD   DE, UI_BUTTON_X
                OR   A
                SBC  HL, DE
                LD   A, L
                LD   B, UI_BUTTON_W
                CALL UI_DivAB                  ; A = col (0..3)
                PUSH AF
                LD   HL, (UIClickY)
                LD   DE, UI_BUTTON_Y
                OR   A
                SBC  HL, DE
                LD   A, L
                LD   B, UI_BUTTON_H
                CALL UI_DivAB                  ; A = row (0..1)
                ADD  A, A
                ADD  A, A                       ; row*4
                LD   B, A
                POP  AF                          ; col
                ADD  A, B                        ; индекс кнопки
                CP   4                           ; End Turn?
                JP   Z, Game_EndTurn
                RET                              ; прочие кнопки — нет подсистемы

; A = A / B (B>0, малые значения), беззнаково.
UI_DivAB:       LD   C, 0
.loop:          CP   B
                JR   C, .done
                SUB  B
                INC  C
                JR   .loop
.done:          LD   A, C
                RET

; End Turn: новый день + пополнить дневной запас хода героя + дневной доход.
Game_EndTurn:
                LD   HL, (GameDay)
                INC  HL
                LD   (GameDay), HL
                LD   A, HERO_MOVE_TILES_MAX
                LD   (HeroMovePoints), A
                ; дневной доход (упрощённо: базовый доход одного замка ~1000 золота/день)
                LD   HL, (ResGold)
                LD   DE, 1000
                ADD  HL, DE
                LD   (ResGold), HL
                LD   A, (ResGold + 2)
                ADC  A, 0
                LD   (ResGold + 2), A
                CALL Resources_BuildPanelDL      ; пересобрать DL панели (золото изменилось)
                RET

; Стартовые ресурсы королевства (fheroes2 _getKingdomStartingResources, человек/NORMAL):
; gold 7500, wood/ore по 20, mercury/sulfur/crystal/gems по 5.
Resources_InitStart:
                LD   HL, 7500
                LD   (ResGold), HL
                XOR  A
                LD   (ResGold + 2), A
                LD   HL, 20
                LD   (ResWood), HL
                LD   (ResOre), HL
                LD   HL, 5
                LD   (ResMercury), HL
                LD   (ResSulfur), HL
                LD   (ResCrystal), HL
                LD   (ResGems), HL
                RET

Hero_CommandTargetFromMouse:
                CALL Input_MouseX
                LD   DE, GAME_VIEW_X
                OR   A
                SBC  HL, DE
                RET  C
                PUSH HL
                LD   DE, GAME_VIEW_W
                OR   A
                SBC  HL, DE
                POP  HL
                RET  NC
                if VIEWPORT_DL_PACK
                LD   DE, (ViewportPixelX)
                ADD  HL, DE
                CALL Cursor_WordDiv32ClampMapX
                else
                CALL Cursor_WordDiv32ClampX
                endif
                LD   B, A
                CALL Input_MouseY
                LD   DE, GAME_VIEW_Y
                OR   A
                SBC  HL, DE
                RET  C
                PUSH HL
                LD   DE, GAME_VIEW_H
                OR   A
                SBC  HL, DE
                POP  HL
                RET  NC
                if VIEWPORT_DL_PACK
                LD   DE, (ViewportPixelY)
                ADD  HL, DE
                CALL Cursor_WordDiv32ClampMapY
                else
                CALL Cursor_WordDiv32ClampY
                endif
                LD   C, A
                CALL Hero_SetTargetIfPassable
                RET

Hero_MoveTowardTarget:
                LD   A, (PathState)
                CP   PATH_STATE_SEARCH
                RET  Z
                LD   A, (HeroMoveFrameGate)
                INC  A
                AND  HERO_MOVE_FRAME_MASK
                LD   (HeroMoveFrameGate), A
                RET  NZ

                CALL Hero_SelectStepIfArrived

                LD   A, (HeroStepX)
                CALL Tile_MulA32ToHL
                EX   DE, HL
                LD   HL, (HeroPixelX)
                CALL Hero_StepWordTowardDE
                LD   (HeroPixelX), HL

                LD   A, (HeroStepY)
                CALL Tile_MulA32ToHL
                EX   DE, HL
                LD   HL, (HeroPixelY)
                CALL Hero_StepWordTowardDE
                LD   (HeroPixelY), HL

                CALL Hero_UpdateTileFromPixel
                RET

Hero_SetTargetIfPassable:
                CALL Hero_BuildPath
                RET

Hero_SelectStepIfArrived:
                LD   A, (HeroStepX)
                CALL Tile_MulA32ToHL
                EX   DE, HL
                LD   HL, (HeroPixelX)
                OR   A
                SBC  HL, DE
                RET  NZ
                LD   A, (HeroStepY)
                CALL Tile_MulA32ToHL
                EX   DE, HL
                LD   HL, (HeroPixelY)
                OR   A
                SBC  HL, DE
                RET  NZ

                CALL Hero_UpdateTileFromPixel
                CALL Hero_CheckPickup          ; подбор ресурсов на тайле (taken защищает)
                LD   A, (HeroTileX)
                LD   B, A
                LD   A, (HeroTileY)
                LD   C, A
                LD   A, (HeroTargetX)
                CP   B
                JR   NZ, .need_step
                LD   A, (HeroTargetY)
                CP   C
                JR   NZ, .need_step
                XOR  A
                LD   (HeroPathLen), A
                LD   (HeroPathIndex), A
                RET

.need_step:     LD   A, (HeroMovePoints)
                OR   A
                JR   Z, .stop                  ; запас хода исчерпан → стоп
                CALL Hero_AdvancePath
                JR   Z, .stop                  ; путь кончился/застрял → стоп
                LD   A, (HeroMovePoints)        ; продвинулись на тайл → −1 MP
                DEC  A
                LD   (HeroMovePoints), A
                RET
.stop:          LD   A, (HeroTileX)            ; зафиксировать героя на текущем тайле
                LD   (HeroTargetX), A
                LD   (HeroStepX), A
                LD   A, (HeroTileY)
                LD   (HeroTargetY), A
                LD   (HeroStepY), A
                XOR  A
                LD   (HeroPathLen), A
                LD   (HeroPathIndex), A
                RET

; Подбор ресурсов: линейный поиск тайла героя в PickupList (из generated_runtime_map).
; При первом наступании — начислить ресурс по resource_idx, пометить taken, перестроить
; панель. taken-битмап защищает от повторного начисления.
PickupTaken:    DEFS (PICKUP_COUNT + 7) / 8

Hero_CheckPickup:
                LD   A, PICKUP_COUNT
                OR   A
                RET  Z
                LD   IX, PickupList
                LD   B, PICKUP_COUNT
                LD   C, 0
.loop:          LD   A, (HeroTileX)
                CP   (IX + 0)
                JR   NZ, .next
                LD   A, (HeroTileY)
                CP   (IX + 1)
                JR   NZ, .next
                PUSH BC
                CALL Pickup_BitPtr             ; HL = байт taken, A = маска
                LD   D, A
                AND  (HL)
                JR   NZ, .seen                 ; уже подобрано
                LD   A, (HL)
                OR   D
                LD   (HL), A                   ; пометить taken
                LD   A, (IX + 2)               ; resource_idx
                CALL Pickup_AddResource
                CALL Resources_BuildPanelDL
.seen:          POP  BC
                RET
.next:          INC  C
                LD   DE, 3
                ADD  IX, DE
                DJNZ .loop
                RET

; in: C = индекс подбора → HL = байт в PickupTaken, A = маска бита.
Pickup_BitPtr:  LD   A, C
                SRL  A
                SRL  A
                SRL  A
                LD   E, A
                LD   D, 0
                LD   HL, PickupTaken
                ADD  HL, DE
                LD   A, C
                AND  7
                INC  A
                LD   B, A
                LD   A, 1
                RRCA
.sh:            RLCA
                DJNZ .sh
                RET

; in: A = resource_idx → Res[idx] += PickupAmounts[idx] (16-бит).
Pickup_AddResource:
                PUSH AF
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                LD   DE, ResourceValueAddrs
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                   ; DE = адрес ResXxx
                POP  AF
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                LD   BC, PickupAmounts
                ADD  HL, BC
                LD   C, (HL)
                INC  HL
                LD   B, (HL)                   ; BC = количество
                LD   A, (DE)
                LD   L, A
                INC  DE
                LD   A, (DE)
                LD   H, A                      ; HL = текущее значение
                ADD  HL, BC
                LD   A, H
                LD   (DE), A
                DEC  DE
                LD   A, L
                LD   (DE), A
                RET

Hero_PathSearchUpdate:
                LD   A, (PathState)
                CP   PATH_STATE_SEARCH
                RET  NZ
                GetPage3
                LD   (PathWorkRestorePage), A
                SetPage3 PathWorkPage
                LD   A, PATH_NODES_PER_FRAME
                LD   (PathStepBudget), A

.loop:          CALL Path_QueueEmpty
                JP   Z, .finish
                CALL Path_DequeueBC
                LD   A, B
                LD   (PathCurrentX), A
                LD   A, C
                LD   (PathCurrentY), A
                CALL Path_LoadCurrentCost
                CALL Path_CurrentCanExpand
                JP   Z, .next_node

.top_left:      LD   A, (PathCurrentX)
                OR   A
                JR   Z, .top
                LD   A, (PathCurrentY)
                OR   A
                JR   Z, .top
                LD   A, (PathCurrentX)
                DEC  A
                LD   B, A
                LD   A, (PathCurrentY)
                DEC  A
                LD   C, A
                LD   D, 0
                CALL Path_TryNeighbor
.top:           LD   A, (PathCurrentY)
                OR   A
                JR   Z, .top_right
                LD   A, (PathCurrentX)
                LD   B, A
                LD   A, (PathCurrentY)
                DEC  A
                LD   C, A
                LD   D, 1
                CALL Path_TryNeighbor
.top_right:     LD   A, (PathCurrentX)
                CP   MAP_MAX_TILE_X
                JR   NC, .right
                LD   A, (PathCurrentY)
                OR   A
                JR   Z, .right
                LD   A, (PathCurrentX)
                INC  A
                LD   B, A
                LD   A, (PathCurrentY)
                DEC  A
                LD   C, A
                LD   D, 2
                CALL Path_TryNeighbor
.right:         LD   A, (PathCurrentX)
                CP   MAP_MAX_TILE_X
                JR   NC, .bottom_right
                INC  A
                LD   B, A
                LD   A, (PathCurrentY)
                LD   C, A
                LD   D, 3
                CALL Path_TryNeighbor
.bottom_right:  LD   A, (PathCurrentX)
                CP   MAP_MAX_TILE_X
                JR   NC, .bottom
                LD   A, (PathCurrentY)
                CP   MAP_MAX_TILE_Y
                JR   NC, .bottom
                LD   A, (PathCurrentX)
                INC  A
                LD   B, A
                LD   A, (PathCurrentY)
                INC  A
                LD   C, A
                LD   D, 4
                CALL Path_TryNeighbor
.bottom:        LD   A, (PathCurrentY)
                CP   MAP_MAX_TILE_Y
                JR   NC, .bottom_left
                INC  A
                LD   C, A
                LD   A, (PathCurrentX)
                LD   B, A
                LD   D, 5
                CALL Path_TryNeighbor
.bottom_left:   LD   A, (PathCurrentX)
                OR   A
                JR   Z, .left
                LD   A, (PathCurrentY)
                CP   MAP_MAX_TILE_Y
                JR   NC, .left
                LD   A, (PathCurrentX)
                DEC  A
                LD   B, A
                LD   A, (PathCurrentY)
                INC  A
                LD   C, A
                LD   D, 6
                CALL Path_TryNeighbor
.left:          LD   A, (PathCurrentX)
                OR   A
                JR   Z, .next_node
                LD   A, (PathCurrentX)
                DEC  A
                LD   B, A
                LD   A, (PathCurrentY)
                LD   C, A
                LD   D, 7
                CALL Path_TryNeighbor

.next_node:     LD   A, (PathStepBudget)
                DEC  A
                LD   (PathStepBudget), A
                JP   NZ, .loop
                LD   A, 1
                JP   Path_RestoreWorkPage

.finish:        LD   A, (PathTargetX)
                LD   B, A
                LD   A, (PathTargetY)
                LD   C, A
                CALL Path_ParentAddr
                LD   A, (HL)
                CP   #FF
                JR   Z, .not_found
                LD   A, (PathTargetX)
                LD   B, A
                LD   A, (PathTargetY)
                LD   C, A
                CALL Path_Reconstruct
                LD   A, (PathFound)
                OR   A
                JR   Z, .clear_search
                LD   A, (PathTargetX)
                LD   (HeroTargetX), A
                LD   A, (PathTargetY)
                LD   (HeroTargetY), A
                JR   .clear_search
.not_found:     XOR  A
                LD   (HeroPathLen), A
                LD   (HeroPathIndex), A
                LD   (PathFound), A
.clear_search:  XOR  A
                LD   (PathState), A
                LD   A, 1
                JP   Path_RestoreWorkPage

Hero_AdvancePath:
                LD   A, (HeroPathLen)
                OR   A
                RET  Z
                LD   A, (HeroPathIndex)
                LD   E, A
                LD   D, 0
                LD   HL, HeroPathXBuf
                ADD  HL, DE
                LD   B, (HL)
                LD   HL, HeroPathYBuf
                ADD  HL, DE
                LD   C, (HL)
                CALL Hero_SetStepBC
                LD   A, (HeroPathIndex)
                OR   A
                JR   Z, .last
                DEC  A
                LD   (HeroPathIndex), A
                OR   1
                RET
.last:          XOR  A
                LD   (HeroPathIndex), A
                OR   1
                RET

Hero_CandidateTowardTarget:
                CALL Hero_CandidateXTowardTarget
                LD   D, B
                LD   A, (HeroTileY)
                LD   C, A
                LD   A, (HeroTargetY)
                CP   C
                JR   Z, .store_x
                JR   C, .dec_y
                INC  C
                JR   .store_x
.dec_y:         DEC  C
.store_x:       LD   B, D
                RET

Hero_CandidateXTowardTarget:
                LD   A, (HeroTileX)
                LD   B, A
                LD   A, (HeroTileY)
                LD   C, A
                LD   A, (HeroTargetX)
                CP   B
                RET  Z
                JR   C, .dec_x
                INC  B
                RET
.dec_x:         DEC  B
                RET

Hero_CandidateYTowardTarget:
                LD   A, (HeroTileX)
                LD   B, A
                LD   A, (HeroTileY)
                LD   C, A
                LD   A, (HeroTargetY)
                CP   C
                RET  Z
                JR   C, .dec_y
                INC  C
                RET
.dec_y:         DEC  C
                RET

Hero_CandidateDetourDown:
                LD   A, (HeroTileX)
                LD   B, A
                LD   A, (HeroTileY)
                LD   C, A
                INC  C
                RET

Hero_CandidateDetourUp:
                LD   A, (HeroTileX)
                LD   B, A
                LD   A, (HeroTileY)
                LD   C, A
                DEC  C
                RET

Hero_CandidateXDetourDown:
                CALL Hero_CandidateXTowardTarget
                INC  C
                RET

Hero_CandidateXDetourUp:
                CALL Hero_CandidateXTowardTarget
                DEC  C
                RET

Hero_SetStepBC:
                LD   A, B
                LD   (HeroStepX), A
                LD   A, C
                LD   (HeroStepY), A
                LD   A, (HeroTileX)
                CP   B
                JR   Z, .moved
                JR   C, .face_right
                XOR  A
                LD   (HeroFacingRight), A
                JR   .moved
.face_right:    LD   A, 1
                LD   (HeroFacingRight), A
.moved:         OR   1
                RET

Hero_TryStepCandidate:
                LD   A, B
                CP   MAP_MAX_TILE_X + 1
                RET  NC
                LD   A, C
                CP   MAP_MAX_TILE_Y + 1
                RET  NC
                PUSH BC
                CALL Map_IsTilePassable
                POP  BC
                RET  Z
                JP   Hero_SetStepBC

Hero_BuildPath:
                PUSH BC
                CALL Map_IsTilePassable
                POP  BC
                JR   NZ, .valid_target
                XOR  A
                LD   (PathState), A
                LD   (PathDebugLen), A
                LD   (PathDebugLen + 1), A
                LD   (HeroPathLen), A
                LD   (HeroPathIndex), A
                LD   (PathFound), A
                RET
.valid_target:
                LD   A, B
                LD   (PathTargetX), A
                LD   A, C
                LD   (PathTargetY), A

                GetPage3
                LD   (PathWorkRestorePage), A
                SetPage3 PathWorkPage

                XOR  A
                LD   (HeroPathLen), A
                LD   (HeroPathIndex), A
                LD   (PathFound), A
                LD   (PathDebugLen), A
                LD   (PathDebugLen + 1), A

                LD   HL, PATH_PARENT_BUF
                LD   BC, MAP0_TILES
                LD   A, #FF
.clear_parent:  LD   (HL), A
                INC  HL
                DEC  BC
                LD   A, B
                OR   C
                LD   A, #FF
                JR   NZ, .clear_parent

                LD   HL, 0
                LD   (PathQueueHead), HL
                LD   (PathQueueTail), HL

                LD   A, (HeroTileX)
                LD   B, A
                LD   A, (HeroTileY)
                LD   C, A
                CALL Path_ParentAddr
                LD   (HL), #FE
                CALL Path_CostLoAddr
                LD   (HL), 0
                CALL Path_CostHiAddr
                LD   (HL), 0
                CALL Path_EnqueueBC
                LD   A, PATH_STATE_SEARCH
                LD   (PathState), A
                LD   A, 1
                JP   Path_RestoreWorkPage

Path_RestoreWorkPage:
                PUSH AF
                LD   A, (PathWorkRestorePage)
                SetPage3_A
                POP  AF
                OR   A
                RET

Hero_StepWordTowardDE:
                PUSH HL
                OR   A
                SBC  HL, DE
                POP  HL
                RET  Z
                JR   C, .increase
                LD   BC, HERO_STEP_PIXELS
                OR   A
                SBC  HL, BC
                PUSH HL
                OR   A
                SBC  HL, DE
                POP  HL
                JR   NC, .changed
                EX   DE, HL
                SCF
                RET
.increase:      LD   BC, HERO_STEP_PIXELS
                ADD  HL, BC
                PUSH HL
                OR   A
                SBC  HL, DE
                POP  HL
                JR   C, .changed
                EX   DE, HL
.changed:       SCF
                RET

Hero_UpdateTileFromPixel:
                LD   HL, (HeroPixelX)
                CALL WordDiv32ToA
                CP   MAP_MAX_TILE_X + 1
                JR   C, .store_x
                LD   A, MAP_MAX_TILE_X
.store_x:       LD   (HeroTileX), A
                LD   HL, (HeroPixelY)
                CALL WordDiv32ToA
                CP   MAP_MAX_TILE_Y + 1
                JR   C, .store_y
                LD   A, MAP_MAX_TILE_Y
.store_y:       LD   (HeroTileY), A
                RET

Cursor_Update:
                LD   A, (InputState)
                AND  %00001111
                JR   NZ, .has_input
                CALL Cursor_UpdateFromMouse
                RET  C
                XOR  A
                LD   (CursorMoveCooldown), A
                RET

.has_input:     LD   A, (CursorMoveCooldown)
                OR   A
                JR   Z, .move
                DEC  A
                LD   (CursorMoveCooldown), A
                RET

.move:          LD   A, (InputState)
                BIT  0, A
                JR   Z, .check_right
                LD   HL, (CursorPixelX)
                LD   DE, CURSOR_STEP_PIXELS
                OR   A
                SBC  HL, DE
                JR   NC, .store_x_left
                LD   HL, 0
.store_x_left:  LD   (CursorPixelX), HL
                JR   .check_up

.check_right:   LD   A, (InputState)
                BIT  1, A
                JR   Z, .check_up
                LD   HL, (CursorPixelX)
                LD   DE, CURSOR_STEP_PIXELS
                ADD  HL, DE
                LD   DE, CURSOR_MAX_X
                CALL Cursor_ClampHLToDE
                LD   (CursorPixelX), HL

.check_up:      LD   A, (InputState)
                BIT  2, A
                JR   Z, .check_down
                LD   HL, (CursorPixelY)
                LD   DE, CURSOR_STEP_PIXELS
                OR   A
                SBC  HL, DE
                JR   NC, .store_y_up
                LD   HL, 0
.store_y_up:    LD   (CursorPixelY), HL
                JR   .moved

.check_down:    LD   A, (InputState)
                BIT  3, A
                JR   Z, .moved
                LD   HL, (CursorPixelY)
                LD   DE, CURSOR_STEP_PIXELS
                ADD  HL, DE
                LD   DE, CURSOR_MAX_Y
                CALL Cursor_ClampHLToDE
                LD   (CursorPixelY), HL

.moved:         CALL Cursor_UpdateTileFromPixel
.arm_delay:     XOR  A
                LD   (CursorMoveCooldown), A
                RET

Viewport_UpdateScroll:
                if VIEWPORT_DL_PACK
                CALL Viewport_AutoEdgeScroll
                RET  C
                LD   A, (InputState)
                BIT  0, A
                JR   Z, .right
                LD   HL, (CursorPixelX)
                LD   DE, GAME_VIEW_X + 1
                OR   A
                SBC  HL, DE
                JR   NC, .right
                LD   HL, (ViewportPixelX)
                LD   A, H
                OR   L
                JR   Z, .right
                LD   DE, CURSOR_STEP_PIXELS
                OR   A
                SBC  HL, DE
                JR   NC, .store_left
                LD   HL, 0
.store_left:   LD   (ViewportPixelX), HL
                JR   .refresh

.right:         LD   A, (InputState)
                BIT  1, A
                JR   Z, .up
                LD   HL, (CursorPixelX)
                LD   DE, GAME_VIEW_CURSOR_MAX_X
                OR   A
                SBC  HL, DE
                JR   C, .up
                LD   HL, (ViewportPixelX)
                LD   DE, CURSOR_STEP_PIXELS
                ADD  HL, DE
                LD   DE, VIEWPORT_PIXEL_MAX_X
                CALL Cursor_ClampHLToDE
                LD   (ViewportPixelX), HL
                JR   .refresh

.up:            LD   A, (InputState)
                BIT  2, A
                JR   Z, .down
                LD   HL, (CursorPixelY)
                LD   DE, GAME_VIEW_Y + 1
                OR   A
                SBC  HL, DE
                JR   NC, .down
                LD   HL, (ViewportPixelY)
                LD   A, H
                OR   L
                JR   Z, .down
                LD   DE, CURSOR_STEP_PIXELS
                OR   A
                SBC  HL, DE
                JR   NC, .store_up
                LD   HL, 0
.store_up:     LD   (ViewportPixelY), HL
                JR   .refresh

.down:          LD   A, (InputState)
                BIT  3, A
                JR   Z, .done
                LD   HL, (CursorPixelY)
                LD   DE, GAME_VIEW_CURSOR_MAX_Y
                OR   A
                SBC  HL, DE
                JR   C, .done
                LD   HL, (ViewportPixelY)
                LD   DE, CURSOR_STEP_PIXELS
                ADD  HL, DE
                LD   DE, VIEWPORT_PIXEL_MAX_Y
                CALL Cursor_ClampHLToDE
                LD   (ViewportPixelY), HL
.refresh:       CALL Viewport_UpdateOriginFromPixel
                CALL Cursor_UpdateTileFromPixel
.done:
                endif
                RET

Viewport_AutoEdgeScroll:
                if VIEWPORT_DL_PACK
                LD   B, 0
                LD   HL, (CursorPixelX)
                LD   DE, GAME_VIEW_X + 1
                OR   A
                SBC  HL, DE
                JR   NC, .right
                LD   HL, (ViewportPixelX)
                LD   A, H
                OR   L
                JR   Z, .right
                LD   DE, CURSOR_STEP_PIXELS
                OR   A
                SBC  HL, DE
                JR   NC, .store_left
                LD   HL, 0
.store_left:   LD   (ViewportPixelX), HL
                LD   B, 1
                JR   .up

.right:         LD   HL, (CursorPixelX)
                LD   DE, GAME_VIEW_CURSOR_MAX_X
                OR   A
                SBC  HL, DE
                JR   C, .up
                LD   HL, (ViewportPixelX)
                LD   DE, CURSOR_STEP_PIXELS
                ADD  HL, DE
                LD   DE, VIEWPORT_PIXEL_MAX_X
                CALL Cursor_ClampHLToDE
                LD   (ViewportPixelX), HL
                LD   B, 1

.up:            LD   HL, (CursorPixelY)
                LD   DE, GAME_VIEW_Y + 1
                OR   A
                SBC  HL, DE
                JR   NC, .down
                LD   HL, (ViewportPixelY)
                LD   A, H
                OR   L
                JR   Z, .down
                LD   DE, CURSOR_STEP_PIXELS
                OR   A
                SBC  HL, DE
                JR   NC, .store_up
                LD   HL, 0
.store_up:     LD   (ViewportPixelY), HL
                LD   B, 1
                JR   .done_axes

.down:          LD   HL, (CursorPixelY)
                LD   DE, GAME_VIEW_CURSOR_MAX_Y
                OR   A
                SBC  HL, DE
                JR   C, .done_axes
                LD   HL, (ViewportPixelY)
                LD   DE, CURSOR_STEP_PIXELS
                ADD  HL, DE
                LD   DE, VIEWPORT_PIXEL_MAX_Y
                CALL Cursor_ClampHLToDE
                LD   (ViewportPixelY), HL
.store_down:    LD   B, 1
.done_axes:     LD   A, B
                OR   A
                JR   Z, .none
                CALL Viewport_UpdateOriginFromPixel
                CALL Cursor_UpdateTileFromPixel
                SCF
                RET
.none:          OR   A
                endif
                RET

Viewport_UpdateOriginFromPixel:
                if VIEWPORT_DL_PACK
                LD   HL, (ViewportPixelX)
                CALL WordDiv32ToA
                LD   (ViewportOriginX), A
                LD   HL, (ViewportPixelY)
                CALL WordDiv32ToA
                LD   (ViewportOriginY), A
                endif
                RET

Cursor_StoreMousePos:
                CALL Input_MouseX
                LD   (CursorLastMouseX), HL
                CALL Input_MouseY
                LD   (CursorLastMouseY), HL
                RET

Cursor_UpdateFromMouse:
                CALL Input_MouseX
                LD   DE, (CursorLastMouseX)
                OR   A
                SBC  HL, DE
                JR   NZ, .changed
                CALL Input_MouseY
                LD   DE, (CursorLastMouseY)
                OR   A
                SBC  HL, DE
                RET  Z

.changed:       CALL Cursor_StoreMousePos
                LD   HL, (CursorLastMouseX)
                LD   DE, CURSOR_MAX_X
                CALL Cursor_ClampHLToDE
                LD   (CursorPixelX), HL
                LD   HL, (CursorLastMouseY)
                LD   DE, CURSOR_MAX_Y
                CALL Cursor_ClampHLToDE
                LD   (CursorPixelY), HL
                CALL Cursor_UpdateTileFromPixel
                XOR  A
                LD   (CursorMoveCooldown), A
                SCF
                RET

Cursor_UpdateTileFromPixel:
                CALL Cursor_CheckGameArea
                RET  Z
                LD   HL, (CursorPixelX)
                LD   DE, GAME_VIEW_X
                OR   A
                SBC  HL, DE
                if VIEWPORT_DL_PACK
                LD   DE, (ViewportPixelX)
                ADD  HL, DE
                CALL Cursor_WordDiv32ClampMapX
                else
                CALL Cursor_WordDiv32ClampX
                endif
                LD   (CursorTileX), A
                LD   HL, (CursorPixelY)
                LD   DE, GAME_VIEW_Y
                OR   A
                SBC  HL, DE
                if VIEWPORT_DL_PACK
                LD   DE, (ViewportPixelY)
                ADD  HL, DE
                CALL Cursor_WordDiv32ClampMapY
                else
                CALL Cursor_WordDiv32ClampY
                endif
                LD   (CursorTileY), A
                RET

Cursor_UpdateTheme:
                LD   A, (CursorInGameArea)
                OR   A
                JR   Z, .pointer
                ; КАК ТОЛЬКО начался расчёт маршрута (PATH_STATE_SEARCH) — СРАЗУ
                ; показываем курсор-лошадку (фидбэк: Z80 считает путь). Раньше тут
                ; был указатель → казалось, что во время расчёта ничего не происходит.
                ; (В оригинале путь предпросчитан на ховере; у нас Z80 медленный,
                ; поэтому даём визуальный отклик на момент клика/начала поиска.)
                LD   A, (PathState)
                CP   PATH_STATE_SEARCH
                JR   Z, .move
                LD   A, (PathFound)
                OR   A
                JR   Z, .pointer
                LD   A, (HeroPathLen)
                OR   A
                JR   Z, .pointer
                LD   A, (CursorTileX)
                LD   B, A
                LD   A, (HeroTargetX)
                CP   B
                JR   NZ, .pointer
                LD   A, (CursorTileY)
                LD   B, A
                LD   A, (HeroTargetY)
                CP   B
                JR   NZ, .pointer
.move:          LD   A, CURSOR_MOVE_BASE_INDEX
                LD   (CursorSpriteIndex), A
                RET
.pointer:       XOR  A
                LD   (CursorSpriteIndex), A
                RET

Cursor_CheckGameArea:
                LD   HL, (CursorPixelX)
                LD   DE, GAME_VIEW_X
                OR   A
                SBC  HL, DE
                JR   C, .out
                PUSH HL
                LD   DE, GAME_VIEW_W
                OR   A
                SBC  HL, DE
                POP  HL
                JR   NC, .out
                LD   HL, (CursorPixelY)
                LD   DE, GAME_VIEW_Y
                OR   A
                SBC  HL, DE
                JR   C, .out
                PUSH HL
                LD   DE, GAME_VIEW_H
                OR   A
                SBC  HL, DE
                POP  HL
                JR   NC, .out
                LD   A, 1
                LD   (CursorInGameArea), A
                OR   A
                RET
.out:           XOR  A
                LD   (CursorInGameArea), A
                RET

Cursor_ClampHLToDE:
                PUSH HL
                OR   A
                SBC  HL, DE
                POP  HL
                RET  C
                EX   DE, HL
                RET

WordDiv32ToA:
                SRL  H
                RR   L
                SRL  H
                RR   L
                SRL  H
                RR   L
                SRL  H
                RR   L
                SRL  H
                RR   L
                LD   A, L
                RET

Cursor_WordDiv32ClampX:
                CALL WordDiv32ToA
                CP   20
                RET  C
                LD   A, 19
                RET

Cursor_WordDiv32ClampY:
                CALL Cursor_WordDiv32ClampX
                CP   15
                RET  C
                LD   A, 14
                RET

Cursor_WordDiv32ClampMapX:
                CALL WordDiv32ToA
                CP   MAP_MAX_TILE_X + 1
                RET  C
                LD   A, MAP_MAX_TILE_X
                RET

Cursor_WordDiv32ClampMapY:
                CALL WordDiv32ToA
                CP   MAP_MAX_TILE_Y + 1
                RET  C
                LD   A, MAP_MAX_TILE_Y
                RET

Tile_MulA32ToHL:
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                RET

Map_IsTilePassable:
                GetPage3
                LD   (.RestorePage), A
                SetPage3 MAP0_PASS_PAGE
                CALL Map_TilePassabilityAddr
                LD   A, (HL)
                OR   A
                JR   Z, .blocked
                LD   A, 1
                JR   .restore
.blocked:       XOR  A
.restore:       PUSH AF
.RestorePage    EQU $+1
                LD   A, #00
                SetPage3_A
                POP  AF
                OR   A
                RET

Map_IsTilePassableFromMask:
                LD   (PathMoveMask), A
                GetPage3
                LD   (.RestorePage), A
                SetPage3 MAP0_PASS_PAGE
                CALL Map_TilePassabilityAddr
                LD   A, (HL)
                LD   HL, PathMoveMask
                AND  (HL)
                JR   Z, .blocked
                LD   A, 1
                JR   .restore
.blocked:       XOR  A
.restore:       PUSH AF
.RestorePage    EQU $+1
                LD   A, #00
                SetPage3_A
                POP  AF
                OR   A
                RET

Map_GetTilePathCost:
                GetPage3
                LD   (.RestorePage), A
                SetPage3 MAP0_PATH_PAGE
                CALL Map_TilePathCostAddr
                LD   A, (HL)
                PUSH AF
.RestorePage    EQU $+1
                LD   A, #00
                SetPage3_A
                POP  AF
                RET

Map_GetTilePathFlags:
                GetPage3
                LD   (.RestorePage), A
                SetPage3 MAP0_PATH_PAGE
                CALL Map_TilePathFlagsAddr
                LD   A, (HL)
                PUSH AF
.RestorePage    EQU $+1
                LD   A, #00
                SetPage3_A
                POP  AF
                RET

Path_DebugAppendCurrent:
                LD   HL, (PathDebugLen)
                LD   DE, PATH_DEBUG_MAX
                OR   A
                SBC  HL, DE
                RET  NC
                LD   HL, (PathDebugLen)
                LD   DE, PATH_DEBUG_X_BUF
                ADD  HL, DE
                LD   A, (PathCurrentX)
                LD   (HL), A
                LD   HL, (PathDebugLen)
                LD   DE, PATH_DEBUG_Y_BUF
                ADD  HL, DE
                LD   A, (PathCurrentY)
                LD   (HL), A
                LD   HL, (PathDebugLen)
                INC  HL
                LD   (PathDebugLen), HL
                RET

Path_LoadCurrentCost:
                LD   A, (PathCurrentX)
                LD   B, A
                LD   A, (PathCurrentY)
                LD   C, A
                CALL Path_CostLoAddr
                LD   A, (HL)
                LD   (PathCurrentCost), A
                CALL Path_CostHiAddr
                LD   A, (HL)
                LD   (PathCurrentCost + 1), A
                RET

Path_CurrentCanExpand:
                LD   A, (PathCurrentX)
                LD   B, A
                LD   A, (PathCurrentY)
                LD   C, A
                LD   A, (HeroTileX)
                CP   B
                JR   NZ, .check_flags
                LD   A, (HeroTileY)
                CP   C
                JR   NZ, .check_flags
                LD   A, 1
                OR   A
                RET
.check_flags:   CALL Map_GetTilePathFlags
                AND  PATH_FLAG_STOP
                JR   NZ, .blocked
                LD   A, 1
                OR   A
                RET
.blocked:       XOR  A
                RET

Path_TryNeighbor:
                LD   A, D
                LD   (PathParentCode), A
                LD   A, B
                LD   (PathTempX), A
                LD   A, C
                LD   (PathTempY), A

                LD   A, (HeroTileX)
                CP   B
                JR   NZ, .check_exit
                LD   A, (HeroTileY)
                CP   C
                RET  Z

.check_exit:    PUSH BC
                LD   A, (PathCurrentX)
                LD   B, A
                LD   A, (PathCurrentY)
                LD   C, A
                LD   A, (PathParentCode)
                CALL Path_ExitMaskFromParentCode
                CALL Map_IsTilePassableFromMask
                POP  BC
                RET  Z

                PUSH BC
                LD   A, (PathParentCode)
                CALL Path_EntryMaskFromParentCode
                CALL Map_IsTilePassableFromMask
                POP  BC
                RET  Z

                PUSH BC
                CALL Map_GetTilePathFlags
                LD   (PathToFlags), A
                POP  BC
                AND  PATH_FLAG_WATER
                RET  NZ

                PUSH BC
                LD   A, (PathCurrentX)
                LD   B, A
                LD   A, (PathCurrentY)
                LD   C, A
                CALL Map_GetTilePathFlags
                LD   (PathFromFlags), A
                POP  BC

                CALL Path_ComputePenalty
                LD   HL, (PathCurrentCost)
                LD   DE, (PathPenalty)
                ADD  HL, DE
                LD   (PathNewCost), HL

                CALL Path_ParentAddr
                LD   A, (HL)
                CP   #FF
                JR   Z, .update
                CALL Path_CostLoAddr
                LD   E, (HL)
                CALL Path_CostHiAddr
                LD   D, (HL)
                LD   HL, (PathNewCost)
                OR   A
                SBC  HL, DE
                RET  NC

.update:        CALL Path_ParentAddr
                LD   A, (PathParentCode)
                LD   (HL), A
                CALL Path_CostLoAddr
                LD   A, (PathNewCost)
                LD   (HL), A
                CALL Path_CostHiAddr
                LD   A, (PathNewCost + 1)
                LD   (HL), A
                CALL Path_EnqueueBC
                RET

Path_ComputePenalty:
                LD   A, (PathFromFlags)
                AND  PATH_FLAG_ROAD
                JR   Z, .ground
                LD   A, (PathToFlags)
                AND  PATH_FLAG_ROAD
                JR   Z, .ground
                LD   HL, 75
                JR   .diagonal
.ground:        PUSH BC
                LD   A, (PathCurrentX)
                LD   B, A
                LD   A, (PathCurrentY)
                LD   C, A
                CALL Map_GetTilePathCost
                POP  BC
                LD   L, A
                LD   H, 0
.diagonal:      LD   A, (PathParentCode)
                CALL Path_IsDiagonalCode
                JR   Z, .store
                LD   D, H
                LD   E, L
                SRL  D
                RR   E
                ADD  HL, DE
.store:         LD   (PathPenalty), HL
                RET

Path_IsDiagonalCode:
                AND  1
                JR   Z, .diagonal
                XOR  A
                RET
.diagonal:      LD   A, 1
                OR   A
                RET

Path_ExitMaskFromParentCode:
                CP   0
                JR   Z, .to_top_left
                CP   1
                JR   Z, .to_top
                CP   2
                JR   Z, .to_top_right
                CP   3
                JR   Z, .to_right
                CP   4
                JR   Z, .to_bottom_right
                CP   5
                JR   Z, .to_bottom
                CP   6
                JR   Z, .to_bottom_left
                LD   A, #80
                RET
.to_top_left:   LD   A, #01
                RET
.to_top:        LD   A, #02
                RET
.to_top_right:  LD   A, #04
                RET
.to_right:      LD   A, #08
                RET
.to_bottom_right:
                LD   A, #10
                RET
.to_bottom:     LD   A, #20
                RET
.to_bottom_left:
                LD   A, #40
                RET

Path_EntryMaskFromParentCode:
                CP   0
                JR   Z, .from_bottom_right
                CP   1
                JR   Z, .from_bottom
                CP   2
                JR   Z, .from_bottom_left
                CP   3
                JR   Z, .from_left
                CP   4
                JR   Z, .from_top_left
                CP   5
                JR   Z, .from_top
                CP   6
                JR   Z, .from_top_right
                LD   A, #08
                RET
.from_bottom_right:
                LD   A, #10
                RET
.from_bottom:   LD   A, #20
                RET
.from_bottom_left:
                LD   A, #40
                RET
.from_left:     LD   A, #80
                RET
.from_top_left: LD   A, #01
                RET
.from_top:      LD   A, #02
                RET
.from_top_right:
                LD   A, #04
                RET

Path_CheckFound:
                LD   A, (PathFound)
                OR   A
                RET

Path_QueueEmpty:
                LD   HL, (PathQueueHead)
                LD   DE, (PathQueueTail)
                OR   A
                SBC  HL, DE
                RET

Path_EnqueueBC:
                PUSH BC
                LD   DE, (PathQueueTail)
                LD   A, D
                CP   #10
                JR   NC, .overflow
                LD   HL, PATH_QUEUE_X_BUF
                ADD  HL, DE
                LD   (HL), B
                LD   HL, PATH_QUEUE_Y_BUF
                ADD  HL, DE
                LD   (HL), C
                INC  DE
                LD   (PathQueueTail), DE
.overflow:
                POP  BC
                RET

Path_DequeueBC:
                LD   DE, (PathQueueHead)
                LD   HL, PATH_QUEUE_X_BUF
                ADD  HL, DE
                LD   B, (HL)
                LD   HL, PATH_QUEUE_Y_BUF
                ADD  HL, DE
                LD   C, (HL)
                INC  DE
                LD   (PathQueueHead), DE
                RET

Path_Reconstruct:
                XOR  A
                LD   (HeroPathLen), A
                LD   A, (PathTargetX)
                LD   B, A
                LD   A, (PathTargetY)
                LD   C, A
.loop:          LD   A, (HeroTileX)
                CP   B
                JR   NZ, .store
                LD   A, (HeroTileY)
                CP   C
                JR   Z, .done
.store:         LD   A, (HeroPathLen)
                CP   HERO_PATH_MAX
                JR   NC, .fail
                LD   E, A
                LD   D, 0
                LD   HL, HeroPathXBuf
                ADD  HL, DE
                LD   (HL), B
                LD   HL, HeroPathYBuf
                ADD  HL, DE
                LD   (HL), C
                LD   A, (HeroPathLen)
                INC  A
                LD   (HeroPathLen), A

                CALL Path_ParentAddr
                LD   A, (HL)
                CP   #FE
                JR   Z, .done
                CP   0
                JP   Z, .parent_right_down
                CP   1
                JP   Z, .parent_down
                CP   2
                JP   Z, .parent_left_down
                CP   3
                JP   Z, .parent_left
                CP   4
                JP   Z, .parent_left_up
                CP   5
                JP   Z, .parent_up
                CP   6
                JP   Z, .parent_right_up
                CP   7
                JP   Z, .parent_right
.fail:          XOR  A
                LD   (HeroPathLen), A
                LD   (PathFound), A
                RET
.parent_left:   DEC  B
                JP   .loop
.parent_right:  INC  B
                JP   .loop
.parent_up:     DEC  C
                JP   .loop
.parent_down:   INC  C
                JP   .loop
.parent_left_up:
                DEC  B
                DEC  C
                JP   .loop
.parent_left_down:
                DEC  B
                INC  C
                JP   .loop
.parent_right_up:
                INC  B
                DEC  C
                JP   .loop
.parent_right_down:
                INC  B
                INC  C
                JP   .loop
.done:          LD   A, (HeroPathLen)
                OR   A
                JR   Z, .same_tile
                DEC  A
                LD   (HeroPathIndex), A
                LD   A, 1
                LD   (PathFound), A
                RET
.same_tile:     XOR  A
                LD   (HeroPathIndex), A
                LD   A, 1
                LD   (PathFound), A
                RET

Path_ParentAddr:
                CALL Map_TileIndexToHL
                LD   DE, PATH_PARENT_BUF
                ADD  HL, DE
                RET

Path_CostLoAddr:
                CALL Map_TileIndexToHL
                LD   DE, PATH_COST_LO_BUF
                ADD  HL, DE
                RET

Path_CostHiAddr:
                CALL Map_TileIndexToHL
                LD   DE, PATH_COST_HI_BUF
                ADD  HL, DE
                RET

Map_TileIndexToHL:
                LD   L, C
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                EX   DE, HL
                LD   L, C
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE
                LD   E, B
                LD   D, 0
                ADD  HL, DE
                RET

Map_TileObjectAddr:
                CALL Map_TileIndexToHL
                PUSH HL
                ADD  HL, HL
                ADD  HL, HL
                EX   DE, HL
                POP  HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE
                LD   DE, #C000 + 19
                ADD  HL, DE
                RET

Map_TilePassabilityAddr:
                CALL Map_TileIndexToHL
                LD   DE, #C000 + MAP0_PASS_ADDR
                ADD  HL, DE
                RET

Map_TilePathCostAddr:
                CALL Map_TileIndexToHL
                LD   DE, #C000 + MAP0_PATH_COST_ADDR
                ADD  HL, DE
                RET

Map_TilePathFlagsAddr:
                CALL Map_TileIndexToHL
                LD   DE, #C000 + MAP0_PATH_FLAGS_ADDR
                ADD  HL, DE
                RET

                endif
