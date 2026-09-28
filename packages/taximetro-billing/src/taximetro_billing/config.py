"""Configuración de billing: tarifas vigentes desde config/tarifas.json."""

import json
import sys
from decimal import Decimal
from pathlib import Path

from taximetro_billing.tarifa import Tarifa


def _raiz_recursos() -> Path:
    """Raíz de `config/`: el paquete fuente en dev, `_MEIPASS` en el binario frozen."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2]


# Resuelta contra el paquete fuente (instalación editable del workspace).
_RUTA_POR_DEFECTO = _raiz_recursos() / "config" / "tarifas.json"


def cargar_tarifa(ruta: Path = _RUTA_POR_DEFECTO) -> Tarifa:
    """Lee las tarifas (€/segundo) y las devuelve en céntimos exactos."""
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    return Tarifa(
        parada_centimos_por_segundo=int(
            Decimal(str(datos["parada_eur_segundo"])) * 100
        ),
        movimiento_centimos_por_segundo=int(
            Decimal(str(datos["movimiento_eur_segundo"])) * 100
        ),
    )
