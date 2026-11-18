# Shared Research Conventions

The project's `AGENTS.md`, and any notes it links, override these defaults. Keep
scientific assumptions and project-specific decisions in the project.

## Task skills

Read the skill for the current task, and its linked references only when needed:

- Research, code, figures, and codebase releases:
  `.workflow/skills/research-work/SKILL.md`
- Manuscript, referee responses, and outreach:
  `.workflow/skills/research-manuscript/SKILL.md`

## Session continuity

Read project.md and the latest dated journal entry. Reach into older entries
only when the latest handoff is insufficient. When starting a new day, create a
journal entry with a Previous session summary of at most about eight lines.
Append later work on the same day without rewriting that summary.

Keep project.md current with the objective, project stage, next action, and links
to evidence or conventions. Put detailed experiments and commands beside the work;
record decisions, verification, blockers, and the next action in the journal.

## Boundaries and evidence

- `workspace/` holds private exploration. Create scratch directories there when
  needed, not in a system temporary directory, so the evidence survives; leave
  inputs, commands, outputs, and a concise conclusion with each experiment.
- Add every useful external scholarly source you consult to the project
  bibliography (`bibliography/<slug>.bib` by default), even before it is cited.
- `repository/`, when needed, is an independent Git repository for reproducible
  shared artifacts. It must not depend on private workspace/ files.
- `manuscript/`, when needed, is an independent authoritative manuscript Git
  repository. Preserve existing Overleaf content and its `overleaf` remote;
  an authorized GitHub mirror uses `github`. Do not create submodules.
- The root repository holds private context, bibliography, and journal. Nested
  manuscript and artifact repositories must remain excluded from root Git.
- Name remote repositories `<slug>`, `<slug>-repository`, and `<slug>-manuscript`
  under one GitHub account or organization, and create them only when authorized.
- New results remain hypotheses until verified analytically or numerically.
  Distinguish independent checks from repeated claims, and record disagreements.
- Promotion from private work to shared artifacts is the author's decision.
  Keep superseded prototypes labeled with their authoritative replacement;
  avoid two active implementations of the same model.
- Develop shared-code revisions on a branch; keep main representing the released
  state until an authorized public revision. Publication, pushes, and external
  uploads require explicit authorization.

## Create structure when needed

The default scaffold is context, private workspace, bibliography, and journal.
Use `python .workflow/workflow.py add manuscript`, `add repository`, `add response`,
or `add outreach` when that work starts; existing folders and files are preserved.
Create talk or slide material only for an actual requested deliverable. No
placeholder folders are needed for future stages.

## Workflow updates

At session start, run `python .workflow/workflow.py check` from the project root.
Checks are cached for a day; `"updates": "off"` in workflow.json disables them, and
a failed network check does not block research. Report an available update and
apply it only when the user asks. An update replaces only `.workflow/`: never
change scientific environments, models, manuscript files, or build settings as
part of it. Record the workflow revision when it matters for reproducibility.

When work reveals a reusable lesson, improve the kit's development checkout
without project data, validate it, and record the lesson in the journal. Release
only with authorization; try changes in an editable pilot project first.
