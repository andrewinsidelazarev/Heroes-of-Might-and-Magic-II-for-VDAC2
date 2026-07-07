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
BattleUnitShots: DEFS BATTLE_UNIT_COUNT  ; ОСТАТОК выстрелов (_shotsLeft; Unit::isArchers = остаток>0!)
BattleStartCnt:  DEFS BATTLE_UNIT_COUNT * 2 ; СНАПШОТ стартовых count (потери = старт − текущее;
                                             ;   Init не годится: армия защитника переопределяется монстром)
; --- ПКМ-попап ArmyInfo (Dialog::ArmyInfo ZERO): композит стримится в ОБЛАСТЬ ФИНАЛА ---
ArmyInfoLoaded:  DEFB 0           ; что в области финала: 0=финал, 1=попап Peasant, 2=Archer
ArmyInfoModal:   DEFB 0           ; 0=ПКМ-hold (Dialog::ZERO) / 1=модалка с EXIT (Dialog::BUTTONS)
ArmyInfoLatch:   DEFB 0           ; 1=открывший ЛКМ ещё зажат (не принимать клик по EXIT)
ArmyInfoShow:    DEFB 0           ; попап показан: 0=нет, 1/2=тип+1 (пока ПКМ зажат — пауза боя)
BattleSettingsOpen: DEFB 0        ; окно настроек боя открыто (модальная пауза, openBattleOptionDialog)
BattleSetOkHeld: DEFB 0           ; ЛКМ зажат над OKAY настроек (pressed-кадр + click по release)
BattleHelpShow:  DEFB #FF         ; ПКМ-справка (Dialog::ZERO): #FF=нет, 0..2=кнопки, 3..8=опции настроек
ArmyInfoUnit:    DEFB 0           ; юнит попапа
ArmyInfoType:    DEFB 0           ; его тип (0/1)
ArmyInfoCnt:     DEFW 0           ; кэш динамики при открытии: count
ArmyInfoHpl:     DEFW 0           ; Hit Points Left = hp-пул − (count−1)×maxHP
ArmyInfoShot:    DEFB 0           ; Shots Left
BattleWasMelee:  DEFB 0           ; 1 = последняя атака была ближней (сосед) → возможна ответка
BattleBestIdx:   DEFB 0           ; scratch Battle_NextTurn: лучший кандидат
BattleBestSpd:   DEFB 0           ; scratch: его скорость
BattleSideTmp:   DEFB 0           ; scratch Battle_SideAlive
BattleAliveCnt:  DEFB 0           ; scratch: счётчик живых стороны
BattleReach:     DEFS 99          ; достижимость клетки: 0=нет, 1..speed=дист, #FF=origin
BattleReachEn:   DEFS 99          ; второй буфер: флуд ЗА ВРАГА (archerDecision, с игнором активного)
BattleReachSpd:  DEFB 0           ; scratch: speed юнита флуда
BattleReachStep: DEFB 0           ; scratch: текущий шаг flood
BattleReachSrc:  DEFB 0           ; scratch: значение-источник flood
BattleReachUnit: DEFB 0           ; параметр ReachEx: юнит флуда
BattleReachBufPtr: DEFW BattleReach ; параметр ReachEx: буфер результата
BattleFindIgnore: DEFB #FF        ; FindUnitAtCell: игнорировать юнит с этим индексом (#FF=никого; UnitRemover)
BattleRshCell:   DEFB 0           ; scratch: индекс клетки в рендере теней достижимости
BattleStatusMsg: DEFB 0           ; статус-сообщение панели: 0=нет, 1..N (BattleStatusPreTab[idx-1])
BattleStatusIdx: DEFB 0           ; scratch: 0-based индекс сообщения в рендере
BattleResult:    DEFB 0           ; итог боя: 0=идёт, 1=Victory (защ.выбит), 2=Defeat (атак.выбит)
BattleRound:     DEFB 1           ; номер раунда (для "Turn N"); ++ при новом раунде в NextTurn
; --- AI боя (ai_battle.cpp planUnitTurn; выбор цели = Troop::evaluateThreatForUnit по оригиналу) ---
BattleAutoMode:  DEFB 0           ; 0=ручной (человек=side0, AI=side1); 1=авто-режим (AI обе стороны до конца)
BattleAISide:    DEFB 0           ; scratch: сторона активного (стабильно через MonsterStats_Read-пейджинг)
BattleAIBestTgt: DEFB 0           ; scratch: лучшая цель (макс. угроза)
BattleAIBestScore: DEFW 0         ; scratch: её угроза = evaluateThreatForUnit (getPotentialDamage÷distanceModifier)
BattleAIBestCell: DEFB 0          ; scratch: лучшая клетка подхода (мили)
BattleAIBestDist: DEFB 0          ; scratch: её dist² до цели
BattleAITRow:    DEFB 0           ; scratch: ряд цели
BattleAITCol:    DEFB 0           ; scratch: колонка цели
; --- scratch для Battle_EvalThreat (все slot3-чтения ДО MonsterStats_Read) ---
BattleThrACell:  DEFB 0           ; клетка активного (защищающегося)
BattleThrDef:    DEFB 0           ; защита активного
BattleThrECell:  DEFB 0           ; клетка врага (атакующего)
BattleThrAId:    DEFB 0           ; id активного (type+1)
BattleThrEId:    DEFB 0           ; id врага (type+1)
BattleThrCnt:    DEFW 0           ; count врага
BattleThrR:      DEFB 0           ; r = enemy.attack − active.defense (для двух ApplyDmgMod)
BattleThrEShots: DEFB 0           ; shots врага (побочно из EvalThreat — для non-evader теста)
BattleThrESpd:   DEFB 0           ; speed врага (побочно из EvalThreat, только в мили-ветке)
; --- scratch для Battle_AIPickApproach (мили: цель подхода = max(threat/dist), non-evader) ---
BattleApprBestTgt:  DEFB #FF      ; лучший враг для подхода
BattleApprBestThr:  DEFW 0        ; его threat
BattleApprBestDist: DEFB 0        ; его dist (гекс-6)
BattleApprActSpd:   DEFB 0        ; speed активного (для non-evader теста)
BattleApprActCell:  DEFB 0        ; клетка активного
BattleApprPass:     DEFB 0        ; 1=только non-evaders, 2=все
BattleApprCurThr:   DEFW 0        ; threat текущего кандидата
BattleApprCurDist:  DEFB 0        ; dist текущего кандидата
BattleApprIdx:      DEFB 0        ; индекс текущего врага (Mul16x8/LDIR портят BC)
BattleMulBuf:       DEFB 0,0,0    ; 24-бит произведение (threat_i × bestDist)
BattleMulBuf2:      DEFB 0,0,0    ; 24-бит произведение (bestThr × dist_i)
; --- analyzeBattleState (ai_battle.cpp:949): суммы сил + тактические флаги ---
BattleAnlMyStr:     DEFB 0,0,0    ; Σ GetStrength живых СВОИХ (24-бит LE; str_fp×16 × count)
BattleAnlEnStr:     DEFB 0,0,0    ; Σ GetStrength живых ВРАГОВ
BattleAnlMyShoot:   DEFB 0,0,0    ; Σ силы своих СТРЕЛКОВ (_myShootersStrength; без замка = RangedOnly)
BattleAnlEnShoot:   DEFB 0,0,0    ; Σ силы вражеских стрелков
BattleDefTactics:   DEFB 0        ; _defensiveTactics: 1=оборона (melee → Defense, не Offense)
BattleCautious:     DEFB 0        ; _cautiousOffensive: врag почти без стрелков (<0.15)
BattleAnlIdx:       DEFB 0        ; scratch: индекс юнита
BattleAnlN1:        DEFW 0        ; scratch: нормализованные 16-бит значения для пропорций
BattleAnlN2:        DEFW 0
; --- кэши по юнитам (строятся один раз в Battle_AIBuildThreatCache — далее без пейджинга) ---
BattleEnemyCache:   DEFS BATTLE_UNIT_COUNT       ; 1=живой враг активного
BattleArcherCache:  DEFS BATTLE_UNIT_COUNT       ; 1=стрелок (shots>0)
BattleCellCache:    DEFS BATTLE_UNIT_COUNT       ; клетка юнита
BattleSpdCache:     DEFS BATTLE_UNIT_COUNT       ; speed юнита (живым; archerDecision)
BattleThreatCache:  DEFS BATTLE_UNIT_COUNT * 2   ; threat (16-бит) = evaluateThreatForUnit
; --- scratch archerDecision (кайтинг стрелка, ai_battle.cpp:1172) ---
BattleArcMySpd:     DEFB 0        ; speed активного стрелка
BattleArcCur:       DEFB 0        ; его клетка
BattleArcMask:      DEFB 0        ; маска врагов, угрожающих ТЕКУЩЕЙ позиции
BattleArcAdjMask:   DEFB 0        ; маска врагов-СОСЕДЕЙ (isHandFighting)
BattleArcEIdx:      DEFB 0        ; scratch индекс врага
BattleArcWeak:      DEFB 0        ; 1=враг «слабый» (стрелок-не-в-упоре/спид0): метит только dist=1
BattleArcBestC:     DEFB #FF      ; лучшая безопасная клетка ретрита
BattleArcBestDN:    DEFB 0        ; её dist до ближайшего врага (max)
BattleArcBestDC:    DEFB 0        ; её dist до центра (min при равенстве)
BattleArcCandC:     DEFB 0        ; клетка-кандидат (внутр. цикл)
BattleArcBestE:     DEFB #FF      ; лучшая мили-цель (ветка B)
BattleArcBestDiff:  DEFW 0        ; её diff+#8000 (biased signed)
BattleArcPot:       DEFW 0        ; scratch potDmg
; --- scratch getMeleeBestOutcome (offense §1; фильтры — для Defense) ---
BattleMBOEnMask:    DEFB #FF      ; фильтр: битовая маска допущенных врагов (бит i = юнит i); #FF=все
BattleMBOZoneOnly:  DEFB 0        ; фильтр: 1=клетка атаки только в СВОЕЙ защищённой половине
BattleMBOFound:     DEFB 0        ; найдена ли атакуемая-в-ход цель
BattleMBOTgt:       DEFB #FF      ; лучшая цель
BattleMBOCell:      DEFB #FF      ; клетка атаки (откуда бить)
BattleMBOPV:        DEFW 0        ; positionValue лучшей
BattleMBOThr:       DEFW 0        ; threat лучшей
BattleMBOEIdx:      DEFB 0        ; индекс врага (внешний цикл)
BattleMBOCurCell:   DEFB 0        ; клетка-кандидат (сохранить через PosValue)
BattleMBOCurPV:     DEFW 0        ; positionValue кандидата
BattleMBOCurThr:    DEFW 0        ; threat кандидата-врага
BattlePVCurCell:    DEFB 0        ; клетка-кандидат в PosValue
BattlePVMax:        DEFW 0        ; scratch: max угроз мили-соседей
BattlePVArch:       DEFW 0        ; scratch: Σ угроз стрелков-соседей
BattlePVIdx:        DEFB 0        ; индекс в цикле PosValue
; --- scratch meleeUnitDefense (прикрытие стрелков) ---
BattleDefAnyImm:    DEFB 0        ; isAnyEnemyCanBeAttackedImmediately (полный MBO до фильтров)
BattleDefFIdx:      DEFB 0        ; индекс своего стрелка F (цикл)
BattleDefFCell:     DEFB 0        ; его клетка
BattleDefCover:     DEFB #FF      ; cover-клетка кандидата (приоритетная достижимая рядом с F)
BattleDefMask:      DEFB 0        ; маска врагов, блокирующих F (dist==1)
BattleDefDist:      DEFB 0        ; dist кандидата (min: до cover / до соседа блокирующего)
BattleDefBestF:     DEFB #FF      ; лучший стрелок
BattleDefBestVal:   DEFW 0        ; его archerValue (клемп ≥0)
BattleDefBestCover: DEFB #FF      ; его cover-клетка
BattleDefBestMask:  DEFB 0        ; его маска блокирующих
BattleDefPen:       DEFW 0        ; penalty16 = myShoot16/15 (defenseDistanceModifier ×16fp)
BattleDefActSpd:    DEFB 0        ; speed активного (для гейта speed×2)
BattleDefK:         DEFB 0        ; счётчик направлений
BattleDefAdjBase:   DEFW 0        ; &BattleAdjTab[Fcell*6]
BattleDefCoverD:    DEFB 0        ; дистанция до cover-клетки (Reach; #FF-origin → 0)
BattleDefEIdx:      DEFB 0        ; scratch: индекс врага во вложенных циклах
; --- scratch Battle_AICautiousStop (findOptimalPositionForSubsequentAttack :351) ---
BattleCautLen:      DEFB 0        ; длина пути (шагов, ≤12)
BattleCautPath:     DEFS 12       ; клетки пути: [0]=dest … [len-1]=первый шаг от origin
BattleCautThr:      DEFS 12*2     ; threat16 шага = Σ угроз врагов, достающих соседей клетки
BattleCautEIdx:     DEFB 0        ; scratch: индекс врага
BattleCautStep:     DEFB 0        ; scratch: индекс шага пути
BattleCautTmp:      DEFB 0        ; scratch: клетка-родитель при реконструкции
BattleCautMin:      DEFW 0        ; scratch: минимальная угроза при выборе
; приоритет направлений прикрытия (castle_dialog… нет: ai_battle.cpp:1800-1806, не-wide):
; side0 (смотрит вправо): R,TR,BR,TL,BL,L; side1 (reflect): L,TL,BL,TR,BR,R. Индексы BattleAdjTab {TL,TR,L,R,BL,BR}.
BattleDefPrioS0:    DEFB 3,1,5,0,4,2
BattleDefPrioS1:    DEFB 2,0,4,1,5,3
BATTLE_AI_GATE_MASK EQU %00011111 ; ход AI раз в 32 кадра (~0.6с) — бой видно
BATTLE_AI_MAX_ROUND EQU 60        ; страховка от зависания авто-боя (fheroes2: лимит ходов → auto-resolve)
; Зона кнопки Auto = спрайт TEXTBAR[4] @ (0,443) 49×18 (панель боя). Ниже неё — кнопка
; Settings TEXTBAR[6] @ (0,461) 49×19 (зоны НЕ пересекаются!).
BATTLE_AUTO_X0   EQU 0
BATTLE_AUTO_Y0   EQU 443
BATTLE_AUTO_X1   EQU 49
BATTLE_AUTO_Y1   EQU 461
; Кнопка Skip (пропуск хода юнита; fheroes2 _buttonSkip = TEXTBAR[0,1], правый край панели)
; Кнопка SKIP = TEXTBAR0 @(591,443) 49×37 — ЛОГИЧЕСКИЕ координаты (мышь в лог. 640×480)
BATTLE_SKIP_X0   EQU 591
BATTLE_SKIP_Y0   EQU 443
BATTLE_SKIP_X1   EQU 640
BATTLE_SKIP_Y1   EQU 480
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
; --- ★АНИМАЦИЯ ПО ОРИГИНАЛУ (BIN <MON>_FRM: кадры/тайминги fheroes2, BattleSpeed=4) ---
BattleAnimSlot:  DEFB 0           ; слот кадра текущего юнита (индекс в BattleFrameDL/OfsTab)
BattleTmpVar:    DEFB 0           ; вариант (type*2+side) для эмита спрайта/вершины
BattleTmpAnchX:  DEFW 0           ; якорь спрайта (vertex 1/16): клетка или интерполяция движения
BattleTmpAnchY:  DEFW 0
BattleRenderIdx: DEFB 0           ; индекс юнита в цикле рендера
BattleCorpsePass: DEFB 0          ; 1 = проход рендера ТРУПОВ (последний DEATH-кадр, под живыми)
BattleMoveActive: DEFB 0          ; 1 = идёт анимация движения (ход AI ждёт её окончания)
BattleMoveUnit:  DEFB 0           ; индекс движущегося юнита
BattleMoveDestCell: DEFB 0        ; клетка назначения (ставится по завершении)
BattleMoveProg:  DEFB 0           ; тиков с начала движения
BattleMoveSteps: DEFB 0           ; всего тиков = max(|dx|,|dy|)/BATTLE_MOVE_VEL (пропорц. дистанции,
                                  ;   465мс/клетку как BIN moveSpeed)
BattleMoveCurX:  DEFW 0           ; интерполируемый ЯКОРЬ движущегося юнита (vertex 1/16px)
BattleMoveCurY:  DEFW 0
BattleMoveStepX: DEFW 0           ; шаг/тик = (to−from)/steps (знаковый)
BattleMoveStepY: DEFW 0
BattleMoveSrcCell: DEFB 0         ; клетка-источник движения (для строки «Moved …: from [src] to [dst].»)
BattlePendAttack: DEFB 0          ; 1 = после движения проверить соседство и атаковать BattleTargetUnit
BattleAtkActive: DEFB 0           ; 1 = идёт анимация атаки (урон применяется в пике-контакте)
BattleAtkUnit:   DEFB 0           ; индекс атакующего (играет ATTACK2/SHOOT2-кадры)
BattleAtkProg:   DEFB 0           ; тиков с начала атаки
BattleAtkHit:    DEFB 0           ; 0 = урон ещё не применён в этой анимации
BattleAtkShoot:  DEFB 0           ; 1 = анимация ВЫСТРЕЛА (SHOOT2/END), 0 = мили (ATTACK2/END)
BattleAtkPeak:   DEFB 0           ; тик контакта (= конец мейн-фазы, BattleAtkTimTab)
BattleAtkTotal:  DEFB 0           ; тик конца анимации (мейн+END)
BattleDeathActive: DEFB 0         ; идёт анимация смерти отряда
BattleDeathUnit: DEFB 0           ; индекс умирающего (играет DEATH-кадры, потом ЛЕЖИТ трупом)
BattleDeathProg: DEFB 0           ; прогресс анимации смерти
BattleDeathTicks: DEFB 0          ; длительность смерти = len(DEATH)×6 по типу (BattleDeathTicksTab)
BattleDeathPend: DEFB 0           ; 1 = в этой атаке цель умерла → запустить смерть после удара
; --- WINCE выжившей цели (fheroes2 WINCE_UP/END при получении урона; чисто визуально) ---
BattleWinceActive: DEFB 0
BattleWinceUnit: DEFB 0
BattleWinceProg: DEFB 0
BattleWinceTotal: DEFB 0          ; тик конца (BattleWinceTimTab[тип][1])
; --- Per-юнит IDLE (оригинал: юнит стоит STATIC; раз в idleDelay×(75..125%) играет ОДИН
;     idle-вариант по вероятностям priorities, потом снова STATIC) ---
BattleIdleGrp:   DEFS BATTLE_UNIT_COUNT   ; 0=STATIC / 1..3=играет IDLE-вариант (коды групп!)
BattleIdleIdx:   DEFS BATTLE_UNIT_COUNT   ; индекс кадра в последовательности
BattleIdleTick:  DEFS BATTLE_UNIT_COUNT   ; тики до следующего кадра (BATTLE_ANIM_TICKS)
BattleIdleWait:  DEFS BATTLE_UNIT_COUNT * 2 ; DEFW: тики STATIC до следующего idle-варианта
BattleIdleCur:   DEFB 0           ; счётчик юнита в фоновом тике
BattleRndSeed:   DEFB #A5         ; 8-бит LFSR (Battle_Rand8)
; --- СТРЕЛА лучника (faithful ICN::ARCH_MSL; RedrawMissileAnimation): BattleArrowSteps тиков
;     полёта до пика (32 @ speed4; в наборе BattleSpeedSets — generated_battle.inc) ---
BattleArrowActive: DEFB 0         ; 1 = стрела в полёте (только дальний выстрел, WasMelee==0)
BattleArrowPend: DEFB 0           ; 1 = запуск стрелы запланирован на тик BattleArrowLaunch
BattleArrowLaunch: DEFB 0         ; тик запуска (= пик − полёт; долетает точно к урону)
BattleArrowProg: DEFB 0           ; прогресс 0..BattleArrowSteps
BattleArrowDir:  DEFB 0           ; 0 = вправо (атакующий side0) / 1 = влево (зеркало) → BattleArrowSrcTab
BattleArrowCurX: DEFW 0           ; интерполир. позиция стрелы (vertex 1/16px)
BattleArrowCurY: DEFW 0
BattleArrowEndX: DEFW 0           ; цель (для расчёта шага)
BattleArrowEndY: DEFW 0
BattleArrowStepX: DEFW 0          ; шаг/тик = (end−start)/steps
BattleArrowStepY: DEFW 0
BATTLE_EVT_Y    EQU 448 * 256 / 10  ; физ-Y верхней строки статуса (логич 448 ×1.6), vertex 1/16px
BATTLE_HOVER_Y  EQU 465 * 256 / 10  ; физ-Y НИЖНЕЙ строки (hover-подсказки, как BattleStatusVertTab)

; Вход в бой (через Battle_Enter_Tramp; чёрный кадр уже показан трамплином).
Battle_Enter:
                LD   A, GAME_MODE_COMBAT
                LD   (GameMode), A
                LD   A, 1
                LD   (BattleExitLatch), A
                CALL Battle_ApplySpeed             ; тик-таблицы по BattleSpeedSetting (резидент)
                ; сброс позиций юнитов из read-only Init в мутабельную таблицу + активный юнит = 0
                LD   HL, BattleUnitStateInit
                LD   DE, BattleUnitState
                LD   BC, BATTLE_UNIT_COUNT * BATTLE_UNIT_STATE_SIZE
                LDIR
                ; --- армия защитника = БРОДЯЧИЙ МОНСТР карты (EngagedMonIdx≠#FF): ОДИН стек
                ;     (id,count из MapMonsterTab) на центр. клетке; второй слот пуст. #FF → Init. ---
                LD   A, (EngagedMonIdx)
                CP   #FF
                JR   Z, .army_default
                LD   L, A                          ; &MapMonsterTab[idx*6]
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL                        ; 2
                ADD  HL, DE                        ; 3
                ADD  HL, HL                        ; 6
                LD   DE, MapMonsterTab
                ADD  HL, DE
                INC  HL
                INC  HL                            ; +2 = monsterId
                LD   A, (HL)
                DEC  A                             ; battle-тип = id−1 (0=Peasant,1=Archer)
                LD   (BattleUnitState + 2 * BATTLE_UNIT_STATE_SIZE + 0), A
                INC  HL                            ; +3 countLo
                LD   A, (HL)
                LD   (BattleUnitState + 2 * BATTLE_UNIT_STATE_SIZE + 3), A
                INC  HL                            ; +4 countHi
                LD   A, (HL)
                LD   (BattleUnitState + 2 * BATTLE_UNIT_STATE_SIZE + 4), A
                XOR  A                             ; слот 3 пуст (мёртв со старта)
                LD   (BattleUnitState + 3 * BATTLE_UNIT_STATE_SIZE + 3), A
                LD   (BattleUnitState + 3 * BATTLE_UNIT_STATE_SIZE + 4), A
.army_default:
                ; --- СНАПШОТ стартовых count (для потерь финала; Init≠старт при бое с монстром) ---
                LD   B, BATTLE_UNIT_COUNT
                LD   HL, BattleUnitState + 3       ; &count юнита 0
                LD   DE, BattleStartCnt
.snapcnt:       LD   A, (HL)
                LD   (DE), A
                INC  HL
                INC  DE
                LD   A, (HL)
                LD   (DE), A
                INC  DE
                LD   A, L                          ; следующий юнит (+5 от count_hi−1 → +4)
                ADD  A, BATTLE_UNIT_STATE_SIZE - 1
                LD   L, A
                JR   NC, .snapnc
                INC  H
.snapnc:        DJNZ .snapcnt
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
                CALL Battle_InitIdle              ; ★per-юнит idle + LFSR + wince сброс (портит A!)
                LD   A, 1
                LD   (BattleRound), A             ; раунд 1
                CALL Battle_InitHP                ; hp-пул каждого отряда = count×maxHP (по оригиналу)
                CALL Battle_InitShots             ; _shotsLeft каждого отряда = базовые shots (#91)
                XOR  A
                LD   (ArmyInfoShow), A            ; попап скрыт; в области финала — ФИНАЛ (payload)
                LD   (ArmyInfoLoaded), A
                LD   (ArmyInfoModal), A
                LD   (ArmyInfoLatch), A
                LD   (BattleSettingsOpen), A      ; окно настроек закрыто
                LD   (BattleSetOkHeld), A
                LD   A, #FF
                LD   (BattleHelpShow), A          ; ПКМ-справка скрыта
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
                CALL Battle_TypeToMonId  ; monster id = type+1 [TypeToMonId]
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

; Открыть ПКМ-попап ArmyInfo для (ArmyInfoUnit): кэш динамики (count/HP Left/Shots Left) +
; стрим композита типа в ОБЛАСТЬ ФИНАЛА (если там не он) + показать. Портит всё.
Battle_ArmyInfoOpen:
                LD   A, (ArmyInfoUnit)              ; ---- кэш динамики (до пейджинга) ----
                CALL Battle_UnitAddr
                LD   A, (HL)
                LD   (ArmyInfoType), A              ; тип (0/1)
                INC  HL
                INC  HL
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (ArmyInfoCnt), DE              ; count
                LD   A, (ArmyInfoUnit)
                LD   HL, BattleUnitShots
                CALL Battle_IdxByte
                LD   A, (HL)
                LD   (ArmyInfoShot), A              ; Shots Left (остаток)
                LD   A, (ArmyInfoUnit)              ; hp-пул
                CALL Battle_UnitHPAddr
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                PUSH DE                             ; hp
                LD   A, (ArmyInfoType)              ; maxHP из #91 (пейджинг)
                CALL Battle_TypeToMonId  ; type→id
                LD   B, A
                CALL MonsterStats_Read
                LD   HL, (MonsterStatBuf + 4)       ; maxHP (16-бит)
                EX   DE, HL                         ; DE=maxHP
                LD   HL, (ArmyInfoCnt)              ; HPLeft = hp − (count−1)×maxHP
                DEC  HL
                LD   A, H                           ; (count−1) — для скирмиша ≤255: берём L
                OR   A
                JR   Z, .cnt8
                LD   L, #FF                         ; клемп (не бывает)
.cnt8:          LD   B, L
                POP  HL                             ; HL = hp
                LD   A, B
                OR   A
                JR   Z, .hplw                       ; count==1 → HPLeft = hp
.hpll:          OR   A
                SBC  HL, DE                         ; − maxHP × (count−1)
                DJNZ .hpll
.hplw:          LD   (ArmyInfoHpl), HL
                ; ---- нужный композит уже в области? ----
                LD   A, (ArmyInfoType)
                INC  A                              ; 1/2
                LD   B, A
                LD   A, (ArmyInfoLoaded)
                CP   B
                JR   Z, .show                       ; уже там → просто показать
                PUSH BC                             ; ---- стрим попапа из PAK (общий хелпер) ----
                LD   A, (ArmyInfoType)              ; сектор попапа типа
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, ArmyInfoSecTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   BC, ARMYINFO_SECTORS
                CALL Battle_StreamWinArea           ; HL=сектор, BC=сектора → область финала
                POP  BC
                LD   A, B                           ; область теперь = попап типа
                LD   (ArmyInfoLoaded), A
.show:          LD   A, B
                LD   (ArmyInfoShow), A
                RET

; NZ если мышь в зоне кнопки EXIT модального ArmyInfo (лог. коорд.). Портит A,DE,HL.
Battle_AIExitHit:
                CALL Input_MouseX
                LD   DE, AIEXIT_X0
                OR   A
                SBC  HL, DE
                JR   C, .no
                LD   DE, AIEXIT_X1 - AIEXIT_X0
                OR   A
                SBC  HL, DE
                JR   NC, .no
                CALL Input_MouseY
                LD   DE, AIEXIT_Y0
                OR   A
                SBC  HL, DE
                JR   C, .no
                LD   DE, AIEXIT_Y1 - AIEXIT_Y0
                OR   A
                SBC  HL, DE
                JR   NC, .no
                LD   A, 1
                OR   A
                RET
.no:            XOR  A
                RET

; Общий стрим в ОБЛАСТЬ ФИНАЛА: HL=сектор в PAK, BC=сектора. Портит всё (Loader клоберит IX).
Battle_StreamWinArea:
                PUSH BC
                PUSH HL
                LD   HL, BattlePakName
                LD   DE, MenuNameBuf
                LD   BC, 13
                LDIR
                CALL Loader_Init
                CALL Loader_Mount
                LD   HL, MenuNameBuf
                CALL Loader_OpenFile
                POP  HL
                CALL Loader_SeekSector
                POP  BC
                LD   DE, BATTLE_WIN_DLG_RAMG & #FFFF
                LD   A, BATTLE_WIN_DLG_RAMG >> 16
                JP   Loader_StreamToRamGAt

; Вернуть ФИНАЛЬНОЕ ОКНО в его область (рестрим куска payload по сектору WINDLG_SEC) —
; зовётся из .result_wait, когда область занята попапом. Портит всё.
Battle_RestoreWinDlg:
                LD   HL, WINDLG_SEC
                LD   BC, WINDLG_SECTORS
                CALL Battle_StreamWinArea
                XOR  A
                LD   (ArmyInfoLoaded), A            ; в области снова финал
                LD   (ArmyInfoShow), A
                RET

; ============================================================================
; Окно НАСТРОЕК боя (openBattleOptionDialog, battle_dialogs.cpp:260): кнопка Settings панели
; (TEXTBAR[6], лево-низ) → модалка в области финала. Рабочая опция — Speed (клик: speed%10+1
; → Battle_ApplySpeed → живые тик-таблицы); остальные опции визуальны (подменю Interface/
; Audio/HotKeys не переносятся: Audio/HotKeys — новоделы fheroes2, спеллов нет). OKAY = закрыть.
; ============================================================================

; NZ если мышь (лог. 640×480) в прямоугольнике: HL → таблица DEFW X0,X1,Y0,Y1. Портит A,BC,DE,HL.
Battle_MouseInRect4:
                LD   (BattleSetRectPtr), HL
                CALL Input_MouseX                    ; HL = x (лог.)
                CALL .axis                           ; проверить пару X0/X1
                RET  Z
                CALL Input_MouseY
                ; падаем в .axis для пары Y0/Y1; его RET — наш результат
.axis:          EX   DE, HL                          ; DE = координата
                LD   HL, (BattleSetRectPtr)
                LD   C, (HL)
                INC  HL
                LD   B, (HL)
                INC  HL                              ; BC = MIN
                EX   DE, HL                          ; HL = коорд, DE = ptr
                OR   A
                SBC  HL, BC                          ; коорд − MIN
                JR   C, .no
                ADD  HL, BC                          ; восстановить коорд
                EX   DE, HL                          ; HL = ptr
                LD   C, (HL)
                INC  HL
                LD   B, (HL)
                INC  HL                              ; BC = MAX
                LD   (BattleSetRectPtr), HL          ; ptr → следующая пара (для Y-захода)
                EX   DE, HL                          ; HL = коорд
                OR   A
                SBC  HL, BC                          ; коорд − MAX
                JR   NC, .no
                LD   A, 1
                OR   A
                RET
.no:            XOR  A
                RET
BattleSetRectPtr: DEFW 0
BattleSetBtnRect:   DEFW BTLSET_BTN_X0, BTLSET_BTN_X1, BTLSET_BTN_Y0, BTLSET_BTN_Y1
BattleSetSpeedRect: DEFW BTLSET_SPEED_X0, BTLSET_SPEED_X1, BTLSET_SPEED_Y0, BTLSET_SPEED_Y1
BattleSetOkRect:    DEFW BTLSET_OK_X0, BTLSET_OK_X1, BTLSET_OK_Y0, BTLSET_OK_Y1
Battle_CheckSettingsClick:                          ; кнопка Settings панели (TEXTBAR[6] @ 0,461)
                LD   HL, BattleSetBtnRect
                JR   Battle_MouseInRect4
Battle_SetSpeedHit:                                 ; зона опции Speed (65×65)
                LD   HL, BattleSetSpeedRect
                JR   Battle_MouseInRect4
Battle_SetOkHit:                                    ; зона кнопки OKAY
                LD   HL, BattleSetOkRect
                JR   Battle_MouseInRect4

; Открыть окно настроек: стрим композита в область финала (если она занята другим) + флаг.
; Портит всё (ЛОВУШКА: Loader клоберит IX).
Battle_SettingsOpen:
                LD   A, (ArmyInfoLoaded)
                CP   3                               ; 3 = в области уже композит настроек
                JR   Z, .shw
                LD   HL, SETTINGS_SEC
                LD   BC, SETTINGS_SECTORS
                CALL Battle_StreamWinArea
                LD   A, 3
                LD   (ArmyInfoLoaded), A
.shw:           LD   A, 1
                LD   (BattleSettingsOpen), A
                XOR  A
                LD   (BattleSetOkHeld), A
                RET

; --- ПКМ-справки (showStandardTextMessage, Dialog::ZERO — показ пока ПКМ зажат) ---
; A=индекс окна (0..8) → стрим композита в область финала (если не он там) + показать.
; Портит всё (Loader клоберит IX).
Battle_HelpOpen:
                LD   C, A
                ADD  A, 4                            ; код области = 4+idx
                LD   HL, ArmyInfoLoaded
                CP   (HL)
                JR   Z, .shw
                LD   (HL), A
                PUSH BC
                LD   A, C                            ; размер = BattleHelpSecN[idx]
                LD   HL, BattleHelpSecN
                CALL Battle_IdxByte
                LD   B, 0
                LD   A, (HL)
                PUSH AF
                LD   A, C                            ; сектор = BattleHelpSecTab[idx]
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, BattleHelpSecTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                POP  AF
                LD   C, A
                CALL Battle_StreamWinArea            ; HL=сектор, BC=сектора
                POP  BC
.shw:           LD   A, C
                LD   (BattleHelpShow), A
                RET

; ПКМ над кнопками панели боя → индекс окна справки (0=Auto,1=Settings,2=Skip) или #FF.
Battle_BtnHelpScan:
                CALL Battle_CheckAutoClick           ; зоны кнопок = их спрайты
                JR   Z, .b1
                XOR  A
                RET
.b1:            CALL Battle_CheckSettingsClick
                JR   Z, .b2
                LD   A, 1
                RET
.b2:            CALL Battle_CheckSkipClick
                JR   Z, .none
                LD   A, 2
                RET
.none:          LD   A, #FF
                RET

; ПКМ над опциями окна настроек → окно справки 3..8 (5 опций + OKAY) или #FF.
Battle_SetHelpScan:
                LD   B, 0
.shs:           PUSH BC
                LD   A, B                            ; HL = BattleSetHelpRects + i×8
                ADD  A, A
                ADD  A, A
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, BattleSetHelpRects
                ADD  HL, DE
                CALL Battle_MouseInRect4
                POP  BC
                OR   A
                JR   NZ, .hit
                INC  B
                LD   A, B
                CP   6
                JR   C, .shs
                LD   A, #FF
                RET
.hit:           LD   A, B
                ADD  A, 3
                RET

; Модалка настроек (пауза боя): Speed-зона → speed%10+1 → ApplySpeed; OKAY = press в зоне +
; release в зоне (MouseClickLeft); ПКМ над опцией → hold-справка (закрытие рестримит окно
; настроек — область финала одна). OUT: A=0 (выход из боя не отсюда).
Battle_SettingsUpdate:
                LD   A, (BattleHelpShow)             ; справка показана? → держать пока ПКМ
                CP   #FF
                JR   Z, .nohelp
                CALL Input_MouseRMB
                JR   NZ, .hold
                LD   A, #FF                          ; отпустили → закрыть + вернуть окно настроек
                LD   (BattleHelpShow), A
                JP   Battle_SettingsOpen             ; рестрим композита настроек (A=0 не важен: RET→caller)
.nohelp:        CALL Input_MouseRMB                  ; ПКМ над опцией → открыть справку
                JR   Z, .lmb
                CALL Battle_SetHelpScan
                CP   #FF
                JR   Z, .hold
                CALL Battle_HelpOpen
                JR   .hold
.lmb:           CALL Input_MouseLMB
                JR   NZ, .prs
                XOR  A                               ; отпущено
                LD   (BattleExitLatch), A
                LD   A, (BattleSetOkHeld)            ; release после press над OKAY?
                OR   A
                JR   Z, .idle
                XOR  A
                LD   (BattleSetOkHeld), A
                CALL Battle_SetOkHit                 ; всё ещё в зоне → клик OKAY → закрыть
                JR   Z, .idle
                XOR  A
                LD   (BattleSettingsOpen), A
.idle:          XOR  A
                RET
.prs:           LD   A, (BattleExitLatch)            ; press уже обработан → ждать release
                OR   A
                JR   NZ, .hold
                LD   A, 1
                LD   (BattleExitLatch), A
                CALL Battle_SetOkHit                 ; press над OKAY → held (кадр+клик по release)
                JR   Z, .notok
                LD   A, 1
                LD   (BattleSetOkHeld), A
                XOR  A
                RET
.notok:         CALL Battle_SetSpeedHit              ; клик по Speed → следующая скорость (:316)
                JR   Z, .hold
                LD   A, (BattleSpeedSetting)         ; speed % 10 + 1
                CP   10
                JR   C, .inc
                XOR  A
.inc:           INC  A
                LD   (BattleSpeedSetting), A
                CALL Battle_ApplySpeed
.hold:          XOR  A
                RET

; Опрос боя: клик ЛКМ (после отпускания входного) → выход. OUT: A=1 если запрошен выход
; (резидентный Battle_Update_Tramp по A=1 зовёт Adventure_Enter — slot3-edge).
Battle_Update:
                CALL Battle_AnimBgTick            ; фоновые анимации: wince + per-юнит idle
                CALL Battle_ComputeHover          ; обновить наведённую гекс-ячейку (подсветка)
                LD   A, (BattleResult)             ; бой окончен? → показываем итог, выход по клику
                OR   A
                JP   NZ, .result_wait
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
.noanim:        LD   A, (BattleSettingsOpen)       ; окно настроек — модальная пауза
                OR   A
                JP   NZ, Battle_SettingsUpdate
                LD   A, (BattleHelpShow)           ; ПКМ-справка кнопки — держать пока ПКМ (пауза)
                CP   #FF
                JR   Z, .nohelp
                CALL Input_MouseRMB
                JR   NZ, .helphold
                LD   A, #FF                        ; отпустили → закрыть
                LD   (BattleHelpShow), A
.helphold:      XOR  A
                RET
.nohelp:        ; --- Попап ArmyInfo: ПКМ-hold (Dialog::ZERO) ИЛИ модалка с EXIT (Dialog::BUTTONS) ---
                LD   A, (ArmyInfoShow)
                OR   A
                JR   Z, .no_popup_held
                LD   A, (ArmyInfoModal)
                OR   A
                JR   NZ, .popup_modal
                CALL Input_MouseRMB                 ; hold: ещё держат?
                JR   NZ, .popup_hold
                XOR  A                              ; отпустили → закрыть (battle_interface.cpp:582)
                LD   (ArmyInfoShow), A
.popup_hold:    XOR  A
                RET                                 ; пауза: ни AI, ни ввода пока попап
.popup_modal:   CALL Input_MouseLMB                 ; модалка: закрытие ТОЛЬКО кликом по EXIT (ориг.)
                JR   NZ, .pm_pressed
                XOR  A                              ; отпущено → следующий клик валиден
                LD   (ArmyInfoLatch), A
                RET
.pm_pressed:    LD   A, (ArmyInfoLatch)
                OR   A
                JR   NZ, .pm_hold                   ; открывший клик ещё зажат
                CALL Battle_AIExitHit               ; клик: по кнопке EXIT?
                JR   Z, .pm_hold
                XOR  A                              ; закрыть модалку
                LD   (ArmyInfoShow), A
                LD   (ArmyInfoModal), A
                LD   A, 1
                LD   (BattleExitLatch), A           ; текущее зажатие не должно кликнуть поле
.pm_hold:       XOR  A
                RET
.no_popup_held: CALL Input_MouseRMB                 ; ПКМ на клетке с юнитом → hold-попап
                JR   Z, .no_popup
                CALL Battle_BtnHelpScan             ; ПКМ над кнопкой панели → hold-справка
                CP   #FF
                JR   Z, .nobtnhelp
                CALL Battle_HelpOpen
                XOR  A
                RET
.nobtnhelp:     LD   A, (BattleHoverCell)
                CP   #FF
                JR   Z, .no_popup
                CALL Battle_FindUnitAtCell          ; и живой юнит под курсором
                CP   #FF
                JR   Z, .no_popup
                LD   (ArmyInfoUnit), A
                CALL Battle_ArmyInfoOpen            ; кэш динамики + стрим композита при смене типа
                XOR  A
                LD   (ArmyInfoModal), A             ; ПКМ = hold-режим (без кнопки)
                RET
.no_popup:      CALL Battle_AIMaybeAct            ; AI-сторона (защитник, либо все в авто) ходит сама; A=1 если AI владеет ходом
                OR   A
                JR   Z, .humaninput              ; A=0 → ход человека → обычный ввод
                XOR  A                            ; AI обрабатывает этот кадр → ни клика, ни выхода
                RET
.humaninput:    CALL Input_MouseLMB               ; NZ = нажато
                JR   NZ, .pressed
                XOR  A
                LD   (BattleExitLatch), A
                RET
.result_wait:   LD   A, (ArmyInfoLoaded)           ; в области финала попап? → РЕстрим финала (1 раз)
                OR   A
                CALL NZ, Battle_RestoreWinDlg
                CALL Input_MouseLMB
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
                CALL Battle_CheckSkipClick          ; клик по зоне Skip → пропустить ход юнита (SKIP-команда)
                JR   NZ, .skipturn
                CALL Battle_CheckSettingsClick      ; клик по кнопке Settings (TEXTBAR[6]) → окно настроек
                JR   NZ, .setopen
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
.ownunit:       LD   A, (BattleTargetUnit)          ; ЛКМ по СВОЕМУ → МОДАЛЬНОЕ окно ArmyInfo с EXIT
                LD   (ArmyInfoUnit), A              ;   (Dialog::BUTTONS, battle_interface.cpp:3827)
                CALL Battle_ArmyInfoOpen
                LD   A, 1
                LD   (ArmyInfoModal), A
                LD   (ArmyInfoLatch), A             ; открывший клик ещё зажат
                XOR  A
                RET
.moveact:       CALL Battle_MoveActive              ; пустая ячейка → передвинуть активного юнита
                XOR  A
                RET
.autoon:        LD   A, 1
                LD   (BattleAutoMode), A             ; кнопка Auto → AI доигрывает бой за обе стороны
                XOR  A
                RET
.setopen:       CALL Battle_SettingsOpen             ; кнопка Settings → стрим окна + модальная пауза
                XOR  A
                RET
.skipturn:      CALL Battle_EndTurn                  ; Skip: юнит завершает ход без действия (SKIP)
                XOR  A
                RET
.exit:          ; --- исход боя против Sorc-героя: пишем РЕЗИДЕНТНЫЙ маркер BattleVsSorc для
                ; SorcHero_LoadCache (пейджить #91 из battle-overlay нельзя; BattleResult живёт
                ; тут, в overlay — из adventure не читается). 2=победа игрока (Sorc убит), 0=иначе.
                LD   A, (BattleVsSorc)
                DEC  A                             ; ==1 (шёл Sorc-бой)?
                JR   NZ, .exit_mon
                LD   A, (BattleResult)             ; overlay — доступен здесь
                DEC  A                             ; 1=Victory → 0
                LD   A, 0                          ; поражение → маркер 0 (Sorc жив; TODO LOSS-экран)
                JR   NZ, .exit_vsset
                LD   A, 2                          ; победа → маркер 2 (LoadCache снимет Sorc)
.exit_vsset:    LD   (BattleVsSorc), A
                JR   .exit_plain
.exit_mon:      ; --- исход боя с БРОДЯЧИМ МОНСТРОМ (EngagedMonIdx≠#FF) ---
                LD   A, (EngagedMonIdx)
                CP   #FF
                JR   Z, .exit_plain
                LD   L, A                          ; &MapMonsterTab[idx*6]
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, DE
                ADD  HL, HL
                LD   DE, MapMonsterTab
                ADD  HL, DE
                LD   A, (BattleResult)             ; 1=победа игрока
                CP   1
                JR   NZ, .lostmon
                LD   DE, 5                          ; ПОБЕДА: монстр убит (alive=0); спрайт остаётся
                ADD  HL, DE                         ;   «трупом»-препятствием до рантайм-слоя монстров
                LD   (HL), 0
                JR   .monout
.lostmon:       LD   A, (HeroPrevTileX)             ; ПОРАЖЕНИЕ/иное: герой откатывается с тайла
                LD   B, A                           ;   живого монстра на тайл до шага
                LD   A, (HeroPrevTileY)
                LD   C, A
                CALL Hero_SetTile
.monout:        LD   A, #FF
                LD   (EngagedMonIdx), A
.exit_plain:    LD   A, 1
                LD   (AdvReenter), A                ; возврат на карту БЕЗ сброса героя/дня/ресурсов
                ; Бой затёр RAM_G-кэш террейн-композита (payload base0). Перед возвратом на карту
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

; A = ростер-type → A = engine monster id. ★Заменяет прежний INC A (type+1 верно лишь для
; Peasant/Archer id1,2). ФОРМУЛА для ростера [Peasant1,Archer2,Sprite21,Dwarf22] (бюджет оверлея
; — без таблицы): type 0,1 → +1; type 2,3 → +19 (→21,22). ★КОУПЛИНГ: при смене ростера юнитов
; обновить здесь и UNIT_MONID в battle_pack.py. Сохраняет BC,DE,HL (только A,F — drop-in для INC A).
Battle_TypeToMonId:
                CP   2
                JR   NC, .sorc                     ; type 2,3 (Sprite/Dwarf враг)
                INC  A                              ; type 0,1 → id 1,2 (Peasant/Archer)
                RET
.sorc:          ADD  A, 19                          ; type 2→21 (Sprite), 3→22 (Dwarf)
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
                CALL Battle_TypeToMonId  ; type→id
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

; _shotsLeft каждого отряда = базовые shots из #91 (battle_troop.cpp:140). Unit::isArchers =
; ОСТАТОК>0 → все archer-гейты боя читают BattleUnitShots, не статы. Зовётся в Battle_Enter.
Battle_InitShots:
                LD   C, 0
.isloop:        LD   A, C                          ; id = type+1
                CALL Battle_UnitAddr
                LD   A, (HL)
                CALL Battle_TypeToMonId  ; type→id
                LD   B, A
                PUSH BC                            ; MonsterStats_Read портит BC
                CALL MonsterStats_Read
                POP  BC
                LD   A, (MonsterStatBuf + 7)       ; базовые shots
                LD   B, A
                LD   A, C
                LD   HL, BattleUnitShots
                CALL Battle_IdxByte
                LD   (HL), B
                INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JR   C, .isloop
                RET

; A = cell → A = индекс ЖИВОГО юнита в этой ячейке, или #FF. (cell@+1, count@+3,+4)
; Юнит с индексом (BattleFindIgnore) НЕ виден (#FF=никого) — «UnitRemover» для флуда за врага.
Battle_FindUnitAtCell:
                LD   (BattleFindCell), A
                LD   C, 0
.floop:         LD   A, (BattleFindIgnore)         ; временно снятый юнит (archerDecision)
                CP   C
                JR   Z, .fnext
                LD   A, C
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
                CALL Battle_TypeToMonId  ; type→id
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
                CALL Battle_TypeToMonId  ; type→id
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
                ; ★WINCE выжившей цели (fheroes2: WINCE_UP/END при получении урона)
                LD   A, (BattleTargetUnit)
                LD   (BattleWinceUnit), A
                CALL Battle_UnitAddr
                LD   A, (HL)                        ; тип цели → длительность wince
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, BattleWinceTimTab
                ADD  HL, DE
                INC  HL                             ; [1] = всего тиков
                LD   A, (HL)
                LD   (BattleWinceTotal), A
                XOR  A
                LD   (BattleWinceProg), A
                INC  A
                LD   (BattleWinceActive), A
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

; «Shoot %{monster} (N shot(s) left)» — hover-подсказка с ЖИВЫМ остатком выстрелов активного
; (ориг. GetBattleCursor:2929: GetShots=_shotsLeft; «(1 shot left)» в единственном).
; Нижняя строка бара (BATTLE_HOVER_Y), центр X=512, шрифт статуса. Портит всё.
Battle_RenderShootStatus:
                LD   A, (BattleActiveUnit)          ; N = _shotsLeft активного
                LD   HL, BattleUnitShots
                CALL Battle_IdxByte
                LD   A, (HL)
                LD   (BattleShootN), A
                LD   A, (BattleTargetUnit)          ; head по типу ЦЕЛИ («Shoot Peasants (»)
                CALL Battle_UnitAddr
                LD   A, (HL)
                LD   (BattleShootT), A
                CALL Battle_ShootHeadAddr           ; --- суммарная ширина ---
                CALL Battle_EvtEntW
                LD   L, A
                LD   H, 0
                PUSH HL
                LD   A, (BattleShootN)
                LD   L, A
                LD   H, 0
                CALL Battle_EvtNumW
                POP  HL
                CALL Battle_AddAToHL
                PUSH HL
                CALL Battle_ShootTailAddr
                CALL Battle_EvtEntW
                POP  HL
                CALL Battle_AddAToHL
                SRL  H                              ; перо: X = (512 − w/2)×16
                RR   L
                EX   DE, HL
                LD   HL, 512
                OR   A
                SBC  HL, DE
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL
                LD   (ResPenX), HL
                LD   HL, BATTLE_HOVER_Y             ; нижняя строка бара (как hover-вершины)
                LD   (ResPenY), HL
                LD   HL, Battle_Status_Begin_DL
                LD   BC, Battle_Status_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Battle_ShootHeadAddr           ; «Shoot X (»
                CALL Battle_DrawEvtSprite
                LD   A, (BattleShootN)              ; N
                LD   L, A
                LD   H, 0
                CALL Battle_DrawEvtNum
                CALL Battle_ShootTailAddr           ; « shot(s) left)»
                CALL Battle_DrawEvtSprite
                LD   HL, Battle_Status_End_DL
                LD   BC, Battle_Status_End_DL_SIZE
                JP   Render_CmdBufCopy

; HL = &BattleShootHeadTab[(BattleShootT)*5]. Портит A,DE,HL.
Battle_ShootHeadAddr:
                LD   A, (BattleShootT)
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, A
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE                        ; ×5
                LD   DE, BattleShootHeadTab
                ADD  HL, DE
                RET
; HL = &tail: « shot left)» при N==1, иначе « shots left)». Портит A.
Battle_ShootTailAddr:
                LD   A, (BattleShootN)
                CP   1
                LD   HL, BattleShootTailSg
                RET  Z
                LD   HL, BattleShootTailPl
                RET
BattleShootN:   DEFB 0
BattleShootT:   DEFB 0

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

; ═══ ПКМ-попап ArmyInfo: тень (ГЛОБАЛЬНАЯ Render_WindowShadowDL) + окно (стримленный композит
; в области финала) + монстр (кадр СТОЙКИ из атласа юнитов, reflect по стороне) + динамика
; (Count по центру бокса / Hit Points Left / Shots Left — нативные ×1.6-маски, белый пролог). ═══
Battle_RenderArmyInfo:
                LD   HL, Battle_ArmyInfo_DL          ; тень: ТА ЖЕ глобальная процедура, что у всех окон
                LD   BC, Battle_ArmyInfo_DL_SIZE
                CALL Render_WindowShadowDL
                LD   HL, Battle_ArmyInfo_DL          ; само окно
                LD   BC, Battle_ArmyInfo_DL_SIZE
                CALL Render_CmdBufCopy
                ; --- монстр: кадр СТОЙКИ, вершина = якорь ног попапа + смещение кадра ---
                LD   A, (ArmyInfoUnit)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                LD   C, (HL)                         ; side
                LD   A, (ArmyInfoType)
                ADD  A, A
                ADD  A, C                            ; вариант
                LD   (BattleTmpVar), A
                LD   A, (ArmyInfoType)               ; слот стойки типа
                LD   HL, BattleStaticSlotTab
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                LD   A, (HL)
                LD   (BattleAnimSlot), A
                LD   A, (ArmyInfoType)               ; якорь ног (146,175 окна)
                ADD  A, A
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, ArmyInfoMonAnchor
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleTmpAnchX), DE
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleTmpAnchY), DE
                CALL Battle_EmitUnitSprite
                CALL Battle_EmitUnitVertex
                ; --- модалка (Dialog::BUTTONS): кнопка EXIT (нажатое состояние при ЛКМ в зоне) ---
                LD   A, (ArmyInfoModal)
                OR   A
                JR   Z, .nobtn
                CALL Input_MouseLMB
                JR   Z, .btnrel
                CALL Battle_AIExitHit
                JR   Z, .btnrel
                LD   HL, Battle_AIExitBtn1_DL       ; нажата
                LD   BC, Battle_AIExitBtn1_DL_SIZE
                JR   .btndraw
.btnrel:        LD   HL, Battle_AIExitBtn0_DL       ; отжата
                LD   BC, Battle_AIExitBtn0_DL_SIZE
.btndraw:       CALL Render_CmdBufCopy
.nobtn:         LD   HL, Battle_ArmyInfo_Post_DL      ; сброс SIZE_H (ловушка &511)
                LD   BC, Battle_ArmyInfo_Post_DL_SIZE
                CALL Render_CmdBufCopy
                ; --- динамика: белый пролог (та же палитра, что статус) ---
                LD   HL, Battle_Status_Begin_DL
                LD   BC, Battle_Status_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, (ArmyInfoCnt)               ; Count: центр бокса → ResPenX = CX16 − totW×8
                CALL Battle_ArmyInfoNumW             ; DE = Σширин цифр (px)
                EX   DE, HL                          ; HL=Σw
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                          ; ×8
                EX   DE, HL
                LD   HL, ARMYINFO_CNT_CX16
                OR   A
                SBC  HL, DE
                LD   (ResPenX), HL
                LD   HL, ARMYINFO_CNT_Y16
                LD   (ResPenY), HL
                LD   HL, (ArmyInfoCnt)
                CALL Battle_ArmyInfoDrawNum
                ; Hit Points Left @ (VALX16, HplY16[type])
                LD   HL, ARMYINFO_VALX16
                LD   (ResPenX), HL
                LD   A, (ArmyInfoType)
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, ArmyInfoHplY16Tab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   (ResPenY), HL
                LD   HL, (ArmyInfoHpl)
                CALL Battle_ArmyInfoDrawNum
                ; Shots Left (если есть строка)
                LD   A, (ArmyInfoType)
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, ArmyInfoShotY16Tab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   A, E
                OR   D
                JR   Z, .noshots                     ; 0 = строки нет (не стрелок)
                EX   DE, HL
                LD   (ResPenY), HL
                LD   HL, ARMYINFO_VALX16
                LD   (ResPenX), HL
                LD   A, (ArmyInfoShot)
                LD   L, A
                LD   H, 0
                CALL Battle_ArmyInfoDrawNum
.noshots:       LD   HL, Battle_Status_End_DL         ; конец текстового блока
                LD   BC, Battle_Status_End_DL_SIZE
                JP   Render_CmdBufCopy

; ПКМ-справка: общий пролог (SOURCE и пр.) + тень + LAYOUT/SIZE/VERTEX окна + сброс SIZE_H.
; Портит всё.
Battle_RenderHelp:
                LD   HL, Battle_HelpPre_DL           ; пролог (TRANSFORM/PALETTE/BEGIN/SOURCE)
                LD   BC, Battle_HelpPre_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (BattleHelpShow)
                ADD  A, A                            ; ×2 (DLTab: только ptr, размер общий)
                LD   L, A
                LD   H, 0
                LD   DE, BattleHelpDLTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                PUSH DE
                EX   DE, HL                          ; HL = фрагмент окна
                LD   BC, BATTLE_HELP_DL_SIZE
                CALL Render_WindowShadowDL           ; тень окна (глобальная процедура)
                POP  HL
                LD   BC, BATTLE_HELP_DL_SIZE
                CALL Render_CmdBufCopy               ; само окно
                LD   HL, Battle_Settings_Post_DL     ; сброс SIZE_H (общий Post)
                LD   BC, Battle_Settings_Post_DL_SIZE
                JP   Render_CmdBufCopy

; Окно настроек боя: композит (область финала) + динамика: иконка Speed по диапазону
; (CSPANEL 0 вбейкан / [1] 5..7 / [2] ≥8, battle_dialogs.cpp:232), OKAY pressed при
; удержании в зоне, строка «Speed: N» (маска ×1.6, белый статус-пролог, центр по иконке).
; Портит всё.
Battle_RenderSettings:
                LD   HL, Battle_Settings_DL          ; тень окна — глобальная процедура
                LD   BC, Battle_Settings_DL_SIZE
                CALL Render_WindowShadowDL
                LD   HL, Battle_Settings_DL
                LD   BC, Battle_Settings_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (BattleSpeedSetting)
                CP   8
                JR   C, .nspd2
                LD   HL, Battle_SetSpdIcon2_DL
                LD   BC, Battle_SetSpdIcon2_DL_SIZE
                CALL Render_CmdBufCopy
                JR   .spdok
.nspd2:         CP   5
                JR   C, .spdok
                LD   HL, Battle_SetSpdIcon1_DL
                LD   BC, Battle_SetSpdIcon1_DL_SIZE
                CALL Render_CmdBufCopy
.spdok:         LD   A, (BattleSetOkHeld)            ; OKAY pressed (удержание в зоне)
                OR   A
                JR   Z, .okrel
                CALL Battle_SetOkHit
                JR   Z, .okrel
                LD   HL, Battle_SetOkay1_DL
                LD   BC, Battle_SetOkay1_DL_SIZE
                CALL Render_CmdBufCopy
.okrel:         LD   HL, Battle_Settings_Post_DL     ; сброс SIZE_H (ловушка &511)
                LD   BC, Battle_Settings_Post_DL_SIZE
                CALL Render_CmdBufCopy
                LD   HL, Battle_Status_Begin_DL      ; строка «Speed: N» — белый пролог
                LD   BC, Battle_Status_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (BattleSpeedSetting)         ; запись = BattleSetValTab + (s−1)×5
                DEC  A
                LD   E, A
                LD   D, 0
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                          ; ×4
                ADD  HL, DE                          ; ×5
                LD   DE, BattleSetValTab
                ADD  HL, DE
                PUSH HL
                LD   DE, 3                           ; ширина маски (+3) → центрирование
                ADD  HL, DE
                LD   E, (HL)
                LD   D, 0
                EX   DE, HL                          ; HL = w
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                          ; ×8 (полширины ×16)
                EX   DE, HL                          ; DE = w×8
                LD   HL, SETVAL_CX16
                OR   A
                SBC  HL, DE
                LD   (ResPenX), HL
                LD   HL, SETVAL_Y16
                LD   (ResPenY), HL
                POP  HL
                CALL Battle_DrawEvtSprite
                LD   HL, Battle_Status_End_DL
                LD   BC, Battle_Status_End_DL_SIZE
                JP   Render_CmdBufCopy

; HL=число → DE = суммарная ширина его цифр в px (маски ArmyInfoDigitTab; для центрирования).
; Портит всё (Div16by8 портит B).
Battle_ArmyInfoNumW:
                XOR  A
                LD   (ArmyInfoDigN), A
.nws:           LD   C, 10
                CALL Battle_Div16by8                 ; HL/=10, A=остаток (цифра)
                PUSH AF                              ; цифры в стек
                LD   A, (ArmyInfoDigN)
                INC  A
                LD   (ArmyInfoDigN), A
                LD   A, H
                OR   L
                JR   NZ, .nws
                LD   DE, 0                           ; Σ ширин
.nwo:           POP  AF                              ; очередная цифра
                PUSH DE
                LD   E, A
                LD   D, 0
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                          ; d*4
                ADD  HL, DE                          ; d*5
                LD   DE, ArmyInfoDigitTab + 3        ; поле w
                ADD  HL, DE
                LD   A, (HL)
                POP  DE
                ADD  A, E                            ; DE += w
                LD   E, A
                JR   NC, .nwc
                INC  D
.nwc:           LD   A, (ArmyInfoDigN)
                DEC  A
                LD   (ArmyInfoDigN), A
                JR   NZ, .nwo
                RET

; HL=число → нарисовать цифры слева направо от пера (ResPenX/Y; DrawEvtSprite продвигает). Портит всё.
Battle_ArmyInfoDrawNum:
                XOR  A
                LD   (ArmyInfoDigN), A
.dds:           LD   C, 10
                CALL Battle_Div16by8                 ; HL/=10, A=остаток
                PUSH AF                              ; цифры в стек (LIFO → старшая выйдет первой)
                LD   A, (ArmyInfoDigN)
                INC  A
                LD   (ArmyInfoDigN), A
                LD   A, H
                OR   L
                JR   NZ, .dds
.ddo:           POP  AF                              ; старшая → младшая
                LD   E, A
                LD   D, 0
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                          ; d*4
                ADD  HL, DE                          ; d*5
                LD   DE, ArmyInfoDigitTab
                ADD  HL, DE
                CALL Battle_DrawEvtSprite            ; маска @ перо, перо += w×16
                LD   A, (ArmyInfoDigN)
                DEC  A
                LD   (ArmyInfoDigN), A
                JR   NZ, .ddo
                RET
ArmyInfoDigN:   DEFB 0

; Надписи окна итога нативными спрайтами поверх ×1.6-диалога (заголовок жёлтый / потери белые).
; Записи (11Б: [lo,mid,hi,w,h] + палитра + vx(2) + vy(2) + видимость) — в GlobalData #91
; (вынос: оверлей у потолка), копируются в BattleWinTextBuf через GData_ReadByte.
Battle_RenderWinText:
                LD   HL, GDBattleWinTextTab
                LD   (BattleWinTextPtr), HL
                LD   B, BATTLE_WIN_TEXT_COUNT
.wtloop:        PUSH BC
                LD   HL, (BattleWinTextPtr)         ; запись (11Б) из #91 → буфер
                LD   DE, BattleWinTextBuf
                LD   C, WIN_TEXT_REC
.wtcp:          CALL GData_ReadByte                 ; HL цел, портит B
                LD   (DE), A
                INC  HL
                INC  DE
                DEC  C
                JR   NZ, .wtcp
                LD   (BattleWinTextPtr), HL         ; HL уже на следующей записи
                LD   A, (BattleWinTextBuf + 10)     ; тег видимости: 0=всегда, 1=победа, 2=поражение
                OR   A
                JR   Z, .wtshow
                LD   HL, BattleResult
                CP   (HL)
                JR   NZ, .wtadv
.wtshow:        LD   A, (BattleWinTextBuf + 5)      ; палитра-флаг
                OR   A
                JR   Z, .wtwhite
                LD   HL, Battle_WinTitle_Begin_DL   ; жёлтый пролог (заголовок)
                LD   BC, Battle_WinTitle_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                JR   .wtpen
.wtwhite:       LD   HL, Battle_Status_Begin_DL     ; белый пролог (потери) — та же палитра, что статус
                LD   BC, Battle_Status_Begin_DL_SIZE
                CALL Render_CmdBufCopy
.wtpen:         LD   HL, (BattleWinTextBuf + 6)     ; vx
                LD   (ResPenX), HL
                LD   HL, (BattleWinTextBuf + 8)     ; vy
                LD   (ResPenY), HL
                LD   HL, BattleWinTextBuf           ; спрайт (addr24,w,h с +0)
                CALL Battle_DrawEvtSprite
                LD   HL, Battle_Status_End_DL
                LD   BC, Battle_Status_End_DL_SIZE
                CALL Render_CmdBufCopy
.wtadv:         POP  BC
                DJNZ .wtloop
                RET
BattleWinTextBuf: DEFS 11

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

; A=сторона → BattleCasK0/K1 = суммарно убито по типам 0/1 (СНАПШОТ старта − State.count).
Battle_CountKilled:
                LD   (BattleSideTmp), A
                LD   HL, 0
                LD   (BattleCasK0), HL
                LD   (BattleCasK1), HL
                LD   IX, BattleUnitState
                LD   IY, BattleStartCnt           ; стартовые count (Init≠старт при бое с монстром)
                LD   B, BATTLE_UNIT_COUNT
.ckl:           LD   A, (IX+2)                    ; side юнита
                LD   C, A
                LD   A, (BattleSideTmp)
                CP   C
                JR   NZ, .cknext
                LD   L, (IY+0)                    ; HL = стартовый count (снапшот)
                LD   H, (IY+1)
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
                LD   DE, 2
                ADD  IY, DE                       ; снапшот: 2Б/юнит
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
                PUSH BC                           ; ★тип через стек: DrawEvtSprite ПОРТИТ C (ширина!)
                                                  ;   — иначе выбор K0/K1 всегда падал в K1 (вечный «0»)
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
                POP  BC                           ; C = тип (восстановлен)
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

; Эмит спрайта юнита: вариант=(BattleTmpVar), слот=(BattleAnimSlot) → SOURCE кадра (per-вариант,
; зеркало = свой блоб) + LAYOUT/SIZE кадра (per-тип, общие для зеркала). Палитра/BEGIN — вызывающий.
; Портит A,BC,DE,HL.
Battle_EmitUnitSprite:
                LD   A, (BattleTmpVar)
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, BattleFrameSrcTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = блок SOURCE варианта
                LD   A, (BattleAnimSlot)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                        ; слот*4
                ADD  HL, DE
                LD   BC, 4
                CALL Render_CmdBufCopy             ; FT_BITMAP_SOURCE
                LD   A, (BattleTmpVar)
                SRL  A                             ; тип = вариант>>1
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, BattleFrameLayTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = блок LAYOUT/SIZE типа
                LD   A, (BattleAnimSlot)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, HL                        ; слот*8
                ADD  HL, DE
                LD   BC, 8
                JP   Render_CmdBufCopy             ; LAYOUT+SIZE (RET через JP)

; Вершина юнита ПО ОРИГИНАЛУ (GetTroopPosition): (BattleTmpAnchX/Y) + BattleFrameOfs[вариант][слот]
; → FT_VERTEX2F. Смещения per-кадр (ox/oy из ICN, reflect учтён в таблице) — данные в
; GlobalData #91 (вынос: оверлей у потолка), читаем 4Б через GData_ReadByte. Портит A,BC,DE,HL.
Battle_EmitUnitVertex:
                LD   A, (BattleTmpVar)
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, BattleFrameOfsTab
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                       ; DE = &GD-таблица варианта (#91-окно)
                LD   A, (BattleAnimSlot)
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                        ; слот*4
                ADD  HL, DE                        ; &(ofsX,ofsY) в #91
                LD   DE, BattleAnchBuf
                LD   C, 4
.euv:           CALL GData_ReadByte                ; HL цел, портит B
                LD   (DE), A
                INC  HL
                INC  DE
                DEC  C
                JR   NZ, .euv
                LD   HL, (BattleAnchBuf)           ; ofsX (знак.)
                LD   DE, (BattleTmpAnchX)
                ADD  HL, DE
                LD   (RenderPathVertexX), HL
                LD   HL, (BattleAnchBuf + 2)       ; ofsY (знак.)
                LD   DE, (BattleTmpAnchY)
                ADD  HL, DE
                LD   (RenderPathVertexY), HL
                JP   Render_WriteVertex2FCmd

; A=клетка → HL=&якорь клетки (ax lo,hi, ay lo,hi — 4Б в буфере). Таблица GDBattleCellAnchor
; в GlobalData #91 (вынос: оверлей у потолка) — копируем 4Б резидентным GData_ReadByte.
; Портит A,BC,DE,HL (раньше A,DE,HL — callers B не полагаются: проверено по всем 5 вызовам).
Battle_CellAnchorAddr:
                LD   L, A
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                        ; клетка*4
                LD   DE, GDBattleCellAnchor
                ADD  HL, DE
                LD   DE, BattleAnchBuf
                LD   C, 4
.cab:           CALL GData_ReadByte                ; A=(#91:HL); HL цел, портит B
                LD   (DE), A
                INC  HL
                INC  DE
                DEC  C
                JR   NZ, .cab
                LD   HL, BattleAnchBuf
                RET
BattleAnchBuf:  DEFS 4

; A=клетка → (BattleTmpAnchX/Y) = якорь клетки. Портит A,DE,HL.
Battle_SetCellAnchor:
                CALL Battle_CellAnchorAddr
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleTmpAnchX), DE
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleTmpAnchY), DE
                RET

; C=код группы (BATTLE_GRP_*), тип=(BattleTmpType) → HL=&seq {DEFB len, слоты...}. Z=1 если
; группы у типа нет (HL мусор). Портит A,DE,HL (B,C целы).
Battle_SeqAddr:
                LD   A, (BattleTmpType)
                ADD  A, A
                ADD  A, A                          ; тип*4
                LD   E, A
                ADD  A, A                          ; тип*8
                ADD  A, E                          ; тип*12 (=BATTLE_NGROUPS)
                ADD  A, C                          ; + группа
                ADD  A, A                          ; *2 (DEFW)
                LD   L, A
                LD   H, 0
                LD   DE, BattleSeqPtrTab           ; ★таблица в #91 (вынос из оверлея) → GData_ReadByte
                ADD  HL, DE
                CALL GData_ReadByte                ; A = lo (#91:HL); HL цел, портит B
                LD   E, A
                INC  HL
                CALL GData_ReadByte                ; A = hi
                LD   D, A
                OR   E                             ; D|E: указатель 0? (A=hi уже)
                EX   DE, HL                        ; HL = seq (или 0 → Z)
                RET

; C=группа → A=длина последовательности (0 если группы нет). Seq-данные в GlobalData #91
; (вынос: оверлей у потолка) — байты через GData_ReadByte. Портит A,B,DE,HL (C цел).
Battle_SeqLen:
                CALL Battle_SeqAddr
                LD   A, 0
                RET  Z
                JP   GData_ReadByte                ; A = len (#91:HL)

; C=группа, E=индекс кадра (клампится на последний) → (BattleAnimSlot).
; Нет группы → слот стойки типа. Портит A,B,DE,HL.
Battle_SeqSlot:
                PUSH DE                            ; SeqAddr клоббит DE (E=индекс!)
                CALL Battle_SeqAddr
                POP  DE
                JR   Z, .fallback
                CALL GData_ReadByte                ; A = len (#91:HL; HL цел)
                DEC  A
                CP   E
                JR   NC, .ok                       ; idx ≤ len−1
                LD   E, A                          ; кламп на последний кадр
.ok:            INC  HL                            ; &слоты
                LD   D, 0
                ADD  HL, DE
                CALL GData_ReadByte                ; A = слот кадра
                LD   (BattleAnimSlot), A
                RET
.fallback:      LD   A, (BattleTmpType)
                LD   HL, BattleStaticSlotTab
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                LD   A, (HL)
                LD   (BattleAnimSlot), A
                RET

; A = A / C (беззнак., через Battle_Div16by8). Портит F,B,HL (C цел).
Battle_DivA:
                LD   L, A
                LD   H, 0
                CALL Battle_Div16by8
                LD   A, L
                RET

; 8-бит LFSR (poly #1D). Портит F.
Battle_Rand8:
                LD   A, (BattleRndSeed)
                ADD  A, A
                JR   NC, .nox
                XOR  #1D
.nox:           LD   (BattleRndSeed), A
                RET

; A=индекс юнита, (BattleTmpType)=его тип → (BattleAnimSlot) ПО ОРИГИНАЛУ:
; смерть > атака (мили ATTACK2/END | выстрел SHOOT2/END) > движение (MOVE_MAIN цикл) >
; wince (WINCE_UP/END) > idle (per-юнит: STATIC или редкий IDLE-вариант). Портит A,BC,DE,HL.
Battle_CalcAnimSlot:
                LD   B, A                          ; B = индекс юнита
                LD   A, (BattleDeathActive)        ; умирает? → DEATH (кламп = труп)
                OR   A
                JR   Z, .nodeath
                LD   A, (BattleDeathUnit)
                CP   B
                JR   NZ, .nodeath
                LD   A, (BattleAnimTicks)
                LD   C, A
                LD   A, (BattleDeathProg)
                CALL Battle_DivA
                LD   E, A
                LD   C, BATTLE_GRP_DEATH
                JP   Battle_SeqSlot
.nodeath:       LD   A, (BattleAtkActive)          ; атакует? → мейн/END фаза
                OR   A
                JR   Z, .noatk
                LD   A, (BattleAtkUnit)
                CP   B
                JR   NZ, .noatk
                LD   A, (BattleAtkShoot)
                OR   A
                JR   NZ, .shoot
                LD   A, (BattleAnimTicks)          ; мили: idx = prog/тик
                LD   C, A
                LD   A, (BattleAtkProg)
                CALL Battle_DivA
                LD   E, A
                LD   C, BATTLE_GRP_ATTACK2
                JR   .phase2
.shoot:         LD   A, (BattleTmpType)            ; выстрел: idx = prog/shootTick (shootSpeed/len)
                LD   HL, BattleShootTickTab
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                LD   C, (HL)
                LD   A, (BattleAtkProg)
                CALL Battle_DivA
                LD   E, A
                LD   C, BATTLE_GRP_SHOOT2
.phase2:        ; E=idx, C=мейн-группа; idx≥len(мейн) → END-группа (= мейн+1 в ANIM_GROUPS), idx−=len
                PUSH DE
                CALL Battle_SeqLen                 ; A = len мейн (C цел)
                POP  DE
                CP   E
                JR   Z, .toend
                JR   NC, .mainok                   ; len > idx → мейн-фаза
.toend:         LD   D, A
                LD   A, E
                SUB  D
                LD   E, A
                LD   D, 0
                INC  C                             ; ATTACK2_END/SHOOT2_END/WINCE_END
.mainok:        JP   Battle_SeqSlot
.noatk:         LD   A, (BattleMoveActive)         ; движется? → цикл MOVE_MAIN
                OR   A
                JR   Z, .nomove
                LD   A, (BattleMoveUnit)
                CP   B
                JR   NZ, .nomove
                LD   A, (BattleTmpType)            ; idx = (prog/moveTick) & 7 (len=8, 465мс/клетку)
                LD   HL, BattleMoveTickTab
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                LD   C, (HL)
                LD   A, (BattleMoveProg)
                CALL Battle_DivA
                AND  7
                LD   E, A
                LD   C, BATTLE_GRP_MOVE_MAIN
                JP   Battle_SeqSlot
.nomove:        LD   A, (BattleWinceActive)        ; wince (получил урон, выжил)?
                OR   A
                JR   Z, .idle
                LD   A, (BattleWinceUnit)
                CP   B
                JR   NZ, .idle
                LD   A, (BattleAnimTicks)
                LD   C, A
                LD   A, (BattleWinceProg)
                CALL Battle_DivA
                LD   E, A
                LD   C, BATTLE_GRP_WINCE_UP
                JR   .phase2
.idle:          LD   E, B                          ; per-юнит idle-состояние
                LD   D, 0
                LD   HL, BattleIdleGrp
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   NZ, .idlevar
                LD   C, BATTLE_GRP_STATIC          ; стоит
                LD   E, 0
                JP   Battle_SeqSlot
.idlevar:       LD   C, A                          ; играет IDLE-вариант (код группы = 1..3)
                LD   HL, BattleIdleIdx
                ADD  HL, DE
                LD   E, (HL)
                LD   D, 0
                JP   Battle_SeqSlot

; E=юнит (D=0), (BattleTmpType)=тип: wait = IdleWaitMin[тип] + (rand8 & MASK)
; (≈ idleDelay × 75..125% оригинала). Портит A,BC,HL (DE цел).
Battle_SetIdleWait:
                LD   A, (BattleTmpType)
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   BC, BattleIdleWaitMinTab
                ADD  HL, BC
                LD   C, (HL)
                INC  HL
                LD   B, (HL)                       ; BC = min (тиков)
                CALL Battle_Rand8
                AND  BATTLE_IDLE_RND_MASK
                LD   L, A
                LD   H, 0
                ADD  HL, BC
                LD   C, L
                LD   B, H                          ; BC = wait
                LD   HL, BattleIdleWait
                ADD  HL, DE
                ADD  HL, DE                        ; + юнит*2
                LD   (HL), C
                INC  HL
                LD   (HL), B
                RET

; Инициализация анимаций на входе в бой: сброс idle/wince, посев LFSR, паузы по типам.
Battle_InitIdle:
                LD   A, R
                OR   1                             ; LFSR ≠ 0
                LD   (BattleRndSeed), A
                XOR  A
                LD   (BattleWinceActive), A
                LD   (BattleArrowPend), A
                LD   (BattleCorpsePass), A
                LD   HL, BattleIdleGrp             ; Grp+Idx+Tick смежны → чистим разом
                LD   B, BATTLE_UNIT_COUNT * 3
.clr:           LD   (HL), A
                INC  HL
                DJNZ .clr
                LD   DE, 0                         ; юнит
.wl:            PUSH DE
                LD   A, E
                CALL Battle_UnitAddr               ; клоббит DE!
                LD   A, (HL)                       ; тип
                LD   (BattleTmpType), A
                POP  DE
                CALL Battle_SetIdleWait
                INC  E
                LD   A, E
                CP   BATTLE_UNIT_COUNT
                JR   C, .wl
                RET

; Фоновый тик анимаций (каждый кадр, независимо от хода/анимаций действия):
; wince цели + per-юнит idle ПО ОРИГИНАЛУ (STATIC → редкий IDLE-вариант по priorities → STATIC).
Battle_AnimBgTick:
                LD   A, (BattleWinceActive)
                OR   A
                JR   Z, .nowince
                LD   A, (BattleWinceProg)
                INC  A
                LD   (BattleWinceProg), A
                LD   HL, BattleWinceTotal
                CP   (HL)
                JR   C, .nowince
                XOR  A
                LD   (BattleWinceActive), A
.nowince:       XOR  A
.iloop:         LD   (BattleIdleCur), A
                CALL Battle_UnitAddr               ; HL = &{type,cell,side,count}
                LD   A, (HL)
                LD   (BattleTmpType), A
                INC  HL
                INC  HL
                INC  HL
                LD   A, (HL)
                INC  HL
                OR   (HL)
                JP   Z, .inext                     ; мёртв → пропуск
                LD   A, (BattleIdleCur)
                LD   E, A
                LD   D, 0
                LD   HL, BattleIdleGrp
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   NZ, .playing
                ; STATIC: wait−−; по нулю выбрать idle-вариант по порогам rand8 (priorities BIN)
                LD   HL, BattleIdleWait
                ADD  HL, DE
                ADD  HL, DE
                LD   C, (HL)
                INC  HL
                LD   B, (HL)                       ; BC = wait
                LD   A, B
                OR   C
                JR   Z, .pick                      ; страховка
                DEC  BC
                LD   (HL), B
                DEC  HL
                LD   (HL), C
                LD   A, B
                OR   C
                JP   NZ, .inext
.pick:          CALL Battle_Rand8
                LD   C, A                          ; C = rand
                LD   A, (BattleTmpType)            ; пороги = BattleIdleThreshTab[тип*3]
                ADD  A, A
                LD   L, A
                LD   A, (BattleTmpType)
                ADD  A, L                          ; тип*3
                LD   L, A
                LD   H, 0
                PUSH DE
                LD   DE, BattleIdleThreshTab
                ADD  HL, DE
                POP  DE
                INC  HL                            ; → порог1 (n вариантов учтён порогами)
                LD   A, C
                CP   (HL)
                LD   B, 1                          ; < порог1 → IDLE1
                JR   C, .chose
                INC  HL
                CP   (HL)
                LD   B, 2                          ; < порог2 → IDLE2
                JR   C, .chose
                LD   B, 3                          ; иначе IDLE3
.chose:         LD   HL, BattleIdleGrp
                ADD  HL, DE
                LD   (HL), B
                LD   HL, BattleIdleIdx
                ADD  HL, DE
                LD   (HL), 0
                LD   HL, BattleIdleTick
                ADD  HL, DE
                LD   (HL), 0
                JP   .inext
.playing:       LD   C, A                          ; C = группа (1..3)
                LD   HL, BattleIdleTick
                ADD  HL, DE
                LD   A, (HL)
                INC  A
                LD   (HL), A
                PUSH HL                            ; кадр раз в BattleAnimTicks (120мс @ speed4)
                LD   HL, BattleAnimTicks
                CP   (HL)
                POP  HL
                JP   C, .inext
                LD   (HL), 0
                LD   HL, BattleIdleIdx
                ADD  HL, DE
                LD   A, (HL)
                INC  A
                LD   (HL), A                       ; idx++
                PUSH DE
                PUSH HL
                CALL Battle_SeqLen                 ; A = len варианта (C цел)
                POP  HL
                POP  DE
                CP   (HL)                          ; len vs новый idx
                JR   Z, .iend                      ; idx==len → конец варианта
                JP   NC, .inext                    ; idx<len → играем дальше
.iend:          LD   HL, BattleIdleGrp             ; конец → STATIC + новая пауза
                ADD  HL, DE
                LD   (HL), 0
                CALL Battle_SetIdleWait
.inext:         LD   A, (BattleIdleCur)
                INC  A
                CP   BATTLE_UNIT_COUNT
                JP   C, .iloop
                RET

; Проход рендера юнитов (внутри Battle_Units_Begin/End_DL). (BattleCorpsePass)=1 → рисуем
; ТОЛЬКО трупы (count==0, старт>0, НЕ умирающий: последний DEATH-кадр на клетке);
; =0 → только живых (+ умирающего с DEATH-анимацией). Портит всё.
Battle_DrawUnitsPass:
                LD   HL, BattleUnitState
                LD   (BattleUnitPtr), HL
                XOR  A
                LD   (BattleRenderIdx), A
                LD   B, BATTLE_UNIT_COUNT
.uloop:         PUSH BC
                LD   HL, (BattleUnitPtr)          ; поля юнита → temp
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
                JR   NZ, .alive
                LD   A, (BattleDeathActive)         ; count==0: умирающий (анимация)?
                OR   A
                JR   Z, .corpse
                LD   A, (BattleRenderIdx)
                LD   HL, BattleDeathUnit
                CP   (HL)
                JR   NZ, .corpse
                LD   A, (BattleCorpsePass)          ; умирающий рисуется в ЖИВОМ проходе
                OR   A
                JP   NZ, .uskip
                JR   .draw_anim
.corpse:        LD   A, (BattleCorpsePass)          ; труп: только в трупном проходе
                OR   A
                JP   Z, .uskip
                LD   A, (BattleRenderIdx)           ; участвовал? (BattleStartCnt[idx]≠0 — не пустой слот)
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, BattleStartCnt
                ADD  HL, DE
                LD   A, (HL)
                INC  HL
                OR   (HL)
                JP   Z, .uskip
                LD   A, (BattleTmpType)             ; слот трупа = последний DEATH-кадр
                LD   HL, BattleCorpseSlotTab
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                LD   A, (HL)
                LD   (BattleAnimSlot), A
                JR   .draw_common
.alive:         LD   A, (BattleCorpsePass)          ; живой: не в трупном проходе
                OR   A
                JP   NZ, .uskip
.draw_anim:     LD   A, (BattleRenderIdx)           ; слот по состоянию (смерть/атака/движение/wince/idle)
                CALL Battle_CalcAnimSlot
.draw_common:   LD   A, (BattleTmpType)             ; вариант = type*2+side
                ADD  A, A
                LD   C, A
                LD   A, (BattleTmpSide)
                ADD  A, C
                LD   (BattleTmpVar), A
                CALL Battle_EmitUnitSprite
                LD   A, (BattleMoveActive)          ; якорь: движущийся → интерполяция; иначе клетка
                OR   A
                JR   Z, .anchcell
                LD   A, (BattleRenderIdx)
                LD   HL, BattleMoveUnit
                CP   (HL)
                JR   NZ, .anchcell
                LD   HL, (BattleMoveCurX)
                LD   (BattleTmpAnchX), HL
                LD   HL, (BattleMoveCurY)
                LD   (BattleTmpAnchY), HL
                JR   .vtx
.anchcell:      LD   A, (BattleTmpCell)
                CALL Battle_SetCellAnchor
.vtx:           CALL Battle_EmitUnitVertex          ; вершина = якорь + смещение кадра (reflect в табл.)
.uskip:         POP  BC
                LD   A, (BattleRenderIdx)
                INC  A
                LD   (BattleRenderIdx), A
                DEC  B
                JP   NZ, .uloop
                RET

; Запустить анимацию движения активного юнита из его клетки в BattleMoveDestCell.
; ПО ОРИГИНАЛУ: длительность пропорциональна дистанции (BIN moveSpeed 465мс/клетку):
; steps = max(|dX|,|dY|)/BATTLE_MOVE_VEL (48 v-ед/тик ≈ 44px-клетка за 23 тика), кламп 12..120.
; Интерполируется ЯКОРЬ (низ-центр); кадр добавляет своё смещение.
Battle_StartMove:
                LD   A, (BattleActiveUnit)
                LD   (BattleMoveUnit), A
                CALL Battle_UnitAddr
                LD   A, (HL)                        ; тип
                LD   (BattleTmpType), A
                INC  HL
                LD   A, (HL)                        ; from-клетка
                LD   (BattleMoveSrcCell), A         ; запомнить src для строки «Moved …: from [src] to [dst].»
                CALL Battle_CellAnchorAddr          ; HL = &anchor[from]
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleMoveCurX), DE           ; Cur = якорь from
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleMoveCurY), DE
                LD   A, (BattleMoveDestCell)
                CALL Battle_CellAnchorAddr          ; HL = &anchor[dest]
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                INC  HL
                PUSH HL                             ; &anchor.y dest
                LD   HL, (BattleMoveCurX)
                EX   DE, HL                         ; HL=toX, DE=fromX
                OR   A
                SBC  HL, DE
                LD   (BattleMoveStepX), HL          ; временно dX
                POP  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   HL, (BattleMoveCurY)
                EX   DE, HL                         ; HL=toY, DE=fromY
                OR   A
                SBC  HL, DE
                LD   (BattleMoveStepY), HL          ; временно dY
                ; steps = max(|dX|,|dY|) / BATTLE_MOVE_VEL, кламп 12..120
                CALL Battle_Abs16                   ; HL = |dY|
                PUSH HL
                LD   HL, (BattleMoveStepX)
                CALL Battle_Abs16                   ; HL = |dX|
                POP  DE
                OR   A                              ; max(|dX|,|dY|)
                SBC  HL, DE
                ADD  HL, DE                         ; сравнить, HL восстановлен
                JR   NC, .xmax
                EX   DE, HL
.xmax:          LD   A, (BattleMoveVel)
                LD   C, A
                CALL Battle_Div16by8                ; HL = дистанция/скорость
                LD   A, H
                OR   A
                JR   NZ, .clhi                      ; >255 → кламп сверху
                LD   A, L
                CP   121
                JR   C, .cklo
.clhi:          LD   A, 120
.cklo:          CP   12
                JR   NC, .stok
                LD   A, 12
.stok:          LD   (BattleMoveSteps), A
                LD   C, A                           ; шаги = делитель
                LD   HL, (BattleMoveStepX)          ; stepX = dX/steps (знак.)
                CALL Battle_SDiv16by8
                LD   (BattleMoveStepX), HL
                LD   HL, (BattleMoveStepY)
                CALL Battle_SDiv16by8
                LD   (BattleMoveStepY), HL
                XOR  A
                LD   (BattleMoveProg), A
                LD   A, 1
                LD   (BattleMoveActive), A
                RET

; HL = |HL| (16-бит модуль). Портит A,F.
Battle_Abs16:
                BIT  7, H
                RET  Z
; HL = −HL. Портит A,F.
Battle_Neg16:
                XOR  A
                SUB  L
                LD   L, A
                SBC  A, A
                SUB  H
                LD   H, A
                RET

; HL = HL / C ЗНАКОВО (C беззнак. ≤127). Портит AF,B.
Battle_SDiv16by8:
                BIT  7, H
                JP   Z, Battle_Div16by8
                CALL Battle_Neg16
                CALL Battle_Div16by8
                JP   Battle_Neg16

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
                LD   HL, BattleMoveSteps
                CP   (HL)
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
; AttackAllowed). ПО ОРИГИНАЛУ: тайминги из BattleAtkTimTab (пик=контакт=конец мейн-фазы,
; мили ATTACK2+END @120мс, выстрел SHOOT2+END @shootSpeed/len). Урон в ПИКЕ (Battle_AtkTick);
; по завершении — ответка + ход. Стрела запускается тиком (пик−32) — долетает точно к урону.
Battle_StartAttack:
                LD   A, (BattleActiveUnit)
                LD   (BattleAtkUnit), A
                XOR  A
                LD   (BattleAtkProg), A
                LD   (BattleAtkHit), A
                LD   (BattleAtkShoot), A
                LD   (BattleArrowPend), A
                LD   A, (BattleAtkUnit)             ; тайминги по типу и виду атаки
                CALL Battle_UnitAddr
                LD   A, (HL)                        ; тип
                ADD  A, A
                ADD  A, A                           ; тип*4 (мили пик,всего, выстрел пик,всего)
                LD   L, A
                LD   H, 0
                LD   DE, BattleAtkTimTab
                ADD  HL, DE
                LD   A, (BattleWasMelee)
                OR   A
                JR   NZ, .tim
                INC  HL
                INC  HL                             ; → выстрел
.tim:           LD   A, (HL)
                LD   (BattleAtkPeak), A
                INC  HL
                LD   A, (HL)
                LD   (BattleAtkTotal), A
                LD   A, 1
                LD   (BattleAtkActive), A
                LD   A, (BattleWasMelee)
                OR   A
                RET  NZ                              ; мили — готово
                LD   A, 1                            ; ВЫСТРЕЛ: SHOOT-кадры + план запуска стрелы
                LD   (BattleAtkShoot), A
                LD   (BattleArrowPend), A
                LD   A, (BattleArrowSteps)           ; запуск = пик − полёт
                LD   C, A
                LD   A, (BattleAtkPeak)
                SUB  C
                JR   NC, .lok
                XOR  A
.lok:           LD   (BattleArrowLaunch), A
                LD   A, (BattleAtkUnit)             ; --_shotsLeft (battle_troop.cpp:951)
                LD   HL, BattleUnitShots
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                RET  Z                              ; страховка от underflow
                DEC  (HL)
                RET

; Запуск полёта стрелы (из Battle_AtkTick в тик BattleArrowLaunch): старт/конец = якоря клеток
; на высоте груди (BATTLE_ARROW_YOFS); шаг = (end−start)>>5 (32 тика полёта).
Battle_StartArrow:
                LD   A, (BattleAtkUnit)             ; атакующий → Cur + направление
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)                        ; клетка
                INC  HL
                LD   C, (HL)                        ; сторона → направление (0=вправо/1=влево)
                PUSH AF
                LD   A, C
                LD   (BattleArrowDir), A
                POP  AF
                CALL Battle_CellAnchorAddr          ; HL = &anchor[atk]
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleArrowCurX), DE
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   DE, BATTLE_ARROW_YOFS          ; на высоте груди (якорь = ноги)
                ADD  HL, DE
                LD   (BattleArrowCurY), HL
                LD   A, (BattleTargetUnit)          ; цель → End
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)
                CALL Battle_CellAnchorAddr
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleArrowEndX), DE
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                EX   DE, HL
                LD   DE, BATTLE_ARROW_YOFS
                ADD  HL, DE
                LD   (BattleArrowEndY), HL
                LD   HL, (BattleArrowEndX)          ; stepX = (End−Cur)/steps (steps per speed)
                LD   DE, (BattleArrowCurX)
                OR   A
                SBC  HL, DE
                LD   A, (BattleArrowSteps)
                LD   C, A
                CALL Battle_SDiv16by8
                LD   (BattleArrowStepX), HL
                LD   HL, (BattleArrowEndY)          ; stepY = (End−Cur)/steps
                LD   DE, (BattleArrowCurY)
                OR   A
                SBC  HL, DE
                LD   A, (BattleArrowSteps)
                LD   C, A
                CALL Battle_SDiv16by8
                LD   (BattleArrowStepY), HL
                XOR  A
                LD   (BattleArrowProg), A
                INC  A
                LD   (BattleArrowActive), A
                RET

; Тик анимации атаки (каждый кадр): запуск стрелы в спланированный тик; в пике-КОНТАКТЕ —
; применить урон; по завершении (мейн+END) — ответка + след.ход.
Battle_AtkTick:
                LD   A, (BattleArrowPend)           ; запуск стрелы в тик BattleArrowLaunch
                OR   A
                JR   Z, .nopend
                LD   A, (BattleArrowLaunch)
                LD   C, A
                LD   A, (BattleAtkProg)
                CP   C
                JR   C, .nopend
                XOR  A
                LD   (BattleArrowPend), A
                CALL Battle_StartArrow
.nopend:        LD   A, (BattleArrowActive)         ; стрела в полёте → двигать (долетает к пику)
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
                LD   HL, BattleArrowSteps
                CP   (HL)
                JR   C, .noarrow
                XOR  A
                LD   (BattleArrowActive), A         ; долетела (в момент урона)
.noarrow:       LD   A, (BattleAtkProg)
                INC  A
                LD   (BattleAtkProg), A
                LD   HL, BattleAtkPeak              ; ПИК-контакт → урон (один раз)
                CP   (HL)
                JR   C, .atknotpeak
                LD   A, (BattleAtkHit)
                OR   A
                JR   NZ, .atknotpeak
                LD   A, 1
                LD   (BattleAtkHit), A
                CALL Battle_Attack                  ; урон цели (active→target, флаги уже выставлены)
.atknotpeak:    LD   A, (BattleAtkProg)
                LD   HL, BattleAtkTotal
                CP   (HL)
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
                LD   A, (BattleDeathUnit)           ; длительность = len(DEATH)×6 по типу умирающего
                CALL Battle_UnitAddr
                LD   A, (HL)
                LD   HL, BattleDeathTicksTab
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                LD   A, (HL)
                LD   (BattleDeathTicks), A
                LD   A, 1
                LD   (BattleDeathActive), A         ; BattleDeathUnit уже выставлен в Battle_Attack
                RET
.atkdone:       JP   Battle_EndTurn

; Тик анимации смерти: играть DEATH-кадры; по завершении отряд ОСТАЁТСЯ ЛЕЖАТЬ трупом
; (последний DEATH-кадр, трупный проход рендера) до конца боя — как в оригинале.
Battle_DeathTick:
                LD   A, (BattleDeathProg)
                INC  A
                LD   (BattleDeathProg), A
                LD   HL, BattleDeathTicks
                CP   (HL)
                RET  C                              ; ещё играет
                XOR  A
                LD   (BattleDeathActive), A
                JP   Battle_EndTurn

; ============================================================================
; AI боя = AI::BattlePlanner planUnitTurn (ai_battle.cpp) для безгеройного skirmish.
; Не переносится по скоупу порта: спеллы (Step 2/3 — у монстров карты нет героя-командира,
; ретрит/сдача/каст неприменимы), осада (замковых боёв нет). Дерево по оригиналу:
; analyzeBattleState (тактика Def/Off + cautious) → СТРЕЛОК: archerDecision (кайтинг/
; мили-в-упоре/выстрел по max threat); МИЛИ Defense: прикрыть стрелков/бить блокирующих;
; МИЛИ Offense: getMeleeBestOutcome (атакуемая-в-ход цель, posValue→threat) → иначе подход
; (2 прохода non-evader; при cautious — стоп на пути с мин. угрозой) → SKIP.
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
                JP   Battle_AIArcherTurn            ; СТРЕЛОК: archerDecision (кайтинг/мили-в-упоре/выстрел)
.melee:         CALL Battle_ComputeReachable        ; достижимость активного в этот ход (для §1 и подхода)
                CALL Battle_AIBuildThreatCache      ; кэши threat/archer/cell/сила своих (весь пейджинг здесь)
                CALL Battle_AIAnalyze               ; analyzeBattleState → _defensiveTactics/_cautious
                LD   A, (BattleDefTactics)          ; melee-дерево: Defense или Offense (planUnitTurn :903)
                OR   A
                JR   Z, .offense
                CALL Battle_AIMeleeDefense          ; ОБОРОНА: прикрыть стрелков/бить блокирующих/зона
                OR   A
                JP   Z, .endturn                    ; 0 → SKIP хода
                DEC  A
                JR   Z, .defmove                    ; 1 → MOVE (dest уже стоит)
                JR   .attackgo                      ; 2 → ATTACK (Target+Dest от MBO)
.defmove:       CALL Battle_StartMove               ; движение без атаки (прикрытие)
                XOR  A
                LD   (BattlePendAttack), A
                RET
.offense:       CALL Battle_AIMeleeBestOutcome      ; §1: лучшая АТАКУЕМАЯ-в-ход цель (posValue→threat)
                OR   A                              ;   → BattleTargetUnit + BattleMoveDestCell (клетка атаки)
                JR   Z, .approach                   ; никого не достать в этот ход → подойти (§2)
.attackgo:      LD   A, (BattleActiveUnit)           ; клетка атаки == текущая? → бить сразу
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)
                LD   HL, BattleMoveDestCell
                CP   (HL)
                JP   Z, Battle_StartAttack           ; уже на клетке атаки → атака
                CALL Battle_StartMove                ; иначе двигаться на клетку атаки
                LD   A, 1
                LD   (BattlePendAttack), A           ; по приходу — атаковать BattleTargetUnit
                RET
.approach:      CALL Battle_AIPickApproach           ; §2: цель подхода = max(threat/dist), non-evader
                LD   A, (BattleTargetUnit)
                CP   #FF
                JP   Z, .endturn                     ; врагов нет (не должно) → пропуск
                CALL Battle_AIMoveToward             ; Reach уже посчитан выше → ближайшая достижимая клетка к цели
                LD   A, (BattleCautious)             ; _cautiousOffensive → стоп на пути с мин. угрозой (:1628)
                OR   A
                CALL NZ, Battle_AICautiousStop
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

; Применить скорость боя (Game::UpdateGameSpeed): скопировать набор тик-таблиц скорости
; BattleSpeedSetting (резидент, 1..10; мусор → дефолт 4) в рабочий блок BattleAnimTicks..
; BattleArrowSteps (21Б подряд, layout = GDBattleSpeedSets в GlobalData #91 — оверлей боя у
; потолка 16К; чтение резидентным GData_ReadByte, HL цел). Портит A,BC,DE,HL.
Battle_ApplySpeed:
                LD   A, (BattleSpeedSetting)
                DEC  A                              ; 1..10 → 0..9
                CP   10
                JR   C, .vs
                LD   A, 4                           ; вне диапазона (холодный старт) → 4
                LD   (BattleSpeedSetting), A
                LD   A, 3
.vs:            LD   HL, 0                          ; HL = idx × BATTLE_SPEED_SET_LEN (#91-окно)
                LD   DE, BATTLE_SPEED_SET_LEN        ; ★НЕ хардкод 21: len=3+9×юнитов (4 юнита → 39)
                OR   A                              ; idx (в A) == 0?
                JR   Z, .off
                LD   B, A
.mul:           ADD  HL, DE
                DJNZ .mul
.off:           LD   DE, GDBattleSpeedSets
                ADD  HL, DE
                LD   DE, BattleAnimTicks            ; рабочий блок (BATTLE_SPEED_SET_LEN Б подряд)
                LD   C, BATTLE_SPEED_SET_LEN
.cp:            CALL GData_ReadByte                 ; A = (#91:HL); HL цел, портит B
                LD   (DE), A
                INC  HL
                INC  DE
                DEC  C
                JR   NZ, .cp
                RET

; ★Battle_EvalThreat — Troop::evaluateThreatForUnit (battle_troop.cpp): насколько ВРАГ C (как
; атакующий) угрожает активному юниту (как защите). По оригиналу:
;   threat = getPotentialDamage(enemy) / distanceModifier(enemy → active)
;   getPotentialDamage = enemy.count × enemy.avgDmg × mod(enemy.attack − active.defense)
;   distanceModifier: стрелок → 1.0 (бьёт отовсюду); иначе dist=GetDistance(enemy,active),
;     range=speed+1; dist≤range → 1.0; иначе 1.5·dist/speed → threat×2·speed÷(3·dist).
; (У Knight нет летунов; летающих учтём при добавлении рас с флагом полёта.)
; IN: C=enemyIdx. OUT: HL=threat (16-бит, cap FFFF). Портит всё. ВСЕ slot3-чтения — ДО MonsterStats_Read.
Battle_EvalThreat:
                ; ---- Фаза A: все чтения slot3-state ДО пейджинга MonsterStats_Read ----
                LD   A, (BattleActiveUnit)           ; активный: id (type+1) + cell
                CALL Battle_UnitAddr                 ; HL=&type[active]
                LD   A, (HL)
                CALL Battle_TypeToMonId  ; type→id
                LD   (BattleThrAId), A               ; active.id
                INC  HL
                LD   A, (HL)
                LD   (BattleThrACell), A             ; active.cell
                LD   A, C                            ; враг C: id + cell + count
                CALL Battle_UnitAddr                 ; HL=&type[enemy]
                LD   A, (HL)
                CALL Battle_TypeToMonId  ; type→id
                LD   (BattleThrEId), A               ; enemy.id
                INC  HL
                LD   A, (HL)
                LD   (BattleThrECell), A             ; enemy.cell (+1)
                INC  HL                              ; +2 side
                INC  HL                              ; +3 count_lo
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                         ; DE = enemy.count
                LD   (BattleThrCnt), DE
                PUSH BC                              ; isArchers врага = ОСТАТОК (BattleUnitShots),
                LD   A, C                            ;   не статы (Unit::GetShots=_shotsLeft)
                LD   HL, BattleUnitShots
                CALL Battle_IdxByte
                LD   A, (HL)
                LD   (BattleThrEShots), A
                POP  BC
                ; ---- Фаза B: статы (#91) ----
                LD   A, (BattleThrAId)               ; защита активного
                LD   B, A
                CALL MonsterStats_Read
                LD   A, (MonsterStatBuf + 1)
                LD   (BattleThrDef), A
                LD   A, (BattleThrEId)               ; статы врага (attack/dmg/speed/shots)
                LD   B, A
                CALL MonsterStats_Read
                ; ---- potDmg = getPotentialDamage = (mod(count·dmgMin)+mod(count·dmgMax)) / 2 ----
                ; Модификатор применяется к min и max ОТДЕЛЬНО, затем среднее (как fheroes2:
                ; (CalculateMinDamage+CalculateMaxDamage)/2) — сохраняет ½ у нечётного dmg-диапазона.
                LD   A, (MonsterStatBuf)             ; r = enemy.attack − active.defense
                LD   HL, BattleThrDef
                SUB  (HL)
                LD   (BattleThrR), A                 ; сохранить r (ApplyDmgMod портит A)
                LD   A, (MonsterStatBuf + 2)         ; dmgMin
                CALL .etcntmul                       ; HL = count × dmgMin (cap FFFF)
                LD   A, (BattleThrR)
                CALL Battle_ApplyDmgMod              ; HL = mod(count·dmgMin) = potMin
                PUSH HL
                LD   A, (MonsterStatBuf + 3)         ; dmgMax
                CALL .etcntmul                       ; HL = count × dmgMax (cap FFFF)
                LD   A, (BattleThrR)
                CALL Battle_ApplyDmgMod              ; HL = potMax
                POP  DE                              ; DE = potMin
                ADD  HL, DE                          ; HL = potMin+potMax (CF = бит16)
                RR   H                               ; (17-бит) >> 1
                RR   L                               ; HL = potDmg
                ; ---- distanceModifier ----
                LD   A, (BattleThrEShots)            ; ОСТАТОК шотов врага (Phase A): >0 → стрелок →
                OR   A                               ;   distMod=1.0 → threat=potDmg
                RET  NZ
                PUSH HL                              ; сохранить potDmg (GetDistance портит HL)
                LD   A, (BattleThrECell)
                LD   D, A                            ; D=enemy.cell
                LD   A, (BattleThrACell)
                LD   E, A                            ; E=active.cell
                CALL Battle_GetDistance              ; A = dist (гекс-6)
                LD   C, A                            ; C=dist
                LD   A, (MonsterStatBuf + 6)         ; speed (буфер не тронут GetDistance)
                LD   (BattleThrESpd), A              ; побочно: speed врага (для non-evader теста)
                LD   B, A                            ; B=speed
                INC  A                               ; range = speed+1
                CP   C                               ; range − dist: CF ⇒ dist>range (далеко)
                JR   C, .etfar
                POP  HL                              ; dist≤range → 1.0 → threat=potDmg
                RET
.etfar:         POP  HL                              ; HL = potDmg
                LD   D, H
                LD   E, L                            ; DE = potDmg
                LD   A, B                            ; product = potDmg × 2·speed (cap FFFF)
                ADD  A, A
                LD   B, A                            ; B = 2·speed (счётчик)
                LD   HL, 0
                OR   A
                JR   Z, .etfz
.etfmul:        ADD  HL, DE
                JR   C, .etfcap
                DJNZ .etfmul
                JR   .etfdiv
.etfcap:        LD   HL, #FFFF
.etfdiv:        LD   A, C                            ; делитель = 3·dist
                ADD  A, A
                ADD  A, C
                LD   C, A
                CALL Battle_Div16by8                 ; HL = product ÷ (3·dist)
                RET
.etfz:          LD   HL, 0                           ; speed 0 (не бывает) → 0
                RET
; внутр.: A=множитель → HL = count(BattleThrCnt) × A (повт.сложение, cap FFFF). Портит A,B,DE,HL.
.etcntmul:      LD   B, A
                LD   DE, (BattleThrCnt)
                LD   HL, 0
                LD   A, B
                OR   A
                RET  Z
.etcm1:         ADD  HL, DE
                JR   C, .etcmcap
                DJNZ .etcm1
                RET
.etcmcap:       LD   HL, #FFFF
                RET

; Лучшая цель AI = живой ВРАГ с макс. угрозой evaluateThreatForUnit (Battle_EvalThreat).
; Эталон: берётся максимум по врагам. OUT: BattleTargetUnit (#FF если врагов нет).
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
                ; C=индекс живого врага → угроза = evaluateThreatForUnit(C)
                PUSH BC                              ; сохранить C (EvalThreat портит всё)
                CALL Battle_EvalThreat               ; HL = threat (потенц.урон ÷ дист-модификатор)
                POP  BC                              ; C = индекс врага
                PUSH HL                              ; threat
                LD   DE, (BattleAIBestScore)
                OR   A
                SBC  HL, DE                          ; threat − best
                POP  HL                              ; threat
                JR   C, .ftnext                      ; threat < best → пропуск
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

; ★Battle_AIPickApproach — meleeUnitOffense шаг 2 (нет цели в досягаемости этот ход): выбрать
; ВРАГА для подхода с макс. приоритетом = evaluateThreatForUnit / distance. Два прохода как в
; оригинале: (1) только враги, что НЕ увернутся — стрелок / speed==0 / медленнее активного;
; (2) если таких нет — все достижимые. dist = гекс-6 (аппрокс. длины пути к соседней клетке).
; Ставит BattleTargetUnit (#FF если врагов нет). Портит всё. (Летунов у Knight нет —
; flying-ветку добавить с расами полёта.) Cross-mult даёт точный порядок threat/dist без float.
Battle_AIPickApproach:
                LD   A, (BattleActiveUnit)           ; сторона/клетка/speed активного
                CALL Battle_UnitAddr
                PUSH HL
                INC  HL
                LD   A, (HL)
                LD   (BattleApprActCell), A           ; active.cell
                INC  HL
                LD   A, (HL)
                LD   (BattleAISide), A                ; active.side
                POP  HL
                LD   A, (HL)                          ; active.type → id
                CALL Battle_TypeToMonId  ; type→id
                LD   B, A
                CALL MonsterStats_Read
                LD   A, (MonsterStatBuf + 6)
                LD   (BattleApprActSpd), A            ; active.speed
                LD   A, 1
                LD   (BattleApprPass), A              ; проход 1 = non-evaders
.appass:        LD   A, #FF
                LD   (BattleApprBestTgt), A
                LD   C, 0
.aploop:        LD   A, C
                LD   (BattleApprIdx), A                ; индекс — восстанавливается в .apnext во всех путях
                CALL Battle_UnitAddr                  ; враг? (сторона != active.side)
                PUSH HL
                INC  HL
                INC  HL
                LD   A, (HL)
                LD   HL, BattleAISide
                CP   (HL)
                POP  HL
                JP   Z, .apnext                       ; своя сторона
                PUSH HL                               ; жив? count
                INC  HL
                INC  HL
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                POP  HL
                LD   A, D
                OR   E
                JP   Z, .apnext                       ; мёртв
                CALL Battle_EvalThreat                ; HL=threat (+ThrECell/EShots/ESpd); C=enemyIdx (вход, из .aploop)
                LD   (BattleApprCurThr), HL
                LD   A, (BattleApprActCell)           ; dist = GetDistance(active, enemy)
                LD   D, A
                LD   A, (BattleThrECell)
                LD   E, A
                CALL Battle_GetDistance                ; A = hexDist (центр-в-центр)
                OR   A
                JR   Z, .apnext                       ; совпадение клеток → пропуск
                DEC  A                                 ; dist до соседней с врагом клетки = hexDist−1
                JR   NZ, .apd1                         ;   (findNearestCellNextToUnit — путь к клетке рядом)
                INC  A                                 ; клемп ≥1 (враг вплотную)
.apd1:          LD   (BattleApprCurDist), A
                LD   A, (BattleApprPass)               ; проход 1 → non-evader тест
                CP   1
                JR   NZ, .apeval
                LD   A, (BattleThrEShots)
                OR   A
                JR   NZ, .apeval                      ; стрелок → non-evader
                LD   A, (BattleThrESpd)
                OR   A
                JR   Z, .apeval                       ; speed 0 → non-evader
                LD   HL, BattleApprActSpd
                CP   (HL)
                JR   NC, .apnext                      ; speed>=active → уклонится → пропуск (проход1)
.apeval:        LD   A, (BattleApprBestTgt)            ; сравнить threat/dist (cross-mult)
                CP   #FF
                JR   Z, .aptake                       ; первый кандидат
                LD   HL, (BattleApprCurThr)            ; P1 = curThr × bestDist
                LD   A, (BattleApprBestDist)
                CALL Battle_Mul16x8
                LD   HL, BattleMulBuf
                LD   DE, BattleMulBuf2
                LD   BC, 3
                LDIR                                  ; P1 → BattleMulBuf2
                LD   HL, (BattleApprBestThr)           ; P2 = bestThr × curDist
                LD   A, (BattleApprCurDist)
                CALL Battle_Mul16x8
                LD   A, (BattleMulBuf2 + 2)            ; P1 > P2 ? (24-бит без знака, со старшего)
                LD   HL, BattleMulBuf + 2
                CP   (HL)
                JR   C, .apnext                       ; P1.hi < P2.hi → не лучше
                JR   NZ, .aptake                      ; P1.hi > P2.hi → лучше
                LD   A, (BattleMulBuf2 + 1)
                DEC  HL
                CP   (HL)
                JR   C, .apnext
                JR   NZ, .aptake
                LD   A, (BattleMulBuf2)
                DEC  HL
                CP   (HL)
                JR   C, .apnext
                JR   Z, .apnext                       ; равно → оставить первого
.aptake:        LD   A, (BattleApprIdx)                ; новый лучший (индекс из scratch)
                LD   (BattleApprBestTgt), A
                LD   HL, (BattleApprCurThr)
                LD   (BattleApprBestThr), HL
                LD   A, (BattleApprCurDist)
                LD   (BattleApprBestDist), A
.apnext:        LD   A, (BattleApprIdx)                ; C испорчен Mul/LDIR/EvalThreat — восстановить
                LD   C, A
                INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JP   C, .aploop
                LD   A, (BattleApprBestTgt)            ; проход 1 дал результат?
                CP   #FF
                JR   NZ, .apdone
                LD   A, (BattleApprPass)
                CP   1
                JR   NZ, .apdone                      ; проход 2 тоже пуст → #FF
                LD   A, 2
                LD   (BattleApprPass), A
                JP   .appass
.apdone:        LD   A, (BattleApprBestTgt)
                LD   (BattleTargetUnit), A
                RET

; --- Мелкие хелперы кэшей (индексация, БЕЗ пейджинга) ---
; A=idx, HL=base → HL=base+idx. Портит A,F.
Battle_IdxByte: ADD  A, L
                LD   L, A
                RET  NC
                INC  H
                RET
; A=idx → DE = BattleThreatCache[idx] (16-бит). Портит A,F,HL.
Battle_ThreatCacheGet:
                ADD  A, A                            ; idx*2
                LD   L, A
                LD   H, 0
                LD   DE, BattleThreatCache
                ADD  HL, DE
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                RET
; A=Ecell → A=1 если (BattlePVCurCell) среди BattleAdjTab[Ecell*6], иначе 0. Портит A,BC,DE,HL.
Battle_CellAdjToCur:
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL                          ; 2c
                ADD  HL, HL                          ; 4c
                ADD  HL, DE                          ; 5c
                ADD  HL, DE                          ; 6c
                LD   DE, BattleAdjTab
                ADD  HL, DE                          ; &adj[Ecell*6]
                LD   A, (BattlePVCurCell)
                LD   B, 6
.caloop:        CP   (HL)
                JR   Z, .cayes
                INC  HL
                DJNZ .caloop
                XOR  A
                RET
.cayes:         LD   A, 1
                RET

; ★Battle_AIBuildThreatCache — один раз за ход: заполнить кэши enemy/archer/cell/threat по всем юнитам.
; ВРАГИ: threat=evaluateThreatForUnit, archer=shots>0. СВОИ ЖИВЫЕ: archer=shots>0 (для Defense),
; ThreatCache = ИХ GetStrength (str_fp×count, клемп 16 бит) — для archerValue прикрытия.
; ВСЕ EvalThreat/MonsterStats_Read (пейджинг #91) здесь; далее PosValue/BestOutcome/Defense — без пейджинга.
; Портит всё. (side активного → BattleAISide.)
Battle_AIBuildThreatCache:
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                LD   A, (HL)
                LD   (BattleAISide), A                ; сторона активного
                LD   C, 0
.btloop:        LD   A, C
                LD   (BattlePVIdx), A                 ; сохранить индекс (EvalThreat клоббит BC)
                CALL Battle_UnitAddr                  ; HL=&type[C]
                INC  HL
                LD   B, (HL)                          ; B=cell
                LD   A, C                             ; cellCache[C]=cell
                LD   HL, BattleCellCache
                CALL Battle_IdxByte
                LD   (HL), B
                LD   A, C                             ; side
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                LD   A, (HL)
                LD   HL, BattleAISide
                CP   (HL)
                JR   Z, .btno                         ; своя сторона → не враг
                LD   A, C                             ; count (жив?)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   A, D
                OR   E
                JR   Z, .btno                         ; мёртв → не враг
                CALL Battle_EvalThreat                ; HL=threat (C=enemyIdx вход), пишет BattleThrEShots
                LD   A, (MonsterStatBuf + 6)          ; буфер после EvalThreat = статы ВРАГА → speed
                LD   B, A
                LD   A, (BattlePVIdx)
                PUSH HL
                LD   HL, BattleSpdCache
                CALL Battle_IdxByte
                LD   (HL), B                          ; SpdCache[враг]
                POP  HL
                LD   A, (BattlePVIdx)                 ; threatCache[C]=HL
                LD   C, A
                PUSH HL
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, BattleThreatCache
                ADD  HL, DE
                POP  DE                               ; DE=threat
                LD   (HL), E
                INC  HL
                LD   (HL), D
                LD   A, C                             ; enemyCache[C]=1
                LD   HL, BattleEnemyCache
                CALL Battle_IdxByte
                LD   (HL), 1
                LD   A, (BattleThrEShots)             ; archerCache[C]=(shots>0)
                OR   A
                JR   Z, .btam
                LD   A, 1
                JR   .btaw
.btam:          XOR  A
.btaw:          LD   B, A
                LD   A, C
                LD   HL, BattleArcherCache
                CALL Battle_IdxByte
                LD   (HL), B
                JP   .btnext
.btno:          LD   A, (BattlePVIdx)                 ; не враг: enemy=0
                LD   C, A
                LD   HL, BattleEnemyCache
                CALL Battle_IdxByte
                LD   (HL), 0
                LD   A, C                             ; жив? (свой живой → archer+strength для Defense)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)                          ; DE=count
                LD   A, D
                OR   E
                JR   NZ, .btself                      ; живой свой
                LD   A, (BattlePVIdx)                 ; мёртвый: archer=0, threat=0
                LD   C, A
                LD   HL, BattleArcherCache
                CALL Battle_IdxByte
                LD   (HL), 0
                LD   A, C
                ADD  A, A
                LD   L, A
                LD   H, 0
                LD   DE, BattleThreatCache
                ADD  HL, DE
                LD   (HL), 0
                INC  HL
                LD   (HL), 0
                JR   .btnext
.btself:        PUSH DE                               ; живой СВОЙ: count
                LD   A, (BattlePVIdx)                 ; id (type+1)
                CALL Battle_UnitAddr
                LD   A, (HL)
                CALL Battle_TypeToMonId  ; type→id
                LD   B, A
                CALL MonsterStats_Read                ; → str_fp(+8/9), speed(+6)
                LD   A, (BattlePVIdx)                 ; archerCache = ОСТАТОК шотов>0 (не статы)
                LD   HL, BattleUnitShots
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JR   Z, .btsm
                LD   A, 1
.btsm:          LD   B, A
                LD   A, (BattlePVIdx)
                LD   HL, BattleArcherCache
                CALL Battle_IdxByte
                LD   (HL), B
                LD   A, (MonsterStatBuf + 6)          ; SpdCache[свой]
                LD   B, A
                LD   A, (BattlePVIdx)
                LD   HL, BattleSpdCache
                CALL Battle_IdxByte
                LD   (HL), B
                POP  DE                               ; strength24 = str_fp × count
                LD   HL, (MonsterStatBuf + 8)
                CALL Battle_Mul16x16_24
                LD   A, (BattleMulBuf + 2)            ; клемп до 16 бит
                OR   A
                JR   Z, .btsl
                LD   HL, #FFFF
                JR   .btsw
.btsl:          LD   HL, (BattleMulBuf)
.btsw:          EX   DE, HL                           ; DE = strength16
                LD   A, (BattlePVIdx)                 ; ThreatCache[self] = strength16
                ADD  A, A
                LD   L, A
                LD   H, 0
                PUSH DE
                LD   DE, BattleThreatCache
                ADD  HL, DE
                POP  DE
                LD   (HL), E
                INC  HL
                LD   (HL), D
.btnext:        LD   A, (BattlePVIdx)
                LD   C, A
                INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JP   C, .btloop
                RET

; ★Battle_AIPosValue — positionValue клетки (evaluatePotentialAttackPositions): max(угрозы соседних
; МИЛИ-врагов) + Σ(угрозы соседних СТРЕЛКОВ). Только кэши, без пейджинга. IN: A=cell. OUT: HL=posVal (cap FFFF).
Battle_AIPosValue:
                LD   (BattlePVCurCell), A
                LD   HL, 0
                LD   (BattlePVMax), HL                ; maxMelee=0
                LD   (BattlePVArch), HL               ; sumArcher=0
                LD   C, 0
.pvloop:        LD   A, C
                LD   HL, BattleEnemyCache
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JR   Z, .pvnext                       ; не враг
                LD   A, C                             ; Ecell → сосед ли PVCurCell?
                LD   HL, BattleCellCache
                CALL Battle_IdxByte
                LD   A, (HL)
                PUSH BC
                CALL Battle_CellAdjToCur              ; A=1 если сосед
                POP  BC
                OR   A
                JR   Z, .pvnext
                LD   A, C                             ; t = threatCache[C]
                PUSH BC
                CALL Battle_ThreatCacheGet            ; DE=t
                POP  BC
                LD   A, C                             ; стрелок?
                LD   HL, BattleArcherCache
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JR   Z, .pvmelee
                LD   HL, (BattlePVArch)               ; sumArcher += t (cap FFFF)
                ADD  HL, DE
                JR   NC, .pvarok
                LD   HL, #FFFF
.pvarok:        LD   (BattlePVArch), HL
                JR   .pvnext
.pvmelee:       LD   HL, (BattlePVMax)                ; maxMelee = max(maxMelee, t)
                LD   A, L
                SUB  E
                LD   A, H
                SBC  A, D                             ; CF если maxMelee < t
                JR   NC, .pvnext
                LD   (BattlePVMax), DE
.pvnext:        INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JR   C, .pvloop
                LD   HL, (BattlePVMax)                ; posVal = maxMelee + sumArcher (cap FFFF)
                LD   DE, (BattlePVArch)
                ADD  HL, DE
                RET  NC
                LD   HL, #FFFF
                RET

; ★Battle_AIMeleeBestOutcome — meleeUnitOffense §1 (getMeleeBestOutcome): лучшая цель, атакуемая В
; ЭТОТ ХОД (клетка рядом с врагом, достижимая). Критерий IsOutcomeImproved: positionValue → threat
; (canAttackImmediately одинаково=1 у всех кандидатов). Предпосылка: ComputeReachable + BuildThreatCache.
; OUT: BattleTargetUnit + BattleMoveDestCell; A=1 если найдена, A=0 иначе. Портит всё.
Battle_AIMeleeBestOutcome:
                XOR  A
                LD   (BattleMBOFound), A
                LD   A, #FF
                LD   (BattleMBOTgt), A
                LD   (BattleMBOCell), A
                LD   C, 0                             ; C = индекс врага (внешний)
.mboEloop:      LD   A, C
                LD   (BattleMBOEIdx), A
                LD   HL, BattleEnemyCache
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JP   Z, .mboEnext                     ; не враг
                LD   A, (BattleMBOEIdx)               ; фильтр маски врагов (Defense: только блокирующие)
                LD   B, A
                INC  B
                LD   A, (BattleMBOEnMask)
.mbomsk:        RRCA                                  ; бит C → carry
                DJNZ .mbomsk
                JP   NC, .mboEnext                    ; враг вне маски
                LD   A, (BattleMBOEIdx)               ; HL=&adj[Ecell*6]
                LD   HL, BattleCellCache
                CALL Battle_IdxByte
                LD   A, (HL)
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
                LD   B, 6                             ; 6 соседних клеток врага
.mboKloop:      LD   A, (HL)
                CP   #FF
                JP   Z, .mboKnext                     ; нет клетки
                LD   (BattleMBOCurCell), A            ; клетка-кандидат
                PUSH HL
                PUSH BC
                LD   C, A                             ; достижима в этот ход? BattleReach[C]!=0
                LD   B, 0
                LD   HL, BattleReach
                ADD  HL, BC
                LD   A, (HL)
                OR   A
                JR   Z, .mboKpop                      ; недостижима
                LD   A, (BattleMBOZoneOnly)           ; фильтр зоны (Defense §2): клетка в СВОЕЙ половине?
                OR   A
                JR   Z, .mbozok
                LD   A, (BattleMBOCurCell)
                CALL Battle_CellRowCol                ; A=x
                LD   B, A
                LD   A, (BattleAISide)
                OR   A
                LD   A, B
                JR   NZ, .mboz1
                CP   5                                ; side0: x≤4
                JR   NC, .mboKpop
                JR   .mbozok
.mboz1:         CP   6                                ; side1: x≥6
                JR   C, .mboKpop
.mbozok:
                LD   A, (BattleMBOCurCell)            ; positionValue(cell)
                CALL Battle_AIPosValue                ; HL=pv
                LD   (BattleMBOCurPV), HL
                LD   A, (BattleMBOEIdx)               ; threat кандидата-врага
                CALL Battle_ThreatCacheGet            ; DE=thr
                LD   (BattleMBOCurThr), DE
                LD   A, (BattleMBOFound)              ; первый? → взять
                OR   A
                JR   Z, .mbotake
                LD   HL, (BattleMBOCurPV)             ; pv > bestPV?
                LD   DE, (BattleMBOPV)
                OR   A
                SBC  HL, DE
                JR   Z, .mbopveq
                JR   C, .mboKpop                      ; pv < bestPV → пропуск
                JR   .mbotake                         ; pv > bestPV → взять
.mbopveq:       LD   HL, (BattleMBOCurThr)            ; равный pv → по threat
                LD   DE, (BattleMBOThr)
                OR   A
                SBC  HL, DE
                JR   C, .mboKpop                      ; thr < best → пропуск
                JR   Z, .mboKpop                      ; равно → оставить первого
.mbotake:       LD   HL, (BattleMBOCurPV)
                LD   (BattleMBOPV), HL
                LD   HL, (BattleMBOCurThr)
                LD   (BattleMBOThr), HL
                LD   A, 1
                LD   (BattleMBOFound), A
                LD   A, (BattleMBOEIdx)
                LD   (BattleMBOTgt), A
                LD   A, (BattleMBOCurCell)
                LD   (BattleMBOCell), A
.mboKpop:       POP  BC
                POP  HL
.mboKnext:      INC  HL
                DEC  B                                ; (DJNZ вне диапазона)
                JP   NZ, .mboKloop
.mboEnext:      LD   A, (BattleMBOEIdx)
                LD   C, A
                INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JP   C, .mboEloop
                LD   A, #FF                           ; сброс фильтров в дефолт (одноразовые)
                LD   (BattleMBOEnMask), A
                XOR  A
                LD   (BattleMBOZoneOnly), A
                LD   A, (BattleMBOTgt)
                LD   (BattleTargetUnit), A
                LD   A, (BattleMBOCell)
                LD   (BattleMoveDestCell), A
                LD   A, (BattleMBOFound)
                RET

; A=cell → A=min дистанции по BattleReach среди 6 соседей (пустых/достижимых): Reach 1..spd=дист,
; #FF(origin)=0; недостижимо → A=#FF. (findNearestCellNextToUnit по уже посчитанному флуду.) Портит всё.
Battle_MinReachAdj:
                LD   L, A                             ; &adj[cell*6]
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE
                ADD  HL, DE
                LD   DE, BattleAdjTab
                ADD  HL, DE
                LD   C, #FF                           ; C = min (старт: недостижимо)
                LD   B, 6
.mraloop:       LD   A, (HL)
                CP   #FF
                JR   Z, .mranext                      ; нет клетки
                PUSH HL
                PUSH BC
                LD   L, A                             ; Reach[c]
                LD   H, 0
                LD   BC, BattleReach
                ADD  HL, BC
                LD   A, (HL)
                POP  BC
                POP  HL
                OR   A
                JR   Z, .mranext                      ; недостижима
                CP   #FF                              ; origin → дистанция 0
                JR   NZ, .mrad
                XOR  A
.mrad:          CP   C                                ; A < min?
                JR   NC, .mranext
                LD   C, A
.mranext:       INC  HL
                DJNZ .mraloop
                LD   A, C
                RET

; ★Battle_AIMeleeDefense — meleeUnitDefense (ai_battle.cpp:1708) для 1-клеточных юнитов без замка:
; §1 прикрыть своих СТРЕЛКОВ (приоритетная клетка рядом по направлениям стороны) / атаковать
; врагов, БЛОКИРУЮЩИХ их (dist=1); выбор стрелка = max archerValue = GetStrength − dist×(myShoot/15);
; гейт: есть немедленная цель И dist>speed×2 → стрелка игнорить. §2 иначе: лучшая цель, атакуемая
; ИЗ СВОЕЙ половины (MBO ZoneOnly). Предпосылки: ComputeReachable + BuildThreatCache + AIAnalyze.
; OUT: A=0 SKIP хода; A=1 MOVE на BattleMoveDestCell; A=2 ATTACK BattleTargetUnit (dest=клетка атаки).
; Допущения (зафиксированы в Docs): «позиция-для-будущей-атаки» BestAttackOutcome не моделируется;
; avoidStacking=false (у Knight нет AREA_SHOT-врагов); wide-прикрытие — с расами wide; value клемп ≥0.
Battle_AIMeleeDefense:
                CALL Battle_AIMeleeBestOutcome        ; isAnyEnemyCanBeAttackedImmediately (полный MBO)
                LD   (BattleDefAnyImm), A             ;   Target/Dest ниже перезапишутся
                LD   A, (BattleActiveUnit)            ; speed активного (гейт speed×2)
                CALL Battle_UnitAddr
                LD   A, (HL)
                CALL Battle_TypeToMonId  ; type→id
                LD   B, A
                CALL MonsterStats_Read
                LD   A, (MonsterStatBuf + 6)
                LD   (BattleDefActSpd), A
                LD   A, (BattleAnlMyShoot + 2)        ; penalty16 = min(myShoot,FFFF)/15
                OR   A
                JR   Z, .dfp1
                LD   HL, #FFFF
                JR   .dfp2
.dfp1:          LD   HL, (BattleAnlMyShoot)
.dfp2:          LD   C, 15
                CALL Battle_Div16by8
                LD   (BattleDefPen), HL
                LD   A, #FF                           ; лучший стрелок = нет
                LD   (BattleDefBestF), A
                LD   HL, 0
                LD   (BattleDefBestVal), HL
                LD   C, 0
                ; ======== цикл по своим живым стрелкам F ========
.dfF:           LD   A, C
                LD   (BattleDefFIdx), A
                LD   A, (BattleActiveUnit)            ; не сам активный
                CP   C
                JP   Z, .dfFnext
                LD   A, C                             ; свой? (EnemyCache==0)
                LD   HL, BattleEnemyCache
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JP   NZ, .dfFnext
                LD   A, C                             ; стрелок? (мёртвым кэш пишет 0 → отсев)
                LD   HL, BattleArcherCache
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JP   Z, .dfFnext
                LD   A, C
                LD   HL, BattleCellCache
                CALL Battle_IdxByte
                LD   A, (HL)
                LD   (BattleDefFCell), A
                ; ---- cover: первая приоритетная достижимая клетка рядом с F ----
                LD   L, A                             ; adjBase = &BattleAdjTab[Fcell*6]
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL
                ADD  HL, HL
                ADD  HL, DE
                ADD  HL, DE
                LD   DE, BattleAdjTab
                ADD  HL, DE
                LD   (BattleDefAdjBase), HL
                LD   A, #FF
                LD   (BattleDefCover), A
                LD   A, (BattleAISide)                ; таблица приоритета направлений стороны
                OR   A
                LD   DE, BattleDefPrioS0
                JR   Z, .dfk0
                LD   DE, BattleDefPrioS1
.dfk0:          LD   A, 6
                LD   (BattleDefK), A
.dfKloop:       LD   A, (DE)                          ; dir → c=adjBase[dir]
                PUSH DE
                LD   HL, (BattleDefAdjBase)
                ADD  A, L
                LD   L, A
                JR   NC, .dfk1
                INC  H
.dfk1:          LD   A, (HL)                          ; c
                CP   #FF
                JR   Z, .dfkNext                      ; клетки нет
                LD   L, A                             ; Reach[c]: ≠0 = достижима (пустая/origin — флуд
                LD   H, 0                             ;   не заходит в занятые, origin=#FF)
                PUSH AF
                LD   DE, BattleReach
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .dfkPop                       ; недостижима
                CP   #FF                              ; origin → дистанция 0
                JR   NZ, .dfk2
                XOR  A
.dfk2:          LD   (BattleDefCoverD), A             ; дистанция
                POP  AF                               ; A=c
                LD   (BattleDefCover), A
                POP  DE
                JR   .dfCoverDone                     ; ПЕРВАЯ по приоритету — стоп
.dfkPop:        POP  AF
.dfkNext:       POP  DE
                INC  DE
                LD   HL, BattleDefK
                DEC  (HL)
                JR   NZ, .dfKloop
.dfCoverDone:   ; ---- маска врагов, блокирующих F (GetDistance(F,E)==1) ----
                XOR  A
                LD   (BattleDefMask), A
                LD   C, 0
.dfMloop:       LD   A, C
                LD   (BattleDefEIdx), A
                LD   HL, BattleEnemyCache
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JR   Z, .dfMnext                      ; не живой враг
                LD   A, C
                LD   HL, BattleCellCache
                CALL Battle_IdxByte
                LD   A, (HL)
                LD   E, A                             ; E=Ecell
                LD   A, (BattleDefFCell)
                LD   D, A                             ; D=Fcell
                CALL Battle_GetDistance               ; A=dist (портит BC/DE/HL)
                CP   1
                JR   NZ, .dfMnext
                LD   A, (BattleDefEIdx)               ; mask |= bit(E)
                LD   B, A
                INC  B
                XOR  A
                SCF
.dfMbit:        RLA                                   ; A = 1<<E
                DJNZ .dfMbit
                LD   HL, BattleDefMask
                OR   (HL)
                LD   (HL), A
.dfMnext:       LD   A, (BattleDefEIdx)
                LD   C, A
                INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JR   C, .dfMloop
                ; ---- отсев: нет cover И нет блокирующих → игнор стрелка ----
                LD   A, (BattleDefCover)
                CP   #FF
                JR   NZ, .dfHasAny
                LD   A, (BattleDefMask)
                OR   A
                JP   Z, .dfFnext
.dfHasAny:      ; ---- dist = min(coverDist, min по блокирующим reach-до-соседа) ----
                LD   A, (BattleDefCover)
                CP   #FF
                LD   A, #FF
                JR   Z, .dfd0
                LD   A, (BattleDefCoverD)
.dfd0:          LD   (BattleDefDist), A
                LD   C, 0
.dfDloop:       LD   A, (BattleDefMask)               ; E в маске?
                LD   B, C
                INC  B
.dfDbit:        RRCA
                DJNZ .dfDbit
                JR   NC, .dfDnext
                LD   A, C
                LD   (BattleDefEIdx), A
                LD   HL, BattleCellCache              ; dE = min reach соседей Ecell
                CALL Battle_IdxByte
                LD   A, (HL)
                CALL Battle_MinReachAdj               ; A=dE (#FF недостижимо; портит BC)
                LD   HL, BattleDefDist
                CP   (HL)
                JR   NC, .dfDrest
                LD   (HL), A                          ; новый min
.dfDrest:       LD   A, (BattleDefEIdx)
                LD   C, A
.dfDnext:       INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JR   C, .dfDloop
                LD   A, (BattleDefDist)               ; всё недостижимо → игнор стрелка
                CP   #FF
                JP   Z, .dfFnext
                ; ---- гейт: AnyImm && dist > speed×2 → игнор ----
                LD   B, A                             ; B=dist
                LD   A, (BattleDefAnyImm)
                OR   A
                JR   Z, .dfVal
                LD   A, (BattleDefActSpd)
                ADD  A, A                             ; speed×2
                CP   B                                ; speed×2 < dist ⇔ dist > speed×2
                JP   C, .dfFnext
.dfVal:         ; ---- archerValue = strength16(F) − dist×pen (клемп ≥0) ----
                LD   HL, (BattleDefPen)
                LD   A, B                             ; dist
                CALL Battle_Mul16x8                   ; MulBuf = pen×dist (24-бит)
                LD   A, (BattleDefFIdx)
                CALL Battle_ThreatCacheGet            ; DE = strength16 (свои: сила)
                LD   A, (BattleMulBuf + 2)            ; штраф ≥ 2^16 → value 0
                OR   A
                JR   NZ, .dfv0
                LD   HL, (BattleMulBuf)
                EX   DE, HL                           ; HL=strength, DE=penalty
                OR   A
                SBC  HL, DE                           ; value = strength − penalty
                JR   NC, .dfvOK
.dfv0:          LD   HL, 0                            ; клемп 0
.dfvOK:         ; ---- max по value (строго >; первый при равенстве) ----
                LD   A, (BattleDefBestF)
                CP   #FF
                JR   Z, .dfTake                       ; первый кандидат
                PUSH HL
                LD   DE, (BattleDefBestVal)
                OR   A
                SBC  HL, DE
                POP  HL
                JP   C, .dfFnext                      ; value < best
                JP   Z, .dfFnext                      ; равно → первый
.dfTake:        LD   (BattleDefBestVal), HL
                LD   A, (BattleDefFIdx)
                LD   (BattleDefBestF), A
                LD   A, (BattleDefCover)
                LD   (BattleDefBestCover), A
                LD   A, (BattleDefMask)
                LD   (BattleDefBestMask), A
.dfFnext:       LD   A, (BattleDefFIdx)
                LD   C, A
                INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JP   C, .dfF
                ; ======== решение ========
                LD   A, (BattleDefBestF)
                CP   #FF
                JR   Z, .dfZone                       ; стрелков нет/не помочь → §2
                LD   A, (BattleDefBestMask)           ; блокирован? → атаковать лучшего блокирующего
                OR   A
                JR   Z, .dfGoCover
                LD   (BattleMBOEnMask), A             ; MBO только по блокирующим
                CALL Battle_AIMeleeBestOutcome
                OR   A
                JR   Z, .dfGoCover                    ; не достать → идти прикрывать
                LD   A, 2                             ; ATTACK (Target/Dest от MBO)
                RET
.dfGoCover:     LD   A, (BattleDefBestCover)          ; идти на cover-клетку
                CP   #FF
                JR   Z, .dfApproachF                  ; cover нет (блокирован полностью) → идти к стрелку
                LD   (BattleMoveDestCell), A
                LD   B, A
                LD   A, (BattleActiveUnit)            ; уже стоим на ней? → SKIP (держим прикрытие)
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)
                CP   B
                JR   Z, .dfSkip
                LD   A, 1                             ; MOVE
                RET
.dfApproachF:   LD   A, (BattleDefBestF)              ; двигаться к стрелку (приблизит к блокирующим)
                LD   (BattleTargetUnit), A
                CALL Battle_AIMoveToward              ; → BattleMoveDestCell (Reach уже посчитан)
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)
                LD   HL, BattleMoveDestCell
                CP   (HL)
                JR   Z, .dfSkip                       ; некуда → SKIP
                LD   A, 1                             ; MOVE
                RET
.dfZone:        LD   A, 1                             ; §2: лучшая цель, атакуемая ИЗ СВОЕЙ половины
                LD   (BattleMBOZoneOnly), A
                CALL Battle_AIMeleeBestOutcome
                OR   A
                JR   Z, .dfSkip                       ; никого из зоны не достать → стоять (SKIP)
                LD   A, 2                             ; ATTACK
                RET
.dfSkip:        XOR  A                                ; SKIP хода
                RET

; A=unitIdx (враг) → A=1 если он «в упоре» (hand fighting: живой юнит ДРУГОЙ стороны в соседях).
; Прямые чтения BattleUnitState (без пейджинга). Портит всё.
Battle_UnitHandFighting:
                LD   (BattleArcEIdx), A
                CALL Battle_UnitAddr                  ; его side и cell
                INC  HL
                LD   B, (HL)                          ; B=cell(E)
                INC  HL
                LD   A, (HL)
                LD   (BattleArcWeak), A               ; временно: side(E)
                LD   C, 0
.uhloop:        LD   A, (BattleArcEIdx)
                CP   C
                JR   Z, .uhnext                       ; сам
                PUSH BC
                LD   A, C
                CALL Battle_UnitAddr
                INC  HL
                LD   D, (HL)                          ; D=cell(j)
                INC  HL
                LD   A, (HL)                          ; side(j)
                LD   HL, BattleArcWeak
                CP   (HL)
                JR   Z, .uhpop                        ; та же сторона
                PUSH DE
                INC  HL                               ; жив? (state+3/+4 через UnitAddr заново — проще count)
                POP  DE
                LD   A, C                             ; count(j)
                PUSH DE
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                INC  HL
                LD   A, (HL)
                INC  HL
                OR   (HL)
                POP  DE
                JR   Z, .uhpop                        ; мёртв
                POP  BC
                PUSH BC
                LD   A, B                             ; dist(E, j)==1 ?
                PUSH DE
                POP  HL                               ; D=cell(j) → в D остаётся
                LD   E, D
                LD   D, A                             ; D=cell(E), E=cell(j)
                CALL Battle_GetDistance
                CP   1
                JR   NZ, .uhpop
                POP  BC                               ; сосед другой стороны → в упоре
                LD   A, 1
                RET
.uhpop:         POP  BC
.uhnext:        INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JR   C, .uhloop
                XOR  A
                RET

; Враг E «слабый» для угрозы издали? (archerDecision: стрелок-не-в-упоре ИЛИ speed==0 метят
; только соседство). IN A=E. OUT A=1 слабый / 0 полноценный. Портит всё.
Battle_AIArcEnemyWeak:
                LD   (BattleArcEIdx), A
                LD   HL, BattleSpdCache               ; speed==0 → слабый
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JR   Z, .ewyes
                LD   A, (BattleArcEIdx)               ; стрелок?
                LD   HL, BattleArcherCache
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JR   Z, .ewno                         ; мили с ходом → полноценный
                LD   A, (BattleArcEIdx)               ; стрелок: в упоре → дерётся → полноценный
                CALL Battle_UnitHandFighting
                OR   A
                JR   NZ, .ewno
.ewyes:         LD   A, 1
                RET
.ewno:          XOR  A
                RET

; Маска врагов, УГРОЖАЮЩИХ клетке (BattleArcCandC): сосед → угроза; слабый враг издали — нет;
; иначе флуд за врага (ReachEn, активный «снят») → сосед клетки достижим → угроза. Портит всё.
Battle_AIArcThreatMaskAt:
                XOR  A
                LD   (BattleArcMask), A
                LD   C, 0
.tmloop:        LD   A, C
                LD   (BattleArcEIdx), A
                LD   HL, BattleEnemyCache
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JP   Z, .tmnext                       ; не живой враг
                LD   A, (BattleArcEIdx)               ; dist(cand, E)==1 → угроза
                LD   HL, BattleCellCache
                CALL Battle_IdxByte
                LD   A, (HL)
                LD   E, A
                LD   A, (BattleArcCandC)
                LD   D, A
                CALL Battle_GetDistance
                CP   1
                JR   Z, .tmmark
                LD   A, (BattleArcEIdx)               ; слабый → издали не угрожает
                CALL Battle_AIArcEnemyWeak
                OR   A
                JR   NZ, .tmnext
                LD   A, (BattleArcEIdx)               ; флуд за врага (активный снят)
                LD   (BattleReachUnit), A
                LD   HL, BattleReachEn
                LD   (BattleReachBufPtr), HL
                LD   A, (BattleActiveUnit)
                LD   (BattleFindIgnore), A
                CALL Battle_ComputeReachEx            ; (сбрасывает ignore; портит всё)
                LD   A, (BattleArcCandC)              ; соседи cand: достижимы врагом?
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
.tmadj:         LD   A, (HL)
                CP   #FF
                JR   Z, .tmadjn
                PUSH HL
                LD   L, A
                LD   H, 0
                LD   DE, BattleReachEn
                ADD  HL, DE
                LD   A, (HL)
                POP  HL
                OR   A
                JR   NZ, .tmmark                      ; враг дойдёт до соседа → угроза
.tmadjn:        INC  HL
                DJNZ .tmadj
                JR   .tmnext                          ; не достижимо → не угрожает
.tmmark:        LD   A, (BattleArcEIdx)               ; mask |= bit(E)
                LD   B, A
                INC  B
                XOR  A
                SCF
.tmbit:         RLA
                DJNZ .tmbit
                LD   HL, BattleArcMask
                OR   (HL)
                LD   (HL), A
.tmnext:        LD   A, (BattleArcEIdx)
                LD   C, A
                INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JP   C, .tmloop
                LD   A, (BattleArcMask)
                RET

; Пометить в BattleReach бит7 = «клетка под угрозой» (для кандидатов ретрита 1..spd; origin/#FF
; не трогаем). Слабый враг метит только своих соседей; полноценный — флуд (ReachEn) и клетки,
; у которых сосед достижим врагом (включая клетку врага: origin=#FF≠0). Портит всё.
Battle_AIArcMarkDanger:
                LD   C, 0
.mdloop:        LD   A, C
                LD   (BattleArcEIdx), A
                LD   HL, BattleEnemyCache
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JP   Z, .mdnext
                LD   A, (BattleArcEIdx)
                CALL Battle_AIArcEnemyWeak
                OR   A
                JR   Z, .mdfull
                ; слабый: пометить соседей клетки врага
                LD   A, (BattleArcEIdx)
                LD   HL, BattleCellCache
                CALL Battle_IdxByte
                LD   A, (HL)
                LD   L, A                             ; &adj[Ecell*6]
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
.mdwadj:        LD   A, (HL)
                CP   #FF
                JR   Z, .mdwn
                PUSH HL
                LD   L, A                             ; Reach[c] ∈ 1..spd → |= #80
                LD   H, 0
                LD   DE, BattleReach
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .mdwp
                CP   #FF
                JR   Z, .mdwp
                BIT  7, A
                JR   NZ, .mdwp
                SET  7, (HL)
.mdwp:          POP  HL
.mdwn:          INC  HL
                DJNZ .mdwadj
                JP   .mdnext
.mdfull:        LD   A, (BattleArcEIdx)               ; полноценный: флуд за врага (активный снят)
                LD   (BattleReachUnit), A
                LD   HL, BattleReachEn
                LD   (BattleReachBufPtr), HL
                LD   A, (BattleActiveUnit)
                LD   (BattleFindIgnore), A
                CALL Battle_ComputeReachEx
                LD   C, 0                             ; все клетки-кандидаты
.mdcell:        LD   A, C
                LD   L, A
                LD   H, 0
                LD   DE, BattleReach
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .mdcn                         ; не кандидат
                CP   #FF
                JR   Z, .mdcn                         ; origin
                BIT  7, A
                JR   NZ, .mdcn                        ; уже помечена
                PUSH HL                               ; соседи c: ReachEn≠0 → опасна
                LD   A, C
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
.mdca:          LD   A, (HL)
                CP   #FF
                JR   Z, .mdcan
                PUSH HL
                LD   L, A
                LD   H, 0
                LD   DE, BattleReachEn
                ADD  HL, DE
                LD   A, (HL)
                POP  HL
                OR   A
                JR   NZ, .mdmark
.mdcan:         INC  HL
                DJNZ .mdca
                POP  HL
                JR   .mdcn
.mdmark:        POP  HL                               ; HL = &Reach[c]
                SET  7, (HL)
.mdcn:          INC  C
                LD   A, C
                CP   99
                JR   C, .mdcell
.mdnext:        LD   A, (BattleArcEIdx)
                LD   C, A
                INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JP   C, .mdloop
                RET

; HL = (BattleThrCnt) × A (повт.слож., cap FFFF). Портит A,B,DE,HL. (копия .etcntmul для archer-мили)
Battle_CntMulA:
                LD   B, A
                LD   DE, (BattleThrCnt)
                LD   HL, 0
                LD   A, B
                OR   A
                RET  Z
.cml:           ADD  HL, DE
                JR   C, .cmcap
                DJNZ .cml
                RET
.cmcap:         LD   HL, #FFFF
                RET

; Ветка B archerDecision: блокированный стрелок дерётся в мили — цель = сосед с max
; (potDmg(я→E со штрафом ÷2) − EstimateRetaliatoryDamage(E)). IN: BattleArcAdjMask.
; OUT: BattleTargetUnit. Портит всё. slot3-чтения ДО MonsterStats_Read (Phase A — как EvalThreat).
Battle_AIArcMeleePick:
                LD   A, #FF
                LD   (BattleArcBestE), A
                LD   HL, 0
                LD   (BattleArcBestDiff), HL
                LD   C, 0
.mpLoop:        LD   A, (BattleArcAdjMask)            ; E в маске?
                LD   B, C
                INC  B
.mpBit:         RRCA
                DJNZ .mpBit
                JP   NC, .mpNext
                LD   A, C
                LD   (BattleArcEIdx), A
                ; ---- Phase A (slot3): мой count, мой id; E id; E hp-пул; E retaliated ----
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                LD   A, (HL)
                CALL Battle_TypeToMonId  ; type→id
                LD   (BattleThrAId), A                ; мой id
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                INC  HL
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleThrCnt), DE               ; мой count
                LD   A, C
                CALL Battle_UnitAddr
                LD   A, (HL)
                CALL Battle_TypeToMonId  ; type→id
                LD   (BattleThrEId), A                ; id врага
                LD   A, C                             ; hp-пул врага
                CALL Battle_UnitHPAddr
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   (BattleArcPot), DE               ; временно: hpE (переложим ниже)
                PUSH DE                               ; hpE
                LD   A, C                             ; E уже отвечал в раунде?
                LD   HL, BattleRetaliated
                CALL Battle_IdxByte
                LD   A, (HL)
                PUSH AF                               ; retaliated-флаг
                ; ---- Phase B (пейджинг): статы ----
                LD   A, (BattleThrEId)                ; E: def, avg, maxHP
                LD   B, A
                CALL MonsterStats_Read
                LD   A, (MonsterStatBuf + 1)          ; def(E)
                LD   (BattleThrDef), A
                LD   A, (MonsterStatBuf + 2)          ; avgE=(dmin+dmax)/2
                LD   C, A
                LD   A, (MonsterStatBuf + 3)
                ADD  A, C
                SRL  A
                LD   (BattleArcWeak), A               ; временно: avgE
                LD   HL, (MonsterStatBuf + 4)         ; maxHP(E) 16-бит
                LD   (BattleAnlN2), HL                ; временно: maxHP(E)
                LD   A, (BattleThrAId)                ; Я: atk, dmin, dmax
                LD   B, A
                CALL MonsterStats_Read
                LD   A, (MonsterStatBuf)              ; r = myAtk − E.def
                LD   HL, BattleThrDef
                SUB  (HL)
                LD   (BattleThrR), A
                LD   A, (MonsterStatBuf + 2)          ; potMin=mod(count·dmin)
                CALL Battle_CntMulA
                LD   A, (BattleThrR)
                CALL Battle_ApplyDmgMod
                PUSH HL
                LD   A, (MonsterStatBuf + 3)          ; potMax=mod(count·dmax)
                CALL Battle_CntMulA
                LD   A, (BattleThrR)
                CALL Battle_ApplyDmgMod
                POP  DE
                ADD  HL, DE                           ; (potMin+potMax) — 17 бит через CF
                RR   H
                RR   L                                ; /2 = getPotentialDamage
                SRL  H
                RR   L                                ; ÷2 — мили-штраф стрелка (CalculateDamageUnit)
                LD   (BattleArcPot), HL               ; potDmg
                ; ---- ответка EstimateRetaliatoryDamage ----
                POP  AF                               ; retaliated-флаг
                POP  DE                               ; hpE
                OR   A
                JR   NZ, .mpRet0                      ; уже отвечал → 0
                LD   HL, (BattleArcPot)               ; potDmg ≥ hpE → весь отряд гибнет → 0
                EX   DE, HL                           ; HL=hpE, DE=pot
                OR   A
                SBC  HL, DE                           ; hpE − pot
                JR   Z, .mpRet0
                JR   C, .mpRet0
                ; unitsLeft = ceil((hpE−pot)/maxHP): повторное вычитание (точно, 16-бит)
                LD   DE, (BattleAnlN2)                ; maxHP(E)
                LD   B, 0                             ; unitsLeft (8-бит хватает: count ≤ 255 в скирмише; клемп ниже)
.mpDiv:         INC  B
                OR   A
                SBC  HL, DE
                JR   Z, .mpDivD                       ; ровно → ceil учтён (INC уже был)
                JR   NC, .mpDiv
.mpDivD:        ; ret = unitsLeft × avgE (cap FFFF)
                LD   A, (BattleArcWeak)               ; avgE
                LD   E, A
                LD   D, 0
                LD   HL, 0
                LD   A, B
                OR   A
                JR   Z, .mpRetW
.mpRMul:        ADD  HL, DE
                JR   C, .mpRCap
                DJNZ .mpRMul
                JR   .mpRetW
.mpRCap:        LD   HL, #FFFF
                JR   .mpRetW
.mpRet0:        LD   HL, 0
.mpRetW:        ; ---- diff = pot − ret → biased = #8000 + diff (насыщение в обе стороны) ----
                LD   (BattleAnlN1), HL                ; сохранить ret (нужен в отриц. ветке)
                EX   DE, HL                           ; DE = ret
                LD   HL, (BattleArcPot)               ; HL = pot
                OR   A
                SBC  HL, DE                           ; pot − ret
                JR   C, .mpNeg
                LD   A, H                             ; положит.: клемп diff ≤ 7FFF, biased=#8000+diff
                AND  #80
                JR   Z, .mpPosOk
                LD   HL, #7FFF
.mpPosOk:       LD   A, H
                ADD  A, #80
                LD   H, A
                JR   .mpCmp
.mpNeg:         LD   HL, (BattleAnlN1)                ; отрицат.: biased = #8000 − (ret−pot), клемп ≥0
                LD   DE, (BattleArcPot)
                OR   A
                SBC  HL, DE                           ; HL = ret − pot (>0)
                LD   A, H
                AND  #80
                JR   Z, .mpNegOk
                LD   HL, #7FFF                        ; клемп величины
.mpNegOk:       EX   DE, HL                           ; DE = ret−pot
                LD   HL, #8000
                OR   A
                SBC  HL, DE                           ; biased = #8000 − (ret−pot)
.mpCmp:         LD   DE, (BattleArcBestDiff)          ; строго больше → взять
                PUSH HL
                OR   A
                SBC  HL, DE
                POP  HL
                JR   C, .mpNext
                JR   Z, .mpNext
                LD   (BattleArcBestDiff), HL
                LD   A, (BattleArcEIdx)
                LD   (BattleArcBestE), A
.mpNext:        LD   A, (BattleArcEIdx)
                LD   C, A
                INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JP   C, .mpLoop
                LD   A, (BattleArcBestE)
                LD   (BattleTargetUnit), A
                RET

; ★Battle_AIArcherTurn — archerDecision (ai_battle.cpp:1172) для активного СТРЕЛКА:
; A) позиция под угрозой И от всех угрожающих реально уйти (spd==0 или spd+2<мой) И есть
;    безопасная достижимая клетка → ОТСТУПИТЬ на лучшую (dist до ближ. врага max; при равенстве
;    ближе к центру поля [клетка 49]); B) иначе блокирован (сосед-враг) → МИЛИ по лучшему
;    (potDmg÷2 − ответка); C) иначе СТРЕЛЯТЬ max-threat (BattleTargetUnit от FindTarget).
; (Летунов у Knight нет — ветку «не отступать от летунов» добавить с расами полёта. AREA_SHOT нет.)
Battle_AIArcherTurn:
                CALL Battle_ComputeReachable          ; свой флуд (юниты=препятствия)
                CALL Battle_AIBuildThreatCache        ; кэши enemy/cell/archer/spd
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitSpeed
                LD   (BattleArcMySpd), A
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)
                LD   (BattleArcCur), A
                ; ---- 1) угрозы текущей позиции ----
                LD   A, (BattleArcCur)
                LD   (BattleArcCandC), A
                CALL Battle_AIArcThreatMaskAt         ; A=маска
                LD   (BattleArcMask), A
                OR   A
                JP   Z, .arcShoot                     ; безопасно → стрелять
                ; ---- 2) worth retreat: ВСЕ угрожающие (spd==0 || spd+2 < mySpd) ----
                LD   C, 0
.arcW:          LD   A, (BattleArcMask)
                LD   B, C
                INC  B
.arcWb:         RRCA
                DJNZ .arcWb
                JR   NC, .arcWn
                LD   A, C
                LD   HL, BattleSpdCache
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JR   Z, .arcWn                        ; обездвижен → уйдём
                ADD  A, 2                             ; spd+2 < mySpd ?
                LD   B, A
                LD   A, (BattleArcMySpd)
                CP   B
                JP   C, .arcHand                      ; mySpd < spd+2 → не уйти → мили/стрелять
                JP   Z, .arcHand                      ; == → не уйти (строго <)
.arcWn:         INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JR   C, .arcW
                ; ---- 3) лучший безопасный кандидат ретрита ----
                CALL Battle_AIArcMarkDanger           ; бит7 Reach = опасно
                LD   A, #FF
                LD   (BattleArcBestC), A
                XOR  A
                LD   (BattleArcBestDN), A
                LD   C, 0
.arcC:          LD   A, C
                LD   (BattleArcCandC), A
                LD   L, A
                LD   H, 0
                LD   DE, BattleReach
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JP   Z, .arcCn                        ; недостижима
                CP   #FF
                JP   Z, .arcCn                        ; origin (стоять ≠ ретрит)
                BIT  7, A
                JP   NZ, .arcCn                       ; под угрозой
                ; dN = min dist(c, живые враги)
                LD   A, #FF
                LD   (BattleArcWeak), A               ; временно: min
                LD   B, 0
.arcD:          PUSH BC
                LD   A, B
                LD   HL, BattleEnemyCache
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JR   Z, .arcDn
                POP  BC
                PUSH BC
                LD   A, B
                LD   HL, BattleCellCache
                CALL Battle_IdxByte
                LD   A, (HL)
                LD   E, A
                LD   A, (BattleArcCandC)
                LD   D, A
                CALL Battle_GetDistance               ; A=dist
                LD   HL, BattleArcWeak
                CP   (HL)
                JR   NC, .arcDn
                LD   (HL), A
.arcDn:         POP  BC
                INC  B
                LD   A, B
                CP   BATTLE_UNIT_COUNT
                JR   C, .arcD
                ; сравнение (dN ↑; при равенстве dC ↓)
                LD   A, (BattleArcWeak)               ; dN кандидата
                LD   B, A
                LD   A, (BattleArcBestDN)
                CP   B                                ; best < dN → лучше
                JR   C, .arcTake
                JR   NZ, .arcCn                       ; best > dN → хуже
                ; равные dN → ближе к центру (49)
                LD   A, (BattleArcCandC)
                LD   D, A
                LD   E, 49
                PUSH BC
                CALL Battle_GetDistance
                POP  BC
                LD   C, A                             ; dC кандидата
                LD   A, (BattleArcBestDC)
                CP   C                                ; bestDC ≤ dC → хуже/равно
                JR   C, .arcCn
                JR   Z, .arcCn
.arcTake:       LD   A, (BattleArcCandC)
                LD   (BattleArcBestC), A
                LD   A, B
                LD   (BattleArcBestDN), A
                LD   A, (BattleArcCandC)              ; dC пересчитать (мог не считаться в ветке dN>)
                LD   D, A
                LD   E, 49
                CALL Battle_GetDistance
                LD   (BattleArcBestDC), A
.arcCn:         LD   A, (BattleArcCandC)
                LD   C, A
                INC  C
                LD   A, C
                CP   99
                JP   C, .arcC
                LD   A, (BattleArcBestC)              ; безопасная нашлась → ОТСТУПИТЬ
                CP   #FF
                JR   Z, .arcHand
                LD   (BattleMoveDestCell), A
                CALL Battle_StartMove                 ; движение без атаки
                XOR  A
                LD   (BattlePendAttack), A
                RET
.arcHand:       ; ---- B/C: блокирован? маска соседей ----
                XOR  A
                LD   (BattleArcAdjMask), A
                LD   C, 0
.arcH:          LD   A, C
                LD   HL, BattleEnemyCache
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JR   Z, .arcHn
                LD   A, C
                LD   HL, BattleCellCache
                CALL Battle_IdxByte
                LD   A, (HL)
                LD   E, A
                LD   A, (BattleArcCur)
                LD   D, A
                PUSH BC
                CALL Battle_GetDistance
                POP  BC
                CP   1
                JR   NZ, .arcHn
                LD   A, C                             ; adjMask |= bit(C)
                LD   B, A
                INC  B
                XOR  A
                SCF
.arcHb:         RLA
                DJNZ .arcHb
                LD   HL, BattleArcAdjMask
                OR   (HL)
                LD   (HL), A
.arcHn:         INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JR   C, .arcH
                LD   A, (BattleArcAdjMask)
                OR   A
                JR   Z, .arcShoot                     ; не блокирован → стрелять
                CALL Battle_AIArcMeleePick            ; B: мили по лучшему diff
                LD   A, (BattleTargetUnit)
                CP   #FF
                JR   Z, .arcShoot                     ; (страховка)
                CALL Battle_AttackAllowed             ; в упор: выставит мили-штраф ÷2 + ответку
                JP   Battle_StartAttack
.arcShoot:      CALL Battle_AIFindTarget              ; C: стрелять max evaluateThreatForUnit
                LD   A, (BattleTargetUnit)
                CP   #FF
                JP   Z, Battle_EndTurn                ; врагов нет (не должно)
                CALL Battle_AttackAllowed
                JP   Battle_StartAttack

; A=1 если активный — стрелок (ОСТАТОК шотов >0: Unit::isArchers=_shotsLeft), иначе A=0. Портит A,F,HL.
Battle_AIActiveIsArcher:
                LD   A, (BattleActiveUnit)
                LD   HL, BattleUnitShots
                CALL Battle_IdxByte
                LD   A, (HL)
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

; ★Battle_AICautiousStop — findOptimalPositionForSubsequentAttack (ai_battle.cpp:351): при
; _cautiousOffensive (у врага почти нет стрелков) мили-юнит идёт к цели, но останавливается на
; САМОМ ДАЛЬНЕМ шаге пути с МИНИМАЛЬНОЙ угрозой (не подставляться в конце хода). Путь =
; реконструкция по волне флуда (BattleReach: от dest к origin по убыванию волны — один из
; кратчайших, эквивалент GetPath). Угроза шага = Σ threatCache[e] по полноценным врагам
; (НЕ «слабый» AIArcEnemyWeak: свободный стрелок/speed0 — оригинал исключает стрелков не в
; упоре, speed0 отсеет isUnitAbleToApproachPosition), способным подойти: флуд за врага
; (ComputeReachEx, активный «снят» = UnitRemover) достигает СОСЕДА шага (вкл. клетку врага:
; origin=#FF≠0). Обход буфера от dest к origin со СТРОГИМ < ⇔ оригинальный обход от начала
; пути с ≤ (оба дают самый дальний глобальный минимум). Отступление: кандидаты только в
; пределах этого хода (оригинал оценивает весь многоходовый путь и обрезает по достижимости).
; IN: BattleMoveDestCell (от MoveToward), BattleReach (флуд активного).
; OUT: BattleMoveDestCell. Портит всё (в т.ч. BattleReachEn).
Battle_AICautiousStop:
                LD   A, (BattleActiveUnit)           ; dest==origin → идти некуда, выходим
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)
                LD   HL, BattleMoveDestCell
                CP   (HL)
                RET  Z
                ; --- реконструкция пути: c=dest; родитель = сосед с волной Reach[c]−1 ---
                XOR  A
                LD   (BattleCautLen), A
                LD   A, (HL)                         ; c = dest
.csrec:         LD   C, A                            ; C = c
                LD   A, (BattleCautLen)
                CP   12
                JR   NC, .cszero                     ; страховка переполнения буфера
                LD   HL, BattleCautPath              ; path[len] = c
                CALL Battle_IdxByte
                LD   (HL), C
                LD   HL, BattleCautLen
                INC  (HL)
                LD   A, C                            ; r = Reach[c] (1..spd)
                LD   L, A
                LD   H, 0
                LD   DE, BattleReach
                ADD  HL, DE
                LD   A, (HL)
                CP   1
                JR   Z, .cszero                      ; волна 1 → родитель = origin, путь готов
                DEC  A
                LD   B, A                            ; B = искомая волна r−1
                LD   A, C                            ; HL = &adj[c*6]
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
                LD   C, 6
.csadj:         LD   A, (HL)
                CP   #FF
                JR   Z, .csan
                LD   (BattleCautTmp), A              ; кандидат-родитель
                PUSH HL
                LD   L, A
                LD   H, 0
                LD   DE, BattleReach
                ADD  HL, DE
                LD   A, (HL)
                POP  HL
                CP   B
                JR   Z, .csstep                      ; волна r−1 → шаг к origin
.csan:          INC  HL
                DEC  C
                JR   NZ, .csadj
                JR   .cszero                         ; родителя нет (не должно) → путь как есть
.csstep:        LD   A, (BattleCautTmp)
                JR   .csrec
                ; --- обнулить threat-аккумулятор пути ---
.cszero:        LD   HL, BattleCautThr
                LD   B, 12*2
                XOR  A
.cszl:          LD   (HL), A
                INC  HL
                DJNZ .cszl
                ; --- по врагам: полноценный → флуд → добавить threat шагам с достижимым соседом ---
                XOR  A
.csen:          LD   (BattleCautEIdx), A
                LD   HL, BattleEnemyCache            ; живой враг?
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JR   Z, .csennext
                LD   A, (BattleCautEIdx)             ; «слабый» (свободный стрелок/speed0) → мимо
                CALL Battle_AIArcEnemyWeak
                OR   A
                JR   NZ, .csennext
                LD   A, (BattleCautEIdx)             ; флуд за врага, активный снят (UnitRemover)
                LD   (BattleReachUnit), A
                LD   HL, BattleReachEn
                LD   (BattleReachBufPtr), HL
                LD   A, (BattleActiveUnit)
                LD   (BattleFindIgnore), A
                CALL Battle_ComputeReachEx
                XOR  A                               ; шаги пути
.csst:          LD   (BattleCautStep), A
                LD   HL, BattleCautPath
                CALL Battle_IdxByte
                LD   A, (HL)                         ; клетка шага
                CALL Battle_CellAdjReachEn           ; сосед достижим врагом?
                OR   A
                JR   Z, .cssn
                LD   A, (BattleCautEIdx)             ; thr[step] += threatCache[e] (cap FFFF)
                CALL Battle_ThreatCacheGet           ; DE = threat врага
                LD   A, (BattleCautStep)
                ADD  A, A
                LD   HL, BattleCautThr
                CALL Battle_IdxByte                  ; HL = &thr[step].lo
                LD   C, (HL)
                INC  HL
                LD   B, (HL)                         ; BC = текущая сумма, HL = &hi
                PUSH HL
                LD   H, B
                LD   L, C
                ADD  HL, DE
                JR   NC, .csok
                LD   HL, #FFFF
.csok:          EX   DE, HL                          ; DE = новая сумма
                POP  HL                              ; HL = &hi
                LD   (HL), D
                DEC  HL
                LD   (HL), E
.cssn:          LD   A, (BattleCautStep)
                INC  A
                LD   HL, BattleCautLen
                CP   (HL)
                JR   C, .csst
.csennext:      LD   A, (BattleCautEIdx)
                INC  A
                CP   BATTLE_UNIT_COUNT
                JR   C, .csen
                ; --- выбор: от dest (path[0]) к origin, обновление при СТРОГО меньшей угрозе ---
                LD   A, (BattleCautPath)             ; старт: dest
                LD   (BattleMoveDestCell), A
                LD   HL, (BattleCautThr)             ; min = thr[0]
                LD   (BattleCautMin), HL
                LD   A, 1
.cspick:        LD   (BattleCautStep), A
                LD   HL, BattleCautLen
                CP   (HL)
                RET  NC                              ; все шаги пройдены
                ADD  A, A                            ; DE = thr[step]
                LD   HL, BattleCautThr
                CALL Battle_IdxByte
                LD   E, (HL)
                INC  HL
                LD   D, (HL)
                LD   HL, (BattleCautMin)             ; thr < min ? (min−thr: NC и NZ)
                OR   A
                SBC  HL, DE
                JR   C, .cspn
                JR   Z, .cspn
                LD   (BattleCautMin), DE             ; новый минимум → стоп-клетка ближе к origin
                LD   A, (BattleCautStep)
                LD   HL, BattleCautPath
                CALL Battle_IdxByte
                LD   A, (HL)
                LD   (BattleMoveDestCell), A
.cspn:          LD   A, (BattleCautStep)
                INC  A
                JR   .cspick

; A=cell → A=1 если у клетки есть сосед с ReachEn≠0 (вкл. origin врага #FF), иначе 0. Портит A,B,DE,HL.
Battle_CellAdjReachEn:
                LD   L, A
                LD   H, 0
                LD   D, H
                LD   E, L
                ADD  HL, HL                          ; 2c
                ADD  HL, HL                          ; 4c
                ADD  HL, DE                          ; 5c
                ADD  HL, DE                          ; 6c
                LD   DE, BattleAdjTab
                ADD  HL, DE                          ; &adj[cell*6]
                LD   B, 6
.carl:          LD   A, (HL)
                CP   #FF
                JR   Z, .carn
                PUSH HL
                LD   L, A
                LD   H, 0
                LD   DE, BattleReachEn
                ADD  HL, DE
                LD   A, (HL)
                POP  HL
                OR   A
                JR   NZ, .caryes
.carn:          INC  HL
                DJNZ .carl
                XOR  A
                RET
.caryes:        LD   A, 1
                RET

; ★Гекс-6 ДИСТАНЦИЯ (battle_board.cpp GetDistance) — фундамент AI/угрозы. x=i%11, y=i÷11;
; du=yB−yA; dv=(xB+yB÷2)−(xA+yA÷2); знаки du,dv ОДИНАКОВЫ → max(|du|,|dv|), иначе |du|+|dv|.
; НЕ Чебышёв (исправляет §7.3). IN: D=cellA, E=cellB. OUT: A=дистанция. Портит AF,BC,DE,HL.
Battle_GetDistance:
                LD   A, D
                CALL Battle_CellRowCol             ; B=yA, A=xA
                LD   C, A                           ; C=xA
                LD   A, B
                SRL  A
                ADD  A, C                           ; A = uA = xA + yA÷2
                LD   C, A                           ; C=uA
                LD   A, B                           ; A=yA
                PUSH AF                             ; stack: yA (в D после POP)
                PUSH BC                             ; stack: C=uA
                LD   A, E
                CALL Battle_CellRowCol             ; B=yB, A=xB
                LD   L, A                           ; L=xB
                LD   A, B
                SRL  A
                ADD  A, L                           ; A = uB = xB + yB÷2
                LD   L, A                           ; L=uB
                LD   A, B                           ; A=yB
                POP  BC                             ; C=uA (B=мусор)
                POP  DE                             ; D=yA (E=мусор-флаги)
                SUB  D                              ; A = yB − yA = du (signed)
                LD   H, A                           ; H=du
                LD   A, L                           ; A=uB
                SUB  C                              ; A = uB − uA = dv (signed)
                LD   E, A                           ; E=dv
                CALL .abs8                          ; |dv|
                LD   B, A                           ; B=|dv|
                LD   A, H
                CALL .abs8                          ; |du|
                LD   D, A                           ; D=|du|
                LD   A, H                           ; знаки du,dv одинаковы?
                XOR  E                              ; bit7=1 → разные знаки
                AND  #80
                JR   NZ, .gdsum                     ; разные → |du|+|dv|
                LD   A, D                           ; одинаковые → max(|du|,|dv|)
                CP   B
                RET  NC                             ; |du|≥|dv| → A=|du|
                LD   A, B
                RET
.gdsum:         LD   A, D
                ADD  A, B                           ; |du|+|dv|
                RET
.abs8:          BIT  7, A                           ; A=|A| (signed 8-bit)
                RET  Z
                NEG
                RET

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

; HL = HL / C (беззнак. 16÷8, сдвиг-вычитание, 16 итераций). C≠0. OUT: HL=частное, A=остаток.
; Остаток < C ≤ ~42, переполнения RLA нет. Портит AF,B,HL (C сохраняется как делитель).
Battle_Div16by8:
                XOR  A                               ; остаток = 0
                LD   B, 16
.dvloop:        ADD  HL, HL                          ; HL <<= 1, старший бит → CF
                RLA                                  ; остаток = остаток<<1 | CF
                CP   C
                JR   C, .dvskip
                SUB  C                               ; остаток -= делитель
                INC  L                               ; бит частного (L bit0, только что освобождён сдвигом)
.dvskip:        DJNZ .dvloop
                RET

; 24-бит произведение (BattleMulBuf) = HL(16) × A(8, малый — dist≤~14, повт.сложение).
; Портит AF,BC,DE,HL. Результат LE в BattleMulBuf[0..2].
Battle_Mul16x8:
                LD   B, A
                XOR  A                               ; acc24 = 0
                LD   (BattleMulBuf), A
                LD   (BattleMulBuf + 1), A
                LD   (BattleMulBuf + 2), A
                LD   A, B
                OR   A
                RET  Z                               ; ×0 → 0
.mlloop:        PUSH HL
                LD   DE, (BattleMulBuf)              ; acc.low16 += HL
                ADD  HL, DE
                LD   (BattleMulBuf), HL              ; (LD не трогает CF)
                LD   A, (BattleMulBuf + 2)
                ADC  A, 0                            ; +перенос в байт2
                LD   (BattleMulBuf + 2), A
                POP  HL
                DJNZ .mlloop
                RET

; BattleMulBuf(24,LE) = HL × DE (сдвиг-сложение, 16 итераций). Для GetStrength=str_fp×count.
; Переполнение >16.7M вне скоупа skirmish. Портит AF,B,DE,HL.
Battle_Mul16x16_24:
                XOR  A
                LD   (BattleMulBuf), A
                LD   (BattleMulBuf + 1), A
                LD   (BattleMulBuf + 2), A
                LD   B, 16
.m24loop:       PUSH HL                              ; acc <<= 1 (24-бит)
                LD   HL, (BattleMulBuf)
                ADD  HL, HL                          ; low16<<1, CF=бит15
                LD   (BattleMulBuf), HL
                LD   A, (BattleMulBuf + 2)
                RLA                                  ; байт2<<1 + CF
                LD   (BattleMulBuf + 2), A
                POP  HL
                EX   DE, HL                          ; DE <<= 1, старший бит → CF
                ADD  HL, HL
                EX   DE, HL
                JR   NC, .m24skip
                PUSH DE                              ; бит=1 → acc += HL
                LD   DE, (BattleMulBuf)
                PUSH HL
                ADD  HL, DE
                LD   (BattleMulBuf), HL
                LD   A, (BattleMulBuf + 2)
                ADC  A, 0
                LD   (BattleMulBuf + 2), A
                POP  HL
                POP  DE
.m24skip:       DJNZ .m24loop
                RET

; 24-бит аккумулятор по DE += BattleMulBuf. Портит A,F,HL; DE — на байт2 acc (выход).
Battle_Acc24AddMul:
                LD   HL, BattleMulBuf
                LD   A, (DE)
                ADD  A, (HL)
                LD   (DE), A
                INC  DE
                INC  HL
                LD   A, (DE)
                ADC  A, (HL)
                LD   (DE), A
                INC  DE
                INC  HL
                LD   A, (DE)
                ADC  A, (HL)
                LD   (DE), A
                RET

; Нормализовать ПАРУ 24-бит величин (HL→A-ptr, DE→B-ptr) в 16-бит BattleAnlN1/N2 с сохранением
; отношения: while (любая ≥ #8000 в low16 || байт2≠0) обе >>= 1. Портит всё.
Battle_AnlNormPair:
                PUSH DE
                PUSH HL
.nploop:        POP  HL                              ; ptrA
                POP  DE                              ; ptrB
                PUSH DE
                PUSH HL
                INC  HL
                INC  HL
                LD   A, (HL)                         ; A.byte2
                OR   A
                JR   NZ, .npshift
                DEC  HL
                LD   A, (HL)                         ; A.byte1
                AND  #80
                JR   NZ, .npshift
                EX   DE, HL                          ; проверить B
                INC  HL
                INC  HL
                LD   A, (HL)
                OR   A
                JR   NZ, .npshift
                DEC  HL
                LD   A, (HL)
                AND  #80
                JR   NZ, .npshift
                POP  HL                              ; обе <32768 → скопировать low16 в N1/N2
                POP  DE
                LD   A, (HL)
                LD   (BattleAnlN1), A
                INC  HL
                LD   A, (HL)
                LD   (BattleAnlN1 + 1), A
                LD   A, (DE)
                LD   (BattleAnlN2), A
                INC  DE
                LD   A, (DE)
                LD   (BattleAnlN2 + 1), A
                RET
.npshift:       POP  HL                              ; сдвиг ОБЕИХ >>1 (24-бит, in place)
                POP  DE
                PUSH DE
                PUSH HL
                CALL .npshr3                         ; A-ptr >>= 1
                POP  HL
                POP  DE
                PUSH DE
                PUSH HL
                EX   DE, HL
                CALL .npshr3                         ; B-ptr >>= 1
                JR   .nploop
.npshr3:        INC  HL                              ; HL → 24-бит LE; сдвиг вправо с байта2
                INC  HL
                SRL  (HL)                            ; byte2
                DEC  HL
                RR   (HL)                            ; byte1
                DEC  HL
                RR   (HL)                            ; byte0
                RET

; A=1 если N1×C > N2×B (строго), иначе A=0. Портит всё.
Battle_AnlRatioGT:
                PUSH BC
                LD   HL, (BattleAnlN1)
                LD   A, C
                CALL Battle_Mul16x8                  ; MulBuf = N1×k1 (24-бит)
                LD   HL, BattleMulBuf
                LD   DE, BattleMulBuf2
                LD   BC, 3
                LDIR                                 ; → MulBuf2
                POP  BC
                LD   HL, (BattleAnlN2)
                LD   A, B
                CALL Battle_Mul16x8                  ; MulBuf = N2×k2
                LD   A, (BattleMulBuf2 + 2)          ; MulBuf2 > MulBuf ? (24-бит, со старшего)
                LD   HL, BattleMulBuf + 2
                CP   (HL)
                JR   C, .rgno
                JR   NZ, .rgyes
                LD   A, (BattleMulBuf2 + 1)
                DEC  HL
                CP   (HL)
                JR   C, .rgno
                JR   NZ, .rgyes
                LD   A, (BattleMulBuf2)
                DEC  HL
                CP   (HL)
                JR   C, .rgno
                JR   Z, .rgno                        ; равно → НЕ строго больше
.rgyes:         LD   A, 1
                RET
.rgno:          XOR  A
                RET

; 24-бит сравнение (HL) < (DE) (оба ptr на LE-тройки)? A=1 да, A=0 нет. Портит всё.
Battle_Cmp24LT:
                INC  HL
                INC  HL
                INC  DE
                INC  DE
                LD   A, (DE)                         ; B.byte2
                CP   (HL)                            ; − A.byte2
                JR   C, .clno                        ; B<A → not less
                JR   NZ, .clyes                      ; B>A → A<B
                DEC  HL
                DEC  DE
                LD   A, (DE)
                CP   (HL)
                JR   C, .clno
                JR   NZ, .clyes
                DEC  HL
                DEC  DE
                LD   A, (DE)
                CP   (HL)
                JR   C, .clno
                JR   NZ, .clyes
.clno:          XOR  A                               ; равно/больше → не меньше
                RET
.clyes:         LD   A, 1
                RET

; ★Battle_AIAnalyze — analyzeBattleState (ai_battle.cpp:949) для безгеройного skirmish:
; суммы GetStrength (=str_fp×count, фикс ×16) своих/врагов + стрелков; флаги
; _defensiveTactics (:1124) и _cautiousOffensive (:1164). Замок/спеллы/ретрит — n/a (нет героя).
; (isFlying у Knight-юнитов нет; overPower=10; ветку flying→6 добавить с расами полёта.)
; Портит всё. OUT: BattleAnl*/BattleDefTactics/BattleCautious.
Battle_AIAnalyze:
                LD   HL, BattleAnlMyStr              ; обнулить 4 аккумулятора (12 байт подряд)
                LD   B, 12
                XOR  A
.azclr:         LD   (HL), A
                INC  HL
                DJNZ .azclr
                LD   A, (BattleActiveUnit)           ; сторона активного
                CALL Battle_UnitAddr
                INC  HL
                INC  HL
                LD   A, (HL)
                LD   (BattleAISide), A
                LD   C, 0
.azloop:        LD   A, C
                LD   (BattleAnlIdx), A
                CALL Battle_UnitAddr                 ; slot3-чтения ДО MonsterStats_Read
                LD   A, (HL)                         ; type
                CALL Battle_TypeToMonId  ; type→id
                LD   (BattleThrEId), A               ; id (переиспользуем scratch)
                INC  HL
                INC  HL                              ; +2 side
                LD   B, (HL)
                INC  HL
                LD   E, (HL)                         ; count
                INC  HL
                LD   D, (HL)
                LD   A, D
                OR   E
                JP   Z, .aznext                      ; мёртв → пропуск
                LD   A, (BattleAISide)               ; my? (side==active.side) → флаг в C
                CP   B
                LD   A, 1
                JR   Z, .azmy
                XOR  A
.azmy:          LD   (BattleThrR), A                 ; myFlag (переиспользуем scratch)
                PUSH DE                              ; count
                LD   A, (BattleThrEId)
                LD   B, A
                CALL MonsterStats_Read               ; → str_fp в буфере (+8/+9), shots (+7)
                POP  DE                              ; count
                LD   HL, (MonsterStatBuf + 8)        ; str_fp
                CALL Battle_Mul16x16_24              ; MulBuf = GetStrength×16 (24-бит)
                LD   A, (BattleThrR)                 ; армейский аккумулятор
                OR   A
                JR   Z, .azen
                LD   DE, BattleAnlMyStr
                JR   .azacc
.azen:          LD   DE, BattleAnlEnStr
.azacc:         CALL Battle_Acc24AddMul
                LD   A, (BattleAnlIdx)               ; стрелок = ОСТАТОК шотов>0 (isArchers) → и в shooters
                LD   HL, BattleUnitShots
                CALL Battle_IdxByte
                LD   A, (HL)
                OR   A
                JR   Z, .aznext
                LD   A, (BattleThrR)
                OR   A
                JR   Z, .azens
                LD   DE, BattleAnlMyShoot
                JR   .azaccs
.azens:         LD   DE, BattleAnlEnShoot
.azaccs:        CALL Battle_Acc24AddMul
.aznext:        LD   A, (BattleAnlIdx)
                LD   C, A
                INC  C
                LD   A, C
                CP   BATTLE_UNIT_COUNT
                JP   C, .azloop
                ; ---- флаги ----
                XOR  A
                LD   (BattleDefTactics), A
                ; _cautiousOffensive = enemyArcherRatio < 0.15 ⇔ en×3 > enShoot×20 (СТРОГО, как double <)
                LD   HL, BattleAnlEnStr              ; нормализовать пару (en, enShoot)
                LD   DE, BattleAnlEnShoot
                CALL Battle_AnlNormPair              ; N1=en, N2=enShoot
                LD   C, 3
                LD   B, 20
                CALL Battle_AnlRatioGT               ; en×3 > enShoot×20 ⇔ ratio<0.15
                LD   (BattleCautious), A
                ; --- _defensiveTactics (:1124) ---
                ; 1) активный в СВОЕЙ защищённой половине? x=cell%11; side0: x≤4; side1: x≥6
                LD   A, (BattleActiveUnit)
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)                          ; cell
                CALL Battle_CellRowCol                ; B=ряд, A=кол(x)
                LD   B, A
                LD   A, (BattleAISide)
                OR   A
                LD   A, B
                JR   NZ, .azs1
                CP   5                                ; side0: x+1≤5 ⇔ x<5
                RET  NC                               ; вне зоны → offensive (defTactics=0)
                JR   .azzone
.azs1:          CP   6                                ; side1: 11−x≤5 ⇔ x≥6
                RET  C                                ; вне зоны → offensive
.azzone:        ; 2) my > enemy×10 → offensive (overPower; flying→6 с расами полёта)
                LD   HL, BattleAnlMyStr
                LD   DE, BattleAnlEnStr
                CALL Battle_AnlNormPair               ; N1=my, N2=en
                LD   C, 1
                LD   B, 10
                CALL Battle_AnlRatioGT                ; my×1 > en×10 ?
                OR   A
                RET  NZ                               ; сильно сильнее → offensive
                ; 3) myShooters < enemyShooters → offensive
                LD   HL, BattleAnlMyShoot
                LD   DE, BattleAnlEnShoot
                CALL Battle_Cmp24LT
                OR   A
                RET  NZ                               ; своих стрелков меньше → offensive
                ; 4) _defendingCastle → true (skirmish: замка нет — пропуск)
                ; 5) myArcherRatio < 0.15 → offensive ⇔ my×3 > myShoot×20 (СТРОГО)
                LD   HL, BattleAnlMyStr
                LD   DE, BattleAnlMyShoot
                CALL Battle_AnlNormPair               ; N1=my, N2=myShoot
                LD   C, 3
                LD   B, 20
                CALL Battle_AnlRatioGT
                OR   A
                RET  NZ                               ; ratio<0.15 → offensive
                ; 6) enemyArcherRatio > 0.66 → offensive ⇔ enShoot×50 > en×33
                LD   HL, BattleAnlEnShoot
                LD   DE, BattleAnlEnStr
                CALL Battle_AnlNormPair               ; N1=enShoot, N2=en
                LD   C, 50
                LD   B, 33
                CALL Battle_AnlRatioGT
                OR   A
                RET  NZ                               ; у врага перебор стрелков → offensive
                LD   A, 1                             ; все условия → оборона
                LD   (BattleDefTactics), A
                RET

; Клик по зоне кнопки Skip (право панели)? OUT: A=1 (NZ) попал, A=0 (Z) мимо.
Battle_CheckSkipClick:
                CALL Input_MouseX
                LD   DE, BATTLE_SKIP_X0
                OR   A
                SBC  HL, DE
                JR   C, .smiss
                CALL Input_MouseX
                LD   DE, BATTLE_SKIP_X1
                OR   A
                SBC  HL, DE
                JR   NC, .smiss
                CALL Input_MouseY
                LD   DE, BATTLE_SKIP_Y0
                OR   A
                SBC  HL, DE
                JR   C, .smiss
                CALL Input_MouseY
                LD   DE, BATTLE_SKIP_Y1
                OR   A
                SBC  HL, DE
                JR   NC, .smiss
                LD   A, 1
                RET
.smiss:         XOR  A
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
.aashots:       PUSH DE                            ; сохранить флаг соседства (D)
                LD   A, (BattleActiveUnit)         ; isArchers = ОСТАТОК выстрелов (BattleUnitShots),
                LD   HL, BattleUnitShots           ;   НЕ базовые статы (Unit::GetShots=_shotsLeft):
                CALL Battle_IdxByte                ;   пустой стрелок дерётся как мили. Без пейджинга.
                LD   A, (HL)
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

; Достижимые клетки АКТИВНОГО → BattleReach (обёртка над ReachEx; ignore=#FF).
Battle_ComputeReachable:
                LD   A, (BattleActiveUnit)
                LD   (BattleReachUnit), A
                LD   HL, BattleReach
                LD   (BattleReachBufPtr), HL
                LD   A, #FF
                LD   (BattleFindIgnore), A
                ; fallthrough → Battle_ComputeReachEx
; Параметризованный flood по соседям (BattleAdjTab) на глубину speed юнита (#91):
; юнит = (BattleReachUnit), буфер 99 = (BattleReachBufPtr), (BattleFindIgnore) = «снятый» юнит
; (UnitRemover archerDecision; #FF=никого). buf[c]: 0=нет, 1..speed=дист, #FF=origin.
; ЖИВЫЕ ЮНИТЫ = ПРЕПЯТСТВИЯ: flood НЕ заходит в занятые (как fheroes2 BattlePathfinder) —
; buf≠0 ⇒ «можно встать» (этим пользуются AI MBO/Defense-cover и ход игрока). Портит всё.
Battle_ComputeReachEx:
                LD   HL, (BattleReachBufPtr)       ; очистить 99
                LD   B, 99
.crclr:         LD   (HL), 0
                INC  HL
                DJNZ .crclr
                LD   A, (BattleReachUnit)           ; speed юнита
                CALL Battle_UnitSpeed
                LD   (BattleReachSpd), A
                LD   A, (BattleReachUnit)           ; buf[cell]=#FF (origin)
                CALL Battle_UnitAddr
                INC  HL
                LD   A, (HL)
                LD   E, A
                LD   D, 0
                LD   HL, (BattleReachBufPtr)
                ADD  HL, DE
                LD   (HL), #FF
                LD   A, 1                            ; шаг d=1..speed
.crpass:        LD   (BattleReachStep), A
                LD   HL, BattleReachSpd
                CP   (HL)
                JR   Z, .crdo
                JR   C, .crdo
                LD   A, #FF                          ; d>speed → готово; ignore сбросить (одноразовый)
                LD   (BattleFindIgnore), A
                RET
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
                LD   DE, (BattleReachBufPtr)
                ADD  HL, DE
                LD   A, (HL)
                LD   HL, BattleReachSrc
                CP   (HL)
                JR   NZ, .crcnext                    ; buf[c]!=источник
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
                PUSH AF                              ; n — клетка занята живым юнитом? → препятствие
                CALL Battle_FindUnitAtCell           ; (портит C/HL/DE — всё под PUSH; чтит ignore)
                CP   #FF
                JR   NZ, .crnbskp                    ; занята → не расширяться
                POP  AF                              ; A=n
                LD   L, A
                LD   H, 0
                LD   DE, (BattleReachBufPtr)
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   NZ, .crnbsk                     ; уже помечен
                LD   A, (BattleReachStep)
                LD   (HL), A                         ; buf[n]=d
                JR   .crnbsk
.crnbskp:       POP  AF                              ; сбалансировать стек (занятая клетка)
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
                LD   (BattleStatusMsg), A          ; по умолчанию пусто
                LD   A, (BattleHoverCell)
                CP   #FF
                JP   Z, Battle_StatusButtons       ; вне поля → hover-подсказки кнопок панели
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
                CALL Battle_AttackAllowed           ; враг: можно дотянуться? (+ выставляет BattleWasMelee)
                OR   A
                RET  Z                              ; нельзя → Turn N
                ; ПО ОРИГИНАЛУ (GetBattleCursor:2928): Shoot ТОЛЬКО стрелок (isArchers=_shotsLeft>0)
                ; И НЕ в контакте (isHandFighting → мили-меч и «Attack», даже у стрелка).
                LD   A, (BattleActiveUnit)
                LD   HL, BattleUnitShots
                CALL Battle_IdxByte
                LD   B, (HL)                        ; B = остаток выстрелов
                LD   A, (BattleTargetUnit)
                CALL Battle_UnitAddr
                LD   C, (HL)                        ; C = target.type (0/1)
                LD   A, B
                OR   A
                JR   Z, .stmelee                    ; выстрелов нет → мили
                LD   A, (BattleWasMelee)            ; цель — сосед → hand fighting → мили
                OR   A
                JR   NZ, .stmelee
                LD   A, C
                ADD  A, 5                            ; Shoot: 5=Peasant,6=Archer
                LD   (BattleStatusMsg), A
                RET
.stmelee:       LD   A, C
                ADD  A, 3                            ; Attack: 3=Peasant,4=Archer
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

; Мышь вне поля: hover-подсказки КНОПОК панели (ориг. battle_interface.cpp:3274-3306):
; Auto (0..49, 443..461) → 9 «Automatic combat modes»; Settings (0..49, 461..480) → 10
; «Customize system options»; Skip (591..640, 443..480) → 11 «Skip this unit». Лог. коорд.
Battle_StatusButtons:
                CALL Input_MouseY
                LD   DE, 443
                OR   A
                SBC  HL, DE
                RET  C                              ; выше панели кнопок
                PUSH HL                             ; HL = my−443
                CALL Input_MouseX
                LD   DE, 49
                OR   A
                SBC  HL, DE
                JR   C, .leftbtns                   ; x < 49 → Auto/Settings
                LD   DE, 591 - 49
                OR   A
                SBC  HL, DE
                POP  DE                             ; (баланс стека; my больше не нужен)
                RET  C                              ; 49..590 — статус-бары, без подсказки
                LD   A, 11                          ; Skip this unit
                LD   (BattleStatusMsg), A
                RET
.leftbtns:      POP  HL                             ; HL = my−443
                LD   DE, 461 - 443
                OR   A
                SBC  HL, DE                         ; my−461
                LD   A, 9                           ; C: my<461 → Automatic combat modes
                JR   C, .setb
                LD   A, 10                          ; иначе Customize system options
.setb:          LD   (BattleStatusMsg), A
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
                LD   A, (BattleTmpType)           ; вариант = type*2+side
                ADD  A, A
                LD   C, A
                LD   A, (BattleTmpSide)
                ADD  A, C
                LD   (BattleTmpVar), A
                LD   A, (BattleActiveUnit)         ; текущий слот кадра активного
                CALL Battle_CalcAnimSlot
                LD   A, (BattleTmpCell)            ; якорь клетки активного
                CALL Battle_SetCellAnchor
                LD   HL, Battle_Contour_Begin_DL
                LD   BC, Battle_Contour_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Battle_EmitUnitSprite        ; контур текущего кадра (палитра-силуэт от пролога)
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
                CALL Battle_EmitUnitVertex         ; вершина = якорь + смещение кадра
                POP  BC
                INC  C
                DJNZ .contloop
                LD   HL, Battle_Contour_End_DL     ; сброс TRANSLATE 0 + END
                LD   BC, Battle_Contour_End_DL_SIZE
                CALL Render_CmdBufCopy
.contour_done:
                ; --- ДИНАМИЧЕСКИЕ ЮНИТЫ (ПО ОРИГИНАЛУ, 2 прохода): сначала ТРУПЫ (последний
                ;     DEATH-кадр, лежат до конца боя — RedrawCorpses), затем живые/умирающий. ---
                LD   HL, Battle_Units_Begin_DL
                LD   BC, Battle_Units_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, 1
                LD   (BattleCorpsePass), A
                CALL Battle_DrawUnitsPass          ; трупы (под живыми)
                XOR  A
                LD   (BattleCorpsePass), A
                CALL Battle_DrawUnitsPass          ; живые + умирающий
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
                LD   A, (BattleTmpCell)            ; бар = якорь клетки ± смещения (таблица не нужна)
                CALL Battle_SetCellAnchor
                LD   HL, (BattleTmpAnchX)
                LD   DE, -BATTLE_CNTBAR_DX
                ADD  HL, DE
                LD   (RenderPathVertexX), HL
                LD   HL, (BattleTmpAnchY)
                LD   DE, BATTLE_CNTBAR_DY0
                ADD  HL, DE
                LD   (RenderPathVertexY), HL
                CALL Render_WriteVertex2FCmd       ; верх-лево бара
                LD   HL, (BattleTmpAnchX)
                LD   DE, BATTLE_CNTBAR_DX
                ADD  HL, DE
                LD   (RenderPathVertexX), HL
                LD   HL, (BattleTmpAnchY)
                LD   DE, BATTLE_CNTBAR_DY1
                ADD  HL, DE
                LD   (RenderPathVertexY), HL
                CALL Render_WriteVertex2FCmd       ; низ-право бара
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
                PUSH DE                            ; сохранить count
                LD   A, (BattleTmpCell)            ; перо = якорь клетки (центр X, y бара)
                CALL Battle_SetCellAnchor
                LD   HL, (BattleTmpAnchX)
                LD   (ResPenX), HL
                LD   HL, (BattleTmpAnchY)
                LD   DE, BATTLE_CNTPEN_DY
                ADD  HL, DE
                LD   (ResPenY), HL
                POP  HL                            ; HL = count
                CALL Battle_DrawCountNum          ; центрир. число СВОИМИ цифрами боя (глоб.DigitTable затёрт payload'ом)
.numskip:       POP  BC
                DJNZ .numloop
                LD   HL, Battle_Count_End_DL
                LD   BC, Battle_Count_End_DL_SIZE
                CALL Render_CmdBufCopy
                ; --- СТАТУС-БАР панели (КАК ВИДИТ ИГРОК, battle-no-turn-n-label): идёт движение →
                ;     «Moved …: from [src] to [dst].»; иначе событие → «X do N damage[. M perish]»;
                ;     иначе hover-подсказка; msg==0 → ПУСТО («Turn N» игрок в оригинале НЕ видит).
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
.st_normal:     LD   A, (BattleStatusMsg)
                OR   A
                JP   Z, .no_status                 ; msg==0 → ПУСТАЯ строка (НИКАКОГО «Turn N»)
                CP   5                             ; Shoot (5/6) → составная строка с ЖИВЫМ остатком
                JR   Z, .st_shoot
                CP   6
                JR   Z, .st_shoot
                LD   HL, Battle_Status_Begin_DL    ; общий префикс (палитра + BEGIN BITMAPS)
                LD   BC, Battle_Status_Begin_DL_SIZE
                CALL Render_CmdBufCopy
                LD   A, (BattleStatusMsg)
                JR   .st_verb
.st_shoot:      CALL Battle_RenderShootStatus      ; «Shoot X (N shot(s) left)» (свой пролог+эпилог)
                JP   .no_status
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
                ; --- ПКМ-ПОПАП ArmyInfo (пока ПКМ зажат) поверх поля, под курсором ---
                LD   A, (BattleHelpShow)           ; ПКМ-справка ЗАМЕЩАЕТ окна (одна область)
                CP   #FF
                JR   NZ, .helpwin
                LD   A, (ArmyInfoShow)
                OR   A
                CALL NZ, Battle_RenderArmyInfo
                LD   A, (BattleSettingsOpen)
                OR   A
                CALL NZ, Battle_RenderSettings
                JR   .winsdone
.helpwin:       CALL Battle_RenderHelp
.winsdone:      ; --- ОКНО ИТОГА (faithful: WINLOSE-рамка + баннер) если бой окончен ---
                LD   A, (BattleResult)
                OR   A
                JR   Z, .no_result
                LD   HL, Battle_WinDlg_DL           ; ГЛОБАЛЬНАЯ тень (одна формула на все окна)
                LD   BC, Battle_WinDlg_DL_SIZE
                CALL Render_WindowShadowDL
                LD   HL, Battle_WinDlg_DL
                LD   BC, Battle_WinDlg_DL_SIZE
                CALL Render_CmdBufCopy
                CALL Battle_RenderWinText          ; нативные надписи окна поверх (без ×1.6-рвани)
                CALL Battle_RenderCasualties       ; потери: иконы MONS32 + счёт убитых / «None» (faithful)
.no_result:
                ; (жёлтая подсветка наведённой ячейки убрана — не по оригиналу; курсор поверх всего)
                CALL Battle_RenderCursor           ; форма курсора по теме hover (GetBattleCursor)
                ; DEBUG-зеркало боя в резидентную page5-зону (statedump её видит; slot3 — нет)
                LD   HL, BattleUnitState
                LD   DE, DbgBattleMirror
                LD   BC, BATTLE_UNIT_COUNT * BATTLE_UNIT_STATE_SIZE
                LDIR
                LD   HL, BattleStartCnt
                LD   BC, BATTLE_UNIT_COUNT * 2
                LDIR
                LD   A, (BattleResult)
                LD   (DE), A
                INC  DE
                LD   HL, BattleCasK0               ; +29..32: CasK0/K1 (диагностика потерь)
                LD   BC, 4
                LDIR
                CALL Render_SwapFrameDMA
                RET

; Battle_RenderCursor — ФОРМА курсора ПО ОРИГИНАЛУ (GetBattleCursor, battle_interface.cpp:2879):
; вне поля → WAR_POINTER; msg==0 → WAR_NONE; Move→WAR_MOVE; Shoot→WAR_ARROW; View→WAR_INFO;
; Attack → НАПРАВЛЕННЫЙ МЕЧ (зона мыши в клетке врага → направление атаки, фильтр доступности,
; ближайшее по/против часовой — как GetTriangleDirection + getSwordCursorForAttackDirection).
Battle_RenderCursor:
                CALL Input_MouseX
                LD   (CursorPixelX), HL
                CALL Input_MouseY
                LD   (CursorPixelY), HL
                LD   A, (BattleResult)             ; окно итога → ВСЕГДА стрелка (ориг.
                OR   A                             ;   SetThemes(WAR_POINTER), b_interface.cpp:1383)
                JR   NZ, .pointer
                LD   A, (ArmyInfoShow)             ; ПКМ-попап — тоже стрелка (модальная пауза)
                OR   A
                JR   NZ, .pointer
                LD   A, (BattleSettingsOpen)       ; окно настроек — стрелка (Cursor::POINTER :266)
                OR   A
                JR   NZ, .pointer
                LD   A, (BattleHelpShow)           ; ПКМ-справка — стрелка (модальная пауза)
                INC  A                             ; #FF+1=0 → нет справки
                JR   NZ, .pointer
                LD   A, (BattleHoverCell)          ; вне поля/на панели → обычная стрелка
                CP   #FF
                JR   NZ, .onfield
.pointer:
                LD   A, CURSOR_BATTLE_BASE_INDEX + 4   ; WAR_POINTER
                JR   .setidx
.onfield:       LD   A, (BattleStatusMsg)
                CP   9
                JR   C, .ok
                XOR  A                             ; msg вне 0..8 → None
.ok:            CP   3                             ; Attack (3/4) → направленный меч
                JR   Z, .sword
                CP   4
                JR   Z, .sword
                LD   E, A
                LD   D, 0
                LD   HL, BattleCursorTab
                ADD  HL, DE
                LD   A, (HL)
.setidx:        LD   (CursorSpriteIndex), A
                JP   Render_CursorCmd
.sword:         CALL Battle_SwordCursor            ; A = спрайт меча по направлению
                JR   .setidx
BattleCursorTab:                                   ; [BattleStatusMsg] → индекс боевого курсора
                DEFB CURSOR_BATTLE_BASE_INDEX + 0  ; 0 пусто → WAR_NONE
                DEFB CURSOR_BATTLE_BASE_INDEX + 1  ; 1 Move
                DEFB CURSOR_BATTLE_BASE_INDEX + 1  ; 2 Move
                DEFB CURSOR_BATTLE_BASE_INDEX + 0  ; 3 Attack (меч — отдельная ветка)
                DEFB CURSOR_BATTLE_BASE_INDEX + 0  ; 4 Attack
                DEFB CURSOR_BATTLE_BASE_INDEX + 2  ; 5 Shoot → WAR_ARROW
                DEFB CURSOR_BATTLE_BASE_INDEX + 2  ; 6 Shoot
                DEFB CURSOR_BATTLE_BASE_INDEX + 3  ; 7 View  → WAR_INFO
                DEFB CURSOR_BATTLE_BASE_INDEX + 3  ; 8 View

; Направленный меч атаки: зона мыши в hover-клетке → направление (0=TL,1=TOP,2=TR,3=R,4=BR,
; 5=BOTTOM,6=BL,7=L — по часовой); недоступное → ближайшее по часовой/против (оригинальный
; поиск); доступность = сосед-клетка с той стороны достижима (BattleReach≠0, вкл. origin).
; OUT: A = индекс спрайта меча. Портит A,BC,DE,HL.
Battle_SwordCursor:
                LD   A, (BattleHoverCell)          ; центр клетки в ЛОГ. коорд. (мышь — лог. 640×480):
                LD   L, A                          ;   cx = 111 − 22·odd + 44·col, cy = 88 + 42·row
                LD   H, 0
                LD   C, 11
                CALL Battle_Div16by8               ; L = row, A = col
                PUSH AF                            ; col
                LD   A, L
                LD   (BattleSwordDir), A           ; временно row
                LD   H, 0                          ; cy = 88 + 42·row (42r = 32r+8r+2r)
                ADD  HL, HL                        ; 2r
                PUSH HL
                ADD  HL, HL
                ADD  HL, HL                        ; 8r
                PUSH HL
                ADD  HL, HL
                ADD  HL, HL                        ; 32r
                POP  DE
                ADD  HL, DE
                POP  DE
                ADD  HL, DE                        ; 42r
                LD   DE, 88
                ADD  HL, DE
                EX   DE, HL                        ; DE = cy
                LD   HL, (CursorPixelY)
                OR   A
                SBC  HL, DE                        ; HL = dy (лог.)
                PUSH HL
                POP  BC                            ; BC = dy (сохранить)
                POP  AF                            ; col
                LD   L, A                          ; cx = 111 − 22·odd + 44·col (44c = 32c+8c+4c)
                LD   H, 0
                ADD  HL, HL
                ADD  HL, HL                        ; 4c
                PUSH HL
                ADD  HL, HL                        ; 8c
                PUSH HL
                ADD  HL, HL
                ADD  HL, HL                        ; 32c
                POP  DE
                ADD  HL, DE
                POP  DE
                ADD  HL, DE                        ; 44c
                LD   DE, 111
                ADD  HL, DE
                LD   A, (BattleSwordDir)           ; row: нечётный ряд смещён влево на 22
                AND  1
                JR   Z, .cxok
                LD   DE, -22
                ADD  HL, DE
.cxok:          EX   DE, HL                        ; DE = cx
                LD   HL, (CursorPixelX)
                OR   A
                SBC  HL, DE                        ; HL = dx (лог.)
                EX   DE, HL                        ; DE = dx
                LD   H, B                          ; HL = dy
                LD   L, C
                ; зона (ЛОГ. px, ≈ трети гекса 44×52): dy<−9 верх, dy>9 низ, иначе середина
                PUSH DE
                LD   DE, 9
                ADD  HL, DE                        ; dy+9
                POP  DE
                BIT  7, H
                JR   NZ, .top                      ; dy < −9
                PUSH DE
                LD   DE, -19
                ADD  HL, DE                        ; dy−10
                POP  DE
                BIT  7, H
                JR   Z, .bottom                    ; dy ≥ 10
                LD   C, 7                          ; середина: LEFT
                BIT  7, D
                JR   NZ, .havedir                  ; dx<0 → LEFT
                LD   C, 3                          ; иначе RIGHT
                JR   .havedir
.top:           CALL .colsel                       ; C = 0/1/2 (TL/TOP/TR)
                JR   .havedir
.bottom:        CALL .colsel                       ; 0/1/2 → 6/5/4 (BL/BOTTOM/BR)
                LD   A, 6
                SUB  C
                LD   C, A
.havedir:       LD   A, C                          ; поиск доступного: k=0, потом +k (час.) / −k
                LD   (BattleSwordDir), A
                LD   A, (BattleHoverCell)
                LD   A, (BattleActiveUnit)
                LD   B, 0
.sfind:         LD   A, (BattleSwordDir)
                ADD  A, B
                AND  7
                LD   C, A
                CALL .avail
                OR   A
                JR   NZ, .sfound
                LD   A, B
                OR   A
                JR   Z, .snext
                LD   A, (BattleSwordDir)
                SUB  B
                AND  7
                LD   C, A
                CALL .avail
                OR   A
                JR   NZ, .sfound
.snext:         INC  B
                LD   A, B
                CP   5
                JR   C, .sfind
                LD   A, (BattleSwordDir)           ; фолбэк (не должно случаться): исходное
                LD   C, A
.sfound:        LD   A, C
                LD   HL, BattleDirSwordTab         ; направление → спрайт меча
                LD   E, C
                LD   D, 0
                ADD  HL, DE
                LD   A, (HL)
                RET
; C=направление → A=1 доступно / 0 нет. Портит A,DE,HL (B,C целы).
.avail:         LD   HL, BattleDirAdjCol
                LD   E, C
                LD   D, 0
                ADD  HL, DE
                LD   A, (HL)
                CP   #FF
                JR   Z, .nav                       ; TOP/BOTTOM — только wide (не наш случай)
                PUSH BC
                LD   C, A                          ; C = колонка AdjTab
                LD   A, (BattleHoverCell)
                LD   L, A
                LD   H, 0
                ADD  HL, HL                        ; ×2
                LD   E, L
                LD   D, H
                ADD  HL, HL                        ; ×4
                ADD  HL, DE                        ; ×6
                LD   E, C
                LD   D, 0
                ADD  HL, DE
                LD   DE, BattleAdjTab
                ADD  HL, DE
                LD   A, (HL)                       ; сосед с этой стороны
                POP  BC
                CP   #FF
                JR   Z, .nav                       ; за краем поля
                LD   L, A                          ; достижим? (BattleReach: 0=нет, #FF=origin, иначе да)
                LD   H, 0
                LD   DE, BattleReach
                ADD  HL, DE
                LD   A, (HL)
                OR   A
                JR   Z, .nav
                LD   A, 1
                RET
.nav:           XOR  A
                RET
; по dx (DE, лог.): < −7 → C=0 (левая треть), > 7 → C=2 (правая), иначе C=1 (середина)
.colsel:        PUSH DE
                EX   DE, HL                        ; HL = dx
                LD   DE, 7
                ADD  HL, DE                        ; dx+7
                BIT  7, H
                JR   NZ, .csl
                LD   DE, -15
                ADD  HL, DE                        ; dx−8
                BIT  7, H
                JR   Z, .csr
                LD   C, 1
                JR   .csd
.csl:           LD   C, 0
                JR   .csd
.csr:           LD   C, 2
.csd:           POP  DE
                RET
BattleSwordDir: DEFB 0
BattleDirAdjCol: DEFB 0, #FF, 1, 3, 5, #FF, 4, 2   ; направление → колонка BattleAdjTab {TL,TR,L,R,BL,BR}
BattleDirSwordTab:                                 ; направление АТАКИ → меч (противоположный, ориг. маппинг)
                DEFB CURSOR_BATTLE_BASE_INDEX + 7   ; TL → SWORD_BOTTOMRIGHT
                DEFB CURSOR_BATTLE_BASE_INDEX + 7   ; TOP (недостижимо для 1-hex)
                DEFB CURSOR_BATTLE_BASE_INDEX + 8   ; TR → SWORD_BOTTOMLEFT
                DEFB CURSOR_BATTLE_BASE_INDEX + 9   ; RIGHT → SWORD_LEFT
                DEFB CURSOR_BATTLE_BASE_INDEX + 10  ; BR → SWORD_TOPLEFT
                DEFB CURSOR_BATTLE_BASE_INDEX + 10  ; BOTTOM (недостижимо для 1-hex)
                DEFB CURSOR_BATTLE_BASE_INDEX + 5   ; BL → SWORD_TOPRIGHT
                DEFB CURSOR_BATTLE_BASE_INDEX + 6   ; LEFT → SWORD_RIGHT
