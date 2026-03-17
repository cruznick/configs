# New Machine Setup Guide

## Prerequisites (do these before running install.sh)

### 1. Install 1Password
Download from [1password.com](https://1password.com) or:
```bash
brew install --cask 1password 1password-cli
```

### 2. Enable 1Password SSH Agent
1. Open 1Password → Settings → Developer
2. Enable **SSH Agent**
3. Quit and reopen 1Password
4. Verify: `ssh-add -L` should list your keys

### 3. Verify your SSH keys exist in 1Password
The bootstrap expects these items in the `GitKeys` vault:
- `ssh-sign-personal-gl`
- `ssh-sign-personal-gh`
- `ssh-sign-kavak-gl` (or your work company slug)
- `ssh-sign-kavak-gh`

See [SSH-KEYS.md](SSH-KEYS.md) if you need to create them.

---

## Bootstrap

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cruznick/configs/main/install.sh)"
```

You will be prompted for:
| Prompt | Example |
|---|---|
| Full name | `Benjamin J. Martinez` |
| Work email | `you@company.com` |
| Personal email | `you@gmail.com` |
| Work company slug | `kavak` |
| Personal GitHub username | `cruznick` |
| Artifactory username | `your.name` (or blank if not applicable) |

These values are stored in `~/.config/chezmoi/chezmoi.toml` — never committed.

---

## Post-install (one-time manual steps)

### 1. Reload shell
```bash
source ~/.zshrc
```

### 2. Add SSH keys to GitHub/GitLab
Export your public keys:
```bash
ls ~/.ssh/signing-pubs/
```

For each identity, add the `.pub` file to the corresponding account:
- `personal-gh.pub` → github.com (Settings → SSH and GPG keys → **Authentication** + **Signing**)
- `personal-gl.pub` → gitlab.com (Preferences → SSH Keys → **Authentication** + **Signing**)
- `work-gh.pub` → your work GitHub org
- `work-gl.pub` → your work GitLab

### 3. Authenticate glab
```bash
# Work (Kavak)
GLAB_CONFIG_DIR=~/.config/glab-work glab auth login --hostname gitlab.com

# Personal
GLAB_CONFIG_DIR=~/.config/glab-personal glab auth login --hostname gitlab.com
```

### 4. AWS SSO login
```bash
aws sso login --profile development
aws sso login --profile production
```

### 5. Update kubeconfig
```bash
install-eks-kubeconfig both
```

### 6. Load Kavak secrets
```bash
secrets-load
```

### 7. Verify git identity
```bash
cd ~/repos/work/gl/kavak/any-repo
git-check
# Should show kavak email + work-gl signing key

cd ~/repos/personal/gh/configs
git-check
# Should show personal email + personal-gh signing key
```

---

## Updating dotfiles

```bash
chezmoi update        # pull latest + apply
chezmoi diff          # preview what would change
chezmoi apply         # apply without pulling
```
