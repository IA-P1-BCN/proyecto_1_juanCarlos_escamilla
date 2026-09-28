"""ServicioTaximetro — el turno: una Carrera activa con reloj y tarifa inyectados."""

from collections.abc import Callable
from datetime import date, datetime
from typing import Protocol

from taximetro_billing import Tarifa, calcular_importe
from taximetro_kernel import Estado, Money, TaximetroError
from taximetro_ride import Carrera

from taximetro.domain.registro import CarreraRegistro

Reloj = Callable[[], datetime]
Publicador = Callable[[object], None]


class RepositorioHistorico(Protocol):
    """Puerto del histórico: lo implementa la infraestructura (JSON hoy)."""

    def guardar(self, registro: CarreraRegistro) -> None: ...

    def del_dia(self, dia: date) -> list[CarreraRegistro]: ...


class NoHayCarreraError(TaximetroError):
    """No hay Carrera en curso: primero iniciar."""


class CarreraYaEnCursoError(TaximetroError):
    """Ya hay una Carrera en curso: finalízala antes de iniciar otra."""


class ServicioTaximetro:
    """Caso de uso del turno: iniciar, cambiar_estado, finalizar; Importe derivado."""

    def __init__(
        self,
        tarifa: Tarifa,
        reloj: Reloj,
        publicar: Publicador | None = None,
        historico: RepositorioHistorico | None = None,
    ) -> None:
        self._tarifa = tarifa
        self._reloj = reloj
        self._publicar = publicar or (lambda evento: None)
        self._historico = historico
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
        ahora = self._reloj()
        carrera.finalizar(ahora=ahora)
        importe = calcular_importe(carrera.tramos, self._tarifa)
        if self._historico is not None:
            inicio = carrera.tramos[0].inicio
            self._historico.guardar(
                CarreraRegistro(
                    inicio=inicio,
                    duracion_segundos=(ahora - inicio).total_seconds(),
                    importe=importe,
                )
            )
        self._carrera = None
        return importe

    def historial_del_dia(self, dia: date) -> list[CarreraRegistro]:
        """Carreras finalizadas de `dia`, para cuadrar caja (#5)."""
        if self._historico is None:
            return []
        return self._historico.del_dia(dia)

    def _exigir_carrera(self) -> Carrera:
        if self._carrera is None:
            raise NoHayCarreraError("No hay Carrera en curso")
        return self._carrera
