#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from hmm2_ft812_snapshot import (
    HMM2FullZ80Emulator,
    REG_HSIZE,
    REG_VSIZE,
    ROOT,
    attach_hmm2_shadow,
    disasm_dl,
    render_dl_png,
)


MAP_W = 36
MAP_H = 36
MAP_TILES = MAP_W * MAP_H
PATH_WORK_PAGE = 0x13
PATH_PARENT_OFF = 0
PATH_COST_LO_OFF = PATH_PARENT_OFF + MAP_TILES
PATH_COST_HI_OFF = PATH_COST_LO_OFF + MAP_TILES
PATH_QUEUE_X_OFF = PATH_COST_HI_OFF + MAP_TILES
PATH_QUEUE_Y_OFF = PATH_QUEUE_X_OFF + 0x1000
PATH_STATE_SEARCH = 1
PATH_FLAG_WATER = 0x01
PATH_FLAG_STOP = 0x02

DIRECTIONS = [
    ("TL", -1, -1, 0x01, 0x10),
    ("T", 0, -1, 0x02, 0x20),
    ("TR", 1, -1, 0x04, 0x40),
    ("R", 1, 0, 0x08, 0x80),
    ("BR", 1, 1, 0x10, 0x01),
    ("B", 0, 1, 0x20, 0x02),
    ("BL", -1, 1, 0x40, 0x04),
    ("L", -1, 0, 0x80, 0x08),
]


def parse_xy(text: str) -> tuple[int, int]:
    try:
        x_text, y_text = text.split(",", 1)
        x = int(x_text, 10)
        y = int(y_text, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("ожидается формат X,Y") from exc
    if not (0 <= x < MAP_W and 0 <= y < MAP_H):
        raise argparse.ArgumentTypeError(f"координаты вне карты {MAP_W}x{MAP_H}: {x},{y}")
    return x, y


def page_byte(emu: HMM2FullZ80Emulator, page: int, offset: int) -> int:
    return emu.mem.physical[page * 0x4000 + offset]


def work_byte(emu: HMM2FullZ80Emulator, offset: int) -> int:
    return page_byte(emu, PATH_WORK_PAGE, offset)


def tile_index(x: int, y: int) -> int:
    return y * MAP_W + x


def parent_at(emu: HMM2FullZ80Emulator, x: int, y: int) -> int:
    return work_byte(emu, PATH_PARENT_OFF + tile_index(x, y))


def cost_at(emu: HMM2FullZ80Emulator, x: int, y: int) -> int:
    index = tile_index(x, y)
    return work_byte(emu, PATH_COST_LO_OFF + index) | (work_byte(emu, PATH_COST_HI_OFF + index) << 8)


def debug_len(emu: HMM2FullZ80Emulator) -> int:
    return emu.get_word(emu.sym["PathDebugLen"])


def read_path_buffer(emu: HMM2FullZ80Emulator) -> list[tuple[int, int]]:
    count = emu.get_byte(emu.sym["HeroPathLen"])
    xs = emu.sym["HeroPathXBuf"]
    ys = emu.sym["HeroPathYBuf"]
    return [(emu.get_byte(xs + i), emu.get_byte(ys + i)) for i in range(count)]


def read_debug_buffer(emu: HMM2FullZ80Emulator) -> list[tuple[int, int]]:
    count = debug_len(emu)
    xs = emu.sym["PathDebugXBuf"] - 0xC000
    ys = emu.sym["PathDebugYBuf"] - 0xC000
    return [(page_byte(emu, PATH_WORK_PAGE, xs + i), page_byte(emu, PATH_WORK_PAGE, ys + i)) for i in range(count)]


def init_emu():
    emu = HMM2FullZ80Emulator(ROOT)
    regs = attach_hmm2_shadow(emu)
    emu.input.mouse_x = 0
    emu.input.mouse_y = 0
    emu.input.mouse_buttons = 0x01
    emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=12_000_000)
    return emu, regs


def set_hero(emu: HMM2FullZ80Emulator, x: int, y: int) -> None:
    emu.set_byte(emu.sym["HeroTileX"], x)
    emu.set_byte(emu.sym["HeroTileY"], y)
    emu.set_byte(emu.sym["HeroStepX"], x)
    emu.set_byte(emu.sym["HeroStepY"], y)
    emu.set_byte(emu.sym["HeroTargetX"], x)
    emu.set_byte(emu.sym["HeroTargetY"], y)
    emu.set_word(emu.sym["HeroPixelX"], x * 32)
    emu.set_word(emu.sym["HeroPixelY"], y * 32)
    emu.set_byte(emu.sym["HeroPathLen"], 0)
    emu.set_byte(emu.sym["HeroPathIndex"], 0)
    emu.set_byte(emu.sym["PathState"], 0)
    emu.set_byte(emu.sym["PathDebugLen"], 0)
    emu.set_byte(emu.sym["PathDebugLen"] + 1, 0)


def set_viewport_origin(emu: HMM2FullZ80Emulator, x: int, y: int) -> None:
    emu.set_byte(emu.sym["ViewportOriginX"], x)
    emu.set_byte(emu.sym["ViewportOriginY"], y)
    emu.set_word(emu.sym["ViewportPixelX"], x * 32)
    emu.set_word(emu.sym["ViewportPixelY"], y * 32)


def load_map_data() -> tuple[bytes, bytes, bytes]:
    passability = (ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.pass.bin").read_bytes()
    path_meta = (ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.path.bin").read_bytes()
    costs = path_meta[:MAP_TILES]
    flags = path_meta[MAP_TILES:MAP_TILES * 2]
    if len(passability) != MAP_TILES or len(costs) != MAP_TILES or len(flags) != MAP_TILES:
        raise RuntimeError("неверный размер passability/path metadata")
    return passability, costs, flags


def transition_reason(passability: bytes, flags: bytes, x: int, y: int, direction) -> str:
    name, dx, dy, out_mask, in_mask = direction
    nx = x + dx
    ny = y + dy
    if not (0 <= nx < MAP_W and 0 <= ny < MAP_H):
        return f"{name}: вне карты"
    src = passability[tile_index(x, y)]
    dst = passability[tile_index(nx, ny)]
    dst_flags = flags[tile_index(nx, ny)]
    if (src & out_mask) == 0:
        return f"{name}->{nx},{ny}: BLOCK exit src={src:02X} need={out_mask:02X}"
    if (dst & in_mask) == 0:
        return f"{name}->{nx},{ny}: BLOCK entry dst={dst:02X} need={in_mask:02X}"
    if dst_flags & PATH_FLAG_WATER:
        return f"{name}->{nx},{ny}: BLOCK water flags={dst_flags:02X}"
    return f"{name}->{nx},{ny}: ok src={src:02X} dst={dst:02X} flags={dst_flags:02X}"


def dump_area(passability: bytes, flags: bytes, center: tuple[int, int], radius: int) -> None:
    cx, cy = center
    x0 = max(0, cx - radius)
    x1 = min(MAP_W - 1, cx + radius)
    y0 = max(0, cy - radius)
    y1 = min(MAP_H - 1, cy + radius)
    print(f"area pass/flags around {cx},{cy}:")
    for y in range(y0, y1 + 1):
        row = []
        for x in range(x0, x1 + 1):
            i = tile_index(x, y)
            row.append(f"{passability[i]:02X}/{flags[i]:02X}")
        print(f"  y={y:02d}: " + " ".join(row))


def update_frame(emu: HMM2FullZ80Emulator, max_steps: int = 600_000) -> int:
    steps = emu.call(emu.sym["Input_Poll"], max_steps=300_000)
    steps += emu.call(emu.sym["Game_Update"], max_steps=max_steps)
    return steps


def run_z80_path_direct(emu: HMM2FullZ80Emulator, target: tuple[int, int], max_frames: int) -> list[str]:
    tx, ty = target
    emu.reg.B = tx
    emu.reg.C = ty
    steps = emu.call(emu.sym["Hero_SetTargetIfPassable"], max_steps=4_000_000)
    trace = [
        "after build: "
        f"steps={steps} state={emu.get_byte(emu.sym['PathState'])} "
        f"target={emu.get_byte(emu.sym['PathTargetX'])},{emu.get_byte(emu.sym['PathTargetY'])} "
        f"debug={debug_len(emu)}"
    ]
    for frame in range(max_frames):
        state = emu.get_byte(emu.sym["PathState"])
        if state != PATH_STATE_SEARCH:
            break
        steps = emu.call(emu.sym["Hero_PathSearchUpdate"], max_steps=4_000_000)
        if frame < 32 or frame % 16 == 15:
            trace.append(
                f"frame={frame + 1:03d} steps={steps:06d} "
                f"state={emu.get_byte(emu.sym['PathState'])} "
                f"queue={emu.get_word(emu.sym['PathQueueHead'])}/{emu.get_word(emu.sym['PathQueueTail'])} "
                f"cur={emu.get_byte(emu.sym['PathCurrentX'])},{emu.get_byte(emu.sym['PathCurrentY'])} "
                f"debug={debug_len(emu)} "
                f"path_len={emu.get_byte(emu.sym['HeroPathLen'])}"
            )
    return trace


def run_z80_path_via_game(
    emu: HMM2FullZ80Emulator,
    target: tuple[int, int],
    viewport_origin: tuple[int, int],
    max_frames: int,
) -> list[str]:
    tx, ty = target
    vx, vy = viewport_origin
    set_viewport_origin(emu, vx, vy)
    cursor_px = tx * 32 - vx * 32
    cursor_py = ty * 32 - vy * 32
    if not (0 <= cursor_px <= 624 and 0 <= cursor_py <= 464):
        raise SystemExit(
            f"ОШИБКА: цель {tx},{ty} вне логического viewport origin={vx},{vy}: "
            f"cursor_px={cursor_px}, cursor_py={cursor_py}"
        )
    emu.set_byte(emu.sym["CursorTileX"], tx)
    emu.set_byte(emu.sym["CursorTileY"], ty)
    emu.set_word(emu.sym["CursorPixelX"], cursor_px)
    emu.set_word(emu.sym["CursorPixelY"], cursor_py)
    emu.input.mouse_buttons = 0x01
    emu.input.kempston = 0x10
    steps = update_frame(emu)
    emu.input.kempston = 0
    trace = [
        "after fire Game_Update: "
        f"steps={steps} state={emu.get_byte(emu.sym['PathState'])} "
        f"viewport={emu.get_byte(emu.sym['ViewportOriginX'])},{emu.get_byte(emu.sym['ViewportOriginY'])} "
        f"viewport_px={emu.get_word(emu.sym['ViewportPixelX'])},{emu.get_word(emu.sym['ViewportPixelY'])} "
        f"cursor={emu.get_byte(emu.sym['CursorTileX'])},{emu.get_byte(emu.sym['CursorTileY'])} "
        f"PathTarget={emu.get_byte(emu.sym['PathTargetX'])},{emu.get_byte(emu.sym['PathTargetY'])} "
        f"HeroTarget={emu.get_byte(emu.sym['HeroTargetX'])},{emu.get_byte(emu.sym['HeroTargetY'])} "
        f"hero={emu.get_byte(emu.sym['HeroTileX'])},{emu.get_byte(emu.sym['HeroTileY'])} "
        f"step={emu.get_byte(emu.sym['HeroStepX'])},{emu.get_byte(emu.sym['HeroStepY'])}"
    ]
    for frame in range(max_frames):
        state = emu.get_byte(emu.sym["PathState"])
        hero = (emu.get_byte(emu.sym["HeroTileX"]), emu.get_byte(emu.sym["HeroTileY"]))
        step = (emu.get_byte(emu.sym["HeroStepX"]), emu.get_byte(emu.sym["HeroStepY"]))
        if state == 0 and hero == target and step == target:
            break
        steps = update_frame(emu)
        if frame < 48 or frame % 16 == 15:
            trace.append(
                f"game_frame={frame + 1:03d} steps={steps:06d} "
                f"state={emu.get_byte(emu.sym['PathState'])} "
                f"queue={emu.get_word(emu.sym['PathQueueHead'])}/{emu.get_word(emu.sym['PathQueueTail'])} "
                f"debug={debug_len(emu)} "
                f"path_len={emu.get_byte(emu.sym['HeroPathLen'])} "
                f"path_idx={emu.get_byte(emu.sym['HeroPathIndex'])} "
                f"hero={emu.get_byte(emu.sym['HeroTileX'])},{emu.get_byte(emu.sym['HeroTileY'])} "
                f"pixel={emu.get_word(emu.sym['HeroPixelX'])},{emu.get_word(emu.sym['HeroPixelY'])} "
                f"step={emu.get_byte(emu.sym['HeroStepX'])},{emu.get_byte(emu.sym['HeroStepY'])} "
                f"target={emu.get_byte(emu.sym['HeroTargetX'])},{emu.get_byte(emu.sym['HeroTargetY'])}"
            )
    return trace


def python_reachable(passability: bytes, flags: bytes, start: tuple[int, int]) -> set[tuple[int, int]]:
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        if (x, y) != start and (flags[tile_index(x, y)] & PATH_FLAG_STOP):
            continue
        for direction in DIRECTIONS:
            _name, dx, dy, out_mask, in_mask = direction
            nx = x + dx
            ny = y + dy
            if not (0 <= nx < MAP_W and 0 <= ny < MAP_H):
                continue
            ni = tile_index(nx, ny)
            if flags[ni] & PATH_FLAG_WATER:
                continue
            if (passability[tile_index(x, y)] & out_mask) == 0:
                continue
            if (passability[ni] & in_mask) == 0:
                continue
            node = (nx, ny)
            if node not in seen:
                seen.add(node)
                queue.append(node)
    return seen


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Прогнать построение маршрута настоящим Z80-кодом через Python-эмулятор."
    )
    parser.add_argument("--hero", type=parse_xy, default=(13, 9), help="старт героя X,Y")
    parser.add_argument("--target", type=parse_xy, default=(23, 7), help="цель маршрута X,Y")
    parser.add_argument("--max-frames", type=int, default=512)
    parser.add_argument("--radius", type=int, default=3)
    parser.add_argument("--viewport-origin", type=parse_xy, default=(0, 0), help="origin viewport X,Y для --via-game")
    parser.add_argument("--via-game", action="store_true", help="запускать через Input_Poll/Game_Update + fire")
    parser.add_argument("--out-png", type=Path, default=None, help="после трассировки отрендерить текущий FT812 кадр в PNG")
    args = parser.parse_args()

    passability, costs, flags = load_map_data()
    hero = args.hero
    target = args.target
    hi = tile_index(*hero)
    ti = tile_index(*target)

    print(f"Z80 path trace: hero={hero[0]},{hero[1]} target={target[0]},{target[1]}")
    print(f"hero pass={passability[hi]:02X} flags={flags[hi]:02X} cost={costs[hi]}")
    print(f"target pass={passability[ti]:02X} flags={flags[ti]:02X} cost={costs[ti]}")
    dump_area(passability, flags, hero, args.radius)
    print("transitions from hero:")
    for direction in DIRECTIONS:
        print("  " + transition_reason(passability, flags, hero[0], hero[1], direction))
    print("python reference reachability:", "target reachable" if target in python_reachable(passability, flags, hero) else "target NOT reachable")

    emu, regs = init_emu()
    set_hero(emu, *hero)
    if args.via_game:
        trace = run_z80_path_via_game(emu, target, args.viewport_origin, args.max_frames)
    else:
        trace = run_z80_path_direct(emu, target, args.max_frames)
    for line in trace:
        print(line)

    target_parent = parent_at(emu, *target)
    print(
        "final: "
        f"state={emu.get_byte(emu.sym['PathState'])} "
        f"PathFound={emu.get_byte(emu.sym['PathFound'])} "
        f"HeroTarget={emu.get_byte(emu.sym['HeroTargetX'])},{emu.get_byte(emu.sym['HeroTargetY'])} "
        f"PathTarget={emu.get_byte(emu.sym['PathTargetX'])},{emu.get_byte(emu.sym['PathTargetY'])} "
        f"HeroPathLen={emu.get_byte(emu.sym['HeroPathLen'])} "
        f"HeroPathIndex={emu.get_byte(emu.sym['HeroPathIndex'])} "
        f"target_parent={target_parent:02X} target_cost={cost_at(emu, *target)}"
    )

    debug = read_debug_buffer(emu)
    path_raw = read_path_buffer(emu)
    print(f"debug_len={len(debug)} debug_first={debug[:16]} debug_last={debug[-16:] if debug else []}")
    print(f"path_raw_target_to_start={path_raw}")
    print(f"path_move_order={list(reversed(path_raw))}")
    if args.out_png is not None:
        emu.call(emu.sym["Render_Frame"], max_steps=30_000_000)
        snap = bytes(emu.ft.ram_dl[:0x2000])
        ops = disasm_dl(snap, max_ops=4096)
        render_dl_png(
            ops,
            bytes(emu.ft.ram_g),
            args.out_png,
            regs._get32(REG_HSIZE) or 640,
            regs._get32(REG_VSIZE) or 480,
        )
        print(f"png={args.out_png}")


if __name__ == "__main__":
    main()
