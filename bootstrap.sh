#!/usr/bin/env bash
# ============================================================================
# Research project bootstrap — mechanical setup (meant to be called by an AI
# agent, not run interactively).
#
# Usage:
#   ./bootstrap.sh --slug "<slug>" --title "<title>" --author "<name>" \
#                  [--desc "<description>"] [--status "<status>"]
#
# All flags are required except --desc / --status.  See AGENTS.md for the
# agent-facing workflow.
# ============================================================================

set -euo pipefail

# ── 1.  Parse flags ───────────────────────────────────────────────────
PROJECT_SLUG=""
PAPER_TITLE=""
AUTHOR=""
DESCRIPTION=""
STATUS=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --slug)   PROJECT_SLUG="$2";  shift 2 ;;
        --title)  PAPER_TITLE="$2";   shift 2 ;;
        --author) AUTHOR="$2";        shift 2 ;;
        --desc)   DESCRIPTION="$2";   shift 2 ;;
        --status) STATUS="$2";        shift 2 ;;
        *)
            echo "Usage: $0 --slug <slug> --title <title> --author <name> [--desc <desc>] [--status <status>]"
            exit 1
            ;;
    esac
done

# ── 2.  Validate ──────────────────────────────────────────────────────
missing=()
[[ -z "$PROJECT_SLUG" ]] && missing+=("--slug")
[[ -z "$PAPER_TITLE" ]]  && missing+=("--title")
[[ -z "$AUTHOR" ]]       && missing+=("--author")

if [[ ${#missing[@]} -gt 0 ]]; then
    echo "ERROR: required fields missing: ${missing[*]}" >&2
    exit 1
fi

[[ -z "$DESCRIPTION" ]] && DESCRIPTION="$PAPER_TITLE"

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
DATE_ISO="$(date +%Y-%m-%d)"

# ── 3.  Deploy bootstrap files ────────────────────────────────────────
cp bootstrap/manuscript.gitignore   manuscript/.gitignore
cp bootstrap/repository.gitignore   repository/.gitignore
sed -i "s|{{ PROJECT_SLUG }}|$PROJECT_SLUG|g" manuscript/.gitignore

# ── 4.  Replace placeholders ──────────────────────────────────────────
cd "$REPO_ROOT"

echo "  Replacing placeholders …"

sed -i "s|{{ PROJECT_TITLE }}|$PAPER_TITLE|g"    project.md
sed -i "s|{{ DESCRIPTION }}|$DESCRIPTION|g"     project.md
sed -i "s|{{ AUTHORS }}|$AUTHOR|g"              project.md
sed -i "s|{{ STATUS }}|$STATUS|g"               project.md

mv journal/YYYY-MM-DD.md "journal/$DATE_ISO.md"
sed -i "s|{{ PROJECT_TITLE }}|$PAPER_TITLE|g"   "journal/$DATE_ISO.md"
sed -i "s|{{ DATE_ISO }}|$DATE_ISO|g"           "journal/$DATE_ISO.md"

sed -i "s|{{ DATE_ISO }}|$DATE_ISO|g"           notation_helper.md

sed -i "s|{{ PAPER_TITLE }}|$PAPER_TITLE|g"     repository/README.md

sed -i "s|{{ AUTHOR }}|$AUTHOR|g"               repository/pixi.toml
sed -i "s|{{ PROJECT_SLUG }}|$PROJECT_SLUG|g"   repository/pixi.toml

# ── 5.  Clean up ──────────────────────────────────────────────────────
echo "  Cleaning up …"

rm -f bootstrap.sh
rm -rf bootstrap/
rm -f workspace/.gitkeep manuscript/.gitkeep repository/.gitkeep bibliography/.gitkeep

# ── 6.  Initialise git ────────────────────────────────────────────────
echo "  Initialising git …"

git init
git add -A
git commit -m "Initialise $PROJECT_SLUG project"



# ── 7.  Done ──────────────────────────────────────────────────────────
echo ""
echo "  Done!  $PROJECT_SLUG is ready."
echo ""
echo "  Next steps:"
echo "    - Edit project.md with your full description."
echo "    - Link manuscript/ to your Overleaf git remote."
echo "    - Start exploring in workspace/."
echo "    - When calculations stabilise, promote code to repository/."
echo ""
