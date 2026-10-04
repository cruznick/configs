# Homebrew

## Source Of Truth

Homebrew state is declared in repo-tracked Brewfiles:

- `homebrew/Brewfile.core`
- `homebrew/Brewfile.dev`
- `homebrew/Brewfile.apps`
- `homebrew/Brewfile.personal`
- `homebrew/Brewfile.extras`
- `homebrew/Brewfile.work`

These files are the only persistent source of truth for Homebrew packages.
The machine-specific active Brewfile is rendered from them by:

- [.chezmoitemplates/homebrew-active-brewfile.tmpl](../.chezmoitemplates/homebrew-active-brewfile.tmpl)

The install hook uses that rendered Brewfile during `chezmoi apply`. Brewfile
rendering reads only profiles and `~/.config/dotfiles/overrides.toml`; it does
not parse private work-context files.

## Group Semantics

Use the narrowest group that describes why the package should be present:

- `core`: baseline CLI tools expected on every managed machine.
- `dev`: developer and infrastructure tooling.
- `apps`: general desktop apps that are not profile-specific.
- `personal`: personal-profile apps and tools that should not install by default on work-profile machines.
- `extras`: optional heavy, niche, media, or game-related tools.
- `work`: work-profile tools that should not install by default on personal-profile machines.

Examples:

- Put `git`, `jq`, `ripgrep`, and shell ergonomics in `core`.
- Put `docker`, `gh`, `awscli`, and Kubernetes tools in `dev`.
- Put normal daily desktop apps such as browsers, terminal apps, and productivity apps in `apps`.
- Put personal-only tools such as `beets`, `balenaetcher`, game-adjacent apps, personal media utilities, and remote-support tools in `personal` when they should not follow a work profile.
- Put large optional apps or tools that are useful only on selected machines in `extras`.
- Put company-required apps and CLIs in `work`.

If a package is installed briefly for testing, it does not need to be declared.
If it should survive rebuilds or new-machine setup, declare it in one of these
Brewfiles.

## Machine Selection

Presets provide group defaults: `mac-dev` enables core/dev/apps; `mac-minimal`
enables core only. Work apps and extras remain opt-in. Each group is independent:
disabling core does not disable another enabled group. Local flags override presets:

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

Default behavior for `mac-dev` (also used by existing overrides without a preset):

- `homebrew_core = true`
- `homebrew_dev = true`
- `homebrew_apps = true`
- `homebrew_personal = true` when `profile = "personal"`, otherwise `false`
- `homebrew_extras = false`
- `homebrew_work = false`

`mac-minimal` explicitly enables only `homebrew_core`.

The `personal` group is profile-gated. It defaults to enabled only when the
active profile is `personal`. On a work-profile machine, it defaults to disabled
unless the local override file explicitly enables it.

The `work` group is opt-in. It defaults to disabled even when the active profile
is `work`, because concrete work requirements vary by machine and company.

This stays machine-local, debuggable, and separate from private work-context data.

## Profile Examples

Personal machine with personal tools and extras:

```toml
# ~/.config/dotfiles/overrides.toml
profile = "personal"
provider = "gh"

[optional_integrations]
homebrew_core = true
homebrew_dev = true
homebrew_apps = true
homebrew_personal = true
homebrew_extras = true
homebrew_work = false
```

Work machine without personal apps:

```toml
# ~/.config/dotfiles/overrides.toml
profile = "work"
provider = "gh"

[optional_integrations]
homebrew_core = true
homebrew_dev = true
homebrew_apps = true
homebrew_personal = false
homebrew_extras = false
homebrew_work = true
```

Minimal machine:

```toml
# ~/.config/dotfiles/overrides.toml
profile = "personal"

[optional_integrations]
homebrew_core = true
homebrew_dev = false
homebrew_apps = false
homebrew_personal = false
homebrew_extras = false
homebrew_work = false
```

You can inspect the resolved result with:

```bash
dots-brew groups
dots-debug --json
```

## Workflows

Update everything declared for the current machine:

```bash
dots-brew update
```

This refreshes Homebrew metadata and runs `brew bundle install --upgrade` for the
active Brewfile. It does not run a global `brew upgrade` or upgrade undeclared
packages intentionally. Homebrew can still update required shared dependencies.

Install missing declared packages without explicitly upgrading installed ones:

```bash
dots-brew sync
```

Normal sync behavior:

- runs `brew bundle install --no-upgrade` for the active Brewfile
- does not uninstall undeclared packages
- is what `chezmoi apply` uses in the brew onchange hook

Preview what `dots-brew sync` would do:

```bash
dots-brew plan
```

This uses `brew bundle check --no-upgrade` to report missing packages. It does not
install, upgrade, or perform cleanup. `dots-health` uses the same check, so an
available upgrade alone is not treated as missing-package drift.

This is predictable update *intent*, not a package lockfile. Installing a missing
package can update a shared dependency, and self-updating apps can change outside
Homebrew. See [Homebrew's Bundle documentation](https://docs.brew.sh/Brew-Bundle-and-Brewfile).

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

If the package is currently reported as untracked, decide whether it should be
shared, personal-profile only, work-profile only, optional, or removed before
adding it.

Remove a package or app:

1. Remove the entry from the appropriate file under `homebrew/Brewfile.*`
2. Run `chezmoi apply` or `dots-brew sync`

Removal from a Brewfile stops future installs but does not uninstall the package.
Use `dots-brew cleanup` or an explicit `brew uninstall ...` when you want to
remove the installed package too.

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

That installs Homebrew if needed, selects/preserves the local preset before
initializing/updating chezmoi's source, applies the repo, and installs missing
packages from the active Homebrew groups. See [MULTI-MACHINE.md](MULTI-MACHINE.md).

## Notes

- Direct `brew install` is acceptable for short-lived testing.
- Persistent Homebrew state must be recorded in `homebrew/Brewfile.*`.
- The `personal` group is repo-tracked but profile-scoped; it is not a local-only Brewfile.
- Brew setup remains non-fatal during bootstrap and apply.
- `chezmoi` is intentionally unmanaged by Brewfiles because bootstrap installs it separately.
- Version-pinned runtimes and CLIs (`nodejs`, `python`, `golang`, `terraform`, `kubectl`, `helm`) remain managed by asdf to avoid shim conflicts.
- `uv` remains Homebrew-managed; asdf owns the Python runtime while `uv` manages project environments and packages.
- `docker-completion` is intentionally not declared; Homebrew marks it deprecated, and `docker` now owns the completion files.
- The work group uses `claude-code@latest` for Claude Code's latest channel, matching the installed CLI selection.
- Core declares Homebrew Bash because the audit helper requires Bash 4+ (macOS ships Bash 3.2).
- `chatgpt-classic` belongs to the apps group; core contains no GUI casks.
- Cleanup is always manual through `dots-brew cleanup`; neither `chezmoi apply` nor `dots-brew sync` uninstalls undeclared packages.
