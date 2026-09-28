"""Los eventos de dominio aterrizan en la bitácora — wiring de la aplicación (#6)."""

from datetime import UTC, datetime
from pathlib import Path

from taximetro import Estado, EventBus, ServicioTaximetro, Tarifa, registrar_eventos
from taximetro_log import BitacoraJSON, leer

TARIFA_EMT = Tarifa(parada_centimos_por_segundo=2, movimiento_centimos_por_segundo=5)


def hora(h: int, m: int = 0, s: int = 0) -> datetime:
    return datetime(2026, 9, 28, h, m, s, tzinfo=UTC)


class RelojFalso:
    """Doble de prueba: devuelve instantes guiñados uno a uno (reloj inyectado)."""

    def __init__(self, instantes: list[datetime]) -> None:
        self._instantes = instantes
        self._indice = 0

    def __call__(self) -> datetime:
        instante = self._instantes[min(self._indice, len(self._instantes) - 1)]
        self._indice += 1
        return instante


def test_el_turno_completo_queda_en_la_bitacora(tmp_path: Path) -> None:
    ruta = tmp_path / "taximetro.log"
    bitacora = BitacoraJSON(ruta)
    bus = EventBus()
    registrar_eventos(bus, bitacora)
    servicio = ServicioTaximetro(
        tarifa=TARIFA_EMT,
        reloj=RelojFalso([hora(10), hora(10, 0, 5), hora(10, 0, 20)]),
        publicar=bus.publicar,
    )

    servicio.iniciar()
    servicio.cambiar_estado(Estado.EN_MOVIMIENTO)
    servicio.finalizar()

    eventos = leer(ruta)
    assert [e["evento"] for e in eventos] == [
        "carrera_iniciada",
        "estado_cambiado",
        "carrera_finalizada",
    ]
    assert eventos[1]["estado"] == "en_movimiento"
    assert eventos[0]["momento"] == hora(10).isoformat()
