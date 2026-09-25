"""El CLI arranca mostrando el taxi — costura: borde del CLI (spec #14)."""

from cli.main import app
from typer.testing import CliRunner

runner = CliRunner()


def test_al_arrancar_muestra_taxi_e_instrucciones_en_espanol() -> None:
    resultado = runner.invoke(app, [])
    salida = resultado.output
    # Español fijado por el locale es.yml (requisito Fase 1: idioma español)
    assert "🚕" in salida
    assert "Bienvenido" in salida
    assert "iniciar" in salida
    assert "estado" in salida
    assert "finalizar" in salida


def test_los_textos_se_resuelven_y_no_van_en_blanco() -> None:
    resultado = runner.invoke(app, [])
    salida = resultado.output.strip()
    # El placeholder i18n se resolvió: la clave cruda no puede viajar a la salida
    assert "taximetro." not in salida
    # Ni en blanco: hay contenido real renderizado
    assert salida != ""
