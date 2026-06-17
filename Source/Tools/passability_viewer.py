#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageDraw, ImageTk

from agg_tools import read_agg_index
from object_atlas import ICN_BY_OBJECT_TYPE, agg_entry as object_agg_entry, decode_icn_sprite, read_icn, read_palette as read_object_palette
from terrain_atlas import agg_entry as terrain_agg_entry, read_til, read_palette as read_terrain_palette, transform_tile
from terrain_preview import TILE_PX, read_map


ROOT = Path(__file__).resolve().parents[2]
PATH_FLAG_WATER = 0x01
PATH_FLAG_STOP = 0x02
PATH_FLAG_ROAD = 0x04


def terrain_color(terrain: int) -> tuple[int, int, int]:
    if terrain < 30:
        return (36, 80, 128)
    if terrain < 92:
        return (38, 118, 44)
    if terrain < 146:
        return (180, 184, 190)
    if terrain < 208:
        return (74, 98, 62)
    if terrain < 262:
        return (112, 54, 38)
    if terrain < 321:
        return (150, 106, 54)
    if terrain < 361:
        return (120, 74, 38)
    if terrain < 415:
        return (92, 82, 70)
    return (180, 158, 92)


def pass_color(mask: int, alpha: int) -> tuple[int, int, int, int]:
    if mask == 0x00:
        return (220, 30, 30, alpha)
    if mask == 0xFF:
        return (30, 190, 70, alpha)
    return (255, 210, 0, alpha)


def path_flag_label(flags: int) -> str:
    label = ""
    if flags & PATH_FLAG_WATER:
        label += "W"
    if flags & PATH_FLAG_STOP:
        label += "S"
    if flags & PATH_FLAG_ROAD:
        label += "R"
    return label or "-"


def path_flag_color(flags: int, alpha: int) -> tuple[int, int, int, int]:
    if flags & PATH_FLAG_STOP:
        return (210, 40, 210, alpha)
    if flags & PATH_FLAG_ROAD:
        return (40, 170, 230, alpha)
    if flags & PATH_FLAG_WATER:
        return (45, 90, 220, alpha)
    return (0, 0, 0, 0)


def make_flat_background(width: int, height: int, tiles) -> Image.Image:
    image = Image.new("RGB", (width * TILE_PX, height * TILE_PX))
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(height):
        for x in range(width):
            tile = tiles[y * width + x]
            box = (x * TILE_PX, y * TILE_PX, (x + 1) * TILE_PX - 1, (y + 1) * TILE_PX - 1)
            draw.rectangle(box, fill=terrain_color(tile["terrain"]))
    return image


def pil_tile(raw: bytes, palette) -> Image.Image:
    image = Image.new("RGB", (TILE_PX, TILE_PX))
    image.putdata([palette[pix] for pix in raw])
    return image


def argb4_to_image(raw: bytes, width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height))
    pixels = []
    for i in range(width * height):
        value = raw[i * 2] | (raw[i * 2 + 1] << 8)
        a = ((value >> 12) & 15) * 17
        r = ((value >> 8) & 15) * 17
        g = ((value >> 4) & 15) * 17
        b = (value & 15) * 17
        pixels.append((r, g, b, a))
    image.putdata(pixels)
    return image


def collect_object_parts(tile, addons, tile_x: int, tile_y: int):
    parts = []

    def add(layer: int, object_name: int, index: int, top: bool) -> None:
        icn_type = object_name >> 2
        icn_name = ICN_BY_OBJECT_TYPE.get(icn_type)
        if icn_name and index != 0xFF:
            parts.append({"tile_x": tile_x, "tile_y": tile_y, "icn": icn_name, "index": index, "layer": layer, "top": top})

    add(tile["quantity1"] & 0x03, tile["object_name1"], tile["bottom_icn"], False)
    add(0, tile["object_name2"], tile["top_icn"], True)

    addon_index = tile.get("next_addon", 0)
    guard = 0
    while addon_index > 0 and addon_index < len(addons) and guard < 128:
        addon = addons[addon_index]
        add(addon["quantity"] & 0x03, addon["object_name1"], addon["bottom_icn"], False)
        add(0, addon["object_name2"], addon["top_icn"], True)
        addon_index = addon["next_addon"]
        guard += 1

    ground = [part for part in parts if not part["top"]]
    top = [part for part in parts if part["top"]]
    ground.sort(key=lambda item: item["layer"], reverse=True)
    return ground + top


def render_full_background(agg_path: Path, width: int, height: int, map_data) -> Image.Image:
    tiles, addons = map_data if isinstance(map_data, tuple) else (map_data, [])
    agg_data, entries = read_agg_index(agg_path)
    terrain_tiles = read_til(terrain_agg_entry(agg_data, entries, "GROUND32.TIL"))
    palette = read_terrain_palette(terrain_agg_entry(agg_data, entries, "KB.PAL"))

    image = Image.new("RGBA", (width * TILE_PX, height * TILE_PX), (0, 0, 0, 255))
    terrain_cache = {}
    for y in range(height):
        for x in range(width):
            tile = tiles[y * width + x]
            terrain = tile["terrain"]
            shape = tile["terrain_flags"] & 3
            key = (terrain, shape)
            if key not in terrain_cache:
                if terrain >= len(terrain_tiles):
                    raise ValueError(f"индекс terrain {terrain} вне GROUND32.TIL")
                terrain_cache[key] = pil_tile(transform_tile(terrain_tiles[terrain], shape), palette).convert("RGBA")
            image.alpha_composite(terrain_cache[key], (x * TILE_PX, y * TILE_PX))

    object_palette = read_object_palette(object_agg_entry(agg_data, entries, "KB.PAL"))
    icn_cache = {}
    sprite_cache = {}
    for y in range(height):
        for x in range(width):
            tile = tiles[y * width + x]
            for part in collect_object_parts(tile, addons, x, y):
                key = (part["icn"], part["index"])
                if key not in sprite_cache:
                    if part["icn"] not in icn_cache:
                        icn_cache[part["icn"]] = read_icn(object_agg_entry(agg_data, entries, part["icn"]))
                    sprites = icn_cache[part["icn"]]
                    if part["index"] >= len(sprites):
                        continue
                    header, encoded = sprites[part["index"]]
                    if header["w"] == 0 or header["h"] == 0:
                        continue
                    raw = decode_icn_sprite(header, encoded, object_palette)
                    sprite_cache[key] = {
                        "image": argb4_to_image(raw, header["w"], header["h"]),
                        "ox": header["ox"],
                        "oy": header["oy"],
                    }
                sprite = sprite_cache.get(key)
                if sprite is None:
                    continue
                px = part["tile_x"] * TILE_PX + sprite["ox"]
                py = part["tile_y"] * TILE_PX + sprite["oy"]
                image.alpha_composite(sprite["image"], (px, py))

    return image.convert("RGB")


def make_passability(width: int, height: int, masks: bytes, alpha: int, draw_text: bool) -> Image.Image:
    image = Image.new("RGBA", (width * TILE_PX, height * TILE_PX), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(height):
        for x in range(width):
            mask = masks[y * width + x]
            box = (x * TILE_PX, y * TILE_PX, (x + 1) * TILE_PX - 1, (y + 1) * TILE_PX - 1)
            draw.rectangle(box, fill=pass_color(mask, alpha))
            if draw_text and mask not in (0x00, 0xFF):
                draw.text((x * TILE_PX + 4, y * TILE_PX + 8), f"{mask:02X}", fill=(0, 0, 0, 255))
    return image


def draw_grid(image: Image.Image, width: int, height: int) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    color = (0, 0, 0, 70)
    for x in range(width + 1):
        sx = x * TILE_PX
        draw.line((sx, 0, sx, height * TILE_PX), fill=color)
    for y in range(height + 1):
        sy = y * TILE_PX
        draw.line((0, sy, width * TILE_PX, sy), fill=color)


class PassabilityViewer:
    def __init__(
        self,
        root: tk.Tk,
        width: int,
        height: int,
        tiles,
        masks: bytes,
        path_flags: bytes | None,
        background: Image.Image,
        origin_x: int,
        origin_y: int,
    ) -> None:
        self.root = root
        self.width = width
        self.height = height
        self.tiles = tiles
        self.masks = masks
        self.path_flags = path_flags
        self.background = background.convert("RGB")
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.view_w = self.background.width // TILE_PX
        self.view_h = self.background.height // TILE_PX
        self.show_pass = tk.BooleanVar(value=True)
        self.show_flags = tk.BooleanVar(value=path_flags is not None)
        self.show_grid = tk.BooleanVar(value=True)
        self.show_text = tk.BooleanVar(value=True)
        self.alpha = tk.IntVar(value=150)
        self.zoom = tk.IntVar(value=1)
        self.photo = None

        root.title("HMM2 passability viewer")

        toolbar = tk.Frame(root)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        tk.Checkbutton(toolbar, text="Passability", variable=self.show_pass, command=self.render).pack(side=tk.LEFT)
        tk.Checkbutton(toolbar, text="Path flags", variable=self.show_flags, command=self.render).pack(side=tk.LEFT)
        tk.Checkbutton(toolbar, text="Grid", variable=self.show_grid, command=self.render).pack(side=tk.LEFT)
        tk.Checkbutton(toolbar, text="Mask text", variable=self.show_text, command=self.render).pack(side=tk.LEFT)
        tk.Label(toolbar, text="Alpha").pack(side=tk.LEFT, padx=(12, 2))
        tk.Scale(toolbar, from_=0, to=230, orient=tk.HORIZONTAL, variable=self.alpha, command=lambda _v: self.render(), length=160).pack(side=tk.LEFT)
        tk.Label(toolbar, text="Zoom").pack(side=tk.LEFT, padx=(12, 2))
        tk.Scale(toolbar, from_=1, to=4, orient=tk.HORIZONTAL, variable=self.zoom, command=lambda _v: self.render(), length=120).pack(side=tk.LEFT)

        self.status = tk.Label(root, anchor="w")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        body = tk.Frame(root)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(body, width=min(self.background.width, 1024), height=min(self.background.height, 720), bg="black")
        vscroll = tk.Scrollbar(body, orient=tk.VERTICAL, command=self.canvas.yview)
        hscroll = tk.Scrollbar(body, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=hscroll.set, yscrollcommand=vscroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vscroll.grid(row=0, column=1, sticky="ns")
        hscroll.grid(row=1, column=0, sticky="ew")
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        self.render()

    def render(self) -> None:
        image = self.background.convert("RGBA")
        if self.show_pass.get():
            image.alpha_composite(self.make_view_passability())
        if self.show_flags.get() and self.path_flags is not None:
            image.alpha_composite(self.make_view_path_flags())
        if self.show_grid.get():
            draw_grid(image, self.view_w, self.view_h)

        zoom = self.zoom.get()
        if zoom != 1:
            image = image.resize((image.width * zoom, image.height * zoom), Image.Resampling.NEAREST)

        self.photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, image.width, image.height))
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")

    def on_motion(self, event) -> None:
        zoom = self.zoom.get()
        view_x = int(self.canvas.canvasx(event.x) // (TILE_PX * zoom))
        view_y = int(self.canvas.canvasy(event.y) // (TILE_PX * zoom))
        x = self.origin_x + view_x
        y = self.origin_y + view_y
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            self.status.config(text="")
            return
        index = y * self.width + x
        tile = self.tiles[index]
        mask = self.masks[index]
        flags = self.path_flags[index] if self.path_flags is not None else 0
        self.status.config(
            text=(
                f"tile={x},{y} mask={mask:02X} flags={flags:02X}({path_flag_label(flags)}) terrain={tile['terrain']} "
                f"map_object={tile['map_object']} obj1={tile['object_name1'] >> 2}:{tile['bottom_icn']} "
                f"obj2={tile['object_name2'] >> 2}:{tile['top_icn']}"
            )
        )

    def on_mouse_wheel(self, event) -> None:
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def make_view_passability(self) -> Image.Image:
        image = Image.new("RGBA", self.background.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image, "RGBA")
        for view_y in range(self.view_h):
            y = self.origin_y + view_y
            if y >= self.height:
                continue
            for view_x in range(self.view_w):
                x = self.origin_x + view_x
                if x >= self.width:
                    continue
                mask = self.masks[y * self.width + x]
                box = (view_x * TILE_PX, view_y * TILE_PX, (view_x + 1) * TILE_PX - 1, (view_y + 1) * TILE_PX - 1)
                draw.rectangle(box, fill=pass_color(mask, self.alpha.get()))
                if self.show_text.get() and mask not in (0x00, 0xFF):
                    draw.text((view_x * TILE_PX + 4, view_y * TILE_PX + 8), f"{mask:02X}", fill=(0, 0, 0, 255))
        return image

    def make_view_path_flags(self) -> Image.Image:
        image = Image.new("RGBA", self.background.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image, "RGBA")
        assert self.path_flags is not None
        for view_y in range(self.view_h):
            y = self.origin_y + view_y
            if y >= self.height:
                continue
            for view_x in range(self.view_w):
                x = self.origin_x + view_x
                if x >= self.width:
                    continue
                flags = self.path_flags[y * self.width + x]
                label = path_flag_label(flags)
                if label == "-":
                    continue
                px = view_x * TILE_PX
                py = view_y * TILE_PX
                fill = path_flag_color(flags, 210)
                draw.rectangle((px + 1, py + 1, px + 17, py + 11), fill=fill)
                draw.text((px + 3, py), label, fill=(255, 255, 255, 255))
        return image


def main() -> None:
    parser = argparse.ArgumentParser(description="Интерактивно показать фон карты и passability без внешних редакторов.")
    parser.add_argument("--map", type=Path, default=ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.map.bin")
    parser.add_argument("--passability", type=Path, default=ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.pass.bin")
    parser.add_argument("--path-metadata", type=Path, default=ROOT / "Assets" / "Converted" / "Maps" / "SKIRMISH.path.bin")
    parser.add_argument("--agg", type=Path, default=ROOT / "Assets" / "Original" / "DATA" / "HEROES2.AGG")
    parser.add_argument("--background", type=Path, default=None)
    parser.add_argument("--origin-x", type=int, default=0)
    parser.add_argument("--origin-y", type=int, default=0)
    args = parser.parse_args()

    width, height, map_data = read_map(args.map)
    tiles = map_data[0] if isinstance(map_data, tuple) else map_data
    masks = args.passability.read_bytes()
    if len(masks) != width * height:
        raise ValueError(f"{args.passability}: размер {len(masks)} не равен {width * height}")
    path_flags = None
    if args.path_metadata.exists():
        path_metadata = args.path_metadata.read_bytes()
        if len(path_metadata) != width * height * 2:
            raise ValueError(f"{args.path_metadata}: размер {len(path_metadata)} не равен {width * height * 2}")
        path_flags = path_metadata[width * height:]

    if args.background is not None and args.background.exists():
        background = Image.open(args.background).convert("RGB")
    else:
        background = render_full_background(args.agg, width, height, map_data)
        args.origin_x = 0
        args.origin_y = 0

    root = tk.Tk()
    PassabilityViewer(root, width, height, tiles, masks, path_flags, background, args.origin_x, args.origin_y)
    root.mainloop()


if __name__ == "__main__":
    main()
