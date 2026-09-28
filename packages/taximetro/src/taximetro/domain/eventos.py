"""Estados y eventos del ciclo de vida de la Carrera."""

from dataclasses import dataclass
from enum import Enum


class Estado(Enum):
    PARADA = "parada"
    EN_MOVIMIENTO = "en_movimiento"


@dataclass(frozen=True)
class CarreraIniciada:
    """La Carrera arrancó: el cobro corre desde `momento`."""

    momento: float


@dataclass(frozen=True)
class EstadoCambiado:
    """El vehículo pasó a un nuevo Estado; la acumulación sigue su curso."""

    momento: float
    estado: Estado


@dataclass(frozen=True)
class CarreraFinalizada:
    """La Carrera se cerró; su Importe queda fijado."""

    momento: float
