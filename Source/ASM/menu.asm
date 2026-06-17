                ifndef _HMM2_MENU_
                define _HMM2_MENU_
; ============================================================================
; Экран главного меню — зеркалит game_mainmenu.cpp / drawMainMenuScreen().
; Оригинал: фон ICN::HEROES[0] (640×480) + кнопки ICN::BTNSHNGL[1/5/9/13/17]
; (New Game / Load / High Scores / Credits / Quit).
;
; Ассеты (фон-куски + кнопки + палитры) извлекает menu_pack.py → generated_menu.inc
; (MenuScene_DL — готовый DL; MenuButtonZones — зоны кнопок; Menu_LoadAssets — DMA).
; Меню переиспользует RAM_G (base 0): adventure-ассеты грузятся позже, в Adventure_Enter.
;
; Координаты: hit-test в ЛОГИЧЕСКИХ 640×480 (как UI-диспетчер adventure); DL-вершины —
; в ФИЗИЧЕСКИХ 1024×768 (×1.6, уже зашито в MenuScene_DL экстрактором).
; ============================================================================

                include "generated_menu.inc"

Menu_Enter:
                LD   A, GAME_MODE_MENU
                LD   (GameMode), A
                XOR  A
                LD   (MenuClickLatch), A
                CALL Menu_LoadFromPak            ; стрим HMM2MENU.PAK с SD → RAM_G
                RET

; --- Загрузка HMM2MENU.PAK с SD в RAM_G через загрузчик ---
; Mount → OpenFile → пропустить HPAK header → стрим payload в RAM_G[0].
; Сам стрим-цикл (Loader_StreamToRamG) лежит в SLOT1: он ремапит slot2 под буфер для
; FT.WriteMem, и код в slot2 (menu.asm) исчез бы во время ремапа. Здесь — только
; подготовка (имя в slot1-буфер, Mount/OpenFile/skip) и один вызов стримера.
Menu_LoadFromPak:
                LD   HL, MenuPakName             ; имя → slot1-буфер (raw_pak ремапит slot2)
                LD   DE, MenuNameBuf
                LD   BC, 13
                LDIR
                CALL Loader_Init                 ; sd_init
                CALL Loader_Mount                ; CF=1 = ok
                RET  NC
                LD   HL, MenuNameBuf
                CALL Loader_OpenFile             ; CF=1 = ok
                RET  NC
                LD   C, RAWPAK_BUF_PAGE          ; пропустить HPAK header (сектор 0)
                LD   HL, 0
                LD   B, MENU_BODY_SECTOR
                CALL Loader_ReadSectors
                LD   BC, MENU_PAYLOAD_SECTORS    ; стрим payload → RAM_G[0]
                CALL Loader_StreamToRamG
                RET

; Опрос ввода меню. LMB с latch: один клик = одно действие; hit-test New Game.
; (Остальные кнопки — заглушка до реализации Load/Scores/Credits/Quit.)
Menu_Update:
                CALL Input_MouseLMB              ; Z=не нажато / NZ=нажато
                JR   Z, .released
                LD   A, (MenuClickLatch)
                OR   A
                RET  NZ                          ; этот клик уже обработан
                LD   A, 1
                LD   (MenuClickLatch), A
                LD   IX, MenuButtonZones         ; зона[0] = New Game
                CALL Menu_HitTestZone
                OR   A
                RET  Z                           ; мимо зоны New Game
                CALL Adventure_Enter             ; New Game → запустить adventure
                RET
.released:      XOR  A
                LD   (MenuClickLatch), A
                RET

; Menu_HitTestZone: IX → зона (x0,y0,x1,y1, по 2б, логич). Out: A=1 попал, A=0 мимо.
Menu_HitTestZone:
                CALL Input_MouseX
                LD   (UIClickX), HL
                CALL Input_MouseY
                LD   (UIClickY), HL
                LD   HL, (UIClickX)
                LD   E, (IX+0)
                LD   D, (IX+1)
                OR   A
                SBC  HL, DE                      ; mx - x0
                JR   C, .miss                    ; mx < x0
                LD   HL, (UIClickX)
                LD   E, (IX+4)
                LD   D, (IX+5)
                OR   A
                SBC  HL, DE                      ; mx - x1
                JR   NC, .miss                   ; mx >= x1
                LD   HL, (UIClickY)
                LD   E, (IX+2)
                LD   D, (IX+3)
                OR   A
                SBC  HL, DE                      ; my - y0
                JR   C, .miss                    ; my < y0
                LD   HL, (UIClickY)
                LD   E, (IX+6)
                LD   D, (IX+7)
                OR   A
                SBC  HL, DE                      ; my - y1
                JR   NC, .miss                   ; my >= y1
                LD   A, 1
                RET
.miss:          XOR  A
                RET

; Сборка кадра меню: CMD_DLSTART + готовый MenuScene_DL (фон + кнопки) из RAM_G.
Render_Menu:
                CALL Render_BeginFrameSync       ; vsync
                FT_CMD_Start
                LD   HL, #FFFF                   ; CMD_DLSTART (0xFFFFFF00): новый DL c offset 0
                LD   DE, #FF00
                CALL Render_CmdBufWrite32
                LD   HL, MenuScene_DL
                LD   BC, MenuScene_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Render_SubmitFrameDMA
                RET

                endif
