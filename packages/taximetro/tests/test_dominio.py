"""Dominio: Carrera por tramos, Tarifa y cálculo del Importe (spec #14, #16–#18)."""

from datetime import UTC, datetime

import pytest
from taximetro import (
    Carrera,
    CarreraYaFinalizadaError,
    Estado,
    Tarifa,
    Tramo,
    calcular_importe,
)
from taximetro.domain.dinero import Money

TARIFA_EMT = Tarifa(parada_centimos_por_segundo=2, movimiento_centimos_por_segundo=5)


def hora(h: int, m: int = 0, s: int = 0, ms: int = 0) -> datetime:
    return datetime(2026, 9, 28, h, m, s, ms, tzinfo=UTC)


def test_la_carrera_nace_en_parada_con_un_tramo_abierto() -> None:
    carrera = Carrera(publicar=lambda evento: None)

    carrera.iniciar(ahora=hora(10))

    assert carrera.estado is Estado.PARADA
    assert carrera.tramos == (Tramo(estado=Estado.PARADA, inicio=hora(10)),)


def test_cambiar_estado_cierra_el_tramo_y_abre_otro() -> None:
    carrera = Carrera(publicar=lambda evento: None)
    carrera.iniciar(ahora=hora(10))

    carrera.cambiar_estado(Estado.EN_MOVIMIENTO, ahora=hora(10, 0, 5))

    assert carrera.estado is Estado.EN_MOVIMIENTO
    assert carrera.tramos == (
        Tramo(estado=Estado.PARADA, inicio=hora(10), fin=hora(10, 0, 5)),
        Tramo(estado=Estado.EN_MOVIMIENTO, inicio=hora(10, 0, 5)),
    )


def test_repetir_el_estado_actual_no_abre_tramo() -> None:
    carrera = Carrera(publicar=lambda evento: None)
    carrera.iniciar(ahora=hora(10))

    carrera.cambiar_estado(Estado.PARADA, ahora=hora(10, 0, 3))

    assert len(carrera.tramos) == 1


def test_finalizar_cierra_el_ultimo_tramo_y_bloquea_la_carrera() -> None:
    carrera = Carrera(publicar=lambda evento: None)
    carrera.iniciar(ahora=hora(10))

    carrera.finalizar(ahora=hora(10, 0, 10))

    assert carrera.tramos[-1].fin == hora(10, 0, 10)

    with pytest.raises(CarreraYaFinalizadaError):
        carrera.cambiar_estado(Estado.EN_MOVIMIENTO, ahora=hora(10, 0, 12))


def test_importe_5s_parada_15s_movimiento_son_0_85() -> None:
    carrera = Carrera(publicar=lambda evento: None)
    carrera.iniciar(ahora=hora(10))
    carrera.cambiar_estado(Estado.EN_MOVIMIENTO, ahora=hora(10, 0, 5))
    carrera.finalizar(ahora=hora(10, 0, 20))

    importe = calcular_importe(carrera.tramos, TARIFA_EMT)

    assert importe == Money(centimos=85)
    assert importe.formato() == "0,85 €"


def test_importe_en_curso_deriva_con_hasta() -> None:
    carrera = Carrera(publicar=lambda evento: None)
    carrera.iniciar(ahora=hora(10))
    carrera.cambiar_estado(Estado.EN_MOVIMIENTO, ahora=hora(10, 0, 5))

    importe = calcular_importe(carrera.tramos, TARIFA_EMT, hasta=hora(10, 0, 20))

    assert importe == Money(centimos=85)  # 0,02 × 5 + 0,05 × 15, sin cerrar la Carrera


def test_redondeo_unico_half_up() -> None:
    carrera = Carrera(publicar=lambda evento: None)
    carrera.iniciar(ahora=hora(10))
    carrera.finalizar(ahora=hora(10, 0, 0, 625000))

    # 0.625 s × 2 c/s = 1.25 c: se redondea UNA vez al final, 1.25 → 1
    assert calcular_importe(carrera.tramos, TARIFA_EMT) == Money(centimos=1)
