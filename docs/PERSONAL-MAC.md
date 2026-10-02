# Personal Mac setup and update

macOS is the supported platform. Use `mac-dev` for a development machine or
`mac-minimal` for core command-line tools. Both support personal identity.

## Afternoon trial

Start on the personal Mac with the existing-machine steps below. Stop before
apply if the diff would remove local settings you still need. Keep a local
backup of existing `~/.zshrc`, `~/.gitconfig`, `~/.ssh/config`,
`~/.config/dotfiles/`, and `~/.config/git/local.gitconfig` before applying.
Keep that backup private: these files can contain machine-specific credentials.

Run this in the personal Mac's terminal before editing or applying:

```bash
(
  set -eu
  umask 077
  trial_backup="$(mktemp -d "$HOME/dotfiles-backup.XXXXXX")"
  for relative in .zshrc .zshenv .gitconfig .ssh/config .tool-versions \
    .config/dotfiles .config/git/local.gitconfig .config/1Password/ssh/agent.toml; do
    if [ -e "$HOME/$relative" ]; then
      mkdir -p "$trial_backup/$(dirname "$relative")"
      cp -pR "$HOME/$relative" "$trial_backup/$relative"
    fi
  done
  git -C "$(chezmoi source-path)" rev-parse HEAD > "$trial_backup/source-revision.txt"
  printf 'Backup: %s\n' "$trial_backup"
)
```

This requires an existing chezmoi setup. On a Mac with no chezmoi yet, back up
any existing shell/Git/SSH configuration manually before bootstrap.
To restore a file, copy that specific saved file back to its original path,
then review `chezmoi diff` before applying again. Keep the printed backup path.

For an assisted session, use this handoff:

> Update this personal Mac using docs/PERSONAL-MAC.md in cruznick/configs.
> Inspect the current chezmoi source, local edits, and overrides first.
> Use personal/GitHub identity and mac-dev unless this Mac already intentionally
> uses mac-minimal. Disable work apps and unwanted work contexts, preserve local
> settings, review the diff, then apply and verify. Remove MeetingBar if installed.
> Report the applied Git revision, health summary, and any remaining warnings.

Success means the verification commands below pass, personal identity is
correct, work contexts are absent, and MeetingBar is gone. If anything fails,
save the exact command and error locally before retrying. Restoring config
backups does not undo package installations or upgrades.

## Before moving to the other Mac

Commit and publish the reviewed source changes first: the other Mac pulls from
GitHub, not from this checkout. Check `git status -sb` and `git log origin/main..HEAD`.
Preserve any unfinished local changes before pulling on either machine.

Do not copy work-machine overrides, work contexts, legacy
`.chezmoidata/companies.toml`, shell startup files, or credentials onto the
personal Mac. App settings under [apps/](../apps/README.md) are manual imports.

## Existing personal Mac

Find the configured source and inspect its state:

```bash
chezmoi source-path
git -C "$(chezmoi source-path)" status -sb
# Once local changes are committed or stashed:
git -C "$(chezmoi source-path)" pull --ff-only
```

Edit `~/.config/dotfiles/overrides.toml`, preserving unrelated local settings.
Place the selectors before any TOML table headers:

```toml
machine_preset = "mac-dev"
profile = "personal"
provider = "gh"
work_contexts = []
primary_machine = false

[optional_integrations]
homebrew_work = false
homebrew_extras = false
```

`work_contexts = []` means automatic discovery, **not disable all**. If the Mac
already has files in `~/.config/dotfiles/work-contexts/`, set `enabled = false`
inside each unwanted file's `[context]` table. Check for legacy company data in
the source's `.chezmoidata/companies.toml` too: it is used as a fallback when no
local contexts exist. Back up and remove unwanted legacy entries locally.

Inherited `DOTFILES_PROFILE`, `DOTFILES_PROVIDER`, and `DOTFILES_MACHINE_PRESET`
override the file's selectors. Clear unwanted values and remove their exports
from local startup files before continuing:

```bash
unset DOTFILES_PROFILE DOTFILES_PROVIDER DOTFILES_MACHINE_PRESET
chezmoi execute-template '{{ includeTemplate ".chezmoitemplates/effective-config.json.tmpl" . }}' \
  | jq '{active_profile, active_provider, machine_preset, selected_work_contexts, optional_integrations}'
chezmoi diff
chezmoi status
```

Review shell, Git, SSH, package, and script changes. Preserve target-side edits
using [APPLY-SAFETY.md](APPLY-SAFETY.md). A full apply can install missing packages
and pinned asdf runtimes, so allow time for downloads.

```bash
chezmoi apply
exec zsh -l
```

## New personal Mac

After the reviewed changes are available on GitHub:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cruznick/configs/main/install.sh)" -- --preset mac-dev
```

Choose `mac-minimal` instead if desired. Bootstrap creates personal/GitHub
overrides with work apps disabled, then applies the configuration. Existing
overrides are preserved; use the existing-machine steps to correct them.

Configure 1Password and personal SSH/signing keys locally using
[SSH-KEYS.md](SSH-KEYS.md). Missing selectors leave Git signing disabled.

## Remove MeetingBar on each Mac

MeetingBar is no longer declared. Applying or syncing does not uninstall it.
Quit MeetingBar, then check and remove only that app if installed:

```bash
brew list --cask meetingbar
# If installed:
brew uninstall --cask meetingbar
```

Avoid broad package cleanup just to remove this app. Turning off the work group
can make other installed work packages appear as cleanup candidates.

## Verify

```bash
dots-profile
dots-debug --json
dots-brew plan
dots-brew status
dots-brew audit --missing
dots-health --fast
chezmoi status
git -C "$HOME" var GIT_AUTHOR_IDENT
```

Expect personal/GitHub identity, the chosen preset, no selected work contexts,
and `homebrew_work = false`. Confirm the Git identity is yours; local Git
overrides may supersede profile defaults. Resolve missing runtime/package
warnings and review remaining drift. Optional hooks warn without failing apply,
so a successful apply alone does not establish readiness.

For intentional upgrades of the active Homebrew groups, run `dots-brew update`.
Normal apply/sync uses `--no-upgrade`. See [ASDF.md](ASDF.md) for runtime retries.

## If verification finds gaps

| Finding | Action |
| --- | --- |
| Missing Homebrew packages | Run `dots-brew sync`, then `dots-brew audit --missing`. |
| Missing pinned Node or another runtime | After applying `.tool-versions`, run `(cd "$HOME" && asdf install && asdf reshim)`. |
| Missing asdf plugins | Use the complete hook retry below. |
| Incorrect Git identity | Inspect `git -C "$HOME" config --show-origin --get-regexp '^user[.]'`; correct local overrides before committing. |
| Missing SSH/signing selectors | Unlock/configure 1Password, follow [SSH-KEYS.md](SSH-KEYS.md), then apply again. |
| Untracked Homebrew packages | Review each item; personal apps can be intentionally retained. Do not run broad cleanup to make health green. |
| Pending target edits | Preserve or merge the edits using [APPLY-SAFETY.md](APPLY-SAFETY.md), then review the diff again. |

Retry the full asdf hook from any source location:

```bash
(
  set -o pipefail
  chezmoi execute-template \
    '{{ includeTemplate ".chezmoiscripts/run_onchange_after_20-setup-asdf.sh.tmpl" . }}' | bash
)
dots-health --fast
```

The hook reports failures as warnings, so verify the health result afterward.
Check GUI apps launch and grant requested macOS permissions locally. App
licenses, accessibility permissions, 1Password authentication, and manual app
imports cannot be established by repository tests.

Record `git -C "$(chezmoi source-path)" rev-parse HEAD`, the health summary,
and any accepted untracked packages for this trial. Keep private diffs and
credential-related output on the personal Mac.
