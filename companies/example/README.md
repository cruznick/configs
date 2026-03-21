# companies/example — Local work-context example assets

This directory contains local-use example files for private work contexts.
It is **not deployed by chezmoi**.

The directory name is historical. These files are examples only; concrete work
details still belong in local work-context files under:

- `~/.config/dotfiles/work-contexts/<slug>.toml`

## Files

- `.envrc.example` — direnv + direnv-1password template for per-context secrets.
  Copy to `~/repos/work/<platform>/<slug>/.envrc.example` manually if you want a per-company secret template.
  Then: `cp .envrc.example .envrc`, fill in `op://` references, `direnv allow`.

- `npmrc` — private registry config example (no credentials — those come from direnv `.envrc`)

- `README.md` — this file

## Secrets architecture

| What | Where | Why |
|------|-------|-----|
| Registry tokens, proxies | `.envrc` (per work repo dir) | Fetched from 1Password on `cd`; unloaded on `cd` out |
| Global personal tokens (`GITHUB_TOKEN`) | `~/.envrc` | Loaded by direnv; edit op:// paths, then: `dots-allow` |
| Non-secret work-context metadata | `~/.config/dotfiles/work-contexts/<slug>.toml` | Local-only source of truth for work Git/direnv config |
