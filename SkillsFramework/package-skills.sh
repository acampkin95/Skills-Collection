#!/usr/bin/env bash
# Claude Skills Manager — validate and package skills as .skill ZIP archives
# Usage:
#   ./package-skills.sh              Interactive menu
#   ./package-skills.sh validate     Validate all skills (exit 1 if any fail)
#   ./package-skills.sh package      Package all skills (skip failures)
#   ./package-skills.sh single NAME  Validate & package a single skill
#   ./package-skills.sh clean        Remove all .skill packages
#   ./package-skills.sh list         List packaged skills
#   ./package-skills.sh help         Show this help
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MAINT_DIR="$SCRIPT_DIR"
# Canonical distribution point for packaged .skill zips (2026-06-02 refactor)
PACKAGES_DIR="$SKILLS_ROOT/skills_conversions/Claude-Desktop"
SKILLS_REF_SRC="$MAINT_DIR/skills-ref/src"
VENV_DIR="$MAINT_DIR/.venv"
PYTHON="$VENV_DIR/bin/python3"

# ── Colors ────────────────────────────────────────────────────────────────────
BOLD=$'\e[1m'
RESET=$'\e[0m'
GREEN=$'\e[32m'
RED=$'\e[31m'
YELLOW=$'\e[33m'
CYAN=$'\e[36m'
DIM=$'\e[2m'

# ── Venv auto-setup ───────────────────────────────────────────────────────────
ensure_venv() {
  if [[ -x "$PYTHON" ]] && "$PYTHON" -c "import strictyaml" 2>/dev/null; then
    return 0
  fi

  echo "${YELLOW}First-run setup: creating Python venv and installing skills-ref...${RESET}"

  if command -v uv &>/dev/null; then
    uv venv --python 3.11 "$VENV_DIR" --quiet 2>/dev/null \
      || uv venv "$VENV_DIR" --quiet
    uv pip install --python "$PYTHON" \
      --editable "$MAINT_DIR/skills-ref" --quiet
  else
    # Check Python version — skills-ref requires 3.11+
    local py_version
    py_version="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    local py_major py_minor
    py_major="${py_version%%.*}"
    py_minor="${py_version##*.}"
    if [[ "$py_major" -lt 3 ]] || { [[ "$py_major" -eq 3 ]] && [[ "$py_minor" -lt 11 ]]; }; then
      echo "${RED}Error: skills-ref requires Python ≥3.11, but found $py_version${RESET}"
      echo "Install uv (https://docs.astral.sh/uv/) or Python 3.11+ to continue."
      exit 1
    fi
    python3 -m venv "$VENV_DIR"
    "$PYTHON" -m pip install --quiet \
      --editable "$MAINT_DIR/skills-ref"
  fi

  echo "${GREEN}✓ Setup complete.${RESET}"
  echo
}

# ── Trap ──────────────────────────────────────────────────────────────────────
trap 'echo; echo "${YELLOW}Interrupted.${RESET}"; exit 130' INT TERM

# ── Python helper: validate one skill dir → JSON {"errors": [...], "count": N}
py_validate() {
  local skill_dir="$1"
  "$PYTHON" - "$skill_dir" "$SKILLS_REF_SRC" <<'PYEOF'
import sys, json
skill_dir, src = sys.argv[1], sys.argv[2]
sys.path.insert(0, src)
from pathlib import Path
from skills_ref.validator import validate
errors = validate(Path(skill_dir))
json.dump({"errors": errors, "count": len(errors)}, sys.stdout)
PYEOF
}

# ── Python helper: extract error count from validate JSON ─────────────────────
py_error_count() {
  "$PYTHON" -c "import json,sys; print(json.loads(sys.stdin.read())['count'])"
}

# ── Python helper: package one skill dir → ZIP ────────────────────────────────
py_package() {
  local skill_dir="$1"
  local out_path="$2"
  "$PYTHON" - "$skill_dir" "$out_path" <<'PYEOF'
import zipfile, os, sys
skill_dir, out_path = sys.argv[1], sys.argv[2]
name = os.path.basename(skill_dir)
EXCLUDE = {'__pycache__', '.DS_Store', '.git', '.gitignore'}
with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(skill_dir):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE)
        for f in sorted(files):
            if f in EXCLUDE or f.endswith('.pyc'):
                continue
            full = os.path.join(root, f)
            arc = os.path.join(name, os.path.relpath(full, skill_dir))
            zf.write(full, arc)
PYEOF
}

# ── Discover skill directories ───────────────────────────────────────────────
discover_skills() {
  # Scan only the canonical skill source: $SKILLS_ROOT/skills_master/
  # (Previously this iterated $SKILLS_ROOT/*/ which also picked up .aistore/,
  # .archive/, SkillsFramework/, etc. — wrong now that the repo root contains
  # more than just skill dirs.)
  local -a skills=()
  local skills_src="$SKILLS_ROOT/skills_master"
  local skip_dirs=(".maintenance" ".omc" ".sisyphus" "learned" "logs")
  [[ -d "$skills_src" ]] || return 0
  for dir in "$skills_src"/*/; do
    [[ ! -d "$dir" ]] && continue
    [[ -L "$dir" ]] && continue
    local dname
    dname="$(basename "$dir")"
    # skip dot-dirs
    [[ "$dname" == .* ]] && continue
    # skip explicit dirs
    local skip=false
    for s in "${skip_dirs[@]}"; do
      [[ "$dname" == "$s" ]] && skip=true && break
    done
    $skip && continue
    # must contain SKILL.md or skill.md
    if [[ -f "$dir/SKILL.md" || -f "$dir/skill.md" ]]; then
      skills+=("$dir")
    fi
  done
  printf '%s\n' "${skills[@]}"
}

# ── Ensure packages dir exists ────────────────────────────────────────────────
ensure_packages_dir() {
  mkdir -p "$PACKAGES_DIR"
}

# ── 1. Validate all skills ────────────────────────────────────────────────────
cmd_validate_all() {
  echo
  echo "${BOLD}${CYAN}Validating all skills...${RESET}"
  echo

  local -a skill_dirs
  mapfile -t skill_dirs < <(discover_skills)
  local total="${#skill_dirs[@]}"

  if [[ $total -eq 0 ]]; then
    echo "${YELLOW}No skills found.${RESET}"
    return 0
  fi

  local pass=0 fail=0
  local -a failures=()

  for skill_dir in "${skill_dirs[@]}"; do
    local sname
    sname="$(basename "$skill_dir")"
    local result
    result="$(py_validate "$skill_dir")"
    local error_count
    error_count="$(echo "$result" | py_error_count)"

    if [[ "$error_count" -eq 0 ]]; then
      printf "  ${GREEN}✓${RESET} %-40s ${DIM}pass${RESET}\n" "$sname"
      ((pass++)) || true
    else
      printf "  ${RED}✗${RESET} %-40s ${RED}FAIL (%d error(s))${RESET}\n" "$sname" "$error_count"
      ((fail++)) || true
      failures+=("$skill_dir:$result")
    fi
  done

  echo
  echo "${BOLD}Summary:${RESET} ${GREEN}${pass} passed${RESET}, ${RED}${fail} failed${RESET} / ${total} total"

  if [[ ${#failures[@]} -gt 0 ]]; then
    echo
    echo "${BOLD}${RED}Error details:${RESET}"
    for entry in "${failures[@]}"; do
      local sdir="${entry%%:*}"
      local res="${entry#*:}"
      local ename
      ename="$(basename "$sdir")"
      echo
      echo "  ${RED}${BOLD}${ename}${RESET}"
      "$PYTHON" -c "
import json, sys
d = json.loads(sys.stdin.read())
for e in d['errors']:
    print('    •', e)
" <<< "$res"
    done
  fi
  echo

  # Return non-zero for CI/automation if any skill failed
  [[ "$fail" -gt 0 ]] && return 1
  return 0
}

# ── 2. Package all skills ─────────────────────────────────────────────────────
cmd_package_all() {
  ensure_packages_dir
  echo
  echo "${BOLD}${CYAN}Packaging all skills...${RESET}"
  echo

  local -a skill_dirs
  mapfile -t skill_dirs < <(discover_skills)
  local total="${#skill_dirs[@]}"

  if [[ $total -eq 0 ]]; then
    echo "${YELLOW}No skills found.${RESET}"
    return 0
  fi

  local packaged=0 skipped=0 idx=0
  local -a skip_reasons=()

  for skill_dir in "${skill_dirs[@]}"; do
    ((idx++)) || true
    local sname
    sname="$(basename "$skill_dir")"
    printf "[%d/%d] Validating %-35s" "$idx" "$total" "$sname..."

    local result
    result="$(py_validate "$skill_dir")"
    local error_count
    error_count="$(echo "$result" | py_error_count)"

    if [[ "$error_count" -gt 0 ]]; then
      printf " ${YELLOW}skipped (validation failed)${RESET}\n"
      ((skipped++)) || true
      skip_reasons+=("$sname: validation failed ($error_count error(s))")
      continue
    fi

    local out_path="$PACKAGES_DIR/${sname}.skill"
    py_package "$skill_dir" "$out_path"
    printf " ${GREEN}✓ packaged${RESET}\n"
    ((packaged++)) || true
  done

  echo
  echo "${BOLD}Summary:${RESET} ${GREEN}${packaged} packaged${RESET}, ${YELLOW}${skipped} skipped${RESET} / ${total} total"
  if [[ ${#skip_reasons[@]} -gt 0 ]]; then
    echo
    echo "${YELLOW}Skipped:${RESET}"
    for r in "${skip_reasons[@]}"; do
      echo "  • $r"
    done
  fi
  echo "${DIM}Output: $PACKAGES_DIR${RESET}"
  echo
}

# ── 3. Validate & package a single skill ─────────────────────────────────────
cmd_single() {
  local target="${1:-}"

  local -a skill_dirs
  mapfile -t skill_dirs < <(discover_skills)

  if [[ ${#skill_dirs[@]} -eq 0 ]]; then
    echo "${YELLOW}No skills found.${RESET}"
    return 0
  fi

  local -a skill_names=()
  for d in "${skill_dirs[@]}"; do
    skill_names+=("$(basename "$d")")
  done

  local chosen_name=""

  # If name was passed as argument, use it directly
  if [[ -n "$target" ]]; then
    for sn in "${skill_names[@]}"; do
      if [[ "$sn" == "$target" ]]; then
        chosen_name="$target"
        break
      fi
    done
    if [[ -z "$chosen_name" ]]; then
      echo "${RED}Skill '$target' not found.${RESET}"
      echo "Available: ${skill_names[*]}"
      return 1
    fi
  fi

  # Interactive selection if no target given
  if [[ -z "$chosen_name" ]]; then
    # Use fzf if available
    if command -v fzf &>/dev/null; then
      chosen_name="$(printf '%s\n' "${skill_names[@]}" | fzf --prompt="Select skill: " --height=40% --border)" || true
    fi

    if [[ -z "$chosen_name" ]]; then
      echo
      echo "${BOLD}Select a skill:${RESET}"
      PS3=$'\nEnter number: '
      select sname in "${skill_names[@]}" "Cancel"; do
        if [[ "$sname" == "Cancel" ]]; then
          return 0
        elif [[ -n "$sname" ]]; then
          chosen_name="$sname"
          break
        fi
      done
    fi
  fi

  [[ -z "$chosen_name" ]] && return 0

  local skill_dir="$SKILLS_ROOT/$chosen_name"
  echo
  echo "${BOLD}${CYAN}Validating '${chosen_name}'...${RESET}"

  local result
  result="$(py_validate "$skill_dir")"
  local error_count
  error_count="$(echo "$result" | py_error_count)"

  if [[ "$error_count" -gt 0 ]]; then
    echo "${RED}Validation FAILED (${error_count} error(s)):${RESET}"
    "$PYTHON" -c "
import json, sys
d = json.loads(sys.stdin.read())
for e in d['errors']:
    print('  •', e)
" <<< "$result"
    echo
    return 1
  fi

  echo "${GREEN}✓ Validation passed${RESET}"
  echo

  ensure_packages_dir
  local out_path="$PACKAGES_DIR/${chosen_name}.skill"
  echo "${BOLD}${CYAN}Packaging '${chosen_name}'...${RESET}"
  py_package "$skill_dir" "$out_path"

  local size
  size="$(du -sh "$out_path" | cut -f1)"
  echo "${GREEN}✓ Packaged:${RESET} $out_path ${DIM}(${size})${RESET}"
  echo
}

# ── 4. Clean packages ─────────────────────────────────────────────────────────
cmd_clean() {
  local count
  count="$(find "$PACKAGES_DIR" -maxdepth 1 -name '*.skill' 2>/dev/null | wc -l | tr -d ' ')"

  if [[ "$count" -eq 0 ]]; then
    echo
    echo "${YELLOW}No packages to clean.${RESET}"
    echo
    return 0
  fi

  # Non-interactive if --yes flag
  if [[ "${FORCE_YES:-}" == "1" ]]; then
    find "$PACKAGES_DIR" -maxdepth 1 -name '*.skill' -delete
    echo "${GREEN}✓ Cleaned ${count} package(s).${RESET}"
    return 0
  fi

  echo
  echo "${YELLOW}This will remove ${count} .skill file(s) from:${RESET}"
  echo "  $PACKAGES_DIR"
  printf "\nContinue? [y/N] "
  read -r confirm
  if [[ "$confirm" =~ ^[Yy]$ ]]; then
    find "$PACKAGES_DIR" -maxdepth 1 -name '*.skill' -delete
    echo "${GREEN}✓ Cleaned ${count} package(s).${RESET}"
  else
    echo "Cancelled."
  fi
  echo
}

# ── 5. List packaged skills ──────────────────────────────────────────────────
cmd_list() {
  ensure_packages_dir
  echo
  echo "${BOLD}${CYAN}Packaged skills in:${RESET} $PACKAGES_DIR"
  echo

  local -a files=()
  while IFS= read -r -d '' f; do
    files+=("$f")
  done < <(find "$PACKAGES_DIR" -maxdepth 1 -name '*.skill' -print0 2>/dev/null | sort -z)

  if [[ ${#files[@]} -eq 0 ]]; then
    echo "${DIM}  (none)${RESET}"
    echo
    return 0
  fi

  printf "  ${BOLD}%-40s %8s  %s${RESET}\n" "Name" "Size" "Modified"
  printf "  %s\n" "$(printf '%.0s─' {1..65})"
  for f in "${files[@]}"; do
    local fname fsize mtime
    fname="$(basename "$f")"
    fsize="$(du -sh "$f" | cut -f1)"
    mtime="$(date -r "$f" '+%Y-%m-%d %H:%M' 2>/dev/null || stat -c '%y' "$f" 2>/dev/null | cut -d. -f1)"
    printf "  %-40s %8s  %s\n" "$fname" "$fsize" "$mtime"
  done
  echo
  echo "${DIM}Total: ${#files[@]} package(s)${RESET}"
  echo
}

# ── Help ──────────────────────────────────────────────────────────────────────
cmd_help() {
  echo
  echo "${BOLD}${CYAN}Claude Skills Manager${RESET}"
  echo
  echo "Usage: $(basename "$0") [command] [args]"
  echo
  echo "Commands:"
  echo "  ${BOLD}validate${RESET}         Validate all skills (exit 1 if any fail)"
  echo "  ${BOLD}package${RESET}          Package all valid skills as .skill archives"
  echo "  ${BOLD}single${RESET} [NAME]    Validate & package a single skill"
  echo "  ${BOLD}clean${RESET}            Remove all .skill packages"
  echo "  ${BOLD}list${RESET}             List packaged .skill files"
  echo "  ${BOLD}help${RESET}             Show this help"
  echo
  echo "Run without arguments for interactive menu."
  echo
}

# ── Main menu ─────────────────────────────────────────────────────────────────
menu() {
  while true; do
    local skill_count
    skill_count="$(discover_skills | wc -l | tr -d ' ')"
    echo
    echo "${BOLD}${CYAN}=== Claude Skills Manager ===${RESET} ${DIM}(${skill_count} skills)${RESET}"
    echo
    echo "  1) Validate all skills"
    echo "  2) Package all skills"
    echo "  3) Validate & package a single skill"
    echo "  4) Clean packages"
    echo "  5) List packaged skills"
    echo "  6) Exit"
    echo
    printf "Choose an option [1-6]: "
    read -r choice

    case "$choice" in
      1) cmd_validate_all || true ;;
      2) cmd_package_all ;;
      3) cmd_single ;;
      4) cmd_clean ;;
      5) cmd_list ;;
      6) echo; echo "Bye."; exit 0 ;;
      *) echo "${YELLOW}Invalid choice. Enter 1–6.${RESET}" ;;
    esac
  done
}

# ── Entry point ───────────────────────────────────────────────────────────────
main() {
  ensure_venv

  case "${1:-}" in
    validate)  cmd_validate_all ;;
    package)   cmd_package_all ;;
    single)    cmd_single "${2:-}" ;;
    clean)     cmd_clean ;;
    list)      cmd_list ;;
    help|--help|-h)
               cmd_help ;;
    "")        menu ;;
    *)         echo "${RED}Unknown command: $1${RESET}"; cmd_help; exit 1 ;;
  esac
}

main "$@"
