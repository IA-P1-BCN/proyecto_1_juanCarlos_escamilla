#!/usr/bin/env bash
# Provision the GitHub state of this repo (exported 2026-09-24 from the setup session):
#   1. the `story` / `task` labels
#   2. the 4 Fase milestones (epics)
#   3. the 13 story issues, with acceptance criteria derived from docs/CLIENT_SPECS.md
#
# Flow convention (docs/agents/issue-tracker.md): an epic is a GitHub milestone;
# stories and tasks are labelled issues inside the milestone of their epic.
#
# Idempotent: anything that already exists (by exact title) is skipped, so the
# script is safe to re-run. Override the target repo with: REPO=owner/name ./scripts/provision-github.sh
set -euo pipefail

REPO="${REPO:-$(git config --get remote.origin.url | sed -E 's#.*github\.com[/:]##; s#\.git$##')}"

label_exists() {
  gh label list --repo "$REPO" --json name --jq '.[].name' | grep -Fxq "$1"
}

ensure_label() {
  # $1 name, $2 description, $3 color
  if label_exists "$1"; then
    echo "= label already exists: $1"
  else
    gh label create "$1" --repo "$REPO" --description "$2" --color "$3" >/dev/null
    echo "+ label created: $1"
  fi
}

milestone_exists() {
  gh api "repos/$REPO/milestones?state=all" --jq '.[].title' | grep -Fxq "$1"
}

ensure_milestone() {
  # $1 title, $2 description
  if milestone_exists "$1"; then
    echo "= milestone already exists: $1"
  else
    gh api "repos/$REPO/milestones" -f title="$1" -f description="$2" --jq '"+ milestone created: \(.title) (#\(.number))"'
  fi
}

issue_exists() {
  gh issue list --repo "$REPO" --state all --limit 200 --json title --jq '.[].title' | grep -Fxq "$1"
}

ensure_issue() {
  # $1 title, $2 milestone title; body on stdin
  if issue_exists "$1"; then
    echo "= issue already exists: $1"
  else
    gh issue create --repo "$REPO" --title "$1" --label story --milestone "$2" --body-file -
  fi
}

### 1. Labels ###############################################################

ensure_label story "Historia de usuario dentro de una fase (milestone)" 1D76DB
ensure_label task  "Tarea concreta dentro de una historia"              FBCA04

# Optional: the five triage labels used by /triage (docs/agents/triage-labels.md).
# Uncomment to create them.
# ensure_label needs-triage      "Maintainer needs to evaluate this issue"  D4C5F9
# ensure_label needs-info        "Waiting on reporter for more information" FBCA04
# ensure_label ready-for-agent   "Fully specified, ready for an AFK agent"  0E8A16
# ensure_label ready-for-human   "Requires human implementation"            F9D0C4
# ensure_label wontfix           "Will not be actioned"                     FFFFFF

### 2. Milestones (= epics) #################################################

ensure_milestone "Fase 1 — MVP Funcional" \
  "CLI operativo que cubre el flujo completo de una carrera (US-01 a US-04). El cliente valida la lógica de tarifas antes de avanzar. Tarifas vigentes: parado o <20 km/h → 0,02 €/s; en movimiento → 0,05 €/s."

ensure_milestone "Fase 2 — Observabilidad y Persistencia" \
  "Sistema auditable y datos que sobreviven al cierre: logs estructurados, histórico en disco, tarifas por fichero de configuración (US-05 a US-07). Transversal: la lógica de cálculo de tarifas debe quedar cubierta por tests automatizados (req. 4)."

ensure_milestone "Fase 3 — Arquitectura y Experiencia de Usuario" \
  "Refactorización y experiencia de usuario: OO con responsabilidades delimitadas, contraseña segura, GUI para tablet no bloqueante (US-08 y US-09). Transversal: refactorización estructural OO con responsabilidades claras por componente (req. 1)."

ensure_milestone "Fase 4 — Versión de Producción" \
  "Del prototipo al despliegue: histórico en BD relacional, API REST, panel web y despliegue con un solo comando."

### 3. Story issues #########################################################

ensure_issue "US-01: Iniciar carrera con un solo comando" "Fase 1 — MVP Funcional" <<'EOF'
Como taxista, quiero iniciar una carrera con un solo comando para empezar a cobrar desde el momento de arranque.

**Prioridad (MoSCoW):** Must
**Epic (milestone):** Fase 1 — MVP Funcional
**Fuente:** docs/CLIENT_SPECS.md → Historias de Usuario + Fase 1

## Criterios de aceptación

- [ ] Un solo comando inicia la carrera y el cobro empieza desde el momento de arranque
- [ ] Al arrancar, el sistema explica al conductor cómo usarlo sin necesidad de documentación externa
- [ ] El importe parte de 0,00 € y se acumula de forma continua según el estado activo y el tiempo transcurrido
EOF

ensure_issue "US-02: Cambiar estado entre parado y en movimiento" "Fase 1 — MVP Funcional" <<'EOF'
Como taxista, quiero cambiar el estado entre "parado" y "en movimiento" para que la tarifa se ajuste.

**Prioridad (MoSCoW):** Must
**Epic (milestone):** Fase 1 — MVP Funcional
**Fuente:** docs/CLIENT_SPECS.md → Historias de Usuario + Fase 1

## Criterios de aceptación

- [ ] El conductor puede indicar en cada momento si el vehículo está parado o en movimiento
- [ ] Tarifa por tramo: parado o <20 km/h → 0,02 €/s; en movimiento → 0,05 €/s
- [ ] El contador sigue corriendo con el taxi parado, solo más despacio; cambiar de estado no detiene la acumulación
EOF

ensure_issue "US-03: Finalizar la carrera y ver el total en euros" "Fase 1 — MVP Funcional" <<'EOF'
Como taxista, quiero finalizar la carrera y ver el total en euros para cobrar al pasajero.

**Prioridad (MoSCoW):** Must
**Epic (milestone):** Fase 1 — MVP Funcional
**Fuente:** docs/CLIENT_SPECS.md → Historias de Usuario + Fase 1

## Criterios de aceptación

- [ ] Un comando cierra la carrera y muestra el importe total a cobrar
- [ ] El total se muestra en euros con dos decimales
- [ ] El total es la suma de todos los tramos acumulados parado/en movimiento
EOF

ensure_issue "US-04: Iniciar otra carrera sin cerrar el programa" "Fase 1 — MVP Funcional" <<'EOF'
Como taxista, quiero poder iniciar otra carrera sin cerrar el programa para no perder tiempo entre servicios.

**Prioridad (MoSCoW):** Must
**Epic (milestone):** Fase 1 — MVP Funcional
**Fuente:** docs/CLIENT_SPECS.md → Historias de Usuario + Fase 1

## Criterios de aceptación

- [ ] Tras finalizar, se puede iniciar otra carrera de inmediato sin cerrar el proceso
- [ ] Cada nueva carrera arranca con el acumulador a 0,00 €
EOF

ensure_issue "US-05: Histórico de carreras del día para cuadrar caja" "Fase 2 — Observabilidad y Persistencia" <<'EOF'
Como responsable de flota, quiero ver el histórico de carreras del día para cuadrar caja.

**Prioridad (MoSCoW):** Should
**Epic (milestone):** Fase 2 — Observabilidad y Persistencia
**Fuente:** docs/CLIENT_SPECS.md → Historias de Usuario + Fase 2

## Criterios de aceptación

- [ ] Al finalizar cada carrera se guardan fecha, duración e importe de forma permanente
- [ ] Escritura incremental en disco; disponible en la siguiente sesión sin ninguna acción manual
- [ ] Se puede consultar el histórico de carreras del día para cuadrar caja
EOF

ensure_issue "US-06: Logs de operación para diagnosticar errores" "Fase 2 — Observabilidad y Persistencia" <<'EOF'
Como técnico, quiero que el sistema genere logs de operación para diagnosticar errores en producción.

**Prioridad (MoSCoW):** Should
**Epic (milestone):** Fase 2 — Observabilidad y Persistencia
**Fuente:** docs/CLIENT_SPECS.md → Historias de Usuario + Fase 2

## Criterios de aceptación

- [ ] Se registran arranque, cambios de estado, cierre de carrera y errores
- [ ] Log estructurado, accesible para el equipo técnico sin intervenir el proceso en ejecución
EOF

ensure_issue "US-07: Cambiar tarifas por fichero de configuración" "Fase 2 — Observabilidad y Persistencia" <<'EOF'
Como técnico, quiero poder cambiar las tarifas en un fichero de configuración sin redeployar.

**Prioridad (MoSCoW):** Should
**Epic (milestone):** Fase 2 — Observabilidad y Persistencia
**Fuente:** docs/CLIENT_SPECS.md → Historias de Usuario + Fase 2

## Criterios de aceptación

- [ ] Las tarifas se modifican editando un fichero de configuración externo
- [ ] No hay que tocar el código ni redeployar para actualizar tarifas
EOF

ensure_issue "US-08: Contraseña para proteger el sistema" "Fase 3 — Arquitectura y Experiencia de Usuario" <<'EOF'
Como responsable de flota, quiero que el sistema requiera contraseña para protegerlo de manipulaciones.

**Prioridad (MoSCoW):** Could
**Epic (milestone):** Fase 3 — Arquitectura y Experiencia de Usuario
**Fuente:** docs/CLIENT_SPECS.md → Historias de Usuario + Fase 3

## Criterios de aceptación

- [ ] El acceso a la aplicación está protegido por contraseña
- [ ] Credenciales almacenadas de forma segura: ningún valor sensible en texto plano
EOF

ensure_issue "US-09: Interfaz visual con botones grandes (móvil/tablet)" "Fase 3 — Arquitectura y Experiencia de Usuario" <<'EOF'
Como taxista, quiero una interfaz visual con botones grandes para usarlo fácilmente con el móvil o tablet.

**Prioridad (MoSCoW):** Could
**Epic (milestone):** Fase 3 — Arquitectura y Experiencia de Usuario
**Fuente:** docs/CLIENT_SPECS.md → Historias de Usuario + Fase 3

## Criterios de aceptación

- [ ] GUI funcional en tablet: botones grandes e interacción táctil cómoda
- [ ] Estado del taxi visible de un vistazo; importe actualizado en tiempo real
- [ ] La interfaz no se bloquea en ningún momento durante el uso
EOF

ensure_issue "US-10: Histórico de carreras en base de datos relacional" "Fase 4 — Versión de Producción" <<'EOF'
**Historia propuesta** (no hay fila US en la especificación; derivada de los requisitos funcionales de la Fase 4).

El histórico de carreras debe almacenarse en una base de datos que garantice integridad y permita consultas estructuradas.

**Epic (milestone):** Fase 4 — Versión de Producción
**Fuente:** docs/CLIENT_SPECS.md → Fase 4, req. 1

## Criterios de aceptación

- [ ] El histórico migra de fichero plano a base de datos relacional
- [ ] La base de datos garantiza integridad y permite consultas estructuradas
EOF

ensure_issue "US-11: API REST de la lógica de negocio" "Fase 4 — Versión de Producción" <<'EOF'
**Historia propuesta** (no hay fila US en la especificación; derivada de los requisitos funcionales de la Fase 4).

La lógica de negocio debe exponerse a través de una API que permita iniciar carreras, cambiar su estado, finalizarlas y consultar el historial.

**Epic (milestone):** Fase 4 — Versión de Producción
**Fuente:** docs/CLIENT_SPECS.md → Fase 4, req. 2

## Criterios de aceptación

- [ ] La API permite iniciar carreras, cambiar su estado, finalizarlas y consultar el historial
- [ ] Puede ser consumida por cualquier cliente web o móvil en el futuro
EOF

ensure_issue "US-12: Panel web del histórico" "Fase 4 — Versión de Producción" <<'EOF'
**Historia propuesta** (no hay fila US en la especificación; derivada de los requisitos funcionales de la Fase 4).

El sistema debe incluir un panel web accesible desde el navegador para que el responsable de flota pueda consultar el historial sin instalar nada.

**Epic (milestone):** Fase 4 — Versión de Producción
**Fuente:** docs/CLIENT_SPECS.md → Fase 4, req. 3

## Criterios de aceptación

- [ ] Panel accesible desde el navegador sin instalar nada
- [ ] El responsable de flota consulta el histórico desde el panel
EOF

ensure_issue "US-13: Despliegue con un solo comando" "Fase 4 — Versión de Producción" <<'EOF'
**Historia propuesta** (no hay fila US en la especificación; derivada de los requisitos funcionales de la Fase 4).

El despliegue debe poder realizarse con un único comando, sin configuración manual del entorno.

**Epic (milestone):** Fase 4 — Versión de Producción
**Fuente:** docs/CLIENT_SPECS.md → Fase 4, req. 4

## Criterios de aceptación

- [ ] Un único comando despliega el sistema sin configuración manual del entorno
- [ ] Los datos sobreviven a reinicios del sistema
EOF

echo "Provisioning against $REPO finished."
