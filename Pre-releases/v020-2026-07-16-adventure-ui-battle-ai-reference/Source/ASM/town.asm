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
TownConstructOpen: DEFB 0         ; окно строительства замка открыто (1) / закрыто (0) (Castle::_openConstructionDialog)
TownTavernOpen:  DEFB 0           ; окно таверны открыто (модалка с OKAY; Castle::_openTavern)
TownTavernRumor: DEFB 0           ; слух недели 0..6 на момент открытия ((day-1)/7 mod 7)
TownMarketOpen:  DEFB 0           ; окно рынка открыто (Dialog::Marketplace)
TownWellOpen:    DEFB 0           ; окно колодца открыто (Castle::_openWell)
ConstructLoaded: DEFB 0           ; что в construct-области: 0=окно строительства, 1=WELL
MarketFrom:      DEFB #FF         ; выбранный ресурс-источник 0..6 (#FF=нет); 6=gold
MarketTo:        DEFB #FF         ; выбранный ресурс-цель
MarketQty:       DEFW 0           ; количество к обмену (buy; для to=gold — sell)
MarketMax:       DEFW 0           ; максимум для текущей пары
TownRecrLoaded:  DEFB 0           ; что в области найма: 0=RECRBKG, 1=ассеты рынка
ConstructBuiltSlot: DEFB 0        ; рабочий индекс слота при отрисовке галочек
TownRecruitCount: DEFW 0          ; текущий счётчик найма (1..available); = available при открытии
RecMX:          DEFW 0            ; кэш мыши X для хит-теста кнопок найма
RecMY:          DEFW 0
RecNumVal:      DEFW 0            ; рабочее для Render_DrawNum
RecNumStarted:  DEFB 0
RecNumW:        DEFW 0            ; аккумулятор ширины числа (Render_NumPixW)
RecTmpW:        DEFW 0            ; временная ширина (центрирование "Available: N")
RecTmpN:        DEFW 0            ; временное число
CurFontTab:     DEFW FontGlyphTab  ; текущий атлас глифов (Render_DrawString/Town_StrPixW); переключается на BigFontGlyphTab для заголовка
; ★ЕДИНЫЙ ВЕКТОР ФОНДОВ (Kingdom::AllowPayment/OddFundsResource): 7×DW ПОДРЯД в порядке
; gold,wood,mercury,ore,sulfur,crystal,gems — как ConstructCostFull (сравнение/списание циклом).
; КАЗНА ТЕПЕРЬ В РЕЗИДЕНТЕ (KingdomFunds, main.asm) — общая с панелью карты и доходом
; End Turn, переживает рестрим оверлея.
KingdomGold     EQU KingdomFunds        ; казна (золото)
KingdomRes6     EQU KingdomFunds + 2    ; wood,mercury,ore,sulfur,crystal,gems
; --- ПЕРС-БЛОК ГОРОДА (68Б ПОДРЯД = GSTATE_LEN): сохраняется в #91 через TownStateBuf при
; выходе (Town_SaveState), восстанавливается при входе (GState_Fetch) — оверлей города
; рестримится каждый вход, иначе постройки/жилища/гарнизон терялись бы. ---
TownPersist:
TownStateInit:  DEFB 0            ; 0 = ещё не инициализировано
DwellAvail:     DEFW 0,0,0,0,0,0  ; доступно в жилищах [recruit idx] (декремент при найме)
BuildToday:     DEFB 1            ; ALLOW_TO_BUILD_TODAY (сброс при постройке, взвод новым днём)
TownLastDay:    DEFW 0            ; последний обработанный DayCounter (догон экономики)
WeekPos:        DEFB 0            ; день недели 0..6 (7-й — рост жилищ, ActionNewWeek)
BuiltMask:      DEFB 0,0,0        ; рабочая 18-бит маска построенных (бит i = слот i)
BuiltRuntime:   DEFB 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0  ; [18] построен ли слот (0/1)
ArmyType:       DEFB 0,0,0,0,0, 0,0,0,0,0   ; слот-модель армии: 0=пусто, 1-6=recruit idx+1
ArmyCnt:        DEFW 0,0,0,0,0, 0,0,0,0,0
TOWN_PERSIST_LEN EQU $ - TownPersist
                ASSERT TOWN_PERSIST_LEN == GSTATE_LEN
                ASSERT BuiltRuntime + CONSTRUCT_STATUE_SLOT - TownPersist == GSTATE_OFS_STATUE
; --- Строительство по оригиналу (Castle::BuyBuilding/CheckBuyBuilding) ---
CurStatus:      DEFB 255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255
                                  ; [18] кэш статуса слота: 0=ALLOW 1=BUILT 2=REQUIRES 3=LACK
                                  ;      4=NOT_TODAY 5=DISABLE; 255 = не отрисован (патчить)
CalcSlot:       DEFB 0            ; рабочий индекс пересчёта статусов
CalcStat:       DEFB 0            ; рабочий статус слота
; Единая слот-модель армии (ArmyBar castle_dialog.cpp): 10 слотов, 0-4=гарнизон(top), 5-9=герой(bottom).
; Слот: тип (0=пусто, 1-6=recruit idx+1) + счётчик. Гарнизон стартует ПУСТ (customDefenders=0),
; стартовая армия у героя (Army::Reset defaultArmy: Peasant 30-50 + Archer 3-5).
; ArmyType/ArmyCnt — в ПЕРС-БЛОКЕ TownPersist (выше).
ArmyDrawSlot:   DEFB 0            ; рабочий индекс слота при отрисовке армбаров
GarAnchorX:     DEFW 0            ; рабочий X-центр ячейки для Garrison_DrawMonh
GarAnchorY:     DEFW 0            ; рабочий Y-низ ячейки для Garrison_DrawMonh
ArmySel:        DEFB 255          ; выбранный слот армбара (0-9) для переноса / 255 = нет (ArmyBar isSelected)
ArmySrcSlot:    DEFB 0            ; рабочее: слот-источник переноса
ArmyDstSlot:    DEFB 0            ; рабочее: слот-приёмник переноса

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
                LD   DE, GDTownHitMap              ; хит-карта на #91 (вынос из оверлея 16К)
                ADD  HL, DE
                CALL GData_ReadByte                ; A = байт с data-страницы (резидент)
                OR   A
                JR   Z, .runtime                   ; фон в запечённой карте → runtime-постройки (bbox)
                LD   (TownHoverIdx), A
                RET
.none:          XOR  A
                LD   (TownHoverIdx), A
                RET
; Runtime-построенные здания не в запечённой TownHitMap — ловим их bbox-ами (PanoBBox*)
; в ОБРАТНОМ z-порядке (передний план первым). Индекс здания = z+1 (как в hitmap).
.runtime:       LD   B, 18                         ; z: 18..0
.rt:            LD   A, B
                LD   L, A                          ; слот стройки этого z
                LD   H, 0
                LD   DE, PanoToSlot
                ADD  HL, DE
                LD   A, (HL)
                CP   255
                JR   Z, .rtnext
                LD   C, A
                LD   L, A                          ; построен в рантайме и НЕ запечён?
                LD   H, 0
                LD   DE, BuiltRuntime
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .rtnext
                LD   A, C
                LD   L, A
                LD   H, 0
                LD   DE, ConstructInitBuilt
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   NZ, .rtnext                   ; запечённые ловит hitmap
                ; bbox-проверка: PanoBBoxX0[z] <= MX < X1, Y0 <= MY < Y1
                PUSH BC
                LD   A, B
                ADD  A, A
                LD   L, A
                LD   H, 0
                PUSH HL
                LD   DE, PanoBBoxX0
                ADD  HL, DE
                CALL Town_BBoxLoad                 ; DE = значение таблицы
                CALL Input_MouseX
                OR   A
                SBC  HL, DE
                JP   M, .rtpop                     ; MX < X0
                POP  HL
                PUSH HL
                LD   DE, PanoBBoxX1
                ADD  HL, DE
                CALL Town_BBoxLoad
                CALL Input_MouseX
                OR   A
                SBC  HL, DE
                JP   P, .rtpop                     ; MX >= X1
                POP  HL
                PUSH HL
                LD   DE, PanoBBoxY0
                ADD  HL, DE
                CALL Town_BBoxLoad
                CALL Input_MouseY
                OR   A
                SBC  HL, DE
                JP   M, .rtpop                     ; MY < Y0
                POP  HL
                PUSH HL
                LD   DE, PanoBBoxY1
                ADD  HL, DE
                CALL Town_BBoxLoad
                CALL Input_MouseY
                OR   A
                SBC  HL, DE
                JP   P, .rtpop                     ; MY >= Y1
                POP  HL
                POP  BC
                LD   A, B                          ; попадание: индекс = z+1
                INC  A
                LD   (TownHoverIdx), A
                RET
.rtpop:         POP  HL
                POP  BC
.rtnext:        LD   A, B
                OR   A
                JP   Z, .none
                DEC  B
                JP   .rt

; Town_BBoxLoad — DE = слово по (HL) (bbox-таблица). Портит A.
Town_BBoxLoad:  LD   A, (HL)
                INC  HL
                LD   D, (HL)
                LD   E, A
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
                LD   DE, (CurFontTab)
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
                LD   DE, (CurFontTab)
                ADD  HL, DE
                INC  HL
                INC  HL
                INC  HL                            ; +3 → поле w
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

; Render_DrawStrCenteredAt — строка (HL) по центру DE (экран px), ResPenY задан. OUT: HL на терм.
Render_DrawStrCenteredAt:
                PUSH HL
                PUSH DE
                CALL Town_StrPixW                  ; BC = ширина
                SRL  B
                RR   C                             ; BC = w/2
                POP  HL                            ; HL = центр (px)
                OR   A
                SBC  HL, BC                        ; центр − w/2
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                        ; ×16 (vertex)
                LD   (ResPenX), HL
                POP  HL
                JP   Render_DrawString
; Render_DrawStringCentered — строка (HL) по центру экрана (1024 → 512).
Render_DrawStringCentered:
                LD   DE, 512
                JR   Render_DrawStrCenteredAt

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
                ADD  A, 16                         ; '0' = глиф idx 16 (CurFontTab)
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                        ; idx*5
                LD   DE, (CurFontTab)              ; шрифт числа = текущий (SMALFONT / BigFont для счётчика)
                ADD  HL, DE
                PUSH IX
                CALL Render_DrawSpriteEntry
                POP  IX
                JR   .dl

; Render_NumPixW — HL = беззнаковое число → BC = ширина в экранных px (CurFontTab, вед.нули скрыты как
; в Render_DrawNum). Ничего не рисует. Портит AF/DE/HL/IX; результат в BC.
Render_NumPixW:
                LD   (RecNumVal), HL
                XOR  A
                LD   (RecNumStarted), A
                LD   HL, 0
                LD   (RecNumW), HL
                LD   IX, RecNumDivs
.wl:            LD   E, (IX+0)
                LD   D, (IX+1)
                INC  IX
                INC  IX
                LD   A, D
                OR   E
                JR   Z, .wdone                     ; делитель 0 → конец
                LD   HL, (RecNumVal)
                LD   B, 0
.wsub:          OR   A
                SBC  HL, DE
                JR   C, .wsd
                INC  B
                JR   .wsub
.wsd:           ADD  HL, DE
                LD   (RecNumVal), HL
                LD   A, B
                OR   A
                JR   NZ, .wshow
                LD   A, (RecNumStarted)
                OR   A
                JR   NZ, .wshow
                LD   A, E                          ; цифра 0 не начато: пропуск кроме единиц
                DEC  A
                OR   D
                JR   NZ, .wl
.wshow:         LD   A, 1
                LD   (RecNumStarted), A
                LD   A, B                          ; цифра B → глиф idx 16+B, поле w (+3)
                ADD  A, 16
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                        ; idx*5
                LD   DE, (CurFontTab)
                ADD  HL, DE
                INC  HL
                INC  HL
                INC  HL                            ; +3 → ширина глифа
                LD   A, (HL)
                LD   HL, (RecNumW)
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                LD   (RecNumW), HL
                JR   .wl
.wdone:         LD   BC, (RecNumW)
                RET

; Render_DrawNumCentered — HL=число, DE=центр X (экран px), ResPenY задан. Центрирует по ширине.
Render_DrawNumCentered:
                PUSH HL
                PUSH DE
                CALL Render_NumPixW                ; BC = ширина
                SRL  B
                RR   C                             ; BC = w/2
                POP  HL                            ; HL = центр
                OR   A
                SBC  HL, BC                        ; центр − w/2
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                        ; ×16
                LD   (ResPenX), HL
                POP  HL                            ; число
                JP   Render_DrawNum

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
                LD   HL, (GarAnchorY)
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

; Army_PlateLoop — плита STRIP[4] (Knight, горы) под каждым ЗАНЯТЫМ слотом (0-9) ДО MONH-портрета
; (renderMonsterFrame, ui_monster.cpp: STRIP[4] под монстром). Каждый блок ArmyPlateDL самодостаточен
; (opaque палитра ×1.6), копируется по ArmyPlateDLTab[slot]. Пустой слот → плита не рисуется (STRIP[2]
; уже в композите). Портит всё (после — MONH-пролог сбрасывает transform/палитру).
Army_PlateLoop: XOR  A
                LD   (ArmyDrawSlot), A
.apl:           LD   A, (ArmyDrawSlot)
                CP   10
                RET  Z
                LD   L, A
                LD   H, 0
                LD   DE, ArmyType
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .apl_next                   ; пусто → нет плиты
                LD   A, (ArmyDrawSlot)              ; запись = ArmyPlateDLTab + slot*4
                ADD  A, A
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, ArmyPlateDLTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL                             ; DE = addr блока
                LD   C, (HL)
                INC  HL
                LD   B, (HL)                        ; BC = size
                EX   DE, HL                          ; HL = addr
                CALL Render_CmdBufCopy
.apl_next:      LD   A, (ArmyDrawSlot)
                INC  A
                LD   (ArmyDrawSlot), A
                JR   .apl

; Army_MonhLoop — портреты MONH всех непустых слотов (0-9) в позициях ArmyMonhX/Y[slot].
; Пролог MONH-спрайта (Recruit_Mon_Begin_DL) должен быть уже в DL. Портит всё.
Army_MonhLoop:  XOR  A
                LD   (ArmyDrawSlot), A
.aml:           LD   A, (ArmyDrawSlot)
                CP   10
                RET  Z
                LD   L, A                           ; тип слота
                LD   H, 0
                LD   DE, ArmyType
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .aml_next                   ; пусто → пропуск
                DEC  A                               ; recruit idx (тип-1)
                PUSH AF
                LD   A, (ArmyDrawSlot)              ; GarAnchorX = ArmyMonhX[slot]
                ADD  A, A
                LD   L, A
                LD   H, 0
                PUSH HL
                LD   DE, ArmyMonhX
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   (GarAnchorX), HL
                POP  HL                             ; GarAnchorY = ArmyMonhY[slot]
                LD   DE, ArmyMonhY
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   (GarAnchorY), HL
                POP  AF                             ; A = recruit idx
                CALL Garrison_DrawMonh
.aml_next:      LD   A, (ArmyDrawSlot)
                INC  A
                LD   (ArmyDrawSlot), A
                JR   .aml

; Army_CntLoop — счётчики всех непустых слотов (0-9) в позициях ArmyCntX/Y[slot].
; Пролог текста (Town_Name_Begin_DL) должен быть уже в DL. Портит всё.
Army_CntLoop:   XOR  A
                LD   (ArmyDrawSlot), A
.acl:           LD   A, (ArmyDrawSlot)
                CP   10
                RET  Z
                LD   L, A
                LD   H, 0
                LD   DE, ArmyType
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .acl_next
                LD   A, (ArmyDrawSlot)              ; slot*2
                ADD  A, A
                LD   L, A
                LD   H, 0
                PUSH HL
                LD   DE, ArmyCntY                   ; ResPenY = ArmyCntY[slot]
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   (ResPenY), HL
                POP  HL
                PUSH HL                             ; slot*2 → &ArmyCnt[slot]
                LD   DE, ArmyCnt
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A                           ; HL = ArmyCnt[slot] (число)
                PUSH HL
                CALL Render_NumPixW                ; BC = ширина числа (px)
                POP  HL                             ; HL = число
                POP  DE                             ; DE = slot*2
                PUSH HL
                LD   HL, ArmyCntX                  ; правый край счётчика (px) слота
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                        ; DE = правый край (px)
                EX   DE, HL                          ; HL = правый край
                OR   A
                SBC  HL, BC                         ; правый − ширина = левый (px)
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                         ; ×16 (vertex)
                LD   (ResPenX), HL
                POP  HL                             ; число
                CALL Render_DrawNum
.acl_next:      LD   A, (ArmyDrawSlot)
                INC  A
                LD   (ArmyDrawSlot), A
                JR   .acl

; Army_HitTest — клик по армбару? OUT: A=slot(0-9) или 255. Логич.640×480. Ячейки: x[112..552) шаг 88,
; ряд гарнизона y[262..355), ряд героя y[361..454) (rectSign1/2 + strip). Портит BC/DE/HL.
Army_HitTest:   CALL Input_MouseX                 ; HL = x
                LD   DE, 112
                OR   A
                SBC  HL, DE                         ; x - 112
                JP   M, .aht_none                   ; x < 112
                LD   DE, 440                        ; 5*88
                PUSH HL
                OR   A
                SBC  HL, DE
                POP  HL
                JR   NC, .aht_none                  ; x-112 >= 440
                LD   B, 255                         ; col = (x-112)/88
                LD   DE, 88
.aht_dc:        INC  B
                OR   A
                SBC  HL, DE
                JR   NC, .aht_dc
                LD   C, B                            ; C = col (0-4)
                CALL Input_MouseY                   ; HL = y
                LD   DE, 262                        ; ряд гарнизона?
                PUSH HL
                OR   A
                SBC  HL, DE                         ; y-262
                JP   M, .aht_hero
                LD   DE, 93
                OR   A
                SBC  HL, DE
                POP  HL
                JR   NC, .aht_hero_ny               ; y-262 >= 93 → не гарнизон
                LD   A, C                            ; гарнизон: slot = col
                RET
.aht_hero:      POP  HL
.aht_hero_ny:   CALL Input_MouseY                   ; HL = y (заново)
                LD   DE, 361                        ; ряд героя?
                PUSH HL
                OR   A
                SBC  HL, DE                         ; y-361
                JP   M, .aht_none_pop
                LD   DE, 93
                OR   A
                SBC  HL, DE
                POP  HL
                JR   NC, .aht_none                  ; y-361 >= 93
                LD   A, C                            ; герой: slot = 5 + col
                ADD  A, 5
                RET
.aht_none_pop:  POP  HL
.aht_none:      LD   A, 255
                RET

; Army_Click — обработка клика по армбару. Вход: A = clicked slot (0-9). ArmyBar::ActionBarLeftMouseSingleClick.
Army_Click:     LD   C, A                            ; C = clicked slot
                LD   A, (ArmySel)
                CP   255
                JR   NZ, .aclk_place
                ; ничего не выбрано → выбрать, если слот НЕ пуст
                LD   A, C
                LD   L, A
                LD   H, 0
                LD   DE, ArmyType
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                RET  Z                              ; пусто → ничего
                LD   A, C
                LD   (ArmySel), A                   ; выбрать
                RET
.aclk_place:    ; A = ArmySel, C = clicked. Тот же слот → снять выбор.
                CP   C
                JR   Z, .aclk_desel
                CALL Army_MoveSlots                ; src=A(sel), dst=C
.aclk_desel:    LD   A, 255
                LD   (ArmySel), A
                RET

; Army_MoveSlots — src(A) → dst(C). Пусто→move; тот же тип→merge; иначе→swap.
Army_MoveSlots: LD   (ArmySrcSlot), A
                LD   A, C
                LD   (ArmyDstSlot), A
                LD   A, (ArmySrcSlot)              ; B = src type
                LD   L, A
                LD   H, 0
                LD   DE, ArmyType
                ADD  HL, DE
                LD   B, (HL)
                LD   A, (ArmyDstSlot)              ; C = dst type
                LD   L, A
                LD   H, 0
                LD   DE, ArmyType
                ADD  HL, DE
                LD   C, (HL)
                LD   A, C
                OR   A
                JR   Z, .ams_move                  ; dst пусто → move
                LD   A, B
                CP   C
                JR   Z, .ams_merge                 ; тот же тип → merge
                JP   Army_Swap                     ; иначе → swap
.ams_move:      ; dst = src (тип+счётчик), src обнулить
                LD   A, (ArmySrcSlot)
                CALL Army_CntPtr                   ; HL=&ArmyCnt[src]
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                        ; DE = src count
                LD   A, (ArmyDstSlot)
                CALL Army_CntPtr
                LD   (HL), E
                INC  HL
                LD   (HL), D                        ; ArmyCnt[dst] = src count
                LD   A, (ArmyDstSlot)              ; ArmyType[dst] = src type = B
                CALL Army_TypePtr
                LD   (HL), B
                JR   Army_ResetSrc
.ams_merge:     ; ArmyCnt[dst] += ArmyCnt[src], src обнулить
                LD   A, (ArmySrcSlot)
                CALL Army_CntPtr
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                        ; DE = src count
                LD   A, (ArmyDstSlot)
                CALL Army_CntPtr
                PUSH HL
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A                            ; HL = dst count
                ADD  HL, DE                         ; + src count
                EX   DE, HL                          ; DE = сумма
                POP  HL
                LD   (HL), E
                INC  HL
                LD   (HL), D
                ; fallthrough Army_ResetSrc
Army_ResetSrc:  LD   A, (ArmySrcSlot)              ; src: тип=0, счётчик=0
                CALL Army_TypePtr
                LD   (HL), 0
                LD   A, (ArmySrcSlot)
                CALL Army_CntPtr
                XOR  A
                LD   (HL), A
                INC  HL
                LD   (HL), A
                RET

; Army_Swap — обменять тип+счётчик слотов ArmySrcSlot ↔ ArmyDstSlot.
Army_Swap:      LD   A, (ArmySrcSlot)              ; типы
                CALL Army_TypePtr
                LD   B, (HL)                        ; B = src type
                LD   A, (ArmyDstSlot)
                CALL Army_TypePtr
                LD   C, (HL)                        ; C = dst type
                LD   (HL), B                        ; dst type = src
                LD   A, (ArmySrcSlot)
                CALL Army_TypePtr
                LD   (HL), C                        ; src type = dst
                LD   A, (ArmySrcSlot)              ; счётчики
                CALL Army_CntPtr
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                        ; DE = src count
                LD   A, (ArmyDstSlot)
                CALL Army_CntPtr
                LD   C, (HL)
                INC  HL
                LD   B, (HL)                        ; BC = dst count
                DEC  HL
                LD   (HL), E
                INC  HL
                LD   (HL), D                        ; ArmyCnt[dst] = src count
                LD   A, (ArmySrcSlot)
                CALL Army_CntPtr
                LD   (HL), C
                INC  HL
                LD   (HL), B                        ; ArmyCnt[src] = dst count
                RET

; Army_TypePtr — A=slot → HL=&ArmyType[slot]. Army_CntPtr — A=slot → HL=&ArmyCnt[slot].
; DE СОХРАНЯЕТСЯ (важно: вызывающие держат в DE счётчик-источник между вызовами).
Army_TypePtr:   PUSH DE
                LD   L, A
                LD   H, 0
                LD   DE, ArmyType
                ADD  HL, DE
                POP  DE
                RET
Army_CntPtr:    PUSH DE
                LD   L, A
                LD   H, 0
                ADD  HL, HL                         ; slot*2
                LD   DE, ArmyCnt
                ADD  HL, DE
                POP  DE
                RET

; Construct_TryBuild — клик по слоту окна строительства → построить (BuyBuilding). Логич.640×480.
; Castle::BuyBuilding по оригиналу: клик по слоту → строится ТОЛЬКО при статусе ALLOW
; (CheckBuyBuilding уже учёл BUILT/DISABLE/NOT_TODAY/REQUIRES/LACK) → OddFundsResource
; (списать ВСЕ 7 ресурсов) → BuiltRuntime=1 → ResetModes(ALLOW_TO_BUILD_TODAY) → пересчёт
; статусов (патчи) → здание на панораму.
Construct_TryBuild:
                CALL Construct_HitSlot            ; A = slot (0-17) или 255
                CP   18
                RET  NC                            ; не слот
                LD   C, A                          ; C = slot
                LD   L, A
                LD   H, 0
                LD   DE, CurStatus
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                RET  NZ                            ; статус не ALLOW → нельзя (по оригиналу)
                ; --- OddFundsResource: funds[k] -= cost[k], 7×DW ---
                LD   A, C                          ; HL = ConstructCostFull + slot*14
                LD   L, A
                LD   H, 0
                ADD  HL, HL                        ; *2
                LD   D, H
                LD   E, L
                ADD  HL, HL                        ; *4
                ADD  HL, HL                        ; *8
                ADD  HL, DE                        ; *10... нет: *8+*2=*10; надо *14 = *8+*4+*2
                PUSH HL                            ; *10
                LD   A, C
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                        ; *4
                POP  DE
                ADD  HL, DE                        ; *14
                LD   DE, ConstructCostFull
                ADD  HL, DE                        ; HL = cost-вектор
                LD   DE, KingdomGold               ; DE = вектор фондов (7×DW подряд)
                LD   B, 7
.pay:           PUSH BC
                LD   A, (DE)
                LD   C, A
                INC  DE
                LD   A, (DE)
                LD   B, A                          ; BC = fund
                PUSH DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL                            ; DE = cost, HL → след. cost
                PUSH HL
                LD   L, C
                LD   H, B                          ; HL = fund
                OR   A
                SBC  HL, DE                        ; fund - cost
                LD   C, L
                LD   B, H                          ; BC = остаток
                POP  HL
                POP  DE
                LD   A, B
                LD   (DE), A                       ; ??? порядок: сначала lo
                DEC  DE
                LD   A, C
                LD   (DE), A
                INC  DE
                INC  DE                            ; DE → след. фонд
                POP  BC
                DJNZ .pay
                LD   A, C                          ; BuiltRuntime[slot] = 1
                LD   L, A
                LD   H, 0
                LD   DE, BuiltRuntime
                ADD  HL, DE
                LD   (HL), 1
                XOR  A
                LD   (BuildToday), A               ; ResetModes(ALLOW_TO_BUILD_TODAY) — 1 стройка в день
                CALL Construct_Recalc              ; статусы всех слотов → патчи изменившихся
                JP   Town_PanoRuntime              ; построенное — на панораму (в z-порядке)

; Construct_HitSlot — клик по ячейке окна строительства? OUT: A=slot(0-17) или 255. Ячейка 137×70 @ ConstructHitX/Y.
Construct_HitSlot:
                LD   B, 0                          ; slot counter
.chs:           LD   A, B
                CP   18
                JR   NC, .chs_none
                LD   A, B                          ; hitX[slot]
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, ConstructHitX
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                        ; DE = hitX
                CALL Input_MouseX                  ; HL = x
                OR   A
                SBC  HL, DE                         ; x - hitX
                JP   M, .chs_next
                LD   DE, CONSTRUCT_SLOT_W
                OR   A
                SBC  HL, DE                         ; (x-hitX) - 137
                JR   NC, .chs_next                  ; вне по X
                LD   A, B                          ; hitY[slot]
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, ConstructHitY
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                        ; DE = hitY
                CALL Input_MouseY
                OR   A
                SBC  HL, DE                         ; y - hitY
                JP   M, .chs_next
                LD   DE, CONSTRUCT_SLOT_H
                OR   A
                SBC  HL, DE
                JR   NC, .chs_next                  ; вне по Y
                LD   A, B                          ; попали → slot
                RET
.chs_next:      INC  B
                JR   .chs
.chs_none:      LD   A, 255
                RET

; Construct_ChkLoop — галочка на каждый ПОСТРОЕННЫЙ слот (BuiltRuntime), кроме изначально построенных
; (у тех галочка уже запечена). Пролог MONH-спрайта уже в DL. Позиция = ConstructChkVX/VY[slot].
Construct_ChkLoop:
                XOR  A
                LD   (ConstructBuiltSlot), A
.ccl:           LD   A, (ConstructBuiltSlot)
                CP   18
                RET  Z
                LD   L, A                          ; построен рантайм? BuiltRuntime[slot]
                LD   H, 0
                LD   DE, BuiltRuntime
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .ccl_next                  ; не построен
                LD   A, (ConstructBuiltSlot)       ; изначально построен? (галочка уже запечена)
                LD   L, A
                LD   H, 0
                LD   DE, ConstructInitBuilt
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   NZ, .ccl_next                 ; запечён → не рисуем повторно
                LD   A, (ConstructBuiltSlot)       ; ResPenX = ConstructChkVX[slot]
                ADD  A, A
                LD   L, A
                LD   H, 0
                PUSH HL
                LD   DE, ConstructChkVX
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   (ResPenX), HL
                POP  HL
                LD   DE, ConstructChkVY
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   (ResPenY), HL
                LD   HL, ConstructChkRec
                CALL Render_DrawSpriteEntry        ; галочка @ перо
.ccl_next:      LD   A, (ConstructBuiltSlot)
                INC  A
                LD   (ConstructBuiltSlot), A
                JR   .ccl

; ============================================================================
; СТРОИТЕЛЬСТВО ПО ОРИГИНАЛУ — пересчёт статусов + патчи + панорама.
; ============================================================================
Construct_BitTab: DEFB 1, 2, 4, 8, 16, 32, 64, 128

; Construct_BuildMask — BuiltRuntime[18] → BuiltMask (3Б, бит i = слот i построен).
Construct_BuildMask:
                XOR  A
                LD   (BuiltMask), A
                LD   (BuiltMask+1), A
                LD   (BuiltMask+2), A
                LD   HL, BuiltRuntime
                LD   B, 0
.bm:            LD   A, B
                CP   18
                RET  Z
                LD   A, (HL)
                OR   A
                JR   Z, .bmnext
                PUSH HL
                PUSH BC
                LD   A, B
                AND  7
                LD   L, A
                LD   H, 0
                LD   DE, Construct_BitTab
                ADD  HL, DE
                LD   C, (HL)                       ; C = 1<<(bit&7)
                LD   A, B
                SRL  A
                SRL  A
                SRL  A
                LD   L, A
                LD   H, 0
                LD   DE, BuiltMask
                ADD  HL, DE
                LD   A, (HL)
                OR   C
                LD   (HL), A
                POP  BC
                POP  HL
.bmnext:        INC  HL
                INC  B
                JR   .bm

; Construct_Recalc — статус каждого из 18 слотов ТОЧНО по Castle::CheckBuyBuilding
; (castle.cpp:1137, порядок: BUILT → DISABLE → NOT_TODAY → REQUIRES → LACK → ALLOW).
; Изменившиеся против CurStatus → band/corner-патчи из PAK в композит окна стройки.
Construct_Recalc:
                CALL Construct_BuildMask
                XOR  A
                LD   (CalcSlot), A
.rc:            LD   A, (CalcSlot)
                CP   18
                RET  Z
                ; --- статус слота ---
                LD   L, A                          ; BUILT?
                LD   H, 0
                LD   DE, BuiltRuntime
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                LD   B, 1                          ; статус BUILT
                JR   NZ, .have
                LD   A, (CalcSlot)                 ; DISABLE (вечный, запечён)?
                LD   L, A
                LD   H, 0
                LD   DE, ConstructDisable
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                LD   B, 5
                JR   NZ, .have
                LD   A, (BuildToday)               ; NOT_TODAY?
                OR   A
                LD   B, 4
                JR   Z, .have
                ; REQUIRES: ConstructReqMask[slot*3] & ~BuiltMask != 0
                LD   A, (CalcSlot)
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, DE                        ; *3
                LD   DE, ConstructReqMask
                ADD  HL, DE
                LD   DE, BuiltMask
                LD   B, 3
.rq:            LD   A, (DE)
                CPL                                ; ~built
                AND  (HL)                          ; & req
                JR   NZ, .requires
                INC  HL
                INC  DE
                DJNZ .rq
                ; LACK: любой из 7 фондов < стоимости (Kingdom::AllowPayment)
                LD   A, (CalcSlot)                 ; HL = ConstructCostFull + slot*14
                LD   L, A
                LD   H, 0
                ADD  HL, HL                        ; *2
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL                        ; *8
                ADD  HL, DE                        ; *10
                PUSH HL
                LD   A, (CalcSlot)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                        ; *4
                POP  DE
                ADD  HL, DE                        ; *14
                LD   DE, ConstructCostFull
                ADD  HL, DE
                LD   DE, KingdomGold               ; вектор фондов 7×DW
                LD   B, 7
.lk:            PUSH BC
                LD   C, (HL)
                INC  HL
                LD   B, (HL)
                INC  HL                            ; BC = cost, HL → след.
                LD   A, (DE)
                INC  DE
                PUSH HL
                LD   L, A
                LD   A, (DE)
                LD   H, A                          ; HL = fund
                INC  DE
                OR   A
                SBC  HL, BC                        ; fund - cost
                POP  HL
                POP  BC
                JR   C, .lack
                DJNZ .lk
                LD   B, 0                          ; ALLOW
                JR   .have
.requires:      LD   B, 2
                JR   .have
.lack:          LD   B, 3
.have:          LD   A, B
                LD   (CalcStat), A
                ; --- сравнить с кэшем; изменился → патчи band+corner ---
                LD   A, (CalcSlot)
                LD   L, A
                LD   H, 0
                LD   DE, CurStatus
                ADD  HL, DE
                LD   A, (CalcStat)
                CP   (HL)
                JR   Z, .next
                LD   (HL), A
                CP   5
                JR   Z, .next                      ; DISABLE запечён — не патчить
                CALL Construct_PatchSlot
.next:          LD   A, (CalcSlot)
                INC  A
                LD   (CalcSlot), A
                JP   .rc

; Construct_PatchSlot — применить band+corner патчи для CalcSlot по CalcStat.
; band: BUILT→0(plain) ALLOW→1(green) прочее→2(red); corner: BUILT→1(check)
; ALLOW→0(clean) LACK→3(money) REQUIRES/NOT_TODAY→2(deny). (buildinginfo.cpp:349)
Construct_PatchSlot:
                LD   A, (CalcStat)                 ; band-вариант
                LD   C, 2                          ; по умолчанию red
                OR   A
                JR   Z, .bgreen
                CP   1
                JR   NZ, .bhave
                LD   C, 0                          ; BUILT → plain
                JR   .bhave
.bgreen:        LD   C, 1                          ; ALLOW → green
.bhave:         LD   A, (CalcSlot)                 ; HL = BandPatchSec + (slot*3+var)*2
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, DE                        ; *3
                LD   E, C
                LD   D, 0
                ADD  HL, DE
                ADD  HL, HL                        ; *2 (DW)
                LD   DE, BandPatchSec
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                CALL Loader_ApplyPatch             ; NB: клоберит IX (raw_pak)
                LD   A, (CalcStat)                 ; corner-вариант
                LD   C, 2                          ; deny (REQUIRES/NOT_TODAY)
                OR   A
                JR   NZ, .c1
                LD   C, 0                          ; ALLOW → clean
                JR   .chave
.c1:            CP   1
                JR   NZ, .c3
                LD   C, 1                          ; BUILT → check
                JR   .chave
.c3:            CP   3
                JR   NZ, .chave
                LD   C, 3                          ; LACK → money
.chave:         LD   A, (CalcSlot)                 ; HL = CornerPatchSec + (slot*4+var)*2
                ADD  A, A
                ADD  A, A                          ; slot*4 (≤68, влезает в байт)
                ADD  A, C
                ADD  A, A                          ; *2 (DW)
                LD   L, A
                LD   H, 0
                LD   DE, CornerPatchSec
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                JP   Loader_ApplyPatch

; Town_PanoRuntime — все ПОСТРОЕННЫЕ В РАНТАЙМЕ здания на панораму, В Z-ПОРЯДКЕ
; (redrawCastleBuildings: перекрытия честны при повторном применении по порядку).
; Запечённые изначально (ConstructInitBuilt) уже в композите — пропуск.
Town_PanoRuntime:
                XOR  A
                LD   (ConstructBuiltSlot), A       ; reuse: z-индекс 0..18
.pr:            LD   A, (ConstructBuiltSlot)
                CP   19
                RET  Z
                LD   L, A                          ; слот стройки этого здания
                LD   H, 0
                LD   DE, PanoToSlot
                ADD  HL, DE
                LD   A, (HL)
                CP   255
                JR   Z, .prnext                    ; CASTLE/CAPTAIN — не строятся тут
                LD   C, A
                LD   L, A                          ; построен в рантайме?
                LD   H, 0
                LD   DE, BuiltRuntime
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .prnext
                LD   A, C                          ; запечён изначально?
                LD   L, A
                LD   H, 0
                LD   DE, ConstructInitBuilt
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   NZ, .prnext
                LD   A, (ConstructBuiltSlot)       ; сектор патча = PanoPatchSec[z]
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, PanoPatchSec
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                CALL Loader_ApplyPatch
.prnext:        LD   A, (ConstructBuiltSlot)
                INC  A
                LD   (ConstructBuiltSlot), A
                JR   .pr

; Town_EconomyCatchUp — догнать экономику по дням (DayCounter=GameDay vs TownLastDay):
; за каждый день: WeekPos++, 7-й день → рост построенных жилищ (ActionNewWeek: base +
; Well(+2) + Wel2(+8 к DW1)); день сменился → ALLOW_TO_BUILD_TODAY. ДОХОД ЗОЛОТА — НЕ
; здесь: единая казна в резиденте, доход начисляет Game_EndTurn (1000 + 250×Statue из #91).
Town_EconomyCatchUp:
                LD   HL, (DayCounter)
                LD   DE, (TownLastDay)
                OR   A
                SBC  HL, DE
                RET  Z                             ; дни не менялись
                RET  C                             ; (страховка)
                LD   B, L                          ; дней прошло (малое число)
                LD   HL, (DayCounter)
                LD   (TownLastDay), HL
                LD   A, 1
                LD   (BuildToday), A               ; новый день → строить можно
.day:           PUSH BC
                LD   A, (WeekPos)                  ; день недели
                INC  A
                CP   7
                JR   C, .storeWeek
                CALL Town_WeekGrowth               ; новая неделя → рост жилищ
                XOR  A
.storeWeek:     LD   (WeekPos), A
                POP  BC
                DJNZ .day
                RET

; Town_WeekGrowth — рост ПОСТРОЕННЫХ жилищ (Castle::ActionNewWeek): DwellAvail[r] +=
; base(RecruitAvailNum) + 2 если Well построен + 8 к DW1 если Wel2 построен.
Town_WeekGrowth:
                LD   B, 0                          ; recruit idx 0..5
.wg:            LD   A, B
                CP   6
                RET  Z
                PUSH BC
                LD   L, B                          ; слот жилища DW(r+1)
                LD   H, 0
                LD   DE, RecruitToSlot
                ADD  HL, DE
                LD   A, (HL)
                LD   L, A                          ; построено?
                LD   H, 0
                LD   DE, BuiltRuntime
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .wgnext
                LD   A, B                          ; базовый рост RecruitAvailNum[r]
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, RecruitAvailNum
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = base
                LD   A, (BuiltRuntime + CONSTRUCT_WELL_SLOT)
                OR   A
                JR   Z, .noWell
                INC  DE
                INC  DE                            ; +2 (Well)
.noWell:        LD   A, B
                OR   A
                JR   NZ, .noWel2
                LD   A, (BuiltRuntime + CONSTRUCT_WEL2_SLOT)
                OR   A
                JR   Z, .noWel2
                LD   HL, 8                         ; +8 к DW1 (Wel2)
                ADD  HL, DE
                EX   DE, HL
.noWel2:        LD   A, B                          ; DwellAvail[r] += DE
                ADD  A, A
                LD   L, A
                LD   H, 0
                PUSH DE
                LD   DE, DwellAvail
                ADD  HL, DE
                POP  DE
                LD   A, (HL)
                ADD  A, E
                LD   (HL), A
                INC  HL
                LD   A, (HL)
                ADC  A, D
                LD   (HL), A
.wgnext:        POP  BC
                INC  B
                JR   .wg

; Town_DrawRes6 — живые числа 6 ресурсов (кроме золота): центры из таблицы CX (экран px),
; Y из таблицы VY (vertex). IN: HL=таблица CX, DE=таблица VY. Пролог текста уже в DL.
Res6CXPtr:      DEFW 0
Res6VYPtr:      DEFW 0
Res6Idx:        DEFB 0
Town_DrawRes6:
                LD   (Res6CXPtr), HL
                LD   (Res6VYPtr), DE
                XOR  A
                LD   (Res6Idx), A
.dr:            LD   A, (Res6Idx)
                CP   6
                RET  Z
                ADD  A, A                          ; idx*2
                LD   L, A
                LD   H, 0
                PUSH HL
                LD   DE, (Res6VYPtr)
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   (ResPenY), HL                 ; Y строки
                POP  HL
                PUSH HL
                LD   DE, (Res6CXPtr)
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                EX   DE, HL                          ; DE = центр X
                POP  HL
                LD   BC, KingdomRes6
                ADD  HL, BC
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A                           ; HL = значение ресурса
                CALL Render_DrawNumCentered
                LD   A, (Res6Idx)
                INC  A
                LD   (Res6Idx), A
                JR   .dr

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
                XOR  A
                LD   (TownConstructOpen), A       ; окно строительства закрыто
                LD   (TownTavernOpen), A          ; окно таверны закрыто
                LD   (TownWellOpen), A
                LD   A, 255
                LD   (ArmySel), A                 ; выбор армбара сброшен
                ; --- состояние города: восстановить снимок из #91 (оверлей рестримится каждый
                ;     вход!) либо init один раз. Казна — резидентная (KingdomFunds), init её
                ;     делает Resources_InitStart при новой игре. ---
                CALL GState_Fetch                 ; A=1 → снимок в TownStateBuf
                OR   A
                JR   Z, .nosnap
                LD   HL, TownStateBuf             ; восстановить перс-блок города
                LD   DE, TownPersist
                LD   BC, TOWN_PERSIST_LEN
                LDIR
                JR   .stateok                     ; (TownStateInit=1 пришёл со снимком)
.nosnap:        LD   A, (TownStateInit)
                OR   A
                JR   NZ, .stateok
                LD   HL, RecruitAvailNum          ; копировать базовое доступное → DwellAvail (6×DW)
                LD   DE, DwellAvail
                LD   BC, 12
                LDIR
                ; Гарнизон пуст, стартовая армия у героя (слоты 5,6 = Peasant 40, Archer 4).
                LD   A, 1                          ; slot5 = Peasant (type 1)
                LD   (ArmyType + 5), A
                LD   HL, 40
                LD   (ArmyCnt + 10), HL           ; ArmyCnt[5] (word) = 40
                LD   A, 2                          ; slot6 = Archer (type 2)
                LD   (ArmyType + 6), A
                LD   HL, 4
                LD   (ArmyCnt + 12), HL           ; ArmyCnt[6] = 4
                LD   HL, ConstructInitBuilt       ; рантайм-постройки = начально построенные (18 байт)
                LD   DE, BuiltRuntime
                LD   BC, 18
                LDIR
                LD   HL, (DayCounter)             ; день входа в игру (экономика с этого дня)
                LD   (TownLastDay), HL
                XOR  A
                LD   (WeekPos), A
                LD   A, 1
                LD   (BuildToday), A
                LD   A, 1
                LD   (TownStateInit), A
.stateok:       LD   HL, CurStatus                ; кэш статусов сброшен: композит стройки пере-стримится
                LD   B, 18
.csr:           LD   (HL), 255
                INC  HL
                DJNZ .csr
                CALL Town_EconomyCatchUp          ; дни End Turn: доход/рост/ALLOW_TO_BUILD_TODAY
                CALL Town_LoadFromPak             ; стрим HMM2TOWN.PAK → RAM_G[0]
                JP   Town_PanoRuntime             ; рантайм-постройки → на свежую панораму (z-порядок)

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
                LD   HL, TAV_TAIL_SECTOR          ; хвост таверны (TAVWIN+OKAY) → ЗА курсором
                CALL Loader_SeekSector
                LD   BC, TAV_TAIL_SECTORS
                LD   DE, TAV_TAIL_BASE & #FFFF
                LD   A, TAV_TAIL_BASE >> 16
                JP   Loader_StreamToRamGAt        ; (RET через JP)

; Опрос города: клик ЛКМ (после отпускания входного) → выход. OUT: A=1 если запрошен выход
; (резидентный Town_Update_Tramp по A=1 зовёт Adventure_Enter — slot3-edge).
Town_Update:
                ; --- Окно строительства открыто → МОДАЛЬНО: клик по EXIT закрывает, прочее игнор ---
                LD   A, (TownConstructOpen)
                OR   A
                JP   Z, .noconstruct
                CALL Input_MouseLMB
                JR   NZ, .con_pressed
                XOR  A
                LD   (TownExitLatch), A            ; отпущено → сбросить latch; A=0
                RET
.con_pressed:   LD   A, (TownExitLatch)
                OR   A
                JR   Z, .con_act
                XOR  A                             ; входной/повторный клик зажат → игнор
                RET
.con_act:       LD   A, 1
                LD   (TownExitLatch), A            ; одно действие на клик
                CALL Input_MouseX                 ; хит-тест EXIT (native 553..633 = логич.640×480)
                LD   DE, CONSTRUCT_EXIT_X0
                OR   A
                SBC  HL, DE
                JP   M, .con_stay
                LD   DE, CONSTRUCT_EXIT_X1 - CONSTRUCT_EXIT_X0
                OR   A
                SBC  HL, DE
                JR   NC, .con_stay                 ; X >= X1
                CALL Input_MouseY
                LD   DE, CONSTRUCT_EXIT_Y0
                OR   A
                SBC  HL, DE
                JP   M, .con_stay
                LD   DE, CONSTRUCT_EXIT_Y1 - CONSTRUCT_EXIT_Y0
                OR   A
                SBC  HL, DE
                JR   NC, .con_stay                 ; Y >= Y1
                XOR  A                             ; клик в EXIT → закрыть окно строительства
                LD   (TownConstructOpen), A
                RET
.con_stay:      CALL Construct_TryBuild            ; клик НЕ по EXIT → попытка построить здание
                XOR  A
                RET
.noconstruct:
                ; --- Окно таверны открыто → МОДАЛЬНО: закрытие ТОЛЬКО кликом по OKAY (Dialog::OK) ---
                LD   A, (TownTavernOpen)
                OR   A
                JR   Z, .notavern
                CALL Input_MouseLMB
                JR   NZ, .tav_pressed
                XOR  A
                LD   (TownExitLatch), A            ; отпущено → следующий клик валиден
                RET
.tav_pressed:   LD   A, (TownExitLatch)
                OR   A
                JR   NZ, .tav_hold                 ; открывающий клик ещё зажат
                CALL Town_TavernOkHit              ; NZ = клик по кнопке OKAY
                JR   Z, .tav_hold
                XOR  A
                LD   (TownTavernOpen), A           ; закрыть
                LD   A, 1
                LD   (TownExitLatch), A            ; зажатие не должно кликнуть панораму
.tav_hold:      XOR  A
                RET
.notavern:
                ; --- Окно РЫНКА открыто → МОДАЛЬНО (Dialog::Marketplace): сетки/стрелки/Max/Min/
                ;     TRADE/EXIT; одно действие на клик ---
                LD   A, (TownMarketOpen)
                OR   A
                JR   Z, .nomarket
                CALL Input_MouseLMB
                JR   NZ, .mk_pressed
                XOR  A
                LD   (TownExitLatch), A
                RET
.mk_pressed:    LD   A, (TownExitLatch)
                OR   A
                JR   NZ, .mk_hold
                LD   A, 1
                LD   (TownExitLatch), A            ; одно действие на клик
                CALL Market_Click                  ; обработать клик по элементам рынка
.mk_hold:       XOR  A
                RET
.nomarket:
                ; --- КОЛОДЕЦ открыт → МОДАЛЬНО: клик секции → найм жилища; EXIT → закрыть ---
                LD   A, (TownWellOpen)
                OR   A
                JR   Z, .nowell
                CALL Input_MouseLMB
                JR   NZ, .wl_pressed
                XOR  A
                LD   (TownExitLatch), A
                RET
.wl_pressed:    LD   A, (TownExitLatch)
                OR   A
                JR   NZ, .wl_hold
                LD   A, 1
                LD   (TownExitLatch), A
                CALL Well_Click
.wl_hold:       XOR  A
                RET
.nowell:
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
                ; JoinTroop в ГАРНИЗОН (слоты 0-4): тот же тип → слить; иначе первый пустой.
                LD   A, (TownRecruitIdx)
                INC  A                              ; тип = idx+1 (1-6)
                LD   C, A
                LD   B, 5
                LD   HL, ArmyType                  ; тот же тип уже стоит?
.rec_merge:     LD   A, (HL)
                CP   C
                JR   Z, .rec_addcnt
                INC  HL
                DJNZ .rec_merge
                LD   B, 5                           ; нет → первый пустой (тип 0)
                LD   HL, ArmyType
.rec_free:      LD   A, (HL)
                OR   A
                JR   Z, .rec_setnew
                INC  HL
                DJNZ .rec_free
                JR   .rec_doclose                 ; гарнизон полон
.rec_setnew:    LD   (HL), C                       ; ArmyType[slot] = тип
.rec_addcnt:    LD   DE, ArmyType                  ; HL=&ArmyType[slot] → &ArmyCnt[slot]
                OR   A
                SBC  HL, DE                         ; HL = slot (0-4)
                ADD  HL, HL                         ; slot*2
                LD   DE, ArmyCnt
                ADD  HL, DE                         ; &ArmyCnt[slot]
                PUSH HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                         ; DE = старый count
                LD   HL, (TownRecruitCount)
                ADD  HL, DE                         ; + count
                EX   DE, HL
                POP  HL
                LD   (HL), E
                INC  HL
                LD   (HL), D                         ; ArmyCnt[slot] += count
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
                ; Клик по армбару (перенос гарнизон↔герой) — приоритет над зданиями/EXIT.
.check:         CALL Army_HitTest
                CP   255
                JR   Z, .check_bld
                CALL Army_Click                   ; выбрать/поставить (move/merge/swap)
                LD   A, 1
                LD   (TownExitLatch), A            ; одно действие на клик
                XOR  A
                RET
                ; Клик по ЖИЛИЩУ → открыть диалог найма (Dialog::RecruitMonster). TownDwellingMap[idx-1].
.check_bld:     LD   A, (TownHoverIdx)
                OR   A
                JP   Z, .exitbtn                  ; не здание (панель) → проверить кнопку EXIT
                CP   2                             ; «Castle» = keep(2)+башни(5,6) → окно строительства
                JR   Z, .opencastle
                CP   5
                JR   Z, .opencastle
                CP   6
                JR   NZ, .notcastle
.opencastle:    CALL Well_EnsureConstruct          ; если в области WELL → рестрим construct
                LD   A, 1
                LD   (TownConstructOpen), A        ; открыть Castle::_openConstructionDialog
                LD   (TownExitLatch), A            ; залатчить открывающий клик
                CALL Construct_Recalc              ; ЖИВЫЕ статусы слотов → патчи (band+corner из PAK)
                XOR  A
                RET
.notcastle:     LD   A, (TownHoverIdx)
                CP   11                            ; ТАВЕРНА (KNIGHT_BUILDINGS[10], 1-based) →
                JR   NZ, .nottavclk                ;   окно слуха недели (Castle::_openTavern)
                LD   HL, (GameDay)                 ; слух = ((day−1) mod 49) / 7 = неделя mod 7
                DEC  HL
.tavmod:        LD   DE, 49
                OR   A
                SBC  HL, DE
                JR   NC, .tavmod
                ADD  HL, DE                        ; HL = (day−1) mod 49 (0..48)
                LD   A, L
                LD   C, 0
.tavdiv:        CP   7
                JR   C, .tavgot
                SUB  7
                INC  C
                JR   .tavdiv
.tavgot:        LD   A, C
                LD   (TownTavernRumor), A
                LD   A, 1
                LD   (TownTavernOpen), A
                LD   (TownExitLatch), A            ; залатчить открывающий клик
                XOR  A
                RET
.nottavclk:     LD   A, (TownHoverIdx)
                CP   18                            ; КОЛОДЕЦ (KNIGHT_BUILDINGS[17] WELL, 1-based)
                JR   NZ, .notwellclk
                CALL Well_Open                     ; стрим базы + патчи построенных жилищ
                LD   A, 1
                LD   (TownWellOpen), A
                LD   (TownExitLatch), A
                XOR  A
                RET
.notwellclk:    LD   A, (TownHoverIdx)
                CP   8                             ; РЫНОК (KNIGHT_BUILDINGS[7] MARKET, 1-based)
                JR   NZ, .notmktclk
                CALL Market_Open                   ; стрим TRADPOST-ассетов в область найма
                LD   A, 1
                LD   (TownMarketOpen), A
                LD   (TownExitLatch), A
                XOR  A
                RET
.notmktclk:     LD   A, (TownHoverIdx)
                DEC  A
                LD   L, A
                LD   H, 0
                LD   DE, TownDwellingMap
                ADD  HL, DE
                LD   A, (HL)                       ; recruit idx (0..5) или 255
                CP   255
                JR   Z, .exitbtn                  ; здание не жилище → проверить EXIT (даст .stay)
                LD   (TownRecruitIdx), A            ; открыть диалог найма для монстра
                CALL Market_EnsureRecrbkg          ; если в области найма рынок → рестрим RECRBKG
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
.exit:          CALL Town_SaveState                ; снимок города → #91 (постройки/жилища/армия)
                ; Город затёр RAM_G-кэш террейн-композита. Перед возвратом на карту форсируем
                ; полный перезалив: сбросить RuntimeLastOrigin (резидентная RAM, пишем из оверлея)
                ; в #FF → Runtime_UploadStaticIfDirty увидит origin!=last → зальёт грунт заново.
                LD   HL, #FFFF
                LD   (RuntimeLastOriginX), HL      ; X и Y смежны → одной записью
                LD   A, 1
                LD   (TownExitLatch), A            ; зафиксировать; A=1 (выход)
                RET

; Снимок перс-блока города → #91 (через TownStateBuf: при мапе #91 оверлей невидим).
; TownStateInit=1 попадает в снимок → вход по снимку минует init. Портит A,BC,DE,HL.
Town_SaveState:
                LD   A, 1
                LD   (TownStateInit), A
                LD   HL, TownPersist
                LD   DE, TownStateBuf
                LD   BC, TOWN_PERSIST_LEN
                LDIR
                JP   GState_Commit

; Рендер города: новый DL = Town_DL (CLEAR + композит ×1.6) + курсор + swap.
; Зовётся через Render_Town_Tramp. Хелперы (CmdBufCopy/GlobalCursor/SwapFrameDMA) slot3-safe.
Render_Town:
                FT_CMD_Start
                LD   HL, #FFFF                    ; CMD_DLSTART (новый DL, offset 0)
                LD   DE, #FF00
                CALL Render_CmdBufWrite32
                LD   A, (TownConstructOpen)        ; окно строительства открыто → рисуем его на весь экран
                OR   A
                JP   NZ, .construct
                LD   HL, Town_DL
                LD   BC, Town_DL_SIZE
                CALL Render_CmdBufCopy
                ; --- плиты STRIP[4] под ЗАНЯТЫМИ слотами (renderMonsterFrame) — ДО MONH-портретов ---
                CALL Army_PlateLoop
                ; --- MONH-портреты всех слотов армии (гарнизон 0-4 + герой 5-9), прозрачная палитра ---
                LD   HL, Recruit_Mon_Begin_DL
                LD   BC, Recruit_Mon_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Army_MonhLoop
                LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                ; --- текст: золото на панели + счётчики всех слотов армии ---
                LD   HL, Town_Name_Begin_DL
                LD   BC, Town_Name_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, GOLD_PANEL_VY
                LD   (ResPenY), HL
                LD   HL, (KingdomGold)
                LD   DE, GOLD_PANEL_CX             ; число золота ЦЕНТРИРУЕТСЯ (ui_castle.cpp:295)
                CALL Render_DrawNumCentered
                LD   HL, TownResCX                 ; + живые 6 ресурсов (постройка тратит их)
                LD   DE, TownResVY
                CALL Town_DrawRes6
                ; счётчики армии = normalWhite (army_bar.cpp:273 non-mini), право-выравнивание в цикле
                LD   HL, BigFontGlyphTab
                LD   (CurFontTab), HL
                CALL Army_CntLoop
                LD   HL, FontGlyphTab
                LD   (CurFontTab), HL
                LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                ; --- подсветка выбранного слота армбара (перенос гарнизон↔герой) ---
                LD   A, (ArmySel)
                CP   255
                JR   Z, .nohl
                ADD  A, A
                ADD  A, A                          ; slot*4 (запись = addr DW + size DW)
                LD   L, A
                LD   H, 0
                LD   DE, HighlightDLTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL                             ; DE = addr блока
                LD   C, (HL)
                INC  HL
                LD   B, (HL)                        ; BC = size
                EX   DE, HL                          ; HL = addr
                CALL Render_CmdBufCopy
.nohl:          LD   A, (TownRecruitIdx)          ; диалог найма открыт → его рисуем (приоритет)
                INC  A
                JP   NZ, .recruit
                LD   A, (TownTavernOpen)          ; окно таверны (модалка со слухом недели)
                OR   A
                JP   NZ, .tavern
                LD   A, (TownMarketOpen)          ; окно рынка (Dialog::Marketplace)
                OR   A
                JP   NZ, .market
                LD   A, (TownWellOpen)            ; колодец (Castle::_openWell)
                OR   A
                JP   NZ, .well
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
                LD   A, (TownHoverIdx)             ; имя = строка TownNameStrTab[idx-1], глиф-за-глифом
                DEC  A                             ; (пре-рендер маска шире 127px после ×1.5 ломает
                LD   L, A                          ;  DrawSpriteEntry — stride w*2 в байте)
                LD   H, 0
                ADD  HL, HL                        ; idx*2 (таблица DW)
                LD   DE, TownNameStrTab
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A                           ; HL = &имя (null-term)
                LD   DE, TOWN_NAME_Y               ; статус-бар Y (vertex)
                LD   (ResPenY), DE
                CALL Render_DrawStringCentered     ; SMALFONT ×1.5, центр экрана
                LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
.noname:        CALL Render_GlobalCursor          ; курсор (содержит DISPLAY)
                CALL Render_SwapFrameDMA          ; vsync перед DMA+DLSWAP
                RET

; Окно строительства замка — статичный композит CASLWIND ×1.6 на весь экран (Castle::_openConstructionDialog).
.construct:     LD   HL, Castle_Construct_DL
                LD   BC, Castle_Construct_DL_SIZE
                CALL Render_CmdBufCopy
                ; (галочки/полосы статусов теперь В КОМПОЗИТЕ — band/corner-патчи Construct_Recalc)
                ; --- живые числа ресурсов панели окна строительства (7 штук) ---
                LD   HL, Town_Name_Begin_DL
                LD   BC, Town_Name_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, CONSTRUCT_GOLD_VY
                LD   (ResPenY), HL
                LD   HL, (KingdomGold)
                LD   DE, CONSTRUCT_GOLD_CX         ; центрируется в ячейке золота (drawResourcePanel)
                CALL Render_DrawNumCentered
                LD   HL, ConResCX                  ; + 6 ресурсов (wood..gems)
                LD   DE, ConResVY
                CALL Town_DrawRes6
                LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                JP   .noname

; --- right-click инфо-попап: рамка + заголовок(имя) + описание построчно (faithful Dialog::Message) ---
; Попап = ТОЧНО Dialog::NonFixedFrameBox (dialog_box.cpp): рамка BUYBUILD (тень+куски, статичный
; DL по высоте текста), заголовок normalYellow + тело normalWhite (FONT), центр интерьера 244.
.popup:         LD   A, (TownInfoIdx)              ; запись = TownInfoDLTab + (idx-1)*4 (DW addr, DW size)
                DEC  A
                ADD  A, A
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, TownInfoDLTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   C, (HL)
                INC  HL
                LD   B, (HL)
                EX   DE, HL                          ; HL=addr, BC=size DL окна
                PUSH HL
                PUSH BC
                CALL Render_WindowShadowDL         ; ★тень = DL окна чёрным со сдвигом (глоб. процедура)
                POP  BC
                POP  HL
                CALL Render_CmdBufCopy             ; настоящее окно (куски BUYBUILD)
                LD   HL, Town_Name_Begin_DL       ; пролог текста (native + белая-альфа палитра)
                LD   BC, Town_Name_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, BigFontGlyphTab           ; заголовок и тело = FONT «normal» (ui_dialog.cpp:324-325)
                LD   (CurFontTab), HL
                LD   HL, #04FC                    ; COLOR_RGB 252,176,0 — normalYellow
                LD   DE, #B000
                CALL Render_CmdBufWrite32
                LD   A, (TownInfoIdx)              ; заголовок = имя, Y из TownInfoTitleVY[idx-1]
                DEC  A
                ADD  A, A                          ; (idx-1)*2
                LD   L, A
                LD   H, 0
                PUSH HL
                LD   DE, TownInfoTitleVY
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   (ResPenY), HL
                POP  HL
                PUSH HL
                LD   DE, TownNameStrTab
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A                           ; HL = &имя (null-term)
                CALL Render_DrawStringCentered
                LD   HL, #04FF                    ; COLOR_RGB 255,255,255 — тело normalWhite
                LD   DE, #FFFF
                CALL Render_CmdBufWrite32
                POP  HL                            ; (idx-1)*2
                PUSH HL
                LD   DE, TownInfoLine0VY           ; Y первой строки (заголовок + headerHeight)
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   (TownInfoLineY), HL
                POP  HL
                LD   DE, TownDescTab
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A                           ; HL = &блок строк
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
.descdone:      LD   HL, FontGlyphTab              ; вернуть SMALFONT остальным текстам
                LD   (CurFontTab), HL
                LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                JP   .noname

; --- ТАВЕРНА (Castle::_openTavern → showStandardTextMessage OK): рамка per слух (куски
; BUYBUILD + TAVWIN + OKAY в одном DL) + заголовок «Tavern» жёлтым + intro + слух белым. ---
.tavern:        LD   A, (TownTavernRumor)          ; запись = TavernDLTab[rumor]*8
                ADD  A, A
                ADD  A, A
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, TavernDLTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   C, (HL)
                INC  HL
                LD   B, (HL)
                INC  HL
                LD   (TavPressPtr), HL             ; → поля press-фрагмента
                EX   DE, HL                        ; HL = DL окна, BC = size
                PUSH HL
                PUSH BC
                CALL Render_WindowShadowDL         ; глобальная тень (DL чёрным со сдвигом)
                POP  BC
                POP  HL
                CALL Render_CmdBufCopy             ; окно (рамка + TAVWIN + OKAY отжата)
                CALL Input_MouseLMB                ; удержание ЛКМ на кнопке → нажатый кадр поверх
                JR   Z, .tvnopress
                CALL Town_TavernOkHit
                JR   Z, .tvnopress
                LD   HL, (TavPressPtr)
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                LD   C, (HL)
                INC  HL
                LD   B, (HL)
                EX   DE, HL
                CALL Render_CmdBufCopy
.tvnopress:     LD   HL, Town_Name_Begin_DL        ; тексты: пролог (native + альфа-палитра)
                LD   BC, Town_Name_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, BigFontGlyphTab           ; заголовок/тело = FONT (ui_dialog.cpp)
                LD   (CurFontTab), HL
                LD   HL, #04FC                     ; COLOR_RGB 252,176,0 — normalYellow
                LD   DE, #B000
                CALL Render_CmdBufWrite32
                LD   A, (TownTavernRumor)
                ADD  A, A
                LD   L, A
                LD   H, 0
                PUSH HL
                LD   DE, TavernTitleVY
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   (ResPenY), HL
                LD   HL, TownNameStrTab + 10 * 2   ; «Tavern» = имя здания [10]
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                CALL Render_DrawStringCentered
                LD   HL, #04FF                     ; COLOR_RGB 255,255,255 — normalWhite
                LD   DE, #FFFF
                CALL Render_CmdBufWrite32
                POP  HL                            ; rumor*2
                PUSH HL
                LD   DE, TavernIntroVY
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   (TownInfoLineY), HL
                LD   HL, TavernIntroBlk            ; «A generous tip for the barkeep …»
                CALL Town_DrawTextBlock
                POP  HL                            ; rumor*2
                PUSH HL
                LD   DE, TavernRumorVY
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   (TownInfoLineY), HL
                POP  HL
                LD   DE, TavernRumorTab
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A                          ; HL = блок строк слуха недели
                CALL Town_DrawTextBlock
                LD   HL, FontGlyphTab
                LD   (CurFontTab), HL
                LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                JP   .noname

; --- РЫНОК (Dialog::Marketplace): рамка+сетки+кнопки (Market_DL) + заголовок + запасы +
;     курсы «1/N» + рамки выбора + торг-зона (иконки/слайдер/qty/±) + нажатия. ---
.market:        LD   HL, Market_DL
                LD   BC, Market_DL_SIZE
                CALL Render_WindowShadowDL         ; глобальная тень
                LD   HL, Market_DL
                LD   BC, Market_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Market_PressedOverlays        ; нажатые кнопки при удержании ЛКМ
                CALL Market_DrawSel                ; рамки выбора from/to
                CALL Market_DrawTradeIcons         ; торг-зона: иконки from/to + обмен + слайдер
                LD   HL, Town_Name_Begin_DL        ; тексты
                LD   BC, Town_Name_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, BigFontGlyphTab
                LD   (CurFontTab), HL
                LD   HL, #04FC                     ; заголовок жёлтым
                LD   DE, #B000
                CALL Render_CmdBufWrite32
                LD   HL, MK_TITLE_VY
                LD   (ResPenY), HL
                LD   HL, TownNameStrTab + 7 * 2    ; «Marketplace» (имя здания [7])
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                CALL Render_DrawStringCentered
                LD   HL, #04FF                     ; тело белым
                LD   DE, #FFFF
                CALL Render_CmdBufWrite32
                CALL Market_DrawOfferText          ; «I can offer you …» (Big, белый)
                LD   HL, FontGlyphTab              ; запасы/курсы — SMALFONT
                LD   (CurFontTab), HL
                CALL Market_DrawStocks             ; запасы под from-сеткой
                CALL Market_DrawRates              ; «1/N» под to-сеткой
                CALL Market_DrawTradeText          ; qty + «-N (M)» / «+N (M)»
                LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                JP   .noname

; --- КОЛОДЕЦ (Castle::_openWell): полноэкранный композит в construct-области (тот же DL,
;     что окно строительства) + Available-числа ЖЁЛТЫМ + EXIT (WELLXTRA) + подпись в баре. ---
.well:          LD   HL, Castle_Construct_DL       ; SOURCE = construct-область (там сейчас WELL)
                LD   BC, Castle_Construct_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Input_MouseLMB                ; EXIT: нажатый кадр поверх (отжатый вбейкан)
                JR   Z, .wexrel
                CALL Well_ExitHit
                JR   Z, .wexrel
                LD   HL, WellExit1_DL
                LD   BC, WellExit1_DL_SIZE
                CALL Render_CmdBufCopy
.wexrel:
                LD   HL, Town_Name_Begin_DL        ; тексты: жёлтые Available + подпись бара
                LD   BC, Town_Name_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, #04FC                     ; normalYellow (Available-числа)
                LD   DE, #B000
                CALL Render_CmdBufWrite32
                LD   B, 0
.wavl:          PUSH BC
                LD   A, B                          ; построено? (BuiltMask бит i; DW1 всегда)
                CALL Well_DwellBuilt
                JR   Z, .wskip
                POP  BC
                PUSH BC
                LD   A, B                          ; ResPenY = WellAvailVY[i]
                ADD  A, A
                LD   L, A
                LD   H, 0
                PUSH HL
                LD   DE, WellAvailVY
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   (ResPenY), HL
                POP  HL
                LD   DE, WellAvailCX               ; DE = физ. центр
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                PUSH DE
                POP  IY                            ; IY = центр (сохранить от DwellAvail-чтения)
                POP  BC
                PUSH BC
                LD   A, B                          ; HL = DwellAvail[i]
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, DwellAvail
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                PUSH IY
                POP  DE
                CALL Render_DrawNumCentered
.wskip:         POP  BC
                INC  B
                LD   A, B
                CP   6
                JR   C, .wavl
                LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                JP   .noname

; --- диалог найма: окно RECRBKG ×1.6 + имя/доступно/цена/счётчик (Dialog::RecruitMonster) ---
.recruit:       LD   HL, Recruit_Win_DL           ; ★тень = тот же DL окна чёрным со сдвигом (глоб. процедура)
                LD   BC, Recruit_Win_DL_SIZE
                CALL Render_WindowShadowDL
                LD   HL, Recruit_Win_DL
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
                LD   HL, #04FF                    ; COLOR_RGB 255,230,0 — заголовок ЖЁЛТЫЙ (normalYellow, стр.164)
                LD   DE, #E600
                CALL Render_CmdBufWrite32
                LD   HL, BigFontGlyphTab           ; заголовок = FONT 14px normalYellow (C:164, не SMALFONT)
                LD   (CurFontTab), HL
                LD   A, (TownRecruitIdx)           ; имя монстра
                LD   DE, RecruitNameTab
                CALL Recr_StrPtr
                LD   DE, RECR_NAME_VY
                LD   (ResPenY), DE
                CALL Render_DrawStringCentered
                LD   HL, FontGlyphTab              ; вернуть SMALFONT для остальных подписей
                LD   (CurFontTab), HL
                LD   HL, #04FF                    ; COLOR_RGB 255,255,255 — остальной текст белый
                LD   DE, #FFFF
                CALL Render_CmdBufWrite32
                ; --- "Available: N" ЦЕНТР по RECR_AVAIL_CX (весь текст = префикс+число, стр.215 x+64 центр) ---
                LD   HL, RECR_AVAIL_VY
                LD   (ResPenY), HL
                LD   HL, RecruitAvailPfx           ; ширина префикса
                CALL Town_StrPixW
                LD   (RecTmpW), BC
                CALL Town_RecAvail                 ; DE = доступно
                LD   (RecTmpN), DE
                EX   DE, HL                         ; HL = число
                CALL Render_NumPixW                ; BC = ширина числа
                LD   HL, (RecTmpW)
                ADD  HL, BC                         ; HL = pfxW + numW = полная ширина
                SRL  H
                RR   L                              ; ширина/2
                EX   DE, HL                         ; DE = ширина/2
                LD   HL, RECR_AVAIL_CX
                OR   A
                SBC  HL, DE                         ; центр − ширина/2 = левый край (px)
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                         ; ×16
                LD   (ResPenX), HL
                LD   HL, RecruitAvailPfx
                CALL Render_DrawString             ; префикс, двигает перо
                LD   HL, (RecTmpN)
                CALL Render_DrawNum                ; число сразу за префиксом
                ; --- "Number to buy:" ПРАВЫЙ край по RECR_NUMBUY_RX (стр.219 x+107 − tw) ---
                LD   HL, RECR_NUMBUY_VY
                LD   (ResPenY), HL
                LD   HL, RecruitNumBuy
                CALL Town_StrPixW                  ; BC = ширина
                LD   HL, RECR_NUMBUY_RX
                OR   A
                SBC  HL, BC                         ; правый край − ширина = левый (px)
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                LD   (ResPenX), HL
                LD   HL, RecruitNumBuy
                CALL Render_DrawString
                ; --- итог = число ЦЕНТР по RECR_TOTAL_CX (стр.124 x+144 центр) ---
                LD   HL, RECR_COST_VY
                LD   (ResPenY), HL
                CALL Town_RecTotal                 ; HL = TownRecruitCount × цена-за-1
                LD   DE, RECR_TOTAL_CX
                CALL Render_DrawNumCentered
                ; --- счётчик ЦЕНТР бокса по RECR_COUNT_CX — normalWhite (BigFont, стр.101/106) ---
                LD   HL, BigFontGlyphTab
                LD   (CurFontTab), HL
                LD   HL, RECR_COUNT_VY
                LD   (ResPenY), HL
                LD   HL, (TownRecruitCount)
                LD   DE, RECR_COUNT_CX
                CALL Render_DrawNumCentered
                LD   HL, FontGlyphTab              ; вернуть SMALFONT
                LD   (CurFontTab), HL
                ; --- цена-за-1 (строка) ЦЕНТР под иконкой золота по RECR_PT_CX (стр.148 x+189 центр) ---
                LD   HL, RECR_PT_VY
                LD   (ResPenY), HL
                LD   A, (TownRecruitIdx)
                LD   DE, RecruitPerTroopTab
                CALL Recr_StrPtr                   ; HL = строка
                LD   DE, RECR_PT_CX
                CALL Render_DrawStrCenteredAt
                LD   HL, Town_Name_End_DL
                LD   BC, Town_Name_End_DL_SIZE
                CALL Render_CmdBufCopy
                JP   .noname

TOWN_NAME_Y     EQU 745 * 16       ; статус-бар (экран y≈745, в нижней панели), vertex 1/16px

; --- Хелперы таверны (глобальные — В КОНЦЕ файла, чтобы не рвать локальный скоуп Render_Town) ---
TavPressPtr:    DEFW 0             ; scratch: &поля press-фрагмента записи TavernDLTab

; HL = блок null-строк (пустая = конец): рисовать построчно от (TownInfoLineY) с шагом
; TOWN_INFO_LINE_H, центрируя. Портит A,BC,DE,HL.
Town_DrawTextBlock:
.tblp:          LD   A, (HL)
                OR   A
                RET  Z
                LD   DE, (TownInfoLineY)
                LD   (ResPenY), DE
                CALL Render_DrawStringCentered
                INC  HL
                PUSH HL
                LD   HL, (TownInfoLineY)
                LD   DE, TOWN_INFO_LINE_H
                ADD  HL, DE
                LD   (TownInfoLineY), HL
                POP  HL
                JR   .tblp

; NZ если мышь в hit-зоне кнопки OKAY таверны (лог. коорд.; Y per слух). Портит A,DE,HL.
Town_TavernOkHit:
                CALL Input_MouseX
                LD   DE, TAVERN_OK_X0
                OR   A
                SBC  HL, DE
                JR   C, .no
                LD   DE, TAVERN_OK_X1 - TAVERN_OK_X0
                OR   A
                SBC  HL, DE
                JR   NC, .no
                LD   A, (TownTavernRumor)
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, TavernOkHitY0
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = y0 кнопки
                CALL Input_MouseY
                OR   A
                SBC  HL, DE
                JR   C, .no
                LD   DE, TAVERN_OK_H
                OR   A
                SBC  HL, DE
                JR   NC, .no
                LD   A, 1
                OR   A
                RET
.no:            XOR  A
                RET

; ============================================================================
; РЫНОК (Dialog::Marketplace) — хелперы (глобальные, в конце файла после скоупа Render_Town).
; Ресурсы по индексам СЕТКИ: 0=wood 1=mercury 2=ore 3=sulfur 4=crystal 5=gems 6=gold.
; Золото — МЛАДШИЕ 2 байта ResGold (кламп #FFFF; переполнение казны в скирмише недостижимо).
; ============================================================================
MarketResAddrTab:                  ; [сетка] -> КАЗНА ГОРОДА (KingdomGold+Res6, ЕДИНЫЙ вектор)
                DW KingdomRes6, KingdomRes6 + 2, KingdomRes6 + 4     ; wood, mercury, ore
                DW KingdomRes6 + 6, KingdomRes6 + 8, KingdomRes6 + 10 ; sulfur, crystal, gems
                DW KingdomGold
MkSegMax:       DEFB "Max", 0
MkSegMin:       DEFB "Min", 0
MkSegQty:       DEFB "Qty to trade", 0
MkSegSlash:     DEFB "1/", 0
MkMul24:        DEFB 0, 0, 0       ; 24-бит аккумулятор (LE)

; Открыть рынок: стрим TRADPOST-ассетов в область найма + сброс стейта. Портит всё.
Market_Open:
                LD   HL, TownPakName
                LD   DE, MenuNameBuf
                LD   BC, 13
                LDIR
                CALL Loader_Init
                CALL Loader_Mount
                LD   HL, MenuNameBuf
                CALL Loader_OpenFile
                LD   HL, MK_SECTOR
                CALL Loader_SeekSector
                LD   BC, MK_SECTORS
                LD   DE, RECRUIT_WIN_RAMG & #FFFF
                LD   A, RECRUIT_WIN_RAMG >> 16
                CALL Loader_StreamToRamGAt
                LD   A, 1
                LD   (TownRecrLoaded), A
                LD   A, #FF
                LD   (MarketFrom), A
                LD   (MarketTo), A
                LD   HL, 0
                LD   (MarketQty), HL
                LD   (MarketMax), HL
                RET

; Если в области найма рынок — вернуть RECRBKG (рестрим куска payload). Портит всё.
Market_EnsureRecrbkg:
                LD   A, (TownRecrLoaded)
                OR   A
                RET  Z
                LD   HL, TownPakName
                LD   DE, MenuNameBuf
                LD   BC, 13
                LDIR
                CALL Loader_Init
                CALL Loader_Mount
                LD   HL, MenuNameBuf
                CALL Loader_OpenFile
                LD   HL, RECR_SECTOR
                CALL Loader_SeekSector
                LD   BC, RECR_SECTORS
                LD   DE, RECRUIT_WIN_RAMG & #FFFF
                LD   A, RECRUIT_WIN_RAMG >> 16
                CALL Loader_StreamToRamGAt
                XOR  A
                LD   (TownRecrLoaded), A
                RET

MkRectW:        DEFB 0             ; scratch зоны
MkRectH:        DEFB 0

; Мышь в прямоугольнике: DE=x0 (лог.), BC=y0, (MkRectW/H) — размеры. NZ внутри. Портит A,HL.
Market_MouseInRect:
                PUSH BC
                PUSH DE
                CALL Input_MouseX
                POP  DE
                OR   A
                SBC  HL, DE
                POP  BC
                JR   C, .no
                LD   A, H
                OR   A
                JR   NZ, .no
                LD   A, (MkRectW)
                CP   L
                JR   C, .no
                JR   Z, .no
                PUSH BC
                CALL Input_MouseY
                POP  BC
                OR   A
                SBC  HL, BC
                JR   C, .no
                LD   A, H
                OR   A
                JR   NZ, .no
                LD   A, (MkRectH)
                CP   L
                JR   C, .no
                JR   Z, .no
                LD   A, 1
                OR   A
                RET
.no:            XOR  A
                RET

; Клик по сетке: DE = базовый X сетки -> A = индекс 0..6 или #FF. Портит A,BC,HL.
Market_GridHit:
                LD   A, 34
                LD   (MkRectW), A
                LD   (MkRectH), A
                LD   B, 0                          ; индекс
.gh:            PUSH BC
                PUSH DE
                LD   A, B
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   BC, MarketGridOfs
                ADD  HL, BC
                LD   C, (HL)                       ; dx
                INC  HL
                LD   A, (HL)                       ; dy
                PUSH AF
                LD   L, C
                LD   H, 0
                ADD  HL, DE
                EX   DE, HL                        ; DE = x0
                POP  AF
                LD   C, A
                LD   B, 0
                LD   HL, MK_GRID_Y
                ADD  HL, BC
                LD   B, H
                LD   C, L                          ; BC = y0
                CALL Market_MouseInRect
                POP  DE
                POP  BC
                JR   NZ, .ghit
                INC  B
                LD   A, B
                CP   7
                JR   C, .gh
                LD   A, #FF
                RET
.ghit:          LD   A, B
                RET

; rate (DW) по (MarketFrom, MarketTo) -> HL; 0 если не выбраны/same. Портит A,DE.
Market_Rate:
                LD   A, (MarketFrom)
                CP   #FF
                JR   Z, .zero
                LD   D, A
                LD   A, (MarketTo)
                CP   #FF
                JR   Z, .zero
                LD   E, A
                LD   A, D                          ; from*7 + to
                ADD  A, A
                ADD  A, A
                ADD  A, A
                SUB  D
                ADD  A, E
                ADD  A, A                          ; *2 (DW)
                LD   L, A
                LD   H, 0
                LD   DE, MarketRateTab
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                RET
.zero:          LD   HL, 0
                RET

; Казна[A=индекс сетки] -> HL (16 бит; gold — младшие 2Б). Портит A,DE.
Market_GetFunds:
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, MarketResAddrTab
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                RET

; Казна[A] = HL. Портит A,DE,HL.
Market_SetFunds:
                PUSH HL
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, MarketResAddrTab
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                POP  DE
                LD   (HL), E
                INC  HL
                LD   (HL), D
                RET

; MkMul24 = HL x DE (цикл по DE — звать с DE=МЕНЬШИМ множителем). Портит A,DE.
Market_Mul:
                XOR  A
                LD   (MkMul24), A
                LD   (MkMul24 + 1), A
                LD   (MkMul24 + 2), A
.ml:            LD   A, D
                OR   E
                RET  Z
                LD   A, (MkMul24)                  ; acc += HL
                ADD  A, L
                LD   (MkMul24), A
                LD   A, (MkMul24 + 1)
                ADC  A, H
                LD   (MkMul24 + 1), A
                LD   A, (MkMul24 + 2)
                ADC  A, 0
                LD   (MkMul24 + 2), A
                DEC  DE
                JR   .ml

; Пересчёт MarketMax по паре: to=gold -> funds[from]; иначе funds[from]/rate. Кламп 999
; (практичный потолок счётчика; спиннер ориг. столь же ограничен слайдером). Портит всё.
Market_Recalc:
                LD   HL, 0
                LD   (MarketQty), HL
                LD   (MarketMax), HL
                CALL Market_Rate
                LD   A, H
                OR   L
                RET  Z
                PUSH HL                            ; rate
                LD   A, (MarketFrom)
                CALL Market_GetFunds               ; HL = запас from
                POP  DE                            ; DE = rate
                LD   A, (MarketTo)
                CP   6
                JR   NZ, .div
                LD   (MarketMax), HL               ; продаём за золото: max = весь запас
                JR   .clamp
.div:           LD   BC, 0                         ; max = funds/rate (повт. вычитание)
.dv:            OR   A
                SBC  HL, DE
                JR   C, .dvd
                INC  BC
                JR   .dv
.dvd:           LD   (MarketMax), BC
.clamp:         LD   HL, (MarketMax)
                LD   DE, 999
                OR   A
                SBC  HL, DE
                RET  C
                LD   HL, 999
                LD   (MarketMax), HL
                RET

; Сделка (формулы ориг.): to=gold: -qty from, +qty*rate gold; from=gold: -qty*rate gold,
; +qty to; иначе: -qty*rate from, +qty to. Портит всё.
Market_Trade:
                LD   HL, (MarketQty)
                LD   A, H
                OR   L
                RET  Z
                CALL Market_Rate
                LD   A, H
                OR   L
                RET  Z
                PUSH HL                            ; rate
                LD   A, (MarketTo)
                CP   6
                JR   NZ, .notgold
                LD   A, (MarketFrom)               ; продаём from за золото
                CALL Market_GetFunds
                LD   DE, (MarketQty)
                OR   A
                SBC  HL, DE
                LD   A, (MarketFrom)
                CALL Market_SetFunds
                POP  DE                            ; rate <= 50: цикл по rate
                LD   HL, (MarketQty)
                CALL Market_Mul                    ; qty*rate
                LD   A, 6
                CALL Market_GetFunds
                LD   DE, (MkMul24)
                ADD  HL, DE
                JR   NC, .goldw
                LD   HL, #FFFF
.goldw:         LD   A, 6
                JP   Market_SetFunds
.notgold:       LD   A, (MarketFrom)
                CP   6
                JR   NZ, .res2res
                POP  HL                            ; rate 2500/5000: цикл по qty (<=26)
                LD   DE, (MarketQty)
                CALL Market_Mul                    ; rate*qty
                LD   A, 6
                CALL Market_GetFunds
                LD   DE, (MkMul24)
                OR   A
                SBC  HL, DE
                JR   NC, .gw2
                LD   HL, 0
.gw2:           LD   A, 6
                CALL Market_SetFunds
                JR   .credit
.res2res:       POP  DE                            ; rate <= 20: цикл по rate
                LD   HL, (MarketQty)
                CALL Market_Mul                    ; qty*rate
                LD   A, (MarketFrom)
                CALL Market_GetFunds
                LD   DE, (MkMul24)
                OR   A
                SBC  HL, DE
                JR   NC, .fw
                LD   HL, 0
.fw:            LD   A, (MarketFrom)
                CALL Market_SetFunds
.credit:        LD   A, (MarketTo)                 ; +qty to
                CALL Market_GetFunds
                LD   DE, (MarketQty)
                ADD  HL, DE
                LD   A, (MarketTo)
                JP   Market_SetFunds

; Обработка клика по рынку (одно действие на клик). Портит всё.
Market_Click:
                LD   DE, MK_GRID_FROM_X            ; СЕТКИ ПЕРВЫМИ (gold-to перекрыт зоной EXIT)
                CALL Market_GridHit
                CP   #FF
                JR   Z, .ckto
                LD   (MarketFrom), A
                JP   Market_Recalc
.ckto:          LD   DE, MK_GRID_TO_X
                CALL Market_GridHit
                CP   #FF
                JR   Z, .ckbtns
                LD   (MarketTo), A
                JP   Market_Recalc
.ckbtns:        LD   A, 96
                LD   (MkRectW), A
                LD   A, 25
                LD   (MkRectH), A
                LD   DE, MK_EXIT_X0
                LD   BC, MK_EXIT_Y0
                CALL Market_MouseInRect
                JR   Z, .noexit
                XOR  A
                LD   (TownMarketOpen), A           ; закрыть (RECRBKG вернётся лениво при найме)
                RET
.noexit:        LD   DE, MK_TRADE_X0
                LD   BC, MK_TRADE_Y0
                CALL Market_MouseInRect
                JR   Z, .notrade
                CALL Market_Trade
                JP   Market_Recalc
.notrade:       LD   A, 14
                LD   (MkRectW), A
                LD   (MkRectH), A
                LD   DE, MK_ARRL_X0
                LD   BC, MK_ARR_Y0
                CALL Market_MouseInRect
                JR   Z, .noleft
                LD   HL, (MarketQty)               ; qty-1 (не ниже 0)
                LD   A, H
                OR   L
                RET  Z
                DEC  HL
                LD   (MarketQty), HL
                RET
.noleft:        LD   DE, MK_ARRR_X0
                LD   BC, MK_ARR_Y0
                CALL Market_MouseInRect
                JR   Z, .noright
                LD   HL, (MarketQty)               ; qty+1 (не выше max)
                LD   DE, (MarketMax)
                OR   A
                SBC  HL, DE
                RET  NC
                LD   HL, (MarketQty)
                INC  HL
                LD   (MarketQty), HL
                RET
.noright:       LD   A, MK_MAXMIN_X1 - MK_MAXMIN_X0
                LD   (MkRectW), A
                LD   A, MK_MAXMIN_H
                LD   (MkRectH), A
                LD   DE, MK_MAXMIN_X0
                LD   BC, MK_MAX_Y0
                CALL Market_MouseInRect
                JR   Z, .nomax
                LD   HL, (MarketMax)               ; Max
                LD   (MarketQty), HL
                RET
.nomax:         LD   DE, MK_MAXMIN_X0
                LD   BC, MK_MIN_Y0
                CALL Market_MouseInRect
                JR   Z, .nomin
                LD   HL, (MarketMax)               ; Min = 1 (если max>0)
                LD   A, H
                OR   L
                LD   HL, 1
                JR   NZ, .minw
                LD   HL, 0
.minw:          LD   (MarketQty), HL
                RET
.nomin:         LD   A, 187                        ; клик по ПОЛОСЕ слайдера -> qty = dx*max/187
                LD   (MkRectW), A
                LD   A, 14
                LD   (MkRectH), A
                LD   DE, MK_SLIDER_X0
                LD   BC, MK_BAR_Y0
                CALL Market_MouseInRect
                JR   Z, .nobar
                LD   HL, (MarketMax)
                LD   A, H
                OR   L
                JR   Z, .nobar
                PUSH HL
                CALL Input_MouseX
                LD   DE, MK_SLIDER_X0
                OR   A
                SBC  HL, DE                        ; dx (0..187)
                POP  DE                            ; max
                CALL Market_Mul                    ; MkMul24 = dx*max (цикл по max<=999)
                LD   HL, 187
                LD   (MkDivisor), HL
                CALL Market_Div24                  ; BC = dx*max/187
                LD   (MarketQty), BC
                RET
.nobar:         RET

; --- РЕНДЕР-хелперы рынка ---
; Нажатые кнопки при удержании ЛКМ. Портит всё.
Market_PressedOverlays:
                CALL Input_MouseLMB
                RET  Z
                LD   A, 96
                LD   (MkRectW), A
                LD   A, 25
                LD   (MkRectH), A
                LD   DE, MK_EXIT_X0
                LD   BC, MK_EXIT_Y0
                CALL Market_MouseInRect
                JR   Z, .nexit
                LD   HL, Market_MkExitPress_DL
                LD   BC, Market_MkExitPress_DL_SIZE
                JP   Render_CmdBufCopy
.nexit:         LD   DE, MK_TRADE_X0
                LD   BC, MK_TRADE_Y0
                CALL Market_MouseInRect
                JR   Z, .ntrade
                LD   HL, Market_MkTradePress_DL
                LD   BC, Market_MkTradePress_DL_SIZE
                JP   Render_CmdBufCopy
.ntrade:        LD   A, 14
                LD   (MkRectW), A
                LD   (MkRectH), A
                LD   DE, MK_ARRL_X0
                LD   BC, MK_ARR_Y0
                CALL Market_MouseInRect
                JR   Z, .nleft
                LD   HL, Market_MkArrLPress_DL
                LD   BC, Market_MkArrLPress_DL_SIZE
                JP   Render_CmdBufCopy
.nleft:         LD   DE, MK_ARRR_X0
                LD   BC, MK_ARR_Y0
                CALL Market_MouseInRect
                RET  Z
                LD   HL, Market_MkArrRPress_DL
                LD   BC, Market_MkArrRPress_DL_SIZE
                JP   Render_CmdBufCopy

; лог.px (HL) -> vertex 1/16 физ.: v = x*25 + (x*6)/10 (= x*25.6). Портит A,BC,DE.
Market_LogToVtx:
                LD   E, L
                LD   D, H                          ; DE = x
                ADD  HL, HL
                ADD  HL, HL                        ; x4
                ADD  HL, DE                        ; x5
                LD   C, L
                LD   B, H
                ADD  HL, HL
                ADD  HL, HL                        ; x20
                ADD  HL, BC                        ; x25
                PUSH HL
                EX   DE, HL                        ; HL = x
                LD   C, L
                LD   B, H
                ADD  HL, HL
                ADD  HL, BC                        ; x3
                ADD  HL, HL                        ; x6
                LD   C, 10
                CALL Town_Div16by8
                POP  DE
                ADD  HL, DE
                RET

; HL = HL / C (беззнак.). Портит AF,B.
Town_Div16by8:
                XOR  A
                LD   B, 16
.dv:            ADD  HL, HL
                RLA
                CP   C
                JR   C, .sk
                SUB  C
                INC  L
.sk:            DJNZ .dv
                RET

; Рамки выбора from/to (спрайт [14] на rect-2). Портит всё.
Market_DrawSel:
                LD   A, (MarketFrom)
                CP   #FF
                JR   Z, .nofrom
                LD   DE, MK_GRID_FROM_X
                CALL Market_SelEmit
.nofrom:        LD   A, (MarketTo)
                CP   #FF
                RET  Z
                LD   DE, MK_GRID_TO_X
                ; fallthrough
; A=индекс ресурса, DE=база сетки: эмит Market_MkSel_DL + vertex(rect-2). Портит всё.
Market_SelEmit:
                PUSH DE
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   BC, MarketGridOfs
                ADD  HL, BC
                LD   C, (HL)                       ; dx
                INC  HL
                LD   B, (HL)                       ; dy
                POP  DE
                PUSH BC
                LD   L, C
                LD   H, 0
                ADD  HL, DE                        ; x = base+dx
                DEC  HL
                DEC  HL                            ; -2
                CALL Market_LogToVtx
                LD   (RenderPathVertexX), HL
                POP  BC
                LD   L, B
                LD   H, 0
                LD   BC, MK_GRID_Y - 2
                ADD  HL, BC
                CALL Market_LogToVtx
                LD   (RenderPathVertexY), HL
                LD   HL, Market_MkSel_DL
                LD   BC, Market_MkSel_DL_SIZE
                CALL Render_CmdBufCopy
                JP   Render_WriteVertex2FCmd

; Торг-зона: иконки from/to + обмен-стрелки + слайдер (полоса+ползунок). Портит всё.
Market_DrawTradeIcons:
                LD   A, (MarketFrom)
                CP   #FF
                RET  Z
                LD   A, (MarketTo)
                CP   #FF
                RET  Z
                LD   B, A
                LD   A, (MarketFrom)
                CP   B
                RET  Z                              ; same -> зоны нет (n/a)
                ; иконка FROM: SOURCE по ресурсу + LAYOUT/SIZE 34x34 + vertex
                LD   A, (MarketFrom)
                LD   HL, MK_ICON_FROM_VX
                CALL Market_EmitResIcon
                LD   A, (MarketTo)
                LD   HL, MK_ICON_TO_VX
                CALL Market_EmitResIcon
                LD   HL, Market_MkFromTo_DL        ; обмен-стрелки [0]
                LD   BC, Market_MkFromTo_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, MK_FROMTO_VX
                LD   (RenderPathVertexX), HL
                LD   HL, MK_FROMTO_VY
                LD   (RenderPathVertexY), HL
                CALL Render_WriteVertex2FCmd
                LD   HL, Market_MkBar_DL           ; полоса слайдера
                LD   BC, Market_MkBar_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, MK_BAR_VX
                LD   (RenderPathVertexX), HL
                LD   HL, MK_BAR_VY
                LD   (RenderPathVertexY), HL
                CALL Render_WriteVertex2FCmd
                ; ползунок: x = MK_SLIDER_X0 + qty*187/max (pos <= 187)
                LD   HL, (MarketMax)
                LD   A, H
                OR   L
                RET  Z
                LD   HL, (MarketQty)
                LD   DE, 187
                CALL Market_Mul                    ; MkMul24 = qty*187 (цикл 187)
                LD   HL, (MarketMax)
                LD   (MkDivisor), HL
                CALL Market_Div24                  ; BC = MkMul24 / MarketMax
                LD   HL, MK_SLIDER_X0
                ADD  HL, BC
                CALL Market_LogToVtx
                LD   (RenderPathVertexX), HL
                LD   HL, MK_SLIDER_Y
                CALL Market_LogToVtx
                LD   (RenderPathVertexY), HL
                LD   HL, Market_MkSlider_DL
                LD   BC, Market_MkSlider_DL_SIZE
                CALL Render_CmdBufCopy
                JP   Render_WriteVertex2FCmd

; A=ресурс, HL=vertex X: эмит SOURCE(из таблиц) + LAYOUT/SIZE 34x34 + vertex Y=MK_ICON_VY. Портит всё.
Market_EmitResIcon:
                PUSH HL
                PUSH AF
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, MarketResSrcTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = адрес lo16
                POP  AF
                LD   L, A
                LD   H, 0
                LD   BC, MarketResSrcHiTab
                ADD  HL, BC
                LD   A, (HL)                       ; hi байт
                LD   H, #01                        ; FT_BITMAP_SOURCE = cmd 0x01 : addr24
                LD   L, A
                CALL Render_CmdBufWrite32          ; HL:DE = 32-бит команда
                LD   HL, Market_ResIconLay_DL      ; LAYOUT+SIZE 34x34 (общие)
                LD   BC, Market_ResIconLay_DL_SIZE
                CALL Render_CmdBufCopy
                POP  HL
                LD   (RenderPathVertexX), HL
                LD   HL, MK_ICON_VY
                LD   (RenderPathVertexY), HL
                JP   Render_WriteVertex2FCmd

; Запасы под from-сеткой (7 чисел, центр иконки). Портит всё.
Market_DrawStocks:
                LD   B, 0
.sl:            PUSH BC
                LD   A, B
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, MarketGridOfs
                ADD  HL, DE
                LD   C, (HL)                       ; dx
                INC  HL
                LD   A, (HL)                       ; dy
                ; ResPenY = V(MK_GRID_Y + dy + 23)
                ADD  A, 23
                LD   L, A
                LD   H, 0
                LD   DE, MK_GRID_Y
                ADD  HL, DE
                CALL Market_LogToVtx
                LD   (ResPenY), HL
                ; центр X = MK_GRID_FROM_X + dx + 17
                LD   A, C
                ADD  A, 17
                LD   L, A
                LD   H, 0
                LD   DE, MK_GRID_FROM_X
                ADD  HL, DE                        ; лог. центр
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                        ; x8
                LD   C, 5
                CALL Town_Div16by8                 ; физ = лог*8/5 (DrawNumCentered ждёт ФИЗ)
                EX   DE, HL                        ; DE = центр (физ. px)
                POP  BC
                PUSH BC
                PUSH DE                            ; GetFunds клоббит DE (центр числа!)
                LD   A, B
                CALL Market_GetFunds               ; HL = запас
                POP  DE
                CALL Render_DrawNumCentered        ; HL=число, DE=центр px
                POP  BC
                INC  B
                LD   A, B
                CP   7
                JR   C, .sl
                RET

; Курсы «1/N» под to-сеткой (по выбранному from; same -> пропуск). Портит всё.
Market_DrawRates:
                LD   A, (MarketFrom)
                CP   #FF
                RET  Z
                LD   B, 0
.rl:            PUSH BC
                LD   A, (MarketFrom)
                CP   B
                JR   Z, .skip                      ; same - «n/a» не рисуем (пусто)
                LD   A, B
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, MarketGridOfs
                ADD  HL, DE
                LD   C, (HL)
                INC  HL
                LD   A, (HL)
                ADD  A, 23
                LD   L, A
                LD   H, 0
                LD   DE, MK_GRID_Y
                ADD  HL, DE
                CALL Market_LogToVtx
                LD   (ResPenY), HL
                LD   A, C
                ADD  A, 3                          ; левее центра (строка «1/N» шире числа)
                LD   L, A
                LD   H, 0
                LD   DE, MK_GRID_TO_X
                ADD  HL, DE
                CALL Market_LogToVtx
                LD   (ResPenX), HL
                LD   HL, MkSegSlash                ; «1/»
                CALL Render_DrawString
                POP  BC
                PUSH BC
                LD   A, (MarketFrom)               ; rate(from -> B)
                LD   D, A
                LD   A, B
                LD   E, A
                LD   A, D
                ADD  A, A
                ADD  A, A
                ADD  A, A
                SUB  D
                ADD  A, E
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, MarketRateTab
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                CALL Render_DrawNum                ; N от пера
.skip:          POP  BC
                INC  B
                LD   A, B
                CP   7
                JR   C, .rl
                RET

; Число qty над слайдером + «-N (ост)» / «+M (станет)» + Max/Min/Qty подписи. Портит всё.
Market_DrawTradeText:
                LD   A, (MarketFrom)
                CP   #FF
                RET  Z
                LD   A, (MarketTo)
                CP   #FF
                RET  Z
                LD   B, A
                LD   A, (MarketFrom)
                CP   B
                RET  Z
                ; Max / Min / Qty to trade (мелкие подписи)
                LD   HL, MK_QTY_VY
                LD   (ResPenY), HL
                LD   HL, (MarketQty)               ; qty по центру (512 физ)
                LD   DE, 512
                CALL Render_DrawNumCentered
                LD   HL, MK_MAX_Y0 + 2
                CALL Market_LogToVtx
                LD   (ResPenY), HL
                LD   HL, MkSegMax
                LD   DE, 504
                CALL Render_DrawStrCenteredAt
                LD   HL, MK_MIN_Y0 + 2
                CALL Market_LogToVtx
                LD   (ResPenY), HL
                LD   HL, MkSegMin
                LD   DE, 504
                CALL Render_DrawStrCenteredAt
                LD   HL, MK_INFO_VY
                LD   (ResPenY), HL
                LD   HL, MkSegQty
                LD   DE, 512
                CALL Render_DrawStrCenteredAt
                RET

MkDivisor:      DEFW 0             ; делитель Market_Div24 (MarketMax для позиции, 187 для клика)
; BC = MkMul24 / (MkDivisor) — 24/16 повторным вычитанием (частное <= ~999). Портит A,DE,HL.
Market_Div24:
                LD   BC, 0
.l:             LD   A, (MkMul24 + 2)
                OR   A
                JR   NZ, .big
                LD   HL, (MkMul24)
                LD   DE, (MkDivisor)
                OR   A
                SBC  HL, DE
                RET  C                             ; остаток < делителя → BC = частное
                LD   (MkMul24), HL
                INC  BC
                JR   .l
.big:           LD   HL, (MkMul24)
                LD   DE, (MkDivisor)
                OR   A
                SBC  HL, DE
                LD   (MkMul24), HL
                JR   NC, .nb
                LD   A, (MkMul24 + 2)
                DEC  A
                LD   (MkMul24 + 2), A
.nb:            INC  BC
                JR   .l

; --- Offer-текст рынка (ориг. ShowTradeArea): 2 строки BigFont белым от MK_MSG_X0. ---
MarketResNameTab:
                DW MkNmWood, MkNmMerc, MkNmOre, MkNmSulf, MkNmCryst, MkNmGems, MkNmGold
MkNmWood:       DEFB "wood", 0
MkNmMerc:       DEFB "mercury", 0
MkNmOre:        DEFB "ore", 0
MkNmSulf:       DEFB "sulfur", 0
MkNmCryst:      DEFB "crystal", 0
MkNmGems:       DEFB "gems", 0
MkNmGold:       DEFB "gold", 0
MkSeg1:         DEFB "I can offer you ", 0
MkSeg1u:        DEFB "1 unit of ", 0
MkSegFor:       DEFB "for ", 0
MkSegFor1:      DEFB "for 1 unit of ", 0
MkSegUnits:     DEFB " units of ", 0
MkSegDot:       DEFB ".", 0

; A=ресурс → HL=имя (null-term). Портит A,DE.
Market_ResName:
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, MarketResNameTab
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                RET

; «I can offer you %{count} for 1 unit of %{from}.» (to=gold) /
; «I can offer you 1 unit of %{to} for %{count} units of %{from}.» — 2 строки. Портит всё.
Market_DrawOfferText:
                LD   A, (MarketFrom)
                CP   #FF
                RET  Z
                LD   A, (MarketTo)
                CP   #FF
                RET  Z
                LD   B, A
                LD   A, (MarketFrom)
                CP   B
                RET  Z
                LD   HL, MK_MSG_VY                 ; строка 1
                LD   (ResPenY), HL
                LD   HL, MK_MSG_X0
                CALL Market_LogToVtx
                LD   (ResPenX), HL
                LD   HL, MkSeg1                    ; «I can offer you »
                CALL Render_DrawString
                LD   A, (MarketTo)
                CP   6
                JR   NZ, .l1res
                CALL Market_Rate                   ; gold: «…you N»
                CALL Render_DrawNum
                JR   .line2
.l1res:         LD   HL, MkSeg1u                   ; «…you 1 unit of <to>»
                CALL Render_DrawString
                LD   A, (MarketTo)
                CALL Market_ResName
                CALL Render_DrawString
.line2:         LD   HL, MK_MSG2_VY                ; строка 2
                LD   (ResPenY), HL
                LD   HL, MK_MSG_X0
                CALL Market_LogToVtx
                LD   (ResPenX), HL
                LD   A, (MarketTo)
                CP   6
                JR   NZ, .l2res
                LD   HL, MkSegFor1                 ; gold: «for 1 unit of <from>.»
                CALL Render_DrawString
                LD   A, (MarketFrom)
                CALL Market_ResName
                CALL Render_DrawString
                JR   .dot
.l2res:         LD   HL, MkSegFor                  ; «for N units of <from>.»
                CALL Render_DrawString
                CALL Market_Rate
                CALL Render_DrawNum
                LD   HL, MkSegUnits
                CALL Render_DrawString
                LD   A, (MarketFrom)
                CALL Market_ResName
                CALL Render_DrawString
.dot:           LD   HL, MkSegDot
                JP   Render_DrawString

; --- Хелперы КОЛОДЦА ---
; A=DW-индекс 0..5 → NZ если жилище построено (DW1 всегда; прочие — BuiltMask бит i). Портит A,BC,HL.
Well_DwellBuilt:
                OR   A
                JR   NZ, .chk
                LD   A, 1                          ; DW1 (Thatched Hut) построен на старте
                OR   A
                RET
.chk:           LD   C, A
                LD   B, 0
                LD   HL, BuiltMask
                LD   A, C
                CP   8
                JR   C, .b0
                INC  HL
                SUB  8
.b0:            INC  A                             ; сдвигаем бит i в C-флаг… проще маской
                LD   B, A
                LD   A, (HL)
.sh:            DEC  B
                JR   Z, .got
                RRCA
                JR   .sh
.got:           AND  1
                RET

; Открыть колодец: стрим базы (construct-область) + патчи построенных жилищ. Портит всё.
Well_Open:
                LD   HL, TownPakName
                LD   DE, MenuNameBuf
                LD   BC, 13
                LDIR
                CALL Loader_Init
                CALL Loader_Mount
                LD   HL, MenuNameBuf
                CALL Loader_OpenFile
                LD   HL, WELL_SECTOR
                CALL Loader_SeekSector
                LD   BC, WELL_SECTORS
                LD   DE, CASTLE_CONSTRUCT_RAMG & #FFFF
                LD   A, CASTLE_CONSTRUCT_RAMG >> 16
                CALL Loader_StreamToRamGAt
                LD   A, 1
                LD   (ConstructLoaded), A          ; в области — WELL
                LD   B, 0
.wp:            PUSH BC
                LD   A, B
                CALL Well_DwellBuilt
                JR   Z, .wnp
                POP  BC
                PUSH BC
                LD   A, B                          ; сектор патча секции
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, WellSecPatchSec
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                LD   H, (HL)
                LD   L, A
                CALL Loader_ApplyPatch             ; NB: клоберит IX
.wnp:           POP  BC
                INC  B
                LD   A, B
                CP   6
                JR   C, .wp
                RET

; Если в construct-области WELL → рестрим композита строительства. Портит всё.
Well_EnsureConstruct:
                LD   A, (ConstructLoaded)
                OR   A
                RET  Z
                LD   HL, TownPakName
                LD   DE, MenuNameBuf
                LD   BC, 13
                LDIR
                CALL Loader_Init
                CALL Loader_Mount
                LD   HL, MenuNameBuf
                CALL Loader_OpenFile
                LD   HL, CONSTRUCT_SECTOR
                CALL Loader_SeekSector
                LD   BC, CONSTRUCT_SECTORS
                LD   DE, CASTLE_CONSTRUCT_RAMG & #FFFF
                LD   A, CASTLE_CONSTRUCT_RAMG >> 16
                CALL Loader_StreamToRamGAt
                XOR  A
                LD   (ConstructLoaded), A
                RET

; NZ если мышь в зоне EXIT колодца. Портит A,DE,HL.
Well_ExitHit:
                LD   A, WELL_EXIT_W
                LD   (MkRectW), A
                LD   A, WELL_EXIT_H
                LD   (MkRectH), A
                LD   DE, WELL_EXIT_X0
                LD   BC, WELL_EXIT_Y0
                JP   Market_MouseInRect

; Клик по колодцу: EXIT → закрыть; секция построенного жилища → штатный найм. Портит всё.
Well_Click:
                CALL Well_ExitHit
                JR   Z, .notexit
                XOR  A
                LD   (TownWellOpen), A             ; закрыть (construct рестримится лениво)
                RET
.notexit:       CALL Input_MouseY                  ; секция: ряд = (y−1)/150 (0..2), кол = x≥314
                LD   DE, 1
                OR   A
                SBC  HL, DE
                RET  C
                LD   B, 0                          ; ряд
.rw:            LD   DE, 150
                OR   A
                SBC  HL, DE
                JR   C, .rok
                INC  B
                JR   .rw
.rok:           LD   A, B
                CP   3
                RET  NC                            ; ниже секций
                PUSH BC
                CALL Input_MouseX
                LD   DE, 314
                OR   A
                SBC  HL, DE
                POP  BC
                LD   A, B                          ; i = ряд + (кол?3:0)
                JR   C, .col0
                ADD  A, 3
.col0:          PUSH AF
                CALL Well_DwellBuilt
                JR   Z, .nb
                POP  AF
                PUSH AF                            ; доступно > 0?
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, DwellAvail
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                OR   (HL)
                JR   Z, .nb
                POP  AF                            ; открыть ШТАТНЫЙ найм для жилища A
                LD   (TownRecruitIdx), A
                XOR  A
                LD   (TownWellOpen), A             ; ориг. возвращает в well; у нас — панорама+найм
                CALL Market_EnsureRecrbkg          ; если в области найма рынок — вернуть RECRBKG
                CALL Town_RecAvail
                LD   (TownRecruitCount), DE
                RET
.nb:            POP  AF
                RET
