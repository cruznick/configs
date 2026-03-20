# cruznick/configs

Personal dotfiles managed by [chezmoi](https://chezmoi.io).

## Bootstrap

macOS or Linux:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cruznick/configs/master/install.sh)"
```

What bootstrap does:
1. Installs Homebrew on macOS if needed
2. Installs chezmoi if needed
3. Verifies or repairs the chezmoi source
4. Creates `~/.config/dotfiles/overrides.toml` if missing
5. Runs `chezmoi apply`
6. Runs optional setup hooks without blocking bootstrap

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
```

## Optional Integrations

These never block baseline bootstrap:
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

See [docs/ADD-COMPANY.md](docs/ADD-COMPANY.md).

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
