"""Tarifa — precios por Estado y derivación única del Importe."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from taximetro_kernel import Estado, Money, Tramo


@dataclass(frozen=True)
class Tarifa:
    """Par de precios vigentes en céntimos/segundo: parada y en movimiento."""

    parada_centimos_por_segundo: int
    movimiento_centimos_por_segundo: int

    def centimos_por_segundo(self, estado: Estado) -> int:
        if estado is Estado.PARADA:
            return self.parada_centimos_por_segundo
        return self.movimiento_centimos_por_segundo


def calcular_importe(
    tramos: Sequence[Tramo], tarifa: Tarifa, hasta: datetime | None = None
) -> Money:
    """Deriva el Importe de los tramos; el último abierto corre hasta `hasta`.

    Redondea UNA sola vez (half-up) al final: nunca por tramo.
    """
    total = Decimal(0)
    for tramo in tramos:
        fin = tramo.fin if tramo.fin is not None else hasta
        if fin is None:
            continue
        duracion = Decimal(str((fin - tramo.inicio).total_seconds()))
        total += duracion * tarifa.centimos_por_segundo(tramo.estado)
    return Money(centimos=int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)))
