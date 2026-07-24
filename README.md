# Academic Research Workflow

**Current version:** 1.2

This template organizes an academic paper around three working areas:

- `workspace/` for private, personal exploration, derivations, draft code, and
  evidence;
- `repository/` for finalized reproducible code, public documentation, and
  accompanying material shared with collaborators or released with the paper;
- `manuscript/` for the authoritative LaTeX manuscript, normally connected to
  Overleaf.

Personal work stays private until the author promotes it.
See [AGENTS.md](AGENTS.md) for the authoritative folder boundaries, promotion
rules, and research workflow, and [CHANGELOG.md](CHANGELOG.md) for version
history.

## Start a project

Bootstrap requires these tools on `PATH`: Git, Python 3, `just`, `latexmk`,
`pdflatex`, BibTeX, and `latexdiff`.
Python may be installed as either `python3` or `python`.
Formatting is optional: install `tex-fmt` for `just format` and
`just format-check`, and install `pre-commit` only if you want
`just install-hooks`.

Linux, macOS, and Windows are supported. On Windows, run the commands below
from Git Bash (installed with Git for Windows) and install the required tools
above on `PATH`.
Invoke scripts with `bash`, not a system's generic `sh`.
Generated Pixi workspaces target `linux-64`, Intel and Apple Silicon macOS, and
`win-64`; executable shell inputs stay on LF line endings for Git Bash.

Ask your AI coding agent to “start a new project” and provide the requested
project details. The agent will run the bootstrap script for you. To run it
directly instead:

```sh
bash ./bootstrap.sh \
    --slug "project-slug" \
    --title "Paper title" \
    --author "Author name" \
    --desc "Short project description"
```

Add `--overleaf-url "<url-or-project-id>"` when an Overleaf project already
exists. Run `bash ./bootstrap.sh --check` to validate the untouched template,
or `bash ./tests/smoke-bootstrap.sh` to exercise the full bootstrap in a
temporary copy.

Bootstrap replaces the template placeholders, initializes `repository/` and
`manuscript/` as separate Git repositories, and removes bootstrap-only material.
When no Overleaf URL is supplied, the local manuscript repository is ready to
receive an Overleaf remote later.
Bootstrap never promotes private personal work from `workspace/` into
`repository/`.
