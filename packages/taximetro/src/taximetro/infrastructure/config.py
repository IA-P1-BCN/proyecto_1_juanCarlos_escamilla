"""Configuración: tarifas vigentes desde config/tarifas.json."""

import json
from decimal import Decimal
from pathlib import Path

from taximetro.domain.tarifa import Tarifa

# Resuelta contra el paquete fuente (instalación editable del workspace).
_RUTA_POR_DEFECTO = Path(__file__).resolve().parents[3] / "config" / "tarifas.json"


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
