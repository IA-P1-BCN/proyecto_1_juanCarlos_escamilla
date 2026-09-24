#!/usr/bin/env bash
set -euo pipefail

REPO_FULL=$(gh repo view --json nameWithOwner -q .nameWithOwner)
OWNER=$(echo "$REPO_FULL" | cut -d'/' -f1)
REPO_NAME=$(echo "$REPO_FULL" | cut -d'/' -f2)

echo "[3/6] Applying Pull Request protection rules to main, stg, and dev..."

for BRANCH in main stg dev; do
  gh api \
    --method PUT \
    -H "Accept: application/vnd.github+json" \
    "/repos/$OWNER/$REPO_NAME/branches/$BRANCH/protection" \
    -F "required_status_checks=null" \
    -F "enforce_admins=false" \
    -F "required_pull_request_reviews[required_approving_review_count]=1" \
    -F "restrictions=null" > /dev/null
  echo " Protected branch: $BRANCH"
done

echo "✓ Branch protection rules applied!"
