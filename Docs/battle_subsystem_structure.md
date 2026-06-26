# Структура подсистемы БОЯ (суть: структура + алгоритмы, не C++)

Полная схема архитектуры боя fheroes2/OpenHMM2 для переноса на FT812/Z80. Язык — лишь описание
сути; здесь — СУТЬ (данные + алгоритмы), чтобы реализовать, а не транслитерировать построчно.
Источник: OpenHMM2 `src/fheroes2/battle/*` (34 файла). Изучено по заголовкам (структура) + ключевым
функциям (алгоритмы).

═══════════════════════════════════════════════════════════════════════════════
## 0. ГЛАВНЫЙ ПРИНЦИП: МОДЕЛЬ ⟂ UI
- **Логика (`Arena`)** держит всё состояние и гоняет алгоритм. Рисовать НЕ умеет. Работает headless
  (AI / авто-бой). UI у неё — опциональный указатель `_interface`.
- **UI (`Interface`)** — отдельный слой: рендер состояния + ввод человека + ВСЕ диалоги + анимации
  действий + панель/лог/очередь.
- **Финал боя = диалог UI**, чистая функция от `Result` + потерь. Бой играть НЕ надо: дать готовый
  Result → показать блокирующий модал. Процесс и показ РАЗВЯЗАНЫ. (Моя ошибка была — впихнуть финал
  веткой в покадровый Update с форсом флага.)

═══════════════════════════════════════════════════════════════════════════════
## 1. МОДЕЛЬ ДАННЫХ (структура)

### Result (battle.h) — итог
Флаги на сторону: `WINS=0x80, LOSS=0x01, RETREAT=0x02, SURRENDER=0x04`. + опыт атакующего/защитника,
число мёртвых для некромантии. `isAttackerWin/isDefenderWin`.

### Unit (battle_troop.h) — ОТРЯД (наследует ArmyTroop[тип+число]+BitModes[флаги]+Control)
- `_uid` — уникальный id (по нему адресуются Command).
- **`_hitPoints` — ОБЩИЙ ПУЛ HP отряда** (не «N существ по полному hp»). Число живых = ceil(hp / hpМонстра).
  Урон уменьшает пул; killed = сколько ПОЛНЫХ существ умерло (с переносом остатка). ⚠ Моя «урон vs
  полное hp одного» — НЕВЕРНА (отсюда был «count 2→2»: урон < остатка пула → 0 убитых).
- `_initialCount`, **`_deadCount`/`GetDead()`** — для потерь. `_maxCount`.
- `_shotsLeft` — выстрелы (стрелок). `_position` (head+tail). `_affected` (длительности заклинаний).
- Флаги состояния `MonsterState`: `TR_MOVED`(ходил), `TR_RETALIATED`(ответил), `TR_SKIP`, удача/мораль
  good/bad, эффекты заклинаний (bless/haste/curse/slow/blind/paralyze/stone…).
- Алгоритмы: `NewTurn()`(сброс хода), `GetSpeed(skipStanding,skipMoved)`, `GetDamage(enemy,rng)`,
  `CalculateMin/MaxDamage`, `ApplyDamage→killed`, `isFlying/isDoubleAttack/isHandFighting/isArchers`,
  `isRetaliationAllowed`, `HowManyWillBeKilled(dmg)`.

### Cell (battle_cell.h) — КЛЕТКА  (44×52 px)
- `_index`(0..98), `_object`(препятствие, 0=проходима), `_unit`(кто стоит), `_coord[7]`.
- **Соседство = 6 направлений** (`CellDirection`: TOP_LEFT/TOP_RIGHT/RIGHT/BOTTOM_RIGHT/BOTTOM_LEFT/LEFT),
  гекс. ⚠ НЕ 8-Чебышёв (моя ошибка в добойщике).
- `isPassableForUnit/isPassableFromAdjacent`.
- `Position` = пара (head,tail) — широкие юниты занимают 2 клетки. `GetReachable(unit,dst,speed)`.

### Board (battle_board.h) — ДОСКА  (11×9 = 99 клеток)
Статика-алгоритмы сетки: `GetDirection(i1,i2)`, `GetIndexDirection(idx,dir)`, `isValidDirection`,
`GetAroundIndexes`(6 соседей), `GetDistance`(гекс-дистанция), `GetDistanceIndexes(center,radius)`,
`CanAttackFromCell`, `CanAttackTargetFromPosition`, `removeDeadUnits`, `GetNearestTroops`. + осада
(moat/castle/walls).

### Command (battle_command.h) — ДЕЙСТВИЕ как ДАННЫЕ (command-pattern)
Тип + параметры: `MOVE`(UID,клетка), `ATTACK`(атакер UID, цель UID, клетка-движения, клетка-цели,
направление), `SPELLCAST`, `MORALE`, `CATAPULT`, `TOWER`, `RETREAT`, `SURRENDER`, `SKIP`(UID),
TOGGLE_AUTO/QUICK. Ввод (человек/AI) → Command → `Arena.ApplyAction(Command)`.

### Force / Units (battle_army.h) — СТОРОНА
- `Units` = vector<Unit*> + `SortFastest()` (**порядок хода по скорости**) + `FindUID/FindMode` + фильтры.
- `Force` = армия стороны: `isValid()` (**есть живые ⇔ бой продолжается**), **`GetKilledTroops()`**(потери),
  `getTotalNumberOfDeadUnits`, `calculateExperienceBasedOnLosses`, `GetSurrenderCost`, `NewTurn`,
  `syncOriginalArmy()` (записать выживших в армию карты). Держит исходную `Army`+uids.

### Graveyard (battle_grave.h)
map<клетка → мёртвые юниты> — для воскрешения/рисования трупов.

### BattlePathfinder (battle_pathfinding.*) — ДОСТИЖИМОСТЬ
**Дейкстра/BFS** из клетки юнита (`reEvaluateIfNeeded`): очередь узлов; для каждого — `GetAroundIndexes`
(6 соседей); если `isPassableFromAdjacent` → `cost = текущий + 1` (или MOAT_PENALTY в рву, осада);
новый/дешевле → обновить узел {from,cost,distance}, в очередь. Летающий — любая подходящая клетка
(cost 1). Кэш на (старт, скорость, широкий, летающий, цвет, проходимость доски).
`getAllAvailableMoves(unit)` = узлы с `distance ≤ speed` (= подсветка достижимых в этот ход);
`isPositionReachable/getCost/getDistance/buildPath/getClosestReachablePosition`.
(Для skirmish без рва = чистый BFS на глубину `speed` по 6-соседям — моя flood-аппроксимация близка.)

═══════════════════════════════════════════════════════════════════════════════
## 2. АЛГОРИТМЫ

### Поток боя (battle_main.cpp `Battle::Loader`)
```
validate(армии)               // пустая армия → мгновенный Result, без боя (BattleValid ложь)
setup(командиры, seed)
loop:
    arena = Arena(attacker, defender, tile, showInterface)
    while arena.BattleValid():  arena.Turns()        // играть
    result = arena.GetResult()
    if showInterface: arena.FadeArena()              // затемнить поле
    if human: arena.DialogBattleSummary(result)      // ← ФИНАЛ = модал UI
return result   // наружу на карту: убрать проигравшего, опыт, артефакты, syncOriginalArmy
```
- `BattleValid()` = `attacker.isValid() && defender.isValid() && result==0`.

### Раунд (battle_arena.cpp `Turns`) — один раунд = все ходят раз
`++turn` → `RedrawActionNewTurn` (в ЛОГ пишет «Turn N» — НЕ в статус-бар!) → обе силы `NewTurn()`
(сброс TR_MOVED, мораль/удача) → внутренний `while(BattleValid)`:
- `_currentUnit = GetCurrentUnit(...)` — следующий по очереди (макс.скорость среди не-ходивших; порядок
  чередует стороны от цвета прошлого активного);
- (замок: катапульта в ход 1-го атакующего, башни в ход 1-го защитника);
- `UnitTurn` — ход юнита: человек `HumanTurn`→Command, AI→Command → `ApplyAction`. Мораль good →
  ещё ход; bad → пропуск. Удача влияет на урон.
- нет юнитов → раунд кончился.
После раунда: проверка конца → флаги Result + **опыт** = `Σ(hp_монстра × dead)` ВРАГА
(`calculateExperienceBasedOnLosses`), +500 за разбитого героя-врага, +500 осада.
- **Потери** (`GetKilledTroops`) = по юниту `min(initialCount, GetDead())`.
- **Некромантия** raise = `Σ min(initial, dead)` проигравшего (поднимает SKELETON).
- **`syncOriginalArmy`** (пост-бой) = выжившие `maxCount − dead` (или 0) обратно в армию карты — так потери
  сохраняются на карте. `Force::NewTurn` = сброс героя SPELLCASTED + `Unit::NewTurn` всех.

### Атака (battle_action.cpp `ApplyActionAttack` → `BattleProcess`)
```
validate: атакер не TR_MOVED, цель — враг;
          ЛУЧНИК стреляет ТОЛЬКО если НЕ блокирован соседом (isHandFighting) и dst==-1;
          мили — нужна валидная клетка атаки и направление.
moveUnit(attacker, dst)                       // мили сначала идёт вплотную к цели
BattleProcess(attacker → defender):           // одна атака
    цель/направление → повороты → удача → GetTargetsForDamage (цель + сплэш)
    → анимация Part1 → TargetsApplyDamage → Part2 → встроенный спелл атакера → PostAttack
if цель жива:
    if ближний бой И ответка разрешена: BattleProcess(defender → attacker) [ОТВЕТКА, раз/раунд]
    if двойная атака И атакер жив:        BattleProcess(attacker → defender) [ещё раз]
attacker.SetModes(TR_MOVED)                   // ход потрачен
```
- Урон: `GetDamage` = число × dmg(min..max) × модификаторы(атака−защита, бафы). `ApplyDamage` бьёт по
  пулу `_hitPoints`, возвращает killed.

### Конец и потери
- Конец = предикат: одна `Force.isValid()` ложь (нет живых). Тогда `GetResult` (выжившая сторона WINS).
- **Потери = `Force.GetKilledTroops()`** = по каждому исходному отряду его `GetDead()` (= старт − выжило).

### ТОЧНАЯ ФОРМУЛА УРОНА (battle_troop.cpp) — для faithful боёвки
`CalculateDamageUnit(enemy, dmg)` где dmg = число × damageMin/Max монстра:
1. ЛУЧНИК: если НЕ блокирован (стреляет) → бонус Archery героя, штраф стен замка, Shield-спелл;
   если блокирован/мили → **`dmg /= 2`** (штраф ближнего боя, кроме NO_MELEE_PENALTY).
2. blind-ответка ×(100−X)/100; цель окаменена → ÷2; стихийные/анти-нежить → ×2.
3. **`r = GetAttack() − enemy.GetDefense()`; `dmg *= 1 + (r>0 ? 0.1·min(r,20) : 0.05·max(r,−16))`**
   → множитель от ×0.2 (r=−16) до ×3.0 (r≥20). `max(dmg,1)`.
`GetDamage(enemy,rng)` = `random(CalcMin..CalcMax)` (bless→max, curse→min); удача: good ×2 / bad ÷2.
`_applyDamage`: killed = `HowManyWillBeKilled` = (dmg≥`_hitPoints` ? всё : count − count_из_hp(`_hitPoints`−dmg));
`_deadCount += killed`; SetCount. ⚠ HP-ПУЛ, не «полное hp одного».

### ТОЧНАЯ СЕТКА (battle_board.cpp) — гекс 11×9, ряд = «кирпичи»
- `GetDistance(i1,i2)`: `x=i%11,y=i/11`; `du=y2−y1`, `dv=(x2+y2/2)−(x1+y1/2)`;
  одного знака → `max(|du|,|dv|)`; разного → `|du|+|dv|`. (НЕ Чебышёв!)
- `GetIndexDirection(i,dir)` (6 соседей, по чётности ряда y%2):
  TL `i−(нечёт?12:11)`, TR `i−(нечёт?11:10)`, L `i−1`, R `i+1`, BL `i+(нечёт?10:11)`, BR `i+(нечёт?11:12)`.
- `GetReflectDirection`: TL↔BR, TR↔BL, L↔R. `isValidDirection` — края по чётности ряда.
- `GetDirection(i1,i2)` — перебор 6 dir: какой ведёт i1→i2 (или CENTER/UNKNOWN).

═══════════════════════════════════════════════════════════════════════════════
## 3. UI-СЛОЙ (battle_interface.*) — равноправная часть боя

**ПОРЯДОК РЕНДЕРА КАДРА** (battle_interface.cpp):
`fullRedraw`(старт): `_redrawBattleGround`(фон террейна `_battleGroundIcn`→`_mainSurface`) → fade-in.
`Redraw`(каждый кадр): `RedrawPartialStart` = **`RedrawCover`** → **`RedrawArmies`**; затем
`RedrawPartialFinish` = `redrawPreRender`(очередь `_turnOrder` поверх `_mainSurface`, копия в дисплей) →
**`RedrawInterface`**(статус-бар + кнопки Auto/Settings/Skip + popup + лог).
- `RedrawCover` = `_redrawCoverStatic`(сетка `_hexagonGridShadow`, зона хода `_hexagonHighlightShadow`,
  объекты) → мост(осада) → **hover-подсветка**: по типу курсора собрать клетки (ход→клетка / широкий
  head+tail; меч→клетка(и) цели + double/all-adjacent; спелл→область; иначе сама клетка) → на каждую
  блит `_hexagonCursorShadow`. ТРИ тени: grid(сетка) / highlight(зона хода) / cursor(под курсором).
- `RedrawArmies` = отряды `RedrawTroopSprite`+`RedrawTroopCount`, контур текущего (cycling `_contourColor`),
  трупы `RedrawKilled`.

**КУРСОР + СТАТУС** (`GetBattleCursor`, КАЖДЫЙ кадр по наведённой клетке `_currentCellIndex`) — курсор
МЕНЯЕТ форму, статус = соответствующая строка:
- достижимая клетка → «Move %{monster} here» / «Fly … here», курсор `WAR_MOVE`/`WAR_FLY`;
- своя позиция / свой юнит → «View %{monster} info», `WAR_INFO`;
- враг + лучник не блокирован → «Shoot %{monster} (N shots left)», `WAR_ARROW`/`WAR_BROKENARROW`(штраф);
- враг + мили → «Attack %{monster}», курсор-МЕЧ по направлению (8 sword-курсоров);
- **ни на что действенное → «Turn %{turn}», курсор `WAR_NONE`** ← ДЕФОЛТ статуса (НЕ выдумка!).

**ВВОД = КУРСОР-СЕЛЕКТОР** (`MouseLeftClickBoardAction`): клик по доске → Command ПО ТИПУ КУРСОРА:
`WAR_MOVE`/`WAR_FLY`→`MOVE(UID,клетка)`; `SWORD_*`→`ATTACK(UID,цель,клетка-движ[−1 если рядом],клетка,напр)`;
`WAR_ARROW`/`WAR_BROKENARROW`→`ATTACK(UID,цель,−1,клетка,0)` (выстрел); `WAR_INFO`→диалог инфо (без хода).
То есть форму курсора и действие задаёт ОДНА функция `GetBattleCursor` по hover; клик лишь исполняет тему.

**ОТРЯД+СЧЁТЧИК**: спрайт = ICN монстра[кадр], `AlphaBlit`(reflect, alpha); контур активного =
`CreateContour` в cycling `_contourColor`. Счётчик (`RedrawTroopCount`) = полоска `TEXTBAR[GetIndexIndicator]`
в нижнем углу + `abbreviateNumber(count)` smallWhite по центру.

**Виджеты панели**: `_buttonAuto`/`_buttonSettings`/`_buttonSkip`, `Status status` (статус-бар),
`StatusListBox listlog` (лог боя — «Turn N» пишется И сюда через `RedrawActionNewTurn`),
`TurnOrder _turnOrder` (иконки очереди), `PopupDamageInfo popup`, `OpponentSprite` (герои).
**Фон диалогов** `_background` = `StandardWindow`.
**Анимации действий** `RedrawAction*`: Attack(Part1/2), SpellCast, Move, Fly, Missile, Morale, Luck,
Resist, Necromancy, TowerShot, Catapult, NewTurn… + `FadeArena`(затемнение перехода).
**ВСЕ диалоги боя**: `DialogBattleSummary`(итог), `DialogBattleHero`, `DialogBattleSettings`,
`DialogBattleNecromancy`.

**АНИМАЦИИ ДЕЙСТВИЙ (детали)** — на FT812 полную плавность опускаем (уступка), суть сохраняем:
- Атака `RedrawActionAttackPart1`: звук + удача; мили — анимация удара MELEE по относит.Y; лучник —
  угол к цели → анимация стрельбы RANG(TOP/FRONT/BOT) + `RedrawMissileAnimation` (спрайт снаряда летит
  по линии shooter→цель; маг = луч). `Part2`: цель вздрагивает/гибнет `_redrawActionWincesKills`, статус
  **«%{attacker} does %{damage} damage. N creatures perish.»** / «N %{defender} perish.» (реальные строки).
- Движение `RedrawActionMove(unit, path)`: идёт по пути клетка-за-клеткой (анимация MOVING, скорость
  moveSpeed±haste/slow), статус «Moved %{monster}: from [src] to [dst].».
- Прочее `RedrawAction*`: Luck/Morale/Resist/Skip/Necromancy/Tower/Catapult.

**ПЕРЕХОД К ФИНАЛУ** `FadeArena`: reset audio → (очистить статус) → `Redraw`(финал) → `FadeDisplayWithPalette`
(палитра-затемнение области поля в чёрное, 5 шагов) → потом `DialogBattleSummary`. (У меня = Render_BlackFrame.)

**ДИАЛОГ ГЕРОЯ** `DialogBattleHero` (фон `VGENBKG`): портрет + статы (Attack/Defense/Spell Power/Knowledge/
Morale/Luck/Spell Points), 4 кнопки `VIEWGEN`: Cast(9/10)/Retreat(11/12)/Surrender(13/14)/Close(15/16),
дизейбл по условиям (нет книги/нельзя отступить/сдаться). Открывается кликом по портрету героя. Для
безгеройного skirmish НЕ нужен. `DialogBattleSettings`/`DialogBattleNecromancy` — настройки/подъём скелетов.

═══════════════════════════════════════════════════════════════════════════════
## 4. ФИНАЛ — `DialogBattleSummary` (battle_dialogs.cpp:474). Самодостаточный блокирующий модал
Вход: `Result` + артефакты + allowRestart. Рисует раз, крутит анимацию, ждёт OK → возврат.
- Окно = `StandardWindow(335×424)` (углы/верт.края `WINLOSE[0]`, гориз.края `SURDRBKG[0]`, фон `STONEBAK[0]`).
- Регион анимации `WINLOSE[0]{43,32,231,133}` + кадр `WINCMBT`(победа)/`CMBTLOS`(пораж.).
- Заголовок (no-hero): жёлтым «A glorious victory!» / белым «Your forces suffer a bitter defeat.»
  (опыт «For valor…» — только если есть герой).
- Потери: «Battlefield Casualties / Attacker / Defender» + `drawSingleDetailedMonsterLine`(иконка MONS32 +
  число `GetDead()`) или «None».
- Кнопка OK (BOTTOM_CENTER). Подробный чертёж — [[hmm2-battle-winlose-faithful-spec]].

═══════════════════════════════════════════════════════════════════════════════
## 5. ОСАДА / ПРОЧЕЕ (для базового skirmish НЕ нужно, отметить)
`battle_tower`/`battle_catapult`/`battle_bridge` (стены/башни/мост/ров), спеллы (`ApplyActionSpell*`,
TargetsForSpell, ChainLightning, Earthquake, MirrorImage, SummonElemental), `battle_only`(постановка
отдельного боя), `battle_interface_settings`(окно настроек боя), AI-планировщик.

═══════════════════════════════════════════════════════════════════════════════
## 6. ПЕРЕНОС НА МОЙ ПОРТ (FT812/Z80)
- **МОДЕЛЬ** = `battle.asm`: состояние отрядов (HP-ПУЛ, не «N×полное hp»!), доска 99, соседство 6-напр.,
  Command-ы. Конец = `Force.isValid` ложь. Потери = `GetDead()` по отряду.
- **UI** = `Render_Battle` DL + ввод + диалоги. Статус-бар — по hover каждый кадр (НЕ «Turn N»).
  Достижимые клетки — pathfinder BFS (`getAllAvailableMoves`).
- **ФИНАЛ** = ОТДЕЛЬНЫЙ экран/сцена (GameMode), управляемый `Result`+потерями, БЛОКИРУЮЩИЙ; показать =
  войти в сцену с готовым Result (бой не требуется). НЕ покадровый оверлей.
- Аппаратные уступки FT812: looped-анимация → статичный кадр; процедурный StandardWindow → пред-композ.
  спрайт. Текст/раскладка/строки/потери/числа — без отступлений.

### ⚠ ГОЧИ Z80-кода (клоббер регистров — проверено на железе, ловится только эмулятором):
- **`MonsterStats_Read` клоббит BC** (внутри `LD BC,8; LDIR`). В циклах со счётчиком в C — `PUSH BC`/`POP BC`
  вокруг вызова (как `Battle_NextTurn` вокруг `Battle_UnitSpeed`). Иначе бесконечный цикл/зависание.
- **`Battle_UnitAddr` клоббит DE** (`LD DE,BattleUnitState`). Вычисленное значение в DE (потери/count)
  сохранять `PUSH DE`/`POP DE` вокруг вызова. Иначе в память пишется адрес массива (мусор ~0xD027).
- Чтение slot3 (BattleUnitState) СРАЗУ после `MonsterStats_Read` ненадёжно на железе — читать ДО вызова.
- **HP-пул реализован** (`BattleUnitHP`, init=count×maxHP в `Battle_InitHP`, атака hp−=raw/count=ceil(hp/maxHP))
  — проверен на bt8xxemu: P20 20→12→4 (частичный урон копится). N1 закрыт.

═══════════════════════════════════════════════════════════════════════════════
## 7. МОИ ОШИБКИ (исправить по схеме)
1. Транслитерировал реализацию (компоновщик StandardWindow с дизерингом) вместо переноса СУТИ.
2. Финал — ветка в покадровом `Battle_Update` с форсом флага. Надо: отдельная сцена от `Result`.
3. Соседство по Чебышёву (8) вместо гекс-6. → добойщик кликал не туда.
4. HP-модель «урон vs полное hp одного» вместо ОБЩЕГО ПУЛА `_hitPoints`. → «count 2→2» без убыли.
5. Статус-бар: я делал статичный набор строк + «Turn 1» как постоянную подпись, БЕЗ смены курсора и
   пересчёта по hover. На деле (`GetBattleCursor`) статус+КУРСОР считаются каждый кадр по наведению
   (Move/View/Shoot/Attack), а «Turn %{turn}» — РЕАЛЬНЫЙ дефолт статуса (и одновременно лог). Строка
   НЕ выдумана — я зря согласился, что выдумал; ошибка была в реализации, не в тексте.
6. Лучник: не учёл, что блокированный соседом стрелок НЕ стреляет (ближний бой).
7. Мили атакует, СНАЧАЛА подойдя вплотную (`moveUnit`), потом `BattleProcess` + ответка.

═══════════════════════════════════════════════════════════════════════════════
## 8. ДЕТАЛИ (полное изучение — setup, порядок хода, мораль, препятствия, спеллы, осада, AI)

### Расстановка отрядов (`Force` ctor, battle_army.cpp:71)
Слот армии i → клетка `idx = (spread? i*22 : 22 + i*11)`; защитник `idx += (wide?9:10)`; атакующий
широкий `+1`. → атакующий кол.0 (22,33,44,55,66), защитник кол.10 (32,43,54,65,76). Подтверждает наш
layout P40=22/A4=33/P20=32/A2=43.

### Точный порядок хода (`GetCurrentUnit`/`SortFastest`, battle_arena.cpp:169)
- `SortFastest` = `stable_sort` по скорости убыв. (равные — в исходном порядке слотов).
- Фильтр кандидатов: `GetSpeed() > STANDING`. ВАЖНО: `GetSpeed()` у ходившего (TR_MOVED) или
  обездвиженного возвращает STANDING → «не ходил» определяется автоматически, без отд. флага в выборе.
- Берётся быстрейший с каждой стороны; РАВНАЯ скорость → сторона по `preferredColor` (= противоположна
  цвету прошлого активного, чередование); иначе быстрейший. Это НЕ простой раунд-робин.

### Ход юнита + мораль (`UnitTurn`, battle_arena.cpp:460)
Роллит мораль (если подвержен) → действие (AI/человек) → применить. **MORALE_GOOD после хода → ДОП.ХОД**
(команда MORALE true, ходит снова). **MORALE_BAD → ЗАМОРОЗКА** (команда MORALE false, теряет ход).
Удача — на урон (`GetDamage`: good ×2 / bad ÷2). `removeDeadUnits` после каждого действия.

### Препятствия / setup поля (`Arena` ctor, battle_arena.cpp:346)
- ОТКРЫТОЕ ПОЛЕ: случайные препятствия — COVR-декор (40% шанс, по грунту) + `SetCobjObjects` (камни/
  деревья, seed = мапсид+тайл). Блокируют клетки (`Cell._object != 0`). ⚠ У меня поле ПУСТОЕ — упущение
  (для faithful нужны препятствия; для упрощённого skirmish можно без, отметить как уступку).
- ЗАМОК (осада): объекты стен/башен/ворот/катапульты на клетках + башни/катапульта/мост.

### Спеллы (`ApplyActionSpellCast`, battle_action.cpp:412) — ТОЛЬКО с героем
Кастует commander, раз/ход, тратит spell points. Диспетч: TELEPORT/EARTHQUAKE/MIRRORIMAGE/SUMMON —
спец-обработчики; остальные → `_applyActionSpellDefaults`→`GetTargetsForSpell`→`Unit::ApplySpell`
(урон `CalculateSpellDamage`, эффекты через Unit-modes bless/haste/curse/slow/blind/…). Сохраняется
(Eagle Eye). Для безгеройного skirmish спеллов НЕТ. (Per-spell формулы — большая таблица, при нужде.)
- **`Unit::ApplySpell`** диспетч: damage → `_spellApplyDamage`(=`CalculateSpellDamage`→`_applyDamage`, та же
  HP-пул убыль); restore/resurrect → `_spellRestoreAction` (CURE: −дебафы+HP cap; RESURRECT/ANIMATEDEAD:
  поднять мёртвых из graveyard, «N rise from the dead!», RESURRECT временно); иначе → `_spellModesAction`
  (баф/дебаф с длительностью=база+артефакт; противоположности ЗАМЕНЯЮТ: BLESS↔CURSE/HASTE↔SLOW/
  STONESKIN↔STEELSKIN/BERSERKER↔HYPNOTIZE; BLOODLUST=3 фикс; DISPEL/ANTIMAGIC снимают магию).
- Эффекты влияют на бой через modes: haste→+скорость, bless→макс-урон, curse→мин, shield→стрельба÷, 
  stoneskin/steelskin→+защита, blind/paralyze/stone→обездвижен, berserker→бьёт любого, hypnotize→сменил сторону.
- Длительность −1/ход (`ModesAffected::DecreaseDuration` в `NewTurn`); 0 → снять. Магорезист `GetMagicResist`.
- **Цели** (`GetTargetsForSpell`): single (юнит dst); resurrect (мёртвый из graveyard); CHAINLIGHTNING
  (отскок с убылью урона); FIREBALL/COLDRING/FIREBLAST (площадь rad 1-2); MASS*/HOLYWORD/ARMAGEDDON (ВСЯ
  доска, фильтр `AllowApplySpell`: holy→нежить, mass-bless→свои). Резист-цели отсеиваются (`RedrawActionResistSpell`).

### NewTurn (каждый раунд, `Unit::NewTurn`/`Force::NewTurn`)
Реген HP (троллю); сброс TR_RETALIATED/MOVED/SKIP + LUCK/MORALE good/bad; `DecreaseDuration` эффектов,
истёкшие снять (mirror-owner → убить копию).

### Команды (`battle_command.cpp`)
`Command` = вектор<int> (LIFO: `<<` push / `>>` pop с конца, ctor реверсит). `updatePCG32Stream` —
детерминированный сдвиг RNG-потока (реплей/мультиплеер; для базового порта не нужен).

### Осада (только при замке)
- `TowerAction`: башня бьёт цель с макс. угрозой (`evaluateThreatForUnit`) → TOWER-команда. Не двигается.
- `CatapultAction`: N выстрелов по стенам/башням/мосту (цель+урон+попадание) → CATAPULT-команда.

### AI боя (`AI::BattlePlanner`, ai/ai_battle.cpp) — для vs-computer (изучено подробно)
**`BattleTurn`** → лимит 50 ходов без смертей (auto-off / retreat) → **`planUnitTurn`**:
1. Берсерк → `berserkTurn` (бить ближайшего любой стороны).
2. **`analyzeBattleState`**: суммы `GetStrength()` my/enemy (армия/стрелки/ср.скорость, взвеш. по силе);
   флаги: `_avoidStackingUnits`(area-атака врага >10%), `_considerRetreat`(были потери ИЛИ <4 отрядов),
   `_defensiveTactics`(оборона замка с башнями), `_cautiousOffensive`.
3. Ретрит/сдача (герой): моя_сила×коэф(сложность) ≥ вражеская → биться; иначе оценить артефакты/
   возможность сдаться(золото)/перенайма → RETREAT/SURRENDER (+ прощальный макс-урон спелл).
4. **Спелл героя** `selectBestSpell` (оценка ценности: damage/dispel/resurrect/summon/effect) → SPELLCAST.
5. **Действие отряда**:
   - СТРЕЛОК `archerDecision`: если враг-мили подходит — КАЙТИНГ (уйти на клетку без соседства с врагом;
     в упор стрелять нельзя; от летающих не убежать); иначе стрелять лучшую цель.
   - МИЛИ: `_defensiveTactics`? `meleeUnitDefense`(держать защищённую зону) : `meleeUnitOffense`:
     (а) цель в досягаемости → `getMeleeBestOutcome` (атаковать лучшего: ценность атаки + безопасность
     позиции `evaluatePotentialAttackPositions`); (б) нет → дальняя цель по `угроза/дистанция` (сначала
     кто не убежит: стрелки/обездвиженные/медленные), идти к ней (`path.back`, `optimalAttackVector`).
   - Иначе SKIP.
Базовая метрика — `Unit::GetStrength()` (боевая мощь) и `evaluateThreatForUnit` (урон÷дистанция).
- Скоринг мили (`MeleeAttackOutcome`/`BestAttackOutcome`/`evaluatePotentialAttackPositions`): приоритет
  ударить-сейчас > безопасность позиции > угроза врага; позиции у нескольких врагов — сумма для блокировки
  стрелков. `optimalAttackVector` — лучшая клетка+направление. `findOptimalPositionForSubsequentAttack` —
  безопаснейшая на пути (cautious).
- `meleeUnitDefense`: прикрыть СВОИХ стрелков (встать рядом, блокируя вражеский мили; штраф дистанции
  `_myRangedUnitsOnly/15` за тайл; широкие кроют с боку). `berserkTurn`: бить БЛИЖАЙШЕГО любой стороны.
- `selectBestSpell` (ai_battle_spell.cpp): порог = `моя_сила²/вражеская·0.04` (беречь очки при перевесе),
  ценность спелла по типу (damage/dispel/summon/resurrect/effect) ÷ `sqrt(стоимость/3)`; лучший выше порога.
Для player-vs-player skirmish AI не нужен; для vs-computer — переносить упрощённо (порог-эвристики).

═══════════════════════════════════════════════════════════════════════════════
## 9. ТОНКИЕ ДЕТАЛИ (геометрия, рендер поля, препятствия, тени)

### Геометрия клетки (`Cell::SetArea`, battle_cell.cpp:256) — ПИКСЕЛЬ-ТОЧНО = мой layout
`_pos.x = areaX + 89 − (нечёт.ряд? 44/2 : 0) + 44·col`; `_pos.y = areaY + 62 + 42·row`
(widthPx=44, heightPx=52, cellHeightVerSide=32, шаг = 52−(52−32)/2 = 42). 7 вершин `_coord[0..6]` =
центр + 6 углов гекса (масштаб `infl` для sub-pixel).

### Направление атаки от курсора (`Cell::GetTriangleDirection`)
Точка курсора в клетке врага → какой из 8 треугольников (центр→две соседние вершины) = AttackDirection
(TOP_LEFT/TOP/TOP_RIGHT/RIGHT/BOTTOM_RIGHT/BOTTOM/BOTTOM_LEFT/LEFT). ГДЕ навёл в клетке → с какой
стороны бьёшь и в какую соседнюю встаёшь. (Мили-направление.)

### 5 гекс-картинок (тени/сетка)
`_hexagonGrid`(контур сетки, в `_battleGround` если опция `BattleShowGrid`), `_hexagonShadow`/
`_hexagonGridShadow`(тень ЗОНЫ ХОДА текущего, выбор по grid-опции), `_hexagonHighlightShadow`(зона врага,
блит ×2), `_hexagonCursorShadow`(под курсором, hover). Зона хода = для каждой клетки `GetReachable`≠null.

### Рендер поля (`_redrawBattleGround` → `_battleGround` один раз)
террейн CBKG[ground] → бордюр FRNG (лево/право) → большой COVR-обстакл → (замок: CASTBKG[race]+ров
MOATWHOL) → сетка (опция) → наземные препятствия `_redrawGroundObjects` → (стена замка). Высокие
препятствия и трупы — per-frame в `_mainSurface` (z-порядок: юниты за деревьями).

### Препятствия = COBJ (`cell._object` 0x80-0x9F → ICN COBJ0000-0031)
- `_redrawHighObjects`: 0x80-0x9D → COBJ0000-0029 (высокие: деревья/камни, юнит может быть за ними).
- `_redrawGroundObjects`: 0x90/0x9E/0x9F → COBJ0016/0030/0031 (наземные, под юнитом).
- Генерация (`SetCobjObjects`): пул по ГРУНТУ (Grass: COBJ 0002/0004/0005/0008/0011/0012/0014/0015/0019/
  0027/0028; Desert/Snow/Swamp/Beach/Dirt/Wasteland/Lava/Water — свои; Graveyard-тайл — особый), shuffle,
  число = random(0..maxSmall=6/4/3/2 по числу больших COVR), правила (свободно, two-hex не на кол.8,
  высокие не в верх.2 рядах). `cell._object = 0x80 + (icn−COBJ0000)`.
- ⚠ Моё поле ПУСТОЕ (без COBJ). Для faithful — генерить препятствия; упрощённо — отметить уступку.

### Статус-бар = ДВЕ строки (`Status`, battle_interface.cpp:1138)
Верх `_upperBackground`=TEXTBAR[8], низ `_lowerBackground`=TEXTBAR[9], текст normalWhite по центру.
`setMessage(msg, top=true)` → ВЕРХ (события боя «X does Y damage», +в лог `listlog`); `top=false` → НИЗ
(hover-подсказка Move/Attack/Shoot/Turn, не логируется, только если изменилась). ⚠ У меня ОДНА строка.

### Цвет полоски счётчика (`GetIndexIndicator`)
По магии отряда: нет магии → ФИОЛЕТОВЫЙ TEXTBAR[10]; баф → ЗЕЛЁНЫЙ[12]; дебаф → КРАСНЫЙ[14]; оба → ЖЁЛТЫЙ[13].
Без героя (нет спеллов) — всегда фиолетовый [10]. Кнопки панели: Skip=TEXTBAR[0/1], Auto[4/5], Settings[6/7].

### Постановка отдельного боя (`Battle::Only`, battle_only.cpp)
2 армии (дефолт army0=HUMAN vs army1=AI). `setup`=конфигуратор (control human/AI, герой?, монстры, террейн).
`StartBattle`: нет героя → берётся monster-армия → `Battle::Loader(army0, army1, tile)`. Это режим Battle-Only.

### Формула урона заклинания (`CalculateSpellDamage`)
`dmg = spell.Damage() · spellPower` → модификаторы (сопротивления/слабости монстра: снижение % или ×2
fire/cold-слабость; артефакты атакующего/защитника ±%). Спелл-эффекты — через Unit-modes на N ходов.

### ТАБЛИЦА СПЕЛЛОВ (`spell.cpp` `spells[]`: {name, SP, movePts, minMove, imageId, extraValue, desc})
`extraValue` = урон (damage) / магнитуда эффекта / HP-восст / число воскрешения. SP = стоимость.
Боевые (SP / extraValue): Fireball 9/10, Fireblast 15/10, Lightning 7/25, ChainLightning 15/40,
MagicArrow 3/10, HolyWord 9/10, HolyShout 12/20, Armageddon 20/50, ElementalStorm 15/25, MeteorShower
15/25, ColdRay 6/20, ColdRing 9/10, DeathRipple 6/5, DeathWave 10/10. Лечение/воскр: Cure 6/5(HP/power),
MassCure 15/5, Resurrect 12/50(врем.), ResurrectTrue 15/50, AnimateDead 10/50. Эффекты: Haste 3/+2speed,
MassHaste 10/+2, Slow 3, MassSlow 15, Bless 3, MassBless 12, Curse 3, MassCurse 12, Blind 6/50%(сниж.ответки),
Stoneskin 3/+3def, Steelskin 6/+5def, BloodLust 3/+3atk, DragonSlayer 6/+5, Shield 3(стрельба÷2), MassShield 7,
DisruptingRay 7/−3def, AntiMagic 7, Dispel 5, MassDispel 12, Berserker 12, Hypnotize 15/25, Paralyze 9,
Petrify 0, MirrorImage 25, Earthquake 15(стены), Summon*Element 30/3. Для безгеройного skirmish не нужно.

### Оценка угрозы (`evaluateThreatForUnit`) — выбор цели AI/башней
`threat = getPotentialDamage(defender)` [=avg(min,max) урон] ÷ distMod (летающий/стрелок/в радиусе
speed+1 → 1.0; дальше → 1.5·dist/speed). Двойная атака — минус ожидаемая ответка. Башня/AI берут макс.

### BIN-анимация монстра (`AnimationReference`, battle_animation.cpp)
Состояния → последовательности кадров из BIN (`Bin_Info::MonsterAnimInfo`): STATIC, WINCE(вздрагивание),
DEATH, IDLE(неск.), MOVING(MOVE_TILE_START+MAIN+END=цикл ходьбы), MELEE_FRONT/TOP/BOT, RANG_*.
`GetMonsterSprite()`+`GetFrame()` → текущий ICN-кадр. На FT812 анимация — уступка (статичная стойка [1]).

═══════════════════════════════════════════════════════════════════════════════
## 10. УЧЁТ ПОЛНОТЫ (что прочитано построчно, что — нет)
ПРОЧИТАНО построчно (структура+алгоритм+leaf): модель (Unit/Cell/Board/Command/Force/Graveyard/Pathfinder),
бой+формула урона, ход/мораль/удача/NewTurn, сетка(дистанция/направление/адъясенси), pathfinder, поток
Loader+пост-бой, UI (рендер-путь/курсор-ввод/cover/3 тени/отряды/счётчики/геометрия/препятствия/статус-2-строки/
fade/финал/диалог героя), setup+расстановка+генерация препятствий, СПЕЛЛЫ (cast/dispatch/modes/damage/restore/
targeting/спец-обработчики), осада (tower/catapult actions), AI ПОЛНОСТЬЮ (дерево/анализ/скоринг мили/
оборона/берсерк/выбор спелла), команды, BIN-анимация.
ПРОЧИТАНО ТАКЖЕ (геро/визуал): каст-анимация (`redrawActionSpellCastPart1` — герой жест OP_CAST_UP/DOWN/MASS
+ per-spell эффект-ICN: FIREBALL→FIREBALL, METEOR→METEOR, MASSCURE→MAGIC01, BLESS→BLESS, BLIND→BLIND…),
спрайт героя (`OpponentSprite` — ICN по расе + STATIC/CAST + флаг HEROFL по цвету), плееры Morale/Luck.
ОСТАЛИСЬ непрочитанными лишь ТЕЛА однотипных плееров (`RedrawActionFly/Resist/Necromancy/Tower` +
кастомные эффект-функции `_redrawAction{ColdRing,DeathWave,HolyShout,ElementalStorm,Armageddon,Resurrect}Spell`)
— паттерн идентичен (статус-строка + эффект-ICN/звук), и gettext-описания спеллов. На архитектуру не влияют.

### Faithful-строки боевых событий (верхняя строка статуса + лог)
Атака: «%{attacker} does %{damage} damage.» + «1 creature perishes.»/«%{count} creatures perish.»/
«%{count} %{defender} perish.». Движение: «Moved %{monster}: from [%{src}] to [%{dst}].». Мораль:
«High morale enables the %{monster} to attack again.»/«Low morale causes the %{monster} to freeze in panic.».
Удача: «Good luck shines on the %{attacker}.»/«Bad luck descends on the %{attacker}.». Скип:
«The %{name} skips their turn.». Воскрешение: «%{count} %{name} rise from the dead!». Раунд (лог): «Turn %{turn}».
