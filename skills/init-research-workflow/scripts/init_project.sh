#!/usr/bin/env bash

set -euo pipefail

usage() {
    printf 'Usage: %s TARGET-DIRECTORY [bootstrap options...]\n' "$0" >&2
    exit 2
}

[[ $# -ge 1 ]] || usage

target_dir="$1"
shift
[[ "$target_dir" = /* ]] || target_dir="$(pwd)/$target_dir"
target_dir="$(cd "$target_dir" 2>/dev/null && pwd)"

if find "$target_dir" -mindepth 1 -maxdepth 1 -print -quit | grep -q .; then
    printf 'ERROR: target directory is not empty: %s\n' "$target_dir" >&2
    exit 1
fi

skill_root="$(cd "$(dirname "$0")/.." && pwd)"
template_dir="$skill_root/assets/template"

cp -a "$template_dir"/. "$target_dir"/
mkdir -p "$target_dir/bibliography"
rm -f "$target_dir/bibliography/.gitkeep"

(
    cd "$target_dir"
    bash ./bootstrap.sh --check
    bash ./bootstrap.sh "$@"
)
