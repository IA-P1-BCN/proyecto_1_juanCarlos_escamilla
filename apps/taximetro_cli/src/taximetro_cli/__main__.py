"""Punto de entrada de módulo: `python -m taximetro_cli` (REPL) · `tui` (TUI)."""

import sys

from taximetro_cli.interfaces.cli import main
from taximetro_cli.interfaces.tui import main as main_tui


def main_dispatch() -> None:
    """Sin argumentos arranca el REPL; `taximetro_cli tui` abre la TUI."""
    if "tui" in sys.argv[1:]:
        sys.argv.remove("tui")
        main_tui()
    else:
        main()


if __name__ == "__main__":
    main_dispatch()
