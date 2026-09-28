"""El Importe se deriva de los tramos — motor del contexto billing (spec #14)."""

from datetime import UTC, datetime

from taximetro_billing import Tarifa, calcular_importe, cargar_tarifa
from taximetro_kernel import Estado, Money, Tramo

TARIFA_EMT = Tarifa(parada_centimos_por_segundo=2, movimiento_centimos_por_segundo=5)


def hora(h: int, m: int = 0, s: int = 0, ms: int = 0) -> datetime:
    return datetime(2026, 9, 28, h, m, s, ms, tzinfo=UTC)


def _tramos_cerrados() -> tuple[Tramo, Tramo]:
    return (
        Tramo(estado=Estado.PARADA, inicio=hora(10), fin=hora(10, 0, 5)),
        Tramo(estado=Estado.EN_MOVIMIENTO, inicio=hora(10, 0, 5), fin=hora(10, 0, 20)),
    )


def test_importe_5s_parada_15s_movimiento_son_0_85() -> None:
    importe = calcular_importe(_tramos_cerrados(), TARIFA_EMT)

    assert importe == Money(centimos=85)
    assert importe.formato() == "0,85 €"


def test_importe_en_curso_deriva_con_hasta() -> None:
    tramos = (
        Tramo(estado=Estado.PARADA, inicio=hora(10), fin=hora(10, 0, 5)),
        Tramo(estado=Estado.EN_MOVIMIENTO, inicio=hora(10, 0, 5)),
    )

    importe = calcular_importe(tramos, TARIFA_EMT, hasta=hora(10, 0, 20))

    assert importe == Money(centimos=85)  # 0,02 × 5 + 0,05 × 15, tramo abierto


def test_redondeo_unico_half_up() -> None:
    tramos = (Tramo(estado=Estado.PARADA, inicio=hora(10), fin=hora(10, 0, 0, 625000)),)

    # 0.625 s × 2 c/s = 1.25 c: se redondea UNA vez al final, 1.25 → 1
    assert calcular_importe(tramos, TARIFA_EMT) == Money(centimos=1)


def test_las_tarifas_vigentes_se_cargan_del_fichero_de_config() -> None:
    assert cargar_tarifa() == Tarifa(
        parada_centimos_por_segundo=2, movimiento_centimos_por_segundo=5
    )
