# cruznick/configs

Personal dotfiles managed by [chezmoi](https://chezmoi.io).

## Bootstrap

macOS or Linux:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cruznick/configs/main/install.sh)"
```

What bootstrap does:
1. Installs Homebrew on macOS if needed
2. Installs chezmoi if needed
3. Verifies or repairs the chezmoi source
4. Creates `~/.config/dotfiles/overrides.toml` if missing
5. Runs `chezmoi apply`
6. Runs optional setup hooks without blocking bootstrap
7. Applies the active Homebrew Brewfile groups on macOS when Homebrew is available

## Config Model

Effective config resolves in this order:
1. `profiles/defaults.toml`
2. `profiles/personal.toml` or `profiles/work.toml`
3. `~/.config/dotfiles/overrides.toml`
4. `~/.config/dotfiles/work-contexts/*.toml`
5. environment variables

Merge rules:
- maps deep-merge
- scalars replace
- lists replace

Profile model:
- `profile = personal | work`
- `provider = gh | gl`

`work` is a generic support mode only. Concrete work identity still comes from
local work-context files and path-based matching, not from a single global
profile switch.

Local machine selection lives in:

```toml
# ~/.config/dotfiles/overrides.toml
profile = "personal"
provider = "gh"
work_contexts = []
primary_machine = false
```

Notes:
- local work contexts are discovered from `~/.config/dotfiles/work-contexts/*.toml`
- `work_contexts = [...]` is an optional local filter
- work contexts affect only Git and direnv-related behavior

## Manual App Exports

Manual app-export artifacts live under `apps/`.

- `apps/istat-menus/`
- `apps/rectangle-pro/`

These are reference exports only.

- They are not managed by `chezmoi apply`
- They are not part of bootstrap
- They must be exported and imported manually

See [apps/README.md](/Users/bjm/repos/personal/gh/configs/apps/README.md).

## Homebrew

Homebrew state is declarative and Brewfile-driven.

Source of truth:
- `homebrew/Brewfile.core`
- `homebrew/Brewfile.dev`
- `homebrew/Brewfile.apps`
- `homebrew/Brewfile.extras`

The active machine Brewfile is rendered from those repo-tracked group files using
the current effective config. The install hook and audit helper both consume that
rendered Brewfile.

Default group enablement:
- `homebrew_core = true`
- `homebrew_dev = true`
- `homebrew_apps = true`
- `homebrew_extras = false`

Machine-local group selection uses the existing override file:

```toml
# ~/.config/dotfiles/overrides.toml
[optional_integrations]
homebrew_core = true
homebrew_dev = true
homebrew_apps = true
homebrew_extras = false
```

Workflows:
- Update declared brew state: `dots-brew update`
- Install/sync declared brew state: `dots-brew sync`
- Preview sync work: `dots-brew plan`
- Show active groups and drift summary: `dots-brew status`
- Audit drift: `dots-brew audit` or `dots-brew audit --missing`
- Show active groups: `dots-brew groups`
- Add a package/app: edit the right file under `homebrew/Brewfile.*`, then run `chezmoi apply` or `dots-brew sync`
- Remove a package/app: remove it from the right file under `homebrew/Brewfile.*`, then run `chezmoi apply` or `dots-brew sync`

Operational rule:
- direct `brew install` is fine for testing, but persistent state must be added to `homebrew/Brewfile.*`

See [docs/HOMEBREW.md](docs/HOMEBREW.md).

## Debugging

```bash
dots-debug --json
dots-profile
```

Stable keys in `dots-debug --json`:
- `active_profile`
- `active_provider`
- `selected_work_contexts`
- `override_file`
- `env_overrides`
- `optional_integrations`

## Update Workflow

```bash
dots-apply
dots-update
dots-diff
dots-edit
dots-debug --json
dots-profile
dots-brew update
dots-brew plan
dots-brew status
dots-brew audit --missing
```

## Optional Integrations

These never block baseline bootstrap:
- Homebrew package sync if Homebrew is unavailable during apply or bundle operations fail
- Homebrew extras
- zinit
- asdf
- 1Password SSH public key export

If a dependency or secret is missing, bootstrap logs a warning and continues.

## Local Work Contexts

Concrete work contexts are local-only and live in:
- `~/.config/dotfiles/work-contexts/*.toml`

Create one with:

```bash
dots-work create
```

See [docs/WORK-CONTEXTS.md](docs/WORK-CONTEXTS.md).

## Secrets

Secrets remain local-only:
- 1Password vault/account setup
- SSH private keys
- direnv `.envrc`
- tokens and credentials

Public keys may be exported to `~/.ssh/signing-pubs/`, but export is optional and non-fatal.

See [docs/SSH-KEYS.md](docs/SSH-KEYS.md).

## Legacy Compatibility

Legacy `.chezmoidata/companies.toml` support is transitional only during migration.
It is no longer the source of truth and will be removed after migration is complete.
