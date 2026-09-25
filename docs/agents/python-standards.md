# Python standards

Derived from the AppJet Python coding standards
(https://appjet.ai/blog/python-coding-standards) + PEP 8. Formatting is enforced by
tooling so review can focus on design — "revisas el diseño, no el formato".

## Naming

- `snake_case` for functions and variables; functions start with a verb
  (`calcular_importe`, `cambiar_estado`).
- `CapWords` for classes naming a thing or role (`Carrera`, `Tarifa`,
  `TarifasService`).
- `UPPER_SNAKE_CASE` for constants (`TARIFA_PARADA`, `TARIFA_MOVIMIENTO`).
- Leading underscore for private/internal details.
- No intent-hiding abbreviations; no camelCase.

## Formatting & linting — Ruff is the single source of truth

- `line-length = 88`, `target-version = "py312"`, rule set `E, F, I, B, UP`
  (PEP 8 + pyflakes + import sorting + bugbear + pyupgrade).
- Never debate formatting in review; run `uv run ruff format .` before committing.
- No trailing whitespace; imports grouped stdlib → third-party → local, sorted.

## Typing — layered, not all-or-nothing

- Type hints **required** on public APIs, service boundaries, and the domain
  (`packages/core/domain`).
- Union syntax is `X | None`. Use `Protocol` for structural seams (e.g. the
  persistence service port).
- Checker: **mypy**, starting permissive (`check_untyped_defs = true`,
  `warn_return_any = true`), tightened over time; newly changed public functions
  must gain annotations.

## Docstrings & comments

- Google style, applied consistently.
- Public functions document purpose, args, returns, and raised exceptions when not
  obvious.
- Comments explain *why* a surprising decision exists — never narrate the code.

## Error handling

- Raise specific exceptions, never bare `Exception`; no bare `except`.
- Project hierarchy rooted at `TaximetroError` (e.g. `CarreraActivaError`,
  `EstadoInvalidoError`, `PersistenciaError`).
- Chain context with `raise ... from err`.

## Functions & structure

- One responsibility per function — split validation, I/O, transformation,
  persistence, presentation.
- No mutable default arguments; use `None` + allocate per call.

## CI gate (the standards survive ordinary merges)

`uv run ruff format --check .` → `uv run ruff check .` → type check → `pytest`,
enforced on every PR by `.github/workflows/pr-checks.yml`. No "fix lint in a
follow-up PR".
