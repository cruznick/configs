# Migration Plan

## Legacy Company Data

Legacy `.chezmoidata/companies.toml` is supported only as a transitional compatibility layer.

Current behavior:
- local `~/.config/dotfiles/work-contexts/*.toml` is the preferred source of truth for private work contexts
- legacy company data is only used as a temporary compatibility layer when no local work contexts exist

Planned removal:
- legacy support will be removed after the repo is fully migrated to local work-context files
- do not treat legacy data as a permanent parallel source of truth

## Target State

- repo-tracked reusable generic configuration only
- local override file only for machine-specific non-secret selection
- local work-context files for private Git/direnv behavior
- no unmanaged `~/.gitconfig-work-*`
- no unmanaged `~/.zshrc.d/work-*.zsh`
