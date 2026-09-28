# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y
[SemVer](https://semver.org/lang/es/). Cada merge `dev → stg` genera la etiqueta
`v<versión>` (leída de `pyproject.toml`); cada merge `stg → main` publica la Release.

## [0.1.0] — 2026-09-28

Primera versión del taxímetro digital (TTX-247): Fases 1 y 2 completas.

### Fase 1 — MVP Funcional

- Carrera por tramos con Importe derivado y un único redondeo half-up: `iniciar`,
  `estado parada|en_movimiento`, `finalizar`, encadenar carreras sin cerrar el
  programa y guardas de turno (#16–#19)
- TUI del conductor a pantalla completa (Textual): contador grande en tiempo real,
  badge de Estado, toasts y teclas 1/2/3/q
- REPL clásico de comandos (`taximetro-cli`) con línea de estado siempre visible

### Fase 2 — Observabilidad y Persistencia

- Histórico de carreras del día persistido en JSON y consultable con `historial`
  para cuadrar caja (#5)
- Bitácora de operación en JSON-lines rotativo: arranque, cambios de Estado, cierre
  de Carrera y errores (#6)
- Tarifas configurables en `config/tarifas.json` sin tocar código (#7)

### Arquitectura

- Monorepo uv con contextos delimitados como paquetes: `taximetro-kernel`
  (vocabulario común), `taximetro-ride`, `taximetro-billing`, `taximetro-log` y
  `taximetro` como capa de aplicación/fachada (ADR 0004, ADR 0005)
- Presentación en capas dentro de la app: `interfaces/` (cli, tui) e
  `infrastructure/` (composition root, reloj, textos)
- Eventos de dominio en el EventBus como costura para proyecciones futuras

### Tooling

- Workspace uv con Taskfile (`setup`, `bin`, `run-tui`, `check`…), pre-commit
  (ruff + higiene) y CI de PRs: ruff + mypy + pytest
- Binario nativo autocontenido con PyInstaller (`task bin` → `bin/taximetro`)
- Demo GIF de la TUI regenerable con `scripts/demo-gif.sh`
- Tablero de Fases: [0.1.0] completa Fases 1 y 2 (🟢🟢)
