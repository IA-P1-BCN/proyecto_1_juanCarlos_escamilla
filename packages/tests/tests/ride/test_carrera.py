"""La Carrera cambia de Estado sin perder el acumulado — aggregate de ride (#17)."""

from ride import Carrera, CarreraIniciada, EstadoCambiado
from shared_kernel import Estado, Money
from shared_libs import EventBus


def _carrera_con_captor() -> tuple[Carrera, list[object]]:
    bus = EventBus()
    eventos: list[object] = []
    bus.suscribir(CarreraIniciada, eventos.append)
    bus.suscribir(EstadoCambiado, eventos.append)
    return Carrera(publicador=bus), eventos


def _carrera_en_marcha() -> tuple[Carrera, list[object]]:
    carrera, eventos = _carrera_con_captor()
    carrera.iniciar(ahora=0.0)
    return carrera, eventos


def test_cambiar_estado_a_en_movimiento() -> None:
    carrera, _ = _carrera_en_marcha()

    carrera.cambiar_estado(Estado.EN_MOVIMIENTO, ahora=10.0)

    assert carrera.estado is Estado.EN_MOVIMIENTO


def test_cambiar_estado_no_reinicia_el_importe() -> None:
    carrera, _ = _carrera_en_marcha()
    carrera.acumular(Money(centimos=10))

    carrera.cambiar_estado(Estado.EN_MOVIMIENTO, ahora=10.0)

    assert carrera.importe == Money(centimos=10)


def test_cambiar_estado_emite_estado_cambiado() -> None:
    carrera, eventos = _carrera_en_marcha()

    carrera.cambiar_estado(Estado.EN_MOVIMIENTO, ahora=10.0)

    cambios = [e for e in eventos if isinstance(e, EstadoCambiado)]
    assert len(cambios) == 1
    assert cambios[0].momento == 10.0
    assert cambios[0].estado is Estado.EN_MOVIMIENTO
