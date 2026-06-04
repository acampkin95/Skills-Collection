#!/usr/bin/env bash
# =============================================================================
# package.sh — Create .skill zip archives from master/ skill directories
#
# EXIT CODE CONTRACT:
#   0  All skills packaged successfully (or no skills to package)
#   1  One or more per-skill package errors occurred
#
# PACKAGING STATES (per skill):
#   ok              — SKILL.md found, zip created successfully
#   error           — zip creation failed
#   skip_not_skill  — no SKILL.md/skill.md found (non-skill directory like learned/)
#
# ENVIRONMENT:
#   HISTORY_DIR  — If set (by sync.sh), per-skill log entries written to
#                  $HISTORY_DIR/package.log as JSON lines
#
# Can be called standalone: ./package.sh [skill_name ...]
# When called without args, packages all directories under master/
# =============================================================================
set -euo pipefail

# Resolve REPO_ROOT: SkillsFramework/scripts/ -> repo root (go up 2 levels)
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills_master"
OUT_DIR="$REPO_ROOT/skills_conversions/Claude-Desktop"

mkdir -p "$OUT_DIR"

PKG_OK=0
PKG_ERROR=0
PKG_SKIP=0

log_entry() {
  local skill="$1" state="$2" size_bytes="${3:-0}" error="${4:-null}"
  local file_count="${5:-0}" categories_json="${6:-{\"md\":0,\"scripts\":0,\"refs\":0,\"other\":0}}" excluded_bin="${7:-false}"
  if [[ -n "${HISTORY_DIR:-}" ]]; then
    printf '{"skill":"%s","state":"%s","size_bytes":%d,"file_count":%d,"categories":%s,"excluded_binary_warning":%s,"error":%s}\n' \
      "$skill" "$state" "$size_bytes" "$file_count" "$categories_json" "$excluded_bin" "$error" \
      >> "$HISTORY_DIR/package.log"
  fi
}

package_skill() {
  local skill_dir="$1"
  local skill_name
  skill_name="$(basename "$skill_dir")"
  local outfile="$OUT_DIR/${skill_name}.skill"

  if [ ! -f "$skill_dir/SKILL.md" ] && [ ! -f "$skill_dir/skill.md" ]; then
    log_entry "$skill_name" "skip_not_skill" 0 "null"
    echo "SKIP  $skill_name (no SKILL.md or skill.md)"
    return 2
  fi

  local pkg_output pkg_rc=0
  pkg_output=$(
    cd "$skill_dir"
    zip -r -q "$outfile" . \
      -x "*.DS_Store" \
      -x "*__pycache__*" \
      -x "*.pyc" \
      -x "*.pkg" \
      -x "*.deb" \
      -x "*.dmg" \
      -x "*.exe" \
      -x "*.msi" \
      -x "*.tar.gz" \
      -x "*.tgz" \
      -x "node_modules/*" \
      -x ".git/*" \
      -x ".git/*/*" \
      -x ".maintenance/*" \
      -x ".maintenance/*/*" \
      -x ".omc/*" \
      -x ".omc/*/*" \
      -x ".omc/*/*/*" \
      -x ".omc/*/*/*/*" \
      -x "*.sqlite" \
      -x "*.sqlite-shm" \
      -x "*.sqlite-wal" \
      2>&1
  ) || pkg_rc=$?

  if [[ $pkg_rc -eq 0 ]]; then
    local size_bytes
    size_bytes="$(stat -f%z "$outfile" 2>/dev/null || echo 0)"
    local size
    size="$(du -h "$outfile" | cut -f1 | xargs)"

    # --- composition metrics ---
    local file_list fc md_count scripts_count refs_count other_count
    file_list="$(zipinfo -1 "$outfile")"
    fc="$(echo "$file_list" | wc -l | xargs)"
    md_count="$(echo "$file_list" | grep -c '\.md$' || true)"
    scripts_count="$(echo "$file_list" | grep -cE '\.(sh|py|js|ts)$' || true)"
    refs_count="$(echo "$file_list" | grep -c '^references/' || true)"
    other_count=$(( fc - md_count - scripts_count - refs_count ))
    local cats="{\"md\":${md_count},\"scripts\":${scripts_count},\"refs\":${refs_count},\"other\":${other_count}}"

    # binary warning: true if zip stderr mentioned skipping or pkg_output has warnings
    local bin_warn="false"
    if echo "$pkg_output" | grep -qi "skipping\|binary\|warning"; then
      bin_warn="true"
    fi

    log_entry "$skill_name" "ok" "$size_bytes" "null" "$fc" "$cats" "$bin_warn"
    echo "OK    $skill_name -> ${skill_name}.skill ($size, ${fc} files)"
    return 0
  else
    local first_err
    first_err="$(echo "$pkg_output" | head -1)"
    log_entry "$skill_name" "error" 0 "\"${first_err//\"/\\\"}\"" 0 "{\"md\":0,\"scripts\":0,\"refs\":0,\"other\":0}" "false"
    echo -e "\033[0;31mERROR $skill_name (zip failed): ${first_err}\033[0m"
    return 1
  fi
}

count_skills() {
  if [ $# -gt 0 ]; then
    echo "$#"
    return
  fi
  local count=0
  for d in "$SKILLS_DIR"/*/; do
    [ -d "$d" ] && ((count++)) || true
  done
  echo "$count"
}

echo "Packaging skills from: $SKILLS_DIR"
echo "Output directory:      $OUT_DIR"
echo "---"

TOTAL=$(count_skills "$@")
CURRENT=0

if [ $# -gt 0 ]; then
  for name in "$@"; do
    ((CURRENT++)) || true
    echo -n "[$CURRENT/$TOTAL] "
    if [ -d "$SKILLS_DIR/$name" ]; then
      pkg_rc=0
      package_skill "$SKILLS_DIR/$name" || pkg_rc=$?
      if [[ $pkg_rc -eq 0 ]]; then
        ((PKG_OK++)) || true
      elif [[ $pkg_rc -eq 2 ]]; then
        ((PKG_SKIP++)) || true
      else
        ((PKG_ERROR++)) || true
      fi
    else
      echo "SKIP  $name (directory not found)"
      log_entry "$name" "skip_not_skill" 0 "null"
      ((PKG_SKIP++)) || true
    fi
  done
else
  for skill_dir in "$SKILLS_DIR"/*/; do
    [ -d "$skill_dir" ] || continue
    ((CURRENT++)) || true
    echo -n "[$CURRENT/$TOTAL] "
    pkg_rc=0
    package_skill "$skill_dir" || pkg_rc=$?
    if [[ $pkg_rc -eq 0 ]]; then
      ((PKG_OK++)) || true
    elif [[ $pkg_rc -eq 2 ]]; then
      ((PKG_SKIP++)) || true
    else
      ((PKG_ERROR++)) || true
    fi
  done
fi

echo "---"
echo "Total: $(ls "$OUT_DIR"/*.skill 2>/dev/null | wc -l | xargs) packages in $OUT_DIR"
echo "Stats: ok=$PKG_OK  error=$PKG_ERROR  skip=$PKG_SKIP"

if [[ "$PKG_ERROR" -gt 0 ]]; then
  exit 1
fi
