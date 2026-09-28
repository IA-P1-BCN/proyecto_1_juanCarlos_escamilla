"""Histórico en JSON — carreras finalizadas persistidas por día (#5)."""

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

from taximetro_kernel import Money

from taximetro.domain.registro import CarreraRegistro

# Los datos viven donde se ejecuta el taxímetro (`data/` del cwd),
# no dentro del paquete: el binario frozen no puede escribir en su bundle.
_RUTA_POR_DEFECTO = Path(os.environ.get("TAXIMETRO_DATA", "data")) / "historico.json"


class HistoricoJson:
    """Guarda cada CarreraRegistro al finalizar y recupera los de un día.

    El fichero se reescribe completo en cada guardar: el histórico del día cabe
    en memoria y la escritura por carrera ya es incremental a efectos del turno.
    """

    def __init__(self, ruta: Path = _RUTA_POR_DEFECTO) -> None:
        self._ruta = ruta

    def guardar(self, registro: CarreraRegistro) -> None:
        registros = self._leer()
        registros.append(registro)
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        self._ruta.write_text(
            json.dumps([_a_dict(r) for r in registros], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def del_dia(self, dia: date) -> list[CarreraRegistro]:
        return [r for r in self._leer() if r.inicio.astimezone().date() == dia]

    def _leer(self) -> list[CarreraRegistro]:
        if not self._ruta.exists():
            return []
        datos = json.loads(self._ruta.read_text(encoding="utf-8"))
        return [_de_dict(d) for d in datos]


def _a_dict(registro: CarreraRegistro) -> dict[str, object]:
    return {
        "inicio": registro.inicio.isoformat(),
        "duracion_segundos": registro.duracion_segundos,
        "importe_centimos": registro.importe.centimos,
    }


def _de_dict(datos: dict[str, Any]) -> CarreraRegistro:
    return CarreraRegistro(
        inicio=datetime.fromisoformat(str(datos["inicio"])),
        duracion_segundos=float(datos["duracion_segundos"]),
        importe=Money(centimos=int(datos["importe_centimos"])),
    )
