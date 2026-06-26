#!/usr/bin/env python3
"""Реальный поток отладки на РАБОЧЕМ билде (DBG_BOOT off): надёжный клик по логической цели.

МЕХАНИЗМ (после патча Unreal input.cpp): `uipos.req` = "x y" (логич. 640x480) → эмулятор каждый
кадр пишет Input.Mouse.PositionX/Y (#51F6/#51F8) в RAM игры — курсор встаёт ТОЧНО (без relative-гонки
vmouse). Пока файл есть — позиция держится. Клик — `vmouse.bin` buttons bit0 (active-low LMB), dx=dy=0
(позицию не трогает). Удалить uipos.req = отпустить.

statedump.bin (dump.req=b"5") = page5(#4000..)+page6: UIClickX@0x241, UIClickY@0x243, MenuHoverIndex@0x267.
"""
import struct, sys, time
from pathlib import Path

UDIR = Path(r"C:/Users/Администратор/Desktop/unreal_x64")
VM = UDIR / "vmouse.bin"
UIPOS = UDIR / "uipos.req"
DUMPREQ = UDIR / "dump.req"
STATEDUMP = UDIR / "statedump.bin"

def write_vm(active, buttons, dx=0, dy=0):
    VM.write_bytes(struct.pack("<BBii", active, buttons, int(dx), int(dy)))

def set_pos(x, y):
    UIPOS.write_text(f"{x} {y}")     # держится эмулятором каждый кадр, пока файл есть

def release_pos():
    if UIPOS.exists():
        UIPOS.unlink()
    write_vm(0, 0)

def read_state():
    if STATEDUMP.exists():
        STATEDUMP.unlink()
    DUMPREQ.write_bytes(b"5")
    for _ in range(40):
        time.sleep(0.05)
        if STATEDUMP.exists():
            break
    time.sleep(0.05)
    d = STATEDUMP.read_bytes()
    ux = int.from_bytes(d[0x241:0x243], "little")
    uy = int.from_bytes(d[0x243:0x245], "little")
    hv = d[0x267]
    tx = d[0x204]                        # CursorTileX #4204
    ty = d[0x205]                        # CursorTileY #4205
    gm = d[0x203]                        # GameMode #4203
    return ux, uy, hv, tx, ty, gm

def click_at(x, y, verify=True):
    set_pos(x, y)
    time.sleep(0.35)                  # курсор встал + hover посчитан
    if verify:
        ux, uy, hv, tx, ty, gm = read_state()
        print(f"  before click: UIClick=({ux},{uy}) hover={hv if hv!=0xFF else 'NONE'} tile=({tx},{ty}) gm={gm}")
        set_pos(x, y); time.sleep(0.05)   # дамп снял uipos-удержание — восстановить позицию
    for _ in range(14):               # ЛКМ нажата (active-low: buttons bit0=1)
        write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(8):                # отпустить
        write_vm(1, 0, 0, 0); time.sleep(0.02)
    release_pos()

def find_tile_pixel(target_tx, target_ty, x0=288, y0=288):
    """Замкнутый контур по логическому пикселю → CursorTileX/Y == target (для клика по объекту карты)."""
    x, y = x0, y0
    for _ in range(8):
        set_pos(x, y); time.sleep(0.2)
        ux, uy, hv, tx, ty, gm = read_state()
        print(f"  pixel=({x},{y}) -> tile=({tx},{ty}) gm={gm}")
        if tx == target_tx and ty == target_ty:
            return x, y
        x += (target_tx - tx) * 32       # тайл = 32 логич.px
        y += (target_ty - ty) * 32
    return x, y

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "pos":     # только поставить курсор+проверить
        x = int(sys.argv[2]); y = int(sys.argv[3])
        set_pos(x, y); time.sleep(0.35)
        print("pos ->", read_state())
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "townstay":  # вход в город БЕЗ выхода (для снимка)
        click_at(522, 232, verify=False); time.sleep(5)
        cx, cy = find_tile_pixel(24, 13)
        click_at(cx, cy, verify=False); time.sleep(4)
        ux, uy, hv, tx, ty, gm = read_state()
        print(f"   in town: GameMode={gm}")
        release_pos()
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "town":    # меню→New Game→клик по замку (24,13)→город
        print("1) click New Game (522,232)")
        click_at(522, 232, verify=True)
        print("2) wait adventure load...")
        time.sleep(5)
        print("3) find castle tile (24,13)")
        cx, cy = find_tile_pixel(24, 13)
        print(f"4) click castle at pixel ({cx},{cy})")
        click_at(cx, cy, verify=True)
        print("5) wait town load...")
        time.sleep(4)
        ux, uy, hv, tx, ty, gm = read_state()
        print(f"   in town: GameMode={gm} (1=TOWN expected)")
        print("6) click in town -> exit back to adventure")
        click_at(300, 300, verify=False)   # любой клик в городе = выход
        time.sleep(4)
        ux, uy, hv, tx, ty, gm = read_state()
        print(f"   after exit: GameMode={gm} (0=ADVENTURE expected)")
        release_pos()
        sys.exit(0)
    x = int(sys.argv[1]) if len(sys.argv) > 1 else 522   # New Game center
    y = int(sys.argv[2]) if len(sys.argv) > 2 else 232
    print(f"realflow click at ({x},{y})")
    click_at(x, y)
    print("click sent; waiting adventure load from SD...")
