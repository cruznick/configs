# cruznick/configs

Personal dotfiles — managed by [chezmoi](https://chezmoi.io).

## Install on a new Mac

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cruznick/configs/master/install.sh)"
```

This single command:
1. Installs Homebrew (if missing)
2. Installs chezmoi
3. Clones this repo into `~/.local/share/chezmoi/`
4. Prompts for name, personal email, GitHub username, 1Password vault — stored locally, never committed
5. Deploys all dotfiles to `$HOME`
6. Runs one-time scripts: zinit install, brew packages, asdf tool versions, SSH key export from 1Password, work gitconfig generation

## Update dotfiles on an existing machine

```bash
chezmoi update
```

Pulls latest from this repo and re-applies any changes.

## Repo structure

```
configs/
├── install.sh                    # curl entry point
├── .chezmoi.toml.tmpl            # first-run prompts (name, email, vault)
├── .chezmoidata/
│   ├── companies.toml            # gitignored — your local company registry
│   └── companies.toml.example   # committed example (copy and fill in)
├── .chezmoiscripts/              # run-once setup scripts (brew, zinit, asdf, SSH, gitconfigs)
├── dot_zshrc.tmpl                # ~/.zshrc
├── dot_gitconfig.tmpl            # ~/.gitconfig (dynamic per-company includeIf)
├── dot_gitconfig-personal-*.tmpl # personal git identity configs
├── dot_secrets.zsh.tmpl          # ~/.secrets.zsh skeleton (global tokens only)
├── dot_ssh/config.tmpl           # ~/.ssh/config (host aliases per company)
├── dot_config/1Password/ssh/     # 1Password SSH agent config
├── dot_zshrc.d/work.zsh.tmpl    # template for per-company ~/.zshrc.d/work-<slug>.zsh
├── bin/                          # ~/bin scripts (work-config, git-check, glab-auto, …)
├── companies/example/            # reference template for a work company (.envrc.example)
├── docs/                         # Guides
└── legacy/                       # Pre-2025 configs (historical, not managed)
```

## Directory layout on disk

```
~/repos/
├── work/
│   ├── gl/<company>/   ← Work GitLab repos (identity auto-selected by path)
│   └── gh/<company>/   ← Work GitHub repos (identity auto-selected by path)
└── personal/
    ├── gl/             ← Personal GitLab repos
    └── gh/             ← Personal GitHub repos
        └── configs/    ← This repo
```

Git identity is automatically selected by directory — no manual config switching needed.

## Secrets architecture

| Scope | Mechanism | When loaded | Example |
|-------|-----------|-------------|---------|
| Global (auth tokens) | `~/.secrets.zsh` | Each shell session | `GITHUB_TOKEN` |
| Per-company (registry, proxies) | direnv `.envrc` in repo dir | On `cd` into dir | `ARTIFACTORY_TOKEN` |
| Per-project (overrides) | direnv `.envrc` in project | On `cd` into project | `NODE_ENV`, `AWS_PROFILE` |

Company secrets are fetched from 1Password via `op://` URIs using [direnv-1password](https://github.com/tmatilai/direnv-1password).

## Managing work companies

```bash
# Add a company
work-config add --slug=acme --platform=gh --email=you@acme.com

# List configured companies and verify setup
work-config list
work-config check
```

## See also

- [docs/SETUP.md](docs/SETUP.md) — Step-by-step new machine guide
- [docs/ADD-COMPANY.md](docs/ADD-COMPANY.md) — How to add a work company
- [docs/SSH-KEYS.md](docs/SSH-KEYS.md) — 1Password SSH key setup
