"""Eventos de dominio del contexto ride."""

from dataclasses import dataclass

from shared_kernel import DomainEvent


@dataclass(frozen=True)
class CarreraIniciada(DomainEvent):
    """La Carrera arrancó: el cobro empieza desde este momento."""
