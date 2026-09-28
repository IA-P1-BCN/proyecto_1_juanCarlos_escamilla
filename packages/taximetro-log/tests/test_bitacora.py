"""La bitácora escribe JSON-lines acumulativos — API pública de taximetro-log (#6)."""

import json
from pathlib import Path

from taximetro_log import BitacoraJSON, leer


def test_registrar_escribe_una_linea_json(tmp_path: Path) -> None:
    ruta = tmp_path / "taximetro.log"

    BitacoraJSON(ruta).registrar(
        "carrera_iniciada", momento="2026-09-28T10:00:00+00:00"
    )

    lineas = ruta.read_text(encoding="utf-8").splitlines()
    assert len(lineas) == 1
    evento = json.loads(lineas[0])
    assert evento["evento"] == "carrera_iniciada"
    assert evento["momento"] == "2026-09-28T10:00:00+00:00"
    assert evento["timestamp"]  # siempre hay timestamp UTC


def test_los_eventos_se_acumulan_en_orden(tmp_path: Path) -> None:
    ruta = tmp_path / "taximetro.log"
    bitacora = BitacoraJSON(ruta)

    bitacora.registrar("arranque")
    bitacora.registrar("carrera_finalizada", momento="2026-09-28T10:00:20+00:00")

    eventos = leer(ruta)
    assert [e["evento"] for e in eventos] == ["arranque", "carrera_finalizada"]


def test_leer_de_un_fichero_inexistente_es_vacio(tmp_path: Path) -> None:
    assert leer(tmp_path / "nada.log") == []
