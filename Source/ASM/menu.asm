                ifndef _HMM2_MENU_
                define _HMM2_MENU_
; ============================================================================
; Экран главного меню — зеркалит game_mainmenu.cpp (drawMainMenuScreen + MainMenu loop).
; Оригинал: фон ICN::HEROES[0] (640×480) + кнопки ICN::BTNSHNGL (New Game / Load /
; High Scores / Credits / Quit) + анимированный фонарь у двери (ICN::SHNGANIM).
;
; ПО ОРИГИНАЛУ воспроизводятся:
;   - hover кнопок: при наведении кадр base+1 (в оригинале ++frame), увод → base;
;   - pressed: при зажатой ЛКМ над кнопкой кадр base+2;
;   - анимация фонаря: ICN::SHNGANIM (1+frame%39), ПРОРЕЖЕНА под RAM_G (аппаратная
;     оговорка: 39 кадров 136×180 ≈ 932 КБ не влезают в 1 МБ RAM_G вместе с фоном).
; Quit рисуется со всеми состояниями (по оригиналу), но КЛИК неактивен — на VDAC2/
; TS-Config нет программного сброса платы (аппаратное ограничение).
;
; Ассеты (фон-куски + кнопки rel/hover/pressed + фонарь + палитры) извлекает
; menu_pack.py → generated_menu.inc:
;   MenuBg_DL — статический DL фона; MenuSpritesProlog/End_DL — обрамление спрайтов;
;   MenuLanternBase_DL + MenuLanternFrameTab; MenuBtnFrameTab (3 указателя/кнопку);
;   MenuButtonZones — зоны hit-test; метаданные HMM2MENU.PAK.
; Меню переиспользует RAM_G (base 0): adventure-ассеты грузятся позже, в Adventure_Enter.
;
; Координаты: hit-test в ЛОГИЧЕСКИХ 640×480; DL-вершины — в ФИЗИЧЕСКИХ 1024×768
; (×1.6, уже зашито в DL-блоки экстрактором).
; ============================================================================

                include "generated_menu.inc"

Menu_Enter:
                LD   A, GAME_MODE_MENU
                LD   (GameMode), A
                XOR  A
                LD   (MenuClickLatch), A
                LD   (MenuLmbDown), A
                LD   (MenuLanternIdx), A
                LD   (MenuDoorHover), A
                LD   A, #FF
                LD   (MenuHoverIndex), A
                CALL Menu_LoadFromPak            ; стрим HMM2MENU.PAK с SD → RAM_G
                ; музыка меню: slot3 → страница MIDI-потока, запустить MIDI0042 (главное меню)
                LD   A, HMM2_MUSIC_PAGE
                SetPage3_A
                LD   HL, Music_MainMenu
                CALL Music_Start
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

; Опрос ввода меню (зеркалит MainMenu loop): анимация фонаря по таймеру, hover-индекс
; кнопки под мышью, pressed по ЛКМ, и клик-действие с latch.
Menu_Update:
                ; --- MIDI-музыка: slot3 на страницу потока, продвинуть на кадр ---
                LD   A, HMM2_MUSIC_PAGE
                SetPage3_A
                CALL Music_Tick
                ; --- анимация фонаря: смена кадра каждые (1<<SHIFT) гейм-кадров ---
                LD   A, (FrameCounter)
                AND  (1 << MENU_LANTERN_SHIFT) - 1
                JR   NZ, .noAnim
                LD   A, (MenuLanternIdx)
                INC  A
                CP   MENU_LANTERN_FRAMES
                JR   C, .storeIdx
                XOR  A
.storeIdx:      LD   (MenuLanternIdx), A
.noAnim:
                ; --- какая кнопка под мышью → MenuHoverIndex (#FF если ни одной) ---
                CALL Menu_ComputeHover
                ; --- наведение на зону настроек → подсветка двери (UIClickX/Y уже прочитаны) ---
                LD   IX, MenuSettingsZone
                CALL Menu_HitTestZone
                LD   (MenuDoorHover), A
                ; --- ЛКМ: pressed-состояние + клик-действие с latch ---
                CALL Input_MouseLMB              ; Z=отпущена / NZ=нажата
                JR   Z, .released
                LD   A, 1
                LD   (MenuLmbDown), A            ; зажата → hover-кнопка рисуется pressed
                LD   A, (MenuClickLatch)
                OR   A
                RET  NZ                          ; этот клик уже обработан
                LD   A, 1
                LD   (MenuClickLatch), A
                LD   A, (MenuHoverIndex)
                CP   #FF
                RET  Z                           ; клик мимо кнопок
                OR   A                           ; индекс 0 = New Game
                RET  NZ                          ; Load/HighScores/Credits/Quit — пока заглушка
                CALL Adventure_Enter             ; New Game → запустить adventure
                RET
.released:      XOR  A
                LD   (MenuLmbDown), A
                LD   (MenuClickLatch), A
                RET

; Menu_ComputeHover: найти кнопку под мышью. Out: A=индекс (0..N-1) или #FF; пишет
; MenuHoverIndex. Мышь читается раз (UIClickX/Y), затем перебор зон.
Menu_ComputeHover:
                CALL Input_MouseX
                LD   (UIClickX), HL
                CALL Input_MouseY
                LD   (UIClickY), HL
                LD   IX, MenuButtonZones
                LD   B, MENU_BUTTON_COUNT - 1    ; БЕЗ Quit (последняя): аппаратно неактивна →
                LD   C, 0                        ; не подсвечивается и не кликается (по решению юзера)
.loop:          PUSH BC
                CALL Menu_HitTestZone            ; A=1 попал в зону (IX)
                POP  BC
                OR   A
                JR   NZ, .hit
                LD   DE, 8                        ; следующая зона (4 слова)
                ADD  IX, DE
                INC  C
                DJNZ .loop
                LD   A, #FF
                LD   (MenuHoverIndex), A
                RET
.hit:           LD   A, C
                LD   (MenuHoverIndex), A
                RET

; Menu_HitTestZone: IX → зона (x0,y0,x1,y1, по 2б, логич.). Использует готовые
; UIClickX/UIClickY (мышь прочитана вызывающим). Out: A=1 попал, A=0 мимо.
Menu_HitTestZone:
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

; Сборка кадра меню: CMD_DLSTART + фон + фонарь (база+анимкадр) + кнопки (rel/hover/
; pressed по состоянию) + глобальный курсор. DL строится динамически в CMD-буфере.
; ВАЖНО (frame pacing, см. Чат.txt 2026-06-17 «cursor pacing fix»): НЕ ждать vsync
; ДО сборки. Иначе на тяжёлом меню-кадре фаза DLSWAP «плавает» относительно refresh
; FT812 → инерция/дёрганье курсора. Сборка идёт свободно (в Z80-staging), затем
; Render_SwapFrameDMA ждёт FT_INT_SWAP ПЕРЕД DMA+DLSWAP → фаза свапа фиксирована.
; В RAM_G меню не пишет (статично с Menu_Enter), поэтому ранний sync не нужен.
Render_Menu:
                FT_CMD_Start
                LD   HL, #FFFF                   ; CMD_DLSTART (0xFFFFFF00): новый DL с offset 0
                LD   DE, #FF00
                CALL Render_CmdBufWrite32
                ; фон (статический пролог + opaque-палитра + тайлы)
                LD   HL, MenuBg_DL
                LD   BC, MenuBg_DL_SIZE
                CALL Render_CmdBufCopy
                ; обрамление спрайтов: transparent-палитра + BEGIN BITMAPS
                LD   HL, MenuSpritesProlog_DL
                LD   BC, MenuSpritesProlog_DL_SIZE
                CALL Render_CmdBufCopy
                ; фонарь: статичная база
                LD   HL, MenuLanternBase_DL
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
                ; фонарь: текущий кадр анимации (MenuLanternIdx)
                LD   A, (MenuLanternIdx)
                LD   L, A
                LD   H, 0
                ADD  HL, HL                      ; idx*2 (слово)
                LD   DE, MenuLanternFrameTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                     ; DE = адрес 16-байтного DL-блока
                EX   DE, HL
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
                ; подсветка двери (поверх фонаря) при наведении на зону настроек
                LD   A, (MenuDoorHover)
                OR   A
                JR   Z, .noDoor
                LD   HL, MenuDoor_DL
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
.noDoor:
                ; кнопки (rel/hover/pressed по состоянию)
                CALL Menu_RenderButtons
                ; конец спрайтов
                LD   HL, MenuSpritesEnd_DL
                LD   BC, MenuSpritesEnd_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Render_GlobalCursor         ; курсор по raw-мыши (CURSOR_DL содержит DISPLAY)
                CALL Render_SwapFrameDMA         ; vsync ПЕРЕД DMA+DLSWAP — фаза свапа = refresh, не build
                RET

; Дорисовка кнопок: для каждой кнопки i выбрать кадр по состоянию и скопировать его
; 16-байтный DL-блок. state: 0=released; 1=hover (i==MenuHoverIndex); 2=pressed
; (hover И MenuLmbDown). Указатель = MenuBtnFrameTab[(i*3 + state)].
Menu_RenderButtons:
                LD   B, MENU_BUTTON_COUNT
                LD   C, 0                        ; индекс кнопки
.loop:
                LD   A, (MenuHoverIndex)
                CP   C
                JR   NZ, .rel                    ; не под мышью → released
                LD   A, (MenuLmbDown)
                OR   A
                JR   Z, .hov                     ; наведено без нажатия → hover
                LD   A, 2                        ; нажато → pressed
                JR   .haveState
.hov:           LD   A, 1
                JR   .haveState
.rel:           XOR  A
.haveState:
                ; offset слова = (i*3 + state) * 2
                PUSH BC
                LD   E, A                        ; state
                LD   A, C
                ADD  A, A
                ADD  A, C                        ; i*3
                ADD  A, E                        ; + state
                ADD  A, A                        ; *2 (слово-указатель)
                LD   L, A
                LD   H, 0
                LD   DE, MenuBtnFrameTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                     ; DE = адрес 16-байтного DL-блока
                EX   DE, HL
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
                POP  BC
                INC  C
                DJNZ .loop
                RET

                endif
