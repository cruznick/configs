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
4. Prompts for identity and machine profile (see below)
5. Deploys all dotfiles to `$HOME`
6. Runs setup scripts: zinit install, brew packages, asdf tool versions, SSH key export from 1Password, work gitconfig generation, font install

### First-run prompts

| Prompt | Example |
|--------|---------|
| Full name | `Your Name` |
| Personal email | `you@gmail.com` |
| Personal GitHub username | `your-gh-username` |
| Work registry username | `your.name` (or blank) |
| 1Password vault name for SSH keys | `GitKeys` |
| Install work apps? | `y/n` |
| Install personal apps? | `y/n` |
| Install AI tools? | `y/n` |

These values are stored in `~/.config/chezmoi/chezmoi.toml` — never committed.

## Machine profiles

Three opt-in flags control which extra apps are installed:

| Flag | Apps installed |
|------|----------------|
| `installWorkApps` | openlens, okta-verify, pritunl, pup (Datadog CLI) |
| `installPersonalApps` | chatgpt, spotify, tidal, eqmac, meetingbar, shottr, istat-menus, elgato-stream-deck, logi-options+, yubico-authenticator |
| `installAiTools` | claude, claude-code, codex, codex-app |
| `primaryMachine` | deploys iStat Menus config from repo (set `false` on secondary machines) |

Core tools (git, neovim, k9s, docker, ghostty, cursor, 1password, etc.) are always installed.

Hardware-specific apps (macfuse) remain manual — install from https://osxfuse.github.io.

To change a flag on an existing machine, edit `~/.config/chezmoi/chezmoi.toml` and run `dots-apply`.

## Update workflow

```bash
dots-update           # pull latest from GitHub + apply
dots-apply            # apply local changes without pulling
dots-diff             # preview what would change
dots-edit             # open a dotfile in chezmoi's editor
dots-capture-rect     # sync Rectangle Pro shortcuts → repo (any machine)
dots-capture-istat    # sync iStat Menus config → repo (primary machine only)
dots-capture          # sync both (primary machine only)
dots-allow            # direnv allow in current directory
dots-brew-audit       # show installed packages not tracked in brew script
```

The brew install script re-runs automatically whenever it changes — adding or removing a package triggers a re-run on every machine via `dots-update`.

When you `cd` into a directory with an `.envrc` containing `op://` references, your shell auto-signs in to 1Password if the session has expired.

### Selective apply

To skip specific files during apply:

```bash
# Skip all scripts (no brew re-run, no font install)
chezmoi apply --exclude scripts

# Apply only specific files
chezmoi apply ~/Library/Preferences/com.knollsoft.Hookshot.plist
chezmoi apply ~/.zshrc

# Skip the app config plists (e.g. iStat not installed yet)
chezmoi apply --exclude encrypted $(chezmoi managed | grep -v "Library/Preferences")
```

### App config flow (iStat Menus, Rectangle Pro)

These configs are **repo → machine** only on secondary machines:
- `chezmoi apply` deploys the repo's config to every machine
- Only run `dots-capture-istat` on your **primary machine** (the one where you configure iStat Menus)
- Rectangle Pro shortcuts may differ per display setup — `dots-capture-rect` is safe to run on any machine

## Fonts

Fonts in `font/` are automatically installed to `~/Library/Fonts/` on first `chezmoi apply`. Currently includes FiraCode and Nerd-patched FiraCode variants.

## Repo structure

```
configs/
├── install.sh                    # curl entry point
├── .chezmoi.toml.tmpl            # first-run prompts (name, email, vault, machine flags)
├── .chezmoidata/
│   └── companies.toml            # gitignored — your local company registry
├── docs/
│   └── companies.toml.example   # committed example (copy to .chezmoidata/ and fill in)
├── .chezmoiscripts/              # setup scripts
│   ├── run_once_05-install-fonts.sh.tmpl
│   ├── run_onchange_10-install-brew.sh.tmpl
│   ├── run_once_20-setup-asdf.sh.tmpl
│   └── ...
├── font/                         # font files (deployed to ~/Library/Fonts/)
├── dot_zshrc.tmpl                # ~/.zshrc
├── dot_gitconfig.tmpl            # ~/.gitconfig (dynamic per-company includeIf)
├── dot_gitconfig-personal-*.tmpl # personal git identity configs
├── dot_ssh/config.tmpl           # ~/.ssh/config (host aliases per company)
├── dot_config/1Password/ssh/     # 1Password SSH agent config
├── dot_zshrc.d/work.zsh.tmpl    # template for per-company ~/.zshrc.d/work-<slug>.zsh
├── bin/                          # ~/bin scripts (work-config, git-check, glab-auto, …)
├── companies/example/            # reference template for a work company
├── docs/                         # Guides
└── legacy/                       # Pre-2025 configs (historical, not managed)
```

## Post-install (one-time manual steps)

### 1. Reload shell
```bash
source ~/.zshrc
```

### 2. Add SSH keys to GitHub/GitLab
```bash
ls ~/.ssh/signing-pubs/
```
Add each `.pub` file to the corresponding account (Authentication + Signing keys).

### 3. Add work companies
```bash
work-config add --slug=acme --platform=gh --email=you@acme.com
```

### 4. Set up global secrets
Edit `~/.envrc` — fill in the `op://` paths for global tokens (e.g. `GITHUB_TOKEN`), then run `dots-allow`.

### 5. Set up per-company secrets (direnv)
```bash
cd ~/repos/work/gh/<slug>
cp .envrc.example .envrc
# Edit .envrc — fill in op:// references to your 1Password items
direnv allow
```

## Secrets architecture

All secrets are loaded by [direnv](https://direnv.net) via `op read` calls — no static secret files.
Tokens are scoped to their identity's directory tree so personal and work credentials never bleed across contexts.

| Scope | File | When loaded | Example |
|-------|------|-------------|---------|
| Personal GitHub/GitLab tokens | `~/repos/personal/gh/.envrc` | On `cd` into any personal gh repo | `GITHUB_TOKEN` |
| Personal GitLab tokens | `~/repos/personal/gl/.envrc` | On `cd` into any personal gl repo | `GITLAB_TOKEN` |
| Per-company (registry, proxies) | `~/repos/work/<platform>/<slug>/.envrc` | On `cd` into work dir | `ARTIFACTORY_TOKEN` |
| Per-project (overrides) | project-level `.envrc` | On `cd` into project | `NODE_ENV`, `AWS_PROFILE` |

**Setup** (once per machine):
```bash
cp personal/.envrc.example ~/repos/personal/gh/.envrc
cp personal/.envrc.example ~/repos/personal/gl/.envrc
# Edit each — fill in op:// paths, then:
direnv allow ~/repos/personal/gh/.envrc
direnv allow ~/repos/personal/gl/.envrc
```

- On `cd` into a dir with `op://` references, the shell auto-signs in to 1Password if the session expired
- Tokens unload automatically when you `cd` out — no cross-identity leakage

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

## See also

- [docs/ADD-COMPANY.md](docs/ADD-COMPANY.md) — How to add a work company
- [docs/SSH-KEYS.md](docs/SSH-KEYS.md) — 1Password SSH key setup
