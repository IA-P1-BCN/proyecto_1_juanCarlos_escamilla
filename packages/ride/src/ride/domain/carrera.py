"""Carrera — aggregate root de ride: se inicia, cambia de estado y finaliza."""

from ride.application.ports import PublicadorEventos
from ride.domain.eventos import CarreraIniciada, EstadoCambiado
from shared_kernel import Estado, Money


class Carrera:
    """El servicio de taxi: nace al iniciar y acumula el Importe hasta finalizar."""

    def __init__(self, publicador: PublicadorEventos) -> None:
        self._publicador = publicador
        self._estado: Estado | None = None
        self._instante_inicio: float | None = None
        self._importe = Money.cero()

    @property
    def estado(self) -> Estado | None:
        return self._estado

    @property
    def importe(self) -> Money:
        return self._importe

    def iniciar(self, ahora: float) -> None:
        """Arranca la Carrera en `parada`; el cobro empieza desde `ahora`."""
        self._estado = Estado.PARADA
        self._instante_inicio = ahora
        self._publicador.publicar(CarreraIniciada(momento=ahora))

    def cambiar_estado(self, estado: Estado, ahora: float) -> None:
        """Pasa el vehículo a `estado`; no detiene ni reinicia la acumulación."""
        self._estado = estado
        self._publicador.publicar(EstadoCambiado(momento=ahora, estado=estado))

    def acumular(self, importe: Money) -> None:
        """Suma al Importe de la Carrera el importe calculado por pricing."""
        self._importe = self._importe.mas(importe)
