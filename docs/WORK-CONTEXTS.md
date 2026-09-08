# Local Work Contexts

Work contexts are local-only. They are not stored in the Git-tracked dotfiles repo.

## Quick path

```bash
dots-work create
```

This creates:
- `~/.config/dotfiles/work-contexts/<slug>.toml`
- optional local work directories
- optional `.envrc.example`

Then it runs `chezmoi apply`.

## Local work-context schema

See:
- [profiles/work-context.example.toml](../profiles/work-context.example.toml)

Important rules:
- `name` is optional
- work contexts affect only Git and direnv-related behavior
- concrete company/client details remain local-only
- `.envrc.example` may be generated, but real secret-bearing `.envrc` is still manual
- work-context files must be valid TOML; use `key = ["value"]` arrays, not shell arrays
- `[context].enabled` defaults to `true` only when omitted; an explicit `false` always disables the context
- `work_contexts = [...]` filters enabled contexts; listing a disabled context does not reactivate it
- machine/session bootstrap belongs in local startup files such as `~/.zshenv`, not in managed `.zshrc`

## Disabling A Context

Keep the local file but stop applying its work identity:

```toml
[context]
slug = "example"
enabled = false
```

Review `chezmoi diff`, then apply. The context stays discoverable in debug output
but is absent from `selected_work_contexts`; its Git/SSH entries are omitted and
the work-config hook removes its stale generated Git fragment.

## Removal

```bash
dots-work remove --slug=<slug>
```

Legacy `.chezmoidata/companies.toml` support is transitional only and will be removed after migration.
