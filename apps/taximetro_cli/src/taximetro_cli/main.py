"""REPL del taxímetro: sesión de comandos con la línea de estado siempre visible."""

import json
import sys
import threading
import time
from pathlib import Path

import typer
from rich.live import Live
from rich.text import Text
from taximetro import (
    Estado,
    EventBus,
    ServicioTaximetro,
    TaximetroError,
    cargar_tarifa,
)

TEXTOS = json.loads((Path(__file__).parent / "textos.json").read_text(encoding="utf-8"))

_ETIQUETAS = {
    Estado.PARADA: "parada",
    Estado.EN_MOVIMIENTO: "en_movimiento",
}
_ESTADOS_POR_PALABRA = {
    "parada": Estado.PARADA,
    "movimiento": Estado.EN_MOVIMIENTO,
}


def t(clave: str, **valores: str) -> str:
    """Traduce una clave de textos.json; interpola valores si los hay."""
    texto = str(TEXTOS.get(clave, clave))
    return texto.format(**valores) if valores else texto


class RelojMonotono:
    """Reloj real del sistema: monotónico, inmune a saltos del reloj de pared."""

    def __call__(self) -> float:
        return time.monotonic()


def crear_servicio(reloj) -> ServicioTaximetro:
    """Composition root: tarifas del fichero de config y eventos al EventBus."""
    return ServicioTaximetro(
        tarifa=cargar_tarifa(), reloj=reloj, publicar=EventBus().publicar
    )


def linea_estado(servicio: ServicioTaximetro) -> str:
    """Línea siempre visible: libre, o Estado + Importe derivado al instante."""
    if not servicio.en_carrera:
        return t("linea_libre")
    estado = servicio.estado
    assert estado is not None
    return t(
        "linea_en_carrera",
        estado=t(_ETIQUETAS[estado]),
        importe=servicio.importe.formato(),
    )


def ejecutar_comando(servicio: ServicioTaximetro, comando: str) -> None:
    verbo, _, resto = comando.partition(" ")
    try:
        if verbo == "iniciar" and not resto:
            servicio.iniciar()
            typer.echo(t("carrera_iniciada"))
        elif verbo == "estado" and not resto:
            typer.echo(linea_estado(servicio))
        elif verbo == "estado" and resto in _ESTADOS_POR_PALABRA:
            servicio.cambiar_estado(_ESTADOS_POR_PALABRA[resto])
        elif verbo == "finalizar" and not resto:
            typer.echo(t("carrera_finalizada", importe=servicio.finalizar().formato()))
        else:
            typer.echo(t("comando_desconocido"))
    except TaximetroError as error:
        typer.echo(str(error))


def bucle(servicio: ServicioTaximetro) -> None:
    """Bucle de comandos: la línea de estado se pinta antes de cada lectura."""
    while True:
        typer.echo(linea_estado(servicio))
        try:
            comando = input("> ").strip().lower()
        except EOFError:
            return
        if comando == "salir":
            return
        if comando:
            ejecutar_comando(servicio, comando)


def sesion(reloj) -> None:
    """Arranca el turno; en terminal interactiva la línea se refresca sola."""
    servicio = crear_servicio(reloj)
    if not sys.stdout.isatty():
        bucle(servicio)
        return
    parar = threading.Event()

    def refrescar(live: Live) -> None:
        while not parar.wait(1.0):
            live.update(Text(linea_estado(servicio)))

    with Live(Text(linea_estado(servicio)), refresh_per_second=1) as live:
        hilo = threading.Thread(target=refrescar, args=(live,), daemon=True)
        hilo.start()
        try:
            bucle(servicio)
        finally:
            parar.set()


def crear_app(reloj) -> typer.Typer:
    """App Typer con el reloj inyectado (los tests pasan uno falso)."""
    app = typer.Typer(help=t("banner"), invoke_without_command=True)

    @app.callback()
    def sesion_interactiva() -> None:
        """Muestra el banner, las instrucciones y arranca la sesión interactiva."""
        typer.echo(t("banner"))
        typer.echo(t("instrucciones"))
        sesion(reloj)

    return app


app = crear_app(RelojMonotono())


def main() -> None:
    """Ejecuta la aplicación del CLI."""
    app()
