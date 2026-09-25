# 0002 — Fleet is an event-driven projection of ride

## Status

accepted (2026-09-25)

## Decision

`fleet` never queries ride's aggregates. `ride` publishes domain events
(`CarreraIniciada`, `EstadoCambiado`, `CarreraFinalizada`) on the in-memory EventBus;
`fleet` subscribes and maintains its own model — the immutable `CarreraRegistro`
(fecha, duración, importe) — in a JSON ledger, migrating to a relational read model in
Fase 4 behind the same port.

Why: "carrera" means a mutable lifecycle in ride and a frozen fact in fleet — the same
word with two models, which is the DDD signal for separate contexts joined by a
contract, not a shared class.

## Considered options

- **fleet imports ride's `Carrera`**: rejected — couples the ledger to the meter's model
  and forces the projection to track live state it must not own.
- **Synchronous call ride → fleet on finalizar**: rejected — same coupling, and harder
  to grow (pricing listens to the same events).
