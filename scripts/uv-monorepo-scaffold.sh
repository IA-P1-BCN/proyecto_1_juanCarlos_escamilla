#!/usr/bin/env bash
set -e

REPO_NAME=${1:-"my-monorepo"}

echo "🚀 Scaffolding uv monorepo in './$REPO_NAME'..."
mkdir -p "$REPO_NAME"
cd "$REPO_NAME"

# 1. Initialize root workspace directory structure
mkdir -p apps packages

# 2. Generate root pyproject.toml with uv workspace settings
cat << 'EOF' > pyproject.toml
[project]
name = "monorepo-root"
version = "0.1.0"
description = "Monorepo initialized with uv and Taskfile"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[tool.uv.workspace]
members = ["apps/*", "packages/*"]
EOF

touch README.md

# 3. Create Taskfile.yml with dynamic automation tasks
cat << 'EOF' > Taskfile.yml
version: '3'

tasks:
  # --- Dynamic Scaffolding Tasks ---
  create:pkg:
    desc: "Create a new Python workspace package (e.g., task create:pkg NAME=utils)"
    cmds:
      - uv init packages/{{.NAME}} --lib --name {{.NAME}} --python 3.12
      - uv sync

  create:app:
    desc: "Create a new Python app (e.g., task create:app NAME=worker)"
    cmds:
      - uv init apps/{{.NAME}} --app --name {{.NAME}} --python 3.12
      - uv sync

  # --- Project Orchestration Tasks ---
  install:
    desc: "Install all Python and Node dependencies"
    cmds:
      - uv sync --all-packages
      - cd apps/frontend && npm install

  create:fastapi:
    desc: "Create a new FastAPI app (e.g., task create:fastapi NAME=service)"
    cmds:
      - uv init apps/{{.NAME}} --app --name {{.NAME}}-app --python 3.12
      - uv add "fastapi[standard]" --package {{.NAME}}-app
      - uv sync --all-packages

  dev:fastapi:
    desc: "Run FastAPI app in development mode"
    dir: apps/fastapi
    cmds:
      - uv run fastapi dev

  dev:cli:
    desc: "Run CLI app"
    dir: apps/cli
    cmds:
      - uv run python main.py

  dev:frontend:
    desc: "Run Next.js frontend"
    dir: apps/frontend
    cmds:
      - npm run dev

  test:
    desc: "Run tests across packages"
    cmds:
      - uv run pytest
EOF

# 4. Bootstrap core Python packages and apps using uv
echo "📦 Creating shared libraries..."
uv init packages/core --lib --name core --python 3.12
uv init packages/tests --lib --name tests --python 3.12

# Add dummy module in core package
cat << 'EOF' > packages/core/src/core/dummy.py
def get_hello_message(caller: str = "World") -> str:
    """Return a hello world greeting message from the core package."""
    return f"Hello {caller} from core package!"
EOF

cat << 'EOF' > packages/core/src/core/__init__.py
from core.dummy import get_hello_message

__all__ = ["get_hello_message"]
EOF

echo "🐍 Creating Python apps..."
uv init apps/cli --app --name cli --python 3.12
uv init apps/fastapi --app --name fastapi-app --python 3.12

# Scaffold FastAPI app dependencies
echo "⚡ Scaffolding FastAPI dependencies..."
uv add "fastapi[standard]" --package fastapi-app

# Hello world in CLI importing core
cat << 'EOF' > apps/cli/main.py
from core.dummy import get_hello_message


def main():
    print(get_hello_message("CLI"))


if __name__ == "__main__":
    main()
EOF

# Hello world in FastAPI importing core
cat << 'EOF' > apps/fastapi/main.py
from fastapi import FastAPI
from core.dummy import get_hello_message

app = FastAPI(title="FastAPI Service")


@app.get("/")
def read_root():
    return {"message": get_hello_message("FastAPI")}


@app.get("/health")
def health_check():
    return {"status": "ok"}
EOF

# 5. Bootstrap Next.js frontend non-interactively
echo "🌐 Creating Next.js frontend..."
npx create-next-app@latest apps/frontend \
  --ts \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*" \
  --use-npm \
  --no-git \
  --yes

# 6. Link internal workspace dependencies
echo "🔗 Linking 'core' package to fastapi, cli, and tests..."
uv add core --package fastapi-app
uv add core --package cli
uv add core --package tests

# 7. Final workspace sync
echo "🔄 Running initial uv sync..."
uv sync --all-packages

echo "✅ Done! Your monorepo is ready in './$REPO_NAME'."
