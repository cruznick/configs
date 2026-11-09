# Local Override Examples

These files are intentionally local-only. They are not tracked by this repo.
Use them to keep machine-specific state out of managed dotfiles.

## Machine Preset

```toml
# ~/.config/dotfiles/overrides.toml
machine_preset = "mac-dev" # or mac-minimal
profile = "personal"
provider = "gh"
work_contexts = []

[optional_integrations]
homebrew_work = true # independent of profile and private work identity
```

Keep only exceptions to the preset in `[optional_integrations]`; copying every
flag freezes those choices even when the preset changes. Existing overrides are
never rewritten by bootstrap. See [MULTI-MACHINE.md](MULTI-MACHINE.md).

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
Machine profiles control package defaults, not account restrictions. Work contexts
may enable GitHub, GitLab, or both. The `kavak` context specifically requires
GitLab only and dedicated credentials.

For three simultaneous contexts:

| Directory | Providers | Credentials |
| --- | --- | --- |
| `~/repos/personal/{gh,gl}/` | GitHub + GitLab | Personal |
| `~/repos/work/{gh,gl}/freelance/` | GitHub + GitLab | Personal |
| `~/repos/work/gl/kavak/` | GitLab | Dedicated Kavak |

Copy `profiles/freelance-context.example.toml` to
`~/.config/dotfiles/work-contexts/freelance.toml`. Set Kavak's providers to
`enabled = ["gl"]`, `default = "gl"`, and its context credentials to
`"dedicated"`. If `work_contexts` in overrides lists selected contexts explicitly,
include both `"freelance"` and `"kavak"`.

`context.credentials = "personal"` reuses the personal SSH aliases, signing key
(for the context's default provider), and CLI config directories. Git name/email
inherit the personal identity unless overridden. Dedicated contexts use their
own selectors and CLI directories (`gh-<slug>`, `glab-<slug>`), optionally
customized through `[cli].gh_config_dir` and `glab_config_dir`.
The global personal signing key defaults to `personal-gh.pub`, independently
of the machine profile. Override `[git].personal_signing_provider = "gl"` if
desired; register the signing public key with every host where you need
verified signatures.

Git URL rewrites are directory-scoped and support SCP-style SSH, `ssh://`, and
HTTPS URLs (rewritten to SSH). Disabled providers route to an SSH alias that
fails locally. Clone into the appropriate directory; ordinary clone uses the
destination's Git config. Keep match directories disjoint to avoid conflicting
Git includes. Linked worktrees retain their repository context.

The shell routes `gh` and `glab` through `gh-auto` and `glab-auto`; wrappers use
the most specific context and reject disabled providers. Existing API token
environment variables still override CLI credential stores: keep them in the
appropriate direnv scope, not global shell startup. `command gh`/`command glab`
and explicit SSH aliases bypass these convenience routes; this is not an
organization security boundary. No management controls are modified.

Apply the generated Git/SSH config and wrappers, then start a new shell. No
GitHub mirror is required for this separation.
