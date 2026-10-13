# Research Workflow Skill

**Version: 2.0.0** — see [CHANGELOG.md](CHANGELOG.md) for changes and migration notes.

This repository develops the agent-neutral `init-research-workflow` skill and its
bundled academic research project template.

The canonical skill is in
[`skills/init-research-workflow/`](skills/init-research-workflow/).
Its portable template is in
[`skills/init-research-workflow/assets/template/`](skills/init-research-workflow/assets/template/).

Use the skill from an empty target directory to collect project details, copy
the bundled template, and initialize the project with nested manuscript and
repository Git boundaries.

Development checks:

```sh
python skills/init-research-workflow/scripts/init_project.py --check
python -m unittest discover -s skills/init-research-workflow/tests -v
# Optional real manuscript builds (requires Just and TeX):
TEST_LATEX=1 python -m unittest discover -s skills/init-research-workflow/tests -v
# Requires the plotting stack and system tools already installed:
python skills/init-research-workflow/tests/smoke-figures.py /tmp/research-figures
```

Setup requires only Python 3.11+ and Git. The initializer lives outside the
template, which contains only generated-project files. The shell entry point
is retained as a compatibility wrapper.

The template snapshot is the source of truth for generated projects.
Keep skill-development files outside `assets/template/`.

## Bootstrapping a new project

The same `SKILL.md`, scripts, and template can be used by Codex, Claude Code,
or another agent with filesystem and shell access. Point the agent at
[`skills/init-research-workflow/SKILL.md`](skills/init-research-workflow/SKILL.md)
from an empty target directory. If the
client supports skill discovery, install or link the complete skill folder in
that client's configured skill directory; follow its installation conventions.
There is no client-specific invocation required by the workflow itself.

For a standalone installation, copy the entire `skills/init-research-workflow/`
folder, including `assets/` and `scripts/`. The initializer resolves these paths
relative to itself rather than to this development checkout.

`AGENTS.md` is the single project-instruction file. Explicitly ask an agent to
read it if its client does not load it automatically; no `CLAUDE.md` alias is
needed. When switching agents for a cross-check, point the reviewer to the same
project context, latest journal entry, and relevant evidence. Record what was
independently checked and any unresolved disagreement in the journal.

`agents/openai.yaml` is optional Codex UI metadata. Other clients can ignore it;
it adds no workflow rules or runtime dependencies. Client-specific validators
may be run when available, in addition to the portable checks above.
