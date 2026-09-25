"""Eventos de dominio del contexto ride."""

from dataclasses import dataclass

from shared_kernel import DomainEvent, Estado


@dataclass(frozen=True)
class CarreraIniciada(DomainEvent):
    """La Carrera arrancó: el cobro empieza desde este momento."""


@dataclass(frozen=True)
class EstadoCambiado(DomainEvent):
    """El vehículo pasó a un nuevo Estado; la acumulación sigue su curso."""

    estado: Estado
