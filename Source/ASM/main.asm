; ============================================================================
; Каркас порта Open HMM2 для TS-Config / VDAC2 FT812.
; ============================================================================

                DEVICE ZXSPECTRUM4096
                define MAPPING_REGISTERS

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
; Ресурсы королевства (fheroes2 Funds). Золото 3б (растёт >65535), прочее 2б.
ResGold        EQU #4248        ; 3б
ResWood        EQU #424B        ; 2б
ResOre         EQU #424D        ; 2б
ResMercury     EQU #424F        ; 2б
ResSulfur      EQU #4251        ; 2б
ResCrystal     EQU #4253        ; 2б
ResGems        EQU #4255        ; 2б  (до #4257)
MenuClickLatch EQU #4258        ; latch LMB в меню (1 клик = 1 действие)
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
                define CMD_ADDRESS_PTR #A400    ; DL-staging буфер (frame_max #0F90=3984Б).
                ; Сдвинут #A200→#A400: резидент дорос (диспетчер сцен + menu.asm).
                ; Потолок буфера ~#B06F (#A400+3984<#BFFF, не пересекает #C000). Loader отключён.
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
                include "menu.asm"          ; после module FT (нужны FT_* макросы)

                ; --- Резидентные trampolines к PAK-loader (ОТКЛЮЧЕНО) -------------
                ; Loader пассивен (диспетчер сцен не готов) и не должен быть в SPG, пока
                ; не интегрирован: отключён через if 0, чтобы не влиять на рабочую сборку
                ; (бисект глюков на unreal). Код sd_zc/raw_pak готов, включить при шаге
                ; «диспетчер сцен».
HMM2_LOADER_PAGE EQU #A0
RAWPAK_BUF_PAGE  EQU #A1

                if 0
Loader_Mount:
                CALL Loader_MapIn
                CALL RawPak_Mount
                JR   Loader_MapOutCF
Loader_OpenFile:                                 ; HL = имя файла (zero-term, резидент)
                CALL Loader_MapIn
                CALL RawPak_OpenFile
                JR   Loader_MapOutCF
Loader_ReadSectors:                              ; C=dst page, HL=dst off, B=count
                CALL Loader_MapIn
                CALL RawPak_ReadSectors
                JR   Loader_MapOutCF
Loader_MapIn:
                GetPage3
                LD   (Loader_SavedP3), A
                SetPage3 HMM2_LOADER_PAGE
                RET
Loader_MapOutCF:
                PUSH AF                          ; сохранить CF результата loader
                LD   A, CorePage + 1
                SetPage2_A                       ; raw_pak менял slot2 → вернуть Core
Loader_SavedP3 EQU $+1
                LD   A, #00
                SetPage3_A
                POP  AF
                RET
                endif

CoreEnd:
                ASSERT CoreEnd <= CMD_ADDRESS_PTR
                ASSERT CMD_ADDRESS_PTR + RUNTIME_CMD_FRAME_MAX <= StackTop
                SAVEBIN "Build/Core.bin", EntryPoint, CoreEnd - EntryPoint

                ; --- Loader overlay (ОТКЛЮЧЕНО, см. выше) ---
                if 0
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
