# -*- mode: python ; coding: utf-8 -*-
# Binario nativo del taxímetro: `task bin` → bin/taximetro (onefile, macOS arm64).
# La entrada es la TUI del conductor (interfaces/tui.py) — no hay REPL en el binario.

import os

SPEC_DIR = SPECPATH  # directorio de este spec (inyectado por PyInstaller)
WS = os.path.join(SPEC_DIR, "..", "..")

a = Analysis(
    ["src/taximetro_cli/__main__.py"],
    pathex=[
        os.path.join(WS, "packages", "taximetro-kernel", "src"),
        os.path.join(WS, "packages", "taximetro-ride", "src"),
        os.path.join(WS, "packages", "taximetro-billing", "src"),
        os.path.join(WS, "packages", "taximetro-log", "src"),
        os.path.join(WS, "packages", "taximetro", "src"),
    ],
    datas=[
        ("src/taximetro_cli/infrastructure/textos.json", "taximetro_cli/infrastructure"),
        (os.path.join(WS, "packages", "taximetro-billing", "config", "tarifas.json"), "config"),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="taximetro",
    debug=False,
    strip=False,
    upx=False,
    console=True,
)
