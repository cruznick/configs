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

- [.chezmoitemplates/homebrew-active-brewfile.tmpl](../.chezmoitemplates/homebrew-active-brewfile.tmpl)

The install hook uses that rendered Brewfile during `chezmoi apply`. Brewfile
rendering reads only profiles and `~/.config/dotfiles/overrides.toml`; it does
not parse private work-context files.

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

Preview removal candidates without changing installed packages:

```bash
dots-brew cleanup --dry-run
```

Remove the same candidates after confirmation:

```bash
dots-brew cleanup
```

This is destructive and manual-only. It is not part of bootstrap, `chezmoi apply`,
or `dots-brew sync`.

Cleanup uses the audit's `untracked_formulae` and `untracked_casks` lists. It
removes explicitly requested formulae and installed casks absent from the active
Brewfile. Formulae installed only as dependencies remain installed. Formula and
cask names are compared separately, including when both have the same name.

The audit's intentional formula exclusions are also protected from cleanup:
`chezmoi`, `terraform`, `kubernetes-cli`, `helm`, `nvm`, `pyenv`, `tcl-tk`,
`tcl-tk@8`, and `zlib`. The exclusion list lives in `bin/executable_dots-brew-audit`;
cleanup consumes that audit instead of maintaining a second list.

`dots-brew cleanup --force` skips the wrapper's confirmation only. Removal uses
ordinary `brew uninstall` with `HOMEBREW_NO_AUTOREMOVE=1`, preserving Homebrew's
dependency checks and limiting removal to the previewed packages. Declining the
prompt or providing no input cancels removal. An audit or uninstall failure stops
the command. No `brew bundle cleanup`, automatic dependency removal, tap removal,
or trust-store reset is performed. Manage orphaned dependencies separately if
you want to remove them.

Apply `dots-brew` and `dots-brew-audit` together when upgrading these helpers.

Show active groups and a drift summary:

```bash
dots-brew status
```

Run the full non-destructive dotfiles and Homebrew health check:

```bash
dots-health
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
- Version-pinned runtimes and CLIs (`nodejs`, `python`, `golang`, `terraform`, `kubectl`, `helm`) remain managed by asdf to avoid shim conflicts.
- `uv` remains Homebrew-managed; asdf owns the Python runtime while `uv` manages project environments and packages.
- `docker-completion` is intentionally not declared; Homebrew marks it deprecated, and `docker` now owns the completion files.
- The work group uses `claude-code@latest` for Claude Code's latest channel, matching the installed CLI selection.
- Cleanup is always manual through `dots-brew cleanup`; neither `chezmoi apply` nor `dots-brew sync` uninstalls undeclared packages.
