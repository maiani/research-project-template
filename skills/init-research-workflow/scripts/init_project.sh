#!/usr/bin/env bash
# Compatibility entry point; all initialization logic lives in Python.
set -euo pipefail
exec "$(command -v python3 || command -v python)" "$(dirname "$0")/init_project.py" "$@"
