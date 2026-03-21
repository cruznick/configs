# iStat Menus

This folder stores manual iStat Menus preference exports for reference and
optional hand-restore on another machine.

Contents:

- `exports/` contains repo-tracked plist exports captured from
  `~/Library/Preferences/`

Manual export workflow:

1. Quit iStat Menus or ensure settings are fully written to disk.
2. Copy these files from `~/Library/Preferences/` into `exports/`:
   - `com.bjango.istatmenus.plist`
   - `com.bjango.istatmenus.menubar.7.plist`
   - `com.bjango.istatmenus.agent.plist`
   - `com.bjango.istatmenus.status.plist`
3. Review the diff and commit the updated exports.

Manual import workflow:

1. Quit iStat Menus on the target machine.
2. Back up any existing files in `~/Library/Preferences/`.
3. Copy the plist files from `exports/` into `~/Library/Preferences/`.
4. Re-open iStat Menus and verify the settings loaded as expected.

This is intentionally manual:

- no chezmoi-managed target exists for these files
- no bootstrap hook imports them
- no `dots-*` command syncs or applies them
