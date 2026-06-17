; Изолированный юнит-тест sd_zc + SD-модель эмулятора.
; Читает сектор 0 (BPB FAT32) в #8000 через sd_init + sd_read_sector.
                DEVICE ZXSPECTRUM48
                ORG #6000
SdTest:
                CALL sd_init
                XOR  A
                LD   H, A : LD L, A      ; LBA low16 = 0
                LD   D, A : LD E, A      ; LBA high16 = 0
                LD   IX, #8000           ; буфер 512 байт
                CALL sd_read_sector      ; CF=1 ошибка
                RET
                include "../ASM/sd_zc.asm"
SdTestEnd:
                SAVEBIN "Build/sdtest.bin", #6000, SdTestEnd - #6000
