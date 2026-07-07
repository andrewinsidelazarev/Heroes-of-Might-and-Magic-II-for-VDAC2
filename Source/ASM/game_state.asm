                ifndef _HMM2_GAME_STATE_
                define _HMM2_GAME_STATE_

GAME_MODE_ADVENTURE EQU 0
GAME_MODE_TOWN      EQU 1
GAME_MODE_COMBAT    EQU 2
GAME_MODE_MENU      EQU 3
GAME_MODE_HIGHSCORES_STANDARD EQU 4
GAME_MODE_HIGHSCORES_CAMPAIGN EQU 5

CURSOR_STEP_PIXELS  EQU 5
; Логический viewport игры: 640×480, поверх физического FT812 1024×768.
; Не пересчитывать эти границы под физический режим.
CURSOR_MAX_X        EQU 624
CURSOR_MAX_Y        EQU 464
; Edge-scroll по оригиналу fheroes2 (interface_base.h isScrollLeft/Right/Top/Bottom):
; scroll-зона = бордюр borderWidthPx=16 у самого края ЭКРАНА, НЕ у края game area.
; left: x<16, right: x>=640-16=624, top: y<16, bottom: y>=480-16=464. Radar/кнопки
; (480..624) внутри → наведение на них (вкл. End Turn) НЕ скроллит карту.
SCROLL_EDGE_BORDER  EQU 16
; Старт как в ОРИГИНАЛЕ: герой рекрутируется в ПЕРВОМ замке (startWithHeroInFirstCastle),
; ставится у гейта замка (GetCenter). Первый замок игрока — OBJNTOWN, гейт (24,13).
; Герой стоит на тайле ПОД гейтом (24,14): вход в замок = клик по гейту → шаг вверх на (24,13)
; → штатный вход по прибытии (Hero_SelectStepIfArrived). Спавн ПРЯМО на (24,13) не давал бы войти
; (вход только «по прибытии шагом», а стоя на тайле прибытия нет). Гейт проходим.
HERO_START_TILE_X   EQU 24
HERO_START_TILE_Y   EQU 14
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
                LD   A, 1                         ; сложность по умолчанию = Normal (экран сценария);
                LD   (GameDifficulty), A          ; init ЗДЕСЬ (резидент, boot), НЕ в Menu_Enter —
                                                  ; там чтение/запись ломало загрузку меню в чёрный
                CALL Cursor_GlobalUpload          ; глобальный курсор в постоянную RAM_G (раз)
                CALL Music_InitPort               ; AY port A → выход (иначе MIDI не идёт на пин)
                CALL Music_GMReset                ; SAM2695 → General MIDI (раз при старте)
            IFDEF DBG_BOOT_ADVENTURE
                CALL Adventure_Enter              ; DEBUG: сразу в игровой экран для ground-truth-проверки
            ELSE
                CALL Menu_Enter_Tramp            ; меню в оверлее (slot3) — через резидентный трамплин
            ENDIF
                RET

; --- Стрим битмапов карты adventure (террейн/объекты/вьюпорты) с SD в их Z80-страницы ---
; Балласт ~2.2МБ (раньше пёкся в SPG) вынесен в HMM2ADV.PAK. Грузим на входе в adventure
; (ДО Background_Upload, который читает страницы #20-8F). MapStreamTable: на запись
; (страница, число секторов); читаем ПОДРЯД — PAK уложен посекторно, позиция сама встаёт
; на следующий блок. Имя — общий MenuNameBuf (slot1; raw_pak ремапит slot2). Loader_ReadSectors
; сам гоняет SP в slot1-стек и восстанавливает slot2/3 → между записями страницы/таблица целы.
Adventure_LoadMap:
                LD   HL, MapPakName
                LD   DE, MenuNameBuf
                LD   BC, 13
                LDIR
                CALL Loader_Init
                CALL Loader_Mount
                RET  NC
                LD   HL, MenuNameBuf
                CALL Loader_OpenFile
                RET  NC
                LD   C, RAWPAK_BUF_PAGE             ; пропустить header+каталог в buffer-page
                LD   HL, 0
                LD   B, MAP_BODY_SECTOR
                CALL Loader_ReadSectors
                LD   HL, MapStreamTable
.loop:          LD   C, (HL)                        ; страница назначения
                INC  HL
                LD   B, (HL)                        ; число секторов (=32, полная страница)
                INC  HL
                PUSH HL                             ; raw_pak КЛОБЕРИТ HL/BC/A/IX → указатель в стек
                LD   HL, 0
                CALL Loader_ReadSectors             ; B секторов с SD → страница C, офсет 0
                POP  HL                             ; вернуть указатель таблицы
                PUSH HL                             ; HL < конец таблицы?
                LD   DE, MapStreamTable + MAP_STREAM_COUNT * 2
                OR   A
                SBC  HL, DE
                POP  HL
                JR   C, .loop                       ; ещё есть записи
                RET
                include "generated_map_stream.inc"

; Вход в adventure-сцену: загрузка карты в RAM_G + инициализация состояния.
; Вызывается из Menu_Update по клику New Game (ленивая загрузка карты).
Adventure_Enter:
                CALL Music_Stop                   ; погасить меню-музыку (slot3 пойдёт под loader)
                CALL Render_BlackFrame            ; межсценный чёрный кадр ДО перезаписи RAM_G
                CALL Adventure_LoadMap            ; стрим битмапов карты (#20-8F) с SD в их страницы
                CALL Background_Upload            ; (иначе старый меню-DL покажет мусор поверх
                CALL Objects_Upload              ;  частично загруженных adventure-битмапов)
                LD   A, GAME_MODE_ADVENTURE
                LD   (GameMode), A
                LD   A, (AdvReenter)              ; ВОЗВРАТ из боя/города: НЕ сбрасывать героя/
                OR   A                            ; день/ресурсы/вьюпорт (только перезалив RAM_G)
                JR   NZ, .keepstate
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
                LD   A, STATUS_ARMY            ; дефолт статус-окна = армия героя (как оригинал)
                LD   (StatusState), A
                CALL Resources_InitStart
                CALL GState_Reset                ; новая игра → сброс снимка города в #91
                CALL AiKingdom_Init              ; ★новая игра → казна AI-королевства Sorc (враг) = стартовое золото
.keepstate:     XOR  A
                LD   (AdvReenter), A
                CALL Resources_BuildPanelDL      ; собрать DL панели в RAM_G (по StatusState)
                CALL SorcHero_LoadCache          ; ★кэш Sorc + разрешение исхода Sorc-боя (BattleVsSorc)
                XOR  A
                LD   (CursorMoveCooldown), A
                LD   (CursorSpriteIndex), A
                CALL Cursor_StoreMousePos
                ; Клик по New Game ещё «зажат»: погасить его для adventure, чтобы
                ; не превратился в команду движения героя до следующего нажатия.
                LD   A, 1
                LD   (HeroFireLatch), A
                ; Курсор грузится в Game_Init. КОРЕНЬ бага «нет курсора» был в RAM_G-коллизии:
                ; CURSOR_RAMG_BASE #0E0000 попадал ВНУТРЬ object atlas (разросся до #0E3382) →
                ; Objects_Upload затирал курсор. ИСПРАВЛЕНО переносом базы на #0E8000 (viewport_pack.py).
                ; Этот перезалив оставлен как СТРАХОВКА на случай будущих аплоадов в зону курсора.
                CALL Cursor_GlobalUpload
                RET

Game_Update:
                LD   HL, (FrameCounter)          ; общий счётчик кадров (анимация)
                INC  HL
                LD   (FrameCounter), HL
                LD   A, (GameMode)
                CP   GAME_MODE_MENU
                JP   Z, Menu_Update_Tramp
                CP   GAME_MODE_TOWN
                JP   Z, Town_Update_Tramp
                CP   GAME_MODE_COMBAT
                JP   Z, Battle_Update_Tramp
                CP   GAME_MODE_HIGHSCORES_STANDARD
                JP   Z, HiScores_Update_Tramp
                CP   GAME_MODE_HIGHSCORES_CAMPAIGN
                JP   Z, HiScores_Update_Tramp
                CALL Cursor_Update
                CALL Viewport_UpdateScroll
                CALL Hero_Update
                CALL UI_ButtonsStateUpdate
                CALL UI_ButtonsPressedUpdate      ; pressed-кадр пока ЛКМ реально зажата
                CALL Cursor_UpdateTheme
                ; --- End Turn: хоткей E (HotKeyEvent::END_TURN) → ПОЛНЫЙ новый день (edge-детект) ---
                LD   A, (Input_KE)
                LD   B, A
                LD   A, (DayLastE)
                CP   B
                LD   A, B
                LD   (DayLastE), A
                RET  Z                            ; состояние не менялось
                OR   A
                RET  Z                            ; отпускание
                JP   Game_EndTurn                 ; тот же новый день, что кнопка End Turn

; ЕДИНЫЙ счётчик игровых дней: DayCounter (экономика города) = GameDay (End Turn/E).
; Город догоняет при входе (Town_Enter сверяет TownLastDay): недельный рост жилищ,
; ALLOW_TO_BUILD_TODAY; доход золота — в Game_EndTurn (резидент, единая казна).
DayCounter:     EQU GameDay
DayLastE:       DEFB 0

; Возвращает в A индекс кнопки под мышью (row*4+col) или #FF.
UI_GetHoveredButton:
                CALL Input_MouseX                ; HL = x
                LD   DE, UI_BUTTON_X
                OR   A
                SBC  HL, DE
                JR   C, .none                    ; x < панели
                LD   A, H
                OR   A
                JR   NZ, .none                   ; x далеко справа
                LD   A, L
                LD   B, UI_BUTTON_W
                CALL UI_DivAB                    ; A = col
                CP   4
                JR   NC, .none
                PUSH AF                           ; save col
                CALL Input_MouseY                ; HL = y
                LD   DE, UI_BUTTON_Y
                OR   A
                SBC  HL, DE
                JR   C, .none_pop                ; y выше панели
                LD   A, H
                OR   A
                JR   NZ, .none_pop
                LD   A, L
                LD   B, UI_BUTTON_H
                CALL UI_DivAB                    ; A = row
                CP   2
                JR   NC, .none_pop
                ADD  A, A
                ADD  A, A                         ; row*4
                LD   C, A
                POP  AF                           ; restore col
                ADD  A, C                         ; + col
                RET
.none_pop:      POP  AF
.none:          LD   A, #FF
                RET

; Пока ЛКМ зажата над активной кнопкой — UI_ButtonPressed = её индекс (row*4+col),
; иначе #FF. Геометрия как в UI_ButtonClick (сетка 4×2 от UI_BUTTON_X/Y).
UI_ButtonsPressedUpdate:
                LD   A, (UI_ActiveButton)
                CP   #FF
                JR   Z, .none
                CALL Input_MouseLMB
                JR   Z, .none                    ; ЛКМ отпущена
                CALL UI_GetHoveredButton
                LD   B, A
                LD   A, (UI_ActiveButton)
                CP   B
                JR   NZ, .none
                
                ; Проверяем, не является ли кнопка Disabled (3)
                LD   C, A
                LD   HL, UI_ButtonStates
                LD   B, 0
                ADD  HL, BC
                LD   A, (HL)
                CP   3
                JR   Z, .none                    ; Disabled-кнопки не нажимаются
                
                LD   A, C
                LD   (UI_ButtonPressed), A
                RET
.none:          LD   A, #FF
                LD   (UI_ButtonPressed), A
                RET

; Пересчитывает логические состояния всех кнопок на панели
UI_ButtonsStateUpdate:
                ; Сброс ВСЕХ 8 состояний в Normal(0). Без него индексы 0/2/3/5/6/7 —
                ; мусор в #4274 → Render_AdvButtonsCmd индексирует UI_BtnColors за таблицей
                ; → мусорный FT_COLOR_RGB (зелёный тинт на Adventure-флаге и т.п.).
                XOR  A
                LD   HL, UI_ButtonStates
                LD   B, 8
.clrstate:      LD   (HL), A
                INC  HL
                DJNZ .clrstate
                ; 1. Hero Movement (индекс 1)
                ; Если нет активного героя (пока упрощенно), то Disabled (3)
                ; Если HeroPathLen == 0, то Disabled (3)
                ; Если HeroPathLen > 0, но HeroMovePoints == 0, то Inactive (2)
                ; Иначе Move (0)
                LD   A, (HeroPathLen)
                OR   A
                JR   Z, .hero_move_disabled
                LD   A, (HeroMovePoints)
                OR   A
                JR   Z, .hero_move_inactive
                LD   A, 0                       ; 0 = Normal
                JR   .hero_move_done
.hero_move_inactive:
                LD   A, 2                       ; 2 = Inactive
                JR   .hero_move_done
.hero_move_disabled:
                LD   A, 3                       ; 3 = Disabled
.hero_move_done:
                LD   (UI_HeroMoveButtonState), A

                ; NextHero (индекс 0): disabled, если у героя не осталось хода (MovePoints==0).
                ; fheroes2 interface_buttons.cpp:328 — enabled только при наличии ходячего героя.
                LD   A, (HeroMovePoints)
                OR   A
                JR   NZ, .next_hero_ok
                LD   A, 3                       ; 3 = Disabled
                LD   (UI_ButtonStates), A        ; индекс 0 = NextHero
.next_hero_ok:

                ; End Turn (индекс 4) - пока всегда 0
                XOR  A
                LD   (UI_EndTurnButtonState), A
                RET

; Поставить героя на тайл B=x, C=y (телепорт: откат при поражении в бою). Портит A,HL.
Hero_SetTile:
                LD   A, B
                LD   (HeroTileX), A
                LD   (HeroTargetX), A
                LD   (HeroStepX), A
                CALL Tile_MulA32ToHL
                LD   (HeroPixelX), HL
                LD   A, C
                LD   (HeroTileY), A
                LD   (HeroTargetY), A
                LD   (HeroStepY), A
                CALL Tile_MulA32ToHL
                LD   (HeroPixelY), HL
                XOR  A
                LD   (HeroPathLen), A
                LD   (HeroPathIndex), A
                LD   (HeroWalkActive), A
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
                LD   (HeroWalkActive), A          ; спавн ≠ движение: не триггерить вход в гейт (24,13) на старте
                LD   (PathState), A
                LD   (PathDebugLen), A
                LD   (PathDebugLen + 1), A
                LD   A, #FF
                LD   (UI_ActiveButton), A
                LD   (UI_ButtonPressed), A
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
                CALL UI_GetHoveredButton
                CP   #FF
                JR   NZ, .do_btn
                CALL UI_DispatchClick
                RET
.do_btn:
                LD   (UI_ActiveButton), A
                LD   (UI_ButtonPressed), A
                CALL UI_ButtonClick_Index
                RET
.released:      LD   A, (HeroFireLatch)
                OR   A
                JR   Z, .clear_latch
.clear_latch:   XOR  A
                LD   (HeroFireLatch), A
                LD   A, #FF
                LD   (UI_ActiveButton), A
                LD   (UI_ButtonPressed), A
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
                JP   C, Adventure_GameAreaClick   ; клик по замку → город (оверлей), иначе команда герою
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
                JR   NC, .try_status          ; y >= 392 → возможно статус-окно
                JP   UI_ButtonClick
.try_status:    ; статус-окно [392..464): клик переключает вид (DATE↔FUNDS), как оригинал.
                LD   HL, (UIClickY)
                LD   DE, UI_STATUS_Y          ; 392
                OR   A
                SBC  HL, DE
                RET  C
                PUSH HL
                LD   DE, UI_STATUS_H          ; 72
                OR   A
                SBC  HL, DE
                POP  HL
                RET  NC                       ; y >= 464 → игнор
                LD   A, (StatusState)
                INC  A
                CP   STATUS_STATE_COUNT
                JR   C, .st_ok
                XOR  A
.st_ok:         LD   (StatusState), A
                JP   Resources_BuildPanelDL   ; пересобрать композит под новый вид

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
                CALL UI_GetHoveredButton
                CP   #FF
                RET  Z
UI_ButtonClick_Index:
                OR   A                           ; индекс 0 = Next Hero?
                JR   Z, .next_hero
                CP   4                           ; End Turn?
                JP   Z, Game_EndTurn
                CP   1                           ; Hero Movement?
                JR   Z, .hero_move
                RET

.next_hero:
                ; NextHero disabled, если нет хода (MovePoints==0) → клик игнор, как в оригинале.
                LD   A, (HeroMovePoints)
                OR   A
                RET  Z
                ; центрировать вьюпорт на герое (faithful EventNextHero → SetFocus).
                LD   A, (HeroTileX)
                LD   B, MAP0_W - GAME_VIEW_TILE_W
                CALL UI_CenterOrigin
                LD   (ViewportOriginX), A
                CALL UI_TileToPixelHL
                LD   (ViewportPixelX), HL
                LD   A, (HeroTileY)
                LD   B, MAP0_H - GAME_VIEW_TILE_H
                CALL UI_CenterOrigin
                LD   (ViewportOriginY), A
                CALL UI_TileToPixelHL
                LD   (ViewportPixelY), HL
                RET

.hero_move:
                LD   A, (HeroPathLen)
                OR   A
                RET  Z
                LD   A, 1
                LD   (HeroWalkActive), A
                RET

; A = A / B (B>0, малые значения), беззнаково.
UI_DivAB:       LD   C, 0
.loop:          CP   B
                JR   C, .done
                SUB  B
                INC  C
                JR   .loop
.done:          LD   A, C
                RET

; End Turn (кнопка панели И хоткей E): новый день + дневной запас хода героя + доход
; королевства (ProfitConditions: BUILD_CASTLE 1000 + BUILD_STATUE 250 — статуя из снимка
; города в #91: город догоняет недели/BuildToday сам при входе, Town_EconomyCatchUp).
Game_EndTurn:
                LD   HL, (GameDay)
                INC  HL
                LD   (GameDay), HL
                LD   A, HERO_MOVE_TILES_MAX
                LD   (HeroMovePoints), A
                LD   HL, (ResGold)               ; +1000 (замок), кламп 65535
                LD   DE, 1000
                ADD  HL, DE
                JR   NC, .nc1
                LD   HL, #FFFF
.nc1:           LD   (ResGold), HL
                CALL GState_Fetch                ; снимок города есть и Statue построена → +250
                OR   A
                JR   Z, .nostatue
                LD   A, (TownStateBuf + GSTATE_OFS_STATUE)
                OR   A
                JR   Z, .nostatue
                LD   HL, (ResGold)
                LD   DE, 250
                ADD  HL, DE
                JR   NC, .nc2
                LD   HL, #FFFF
.nc2:           LD   (ResGold), HL
.nostatue:      CALL AiKingdom_EndTurn            ; ★AI-фаза хода: доход королевства Sorc (враг) в #91
                CALL AiKingdom_MoveHero          ; ★Sorc-герой шаг к игроку (простой ход AI)
                CALL SorcHero_LoadCache          ; обновить кэш позиции Sorc для рендера
                CALL Resources_BuildPanelDL      ; пересобрать DL панели (золото изменилось)
                ; ★Sorc-герой дошёл до игрока (AI-фаза) → Sorc атакует: бой. Армия защиты =
                ; дефолт SKIRMISH (EngagedMonIdx=#FF → BattleUnitStateInit слоты 2,3).
                LD   A, (SorcAttackPending)       ; MoveHero обнуляет каждый ход → clear не нужен
                OR   A
                RET  Z
                JP   Sorc_TriggerBattle           ; Sorc дошёл до игрока → бой (общий триггер)

; Общий триггер боя против Sorc-героя (forward: Sorc→игрок в End Turn; reverse: игрок→Sorc
; при прибытии). Армия защиты = дефолт SKIRMISH (EngagedMonIdx=#FF → BattleUnitStateInit 2,3).
; BattleVsSorc=1 → battle.asm .exit пишет маркер исхода (2=победа → Sorc снят в LoadCache).
Sorc_TriggerBattle:
                LD   A, #FF
                LD   (EngagedMonIdx), A
                LD   A, 1
                LD   (BattleVsSorc), A
                JP   Battle_Enter_Tramp

; Стартовые ресурсы королевства (fheroes2 _getKingdomStartingResources, человек) ПО СЛОЖНОСТИ
; GameDifficulty: копируем запись ResStartTab[diff] (7×DW gold,wood,merc,ore,sulf,cryst,gems) →
; вектор KingdomFunds. Вне диапазона → Normal (1). Порядок вектора совпадает с fheroes2 Cost.
Resources_InitStart:
                LD   A, (GameDifficulty)
                CP   5
                JR   C, .ok
                LD   A, 1                          ; мусор → Normal
.ok:            LD   L, A                          ; HL = diff×14 (×2+×4+×8)
                LD   H, 0
                ADD  HL, HL                        ; ×2
                LD   D, H
                LD   E, L                          ; DE = ×2
                ADD  HL, HL                        ; ×4
                ADD  HL, HL                        ; ×8
                ADD  HL, DE                        ; ×10
                ADD  HL, DE                        ; ×12
                ADD  HL, DE                        ; ×14
                LD   DE, ResStartTab
                ADD  HL, DE
                LD   DE, KingdomFunds
                LD   BC, 14
                LDIR
                RET
; [difficulty] → 7×DW (gold,wood,mercury,ore,sulfur,crystal,gems). fheroes2 kingdom.cpp:881.
ResStartTab:
                DEFW 10000, 30, 10, 30, 10, 10, 10   ; Easy
                DEFW 7500, 20, 5, 20, 5, 5, 5        ; Normal
                DEFW 5000, 10, 2, 10, 2, 2, 2        ; Hard
                DEFW 2500, 5, 0, 5, 0, 0, 0          ; Expert
                DEFW 0, 0, 0, 0, 0, 0, 0             ; Impossible

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

                ; Клик по тайлу, на котором герой УЖЕ СТОИТ → действие объекта сразу (ориг.:
                ; повторный клик по замку под ногами открывает город; после выхода герой
                ; остаётся на гейте (24,13) и «вход по прибытии» не сработал бы).
                LD   A, (HeroTileX)
                CP   B
                JR   NZ, .not_self
                LD   A, (HeroTileY)
                CP   C
                JR   NZ, .not_self
                LD   A, B
                CP   24
                JR   NZ, .not_self
                LD   A, C
                CP   13
                JP   Z, Town_Enter_Tramp          ; стоим на гейте → войти в замок
.not_self:
                LD   A, (HeroTargetX)
                CP   B
                JR   NZ, .new_target
                LD   A, (HeroTargetY)
                CP   C
                JR   NZ, .new_target

                LD   A, (HeroPathLen)
                OR   A
                RET  Z                  ; маршрута нет (или 0), ничего не делаем
                
                LD   A, 1
                LD   (HeroWalkActive), A
                RET
                
.new_target:
                XOR  A
                LD   (HeroWalkActive), A
                
                CALL Hero_SetTargetIfPassable
                RET

Hero_MoveTowardTarget:
                LD   A, (HeroWalkActive)
                OR   A
                RET  Z

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
                LD   (HeroWalkActive), A
                ; Прибыли на КЛИКНУТУЮ цель (по оригиналу действие = шаг героя на тайл, не клик).
                ; B=TileX, C=TileY. 1) БРОДЯЧИЙ МОНСТР (MapMonsterTab, random разрешён при
                ; конвертации) → БОЙ с его армией; 2) гейт замка (24,13) → город.
                CALL Hero_FindMonsterAt         ; A=индекс живого монстра на (B,C) или #FF
                CP   #FF
                JR   Z, .no_monster
                LD   (EngagedMonIdx), A          ; бой с этим монстром (армия из таблицы)
                XOR  A
                LD   (BattleVsSorc), A            ; монстр-бой, не Sorc (маркер чистый для .exit)
                JP   Battle_Enter_Tramp
.no_monster:    ; ★Обратное столкновение: игрок пришёл НА тайл Sorc-героя → бой (игрок атакует).
                LD   A, (SorcHeroVisible)       ; Sorc на карте (hasHero)?
                OR   A
                JR   Z, .no_sorc
                LD   A, (SorcHeroTileX)
                CP   B
                JR   NZ, .no_sorc
                LD   A, (SorcHeroTileY)
                CP   C
                JR   NZ, .no_sorc
                JP   Sorc_TriggerBattle         ; тайл совпал → бой против Sorc (общий триггер)
.no_sorc:       LD   A, B
                CP   24
                RET  NZ                         ; не колонка 24 → ничего
                LD   A, C
                CP   13
                JP   Z, Town_Enter_Tramp        ; гейт замка (24,13) → войти в замок
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
                LD   (HeroWalkActive), A
                RET

; B=TileX, C=TileY → A = индекс ЖИВОГО монстра MapMonsterTab на этом тайле, или #FF. Портит DE,HL.
Hero_FindMonsterAt:
                LD   HL, MapMonsterTab
                LD   D, 0                        ; индекс
.fmloop:        LD   A, (HL)                     ; x
                CP   B
                JR   NZ, .fmnext
                INC  HL
                LD   A, (HL)                     ; y
                DEC  HL
                CP   C
                JR   NZ, .fmnext
                PUSH HL
                LD   E, 5
                ADD  HL, DE                      ; +5 alive (E=5, D=0)
                LD   A, (HL)
                POP  HL
                OR   A
                JR   Z, .fmnext                  ; убит
                LD   A, D
                RET
.fmnext:        LD   A, 6
                ADD  A, L
                LD   L, A
                JR   NC, .fmnc
                INC  H
.fmnc:          INC  D
                LD   A, D
                CP   MAP_MONSTER_COUNT
                JR   C, .fmloop
                LD   A, #FF
                RET
EngagedMonIdx:  DEFB #FF                        ; монстр текущего боя (#FF = бой не с монстром карты)
AdvReenter:     DEFB 0                          ; 1 = возврат в adventure из сцены (сохранить состояние)
HeroPrevTileX:  DEFB 0                          ; тайл ДО последнего шага (откат при поражении)
HeroPrevTileY:  DEFB 0

; Подбор ресурсов: линейный поиск тайла героя в PickupList (из generated_runtime_map).
; При первом наступании — начислить ресурс по resource_idx, пометить taken, перестроить
; панель. taken-битмап защищает от повторного начисления.
PickupTaken:    DEFS (PICKUP_COUNT + 7) / 8

Pickup_SavedP3: DEFB 0                          ; сохранённый slot3 на время чтения PickupList из #91
Pickup_ResIdx:  DEFB 0                          ; resource_idx найденного тайла (перед restore slot3)
Hero_CheckPickup:
                LD   A, PICKUP_COUNT
                OR   A
                RET  Z
                GetPage3                        ; PickupList вынесен в data-страницу #91 (не резидент)
                LD   (Pickup_SavedP3), A
                SetPage3 GLOBAL_DATA_PAGE
                LD   IX, PickupList
                LD   B, PICKUP_COUNT
                LD   C, 0
.loop:          LD   A, (HeroTileX)
                CP   (IX + 0)
                JR   NZ, .next
                LD   A, (HeroTileY)
                CP   (IX + 1)
                JR   NZ, .next
                LD   A, (IX + 2)               ; resource_idx (в #91)
                LD   (Pickup_ResIdx), A
                LD   A, (Pickup_SavedP3)        ; вернуть slot3 ДО резидентной обработки
                SetPage3_A
                PUSH BC
                CALL Pickup_BitPtr             ; HL = байт taken, A = маска (по C)
                LD   D, A
                AND  (HL)
                JR   NZ, .seen                 ; уже подобрано
                LD   A, (HL)
                OR   D
                LD   (HL), A                   ; пометить taken
                LD   A, (Pickup_ResIdx)        ; resource_idx
                CALL Pickup_AddResource
                CALL Resources_BuildPanelDL
.seen:          POP  BC
                RET
.next:          INC  C
                LD   DE, 3
                ADD  IX, DE
                DJNZ .loop
                LD   A, (Pickup_SavedP3)        ; нет совпадения → вернуть slot3
                SetPage3_A
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
                LD   A, (HeroTileX)             ; тайл ДО шага (откат героя при поражении в бою)
                LD   (HeroPrevTileX), A
                LD   A, (HeroTileY)
                LD   (HeroPrevTileY), A
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
                ; Клава/Kempston двигают ГЛОБАЛЬНУЮ мышь (Input_VirtualCursor, input.asm) —
                ; курсор карты синкается с неё ЕДИНЫМ путём: мышь и клавиатура неотличимы.
                ; (Прежняя локальная key-ветка удалена — она дублировала бы шаг.)
                CALL Cursor_UpdateFromMouse
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
                LD   DE, SCROLL_EDGE_BORDER          ; left: x < 16
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
                LD   DE, CURSOR_MAX_X   ; right: x >= 624
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
                LD   DE, SCROLL_EDGE_BORDER          ; top: y < 16
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
                LD   DE, CURSOR_MAX_Y   ; bottom: y >= 464
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
                CALL Cursor_ScrollTheme          ; стрелка скролла на кромке экрана
                RET  C                            ; выставлена — приоритет над pointer/move
                LD   A, (CursorInGameArea)
                OR   A
                JP   Z, .pointer
                ; ★ПО ОРИГИНАЛУ (GetCursorFocusHeroes, game_startgame.cpp:603): тип курсора по
                ; тайлу под мышью: монстр/защищённый тайл → FIGHT (меч); сам герой → HEROES;
                ; гейт замка → ACTION; корпус замка → CASTLE; иначе MOVE/POINTER (path-логика).
                ; Дни пути (1..8) на курсоре — только при ПРЕДРАССЧИТАННОМ пути (Z80 не может
                ; считать путь на каждый hover — аппаратное ограничение, база = без цифры).
                LD   A, (CursorTileX)
                LD   B, A
                LD   A, (CursorTileY)
                LD   C, A
                CALL Hero_FindMonsterAt          ; сам монстр на тайле → меч безусловно
                CP   #FF
                JR   NZ, .fight
                CALL Cursor_TileProtected        ; зона охраны монстра (радиус 1)?
                JR   Z, .noprot
                PUSH BC                          ; охраняемый, но НЕПРОХОДИМЫЙ тайл → POINTER
                CALL Map_IsTilePassable          ;   (ориг.: FIGHT только на passable, :688)
                POP  BC
                JR   NZ, .fight
                JR   .pointer
.noprot:
                LD   A, (HeroTileX)              ; на самом герое → HEROES
                CP   B
                JR   NZ, .nothero
                LD   A, (HeroTileY)
                CP   C
                JR   NZ, .nothero
                LD   A, CURSOR_HEROES_INDEX
                JR   .set
.nothero:       LD   A, B                        ; гейт замка (24,13) → ACTION (вход, свой замок)
                CP   24
                JR   NZ, .ncgate
                LD   A, C
                CP   13
                JR   NZ, .ncgate
                LD   A, CURSOR_ACTION_BASE_INDEX
                JR   .set
.ncgate:        LD   A, B                        ; корпус замка (22..26, 10..12) → CASTLE
                CP   22
                JR   C, .nocastle
                CP   27
                JR   NC, .nocastle
                LD   A, C
                CP   10
                JR   C, .nocastle
                CP   13
                JR   NC, .nocastle
                LD   A, CURSOR_CASTLE_INDEX
                JR   .set
.nocastle:      ; КАК ТОЛЬКО начался расчёт маршрута (PATH_STATE_SEARCH) — СРАЗУ
                ; показываем курсор-лошадку (фидбэк: Z80 считает путь). В оригинале путь
                ; предпросчитан на ховере; у нас Z80 медленный — отклик на момент клика.
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
.fight:         LD   A, CURSOR_FIGHT_BASE_INDEX
.set:           LD   (CursorSpriteIndex), A
                RET
.pointer:       XOR  A
                LD   (CursorSpriteIndex), A
                RET

; B=TileX, C=TileY → NZ если тайл занят ЖИВЫМ монстром или под его защитой (радиус 1,
; fheroes2 Maps::isTileUnderProtection — 8-окрестность монстра). Портит A,DE,HL (B,C целы).
Cursor_TileProtected:
                LD   HL, MapMonsterTab
                LD   D, MAP_MONSTER_COUNT
.tploop:        PUSH DE
                PUSH HL
                LD   DE, 5
                ADD  HL, DE
                LD   A, (HL)                     ; alive
                POP  HL
                OR   A
                JR   Z, .tpnext
                LD   A, (HL)                     ; монстр.x
                SUB  B
                JR   NC, .tpdx
                NEG
.tpdx:          CP   2
                JR   NC, .tpnext                 ; |dx| > 1
                INC  HL
                LD   A, (HL)                     ; монстр.y
                DEC  HL
                SUB  C
                JR   NC, .tpdy
                NEG
.tpdy:          CP   2
                JR   NC, .tpnext                 ; |dy| > 1
                POP  DE                          ; защищён/занят
                LD   A, 1
                OR   A
                RET
.tpnext:        LD   DE, 6
                ADD  HL, DE
                POP  DE
                DEC  D
                JR   NZ, .tploop
                XOR  A
                RET

; Курсор-стрелка скролла на кромке экрана (по оригиналу Interface::GameArea::
; GetScrollCursor). Зоны те же, что у Viewport_AutoEdgeScroll: left x<16, right
; x>=624, top y<16, bottom y>=464. C-флаги краёв: bit0 left, bit1 right, bit2 top,
; bit3 bottom. Возврат CF=1 + CursorSpriteIndex, если мышь в кромке; иначе CF=0.
Cursor_ScrollTheme:
                LD   C, 0
                LD   HL, (CursorPixelX)
                LD   DE, SCROLL_EDGE_BORDER          ; left
                OR   A
                SBC  HL, DE
                JR   NC, .chk_right
                SET  0, C
                JR   .chk_top
.chk_right:     LD   HL, (CursorPixelX)
                LD   DE, CURSOR_MAX_X             ; right
                OR   A
                SBC  HL, DE
                JR   C, .chk_top
                SET  1, C
.chk_top:       LD   HL, (CursorPixelY)
                LD   DE, SCROLL_EDGE_BORDER       ; top
                OR   A
                SBC  HL, DE
                JR   NC, .chk_bottom
                SET  2, C
                JR   .decide
.chk_bottom:    LD   HL, (CursorPixelY)
                LD   DE, CURSOR_MAX_Y             ; bottom
                OR   A
                SBC  HL, DE
                JR   C, .decide
                SET  3, C
.decide:        LD   A, C
                OR   A
                JR   Z, .no_edge                  ; не в кромке → CF=0
                ; flags → offset кадра (порядок ADVMCO 0x20..0x27):
                ; 0 TOP,1 TOPRIGHT,2 RIGHT,3 BOTTOMRIGHT,4 BOTTOM,5 BOTTOMLEFT,6 LEFT,7 TOPLEFT
                CP   %00000100                    ; top
                JR   Z, .o0
                CP   %00000110                    ; top+right
                JR   Z, .o1
                CP   %00000010                    ; right
                JR   Z, .o2
                CP   %00001010                    ; bottom+right
                JR   Z, .o3
                CP   %00001000                    ; bottom
                JR   Z, .o4
                CP   %00001001                    ; bottom+left
                JR   Z, .o5
                CP   %00000001                    ; left
                JR   Z, .o6
                CP   %00000101                    ; top+left
                JR   Z, .o7
.no_edge:       OR   A                            ; CF=0
                RET
.o0:            LD   A, 0
                JR   .set
.o1:            LD   A, 1
                JR   .set
.o2:            LD   A, 2
                JR   .set
.o3:            LD   A, 3
                JR   .set
.o4:            LD   A, 4
                JR   .set
.o5:            LD   A, 5
                JR   .set
.o6:            LD   A, 6
                JR   .set
.o7:            LD   A, 7
.set:           ADD  A, CURSOR_SCROLL_BASE_INDEX
                LD   (CursorSpriteIndex), A
                SCF
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
