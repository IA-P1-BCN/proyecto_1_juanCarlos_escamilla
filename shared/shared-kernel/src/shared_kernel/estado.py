"""Estado — situación del vehículo: parada o en_movimiento (glosario)."""

from enum import Enum


class Estado(Enum):
    PARADA = "parada"
    EN_MOVIMIENTO = "en_movimiento"
