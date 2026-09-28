"""Helpers compartidos por los tests de la app: reloj falso y horas."""

from datetime import UTC, datetime


def hora(h: int, m: int = 0, s: int = 0, ms: int = 0) -> datetime:
    return datetime(2026, 9, 28, h, m, s, ms, tzinfo=UTC)


class RelojFalso:
    """Doble de prueba: devuelve instantes guiñados uno a uno (reloj inyectado)."""

    def __init__(self, instantes: list[datetime]) -> None:
        self._instantes = instantes
        self._indice = 0

    def __call__(self) -> datetime:
        instante = self._instantes[min(self._indice, len(self._instantes) - 1)]
        self._indice += 1
        return instante
