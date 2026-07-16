# Map Pipeline

The first gameplay milestone is a static adventure-map viewport.

## Current Source Map

The initial test map is:

```text
Assets/Original/MAPS/SKIRMISH.MX2
```

It is one of the smallest available maps, which makes it a good conversion and
render smoke test.

## Conversion

Run:

```bat
python Source\Tools\map_tools.py Assets\Original\MAPS\SKIRMISH.MX2
```

Outputs:

- `Assets/Converted/Maps/SKIRMISH.map.bin`
- `Assets/Converted/Maps/SKIRMISH.manifest.json`
- `Source/ASM/generated_map.inc`

## Binary Format

Header:

| Offset | Size | Meaning |
| --- | ---: | --- |
| 0 | 4 | ASCII `H2MP` |
| 4 | 1 | format version, currently `1` |
| 5 | 1 | map width in tiles |
| 6 | 1 | map height in tiles |
| 7 | 1 | difficulty |
| 8 | 2 | tile count |

Tile record, 8 bytes each:

| Offset | Size | Meaning |
| --- | ---: | --- |
| 0 | 2 | terrain image index |
| 2 | 1 | bottom object ICN type |
| 3 | 1 | bottom object image index |
| 4 | 1 | top object ICN type |
| 5 | 1 | top object image index |
| 6 | 1 | terrain flags |
| 7 | 1 | main map object type |

This is intentionally smaller than the full MP2 tile structure. It is enough for
the first renderer milestone and can be replaced by a fuller format later.
