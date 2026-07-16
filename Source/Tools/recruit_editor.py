#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Визуальный редактор раскладки диалога НАЙМА (Dialog::RecruitMonster).

Фон = RECRBKG.ICN[0] (321×304, оконно-локальные координаты). Поверх — перетаскиваемые
элементы (спрайт монстра, иконки золота, тексты). Пользователь расставляет их мышью;
ПО ЗАКРЫТИИ окна (или кнопкой «Save & Close») координаты якорей пишутся в JSON
(оконно-локальные native, как в fheroes2: offset.x + x, offset.y + y).

Запуск:
    python Source/Tools/recruit_editor.py            # GUI-редактор
    python Source/Tools/recruit_editor.py --selftest # только проверка загрузки ассетов (без окна)

Выход: Diagnostics/recruit_layout.json
Управление: ЛКМ-перетаскивание элемента; стрелки — точное смещение выбранного на 1px;
            колёсико — зум; правый список — живые координаты.
"""
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import town_pack as T
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Diagnostics" / "recruit_layout.json"

BG_ICN = "RECRBKG.ICN"          # окно найма (321×304)
PAD = 48                        # поле вокруг окна на холсте (px экрана)

# --- загрузка ассетов AGG ---
_agg, _ent = T.read_agg_index_with_expansion(T.AGG_PATH)
_pal = T.read_palette(T.agg_entry(_agg, _ent, "KB.PAL"))


def icn_to_rgba(icn_name, frame=0, opaque=False):
    """ICN-кадр → PIL RGBA (idx0 прозрачен, если не opaque)."""
    h, e = T.read_icn(T.agg_entry(_agg, _ent, icn_name))[frame]
    gi = T.decode_icn_indices(h, e)
    w, hh = h["w"], h["h"]
    img = Image.new("RGBA", (w, hh), (0, 0, 0, 0))
    px = img.load()
    for y in range(hh):
        row = y * w
        for x in range(w):
            idx = gi[row + x]
            if idx == 0 and not opaque:
                continue
            r, g, b = _pal[idx]
            px[x, y] = (r, g, b, 255)
    return img, w, hh


# --- элементы диалога (динамика, рисуется поверх RECRBKG). xy = якорь, оконно-локальный native.
# anchor: tl=верх-лево, center=центр, s=низ-центр, e=право (текст растёт влево). Начальные позиции —
# приблизительно по dialog_recruit.cpp; пользователь уточнит перетаскиванием.
ELEMENTS = [
    {"name": "title",           "kind": "text",   "anchor": "center", "text": "Recruit Peasants", "xy": [160, 11]},
    {"name": "monster_sprite",  "kind": "sprite", "anchor": "s",      "icn": "PEASANT.ICN", "frame": 1, "xy": [80, 130]},
    {"name": "cost_label",      "kind": "text",   "anchor": "tl",     "text": "Cost per troop:", "xy": [110, 47]},
    {"name": "cost_gold_icon",  "kind": "icon",   "anchor": "tl",     "icn": "RESOURCE.ICN", "frame": 6, "xy": [159, 59]},
    {"name": "cost_number",     "kind": "text",   "anchor": "center", "text": "20", "xy": [199, 89]},
    {"name": "available",       "kind": "text",   "anchor": "center", "text": "Available: 12", "xy": [80, 145]},
    {"name": "numbuy_label",    "kind": "text",   "anchor": "e",      "text": "Number to buy:", "xy": [170, 150]},
    {"name": "count",           "kind": "text",   "anchor": "center", "text": "12", "xy": [214, 147]},
    {"name": "total_gold_icon", "kind": "icon",   "anchor": "tl",     "icn": "RESOURCE.ICN", "frame": 6, "xy": [124, 184]},
    {"name": "total_number",    "kind": "text",   "anchor": "center", "text": "240", "xy": [160, 214]},
]

# цвета маркеров текста
TEXT_COLOR = {
    "title": "#ffe000", "cost_label": "#ffffff", "cost_number": "#ffe000",
    "available": "#ffffff", "numbuy_label": "#ffffff", "count": "#ffffff", "total_number": "#c0ffc0",
}
ANCHOR_TK = {"tl": "nw", "center": "center", "s": "s", "e": "e"}


def selftest():
    bg, bw, bh = icn_to_rgba(BG_ICN, 0, opaque=True)
    print(f"OK {BG_ICN}[0] = {bw}x{bh}")
    for el in ELEMENTS:
        if el["kind"] in ("sprite", "icon"):
            _, w, h = icn_to_rgba(el["icn"], el.get("frame", 0))
            print(f"  {el['name']:15} {el['icn']}[{el.get('frame',0)}] = {w}x{h}")
        else:
            print(f"  {el['name']:15} text '{el['text']}' anchor={el['anchor']} @ {el['xy']}")
    print("selftest ok")


def run_gui():
    import tkinter as tk
    from PIL import ImageTk

    bg_img, BGW, BGH = icn_to_rgba(BG_ICN, 0, opaque=True)

    root = tk.Tk()
    root.title("Recruit dialog layout editor — расставь элементы, закрой окно для записи")
    state = {"zoom": 2}

    main = tk.Frame(root)
    main.pack(fill="both", expand=True)

    side = tk.Frame(main, width=240, bg="#2b2b2b")
    side.pack(side="right", fill="y")
    side.pack_propagate(False)

    cwrap = tk.Frame(main)
    cwrap.pack(side="left", fill="both", expand=True)
    vbar = tk.Scrollbar(cwrap, orient="vertical")
    vbar.pack(side="right", fill="y")
    hbar = tk.Scrollbar(cwrap, orient="horizontal")
    hbar.pack(side="bottom", fill="x")
    canvas = tk.Canvas(cwrap, bg="#202020", highlightthickness=0,
                       xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    vbar.config(command=canvas.yview)
    hbar.config(command=canvas.xview)
    tk.Label(side, text="Элементы (оконно-локальные native)", bg="#2b2b2b", fg="#eee",
             wraplength=230, justify="left").pack(anchor="w", padx=6, pady=(8, 4))
    coord_labels = {}
    for el in ELEMENTS:
        lb = tk.Label(side, text="", bg="#2b2b2b", fg="#cfe", anchor="w", font=("Consolas", 9))
        lb.pack(anchor="w", padx=8)
        coord_labels[el["name"]] = lb
    status = tk.Label(side, text="", bg="#2b2b2b", fg="#ffd", anchor="w",
                      wraplength=230, justify="left", font=("Consolas", 9))
    status.pack(anchor="w", padx=6, pady=8)

    imgrefs = {}          # держим ссылки на PhotoImage (иначе GC)
    items = {}            # name -> canvas item id
    drag = {"name": None, "dx": 0, "dy": 0}

    def to_canvas(nx, ny):
        z = state["zoom"]
        return PAD + nx * z, PAD + ny * z

    def to_native(cx, cy):
        z = state["zoom"]
        return round((cx - PAD) / z), round((cy - PAD) / z)

    def redraw():
        canvas.delete("all")
        items.clear()
        imgrefs.clear()
        z = state["zoom"]
        # фон окна
        bg_disp = bg_img.resize((BGW * z, BGH * z), Image.NEAREST)
        imgrefs["_bg"] = ImageTk.PhotoImage(bg_disp)
        canvas.create_image(PAD, PAD, anchor="nw", image=imgrefs["_bg"])
        canvas.create_rectangle(PAD, PAD, PAD + BGW * z, PAD + BGH * z, outline="#666")
        canvas.config(scrollregion=(0, 0, PAD * 2 + BGW * z, PAD * 2 + BGH * z))
        # элементы
        for el in ELEMENTS:
            cx, cy = to_canvas(*el["xy"])
            tkanch = ANCHOR_TK[el["anchor"]]
            if el["kind"] in ("sprite", "icon"):
                spr, w, h = icn_to_rgba(el["icn"], el.get("frame", 0))
                sd = spr.resize((max(1, w * z), max(1, h * z)), Image.NEAREST)
                imgrefs[el["name"]] = ImageTk.PhotoImage(sd)
                iid = canvas.create_image(cx, cy, anchor=tkanch, image=imgrefs[el["name"]],
                                          tags=("elem", el["name"]))
            else:
                col = TEXT_COLOR.get(el["name"], "#ffffff")
                iid = canvas.create_text(cx, cy, anchor=tkanch, text=el["text"], fill=col,
                                         font=("Arial", max(8, 5 * z), "bold"), tags=("elem", el["name"]))
            items[el["name"]] = iid
            # якорь-крестик
            canvas.create_line(cx - 5, cy, cx + 5, cy, fill="#ff2020", tags=("cross", el["name"]))
            canvas.create_line(cx, cy - 5, cx, cy + 5, fill="#ff2020", tags=("cross", el["name"]))
        update_side()

    def update_side():
        for el in ELEMENTS:
            coord_labels[el["name"]].config(
                text=f"{el['name']:15}[{el['anchor']:6}] x={el['xy'][0]:3} y={el['xy'][1]:3}")

    def elem_at(cx, cy):
        hit = canvas.find_closest(cx, cy)
        if not hit:
            return None
        tags = canvas.gettags(hit[0])
        for el in ELEMENTS:
            if el["name"] in tags:
                return el["name"]
        return None

    def on_press(ev):
        cx = canvas.canvasx(ev.x); cy = canvas.canvasy(ev.y)
        name = elem_at(cx, cy)
        drag["name"] = name
        if name:
            acx, acy = to_canvas(*next(e for e in ELEMENTS if e["name"] == name)["xy"])
            drag["dx"] = cx - acx; drag["dy"] = cy - acy
            status.config(text=f"выбран: {name}")

    def on_motion(ev):
        name = drag["name"]
        if not name:
            return
        cx = canvas.canvasx(ev.x) - drag["dx"]
        cy = canvas.canvasy(ev.y) - drag["dy"]
        nx, ny = to_native(cx, cy)
        nx = max(0, min(BGW, nx)); ny = max(0, min(BGH, ny))
        el = next(e for e in ELEMENTS if e["name"] == name)
        el["xy"] = [nx, ny]
        move_elem(name)

    def move_elem(name):
        el = next(e for e in ELEMENTS if e["name"] == name)
        ncx, ncy = to_canvas(*el["xy"])
        canvas.coords(items[name], ncx, ncy)
        # перерисуем крестик
        canvas.delete("cross_" + name)
        for cid in canvas.find_withtag(name):
            pass
        # проще: убрать старые cross с этим именем и создать новые
        for cid in list(canvas.find_withtag("cross")):
            if name in canvas.gettags(cid):
                canvas.delete(cid)
        canvas.create_line(ncx - 5, ncy, ncx + 5, ncy, fill="#ff2020", tags=("cross", name))
        canvas.create_line(ncx, ncy - 5, ncx, ncy + 5, fill="#ff2020", tags=("cross", name))
        coord_labels[name].config(text=f"{name:15}[{el['anchor']:6}] x={el['xy'][0]:3} y={el['xy'][1]:3}")
        status.config(text=f"{name}: x={el['xy'][0]} y={el['xy'][1]}")

    def nudge(dx, dy):
        name = drag["name"]
        if not name:
            return
        el = next(e for e in ELEMENTS if e["name"] == name)
        el["xy"][0] = max(0, min(BGW, el["xy"][0] + dx))
        el["xy"][1] = max(0, min(BGH, el["xy"][1] + dy))
        move_elem(name)

    def on_wheel(ev):
        state["zoom"] = max(1, min(6, state["zoom"] + (1 if ev.delta > 0 else -1)))
        redraw()

    def save():
        data = {"window": BG_ICN, "w": BGW, "h": BGH,
                "elements": {el["name"]: {"anchor": el["anchor"], "x": el["xy"][0], "y": el["xy"][1]}
                             for el in ELEMENTS}}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print("saved", OUT)

    def save_and_close():
        save()
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_motion)
    canvas.bind("<MouseWheel>", on_wheel)
    root.bind("<Left>", lambda e: nudge(-1, 0))
    root.bind("<Right>", lambda e: nudge(1, 0))
    root.bind("<Up>", lambda e: nudge(0, -1))
    root.bind("<Down>", lambda e: nudge(0, 1))
    root.protocol("WM_DELETE_WINDOW", save_and_close)   # запись координат по закрытию

    tk.Button(side, text="Save & Close", command=save_and_close, bg="#3a5", fg="white",
              font=("Arial", 11, "bold")).pack(side="bottom", fill="x", padx=6, pady=8)

    redraw()
    root.geometry("1030x780")     # холст ~770 (321×2 + поля) + боковая панель 240
    root.mainloop()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
    else:
        run_gui()
