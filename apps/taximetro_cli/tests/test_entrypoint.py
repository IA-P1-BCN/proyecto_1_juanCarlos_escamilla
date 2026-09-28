"""El dispatcher: `python -m taximetro_cli` arranca el REPL; `tui` abre la TUI."""

import subprocess


def test_python_m_taximetro_cli_arranca_el_repl() -> None:
    resultado = subprocess.run(
        ["uv", "run", "python", "-m", "taximetro_cli"],
        input="salir\n",
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert resultado.returncode == 0
    assert "🚕" in resultado.stdout
    assert "Bienvenido" in resultado.stdout
