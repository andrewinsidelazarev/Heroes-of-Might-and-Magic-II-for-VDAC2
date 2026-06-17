#!/usr/bin/env python3
"""Audit: which animated object parts actually appear on SKIRMISH.MX2.

Cross-references on-map (icn, icn_index) parts against object_animation.csv,
reports distinct animated parts, tile usage counts, extra frame counts, and an
estimated PALETTED4444 atlas-byte cost if all on-map frames were pre-packed.
"""
import csv
from collections import Counter, defaultdict
from pathlib import Path

import map_tools
from object_atlas import (
    ICN_BY_OBJECT_TYPE,
    agg_entry,
    read_icn,
)
from agg_tools import read_agg_index_with_expansion

ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT / "Assets" / "Original" / "MAPS" / "SKIRMISH.MX2"
ANIM_CSV = ROOT / "Assets" / "Converted" / "Maps" / "object_animation.csv"
AGG_PATH = ROOT / "Assets" / "Original" / "DATA" / "HEROES2.AGG"

WATER_ICNS = {"OBJNWATR.ICN", "OBJNWAT2.ICN"}

# Lightweight categorisation by ICN tileset (HMM2 object tilesets).
CAMPFIRE_KEYS = set()   # campfires live in OBJNMUL2/OBJNMULT (generic adventure objects)
# We tag by (icn, base_index) via fheroes2 object semantics below.


def load_anim_csv():
    """(ICN, base_index) -> frames"""
    out = {}
    with ANIM_CSV.open("r", encoding="utf-8") as fp:
        for row in csv.DictReader(fp):
            out[(row["icn"].strip().upper(), int(row["index"]))] = int(row["frames"])
    return out


def categorize(icn, index):
    """Best-effort human label for an animated part."""
    icn = icn.upper()
    if icn in ("OBJNLAVA.ICN", "OBJNLAV2.ICN", "OBJNLAV3.ICN"):
        return "lava"
    if icn in ("OBJNWATR.ICN", "OBJNWAT2.ICN"):
        return "water"
    # Generic adventure objects: OBJNMUL2 / OBJNMULT hold campfires, windmills,
    # fountains, fire, etc. fheroes2 object ids per index ranges:
    #   OBJNMUL2 index 240/241/248 region -> campfire/fire family
    #   OBJNMULT index 90/97/104/124/131 -> fire/campfire family
    # We keep a coarse label; exact semantic id needs fheroes2_object_info.csv.
    return "terrain-decor / generic-adventure"


def main():
    print(f"MAP: {MAP_PATH}")
    print(f"ANIM CSV: {ANIM_CSV}")
    print()

    anim = load_anim_csv()
    header, tiles, addons = map_tools.read_mp2(MAP_PATH)
    width, height = header["width"], header["height"]
    print(f"Map '{header['name']}' {width}x{height}, tiles={header['tile_count']}, addons={len(addons)}")
    print()

    # Enumerate every object PART present on every tile (same enumeration the
    # packer uses): icn = ICN_BY_OBJECT_TYPE[object_name>>2], index = icn_index.
    # We count distinct TILES that carry each animated (icn, index).
    tile_count = Counter()        # (icn, index) -> number of tiles carrying it
    part_count = Counter()        # (icn, index) -> number of part occurrences
    from viewport_pack import tile_object_parts_original

    for y in range(height):
        for x in range(width):
            tile = tiles[y * width + x]
            seen_on_tile = set()
            for part in tile_object_parts_original(tile, addons, x, y):
                key = (part["icn"].upper(), part["index"])
                if key in anim:
                    part_count[key] += 1
                    if key not in seen_on_tile:
                        tile_count[key] += 1
                        seen_on_tile.add(key)

    if not tile_count:
        print("No animated parts found on map.")
        return

    # Resolve sprite dimensions from the AGG so the byte estimate is real, not
    # assumed. PALETTED4444 packs 1 byte/pixel of *index* data (the engine's
    # COMPOSITE_TILE_BYTES uses w*h for PALETTED4444). We report BOTH the
    # task's stated formula (w*h/2) and the engine-accurate (w*h).
    agg_data, entries = read_agg_index_with_expansion(AGG_PATH)
    icn_cache = {}

    def frame_dims(icn, base_index, frame_offset):
        """Return (w,h) of frame = base_index+frame_offset, or None."""
        if icn not in icn_cache:
            try:
                icn_cache[icn] = read_icn(agg_entry(agg_data, entries, icn))
            except Exception:
                icn_cache[icn] = None
        sprites = icn_cache[icn]
        if not sprites:
            return None
        idx = base_index + frame_offset
        if idx < 0 or idx >= len(sprites):
            return None
        hdr = sprites[idx][0]
        return hdr["w"], hdr["h"]

    print("=" * 78)
    print("(1) DISTINCT ANIMATED PARTS ON SKIRMISH")
    print("=" * 78)
    print(f"{'ICN':<14}{'idx':>5}{'frames':>7}{'tiles':>7}{'parts':>7}  category")
    print("-" * 78)

    water_rows = []
    nonwater_rows = []
    for key in sorted(tile_count, key=lambda k: (k[0], k[1])):
        icn, index = key
        frames = anim[key]
        row = (icn, index, frames, tile_count[key], part_count[key], categorize(icn, index))
        if icn in WATER_ICNS:
            water_rows.append(row)
        else:
            nonwater_rows.append(row)

    def print_rows(rows):
        for icn, index, frames, tc, pc, cat in rows:
            print(f"{icn:<14}{index:>5}{frames:>7}{tc:>7}{pc:>7}  {cat}")

    print("[NON-WATER]")
    print_rows(nonwater_rows)
    print()
    print("[WATER (OBJNWATR/OBJNWAT2) - reported separately, palette-cycled]")
    print_rows(water_rows)
    print()

    # (2) frame totals + byte estimate. Animated part draws frames base+1..base+frames
    # (per viewport_pack note). We pack `frames` extra frames per distinct part.
    def estimate(rows, label):
        total_frames = 0
        bytes_half = 0      # task formula w*h/2
        bytes_full = 0      # engine-accurate w*h (PALETTED4444 = 1 byte/index px)
        missing_dims = 0
        # assumption fallback when AGG dims unavailable
        ASSUME_W = ASSUME_H = 32
        for icn, index, frames, tc, pc, cat in rows:
            total_frames += frames
            for f in range(1, frames + 1):
                dims = frame_dims(icn, index, f)
                if dims is None:
                    missing_dims += 1
                    w, h = ASSUME_W, ASSUME_H
                else:
                    w, h = dims
                bytes_half += (w * h) // 2
                bytes_full += w * h
        print(f"  {label}: distinct parts={len(rows)}, total extra frames={total_frames}")
        print(f"    est atlas bytes  (w*h/2, task formula)  = {bytes_half} ({bytes_half/1024:.1f} KiB)")
        print(f"    est atlas bytes  (w*h, PALETTED4444 1B/px)= {bytes_full} ({bytes_full/1024:.1f} KiB)")
        if missing_dims:
            print(f"    [! {missing_dims} frames used fallback {ASSUME_W}x{ASSUME_H}]")
        return total_frames, bytes_half, bytes_full

    print("=" * 78)
    print("(2) TOTAL EXTRA FRAMES + ESTIMATED ATLAS BYTES")
    print("=" * 78)
    nf, nh, nfu = estimate(nonwater_rows, "NON-WATER (would need packing)")
    print()
    wf, wh, wfu = estimate(water_rows, "WATER (already palette-cycled, EXCLUDED from cost)")
    print()
    print(f"  >>> NON-WATER pack cost: {nf} frames, "
          f"{nh} bytes (w*h/2) / {nfu} bytes (w*h)")
    print()

    # (3) campfire/windmill/flag/lava breakdown
    print("=" * 78)
    print("(3) CAMPFIRES / WINDMILLS / FLAGS / LAVA on map")
    print("=" * 78)
    lava = [r for r in nonwater_rows if r[0] in ("OBJNLAVA.ICN", "OBJNLAV2.ICN", "OBJNLAV3.ICN")]
    flags = [r for r in (nonwater_rows + water_rows) if r[0] == "FLAG32.ICN"]
    print(f"  LAVA parts on map: {len(lava)}")
    print_rows(lava)
    print(f"  FLAG32 parts on map: {len(flags)} (flags are dynamic-visual, packed per-frame elsewhere)")
    print_rows(flags)
    print("  CAMPFIRES/WINDMILLS: live in OBJNMUL2/OBJNMULT (generic adventure tilesets).")
    mul = [r for r in nonwater_rows if r[0] in ("OBJNMUL2.ICN", "OBJNMULT.ICN")]
    print(f"  OBJNMUL2/OBJNMULT animated parts on map: {len(mul)}")
    print_rows(mul)
    print()

    # (4) RAM_G headroom check
    RAM_G = 1024 * 1024
    OBJECT_ATLAS_END = 0x0E364D   # from check_ramg_usage.py output
    headroom = RAM_G - OBJECT_ATLAS_END
    print("=" * 78)
    print("(4) RAM_G HEADROOM FIT")
    print("=" * 78)
    print(f"  RAM_G size                = {RAM_G} (0x{RAM_G:06X})")
    print(f"  current object-atlas end  = 0x{OBJECT_ATLAS_END:06X} ({OBJECT_ATLAS_END})")
    print(f"  headroom                  = {headroom} bytes ({headroom/1024:.1f} KiB)")
    print(f"  non-water pack cost (w*h) = {nfu} bytes -> fits: {nfu <= headroom}")
    print(f"  non-water pack cost (w*h/2)= {nh} bytes -> fits: {nh <= headroom}")
    print("  NOTE: object frames are ARGB4 (2 B/px) in the live atlas (FT_ARGB4),")
    print("        so a real pack would be ~2x the w*h estimate; PALETTED4444 (1 B/px)")
    print("        would need a shared palette already resident.")
    argb = nfu * 2
    print(f"  non-water pack cost (ARGB4 2B/px, live-atlas fmt) = {argb} bytes "
          f"({argb/1024:.1f} KiB) -> fits: {argb <= headroom}")


if __name__ == "__main__":
    main()
