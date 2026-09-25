# Repo workflow

Repo facts and conventions for `IA-P1-BCN/proyecto_1_juanCarlos_escamilla` (product: TaxiTech Taxímetro). This is the one
file for git / PR / CI / scripts facts. Commit-message *philosophy* is not policed in
docs — the CI title check below is the only rule in that area.

## Branches

- `main` — protected, production-ready.
- `stg` — integration branch; PRs into `main` come from `stg` (CI branch guardrails warn
  otherwise).
- `dev` — daily work integrates here; PRs from feature branches into `dev`, then
  `dev` → `stg` → `main`.
- Feature branches: `<type>/<slug>` off `dev`.
- `main` is the **source of truth**: keep `dev` synced by merging `main` into `dev`
  (admin-bypassed push — it's a sync, not feature work).
- Tickets close **manually** when their PR targets `dev`: "Closes #N" only auto-fires on
  the default branch.

## Pull requests

- PR titles are validated by CI (semantic-pull-request action in
  `.github/workflows/pr-checks.yml`): allowed types
  `feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert`.
- Merge gate (`pr-checks.yml`): `uv sync --all-packages` → `uv run ruff format --check .`
  → `uv run ruff check .` → pytest on changed packages.
- Every PR also gets an **Allure HTML test report** published to GitHub Pages
  (`.github/workflows/allure-pr-report.yml` → `gh-pages` branch, `pr-<n>/` subfolder,
  history kept) plus an idempotent PR comment with the report link.

## GitHub state (provisioned by `scripts/provision-github.sh`, idempotent)

- Labels `story` and `task`; the five triage labels of `docs/agents/triage-labels.md` are
  documented but optional to create.
- Milestones = the 4 Fases (epics); stories/tasks are labelled issues inside them —
  conventions in `docs/agents/issue-tracker.md`.
- Test reports: `https://ia-p1-bcn.github.io/proyecto_1_juanCarlos_escamilla/` (GitHub Pages from `gh-pages`).

## Scripts inventory

- `scripts/provision-github.sh` — labels + milestones + story issues (idempotent;
  `REPO=owner/name` override).
- `scripts/06-create-workflow.sh` — creates `.github/workflows/pr-checks.yml`.
- `scripts/07-setup-allure-pages.sh` — creates the `gh-pages` orphan branch, enables
  Pages, creates the Allure workflow.
- `scripts/uv-monorepo-scaffold.sh` — superseded by `docs/agents/architecture.md`
  (kept for reference only).
- `scripts/01–03`, `05`, `setup-repo.sh` — bootstrap helpers; note `setup-repo.sh`
  expects the scripts under `./scripts/` while they sit at the repo root — fix paths
  before running.
