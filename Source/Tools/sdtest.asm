; Изолированный юнит-тест загрузчика: sd_zc + raw_pak + SD-модель эмулятора.
;   SdReadSector — sd_init + чтение сектора 0 (BPB) в #8000.
;   SdMountOpen  — sd_init + RawPak_Mount + RawPak_OpenFile(PakName); результат в
;                  TestResult (0=ok / #FF=fail) и RawPak_FoundSize/FileStartClus.
                DEVICE ZXSPECTRUM4096
                define MAPPING_REGISTERS
TSLibPage       EQU #00
CorePage        EQU #05
RAWPAK_BUF_PAGE EQU #06                   ; slot2-страница под dir/sector buffer (#8000)
                include "../../Docs/TSLib/Include/TSConf.inc"
                include "../../Docs/TSLib/Include/Memory/Include.inc"
                ORG #6000

SdReadSector:
                FMapAddrInit              ; включить mapping-регистры (как main)
                CALL sd_init
                XOR  A
                LD   H, A : LD L, A       ; LBA low16 = 0
                LD   D, A : LD E, A       ; LBA high16 = 0
                LD   IX, #8000
                CALL sd_read_sector
                RET

SdMountOpen:
                FMapAddrInit
                CALL sd_init
                CALL RawPak_Mount
                JR   NC, .mountfail       ; конвенция raw_pak: CF=1 = OK
                LD   HL, PakName
                CALL RawPak_OpenFile
                JR   NC, .openfail        ; CF=1 = найден
                XOR  A
                LD   (TestResult), A      ; 0 = найден
                RET
.mountfail:     LD   A, #01               ; Mount fail
                LD   (TestResult), A
                RET
.openfail:      LD   A, #02               ; OpenFile fail (Mount ok)
                LD   (TestResult), A
                RET

; SdReadData — Mount+Open+прочитать 4 сектора файла в page #07 off 0 (#8000 в slot2).
; ReadSectors: конвенция CF=0=ok (ОБРАТНАЯ Mount/OpenFile).
SdReadData:
                FMapAddrInit
                CALL sd_init
                CALL RawPak_Mount
                JR   NC, .fail
                LD   HL, PakName
                CALL RawPak_OpenFile
                JR   NC, .fail
                LD   C, #07               ; dst page (slot2 window)
                LD   HL, 0                ; dst off → #8000
                LD   B, 4                 ; 4 сектора = 2 КБ
                CALL RawPak_ReadSectors
                JR   C, .fail             ; CF=1 = ошибка
                XOR  A
                LD   (TestResult), A
                RET
.fail:          LD   A, #FF
                LD   (TestResult), A
                RET

; SdReadMenuPak — открыть HMM2MENU.PAK, прочитать 3 сектора (0=header, 1-2=blob)
; в page #07 off 0 (#8000). Проверяем, что blob (сектор 1) = начало payload.
SdReadMenuPak:
                FMapAddrInit
                CALL sd_init
                CALL RawPak_Mount
                JR   NC, .fail
                LD   HL, MenuPakName2
                CALL RawPak_OpenFile
                JR   NC, .fail
                LD   C, #07
                LD   HL, 0
                LD   B, 3
                CALL RawPak_ReadSectors
                JR   C, .fail
                XOR  A
                LD   (TestResult), A
                RET
.fail:          LD   A, #FF
                LD   (TestResult), A
                RET

TestResult:     DEFB #AA
PakName:        DEFB "HMM2_VD2.SPG", 0
MenuPakName2:   DEFB "HMM2MENU.PAK", 0

                include "../ASM/sd_zc.asm"
                include "../ASM/raw_pak.asm"
SdTestEnd:
                SAVEBIN "Build/sdtest.bin", #6000, SdTestEnd - #6000
