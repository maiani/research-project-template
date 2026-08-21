# Research Workflow Skill

This repository develops the `init-research-workflow` Codex skill and its
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
python3 /home/skdys/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/init-research-workflow
bash skills/init-research-workflow/assets/template/bootstrap.sh --check
```

The template snapshot is the source of truth for generated projects.
Keep skill-development files outside `assets/template/`.

## Install the skill

For development, install a symlink so changes in this repository are available
immediately to Codex:

```sh
mkdir -p ~/.codex/skills
ln -sfn "$PWD/skills/init-research-workflow" \
  ~/.codex/skills/init-research-workflow
```

Open Codex in an empty target directory and run `/init-research-workflow`.

For a standalone copy instead of a development symlink, replace the `ln`
command with:

```sh
cp -a skills/init-research-workflow ~/.codex/skills/
```
