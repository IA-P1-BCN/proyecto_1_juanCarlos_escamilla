"""Histórico: carreras finalizadas persistidas y consultables por día (#5, US-05)."""

from datetime import UTC, date, datetime
from pathlib import Path

from taximetro import (
    CarreraRegistro,
    HistoricoJson,
    Money,
    ServicioTaximetro,
    Tarifa,
)

TARIFA_EMT = Tarifa(parada_centimos_por_segundo=2, movimiento_centimos_por_segundo=5)


def hora(dia: int, h: int, m: int = 0, s: int = 0) -> datetime:
    return datetime(2026, 9, dia, h, m, s, tzinfo=UTC)


class RelojFalso:
    """Doble de prueba: devuelve instantes guiñados uno a uno (reloj inyectado)."""

    def __init__(self, instantes: list[datetime]) -> None:
        self._instantes = instantes
        self._indice = 0

    def __call__(self) -> datetime:
        instante = self._instantes[min(self._indice, len(self._instantes) - 1)]
        self._indice += 1
        return instante


def test_el_json_persiste_y_recupera_en_una_sesion_nueva(tmp_path: Path) -> None:
    ruta = tmp_path / "historico.json"
    registro = CarreraRegistro(
        inicio=hora(28, 10), duracion_segundos=120.0, importe=Money(centimos=240)
    )

    HistoricoJson(ruta).guardar(registro)
    recuperado = HistoricoJson(ruta).del_dia(date(2026, 9, 28))  # sesión posterior

    assert recuperado == [registro]


def test_del_dia_filtra_solo_las_carreras_de_ese_dia(tmp_path: Path) -> None:
    historico = HistoricoJson(tmp_path / "historico.json")
    del_27 = CarreraRegistro(
        inicio=hora(27, 10), duracion_segundos=60.0, importe=Money(centimos=120)
    )
    del_28 = CarreraRegistro(
        inicio=hora(28, 18), duracion_segundos=30.0, importe=Money(centimos=60)
    )

    historico.guardar(del_27)
    historico.guardar(del_28)

    assert historico.del_dia(date(2026, 9, 28)) == [del_28]


def test_finalizar_guarda_fecha_duracion_e_importe(tmp_path: Path) -> None:
    historico = HistoricoJson(tmp_path / "historico.json")
    servicio = ServicioTaximetro(
        tarifa=TARIFA_EMT,
        reloj=RelojFalso([hora(28, 10), hora(28, 10, 0, 20)]),
        publicar=lambda evento: None,
        historico=historico,
    )

    servicio.iniciar()
    total = servicio.finalizar()

    registros = historico.del_dia(date(2026, 9, 28))
    assert len(registros) == 1
    assert registros[0] == CarreraRegistro(
        inicio=hora(28, 10), duracion_segundos=20.0, importe=total
    )
