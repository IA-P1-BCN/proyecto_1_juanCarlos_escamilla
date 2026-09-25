"""EventBus — publicador/suscriptor en memoria (Fase 1: síncrono)."""

from collections import defaultdict
from collections.abc import Callable
from typing import Any, TypeVar

from shared_kernel import DomainEvent

E = TypeVar("E", bound=DomainEvent)


class EventBus:
    """Distribuye eventos de dominio a sus suscriptores, en el mismo proceso."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[Callable[[Any], None]]] = (
            defaultdict(list)
        )

    def suscribir(self, tipo: type[E], handler: Callable[[E], None]) -> None:
        self._handlers[tipo].append(handler)

    def publicar(self, evento: DomainEvent) -> None:
        for handler in self._handlers.get(type(evento), []):
            handler(evento)
