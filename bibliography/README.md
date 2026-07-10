# Bibliography

This folder stores the project bibliography and local copies of useful sources.
It is a superset of the manuscript bibliography: keep exploratory references here
even when they are not cited in the paper yet.

Recommended layout:

```text
bibliography/
├── project-slug.bib  # renamed to <actual-project-slug>.bib during bootstrap
├── README.md         # this file
├── *.files/          # local copies managed by pynakes
└── .pynakes-cache/   # API/cache data, git-ignored
```

Use [pynakes](https://github.com/maiani/pynakes) when available:

```sh
pynakes add bibliography/project-slug.bib path-or-url
pynakes lint bibliography/project-slug.bib
```

If `pynakes` is unavailable, add BibTeX entries manually to the project `.bib`
file and keep downloaded PDFs or source snapshots out of git.
