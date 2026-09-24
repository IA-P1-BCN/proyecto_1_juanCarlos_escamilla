#!/usr/bin/env bash
set -euo pipefail

REPO_FULL=$(gh repo view --json nameWithOwner -q .nameWithOwner)
OWNER=$(echo "$REPO_FULL" | cut -d'/' -f1)
REPO_NAME=$(echo "$REPO_FULL" | cut -d'/' -f2)

echo "[7/7] Configuring GitHub Pages and Allure PR Reporting Workflow..."

# 1. Create gh-pages branch if it doesn't exist
echo "Checking 'gh-pages' branch..."
if ! git rev-parse --verify origin/gh-pages >/dev/null 2>&1; then
  echo "Creating orphan 'gh-pages' branch..."
  CURRENT_BRANCH=$(git branch --show-current)
  git checkout --orphan gh-pages
  git rm -rf . >/dev/null 2>&1 || true
  git commit --allow-empty -m "Initial gh-pages commit for Allure reports"
  git push -u origin gh-pages
  git checkout "$CURRENT_BRANCH"
  echo "✓ Created and pushed gh-pages branch."
else
  echo "✓ 'gh-pages' branch already exists."
fi

# 2. Enable GitHub Pages to deploy from 'gh-pages' branch root
echo "Enabling GitHub Pages on 'gh-pages' branch..."
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  "/repos/$OWNER/$REPO_NAME/pages" \
  -f "source[branch]=gh-pages" \
  -f "source[path]=/" > /dev/null 2>&1 || \
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/$OWNER/$REPO_NAME/pages" \
  -f "source[branch]=gh-pages" \
  -f "source[path]=/" > /dev/null 2>&1 || \
  echo " Note: GitHub Pages is already active."

# 3. Enable read & write permissions for GITHUB_TOKEN on PRs
echo "Updating repository workflow permissions..."
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/$OWNER/$REPO_NAME/actions/permissions/workflow" \
  -f "default_workflow_permissions=write" \
  -F "can_approve_pull_request_reviews=false" > /dev/null 2>&1 || echo " Note: Could not update token permissions via API; ensure workflow permissions are set to Read/Write in settings."

# 4. Generate .github/workflows/allure-pr-report.yml
mkdir -p .github/workflows
WORKFLOW_PATH=".github/workflows/allure-pr-report.yml"

cat << 'EOF' > "$WORKFLOW_PATH"
name: Allure PR Report (Historical Retention)

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: write
  pull-requests: write

concurrency:
  group: allure-gh-pages-${{ github.event.pull_request.number }}
  cancel-in-progress: false

jobs:
  allure-report:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
          cache-suffix: "uv-monorepo"

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Dependencies
        run: uv sync --all-packages --all-extras

      - name: Run Pytest with Allure
        run: uv run pytest --alluredir=allure-results
        continue-on-error: true

      - name: Set Report Variables
        id: vars
        run: |
          PR_NUM="${{ github.event.pull_request.number }}"
          echo "pr_num=$PR_NUM" >> $GITHUB_OUTPUT
          echo "subfolder=pr-$PR_NUM" >> $GITHUB_OUTPUT

      - name: Generate Allure Report with History
        uses: simple-elf/allure-report-action@v1.10
        with:
          allure_results: allure-results
          allure_history: allure-history
          gh_pages: gh-pages
          subfolder: ${{ steps.vars.outputs.subfolder }}
          keep_reports: 20

      - name: Deploy Report to gh-pages Branch
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_branch: gh-pages
          publish_dir: allure-history
          keep_files: true

      - name: Comment PR Report URL
        uses: actions/github-script@v7
        with:
          script: |
            const owner = context.repo.owner;
            const repo = context.repo.repo;
            const prNum = "${{ steps.vars.outputs.pr_num }}";
            const subfolder = "${{ steps.vars.outputs.subfolder }}";
            
            const reportUrl = `https://${owner}.github.io/${repo}/${subfolder}/`;
            const commentBody = `📊 **Allure Test Report Updated for PR #${prNum}**\n\nView interactive test results:\n${reportUrl}`;

            const comments = await github.rest.issues.listComments({
              owner,
              repo,
              issue_number: context.issue.number,
            });

            const botComment = comments.data.find(c => c.body.includes('Allure Test Report Updated'));

            if (botComment) {
              await github.rest.issues.updateComment({
                owner,
                repo,
                comment_id: botComment.id,
                body: commentBody
              });
            } else {
              await github.rest.issues.createComment({
                owner,
                repo,
                issue_number: context.issue.number,
                body: commentBody
              });
            }
EOF

echo "✓ Created $WORKFLOW_PATH"
echo "✓ Allure GitHub Pages setup completed successfully!"
