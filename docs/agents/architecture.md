# Architecture

Layered DDD in one package, simplified on purpose (ADR 0004, supersedes ADR 0001).
All business logic lives in `packages/taximetro`; all presentation in
`apps/taximetro_cli`.

## Layout

```
packages/taximetro/
├── config/tarifas.json       # tarifas vigentes (€/segundo por Estado)
├── src/taximetro/
│   ├── domain/               # Carrera, Tramo, Tarifa, Money, eventos — reglas puras
│   ├── application/          # ServicioTaximetro: iniciar · cambiar_estado · finalizar
│   └── infrastructure/       # config.py (tarifas.json) · event_bus.py (pub/sub)
└── tests/

apps/taximetro_cli/
├── src/taximetro_cli/
│   ├── main.py               # REPL Typer (taximetro-cli) + línea de estado/ticker
│   ├── tui.py                # TUI Textual (taximetro-tui): contador, badge, 1/2/3/q
│   └── textos.json           # todos los textos (español)
└── tests/
```

`interfaces/` y `logs/` del layout objetivo llegan con sus fases: GUI/API como apps
nuevas, logging con US-06.

## Layers and rules

1. **`domain/` is pure** — zero dependencies, no I/O. `Carrera` is the aggregate: a
   list of `Tramo`s (Estado + inicio + fin) between `iniciar` and `finalizar`.
   `calcular_importe(tramos, tarifa, hasta)` derives the Importe with exact `Decimal`
   math and a **single half-up rounding at the end** — never per tramo, never
   accumulated by ticks.
2. **`application/`** — `ServicioTaximetro` owns the turno: one active Carrera, the
   injected clock (`Callable[[], float]`), and the tariff. Raises `NoHayCarreraError`
   / `CarreraYaEnCursoError`.
3. **`infrastructure/`** — `cargar_tarifa()` reads `config/tarifas.json`; `EventBus`
   is an in-memory pub/sub kept as the seam for Fase 2 projections (histórico, logs).
4. **`apps/taximetro_cli` is presentation only** — translates commands/keys into
   `ServicioTaximetro` calls and paints. No business rules, ever. The clock is always
   injected (`crear_app(reloj)` / `crear_tui(reloj)`).

## Domain events

`CarreraIniciada`, `EstadoCambiado`, `CarreraFinalizada` — published through the
injected `publicar` callable onto the EventBus. Fase 2 projections subscribe to them.

## Testing seams (pre-agreed)

1. **Package public API** (`from taximetro import …`) — domain math and service
   behavior with a scripted fake clock.
2. **CLI edge** — Typer `CliRunner` with scripted `input=` + fake clock.
3. **TUI pilot** — Textual `App.run_test()` + `pilot.press` with a fake clock.
