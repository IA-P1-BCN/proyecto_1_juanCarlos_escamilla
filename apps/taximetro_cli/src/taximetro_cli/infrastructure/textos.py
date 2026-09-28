"""Textos de la interfaz — cargados de textos.json (español)."""

import json
from pathlib import Path

TEXTOS = json.loads((Path(__file__).parent / "textos.json").read_text(encoding="utf-8"))


def t(clave: str, **valores: str) -> str:
    """Traduce una clave de textos.json; interpola valores si los hay."""
    texto = str(TEXTOS.get(clave, clave))
    return texto.format(**valores) if valores else texto
