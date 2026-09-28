"""Estado y Tramo — el vocabulario que ride produce y billing lee."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Estado(Enum):
    PARADA = "parada"
    EN_MOVIMIENTO = "en_movimiento"


@dataclass(frozen=True)
class Tramo:
    """Trecho de Carrera en un Estado; fin=None mientras está en curso."""

    estado: Estado
    inicio: datetime
    fin: datetime | None = None
