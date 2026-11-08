# Prompt for restoring a work Mac

Paste this into a new agent session after decrypting the backup. Replace the
bracketed fields. Do not paste credentials or session transcripts into the prompt.

> Restore this work Mac from [ABSOLUTE PATH TO DECRYPTED KIT].
> New home directory: [NEW HOME]. Preferred repository root: [NEW REPO ROOT].
> The old home and source root are in the kit's machine-paths.json.
>
> Read RESTORE.md, coverage.json and SHA256SUMS first. Verify checksums before
> restoring. Show missing data and excluded sessions explicitly. This is not a
> full-disk backup. Do not erase, clean up, uninstall or overwrite newer files.
>
> Use profile work, preset mac-dev, homebrew_work=true,
> homebrew_personal=false and homebrew_extras=false. Restore these overrides
> before bootstrap: the default bootstrap selects personal.
>
> Ask for any missing path mappings once. Build an explicit old-prefix →
> new-prefix map for home, repositories, worktrees and tool directories. Inventory
> absolute paths in shell startup, Git includes, SSH config, work-context TOML,
> chezmoi source settings, symlinks, editor settings and agent configuration.
> Produce a private diff for text configuration and review it before applying.
> Rewrite path prefixes only; do not globally replace usernames or strings.
> Never modify credentials, signatures, Git objects, encrypted material, session
> JSONL, or SQLite databases with search-and-replace.
>
> Recover the configs Git bundle at its recorded revision and apply the saved
> tracked working-tree patch if nonempty. Restore local config selectively.
> Resolve symlinks explicitly; never follow them into unrelated/private folders.
> Download Homebrew and asdf tools again. homebrew/Brewfile.recovery is the
> explicit snapshot of every Homebrew formula and cask installed at backup time;
> normal profile groups remain the default. If I want the exact old installed
> set including personal and dependency packages, run that snapshot separately.
> This snapshot records package names, not immutable downloadable versions.
>
> Keep copied session JSONL as recoverable evidence. Use supported application
> resume/import behavior where available; do not promise it will reconstruct
> indexes or worktrees. Do not overwrite new sessions. Mixed global databases,
> confidential work sessions, browser cookies, Keychain and macOS permissions
> may be excluded or require separate recovery. Reauthenticate clients.
>
> Company enrollment, administrator prompts, VPN/MFA and GUI app imports are
> human steps. Preserve company-managed security software. Never perform
> production infrastructure or identity-provider writes.
>
> Verify shell startup, Git identities/signing, work routing, all pinned runtimes,
> active Brewfile dependencies and chosen app settings. Check recoverable
> sessions in the application. Report failures and remaining manual steps.
> Only propose cleanup after I confirm the restored machine works.

## Package snapshot

`homebrew/Brewfile.recovery` is deliberately outside the automatic profile groups.
It includes dependency packages and duplicate runtime managers because its purpose
is recovery of the installed set, not defining the recommended baseline.
`homebrew/installed-versions.tsv` records observed versions; Homebrew normally
downloads the versions currently available upstream, which may differ.

Use the snapshot only after reviewing it:

```bash
brew bundle install --no-upgrade --file homebrew/Brewfile.recovery
```

Do not run package cleanup during recovery. Some installed packages will be outside
the selected work profile even though they are recorded in the recovery snapshot.
