#!/usr/bin/env bash
# Publish the Fase 1 tracer-bullet task tickets (T1–T5) with their native blocking chain.
# Exported 2026-09-25 from the to-tickets session (reproduces the task tickets #15–#19
# of the original jcxk/p1 tracker).
#
# Requires the Fase 1 milestone to exist (run scripts/provision-github.sh first).
# Conventions: tickets carry `task` + `enhancement` + `ready-for-agent`, live in the
# Fase 1 milestone, reference their parent story + spec #14, and are chained
# #15 → #16 → #17 → #18 → #19 via native "blocked by" edges.
#
# Idempotent: tickets are found by exact title; blocking edges are only added when
# missing. Override the target repo with: REPO=owner/name ./scripts/provision-fase1-tickets.sh
set -euo pipefail

REPO="${REPO:-$(git config --get remote.origin.url | sed -E 's#.*github\.com[/:]##; s#\.git$##')}"
MILESTONE_TITLE="Fase 1 — MVP Funcional"

TICKET_NUM=""

find_issue_by_title() {
  gh issue list --repo "$REPO" --state all --limit 200 --json number,title \
    --jq '.[] | "\(.number)\t\(.title)"' \
    | awk -F'\t' -v t="$1" '$2 == t { print $1; exit }' || true
}

# $1 = title, $2 = blocker issue number ("" for none); body (without "Blocked by") on stdin
publish_ticket() {
  local title="$1" blocker="$2" num body_file url
  num=$(find_issue_by_title "$title")
  if [ -n "$num" ]; then
    TICKET_NUM="$num"
    echo "= ticket already exists: #$num — $title"
    return 0
  fi
  body_file=$(mktemp)
  cat > "$body_file"
  if [ -n "$blocker" ]; then
    printf '\n## Blocked by\n\n- #%s\n' "$blocker" >> "$body_file"
  else
    printf '\n## Blocked by\n\nNone — can start immediately.\n' >> "$body_file"
  fi
  url=$(gh issue create --repo "$REPO" --title "$title" \
    --label task --label enhancement --label ready-for-agent \
    --milestone "$MILESTONE_TITLE" --body-file "$body_file")
  rm -f "$body_file"
  TICKET_NUM="${url##*/}"
  echo "+ ticket created: $url"
}

ensure_label() {
  if gh label list --repo "$REPO" --json name --jq '.[].name' | grep -Fxq "$1"; then
    echo "= label already exists: $1"
  else
    gh label create "$1" --repo "$REPO" --description "$2" --color "$3" >/dev/null
    echo "+ label created: $1"
  fi
}

wire_block() {
  # $1 = blocked issue, $2 = blocker
  local blocked
  blocked=$(gh api "repos/$REPO/issues/$1" --jq '.issue_dependencies_summary.blocked_by // 0')
  if [ "${blocked:-0}" -gt 0 ]; then
    echo "= #$1 already reports blocked edges"
  else
    gh issue edit "$1" --repo "$REPO" --add-blocked-by "$2" >/dev/null
    echo "+ #$1 blocked by #$2"
  fi
}

### 1. Labels ###############################################################

ensure_label task             "Tarea concreta dentro de una historia"              FBCA04
ensure_label enhancement      "New feature or request"                             A2EEEF
ensure_label ready-for-agent  "Fully specified, ready for an AFK agent"            0E8A16

### 2. Milestone guard ######################################################

ms_number=$(gh api "repos/$REPO/milestones?state=all" --jq '.[] | "\(.number)\t\(.title)"' \
  | awk -F'\t' -v t="$MILESTONE_TITLE" '$2 == t { print $1; exit }' || true)
if [ -z "$ms_number" ]; then
  echo "! milestone not found: $MILESTONE_TITLE — run scripts/provision-github.sh first" >&2
  exit 1
fi
echo "= milestone found: #$ms_number — $MILESTONE_TITLE"

### 3. Tickets (dependency order, blockers first) ###########################

publish_ticket "Task: Walking skeleton — workspace uv + pipeline verde" "" <<'EOF'
## Parent

Spec: #14 · Base común de las historias #1–#4.

## What to build

El andamiaje completo del monorepo uv definido en docs/agents/architecture.md, con el pipeline de calidad en verde: un CLI que arranca y una prueba que atraviesa el camino completo desde packages/tests. Es el rail sobre el que aterrizan el resto de tickets de la Fase 1.

## Acceptance criteria

- [ ] Workspace uv con miembros `apps/cli`, `packages/ride`, `packages/pricing`, `packages/tests` y `shared/shared-kernel` + `shared/shared-libs` (mínimo), según la estructura de architecture.md
- [ ] `uv sync --all-packages` termina sin errores
- [ ] Una prueba trivial en packages/tests arranca el CLI y pasa: `uv run pytest` en verde
- [ ] `uv run ruff format --check .` y `uv run ruff check .` en verde (config de docs/agents/python-standards.md: line-length 88, E/F/I/B/UP, py312)
- [ ] mypy configurado con la política inicial (check_untyped_defs, warn_return_any) y en verde
EOF
T1="$TICKET_NUM"

publish_ticket "Task: Instrucciones al arrancar + iniciar Carrera acumulando en \`parada\`" "$T1" <<'EOF'
## Parent

Historia #1 · Spec: #14

## What to build

Primer camino vertical completo del taxímetro: al arrancar, el CLI explica al taxista cómo usarlo; un solo comando inicia la Carrera y el Importe empieza a acumularse desde 0,00 € a 0,02 €/s con el vehículo en `parada`. Probado a través del borde del CLI con reloj inyectado.

## Acceptance criteria

- [ ] Al arrancar, el sistema muestra las instrucciones de uso sin necesidad de documentación externa
- [ ] Un solo comando inicia la Carrera y el cobro empieza desde el momento de arranque
- [ ] El Importe parte de 0,00 € y se acumula de forma continua según el tiempo en `parada`
- [ ] Tras t segundos en `parada`, el acumulado es exactamente 0,02 × t € (reloj inyectado)
- [ ] ride emite `CarreraIniciada` al iniciar
EOF
T2="$TICKET_NUM"

publish_ticket "Task: Cambiar Estado a \`en_movimiento\` (0,05 €/s por tramo)" "$T2" <<'EOF'
## Parent

Historia #2 · Spec: #14

## What to build

El taxista puede indicar en cualquier momento si el vehículo está `parada` o `en_movimiento`. Cada tramo aplica su Tarifa (parada → 0,02 €/s; en_movimiento → 0,05 €/s) y cambiar de Estado no detiene ni reinicia la acumulación — el contador sigue corriendo, solo más despacio.

## Acceptance criteria

- [ ] El conductor puede indicar en cada momento si el vehículo está parado o en movimiento
- [ ] Cada tramo aplica su tarifa: parada → 0,02 €/s; en_movimiento → 0,05 €/s
- [ ] Cambiar de Estado no detiene la acumulación ni la reinicia
- [ ] Tras t1 s en `parada` + t2 s en `en_movimiento`, el acumulado es 0,02·t1 + 0,05·t2 € (reloj inyectado)
- [ ] ride emite `EstadoCambiado` en cada cambio
EOF
T3="$TICKET_NUM"

publish_ticket "Task: Finalizar y mostrar el Importe con dos decimales" "$T3" <<'EOF'
## Parent

Historia #3 · Spec: #14

## What to build

Un comando finaliza la Carrera y muestra el Importe total a cobrar en euros con dos decimales: la suma exacta de todos los tramos acumulados. La acumulación interna nunca redondea; el redondeo (medio punto hacia arriba) ocurre solo al mostrar. ride emite `CarreraFinalizada` con el Importe.

## Acceptance criteria

- [ ] Un comando cierra la Carrera y muestra el Importe total a cobrar
- [ ] El total se muestra en euros con dos decimales
- [ ] El total es la suma exacta de todos los tramos acumulados parada/en_movimiento
- [ ] Sin redondeo intermedio: 1,5 s en `parada` muestran 0,03 € (0,015 € internos), con reloj inyectado
- [ ] ride emite `CarreraFinalizada` con el Importe final
EOF
T4="$TICKET_NUM"

publish_ticket "Task: Encadenar carreras sin cerrar el programa" "$T4" <<'EOF'
## Parent

Historia #4 · Spec: #14

## What to build

Tras finalizar, el taxista inicia otra Carrera de inmediato sin cerrar el programa: cada nueva Carrera arranca con el acumulador a 0,00 €, sin arrastrar estado de la anterior, y los totales de carreras consecutivas son independientes. El ciclo iniciar → cambiar_estado → finalizar → iniciar se repite indefinidamente.

## Acceptance criteria

- [ ] Tras finalizar, se puede iniciar otra Carrera de inmediato sin cerrar el proceso
- [ ] Cada nueva Carrera arranca con el acumulador a 0,00 €
- [ ] Varias carreras consecutivas producen totales independientes y correctos
- [ ] El programa no se cierra entre carreras
EOF
T5="$TICKET_NUM"

### 4. Blocking chain #######################################################

wire_block "$T2" "$T1"
wire_block "$T3" "$T2"
wire_block "$T4" "$T3"
wire_block "$T5" "$T4"

echo "Provisioning of Fase 1 task tickets against $REPO finished (frontier: #$T1)."
