# v020 — 2026-07-16 — Adventure UI assets + Battle AI fix

Опорная версия текущего успешно собранного проекта с исходниками в штатном формате
серии `Pre-releases`.

## Основное состояние

- Adventure UI перенесён в отдельный `UIAdv`-блок RAM_G с обязательной повторной
  загрузкой после возврата из town-сцены.
- Статические части списков героев/замков заранее вбейканы в фоновые полосы для
  снижения построчной нагрузки FT812.
- Исправлено зависание `Battle_AIArcMeleePick` на разреженной adjacency mask.
- Сохранены диагностические и reproduction-инструменты для battle, cursor, monster,
  status font и recruit dialog.
- В снимок входит накопленное состояние после v019: recruit/economy/garrison,
  battle UI/settings/help, меню и выбор сценария, enemy adventure AI и полная
  анимация героя.

## Сборка

```text
.\build.cmd
```

Результат:

```text
sjasmplus: 0 errors, 0 warnings
Core split: p05=12288 bytes, p06=12210 bytes
RAM_DL max frame=7892/8192
RAM_G calculator: OK
SPG build: OK
FT812/RAM_G/DL verify: OK
```

Исходное состояние проекта: Git commit
`0147c4920895829e4a33a2141f1cfcdd0a68f7ec`.

Подробные контрольные суммы и состав снимка находятся в `REFERENCE.md`.
