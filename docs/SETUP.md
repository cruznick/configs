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
The bootstrap expects these items in your SSH vault (e.g. `MyVault`):
- `ssh-sign-personal-gl`
- `ssh-sign-personal-gh`
- Work keys added later via `work-config add`

See [SSH-KEYS.md](SSH-KEYS.md) if you need to create them.

### 4. Prepare your company data file
```bash
cp ~/.local/share/chezmoi/docs/companies.toml.example \
   ~/.local/share/chezmoi/.chezmoidata/companies.toml
# Edit companies.toml and fill in your company slug, email, and platforms
```

---

## Bootstrap

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cruznick/configs/master/install.sh)"
```

You will be prompted for:
| Prompt | Example |
|---|---|
| Full name | `Your Name` |
| Personal email | `you@gmail.com` |
| Personal GitHub username | `your-gh-username` |
| Work registry username | `your.name` (or blank if not applicable) |
| 1Password vault name for SSH keys | `MyVault` |

These values are stored in `~/.config/chezmoi/chezmoi.toml` — never committed.

Work company emails are configured per-company in `companies.toml` (see below).

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

### 3. Add work companies

```bash
work-config add --slug=acme --platform=gh --email=you@acme.com
```

Follow the printed next steps (SSH key creation, pubkey upload, direnv setup).

### 4. Set up global secrets
Fill in `~/.secrets.zsh` with your global tokens (e.g. `GITHUB_TOKEN`).

### 5. Set up per-company secrets (direnv)
For each company:
```bash
cd ~/repos/work/gh/<slug>
cp .envrc.example .envrc
# Edit .envrc — fill in op:// references to your 1Password items
direnv allow
```

### 6. Authenticate glab (if using GitLab)
```bash
# Work
GLAB_CONFIG_DIR=~/.config/glab-<slug> glab auth login --hostname gitlab.com

# Personal
GLAB_CONFIG_DIR=~/.config/glab-personal glab auth login --hostname gitlab.com
```

### 7. AWS SSO login (if applicable)
```bash
aws sso login --profile development
aws sso login --profile production
```

### 8. Update kubeconfig (if applicable)
```bash
install-eks-kubeconfig both
```

### 9. Verify git identity
```bash
cd ~/repos/work/gl/<company>/any-repo
git-check
# Should show work email + work-gl signing key

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

---

## Verification checklist

```bash
# No unrendered template vars deployed
grep -r '{{' ~/.gitconfig ~/.zshrc ~/.ssh/config && echo "FAIL" || echo "OK"

# Shell loads cleanly
source ~/.zshrc

# asdf versions (no brew conflicts for terraform/kubectl)
asdf current

# direnv works
cd ~/repos/work/gh/<slug>/
# → direnv should load secrets; cd ~ → vars gone

# work-config shows correct state
work-config list
work-config check
```
