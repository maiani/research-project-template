# AI agent instructions — research workflow skill development

This repository develops the `init-research-workflow` Codex skill.
It is not itself an initialized research project.

## Repository layout

```text
.
├── skills/init-research-workflow/
│   ├── SKILL.md                    # callable skill instructions
│   ├── agents/openai.yaml          # UI metadata
│   ├── scripts/init_project.sh     # portable initialization runner
│   └── assets/template/            # canonical project template
├── README.md                       # development overview
├── CHANGELOG.md                    # workflow release history
└── CLAUDE.md                       # repository-level development guidance
```

The template inside `assets/template/` must be self-contained.
It must not depend on the development repository being present when the skill
is used in an empty directory.

## Development rules

- Edit the bundled template under `skills/init-research-workflow/assets/template/`.
- Keep skill instructions and helper scripts outside the bundled template.
- Use `git mv` for structural moves so Git preserves file history.
- Do not copy development-only files into generated research projects.
- Preserve the template’s private `workspace/`, shared `repository/`,
  authoritative `manuscript/`, bibliography, and journal boundaries.
- Do not commit, push, or publish changes without explicit user approval.

## Validation

Run the official skill validator after changing the skill:

```sh
python3 /home/skdys/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/init-research-workflow
```

Run the bundled template preflight and smoke test when changing the template:

```sh
bash skills/init-research-workflow/assets/template/bootstrap.sh --check
bash skills/init-research-workflow/assets/template/tests/smoke-bootstrap.sh
```

For an end-to-end portable-skill test, invoke
`skills/init-research-workflow/scripts/init_project.sh` with an empty temporary
directory and representative project values.
