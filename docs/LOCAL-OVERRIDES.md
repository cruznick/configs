# Local Override Examples

These files are intentionally local-only. They are not tracked by this repo.
Use them to keep machine-specific state out of managed dotfiles.

## Git

Path:

```text
~/.config/git/local.gitconfig
```

Example:

```gitconfig
[core]
  excludesfile = /Users/example/.gitignore_global

[gpg "ssh"]
  allowedSignersFile = /Users/example/.ssh/allowed_signers

[tool]
  machineId = local-only-value
```

The managed `~/.gitconfig` includes this file at the end. Values here can
override repo defaults without making the managed target dirty.

## Zsh Startup

Path:

```text
~/.zshenv
```

Example:

```zsh
# Machine-local CLI bootstrap.
if [[ -f "$HOME/.company-cli.sh" ]]; then
  source "$HOME/.company-cli.sh"
fi

# Tool-managed PATH block.
# >>> local-tool >>>
export LOCAL_TOOL_HOME="$HOME/.local/tool"
case ":$PATH:" in
  *":$LOCAL_TOOL_HOME/bin:"*) ;;
  *) export PATH="$LOCAL_TOOL_HOME/bin:$PATH" ;;
esac
# <<< local-tool <<<
```

Use `~/.zshenv` for bootstraps that must be available in every zsh process.
Keep generated blocks clearly marked so their owning installer can replace
them idempotently.

## Work Directory Environment

Path:

```text
/path/to/workspace/.envrc
```

Example:

```sh
export AWS_PROFILE=example
export SOME_SERVICE_URL=https://example.invalid

# Prefer fetching secrets from a local secret manager here instead of storing
# literal tokens in the repo.
```

Secrets, temporary credentials, cloud profiles, and per-project registries
belong in `.envrc`, not in managed dotfiles.

## Local Work Contexts

Path:

```text
~/.config/dotfiles/work-contexts/<slug>.toml
```

Example:

```toml
[context]
slug = "example"
enabled = true
name = "Example"

[providers]
enabled = ["gh"]
default = "gh"

[git]
name = "Example User"
email = "user@example.invalid"
signing_key = "~/.ssh/signing-pubs/example-gh.pub"
signing_item = "ssh-sign-example-gh"
commit_gpgsign = true

[match]
directories = ["/Users/example/repos/work/gh/example"]

[ssh]
github_alias = "github.com-example"
gitlab_alias = ""
github_identity_file = "~/.ssh/signing-pubs/example-gh.pub"
gitlab_identity_file = ""
github_agent_item = ""
gitlab_agent_item = ""

[direnv]
root_directories = ["/Users/example/repos/work/gh/example"]
envrc_example_target = "/Users/example/repos/work/gh/example/.envrc.example"
```

Work contexts are metadata only. They should not contain secrets.
