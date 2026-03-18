#!/usr/bin/env bash
# install.sh — Bootstrap a new Mac with Benjamin's dotfiles
#
# Usage (curl-installable):
#   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/cruznick/configs/main/install.sh)"
#
# Or clone-and-run:
#   bash ~/repos/personal/gh/configs/install.sh
#
set -euo pipefail

REPO="cruznick/configs"
CHEZMOI_BIN_DIR="$HOME/.local/bin"

log()  { printf "\n\033[1;34m==> %s\033[0m\n" "$*"; }
ok()   { printf "\033[1;32m✓ %s\033[0m\n" "$*"; }
warn() { printf "\033[1;33m[WARN] %s\033[0m\n" "$*" >&2; }
die()  { printf "\033[1;31m[ERROR] %s\033[0m\n" "$*" >&2; exit 1; }

# ── Homebrew ──────────────────────────────────────────────────────────────────
install_homebrew() {
  if command -v brew >/dev/null 2>&1; then
    ok "Homebrew already installed"
    return 0
  fi
  log "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Add brew to PATH for this session (Apple Silicon)
  if [[ -f /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
  ok "Homebrew installed"
}

# ── chezmoi ───────────────────────────────────────────────────────────────────
install_chezmoi() {
  if command -v chezmoi >/dev/null 2>&1; then
    ok "chezmoi already installed ($(chezmoi --version 2>&1 | head -1))"
    return 0
  fi
  # Try brew first (preferred on macOS)
  if command -v brew >/dev/null 2>&1; then
    log "Installing chezmoi via brew..."
    brew install chezmoi
  else
    log "Installing chezmoi via official script..."
    mkdir -p "$CHEZMOI_BIN_DIR"
    sh -c "$(curl -fsLS get.chezmoi.io)" -- -b "$CHEZMOI_BIN_DIR"
    export PATH="$CHEZMOI_BIN_DIR:$PATH"
  fi
  ok "chezmoi installed"
}

# ── dotfiles ──────────────────────────────────────────────────────────────────
apply_dotfiles() {
  local local_repo="$HOME/repos/personal/gh/configs"
  local toml_path

  if [[ -d "$local_repo/.git" ]]; then
    # Repo already cloned locally — register it as the chezmoi source
    log "Using existing local repo at $local_repo..."
    chezmoi init --source "$local_repo"
    toml_path="$local_repo/.chezmoidata/companies.toml"
  elif chezmoi source-path >/dev/null 2>&1; then
    # Already initialised at default location — update
    log "Updating existing chezmoi dotfiles..."
    chezmoi update
    toml_path="$(chezmoi source-path)/.chezmoidata/companies.toml"
  else
    # Fresh machine — clone from GitHub
    log "Initializing chezmoi with $REPO..."
    chezmoi init "$REPO"
    toml_path="$(chezmoi source-path)/.chezmoidata/companies.toml"
  fi

  # Seed companies.toml if missing (gitignored — must exist for templates)
  if [[ -n "$toml_path" && ! -f "$toml_path" ]]; then
    mkdir -p "$(dirname "$toml_path")"
    printf '[companies]\n' > "$toml_path"
    ok "Created empty $toml_path"
  fi

  chezmoi apply
  ok "Dotfiles applied"
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
  log "Benjamin's dotfiles bootstrap"
  echo "Repo: https://github.com/$REPO"
  echo ""

  [[ "$(uname)" == "Darwin" ]] || die "This script is macOS-only. Adapt for Linux manually."

  install_homebrew
  install_chezmoi
  apply_dotfiles

  log "Done ✅"
  cat <<'EOF'

Next steps (one-time manual actions):
  1. Reload shell:          source ~/.zshrc
  2. Verify SSH agent:      ssh-add -L
  3. glab personal auth:    GLAB_CONFIG_DIR=~/.config/glab-personal glab auth login --hostname gitlab.com
  4. AWS SSO login:         aws sso login --profile development
  5. EKS kubeconfig:        install-eks-kubeconfig (run the script in ~/bin/)
  6. Switch npm registry:   ln -sf ~/.npmrcs/default ~/.npmrc  (for personal projects)

EOF
}

main "$@"
