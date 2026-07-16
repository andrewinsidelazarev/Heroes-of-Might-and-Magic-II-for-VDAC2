#!/usr/bin/env python3
"""Adventure → отвести героя на безопасный тайл, затем ПРИЙТИ на гейт (24,13) → вход в город.
Вход = прибытие героя на тайл (game_state:687), движение ДВУХкликовое. Проверка по gm==1 на Unreal."""
import time, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import realflow_click as R

U = Path(r"C:/Users/Администратор/Desktop/unreal_x64")

def clk(x, y):
    R.set_pos(x, y); time.sleep(0.45)
    for _ in range(6):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    for _ in range(12): R.write_vm(1, 1, 0, 0); time.sleep(0.02)
    for _ in range(8):  R.write_vm(1, 0, 0, 0); time.sleep(0.02)
    R.release_pos(); time.sleep(0.15)

def move_to(col, row, settle=3.5):
    cx, cy = R.find_tile_pixel(col, row)
    clk(cx, cy); time.sleep(0.3); clk(cx, cy)      # двухкликовое движение
    time.sleep(settle)

def main():
    subprocess.Popen([str(U / "Unreal.exe"), "hmm2_vdac2.spg"], cwd=str(U)); time.sleep(14)
    clk(522, 232); time.sleep(7)                    # New Game → adventure
    print("gm после New Game:", R.read_state()[5])
    move_to(24, 15)                                  # отойти на безопасный тайл (колонка 24, не 13/16)
    print("gm после отхода на (24,15):", R.read_state()[5], "(ожидаю 0)")
    move_to(24, 13)                                  # вернуться на гейт → Town_Enter по прибытии
    for _ in range(16):
        if R.read_state()[5] == 1: break
        time.sleep(0.4)
    gm = R.read_state()[5]
    print("gm после прихода на (24,13):", gm, "→", "ГОРОД ОТКРЫТ ✓" if gm == 1 else "НЕ открыт ✗")
    if gm == 1:
        import time as _t; _t.sleep(1.6)
        from PIL import Image
        DIAG = Path(__file__).resolve().parents[2] / "Diagnostics"
        Image.open(str(U / "ft812_dump.bmp")).convert("RGB").save(str(DIAG / "town_real.png"))
        print("реальный кадр города → town_real.png")

if __name__ == "__main__":
    main()
