# Academic Research Workflow

**Current version:** 1.1

This template organizes an academic paper around three distinct working areas:

- `workspace/` for private exploration, derivations, draft code, and evidence;
- `repository/` for finalized, reproducible code that can ship with the paper;
- `manuscript/` for the authoritative LaTeX manuscript, normally connected to
  Overleaf.

The workflow keeps tentative results private until they are verified and the
author explicitly promotes them into the public reproducibility repository.
See [AGENTS.md](AGENTS.md) for the complete working rules and
[CHANGELOG.md](CHANGELOG.md) for workflow-version history.

## Start a project

Ask your AI coding agent to “start a new project” and provide the requested
project details. The agent will run the bootstrap script for you. To run it
directly instead:

```sh
./bootstrap.sh \
    --slug "project-slug" \
    --title "Paper title" \
    --author "Author name" \
    --desc "Short project description"
```

Add `--overleaf-url "<url-or-project-id>"` when an Overleaf project already
exists. Run `./bootstrap.sh --check` to validate the untouched template, or
`./tests/smoke-bootstrap.sh` to exercise the full bootstrap in a temporary copy.

Bootstrap replaces the template placeholders, initializes `repository/` and
`manuscript/` as separate Git repositories, and removes bootstrap-only material.
When no Overleaf URL is supplied, the local manuscript repository is ready to
receive an Overleaf remote later. Bootstrap never promotes exploratory work from
`workspace/` into `repository/`.

The generated manuscript repository includes a pinned `tex-fmt` pre-commit
configuration. From `manuscript/`, run `just install-hooks` once per clone,
`just format` to format tracked LaTeX sources, or `just format-check` to check them.
