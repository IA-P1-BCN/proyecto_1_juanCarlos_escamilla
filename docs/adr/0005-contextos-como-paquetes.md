# 0005 — Contextos delimitados como paquetes del workspace

## Status

accepted (2026-09-28) — matiza 0004 (mantiene tramos y derivación única; sustituye su
"un solo paquete")

## Decision

La lógica se reparte en paquetes del workspace por contexto delimitado:
`taximetro-kernel` (vocabulario común: Money, Estado, Tramo, EventBus, errores),
`taximetro-ride` (Carrera y su ciclo de vida), `taximetro-billing` (Tarifa e Importe,
propietario de `config/tarifas.json`) y `taximetro` como capa de aplicación
(ServicioTaximetro + histórico) que **reexporta el API público como fachada**: la app
depende solo de `taximetro`. Los contextos nunca se importan entre sí — hablan a través
del kernel (Tramo/Estado) y de eventos de dominio.

## Considered options

- **Un solo paquete (0004)**: funcionó para el MVP, pero el histórico (#5) ya añadió una
  proyección y Fase 3/4 traen auth y API — los contextos vuelven a pagar su sitio.
- **Contextos + capa shared/ (0001)**: rechazado de nuevo — 6 miembros para un taxímetro;
  el kernel mínimo (4 módulos) cubre lo que ride y billing comparten de verdad.
- **billing lee los tramos por suscripción de eventos**: rechazado — obliga a acumular
  estado espejo; leer los Tramo inmutables del kernel es derivación pura (sin estado).

## Consequences

El Tramo vive en el kernel como contrato de integración entre ride (lo produce) y
billing (lo tarifica). Añadir un contexto nuevo = paquete nuevo; la app no cambia sus
imports mientras la fachada los reexporte.
