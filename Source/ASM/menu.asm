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

MenuScreen:     DEFB 0            ; 0 = главное меню, 1 = подменю NEW GAME, 2 = экран сценария
ScenHelpShow:   DEFB #FF          ; ПКМ-справка scenario: #FF=нет, 0..6=индекс окна (пока ПКМ зажат)
ScenHelpDirty:  DEFB 0            ; справка стрималась в #090BC4 (перекрыла кнопки/кадры) → Cancel рестримит

Menu_Enter:
                LD   A, GAME_MODE_MENU
                LD   (GameMode), A
                XOR  A
                LD   (MenuClickLatch), A
                LD   (MenuLmbDown), A
                LD   (MenuLanternIdx), A
                LD   (MenuDoorHover), A
                LD   (MenuScreen), A
                ; [ИЗОЛЯЦИЯ: init убран]
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
; OUT: A = действие (0=нет, 1=New Game, 2=High Scores). Резидентный Menu_Update_Tramp диспатчит
; (menu.asm в ОВЕРЛЕЕ slot3 — нельзя звать Adventure_Enter/HiScores отсюда, slot3-edge).
Menu_Update:
                ; --- MIDI-музыка: Music_Tick_Tramp сам мапит slot3=поток и восстанавливает (меню в slot3) ---
                CALL Music_Tick_Tramp
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
                LD   A, (MenuScreen)             ; 1=подменю NEW GAME, 2=экран сценария
                CP   2
                JP   Z, MenuScen_Update
                OR   A
                JP   NZ, MenuNg_Update
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
                JR   NZ, .none                   ; этот клик уже обработан → действие 0
                LD   A, 1
                LD   (MenuClickLatch), A
                LD   A, (MenuHoverIndex)
                CP   #FF
                JR   Z, .none                    ; клик мимо кнопок → 0
                OR   A                           ; индекс 0 = New Game
                JR   Z, .act_newgame
                CP   2                           ; индекс 2 = High Scores (internal [9])
                JR   Z, .act_hiscores
.none:          XOR  A                           ; Load/Credits/Quit заглушка → действие 0
                RET
.act_newgame:   LD   A, 1                        ; New Game → ПОДМЕНЮ (ориг.: Standard/Campaign/…)
                LD   (MenuScreen), A
                LD   A, #FF
                LD   (MenuHoverIndex), A
                XOR  A                           ; остаёмся в меню (действие 0)
                RET
.act_hiscores:  LD   A, 2                        ; → резидент зовёт HiScores
                RET
.released:      XOR  A
                LD   (MenuLmbDown), A
                LD   (MenuClickLatch), A
                XOR  A                           ; действие 0
                RET

; --- Подменю NEW GAME (game_newgame.cpp 1.0.0): Standard → старт игры; Campaign/Multi —
; контента нет (кампании/мультиплеера в порте нет — клик пуст); Cancel → главное меню.
; Кнопки BTNNEWGM: released/pressed (hover-кадров у ассета нет — по оригиналу).
; OUT: A = действие (0=нет, 1=New Game старт).
MenuNg_Update:
                CALL Input_MouseX                ; hover NG-кнопки → MenuHoverIndex
                LD   (UIClickX), HL
                CALL Input_MouseY
                LD   (UIClickY), HL
                LD   IX, MenuNgZones
                LD   B, MENU_NG_BUTTON_COUNT
                LD   C, 0
.zloop:         PUSH BC
                CALL Menu_HitTestZone
                POP  BC
                OR   A
                JR   NZ, .zhit
                LD   DE, 8
                ADD  IX, DE
                INC  C
                DJNZ .zloop
                LD   A, #FF                      ; ни одной
                JR   .zstore
.zhit:          LD   A, C
.zstore:        LD   (MenuHoverIndex), A
                CALL Input_MouseLMB
                JR   Z, .ngreleased
                LD   A, 1
                LD   (MenuLmbDown), A
                LD   A, (MenuClickLatch)
                OR   A
                JR   NZ, .ngnone
                LD   A, 1
                LD   (MenuClickLatch), A
                LD   A, (MenuHoverIndex)
                CP   #FF
                JR   Z, .ngnone
                OR   A                           ; 0 = Standard Game → старт
                JR   Z, .ngstandard
                CP   3                           ; 3 = Cancel → главное меню
                JR   Z, .ngcancel
.ngnone:        XOR  A                           ; Campaign/Multi: контента нет → пусто
                RET
.ngstandard:    CALL Menu_LoadScenario           ; Standard → экран выбора сценария (стрим в base 0)
                LD   A, 2
                LD   (MenuScreen), A
                LD   A, #FF
                LD   (MenuHoverIndex), A
                XOR  A                           ; остаёмся в меню
                RET
.ngcancel:      CALL Menu_LoadFromPak            ; восстановить кадры фонаря (панель scenario их заняла);
                XOR  A                           ; рестрим ТОГО ЖЕ меню → HEROES идентичен, кадры #064840 не
                LD   (MenuScreen), A             ; читаются подменю-DL (фонарь статичен) → без мусора
                LD   A, #FF
                LD   (MenuHoverIndex), A
                XOR  A
                RET
.ngreleased:    XOR  A
                LD   (MenuLmbDown), A
                LD   (MenuClickLatch), A
                XOR  A
                RET

; --- Экран выбора сценария (ChooseNewMap): клик по иконке сложности → GameDifficulty;
; OKAY → старт игры (действие 1); Cancel → назад в подменю NEW GAME (пере-стрим меню).
; OUT: A = действие (0=нет, 1=старт).
MenuScen_Update:
                CALL Input_MouseX
                LD   (UIClickX), HL
                CALL Input_MouseY
                LD   (UIClickY), HL
                ; --- ПКМ-справка (showStandardTextMessage, Dialog::ZERO): показ пока ПКМ зажат ---
                LD   A, (ScenHelpShow)
                CP   #FF
                JR   Z, .scnohelp
                CALL Input_MouseRMB              ; справка показана → держать пока ПКМ зажат
                JR   NZ, .schkeep
                LD   A, #FF                      ; отпустили → закрыть (рендер вернёт чистый scenario)
                LD   (ScenHelpShow), A
.schkeep:       XOR  A
                RET
.scnohelp:      CALL Input_MouseRMB             ; ПКМ нажата → открыть справку по зоне под курсором
                JR   Z, .scnorm
                LD   IX, ScenHelpZones
                LD   B, MENU_SCEN_HELP_COUNT
                LD   C, 0
.schscan:       PUSH BC
                CALL Menu_HitTestZone
                POP  BC
                OR   A
                JR   NZ, .schhit
                LD   DE, 8
                ADD  IX, DE
                INC  C
                DJNZ .schscan
                XOR  A                           ; ПКМ мимо зон → ничего
                RET
.schhit:        LD   A, C
                CALL Scen_HelpOpen              ; стрим окна idx @ SCEN_HELP_AREA + ScenHelpShow=idx
                XOR  A
                RET
.scnorm:        CALL Input_MouseLMB
                JR   Z, .screleased
                LD   A, 1
                LD   (MenuLmbDown), A
                LD   A, (MenuClickLatch)
                OR   A
                JR   NZ, .scnone
                LD   A, 1
                LD   (MenuClickLatch), A
                LD   IX, ScenOkZone              ; OKAY?
                CALL Menu_HitTestZone
                OR   A
                JR   NZ, .scok
                LD   IX, ScenCancelZone          ; Cancel?
                CALL Menu_HitTestZone
                OR   A
                JR   NZ, .sccancel
                LD   IX, ScenDiffZones           ; клик по иконке сложности → сменить
                LD   B, MENU_SCEN_DIFF_COUNT
                LD   C, 0
.sdloop:        PUSH BC
                CALL Menu_HitTestZone
                POP  BC
                OR   A
                JR   NZ, .sdhit
                LD   DE, 8
                ADD  IX, DE
                INC  C
                DJNZ .sdloop
.scnone:        XOR  A
                RET
.sdhit:         LD   A, C
                LD   (GameDifficulty), A
                XOR  A
                RET
.scok:          LD   A, 1                         ; OKAY → резидент зовёт Adventure_Enter (сложность выбрана)
                RET
.sccancel:      LD   A, (ScenHelpDirty)          ; справка стрималась → перекрыла кнопки/кадры → рестрим
                OR   A
                JR   Z, .sccnclean
                CALL Menu_RenderBgBase           ; фон+база (не читает #064840+) → рестрим «за кадром»
                CALL Menu_LoadFromPak            ; восстановить кнопки/кадры (HEROES идентичен → без мусора)
.sccnclean:     LD   A, 1                         ; назад в подменю NEW GAME (фонарь статичен, панель невидима)
                LD   (MenuScreen), A
                LD   A, #FF
                LD   (MenuHoverIndex), A
                XOR  A
                RET
.screleased:    XOR  A
                LD   (MenuLmbDown), A
                LD   (MenuClickLatch), A
                XOR  A
                RET

; Стрим composite экрана сценария (2-я PAK-entry HMM2MENU) в RAM_G base 0 — эксклюзивно с
; меню-payload (переход = пере-стрим, как город). Подготовка в slot1, один вызов стримера.
Menu_LoadScenario:
                LD   A, #FF                      ; сброс ПКМ-справки при входе в scenario
                LD   (ScenHelpShow), A
                XOR  A
                LD   (ScenHelpDirty), A          ; RAM_G кнопок ещё чист (справок не было)
                CALL Menu_RenderBgBase           ; показать фон+базу фонаря (кадры #064840 НЕ читаются)
                LD   HL, MenuPakName             ; → стрим панели @ #064840 «за кадром», без мусора/чёрного
                LD   DE, MenuNameBuf
                LD   BC, 13
                LDIR
                CALL Loader_Init
                CALL Loader_Mount
                RET  NC
                LD   HL, MenuNameBuf
                CALL Loader_OpenFile
                RET  NC
                LD   HL, SCEN_BODY_SECTOR        ; seek на сектор сценария (>255 → не ReadSectors)
                CALL Loader_SeekSector
                LD   BC, SCEN_PAYLOAD_SECTORS    ; панель-окно → в область кадров фонаря #064840
                LD   DE, #4840
                LD   A, #06
                JP   Loader_StreamToRamGAt

; Показать фон меню + статичную базу фонаря (БЕЗ кадров #064840) — фиксированный кадр, чтобы
; последующий стрим панели/кадров @ #064840 шёл «за кадром» (DL не читает эту область) → без мусора.
Menu_RenderBgBase:
                FT_CMD_Start
                LD   HL, #FFFF
                LD   DE, #FF00
                CALL Render_CmdBufWrite32
                LD   HL, MenuBg_DL
                LD   BC, MenuBg_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, MenuSpritesProlog_DL
                LD   BC, MenuSpritesProlog_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, MenuLanternBase_DL
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, MenuSpritesEnd_DL
                LD   BC, MenuSpritesEnd_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Render_GlobalCursor
                JP   Render_SwapFrameDMA

; ПКМ-справка scenario: стрим окна idx (A=0..6) в SCEN_HELP_AREA + ScenHelpShow=idx. Портит IX (Loader).
Scen_HelpOpen:
                LD   (ScenHelpShow), A
                LD   A, 1                        ; пометить: RAM_G кнопок/кадров перекрыт справкой
                LD   (ScenHelpDirty), A
                LD   HL, MenuPakName
                LD   DE, MenuNameBuf
                LD   BC, 13
                LDIR
                CALL Loader_Init
                CALL Loader_Mount
                RET  NC
                LD   HL, MenuNameBuf
                CALL Loader_OpenFile
                RET  NC
                LD   A, (ScenHelpShow)            ; idx → ScenHelpSecTab[idx] (сектор, DW)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                LD   DE, ScenHelpSecTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL                       ; HL = сектор
                CALL Loader_SeekSector
                LD   A, (ScenHelpShow)            ; ScenHelpSecN[idx] (сектора, DB)
                LD   L, A
                LD   H, 0
                LD   DE, ScenHelpSecN
                ADD  HL, DE
                LD   C, (HL)
                LD   B, 0                         ; BC = сектора
                LD   DE, SCEN_HELP_AREA & #FFFF
                LD   A, SCEN_HELP_AREA >> 16
                JP   Loader_StreamToRamGAt        ; окно → RAM_G @ SCEN_HELP_AREA

; Рендер ПКМ-справки поверх scenario: пролог (SOURCE=area) + окно idx + глоб. тень. IN: ScenHelpShow.
Scen_RenderHelp:
                LD   HL, ScenHelpPre_DL
                LD   BC, ScenHelpPre_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (ScenHelpShow)
                ADD  A, A                         ; ×2 (DLTab: только ptr, размер общий)
                LD   L, A
                LD   H, 0
                LD   DE, ScenHelpDLTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                PUSH DE
                EX   DE, HL                       ; HL = фрагмент окна idx
                LD   BC, SCEN_HELP_DL_SIZE
                CALL Render_WindowShadowDL        ; тень окна (глоб. процедура)
                POP  HL
                LD   BC, SCEN_HELP_DL_SIZE
                JP   Render_CmdBufCopy            ; само окно поверх тени

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
                LD   A, (MenuScreen)             ; экран сценария — свой полный кадр
                CP   2
                JP   Z, MenuScen_Render
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
                LD   A, (MenuScreen)             ; подменю NEW GAME → свой хвост кадра
                OR   A
                JP   NZ, MenuNg_Render
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

; Хвост кадра подменю NEW GAME (drawMainMenuScreen + drawButtonPanel, 1.0.0): фонарь-база
; СТАТИЧНА (в подменю не анимируется), шингл-кнопки released (панель закрывает правые),
; панель REDBACK, 4 кнопки BTNNEWGM (pressed при удержании в зоне).
MenuNg_Render:
                LD   HL, MenuLanternBase_DL      ; фонарь: только статичная база
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
                LD   B, MENU_BUTTON_COUNT        ; шингл-кнопки все released
                LD   C, 0
.sbl:           PUSH BC
                LD   A, C
                ADD  A, A
                ADD  A, C                        ; i*3 (state 0)
                ADD  A, A                        ; *2
                LD   L, A
                LD   H, 0
                LD   DE, MenuBtnFrameTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
                POP  BC
                INC  C
                DJNZ .sbl
                LD   HL, MenuNgPanel_DL          ; панель REDBACK (SIZE_H внутри + сброс)
                LD   BC, MenuNgPanel_DL_SIZE
                CALL Render_CmdBufCopy
                LD   B, MENU_NG_BUTTON_COUNT     ; кнопки: released / pressed (hover нет — ориг.)
                LD   C, 0
.nbl:           PUSH BC
                LD   E, 0                        ; state: pressed если hover==i и ЛКМ зажата
                LD   A, (MenuHoverIndex)
                CP   C
                JR   NZ, .nst
                LD   A, (MenuLmbDown)
                OR   A
                JR   Z, .nst
                LD   E, 1
.nst:           LD   A, C
                ADD  A, A                        ; i*2
                ADD  A, E                        ; + state
                ADD  A, A                        ; *2 (слово)
                LD   L, A
                LD   H, 0
                LD   DE, MenuNgBtnTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
                POP  BC
                INC  C
                DJNZ .nbl
                LD   HL, MenuSpritesEnd_DL       ; конец спрайтов + курсор + swap (общий хвост)
                LD   BC, MenuSpritesEnd_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Render_GlobalCursor
                CALL Render_SwapFrameDMA
                RET

; Кадр экрана сценария: composite (фон+панель+тексты) + рамка-курсор на выбранной сложности
; + OKAY/CANCEL pressed при удержании в зоне + рейтинг по сложности + курсор мыши.
MenuScen_Render:
                FT_CMD_Start
                LD   HL, #FFFF
                LD   DE, #FF00
                CALL Render_CmdBufWrite32
                LD   HL, MenuBg_DL               ; СЛОЙ 1: фон HEROES из МЕНЮ (base 0, не рестримится)
                LD   BC, MenuBg_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, MenuSpritesProlog_DL    ; transp-палитра + BEGIN (для базы фонаря)
                LD   BC, MenuSpritesProlog_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, MenuLanternBase_DL      ; база фонаря СТАТИЧНА (кадры заняты панелью-окном)
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, ScenPanel_DL            ; СЛОЙ 2: панель-окно @ #064840 (transp)
                LD   BC, ScenPanel_DL_SIZE
                PUSH HL                          ; ★тень окна = ГЛОБАЛЬНАЯ Render_WindowShadowDL (как в бою)
                PUSH BC
                CALL Render_WindowShadowDL       ; DL панели чёрным (COLOR_A 80) со сдвигом −8,+8
                POP  BC
                POP  HL
                CALL Render_CmdBufCopy           ; сама панель поверх тени
                LD   HL, ScenSpritesProlog_DL    ; transparent-палитра + BEGIN
                LD   BC, ScenSpritesProlog_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (GameDifficulty)         ; рамка-курсор на выбранной сложности
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, ScenCursorTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (GameDifficulty)         ; рейтинг по сложности
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, ScenRatingTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Input_MouseX               ; OKAY pressed при ЛКМ в зоне
                LD   (UIClickX), HL
                CALL Input_MouseY
                LD   (UIClickY), HL
                LD   A, (MenuLmbDown)
                OR   A
                JR   Z, .scnobtn
                LD   IX, ScenOkZone
                CALL Menu_HitTestZone
                OR   A
                JR   Z, .scnotok
                LD   HL, ScenOkPressed_DL
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
                JR   .scnobtn
.scnotok:       LD   IX, ScenCancelZone
                CALL Menu_HitTestZone
                OR   A
                JR   Z, .scnobtn
                LD   HL, ScenCancelPressed_DL
                LD   BC, MENU_SPRITE_DL_SIZE
                CALL Render_CmdBufCopy
.scnobtn:       LD   HL, ScenSpritesEnd_DL
                LD   BC, ScenSpritesEnd_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (ScenHelpShow)          ; ПКМ-справка показана → рисуем окно поверх scenario
                CP   #FF
                CALL NZ, Scen_RenderHelp
                CALL Render_GlobalCursor
                CALL Render_SwapFrameDMA
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
