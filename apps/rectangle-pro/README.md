# Rectangle Pro

This folder stores manual Rectangle Pro preference exports for reference and
optional hand-restore on another machine.

Contents:

- `exports/` contains the repo-tracked plist export captured from
  `~/Library/Preferences/com.knollsoft.Hookshot.plist`

Manual export workflow:

1. Quit Rectangle Pro or ensure settings are fully written to disk.
2. Copy `~/Library/Preferences/com.knollsoft.Hookshot.plist` into `exports/`.
3. Review the diff and commit the updated export.

Manual import workflow:

1. Quit Rectangle Pro on the target machine.
2. Back up any existing `~/Library/Preferences/com.knollsoft.Hookshot.plist`.
3. Copy `exports/com.knollsoft.Hookshot.plist` into `~/Library/Preferences/`.
4. Re-open Rectangle Pro and verify the shortcuts/settings loaded correctly.

This is intentionally manual:

- no chezmoi-managed target exists for this file
- no bootstrap hook imports it
- no `dots-*` command syncs or applies it
