# 0003 — Dev loop: Taskfile + pre-commit; CI en crudo con uv

## Status

accepted (2026-09-25)

## Decision

El día a día del repo se maneja con un `Taskfile.yml` raíz (`task setup`, `task run`,
`task check`) siguiendo la receta de monorepo uv de
[_Python Monorepo Magic_](https://dev.to/_mh/python-monorepo-magic-organize-build-and-ship-multi-service-apps-3al3),
adaptada a un solo entregable: tareas planas, sin namespaces por servicio. La higiene
local corre en pre-commit (ruff lint + formato, check-toml/yaml, end-of-file,
whitespace) como dependencia del grupo `dev` — dentro de `uv.lock`, no como `uv tool`
global. La CI **no** usa `task`: ejecuta los comandos uv en crudo con `--frozen`,
igual que el artículo, para no depender del binario Go en los runners. El ejecutable
del CLI pasa a llamarse `taximetro-cli` (el paquete workspace sigue siendo `cli`).

## Considered options

- **Make / just**: rechazados — task es declarativo, multiplataforma y
  auto-documentado (`task` a secas lista las tareas).
- **Solo comandos uv documentados**: rechazado — pierde el punto de entrada único y
  la superficie crece con las fases (gui, api).

## Consequences

`task` (go-task) es un requisito solo para humanos; el README documenta el fallback
con uv para quien no lo instale. pre-commit viaja en el lock, así que `task setup` es
reproducible. Los hooks de ruff se pinan a la misma versión que el lock (hoy v0.16.9):
al subir ruff, se suben juntos.
