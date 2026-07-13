#!/usr/bin/env bash
# ============================================================================
# Research project bootstrap -- mechanical setup (meant to be called by an AI
# agent, not run interactively).
#
# Usage:
#   ./bootstrap.sh --slug "<slug>" --title "<title>" --author "<name>" \
#                  [--desc "<description>"] [--status "<status>"] \
#                  [--overleaf-url "<url-or-project-id>"] [--no-commit] [--force]
#   ./bootstrap.sh --check
#
# All flags are required except --desc / --status / --overleaf-url. See
# AGENTS.md for the agent-facing workflow.
# ============================================================================

set -euo pipefail

usage() {
    cat >&2 <<'EOF'
Usage: ./bootstrap.sh --slug <slug> --title <title> --author <name> [options]

Required:
  --slug <slug>                Project directory/package slug
  --title <title>              Paper title
  --author <name>              Author name(s)

Optional:
  --desc <description>         Short project description (defaults to title)
  --status <status>            Initial status (defaults to "Initial setup.")
  --overleaf-url <url-or-id>   Overleaf project URL or project id for manuscript/
  --no-commit                  Apply bootstrap mutations but do not commit
  --force                      Allow running with a dirty git worktree
  --check                      Validate the template without modifying it
  -h, --help                   Show this help
EOF
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

info() {
    printf '  %s\n' "$*"
}

require_value() {
    local flag="$1"
    local value="${2-}"
    [[ -n "$value" ]] || die "$flag requires a value"
}

# -- 1. Parse flags -----------------------------------------------------------
PROJECT_SLUG=""
PAPER_TITLE=""
AUTHOR=""
DESCRIPTION=""
STATUS="Initial setup."
OVERLEAF_INPUT=""
NO_COMMIT=0
FORCE=0
CHECK=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --slug)         require_value "$1" "${2-}"; PROJECT_SLUG="$2"; shift 2 ;;
        --title)        require_value "$1" "${2-}"; PAPER_TITLE="$2";  shift 2 ;;
        --author)       require_value "$1" "${2-}"; AUTHOR="$2";       shift 2 ;;
        --desc)         require_value "$1" "${2-}"; DESCRIPTION="$2";  shift 2 ;;
        --status)       require_value "$1" "${2-}"; STATUS="$2";       shift 2 ;;
        --overleaf-url) require_value "$1" "${2-}"; OVERLEAF_INPUT="$2"; shift 2 ;;
        --no-commit)    NO_COMMIT=1; shift ;;
        --force)        FORCE=1; shift ;;
        --check)        CHECK=1; shift ;;
        -h|--help)      usage; exit 0 ;;
        *)              usage; die "unknown argument: $1" ;;
    esac
done

if [[ "$CHECK" -eq 0 ]]; then
    missing=()
    [[ -z "$PROJECT_SLUG" ]] && missing+=("--slug")
    [[ -z "$PAPER_TITLE" ]]  && missing+=("--title")
    [[ -z "$AUTHOR" ]]       && missing+=("--author")
    [[ ${#missing[@]} -eq 0 ]] || die "required fields missing: ${missing[*]}"
fi

[[ -z "$DESCRIPTION" ]] && DESCRIPTION="$PAPER_TITLE"

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
DATE_ISO="${BOOTSTRAP_DATE:-$(date +%Y-%m-%d)}"
JOURNAL_TEMPLATE="$REPO_ROOT/journal/YYYY-MM-DD.md"
JOURNAL_TARGET="$REPO_ROOT/journal/$DATE_ISO.md"
BIB_TEMPLATE="$REPO_ROOT/bibliography/project-slug.bib"
BIB_TARGET="$REPO_ROOT/bibliography/$PROJECT_SLUG.bib"

in_git_work_tree() {
    git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1
}

git_worktree_dirty() {
    ! git -C "$REPO_ROOT" diff --quiet \
        || ! git -C "$REPO_ROOT" diff --cached --quiet \
        || [[ -n "$(git -C "$REPO_ROOT" ls-files --others --exclude-standard)" ]]
}

require_file() {
    local path="$1"
    [[ -f "$path" ]] || die "required file is missing: ${path#$REPO_ROOT/}"
}

require_dir() {
    local path="$1"
    [[ -d "$path" ]] || die "required directory is missing: ${path#$REPO_ROOT/}"
}

require_bibliography_seed() {
    [[ -f "$BIB_TEMPLATE" || -f "$BIB_TARGET" ]] \
        || die "neither bibliography/project-slug.bib nor bibliography/${PROJECT_SLUG}.bib exists"
}

require_placeholder() {
    local path="$1"
    local placeholder="$2"
    [[ -f "$path" ]] || die "cannot check missing file: ${path#$REPO_ROOT/}"
    grep -Fq "$placeholder" "$path" || die "missing placeholder $placeholder in ${path#$REPO_ROOT/}"
}

replace_placeholder() {
    local path="$1"
    local placeholder="$2"
    local value="$3"
    [[ -f "$path" ]] || die "cannot replace in missing file: ${path#$REPO_ROOT/}"
    python3 - "$path" "$placeholder" "$value" <<'PY'
from pathlib import Path
import os
import sys
import tempfile

path = Path(sys.argv[1])
placeholder = sys.argv[2]
value = sys.argv[3]

text = path.read_text(encoding="utf-8")
updated = text.replace(placeholder, value)
if updated == text:
    sys.exit(0)

fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
try:
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
        handle.write(updated)
    os.replace(tmp_name, path)
finally:
    if os.path.exists(tmp_name):
        os.unlink(tmp_name)
PY
}

normalize_overleaf_remote() {
    python3 - "$1" <<'PY'
import re
import sys

raw = sys.argv[1].strip()
if not raw:
    sys.exit("missing Overleaf project URL or id")

if raw.startswith("git@git.overleaf.com:"):
    print(raw)
    raise SystemExit

git_url = re.match(r"^https://git\.overleaf\.com/([0-9A-Za-z]+)(?:/?|\.git)$", raw)
if git_url:
    print(f"https://git.overleaf.com/{git_url.group(1)}")
    raise SystemExit

project = re.search(r"overleaf\.com/(?:project/)?([0-9A-Za-z]{8,})", raw)
if project:
    print(f"https://git.overleaf.com/{project.group(1)}")
    raise SystemExit

bare = re.fullmatch(r"[0-9A-Za-z]{8,}", raw)
if bare:
    print(f"https://git.overleaf.com/{raw}")
    raise SystemExit

sys.exit(f"could not extract an Overleaf project id from: {raw}")
PY
}

placeholder_audit() {
    local matches
    if command -v rg >/dev/null 2>&1; then
        matches="$(rg --no-ignore -n '\{\{[[:space:]]*[A-Z][A-Z0-9_ ]*[[:space:]]*\}\}' "$REPO_ROOT" -g '!/.git/*' -g '!/manuscript/.git/*' -g '!/repository/.git/*' || true)"
    else
        matches="$(grep -RInE '\{\{[[:space:]]*[A-Z][A-Z0-9_ ]*[[:space:]]*\}\}' "$REPO_ROOT" --exclude-dir=.git || true)"
    fi
    [[ -z "$matches" ]] || die "template placeholders remain after bootstrap:
$matches"
}

check_template() {
    require_file "$REPO_ROOT/README.md"
    require_file "$REPO_ROOT/CHANGELOG.md"
    require_file "$REPO_ROOT/tests/smoke-bootstrap.sh"
    require_placeholder "$REPO_ROOT/project.md" "{{ PROJECT_TITLE }}"
    require_placeholder "$REPO_ROOT/project.md" "{{ DESCRIPTION }}"
    require_placeholder "$REPO_ROOT/project.md" "{{ AUTHORS }}"
    require_placeholder "$REPO_ROOT/project.md" "{{ STATUS }}"
    require_placeholder "$REPO_ROOT/journal/YYYY-MM-DD.md" "{{ PROJECT_TITLE }}"
    require_placeholder "$REPO_ROOT/journal/YYYY-MM-DD.md" "{{ DATE_ISO }}"
    require_placeholder "$REPO_ROOT/repository/README.md" "{{ PAPER_TITLE }}"
    require_placeholder "$REPO_ROOT/repository/pixi.toml" "{{ AUTHOR }}"
    require_placeholder "$REPO_ROOT/repository/pixi.toml" "{{ PROJECT_SLUG }}"
    require_placeholder "$REPO_ROOT/manuscript/justfile" "{{ PROJECT_SLUG }}"
    require_file "$REPO_ROOT/manuscript/.pre-commit-config.yaml"
    require_file "$REPO_ROOT/manuscript/tex-fmt.toml"
    require_placeholder "$REPO_ROOT/bootstrap/manuscript.gitignore" "{{ PROJECT_SLUG }}"
    require_file "$BIB_TEMPLATE"
    grep -Fq "## Bootstrapping a new project" "$REPO_ROOT/AGENTS.md" \
        || die "AGENTS.md is missing the bootstrap instruction section"
    grep -Fq "Academic Research Workflow version:** 1.1" "$REPO_ROOT/AGENTS.md" \
        || die "AGENTS.md is missing the workflow version"
    bash -n "$REPO_ROOT/bootstrap.sh"
    bash -n "$REPO_ROOT/tests/smoke-bootstrap.sh"
    info "template check passed."
}

preflight() {
    command -v git >/dev/null 2>&1 || die "git is required"
    command -v python3 >/dev/null 2>&1 || die "python3 is required for safe placeholder replacement"

    require_dir "$REPO_ROOT/manuscript"
    require_dir "$REPO_ROOT/manuscript/svg"
    require_dir "$REPO_ROOT/repository"
    require_dir "$REPO_ROOT/workspace"
    require_dir "$REPO_ROOT/bibliography"
    require_dir "$REPO_ROOT/journal"

    require_file "$REPO_ROOT/project.md"
    require_bibliography_seed
    require_file "$REPO_ROOT/repository/README.md"
    require_file "$REPO_ROOT/repository/pixi.toml"
    require_file "$REPO_ROOT/manuscript/justfile"
    require_file "$REPO_ROOT/manuscript/.pre-commit-config.yaml"
    require_file "$REPO_ROOT/manuscript/tex-fmt.toml"

    if [[ -d "$REPO_ROOT/bootstrap" ]]; then
        require_file "$REPO_ROOT/bootstrap/manuscript.gitignore"
        require_file "$REPO_ROOT/bootstrap/repository.gitignore"
    else
        require_file "$REPO_ROOT/manuscript/.gitignore"
        require_file "$REPO_ROOT/repository/.gitignore"
        info "bootstrap/ is already absent; treating cleanup as already done."
    fi

    if [[ -f "$JOURNAL_TEMPLATE" && -f "$JOURNAL_TARGET" && "$JOURNAL_TEMPLATE" != "$JOURNAL_TARGET" ]]; then
        die "both journal/YYYY-MM-DD.md and journal/$DATE_ISO.md exist; remove one before bootstrapping"
    fi
    if [[ ! -f "$JOURNAL_TEMPLATE" && ! -f "$JOURNAL_TARGET" ]]; then
        die "neither journal/YYYY-MM-DD.md nor journal/$DATE_ISO.md exists"
    fi

    if in_git_work_tree && git_worktree_dirty && [[ "$CHECK" -eq 0 && "$FORCE" -eq 0 && "$NO_COMMIT" -eq 0 ]]; then
        die "git worktree is dirty before bootstrap; commit/stash changes, or use --force or --no-commit"
    fi
}

deploy_gitignores() {
    if [[ -d "$REPO_ROOT/bootstrap" ]]; then
        if [[ ! -f "$REPO_ROOT/manuscript/.gitignore" ]]; then
            cp "$REPO_ROOT/bootstrap/manuscript.gitignore" "$REPO_ROOT/manuscript/.gitignore"
        fi
        if [[ ! -f "$REPO_ROOT/repository/.gitignore" ]]; then
            cp "$REPO_ROOT/bootstrap/repository.gitignore" "$REPO_ROOT/repository/.gitignore"
        fi
    fi

    replace_placeholder "$REPO_ROOT/manuscript/.gitignore" "{{ PROJECT_SLUG }}" "$PROJECT_SLUG"
}

move_journal_template() {
    if [[ -f "$JOURNAL_TEMPLATE" && "$JOURNAL_TEMPLATE" != "$JOURNAL_TARGET" ]]; then
        mv "$JOURNAL_TEMPLATE" "$JOURNAL_TARGET"
    else
        info "journal/$DATE_ISO.md already exists; leaving it in place."
    fi
}

move_bibliography_template() {
    if [[ -f "$BIB_TEMPLATE" && "$BIB_TEMPLATE" != "$BIB_TARGET" ]]; then
        [[ ! -e "$BIB_TARGET" ]] || die "bibliography/${PROJECT_SLUG}.bib already exists"
        mv "$BIB_TEMPLATE" "$BIB_TARGET"
    elif [[ -f "$BIB_TARGET" ]]; then
        info "bibliography/${PROJECT_SLUG}.bib already exists; leaving it in place."
    else
        die "neither bibliography/project-slug.bib nor bibliography/${PROJECT_SLUG}.bib exists"
    fi
}

cleanup_bootstrap_assets() {
    rm -rf "$REPO_ROOT/bootstrap"
    rm -rf "$REPO_ROOT/tests"
    rm -f "$REPO_ROOT/README.md" \
          "$REPO_ROOT/CHANGELOG.md" \
          "$REPO_ROOT/bootstrap.sh"
    rm -f "$REPO_ROOT/workspace/.gitkeep" \
          "$REPO_ROOT/manuscript/.gitkeep" \
          "$REPO_ROOT/repository/.gitkeep"
}

remove_bootstrap_instructions() {
    python3 - "$REPO_ROOT/AGENTS.md" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
marker = "\n## Bootstrapping a new project\n"
if marker not in text:
    raise SystemExit("AGENTS.md is missing the bootstrap instruction section")

before, _, _ = text.partition(marker)
path.write_text(before.rstrip() + "\n", encoding="utf-8")
PY
}

initialise_public_repository() {
    local repo_top

    info "initialising public code repository..."
    repo_top="$(git -C "$REPO_ROOT/repository" rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ "$repo_top" != "$REPO_ROOT/repository" ]]; then
        git -C "$REPO_ROOT/repository" init -b main
    fi

    if [[ "$NO_COMMIT" -eq 1 ]]; then
        info "--no-commit supplied; leaving repository/ uncommitted."
        return
    fi

    git -C "$REPO_ROOT/repository" add -A
    if git -C "$REPO_ROOT/repository" diff --cached --quiet; then
        info "no repository/ git changes to commit."
        return
    fi
    git -C "$REPO_ROOT/repository" commit -m "Initialise reproducibility repository"
}

initialise_local_manuscript_repository() {
    local repo_top

    info "initialising local manuscript repository..."
    repo_top="$(git -C "$REPO_ROOT/manuscript" rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ "$repo_top" != "$REPO_ROOT/manuscript" ]]; then
        git -C "$REPO_ROOT/manuscript" init -b main
    fi

    if [[ "$NO_COMMIT" -eq 1 ]]; then
        info "--no-commit supplied; leaving manuscript/ uncommitted."
        return
    fi

    git -C "$REPO_ROOT/manuscript" add -A
    if git -C "$REPO_ROOT/manuscript" diff --cached --quiet; then
        info "no manuscript/ git changes to commit."
        return
    fi
    git -C "$REPO_ROOT/manuscript" commit -m "Initialise manuscript repository"
}

drop_root_index_for_nested_repos() {
    in_git_work_tree || return 0
    git -C "$REPO_ROOT" rm -r --cached --ignore-unmatch repository >/dev/null 2>&1 || true
    git -C "$REPO_ROOT" rm -r --cached --ignore-unmatch manuscript >/dev/null 2>&1 || true
}

commit_changes() {
    if [[ "$NO_COMMIT" -eq 1 ]]; then
        info "--no-commit supplied; leaving changes uncommitted."
        return
    fi

    if ! in_git_work_tree; then
        info "initialising root git repository..."
        git -C "$REPO_ROOT" init
    else
        info "root git repository already initialised."
    fi

    git -C "$REPO_ROOT" add -A
    if git -C "$REPO_ROOT" diff --cached --quiet; then
        info "no root git changes to commit."
        return
    fi
    git -C "$REPO_ROOT" commit -m "Initialise $PROJECT_SLUG project"
}

connect_overleaf() {
    [[ -n "$OVERLEAF_INPUT" ]] || return 0

    local remote template_dir clone_dir template_file
    remote="$(normalize_overleaf_remote "$OVERLEAF_INPUT")"
    info "cloning Overleaf remote into manuscript/: $remote"

    template_dir="$(mktemp -d "${TMPDIR:-/tmp}/research-template-manuscript.XXXXXX")"
    clone_dir="$(mktemp -d "${TMPDIR:-/tmp}/overleaf-manuscript.XXXXXX")"

    for template_file in justfile .gitignore .pre-commit-config.yaml tex-fmt.toml; do
        if [[ -f "$REPO_ROOT/manuscript/$template_file" ]]; then
            cp "$REPO_ROOT/manuscript/$template_file" "$template_dir/$template_file"
        fi
    done

    git clone "$remote" "$clone_dir"
    rm -rf "$REPO_ROOT/manuscript"
    mv "$clone_dir" "$REPO_ROOT/manuscript"

    for template_file in justfile .gitignore .pre-commit-config.yaml tex-fmt.toml; do
        if [[ -f "$template_dir/$template_file" && ! -f "$REPO_ROOT/manuscript/$template_file" ]]; then
            cp "$template_dir/$template_file" "$REPO_ROOT/manuscript/$template_file"
        fi
    done
    mkdir -p "$REPO_ROOT/manuscript/svg"

    rm -rf "$template_dir"
}

initialise_manuscript_repository() {
    if [[ -n "$OVERLEAF_INPUT" ]]; then
        connect_overleaf
    else
        initialise_local_manuscript_repository
    fi
}

# -- 2. Preflight before any mutations ---------------------------------------
preflight
if [[ "$CHECK" -eq 1 ]]; then
    check_template
    exit 0
fi

# -- 3. Deploy bootstrap files ------------------------------------------------
info "deploying bootstrap files..."
deploy_gitignores
mkdir -p "$REPO_ROOT/manuscript/svg"
mkdir -p "$REPO_ROOT/repository/analytics" \
         "$REPO_ROOT/repository/plots/figures"
: > "$REPO_ROOT/repository/analytics/.gitkeep"
: > "$REPO_ROOT/repository/plots/.gitkeep"

# -- 4. Replace placeholders --------------------------------------------------
info "replacing placeholders..."
replace_placeholder "$REPO_ROOT/project.md" "{{ PROJECT_TITLE }}" "$PAPER_TITLE"
replace_placeholder "$REPO_ROOT/project.md" "{{ DESCRIPTION }}" "$DESCRIPTION"
replace_placeholder "$REPO_ROOT/project.md" "{{ AUTHORS }}" "$AUTHOR"
replace_placeholder "$REPO_ROOT/project.md" "{{ STATUS }}" "$STATUS"

move_journal_template
move_bibliography_template
replace_placeholder "$JOURNAL_TARGET" "{{ PROJECT_TITLE }}" "$PAPER_TITLE"
replace_placeholder "$JOURNAL_TARGET" "{{ DATE_ISO }}" "$DATE_ISO"

replace_placeholder "$REPO_ROOT/repository/README.md" "{{ PAPER_TITLE }}" "$PAPER_TITLE"
replace_placeholder "$REPO_ROOT/repository/pixi.toml" "{{ AUTHOR }}" "$AUTHOR"
replace_placeholder "$REPO_ROOT/repository/pixi.toml" "{{ PROJECT_SLUG }}" "$PROJECT_SLUG"
replace_placeholder "$REPO_ROOT/manuscript/justfile" "{{ PROJECT_SLUG }}" "$PROJECT_SLUG"

# -- 5. Clean up and audit ----------------------------------------------------
info "cleaning up bootstrap assets..."
remove_bootstrap_instructions
cleanup_bootstrap_assets

info "auditing unresolved template placeholders..."
placeholder_audit

# -- 6. Initialise nested repos and commit the root ---------------------------
initialise_public_repository
initialise_manuscript_repository
drop_root_index_for_nested_repos
commit_changes

# -- 7. Done -----------------------------------------------------------------
printf '\n'
info "Done! $PROJECT_SLUG is ready."
printf '\n'
info "Next steps:"
printf '    - Edit project.md with your full description.\n'
printf '    - Add an Overleaf remote to manuscript/ if one is not already connected.\n'
printf '    - Start exploring in workspace/.\n'
printf '    - When calculations stabilise, promote code to repository/.\n'
printf '\n'
