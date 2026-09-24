#!/usr/bin/env bash
set -euo pipefail

REPO_FULL=$(gh repo view --json nameWithOwner -q .nameWithOwner)
OWNER=$(echo "$REPO_FULL" | cut -d'/' -f1)

echo "[4/6] Setting up Issue Types and GitHub Project V2..."

gh api graphql -f query='
mutation {
  createIssueType(input: {ownerId: "'$(gh api "users/$OWNER" -q .node_id 2>/dev/null || gh api "orgs/$OWNER" -q .node_id)'", name: "Epic", description: "Large body of work"}) { issueType { id } }
}' > /dev/null 2>&1 || echo " Note: Issue type 'Epic' already exists or requires Org admin."

gh api graphql -f query='
mutation {
  createIssueType(input: {ownerId: "'$(gh api "users/$OWNER" -q .node_id 2>/dev/null || gh api "orgs/$OWNER" -q .node_id)'", name: "Story", description: "User feature request"}) { issueType { id } }
}' > /dev/null 2>&1 || echo " Note: Issue type 'Story' already exists or requires Org admin."

gh api graphql -f query='
mutation {
  createIssueType(input: {ownerId: "'$(gh api "users/$OWNER" -q .node_id 2>/dev/null || gh api "orgs/$OWNER" -q .node_id)'", name: "Task", description: "Technical task or sub-item"}) { issueType { id } }
}' > /dev/null 2>&1 || echo " Note: Issue type 'Task' already exists or requires Org admin."

PROJECT_URL=$(gh project create --owner "$OWNER" --title "main" --format json | jq -r '.url')
echo "✓ Project created: $PROJECT_URL"
