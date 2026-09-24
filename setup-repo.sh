#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo " Starting Full Repository Setup"
echo "========================================"

chmod +x scripts/01-create-gitignore.sh \
         scripts/02-setup-branches.sh \
         scripts/03-protect-branches.sh \
         scripts/04-setup-github-project.sh \
         scripts/05-create-demo-issues.sh \
         scripts/06-create-workflow.sh

./scripts/01-create-gitignore.sh
./scripts/02-setup-branches.sh
./scripts/03-protect-branches.sh
./scripts/04-setup-github-project.sh
./scripts/05-create-demo-issues.sh
./scripts/06-create-workflow.sh

echo "========================================"
echo " Repository Setup Completed Successfully!"
echo "========================================"
