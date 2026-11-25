#!/usr/bin/env bash
# agy-mpm-kit installer & language edition switcher for Google Antigravity.
# Manages ONLY the ~/.gemini/config/plugins/agy-mpm-core symlink.
# NEVER reads or modifies ~/.gemini/config/config.json.

set -euo pipefail

PLUGIN_DIR_NAME="agy-mpm-core"
PLUGINS_ROOT="${AGY_PLUGINS_DIR:-${HOME}/.gemini/config/plugins}"
TARGET_LINK="${PLUGINS_ROOT}/${PLUGIN_DIR_NAME}"

# Resolve repository root portably even if invoked via relative path or symlink
resolve_script_dir() {
  local src="${BASH_SOURCE[0]}"
  while [ -L "${src}" ]; do
    local dir
    dir="$(cd -P "$(dirname "${src}")" && pwd)"
    src="$(readlink "${src}")"
    [[ "${src}" != /* ]] && src="${dir}/${src}"
  done
  cd -P "$(dirname "${src}")" && pwd
}

REPO_ROOT="$(resolve_script_dir)"

usage() {
  cat <<'EOF'
agy-mpm-kit — Installer & Edition Switcher (v1.9.0)

Usage:
  ./install.sh [--lang en|ru] [--force]
  ./install.sh --status
  ./install.sh --uninstall
  ./install.sh --help

Options:
  --lang <en|ru>  Install or switch active plugin edition (default: en)
                    en -> symlinks repo root (English rules & templates, lowest token footprint)
                    ru -> symlinks ./ru      (Native Russian rules & templates)
  --status        Show current installation state, symlink target, and active language edition
  --uninstall     Remove ~/.gemini/config/plugins/agy-mpm-core ONLY if it is a symlink
  --force         Allow replacing an existing non-symlink directory (backs it up with .bak.<timestamp>)
  -h, --help      Show this help message and exit

Notes:
  - Antigravity discovers plugin changes automatically (no IDE restart required).
  - Toggle the plugin on/off anytime in 1 click via /plugin (customization://agy-mpm-core).
  - This script NEVER modifies ~/.gemini/config/config.json.
EOF
}

read_version() {
  local manifest="$1"
  if [ -f "${manifest}" ]; then
    sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "${manifest}" | head -n 1
  fi
}

detect_edition() {
  local link_target="$1"
  local resolved=""
  if [ -d "${link_target}" ]; then
    resolved="$(cd -P "${link_target}" 2>/dev/null && pwd || true)"
  fi

  if [ "${resolved}" = "${REPO_ROOT}/ru" ] || [[ "${link_target}" == */ru ]]; then
    printf "ru (Russian edition)"
  elif [ "${resolved}" = "${REPO_ROOT}" ]; then
    printf "en (English edition)"
  else
    printf "external/custom (%s)" "${link_target}"
  fi
}

cmd_status() {
  printf "Plugin slot : %s\n" "${TARGET_LINK}"
  printf "Kit repo    : %s\n" "${REPO_ROOT}"

  if [ -L "${TARGET_LINK}" ]; then
    local raw_target
    raw_target="$(readlink "${TARGET_LINK}")"
    local resolved_target="${raw_target}"
    if [[ "${raw_target}" != /* ]]; then
      resolved_target="$(dirname "${TARGET_LINK}")/${raw_target}"
    fi

    if [ -f "${resolved_target}/plugin.json" ]; then
      local ver
      ver="$(read_version "${resolved_target}/plugin.json")"
      printf "State       : INSTALLED (valid symlink)\n"
      printf "Target      : %s\n" "${raw_target}"
      printf "Edition     : %s\n" "$(detect_edition "${resolved_target}")"
      [ -n "${ver}" ] && printf "Version     : v%s\n" "${ver}"
      printf "Manage UI   : /plugin -> customization://%s\n" "${PLUGIN_DIR_NAME}"
    else
      printf "State       : BROKEN SYMLINK (target plugin.json not found)\n"
      printf "Target      : %s\n" "${raw_target}"
      return 1
    fi
  elif [ -e "${TARGET_LINK}" ]; then
    printf "State       : NON-SYMLINK DIRECTORY/FILE PRESENT\n"
    printf "Warning     : %s exists and is not a symlink.\n" "${TARGET_LINK}"
    printf "              Re-run with --force to back it up and replace it with a managed symlink.\n"
  else
    printf "State       : NOT INSTALLED\n"
    printf "Install EN  : ./install.sh --lang en\n"
    printf "Install RU  : ./install.sh --lang ru\n"
  fi
}

cmd_uninstall() {
  if [ -L "${TARGET_LINK}" ]; then
    local prev_target
    prev_target="$(readlink "${TARGET_LINK}")"
    rm -f "${TARGET_LINK}"
    printf "Removed symlink: %s (was -> %s)\n" "${TARGET_LINK}" "${prev_target}"
    printf "Note: ~/.gemini/config/config.json was left untouched.\n"
  elif [ -e "${TARGET_LINK}" ]; then
    printf "Error: Refusing to uninstall %s because it is a real directory/file (not a symlink).\n" "${TARGET_LINK}" >&2
    printf "Move or inspect it manually to avoid accidental data loss.\n" >&2
    exit 1
  else
    printf "Nothing to uninstall: %s does not exist.\n" "${TARGET_LINK}"
  fi
}

cmd_install() {
  local lang="$1"
  local force="$2"
  local source_dir=""

  case "${lang}" in
    en)
      source_dir="${REPO_ROOT}"
      ;;
    ru)
      source_dir="${REPO_ROOT}/ru"
      ;;
    *)
      printf "Error: Unsupported language '%s'. Expected 'en' or 'ru'.\n" "${lang}" >&2
      exit 1
      ;;
  esac

  if [ ! -f "${source_dir}/plugin.json" ]; then
    printf "Error: Cannot find plugin manifest at '%s/plugin.json'.\n" "${source_dir}" >&2
    exit 1
  fi

  mkdir -p "${PLUGINS_ROOT}"

  if [ -L "${TARGET_LINK}" ]; then
    # Remove existing symlink first so BSD/macOS ln -s never traverses into target dir
    rm -f "${TARGET_LINK}"
  elif [ -e "${TARGET_LINK}" ]; then
    if [ "${force}" != "true" ]; then
      printf "Error: '%s' already exists as a non-symlink directory or file.\n" "${TARGET_LINK}" >&2
      printf "Refusing to overwrite safely. Move it manually or pass --force to back it up automatically.\n" >&2
      exit 1
    fi
    local backup_path
    backup_path="${TARGET_LINK}.bak.$(date +%Y%m%d%H%M%S)"
    mv "${TARGET_LINK}" "${backup_path}"
    printf "Backed up existing non-symlink target to: %s\n" "${backup_path}"
  fi

  ln -s "${source_dir}" "${TARGET_LINK}"

  local ver
  ver="$(read_version "${source_dir}/plugin.json")"
  printf "Installed %s (%s%s):\n" "${PLUGIN_DIR_NAME}" "${lang}" "${ver:+, v${ver}}"
  printf "  %s -> %s\n" "${TARGET_LINK}" "${source_dir}"
  printf "\nNext steps in Google Antigravity:\n"
  printf "  1. Manage or toggle live via /plugin (customization://%s)\n" "${PLUGIN_DIR_NAME}"
  printf "  2. Open any project and run: /kit-bootstrap --lite | --full | --migrate or /kit-architecture\n"
}

ACTION="install"
LANG_CHOICE="en"
FORCE_INSTALL="false"

while [ $# -gt 0 ]; do
  case "$1" in
    --lang)
      if [ $# -lt 2 ]; then
        printf "Error: --lang requires an argument ('en' or 'ru').\n" >&2
        exit 1
      fi
      LANG_CHOICE="$2"
      shift 2
      ;;
    --lang=*)
      LANG_CHOICE="${1#--lang=}"
      shift
      ;;
    --status)
      ACTION="status"
      shift
      ;;
    --uninstall)
      ACTION="uninstall"
      shift
      ;;
    --force)
      FORCE_INSTALL="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf "Error: Unknown argument '%s'. Run './install.sh --help' for usage.\n" "$1" >&2
      exit 1
      ;;
  esac
done

case "${ACTION}" in
  status)
    cmd_status
    ;;
  uninstall)
    cmd_uninstall
    ;;
  install)
    cmd_install "${LANG_CHOICE}" "${FORCE_INSTALL}"
    ;;
esac
