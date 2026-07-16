                ifndef _HMM2_PLATFORM_TSCONF_
                define _HMM2_PLATFORM_TSCONF_

Platform_Init:
                ; Включаем mapped-регистры TS-Config до любых SetPage*.
                ; Без этого на железе SetPage3 пишет в обычную RAM #0413,
                ; atlas upload читает старую slot3-страницу вместо #20..#2E.
                FMapAddrInit
                System_Setting SYS_ZCLK14 | SYS_CACHEEN
                Cache_Setting  EN_0000 | EN_4000 | EN_8000
                SetPage1 CorePage
                ; Core.bin после апскейла пересёк границу #8000.
                ; Slot2 должен видеть следующую 16K-страницу core-блока,
                ; иначе вызовы FT/Render в #80xx исполняют чужие данные.
                SetPage2 CorePage + 1
                ; До переключения на FT812 гасим обычный TS-Config gfx,
                ; чтобы во время FT_BOOT_UP не показывался старый framebuffer.
                Video_Setting VID_NOGFX
                XOR  A
                LD   BC, BORDER
                OUT  (C), A
                CALL Init_Int
                CALL Init_Video
                DI
                INT_Setting 0
                ; Указатели нужны Kempston Mouse для логического viewport.
                ; Физический FT812 режим остаётся 1024×768 в Init_Video.
                LD   HL, 640
                LD   (ResolutionWidthPtr), HL
                LD   HL, 480
                LD   (ResolutionHeightPtr), HL
                RET

; ---------------------------------------------------------------------------
; Init_Int
; Ждём первый frame interrupt TS-Conf перед FT_BOOT_UP. В Zuma это критично:
; железу нужно время стабилизировать timing до старта FT812.
; ---------------------------------------------------------------------------
Init_Int:
                LD   HL, INT_Handler
                LD   (InterruptVA + INT_VEC_FRAME), HL
                LD   A, HIGH InterruptVA
                LD   I, A
                IM   2
                INT_Setting INT_MSK_FRAME
                EI
                HALT
                RET

INT_Handler:    EI
                RET

                endif
