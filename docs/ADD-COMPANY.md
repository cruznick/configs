# Adding a New Work Company

## Quick way (recommended)

```bash
work-config add --slug=acme --platform=gh --email=you@acme.com
```

This automatically:
- Adds `[companies.acme]` to your local `companies.toml`
- Creates `~/repos/work/gh/acme/`
- Copies `.envrc.example` to `~/repos/work/gh/acme/`
- Runs `chezmoi apply` (writes gitconfig, SSH config, 1Password agent config)
- Prints next steps

---

## Manual way (power users)

### Step 1: Update your local company registry

Edit `.chezmoidata/companies.toml` (gitignored, lives on your machine only):

```toml
[companies.acme]
  slug           = "acme"
  email          = "you@acme.com"
  platforms      = ["gh"]   # "gl", "gh", or both
  ssh_key_prefix = "acme"   # matches 1Password item: ssh-sign-acme-gh
```

### Step 2: Create SSH keys in 1Password

In your SSH vault, create SSH key items named:
- `ssh-sign-acme-gh` (if using GitHub)
- `ssh-sign-acme-gl` (if using GitLab)

See [SSH-KEYS.md](SSH-KEYS.md) for how to create them.

### Step 3: Create repo directories

```bash
mkdir -p ~/repos/work/gh/acme   # or gl/acme
```

### Step 4: Apply chezmoi

```bash
chezmoi apply
```

This automatically:
- Regenerates `~/.gitconfig` with a new `includeIf` for `~/repos/work/gh/acme/`
- Regenerates `~/.ssh/config` with a new `Host github.com-acme` alias
- Writes `~/.gitconfig-work-acme-gh` (with `you@acme.com`)
- Writes `~/.zshrc.d/work-acme.zsh` stub
- Updates `~/.config/1Password/ssh/agent.toml` with the new key entry

### Step 5: Add SSH keys to the platform

Add `~/.ssh/signing-pubs/work-gh.pub` to your acme GitHub account.

### Step 6: Set up company secrets (direnv)

```bash
cd ~/repos/work/gh/acme
cp .envrc.example .envrc
# Edit .envrc — fill in your 1Password op:// item paths
direnv allow
```

When you `cd` into `~/repos/work/gh/acme/`, direnv fetches your secrets from 1Password automatically.
When you `cd` out, they're unloaded.

### Step 7: Authenticate glab (GitLab only)

```bash
GLAB_CONFIG_DIR=~/.config/glab-acme glab auth login --hostname gitlab.com
```

### Step 8: Verify identity

```bash
cd ~/repos/work/gh/acme
git-check
# Should show: email = you@acme.com, signingkey = ~/.ssh/signing-pubs/work-gh.pub
```
