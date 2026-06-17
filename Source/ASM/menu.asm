                ifndef _HMM2_MENU_
                define _HMM2_MENU_
; ============================================================================
; Экран главного меню — зеркалит game_mainmenu.cpp / drawMainMenuScreen().
; Оригинал: фон ICN::HEROES[0] (640×480) + кнопки ICN::BTNSHNGL[1/5/9/13/17]
; (New Game / Load / High Scores / Credits / Quit), pressed = +2.
;
; ШАГ 1 (каркас, этот файл): фон-заливка + одна зона New Game (заглушка) +
; переход в adventure по клику. Назначение — проверить ДИСПЕТЧЕР СЦЕН
; (GameMode-ветвление Update/Render, ленивый Adventure_Enter) до того, как
; грузить тяжёлый фон HEROES/PAK. Реальные ассеты — следующим подшагом.
;
; Координаты: hit-test в ЛОГИЧЕСКИХ 640×480 (как UI-диспетчер adventure,
; сравнение с UI_RADAR_X=480); DL-вершины — в ФИЗИЧЕСКИХ 1024×768 (×1.6=×8/5).
; ============================================================================

; Зона кнопки New Game в логических координатах 640×480 (заглушка, ~центр-низ).
; Реальная зона придёт из offset спрайта BTNSHNGL[1] на подшаге ассетов.
MENU_NG_X0     EQU 440
MENU_NG_Y0     EQU 200
MENU_NG_X1     EQU 610
MENU_NG_Y1     EQU 250
MENU_SCALE_N   EQU 8             ; ×1.6 = ×8/5 (логическое → физическое)
MENU_SCALE_D   EQU 5

Menu_Enter:
                LD   A, GAME_MODE_MENU
                LD   (GameMode), A
                XOR  A
                LD   (MenuClickLatch), A
                RET

; Опрос ввода меню. LMB с latch: один клик = одно действие; hit-test New Game.
Menu_Update:
                CALL Input_MouseLMB              ; Z=не нажато / NZ=нажато
                JR   Z, .released
                LD   A, (MenuClickLatch)
                OR   A
                RET  NZ                          ; этот клик уже обработан
                LD   A, 1
                LD   (MenuClickLatch), A
                ; --- hit-test зоны New Game (логические координаты) ---
                CALL Input_MouseX                ; HL = x
                LD   DE, MENU_NG_X0
                OR   A
                SBC  HL, DE
                RET  C                           ; x < X0 → мимо
                LD   DE, MENU_NG_X1 - MENU_NG_X0
                OR   A
                SBC  HL, DE
                RET  NC                          ; x >= X1 → мимо
                CALL Input_MouseY                ; HL = y
                LD   DE, MENU_NG_Y0
                OR   A
                SBC  HL, DE
                RET  C                           ; y < Y0 → мимо
                LD   DE, MENU_NG_Y1 - MENU_NG_Y0
                OR   A
                SBC  HL, DE
                RET  NC                          ; y >= Y1 → мимо
                ; попадание → New Game → запустить adventure (ленивая загрузка)
                CALL Adventure_Enter
                RET
.released:      XOR  A
                LD   (MenuClickLatch), A
                RET

; Сборка кадра меню. RAM_G не трогаем (фон/ассетов пока нет) — только DL.
Render_Menu:
                CALL Render_BeginFrameSync       ; vsync
                FT_CMD_Start
                LD   HL, #FFFF                   ; CMD_DLSTART (0xFFFFFF00): копроцессор
                LD   DE, #FF00                   ; начинает новый DL c RAM_DL offset 0
                CALL Render_CmdBufWrite32
                LD   HL, MenuDL_Stub
                LD   BC, MenuDL_Stub_SIZE
                CALL Render_CmdBufCopy
                CALL Render_SubmitFrameDMA
                RET

; Статический DL-блок меню-заглушки: тёмный фон + прямоугольник зоны New Game.
MenuDL_Stub:
                FT_CLEAR_COLOR_RGB 30, 24, 16
                FT_CLEAR 1, 1, 1
                FT_COLOR_RGB 184, 144, 64
                FT_BEGIN FT_RECTS
                FT_VERTEX2F MENU_NG_X0*MENU_SCALE_N/MENU_SCALE_D*16, MENU_NG_Y0*MENU_SCALE_N/MENU_SCALE_D*16
                FT_VERTEX2F MENU_NG_X1*MENU_SCALE_N/MENU_SCALE_D*16, MENU_NG_Y1*MENU_SCALE_N/MENU_SCALE_D*16
                FT_END
                FT_COLOR_RGB 255, 255, 255
                FT_DISPLAY
MenuDL_Stub_SIZE EQU $ - MenuDL_Stub

                endif
