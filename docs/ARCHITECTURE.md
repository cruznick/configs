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
