# cruznick/configs

Personal dotfiles managed by [chezmoi](https://chezmoi.io).

## Bootstrap

macOS (the supported platform):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cruznick/configs/main/install.sh)"
```

What bootstrap does:

1. Installs Homebrew on macOS if needed
2. Installs chezmoi if needed
3. Selects a machine preset and creates `~/.config/dotfiles/overrides.toml` if missing; existing overrides are preserved
4. Verifies or repairs the chezmoi source; existing sources update with `git pull --ff-only`, without an implicit apply
5. Runs `chezmoi apply`
6. Runs optional setup hooks without blocking bootstrap
7. Applies the active Homebrew Brewfile groups on macOS when Homebrew is available

Choose `mac-dev` (default) or `mac-minimal` before the first apply:

```bash
bash install.sh --preset mac-minimal
```

Interactive bootstrap asks if no preset is supplied and no local overrides exist.
Noninteractive bootstrap defaults to `mac-dev`. See
[docs/MULTI-MACHINE.md](docs/MULTI-MACHINE.md) for presets, per-Mac setup, and the
possible future Linux approach. Linux is not a tested/supported setup today.

For an existing machine, review [docs/APPLY-SAFETY.md](docs/APPLY-SAFETY.md)
before running `chezmoi apply`.

For a personal Mac, follow [docs/PERSONAL-MAC.md](docs/PERSONAL-MAC.md)
for the update checklist, local identity settings, and verification.

## Config Model

Effective config resolves in this order:

1. `profiles/defaults.toml`
2. `profiles/personal.toml` or `profiles/work.toml`
3. `profiles/machines/mac-dev.toml` or `profiles/machines/mac-minimal.toml`
4. `~/.config/dotfiles/overrides.toml`
5. `~/.config/dotfiles/work-contexts/*.toml`
6. environment variables (`DOTFILES_PROFILE`, `DOTFILES_PROVIDER`, `DOTFILES_MACHINE_PRESET`)

Merge rules:
- maps deep-merge
- scalars replace
- lists replace

Profile model:
- `profile = personal | work`
- `provider = gh | gl`
- `machine_preset = mac-dev | mac-minimal` (capabilities, independent of identity)

`work` is a generic support mode only. Concrete work identity still comes from
local work-context files and path-based matching, not from a single global
profile switch.

Local machine selection lives in:

```toml
# ~/.config/dotfiles/overrides.toml
machine_preset = "mac-dev"
profile = "personal"
provider = "gh"
work_contexts = []
primary_machine = false

[identity]
# Optional for built-in Personal/Private/Employee vaults with unique item titles.
# Recommended for shared/custom vaults or ambiguous SSH item names.
op_vault = ""
```

Notes:
- local work contexts are discovered from `~/.config/dotfiles/work-contexts/*.toml`
- `work_contexts = [...]` is an optional local filter
- `[context].enabled = false` excludes a context even when the filter names it
- work contexts affect only Git and direnv-related behavior
- `[identity].op_vault` is machine-local and may be needed for repo-managed 1Password SSH key export/pinning

Profile files resolve against the chezmoi source directory. Rendering and applying
the configuration work from any current directory.

## Manual App Exports

Manual app-export artifacts live under `apps/`.

- `apps/istat-menus/`
- `apps/rectangle-pro/`

These are reference exports only.

- They are not managed by `chezmoi apply`
- They are not part of bootstrap
- They must be exported and imported manually

See [apps/README.md](apps/README.md).

## Homebrew

Homebrew state is declarative and Brewfile-driven.

Source of truth:
- `homebrew/Brewfile.core`
- `homebrew/Brewfile.dev`
- `homebrew/Brewfile.apps`
- `homebrew/Brewfile.personal`
- `homebrew/Brewfile.extras`
- `homebrew/Brewfile.work`

The active machine Brewfile is rendered from those repo-tracked group files using
Homebrew-specific config from profiles and `~/.config/dotfiles/overrides.toml`.
It does not parse private work-context files, so a broken local work context
does not block Brewfile rendering.

Group intent:
- `core`: baseline CLI tools
- `dev`: developer and infrastructure tooling
- `apps`: general desktop apps
- `personal`: personal-profile tools and apps, skipped by default on work-profile machines
- `extras`: optional heavy, niche, media, or game-related tools
- `work`: work-profile tools

Default group enablement for `mac-dev`:
- `homebrew_core = true`
- `homebrew_dev = true`
- `homebrew_apps = true`
- `homebrew_personal = true` when `profile = "personal"`, otherwise `false`
- `homebrew_extras = false`
- `homebrew_work = false`

`mac-minimal` explicitly enables only `homebrew_core`.

Machine-local group selection uses the existing override file:

```toml
# ~/.config/dotfiles/overrides.toml
[optional_integrations]
homebrew_core = true
homebrew_dev = true
homebrew_apps = true
homebrew_personal = true
homebrew_extras = false
homebrew_work = false
```

Workflows:
- Explicitly install/upgrade active declared brew state: `dots-brew update`
- Install missing declared packages without explicit upgrades: `dots-brew sync`
- Preview sync work: `dots-brew plan`
- Preview removal candidates without changing packages: `dots-brew cleanup --dry-run`
- Cleanup undeclared packages explicitly: `dots-brew cleanup`
- Show active groups and drift summary: `dots-brew status`
- Audit drift: `dots-brew audit` or `dots-brew audit --missing`
- Show active groups: `dots-brew groups`
- Add a package/app: edit the right file under `homebrew/Brewfile.*`, then run `chezmoi apply` or `dots-brew sync`
- Remove a package/app: remove it from the right file under `homebrew/Brewfile.*`, then run `chezmoi apply` or `dots-brew sync`

Operational rule:
- direct `brew install` is fine for testing, but persistent state must be added to `homebrew/Brewfile.*`
- personal tools that should not follow a work profile belong in `homebrew/Brewfile.personal`
- `chezmoi apply` and `dots-brew sync` do not uninstall undeclared packages
- apply/sync use `--no-upgrade`; Homebrew may still update shared dependencies needed by newly installed packages
- destructive removal of undeclared packages is manual-only via `dots-brew cleanup`
- cleanup uses the audit's untracked requested formulae and casks; intentional exclusions and dependency-only installs are retained
- `chezmoi` is intentionally left unmanaged by Brewfiles because bootstrap installs it separately
- Version-pinned runtimes and CLIs (`nodejs`, `python`, `golang`, `terraform`, `kubectl`, `helm`) are managed by asdf, not Homebrew.

See [docs/HOMEBREW.md](docs/HOMEBREW.md).

The asdf setup hook supports the executable-based asdf (0.16+) and reruns when
`dot_tool-versions` changes. See [docs/ASDF.md](docs/ASDF.md) for setup and retries.

## Debugging

```bash
dots-debug --json
dots-profile
dots-health
```

Stable keys in `dots-debug --json`:
- `active_profile`
- `active_provider`
- `machine_preset`
- `selected_work_contexts`
- `override_file`
- `env_overrides`
- `optional_integrations`

## Update Workflow

```bash
git -C ~/repos/personal/gh/configs pull --ff-only
chezmoi diff --source ~/repos/personal/gh/configs
chezmoi status --source ~/repos/personal/gh/configs
dots-health --fast
chezmoi apply --source ~/repos/personal/gh/configs
dots-diff
dots-edit
dots-debug --json
dots-profile
dots-brew plan
dots-brew cleanup --dry-run
dots-brew status
dots-brew audit --missing
```

When you intentionally want package upgrades, run `dots-brew update` separately.

See [docs/APPLY-SAFETY.md](docs/APPLY-SAFETY.md) for selective apply,
target-side edit handling, and validation commands.

Run regression checks before committing changes:

```bash
python3 -m unittest discover -s tests -v
```

These use isolated fixtures and mocked package commands. They do not install or
remove packages or change your home configuration.
GitHub Actions runs the same suite on macOS for pushes to `main` and pull requests,
including both machine presets, both identity profiles, optional toggles, and bootstrap safety.

## Optional Integrations

These never block baseline bootstrap:
- Homebrew package sync if Homebrew is unavailable during apply or bundle operations fail
- Homebrew extras
- zinit
- asdf
- 1Password SSH public key export

If a dependency or secret is missing, bootstrap logs a warning and continues.
Integration flags govern hook execution, shell initialization, and relevant health
checks. Disabling an integration does not uninstall software, delete keys, or clear
environment variables inherited from machine-local startup files. See
[MULTI-MACHINE.md](docs/MULTI-MACHINE.md) for individual flag behavior.

## Local Work Contexts

Concrete work contexts are local-only and live in:
- `~/.config/dotfiles/work-contexts/*.toml`

Create one with:

```bash
dots-work create
```

See [docs/WORK-CONTEXTS.md](docs/WORK-CONTEXTS.md).

## Local Session Layers

Machine-local shell bootstraps, tool-managed PATH blocks, and secret-bearing
work session variables stay outside the managed `.zshrc`.

Use:
- `dot_zshrc.tmpl` for shared shell behavior
- local startup files such as `~/.zshenv` for machine-local session bootstrap
- work-directory `.envrc` files for secrets, cloud profiles, and temporary tokens

See [docs/LOCAL-SESSION.md](docs/LOCAL-SESSION.md).

Examples for `~/.zshenv`, `~/.config/git/local.gitconfig`, `.envrc`, and local
work-context TOML live in [docs/LOCAL-OVERRIDES.md](docs/LOCAL-OVERRIDES.md).

## Secrets

Secrets remain local-only:
- 1Password vault/account setup
- SSH private keys
- direnv `.envrc`
- tokens and credentials

Public keys may be exported to `~/.ssh/signing-pubs/` as SSH/signing selector files, but export is optional and non-fatal.

See [docs/SSH-KEYS.md](docs/SSH-KEYS.md).

## Legacy Compatibility

Legacy `.chezmoidata/companies.toml` support is transitional only during migration.
It is no longer the source of truth and will be removed after migration is complete.
