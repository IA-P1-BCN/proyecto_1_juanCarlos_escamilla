"""Driver de la demo TUI: graba bin/taximetro en un pty tecleando el turno a ritmo fijo.

Uso: python3 scripts/demo-tui-driver.py [RUTA_BINARIO] [SALIDA.cast]
Secuencia: 1 · (3s) · 2 · (5s) · 2 · (4s) · 3 · (2s) · q — el vídeo termina al salir.
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

# (retraso en segundos desde el montaje de la TUI, tecla a enviar)
SECUENCIA = [(0.3, "1"), (3.3, "2"), (8.3, "2"), (12.3, "3"), (14.3, "q")]
MONTAJE = b"pulsa 1"  # texto del estado inicial: la TUI ya está en pantalla
FIN = 16.5  # corte tras la última tecla (los 2s de cola tras finalizar)
ANCHO, ALTO = 80, 24


def main() -> None:
    binario = sys.argv[1] if len(sys.argv) > 1 else "./bin/taximetro"
    salida = sys.argv[2] if len(sys.argv) > 2 else "demo-tui.cast"
    pid, maestro = pty.fork()
    if pid == 0:
        os.execvp(binario, [binario])
        os._exit(1)
    ioctl(maestro, TIOCSWINSZ, pack("HHHH", ALTO, ANCHO, 0, 0))

    eventos: list[tuple[float, str]] = []
    arranque = time.monotonic()  # reloj de los eventos: nunca se reinicia (monótono)
    montaje: float | None = None  # instante del montaje: origen del ritmo de teclas
    pendientes = list(SECUENCIA)
    recorte = b""
    while True:
        ahora = time.monotonic()
        if montaje is not None:
            if pendientes and ahora - montaje >= pendientes[0][0]:
                os.write(maestro, pendientes.pop(0)[1].encode())
                continue
            if ahora - montaje > FIN:
                break
        elif ahora - arranque > 30:
            break  # la TUI nunca montó: no grabar eternamente
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
        if montaje is None:
            recorte = (recorte + datos)[-200:]
            if MONTAJE in recorte:
                montaje = time.monotonic()
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
