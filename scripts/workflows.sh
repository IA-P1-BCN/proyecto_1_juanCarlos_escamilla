#!/usr/bin/env bash
# Enable/disable the repo's GitHub Actions workflows without touching their YAML.
#
# Usage: scripts/workflows.sh off|on|status
#
# Note: 'pages-build-deployment' is GitHub's automatic Pages build — it can't be
# disabled from here; it only stops if you disable Pages (Settings → Pages).
set -euo pipefail

REPO="${REPO:-$(git config --get remote.origin.url | sed -E 's#.*github\.com[/:]##; s#\.git$##')}"
WORKFLOWS=("pr-checks.yml" "allure-pr-report.yml")
ACTION="${1:-status}"

case "$ACTION" in
  off)
    for w in "${WORKFLOWS[@]}"; do
      gh workflow disable "$w" --repo "$REPO"
      echo "disabled: $w"
    done
    ;;
  on)
    for w in "${WORKFLOWS[@]}"; do
      gh workflow enable "$w" --repo "$REPO"
      echo "enabled: $w"
    done
    ;;
  status)
    gh workflow list --repo "$REPO"
    ;;
  *)
    echo "usage: $0 off|on|status" >&2
    exit 1
    ;;
esac
