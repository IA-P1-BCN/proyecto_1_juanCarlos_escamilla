"""Driver de la demo TUI: graba la sesión en un pty — terminal, `task run-tui` y turno.

Uso: scripts/demo-gif.sh   (graba con este driver y renderiza el GIF con agg)

Vídeo: prompt del shell → se escribe `task run-tui` → TUI →
       1 · (3s) · 2 · (5s) · 2 · (4s) · 3 · (2s) · q — el vídeo termina al salir.
Produce un fichero asciinema v2 (.cast) que `agg` convierte en GIF.
"""

import json
import os
import pty
import select
import sys
import time
from fcntl import ioctl
from struct import pack
from termios import TIOCSWINSZ

PROMPT = b"$ "  # prompt de bash --norc
COMANDO = "task run-tui"
# Fase shell: tecleo del comando (70 ms por carácter) + Enter
FASE_SHELL = [(i * 0.07, c) for i, c in enumerate(COMANDO)] + [(4.0, "\r")]
# Fase TUI (segundos desde el montaje de la TUI): el turno del taxista
FASE_TUI = [(0.3, "1"), (3.3, "2"), (8.3, "2"), (12.3, "3"), (14.3, "q")]
MONTAJE = b"pulsa 1"  # texto del estado inicial: la TUI ya está en pantalla
FIN_TUI = 16.5  # corte tras la última tecla (los 2s de cola tras finalizar)
ANCHO, ALTO = 80, 24


def main() -> None:
    salida = sys.argv[1] if len(sys.argv) > 1 else "demo-tui.cast"
    pid, maestro = pty.fork()
    if pid == 0:
        env = dict(os.environ, BASH_SILENCE_DEPRECATION_WARNING="1", PS1="$ ")
        os.execvpe("bash", ["bash", "--noprofile", "--norc"], env)
        os._exit(1)
    ioctl(maestro, TIOCSWINSZ, pack("HHHH", ALTO, ANCHO, 0, 0))

    eventos: list[tuple[float, str]] = []
    arranque = time.monotonic()  # reloj de los eventos: nunca se reinicia (monótono)
    anclas = {"shell": None, "tui": None}  # instantes de arranque de cada fase
    pendientes = [("shell", t, k) for t, k in FASE_SHELL] + [
        ("tui", t, k) for t, k in FASE_TUI
    ]
    recorte = b""
    while True:
        ahora = time.monotonic()
        vencidos = [
            (t, k, fase)
            for fase, t, k in pendientes
            if anclas[fase] is not None and ahora - anclas[fase] >= t
        ]
        if vencidos:
            _, tecla, fase = min(vencidos)
            pendientes.remove((fase, min(vencidos)[0], tecla))
            os.write(maestro, tecla.encode())
            continue
        if anclas["tui"] is not None and ahora - anclas["tui"] > FIN_TUI:
            break
        if all(a is None for a in anclas.values()) and ahora - arranque > 30:
            break  # ni prompt ni TUI: no grabar eternamente
        listo, _, _ = select.select([maestro], [], [], 0.02)
        if not listo:
            continue
        try:
            datos = os.read(maestro, 65536)
        except OSError:
            break  # el hijo cerró el pty
        if not datos:
            break
        eventos.append((ahora - arranque, datos))
        recorte = (recorte + datos)[-200:]
        if anclas["shell"] is None and PROMPT in recorte:
            anclas["shell"] = time.monotonic()
        elif anclas["tui"] is None and MONTAJE in recorte:
            anclas["tui"] = time.monotonic()
    try:
        os.close(maestro)
    except OSError:
        pass
    os.waitpid(pid, 0)

    cabecera = {
        "version": 2,
        "width": ANCHO,
        "height": ALTO,
        "timestamp": int(time.time()),
        "env": {"TERM": "xterm-256color", "COLORTERM": "truecolor"},
    }
    with open(salida, "w", encoding="utf-8") as f:
        f.write(json.dumps(cabecera) + "\n")
        for instante, datos in eventos:
            f.write(
                json.dumps(
                    [round(instante, 3), "o", datos.decode("utf-8", "replace")],
                    ensure_ascii=False,
                )
                + "\n"
            )
    print(f"{salida}: {len(eventos)} eventos, {eventos[-1][0]:.1f}s")


if __name__ == "__main__":
    main()
