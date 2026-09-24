#!/usr/bin/env bash
set -euo pipefail

GITIGNORE_PATH=".gitignore"
CUSTOM_MARKER="# --- Custom project patterns ---"

echo "[1/6] Generating Python & uv .gitignore..."

# Capture existing custom patterns so regeneration never overwrites them.
custom_block=""
if [ -f "$GITIGNORE_PATH" ]; then
    start_line="$(grep -nF "$CUSTOM_MARKER" "$GITIGNORE_PATH" | cut -d: -f1 | head -n 1 || true)"
    if [ -n "$start_line" ]; then
        # Everything from the marker to EOF is custom-managed: keep it verbatim.
        custom_block="$(tail -n "+${start_line}" "$GITIGNORE_PATH")"
    else
        # No marker: treat the entire existing file as hand-written patterns.
        custom_block="$(cat "$GITIGNORE_PATH")"
    fi
fi

# Build the new file in a temp location so a failed download can never
# clobber the existing .gitignore.
tmp_file="$(mktemp)"
trap 'rm -f "$tmp_file"' EXIT

{
    curl -fsSL "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
    echo
    if [ -n "$custom_block" ]; then
        printf '%s\n' "$custom_block"
    else
        cat << 'EOF'
# --- Custom project patterns ---
# --- OS / macOS ---
.DS_Store
._*
.AppleDouble
.LSOverride
Thumbs.db

# --- Virtual environments ---
.venv/
venv/
env/

# --- uv ---
.uv/

# --- Testing & quality tooling ---
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
.coverage.*
htmlcov/
coverage.xml

# --- Environment variables ---
.env
.env.local
.env.*.local

# --- Node / Next.js ---
node_modules/
.next/
out/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# --- IDEs & Editors ---
.vscode/
.idea/
*.swp
*.swo
EOF
    fi
} > "$tmp_file"

mv "$tmp_file" "$GITIGNORE_PATH"

if [ -n "$custom_block" ]; then
    echo "✓ Regenerated $GITIGNORE_PATH (existing custom patterns preserved)."
else
    echo "✓ Created $GITIGNORE_PATH successfully!"
fi
