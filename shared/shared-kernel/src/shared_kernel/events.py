"""DomainEvent — base de los eventos de dominio que viajan por el EventBus."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DomainEvent:
    """Evento de dominio; `momento` es el instante en que ocurrió (reloj inyectado)."""

    momento: float
