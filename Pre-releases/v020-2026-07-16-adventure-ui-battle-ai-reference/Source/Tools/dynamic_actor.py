#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from agg_tools import read_agg_index
from object_atlas import agg_entry, decode_icn_sprite, read_icn, read_palette


PAGE_SIZE = 0x4000
RAMG_OBJECT_BASE = 0x03A800
OBJECT_PAGE_BASE = 0x30


def write_chunks(out_dir: Path, payload: bytes):
    out_dir.mkdir(parents=True, exist_ok=True)
    for old_chunk in out_dir.glob("SKIRMISH_OBJECTS_p*.bin"):
        old_chunk.unlink()
    chunks = []
    for i in range(math.ceil(len(payload) / PAGE_SIZE)):
        chunk = payload[i * PAGE_SIZE:(i + 1) * PAGE_SIZE]
        padded = chunk + b"\0" * (PAGE_SIZE - len(chunk))
        path = out_dir / f"SKIRMISH_OBJECTS_p{i:02d}.bin"
        path.write_bytes(padded)
        chunks.append((path, len(chunk)))
    return chunks


def write_objects_inc(path: Path, chunks, total_size: int, width: int, height: int) -> None:
    lines = [
        "; Сгенерировано Source/Tools/dynamic_actor.py",
        "; Один безопасный динамический герой поверх pseudo-DXT карты.",
        "",
        f"OBJECT_ATLAS_RAMG       EQU #{RAMG_OBJECT_BASE:06X}",
        f"OBJECT_ATLAS_PAGE_BASE  EQU #{OBJECT_PAGE_BASE:02X}",
        f"OBJECT_ATLAS_PAGE_COUNT EQU {len(chunks)}",
        f"OBJECT_ATLAS_SIZE       EQU {total_size}",
        f"DYNAMIC_ACTOR_RAMG      EQU #{RAMG_OBJECT_BASE:06X}",
        f"DYNAMIC_ACTOR_W         EQU {width}",
        f"DYNAMIC_ACTOR_H         EQU {height}",
        "",
        "Objects_Upload:",
        "                GetPage3",
        "                LD   (.RestorePage), A",
    ]
    ramg = RAMG_OBJECT_BASE
    for i, (_, real_size) in enumerate(chunks):
        lines.extend(
            [
                f"                SetPage3 #{OBJECT_PAGE_BASE + i:02X}",
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


def update_spgbld(path: Path, chunks) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.split("; Страницы object atlas.", 1)[0].rstrip()
    lines = [text, "", "; Страницы object atlas."]
    for i, (chunk_path, _) in enumerate(chunks):
        lines.append(f"Block = #0000, #{OBJECT_PAGE_BASE + i:02X}, {chunk_path.as_posix()}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_preview(path: Path, payload: bytes, width: int, height: int) -> None:
    try:
        from PIL import Image
    except ImportError:
        return
    pixels = []
    for i in range(width * height):
        value = payload[i * 2] | (payload[i * 2 + 1] << 8)
        a = ((value >> 12) & 15) * 17
        r = ((value >> 8) & 15) * 17
        g = ((value >> 4) & 15) * 17
        b = (value & 15) * 17
        pixels.append((r, g, b, a))
    img = Image.new("RGBA", (width, height))
    img.putdata(pixels)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Собрать один динамический MINIHERO-спрайт для FT812.")
    parser.add_argument("--agg", type=Path, default=Path("Assets/Original/DATA/HEROES2.AGG"))
    parser.add_argument("--out-dir", type=Path, default=Path("Assets/Converted/Objects"))
    parser.add_argument("--objects-inc", type=Path, default=Path("Source/ASM/generated_objects.inc"))
    parser.add_argument("--spgbld", type=Path, default=Path("spgbld_vdac2.ini"))
    parser.add_argument("--preview", type=Path, default=Path("Diagnostics/dynamic_actor_preview.png"))
    parser.add_argument("--frame", type=int, default=8)
    args = parser.parse_args()

    agg_data, entries = read_agg_index(args.agg)
    palette = read_palette(agg_entry(agg_data, entries, "KB.PAL"))
    sprites = read_icn(agg_entry(agg_data, entries, "MINIHERO.ICN"))
    if args.frame < 0 or args.frame >= len(sprites):
        raise ValueError(f"MINIHERO.ICN: кадр {args.frame} вне диапазона 0..{len(sprites) - 1}")
    header, encoded = sprites[args.frame]
    payload = decode_icn_sprite(header, encoded, palette)
    chunks = write_chunks(args.out_dir, payload)
    write_objects_inc(args.objects_inc, chunks, len(payload), header["w"], header["h"])
    update_spgbld(args.spgbld, chunks)
    write_preview(args.preview, payload, header["w"], header["h"])

    print(f"dynamic actor: MINIHERO.ICN frame={args.frame}, {header['w']}x{header['h']}, bytes={len(payload)}")
    print(f"pages: {len(chunks)}, base=#{OBJECT_PAGE_BASE:02X}, ram_g=#{RAMG_OBJECT_BASE:06X}")
    print(f"preview: {args.preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
