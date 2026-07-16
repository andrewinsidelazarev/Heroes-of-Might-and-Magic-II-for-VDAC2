#!/usr/bin/env python3
"""Сборка ассетов и стартового файла HiScores для HMM2 VDAC2.

Экран повторяет game_highscores.cpp: HSBKG[0], HISCORE[6/7], кнопки из
HISCORE[0..5], MINIMON[*9 + 0..6] и таблица из 10+10 записей.

Данные таблицы не входят в PAK. Mutable-файл HMM2.HGS создается отдельно:
2048 байт = два encoded A/B слота по 1024 байта.
"""
from __future__ import annotations

import argparse
import binascii
import struct
from pathlib import Path

from agg_tools import read_agg_index_with_expansion
from object_atlas import agg_entry, read_icn, read_palette
from pak_builder import SECTOR, TYPE_RAMG_BLOB, build_pak
from viewport_pack import (
    align,
    crop_indices,
    decode_icn_indices,
    palette_argb4444,
    palette_argb4444_opaque,
    split_ui_blits,
)


ROOT = Path(__file__).resolve().parents[2]
AGG_PATH = ROOT / "Assets" / "Original" / "DATA" / "HEROES2.AGG"
PAK_PATH = ROOT / "Build" / "HMM2HISC.PAK"
HGS_PATH = ROOT / "Build" / "HMM2.HGS"
ASM_INC = ROOT / "Source" / "ASM" / "generated_hiscores.inc"
ASM_META_INC = ROOT / "Source" / "ASM" / "generated_hiscores_meta.inc"

HS_RAMG_BASE = 0x000000
TRANSPARENT = 0

HS_ENTRY_SIZE = 48
HS_ENTRY_COUNT = 10
HS_SLOT_SIZE = 1024
HS_FILE_SIZE = HS_SLOT_SIZE * 2
HS_HEADER_SIZE = 64
HS_MAGIC = b"H2HS"
HS_VERSION = 1
HS_XOR_KEY = 0x48324A53
HS_NATIVE_TEXT_FONT_SIZE = 22

MONSTER_IDS_IN_RANKING = [
    1, 12, 21, 39, 30, 58, 48, 13, 49, 2, 3, 40, 22, 50, 14, 24, 31,
    4, 25, 23, 59, 5, 15, 51, 41, 52, 16, 32, 6, 26, 42, 7, 63, 27,
    65, 61, 53, 66, 62, 43, 33, 8, 18, 44, 60, 55, 17, 34, 9, 19,
    54, 45, 56, 28, 35, 10, 64, 11, 20, 46, 29, 57, 36, 37, 47, 38,
]

DEFAULT_STANDARD = [
    ("Lord Kilburn", "Beltway", 70, 150),
    ("Tsabu", "Deathgate", 80, 140),
    ("Sir Galant", "Enroth", 90, 130),
    ("Thundax", "Lost Continent", 100, 120),
    ("Lord Haart", "Mountain King", 120, 110),
    ("Ariel", "Pandemonium", 140, 100),
    ("Rebecca", "Terra Firma", 160, 90),
    ("Sandro", "The Clearing", 180, 80),
    ("Crodo", "Vikings!", 200, 70),
    ("Barock", "Wastelands", 240, 60),
]

DEFAULT_CAMPAIGN = [
    ("Antoine", "Roland", 600, 600),
    ("Astra", "Archibald", 650, 650),
    ("Agar", "Roland", 700, 700),
    ("Vatawna", "Archibald", 750, 750),
    ("Vesper", "Roland", 800, 800),
    ("Ambrose", "Archibald", 850, 850),
    ("Troyan", "Roland", 900, 900),
    ("Jojosh", "Archibald", 1000, 1000),
    ("Wrathmont", "Roland", 2000, 2000),
    ("Maximus", "Archibald", 3000, 3000),
]


def _frame(icn, idx: int) -> dict:
    header, encoded = icn[idx]
    return {
        "ox": int(header["ox"]),
        "oy": int(header["oy"]),
        "w": int(header["w"]),
        "h": int(header["h"]),
        "indices": decode_icn_indices(header, encoded),
    }


def _put(payload: bytearray, raw: bytes) -> int:
    addr = HS_RAMG_BASE + align(len(payload), 4)
    while HS_RAMG_BASE + len(payload) < addr:
        payload.append(0)
    payload.extend(raw)
    return addr


def _split_frame(sprite: dict, dst_x: int, dst_y: int) -> list[dict]:
    parts = []
    for sx, sy, w, h, dx, dy in split_ui_blits([(0, 0, sprite["w"], sprite["h"], dst_x, dst_y)]):
        parts.append(
            {
                "indices": crop_indices(sprite["indices"], sprite["w"], sx, sy, w, h),
                "w": w,
                "h": h,
                "x": dx,
                "y": dy,
            }
        )
    return parts


def _nearest_palette_index(palette: list[tuple[int, int, int]], target: tuple[int, int, int]) -> int:
    best_i = 1
    best_d = 1 << 30
    tr, tg, tb = target
    for i, (r, g, b) in enumerate(palette):
        if i == TRANSPARENT:
            continue
        d = (r - tr) * (r - tr) + (g - tg) * (g - tg) + (b - tb) * (b - tb)
        if d < best_d:
            best_i = i
            best_d = d
    return best_i


def _load_font(size: int):
    try:
        from PIL import ImageFont

        candidates = [
            Path(r"C:\Windows\Fonts\tahoma.ttf"),
            Path(r"C:\Windows\Fonts\arial.ttf"),
            Path(r"C:\Windows\Fonts\segoeui.ttf"),
        ]
        for path in candidates:
            if path.exists():
                return ImageFont.truetype(str(path), size=size)
        return ImageFont.load_default()
    except Exception:
        return None


def _build_glyphs(payload: bytearray, white_idx: int, yellow_idx: int) -> list[dict]:
    try:
        from PIL import Image, ImageDraw
    except Exception as exc:  # pragma: no cover - на build-машине PIL обычно есть
        raise RuntimeError("Pillow is required for HiScores glyph atlas") from exc

    font = _load_font(HS_NATIVE_TEXT_FONT_SIZE)
    if font is None:
        raise RuntimeError("Unable to load a font for HiScores glyph atlas")

    compact: list[dict] = []
    for code in range(32, 127):
        ch = chr(code)
        if ch == " ":
            compact.append({"white": 0, "yellow": 0, "w": 1, "h": 1, "adv": 4, "oy": 0})
            continue

        bbox = font.getbbox(ch)
        w = max(1, bbox[2] - bbox[0] + 2)
        h = max(1, bbox[3] - bbox[1] + 4)
        img = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(img)
        draw.text((1 - bbox[0], 1 - bbox[1]), ch, font=font, fill=255)
        mask = img.tobytes()

        pair = []
        for color_idx in (white_idx, yellow_idx):
            raw = bytearray()
            for alpha in mask:
                raw.append(color_idx if alpha >= 96 else 0)
            addr = _put(payload, bytes(raw))
            pair.append(addr)
        compact.append(
            {
                "white": pair[0],
                "yellow": pair[1],
                "w": w,
                "h": h,
                "adv": max(1, w - 1),
                "oy": 0,
            }
        )
    return compact


def _pack_entry(name: str, scenario: str, days: int, rating: int, seed: int = 0) -> bytes:
    out = bytearray(HS_ENTRY_SIZE)
    out[0:16] = name.encode("ascii", errors="replace")[:15].ljust(16, b"\0")
    out[16:36] = scenario.encode("ascii", errors="replace")[:19].ljust(20, b"\0")
    struct.pack_into("<HHII", out, 36, days & 0xFFFF, rating & 0xFFFF, 0, seed & 0xFFFFFFFF)
    return bytes(out)


def _crc32(data: bytes) -> int:
    return binascii.crc32(data) & 0xFFFFFFFF


def _tag(data: bytes, generation: int, slot_id: int) -> int:
    tag = 0xA5C35A7D ^ generation ^ (slot_id * 0x45D9F3B)
    for b in data:
        tag = ((tag << 5) | (tag >> 27)) & 0xFFFFFFFF
        tag ^= (b + 0x9E3779B9) & 0xFFFFFFFF
    return tag


def _encode_slot(plain: bytes, slot_id: int) -> bytes:
    seed = (HS_XOR_KEY ^ (slot_id * 0x45D9F3B)) & 0xFFFFFFFF
    out = bytearray(len(plain))
    for i, b in enumerate(plain):
        seed = (1664525 * seed + 1013904223) & 0xFFFFFFFF
        mask = ((seed >> 24) ^ (i * 37) ^ (i >> 3)) & 0xFF
        rot = (i + slot_id) & 7
        v = b ^ mask
        out[i] = ((v << rot) | (v >> (8 - rot))) & 0xFF if rot else v
    return bytes(out)


def _plain_slot(slot_id: int, generation: int) -> bytes:
    payload = bytearray()
    for entry in DEFAULT_STANDARD:
        payload.extend(_pack_entry(*entry))
    for entry in DEFAULT_CAMPAIGN:
        payload.extend(_pack_entry(*entry))
    payload.extend(b"\0" * (HS_SLOT_SIZE - HS_HEADER_SIZE - len(payload)))

    header = bytearray(HS_HEADER_SIZE)
    header[0:4] = HS_MAGIC
    header[4] = HS_VERSION
    header[5] = slot_id
    header[6] = HS_ENTRY_SIZE
    header[7] = HS_ENTRY_COUNT
    header[8] = HS_ENTRY_COUNT
    struct.pack_into("<I", header, 12, generation)
    struct.pack_into("<I", header, 16, _crc32(payload))
    struct.pack_into("<I", header, 20, _tag(payload, generation, slot_id))
    return bytes(header) + bytes(payload)


def build_hgs(path: Path) -> None:
    # slot A valid, slot B старше на тот же payload: загрузчик выберет generation=2.
    data = _encode_slot(_plain_slot(0, 1), 0) + _encode_slot(_plain_slot(1, 2), 1)
    assert len(data) == HS_FILE_SIZE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def build_assets() -> dict:
    agg, entries = read_agg_index_with_expansion(AGG_PATH)
    palette = read_palette(agg_entry(agg, entries, "KB.PAL"))

    hsbkg = read_icn(agg_entry(agg, entries, "HSBKG.ICN"))
    hiscore = read_icn(agg_entry(agg, entries, "HISCORE.ICN"))
    minimon = read_icn(agg_entry(agg, entries, "MINIMON.ICN"))

    payload = bytearray()
    transparent_addr = _put(payload, palette_argb4444(palette))
    opaque_addr = _put(payload, palette_argb4444_opaque(palette))

    bg = _frame(hsbkg, 0)
    bg_parts = _split_frame(bg, 0, 0)
    for part in bg_parts:
        part["addr"] = _put(payload, part["indices"])

    titles = {
        "standard": _split_frame(_frame(hiscore, 6), 50, 31),
        "campaign": _split_frame(_frame(hiscore, 7), 50, 31),
    }
    for parts in titles.values():
        for part in parts:
            part["addr"] = _put(payload, part["indices"])

    # HISCORE[0/1] campaign, [2/3] standard, [4/5] exit. Кнопки рисуются в
    # координаты Button(x,y), offset ICN тут не используется.
    buttons = {}
    for name, base, x in (("campaign", 0, 8), ("standard", 2, 8), ("exit", 4, 604)):
        buttons[name] = []
        for frame in (base, base + 1):
            spr = _frame(hiscore, frame)
            raw = spr["indices"]
            buttons[name].append({"addr": _put(payload, raw), "w": spr["w"], "h": spr["h"], "x": x, "y": 315})

    monsters: dict[int, list[dict]] = {}
    for monster_id in MONSTER_IDS_IN_RANKING:
        frames = []
        base = (monster_id - 1) * 9
        for frame in range(7):
            spr = _frame(minimon, base + frame)
            frames.append(
                {
                    "addr": _put(payload, spr["indices"]),
                    "w": spr["w"],
                    "h": spr["h"],
                    "ox": spr["ox"],
                    "oy": spr["oy"],
                }
            )
        monsters[monster_id] = frames

    white_idx = _nearest_palette_index(palette, (255, 255, 255))
    yellow_idx = _nearest_palette_index(palette, (255, 225, 48))
    glyphs = _build_glyphs(payload, white_idx, yellow_idx)

    summary = build_pak([{"type": TYPE_RAMG_BLOB, "target": HS_RAMG_BASE, "data": bytes(payload)}], PAK_PATH)
    pak = {
        "payload_bytes": len(payload),
        "payload_sectors": (len(payload) + SECTOR - 1) // SECTOR,
        "body_start_sector": summary["body_start_sector"],
        "total_bytes": summary["total_bytes"],
    }
    return {
        "bg": bg_parts,
        "titles": titles,
        "buttons": buttons,
        "monsters": monsters,
        "glyphs": glyphs,
        "pak": pak,
        "transparent_addr": transparent_addr,
        "opaque_addr": opaque_addr,
    }


def _c_sprite(item: dict) -> str:
    return (
        "{"
        f"0x{item['addr'] & 0xFFFF:04X},0x{(item['addr'] >> 16) & 0xFF:02X},"
        f"{item['w']},{item['h']},{item.get('x', item.get('ox', 0))},{item.get('y', item.get('oy', 0))}"
        "}"
    )


def _scaled_px(value: int) -> int:
    return (value * 8 + 4) // 5


def _asm_word(value: int) -> str:
    return f"#{value & 0xFFFF:04X}"


def _asm_sprite(item: dict) -> list[str]:
    x = int(item.get("x", item.get("ox", 0)))
    y = int(item.get("y", item.get("oy", 0)))
    w = int(item["w"])
    h = int(item["h"])
    addr = int(item["addr"])
    return [
        f"                DEFW {_asm_word(addr)}",
        f"                DEFB #{(addr >> 16) & 0xFF:02X}",
        f"                DEFW {w}, {h}, {_scaled_px(w)}, {_scaled_px(h)}, {_asm_word(x)}, {_asm_word(y)}",
    ]


def _monster_by_rating(rating: int) -> int:
    threshold = 0
    step = 0
    for monster in MONSTER_IDS_IN_RANKING:
        if monster == 1:
            step = 3
        elif monster == 12:
            step = 4
        elif monster == 27:
            step = 3
        elif monster == 38:
            step = 1
        threshold += step
        if rating <= threshold:
            return MONSTER_IDS_IN_RANKING.index(monster)
    return len(MONSTER_IDS_IN_RANKING) - 1


def _monster_by_day(days: int) -> int:
    threshold = 0
    step = 0
    for i in range(len(MONSTER_IDS_IN_RANKING) - 1, -1, -1):
        monster = MONSTER_IDS_IN_RANKING[i]
        if monster == 38:
            step = 300
        elif monster == 47:
            step = 20
        elif monster == 26:
            step = 100
        elif monster == 23:
            step = 200
        elif monster == 1:
            step = 1
        threshold += step
        if days <= threshold:
            return i
    return 0


def emit_asm_meta(data: dict) -> None:
    lines: list[str] = [
        "; Сгенерировано Source/Tools/hiscores_pack.py.",
        "                ifndef _HMM2_GENERATED_HISCORES_META_",
        "                define _HMM2_GENERATED_HISCORES_META_",
        "",
    ]

    def sprite_table(label: str, items: list[dict]) -> None:
        lines.append(f"{label}:")
        for item in items:
            lines.extend(_asm_sprite(item))
        lines.append("")

    sprite_table("HsBgTable", data["bg"])
    sprite_table("HsTitleStandardTable", data["titles"]["standard"])
    sprite_table("HsTitleCampaignTable", data["titles"]["campaign"])
    sprite_table("HsButtonCampaignTable", data["buttons"]["campaign"])
    sprite_table("HsButtonStandardTable", data["buttons"]["standard"])
    sprite_table("HsButtonExitTable", data["buttons"]["exit"])

    lines.append("HsMonsterTable:")
    for monster_id in MONSTER_IDS_IN_RANKING:
        for frame in data["monsters"][monster_id]:
            lines.extend(_asm_sprite(frame))
    lines.append("")

    lines.append("HsGlyphTable:")
    for g in data["glyphs"]:
        w = int(g["w"])
        h = int(g["h"])
        lines.append(f"                DEFW {_asm_word(g['white'])}")
        lines.append(f"                DEFB #{(g['white'] >> 16) & 0xFF:02X}")
        lines.append(f"                DEFW {_asm_word(g['yellow'])}")
        lines.append(f"                DEFB #{(g['yellow'] >> 16) & 0xFF:02X}")
        lines.append(f"                DEFB {w}, {h}, {w}, {h}, {int(g['adv'])}, {int(g['oy']) & 0xFF}")
    lines.append("")

    def emit_string_table(prefix: str, entries: list[tuple[str, str, int, int]]) -> None:
        for i, (player, scenario, _days, _rating) in enumerate(entries):
            safe_player = player.replace('"', "'")
            safe_scenario = scenario.replace('"', "'")
            lines.append(f"{prefix}Player{i}: DEFB \"{safe_player}\", 0")
            lines.append(f"{prefix}Scenario{i}: DEFB \"{safe_scenario}\", 0")
        lines.append(f"{prefix}Rows:")
        for i, (_player, _scenario, days, rating) in enumerate(entries):
            rank = _monster_by_day(rating) if prefix == "HsCampaign" else _monster_by_rating(rating)
            monster0 = f"HsMonsterTable + {(rank * 7 + 0) * 15}"
            monster1 = f"HsMonsterTable + {(rank * 7 + 1) * 15}"
            lines.append(
                f"                DEFW {prefix}Player{i}, {prefix}Scenario{i}, {days}, {rating}, {monster0}, {monster1}"
            )
        lines.append("")

    emit_string_table("HsStandard", DEFAULT_STANDARD)
    emit_string_table("HsCampaign", DEFAULT_CAMPAIGN)

    lines.append("                endif")
    ASM_META_INC.parent.mkdir(parents=True, exist_ok=True)
    ASM_META_INC.write_text("\n".join(lines), encoding="utf-8")


def emit_asm_inc(data: dict) -> None:
    pak = data["pak"]
    lines = [
        "; Сгенерировано Source/Tools/hiscores_pack.py.",
        "                ifndef _HMM2_GENERATED_HISCORES_",
        "                define _HMM2_GENERATED_HISCORES_",
        "",
        f"HISCORES_PAYLOAD_BYTES   EQU {pak['payload_bytes']}",
        f"HISCORES_PAYLOAD_SECTORS EQU {pak['payload_sectors']}",
        f"HISCORES_BODY_SECTOR     EQU {pak['body_start_sector']}",
        "HS_SPRITE_ENTRY_SIZE     EQU 15",
        "HS_GLYPH_ENTRY_SIZE      EQU 12",
        "HS_ROW_ENTRY_SIZE        EQU 12",
        f"HS_TRANSPARENT_PAL_LO    EQU {_asm_word(data['transparent_addr'])}",
        f"HS_TRANSPARENT_PAL_HI    EQU #{(data['transparent_addr'] >> 16) & 0xFF:02X}",
        f"HS_OPAQUE_PAL_LO         EQU {_asm_word(data['opaque_addr'])}",
        f"HS_OPAQUE_PAL_HI         EQU #{(data['opaque_addr'] >> 16) & 0xFF:02X}",
        f"HsBgTable_COUNT          EQU {len(data['bg'])}",
        f"HsTitleStandardTable_COUNT EQU {len(data['titles']['standard'])}",
        f"HsTitleCampaignTable_COUNT EQU {len(data['titles']['campaign'])}",
        f"HsButtonCampaignTable_COUNT EQU {len(data['buttons']['campaign'])}",
        f"HsButtonStandardTable_COUNT EQU {len(data['buttons']['standard'])}",
        f"HsButtonExitTable_COUNT  EQU {len(data['buttons']['exit'])}",
        'HiScoresPakName:         DEFB "HMM2HISC.PAK", 0',
        'HiScoresHgsName:         DEFB "HMM2.HGS", 0',
        'HiScoresMetaName:        DEFB "HMM2HISC.MTA", 0',
        "",
        "                endif",
    ]
    ASM_INC.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build HiScores PAK, C metadata and default HMM2.HGS.")
    parser.add_argument("--no-hgs", action="store_true", help="Do not regenerate Build/HMM2.HGS")
    args = parser.parse_args()

    data = build_assets()
    emit_asm_inc(data)
    emit_asm_meta(data)
    if not args.no_hgs:
        build_hgs(HGS_PATH)

    pak = data["pak"]
    print(
        f"hiscores pack -> {PAK_PATH.name}: payload={pak['payload_bytes']} bytes "
        f"({pak['payload_sectors']} sectors), PAK={pak['total_bytes']} bytes"
    )
    print(f"  inc: {ASM_INC}")
    print(f"  asm-meta: {ASM_META_INC}")
    if not args.no_hgs:
        print(f"  hgs: {HGS_PATH} ({HS_FILE_SIZE} bytes, encoded A/B slots)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
