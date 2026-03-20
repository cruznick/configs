# Adding a Local Work Context

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
- [profiles/work-context.example.toml](/Users/bjm/repos/personal/gh/configs/profiles/work-context.example.toml)

Important rules:
- `name` is optional
- work contexts affect only Git and direnv-related behavior
- concrete company/client details remain local-only
- `.envrc.example` may be generated, but real secret-bearing `.envrc` is still manual

## Removal

```bash
dots-work remove --slug=<slug>
```

Legacy `.chezmoidata/companies.toml` support is transitional only and will be removed after migration.
