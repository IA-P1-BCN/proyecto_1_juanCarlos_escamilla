"""Borde del CLI: cambiar Estado con reloj inyectado (spec #14, #17)."""

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


def test_5_segundos_en_parada_y_15_en_movimiento_son_0_85() -> None:
    # t1=5 s en parada (0,10 €) + t2=15 s en movimiento (0,75 €)
    app = crear_app(RelojFalso([0.0, 0.0, 5.0, 15.0, 20.0, 20.0]))

    resultado = runner.invoke(
        app, [], input="iniciar\nestado movimiento\nestado\nsalir\n"
    )

    assert resultado.exit_code == 0
    assert "0,00 €" in resultado.output  # el Importe parte de cero
    assert "en_movimiento" in resultado.output
    assert "0,85 €" in resultado.output  # 0,02 × 5 + 0,05 × 15


def test_estado_movimiento_sin_carrera_avisa_y_no_cambia_nada() -> None:
    app = crear_app(RelojFalso([0.0, 0.0]))

    resultado = runner.invoke(app, [], input="estado movimiento\nsalir\n")

    assert resultado.exit_code == 0
    assert "No hay Carrera en curso" in resultado.output
    assert "libre" in resultado.output
