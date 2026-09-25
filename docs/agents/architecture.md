# Architecture — DDD bounded contexts in a uv monorepo

Canonical sources: `docs/rules_project.md` (clean-architecture principles, Factoria F5
deck), `docs/CLIENT_SPECS.md` (requirements, fases, US table), and the ADRs in `docs/adr/`
(decisions and deliberate deviations).

## Principles (non-negotiable)

1. **Separation of responsibilities** — business logic never mixes with storage or
   interface code.
2. **Independent layers** — the database or web framework can be replaced without
   rewriting the core.
3. **Low coupling** — a change in one part must not force edits across ten files.
4. **Testable code** — pieces are separated precisely so each is testable on its own.

## Monorepo layout

```
stn-taximetro/
├── pyproject.toml                     # uv workspace root — members: apps/*, packages/*, shared/*
├── uv.lock
├── apps/                              # entregables (entry doors) — the composition roots
│   ├── cli/                           # Fases 1–2 — interactive console (src/cli)
│   ├── gui/                           # Fase 3 — Tkinter, tablet-mounted (src/gui)
│   └── api/                           # Fase 4 — FastAPI + fleet web dashboard (src/api)
├── packages/                          # bounded contexts (business)
│   ├── ride/                          # src/ride — carrera lifecycle & vehicle state machine (F1)
│   ├── pricing/                       # src/pricing — tariff engine & financial calculation (F1)
│   ├── identity/                      # src/identity — auth, roles, secure password hashing (F3)
│   ├── fleet/                         # src/fleet — histórico, auditoría, informe de caja (F2)
│   └── tests/                         # src/tests — pytest + Allure suite (imports everything)
└── shared/                            # modules shared across contexts
    ├── shared-kernel/                 # src/shared_kernel — Money, Entity, AggregateRoot,
    │                                  #   ValueObject, DomainEvent, base domain exceptions
    └── shared-libs/                   # src/shared_libs — structured logging, config loader
                                       #   (tarifas.json), in-memory EventBus, security, db
```

Inside every bounded context (`packages/<context>/`):

```
domain/          # entities, value objects, state machines — pure, zero deps
application/     # use cases + ports.py (consumer-owned Protocols)
infrastructure/  # adapters: config readers, repositories, external clients
```

## The four bounded contexts

| Context | Type | Owns | Emits / consumes |
| --- | --- | --- | --- |
| `ride` | Core domain | Carrera lifecycle: `iniciar`, `cambiar_estado` (`parada`/`en_movimiento`), `finalizar`; the vehicle state machine | Emits `CarreraIniciada`, `EstadoCambiado`, `CarreraFinalizada` |
| `pricing` | Core domain | Tariff engine & financial rules: motor de tarifas, cálculo del importe; rates loadable from external config without redeploy (US-07) | Consumes ride events to price carreras |
| `identity` | Supporting | Password auth (Bcrypt/Argon2 hashing), roles & permissions (US-08) | — |
| `fleet` | Analysis / read model | Histórico of finished carreras, auditoría, InformeCaja (US-05). Projection of ride in early fases; relational Read Model in F4 | Consumes ride events |

## Shared layer

- **shared-kernel** — the ubiquitous-language building blocks every context speaks:
  `Money`, `Entity`, `AggregateRoot`, `ValueObject`, `DomainEvent`, and the base domain
  exception hierarchy (`TaximetroError`). Depends on nothing.
- **shared-libs** — business-agnostic technical plumbing: structured logging (US-06),
  config loader (pydantic-settings; `tarifas.json`), in-memory **EventBus** (pub/sub),
  security helpers, DB connection. Depends on nothing business-wise.

## Dependency rules (the iron rules)

1. **Contexts never import contexts.** They communicate only through domain events on
   the EventBus and `shared-kernel` types. No exceptions.
2. **`shared-kernel` and `shared-libs` are leaves** — they import nothing from the
   workspace.
3. **`domain/` imports nothing** from `application/`, `infrastructure/`, or other
   packages.
4. **Ports are consumer-owned**: the Protocol lives in the needing context's
   `application/ports.py`; the adapter lives on the providing side's `infrastructure/`
   and implements it. Swapping an adapter must never touch the consumer.
5. **Apps are the composition roots** — the only place that imports across boundaries
   to wire adapters, subscribe projections to the EventBus, and inject dependencies.
   Constructor injection only; no DI framework.
6. **`packages/tests` may import everything**; nothing imports it.

```
apps/* ──► packages/* ──► shared/*
   │             │
   │             ▼
   │      contexts never import each other
   │      (domain events via EventBus + shared-kernel types)
   └──► wires everything at composition time
```

## SOLID & DRY in this structure

- **S** — one context per reason-to-change: fare regulations → `pricing`; auth rules →
  `identity`; storage technology → `infrastructure` adapters; one layer per
  responsibility (see the layer table in `docs/rules_project.md`).
- **O** — new capabilities extend: a new adapter implements an existing port; a new door
  (`gui`, `api`) reuses the same contexts.
- **L** — adapters are interchangeable because contract tests pin each port's behavior
  (see `testing-tdd.md`).
- **I** — one small port per concern (rate loading, ledger persistence), never a
  god-interface.
- **D** — contexts depend on abstractions (ports, `DomainEvent`), never on another
  context's concrete model.
- **DRY** — a domain rule is stated exactly once, in the context that owns it. Apps
  never re-implement fare math; `fleet` never re-derives the importe (it stores what
  `CarreraFinalizada` carries). Logic earns a place in `shared/` only on its second
  real consumer.

## Fase scaling — contexts are added, never rewritten

- **Fase 1 — MVP (US-01…04, current):** `ride` + `pricing` + `apps/cli` exist. Tariffs
  are hardcoded defaults inside `pricing`'s domain — the meter never knows where rates
  come from.
- **Fase 2 — Observabilidad (US-05…07):** `fleet` appears — subscribes to ride events on
  the EventBus, persists each finished carrera as an immutable `CarreraRegistro` (JSON
  ledger), serves the Histórico and the InformeCaja. `shared-libs` gains structured
  logging; `pricing` externalizes tariffs to `tarifas.json` via the config loader
  (US-07).
- **Fase 3 — Arquitectura y UX (US-08…09):** `identity` appears (secure password
  hashing, roles); `apps/gui` opens as a new door over the same contexts.
- **Fase 4 — Producción:** `fleet`'s ledger migrates to a relational read model behind
  the same port (adapter swap + contract tests, zero consumer changes); `apps/api`
  (FastAPI + fleet dashboard) opens; one-command deploy.

The constant: existing contexts only ever gain use cases or swap adapters — no fase
rewrites another context's domain.

## Collaboration rule (why this matters for agents)

Before writing a change, name the context and the layer it belongs to. If you cannot
place it, stop and ask — don't invent a location. Clean structure + PEP 8 is what lets
human and agent edits land in the right place without stepping on each other.
