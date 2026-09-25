"""La Carrera arranca en parada y anuncia su inicio — aggregate de ride (spec #14)."""

from ride import Carrera, CarreraIniciada
from shared_kernel import Estado, Money
from shared_libs import EventBus


def _carrera_con_captor() -> tuple[Carrera, list[CarreraIniciada]]:
    bus = EventBus()
    eventos: list[CarreraIniciada] = []
    bus.suscribir(CarreraIniciada, eventos.append)
    return Carrera(publicador=bus), eventos


def test_al_iniciar_la_carrera_arranca_en_parada() -> None:
    carrera, _ = _carrera_con_captor()

    carrera.iniciar(ahora=0.0)

    assert carrera.estado is Estado.PARADA
    assert carrera.importe == Money.cero()


def test_al_iniciar_emite_carrera_iniciada() -> None:
    carrera, eventos = _carrera_con_captor()

    carrera.iniciar(ahora=7.5)

    assert len(eventos) == 1
    assert isinstance(eventos[0], CarreraIniciada)
    assert eventos[0].momento == 7.5
