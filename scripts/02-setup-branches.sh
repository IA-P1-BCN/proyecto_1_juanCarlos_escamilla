#!/usr/bin/env bash
set -euo pipefail

echo "[2/6] Creating main, stg, and dev branches..."

git checkout -B main
git push -u origin main --force-with-lease || true

git checkout -B stg
git push -u origin stg --force-with-lease

git checkout -B dev
git push -u origin dev --force-with-lease

git checkout main

echo "✓ Branches main, stg, and dev created and pushed!"
