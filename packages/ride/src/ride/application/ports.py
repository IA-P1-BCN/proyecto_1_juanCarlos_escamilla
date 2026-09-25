"""Ports del contexto ride — propiedad del consumidor (ADR 0001)."""

from typing import Protocol

from shared_kernel import DomainEvent


class PublicadorEventos(Protocol):
    """Lo que ride necesita de cualquier bus de eventos; lo implementa shared-libs."""

    def publicar(self, evento: DomainEvent) -> None: ...
