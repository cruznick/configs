# AI CLI Modes

`ai-mode` is a zsh function loaded from `~/bin/ai-mode`. It switches Claude
and/or Codex between normal account login and AWS Bedrock for the current
terminal only. It does not rewrite `~/.claude/settings.json` or
`~/.codex/config.toml`.

```zsh
ai-mode bedrock          # switch both in this terminal
ai-mode login            # return both to normal account login
ai-mode status           # show both modes
ai-mode bedrock claude   # switch only Claude
ai-mode login codex      # switch only Codex
```

Each new terminal starts in login mode. In Bedrock mode, Claude receives its
AWS and model environment only when launched; Codex receives config overrides
only on its command line. Existing global tool settings remain untouched. Run
AWS SSO login when prompted:

```zsh
aws sso login --profile platform
```

## Updating installed packages

Update packages declared in the active Homebrew groups:

```zsh
dots-brew update
```

To upgrade every Homebrew formula and cask installed on the machine, including
packages outside this repo's active Brewfiles (including auto-updating casks):

```zsh
brew upgrade --greedy
```

Other managed tool updates:

```zsh
asdf install                 # install versions pinned in ~/.tool-versions
uv tool upgrade --all        # upgrade all uv-installed CLI tools
```

To change asdf runtime versions, edit the pinned values in `dot_tool-versions`
first, then run `asdf install`.
