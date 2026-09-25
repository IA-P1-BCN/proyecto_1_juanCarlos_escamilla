# 0001 — Monorepo layout and port ownership

## Status

accepted (2026-09-25)

## Decision

The taximeter system (TTX-247) is a uv workspace monorepo with four DDD bounded contexts
in `packages/` (`ride`, `pricing`, `identity`, `fleet`), a shared layer in `shared/`
(`shared-kernel` building blocks, `shared-libs` technical plumbing), and deliverables in
`apps/` (`cli`, `gui`, `api`). Contexts never import each other: they integrate through
domain events on the in-memory EventBus (`shared-libs`) and `shared-kernel` types only.
Ports are consumer-owned: the Protocol lives in the needing context's
`application/ports.py`, the adapter in the providing side's `infrastructure/`, and
contract tests pin every port so adapters stay swappable.

## Considered options

- **Single `core` context** (earlier draft of this project): rejected — "carrera" means a
  mutable lifecycle to the meter and an immutable record to reporting; one model would
  couple both, and money rules would leak into the meter.
- **Standalone `persistence` package** (earlier draft): rejected — adapters live inside
  each context's `infrastructure/`, next to the domain they serve.
- **Ports owned by the provider**: rejected — consumer-owned ports keep the dependency
  arrow pointing at the abstraction and make adapters drop-in swappable.

## Consequences

Deliberately deviates from `docs/rules_project.md` (the deck): the `interfaces/` layer
becomes `apps/*`, and `tarifas.json` lives inside `pricing`'s `infrastructure/` instead
of a root `config/`. Adding a capability = new bounded context; swapping storage = new
adapter + contract tests.
