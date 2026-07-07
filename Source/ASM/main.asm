; ============================================================================
; Каркас порта Open HMM2 для TS-Config / VDAC2 FT812.
; ============================================================================

                DEVICE ZXSPECTRUM4096
                define MAPPING_REGISTERS
                ; define DBG_BOOT_ADVENTURE       ; DEBUG-boot прямо в adventure ОТКЛЮЧЁН: отладка только на РАБОЧЕМ билде
                                                  ; (реальный поток меню→New Game→Adventure_Enter), чтобы не плодить баги «промежуточного стека».

EntryPoint      EQU #5000
StackTop        EQU #BFFF
FrameCounter    EQU #4200
InputState      EQU #4202
GameMode        EQU #4203
CursorTileX     EQU #4204
CursorTileY     EQU #4205
CursorMoveCooldown EQU #4206
CursorLastMouseX EQU #4207
CursorLastMouseY EQU #4209
CursorPixelX    EQU #420B
CursorPixelY    EQU #420D
HeroPixelX      EQU #420F
HeroPixelY      EQU #4211
HeroTileX       EQU #4213
HeroTileY       EQU #4214
HeroTargetX     EQU #4215
HeroTargetY     EQU #4216
HeroMoveCooldown EQU #4217
HeroFireLatch   EQU #4218
HeroMoveFrameGate EQU #4219
ViewportOriginX EQU #421A
ViewportOriginY EQU #421B
ViewportPixelX  EQU #421C
ViewportPixelY  EQU #421E
HeroStepX       EQU #4220
HeroStepY       EQU #4221
HeroFacingRight EQU #4222
HeroPathLen    EQU #4223
HeroPathIndex  EQU #4224
PathQueueHead  EQU #4225
PathQueueTail  EQU #4227
PathCurrentX   EQU #4229
PathCurrentY   EQU #422A
PathTargetX    EQU #422B
PathTargetY    EQU #422C
PathFound      EQU #422D
PathParentCode EQU #422E
PathWorkRestorePage EQU #422F
PathMoveMask   EQU #4230
PathCurrentCost EQU #4231
PathNewCost    EQU #4233
PathPenalty    EQU #4235
PathTempX      EQU #4237
PathTempY      EQU #4238
PathFromFlags  EQU #4239
PathToFlags    EQU #423A
PathState      EQU #423B
PathStepBudget EQU #423C
PathDebugLen   EQU #423D
PathDebugLenHi EQU #423E
CursorSpriteIndex EQU #423F
CursorInGameArea EQU #4240
UIClickX       EQU #4241        ; временные координаты клика для UI-диспетчера (2б)
UIClickY       EQU #4243        ; (2б)
HeroMovePoints EQU #4245        ; очки передвижения героя (в тайлах, 0..MAX); End Turn пополняет
GameDay        EQU #4246        ; счётчик дня (1-based, 2б)
; Ресурсы королевства — ЕДИНАЯ КАЗНА (Kingdom::Funds): 7×DW ПОДРЯД в порядке cost-вектора
; fheroes2 (gold,wood,mercury,ore,sulfur,crystal,gems) — город адресует вектором
; (KingdomGold/KingdomRes6 EQU сюда), карта — по именам. Gold 2б (кламп 65535 — в
; скирмише недостижимо; было 3б).
KingdomFunds   EQU #4248
ResGold        EQU #4248        ; 2б
ResWood        EQU #424A        ; 2б
ResMercury     EQU #424C        ; 2б
ResOre         EQU #424E        ; 2б
ResSulfur      EQU #4250        ; 2б
ResCrystal     EQU #4252        ; 2б
ResGems        EQU #4254        ; 2б  (до #4255)
GameDifficulty EQU #4256        ; сложность 0..4 (безопасная зона, не под стеком загрузчика)
; Снимок состояния города в GlobalData #91 (город — оверлей, рестримится каждый вход):
; #91:GLOBAL_STATE_BASE = магия GSTATE_MAGIC, +1.. = перс-блок города (TownPersist, town.asm).
GSTATE_MAGIC   EQU #A5
GSTATE_LEN     EQU 68           ; ASSERT в town.asm сверяет с фактической длиной блока
GSTATE_OFS_STATUE EQU 30        ; смещение BuiltRuntime[CONSTRUCT_STATUE_SLOT] в блоке (доход +250)
; --- Мультиигровость (враги): kingdom AI-игрока Sorc в #91 после блока города ---
; SKIRMISH: игрок Knight (index0, казна KingdomFunds резидент), Sorc = AI (index1, казна здесь в #91).
AI_KINGDOM_OFS      EQU 1 + GSTATE_LEN            ; offset в #91 от GLOBAL_STATE_BASE (после магии+город)
AI_KINGDOM_GOLD_OFS EQU AI_KINGDOM_OFS            ; Sorc gold 2б
AI_KINGDOM_LEN      EQU 2                          ; пока только казна-золото (нарастает: замок/герой)
MenuClickLatch EQU #4258        ; latch LMB в меню (1 клик = 1 действие)
MenuNameBuf    EQU #4259        ; slot1-буфер имени PAK (14б, #4259..#4266) для loader
MenuHoverIndex EQU #4267        ; индекс кнопки под мышью (#FF=нет) — hover-подсветка по оригиналу
MenuLmbDown    EQU #4268        ; 1=LMB зажат над hover-кнопкой → pressed-кадр (base+2)
MenuLanternIdx EQU #4269        ; текущий кадр анимации фонаря SHNGANIM (0..MENU_LANTERN_FRAMES-1)
MenuDoorHover  EQU #426A        ; 1=мышь над зоной настроек → подсветка двери (SHNGANIM[18]+пал.8)
MusicActive    EQU #426B        ; 1=играет MIDI-трек (SAM2695 через AY)
MusicWait      EQU #426C        ; кадров до следующего MIDI-события
MusicPtr       EQU #426D        ; текущая позиция в покадровом потоке (2б)
MusicStart     EQU #426F        ; начало потока — для зацикливания (2б)
UI_ActiveButton  EQU #4272       ; индекс кнопки, на которой было начато нажатие ЛКМ (#FF=нет)
UI_ButtonPressed EQU #4273       ; индекс кнопки, которая визуально нажата в данный момент (#FF=нет)
UI_ButtonStates  EQU #4274       ; 8 байт (состояния кнопок панели: 0=Normal, 2=Inactive, 3=Disabled)
UI_HeroMoveButtonState EQU UI_ButtonStates + 1
UI_EndTurnButtonState  EQU UI_ButtonStates + 4
HeroWalkActive   EQU #427C       ; 1 = герой шагает по маршруту, 0 = ждёт команды (клик/кнопка)
StatusState      EQU #427D        ; вид статус-окна (клик переключает, как в оригинале)
BattleSpeedSetting EQU #427E      ; скорость боя 1..10 (Settings; вне диапазона → дефолт 4);
                                  ; живёт в резиденте — battle-оверлей рестримится каждый бой
                                  ; (#427F свободен)
; Порядок = клик-цикл оригинала NextStatus при фокус-герое (interface_status.cpp:188-204):
; ARMY → DATE(DAY) → FUNDS → ARMY. INC-wrap StatusState 0→1→2→0 даёт ровно этот порядок.
STATUS_ARMY      EQU 0            ; армия фокус-героя (MONS32 + счётчики) — ДЕФОЛТ
STATUS_DATE      EQU 1            ; счётчик дней (день/неделя/месяц)
STATUS_FUNDS     EQU 2            ; ресурсы королевства (RESSMALL + числа)
STATUS_STATE_COUNT EQU 3          ; ARMY / DATE / FUNDS
HeroPathXBuf   EQU #4300
HeroPathYBuf   EQU #4360
PathDebugXBuf  EQU #EF30
PathDebugYBuf  EQU #F440
ResolutionWidthPtr   EQU #41F3
ResolutionHeightPtr  EQU #41F5
InterruptVA          EQU #4000
TSLibPage       EQU #00
CorePage        EQU #05
ScaleTablePage  EQU #12
PathWorkPage    EQU #13
ActiveHeroIndex EQU #426D
                define CMD_ADDRESS_PTR #B000    ; DL-staging буфер (frame_max #0FFC; #B000+#0FFC=#BFFC≤StackTop). Поднят под резидентные трамплины town-оверлея. Реальный DL кадра ≪4КБ, стек не достаёт.
                ; Сдвинут до #AA00: резидент дорос (диспетчер + menu.asm hover/pressed/фонарь +
                ; generated_menu.inc: MenuBg_DL/кнопки×3/13 кадров фонаря/таблицы/зоны). Потолок
                ; #B070 (+#0F90 = #B990 < #C000, не пересекает slot3). TODO: меню-DL/загрузчик в
                ; overlay при упоре в потолок.
                ; TODO: вынести MinimapTileColorTable (1296Б)/PickupList в paged при упоре.
HMM2_SIGNAL_CANARY EQU 0                         ; 1 = только Init_Video и чёрный экран для проверки сигнала

                include "../../Docs/TSLib/Include/TSConf.inc"
                include "../../Docs/TSLib/Include/Memory/Include.inc"
                include "../../Docs/TSLib/Include/Cache/Macro.inc"
                include "../../Docs/TSLib/Include/Video/Macro.inc"
                include "../../Docs/TSLib/Include/INT/Macro.inc"
                include "../../Docs/TSLib/Include/System/Macro.inc"
                include "../../Docs/TSLib/Include/FT/DL  Macro.inc"
                include "../../Docs/TSLib/Include/FT/812 Macro.inc"

                ORG EntryPoint
                JP   Start

                include "../../Docs/TSLib/Include/FT/81x Const.inc"
                include "../../Docs/TSLib/Include/Input/Include.inc"

Start:
                DI
                ; До первого CALL выставляем slot2 под страницу стека.
                ; Иначе CALL Platform_Init кладёт return address в старую
                ; page2, а SetPage2 внутри Platform_Init делает RET в мусор.
                FMapAddrInit
                System_Setting SYS_ZCLK14 | SYS_CACHEEN
                Cache_Setting  EN_0000 | EN_4000 | EN_8000
                SetPage1 CorePage
                SetPage2 CorePage + 1
                LD   SP, StackTop

                CALL Platform_Init
                if HMM2_SIGNAL_CANARY
.signal_hold:   JR   .signal_hold
                endif
                CALL Input.Mouse.Initialize
                CALL Input_Init
                CALL Game_Init

MainLoop:
                ; Vsync-ожидание перенесено ВНУТРЬ Render_Frame (Render_SwapFrameDMA,
                ; непосредственно перед DMA-отправкой): input/update/сборка кадра
                ; идут, пока показывается предыдущий кадр, а свап армируется сразу
                ; после vsync. Ожидание в начале цикла сдвигало армирование на конец
                ; сборки — на тяжёлых кадрах (скролл) свап проскакивал границу
                ; кадра (74↔37 Гц) → дёргался курсор/герой/скролл.
                CALL Input_Poll
                CALL Game_Update
                CALL Render_Frame
                JP   MainLoop

                ; --- Резидентные trampolines к PAK-loader (В SLOT1, #5xxx) ----------
                ; Загрузчик (sd_zc+raw_pak) в overlay-странице HMM2_LOADER_PAGE (slot3).
                ; Trampolines: мапят overlay в slot3, переключают SP на локальный стек
                ; загрузчика (slot1 — raw_pak ремапит slot2 и сломал бы основной стек на
                ; #BFFF), вызывают RawPak_*, восстанавливают Core. ОБЯЗАНЫ быть в slot1:
                ; raw_pak ремапит slot2, и код трамплина в slot2 исчез бы во время вызова
                ; (RET ушёл бы в мусор-страницу буфера — корень «висло до FT812»).
Loader_Init:                                     ; sd_init (byte addressing + dummy clocks)
                LD   (LdSavedSP), SP
                LD   SP, LdStackTop
                CALL Loader_MapIn
                CALL sd_init
                JR   Loader_Leave
Loader_Mount:
                LD   (LdSavedSP), SP
                LD   SP, LdStackTop
                CALL Loader_MapIn
                CALL RawPak_Mount
                JR   Loader_Leave
Loader_OpenFile:                                 ; HL = имя файла (zero-term)
                LD   (LdSavedSP), SP
                LD   SP, LdStackTop
                CALL Loader_MapIn
                CALL RawPak_OpenFile
                JR   Loader_Leave
Loader_ReadSectors:                              ; C=dst page, HL=dst off, B=count
                LD   (LdSavedSP), SP
                LD   SP, LdStackTop
                CALL Loader_MapIn
                CALL RawPak_ReadSectors
                JR   Loader_Leave
Loader_SeekSector:                               ; HL = логический сектор файла (RawPak_LogCur)
                LD   (LdSavedSP), SP
                LD   SP, LdStackTop
                PUSH HL
                CALL Loader_MapIn
                POP  HL
                LD   (RawPak_LogCur), HL
                JR   Loader_Leave
Loader_Leave:                                    ; CF результата raw_pak сохранён
                PUSH AF
                LD   A, CorePage + 1
                SetPage2_A                       ; raw_pak менял slot2 → вернуть Core
Loader_SavedP3 EQU $+1
                LD   A, #00
                SetPage3_A
                POP  AF
                LD   SP, (LdSavedSP)             ; вернуть основной стек (slot2 #BFFF)
                RET
Loader_MapIn:
                ; SetPage3_A (через A), НЕ SetPage3 (через HL) — Loader_OpenFile передаёт
                ; имя файла в HL, а макрос SetPage3 портит HL (LD HL,FMADDR_REGS...).
                GetPage3
                LD   (Loader_SavedP3), A
                LD   A, HMM2_LOADER_PAGE
                SetPage3_A
                RET

; Loader_StreamToRamGAt — как StreamToRamG, но цель задана: A=RAM_G байт2, DE=байты0-1.
; (ПКМ-попап ArmyInfo → область финального окна; рестрим финала из payload-куска.)
Loader_StreamToRamGAt:
                LD   (LdStreamRamgLo), DE
                LD   (LdStreamRamgHi), A
                LD   (LdStreamRemain), BC
                JR   Loader_StreamCommon
; Loader_StreamToRamG — стрим открытого файла (с текущей позиции) в RAM_G[0] чанками
; по 32 сектора. Вход: BC = число секторов. ДОЛЖНА быть в slot1: цикл делает
; SetPage2_A(buffer) под FT.WriteMem, и код в slot2 исчез бы во время ремапа.
; Состояние тоже в slot1. КРИТИЧНО (Zuma): весь чанк сначала с SD, потом весь DMA.
Loader_StreamToRamG:
                LD   (LdStreamRemain), BC
                LD   HL, 0
                LD   (LdStreamRamgLo), HL
                XOR  A
                LD   (LdStreamRamgHi), A
Loader_StreamCommon:
.loop:          LD   BC, (LdStreamRemain)
                LD   A, B
                OR   C
                JR   NZ, .chunk                  ; ещё есть данные
                ; Стрим окончен: за секунды без Input_Scan PS/2 FIFO переполнился —
                ; break-коды потеряны, латчи клавиш ЗАЛИПАЮТ (ловилось: AltGr=1 →
                ; попап «по hover»). Дренаж мусора + сброс латчей.
                CALL Input_DiscardPS2Fifo
                JP   Input_ClearState
.chunk:
                LD   A, B                        ; chunk = min(32, remain) → B
                OR   A
                JR   NZ, .full
                LD   A, C
                CP   32
                JR   NC, .full
                LD   B, C
                JR   .read
.full:          LD   B, 32
.read:          PUSH BC
                LD   C, RAWPAK_BUF_PAGE
                LD   HL, 0
                CALL Loader_ReadSectors          ; чанк с SD в buffer-page (восстанавливает slot2)
                POP  BC
                LD   A, RAWPAK_BUF_PAGE
                SetPage2_A                       ; buffer-page в slot2 для FT.WriteMem
                PUSH BC
                LD   H, B
                LD   L, 0
                ADD  HL, HL                      ; HL = B*512 (байт чанка)
                LD   B, H
                LD   C, L
                LD   HL, #8000
                LD   A, (LdStreamRamgHi)
                LD   DE, (LdStreamRamgLo)
                CALL FT.WriteMem
                LD   A, CorePage + 1
                SetPage2_A                       ; вернуть Core
                POP  BC                          ; B = sector count
                LD   H, B                        ; advance RAM_G dst += B*512
                LD   L, 0
                ADD  HL, HL
                LD   DE, (LdStreamRamgLo)
                ADD  HL, DE
                LD   (LdStreamRamgLo), HL
                JR   NC, .nocy
                LD   A, (LdStreamRamgHi)
                INC  A
                LD   (LdStreamRamgHi), A
.nocy:          LD   HL, (LdStreamRemain)        ; remain -= B
                LD   A, L
                SUB  B
                LD   L, A
                JR   NC, .nobor
                DEC  H
.nobor:         LD   (LdStreamRemain), HL
                JR   .loop
LdStreamRemain: DEFW 0
LdStreamRamgLo: DEFW 0
LdStreamRamgHi: DEFB 0

; ----------------------------------------------------------------------------
; Loader_ApplyPatch — применить ПАТЧ из HMM2TOWN.PAK в RAM_G (строительство по
; оригиналу: спрайты зданий на панораму / полосы статусов в окно стройки).
; IN: HL = абсолютный логический сектор патча в файле (PanoPatchSec/BandPatchSec/
; CornerPatchSec). Формат потока (сектор-локальные записи, см. town_pack._pack_patch):
;   [len u16][addr u24][len байт]; len=0 → следующий сектор; len=#FFFF → конец.
; Каждый сектор: Loader_ReadSectors → буфер (slot2) → FT.WriteMem ранов.
; Живёт в SLOT1 (raw_pak ремапит slot2). CF=1 = ok.
; ----------------------------------------------------------------------------
Loader_ApplyPatch:
                LD   (LdPatchSec), HL
                LD   HL, LdPatchName             ; имя в slot1 (оверлеи в slot2/3 недоступны при ремапе)
                CALL Loader_OpenFile             ; CF=1 = ok (Seek0 + run-table)
                RET  NC
                LD   HL, (LdPatchSec)
                CALL Loader_SeekSector           ; LogCur = сектор патча
.sector:        LD   C, RAWPAK_BUF_PAGE          ; сектор потока → буфер-страница
                LD   HL, 0
                LD   B, 1
                CALL Loader_ReadSectors          ; CF=1 = ОШИБКА (конвенция RawPak_ReadSectors)
                JR   C, .fail
                LD   A, RAWPAK_BUF_PAGE
                SetPage2_A                       ; буфер в окно slot2 для FT.WriteMem
                LD   IX, #8000                   ; курсор потока в секторе
.rec:           LD   E, (IX+0)
                LD   D, (IX+1)                   ; DE = len записи
                LD   A, D
                AND  E
                INC  A
                JR   Z, .done                    ; len = #FFFF → конец патча
                LD   A, D
                OR   E
                JR   Z, .next_sector             ; len = 0 → следующий сектор
                LD   (LdPatchLen), DE
                LD   L, (IX+2)
                LD   H, (IX+3)
                LD   (LdPatchLo), HL             ; RAM_G адрес lo16
                LD   A, (IX+4)
                LD   (LdPatchHi), A              ; RAM_G адрес hi
                PUSH IX
                POP  HL
                LD   DE, 5
                ADD  HL, DE                      ; HL = данные рана (в буфере slot2)
                LD   A, (LdPatchHi)
                LD   DE, (LdPatchLo)
                LD   BC, (LdPatchLen)
                CALL FT.WriteMem                 ; ран → RAM_G
                LD   A, RAWPAK_BUF_PAGE          ; WriteMem мог вернуть Core в slot2 — буфер обратно
                SetPage2_A
                PUSH IX
                POP  HL
                LD   DE, (LdPatchLen)
                ADD  HL, DE
                LD   DE, 5
                ADD  HL, DE                      ; IX += 5 + len
                PUSH HL
                POP  IX
                JR   .rec
.next_sector:   LD   A, CorePage + 1
                SetPage2_A                       ; вернуть Core перед raw_pak (он ремапит сам)
                JR   .sector
.done:          LD   A, CorePage + 1
                SetPage2_A                       ; вернуть Core в slot2
                SCF
                RET
.fail:          LD   A, CorePage + 1
                SetPage2_A
                OR   A
                RET
LdPatchSec:     DEFW 0
LdPatchLen:     DEFW 0
LdPatchLo:      DEFW 0
LdPatchHi:      DEFB 0
LdPatchName:    DEFB "HMM2TOWN.PAK", 0

                include "platform_tsconf.asm"
                include "Init_Video.asm"
                include "input.asm"
                include "assets.inc"
                include "game_state.asm"

                module FT
                include "../../Docs/TSLib/Include/FT/812 Func.asm"
                include "../../Docs/TSLib/Include/FT/Coprocessor/Include.inc"
                endmodule

                include "render.asm"
                include "generated_runtime_map.inc"
                include "generated_map_anim.inc"
                ; menu.asm и town.asm — в ОВЕРЛЕЙ-страницах (slot3), не в резиденте (ядро полно).
                ; Резидент держит только их трамплины (Menu_*_Tramp/Town_*_Tramp). См. блоки оверлеев ниже.
                include "music.asm"         ; MIDI-плеер (SAM2695 через AY port A)

                ; Trampolines загрузчика перенесены ВЫШЕ (после MainLoop) — должны быть в
                ; slot1 (#5000-#7FFF): они вызывают raw_pak, который ремапит slot2; если бы
                ; сами лежали в slot2 (Core перерос #8000), код трамплина исчез бы во время
                ; ремапа и RET ушёл бы в мусор-страницу. EQU-константы — здесь:
HMM2_LOADER_PAGE EQU #A0                          ; overlay-страница загрузчика (slot3)
RAWPAK_BUF_PAGE  EQU #A1                          ; dir/sector buffer raw_pak (slot2)
HMM2_MUSIC_PAGE  EQU #A9                          ; overlay-страница покадрового MIDI-потока (slot3); #A2..#A5 — курсоры, #A6/#A8 — сцены
HMM2_HISCORES_PAGE EQU #AA                        ; оверлей high scores (#A5 занял курсор p03)
HMM2_TOWN_PAGE   EQU #A6                          ; overlay-страница сцены города (town.asm, slot3)
HMM2_MENU_PAGE   EQU #A7                          ; overlay-страница главного меню (menu.asm, slot3)
HMM2_BATTLE_PAGE EQU #A8                          ; overlay-страница сцены боя (battle.asm, slot3)
GLOBAL_DATA_PAGE EQU #91                          ; ГЛОБАЛЬНЫЕ ДАННЫЕ (data-страница, мапится в slot3-окно):
                                                  ; ref-таблицы (статы монстров) + растущее глоб.состояние
                                                  ; (королевство/герои/замки/армии). Доступ — резидентный хелпер
                                                  ; (map #91→slot3, читать, restore slot3), как loader. НЕ в оверлей сцены!
LdSavedSP       EQU #4278                         ; slot1: сохранённый основной SP (2б)
LdStackTop      EQU #4300                         ; slot1: вершина стека загрузчика (#4280..#42FF)

; ============================================================================
; Trampolines для High Scores и музыки
; ============================================================================
Music_Tick_Tramp:
                GetPage3
                PUSH AF
                LD   A, HMM2_MUSIC_PAGE
                SetPage3_A
                CALL Music_Tick
                POP  AF
                SetPage3_A
                RET

HiScores_EnterStandard_Tramp:
                LD   A, HMM2_HISCORES_PAGE
                LD   (ScnOvlPage), A
                LD   A, SCN_HISC_SECTOR
                LD   (ScnOvlSkip), A
                CALL Scene_LoadOverlay            ; стрим hiscores.asm в #A5 из HMM2SCN.PAK
                GetPage3
                PUSH AF
                LD   A, HMM2_HISCORES_PAGE
                SetPage3_A
                CALL HiScores_EnterStandard
                POP  AF
                SetPage3_A
                RET

HiScores_Update_Tramp:                            ; HiScores_Update вернёт A=0 (остаться) / 1 (выход в меню)
                GetPage3
                PUSH AF
                LD   A, HMM2_HISCORES_PAGE
                SetPage3_A
                CALL HiScores_Update
                POP  BC                            ; B = сохранённая страница slot3
                LD   C, A                          ; C = код действия
                LD   A, B
                SetPage3_A                         ; вернуть прежний slot3
                LD   A, C
                OR   A
                RET  Z                             ; 0 → остаться в High Scores
                CALL Render_BlackFrame             ; 1 → выход: чёрный кадр (резидент)
                JP   Menu_Enter_Tramp              ; → меню (маппит #A7)

Render_HiScores_Tramp:
                GetPage3
                PUSH AF
                LD   A, HMM2_HISCORES_PAGE
                SetPage3_A
                CALL Render_HiScores
                POP  AF
                SetPage3_A
                RET

; --- Резидентные трамплины СЦЕН-ОВЕРЛЕЕВ (menu/town в slot3) ---
; Общий хелпер Scene_RunOvl: B=страница-оверлей, HL=процедура в нём. Мапит оверлей в slot3,
; CALL(HL), восстанавливает slot3, возвращает A=результат процедуры. Резидент — не выгружается.
Scene_RunOvl:
                GetPage3                          ; A = текущая страница slot3
                PUSH AF                           ; [page|flags] на стек
                LD   A, B
                SetPage3_A                        ; мапим целевой оверлей
                CALL .jphl                        ; A = результат процедуры
                POP  BC                           ; B = сохранённая страница
                LD   C, A                          ; C = результат
                LD   A, B
                SetPage3_A                        ; вернуть прежний slot3
                LD   A, C
                RET
.jphl:          JP   (HL)
; --- Город (town.asm в HMM2_TOWN_PAGE) ---
Town_Enter_Tramp:
                CALL Render_BlackFrame            ; чёрный кадр (резидент, ДО перезаписи RAM_G)
                LD   A, HMM2_TOWN_PAGE
                LD   (ScnOvlPage), A
                LD   A, SCN_TOWN_SECTOR
                LD   (ScnOvlSkip), A
                CALL Scene_LoadOverlay            ; стрим town.asm в #A6 из HMM2SCN.PAK
                LD   B, HMM2_TOWN_PAGE
                LD   HL, Town_Enter
                JP   Scene_RunOvl
Render_Town_Tramp:
                LD   B, HMM2_TOWN_PAGE
                LD   HL, Render_Town
                JP   Scene_RunOvl
Town_Update_Tramp:                                ; Town_Update вернёт A=1 если запрошен выход
                LD   B, HMM2_TOWN_PAGE
                LD   HL, Town_Update
                CALL Scene_RunOvl
                OR   A
                RET  Z
                LD   A, 1                         ; возврат из города: сохранить героя/день/ресурсы
                LD   (AdvReenter), A
                JP   Adventure_Enter              ; выход: назад на карту (резидент)
; --- Бой (battle.asm в HMM2_BATTLE_PAGE) ---
Battle_Enter_Tramp:
                CALL Render_BlackFrame            ; чёрный кадр (резидент, ДО перезаписи RAM_G)
                LD   A, HMM2_BATTLE_PAGE
                LD   (ScnOvlPage), A
                LD   A, SCN_BATTLE_SECTOR
                LD   (ScnOvlSkip), A
                CALL Scene_LoadOverlay            ; стрим battle.asm в #A8 из HMM2SCN.PAK
                LD   B, HMM2_BATTLE_PAGE
                LD   HL, Battle_Enter
                JP   Scene_RunOvl
Render_Battle_Tramp:
                LD   B, HMM2_BATTLE_PAGE
                LD   HL, Render_Battle
                JP   Scene_RunOvl
Battle_Update_Tramp:                              ; Battle_Update вернёт A=1 если запрошен выход
                LD   B, HMM2_BATTLE_PAGE
                LD   HL, Battle_Update
                CALL Scene_RunOvl
                OR   A
                RET  Z
                JP   Adventure_Enter              ; выход: назад на карту (резидент)

; --- Стрим ОВЕРЛЕЯ сцены (код) в его slot3-страницу из HMM2SCN.PAK (как карта из HMM2MAP) ---
; IN: (ScnOvlPage)=целевая страница (#A6/#A8/#A5), (ScnOvlSkip)=body-сектор оверлея в PAK.
; В slot1 (loader ремапит slot2). Зовётся ТОЛЬКО из Enter-трамплинов (Update/Render не нужно —
; оверлей уже в странице, она не клоберится: карта=#20-8F, курсор=#A2/3, буфер=#A1).
Scene_LoadOverlay:
                LD   HL, ScnPakName
                LD   DE, MenuNameBuf
                LD   BC, 13
                LDIR
                CALL Loader_Init
                CALL Loader_Mount
                RET  NC
                LD   HL, MenuNameBuf
                CALL Loader_OpenFile
                RET  NC
                LD   A, (ScnOvlSkip)              ; пропустить header+предыдущие оверлеи
                CALL Scene_Skip
                LD   A, (ScnOvlPage)              ; целевая страница оверлея
                LD   C, A
                LD   B, SCN_OVL_SECTORS           ; 32 сектора = 16КБ = полная страница
                LD   HL, 0
                CALL Loader_ReadSectors          ; оверлей с SD → страница C
                RET
Scene_Skip:                                      ; A = секторов пропустить (в buffer, чанками ≤32)
.sk:            OR   A
                RET  Z
                LD   B, 32
                CP   32
                JR   NC, .full
                LD   B, A
.full:          PUSH AF                          ; сохранить остаток (raw_pak клоберит A/B)
                PUSH BC                          ; сохранить размер чанка
                LD   C, RAWPAK_BUF_PAGE
                LD   HL, 0
                CALL Loader_ReadSectors
                POP  BC
                POP  AF
                SUB  B
                JR   .sk
ScnOvlPage:     DB   0
ScnOvlSkip:     DB   0
                include "generated_scn_stream.inc"

; Мост adventure→сцена (резидент): клик по тайлу = ВЕСТИ героя к нему. Вход в замок (24,13) / бой
; (22,13) — ПО ПРИБЫТИИ героя на тайл (Hero_SelectStepIfArrived), а НЕ мгновенно по клику издалека
; (по оригиналу fheroes2: вход = шаг героя на тайл-действие, не клик).
Adventure_GameAreaClick:
                JP   Hero_CommandTargetFromMouse
; --- Меню (menu.asm в HMM2_MENU_PAGE) ---
Menu_Enter_Tramp:
                LD   B, HMM2_MENU_PAGE
                LD   HL, Menu_Enter
                JP   Scene_RunOvl
Render_Menu_Tramp:
                LD   B, HMM2_MENU_PAGE
                LD   HL, Render_Menu
                JP   Scene_RunOvl
Menu_Update_Tramp:                                ; Menu_Update вернёт A=0/1=NewGame/2=HiScores
                LD   B, HMM2_MENU_PAGE
                LD   HL, Menu_Update
                CALL Scene_RunOvl
                OR   A
                RET  Z                            ; 0 → ничего
                DEC  A
                JP   Z, Adventure_Enter           ; 1 → New Game
                JP   HiScores_EnterStandard_Tramp ; 2 → High Scores

; --- Чтение статов монстра из глоб-страницы #91 (GLOBAL_DATA_PAGE) ---
; B = индекс монстра (0=Unknown, 1=Peasant, 2=Archer, …). Мапит #91 в slot3, копирует
; 10 байт (atk,def,dmin,dmax,hpLo,hpHi,spd,shots,strLo,strHi) из MonsterStats[B*10] в
; MonsterStatBuf (резидент slot1), восстанавливает slot3. str = GetMonsterStrength×16
; (фикс-точка, для AI analyzeBattleState: Unit::GetStrength = str×count).
MonsterStats_Read:
                GetPage3
                PUSH AF                           ; сохранить прежнюю slot3-страницу
                LD   A, GLOBAL_DATA_PAGE
                SetPage3_A                        ; #91 → slot3 (#C000)
                LD   L, B
                LD   H, 0
                ADD  HL, HL                       ; B*2
                LD   D, H
                LD   E, L                         ; DE = B*2
                ADD  HL, HL                       ; B*4
                ADD  HL, HL                       ; B*8
                ADD  HL, DE                       ; HL = B*10
                LD   DE, MonsterStats             ; #C000 в странице #91
                ADD  HL, DE                       ; HL = &MonsterStats[B*10]
                LD   DE, MonsterStatBuf
                LD   BC, 10                        ; MONSTER_STAT_SIZE
                LDIR                              ; копировать 10 байт статов
                POP  AF
                SetPage3_A                        ; вернуть прежний slot3
                RET
MonsterStatBuf: DEFS 10                           ; статы прочитанного монстра (резидент slot1 RAM)
; A = байт GLOBAL_DATA-страницы (#91) по адресу HL (#C000-based). Для КОДА В SLOT3 (город!):
; резидент свапает slot3 на #91, читает, восстанавливает. Портит B,F.
GData_ReadByte:
                GetPage3
                LD   B, A                          ; прежняя страница slot3
                PUSH HL                            ; ★SetPage3 <const> в MAPPING-режиме ПОРТИТ HL!
                SetPage3 GLOBAL_DATA_PAGE
                POP  HL
                LD   A, (HL)
                PUSH AF
                LD   A, B
                SetPage3_A
                POP  AF
                RET
; --- Снимок состояния города (персистентность: оверлей города рестримится каждый вход) ---
; Протокол: town-код (slot3) копирует перс-блок ↔ TownStateBuf (нижняя RAM видна всегда),
; резидентные хелперы переносят буфер ↔ #91:GLOBAL_STATE_BASE (город при мапе #91 невидим!).
TownStateBuf:   DEFS GSTATE_LEN
; Записать буфер в #91 + магия. Портит A,BC,DE,HL.
GState_Commit:
                GetPage3
                PUSH AF
                SetPage3 GLOBAL_DATA_PAGE
                LD   HL, TownStateBuf
                LD   DE, GLOBAL_STATE_BASE + 1
                LD   BC, GSTATE_LEN
                LDIR
                LD   A, GSTATE_MAGIC
                LD   (GLOBAL_STATE_BASE), A
                POP  AF
                SetPage3_A
                RET
; Прочитать снимок в буфер. OUT: A=1 снимок есть / A=0 нет. Портит A,BC,DE,HL.
GState_Fetch:
                GetPage3
                PUSH AF
                SetPage3 GLOBAL_DATA_PAGE
                LD   A, (GLOBAL_STATE_BASE)
                CP   GSTATE_MAGIC
                JR   NZ, .none
                LD   HL, GLOBAL_STATE_BASE + 1
                LD   DE, TownStateBuf
                LD   BC, GSTATE_LEN
                LDIR
                LD   C, 1
                JR   .done
.none:          LD   C, 0
.done:          POP  AF
                SetPage3_A
                LD   A, C
                RET
; Сбросить снимок (новая игра). Портит A,B.
GState_Reset:
                GetPage3
                LD   B, A
                XOR  A
                PUSH HL                            ; ★SetPage3 <const> ПОРТИТ HL
                SetPage3 GLOBAL_DATA_PAGE
                POP  HL
                LD   (GLOBAL_STATE_BASE), A
                LD   A, B
                SetPage3_A
                RET

; --- AI-королевство Sorc (враг, мультиигровость): казна в #91 ---
; Доход хода AI: Sorc gold += 1000 (замок). Портит A,DE,HL. Вызывать раз в ход (Game_EndTurn).
AiKingdom_EndTurn:
                GetPage3
                PUSH AF
                SetPage3 GLOBAL_DATA_PAGE          ; портит HL — грузим HL ПОСЛЕ
                LD   HL, GLOBAL_STATE_BASE + AI_KINGDOM_GOLD_OFS
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = Sorc gold
                PUSH HL                            ; HL = адрес high-байта
                LD   HL, 1000
                ADD  HL, DE                        ; +1000 доход замка
                JR   NC, .nc
                LD   HL, #FFFF                     ; кламп 65535
.nc:            EX   DE, HL                        ; DE = новое золото
                POP  HL                            ; HL = адрес high-байта
                LD   (HL), D
                DEC  HL
                LD   (HL), E                       ; записали 2б
                POP  AF
                SetPage3_A
                RET
; Init казны AI (новая игра): Sorc gold = стартовое золото (ResStartTab[diff], как у игрока).
; Вызывать ПОСЛЕ Resources_InitStart (KingdomFunds уже = стартовое). Портит A,DE,HL.
AiKingdom_Init:
                LD   DE, (KingdomFunds)            ; стартовое золото (общее для всех по difficulty)
                GetPage3
                PUSH AF
                SetPage3 GLOBAL_DATA_PAGE
                LD   HL, GLOBAL_STATE_BASE + AI_KINGDOM_GOLD_OFS
                LD   (HL), E
                INC  HL
                LD   (HL), D                       ; Sorc gold = стартовое
                POP  AF
                SetPage3_A
                RET

; Отладочное зеркало боя для statedump (эмулятор дампит страницы 5/6; оверлей боя в slot3 не виден).
; Battle_Render копирует сюда состояние каждый кадр: units(20) + startCnt(8) + result(1).
DbgBattleMirror: DEFS 41           ; +33..40: дебаг меч-курсора {dirW, dx16, dy16, dirC, hover, active}

CoreEnd:
                ASSERT CoreEnd <= CMD_ADDRESS_PTR
                ASSERT CMD_ADDRESS_PTR + RUNTIME_CMD_FRAME_MAX <= StackTop
                SAVEBIN "Build/Core.bin", EntryPoint, CoreEnd - EntryPoint

                ; --- Loader overlay (АКТИВНО): sd_zc + raw_pak в page #A0 @ #C000 ---
                if 1
                SLOT 3
                PAGE HMM2_LOADER_PAGE
                ORG  #C000
LoaderOvl_Start:
                include "sd_zc.asm"
                include "raw_pak.asm"
LoaderOvl_End:
                ASSERT LoaderOvl_End <= #FFFF
                SAVEBIN "Build/loader_ovl.bin", LoaderOvl_Start, LoaderOvl_End - LoaderOvl_Start
                endif

                ; --- Music overlay (АКТИВНО): покадровый MIDI-поток меню в page #A3 @ #C000 ---
                ; Плеер (music.asm, резидент slot1) читает поток из slot3, который меню держит
                ; на HMM2_MUSIC_PAGE. Поток генерит music_pack.py из MIDI0042 (XMI→MID→stream).
                if 1
                SLOT 3
                PAGE HMM2_MUSIC_PAGE
                ORG  #C000
MusicOvl_Start:
                include "generated_music.inc"
MusicOvl_End:
                ASSERT MusicOvl_End <= #FFFF
                SAVEBIN "Build/music_ovl.bin", MusicOvl_Start, MusicOvl_End - MusicOvl_Start
                endif
                if 1
                SLOT 3
                PAGE HMM2_HISCORES_PAGE
                ORG  #C000
HiScoresOvl_Start:
                include "hiscores.asm"
HiScoresOvl_End:
                ASSERT HiScoresOvl_End <= #FFFF
                SAVEBIN "Build/hiscores_ovl.bin", HiScoresOvl_Start, HiScoresOvl_End - HiScoresOvl_Start
                endif

                ; --- Town overlay: сцена города в page HMM2_TOWN_PAGE @ #C000 ---
                if 1
                SLOT 3
                PAGE HMM2_TOWN_PAGE
                ORG  #C000
TownOvl_Start:
                include "town.asm"
TownOvl_End:
                ASSERT TownOvl_End <= #FFFF
                SAVEBIN "Build/town_ovl.bin", TownOvl_Start, TownOvl_End - TownOvl_Start
                endif

                ; --- ГЛОБАЛЬНЫЕ ДАННЫЕ: data-страница GLOBAL_DATA_PAGE @ #C000 (slot3-окно) ---
                ; Ref-таблицы (read-only, грузятся с boot) в начале; растущее мутабельное глоб.
                ; состояние (королевство/герои/замки/армии) — после, инициализируется в рантайме.
                if 1
                SLOT 3
                PAGE GLOBAL_DATA_PAGE
                ORG  #C000
GlobalData_Start:
                include "generated_monsters.inc"    ; MonsterStats @ #C000 (72×10=720Б)
                include "generated_minimap_tab.inc" ; цвета тайлов мини-карты (1296Б; вынос из резидента)
                include "generated_town_hit.inc"    ; GDTownHitMap 2.5К (вынос: оверлей города упёрся в 16К)
                include "generated_battle_speed.inc" ; наборы тик-таблиц боя per speed (210Б; бой у потолка)
GLOBAL_STATE_BASE EQU $                             ; ← мутабельное глоб.состояние начинается здесь
GlobalData_End:
                ASSERT GlobalData_End <= #FFFF
                SAVEBIN "Build/global_data.bin", GlobalData_Start, GlobalData_End - GlobalData_Start
                endif

                ; --- Menu overlay: главное меню в page HMM2_MENU_PAGE @ #C000 ---
                ; Музыку зовёт через Music_Tick_Tramp (сам мапит slot3=поток). New Game/HiScores —
                ; через код действия из Menu_Update (резидентный Menu_Update_Tramp диспатчит).
                if 1
                SLOT 3
                PAGE HMM2_MENU_PAGE
                ORG  #C000
MenuOvl_Start:
                include "menu.asm"
MenuOvl_End:
                ASSERT MenuOvl_End <= #FFFF
                SAVEBIN "Build/menu_ovl.bin", MenuOvl_Start, MenuOvl_End - MenuOvl_Start
                endif

                ; --- Battle overlay: сцена боя в page HMM2_BATTLE_PAGE @ #C000 ---
                if 1
                SLOT 3
                PAGE HMM2_BATTLE_PAGE
                ORG  #C000
BattleOvl_Start:
                include "battle.asm"
BattleOvl_End:
                ASSERT BattleOvl_End <= #FFFF
                SAVEBIN "Build/battle_ovl.bin", BattleOvl_Start, BattleOvl_End - BattleOvl_Start
                endif
