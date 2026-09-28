# 🚕 TaxiTech — Taxímetro Digital

> **Taximetro app de 0 a 100.** De la terminal a la flota: un taxímetro 100 % software,
> céntimo a céntimo, construido con DDD en un monorepo uv.

![CI](https://github.com/IA-P1-BCN/proyecto_1_juanCarlos_escamilla/actions/workflows/pr-checks.yml/badge.svg)
[![Tests — Allure](https://img.shields.io/badge/tests-Allure%20report-50AF82?logo=allure&logoColor=white)](https://ia-p1-bcn.github.io/proyecto_1_juanCarlos_escamilla/)
![Python](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)
![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge.json)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🎬 Demo

![Taxímetro TUI en acción](docs/assets/demo-taximetro.gif)

El turno completo en la TUI del conductor, grabado sobre el binario nativo: `1` inicia
la Carrera (3 s), `2` pasa a `en_movimiento` (5 s), `2` vuelve a `parada` (4 s), `3`
finaliza — con el Importe total exacto en pantalla — y `q` sale. Para regenerarla:

```bash
task bin                                                    # binario nativo
python3 scripts/demo-tui-driver.py bin/taximetro demo.cast  # graba la sesión (.cast)
agg demo.cast docs/assets/demo-taximetro.gif \
  --theme dracula --font-size 20 --idle-time-limit 5 --last-frame-duration 2
```

El ritmo de teclas vive en [`scripts/demo-tui-driver.py`](scripts/demo-tui-driver.py);
para renderizar hace falta [agg](https://github.com/asciinema/agg) (`brew install agg`).

## ✨ Características

- ⌨️ **CLI en tiempo real** — inicia la Carrera con un comando, cambia entre `parada` y
  `en_movimiento`, cobra el Importe exacto con dos decimales; REPL de comandos y TUI a
  pantalla completa *(Fase 1 — 🟢)*
- 🧾 **Histórico y observabilidad** — cada carrera queda registrada en disco
  (`historial` para cuadrar caja) y la operación completa llega a una bitácora
  JSON-lines (arranque, cambios de estado, cierre, errores) *(Fase 2 — 🟢)*; tarifas
  configurables en `tarifas.json` *(✔)*
- 🔐 **Arquitectura y UX** — refactorización OO, acceso por contraseña segura, GUI para
  tablet con botones grandes *(Fase 3)*
- 🌐 **Producción** — histórico en base de datos, API REST, panel web y despliegue con un
  solo comando *(Fase 4)*

## 🗺️ Roadmap — la carretera del proyecto

```mermaid
flowchart LR
    TAXI(["🚕<br/>estás aquí"]) -- Fase 2 completada ✔ --> F3
    subgraph CARRETERA["🛣️  Carretera de Fases"]
        direction LR
        F1["🚩 FASE 1<br/>MVP Funcional<br/>🟢 completada"] ==> F2["🚩 FASE 2<br/>Observabilidad<br/>🟢 completada"] ==> F3["🚩 FASE 3<br/>Arquitectura y UX<br/>⏳ pendiente"] ==> F4["🚩 FASE 4<br/>Producción<br/>⏳ pendiente"]
    end
    style TAXI fill:#facc15,stroke:#a16207,color:#111827
    style CARRETERA fill:#f3f4f6,stroke:#9ca3af
    style F1 fill:#86efac,stroke:#16a34a,color:#111827
    style F2 fill:#86efac,stroke:#16a34a,color:#111827
    style F3 fill:#e5e7eb,stroke:#9ca3af,color:#374151
    style F4 fill:#e5e7eb,stroke:#9ca3af,color:#374151
```

🟢 completada · 🟡 en curso · ⚪ pendiente — **el 🚕 avanza al cerrar cada Fase**.

Cada Fase es un milestone con sus historias: [`Fase 1`](https://github.com/IA-P1-BCN/proyecto_1_juanCarlos_escamilla/milestone/1) · [`Fase 2`](https://github.com/IA-P1-BCN/proyecto_1_juanCarlos_escamilla/milestone/2) · [`Fase 3`](https://github.com/IA-P1-BCN/proyecto_1_juanCarlos_escamilla/milestone/3) · [`Fase 4`](https://github.com/IA-P1-BCN/proyecto_1_juanCarlos_escamilla/milestone/4)

## 🛠️ Instalación

Requisitos: Python 3.12+, [uv](https://docs.astral.sh/uv/) y
[Task](https://taskfile.dev) (`brew install go-task`; [otras formas de
instalarlo](https://taskfile.dev/installation/)).

```bash
git clone git@github.com:IA-P1-BCN/proyecto_1_juanCarlos_escamilla.git
cd proyecto_1_juanCarlos_escamilla
task setup        # uv sync --all-packages + hooks de pre-commit
```

> ¿Sin `task`? Fallback directo: `uv sync --all-packages && uv run pre-commit install`.

## 🧰 Comandos del día a día

| qué quieres | con task | con uv (fallback) |
| --- | --- | --- |
| arrancar la TUI | `task run-tui` | `uv run taximetro-tui` |
| compilar el binario | `task bin` | — |
| formatear | `task format` | `uv run ruff format .` |
| lint | `task lint` | `uv run ruff check .` |
| tipos | `task typecheck` | `uv run mypy` |
| tests | `task test` | `uv run pytest` |
| todo lo que exige la CI | `task check` | los cuatro anteriores |

## 🚦 Uso

### REPL de comandos — `task run`

La línea de estado está siempre visible y se refresca sola cada segundo; tras
`finalizar` puedes encadenar otra Carrera sin cerrar el programa:

```text
$ task run
🚕 TaxiTech — Taxímetro Digital
Bienvenido. Comandos: iniciar · estado parada|movimiento · finalizar · historial [YYYY-MM-DD] · salir
🚕 libre · sin carrera
> iniciar
Carrera iniciada — el contador corre en parada (0,02 €/s)
🚕 parada · 0,00 €
> estado movimiento
🚕 en_movimiento · 0,06 €
> finalizar
Carrera finalizada. Importe total: 0,26 €
🚕 libre · sin carrera
> historial
Histórico · 28/09/2026
FECHA          DURACIÓN  IMPORTE
28/09 12:02   00:00:07   0,26 €
1 carreras · 0,26 € totales
> salir
```

Opciones con `task run -- --help` (equivale a `uv run taximetro-cli --help`).

### TUI a pantalla completa — `task tui`

El puesto del conductor: contador grande que corre en tiempo real, badge de Estado
(`🅿️ PARADA` / `🚕 EN_MOVIMIENTO`) y avisos al finalizar.

| tecla | acción |
| --- | --- |
| `1` | Iniciar carrera |
| `2` | Cambiar estado (parada ↔ en_movimiento) |
| `3` | Finalizar — muestra el Importe total |
| `q` | Salir |

### Binario nativo — `task bin`

`task bin` compila **`bin/taximetro`**, un ejecutable autocontenido (PyInstaller,
~14 MB, macOS arm64) que no necesita uv ni venv: lo copias donde quieras y arranca
la TUI del conductor directamente.

```bash
task bin
./bin/taximetro      # la TUI a pantalla completa
```

Los datos (Histórico y bitácora) se escriben en `data/` junto al directorio desde
el que se ejecuta — overridable con la variable `TAXIMETRO_DATA`.

## 🧭 Cómo está construido

Monorepo uv con **contextos delimitados como paquetes** y la presentación en capas:

```text
packages/
├── taximetro-kernel/     # vocabulario común: Money, Estado, Tramo, EventBus
├── taximetro-ride/       # la Carrera y su ciclo de vida (tramos + eventos)
├── taximetro-billing/    # Tarifa e Importe — dueño de config/tarifas.json
└── taximetro/            # capa de aplicación: ServicioTaximetro + histórico (fachada única)

apps/taximetro_cli/       # presentación, en capas
└── src/taximetro_cli/
    ├── main.py           # solo los puntos de entrada: taximetro-cli · taximetro-tui
    ├── interfaces/       # cli.py (REPL) · tui.py (TUI Textual) — gui/api llegan con sus fases
    └── infrastructure/   # composición (composition root) · reloj real · textos.json
```

El Importe se **deriva de los tramos** con un único redondeo half-up; los contextos
nunca se importan entre sí — hablan a través del kernel y de eventos de dominio en el
EventBus, que alimentan la bitácora de operación y el histórico del día.

- 📘 Arquitectura: [`docs/agents/architecture.md`](docs/agents/architecture.md)
- 🗣️ Lenguaje del dominio: [`CONTEXT.md`](CONTEXT.md)
- 🧾 Decisiones: [`docs/adr/`](docs/adr/)

## 🤝 Contribuir

1. Rama de trabajo desde `dev`: `git checkout -b feat/mi-cambio dev`
2. PR hacia `dev` con título semántico (`feat: …`, `fix: …`) — la CI ejecuta
   ruff + mypy + pytest.
3. TDD estricto: primero el test en rojo (`docs/agents/testing-tdd.md`).

Tras `task setup`, cada commit pasa por pre-commit (ruff lint + formato y checks
de higiene de ficheros).

**Checklist del README en cada PR:** si cerraste una Fase, **mueve el 🚕** al siguiente
tramo del diagrama y pon su banner en 🟢.

## 📄 Licencia

[Distribuido bajo la licencia MIT](LICENSE).
