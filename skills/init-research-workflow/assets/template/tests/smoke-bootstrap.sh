#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/research-workflow-smoke.XXXXXX")"
# Exercise the path quoting needed for Windows checkouts under directories such
# as "C:/Users/First Last/Documents".
COPY="$TMP_ROOT/template with spaces"
SLUG="smoke-project"
DATE="2030-01-02"

cleanup() {
    rm -rf "$TMP_ROOT"
}
trap cleanup EXIT

mkdir -p "$COPY"
cp -R "$ROOT/." "$COPY"
rm -rf "$COPY/repository/.git" "$COPY/manuscript/.git"

if (
    cd "$COPY"
    BOOTSTRAP_DATE="$DATE" ./bootstrap.sh \
        --slug '../escaped' \
        --title "Rejected slug" \
        --author "Test Author" \
        --no-commit \
        --force
); then
    printf 'ERROR: bootstrap accepted a path-traversal project slug\n' >&2
    exit 1
fi
[[ ! -e "$COPY/escaped.bib" ]]

(
    cd "$COPY"
    GIT_AUTHOR_NAME="Bootstrap Test" \
    GIT_AUTHOR_EMAIL="bootstrap@example.invalid" \
    GIT_COMMITTER_NAME="Bootstrap Test" \
    GIT_COMMITTER_EMAIL="bootstrap@example.invalid" \
    BOOTSTRAP_DATE="$DATE" ./bootstrap.sh \
        --slug "$SLUG" \
        --title "Bootstrap Smoke Test" \
        --author "Test Author" \
        --desc "End-to-end bootstrap validation" \
        --force
)

[[ ! -e "$COPY/bootstrap.sh" ]]
[[ ! -d "$COPY/bootstrap" ]]
[[ ! -d "$COPY/tests" ]]
[[ ! -d "$COPY/skills" ]]
[[ ! -e "$COPY/README.md" ]]
[[ ! -e "$COPY/CHANGELOG.md" ]]
[[ -f "$COPY/journal/$DATE.md" ]]
[[ ! -e "$COPY/journal/YYYY-MM-DD.md" ]]
[[ -f "$COPY/bibliography/$SLUG.bib" ]]
grep -Fq '% Project bibliography.' "$COPY/bibliography/$SLUG.bib"
[[ -d "$COPY/workspace/scratch" ]]
git -C "$COPY" ls-files --error-unmatch workspace/scratch/.gitkeep >/dev/null
[[ -d "$COPY/repository/.git" ]]
[[ -d "$COPY/manuscript/.git" ]]
if git -C "$COPY" remote get-url origin >/dev/null 2>&1; then
    printf 'ERROR: inherited template remote remains after bootstrap\n' >&2
    exit 1
fi
[[ -f "$COPY/manuscript/.gitignore" ]]
[[ -f "$COPY/manuscript/.gitattributes" ]]
[[ -d "$COPY/manuscript/outreach" ]]
[[ -f "$COPY/manuscript/.pre-commit-config.yaml" ]]
[[ -f "$COPY/manuscript/badness.toml" ]]
grep -Fq 'repo: https://github.com/jolars/badness-pre-commit' "$COPY/manuscript/.pre-commit-config.yaml"
grep -Fq 'wrap = "semantic"' "$COPY/manuscript/badness.toml"
grep -Fq 'line-width = 100' "$COPY/manuscript/badness.toml"
grep -Fq 'badness-format' "$COPY/manuscript/.pre-commit-config.yaml"
grep -Fq 'format-check:' "$COPY/manuscript/justfile"
grep -Fq 'platforms = ["linux-64", "osx-64", "osx-arm64", "win-64"]' "$COPY/repository/pixi.toml"
[[ "$(git -C "$COPY/manuscript" check-attr eol -- justfile)" == "justfile: eol: lf" ]]

git -C "$COPY/repository" rev-parse --verify HEAD >/dev/null
git -C "$COPY/manuscript" rev-parse --verify HEAD >/dev/null
nested_tracked="$(git -C "$COPY" ls-files repository manuscript)"
if [[ -n "$nested_tracked" ]]; then
    printf 'ERROR: nested repositories are tracked by the root repository:\n%s\n' \
        "$nested_tracked" >&2
    exit 1
fi

grep -Fq "# Bootstrap Smoke Test" "$COPY/project.md"
grep -Fq "Test Author" "$COPY/project.md"
if grep -Fiq "bootstrap" "$COPY/AGENTS.md"; then
    printf 'ERROR: bootstrap-specific references remain in AGENTS.md\n' >&2
    exit 1
fi
grep -Fq "Academic Research Workflow version:** 1.3" "$COPY/AGENTS.md"
grep -Fq 'Private, personal exploration:' "$COPY/AGENTS.md"
grep -Fq 'Shared/public artifact:' "$COPY/AGENTS.md"
grep -Fq 'public documentation' "$COPY/repository/README.md"

if command -v rg >/dev/null 2>&1; then
    if rg --no-ignore -n '\{\{[[:space:]]*[A-Z][A-Z0-9_ ]*[[:space:]]*\}\}' "$COPY" \
        -g '!/.git/*' -g '!/manuscript/.git/*' -g '!/repository/.git/*'; then
        printf 'ERROR: template placeholders remain after bootstrap\n' >&2
        exit 1
    fi
fi

printf 'Bootstrap smoke test passed.\n'
