#!/usr/bin/env bash
# Publish the Fase 1 spec issue and link it from the Fase 1 milestone description.
# Exported 2026-09-25 from the to-spec session (reproduces the spec issue #14 of the
# original jcxk/p1 tracker).
#
# Conventions (docs/agents/issue-tracker.md → Specs): specs are standalone issues
# labelled `spec`, never inside a milestone; the epic's milestone description links
# to them with both forms: `**Spec:** #N — <full url>`.
#
# Idempotent: skips whatever already exists. To reuse for another fase, duplicate
# the file and adjust SPEC_TITLE, MILESTONE_TITLE and the spec body.
# Override the target repo with: REPO=owner/name ./scripts/provision-fase1-spec.sh
set -euo pipefail

REPO="${REPO:-$(git config --get remote.origin.url | sed -E 's#.*github\.com[/:]##; s#\.git$##')}"
SPEC_TITLE="Spec: Fase 1 — MVP Funcional"
MILESTONE_TITLE="Fase 1 — MVP Funcional"

### 1. The `spec` label ######################################################

if gh label list --repo "$REPO" --json name --jq '.[].name' | grep -Fxq spec; then
  echo "= label already exists: spec"
else
  gh label create spec --repo "$REPO" --color 5319E7 \
    --description "Especificación de referencia de una fase/epic" >/dev/null
  echo "+ label created: spec"
fi

### 2. The spec issue ########################################################

spec_number=$(gh issue list --repo "$REPO" --state all --limit 200 --json number,title \
  --jq '.[] | "\(.number)\t\(.title)"' \
  | awk -F'\t' -v t="$SPEC_TITLE" '$2 == t { print $1; exit }' || true)

if [ -n "$spec_number" ]; then
  echo "= spec issue already exists: #$spec_number"
else
  body_file=$(mktemp)
  cat > "$body_file" <<'EOF'
Especificación de referencia de la Fase 1. Fuente de las historias implementables: #1–#4 (milestone `Fase 1 — MVP Funcional`). La spec no pasa por triage (docs/agents/issue-tracker.md → Specs).

## Problema

TaxiTech Solutions lleva desde 2018 con taxímetros físicos Hale T200 sin soporte del fabricante. El taxista necesita arrancar el servicio al inicio del turno, cobrar en tiempo real —con tarifa distinta si el taxi está parado o en movimiento— y cerrar la carrera con el total exacto, sin perder tiempo entre servicios ni depender de hardware que falla.

## Solución

Un CLI en Python que el taxista arranca al inicio del turno: presenta las instrucciones de uso, permite iniciar una carrera con un solo comando, cambiar el estado del vehículo (`parada` / `en_movimiento`) y finalizarla mostrando el Importe total en euros con dos decimales. Las carreras se encadenan sin cerrar el programa. Tarifas vigentes (Zona EMT Madrid): `parada` → 0,02 €/s; `en_movimiento` → 0,05 €/s.

## Historias de usuario

1. Como taxista, quiero iniciar una carrera con un solo comando, para empezar a cobrar desde el momento de arranque.
2. Como taxista, quiero cambiar el estado entre `parada` y `en_movimiento`, para que la tarifa se ajuste a cada tramo.
3. Como taxista, quiero finalizar la carrera y ver el total en euros, para cobrar al pasajero.
4. Como taxista, quiero iniciar otra carrera sin cerrar el programa, para no perder tiempo entre servicios.
5. Como taxista, quiero que al arrancar el sistema me explique cómo usarlo, para no necesitar documentación externa.
6. Como taxista, quiero que el contador siga corriendo —más despacio— con el taxi parado, para no perder importe en semáforos.
7. Como taxista, quiero que el total sea la suma exacta de todos los tramos parado/en movimiento con dos decimales, para cobrar lo justo.

## Decisiones de implementación

- Arquitectura DDD en monorepo uv (docs/agents/architecture.md): esta fase crea `packages/ride` (máquina de estados de la Carrera), `packages/pricing` (motor de tarifas), `apps/cli` (puerta de entrada) y `packages/tests`; `shared/shared-kernel` y `shared/shared-libs` se crean con lo mínimo que esta fase necesite.
- `ride` emite eventos de dominio (`CarreraIniciada`, `EstadoCambiado`, `CarreraFinalizada`); `pricing` calcula el Importe. La composición —inyección y EventBus— vive en `apps/cli` como composition root (ADR 0001).
- Tarifas hardcoded en `pricing` para esta fase; externalizarlas a `tarifas.json` es US-07 (Fase 2).
- El Importe se acumula de forma continua por tramos según el Estado activo y el tiempo transcurrido; el total se muestra con dos decimales.
- El proceso no termina entre carreras: cada nueva Carrera arranca con el acumulador a 0,00 €.
- Vocabulario del glosario (CONTEXT.md): Carrera, Estado (`parada`/`en_movimiento`), Importe, Tarifa.
- Sin persistencia, sin logs, sin GUI, sin autenticación (Fases 2–3).

## Decisiones de testing

- TDD estricto (docs/agents/testing-tdd.md): rojo → verde, una prueba por ciclo vertical, comportamiento solo a través de interfaces públicas, sin mocks de colaboradores internos.
- **Costuras (seams)**, de mayor a menor:
  1. **Borde del CLI** (`apps/cli`): cada historia se prueba como comportamiento observable (comandos → salida), con reloj inyectado para controlar el tiempo.
  2. **Motor de tarifas de `pricing`** (interfaz pública): precisión de las reglas de dinero —acumulación por tramos, redondeo a dos decimales— con duraciones controladas.
- Las pruebas leen como especificación de Carrera/Tarifa y usan el vocabulario del glosario.

## Fuera de alcance

- Histórico/persistencia, logs estructurados, tarifas configurables (Fase 2 — US-05…07).
- Contraseña y GUI (Fase 3 — US-08…09).
- Base de datos, API REST, panel web, despliegue (Fase 4).
- Pagos, facturación e integraciones externas.

## Notas

- Entregables de la fase (CLIENT_SPECS): repo con el código fuente y demo en directo. El tablero kanban está pendiente de recrear (el proyecto GitHub se revertió); decisión aparte.
- Restricción cliente: lenguaje Python; Git y GitHub desde el inicio (cumplido).
EOF
  url=$(gh issue create --repo "$REPO" --title "$SPEC_TITLE" --label spec --body-file "$body_file")
  rm -f "$body_file"
  spec_number="${url##*/}"
  echo "+ spec issue created: $url"
fi

### 3. Link from the milestone description ###################################

ms_number=$(gh api "repos/$REPO/milestones?state=all" --jq '.[] | "\(.number)\t\(.title)"' \
  | awk -F'\t' -v t="$MILESTONE_TITLE" '$2 == t { print $1; exit }' || true)

if [ -z "$ms_number" ]; then
  echo "! milestone not found: $MILESTONE_TITLE" >&2
  exit 1
fi

desc=$(gh api "repos/$REPO/milestones/$ms_number" --jq '.description // ""')

if printf '%s' "$desc" | grep -q '\*\*Spec:\*\*'; then
  echo "= milestone description already links the spec"
else
  gh api --method PATCH "repos/$REPO/milestones/$ms_number" \
    -f description="${desc}

**Spec:** #${spec_number} — https://github.com/${REPO}/issues/${spec_number}" \
    --jq '"+ milestone description updated: \(.title)"'
fi

echo "Provisioning of $SPEC_TITLE against $REPO finished."
