# companies/example — Work company template

This directory contains template files for a work company setup.
It is **not deployed by chezmoi** — it is a reference for repo-tracked work/company setup.

## Files

- `.envrc.example` — direnv + direnv-1password template for per-company secrets.
  Copy to `~/repos/work/<platform>/<slug>/.envrc.example` manually if you want a per-company secret template.
  Then: `cp .envrc.example .envrc`, fill in `op://` references, `direnv allow`.

- `npmrc` — private npm registry config (no credentials — those come from direnv `.envrc`)

- `README.md` — this file

## Secrets architecture

| What | Where | Why |
|------|-------|-----|
| Registry tokens, proxies | `.envrc` (per company repo dir) | Fetched from 1Password on `cd`; unloaded on `cd` out |
| Global personal tokens (`GITHUB_TOKEN`) | `~/.envrc` | Loaded by direnv; edit op:// paths, then: `dots-allow` |
| Non-secret company metadata | `~/.config/dotfiles/work-contexts/<slug>.toml` | Local-only source of truth for work Git/direnv config |
