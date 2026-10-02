# asdf Tool Versions

asdf owns the versions declared in `dot_tool-versions`: Node.js, Python, Go,
Terraform, kubectl, and Helm. Homebrew installs the asdf executable through the
dev Brewfile group. This configuration supports asdf 0.16 and later; the old
`asdf.sh` shell initializer is no longer used.

All six repo selections are concrete versions. Node is pinned to `24.14.0`, the
version used on the existing Mac when introducing presets, instead of the moving
`lts` selector. This is a reproducibility baseline, not a claim that it is the
latest release. Future upgrades are deliberate edits to `dot_tool-versions`.
An existing `lts` installation may need the exact-version install on next apply;
old installs are not automatically removed.

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

This skips the installation hook, managed shell shim setup, and asdf health
checks. It does not uninstall tools or remove inherited PATH entries. `mac-minimal`
sets it to false automatically. Linux continues to skip this macOS setup hook.

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
When enabled, it also appends existing install `bin` and Go `packages/bin`
directories for versions in the home `.tool-versions`. This exposes locally
installed commands before their shims are refreshed. Shims and existing PATH
entries retain priority; disabling asdf skips these additions too. Run
`asdf reshim` after installing commands to preserve project-specific selection.

`dots-health` verifies all six shim paths and checks that each repo-declared
version is installed when asdf is enabled. Project-specific `.tool-versions` files still control the
selected versions within those projects.
