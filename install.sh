#!/usr/bin/env bash
# install.sh — chezmoi bootstrap for macOS (Linux is unvalidated).
set -euo pipefail

REPO="cruznick/configs"
REPO_URL="https://github.com/${REPO}.git"
CHEZMOI_BIN_DIR="$HOME/.local/bin"
OVERRIDES_DIR="$HOME/.config/dotfiles"
OVERRIDES_FILE="$OVERRIDES_DIR/overrides.toml"
MACHINE_PRESET="${DOTFILES_MACHINE_PRESET:-}"

log()  { printf "\n[INFO] %s\n" "$*"; }
ok()   { printf "[OK] %s\n" "$*"; }
warn() { printf "[WARN] %s\n" "$*" >&2; }
die()  { printf "[ERROR] %s\n" "$*" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage: bash install.sh [--preset mac-dev|mac-minimal]

mac-dev      Development tools, GUI apps, asdf, zinit, and 1Password (default).
mac-minimal  Core command-line tools and zinit, without runtimes or GUI apps.

Existing overrides.toml is preserved. To change an existing machine, edit its
machine_preset there, review chezmoi diff, then apply. Work apps are a local switch.
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --preset)
        [[ $# -ge 2 && -n "$2" ]] || die "--preset requires mac-dev or mac-minimal"
        MACHINE_PRESET="$2"
        shift 2
        ;;
      --preset=*)
        MACHINE_PRESET="${1#*=}"
        [[ -n "$MACHINE_PRESET" ]] || die "--preset requires mac-dev or mac-minimal"
        shift
        ;;
      -h|--help) usage; exit 0 ;;
      *) die "Unknown argument: $1 (use --help)" ;;
    esac
  done
  case "$MACHINE_PRESET" in
    ""|mac-dev|mac-minimal) ;;
    *) die "Unknown preset: $MACHINE_PRESET (choose mac-dev or mac-minimal)" ;;
  esac
  # An explicit CLI selection wins over an inherited environment selection.
  if [[ -n "$MACHINE_PRESET" ]]; then
    export DOTFILES_MACHINE_PRESET="$MACHINE_PRESET"
  fi
}

script_dir() {
  local source_file="${BASH_SOURCE[0]:-}"
  [[ -n "$source_file" ]] || return 1
  cd "$(dirname "$source_file")" && pwd
}

is_supported_os() {
  case "$(uname)" in
    Darwin|Linux) return 0 ;;
    *) return 1 ;;
  esac
}

is_valid_git_repo() {
  local path="$1"
  [[ -d "$path/.git" ]] || return 1
  git -C "$path" rev-parse --is-inside-work-tree >/dev/null 2>&1
}

repo_matches_expected() {
  local path="$1"
  local remote=""
  remote="$(git -C "$path" config --get remote.origin.url 2>/dev/null || true)"
  [[ "$remote" == *"$REPO"* ]]
}

ensure_curl() {
  command -v curl >/dev/null 2>&1 || die "curl is required for bootstrap"
}

install_homebrew_if_needed() {
  if [[ "$(uname)" != "Darwin" ]]; then
    return 0
  fi
  if command -v brew >/dev/null 2>&1; then
    ok "Homebrew already installed"
    return 0
  fi
  log "Installing Homebrew"
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || die "Homebrew installation failed"
  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
  ok "Homebrew installed"
}

install_chezmoi() {
  if command -v chezmoi >/dev/null 2>&1; then
    ok "chezmoi already installed"
    return 0
  fi
  if command -v brew >/dev/null 2>&1; then
    log "Installing chezmoi via brew"
    brew install chezmoi || die "Failed to install chezmoi via brew"
  else
    log "Installing chezmoi via official script"
    mkdir -p "$CHEZMOI_BIN_DIR"
    sh -c "$(curl -fsLS get.chezmoi.io)" -- -b "$CHEZMOI_BIN_DIR" || die "Failed to install chezmoi"
    export PATH="$CHEZMOI_BIN_DIR:$PATH"
  fi
  ok "chezmoi installed"
}

find_local_source_candidate() {
  local candidate
  candidate="$(script_dir || true)"
  if is_valid_git_repo "$candidate" && repo_matches_expected "$candidate"; then
    printf '%s\n' "$candidate"
    return 0
  fi
  candidate="$HOME/repos/personal/gh/configs"
  if is_valid_git_repo "$candidate" && repo_matches_expected "$candidate"; then
    printf '%s\n' "$candidate"
    return 0
  fi
  return 1
}

backup_broken_source() {
  local path="$1"
  local backup="${path}.broken.$(date +%Y%m%d%H%M%S)"
  if [[ -e "$path" ]]; then
    mv "$path" "$backup"
    warn "Backed up broken chezmoi source to $backup"
  fi
}

init_or_update_source() {
  local candidate="${1:-}"
  local current=""

  current="$(chezmoi source-path 2>/dev/null || true)"
  if [[ -n "$current" ]]; then
    log "Found existing chezmoi source: $current"
    if is_valid_git_repo "$current" && repo_matches_expected "$current"; then
      log "Updating existing chezmoi source"
      if [[ -n "$(git -C "$current" status --porcelain)" ]]; then
        die "Commit or stash source changes before updating: $current"
      fi
      # Fetch source changes without implicitly applying them.
      git -C "$current" pull --ff-only || die "Source update failed"
      ok "chezmoi source updated"
      return 0
    fi
    warn "Existing chezmoi source is invalid or unexpected"
    backup_broken_source "$current"
  fi

  if [[ -n "$candidate" ]]; then
    log "Initializing chezmoi from local source: $candidate"
    chezmoi init --source "$candidate" || die "chezmoi init --source failed"
  else
    log "Initializing chezmoi from ${REPO}"
    chezmoi init "$REPO" || die "chezmoi init failed"
  fi
  ok "chezmoi source initialized"
}

seed_local_overrides() {
  if [[ -f "$OVERRIDES_FILE" ]]; then
    if [[ -n "$MACHINE_PRESET" ]]; then
      local existing_preset
      existing_preset="$(DOTFILES_BOOTSTRAP_OVERRIDES="$OVERRIDES_FILE" chezmoi execute-template '{{ (include (env "DOTFILES_BOOTSTRAP_OVERRIDES") | fromToml).machine_preset | default "mac-dev" }}')" || die "Cannot read existing overrides"
      [[ "$MACHINE_PRESET" == "$existing_preset" ]] || die "Existing preset is $existing_preset. Edit machine_preset in $OVERRIDES_FILE first; no overrides were replaced."
    fi
    ok "Local overrides already present"
    return 0
  fi
  if [[ -z "$MACHINE_PRESET" && -t 0 ]]; then
    read -r -p "Machine preset [mac-dev/mac-minimal] (default mac-dev): " MACHINE_PRESET || MACHINE_PRESET=""
  fi
  MACHINE_PRESET="${MACHINE_PRESET:-mac-dev}"
  case "$MACHINE_PRESET" in
    mac-dev|mac-minimal) ;;
    *) die "Unknown preset: $MACHINE_PRESET (choose mac-dev or mac-minimal)" ;;
  esac
  mkdir -p "$OVERRIDES_DIR"
  log "Creating local overrides file"
  cat >"$OVERRIDES_FILE" <<EOF
# Machine-local, non-secret overrides.
machine_preset = "$MACHINE_PRESET"
profile = "personal"
provider = "gh"
work_contexts = []
primary_machine = false

# Optional machine-local Homebrew selection:
# [optional_integrations]
# homebrew_core = true
# homebrew_dev = true
# homebrew_apps = true
# homebrew_extras = false
# homebrew_work = false

# Optional machine-local 1Password vault pinning:
# [identity]
# op_vault = "Personal"
EOF
  ok "Created $OVERRIDES_FILE"
}

apply_dotfiles() {
  log "Applying dotfiles"
  chezmoi apply || die "chezmoi apply failed"
  ok "Dotfiles applied"
}

main() {
  parse_args "$@"
  is_supported_os || die "Unsupported OS: $(uname)"
  if [[ "$(uname)" == "Linux" ]]; then
    warn "macOS is the supported platform; Linux bootstrap is unvalidated and macOS hooks will skip."
  fi
  ensure_curl
  log "Bootstrapping dotfiles for $(uname)"

  install_homebrew_if_needed
  install_chezmoi

  local candidate=""
  candidate="$(find_local_source_candidate || true)"
  seed_local_overrides
  init_or_update_source "$candidate"
  apply_dotfiles

  log "Bootstrap complete"
  cat <<'EOF'

Debug commands:
  dots-debug --json
  dots-profile

Local machine selection:
  ~/.config/dotfiles/overrides.toml
  ~/.config/dotfiles/work-contexts/

If you still have legacy .chezmoidata/companies.toml data, migrate it soon.
Legacy support is transitional and will be removed after migration.
EOF
}

if [[ -z "${BASH_SOURCE[0]:-}" || "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
