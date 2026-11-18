# AI agent instructions — research workflow skill development

This repository develops the agent-neutral `init-research-workflow` skill.
It is not itself an initialized research project. The skill also distributes the
shared runtime under `assets/workflow/`.

## Repository layout

```text
.
├── skills/init-research-workflow/
│   ├── SKILL.md                    # callable skill instructions
│   ├── agents/openai.yaml          # optional Codex UI metadata
│   ├── scripts/init_project.py     # portable initializer
│   ├── tests/                      # initializer and optional rendering checks
│   ├── assets/template/            # minimal project scaffold
│   └── assets/workflow/            # updateable method and optional templates
├── workflow.py                    # user-facing install/init/adopt entry point
├── README.md                       # development overview
├── CHANGELOG.md                    # workflow release history
└── AGENTS.md                       # shared development guidance
```

The template inside `assets/template/` must be self-contained.
It must not depend on the development repository being present when the skill
is used in an empty directory.

## Bootstrapping a new project

When asked to start a project, follow
[`skills/init-research-workflow/SKILL.md`](skills/init-research-workflow/SKILL.md)
with an empty target directory. That skill is the authoritative setup procedure
for all agents; do not initialize this development checkout as a research project.

## Development rules

- Edit the minimal scaffold under `skills/init-research-workflow/assets/template/`
  and the shared method under `skills/init-research-workflow/assets/workflow/`.
- Create optional project structure only when a current task requires it.
- Updates may replace owned method files, never project science or configuration.
- Keep skill instructions and helper scripts outside the bundled template.
- Keep structural moves reviewable; do not stage or commit without authorization.
- Do not copy development-only files into generated research projects.
- Preserve the template’s private `workspace/`, shared `repository/`,
  authoritative `manuscript/`, bibliography, and journal boundaries.
- Do not commit, push, or publish changes without explicit user approval.

## Validation

Keep `SKILL.md` and project guidance independent of any agent client. Client
metadata may be optional, but must not contain unique workflow instructions.
Use `AGENTS.md` as the single instructions file; do not create client aliases.

Validate setup without requiring scientific or TeX dependencies:

```sh
python skills/init-research-workflow/scripts/init_project.py --check
python -m unittest discover -s skills/init-research-workflow/tests -v
```

For manuscript changes, also run with `TEST_LATEX=1` to exercise actual
LaTeX/BibTeX builds and cleanup. For figure guidance/API changes, run
`tests/smoke-figures.py OUTPUT-DIRECTORY` in an existing environment containing
the plotting stack and system rendering tools.
