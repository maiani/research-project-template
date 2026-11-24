---
name: manuscript-preflight
description: Audit a scientific LaTeX manuscript, thesis, or supplement before journal or arXiv submission (abbreviations, symbols, cross-references, citations, typography, LaTeX and source-bundle hygiene, venue requirements) and recheck findings after corrections. Use when asked to review, polish, audit, or prepare a manuscript for submission.
---

# Manuscript Preflight

This skill works in any LaTeX project. When the project uses the research
workflow (`.workflow/conventions.md` exists), first read it, `project.md`, and the
latest journal entry; that project's instructions take precedence, and
`.workflow/skills/research-manuscript/SKILL.md` covers drafting, revisions, and
builds. Otherwise follow the project's own instructions and build documentation.

Default to reporting findings with evidence and suggested fixes. Edit only when
requested or when the task clearly requires edits. An audit does not establish
scientific validity or guarantee acceptance.

## Scope

- Audit a typical article in full. When the user names particular concerns,
  audit only the matching checklist sections and say so.
- For a quick pass or a long manuscript (thesis, long review, main text plus
  supplement), run the checker plus abbreviation, symbol, cross-reference,
  citation, and submission-blocker checks. State which sections were deferred.
- For a follow-up, start from the previous report: recheck its findings and the
  material changed since, and widen the audit when the changes warrant it.

## Audit

1. Identify the main text, supplements, target venue, and intended submission
   contents. Assess bundle hygiene against what will be submitted: private notes
   and response material may legitimately remain in a working checkout.
2. Build with the project's documented command when practical, otherwise
   `latexmk -pdf -interaction=nonstopmode -halt-on-error <main.tex>`. Inspect the
   PDF and the relevant `.log`, `.blg`, `.bbl`, and `.aux` output. If a build or
   visual check is unavailable, continue with source checks and report the
   limitation.
3. Run the deterministic checker, `scripts/check_manuscript.py` in this skill's
   folder (resolve symlinks; it needs only the Python standard library):

   ```sh
   python <skill-folder>/scripts/check_manuscript.py <manuscript-dir>
   ```

   In a research-workflow project, run
   `python .workflow/skills/manuscript-preflight/scripts/check_manuscript.py manuscript`
   from the project root. Add `--json` for structured output.

   Check the reported roots and skipped files: detection honors `latexmkrc`,
   follows input closures, and skips backups, latexdiffs, and auxiliary documents
   such as response letters. Use `--main path/to/file.tex` to correct the
   selection or to audit a skipped document on request. Build logs are read from
   the latexmkrc `$aux_dir` or `$out_dir`, else beside the source; pass
   `--log-dir` (relative to the working directory) for other builds.

   ERROR findings are Must-fix candidates; verify WARN and INFO findings in
   context, since they are heuristics.
4. Read [references/checklist.md](references/checklist.md) and apply the
   sections within scope. The checker covers mechanical findings: labels,
   citation keys, duplicate DOIs, figure files and their case, PDF metadata,
   deprecated packages, draft artifacts, invisible Unicode, non-semantic
   constructs, and build-log warnings. Review prose, notation, abstract/body and
   supplement consistency, and venue requirements in context; for symbols,
   read the prose near first use rather than relying on lexical extraction.
   Verify current venue rules before treating them as submission requirements.

## Report

Give the entry points, scope, checks performed, and their limitations, then:

- **Must fix:** compile or submission blockers, undefined references or
  citations, an abbreviation not expanded at first use, an ambiguous symbol, or a
  clear typo.
- **Should fix:** style and consistency, weak cross-reference wording,
  unnecessary abbreviations, unused or deprecated packages, source-bundle
  hygiene, or avoidable LaTeX fragility.
- **Consider:** judgment calls, venue-style choices, and clarity suggestions.

Cite file and line, quote only enough to locate each issue, and give exact
replacements for local prose fixes. Separate confirmed findings from heuristics.

In a research-workflow project, save the report as
`workspace/preflight/YYYY-MM-DD.md`, since it may quote private notes, and record
its path and the blocking findings in the journal; a follow-up starts from it.
Otherwise return the report in the conversation and save it only where the user
asks, outside the submission sources.

## Corrections

- Make minimal, local, source-preserving edits. Preserve author voice, journal
  macros, and typography conventions; propose substantial rewrites separately.
- Do not silently change scientific claims, equations, definitions, notation,
  units, author names, affiliations, acknowledgments, funding text, or
  bibliography metadata.
- Report anonymization edits and missing required statements (author
  contributions, competing interests, funding) for the authors to decide; do not
  draft them.
- Rerun the affected checks, and rebuild and inspect the PDF after changes that
  affect rendered output.
