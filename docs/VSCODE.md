# Visual Studio Code isolation and extension inventory

## Persona isolation

The managed `code` command reads the active dotfiles profile and launches VS
Code with separate data paths:

- personal: `~/Library/Application Support/Code-dotfiles/personal`
- work: `~/Library/Application Support/Code-dotfiles/work`

This separates user settings, native profiles, installed extensions, and sign-in
state. Keep Settings Sync signed into the matching personal or work Microsoft or
GitHub account in each data directory. With **Profiles** enabled, VS Code syncs
the profiles belonging to that account. Do not use one Sync account for both
personas.

The first launch in a new data directory is a fresh VS Code instance. Sign into
the correct Sync account and select the intended categories. Keep the existing
VS Code data directory until the new instance has synchronized and been reviewed.

## Launch aliases

The shell aliases select the profile automatically from the effective dotfiles
profile:

```sh
code                 # personal or work base profile
code-go              # personal-go or work-go profile
code-python          # personal-python or work-python profile
code-typescript      # personal-typescript or work-typescript profile
```

When the current directory matches an enabled work context, that context is
added to the native profile name. For example, inside a configured freelance
directory on a personal-profile Mac, `code` opens `personal-freelance` and
`code-go` opens `personal-freelance-go`. These remain under the personal data
directory and personal Sync account because the freelance context reuses
personal credentials. On a work-profile Mac, a matching context is scoped under
the work data directory and work Sync account.

The native language profiles are separate VS Code profiles. VS Code profiles
do not inherit another profile's settings, so customize and sync settings for
each language profile that needs them. The extension inventory combines the
persona's global file, any matching context's global file, the persona language
file, and the context language file. More specific files override the same
extension ID in less specific files.

## Versioned extension inventory

Lists contain only `publisher.extension@version` lines. No extension package
files or VS Code databases are stored in the repo. Install extensions manually
in the matching VS Code profile, using the listed version as the requirement.

```sh
dots-vscode extensions
dots-vscode extensions --language go
code-go --install-extension golang.go@0.56.1
dots-vscode capture --language go
```

`dots-vscode capture` records the installed extension IDs and versions for the
active persona/context profile. For a language profile it records only entries
that differ from the inherited persona and context inventories. Review the
resulting file before committing. The current personal inventory is a baseline
from this Mac's Stable VS Code installation; update it after confirming the
profiles you want to keep. Context-specific extension lists live under the
persona directory, such as `vscode/extensions/personal/freelance/`.
The initial work global and language lists are copied from this inventory as a
starting point; review them on the work Mac before installing or revising them.

## Backup

Use **Profiles: Export Profile…** and save `.code-profile` files locally for
profiles that need a portable backup. Review exports for sensitive values and
machine-specific paths before storing them. Keep exports outside this repo by
default; work profile exports belong only in storage approved for work data.
Settings Sync is the cross-machine transfer mechanism. The repo stores launcher
logic and extension version inventories, not VS Code user-data directories,
credentials, caches, or extension binaries.
