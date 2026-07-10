#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/research-workflow-smoke.XXXXXX")"
COPY="$TMP_ROOT/template"
SLUG="smoke-project"
DATE="2030-01-02"

cleanup() {
    rm -rf "$TMP_ROOT"
}
trap cleanup EXIT

mkdir -p "$COPY"
cp -R "$ROOT/." "$COPY"
rm -rf "$COPY/.git" "$COPY/repository/.git" "$COPY/manuscript/.git"

(
    cd "$COPY"
    BOOTSTRAP_DATE="$DATE" ./bootstrap.sh \
        --slug "$SLUG" \
        --title "Bootstrap Smoke Test" \
        --author "Test Author" \
        --desc "End-to-end bootstrap validation" \
        --no-commit
)

[[ ! -e "$COPY/bootstrap.sh" ]]
[[ ! -d "$COPY/bootstrap" ]]
[[ ! -d "$COPY/tests" ]]
[[ ! -e "$COPY/README.md" ]]
[[ ! -e "$COPY/CHANGELOG.md" ]]
[[ -f "$COPY/journal/$DATE.md" ]]
[[ ! -e "$COPY/journal/YYYY-MM-DD.md" ]]
[[ -f "$COPY/bibliography/$SLUG.bib" ]]
[[ ! -e "$COPY/bibliography/project-slug.bib" ]]
[[ -d "$COPY/repository/.git" ]]
[[ -f "$COPY/manuscript/.gitignore" ]]

grep -Fq "# Bootstrap Smoke Test" "$COPY/project.md"
grep -Fq "Test Author" "$COPY/project.md"
if grep -Fiq "bootstrap" "$COPY/AGENTS.md"; then
    printf 'ERROR: bootstrap-specific references remain in AGENTS.md\n' >&2
    exit 1
fi
grep -Fq "Academic Research Workflow version:** 1.1" "$COPY/AGENTS.md"

if command -v rg >/dev/null 2>&1; then
    if rg --no-ignore -n '\{\{[[:space:]]*[A-Z][A-Z0-9_ ]*[[:space:]]*\}\}' "$COPY" \
        -g '!/.git/*' -g '!/manuscript/.git/*' -g '!/repository/.git/*'; then
        printf 'ERROR: template placeholders remain after bootstrap\n' >&2
        exit 1
    fi
fi

printf 'Bootstrap smoke test passed.\n'
