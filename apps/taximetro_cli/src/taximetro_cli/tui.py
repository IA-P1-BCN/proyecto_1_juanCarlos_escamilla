"""TUI del taxímetro: el puesto del conductor a pantalla completa (Textual)."""

from taximetro import Estado, ServicioTaximetro, TaximetroError
from textual.app import App, ComposeResult
from textual.widgets import Digits, Footer, Header, Static

from taximetro_cli.main import RelojMonotono, crear_servicio, t


class TaximetroApp(App[None]):
    """Contador grande, badge de Estado y teclas 1/2/3/q — sobre ServicioTaximetro."""

    TITLE = t("banner")
    SUB_TITLE = "TaxiTech Solutions · TTX-247"

    BINDINGS = [
        ("1", "iniciar", "Iniciar carrera"),
        ("2", "cambiar_estado", "Cambiar estado"),
        ("3", "finalizar", "Finalizar"),
        ("q", "quit", "Salir"),
    ]

    CSS = """
    #hero { width: 100%; content-align: center middle; }
    #contador { width: 100%; content-align: center middle; }
    #estado { width: 100%; content-align: center middle; text-style: bold; }
    #estado.movimiento { background: $success; text-style: bold blink; }
    """

    def __init__(self, servicio: ServicioTaximetro) -> None:
        super().__init__()
        self.servicio = servicio

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("🚕", id="hero")
        yield Digits("0.00", id="contador")
        yield Static(t("estado_inicial"), id="estado")
        yield Footer()

    def on_mount(self) -> None:
        self.set_interval(1.0, self.refrescar)
        self.refrescar()

    def refrescar(self) -> None:
        """Actualiza contador y badge; el Importe se deriva con el reloj inyectado."""
        contador = self.query_one("#contador", Digits)
        badge = self.query_one("#estado", Static)
        if not self.servicio.en_carrera:
            contador.update("0.00")
            badge.update(t("estado_inicial"))
            badge.remove_class("movimiento")
            return
        euros = self.servicio.importe.centimos / 100
        contador.update(f"{euros:.2f}")
        if self.servicio.estado is Estado.EN_MOVIMIENTO:
            badge.update(t("badge_movimiento"))
            badge.add_class("movimiento")
        else:
            badge.update(t("badge_parada"))
            badge.remove_class("movimiento")

    def action_iniciar(self) -> None:
        try:
            self.servicio.iniciar()
        except TaximetroError as error:
            self.notify(f"⚠ {error}", severity="error")
            return
        self.bell()
        self.notify(t("tui_carrera_iniciada"), title=t("tui_titulo"))
        self.refrescar()

    def action_cambiar_estado(self) -> None:
        objetivo = (
            Estado.EN_MOVIMIENTO
            if self.servicio.estado is Estado.PARADA
            else Estado.PARADA
        )
        try:
            self.servicio.cambiar_estado(objetivo)
        except TaximetroError as error:
            self.notify(f"⚠ {error}", severity="error")
            return
        self.bell()
        self.refrescar()

    def action_finalizar(self) -> None:
        try:
            importe = self.servicio.finalizar()
        except TaximetroError as error:
            self.notify(f"⚠ {error}", severity="error")
            return
        self.bell()
        self.notify(
            t("tui_carrera_finalizada", importe=importe.formato()),
            title=t("tui_carrera_finalizada_titulo"),
        )
        self.refrescar()


def crear_tui(reloj) -> TaximetroApp:
    """Composition root de la TUI con el reloj inyectado (los tests pasan uno falso)."""
    return TaximetroApp(crear_servicio(reloj))


def main() -> None:
    """Ejecuta la TUI a pantalla completa."""
    crear_tui(RelojMonotono()).run()
