"""Borde del REPL: el turno completo con reloj inyectado (spec #14, #16–#19, #5)."""

from datetime import UTC, datetime
from pathlib import Path

from taximetro import BitacoraJSON, HistoricoJson
from taximetro_cli.main import crear_app
from taximetro_log import leer
from typer.testing import CliRunner


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


runner = CliRunner()


def test_al_arrancar_muestra_banner_e_instrucciones() -> None:
    resultado = runner.invoke(crear_app(RelojFalso([])), [], input="salir\n")

    assert resultado.exit_code == 0
    assert "🚕" in resultado.output
    assert "Bienvenido" in resultado.output
    assert "iniciar" in resultado.output
    assert "estado" in resultado.output
    assert "finalizar" in resultado.output
    assert "historial" in resultado.output


def test_iniciar_arranca_en_parada_desde_0_00() -> None:
    resultado = runner.invoke(
        crear_app(RelojFalso([hora(10), hora(10)])), [], input="iniciar\nsalir\n"
    )

    assert "Carrera iniciada" in resultado.output
    assert "parada" in resultado.output
    assert "0,00 €" in resultado.output


def test_5s_parada_y_15s_movimiento_son_0_85() -> None:
    reloj = RelojFalso(
        [
            hora(10),
            hora(10),
            hora(10, 0, 5),
            hora(10, 0, 20),
            hora(10, 0, 20),
            hora(10, 0, 20),
        ]
    )
    resultado = runner.invoke(
        crear_app(reloj), [], input="iniciar\nestado movimiento\nestado\nsalir\n"
    )

    assert "0,00 €" in resultado.output  # el Importe parte de cero
    assert "en_movimiento" in resultado.output
    assert "0,85 €" in resultado.output  # 0,02 × 5 + 0,05 × 15


def test_finalizar_muestra_el_total_y_vuelve_a_libre() -> None:
    reloj = RelojFalso(
        [hora(10), hora(10), hora(10, 0, 5), hora(10, 0, 20), hora(10, 0, 20)]
    )
    resultado = runner.invoke(
        crear_app(reloj), [], input="iniciar\nestado movimiento\nfinalizar\nsalir\n"
    )

    assert "Carrera finalizada. Importe total: 0,85 €" in resultado.output
    assert resultado.output.count("libre") >= 2  # al arrancar y tras finalizar


def test_encadena_carreras_en_la_misma_sesion() -> None:
    reloj = RelojFalso(
        [
            hora(10),
            hora(10),
            hora(10, 0, 10),
            hora(10, 0, 10),
            hora(10, 0, 10),
            hora(10, 0, 10),
        ]
    )
    resultado = runner.invoke(
        crear_app(reloj), [], input="iniciar\nfinalizar\niniciar\nfinalizar\nsalir\n"
    )

    assert "Importe total: 0,20 €" in resultado.output
    assert "Importe total: 0,00 €" in resultado.output


def test_finalizar_sin_carrera_avisa() -> None:
    resultado = runner.invoke(crear_app(RelojFalso([])), [], input="finalizar\nsalir\n")

    assert "No hay Carrera en curso" in resultado.output


def test_iniciar_con_carrera_en_curso_avisa() -> None:
    resultado = runner.invoke(
        crear_app(RelojFalso([hora(10), hora(10)])),
        [],
        input="iniciar\niniciar\nsalir\n",
    )

    assert "Ya hay una Carrera en curso" in resultado.output


def test_historial_muestra_las_carreras_del_dia_y_el_total(tmp_path: Path) -> None:
    historico = HistoricoJson(tmp_path / "historico.json")
    resultado = runner.invoke(
        crear_app(
            RelojFalso([hora(10), hora(10), hora(10, 0, 20)]), historico=historico
        ),
        [],
        input="iniciar\nfinalizar\nhistorial 2026-09-28\nsalir\n",
    )

    assert "Histórico · 28/09/2026" in resultado.output
    assert "00:00:20" in resultado.output  # la duración de la Carrera
    assert "0,40 €" in resultado.output  # 20 s en parada
    assert "1 carreras · 0,40 € totales" in resultado.output


def test_historial_de_un_dia_sin_carreras_avisa(tmp_path: Path) -> None:
    historico = HistoricoJson(tmp_path / "historico.json")
    resultado = runner.invoke(
        crear_app(RelojFalso([]), historico=historico),
        [],
        input="historial 2026-01-01\nsalir\n",
    )

    assert "Sin carreras finalizadas el 01/01/2026" in resultado.output


def test_historial_con_dia_mal_formado_avisa(tmp_path: Path) -> None:
    resultado = runner.invoke(
        crear_app(RelojFalso([]), historico=HistoricoJson(tmp_path / "h.json")),
        [],
        input="historial 28-09-2026\nsalir\n",
    )

    assert "Formato de día inválido" in resultado.output


def test_el_arranque_y_los_errores_quedan_en_la_bitacora(tmp_path: Path) -> None:
    ruta_bitacora = tmp_path / "taximetro.log"
    bitacora = BitacoraJSON(ruta_bitacora)

    runner.invoke(
        crear_app(RelojFalso([]), bitacora=bitacora), [], input="finalizar\nsalir\n"
    )

    eventos = leer(ruta_bitacora)
    assert eventos[0]["evento"] == "arranque"
    assert eventos[-1]["evento"] == "error"
    assert "No hay Carrera en curso" in eventos[-1]["mensaje"]
