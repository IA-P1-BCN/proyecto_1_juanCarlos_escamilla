"""EventBus — publicador/suscriptor en memoria."""

from collections import defaultdict
from collections.abc import Callable
from typing import Any, TypeVar

E = TypeVar("E")


class EventBus:
    """Distribuye eventos a los suscriptores por tipo, en el mismo proceso."""

    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable[[Any], None]]] = defaultdict(list)

    def suscribir(self, tipo: type[E], handler: Callable[[E], None]) -> None:
        self._handlers[tipo].append(handler)

    def publicar(self, evento: object) -> None:
        for handler in self._handlers.get(type(evento), []):
            handler(evento)
