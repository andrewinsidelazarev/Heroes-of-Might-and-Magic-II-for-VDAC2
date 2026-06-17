                ifndef _HMM2_MUSIC_
                define _HMM2_MUSIC_
; ============================================================================
; Музыка HMM2 через MIDI-синтезатор SAM2695 (General MIDI) на MIDI-порту AY.
; Оригинальная музыка — XMI в HEROES2.AGG → SMF (xmi2mid.py) → компактный покадровый
; поток (music_pack.py): вся tempo-математика свёрнута в Python, здесь — простой плеер.
;
; MIDI-выход: AY port A (регистр 14), бит 2 — стандартная схема ZX Spectrum 128 /
; ZX Evolution (как в zx-midiplayer UzixLS). Bit-bang 31250 бод: start(0)+8data(LSB)+stop(1).
; Значение порта: бит2=1 → #FE, бит2=0 → #FA (остальные биты idle high).
;
; Формат потока (music_pack.py):
;   #F8 nn      — ждать nn кадров;
;   #FF         — конец (зациклить);
;   #80..#EF …  — MIDI-событие: status + данные (Cx/Dx → 1 байт, иначе 2). Без running status.
; ============================================================================

; Тайминг bit-bang ТОЧНО по zx-midiplayer uart_putc для 14МГц (448 такт/бит = 31250 бод):
; .B = внутренний счётчик 26, .C = задержка после стоп-бита 24. Симметричные ветки 0/1 (обе
; jr .nextbit), переходы JP NZ (10T), 2 nop — как в эталоне. Прерывания в HMM2 ВЫКЛЮЧЕНЫ
; (platform_tsconf: DI + INT mask 0), поэтому di/ei оригинала не нужны и опущены.
MIDI_BIT_DELAY  EQU 26                    ; .B (14МГц)
MIDI_STOP_DELAY EQU 24                    ; .C (14МГц, межбайтовый зазор после стоп-бита)

; Music_InitPort: КРИТИЧНО перед любой отправкой — настроить AY port A на ВЫХОД
; (рег 7, бит 6 = 1), иначе запись в рег 14 не выходит на физ. пин MIDI → тишина
; (zx-midiplayer uart_prepare). Затем выставить линию в idle-high (stop-уровень).
Music_InitPort:
                LD   BC, #FFFD
                LD   A, #07              ; AY регистр 7 (mixer / направление портов)
                OUT  (C), A
                LD   B, #BF              ; BC=#BFFD
                LD   A, #FC              ; бит6=1 → port A на ВЫХОД (MIDI-линия)
                OUT  (C), A
                LD   B, #FF              ; BC=#FFFD
                LD   A, #0E              ; регистр 14 (port A data)
                OUT  (C), A
                LD   B, #BF
                LD   A, #FE              ; бит2=1 → линия idle high (между байтами)
                OUT  (C), A
                RET

; MIDI_PutByte: A=байт → SAM2695 через AY (reg14, bit2), 31250 бод. Портит A,BC,DE; HL цел.
MIDI_PutByte:
                LD   E, A
                LD   BC, #FFFD
                LD   A, #0E
                OUT  (C), A              ; выбрать AY-регистр 14 (I/O port A)
                LD   B, #BF              ; BC=#BFFD — запись данных порта A
                LD   D, 1 + 8 + 1        ; START + 8 DATA + STOP
                SCF                      ; STOP-бит в CF — выдвинется через RR E
                JR   .put0               ; START-бит (0)
.loop:          RR   E                   ; (8) следующий бит (LSB вперёд) в CF
                JP   NC, .put0           ; (10)
.put1:          LD   A, #FE              ; (7) бит2=1
                OUT  (C), A              ; (11)
                JR   .nextbit            ; (12)
.put0:          LD   A, #FA              ; (7) бит2=0
                OUT  (C), A              ; (11)
                JR   .nextbit            ; (12) симметрично put1 — равный тайминг 0/1
.nextbit:       LD   A, 0                ; (7) .A — тайминг-填充 (на 14МГц остаётся ld a,0)
                LD   A, MIDI_BIT_DELAY   ; (7) .B = 26
.dlb:           DEC  A                   ; (4×26)
                JP   NZ, .dlb            ; (10×26)
                NOP                      ; (4)
                NOP                      ; (4)
                DEC  D                   ; (4)
                JP   NZ, .loop           ; (10) → 448 такт/бит = 31250 бод
                LD   E, MIDI_STOP_DELAY  ; .C = 24 — зазор после стоп-бита
.dlc:           DEC  E
                JR   NZ, .dlc
                RET

; Music_GMReset: GM System On (SysEx F0 7E 7F 09 01 F7) — перевести SAM2695 в General MIDI.
Music_GMReset:
                LD   HL, MidiGMOn
                LD   B, MidiGMOn_SIZE
.l:             LD   A, (HL)
                PUSH HL
                PUSH BC
                CALL MIDI_PutByte
                POP  BC
                POP  HL
                INC  HL
                DJNZ .l
                RET
MidiGMOn:       DEFB #F0, #7E, #7F, #09, #01, #F7
MidiGMOn_SIZE   EQU $ - MidiGMOn

; Music_Start: HL = адрес покадрового потока. Запоминает начало (для зацикливания) и активирует.
Music_Start:
                LD   (MusicPtr), HL
                LD   (MusicStart), HL
                XOR  A
                LD   (MusicWait), A
                INC  A
                LD   (MusicActive), A
                RET

; Music_Stop: гасит все ноты (CC123=0 на 16 каналах) и снимает активность.
Music_Stop:
                XOR  A
                LD   (MusicActive), A
                LD   B, 0                ; канал 0..15
.ch:            PUSH BC
                LD   A, #B0
                OR   B                   ; status = Control Change | channel
                CALL MIDI_PutByte
                LD   A, #7B              ; CC 123 = All Notes Off
                CALL MIDI_PutByte
                XOR  A
                CALL MIDI_PutByte
                POP  BC
                INC  B
                LD   A, B
                CP   16
                JR   C, .ch
                RET

; Music_Tick: вызывать РАЗ за кадр. Отсчитывает кадры; когда пауза истекла — шлёт все
; события до следующей паузы. На #FF — зацикливает трек.
Music_Tick:
                LD   A, (MusicActive)
                OR   A
                RET  Z
                LD   A, (MusicWait)
                OR   A
                JR   Z, .play
                DEC  A                   ; ждём ещё кадр
                LD   (MusicWait), A
                RET
.play:          LD   HL, (MusicPtr)
.next:          LD   A, (HL)
                CP   #F8                 ; WAIT nn
                JR   Z, .wait
                CP   #FF                 ; END → зациклить
                JR   Z, .loopTrack
                ; MIDI-событие: длина данных по нибблу status (Cx/Dx → 1, иначе 2)
                AND  #F0
                CP   #C0
                JR   Z, .send1
                CP   #D0
                JR   Z, .send1
.send2:         LD   A, (HL)            ; status
                CALL MIDI_PutByte
                INC  HL
                LD   A, (HL)
                CALL MIDI_PutByte
                INC  HL
                LD   A, (HL)
                CALL MIDI_PutByte
                INC  HL
                JR   .next
.send1:         LD   A, (HL)
                CALL MIDI_PutByte
                INC  HL
                LD   A, (HL)
                CALL MIDI_PutByte
                INC  HL
                JR   .next
.wait:          INC  HL
                LD   A, (HL)            ; nn кадров
                LD   (MusicWait), A
                INC  HL
                LD   (MusicPtr), HL
                RET
.loopTrack:     LD   HL, (MusicStart)
                LD   (MusicPtr), HL
                RET

                endif
