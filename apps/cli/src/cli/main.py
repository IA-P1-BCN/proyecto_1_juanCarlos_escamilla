"""Punto de entrada del CLI del taxímetro."""

import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import i18n
import typer
from pricing import MotorDeTarifas
from rich.live import Live
from rich.text import Text
from ride import Carrera
from shared_libs import EventBus

_BANNER = "taximetro.banner"
_INSTRUCCIONES = "taximetro.instrucciones"
_LIBRE = "taximetro.libre"
_SIN_CARRERA = "taximetro.sin_carrera"
_PARADA = "taximetro.parada"
_CARRERA_INICIADA = "taximetro.carrera_iniciada"
_COMANDO_DESCONOCIDO = "taximetro.comando_desconocido"
_PROMPT = "> "


class Reloj(Protocol):
    """Fuente de tiempo inyectable: el dominio nunca consulta el reloj por sí solo."""

    def ahora(self) -> float: ...


class RelojMonotono:
    """Reloj real del sistema: monotónico, inmune a saltos del reloj de pared."""

    def ahora(self) -> float:
        return time.monotonic()


def configurar_i18n() -> None:
    """Carga los locales del paquete y fija el idioma principal (español)."""
    i18n.load_path.append(str(Path(__file__).parent / "locales"))
    i18n.set("filename_format", "{locale}.{format}")
    i18n.set("locale", "es")


configurar_i18n()


@dataclass
class Sesion:
    """Estado del turno: la Carrera activa y desde cuándo corre el contador."""

    motor: MotorDeTarifas
    bus: EventBus
    carrera: Carrera | None = None
    ultimo_instante: float = 0.0


def linea_estado(sesion: Sesion, reloj: Reloj) -> str:
    """Línea de estado del taxista: siempre visible, refrescada con el reloj."""
    if sesion.carrera is None:
        return f"🚕 {i18n.t(_LIBRE)} · {i18n.t(_SIN_CARRERA)}"
    ahora = reloj.ahora()
    transcurrido = ahora - sesion.ultimo_instante
    if transcurrido > 0:
        sesion.carrera.acumular(sesion.motor.importe_en_parada(transcurrido))
        sesion.ultimo_instante = ahora
    return f"🚕 {i18n.t(_PARADA)} · {sesion.carrera.importe.formato()}"


def iniciar_carrera(sesion: Sesion, reloj: Reloj) -> None:
    ahora = reloj.ahora()
    sesion.carrera = Carrera(publicador=sesion.bus)
    sesion.carrera.iniciar(ahora=ahora)
    sesion.ultimo_instante = ahora
    typer.echo(i18n.t(_CARRERA_INICIADA))


def leer_comando() -> str | None:
    """Lee un comando del taxista; None significa fin de sesión (salir o EOF)."""
    try:
        comando = input(_PROMPT).strip().lower()
    except EOFError:
        return None
    return comando or None


def bucle_sesion(sesion: Sesion, reloj: Reloj) -> None:
    """Bucle de comandos: la línea de estado se pinta antes de cada lectura."""
    while True:
        typer.echo(linea_estado(sesion, reloj))
        comando = leer_comando()
        if comando is None or comando == "salir":
            return
        if comando == "iniciar":
            iniciar_carrera(sesion, reloj)
        elif comando == "estado":
            typer.echo(linea_estado(sesion, reloj))
        else:
            typer.echo(i18n.t(_COMANDO_DESCONOCIDO))


def ejecutar_sesion(reloj: Reloj) -> None:
    sesion = Sesion(motor=MotorDeTarifas(), bus=EventBus())
    if sys.stdout.isatty():
        bucle_con_ticker(sesion, reloj)
    else:
        bucle_sesion(sesion, reloj)


def bucle_con_ticker(sesion: Sesion, reloj: Reloj) -> None:
    """Sesión interactiva: la línea de estado se refresca sola cada segundo."""
    parar = threading.Event()

    def refrescar(live: Live) -> None:
        while not parar.wait(1.0):
            live.update(Text(linea_estado(sesion, reloj)))

    with Live(Text(linea_estado(sesion, reloj)), refresh_per_second=1) as live:
        hilo = threading.Thread(target=refrescar, args=(live,), daemon=True)
        hilo.start()
        try:
            bucle_sesion(sesion, reloj)
        finally:
            parar.set()


def crear_app(reloj: Reloj) -> typer.Typer:
    """Composition root: inyecta el reloj y devuelve la app lista para ejecutar."""
    app = typer.Typer(help=i18n.t(_BANNER), invoke_without_command=True)

    @app.callback()
    def sesion_interactiva() -> None:
        """Muestra el banner, las instrucciones y arranca la sesión interactiva."""
        typer.echo(i18n.t(_BANNER))
        typer.echo(i18n.t(_INSTRUCCIONES))
        ejecutar_sesion(reloj)

    return app


app = crear_app(RelojMonotono())


def main() -> None:
    """Ejecuta la aplicación del CLI."""
    app()
