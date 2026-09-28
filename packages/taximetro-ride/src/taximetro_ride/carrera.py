"""Carrera — aggregate de ride: nace en parada, avanza por tramos y finaliza."""

from collections.abc import Callable
from datetime import datetime

from taximetro_kernel import Estado, TaximetroError, Tramo

from taximetro_ride.eventos import CarreraFinalizada, CarreraIniciada, EstadoCambiado

Publicador = Callable[[object], None]


class TramoInvalidoError(TaximetroError):
    """El instante debe ser posterior al inicio del tramo en curso."""


class CarreraYaFinalizadaError(TaximetroError):
    """La Carrera ya finalizó: es inmutable."""


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
