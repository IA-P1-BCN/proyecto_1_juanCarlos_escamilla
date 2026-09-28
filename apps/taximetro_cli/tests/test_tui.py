"""TUI (Textual): el puesto del conductor con reloj inyectado (spec #14, #16–#19)."""

from datetime import UTC, datetime

from taximetro import Estado
from taximetro_cli.interfaces.tui import crear_tui
from textual.widgets import Digits, Static


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


async def test_el_puesto_del_conductor_arranca_libre() -> None:
    app = crear_tui(RelojFalso([]))
    async with app.run_test() as pilot:
        await pilot.pause()

        estado = app.query_one("#estado", Static)
        app.query_one("#contador", Digits)  # el contador grande existe
        assert "pulsa 1" in str(estado.render())


async def test_teclas_1_2_3_llevan_la_carrera_completa() -> None:
    app = crear_tui(
        RelojFalso(
            [hora(10), hora(10), hora(10, 0, 5), hora(10, 0, 20), hora(10, 0, 20)]
        )
    )
    async with app.run_test() as pilot:
        estado = app.query_one("#estado", Static)

        await pilot.press("1")
        await pilot.pause()
        assert app.servicio.en_carrera
        assert "PARADA" in str(estado.render())

        await pilot.press("2")
        await pilot.pause()
        assert app.servicio.estado is Estado.EN_MOVIMIENTO
        assert "EN_MOVIMIENTO" in str(estado.render())

        await pilot.press("3")
        await pilot.pause()
        assert not app.servicio.en_carrera
        assert "pulsa 1" in str(estado.render())


async def test_los_errores_no_tumban_la_pantalla() -> None:
    app = crear_tui(RelojFalso([]))
    async with app.run_test() as pilot:
        await pilot.press("3")  # finalizar sin Carrera
        await pilot.press("2")  # cambiar estado sin Carrera
        await pilot.pause()

        assert "pulsa 1" in str(app.query_one("#estado", Static).render())
