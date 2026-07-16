#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MSBUILD = Path(r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe")
PROJECT = ROOT / "Source" / "Tools" / "UnrealSpeccyRef" / "zx-evo-unreal" / "Unreal" / "Unreal2017.vcxproj"


def main() -> int:
    env = {}
    for key, value in os.environ.items():
        if key.lower() == "path":
            continue
        env[key] = value
    env["Path"] = os.pathsep.join(
        [
            r"C:\Windows\System32",
            r"C:\Windows",
            r"C:\Windows\System32\Wbem",
            str(MSBUILD.parent),
        ]
    )
    cmd = [
        str(MSBUILD),
        str(PROJECT),
        "/p:Configuration=Release",
        "/p:Platform=x64",
        "/p:PlatformToolset=v143",
        "/m",
    ]
    return subprocess.call(cmd, cwd=str(ROOT), env=env)


if __name__ == "__main__":
    raise SystemExit(main())
