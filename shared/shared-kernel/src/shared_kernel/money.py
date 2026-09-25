"""Money — importe en euros como céntimos enteros (value object)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """Importe en euros; se representa en céntimos para que el dinero sea exacto."""

    centimos: int

    @classmethod
    def cero(cls) -> "Money":
        return cls(centimos=0)

    def mas(self, otro: "Money") -> "Money":
        return Money(centimos=self.centimos + otro.centimos)

    def formato(self) -> str:
        """Devuelve el importe en euros con dos decimales, formato español."""
        euros, resto = divmod(self.centimos, 100)
        return f"{euros},{resto:02d} €"
