"""El dispatcher: `python -m taximetro_cli` abre la TUI — no es el REPL."""

import subprocess


def test_python_m_taximetro_cli_arranca_la_tui_no_el_repl() -> None:
    resultado = subprocess.run(
        ["uv", "run", "python", "-m", "taximetro_cli"],
        input="q\n",
        capture_output=True,
        text=True,
        timeout=30,
    )

    salida = resultado.stdout + resultado.stderr
    # El marcador del REPL (banner + instrucciones) no puede aparecer:
    # la entrada del binario es la TUI, no la sesión de comandos.
    assert "Bienvenido. Comandos" not in salida
    assert "libre · sin carrera" not in salida
