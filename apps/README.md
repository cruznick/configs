# Manual Apps and Exports

Apps installed outside Homebrew are listed in [MANUAL-INSTALLS.md](MANUAL-INSTALLS.md),
with their intended group and setup instructions. These are manual setup steps;
bootstrap and `chezmoi apply` do not run them.

## App Exports

For fresh private exports of the current working apps, including
[Bartender](bartender/README.md), use [dots-snapshot](../docs/SNAPSHOTS.md).
The existing repo exports below are historical reference artifacts.

This directory holds manual app-export artifacts that are kept in the repo for
reference and optional hand-import on another machine.

Important rules:

- These files are not part of `chezmoi apply`
- These files are not part of bootstrap
- No automatic import or sync is performed
- Update them only by exporting from the app on the current machine and then
  replacing the files in `apps/*/exports/`

This is intentionally separate from:

- declarative dotfiles and shell config managed by chezmoi
- declarative Homebrew package state under `homebrew/`
- local private work-context files under `~/.config/dotfiles/work-contexts/`
