"""Criterios de aceptación de las Fases 1 y 2 (milestones 1 y 2, v0.1.0).

Cada test recupera UN criterio literal de las issues #5 #6 #7 #16 #17 #18 #19
y lo verifica por las costuras pactadas (API pública del paquete y borde del REPL),
con reloj inyectado. Pensado para alimentar el informe Allure: epic = Fase,
story = issue.
"""

import json
import re
from pathlib import Path

import allure
import pytest
from conftest import RelojFalso, hora
from taximetro import (
    BitacoraJSON,
    CarreraFinalizada,
    CarreraIniciada,
    Estado,
    EstadoCambiado,
    EventBus,
    HistoricoJson,
    Money,
    ServicioTaximetro,
    Tarifa,
    cargar_tarifa,
    registrar_eventos,
)
from taximetro_cli.interfaces.cli import crear_app
from taximetro_log import leer
from typer.testing import CliRunner

TARIFA_EMT = Tarifa(parada_centimos_por_segundo=2, movimiento_centimos_por_segundo=5)
runner = CliRunner()

EPIC_F1 = allure.epic("Fase 1 — MVP Funcional")
EPIC_F2 = allure.epic("Fase 2 — Observabilidad y Persistencia")


def _servicio(instantes, historico=None):
    eventos: list[object] = []
    bus = EventBus()
    for tipo in (CarreraIniciada, EstadoCambiado, CarreraFinalizada):
        bus.suscribir(tipo, eventos.append)
    servicio = ServicioTaximetro(
        tarifa=TARIFA_EMT,
        reloj=RelojFalso(instantes),
        publicar=bus.publicar,
        historico=historico,
    )
    return servicio, eventos


# ---------------------------------------------------------------- #16


@EPIC_F1
@allure.story("#16 Instrucciones al arrancar + iniciar Carrera en parada")
@allure.title("AC: al arrancar muestra las instrucciones sin documentación externa")
def test_ac16_instrucciones_al_arrancar() -> None:
    resultado = runner.invoke(crear_app(RelojFalso([])), [], input="salir\n")

    assert "Bienvenido. Comandos:" in resultado.output


@EPIC_F1
@allure.story("#16 Instrucciones al arrancar + iniciar Carrera en parada")
@allure.title("AC: un solo comando inicia la Carrera y cobra desde el arranque")
def test_ac16_un_comando_inicia_y_cobra_desde_el_arranque() -> None:
    servicio, _ = _servicio([hora(10), hora(10, 0, 5)])

    servicio.iniciar()

    assert servicio.en_carrera
    assert servicio.importe == Money(centimos=10)  # 5 s × 0,02 €/s desde el arranque


@EPIC_F1
@allure.story("#16 Instrucciones al arrancar + iniciar Carrera en parada")
@allure.title("AC: el Importe parte de 0,00 € y se acumula de forma continua")
def test_ac16_importe_parte_de_cero() -> None:
    servicio, _ = _servicio([hora(10), hora(10)])

    servicio.iniciar()

    assert servicio.importe.formato() == "0,00 €"


@EPIC_F1
@allure.story("#16 Instrucciones al arrancar + iniciar Carrera en parada")
@allure.title("AC: tras t segundos en parada, exactamente 0,02 × t €")
@pytest.mark.parametrize("segundos,centimos", [(7, 14), (10, 20), (63, 126)])
def test_ac16_0_02_por_segundo_exacto(segundos: int, centimos: int) -> None:
    minuto, segundo = divmod(segundos, 60)
    servicio, _ = _servicio([hora(10), hora(10, minuto, segundo)])

    servicio.iniciar()

    assert servicio.importe.centimos == centimos


@EPIC_F1
@allure.story("#16 Instrucciones al arrancar + iniciar Carrera en parada")
@allure.title("AC: ride emite CarreraIniciada al iniciar")
def test_ac16_emite_carrera_iniciada() -> None:
    servicio, eventos = _servicio([hora(10), hora(10)])

    servicio.iniciar()

    assert [type(e).__name__ for e in eventos] == ["CarreraIniciada"]


# ---------------------------------------------------------------- #17


@EPIC_F1
@allure.story("#17 Cambiar Estado a en_movimiento (0,05 €/s por tramo)")
@allure.title("AC: el conductor puede indicar el estado en cada momento")
def test_ac17_indicar_estado_en_cada_momento() -> None:
    servicio, _ = _servicio([hora(10), hora(10, 0, 5), hora(10, 0, 10)])

    servicio.iniciar()
    servicio.cambiar_estado(Estado.EN_MOVIMIENTO)
    assert servicio.estado is Estado.EN_MOVIMIENTO
    servicio.cambiar_estado(Estado.PARADA)
    assert servicio.estado is Estado.PARADA


@EPIC_F1
@allure.story("#17 Cambiar Estado a en_movimiento (0,05 €/s por tramo)")
@allure.title("AC: cada tramo aplica su tarifa (0,02 / 0,05 €/s)")
def test_ac17_cada_tramo_su_tarifa() -> None:
    tramo_parada = _servicio([hora(10), hora(10, 0, 5)])
    tramo_parada[0].iniciar()
    assert tramo_parada[0].importe.centimos == 10  # 5 s × 2 c/s

    tramo_movimiento = _servicio([hora(10), hora(10, 0, 4), hora(10, 0, 8)])
    tramo_movimiento[0].iniciar()
    tramo_movimiento[0].cambiar_estado(Estado.EN_MOVIMIENTO)

    # 4 s × 2 c (parada) + 4 s × 5 c (movimiento): cada tramo con SU tarifa
    assert tramo_movimiento[0].importe.centimos == 8 + 20


@EPIC_F1
@allure.story("#17 Cambiar Estado a en_movimiento (0,05 €/s por tramo)")
@allure.title("AC: cambiar de Estado no detiene la acumulación ni la reinicia")
def test_ac17_cambiar_no_detiene_ni_reinicia() -> None:
    servicio, _ = _servicio([hora(10), hora(10, 0, 5), hora(10, 0, 5), hora(10, 0, 6)])

    servicio.iniciar()
    antes = servicio.importe.centimos  # 0,10 € tras 5 s en parada
    servicio.cambiar_estado(Estado.EN_MOVIMIENTO)
    despues = servicio.importe.centimos

    assert antes == 10
    assert despues == 15  # 0,10 acumulados + 1 s × 0,05: ni congelado ni a cero


@EPIC_F1
@allure.story("#17 Cambiar Estado a en_movimiento (0,05 €/s por tramo)")
@allure.title("AC: t1 s en parada + t2 s en movimiento = 0,02·t1 + 0,05·t2")
def test_ac17_formula_por_tramos() -> None:
    servicio, _ = _servicio([hora(10), hora(10, 0, 5), hora(10, 0, 20)])

    servicio.iniciar()
    servicio.cambiar_estado(Estado.EN_MOVIMIENTO)

    assert servicio.importe.centimos == 0.02 * 5 * 100 + 0.05 * 15 * 100  # 85


@EPIC_F1
@allure.story("#17 Cambiar Estado a en_movimiento (0,05 €/s por tramo)")
@allure.title("AC: ride emite EstadoCambiado en cada cambio")
def test_ac17_emite_estado_cambiado() -> None:
    servicio, eventos = _servicio([hora(10), hora(10, 0, 5)])

    servicio.iniciar()
    servicio.cambiar_estado(Estado.EN_MOVIMIENTO)

    cambios = [e for e in eventos if type(e).__name__ == "EstadoCambiado"]
    assert len(cambios) == 1
    assert cambios[0].estado is Estado.EN_MOVIMIENTO


# ---------------------------------------------------------------- #18


@EPIC_F1
@allure.story("#18 Finalizar y mostrar el Importe con dos decimales")
@allure.title("AC: un comando cierra la Carrera y muestra el Importe total")
def test_ac18_comando_finaliza_y_muestra_total() -> None:
    resultado = runner.invoke(
        crear_app(RelojFalso([hora(10), hora(10), hora(10, 0, 10)])),
        [],
        input="iniciar\nfinalizar\nsalir\n",
    )

    assert "Carrera finalizada. Importe total:" in resultado.output


@EPIC_F1
@allure.story("#18 Finalizar y mostrar el Importe con dos decimales")
@allure.title("AC: el total se muestra en euros con dos decimales")
def test_ac18_total_con_dos_decimales() -> None:
    resultado = runner.invoke(
        crear_app(RelojFalso([hora(10), hora(10), hora(10, 0, 10)])),
        [],
        input="iniciar\nfinalizar\nsalir\n",
    )

    assert re.search(r"Importe total: \d+,\d{2} €", resultado.output)


@EPIC_F1
@allure.story("#18 Finalizar y mostrar el Importe con dos decimales")
@allure.title("AC: el total es la suma exacta de todos los tramos")
def test_ac18_total_suma_exacta_de_tramos() -> None:
    servicio, _ = _servicio([hora(10), hora(10, 0, 5), hora(10, 0, 20)])

    servicio.iniciar()
    servicio.cambiar_estado(Estado.EN_MOVIMIENTO)
    total = servicio.finalizar()

    assert total.centimos == 10 + 75  # tramo parada (5 s × 2) + tramo mov (15 s × 5)


@EPIC_F1
@allure.story("#18 Finalizar y mostrar el Importe con dos decimales")
@allure.title("AC: sin redondeo intermedio — un único redondeo al final")
def test_ac18_sin_redondeo_intermedio() -> None:
    servicio = _servicio([hora(10), hora(10, 0, 1, 500000)])[0]

    servicio.iniciar()
    total = servicio.finalizar()

    assert total.formato() == "0,03 €"  # 1,5 s × 0,02 = 3 c exactos

    raro = _servicio([hora(10), hora(10, 0, 0, 625000)])[0]
    raro.iniciar()
    assert raro.finalizar().centimos == 1  # 1,25 c internos → 1 (half-up, una vez)


@EPIC_F1
@allure.story("#18 Finalizar y mostrar el Importe con dos decimales")
@allure.title("AC: ride emite CarreraFinalizada al cerrar")
def test_ac18_emite_carrera_finalizada() -> None:
    # El evento lleva el momento del cierre; el Importe lo deriva billing del
    # tramo cerrado en ese instante (ADR 0005: ride no conoce tarifas).
    servicio, eventos = _servicio([hora(10), hora(10, 0, 10)])

    servicio.iniciar()
    total = servicio.finalizar()

    assert [type(e).__name__ for e in eventos] == [
        "CarreraIniciada",
        "CarreraFinalizada",
    ]
    assert eventos[-1].momento == hora(10, 0, 10)
    assert total.centimos == 20


# ---------------------------------------------------------------- #19


@EPIC_F1
@allure.story("#19 Encadenar carreras sin cerrar el programa")
@allure.title("AC: tras finalizar se puede iniciar otra Carrera de inmediato")
def test_ac19_iniciar_otra_de_inmediato() -> None:
    servicio, _ = _servicio([hora(10), hora(10, 0, 10), hora(10, 0, 10)])

    servicio.iniciar()
    servicio.finalizar()
    servicio.iniciar()

    assert servicio.en_carrera


@EPIC_F1
@allure.story("#19 Encadenar carreras sin cerrar el programa")
@allure.title("AC: cada nueva Carrera arranca con el acumulador a 0,00 €")
def test_ac19_nueva_carrera_a_cero() -> None:
    servicio, _ = _servicio(
        [hora(10), hora(10, 0, 10), hora(10, 0, 10), hora(10, 0, 10)]
    )

    servicio.iniciar()
    assert servicio.finalizar().centimos == 20
    servicio.iniciar()

    assert servicio.importe.formato() == "0,00 €"


@EPIC_F1
@allure.story("#19 Encadenar carreras sin cerrar el programa")
@allure.title("AC: varias carreras consecutivas producen totales independientes")
def test_ac19_totales_independientes() -> None:
    servicio, _ = _servicio(
        [hora(10), hora(10, 0, 10), hora(10, 0, 10), hora(10, 0, 15), hora(10, 0, 20)]
    )

    servicio.iniciar()
    primera = servicio.finalizar()
    servicio.iniciar()
    servicio.cambiar_estado(Estado.EN_MOVIMIENTO)
    segunda = servicio.finalizar()

    assert primera.centimos == 20  # 10 s en parada
    assert segunda.centimos == 35  # 5 s parada + 5 s movimiento


@EPIC_F1
@allure.story("#19 Encadenar carreras sin cerrar el programa")
@allure.title("AC: el programa no se cierra entre carreras")
def test_ac19_programa_no_se_cierra() -> None:
    resultado = runner.invoke(
        crear_app(
            RelojFalso(
                [hora(10), hora(10), hora(10, 0, 5), hora(10, 0, 5), hora(10, 0, 5)]
            )
        ),
        [],
        input="iniciar\nfinalizar\niniciar\nsalir\n",
    )

    assert resultado.exit_code == 0  # una sola sesión, dos Carreras
    assert resultado.output.count("Carrera iniciada") == 2


# ---------------------------------------------------------------- #5


@EPIC_F2
@allure.story("#5 Histórico de carreras del día para cuadrar caja")
@allure.title("AC: al finalizar se guardan fecha, duración e importe permanentes")
def test_ac5_guarda_fecha_duracion_importe(tmp_path: Path) -> None:
    historico = HistoricoJson(tmp_path / "historico.json")
    servicio = ServicioTaximetro(
        tarifa=TARIFA_EMT,
        reloj=RelojFalso([hora(10), hora(10, 0, 20)]),
        historico=historico,
    )

    servicio.iniciar()
    total = servicio.finalizar()

    registros = historico.del_dia(hora(10).date())
    assert len(registros) == 1
    assert registros[0].inicio == hora(10)
    assert registros[0].duracion_segundos == 20.0
    assert registros[0].importe == total


@EPIC_F2
@allure.story("#5 Histórico de carreras del día para cuadrar caja")
@allure.title("AC: escritura incremental; disponible en la siguiente sesión")
def test_ac5_incremental_y_entre_sesiones(tmp_path: Path) -> None:
    ruta = tmp_path / "historico.json"

    def turno() -> None:
        # una "sesión" nueva: proceso y fichero reabiertos
        servicio = ServicioTaximetro(
            tarifa=TARIFA_EMT,
            reloj=RelojFalso([hora(10), hora(10, 0, 10)]),
            historico=HistoricoJson(ruta),
        )
        servicio.iniciar()
        servicio.finalizar()

    turno()
    turno()

    registros = HistoricoJson(ruta).del_dia(hora(10).date())
    assert len(registros) == 2  # incremental: cada finalizar persiste su carrera


@EPIC_F2
@allure.story("#5 Histórico de carreras del día para cuadrar caja")
@allure.title("AC: se puede consultar el histórico del día para cuadrar caja")
def test_ac5_consulta_del_dia(tmp_path: Path) -> None:
    historico = HistoricoJson(tmp_path / "historico.json")
    resultado = runner.invoke(
        crear_app(
            RelojFalso([hora(10), hora(10), hora(10, 0, 10)]), historico=historico
        ),
        [],
        input="iniciar\nfinalizar\nhistorial 2026-09-28\nsalir\n",
    )

    assert "Histórico · 28/09/2026" in resultado.output
    assert "00:00:10" in resultado.output
    assert "1 carreras · 0,20 € totales" in resultado.output


# ---------------------------------------------------------------- #6


@EPIC_F2
@allure.story("#6 Logs de operación para diagnosticar errores")
@allure.title("AC: se registran arranque, cambios de estado, cierre y errores")
def test_ac6_registra_todo_el_ciclo_y_errores(tmp_path: Path) -> None:
    ruta = tmp_path / "taximetro.log"
    bitacora = BitacoraJSON(ruta)

    runner.invoke(
        crear_app(
            RelojFalso([hora(10), hora(10), hora(10, 0, 5), hora(10, 0, 5)]),
            bitacora=bitacora,
        ),
        [],
        input="iniciar\nestado movimiento\nfinalizar\nfinalizar\nsalir\n",
    )

    eventos = [e["evento"] for e in leer(ruta)]
    assert "arranque" in eventos
    assert "carrera_iniciada" in eventos
    assert "estado_cambiado" in eventos
    assert "carrera_finalizada" in eventos
    assert "error" in eventos  # el segundo finalizar, sin Carrera en curso


@EPIC_F2
@allure.story("#6 Logs de operación para diagnosticar errores")
@allure.title("AC: log estructurado, accesible sin intervenir el proceso")
def test_ac6_estructurado_y_accesible(tmp_path: Path) -> None:
    ruta = tmp_path / "taximetro.log"
    bitacora = BitacoraJSON(ruta)
    bus = EventBus()
    registrar_eventos(bus, bitacora)

    bus.publicar(CarreraIniciada(momento=hora(10)))

    lineas = ruta.read_text(encoding="utf-8").splitlines()
    assert len(lineas) == 1  # flusheado línea a línea: legible en caliente
    registro = json.loads(lineas[0])
    assert set(registro) >= {"timestamp", "evento"}
    assert registro["evento"] == "carrera_iniciada"


# ---------------------------------------------------------------- #7


@EPIC_F2
@allure.story("#7 Cambiar tarifas por fichero de configuración")
@allure.title("AC: las tarifas se modifican editando un fichero externo")
def test_ac7_tarifas_desde_fichero(tmp_path: Path) -> None:
    fichero = tmp_path / "tarifas.json"
    fichero.write_text(
        '{"parada_eur_segundo": 0.03, "movimiento_eur_segundo": 0.10}',
        encoding="utf-8",
    )

    assert cargar_tarifa(fichero) == Tarifa(
        parada_centimos_por_segundo=3, movimiento_centimos_por_segundo=10
    )


@EPIC_F2
@allure.story("#7 Cambiar tarifas por fichero de configuración")
@allure.title("AC: sin tocar código ni redeployar para actualizar tarifas")
def test_ac7_actualizar_sin_redeployar(tmp_path: Path) -> None:
    fichero = tmp_path / "tarifas.json"
    fichero.write_text(
        '{"parada_eur_segundo": 0.02, "movimiento_eur_segundo": 0.05}',
        encoding="utf-8",
    )
    antes = cargar_tarifa(fichero)

    fichero.write_text(
        '{"parada_eur_segundo": 0.04, "movimiento_eur_segundo": 0.09}',
        encoding="utf-8",
    )  # solo se edita el fichero: la siguiente arranque ya aplica lo nuevo
    despues = cargar_tarifa(fichero)

    assert antes != despues
    assert despues == Tarifa(
        parada_centimos_por_segundo=4, movimiento_centimos_por_segundo=9
    )
