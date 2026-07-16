# HMM2 VDAC2 — adventure UI: дефекты vs OpenHMM2 + план доводки

Источник: автономный workflow-аудит (7 агентов, OpenHMM2 эталон ↔ наш render.asm/generated_objects.inc/game_state.asm).
**ВНИМАНИЕ:** аудит — ориентир, не истина. Часть конкретики агенты галлюцинируют (пример: «золото
улетает в x+1920» неверно — `B=6 AND 3 = 2`, золото на col2 в панели). КАЖДУЮ правку проверять по
реальному коду + кадру эмулятора перед коммитом. Всё по OpenHMM2, кроме honest hardware-лимитов (см.
[hardware_limitations_ui.md](hardware_limitations_ui.md)).

Геометрия: логические 640×480, FT812 ×1.6 → 1024×768. Радар 144×144 @ (480,16). Бордюр 16, тайл 32.

## Статус правок (ведётся по ходу)
- [x] **hero-иконка посажена в ячейку 0** (render.asm UI_RightPanel_DL): была (488,168) → стала
  PORTXTRA(485,181)+MINIPORT(493,181)+MOBILITY(485,181). ПРОВЕРЕНО кадром (panel_after.png).
- [x] **КУРСОР починен** (был невидим всегда): RAM_G #0E0000 попадал внутрь object atlas → Objects_Upload
  затирал. База курсора → #0E8000 (viewport_pack.py). build verify зелёный, подтверждено на реале.
- [x] **Статус-окно kingdom-вид ПО ОРИГИНАЛУ** (проверено на железе): STONBACK каменный фон +
  RESSMALL иконки (замок/город/золото + 6 ресурсов) + числа на позициях оригинала (gold 602,422;
  ресурсы x=495/517/540/564/588/610, y=452). РЕШЕНИЕ бюджета: STONBACK+RESSMALL (×1.6) собраны в
  RAM_G-композите Resources_BuildPanelDL через статический блоб UI_StatusBg_DL (Render_CmdBufCopy),
  НЕ в покадровый DL (бюджет 4096 цел). Core переполнялся — освободил место удалением неиспользуемых
  ResColOffsets/ResRowOffsets/ResCellX/Y/ResBaseX/Y. build verify зелёный.
  ОСТАЛОСЬ по статусу: числа замков/городов (нужен GetCountCastle/Town), центрирование чисел (x−w/2),
  виды DATE/ARMY + переключение кликом.
- [x] **Статус-окно ПЕРЕКЛЮЧЕНИЕ ВИДОВ (как оригинал NextState)**: клик по статус-окну циклит
  DATE↔FUNDS (UI_DispatchClick → зона [480..624)×[392..464) → StatusState++ → пересборка композита).
  Дефолт DATE (как оригинал). DATE = STONBACK + баннер солнца SUNMOON + счётчик дня (центрирован).
  FUNDS = STONBACK + RESSMALL + замок/город/золото + 6 ресурсов, ВСЁ ЦЕНТРИРОВАНО (Render_Number16C,
  ≈x−width/2). ПРОВЕРЕНО кадром (funds_centered.png: 1/0/7500 + 20/5/20/5/5/5 под иконками; date_view.png).
  Бюджет: освободил Core (мёртвый resource-icon код), DL-staging → #AF00 (+256Б резиденту).
  ОБНОВЛЕНО: DATE теперь ТЕКСТОМ как оригинал — «Month: M Week: W» + «Day: D», шрифт SMALFONT
  (метки-спрайты из viewport_pack smalfont_label), день/неделя/месяц вычисляются из GameDay (div7/mod4).
  Проверено date_text.png. Хелпер Render_Number16C (центрирование). Core: DL-staging → #AF80.
- [x] **Статус-окно ВИД ARMY (ДЕФОЛТ, как оригинал)** — ПОДТВЕРЖДЕНО кадром реального bt8xxemu
  (Diagnostics/army_real.png). SKIRMISH.MX2 героев НЕ содержит (распарсил MP2-блоки по эталону
  world_loadmap.cpp: замки Knight@(24,13)+Sorc@(9,22), 0 hero-блоков). Армию стартового героя движок
  генерит сам: Army::Reset(true)+getNumberOfMonstersInStartingArmy → Knight = Peasant(30-50)+Archer(3-5).
  Реализация: в RAM_G грузим РОВНО типы из армии (2 спрайта MONS32, индекс=MP2-тип), viewport_pack
  HERO_ARMY=[(0,40),(1,4)]; render.asm UI_StatusArmy_DL (STONBACK+2 спрайта ×1.6) + .nums_army (счётчики
  центрированы). Дефолт StatusState=STATUS_ARMY (game_state.asm), цикл клика 3 вида (FUNDS/DATE/ARMY).
  Парсер Source/Tools/dump_mp2_armies.py — универсальный (любой MP2/MX2).
  ОСТАЛОСЬ по ARMY: счётчики у оригинала рандомные (взяты представительные 40/4); раскладка 2 стеков —
  фигура слева в 32px-боксе, число под центром бокса (минорно). Реальные счётчики замков/городов —
  когда появится kingdom-учёт (сейчас стаб 1/0). Оригинал (interface_status.cpp)
  = многосекционная панель: DATE (солнце/луна + Month/Week/Day) + KINGDOM (RESSMALL: иконки замок/город/золото
  + 7 ресурсов; числа на x+15/37/60/84/108/130, castle x+26/town x+78/gold x+122) + ARMY (войска фокус-героя),
  переключение кликом (DAY→FUNDS→ARMY). Наш — грубая сетка 7 больших иконок на чёрном.
  **БЛОКЕР:** STONBACK(144×72)+RESSMALL(133×56) в per-frame DL переполняют CMD-FIFO 4096 (ASSERT). РЕШЕНИЕ:
  строить STONBACK+RESSMALL+числа в RAM_G-КОМПОЗИТЕ Resources_BuildPanelDL (аппендится 1 командой, кадровый
  бюджет не растит) со СМЕНОЙ масштаба внутри (STONBACK/RESSMALL ×1.6, числа native) — аккуратная задача,
  отдельным заходом. Ассеты STONBACK/RESSMALL уже знаем как извлечь (viewport_pack append_paletted_sprite).
  ВНИМАНИЕ: в существующем коде композита трансформ помечен «TRANSFORM_E» опкодом #1700 (это TRANSFORM_C!);
  для ×1.6 ставить A=#15 и E=#19 правильными опкодами.
- [ ] Циклы статус-окна Day/Army (нужен буквенный шрифт для даты + войска).
- [ ] LOCATORS-фон пустых ячеек; список из неск. героев/замков.

## Волна сверки с оригиналом (2026-06-22): мультиагентный аудит (8 элементов, 27 расхождений)
Полный аудит adventure-UI ↔ fheroes2 с точными значениями. ИСТОЧНИК ИСТИНЫ перечитан напрямую
(interface_status.cpp, army.cpp/army_ui_helper.cpp drawMiniMonsters, interface_icons/buttons/radar.cpp,
kingdom.cpp). Ключевое: МНОГОЕ уже верно (ARMY-источник, FUNDS пиксель-точны, DATE-математика/позиции,
геометрия рамки, радар-грунты, порядок кнопок).

### СДЕЛАНО + ПРОВЕРЕНО кадром реального bt8xxemu (Diagnostics/wave1_army.png):
- **ARMY пиксель-точно** по drawMiniMonsters(compact): chunk=46, cy=409; Peasant chunk@507 (box vertex 515,417),
  Archer chunk@553 (vertex 562,415); числа правым краем чанка центр 538/587 y=432; общий baseline y=446.
- **Порядок цикла** ARMY→DATE→FUNDS→ARMY (NextStatus при фокус-герое): EQU STATUS_ARMY=0/DATE=1/FUNDS=2, дефолт ARMY.
- **Радар: точка героя** = палитра владельца RED 0xBD=RGB(168,32,32) (было 255,48,48).
- **Рамка: OPAQUE-палитра** (border_blits → OBJECT_OPAQUE_PALETTE_RAMG): чёрная тень рамки больше не «дыры».
- **MINIPORT** инсет +7 (492 vs 493) по heroes.cpp barw=7.
- Подтверждено уже-верным: FUNDS X{495,517,540,564,588,610}y452 + gold602/castle506/town558 y422; DATE y424/440 центр.

### ОСТАТОК (план аудита, по приоритету) — ГЕЙТ: RAM_G почти полон (атлас→#0E7512, курсор #0E8000, своб. ~2.7КБ).
Асет-ёмкие фиксы требуют реорганизации RAM_G (поднять базу курсора / уплотнить атлас) — отдельной волной:
- **rank4 DATE SUNMOON по дню** (icnId=(dow>1)?0:((week-1)%4)+1; старт day1→0 уже верно): нужны 5 кадров SUNMOON (~18КБ RAM_G).
- **rank8-10 список героев/замков**: 4 слота×2 колонки (герои X485 / замки X557, шаг Y32), пустые=LOCATORS[1+i%8] 46×22,
  cyan-маркер RGB(160,224,224) 56×32 на фокусе. Нужны LOCATORS(8 кадров ~8КБ)+PORT_SMALL+иконка замка(drawCastleIcon).
- **rank11/19/20 радар: точки объектов** (замки/шахты=цвет владельца 0x47/5D/BD/70/CA/87; артефакт/ресурс=GRAY 0x10): нужен список объектов+владельцы.
- **rank12-16 state-машины кнопок** (NextHero/Spell enable/disable; HeroMovement action 16/17 / inactive 18/19): нужны ADVBTNS 16-19 + данные героя (ходы/книга).
- **rank17-18 DATE**: «Day:» крупным normalWhite; истинное центрирование по ширине строки.
- **rank21** фокус-зависимый дефолт (герой→ARMY, замок→FUNDS, пусто→DATE) — при появлении переключения фокуса.
- **rank23** аббревиатура больших чисел (≥1000→NK) — не нужна на старте (40/4).
HW-лимиты (НЕ чинить): dimming disabled-кнопок и MANA-бар в списке опущены ради CMD-FIFO 4096; Quit невозможен (нет сброса TS-Config).

## Быстрые победы (дёшево + заметно) — ПРОВЕРИТЬ каждую по коду
1. Сетка ресурсов: верх 4 (wood/mercury/ore/sulfur), низ 3 (crystal/gems/gold). ПРОВЕРИТЬ: возможно уже верно (col=B AND 3, row=B>>2 → gold col2). render.asm Resources_BuildPanelDL ~2146-2219.
2. Снять `+2` смещение статус-панели (render.asm ~2140,2143) — если реально не совпадает с рамкой.
3. Заливка фона панели x=480..624 (убрать чёрные дыры) — СНАЧАЛА проверить, где реально чёрное (радар-туман и тёмные ячейки LOCATORS могут быть нормой). Фон по оригиналу = текстура ADVBORD, не плоский цвет.
4. Палитра рамки: generated_objects.inc:325 OBJECT_PALETTE_RAMG → отдельная палитра ADVBORD (нужен экстрактор).
5. Инициализация радара при Adventure_Enter (Minimap_BuildFull) — если радар реально пуст (но туман = чёрное это норма).
6. Цвет квадрата героя по игроку (render.asm ~1923) вместо хардкода #FF3030 — для красного игрока и так верно.
7. State кнопок NextHero(0)/Spell(3): disabled по условиям (game_state.asm ~202-234).
8. Переставить hero cards после блока рамки (generated_objects.inc) — если рамка их перекрывает.

## Крупные подсистемы (новые модули + ассеты, НЕ quick-win)
- **Список героев/замков** (icons): 2 колонки 56×32, скроллбар, портреты PORT_SMALL + иконки замков в RAM_G,
  хит-тест/выбор. Сейчас рисуется лишь 1 карточка героя. Самый большой пробел.
- **Статус-окно циклами** Day/Kingdom/Army/Resource по клику (сейчас только полоса ресурсов).
- **Полные state-машины кнопок** (HeroMovement move/action/inactive, NextHero, Spell).
- **Радар: типы объектов** (замки/герои/шахты/ресурсы цветом игрока; грунт по GetPaletteIndexFromGround).

## ВАЖНАЯ находка (проверено кадром): «карточка героя» посажена не туда
Кроп `Diagnostics/herocard_zoom.png`: в зоне списка (логич. ~488,168) рисуется hero-quick-info —
портрет MINIPORT + жёлтая полоса MOBILITY с «плюсами» (слева) + синяя полоса (справа), полосы выше
портрета и налезают. НО в OpenHMM2 `redrawHeroesIcon` = ТОЛЬКО `PortraitRedraw(PORT_SMALL)` — в списке
НЕТ полос mobility/mana. Полосы mobility/spell-points — это hero-display СТАТУС-окна (Y=392+), при фокусе
на героя. Значит наш `UI_RightPanel_DL` (render.asm:1744) — это контент статус-окна, ошибочно посаженный
в зону икон (Y=168). РЕШЕНИЕ (требует дизайна, не вслепую):
- В списке икон (cells X=480/552, Y=176+) рисовать чистые портреты PORT_SMALL (нужен ассет PORT_SMALL ~ размера ячейки 46×22 контент).
- hero-quick-info (портрет+mobility+mana+армия) перенести в СТАТУС-окно (Y=392), показывать при фокусе.
- Интерьеры пустых ячеек сейчас ЧЁРНЫЕ — в оригинале фон ADVBORD/спрайт LOCATORS[1+i%8]. Нужен ассет LOCATORS.
Размеры наших ассетов (MINIPORT 30×22 аним / MOBILITY 7×22) НЕ совпадают с PORT_SMALL оригинала — нужна ревизия ассетов.

## Детали по подсистемам (из аудита)
### radar
Эталон: 144×144 @ (480,16). RedrawObjects заполняет 8-bit карту: hero→цвет игрока, mine/sawmill→цвет владельца,
artifact/resource→GRAY 0x10, замок→цвет замка, грунт→GetPaletteIndexFromGround (горы/лес +3). Viewport-rect
solid цвет 0xB5 RGB(216,124,124). Наш: UI_RADAR_RAMG #0D7848, hero-dot хардкод #FF3030, рисунок по разведке
(Minimap_RevealTile). Пробел: типы объектов, цвет игрока, инициализация при входе.

### icons (heroes/castles)
Эталон: ячейка-курсор 56×32, контент 46×22, 2 колонки (герои x+0, замки x+72), портрет @(ox+5,oy+5),
шаг 32px, скроллбар @(x+59,y+19) h=32*N-38, пустые ячейки LOCATORS[1+i%8], маркер выбора cyan 0xA0E0E0.
Наш: только Render_RightPanelCmd рисует 1 карточку (PORTXTRA 488,168 + MINIPORT 493,173 + MOBILITY). Список отсутствует.

### status
Эталон: 144×72 @ (480,392), 4 состояния (Day/Funds/Army/Resource) по клику, фон STONBACK. Наш:
Resources_BuildPanelDL — только 7 ресурсов сеткой, фон чёрный, без циклов. Константы UI_STATUS_X=480,Y=392,W=144,H=72.

### buttons
Эталон: 2×4 @ (480,320..392), 36×36, ADVBTNS пары; state-машины (HeroMovement move/action/inactive/disabled,
NextHero/Spell по условиям). Наш: 8 кнопок, состояния 0/1/2/3/4 в UI_ButtonStates(#4274), pressed работает;
неполны state-машины; нет затемнения disabled (hw-лимит CMD-FIFO).

### border
Эталон: ADVBORD рамка по периметру + ICON-border @ y=160; фон панели заполнен. Наш: AdventureUI_DL рисует
рамку пьесами + 4+4 ячейки + радар, но PALETTE_SOURCE рамки = OBJECT_PALETTE_RAMG (возможно неверные цвета),
возможны незаполненные участки. Проверить визуально.

### cpanel
Эталон: 5-зонная toggle-панель (radar/icons/buttons/status/end). У нас заменена 8-кнопочной сеткой —
осознанная адаптация, не баг (задокументировать).
