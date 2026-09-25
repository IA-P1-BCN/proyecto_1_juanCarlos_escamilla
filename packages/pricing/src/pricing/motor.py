"""Motor de tarifas — aplica la Tarifa vigente a la actividad de la Carrera."""

from dataclasses import dataclass

from shared_kernel import Money


@dataclass(frozen=True)
class Tarifa:
    """Par de precios vigentes en céntimos/segundo: parada y en movimiento."""

    parada_centimos_por_segundo: int
    movimiento_centimos_por_segundo: int


# Tarifas Zona EMT Madrid (junio 2025), hardcoded en Fase 1
# (US-07 las externaliza a fichero en Fase 2).
TARIFA_VIGENTE = Tarifa(
    parada_centimos_por_segundo=2, movimiento_centimos_por_segundo=5
)


class MotorDeTarifas:
    """Calcula el Importe aplicando la tarifa del Estado al tiempo transcurrido."""

    def __init__(self, tarifa: Tarifa = TARIFA_VIGENTE) -> None:
        self._tarifa = tarifa

    def importe_en_parada(self, segundos: float) -> Money:
        return Money(
            centimos=round(segundos * self._tarifa.parada_centimos_por_segundo)
        )
