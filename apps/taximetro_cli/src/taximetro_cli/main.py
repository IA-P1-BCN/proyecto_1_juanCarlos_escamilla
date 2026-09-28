"""Puntos de entrada del taxímetro: `taximetro-cli` (REPL) y `taximetro-tui` (TUI)."""

from taximetro_cli.interfaces.cli import main
from taximetro_cli.interfaces.tui import main as main_tui

__all__ = ["main", "main_tui"]
