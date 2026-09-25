"""Borde del CLI: iniciar la Carrera en parada, reloj inyectado (spec #14, #16)."""

from cli.main import crear_app
from typer.testing import CliRunner


class RelojFalso:
    """Doble de prueba: devuelve instantes guiñados uno a uno (reloj inyectado)."""

    def __init__(self, instantes: list[float]) -> None:
        self._instantes = instantes
        self._indice = 0

    def ahora(self) -> float:
        instante = self._instantes[min(self._indice, len(self._instantes) - 1)]
        self._indice += 1
        return instante


runner = CliRunner()


def test_iniciar_arranca_la_carrera_en_parada_con_importe_0_00() -> None:
    app = crear_app(RelojFalso([0.0, 0.0, 0.0]))

    resultado = runner.invoke(app, [], input="iniciar\nsalir\n")

    assert resultado.exit_code == 0
    assert "Carrera iniciada" in resultado.output
    assert "parada" in resultado.output
    assert "0,00 €" in resultado.output


def test_tras_10_segundos_en_parada_el_importe_es_0_20() -> None:
    app = crear_app(RelojFalso([0.0, 0.0, 10.0, 10.0]))

    resultado = runner.invoke(app, [], input="iniciar\nestado\nsalir\n")

    assert resultado.exit_code == 0
    assert "0,00 €" in resultado.output  # el Importe parte de cero al iniciar
    assert "0,20 €" in resultado.output  # el refresco muestra exactamente 0,02 × 10
