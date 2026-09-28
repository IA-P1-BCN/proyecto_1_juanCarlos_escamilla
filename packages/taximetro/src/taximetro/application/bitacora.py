"""Wiring de la bitácora: eventos de dominio de ride → líneas de operación."""

from taximetro_kernel import EventBus
from taximetro_log import BitacoraJSON
from taximetro_ride import CarreraFinalizada, CarreraIniciada, EstadoCambiado


def registrar_eventos(bus: EventBus, bitacora: BitacoraJSON) -> None:
    """Suscribe la bitácora al EventBus: cada evento de ride queda registrado."""
    bus.suscribir(
        CarreraIniciada,
        lambda e: bitacora.registrar("carrera_iniciada", momento=e.momento.isoformat()),
    )
    bus.suscribir(
        EstadoCambiado,
        lambda e: bitacora.registrar(
            "estado_cambiado", momento=e.momento.isoformat(), estado=e.estado.value
        ),
    )
    bus.suscribir(
        CarreraFinalizada,
        lambda e: bitacora.registrar(
            "carrera_finalizada", momento=e.momento.isoformat()
        ),
    )
