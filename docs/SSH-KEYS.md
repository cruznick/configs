# 1Password SSH Keys

SSH private keys remain in 1Password. Public keys exported to `~/.ssh/signing-pubs/`
are selector files used by:

- SSH host aliases to tell OpenSSH which 1Password-backed key to ask for
- Git SSH signing to tell `op-ssh-sign` which 1Password-backed key to use

The `.pub` files are not private keys and do not contain private material.

Current behavior:
- 1Password integration is optional
- missing `op`, locked 1Password, or missing items no longer block bootstrap
- export is best-effort and warning-only
- if selector files are missing, SSH auth falls back to the 1Password agent defaults
- if a signing selector file is missing, Git signing is disabled instead of being left broken

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

## Vault configuration

`identity.op_vault` is optional for the common case where your SSH keys live in a
built-in Personal, Private, or Employee vault and item titles are unique.

Set `[identity].op_vault` in `~/.config/dotfiles/overrides.toml` when:

- your SSH keys live in a shared or custom vault
- item titles are ambiguous across multiple vaults
- you want the repo-managed export and agent config to target one specific vault

## Manual export example

```bash
op item get "ssh-sign-personal-gh" --fields "public key" \
  > ~/.ssh/signing-pubs/personal-gh.pub
```

If the item lives in a shared/custom vault, add `--vault "<vault>"`.

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
- `user.signingkey` and host `IdentityFile` may legitimately point at exported `.pub` selector files when using the 1Password SSH agent
