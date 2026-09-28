"""Eventos de dominio del contexto ride."""

from dataclasses import dataclass
from datetime import datetime

from taximetro_kernel import Estado


@dataclass(frozen=True)
class CarreraIniciada:
    """La Carrera arrancó: el cobro corre desde `momento`."""

    momento: datetime


@dataclass(frozen=True)
class EstadoCambiado:
    """El vehículo pasó a un nuevo Estado; la acumulación sigue su curso."""

    momento: datetime
    estado: Estado


@dataclass(frozen=True)
class CarreraFinalizada:
    """La Carrera se cerró; su Importe queda fijado."""

    momento: datetime
