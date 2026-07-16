#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import struct
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAM_G_SIZE = 1024 * 1024
RAM_DL_SIZE = 8 * 1024
PAGE_SIZE = 0x4000

FT_BITMAP_SOURCE = 1
FT_CELL = 6
FT_BITMAP_LAYOUT = 7
FT_PALETTE_SOURCE = 42

FT_ARGB4 = 6
FT_RGB565 = 7
FT_PALETTED4444 = 15


@dataclass(frozen=True)
class Range:
    name: str
    start: int
    end: int

    @property
    def size(self) -> int:
        return self.end - self.start


def parse_num(text: str) -> int:
    text = text.strip()
    if text.startswith("#"):
        return int(text[1:], 16)
    if text.lower().startswith("0x"):
        return int(text, 16)
    return int(text, 10)


def parse_equ(path: Path, initial: dict[str, int] | None = None) -> dict[str, int]:
    out: dict[str, int] = dict(initial or {})
    rx = re.compile(r"^\s*([A-Za-z0-9_]+)\s+EQU\s+(.+?)\s*$")
    with path.open("r", encoding="utf-8", errors="replace") as fp:
        for line in fp:
            m = rx.match(line)
            if not m:
                continue
            name, expr = m.groups()
            expr = expr.split(";", 1)[0].strip()
            if not expr:
                continue
            try:
                out[name] = eval_expr(expr, out)
            except Exception:
                pass
    return out


def eval_expr(expr: str, values: dict[str, int]) -> int:
    expr = re.sub(r"#([0-9A-Fa-f]+)", r"0x\1", expr)
    allowed = {k: int(v) for k, v in values.items()}
    return int(eval(expr, {"__builtins__": {}}, allowed))


def parse_spg_pages(path: Path) -> dict[int, bytes]:
    pages: dict[int, bytes] = {}
    # page -> [(start, end, file)] для детекта перекрытий. Раньше pages[page]=buf
    # делал last-wins → коллизия двух блоков на одной странице ТИХО скрывалась
    # (баг «герой застревает»: object-view DL затёр SKIRMISH.path.bin на page #11,
    # билд/verify были зелёные, проявлялось только в геймплее). Теперь — явная ошибка.
    occupancy: dict[int, list] = {}
    rx = re.compile(r"^\s*Block\s*=\s*([^,]+),\s*([^,]+),\s*(.+?)\s*$", re.I)
    with path.open("r", encoding="utf-8", errors="replace") as fp:
        for line in fp:
            m = rx.match(line)
            if not m:
                continue
            offset = parse_num(m.group(1)) & (PAGE_SIZE - 1)
            page = parse_num(m.group(2)) & 0xFF
            rel = m.group(3).strip().replace("/", "\\")
            data = (ROOT / rel).read_bytes()
            end = offset + min(len(data), PAGE_SIZE - offset)
            for (s, e, f) in occupancy.get(page, []):
                if offset < e and s < end:
                    raise RuntimeError(
                        f"КОЛЛИЗИЯ страниц SPG: page #{page:02X} — '{rel}' "
                        f"[#{offset:04X}..#{end:04X}) перекрывает '{f}' [#{s:04X}..#{e:04X}). "
                        f"Проверь page-списки (OBJECT_VIEW_PAGE_LIST не должен задевать "
                        f"страницы карты/пути 0x10/0x11/0x13/0x14/0xC4)."
                    )
            occupancy.setdefault(page, []).append((offset, end, rel))
            buf = bytearray(pages.get(page, bytes(PAGE_SIZE)))
            buf[offset:end] = data[:end - offset]
            pages[page] = bytes(buf)
    return pages


def parse_sym(path: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    rx = re.compile(r"^([^:]+):\s+EQU\s+0x([0-9A-Fa-f]+)")
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8", errors="replace") as fp:
        for line in fp:
            m = rx.match(line)
            if m:
                out[m.group(1)] = int(m.group(2), 16)
    return out


def parse_object_table(path: Path, count: int) -> list[tuple[int, int, int, int]]:
    # Запись 7 байт: DEFB page, DEFW off, DEFW bottom_size, DEFW top_size.
    rows: list[tuple[int, int, int, int]] = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    in_table = False
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == "ObjectViewDL_Table:":
            in_table = True
            i += 1
            continue
        if not in_table:
            i += 1
            continue
        if not line.startswith("DEFB"):
            if rows:
                break
            i += 1
            continue
        page = parse_num(line.split(None, 1)[1])
        off = parse_num(lines[i + 1].strip().split(None, 1)[1])
        bottom_size = parse_num(lines[i + 2].strip().split(None, 1)[1])
        top_size = parse_num(lines[i + 3].strip().split(None, 1)[1])
        rows.append((page, off, bottom_size, top_size))
        i += 4
        if len(rows) == count:
            break
    if len(rows) != count:
        raise RuntimeError(f"ObjectViewDL_Table: ожидалось {count}, найдено {len(rows)}")
    return rows


def read_page_slice(pages: dict[int, bytes], page: int, off: int, size: int) -> bytes:
    if page not in pages:
        raise RuntimeError(f"нет SPG page #{page:02X} для object-view")
    if off + size > PAGE_SIZE:
        raise RuntimeError(f"object-view пересекает page boundary: page=#{page:02X} off=#{off:04X} size={size}")
    return pages[page][off:off + size]


def bitmap_data_size(fmt: int, stride: int, height: int) -> int:
    if fmt in (FT_ARGB4, FT_RGB565, FT_PALETTED4444):
        return stride * height
    return stride * height


def parse_dl_ranges(origin: tuple[int, int], dl: bytes) -> list[Range]:
    ranges: list[Range] = []
    current_source: int | None = None
    current_palette: int | None = None
    current_cell = 0
    current_layout: tuple[int, int, int, int] | None = None
    words = len(dl) // 4
    for index in range(words):
        (word,) = struct.unpack_from("<I", dl, index * 4)
        op = (word >> 24) & 0xFF
        if op == FT_BITMAP_SOURCE:
            current_source = word & 0xFFFFF
            current_cell = 0
            current_layout = None
        elif op == FT_PALETTE_SOURCE:
            current_palette = word & 0x3FFFFF
            ranges.append(Range(f"origin {origin[0]},{origin[1]} PALETTE_SOURCE word {index}", current_palette, current_palette + 512))
        elif op == FT_BITMAP_LAYOUT and current_source is not None:
            fmt = (word >> 19) & 31
            stride = (word >> 9) & 1023
            height = word & 511
            size = bitmap_data_size(fmt, stride, height)
            current_layout = (fmt, stride, height, size)
            ranges.append(Range(f"origin {origin[0]},{origin[1]} BITMAP_SOURCE word {index}", current_source, current_source + size))
        elif op == FT_CELL:
            current_cell = word & 127
            if current_source is not None and current_layout is not None:
                _, _, _, size = current_layout
                start = current_source + current_cell * size
                ranges.append(Range(f"origin {origin[0]},{origin[1]} CELL {current_cell} word {index}", start, start + size))
    return ranges


def overlaps(a: Range, b: Range) -> bool:
    return a.start < b.end and b.start < a.end


def fmt_range(r: Range) -> str:
    return f"{r.name}: #{r.start:06X}-#{r.end - 1:06X} ({r.size} bytes)"


def check_inside_ramg(r: Range) -> None:
    if r.start < 0 or r.end > RAM_G_SIZE:
        raise RuntimeError(f"выход за RAM_G: {fmt_range(r)} > #0FFFFF")


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверить RAM_G диапазоны HMM2 для каждого viewport origin.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    terrain = parse_equ(ROOT / "Source/ASM/generated_terrain.inc")
    objects = parse_equ(ROOT / "Source/ASM/generated_objects.inc")
    runtime = parse_equ(ROOT / "Source/ASM/generated_runtime_map.inc")
    runtime.update(parse_sym(ROOT / "Build/hmm2.sym"))
    render = parse_equ(ROOT / "Source/ASM/render.asm", {**terrain, **objects, **runtime})

    count_x = terrain["VIEWPORT_ORIGIN_COUNT_X"]
    count_y = terrain["VIEWPORT_ORIGIN_COUNT_Y"]
    origin_count = count_x * count_y
    table = parse_object_table(ROOT / "Source/ASM/generated_runtime_map.inc", origin_count)
    pages = parse_spg_pages(ROOT / "spgbld_vdac2.ini")

    terrain_range = Range("terrain atlas", terrain["TERRAIN_ATLAS_RAMG"], terrain["TERRAIN_ATLAS_RAMG"] + terrain["TERRAIN_ATLAS_SIZE"])
    object_range = Range("object atlas", objects["OBJECT_ATLAS_RAMG"], objects["OBJECT_ATLAS_RAMG"] + objects["OBJECT_ATLAS_SIZE"])
    left_range = Range("runtime left DL", render["RUNTIME_DL_LEFT_RAMG"], render["RUNTIME_DL_LEFT_RAMG"] + runtime["RUNTIME_LEFT_DL_BYTES"])
    right_range = Range("runtime right DL", render["RUNTIME_DL_RIGHT_RAMG"], render["RUNTIME_DL_RIGHT_RAMG"] + runtime["RUNTIME_RIGHT_DL_BYTES"])
    static_ranges = [terrain_range, object_range, left_range, right_range]

    for item in static_ranges:
        check_inside_ramg(item)
    for a in static_ranges:
        for b in static_ranges:
            if a.name < b.name and overlaps(a, b):
                raise RuntimeError(f"пересечение RAM_G: {fmt_range(a)} / {fmt_range(b)}")

    max_object_dl = 0
    max_frame_dl = 0
    max_frame_origin = (0, 0)
    max_read_end = 0
    max_write_end = 0
    checked_sources = 0
    for idx, (page, off, bottom_size, top_size) in enumerate(table):
        ox = idx % count_x
        oy = idx // count_x
        # В RUNTIME_DL_OBJECT_RAMG заливается blob [низ][верх]; два CMD_APPEND.
        size = bottom_size + top_size
        if size > terrain["OBJECT_VIEW_DL_SIZE"] - 4:
            raise RuntimeError(f"origin {ox},{oy}: object blob {size} (низ {bottom_size}+верх {top_size}) > OBJECT_VIEW_DL_SIZE-4")
        object_dl = Range(f"origin {ox},{oy} runtime object DL", render["RUNTIME_DL_OBJECT_RAMG"], render["RUNTIME_DL_OBJECT_RAMG"] + size)
        check_inside_ramg(object_dl)
        for fixed in (terrain_range, object_range):
            if overlaps(object_dl, fixed):
                raise RuntimeError(f"origin {ox},{oy}: runtime object DL пересекает {fixed.name}: {fmt_range(object_dl)} / {fmt_range(fixed)}")
        # Полная модель RAM_DL за кадр — суммируем ВСЁ, что Render_RuntimeFrameCmd
        # (render.asm 45-110) кладёт в RAM_DL: CmdBufCopy-фрагменты + CMD_APPEND,
        # который копирует блоб целиком. Раньше тут не хватало hero-path, fog,
        # actor, minimap, ведущего CLEAR (~2.6 КБ) — а это ЕДИНСТВЕННЫЙ страж
        # RAM_DL≤8192 (ASM RUNTIME_CMD_FRAME_MAX стережёт ДРУГОЙ буфер, RAM_CMD).
        # Условные термы (.get,0): hero-path под HERO_PATH_ROUTE_DL, actor под
        # DYNAMIC_ACTOR_RAMG. Остальные эмитятся в кадре безусловно — читаем прямо
        # (отсутствие символа → явная ошибка, не тихий недосчёт).
        frame_dl = (
            4  # ведущий CLEAR/write32 (render.asm 64-66)
            + runtime["RuntimeDL_Header_SIZE"]
            + runtime["RUNTIME_LEFT_DL_BYTES"]
            + runtime["RuntimeDL_RightBand_SIZE"]
            + runtime["RUNTIME_RIGHT_DL_BYTES"]
            + runtime["RuntimeDL_Tail_SIZE"] - 4
            + runtime["RuntimeDL_ObjectTranslate_SIZE"]
            + bottom_size
            # top-оверлей: ещё одна копия ObjectTranslate + top DL (CMD_APPEND после актёра)
            + (runtime["RuntimeDL_ObjectTranslate_SIZE"] + top_size if top_size else 0)
            + runtime.get("HERO_PATH_CMD_MAX", 0)          # маршрут героя (условно)
            + runtime["HERO_MARKER_DL_SIZE"] - 4
            + max(0, runtime.get("ACTOR_DL_SIZE", 0) - 4)  # актёр (условно)
            + runtime.get("MAP_ANIM_CMD_BYTES", 0)         # анимир. объекты (кап MAP_ANIM_MAX_PER_FRAME)
            + runtime["FOG_CMD_BYTES"]                     # туман
            + runtime["AdventureUI_DL_SIZE"]               # UI-рамка (FIFO)
            + runtime["UIADV_ICONSDYN_SIZE"]               # динамика списка (RAM_G, CMD_APPEND)
            + runtime["MINIMAP_RECT_CMD_BYTES"]            # рамка вьюпорта + точка героя на радаре
            + runtime["CURSOR_DL_SIZE"] - 4
        )
        if frame_dl > RAM_DL_SIZE:
            raise RuntimeError(
                f"origin {ox},{oy}: выход за RAM_DL FT812: frame DL {frame_dl} > {RAM_DL_SIZE}; "
                f"object DL={size}, terrain/static={frame_dl - size}"
            )
        if frame_dl > max_frame_dl:
            max_frame_dl = frame_dl
            max_frame_origin = (ox, oy)
        if size == 0:
            continue
        dl = read_page_slice(pages, page, off, size)
        for r in parse_dl_ranges((ox, oy), dl):
            checked_sources += 1
            check_inside_ramg(r)
            if r.name.find("PALETTE_SOURCE") >= 0:
                if not overlaps(r, object_range) or r.start != objects["OBJECT_PALETTE_RAMG"]:
                    raise RuntimeError(f"origin {ox},{oy}: palette вне object atlas: {fmt_range(r)}")
            elif not (object_range.start <= r.start < r.end <= object_range.end):
                raise RuntimeError(f"origin {ox},{oy}: bitmap source вне object atlas: {fmt_range(r)}; atlas #{object_range.start:06X}-#{object_range.end - 1:06X}")
            max_read_end = max(max_read_end, r.end)
        max_object_dl = max(max_object_dl, size)
        max_write_end = max(max_write_end, object_dl.end)
        if args.verbose:
            print(f"origin {ox:02d},{oy:02d}: page=#{page:02X} off=#{off:04X} dl={size} write=#{object_dl.start:06X}-#{object_dl.end - 1:06X}")

    print("OK: RAM_G calculator")
    print(f"  origins={origin_count} ({count_x}x{count_y}), object-view pages checked={len({p for p, _, _, _ in table})}")
    print(f"  {fmt_range(terrain_range)}")
    print(f"  {fmt_range(object_range)}")
    print(f"  {fmt_range(left_range)}")
    print(f"  {fmt_range(right_range)}")
    print(f"  runtime object DL base=#{render['RUNTIME_DL_OBJECT_RAMG']:06X}, max_size={max_object_dl}, max_end=#{max_write_end - 1:06X}")
    print(f"  RAM_DL max frame={max_frame_dl}/{RAM_DL_SIZE} at origin={max_frame_origin[0]},{max_frame_origin[1]}")
    print(f"  checked bitmap/palette sources={checked_sources}, max_source_end=#{max_read_end - 1:06X}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ОШИБКА: {exc}")
        raise SystemExit(1)
