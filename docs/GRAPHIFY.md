# Graphify

[Graphify](https://github.com/Graphify-Labs/graphify) turns a codebase into a
queryable local knowledge graph and provides a skill for Codex and other coding
assistants. The official Python package is `graphifyy`; its command is
`graphify`.

On macOS, the `run_onchange_after_25-setup-graphify.sh.tmpl` chezmoi hook uses
`uv` to install or upgrade the CLI, then registers the Codex skill for the
current user. This installs the skill globally so it is available across
projects. If `uv` is unavailable, the hook warns and skips setup.

To retry manually:

```bash
uv tool install --upgrade graphifyy
uv tool run --from graphifyy graphify install --platform codex
```

In Codex, invoke the skill with `$graphify`. Graphify builds its output inside
the project being analyzed; review those generated files before committing
them.
