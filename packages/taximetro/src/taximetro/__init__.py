"""Taxímetro — capa de aplicación: el turno (ServicioTaximetro) y el histórico.

Fachada: reexporta el API público que compone (kernel + ride + billing + log) para
que la app dependa solo de este paquete.
"""

from taximetro_billing import Tarifa, calcular_importe, cargar_tarifa
from taximetro_kernel import Estado, EventBus, Money, TaximetroError, Tramo
from taximetro_log import BitacoraJSON
from taximetro_ride import (
    Carrera,
    CarreraFinalizada,
    CarreraIniciada,
    CarreraYaFinalizadaError,
    EstadoCambiado,
)

from taximetro.application.bitacora import registrar_eventos
from taximetro.application.servicio import (
    CarreraYaEnCursoError,
    NoHayCarreraError,
    RepositorioHistorico,
    ServicioTaximetro,
)
from taximetro.domain.registro import CarreraRegistro
from taximetro.infrastructure.historico import HistoricoJson

__all__ = [
    "BitacoraJSON",
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
    "registrar_eventos",
]
