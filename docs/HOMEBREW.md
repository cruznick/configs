# Homebrew

## Source Of Truth

Homebrew state is declared in repo-tracked Brewfiles:

- `homebrew/Brewfile.core`
- `homebrew/Brewfile.dev`
- `homebrew/Brewfile.apps`
- `homebrew/Brewfile.extras`
- `homebrew/Brewfile.work` 

These files are the only persistent source of truth for Homebrew packages.
The machine-specific active Brewfile is rendered from them by:

- [.chezmoitemplates/homebrew-active-brewfile.tmpl](/Users/bjm/repos/personal/gh/configs/.chezmoitemplates/homebrew-active-brewfile.tmpl)

The install hook uses that rendered Brewfile during `chezmoi apply`.

## Machine Selection

Group enablement is controlled through the existing local override model:

```toml
# ~/.config/dotfiles/overrides.toml
[optional_integrations]
homebrew_core = true
homebrew_dev = true
homebrew_apps = true
homebrew_extras = false
homebrew_work = false
```

Default behavior from the repo:

- `homebrew_core = true`
- `homebrew_dev = true`
- `homebrew_apps = true`
- `homebrew_extras = false`
- `homebrew_work = false`

This stays machine-local, debuggable, and separate from private work-context data.

## Workflows

Update everything declared for the current machine:

```bash
dots-brew update
```

Install or re-sync the declared state without a general upgrade:

```bash
dots-brew sync
```

Normal sync behavior:

- runs `brew bundle install` for the active Brewfile
- does not uninstall undeclared packages
- is what `chezmoi apply` uses in the brew onchange hook

Preview what `dots-brew sync` would do:

```bash
dots-brew plan
```

This previews install or upgrade work only. It does not perform cleanup.

Explicitly remove undeclared packages:

```bash
dots-brew cleanup
```

This is destructive and manual-only. It is not part of bootstrap, `chezmoi apply`,
or `dots-brew sync`.

Show active groups and a drift summary:

```bash
dots-brew status
```

Add a package or app:

1. Edit the appropriate file under `homebrew/Brewfile.*`
2. Run `chezmoi apply` or `dots-brew sync`

Remove a package or app:

1. Remove the entry from the appropriate file under `homebrew/Brewfile.*`
2. Run `chezmoi apply` or `dots-brew sync`

Audit drift between installed packages and the active declared state:

```bash
dots-brew audit
dots-brew audit --missing
```

This reports drift only. It does not uninstall anything.

Show which groups are currently enabled:

```bash
dots-brew groups
```

Bootstrap a new machine:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cruznick/configs/main/install.sh)"
```

That installs Homebrew if needed, initializes chezmoi, applies the repo, and then
installs the active Homebrew Brewfile groups on macOS.

## Notes

- Direct `brew install` is acceptable for short-lived testing.
- Persistent Homebrew state must be recorded in `homebrew/Brewfile.*`.
- Brew setup remains non-fatal during bootstrap and apply.
- `chezmoi` is intentionally unmanaged by Brewfiles because bootstrap installs it separately.
- `terraform` and `kubectl` remain managed outside Homebrew to avoid shim conflicts.
- `macfuse` remains a manual install.
