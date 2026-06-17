# Скролл pseudo-DXT L4 фона HMM2

Этот документ фиксирует, как скроллить фон карты в формате Zuma
`c0 RGB565 + c1 RGB565 + L4 mask`, когда игра работает в логическом окне
640x480, а FT812 физически выводит 1024x768 через nearest 8/5.

## Что берём из Zuma

В загрузчике Zuma фон выводится в три прохода:

1. L4 mask пишет только destination alpha.
2. RGB565 слой `c1` рисуется с `BLEND_FUNC(DST_ALPHA, ZERO)`.
3. RGB565 слой `c0` рисуется с `BLEND_FUNC(ONE_MINUS_DST_ALPHA, ONE)`.

Цветовые слои являются endpoint-сеткой DXT: один texel endpoint-слоя покрывает
4x4 пикселя исходного изображения. Маска L4 хранится в полном разрешении.

## Что добавляет HMM2

Для карты нужен не статичный 640x480 фон, а рабочий фон 21x16 тайлов:

- исходный scroll-buffer: 672x512;
- видимое логическое окно: 640x480;
- физический вывод: 1024x768;
- `ViewportOriginX/Y` задаёт левый верхний тайл, по нему фон пересобирается;
- `ViewportPixelX/Y & 31` задаёт пиксельный остаток внутри этого фона.

Фон нельзя перезаливать при каждом пикселе скролла. Перезаливка нужна только
при смене `ViewportOriginX/Y`. Пиксельный скролл делается матрицей FT812.

## Формулы матрицы

FT812 bitmap matrix читает источник так:

```text
src_x = (A * dst_x + C) / 256
src_y = (E * dst_y + F) / 256
```

Для physical 1024x768 один физический пиксель равен `5/8` логического пикселя.

Для L4 mask:

```text
A = E = 256 * 5 / 8 = 160
C = rem_x * 256
F = rem_y * 256
```

Для RGB565 endpoint-слоёв:

```text
A = E = 256 * 5 / (8 * 4) = 40
C = rem_x * 64
F = rem_y * 64
```

`rem_x` и `rem_y` всегда в диапазоне `0..31`, потому что при переходе через
границу тайла меняется `ViewportOriginX/Y`, а scroll-buffer пересобирается уже
от нового тайла.

## Почему нельзя сдвигать только L4

L4 mask и RGB565 endpoint-слои описывают один и тот же DXT-блок. Если двигать
только L4, blend alpha уедет относительно цветов. Скролл должен применяться ко
всем трём проходам:

- mask: `A/E=160`, `C/F=rem*256`;
- `c1`: `A/E=40`, `C/F=rem*64`;
- `c0`: `A/E=40`, `C/F=rem*64`.

## Проверка

Расчёт можно проверить командой:

```powershell
python Source\Tools\dxt_l4_scroll_math.py --rem-x 31 --rem-y 31
```

Ожидаемые крайние значения:

- L4 `C/F = #001F00`;
- RGB565 endpoint `C/F = #0007C0`;
- размеры RAW для 672x512: `258048` байт.

Сборка тестового RAW фона текущего экрана:

```powershell
python Source\Tools\dxt_l4_scroll_buffer.py --origin-x 0 --origin-y 0
```

Этот инструмент рендерит terrain текущего 21x16 экрана из `GROUND32.TIL`,
кодирует его CPU-only в layout `c0+c1+L4`, пишет `.raw`, 16-КБ страницы для
загрузки, `Source/ASM/generated_dxt_background.inc` с адресами/размерами и
`Source/ASM/generated_dxt_scroll_dl.inc` с DL-шаблоном вывода. Он не
переключает основной рендер сам по себе.

## Полная карта как источник SPI

Полный terrain-фон карты 36x36 хранится как один DXT L4 RAW:

```text
Assets/Converted/Background/SKIRMISH_FULLMAP_DXT_L4.raw
```

Размер `1152x1152`, layout тот же:

- `c0`: `288 * 288 * 2 = 165888` байт;
- `c1`: `165888` байт;
- `mask`: `1152 * 1152 / 2 = 663552` байт;
- всего: `995328` байт.

В `RAM_G` целиком его не грузить. Это источник для SPI/SD. В `RAM_G` остаётся
одно рабочее окно `672x512`.

Окно `origin_x/origin_y` вырезается без декодирования:

```text
pixel_x = origin_x * 32
pixel_y = origin_y * 32

block_x = pixel_x / 4
block_y = pixel_y / 4

c0 offset row = full_c0 + block_y * full_color_stride + block_x * 2
c1 offset row = full_c1 + block_y * full_color_stride + block_x * 2
mask offset row = full_mask + pixel_y * full_mask_stride + pixel_x / 2
```

Копировать надо:

- `c0`: `128` строк по `336` байт;
- `c1`: `128` строк по `336` байт;
- `mask`: `512` строк по `336` байт.

Проверка layout:

```powershell
python Source\Tools\dxt_l4_extract_window.py --origin-x 0 --origin-y 0 --compare Assets\Converted\Background\SKIRMISH_BG_DXT_L4.raw
```

Результат должен быть byte-for-byte одинаковым.
