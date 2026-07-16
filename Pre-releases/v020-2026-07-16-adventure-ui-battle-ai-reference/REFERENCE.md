# HMM2 v020 reference — adventure UI assets and battle AI fix

Дата: 2026-07-16

Статус: **опорная по текущему успешно собранному build**. Это снимок проекта в формате
серии `Pre-releases`: `Source`, `Build`, `Docs`, `Music`, корневые build/config-файлы,
память проекта и описание версии.

## Привязка

- Исходный Git-коммит: `0147c4920895829e4a33a2141f1cfcdd0a68f7ec`
- Целевая платформа: TS-Config / VDAC2 / FT812
- Каталог: `Pre-releases\v020-2026-07-16-adventure-ui-battle-ai-reference`

## Ключевое состояние

- Adventure UI использует отдельный блок ассетов `UIAdv` в хвосте RAM_G.
- При каждом `Adventure_Enter` UI-блок загружается повторно, поскольку town-сцена
  перезаписывает пересекающуюся область RAM_G.
- Статические элементы списков героев/замков вбейканы в фоновые полосы, уменьшая
  построчную нагрузку FT812.
- Исправлен зависающий цикл `Battle_AIArcMeleePick`: индекс кандидата теперь обновляется
  на каждой итерации, включая unset-биты adjacency mask.
- В reference входят текущие инструменты воспроизведения боевых и UI-регрессий.
- Сохранена вся история функциональности после v019: town recruit/economy/garrison,
  battle UI/settings/help, меню и выбор сценария, enemy adventure AI, анимация героя.

## Проверено

```text
.\build.cmd
```

Итог:

```text
sjasmplus: 0 errors, 0 warnings
Core split: p05=12288 bytes, p06=12210 bytes
RAM_DL max frame=7892/8192
RAM_G calculator: OK
SPG build: OK
FT812/RAM_G/DL verify: OK
```

## SHA256

```text
Build/hmm2_vdac2.spg  FF70DC6D04920F7E4057E1CBBAE6F82DC661EC83EB4DEF65A29678EA11B69B5C
Build/Core.bin        D0F48242A08F3FF79C4AE7DD784EE22238F05000243100BE6AF73EAF1DE3C359
Build/Core_p05.bin    9200CFC90A5A4806CAEAE0BFBA8D530721761ABA17D50DF9C23AAB92E16907D8
Build/Core_p06.bin    41318A408544CE97DF8CB94A7F1B6F4383250A41D718CD2FA3CC225A85297C84
Build/HMM2MENU.PAK    616DBCD29AC229B0164946B2E1A2C56D40D8E668C80B5459AB28B4965990C2EC
Build/HMM2TOWN.PAK    B7A0572DD4072FDB709A3FDC684DB319C80C567005858EDE10479BE7DE1BA379
Build/HMM2BATL.PAK    4B8C5E8ACBFD75A764891A7A1C63B2FA0B46B8AED55239F52C25C87F63672E74
Build/HMM2HISC.PAK    DB6FF8F7B64F9B9CC0290F72AB35E8332340E7DFFAA63165EBFE06B11202FDE5
Build/HMM2MAP.PAK     D6C5A2D68AA26085B30F933E04F71DCABFA133628F29005664F4805BF929C62A
Build/HMM2SCN.PAK     9269CA0F5550B3AE01B7D5D3897562F0D5548057BA8584BCA4EA694CAAAE4432
```

## Формат снимка

В reference копируются:

```text
Source\
Build\
Docs\
Music\
build.cmd
spgbld_vdac2.ini
PROJECT_MEMORY.md
REFERENCE.md
RELEASE_NOTES.md
```

Не копируются локальные `.git`, `.claude`, `__pycache__`, временные каталоги сборки
эмулятора, сырые игровые ресурсы `Assets/Original`, `Diagnostics` и внешние reference-проекты.
