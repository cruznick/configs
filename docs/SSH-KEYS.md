# 1Password SSH Keys

SSH private keys remain in 1Password. Only public keys may be exported to `~/.ssh/signing-pubs/`.

Current behavior:
- 1Password integration is optional
- missing `op`, locked 1Password, or missing items no longer block bootstrap
- export is best-effort and warning-only

Personal items:
- `ssh-sign-personal-gh`
- `ssh-sign-personal-gl`

Work items:
- `ssh-sign-<key_prefix>-gh`
- `ssh-sign-<key_prefix>-gl`

`key_prefix` is now represented by the local work-context naming you choose in:
- `~/.config/dotfiles/work-contexts/<slug>.toml`

For local work contexts, keep Git signing items and SSH auth items distinct when needed:
- `git.signing_item`
- `ssh.github_agent_item`
- `ssh.gitlab_agent_item`

## Manual export example

```bash
op item get "ssh-sign-personal-gh" --vault "<vault>" --fields "public key" \
  > ~/.ssh/signing-pubs/personal-gh.pub
```

## Verify agent

```bash
ssh-add -L
```

## Add keys to GitHub / GitLab

Add each public key as both:
- authentication key
- signing key

## Notes

- `~/.config/1Password/ssh/agent.toml` is rendered from repo-tracked config
- local work-context additions come from `~/.config/dotfiles/work-contexts/*.toml`
- missing keys are skipped with warnings
- local vault/account setup is still local-only
