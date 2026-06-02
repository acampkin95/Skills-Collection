#!/usr/bin/env bash
# =============================================================================
# sync.sh — Validate Dev_Skills, sync to master, symlink, package
#
# EXIT CODE CONTRACT:
#   0  Validation passed and all package operations succeeded
#   1  Validation passed but one or more per-skill package errors occurred
#   2  Catastrophic failure before/after the per-skill loop (e.g. missing dirs)
#   3  Validation failure — one or more skills failed SKILL.md checks
#
# REPORT ARTIFACTS (created under packaged/reports/):
#   latest.html        — stable symlink/alias to most recent HTML report
#   latest.json        — stable symlink/alias to most recent metrics summary
#   latest-run.json    — stable symlink/alias to most recent unified run manifest
#   history/<ts>/      — timestamped history dir (newest 10 runs retained)
#     report.html      — human-readable HTML report
#     metrics.json     — per-skill metrics (size, file count, warnings)
#     run.json         — unified run manifest (validation, rsync, symlink, packaging)
#     sync.log         — captured stdout from sync.sh
#     package.log      — captured stdout from package.sh
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_DIR="$REPO_ROOT/Dev_Skills"
MASTER_DIR="$REPO_ROOT/master"
PACKAGED_DIR="$REPO_ROOT/packaged"
REPORTS_DIR="$PACKAGED_DIR/reports"
RUN_TIMESTAMP="$(date -u '+%Y%m%dT%H%M%SZ')"
HISTORY_DIR="$REPORTS_DIR/history/$RUN_TIMESTAMP"

DRY_RUN=false
SKIP_PACKAGE=false
FORCE_SYMLINKS=false

RED=$'\033[0;31m'
GRN=$'\033[0;32m'
YEL=$'\033[0;33m'
BLU=$'\033[0;34m'
RST=$'\033[0m'

ERRORS=0
WARNINGS=0
VALIDATED=0
SKIPPED=0
SYNCED=0
REMOVED=0

SYMLINK_TARGETS=(
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.agents/skills"
  "$HOME/.config/opencode/skills"
)

RSYNC_EXCLUDES=(
  --exclude='.DS_Store'
  --exclude='.git'
  --exclude='.maintenance'
  --exclude='*.pkg'
  --exclude='*.deb'
  --exclude='*.dmg'
  --exclude='*.exe'
  --exclude='*.msi'
  --exclude='*.tar.gz'
  --exclude='*.tgz'
  --exclude='__pycache__'
  --exclude='*.pyc'
  --exclude='node_modules'
  --exclude='*.sqlite'
  --exclude='*.sqlite-shm'
  --exclude='*.sqlite-wal'
)

usage() {
  cat <<EOF
Usage: ./sync.sh [options]

Validate Dev_Skills, sync skill directories into master, update local skill
symlinks, and rebuild packaged/*.skill archives.

Options:
  --dry-run          Show what would change without writing files
  --skip-package     Sync without rebuilding packaged/*.skill files
  --force-symlinks   Replace existing real skill directories at local targets
  -h, --help         Show this help
EOF
}

log() {
  printf '%s\n' "$*"
}

die() {
  log "${RED}ERROR${RST} $*"
  exit 2
}

run() {
  if "$DRY_RUN"; then
    printf '  %sDRY%s  ' "$BLU" "$RST"
    printf '%q ' "$@"
    printf '\n'
  else
    "$@"
  fi
}

is_skill_dir() {
  [[ -d "$1" && ( -f "$1/SKILL.md" || -f "$1/skill.md" ) ]]
}

skill_md_path() {
  if [[ -f "$1/SKILL.md" ]]; then
    printf '%s\n' "$1/SKILL.md"
  elif [[ -f "$1/skill.md" ]]; then
    printf '%s\n' "$1/skill.md"
  fi
}

discover_skill_dirs() {
  local root="$1"
  local dir name

  [[ -d "$root" ]] || return 0

  for dir in "$root"/*/; do
    [[ -d "$dir" ]] || continue
    name="$(basename "$dir")"
    [[ "$name" == .* ]] && continue
    [[ "$name" == "learned" || "$name" == "logs" || "$name" == "reports" ]] && continue
    is_skill_dir "$dir" && printf '%s\n' "${dir%/}"
  done | sort
}

validate_skill() {
  local skill_dir="$1"
  local skill_name
  skill_name="$(basename "$skill_dir")"
  local skill_md
  skill_md="$(skill_md_path "$skill_dir")"
  local errors=0
  local warnings=0

  if [[ -z "$skill_md" || ! -f "$skill_md" ]]; then
    log "  ${RED}FAIL${RST} $skill_name: no SKILL.md or skill.md found"
    ((ERRORS++)) || true
    return 1
  fi

  local first_line
  first_line="$(head -n 1 "$skill_md")"
  if [[ "$first_line" != "---" ]]; then
    log "  ${RED}FAIL${RST} $skill_name: missing opening --- in YAML frontmatter"
    ((errors++)) || true
  fi

  local closing_line
  closing_line="$(awk '/^---/{n++; if(n==2){print NR; exit}} END{if(n<2) print 0}' "$skill_md")"
  if [[ "$closing_line" == "0" ]]; then
    log "  ${RED}FAIL${RST} $skill_name: missing closing --- in YAML frontmatter"
    ((errors++)) || true
  fi

  local name_val
  name_val="$(awk -F': ' '/^name:/{print $2}' "$skill_md" | head -n 1 | tr -d '"' | tr -d "'")"
  if [[ -z "$name_val" ]]; then
    log "  ${RED}FAIL${RST} $skill_name: missing 'name' field in frontmatter"
    ((errors++)) || true
  elif [[ ${#name_val} -gt 64 ]]; then
    log "  ${RED}FAIL${RST} $skill_name: name exceeds 64 characters (${#name_val})"
    ((errors++)) || true
  elif ! grep -qE '^[a-z0-9-]+$' <<< "$name_val"; then
    log "  ${RED}FAIL${RST} $skill_name: invalid name '$name_val' (lowercase, numbers, hyphens only)"
    ((errors++)) || true
  elif grep -qiE 'anthropic|claude' <<< "$name_val" && [[ "$name_val" != "claude-code" ]]; then
    log "  ${RED}FAIL${RST} $skill_name: name contains reserved word (anthropic/claude)"
    ((errors++)) || true
  fi

  if [[ -n "$name_val" && "$name_val" != "$skill_name" ]]; then
    log "  ${YEL}WARN${RST} $skill_name: name '$name_val' != directory '$skill_name'"
    ((warnings++)) || true
  fi

  local desc_val
  desc_val="$(awk '/^description:/{sub(/^description: /, ""); print; exit}' "$skill_md")"
  if [[ -z "$desc_val" ]]; then
    log "  ${RED}FAIL${RST} $skill_name: missing 'description' field in frontmatter"
    ((errors++)) || true
  elif [[ ${#desc_val} -gt 1024 ]]; then
    log "  ${RED}FAIL${RST} $skill_name: description exceeds 1024 chars (${#desc_val})"
    ((errors++)) || true
  fi

  if grep -qE '^".*"$|^'\''.*'\''$' <<< "$desc_val"; then
    log "  ${YEL}WARN${RST} $skill_name: description is quote-wrapped"
    ((warnings++)) || true
  fi

  if [[ -n "$desc_val" && ${#desc_val} -lt 40 ]]; then
    log "  ${YEL}WARN${RST} $skill_name: description is very short (${#desc_val} chars)"
    ((warnings++)) || true
  fi

  local line_count
  line_count="$(wc -l < "$skill_md" | tr -d ' ')"
  if [[ "$line_count" -gt 500 ]]; then
    log "  ${RED}FAIL${RST} $skill_name: SKILL.md is ${line_count} lines (max 500)"
    ((errors++)) || true
  fi

  local fm_content
  fm_content="$(awk '/^---/{n++; next} n==1{print}' "$skill_md")"
  if grep -qE '<[^>]+>' <<< "$fm_content"; then
    log "  ${RED}FAIL${RST} $skill_name: XML tags found in frontmatter"
    ((errors++)) || true
  fi

  local body_headings
  body_headings="$(awk 'BEGIN{f=0} /^---/{f++; next} f>=2 && /^#/{print}' "$skill_md" | wc -l | tr -d ' ')"
  if [[ "$body_headings" -eq 0 ]]; then
    log "  ${YEL}WARN${RST} $skill_name: no markdown headings in body"
    ((warnings++)) || true
  fi

  local bins
  bins="$(find "$skill_dir" -type f \( -name '*.pkg' -o -name '*.deb' -o -name '*.dmg' -o -name '*.exe' -o -name '*.msi' \) 2>/dev/null || true)"
  if [[ -n "$bins" ]]; then
    log "  ${YEL}WARN${RST} $skill_name: contains binary files excluded from packages"
    while IFS= read -r file; do
      [[ -n "$file" ]] && log "       $(basename "$file")"
    done <<< "$bins"
    ((warnings++)) || true
  fi

  local desc_lower
  desc_lower="$(tr '[:upper:]' '[:lower:]' <<< "$desc_val")"
  if grep -qE '^use this skill when.*use this skill when' <<< "$desc_lower"; then
    log "  ${YEL}WARN${RST} $skill_name: description contains duplicated trigger phrase"
    ((warnings++)) || true
  fi

  ((ERRORS+=errors)) || true
  ((WARNINGS+=warnings)) || true

  if [[ "$errors" -gt 0 ]]; then
    log "  ${RED}FAIL${RST} $skill_name: ${errors} error(s), ${warnings} warning(s)"
    return 1
  fi

  if [[ "$warnings" -gt 0 ]]; then
    log "  ${GRN} OK ${RST}  $skill_name (${warnings} warning(s))"
  else
    log "  ${GRN} OK ${RST}  $skill_name"
  fi
}

sync_skills() {
  local -a dev_skill_dirs=("$@")
  local skill_dir skill_name dest

  mkdir -p "$MASTER_DIR"

  for skill_dir in "${dev_skill_dirs[@]}"; do
    skill_name="$(basename "$skill_dir")"
    dest="$MASTER_DIR/$skill_name"
    run mkdir -p "$dest"

    if "$DRY_RUN"; then
      rsync -ani --delete "${RSYNC_EXCLUDES[@]}" "$skill_dir/" "$dest/" | sed "s/^/  ${BLU}DRY${RST}  /"
    else
      rsync -a --delete "${RSYNC_EXCLUDES[@]}" "$skill_dir/" "$dest/"
    fi

    ((SYNCED++)) || true
  done
}

remove_orphaned_master_skills() {
  local master_skill dev_match skill_name

  while IFS= read -r master_skill; do
    skill_name="$(basename "$master_skill")"
    dev_match="$DEV_DIR/$skill_name"
    if ! is_skill_dir "$dev_match"; then
      log "  ${YEL}REMOVE${RST} master/$skill_name (not present in Dev_Skills)"
      run rm -rf "$master_skill"
      ((REMOVED++)) || true
    fi
  done < <(discover_skill_dirs "$MASTER_DIR")
}

ensure_symlinks() {
  local target current

  for target in "${SYMLINK_TARGETS[@]}"; do
    if [[ -L "$target" ]]; then
      current="$(readlink "$target")"
      if [[ "$current" == "$MASTER_DIR" ]]; then
        log "  ${GRN} OK ${RST}  $target -> master/"
        continue
      fi
      log "  ${YEL}UPDATE${RST} $target -> master/"
      run rm "$target"
    elif [[ -d "$target" ]]; then
      if "$FORCE_SYMLINKS"; then
        log "  ${YEL}REPLACE${RST} $target real directory -> symlink"
        run rm -rf "$target"
      else
        log "  ${YEL}SKIP${RST}  $target is a real directory (use --force-symlinks to replace)"
        continue
      fi
    elif [[ -e "$target" ]]; then
      log "  ${YEL}UPDATE${RST} $target file -> symlink"
      run rm "$target"
    fi

    run mkdir -p "$(dirname "$target")"
    run ln -s "$MASTER_DIR" "$target"
    log "  ${GRN} OK ${RST}  $target -> master/ (created)"
  done
}

package_skills() {
  if "$SKIP_PACKAGE"; then
    log "  ${YEL}SKIP${RST} packaging (--skip-package)"
    return 0
  fi

  if [[ ! -f "$REPO_ROOT/package.sh" ]]; then
    log "  ${YEL}SKIP${RST} package.sh not found"
    return 0
  fi

  if "$DRY_RUN"; then
    run rm -f "$PACKAGED_DIR"/*.skill
    run "$REPO_ROOT/package.sh"
    return 0
  fi

  mkdir -p "$PACKAGED_DIR"
  rm -f "$PACKAGED_DIR"/*.skill
  "$REPO_ROOT/package.sh"
}

# JSON schema for latest-run.json (unified run manifest):
# {
#   "run_timestamp": "<ISO 8601 UTC>",
#   "exit_code": 0|1|2|3,
#   "phases": {
#     "validation": { "status": "ok"|"error", "passed": N, "failed": N, "warnings": N, "failed_skills": [] },
#     "rsync":       { "status": "ok", "synced": N, "removed": N },
#     "symlink":     { "status": "ok", "targets": N },
#     "packaging":   { "status": "ok"|"error", "total": N, "ok": N, "error": N, "skip_not_skill": N, "skills": [
#       { "name": "<skill>", "state": "ok"|"error"|"skip_not_skill", "size": "<human>" }
#     ]},
#     "reporting":   { "status": "ok"|"error", "reports_dir": "<path>" }
#   },
#   "duration_seconds": N
# }

init_reports() {
  mkdir -p "$HISTORY_DIR"

  local history_dirs
  history_dirs=()
  while IFS= read -r d; do
    [[ -n "$d" ]] && history_dirs+=("$d")
  done < <(find "$REPORTS_DIR/history" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)

  local count="${#history_dirs[@]}"
  if [[ "$count" -gt 10 ]]; then
    local to_remove=$((count - 10))
    local i
    for ((i = 0; i < to_remove; i++)); do
      rm -rf "${history_dirs[$i]}"
    done
  fi
}

emit_run_manifest() {
  local pkg_exit="$1"
  local run_exit
  if [[ "$pkg_exit" -eq 0 ]]; then
    run_exit=0
  else
    run_exit=1
  fi

  local manifest="$HISTORY_DIR/run.json"
  cat > "$manifest" <<RUNEOF
{
  "run_timestamp": "$RUN_TIMESTAMP",
  "exit_code": $run_exit,
  "phases": {
    "validation": { "status": "ok", "passed": $VALIDATED, "failed": ${#failed_skills[@]}, "warnings": $WARNINGS, "failed_skills": [] },
    "rsync":       { "status": "ok", "synced": $SYNCED, "removed": $REMOVED },
    "symlink":     { "status": "ok", "targets": ${#SYMLINK_TARGETS[@]} },
    "packaging":   { "status": "ok", "total": 0, "ok": 0, "error": 0, "skip_not_skill": 0, "skills": [] },
    "reporting":   { "status": "ok", "reports_dir": "$REPORTS_DIR" }
  },
  "duration_seconds": 0
}
RUNEOF

  ln -sf "$manifest" "$REPORTS_DIR/latest-run.json"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      ;;
    --skip-package)
      SKIP_PACKAGE=true
      ;;
    --force-symlinks)
      FORCE_SYMLINKS=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      die "unknown option: $1"
      ;;
  esac
  shift
done

[[ -d "$DEV_DIR" ]] || die "Dev_Skills directory not found: $DEV_DIR"
[[ -d "$MASTER_DIR" ]] || die "master directory not found: $MASTER_DIR"

log "========================================"
log " Skills Sync - Validate & Deploy"
log "========================================"
log ""
log "Source:   $DEV_DIR"
log "Target:   $MASTER_DIR"
log "Packages: $PACKAGED_DIR"
"$DRY_RUN" && log "Mode:     dry run"
log ""

log "Phase 1: Validating Dev_Skills/"
log "----------------------------------------"

failed_skills=()
dev_skill_dirs=()

while IFS= read -r skill_dir; do
  dev_skill_dirs+=("$skill_dir")
done < <(discover_skill_dirs "$DEV_DIR")

if [[ "${#dev_skill_dirs[@]}" -eq 0 ]]; then
  die "no skill directories found in $DEV_DIR"
fi

for skill_dir in "${dev_skill_dirs[@]}"; do
  if validate_skill "$skill_dir"; then
    ((VALIDATED++)) || true
  else
    failed_skills+=("$(basename "$skill_dir")")
  fi
done

log ""
log "----------------------------------------"
log "Results: ${GRN}${VALIDATED} passed${RST}, ${RED}${#failed_skills[@]} failed${RST}, ${YEL}${SKIPPED} skipped${RST}, ${WARNINGS} warnings"
log "----------------------------------------"
log ""

if [[ "${#failed_skills[@]}" -gt 0 ]]; then
  log "${RED}SYNC BLOCKED${RST} - ${#failed_skills[@]} skill(s) failed validation:"
  for skill_name in "${failed_skills[@]}"; do
    log "  - $skill_name"
  done
  log ""
  log "Fix the errors above and re-run sync.sh"
  exit 3
fi

log "Phase 2: Syncing Dev_Skills/ -> master/"
log "----------------------------------------"
sync_skills "${dev_skill_dirs[@]}"
remove_orphaned_master_skills
log "Synced $SYNCED skill directories to master/"
[[ "$REMOVED" -gt 0 ]] && log "Removed $REMOVED orphaned skill directories from master/"
log ""

log "Phase 3: Ensuring local skill symlinks"
log "----------------------------------------"
ensure_symlinks
log ""

log "Phase 4: Re-packaging .skill files"
log "----------------------------------------"
init_reports
package_exit=0
package_skills || package_exit=$?
log ""

if [[ "$package_exit" -ne 0 && "$package_exit" -ne 1 ]]; then
  log "${RED}CATASTROPHIC${RST} package.sh exited with $package_exit"
  emit_run_manifest "$package_exit"
  exit 2
fi

emit_run_manifest "$package_exit"

package_count="$(find "$PACKAGED_DIR" -maxdepth 1 -name '*.skill' 2>/dev/null | wc -l | tr -d ' ')"

log "========================================"
if [[ "$package_exit" -eq 0 ]]; then
  log " ${GRN}Sync complete${RST}"
else
  log " ${YEL}Sync complete (with package errors)${RST}"
fi
log "========================================"
log "  Validated: $VALIDATED skills"
log "  Warnings:  $WARNINGS"
log "  Synced:    $SYNCED skills"
log "  Removed:   $REMOVED orphaned skills"
log "  Symlinks:  ${#SYMLINK_TARGETS[@]} targets"
log "  Packages:  $package_count .skill files"
log "  Reports:   $REPORTS_DIR"
log ""

if [[ "$package_exit" -ne 0 ]]; then
  exit 1
fi
