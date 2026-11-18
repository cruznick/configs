# Apps Installed Outside Homebrew

Use this list for apps that should be available after a machine rebuild but are
installed outside Homebrew. The group records where the app belongs conceptually;
it does not enable an automatic installer.

| App | Group | Installation |
| --- | --- | --- |
| [ccdeck](https://ccdeck.dev/) | Shared apps (`apps`) | macOS app installer or npm runner |

## ccdeck

ccdeck provides a local dashboard for Claude Code and Codex CLI sessions.
Choose one of the following methods.

### macOS desktop app

Download the macOS installer from [ccdeck.dev](https://ccdeck.dev/), or use the
project's documented installer:

```sh
curl -fsSL https://ccdeck.dev/install.sh | sh
```

### Run with npm

With Node.js and npm available (managed by asdf in this repo):

```sh
npx ccdeck
```

`npx` downloads and runs the package as needed; it does not install a global
`ccdeck` command. Run the same command again to start it.

The project documents adding a hook to `~/.claude/settings.json` for Claude Code
events. Codex sessions are read from local rollout logs.

## Adding another app

Add a row with the official project URL, intended group, and installation method,
then document any prerequisites and configuration changes below it. Keep these
manual steps separate from the Brewfiles and automatic bootstrap hooks.
