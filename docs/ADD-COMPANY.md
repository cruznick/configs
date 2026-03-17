# Adding a New Work Company

This guide adds a second company (e.g. `birdie`) alongside Kavak.

## Step 1: Update company registry

Edit `.chezmoidata/companies.toml`:

```toml
[companies.birdie]
  slug      = "birdie"
  platforms = ["gh"]   # "gl", "gh", or both
```

## Step 2: Create SSH keys in 1Password

In the `GitKeys` vault, create SSH key items named:
- `ssh-sign-birdie-gh` (if using GitHub)
- `ssh-sign-birdie-gl` (if using GitLab)

See [SSH-KEYS.md](SSH-KEYS.md) for how to create them.

## Step 3: Create git identity files

Create `dot_gitconfig-work-birdie-gh.tmpl`:

```toml
[user]
  name       = {{ .name | quote }}
  email      = "you@birdie.co"
  signingkey = ~/.ssh/signing-pubs/work-birdie-gh.pub

[url "git@github.com-birdie:"]
  insteadOf = git@github.com:
```

> Note: The signing key filename is `work-birdie-gh.pub` — the export script
> in `run_once_30` auto-generates this from the 1Password item name.

## Step 4: Create company shell config (optional)

Create `companies/birdie/env.zsh`:

```zsh
# Birdie-specific env vars
export BIRDIE_ENV=production
```

And source it from `dot_zshrc.tmpl` — the `COMPANY_RC` section already handles
this automatically when `workCompany = "birdie"` is set.

## Step 5: Create repo directories

```bash
mkdir -p ~/repos/work/gh/birdie
```

## Step 6: Commit and push

```bash
cd ~/repos/personal/gh/configs
git add .
git commit -m "Add birdie company config"
git push
```

## Step 7: Apply on all machines

```bash
chezmoi update
```

chezmoi re-runs `run_once_30-export-ssh-keys` (because the script contents
changed) and exports the new `birdie` keys automatically.
