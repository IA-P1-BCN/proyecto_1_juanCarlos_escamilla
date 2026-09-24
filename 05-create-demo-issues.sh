#!/usr/bin/env bash
set -euo pipefail

REPO_FULL=$(gh repo view --json nameWithOwner -q .nameWithOwner)
OWNER=$(echo "$REPO_FULL" | cut -d'/' -f1)

echo "[5/6] Creating demo issues and adding them to Project 'main'..."

EPIC_URL=$(gh issue create \
  --title "[DEMO] Epic: Redesign User Authentication System" \
  --body "## Goal\nOverhaul authentication workflow to support OAuth2 and MFA.\n\n*Note: Demo issue to be deleted.*" \
  --label "epic" 2>/dev/null || gh issue create --title "[DEMO] Epic: Redesign User Authentication System" --body "Demo Epic")

STORY_URL=$(gh issue create \
  --title "[DEMO] Story: Implement Google OAuth Login" \
  --body "As a user, I want to sign in using my Google account.\n\n**Parent Epic:** $EPIC_URL\n\n*Note: Demo issue to be deleted.*" \
  --label "story" 2>/dev/null || gh issue create --title "[DEMO] Story: Implement Google OAuth Login" --body "Demo Story")

TASK_URL=$(gh issue create \
  --title "[DEMO] Task: Configure OAuth Client Credentials" \
  --body "Set up developer console credentials for Google OAuth client ID and secrets.\n\n**Parent Story:** $STORY_URL\n\n*Note: Demo issue to be deleted.*" \
  --label "task" 2>/dev/null || gh issue create --title "[DEMO] Task: Configure OAuth Client Credentials" --body "Demo Task")

gh project item-add --owner "$OWNER" --url "$EPIC_URL" > /dev/null
gh project item-add --owner "$OWNER" --url "$STORY_URL" > /dev/null
gh project item-add --owner "$OWNER" --url "$TASK_URL" > /dev/null

echo "✓ Demo Epic:  $EPIC_URL"
echo "✓ Demo Story: $STORY_URL"
echo "✓ Demo Task:  $TASK_URL"
