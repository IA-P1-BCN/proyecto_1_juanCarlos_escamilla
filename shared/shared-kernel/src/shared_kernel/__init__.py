"""Bloques de construcción DDD compartidos (Money, Estado, DomainEvent)."""

from shared_kernel.estado import Estado
from shared_kernel.events import DomainEvent
from shared_kernel.money import Money

__all__ = ["DomainEvent", "Estado", "Money"]
