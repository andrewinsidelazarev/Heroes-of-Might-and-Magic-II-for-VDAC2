#!/usr/bin/env python3
from __future__ import annotations

import math
import os
import struct
from dataclasses import dataclass
from pathlib import Path

from agg_tools import read_agg_index, read_agg_index_with_expansion
from object_atlas import (
    ICN_BY_OBJECT_TYPE,
    agg_entry,
    decode_icn_paletted,
    decode_icn_sprite,
    read_icn,
    read_palette,
)
from terrain_atlas import read_til, to_rgb565, transform_tile, write_preview_png
from terrain_preview import TILE_PX, read_map
from map_tools import OBJECT_INFO


PAGE_SIZE = 0x4000
VIEWPORT_DL_SIZE = 3072
OBJECT_VIEW_DL_SIZE = 16384
RUNTIME_TILEMAP_RENDER = os.environ.get("HMM2_RUNTIME_TILEMAP", "1") != "0"
COMPOSITE_STATIC_TILEMAP = os.environ.get("HMM2_COMPOSITE_STATIC", "1") != "0"
GAME_VIEW_X = 16
GAME_VIEW_Y = 16
GAME_VIEW_W = 448
GAME_VIEW_H = 448
VIEW_W = GAME_VIEW_W // TILE_PX
VIEW_H = GAME_VIEW_H // TILE_PX
PACK_VIEW_W = VIEW_W + 1 if RUNTIME_TILEMAP_RENDER else VIEW_W
PACK_VIEW_H = VIEW_H + 1 if RUNTIME_TILEMAP_RENDER else VIEW_H
RUNTIME_SPLIT_X = min(16, PACK_VIEW_W)
OBJECT_VIEW_MARGIN_TILES = 4
TERRAIN_PAGE_BASE = 0x20
OBJECT_PAGE_BASE = 0x07
OBJECT_PAGE_LIST = [*range(0x72, 0x96)] if COMPOSITE_STATIC_TILEMAP else [*range(0x01, 0x05), *range(0x07, 0x10), 0x11, 0x13, *range(0x15, 0x20)]
OBJECT_VIEW_PAGE_BASE = 0x96 if COMPOSITE_STATIC_TILEMAP else 0x3C
# КРИТИЧНО: НЕ включать страницы карты/пути — иначе раздутый object-view payload
# затрёт их (баг «герой застревает»: 0x11=MAP0_PATH_PAGE с cost/flags пути был
# затёрт объектным DL → ложная «вода» → pathfinding обрывался). Зарезервированы:
# 0x10=MAP0_SPG, 0x11=MAP0_PATH, 0x13=PathWorkPage, 0x14=MAP0_PASS, 0xC4=COMPOSITE_UPLOAD.
OBJECT_VIEW_PAGE_LIST = ([
    *range(0x01, 0x05), *range(0x07, 0x10),          # пропускает 0x05/0x06 и 0x10
    *range(0x15, 0x20),                              # 0x11/0x13/0x14 НЕ занимать
    *range(0x96, 0xC4), *range(0xC5, 0xE0),          # 0xC4 = COMPOSITE_UPLOAD
    *range(0xF8, 0x100),
] if COMPOSITE_STATIC_TILEMAP else None)
COMPOSITE_UPLOAD_PAGE_BASE = 0xC4
VIEWPORT_PAGE_BASE = 0x70
RUNTIME_MAP_CELLS_NAME = "SKIRMISH_RUNTIME_CELLS.bin"
RAMG_TERRAIN_BASE = 0x000000
FULLMAP_DXT = False
COMPOSITE_BG_PALETTED4444 = COMPOSITE_STATIC_TILEMAP
COMPOSITE_BG_PALETTE_SIZE = 512
COMPOSITE_BG_TILE_OFFSET = ((COMPOSITE_BG_PALETTE_SIZE + PAGE_SIZE - 1) & ~(PAGE_SIZE - 1)) if COMPOSITE_BG_PALETTED4444 else 0
COMPOSITE_BG_TILE_BASE = RAMG_TERRAIN_BASE + COMPOSITE_BG_TILE_OFFSET
COMPOSITE_TILE_BYTES = TILE_PX * TILE_PX if COMPOSITE_BG_PALETTED4444 else TILE_PX * TILE_PX * 2
COMPOSITE_SLOT_COUNT = PACK_VIEW_W * PACK_VIEW_H
COMPOSITE_TILE_CACHE_SIZE = COMPOSITE_BG_TILE_OFFSET + COMPOSITE_SLOT_COUNT * COMPOSITE_TILE_BYTES
COMPOSITE_CACHE_BANKS = 2 if COMPOSITE_STATIC_TILEMAP else 1
COMPOSITE_RAMG_CACHE_SIZE = COMPOSITE_TILE_CACHE_SIZE * COMPOSITE_CACHE_BANKS
RAMG_OBJECT_BASE = ((COMPOSITE_RAMG_CACHE_SIZE + 0x0FFF) & ~0x0FFF) if COMPOSITE_STATIC_TILEMAP else 0x070000
# Глобальный курсор: ПОСТОЯННАЯ зона RAM_G выше object atlas и ниже DL #0F0000.
# ВНИМАНИЕ: object atlas разросся до ~#0E3382 (objects base #079000 + 435138 байт), поэтому
# прежняя база #0E0000 попадала ВНУТРЬ объектов → Objects_Upload затирал курсор #00-паддингом
# (курсор был невидим всегда). Подняли выше конца объектов: #0E8000..#0ED37C (DL @ #0F0000).
# Доступен всем сценам; не перезаписывается сменой сцены.
CURSOR_RAMG_BASE = 0x0E8000
CURSOR_RESIDENT_PAGE = 0xA2          # SPG-страница курсор-спрайтов (рядом с loader #A0/#A1, ≤#F0)
OBJECT_PALETTE_SIZE = 512
OBJECT_OPAQUE_PALETTE_SIZE = 512
OBJECT_TRANSPARENT_INDEX = 0
CELLS_PER_HANDLE = 128
DYNAMIC_VISUAL_ICNS = {
    "FLAG32.ICN",
    "OBJNARTI.ICN",
    "OBJNRSRC.ICN",
    "MONS32.ICN",
}
FULL_VIEWPORT_PACK = os.environ.get("HMM2_FULL_VIEWPORT_PACK", "1") != "0"
COMPACT_VIEWPORT_ORIGINS_X = int(os.environ.get("HMM2_COMPACT_VIEWPORT_ORIGINS_X", "3"))
COMPACT_VIEWPORT_ORIGINS_Y = int(os.environ.get("HMM2_COMPACT_VIEWPORT_ORIGINS_Y", "3"))
DISPLAY_SCALE_NUM = int(os.environ.get("HMM2_DISPLAY_SCALE_NUM", "8"))
DISPLAY_SCALE_DEN = int(os.environ.get("HMM2_DISPLAY_SCALE_DEN", "5"))
# Физический режим 1024x768 показывает логический 640x480 viewport через nearest 8/5.
DISPLAY_TILE_PX = (TILE_PX * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN
DISPLAY_BITMAP_TRANSFORM = (256 * DISPLAY_SCALE_DEN) // DISPLAY_SCALE_NUM

FT_BITMAPS = 1
FT_L1 = 1
FT_ARGB4 = 6
FT_RGB565 = 7
FT_PALETTED4444 = 15
FT_NEAREST = 0
FT_BORDER = 0
FT_REPEAT = 1
FT_ZERO = 0
FT_ONE = 1
FT_SRC_ALPHA = 2
FT_DST_ALPHA = 3
FT_ONE_MINUS_SRC_ALPHA = 4
FT_ONE_MINUS_DST_ALPHA = 5
ROUTE_SPRITE_COUNT = 145
BORDER_PX = 16
# Логическое пространство, в котором верстается панель (как fheroes2 display).
# 640x480 = текущая система (всё логическое, отрисовка x1.6). 1024x768 = нативная
# панель (8 слотов), требует перевода клика/курсора/бюджета DL.
PANEL_DISPLAY_W = 640
PANEL_DISPLAY_H = 480
UI_RADAR_X = 480
UI_RADAR_Y = 16
UI_RADAR_SIZE = 144
UI_BUTTON_X = 480
UI_BUTTON_Y = 320
UI_BUTTON_W = 36
UI_BUTTON_H = 36
UI_BUTTON_INDICES = [0, 2, 4, 6, 8, 10, 12, 14]
UI_STATUS_X = 480
UI_STATUS_Y = 392
UI_STATUS_W = 144
UI_STATUS_H = 72
CURSOR_POINTER_INDEX = 0
CURSOR_MOVE_BASE_INDEX = 1
CURSOR_MOVE_DIGIT_COLOR = 115
CURSOR_MOVE_CONTOUR_COLOR = 35
CURSOR_MOVE_DIGIT_OFFSET = (-2, 1)
CURSOR_DIGIT_POINTS = [
    [(2, 1), (3, 1), (1, 2), (4, 2), (3, 3), (2, 4), (1, 5), (2, 5), (3, 5), (4, 5)],
    [(1, 1), (2, 1), (3, 1), (4, 2), (1, 3), (2, 3), (3, 3), (4, 4), (1, 5), (2, 5), (3, 5)],
    [(1, 1), (3, 1), (1, 2), (3, 2), (1, 3), (2, 3), (3, 3), (4, 3), (3, 4), (3, 5)],
    [(1, 1), (2, 1), (3, 1), (4, 1), (1, 2), (1, 3), (2, 3), (3, 3), (4, 4), (1, 5), (2, 5), (3, 5)],
    [(2, 1), (3, 1), (1, 2), (1, 3), (2, 3), (3, 3), (1, 4), (4, 4), (2, 5), (3, 5)],
    [(1, 1), (2, 1), (3, 1), (4, 1), (4, 2), (3, 3), (2, 4), (2, 5)],
]
CURSOR_PLUS_POINTS = [(2, 1), (1, 2), (2, 2), (3, 2), (2, 3)]


def pack_origin_max(width: int, height: int) -> tuple[int, int]:
    if FULL_VIEWPORT_PACK:
        return width - VIEW_W, height - VIEW_H
    return (
        max(0, min(width - VIEW_W, COMPACT_VIEWPORT_ORIGINS_X - 1)),
        max(0, min(height - VIEW_H, COMPACT_VIEWPORT_ORIGINS_Y - 1)),
    )


def cmd(value: int) -> bytes:
    return struct.pack("<I", value & 0xFFFFFFFF)


def c_display():
    return cmd(0 << 24)


def c_bitmap_source(addr):
    return cmd((1 << 24) | (addr & 0xFFFFF))


def c_clear_color_rgb(r, g, b):
    return cmd((2 << 24) | ((r & 255) << 16) | ((g & 255) << 8) | (b & 255))


def c_color_rgb(r, g, b):
    return cmd((4 << 24) | ((r & 255) << 16) | ((g & 255) << 8) | (b & 255))


def c_bitmap_handle(handle):
    return cmd((5 << 24) | (handle & 31))


def c_cell(cell):
    return cmd((6 << 24) | (cell & 127))


def c_bitmap_layout(fmt, stride, height):
    return cmd((7 << 24) | ((fmt & 31) << 19) | ((stride & 1023) << 9) | (height & 511))


def c_bitmap_size(width, height, wrapx=FT_BORDER, wrapy=FT_BORDER):
    return cmd((8 << 24) | ((FT_NEAREST & 1) << 20) | ((wrapx & 1) << 19) | ((wrapy & 1) << 18) | ((width & 511) << 9) | (height & 511))


def c_palette_source(addr):
    return cmd((42 << 24) | (addr & 0x3FFFFF))


def c_bitmap_transform_a(value):
    return cmd((21 << 24) | (value & 0x1FFFF))


def c_bitmap_transform_e(value):
    return cmd((25 << 24) | (value & 0x1FFFF))


def c_blend_func(src, dst):
    return cmd((11 << 24) | ((src & 7) << 3) | (dst & 7))


def c_color_a(alpha):
    return cmd((16 << 24) | (alpha & 255))


def c_color_mask(r, g, b, a):
    return cmd((32 << 24) | ((r & 1) << 3) | ((g & 1) << 2) | ((b & 1) << 1) | (a & 1))


def c_begin(prim):
    return cmd((31 << 24) | (prim & 15))


def c_end():
    return cmd(33 << 24)


def c_clear(color, stencil, tag):
    return cmd((38 << 24) | ((color & 1) << 2) | ((stencil & 1) << 1) | (tag & 1))


def c_vertex2f(x, y):
    return cmd((64 << 24) | ((x & 32767) << 15) | (y & 32767))


def c_vertex2ii(x, y, handle, cell):
    return cmd((2 << 30) | ((x & 511) << 21) | ((y & 511) << 12) | ((handle & 31) << 7) | (cell & 127))


def scaled_vertex2f_units(value: int) -> int:
    return (value * DISPLAY_SCALE_NUM * 16 + DISPLAY_SCALE_DEN // 2) // DISPLAY_SCALE_DEN


def native_vertex2f_units(value: int) -> int:
    # Панель рисуется НАТИВНО (1:1), без ×1.6: VERTEX2F = px * 16.
    return value * 16


def map_vertex2f_units(value: int) -> int:
    return (value * DISPLAY_SCALE_NUM * 16) // DISPLAY_SCALE_DEN


def map_tile_vertex2f_units(tile_index: int) -> int:
    return map_vertex2f_units(tile_index * TILE_PX)


def scaled_screen_pixels(value: int) -> int:
    return (value * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN


def tile_vertex2f_units(tile_index: int) -> int:
    # Шаг тайлов должен идти по точному масштабу 32*8/5=51.2px.
    # Округленный bitmap size 52px нужен только как запас перекрытия, иначе
    # край тайла попадает в FT_BORDER и при скролле появляется черная сетка.
    return map_tile_vertex2f_units(tile_index)


def c_nop():
    return cmd(45 << 24)


def align(value: int, step: int) -> int:
    return (value + step - 1) & ~(step - 1)


def write_chunks(out_dir: Path, pattern: str, page_base: int, payload: bytes):
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob(pattern.replace("{:02d}", "*")):
        old.unlink()
    chunks = []
    for i in range(math.ceil(len(payload) / PAGE_SIZE)):
        chunk = payload[i * PAGE_SIZE:(i + 1) * PAGE_SIZE]
        padded = chunk + b"\0" * (PAGE_SIZE - len(chunk))
        path = out_dir / pattern.format(i)
        path.write_bytes(padded)
        chunks.append((path, page_base + i, len(chunk)))
    return chunks


def write_chunks_pages(out_dir: Path, pattern: str, pages: list[int], payload: bytes):
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob(pattern.replace("{:02d}", "*")):
        old.unlink()
    need = math.ceil(len(payload) / PAGE_SIZE)
    if need > len(pages):
        raise ValueError(f"{pattern}: нужно {need} страниц, доступно {len(pages)}")
    chunks = []
    for i in range(need):
        chunk = payload[i * PAGE_SIZE:(i + 1) * PAGE_SIZE]
        padded = chunk + b"\0" * (PAGE_SIZE - len(chunk))
        path = out_dir / pattern.format(i)
        path.write_bytes(padded)
        chunks.append((path, pages[i], len(chunk)))
    return chunks


def all_terrain_keys(tiles):
    out = []
    seen = set()
    for tile in tiles:
        key = (tile["terrain"], tile["terrain_flags"] & 3)
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def build_terrain_atlas(ground_tiles, palette, keys):
    payload = bytearray()
    remap = {}
    for i, (terrain, shape) in enumerate(keys):
        if terrain >= len(ground_tiles):
            raise ValueError(f"terrain {terrain} вне GROUND32.TIL")
        remap[(terrain, shape)] = (i // CELLS_PER_HANDLE, i % CELLS_PER_HANDLE)
        payload.extend(to_rgb565(transform_tile(ground_tiles[terrain], shape), palette))
    return bytes(payload), remap


def cycled_terrain_indices(ground_tiles) -> frozenset:
    """Индексы наземных тайлов, чьи пиксели попадают в палитровый цикл-диапазон
    (анимир. вода 231-237). Data-driven, не зависит от карты/нумерации терэйна:
    объекты на таких тайлах должны ТОЛЬКО запекаться (мерцать синхронно с водой),
    а не рисоваться статичным оверлеем поверх (иначе кромка рассинхронится)."""
    lo, hi = WATER_CYCLE_INDEX, WATER_CYCLE_INDEX + WATER_CYCLE_COUNT
    return frozenset(i for i, tile in enumerate(ground_tiles) if any(lo <= px < hi for px in tile))


@dataclass(frozen=True)
class ObjectTransferPlan:
    width: int
    height: int
    static_by_tile: tuple[tuple[dict, ...], ...]
    dynamic_by_tile: tuple[tuple[dict, ...], ...]
    top_by_tile: tuple[tuple[dict, ...], ...]
    cycled_by_tile: tuple[bool, ...] = ()

    def static_at(self, x: int, y: int) -> tuple[dict, ...]:
        return self.static_by_tile[y * self.width + x]

    def dynamic_at(self, x: int, y: int) -> tuple[dict, ...]:
        return self.dynamic_by_tile[y * self.width + x]

    def top_at(self, x: int, y: int) -> tuple[dict, ...]:
        return self.top_by_tile[y * self.width + x]

    def is_cycled_tile(self, x: int, y: int) -> bool:
        idx = y * self.width + x
        return bool(self.cycled_by_tile and self.cycled_by_tile[idx])


def build_object_transfer_plan(width: int, height: int, map_data, cycled_terrain=frozenset()) -> ObjectTransferPlan:
    tiles, addons = map_data if isinstance(map_data, tuple) else (map_data, [])
    static_by_tile: list[tuple[dict, ...]] = []
    dynamic_by_tile: list[tuple[dict, ...]] = []
    top_by_tile: list[tuple[dict, ...]] = []
    cycled_by_tile: list[bool] = []
    for y in range(height):
        for x in range(width):
            tile = tiles[y * width + x]
            parts = tile_object_parts_original(tile, addons, x, y)
            # СИСТЕМНОЕ правило: если наземный тайл палитрово-циклится (анимир.
            # вода), ВСЕ его объекты только запекаются — без оверлея. Причина: герой
            # по воде не ходит (окклюзия не нужна), а статичный оверлей поверх
            # циклящей воды рассинхронит кромку объекта → «камень портится по Z».
            # Запечённый объект мерцает В СИНХРОНЕ с водой (как в оригинале HMM2).
            is_cycled = tile["terrain"] in cycled_terrain
            cycled_by_tile.append(is_cycled)
            if is_cycled:
                static_by_tile.append(tuple(parts))   # всё в фон, без оверлея
                dynamic_by_tile.append(())
                top_by_tile.append(())
                continue
            # z-слои fheroes2: top-слой (level2) рисуется ПОВЕРХ героев/актёров.
            # ВАЖНО: top-части одного объекта чередуются с низ-частями потайлово
            # (горы/постройки), поэтому НЕЛЬЗЯ просто вынуть top из запекания — в
            # фоне появятся дыры/срезы («замок обрезан по Z»). Решение: запекаем
            # ВСЮ статику (низ И top) → фон ЦЕЛЫЙ; top-части ДОПОЛНИТЕЛЬНО рисуем
            # оверлеем после актёра (z над героем). Двойная отрисовка top-статики
            # безопасна — оверлей перерисовывает те же пиксели поверх (или поверх
            # героя, если он под top-частью).
            bottom_parts = [p for p in parts if not p["top"]]
            top_parts = [p for p in parts if p["top"]]
            static_bottom, dynamic_bottom = split_static_dynamic_parts(bottom_parts)
            top_static, _top_dynamic = split_static_dynamic_parts(top_parts)
            static_by_tile.append(tuple(static_bottom + top_static))
            dynamic_by_tile.append(tuple(dynamic_bottom))
            top_by_tile.append(tuple(top_parts))
    return ObjectTransferPlan(width, height, tuple(static_by_tile), tuple(dynamic_by_tile), tuple(top_by_tile), tuple(cycled_by_tile))


def validate_object_transfer_plan(plan: ObjectTransferPlan) -> None:
    for y in range(plan.height):
        for x in range(plan.width):
            # На циклящихся (водных) тайлах ВСЕ объекты намеренно только в фоне
            # (без оверлея) — проверки слоёв к ним не применяем.
            if plan.is_cycled_tile(x, y):
                if plan.dynamic_at(x, y) or plan.top_at(x, y):
                    raise ValueError(f"объект циклящегося тайла попал в оверлей: tile={x},{y}")
                continue
            for part in plan.dynamic_at(x, y):
                icn = part["icn"].upper()
                if not part_is_dynamic(part):
                    raise ValueError(f"динамика вне правила: tile={x},{y} {icn}#{part['index']}")
            for part in plan.static_at(x, y):
                icn = part["icn"].upper()
                if part_is_dynamic(part):
                    raise ValueError(f"динамический ICN попал в фон: tile={x},{y} {icn}#{part['index']}")
                # top-статика теперь НАМЕРЕННО и в фоне (целостность), и в оверлее
            for part in plan.top_at(x, y):
                if not part["top"]:
                    raise ValueError(f"низ-слой попал в top-оверлей: tile={x},{y} {part['icn'].upper()}#{part['index']}")


def build_composite_tiles(ground_tiles, agg_data, entries, palette, width: int, height: int, map_data, transfer_plan: ObjectTransferPlan) -> bytes:
    tiles = map_data[0] if isinstance(map_data, tuple) else map_data
    if COMPOSITE_BG_PALETTED4444:
        canvas = bytearray(width * height * TILE_PX * TILE_PX)
    else:
        canvas = bytearray(width * height * TILE_PX * TILE_PX * 2)
    for my in range(height):
        for mx in range(width):
            tile = tiles[my * width + mx]
            transformed = transform_tile(ground_tiles[tile["terrain"]], tile["terrain_flags"] & 3)
            if COMPOSITE_BG_PALETTED4444:
                for row in range(TILE_PX):
                    dst = (my * TILE_PX + row) * width * TILE_PX + mx * TILE_PX
                    src = row * TILE_PX
                    canvas[dst:dst + TILE_PX] = bytes(transformed[src:src + TILE_PX])
            else:
                rgb = to_rgb565(transformed, palette)
                for row in range(TILE_PX):
                    dst = ((my * TILE_PX + row) * width * TILE_PX + mx * TILE_PX) * 2
                    src = row * TILE_PX * 2
                    canvas[dst:dst + TILE_PX * 2] = rgb[src:src + TILE_PX * 2]

    icn_cache = {}
    # Глобальные проходы по уровням как в fheroes2 (interface_gamearea.cpp делает
    # отдельный полнокарточный проход на каждый layerType): сортируем все статич.
    # низ-части по рангу слоя, затем row-major. Это корректно для объектов,
    # перекрывающих границу тайла с разными слоями.
    bake_list = []
    for my in range(height):
        for mx in range(width):
            for obj in transfer_plan.static_at(mx, my):
                bake_list.append((BOTTOM_LAYER_RANK.get(obj["layer"], 3), my, mx, obj))
    bake_list.sort(key=lambda t: (t[0], t[1], t[2]))
    for _rank, my, mx, obj in bake_list:
        if obj["icn"] not in icn_cache:
            icn_cache[obj["icn"]] = read_icn(agg_entry(agg_data, entries, obj["icn"]))
        sprites = icn_cache[obj["icn"]]
        if obj["index"] >= len(sprites):
            continue
        header, encoded = sprites[obj["index"]]
        raw = decode_icn_indices(header, encoded)
        base_x = mx * TILE_PX + header["ox"]
        base_y = my * TILE_PX + header["oy"]
        for sy in range(header["h"]):
            y = base_y + sy
            if y < 0 or y >= height * TILE_PX:
                continue
            for sx in range(header["w"]):
                x = base_x + sx
                if x < 0 or x >= width * TILE_PX:
                    continue
                pix = raw[sy * header["w"] + sx]
                if pix == OBJECT_TRANSPARENT_INDEX:
                    continue
                if COMPOSITE_BG_PALETTED4444:
                    dst = y * width * TILE_PX + x
                    canvas[dst] = pix
                else:
                    r, g, b = palette[pix]
                    value = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                    dst = (y * width * TILE_PX + x) * 2
                    canvas[dst] = value & 0xFF
                    canvas[dst + 1] = value >> 8

    out = bytearray()
    if COMPOSITE_BG_PALETTED4444:
        out.extend(palette_argb4444_opaque(palette))
        while len(out) < COMPOSITE_BG_TILE_OFFSET:
            out.append(0)
    for my in range(height):
        for mx in range(width):
            for row in range(TILE_PX):
                if COMPOSITE_BG_PALETTED4444:
                    src = (my * TILE_PX + row) * width * TILE_PX + mx * TILE_PX
                    out.extend(canvas[src:src + TILE_PX])
                else:
                    src = ((my * TILE_PX + row) * width * TILE_PX + mx * TILE_PX) * 2
                    out.extend(canvas[src:src + TILE_PX * 2])
    return bytes(out)


def build_composite_upload_scripts(width: int, height: int, max_x: int, max_y: int):
    payload = bytearray()
    for my in range(height + 1):
        src_y = min(my, height - 1)
        for mx in range(width + 1):
            src_x = min(mx, width - 1)
            tile_index = src_y * width + src_x
            src_pos = COMPOSITE_BG_TILE_OFFSET + tile_index * COMPOSITE_TILE_BYTES
            page = TERRAIN_PAGE_BASE + src_pos // PAGE_SIZE
            off = src_pos % PAGE_SIZE
            slot = composite_slot_for_tile(mx, my)
            dst = COMPOSITE_BG_TILE_BASE + slot * COMPOSITE_TILE_BYTES
            payload.extend(
                (
                    page & 0xFF,
                    off & 0xFF,
                    off >> 8,
                    (dst >> 16) & 0xFF,
                    dst & 0xFF,
                    (dst >> 8) & 0xFF,
                )
            )
    if len(payload) > PAGE_SIZE:
        raise ValueError(f"таблица заливки составного фона не помещается в одну страницу: {len(payload)}")
    return bytes(payload), []


def composite_slot_for_tile(x: int, y: int) -> int:
    sx = x % PACK_VIEW_W
    sy = y % PACK_VIEW_H
    if sx < RUNTIME_SPLIT_X:
        return sy * RUNTIME_SPLIT_X + sx
    return RUNTIME_SPLIT_X * PACK_VIEW_H + sy * (PACK_VIEW_W - RUNTIME_SPLIT_X) + (sx - RUNTIME_SPLIT_X)


def palette_argb4444(palette):
    out = bytearray()
    for i, (r, g, b) in enumerate(palette):
        alpha = 0 if i == OBJECT_TRANSPARENT_INDEX else 15
        value = (alpha << 12) | ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4)
        out.extend((value & 0xFF, value >> 8))
    return bytes(out)


def palette_argb4444_opaque(palette):
    out = bytearray()
    for r, g, b in palette:
        value = (15 << 12) | ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4)
        out.extend((value & 0xFF, value >> 8))
    return bytes(out)


def l1_mask_rows(raw: bytes, width: int, height: int, cell_w: int, cell_h: int) -> bytes:
    stride = (cell_w + 7) // 8
    out = bytearray()
    for row in range(cell_h):
        row_bytes = [0] * stride
        if row < height:
            base = row * width
            for x in range(width):
                if raw[base + x] != OBJECT_TRANSPARENT_INDEX:
                    row_bytes[x >> 3] |= 0x80 >> (x & 7)
        out.extend(row_bytes)
    return bytes(out)


def object_cell_bucket(width: int, height: int) -> tuple[int, int]:
    return align(max(1, width), 4), align(max(1, height), 4)


def decode_icn_indices(header, data: bytes):
    w = header["w"]
    h = header["h"]
    pixels = [OBJECT_TRANSPARENT_INDEX] * (w * h)
    pos_x = 0
    row = 0
    p = 0
    mono = bool(header["frames"] & 0x20)
    while p < len(data) and row < h:
        cmd_byte = data[p]
        p += 1
        if cmd_byte == 0x00:
            row += 1
            pos_x = 0
            continue
        if cmd_byte == 0x80:
            break
        base = row * w + pos_x
        if mono:
            if cmd_byte < 0x80:
                for i in range(cmd_byte):
                    if 0 <= base + i < len(pixels):
                        pixels[base + i] = 1
                pos_x += cmd_byte
            else:
                pos_x += cmd_byte - 0x80
            continue
        if cmd_byte < 0x80:
            count = cmd_byte
            chunk = data[p:p + count]
            p += len(chunk)
            for i, pix in enumerate(chunk):
                if 0 <= base + i < len(pixels):
                    pixels[base + i] = pix
            pos_x += count
        elif cmd_byte < 0xC0:
            pos_x += cmd_byte - 0x80
        elif cmd_byte == 0xC0:
            if p >= len(data):
                break
            transform = data[p]
            p += 1
            count = transform & 0x03
            if count == 0:
                if p >= len(data):
                    break
                count = data[p]
                p += 1
            pos_x += count
        else:
            if cmd_byte == 0xC1:
                if p >= len(data):
                    break
                count = data[p]
                p += 1
            else:
                count = cmd_byte - 0xC0
            if p >= len(data):
                break
            pix = data[p]
            p += 1
            for i in range(count):
                if 0 <= base + i < len(pixels):
                    pixels[base + i] = pix
            pos_x += count
    return bytes(pixels)


def visible_cells(width, height, tiles, origin_x, origin_y):
    cells = []
    for y in range(PACK_VIEW_H):
        my = origin_y + y
        if my >= height:
            continue
        for x in range(PACK_VIEW_W):
            mx = origin_x + x
            if mx >= width:
                continue
            tile = tiles[my * width + mx]
            cells.append((x, y, tile["terrain"], tile["terrain_flags"] & 3))
    return cells


def tile_object_parts_original(tile, addons, tile_x: int, tile_y: int):
    parts = []

    def add(layer: int, uid: int, object_name: int, index: int, top: bool) -> None:
        icn_type = object_name >> 2
        # fheroes2 Tile::Init (maps_tiles.cpp): трещина OBJNCRCK (тип 57) с top-index
        # 226 кладётся НЕ в top-слой, а в низ-террейн (TERRAIN, под всем). Без этой
        # демоции она ушла бы в top-оверлей и нарисовалась ПОВЕРХ героя.
        if top and icn_type == 57 and index == 226:
            top = False
            layer = 3  # TERRAIN_LAYER
        icn_name = ICN_BY_OBJECT_TYPE.get(icn_type)
        if icn_name and index != 0xFF:
            parts.append(
                {
                    "tile_x": tile_x,
                    "tile_y": tile_y,
                    "icn": icn_name,
                    "index": index,
                    "object_name": object_name,
                    "type": icn_type,
                    "layer": layer,
                    "uid": uid,
                    "top": top,
                }
            )

    add(tile["quantity1"] & 0x03, tile["uid1"], tile["object_name1"], tile["bottom_icn"], False)
    add(0, tile["uid2"], tile["object_name2"], tile["top_icn"], True)

    addon_index = tile.get("next_addon", 0)
    guard = 0
    while addon_index > 0 and addon_index < len(addons) and guard < 128:
        addon = addons[addon_index]
        add(addon["quantity"] & 0x03, addon["uid1"], addon["object_name1"], addon["bottom_icn"], False)
        add(0, addon["uid2"], addon["object_name2"], addon["top_icn"], True)
        addon_index = addon["next_addon"]
        guard += 1

    ground = [part for part in parts if not part["top"]]
    top = [part for part in parts if part["top"]]
    # Порядок отрисовки низ-слоёв как в fheroes2 (interface_gamearea.cpp):
    # TERRAIN(3) → BACKGROUND(1) → SHADOW(2) → OBJECT(0). НЕ простой reverse
    # (был 3,2,1,0 — shadow/background перепутаны).
    ground.sort(key=lambda item: BOTTOM_LAYER_RANK.get(item["layer"], 3))
    return ground + top


# Маршрут слоёв fheroes2: layerType значение (quantity1 & 3) → ранг отрисовки.
# OBJECT_LAYER=0, BACKGROUND_LAYER=1, SHADOW_LAYER=2, TERRAIN_LAYER=3 (maps_tiles.h).
BOTTOM_LAYER_RANK = {3: 0, 1: 1, 2: 2, 0: 3}


def object_info_for_part(part: dict):
    return OBJECT_INFO.get((part["object_name"] >> 2, part["index"]))


def object_type_for_part(part: dict) -> int:
    info = object_info_for_part(part)
    return 0 if info is None else int(info["object_type"])


def _load_animated_parts() -> dict:
    """Анимированные (icn, base_index) -> число кадров (из object_animation.csv,
    выдрано из fheroes2 map_object_info.cpp инструментом extract_object_animation.py).
    Анимир. часть рисуется кадрами base_index+1 .. base_index+frames."""
    path = Path(__file__).resolve().parents[2] / "Assets" / "Converted" / "Maps" / "object_animation.csv"
    out: dict[tuple[str, int], int] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines()[1:]:
            cols = line.split(",")
            if len(cols) >= 3 and cols[1].strip().isdigit():
                out[(cols[0].strip().upper(), int(cols[1]))] = int(cols[2])
    return out


ANIMATED_FRAMES = _load_animated_parts()


def part_animation_frames(part: dict) -> int:
    """Число кадров анимации части (0 = статика)."""
    return ANIMATED_FRAMES.get((part["icn"].upper(), part["index"]), 0)


def part_is_dynamic(part: dict) -> bool:
    if part["icn"].upper() in DYNAMIC_VISUAL_ICNS:
        return True
    return (part["icn"].upper(), part["index"]) in ANIMATED_FRAMES


def split_static_dynamic_parts(parts: list[dict]) -> tuple[list[dict], list[dict]]:
    static_parts = []
    dynamic_parts = []
    for part in parts:
        if part_is_dynamic(part):
            dynamic_parts.append(part)
        else:
            static_parts.append(part)
    return static_parts, dynamic_parts


def _objects_for_view(width, height, transfer_plan: ObjectTransferPlan, origin_x, origin_y, selector):
    objects = []
    start_x = max(0, origin_x - OBJECT_VIEW_MARGIN_TILES)
    start_y = max(0, origin_y - OBJECT_VIEW_MARGIN_TILES)
    end_x = min(width, origin_x + PACK_VIEW_W + OBJECT_VIEW_MARGIN_TILES)
    end_y = min(height, origin_y + PACK_VIEW_H + OBJECT_VIEW_MARGIN_TILES)
    for my in range(start_y, end_y):
        for mx in range(start_x, end_x):
            for part in selector(mx, my):
                obj = dict(part)
                obj["map_x"] = mx
                obj["map_y"] = my
                obj["tile_x"] = mx - origin_x
                obj["tile_y"] = my - origin_y
                objects.append(obj)
    return objects


def original_objects_for_view(width, height, transfer_plan: ObjectTransferPlan, origin_x, origin_y):
    # низ-динамика (level1, динамические ICN) — оверлей ДО актёра
    return _objects_for_view(width, height, transfer_plan, origin_x, origin_y, transfer_plan.dynamic_at)


def original_top_objects_for_view(width, height, transfer_plan: ObjectTransferPlan, origin_x, origin_y):
    # top-слой (level2) — оверлей ПОСЛЕ актёра (поверх героев), статика+динамика
    return _objects_for_view(width, height, transfer_plan, origin_x, origin_y, transfer_plan.top_at)


def build_object_atlas(agg_data, entries, palette, width, height, transfer_plan: ObjectTransferPlan):
    if FULLMAP_DXT:
        return b"", {}
    icn_cache = {}
    sprite_defs = {}
    max_x, max_y = pack_origin_max(width, height)
    for oy in range(max_y + 1):
        for ox in range(max_x + 1):
            view_objs = original_objects_for_view(width, height, transfer_plan, ox, oy)
            view_objs += original_top_objects_for_view(width, height, transfer_plan, ox, oy)
            for obj in view_objs:
                key = (obj["icn"], obj["index"])
                if key in sprite_defs:
                    continue
                if obj["icn"] not in icn_cache:
                    icn_cache[obj["icn"]] = read_icn(agg_entry(agg_data, entries, obj["icn"]))
                sprites = icn_cache[obj["icn"]]
                if obj["index"] >= len(sprites):
                    continue
                header, encoded = sprites[obj["index"]]
                if header["w"] == 0 or header["h"] == 0:
                    continue
                sprite_defs[key] = {
                    "raw": decode_icn_sprite(header, encoded, palette),
                    "w": header["w"],
                    "h": header["h"],
                    "ox": header["ox"],
                    "oy": header["oy"],
                }

    payload = bytearray(palette_argb4444(palette))
    payload.extend(palette_argb4444_opaque(palette))
    sprite_cache = {}
    for key, sprite in sorted(sprite_defs.items()):
        source = RAMG_OBJECT_BASE + align(len(payload), 4)
        while RAMG_OBJECT_BASE + len(payload) < source:
            payload.append(0)
        payload.extend(sprite["raw"])
        sprite_cache[key] = {
            "addr": source,
            "cell": 0,
            "w": sprite["w"],
            "h": sprite["h"],
            "ox": sprite["ox"],
            "oy": sprite["oy"],
            "fmt": FT_ARGB4,
            "stride": sprite["w"] * 2,
        }
    return bytes(payload), sprite_cache


def append_overlay_sprite(payload: bytearray, agg_data: bytes, entries, palette, icn_name: str, index: int):
    sprites = read_icn(agg_entry(agg_data, entries, icn_name))
    if index >= len(sprites):
        raise ValueError(f"{icn_name}: кадр {index} вне диапазона 0..{len(sprites) - 1}")
    header, encoded = sprites[index]
    addr = RAMG_OBJECT_BASE + align(len(payload), 4)
    while RAMG_OBJECT_BASE + len(payload) < addr:
        payload.append(0)
    payload.extend(decode_icn_sprite(header, encoded, palette))
    return {"addr": addr, "w": header["w"], "h": header["h"], "ox": header["ox"], "oy": header["oy"], "icn": icn_name, "index": index, "fmt": FT_ARGB4, "stride": header["w"] * 2}


# ---- Анимация adventure-объектов (костры/мельницы/лава/водяные колёса) ----
# fheroes2 (maps_tiles_render.cpp): анимир. часть рисует БАЗУ (icnIndex), затем
# текущий кадр (icnIndex + (globalCounter % N) + 1) ПОВЕРХ. Кадры — подряд
# icnIndex+1..icnIndex+N. Единый счётчик, шаг MAPS_DELAY=250мс. У нас база уже
# рисуется (запечена/оверлей), а кадр-дельту добавляет рантайм-проход.
# Вода (OBJNWATR/OBJNWAT2) исключена — её делает water palette-cycle (task #12).
ANIM_WATER_ICNS = {"OBJNWATR.ICN", "OBJNWAT2.ICN"}


def collect_map_anim_objects(transfer_plan: ObjectTransferPlan):
    """Анимир. не-водные части на карте (из dynamic/top оверлея плана) с абс.
    позицией tile_x/tile_y, базовым индексом и числом кадров N. Системно: список
    идёт из ANIMATED_FRAMES (object_animation.csv) — работает для любой карты."""
    seen = set()
    result = []
    for y in range(transfer_plan.height):
        for x in range(transfer_plan.width):
            for part in transfer_plan.dynamic_at(x, y) + transfer_plan.top_at(x, y):
                n = part_animation_frames(part)
                if not n:
                    continue
                if part["icn"].upper() in ANIM_WATER_ICNS:
                    continue
                key = (x, y, part["icn"].upper(), part["index"])
                if key in seen:
                    continue
                seen.add(key)
                result.append({"map_x": x, "map_y": y, "icn": part["icn"], "base": part["index"], "frames": n})
    return result


def pack_anim_frames(object_payload: bytearray, agg_data, entries, anim_objects):
    """Упаковывает кадры-дельты (PALETTED4444, 1Б/px, вдвое легче ARGB4) в
    object_payload. Возвращает (anim_table, skipped). anim_table: per-часть dict
    {map_x,map_y,frames:[{addr,w,h,ox,oy},...]}. Кадры дедуплицируются по
    (icn,frame_index). mono-кадры (тень) пропускаются — их база остаётся статичной."""
    icn_cache = {}
    frame_cache = {}   # (icn_upper, frame_index) -> {addr,w,h,ox,oy}
    anim_table = []
    skipped = []
    for obj in anim_objects:
        icn = obj["icn"]
        if icn not in icn_cache:
            icn_cache[icn] = read_icn(agg_entry(agg_data, entries, icn))
        sprites = icn_cache[icn]
        frames = []
        mono = False
        for k in range(1, obj["frames"] + 1):
            fidx = obj["base"] + k
            if fidx >= len(sprites):
                # Кадр вне диапазона ICN (битые/нестандартные данные на чужой карте):
                # не валим билд — пропускаем часть, её база остаётся статичной.
                mono = True
                break
            ckey = (icn.upper(), fidx)
            if ckey not in frame_cache:
                header, encoded = sprites[fidx]
                if header["w"] == 0 or header["h"] == 0:
                    mono = True
                    break
                idx_bytes, is_mono = decode_icn_paletted(header, encoded)
                if is_mono:
                    mono = True
                    break
                addr = RAMG_OBJECT_BASE + align(len(object_payload), 4)
                while RAMG_OBJECT_BASE + len(object_payload) < addr:
                    object_payload.append(0)
                object_payload.extend(idx_bytes)
                frame_cache[ckey] = {"addr": addr, "w": header["w"], "h": header["h"], "ox": header["ox"], "oy": header["oy"]}
            frames.append(frame_cache[ckey])
        if mono:
            skipped.append((icn, obj["base"]))
            continue
        anim_table.append({"map_x": obj["map_x"], "map_y": obj["map_y"], "frames": frames})
    return anim_table, skipped


def write_map_anim_inc(path: Path, anim_table):
    """generated_map_anim.inc: MapAnimTable для рантайм-прохода Render_MapAnimCmd.
    Per-часть: DEFB map_x,map_y,N; затем N×[SOURCE(4) LAYOUT(4) SIZE(4) ox(1) oy(1)].
    SOURCE/LAYOUT/SIZE — готовые FT812-dword'ы (те же c_* что и оверлей объектов →
    кодировка гарантированно совпадает). Рантайм копирует их + считает VERTEX2F."""
    def defb(data: bytes) -> str:
        return "                DEFB " + ", ".join(f"#{b:02X}" for b in data)

    lines = [
        "; Сгенерировано Source/Tools/viewport_pack.py — анимация adventure-объектов.",
        "; Кадры-дельты (PALETTED4444) поверх базы; формула fheroes2:",
        ";   frame = base + (MapAnimPhase % N) + 1; шаг ~250мс (MAPS_DELAY).",
        f"MAP_ANIM_COUNT          EQU {len(anim_table)}",
        "MAP_ANIM_PALETTE_RAMG   EQU OBJECT_PALETTE_RAMG",
        "MapAnimTable:",
    ]
    for e in anim_table:
        frames = e["frames"]
        lines.append(f"                DEFB {e['map_x']}, {e['map_y']}, {len(frames)}")
        for f in frames:
            sw = (f["w"] * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN
            sh = (f["h"] * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN
            lines.append(defb(c_bitmap_source(f["addr"])) + f"   ; SOURCE #{f['addr']:05X}")
            lines.append(defb(c_bitmap_layout(FT_PALETTED4444, f["w"], f["h"])) + f"   ; LAYOUT pal4444 {f['w']}x{f['h']}")
            lines.append(defb(c_bitmap_size(sw, sh)) + "   ; SIZE")
            lines.append(f"                DEFB {f['ox'] & 0xFF}, {f['oy'] & 0xFF}   ; ox,oy (signed)")
    lines.append("MAP_ANIM_ENTRY_HEADER   EQU 3")
    lines.append("MAP_ANIM_FRAME_SIZE     EQU 14")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def argb4_word_from_palette(palette, color_index: int, alpha: int = 15) -> int:
    r, g, b = palette[color_index]
    return ((alpha & 15) << 12) | ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4)


def argb4_bytes_to_words(raw: bytes) -> list[int]:
    return [raw[i] | (raw[i + 1] << 8) for i in range(0, len(raw), 2)]


def argb4_words_to_bytes(words: list[int]) -> bytes:
    out = bytearray()
    for value in words:
        out.extend((value & 0xFF, (value >> 8) & 0xFF))
    return bytes(out)


def blit_argb4_words(dst: list[int], dst_w: int, dst_h: int, src: list[int], src_w: int, src_h: int, dst_x: int, dst_y: int) -> None:
    for sy in range(src_h):
        y = dst_y + sy
        if y < 0 or y >= dst_h:
            continue
        for sx in range(src_w):
            x = dst_x + sx
            if x < 0 or x >= dst_w:
                continue
            pix = src[sy * src_w + sx]
            if pix & 0xF000:
                dst[y * dst_w + x] = pix


def cursor_digit_words(width: int, height: int, points: list[tuple[int, int]], palette) -> dict:
    digit_word = argb4_word_from_palette(palette, CURSOR_MOVE_DIGIT_COLOR)
    contour_word = argb4_word_from_palette(palette, CURSOR_MOVE_CONTOUR_COLOR)
    words = [0] * (width * height)
    point_set = set(points)
    for x, y in points:
        for cy in range(y - 1, y + 2):
            if cy < 0 or cy >= height:
                continue
            for cx in range(x - 1, x + 2):
                if cx < 0 or cx >= width or (cx, cy) in point_set:
                    continue
                words[cy * width + cx] = contour_word
    for x, y in points:
        if 0 <= x < width and 0 <= y < height:
            words[y * width + x] = digit_word
    return {"w": width, "h": height, "words": words}


def add_digit_words(original: dict, digit: dict, offset: tuple[int, int]) -> dict:
    out_w = original["w"] + digit["w"] + offset[0]
    out_h = original["h"] + (0 if offset[1] < 0 else offset[1])
    if out_w <= 0 or out_h <= 0:
        raise ValueError("cursor digit composition produced an empty image")
    out = [0] * (out_w * out_h)
    blit_argb4_words(out, out_w, out_h, original["words"], original["w"], original["h"], 0, 0)
    digit_x = original["w"] + offset[0]
    digit_y = out_h - digit["h"] + (0 if offset[1] >= 0 else offset[1])
    blit_argb4_words(out, out_w, out_h, digit["words"], digit["w"], digit["h"], digit_x, digit_y)
    return {"w": out_w, "h": out_h, "x": out_w - original["w"], "y": out_h - original["h"], "words": out}


def cursor_default_draw_offset(sprite: dict) -> tuple[int, int]:
    return -((sprite["w"] - sprite.get("x", 0)) // 2), -((sprite["h"] - sprite.get("y", 0)) // 2)


def append_argb4_sprite(payload: bytearray, raw: bytes, width: int, height: int, draw_ox: int, draw_oy: int, label: str, index: int, base: int = RAMG_OBJECT_BASE):
    addr = base + align(len(payload), 4)
    while base + len(payload) < addr:
        payload.append(0)
    payload.extend(raw)
    return {
        "addr": addr,
        "w": width,
        "h": height,
        "draw_ox": draw_ox,
        "draw_oy": draw_oy,
        "ox": draw_ox,
        "oy": draw_oy,
        "stride": width * 2,
        "scaled_w": (width * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN,
        "scaled_h": (height * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN,
        "icn": label,
        "index": index,
        "fmt": FT_ARGB4,
    }


def append_paletted_sprite(payload: bytearray, raw: bytes, width: int, height: int, label: str, index: int):
    addr = RAMG_OBJECT_BASE + align(len(payload), 4)
    while RAMG_OBJECT_BASE + len(payload) < addr:
        payload.append(0)
    payload.extend(raw)
    return {
        "addr": addr,
        "w": width,
        "h": height,
        "stride": width,
        "scaled_w": (width * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN,
        "scaled_h": (height * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN,
        "icn": label,
        "index": index,
        "fmt": FT_PALETTED4444,
    }


def append_rgb565_sprite(payload: bytearray, raw: bytes, width: int, height: int, label: str):
    addr = RAMG_OBJECT_BASE + align(len(payload), 4)
    while RAMG_OBJECT_BASE + len(payload) < addr:
        payload.append(0)
    payload.extend(raw)
    return {
        "addr": addr,
        "w": width,
        "h": height,
        "stride": width * 2,
        "scaled_w": (width * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN,
        "scaled_h": (height * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN,
        "icn": label,
        "index": 0,
        "fmt": FT_RGB565,
    }


def append_radar_paletted_sprite(payload: bytearray, indices: bytes, palette: bytes, width: int, height: int, label: str):
    """Кладёт в RAM_G индексы PALETTED4444 (1 байт/пиксель) + отдельную палитру."""
    addr = RAMG_OBJECT_BASE + align(len(payload), 4)
    while RAMG_OBJECT_BASE + len(payload) < addr:
        payload.append(0)
    payload.extend(indices)
    palette_addr = RAMG_OBJECT_BASE + align(len(payload), 4)
    while RAMG_OBJECT_BASE + len(payload) < palette_addr:
        payload.append(0)
    payload.extend(palette)
    return {
        "addr": addr,
        "palette_addr": palette_addr,
        "w": width,
        "h": height,
        "stride": width,
        "scaled_w": (width * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN,
        "scaled_h": (height * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN,
        "icn": label,
        "index": 0,
        "fmt": FT_PALETTED4444,
    }


def crop_indices(raw: bytes, src_w: int, sx: int, sy: int, w: int, h: int) -> bytes:
    out = bytearray()
    for row in range(h):
        start = (sy + row) * src_w + sx
        out.extend(raw[start:start + w])
    return bytes(out)


def split_ui_blits(blits: list[tuple[int, int, int, int, int, int]]) -> list[tuple[int, int, int, int, int, int]]:
    # Keep individual UI bitmaps comfortably under the FT812 low-size limit.
    max_logical_w = 319
    max_logical_h = 319
    out: list[tuple[int, int, int, int, int, int]] = []
    for sx, sy, w, h, dx, dy in blits:
        y = 0
        while y < h:
            part_h = min(max_logical_h, h - y)
            x = 0
            while x < w:
                part_w = min(max_logical_w, w - x)
                out.append((sx + x, sy + y, part_w, part_h, dx + x, dy + y))
                x += part_w
            y += part_h
    return out


def append_adventure_border_blits(
    payload: bytearray,
    raw: bytes,
    border_w: int,
    blits: list[tuple[int, int, int, int, int, int]],
):
    cache: dict[tuple[int, int, int, int], dict] = {}
    packed = []
    for sx, sy, w, h, dx, dy in split_ui_blits(blits):
        key = (sx, sy, w, h)
        sprite = cache.get(key)
        if sprite is None:
            sprite = append_paletted_sprite(payload, crop_indices(raw, border_w, sx, sy, w, h), w, h, "ADVBORD.ICN", 0)
            cache[key] = sprite
        packed.append({"sprite": sprite, "dx": dx, "dy": dy})
    return packed


def radar_ground_palette_index(terrain_image_index: int) -> int:
    # fheroes2 GetPaletteIndexFromGround (interface_radar.cpp): тип грунта по диапазону
    # индекса изображения GROUND32.TIL → фиксированный индекс палитры KB.PAL радара.
    timg = terrain_image_index
    if timg < 30:   return 0x4D   # WATER
    if timg < 92:   return 0x62   # GRASS
    if timg < 146:  return 0x0D   # SNOW
    if timg < 208:  return 0x68   # SWAMP
    if timg < 262:  return 0x20   # LAVA
    if timg < 321:  return 0x76   # DESERT
    if timg < 361:  return 0x36   # DIRT
    if timg < 415:  return 0xCE   # WASTELAND
    return 0x29                    # BEACH


def radar_tile_palette_index(tile) -> int:
    # fheroes2 Radar::RedrawObjects (грунтовая часть). Объекты-ориентиры (замки/шахты
    # цветом владельца, ресурсы серым) НЕ рисуем: сырой map_object содержит и декорации,
    # а цвет владельца требует парсинга списка замков — это отдельная задача. Здесь —
    # только грунт: дорога, тип грунта, и горы(100)/деревья(99) оттенком +3 (как оригинал).
    if tile["terrain_flags"] & 0x04:
        return 0x7A   # COLOR_ROAD
    ri = radar_ground_palette_index(tile["terrain"])
    if tile["map_object"] in (99, 100):   # OBJ_TREES, OBJ_MOUNTAINS
        ri += 3
    return ri


def build_radar_paletted4444(ground_tiles, palette, width: int, height: int, map_data):
    """Мини-карта в PALETTED4444. Цвета тайлов — ТОЧНО как fheroes2 radar
    (GetPaletteIndexFromGround, interface_radar.cpp): фиксированный индекс KB.PAL на
    ТИП ГРУНТА (а НЕ усреднение пикселей тайла), дорога = COLOR_ROAD 0x7A. Печётся
    ЧЁРНОЙ (как memset(radarImage, COLOR_BLACK)); рантайм раскрывает разведанное
    (Minimap_RevealTile из Fog_RevealHero), таблица tile_color_table — источник цвета.

    Возвращает (indices 144x144 (чёрные), palette_argb4 opaque, tile_color_table)."""
    tiles = map_data[0] if isinstance(map_data, tuple) else map_data

    # палитра мини-карты: индекс 0 = чёрный фон (туман); далее уникальные radar-цвета
    color_list = [(0, 0, 0)]
    color_index = {}

    def color_slot(pal_idx: int) -> int:
        rgb = tuple(palette[pal_idx])
        slot = color_index.get(rgb)
        if slot is None:
            slot = len(color_list)
            color_index[rgb] = slot
            color_list.append(rgb)
        return slot

    out = bytearray(UI_RADAR_SIZE * UI_RADAR_SIZE)  # 1 байт/пиксель, всё 0 = чёрный туман
    tile_color_table = bytearray(width * height)
    for my in range(height):
        for mx in range(width):
            tile = tiles[my * width + mx]
            tile_color_table[my * width + mx] = color_slot(radar_tile_palette_index(tile))
    if len(color_list) > 256:
        raise ValueError(f"мини-карте нужно >256 цветов палитры: {len(color_list)}")
    return bytes(out), palette_argb4444_opaque(color_list), bytes(tile_color_table)


def adventure_border_blits(border_w: int, border_h: int,
                           display_w: int = PANEL_DISPLAY_W,
                           display_h: int = PANEL_DISPLAY_H) -> list[tuple[int, int, int, int, int, int]]:
    # Faithful port of fheroes2 Interface::GameBorderRedraw(false), good interface.
    # Source ADVBORD = border_w x border_h (640x480); tiled to fill display_w x display_h.
    # For 1024x768 the paddings are all 0 (384 and 288 are multiples of 32) and iconsCount=8.
    blits: list[tuple[int, int, int, int, int, int]] = []

    def blit(sx: int, sy: int, w: int, h: int, dx: int, dy: int) -> None:
        if w > 0 and h > 0:
            blits.append((sx, sy, w, h, dx, dy))

    # Mirror of fheroes2 repeatPattern(): tile (inW x inH) over (outW x outH).
    def repeat(sx: int, sy: int, w: int, h: int, dx: int, dy: int, out_w: int, out_h: int) -> None:
        if w <= 0 or h <= 0 or out_w <= 0 or out_h <= 0:
            return
        count_x = out_w // w
        count_y = out_h // h
        rest_w = out_w % w
        rest_h = out_h % h
        for ry in range(count_y):
            for rx in range(count_x):
                blit(sx, sy, w, h, dx + rx * w, dy + ry * h)
            if rest_w:
                blit(sx, sy, rest_w, h, dx + out_w - rest_w, dy + ry * h)
        if rest_h:
            for rx in range(count_x):
                blit(sx, sy, w, rest_h, dx + rx * w, dy + out_h - rest_h)
            if rest_w:
                blit(sx, sy, rest_w, rest_h, dx + out_w - rest_w, dy + out_h - rest_h)

    border = BORDER_PX            # fheroes2::borderWidthPx
    radar = UI_RADAR_SIZE         # fheroes2::radarWidthPx (144)
    tile = 32                     # fheroes2::tileWidthPx
    icn_w = border_w              # icnadv.width()  (640)
    icn_h = border_h              # icnadv.height() (480)

    extra_w = display_w - 640     # DEFAULT_WIDTH
    extra_h = display_h - 480     # DEFAULT_HEIGHT
    top_repeat_count = extra_w // tile if extra_w > 0 else 0
    top_repeat_width = (top_repeat_count + 1) * tile
    vert_repeat_count = extra_h // tile if extra_h > 0 else 0
    icons_count = 8 if vert_repeat_count > 3 else (4 if vert_repeat_count < 3 else 7)
    vert_repeat_h = (vert_repeat_count + 1) * tile
    vert_top_h = (icons_count - 3) * tile
    vert_bottom_h = vert_repeat_h - vert_top_h
    top_pad = extra_w % tile
    top_pad_l = top_pad // 2
    top_pad_r = top_pad - top_pad_l
    bottom_tile_w = tile
    bottom_repeat_count = top_repeat_count
    bottom_repeat_width = (bottom_repeat_count + 1) * bottom_tile_w
    bottom_pad = extra_w % bottom_tile_w
    bottom_pad_l = bottom_pad // 2
    bottom_pad_r = bottom_pad - bottom_pad_l
    vert_pad_h = extra_h % tile

    # TOP BORDER
    sx = 0
    blit(0, 0, 193, border, 0, 0); sx = 193; dx = 193
    repeat(sx, 0, 6, border, dx, 0, 6 + top_pad_l, border); dx += 6 + top_pad_l; sx += 6
    blit(sx, 0, 24, border, dx, 0); dx += 24; sx += 24
    repeat(sx, 0, tile, border, dx, 0, top_repeat_width, border); dx += top_repeat_width; sx += tile
    blit(sx, 0, 25, border, dx, 0); dx += 25; sx += 25
    repeat(sx, 0, 6, border, dx, 0, 6 + top_pad_r, border); dx += 6 + top_pad_r; sx += 6
    blit(sx, 0, icn_w - sx, border, dx, 0)

    # LEFT BORDER
    sx = 0; sy = border; dy = border
    blit(sx, sy, border, 255 - border, 0, dy); sy += 255 - border; dy += 255 - border
    repeat(sx, sy, border, tile, 0, dy, border, vert_repeat_h); dy += vert_repeat_h; sy += tile
    blit(sx, sy, border, 125, 0, dy); sy += 125; dy += 125
    repeat(sx, sy, border, 4, 0, dy, border, 4 + vert_pad_h); dy += 4 + vert_pad_h; sy += 4
    blit(sx, sy, border, icn_h - border - sy, 0, dy)

    # MIDDLE BORDER (divider between map area and panel)
    sx = icn_w - radar - 2 * border; sy = border
    dx = display_w - radar - 2 * border; dy = border
    blit(sx, sy, border, 255 - border, dx, dy); sy += 255 - border; dy += 255 - border
    repeat(sx, sy, border, tile, dx, dy, border, vert_top_h); dy += vert_top_h; sy += tile
    blit(sx, sy, border, 50, dx, dy); dy += 50; sy += 50
    blit(sx, sy, border, tile, dx, dy); dy += tile
    repeat(sx, sy, border, tile, dx, dy, border, vert_bottom_h); dy += vert_bottom_h; sy += tile
    blit(sx, sy, border, 43, dx, dy); dy += 43; sy += 43
    repeat(sx, sy, border, 8, dx, dy, border, 8 + vert_pad_h); dy += 8 + vert_pad_h; sy += 8
    blit(sx, sy, border, icn_h - border - sy, dx, dy)

    # RIGHT BORDER
    sx = icn_w - border; sy = border
    dx = display_w - border; dy = border
    blit(sx, sy, border, 255 - border, dx, dy); sy += 255 - border; dy += 255 - border
    repeat(sx, sy, border, tile, dx, dy, border, vert_top_h); dy += vert_top_h; sy += tile
    blit(sx, sy, border, 50, dx, dy); dy += 50; sy += 50
    blit(sx, sy, border, tile, dx, dy); dy += tile
    repeat(sx, sy, border, tile, dx, dy, border, vert_bottom_h); dy += vert_bottom_h; sy += tile
    blit(sx, sy, border, 43, dx, dy); dy += 43; sy += 43
    repeat(sx, sy, border, 4, dx, dy, border, 4 + vert_pad_h); dy += 4 + vert_pad_h; sy += 4
    blit(sx, sy, border, icn_h - border - sy, dx, dy)

    # BOTTOM BORDER
    sx = 0; sy = icn_h - border
    dx = 0; dy = display_h - border
    blit(sx, sy, 193, border, dx, dy); dx += 193; sx += 193
    repeat(sx, sy, 6, border, dx, dy, 6 + bottom_pad_l, border); dx += 6 + bottom_pad_l; sx += 6
    blit(sx, sy, 24, border, dx, dy); dx += 24; sx += 24
    repeat(sx, sy, bottom_tile_w, border, dx, dy, bottom_repeat_width, border); dx += bottom_repeat_width; sx += bottom_tile_w
    blit(sx, sy, 25, border, dx, dy); dx += 25; sx += 25
    repeat(sx, sy, 6, border, dx, dy, 6 + bottom_pad_r, border); dx += 6 + bottom_pad_r; sx += 6
    blit(sx, sy, icn_w - sx, border, dx, dy)

    # ICON BORDER (horizontal separators below radar and below the icons column)
    sx = icn_w - radar - border
    blit(sx, radar + border, radar, border, display_w - radar - border, radar + border)
    blit(sx, radar + 2 * border + 4 * 32, radar, border, display_w - radar - border, radar + 2 * border + icons_count * 32)
    return blits


def adventure_icons_background_blits(border_w: int) -> list[tuple[int, int, int, int, int, int]]:
    # IconsBar::redrawBackground for heroes and castles columns.
    blits: list[tuple[int, int, int, int, int, int]] = []
    src_x = border_w - UI_RADAR_SIZE - 16
    src_y = UI_RADAR_SIZE + 32
    for dst_x in (480, 552):
        blits.append((src_x, src_y, 72, 32, dst_x, 176))
        blits.append((src_x, src_y + 32, 72, 32, dst_x, 208))
        blits.append((src_x, src_y + 32, 72, 32, dst_x, 240))
        blits.append((src_x, src_y + 96, 72, 32, dst_x, 272))
    return blits


def append_adventure_ui_sprites(payload: bytearray, agg_data: bytes, entries, palette, ground_tiles, width: int, height: int, map_data):
    border_sprites = read_icn(agg_entry(agg_data, entries, "ADVBORD.ICN"))
    border_header, border_encoded = border_sprites[0]
    border_raw = decode_icn_indices(border_header, border_encoded)
    border_w = border_header["w"]
    border_h = border_header["h"]
    background_rects = adventure_icons_background_blits(border_w)
    background_rects.append((UI_STATUS_X, UI_STATUS_Y, UI_STATUS_W, UI_STATUS_H, UI_STATUS_X, UI_STATUS_Y))
    background_blits = append_adventure_border_blits(payload, border_raw, border_w, background_rects)
    border_blits = append_adventure_border_blits(payload, border_raw, border_w, adventure_border_blits(border_w, border_h))

    button_icn = read_icn(agg_entry(agg_data, entries, "ADVBTNS.ICN"))
    buttons = []
    buttons_pressed = []
    for index in UI_BUTTON_INDICES:
        header, encoded = button_icn[index]
        buttons.append(append_paletted_sprite(payload, decode_icn_indices(header, encoded), header["w"], header["h"], "ADVBTNS.ICN", index))
        # pressed-кадр = released+1 (как в оригинале fheroes2: ADVBTNS released/pressed пара),
        # рисуется поверх нажатой кнопки пока ЛКМ зажата.
        ph, pe = button_icn[index + 1]
        buttons_pressed.append(append_paletted_sprite(payload, decode_icn_indices(ph, pe), ph["w"], ph["h"], "ADVBTNS.ICN", index + 1))

    # Цифры SMALFONT.ICN[16..25] = '0'..'9' (5×8). Рисуются НАТИВНО (без ×1.6 апскейла).
    # +2 пустые строки снизу (h 8→10): реальный FT812 поджимает низ мелкого глифа —
    # запас гарантирует, что нижние строки цифры не срежутся (snapshot этого не ловит).
    DIGIT_PAD_BOTTOM = 2
    smalfont = read_icn(agg_entry(agg_data, entries, "SMALFONT.ICN"))
    digits = []
    for ch in range(10):
        header, encoded = smalfont[16 + ch]
        w, h = header["w"], header["h"]
        idx = decode_icn_indices(header, encoded) + bytes(w * DIGIT_PAD_BOTTOM)
        digits.append(append_paletted_sprite(payload, idx, w, h + DIGIT_PAD_BOTTOM, "SMALFONT.ICN", 16 + ch))

    # Метки даты для DATE-вида статуса (текст SMALFONT, char index = ord-32; baseline по oy).
    def smalfont_label(text):
        gl = []
        for c in text:
            hd, enc = smalfont[ord(c) - 32]
            oy = hd.get("oy", hd.get("offset_y", 0))
            gl.append((hd["w"], hd["h"], oy, decode_icn_indices(hd, enc)))
        tw = sum(g[0] for g in gl) + max(0, len(gl) - 1)
        th = max((g[2] + g[1]) for g in gl) + DIGIT_PAD_BOTTOM
        buf = bytearray(tw * th)
        x = 0
        for gw, gh, oy, gidx in gl:
            for py in range(gh):
                for px in range(gw):
                    v = gidx[py * gw + px]
                    if v:
                        buf[(oy + py) * tw + x + px] = v
            x += gw + 1
        return bytes(buf), tw, th
    date_labels = {}
    for txt, key in (("Month:", "month"), ("Week:", "week"), ("Day:", "day")):
        b, lw, lh = smalfont_label(txt)
        date_labels[key] = append_paletted_sprite(payload, b, lw, lh, "LBL", 0)

    # Буфер в RAM_G под готовый DL ресурсной панели (CMD_APPEND каждый кадр; пересборка
    # при изменении ресурсов). Полная панель ~7 иконок + 7 чисел + дата ≤ 1 КБ.
    resource_panel_ramg = RAMG_OBJECT_BASE + align(len(payload), 4)
    while RAMG_OBJECT_BASE + len(payload) < resource_panel_ramg:
        payload.append(0)
    payload.extend(b"\0" * 1024)

    # Геройская панель справа: подложка, портреты, полоски маны и хода
    portxtra_icn = read_icn(agg_entry(agg_data, entries, "PORTXTRA.ICN"))
    header, encoded = portxtra_icn[0]
    portxtra = append_paletted_sprite(payload, decode_icn_indices(header, encoded), header["w"], header["h"], "PORTXTRA.ICN", 0)

    mobility_icn = read_icn(agg_entry(agg_data, entries, "MOBILITY.ICN"))
    mobility_frames = []
    max_mob_w = max(m[0]["w"] for m in mobility_icn)
    max_mob_h = max(m[0]["h"] for m in mobility_icn)
    for i in range(26):
        header, encoded = mobility_icn[i]
        pixels = decode_icn_indices(header, encoded)
        padded = bytearray(max_mob_w * max_mob_h) # 0 is transparent
        ox = header.get("ox", header.get("offset_x", 0))
        oy = header.get("oy", header.get("offset_y", 0))
        for py in range(header["h"]):
            for px in range(header["w"]):
                padded[(oy + py) * max_mob_w + (ox + px)] = pixels[py * header["w"] + px]
        mobility_frames.append(append_paletted_sprite(payload, padded, max_mob_w, max_mob_h, "MOBILITY.ICN", i))

    mana_icn = read_icn(agg_entry(agg_data, entries, "MANA.ICN"))
    mana_frames = []
    max_mana_w = max(m[0]["w"] for m in mana_icn)
    max_mana_h = max(m[0]["h"] for m in mana_icn)
    for i in range(26):
        header, encoded = mana_icn[i]
        pixels = decode_icn_indices(header, encoded)
        padded = bytearray(max_mana_w * max_mana_h)
        ox = header.get("ox", header.get("offset_x", 0))
        oy = header.get("oy", header.get("offset_y", 0))
        for py in range(header["h"]):
            for px in range(header["w"]):
                padded[(oy + py) * max_mana_w + (ox + px)] = pixels[py * header["w"] + px]
        mana_frames.append(append_paletted_sprite(payload, padded, max_mana_w, max_mana_h, "MANA.ICN", i))

    miniport_icn = read_icn(agg_entry(agg_data, entries, "MINIPORT.ICN"))
    miniport_frames = []
    for i in range(len(miniport_icn)):
        header, encoded = miniport_icn[i]
        miniport_frames.append(append_paletted_sprite(payload, decode_icn_indices(header, encoded), header["w"], header["h"], "MINIPORT.ICN", i))

    # Статус-окно (kingdom-вид): STONBACK = каменный фон 144×72, RESSMALL[0] = спрайт иконок
    # королевства (замок/город/золото + 7 ресурсов). Числа рисуются поверх (Render_ResourcePanelCmd).
    stonback_icn = read_icn(agg_entry(agg_data, entries, "STONBACK.ICN"))
    header, encoded = stonback_icn[0]
    stonback = append_paletted_sprite(payload, decode_icn_indices(header, encoded), header["w"], header["h"], "STONBACK.ICN", 0)
    ressmall_icn = read_icn(agg_entry(agg_data, entries, "RESSMALL.ICN"))
    header, encoded = ressmall_icn[0]
    ressmall = append_paletted_sprite(payload, decode_icn_indices(header, encoded), header["w"], header["h"], "RESSMALL.ICN", 0)
    # DATE-вид статус-окна: SUNMOON[0] = солнце (день). Фаза луны/недели — позже по дню.
    sunmoon_icn = read_icn(agg_entry(agg_data, entries, "SUNMOON.ICN"))
    header, encoded = sunmoon_icn[0]
    sunmoon = append_paletted_sprite(payload, decode_icn_indices(header, encoded), header["w"], header["h"], "SUNMOON.ICN", 0)
    # ARMY-вид статус-окна: армия стартового героя. SKIRMISH героев на карте НЕ содержит —
    # игрок стартует замком Рыцаря (24,13), движок выдаёт дефолтную армию класса (эталон
    # fheroes2 Army::Reset/getNumberOfMonstersInStartingArmy): Knight = Peasant(MONS32[0], 30-50)
    # + Archer(MONS32[1], 3-5). Счётчики у оригинала рандомные — берём представительные.
    # В RAM_G грузим ТОЛЬКО типы монстров этой армии (не весь MONS32), индекс = тип монстра.
    HERO_ARMY = [(0, 40), (1, 4)]  # (MONS32-индекс, кол-во)
    mons32_icn = read_icn(agg_entry(agg_data, entries, "MONS32.ICN"))
    MONS_W, MONS_H = 32, 32
    army_sprites = []
    for mons_idx, count in HERO_ARMY:
        hd, enc = mons32_icn[mons_idx]
        gidx = decode_icn_indices(hd, enc)
        ox = hd.get("ox", hd.get("offset_x", 0))
        oy = hd.get("oy", hd.get("offset_y", 0))
        buf = bytearray(MONS_W * MONS_H)
        for py in range(hd["h"]):
            yy = oy + py
            if 0 <= yy < MONS_H:
                for px in range(hd["w"]):
                    xx = ox + px
                    if 0 <= xx < MONS_W:
                        v = gidx[py * hd["w"] + px]
                        if v:
                            buf[yy * MONS_W + xx] = v
        spr = append_paletted_sprite(payload, bytes(buf), MONS_W, MONS_H, "MONS32.ICN", mons_idx)
        army_sprites.append((spr, count))

    radar_indices, radar_palette, radar_tile_colors = build_radar_paletted4444(ground_tiles, palette, width, height, map_data)
    radar = append_radar_paletted_sprite(payload, radar_indices, radar_palette, UI_RADAR_SIZE, UI_RADAR_SIZE, "RADAR_MINIMAP")
    radar["tile_px"] = UI_RADAR_SIZE // width  # px мини-карты на тайл карты
    radar["tile_colors"] = radar_tile_colors   # индекс цвета палитры на тайл (для рантайм-раскрытия тумана)
    radar["map_w"] = width
    radar["map_h"] = height
    return {"border_w": border_w, "border_h": border_h, "background_blits": background_blits, "border_blits": border_blits, "buttons": buttons, "buttons_pressed": buttons_pressed, "portxtra": portxtra, "mobility": mobility_frames, "mana": mana_frames, "miniport": miniport_frames, "radar": radar, "digits": digits, "resource_panel_ramg": resource_panel_ramg, "stonback": stonback, "ressmall": ressmall, "sunmoon": sunmoon, "date_labels": date_labels, "army_sprites": army_sprites}



def append_cursor_sprites(agg_data: bytes, entries, palette):
    # Курсор — ГЛОБАЛЬНЫЙ драйвер: спрайты в ОТДЕЛЬНОМ payload с базой CURSOR_RAMG_BASE
    # (постоянная зона RAM_G, не object atlas) — резидентны, доступны во всех сценах.
    # Возвращает (cursor_sprites, payload).
    payload = bytearray()
    sprites = read_icn(agg_entry(agg_data, entries, "ADVMCO.ICN"))
    if len(sprites) <= 4:
        raise ValueError("ADVMCO.ICN: missing adventure map cursor sprites")

    def original_sprite(index: int) -> dict:
        header, encoded = sprites[index]
        raw = decode_icn_sprite(header, encoded, palette)
        return {
            "raw": raw,
            "words": argb4_bytes_to_words(raw),
            "w": header["w"],
            "h": header["h"],
            "x": header["ox"],
            "y": header["oy"],
        }

    cursor_sprites = []
    pointer = original_sprite(0)
    cursor_sprites.append(append_argb4_sprite(payload, pointer["raw"], pointer["w"], pointer["h"], 0, 0, "ADVMCO.ICN", 0, base=CURSOR_RAMG_BASE))

    move = original_sprite(4)
    move_ox, move_oy = cursor_default_draw_offset(move)
    cursor_sprites.append(append_argb4_sprite(payload, move["raw"], move["w"], move["h"], move_ox, move_oy, "COLOR_CURSOR_ADVENTURE_MAP", 0, base=CURSOR_RAMG_BASE))

    digits = [cursor_digit_words(6, 7, points, palette) for points in CURSOR_DIGIT_POINTS]
    plus = cursor_digit_words(5, 5, CURSOR_PLUS_POINTS, palette)
    digits.append(add_digit_words(digits[-1], plus, (-1, -1)))

    for distance_index, digit in enumerate(digits, start=1):
        composed = add_digit_words(move, digit, CURSOR_MOVE_DIGIT_OFFSET)
        raw = argb4_words_to_bytes(composed["words"])
        draw_ox, draw_oy = cursor_default_draw_offset(composed)
        cursor_sprites.append(
            append_argb4_sprite(
                payload,
                raw,
                composed["w"],
                composed["h"],
                draw_ox,
                draw_oy,
                "COLOR_CURSOR_ADVENTURE_MAP",
                distance_index,
                base=CURSOR_RAMG_BASE,
            )
        )

    # ★FIGHT (ADVMCO[5], цифро-офсет (1,1)) и ACTION (ADVMCO[9], (−6,1)) серии с днями пути 1..8
    # (agg_image.cpp:3726/3735 populateCursorIcons) + статические HEROES=ADVMCO[2], CASTLE=ADVMCO[3]
    # (cursor.h: HEROES=0x1002, CASTLE=0x1003 → кадр ICN). Faithful GetCursorFocusHeroes.
    for base_frame, digit_ofs, tag in ((5, (1, 1), "FIGHT"), (9, (-6, 1), "ACTION")):
        base = original_sprite(base_frame)
        box, boy = cursor_default_draw_offset(base)
        cursor_sprites.append(append_argb4_sprite(payload, base["raw"], base["w"], base["h"],
                                                  box, boy, "ADVMCO.ICN", base_frame, base=CURSOR_RAMG_BASE))
        for digit in digits:
            composed = add_digit_words(base, digit, digit_ofs)
            raw = argb4_words_to_bytes(composed["words"])
            dox, doy = cursor_default_draw_offset(composed)
            cursor_sprites.append(append_argb4_sprite(payload, raw, composed["w"], composed["h"],
                                                      dox, doy, "COLOR_CURSOR_ADVENTURE_MAP",
                                                      base_frame * 100, base=CURSOR_RAMG_BASE))
    for st_frame in (2, 3):                              # HEROES, CASTLE
        s = original_sprite(st_frame)
        sox, soy = cursor_default_draw_offset(s)
        cursor_sprites.append(append_argb4_sprite(payload, s["raw"], s["w"], s["h"],
                                                  sox, soy, "ADVMCO.ICN", st_frame, base=CURSOR_RAMG_BASE))

    # Боевые курсоры (CMSECO.ICN = ICN::CURSOR в fheroes2): тема = младший байт enum Cursor (cursor.h).
    # ПОЛНЫЙ faithful-набор GetBattleCursor: NONE=0, MOVE=1, ARROW=3, INFO=5, POINTER=6 (вне поля/панель)
    # + 6 направленных МЕЧЕЙ (SWORD_TOPRIGHT=7, RIGHT=8, BOTTOMRIGHT=9, BOTTOMLEFT=0xA, LEFT=0xB,
    # TOPLEFT=0xC; TOP/BOTTOM только для wide-юнитов — не грузим). Порядок фиксирован для ASM
    # (CURSOR_BATTLE_BASE_INDEX + 0..10). Базовый индекс = len здесь (до scroll → их индекс цел).
    bcur = read_icn(agg_entry(agg_data, entries, "CMSECO.ICN"))
    for cf in (0, 1, 3, 5, 6, 7, 8, 9, 0xA, 0xB, 0xC):
        bh, be = bcur[cf]
        braw = decode_icn_sprite(bh, be, palette)
        bsp = {"w": bh["w"], "h": bh["h"], "x": bh.get("ox", 0), "y": bh.get("oy", 0)}
        box, boy = cursor_default_draw_offset(bsp)       # центрирующий hotspot (вместо top-left 0,0)
        cursor_sprites.append(append_argb4_sprite(payload, braw, bh["w"], bh["h"], box, boy, "CMSECO.ICN", cf, base=CURSOR_RAMG_BASE))

    # Scroll-курсоры краёв карты (ADVMCO кадры 0x20..0x27, порядок по enum fheroes2
    # Cursor::SCROLL_*): TOP, TOPRIGHT, RIGHT, BOTTOMRIGHT, BOTTOM, BOTTOMLEFT, LEFT,
    # TOPLEFT. Показываются, когда мышь в кромочной зоне экрана (как в оригинале).
    if len(sprites) <= 0x27:
        raise ValueError("ADVMCO.ICN: отсутствуют scroll-курсоры (кадры 0x20..0x27)")
    for frame in range(0x20, 0x28):
        s = original_sprite(frame)
        sox, soy = cursor_default_draw_offset(s)
        cursor_sprites.append(append_argb4_sprite(payload, s["raw"], s["w"], s["h"], sox, soy, "ADVMCO.ICN", frame, base=CURSOR_RAMG_BASE))
    return cursor_sprites, payload


def append_route_sprites(payload: bytearray, agg_data: bytes, entries, palette):
    sprites = read_icn(agg_entry(agg_data, entries, "ROUTE.ICN"))
    if len(sprites) < ROUTE_SPRITE_COUNT:
        raise ValueError(f"ROUTE.ICN: нужно минимум {ROUTE_SPRITE_COUNT} кадров, есть {len(sprites)}")
    route_sprites = []
    for index in range(ROUTE_SPRITE_COUNT):
        header, encoded = sprites[index]
        addr = RAMG_OBJECT_BASE + align(len(payload), 4)
        while RAMG_OBJECT_BASE + len(payload) < addr:
            payload.append(0)
        # PALETTED4444 (1 байт/px): вдвое легче ARGB4 И позволяет красить недостижимую
        # часть пути сменой палитры (fheroes2 ROUTERED = ROUTE с красной палитрой).
        idx_bytes, _mono = decode_icn_paletted(header, encoded)
        payload.extend(idx_bytes)
        route_sprites.append(
            {
                "addr": addr,
                "w": header["w"],
                "h": header["h"],
                "draw_ox": header["ox"] - 12,
                "draw_oy": header["oy"] + 2,
                "stride": header["w"],
                "scaled_w": (header["w"] * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN,
                "scaled_h": (header["h"] * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN,
            }
        )
    return route_sprites


def palette_argb4444_red(palette):
    """KB.PAL → красные оттенки (как fheroes2 PAL::RED): цвет с яркостью пикселя,
    но красный канал. index 0 — прозрачный. Для недостижимой части маршрута."""
    out = bytearray()
    for i, (r, g, b) in enumerate(palette):
        if i == OBJECT_TRANSPARENT_INDEX:
            out.extend((0, 0))
            continue
        lum = max(r, g, b)
        rr = min(255, lum)
        gg = bb = lum // 5
        value = (15 << 12) | ((rr >> 4) << 8) | ((gg >> 4) << 4) | (bb >> 4)
        out.extend((value & 0xFF, value >> 8))
    return bytes(out)


def route_table_payload(route_sprites) -> bytes:
    out = bytearray()
    for sprite in route_sprites:
        out.extend(
            (
                (sprite["addr"] >> 16) & 0xFF,
                sprite["addr"] & 0xFF,
                (sprite["addr"] >> 8) & 0xFF,
                sprite["h"],
                sprite["stride"],
                sprite["scaled_w"],
                sprite["scaled_h"],
                0,
            )
        )
        out.extend(struct.pack("<h", sprite["draw_ox"]))
        out.extend(struct.pack("<h", sprite["draw_oy"]))
    return bytes(out)


def write_route_table(path: Path, page: int, route_sprites):
    payload = route_table_payload(route_sprites)
    if len(payload) > PAGE_SIZE:
        raise ValueError(f"ROUTE table {len(payload)} > {PAGE_SIZE}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload + b"\0" * (PAGE_SIZE - len(payload)))
    return [(path, page, len(payload))]


def runtime_map_cells_payload(width: int, height: int, tiles, terrain_remap) -> bytes:
    out = bytearray()
    for my in range(height + 1):
        src_y = min(my, height - 1)
        for mx in range(width + 1):
            src_x = min(mx, width - 1)
            tile = tiles[src_y * width + src_x]
            if COMPOSITE_STATIC_TILEMAP:
                slot = composite_slot_for_tile(mx, my)
                handle, cell = slot // CELLS_PER_HANDLE, slot % CELLS_PER_HANDLE
            else:
                handle, cell = terrain_remap[(tile["terrain"], tile["terrain_flags"] & 3)]
            low = cell | ((handle & 1) << 7)
            high = (handle >> 1) & 15
            out.extend((low, high))
            out.extend(struct.pack("<HH", map_tile_vertex2f_units(mx), map_tile_vertex2f_units(my)))
    return bytes(out)


def write_runtime_map_cells(path: Path, page: int, width: int, height: int, tiles, terrain_remap):
    payload = runtime_map_cells_payload(width, height, tiles, terrain_remap)
    if len(payload) > PAGE_SIZE:
        raise ValueError(f"runtime map cells {len(payload)} > {PAGE_SIZE}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload + b"\0" * (PAGE_SIZE - len(payload)))
    return [(path, page, len(payload))]


def viewport_dl(width, height, map_data, transfer_plan: ObjectTransferPlan, origin_x, origin_y, terrain_remap, sprite_cache):
    tiles = map_data[0] if isinstance(map_data, tuple) else map_data
    out = bytearray()
    out.extend(c_clear_color_rgb(0, 0, 0))
    out.extend(c_clear(1, 1, 1))
    out.extend(c_color_rgb(255, 255, 255))
    out.extend(c_color_a(255))
    out.extend(c_blend_func(FT_ONE, FT_ZERO))
    used_handles = sorted({terrain_remap[(terrain, shape)][0] for _, _, terrain, shape in visible_cells(width, height, tiles, origin_x, origin_y)})
    for handle in used_handles:
        out.extend(c_bitmap_handle(handle))
        out.extend(c_bitmap_source(RAMG_TERRAIN_BASE + handle * CELLS_PER_HANDLE * 32 * 32 * 2))
        out.extend(c_bitmap_layout(FT_RGB565, 64, 32))
        out.extend(c_bitmap_size(32, 32, FT_REPEAT, FT_REPEAT))
    out.extend(c_begin(FT_BITMAPS))
    for x, y, terrain, shape in visible_cells(width, height, tiles, origin_x, origin_y):
        handle, cell = terrain_remap[(terrain, shape)]
        out.extend(c_vertex2ii(x * 32, y * 32, handle, cell))
    out.extend(c_end())

    objects = original_objects_for_view(width, height, transfer_plan, origin_x, origin_y)
    placements = []
    for obj in objects:
        if obj["tile_x"] >= VIEW_W or obj["tile_y"] >= VIEW_H:
            continue
        sprite = sprite_cache.get((obj["icn"], obj["index"]))
        if not sprite:
            continue
        placements.append(
            {
                **sprite,
                "x": obj["tile_x"] * 32 + sprite["ox"],
                "y": obj["tile_y"] * 32 + sprite["oy"],
            }
        )
    if placements:
        out.extend(c_color_rgb(255, 255, 255))
        out.extend(c_color_a(255))
        out.extend(c_blend_func(FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA))
        out.extend(c_bitmap_handle(2))
        out.extend(c_palette_source(RAMG_OBJECT_BASE))
        out.extend(c_cell(0))
        out.extend(c_begin(FT_BITMAPS))
        for item in placements:
            out.extend(c_bitmap_source(item["addr"]))
            out.extend(c_bitmap_layout(item.get("fmt", FT_ARGB4), item.get("stride", item["w"] * 2), item["h"]))
            out.extend(c_bitmap_size((item["w"] * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN, (item["h"] * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN))
            out.extend(c_bitmap_transform_a(DISPLAY_BITMAP_TRANSFORM))
            out.extend(c_bitmap_transform_e(DISPLAY_BITMAP_TRANSFORM))
            out.extend(c_vertex2f(map_vertex2f_units(item["x"]), map_vertex2f_units(item["y"])))
        out.extend(c_end())
        out.extend(c_blend_func(FT_ONE, FT_ZERO))

    if len(out) > VIEWPORT_DL_SIZE:
        raise ValueError(f"viewport DL {origin_x},{origin_y}: {len(out)} > {VIEWPORT_DL_SIZE}")
    out.extend(c_display())
    while len(out) < VIEWPORT_DL_SIZE:
        out.extend(c_nop())
    return bytes(out)


def _build_objects_dl(objects, origin_x, origin_y, sprite_cache, label):
    out = bytearray()
    origin_base_x = map_tile_vertex2f_units(origin_x)
    origin_base_y = map_tile_vertex2f_units(origin_y)
    groups = {}
    for obj in objects:
        sprite = sprite_cache.get((obj["icn"], obj["index"]))
        if not sprite:
            continue
        x = obj["tile_x"] * 32 + sprite["ox"]
        y = obj["tile_y"] * 32 + sprite["oy"]
        if x + sprite["w"] <= 0 or y + sprite["h"] <= 0:
            continue
        if x >= VIEW_W * TILE_PX + TILE_PX or y >= VIEW_H * TILE_PX + TILE_PX:
            continue
        world_x = obj["map_x"] * TILE_PX + sprite["ox"]
        world_y = obj["map_y"] * TILE_PX + sprite["oy"]
        view_x = map_vertex2f_units(world_x) - origin_base_x
        view_y = map_vertex2f_units(world_y) - origin_base_y
        key = (sprite["addr"], sprite.get("fmt", FT_ARGB4), sprite.get("stride", sprite["w"] * 2), sprite["h"])
        groups.setdefault(key, []).append((sprite.get("cell", 0), sprite["w"], view_x, view_y))
    if groups:
        out.extend(c_color_rgb(255, 255, 255))
        out.extend(c_color_a(255))
        out.extend(c_blend_func(FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA))
        out.extend(c_bitmap_handle(2))
        out.extend(c_cell(0))
        out.extend(c_bitmap_transform_a(DISPLAY_BITMAP_TRANSFORM))
        out.extend(c_bitmap_transform_e(DISPLAY_BITMAP_TRANSFORM))
        out.extend(c_begin(FT_BITMAPS))
        last_size = None
        last_cell = 0
        for addr, fmt, stride, h in sorted(groups):
            out.extend(c_bitmap_source(addr))
            out.extend(c_bitmap_layout(fmt, stride, h))
            for cell, w, x, y in sorted(groups[(addr, fmt, stride, h)]):
                size_state = (w, h)
                if size_state != last_size:
                    out.extend(c_bitmap_size((w * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN, (h * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN))
                    last_size = size_state
                if cell != last_cell:
                    out.extend(c_cell(cell))
                    last_cell = cell
                out.extend(c_vertex2f(x, y))
        out.extend(c_end())
        out.extend(c_blend_func(FT_ONE, FT_ZERO))
    if len(out) + 4 > OBJECT_VIEW_DL_SIZE:
        raise ValueError(f"{label} DL {origin_x},{origin_y}: {len(out) + 4} > {OBJECT_VIEW_DL_SIZE}")
    out.extend(c_display())
    return bytes(out)


def object_view_dl(width, height, transfer_plan: ObjectTransferPlan, origin_x, origin_y, sprite_cache):
    # низ-оверлей (level1-динамика), CMD_APPEND ДО актёра
    objects = original_objects_for_view(width, height, transfer_plan, origin_x, origin_y)
    return _build_objects_dl(objects, origin_x, origin_y, sprite_cache, "object view")


def top_object_view_dl(width, height, transfer_plan: ObjectTransferPlan, origin_x, origin_y, sprite_cache):
    # top-оверлей (level2), CMD_APPEND ПОСЛЕ актёра (поверх героев)
    objects = original_top_objects_for_view(width, height, transfer_plan, origin_x, origin_y)
    return _build_objects_dl(objects, origin_x, origin_y, sprite_cache, "top object view")


def write_terrain_inc(path: Path, terrain_chunks, object_chunks, viewport_chunks, width: int, height: int, object_view_page_base: int):
    max_x, max_y = pack_origin_max(width, height)
    pixel_max_x = width * TILE_PX - VIEW_W * TILE_PX if RUNTIME_TILEMAP_RENDER else max_x * TILE_PX
    pixel_max_y = height * TILE_PX - VIEW_H * TILE_PX if RUNTIME_TILEMAP_RENDER else max_y * TILE_PX
    lines = [
        "; Сгенерировано Source/Tools/viewport_pack.py",
        "",
        "VIEWPORT_DL_PACK       EQU 1",
        f"RUNTIME_TILEMAP_RENDER EQU {1 if RUNTIME_TILEMAP_RENDER else 0}",
        f"COMPOSITE_STATIC_TILEMAP EQU {1 if COMPOSITE_STATIC_TILEMAP else 0}",
        f"VIEWPORT_ORIGIN_MAX_X  EQU {max_x}",
        f"VIEWPORT_ORIGIN_MAX_Y  EQU {max_y}",
        f"VIEWPORT_ORIGIN_COUNT_X EQU {max_x + 1}",
        f"VIEWPORT_ORIGIN_COUNT_Y EQU {max_y + 1}",
        f"VIEWPORT_PIXEL_MAX_X   EQU {pixel_max_x}",
        f"VIEWPORT_PIXEL_MAX_Y   EQU {pixel_max_y}",
        f"GAME_VIEW_X            EQU {GAME_VIEW_X}",
        f"GAME_VIEW_Y            EQU {GAME_VIEW_Y}",
        f"GAME_VIEW_W            EQU {GAME_VIEW_W}",
        f"GAME_VIEW_H            EQU {GAME_VIEW_H}",
        f"GAME_VIEW_TILE_W       EQU {VIEW_W}",
        f"GAME_VIEW_TILE_H       EQU {VIEW_H}",
        f"GAME_VIEW_X16          EQU {scaled_vertex2f_units(GAME_VIEW_X)}",
        f"GAME_VIEW_Y16          EQU {scaled_vertex2f_units(GAME_VIEW_Y)}",
        f"GAME_VIEW_CURSOR_MAX_X EQU {GAME_VIEW_X + GAME_VIEW_W - 1}",
        f"GAME_VIEW_CURSOR_MAX_Y EQU {GAME_VIEW_Y + GAME_VIEW_H - 1}",
        f"GAME_VIEW_SCREEN_X     EQU {scaled_screen_pixels(GAME_VIEW_X)}",
        f"GAME_VIEW_SCREEN_Y     EQU {scaled_screen_pixels(GAME_VIEW_Y)}",
        f"GAME_VIEW_SCREEN_W     EQU {scaled_screen_pixels(GAME_VIEW_W)}",
        f"GAME_VIEW_SCREEN_H     EQU {scaled_screen_pixels(GAME_VIEW_H)}",
        f"VIEWPORT_DL_SIZE       EQU {VIEWPORT_DL_SIZE}",
        f"VIEWPORT_DL_PAGE_BASE  EQU #{VIEWPORT_PAGE_BASE:02X}",
        f"OBJECT_VIEW_DL_SIZE    EQU {OBJECT_VIEW_DL_SIZE}",
        f"OBJECT_VIEW_DL_PAGE_BASE EQU #{object_view_page_base:02X}",
        f"TERRAIN_ATLAS_RAMG      EQU #{RAMG_TERRAIN_BASE:06X}",
        f"TERRAIN_ATLAS_PAGE_BASE EQU #{TERRAIN_PAGE_BASE:02X}",
        f"TERRAIN_ATLAS_PAGE_COUNT EQU {len(terrain_chunks)}",
        f"TERRAIN_ATLAS_SIZE      EQU {COMPOSITE_RAMG_CACHE_SIZE if COMPOSITE_STATIC_TILEMAP else sum(size for _, _, size in terrain_chunks)}",
        "TERRAIN_TILE_W          EQU 32",
        "TERRAIN_TILE_H          EQU 32",
        f"TERRAIN_TILE_STRIDE     EQU {TILE_PX if COMPOSITE_BG_PALETTED4444 else TILE_PX * 2}",
        "",
        "Terrain_Upload:",
        "                GetPage3",
        "                LD   (.RestorePage), A",
    ]
    if COMPOSITE_STATIC_TILEMAP:
        lines.extend(["                JR   .RestorePage", ""])
    ramg = RAMG_TERRAIN_BASE
    if not COMPOSITE_STATIC_TILEMAP:
        for _, page, real_size in terrain_chunks:
            lines.extend(
                [
                    f"                SetPage3 #{page:02X}",
                    "                LD   HL, #C000",
                    f"                LD   A, #{(ramg >> 16) & 0xFF:02X}",
                    f"                LD   DE, #{ramg & 0xFFFF:04X}",
                    f"                LD   BC, {real_size}",
                    "                CALL FT.WriteMem",
                ]
            )
            ramg += real_size
    lines.extend([".RestorePage    EQU $+1", "                LD   A, #00", "                SetPage3_A", "                RET", ""])
    lines.extend(["ViewportDL_Table:"])
    for _, page, _ in viewport_chunks:
        # One table entry per 4K viewport DL, four entries per 16K page.
        pass
    count = (max_x + 1) * (max_y + 1)
    for i in range(count):
        page = VIEWPORT_PAGE_BASE + (i * VIEWPORT_DL_SIZE) // PAGE_SIZE
        off = (i * VIEWPORT_DL_SIZE) % PAGE_SIZE
        lines.append(f"                DEFB #{page:02X}")
        lines.append(f"                DEFW #{off:04X}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


WATER_CYCLE_INDEX = 231   # палитровый диапазон анимированной воды HMM2 (подтверждён трейсом RAM_G)
WATER_CYCLE_COUNT = 7


def write_runtime_map_inc(path: Path, width: int, height: int, tiles, terrain_remap, object_view_page_base: int, runtime_map_cells_page: int, object_view_entries=None, composite_upload_entries=None, palette=None):
    lines = [
        "; Сгенерировано Source/Tools/viewport_pack.py",
        "",
        "RUNTIME_DL_BUFFER       EQU CMD_ADDRESS_PTR",
        f"RUNTIME_VIEW_W          EQU {PACK_VIEW_W}",
        f"RUNTIME_VIEW_H          EQU {PACK_VIEW_H}",
        "RUNTIME_TILE_COUNT      EQU RUNTIME_VIEW_W * RUNTIME_VIEW_H",
        "",
        "RuntimeDL_Header:",
        "                FT_CLEAR_COLOR_RGB 0, 0, 0",
        "                FT_CLEAR 1, 1, 1",
        "                FT_SCISSOR_XY GAME_VIEW_SCREEN_X, GAME_VIEW_SCREEN_Y",
        "                FT_SCISSOR_SIZE GAME_VIEW_SCREEN_W, GAME_VIEW_SCREEN_H",
        "RuntimeDL_TranslateX:",
        "RuntimeDL_TranslateX_Low:",
        "                DEFW 0",
        "RuntimeDL_TranslateX_High:",
        "                DEFW #2B00",
        "RuntimeDL_TranslateY:",
        "RuntimeDL_TranslateY_Low:",
        "                DEFW 0",
        "RuntimeDL_TranslateY_High:",
        "                DEFW #2C00",
    ]
    handle_count = math.ceil(COMPOSITE_SLOT_COUNT / CELLS_PER_HANDLE) if COMPOSITE_STATIC_TILEMAP else max(handle for handle, _ in terrain_remap.values()) + 1

    def terrain_source_patch_lines() -> list[str]:
        out = ["", "RuntimeDL_UpdateTerrainSources:"]
        if not COMPOSITE_STATIC_TILEMAP:
            out.append("                RET")
            return out
        out.extend(
            [
                "                LD   A, (CompositeDrawBank)",
                "                OR   A",
                "                JR   Z, .bank0",
                ".bank1:",
            ]
        )
        for patch_handle in range(handle_count):
            palette_addr = RAMG_TERRAIN_BASE + COMPOSITE_TILE_CACHE_SIZE
            bitmap_addr = COMPOSITE_BG_TILE_BASE + COMPOSITE_TILE_CACHE_SIZE + patch_handle * CELLS_PER_HANDLE * COMPOSITE_TILE_BYTES
            if COMPOSITE_BG_PALETTED4444:
                out.extend(
                    [
                        f"                LD   HL, #{palette_addr & 0xFFFF:04X}",
                        f"                LD   (RuntimeDL_Handle{patch_handle}_PaletteSource), HL",
                        f"                LD   A, #{(palette_addr >> 16) & 0xFF:02X}",
                        f"                LD   (RuntimeDL_Handle{patch_handle}_PaletteSource + 2), A",
                    ]
                )
            out.extend(
                [
                    f"                LD   HL, #{bitmap_addr & 0xFFFF:04X}",
                    f"                LD   (RuntimeDL_Handle{patch_handle}_BitmapSource), HL",
                    f"                LD   A, #{(bitmap_addr >> 16) & 0xFF:02X}",
                    f"                LD   (RuntimeDL_Handle{patch_handle}_BitmapSource + 2), A",
                ]
            )
        out.extend(["                RET", ".bank0:"])
        for patch_handle in range(handle_count):
            palette_addr = RAMG_TERRAIN_BASE
            bitmap_addr = COMPOSITE_BG_TILE_BASE + patch_handle * CELLS_PER_HANDLE * COMPOSITE_TILE_BYTES
            if COMPOSITE_BG_PALETTED4444:
                out.extend(
                    [
                        f"                LD   HL, #{palette_addr & 0xFFFF:04X}",
                        f"                LD   (RuntimeDL_Handle{patch_handle}_PaletteSource), HL",
                        f"                LD   A, #{(palette_addr >> 16) & 0xFF:02X}",
                        f"                LD   (RuntimeDL_Handle{patch_handle}_PaletteSource + 2), A",
                    ]
                )
            out.extend(
                [
                    f"                LD   HL, #{bitmap_addr & 0xFFFF:04X}",
                    f"                LD   (RuntimeDL_Handle{patch_handle}_BitmapSource), HL",
                    f"                LD   A, #{(bitmap_addr >> 16) & 0xFF:02X}",
                    f"                LD   (RuntimeDL_Handle{patch_handle}_BitmapSource + 2), A",
                ]
            )
        out.append("                RET")
        return out

    for handle in range(handle_count):
        source = (COMPOSITE_BG_TILE_BASE + handle * CELLS_PER_HANDLE * COMPOSITE_TILE_BYTES) if COMPOSITE_STATIC_TILEMAP else (RAMG_TERRAIN_BASE + handle * CELLS_PER_HANDLE * COMPOSITE_TILE_BYTES)
        lines.extend(
            [
                f"                FT_BITMAP_HANDLE {handle}",
                f"RuntimeDL_Handle{handle}_PaletteSource:" if COMPOSITE_BG_PALETTED4444 else None,
                f"                FT_PALETTE_SOURCE #{RAMG_TERRAIN_BASE:06X}" if COMPOSITE_BG_PALETTED4444 else None,
                f"RuntimeDL_Handle{handle}_BitmapSource:",
                f"                FT_BITMAP_SOURCE #{source:06X}",
                f"                FT_BITMAP_LAYOUT {'FT_PALETTED4444' if COMPOSITE_BG_PALETTED4444 else 'FT_RGB565'}, {TILE_PX if COMPOSITE_BG_PALETTED4444 else TILE_PX * 2}, 32",
                f"                FT_BITMAP_SIZE FT_NEAREST, FT_REPEAT, FT_REPEAT, {DISPLAY_TILE_PX}, {DISPLAY_TILE_PX}",
                f"                FT_BITMAP_TRANSFORM_A {DISPLAY_BITMAP_TRANSFORM}",
                f"                FT_BITMAP_TRANSFORM_E {DISPLAY_BITMAP_TRANSFORM}",
            ]
        )
        lines = [line for line in lines if line is not None]
    lines.extend(
        [
            "",
            "                FT_BEGIN FT_BITMAPS",
            "RuntimeDL_Header_SIZE EQU $ - RuntimeDL_Header",
            *terrain_source_patch_lines(),
            "",
            "RuntimeDL_RightBand:",
            "                FT_END",
            "RuntimeDL_TranslateXRight:",
            "RuntimeDL_TranslateXRight_Low:",
            f"                DEFW {tile_vertex2f_units(RUNTIME_SPLIT_X)}",
            "RuntimeDL_TranslateXRight_High:",
            "                DEFW #2B00",
            "                FT_BEGIN FT_BITMAPS",
            "RuntimeDL_RightBand_SIZE EQU $ - RuntimeDL_RightBand",
            "",
            "RuntimeDL_Tail:",
            "                FT_END",
            "                FT_DISPLAY",
            "RuntimeDL_Tail_SIZE EQU $ - RuntimeDL_Tail",
            "",
            "RuntimeDL_ObjectTranslate:",
            "RuntimeDL_ObjectTranslateX_Low:",
            "                DEFW 0",
            "RuntimeDL_ObjectTranslateX_High:",
            "                DEFW #2B00",
            "RuntimeDL_ObjectTranslateY_Low:",
            "                DEFW 0",
            "RuntimeDL_ObjectTranslateY_High:",
            "                DEFW #2C00",
            "RuntimeDL_ObjectTranslate_SIZE EQU $ - RuntimeDL_ObjectTranslate",
            f"MAP_TERRAIN_CELL_STRIDE EQU {width + 1}",
            f"RUNTIME_LEFT_VIEW_W EQU {RUNTIME_SPLIT_X}",
            "RUNTIME_RIGHT_VIEW_W EQU RUNTIME_VIEW_W - RUNTIME_LEFT_VIEW_W",
            f"RUNTIME_LEFT_SCREEN_X16 EQU {tile_vertex2f_units(RUNTIME_SPLIT_X)}",
            f"RUNTIME_TILE_DL_BYTES EQU {3 * 4}",
            f"MAP_TERRAIN_CELL_ENTRY_SIZE EQU {2 + 4}",
            f"RUNTIME_LEFT_DL_BYTES EQU {RUNTIME_SPLIT_X * PACK_VIEW_H * 3 * 4}",
            f"RUNTIME_RIGHT_DL_BYTES EQU {(PACK_VIEW_W - RUNTIME_SPLIT_X) * PACK_VIEW_H * 3 * 4}",
            "RUNTIME_BASE_DL_SIZE EQU RuntimeDL_Header_SIZE + RUNTIME_LEFT_DL_BYTES + RuntimeDL_RightBand_SIZE + RUNTIME_RIGHT_DL_BYTES + RuntimeDL_Tail_SIZE",
            "RUNTIME_OBJECT_DL_SIZE EQU RUNTIME_BASE_DL_SIZE + RuntimeDL_ObjectTranslate_SIZE + OBJECT_VIEW_DL_SIZE - 4",
            f"COMPOSITE_UPLOAD_PAGE_BASE EQU #{COMPOSITE_UPLOAD_PAGE_BASE:02X}",
            f"COMPOSITE_UPLOAD_CELL_PAGE EQU #{COMPOSITE_UPLOAD_PAGE_BASE:02X}",
            f"COMPOSITE_UPLOAD_STRIDE EQU {width + 1}",
            f"COMPOSITE_UPLOAD_HEIGHT EQU {height + 1}",
            f"COMPOSITE_UPLOAD_ENTRY_SIZE EQU {(width + 1) * (height + 1) * 6}",
            f"COMPOSITE_TILE_BYTES EQU {COMPOSITE_TILE_BYTES}",
            f"COMPOSITE_BG_PALETTE_SIZE EQU {COMPOSITE_BG_PALETTE_SIZE if COMPOSITE_BG_PALETTED4444 else 0}",
            f"COMPOSITE_BG_TILE_BASE EQU #{COMPOSITE_BG_TILE_BASE:06X}",
            f"COMPOSITE_BG_PALETTED4444 EQU {1 if COMPOSITE_BG_PALETTED4444 else 0}",
            f"COMPOSITE_CACHE_BANKS EQU {COMPOSITE_CACHE_BANKS}",
            f"COMPOSITE_CACHE_BANK_SIZE EQU {COMPOSITE_TILE_CACHE_SIZE}",
            f"COMPOSITE_CACHE_BANK1_RAMG EQU #{(RAMG_TERRAIN_BASE + COMPOSITE_TILE_CACHE_SIZE):06X}",
            f"MAP_TERRAIN_CELLS_PAGE EQU #{runtime_map_cells_page:02X}",
            "MAP_TERRAIN_CELLS_ADDR EQU #0000",
            # Stride объектной таблицы = число origin по X (max_x+1). Рантайм
            # (Render_ObjectViewTableEntry) ОБЯЗАН индексировать с этим stride;
            # раньше там был зашит ×17, а таблица упакована со stride (max_x+1)=23
            # → при originY>0 грузился чужой пакет (спрайты «в воде/где попало»).
            f"OBJECT_VIEW_STRIDE EQU {pack_origin_max(width, height)[0] + 1}",
            "OBJECT_VIEW_ENTRY_SIZE EQU 7",   # page(1)+off(2)+bottom_size(2)+top_size(2)
            f"WATER_CYCLE_INDEX EQU {WATER_CYCLE_INDEX}",
            f"WATER_CYCLE_COUNT EQU {WATER_CYCLE_COUNT}",
            f"WATER_CYCLE_BANK0_RAMG EQU #{(RAMG_TERRAIN_BASE + WATER_CYCLE_INDEX * 2):06X}",
            f"WATER_CYCLE_BANK1_RAMG EQU #{(RAMG_TERRAIN_BASE + COMPOSITE_TILE_CACHE_SIZE + WATER_CYCLE_INDEX * 2):06X}",
            "WaterCycleOriginal:",
            "                DEFW " + ", ".join(
                f"#{((15 << 12) | ((palette[WATER_CYCLE_INDEX + k][0] >> 4) << 8) | ((palette[WATER_CYCLE_INDEX + k][1] >> 4) << 4) | (palette[WATER_CYCLE_INDEX + k][2] >> 4)):04X}"
                for k in range(WATER_CYCLE_COUNT)
            ) if palette is not None else "                DEFW 0, 0, 0, 0, 0, 0, 0",
            "",
            "ObjectViewDL_Table:",
        ]
    )
    max_x, max_y = pack_origin_max(width, height)
    count = (max_x + 1) * (max_y + 1)
    # Запись 7 байт: page(1), off(2), bottom_size(2), top_size(2).
    # bottom — CMD_APPEND до актёра; top — CMD_APPEND после (z-слои).
    for i in range(count):
        if object_view_entries is None:
            page = object_view_page_base + (i * OBJECT_VIEW_DL_SIZE) // PAGE_SIZE
            off = (i * OBJECT_VIEW_DL_SIZE) % PAGE_SIZE
            bottom_size = OBJECT_VIEW_DL_SIZE - 4
            top_size = 0
        else:
            page, off, bottom_size, top_size = object_view_entries[i]
        lines.append(f"                DEFB #{page:02X}")
        lines.append(f"                DEFW #{off:04X}")
        lines.append(f"                DEFW {bottom_size}")
        lines.append(f"                DEFW {top_size}")

    # Подбираемые объекты (ресурсы): список (tile_x, tile_y, resource_idx). Извлекаем
    # как fheroes2: OBJ_RESOURCE + OBJNRSRC sprite (bottom_icn) → тип (sprite 1→WOOD..
    # 13→GOLD, idx=(sprite-1)//2 = RESOURCE.ICN index). qty в mp2 = 0 → среднее по типу.
    pickups = []
    for py in range(height):
        for px in range(width):
            t = tiles[py * width + px]
            if t["map_object"] == 155 and (t["object_name1"] >> 2) == 46:
                sprite = t["bottom_icn"]
                if 1 <= sprite <= 13 and sprite % 2 == 1:
                    pickups.append((px, py, (sprite - 1) // 2))
    lines.append("")
    lines.append(f"PICKUP_COUNT            EQU {len(pickups)}")
    lines.append("PickupList:")
    for px, py, idx in pickups:
        lines.append(f"                DEFB {px}, {py}, {idx}")
    if not pickups:
        lines.append("                DEFB 0")
    lines.append("PickupAmounts:          DEFW 7, 4, 7, 4, 4, 4, 700")  # wood,merc,ore,sulf,crys,gems,gold
    lines.append("")

    if composite_upload_entries is not None:
        lines.extend(
            [
                "",
                "CompositeBank_SelectNext:",
                "                LD   A, (CompositeDrawBank)",
                "                XOR  1",
                "                LD   (CompositeDrawBank), A",
                "                OR   A",
                "                JR   Z, .bank0",
                f"                LD   HL, #{COMPOSITE_TILE_CACHE_SIZE & 0xFFFF:04X}",
                "                LD   (CompositeUploadOffsetLow), HL",
                f"                LD   A, #{(COMPOSITE_TILE_CACHE_SIZE >> 16) & 0xFF:02X}",
                "                LD   (CompositeUploadOffsetHigh), A",
                "                RET",
                ".bank0:        LD   HL, #0000",
                "                LD   (CompositeUploadOffsetLow), HL",
                "                XOR  A",
                "                LD   (CompositeUploadOffsetHigh), A",
                "                RET",
                "",
                "CompositeUpload_AddBankOffset:",
                "                PUSH HL",
                "                LD   L, E",
                "                LD   H, D",
                "                LD   BC, (CompositeUploadOffsetLow)",
                "                ADD  HL, BC",
                "                EX   DE, HL",
                "                LD   B, A",
                "                LD   A, (CompositeUploadOffsetHigh)",
                "                ADC  A, B",
                "                POP  HL",
                "                RET",
                "",
                "CompositeTiles_UploadForScroll:",
                "                CALL CompositeBank_SelectNext",
                "                JP   CompositeTiles_UploadFull",
                "                LD   A, (RuntimeLastOriginX)",
                "                CP   #FF",
                "                JP   Z, CompositeTiles_UploadFull",
                "                LD   A, (ViewportOriginY)",
                "                LD   B, A",
                "                LD   A, (RuntimeLastOriginY)",
                "                CP   B",
                "                JR   NZ, CompositeUpload_CheckY",
                "                LD   A, (ViewportOriginX)",
                "                LD   B, A",
                "                LD   A, (RuntimeLastOriginX)",
                "                CP   B",
                "                RET  Z",
                "                INC  A",
                "                CP   B",
                "                JP   Z, CompositeTiles_UploadRight",
                "                LD   A, (ViewportOriginX)",
                "                INC  A",
                "                LD   B, A",
                "                LD   A, (RuntimeLastOriginX)",
                "                CP   B",
                "                JP   Z, CompositeTiles_UploadLeft",
                "                JP   CompositeTiles_UploadFull",
                "CompositeUpload_CheckY:",
                "                LD   A, (ViewportOriginX)",
                "                LD   B, A",
                "                LD   A, (RuntimeLastOriginX)",
                "                CP   B",
                "                JP   NZ, CompositeTiles_UploadFull",
                "                LD   A, (ViewportOriginY)",
                "                LD   B, A",
                "                LD   A, (RuntimeLastOriginY)",
                "                INC  A",
                "                CP   B",
                "                JP   Z, CompositeTiles_UploadDown",
                "                LD   A, (ViewportOriginY)",
                "                INC  A",
                "                LD   B, A",
                "                LD   A, (RuntimeLastOriginY)",
                "                CP   B",
                "                JP   Z, CompositeTiles_UploadUp",
                "                JP   CompositeTiles_UploadFull",
                "",
                "CompositeTiles_UploadFull:",
                "                CALL CompositeUpload_UploadPalette",
                "                LD   A, (ViewportOriginX)",
                "                LD   (CompositeUpload_StartX), A",
                "                LD   A, (ViewportOriginY)",
                "                LD   (CompositeUpload_StartY), A",
                f"                LD   A, {PACK_VIEW_W}",
                "                LD   (CompositeUpload_RectW), A",
                f"                LD   A, {PACK_VIEW_H}",
                "                LD   (CompositeUpload_RectH), A",
                "                CALL CompositeUpload_ClampRect",
                "                JP   CompositeUpload_Rect",
                "",
                "CompositeTiles_UploadRight:",
                "                LD   A, (ViewportOriginX)",
                f"                ADD  A, {PACK_VIEW_W - 1}",
                f"                CP   {width}",
                "                JR   C, .store_x",
                f"                LD   A, {width - 1}",
                ".store_x:      LD   (CompositeUpload_StartX), A",
                "                LD   A, (ViewportOriginY)",
                "                LD   (CompositeUpload_StartY), A",
                "                LD   A, 1",
                "                LD   (CompositeUpload_RectW), A",
                f"                LD   A, {PACK_VIEW_H}",
                "                LD   (CompositeUpload_RectH), A",
                "                CALL CompositeUpload_ClampRect",
                "                JP   CompositeUpload_Rect",
                "",
                "CompositeTiles_UploadLeft:",
                "                LD   A, (ViewportOriginX)",
                "                LD   (CompositeUpload_StartX), A",
                "                LD   A, (ViewportOriginY)",
                "                LD   (CompositeUpload_StartY), A",
                "                LD   A, 1",
                "                LD   (CompositeUpload_RectW), A",
                f"                LD   A, {PACK_VIEW_H}",
                "                LD   (CompositeUpload_RectH), A",
                "                CALL CompositeUpload_ClampRect",
                "                JP   CompositeUpload_Rect",
                "",
                "CompositeTiles_UploadDown:",
                "                LD   A, (ViewportOriginX)",
                "                LD   (CompositeUpload_StartX), A",
                "                LD   A, (ViewportOriginY)",
                f"                ADD  A, {PACK_VIEW_H - 1}",
                f"                CP   {height}",
                "                JR   C, .store_y",
                f"                LD   A, {height - 1}",
                ".store_y:      LD   (CompositeUpload_StartY), A",
                f"                LD   A, {PACK_VIEW_W}",
                "                LD   (CompositeUpload_RectW), A",
                "                LD   A, 1",
                "                LD   (CompositeUpload_RectH), A",
                "                CALL CompositeUpload_ClampRect",
                "                JP   CompositeUpload_Rect",
                "",
                "CompositeTiles_UploadUp:",
                "                LD   A, (ViewportOriginX)",
                "                LD   (CompositeUpload_StartX), A",
                "                LD   A, (ViewportOriginY)",
                "                LD   (CompositeUpload_StartY), A",
                f"                LD   A, {PACK_VIEW_W}",
                "                LD   (CompositeUpload_RectW), A",
                "                LD   A, 1",
                "                LD   (CompositeUpload_RectH), A",
                "                CALL CompositeUpload_ClampRect",
                "                JP   CompositeUpload_Rect",
                "",
                "CompositeUpload_ClampRect:",
                "                LD   A, (CompositeUpload_StartX)",
                "                LD   B, A",
                f"                LD   A, {width + 1}",
                "                SUB  B",
                "                LD   B, A",
                "                LD   A, (CompositeUpload_RectW)",
                "                CP   B",
                "                JR   C, .height",
                "                JR   Z, .height",
                "                LD   A, B",
                "                LD   (CompositeUpload_RectW), A",
                ".height:       LD   A, (CompositeUpload_StartY)",
                "                LD   B, A",
                f"                LD   A, {height + 1}",
                "                SUB  B",
                "                LD   B, A",
                "                LD   A, (CompositeUpload_RectH)",
                "                CP   B",
                "                RET  C",
                "                RET  Z",
                "                LD   A, B",
                "                LD   (CompositeUpload_RectH), A",
                "                RET",
                "",
                "CompositeUpload_UploadPalette:",
                f"                LD   A, #{TERRAIN_PAGE_BASE:02X}",
                "                LD   (Render_DmaSourcePage), A",
                "                LD   HL, #C000",
                f"                LD   A, #{(RAMG_TERRAIN_BASE >> 16) & 0xFF:02X}",
                f"                LD   DE, #{RAMG_TERRAIN_BASE & 0xFFFF:04X}",
                "                CALL CompositeUpload_AddBankOffset",
                f"                LD   BC, {COMPOSITE_BG_PALETTE_SIZE if COMPOSITE_BG_PALETTED4444 else 0}",
                "                CALL Render_WriteMem_DMA",
                "                RET",
                "",
                "CompositeUpload_Rect:",
                "                GetPage3",
                "                LD   (CompositeUpload_RestorePage), A",
                f"                SetPage3 #{COMPOSITE_UPLOAD_PAGE_BASE:02X}",
                "                CALL CompositeUploadCellPtr",
                "CompositeUpload_RowLoop:",
                "                LD   A, (CompositeUpload_RectW)",
                "                LD   (CompositeUpload_ColCount), A",
                "CompositeUpload_ColLoop:",
                "                CALL CompositeUpload_Cell",
                "                LD   BC, 6",
                "                ADD  IX, BC",
                "                LD   HL, CompositeUpload_ColCount",
                "                DEC  (HL)",
                "                JR   NZ, CompositeUpload_ColLoop",
                "                LD   BC, (COMPOSITE_UPLOAD_STRIDE - 1) * 6",
                "                LD   A, (CompositeUpload_RectW)",
                "CompositeUpload_RowSkipLoop:",
                "                DEC  A",
                "                JR   Z, CompositeUpload_RowSkipDone",
                "                LD   DE, -6",
                "                ADD  IX, DE",
                "                JR   CompositeUpload_RowSkipLoop",
                "CompositeUpload_RowSkipDone:",
                "                ADD  IX, BC",
                "                LD   HL, CompositeUpload_RectH",
                "                DEC  (HL)",
                "                JR   NZ, CompositeUpload_RowLoop",
                "CompositeUpload_RestorePage EQU $+1",
                "                LD   A, #00",
                "                SetPage3_A",
                "                RET",
                "",
                "CompositeUpload_Cell:",
                "                LD   A, (IX + 0)",
                "                LD   (Render_DmaSourcePage), A",
                "                LD   L, (IX + 1)",
                "                LD   H, (IX + 2)",
                "                LD   DE, #C000",
                "                ADD  HL, DE",
                "                LD   A, (IX + 3)",
                "                LD   E, (IX + 4)",
                "                LD   D, (IX + 5)",
                "                CALL CompositeUpload_AddBankOffset",
                f"                LD   BC, {COMPOSITE_TILE_BYTES}",
                "                CALL Render_WriteMem_DMA",
                "                RET",
                "",
                "CompositeUploadCellPtr:",
                "                LD   HL, 0",
                "                LD   A, (CompositeUpload_StartY)",
                "                LD   B, A",
                f"                LD   DE, {(width + 1) * 6}",
                "                OR   A",
                "                JR   Z, .x",
                ".yloop:         ADD  HL, DE",
                "                DJNZ .yloop",
                ".x:             LD   A, (CompositeUpload_StartX)",
                "                LD   E, A",
                "                LD   D, 0",
                "                ADD  HL, DE",
                "                ADD  HL, DE",
                "                ADD  HL, DE",
                "                ADD  HL, DE",
                "                ADD  HL, DE",
                "                ADD  HL, DE",
                "                LD   DE, #C000",
                "                ADD  HL, DE",
                "                PUSH HL",
                "                POP  IX",
                "                RET",
                "",
                "CompositeUpload_StartX:",
                "                DEFB 0",
                "CompositeUpload_StartY:",
                "                DEFB 0",
                "CompositeUpload_RectW:",
                "                DEFB 0",
                "CompositeUpload_RectH:",
                "                DEFB 0",
                "CompositeUpload_ColCount:",
                "                DEFB 0",
                "CompositeDrawBank:",
                "                DEFB 0",
                "CompositeUploadOffsetLow:",
                "                DEFW 0",
                "CompositeUploadOffsetHigh:",
                "                DEFB 0",
            ]
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_objects_inc(path: Path, object_chunks, object_size: int, hero_sprite, sorc_sprite, cursor_sprites, ui_sprites, route_sprites, route_table_page: int, route_red_palette_addr: int = 0, cursor_chunks=None):
    cursor_sprite = cursor_sprites[CURSOR_POINTER_INDEX]
    ui_radar = ui_sprites["radar"]
    lines = [
        "; Сгенерировано Source/Tools/viewport_pack.py",
        "",
        f"OBJECT_ATLAS_RAMG       EQU #{RAMG_OBJECT_BASE:06X}",
        f"OBJECT_PALETTE_RAMG     EQU #{RAMG_OBJECT_BASE:06X}",
        f"OBJECT_OPAQUE_PALETTE_RAMG EQU #{RAMG_OBJECT_BASE + OBJECT_PALETTE_SIZE:06X}",
        f"OBJECT_PALETTE_SIZE     EQU {OBJECT_PALETTE_SIZE}",
        f"OBJECT_OPAQUE_PALETTE_SIZE EQU {OBJECT_OPAQUE_PALETTE_SIZE}",
        f"OBJECT_ATLAS_PAGE_BASE  EQU #{OBJECT_PAGE_BASE:02X}",
        f"OBJECT_ATLAS_PAGE_COUNT EQU {len(object_chunks)}",
        f"OBJECT_ATLAS_SIZE       EQU {object_size}",
        f"HERO_SPRITE_RAMG        EQU #{hero_sprite['addr']:06X}",
        f"HERO_SPRITE_W           EQU {hero_sprite['w']}",
        f"HERO_SPRITE_H           EQU {hero_sprite['h']}",
        f"HERO_SPRITE_OX          EQU {hero_sprite['ox']}",
        f"HERO_SPRITE_OY          EQU {hero_sprite['oy']}",
        f"SORC_SPRITE_RAMG        EQU #{sorc_sprite['addr']:06X}",
        f"SORC_SPRITE_W           EQU {sorc_sprite['w']}",
        f"SORC_SPRITE_H           EQU {sorc_sprite['h']}",
        f"SORC_SPRITE_OX          EQU {sorc_sprite['ox']}",
        f"SORC_SPRITE_OY          EQU {sorc_sprite['oy']}",
        f"CURSOR_SPRITE_RAMG      EQU #{cursor_sprite['addr']:06X}",
        f"CURSOR_SPRITE_W         EQU {cursor_sprite['w']}",
        f"CURSOR_SPRITE_H         EQU {cursor_sprite['h']}",
        f"CURSOR_SPRITE_OX        EQU {cursor_sprite['ox']}",
        f"CURSOR_SPRITE_OY        EQU {cursor_sprite['oy']}",
        f"CURSOR_SPRITE_STRIDE    EQU {cursor_sprite['stride']}",
        f"CURSOR_SPRITE_SIZE_W    EQU {cursor_sprite['scaled_w']}",
        f"CURSOR_SPRITE_SIZE_H    EQU {cursor_sprite['scaled_h']}",
        f"CURSOR_SPRITE_COUNT     EQU {len(cursor_sprites)}",
        f"CURSOR_POINTER_INDEX    EQU {CURSOR_POINTER_INDEX}",
        f"CURSOR_MOVE_BASE_INDEX  EQU {CURSOR_MOVE_BASE_INDEX}",
        f"CURSOR_FIGHT_BASE_INDEX EQU {CURSOR_MOVE_BASE_INDEX + 8}",   # FIGHT 1..8 (меч + дни)
        f"CURSOR_ACTION_BASE_INDEX EQU {CURSOR_MOVE_BASE_INDEX + 16}", # ACTION 1..8 (конь + дни)
        f"CURSOR_HEROES_INDEX    EQU {CURSOR_MOVE_BASE_INDEX + 24}",   # на своём герое
        f"CURSOR_CASTLE_INDEX    EQU {CURSOR_MOVE_BASE_INDEX + 25}",   # на своём замке
        f"CURSOR_SCROLL_BASE_INDEX EQU {len(cursor_sprites) - 8}",
        f"CURSOR_BATTLE_BASE_INDEX EQU {len(cursor_sprites) - 19}",  # боевые: NONE/MOVE/ARROW/INFO/POINTER/6×SWORD (11) до 8 скроллов",
        "CURSOR_TABLE_ENTRY_SIZE EQU 12",
        f"UI_BORDER_W             EQU {ui_sprites['border_w']}",
        f"UI_BORDER_H             EQU {ui_sprites['border_h']}",
        f"UI_RADAR_RAMG           EQU #{ui_radar['addr']:06X}",
        f"UI_RADAR_PALETTE_RAMG   EQU #{ui_radar['palette_addr']:06X}",
        f"UI_RADAR_W              EQU {ui_radar['w']}",
        f"UI_RADAR_H              EQU {ui_radar['h']}",
        f"UI_RADAR_STRIDE         EQU {ui_radar['stride']}",
        f"UI_RADAR_X              EQU {UI_RADAR_X}",
        f"UI_RADAR_Y              EQU {UI_RADAR_Y}",
        f"MINIMAP_TILE_PX         EQU {ui_radar['tile_px']}",
        f"MINIMAP_RECT_LOGICAL    EQU {VIEW_W * ui_radar['tile_px']}",
        f"UI_RADAR_X16            EQU {scaled_vertex2f_units(UI_RADAR_X)}",
        f"UI_RADAR_Y16            EQU {scaled_vertex2f_units(UI_RADAR_Y)}",
        f"UI_BUTTON_X             EQU {UI_BUTTON_X}",
        f"UI_BUTTON_Y             EQU {UI_BUTTON_Y}",
        f"UI_BUTTON_W             EQU {UI_BUTTON_W}",
        f"UI_BUTTON_H             EQU {UI_BUTTON_H}",
        f"UI_BUTTON_COLS          EQU 4",
        f"UI_BUTTON_GRID_W        EQU {UI_BUTTON_W * 4}",
        f"UI_BUTTON_GRID_H        EQU {UI_BUTTON_H * 2}",
        f"UI_BUTTON_COUNT         EQU {len(UI_BUTTON_INDICES)}",
        f"UI_STATUS_X             EQU {UI_STATUS_X}",
        f"UI_STATUS_Y             EQU {UI_STATUS_Y}",
        f"UI_STATUS_W             EQU {UI_STATUS_W}",
        f"UI_STATUS_H             EQU {UI_STATUS_H}",
        f"ROUTE_SPRITE_COUNT      EQU {len(route_sprites)}",
        "ROUTE_PALETTE_RAMG      EQU OBJECT_PALETTE_RAMG",
        f"ROUTE_RED_PALETTE_RAMG  EQU #{route_red_palette_addr:06X}",
        f"ROUTE_TABLE_PAGE        EQU #{route_table_page:02X}",
        "ROUTE_TABLE_ADDR        EQU #0000",
        "ROUTE_TABLE_ENTRY_SIZE  EQU 12",
        "",
    ]
    lines.append("CursorSpriteTable:")
    for sprite in cursor_sprites:
        lines.append(
            f"                DEFB #{(sprite['addr'] >> 16) & 0xFF:02X}, "
            f"#{sprite['addr'] & 0xFF:02X}, #{(sprite['addr'] >> 8) & 0xFF:02X}, "
            f"{sprite['h']}, {sprite['stride']}, {sprite['scaled_w']}, {sprite['scaled_h']}, 0"
        )
        lines.append(f"                DEFW #{sprite['draw_ox'] & 0xFFFF:04X}")
        lines.append(f"                DEFW #{sprite['draw_oy'] & 0xFFFF:04X}")
    lines.append("")

    # Таблица цвета-палитры мини-карты на каждый тайл (1 байт/тайл, stride = map_w).
    # Источник для рантайм-раскрытия тумана на радаре (Minimap_RevealTile).
    # ★ВЫНЕСЕНА из резидента (1296Б, упор ядра в CMD_ADDRESS_PTR) в data-страницу #91
    # (GLOBAL_DATA_PAGE): читатель ОДИН байт за вызов и мапит slot3 (как MonsterStats_Read).
    radar_tile_colors = ui_radar["tile_colors"]
    lines.append(f"MINIMAP_MAP_W           EQU {ui_radar['map_w']}")
    lines.append(f"MINIMAP_MAP_H           EQU {ui_radar['map_h']}")
    mlines = ["; Сгенерировано viewport_pack.py — цвета тайлов мини-карты (включать в GLOBAL_DATA_PAGE #91).",
              "MinimapTileColorTable:"]
    for i in range(0, len(radar_tile_colors), 32):
        chunk = radar_tile_colors[i:i + 32]
        mlines.append("                DEFB " + ", ".join(str(b) for b in chunk))
    (Path("Source/ASM/generated_minimap_tab.inc")).write_text("\n".join(mlines) + "\n", encoding="utf-8")
    lines.append("")

    # Статус-окно: STONBACK (каменный фон) + RESSMALL (иконки kingdom-вида).
    stonback = ui_sprites["stonback"]
    ressmall = ui_sprites["ressmall"]
    sunmoon = ui_sprites["sunmoon"]
    lines.extend(
        [
            f"UI_STONBACK_RAMG        EQU #{stonback['addr']:06X}",
            f"UI_STONBACK_W           EQU {stonback['w']}",
            f"UI_STONBACK_H           EQU {stonback['h']}",
            f"UI_STONBACK_STRIDE      EQU {stonback['stride']}",
            f"UI_RESSMALL_RAMG        EQU #{ressmall['addr']:06X}",
            f"UI_RESSMALL_W           EQU {ressmall['w']}",
            f"UI_RESSMALL_H           EQU {ressmall['h']}",
            f"UI_RESSMALL_STRIDE      EQU {ressmall['stride']}",
            f"UI_SUNMOON_RAMG         EQU #{sunmoon['addr']:06X}",
            f"UI_SUNMOON_W            EQU {sunmoon['w']}",
            f"UI_SUNMOON_H            EQU {sunmoon['h']}",
            f"UI_SUNMOON_STRIDE       EQU {sunmoon['stride']}",
        ]
    )
    dl = ui_sprites["date_labels"]
    for key, name in (("month", "MONTH"), ("week", "WEEK"), ("day", "DAY")):
        s = dl[key]
        lines.extend([
            f"UI_LBL_{name}_RAMG       EQU #{s['addr']:06X}",
            f"UI_LBL_{name}_W          EQU {s['w']}",
            f"UI_LBL_{name}_H          EQU {s['h']}",
            f"UI_LBL_{name}_STRIDE     EQU {s['stride']}",
        ])

    # ARMY-вид: дефолтная армия стартового героя (Knight: Peasant+Archer). В RAM_G только её типы.
    army = ui_sprites["army_sprites"]
    lines.append(f"UI_ARMY_COUNT           EQU {len(army)}")
    for i, (s, count) in enumerate(army):
        lines.extend([
            f"UI_ARMY{i}_RAMG           EQU #{s['addr']:06X}",
            f"UI_ARMY{i}_W              EQU {s['w']}",
            f"UI_ARMY{i}_H              EQU {s['h']}",
            f"UI_ARMY{i}_STRIDE         EQU {s['stride']}",
            f"UI_ARMY{i}_COUNT          EQU {count}",
        ])

    # Панель героя (фон, портреты, полоски маны и хода)
    portxtra = ui_sprites["portxtra"]
    lines.extend(
        [
            f"UI_PORTXTRA_RAMG        EQU #{portxtra['addr']:06X}",
            f"UI_PORTXTRA_W           EQU {portxtra['w']}",
            f"UI_PORTXTRA_H           EQU {portxtra['h']}",
            f"UI_PORTXTRA_STRIDE      EQU {portxtra['stride']}",
        ]
    )

    mobility_first = ui_sprites["mobility"][0]
    mobility_last = ui_sprites["mobility"][-1]
    lines.extend(
        [
            f"UI_MOBILITY_RAMG        EQU #{mobility_first['addr']:06X}",
            f"UI_MOBILITY_W           EQU {mobility_last['w']}",
            f"UI_MOBILITY_H           EQU {mobility_last['h']}",
            f"UI_MOBILITY_STRIDE      EQU {mobility_last['stride']}",
            f"UI_MOBILITY_FRAMES      EQU {len(ui_sprites['mobility'])}",
        ]
    )

    lines.append("MobilityFrameTable:")
    for m in ui_sprites["mobility"]:
        a = m["addr"]
        lines.append(f"                DEFB #{a & 0xFF:02X}, #{(a >> 8) & 0xFF:02X}, #{(a >> 16) & 0xFF:02X}")

    mana_first = ui_sprites["mana"][0]
    mana_last = ui_sprites["mana"][-1]
    lines.extend(
        [
            f"UI_MANA_RAMG            EQU #{mana_first['addr']:06X}",
            f"UI_MANA_W               EQU {mana_last['w']}",
            f"UI_MANA_H               EQU {mana_last['h']}",
            f"UI_MANA_STRIDE          EQU {mana_last['stride']}",
            f"UI_MANA_FRAMES          EQU {len(ui_sprites['mana'])}",
        ]
    )

    lines.append("ManaFrameTable:")
    for m in ui_sprites["mana"]:
        a = m["addr"]
        lines.append(f"                DEFB #{a & 0xFF:02X}, #{(a >> 8) & 0xFF:02X}, #{(a >> 16) & 0xFF:02X}")

    miniport = ui_sprites["miniport"][0]
    lines.extend(
        [
            f"UI_MINIPORT_RAMG        EQU #{miniport['addr']:06X}",
            f"UI_MINIPORT_W           EQU {miniport['w']}",
            f"UI_MINIPORT_H           EQU {miniport['h']}",
            f"UI_MINIPORT_STRIDE      EQU {miniport['stride']}",
            f"UI_MINIPORT_FRAMES      EQU {len(ui_sprites['miniport'])}",
        ]
    )

    lines.append("")

    # Цифры SMALFONT для Render_Number16. (ResourceIconTable удалён — иконки даёт RESSMALL.)
    lines.append("DIGIT_ENTRY             EQU 5")
    lines.append("DigitTable:")
    for d in ui_sprites["digits"]:
        a = d["addr"]
        lines.append(f"                DEFB #{a & 0xFF:02X}, #{(a >> 8) & 0xFF:02X}, #{(a >> 16) & 0xFF:02X}, {d['w']}, {d['h']}")
    lines.append(f"RESOURCE_PANEL_RAMG     EQU #{ui_sprites['resource_panel_ramg']:06X}")
    lines.append("")

    def scaled_len(value: int) -> int:
        return (value * DISPLAY_SCALE_NUM + DISPLAY_SCALE_DEN - 1) // DISPLAY_SCALE_DEN

    def add_paletted_blit(sprite: dict, sx: int, sy: int, w: int, h: int, dx: int, dy: int) -> None:
        if w <= 0 or h <= 0:
            return
        scaled_w = scaled_len(w)
        scaled_h = scaled_len(h)
        lines.extend(
            [
                f"                FT_BITMAP_SOURCE #{sprite['addr'] + sy * sprite['stride'] + sx:06X}",
                f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {sprite['stride']}, {h}",
                f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {scaled_w}, {scaled_h}",
                f"                FT_VERTEX2F {scaled_vertex2f_units(dx)}, {scaled_vertex2f_units(dy)}",
            ]
        )

    lines.extend(
        [
            "AdventureUI_DL:",
            "                FT_SCISSOR_XY 0, 0",
            "                FT_SCISSOR_SIZE 1024, 768",
            "                FT_COLOR_RGB 255, 255, 255",
            "                FT_COLOR_A 255",
            "                FT_BITMAP_HANDLE 3",
            "                FT_CELL 0",
            "                FT_BITMAP_TRANSFORM_A 160",
            "                FT_BITMAP_TRANSFORM_B 0",
            "                FT_BITMAP_TRANSFORM_C 0",
            "                FT_BITMAP_TRANSFORM_D 0",
            "                FT_BITMAP_TRANSFORM_E 160",
            "                FT_BITMAP_TRANSFORM_F 0",
            "                FT_VERTEX_TRANSLATE_X 0",
            "                FT_VERTEX_TRANSLATE_Y 0",
            "                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA",
            "                FT_PALETTE_SOURCE OBJECT_OPAQUE_PALETTE_RAMG",
            "                FT_BITMAP_LAYOUT_H 0, 0",
            "                FT_BITMAP_SIZE_H 0, 0",
            "                FT_BEGIN FT_BITMAPS",
        ]
    )
    for item in ui_sprites["background_blits"]:
        sprite = item["sprite"]
        add_paletted_blit(sprite, 0, 0, sprite["w"], sprite["h"], item["dx"], item["dy"])
    lines.extend(["                FT_END", "                FT_PALETTE_SOURCE OBJECT_PALETTE_RAMG", "                FT_BEGIN FT_BITMAPS"])
    # Кнопки панели приключений теперь отрисовываются динамически в Render_AdvButtonsCmd
    # в зависимости от их логического состояния (Normal/Inactive/Disabled/Pressed).
    lines.extend(
        [
            "                FT_END",
            "                FT_BLEND_FUNC FT_ONE, FT_ZERO",
            "                FT_PALETTE_SOURCE UI_RADAR_PALETTE_RAMG",
            f"                FT_BITMAP_SOURCE #{ui_radar['addr']:06X}",
            f"                FT_BITMAP_LAYOUT FT_PALETTED4444, {ui_radar['stride']}, {ui_radar['h']}",
            f"                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, {ui_radar['scaled_w']}, {ui_radar['scaled_h']}",
            "                FT_BEGIN FT_BITMAPS",
            f"                FT_VERTEX2F {scaled_vertex2f_units(UI_RADAR_X)}, {scaled_vertex2f_units(UI_RADAR_Y)}",
            "                FT_END",
            "                FT_BLEND_FUNC FT_SRC_ALPHA, FT_ONE_MINUS_SRC_ALPHA",
            # Рамка ADVBORD непрозрачна (оригинал = Blit без альфы): индекс-0 = сплошной чёрный,
            # НЕ прозрачность. OBJECT_PALETTE_RAMG даёт alpha=0 у инд.0 → дыры в тени рамки.
            # OPAQUE-палитра (alpha=15 всем) убирает дыры. Фон панели уже на ней.
            "                FT_PALETTE_SOURCE OBJECT_OPAQUE_PALETTE_RAMG",
            "                FT_BEGIN FT_BITMAPS",
            "                FT_BITMAP_LAYOUT_H 0, 0",
            "                FT_BITMAP_SIZE_H 0, 0",
        ]
    )
    for item in ui_sprites["border_blits"]:
        sprite = item["sprite"]
        add_paletted_blit(sprite, 0, 0, sprite["w"], sprite["h"], item["dx"], item["dy"])
    lines.extend(["                FT_END", "                FT_BITMAP_LAYOUT_H 0, 0", "                FT_BITMAP_SIZE_H 0, 0", "AdventureUI_DL_SIZE EQU $ - AdventureUI_DL", ""])

    def generate_btn_dl(prefix: str, sprites: list):
        lines.append(f"@{prefix}Tab:")
        for i in range(len(sprites)):
            lines.append(f"                DEFW {prefix}_{i}_DL")
        for i, sprite in enumerate(sprites):
            bx = UI_BUTTON_X + (i % 4) * UI_BUTTON_W
            by = UI_BUTTON_Y + (i // 4) * UI_BUTTON_H
            lines.append(f"{prefix}_{i}_DL:")
            add_paletted_blit(sprite, 0, 0, sprite["w"], sprite["h"], bx, by)
        lines.append(f"@{prefix}_DL_SIZE EQU {prefix}_1_DL - {prefix}_0_DL")

    generate_btn_dl("UI_BtnNormal", ui_sprites["buttons"])
    generate_btn_dl("UI_BtnPressed", ui_sprites["buttons_pressed"])

    lines.append("")
    lines.extend(
        [
        "Objects_Upload:",
        "                GetPage3",
        "                LD   (.RestorePage), A",
        ]
    )
    ramg = RAMG_OBJECT_BASE
    for _, page, real_size in object_chunks:
        lines.extend(
            [
                f"                SetPage3 #{page:02X}",
                "                LD   HL, #C000",
                f"                LD   A, #{(ramg >> 16) & 0xFF:02X}",
                f"                LD   DE, #{ramg & 0xFFFF:04X}",
                f"                LD   BC, {real_size}",
                "                CALL FT.WriteMem",
            ]
        )
        ramg += real_size
    lines.extend([".RestorePage    EQU $+1", "                LD   A, #00", "                SetPage3_A", "                RET", ""])
    # Глобальный курсор: резидентная загрузка спрайтов в постоянную зону RAM_G один раз
    # (вызывается из Game_Init). Спрайты в SPG-странице CURSOR_RESIDENT_PAGE.
    if cursor_chunks:
        lines.extend(["Cursor_GlobalUpload:", "                GetPage3", "                LD   (.CurRestore), A"])
        ramg = CURSOR_RAMG_BASE
        for _, page, real_size in cursor_chunks:
            lines.extend([
                f"                SetPage3 #{page:02X}",
                "                LD   HL, #C000",
                f"                LD   A, #{(ramg >> 16) & 0xFF:02X}",
                f"                LD   DE, #{ramg & 0xFFFF:04X}",
                f"                LD   BC, {real_size}",
                "                CALL FT.WriteMem",
            ])
            ramg += real_size
        lines.extend([".CurRestore     EQU $+1", "                LD   A, #00", "                SetPage3_A", "                RET", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_background_inc(path: Path):
    path.write_text(
        "\n".join(
            [
                "; Сгенерировано Source/Tools/viewport_pack.py",
                "; Штатный фон adventure map строится из terrain atlas.",
                "",
                "Background_Upload:",
                "                CALL Terrain_Upload",
                "                RET",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_empty_adventure_dl(path: Path):
    path.write_text(
        "\n".join(
            [
                "; Сгенерировано Source/Tools/viewport_pack.py",
                "; ADVENTURE_DL берется из viewport DL pack.",
                "",
                "ADVENTURE_DL:",
                "                FT_DISPLAY",
                "ADVENTURE_DL_SIZE EQU $ - ADVENTURE_DL",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_composite_view_preview(path: Path, terrain_payload: bytes, palette, width: int, height: int, origin_x: int = 0, origin_y: int = 0):
    try:
        from PIL import Image
    except ImportError:
        return
    img = Image.new("RGB", (VIEW_W * TILE_PX, VIEW_H * TILE_PX), (0, 0, 0))
    for vy in range(VIEW_H):
        my = min(origin_y + vy, height - 1)
        for vx in range(VIEW_W):
            mx = min(origin_x + vx, width - 1)
            tile_index = my * width + mx
            off = COMPOSITE_BG_TILE_OFFSET + tile_index * COMPOSITE_TILE_BYTES
            tile = terrain_payload[off:off + COMPOSITE_TILE_BYTES]
            tile_img = Image.new("RGB", (TILE_PX, TILE_PX))
            if COMPOSITE_BG_PALETTED4444:
                tile_img.putdata([palette[pix] for pix in tile])
            else:
                pixels = []
                for i in range(TILE_PX * TILE_PX):
                    value = tile[i * 2] | (tile[i * 2 + 1] << 8)
                    pixels.append((((value >> 11) & 31) << 3, ((value >> 5) & 63) << 2, (value & 31) << 3))
                tile_img.putdata(pixels)
            img.paste(tile_img, (vx * TILE_PX, vy * TILE_PX))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def update_spgbld(path: Path, chunks):
    text = path.read_text(encoding="utf-8")
    head = text.split("; Страницы terrain atlas.", 1)[0].rstrip()
    lines = [head, "", "; Страницы terrain atlas."]
    for chunk_path, page, _ in chunks:
        lines.append(f"Block = #0000, #{page:02X}, {chunk_path.as_posix()}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = Path(".")
    agg_data, entries = read_agg_index_with_expansion(root / "Assets/Original/DATA/HEROES2.AGG")
    palette = read_palette(agg_entry(agg_data, entries, "KB.PAL"))
    ground_tiles = read_til(agg_entry(agg_data, entries, "GROUND32.TIL"))
    width, height, map_data = read_map(root / "Assets/Converted/Maps/SKIRMISH.map.bin")
    tiles = map_data[0] if isinstance(map_data, tuple) else map_data
    transfer_plan = build_object_transfer_plan(width, height, map_data, cycled_terrain_indices(ground_tiles))
    validate_object_transfer_plan(transfer_plan)

    max_x, max_y = pack_origin_max(width, height)
    if COMPOSITE_STATIC_TILEMAP:
        terrain_keys = all_terrain_keys(tiles)
        _, terrain_remap = build_terrain_atlas(ground_tiles, palette, terrain_keys)
        terrain_payload = build_composite_tiles(ground_tiles, agg_data, entries, palette, width, height, map_data, transfer_plan)
        upload_payload, composite_upload_entries = build_composite_upload_scripts(width, height, max_x, max_y)
        object_payload_raw, sprite_cache = build_object_atlas(agg_data, entries, palette, width, height, transfer_plan)
        object_payload = bytearray(object_payload_raw)
    else:
        if FULL_VIEWPORT_PACK:
            terrain_keys = all_terrain_keys(tiles)
        else:
            terrain_keys = []
            seen_terrain = set()
            for oy in range(max_y + 1):
                for ox in range(max_x + 1):
                    for _, _, terrain, shape in visible_cells(width, height, tiles, ox, oy):
                        key = (terrain, shape)
                        if key not in seen_terrain:
                            seen_terrain.add(key)
                            terrain_keys.append(key)
        terrain_payload, terrain_remap = build_terrain_atlas(ground_tiles, palette, terrain_keys)
        upload_payload = b""
        composite_upload_entries = None
        object_payload_raw, sprite_cache = build_object_atlas(agg_data, entries, palette, width, height, transfer_plan)
        object_payload = bytearray(object_payload_raw)
    route_sprites = append_route_sprites(object_payload, agg_data, entries, palette)
    # Красная палитра для недостижимой части маршрута (paletted route + смена палитры).
    route_red_palette_addr = RAMG_OBJECT_BASE + align(len(object_payload), 4)
    while RAMG_OBJECT_BASE + len(object_payload) < route_red_palette_addr:
        object_payload.append(0)
    object_payload.extend(palette_argb4444_red(palette))
    # Герой на карте = MINIHERO.ICN, индекс = colorIndex*7 + race (map_object_info.cpp:5819).
    # Цвета строк: 0=Blue 1=Green 2=Red 3=Yellow 4=Orange 5=Purple; расы: 0=Knight 1=Barbar
    # 2=Sorc 3=Warlock 4=Wizard 5=Necro 6=Random. Игрок SKIRMISH = Blue Knight «Hampshire»
    # → idx 0*7+0 = 0. Враг = Yellow Sorceress «Quick Silver» → idx 3*7+2 = 23.
    hero_sprite = append_overlay_sprite(object_payload, agg_data, entries, palette, "MINIHERO.ICN", 0)
    sorc_sprite = append_overlay_sprite(object_payload, agg_data, entries, palette, "MINIHERO.ICN", 23)
    cursor_sprites, cursor_payload = append_cursor_sprites(agg_data, entries, palette)
    ui_sprites = append_adventure_ui_sprites(object_payload, agg_data, entries, palette, ground_tiles, width, height, map_data)

    # Анимация adventure-объектов: упаковать кадры-дельты (PALETTED) в object_payload
    # и собрать MapAnimTable. Делаем ДО write_chunks_pages, чтобы кадры попали в
    # object-страницы RAM_G.
    anim_objects = collect_map_anim_objects(transfer_plan)
    map_anim_table, anim_skipped = pack_anim_frames(object_payload, agg_data, entries, anim_objects)
    anim_frames_total = sum(len(e["frames"]) for e in map_anim_table)
    print(f"анимация объектов: {len(map_anim_table)} частей, {anim_frames_total} кадров (PALETTED)")
    if anim_skipped:
        print(f"анимация: пропущено mono/empty-частей (база статична): {len(anim_skipped)} {anim_skipped[:6]}")

    dl_payload = bytearray()
    if not RUNTIME_TILEMAP_RENDER:
        for oy in range(max_y + 1):
            for ox in range(max_x + 1):
                dl_payload.extend(viewport_dl(width, height, map_data, transfer_plan, ox, oy, terrain_remap, sprite_cache))

    terrain_chunks = write_chunks(root / "Assets/Converted/Terrain", "SKIRMISH_GROUND32_p{:02d}.bin", TERRAIN_PAGE_BASE, terrain_payload)
    object_chunks = write_chunks_pages(root / "Assets/Converted/Objects", "SKIRMISH_OBJECTS_p{:02d}.bin", OBJECT_PAGE_LIST, bytes(object_payload))
    if len(object_chunks) >= len(OBJECT_PAGE_LIST):
        raise ValueError("нет свободной страницы для ROUTE table")
    route_table_page = OBJECT_PAGE_LIST[len(object_chunks)]
    route_table_chunks = write_route_table(root / "Assets/Converted/Objects/SKIRMISH_ROUTE_TABLE.bin", route_table_page, route_sprites)
    runtime_map_cells_index = len(object_chunks) + len(route_table_chunks)
    if runtime_map_cells_index >= len(OBJECT_PAGE_LIST):
        raise ValueError("нет свободной страницы для runtime map cells")
    runtime_map_cells_page = OBJECT_PAGE_LIST[runtime_map_cells_index]
    runtime_map_cells_chunks = write_runtime_map_cells(
        root / "Assets/Converted/Maps" / RUNTIME_MAP_CELLS_NAME,
        runtime_map_cells_page,
        width,
        height,
        tiles,
        terrain_remap,
    )
    viewport_chunks = write_chunks(root / "Assets/Converted/Viewports", "SKIRMISH_VIEWPORT_p{:02d}.bin", VIEWPORT_PAGE_BASE, bytes(dl_payload))
    object_view_page_base = OBJECT_VIEW_PAGE_BASE
    object_view_pages = OBJECT_VIEW_PAGE_LIST
    object_view_payload = bytearray()
    object_view_entries = []
    for oy in range(max_y + 1):
        for ox in range(max_x + 1):
            # blob = [низ-оверлей][top-оверлей] без хвостовых DISPLAY (append-части).
            # Одна заливка в RUNTIME_DL_OBJECT_RAMG, два CMD_APPEND: низ до актёра,
            # верх — после (z-слои fheroes2).
            bottom = object_view_dl(width, height, transfer_plan, ox, oy, sprite_cache)
            top = top_object_view_dl(width, height, transfer_plan, ox, oy, sprite_cache)
            bottom_size = len(bottom) - 4
            top_size = len(top) - 4
            if bottom_size + top_size + 4 > OBJECT_VIEW_DL_SIZE:
                raise ValueError(f"object blob {ox},{oy}: низ {bottom_size} + верх {top_size} > {OBJECT_VIEW_DL_SIZE - 4}")
            blob = bottom[:-4] + top[:-4]
            pos_in_page = len(object_view_payload) % PAGE_SIZE
            if pos_in_page and pos_in_page + len(blob) > PAGE_SIZE:
                object_view_payload.extend(b"\0" * (PAGE_SIZE - pos_in_page))
            pos = len(object_view_payload)
            page_index = pos // PAGE_SIZE
            if object_view_pages is None:
                page = object_view_page_base + page_index
            else:
                if page_index >= len(object_view_pages):
                    raise ValueError(f"object-view pages: need index {page_index}, available {len(object_view_pages)}")
                page = object_view_pages[page_index]
            object_view_entries.append((page, pos % PAGE_SIZE, bottom_size, top_size))
            object_view_payload.extend(blob)
    if object_view_pages is None:
        object_view_chunks = write_chunks(
            root / "Assets/Converted/Viewports",
            "SKIRMISH_OBJECTVIEW_p{:02d}.bin",
            object_view_page_base,
            bytes(object_view_payload),
        )
    else:
        object_view_chunks = write_chunks_pages(
            root / "Assets/Converted/Viewports",
            "SKIRMISH_OBJECTVIEW_p{:02d}.bin",
            object_view_pages,
            bytes(object_view_payload),
        )
    upload_chunks = write_chunks(root / "Assets/Converted/Viewports", "SKIRMISH_COMPOSITE_UPLOAD_p{:02d}.bin", COMPOSITE_UPLOAD_PAGE_BASE, upload_payload)
    write_terrain_inc(root / "Source/ASM/generated_terrain.inc", terrain_chunks, object_chunks, viewport_chunks, width, height, object_view_page_base)
    cursor_chunks = write_chunks(root / "Assets/Converted/Cursor", "SKIRMISH_CURSOR_p{:02d}.bin", CURSOR_RESIDENT_PAGE, bytes(cursor_payload))
    write_objects_inc(root / "Source/ASM/generated_objects.inc", object_chunks, len(object_payload), hero_sprite, sorc_sprite, cursor_sprites, ui_sprites, route_sprites, route_table_page, route_red_palette_addr, cursor_chunks)
    write_runtime_map_inc(root / "Source/ASM/generated_runtime_map.inc", width, height, tiles, terrain_remap, object_view_page_base, runtime_map_cells_page, object_view_entries, composite_upload_entries, palette)
    write_map_anim_inc(root / "Source/ASM/generated_map_anim.inc", map_anim_table)
    write_background_inc(root / "Source/ASM/generated_background.inc")
    write_empty_adventure_dl(root / "Source/ASM/generated_adventure_dl.inc")
    update_spgbld(root / "spgbld_vdac2.ini", terrain_chunks + object_chunks + route_table_chunks + runtime_map_cells_chunks + object_view_chunks + upload_chunks + viewport_chunks + cursor_chunks)

    if COMPOSITE_STATIC_TILEMAP:
        write_composite_view_preview(root / "Diagnostics/terrain_ground32_preview.png", terrain_payload, palette, width, height, 0, 0)
        write_composite_view_preview(root / "Diagnostics/terrain_ground32_preview_x40.png", terrain_payload, palette, width, height, 1, 0)
    else:
        cells0 = visible_cells(width, height, tiles, 0, 0)
        write_preview_png(
            root / "Diagnostics/terrain_ground32_preview.png",
            terrain_payload,
            cells0,
            {k: h * CELLS_PER_HANDLE + c for k, (h, c) in terrain_remap.items()},
            palette if COMPOSITE_BG_PALETTED4444 else None,
            COMPOSITE_TILE_BYTES,
            COMPOSITE_BG_TILE_OFFSET if COMPOSITE_BG_PALETTED4444 else 0,
        )
    print(f"viewport pack: origins={(max_x + 1) * (max_y + 1)}, dl={len(dl_payload)} bytes")
    print(f"terrain/composite tiles={len(terrain_payload) // COMPOSITE_TILE_BYTES}, atlas={len(terrain_payload)} bytes, pages={len(terrain_chunks)}")
    ui_strip_count = len(ui_sprites["background_blits"]) + len(ui_sprites["border_blits"])
    print(f"object sprites={len(sprite_cache)} + route={len(route_sprites)} + overlays={1 + len(cursor_sprites)} + ui strips={ui_strip_count} + buttons={len(ui_sprites['buttons'])} + radar=1, atlas={len(object_payload)} bytes, pages={len(object_chunks)}")
    print(f"route sprites: ROUTE.ICN#0..#{len(route_sprites) - 1}, table page=#{route_table_page:02X}")
    print(f"runtime map cells: page=#{runtime_map_cells_page:02X}, bytes={runtime_map_cells_chunks[0][2]}")
    if COMPOSITE_STATIC_TILEMAP:
        print(f"composite upload scripts={len(upload_payload)} bytes, pages={len(upload_chunks)}")
    print(f"hero sprite: {hero_sprite['icn']}#{hero_sprite['index']} {hero_sprite['w']}x{hero_sprite['h']}")
    print(f"cursor sprites: ADVMCO pointer + move distance 1..8 ({len(cursor_sprites)} total)")
    print(f"adventure UI: ADVBORD strips={ui_strip_count}, radar + {len(ui_sprites['buttons'])} ADVBTNS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
