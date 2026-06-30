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
TownRecruitIdx: DEFB 255          ; диалог найма: 0..5 монстр / 255 = закрыт (Dialog::RecruitMonster)
TownRecruitCount: DEFW 0          ; текущий счётчик найма (1..available); = available при открытии
RecMX:          DEFW 0            ; кэш мыши X для хит-теста кнопок найма
RecMY:          DEFW 0
RecNumVal:      DEFW 0            ; рабочее для Render_DrawNum
RecNumStarted:  DEFB 0
; --- Состояние королевства (3c, персистентное между визитами; init один раз) ---
TownStateInit:  DEFB 0            ; 0 = ещё не инициализировано
KingdomGold:    DEFW 0            ; казна (золото)
DwellAvail:     DEFW 0,0,0,0,0,0  ; доступно в жилищах [recruit idx] (декремент при найме)
GarCount:       DEFW 0,0,0,0,0,0  ; армия гарнизона по [recruit idx] (JoinTroop: +count при найме)
GarSlotType:    DEFB 255,255,255  ; динам.слоты армбара 2,3,4 → recruit idx нового типа (255=пусто)
GarAnchorX:     DEFW 0            ; рабочее: X-якорь ячейки для Garrison_DrawMonh

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

; Recr_StrPtr — IN: A=idx, DE=база DW-таблицы → HL = строка table[idx]. Портит AF.
Recr_StrPtr:    ADD  A, A                          ; idx*2
                LD   L, A
                LD   H, 0
                ADD  HL, DE                        ; &table[idx]
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A                           ; HL = указатель строки
                RET

; Render_DrawNum — HL = беззнаковое число → десятично глифами FontGlyphTab (idx16='0') пером. Вед.нули скрыты.
RecNumDivs:     DEFW 10000, 1000, 100, 10, 1, 0
Render_DrawNum:
                LD   (RecNumVal), HL
                XOR  A
                LD   (RecNumStarted), A
                LD   IX, RecNumDivs
.dl:            LD   E, (IX+0)
                LD   D, (IX+1)
                INC  IX
                INC  IX
                LD   A, D
                OR   E
                RET  Z                             ; делитель 0 → конец
                LD   HL, (RecNumVal)
                LD   B, 0
.sub:           OR   A
                SBC  HL, DE
                JR   C, .done
                INC  B
                JR   .sub
.done:          ADD  HL, DE                        ; восстановить остаток
                LD   (RecNumVal), HL
                LD   A, B
                OR   A
                JR   NZ, .show
                LD   A, (RecNumStarted)
                OR   A
                JR   NZ, .show
                LD   A, E                          ; цифра 0, не начато: пропуск кроме единиц (делитель==1)
                DEC  A
                OR   D
                JR   NZ, .dl
.show:          LD   A, 1
                LD   (RecNumStarted), A
                LD   A, B
                ADD  A, 16                         ; '0' = FontGlyphTab idx 16
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                        ; idx*5
                LD   DE, FontGlyphTab
                ADD  HL, DE
                PUSH IX
                CALL Render_DrawSpriteEntry
                POP  IX
                JR   .dl

; Town_Box — IX=&rect{x0,x1,y0,y1 words}. OUT: Z=курсор внутри (RecMX/RecMY).
Town_Box:       LD   L, (IX+0)
                LD   H, (IX+1)
                LD   DE, (RecMX)
                EX   DE, HL
                OR   A
                SBC  HL, DE                        ; MX-x0
                JR   C, .no
                LD   L, (IX+2)
                LD   H, (IX+3)
                LD   DE, (RecMX)
                EX   DE, HL
                OR   A
                SBC  HL, DE                        ; MX-x1
                JR   NC, .no
                LD   L, (IX+4)
                LD   H, (IX+5)
                LD   DE, (RecMY)
                EX   DE, HL
                OR   A
                SBC  HL, DE
                JR   C, .no
                LD   L, (IX+6)
                LD   H, (IX+7)
                LD   DE, (RecMY)
                EX   DE, HL
                OR   A
                SBC  HL, DE
                JR   NC, .no
                XOR  A
                RET                                ; внутри
.no:            OR   1
                RET

; Прямоугольники кнопок (логич. 640×480, измерены по реальному кадру оригинала RECRBKG ×1.6).
RecBoxUp:       DEFW 344, 402, 246, 257          ; стрелка вверх (верх ромба)
RecBoxDn:       DEFW 344, 402, 257, 267          ; стрелка вниз (низ ромба)
RecBoxMax:      DEFW 414, 470, 244, 266          ; MAX
RecBoxOk:       DEFW 214, 331, 328, 359          ; OKAY
RecBoxCancel:   DEFW 367, 459, 336, 359          ; CANCEL

; Town_RecAvail — OUT: DE = текущее доступно для TownRecruitIdx (DwellAvail, динамич.). Портит HL,AF.
Town_RecAvail:  LD   A, (TownRecruitIdx)
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, DwellAvail
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                RET

; Town_RecTotal — OUT: HL = TownRecruitCount × цена-за-1 (RecruitCostNum[idx]). Портит все.
Town_RecTotal:  LD   A, (TownRecruitIdx)
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, RecruitCostNum
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = цена-за-1
                LD   BC, (TownRecruitCount)
                LD   HL, 0
.m:             LD   A, B
                OR   C
                RET  Z
                ADD  HL, DE
                DEC  BC
                JR   .m

; Garrison_DrawMonh — A=recruit type, (GarAnchorX)=X-центр ячейки (vertex). MONH bottom-anchored. Портит всё.
Garrison_DrawMonh:
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                        ; type*5
                LD   DE, RecruitMonhTab
                ADD  HL, DE                        ; &record
                PUSH HL
                INC  HL
                INC  HL
                INC  HL
                LD   A, (HL)                        ; w
                PUSH AF
                INC  HL
                LD   A, (HL)                        ; h
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                         ; h*16
                EX   DE, HL
                LD   HL, GAR_ANCHOR_Y
                OR   A
                SBC  HL, DE                         ; y = низ ячейки − h*16
                LD   (ResPenY), HL
                POP  AF                             ; w
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                         ; w*8 = (w/2)*16
                EX   DE, HL
                LD   HL, (GarAnchorX)
                OR   A
                SBC  HL, DE                         ; x = центр − w*8
                LD   (ResPenX), HL
                POP  HL                             ; record
                JP   Render_DrawSpriteEntry

; Garrison_DrawCount — A=recruit type, HL=X-позиция счётчика (vertex). Рисует GarCount[type].
Garrison_DrawCount:
                LD   (ResPenX), HL
                LD   HL, GAR_CNT_VY
                LD   (ResPenY), HL
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, GarCount
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A                           ; HL = GarCount[type]
                JP   Render_DrawNum

; Вход в город (вызывается через Town_Enter_Tramp; чёрный кадр уже показан трамплином).
; Стрим композита города в RAM_G[0] + установка состояния. GameMode уже не важен здесь —
; ставит трамплин? нет: ставим тут, пока slot3=town (GameMode — резидентная переменная, ок).
Town_Enter:
                LD   A, GAME_MODE_TOWN
                LD   (GameMode), A
                LD   A, 1
                LD   (TownExitLatch), A           ; клик-вход ещё «зажат» — не выходить сразу
                XOR  A
                LD   (TownInfoIdx), A             ; инфо-попап закрыт
                LD   A, 255
                LD   (TownRecruitIdx), A          ; диалог найма закрыт
                ; --- состояние королевства: init один раз (персистентно между визитами) ---
                LD   A, (TownStateInit)
                OR   A
                JR   NZ, .stateok
                LD   HL, START_GOLD
                LD   (KingdomGold), HL
                LD   HL, RecruitAvailNum          ; копировать базовое доступное → DwellAvail (6×DW)
                LD   DE, DwellAvail
                LD   BC, 12
                LDIR
                LD   HL, GarCountInit             ; начальная армия → GarCount (Peasant40, Archer4)
                LD   DE, GarCount
                LD   BC, 12
                LDIR
                LD   A, 1
                LD   (TownStateInit), A
.stateok:       CALL Town_LoadFromPak             ; стрим HMM2TOWN.PAK → RAM_G[0]
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
                ; --- Диалог найма открыт → МОДАЛЬНО: клик ЛКМ закрывает, прочее игнор ---
                LD   A, (TownRecruitIdx)
                INC  A                             ; 255→0 (Z = найма нет)
                JP   Z, .norecruit
                CALL Input_MouseLMB
                JR   NZ, .rec_pressed
                XOR  A
                LD   (TownExitLatch), A            ; отпущено → сбросить latch; A=0
                RET
.rec_pressed:   LD   A, (TownExitLatch)
                OR   A
                JR   Z, .rec_act
                XOR  A                             ; открывающий/повторный клик зажат → игнор
                RET
.rec_act:       ; ЛКМ нажата, latch=0 → ОДНО действие на клик (faithful кнопки диалога найма)
                CALL Input_MouseX
                LD   (RecMX), HL
                CALL Input_MouseY
                LD   (RecMY), HL
                LD   A, 1
                LD   (TownExitLatch), A            ; залатчить (одно действие)
                LD   IX, RecBoxOk
                CALL Town_Box
                JR   Z, .rec_ok                    ; OKAY → реальный найм (Castle::RecruitMonster)
                LD   IX, RecBoxCancel
                CALL Town_Box
                JR   Z, .rec_doclose               ; CANCEL → закрыть без найма
                LD   IX, RecBoxMax
                CALL Town_Box
                JP   Z, .rec_max
                LD   IX, RecBoxUp
                CALL Town_Box
                JP   Z, .rec_up
                LD   IX, RecBoxDn
                CALL Town_Box
                JP   Z, .rec_dn
                XOR  A                             ; вне кнопок → ничего
                RET
.rec_doclose:   LD   A, 255
                LD   (TownRecruitIdx), A
                XOR  A
                RET
.rec_ok:        ; найм по оригиналу: проверить казну → списать золото → DwellAvail[idx] -= count → закрыть
                CALL Town_RecTotal                 ; HL = count × цена-за-1
                EX   DE, HL                         ; DE = total
                LD   HL, (KingdomGold)
                OR   A
                SBC  HL, DE                         ; gold - total
                JR   C, .rec_doclose               ; не хватает золота (AllowPayment=false) → без найма
                LD   (KingdomGold), HL              ; OddFundsResource: списать
                CALL Town_RecAvail                 ; DE = текущее доступно
                LD   HL, (TownRecruitCount)
                EX   DE, HL                         ; HL=avail, DE=count
                OR   A
                SBC  HL, DE                         ; avail - count
                EX   DE, HL                         ; DE = новое доступно
                LD   A, (TownRecruitIdx)
                ADD  A, A
                LD   L, A
                LD   H, 0
                PUSH DE
                LD   DE, DwellAvail
                ADD  HL, DE                         ; &DwellAvail[idx]
                POP  DE
                LD   (HL), E
                INC  HL
                LD   (HL), D                         ; _dwelling[idx] -= count
                ; JoinTroop: GarCount[idx] += count (тот же recruit idx → тот же слот армии)
                LD   A, (TownRecruitIdx)
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, GarCount
                ADD  HL, DE                         ; &GarCount[idx]
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                         ; DE = GarCount[idx]
                LD   HL, (TownRecruitCount)
                ADD  HL, DE                         ; + count
                EX   DE, HL                         ; DE = новое
                LD   A, (TownRecruitIdx)
                ADD  A, A
                LD   L, A
                LD   H, 0
                PUSH DE
                LD   DE, GarCount
                ADD  HL, DE
                POP  DE
                LD   (HL), E
                INC  HL
                LD   (HL), D                         ; GarCount[idx] = старое + count
                ; новый тип (idx>=2) → назначить динам.слот армбара, если ещё не назначен
                LD   A, (TownRecruitIdx)
                CP   2
                JR   C, .rec_doclose               ; Peasant/Archer = слоты 0,1 (запечены)
                LD   C, A                            ; C = idx
                LD   HL, GarSlotType                ; уже назначен этому типу?
                LD   B, 3
.rec_findasn:   LD   A, (HL)
                CP   C
                JR   Z, .rec_doclose               ; да → ничего
                INC  HL
                DJNZ .rec_findasn
                LD   HL, GarSlotType               ; найти свободный (255) слот
                LD   B, 3
.rec_findfree:  LD   A, (HL)
                CP   255
                JR   Z, .rec_assign
                INC  HL
                DJNZ .rec_findfree
                JR   .rec_doclose                 ; нет места (армия полна) — тип не показать
.rec_assign:    LD   (HL), C                       ; GarSlotType[слот] = idx
                JR   .rec_doclose
.rec_max:       CALL Town_RecAvail                 ; счётчик = доступно
                LD   (TownRecruitCount), DE
                XOR  A
                RET
.rec_up:        CALL Town_RecAvail                 ; count++ если < доступно
                LD   HL, (TownRecruitCount)
                OR   A
                SBC  HL, DE
                JR   NC, .rec_noop                 ; count >= avail
                LD   HL, (TownRecruitCount)
                INC  HL
                LD   (TownRecruitCount), HL
                XOR  A
                RET
.rec_dn:        LD   HL, (TownRecruitCount)        ; count-- если > 1
                LD   DE, 1
                OR   A
                SBC  HL, DE
                JR   Z, .rec_noop                  ; count==1
                JR   C, .rec_noop                  ; count==0
                LD   HL, (TownRecruitCount)
                DEC  HL
                LD   (TownRecruitCount), HL
.rec_noop:      XOR  A
                RET
.norecruit:     CALL Town_HitTest                 ; здание под курсором → TownHoverIdx (для hover-имени)
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
                ; Клик по ЖИЛИЩУ → открыть диалог найма (Dialog::RecruitMonster). TownDwellingMap[idx-1].
.check:         LD   A, (TownHoverIdx)
                OR   A
                JR   Z, .exitbtn                  ; не здание (панель) → проверить кнопку EXIT
                DEC  A
                LD   L, A
                LD   H, 0
                LD   DE, TownDwellingMap
                ADD  HL, DE
                LD   A, (HL)                       ; recruit idx (0..5) или 255
                CP   255
                JR   Z, .exitbtn                  ; здание не жилище → проверить EXIT (даст .stay)
                LD   (TownRecruitIdx), A            ; открыть диалог найма для монстра
                CALL Town_RecAvail                 ; счётчик = доступно при открытии (как fheroes2 result=max)
                LD   (TownRecruitCount), DE
                LD   A, 1
                LD   (TownExitLatch), A            ; залатчить открывающий клик
                XOR  A
                RET
                ; Выход ТОЛЬКО по кнопке EXIT (castle_dialog.cpp: BUTTON_EXIT_TOWN), не по любому клику.
                ; TREASURY[1] 80×25 @ логич.(553,428) → X∈[553,633), Y∈[428,453).
.exitbtn:       CALL Input_MouseX                 ; HL = логич. X
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
                ; --- MONH новых типов в динам.слотах 2-4 (прозрачная палитра) ---
                LD   HL, Recruit_Mon_Begin_DL
                LD   BC, Recruit_Mon_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (GarSlotType + 0)
                CP   255
                JR   Z, .gmon_c
                LD   HL, GAR_ANCHOR_X2
                LD   (GarAnchorX), HL
                CALL Garrison_DrawMonh
.gmon_c:        LD   A, (GarSlotType + 1)
                CP   255
                JR   Z, .gmon_d
                LD   HL, GAR_ANCHOR_X3
                LD   (GarAnchorX), HL
                CALL Garrison_DrawMonh
.gmon_d:        LD   A, (GarSlotType + 2)
                CP   255
                JR   Z, .gmon_e
                LD   HL, GAR_ANCHOR_X4
                LD   (GarAnchorX), HL
                CALL Garrison_DrawMonh
.gmon_e:        LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                ; --- живое золото на панели (всегда; число не запечено) ---
                LD   HL, Town_Name_Begin_DL
                LD   BC, Town_Name_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, GOLD_PANEL_VX
                LD   (ResPenX), HL
                LD   HL, GOLD_PANEL_VY
                LD   (ResPenY), HL
                LD   HL, (KingdomGold)
                CALL Render_DrawNum
                LD   HL, GAR_CNT0_VX               ; живой счётчик гарнизона: слот0 Peasant
                LD   (ResPenX), HL
                LD   HL, GAR_CNT_VY
                LD   (ResPenY), HL
                LD   HL, (GarCount)
                CALL Render_DrawNum
                LD   HL, GAR_CNT1_VX               ; слот1 Archer
                LD   (ResPenX), HL
                LD   HL, GAR_CNT_VY
                LD   (ResPenY), HL
                LD   HL, (GarCount + 2)
                CALL Render_DrawNum
                LD   A, (GarSlotType + 0)          ; счётчики новых типов (динам.слоты 2-4)
                CP   255
                JR   Z, .gcnt_c
                LD   HL, GAR_CNT2_VX
                CALL Garrison_DrawCount
.gcnt_c:        LD   A, (GarSlotType + 1)
                CP   255
                JR   Z, .gcnt_d
                LD   HL, GAR_CNT3_VX
                CALL Garrison_DrawCount
.gcnt_d:        LD   A, (GarSlotType + 2)
                CP   255
                JR   Z, .gcnt_e
                LD   HL, GAR_CNT4_VX
                CALL Garrison_DrawCount
.gcnt_e:        LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (TownRecruitIdx)          ; диалог найма открыт → его рисуем (приоритет)
                INC  A
                JP   NZ, .recruit
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

; --- диалог найма: окно RECRBKG ×1.6 + имя/доступно/цена/счётчик (Dialog::RecruitMonster) ---
.recruit:       LD   HL, Recruit_Win_DL
                LD   BC, Recruit_Win_DL_SIZE
                CALL Render_CmdBufCopy
                ; --- спрайт монстра (боевой статик ×1.6, прозрачная палитра idx0) ---
                LD   HL, Recruit_Mon_Begin_DL
                LD   BC, Recruit_Mon_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (TownRecruitIdx)           ; позиция = RecruitMonPosTab + idx*4
                ADD  A, A
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, RecruitMonPosTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   (ResPenX), DE                 ; X спрайта (vertex)
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (ResPenY), DE                 ; Y спрайта (vertex)
                LD   A, (TownRecruitIdx)           ; запись = RecruitMonSprTab + idx*5
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE
                LD   DE, RecruitMonSprTab
                ADD  HL, DE
                CALL Render_DrawSpriteEntry        ; спрайт монстра @ перо
                LD   HL, RECR_GOLD_VX              ; иконка золота (цена-за-1) в рамке «Cost per troop»
                LD   (ResPenX), HL
                LD   HL, RECR_GOLD_VY
                LD   (ResPenY), HL
                LD   HL, RecruitGoldRec
                CALL Render_DrawSpriteEntry        ; та же прозрачная палитра, что у монстра
                LD   HL, RECR_TOTGOLD_VX           ; иконка золота ИТОГА под полем (по оригиналу стр.151)
                LD   (ResPenX), HL
                LD   HL, RECR_TOTGOLD_VY
                LD   (ResPenY), HL
                LD   HL, RecruitGoldRec
                CALL Render_DrawSpriteEntry
                LD   HL, Town_Name_End_DL          ; закрыть BITMAPS монстра+иконки
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, Town_Name_Begin_DL       ; пролог текста (native + палитра + BEGIN BITMAPS)
                LD   BC, Town_Name_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, #04FF                    ; COLOR_RGB 255,255,0 — имя ЖЁЛТОЕ (faithful normalYellow)
                LD   DE, #FF00
                CALL Render_CmdBufWrite32
                LD   A, (TownRecruitIdx)           ; имя монстра
                LD   DE, RecruitNameTab
                CALL Recr_StrPtr
                LD   DE, RECR_NAME_VY
                LD   (ResPenY), DE
                CALL Render_DrawStringCentered
                LD   HL, #04FF                    ; COLOR_RGB 255,255,255 — остальной текст белый
                LD   DE, #FFFF
                CALL Render_CmdBufWrite32
                LD   HL, RECR_AVAIL_VY             ; "Available: N" ПОД спрайтом (центр x+64, y+120)
                LD   (ResPenY), HL
                LD   HL, 310 * 16                  ; ≈центр 357 для "Available: " (лево-выр.)
                LD   (ResPenX), HL
                LD   HL, RecruitAvailPfx
                CALL Render_DrawString
                CALL Town_RecAvail                 ; DE = доступно
                EX   DE, HL
                CALL Render_DrawNum
                LD   HL, RECR_NUMBUY_VY            ; "Number to buy:" (по оригиналу стр.218, был пропущен)
                LD   (ResPenY), HL
                LD   HL, 314 * 16
                LD   (ResPenX), HL
                LD   HL, RecruitNumBuy
                CALL Render_DrawString
                LD   HL, RECR_COST_VY             ; итог = ЧИСЛО у иконки золота (НЕ «Cost: N gold» текстом)
                LD   (ResPenY), HL
                LD   HL, 465 * 16
                LD   (ResPenX), HL
                CALL Town_RecTotal                 ; HL = TownRecruitCount × цена-за-1
                CALL Render_DrawNum
                LD   HL, RECR_COUNT_VY             ; счётчик (динамический TownRecruitCount)
                LD   (ResPenY), HL
                LD   HL, 505 * 16
                LD   (ResPenX), HL
                LD   HL, (TownRecruitCount)
                CALL Render_DrawNum
                LD   HL, RECR_PT_VX               ; число цены-за-1 под иконкой золота (лево-выр.)
                LD   (ResPenX), HL
                LD   HL, RECR_PT_VY
                LD   (ResPenY), HL
                LD   A, (TownRecruitIdx)
                LD   DE, RecruitPerTroopTab
                CALL Recr_StrPtr
                CALL Render_DrawString
                LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                JP   .noname

TOWN_NAME_Y     EQU 745 * 16       ; статус-бар (экран y≈745, в нижней панели), vertex 1/16px
