"""Bitácora de operación — JSON-lines legibles mientras el proceso corre (US-06)."""

import json
import logging
import os
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

# La bitácora vive donde se ejecuta el taxímetro (`data/` del cwd),
# no dentro del paquete: el binario frozen no puede escribir en su bundle.
_RUTA_POR_DEFECTO = Path(os.environ.get("TAXIMETRO_DATA", "data")) / "taximetro.log"


class BitacoraJSON:
    """Una línea JSON por evento de operación, en fichero rotativo (1 MB × 3)."""

    def __init__(self, ruta: Path = _RUTA_POR_DEFECTO) -> None:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        # Logger propio (no registrado en el manager): cada bitácora es independiente
        # y escribe/flushea línea a línea — legible sin intervenir el proceso.
        self._logger = logging.Logger(name="taximetro.bitacora", level=logging.INFO)
        handler = RotatingFileHandler(
            ruta, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(handler)

    def registrar(self, evento: str, **campos: Any) -> None:
        """Anota un evento con timestamp UTC; los campos extra viajan tal cual."""
        linea = json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "evento": evento,
                **campos,
            },
            ensure_ascii=False,
        )
        self._logger.info(linea)


def leer(ruta: Path) -> list[dict[str, Any]]:
    """Lee la bitácora como eventos (para diagnóstico y el futuro panel de la TUI)."""
    if not ruta.exists():
        return []
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    return [json.loads(linea) for linea in lineas if linea]
