"""Borde del REPL: el turno completo con reloj inyectado (spec #14, #16–#19)."""

from taximetro_cli.main import crear_app
from typer.testing import CliRunner


class RelojFalso:
    """Doble de prueba: devuelve instantes guiñados uno a uno (reloj inyectado)."""

    def __init__(self, instantes: list[float]) -> None:
        self._instantes = instantes
        self._indice = 0

    def __call__(self) -> float:
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


def test_iniciar_arranca_en_parada_desde_0_00() -> None:
    resultado = runner.invoke(
        crear_app(RelojFalso([0.0, 0.0])), [], input="iniciar\nsalir\n"
    )

    assert "Carrera iniciada" in resultado.output
    assert "parada" in resultado.output
    assert "0,00 €" in resultado.output


def test_5s_parada_y_15s_movimiento_son_0_85() -> None:
    resultado = runner.invoke(
        crear_app(RelojFalso([0.0, 0.0, 5.0, 20.0, 20.0, 20.0])),
        [],
        input="iniciar\nestado movimiento\nestado\nsalir\n",
    )

    assert "0,00 €" in resultado.output  # el Importe parte de cero
    assert "en_movimiento" in resultado.output
    assert "0,85 €" in resultado.output  # 0,02 × 5 + 0,05 × 15


def test_finalizar_muestra_el_total_y_vuelve_a_libre() -> None:
    resultado = runner.invoke(
        crear_app(RelojFalso([0.0, 0.0, 5.0, 20.0, 20.0])),
        [],
        input="iniciar\nestado movimiento\nfinalizar\nsalir\n",
    )

    assert "Carrera finalizada. Importe total: 0,85 €" in resultado.output
    assert resultado.output.count("libre") >= 2  # al arrancar y tras finalizar


def test_encadena_carreras_en_la_misma_sesion() -> None:
    resultado = runner.invoke(
        crear_app(RelojFalso([0.0, 0.0, 10.0, 10.0, 10.0, 10.0])),
        [],
        input="iniciar\nfinalizar\niniciar\nfinalizar\nsalir\n",
    )

    assert "Importe total: 0,20 €" in resultado.output
    assert "Importe total: 0,00 €" in resultado.output


def test_finalizar_sin_carrera_avisa() -> None:
    resultado = runner.invoke(crear_app(RelojFalso([])), [], input="finalizar\nsalir\n")

    assert "No hay Carrera en curso" in resultado.output


def test_iniciar_con_carrera_en_curso_avisa() -> None:
    resultado = runner.invoke(
        crear_app(RelojFalso([0.0, 0.0])), [], input="iniciar\niniciar\nsalir\n"
    )

    assert "Ya hay una Carrera en curso" in resultado.output
