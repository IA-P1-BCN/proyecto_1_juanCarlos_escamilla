"""REPL del taxímetro: sesión de comandos con la línea de estado siempre visible."""

import json
import sys
import threading
from datetime import UTC, date, datetime
from pathlib import Path

import typer
from rich.live import Live
from rich.text import Text
from taximetro import (
    BitacoraJSON,
    Estado,
    EventBus,
    HistoricoJson,
    Money,
    ServicioTaximetro,
    TaximetroError,
    cargar_tarifa,
    registrar_eventos,
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


class RelojReal:
    """Reloj de pared del sistema: fechas reales para la Carrera y el histórico."""

    def __call__(self) -> datetime:
        return datetime.now(UTC)


def crear_servicio(
    reloj, historico: HistoricoJson | None = None, bitacora: BitacoraJSON | None = None
) -> ServicioTaximetro:
    """Composition root: tarifas, bus con bitácora suscrita e histórico en JSON."""
    bitacora = bitacora or BitacoraJSON()
    bus = EventBus()
    registrar_eventos(bus, bitacora)
    bitacora.registrar("arranque")
    return ServicioTaximetro(
        tarifa=cargar_tarifa(),
        reloj=reloj,
        publicar=bus.publicar,
        historico=historico or HistoricoJson(),
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


def _duracion(segundos: float) -> str:
    total = int(segundos)
    horas, resto = divmod(total, 3600)
    minutos, segundos = divmod(resto, 60)
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"


def _mostrar_historial(servicio: ServicioTaximetro, dia: date) -> None:
    registros = servicio.historial_del_dia(dia)
    dia_texto = dia.strftime("%d/%m/%Y")
    if not registros:
        typer.echo(t("historial_vacio", dia=dia_texto))
        return
    typer.echo(t("historial_titulo", dia=dia_texto))
    typer.echo(t("historial_cabecera"))
    for registro in registros:
        typer.echo(
            f"{registro.inicio.astimezone():%d/%m %H:%M}   "
            f"{_duracion(registro.duracion_segundos)}   {registro.importe.formato()}"
        )
    total = Money(centimos=sum(r.importe.centimos for r in registros))
    typer.echo(t("historial_pie", n=str(len(registros)), total=total.formato()))


def _parsear_dia(texto: str) -> date | None:
    if not texto:
        return date.today()
    try:
        return date.fromisoformat(texto)
    except ValueError:
        return None


def ejecutar_comando(
    servicio: ServicioTaximetro, comando: str, bitacora: BitacoraJSON
) -> None:
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
        elif verbo == "historial":
            dia = _parsear_dia(resto.strip())
            if dia is None:
                typer.echo(t("historial_dia_invalido"))
            else:
                _mostrar_historial(servicio, dia)
                bitacora.registrar("historial_consultado", dia=dia.isoformat())
        else:
            typer.echo(t("comando_desconocido"))
    except TaximetroError as error:
        bitacora.registrar("error", mensaje=str(error))
        typer.echo(str(error))


def bucle(servicio: ServicioTaximetro, bitacora: BitacoraJSON) -> None:
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
            ejecutar_comando(servicio, comando, bitacora)


def sesion(
    reloj, historico: HistoricoJson | None = None, bitacora: BitacoraJSON | None = None
) -> None:
    """Arranca el turno; en terminal interactiva la línea se refresca sola."""
    bitacora = bitacora or BitacoraJSON()
    servicio = crear_servicio(reloj, historico, bitacora)
    if not sys.stdout.isatty():
        bucle(servicio, bitacora)
        return
    parar = threading.Event()

    def refrescar(live: Live) -> None:
        while not parar.wait(1.0):
            live.update(Text(linea_estado(servicio)))

    with Live(Text(linea_estado(servicio)), refresh_per_second=1) as live:
        hilo = threading.Thread(target=refrescar, args=(live,), daemon=True)
        hilo.start()
        try:
            bucle(servicio, bitacora)
        finally:
            parar.set()


def crear_app(
    reloj, historico: HistoricoJson | None = None, bitacora: BitacoraJSON | None = None
) -> typer.Typer:
    """App Typer con el reloj inyectado (los tests pasan uno falso)."""
    app = typer.Typer(help=t("banner"), invoke_without_command=True)

    @app.callback()
    def sesion_interactiva() -> None:
        """Muestra el banner, las instrucciones y arranca la sesión interactiva."""
        typer.echo(t("banner"))
        typer.echo(t("instrucciones"))
        sesion(reloj, historico, bitacora)

    return app


app = crear_app(RelojReal())


def main() -> None:
    """Ejecuta la aplicación del CLI."""
    app()
