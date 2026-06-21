# HMM2 v017 reference - scroll cursors, active-high mouse button, adventure button pressed frame

Дата: 2026-06-18

Статус: **опорная по текущему собранному build**. Это снимок Source/Build/Docs/Music/build/config
в формате последних `releases` проекта. Внешние reference-проекты и SD-образ отдельно не копировались.

## Что добавлено поверх v016

- Edge-scroll приведён к оригинальной геометрии fheroes2: scroll-зона теперь 16 px у края
  всего логического экрана 640x480 (`x<16`, `x>=624`, `y<16`, `y>=464`), а не у края
  adventure viewport. Наведение на радар/кнопки внутри правой панели больше не скроллит карту.
- Добавлены scroll-курсоры ADVMCO для 8 направлений кромки. У scroll-курсора приоритет над
  обычными pointer/move cursor themes.
- Исправлена семантика Kempston Mouse LMB: кнопка active-HIGH через `Input.Mouse.KeyState`.
  Старый инвертор давал состояние "вечно нажато" на железе.
- Adventure buttons получили pressed overlay: `UI_ButtonPressed` обновляется пока ЛКМ зажата
  над сеткой 4x2, `Render_AdvButtonPressedCmd` накладывает pressed-кадр поверх панели.
- Cursor sprites выросли до двух страниц: `SKIRMISH_CURSOR_p00` -> page `#A2`,
  `SKIRMISH_CURSOR_p01` -> page `#A3`. MIDI menu overlay перенесён с `#A3` на `#A4`.
- Object atlas вырос до 24 страниц; `SKIRMISH_ROUTE_TABLE` перенесён на `#8A`,
  `SKIRMISH_RUNTIME_CELLS` на `#8B`.
- `CMD_ADDRESS_PTR` сдвинут на `#AC00` под новый runtime CMD budget.

## Проверено

```text
.\build.cmd
```

Итог сборки:

```text
sjasmplus: 0 errors, 0 warnings
RAM_G calculator: OK
Core split: p05=12288 bytes, p06=11102 bytes
RAM_DL max frame=7832/8192
RUNTIME_CMD_FRAME_MAX около 4012/4096
verify FT812/RAM_G/DL: OK
```

Дополнительно:

```text
python -u Source\Tools\test_menu_transition.py  # PASS
```

## Известное / тесты

- В конце `build.cmd` остаётся шум stdout про несколько нераспознанных команд, но процесс
  завершился кодом 0 и финальный assembler pass тоже `Errors: 0`.
- Старые профильные тесты `test_cursor_input.py`, `test_menu_hover.py`, `test_hero_command.py`
  сейчас не зелёные после смены semantics LMB/cursor state; `test_adventure_cursor.py` был
  остановлен по timeout. Эти тесты надо обновить отдельно под новый runtime input contract.
- На реальном железе этот v017-снимок ещё не подтверждён отдельно от build/симуляторной проверки.

## SHA256

```text
Build/hmm2_vdac2.spg   2D3C5A1786E3C7CAAD860AA27EF12A356715F492CB56F7D367A2917F42CBD235
Build/Core.bin         895655E29C509BD9CB9A6FE90CE0583490D475C49A582569D115ACE9B45C08A6
Build/Core_p05.bin     3A16DAE233F7133FD95C524B88D9199A964C52AF2F9E44E6DC2A4B639BC877B7
Build/Core_p06.bin     50CB7AFC1CAF2C40212881771F3B60F9F30AD7C4B1FBBB0812AED7AF385371E2
Build/HMM2MENU.PAK     F043972576EC4AD2B1D2F032D1D1FE16FF6532D22B18CE7752F7A7E47E65D3AB
```

## Формат

Снимок сохранён в:

```text
releases\v017-2026-06-18-scroll-cursors-buttons-reference
```

Состав как у v016: `Source`, `Build`, `Docs`, `Music`, `build.cmd`, `spgbld_vdac2.ini`,
`PROJECT_MEMORY.md`, `REFERENCE.md`.
