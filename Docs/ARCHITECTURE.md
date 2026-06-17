# Architecture

## Target

- Platform: TS-Config.
- Video output: VDAC2 / FT812.
- Display target: 640x480.
- Package format: SPG.
- CPU side: Z80 with banked memory.

## Porting Strategy

The project should not start by copying the whole game logic at once. HMM2 is better split into deterministic subsystems:

1. Core state model: player, heroes, resources, castles, map date.
2. Adventure map renderer and cursor.
3. Object interaction and pathfinding.
4. Town screen.
5. Combat screen.
6. AI turn.
7. Sound/music.

The first milestone should be a static adventure map with cursor movement and object selection. That proves the FT812 asset path, input, bank layout, and frame loop.

## FT812 Rendering Model

The FT812 should be treated as the primary compositor:

- Background tiles and large panels live in RAM_G.
- Display lists are rebuilt each frame.
- UI panels use bitmaps and simple primitives.
- Z80 updates compact state and emits draw commands.

Avoid software blitting on the Z80 except for data preparation, unpacking, or small control buffers.

## Data Packaging

SPG pages should be grouped by lifecycle:

- Boot/core code.
- Resident UI font and cursor assets.
- Adventure map tiles.
- Town screen assets.
- Combat screen assets.
- Audio banks.

Only resident assets should stay loaded across all modes.
