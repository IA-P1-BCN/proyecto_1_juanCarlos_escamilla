#!/usr/bin/env bash
# Genera docs/assets/demo-taximetro.gif: graba la sesión TUI con el driver pty
# (scripts/demo-tui-driver.py — terminal + `task run-tui` + teclas 1/2/3/q) y
# renderiza el GIF con agg.
#
# Uso: scripts/demo-gif.sh
# Requisitos: task (compila/arranca), agg (brew install agg).
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"

GIF="docs/assets/demo-taximetro.gif"
CAST="$(mktemp -t demo-tui)"
CAST="${CAST}.cast"
trap 'rm -f "$CAST"' EXIT

command -v task >/dev/null || { echo "✗ Falta task (go-task): brew install go-task" >&2; exit 1; }
command -v agg >/dev/null || { echo "✗ Falta agg (renderizador de GIF): brew install agg" >&2; exit 1; }

echo "→ Grabando la sesión TUI (~20s)..."
python3 scripts/demo-tui-driver.py "$CAST"

echo "→ Renderizando $GIF..."
agg "$CAST" "$GIF" --theme dracula --font-size 20 --idle-time-limit 5 \
    --last-frame-duration 2

echo "✓ Demo generada: $GIF"
