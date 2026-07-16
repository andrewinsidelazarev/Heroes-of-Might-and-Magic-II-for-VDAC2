# СПЕКА: Dialog::RecruitMonster (Проход 1 по CLAUDE.md)

Источник: `OpenHMM2/src/fheroes2/dialog/dialog_recruit.cpp` + `gui/ui_window.cpp` + ассеты AGG.
Каждый пункт привязан к строке оригинала. Это и есть единственный источник истины для Прохода 2.
Масштаб порта VDAC2 = ×1.6 (native → 1024×768), окно по центру экрана.

## 1. Окно (НЕ RECRBKG!)
- `StandardWindow` active-area **299×272**, центр экрана + windowOffsetY `:273-276`.
- Бордюр `borderWidthPx` = **16px** вокруг active-area `ui_window.cpp:35`.
- `render()`: рамка тайлится из `ICN::SURDRBKG`(гориз.) + `ICN::WINLOSE`(верт.); углы (cornerSize), края, заливка фоном `ui_window.cpp:139-235`. **Портировать как bake-композит 299×272 (+бордюр).**

## 2. Композитные куски (поверх окна, координаты от offset = угол active-area)
- **Поле счётчика**: спрайт **68×19** = вырез `RECRBKG[0](134,159)`; рисуется в `(118,143)`, ввод-зона `(118,147)` `:285-295`. Тень `addGradientShadow(поле,(118,143),{-5,5})` `:296`.
- **Рамка «Cost per troop»**: спрайт **132×67** в `(132,38)`; собран: `BLDGXTRA[0]`(137×72) куски (3,58)→(3,0)63×14 и (w-66,58)→(66,0)63×14; борта `RECRBKG[0]`(138,54)→(0,0)3×63 / (267,54)→(129,0)3×63 / (138,117)→(0,63)132×4; текст «Cost per troop:» smallWhite центр y=3 `:69-87,300`.

## 3. Кнопки (ICN-спрайты, у каждой `drawButtonShadow`)
- OKAY `(18,233)` `:304-309`; CANCEL `(299−18−w,233)` `:311-315`.
- MAX/MIN `(253−w/2,140)` `:317-324`; UP `(189,138)` / DN `(189,153)` = `RECRUIT.ICN`[0/1],[2/3], размер 20×10 `:326-333`.

## 4. Шрифты (высота глифа из ICN)
- `SMALFONT.ICN` = **9px** = `smallWhite/smallYellow`.
- `FONT.ICN` = **14px** = `normalWhite/normalYellow`.
- Заголовок «Recruit X» = **normalYellow/FONT 14** `:164`; счётчик(result) = **normalWhite/FONT 14** `:101`.
- Available / Number to buy / Cost per troop / итог = **smallWhite/SMALFONT 9**.
- ⚠ Текущий порт печёт ВСЁ в SMALFONT (`town_pack:309`) → заголовок и счётчик неверного размера.

## 5. Текст/спрайт (RedrawMonsterInfo/CurrentInfo, всё от offset, offsetX=10 т.к. showTotalSum)
- Заголовок: `x+(width−tw)/2, y+11` `:165`.
- Спрайт монстра (статик-кадр, размер РАЗНЫЙ — Paladin 49×87, Centaur 59×66): `x+64+smon.x()−(wide?22:0), y+119−h+extraY` `:173-182`.
- Икона золота `RESOURCE[6]`(68×25): `x+159+10, y+59`; число `x+189+10−tw/2, y+89` `:209,136-148`.
- Икона золота ИТОГА: `x+159−45, y+59+125` = `x+114,y+184` `:150-152`.
- «Available: N»: `x+64−tw/2, y+120+max(extraY,2)` `:212-215`.
- «Number to buy:»: `x+107−tw, y+149` `:217-220`.
- Счётчик: `x+151−tw/2, y+147` `:101-106`.
- Итог «стоимость (остаток)»: `x+144−tw/2, y+214` `:108,124`.
- Старт `result = CalculateMax` (по казне и доступности) `:268-269`.

## Проход 2 — единицы (по CLAUDE.md, по одной + прогон):
1. bake StandardWindow 299×272 (+бордюр16) из SURDRBKG/WINLOSE.
2. FONT-атлас 14px + рендер-вариант; заголовок и счётчик на него.
3. bake рамки cost 132×67.
4. поле счётчика 68×19 + его тень.
5. кнопки OKAY/CANCEL/MAX/UP/DN + тени.
6. текст по формулам `−tw/2` / `−tw` (ширина строки, не хардкод).
