# TaxiTech Taxímetro Digital (project `taximetro`, repo `IA-P1-BCN/proyecto_1_juanCarlos_escamilla`)

Digital taximeter prototype for TaxiTech Solutions (TTX-247): a CLI that prices a
*carrera* in real time, growing through 4 delivery fases into observability, a GUI,
and an API + web panel. Requirements live in `docs/CLIENT_SPECS.md`; the clean
architecture rules in `docs/rules_project.md`.

- **Language:** Python 3.12 · **Stack:** uv monorepo (`apps/*`, `packages/*`) · bounded
  contexts as packages: `taximetro-kernel` (shared vocabulary), `taximetro-ride`
  (Carrera lifecycle), `taximetro-billing` (Tarifa/Importe), `taximetro-log`
  (BitacoraJSON, US-06) + `taximetro` (application layer + facade) · app
  `apps/taximetro_cli`: Typer REPL + Textual TUI, texts in `textos.json` (Spanish
  primary)

## Non-negotiables

1. **TDD.** Strict red → green, one vertical slice at a time, tests only at pre-agreed
   seams, tests verify behavior through public interfaces — never production code
   without a failing test first. Details: `docs/agents/testing-tdd.md`.
2. **Python best practices.** PEP 8 enforced by Ruff (format is never debated in
   review). Full standards: `docs/agents/python-standards.md`.
3. **Bounded contexts, one kernel.** Contexts live as workspace packages
   (`taximetro-ride`, `taximetro-billing`) and never import each other — they speak
   through `taximetro-kernel` types (`Tramo`, `Estado`, `Money`) and domain events.
   `taximetro` is the application layer (`ServicioTaximetro`, histórico) and re-exports
   the public API as a facade. The Importe is always derived from the tramos (single
   half-up rounding), never accumulated tick by tick. Apps are presentation only.
   Details: `docs/agents/architecture.md`.

## Commands

```bash
uv sync --all-packages                          # install the workspace
uv run pytest                                   # run the test suite
uv run ruff format . && uv run ruff check .     # format + lint
uv run taximetro-cli                            # run the REPL
uv run taximetro-tui                            # run the TUI
```

Human wrappers for the same commands live in `Taskfile.yml` (`task setup`, `task
check`, `task run`, `task tui`; requires go-task). Agents and CI use the raw uv
commands.

## Agent skills

### Issue tracker

GitHub Issues on `IA-P1-BCN/proyecto_1_juanCarlos_escamilla`: epics are GitHub milestones; stories and tasks are issues inside them. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
