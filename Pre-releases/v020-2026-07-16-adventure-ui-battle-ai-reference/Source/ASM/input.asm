; ============================================================================
; Input.asm — РЕЗИДЕНТНЫЙ глобальный модуль ВСЕГО управления. Здесь читаются ВСЕ
; источники ввода, поэтому любая сцена-overlay (геймплей #04, UI #41) может
; опрашивать ввод без переключения страниц.
;
; Источники (всё в одном месте — клавиатура + джойстик + мышь):
;   * Расширенная PC-клавиатура ZX Evolution через Mr.Gluk Z-контроллер:
;       OUT #EFF7,#80 = enable; OUT #DFF7,рег = выбор регистра; #BFF7 = данные.
;       Регистр #F0 = PS/2 FIFO scancode'ов (set-2). Тот же чип, что и RTC
;       (VDC.ReadRTCSeconds), который ГАСИТ #EFF7 после чтения — поэтому
;       Input_Scan каждый кадр включает его заново. См. заметку памяти
;       reference_zuma_vdac2_zxevo_ps2_keyboard.
;   * Kempston-джойстик (TSLib Input.Kempston). KJoystick=1 направляет PC-стрелки
;     сюда же.
;   * Мышь (TSLib Input.Mouse) — позиция + ЛКМ.
;
; Схема управления: лягушка = вращение Влево/Вправо (геймплей). Глобальные UI:
;   Up/Down — навигация меню/выбор сложности; Влево/Вправо — активная кнопка в
;   диалогах; ESC — меню/назад; Fire = Space | Enter | Kempston-Fire | ЛКМ.
; Клавиатурные эквиваленты направлений (классическая ZX-раскладка):
;   Up = ↑ | Q;  Down = ↓ | A;  Влево = ← | O;  Вправо = → | P.
;
; Применение: Input_Init один раз на старте; Input_Scan один раз за кадр (в любой
; сцене — он обновляет и клавиатуру, и мышь); затем опросы Input_Up/Down/Left/
; Right/Fire/Esc (каждый возвращает NZ = активно). Edge-хелперы — для навигации.
; ============================================================================

; Скан-коды PS/2 set-2 (make-коды; стрелки идут с префиксом E0, но их коды
; уникальны, поэтому при сопоставлении префикс E0 игнорируется).
INP_SC_ESC      EQU #76
INP_SC_UP       EQU #75
INP_SC_DOWN     EQU #72
INP_SC_LEFT     EQU #6B
INP_SC_RIGHT    EQU #74
INP_SC_ENTER    EQU #5A
INP_SC_SPACE    EQU #29
INP_SC_Q        EQU #15
INP_SC_A        EQU #1C
INP_SC_O        EQU #44          ; O = Влево (классическая ZX-раскладка)
INP_SC_P        EQU #4D          ; P = Вправо
INP_SC_ALT      EQU #11          ; #11 c E0-префиксом = AltGr (правый Alt) = ПКМ; без E0 = левый Alt (игнор)
INP_SC_E        EQU #24          ; E = End Turn (хоткей оригинала HotKeyEvent::END_TURN)

; Флаги «клавиша нажата» (1 = нажата, 0 = отпущена), обновляются Input_Scan.
Input_KEsc:     DEFB 0
Input_KUp:      DEFB 0
Input_KDown:    DEFB 0
Input_KLeft:    DEFB 0
Input_KRight:   DEFB 0
Input_KEnter:   DEFB 0
Input_KSpace:   DEFB 0
Input_KQ:       DEFB 0
Input_KA:       DEFB 0
Input_KO:       DEFB 0
Input_KP:       DEFB 0
Input_KAlt:     DEFB 0          ; AltGr (E0 11) — виртуальная ПКМ (инфо-попапы)
Input_KE:       DEFB 0          ; E — End Turn (новый день, adventure)
Input_PS2Brk:   DEFB 0          ; ожидается префикс отпускания (#F0)
Input_PS2Ext:   DEFB 0          ; видел префикс #E0 (extended) — различает AltGr от левого Alt
Input_DrainCnt: DEFB 0          ; ограничитель дренажа FIFO (макс байт за скан)

; ----------------------------------------------------------------------------
; Input_Init — включить Mr.Gluk и взвести PS/2-клавиатуру. Вызвать раз на старте.
; ----------------------------------------------------------------------------
Input_Init:
                CALL Input_ClearState
                LD   BC, #EFF7 : LD A, #80 : OUT (C), A    ; Mr.Gluk enable
                LD   BC, #DFF7 : LD A, #0C : OUT (C), A
                LD   BC, #BFF7 : LD A, #01 : OUT (C), A    ; сброс буфера PS/2
                LD   BC, #DFF7 : LD A, #F0 : OUT (C), A
                LD   BC, #BFF7 : LD A, #02 : OUT (C), A    ; PS/2 ON
                CALL Input_DiscardPS2Fifo
                CALL Input_ClearState
                RET

Input_ClearState:
                XOR  A
                LD   (InputState), A
                LD   (Input_KEsc), A
                LD   (Input_KUp), A
                LD   (Input_KDown), A
                LD   (Input_KLeft), A
                LD   (Input_KRight), A
                LD   (Input_KEnter), A
                LD   (Input_KSpace), A
                LD   (Input_KQ), A
                LD   (Input_KA), A
                LD   (Input_KO), A
                LD   (Input_KP), A
                LD   (Input_KAlt), A
                LD   (Input_KE), A
                LD   (Input_PS2Brk), A
                LD   (Input_PS2Ext), A
                LD   (Input_DrainCnt), A
                RET

Input_DiscardPS2Fifo:
                LD   BC, #EFF7 : LD A, #80 : OUT (C), A
                LD   BC, #DFF7 : LD A, #F0 : OUT (C), A
                LD   A, 64
                LD   (Input_DrainCnt), A
                LD   BC, #BFF7
.drain:         IN   A, (C)
                OR   A
                RET  Z
                LD   A, (Input_DrainCnt)
                DEC  A
                LD   (Input_DrainCnt), A
                JR   NZ, .drain
                RET

; ----------------------------------------------------------------------------
; Input_Scan — опросить ВСЕ источники за кадр: дренаж PS/2 FIFO (флаги клавиш) +
; обновление состояния мыши. Вызывать раз за кадр в любой сцене.
; Сначала заново включает Mr.Gluk (чтение RTC его гасит). Портит AF, BC, DE, HL.
; ----------------------------------------------------------------------------
Input_Scan:
                CALL Input.Mouse.UpdateMouseState          ; мышь — единая точка опроса здесь
                LD   BC, #EFF7 : LD A, #80 : OUT (C), A    ; заново enable (RTC мог погасить)
                LD   BC, #DFF7 : LD A, #F0 : OUT (C), A    ; выбрать регистр PS/2 FIFO
                LD   A, 24 : LD (Input_DrainCnt), A        ; ограничить дренаж (без зависания на мусоре)
                LD   BC, #BFF7                             ; BC = порт данных (держим на весь цикл)
.drain:         IN   A, (C)
                OR   A : RET Z                             ; 0 = FIFO пуст -> готово
                CP   #FF : JR Z, .overflow                 ; переполнение: break-коды ПОТЕРЯНЫ -> сброс латчей
                CP   #E0 : JR Z, .set_ext                  ; префикс extended -> взвести флаг (AltGr vs Alt)
                CP   #F0 : JR Z, .set_brk                  ; префикс break -> следующий код = отпускание
                CALL Input_SetKey
.next:          LD   A, (Input_DrainCnt) : DEC A : LD (Input_DrainCnt), A : RET Z
                JR   .drain
.set_brk:       LD   A, 1 : LD (Input_PS2Brk), A
                JR   .next
.set_ext:       LD   A, 1 : LD (Input_PS2Ext), A           ; E0 приходит ПЕРЕД F0 (отпускание: E0 F0 xx)
                JR   .next
.overflow:      CALL Input_ClearState                      ; потеряны отпускания -> иначе клавиши ЗАЛИПАЮТ
                JR   .next                                 ; (ловилось: AltGr залип -> попап «по hover»)

; A = scancode -> выставить/сбросить его флаг (1 если make, 0 если break),
; затем съесть префикс break. Сохраняет BC (порт дренажа #BFF7). Портит AF, DE, HL.
Input_SetKey:
                LD   E, A                                  ; E = scancode
                LD   A, (Input_PS2Brk)
                XOR  1                                     ; A = 1 (make) или 0 (break)
                LD   D, A                                  ; D = значение для записи
                XOR  A : LD (Input_PS2Brk), A              ; съесть префикс break
                LD   A, E
                CP   INP_SC_ALT       : JR Z, .alt         ; #11: AltGr (с E0) / левый Alt (без) — раздельно
                LD   HL, Input_KEsc   : CP INP_SC_ESC   : JR Z, .sk
                LD   HL, Input_KUp    : CP INP_SC_UP    : JR Z, .sk
                LD   HL, Input_KDown  : CP INP_SC_DOWN  : JR Z, .sk
                LD   HL, Input_KLeft  : CP INP_SC_LEFT  : JR Z, .sk
                LD   HL, Input_KRight : CP INP_SC_RIGHT : JR Z, .sk
                LD   HL, Input_KEnter : CP INP_SC_ENTER : JR Z, .sk
                LD   HL, Input_KSpace : CP INP_SC_SPACE : JR Z, .sk
                LD   HL, Input_KQ     : CP INP_SC_Q     : JR Z, .sk
                LD   HL, Input_KA     : CP INP_SC_A     : JR Z, .sk
                LD   HL, Input_KO     : CP INP_SC_O     : JR Z, .sk
                LD   HL, Input_KP     : CP INP_SC_P     : JR Z, .sk
                LD   HL, Input_KE     : CP INP_SC_E     : JR Z, .sk
                JR   .eat_ext                              ; неотслеживаемый код (съесть E0-флаг)
.sk:            LD   (HL), D
.eat_ext:       XOR  A : LD (Input_PS2Ext), A              ; реальный код съедает E0-префикс
                RET
.alt:           LD   A, (Input_PS2Ext)
                OR   A
                JR   Z, .eat_ext                           ; БЕЗ E0 = левый Alt → игнор
                LD   HL, Input_KAlt                        ; С E0 = AltGr → виртуальная ПКМ
                JR   .sk

; ----------------------------------------------------------------------------
; Опросы направлений/огня — возвращают NZ = активно (Z = нет). Объединяют все
; источники по схеме управления. Портят AF (Kempston/мышь также HL).
; ----------------------------------------------------------------------------
Input_Esc:      LD   A, (Input_KEsc) : OR A : RET           ; только клавиатура (у Kempston ESC нет)

Input_Up:       LD   A, (Input_KUp) : OR A : RET NZ         ; ↑ (PS/2)
                LD   A, (Input_KQ)  : OR A : RET NZ         ; Q
                LD   A, Input.VK_KEMPSTON_UP
                JP   Input.Kempston.KeyState               ; Kempston-Up (NZ = нажато)

Input_Down:     LD   A, (Input_KDown) : OR A : RET NZ       ; ↓ (PS/2)
                LD   A, (Input_KA)    : OR A : RET NZ       ; A
                LD   A, Input.VK_KEMPSTON_DOWN
                JP   Input.Kempston.KeyState

Input_Left:     LD   A, (Input_KLeft) : OR A : RET NZ       ; ← (PS/2)
                LD   A, (Input_KO)    : OR A : RET NZ       ; O
                LD   A, Input.VK_KEMPSTON_LEFT
                JP   Input.Kempston.KeyState

Input_Right:    LD   A, (Input_KRight) : OR A : RET NZ      ; → (PS/2)
                LD   A, (Input_KP)     : OR A : RET NZ      ; P
                LD   A, Input.VK_KEMPSTON_RIGHT
                JP   Input.Kempston.KeyState

; Input_FireKey — огонь БЕЗ ЛКМ: Space | Enter | Kempston-Fire. Для сцен, где ЛКМ
; обрабатывается отдельно (лягушка-aim, hit-test диалогов) — иначе ЛКМ дала бы
; двойной огонь. NZ = нажато.
Input_FireKey:  LD   A, (Input_KSpace) : OR A : RET NZ      ; Space
                LD   A, (Input_KEnter) : OR A : RET NZ      ; Enter
                LD   A, Input.VK_KEMPSTON_B
                JP   Input.Kempston.KeyState               ; Kempston-Fire (NZ = нажато)

; Input_Fire — полный огонь: Input_FireKey + ЛКМ. Для сцен без отдельного
; hit-test'а (напр. выход из More Games — любой ввод = огонь). NZ = нажато.
Input_Fire:     CALL Input_FireKey : RET NZ                 ; Space|Enter|Kempston
                ; fall through to Input_MouseLMB

; ----------------------------------------------------------------------------
; Input_EdgeZ — детектор фронта нажатия (для навигации меню/диалогов: одно
; действие на одно нажатие, без автоповтора при удержании).
; Вход: флаг Z = состояние клавиши СЕЙЧАС (Z = отпущена, NZ = нажата),
;       HL = адрес байта «было нажато в прошлом кадре» (0/1).
; Выход: NZ = фронт (0->1, только что нажали), Z = фронта нет. Обновляет (HL).
; Портит A. Вызывать СРАЗУ после Input_Up/Down/Left/Right/FireKey/Esc —
; промежуточный «LD HL, addr» флаги не трогает, поэтому Z доходит сюда целым.
; ----------------------------------------------------------------------------
Input_EdgeZ:    JR   Z, .released
                LD   A, (HL)                               ; было нажато?
                LD   (HL), 1                               ; запомнить «нажато»
                XOR  1                                     ; было 0 -> A=1 (фронт, NZ); было 1 -> A=0 (Z)
                RET
.released:      LD   (HL), 0                               ; отпущено -> сброс
                XOR  A                                     ; Z = фронта нет
                RET

; ----------------------------------------------------------------------------
; Доступ к мыши (единая точка; позиция обновляется в Input_Scan).
;   Input_MouseX / Input_MouseY -> HL = координата.
; ----------------------------------------------------------------------------
Input_MouseX:   LD   HL, (Input.Mouse.PositionX) : RET
Input_MouseY:   LD   HL, (Input.Mouse.PositionY) : RET

; Input_MouseLMB -> NZ = ЛКМ нажата, Z = отпущена.
; ОРИГИНАЛ (восстановлено): Kempston-mouse active-LOW — в покое mbuttons=0xFF (бит=1),
; при нажатии бит сбрасывается в 0. KeyState делает AND маски с портом; CP SVK_LBUTTON:
; Z=бит выставлен(отпущена), NZ=бит сброшен(нажата). Мой прежний JP-вариант (active-high)
; был НЕВЕРЕН — ломал клик. Подтверждено эмулятором bt8xxemu (idle 0xFF).
; Fire (Space|Enter|Kempston) ВЛИВАЕТСЯ в ЛКМ: клавиатура/джойстик = виртуальная мышь,
; все сцены (меню/город/бой) видят «клик» без пер-сценных правок.
Input_MouseLMB: CALL Input_FireKey
                RET  NZ                                    ; Fire держится → «ЛКМ нажата»
                LD   A, Input.Mouse.SVK_LBUTTON
                CALL Input.Mouse.KeyState
                CP   Input.Mouse.SVK_LBUTTON
                RET

; Input_MouseRMB -> NZ = ПКМ нажата, Z = отпущена. Та же active-LOW семантика, что у LMB
; (порт #FADF, бит SVK_RBUTTON=%010). Для right-click инфо-попапов (castle_dialog.cpp).
; AltGr ВЛИВАЕТСЯ в ПКМ (инфо-попапы с клавиатуры — у Kempston/мыши-заменителя ПКМ нет).
Input_MouseRMB: LD   A, (Input_KAlt)
                OR   A
                RET  NZ                                    ; AltGr держится → «ПКМ нажата»
                LD   A, Input.Mouse.SVK_RBUTTON
                CALL Input.Mouse.KeyState
                CP   Input.Mouse.SVK_RBUTTON
                RET

; ----------------------------------------------------------------------------
; Input_Poll — компактное состояние для HMM2 adventure map.
; Биты InputState:
;   0 = влево, 1 = вправо, 2 = вверх, 3 = вниз,
;   4 = огонь/подтверждение, 5 = отмена, 6 = ЛКМ.
; ----------------------------------------------------------------------------
Input_Poll:
                CALL Input_Poll_Build
                JP   Input_VirtualCursor         ; стрелки/Kempston двигают ГЛОБАЛЬНУЮ мышь (все сцены)
Input_Poll_Build:
                CALL Input_Scan
                XOR  A
                LD   (InputState), A

                CALL Input_Left
                JR   Z, .right
                LD   A, (InputState)
                OR   %00000001
                LD   (InputState), A

.right:         CALL Input_Right
                JR   Z, .up
                LD   A, (InputState)
                OR   %00000010
                LD   (InputState), A

.up:            CALL Input_Up
                JR   Z, .down
                LD   A, (InputState)
                OR   %00000100
                LD   (InputState), A

.down:          CALL Input_Down
                JR   Z, .fire
                LD   A, (InputState)
                OR   %00001000
                LD   (InputState), A

.fire:          CALL Input_FireKey
                JR   Z, .mouse_fire
                LD   A, (InputState)
                OR   %00010000
                LD   (InputState), A
                JR   .esc

.mouse_fire:
                CALL Input_MouseLMB
                JR   Z, .esc
                LD   A, (InputState)
                OR   %01010000
                LD   (InputState), A

.esc:           CALL Input_Esc
                RET  Z
                LD   A, (InputState)
                OR   %00100000
                LD   (InputState), A
                RET

; ----------------------------------------------------------------------------
; Input_VirtualCursor — ОДНА ГЛОБАЛЬНАЯ процедура (та же, что двигала курсор в
; adventure): стрелки клавиатуры / Kempston двигают Input.Mouse.PositionX/Y.
; Клава/джойстик неотличимы от мыши: Render_GlobalCursor, хит-тесты всех сцен
; (меню/город/бой/adventure Cursor_UpdateFromMouse) видят обычную мышь.
; Fire=ЛКМ (Input_MouseLMB), AltGr=ПКМ (Input_MouseRMB). Клампы 0..639/0..479.
; ----------------------------------------------------------------------------
INP_VCURSOR_STEP EQU 5           ; px/кадр — как CURSOR_STEP_PIXELS в adventure
Input_VirtualCursor:
                LD   A, (InputState)
                AND  %00001111
                RET  Z                           ; направлений нет
                LD   B, A
                ; --- X: влево (бит0) / вправо (бит1) ---
                LD   HL, (Input.Mouse.PositionX)
                BIT  0, B
                JR   Z, .vright
                LD   DE, INP_VCURSOR_STEP
                OR   A
                SBC  HL, DE
                JR   NC, .vstorex
                LD   HL, 0
                JR   .vstorex
.vright:        BIT  1, B
                JR   Z, .vy
                LD   DE, INP_VCURSOR_STEP
                ADD  HL, DE
                PUSH HL
                LD   DE, 639
                OR   A
                SBC  HL, DE
                POP  HL
                JR   C, .vstorex                 ; < 639 → ок
                LD   HL, 639
.vstorex:       LD   (Input.Mouse.PositionX), HL
.vy:            ; --- Y: вверх (бит2) / вниз (бит3) ---
                LD   HL, (Input.Mouse.PositionY)
                BIT  2, B
                JR   Z, .vdown
                LD   DE, INP_VCURSOR_STEP
                OR   A
                SBC  HL, DE
                JR   NC, .vstorey
                LD   HL, 0
                JR   .vstorey
.vdown:         BIT  3, B
                RET  Z
                LD   DE, INP_VCURSOR_STEP
                ADD  HL, DE
                PUSH HL
                LD   DE, 479
                OR   A
                SBC  HL, DE
                POP  HL
                JR   C, .vstorey                 ; < 479 → ок
                LD   HL, 479
.vstorey:       LD   (Input.Mouse.PositionY), HL
                RET
