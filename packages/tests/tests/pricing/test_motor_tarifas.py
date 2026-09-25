"""El Motor de tarifas aplica la Tarifa a cada tramo — costura: motor de tarifas de
pricing (spec #14, #17): reglas de dinero con duraciones controladas."""

from pricing import MotorDeTarifas
from shared_kernel import Estado, Money


def test_tramo_en_parada_aplica_0_02_eur_por_segundo() -> None:
    motor = MotorDeTarifas()

    importe = motor.importe_de_tramo(Estado.PARADA, segundos=10)

    assert importe == Money(centimos=20)
    assert importe.formato() == "0,20 €"


def test_tramo_en_movimiento_aplica_0_05_eur_por_segundo() -> None:
    motor = MotorDeTarifas()

    importe = motor.importe_de_tramo(Estado.EN_MOVIMIENTO, segundos=8)

    assert importe == Money(centimos=40)
    assert importe.formato() == "0,40 €"
