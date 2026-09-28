"""Reloj real del sistema."""

from datetime import UTC, datetime


class RelojReal:
    """Reloj de pared del sistema: fechas reales para la Carrera y el histórico."""

    def __call__(self) -> datetime:
        return datetime.now(UTC)
