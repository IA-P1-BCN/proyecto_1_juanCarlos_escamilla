"""ServicioTaximetro — el turno: una Carrera activa con reloj y tarifa inyectados."""

from collections.abc import Callable

from taximetro.domain.carrera import Carrera, TaximetroError
from taximetro.domain.dinero import Money
from taximetro.domain.eventos import Estado
from taximetro.domain.tarifa import Tarifa, calcular_importe

Reloj = Callable[[], float]
Publicador = Callable[[object], None]


class NoHayCarreraError(TaximetroError):
    """No hay Carrera en curso: primero iniciar."""


class CarreraYaEnCursoError(TaximetroError):
    """Ya hay una Carrera en curso: finalízala antes de iniciar otra."""


class ServicioTaximetro:
    """Caso de uso del turno: iniciar, cambiar_estado, finalizar; Importe derivado."""

    def __init__(
        self, tarifa: Tarifa, reloj: Reloj, publicar: Publicador | None = None
    ) -> None:
        self._tarifa = tarifa
        self._reloj = reloj
        self._publicar = publicar or (lambda evento: None)
        self._carrera: Carrera | None = None

    @property
    def en_carrera(self) -> bool:
        return self._carrera is not None

    @property
    def estado(self) -> Estado | None:
        return self._carrera.estado if self._carrera else None

    @property
    def importe(self) -> Money:
        """Importe en curso, derivado de los tramos hasta el instante del reloj."""
        if self._carrera is None:
            return Money.cero()
        return calcular_importe(self._carrera.tramos, self._tarifa, hasta=self._reloj())

    def iniciar(self) -> None:
        if self._carrera is not None:
            raise CarreraYaEnCursoError(
                "Ya hay una Carrera en curso: finalízala antes de iniciar otra"
            )
        self._carrera = Carrera(publicar=self._publicar)
        self._carrera.iniciar(ahora=self._reloj())

    def cambiar_estado(self, estado: Estado) -> None:
        self._exigir_carrera().cambiar_estado(estado, ahora=self._reloj())

    def finalizar(self) -> Money:
        carrera = self._exigir_carrera()
        carrera.finalizar(ahora=self._reloj())
        importe = calcular_importe(carrera.tramos, self._tarifa)
        self._carrera = None
        return importe

    def _exigir_carrera(self) -> Carrera:
        if self._carrera is None:
            raise NoHayCarreraError("No hay Carrera en curso")
        return self._carrera
