# Audio Pipeline

## Runtime Target

ZX Evolution has a MIDI-capable SAM synthesizer, so the port should not play `OGG`
files directly.

Runtime music path:

1. Extract original `MIDIxxxx.XMI` resources from `HEROES2.AGG` and `HEROES2X.AGG`.
2. Convert XMI to a SAM-compatible MIDI/event stream.
3. Pack converted streams into a music bank.
4. Drive the SAM synthesizer from the Z80 game audio dispatcher.

`Assets/Original/MUSIC/*.ogg` remains useful as a reference for track order and
expected playback, but it is not a TS-Config runtime asset.

## Current Extraction

`Source/Tools/agg_tools.py` extracts XMI files and writes AGG manifests:

```bat
python Source\Tools\agg_tools.py Assets\Original\DATA\HEROES2.AGG Assets\Original\DATA\HEROES2X.AGG --extract-xmi
```

Current output:

- `Assets/Converted/Music/XMI/HEROES2`: 17 XMI files.
- `Assets/Converted/Music/XMI/HEROES2X`: 6 XMI files.
- `Assets/Converted/Manifest/HEROES2.csv`
- `Assets/Converted/Manifest/HEROES2X.csv`

## fheroes2 Mapping

The reference mapping is in:

- `OpenHMM2/src/fheroes2/agg/mus.h`
- `OpenHMM2/src/fheroes2/agg/xmi.cpp`

The important gameplay mappings:

| Game music | XMI |
| --- | --- |
| Battle 1 | `MIDI0002.XMI` |
| Battle 2 | `MIDI0003.XMI` |
| Battle 3 | `MIDI0004.XMI` |
| Castle themes | `MIDI0005.XMI` ... `MIDI0010.XMI` |
| Lava | `MIDI0011.XMI` |
| Desert | `MIDI0013.XMI` |
| Snow | `MIDI0014.XMI` |
| Swamp | `MIDI0015.XMI` |
| Dirt | `MIDI0017.XMI` |
| Grass | `MIDI0018.XMI` |
| Main menu | `MIDI0042.XMI` |
| Victory | `MIDI0043.XMI` |

## Next Work

- Add or reuse an XMI-to-MIDI converter.
- Define the SAM MIDI I/O protocol for ZX Evolution.
- Build a small single-track playback test before integrating with game modes.
