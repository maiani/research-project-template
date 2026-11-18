# Research Workflow Kit

An agent-neutral, updateable research method with a small project initializer.
The package supplies shared skills and tools; each project owns its scientific
choices, evidence, manuscript, environments, and local instructions.

Install the kit once on your computer, then adopt it only in the projects where
it is useful. The central checkout supplies the setup skill; adopted projects
keep independent method versions and their own research content.

## Install once with your agent

Give your agent this request:

> Install the research workflow from
> <https://github.com/maiani/research-project-template> on this computer. Read its
> README, reuse an existing checkout if present, and register the setup skill for
> my agent. Do not initialize or modify any research project yet.

The agent needs local file and command access, Python 3.11+, Git, and access to
that repository. No uv installation, virtual environment, or scientific packages
are needed just to install or adopt the workflow.

For agents carrying out installation, clone once into a persistent location,
then run the top-level entry point:

```sh
git clone https://github.com/maiani/research-project-template.git \
  "$HOME/.local/share/research-workflow"
python "$HOME/.local/share/research-workflow/workflow.py" install
```

The default skill directory is `~/.agents/skills/`. Use
`python workflow.py install --skills-dir PATH` for a different agent's configured
skill directory. The installer links the setup skill to this checkout: keep the
checkout in place. It preserves existing installations and is safe to rerun.
If links are unavailable, copy the complete `skills/init-research-workflow/`
folder to the agent's skill directory, or ask it to read SKILL.md explicitly.

These commands describe the working-tree version; they become available from a
fresh clone after the maintainer publishes this change.

## Ask your agent to use it

Open the intended project folder in your agent and say:

> Use init-research-workflow to start a research project here. My objective is …

For an existing project:

> Use init-research-workflow to adopt the workflow here. Preserve my files and
> local conventions. Do not stage or commit anything.

The agent gathers only missing context and runs setup or adoption. You do not
need to remember internal paths. In later sessions, ask for the research work
normally; the project's AGENTS.md routes the agent to the relevant skills.
If the skill is not discovered, point the agent directly to
`skills/init-research-workflow/SKILL.md` in the installation checkout.

## Start small

For direct command-line use, create an empty project folder and run:

```sh
python /path/to/research-project-template/workflow.py init /path/to/project \
  --title "Project title" --author "Author"
```

Setup requires Python 3.11+ and Git. It creates `project.md`, `AGENTS.md`, a private
`workspace/`, a bibliography, a dated journal, and the hidden `.workflow/` package.
The root Git repository is initialized, but nothing is staged or committed by
default. `--commit` explicitly opts into initial commits.

No manuscript, public-code repository, outreach, referee response, slides,
plot directories, or scratch folders are created in anticipation of future work.
Create scratch work where needed. When a real task needs an optional component:

```sh
python .workflow/workflow.py add manuscript
python .workflow/workflow.py add repository
python .workflow/workflow.py add response
python .workflow/workflow.py add outreach
```

Manuscript and repository setup creates independent Git repositories without
staging or committing. Response and outreach setup requires the manuscript
repository first. Existing destinations are never overwritten. Slides have no
preset scaffold: create the format needed for the actual talk.

Initialization accepts `--manuscript` and `--repository` when those are needed
immediately. `--overleaf-url URL` clones the authoritative manuscript instead;
it preserves existing content and never commits into that checkout.

## Adopt an existing project

From the existing project root, run the package's manager:

```sh
python /path/to/research-project-template/workflow.py adopt
```

Adoption installs `.workflow/`, writes `workflow.json`, adds a small routing block
to `AGENTS.md`, and links skills under `.agents/skills/` where supported. Existing
instructions and foreign skills are preserved. It creates no project scaffold,
moves no research files, and does not initialize or change existing repositories.
Read the linked skills explicitly when the client cannot discover them.

The old copied workflow remains a local override: review outdated local rules
selectively rather than replacing an existing AGENTS.md during adoption.

## Shared method, local decisions

The package contains three ongoing skills: research, manuscript/revision, and
sharing/release. Setup remains `init-research-workflow`. Detailed figure guidance
and optional templates stay in the hidden package until needed.

Local `AGENTS.md`, `project.md`, and `workflows/research.md`,
`workflows/manuscript.md`, or `workflows/release.md` override shared defaults.
Create override files only when there is something to override. Keep scientific
models, conventions, numerical settings, and environment locks in the project.
Private exploration cannot become a dependency of shared artifacts.

## Python environments

Use the existing shell Python during exploration and development. uv is the
preferred Python dependency manager when needed, but setup creates no virtual
environment or lockfile and installs no packages. The optional shared-code
manifest starts with no dependencies. Add requirements as they arise; resolve,
lock, and verify them in a clean environment when preparing a codebase release.
Existing projects keep their environment choices unless migration is requested.

## Updates

From a project root:

```sh
python .workflow/workflow.py status
python .workflow/workflow.py check
python .workflow/workflow.py update
python .workflow/workflow.py update --to v3.0.0
python .workflow/workflow.py update --unpin
```

`v3.0.0` above is an example for a future release, not a published release.
Normal updates select the latest stable numeric release tag. Revisions predating
this package format cannot be installed; legacy projects use adoption first.
`--to` pins a tag or commit until explicitly unpinned. Updates execute the selected
version's installer. They reject modified or unrecognized package contents.

`workflow.json` records source, revision, pin, installation mode, project metadata,
and update policy. Unknown keys are preserved. Set `updates` to `ask` (default),
`auto` (explicit opt-in), or `off`. Session-start checks are cached for a day;
`check --force` refreshes them. Unavailable networks do not block research. No
scheduler, daemon, package installation, or background service is installed.

An update replaces only the owned hidden package and refreshes missing skill
links. It does not change copied manuscript configuration, project instructions,
scientific code, data, environments, or dependency locks. Compare updated
`.workflow/templates/` with project-owned files manually when a configuration
change is wanted. Keep `workflow.json` and the package snapshot in project version
control for reproducible method versions; local check caches are ignored.

## Develop improvements across projects

Use one pilot project with an editable installation:

```sh
python /path/to/research-project-template/workflow.py adopt \
  --editable /path/to/research-project-template
```

The pilot directly uses the checkout; changes take effect immediately. The manager
never pulls or updates an editable installation. Other projects should use release
snapshots so experiments do not change their instructions unexpectedly.

When project work reveals a reusable lesson, change the shared package without
project data, validate it, and record why in the project's journal. Release with
explicit maintainer authorization; other projects then choose whether to update.
Do not modify an installed snapshot as the source of a reusable fix.

The canonical portable distribution remains the complete
`skills/init-research-workflow/` folder. Its `assets/template/` is the minimal
project scaffold; `assets/workflow/` is the shared runtime, ongoing skills, and
optional templates. Copying that complete skill remains self-contained. No plugin
or client-specific instruction file is required.

## Validation

```sh
python skills/init-research-workflow/scripts/init_project.py --check
python -m unittest discover -s skills/init-research-workflow/tests -v
TEST_LATEX=1 python -m unittest discover \
  -s skills/init-research-workflow/tests -v
```

The last command additionally exercises manuscript builds and cleanup using an
installed Just/TeX toolchain. Figure rendering guidance has its separate optional
`skills/init-research-workflow/tests/smoke-figures.py` check.
