; ============================================================================
; Сцена ГОРОДА (cities) — ОВЕРЛЕЙ-страница HMM2_TOWN_PAGE (slot3 #C000), как hiscores.
; Резидентные трамплины (main.asm): Town_Enter_Tramp/Render_Town_Tramp/Town_Update_Tramp.
; Здесь — только тело сцены. ВАЖНО (slot3-edge): отсюда НЕ звать Render_BlackFrame и
; Adventure_Enter напрямую — их зовут резидентные трамплины (иначе оверлей в slot3 выгрузится).
; Loader-трамплины сохраняют/восстанавливают slot3 → Town_LoadFromPak звать loader безопасно.
; Контент города — потоковый HMM2TOWN.PAK с SD (НЕ SPG).
; ============================================================================
                include "generated_town.inc"

TownExitLatch:  DEFB 1            ; 1 на входе (гасит «зажатый» клик-вход), 0 после отпускания ЛКМ
TownHoverIdx:   DEFB 0            ; здание под курсором (1-based из TownHitMap; 0=нет) для hover-имени
TownInfoIdx:    DEFB 0            ; здание для right-click инфо-попапа (1-based; 0=попап скрыт)
TownInfoLineY:  DEFW 0            ; текущий Y строки описания в попапе (vertex 1/16px)

; Курсор → блок 8×8 хит-карты → индекс здания (TownHitMap). OUT: TownHoverIdx. Только в зоне замка (Y<256).
Town_HitTest:
                CALL Input_MouseY                 ; HL = логич. Y
                LD   A, H
                OR   A
                JR   NZ, .none                    ; Y >= 256 → панель, нет hover
                LD   A, L                          ; Y (0..255)
                SRL  A
                SRL  A
                SRL  A                             ; block_y = Y/8 (0..31)
                LD   B, A
                CALL Input_MouseX                 ; HL = X
                SRL  H
                RR   L
                SRL  H
                RR   L
                SRL  H
                RR   L                             ; HL = X/8 (0..79)
                LD   C, L                          ; block_x
                LD   H, 0                           ; offset = block_y*TOWN_HIT_W(80) + block_x
                LD   L, B
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                        ; B*16
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL                        ; B*64
                ADD  HL, DE                        ; B*80
                LD   D, 0
                LD   E, C
                ADD  HL, DE                        ; + block_x
                LD   DE, TownHitMap
                ADD  HL, DE
                LD   A, (HL)
                LD   (TownHoverIdx), A
                RET
.none:          XOR  A
                LD   (TownHoverIdx), A
                RET

; ============================================================================
; Динамический рендер текста (keystone для попапов/найма/диалогов). Глиф = спрайт из
; FontGlyphTab (атлас SMALFONT в RAM_G, белая-альфа), перо двигает Render_DrawSpriteEntry.
; ============================================================================
; Render_DrawString — null-term строка (HL) пером (ResPenX/ResPenY). OUT: HL на терминаторе.
Render_DrawString:
.loop:          LD   A, (HL)
                OR   A
                RET  Z
                PUSH HL
                SUB  32                            ; char → idx глифа
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                        ; idx*5
                LD   DE, FontGlyphTab
                ADD  HL, DE
                CALL Render_DrawSpriteEntry        ; глиф @ перо, ResPenX += w*16
                POP  HL
                INC  HL
                JR   .loop

; Town_StrPixW — ширина строки (HL) в нативных px → BC. HL сохраняется.
Town_StrPixW:
                PUSH HL
                LD   BC, 0
.l:             LD   A, (HL)
                OR   A
                JR   Z, .done
                PUSH HL
                SUB  32
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                        ; idx*5
                LD   DE, FontGlyphTab + 3          ; +3 → поле w
                ADD  HL, DE
                LD   A, (HL)                       ; ширина глифа
                POP  HL
                ADD  A, C
                LD   C, A
                JR   NC, .nocar
                INC  B
.nocar:         INC  HL
                JR   .l
.done:          POP  HL
                RET

; Render_DrawStringCentered — строка (HL) по центру X (экран 1024 → 512), ResPenY задан. OUT: HL на терм.
Render_DrawStringCentered:
                PUSH HL
                CALL Town_StrPixW                  ; BC = ширина
                SRL  B
                RR   C                             ; BC = w/2
                LD   HL, 512
                OR   A
                SBC  HL, BC                        ; 512 − w/2
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                        ; ×16 (vertex)
                LD   (ResPenX), HL
                POP  HL
                JP   Render_DrawString

; Вход в город (вызывается через Town_Enter_Tramp; чёрный кадр уже показан трамплином).
; Стрим композита города в RAM_G[0] + установка состояния. GameMode уже не важен здесь —
; ставит трамплин? нет: ставим тут, пока slot3=town (GameMode — резидентная переменная, ок).
Town_Enter:
                LD   A, GAME_MODE_TOWN
                LD   (GameMode), A
                LD   A, 1
                LD   (TownExitLatch), A           ; клик-вход ещё «зажат» — не выходить сразу
                CALL Town_LoadFromPak             ; стрим HMM2TOWN.PAK → RAM_G[0]
                RET

; Стрим HMM2TOWN.PAK с SD в RAM_G[0]. Имя — общий MenuNameBuf (сцены эксклюзивны).
; Loader_StreamToRamG (резидент slot1) ремапит slot2; town-оверлей в slot3 сохранён.
Town_LoadFromPak:
                LD   HL, TownPakName
                LD   DE, MenuNameBuf
                LD   BC, 13
                LDIR
                CALL Loader_Init
                CALL Loader_Mount
                RET  NC
                LD   HL, MenuNameBuf
                CALL Loader_OpenFile
                RET  NC
                LD   C, RAWPAK_BUF_PAGE           ; пропустить HPAK header (TOWN_BODY_SECTOR)
                LD   HL, 0
                LD   B, TOWN_BODY_SECTOR
                CALL Loader_ReadSectors
                LD   BC, TOWN_PAYLOAD_SECTORS     ; стрим payload → RAM_G[0]
                CALL Loader_StreamToRamG
                RET

; Опрос города: клик ЛКМ (после отпускания входного) → выход. OUT: A=1 если запрошен выход
; (резидентный Town_Update_Tramp по A=1 зовёт Adventure_Enter — slot3-edge).
Town_Update:
                CALL Town_HitTest                 ; здание под курсором → TownHoverIdx (для hover-имени)
                CALL Input_MouseRMB               ; ПКМ зажата → инфо-попап по зданию (faithful Dialog::Message)
                JR   Z, .noinfo
                LD   A, (TownHoverIdx)            ; зажата → попап для здания под курсором (0=фон=нет)
                LD   (TownInfoIdx), A
                JR   .lmb
.noinfo:        XOR  A
                LD   (TownInfoIdx), A             ; отпущена → попап скрыт
.lmb:           CALL Input_MouseLMB               ; NZ = нажато
                JR   NZ, .pressed
                XOR  A
                LD   (TownExitLatch), A            ; отпущено → сбросить latch; A=0 (выхода нет)
                RET
.pressed:       LD   A, (TownExitLatch)
                OR   A
                JR   Z, .check
                XOR  A                             ; клик ещё «зажат» (входной) → A=0
                RET
                ; Выход ТОЛЬКО по кнопке EXIT (castle_dialog.cpp: BUTTON_EXIT_TOWN), не по любому клику.
                ; TREASURY[1] 80×25 @ логич.(553,428) → X∈[553,633), Y∈[428,453).
.check:         CALL Input_MouseX                 ; HL = логич. X
                LD   DE, 553
                OR   A
                SBC  HL, DE
                JP   M, .stay
                JR   C, .stay
                LD   DE, 80
                OR   A
                SBC  HL, DE
                JR   NC, .stay                    ; X >= 633
                CALL Input_MouseY                 ; HL = логич. Y
                LD   DE, 428
                OR   A
                SBC  HL, DE
                JP   M, .stay
                JR   C, .stay
                LD   DE, 25
                OR   A
                SBC  HL, DE
                JR   NC, .stay                    ; Y >= 453
                JR   .exit                        ; в кнопке EXIT → выход
.stay:          XOR  A                            ; клик НЕ по Exit (здание/панель) → остаёмся; A=0
                RET
.exit:          ; Город затёр RAM_G-кэш террейн-композита. Перед возвратом на карту форсируем
                ; полный перезалив: сбросить RuntimeLastOrigin (резидентная RAM, пишем из оверлея)
                ; в #FF → Runtime_UploadStaticIfDirty увидит origin!=last → зальёт грунт заново.
                LD   HL, #FFFF
                LD   (RuntimeLastOriginX), HL      ; X и Y смежны → одной записью
                LD   A, 1
                LD   (TownExitLatch), A            ; зафиксировать; A=1 (выход)
                RET

; Рендер города: новый DL = Town_DL (CLEAR + композит ×1.6) + курсор + swap.
; Зовётся через Render_Town_Tramp. Хелперы (CmdBufCopy/GlobalCursor/SwapFrameDMA) slot3-safe.
Render_Town:
                FT_CMD_Start
                LD   HL, #FFFF                    ; CMD_DLSTART (новый DL, offset 0)
                LD   DE, #FF00
                CALL Render_CmdBufWrite32
                LD   HL, Town_DL
                LD   BC, Town_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (TownInfoIdx)             ; right-click инфо-попап — приоритет над hover-именем
                OR   A
                JP   NZ, .popup
                ; --- hover-имя здания в статус-баре (faithful castle_dialog.cpp) ---
                LD   A, (TownHoverIdx)
                OR   A
                JR   Z, .noname
                LD   HL, Town_Name_Begin_DL
                LD   BC, Town_Name_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (TownHoverIdx)             ; запись = TownBuildingNameTab + (idx-1)*5
                DEC  A
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                        ; (idx-1)*5
                LD   DE, TownBuildingNameTab
                ADD  HL, DE
                PUSH HL                            ; record
                INC  HL
                INC  HL
                INC  HL                            ; &w (+3)
                LD   A, (HL)                       ; ширина имени (native px)
                SRL  A                             ; w/2
                LD   H, 0
                LD   L, A
                LD   DE, 512                        ; центр X экрана 1024 = 512px
                EX   DE, HL
                OR   A
                SBC  HL, DE                        ; 512 − w/2
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                        ; ×16 (vertex)
                LD   (ResPenX), HL
                LD   HL, TOWN_NAME_Y               ; статус-бар Y (vertex)
                LD   (ResPenY), HL
                POP  HL
                CALL Render_DrawSpriteEntry        ; имя SMALFONT native, белая-альфа палитра
                LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
.noname:        CALL Render_GlobalCursor          ; курсор (содержит DISPLAY)
                CALL Render_SwapFrameDMA          ; vsync перед DMA+DLSWAP
                RET

; --- right-click инфо-попап: рамка + заголовок(имя) + описание построчно (faithful Dialog::Message) ---
.popup:         LD   HL, Town_Info_Box_DL
                LD   BC, Town_Info_Box_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, Town_Name_Begin_DL       ; пролог текста: transform native + палитра + BEGIN BITMAPS
                LD   BC, Town_Name_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                ; заголовок = имя здания по центру
                LD   A, (TownInfoIdx)
                DEC  A
                LD   L, A
                LD   H, 0
                ADD  HL, HL                        ; idx*2 (таблица DW)
                LD   DE, TownNameStrTab
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A                           ; HL = &имя (null-term)
                LD   DE, TOWN_INFO_TITLE_Y
                LD   (ResPenY), DE
                CALL Render_DrawStringCentered
                ; описание: блок строк, каждая по центру, Y из TownInfoLineY
                LD   A, (TownInfoIdx)
                DEC  A
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                LD   DE, TownDescTab
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A                           ; HL = &блок строк
                LD   DE, TOWN_INFO_LINE0_Y
                LD   (TownInfoLineY), DE
.descloop:      LD   A, (HL)
                OR   A
                JR   Z, .descdone                  ; пустая строка → конец блока
                LD   DE, (TownInfoLineY)
                LD   (ResPenY), DE
                CALL Render_DrawStringCentered     ; HL → терминатор строки
                INC  HL                             ; HL → начало следующей строки
                PUSH HL
                LD   HL, (TownInfoLineY)
                LD   DE, TOWN_INFO_LINE_H
                ADD  HL, DE
                LD   (TownInfoLineY), HL
                POP  HL
                JR   .descloop
.descdone:      LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                JR   .noname

TOWN_NAME_Y     EQU 745 * 16       ; статус-бар (экран y≈745, в нижней панели), vertex 1/16px
