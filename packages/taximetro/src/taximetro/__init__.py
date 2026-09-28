"""Taxímetro — lógica de negocio: Carrera por tramos, Tarifa, Importe."""

from taximetro.application.servicio import (
    CarreraYaEnCursoError,
    NoHayCarreraError,
    ServicioTaximetro,
)
from taximetro.domain.carrera import (
    Carrera,
    CarreraYaFinalizadaError,
    TaximetroError,
    Tramo,
)
from taximetro.domain.dinero import Money
from taximetro.domain.eventos import (
    CarreraFinalizada,
    CarreraIniciada,
    Estado,
    EstadoCambiado,
)
from taximetro.domain.tarifa import Tarifa, calcular_importe
from taximetro.infrastructure.config import cargar_tarifa
from taximetro.infrastructure.event_bus import EventBus

__all__ = [
    "Carrera",
    "CarreraFinalizada",
    "CarreraIniciada",
    "CarreraYaEnCursoError",
    "CarreraYaFinalizadaError",
    "Estado",
    "EstadoCambiado",
    "EventBus",
    "Money",
    "NoHayCarreraError",
    "ServicioTaximetro",
    "Tarifa",
    "TaximetroError",
    "Tramo",
    "calcular_importe",
    "cargar_tarifa",
]
