# AI agent instructions — research workflow skill development

This repository develops the agent-neutral research workflow kit, not a research
project. Five sibling skills live under `skills/`; `tools/` holds the kit's own
Python commands, and `templates/` the files they copy into projects: `project/`
for `init` and the optional components added with `add`. `conventions.md` holds
shared rules and names the task skills.

`workflow.py install` registers two skills centrally: `research-setup`, and
`manuscript-preflight`, which also works outside workflow projects. Projects reach
`research-work`, `research-repository`, `research-manuscript`, and
`manuscript-preflight` through their pinned `.workflow/` snapshot: the AGENTS.md
block points only to `conventions.md`, so skills can be renamed in a release
without editing project files. Keep project snapshots independent of the
development checkout unless editable mode was explicitly chosen.

## Bootstrapping a new project

When asked to start a project, follow
[`skills/research-setup/SKILL.md`](skills/research-setup/SKILL.md)
with an empty target directory. That skill is the authoritative setup procedure
for all agents; do not initialize this development checkout as a research project.

## Development rules

- Edit shared skills under `skills/`, tools under `tools/`, and project assets
  under `templates/`.
- Keep each skill usable without the kit whenever its task allows: keep its
  references and the scripts only it runs inside its folder, link only within
  that folder, and use `.workflow/` context when present rather than requiring it.
  `tools/` holds only commands the kit itself runs.
- Keep `tools/workflow.py` at that path: installed projects run it from a newly
  selected release to update.
- Create optional project structure only when a current task requires it.
- Updates may replace owned method files, never project science or configuration.
- Keep skill instructions, helper scripts, and other development-only files out of
  the bundled template and generated research projects.
- Preserve the template’s private `workspace/`, shared `repository/`,
  authoritative `manuscript/`, bibliography, and journal boundaries.
- Keep structural moves reviewable; do not stage, commit, push, or publish without
  explicit user approval.

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
