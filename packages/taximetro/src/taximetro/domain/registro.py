"""CarreraRegistro — representación inmutable de una Carrera cerrada (#5)."""

from dataclasses import dataclass
from datetime import datetime

from taximetro.domain.dinero import Money


@dataclass(frozen=True)
class CarreraRegistro:
    """Lo que queda de una Carrera finalizada: fecha, duración e Importe."""

    inicio: datetime
    duracion_segundos: float
    importe: Money
