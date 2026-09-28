"""Composition root de la app: ensambla el turno con adaptadores reales."""

from taximetro import (
    BitacoraJSON,
    EventBus,
    HistoricoJson,
    ServicioTaximetro,
    cargar_tarifa,
    registrar_eventos,
)


def crear_servicio(
    reloj, historico: HistoricoJson | None = None, bitacora: BitacoraJSON | None = None
) -> ServicioTaximetro:
    """Tarifas del config, bus con bitácora suscrita e histórico en JSON."""
    bitacora = bitacora or BitacoraJSON()
    bus = EventBus()
    registrar_eventos(bus, bitacora)
    bitacora.registrar("arranque")
    return ServicioTaximetro(
        tarifa=cargar_tarifa(),
        reloj=reloj,
        publicar=bus.publicar,
        historico=historico or HistoricoJson(),
    )
