# Research Workflow Kit

An agent-neutral, updateable research method with a small project initializer.
The kit supplies shared skills and tools; each project owns its scientific
choices, evidence, manuscript, environments, and local instructions.

Install the kit once on your computer, then adopt it only in the projects where
it is useful. The central checkout supplies the `research-setup` skill, and
`manuscript-preflight` for pre-submission audits of any LaTeX manuscript; each
project keeps its own pinned copy of the method, so it stays independent of the
central checkout once initialized or adopted.

## Install once with your agent

Give your agent this request:

> Install the research workflow from
> <https://github.com/maiani/research-project-template> on this computer. Read its
> README, reuse an existing checkout if present, and register its skills for
> my agent. Do not initialize or modify any research project yet.

The agent needs local file and command access, Python 3.11+, Git, and access to
that repository. No uv, virtual environment, or scientific packages are needed to
install, initialize, or adopt the workflow.

For agents carrying out installation, clone once into a persistent location,
then run the top-level entry point:

```sh
git clone https://github.com/maiani/research-project-template.git \
  "$HOME/.local/share/research-workflow"
python "$HOME/.local/share/research-workflow/workflow.py" install
```

The default skill directory is `~/.agents/skills/`. Use
`python workflow.py install --skills-dir PATH` for a different agent's configured
skill directory; for Claude Code, that is `--skills-dir ~/.claude/skills`.
The installer links both skills to this checkout: keep the checkout in place.
It preserves existing installations and is safe to rerun. If links are
unavailable, keep the complete kit checkout and ask the agent to read
`skills/research-setup/SKILL.md` explicitly.

## Ask your agent to use it

Open the intended project folder in your agent and say:

> Use research-setup to start a research project here. My objective is …

For an existing project:

> Use research-setup to adopt the workflow here. Preserve my files and local
> conventions. Do not stage or commit anything.

The agent gathers only missing context and runs setup or adoption. In later
sessions, ask for the research work normally: the project's AGENTS.md sends the
agent to `.workflow/conventions.md`, which names the skill for each task.

## Start a project from the command line

Create an empty project folder and run:

```sh
python /path/to/research-project-template/workflow.py init /path/to/project \
  --title "Project title" --author "Author"
```

This creates `project.md`, `AGENTS.md`, a private `workspace/`, a bibliography, a
dated journal, and the hidden `.workflow/` snapshot. The private root Git
repository gets a local initial commit; pass `--commit` to also commit new
manuscript or artifact repositories.
`--manuscript` and `--repository` create those components immediately;
`--overleaf-url URL` clones an existing Overleaf manuscript instead, preserving
its content and never committing into it.

Nothing else is created in advance. When a task needs an optional component, run
from the project root:

```sh
python .workflow/workflow.py add manuscript   # independent Git repository
python .workflow/workflow.py add repository   # independent Git repository
python .workflow/workflow.py add response     # referee response template
python .workflow/workflow.py add outreach     # outreach README and folders
```

Response and outreach need the manuscript repository first. They may be added to
existing folders; existing files are never overwritten.

## Adopt an existing project

From the existing project root:

```sh
python /path/to/research-project-template/workflow.py adopt \
  --title "Project title" --author "Author"
```

Adoption installs `.workflow/`, writes `workflow.json`, and appends a short block
to `AGENTS.md` pointing the agent at `.workflow/conventions.md`. It creates no
scaffold, moves no research files, and does not change existing repositories. The
title and authors are optional; they fill in components added later.

Instructions copied from an older version of the workflow remain local overrides
in AGENTS.md: review outdated rules selectively rather than replacing the file.

## Layout

```text
skills/
  research-setup/       start or adopt a project (installed globally)
  research-work/        research, calculations, code, and figures
  research-repository/  promotion, shared code, collaboration, and codebase releases
  research-manuscript/  manuscript, referee responses, and outreach
  manuscript-preflight/ pre-submission audits (installed globally; works anywhere)
conventions.md          shared rules and routing to the skills
tools/                  the kit's Python commands
templates/              project files for `init` and optional components for `add`
workflow.py             install, init, adopt, and project commands
```

The rules themselves live in `conventions.md` and the skills; this README only
describes how to install and run the kit.

## Updates

From a project root:

```sh
python .workflow/workflow.py status
python .workflow/workflow.py update --dry-run
python .workflow/workflow.py update
python .workflow/workflow.py update --to v3.0.0
python .workflow/workflow.py update --unpin
```

`workflow.json` records the installed `version`: a release tag such as `v3.0.0`,
or the nearest tag plus commits for an unreleased revision. The project's
AGENTS.md points there rather than copying a number that updates would make stale.

Normal updates select the latest stable numeric release tag; `--to` pins a tag or
commit until `--unpin`. `--dry-run` reports what an update with the same options
would install and changes nothing; it warns when an unreleased revision is
installed, since the selected release may be older. `status` works offline: it
shows the installed version and pin, and whether `.workflow/` has local changes
that would make an update refuse.

Updates run the selected version's installer and refuse to replace a modified
`.workflow/`. They change only `.workflow/`, never project instructions,
scientific code, data, environments, dependency locks, or manuscript
configuration; compare `.workflow/templates/` manually when you want a newer
configuration. The central `workflow.py` forwards project commands to the
project's own snapshot, so its pin always applies. Keep `workflow.json` and
`.workflow/` in project version control. Versions
before 3.0 cannot be selected with `--to`; 2.x projects adopt the workflow instead.

## Develop improvements across projects

Use one pilot project with an editable installation:

```sh
python /path/to/research-project-template/workflow.py adopt \
  --editable /path/to/research-project-template
```

The pilot's `.workflow/` links to the checkout's kit files, so changes take effect
immediately; it is never pulled or updated by the manager. Other projects should
use release snapshots so experiments do not change their instructions.

When project work reveals a reusable lesson, change the kit without project data,
validate it, and record why in the project's journal. Release with explicit
maintainer authorization; other projects then choose whether to update.

## Validation

```sh
python workflow.py init --check
python -m unittest discover -s tests -v
TEST_LATEX=1 python -m unittest discover -s tests -v
```

The last command also exercises manuscript builds and cleanup with an installed
Just/TeX toolchain. `tests/smoke-figures.py OUTPUT-DIRECTORY` checks the figure
stack in an environment that has it installed.

## License

MIT; see [LICENSE](LICENSE).
