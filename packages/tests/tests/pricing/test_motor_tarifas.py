"""El Motor de tarifas aplica la Tarifa vigente — costura: motor de tarifas de
pricing (spec #14): precisión de las reglas de dinero con duraciones controladas."""

from pricing import MotorDeTarifas
from shared_kernel import Money


def test_en_parada_acumula_0_02_eur_por_segundo() -> None:
    motor = MotorDeTarifas()

    importe = motor.importe_en_parada(segundos=10)

    assert importe == Money(centimos=20)
    assert importe.formato() == "0,20 €"
