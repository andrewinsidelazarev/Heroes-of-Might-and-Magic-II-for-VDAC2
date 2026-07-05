; Сгенерировано Source/Tools/map_tools.py
MAP0_W         EQU 36
MAP0_H         EQU 36
MAP0_TILES     EQU 1296
MAP0_BIN_SIZE  EQU 32654
MAP0_SPG_PAGE  EQU #10
MAP0_SPG_ADDR  EQU #0000
MAP0_PASS_SIZE EQU 1296
MAP0_PASS_PAGE EQU #14
MAP0_PASS_ADDR EQU #0000
MAP0_PATH_SIZE EQU 2592
MAP0_PATH_PAGE EQU #11
MAP0_PATH_ADDR EQU #0000
MAP0_PATH_COST_ADDR EQU MAP0_PATH_ADDR
MAP0_PATH_FLAGS_ADDR EQU MAP0_PATH_ADDR + MAP0_TILES

; Бродячие монстры (random разрешён при конвертации, см. resolve_random_monsters):
; запись 6Б: x, y, monsterId(1=Peasant,2=Archer), countLo, countHi, alive(1; мутаб. в RAM)
MAP_MONSTER_COUNT EQU 13
MapMonsterTab:
                DB 20, 8, 2, 30, 0, 1   ; (20,8) id2 x30
                DB 26, 8, 2, 30, 0, 1   ; (26,8) id2 x30
                DB 27, 10, 2, 30, 0, 1   ; (27,10) id2 x30
                DB 20, 13, 1, 80, 0, 1   ; (20,13) id1 x80
                DB 11, 14, 2, 30, 0, 1   ; (11,14) id2 x30
                DB 31, 14, 2, 30, 0, 1   ; (31,14) id2 x30
                DB 25, 17, 1, 80, 0, 1   ; (25,17) id1 x80
                DB 3, 21, 2, 30, 0, 1   ; (3,21) id2 x30
                DB 14, 21, 1, 80, 0, 1   ; (14,21) id1 x80
                DB 4, 26, 2, 30, 0, 1   ; (4,26) id2 x30
                DB 11, 26, 1, 80, 0, 1   ; (11,26) id1 x80
                DB 18, 32, 2, 30, 0, 1   ; (18,32) id2 x30
                DB 27, 32, 2, 30, 0, 1   ; (27,32) id2 x30
