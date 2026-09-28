"""Taxímetro — lógica de negocio: Carrera por tramos, Tarifa, Importe."""

from taximetro.application.servicio import (
    CarreraYaEnCursoError,
    NoHayCarreraError,
    RepositorioHistorico,
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
from taximetro.domain.registro import CarreraRegistro
from taximetro.domain.tarifa import Tarifa, calcular_importe
from taximetro.infrastructure.config import cargar_tarifa
from taximetro.infrastructure.event_bus import EventBus
from taximetro.infrastructure.historico import HistoricoJson

__all__ = [
    "Carrera",
    "CarreraFinalizada",
    "CarreraIniciada",
    "CarreraRegistro",
    "CarreraYaEnCursoError",
    "CarreraYaFinalizadaError",
    "Estado",
    "EstadoCambiado",
    "EventBus",
    "HistoricoJson",
    "Money",
    "NoHayCarreraError",
    "RepositorioHistorico",
    "ServicioTaximetro",
    "Tarifa",
    "TaximetroError",
    "Tramo",
    "calcular_importe",
    "cargar_tarifa",
]
