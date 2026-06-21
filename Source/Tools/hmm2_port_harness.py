#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from hmm2_ft812_snapshot import (  # noqa: E402
    HMM2FullZ80Emulator,
    HMM2_VIDEO_TIMING,
    render_dl_png,
)
from shadow_ft812 import (  # noqa: E402
    RAM_DL_SIZE,
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

try:
    from phys_ft812_sim import PhysFT812Machine  # noqa: E402
except Exception:  # pragma: no cover - reported if phys backend is requested.
    PhysFT812Machine = None  # type: ignore

try:
    from unreal_vdac2 import HMM2UnrealVDAC2Machine  # noqa: E402
except Exception:  # pragma: no cover - reported if unreal backend is requested.
    HMM2UnrealVDAC2Machine = None  # type: ignore


PATH_STATE_SEARCH = 0x01
MOUSE_LMB = 0x01


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def passability() -> tuple[bytes, int]:
    data = (ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.pass.bin").read_bytes()
    width = int(len(data) ** 0.5)
    if width * width != len(data):
        fail(f"passability map is not square: {len(data)} bytes")
    return data, width


def find_passable_target(emu: HMM2FullZ80Emulator) -> tuple[int, int]:
    data, width = passability()
    start_x = emu.get_byte(emu.sym["HeroTileX"])
    start_y = emu.get_byte(emu.sym["HeroTileY"])
    candidates = [
        (start_x, start_y + 1),
        (start_x - 1, start_y),
        (start_x + 1, start_y),
        (start_x, start_y - 1),
        (start_x - 1, start_y + 1),
        (start_x + 1, start_y + 1),
        (start_x, start_y + 2),
    ]
    for x, y in candidates:
        if 0 <= x < width and 0 <= y < width and data[y * width + x] != 0:
            return x, y
    fail(f"no passable target near {start_x},{start_y}")


def build_path_to(emu: HMM2FullZ80Emulator, x: int, y: int, max_frames: int = 1024) -> None:
    emu.reg.B = x
    emu.reg.C = y
    emu.call(emu.sym["Hero_SetTargetIfPassable"], max_steps=4_000_000)
    for _ in range(max_frames):
        if emu.get_byte(emu.sym["PathState"]) != PATH_STATE_SEARCH:
            break
        emu.call(emu.sym["Hero_PathSearchUpdate"], max_steps=600_000)
    if emu.get_byte(emu.sym["PathState"]) == PATH_STATE_SEARCH:
        fail(f"path search did not finish for {x},{y}")
    emu.call(emu.sym["UI_ButtonsStateUpdate"], max_steps=100_000)


def make_machine(backend: str) -> tuple[Any, Any]:
    if backend == "fast":
        emu = HMM2FullZ80Emulator(ROOT)
        regs = attach_shadow(emu, HMM2_VIDEO_TIMING)
        return emu, regs
    if backend == "phys":
        if PhysFT812Machine is None:
            fail("phys_ft812_sim backend is unavailable")
        return PhysFT812Machine(ROOT), None
    if backend == "unreal":
        if HMM2UnrealVDAC2Machine is None:
            fail("unreal_vdac2 backend is unavailable")
        return HMM2UnrealVDAC2Machine(ROOT), None
    fail(f"unknown backend: {backend}")


def boot_start_to_mainloop(emu: Any, max_steps: int = 120_000_000) -> None:
    if "Start" not in emu.sym or "MainLoop" not in emu.sym:
        fail("Start/MainLoop symbols are unavailable")
    emu.reg.PC = emu.sym["Start"]
    emu.run_until_pc(
        emu.sym["MainLoop"],
        max_steps=max_steps,
        service_frame_interrupts=True,
    )


def boot_adventure(emu: Any, boot_mode: str = "bypass") -> None:
    emu.input.mouse_x = 0
    emu.input.mouse_y = 0
    emu.input.mouse_buttons = 0
    emu.input.kempston = 0
    if boot_mode == "start":
        boot_start_to_mainloop(emu)
        emu.call(emu.sym["Adventure_Enter"], max_steps=12_000_000, service_frame_interrupts=True)
        emu.reg.PC = emu.sym["MainLoop"]
        return
    if getattr(emu, "vdac2", None) is not None and "Init_Video" in emu.sym:
        emu.fmaddr_enabled = True
        core_page = emu.sym.get("CorePage", 0x05)
        if hasattr(emu, "_write_tsconf_register"):
            emu._write_tsconf_register(0x11, core_page & 0xFF)
            emu._write_tsconf_register(0x12, (core_page + 1) & 0xFF)
        else:
            emu.mem.pages[1] = core_page & 0xFF
            emu.mem.pages[2] = (core_page + 1) & 0xFF
        emu.call(emu.sym["Init_Video"], max_steps=12_000_000)
        if "ResolutionWidthPtr" in emu.sym:
            emu.set_word(emu.sym["ResolutionWidthPtr"], 640)
        if "ResolutionHeightPtr" in emu.sym:
            emu.set_word(emu.sym["ResolutionHeightPtr"], 480)
    else:
        emu.call(emu.sym["Platform_Init"], max_steps=12_000_000)
    emu.call(emu.sym["Input.Mouse.Initialize"], max_steps=200_000)
    emu.call(emu.sym["Input_Init"], max_steps=200_000)
    emu.call(emu.sym["Game_Init"], max_steps=600_000_000)
    emu.call(emu.sym["Adventure_Enter"], max_steps=600_000_000)


def game_update(emu: Any) -> None:
    emu.call(emu.sym["Input_Poll"], max_steps=300_000)
    emu.call(emu.sym["Game_Update"], max_steps=800_000)


def render_frame(emu: Any, regs: Any) -> None:
    if regs is not None:
        regs.tick_frame(emu.ft.ram_dl)
    vdac2 = getattr(emu, "vdac2", None)
    frame_count = vdac2.frame_count if vdac2 is not None else 0
    emu.call(emu.sym["Render_Frame"], max_steps=30_000_000)
    if vdac2 is not None:
        vdac2.wait_frame(frame_count, timeout_s=2.0)


def scenario_idle(emu: Any, regs: Any, args: argparse.Namespace) -> None:
    del args
    render_frame(emu, regs)


def scenario_scroll_cursor(emu: Any, regs: Any, args: argparse.Namespace) -> None:
    positions = {
        "top": (320, 0),
        "top-right": (624, 0),
        "right": (624, 224),
        "bottom-right": (624, 464),
        "bottom": (320, 464),
        "bottom-left": (0, 464),
        "left": (0, 224),
        "top-left": (0, 0),
    }
    x, y = positions[args.edge]
    emu.set_word(emu.sym["CursorPixelX"], x)
    emu.set_word(emu.sym["CursorPixelY"], y)
    emu.call(emu.sym["Cursor_UpdateTheme"], max_steps=100_000)
    render_frame(emu, regs)


def scenario_hero_move_button(emu: Any, regs: Any, args: argparse.Namespace) -> None:
    if args.button_state in ("route", "inactive"):
        target_x, target_y = find_passable_target(emu)
        build_path_to(emu, target_x, target_y)
    if args.button_state == "inactive":
        emu.set_byte(emu.sym["HeroMovePoints"], 0)
        emu.call(emu.sym["UI_ButtonsStateUpdate"], max_steps=100_000)

    if args.press:
        button_x = emu.sym["UI_BUTTON_X"] + emu.sym["UI_BUTTON_W"] + emu.sym["UI_BUTTON_W"] // 2
        button_y = emu.sym["UI_BUTTON_Y"] + emu.sym["UI_BUTTON_H"] // 2
        emu.set_word(emu.sym["Input.Mouse.PositionX"], button_x)
        emu.set_word(emu.sym["Input.Mouse.PositionY"], button_y)
        emu.input.mouse_buttons = MOUSE_LMB
        emu.call(emu.sym["UI_ButtonsPressedUpdate"], max_steps=100_000)
    render_frame(emu, regs)


def scenario_hero_walk_first_frame(emu: Any, regs: Any, args: argparse.Namespace) -> None:
    target_x, target_y = find_passable_target(emu)
    build_path_to(emu, target_x, target_y)
    emu.call(emu.sym["Hero_StartMovement"], max_steps=200_000)
    if emu.get_byte(emu.sym["HeroMoveActive"]) == 0:
        fail(
            "Hero_StartMovement did not activate prepared path: "
            f"target={target_x},{target_y} "
            f"PathFound={emu.get_byte(emu.sym['PathFound'])} "
            f"HeroPathLen={emu.get_byte(emu.sym['HeroPathLen'])} "
            f"HeroMovePoints={emu.get_byte(emu.sym['HeroMovePoints'])}"
        )
    for _ in range(args.walk_updates):
        game_update(emu)
    render_frame(emu, regs)


def scenario_hiscores_standard(emu: Any, regs: Any, args: argparse.Namespace) -> None:
    del args
    emu.input.mouse_buttons = 0
    emu.call(emu.sym["HiScores_EnterStandard"], max_steps=40_000_000, service_frame_interrupts=True)
    render_frame(emu, regs)


SCENARIOS = {
    "idle": scenario_idle,
    "scroll-cursor": scenario_scroll_cursor,
    "hero-move-button": scenario_hero_move_button,
    "hero-walk-first-frame": scenario_hero_walk_first_frame,
    "hiscores-standard": scenario_hiscores_standard,
}


def read_sym_byte(emu: Any, name: str) -> int | None:
    if name not in emu.sym:
        return None
    return emu.get_byte(emu.sym[name])


def read_sym_word(emu: Any, name: str) -> int | None:
    if name not in emu.sym:
        return None
    return emu.get_word(emu.sym[name])


def register_dump(regs: Any, emu: Any) -> dict[str, int]:
    if regs is not None:
        return {
            "hcycle": regs._get32(REG_HCYCLE),
            "hoffset": regs._get32(REG_HOFFSET),
            "hsize": regs._get32(REG_HSIZE),
            "vcycle": regs._get32(REG_VCYCLE),
            "voffset": regs._get32(REG_VOFFSET),
            "vsize": regs._get32(REG_VSIZE),
            "pclk": regs._get32(REG_PCLK),
            "frames": regs._get32(REG_FRAMES),
            "clock": regs._get32(REG_CLOCK),
            "dlswap": regs._get32(REG_DLSWAP),
            "int_flags": regs._get32(REG_INT_FLAGS),
        }
    vdac2 = getattr(emu, "vdac2", None)
    if vdac2 is not None:
        return {
            "hcycle": vdac2.read_reg16(REG_HCYCLE),
            "hoffset": vdac2.read_reg16(REG_HOFFSET),
            "hsize": vdac2.read_reg16(REG_HSIZE),
            "vcycle": vdac2.read_reg16(REG_VCYCLE),
            "voffset": vdac2.read_reg16(REG_VOFFSET),
            "vsize": vdac2.read_reg16(REG_VSIZE),
            "pclk": vdac2.read_reg8(REG_PCLK),
            "frames": vdac2.read_reg32(REG_FRAMES),
            "clock": vdac2.read_reg32(REG_CLOCK),
            "dlswap": vdac2.read_reg8(REG_DLSWAP),
            "int_flags": vdac2.read_reg8(REG_INT_FLAGS),
        }
    if hasattr(emu, "display_timing"):
        t = emu.display_timing()
        return {
            "hcycle": t.hcycle,
            "hoffset": t.hoffset,
            "hsize": t.hsize,
            "vcycle": t.vcycle,
            "voffset": t.voffset,
            "vsize": t.vsize,
            "pclk_hz": int(t.pclk_hz),
            "fps_milli": int(t.fps * 1000),
            "clock_us": int(getattr(emu, "clock", 0.0) * 1_000_000),
        }
    return {}


def dump_state(
    emu: Any,
    regs: Any,
    backend: str,
    scenario: str,
    out_dir: Path,
    dump_dl_text: bool,
    boot_mode: str,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ram_dl = bytes(emu.ft.ram_dl[:RAM_DL_SIZE])
    ops = disasm_dl(ram_dl, max_ops=4096)
    counts = Counter(op.name for op in ops)
    sources = [str(op.fields.get("addr")).upper() for op in ops if op.name == "BITMAP_SOURCE"]
    regs_dump = register_dump(regs, emu)
    ft_writes = emu.ft_write_summary() if hasattr(emu, "ft_write_summary") else None

    png_path = out_dir / f"{scenario}_{backend}.png"
    width = regs_dump.get("hsize", 640) or 640
    height = regs_dump.get("vsize", 480) or 480
    render_dl_png(ops, bytes(emu.ft.ram_g), png_path, width, height)
    vdac2_frame_path = None
    vdac2 = getattr(emu, "vdac2", None)
    vdac2_state = None
    ft_bus_trace_path = None
    ft_bus_trace = emu.ft_bus_trace_summary() if hasattr(emu, "ft_bus_trace_summary") else None
    if ft_bus_trace is not None and ft_bus_trace.get("enabled"):
        ft_bus_trace_path = out_dir / f"{scenario}_{backend}.ft_bus.jsonl"
        emu.dump_ft_bus_trace(ft_bus_trace_path)
    if vdac2 is not None and vdac2.last_frame is not None:
        from PIL import Image

        frame = vdac2.last_frame
        raw = frame.argb8888
        rgba = bytearray(len(raw))
        for i in range(0, len(raw), 4):
            b, g, r, a = raw[i], raw[i + 1], raw[i + 2], raw[i + 3]
            rgba[i:i + 4] = bytes((r, g, b, a))
        vdac2_frame_path = out_dir / f"{scenario}_{backend}.vdac2.png"
        Image.frombytes("RGBA", (frame.width, frame.height), bytes(rgba)).save(vdac2_frame_path)
    if vdac2 is not None:
        vdac2_state = {
            "dll": str(vdac2.dll_path),
            "version": vdac2.version,
            "frame_count": vdac2.frame_count,
            "has_frame": vdac2.last_frame is not None,
            "graphics": vdac2.graphics_stats,
            "logs": list(vdac2.log_messages),
        }

    dl_path = out_dir / f"{scenario}_{backend}.ram_dl.bin"
    dl_path.write_bytes(ram_dl)

    if dump_dl_text:
        (out_dir / f"{scenario}_{backend}.ram_dl.txt").write_text(format_dl(ops), encoding="utf-8")

    json_path = out_dir / f"{scenario}_{backend}.state.json"
    state = {
        "backend": backend,
        "boot_mode": boot_mode,
        "scenario": scenario,
        "outputs": {
            "png": str(png_path),
            "vdac2_png": str(vdac2_frame_path) if vdac2_frame_path is not None else None,
            "ram_dl": str(dl_path),
            "ft_bus_trace": str(ft_bus_trace_path) if ft_bus_trace_path is not None else None,
            "state_json": str(json_path),
        },
        "hashes": {
            "ram_dl_sha256": sha256(ram_dl),
            "ram_g_sha256": sha256(bytes(emu.ft.ram_g)),
        },
        "registers": regs_dump,
        "z80": {
            "tstates": getattr(emu, "tstates", None),
            "frame_interrupts": getattr(emu, "frame_interrupts", None),
            "tsconf_intmask": getattr(emu, "tsconf_intmask", None),
            "fmaddr_enabled": getattr(emu, "fmaddr_enabled", None),
            "pages": list(getattr(getattr(emu, "mem", None), "pages", [])),
            "errors": list(getattr(emu, "errors", [])),
        },
        "vdac2": vdac2_state,
        "ft_writes": ft_writes,
        "ft_bus_trace": ft_bus_trace,
        "game_state": {
            "HeroTileX": read_sym_byte(emu, "HeroTileX"),
            "HeroTileY": read_sym_byte(emu, "HeroTileY"),
            "HeroPixelX": read_sym_word(emu, "HeroPixelX"),
            "HeroPixelY": read_sym_word(emu, "HeroPixelY"),
            "HeroTargetX": read_sym_byte(emu, "HeroTargetX"),
            "HeroTargetY": read_sym_byte(emu, "HeroTargetY"),
            "HeroStepX": read_sym_byte(emu, "HeroStepX"),
            "HeroStepY": read_sym_byte(emu, "HeroStepY"),
            "HeroFacingRight": read_sym_byte(emu, "HeroFacingRight"),
            "HeroMoveCooldown": read_sym_byte(emu, "HeroMoveCooldown"),
            "HeroMoveFrameGate": read_sym_byte(emu, "HeroMoveFrameGate"),
            "HeroMovePoints": read_sym_byte(emu, "HeroMovePoints"),
            "HeroMoveActive": read_sym_byte(emu, "HeroMoveActive"),
            "HeroPathLen": read_sym_byte(emu, "HeroPathLen"),
            "HeroPathIndex": read_sym_byte(emu, "HeroPathIndex"),
            "PathFound": read_sym_byte(emu, "PathFound"),
            "PathState": read_sym_byte(emu, "PathState"),
            "GameMode": read_sym_byte(emu, "GameMode"),
            "HsAbiStatus": read_sym_byte(emu, "HsAbiStatus"),
            "HsAbiCmd": read_sym_byte(emu, "HsAbiCmd"),
            "UI_ButtonPressed": read_sym_byte(emu, "UI_ButtonPressed"),
            "UI_HeroMoveButtonState": read_sym_byte(emu, "UI_HeroMoveButtonState"),
            "CursorSpriteIndex": read_sym_byte(emu, "CursorSpriteIndex"),
            "CursorScrollDir": read_sym_byte(emu, "CursorScrollDir"),
            "CursorPixelX": read_sym_word(emu, "CursorPixelX"),
            "CursorPixelY": read_sym_word(emu, "CursorPixelY"),
            "ViewportPixelX": read_sym_word(emu, "ViewportPixelX"),
            "ViewportPixelY": read_sym_word(emu, "ViewportPixelY"),
            "ViewportOriginX": read_sym_byte(emu, "ViewportOriginX"),
            "ViewportOriginY": read_sym_byte(emu, "ViewportOriginY"),
        },
        "display_list": {
            "op_count": len(ops),
            "counts": dict(sorted(counts.items())),
            "bitmap_sources": sources,
        },
    }
    json_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HMM2 port harness: one scenario, one state/DL/PNG contract dump.")
    parser.add_argument("--backend", choices=("fast", "phys", "unreal"), default="fast")
    parser.add_argument("--scenario", choices=tuple(SCENARIOS), default="idle")
    parser.add_argument(
        "--boot-mode",
        choices=("bypass", "start"),
        default="bypass",
        help="bypass calls init routines directly; start executes Start -> MainLoop with frame IRQ service.",
    )
    parser.add_argument("--out-dir", type=Path, default=ROOT / "Diagnostics" / "port_harness")
    parser.add_argument("--dump-dl", action="store_true")
    parser.add_argument(
        "--edge",
        choices=("top", "top-right", "right", "bottom-right", "bottom", "bottom-left", "left", "top-left"),
        default="right",
        help="Scroll cursor edge for scenario=scroll-cursor.",
    )
    parser.add_argument(
        "--button-state",
        choices=("disabled", "route", "inactive"),
        default="disabled",
        help="Hero Movement state for scenario=hero-move-button.",
    )
    parser.add_argument("--press", action="store_true", help="Hold LMB on Hero Movement button.")
    parser.add_argument(
        "--walk-updates",
        type=int,
        default=1,
        help="Game_Update calls after Hero_StartMovement for scenario=hero-walk-first-frame.",
    )
    parser.add_argument(
        "--trace-ft-bus",
        action="store_true",
        help="Dump raw Z-Controller/FT812 byte-level trace for the scenario window.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    emu, regs = make_machine(args.backend)
    try:
        boot_adventure(emu, args.boot_mode)
        game_update(emu)
        if hasattr(emu, "clear_ft_write_trace"):
            emu.clear_ft_write_trace()
        if args.trace_ft_bus:
            if not hasattr(emu, "enable_ft_bus_trace"):
                fail("--trace-ft-bus is supported only by backends with FT bus tracing")
            emu.enable_ft_bus_trace()
        SCENARIOS[args.scenario](emu, regs, args)
        state = dump_state(emu, regs, args.backend, args.scenario, args.out_dir, args.dump_dl, args.boot_mode)
        print(f"state: {state['outputs']['state_json']}")
        print(f"png: {state['outputs']['png']}")
        if state["outputs"].get("vdac2_png"):
            print(f"vdac2_png: {state['outputs']['vdac2_png']}")
        print(f"ram_dl_sha256: {state['hashes']['ram_dl_sha256']}")
        if state["z80"]["errors"]:
            print(f"errors: {state['z80']['errors']}")
            return 1
        return 0
    finally:
        close = getattr(emu, "close", None)
        if close is not None:
            close()


if __name__ == "__main__":
    raise SystemExit(main())
