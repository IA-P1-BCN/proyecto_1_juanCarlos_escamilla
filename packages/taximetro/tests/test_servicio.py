"""ServicioTaximetro: el turno del taxista con reloj inyectado (spec #14, #17–#19)."""

import pytest
from taximetro import (
    CarreraFinalizada,
    CarreraIniciada,
    Estado,
    EstadoCambiado,
    EventBus,
    ServicioTaximetro,
    Tarifa,
    cargar_tarifa,
)


class RelojFalso:
    """Doble de prueba: devuelve instantes guiñados uno a uno (reloj inyectado)."""

    def __init__(self, instantes: list[float]) -> None:
        self._instantes = instantes
        self._indice = 0

    def ahora(self) -> float:
        instante = self._instantes[min(self._indice, len(self._instantes) - 1)]
        self._indice += 1
        return instante


TARIFA_EMT = Tarifa(parada_centimos_por_segundo=2, movimiento_centimos_por_segundo=5)


def _servicio(instantes: list[float]) -> tuple[ServicioTaximetro, list[object]]:
    eventos: list[object] = []
    bus = EventBus()
    for tipo in (CarreraIniciada, EstadoCambiado, CarreraFinalizada):
        bus.suscribir(tipo, eventos.append)
    servicio = ServicioTaximetro(
        tarifa=TARIFA_EMT, reloj=RelojFalso(instantes).ahora, publicar=bus.publicar
    )
    return servicio, eventos


def test_iniciar_arranca_en_parada_desde_0_00() -> None:
    servicio, eventos = _servicio([0.0, 0.0])

    servicio.iniciar()

    assert servicio.en_carrera
    assert servicio.estado is Estado.PARADA
    assert servicio.importe.formato() == "0,00 €"
    assert len([e for e in eventos if isinstance(e, CarreraIniciada)]) == 1


def test_el_importe_corre_5s_parada_15s_movimiento() -> None:
    # iniciar@0 → cambiar@5 → lectura en curso con hasta=20
    servicio, _ = _servicio([0.0, 5.0, 20.0])

    servicio.iniciar()
    servicio.cambiar_estado(Estado.EN_MOVIMIENTO)

    assert servicio.importe.formato() == "0,85 €"


def test_finalizar_devuelve_el_importe_total_y_emite_evento() -> None:
    servicio, eventos = _servicio([0.0, 5.0, 20.0])

    servicio.iniciar()
    servicio.cambiar_estado(Estado.EN_MOVIMIENTO)
    total = servicio.finalizar()

    assert total.formato() == "0,85 €"
    assert not servicio.en_carrera
    assert len([e for e in eventos if isinstance(e, CarreraFinalizada)]) == 1


def test_encadenar_segunda_carrera_arranca_de_cero() -> None:
    servicio, _ = _servicio([0.0, 10.0, 10.0, 10.0])

    servicio.iniciar()
    assert servicio.finalizar().formato() == "0,20 €"
    servicio.iniciar()

    assert servicio.importe.formato() == "0,00 €"


def test_finalizar_o_cambiar_sin_carrera_es_error() -> None:
    servicio, _ = _servicio([])

    with pytest.raises(Exception, match="No hay Carrera en curso"):
        servicio.finalizar()
    with pytest.raises(Exception, match="No hay Carrera en curso"):
        servicio.cambiar_estado(Estado.PARADA)


def test_iniciar_con_carrera_en_curso_es_error() -> None:
    servicio, _ = _servicio([0.0, 0.0])

    servicio.iniciar()

    with pytest.raises(Exception, match="Ya hay una Carrera en curso"):
        servicio.iniciar()


def test_las_tarifas_vigentes_se_cargan_del_fichero_de_config() -> None:
    assert cargar_tarifa() == Tarifa(
        parada_centimos_por_segundo=2, movimiento_centimos_por_segundo=5
    )
