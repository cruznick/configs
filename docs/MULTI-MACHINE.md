# Multiple Macs

macOS is the supported platform. Git shares configuration and package intent;
each Mac keeps its own identity choices, credentials, paths, and enabled work contexts.

## Presets

| Setting | `mac-dev` (default) | `mac-minimal` |
| --- | --- | --- |
| Homebrew groups | core, dev, apps | core only |
| zinit shell plugins | enabled | enabled |
| asdf runtimes | enabled | disabled |
| 1Password SSH/signing and key export | enabled | disabled |
| Work apps and extras | opt-in locally | opt-in locally |

Both presets keep the shared shell configuration and font setup. Minimal means
core command-line tools without the development/app groups, not a bare OS.
Git's external `difft` helper is configured only when the dev group is enabled.
The default editor falls back from VS Code to Neovim, then vi.

Machine capability and identity are separate: either preset works with
`profile = "personal"` or `"work"`. A work profile does not enable work apps or
pick an employer; private contexts remain path-scoped and local-only.

## First Setup

From a clone:

```bash
bash install.sh --preset mac-dev
# For a smaller Mac, choose --preset mac-minimal instead.
```

Without cloning first:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cruznick/configs/main/install.sh)" -- --preset mac-minimal
```

With no option and no existing overrides, a terminal session prompts for a preset;
noninteractive runs default to `mac-dev`. `DOTFILES_MACHINE_PRESET` also supplies
a choice, with `--preset` taking priority during bootstrap.

Bootstrap creates `~/.config/dotfiles/overrides.toml` before source initialization
or apply. Existing overrides are preserved byte-for-byte. A conflicting explicit
preset stops bootstrap and asks you to edit the file first. Existing overrides
without `machine_preset` retain the previous full setup through `mac-dev`.
Existing source updates require a clean worktree and use `git pull --ff-only`;
the sole apply occurs afterward.

Set only this Mac's exceptions locally:

```toml
# ~/.config/dotfiles/overrides.toml
machine_preset = "mac-dev"
profile = "personal"
provider = "gh"
work_contexts = []
primary_machine = false

[optional_integrations]
homebrew_work = true

[identity]
op_vault = "Personal"
```

Omit integration flags you want the preset to control. Explicit local flags
always override the preset. Invalid profile/provider/preset values stop rendering.
`dots-profile` and `dots-debug --json` show the selected preset and effective flags.

## What Stays Local

Do not synchronize the whole home directory or copy authentication/session state
between Macs. Recreate or securely restore these per machine:

- `~/.config/dotfiles/overrides.toml`: preset and local exceptions.
- `~/.config/dotfiles/work-contexts/*.toml`: identity and directory mappings; adjust paths on the new Mac.
- `~/.config/git/local.gitconfig`, `~/.zshenv`, project `.envrc`: local settings and startup layers.
- 1Password login, SSH-agent integration, exported public-key selectors, and CLI authentication: set up locally; keep private keys/tokens out of Git.

See [LOCAL-OVERRIDES.md](LOCAL-OVERRIDES.md), [WORK-CONTEXTS.md](WORK-CONTEXTS.md),
and [SSH-KEYS.md](SSH-KEYS.md). App exports under `apps/` still require manual import.

## Routine Sync And Intentional Upgrades

On each Mac, review before applying:

```bash
git -C "$(chezmoi source-path)" pull --ff-only
chezmoi diff
chezmoi status
chezmoi apply
dots-brew plan
dots-brew status
dots-health --fast
```

Apply and `dots-brew sync` install missing active packages using `--no-upgrade`.
Use `dots-brew update` for explicit upgrades to the active Brewfile. New packages
can still update shared dependencies; Homebrew is not a version lockfile.
asdf uses concrete repo versions, currently including Node `24.14.0`.
Preview removal separately with `dots-brew cleanup --dry-run`; disabling a group
does not uninstall it. Review the preview carefully after changing presets.

For a preset change, edit `machine_preset` locally and review the diff/status
before applying. To preview temporarily without saving:

```bash
DOTFILES_MACHINE_PRESET=mac-minimal chezmoi diff
```

That environment selector applies only to the command. Existing local integration
overrides still win, so the preview may intentionally differ from a stock preset.

## Integration Switches

- `homebrew_*`: each package group is independent; the install hook and health checks skip Homebrew only if all groups are disabled. Bootstrap may still install Homebrew to obtain chezmoi.
- `zinit`: disables its install hook and shell initialization. Enabling it later reruns the onchange hook; a missing checkout does not cause shell startup errors.
- `asdf`: disables runtime installation, managed shim initialization, and runtime health checks. To avoid installing the asdf package too, disable the dev group.
- `onepassword`: disables managed SSH-agent selection, public-key selectors, Git signing integration, shell sign-in hooks, and management of its agent config file. Normal SSH key/agent defaults remain available; local Git overrides can define another signing setup.
- `ssh_key_export`: disables exporting public selectors only; export also requires `onepassword = true`.

These are activation switches, not uninstall commands. They do not delete packages,
keys, old runtime installs, existing agent config, or inherited environment entries.
Package groups and integration activation are separate: for example, disabling
1Password integration does not remove it from an enabled apps group. Restart the
shell after changing startup flags and review any machine-local startup overrides.

## Validation And Future Linux Option

GitHub Actions runs isolated regression checks on macOS for both presets and both
identity profiles, along with disabled-integrations, bootstrap, cleanup, runtime,
and shell-syntax checks. It does not run bootstrap against a real home directory,
install the declared app list, or exercise actual package removals.

```bash
python3 -m unittest discover -s tests -v
```

Prerequisites: Python 3.9+, chezmoi, Bash 4+, jq, and zsh. Core installs Bash and jq;
Python is needed only to run the regression suite, not normal dotfiles operation.

Linux is a possible future extension, not implemented support in this change.
Some existing shell branches recognize Linux and macOS hooks skip it, but that
does not make the setup complete there. If needed later, add a separate Linux
preset, split portable packages from macOS casks, resolve platform-specific
Homebrew/SSH-agent/font paths, provide a Linux runtime-install path, and add a
Linux CI job. Until there is a real Linux machine to validate, keep this repo Mac-first.
