#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tsconf_ft812_sim import TSConfFT812Machine  # noqa: E402
from shadow_ft812 import (  # noqa: E402
    FT812VideoTiming,
    REG_CLOCK,
    REG_DLSWAP,
    REG_FRAMES,
    REG_HCYCLE,
    REG_HOFFSET,
    REG_HSIZE,
    REG_INT_FLAGS,
    REG_PCLK,
    REG_VCYCLE,
    REG_VOFFSET,
    REG_VSIZE,
    attach_shadow,
    disasm_dl,
    format_dl,
)


# Реальные тайминги VM_1024_768_59Hz (TSLib Docs/TSLib/Include/FT/81x Const.inc:426):
# PCLK = 8 МГц × F_MUL(8) = 64 МГц; HCYCLE=24+136+160+1024=1344;
# VCYCLE=3+6+29+768=806; HOFFSET=24+136+160=320; VOFFSET=3+6+29-1=37.
# Частота кадра = 64e6 / (1344*806) = 59.08 Гц.
HMM2_VIDEO_TIMING = FT812VideoTiming(
    hcycle=1344,
    hoffset=320,
    hsize=1024,
    vcycle=806,
    voffset=37,
    vsize=768,
    pclk=8,
)


def _read_chunks(folder: Path, pattern: str, size: int) -> bytes:
    out = bytearray()
    for path in sorted(folder.glob(pattern)):
        out.extend(path.read_bytes())
        if len(out) >= size:
            break
    return bytes(out[:size])


def _seed_composite_cache_origin0(emu: "HMM2FullZ80Emulator") -> None:
    runtime_inc = ROOT / "Source" / "ASM" / "generated_runtime_map.inc"
    terrain_inc = ROOT / "Source" / "ASM" / "generated_terrain.inc"

    def equ(path: Path, name: str) -> int:
        rx = re.compile(rf"^\s*{re.escape(name)}\s+EQU\s+(.+?)\s*$")
        for line in path.read_text(encoding="utf-8").splitlines():
            m = rx.match(line)
            if m:
                value = m.group(1).strip()
                return int(value[1:], 16) if value.startswith("#") else int(value)
        raise RuntimeError(f"нет EQU {name}")

    view_w = equ(runtime_inc, "RUNTIME_VIEW_W")
    view_h = equ(runtime_inc, "RUNTIME_VIEW_H")
    split_x = min(equ(runtime_inc, "RUNTIME_LEFT_VIEW_W"), view_w)
    tile_bytes = equ(runtime_inc, "COMPOSITE_TILE_BYTES")
    palette_size = equ(runtime_inc, "COMPOSITE_BG_PALETTE_SIZE")
    tile_base = equ(runtime_inc, "COMPOSITE_BG_TILE_BASE")
    terrain_size = equ(terrain_inc, "TERRAIN_ATLAS_SIZE")
    payload = _read_chunks(ROOT / "Assets" / "Converted" / "Terrain", "SKIRMISH_GROUND32_p*.bin", terrain_size)
    map_w = equ(ROOT / "Source" / "ASM" / "generated_map.inc", "MAP0_W")
    emu.ft.ram_g[:palette_size] = payload[:palette_size]
    for y in range(view_h):
        for x in range(view_w):
            src = tile_base + (y * map_w + x) * tile_bytes
            slot = (y * split_x + x) if x < split_x else (split_x * view_h + y * (view_w - split_x) + (x - split_x))
            dst = tile_base + slot * tile_bytes
            emu.ft.ram_g[dst:dst + tile_bytes] = payload[src:src + tile_bytes]


class HMM2FullZ80Emulator(TSConfFT812Machine):
    def __init__(self, root: Path = ROOT, trace: bool = False) -> None:
        root = Path(root)
        super().__init__(
            root,
            spgbld_path=root / "spgbld_vdac2.ini",
            sym_path=root / "Build" / "hmm2.sym",
            trace=trace,
            load_spg=True,
            init_cpu=True,
            default_stack="0x7FFF",
            default_start="0x5C00",
            fmaddr_requires_enable=True,
        )
        self.input.mouse_buttons = 0x01
        # Подключить SD-образ (для PAK-загрузчика). Diagnostics/sd.img = копия wc.img.
        sd_img = Path(root) / "Diagnostics" / "sd.img"
        if sd_img.exists():
            self.load_sd_image(sd_img)


def attach_hmm2_shadow(emu: HMM2FullZ80Emulator):
    return attach_shadow(emu, HMM2_VIDEO_TIMING)


def _field_addr(value) -> int:
    if isinstance(value, str):
        return int(value.lstrip("#"), 16)
    return int(value)


def _rgb565_at(ram_g: bytes, addr: int) -> tuple[int, int, int]:
    if addr < 0 or addr + 1 >= len(ram_g):
        return (255, 0, 255)
    value = ram_g[addr] | (ram_g[addr + 1] << 8)
    return (((value >> 11) & 31) << 3, ((value >> 5) & 63) << 2, (value & 31) << 3)


def _argb4_at(ram_g: bytes, addr: int) -> tuple[int, int, int, int]:
    if addr < 0 or addr + 1 >= len(ram_g):
        return (255, 0, 255, 255)
    value = ram_g[addr] | (ram_g[addr + 1] << 8)
    return (((value >> 8) & 15) * 17, ((value >> 4) & 15) * 17, (value & 15) * 17, ((value >> 12) & 15) * 17)


def _paletted4444_at(ram_g: bytes, palette_addr: int, index: int) -> tuple[int, int, int, int]:
    return _argb4_at(ram_g, palette_addr + (index & 0xFF) * 2)


def _paletted4444_table(ram_g: bytes, palette_addr: int) -> tuple[tuple[int, int, int, int], ...]:
    return tuple(_paletted4444_at(ram_g, palette_addr, index) for index in range(256))


def _l4_alpha_at(ram_g: bytes, addr: int, x: int) -> int:
    value = ram_g[addr]
    nibble = (value >> 4) & 15 if (x & 1) == 0 else value & 15
    return nibble * 17


def _signed_bits(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    mask = (1 << bits) - 1
    value &= mask
    return value - (1 << bits) if value & sign else value


def _blend_argb4(dst: tuple[int, int, int], src: tuple[int, int, int, int]) -> tuple[int, int, int]:
    sr, sg, sb, a = src
    if a <= 0:
        return dst
    if a >= 255:
        return (sr, sg, sb)
    dr, dg, db = dst
    ia = 255 - a
    return ((sr * a + dr * ia) // 255, (sg * a + dg * ia) // 255, (sb * a + db * ia) // 255)


def _blend_bitmap_pixel(
    dst: tuple[int, int, int],
    src: tuple[int, int, int, int],
    blend_func: tuple[str, str],
) -> tuple[int, int, int]:
    sr, sg, sb, a = src
    if blend_func == ("ONE", "ZERO"):
        return (sr, sg, sb)
    if blend_func == ("SRC_ALPHA", "ONE_MINUS_SRC_ALPHA"):
        return _blend_argb4(dst, src)
    if blend_func == ("ONE", "ONE_MINUS_SRC_ALPHA"):
        dr, dg, db = dst
        ia = 255 - a
        return (min(255, sr + (dr * ia) // 255), min(255, sg + (dg * ia) // 255), min(255, sb + (db * ia) // 255))
    return _blend_argb4(dst, src)


def render_dl_into(img, alpha, ops, ram_g: bytes, width: int, height: int,
                   y_lo: int = 0, y_hi: int | None = None):
    """Растеризует DL `ops` (с RAM_G) в готовые img(RGB)/alpha(L), ограничивая
    отрисовку строками [y_lo, y_hi). Используется и для полного кадра, и для
    реконструкции по полосам в физическом cycle-accurate симуляторе."""
    from PIL import ImageDraw

    if y_hi is None:
        y_hi = height
    draw = ImageDraw.Draw(img)
    clear_color = (0, 0, 0)
    color = (255, 255, 255)
    prim = None
    rect_start = None
    def default_bitmap_state() -> dict:
        return {
            "source": 0,
            "palette": 0,
            "layout": {"fmt": None, "stride": 0, "height": 0},
            "layout_h": {"stride_h": 0, "height_h": 0},
            "size": {"w": 0, "h": 0},
            "size_h": {"w_h": 0, "h_h": 0},
            "transform_a": 256,
            "transform_c": 0,
            "transform_e": 256,
        }

    bitmap_handles = [default_bitmap_state() for _ in range(32)]
    bitmap_handle = 0
    bitmap_cell = 0
    vertex_frac = 4
    color_mask = (1, 1, 1, 1)
    blend_func = ("ONE", "ZERO")
    translate_x = 0
    translate_y = 0
    point_radius = 1
    line_width = 1
    line_prev = None
    scissor = [0, 0, width, height]
    palette_cache: dict[int, tuple[tuple[int, int, int, int], ...]] = {}

    def palette_table(addr: int) -> tuple[tuple[int, int, int, int], ...]:
        if addr not in palette_cache:
            palette_cache[addr] = _paletted4444_table(ram_g, addr)
        return palette_cache[addr]

    def in_scissor(x: int, y: int) -> bool:
        return (scissor[0] <= x < scissor[0] + scissor[2]
                and scissor[1] <= y < scissor[1] + scissor[3]
                and y_lo <= y < y_hi)

    def clipped_rect(x0: int, y0: int, x1: int, y1: int) -> tuple[int, int, int, int] | None:
        rx0, rx1 = sorted((x0, x1))
        ry0, ry1 = sorted((y0, y1))
        cx0 = max(rx0, scissor[0], 0)
        cy0 = max(ry0, scissor[1], 0, y_lo)
        cx1 = min(rx1, scissor[0] + scissor[2] - 1, width - 1)
        cy1 = min(ry1, scissor[1] + scissor[3] - 1, height - 1, y_hi - 1)
        if cx0 > cx1 or cy0 > cy1:
            return None
        return (cx0, cy0, cx1, cy1)

    def put_argb4_pixel(pos: tuple[int, int], rgba: tuple[int, int, int, int]) -> None:
        if not in_scissor(pos[0], pos[1]):
            return
        alpha_value = rgba[3]
        if blend_func == ("ONE", "ZERO"):
            img.putpixel(pos, rgba[:3])
        elif blend_func == ("SRC_ALPHA", "ONE_MINUS_SRC_ALPHA"):
            if alpha_value <= 0:
                return
            if alpha_value >= 255:
                img.putpixel(pos, rgba[:3])
            else:
                img.putpixel(pos, _blend_argb4(img.getpixel(pos), rgba))
        else:
            img.putpixel(pos, _blend_bitmap_pixel(img.getpixel(pos), rgba, blend_func))

    for op in ops:
        if op.name == "CLEAR_COLOR_RGB":
            clear_color = (op.fields["r"], op.fields["g"], op.fields["b"])
        elif op.name == "CLEAR" and op.fields.get("c"):
            rect = clipped_rect(0, 0, width - 1, height - 1)
            if rect is not None:
                draw.rectangle(rect, fill=clear_color)
            if op.fields.get("c"):
                rect = clipped_rect(0, 0, width - 1, height - 1)
                if rect is not None:
                    alpha.paste(0, [rect[0], rect[1], rect[2] + 1, rect[3] + 1])
        elif op.name == "COLOR_RGB":
            color = (op.fields["r"], op.fields["g"], op.fields["b"])
        elif op.name == "POINT_SIZE":
            raw_size = int(op.fields.get("size", op.fields.get("v", 16)))
            point_radius = max(1, int(round(raw_size / 16)))
        elif op.name == "LINE_WIDTH":
            line_width = max(1, int(round(int(op.fields.get("width", 16)) / 16)))
        elif op.name == "BEGIN":
            prim = op.fields.get("prim")
            rect_start = None
            line_prev = None
        elif op.name == "END":
            prim = None
            rect_start = None
            line_prev = None
        elif op.name == "VERTEX_FORMAT":
            vertex_frac = int(op.fields.get("frac", 4))
        elif op.name == "CELL":
            bitmap_cell = int(op.fields.get("cell", 0))
        elif op.name == "BITMAP_HANDLE":
            bitmap_handle = int(op.fields.get("handle", 0)) & 31
        elif op.name == "BITMAP_SOURCE":
            bitmap_handles[bitmap_handle]["source"] = _field_addr(op.fields["addr"])
        elif op.name == "PALETTE_SOURCE":
            bitmap_handles[bitmap_handle]["palette"] = _field_addr(op.fields["addr"])
        elif op.name == "BITMAP_LAYOUT":
            bitmap_handles[bitmap_handle]["layout"] = {
                "fmt": op.fields.get("fmt"),
                "stride": int(op.fields.get("stride", 0)),
                "height": int(op.fields.get("height", 0)),
            }
        elif op.name == "BITMAP_LAYOUT_H":
            bitmap_handles[bitmap_handle]["layout_h"] = {
                "stride_h": int(op.fields.get("stride_h", 0)),
                "height_h": int(op.fields.get("height_h", 0)),
            }
        elif op.name == "BITMAP_SIZE":
            bitmap_handles[bitmap_handle]["size"] = {
                "w": int(op.fields.get("w", 0)),
                "h": int(op.fields.get("h", 0)),
            }
        elif op.name == "BITMAP_SIZE_H":
            bitmap_handles[bitmap_handle]["size_h"] = {
                "w_h": int(op.fields.get("w_h", 0)),
                "h_h": int(op.fields.get("h_h", 0)),
            }
        elif op.name == "COLOR_MASK":
            color_mask = (op.fields.get("r", 1), op.fields.get("g", 1), op.fields.get("b", 1), op.fields.get("a", 1))
        elif op.name == "BLEND_FUNC":
            blend_func = (op.fields.get("src"), op.fields.get("dst"))
        elif op.name == "BITMAP_TRANSFORM_A":
            bitmap_handles[bitmap_handle]["transform_a"] = _signed_bits(int(op.fields.get("v", 256)), 17)
        elif op.name == "BITMAP_TRANSFORM_C":
            bitmap_handles[bitmap_handle]["transform_c"] = _signed_bits(int(op.fields.get("v", 0)), 24)
        elif op.name == "BITMAP_TRANSFORM_E":
            bitmap_handles[bitmap_handle]["transform_e"] = _signed_bits(int(op.fields.get("v", 256)), 17)
        elif op.name == "VERTEX_TRANSLATE_X":
            translate_x = int(op.fields.get("x", 0))
        elif op.name == "VERTEX_TRANSLATE_Y":
            translate_y = int(op.fields.get("y", 0))
        elif op.name == "SCISSOR_XY":
            scissor[0] = int(op.fields.get("x", 0))
            scissor[1] = int(op.fields.get("y", 0))
        elif op.name == "SCISSOR_SIZE":
            scissor[2] = int(op.fields.get("w", width))
            scissor[3] = int(op.fields.get("h", height))
        elif op.name == "VERTEX2F" and prim == "RECTS":
            x = int(round((op.fields["x"] + translate_x) / 16))
            y = int(round((op.fields["y"] + translate_y) / 16))
            if rect_start is None:
                rect_start = (x, y)
            else:
                x0, y0 = rect_start
                rect = clipped_rect(x0, y0, x, y)
                if rect is not None:
                    draw.rectangle(rect, fill=color)
                rect_start = None
        elif op.name == "VERTEX2F" and prim in ("LINE_STRIP", "LINES"):
            scale = 1 << vertex_frac
            x = int(round((op.fields["x"] + translate_x) / scale))
            y = int(round((op.fields["y"] + translate_y) / scale))
            if line_prev is not None:
                draw.line([line_prev, (x, y)], fill=color, width=line_width)
            line_prev = (x, y) if prim == "LINE_STRIP" else None
        elif op.name == "VERTEX2F" and prim == "POINTS":
            scale = 1 << vertex_frac
            x = int(round((op.fields["x"] + translate_x) / scale))
            y = int(round((op.fields["y"] + translate_y) / scale))
            r = point_radius
            r2 = r * r
            inner = max(0.0, r - 1.5)
            inner2 = inner * inner
            for py in range(y - r, y + r + 1):
                if py < 0 or py >= height:
                    continue
                for px in range(x - r, x + r + 1):
                    if px < 0 or px >= width or not in_scissor(px, py):
                        continue
                    d2 = (px - x) ** 2 + (py - y) ** 2
                    if d2 > r2:
                        continue
                    if d2 <= inner2:
                        img.putpixel((px, py), color)
                    else:
                        # мягкий (anti-aliased) край круга, как у FT812 POINTS
                        cov = min(1.0, max(0.0, (r - d2 ** 0.5) / 1.5))
                        old = img.getpixel((px, py))
                        img.putpixel((px, py), tuple(int(old[i] * (1 - cov) + color[i] * cov) for i in range(3)))
        elif op.name == "VERTEX2F" and prim == "BITMAPS":
            state = bitmap_handles[bitmap_handle]
            bitmap_layout = state["layout"]
            bitmap_layout_h = state["layout_h"]
            bitmap_size = state["size"]
            bitmap_size_h = state["size_h"]
            if bitmap_layout["fmt"] not in ("RGB565", "ARGB4", "L4", "PALETTED4444"):
                continue
            scale = 1 << vertex_frac
            x = int(round((op.fields["x"] + translate_x) / scale))
            y = int(round((op.fields["y"] + translate_y) / scale))
            cell = bitmap_cell
            stride = bitmap_layout["stride"] | (bitmap_layout_h["stride_h"] << 10)
            tile_h = bitmap_layout["height"] | (bitmap_layout_h["height_h"] << 9)
            tile_w = (bitmap_size["w"] | (bitmap_size_h["w_h"] << 9)) or (stride // 2)
            tile_draw_h = (bitmap_size["h"] | (bitmap_size_h["h_h"] << 9)) or tile_h
            src = state["source"] + cell * stride * tile_h
            pal = palette_table(state["palette"]) if bitmap_layout["fmt"] == "PALETTED4444" else None
            for py in range(tile_draw_h):
                dy = y + py
                if dy < 0 or dy >= height or not (scissor[1] <= dy < scissor[1] + scissor[3]):
                    continue
                for px in range(tile_w):
                    dx = x + px
                    if dx < 0 or dx >= width or not in_scissor(dx, dy):
                        continue
                    sx = int((px * state["transform_a"] + state["transform_c"]) / 256)
                    syy = int(py * state["transform_e"] / 256)
                    if sx < 0 or syy < 0 or syy >= tile_h:
                        continue
                    if bitmap_layout["fmt"] == "L4":
                        if sx >= stride * 2:
                            continue
                        a = _l4_alpha_at(ram_g, src + syy * stride + sx // 2, sx)
                        if color_mask[3]:
                            alpha.putpixel((dx, dy), a)
                        continue
                    if bitmap_layout["fmt"] == "PALETTED4444":
                        if sx >= stride:
                            continue
                        idx = ram_g[src + syy * stride + sx]
                        put_argb4_pixel((dx, dy), pal[idx])
                        continue
                    addr = src + syy * stride + sx * 2
                    if bitmap_layout["fmt"] == "RGB565":
                        src_rgb = _rgb565_at(ram_g, addr)
                        if blend_func == ("DST_ALPHA", "ZERO"):
                            a = alpha.getpixel((dx, dy))
                            img.putpixel((dx, dy), tuple((c * a) // 255 for c in src_rgb))
                        elif blend_func == ("ONE_MINUS_DST_ALPHA", "ONE"):
                            a = alpha.getpixel((dx, dy))
                            old = img.getpixel((dx, dy))
                            img.putpixel((dx, dy), tuple(min(255, old[i] + (src_rgb[i] * (255 - a)) // 255) for i in range(3)))
                        elif color_mask[:3] != (0, 0, 0):
                            img.putpixel((dx, dy), src_rgb)
                    else:
                        old = img.getpixel((dx, dy))
                        img.putpixel((dx, dy), _blend_bitmap_pixel(old, _argb4_at(ram_g, addr), blend_func))
        elif op.name == "VERTEX2II" and prim == "BITMAPS":
            bitmap_handle = int(op.fields["handle"]) & 31
            state = bitmap_handles[bitmap_handle]
            bitmap_layout = state["layout"]
            bitmap_size = state["size"]
            if bitmap_layout["fmt"] not in ("RGB565", "ARGB4", "PALETTED4444"):
                continue
            x = int(op.fields["x"]) + translate_x // 16
            y = int(op.fields["y"]) + translate_y // 16
            cell = int(op.fields["cell"])
            stride = bitmap_layout["stride"]
            tile_h = bitmap_layout["height"]
            tile_w = bitmap_size["w"] or (stride // 2)
            tile_draw_h = bitmap_size["h"] or tile_h
            src = state["source"] + cell * stride * tile_h
            pal = palette_table(state["palette"]) if bitmap_layout["fmt"] == "PALETTED4444" else None
            for py in range(tile_draw_h):
                sy = src + py * stride
                dy = y + py
                if dy < 0 or dy >= height or not (scissor[1] <= dy < scissor[1] + scissor[3]):
                    continue
                for px in range(tile_w):
                    dx = x + px
                    if dx < 0 or dx >= width or not in_scissor(dx, dy):
                        continue
                    if bitmap_layout["fmt"] == "PALETTED4444":
                        idx = ram_g[sy + px]
                        put_argb4_pixel((dx, dy), pal[idx])
                        continue
                    addr = sy + px * 2
                    if bitmap_layout["fmt"] == "RGB565":
                        img.putpixel((dx, dy), _rgb565_at(ram_g, addr))
                    else:
                        old = img.getpixel((dx, dy))
                        img.putpixel((dx, dy), _blend_bitmap_pixel(old, _argb4_at(ram_g, addr), blend_func))
    return img, alpha


def render_dl_band(ops, ram_g: bytes, width: int, height: int, y_lo: int, y_hi: int,
                   img=None, alpha=None):
    """Рендер полосы строк [y_lo, y_hi) поверх (опционально переданных) img/alpha.
    Позволяет собрать кадр из полос с РАЗНЫМИ снапшотами памяти (для tearing)."""
    from PIL import Image

    if img is None:
        img = Image.new("RGB", (width, height), (0, 0, 0))
    if alpha is None:
        alpha = Image.new("L", (width, height), 0)
    render_dl_into(img, alpha, ops, ram_g, width, height, y_lo, y_hi)
    return img, alpha


def render_dl_png(ops, ram_g: bytes, out_path: Path, width: int, height: int) -> None:
    from PIL import Image

    img = Image.new("RGB", (width, height), (0, 0, 0))
    alpha = Image.new("L", (width, height), 0)
    render_dl_into(img, alpha, ops, ram_g, width, height)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def summarize_ops_ru(ops) -> str:
    counts = {}
    for op in ops:
        counts[op.name] = counts.get(op.name, 0) + 1
    order = ["VERTEX2II", "CLEAR_COLOR_RGB", "CLEAR", "BITMAP_HANDLE", "BITMAP_SOURCE", "BITMAP_LAYOUT", "BITMAP_SIZE", "BEGIN", "END", "DISPLAY"]
    parts = []
    for name in order:
        if name in counts:
            parts.append(f"{name}={counts.pop(name)}")
    for name in sorted(counts):
        parts.append(f"{name}={counts[name]}")
    return f"операций DL: {len(ops)}; " + ", ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Full-stack снимок HMM2 FT812.")
    parser.add_argument("--out", type=Path, default=ROOT / "Diagnostics" / "hmm2_ft812_snapshot.png")
    parser.add_argument("--dump-dl", action="store_true")
    parser.add_argument("--scroll-right-frames", type=int, default=0, help="Перед снимком прокрутить карту вправо на N игровых кадров.")
    parser.add_argument("--viewport-x", type=int, default=None, help="Перед снимком выставить ViewportPixelX напрямую.")
    parser.add_argument("--viewport-y", type=int, default=None, help="Перед снимком выставить ViewportPixelY напрямую.")
    parser.add_argument("--after-initial-viewport-x", type=int, default=None, help="Сначала отрисовать стартовый кадр, затем выставить ViewportPixelX и снять следующий кадр.")
    parser.add_argument("--seed-origin0-then-viewport-x", type=int, default=None, help="Засеять RAM_G стартовым кэшем фона, затем снять один кадр с заданным ViewportPixelX.")
    args = parser.parse_args()

    emu = HMM2FullZ80Emulator(ROOT)
    regs = attach_hmm2_shadow(emu)

    def render_frame(max_steps: int = 30_000_000) -> None:
        regs.tick_frame(emu.ft.ram_dl)
        emu.call(emu.sym["Render_Frame"], max_steps=max_steps)

    emu.call(emu.sym["Platform_Init"], max_steps=4_000_000)
    if args.scroll_right_frames:
        emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
        emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=250_000_000)  # включает стрим HMM2MENU.PAK с SD
    if args.seed_origin0_then_viewport_x is not None:
        _seed_composite_cache_origin0(emu)
        emu.set_byte(emu.sym["RuntimeLastOriginX"], 0)
        emu.set_byte(emu.sym["RuntimeLastOriginY"], 0)
        emu.set_word(emu.sym["ViewportPixelX"], args.seed_origin0_then_viewport_x)
        emu.set_byte(emu.sym["ViewportOriginX"], min(args.seed_origin0_then_viewport_x // 32, 16))
        render_frame()
    elif args.after_initial_viewport_x is not None:
        render_frame()
        emu.set_word(emu.sym["ViewportPixelX"], args.after_initial_viewport_x)
        emu.set_byte(emu.sym["ViewportOriginX"], min(args.after_initial_viewport_x // 32, 16))
        render_frame()
    elif args.viewport_x is not None:
        emu.set_word(emu.sym["ViewportPixelX"], args.viewport_x)
        emu.set_byte(emu.sym["ViewportOriginX"], min(args.viewport_x // 32, 16))
    if args.viewport_y is not None:
        emu.set_word(emu.sym["ViewportPixelY"], args.viewport_y)
        emu.set_byte(emu.sym["ViewportOriginY"], min(args.viewport_y // 32, 21))
    if args.seed_origin0_then_viewport_x is not None:
        pass
    elif args.after_initial_viewport_x is not None:
        pass
    elif args.viewport_x is not None or args.viewport_y is not None:
        render_frame()
    elif args.scroll_right_frames:
        emu.set_word(emu.sym["CursorPixelX"], 624)
        emu.set_word(emu.sym["CursorPixelY"], 224)
        emu.call(emu.sym["Cursor_UpdateTileFromPixel"], max_steps=200_000)
        emu.input.kempston = 0x01
        for _ in range(args.scroll_right_frames):
            emu.call(emu.sym["Input_Poll"], max_steps=300_000)
            emu.call(emu.sym["Game_Update"], max_steps=300_000)
            render_frame(12_000_000)
    else:
        render_frame()

    # Для итогового снимка берем RAM_DL после Render_Frame, а не первый DLSWAP
    # из Init_Video.
    snap = bytes(emu.ft.ram_dl[:0x2000])
    ops = disasm_dl(snap, max_ops=4096)
    render_dl_png(ops, bytes(emu.ft.ram_g), args.out, regs._get32(REG_HSIZE) or 640, regs._get32(REG_VSIZE) or 480)

    print(f"png: {args.out}")
    print(
        "регистры: "
        f"hcycle={regs._get32(REG_HCYCLE)} hoffset={regs._get32(REG_HOFFSET)} hsize={regs._get32(REG_HSIZE)} "
        f"vcycle={regs._get32(REG_VCYCLE)} voffset={regs._get32(REG_VOFFSET)} vsize={regs._get32(REG_VSIZE)} "
        f"pclk={regs._get32(REG_PCLK)} frames={regs._get32(REG_FRAMES)} clock={regs._get32(REG_CLOCK)} "
        f"dlswap={regs._get32(REG_DLSWAP)} int_flags={regs._get32(REG_INT_FLAGS):02X}"
    )
    print(f"теневая модель: swaps={regs.swap_count} записей_dlswap={regs.dlswap_writes}")
    print(summarize_ops_ru(ops))
    if args.dump_dl:
        print(format_dl(ops))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
