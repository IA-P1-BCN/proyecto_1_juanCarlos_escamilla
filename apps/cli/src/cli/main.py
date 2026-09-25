"""Punto de entrada del CLI del taxímetro."""

from pathlib import Path

import i18n
import typer

_BANNER = "taximetro.banner"
_INSTRUCCIONES = "taximetro.instrucciones"


def configurar_i18n() -> None:
    """Carga los locales del paquete y fija el idioma principal (español)."""
    i18n.load_path.append(str(Path(__file__).parent / "locales"))
    i18n.set("filename_format", "{locale}.{format}")
    i18n.set("locale", "es")


configurar_i18n()
app = typer.Typer(help=i18n.t(_BANNER), invoke_without_command=True)


@app.callback()
def mostrar_inicio() -> None:
    """Muestra el banner y las instrucciones de uso del CLI."""
    typer.echo(i18n.t(_BANNER))
    typer.echo(i18n.t(_INSTRUCCIONES))


def main() -> None:
    """Ejecuta la aplicación del CLI."""
    app()
