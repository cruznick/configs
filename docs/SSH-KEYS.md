# 1Password SSH Key Setup

## Overview

SSH keys live in 1Password and are never written to disk as private keys.
The 1Password agent handles all signing and authentication.

The vault name is set during `chezmoi init` (prompt: `1Password vault name for SSH keys`).

| 1Password item | Identity | Purpose |
|---|---|---|
| `ssh-sign-personal-gl` | personal GitLab | auth + commit signing |
| `ssh-sign-personal-gh` | personal GitHub | auth + commit signing |
| `ssh-sign-work-gl` | work GitLab | auth + commit signing |
| `ssh-sign-work-gh` | work GitHub | auth + commit signing |

The `work` prefix matches the default `ssh_key_prefix = "work"` in `companies.toml`.
For additional companies, the prefix is the company slug (e.g. `ssh-sign-company2-gh`).

Only the **public keys** are exported to `~/.ssh/signing-pubs/`.

---

## Create keys (first time)

If the keys don't exist yet in 1Password:

```bash
# Sign in
op signin

# Create each key (category: SSH Key) — replace <vault> with your vault name
op item create --category ssh --title "ssh-sign-personal-gl" --vault "<vault>"
op item create --category ssh --title "ssh-sign-personal-gh" --vault "<vault>"
op item create --category ssh --title "ssh-sign-work-gl"     --vault "<vault>"
op item create --category ssh --title "ssh-sign-work-gh"     --vault "<vault>"
```

Or use `~/bin/git-setup` which does this interactively.

---

## Export public keys

```bash
# Runs automatically during chezmoi bootstrap (run_once_30)
# Or manually:
op item get "ssh-sign-personal-gh" --vault "<vault>" --fields "public key" \
  > ~/.ssh/signing-pubs/personal-gh.pub
```

---

## Verify agent is running

```bash
ssh-add -L
# Should list all public keys loaded by 1Password
```

---

## Add keys to GitHub / GitLab

Each public key must be added to the corresponding platform under:
- **Authentication key** — for git push/pull
- **Signing key** — for commit/tag GPG signatures

### GitHub
Settings → SSH and GPG keys → New SSH key → paste `.pub` content

### GitLab
Preferences → SSH Keys → Add new key → paste `.pub` content

---

## Troubleshooting

**`ssh-add -L` shows nothing**
→ 1Password SSH agent is not running. Open 1Password → Settings → Developer → enable SSH agent.

**`git commit` fails with signing error**
→ Run `ssh-add -L` and verify the signing key is listed.
→ Check `git config user.signingkey` matches a listed key.

**Permission denied (publickey)**
→ Verify the key is added to the platform (GitHub/GitLab).
→ Test with: `ssh -T git@github.com-personal`
