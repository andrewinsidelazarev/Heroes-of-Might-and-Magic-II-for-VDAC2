; ============================================================================
; Сцена БОЯ (battle) — ОВЕРЛЕЙ-страница HMM2_BATTLE_PAGE (slot3 #C000), как town/hiscores.
; Резидентные трамплины (main.asm): Battle_Enter_Tramp/Render_Battle_Tramp/Battle_Update_Tramp.
; Здесь — только тело сцены. slot3-edge: отсюда НЕ звать Render_BlackFrame/Adventure_Enter
; напрямую — их зовут резидентные трамплины. Loader-трамплины сохраняют slot3 → LoadFromPak ок.
; Контент поля — потоковый HMM2BATL.PAK с SD (НЕ SPG). Стат монстров — глоб-страница #91.
; ============================================================================
                include "generated_battle.inc"

BattleExitLatch: DEFB 1           ; 1 на входе (гасит «зажатый» клик-вход), 0 после отпускания ЛКМ
BattleHoverCell: DEFB #FF         ; индекс наведённой гекс-ячейки (0..98, #FF=нет) для подсветки
BattleTmpRow:    DEFB 0           ; временный ряд при вычислении ячейки
BattleUnitPtr:   DEFW 0           ; курсор по таблице состояния юнитов (рендер-цикл)
BattleTmpType:   DEFB 0           ; поля текущего юнита в рендер-цикле
BattleTmpCell:   DEFB 0
BattleTmpSide:   DEFB 0
BattleUnitState: DEFS BATTLE_UNIT_COUNT * BATTLE_UNIT_STATE_SIZE  ; МУТАБ. {тип,cell,side,count×2}×N
BattleUnitHP:    DEFS BATTLE_UNIT_COUNT * 2  ; HP-ПУЛ отряда по оригиналу (=count×maxHP). Атака
                                             ; уменьшает hp, count=ceil(hp/maxHP) → частичный урон НЕ теряется.
                                             ; 16-бит (как count/raw); огромные стеки могут переполнить — аппарат.предел.
BattleActiveUnit: DEFB 0          ; индекс активного юнита (чей ход) — двигается кликом по ячейке
BattleFindCell:  DEFB 0           ; scratch: искомая ячейка (Battle_FindUnitAtCell)
BattleTargetUnit: DEFB 0          ; индекс юнита-цели атаки
BattleTmpDmg:    DEFB 0           ; scratch: средний урон атакующего / maxHP цели
BattleTmpAtk:    DEFB 0           ; scratch: атака активного (для модификатора r=атака−защита)
BattleMeleePen:  DEFB 0           ; 1 = лучник бьёт в упор (сосед) → урон ÷2 (мили-штраф оригинала)
BattleTmpRaw:    DEFW 0           ; scratch: сырой урон = count×avgdmg
BattleActed:     DEFS BATTLE_UNIT_COUNT  ; флаг «ходил в этом раунде» (порядок хода по скорости)
BattleRetaliated: DEFS BATTLE_UNIT_COUNT ; флаг «ответил в этом раунде» (ответка раз/раунд, как оригинал)
BattleWasMelee:  DEFB 0           ; 1 = последняя атака была ближней (сосед) → возможна ответка
BattleBestIdx:   DEFB 0           ; scratch Battle_NextTurn: лучший кандидат
BattleBestSpd:   DEFB 0           ; scratch: его скорость
BattleSideTmp:   DEFB 0           ; scratch Battle_SideAlive
BattleAliveCnt:  DEFB 0           ; scratch: счётчик живых стороны
BattleContourVtx: DEFW 0          ; scratch: &вершина спрайта активного (контур)
BattleReach:     DEFS 99          ; достижимость клетки: 0=нет, 1..speed=дист, #FF=origin
BattleReachSpd:  DEFB 0           ; scratch: speed активного
BattleReachStep: DEFB 0           ; scratch: текущий шаг flood
BattleReachSrc:  DEFB 0           ; scratch: значение-источник flood
BattleRshCell:   DEFB 0           ; scratch: индекс клетки в рендере теней достижимости
BattleStatusMsg: DEFB 0           ; статус-сообщение панели: 0=нет, 1..N (BattleStatusPreTab[idx-1])
BattleStatusIdx: DEFB 0           ; scratch: 0-based индекс сообщения в рендере
BattleResult:    DEFB 0           ; итог боя: 0=идёт, 1=Victory (защ.выбит), 2=Defeat (атак.выбит)
BattleRound:     DEFB 1           ; номер раунда (для "Turn N"); ++ при новом раунде в NextTurn
; --- AI боя (ai_battle.cpp planUnitTurn, упрощённо для безгеройного skirmish) ---
BattleAutoMode:  DEFB 0           ; 0=ручной (человек=side0, AI=side1); 1=авто-режим (AI обе стороны до конца)
BattleAISide:    DEFB 0           ; scratch: сторона активного (стабильно через MonsterStats_Read-пейджинг)
BattleAIBestTgt: DEFB 0           ; scratch: лучшая цель (макс. угроза)
BattleAIBestScore: DEFW 0         ; scratch: её угроза = count×avgdmg (потенциал урона, getPotentialDamage)
BattleAIBestCell: DEFB 0          ; scratch: лучшая клетка подхода (мили)
BattleAIBestDist: DEFB 0          ; scratch: её dist² до цели
BattleAITRow:    DEFB 0           ; scratch: ряд цели
BattleAITCol:    DEFB 0           ; scratch: колонка цели
BATTLE_AI_GATE_MASK EQU %00011111 ; ход AI раз в 32 кадра (~0.6с) — бой видно
BATTLE_AI_MAX_ROUND EQU 60        ; страховка от зависания авто-боя (fheroes2: лимит ходов → auto-resolve)
; Зона кнопки Auto (нижняя панель, логич. 640×480). ⚠ ВРЕМЕННО: спрайт TEXTBAR[4/5] и точная
; позиция по оригиналу — отдельный ассет-шаг; здесь только функциональная зона хит-теста.
BATTLE_AUTO_X0   EQU 8
BATTLE_AUTO_Y0   EQU 440
BATTLE_AUTO_X1   EQU 88
BATTLE_AUTO_Y1   EQU 474
; --- Строка СОБЫТИЙ боя (fheroes2 setStatus top: «%{atk} do %{dmg} damage.[ %{n} %{def} perish.]») ---
BattleEvtActive: DEFB 0           ; 0=нет события, 1=показывать строку
BattleEvtVar:    DEFB 0           ; вариант атакующего (type×2 + (count==1)) → BattleEvtAtkTab
BattleEvtDmg:    DEFW 0           ; нанесённый урон (число в строке)
BattleEvtKill:   DEFW 0           ; убито бойцов цели (0 = без клаузы « N def perish.»)
BattleEvtDef:    DEFB 0           ; вариант цели (type×2 + (killed==1)) → BattleEvtPerishTab
BattleEvtOldCnt: DEFW 0           ; счётчик цели ДО удара (killed = old − new)
BattleEvtTotW:   DEFB 0           ; scratch: суммарная нативная ширина строки (для центровки)
BattleWinTextPtr: DEFW 0          ; scratch: курсор по BattleWinTextTab (рендер надписей окна)
BattleCasK0:     DEFW 0           ; scratch: убито type0 (Peasant) на стороне (Battle_CountKilled)
BattleCasK1:     DEFW 0           ; scratch: убито type1 (Archer) на стороне
BattleCasW:      DEFB 0           ; scratch: ширина блока строки потерь (px, для центровки)
; --- АНИМАЦИЯ ДВИЖЕНИЯ (юнит скользит между клетками + цикл ходьбы) ---
BattleAnimFrame: DEFB 0           ; индекс кадра анимации текущего юнита в рендере (0..11)
BattleRenderIdx: DEFB 0           ; индекс юнита в цикле рендера (для сравнения с движущимся)
BattleMoveActive: DEFB 0          ; 1 = идёт анимация движения (ход AI ждёт её окончания)
BattleMoveUnit:  DEFB 0           ; индекс движущегося юнита
BattleMoveDestCell: DEFB 0        ; клетка назначения (ставится по завершении)
BattleMoveProg:  DEFB 0           ; прогресс 0..BATTLE_MOVE_STEPS
BattleMoveCurX:  DEFW 0           ; текущая интерполир. позиция спрайта (vertex 1/16px)
BattleMoveCurY:  DEFW 0
BattleMoveStepX: DEFW 0           ; шаг/кадр = (to−from)/STEPS (знаковый)
BattleMoveStepY: DEFW 0
BattleMoveSrcCell: DEFB 0         ; клетка-источник движения (для строки «Moved …: from [src] to [dst].»)
BattlePendAttack: DEFB 0          ; 1 = после движения проверить соседство и атаковать BattleTargetUnit
BattleAtkActive: DEFB 0           ; 1 = идёт анимация атаки (урон применяется в пике)
BattleAtkUnit:   DEFB 0           ; индекс атакующего (играет ATTACK-кадры)
BattleAtkProg:   DEFB 0           ; прогресс анимации атаки 0..BATTLE_ATK_STEPS
BattleAtkHit:    DEFB 0           ; 0 = урон ещё не применён в этой анимации
BattleDeathActive: DEFB 0         ; идёт анимация смерти отряда
BattleDeathUnit: DEFB 0           ; индекс умирающего (играет DEATH-кадры, потом исчезает)
BattleDeathProg: DEFB 0           ; прогресс анимации смерти
BattleDeathPend: DEFB 0           ; 1 = в этой атаке цель умерла → запустить смерть после удара
; --- СТРЕЛА лучника (faithful ICN::ARCH_MSL; RedrawMissileAnimation): летит атакующий→цель за половину атаки ---
BattleArrowActive: DEFB 0         ; 1 = стрела в полёте (только дальний выстрел, WasMelee==0)
BattleArrowProg: DEFB 0           ; прогресс 0..BATTLE_ATK_STEPS/2 (долетает к пику = моменту урона)
BattleArrowDir:  DEFB 0           ; 0 = вправо (атакующий side0) / 1 = влево (зеркало) → BattleArrowSrcTab
BattleArrowCurX: DEFW 0           ; интерполир. позиция стрелы (vertex 1/16px)
BattleArrowCurY: DEFW 0
BattleArrowEndX: DEFW 0           ; цель (для расчёта шага)
BattleArrowEndY: DEFW 0
BattleArrowStepX: DEFW 0          ; шаг/кадр = (end−start)>>3 (8 шагов до пика)
BattleArrowStepY: DEFW 0
BATTLE_MOVE_STEPS EQU 32          ; кадров на перемещение (≈0.6с)
BATTLE_ATK_STEPS EQU 16           ; кадров на анимацию атаки (≈0.3с); урон в пике (середине)
BATTLE_DEATH_STEPS EQU 28         ; кадров на анимацию смерти (≈0.55с)
BATTLE_EVT_Y    EQU 448 * 256 / 10  ; физ-Y верхней строки статуса (логич 448 ×1.6), vertex 1/16px

; Вход в бой (через Battle_Enter_Tramp; чёрный кадр уже показан трамплином).
Battle_Enter:
                LD   A, GAME_MODE_COMBAT
                LD   (GameMode), A
                LD   A, 1
                LD   (BattleExitLatch), A
                ; сброс позиций юнитов из read-only Init в мутабельную таблицу + активный юнит = 0
                LD   HL, BattleUnitStateInit
                LD   DE, BattleUnitState
                LD   BC, BATTLE_UNIT_COUNT * BATTLE_UNIT_STATE_SIZE
                LDIR
                LD   HL, BattleActed              ; новый бой → никто не ходил И не отвечал
                LD   B, BATTLE_UNIT_COUNT * 2     ; чистим BattleActed + смежный BattleRetaliated
.clracted:      LD   (HL), 0
                INC  HL
                DJNZ .clracted
                XOR  A
                LD   (BattleStatusMsg), A         ; статус считается по hover каждый кадр
                LD   (BattleResult), A            ; бой идёт
                LD   (BattleAutoMode), A          ; каждый бой стартует в ручном режиме (Auto по кнопке)
                LD   (BattleEvtActive), A         ; строки событий ещё нет
                LD   (BattleMoveActive), A        ; анимация движения не идёт
                LD   (BattleAtkActive), A         ; анимация атаки не идёт
                LD   (BattleDeathActive), A       ; анимация смерти не идёт
                LD   (BattleDeathPend), A
                LD   (BattleArrowActive), A       ; стрела не летит
                LD   A, 1
                LD   (BattleRound), A             ; раунд 1
                CALL Battle_InitHP                ; hp-пул каждого отряда = count×maxHP (по оригиналу)
                CALL Battle_NextTurn              ; первый ход = самый быстрый отряд (speed из #91)
                CALL Battle_LoadFromPak           ; стрим HMM2BATL.PAK → RAM_G[0]
                RET

; Передать ход следующему отряду: среди ЖИВЫХ и не-ходивших — с макс.скоростью (#91);
; если таких нет — новый раунд (сбросить «ходил») и повторить. Ставит BattleActiveUnit + «ходил».
Battle_NextTurn:
.retry:         LD   A, #FF
                LD   (BattleBestIdx), A
                XOR  A
                LD   (BattleBestSpd), A
                LD   C, 0                          ; индекс
.nloop:         LD   A, C
                CALL Battle_UnitAddr              ; HL=&type (C сохраняется)
                INC  HL
                INC  HL
                INC  HL                           ; &count_lo
                LD   A, (HL)
                INC  HL
                OR   (HL)                          ; count_lo|count_hi
                JR   Z, .nnext                     ; мёртв
                LD   A, C                          ; не ходил?
                LD   HL, BattleActed
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   NZ, .nnext                    ; уже ходил
                LD   A, C                          ; скорость кандидата
                PUSH BC
                CALL Battle_UnitSpeed             ; A=speed (портит BC)
                POP  BC
                LD   B, A
                LD   A, (BattleBestSpd)
                CP   B
                JR   NC, .nnext                    ; текущий лучший >= → пропуск
                LD   A, B
                LD   (BattleBestSpd), A
                LD   A, C
                LD   (BattleBestIdx), A
.nnext:         INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JR   C, .nloop
                LD   A, (BattleBestIdx)
                CP   #FF
                JR   Z, .newround                  ; все живые отходили → новый раунд
                LD   (BattleActiveUnit), A
                LD   HL, BattleActed               ; пометить «ходил»
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                LD   (HL), 1
                RET
.newround:      LD   A, (BattleRound)              ; новый раунд → "Turn N+1"
                INC  A
                LD   (BattleRound), A
                LD   HL, BattleActed
                LD   B, BATTLE_UNIT_COUNT * 2     ; новый раунд: сброс «ходил» И «ответил» (смежные)
.nrclr:         LD   (HL), 0
                INC  HL
                DJNZ .nrclr
                JR   .retry

; A=индекс → A=скорость отряда (MonsterStatBuf+6 из #91). Портит BC,DE,HL.
Battle_UnitSpeed:
                CALL Battle_UnitAddr
                LD   A, (HL)                       ; type
                INC  A                             ; monster id = type+1
                LD   B, A
                CALL MonsterStats_Read
                LD   A, (MonsterStatBuf + 6)
                RET

; A=сторона → A=число ЖИВЫХ отрядов этой стороны. Портит BC,DE,HL.
Battle_SideAlive:
                LD   (BattleSideTmp), A
                XOR  A
                LD   (BattleAliveCnt), A
                LD   C, 0
.sloop:         LD   A, C
                CALL Battle_UnitAddr              ; HL=&type
                INC  HL
                INC  HL                           ; &side
                LD   A, (HL)
                PUSH HL
                LD   HL, BattleSideTmp
                CP   (HL)
                POP  HL
                JR   NZ, .snext                    ; не та сторона
                INC  HL                            ; &count_lo
                LD   A, (HL)
                INC  HL
                OR   (HL)
                JR   Z, .snext                     ; мёртв
                LD   A, (BattleAliveCnt)
                INC  A
                LD   (BattleAliveCnt), A
.snext:         INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JR   C, .sloop
                LD   A, (BattleAliveCnt)
                RET

; Проверка конца боя: если у стороны 0 живых → форс перезалив грунта + A=1 (выход на карту).
; Проверка конца боя. Сторона выбита → BattleResult (1=Victory защ.выбит / 2=Defeat атак.выбит),
; БОЙ ОСТАЁТСЯ (A=0) — показываем экран итога; выход на карту по клику (Battle_Update .result*).
Battle_CheckEnd:
                XOR  A
                CALL Battle_SideAlive              ; живых атакующего (side0)
                OR   A
                JR   Z, .lose                       ; атакующий выбит → поражение
                LD   A, 1
                CALL Battle_SideAlive              ; живых защитника (side1)
                OR   A
                JR   Z, .win                        ; защитник выбит → победа
                XOR  A                             ; обе стороны живы → продолжать
                RET
.win:           LD   A, 1
                LD   (BattleResult), A
                XOR  A
                RET
.lose:          LD   A, 2
                LD   (BattleResult), A
                XOR  A
                RET

; Стрим HMM2BATL.PAK с SD в RAM_G[0]. Имя — общий MenuNameBuf (сцены эксклюзивны).
Battle_LoadFromPak:
                LD   HL, BattlePakName
                LD   DE, MenuNameBuf
                LD   BC, 13
                LDIR
                CALL Loader_Init
                CALL Loader_Mount
                RET  NC
                LD   HL, MenuNameBuf
                CALL Loader_OpenFile
                RET  NC
                LD   C, RAWPAK_BUF_PAGE           ; пропустить HPAK header (BATTLE_BODY_SECTOR)
                LD   HL, 0
                LD   B, BATTLE_BODY_SECTOR
                CALL Loader_ReadSectors
                LD   BC, BATTLE_PAYLOAD_SECTORS   ; стрим payload → RAM_G[0]
                CALL Loader_StreamToRamG
                RET

; Опрос боя: клик ЛКМ (после отпускания входного) → выход. OUT: A=1 если запрошен выход
; (резидентный Battle_Update_Tramp по A=1 зовёт Adventure_Enter — slot3-edge).
Battle_Update:
                CALL Battle_ComputeHover          ; обновить наведённую гекс-ячейку (подсветка)
                LD   A, (BattleResult)             ; бой окончен? → показываем итог, выход по клику
                OR   A
                JR   NZ, .result_wait
                CALL Battle_ComputeReachable      ; достижимые клетки активного (тень + статус)
                CALL Battle_ComputeStatus         ; статус-подсказка по hover (Move/Attack/Shoot/Turn)
                LD   A, (BattleMoveActive)         ; идёт анимация движения? → тикать её, ввод/ход заморожены
                OR   A
                JR   Z, .nomoveanim
                CALL Battle_MoveTick
                XOR  A
                RET
.nomoveanim:    LD   A, (BattleAtkActive)          ; идёт анимация атаки? → тикать её
                OR   A
                JR   Z, .noatkanim
                CALL Battle_AtkTick
                XOR  A
                RET
.noatkanim:     LD   A, (BattleDeathActive)        ; идёт анимация смерти? → тикать её
                OR   A
                JR   Z, .noanim
                CALL Battle_DeathTick
                XOR  A
                RET
.noanim:        CALL Battle_AIMaybeAct            ; AI-сторона (защитник, либо все в авто) ходит сама; A=1 если AI владеет ходом
                OR   A
                JR   Z, .humaninput              ; A=0 → ход человека → обычный ввод
                XOR  A                            ; AI обрабатывает этот кадр → ни клика, ни выхода
                RET
.humaninput:    CALL Input_MouseLMB               ; NZ = нажато
                JR   NZ, .pressed
                XOR  A
                LD   (BattleExitLatch), A
                RET
.result_wait:   CALL Input_MouseLMB
                JR   NZ, .rpressed
                XOR  A
                LD   (BattleExitLatch), A           ; отпущено → сброс латча, стоим на итоге
                RET
.rpressed:      LD   A, (BattleExitLatch)
                OR   A
                JR   Z, .exit                       ; новый клик по экрану итога → выход на карту
                XOR  A
                RET
.pressed:       LD   A, (BattleExitLatch)
                OR   A
                JR   Z, .newclick
                XOR  A                             ; клик ещё «зажат» → A=0
                RET
.newclick:      LD   A, 1
                LD   (BattleExitLatch), A           ; обработать клик однократно
                CALL Battle_CheckAutoClick          ; клик по зоне Auto → включить авто-режим (AI обе стороны)
                JR   NZ, .autoon
                LD   A, (BattleHoverCell)
                CP   #FF
                JR   Z, .exit                       ; клик ВНЕ поля → выход
                CALL Battle_FindUnitAtCell          ; A = индекс живого юнита в ячейке (#FF=нет)
                CP   #FF
                JR   Z, .moveact                    ; пусто → передвинуть активного
                LD   (BattleTargetUnit), A
                CALL Battle_UnitAddr                ; HL = &state[target]
                INC  HL
                INC  HL                            ; &side цели
                LD   C, (HL)
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL                            ; &side активного
                LD   A, (HL)
                CP   C
                JR   Z, .ownunit                    ; та же сторона → свой, пока ничего
                CALL Battle_AttackAllowed           ; ближний бой — только в соседнюю (стрелок — всегда). adj-first
                JR   Z, .cantreach
                CALL Battle_StartAttack             ; враг в ячейке → анимация атаки (урон+ответка+ход внутри)
                XOR  A
                RET
.cantreach:     XOR  A                              ; melee не дотянуться → ход НЕ тратится
                RET
.ownunit:       XOR  A
                RET
.moveact:       CALL Battle_MoveActive              ; пустая ячейка → передвинуть активного юнита
                XOR  A
                RET
.autoon:        LD   A, 1
                LD   (BattleAutoMode), A             ; кнопка Auto → AI доигрывает бой за обе стороны
                XOR  A
                RET
.exit:          ; Бой затёр RAM_G-кэш террейн-композита (payload base0). Перед возвратом на карту
                ; форсируем полный перезалив грунта: RuntimeLastOrigin = #FF (как в town.asm).
                LD   HL, #FFFF
                LD   (RuntimeLastOriginX), HL
                LD   A, 1
                RET

; Передвинуть активного юнита в наведённую ячейку: запустить АНИМАЦИЮ движения (как AI), чтобы
; показать строку «Moved …: from [src] to [dst].» и скольжение спрайта. Ход завершит Battle_MoveTick.
Battle_MoveActive:
                LD   A, (BattleHoverCell)
                LD   (BattleMoveDestCell), A        ; цель движения = наведённая клетка
                XOR  A
                LD   (BattlePendAttack), A          ; чистое перемещение (без атаки по приходу)
                JP   Battle_StartMove               ; анимация движения; MoveTick поставит клетку + Battle_EndTurn

; A = индекс юнита → HL = &BattleUnitState[A * 5]. Сохраняет A.
Battle_UnitAddr:
                LD   L, A
                LD   H, 0
                ADD  HL, HL                       ; *2
                ADD  HL, HL                       ; *4
                LD   E, A
                LD   D, 0
                ADD  HL, DE                       ; *5
                LD   DE, BattleUnitState
                ADD  HL, DE
                RET

; A = индекс юнита → HL = &BattleUnitHP[A*2] (hp-пул). Сохраняет A.
Battle_UnitHPAddr:
                LD   L, A
                LD   H, 0
                ADD  HL, HL                       ; *2
                LD   DE, BattleUnitHP
                ADD  HL, DE
                RET

; Модификатор урона по оригиналу (CalculateDamageUnit): IN HL=raw, A=r(signed=атака−защита).
; OUT HL = floor(raw × num / 20), cap #FFFF, где (den=20):
;   r>0 → num = 20 + 2·min(r,20)  (до ×3.0);  r≤0 → num = 20 + max(r,−16)  (до ×0.2).
Battle_ApplyDmgMod:
                OR   A
                JP   P, .pos                       ; r >= 0
                CP   #F0                            ; r<0: max(r,−16); −16=#F0 (unsigned: A<#F0?)
                JR   NC, .negok                    ; A>=#F0 → r в [−16,−1], оставить
                LD   A, #F0                         ; r<−16 → −16
.negok:         ADD  A, 20                          ; num = 20 + r  (r отриц. → num<20)
                JR   .domul
.pos:           JR   Z, .pzero                     ; r==0 → ×1
                CP   21
                JR   C, .posok                     ; r<=20
                LD   A, 20
.posok:         ADD  A, A                           ; 2·min(r,20)
                ADD  A, 20                          ; num = 20 + 2·min(r,20)
                JR   .domul
.pzero:         LD   A, 20                          ; num = 20 (×1)
.domul:         LD   B, A                           ; B = num
                LD   D, H
                LD   E, L                           ; DE = raw
                LD   HL, 0
                LD   A, B
                OR   A
                JR   Z, .zero
.mmul:          ADD  HL, DE                         ; product = raw × num (cap #FFFF)
                JR   C, .mcap
                DJNZ .mmul
                JR   .div20
.mcap:          LD   HL, #FFFF
.div20:         LD   C, 20                          ; HL = product / 20 (16/8 вычитанием)
                LD   DE, 0
.d20:           LD   A, L
                SUB  C
                LD   B, A
                LD   A, H
                SBC  A, 0
                JR   C, .d20end
                LD   L, B
                LD   H, A
                INC  DE
                JR   .d20
.d20end:        EX   DE, HL                         ; HL = частное
                RET
.zero:          LD   HL, 0
                RET

; HP-пул каждого отряда = count × maxHP (по оригиналу: _hitPoints). Зовётся в Battle_Enter.
; count и type читаем ИЗ slot3 ДО MonsterStats_Read (чтение slot3 сразу после него ненадёжно на железе).
Battle_InitHP:
                LD   C, 0                          ; индекс юнита
.ihloop:        LD   A, C                          ; 1) count (slot3) — ДО MonsterStats_Read
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                INC  HL                            ; &count_lo
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = count
                PUSH BC                            ; сохранить счётчик C — MonsterStats_Read портит BC (LDIR)!
                PUSH DE                            ; сохранить count
                LD   A, C                          ; 2) type → maxHP
                CALL Battle_UnitAddr
                LD   A, (HL)
                INC  A
                LD   B, A
                CALL MonsterStats_Read
                LD   A, (MonsterStatBuf + 4)       ; maxHP
                POP  DE                            ; DE = count
                LD   HL, 0                          ; HL = count × maxHP (повтор.сложение, cap #FFFF)
                OR   A
                JR   Z, .ihstore
                LD   B, A
.ihmul:         ADD  HL, DE
                JR   C, .ihcap
                DJNZ .ihmul
                JR   .ihstore
.ihcap:         LD   HL, #FFFF
.ihstore:       POP  BC                            ; восстановить счётчик C (MonsterStats_Read его затёр)
                PUSH HL                            ; hp-пул
                LD   A, C
                CALL Battle_UnitHPAddr             ; HL = &BattleUnitHP[C]
                POP  DE                            ; DE = hp-пул
                LD   (HL), E
                INC  HL
                LD   (HL), D
                INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JR   C, .ihloop
                RET

; A = cell → A = индекс ЖИВОГО юнита в этой ячейке, или #FF. (cell@+1, count@+3,+4)
Battle_FindUnitAtCell:
                LD   (BattleFindCell), A
                LD   C, 0
.floop:         LD   A, C
                CALL Battle_UnitAddr               ; HL = &state[C]
                INC  HL                            ; &cell
                LD   A, (HL)
                PUSH HL
                LD   HL, BattleFindCell
                CP   (HL)
                POP  HL
                JR   NZ, .fnext
                INC  HL
                INC  HL                            ; &cell → &count_lo
                LD   A, (HL)
                INC  HL
                OR   (HL)                          ; count_lo | count_hi
                JR   Z, .fnext                     ; count 0 → мёртв
                LD   A, C
                RET
.fnext:         INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JR   C, .floop
                LD   A, #FF
                RET

; Атака: активный юнит бьёт BattleTargetUnit. Потери = active.count×avgdmg / target.hp,
; target.count −= потери (clamp 0 → мёртв). Статы из #91 (MonsterStats_Read; type+1 = monster id).
Battle_Attack:
                LD   A, (BattleTargetUnit)          ; счётчик цели ДО удара (killed = old − new для строки событий)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                INC  HL                            ; &count_lo
                LD   A, (HL)
                LD   (BattleEvtOldCnt), A
                INC  HL
                LD   A, (HL)
                LD   (BattleEvtOldCnt + 1), A
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                LD   A, (HL)                       ; active.type
                INC  A
                LD   B, A
                CALL MonsterStats_Read
                LD   A, (MonsterStatBuf + 0)       ; атака активного → сохранить для r=атака−защита
                LD   (BattleTmpAtk), A
                LD   A, (MonsterStatBuf + 2)       ; dmgMin
                LD   C, A
                LD   A, (MonsterStatBuf + 3)       ; dmgMax
                ADD  A, C
                SRL  A                             ; avgdmg = (min+max)/2
                LD   (BattleTmpDmg), A
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                INC  HL                            ; &count_lo
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = active.count
                LD   HL, 0                          ; raw = count × avgdmg (повторное сложение)
                LD   A, (BattleTmpDmg)
                OR   A
                JR   Z, .rawok
                LD   B, A
.muladd:        ADD  HL, DE
                JR   C, .rawcap
                DJNZ .muladd
                JR   .rawok
.rawcap:        LD   HL, #FFFF
.rawok:         LD   (BattleTmpRaw), HL             ; raw = суммарный урон (count×avgdmg)
                LD   A, (BattleTargetUnit)
                CALL Battle_UnitAddr
                LD   A, (HL)                       ; target.type
                INC  A
                LD   B, A
                CALL MonsterStats_Read
                LD   A, (MonsterStatBuf + 4)       ; maxHP цели
                OR   A
                JR   NZ, .hpok
                LD   A, 1                           ; защита от /0
.hpok:          LD   (BattleTmpDmg), A              ; BattleTmpDmg := maxHP (скретч, avgdmg больше не нужен)
                ; --- модификатор урона r = атака−защита (по оригиналу CalculateDamageUnit, ×0.2…×3.0) ---
                LD   A, (MonsterStatBuf + 1)        ; защита цели (буфер ещё = статы цели)
                LD   B, A
                LD   A, (BattleTmpAtk)              ; атака активного
                SUB  B                              ; A = r = атака − защита (знаковый)
                LD   HL, (BattleTmpRaw)
                CALL Battle_ApplyDmgMod             ; HL = raw × модификатор (атака−защита)
                LD   A, (BattleMeleePen)            ; N2b: лучник в упор (блокирован) → урон ÷2
                OR   A
                JR   Z, .nomelpen
                SRL  H
                RR   L                              ; HL >>= 1 (÷2)
.nomelpen:      LD   (BattleTmpRaw), HL
                ; hp-ПУЛ[target] −= raw, clamp 0 (по оригиналу: _hitPoints -= dmg)
                LD   A, (BattleTargetUnit)
                CALL Battle_UnitHPAddr             ; HL = &hp[target]
                PUSH HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = hp-пул
                LD   HL, (BattleTmpRaw)            ; HL = raw
                EX   DE, HL                        ; HL = hp-пул, DE = raw
                OR   A
                SBC  HL, DE                        ; hp-пул −= raw
                JR   NC, .hpclamp
                LD   HL, 0                          ; заём → пул 0
.hpclamp:       POP  DE                            ; DE = &hp[target]
                LD   A, L
                LD   (DE), A
                INC  DE
                LD   A, H
                LD   (DE), A                        ; сохранить новый hp-пул (HL = пул, не тронут)
                ; count = ceil(hp-пул / maxHP); пул 0 → мёртв
                LD   A, H
                OR   L
                JR   Z, .tdead
                LD   A, (BattleTmpDmg)              ; maxHP (делитель C)
                LD   C, A
                DEC  A                              ; maxHP−1 для ceil
                LD   E, A
                LD   D, 0
                ADD  HL, DE                         ; HL = hp-пул + maxHP−1
                LD   DE, 0                          ; count = floor(HL / maxHP)
.cntdiv:        LD   A, L
                SUB  C
                LD   B, A
                LD   A, H
                SBC  A, 0
                JR   C, .cntend                     ; HL < maxHP → стоп
                LD   L, B
                LD   H, A
                INC  DE
                JR   .cntdiv
.cntend:        LD   A, (BattleTargetUnit)          ; записать новый count цели
                PUSH DE                            ; сохранить count — Battle_UnitAddr клоббит DE!
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                INC  HL                            ; &count_lo
                POP  DE                            ; count
                LD   (HL), E
                INC  HL
                LD   (HL), D
                JP   Battle_SetEvent               ; зафиксировать событие «X do N damage[. M perish]»
.tdead:         LD   A, (BattleTargetUnit)
                LD   (BattleDeathUnit), A           ; цель умерла → анимация смерти (запустит AtkTick)
                LD   B, A
                LD   A, 1
                LD   (BattleDeathPend), A
                LD   A, B
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                INC  HL                            ; &count_lo
                LD   (HL), 0
                INC  HL
                LD   (HL), 0                        ; count 0 → мёртв
                JP   Battle_SetEvent

; N2c — ОТВЕТКА (по оригиналу): если последняя атака была МИЛИ (BattleWasMelee), цель ЖИВА и не
; отвечала в этом раунде — цель бьёт в ответ атакующего, помечается «ответила». На удар меняем
; местами active↔target (Battle_Attack бьёт active→target), потом возвращаем. Зовётся после Battle_Attack.
Battle_Retaliate:
                LD   A, (BattleWasMelee)
                OR   A
                RET  Z                              ; выстрел → без ответки
                LD   A, (BattleTargetUnit)          ; цель жива? (count != 0)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                INC  HL                            ; &count_lo
                LD   A, (HL)
                INC  HL
                OR   (HL)
                RET  Z                              ; цель мертва → без ответки
                LD   A, (BattleTargetUnit)          ; цель уже отвечала в этом раунде?
                LD   HL, BattleRetaliated
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                RET  NZ                             ; уже отвечала → без ответки
                LD   (HL), 1                         ; пометить «ответила»
                LD   A, (BattleActiveUnit)          ; active ↔ target
                LD   B, A
                LD   A, (BattleTargetUnit)
                LD   (BattleActiveUnit), A
                LD   A, B
                LD   (BattleTargetUnit), A
                CALL Battle_AttackAllowed           ; пересчитать соседство/штраф для ответчика
                CALL Battle_Attack                  ; цель бьёт в ответ атакующего
                LD   A, (BattleActiveUnit)          ; вернуть active ↔ target
                LD   B, A
                LD   A, (BattleTargetUnit)
                LD   (BattleActiveUnit), A
                LD   A, B
                LD   (BattleTargetUnit), A
                RET

; ============================================================================
; СТРОКА СОБЫТИЙ боя (fheroes2 RedrawActionAttackPart2): «%{atk} do %{dmg} damage.[ %{n} %{def} perish.]».
; Фиксируется в конце Battle_Attack, рисуется в верхней строке статус-бара (нативный шрифт).
; ============================================================================

; Зафиксировать строку из последней атаки: атакующий=active, цель=target, урон=BattleTmpRaw,
; счётчик цели ДО=BattleEvtOldCnt. Варианты: атакующий type×2+(count==1), цель type×2+(killed==1).
Battle_SetEvent:
                LD   A, (BattleActiveUnit)          ; вариант атакующего = type×2 + (count==1)
                CALL Battle_UnitAddr
                LD   A, (HL)
                ADD  A, A
                LD   C, A                           ; C = type×2
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                        ; DE = active.count
                LD   A, D
                OR   A
                JR   NZ, .atkpl
                LD   A, E
                CP   1
                JR   NZ, .atkpl
                INC  C                              ; count==1 → singular
.atkpl:         LD   A, C
                LD   (BattleEvtVar), A
                LD   HL, (BattleTmpRaw)             ; урон
                LD   (BattleEvtDmg), HL
                LD   A, (BattleTargetUnit)          ; killed = old − new
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                        ; DE = new count
                LD   HL, (BattleEvtOldCnt)
                OR   A
                SBC  HL, DE
                LD   (BattleEvtKill), HL
                LD   A, (BattleTargetUnit)          ; вариант цели = type×2 + (killed==1)
                CALL Battle_UnitAddr
                LD   A, (HL)
                ADD  A, A
                LD   C, A
                LD   HL, (BattleEvtKill)
                LD   A, H
                OR   A
                JR   NZ, .defmn
                LD   A, L
                CP   1
                JR   NZ, .defmn
                INC  C                              ; killed==1 → singular
.defmn:         LD   A, C
                LD   (BattleEvtDef), A
                LD   A, 1
                LD   (BattleEvtActive), A
                RET

; A=вариант → HL=&BattleEvtAtkTab[A*5]. (×5 = ×4+×1.)
Battle_EvtAtkAddr:
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE
                LD   DE, BattleEvtAtkTab
                ADD  HL, DE
                RET
; A=вариант → HL=&BattleEvtPerishTab[A*5].
Battle_EvtPerishAddr:
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE
                LD   DE, BattleEvtPerishTab
                ADD  HL, DE
                RET
; HL=&запись[lo,mid,hi,w,h] → A=w (нативная ширина). Сохраняет HL.
Battle_EvtEntW:
                PUSH HL
                INC  HL
                INC  HL
                INC  HL
                LD   A, (HL)
                POP  HL
                RET
; HL += A (A беззнаково).
Battle_AddAToHL:
                ADD  A, L
                LD   L, A
                RET  NC
                INC  H
                RET
; HL=число → A=ширина (число цифр × ширина «0»). Аппрокс (моноширинно) для центровки. Портит мн.
Battle_EvtNumW:
                CALL Num_DigitCount                 ; A = число цифр
                LD   B, A
                LD   A, (BattleEvtDigitTab + 3)     ; ширина глифа «0»
                LD   C, A
                XOR  A
.nwm:           ADD  A, C
                DJNZ .nwm
                RET

; Собрать и нарисовать строку события центрированной (физ-центр 512), нативным шрифтом.
Battle_RenderEventLine:
                LD   HL, 0                          ; --- суммарная нативная ширина (16-бит) ---
                PUSH HL
                LD   A, (BattleEvtVar)
                CALL Battle_EvtAtkAddr
                CALL Battle_EvtEntW
                POP  HL
                CALL Battle_AddAToHL
                PUSH HL
                LD   HL, (BattleEvtDmg)
                CALL Battle_EvtNumW
                POP  HL
                CALL Battle_AddAToHL
                PUSH HL
                LD   HL, BattleEvtDmgSfx
                CALL Battle_EvtEntW
                POP  HL
                CALL Battle_AddAToHL
                LD   A, (BattleEvtKill)             ; клауза perish только если killed != 0
                LD   B, A
                LD   A, (BattleEvtKill + 1)
                OR   B
                JR   Z, .haveW
                PUSH HL
                LD   HL, BattleEvtSpace
                CALL Battle_EvtEntW
                POP  HL
                CALL Battle_AddAToHL
                PUSH HL
                LD   HL, (BattleEvtKill)
                CALL Battle_EvtNumW
                POP  HL
                CALL Battle_AddAToHL
                PUSH HL
                LD   A, (BattleEvtDef)
                CALL Battle_EvtPerishAddr
                CALL Battle_EvtEntW
                POP  HL
                CALL Battle_AddAToHL
.haveW:         SRL  H                              ; startX = 512 − ширина/2
                RR   L
                EX   DE, HL                         ; DE = ширина/2
                LD   HL, 512
                OR   A
                SBC  HL, DE                         ; HL = startX (физ px)
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                         ; ×16 (vertex 1/16px)
                LD   (ResPenX), HL
                LD   HL, BATTLE_EVT_Y
                LD   (ResPenY), HL
                LD   HL, Battle_Status_Begin_DL     ; пролог: палитра статуса + transform 256 + BEGIN
                LD   BC, Battle_Status_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (BattleEvtVar)              ; «<atk> do » + урон + « damage.»
                CALL Battle_EvtAtkAddr
                CALL Battle_DrawEvtSprite
                LD   HL, (BattleEvtDmg)
                CALL Battle_DrawEvtNum
                LD   HL, BattleEvtDmgSfx
                CALL Battle_DrawEvtSprite
                LD   A, (BattleEvtKill)
                LD   B, A
                LD   A, (BattleEvtKill + 1)
                OR   B
                JR   Z, .eend                      ; нет гибели → без клаузы
                LD   HL, BattleEvtSpace
                CALL Battle_DrawEvtSprite
                LD   HL, (BattleEvtKill)
                CALL Battle_DrawEvtNum
                LD   A, (BattleEvtDef)
                CALL Battle_EvtPerishAddr
                CALL Battle_DrawEvtSprite
.eend:          LD   HL, Battle_Status_End_DL
                LD   BC, Battle_Status_End_DL_SIZE
                CALL Render_CmdBufCopy
                RET

; ============================================================================
; СТРОКА ДВИЖЕНИЯ (fheroes2 RedrawActionMove, battle_interface.cpp:4448):
; «Moved %{monster}: from [%{src}] to [%{dst}].»  src/dst = «row+1, col+1».
; Рисуется пока идёт анимация движения (BattleMoveActive). Источник=BattleMoveSrcCell,
; назначение=BattleMoveDestCell, тип=BattleMoveUnit.type. Центрируется по физ-центру 512.
; ============================================================================

; A=cell → row+1 в B, col+1 в A (для строки координат [row, col], 1-based как fheroes2).
Battle_CellRowColP1:
                CALL Battle_CellRowCol             ; B=row, A=col (0-based)
                INC  A                             ; col+1
                INC  B                             ; row+1
                RET

Battle_TmpCoordCell: DEFB 0

; A=цифра 0-9 → нарисовать нативную цифру (BattleEvtMoveDigitTab) пером ResPenX, продвинуть.
Battle_DrawMoveDigit:
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                         ; A*5
                LD   DE, BattleEvtMoveDigitTab
                ADD  HL, DE
                JP   Battle_DrawEvtSprite

; A=число (1..99) → нарисовать нативными цифрами без ведущего нуля. Портит A,B,C,HL,DE.
Battle_DrawMoveNum:
                CP   10
                JR   C, .single
                LD   B, 0                           ; десятки
.tens:          INC  B
                SUB  10
                CP   10
                JR   NC, .tens
                LD   C, A                           ; C = единицы
                LD   A, B                           ; десятки
                PUSH BC
                CALL Battle_DrawMoveDigit
                POP  BC
                LD   A, C                           ; единицы
.single:        JP   Battle_DrawMoveDigit

; Нарисовать координату «row+1, col+1» пером (ResPenX): row-число + «, » + col-число (нативно). A=cell.
Battle_DrawCoord:
                LD   (Battle_TmpCoordCell), A
                CALL Battle_CellRowColP1           ; B=row+1, A=col+1
                LD   A, B                          ; row+1
                CALL Battle_DrawMoveNum            ; row-число (нативно)
                LD   HL, BattleEvtComma             ; «, »
                CALL Battle_DrawEvtSprite
                LD   A, (Battle_TmpCoordCell)
                CALL Battle_CellRowColP1           ; A=col+1
                JP   Battle_DrawMoveNum             ; col-число (нативно, RET через JP)

; A=число (1..99) → A=ширина нативными цифрами (px). Портит B,C,HL,DE.
Battle_MoveNumW:
                LD   B, 0                           ; B = число цифр
                CP   10
                JR   C, .one
                LD   B, 1                           ; десятки есть → 2 цифры
.one:          INC  B
                LD   A, (BattleEvtMoveDigitTab + 3) ; ширина нативной '0'
                LD   C, A
                XOR  A
.mw:           ADD  A, C
                DJNZ .mw
                RET

; A=BattleMoveUnit.type → HL=&BattleEvtMoveNameTab[type*5]. Портит A,DE.
Battle_MoveNameAddr:
                LD   A, (BattleMoveUnit)
                CALL Battle_UnitAddr
                LD   A, (HL)                       ; type
                LD   C, A
                ADD  A, A
                ADD  A, A
                ADD  A, C                          ; type*5
                LD   L, A
                LD   H, 0
                LD   DE, BattleEvtMoveNameTab
                ADD  HL, DE
                RET

; HL=накопитель, HL2=&запись → HL += ширина записи. Хелпер: HL += EntW(record). Запись в DE-сейв.
; (используется как: LD HL,record / CALL Battle_EvtEntW / затем ADD к накопителю — см. ниже инлайн)

; Собрать ширину строки движения → HL (нативные px), для центрирования.
Battle_MoveLineW:
                LD   HL, 0
                PUSH HL                            ; накопитель
                LD   HL, BattleEvtMoveHead          ; «Moved »
                CALL Battle_EvtEntW
                POP  HL
                CALL Battle_AddAToHL
                PUSH HL
                CALL Battle_MoveNameAddr            ; «Peasants: »/«Archers: »
                CALL Battle_EvtEntW
                POP  HL
                CALL Battle_AddAToHL
                PUSH HL
                LD   HL, BattleEvtMoveFrom           ; «from [»
                CALL Battle_EvtEntW
                POP  HL
                CALL Battle_AddAToHL
                PUSH HL
                LD   A, (BattleMoveSrcCell)         ; координата src
                CALL Battle_AccCoordWrap
                POP  HL
                CALL Battle_AddAToHL
                PUSH HL
                LD   HL, BattleEvtMoveMid           ; «] to [»
                CALL Battle_EvtEntW
                POP  HL
                CALL Battle_AddAToHL
                PUSH HL
                LD   A, (BattleMoveDestCell)         ; координата dst
                CALL Battle_AccCoordWrap
                POP  HL
                CALL Battle_AddAToHL
                PUSH HL
                LD   HL, BattleEvtMoveEnd            ; «].»
                CALL Battle_EvtEntW
                POP  HL
                CALL Battle_AddAToHL
                RET

; A=cell → A=ширина координаты «row+1, col+1» (число+comma+число) нативных px. Портит много.
Battle_AccCoordWrap:
                CALL Battle_CellRowColP1           ; B=row+1, A=col+1
                PUSH AF                            ; A=col+1
                LD   A, B                          ; row+1
                CALL Battle_MoveNumW               ; ширина row (нативные цифры)
                LD   C, A
                PUSH BC                            ; C=row-ширина (Battle_EvtEntW клоббит B? нет, но safe)
                LD   HL, BattleEvtComma
                CALL Battle_EvtEntW
                POP  BC
                ADD  A, C
                LD   C, A
                POP  AF                            ; col+1
                CALL Battle_MoveNumW               ; ширина col (нативные цифры)
                ADD  A, C
                RET

Battle_RenderMoveLine:
                CALL Battle_MoveLineW              ; HL = суммарная нативная ширина
                SRL  H
                RR   L
                EX   DE, HL                        ; DE = ширина/2
                LD   HL, 512
                OR   A
                SBC  HL, DE                        ; startX = 512 − ширина/2 (физ px)
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                        ; ×16
                LD   (ResPenX), HL
                LD   HL, BATTLE_EVT_Y
                LD   (ResPenY), HL
                LD   HL, Battle_Status_Begin_DL    ; пролог статуса (палитра + transform 256 + BEGIN)
                LD   BC, Battle_Status_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, BattleEvtMoveHead          ; «Moved »
                CALL Battle_DrawEvtSprite
                CALL Battle_MoveNameAddr            ; «Peasants: »/«Archers: »
                CALL Battle_DrawEvtSprite
                LD   HL, BattleEvtMoveFrom           ; «from [»
                CALL Battle_DrawEvtSprite
                LD   A, (BattleMoveSrcCell)         ; [src]
                CALL Battle_DrawCoord
                LD   HL, BattleEvtMoveMid           ; «] to [»
                CALL Battle_DrawEvtSprite
                LD   A, (BattleMoveDestCell)        ; [dst]
                CALL Battle_DrawCoord
                LD   HL, BattleEvtMoveEnd            ; «].»
                CALL Battle_DrawEvtSprite
                LD   HL, Battle_Status_End_DL
                LD   BC, Battle_Status_End_DL_SIZE
                CALL Render_CmdBufCopy
                RET

; HL=число → нарисовать пером (ResPenX) шрифтом события (BattleEvtDigitTab), без ведущих нулей.
Battle_DrawEvtNum:
                LD   (NumVal), HL
                LD   IX, NumDivisors
                XOR  A
                LD   (NumStarted), A
.dnl:           LD   E, (IX+0)
                LD   D, (IX+1)
                LD   A, D
                OR   E
                JR   Z, .dnend
                LD   HL, (NumVal)
                LD   B, 0
.dns:           OR   A
                SBC  HL, DE
                JR   C, .dnd
                INC  B
                JR   .dns
.dnd:           ADD  HL, DE
                LD   (NumVal), HL
                LD   A, B
                OR   A
                JR   NZ, .dndraw
                LD   A, (NumStarted)
                OR   A
                JR   Z, .dnn
.dndraw:        LD   A, 1
                LD   (NumStarted), A
                LD   A, B
                PUSH IX
                CALL Battle_DrawEvtDigit
                POP  IX
.dnn:           INC  IX
                INC  IX
                JR   .dnl
.dnend:         LD   A, (NumStarted)
                OR   A
                RET  NZ
                XOR  A                              ; число было 0 → нарисовать «0»
Battle_DrawEvtDigit:                               ; A=цифра 0-9 → Render_DrawSpriteEntry(EVT-цифра)
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                         ; A*5
                LD   DE, BattleEvtDigitTab
                ADD  HL, DE
                JP   Battle_DrawEvtSprite

; HL=число → нарисовать ЦЕНТРИРОВАННО относительно ResPenX нативными цифрами счётчика боя
; (BattleCountDigitTab; палитра/transform от Battle_Count_Begin_DL). Глоб.DigitTable затёрт payload'ом.
Battle_DrawCountNum:
                PUSH HL                              ; число
                CALL Num_DigitCount                 ; A = число цифр
                LD   B, A
                LD   A, (BattleCountDigitTab + 3)   ; ширина '0' (моноширинная аппрокс)
                LD   C, A
                XOR  A
.cw:            ADD  A, C
                DJNZ .cw                            ; A = ширина числа (px)
                SRL  A                              ; ширина/2
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                          ; ×16 (vertex 1/16px)
                EX   DE, HL
                LD   HL, (ResPenX)
                OR   A
                SBC  HL, DE                          ; ResPenX = центр − ширина/2
                LD   (ResPenX), HL
                POP  HL                              ; число
Battle_DrawNumLeft:                                 ; HL=число → рисует ОТ ResPenX вправо, продвигая перо
                LD   (NumVal), HL
                LD   IX, NumDivisors
                XOR  A
                LD   (NumStarted), A
.dnl:           LD   E, (IX+0)
                LD   D, (IX+1)
                LD   A, D
                OR   E
                JR   Z, .dne
                LD   HL, (NumVal)
                LD   B, 0
.dns:           OR   A
                SBC  HL, DE
                JR   C, .dnd
                INC  B
                JR   .dns
.dnd:           ADD  HL, DE
                LD   (NumVal), HL
                LD   A, B
                OR   A
                JR   NZ, .dndr
                LD   A, (NumStarted)
                OR   A
                JR   Z, .dnn
.dndr:          LD   A, 1
                LD   (NumStarted), A
                LD   A, B
                PUSH IX
                CALL Battle_DrawCountDigit
                POP  IX
.dnn:           INC  IX
                INC  IX
                JR   .dnl
.dne:           LD   A, (NumStarted)
                OR   A
                RET  NZ
                XOR  A                              ; число было 0 → нарисовать '0'
Battle_DrawCountDigit:                              ; A=цифра 0-9 → Battle_DrawEvtSprite(цифра счётчика)
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                         ; A*5
                LD   DE, BattleCountDigitTab
                ADD  HL, DE
                JP   Battle_DrawEvtSprite

; HL=&запись[lo,mid,hi,w,h] → нарисовать спрайт пером (ResPenX,ResPenY) с ПОЛНЫМ 10-бит stride
; (ширина до 255 — Render_DrawSpriteEntry ломается при w≥128: stride в байте w*2 переполняется).
; Двигает ResPenX += w*16. Палитра/transform/BEGIN — от вызывающего. PALETTED4444 (формат 15).
Battle_DrawEvtSprite:
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL                              ; DE = mid:lo
                LD   A, (HL)
                INC  HL                              ; A = hi
                LD   C, (HL)
                INC  HL                              ; C = w
                LD   B, (HL)                         ; B = h
                PUSH BC                              ; save w,h
                LD   H, #01
                LD   L, A                            ; HL = 0x01:hi, DE = mid:lo
                CALL Render_CmdBufWrite32            ; BITMAP_SOURCE
                POP  BC                              ; C=w, B=h
                ; BITMAP_LAYOUT = 0x07780000 | (w<<9) | h : hi=0x0778|(w>>7), lo=((w&7F)<<9)|h
                PUSH BC
                LD   A, C
                AND  #7F
                LD   H, A
                LD   L, 0
                ADD  HL, HL                          ; HL = (w&7F)<<9
                LD   A, B
                OR   L
                LD   L, A                            ; lo16 = ((w&7F)<<9)|h
                PUSH HL
                LD   A, C
                RLCA
                AND  1                               ; A = w>>7
                OR   #78
                LD   L, A
                LD   H, #07                          ; hi16 = 0x0778|(w>>7)
                POP  DE                              ; DE = lo16
                CALL Render_CmdBufWrite32            ; BITMAP_LAYOUT
                POP  BC
                ; BITMAP_SIZE = 0x08000000 | (w<<9) | h (NEAREST/BORDER): hi=0x0800|(w>>7)
                PUSH BC
                LD   A, C
                AND  #7F
                LD   H, A
                LD   L, 0
                ADD  HL, HL
                LD   A, B
                OR   L
                LD   L, A                            ; lo16
                PUSH HL
                LD   A, C
                RLCA
                AND  1
                LD   L, A
                LD   H, #08                          ; hi16 = 0x0800|(w>>7)
                POP  DE
                CALL Render_CmdBufWrite32            ; BITMAP_SIZE
                POP  BC
                LD   HL, (ResPenX)                   ; VERTEX2F пером
                LD   (RenderPathVertexX), HL
                LD   HL, (ResPenY)
                LD   (RenderPathVertexY), HL
                PUSH BC
                CALL Render_WriteVertex2FCmd
                POP  BC
                LD   A, C                            ; ResPenX += w*16
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                EX   DE, HL
                LD   HL, (ResPenX)
                ADD  HL, DE
                LD   (ResPenX), HL
                RET

; Надписи окна итога нативными спрайтами поверх ×1.6-диалога (заголовок жёлтый / потери белые).
; Запись BattleWinTextTab (10б): [lo,mid,hi,w,h] + палитра(0=бел/1=жёлт) + vx(2) + vy(2).
Battle_RenderWinText:
                LD   HL, BattleWinTextTab
                LD   (BattleWinTextPtr), HL
                LD   B, BATTLE_WIN_TEXT_COUNT
.wtloop:        PUSH BC
                LD   HL, (BattleWinTextPtr)         ; тег видимости (+10): 0=всегда, 1=победа, 2=поражение
                LD   DE, 10
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .wtshow                    ; 0 → всегда показываем
                LD   HL, BattleResult              ; иначе показ только если тег == результат
                CP   (HL)
                JR   NZ, .wtadv                    ; не тот итог → пропустить запись
.wtshow:        LD   HL, (BattleWinTextPtr)         ; палитра-флаг (+5)
                LD   DE, 5
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .wtwhite
                LD   HL, Battle_WinTitle_Begin_DL   ; жёлтый пролог (заголовок)
                LD   BC, Battle_WinTitle_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                JR   .wtpen
.wtwhite:       LD   HL, Battle_Status_Begin_DL     ; белый пролог (потери) — та же палитра, что статус
                LD   BC, Battle_Status_Begin_DL_SIZE
                CALL Render_CmdBufCopy
.wtpen:         LD   HL, (BattleWinTextPtr)         ; ResPenX = vx (+6), ResPenY = vy (+8)
                LD   DE, 6
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   (ResPenX), HL
                LD   HL, (BattleWinTextPtr)
                LD   DE, 8
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   (ResPenY), HL
                LD   HL, (BattleWinTextPtr)         ; спрайт (запись с +0)
                CALL Battle_DrawEvtSprite
                LD   HL, Battle_Status_End_DL
                LD   BC, Battle_Status_End_DL_SIZE
                CALL Render_CmdBufCopy
.wtadv:         LD   HL, (BattleWinTextPtr)         ; → следующая запись
                LD   DE, WIN_TEXT_REC
                ADD  HL, DE
                LD   (BattleWinTextPtr), HL
                POP  BC
                DJNZ .wtloop
                RET

; ─── ПОТЕРИ БОЯ (faithful battle_dialogs.cpp:578-608) ────────────────────────────────────────────
;  Под «Attacker»/«Defender» — строка убитых: иконка MONS32 типа + счёт (killed = Init.count−State.count),
;  либо «None». killed уже в read-only BattleUnitStateInit (старт) минус BattleUnitState (текущий).
CAS_GAP        EQU 2                              ; зазор иконка↔число (px)
CAS_TYPEGAP    EQU 8                              ; зазор между типами (px)
CAS_NUM_DY     EQU 12 * 16                        ; счёт ниже верха иконки (центровка по высоте, vertex)
Battle_RenderCasualties:
                XOR  A                            ; сторона 0 = Attacker
                CALL Battle_CountKilled
                LD   HL, BATTLE_CAS_ATK_Y
                LD   (ResPenY), HL
                CALL Battle_DrawCasualtyBlock
                LD   A, 1                         ; сторона 1 = Defender
                CALL Battle_CountKilled
                LD   HL, BATTLE_CAS_DEF_Y
                LD   (ResPenY), HL
                JP   Battle_DrawCasualtyBlock

; A=сторона → BattleCasK0/K1 = суммарно убито по типам 0/1 (Init.count − State.count).
Battle_CountKilled:
                LD   (BattleSideTmp), A
                LD   HL, 0
                LD   (BattleCasK0), HL
                LD   (BattleCasK1), HL
                LD   IX, BattleUnitState
                LD   IY, BattleUnitStateInit
                LD   B, BATTLE_UNIT_COUNT
.ckl:           LD   A, (IX+2)                    ; side юнита
                LD   C, A
                LD   A, (BattleSideTmp)
                CP   C
                JR   NZ, .cknext
                LD   L, (IY+3)                    ; HL = Init.count (старт)
                LD   H, (IY+4)
                LD   E, (IX+3)                    ; DE = State.count (текущий)
                LD   D, (IX+4)
                OR   A
                SBC  HL, DE                       ; HL = killed (≥0)
                LD   A, (IX+0)                    ; тип 0/1
                OR   A
                JR   NZ, .ckt1
                LD   DE, (BattleCasK0)
                ADD  HL, DE
                LD   (BattleCasK0), HL
                JR   .cknext
.ckt1:          LD   DE, (BattleCasK1)
                ADD  HL, DE
                LD   (BattleCasK1), HL
.cknext:        LD   DE, BATTLE_UNIT_STATE_SIZE
                ADD  IX, DE
                ADD  IY, DE
                DJNZ .ckl
                RET

; Строка потерь по BattleCasK0/K1 на ResPenY: оба 0 → «None» по центру; иначе иконы+счёт по типам.
Battle_DrawCasualtyBlock:
                LD   HL, (BattleCasK0)
                LD   DE, (BattleCasK1)
                LD   A, H
                OR   L
                OR   D
                OR   E
                JP   Z, Battle_DrawCasNone        ; нет потерь стороны → «None» (далеко — JP, не JR)
                ; --- ширина блока → BattleCasW (аккумулятор в памяти: Battle_NumPixW клобчет BC) ---
                XOR  A
                LD   (BattleCasW), A
                LD   HL, (BattleCasK0)
                LD   A, H
                OR   L
                JR   Z, .bw1
                LD   A, 0
                CALL Battle_CasTypeW              ; A = ширина типа0 (иконка+GAP+число)
                LD   B, A
                LD   A, (BattleCasW)
                ADD  A, B
                ADD  A, CAS_TYPEGAP
                LD   (BattleCasW), A
.bw1:           LD   HL, (BattleCasK1)
                LD   A, H
                OR   L
                JR   Z, .bwe
                LD   A, 1
                CALL Battle_CasTypeW
                LD   B, A
                LD   A, (BattleCasW)
                ADD  A, B
                ADD  A, CAS_TYPEGAP
                LD   (BattleCasW), A
.bwe:           LD   A, (BattleCasW)
                SUB  CAS_TYPEGAP                  ; убрать хвостовой зазор
                ; ResPenX = (512 − W/2) × 16
                SRL  A
                LD   H, 0
                LD   L, A
                LD   DE, 512
                EX   DE, HL                       ; HL=512, DE=W/2
                OR   A
                SBC  HL, DE
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                        ; ×16 (vertex)
                LD   (ResPenX), HL
                LD   HL, Battle_Count_Begin_DL     ; пролог: палитра юнитов (нативно)
                LD   BC, Battle_Count_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, (BattleCasK0)
                LD   A, H
                OR   L
                JR   Z, .dr1
                LD   A, 0
                CALL Battle_DrawCasType
.dr1:           LD   HL, (BattleCasK1)
                LD   A, H
                OR   L
                JR   Z, .dre
                LD   A, 1
                CALL Battle_DrawCasType
.dre:           LD   HL, Battle_Count_End_DL
                LD   BC, Battle_Count_End_DL_SIZE
                JP   Render_CmdBufCopy

; A=тип, HL=число убитых → A = ширина [иконка + GAP + число] (px).
Battle_CasTypeW:
                LD   C, A                         ; C=тип
                PUSH HL                           ; число
                ADD  A, A
                ADD  A, A
                ADD  A, C                         ; тип*5
                ADD  A, 3                         ; +поле w
                LD   L, A
                LD   H, 0
                LD   DE, BattleCasualtyIconTab
                ADD  HL, DE
                LD   A, (HL)                      ; ширина иконы
                ADD  A, CAS_GAP                   ; иконка + GAP
                POP  HL                           ; число
                PUSH AF                           ; сохранить (иконка+GAP)
                CALL Battle_NumPixW               ; A = ширина числа (клобчет B,C)
                LD   B, A
                POP  AF
                ADD  A, B
                RET

; A=тип (0/1): иконка MONS32[тип] + счёт BattleCasK<тип>, продвигает ResPenX (+CAS_TYPEGAP).
Battle_DrawCasType:
                LD   C, A                         ; C=тип
                ADD  A, A
                ADD  A, A
                ADD  A, C                         ; тип*5
                LD   L, A
                LD   H, 0
                LD   DE, BattleCasualtyIconTab
                ADD  HL, DE
                CALL Battle_DrawEvtSprite         ; иконка (ResPenX += icon_w)
                LD   HL, (ResPenX)                ; зазор иконка↔число
                LD   DE, CAS_GAP * 16
                ADD  HL, DE
                LD   (ResPenX), HL
                LD   HL, (ResPenY)                ; счёт ниже на CAS_NUM_DY
                PUSH HL
                LD   DE, CAS_NUM_DY
                ADD  HL, DE
                LD   (ResPenY), HL
                LD   A, C
                OR   A
                JR   NZ, .n1
                LD   HL, (BattleCasK0)
                JR   .nd
.n1:            LD   HL, (BattleCasK1)
.nd:            CALL Battle_DrawNumLeft           ; число от ResPenX вправо
                POP  HL                           ; восстановить базовый Y
                LD   (ResPenY), HL
                LD   HL, (ResPenX)                ; зазор между типами
                LD   DE, CAS_TYPEGAP * 16
                ADD  HL, DE
                LD   (ResPenX), HL
                RET

; HL=число (>0) → A = ширина в px = (цифр) × ширина '0'.
Battle_NumPixW:
                CALL Num_DigitCount               ; A = число цифр
                LD   B, A
                LD   A, (BattleCountDigitTab+3)   ; ширина '0'
                LD   C, A
                XOR  A
.npw:           ADD  A, C
                DJNZ .npw
                RET

; «None» по центру (×1.6 бел., статус-палитра). ResPenY уже задан.
Battle_DrawCasNone:
                LD   A, (BattleNoneSprite+3)      ; none_w
                SRL  A
                LD   H, 0
                LD   L, A
                LD   DE, 512
                EX   DE, HL
                OR   A
                SBC  HL, DE                       ; 512 − w/2
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                LD   (ResPenX), HL
                LD   HL, Battle_Status_Begin_DL   ; белая статус-палитра (нативно)
                LD   BC, Battle_Status_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, BattleNoneSprite
                CALL Battle_DrawEvtSprite
                LD   HL, Battle_Status_End_DL
                LD   BC, Battle_Status_End_DL_SIZE
                JP   Render_CmdBufCopy

; Рендер летящей стрелы (faithful RedrawMissileAnimation): пред-масштаб ×1.6, палитра юнитов
; (transform 256 нативно), перо = интерполир. позиция CurX/Y; кадр-направление BattleArrowDir.
Battle_RenderArrow:
                LD   A, (BattleArrowActive)
                OR   A
                RET  Z
                LD   HL, Battle_Count_Begin_DL
                LD   BC, Battle_Count_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, (BattleArrowCurX)
                LD   (ResPenX), HL
                LD   HL, (BattleArrowCurY)
                LD   (ResPenY), HL
                LD   A, (BattleArrowDir)            ; запись = BattleArrowSrcTab + dir*5
                LD   C, A
                ADD  A, A
                ADD  A, A
                ADD  A, C
                LD   L, A
                LD   H, 0
                LD   DE, BattleArrowSrcTab
                ADD  HL, DE
                CALL Battle_DrawEvtSprite
                LD   HL, Battle_Count_End_DL
                LD   BC, Battle_Count_End_DL_SIZE
                JP   Render_CmdBufCopy

; A=вариант (type*2+side); кадр = BattleAnimFrame (0..11, ставит вызывающий через Battle_CalcAnimFrame).
; Эмитит FT_BITMAP_SOURCE[вариант*12+кадр] + LAYOUT/SIZE варианта. Палитра/BEGIN — вызывающий.
Battle_EmitUnitSprite:
                PUSH AF                            ; сохранить вариант
                LD   C, A                          ; C = вариант
                LD   A, (BattleAnimFrame)
                LD   B, A                          ; B = кадр
                LD   A, C                          ; idx = вариант*16 + кадр
                ADD  A, A
                ADD  A, A
                ADD  A, A
                ADD  A, A                          ; вариант*16
                ADD  A, B                          ; + кадр
                ADD  A, A
                ADD  A, A                          ; idx*4 (SRC_SIZE)
                LD   L, A
                LD   H, 0
                LD   DE, BattleUnitSrcTab
                ADD  HL, DE
                LD   BC, BATTLE_UNIT_SRC_SIZE
                CALL Render_CmdBufCopy             ; FT_BITMAP_SOURCE кадра
                POP  AF                            ; вариант
                ADD  A, A
                ADD  A, A
                ADD  A, A                          ; вариант*8
                LD   L, A
                LD   H, 0
                LD   DE, BattleUnitLayTab
                ADD  HL, DE
                LD   BC, BATTLE_UNIT_LAY_SIZE
                JP   Render_CmdBufCopy             ; LAYOUT+SIZE (RET через JP)

; A=индекс юнита → BattleAnimFrame: движущийся → кадр ходьбы; иначе idle (дыхание). Портит A,B,HL.
Battle_CalcAnimFrame:
                LD   B, A                          ; B = индекс юнита
                LD   A, (BattleDeathActive)        ; умирает этот юнит? → DEATH-кадры
                OR   A
                JR   Z, .cafnodeath
                LD   A, (BattleDeathUnit)
                CP   B
                JR   NZ, .cafnodeath
                LD   A, (BattleDeathProg)          ; DEATH_BASE + (prog>>3)&(DEATH_N-1)
                SRL  A
                SRL  A
                SRL  A
                AND  BATTLE_UNIT_DEATH_N - 1
                ADD  A, BATTLE_UNIT_DEATH_BASE
                LD   (BattleAnimFrame), A
                RET
.cafnodeath:    LD   A, (BattleAtkActive)          ; атакует этот юнит? → ATTACK-кадры
                OR   A
                JR   Z, .cafnoatk
                LD   A, (BattleAtkUnit)
                CP   B
                JR   NZ, .cafnoatk
                LD   A, (BattleAtkProg)            ; ATK_BASE + (prog>>2)&(ATK_N-1)
                SRL  A
                SRL  A
                AND  BATTLE_UNIT_ATK_N - 1
                ADD  A, BATTLE_UNIT_ATK_BASE
                LD   (BattleAnimFrame), A
                RET
.cafnoatk:      LD   A, (BattleMoveActive)
                OR   A
                JR   Z, .cafidle
                LD   A, (BattleMoveUnit)
                CP   B
                JR   NZ, .cafidle                  ; не движущийся → idle
                LD   A, (BattleMoveProg)            ; ходьба: WALK_BASE + (prog>>SHIFT)&(WALK_N-1)
                SRL  A
                SRL  A
                AND  BATTLE_UNIT_WALK_N - 1
                ADD  A, BATTLE_UNIT_WALK_BASE
                LD   (BattleAnimFrame), A
                RET
.cafidle:       LD   A, (FrameCounter)             ; idle: IDLE_BASE + (FrameCounter>>3)&3
                SRL  A
                SRL  A
                SRL  A
                AND  3
                ADD  A, BATTLE_UNIT_IDLE_BASE
                LD   (BattleAnimFrame), A
                RET

; A=тип, B=клетка → HL=&BattleUnitPixTab[тип][клетка] (x lo,hi, y lo,hi). Портит A,DE,HL.
Battle_CellPixAddr:
                LD   L, A
                LD   H, 0
                ADD  HL, HL                        ; тип*2
                LD   DE, BattleUnitPixTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                        ; DE = &BattleUnitPix{тип}
                LD   A, B
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                        ; клетка*4
                ADD  HL, DE
                RET

; HL >>= 5 знаково (арифметический сдвиг). Портит B.
Battle_Asr5:
                LD   B, 5
.a5:            SRA  H
                RR   L
                DJNZ .a5
                RET

; Запустить анимацию движения активного юнита из его клетки в BattleMoveDestCell (по таблице пикселей).
Battle_StartMove:
                LD   A, (BattleActiveUnit)
                LD   (BattleMoveUnit), A
                CALL Battle_UnitAddr
                LD   A, (HL)                        ; тип
                LD   (BattleTmpType), A
                INC  HL
                LD   A, (HL)                        ; from-клетка
                LD   (BattleMoveSrcCell), A         ; запомнить src для строки «Moved …: from [src] to [dst].»
                LD   B, A
                LD   A, (BattleTmpType)
                CALL Battle_CellPixAddr             ; HL = &pix[from]
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleMoveCurX), DE           ; CurX = fromX
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleMoveCurY), DE           ; CurY = fromY
                LD   A, (BattleMoveDestCell)        ; to pixel
                LD   B, A
                LD   A, (BattleTmpType)
                CALL Battle_CellPixAddr             ; HL = &pix[dest]
                LD   E, (HL)                        ; toX
                INC  HL
                LD   D, (HL)
                INC  HL
                PUSH HL                             ; &pix dest +2 → toY
                LD   HL, (BattleMoveCurX)           ; stepX = (toX-fromX)>>5
                EX   DE, HL                         ; HL=toX, DE=fromX
                OR   A
                SBC  HL, DE
                CALL Battle_Asr5
                LD   (BattleMoveStepX), HL
                POP  HL                             ; &pix dest +2 (toY)
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                        ; DE = toY
                LD   HL, (BattleMoveCurY)
                EX   DE, HL                         ; HL=toY, DE=fromY
                OR   A
                SBC  HL, DE
                CALL Battle_Asr5
                LD   (BattleMoveStepY), HL
                XOR  A
                LD   (BattleMoveProg), A
                LD   A, 1
                LD   (BattleMoveActive), A
                RET

; Тик анимации движения (каждый кадр): двигать позицию; по приходу — поставить клетку, ударить, ход дальше.
Battle_MoveTick:
                LD   HL, (BattleMoveCurX)
                LD   DE, (BattleMoveStepX)
                ADD  HL, DE
                LD   (BattleMoveCurX), HL
                LD   HL, (BattleMoveCurY)
                LD   DE, (BattleMoveStepY)
                ADD  HL, DE
                LD   (BattleMoveCurY), HL
                LD   A, (BattleMoveProg)
                INC  A
                LD   (BattleMoveProg), A
                CP   BATTLE_MOVE_STEPS
                RET  C                              ; ещё едет
                LD   A, (BattleMoveUnit)            ; ПРИБЫЛ: unit.cell = dest
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (BattleMoveDestCell)
                LD   (HL), A
                XOR  A
                LD   (BattleMoveActive), A
                LD   A, (BattlePendAttack)          ; по приходу — атаковать, если стал соседом
                OR   A
                JR   Z, .mtfin
                XOR  A
                LD   (BattlePendAttack), A
                CALL Battle_AttackAllowed
                JR   Z, .mtfin                      ; не сосед → без атаки
                JP   Battle_StartAttack             ; стал соседом → анимация атаки (она сделает урон+ответку+ход)
.mtfin:         JP   Battle_EndTurn

; Запустить анимацию атаки активного по BattleTargetUnit (флаги WasMelee/MeleePen уже выставил
; AttackAllowed). Урон применяется в ПИКЕ (Battle_AtkTick); по завершении — ответка + ход.
Battle_StartAttack:
                LD   A, (BattleActiveUnit)
                LD   (BattleAtkUnit), A
                XOR  A
                LD   (BattleAtkProg), A
                LD   (BattleAtkHit), A
                LD   A, 1
                LD   (BattleAtkActive), A
                LD   A, (BattleWasMelee)            ; дальний выстрел (НЕ мили) → запустить стрелу
                OR   A
                RET  NZ
                ; падение сквозь в Battle_StartArrow
; Запуск полёта стрелы: старт = пиксель атакующего, конец = пиксель цели; шаг = (end−start)>>3.
Battle_StartArrow:
                LD   A, (BattleAtkUnit)             ; атакующий → CurX/Y + направление
                CALL Battle_UnitAddr
                LD   A, (HL)                        ; тип
                LD   C, A
                INC  HL
                LD   A, (HL)                        ; клетка
                LD   B, A
                INC  HL
                LD   A, (HL)                        ; сторона → направление (0=вправо/1=влево)
                LD   (BattleArrowDir), A
                LD   A, C
                CALL Battle_CellPixAddr             ; HL = &pix[atk] (x lo,hi, y lo,hi)
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleArrowCurX), DE
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleArrowCurY), DE
                LD   A, (BattleTargetUnit)          ; цель → EndX/Y
                CALL Battle_UnitAddr
                LD   A, (HL)
                LD   C, A
                INC  HL
                LD   A, (HL)
                LD   B, A
                LD   A, C
                CALL Battle_CellPixAddr             ; HL = &pix[tgt]
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleArrowEndX), DE
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleArrowEndY), DE
                LD   HL, (BattleArrowEndX)          ; stepX = (End−Cur)>>3
                LD   DE, (BattleArrowCurX)
                OR   A
                SBC  HL, DE
                CALL Battle_Asr3
                LD   (BattleArrowStepX), HL
                LD   HL, (BattleArrowEndY)          ; stepY = (End−Cur)>>3
                LD   DE, (BattleArrowCurY)
                OR   A
                SBC  HL, DE
                CALL Battle_Asr3
                LD   (BattleArrowStepY), HL
                XOR  A
                LD   (BattleArrowProg), A
                INC  A
                LD   (BattleArrowActive), A
                RET

; HL >>= 3 знаково (арифметический сдвиг). Портит B.
Battle_Asr3:
                LD   B, 3
.asr3l:         SRA  H
                RR   L
                DJNZ .asr3l
                RET

; Тик анимации атаки (каждый кадр): в пике — применить урон; по завершении — ответка + след.ход.
Battle_AtkTick:
                LD   A, (BattleArrowActive)         ; стрела в полёте → двигать к цели (долетает к пику)
                OR   A
                JR   Z, .noarrow
                LD   HL, (BattleArrowCurX)
                LD   DE, (BattleArrowStepX)
                ADD  HL, DE
                LD   (BattleArrowCurX), HL
                LD   HL, (BattleArrowCurY)
                LD   DE, (BattleArrowStepY)
                ADD  HL, DE
                LD   (BattleArrowCurY), HL
                LD   A, (BattleArrowProg)
                INC  A
                LD   (BattleArrowProg), A
                CP   BATTLE_ATK_STEPS / 2
                JR   C, .noarrow
                XOR  A
                LD   (BattleArrowActive), A         ; долетела (в момент урона)
.noarrow:       LD   A, (BattleAtkProg)
                INC  A
                LD   (BattleAtkProg), A
                CP   BATTLE_ATK_STEPS / 2            ; ПИК → урон (один раз)
                JR   NZ, .atknotpeak
                LD   A, (BattleAtkHit)
                OR   A
                JR   NZ, .atknotpeak
                LD   A, 1
                LD   (BattleAtkHit), A
                CALL Battle_Attack                  ; урон цели (active→target, флаги уже выставлены)
.atknotpeak:    LD   A, (BattleAtkProg)
                CP   BATTLE_ATK_STEPS
                RET  C                              ; ещё играет
                XOR  A                              ; ЗАВЕРШЕНА
                LD   (BattleAtkActive), A
                CALL Battle_Retaliate               ; ответка цели (мили, жива, не отвечала)
                LD   A, (BattleDeathPend)            ; кто-то умер? → анимация смерти (потом ход)
                OR   A
                JR   Z, .atkdone
                XOR  A
                LD   (BattleDeathPend), A
                LD   (BattleDeathProg), A
                LD   A, 1
                LD   (BattleDeathActive), A         ; BattleDeathUnit уже выставлен в Battle_Attack
                RET
.atkdone:       JP   Battle_EndTurn

; Тик анимации смерти: играть DEATH-кадры; по завершении — умирающий исчезает (count уже 0), след.ход.
Battle_DeathTick:
                LD   A, (BattleDeathProg)
                INC  A
                LD   (BattleDeathProg), A
                CP   BATTLE_DEATH_STEPS
                RET  C                              ; ещё играет
                XOR  A
                LD   (BattleDeathActive), A          ; завершена → отряд исчез (count==0, не рисуется)
                JP   Battle_EndTurn

; ============================================================================
; AI боя (ai_battle.cpp planUnitTurn, упрощённо для безгеройного skirmish — без спеллов/
; ретрита/осады). Дерево: найти лучшую цель (угроза=урон×count) → СТРЕЛОК: выстрелить лучшую;
; МИЛИ: цель в досягаемости → ударить, иначе подойти к ней (ближайшая достижимая клетка) и
; ударить, если стал соседом; иначе — пропуск. После действия — ответка/след.ход/конец.
; ============================================================================

; Управляет ли AI текущим активным? Авто-режим → да (обе стороны); иначе только защитник (side1).
; Ход гейтится по кадрам (видимость). OUT: A=1 если AI владеет ходом (caller НЕ даёт ввод человеку),
; A=0 если ходит человек (side0 в ручном режиме).
; Владеет ли ходом AI (а не человек)? Авто-режим → да для всех; иначе только защитник (side1).
; OUT: A=1 если AI, A=0 если человек (side0 в ручном режиме). Портит HL.
Battle_AIControlsActive:
                LD   A, (BattleAutoMode)
                OR   A
                JR   NZ, .yes
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                LD   A, (HL)                        ; side активного
                CP   1
                JR   Z, .yes
                XOR  A
                RET
.yes:           LD   A, 1
                RET

; AI ходит сам (gate по кадрам для видимости). OUT: A=1 если AI владеет ходом (caller не даёт
; ввод человеку), A=0 если ходит человек.
Battle_AIMaybeAct:
                CALL Battle_AIControlsActive
                OR   A
                RET  Z                              ; человек → 0
                LD   A, (FrameCounter)              ; гейт: ходить раз в 32 кадра (бой видно)
                AND  BATTLE_AI_GATE_MASK
                JR   Z, .act
                LD   A, 1                           ; не этот кадр, но ход всё равно за AI
                RET
.act:           CALL Battle_AITurn
                LD   A, 1
                RET

; Один ход AI для BattleActiveUnit: выбрать цель и действие, применить, передать ход.
Battle_AITurn:
                CALL Battle_AIFindTarget            ; BattleTargetUnit = лучшая цель (#FF если нет)
                LD   A, (BattleTargetUnit)
                CP   #FF
                JP   Z, .endturn                    ; целей нет → пропуск хода
                CALL Battle_AIActiveIsArcher        ; A=1 стрелок / 0 мили
                OR   A
                JR   Z, .melee
                ; СТРЕЛОК: выстрелить лучшую цель (AttackAllowed для стрелка всегда разрешает;
                ; если цель-сосед — выставит мили-штраф ÷2 и возможна ответка, как блокированный лучник)
                CALL Battle_AttackAllowed
                JP   Battle_StartAttack             ; стрелок → анимация атаки (она сделает урон+ответку+ход)
.melee:         CALL Battle_AttackAllowed           ; цель уже в соседней клетке?
                JR   Z, .approach
                JP   Battle_StartAttack             ; мили-сосед → анимация атаки
.approach:      CALL Battle_ComputeReachable        ; нет — подойти: ближайшая достижимая клетка к цели
                CALL Battle_AIMoveToward             ; → BattleMoveDestCell (клетку НЕ ставит)
                LD   A, (BattleActiveUnit)            ; некуда идти (dest==текущая)? → пропуск хода
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)
                LD   HL, BattleMoveDestCell
                CP   (HL)
                JR   Z, .endturn
                CALL Battle_StartMove                ; запустить анимацию движения; ход завершит Battle_MoveTick
                LD   A, 1
                LD   (BattlePendAttack), A           ; по приходу — проверить соседство и ударить
                RET
.endturn:       JP   Battle_EndTurn
; Завершение хода (общее для AITurn/AtkTick/MoveTick): след.ход + конец + страховка раунд-лимита.
Battle_EndTurn:
                CALL Battle_NextTurn
                CALL Battle_CheckEnd
                LD   A, (BattleResult)               ; бой кончился? → выход
                OR   A
                RET  NZ
                LD   A, (BattleRound)                ; страховка авто: лимит раундов → принудительный итог
                CP   BATTLE_AI_MAX_ROUND
                RET  C
                ; падение сквозь: round>=cap → решить по числу живых стеков
; Принудительный итог (анти-зависание авто): больше живых стеков у side0 → Victory, иначе Defeat.
Battle_AIForceEnd:
                XOR  A
                CALL Battle_SideAlive               ; живых стеков side0
                LD   B, A
                LD   A, 1
                CALL Battle_SideAlive               ; живых стеков side1
                CP   B
                JR   C, .fe_win                     ; side1 < side0 → победа атакующего
                LD   A, 2                            ; иначе поражение
                LD   (BattleResult), A
                RET
.fe_win:        LD   A, 1
                LD   (BattleResult), A
                RET

; Лучшая цель AI = живой ВРАГ с макс. угрозой (getPotentialDamage ≈ count×avgdmg). Эталон
; evaluateThreatForUnit (берётся максимум). OUT: BattleTargetUnit (#FF если врагов нет).
Battle_AIFindTarget:
                LD   A, (BattleActiveUnit)           ; сторона активного (стабильно в var: ниже пейджинг)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                LD   A, (HL)
                LD   (BattleAISide), A
                LD   A, #FF
                LD   (BattleAIBestTgt), A
                XOR  A
                LD   (BattleAIBestScore), A
                LD   (BattleAIBestScore + 1), A
                LD   C, 0
.ftloop:        LD   A, C
                CALL Battle_UnitAddr                 ; HL = &state[C] (=&type)
                PUSH HL                              ; враг? side != active.side
                INC  HL
                INC  HL
                LD   A, (HL)
                LD   HL, BattleAISide
                CP   (HL)
                POP  HL
                JR   Z, .ftnext                      ; своя сторона → не цель
                PUSH HL                              ; жив? count
                INC  HL
                INC  HL
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                         ; DE = count
                POP  HL                              ; HL = &type
                LD   A, D
                OR   E
                JR   Z, .ftnext                      ; мёртв
                LD   A, (HL)                         ; avgdmg(type+1) из #91
                INC  A
                LD   B, A                            ; monster id
                PUSH BC                              ; сохранить C(индекс)+B(id) через пейджинг
                PUSH DE                              ; сохранить count
                CALL MonsterStats_Read               ; клоббит BC/DE/HL
                LD   A, (MonsterStatBuf + 2)         ; dmgMin
                LD   C, A
                LD   A, (MonsterStatBuf + 3)         ; dmgMax
                ADD  A, C
                SRL  A                               ; avg = (min+max)/2
                POP  DE                              ; DE = count
                LD   B, A                            ; B = avg (множитель)
                LD   HL, 0                           ; score = count×avg (повторное сложение, cap FFFF)
                OR   A
                JR   Z, .ftscore                     ; avg 0 → score 0
.ftmul:         ADD  HL, DE
                JR   C, .ftcap
                DJNZ .ftmul
                JR   .ftscore
.ftcap:         LD   HL, #FFFF
.ftscore:       PUSH HL                              ; score
                LD   DE, (BattleAIBestScore)
                OR   A
                SBC  HL, DE                          ; score − best
                POP  HL                              ; score
                POP  BC                              ; восстановить C(индекс)
                JR   C, .ftnext                      ; score < best → пропуск
                JR   Z, .ftnext                      ; равно → оставить первого
                LD   (BattleAIBestScore), HL         ; новый максимум
                LD   A, C
                LD   (BattleAIBestTgt), A
.ftnext:        INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JR   C, .ftloop
                LD   A, (BattleAIBestTgt)
                LD   (BattleTargetUnit), A
                RET

; A=1 если активный — стрелок (shots>0 из #91), иначе A=0. Портит BC,DE,HL.
Battle_AIActiveIsArcher:
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                LD   A, (HL)
                INC  A
                LD   B, A
                CALL MonsterStats_Read
                LD   A, (MonsterStatBuf + 7)         ; shots
                OR   A
                RET  Z
                LD   A, 1
                RET

; Подойти к цели: среди достижимых (BattleReach) ПУСТЫХ клеток (+своя origin) выбрать ближайшую
; к клетке цели по dist²=(Δряд)²+(Δкол)²; поставить туда active.cell. Эталон: «идти к цели» AI.
Battle_AIMoveToward:
                LD   A, (BattleTargetUnit)           ; ряд/кол цели
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)
                CALL Battle_CellRowCol               ; B=ряд, A=кол
                LD   (BattleAITCol), A
                LD   A, B
                LD   (BattleAITRow), A
                LD   A, (BattleActiveUnit)           ; старт-лучшая = текущая клетка активного
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)
                LD   (BattleAIBestCell), A
                CALL Battle_AICellDist
                LD   (BattleAIBestDist), A
                LD   C, 0
.mtloop:        LD   A, C                            ; достижима?
                LD   L, A
                LD   H, 0
                LD   DE, BattleReach
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .mtnext                      ; reach==0 → нет
                LD   A, (BattleActiveUnit)            ; c == своя origin? (стоять можно)
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)
                CP   C
                JR   Z, .mtcand
                PUSH BC                              ; иначе клетка должна быть пустой
                LD   A, C
                CALL Battle_FindUnitAtCell
                POP  BC
                CP   #FF
                JR   NZ, .mtnext                     ; занята → пропуск
.mtcand:        PUSH BC                              ; dist² этой клетки
                LD   A, C
                CALL Battle_AICellDist
                LD   B, A
                LD   A, (BattleAIBestDist)
                CP   B
                JR   C, .mtpop                       ; best<d → не лучше
                JR   Z, .mtpop                       ; равно → оставить
                LD   A, B                            ; d<best → обновить
                LD   (BattleAIBestDist), A
                POP  BC
                LD   A, C
                LD   (BattleAIBestCell), A
                JR   .mtnext
.mtpop:         POP  BC
.mtnext:        INC  C
                LD   A, C
                CP   99
                JR   C, .mtloop
                LD   A, (BattleAIBestCell)            ; цель движения (клетку ставит StartMove по приходу)
                LD   (BattleMoveDestCell), A
                RET

; A=cell → A=dist²=(Δряд)²+(Δкол)² до (BattleAITRow/Col). Макс 164 (8-бит). Портит BC,DE,HL.
Battle_AICellDist:
                CALL Battle_CellRowCol               ; B=ряд, A=кол
                LD   C, B                            ; C=ряд
                LD   HL, BattleAITCol
                SUB  (HL)                            ; кол−tcol
                JR   NC, .cdc
                NEG
.cdc:           PUSH BC                              ; сохранить ряд (C)
                CALL Battle_SqA                      ; A=Δкол²
                POP  BC
                LD   B, A                            ; B=Δкол²
                LD   A, C                            ; ряд
                LD   HL, BattleAITRow
                SUB  (HL)
                JR   NC, .cdr
                NEG
.cdr:           PUSH BC                              ; сохранить Δкол²
                CALL Battle_SqA                      ; A=Δряд²
                POP  BC
                ADD  A, B                            ; +Δкол²
                RET

; A=cell → B=ряд (cell÷11), A=кол (cell mod 11). Сетка 11×9.
Battle_CellRowCol:
                LD   B, 0
.rcloop:        CP   11
                JR   C, .rcdone
                SUB  11
                INC  B
                JR   .rcloop
.rcdone:        RET

; A=A² (вход ≤12, выход ≤144, 8-бит). Портит BC.
Battle_SqA:
                OR   A
                RET  Z
                LD   C, A
                LD   B, A
                XOR  A
.sqloop:        ADD  A, C
                DJNZ .sqloop
                RET

; Клик по зоне кнопки Auto? Читает мышь (Input_MouseX/Y). OUT: A=1 (NZ) попал, A=0 (Z) мимо.
Battle_CheckAutoClick:
                CALL Input_MouseX
                LD   DE, BATTLE_AUTO_X0
                OR   A
                SBC  HL, DE
                JR   C, .miss
                CALL Input_MouseX
                LD   DE, BATTLE_AUTO_X1
                OR   A
                SBC  HL, DE
                JR   NC, .miss
                CALL Input_MouseY
                LD   DE, BATTLE_AUTO_Y0
                OR   A
                SBC  HL, DE
                JR   C, .miss
                CALL Input_MouseY
                LD   DE, BATTLE_AUTO_Y1
                OR   A
                SBC  HL, DE
                JR   NC, .miss
                LD   A, 1
                RET
.miss:          XOR  A
                RET

; Разрешена ли атака активного по BattleTargetUnit? Стрелок (shots>0 из #91, MonsterStatBuf+7)
; бьёт куда угодно; ближний — только если цель в соседней клетке (BattleAdjTab 99×6).
; OUT: A!=0 (NZ) разрешено, A=0 (Z) нельзя. Эталон fheroes2 battle_board GetIndexDirection.
; ВАЖНО: соседство (чтение BattleAdjTab в slot3=#A8) — ПЕРВЫМ, ДО MonsterStats_Read.
; MonsterStats_Read пейджит slot3→#91→назад; на РЕАЛЬНОМ железе чтение slot3 СРАЗУ после него
; ломалось (харнесс этого не ловил!) → гейт ошибочно блокировал ближние атаки. Поэтому shots — ПОСЛЕДНИМ.
Battle_AttackAllowed:
                LD   A, (BattleActiveUnit)         ; HL = &BattleAdjTab[active_cell*6]
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)                       ; active cell
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L                          ; DE = cell
                ADD  HL, HL                        ; 2c
                ADD  HL, HL                        ; 4c
                ADD  HL, DE                        ; 5c
                ADD  HL, DE                        ; 6c
                LD   DE, BattleAdjTab
                ADD  HL, DE                        ; &adj[cell*6]
                PUSH HL
                LD   A, (BattleTargetUnit)
                CALL Battle_UnitAddr
                INC  HL
                LD   C, (HL)                       ; target cell
                POP  HL
                LD   B, 6
                LD   D, 0                           ; D = флаг «сосед»
.aaloop:        LD   A, (HL)
                CP   C
                JR   Z, .aaadj
                INC  HL
                DJNZ .aaloop
                JR   .aashots                       ; не сосед → D=0
.aaadj:         LD   D, 1
.aashots:       PUSH DE                            ; сохранить флаг соседства (D) через MonsterStats_Read
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                LD   A, (HL)                       ; active.type
                INC  A
                LD   B, A
                CALL MonsterStats_Read             ; теперь можно пейджить — adj уже прочитан
                LD   A, (MonsterStatBuf + 7)       ; shots
                POP  DE                            ; D = флаг соседства
                LD   C, A                          ; C = shots (сохранить)
                LD   A, D
                LD   (BattleWasMelee), A           ; N2c: атака ближняя iff цель — сосед (D) → возможна ответка
                ; --- N2b: лучник в упор → ÷2: shots>0 AND сосед ---
                XOR  A
                OR   C
                JR   Z, .ampoff                    ; не лучник
                LD   A, D
                OR   A
                JR   Z, .ampoff                    ; не сосед
                LD   A, 1                           ; лучник + сосед → штраф
                JR   .ampw
.ampoff:        XOR  A
.ampw:          LD   (BattleMeleePen), A
                LD   A, C                          ; восстановить shots
                OR   A
                JR   NZ, .aaallow                  ; стрелок → можно куда угодно
                LD   A, D                          ; ближний: можно iff сосед (A=D: NZ можно / Z нельзя)
                OR   A
                RET
.aaallow:       LD   A, 1                          ; стрелок → можно
                RET

; Достижимые клетки активного: flood по соседям (BattleAdjTab) на глубину speed (#91).
; BattleReach[c]: 0=нет, 1..speed=дист, #FF=origin. Препятствия (юниты) учитываются при ШЕЙДЕ
; (рендер), а не в flood — для простоты (юнитов мало). Faithful-приближение fheroes2.
Battle_ComputeReachable:
                LD   HL, BattleReach               ; очистить 99
                LD   B, 99
.crclr:         LD   (HL), 0
                INC  HL
                DJNZ .crclr
                LD   A, (BattleActiveUnit)          ; speed активного
                CALL Battle_UnitSpeed
                LD   (BattleReachSpd), A
                LD   A, (BattleActiveUnit)          ; reach[active_cell]=#FF (origin)
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)
                LD   E, A
                LD   D, 0
                LD   HL, BattleReach
                ADD  HL, DE
                LD   (HL), #FF
                LD   A, 1                            ; шаг d=1..speed
.crpass:        LD   (BattleReachStep), A
                LD   HL, BattleReachSpd
                CP   (HL)
                JR   Z, .crdo
                JR   C, .crdo
                RET                                  ; d>speed → готово
.crdo:          LD   A, (BattleReachStep)            ; источник = (d==1? #FF : d-1)
                CP   1
                JR   NZ, .crdm1
                LD   A, #FF
                JR   .crsset
.crdm1:         DEC  A
.crsset:        LD   (BattleReachSrc), A
                LD   C, 0                            ; клетка
.crcell:        LD   A, C
                LD   L, A
                LD   H, 0
                LD   DE, BattleReach
                ADD  HL, DE
                LD   A, (HL)
                LD   HL, BattleReachSrc
                CP   (HL)
                JR   NZ, .crcnext                    ; reach[c]!=источник
                LD   A, C                            ; &adj[c*6]
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE
                ADD  HL, DE
                LD   DE, BattleAdjTab
                ADD  HL, DE
                LD   B, 6
.crnb:          LD   A, (HL)
                PUSH HL
                PUSH BC
                CP   #FF
                JR   Z, .crnbsk                      ; нет соседа
                LD   L, A
                LD   H, 0
                LD   DE, BattleReach
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   NZ, .crnbsk                     ; уже помечен
                LD   A, (BattleReachStep)
                LD   (HL), A                         ; reach[n]=d
.crnbsk:        POP  BC
                POP  HL
                INC  HL
                DJNZ .crnb
.crcnext:       INC  C
                LD   A, C
                CP   99
                JR   C, .crcell
                LD   A, (BattleReachStep)
                INC  A
                JR   .crpass

; Статус-подсказка по наведённой клетке (fheroes2 battle_interface.cpp:2889/2914/2928/3009):
; BattleStatusMsg: 0=Turn N; 1/2=Move Peasant/Archer here; 3/4=Attack Peasant/Archer;
; 5/6=Shoot Peasant/Archer; 7/8=View Peasant/Archer info. Пусто+достижима→Move; враг+можно→
; Shoot(стрелок)/Attack(ближний сосед); свой отряд (или своя клетка)→View info (faithful).
Battle_ComputeStatus:
                XOR  A
                LD   (BattleStatusMsg), A          ; по умолчанию Turn N
                LD   A, (BattleHoverCell)
                CP   #FF
                RET  Z                              ; вне поля → Turn N
                CALL Battle_FindUnitAtCell          ; A = живой юнит в клетке (#FF=пусто)
                CP   #FF
                JR   Z, .stempty
                LD   (BattleTargetUnit), A          ; занято: цель
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                LD   C, (HL)                        ; target.side
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                LD   A, (HL)                        ; active.side
                CP   C
                JR   Z, .stview                    ; свой отряд → «View %{monster} info» (faithful)
                CALL Battle_AttackAllowed           ; враг: можно дотянуться? (стрелок везде/ближний сосед)
                OR   A
                RET  Z                              ; нельзя → Turn N
                LD   A, (BattleActiveUnit)           ; стрелок? shots>0 → Shoot, иначе Attack
                CALL Battle_UnitAddr
                LD   A, (HL)
                INC  A
                LD   B, A
                CALL MonsterStats_Read
                LD   A, (MonsterStatBuf + 7)        ; shots активного
                LD   B, A                           ; B = shots (сохранить через UnitAddr)
                LD   A, (BattleTargetUnit)
                CALL Battle_UnitAddr
                LD   C, (HL)                        ; C = target.type (0/1)
                LD   A, B
                OR   A                              ; shots==0? (melee)
                LD   A, C                           ; A = target.type (LD флаги не трогает)
                JR   Z, .stmelee
                ADD  A, 5                            ; Shoot: 5=Peasant,6=Archer
                LD   (BattleStatusMsg), A
                RET
.stmelee:       ADD  A, 3                            ; Attack: 3=Peasant,4=Archer
                LD   (BattleStatusMsg), A
                RET
.stview:        LD   A, (BattleTargetUnit)           ; «View %{monster} info»: 7=Peasant,8=Archer (по типу цели)
                CALL Battle_UnitAddr
                LD   A, (HL)                        ; target.type
                ADD  A, 7
                LD   (BattleStatusMsg), A
                RET
.stempty:       LD   A, (BattleHoverCell)            ; пусто: достижима? BattleReach[cell] in 1..speed
                LD   L, A
                LD   H, 0
                LD   DE, BattleReach
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                RET  Z                              ; недостижима → Turn N
                CP   #FF
                JR   Z, .storigin                  ; origin (под активным) → View info активного (faithful)
                LD   A, (BattleActiveUnit)           ; достижима → Move <active> here
                CALL Battle_UnitAddr
                LD   A, (HL)
                INC  A                              ; 1=Move Peasant,2=Move Archer
                LD   (BattleStatusMsg), A
                RET
.storigin:      LD   A, (BattleActiveUnit)           ; своя клетка активного → «View %{monster} info»
                CALL Battle_UnitAddr
                LD   A, (HL)                        ; active.type
                ADD  A, 7                           ; 7=View Peasant,8=View Archer
                LD   (BattleStatusMsg), A
                RET

; Вычислить наведённую гекс-ячейку из курсора (логич. 640×480). OUT: BattleHoverCell (#FF=нет).
; Геометрия battle_cell.cpp:258 — row=(my−62)/42 [0..8], col=(mx−89+нечёт?22:0)/44 [0..10],
; cell=row*11+col. Приближение прямоугольником (без точного гекс-теста) — для подсветки ок.
Battle_ComputeHover:
                CALL Input_MouseY                 ; HL = my
                LD   DE, 62                        ; CELL_OY
                OR   A
                SBC  HL, DE
                JP   C, .none                      ; my < 62 — выше поля
                LD   B, 0
.rdiv:          LD   DE, 42                        ; ROW_STEP
                OR   A
                SBC  HL, DE
                JR   C, .rdone
                INC  B
                JR   .rdiv
.rdone:         LD   A, B
                CP   9
                JP   NC, .none                     ; ряд > 8 — ниже поля
                LD   (BattleTmpRow), A
                AND  1
                LD   C, 0                           ; смещение X нечётного ряда
                JR   Z, .even
                LD   C, 22                          ; CELL_W/2
.even:          CALL Input_MouseX                  ; HL = mx
                LD   DE, 89                         ; CELL_OX
                OR   A
                SBC  HL, DE                         ; mx−89 (может быть <0)
                LD   E, C
                LD   D, 0
                ADD  HL, DE                         ; mx−89+смещение
                BIT  7, H
                JP   NZ, .none                      ; <0 — слева от поля
                LD   B, 0
.cdiv:          LD   DE, 44                         ; CELL_W
                OR   A
                SBC  HL, DE
                JR   C, .cdone
                INC  B
                JR   .cdiv
.cdone:         LD   A, B
                CP   11                             ; WIDTH_IN_CELLS
                JP   NC, .none                      ; колонка > 10 — справа от поля
                LD   C, A                           ; col
                LD   A, (BattleTmpRow)
                LD   B, A
                ADD  A, A                           ; 2r
                ADD  A, A                           ; 4r
                ADD  A, A                           ; 8r
                ADD  A, B                           ; 9r
                ADD  A, B                           ; 10r
                ADD  A, B                           ; 11r = row*11
                ADD  A, C                           ; + col
                LD   (BattleHoverCell), A
                RET
.none:          LD   A, #FF
                LD   (BattleHoverCell), A
                RET

; Рендер боя: новый DL = Battle_DL (CLEAR + два битмапа поля ×1.6) + подсветка ячейки + курсор + swap.
; Зовётся через Render_Battle_Tramp. Хелперы slot3-safe.
Render_Battle:
                FT_CMD_Start
                LD   HL, #FFFF                    ; CMD_DLSTART (новый DL, offset 0)
                LD   DE, #FF00
                CALL Render_CmdBufWrite32
                LD   HL, Battle_DL
                LD   BC, Battle_DL_SIZE
                CALL Render_CmdBufCopy
                ; ФИНАЛ (BattleResult≠0): модальное окно итога поверх. ВСЁ поле (тени достижимости,
                ; 99 счёт-баров, контуры, статус) — пропускаем: за окном не видно, а CMD-FIFO=4096Б
                ; переполняется (поздние команды бьются). Рисуем только фон + окно итога + потери.
                LD   A, (BattleResult)
                OR   A
                JP   NZ, .no_status
                ; --- ДОСТИЖИМЫЕ КЛЕТКИ активного: тень на пустых клетках в радиусе speed (#91).
                ;     BattleReach уже посчитан в Battle_Update; шейдим reach 1..speed И пустые. ---
                LD   HL, Battle_Shadow_Pre_DL
                LD   BC, Battle_Shadow_Pre_DL_SIZE
                CALL Render_CmdBufCopy
                XOR  A
                LD   (BattleRshCell), A
.rsh:           LD   A, (BattleRshCell)
                LD   L, A
                LD   H, 0
                LD   DE, BattleReach
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .rshnext                     ; недостижима
                CP   #FF
                JR   Z, .rshnext                     ; origin (под активным)
                LD   A, (BattleRshCell)              ; пустая? FindUnitAtCell==#FF
                CALL Battle_FindUnitAtCell
                CP   #FF
                JR   NZ, .rshnext                    ; занято юнитом
                LD   A, (BattleRshCell)              ; вершина top-left = BattleCellVerts[c*8]
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                LD   DE, BattleCellVerts
                ADD  HL, DE
                LD   BC, 4
                CALL Render_CmdBufCopy
.rshnext:       LD   A, (BattleRshCell)
                INC  A
                LD   (BattleRshCell), A
                CP   99
                JR   C, .rsh
                LD   HL, Battle_Shadow_Post_DL
                LD   BC, Battle_Shadow_Post_DL_SIZE
                CALL Render_CmdBufCopy
                ; --- ГЕКС-ТЕНЬ наведённой клетки (faithful hover, как fheroes2 _hexagonCursorShadow:
                ;     тёмная ШЕСТИУГОЛЬНАЯ тень, НЕ жёлтый прямоугольник). Спрайт-маска ПОД юнитами.
                ;     Активный-отряд индикатор (контур спрайта) — отдельный TODO. ---
                LD   A, (BattleHoverCell)
                CP   #FF
                JR   Z, .no_shadow
                PUSH AF
                LD   HL, Battle_Shadow_Pre_DL
                LD   BC, Battle_Shadow_Pre_DL_SIZE
                CALL Render_CmdBufCopy
                POP  AF
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                       ; cell*8
                LD   DE, BattleCellVerts
                ADD  HL, DE
                LD   BC, 4                          ; первая FT_VERTEX2F = top-left клетки
                CALL Render_CmdBufCopy
                LD   HL, Battle_Shadow_Post_DL
                LD   BC, Battle_Shadow_Post_DL_SIZE
                CALL Render_CmdBufCopy
.no_shadow:
                LD   A, (BattleMoveActive)         ; активный движется → контур не рисуем (застрял бы на старой клетке)
                OR   A
                JP   NZ, .contour_done
                ; --- КОНТУР активного отряда (faithful, как fheroes2 — обводка спрайта): силуэт
                ;     спрайта циан-палитрой, смещённый ±2px ×4, ПОД реальным спрайтом (тот закроет
                ;     центр → останется 2px обводка). Читаем тип/cell/side активного. ---
                LD   A, (BattleActiveUnit)
                CP   BATTLE_UNIT_COUNT
                JP   NC, .contour_done            ; активный невалиден (#FF) → контур НЕ рисуем (иначе мусор-спрайт ломает DL)
                CALL Battle_UnitAddr
                LD   A, (HL)                      ; active.type
                LD   (BattleTmpType), A
                INC  HL
                LD   A, (HL)                      ; active.cell
                LD   (BattleTmpCell), A
                INC  HL
                LD   A, (HL)                      ; active.side
                LD   (BattleTmpSide), A
                INC  HL
                LD   A, (HL)                      ; active.count_lo
                INC  HL
                OR   (HL)                         ; | count_hi
                JP   Z, .contour_done             ; активный мёртв → контур НЕ рисуем (faithful + защита DL)
                LD   A, (BattleActiveUnit)         ; кадр анимации контура (idle активного)
                CALL Battle_CalcAnimFrame
                LD   HL, Battle_Contour_Begin_DL
                LD   BC, Battle_Contour_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (BattleTmpType)           ; вариант = type*2+side → SOURCE кадра + LAYOUT/SIZE
                ADD  A, A
                LD   C, A
                LD   A, (BattleTmpSide)
                ADD  A, C
                CALL Battle_EmitUnitSprite        ; контур текущего кадра (палитра-силуэт от пролога)
                LD   A, (BattleTmpType)           ; вершина = BattleUnitVertsTab[type] + cell*4
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, BattleUnitVertsTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   A, (BattleTmpCell)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                       ; cell*4
                ADD  HL, DE
                LD   (BattleContourVtx), HL       ; &вершина активного
                LD   B, 4                          ; 4 смещения силуэта
                LD   C, 0                          ; индекс смещения
.contloop:      PUSH BC
                LD   A, C                          ; BattleContourOfsTab[C] → &смещение
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                LD   DE, BattleContourOfsTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   BC, BATTLE_CONTOUR_OFS_SIZE   ; VERTEX_TRANSLATE_X+Y
                CALL Render_CmdBufCopy
                LD   HL, (BattleContourVtx)        ; вершина силуэта
                LD   BC, 4
                CALL Render_CmdBufCopy
                POP  BC
                INC  C
                DJNZ .contloop
                LD   HL, Battle_Contour_End_DL     ; сброс TRANSLATE 0 + END
                LD   BC, Battle_Contour_End_DL_SIZE
                CALL Render_CmdBufCopy
.contour_done:
                ; --- ДИНАМИЧЕСКИЕ ЮНИТЫ из таблицы состояния: BEGIN BITMAPS + per-юнит
                ;     (префикс SOURCE/LAYOUT/SIZE по варианту type*2+side + вершина по type,cell) + END ---
                LD   HL, Battle_Units_Begin_DL
                LD   BC, Battle_Units_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, BattleUnitState
                LD   (BattleUnitPtr), HL
                XOR  A
                LD   (BattleRenderIdx), A
                LD   B, BATTLE_UNIT_COUNT
.uloop:
                PUSH BC
                LD   HL, (BattleUnitPtr)          ; читаем поля юнита в temp (копии затрут HL)
                LD   A, (HL)
                LD   (BattleTmpType), A
                INC  HL
                LD   A, (HL)
                LD   (BattleTmpCell), A
                INC  HL
                LD   A, (HL)
                LD   (BattleTmpSide), A
                INC  HL
                LD   A, (HL)                      ; count_lo
                LD   C, A
                INC  HL
                LD   A, (HL)                      ; count_hi
                INC  HL
                LD   (BattleUnitPtr), HL          ; продвинулись на BATTLE_UNIT_STATE_SIZE (5)
                OR   C
                JR   NZ, .ualive                   ; count!=0 → живой, рисуем
                LD   A, (BattleDeathActive)         ; count==0: умирающий? (иначе не рисуем)
                OR   A
                JP   Z, .uskip
                LD   A, (BattleRenderIdx)
                LD   HL, BattleDeathUnit
                CP   (HL)
                JP   NZ, .uskip                     ; не умирающий → не рисуем
.ualive:        LD   A, (BattleRenderIdx)          ; кадр анимации (idle/ходьба/атака/смерть)
                CALL Battle_CalcAnimFrame
                LD   A, (BattleTmpType)            ; вариант = type*2+side → SOURCE кадра + LAYOUT/SIZE
                ADD  A, A
                LD   C, A
                LD   A, (BattleTmpSide)
                ADD  A, C
                CALL Battle_EmitUnitSprite
                ; вершина: ДВИЖУЩИЙСЯ юнит → интерполир. позиция; иначе вершина клетки
                LD   A, (BattleMoveActive)
                OR   A
                JR   Z, .uvcell
                LD   A, (BattleRenderIdx)
                LD   HL, BattleMoveUnit
                CP   (HL)
                JR   NZ, .uvcell
                LD   HL, (BattleMoveCurX)          ; интерполированная вершина
                LD   (RenderPathVertexX), HL
                LD   HL, (BattleMoveCurY)
                LD   (RenderPathVertexY), HL
                CALL Render_WriteVertex2FCmd
                JR   .uskip
.uvcell:        LD   A, (BattleTmpType)            ; BattleUnitVertsTab[type] + cell*4
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, BattleUnitVertsTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   A, (BattleTmpCell)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                       ; cell*4
                ADD  HL, DE
                LD   BC, 4
                CALL Render_CmdBufCopy
.uskip:
                POP  BC
                LD   A, (BattleRenderIdx)
                INC  A
                LD   (BattleRenderIdx), A
                DEC  B                              ; (DJNZ вне диапазона — цикл разросся)
                JP   NZ, .uloop
                LD   HL, Battle_Units_End_DL
                LD   BC, Battle_Units_End_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Battle_RenderArrow             ; летящая стрела лучника поверх поля (если в полёте)
                ; --- СЧЁТЧИКИ ОТРЯДОВ (fheroes2 RedrawTroopCount): тёмные бары + числа над живыми.
                ;     Проход 1 — бары (RECTS); проход 2 — числа (Render_Number16C, цифры в #0C95xx
                ;     персистентны, палитра OBJECT_OPAQUE @ #079200 — оба выше battle payload). ---
                LD   HL, Battle_CountBar_Pre_DL
                LD   BC, Battle_CountBar_Pre_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, BattleUnitState
                LD   (BattleUnitPtr), HL
                LD   B, BATTLE_UNIT_COUNT
.barloop:       PUSH BC
                LD   HL, (BattleUnitPtr)
                INC  HL                            ; &cell
                LD   A, (HL)
                LD   (BattleTmpCell), A
                INC  HL
                INC  HL                            ; &count_lo
                LD   A, (HL)
                LD   C, A
                INC  HL
                LD   A, (HL)                       ; count_hi
                LD   HL, (BattleUnitPtr)
                LD   DE, BATTLE_UNIT_STATE_SIZE
                ADD  HL, DE
                LD   (BattleUnitPtr), HL
                OR   C
                JP   Z, .barskip                   ; count 0 → мёртв, бар не рисуем
                LD   A, (BattleTmpCell)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                       ; cell*8
                LD   DE, BattleCountBarVerts
                ADD  HL, DE
                LD   BC, 8
                CALL Render_CmdBufCopy
.barskip:       POP  BC
                DJNZ .barloop
                LD   HL, Battle_CountBar_Post_DL
                LD   BC, Battle_CountBar_Post_DL_SIZE
                CALL Render_CmdBufCopy
                ; проход 2 — числа поверх баров
                LD   HL, Battle_Count_Begin_DL
                LD   BC, Battle_Count_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, BattleUnitState
                LD   (BattleUnitPtr), HL
                LD   B, BATTLE_UNIT_COUNT
.numloop:       PUSH BC
                LD   HL, (BattleUnitPtr)
                INC  HL                            ; &cell
                LD   A, (HL)
                LD   (BattleTmpCell), A
                INC  HL
                INC  HL                            ; &count_lo
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = count
                LD   HL, (BattleUnitPtr)
                PUSH DE
                LD   DE, BATTLE_UNIT_STATE_SIZE
                ADD  HL, DE
                LD   (BattleUnitPtr), HL
                POP  DE
                LD   A, D
                OR   E
                JP   Z, .numskip                   ; count 0 → мёртв
                LD   A, (BattleTmpCell)            ; перо из BattleCountPen[cell*4] = {penX, penY}
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                       ; cell*4
                LD   BC, BattleCountPen
                ADD  HL, BC
                PUSH DE                            ; сохранить count
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (ResPenX), DE
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (ResPenY), DE
                POP  HL                            ; HL = count
                CALL Battle_DrawCountNum          ; центрир. число СВОИМИ цифрами боя (глоб.DigitTable затёрт payload'ом)
.numskip:       POP  BC
                DJNZ .numloop
                LD   HL, Battle_Count_End_DL
                LD   BC, Battle_Count_End_DL_SIZE
                CALL Render_CmdBufCopy
                ; --- СТАТУС-БАР панели (fheroes2): идёт движение → «Moved …: from [src] to [dst].»;
                ;     иначе есть событие → «X do N damage[. M perish]» (верхняя строка, setStatus top);
                ;     иначе msg==0 → "Turn N", иначе hover-подсказка.
                LD   A, (BattleMoveActive)
                OR   A
                JR   Z, .st_noMove
                CALL Battle_RenderMoveLine         ; строка движения (собственный пролог+эпилог)
                JP   .no_status
.st_noMove:     LD   A, (BattleEvtActive)
                OR   A
                JR   Z, .st_normal
                CALL Battle_RenderEventLine        ; строка события (собственный пролог+эпилог)
                JP   .no_status
.st_normal:     LD   HL, Battle_Status_Begin_DL    ; общий префикс (палитра + BEGIN BITMAPS)
                LD   BC, Battle_Status_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (BattleStatusMsg)
                OR   A
                JR   NZ, .st_verb                  ; msg!=0 → hover-подсказка (Move/Attack/Shoot/View)
                ; msg==0 → ДЕФОЛТ статуса «Turn %{turn}» (faithful, battle_interface.cpp:3017).
                ; turnIdx = min(BattleRound, BATTLE_TURN_MAX) − 1; префикс BattleTurnPreTab + вершина.
                LD   A, (BattleRound)
                CP   BATTLE_TURN_MAX + 1
                JR   C, .turn_ok
                LD   A, BATTLE_TURN_MAX            ; раунд > предрендера → показать последний "Turn N"
.turn_ok:       DEC  A                            ; 1-based раунд → 0-based индекс
                LD   (BattleStatusIdx), A
                ADD  A, A                          ; idx*2 (DEFW)
                LD   L, A
                LD   H, 0
                LD   DE, BattleTurnPreTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   BC, BATTLE_TURN_PRE_SIZE
                CALL Render_CmdBufCopy
                LD   A, (BattleStatusIdx)          ; вершина BattleTurnVertTab + idx*4
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                LD   DE, BattleTurnVertTab
                ADD  HL, DE
                LD   BC, 4
                CALL Render_CmdBufCopy
                JP   .st_end
.st_verb:       DEC  A                            ; 1-based → 0-based hover-подсказка
                LD   (BattleStatusIdx), A
                LD   A, (BattleStatusIdx)          ; префикс BattleStatusPreTab[idx]
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, BattleStatusPreTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   BC, BATTLE_STATUS_PRE_SIZE
                CALL Render_CmdBufCopy
                LD   A, (BattleStatusIdx)          ; вершина BattleStatusVertTab + idx*4
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                LD   DE, BattleStatusVertTab
                ADD  HL, DE
                LD   BC, 4
                CALL Render_CmdBufCopy
.st_end:        LD   HL, Battle_Status_End_DL
                LD   BC, Battle_Status_End_DL_SIZE
                CALL Render_CmdBufCopy
.no_status:
                ; --- ОКНО ИТОГА (faithful: WINLOSE-рамка + баннер) если бой окончен ---
                LD   A, (BattleResult)
                OR   A
                JR   Z, .no_result
                LD   HL, Battle_WinDlg_DL
                LD   BC, Battle_WinDlg_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Battle_RenderWinText          ; нативные надписи окна поверх (без ×1.6-рвани)
                CALL Battle_RenderCasualties       ; потери: иконы MONS32 + счёт убитых / «None» (faithful)
.no_result:
                ; (жёлтая подсветка наведённой ячейки убрана — не по оригиналу; курсор поверх всего)
                CALL Battle_RenderCursor           ; форма курсора по теме hover (GetBattleCursor)
                CALL Render_SwapFrameDMA
                RET

; Battle_RenderCursor — ФОРМА курсора по BattleStatusMsg (faithful GetBattleCursor):
; Turn→WAR_NONE, Move→WAR_MOVE, Attack→SWORD, Shoot→WAR_ARROW, View→WAR_INFO. (CMSECO.ICN)
Battle_RenderCursor:
                CALL Input_MouseX
                LD   (CursorPixelX), HL
                CALL Input_MouseY
                LD   (CursorPixelY), HL
                LD   A, (BattleStatusMsg)
                CP   9
                JR   C, .ok
                XOR  A                             ; msg вне 0..8 → Turn/None
.ok:            LD   E, A
                LD   D, 0
                LD   HL, BattleCursorTab
                ADD  HL, DE
                LD   A, (HL)
                LD   (CursorSpriteIndex), A
                JP   Render_CursorCmd
BattleCursorTab:                                   ; [BattleStatusMsg] → индекс боевого курсора
                DEFB CURSOR_BATTLE_BASE_INDEX + 0  ; 0 Turn  → WAR_NONE
                DEFB CURSOR_BATTLE_BASE_INDEX + 1  ; 1 Move
                DEFB CURSOR_BATTLE_BASE_INDEX + 1  ; 2 Move
                DEFB CURSOR_BATTLE_BASE_INDEX + 4  ; 3 Attack → SWORD
                DEFB CURSOR_BATTLE_BASE_INDEX + 4  ; 4 Attack
                DEFB CURSOR_BATTLE_BASE_INDEX + 2  ; 5 Shoot → WAR_ARROW
                DEFB CURSOR_BATTLE_BASE_INDEX + 2  ; 6 Shoot
                DEFB CURSOR_BATTLE_BASE_INDEX + 3  ; 7 View  → WAR_INFO
                DEFB CURSOR_BATTLE_BASE_INDEX + 3  ; 8 View
