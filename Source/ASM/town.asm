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
                CALL Input_MouseLMB               ; NZ = нажато
                JR   NZ, .pressed
                XOR  A
                LD   (TownExitLatch), A            ; отпущено → сбросить latch; A=0 (выхода нет)
                RET
.pressed:       LD   A, (TownExitLatch)
                OR   A
                JR   Z, .exit
                XOR  A                             ; клик ещё «зажат» → A=0
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
                CALL Render_GlobalCursor          ; курсор (содержит DISPLAY)
                CALL Render_SwapFrameDMA          ; vsync перед DMA+DLSWAP
                RET
