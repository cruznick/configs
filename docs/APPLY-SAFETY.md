# Apply Safety

Use this when pulling the repo onto a machine that already has local shell,
Git, or work configuration.

## First Apply Or Update

Inspect before writing:

```bash
git -C ~/repos/personal/gh/configs pull --ff-only
chezmoi diff --source ~/repos/personal/gh/configs
chezmoi status --source ~/repos/personal/gh/configs
```

Apply only after reviewing changes to high-risk targets:

- `~/.zshrc`
- `~/.gitconfig`
- `~/bin/*`
- `~/homebrew/Brewfile.*`

Then run:

```bash
dots-health --fast
chezmoi apply --source ~/repos/personal/gh/configs
dots-brew status
dots-brew plan
```

## Reading Chezmoi Status

`chezmoi status` shows two columns.

- first column: local target changed since chezmoi last wrote it
- second column: target differs from the repo-rendered desired state

Common examples:

- ` M .zshrc`: repo has a pending update for `~/.zshrc`
- `M  .zshrc`: local `~/.zshrc` was hand-edited
- `MM .zshrc`: both are true; review carefully before apply
- ` R .chezmoiscripts/...`: an onchange script will run

## Safe Selective Apply

If `~/.zshrc` has local blocks that should not be deleted yet, apply narrower
targets instead:

```bash
chezmoi apply --source ~/repos/personal/gh/configs ~/.gitconfig
chezmoi apply --source ~/repos/personal/gh/configs ~/bin/dots-brew ~/bin/dots-brew-audit
chezmoi apply --source ~/repos/personal/gh/configs ~/homebrew/Brewfile.core ~/homebrew/Brewfile.dev ~/homebrew/Brewfile.apps
```

Run only scripts, without applying files:

```bash
chezmoi apply --source ~/repos/personal/gh/configs --include scripts
```

Use `--force` only after reading the diff. It answers overwrite prompts for
target-side edits.

## Local State Before Applying

Before applying a managed `~/.zshrc`, move machine-local shell state to local
files:

- startup and PATH bootstraps: `~/.zshenv`
- project/work secrets and temporary tokens: directory `.envrc`
- tool-generated blocks: their own local startup file or `~/.zshenv`

Before applying a managed `~/.gitconfig`, move machine-specific Git state to:

```text
~/.config/git/local.gitconfig
```

The managed Git config includes that file at the end so local values can
override repo defaults.

## Validation

Run this after edits and before pushing:

```bash
git diff --check
chezmoi execute-template --source ~/repos/personal/gh/configs '{{ includeTemplate "dot_gitconfig.tmpl" . }}' >/tmp/rendered-gitconfig
git config --file /tmp/rendered-gitconfig --list >/dev/null
chezmoi execute-template --source ~/repos/personal/gh/configs '{{ includeTemplate ".chezmoitemplates/homebrew-active-brewfile.tmpl" . }}' >/tmp/rendered-brewfile
dots-brew status
dots-brew plan
chezmoi status --source ~/repos/personal/gh/configs
```

For periodic drift checks, run:

```bash
dots-health
```

Use `dots-health --fast` when you want to skip the slower Homebrew dependency
check. The command is read-only; it does not apply dotfiles, install packages,
upgrade packages, or run cleanup.
