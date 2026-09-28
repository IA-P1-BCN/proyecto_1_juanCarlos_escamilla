"""La Carrera avanza por tramos — aggregate del contexto ride (spec #14, #16–#19)."""

from datetime import UTC, datetime

import pytest
from taximetro_kernel import Estado, Tramo
from taximetro_ride import Carrera, CarreraYaFinalizadaError


def hora(h: int, m: int = 0, s: int = 0) -> datetime:
    return datetime(2026, 9, 28, h, m, s, tzinfo=UTC)


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
