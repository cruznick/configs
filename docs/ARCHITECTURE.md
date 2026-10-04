# Dotfiles Architecture

## Merge Order

Effective config resolves in this order:

1. `profiles/defaults.toml`
2. `profiles/personal.toml` or `profiles/work.toml`
3. `profiles/machines/mac-dev.toml` or `profiles/machines/mac-minimal.toml`
4. `~/.config/dotfiles/overrides.toml`
5. `~/.config/dotfiles/work-contexts/*.toml`
6. environment variables

Merge semantics:
- maps deep-merge by key
- scalars are replaced by the later layer
- lists are replaced, never appended

Notes:
- work contexts are local-only
- work contexts affect only Git and direnv-related behavior
- local override `work_contexts = [...]` is an optional filter over local context files
- `profile = "work"` is only a generic support mode; concrete work identity is still path-scoped by local work contexts
- local overrides also deep-merge into repo config, including `optional_integrations`
- shared `.chezmoitemplates/base-config.json.tmpl` resolves profiles, presets, and overrides for both effective and Homebrew config; source-relative includes work from any directory
- `DOTFILES_PROFILE`, `DOTFILES_PROVIDER`, and `DOTFILES_MACHINE_PRESET` override selectors for that command; invalid selectors stop rendering rather than silently falling back
- capability presets do not select identity or private work contexts; local integration overrides take precedence over the preset
- work-context `enabled = false` is preserved, including for explicitly filtered contexts

## Repository Data Types

The repo now separates three different configuration models:

- declarative dotfiles and bootstrap-managed shell/tooling state via chezmoi
- local private work-context files outside the repo
- manual app-export artifacts under `apps/`

Manual app exports are intentionally not part of bootstrap or `chezmoi apply`.

## Homebrew Model

Homebrew is declarative and Brewfile-driven.

Source files:
- `homebrew/Brewfile.core`
- `homebrew/Brewfile.dev`
- `homebrew/Brewfile.apps`
- `homebrew/Brewfile.personal`
- `homebrew/Brewfile.extras`
- `homebrew/Brewfile.work`

Activation:
- the active Brewfile is rendered from those files via `.chezmoitemplates/homebrew-active-brewfile.tmpl`
- machine-local enablement is controlled by `optional_integrations.homebrew_*`
- `homebrew_personal` defaults from the active profile: enabled for `personal`, disabled otherwise
- work-context data is not used for Homebrew selection
- normal apply/sync installs missing declared packages with `--no-upgrade`; explicit `dots-brew update` upgrades only the active Brewfile, not every installed package
- cleanup previews the audit's typed candidate lists; only untracked requested formulae and casks can be removed, and audit exclusions stay protected

## asdf Tool Versions

`dot_tool-versions` declares runtime and CLI versions. The macOS asdf onchange
hook runs after files are deployed, uses the asdf executable, and runs from the
home directory. Its rendered content includes the version file's checksum so a
version edit triggers synchronization. See [ASDF.md](ASDF.md).

The `personal` and `work` groups are both repo-tracked. Their activation is
profile/config driven, not based on private work-context files. This keeps
package selection reproducible while avoiding accidental installation of
personal apps on a work-profile machine.

## Local Session Model

The managed `~/.zshrc` is for shared shell behavior only. Machine-local session
bootstraps and tool-generated blocks live outside this repo, commonly in
`~/.zshenv`. Secret-bearing and temporary work variables live in direnv-managed
`.envrc` files under work directories.

See [LOCAL-SESSION.md](LOCAL-SESSION.md).

See [LOCAL-OVERRIDES.md](LOCAL-OVERRIDES.md) for concrete local-only file
examples.

## Debugging

Use:

```bash
dots-debug --json
```

Stable keys in the JSON output:
- `active_profile`
- `active_provider`
- `machine_preset`
- `selected_work_contexts`
- `override_file`
- `env_overrides`
- `optional_integrations`

For raw chezmoi inspection:

```bash
chezmoi execute-template '{{ includeTemplate ".chezmoitemplates/effective-config.json.tmpl" . }}'
```

For apply safety, target-side edits, and validation commands, see
[APPLY-SAFETY.md](APPLY-SAFETY.md).

For per-machine onboarding, supported presets, and future Linux considerations,
see [MULTI-MACHINE.md](MULTI-MACHINE.md). GitHub Actions validates macOS only.
