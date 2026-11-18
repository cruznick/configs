# Monthly settings snapshots

Capture durable settings, without session history or a full machine image:

```sh
python3 bin/executable_dots-snapshot create --monthly
```

After installing the helper through chezmoi, use `dots-snapshot create --monthly`.
It creates `~/Backups/current-state-YYYY-MM`. Repeated monthly runs verify the
existing snapshot instead of creating duplicates. A failed/incomplete snapshot
must be inspected and moved aside before retrying.

For another snapshot or an explicit repository backup:

```sh
dots-snapshot create
dots-snapshot create --repo ~/repos/personal/gh/configs
dots-snapshot verify ~/Backups/current-state-2026-11
```

## Coverage and storage

Includes shell/Git/SSH settings, work-context configuration, cloud configuration,
Claude/Codex settings and skills, editor settings, selected app settings and an
installed-software inventory. Current Bartender, iStat Menus, Rectangle Pro, eqMac
and Stream Deck preferences are exported, with installed app versions recorded.

Excludes repositories by default, agent session history, caches, dependencies,
browser profiles, Keychain, app binaries, iStat history and Raycast clipboard/AI
history. A requested repository includes Git metadata and uncommitted files,
excluding dependency directories. Read each snapshot's `coverage.json`.

Each snapshot has a complete file view. Unchanged files are hard-linked to the
previous snapshot, so they consume no additional file-data storage. Changed files
are stored again. Deleting an older snapshot leaves later snapshots intact.
Never edit files in a snapshot; copy them out before modifying or restoring them.
Source files are never hard-linked to a snapshot.

SQLite settings databases use online backups and integrity checks. File hashes
are verified. This is not an atomic capture of all running applications.

Snapshots contain credentials and private settings. They are plaintext, stored
with owner-only access. Keep them local; encrypt them before sharing or moving
them to shared storage. Do not commit snapshot data to Git.

## Schedule

The local LaunchAgent `io.dotfiles.settings-snapshot` runs on the first of each
month at 10:00. It also checks at login so a missed month is captured. It calls
`dots-snapshot create --monthly` without repository options.
Logs are in `~/Library/Logs/dots-snapshot.log` and `.error.log`.
The schedule is local, not automatically enabled on every machine by bootstrap.

## Restoring and retiring old backups

Read the snapshot's `RESTORE.md`; restore selectively with affected apps closed.
Bartender 7 provides an **Import from Bartender 6…** migration option. Do not assume
raw preferences work across major app versions.

Only retire old backups after the replacement verifies and its coverage matches
what you intend to retain. Current settings do not retain history that exists only
in old backups. Move known obsolete backups to Trash first. The snapshot command
does not automatically delete earlier snapshots.
