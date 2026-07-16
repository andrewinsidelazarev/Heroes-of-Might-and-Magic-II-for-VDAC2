#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from hmm2_ft812_snapshot import HMM2FullZ80Emulator, ROOT, attach_hmm2_shadow
from shadow_ft812 import disasm_dl
from shadow_ft812 import REG_HSIZE, REG_PCLK, REG_VSIZE


ATLAS_DIR = ROOT / "Assets" / "Converted" / "Terrain"
BACKGROUND_DIR = ROOT / "Assets" / "Converted" / "Background"
OBJECT_DIR = ROOT / "Assets" / "Converted" / "Objects"


def read_equ(path: Path, name: str) -> int:
    rx = re.compile(rf"^\s*{re.escape(name)}\s+EQU\s+(.+?)\s*$", re.I)
    with path.open("r", encoding="utf-8", errors="replace") as fp:
        for line in fp:
            m = rx.match(line)
            if not m:
                continue
            value = m.group(1).strip()
            if value.startswith("#"):
                return int(value[1:], 16)
            return int(value, 0)
    raise ValueError(f"{path}: нет {name}")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def read_expected_chunks(directory: Path, pattern: str, size: int) -> bytes:
    def chunk_index(path: Path) -> int:
        m = re.search(r"_p(\d+)\.bin$", path.name, re.I)
        return int(m.group(1)) if m else 0

    out = bytearray()
    for path in sorted(directory.glob(pattern), key=chunk_index):
        out.extend(path.read_bytes())
    return bytes(out[:size])


def expected_composite_cache(full_tiles: bytes, map_w: int, view_w: int, view_h: int, split_x: int, tile_bytes: int, palette_size: int, tile_offset: int) -> bytes:
    out = bytearray()
    if palette_size:
        out.extend(full_tiles[:palette_size])
    while len(out) < tile_offset:
        out.append(0)
    split_x = min(split_x, view_w)
    order = [(x, y) for y in range(view_h) for x in range(split_x)]
    order.extend((x, y) for y in range(view_h) for x in range(split_x, view_w))
    for x, y in order:
        index = y * map_w + x
        start = tile_offset + index * tile_bytes
        out.extend(full_tiles[start:start + tile_bytes])
    return bytes(out)


def main() -> int:
    emu = HMM2FullZ80Emulator(ROOT)
    regs = attach_hmm2_shadow(emu)

    def render_frame(max_steps: int = 30_000_000) -> None:
        regs.tick_frame(emu.ft.ram_dl)
        emu.call(emu.sym["Render_Frame"], max_steps=max_steps)

    emu.call(emu.sym["Platform_Init"], max_steps=4_000_000)
    if not emu.fmaddr_enabled:
        print("ОШИБКА: FMADDR mapping не включён. Перед SetPage* нужен FMapAddrInit.")
        return 1
    print("OK: FMADDR mapping включён")
    emu.call(emu.sym["Game_Init"], max_steps=250_000_000)  # включает стрим HMM2MENU.PAK с SD
    # Game_Init теперь стартует в ГЛАВНОМ МЕНЮ (диспетчер сцен) и Menu_LoadFromPak
    # заливает меню-ассеты в RAM_G[0..]. Они перекрывают область composite-кэша
    # (2 банка). Этот верификатор проверяет adventure-пайплайн, поэтому очищаем RAM_G
    # (эквивалент чистого первого входа в adventure; в рантайме неактивный банк
    # перезаливается при скролле до показа) и явно входим в adventure-сцену.
    emu.ft.ram_g[:] = b"\x00" * len(emu.ft.ram_g)
    emu.call(emu.sym["Adventure_Enter"], max_steps=12_000_000)

    bg_inc = ROOT / "Source" / "ASM" / "generated_dxt_background.inc"
    bg_size = read_equ(bg_inc, "BG_DXT_RAW_SIZE") if bg_inc.exists() else 0
    composite_static = read_equ(ROOT / "Source" / "ASM" / "generated_terrain.inc", "COMPOSITE_STATIC_TILEMAP")
    rendered_for_cache = False
    if bg_inc.exists() and bg_size > 0:
        bg_base = read_equ(bg_inc, "BG_DXT_RAMG")
        expected = read_expected_chunks(BACKGROUND_DIR, "SKIRMISH_BG_DXT_L4_p*.bin", bg_size)
        actual = bytes(emu.ft.ram_g[bg_base:bg_base + len(expected)])
        label = "background"
    elif composite_static:
        # Проверка composite-кэша считает ожидание для origin (0,0). Стартовый
        # вьюпорт игры может быть НЕ нулевым (герой у замка) — форсируем origin 0
        # для этой проверки (она тестит upload-пайплайн, origin-agnostic).
        emu.set_byte(emu.sym["ViewportOriginX"], 0)
        emu.set_byte(emu.sym["ViewportOriginY"], 0)
        emu.set_word(emu.sym["ViewportPixelX"], 0)
        emu.set_word(emu.sym["ViewportPixelY"], 0)
        for _sym in ("RuntimeLastOriginX", "RuntimeLastOriginY"):
            if _sym in emu.sym:
                emu.set_byte(emu.sym[_sym], 0xFF)  # пометить грязным → перезалить origin 0
        for _ in range(4):  # дать кэшу полностью перезалиться на origin 0
            render_frame()
        rendered_for_cache = True
        terrain_size = read_equ(ROOT / "Source" / "ASM" / "generated_terrain.inc", "TERRAIN_ATLAS_PAGE_COUNT") * 0x4000
        full_tiles = read_expected_chunks(ATLAS_DIR, "SKIRMISH_GROUND32_p*.bin", terrain_size)
        runtime_inc = ROOT / "Source" / "ASM" / "generated_runtime_map.inc"
        expected = expected_composite_cache(
            full_tiles,
            read_equ(ROOT / "Source" / "ASM" / "generated_map.inc", "MAP0_W"),
            read_equ(runtime_inc, "RUNTIME_VIEW_W"),
            read_equ(runtime_inc, "RUNTIME_VIEW_H"),
            read_equ(runtime_inc, "RUNTIME_LEFT_VIEW_W"),
            read_equ(runtime_inc, "COMPOSITE_TILE_BYTES"),
            read_equ(runtime_inc, "COMPOSITE_BG_PALETTE_SIZE"),
            read_equ(runtime_inc, "COMPOSITE_BG_TILE_BASE"),
        )
        cache_bank_size = read_equ(runtime_inc, "COMPOSITE_CACHE_BANK_SIZE")
        active_bank = emu.get_byte(emu.sym.get("CompositeDrawBank", 0)) if "CompositeDrawBank" in emu.sym else 0
        actual_base = active_bank * cache_bank_size
        actual = bytes(emu.ft.ram_g[actual_base: actual_base + len(expected)])
        label = f"composite cache bank{active_bank} after Render_Frame"
    else:
        terrain_size = read_equ(ROOT / "Source" / "ASM" / "generated_terrain.inc", "TERRAIN_ATLAS_SIZE")
        expected = read_expected_chunks(ATLAS_DIR, "SKIRMISH_GROUND32_p*.bin", terrain_size)
        actual = bytes(emu.ft.ram_g[: len(expected)])
        label = "atlas"
    print(f"{label} expected bytes: {len(expected)} sha256={sha(expected)}")
    print(f"ram_g actual bytes:     {len(actual)} sha256={sha(actual)}")
    if expected != actual:
        for i, (a, b) in enumerate(zip(expected, actual)):
            if a != b:
                actual_offset = (actual_base + i) if composite_static and "actual_base" in locals() else i
                print(f"ОШИБКА: первое отличие RAM_G offset=#{actual_offset:06X}: ожидалось #{a:02X}, получено #{b:02X}")
                return 1
        print(f"ОШИБКА: длины {label}/RAM_G не совпали")
        return 1
    print(f"OK: RAM_G байт-в-байт совпадает с {label} pages")

    object_size = read_equ(ROOT / "Source" / "ASM" / "generated_objects.inc", "OBJECT_ATLAS_SIZE")
    object_base = read_equ(ROOT / "Source" / "ASM" / "generated_objects.inc", "OBJECT_ATLAS_RAMG")
    if object_size:
        expected_objects = read_expected_chunks(OBJECT_DIR, "SKIRMISH_OBJECTS_p*.bin", object_size)
        actual_objects = bytearray(emu.ft.ram_g[object_base:object_base + object_size])
        # Мини-карта (UI_RADAR_RAMG) печётся ЧЁРНОЙ и динамически раскрывается в
        # рантайме (Minimap_RevealTile, туман радара) — её область легитимно меняется
        # после Render_Frame, поэтому исключаем её из побайтовой сверки с запечённым.
        radar_base = read_equ(ROOT / "Source" / "ASM" / "generated_objects.inc", "UI_RADAR_RAMG")
        radar_stride = read_equ(ROOT / "Source" / "ASM" / "generated_objects.inc", "UI_RADAR_STRIDE")
        radar_h = read_equ(ROOT / "Source" / "ASM" / "generated_objects.inc", "UI_RADAR_H")
        if radar_base and radar_stride and radar_h:
            rs = radar_base - object_base
            re = rs + radar_stride * radar_h
            if 0 <= rs < re <= len(actual_objects):
                actual_objects[rs:re] = expected_objects[rs:re]
        # Ресурсная панель: DL собирается в RAM_G в рантайме (Resources_BuildPanelDL) →
        # её буфер легитимно меняется после Game_Init, исключаем из сверки (1 КБ).
        panel_base = read_equ(ROOT / "Source" / "ASM" / "generated_objects.inc", "RESOURCE_PANEL_RAMG")
        if panel_base:
            ps = panel_base - object_base
            pe = ps + 1024
            if 0 <= ps < pe <= len(actual_objects):
                actual_objects[ps:pe] = expected_objects[ps:pe]
        actual_objects = bytes(actual_objects)
        print(f"objects expected bytes: {len(expected_objects)} sha256={sha(expected_objects)}")
        print(f"objects ram_g bytes:    {len(actual_objects)} sha256={sha(actual_objects)} (минус область радар-тумана)")
        if expected_objects != actual_objects:
            for i, (a, b) in enumerate(zip(expected_objects, actual_objects)):
                if a != b:
                    print(f"ОШИБКА: первое отличие object RAM_G offset=#{object_base + i:06X}: ожидалось #{a:02X}, получено #{b:02X}")
                    return 1
            print("ОШИБКА: длины object atlas/RAM_G не совпали")
            return 1
        print("OK: RAM_G object atlas совпадает с object pages")

    if not rendered_for_cache:
        render_frame()
    dl = bytes(emu.ft.ram_dl[:0x2000])
    ops = disasm_dl(dl, max_ops=2048)
    counts = {}
    for op in ops:
        counts[op.name] = counts.get(op.name, 0) + 1
    print(f"DL sha256={sha(dl)}")
    print(
        "DL counts: "
        f"CELL={counts.get('CELL', 0)} VERTEX2F={counts.get('VERTEX2F', 0)} "
        f"VERTEX2II={counts.get('VERTEX2II', 0)} "
        f"SCISSOR={counts.get('SCISSOR_XY', 0)}/{counts.get('SCISSOR_SIZE', 0)} "
        f"DISPLAY={counts.get('DISPLAY', 0)}"
    )
    if bg_inc.exists() and bg_size > 0:
        if counts.get("VERTEX2F", 0) < 3 or counts.get("DISPLAY", 0) != 1:
            print("ОШИБКА: неверный DL pseudo-DXT background")
            return 1
        print("OK: DL использует pseudo-DXT background pass и допускает object overlay")
    else:
        runtime_inc = ROOT / "Source" / "ASM" / "generated_runtime_map.inc"
        runtime_tiles = read_equ(runtime_inc, "RUNTIME_VIEW_W") * read_equ(runtime_inc, "RUNTIME_VIEW_H")
        if counts.get("SCISSOR_XY", 0) < 2 or counts.get("SCISSOR_SIZE", 0) < 2:
            print("ОШИБКА: нет scissor-окна карты и/или сброса scissor перед UI")
            return 1
        if counts.get("VERTEX2II", 0) >= runtime_tiles:
            print("OK: DL использует VERTEX2II terrain для adventure viewport и допускает object overlay")
        elif counts.get("CELL", 0) < runtime_tiles or counts.get("VERTEX2F", 0) < runtime_tiles:
            print("ОШИБКА: неверное число bitmap-команд terrain")
            return 1
        else:
            print("OK: DL использует CELL+VERTEX2F для adventure viewport/scroll-buffer с nearest upscale и допускает object overlay")
    print(
        "физический режим: "
        f"hsize={regs._get32(REG_HSIZE)} "
        f"vsize={regs._get32(REG_VSIZE)} "
        f"pclk={regs._get32(REG_PCLK)}"
    )
    if regs._get32(REG_HSIZE) != 1024 or regs._get32(REG_VSIZE) != 768:
        print("ОШИБКА: неверный размер видеорежима, нужен 1024x768")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
