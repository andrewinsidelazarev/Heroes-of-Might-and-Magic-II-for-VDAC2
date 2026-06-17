#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import struct
from pathlib import Path


PAGE_SIZE = 0x4000
RAMG_BG_BASE = 0x000000
BG_PAGE_BASE = 0x40


def read_d1l4(path: Path):
    data = path.read_bytes()
    if len(data) < 16:
        raise ValueError(f"{path}: DXT файл слишком короткий")
    magic = data[:4]
    if magic != b"D1L4":
        raise ValueError(f"{path}: ожидался D1L4, получено {magic!r}")
    width, height, block_count = struct.unpack_from("<III", data, 4)
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    expected_blocks = blocks_x * blocks_y
    if block_count != expected_blocks:
        raise ValueError(f"{path}: blocks={block_count}, ожидалось {expected_blocks}")
    expected_size = 16 + block_count * 12
    if len(data) != expected_size:
        raise ValueError(f"{path}: размер {len(data)}, ожидалось {expected_size}")

    blocks = []
    off = 16
    for _ in range(block_count):
        c0, c1 = struct.unpack_from("<HH", data, off)
        selectors = data[off + 4:off + 12]
        blocks.append((c0, c1, selectors))
        off += 12
    return width, height, blocks_x, blocks_y, blocks


def make_raw(width: int, height: int, blocks_x: int, blocks_y: int, blocks):
    # Формат raw для FT812: слой c0 RGB565, слой c1 RGB565, L4 mask 640x480.
    c0 = bytearray()
    c1 = bytearray()
    for color0, color1, _ in blocks:
        c0.extend(struct.pack("<H", color0))
        c1.extend(struct.pack("<H", color1))

    mask_stride = (width + 1) // 2
    mask = bytearray(mask_stride * height)
    for y in range(height):
        row = y * mask_stride
        by = y // 4
        py = y & 3
        for xb in range(mask_stride):
            value = 0
            for p in range(2):
                x = xb * 2 + p
                if x >= width:
                    continue
                bx = x // 4
                px = x & 3
                _, _, selectors = blocks[by * blocks_x + bx]
                sel = selectors[py * 4 + px] & 0x0F
                if p == 0:
                    value |= sel << 4
                else:
                    value |= sel
            mask[row + xb] = value
    return bytes(c0 + c1 + mask)


def write_chunks(out_dir: Path, payload: bytes):
    out_dir.mkdir(parents=True, exist_ok=True)
    chunks = []
    for i in range(math.ceil(len(payload) / PAGE_SIZE)):
        chunk = payload[i * PAGE_SIZE:(i + 1) * PAGE_SIZE]
        padded = chunk + b"\0" * (PAGE_SIZE - len(chunk))
        path = out_dir / f"HMM2_BG_L4_p{i:02d}.bin"
        path.write_bytes(padded)
        chunks.append((path, len(chunk)))
    return chunks


def write_inc(path: Path, chunks, width: int, height: int, blocks_x: int, blocks_y: int, raw_size: int):
    c0_size = blocks_x * blocks_y * 2
    c1_offset = c0_size
    mask_offset = c0_size * 2
    mask_stride = (width + 1) // 2
    lines = [
        "; Сгенерировано Source/Tools/dxt_background.py",
        "; Host-side pseudo-DXT L4 фон: c0 RGB565 + c1 RGB565 + L4 mask.",
        "",
        f"BG_DXT_RAMG          EQU #{RAMG_BG_BASE:06X}",
        f"BG_DXT_PAGE_BASE     EQU #{BG_PAGE_BASE:02X}",
        f"BG_DXT_PAGE_COUNT    EQU {len(chunks)}",
        f"BG_DXT_RAW_SIZE      EQU {raw_size}",
        f"BG_DXT_W             EQU {width}",
        f"BG_DXT_H             EQU {height}",
        f"BG_DXT_BLOCKS_X      EQU {blocks_x}",
        f"BG_DXT_BLOCKS_Y      EQU {blocks_y}",
        f"BG_DXT_C0_OFFSET     EQU 0",
        f"BG_DXT_C1_OFFSET     EQU {c1_offset}",
        f"BG_DXT_MASK_OFFSET   EQU {mask_offset}",
        f"BG_DXT_COLOR_STRIDE  EQU {blocks_x * 2}",
        f"BG_DXT_COLOR_H       EQU {blocks_y}",
        f"BG_DXT_MASK_STRIDE   EQU {mask_stride}",
        "",
        "Background_Upload:",
        "                GetPage3",
        "                LD   (.RestorePage), A",
    ]
    ramg = RAMG_BG_BASE
    for i, (_, real_size) in enumerate(chunks):
        lines.extend(
            [
                f"                SetPage3 #{BG_PAGE_BASE + i:02X}",
                "                LD   HL, #C000",
                f"                LD   A, #{(ramg >> 16) & 0xFF:02X}",
                f"                LD   DE, #{ramg & 0xFFFF:04X}",
                f"                LD   BC, {real_size}",
                "                CALL FT.WriteMem",
            ]
        )
        ramg += real_size
    lines.extend(
        [
            ".RestorePage    EQU $+1",
            "                LD   A, #00",
            "                SetPage3_A",
            "                RET",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_dl(path: Path):
    lines = [
        "; Сгенерировано Source/Tools/dxt_background.py",
        "; Вывод L4 pseudo-DXT: mask -> dst alpha, затем c1/c0 через alpha blend.",
        "",
        "ADVENTURE_DL:",
        "                FT_CLEAR_COLOR_RGB 0, 0, 0",
        "                FT_CLEAR_COLOR_A 0",
        "                FT_CLEAR 1, 1, 1",
        "                FT_VERTEX_FORMAT 4",
        "",
        "                ; Pass 1: L4 mask пишет только alpha.",
        "                FT_COLOR_MASK 0, 0, 0, 1",
        "                FT_COLOR_RGB 255, 255, 255",
        "                FT_COLOR_A 255",
        "                FT_BLEND_FUNC FT_ONE, FT_ZERO",
        "                FT_BITMAP_HANDLE 1",
        "                FT_BITMAP_SOURCE BG_DXT_RAMG + BG_DXT_MASK_OFFSET",
        "                FT_BITMAP_LAYOUT FT_L4, BG_DXT_MASK_STRIDE, BG_DXT_H",
        "                FT_BITMAP_SIZE_H BG_DXT_W, BG_DXT_H",
        "                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, BG_DXT_W, BG_DXT_H",
        "                FT_BEGIN FT_BITMAPS",
        "                FT_VERTEX2F 0, 0",
        "                FT_END",
        "",
        "                ; Pass 2: c1 * dst_alpha.",
        "                FT_COLOR_MASK 1, 1, 1, 0",
        "                FT_BLEND_FUNC FT_DST_ALPHA, FT_ZERO",
        "                FT_BITMAP_HANDLE 0",
        "                FT_BITMAP_SOURCE BG_DXT_RAMG + BG_DXT_C1_OFFSET",
        "                FT_BITMAP_LAYOUT FT_RGB565, BG_DXT_COLOR_STRIDE, BG_DXT_COLOR_H",
        "                FT_BITMAP_SIZE_H BG_DXT_W, BG_DXT_H",
        "                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, BG_DXT_W, BG_DXT_H",
        "                FT_BITMAP_TRANSFORM_A 64",
        "                FT_BITMAP_TRANSFORM_B 0",
        "                FT_BITMAP_TRANSFORM_D 0",
        "                FT_BITMAP_TRANSFORM_E 64",
        "                FT_BEGIN FT_BITMAPS",
        "                FT_VERTEX2F 0, 0",
        "                FT_END",
        "",
        "                ; Pass 3: c0 * (1 - dst_alpha) + dst.",
        "                FT_BLEND_FUNC FT_ONE_MINUS_DST_ALPHA, FT_ONE",
        "                FT_BITMAP_SOURCE BG_DXT_RAMG + BG_DXT_C0_OFFSET",
        "                FT_BITMAP_LAYOUT FT_RGB565, BG_DXT_COLOR_STRIDE, BG_DXT_COLOR_H",
        "                FT_BITMAP_SIZE_H BG_DXT_W, BG_DXT_H",
        "                FT_BITMAP_SIZE FT_NEAREST, FT_BORDER, FT_BORDER, BG_DXT_W, BG_DXT_H",
        "                FT_BITMAP_TRANSFORM_A 64",
        "                FT_BITMAP_TRANSFORM_B 0",
        "                FT_BITMAP_TRANSFORM_D 0",
        "                FT_BITMAP_TRANSFORM_E 64",
        "                FT_BEGIN FT_BITMAPS",
        "                FT_VERTEX2F 0, 0",
        "                FT_END",
        "",
        "                FT_COLOR_MASK 1, 1, 1, 1",
        "                FT_BLEND_FUNC FT_ONE, FT_ZERO",
        "                FT_DISPLAY",
        "ADVENTURE_DL_SIZE EQU $ - ADVENTURE_DL",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_empty_objects_inc(path: Path, object_dir: Path = Path("Assets/Converted/Objects")):
    object_dir.mkdir(parents=True, exist_ok=True)
    for old_chunk in object_dir.glob("SKIRMISH_OBJECTS_p*.bin"):
        old_chunk.unlink()
    lines = [
        "; Сгенерировано Source/Tools/dxt_background.py",
        "; Object overlay отключен: фон уже запечен host-side pseudo-DXT.",
        "",
        "OBJECT_ATLAS_RAMG       EQU #03A800",
        "OBJECT_ATLAS_PAGE_BASE  EQU #30",
        "OBJECT_ATLAS_PAGE_COUNT EQU 0",
        "OBJECT_ATLAS_SIZE       EQU 0",
        "",
        "Objects_Upload:",
        "                RET",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def update_spgbld(path: Path, chunks):
    text = path.read_text(encoding="utf-8")
    for marker in ("; Страницы pseudo-DXT background.", "; Страницы object atlas.", "; Страницы terrain atlas."):
        if marker in text and marker == "; Страницы pseudo-DXT background.":
            text = text.split(marker, 1)[0].rstrip()
            break
    lines = [text.rstrip(), "", "; Страницы pseudo-DXT background."]
    for i, (chunk_path, _) in enumerate(chunks):
        lines.append(f"Block = #0000, #{BG_PAGE_BASE + i:02X}, {chunk_path.as_posix()}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Подготовить host-side D1L4 фон для FT812.")
    parser.add_argument("--raw", type=Path, default=Path("Assets/Converted/Background/hmm2_ft812_snapshot_l4.raw"))
    parser.add_argument("--dxt", type=Path, default=Path("Assets/Converted/Background/hmm2_ft812_snapshot_l4.dxt"))
    parser.add_argument("--out-dir", type=Path, default=Path("Assets/Converted/Background"))
    parser.add_argument("--inc", type=Path, default=Path("Source/ASM/generated_background.inc"))
    parser.add_argument("--dl-inc", type=Path, default=Path("Source/ASM/generated_adventure_dl.inc"))
    parser.add_argument("--spgbld", type=Path, default=Path("spgbld_vdac2.ini"))
    parser.add_argument("--objects-inc", type=Path, default=Path("Source/ASM/generated_objects.inc"))
    args = parser.parse_args()

    width, height = 640, 480
    blocks_x, blocks_y = 160, 120
    raw_size = blocks_x * blocks_y * 2 * 2 + ((width + 1) // 2) * height
    raw_path = args.raw
    if raw_path.exists():
        raw = raw_path.read_bytes()
        if len(raw) != raw_size:
            raise ValueError(f"{raw_path}: размер {len(raw)}, ожидалось {raw_size}")
    else:
        width, height, blocks_x, blocks_y, blocks = read_d1l4(args.dxt)
        raw = make_raw(width, height, blocks_x, blocks_y, blocks)
        raw_path = args.out_dir / "hmm2_ft812_snapshot_l4.raw"
        raw_path.write_bytes(raw)
    chunks = write_chunks(args.out_dir, raw)
    write_inc(args.inc, chunks, width, height, blocks_x, blocks_y, len(raw))
    write_dl(args.dl_inc)
    write_empty_objects_inc(args.objects_inc)
    update_spgbld(args.spgbld, chunks)
    print(f"background raw: {width}x{height}, blocks={blocks_x * blocks_y}, raw={len(raw)} bytes")
    print(f"raw: {raw_path}")
    print(f"pages: {len(chunks)}, base=#{BG_PAGE_BASE:02X}")


if __name__ == "__main__":
    main()
