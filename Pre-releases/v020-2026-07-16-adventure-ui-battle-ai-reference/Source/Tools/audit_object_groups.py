#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DIAG = ROOT / "Diagnostics" / "object_group_audit"

GROUPS = [
    "OBJNARTI",
    "MONS32",
    "FLAG32",
    "MINIHERO",
    "OBJNTOWN",
    "OBJNTWRD",
    "OBJNRSRC",
    "MTNSNOW",
    "MTNSWMP",
    "MTNLAVA",
    "MTNDSRT",
    "MTNDIRT",
    "MTNMULT",
    "MTNCRCK",
    "MTNGRAS",
    "TREJNGL",
    "TREEVIL",
    "TRESNOW",
    "TREFIR",
    "TREFALL",
    "OBJNGRAS",
    "OBJNSNOW",
    "OBJNSWMP",
    "OBJNLAVA",
    "OBJNDSRT",
    "OBJNDIRT",
    "OBJNCRCK",
]


def run(cmd, env=None) -> subprocess.CompletedProcess:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(cmd, cwd=ROOT, env=merged, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def main() -> int:
    DIAG.mkdir(parents=True, exist_ok=True)
    report = []
    for group in GROUPS:
        env = {"HMM2_OBJECT_LAYER": "1", "HMM2_OBJECT_ICNS": group}
        build = run(["cmd", "/c", "build.cmd"], env=env)
        log_path = DIAG / f"{group}.build.log"
        log_path.write_text(build.stdout, encoding="utf-8")
        if build.returncode != 0:
            report.append(f"{group}: BUILD_FAIL")
            continue
        snap = run(["python", "Source\\Tools\\hmm2_ft812_snapshot.py", "--out", str(DIAG / f"{group}.png")], env=env)
        (DIAG / f"{group}.snapshot.log").write_text(snap.stdout, encoding="utf-8")
        if snap.returncode != 0:
            report.append(f"{group}: SNAPSHOT_FAIL")
            continue
        shutil.copy2(ROOT / "Source" / "ASM" / "generated_adventure_dl.inc", DIAG / f"{group}.dl.inc")
        report.append(f"{group}: OK")

    # Возвращаем рабочую сборку в режим без объектов после аудита.
    final_build = run(["cmd", "/c", "build.cmd"], env={"HMM2_OBJECT_LAYER": "0"})
    (DIAG / "_restore_terrain_only.build.log").write_text(final_build.stdout, encoding="utf-8")
    (DIAG / "report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    return 0 if final_build.returncode == 0 else final_build.returncode


if __name__ == "__main__":
    raise SystemExit(main())
