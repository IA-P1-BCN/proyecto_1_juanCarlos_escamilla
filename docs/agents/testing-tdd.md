# Testing & TDD

## TDD is non-negotiable

The loop (enforced by the installed `tdd` skill, `.agents/skills/tdd/`):

1. **Red before green** — write one failing test that verifies *behavior through a
   public interface*; only then write the minimum production code to pass it.
2. **One vertical slice at a time** — one seam, one test, one minimal
   implementation per cycle; never all tests first.
3. **Seams are pre-agreed** — before writing any test, the seams (where tests
   attach) are written down and confirmed with the user. No test at an unconfirmed
   seam; if the interface shape is in question, consult the `codebase-design`
   skill.
4. **No implementation-coupled tests** — don't mock internal collaborators, don't
   test private methods, don't verify through side channels. Tests read like
   specifications of `Carrera`/`Tarifa` behavior.
5. **Refactoring is not part of the loop** — it happens at review time
   (`code-review` skill).

Exemption: throwaway scaffolding/scripts. Everything in `packages/*` (contexts) and
`apps/*` is production code — no "I'll test it later".

## Where tests live

- All tests in **`packages/tests`** (the dedicated test workspace member) — they may
  import any other member, nothing imports them.
- **CLI tests use Typer's `CliRunner`** — never raw `main()` + capsys: Typer parses
  `sys.argv` and would eat pytest's arguments. The i18n contract is part of the test:
  placeholders must resolve (no raw `taximetro.` keys in the output), rendered text is
  not blank, and the Spanish literals of `locales/es.yml` pin the language.
- Files mirror the structure they specify: `tests/ride/test_carrera.py`,
  `tests/pricing/test_motor_tarifas.py`, …
- Test names state the behavior in domain vocabulary (*carrera*, *tarifa*,
  *cambiar_estado*), e.g. `test_carrera_en_movimiento_acumula_0_05_eur_por_segundo`.
- **Contract tests pin every port**: each consumer-owned port (e.g. `pricing`'s
  rate-loading port, `fleet`'s ledger repository) gets one behavior suite run against
  every adapter — the JSON adapters pass them today; the Fase 4 Postgres adapters must
  pass the same tests before they are accepted.

## Reporting — Allure HTML on GitHub Pages

- The suite runs with pytest; reports are generated with **Allure**.
- CI (`.github/workflows/allure-pr-report.yml`): every PR runs the suite
  (`--alluredir`), builds the HTML report with history, publishes it to **GitHub
  Pages** (`gh-pages` branch) under `pr-<number>/`, and posts/updates a PR comment
  with the report link.
- `.github/workflows/pr-checks.yml` additionally runs ruff + pytest (changed
  packages) as the merge gate.
- Fase 2 requirement to keep in mind: the fare-calculation logic must be fully
  covered by automated tests — build that coverage from Fase 1 via TDD, not
  retroactively.
