# Dotfiles Architecture

## Merge Order

Effective config resolves in this order:

1. `profiles/defaults.toml`
2. `profiles/personal.toml` or `profiles/work.toml`
3. `~/.config/dotfiles/overrides.toml`
4. `~/.config/dotfiles/work-contexts/*.toml`
5. environment variables

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
- `homebrew/Brewfile.extras`
- `homebrew/Brewfile.work`

Activation:
- the active Brewfile is rendered from those files via `.chezmoitemplates/homebrew-active-brewfile.tmpl`
- machine-local enablement is controlled by `optional_integrations.homebrew_*`
- work-context data is not used for Homebrew selection
- normal apply/sync installs declared packages only; destructive cleanup is explicit via `dots-brew cleanup`

## Debugging

Use:

```bash
dots-debug --json
```

Stable keys in the JSON output:
- `active_profile`
- `active_provider`
- `selected_work_contexts`
- `override_file`
- `env_overrides`
- `optional_integrations`

For raw chezmoi inspection:

```bash
chezmoi execute-template '{{ includeTemplate ".chezmoitemplates/effective-config.json.tmpl" . }}'
```
