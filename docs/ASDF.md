# asdf Tool Versions

asdf owns the versions declared in `dot_tool-versions`: Node.js, Python, Go,
Terraform, kubectl, and Helm. Homebrew installs the asdf executable through the
dev Brewfile group. This configuration supports asdf 0.16 and later; the old
`asdf.sh` shell initializer is no longer used.

## Synchronization

On macOS, `.chezmoiscripts/run_onchange_20-setup-asdf.sh.tmpl` runs after chezmoi
deploys files. It adds missing plugins, installs the home `.tool-versions`, enables
corepack when available, and refreshes shims. It always runs from the home
directory, even if `chezmoi apply` was invoked inside another project.

The hook's rendered content includes the checksum of `dot_tool-versions`.
Changing that file therefore triggers installation on the next full apply. The
new hook also runs once when upgrading from the former `run_once_20` hook.

To defer automatic asdf setup on a machine, set:

```toml
# ~/.config/dotfiles/overrides.toml
[optional_integrations]
asdf = false
```

This controls the installation hook. It does not uninstall tools or change the
shell's shim support. Linux continues to skip this macOS setup hook.

## Failures And Retries

Missing asdf, plugin setup failures, or failed installs warn without blocking
the rest of bootstrap. A failed install does not print a success message.
Because a non-fatal onchange hook can be recorded as completed, fix the cause
and explicitly retry rather than relying on an unchanged apply to run it again.

If the plugins are already installed:

```bash
cd "$HOME"
asdf install
asdf reshim
```

To repeat the complete plugin and version setup, including after installing a
previously missing asdf executable:

```bash
set -o pipefail
chezmoi execute-template --source ~/repos/personal/gh/configs \
  '{{ includeTemplate ".chezmoiscripts/run_onchange_20-setup-asdf.sh.tmpl" . }}' | bash
```

Apply the desired `.tool-versions` first if retrying without a full apply.

## Shell And Checks

The managed zsh configuration puts `${ASDF_DATA_DIR:-$HOME/.asdf}/shims` before
Homebrew and removes duplicate copies of that shim directory, including when it
was inherited from the parent shell. It does not source the old asdf initializer.

`dots-health` verifies all six shim paths and checks that each repo-declared
version is installed. Project-specific `.tool-versions` files still control the
selected versions within those projects.
