"""Graba un vídeo (GIF) de cada test de criterios de aceptación ejecutándose.

Uso: python3 scripts/tests-videos.py
Para cada `test_acNN_*` de test_criterios_aceptacion.py abre un pty, teclea el
comando pytest del test, captura la ejecución (asciinema .cast) y la renderiza
con agg a docs/assets/tests/<test>.gif — el attachment que ve el revisor en el
informe Allure.
"""

import json
import os
import pty
import re
import select
import subprocess
import sys
import tempfile
import time
from fcntl import ioctl
from pathlib import Path
from struct import pack
from termios import TIOCSWINSZ

RAIZ = Path(__file__).resolve().parents[1]
FICHERO_AC = "apps/taximetro_cli/tests/test_criterios_aceptacion.py"
DESTINO = RAIZ / "docs" / "assets" / "tests"
ANCHO, ALTO = 100, 26
PROMPT = b"$ "


def _nombres_de_tests() -> list[str]:
    fuente = (RAIZ / FICHERO_AC).read_text(encoding="utf-8")
    return re.findall(r"^def (test_ac\d+_\w+)\(", fuente, re.MULTILINE)


def _grabar(comando: str) -> list[tuple[float, str]]:
    pid, maestro = pty.fork()
    if pid == 0:
        env = dict(os.environ, PS1="$ ", BASH_SILENCE_DEPRECATION_WARNING="1")
        os.execvpe("bash", ["bash", "--noprofile", "--norc"], env)
        os._exit(1)
    ioctl(maestro, TIOCSWINSZ, pack("HHHH", ALTO, ANCHO, 0, 0))

    eventos: list[tuple[float, str]] = []
    arranque = time.monotonic()
    prompt_visto = False
    escrito = False
    fin_del_comando = False
    while True:
        if prompt_visto and not escrito:
            for c in comando:
                eventos.append((time.monotonic() - arranque, c))
                os.write(maestro, c.encode())
                time.sleep(0.012)
            os.write(maestro, b"\r")
            escrito = True
            continue
        if fin_del_comando and time.monotonic() - arranque > 2:
            os.write(maestro, b"exit\r")
            break
        listo, _, _ = select.select([maestro], [], [], 0.05)
        if not listo:
            continue
        try:
            datos = os.read(maestro, 65536)
        except OSError:
            break
        if not datos:
            break
        eventos.append((time.monotonic() - arranque, datos.decode("utf-8", "replace")))
        cola = datos[-60:]
        if not prompt_visto and PROMPT in cola:
            prompt_visto = True
        elif escrito and b"passed" in cola or b"failed" in cola:
            fin_del_comando = True
    try:
        os.close(maestro)
    except OSError:
        pass
    os.waitpid(pid, 0)
    return eventos


def main() -> None:
    if subprocess.run(["which", "agg"], capture_output=True).returncode != 0:
        sys.exit("✗ Falta agg: brew install agg")
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nombre in _nombres_de_tests():
        gif = DESTINO / f"{nombre}.gif"
        comando = f'uv run pytest "{FICHERO_AC}::{nombre}" -q --no-header'
        eventos = _grabar(comando)
        with tempfile.NamedTemporaryFile(suffix=".cast", delete=False) as tmp:
            cast = Path(tmp.name)
        cast.write_text(
            json.dumps(
                {
                    "version": 2,
                    "width": ANCHO,
                    "height": ALTO,
                    "env": {"TERM": "xterm-256color"},
                }
            )
            + "\n"
            + "".join(
                json.dumps([round(t, 3), "o", d], ensure_ascii=False) + "\n"
                for t, d in eventos
            ),
            encoding="utf-8",
        )
        subprocess.run(
            [
                "agg",
                str(cast),
                str(gif),
                "--theme",
                "dracula",
                "--font-size",
                "16",
                "--idle-time-limit",
                "2",
            ],
            check=True,
            capture_output=True,
        )
        cast.unlink(missing_ok=True)
        print(f"✓ {gif.name} ({gif.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
