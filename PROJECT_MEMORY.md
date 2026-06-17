# Память проекта HMM2 TS-Config / VDAC2

## Architecture 2026-06-13: project-agnostic Z80/TS-Config/FT812 simulator

После повторных регрессий со scroll нельзя считать достаточными тесты,
подогнанные под HMM2. Harness переведен на общий слой:

- `Source\Tools\tsconf_ft812_sim.py` — независимый simulator:
  Z80 call/step, TS-Config 16K paging/FMADDR, SPG block loader, DMA_RAM_SPI,
  FT812 SPI, RAM_G/RAM_DL/RAM_CMD и базовый CMD_DLSTART/CMD_APPEND;
- `Source\Tools\_z80_lib_cburbridge\src\z80\*.py` — локальный Z80 core,
  больше нет обязательного импорта из соседнего проекта Zuma;
- `Source\Tools\shadow_ft812.py` теперь локальная модель DL-регистров и
  disasm, без wrapper на Zuma; CMD FIFO `0x302578..0x303577` специально
  пропускается в simulator, иначе co-processor поток не исполняется;
- `Source\Tools\hmm2_ft812_snapshot.py` использует тонкий
  `HMM2FullZ80Emulator(TSConfFT812Machine)`: HMM2 задает только root,
  `spgbld_vdac2.ini`, `Build\hmm2.sym` и стартовое состояние мыши.

Новый обязательный базовый тест перед сдачей изменений в низком уровне:

```text
python -u Source\Tools\test_tsconf_ft812_sim_contract.py
```

Он не импортирует HMM2 и проверяет контракт железного слоя: SPG crossing page,
TS-Config bank mapping/FMADDR gate, FT812 SPI read/write, DMA_RAM_SPI,
CMD_APPEND в RAM_DL, а также то, что `call()` не затирает Z80-регистры, если
они не переданы явно.

Проверено после выноса:

```text
.\build.cmd
python -u Source\Tools\test_tsconf_ft812_sim_contract.py
python -u Source\Tools\test_sprite_scroll_sync.py
python -u Source\Tools\test_background_scroll_monotonic.py
python -u Source\Tools\test_viewport_scroll.py
python -u Source\Tools\test_path_overlay.py
python -u Source\Tools\test_hero_command.py
python -u Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\abstract_sim_current_000.png
python -u Source\Tools\hmm2_ft812_snapshot.py --scroll-right-frames 40 --out Diagnostics\abstract_sim_current_040.png
```

Snapshot hashes differ, so full-stack snapshot scroll is not frozen:

```text
Diagnostics\abstract_sim_current_000.png
4701403361C96D3349620519978D4092B7472BD9139AD9BA9A0CD33B281FADEC

Diagnostics\abstract_sim_current_040.png
0A1628600F74AF715DC47FA5844E5E3C04480C7D2E0719499A7217BEBE23C37A
```

## Fix 2026-06-13: scroll спрайтов и фона без фазового разрыва на origin boundary

Предыдущая запись про scroll была неполной: старый тест проверял только простые
переходы и не ловил главный разрыв на `ViewportPixelX 31->32` / `63->64`, когда
меняется `ViewportOriginX`.

Фактическая причина: при upscale `8/5` нельзя сбрасывать координаты в
origin-local фазу. `32 * 8/5 = 51.2`, поэтому `floor(local * 128/5)` и
`floor(world * 128/5) - floor(viewport * 128/5)` дают разную фазу на границе
origin. Симптом в DL-тесте был виден как центральный object mismatch
`#041494@7783` против `#041494@7782` на `31->32`.

Исправление:

- terrain tiles переведены в world-space: компактная таблица
  `Assets\Converted\Maps\SKIRMISH_RUNTIME_CELLS.bin`, page `#87`, `8214` байт;
- `MapTerrainCells` больше не лежит в Core: runtime временно мапит
  `MAP_TERRAIN_CELLS_PAGE` в slot3, собирает `RUNTIME_DL_BUFFER`, затем
  восстанавливает page;
- `MAP_TERRAIN_CELL_ENTRY_SIZE=6`: 2 байта handle/cell + 4 байта world-space
  `FT_VERTEX2F`;
- `RuntimeDL_TranslateX/Y` теперь считает полный
  `GAME_VIEW_X16/Y16 - scale(ViewportPixelX/Y)`, а не только `ViewportPixel & 31`;
- object-view DL генерируется в world-space координатах, но клиппинг остается
  origin-local;
- hero/actor/route sprites в runtime-ветке также масштабируются от world pixel и
  получают тот же общий translate;
- scale LUT расширен до `0..2047` (`Build\scale8_5_x16.bin`, 4096 байт);
- `test_sprite_scroll_sync.py` теперь проверяет terrain layer, object layer,
  hero и cursor на `0->5`, `31->32`, `32->33`, `63->64`; нормальный вход/выход
  крайнего тайла/спрайта у scissor разрешается, центральный фазовый разрыв
  остается fatal.

Проверено:

```text
.\build.cmd
python -u Source\Tools\test_sprite_scroll_sync.py
python -u Source\Tools\test_background_scroll_monotonic.py
python -u Source\Tools\test_path_overlay.py
python -u Source\Tools\test_viewport_scroll.py
python -u Source\Tools\hmm2_ft812_snapshot.py --viewport-x 31 --out Diagnostics\scroll_sync_x31.png
python -u Source\Tools\hmm2_ft812_snapshot.py --viewport-x 32 --out Diagnostics\scroll_sync_x32.png
```

Состояние проверки:

```text
build: sjasmplus 0 errors, 0 warnings; RAM_G/RAM_DL calculator OK
Core split: p05=12288 bytes, p06=2185 bytes
runtime map cells: page=#87, bytes=8214
OK: map sprites scroll in sync; screen cursor is stable
OK: background scroll transform монотонен и совпадает с ViewportPixelX
OK: path overlay без POINTS и с оригинальными ROUTE.ICN arrows
OK: viewport scroll state идет 5px/кадр, tile-page меняется только на границе 32px
```

SHA256:

```text
Build\hmm2_vdac2.spg
F9870259CC81413639F6A3D8B635AB8785BDF45ABDB428F18B01E9B9DD18A9A6

Build\Core_p05.bin
F17AD1ED304CF0C46D112BB620757F9D4CAC323768F2864C891F02554102FA45

Build\Core_p06.bin
82EB42401E92450F10A8706BDE6BADFF7B0FB4B89B753D40201BE6447372EBAD

Assets\Converted\Maps\SKIRMISH_RUNTIME_CELLS.bin
B59E11904295325DBF165BD261ED716BC6F0083CD538B4AD18EB2D1565E9A119

Build\scale8_5_x16.bin
CEC78C247597B2AE799D93509A8BC58F9AD2D738042E7F5225A18BA78CFFF53D
```

## Запись 2026-06-13: v005 reference — карта проходимости и STOP/ROAD

По команде пользователя текущая рабочая версия сохранена как новая опорная:

```text
releases\v005-2026-06-13-pathfinding-passability-reference
```

Состояние reference:

- поведение движения оставлено по оригинальной логике Heroes II/fheroes2:
  `STOP`-клетка может быть конечной остановкой, но не промежуточной клеткой
  сквозного маршрута;
- убрана подмена заблокированной цели на соседнюю клетку: если target
  непроходимый, `HeroTarget` не меняется и путь не стартует;
- `passability_viewer.py` показывает не только directional mask, но и path flags:
  `W` water, `S` stop, `R` road; `SR` означает road + stop;
- подтвержден спорный участок: `13,9 -> 9,13` строит путь из 5 шагов,
  `13,9 -> 6,16` маршрута не имеет по маскам/STOP-клеткам карты;
- в опорную папку сохранены только файлы проекта в формате предыдущих
  releases: `Source`, `Build`, `Docs`, `AssetsConverted`, корневые build/config
  файлы и `REFERENCE.md`; внешний `OpenHMM2` в release не копировался.

Проверено перед сохранением:

```text
.\build.cmd
python Source\Tools\test_hero_command.py
python Source\Tools\test_path_overlay.py
python -m py_compile Source\Tools\passability_viewer.py
python Source\Tools\trace_z80_pathfinding.py --hero 13,9 --target 9,13 --max-frames 128 --radius 6
python Source\Tools\trace_z80_pathfinding.py --hero 13,9 --target 6,16 --max-frames 256 --radius 8
```

SHA256:

```text
Build\hmm2_vdac2.spg
36B4CF733D63AEB203B95DF6021DDEEF93E9657E0FD78270EE4EABDF217B8D15

Build\Core_p05.bin
49AEEAADA3E80D3745800DFE88BF76225CFD595CB9746B676625D00E4766453A

Build\Core_p06.bin
145C3C7AD85E84B73BD660D4C6E7D552D2EBE27B5F8542B49C3B00FDD6E3197C

Assets\Converted\Maps\SKIRMISH.pass.bin
EEBEBA5147B086156A8A023F9959CE85DA359DC286FE3E3F828E2185D448D788

Assets\Converted\Maps\SKIRMISH.path.bin
0902014966E149C808CB4CEF1898C1BBC5A6F7E33FAA7EFE1B710CA03059991E
```

## Запись 2026-06-12: v004 reference — чистый composite scroll без рывков

По команде пользователя текущая рабочая версия сохранена как новая опорная:

```text
releases\v004-2026-06-12-clean-composite-scroll-reference
```

Состояние reference:

- карта визуально чистая на реальном FT812;
- скролл чистый, без рывков;
- чёрная шахматка в нижней части карты устранена;
- фон: составной tile-cache `PALETTED4444`;
- динамика: флаги, ресурсы, артефакты, монстры, герой, курсор;
- `RUNTIME_DL_BUFFER` перенесён на `CMD_ADDRESS_PTR=#9800`, потому что старый
  `#9000` пересекался с runtime DL/CMD scratch;
- `MapTerrainCells` и composite upload table используют guard-сетку `37x37`;
- composite upload table: page `#C4`, `8214` байт.

Проверено перед сохранением:

```text
.\build.cmd
python Source\Tools\test_viewport_scroll.py
python Source\Tools\test_background_scroll_monotonic.py
python Source\Tools\hmm2_ft812_snapshot.py --viewport-y 672 --out Diagnostics\hmm2_ft812_snapshot_y672.png
```

SHA256:

```text
Build\hmm2_vdac2.spg
BE5EA48E6D570B375BA355AFDA3E630D54CB0B15EB87EC7F28DCD649E87C83F0

Build\Core_p05.bin
B899D99FACB024B91D21883312623D0990CE8A9C503B04CE1A18CCEA24553862

Build\Core_p06.bin
543ECCECA319701DB767CFE23A3F007C4E437AC7175B70B5831472DD20427814

Assets\Converted\ObjectPacks\SKIRMISH_OBJECTS_SPI.pack
EDE9D66BC18103AFDF878B7DDB6DCDC9464388E8D1F4D838B250D1F54CC7E59E
```

## Запись 2026-06-12: активная полная карта объектов для всех origin

После замечания пользователя, что нужен не стартовый экран, а полная карта,
убрана временная схема `origin 0 + empty`. Активная сборка теперь содержит
object layer для всех `374` viewport origins (`17x22`):

- `viewport_pack.py` собирает общий object atlas по всей карте, без
  semantic-фильтра объектов;
- secondary map objects кодируются как `PALETTED4444`, прозрачный индекс
  palette `0`;
- hero/cursor остаются overlay sprites в `ARGB4`;
- общий object atlas: `494` unique secondary object sprites + `2` overlay,
  `OBJECT_ATLAS_SIZE=342050`;
- object atlas pages разложены в свободные страницы `#07-#0F`, `#11`, `#13`,
  `#15-#1E`;
- полный object-view DL pack: `SKIRMISH_OBJECTVIEW_p00..p178`, `2932736`
  байт, pages `#3C-#EE`;
- `ObjectViewDL_Table` теперь хранит `page, offset, size`, а runtime заливает
  и appends ровно фактический размер DL текущего origin;
- `Render_ObjectViewTableEntry` переведён на запись таблицы 5 bytes;
- runtime DL в FT812 перенесён с `#0A0000` на `#0E0000`, потому что полный
  object atlas занимает `RAM_G #080000-#0D3821`;
- object static DL cache теперь `RAM_G #0E0FC0`.

После реального скролла была найдена причина глюка: часть runtime DMA/CMD
адресов всё ещё была hardcoded как `LD A,#0A`, хотя `RUNTIME_DL_LEFT_RAMG`
уже перенесён на `#0E0000`. При попытке скролла static DL продолжал писаться
в `#0A....` и портил середину object atlas. Все такие места заменены на
вычисление high-byte из `RUNTIME_DL_*_RAMG`.

Добавлен обязательный калькулятор `Source/Tools/check_ramg_usage.py`. Он
запускается из `build.cmd` до `sjasmplus` и для каждой позиции карты читает
реальный `ObjectViewDL_Table` + SPG pages, декодирует EVE DL-команды
`BITMAP_SOURCE`, `PALETTE_SOURCE`, `BITMAP_LAYOUT` и проверяет:

- все диапазоны чтения/записи внутри физического `RAM_G #000000-#0FFFFF`;
- runtime DL не пересекает terrain/object atlas;
- все bitmap/palette sources лежат внутри object atlas;
- object-view DL не пересекает границу 16К page.

Сводка калькулятора:

```text
origins=374 (17x22), object-view pages checked=179
terrain atlas: #000000-#06DFFF (450560 bytes)
object atlas: #080000-#0D3821 (342050 bytes)
runtime left DL: #0E0000-#0E0BFF (3072 bytes)
runtime right DL: #0E0C00-#0E0FBF (960 bytes)
runtime object DL base=#0E0FC0, max_size=8548, max_end=#0E3123
checked bitmap/palette sources=92935, max_source_end=#0D29DF
```

Дамп `C:\Users\Администратор\Desktop\HMM2\111` показал, что зависание при
скролле не связано с выходом за `RAM_G`. Состояние дампа:

```text
FrameCounter=229
ViewportOrigin=6,0
ViewportPixel=195,0
RuntimeLastOrigin=6,0
Runtime_UploadObjectStatic: page=#3E, src=#C000, size=#1458, dst=#0E0FC0
```

Фактическая причина — переполнение `RAM_DL` FT812 (8К), а не `RAM_G`.
Текущий кадр строится через `CMD_APPEND`: terrain tile DL + object DL +
hero/cursor/path. Калькулятор `check_ramg_usage.py` теперь проверяет и
`RAM_DL`; первая ошибка:

```text
origin 1,0: frame DL 8292 > 8192; object DL=4012, terrain/static=4280
```

Сводка по всем origins:

```text
372 из 374 origins превышают RAM_DL
worst origin 7,9: frame=12828, object=8548
```

Вывод: полная карта через display-list commands для terrain+objects не
помещается в аппаратный `RAM_DL`. Нужна смена рендера: убирать тысячи terrain
команд из кадра (например, viewport terrain bitmap/палитровый scroll-buffer)
и/или переводить object layer в предкомпозит/стриминг, иначе скролл будет
упираться в копроцессор даже при корректном `RAM_G`.

Внешний `SKIRMISH_OBJECTS_SPI.pack` продолжает генерироваться для следующего
этапа SPI/SD loader. Его destination для object DL синхронизирован с новой
разметкой: `#0E0FC0`. Пока активная runtime-загрузка идёт из SPG pages, не из
SPI-файла.

Проверено:

```text
.\build.cmd
```

`verify_ft812_pipeline.py` в составе build подтвердил:

```text
RAM_G terrain atlas byte-for-byte OK, 450560 bytes
RAM_G object atlas byte-for-byte OK, 342050 bytes
DL: CELL=340, VERTEX2F=534, DISPLAY=1
sjasmplus: 0 errors, 0 warnings
```

SHA256:

```text
Build\hmm2_vdac2.spg
FF41CEA90AC87A0F7977E034C4D90F1121220E046657905A49B319218721D810

Build\Core_p05.bin
925327FB1B22DCA5EBEDCD63EBBA0542CAEA738DF5870F75E3CF119E1C956D8B

Build\Core_p06.bin
86FDDB81F12E55287746794D1C193446BEACD22D201F5025C19DD088BB0FB97C

Assets\Converted\ObjectPacks\SKIRMISH_OBJECTS_SPI.pack
7943F539C6F246B63DD0656B3283A887D0E02BFE487DD39219045F383772A75C
```

## Запись 2026-06-12: v003 reference сохранён, object fill переводится на SPI-pack

По команде пользователя текущая стабильная версия сохранена как опорная:

```text
releases\v003-2026-06-12-tilemap-no-grid-reference
```

Внутри сохранены `Build`, `Source`, `build.cmd`, `spgbld_vdac2.ini`,
`PROJECT_MEMORY.md`, `REFERENCE.md`. Это baseline после отката к tilemap,
фикса чёрной сетки скролла и проверок. Его не перезаписывать.

Следующее направление: наполнение adventure map согласно оригиналу. Не держать
полный object atlas/DL всех положений в Core/SPG как активную runtime-модель:
HMM2 — пошаговая стратегия, поэтому object pack можно подгружать при смене
экрана/чанка через SPI. Все второстепенные элементы карты переводить в
`PALETTED4444`; hero/cursor/важные actors остаются `ARGB4`.

Сделан host-side первый шаг:

- добавлен `Source/Tools/object_spi_pack.py`;
- `build.cmd` теперь генерирует внешний
  `Assets/Converted/ObjectPacks/SKIRMISH_OBJECTS_SPI.pack`;
- pack содержит 374 entry для всех `ViewportOriginX/Y` (`17x22`);
- каждый entry содержит header `H2OB`, PALETTED4444 palette, sprites текущего
  viewport и готовый object DL текущего viewport;
- второстепенные object sprites кодируются как `PALETTED4444`, прозрачный
  индекс palette — `0`;
- worst screen: origin `8,9`, `469` parts, `327` unique sprites,
  `237041` bytes sprites, `11292` bytes DL, `248359` bytes total;
- pack пока НЕ подключён runtime-loader'ом: текущий SPG остаётся совместимым с
  v003 runtime path, а SPI object loader — следующий обязательный этап.

SHA256 `Assets\Converted\ObjectPacks\SKIRMISH_OBJECTS_SPI.pack`:

```text
793A352B28C19850106B157AA0B58D217D3438C8D8914A184A2C87C1D47BD8F6
```

Проверено после добавления pack-генерации:

```text
.\build.cmd
python Source\Tools\test_viewport_scroll.py
python Source\Tools\test_background_scroll_monotonic.py
python Source\Tools\test_cursor_input.py
python Source\Tools\test_hero_command.py
```

## Fix 2026-06-12: чёрная горизонтальная сетка при скролле тайлового фона

После отката к tilemap на реальном выводе при скролле появилась сетка чёрных
горизонтальных линий. Причина была в генераторе `viewport_pack.py`: физический
размер одного логического 32px terrain-тайла при upscale `8/5` равен `51.2px`,
но runtime-шаблоны ставили тайлы с шагом `DISPLAY_TILE_PX=52px`
(`tile_index * 52 * 16`). При `BITMAP_TRANSFORM_A/E=160` край 52-пиксельного
bitmap мог попасть в `FT_BORDER`, поэтому нижняя строка тайла становилась
чёрной. Вертикальная щель обычно перекрывалась следующим тайлом, а
горизонтальная оставалась видимой.

Исправление:

- `tile_vertex2f_units()` теперь считает позицию тайла через точный
  `scaled_vertex2f_units(tile_index * 32)`, то есть по шагу `51.2px` в 16.4
  координатах FT812;
- `RuntimeDL_TranslateXRight_Low` и `RUNTIME_LEFT_SCREEN_X16` используют тот же
  точный расчёт для начала правого band;
- terrain `BITMAP_SIZE` теперь генерируется как
  `FT_NEAREST, FT_REPEAT, FT_REPEAT, 52, 52`, чтобы крайняя выборка terrain не
  могла дать чёрный `FT_BORDER`;
- object/hero/cursor sprites остаются на `FT_BORDER`.

Проверено:

```text
.\build.cmd
python Source\Tools\test_viewport_scroll.py
python Source\Tools\test_background_scroll_monotonic.py
python Source\Tools\test_cursor_input.py
python Source\Tools\test_hero_command.py
python Source\Tools\probe_ft_frequency_writes.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
```

SHA256 `Build\hmm2_vdac2.spg`:

```text
9F0572472A846306842DA4CF65BFD6D8B18C962A428B32A2DBA58CCCA3318541
```

## Решение 2026-06-12: откат фона к тайловой модели

После анализа с Claude принято решение не развивать pseudo-DXT/DXT фон карты
как штатный путь. Выигрыша для HMM2 в `RAM_G` нет: L4/L2 варианты либо дают
артефакты/рябь на блоках, либо требуют тяжёлой перезаливки окна и риска
перезаписи области `RAM_G`, на которую смотрит текущий display list. Для
пошаговой карты важнее стабильный матричный скролл и оригинальный terrain art.

Штатная модель с этого момента:

- adventure map фон строится из `GROUND32.TIL` terrain atlas в `RAM_G`;
- `Background_Upload` в генераторе `viewport_pack.py` всегда зовёт
  `Terrain_Upload`;
- DXT-генераторы и документы остаются как неактивная исследовательская ветка,
  но не должны включаться в дефолтную сборку;
- `build.cmd` по умолчанию отключает DXT scroll background через
  `dxt_l4_scroll_buffer.py --disable`;
- не трогать фиксы кадрового swap, героя, cursor transform, BFS и path overlay.

Проверочный минимум после отката: `.\build.cmd`,
`test_viewport_scroll.py`, `test_cursor_input.py`, `test_hero_command.py`,
`hmm2_ft812_snapshot.py`.

Проверено после правки:

```text
.\build.cmd
python Source\Tools\test_viewport_scroll.py
python Source\Tools\test_cursor_input.py
python Source\Tools\test_hero_command.py
python Source\Tools\test_background_scroll_monotonic.py
python Source\Tools\probe_ft_frequency_writes.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
```

Результат сборки: `RAM_G` после `Game_Init` байт-в-байт совпадает с terrain
atlas `450560` байт, object atlas `73778` байт совпадает с object pages, DL
использует `CELL+VERTEX2F` для tilemap/scroll-buffer, DXT background pass не
активен. `build.cmd` больше не включает старый baked/DXT путь через переменные
окружения.

SHA256 `Build\hmm2_vdac2.spg`:

```text
D9FAA9E5D0BF93E9D64C92D6A85BB052BF2C0E86A6E129EB730037C005D700B3
```

## Fix 2026-06-12: рывок фона из-за неактивной anchor-ветки

Рывок фона "2 вперёд, 1 назад" был не проблемой DXT-формата. В `render.asm`
для DXT anchored-window была проверка `ifdef BG_DXT_ANCHORED_WINDOW`, а
`BG_DXT_ANCHORED_WINDOW` генерируется как `EQU 1`, не как `define`.
Из-за этого sjasmplus не включал anchor-ветку, и `Render_DxtUpdateScrollMatrix`
падал в старую логику `ViewportPixel & 31`. Фактический тест показал:
на кадре 6 камера `ViewportPixelX=35`, а фон получал `world_x=3`.

Исправление: заменить `ifdef BG_DXT_ANCHORED_WINDOW` на
`if BG_DXT_ANCHORED_WINDOW` в `Render_DxtUpdateScrollMatrix`. Добавлен тест
`Source/Tools/test_background_scroll_monotonic.py`, который вызывает реальные
`Input_Poll`/`Game_Update`/`Render_Frame` и проверяет, что transform фона
монотонен и совпадает с `ViewportPixelX`.

Проверено:

```text
.\build.cmd
cmd /c python Source\Tools\test_background_scroll_monotonic.py
python Source\Tools\test_viewport_scroll.py
python Source\Tools\test_cursor_input.py
python Source\Tools\test_hero_command.py
python Source\Tools\probe_ft_frequency_writes.py
```

SPG SHA256:

```text
C9FBE2785754598AA92DAE30D2A97FEA08D5A51A1CBEBC5B509427457FAE7CC2
```

## Запись 2026-06-12: FT812 zlib/CMD_INFLATE в схеме памяти

FT812 умеет аппаратную распаковку zlib через `CMD_INFLATE`, но это механизм
загрузки, а не сжатый runtime-формат bitmap. Копроцессор принимает zlib-поток
через command FIFO и распаковывает его в обычный `RAM_G`; дальше bitmap
рендерится из распакованного буфера. Поэтому в бюджете `RAM_G` всегда считать
полный распакованный размер.

Применение в HMM2:

- object/UI/actor источники можно хранить на SPI/SD/SPG в zlib и распаковывать
  в назначенные cache-слоты `RAM_G` через `CMD_INFLATE`;
- главный terrain-фон карты не грузить целиком в `RAM_G`;
- для terrain pseudo-DXT оставить схему "полный DXT-фон как внешний источник,
  в `RAM_G` только окно 672x512";
- для скролла карты нужен прямоугольный доступ к строкам `c0`, `c1`, `mask`,
  поэтому zlib не должен ломать адресуемость window-loader.

В коде уже подключён `FT/Coprocessor/Include.inc`; в TSLib/ZumaRef есть
готовая функция `FT.Coprocessor.Inflate` и макрос `FT_WR_INFLATE`. Аппаратную
инициализацию FT812/VDAC2 этим не трогать.

## Запись 2026-06-12: план вывода карты без переполнения RAM_G

Опорный документ: `Docs/memory_render_plan.md`.

Карту не делить на произвольные "чанки". Единица работы рендера — текущий
экран карты плюс запас по краям для плавного скролла. Память планировать сразу
по трём уровням: 4 МБ Z80 RAM, `RAM_G` FT812 1 МБ и SPI-подгрузка. `RAM_G`
не является хранилищем всей карты: terrain/object/UI наборы должны жить как
рабочие наборы текущего режима/экрана. Полный object atlas карты и display list
для всех положений экрана хранить нельзя.

Для pseudo-DXT L4 апскейл берётся из загрузчика Zuma: L4 mask пишет destination
alpha, затем RGB565 `c1`/`c0` смешиваются через alpha. Для HMM2 добавляется
пиксельное окно внутри 672x512 scroll-buffer. Расчёт записан в
`Docs/dxt_l4_scroll.md`, проверка в `Source/Tools/dxt_l4_scroll_math.py`.
Для 1024x768 физического вывода: L4 mask `A/E=160`, `C/F=rem*256`; RGB565
endpoint-слои `A/E=40`, `C/F=rem*64`. Фон пересобирается при смене
`ViewportOriginX/Y`, не при каждом пикселе.

CPU-only генератор тестового scroll-buffer:
`Source/Tools/dxt_l4_scroll_buffer.py`. Он собирает terrain 21x16 из
`GROUND32.TIL` в 672x512 RAW layout `c0+c1+L4`, пишет страницы
`Assets/Converted/Background/SKIRMISH_BG_DXT_L4_pXX.bin` и include
`Source/ASM/generated_dxt_background.inc` + DL-шаблон
`Source/ASM/generated_dxt_scroll_dl.inc`. Это подготовка фона; основной рендер
переключать отдельно после проверки. Проверенный RAW для `origin=0,0`:
`258048` байт, SHA256
`445C49A5A4A756D5B80458B783AEACA3FFD52881CD05ADBF342C8712979915BF`.

Ошибка DXT-подключения: в первой DXT-ветке `Render_RuntimeFrameCmd` перед
`BackgroundDxt_DL` не был записан `CMD_DLSTART` (`#FFFFFF00`). Старый tilemap
путь его писал, новый DXT путь сразу отправлял display-list слова в CMD FIFO.
На реальном FT812 это проявилось как `Possible problem with REG_FREQUENCY`,
где значение `0x08002820` похоже на DL-команду `BITMAP_SIZE`, попавшую в
неверный контекст. Исправление: DXT-ветка обязана начинаться с
`Render_CmdBufWrite32(#FFFFFF00)`, затем копировать `BackgroundDxt_DL`.
Проверка после фикса: обычный `build.cmd` проходит, `verify_ft812_pipeline.py`
видит pseudo-DXT pass, `probe_ft_frequency_writes.py` не показывает записей
`REG_FREQUENCY`.

Полная карта как источник SPI: `Source/Tools/dxt_l4_full_map.py` собрал
`Assets/Converted/Background/SKIRMISH_FULLMAP_DXT_L4.raw` размером `995328`
байт (`1152x1152`, SHA256
`B0DA22D528816A43B3484FF02AC0342458C5DAAC04D571941529588E2AB85BA7`).
В `RAM_G` целиком не грузить. `Source/Tools/dxt_l4_extract_window.py`
вырезает из него окно `672x512` по `origin_x/origin_y`; для `0,0` результат
байт-в-байт совпадает с `SKIRMISH_BG_DXT_L4.raw`
(`445C49A5A4A756D5B80458B783AEACA3FFD52881CD05ADBF342C8712979915BF`).

## Запись 2026-06-12: карта HMM2, объекты и память

Правило №1 для карты: делать как в оригинале. Не фильтровать объекты "по
смыслу" и не заменять оригинальную отрисовку эвристикой. Источник порядка и
состава объектов: MP2/compact map (`object_name`, `icn index`, addons,
layer/top) и таблицы fheroes2/OpenHMM2.

Текущий `viewport_pack.py` после аварийного исправления держит компактный
object layer, чтобы сборка не ломалась и страницы не затирали друг друга. Это
не финальный оригинальный слой карты. Его нельзя выдавать за готовый рендер.

Нельзя держать полный object atlas карты в FT812 RAM_G: `RAM_G` 1 МБ, а полный
набор ICN-спрайтов даже для маленькой карты уже выходит за лимит. Нельзя
предсобирать object-DL на все origin viewport: это раздувает страницы и ломает
4 МБ ОЗУ. Правильная стратегия для HMM2 пошаговая: карта, города, экраны и
объекты грузятся по текущему режиму/чанку. SPI это выдержит, потому что HMM2 —
пошаговая стратегия, а не Zuma.

Следующий правильный шаг: сделать paged object streaming для adventure map.
Для текущего viewport/окрестности собрать список оригинальных object parts,
загрузить нужные ICN-спрайты в рабочее окно `RAM_G`, построить DL текущего
экрана и при смене чанка перезагрузить окно. Core не раздувать; загрузчик и
таблицы держать в страницах/оверлеях.

Первый рабочий шаг после этой записи: `viewport_pack.py` собирает полный
оригинальный object layer только для загруженного окна `(0,0)`, без фильтра
объектов, и не предсобирает object-DL для всех origin. Это временный
одновьюпортный пакет: при скролле следующий этап должен подгружать новый
object pack/atlas для текущего чанка.

## Правило №1

Комментарии в коде пишем на русском языке.

Кодировка файлов проекта: UTF-8.

Сторонние скопированные библиотеки, например `Docs\TSLib`, без необходимости не
переписываем, но новый код проекта и правки в коде проекта должны следовать
этому правилу.

## Правило №2

Архитектура игры резидентно-страничная.

Core должен оставаться маленьким резидентным ядром. Нельзя складывать в Core
крупные данные, графику, карты, таблицы ассетов, декодеры и режимные куски
логики, которые можно держать в страницах, оверлеях или пакетах.

Приоритет:

- Core: старт, диспетчер режимов, базовый paging, минимальный FT812 init,
  минимальные общие вызовы.
- Pages/overlays: экран карты, город, бой, загрузчики, декодеры, UI-режимы.
- Data pages/packs: карты, графика, музыка, таблицы ресурсов.

При 4 МБ ОЗУ нельзя потом искать байты в Core из-за раннего распухания ядра.
Все новые подсистемы сначала проектировать как страничные.

## Инструкция: архитектура памяти большой игры (опыт Zuma VDAC2 1024x768)

Выжимка из законченного порта Zuma Deluxe (TS-Config + FT812, ~10 МБ паков,
5+ сцен, полная анимация). Все пункты — не теория, а ответы на реальные
краши/переполнения того проекта. Развивает Правило №2.

### 1. Роли слотов Z80 (16К страницы, slot0..slot3)

- **slot0 (#0000-#3FFF), page0** — всегда видимая страница: маленькие
  межсценные хелперы и код, который зовут при ЛЮБОМ состоянии slot3
  (в Zuma там живут preview-хелперы level-select). Page0 заполняется первой
  и навсегда — класть туда только то, что реально нужно всем сценам.
- **slot1/slot2** — резидентное ядро (Core/Main) + потоковое окно: shared
  декомпрессор стримит паки через окно slot2 (`SafeInflatePage2`-паттерн),
  НЕ трогая slot3 с кодом вызывающей сцены.
- **slot3 (#C000-#FFFF)** — переключаемый код сцены: геймплей, меню,
  level-select, загрузчик — каждый в своей странице. Сцены друг друга не
  видят и не должны видеть.
- **Стек и IM2-вектор/обработчик — только в резидентной памяти.** Никогда в
  переключаемой странице.

### 2. Что ОБЯЗАНО быть резидентным (главные грабли Zuma — дважды)

Любой хелпер, который зовут из РАЗНЫХ сцен (эмиттер матрицы, DMA-отправка
кадра, общий рендер-код), — только резидент (Core или page0).

Вызов хелпера из страницы-оверлея A при замапленной странице B = исполнение
мусора. В Zuma на эти грабли наступили ДВАЖДЫ, второй раз — из-за
устаревшего комментария «caller maps #04 around chain»: маппинг давно
убрали, коммент остался, вызов крашил. Правила:

- комментам о том, «кто что мапит», не верить — проверять по коду вызывающего;
- диагностика по крашу: `PC=NN:ADDR`, где ADDR в диапазоне кода ДРУГОЙ
  страницы = подмена slot под исполнением;
- если резидентного места нет, а оверлею нужен кусок логики чужой страницы —
  не звать её, а ЗАПЕЧЬ результат в данные (готовый CMD-блок + `LDIR`,
  LUT-таблица) и положить копию в свою страницу.

### 3. Инвариант CurrentCodePage

Если в системе есть переменная «какая страница кода сейчас в slot3» (а при
shared-декомпрессорах она нужна — они восстанавливают slot3 из неё), то:

**сменил slot3 → НЕМЕДЛЕННО обнови CurrentCodePage, до любых CALL.**

Zuma-краш: страницу сменили, переменную нет; вложенный лоадер дернул
декомпрессор, тот в конце сделал `SetPage3 (CurrentCodePage)` со старым
значением — и подменил страницу под ещё исполняющимся кодом. Симптом тот же:
«любой уровень виснет», `Illegal port, PC=41:EB4E`.

### 4. Фиксированные буферы: одна страница, канарейка, ASSERT

- Большой буфер с фиксированным адресом (CMD-буфер кадра FT812, лог) обязан
  ЦЕЛИКОМ лежать в одной 16К странице — иначе DMA-источник (`page:offset`)
  его не отправит одним трансфером.
- За концом буфера — байт-канарейка; проверка в отладочной сборке.
- Конец каждого блока данных/кода фиксировать `ASSERT` в asm (адрес конца
  блока <= границы). Переполнение тогда ловится СБОРКОЙ, а не «иногда виснет
  на железе». В Zuma все переполнения page0/Main1 ловились именно ASSERT'ами.

### 5. Бюджеты мерить, предохранители — по факту, не по типу

- Не вводить «гейты» вида «на тяжёлых сценах отключаем фичу X». Сначала
  ЗАМЕРИТЬ worst case эмулятором (полный кадр самой тяжёлой сцены, пик
  указателя буфера). В Zuma worst-кадр оказался 73% буфера — «необходимый»
  гейт удалили.
- Предохранитель ставить по ФАКТИЧЕСКОМУ указателю в рантайме (BufferPtr >=
  порог → деградация конкретного элемента), а не по типу контента.
- Размеры массивов — по физическому максимуму данных (замеренному), не по
  круглым числам.

### 6. Данные: в памяти живёт текущая локация, не вся игра

- Метаданные всех уровней/карт нужны только МЕНЮ/загрузчику. В геймплейной
  памяти держать настройки ОДНОЙ текущей локации (в Zuma: один уровень
  вместо таблицы 22 — освободило сотни байт Main).
- Реестр страниц и реестр RAM_G вести ЯВНО, в одном файле каждый
  (у Zuma: `main_pak_table.inc` + `Docs/RAM_G_MAP.md`). Для HMM2 уже занято:
  `#05` core, `#06` map, `#20-#2E` terrain, `#30` objects, `#40-#4E`
  background — диапазоны по подсистемам, новые страницы только через реестр.

### 7. Хост печёт — Z80 ест

Всё, что можно вычислить заранее, печь Python-скриптом в бинарь и грузить
как данные: матрицы трансформаций (LUT 256 углов × 24 байта вместо
runtime-тригонометрии), масштабированные треки, атласы, паки. На Z80 —
только `LDIR`/DMA готовых блоков. Runtime-композиция сложных вычислений на
Z80 = и медленно, и источник багов (в Zuma runtime-цепочка матриц «плыла»,
запечённый LUT решил всё).

### 8. Когда кончилось место — порядок действий

1. Удалить мёртвый код (в Zuma находились куски по 40-120 байт).
2. Дедуплицировать: общие последовательности → резидентный хелпер.
3. Нерегулярный код (инициализация сцены, загрузка — не покадровый) →
   вынести в отдельную страницу-оверлей; покадровый код сцены остаётся в
   странице сцены.
4. Данные «на всю игру» → данные «на текущую локацию» (п.6).
5. Только потом думать об упаковке/усложнении.

«Компактные» урезания видимых фич вместо поиска места — запрещены
(пользователь это явно отверг в Zuma).

### 9. Процесс

- Make-шаги генераторов держать в ОДНОМ месте: если есть `build.cmd` и
  `build_wc_img.cmd`, второй должен вызывать первый или иметь идентичный
  список. В Zuma фикс генератора «не доезжал» до образа несколько инжектов
  подряд, потому что списки разошлись.
- Не запускать две сборки параллельно (гонка испортила паки в образе).
- Рабочие состояния сохранять как опорные версии `releases/vNNN-дата-...`
  (Source + Build + ini) — сравнение с опорной много раз было самым быстрым
  способом найти регрессию.

## Цель

Портировать open Heroes of Might and Magic II / fheroes2-style gameplay на
ZX Evolution TS-Config с выводом через VDAC2 / FT812.

Основная видеоконфигурация:

- физический FT812 режим: `1024x768`
- логический игровой viewport: `640x480`, выводится через nearest upscale `8/5`
- только VDAC2 / FT812
- без диагностического вывода через ZX bitmap/border
- без fallback на классическую TS-Config графику, если это явно не запрошено

## Текущий локальный проект

Корень:

```text
C:\Users\Администратор\Desktop\HMM2
```

Сборка:

```bat
build.cmd
```

`build.cmd` теперь после `sjasmplus` и `spgbld` обязательно запускает:

```bat
python Source\Tools\verify_ft812_pipeline.py
```

Если не включён `FMapAddrInit/FMADDR`, если `RAM_G` после upload не совпал
байт-в-байт с asset-pages, или если DL contract нарушен, сборка считается
непрошедшей.

Выходные файлы:

```text
Build\hmm2_vdac2.spg
Build\hmm2.sym
Build\Core.bin
```

Текущие SPG-блоки:

- page `#05`: core-код по адресу `#5C00`
- page `#06`: сконвертированная `SKIRMISH.map.bin`
- pages `#20`-`#2C`: первый `GROUND32.TIL` terrain atlas для viewport
  `SKIRMISH`, загружается в FT812 `RAM_G=#000000`

## Инжект в образ

Целевой образ:

```text
\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img
```

Целевая папка внутри образа:

```text
\GAMES\HEROES 2\
```

Имя инжектируемого файла:

```text
HMM2VD2.SPG
```

Проверенный источник инструмента инжекта:

```text
C:\Users\Администратор\Desktop\Zuma Deluxe VDAC2\Source\OTHER\inject_file_to_wc_img.py
```

Он использует FAT32-helper из:

```text
C:\Users\Администратор\Desktop\Zuma Deluxe VDAC2\Source\OTHER\inject_zuma_to_wc_img.py
```

## Важное направление

Не использовать ZX border или экранную память `#4000/#5800` как видимый canary.

Этот проект делается под VDAC2 / FT812. Стартовая диагностика должна идти через:

- `FT_BOOT_UP`
- `FT_RESOLUTION VM_640_480_74Hz`
- `FT.WriteDL`
- `FT_REG_DLSWAP`
- `Video_Setting VID_FT812 | VID_NOGFX`

Текущий HMM2 содержит локальную копию `Docs\TSLib` из Zuma VDAC2 и использует
реальный путь инициализации FT812 в:

```text
Source\ASM\Init_Video.asm
Source\ASM\render.asm
```

Важно: `Docs\TSLib\Include\FT\81x Const.inc` содержит не только `EQU`, но и
таблицы `VM_*` через `FT_ModeTab`. Поэтому этот include должен попадать в
сохраняемый диапазон `Core.bin`. В `Source\ASM\main.asm` сделан `JP Start` в
`EntryPoint`, затем включается `81x Const.inc`; иначе `VM_640_480_74Hz` остается
по адресу около `#0035`, не попадает в SPG, и `FT.Initialize` читает нули из
page0, выставляя неверный видеорежим.

Для `640x480@74` после `FT_RESOLUTION VM_640_480_74Hz` явно пишется
`FT_WR_REG8 FT_REG_PCLK, F1_MUL`, потому что текущая TSLib `FT.Initialize`
загружает H/V-тайминги, но оставляет `REG_PCLK=1`.

Локальная копия `Docs\TSLib\Include\FT\812 Macro.inc` изменена: `FT_DELAY`
сделан через busy-loop без `HALT`. HMM2 стартует с `DI`, поэтому `HALT` внутри
`FT_BOOT_UP` останавливал CPU навсегда.

Конкретный учебник из Zuma скопирован сюда:

```text
Docs\uchebnik_tsconf_vdac2.md
```

Краткая выжимка для HMM2:

```text
Docs\FT812_STUDY_NOTES.md
```

## Соседние reference-проекты

Allowed to copy/reference as needed:

```text
C:\Users\Администратор\Desktop\Zuma Deluxe VDAC2
C:\Users\Администратор\Desktop\WC
C:\Users\Администратор\Desktop\EveApps
```

Most relevant current reference:

```text
C:\Users\Администратор\Desktop\Zuma Deluxe VDAC2
```

Useful pieces from Zuma:

- `Docs\TSLib`
- `Source\ASM\Init_Video.asm`
- FT812 display-list write patterns
- full-stack Z80/TS-Config/FT812 harness and shadow FT812 diagnostics
- RAM_G upload/page reuse discipline
- FAT32 `wc.img` injection tools
- asset packing scripts and SPG delivery patterns

Локальные reference-копии уже сделаны:

```text
Source\ASM\ZumaRef
Source\Tools\ZumaRef
```

Они не подключены к сборке. Использовать как донорский код для дальнейшего
страничного переноса FAT32/RawPak/input.

## Upstream reference

Local clone:

```text
OpenHMM2\
```

Remote:

```text
https://github.com/ihhub/fheroes2.git
```

Purpose:

- logic reference
- map format reference
- AGG/XMI/ICN/TIL reference
- no direct runtime dependency for Z80 code

## Наличие оригинальных ресурсов

Original game resources under:

```text
Assets\Original
```

Present:

- `DATA`
  - `HEROES2.AGG`
  - `HEROES2X.AGG`
- `MAPS`
  - 144 map/campaign files
- `ANIM`
  - 169 `.SMK` files
- `MUSIC`
  - 42 `.ogg` files named `Track02.ogg` through `Track43.ogg`

## Наличие сконвертированных ресурсов

AGG manifests:

```text
Assets\Converted\Manifest\HEROES2.csv
Assets\Converted\Manifest\HEROES2X.csv
```

XMI extracted:

```text
Assets\Converted\Music\XMI\HEROES2
Assets\Converted\Music\XMI\HEROES2X
```

Map converted:

```text
Assets\Converted\Maps\SKIRMISH.map.bin
Assets\Converted\Maps\SKIRMISH.manifest.json
Source\ASM\generated_map.inc
```

Terrain converted:

```text
Assets\Converted\Terrain\SKIRMISH_GROUND32_p00.bin ... p12.bin
Source\ASM\generated_terrain.inc
Source\ASM\generated_adventure_dl.inc
Diagnostics\terrain_ground32_preview.png
Diagnostics\hmm2_ft812_snapshot.png
```

Текущий первый экран уже не цветовая заглушка: `Source\Tools\terrain_atlas.py`
извлекает `GROUND32.TIL` и `KB.PAL` из `HEROES2.AGG`, собирает только видимые
unique cells viewport 15x15, конвертирует их в `RGB565`, раскладывает по SPG
asset-pages и генерирует FT812 `BITMAPS` Display List.

Важно по `terrain_flags`: по fheroes2/MP2 `bit0 = vertical flip`,
`bit1 = horizontal flip`. Перепутанные биты дают визуальные глюки на берегах и
переходах terrain. Это исправлено в `Source\Tools\terrain_atlas.py`.

Последняя проверка full-stack:

- режим: `640x480@74`
- `REG_PCLK=4`
- DL: 300 `FT_CELL` + 300 `FT_VERTEX2F`, без `VERTEX2II`
- atlas: 239616 bytes, 117 unique cells, 15 pages
- injected file: `\GAMES\HEROES 2\HMM2VD2.SPG`, 262144 bytes

Важно по FT812 coordinates: `VERTEX2II` имеет 9-битный `X` и не подходит для
рисования bitmap-тайлов правее `x=511` на экране 640x480. Для полного
640-wide viewport используется `FT_CELL n` и `FT_VERTEX2F x*16, y*16`. Иначе
правая часть экрана выглядит как обрезание/чёрная полоса.

Родственные грабли из Zuma VDAC2 (2026-06-11): координата `VERTEX2F` —
15-битная SIGNED, максимум `+16383`. В `VERTEX_FORMAT 4` (1/16 px) это
1023.94px: координата `1024*16=16384` молча переполняется в `-16384`, и
примитив уезжает за левый край (у Zuma так «исчез» full-screen fade-rect
после перехода на 1024x768 — переходы шли через мусор вместо чёрного).
На 640x480 запас есть, но при любом upscale: либо кламп `16383`, либо
`VERTEX_FORMAT 0` (целые пиксели, диапазон +-16384px).

Важно по paging на железе: при `define MAPPING_REGISTERS` все `SetPage*` макросы
пишут в mapped-регистры `#0410-#0413`. Перед любыми `SetPage*` обязательно
вызвать `FMapAddrInit`. Без этого эмулятор мог проходить, но реальный TS-Config
оставлял slot3 на старой странице, и `Terrain_Upload` заливал в RAM_G мусор
вместо страниц atlas `#20..#2E`. В HMM2 `Platform_Init` теперь вызывает
`FMapAddrInit` перед `Init_Video`.

Последний SPG после фикса paging:

- `Build\hmm2_vdac2.spg`
- размер: 262144 bytes
- SHA256: `A89B0087A086DCFD20CFFCF9408354A8B43089AF6832A7F7927679B7D8F7E2AF`
- такой же SHA после извлечения из `wc.img`

## Обязательные проверки против повторения paging/RAM_G ошибок

Эти проверки обязательны перед любой диагностикой "картинка глючит":

1. `build.cmd` должен пройти до конца.
2. В выводе `verify_ft812_pipeline.py` должно быть:
   - `OK: FMADDR mapping включён`
   - `OK: RAM_G после Game_Init байт-в-байт совпадает с atlas pages`
   - `CELL=300 VERTEX2F>=300 VERTEX2II=0 DISPLAY=1`
   - при включенном object layer `VERTEX2F=300 + число размещенных object sprites`
3. После инжекта `Source\Tools\ZumaRef\inject_file_to_wc_img.py` сам сравнивает
   SHA256 записанного файла с локальным источником.
4. Для отдельной проверки образа запускать:

```bat
python Source\Tools\verify_wc_spg.py --img "\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img"
```

5. Full-stack harness должен входить через `Platform_Init`, не через прямой
   `Init_Video`, иначе тест может обойти `FMapAddrInit`.

Эмулятор HMM2 теперь моделирует `FMADDR`: запись в `#0410-#0413` меняет pages
только после `OUT (#15AF), FM_EN`. Это специально сделано, чтобы тест падал при
пропущенном `FMapAddrInit`, как железо.

## Добавленные инструменты

```text
Source\Tools\agg_tools.py
Source\Tools\map_tools.py
Source\Tools\check_wc_folder.py
Source\Tools\terrain_atlas.py
Source\Tools\object_atlas.py
Source\Tools\hmm2_ft812_snapshot.py
Source\Tools\verify_ft812_pipeline.py
Source\Tools\verify_wc_spg.py
Source\Tools\analyze_z80_dump.py
Source\Tools\render_atlas_direct.py
```

`agg_tools.py`:

- validates AGG hash table
- writes CSV manifests
- extracts XMI

`map_tools.py`:

- parses MP2/MX2 header
- reads 20-byte MP2 tile records
- writes compact map v2:
  - 20-byte MP2 tile records are preserved
  - addon count/table is preserved
  - addon objectNameN1 is stored as uint16 because fheroes2 multiplies the
    original byte by 2 while loading addons

`check_wc_folder.py`:

- lists a folder inside `wc.img` using the Zuma FAT32 helper

`terrain_atlas.py`:

- extracts `GROUND32.TIL` and `KB.PAL`
- builds first visible terrain atlas for FT812 `RGB565`
- writes SPG chunk pages, generated ASM constants/upload routine, and bitmap DL

`object_atlas.py`:

- берет `object_name1/object_name2` и `bottom_icn/top_icn` из compact MP2 map
- переводит `ObjectIcnType` в реальные `*.ICN` имена по таблице fheroes2/MP2
- декодирует ICN RLE в ARGB4 с прозрачностью
- рабочий билд сейчас использует safe semantic object layer:
  `ENABLE_OBJECT_LAYER = True`, `ENABLE_DECORATION_LAYER = False`.
- Compact map v2 сохраняет MP2 tile records и addon-chain; object renderer
  строит parts из tile + addons, сортирует ground parts по layer как fheroes2.
- Terrain/decor fragments (`MTN*`, `TRE*`, `OBJN* terrain decoration`) пока
  не включены в рабочий билд. Они должны идти отдельным terrain-composite pass,
  а не обычным ARGB4 overlay, иначе появляются полосы.
- кладет object atlas в FT812 RAM_G после terrain: `OBJECT_ATLAS_RAMG=#03A800`
- пишет object pages в SPG с базовой страницей `#30`
- патчит `generated_adventure_dl.inc`: terrain остается `RGB565`, объекты идут
  поверх через `FT_ARGB4` и `FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA`
- ВАЖНО: `ARGB4` для FT812 пишется little-endian, как все 16-битные bitmap
  данные EVE/VDAC2. Нельзя писать `high,low`: на железе это дает глюки
  прозрачности/цвета поверх карты. PNG renderer обязан читать ARGB4 так же:
  `low | high << 8`.

`hmm2_ft812_snapshot.py`:

- runs the Zuma-derived full-stack Z80/TS-Config/FT812 harness
- calls `Platform_Init`, `Game_Init`, `Render_Frame`
- rasterizes FT812 rects and `RGB565` bitmap cells to PNG
- rasterizes `ARGB4` object sprites with alpha blending

Важно: актуальный harness вызывает `Platform_Init`, затем `Game_Init`,
`Render_Frame`. Прямой вызов `Init_Video` больше не использовать для full-stack
проверок, потому что он обходит `FMapAddrInit`.

`verify_ft812_pipeline.py`:

- проверяет `FMapAddrInit/FMADDR`
- сравнивает `FT812 RAM_G` после `Game_Init` с atlas pages байт-в-байт
- сравнивает `FT812 RAM_G` object atlas с object pages байт-в-байт
- проверяет DL contract: `CELL=300`, `VERTEX2F>=300`, `VERTEX2II=0`

## Текущий object-layer milestone

Первый экран SKIRMISH теперь рисуется не только terrain:

- terrain: 300 тайлов, 117 уникальных cells, 239616 байт, pages `#20..#2E`
- objects: 8 semantic MP2/ICN parts, 5 unique sprites, 7920 bytes, page `#30`
- display list: `CELL=300`, `VERTEX2F=308`, `VERTEX2II=0`, `DISPLAY=1`
- full-stack PNG: `Diagnostics\hmm2_ft812_snapshot.png`
- текущий SPG injected в `wc.img`:
  `\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img`
  `/GAMES/HEROES 2/HMM2VD2.SPG`
  SHA256 `6691A7D7C22AF4C2E177686C75942CD1D08B398607C86AF97432EDA4AF1636FA`

## Host-side pseudo-DXT background

Пользователь перекодировал текущий 640x480 viewport в host-side L4 pseudo-DXT.
Файлы хранить не в корне, а здесь:

```text
Assets\Converted\Background\hmm2_ft812_snapshot_l4.dxt
Assets\Converted\Background\hmm2_ft812_snapshot_l4.raw
```

SHA256 D1L4 block dump:

```text
427DB9C111DE1EC3FF5B14E95CC29D853FB73863906CB8C5998002C909856C62
```

SHA256 raw layout:

```text
8F0C19A10D7BCC49F6A2D31F6D1443C48BE52D229581DF05A8F690E3F5539F16
```

Правило: pseudo-DXT кодируется на хосте, не на Z80. Runtime должен только
загрузить готовые color/mask layers в RAM_G и вывести их FT812 display list.
Core не раздувать декодером/кодером.

Текущий runtime background:

- `dxt_background.py` берет `.raw` напрямую, `.dxt` нужен только как fallback.
- raw layout: `c0 RGB565 160x120` + `c1 RGB565 160x120` + `L4 mask 640x480`
- raw size: `230400` bytes, pages `#40..#4E`, `BG_DXT_RAMG=#000000`
- DL: 3 passes, `VERTEX2F=3`, `VERTEX2II=0`
- object overlay отключен, потому что фон уже запечен.
- текущий SPG SHA256:

```text
AE92A33E2DEB3847EB7E37F39D25E243D9AFD87DB2DF558DB3302635AF15AE32
```

`verify_wc_spg.py`:

- читает `HMM2VD2.SPG` из `wc.img`
- сравнивает размер и SHA256 с `Build\hmm2_vdac2.spg`

`analyze_z80_dump.py`:

- сравнивает 64К дамп памяти с текущим `Build\Core.bin`
- показывает page-регистры `#0410-#0413`, адреса ключевых символов и начало DL

`render_atlas_direct.py`:

- строит независимый PNG напрямую из atlas pages и `generated_adventure_dl.inc`
- нужен для проверки, что `hmm2_ft812_snapshot.py` не рисует красивую ложь

## Направление по аудио

Runtime audio should use MIDI/SAM, not OGG playback.

Source path:

- extract `MIDIxxxx.XMI` from AGG
- convert XMI to MIDI or a SAM-compatible event stream
- drive ZX Evolution SAM MIDI synthesizer

Reference conversion code:

```text
OpenHMM2\src\tools\xmi2midi.cpp
OpenHMM2\src\engine\audio_xmi2mid.cpp
```

Current machine did not have `cmake`, `ninja`, `msbuild`, `cl`, `g++`, or
`clang++` in PATH when checked, so building upstream `xmi2midi` needs toolchain
setup or a standalone conversion port.

## Milestone 2026-06-08: карта FT812 + курсор

Текущий `Build\hmm2_vdac2.spg` собран, проверен через full-stack PNG и
инжектирован в образ:

```text
\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img
/GAMES/HEROES 2/HMM2VD2.SPG
```

SHA256 SPG с картой, pseudo-DXT фоном и статическим курсором:

```text
9DDA14C0E9CCD79F118DC4F22ED0A9ECFF1A02E2A70D29CEE8C4090C3A199449
```

## Milestone 2026-06-08: управляемый курсор

Текущий `Build\hmm2_vdac2.spg` собран, проверен и инжектирован в тот же образ:

```text
\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img
/GAMES/HEROES 2/HMM2VD2.SPG
```

SHA256 текущего SPG:

```text
7AA587555C64F7F8C7F74AA0A27929E93F549E12500072F770249FE1D613AC72
```

SHA256 текущего Core:

```text
83827B7C55F531B56C3712439902E594ACA1571DA8B43A3F84A01ABC61551CAD
```

Что изменено:

- `Docs/TSLib/Include/Input/Include.inc` подключен после `ORG`, потому что
  внутри есть код TSLib Input; до `ORG` он собирался вне `Core.bin`.
- `Source\ASM\input.asm` взят из ZumaRef, но мышь временно исключена из
  `Input_Scan`: текущий этап использует PS/2 + Kempston.
- `Input_Poll` собирает compact `InputState` для HMM2.
- `Cursor_Update` двигает tile cursor по 20x15 viewport с cooldown.
- `Render_Cursor` позиционирует рамку через `FT_VERTEX_TRANSLATE_X/Y`.
- `Source\Tools\test_cursor_input.py` проверяет right/down, сброс cooldown и
  соответствие FT812 translate.
- `hmm2_ft812_snapshot.py` теперь понимает `VERTEX_TRANSLATE_X/Y` и порт #1F
  Kempston в full-stack модели.

Обязательная проверка перед инжектом:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
```

Последний PNG: `Diagnostics\hmm2_ft812_snapshot.png`.

Текущее состояние:

- карта выводится через host-side pseudo-DXT L4 raw;
- RAM_G после `Game_Init` совпадает с background pages байт-в-байт;
- display list использует 640x480 FT812 background pass;
- поверх карты есть видимый желтый курсор 32x32;
- курсор двигается по тайлам через PS/2/Kempston input;
- object overlay отключен, чтобы не вносить глюки поверх запеченного фона.

## Следующий инженерный milestone

Управляемый adventure viewport:

1. Добавить один безопасный динамический слой для героя/объекта поверх карты.
2. Проверять object layer через full-stack PNG до инжекта.
3. Только после этого возвращать MP2 addon chain и object layer ordering.
4. Для мыши сохранять правило: full-stack модель портов обязательна до инжекта.

Не тратить время на музыку, бой, города или анимации до рабочего управления
курсором на текущей карте.

## Milestone 2026-06-08: Kempston Mouse для курсора

Проблема:

- курсор двигался скачкообразно, потому что работал только tile-step через
  PS/2/Kempston joystick;
- Kempston Mouse не работала: `Input_Scan` временно не вызывал
  `Input.Mouse.UpdateMouseState`;
- после возврата мыши `Input.Mouse.PositionX/Y` clamp-ились в 0, потому что
  `ResolutionWidthPtr/ResolutionHeightPtr` могли оставаться нулевыми.

Исправление:

- `Input_Scan` снова вызывает `Input.Mouse.UpdateMouseState`.
- `Platform_Init` явно пишет логический input размер `ResolutionWidthPtr=640`,
  `ResolutionHeightPtr=480` после `Init_Video`, потому что Kempston Mouse
  должен работать в логическом viewport.
- Физический FT812 режим остаётся `1024x768` через
  `FT_RESOLUTION VM_1024_768_59Hz`; не использовать
  `ResolutionWidthPtr/HeightPtr` как доказательство физического видеорежима.
- `Cursor_Update` берет координаты мыши только если `Input.Mouse.PositionX/Y`
  изменились; если мышь стоит, работает клавиатура/joystick.
- Mouse position переводится в tile через деление на 32 и clamp 20x15.
- `hmm2_ft812_snapshot.py` эмулирует порты Kempston Mouse:
  `#FBDF` X, `#FFDF` Y, `#FADF` buttons.
- `test_cursor_input.py` проверяет Kempston Mouse, right/down и FT812 translate.

Текущий инжект:

```text
\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img
/GAMES/HEROES 2/HMM2VD2.SPG
```

SHA256 текущего SPG:

```text
6C85226F7761DF2899E6CFDBCD87692A0D3E899130A65C6D2F14D9C35FB52EDB
```

SHA256 текущего Core:

```text
E7F11009488B552BB2B73DB087442C6FCE20D3E0E39BF3C7AB55EFE83D4B1EFD
```

Проверено:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
python Source\Tools\verify_wc_spg.py --img "\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img" --src Build\hmm2_vdac2.spg --dir GAMES "HEROES 2" --name HMM2VD2.SPG
```

## Milestone 2026-06-08: пиксельный курсор

Проблема:

- клавиатура/joystick двигали курсор слишком быстро;
- рамка прыгала по 32-пиксельным знакоместам, визуально неприятно.

Исправление:

- добавлены `CursorPixelX/CursorPixelY`;
- рамка FT812 позиционируется от pixel coordinates, а не от `CursorTileX/Y`;
- мышь двигает рамку пиксельно;
- клавиатура/joystick двигают рамку медленно: `2 px` через кадр;
- `CursorTileX/CursorTileY` теперь производные от pixel position и нужны для
  игровой логики выбора клетки, не для отрисовки рамки.

SHA256 текущего SPG:

```text
4AE71211C7D2F8FE116C3F5E62CFB89FCD93BA7178EF2C8A8D2FB2A5AC0ECAE0
```

SHA256 текущего Core:

```text
1573F064F3108C1B1DEDE64ABF10F391B4A6CA7E7B501EE7C1C1B318674627E8
```

Проверено и инжектировано в:

```text
\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img
/GAMES/HEROES 2/HMM2VD2.SPG
```

## Milestone 2026-06-08: автоповтор keyboard/joystick медленнее

Изменение:

- mouse cursor не трогался;
- keyboard/joystick step остался `2 px`;
- cooldown после шага увеличен с `1` до `3` кадров, поэтому автоповтор стал
  в 2 раза медленнее предыдущего режима.

SHA256 текущего SPG:

```text
B9430ED6AE49CEBF29FC41007B5A4EB6D9B4022EA73F14AAFFFDEF473AA4C1EB
```

SHA256 текущего Core:

```text
D081D7C4BA49871F4BEB6E62F28D3D560C5DA36DE28E1DC07D63F2B06E482256
```

Проверено:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
python Source\Tools\verify_wc_spg.py --img "\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img" --src Build\hmm2_vdac2.spg --dir GAMES "HEROES 2" --name HMM2VD2.SPG
```

## Session close 2026-06-08

Пользователь подтвердил: текущий режим управления нормальный.

Зафиксированное состояние для следующей сессии:

- карта HMM2 выводится через host-side pseudo-DXT L4;
- курсор FT812 рисуется поверх карты без мусора;
- Kempston Mouse двигает рамку пиксельно;
- keyboard/joystick двигают рамку медленно: `2 px`, cooldown `3` кадра;
- `CursorTileX/CursorTileY` остаются производными от pixel position для логики
  выбранной клетки;
- актуальный `HMM2VD2.SPG` уже инжектирован в `wc.img` и проверен read-back.

Начинать следующую сессию с динамического игрового слоя поверх карты, не с
повторной отладки видеорежима, фона или cursor input.

## Milestone 2026-06-08: dynamic actor отключен в дефолтной сборке

Проверка dynamic actor показала неверный визуальный результат:

- `Source\Tools\dynamic_actor.py` извлекает один кадр `MINIHERO.ICN` из
  `HEROES2.AGG`, декодирует его в FT812 `ARGB4` и кладет в object pages.
- В первой версии actor был привязан к `CursorTileX/CursorTileY`, поэтому
  курсор визуально таскал за собой зеленый флаг.
- Даже после отвязки `MINIHERO.ICN` выглядел как лишний флаг поверх baked
  pseudo-DXT background.
- Поэтому `build.cmd` больше не включает dynamic actor по умолчанию.
  Включение только явное: `set HMM2_DYNAMIC_ACTOR=1` перед `build.cmd`.
- `dxt_background.py` при отключенном overlay чистит старые
  `Assets\Converted\Objects\SKIRMISH_OBJECTS_p*.bin`, чтобы не оставались
  stale pages от прежнего object layer.
- `test_cursor_input.py` снова проверяет только cursor input/translate.

Текущий runtime overlay поверх карты: только желтая рамка курсора. Object/hero
overlay не загружается и не пишется в DL.

Текущий `Build\hmm2_vdac2.spg` собран, проверен full-stack и инжектирован:

```text
\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img
/GAMES/HEROES 2/HMM2VD2.SPG
```

SHA256 текущего SPG:

```text
873A50CB113135B03F3801F457250DA23B6FCCA7E6BD80098FEBBBA033E55C45
```

SHA256 текущего Core:

```text
726895E30AF72549BBE487D61D302500E13258BBC8A50885391AB2686137EBD2
```

Проверено:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
python Source\Tools\verify_wc_spg.py --img "\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img" --src Build\hmm2_vdac2.spg --dir GAMES "HEROES 2" --name HMM2VD2.SPG
```

Следующий milestone: не использовать `MINIHERO.ICN` как временный actor поверх
baked background. Сначала нужен осмысленный отдельный hero/object state и
визуально проверенный sprite/placement, затем только включать overlay в
дефолтную сборку.

## Milestone 2026-06-08: первая игровая команда героя

Сделан первый минимальный playable-loop для adventure map без возврата
проблемного `MINIHERO.ICN`:

- `HeroTileX/HeroTileY` отделены от `CursorTileX/CursorTileY`.
- `HeroTargetX/HeroTargetY` ставятся по Fire из текущей клетки курсора.
- `HeroFireLatch` не дает переустанавливать цель каждый кадр при удержании Fire.
- `Hero_MoveTowardTarget` двигает героя к target по одной клетке с cooldown:
  сначала X, затем Y. Это простой placeholder до pathfinding.
- Поверх baked pseudo-DXT карты рисуется маленький FT812 marker героя:
  cyan центр с черной подложкой, без bitmap object pages и без ICN-флага.
- `Render_Frame` пишет background DL, затем hero marker DL, затем cursor DL,
  сохраняя один итоговый `FT_DISPLAY`.
- `test_hero_command.py` проверяет: Fire ставит target из cursor, hero state
  доходит до target, `HERO_MARKER_TRANSLATE_X/Y` соответствует tile position.

Текущий визуальный режим:

- baked pseudo-DXT карта;
- маленький cyan marker героя;
- желтая рамка cursor поверх всего.

Текущий `Build\hmm2_vdac2.spg` собран, проверен full-stack и инжектирован:

```text
\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img
/GAMES/HEROES 2/HMM2VD2.SPG
```

SHA256 текущего SPG:

```text
28C86BDD0403CC9319AFC7A33403BB58610E5049EE0C9679ECD89AC3B98E613C
```

SHA256 текущего Core:

```text
B98C8C967F58F967521DB8B61879E1E4ED57345E9C00929290AE3DFF75FAE3F1
```

Проверено:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\test_hero_command.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
python Source\Tools\verify_wc_spg.py --img "\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img" --src Build\hmm2_vdac2.spg --dir GAMES "HEROES 2" --name HMM2VD2.SPG
```

Следующий milestone: заменить прямолинейное X/Y движение на простейший
tile-path или хотя бы blocked/tile-cost check по compact map. Визуальный marker
оставить до подбора корректного hero sprite.

## Fix 2026-06-08: ЛКМ ставит цель движения героя

Пользователь увидел на железе только cyan marker и cursor; marker не двигался
при обычной мышиной работе.

Причина:

- `Input_Poll` для bit4 `InputState` вызывал `Input_FireKey`, то есть только
  `Space | Enter | Kempston-Fire`.
- ЛКМ была доступна через `Input_Fire`, но не попадала в compact adventure
  input state.

Исправление:

- В `Source\ASM\input.asm` `.fire` теперь вызывает `Input_Fire`, поэтому
  `Space`, `Enter`, `Kempston-Fire` и ЛКМ ставят команду движения.
- `test_hero_command.py` проверяет и Fire, и ЛКМ: target должен стать равен
  текущему cursor tile.

Текущее управление:

- двигать cursor: Kempston Mouse / keyboard / joystick;
- поставить цель героя: ЛКМ, Space, Enter или Kempston-Fire;
- cyan marker героя пошагово идет к выбранной клетке.

SHA256 текущего SPG:

```text
F12804C8A32C9A797279EDE020F69F36C2AC919A8837AD14B46DB118C4B17C94
```

SHA256 текущего Core:

```text
DA1949A571E7A9FE6B5F06E3200714A5D57C6D4474463EC685CE8EBA2A9D6856
```

Проверено:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\test_hero_command.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
python Source\Tools\verify_wc_spg.py --img "\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img" --src Build\hmm2_vdac2.spg --dir GAMES "HEROES 2" --name HMM2VD2.SPG
```

## Fix 2026-06-08: цель по центру курсора и плавный marker movement

Пользователь сообщил:

- hero marker не всегда приходит ровно в указанную позицию, чаще рядом;
- движение резкое, не как в оригинале.

Причины:

- `Cursor_UpdateTileFromPixel` считал tile по левому верхнему углу желтой
  рамки: `pixel / 32`. Около границы клетки это выглядело как выбор соседней
  позиции.
- `Hero_MoveTowardTarget` двигал `HeroTileX/Y` и сразу переставлял
  `HeroPixelX/Y` на `tile * 32`, то есть скачками по 32 px.

Исправление:

- cursor tile теперь считается по центру рамки: `(CursorPixel + 16) / 32`.
- hero marker двигается по пикселям с `HERO_STEP_PIXELS=2`, без 32-px скачков.
- target остается tile-based, но `HeroPixelX/Y` плавно идет к `target * 32`.
- `HeroTileX/Y` обновляется из текущего pixel position.
- Текущий motion всё ещё placeholder: движение по X, затем по Y. Это не
  оригинальный pathfinding Heroes II.

Важное инженерное замечание:

- Дальше нельзя продолжать “примерно похожую” механику. Следующий milestone
  должен брать reference из `OpenHMM2`/fheroes2: path построение, стоимость
  клеток, blocked tiles и нормальное пошаговое движение по path.

SHA256 текущего SPG:

```text
6B7A64B304349E7F2BD4A5B299962D827B4033C3018A5F7D64878650C9AC7877
```

SHA256 текущего Core:

```text
D4FD991810F1C86FF2CC394EFB9ED31BD58CE6EF4CE50B66A43EFF4E2B22382E
```

Проверено и инжектировано:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\test_hero_command.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
python Source\Tools\verify_wc_spg.py --img "\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img" --src Build\hmm2_vdac2.spg --dir GAMES "HEROES 2" --name HMM2VD2.SPG
```

## Fix 2026-06-08: убрать L-образную дерготню movement placeholder

Пользователь сообщил, что movement всё ещё дерганный и marker не всегда
приходит в указанную точку. Вывод: нельзя дальше подкручивать старую tile-step
заглушку.

Сделано:

- `Hero_MoveTowardTarget` больше не идет сначала по X, потом по Y.
- `HeroPixelX` и `HeroPixelY` теперь двигаются в один кадр одновременно к
  `HeroTargetX/Y * 32`.
- `HERO_STEP_PIXELS` уменьшен до `1`, чтобы marker не дергался 2-px скачками.
- `HeroTileX/Y` остаются производными от текущих `HeroPixelX/Y`.
- `test_hero_command.py` проверяет первый плавный диагональный шаг и точность
  выбора клетки около границы через `Cursor_UpdateTileFromPixel`.

Ограничение:

- Это всё ещё не оригинальная механика Heroes II. Настоящий следующий шаг:
  переносить pathfinding из `OpenHMM2\src\fheroes2\world\world_pathfinding.*`
  в упрощенный Z80/data-page формат, включая blocked tiles и path queue.

SHA256 текущего SPG:

```text
DB51FFE1E274507441B26841C4CACDA3369504FFDC22A4F21990E80B3F7FB169
```

SHA256 текущего Core:

```text
9CEAAB6F2A981B4499301FD9FEF37DED457E5E90C174F621F15B1C280D758684
```

Проверено и инжектировано:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\test_hero_command.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
python Source\Tools\verify_wc_spg.py --img "\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img" --src Build\hmm2_vdac2.spg --dir GAMES "HEROES 2" --name HMM2VD2.SPG
```

## Tuning 2026-06-08: медленнее marker movement и точнее ЛКМ target

Пользователь сообщил: анимацию можно сделать медленнее, точность повысилась,
но ещё не идеал.

Сделано:

- Добавлен `HeroMoveFrameGate`: marker двигается на 1 px не каждый frame, а
  через frame gate (`HERO_MOVE_FRAME_MASK=1`), то есть примерно вдвое медленнее.
- `Input_Poll` разделяет источники команды:
  - bit4: FireKey (`Space | Enter | Kempston-Fire`);
  - bit6: ЛКМ.
- Приоритет: если активен FireKey, mouse branch не используется в этот кадр.
- Для ЛКМ цель считается из `Input.Mouse.PositionX/Y`, а не из
  `CursorTileX/Y`. Это уменьшает рассинхрон “cursor обновился в другой момент”.
- `test_hero_command.py` проверяет frame gate, точный mouse-position target и
  border case около границы клетки.

SHA256 текущего SPG:

```text
2852BDBE549798F1AA2FC2B6E900D5EB0DB14059EFA5A6F9827A498F279FF55E
```

SHA256 текущего Core:

```text
BC02CE0223A47DA609D4690E8D2F14C0F0A82AFFA28F8E924C0D616F961C8194
```

Проверено и инжектировано:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\test_hero_command.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
python Source\Tools\verify_wc_spg.py --img "\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img" --src Build\hmm2_vdac2.spg --dir GAMES "HEROES 2" --name HMM2VD2.SPG
```

## Milestone 2026-06-08: tile-map mode + реальные object sprites

Пользователь запросил реальную карту со скроллом и реальные спрайты. Первый
обязательный шаг сделан: дефолтная сборка больше не использует baked
pseudo-DXT screenshot.

Изменения:

- `build.cmd` теперь по умолчанию строит tile-map mode:
  - `terrain_atlas.py` генерирует реальный `GROUND32.TIL` terrain atlas;
  - `tile_map_mode.py` пишет `generated_background.inc`, где
    `Background_Upload -> Terrain_Upload`;
  - `object_atlas.py` генерирует реальные semantic ICN object sprites и патчит
    `generated_adventure_dl.inc`.
- Старый baked pseudo-DXT background доступен только явно:

```text
set HMM2_BAKED_BG=1
build.cmd
```

- `Render_Actor` теперь собирается только при `DYNAMIC_ACTOR_RAMG`, потому что
  real object sprites уже вшиваются в `ADVENTURE_DL` самим `object_atlas.py`.
- `object_atlas.py` чистит stale `SKIRMISH_OBJECTS_p*.bin` перед записью.
- `verify_ft812_pipeline.py` корректно различает tile-map mode
  (`BG_DXT_RAW_SIZE=0`) и baked background mode.

Текущий full-stack DL:

- `CELL=300`
- `VERTEX2F=320`
- `VERTEX2II=0`
- `DISPLAY=1`
- terrain atlas: `239616` bytes
- object atlas: `7920` bytes, 8 placements, 5 unique sprites

Ограничение:

- Runtime scroll ещё не реализован. Текущий viewport всё ещё статический
  origin `0,0`, но теперь это реальная tile/object карта, а не screenshot.
- Следующий milestone должен быть именно `ViewportOriginX/Y` + runtime scroll
  или хотя бы tile-row/column paging, а не дальнейшая полировка hero marker.

SHA256 текущего SPG:

```text
F5448E80EAB238FE1226D63C9721ED35EEB26AFD8EAECB5150E2AEE986B6844E
```

SHA256 текущего Core:

```text
0D62564CC5B7E1FBDB4469606AA8D6C3121AF392166CFA1D50462B5784009B0F
```

Проверено и инжектировано:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\test_hero_command.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
python Source\Tools\verify_ft812_pipeline.py
python Source\Tools\verify_wc_spg.py --img "\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img" --src Build\hmm2_vdac2.spg --dir GAMES "HEROES 2" --name HMM2VD2.SPG
```

## Milestone 2026-06-08: рабочая опорная версия real map scroll + sprites + unified input

Пользователь подтвердил: "Всё работает".

Текущая рабочая версия:

- реальная карта HMM2 `SKIRMISH.MX2`, 36x36;
- реальный scroll карты;
- реальные terrain tiles `GROUND32.TIL`;
- реальные object sprites/overlay;
- реальный hero sprite `MINIHERO.ICN#8`;
- реальный cursor sprite `MOUSE.ICN#0`;
- cursor bounds 640x480: `CURSOR_MAX_X=624`, `CURSOR_MAX_Y=464`;
- hero movement нормальный: `HERO_STEP_PIXELS=2`;
- cursor keyboard/joystick movement быстрый: `CURSOR_STEP_PIXELS=16`;
- диагонали keyboard/joystick работают;
- весь ввод идет через единый `Source/ASM/input.asm`;
- fire работает с Space, Enter, Kempston-Fire и ЛКМ;
- ложный fire при запуске исправлен.

Критическое последнее исправление fire:

- `Input_FireKey` оставлен как в Zuma VDAC2: `Space | Enter | Kempston-Fire`;
- причина ложного fire была в полярности ЛКМ;
- `Input_MouseLMB` теперь после `Input.Mouse.KeyState` делает `CP Input.Mouse.SVK_LBUTTON` и `RET`, как в рабочем Zuma VDAC2;
- тестовая модель `hmm2_ft812_snapshot.py` выставляет `mouse_buttons=0x01` как отпущенную ЛКМ.

Опорная версия сохранена в формате Zuma releases, но только build/source:

```text
releases\v001-2026-06-08-real-map-scroll-sprites-input-baseline\
  Build\
  Source\
  build.cmd
  spgbld_vdac2.ini
```

Текущий SPG записан в образ:

```text
/GAMES/HEROES 2/HMM2VD2.SPG
```

SHA256 текущего SPG и файла в `wc.img`:

```text
FFA84D412477BCA3E3427D714CBFD734FDB13E7BFF597A0D1707DF4ABD4F8731
```

Проверено:

```text
.\build.cmd
python Source\Tools\test_hero_command.py
python Source\Tools\test_cursor_input.py
python Source\Tools\test_viewport_scroll.py
python Source\Tools\verify_wc_spg.py --img "\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img" --src Build\hmm2_vdac2.spg --dir GAMES "HEROES 2" --name HMM2VD2.SPG
```
## 2026-06-08: падение изображения на реальном мониторе

Сравнение с `C:\Users\Администратор\Desktop\Zuma Deluxe VDAC2` показало: `Init_Video.asm` у HMM2 и Zuma по сути одинаковый. Совпадают `FT_BOOT_UP`, `FT_CMD_RESET`, `FT_RESOLUTION VM_640_480_74Hz`, включение `FT_INT_SWAP` и `Video_Setting VID_FT812 | VID_NOGFX`. Значит первичная причина не в таймингах 640x480 и не в базовом включении FT812.

Вероятная ошибка находится в `Source/ASM/render.asm`, в конце `Render_Frame`:

```asm
                FT_RD_REG8 FT_REG_INT_FLAGS
                FT_WR_REG8 FT_REG_DLSWAP, FT_DLSWAP_FRAME
.WaitIntSwap:  FT_RD_REG8 FT_REG_INT_FLAGS
                AND  FT_INT_SWAP
                JR   Z, .WaitIntSwap
                RET
```

Проблемы этого паттерна:

- `FT_INT_SWAP` читается, но не очищается. Если флаг остался от предыдущего кадра, `.WaitIntSwap` может выйти сразу, не дождавшись swap текущего кадра.
- После `RET` следующий кадр сразу начинает новые `FT.WriteDL` в `RAM_DL`. На реальном FT812 это может писать поверх display list, который ещё не был безопасно засвапан/показан.
- HMM2 пишет display list напрямую через `FT.WriteDL` много раз за кадр. Это допустимо только при строгой синхронизации с `DLSWAP==0` и очищенным `INT_SWAP`. В текущем коде такой защиты нет.

У Zuma рабочий паттерн находится в `Source/ASM/MainLoop.asm`:

```asm
.WaitIntSync    FT_RD_REG8 FT_REG_INT_FLAGS
                AND  FT_INT_SWAP
                JR   Z, .WaitIntSync
                FT_WR_REG8 FT_REG_INT_FLAGS, FT_INT_SWAP
.WaitDLSwap     FT_RD_REG8 FT_REG_DLSWAP
                AND  3
                JR   NZ, .WaitDLSwap

                ; после этого писать новый кадр
                ; Zuma пишет через RAM_CMD/FT_CMD_Write_DMA или FT_CMD_Write
                CALL FT.Coprocessor.WaitFlush
                FT_WR_REG8 FT_REG_DLSWAP, FT_DLSWAP_FRAME
```

Минимальное исправление для HMM2: перед записью нового кадра ждать `FT_INT_SWAP`, очистить `FT_INT_SWAP`, дождаться `FT_REG_DLSWAP & 3 == 0`, только после этого делать все `FT.WriteDL`, затем ставить `FT_REG_DLSWAP = FT_DLSWAP_FRAME`.

Более надёжный путь: перевести основной кадр HMM2 на Zuma-подобный command FIFO паттерн: собрать кадр в Z80 command buffer через `FT_CMD_Start`, отправить через `FT_CMD_Write`/DMA, вызвать `FT.Coprocessor.WaitFlush`, затем `DLSWAP_FRAME`. Прямой `FT.WriteDL` оставить только для одноразового init/пустого DL или строго синхронизированных статических загрузок.

Почему тесты это не ловят: `build.cmd` и `Source/Tools/verify_ft812_pipeline.py` проверяют сборку, RAM_G и один валидный DL. Они не моделируют много кадров подряд со stale `FT_INT_SWAP` и записью в `RAM_DL` до завершения предыдущего `DLSWAP`, поэтому на эмуляторной проверке всё проходит, а на реальном мониторе изображение может падать.

## Fix 2026-06-08: синхронизация RAM_DL перед кадром

После записи соседа про падение изображения на реальном мониторе исправлен
паттерн `Render_Frame` в `Source/ASM/render.asm`.

Сделано:

- `Render_Frame` теперь начинает кадр с `Render_WaitSafeDL`.
- `Render_WaitSafeDL` ждёт `FT_INT_SWAP`, очищает его через
  `FT_WR_REG8 FT_REG_INT_FLAGS, FT_INT_SWAP`, затем ждёт
  `FT_REG_DLSWAP & 3 == 0`.
- Только после этого HMM2 пишет новый кадр в `RAM_DL` через `FT.WriteDL`.
- В конце кадра теперь только ставится `FT_REG_DLSWAP = FT_DLSWAP_FRAME`, без
  ожидания stale `INT_SWAP` после записи.
- Это минимально повторяет безопасную часть Zuma-паттерна для прямой записи в
  display list и должно убрать запись поверх ещё не засвапанного DL на реальном
  FT812.

Текущий физический видеорежим:

```text
FT_RESOLUTION VM_1024_768_59Hz, ResolutionWidthPtr
```

SHA256 текущего SPG и файла в `wc.img`:

```text
ACFE6E3672427894393860D549CA0802B3B9BE75FE91FC8D20D6D8F7C1150DFC
```

Проверено и инжектировано:

```text
.\build.cmd
python Source\Tools\test_hero_command.py
python Source\Tools\test_cursor_input.py
python Source\Tools\test_viewport_scroll.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
python Source\Tools\ZumaRef\inject_file_to_wc_img.py --img "\\tsclient\D\Работа.Андрей\unreal_x64 - HMM2\wc.img" --src Build\hmm2_vdac2.spg --dir GAMES "HEROES 2" --name HMM2VD2.SPG
```

## Рецепт из Zuma VDAC2 2026-06-11: гладкий V-Sync кадр через DMA

Проверенный на железе паттерн Zuma 1024x768: до его внедрения сцены меню
слали кадр медленным `OTIR` без vsync — курсор и скролл дёргались. После
перевода на vsync + DMA пользователь подтвердил: «Всё гладко, ничего не
лагает». Это готовый рецепт для `Render_Frame` HMM2 вместо прямого
`FT.WriteDL`.

Источники в Zuma:

```text
C:\Users\Администратор\Desktop\Zuma Deluxe VDAC2\Source\ASM\MenuMain.asm      ; MenuSwapFrame (~строка 473)
C:\Users\Администратор\Desktop\Zuma Deluxe VDAC2\Source\ASM\shared_render.asm ; ZL_FT_CMD_Write_DMA (~строка 263)
```

### Архитектура кадра

1. Кадр собирается НЕ прямой записью в `RAM_DL` (`FT.WriteDL`), а в Z80
   CMD-буфер копроцессора: вызовы `FT.Coprocessor.*` пишут команды в буфер
   по `CMD_ADDRESS_PTR`, хвост — `FT.Coprocessor.BufferPtr`.
2. Готовый буфер отправляется ОДНИМ DMA-трансфером (TS-Config `DMA_RAM_SPI`)
   в `FT_REG_CMDB_WRITE` — bulk-регистр FIFO копроцессора FT812.
3. Свап кадра строго по vsync.

### Последовательность свапа (MenuSwapFrame)

```asm
SwapFrame:
                ; (1) vsync: ждать INT_SWAP предыдущего кадра и ОЧИСТИТЬ флаг —
                ; stale-флаг без очистки даёт мгновенный выход из цикла и
                ; плавающую частоту кадров (дёрганье).
.wait_int:      FT_RD_REG8 FT_REG_INT_FLAGS
                AND  FT_INT_SWAP
                JR   Z, .wait_int
                FT_WR_REG8 FT_REG_INT_FLAGS, FT_INT_SWAP
                ; (2) убедиться, что предыдущий DLSWAP реально завершён
.wait_swap:     FT_RD_REG8 FT_REG_DLSWAP
                AND  3
                JR   NZ, .wait_swap
                ; (3) отправить собранный CMD-буфер кадра DMA-путём
                CALL ZL_FT_CMD_Write_DMA
                ; (4) дождаться, пока копроцессор всё переварил
                ; (REG_CMD_READ догнал REG_CMD_WRITE), и только потом свап
                CALL FT.Coprocessor.WaitFlush
                FT_WR_REG8 FT_REG_DLSWAP, FT_DLSWAP_FRAME
                RET
```

Требование: `FT_INT_SWAP` должен быть разрешён в `FT_REG_INT_MASK` при init
(Zuma-like `Init_Video` это уже делает).

### DMA-отправка CMD-буфера (ZL_FT_CMD_Write_DMA, дословно из Zuma)

Контракт: вызывать только после `WaitFlush` предыдущего кадра — тогда в
4К FIFO гарантированно есть место под весь кадр и `REG_CMDB_SPACE` опрашивать
не нужно. Буфер кадра должен целиком лежать в одной 16К странице
(`ZL_CMD_DMA_PAGE` / `ZL_CMD_DMA_ADDR = CMD_ADDRESS_PTR & #3FFF`).

```asm
ZL_CMD_DMA_PAGE EQU #05                                 ; страница Z80 CMD-буфера
ZL_CMD_DMA_ADDR EQU CMD_ADDRESS_PTR & #3FFF             ; смещение внутри страницы

ZL_FT_CMD_Write_DMA:
                FT_CMD_Count                            ; BC = байт в буфере
                LD   A, B
                OR   C
                RET  Z
                SRL  B                                  ; байты -> слова (DMA шлёт словами)
                RR   C
                LD   A, B
                LD   (ZL_CmdDmaWordsHi), A              ; полные чанки по 512 байт
                LD   A, C
                LD   (ZL_CmdDmaWordsLo), A              ; хвост в словах

                FT_ON                                   ; CS вниз
                ; SPI write-header FT812: addr[21:16]|#80, addr[15:8], addr[7:0]
                LD   A, ((FT_REG_CMDB_WRITE >> 16) & #FF) | #80
                OUT  (SPI_DATA), A
                LD   A, (FT_REG_CMDB_WRITE >> 8) & #FF
                OUT  (SPI_DATA), A
                LD   A, FT_REG_CMDB_WRITE & #FF
                OUT  (SPI_DATA), A

                ; источник DMA = CMD-буфер в странице ZL_CMD_DMA_PAGE
                LD   A, LOW ZL_CMD_DMA_ADDR
                LD   BC, DMASADDRL
                OUT  (C), A
                LD   A, HIGH ZL_CMD_DMA_ADDR
                LD   BC, DMASADDRH
                OUT  (C), A
                LD   A, ZL_CMD_DMA_PAGE
                LD   BC, DMASADDRX
                OUT  (C), A

                ; полные 512-байтовые чанки: DMALEN=255 (256 слов), DMANUM=чанки-1
                LD   A, (ZL_CmdDmaWordsHi)
                OR   A
                JR   Z, .tail
                DEC  A
                LD   BC, DMANUM
                OUT  (C), A
                LD   A, #FF
                LD   BC, DMALEN
                OUT  (C), A
                LD   A, DMA_RAM_SPI
                LD   BC, DMACTR
                OUT  (C), A
.wait_full:     LD   BC, DMASTATUS
                IN   A, (C)
                AND  DMA_WNR
                JR   NZ, .wait_full

.tail:          LD   A, (ZL_CmdDmaWordsLo)              ; хвост < 512 байт
                OR   A
                JR   Z, .done
                DEC  A
                LD   BC, DMALEN
                OUT  (C), A
                XOR  A
                LD   BC, DMANUM
                OUT  (C), A
                LD   A, DMA_RAM_SPI
                LD   BC, DMACTR
                OUT  (C), A
.wait_tail:     LD   BC, DMASTATUS
                IN   A, (C)
                AND  DMA_WNR
                JR   NZ, .wait_tail

.done:          FT_OFF                                  ; CS вверх
                RET

ZL_CmdDmaWordsHi: DEFB 0
ZL_CmdDmaWordsLo: DEFB 0
```

### Грабли, на которые уже наступали в Zuma

- Неочищенный `FT_INT_SWAP` — главная причина «всё дёргается»: цикл ожидания
  выходит мгновенно по флагу прошлого кадра, частота сцены плавает.
- `OTIR`-отправка большого кадра занимает миллисекунды CPU и не привязана к
  vsync — даже при правильном ожидании свапа курсор/скролл видимо дрожат.
  DMA шлёт тот же кадр на порядок быстрее.
- `DLSWAP_FRAME` ставить только ПОСЛЕ `FT.Coprocessor.WaitFlush`, иначе свап
  уходит раньше, чем копроцессор дописал DL.
- Хелпер обязан быть РЕЗИДЕНТНЫМ (в Core), если его зовут из разных
  страниц-сцен: вызов хелпера из переключаемой страницы при другом slot3 =
  краш (PC уезжает в чужую страницу). Для HMM2 это согласуется с Правилом №2:
  сам хелпер маленький — место в Core оправдано.
- Если один трансфер может превысить свободное место FIFO (большие заливки
  в RAM_G, не кадр), нужен чанкованный путь с опросом `REG_CMDB_SPACE`; для
  покадрового DL при контракте «после WaitFlush» это не нужно.

## Fix 2026-06-11: runtime кадр через VSync + DMA CMD-buffer

Переведён текущий `RUNTIME_TILEMAP_RENDER` путь HMM2 на проверенный Zuma-паттерн
гладкого кадра:

- `Render_RuntimeFrameCmd` больше не шлёт куски кадра в FIFO через
  `FT.Coprocessor.Write/Write32` по ходу сборки.
- Кадр сначала собирается в локальный CMD-буфер TSLib через `FT_CMD_Start`,
  `Render_CmdBufCopy` и `Render_CmdBufWrite32`.
- CMD-буфер размещён по `CMD_ADDRESS_PTR=#9000` через `define`, чтобы макросы
  TSLib действительно использовали этот адрес. Это page `CorePage+1` (`#06`),
  offset `#1000`, целиком в одной 16К странице для DMA.
- `RUNTIME_DL_BUFFER` и CMD-буфер намеренно используют один адрес `#9000`
  последовательно: сначала runtime scratch DL копируется в `RAM_G`, затем поверх
  него собирается CMD-буфер кадра.
- `Render_SwapFrameDMA` делает:
  wait `FT_INT_SWAP` -> clear `FT_INT_SWAP` -> wait `FT_REG_DLSWAP&3==0` ->
  `Render_CMD_Write_DMA` -> `FT.Coprocessor.WaitFlush` ->
  `FT_REG_DLSWAP=FT_DLSWAP_FRAME`.
- `Render_CMD_Write_DMA` отправляет CMD-буфер одним `DMA_RAM_SPI` трансфером в
  `FT_REG_CMDB_WRITE`.
- В `render.asm` добавлены ASSERT-ы: runtime CMD-frame должен быть `<=4096`
  байт и не пересекать 16К DMA-страницу.

Важно по архитектуре большой игры:

- DMA/swap-хелпер оставлен резидентным как маленький общий хелпер, что
  соответствует Правилу №2.
- Крупные данные/таблицы/ассеты не перенесены в Core.
- Если будущий кадр станет больше 4К FIFO, нельзя молча расширять буфер в Core:
  нужен либо новый компактный baked CMD-блок, либо чанкованный DMA путь с
  опросом `REG_CMDB_SPACE`.

Для тестов:

- `Source\Tools\hmm2_ft812_snapshot.py` теперь ставит локальный
  `Source\Tools` перед Zuma `Source\OTHER` в `sys.path`, чтобы использовать
  HMM2 wrapper `shadow_ft812.py`.
- Локальный `Source\Tools\shadow_ft812.py` оборачивает Zuma shadow-модель, но
  не перехватывает FIFO-регистры `REG_CMDB_SPACE/REG_CMDB_WRITE`, иначе
  DMA/FIFO кадр в harness не исполняется.
- В HMM2 harness добавлена модель TS-Config `DMA_RAM_SPI`, аналогичная Zuma.
- `test_hero_command.py` и `test_cursor_input.py` синхронизированы с реальной
  scale table: `vertex = (pixel*8*16)//5` без округления.

Проверено:

```text
.\build.cmd
python Source\Tools\test_hero_command.py
python Source\Tools\test_cursor_input.py
python Source\Tools\test_viewport_scroll.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
```

`verify_ft812_pipeline.py` видит:

```text
DL counts: CELL=339 VERTEX2F=349 VERTEX2II=0 DISPLAY=1
физический режим: hsize=1024 vsize=768
```

Важно: это не пересчёт игровой логики в 1024×768. Координаты, курсор и
viewport остаются логическими 640×480; FT812 показывает их в 1024×768 через
nearest upscale 8/5.

SHA256 текущего SPG:

```text
E972AAE1EF4FD71276596FD0BDBC70280271F9614D6F22208424A4CA10760A37
```

SHA256 текущего Core:

```text
5646D451C0516769A98271E8F7F342569CEEAD4768BCB68193C9D8C8960080F2
```

## Fix 2026-06-11: убрать рывки scroll/cursor на runtime static upload

После перехода runtime-кадра на VSync + DMA оставались рывки при scroll карты и
движении мышиного курсора. Причина: основной CMD-кадр уже отправлялся DMA, но
`Runtime_UploadStaticIfDirty` при смене tile-origin всё ещё заливал runtime
static DL-блоки в `RAM_G=#0A0000` через медленный `FT.WriteMem`:

- left tile DL block: `RUNTIME_LEFT_DL_BYTES`
- right tile DL block: `RUNTIME_RIGHT_DL_BYTES`
- object static DL block: `OBJECT_VIEW_DL_SIZE - 4`

Эта заливка происходила на границах tile-page и могла выбивать frame budget,
из-за чего визуально дёргались и карта, и курсор.

Сделано:

- добавлен `Render_WriteMem_DMA` для runtime-заливки RAM->FT812 через
  `DMA_RAM_SPI`;
- `Runtime_UploadStaticIfDirty` теперь грузит left/right static DL blocks в
  `RAM_G` через DMA из page `CorePage+1`, offset `RUNTIME_DL_BUFFER`;
- `Runtime_UploadObjectStatic` теперь грузит object static DL block через DMA
  из фактической object-view page, а не через `FT.WriteMem`;
- физический FT812 режим остаётся `1024x768`;
- логический input/viewport остаётся `640x480`, nearest upscale `8/5`;
- `ResolutionWidthPtr/HeightPtr` намеренно остаются `640/480`, потому что их
  использует input/Kempston Mouse для логического clamp. Физический режим
  проверяется по FT shadow-регистрам, не по этим input-переменным.

Проверено:

```text
.\build.cmd
python Source\Tools\test_hero_command.py
python Source\Tools\test_cursor_input.py
python Source\Tools\test_viewport_scroll.py
```

`verify_ft812_pipeline.py` видит:

```text
DL counts: CELL=340 VERTEX2F=359 VERTEX2II=0 DISPLAY=1
физический режим: hsize=1024 vsize=768 pclk=2
```

SHA256 текущего SPG:

```text
873E9ED77B3C34AAB4C28AF69229C6E6C7C5737AE8D51FCAF71323C008FF368E
```

SHA256 текущего Core:

```text
60BB319B37F222A227CF33F70301A50401C0339EEF6CCE83732C956071B0010D
```

## Fix 2026-06-11: плавный cursor keyboard/joystick

После DMA-фиксов пользователь подтвердил, что игра работает, но cursor при
управлении клавиатурой/джойстиком всё ещё двигается дёргано.

Причина в `Source\ASM\game_state.asm`:

- `CURSOR_STEP_PIXELS=16`;
- после каждого keyboard/joystick шага ставился `CursorMoveCooldown=3`;
- итог: видимый скачок на 16 px раз в несколько кадров.

Сделано:

- `CURSOR_STEP_PIXELS=4`;
- после keyboard/joystick шага cooldown теперь `0`;
- удержание направления двигает cursor и edge-scroll каждый кадр маленьким
  шагом, без автоповторных рывков;
- mouse path не менялся: мышь по-прежнему ставит абсолютную pixel-позицию.

Проверено:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\test_viewport_scroll.py
python Source\Tools\test_hero_command.py
```

SHA256 текущего SPG:

```text
3417F290DC91E0C3217A5C3800410579F618C6D74CBA5AF161AD05FD94F89886
```

SHA256 текущего Core:

```text
2F311836FCF68FCF0EDB2805CCF3903AFC89FD1E0BE1D7E779137C0A49FAD61A
```

## Fix 2026-06-12: keyboard/joystick не перебивается шумом мыши

После уменьшения шага cursor до 4px пользователь снова сообщил, что
управление с клавиатуры и джойстика дёргается.

Причина: `Cursor_Update` сначала вызывал `Cursor_UpdateFromMouse`. Если
Kempston Mouse или порт мыши давал мелкое изменение координаты в тот же кадр,
mouse-path возвращал Carry, и keyboard/joystick movement в этом кадре вообще не
выполнялся. На удержании направления это выглядит как нерегулярный пропуск
шагов.

Сделано:

- `Cursor_Update` теперь сначала смотрит `InputState & %00001111`;
- если есть направление keyboard/joystick, mouse absolute update полностью
  пропускается, и cursor двигается регулярным 4px-шагом каждый кадр;
- mouse-path используется только когда направлений keyboard/joystick нет;
- `test_cursor_input.py` добавлен регрессионный случай: при удержанном
  Kempston Right меняется координата мыши, но cursor обязан сдвинуться на 4px,
  а не прыгнуть в mouse absolute position.

Проверено:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\test_viewport_scroll.py
python Source\Tools\test_hero_command.py
```

`verify_ft812_pipeline.py` видит:

```text
физический режим: hsize=1024 vsize=768 pclk=2
```

Важно: режим по-прежнему физически `1024x768`, логический input/viewport
остаётся `640x480` и выводится через nearest upscale `8/5`. В `wc.img` файл не
заливался.

SHA256 текущего SPG:

```text
3785C0CCDF41FC0CA1F2AADE325C17B79544EE7740F7D17103A9E4F831821767
```

SHA256 текущего Core:

```text
304E3D13F5B39B93475F9ECE79025CE2B19873F1900DF23D384EFF7B6EDC2CD8
```

## Fix 2026-06-12: стабильный update-tick, плавный hero, чистый старт input

Пользователь сообщил, что дёргаются уже hero movement и scroll карты, а в
начале управление с клавиатуры глючит.

Найдено три причины в runtime loop/input:

- `MainLoop` делал `Input_Poll -> Game_Update -> Render_Frame`, а ожидание
  `FT_INT_SWAP` было спрятано внутри `Render_Frame`. При переменной цене
  рендера/static upload момент симуляции плавал относительно vsync.
- `Hero_MoveTowardTarget` имел `HERO_MOVE_FRAME_MASK=1`, то есть сам
  намеренно двигался только через кадр.
- `Input_Init` включал PS/2, но не очищал явно все tracked-флаги клавиш и
  `InputState`, что могло давать мусорное состояние в первые кадры.

Сделано:

- добавлен `Render_BeginFrameSync`: wait `FT_INT_SWAP`, clear `FT_INT_SWAP`,
  wait `FT_REG_DLSWAP&3==0`;
- `MainLoop` теперь сначала делает `Render_BeginFrameSync`, потом
  `Input_Poll`, `Game_Update`, `Render_Frame`;
- runtime `Render_Frame` больше не ждёт vsync второй раз, а только собирает
  CMD-frame и вызывает `Render_SubmitFrameDMA`;
- старый `Render_SwapFrameDMA` оставлен совместимым helper-ом: он сам вызывает
  `Render_BeginFrameSync`, затем `Render_SubmitFrameDMA`;
- `HERO_MOVE_FRAME_MASK=0`: hero делает `HERO_STEP_PIXELS=2` каждый кадр, без
  искусственного стоп-кадра;
- `Input_Init` вызывает `Input_ClearState`, который чистит `InputState`,
  `Input_K*`, `Input_PS2Brk`, `Input_DrainCnt`.

Проверено:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\test_viewport_scroll.py
python Source\Tools\test_hero_command.py
```

`verify_ft812_pipeline.py` видит:

```text
физический режим: hsize=1024 vsize=768 pclk=2
```

Важно: физический режим остался `1024x768`, логический viewport/input остался
`640x480` через nearest upscale `8/5`. В `wc.img` файл не заливался.

SHA256 текущего SPG:

```text
F9D4C5A2F1C971E7A388773E69620ACD0AE7954C4867111306F8733812E7188C
```

SHA256 текущего Core:

```text
684762E8809ADC493AF867B2E3DCDDE009A59F580EA8C3F79781CB8C110E210D
```

## Fix 2026-06-12: убрать физическую дрожь nearest 8/5 и стартовый PS/2 мусор

Пользователь повторно сообщил: в начале глючит keyboard input, hero movement и
scroll карты дёрганные.

Найдено:

- при логическом шаге `4px` cursor/scroll в физическом `1024x768` nearest
  `8/5` получается `6.4px`, то есть фактический вывод чередует 6/7 физических
  пикселей;
- это видимая физическая дрожь даже при идеальном vsync;
- `Input_Init` чистил state до включения PS/2, но не выкидывал байты, которые
  могли появиться в FIFO сразу после `PS/2 ON`.

Сделано:

- `CURSOR_STEP_PIXELS=5`: cursor и edge-scroll идут ровно `8` физических
  пикселей за кадр при nearest `8/5`;
- `HERO_STEP_PIXELS` возвращён к `2`: скорость героя менять нельзя без
  отдельного запроса пользователя; если hero визуально дрожит, нужен отдельный
  smooth/render-accumulator путь без изменения gameplay speed;
- добавлен `Input_DiscardPS2Fifo`: после `PS/2 ON` дренирует до 64 байт из
  регистра `#F0` без выставления key-флагов;
- после discard повторно вызывается `Input_ClearState`, чтобы стартовые
  `Input_K*`, `Input_PS2Brk`, `Input_DrainCnt`, `InputState` были нулевые;
- тесты обновлены на контракт `5px/кадр`.

Важно:

- физический FT812 режим остаётся `1024x768`;
- логический viewport/input остаётся `640x480`;
- это не пересчёт логики в 1024, а подбор runtime-шагов, кратных знаменателю
  upscale `8/5`, чтобы nearest не чередовал физические дельты.

Проверено:

```text
.\build.cmd
python Source\Tools\test_cursor_input.py
python Source\Tools\test_viewport_scroll.py
python Source\Tools\test_hero_command.py
```

`verify_ft812_pipeline.py` видит:

```text
физический режим: hsize=1024 vsize=768 pclk=2
```

В `wc.img` файл не заливался.

SHA256 текущего SPG:

```text
4C662D7254083E00E42032C344D6CB6C543E93DDA1DEFB954F8BAF0F0C748933
```

SHA256 текущего Core:

```text
CF84845B0417D2C04AB085376AF2CC16BEBE89734C777F81CDE3EE41DA00475E
```

## Fix 2026-06-12: дёргание курсора/героя/скролла — кадровый конвейер (фикс от соседа Zuma VDAC2)

Симптом: всё двигающееся (курсор, герой, скролл карты) шло рывками.

Две причины в runtime-кадре:

1. Vsync-ожидание стояло В НАЧАЛЕ MainLoop, а свап армировался В КОНЦЕ
   Render_Frame — после input/update/сборки кадра/DMA. На тяжёлых кадрах
   (скролл = пересборка tilemap-буфера + DMA-заливки RAM_G) армирование
   проскакивало границу кадра, и свап уезжал на следующую: период прыгал
   74<->37 Гц = видимые рывки.
2. Двойной механизм свапа: в CMD-поток писался `CMD_SWAP` (#FFFFFF01), а
   после `WaitFlush` ещё и ручной `REG_DLSWAP=FRAME`. Если свап копроцессора
   исполняется ровно на границе кадра, ручная запись армирует ВТОРОЙ свап —
   обратно на старый DL -> периодический «кадр назад».

Исправление (паттерн Zuma VDAC2, проверен там на меню/level-select):

- `MainLoop`: `Render_BeginFrameSync` убран из начала цикла.
- `Render_RuntimeFrameCmd`: `CMD_SWAP` больше НЕ пишется в поток;
  вместо `Render_SubmitFrameDMA` вызывается `Render_SwapFrameDMA`
  (= BeginFrameSync -> DMA -> WaitFlush -> ручной DLSWAP).
- Итоговый порядок: input/update/сборка кадра идут, ПОКА показывается
  предыдущий кадр; vsync-ожидание — непосредственно перед DMA-отправкой;
  свап армируется сразу после vsync и всегда успевает к следующей границе.

Правило: механизм свапа — ОДИН (ручной REG_DLSWAP после WaitFlush); ожидание
INT_SWAP (+очистка) и DLSWAP&3==0 — непосредственно перед отправкой кадра,
не в начале игрового цикла.

Модель эмулятора: `hmm2_ft812_snapshot.py` `_process_cmd_dlstart` теперь
догоняет `REG_CMD_READ` до `REG_CMD_WRITE` и без `CMD_SWAP` (копроцессор
потребляет поток мгновенно) — иначе `WaitFlush` вис в тестах.

SHA256 текущего SPG (1361408 байт, инжектирован и сверен read-back):

```text
3610CF8D08262C0055EA9E3B2F287C58D884E817FB2FA28A20EE64501A34FA1E
```

## Fix 2026-06-12: направление героя через FT812 bitmap transform

Пользователь указал, что герой не должен ехать «попой вперёд»: при смене
горизонтального направления sprite нужно зеркалировать.

Сделано через FT812 display-list/coprocessor path, без второго mirrored bitmap
в RAM_G и без CPU-перерисовки:

- добавлен `HeroFacingRight` в resident state;
- при выборе следующего tile движения `Hero_TryStepCandidate` обновляет
  `HeroFacingRight`: шаг вправо -> `1`, шаг влево -> `0`, вертикальное движение
  сохраняет прошлое направление;
- `HERO_MARKER_DL` теперь содержит patchable `BITMAP_TRANSFORM_A` и
  `BITMAP_TRANSFORM_C`;
- влево: `A=160`, `C=0`;
- вправо/mirror: `A=-160` (`#1501FF60`), `C=(HERO_SPRITE_W-1)*256`;
- `Render_HeroMarkerCmd` по-прежнему копирует DL в CMD-buffer, который уходит
  через DMA в FT812, то есть mirror выполняется самим FT812;
- `hmm2_ft812_snapshot.py` теперь трактует `BITMAP_TRANSFORM_A/E` как signed
  17-bit, `BITMAP_TRANSFORM_C` как signed 24-bit и применяет C-offset при
  bitmap sampling.

Также в начальном passability/path-step слое исправлен offset compact map tile:
`map_object` находится по `header 10 + tile offset 9`, то есть `#C000+19`.
Предыдущий `#C000+18` читал `terrain_flags`.

Проверено:

```text
.\build.cmd
python Source\Tools\test_hero_command.py
python Source\Tools\test_cursor_input.py
python Source\Tools\test_viewport_scroll.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
```

Snapshot видит:

```text
теневая модель: swaps=1 записей_dlswap=1
BITMAP_TRANSFORM_C=1
DISPLAY=1
физический режим: hsize=1024 vsize=768 pclk=2
```

В `wc.img` файл не заливался.

SHA256 текущего SPG:

```text
B2D6AFC29C8E0AF294C7BCA1038C86176D7359EAF5BBFDEF4C21DF62B9B88D59
```

SHA256 текущего Core:

```text
BB24FA0CB54637B4ABB6AF5DDE0C51B97B40DC02EABD020D8933173D0EADE153
```

## Fix 2026-06-12: направление MINIHERO и сброс transform C перед cursor

После первого mirror-fix пользователь сообщил:

- герой всегда едет «попой вперёд»;
- после зеркалирования пропадает mouse cursor.

Причины:

- реальный `MINIHERO.ICN#8` в текущем наборе по умолчанию ориентирован вправо,
  а первый фикс зеркалировал именно `HeroFacingRight=1`;
- `BITMAP_TRANSFORM_C` — состояние FT812 bitmap transform. После hero mirror
  cursor DL сбрасывал `A/E`, но не сбрасывал `C`, поэтому cursor sampling
  уезжал и sprite пропадал.

Сделано:

- `HeroFacingRight=1` теперь идёт обычным sprite (`A=160`, `C=0`);
- `HeroFacingRight=0` зеркалит героя (`A=-160`, `C=(HERO_SPRITE_W-1)*256`);
- в `CURSOR_DL` добавлен явный `FT_BITMAP_TRANSFORM_C 0`;
- правило на будущее: после любого bitmap mirror/offset обязательно сбрасывать
  `BITMAP_TRANSFORM_C` перед следующим bitmap, если следующий bitmap не
  задаёт свой `C`.

Проверено:

```text
.\build.cmd
python Source\Tools\test_hero_command.py
python Source\Tools\test_cursor_input.py
python Source\Tools\test_viewport_scroll.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
```

Snapshot видит:

```text
теневая модель: swaps=1 записей_dlswap=1
BITMAP_TRANSFORM_C=2
DISPLAY=1
физический режим: hsize=1024 vsize=768 pclk=2
```

`BITMAP_TRANSFORM_C=2` — ожидаемо: один C для hero mirror path и один явный
сброс C перед cursor.

В `wc.img` файл не заливался.

SHA256 текущего SPG:

```text
8C8DA5A4E588C20A80DA2E0E85C5A1DAB6F77BD7B776D57FE186BF388E2429C9
```

SHA256 текущего Core:

```text
BE591905AEEE142233F93F1FF5287A6B6BB4CFCD900AD3B20A8248E94D654D1A
```

Проверено:

```text
.\build.cmd                                  (verify_ft812_pipeline: OK, DL contract OK)
python Source\Tools\test_cursor_input.py     OK
python Source\Tools\test_hero_command.py     OK
python Source\Tools\test_viewport_scroll.py  OK
python Source\Tools\hmm2_ft812_snapshot.py   swaps=1, DISPLAY=1
```

## Fix 2026-06-12: BFS-путь героя и страничная рабочая память

После вывода карты/героя/спрайтов добавлен первый слой маршрутизации героя по
тайлам карты:

- клик/Fire теперь строит путь по `map_object` из compact map;
- `map_object != 0` считается непроходимым, offset объекта: `#C000 + 19 +
  tile*20`;
- путь строится BFS по 8 направлениям;
- первый сосед имеет приоритет диагонали в сторону цели, чтобы герой стартовал
  как в прежнем прямом движении, без ортогонального "крюка";
- скорость героя не менялась: `HERO_STEP_PIXELS=2`;
- направление спрайта обновляется от следующего waypoint: вправо обычный
  `MINIHERO.ICN#8`, влево mirror через FT812 transform.

Память организована странично, без экономии внутри Core:

- `#9000` в page `CorePage+1` остается только runtime CMD/DL scratch
  (`CMD_ADDRESS_PTR`/`RUNTIME_DL_BUFFER`);
- в `main.asm` добавлен `ASSERT CoreEnd <= CMD_ADDRESS_PTR`, чтобы Core больше
  не мог тихо залезть в `#9000`;
- LUT nearest upscale `8/5` вынесена из Core в отдельную SPG/RAM page `#12`
  (`Build/scale8_5_x16.bin`), читается через slot3;
- BFS scratch вынесен в рабочую RAM page `#13`, мапится в slot3 только на время
  `Hero_BuildPath`;
- `Map_IsTilePassable` временно мапит page `#10` с картой и восстанавливает
  предыдущую slot3 page, поэтому во время BFS корректно возвращает page `#13`;
- page `#13` не грузится из SPG: parent/queue buffers полностью
  инициализируются при каждом построении пути.

Страницы:

```text
#12: scale8_5_x16.bin, LUT 1024 words для Render_ScaleHL_8_5_ToVertex
#13: runtime-only BFS scratch, PATH_PARENT_BUF/PATH_QUEUE_X/Y at #C000
```

Проверено:

```text
.\build.cmd
python Source\Tools\test_hero_command.py
python Source\Tools\test_cursor_input.py
python Source\Tools\test_viewport_scroll.py
python Source\Tools\hmm2_ft812_snapshot.py --out Diagnostics\hmm2_ft812_snapshot.png
```

Snapshot:

```text
теневая модель: swaps=1 записей_dlswap=1
DISPLAY=1
BITMAP_TRANSFORM_C=2
физический режим: hsize=1024 vsize=768 pclk=2
```

В `wc.img` файл не заливался.

SHA256 текущего SPG:

```text
85D8DC1D127B48FCC79338B36C8F7F5E88C20BCA73E635EED6F813A4C507D7D7
```

SHA256 текущего Core:

```text
DB53F53C919C2791CEE3E1EB1F465FF2946E633311BAB317DCD4B049C9CFB372
```

SHA256 scale LUT:

```text
E684B964B4E5E1CF7EF27CE9FD5D4B1FAA7D786568B371BD2E3B73C9E9704C6E
```
## 2026-06-12: passability только через OpenHMM2 object info

Ложный обход героя на экране с городом/ресурсами был вызван не оригинальной логикой, а временной маской проходимости в `Source/Tools/map_tools.py`: object parts классифицировались грубыми ICN/map_object эвристиками. Из-за этого часть resource/action/shadow/terrain деталей попадала в маску как препятствие (`F8/00`) и BFS строил обход вокруг неоригинальной "стены".

Исправление: добавлен build-time dumper `Source/Tools/dump_fheroes2_object_info.cpp`, который собирается clang/LLVM и читает настоящую таблицу `OpenHMM2/src/fheroes2/maps/map_object_info.cpp`. Его CSV-вывод сохранен в `Assets/Converted/Maps/fheroes2_object_info.csv`; `map_tools.py` теперь берет `object_type` для `(icnType, icnIndex)` из этой таблицы. Если CSV отсутствует, конвертер должен падать, а не возвращаться к эвристикам.

Отладочный path overlay FT812 остается включенным: он нужен для визуального контроля, что путь не строится по ложной маске. В образ `wc.img` ничего не заливалось.

## 2026-06-12: синхронизация скролла фона и спрайтов

После перехода на pseudo-DXT фон карты и runtime/object слой могли ехать не
синхронно. Причины были две:

- `BG_DXT_ANCHORED_WINDOW` генерируется как `EQU 1`, поэтому в asm нельзя
  проверять его через `ifdef`; нужно `if BG_DXT_ANCHORED_WINDOW`. Иначе фон
  использовал старый `ViewportPixel & 31` и сбрасывался каждые 32 пикселя
  вместо смещения относительно загруженного якорного окна.
- `Runtime_NegativePixelRemainderToHL` считал `VERTEX_TRANSLATE` для tile/object
  слоя как старое логическое `rem * 16`. При физическом режиме 1024x768 и
  nearest upscale `8/5` это неверно: object layer должен получать
  `rem * 8/5 * 16`, как и остальные vertex-координаты.

Исправление:

- в `Source/ASM/render.asm` обе проверки anchor-window сделаны через
  `if BG_DXT_ANCHORED_WINDOW`;
- `Runtime_NegativePixelRemainderToHL` теперь берет `rem = ViewportPixel & 31`,
  вызывает существующую `Render_ScaleHL_8_5_ToVertex`, затем меняет знак;
- аппаратную инициализацию FT812/VDAC2 не трогать;
- отладочный path overlay не убирать.

Добавлен/усилен тест `Source/Tools/test_background_scroll_monotonic.py`:

- фон должен монотонно совпадать с `ViewportPixelX`;
- `RuntimeDL_ObjectTranslateX/Y` проверяется в реальных FT812 vertex units:
  ожидается `-((ViewportPixel & 31) * 128 // 5)`.

Проверено:

```text
.\build.cmd
cmd /c python Source\Tools\test_background_scroll_monotonic.py
python Source\Tools\test_viewport_scroll.py
python Source\Tools\test_cursor_input.py
python Source\Tools\test_hero_command.py
python Source\Tools\probe_ft_frequency_writes.py
```

Результат:

```text
background scroll transform монотонен и совпадает с ViewportPixelX
viewport scroll state идет 5px/кадр, tile-page меняется только на границе 32px
Kempston Mouse двигает пиксельно, cursor FT812 translate совпадает
Fire/ЛКМ ставят точную цель, hero state и marker плавно идут к target
записей REG_FREQUENCY нет
```

SHA256 `Build\hmm2_vdac2.spg` после фикса:

```text
A85B763BEE0AFBBE71D48D4EEE3CCB9243C4F6E0E391E95627362C138BDFE945
```

В `wc.img` файл не заливался.

## Fix 2026-06-12: рябь фона при скролле — BILINEAR на цветовых плоскостях DXT (фикс от соседа Zuma VDAC2)

Симптом: при скролле карты pseudo-DXT фон «подглючивает» — рябь/мерцание на
границах 4x4-блоков, меняющееся с фазой скролла.

Корень: в `generated_dxt_scroll_dl.inc` цветовые плоскости c0/c1 (passes 2/3)
рисовались с `FT_BILINEAR`. Интерполятор смешивает цвета СОСЕДНИХ DXT-блоков
ДО применения маски-селектора, а скролл-матрица цветов несёт дробную фазу
(offset/4 с дробями .25/.5/.75) — при движении смесь «дышит» на границах
блоков. Декод DXT требует ПО-БЛОЧНОЙ выборки цветов: c0/c1 — только NEAREST
(маска и так NEAREST). Исправлено в `dxt_l4_scroll_buffer.py` (генератор) и в
сгенерированном inc.

ВТОРАЯ проблема в этом же тракте (диагноз, НЕ исправлена): перезаливка
якорного окна. При пересечении якоря (8 тайлов по X / 7 по Y)
`BackgroundDxt_DoUpload` синхронно копирует ВСЁ окно 896x704 = 473088 байт
~1056 по-строчными DMA-транзакциями (каждая со своим SPI-заголовком) — это
сотни миллисекунд, в течение которых:
1) игра заморожена (upload до сборки кадра);
2) ЭКРАН продолжает сканировать показанный DL, ссылающийся на ТУ ЖЕ
   область RAM_G -> на экране смесь старого/нового окна и рассинхрон
   маска/цвета = вспышка мусора на каждом пересечении якоря.

Варианты решения (по убыванию качества):
- FULLMAP с маской L2 (2 бита — как настоящий DXT1): 1152x1152 фон целиком
  в RAM_G = 331776 (цвета) + 331776 (маска L2) = 648K + ~105K
  (DL-полосы/объекты/спрайты) — помещается в 1 МБ. Скролл становится ЧИСТО
  матричным, заливок при скролле НЕТ вообще. Требует: энкодер маски L2 в
  dxt_l4_fullmap_source.py, FT_L2 layout в DL, переразметку RAM_G
  (DL-полосы выше #A2000). С L4-маской fullmap НЕ влезает (995328 + 105K > 1M).
- Двойная буферизация окна: 2x473K = 946K — с объектами/DL-полосами
  НЕ помещается в 1 МБ без жертв.
- Минимум: на время DoUpload свопать кадр без bg-пассов (вспышка одноцветного
  фона вместо мусора) + слить по-строчные DMA в меньшее число транзакций.

Правило (из Zuma): показанный DL ссылается на RAM_G живьём — НЕЛЬЗЯ
перезаписывать область, на которую ссылается отображаемый кадр; либо
двойной буфер, либо кадр-без-ссылок на время заливки.

Проверено: build.cmd (verify OK, DL contract OK), test_cursor_input,
test_hero_command, test_viewport_scroll — OK. SPG инжектирован и сверен:

```text
A06FEC7687EF0F3044408AF407DC4854BD287D818DD7F55B4C9B01F52D2D5A8E
```

## Запись 2026-06-14: не трогать MONS32 random markers

Важная ошибка сессии: круги `MON`, `MON 1`, `MON 2`, `MON 3`, `MON 4` на карте
НЕ являются мусором и НЕ должны заменяться на реальные creature sprites.
Это оригинальные `MONS32.ICN` random-monster markers из reference-кадра.

Ошибочная ветка была такой:

- `MONS32#66..70` были временно заменены на `MINIMON` adventure sprites;
- это дало визуально неверный кадр относительно опоры;
- ветка откатана: `Source/Tools/monster_render.py` и
  `Source/Tools/test_monster_render.py` удалены, изменения normalization из
  `viewport_pack.py`, `object_spi_pack.py`, `object_atlas.py` сняты.

Текущее правильное состояние:

- `DYNAMIC_VISUAL_ICNS` должен продолжать включать `MONS32.ICN`;
- `MONS32#66..70` должны попадать в runtime object layer как оригинальные
  random markers;
- добавлен regression test:

```text
python -u Source\Tools\test_random_monster_markers.py
```

Он проверяет, что на `SKIRMISH.map.bin` в runtime остаются 13 original
`MONS32` random markers и что они не были снова converted to `MINIMON`.

После отката проверено:

```text
.\build.cmd
python -u Source\Tools\test_random_monster_markers.py
python -u Source\Tools\test_sprite_scroll_sync.py
python -u Source\Tools\test_background_scroll_monotonic.py
python -u Source\Tools\test_path_overlay.py
python -u Source\Tools\test_viewport_scroll.py
python -u Source\Tools\test_adventure_cursor.py
python -u Source\Tools\test_cursor_input.py
python -u Source\Tools\verify_ft812_pipeline.py
python -u Source\Tools\eve_ft812_oracle.py --transition --from-x 480 --from-y 0 --to-x 480 --to-y 0 --out-dir Diagnostics\eve_ft812_random_markers_restored --capture-limit 20
```

`test_hero_command.py` напечатал OK, но процесс был завершён по timeout
обёртки на 60 секунд; при следующем заходе запускать его отдельно с большим
timeout.

Состояние build после отката:

```text
object sprites=24 + route=145 + overlays=10 + ui strips=46 + buttons=8 + radar=1
object atlas=324740 bytes, pages=20
RAM_G object atlas sha256=D72A32B85CFBDDC0074CF071D7B38E65165CBB3E1701010BDDEB8933BF70324B
DL sha256=179BCF8384E884F2FAFABDE3F65019A16B0826833BDC35D0884AF7092AE7B224
```

Следующему агенту: не гадать по отдельному объекту. Если пользователь даёт
скрин как опору, сначала сравнить полный кадр/слои с reference, затем править
только подтверждённое расхождение.

## Архитектурное правило 2026-06-14: не собирать игру по кирпичам

Пользователь зафиксировал главный принцип дальнейшей разработки:

```text
Карта - это всего лишь песчинка игры. Начинать надо не с карты.
Нельзя собирать HMM2 по кирпичам; нужно переносить дом целиком.
```

Практический смысл:

- цель проекта — не отдельный renderer карты, а перенос оригинальной HMM2 как
  целостной game-state системы;
- карта/тайлы/объектный слой являются следствием состояния игры, а не
  самостоятельным ядром;
- основой должны быть оригинальные правила: сценарий, мир, объекты, герои,
  события, ходы, UI-режимы, pathfinding, passability, анимации и только потом
  вывод;
- FT812/TS-Config слой должен быть backend для отображения/ввода/загрузки, а
  не место, где игра заново изобретается локальными костылями;
- при любом новом шаге сначала брать OpenHMM2/fheroes2/original reference как
  источник поведения и переносить подсистему целиком, с её контрактами;
- визуальные тесты должны сравнивать полный результат с опорой, а не
  подтверждать промежуточные догадки;
- если изменение выглядит как “добавим ещё один частный случай для карты”, его
  нужно остановить и вернуться к оригинальной подсистеме, из которой этот
  случай должен следовать.

Следующий крупный этап должен начинаться с инвентаризации оригинальных
подсистем HMM2 и выбора переносимого вертикального среза game-state ->
renderer -> input, а не с очередной доработки отдельного тайла/объекта карты.

## 2026-06-14: cycle-accurate физический симулятор тракта Z80→DMA→SPI→FT812

Проблема: рассинхрон/stutter слоёв при скролле виден на железе, но ни один
автотест его не ловил. Причина — все эмуляторы ВНЕ времени: `tsconf_ft812_sim.py`
делает DMA мгновенным, `shadow_ft812.py` взводит INT_SWAP мгновенно и берёт
когерентный снимок DL → ни tearing, ни просадка частоты невозможны в принципе.

Добавлен **`Source/Tools/phys_ft812_sim.py`** — `PhysFT812Machine(HMM2FullZ80Emulator)`
с осью времени (секунды; clock += tstates/f_z80):

- DMA с физической длительностью: `DMASTATUS` держит busy, пока спин-цикл Z80 не
  доедет до момента завершения; байты пишутся в лог записей с интерполированными
  метками времени. Калибровка ~2.14 МБ/с (учебник: 150 КБ ≈ 70 мс @ 14 МГц).
- Тайминги читаются из регистров, которые прошивка САМА программирует в
  FT_RESOLUTION: PCLK=64МГц, HCYCLE=1344, VCYCLE=806 → **fps=59.081 Гц** (сверено).
- Дисплейный движок: `DLSWAP_FRAME` латчится на vblank; INT_SWAP/DLSWAP/FRAMES из
  часов → главный цикл пейсится к 59 Гц естественно.
- Реконструкция кадра по полосам (`reconstruct_frames`) на forward-replay лога:
  **RAM_DL двойно буферизирован** (латч на vblank → когерентен), **RAM_G читается
  лучом ВЖИВУЮ** (перезапись тайлов/спрайтов во время сканаута = tearing).
  `render_dl_png` обобщён до `render_dl_band(...,y0,y1)` (клип по Y).

Драйвер `Source/Tools/phys_ft812_capture.py` (MainLoop+скролл+PNG/отчёт) и
контракт `Source/Tools/test_phys_ft812_sim_contract.py` (тайминг 59Гц; статический
пейсинг 1.0 кадр/итер; **паритет** физ-реконструкции с абстрактным растром на
статике; физ-эффект под скроллом).

**Ключевая находка (физический root-cause stutter):** `CompositeTiles_UploadForScroll`
начинается с безусловного `JP CompositeTiles_UploadFull` (код проверки направления
ниже — мёртвый). На КАЖДОМ пересечении origin (каждые 32px = ~6.4 кадра при 5px/кадр)
заливается ВЕСЬ композит-окно 15×15×1024 = **225 КБ**. По модели это **~9 кадров
(~152 мс) фриз** на каждое пересечение → игра дёргается при скролле. Абстрактный sim
этого не видит (мгновенный DMA). Фикс рендера — отдельная задача (не делался).

Исправлено в этой сессии в `hmm2_ft812_snapshot.py`: `HMM2_VIDEO_TIMING` был
нефизичен (hcycle=800/vcycle=525/pclk=2) — заменён на реальные 1344/806/8.

Проверено:
```text
python -u Source\Tools\test_phys_ft812_sim_contract.py   # все 4 проверки OK
python -u Source\Tools\test_sprite_scroll_sync.py         # не сломан
python -u Source\Tools\test_viewport_scroll.py            # не сломан
python -u Source\Tools\test_background_scroll_monotonic.py
python -u Source\Tools\test_path_overlay.py
python -u Source\Tools\hmm2_ft812_snapshot.py             # рендер не сломан
```

## 2026-06-14: РЕАЛЬНЫЙ баг карты — stride объектной таблицы (спрайты «в воде»)

Симптом (с железа): спрайты карты оказываются «в воде / где попало», хуже к
правому-нижнему краю; при X-скролле всё ок.

Диагностика НЕ вслепую — по дампу памяти железа (`\\tsclient\D\...\unreal_x64\111`,
64КБ Z80). Из дампа по `hmm2.sym` прочитано реальное состояние: ViewportOriginX=0,
**ViewportOriginY=4** (карта скроллена ВНИЗ). Рендер этого состояния в симуляторе
ВОСПРОИЗВЁЛ баг (сундуки в открытой воде) — раньше я смотрел на originY=0, где
баг не виден.

Root-cause: `Render_ObjectViewTableEntry` (render.asm) индексировал
`ObjectViewDL_Table` с ЗАШИТЫМ ×17 (четыре `ADD HL,HL` = ×16, `+originY`), а
`viewport_pack.py` упаковывает пакеты `for oy: for ox` со stride `max_x+1 =
width-VIEW_W+1 = 36-14+1 = 23`. **17 ≠ 23.** При originY=0 совпадает (потому
X-скролл и старт всегда были зелёные), при originY>0 грузился ЧУЖОЙ пакет:
origin (0,4) → запись 4·17=68 = объекты origin (22,2) поверх правильного
террейна (0,4) → спрайты в воде. Чем больше originY, тем сильнее уезжает.

Почему не ловилось: `test_sprite_scroll_sync` проверял только X-скролл
(originY=0) и относительный dx слоёв, плюс маскировал края.

Фикс:
- `viewport_pack.py`: эмитит `OBJECT_VIEW_STRIDE EQU {max_x+1}` в
  `generated_runtime_map.inc`;
- `render.asm` `Render_ObjectViewTableEntry`: вместо зашитого ×17 —
  `originY * OBJECT_VIEW_STRIDE + originX` (generic-умножение через `ADD HL,DE`
  в цикле), не зависит от размера карты.
- (NB: `Render_ViewportTableEntry` имеет тот же латентный ×17, но НЕ активен при
  RUNTIME_TILEMAP_RENDER=1 — не трогал, пометить на будущее.)

Проверено (до/после на состоянии из дампа origin 0,4): сундуки-в-воде ушли,
объекты легли на сушу; угол (origin 22,22) рендерится корректно. Добавлен
регресс `Source\Tools\test_object_view_table_stride.py` (сверяет индекс рантайма
со stride для originY>0 и угла — поймал бы баг). Существующие контракты зелёные.

Замечен побочный bug инструмента (не критичный): `hmm2_ft812_snapshot.py`
клампит origin к `min(x//32,16)` / `min(y//32,21)` (устаревшие пределы) — при
прямом `--viewport-x/y` за этими пределами даёт несогласованный pixel/origin и
чёрную полосу. Для корректного угла надо `Viewport_UpdateOriginFromPixel`.

## 2026-06-15: доводка карты по OpenHMM2 — мини-карта, fog of war примитивами

Пользователь: довести карту до полноты по OpenHMM2, при упоре в железо — писать.
Правило железа подтверждено в процессе: **RGB565 не используем** (2 байта/пиксель —
дорого по RAM_G/SPI).

Мини-карта (`viewport_pack.py`):
- `RGB565 → PALETTED4444` (1 байт/пиксель + палитра, −20 КБ RAM_G; в билде 0
  вхождений RGB565). `build_radar_paletted4444` + `append_radar_paletted_sprite` +
  `UI_RADAR_PALETTE_RAMG`.
- Динамика по fheroes2 (`Radar::RedrawCursor`/`RedrawObjects`): **белая рамка
  вьюпорта** (LINE_STRIP из ViewportOriginX/Y) + **красная точка героя** (RECTS из
  HeroTileX/Y). Firmware `Render_MinimapRectCmd` + `Render_MinimapHeroDotCmd`,
  EQU `UI_RADAR_X/Y`, `MINIMAP_TILE_PX`, `MINIMAP_RECT_LOGICAL`.

Fog of war — **примитивами FT812, без спрайтов** (это явный выбор; CLOP32 НЕ
извлекаем):
- explored-битмап 36×36 (162 байта), раскрытие радиусом 5 вокруг героя каждый
  кадр (накопительно при движении): `FogExplored`, `Fog_Reveal/BitPtr/TileExplored`.
- рендер: на каждом неразведанном видимом тайле — чёрный **anti-aliased POINT-круг**
  (`POINT_SIZE` + `BEGIN POINTS`, `BLEND SRC_ALPHA`). Перекрытие даёт сплошную
  внутренность, AA-края — мягкую облачную границу (вместо жёстких прямоугольников
  первой грубой версии, которую пользователь отверг). `Render_FogCmd` выровнен по
  скроллу через `RuntimeDL_ObjectTranslate`, покрывает 15×15 тайлов (фикс правой
  margin-полоски). 1 вершина/тайл — дёшево, бюджет кадра проходит ассерт.

Sim `render_dl_png`/`render_dl_into`: добавлена отрисовка `LINE_STRIP/LINES` и
кругов для `POINTS` (с мягким краем) — чтобы видеть рамку/туман в симуляторе.

Урок сессии: грубую заглушку (жёсткие RECTS-прямоугольники тумана) НЕ вкручивать
в живой билд — сначала показать кадром. Пользователь резко против заглушек.

Проверено рендером (origin 0,4 из дампа железа) и контрактами
(`test_sprite_scroll_sync`, `test_object_view_table_stride`, `test_viewport_scroll`).
Сохранено как `releases/v007-2026-06-15-minimap-paletted-fog-points`.

## 2026-06-15: анимация воды через palette-cycle (родной метод HMM2)

Принцип пользователя подтверждён: «у FT812 есть преимущества — иногда нужно их
использовать». Вода анимируется циклом палитры — как в оригинальной DOS-версии
HMM2, и это чистый выигрыш FT812 (перезаливка ~14 байт палитры/банк/кадр, ноль
DL-стоимости, мерцает вся вода без кадров-спрайтов).

Диапазон анимированной воды определён ТРЕЙСОМ RAM_G (а не догадкой): читались
реальные индексы пикселей водных тайлов в composite-кэше текущего банка —
доминируют индексы **231-237** (water-only, не пересекаются с сушей). Подтверждено
рендер-тестом: вращение 231-237 меняет водный бокс ~97%, сухопутный 0%.

Важный урок про банки: composite-фон ДВОЙНО банкируется (`CompositeDrawBank`,
бэнк1 палитры по `#03C400`). Первый тест крутил банк0 (#0001CE) и «не работал» —
отображается банк1. Палитру водного диапазона надо писать в ОБА банка.

Реализация:
- `viewport_pack.py` (`write_runtime_map_inc`, +param `palette`): эмитит
  `WATER_CYCLE_INDEX=231`, `WATER_CYCLE_COUNT=7`, `WATER_CYCLE_BANK0_RAMG`/`BANK1_RAMG`,
  таблицу `WaterCycleOriginal` (7 исходных ARGB4 из KB.PAL).
- `render.asm` `Render_WaterCycle` (вызов после `Runtime_UploadStaticIfDirty`):
  каждый кадр вращает 7 записей по `WaterCycleCounter/8` и пишет штатным
  `FT.WriteMem` в палитру обоих банков RAM_G.

Пойман баг ручной SPI-записи: `FT_ON` ЗАТИРАЕТ `A` (штатный `WriteMem` делает
`PUSH AF; FT_ON; POP AF`), поэтому самописный writer слал мусорный high-байт
адреса → запись уходила в данные тайлов (#0701CE). `verify_ft812_pipeline` это
поймал. Решение: использовать штатный `FT.WriteMem`. (Урок: для записи в RAM_G —
`FT.WriteMem`, не ручной OUT после `FT_ON`.)

Проверено: build verify OK (первый кадр ротация=0 → RAM_G == статика), вода
анимируется (97% бокс / 0% суша за 8 кадров), контракты зелёные.
Сохранено как `releases/v008-2026-06-15-water-palette-cycle`.

---

## Анимация объектов — аппаратно-архитектурное ограничение (находка 2026-06-15)

Пользователь просил «писать, если возникнут ограничения аппаратуры». Возникло.

Попытка сделать анимацию объектов (флаги/мельницы/костры) тем же дешёвым приёмом,
что и воду (патч одной величины по глоб. счётчику), **провалилась по фактам**:

**Кадры анимир. объектов HMM2 РАЗНОГО размера/смещения.** Проверка всех 148
анимир. частей из `object_animation.csv` (читались реальные ICN-хедеры кадров
`base+1..base+F`): **111 из 148 — НЕОДНОРОДНЫ**. Примеры:
- `OBJNDIRT base=169` (F=3): 28×32, 30×32, 28×32;
- `OBJNDIRT base=173`: 17×30, 19×21, 17×32;
- `OBJNCRCK base=190` (F=10): от 3×2 до 4×4 до 1×1;
- у `ox/oy` (якорь спрайта) кадры тоже расходятся.

Следствие: у КАЖДОГО кадра свои **BITMAP_SOURCE (addr), BITMAP_LAYOUT (stride,h),
BITMAP_SIZE (w,h) и VERTEX2F (позиция, т.к. ox/oy меняются)**. Это НЕ патч одной
команды (как вода — 1 запись в палитру), а **полная пере-сборка квартета команд
спрайта на каждый кадр**. Группировка анимир. объектов с другими по BITMAP_SOURCE
тоже невозможна (layout/size индивидуальны).

Почему отвергнут stride-подход (frame0 + (idx%count)*stride): он держится ТОЛЬКО
на одинаковом размере кадров (тогда упаковка подряд даёт фикс. шаг). Размеры
разные → шаг не фикс., адрес кадра k ≠ frame0+k*stride → мусорный BITMAP_SOURCE
(может указать куда угодно в RAM_G). Плюс даже верный addr без правки layout/size/
vertex даёт битый спрайт.

Почему отвергнуто пер-origin хранение офсетов патчей: объект виден из многих
origin → дублирование. Замер: **3482 патча × 8 байт ≈ 28 КБ**, не влезает в Core
(ассерт `CoreEnd <= #A000`).

### Корректный механизм (для следующей сессии)
Анимир. объекты — это «динамика», их надо вести как актёра/героя (fheroes2
перерисовывает кадр целиком), а НЕ через статический `object_view_dl`:
1. Глобальная таблица параметров ВСЕХ анимир. кадров: на `(icn,idx)` →
   `addr(3),w(1),h(1),stride(2),ox(s8),oy(s8)` ≈ 9 байт. ~150 кадров ≈ 1.35 КБ (Core OK).
2. Пер-origin список ИНСТАНСОВ динам. объектов (а не патчей): `tile_x,tile_y,
   icn/anim_id, count`. Инстансов мало (динамика < всех объектов) — но всё равно
   следить за размером (возможно, паковать в страницы, как объектные DL).
3. Firmware каждый кадр: для инстанса берёт кадр `base+1+(animidx%count)`, читает
   его параметры из (1), считает vertex с учётом ox/oy кадра, эмитит квартет
   команд в отдельный «динам.-объектный» DL-буфер и заливает его (как actor DL).
4. Глоб. индекс анимации — как `Game::getAdventureMapAnimationIndex()` (можно от
   `WaterCycleCounter`/N).

### Что сделано безопасно (билд ЗЕЛЁНЫЙ, baseline сохранён)
Step A (re-split `part_is_dynamic` → анимир. кадры в динам. группу, объектов
24→54, без двойной отрисовки) — оставлен. Все пробы Step B (упаковка кадров,
frame0-lookup, stride-таблица `AnimFrame0Table`) **откатаны** как стоящие на
ложном допущении однородности кадров. atlas снова 322478 байт, verify OK,
`test_object_view_table_stride` и `test_sprite_scroll_sync` зелёные.

---

## Полное покрытие объектов + z-слои (пункт 13, 2026-06-15)

Карта рисуется в меньшем окне (UI-рамка ADVBORD), поэтому видимых тайлов в кадре
немного — это дало бюджет «вынуть top-слой из фона» (идея пользователя).

### Z-слои — top-слой поверх актёра (как fheroes2)
До: ВСЯ статика (низ И верх) запекалась в composite-фон → top-слой (level2: кроны
деревьев, верхушки гор, флаги) оказывался ПОД героем/актёром. fheroes2
(interface_gamearea.cpp) рисует низ-слои → актёров → `getTopObjectParts` ПОВЕРХ.

Реализация (FT812, без нового ROM-потока — переиспользуем заливку/страницы):
- На origin собирается blob = `[низ-оверлей DL][top-оверлей DL]` (оба без хвостового
  DISPLAY). ОДНА DMA-заливка в `RUNTIME_DL_OBJECT_RAMG`, ДВА `CMD_APPEND`:
  `Render_RuntimeObjectsCmd` (низ, до актёра) и новый `Render_RuntimeTopObjectsCmd`
  (верх, после `Render_ActorCmd`, перед `Render_FogCmd`).
- Запись `ObjectViewDL_Table` 5→7 байт: `DEFB page, DEFW off, DEFW bottom_size,
  DEFW top_size` (`OBJECT_VIEW_ENTRY_SIZE EQU 7`). `Render_ObjectViewTableEntry`
  индексирует HL = table + index*7 (был ×5).
- `Render_RuntimeTopObjectsCmd`: читает bottom_size(DE)/top_size(BC); top==0 → RET;
  иначе переустанавливает VERTEX_TRANSLATE (копия `RuntimeDL_ObjectTranslate` — актёр
  мог сбить), адрес = `RUNTIME_DL_OBJECT_RAMG + bottom_size` (ADD HL,DE; LD A,imm;
  ADC A,0 — перенос; флаг переноса от ADD доживает, LD A,imm флаги не трогает), append.
- Заливка размером bottom+top: в `Runtime_UploadObjectStatic`/`Render_RuntimeObjects`
  после чтения bottom_size прибавляется top_size (ADD A,(HL)/ADC A,(HL)).
- `viewport_pack.py`: `ObjectTransferPlan` теперь 3-корзинный (static_bottom /
  dynamic_bottom / top_all через `.top_at`); top НЕ запекается; `top_object_view_dl`
  и `original_top_objects_for_view` для top-оверлея; `build_object_atlas` пакует
  спрайты и низа, и верха.

### Порядок низ-слоёв = fheroes2
`BOTTOM_LAYER_RANK={3:0,1:1,2:2,0:3}` → TERRAIN(3)→BACKGROUND(1)→SHADOW(2)→OBJECT(0)
(было `reverse=True` = 3,2,1,0 — shadow/background перепутаны). `build_composite_tiles`
печёт глобальными проходами по рангу (сорт (rank,my,mx)), а не тайл-за-тайлом —
корректно для объектов через границу тайла.

### Полнота покрытия — объекты PoL
Проверка дропов: 64 части (icn_type 62/63 = `X_LOC2/X_LOC3.ICN`, объекты дополнения
The Price of Loyalty) молча терялись — их НЕТ в базовом HEROES2.AGG. Добавлены типы
61/62/63 (X_LOC1/2/3) в `ICN_BY_OBJECT_TYPE`; новый `read_agg_index_with_expansion`
сливает `HEROES2X.AGG` в базовый (сдвиг офсетов записей в конкат-буфер, базовые в
приоритете). Применён в `viewport_pack` И `object_spi_pack`. Покрытие 935→**999**
частей, дроп по неизвестным типам **64→0**.

### Бюджет / проверки
Атлас 322478→446546 байт (28/36 ROM-страниц по 16КБ; RAM_G объектов кончается
`#0E6051`, влезает в 1МБ). `RUNTIME_CMD_FRAME_MAX` += стоимость top-append
(RuntimeDL_ObjectTranslate_SIZE+12) в обеих ветках. `check_ramg_usage.py`
обновлён под 7-байтовую запись + top в frame_dl. Тесты зелёные: build/verify,
`test_object_view_table_stride` (entry_size читается из inc), `test_sprite_scroll_sync`,
`test_viewport_scroll`. Снапшот когерентный.

### Отдельно: пред-существующий пейсинг
`test_phys_ft812_sim_contract` [2] статический пейсинг = 2.0 кадр/итер (норма ~1.0)
— НЕ от z-слоёв (A/B: с отключённым `Render_RuntimeTopObjectsCmd` ровно те же 2.0).
Это от рефактора 1024×768 — рендер кадра не укладывается в один vblank (≈16.93мс).
Реальный риск дёрганья на железе, требует отдельной оптимизации DL/кадра.

### Адверсариальный ревью изменения (4 измерения × независимая перепроверка)
Воркфлоу-ревью (Z80-смещения/перенос, пайплайн-данные, z-порядок vs fheroes2,
verify/бюджет): **0 багов** — вся Z80-логика (×7 индекс, перенос адреса top-append
ADD HL,DE/ADC A,0, чтение 7-байтовой записи, заливка bottom+top), blob-сборка,
эмиссия таблицы и бюджет CMD верны.

Поправлено по итогам ревью:
- **OBJNCRCK#226 → демоция в TERRAIN.** fheroes2 Tile::Init кладёт трещину
  OBJNCRCK (тип 57) с top-index 226 в низ-террейн, НЕ в top. Порт безусловно метил
  любой top_icn как top → трещина ушла бы поверх героя. Добавлена демоция в `add()`.
  (На SKIRMISH таких тайлов нет — фикс защитный для других карт.)
- **check_ramg_usage.frame_dl был занижен на ~2.6 КБ** — пропускал hero-path(1592),
  fog(932), actor, minimap-rect(60), ведущий CLEAR(4). Это ЕДИНСТВЕННЫЙ страж
  RAM_DL≤8192 (ASM RUNTIME_CMD_FRAME_MAX стережёт ДРУГОЙ буфер — RAM_CMD 4096, где
  CMD_APPEND стоит лишь 12 байт). Теперь честно: **RAM_DL max=7748/8192 at (14,8)**,
  запас всего ~444 байта — плотный origin (полный hero-path+туман+больший blob) мог
  бы переполнить RAM_DL незаметно. Фиктивные дефолты (.get,76) заменены прямым
  чтением (отсутствие символа → явная ошибка).
- Косметика: переотступленный bake-цикл (16→8).

Отложено (узкие low-risk, общий корень — оверлей `_build_objects_dl` пересортирует
по адресу спрайта ради батчинга, теряя painter-порядок внутри тайла/вью; точная
верность требует отказа от батчинга / отдельных под-DL):
- FLAG32 не пост-рендерится после main-объекта в пределах тайла (видно лишь при
  перекрытии флаг/анимир-постройка на одном тайле);
- высокие top-объекты (isTallTopLayerObject) не откладываются в самый конец
  (видно лишь на стыке двух вертикально-смежных высоких top-объектов);
- внутри слоя порядок main→addons (в fheroes2 addons→main).

### Анимация объектов — эмпирический лимит RAM_G (2026-06-15, после z-слоёв)
Попытка резидентной анимации (упаковать все кадры base+1..base+F анимир. объектов
в object atlas) дала **жёсткий RAM_G overflow** — билд поймал пересечение:
`object atlas #079000-#0FD079 (540794 байт) ∩ runtime left DL #0F0000`.

Раскладка RAM_G (1 МБ): composite bank0+bank1 (2×246784 ≈ 494 КБ) внизу → object
atlas с #079000 → runtime DL staging (LEFT/RIGHT/OBJECT) у #0F0000 сверху. Между
концом атласа (#0E6051, после z-слоёв/покрытия = 446546 байт) и DL-staging (#0F0000)
свободно лишь **~40 КБ**. Кадры 30 анимир. объектов карты (186 кадров) = **~110 КБ**.
Перебор ~70 КБ → резидентно НЕ влезает.

**Вывод:** все кадры анимации держать резидентно в RAM_G нельзя (composite-кэш +
объектный атлас z-слоёв съедают почти весь 1 МБ). Правильный путь для FT812/TS-Conf —
**стриминг кадров из ROM**: кадры лежат в ROM (постранично), firmware DMA-ит ТОЛЬКО
текущий кадр каждого ВИДИМОГО анимир. экземпляра (~24 в 14×14 вью, ~14 КБ слотов) в
RAM_G по тику анимации (не каждый кадр — раз в ~6), DL указывает на слот. Это влезает
в ~40 КБ и решает оба: non-uniform кадры (полный квартет на слот) и RAM_G-лимит.
Но это отдельный крупный firmware-механизм (пер-экземпляр слоты + DMA-стриминг по
тику + пер-origin метаданные инстансов (постранично) + пер-кадровая пере-сборка DL).
Резидентный приём (как вода/палитра) для объектов невозможен — подтверждено билдом.

---

## Баг «герой проходит несколько шагов и застревает» — коллизия ROM-страниц (2026-06-15)

Симптом: герой делает несколько ходов, потом стоит, дальше не идёт.

Корень (найден трассировкой `trace_z80_pathfinding.py` + диффом Z80-visited vs
Python-эталон): A*-поиск умирал, посетив лишь 17 тайлов из 160 достижимых.
Причина — **path-FLAGS были мусором**: file flag (15,9)=`00`, а Z80 читал `01`
(=`PATH_FLAG_WATER`) → `Path_TryNeighbor` отвергал тайл как воду → фронт умирал →
`PathFound=0`, герой не двигался к дальним целям (близкие ещё работали — отсюда
«несколько шагов»).

Почему флаги мусор: **коллизия страниц в SPG**. `MAP0_PATH_PAGE=0x11` (cost/flags
маршрута) и `PathWorkPage=0x13` были В `OBJECT_VIEW_PAGE_LIST`. Пока object-view
payload был мал (~12 чанков), он до них не дорастал. Z-слои (пункт 13) раздули
payload до `[низ][верх]` (~15 чанков) → `SKIRMISH_OBJECTVIEW_p13.bin` лёг на page
#11 поверх `SKIRMISH.path.bin` → метаданные пути затёрты. **Регресс z-слоёв**, но
тихий: билд/verify зелёные, видно только в геймплее.

Фикс (`viewport_pack.py`): убрать зарезервированные страницы карты/пути из
`OBJECT_VIEW_PAGE_LIST` (0x11, 0x13; заодно 0xC4=COMPOSITE_UPLOAD — латентная того
же класса). Список теперь явно их пропускает с комментом.

Защита от рецидива (`check_ramg_usage.py`): `parse_spg_pages` делал `pages[page]=buf`
(last-wins, коллизия скрыта). Теперь — детектор перекрытий: две Block-записи с
пересекающимися диапазонами на одной странице → явная ошибка с именами обоих файлов.

Проверено: flags mismatch 1204→**0/1296**, z80_visited 17→**160** (=Python, gap=0),
цель (23,7) PathFound=1 len=10; замурованные цели Z80 корректно отвергает (=эталон).
Урок: страничные page-списки ассетов ОБЯЗАНЫ исключать страницы карты/пути/паллет;
рост payload может тихо налезть — нужен SPG-детектор коллизий (добавлен).

---

## Баг «замок обрезан по Z» — дыры в фоне от z-слоёв (2026-06-15)

Симптом (скрин пользователя, первый кадр): замок/постройка обрезаны по горизонтали,
верхняя часть отсутствует, сквозь неё видно террейн.

Корень: многотайловые объекты HMM2 (`OBJNTOWN` замок, `MTNDIRT`/`MTNGRAS` горы)
хранят части ВПЕРЕМЕШКУ потайлово — одни тайлы объекта `top=True` (level2), другие
`top=False` (level1) (одинаковый uid). Z-слои (пункт 13) убрали top-части из
ЗАПЕКАНИЯ (`build_composite_tiles`) → в фоне появились ДЫРЫ на месте top-тайлов
объекта. У `OBJNTOWN` это 12 из ~28 тайлов → вся верхняя половина замка не
запекалась. Тихий регресс — рендер не вглядывали.

Фикс (`viewport_pack.py` `build_object_transfer_plan`): запекать ВСЮ статику — и
низ (`static_bottom`), и top-статику (`top_static`): `static_by_tile = static_bottom
+ top_static`. Фон становится ЦЕЛЫМ. top-части ДОПОЛНИТЕЛЬНО идут в top-оверлей
(после актёра, z над героем) — `top_by_tile` без изменений. `validate` больше не
запрещает top в static (намеренно). Фикс БЕСПЛАТЕН по рантайму: оверлей и так
рисовал все top-части (top_at не менялся), вернули их лишь в разовое запекание.
top-ДИНАМИКА (флаги) НЕ запекается — её рисует только оверлей (это не дыра).

Проверено: каждый top-тайл `OBJNTOWN`(uid 3,4) теперь и в static, и в top (структура
целиком запечена, дыр 0); пиксель-дифф первого кадра ДО/ПОСЛЕ заполнил дыру в
постройке (242px); регресс зелёный (stride/scroll/pathfinding).

УРОК (важно): билд+verify+юнит-тесты НЕ ловят визуальные z/render-баги. После ЛЮБОЙ
правки рендера ОБЯЗАТЕЛЬНО смотреть отрендеренный кадр (снапшот) вблизи, а не только
счётчики DL. Два регресса z-слоёв (page-коллизия pathfinding + срез замка) прошли
именно из-за отсутствия визуальной проверки.

---

## Баг «камень в воде портится по Z» — СИСТЕМНЫЙ фикс (2026-06-15)

Симптом: камень/риф в воде иногда визуально портится.

Корень: спрайты водных объектов (OBJNWATR/OBJNWAT2) используют палитровые индексы
231-237 (синяя кромка у воды) — ровно water-cycle диапазон. Из-за двойной отрисовки
z-слоёв (объект и запечён в composite, и нарисован статичным оверлеем) запечённая
версия циклит палитру ВМЕСТЕ с водой, а оверлейная статична → кромка рассинхронится
→ «портится». (Плюс origin-зависимый оверлей = «иногда».)

СИСТЕМНЫЙ фикс (НЕ хардкод ICN — чтобы работало на любой карте):
`cycled_terrain_indices(ground_tiles)` находит терэйн-индексы, чьи РЕАЛЬНЫЕ пиксели
попадают в цикл-диапазон [WATER_CYCLE_INDEX..+COUNT). Это data-driven: на любой
карте/тайлсете автоматически. `build_object_transfer_plan` получает этот set; если
тайл циклится (`tile["terrain"] in cycled`), ВСЕ его объекты идут ТОЛЬКО в
запекание (static), без dynamic/top-оверлея. Причина-принцип: (1) герой по воде не
ходит → окклюзия оверлеем не нужна; (2) запечённый объект мерцает В СИНХРОНЕ с
водой (как оригинал HMM2); (3) статичный оверлей поверх циклящей воды запрещён.
`ObjectTransferPlan.is_cycled_tile()`; `validate` пропускает циклящиеся тайлы.

Проверено (данные): 38 циклящихся терэйн-индексов, 614 водных тайлов, ВСЕ 75 водных
объектов в static, 0 в оверлее. Атлас даже уменьшился (водные ушли из оверлея).
Билд/verify зелёные. (Визуал: рендер 2 фаз цикла — камень мерцает синхронно.)

ПРИНЦИП на будущее (важно для других карт): любой объект на палитрово-циклящемся
тайле — только запекать. Правило по ТЕРЭЙНУ (data-driven), не по списку ICN.

## 2026-06-15 (v011): стартовая позиция героя = как в ОРИГИНАЛЕ (гейт замка)

fheroes2 при `startWithHeroInFirstCastle` рекрутирует героя в ПЕРВОМ замке и ставит на
его **гейт** (`Castle::GetCenter` = action-тайл входа). У нас старт перенесён с тайла
ПЕРЕД гейтом (24,14) ровно НА гейт **(24,13)**.

Проблема: MAIN-часть гейта — town-basement OBJNTWBA (не-action) → проходимость тайла
= `00`, герой был бы заперт на гейте. СИСТЕМНЫЙ фикс (не хардкод тайла):
`map_tools.py` `CASTLE_ENTRANCE_OBJECTS = {35|128, 49|128}` (OBJ_CASTLE/OBJ_RANDOM_CASTLE
как action-объекты по `map_object`); пост-проход в `build_passability` даёт таким тайлам
`action_object_passability` → гейт проходим, герой выходит вниз. Любая карта, не только
SKIRMISH. Структура замка по-прежнему `00` целиком.

`game_state.asm`: `HERO_START_TILE_Y` 14 → 13.

Проверено: гейт (24,13) pass=F8, структура (24,11-12)=00, достижимо из гейта 151 тайл,
тайлов замка достижимо 0. ВИЗУАЛЬНО (рендер hero_start_gate_24_13.png): рыцарь на гейте,
замок целый, z верный (герой перед аркой). Опорная: releases/v011-2026-06-15-hero-start-original-gate.

ПРИНЦИП: action-вход замка/города (map_object 163/177) всегда проходим, даже если его
MAIN-часть — не-action постройка. Иначе рекрут-на-гейт запирает героя.

## 2026-06-15 (v011): «вертикальные чёрточки» — расследование, НЕ воспроизведено

Жалоба: «иногда вертикальные чёрточки одинаковой толщины/высоты». На v011:
- Детектор изолированных вертикальных линий (столбец, сильно отличный от ОБОИХ соседей,
  run≥20px) на стартовом и скролл-кадре (15px) даёт только края вьюпорта + флагшток
  героя. Перемежающихся штрихов НЕТ.
- Автокорреляция столбцов: пик на лаге **8 px** (≈0.88) — это НЕИЗБЕЖНЫЙ паттерн nearest
  ×1.6 (5/8 → период 8 дублируемых столбцов). КОНСТАНТНЫЙ (в каждом кадре одинаков), не
  «иногда» → это не тот глюк.
- Фон/объекты paletted (PALETTED4444) → билинейная фильтрация НЕЛЬЗЯ (испортит индексы
  цветов). nearest обязателен; лаг-8 паттерн структурно неустраним для paletted.

Детерминированно глюк НЕ воспроизведён. Нужен момент появления от пользователя.
Инструмент: `Diagnostics/vdash_scan.py` (детектор + можно добавить автокорреляцию).

## 2026-06-15 (task #11): анимация adventure-объектов (мельницы/колёса/лава)

Реализована покадровая анимация объектов карты (как в fheroes2: BlitBase, затем
BlitFrame поверх). Вода — отдельно (palette-cycle, task #12), здесь НЕ трогается.

Данные: `extract_object_animation.py` → object_animation.csv (icn,base,N из
map_object_info.cpp). Формула fheroes2: `frame = base + (counter % N) + 1`, кадры
подряд base+1..base+N; единый счётчик, шаг MAPS_DELAY=250мс. FLAG32 НЕ анимируются.

Пайплайн (всё системно, любая карта):
- `viewport_pack.py`: `collect_map_anim_objects` (анимир. части из transfer_plan
  dynamic/top, водные ICN исключены — они на cycled-тайлах → запечены/palette-cycle);
  `pack_anim_frames` упаковывает кадры-дельты в object-атлас как **PALETTED4444**
  (1Б/px — ARGB4 61786Б НЕ влез бы в щель 51634; paletted 30893Б влезает); палитра —
  прозрачная объектная #79000. Кадры дедуп по (icn,frame). mono-кадры (тень) пропуск.
  `write_map_anim_inc` → generated_map_anim.inc: per-часть DEFB map_x,map_y,N + N×
  [SOURCE(4) LAYOUT(4) SIZE(4) ox oy] — готовые FT812-dword'ы (c_* хелперы → кодировка
  совпадает с оверлеем). `decode_icn_paletted` в object_atlas.py (рефактор decode_icn_planes).
- `render.asm` `Render_MapAnimCmd` (после top-объектов, ДО fog — объекты непроходимы,
  туман скрывает): счётчик фазы (÷15 кадров), куллинг по вьюпорту, эмит per-часть.
  Вставлен между Render_RuntimeTopObjectsCmd и Render_FogCmd.

ДВА КРИТИЧНЫХ ОГРАНИЧЕНИЯ:
1. **CMD-FIFO (4096) тугой** → кап `MAP_ANIM_MAX_PER_FRAME=10` объектов/кадр; сверх —
   ФРИЗ (база без кадра). Вмещает мельницу (10 частей). Вода не затронута. Пользователь
   одобрил фриз периферийных при переполнении.
2. **stale BITMAP_TRANSFORM_C=7936** (актёр-флип ставит A=-160,C=7936 для зеркала, потом
   сбрасывает A но НЕ C) → мои paletted-кадры семплились за краем source → НЕВИДИМЫ.
   ФИКС: anim-setup сбрасывает BITMAP_TRANSFORM_C=0. БЕЗ него анимация не видна (и на
   железе — transform глобальный). Урок: после top-объектов/актёра состояние bitmap-
   transform грязное, сбрасывать C явно.

RAM_G: атлас 435790→463026 (29 стр., щель ~24КБ). RAM_DL: 7952/8192 (запас 240).
Проверено ВИЗУАЛЬНО (эмулятор, туман снят, 3 фазы): водяное колесо вращается (1422px/
фаза), мельница — лопасти X→+→X (3242px/фаза). Билд/verify/тесты зелёные.
Инструменты: Diagnostics/render_anim_phase.py (origin+фаза), dump_anim_dl.py (DL),
anim_onoff.py (on/off diff). НА ЖЕЛЕЗЕ ещё не подтверждено пользователем.

## 2026-06-15 (polish анимации, поверх v012): 3 follow-up

1. **graceful-skip в pack_anim_frames** (viewport_pack.py): кадр вне диапазона ICN больше
   НЕ валит билд (был ValueError) — часть пропускается, база статична. Для чужих карт.
2. **wrap-маска счётчика фазы** (render.asm): MapAnimPhase теперь цикл 0..59
   (MAP_ANIM_PHASE_PERIOD=60, делится на 3,4,5,6,10,12,15) → mod-N непрерывен на стыке,
   без скачка фазы (раньше wrap на 256 давал скачок для N=3,6).
3. **приоритет центральным при кап-фризе** (render.asm): two-pass — проход 1 эмитит
   объекты в центре вьюпорта (tile в [3..GVTW-3]), проход 2 — периферию; общий кап →
   периферийные фризятся первыми (как просил пользователь). Множества центр/край не
   пересекаются → без двойной отрисовки, без bitmask. Дальние JR→JP (метка >127б).
   Проверено DL: на плотном origin (16,22, 14 видимых) эмитятся 10 (мельница-части),
   колёса на краю фризятся. Мельница в центре — без регрессии (3242px/фаза, как было).

RAM_DL 7952/8192 (без изменений). Билд/verify/тесты зелёные. Эмулятор: ок. На железе
после polish ещё НЕ подтверждено.

## 2026-06-15 (task #9, часть 1): навигация по мини-карте + диспетчер кликов

Клик LMB теперь диспетчеризуется по зонам (game_state.asm UI_DispatchClick, вызывается
из Hero_CommandFromFire .pressed_mouse вместо прямого Hero_CommandTargetFromMouse):
- x < UI_RADAR_X(480) → игровая зона → команда герою (как было).
- мини-карта [480..624)×[16..160) → UI_MinimapNav: центрировать вьюпорт на тайле
  (tx,ty)=(click-radar)/MINIMAP_TILE_PX(4); origin = clamp(tile - вьюпорт/2, 0, MAP-вьюпорт).
- кнопки [480..624)×[320..392) → UI_ButtonClick (пока stub).
- иначе → игнор.

Прыжок origin безопасен: CompositeTiles_UploadForScroll ВСЕГДА делает полную
перезаливку окна (JP CompositeTiles_UploadFull; инкрементальный код ниже — мёртвый).
Неразведанная цель покажет туман (корректно, как fheroes2).

UI_BUTTON_X/Y/W/H/GRID_H/COUNT теперь эмитятся в generated_objects.inc. UIClickX/Y EQU
#4241/#4243. Проверено эмулятором: 6 точек мини-карты центрируют верно (+клампинг краёв),
регрессии нет (игровой клик командует героем, кнопки/панель игнорятся). Билд зелёный.

ОСТАЛОСЬ (#9 часть 2): кнопки. 8 ADVBTNS [0,2,4,6,8,10,12,14] в сетке 4×2 от (480,320).
Большинство требуют подсистем, которых НЕТ (kingdom/turn/spell/options/2-й герой) →
«функциональными до fheroes2» их не сделать без этих подсистем. Достижимо: cosmetic
press-feedback (показывать pressed-спрайт) — стоит спросить пользователя.

## 2026-06-15 (task #9, часть 2): субсистема End Turn → Следующий день

Построена под кнопку End Turn (ADVBTNS index 4 = ряд2-кол0, fheroes2: 0 NextHero 1
HeroMovement 2 Kingdom 3 Spell 4 EndTurn 5 Adventure 6 File 7 System).

- Очки передвижения героя: HeroMovePoints (в тайлах, MAX=HERO_MOVE_TILES_MAX=16). Расход
  1/тайл в Hero_SelectStepIfArrived .need_step при продвижении; MP=0 → герой стоп
  (.stop фиксирует на текущем тайле, чистит путь). Init=16 в Game_Init.
- GameDay (1-based, #4246). Game_EndTurn: день++, MP=MAX.
- UI_ButtonClick: индекс = row*4+col (UI_DivAB деление на 36); index==4 → Game_EndTurn.
  Прочие кнопки — нет подсистемы (стоп).

Проверено эмулятором: MP=16 цель 3 тайла → прошёл 3 MP=13; MP=2 цель дальше → прошёл
ровно 2 встал MP=0; MP=0 → блок; End Turn (и через клик кнопки #4) → день++ MP=MAX;
клик NextHero(#0) день не меняет. Билд зелёный.

ОГРАНИЧЕНИЕ: видимую полоску MP в статус-области НЕ добавил — CMD-FIFO полон
(RUNTIME_CMD_FRAME_MAX=4092/4096, запас 4б; полоска ~20б). Чтобы влезла, освободить
бюджет: HERO_PATH_CMD_MAX=1592 (путь до 96 тайлов) раздут — герой теперь ходит ≤16/ход,
можно обрезать РЕНДЕР пути до MP (≈312б, экономия ~1280б) — это ещё и fheroes2-фишка
(показывать ход-этот-ход). Видимый эффект сейчас: герой встаёт, когда вышел запас;
End Turn даёт идти дальше.

## 2026-06-15 (task #9, часть 2b): полоска MP + кап рендера маршрута

- Рендер маршрута героя обрезан до досягаемого ЗА ХОД (HeroMovePoints тайлов) —
  Render_HeroPathCmd: RenderPathRemaining=HeroMovePoints, стоп при 0. fheroes2-фишка
  («ход за этот ход»). HERO_PATH_CMD_MAX: 1592→312 (56+HERO_MOVE_TILES_MAX*16). Это
  разгрузило CMD-FIFO на ~1280б (RUNTIME_CMD_FRAME_MAX 4092→2848) И RAM_DL (7952→6672).
- Полоска MP (Render_MovePointsBarCmd, после Render_AdventureUICmd): зелёная заливка
  шириной HeroMovePoints*8 px (0..128) на тёмном фоне, в статус-области (MP_BAR 490-618,
  434-450 лог.). RECTS, без шрифта. MP_BAR_CMD_BYTES=36 в бюджете.

Проверено визуально (эмулятор): MP=16 полная зелёная, MP=6 ~38%, MP=0 пустая.
Движение не сломано (путь-кап только отображение): герой (24,13)→(24,16) MP 16→13.
Билд/verify/3 теста зелёные. На железе после этого блока ещё НЕ подтверждено.

ИТОГ task #9: мини-карта-навигация + субсистема End Turn (день/MP/кнопка) + полоска MP +
кап маршрута — готовы и проверены в эмуляторе. Остальные 7 кнопок — стабы (нужны
подсистемы kingdom/spell/options/2-й герой — отдельные задачи).

## 2026-06-15 (task #9, исправление по железу): полный маршрут + затемнение «след. хода»

Железо-фидбэк: полоска MP есть (ок), но в индикации пути пропали недостижимые-за-ход
ходы (регрессия от прежнего жёсткого капа рендера до MP). Исправлено как в fheroes2:
- Render_HeroPathCmd рисует МАРШРУТ ЦЕЛИКОМ; первые HeroMovePoints тайлов — ярко
  (COLOR_A 255), дальше — затемнённо (COLOR_A 112, одно переключение на границе).
  RenderPathDimmed-флаг. Дальние JR .loop → JP (метка отодвинулась).
- Бюджет: HERO_PATH_CMD_MAX = 60 + HERO_PATH_MAX*16 (полный путь + 1 COLOR_A).
  HERO_PATH_MAX 96→88 (буферы #4300/#4360 врозь на 96, уменьшать безопасно) — чтобы
  полный путь + полоска влезли. RUNTIME_CMD_FRAME_MAX=4008/4096. RAM_DL 7828/8192.
- Полоске MP добавлен COLOR_A 255 (иначе унаследует затемнение пути). MP_BAR_CMD_BYTES 40.

Проверено: DL — 4 ярких + 16 тусклых (alpha 112) тайлов пути 20-тайлового маршрута,
переключение 1 раз. Визуально путь рисуется целиком. Билд/тесты зелёные. Затемнение
alpha=112 субтильно (зелёные стрелки на буром терэйне) — при желании усилить (ниже alpha).

## 2026-06-15 (исправление по железу #2): красный путь + убрана выдуманная полоска MP

Железо-фидбэк: (1) зелёной полоски MP в оригинале НЕТ — это была выдумка, убрал; в
статус-области оригинал показывает дату (Month/Week/Day — нужен шрифт, пока пусто).
(2) недостижимая-за-ход часть пути в оригинале КРАСНАЯ (fheroes2 ROUTERED = ROUTE с
PAL::RED), а не затемнённая.

Сделано:
- Убран Render_MovePointsBarCmd + вызов + бюджет. MP-механика (ход 16/день, End Turn)
  ОСТАЛАСЬ — индикатор теперь зелёный/красный путь, не полоска.
- Route-спрайты → PALETTED4444 (decode_icn_paletted, stride=w, LAYOUT #0778). Это
  ВДВОЕ сократило их RAM_G (object atlas 463026→381498, −82КБ!). Общая палитра route =
  OBJECT_PALETTE_RAMG #79000 (норма/зелёный). Добавлена красная палитра
  palette_argb4444_red (KB.PAL→красные оттенки, lum в R) → ROUTE_RED_PALETTE_RAMG.
- Render_RouteBeginCmd ставит PALETTE_SOURCE норма; Render_HeroPathCmd на границе хода
  (RenderPathRemaining=0) переключает PALETTE_SOURCE на красную (вместо прежнего COLOR_A
  затемнения). Маршрут целиком: первые HeroMovePoints тайлов зелёные, дальше красные.
  HERO_PATH_CMD_MAX = 64 + HERO_PATH_MAX*16. RUNTIME_CMD 3972/4096, RAM_DL 7832.

Проверено: MP=20 весь путь зелёный; MP=2 прямой путь — зелёная стрелка у героя + красный
маркер дальше. Билд/тесты зелёные. УРОК: не выдумывать UI — сверять с оригиналом/скрином.

ОТКРЫТО: «больше места под игроков в панели» (фидбэк) — список героев/замков 2кол×4ряда
(y176-304); уточнить у пользователя точный смысл. Дата в статусе — нужен шрифт.
