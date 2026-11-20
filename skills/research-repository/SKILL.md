---
name: research-repository
description: Promote approved research code to the project's shared repository, organize and document it for collaborators, and prepare authorized codebase releases.
---

# Research Repository

Read project context, the latest journal, and `.workflow/conventions.md`.
`repository/` is the shared, reproducible counterpart of the private workspace: it
holds only results the author has approved and must run without private files.
Computing or verifying a result follows the research-work skill, wherever the code
lives; this skill covers changes to the shared codebase itself.

## Promote

- Promotion is the author's decision, made for specific results. When approved
  work arrives and no shared repository exists, run
  `python .workflow/workflow.py add repository`.
- Move each model and its observables once, then make workspace experiments import
  the shared version. Label the retained prototype as superseded, linking its
  replacement, rather than keeping two active implementations.
- Reproduce promoted results from the shared code and compare them with the
  workspace evidence before relying on them. Record the promotion and any
  discrepancy in the journal.

## Organize

- Keep the model, figure generators, and analytic checks apart, creating
  directories only as needed. Generators and notebooks import the model; name them
  as described in [figures.md](../research-work/figures.md).
- Declare each dependency in `pyproject.toml` when shared code starts using it.
  Until release, run code in the environment research-work describes; lock only
  when preparing a release.
- Keep the README current: map each figure or analytic claim to its script and
  shared model, with inputs, parameters, expected output, command, and approximate
  runtime. For a cache, record the generating code version and how to rebuild or
  invalidate it; a cache must not be the only source of a result.
- Write documentation and accompanying material for collaborators who have never
  seen the private workspace.

## Collaborate

- Make revisions on a branch, never directly on `main`; collaborators may share it.
  Merge their work rather than overwriting it, and do not rewrite history that
  others have fetched.
- At an authorized public revision, squash-merge the branch into `main`, so `main`
  always represents the latest release.

## Release

A codebase release accompanies a manuscript version, such as a preprint, a
revision, or the published paper. Prepare it completely, then wait for explicit
authorization before tagging, pushing, making the repository public, or uploading
an archive.

- Declare the actual dependencies in `pyproject.toml`, run `uv lock`, and verify
  representative outputs in a clean environment with `uv sync --locked` and
  `uv run --locked`. Keep `pyproject.toml` and `uv.lock` in the release, and keep
  an existing project's dependency manager unless migration is requested.
- Document system tools, fonts, and hardware separately; the lockfile does not
  capture them. Preserve an existing release lock unless a change is intentional.
- Check the results against the manuscript version being released, keep numerical
  settings and model choices explicit, and record the workflow version used
  (`workflow.json`).
- Before anything becomes public, review the files and history to be published
  for private paths, workspace references, credentials, unpublished data,
  oversized files, and the licenses of included material.
- Confirm the license and how to cite the code. Tag each release and record in the
  README which manuscript version it accompanies; add an archive DOI, for example
  from Zenodo, once one exists.
