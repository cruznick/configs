# cruznick/configs

Benjamin's dotfiles — managed by [chezmoi](https://chezmoi.io).

## Install on a new Mac

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cruznick/configs/main/install.sh)"
```

This single command:
1. Installs Homebrew (if missing)
2. Installs chezmoi
3. Clones this repo into `~/.local/share/chezmoi/`
4. Prompts for name, emails, work company — stored locally, never committed
5. Deploys all dotfiles to `$HOME`
6. Runs one-time scripts: brew packages, asdf tool versions, SSH key export from 1Password

## Update dotfiles on an existing machine

```bash
chezmoi update
```

Pulls latest from this repo and re-applies any changes.

## Repo structure

```
configs/
├── install.sh                    # curl entry point
├── .chezmoi.toml.tmpl            # first-run prompts (name, email, company)
├── .chezmoidata/companies.toml   # work company registry
├── .chezmoiscripts/              # run-once setup scripts (brew, asdf, SSH)
├── dot_zshrc.tmpl                # ~/.zshrc
├── dot_gitconfig.tmpl            # ~/.gitconfig (dynamic per-company includeIf)
├── dot_gitconfig-*.tmpl          # per-identity git configs
├── dot_ssh/config.tmpl           # ~/.ssh/config (host aliases)
├── dot_config/1Password/ssh/     # 1Password SSH agent config
├── bin/                          # ~/bin scripts
├── companies/kavak/              # Kavak-specific configs (npmrc, env)
├── docs/                         # Guides
└── legacy/                       # Pre-2025 configs (historical, not managed)
```

## Directory layout on disk

```
~/repos/
├── work/
│   ├── gl/kavak/     ← Kavak GitLab repos
│   ├── gl/birdie/    ← (future)
│   ├── gh/kavak/     ← Kavak GitHub repos
│   └── gh/birdie/    ← (future)
└── personal/
    ├── gl/           ← Personal GitLab repos
    └── gh/           ← Personal GitHub repos
        └── configs/  ← This repo
```

Git identity is automatically selected by directory — no manual config switching needed.

## See also

- [SETUP.md](docs/SETUP.md) — Step-by-step new machine guide
- [ADD-COMPANY.md](docs/ADD-COMPANY.md) — How to add a second work company
- [SSH-KEYS.md](docs/SSH-KEYS.md) — 1Password SSH key setup
