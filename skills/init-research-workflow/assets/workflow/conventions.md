# Shared Research Conventions

Local `AGENTS.md`, `project.md`, and `workflows/<job>.md` override these defaults.
Keep scientific assumptions and project-specific decisions in the project.
Read only the skill and supporting guide relevant to the current task.

## Session continuity

Read project.md and the latest dated journal entry. Reach into older entries
only when the latest handoff is insufficient. When starting a new day, create a
journal entry with a Previous session summary of at most about eight lines.
Append later work on the same day without rewriting that summary.

Keep project.md current with the objective, project stage, next action, and links
to evidence or conventions. Put detailed experiments and commands beside the work;
record decisions, verification, blockers, and the next action in the journal.

## Boundaries and evidence

- `workspace/` holds private exploration. Create scratch directories when needed;
  leave inputs, commands, outputs, and a concise conclusion with each experiment.
- `repository/`, when needed, is an independent Git repository for reproducible
  shared artifacts. It must not depend on private workspace/ files.
- `manuscript/`, when needed, is an independent authoritative manuscript Git
  repository. Preserve existing Overleaf content and its `overleaf` remote;
  an authorized GitHub mirror uses `github`. Do not create submodules.
- The root repository holds private context, bibliography, and journal. Nested
  manuscript and artifact repositories must remain excluded from root Git.
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
Use `python .workflow/workflow.py add manuscript` or `add repository` when that
work starts. Preserve existing repositories rather than replacing them.
Outreach and referee-response templates are available with `add outreach` and
`add response` only when needed. Create talk or slide material for an actual
requested deliverable. No placeholder folders are required for future stages.

## Python environments

Use the existing shell Python for exploration and development; avoid creating
virtual environments by default. Prefer uv when dependency management is needed,
with only the dependencies used by the codebase. Fix and verify dependencies at
codebase release preparation, using a clean environment and a uv lockfile.
Respect existing project environments and release locks. See the research guide
for details; do not mutate a shared environment without approval.

## Workflow improvements and updates

At session start, run `python .workflow/workflow.py check` from the project root.
Checks are cached for a day; `updates: "off"` disables them. A failed network
check does not block research. Default `ask` reports changes; `auto` is explicit
opt-in and refreshes only the shared package. Never update scientific environments,
models, manuscript files, or existing build settings as part of a package update.
Record the package revision when it matters for a reproducible investigation.

When work reveals a reusable lesson, improve the development package without
project data, validate it, and record the lesson in the journal. Release only
with authorization. Use editable mode in a pilot project and versioned snapshots
elsewhere, so experimental instructions do not affect every project at once.

Delegate bounded discovery or extraction to cheaper agents when available and
authorized; keep scientific judgments and verification in the main session.
Reuse evidence and return compact findings with sources and uncertainties.
