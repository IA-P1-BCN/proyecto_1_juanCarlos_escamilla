"""Carrera — aggregate: nace en parada, avanza por tramos y finaliza."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from taximetro.domain.eventos import (
    CarreraFinalizada,
    CarreraIniciada,
    Estado,
    EstadoCambiado,
)

Publicador = Callable[[object], None]


class TaximetroError(Exception):
    """Fallo de las reglas del taxímetro."""


class TramoInvalidoError(TaximetroError):
    """El instante debe ser posterior al inicio del tramo en curso."""


class CarreraYaFinalizadaError(TaximetroError):
    """La Carrera ya finalizó: es inmutable."""


@dataclass(frozen=True)
class Tramo:
    """Trecho de Carrera en un Estado; fin=None mientras está en curso."""

    estado: Estado
    inicio: datetime
    fin: datetime | None = None


class Carrera:
    """El servicio de taxi: una lista de Tramos entre iniciar y finalizar."""

    def __init__(self, publicar: Publicador) -> None:
        self._publicar = publicar
        self._tramos: list[Tramo] = []
        self._finalizada = False

    @property
    def tramos(self) -> tuple[Tramo, ...]:
        return tuple(self._tramos)

    @property
    def estado(self) -> Estado | None:
        return self._tramos[-1].estado if self._tramos else None

    def iniciar(self, ahora: datetime) -> None:
        """Nace la Carrera en parada; el cobro corre desde `ahora`."""
        self._tramos = [Tramo(estado=Estado.PARADA, inicio=ahora)]
        self._finalizada = False
        self._publicar(CarreraIniciada(momento=ahora))

    def cambiar_estado(self, estado: Estado, ahora: datetime) -> None:
        """Cierra el tramo en curso y abre otro con el nuevo Estado."""
        self._exigir_abierta(ahora)
        if estado is self.estado:
            return
        self._cerrar_tramo(ahora)
        self._tramos.append(Tramo(estado=estado, inicio=ahora))
        self._publicar(EstadoCambiado(momento=ahora, estado=estado))

    def finalizar(self, ahora: datetime) -> None:
        """Cierra el último tramo; la Carrera queda inmutable."""
        self._exigir_abierta(ahora)
        self._cerrar_tramo(ahora)
        self._finalizada = True
        self._publicar(CarreraFinalizada(momento=ahora))

    def _exigir_abierta(self, ahora: datetime) -> None:
        if self._finalizada:
            raise CarreraYaFinalizadaError("la Carrera ya finalizó")
        if ahora < self._tramos[-1].inicio:
            raise TramoInvalidoError(
                "el instante debe ser posterior al inicio del tramo"
            )

    def _cerrar_tramo(self, ahora: datetime) -> None:
        ultimo = self._tramos[-1]
        self._tramos[-1] = Tramo(estado=ultimo.estado, inicio=ultimo.inicio, fin=ahora)
