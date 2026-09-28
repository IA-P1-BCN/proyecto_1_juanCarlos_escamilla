# Architecture

Bounded contexts as workspace packages with a minimal shared kernel (ADR 0005, which
keeps ADR 0004's tramo model and single-derivation Importe). The app depends only on
the `taximetro` facade.

## Layout

```
packages/
├── taximetro-kernel/            # vocabulario común: Money, Estado, Tramo, EventBus, errores
│   └── src/taximetro_kernel/
├── taximetro-ride/              # contexto ride: Carrera + eventos del ciclo de vida
│   └── src/taximetro_ride/
├── taximetro-billing/           # contexto billing: Tarifa, calcular_importe, config/tarifas.json
│   └── src/taximetro_billing/
└── taximetro/                   # capa de aplicación: ServicioTaximetro + histórico (fachada)
    ├── src/taximetro/
    │   ├── application/         # servicio.py — el turno, reloj inyectado, guarda registro
    │   ├── domain/              # registro.py — CarreraRegistro (proyección del histórico)
    │   └── infrastructure/      # historico.py — HistoricoJson (data/historico.json)
    └── tests/

apps/taximetro_cli/              # solo presentación: REPL Typer + TUI Textual + textos.json
```

## Rules

1. **Contexts never import contexts.** `taximetro-ride` and `taximetro-billing` speak
   only through `taximetro-kernel` types (`Tramo`, `Estado`, `Money`) and domain events.
   The kernel imports nothing from the workspace.
2. **The Importe is always derived** from the tramos (`calcular_importe`) with exact
   `Decimal` math and a single half-up rounding at the end — never accumulated by ticks.
3. **`taximetro` is the application layer** — `ServicioTaximetro` orchestrates the turno
   and owns the histórico port (`RepositorioHistorico`). Its `__init__` re-exports the
   composed public API so `apps/*` import everything from `taximetro` alone.
4. **Apps are presentation only** — REPL/TUI translate commands/keys into service calls
   and paint. The clock is always injected (`crear_app(reloj)` / `crear_tui(reloj)`).
5. **billing owns `config/tarifas.json`** (US-07); the histórico JSON lives under
   `packages/taximetro/data/` (gitignored, file-first — BD in Fase 4).

## Testing seams (pre-agreed)

1. **Package public APIs** (`taximetro_ride`, `taximetro_billing`, `taximetro`) —
   behavior with a scripted fake clock; billing tests build kernel `Tramo`s directly.
2. **CLI edge** — Typer `CliRunner` with scripted `input=` + fake clock.
3. **TUI pilot** — Textual `App.run_test()` + `pilot.press` with a fake clock.
