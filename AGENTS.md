# AI agent instructions — research workflow skill development

This repository develops the agent-neutral research workflow kit, not a research
project. Four sibling skills live under `skills/`; `tools/` holds shared Python
commands, `scaffold/` the minimal project files, and `templates/` the optional
components added with `add`. `conventions.md` holds shared rules and names the
task skills.

`workflow.py install` registers only `research-setup` centrally. Projects reach
`research-work`, `research-repository`, and `research-manuscript` through their
pinned `.workflow/` snapshot: the AGENTS.md block points only to `conventions.md`, so skills can be
renamed in a release without editing project files. Keep project snapshots
independent of the development checkout unless editable mode was explicitly chosen.

## Bootstrapping a new project

When asked to start a project, follow
[`skills/research-setup/SKILL.md`](skills/research-setup/SKILL.md)
with an empty target directory. That skill is the authoritative setup procedure
for all agents; do not initialize this development checkout as a research project.

## Development rules

- Edit shared skills under `skills/`, tools under `tools/`, and project assets
  under `scaffold/` and `templates/`.
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
python workflow.py init --check
python -m unittest discover -s tests -v
```

For manuscript changes, also run with `TEST_LATEX=1` to exercise actual
LaTeX/BibTeX builds and cleanup. For figure guidance/API changes, run
`tests/smoke-figures.py OUTPUT-DIRECTORY` in an existing environment containing
the plotting stack and system rendering tools.
