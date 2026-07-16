from pathlib import Path


OUT_INC = Path("Source/ASM/generated_scale_table.inc")
OUT_BIN = Path("Build/scale8_5_x16.bin")


def main() -> int:
    table_size = 2048
    values = [(x * 128) // 5 for x in range(table_size)]
    lines = [
        "; Сгенерировано Source/Tools/gen_scale_table.py",
        f"; HL -> HL*8/5*16 для координат 0..{table_size - 1}.",
        "",
        "Scale8_5_X16_Table:",
    ]
    for i in range(0, table_size, 8):
        lines.append("                DEFW " + ", ".join(str(v) for v in values[i:i + 8]))
    lines.append("")
    OUT_INC.write_text("\n".join(lines), encoding="utf-8")

    OUT_BIN.parent.mkdir(parents=True, exist_ok=True)
    raw = bytearray()
    for value in values:
        raw.append(value & 0xFF)
        raw.append((value >> 8) & 0xFF)
    OUT_BIN.write_bytes(raw)

    print(f"scale table: {OUT_INC}, {OUT_BIN}, words={table_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
