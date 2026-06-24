# Local Session Layers

This repo owns shared, reproducible shell behavior. Machine-local tools,
company/client bootstraps, and secret-bearing session state stay outside the
repo.

## Layer Model

Use these layers in order from broadest to narrowest.

1. Repo-managed shell config
   - Source: `dot_zshrc.tmpl`
   - Target: `~/.zshrc`
   - Use for shared shell defaults, aliases, Homebrew path setup, asdf loading,
     direnv hook loading, and non-secret tooling behavior.
   - Do not let third-party installers append unmanaged blocks here.

2. Local session bootstrap
   - Source/target: local files outside this repo, commonly `~/.zshenv`.
   - Use for machine-local bootstraps that must exist in every zsh process,
     such as company CLI startup files or tool-managed PATH blocks.
   - Tool-managed blocks should use clear sentinel comments so their own setup
     scripts can replace them idempotently.

3. Work directory environment
   - Source/target: local `.envrc` files under work directories.
   - Use for secrets, cloud profiles, temporary tokens, per-company registries,
     and project/session variables.
   - These files are loaded by direnv when entering the directory and unloaded
     when leaving it.

4. Local work-context metadata
   - Source/target: `~/.config/dotfiles/work-contexts/*.toml`
   - Use for non-secret metadata consumed by these dotfiles, such as work
     context slug, Git identity, matched repo roots, SSH aliases, and direnv
     root directories.
   - Files must be valid TOML. Use TOML arrays, not shell arrays.

## Ownership Rules

- Shared dotfiles belong in this repo.
- Machine-local bootstrap belongs in local startup files outside this repo.
- Secret-bearing work configuration belongs in direnv-managed `.envrc` files.
- Temporary tokens do not belong in managed dotfiles.
- Generated or installer-managed blocks should not be hand-copied into
  `dot_zshrc.tmpl`; keep them in the local layer that owns them.

## Tooling Boundary

Homebrew installs shared packages and GUI apps from `homebrew/Brewfile.*`.
asdf owns version-pinned runtimes and CLIs:

- `nodejs`
- `python`
- `golang`
- `terraform`
- `kubectl`
- `helm`

The managed zsh config prepends `ASDF_DATA_DIR/shims` after asdf loads so these
tools resolve through asdf before Homebrew binaries.

`uv` remains Homebrew-managed. asdf owns the Python runtime; `uv` manages
project environments and packages.

## Apply Checklist

Before `chezmoi apply`:

```bash
chezmoi diff --source ~/repos/personal/gh/configs
dots-brew status
```

After `chezmoi apply`:

```bash
type -a kubectl helm terraform
dots-brew status
chezmoi status --source ~/repos/personal/gh/configs
```

If a tool installer modifies `~/.zshrc`, move that block back to the local
session layer and keep the managed template clean.
