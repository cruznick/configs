# Homebrew

## Source Of Truth

Homebrew state is declared in repo-tracked Brewfiles:

- `homebrew/Brewfile.core`
- `homebrew/Brewfile.dev`
- `homebrew/Brewfile.apps`
- `homebrew/Brewfile.extras`

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
```

Default behavior from the repo:

- `homebrew_core = true`
- `homebrew_dev = true`
- `homebrew_apps = true`
- `homebrew_extras = false`

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

Preview what `dots-brew sync` would do:

```bash
dots-brew plan
```

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
- `terraform` and `kubectl` remain managed outside Homebrew to avoid shim conflicts.
- `macfuse` remains a manual install.
