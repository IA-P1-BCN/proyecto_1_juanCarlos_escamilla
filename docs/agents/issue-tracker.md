# Issue tracker: GitHub Issues + Milestones

Issues and specs for this repo live as GitHub issues on `IA-P1-BCN/proyecto_1_juanCarlos_escamilla`. Epics are GitHub
**milestones**; stories and tasks are issues inside the milestone of their epic. Use the
`gh` CLI for all operations.

## Conventions

- **Epic = milestone**: each epic is a GitHub milestone. The title is the epic name; the
  scope/notes go in the milestone description.
  Create: `gh api repos/<owner>/<repo>/milestones -f title="..." -f description="..."`
- **Story**: an issue labelled `story`, created inside its epic's milestone:
  `gh issue create --milestone "<epic milestone title>" --label story ...`
- **Task**: an issue labelled `task`, same rules as stories.
- **Hierarchy**: milestone (epic) → story and task issues live directly in the milestone.
  When a task belongs to a specific story, link it as a sub-issue of the story or put
  `Part of #<story>` at the top of its body.
- **Where the information lives**: the milestone (epic) description holds the epic's scope
  and its fase-wide/transversal requirements. Story bodies hold the story statement plus
  their acceptance criteria, derived from the epic's text. Don't leave acceptance criteria
  out of the story body.
- **Create an issue**: `gh issue create --title "..." --body "..." --milestone "<epic>"`
  (heredoc for multi-line bodies), plus `--label story` or `--label task`.
- **Read an issue**: `gh issue view <number> --comments`, also fetching labels.
- **List an epic's issues**: `gh issue list --milestone "<epic>" --state open --json number,title,labels`
- **Comment / label / close**: `gh issue comment`, `gh issue edit --add-label/--remove-label`,
  `gh issue close --comment`.
- **Close an epic**: once every issue in the milestone is closed, close the milestone:
  `gh api --method PATCH repos/<owner>/<repo>/milestones/<milestone_number> -F state=closed`

Infer the repo from `git remote -v`; `gh` does this automatically inside a clone.

## Specs

A spec is the reference contract for an epic's stories — it is not work itself.

- Specs are standalone issues labelled `spec`, **never inside a milestone** (milestones
  track deliverable work: stories/tasks).
- The epic's milestone description links to its spec with **both forms** —
  `**Spec:** #N — https://github.com/<owner>/<repo>/issues/N` — so the link survives
  copy-paste outside GitHub; stories reference it in their body too.
- Specs don't go through triage — the stories they cover do.

## Provisioning status

Only the `story` and `task` labels are needed; create with `gh label create` if missing.
Note: `04-setup-github-project.sh` and `05-create-demo-issues.sh` predate this flow — they
set up an Epic/Story/Task *issue-type* layer and a Project V2 board that this flow does not
use. Don't run them for this.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature
requests; `/triage` reads this flag.)_

## When a skill says "publish to the issue tracker"

New epic → create a milestone. Otherwise → create a `story`/`task` issue in the epic's
milestone.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The map is issue-based, independent of the milestone layer. The
**map** is a single issue with **child** issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far /
  Fog body. `gh issue create --label wayfinder:map`.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue (`gh api` on the
  sub-issues endpoint). Where sub-issues aren't enabled, add the child to a task list in the
  map body and put `Part of #<map>` at the top of the child body. Labels:
  `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is
  assigned to the driving dev.
- **Blocking**: GitHub's **native issue dependencies**. Add an edge with
  `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`
  (database id, not `#number`). A ticket is unblocked when every blocker is closed. Where
  dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of
  the child body.
- **Frontier query**: list the map's open children, drop any with an open blocker or an
  assignee; first in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me`, the session's first write.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, then `gh issue close <n>`, then
  append a context pointer (gist + link) to the map's Decisions-so-far.
