"""Integración del binario nativo: compilar bin/taximetro y conducirlo de verdad.

Compila una vez por sesión (fixture) con PyInstaller y luego ejercita la TUI
en un pty con teclas reales — igual que la demo — verificando el ciclo completo
y la persistencia (histórico y bitácora) en el directorio de ejecución.
"""

import json
import os
import pty
import re
import select
import shutil
import subprocess
import time
from fcntl import ioctl
from pathlib import Path
from struct import pack
from termios import TIOCSWINSZ

import allure
import pytest

RAIZ = Path(__file__).resolve().parents[3]
BINARIO = RAIZ / "bin" / "taximetro"
MONTAJE = b"pulsa 1"
ANCHO, ALTO = 80, 24


@pytest.fixture(scope="session")
def binario() -> Path:
    """Compila el ejecutable (equivalente a `task bin`) y devuelve su ruta."""
    subprocess.run(
        [
            "uv",
            "run",
            "pyinstaller",
            "apps/taximetro_cli/taximetro.spec",
            "--noconfirm",
        ],
        cwd=RAIZ,
        check=True,
        capture_output=True,
        timeout=600,
    )
    BINARIO.parent.mkdir(exist_ok=True)
    shutil.copy(RAIZ / "dist" / "taximetro", BINARIO)
    return BINARIO


def conducir(binario: Path, cwd: Path, teclas: list[tuple[float, str]]) -> bytes:
    """Arranca la TUI en un pty, envía las teclas con su retraso y captura todo."""
    pid, maestro = pty.fork()
    if pid == 0:
        os.chdir(cwd)
        os.execv(str(binario), [str(binario)])
        os._exit(1)
    ioctl(maestro, TIOCSWINSZ, pack("HHHH", ALTO, ANCHO, 0, 0))

    salida = bytearray()
    montaje: float | None = None
    arranque = time.monotonic()
    pendientes = list(teclas)
    while True:
        ahora = time.monotonic()
        if montaje is not None and pendientes and ahora - montaje >= pendientes[0][0]:
            os.write(maestro, pendientes.pop(0)[1].encode())
            continue
        if (
            montaje is not None
            and not pendientes
            and ahora - montaje > teclas[-1][0] + 2.5
        ):
            break
        if montaje is None and ahora - arranque > 30:
            raise AssertionError("la TUI nunca montó")
        listo, _, _ = select.select([maestro], [], [], 0.02)
        if not listo:
            continue
        try:
            datos = os.read(maestro, 65536)
        except OSError:
            break
        if not datos:
            break
        salida.extend(datos)
        if montaje is None and MONTAJE in bytes(salida[-200:]):
            montaje = time.monotonic()
    try:
        os.close(maestro)
    except OSError:
        pass
    _, estado = os.waitpid(pid, 0)
    assert estado == 0, "el binario terminó con error"
    return bytes(salida)


@allure.epic("Integración — binario nativo")
@allure.story("Compilación y arranque")
@allure.title("El binario compilado arranca la TUI del conductor")
def test_el_binario_arranca_la_tui(binario: Path, tmp_path: Path) -> None:
    salida = conducir(binario, tmp_path, [(0.5, "q")])

    assert b"Tax" in salida  # título de la TUI
    assert MONTAJE in salida  # pantalla inicial del conductor


@allure.epic("Integración — binario nativo")
@allure.story("Turno completo")
@allure.title("Un turno completo sobre el binario: iniciar, cambiar, finalizar")
def test_turno_completo_en_el_binario(binario: Path, tmp_path: Path) -> None:
    salida = conducir(
        binario,
        tmp_path,
        [(0.3, "1"), (1.3, "2"), (2.3, "3"), (3.6, "q")],
    )
    texto = salida.decode("utf-8", "replace")

    assert "PARADA" in texto
    assert "EN_MOVIMIENTO" in texto
    assert "Carrera finalizada" in texto
    assert re.search(r"Importe total: \d+,\d{2} €", texto)


@allure.epic("Integración — binario nativo")
@allure.story("Persistencia")
@allure.title("El binario persiste histórico y bitácora en data/")
def test_el_binario_persiste_datos(binario: Path, tmp_path: Path) -> None:
    conducir(binario, tmp_path, [(0.3, "1"), (1.3, "2"), (2.3, "3"), (3.6, "q")])

    data = tmp_path / "data"
    registros = json.loads((data / "historico.json").read_text(encoding="utf-8"))
    assert len(registros) == 1
    assert registros[0]["importe_centimos"] == 7  # 1 s parada + 1 s movimiento

    bitacora = [
        json.loads(linea)
        for linea in (data / "taximetro.log").read_text(encoding="utf-8").splitlines()
    ]
    eventos = {e["evento"] for e in bitacora}
    assert {
        "arranque",
        "carrera_iniciada",
        "estado_cambiado",
        "carrera_finalizada",
    } <= eventos
