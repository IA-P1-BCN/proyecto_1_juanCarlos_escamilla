"""Punto de entrada del CLI del taxímetro."""

from pathlib import Path

import i18n
import typer

_locales = Path(__file__).parent / "locales"
i18n.load_path.append(str(_locales))
i18n.set("filename_format", "{locale}.{format}")
i18n.set("locale", "es")

app = typer.Typer(help=i18n.t("taximetro.banner"), invoke_without_command=True)


@app.callback()
def callback() -> None:
    typer.echo(i18n.t("taximetro.banner"))
    typer.echo(i18n.t("taximetro.instrucciones"))


def main() -> None:
    app()
