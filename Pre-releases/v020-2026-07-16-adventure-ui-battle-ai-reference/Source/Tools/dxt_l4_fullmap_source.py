#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path


PAGE_SIZE = 0x4000
TABLE_PAGE = 0x8F
PAGE_BASE = 0x90
TILE_PX = 32
BLOCK_PX = 4
MAP_W = 36 * TILE_PX
MAP_H = 36 * TILE_PX
VIEW_TILES_W = 28
VIEW_TILES_H = 22
VISIBLE_TILES_W = 20
VISIBLE_TILES_H = 15
VIEW_W = VIEW_TILES_W * TILE_PX
VIEW_H = VIEW_TILES_H * TILE_PX
MAX_ORIGIN_X = 36 - VISIBLE_TILES_W
MAX_ORIGIN_Y = 36 - VISIBLE_TILES_H
MAX_ANCHOR_X = 36 - VIEW_TILES_W
MAX_ANCHOR_Y = 36 - VIEW_TILES_H


def layout(width: int, height: int) -> dict[str, int]:
    blocks_x = width // BLOCK_PX
    blocks_y = height // BLOCK_PX
    color_stride = blocks_x * 2
    color_size = color_stride * blocks_y
    mask_stride = width // 2
    return {
        "c0": 0,
        "c1": color_size,
        "mask": color_size * 2,
        "color_stride": color_stride,
        "mask_stride": mask_stride,
        "raw_size": color_size * 2 + mask_stride * height,
    }


def write_pages(out_dir: Path, raw: bytes) -> list[tuple[Path, int, int]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("SKIRMISH_FULLMAP_DXT_L4_p*.bin"):
        old.unlink()
    pages = []
    for index in range(math.ceil(len(raw) / PAGE_SIZE)):
        part = raw[index * PAGE_SIZE:(index + 1) * PAGE_SIZE]
        path = out_dir / f"SKIRMISH_FULLMAP_DXT_L4_p{index:02d}.bin"
        path.write_bytes(part + bytes(PAGE_SIZE - len(part)))
        pages.append((path, PAGE_BASE + index, len(part)))
    return pages


def page_addr(abs_offset: int) -> tuple[int, int]:
    return PAGE_BASE + abs_offset // PAGE_SIZE, 0xC000 + (abs_offset % PAGE_SIZE)


def write_inc(path: Path, raw_size: int, page_count: int) -> None:
    full = layout(MAP_W, MAP_H)
    view = layout(VIEW_W, VIEW_H)
    if raw_size != full["raw_size"]:
        raise ValueError(f"full raw size {raw_size} != {full['raw_size']}")

    lines = [
        "; Сгенерировано Source/Tools/dxt_l4_fullmap_source.py",
        "; Полный pseudo-DXT L4 terrain хранится в Z80/SPG страницах как источник.",
        "; В FT812 RAM_G копируется только якорное окно текущей карты.",
        "",
        f"BG_FULL_DXT_PAGE_BASE     EQU #{PAGE_BASE:02X}",
        f"BG_FULL_DXT_TABLE_PAGE    EQU #{TABLE_PAGE:02X}",
        f"BG_FULL_DXT_PAGE_COUNT    EQU {page_count}",
        f"BG_FULL_DXT_RAW_SIZE      EQU {raw_size}",
        f"BG_FULL_DXT_W             EQU {MAP_W}",
        f"BG_FULL_DXT_H             EQU {MAP_H}",
        f"BG_FULL_DXT_C0_OFFSET     EQU {full['c0']}",
        f"BG_FULL_DXT_C1_OFFSET     EQU {full['c1']}",
        f"BG_FULL_DXT_MASK_OFFSET   EQU {full['mask']}",
        f"BG_FULL_DXT_COLOR_STRIDE  EQU {full['color_stride']}",
        f"BG_FULL_DXT_MASK_STRIDE   EQU {full['mask_stride']}",
        "BG_DXT_ANCHORED_WINDOW    EQU 1",
        f"BG_DXT_ANCHOR_MAX_X       EQU {MAX_ANCHOR_X}",
        f"BG_DXT_ANCHOR_MAX_Y       EQU {MAX_ANCHOR_Y}",
        "",
        "BackgroundDxt_UploadWindow:",
        "                if BG_DXT_RAW_SIZE",
        "                GetPage3",
        "                LD   (BackgroundDxt_RestorePage), A",
        "                CALL BackgroundDxt_UpdateAnchor",
        "                LD   A, (BackgroundDxtAnchorChanged)",
        "                OR   A",
        "                JR   NZ, BackgroundDxt_DoUpload",
        "                JP   BackgroundDxt_RestorePage",
        "",
        "BackgroundDxt_DoUpload:",
        "                SetPage3 BG_FULL_DXT_TABLE_PAGE",
        "",
        "                LD   A, (BackgroundDxtOriginY)",
        "                LD   L, A",
        "                LD   H, 0",
        "                LD   D, H",
        "                LD   E, L",
        "                ADD  HL, HL",
        "                ADD  HL, HL",
        "                ADD  HL, HL",
        "                ADD  HL, DE",
        "                LD   A, (BackgroundDxtOriginX)",
        "                LD   E, A",
        "                LD   D, 0",
        "                ADD  HL, DE",
        "                ADD  HL, HL",
        "                ADD  HL, HL",
        "                ADD  HL, HL",
        "                ADD  HL, HL",
        "                LD   DE, #C000",
        "                ADD  HL, DE",
        "                LD   (BackgroundDxt_TablePtr), HL",
        "",
        "                CALL BackgroundDxt_LoadEntry",
        "                LD   A, BG_DXT_RAMG >> 16",
        "                LD   (BackgroundDxt_DstHigh), A",
        "                LD   HL, BG_DXT_RAMG & #FFFF",
        "                LD   (BackgroundDxt_DstLow), HL",
        "                LD   HL, BG_FULL_DXT_COLOR_STRIDE",
        "                LD   (BackgroundDxt_SrcStride), HL",
        "                LD   HL, BG_DXT_COLOR_STRIDE",
        "                LD   (BackgroundDxt_DstStride), HL",
        "                LD   HL, BG_DXT_COLOR_H",
        "                LD   (BackgroundDxt_Rows), HL",
        "                LD   HL, BG_DXT_COLOR_STRIDE",
        "                LD   (BackgroundDxt_RowBytes), HL",
        "                CALL BackgroundDxt_CopyRows",
        "",
        "                CALL BackgroundDxt_LoadEntry",
        "                LD   A, (BG_DXT_RAMG + BG_DXT_C1_OFFSET) >> 16",
        "                LD   (BackgroundDxt_DstHigh), A",
        "                LD   HL, (BG_DXT_RAMG + BG_DXT_C1_OFFSET) & #FFFF",
        "                LD   (BackgroundDxt_DstLow), HL",
        "                LD   HL, BG_FULL_DXT_COLOR_STRIDE",
        "                LD   (BackgroundDxt_SrcStride), HL",
        "                LD   HL, BG_DXT_COLOR_STRIDE",
        "                LD   (BackgroundDxt_DstStride), HL",
        "                LD   HL, BG_DXT_COLOR_H",
        "                LD   (BackgroundDxt_Rows), HL",
        "                LD   HL, BG_DXT_COLOR_STRIDE",
        "                LD   (BackgroundDxt_RowBytes), HL",
        "                CALL BackgroundDxt_CopyRows",
        "",
        "                CALL BackgroundDxt_LoadEntry",
        "                LD   A, (BG_DXT_RAMG + BG_DXT_MASK_OFFSET) >> 16",
        "                LD   (BackgroundDxt_DstHigh), A",
        "                LD   HL, (BG_DXT_RAMG + BG_DXT_MASK_OFFSET) & #FFFF",
        "                LD   (BackgroundDxt_DstLow), HL",
        "                LD   HL, BG_FULL_DXT_MASK_STRIDE",
        "                LD   (BackgroundDxt_SrcStride), HL",
        "                LD   HL, BG_DXT_MASK_STRIDE",
        "                LD   (BackgroundDxt_DstStride), HL",
        "                LD   HL, BG_DXT_H",
        "                LD   (BackgroundDxt_Rows), HL",
        "                LD   HL, BG_DXT_MASK_STRIDE",
        "                LD   (BackgroundDxt_RowBytes), HL",
        "                CALL BackgroundDxt_CopyRows",
        "",
        "                JP   BackgroundDxt_RestorePage",
        "",
        "BackgroundDxt_UpdateAnchor:",
        "                XOR  A",
        "                LD   (BackgroundDxtAnchorChanged), A",
        "",
        "                LD   A, (ViewportOriginX)",
        "                AND  #F8",
        "                CP   BG_DXT_ANCHOR_MAX_X + 1",
        "                JR   C, BackgroundDxt_AnchorXOk",
        "                LD   A, BG_DXT_ANCHOR_MAX_X",
        "BackgroundDxt_AnchorXOk:",
        "                LD   B, A",
        "                LD   A, (BackgroundDxtOriginX)",
        "                CP   B",
        "                JR   Z, BackgroundDxt_AnchorY",
        "                LD   A, B",
        "                LD   (BackgroundDxtOriginX), A",
        "                LD   A, 1",
        "                LD   (BackgroundDxtAnchorChanged), A",
        "",
        "BackgroundDxt_AnchorY:",
        "                LD   A, (ViewportOriginY)",
        "                CP   14",
        "                JR   C, BackgroundDxt_AnchorYCheck7",
        "                LD   A, 14",
        "                JR   BackgroundDxt_AnchorYHave",
        "BackgroundDxt_AnchorYCheck7:",
        "                CP   7",
        "                JR   C, BackgroundDxt_AnchorYZero",
        "                LD   A, 7",
        "                JR   BackgroundDxt_AnchorYHave",
        "BackgroundDxt_AnchorYZero:",
        "                XOR  A",
        "BackgroundDxt_AnchorYHave:",
        "                LD   B, A",
        "                LD   A, (BackgroundDxtOriginY)",
        "                CP   B",
        "                RET  Z",
        "                LD   A, B",
        "                LD   (BackgroundDxtOriginY), A",
        "                LD   A, 1",
        "                LD   (BackgroundDxtAnchorChanged), A",
        "                RET",
        "",
        "BackgroundDxt_ResetAnchor:",
        "                LD   A, #FF",
        "                LD   (BackgroundDxtOriginX), A",
        "                LD   (BackgroundDxtOriginY), A",
        "                RET",
        "",
        "BackgroundDxt_RestorePage EQU $+1",
        "                LD   A, #00",
        "                SetPage3_A",
        "                endif",
        "                RET",
        "",
        "BackgroundDxt_LoadEntry:",
        "                LD   HL, (BackgroundDxt_TablePtr)",
        "                LD   A, (HL)",
        "                LD   (BackgroundDxt_SourcePage), A",
        "                INC  HL",
        "                LD   E, (HL)",
        "                INC  HL",
        "                LD   D, (HL)",
        "                INC  HL",
        "                LD   (BackgroundDxt_SourceAddr), DE",
        "                LD   (BackgroundDxt_TablePtr), HL",
        "                RET",
        "",
        "BackgroundDxt_CopyRows:",
        "                LD   HL, (BackgroundDxt_Rows)",
        "                LD   A, H",
        "                OR   L",
        "                RET  Z",
        "                CALL BackgroundDxt_CopyRow",
        "",
        "                LD   HL, (BackgroundDxt_SourceAddr)",
        "                LD   BC, (BackgroundDxt_SrcStride)",
        "                ADD  HL, BC",
        "                JR   NC, BackgroundDxt_SourceNoCarry",
        "                LD   A, H",
        "                OR   #C0",
        "                LD   H, A",
        "                LD   A, (BackgroundDxt_SourcePage)",
        "                INC  A",
        "                LD   (BackgroundDxt_SourcePage), A",
        "BackgroundDxt_SourceNoCarry:",
        "                LD   (BackgroundDxt_SourceAddr), HL",
        "",
        "                LD   HL, (BackgroundDxt_DstLow)",
        "                LD   BC, (BackgroundDxt_DstStride)",
        "                ADD  HL, BC",
        "                LD   (BackgroundDxt_DstLow), HL",
        "                JR   NC, BackgroundDxt_DstNoCarry",
        "                LD   A, (BackgroundDxt_DstHigh)",
        "                INC  A",
        "                LD   (BackgroundDxt_DstHigh), A",
        "BackgroundDxt_DstNoCarry:",
        "",
        "                LD   HL, (BackgroundDxt_Rows)",
        "                DEC  HL",
        "                LD   (BackgroundDxt_Rows), HL",
        "                JR   BackgroundDxt_CopyRows",
        "",
        "BackgroundDxt_CopyRow:",
        "                LD   HL, (BackgroundDxt_SourceAddr)",
        "                LD   BC, (BackgroundDxt_RowBytes)",
        "                ADD  HL, BC",
        "                JR   C, BackgroundDxt_CopyRowSplit",
        "                LD   A, (BackgroundDxt_SourcePage)",
        "                LD   (Render_DmaSourcePage), A",
        "                LD   HL, (BackgroundDxt_SourceAddr)",
        "                LD   A, (BackgroundDxt_DstHigh)",
        "                LD   DE, (BackgroundDxt_DstLow)",
        "                LD   BC, (BackgroundDxt_RowBytes)",
        "                CALL Render_WriteMem_DMA",
        "                RET",
        "",
        "BackgroundDxt_CopyRowSplit:",
        "                LD   HL, (BackgroundDxt_SourceAddr)",
        "                LD   DE, 0",
        "                EX   DE, HL",
        "                OR   A",
        "                SBC  HL, DE",
        "                LD   (BackgroundDxt_FirstLen), HL",
        "                LD   HL, (BackgroundDxt_RowBytes)",
        "                LD   DE, (BackgroundDxt_FirstLen)",
        "                OR   A",
        "                SBC  HL, DE",
        "                LD   (BackgroundDxt_SecondLen), HL",
        "",
        "                LD   A, (BackgroundDxt_SourcePage)",
        "                LD   (Render_DmaSourcePage), A",
        "                LD   HL, (BackgroundDxt_SourceAddr)",
        "                LD   A, (BackgroundDxt_DstHigh)",
        "                LD   DE, (BackgroundDxt_DstLow)",
        "                LD   BC, (BackgroundDxt_FirstLen)",
        "                CALL Render_WriteMem_DMA",
        "",
        "                LD   HL, (BackgroundDxt_DstLow)",
        "                LD   BC, (BackgroundDxt_FirstLen)",
        "                ADD  HL, BC",
        "                LD   (BackgroundDxt_TempDstLow), HL",
        "                LD   A, (BackgroundDxt_DstHigh)",
        "                JR   NC, BackgroundDxt_TempDstNoCarry",
        "                INC  A",
        "BackgroundDxt_TempDstNoCarry:",
        "                LD   (BackgroundDxt_TempDstHigh), A",
        "",
        "                LD   A, (BackgroundDxt_SourcePage)",
        "                INC  A",
        "                LD   (Render_DmaSourcePage), A",
        "                LD   HL, #C000",
        "BackgroundDxt_TempDstHigh EQU $+1",
        "                LD   A, #00",
        "BackgroundDxt_TempDstLow EQU $+1",
        "                LD   DE, #0000",
        "                LD   BC, (BackgroundDxt_SecondLen)",
        "                CALL Render_WriteMem_DMA",
        "                RET",
        "",
        "BackgroundDxt_TablePtr:    DEFW 0",
        "BackgroundDxt_SourceAddr:  DEFW 0",
        "BackgroundDxt_SourcePage:  DEFB 0",
        "BackgroundDxt_DstLow:      DEFW 0",
        "BackgroundDxt_DstHigh:     DEFB 0",
        "BackgroundDxt_SrcStride:   DEFW 0",
        "BackgroundDxt_DstStride:   DEFW 0",
        "BackgroundDxt_RowBytes:    DEFW 0",
        "BackgroundDxt_Rows:        DEFW 0",
        "BackgroundDxt_FirstLen:    DEFW 0",
        "BackgroundDxt_SecondLen:   DEFW 0",
        "BackgroundDxtOriginX:      DEFB 0",
        "BackgroundDxtOriginY:      DEFB 0",
        "BackgroundDxtAnchorChanged: DEFB 0",
    ]

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_table(path: Path) -> None:
    full = layout(MAP_W, MAP_H)
    table = bytearray()
    for oy in range(MAX_ANCHOR_Y + 1):
        for ox in range(MAX_ANCHOR_X + 1):
            pixel_x = ox * TILE_PX
            pixel_y = oy * TILE_PX
            block_x = pixel_x // BLOCK_PX
            block_y = pixel_y // BLOCK_PX
            color_x = block_x * 2
            mask_x = pixel_x // 2
            c0_abs = full["c0"] + block_y * full["color_stride"] + color_x
            c1_abs = full["c1"] + block_y * full["color_stride"] + color_x
            mask_abs = full["mask"] + pixel_y * full["mask_stride"] + mask_x
            for abs_offset in (c0_abs, c1_abs, mask_abs):
                page, addr = page_addr(abs_offset)
                table.append(page)
                table.extend(addr.to_bytes(2, "little"))
            table.extend(bytes(7))
    if len(table) > PAGE_SIZE:
        raise ValueError(f"table too large: {len(table)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(table + bytes(PAGE_SIZE - len(table)))


def update_spgbld(path: Path, table_path: Path, pages: list[tuple[Path, int, int]]) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "; Страницы terrain atlas."
    section = "; Страницы полного pseudo-DXT L4 background как source pages."
    if marker not in text:
        raise ValueError(f"{path}: не найден marker '{marker}'")
    text = text.split(section, 1)[0].rstrip() + "\n\n" + marker + text.split(marker, 1)[1]
    head, tail = text.split(marker, 1)
    if marker in tail:
        tail = tail.split(marker, 1)[0].rstrip() + "\n"
    lines = [head.rstrip(), "", section]
    lines.append(f"Block = #0000, #{TABLE_PAGE:02X}, {table_path.as_posix()}")
    for page_path, page, _size in pages:
        lines.append(f"Block = #0000, #{page:02X}, {page_path.as_posix()}")
    lines.extend(["", marker + tail])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Подготовить full-map DXT source pages и ASM loader.")
    parser.add_argument("--raw", type=Path, default=Path("Assets/Converted/Background/SKIRMISH_FULLMAP_DXT_L4.raw"))
    parser.add_argument("--out-dir", type=Path, default=Path("Assets/Converted/Background"))
    parser.add_argument("--inc", type=Path, default=Path("Source/ASM/generated_fullmap_dxt.inc"))
    parser.add_argument("--table", type=Path, default=Path("Assets/Converted/Background/SKIRMISH_FULLMAP_DXT_TABLE.bin"))
    parser.add_argument("--spgbld", type=Path, default=Path("spgbld_vdac2.ini"))
    args = parser.parse_args()

    raw = args.raw.read_bytes()
    pages = write_pages(args.out_dir, raw)
    write_table(args.table)
    write_inc(args.inc, len(raw), len(pages))
    update_spgbld(args.spgbld, args.table, pages)
    print(f"fullmap source raw={len(raw)} bytes, pages={len(pages)}, table_page=#{TABLE_PAGE:02X}, page_base=#{PAGE_BASE:02X}")
    print(f"inc={args.inc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
