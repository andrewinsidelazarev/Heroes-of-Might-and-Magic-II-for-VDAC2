#!/usr/bin/env python3
import argparse
import csv
import json
import struct
from pathlib import Path


MP2_MAP_INFO_SIZE = 428
MP2_TILE_SIZE = 20
MP2_ADDON_SIZE = 15
COMPACT_ADDON_SIZE = 16
PASSABILITY_PAGE = 0x14
PATH_METADATA_PAGE = 0x11
GRASS_START_IMAGE_INDEX = 30
SNOW_START_IMAGE_INDEX = 92
SWAMP_START_IMAGE_INDEX = 146
LAVA_START_IMAGE_INDEX = 208
DESERT_START_IMAGE_INDEX = 262
DIRT_START_IMAGE_INDEX = 321
WASTELAND_START_IMAGE_INDEX = 361
BEACH_START_IMAGE_INDEX = 415
MAX_GROUND_IMAGE_INDEX = 432
OBJECT_INFO_CSV = Path("Assets/Converted/Maps/fheroes2_object_info.csv")

DIRECTION_TOP_LEFT = 0x01
DIRECTION_TOP = 0x02
DIRECTION_TOP_RIGHT = 0x04
DIRECTION_RIGHT = 0x08
DIRECTION_BOTTOM_RIGHT = 0x10
DIRECTION_BOTTOM = 0x20
DIRECTION_BOTTOM_LEFT = 0x40
DIRECTION_LEFT = 0x80
DIRECTION_ALL8 = 0xFF
DIRECTION_CENTER_BOTTOM_ROWS8 = (
    DIRECTION_LEFT
    | DIRECTION_RIGHT
    | DIRECTION_BOTTOM_LEFT
    | DIRECTION_BOTTOM
    | DIRECTION_BOTTOM_RIGHT
)

OBJ_ACTION_OBJECT_TYPE = 128
OBJ_EVENT = 147
OBJ_MONSTER = 152
OBJ_BOAT = 171
OBJ_HERO = 183
OBJ_REEFS = 98
# Вход (гейт) замка/города — action-тайл, проходим (герой стоит на нём и выходит).
# OBJ_CASTLE = 35|128, OBJ_RANDOM_CASTLE = 49|128. Без этого MAIN-часть гейта
# (town basement, не-action) делала тайл 00 → стартовый герой заперт на гейте.
CASTLE_ENTRANCE_OBJECTS = {35 | OBJ_ACTION_OBJECT_TYPE, 49 | OBJ_ACTION_OBJECT_TYPE}
OBJECT_LAYER = 0
BACKGROUND_LAYER = 1
SHADOW_LAYER = 2
TERRAIN_LAYER = 3

ACTION_FULL_PASSABLE = {
    28, 131, 132, 134, 136, 139, 147, 152, 155, 161, 167, 169, 171, 172,
    173, 174, 175, 176, 177, 179, 180, 181, 182, 183, 220, 221, 244, 245,
    246, 247, 251, 387, 388,
}

ROAD_ICN_TYPE = 30
OBJNTOWN_ICN_TYPE = 35   # object_name>>2 для OBJNTOWN (было 34 = TREEVIL — баг)
OBJNTWRD_ICN_TYPE = 37
STREAM_ICN_TYPE = 45
FLAG_ICN_TYPE = 14

PATH_FLAG_WATER = 0x01
PATH_FLAG_STOP = 0x02
PATH_FLAG_ROAD = 0x04

ROAD_SPRITES = {
    0, 2, 3, 4, 5, 6, 7, 9, 12, 13, 14, 16, 17, 18, 19, 20, 21, 26, 28, 29,
    30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
}
OBJNTOWN_ROAD_SPRITES = {13, 29, 45, 61, 77, 93, 109, 125, 141, 157, 173, 189}
OBJNTWRD_ROAD_SPRITES = {13, 29}

DECORATION_ICN_TYPES = {
    22, 23, 24, 25, 26, 27, 31, 32, 33, 34, 42, 43, 44, 48, 50, 51, 52, 53,
    54, 55, 56, 57, 58, 59, 60,
}

SHORT_OBJECT_TYPES = {
    2, 7, 14, 31, 36, 37, 56, 61, 66, 67, 72, 73, 74, 75, 80, 81, 88, 94,
    95, 104, 119,
}

DETACHED_OBJECT_TYPES = {
    7, 23, 29, 35, 37, 124, 125, 126, 127,
}

COMBINED_OBJECT_TYPES = {
    99, 108,
}


def load_object_info(path: Path = OBJECT_INFO_CSV):
    if not path.exists():
        raise FileNotFoundError(
            f"{path}: нет таблицы object info из OpenHMM2. "
            "Соберите Source/Tools/dump_fheroes2_object_info.cpp и сохраните CSV перед конвертацией карты."
        )
    out = {}
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        for row in csv.DictReader(fp):
            key = (int(row["icn"]), int(row["index"]))
            current = out.get(key)
            item = {
                "layer": int(row["layer"]),
                "object_type": int(row["object_type"]),
                "top": int(row["top"]),
            }
            if current is None or (current["top"] and not item["top"]):
                out[key] = item
    return out


OBJECT_INFO = load_object_info()


def c_string(raw: bytes) -> str:
    return raw.split(b"\0", 1)[0].decode("cp1252", errors="replace").strip()


def read_mp2(path: Path):
    data = path.read_bytes()
    if len(data) < MP2_MAP_INFO_SIZE:
        raise ValueError(f"{path}: файл короче заголовка MP2")

    if data[:4] != bytes([0x5C, 0x00, 0x00, 0x00]):
        raise ValueError(f"{path}: неверная сигнатура MP2")

    difficulty = struct.unpack_from("<H", data, 4)[0]
    width = data[6]
    height = data[7]
    tile_count = width * height
    tiles_offset = MP2_MAP_INFO_SIZE
    tiles_size = tile_count * MP2_TILE_SIZE
    tiles_end = tiles_offset + tiles_size

    if width == 0 or height == 0:
        raise ValueError(f"{path}: неверный размер карты {width}x{height}")
    if len(data) < tiles_end:
        raise ValueError(f"{path}: файл закончился до таблицы тайлов")
    if len(data) < tiles_end + 4:
        raise ValueError(f"{path}: файл закончился до счетчика addon")

    header = {
        "file": str(path),
        "name": c_string(data[58:58 + 16]),
        "description": c_string(data[118:118 + 200]),
        "difficulty": difficulty,
        "width": width,
        "height": height,
        "tile_count": tile_count,
        "tiles_offset": tiles_offset,
        "source_size": len(data),
    }

    tiles = []
    for i in range(tile_count):
        off = tiles_offset + i * MP2_TILE_SIZE
        terrain, object_name1, bottom_icn, quantity1, quantity2, object_name2, top_icn, terrain_flags, map_object, next_addon, uid1, uid2 = struct.unpack_from(
            "<HBBBBBBBBHII", data, off
        )
        tiles.append(
            {
                "terrain": terrain,
                "object_name1": object_name1,
                "bottom_icn": bottom_icn,
                "quantity1": quantity1,
                "quantity2": quantity2,
                "object_name2": object_name2,
                "top_icn": top_icn,
                "terrain_flags": terrain_flags,
                "map_object": map_object,
                "next_addon": next_addon,
                "uid1": uid1,
                "uid2": uid2,
            }
        )

    addon_count = struct.unpack_from("<I", data, tiles_end)[0]
    addons_offset = tiles_end + 4
    addons_end = addons_offset + addon_count * MP2_ADDON_SIZE
    if len(data) < addons_end:
        raise ValueError(f"{path}: файл закончился до таблицы addon")

    addons = []
    for i in range(addon_count):
        off = addons_offset + i * MP2_ADDON_SIZE
        next_addon, object_name_n1_raw, bottom_icn, quantity_n, object_name_n2, top_icn, uid1, uid2 = struct.unpack_from("<HBBBBBII", data, off)
        addons.append(
            {
                "next_addon": next_addon,
                # fheroes2 умножает objectNameN1 на 2 при чтении addon.
                "object_name1": object_name_n1_raw * 2,
                "bottom_icn": bottom_icn,
                "quantity": quantity_n,
                "object_name2": object_name_n2,
                "top_icn": top_icn,
                "uid1": uid1,
                "uid2": uid2,
            }
        )

    header["addon_count"] = addon_count
    header["addons_offset"] = addons_offset

    return header, tiles, addons


def write_preview_map_binary(path: Path, header, tiles, addons):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fp:
        fp.write(b"H2MP")
        fp.write(struct.pack("<BBBBH", 2, header["width"], header["height"], header["difficulty"], header["tile_count"]))
        fp.write(struct.pack("<I", len(addons)))
        for tile in tiles:
            # Compact v2 хранит полный MP2 tile record, чтобы renderer мог
            # повторять object layer/order без обращения к исходному MX2.
            fp.write(
                struct.pack(
                    "<HBBBBBBBBHII",
                    tile["terrain"],
                    tile["object_name1"],
                    tile["bottom_icn"],
                    tile["quantity1"],
                    tile["quantity2"],
                    tile["object_name2"],
                    tile["top_icn"],
                    tile["terrain_flags"],
                    tile["map_object"],
                    tile["next_addon"],
                    tile["uid1"],
                    tile["uid2"],
                )
            )
        for addon in addons:
            fp.write(
                struct.pack(
                    "<HHBBBBII",
                    addon["next_addon"],
                    addon["object_name1"],
                    addon["bottom_icn"],
                    addon["quantity"],
                    addon["object_name2"],
                    addon["top_icn"],
                    addon["uid1"],
                    addon["uid2"],
                )
            )


def ground_parts_for_tile(tile, addons):
    parts = [
        {
            "object_name": tile["object_name1"],
            "icn_index": tile["bottom_icn"],
            "layer": tile["quantity1"] & 0x03,
            "uid": tile["uid1"],
        }
    ]
    addon_index = tile.get("next_addon", 0)
    guard = 0
    while 0 < addon_index < len(addons) and guard < 128:
        addon = addons[addon_index]
        parts.append(
            {
                "object_name": addon["object_name1"],
                "icn_index": addon["bottom_icn"],
                "layer": addon["quantity"] & 0x03,
                "uid": addon["uid1"],
            }
        )
        addon_index = addon["next_addon"]
        guard += 1

    return [part for part in parts if part["icn_index"] != 0xFF and (part["object_name"] >> 2) != 0]


def original_order_parts_for_tile(tile, addons):
    parts = ground_parts_for_tile(tile, addons)
    parts.sort(key=effective_part_layer, reverse=True)

    main = None
    for index in range(len(parts) - 1, -1, -1):
        if (parts[index]["object_name"] >> 2) == FLAG_ICN_TYPE:
            continue
        main = parts.pop(index)
        break

    return main, parts


def action_object_passability(map_object: int) -> int:
    if (map_object & OBJ_ACTION_OBJECT_TYPE) != OBJ_ACTION_OBJECT_TYPE:
        return DIRECTION_ALL8
    if map_object in ACTION_FULL_PASSABLE:
        return DIRECTION_ALL8
    return DIRECTION_CENTER_BOTTOM_ROWS8


def object_info_for_part(part):
    return OBJECT_INFO.get((part["object_name"] >> 2, part["icn_index"]))


def object_type_for_part(part) -> int:
    info = object_info_for_part(part)
    if info is None:
        return 0
    return info["object_type"]


def effective_part_layer(part) -> int:
    info = object_info_for_part(part)
    if info is None:
        return part["layer"]
    return info["layer"]


def part_is_top_level(part) -> bool:
    info = object_info_for_part(part)
    return info is not None and info["top"] != 0


def part_is_passability_transparent(part) -> bool:
    return part_is_top_level(part) or effective_part_layer(part) in (SHADOW_LAYER, TERRAIN_LAYER)


def object_part_passability(part) -> int:
    if part["icn_index"] == 0xFF:
        return DIRECTION_ALL8

    icn_type = part["object_name"] >> 2
    if icn_type in (ROAD_ICN_TYPE, STREAM_ICN_TYPE, FLAG_ICN_TYPE):
        return DIRECTION_ALL8

    object_type = object_type_for_part(part)
    if (object_type & OBJ_ACTION_OBJECT_TYPE) == OBJ_ACTION_OBJECT_TYPE:
        return action_object_passability(object_type)

    if object_type == OBJ_REEFS:
        return 0

    # Структура замка/города (OBJNTOWN, кроме входной дороги) — НЕПРОХОДИМА, включая
    # top-level башни. Раньше top-level части трактовались как «проходимый навес»
    # (как кроны деревьев) → герой залезал НА замок. Вход — отдельные дорожные
    # спрайты (OBJNTOWN_ROAD_SPRITES / OBJNTWRD), они остаются проходимы.
    if icn_type == OBJNTOWN_ICN_TYPE and part["icn_index"] not in OBJNTOWN_ROAD_SPRITES:
        return 0

    if part_is_passability_transparent(part):
        return DIRECTION_ALL8

    return DIRECTION_CENTER_BOTTOM_ROWS8


def tile_independent_passability(tile, addons):
    mask = DIRECTION_ALL8
    is_action = False
    main, ground = original_order_parts_for_tile(tile, addons)

    if main is not None:
        mask &= object_part_passability(main)
        is_action = (object_type_for_part(main) & OBJ_ACTION_OBJECT_TYPE) == OBJ_ACTION_OBJECT_TYPE
        if is_action:
            return mask & 0xFF

    for part in reversed(ground):
        mask &= object_part_passability(part)
    return mask & 0xFF


def tile_is_water(tile) -> bool:
    return tile["terrain"] < GRASS_START_IMAGE_INDEX


def terrain_penalty(terrain_image_index: int) -> int:
    if terrain_image_index < GRASS_START_IMAGE_INDEX:
        return 100
    if terrain_image_index < SNOW_START_IMAGE_INDEX:
        return 100
    if terrain_image_index < SWAMP_START_IMAGE_INDEX:
        return 150
    if terrain_image_index < LAVA_START_IMAGE_INDEX:
        return 175
    if terrain_image_index < DESERT_START_IMAGE_INDEX:
        return 100
    if terrain_image_index < DIRT_START_IMAGE_INDEX:
        return 200
    if terrain_image_index < WASTELAND_START_IMAGE_INDEX:
        return 100
    if terrain_image_index < BEACH_START_IMAGE_INDEX:
        return 125
    if terrain_image_index < MAX_GROUND_IMAGE_INDEX:
        return 125
    return 100


def is_sprite_road(icn_type: int, image_index: int) -> bool:
    if icn_type == ROAD_ICN_TYPE:
        return image_index in ROAD_SPRITES
    if icn_type == OBJNTOWN_ICN_TYPE:
        return image_index in OBJNTOWN_ROAD_SPRITES
    if icn_type == OBJNTWRD_ICN_TYPE:
        return image_index in OBJNTWRD_ROAD_SPRITES
    return False


def tile_is_road(tile, addons) -> bool:
    main, ground = original_order_parts_for_tile(tile, addons)
    parts = ([main] if main is not None else []) + ground
    for part in parts:
        if is_sprite_road(part["object_name"] >> 2, part["icn_index"]):
            return True
    return False


def tile_object_type(tile, addons) -> int:
    main, _ground = original_order_parts_for_tile(tile, addons)
    if main is not None:
        object_type = object_type_for_part(main)
        if object_type != 0:
            return object_type
    return tile["map_object"]


def base_action_type(object_type: int) -> int:
    if (object_type & OBJ_ACTION_OBJECT_TYPE) == OBJ_ACTION_OBJECT_TYPE:
        return object_type
    return object_type | OBJ_ACTION_OBJECT_TYPE


def is_off_game_action(object_type: int) -> bool:
    return (object_type & OBJ_ACTION_OBJECT_TYPE) == OBJ_ACTION_OBJECT_TYPE


def is_path_walkthrough_blocked(object_type: int) -> bool:
    if object_type in (OBJ_HERO, OBJ_MONSTER, OBJ_BOAT):
        return True
    return (object_type & OBJ_ACTION_OBJECT_TYPE) == OBJ_ACTION_OBJECT_TYPE and object_type != OBJ_EVENT


def is_short_object(object_type: int) -> bool:
    return object_type in SHORT_OBJECT_TYPES or (object_type & ~OBJ_ACTION_OBJECT_TYPE) in SHORT_OBJECT_TYPES


def is_detached_object(object_type: int) -> bool:
    return object_type in DETACHED_OBJECT_TYPES or (object_type & ~OBJ_ACTION_OBJECT_TYPE) in DETACHED_OBJECT_TYPES


def is_combined_object(object_type: int) -> bool:
    return object_type in COMBINED_OBJECT_TYPES or (object_type & ~OBJ_ACTION_OBJECT_TYPE) in COMBINED_OBJECT_TYPES


def part_affects_passability(part) -> bool:
    icn_type = part["object_name"] >> 2
    return (
        not part_is_passability_transparent(part)
        and icn_type not in (ROAD_ICN_TYPE, STREAM_ICN_TYPE, FLAG_ICN_TYPE)
    )


def tile_is_shadow_only(main, ground) -> bool:
    if main is not None and not part_is_passability_transparent(main):
        return False
    return all(part_is_passability_transparent(part) for part in ground)


def tile_has_uid(tile, addons, uid) -> bool:
    main, ground = original_order_parts_for_tile(tile, addons)
    if main is not None and main["uid"] == uid:
        return True
    return any(part["uid"] == uid for part in ground)


def tile_has_castle_structure(tile, addons) -> bool:
    """Тайл содержит структуру замка/города OBJNTOWN (стена/башня), НЕ входную
    дорогу — в низ-частях ИЛИ в top-частях. Структура замка непроходима целиком,
    включая тайлы под башнями-навесами (top-level), которые иначе трактовались бы
    как «проходимый навес» (как кроны деревьев) → герой залезал на замок."""
    def is_struct(object_name: int, icn_index: int) -> bool:
        return (
            icn_index != 0xFF
            and (object_name >> 2) == OBJNTOWN_ICN_TYPE
            and icn_index not in OBJNTOWN_ROAD_SPRITES
        )

    # низ-части (object_name1)
    for part in ground_parts_for_tile(tile, addons):
        if is_struct(part["object_name"], part["icn_index"]):
            return True
    # top-части (object_name2) тайла и аддонов
    if is_struct(tile["object_name2"], tile["top_icn"]):
        return True
    addon_index = tile.get("next_addon", 0)
    guard = 0
    while 0 < addon_index < len(addons) and guard < 128:
        addon = addons[addon_index]
        if is_struct(addon["object_name2"], addon["top_icn"]):
            return True
        addon_index = addon["next_addon"]
        guard += 1
    return False


def tile_contains_any_icn(tile, addons, icn_types) -> bool:
    main, ground = original_order_parts_for_tile(tile, addons)
    if main is not None and (main["object_name"] >> 2) in icn_types:
        return True
    return any((part["object_name"] >> 2) in icn_types for part in ground)


def tile_has_tall_object(tile, addons, width, index, tiles):
    if index < width:
        return False
    main, ground = original_order_parts_for_tile(tile, addons)
    uids = []
    if main is not None and part_affects_passability(main):
        uids.append(main["uid"])
    for part in ground:
        if part_affects_passability(part):
            uids.append(part["uid"])
    if not uids:
        return False
    top_tile = tiles[index - width]
    top_main, top_ground = original_order_parts_for_tile(top_tile, addons)
    top_parts = ([top_main] if top_main is not None else []) + top_ground
    return any(part["uid"] in uids for part in top_parts)


def update_passability_for_tile(tiles, addons, width, index, independent_masks):
    mask = independent_masks[index]
    if mask == 0:
        return 0

    x = index % width
    y = index // width
    height = len(tiles) // width
    tile = tiles[index]

    if (mask & DIRECTION_TOP_LEFT) and x > 0:
        left_index = index - 1
        if tile_has_tall_object(tiles[left_index], addons, width, left_index, tiles) and (independent_masks[left_index] & DIRECTION_TOP) == 0:
            mask &= ~DIRECTION_TOP_LEFT

    if (mask & DIRECTION_TOP_RIGHT) and x + 1 < width:
        right_index = index + 1
        if tile_has_tall_object(tiles[right_index], addons, width, right_index, tiles) and (independent_masks[right_index] & DIRECTION_TOP) == 0:
            mask &= ~DIRECTION_TOP_RIGHT

    object_type = tile_object_type(tile, addons)
    if is_off_game_action(object_type):
        return mask & 0xFF

    main, ground = original_order_parts_for_tile(tile, addons)
    if tile_is_shadow_only(main, ground):
        return mask & 0xFF
    if main is None or part_is_passability_transparent(main):
        return mask & 0xFF

    if y + 1 >= height:
        return 0

    bottom_index = index + width
    bottom_tile = tiles[bottom_index]
    if not tile_is_water(tile) and tile_is_water(bottom_tile):
        return 0

    tile_uids = [main["uid"]]
    tile_uids.extend(part["uid"] for part in ground if part_affects_passability(part))
    for uid in tile_uids:
        if uid and tile_has_uid(bottom_tile, addons, uid):
            return 0

    bottom_type = tile_object_type(bottom_tile, addons)
    if is_off_game_action(bottom_type) and (independent_masks[bottom_index] & DIRECTION_TOP):
        return mask & 0xFF

    valid_bottom_layer_objects = sum(1 for part in ground if part_affects_passability(part))
    bottom_main, _ = original_order_parts_for_tile(bottom_tile, addons)
    bottom_main_icn = (bottom_main["object_name"] >> 2) if bottom_main is not None else 0
    main_icn = main["object_name"] >> 2
    single_object_tile = valid_bottom_layer_objects == 0 and bottom_main_icn != main_icn

    if (
        not single_object_tile
        and not is_detached_object(object_type)
        and bottom_main is not None
        and not part_is_passability_transparent(bottom_main)
    ):
        corrected_bottom_type = base_action_type(bottom_type)
        if is_off_game_action(bottom_type) or is_off_game_action(corrected_bottom_type):
            if not is_short_object(bottom_type) and not is_short_object(corrected_bottom_type):
                return 0
        else:
            current_icns = {main_icn}
            current_icns.update(part["object_name"] >> 2 for part in ground)
            if not (
                is_short_object(bottom_type)
                or (
                    not tile_contains_any_icn(bottom_tile, addons, current_icns)
                    and (is_combined_object(object_type) or is_combined_object(bottom_type))
                )
            ):
                return 0

    return mask & 0xFF


def build_passability(header, tiles, addons):
    width = header["width"]
    independent = []
    for tile in tiles:
        if tile["terrain"] < GRASS_START_IMAGE_INDEX:
            independent.append(0)
            continue
        independent.append(tile_independent_passability(tile, addons))

    masks = bytearray()
    for index, tile in enumerate(tiles):
        mask = update_passability_for_tile(tiles, addons, width, index, independent)
        # Футпринт структуры замка непроходим ЦЕЛИКОМ (включая тайлы под башнями-
        # навесами top-level). Вход — дорожные спрайты — остаётся проходим.
        if tile_has_castle_structure(tile, addons):
            mask = 0
        # Гейт замка (action-вход) — проходим (вход; герой стоит на нём и выходит
        # вниз). Иначе MAIN-часть гейта (town basement) делает его 00 → герой заперт.
        if tile["map_object"] in CASTLE_ENTRANCE_OBJECTS:
            mask = action_object_passability(tile["map_object"])
        masks.append(mask)
    return bytes(masks)


def build_path_metadata(header, tiles, addons) -> bytes:
    costs = bytearray()
    flags = bytearray()
    for tile in tiles:
        object_type = tile_object_type(tile, addons)
        tile_flags = 0
        if tile_is_water(tile):
            tile_flags |= PATH_FLAG_WATER
        if tile_is_road(tile, addons):
            tile_flags |= PATH_FLAG_ROAD
        if is_path_walkthrough_blocked(object_type):
            tile_flags |= PATH_FLAG_STOP
        costs.append(terrain_penalty(tile["terrain"]))
        flags.append(tile_flags)
    if len(costs) != header["tile_count"] or len(flags) != header["tile_count"]:
        raise ValueError("path metadata size mismatch")
    return bytes(costs + flags)


def write_passability_binary(path: Path, passability: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(passability)


def write_path_metadata_binary(path: Path, metadata: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(metadata)


def write_manifest(path: Path, header, tiles, passability, path_metadata):
    path.parent.mkdir(parents=True, exist_ok=True)
    object_counts = {}
    terrain_counts = {}
    passability_counts = {}
    path_cost_counts = {}
    path_flag_counts = {}
    for tile in tiles:
        object_counts[str(tile["map_object"])] = object_counts.get(str(tile["map_object"]), 0) + 1
        terrain_counts[str(tile["terrain"])] = terrain_counts.get(str(tile["terrain"]), 0) + 1
    for mask in passability:
        key = f"{mask:02X}"
        passability_counts[key] = passability_counts.get(key, 0) + 1
    tile_count = header["tile_count"]
    for cost in path_metadata[:tile_count]:
        path_cost_counts[str(cost)] = path_cost_counts.get(str(cost), 0) + 1
    for flags in path_metadata[tile_count:]:
        key = f"{flags:02X}"
        path_flag_counts[key] = path_flag_counts.get(key, 0) + 1

    manifest = {
        **header,
        "unique_terrain_tiles": len(terrain_counts),
        "unique_object_types": len(object_counts),
        "unique_passability_masks": len(passability_counts),
        "object_counts": dict(sorted(object_counts.items(), key=lambda item: int(item[0]))),
        "terrain_counts": dict(sorted(terrain_counts.items(), key=lambda item: int(item[0]))),
        "passability_counts": dict(sorted(passability_counts.items())),
        "path_cost_counts": dict(sorted(path_cost_counts.items(), key=lambda item: int(item[0]))),
        "path_flag_counts": dict(sorted(path_flag_counts.items())),
    }
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_include(path: Path, symbol_prefix: str, header, map_binary: Path, pass_binary: Path, path_binary: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    size = map_binary.stat().st_size
    pass_size = pass_binary.stat().st_size
    path_size = path_binary.stat().st_size
    text = f"""; Сгенерировано Source/Tools/map_tools.py
{symbol_prefix}_W         EQU {header["width"]}
{symbol_prefix}_H         EQU {header["height"]}
{symbol_prefix}_TILES     EQU {header["tile_count"]}
{symbol_prefix}_BIN_SIZE  EQU {size}
{symbol_prefix}_SPG_PAGE  EQU #10
{symbol_prefix}_SPG_ADDR  EQU #0000
{symbol_prefix}_PASS_SIZE EQU {pass_size}
{symbol_prefix}_PASS_PAGE EQU #{PASSABILITY_PAGE:02X}
{symbol_prefix}_PASS_ADDR EQU #0000
{symbol_prefix}_PATH_SIZE EQU {path_size}
{symbol_prefix}_PATH_PAGE EQU #{PATH_METADATA_PAGE:02X}
{symbol_prefix}_PATH_ADDR EQU #0000
{symbol_prefix}_PATH_COST_ADDR EQU {symbol_prefix}_PATH_ADDR
{symbol_prefix}_PATH_FLAGS_ADDR EQU {symbol_prefix}_PATH_ADDR + {symbol_prefix}_TILES
"""
    path.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Конвертировать карты Heroes II MP2/MX2 для preview-рендера TS-Config.")
    parser.add_argument("map", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("Assets/Converted/Maps"))
    parser.add_argument("--include", type=Path, default=Path("Source/ASM/generated_map.inc"))
    parser.add_argument("--symbol-prefix", default="MAP0")
    args = parser.parse_args()

    header, tiles, addons = read_mp2(args.map)
    stem = args.map.stem.upper()
    bin_path = args.out_dir / f"{stem}.map.bin"
    pass_path = args.out_dir / f"{stem}.pass.bin"
    path_path = args.out_dir / f"{stem}.path.bin"
    manifest_path = args.out_dir / f"{stem}.manifest.json"

    write_preview_map_binary(bin_path, header, tiles, addons)
    passability = build_passability(header, tiles, addons)
    path_metadata = build_path_metadata(header, tiles, addons)
    write_passability_binary(pass_path, passability)
    write_path_metadata_binary(path_path, path_metadata)
    write_manifest(manifest_path, header, tiles, passability, path_metadata)
    write_include(args.include, args.symbol_prefix, header, bin_path, pass_path, path_path)

    print(f"{args.map.name}: {header['name']} {header['width']}x{header['height']}, тайлов={header['tile_count']}")
    print(f"addon-записей: {len(addons)}")
    print(f"бинарная карта: {bin_path} ({bin_path.stat().st_size} байт)")
    print(f"проходимость: {pass_path} ({pass_path.stat().st_size} байт)")
    print(f"path metadata: {path_path} ({path_path.stat().st_size} байт)")
    print(f"манифест: {manifest_path}")
    print(f"include-файл: {args.include}")


if __name__ == "__main__":
    main()
