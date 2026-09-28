# 0004 — Simplificación: un paquete `taximetro` con capas DDD

## Status

accepted (2026-09-28) — supersede 0001

## Decision

El workspace se reduce a `packages/taximetro` (toda la lógica de negocio, cero
dependencias, capas `domain/` `application/` `infrastructure/`) y `apps/taximetro_cli`
(solo presentación: REPL Typer + TUI Textual, textos en `textos.json`). Desaparecen los
cuatro contextos delimitados y la capa `shared/` de ADR 0001: el proyecto prioriza la
simplicidad máxima — entender el código en un vistazo — sobre el aislamiento entre
contextos que las fases futuras aún no necesitan. El modelo pasa a **Carrera por tramos
con Importe derivado una sola vez** (half-up), y las tarifas viven en
`config/tarifas.json`.

## Considered options

- **Mantener los 4 contextos + shared/**: rechazado — coste cognitivo y archivos que un
  MVP de una sola Carrera no amortiza; `docs/rules_project.md` (el deck) prescribe el
  layout por capas que ahora volvemos a seguir.
- **Tramos con derivación única vs acumulador incremental**: elegidos los tramos —
  eliminan el dance settle-then-switch, hacen exacto el redondeo (único, al final) y
  dan `finalizar` y la futura recuperación tras reinicio gratis.

## Consequences

Los eventos de dominio y el EventBus se conservan (en proceso) como costura para las
proyecciones futuras (histórico, logs). Si la complejidad de Fase 4 (API + panel) lo
exige, separar contextos de nuevo será una extracción desde un modelo ya probado.
