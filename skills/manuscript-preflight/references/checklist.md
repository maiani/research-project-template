# Manuscript Editorial Checklist

## Semantic Structure

Machine readers (parsers, indexers, retrieval systems, LLM agents) and assistive technology both work from the source, not the rendered page. Structure that exists only visually — bold text that looks like a theorem, a screenshot that looks like a table — is lost to them. The PDF shows what something looks like; the source declares what it is.

- Check that structurally meaningful content is encoded structurally: theorems, lemmas, propositions, definitions, assumptions, and remarks as `amsthm`/journal environments rather than bold or italic lead-ins; algorithms as `algorithm`/`algorithmic`/listing environments; code and terminal output as verbatim or listing environments.
- Check that display math uses `equation`, `align`, or `\[...\]` rather than plain-TeX `$$...$$`, and that any equation discussed or referenced in prose is numbered and labeled.
- Check that every cross-reference is a live `\ref`/`\eqref`/`\cref`, never a hardcoded number such as "Fig. 2" typed as text.
- Prefer semantic, descriptive labels (`eq:gap-equation`, `fig:phase-diagram`, `thm:main-bound`) over positional ones (`eq1`, `fig2`); positional labels go stale on reorganization and carry no meaning downstream.
- Check that tables, derivations, algorithms, and code blocks are LaTeX source, not images (details in Figures and Tables as Source Objects below).
- Check that macros support notation and formatting rather than concealing content: a macro for `\mathbb{R}` or a repeated operator is good; a macro that expands to a paragraph of prose or a whole result hides content from every source-level reader.
- Check that sectioning uses real `\section`/`\subsection`/`\paragraph` commands rather than manual bold headings, and that lists use `itemize`/`enumerate`/`description` rather than manual bullets or dashes.
- Check that footnotes, URLs, and identifiers use their semantic commands (`\footnote`, `\url`/`\href`, `\doi` where available) rather than typeset imitations.

## Abbreviations and Acronyms

- Build a candidate list from all-caps terms, mixed forms such as `s-wave` or `t-test`, and field-specific abbreviations.
- Verify first textual use expands the abbreviation unless it is a universal convention for the target venue, such as SI, PDF, or URL.
- Suggest removing an abbreviation definition when the term is used only once or twice, when the abbreviation makes prose harder to read, or when the long form is clearer and not burdensome.
- Check consistency after definition: do not alternate between pluralized, hyphenated, or differently capitalized forms without reason.
- Watch for abbreviation definitions in abstract, main text, and supplement. Many journals require the abstract to stand alone.
- Do not expand standard mathematical functions or units as abbreviations.

## Symbols and Notation

- For each important symbol in equations and inline math, verify it is introduced in nearby prose or in a clearly referenced definitions paragraph.
- Prioritize symbols that carry domain meaning: e.g., Hamiltonians and order parameters in physics, estimators and loss functions in statistics/ML, utility and welfare functions in economics, plus field-agnostic objects such as indices, vectors, matrices, distributions, and dimensionless parameters.
- Distinguish local dummy variables from manuscript-level notation. Do not demand definitions for obvious summation/integration variables when context is clear.
- Check notation consistency: roman vs italic subscripts, bold vectors, hats for operators, calligraphic symbols, dagger/star notation, plus/minus branch labels, and overbars.
- Check units and dimensions for quantities stated in prose, axes, captions, and tables.
- Flag reused symbols with incompatible meanings unless the manuscript explicitly scopes the reuse.

## Cross-References

- Check that every `\ref`, `\eqref`, `\autoref`, `\cref`, figure, table, section, appendix, and supplement reference resolves.
- Prefer journal-consistent forms: `Eq.~(\ref{...})`, `Fig.~\ref{...}`, `Sec.~\ref{...}`, or the project's existing macro style.
- Verify labels are meaningful and unique.
- Prefer semantic labels such as `eq:gap-equation`, `fig:phase-diagram`, and `tab:parameters` over opaque labels such as `eq1`, `fig2`, or `table_new`.
- Check that equations, figures, and tables are introduced before or near first discussion unless journal style allows otherwise.
- Inspect captions for standalone clarity: symbols, parameters, units, and panel labels should be understandable.

## Main Text and Supplement Cross-Consistency

- Check that symbols, notation, and terminology are used consistently between main text and supplement; flag redefinition or conflicting usage of the same symbol.
- Check that cross-references between main text and supplement resolve and follow a consistent numbering convention, such as `Eq.~(S3)` in the SM matching how the main text cites it.
- Check that every supplement reference cited from the main text exists in the supplement, and that supplement content is not orphaned from the main narrative.
- Check that abbreviations defined in the main text are not silently redefined or left unexpanded in the supplement, and vice versa.

## Citations and Bibliography

- Check undefined citations, duplicate keys, missing bibliography files, broken BibTeX/BibLaTeX fields, and suspicious placeholder references.
- Check for the same reference imported twice under different keys — matching DOIs, arXiv IDs, or near-identical titles — a duplicate that key-level checks cannot see.
- Verify claims such as "first", "recent", "well known", and "has been shown" have appropriate citations.
- Do not rewrite bibliography metadata unless asked; report metadata issues separately.
- Check that citation ordering and punctuation follow the active style.
- Check whether bibliography entries have enough metadata for reliable resolution: title, author, venue, year, pages or article number, DOI, arXiv ID, and URL when available.

## Abstract and Body Consistency

- Check that quantitative claims, numerical results, and qualitative conclusions stated in the abstract match the values and claims in the body and supplement.
- Check that terminology and abbreviations used in the abstract match their definitions in the main text, since many journals require the abstract to stand alone.
- Flag abstract content that appears to reference an earlier version of a result, such as different parameter values or a conclusion worded differently from the body.

## Anonymization and Double-Blind Compliance

- Apply this section only when the target venue requires double-blind or anonymized review; confirm the requirement from submission guidelines or the user before flagging identity issues as blocking.
- Flag author names, initials, and affiliations appearing in visible text, running headers/footers, file names, or document metadata.
- Flag self-citations phrased in an identifying way, such as "our previous work" or "we previously showed," and suggest neutral third-person phrasing that preserves the citation.
- Check acknowledgments and funding statements for author- or institution-identifying content that should be deferred to a camera-ready version.
- Check PDF metadata (`pdfauthor`, `pdftitle`) and figure/data filenames for identifying strings.
- Check that code or data repository links do not point to non-anonymized accounts; suggest an anonymized mirror when the venue requires one.
- Do not remove or rewrite identifying content automatically; anonymization changes affect authorship attribution and require author confirmation.

## Typography and Prose

- Check spelling, doubled words, missing articles, repeated phrases, inconsistent hyphenation, and capitalization of technical terms.
- Check typography: nonbreaking spaces before citations and references, en-dashes for ranges, minus signs in math mode, correct primes, quotes, and punctuation around equations.
- Check common field-specific wording issues, applying the manuscript's own domain conventions (e.g., in physics: "eigenenergy" vs "eigenvalue", "gap closes" vs "gap is closed"; in statistics: "significant" used loosely vs in its technical sense); "dependence on" vs "dependence of", "couple to" vs "couple with" are common cross-field slips.
- Keep edits conservative. Prefer local replacements over full sentence rewrites unless the sentence is genuinely unclear.
- Preserve author voice and target-journal style.

## LaTeX Hygiene

- Look for unresolved references/citations, overfull boxes in final PDF-relevant areas, duplicate labels, unused labels for deleted material, and fragile macros in captions or section titles.
- Prefer semantic macros already present in the project; do not introduce a new macro layer during an editorial audit.
- Avoid manual spacing fixes unless they address a visible problem and match project style.
- Check math punctuation and alignment environments for missing punctuation, inconsistent equation numbering, and labels placed on the intended lines.
- Watch for submission blockers: absolute local paths, missing figures, generated files expected by the build, comments containing private notes, TODO/FIXME markers, tracked-change artifacts, and arXiv-incompatible packages.
- Watch for draft-stage artifacts that render in the PDF: `\todo`/`todonotes`/`fixme`/`changes` commands and packages, the `draft` document-class option, `lineno` line numbers on a final version, and `lipsum`/lorem-ipsum placeholder text.
- Watch for invisible pasted Unicode (non-breaking spaces, zero-width characters, BOMs) from word processors or PDFs; it compiles inconsistently and typesets wrongly.
- Apply the Semantic Structure section above for environment usage, display math, labels, and macro discipline.

## Package and Macro Cleanup

- Inventory `\usepackage`, `\RequirePackage`, class options, local `.sty` files, and macro definitions before suggesting cleanup.
- Suggest removing packages only when there is clear evidence they are unused, redundant with the document class, or loaded only for deleted material. Treat package interactions conservatively.
- Flag deprecated or obsolete packages and commands, especially `epsfig`, `psfig`, `subfigure`, `times`, `txfonts` when inappropriate, `eqnarray`, raw `\bf`, `\it`, and custom replacements for standard `amsmath` constructs.
- Prefer journal-compatible replacements: `graphicx` for graphics, `subcaption` or journal-approved alternatives for subfigures, `newtxtext/newtxmath` only when the template allows font changes, and `align`/`equation` rather than `eqnarray`.
- Check rarely used macros. If a macro is used only once or twice, suggest inlining it when doing so improves readability and does not obscure notation, semantic intent, or future reuse.
- Do not remove macros that encode scientific notation, journal style, author workflow, or cross-file consistency unless the user asks for an implementation cleanup.
- Flag macros that hide substantive prose, long arguments, results, or large text blocks. Macros should normally support notation, formatting, and repeated mathematical objects, not conceal paper content.
- Report risky package changes as suggestions with rationale and validation requirements; do not apply them silently during an editorial pass.

## Source Bundle and Metadata

- Check whether the public source bundle contains only files needed to compile or understand the submitted paper. Suggest removing old drafts, response letters, private notes, unused figures (image files no root ever includes), local data dumps, screenshots, and versioned clutter such as `final_final`.
- Prefer meaningful file names for manuscript parts, figures, tables, and supplements. Opaque names such as `fig1_new.pdf` or `plot_final2.pdf` are acceptable only when project conventions already make them clear.
- Check for private or misleading source comments: coauthor notes, referee-response fragments, TODOs, local paths, discarded paragraphs, confidential text, hidden prompts, keyword stuffing, or instructions aimed at automated systems.
- Check that arXiv or public-source submissions include a clean compile path, required figures, generated files that cannot be regenerated by the submitter, and no dependency on private local paths.
- When the manuscript has a published or accepted version, suggest adding or updating DOI, journal reference, arXiv relation, and version notes where the venue allows.
- Check PDF metadata when `hyperref` is used: `pdftitle`, `pdfauthor`, and `pdfkeywords` should be present, non-empty, and accurate unless the journal template manages them. Flag empty or placeholder values — an empty `pdfauthor` is a finding in its own right, not only an anonymization concern.
- Check that every `\includegraphics` target exists on disk with the exact same case as written in the source; case mismatches compile on case-insensitive filesystems and then fail on arXiv and Linux.
- Check figure files against the venue's technical limits visible from the log or file inspection, such as embedded PDF version (`found PDF version <1.6>, but at most version <1.5>` warnings).
- Check for persistent identifiers where relevant: DOI, arXiv ID, ORCID, grant numbers, dataset DOI, software DOI, and code archive DOI.
- For computational or data-driven papers, check for a clear data/code availability statement and stable archival links, not only informal repository URLs.

## Required Editorial Statements

- Check for an author contribution statement (e.g., CRediT taxonomy) when the venue requires one, and that all listed authors are covered.
- Check for a competing interests / conflict of interest statement, including a proper "no competing interests" declaration when appropriate.
- Check acknowledgments and funding text for consistency with grant numbers, agency names, and any specific wording mandated by funders.
- Do not draft or alter the substance of these statements; report missing or inconsistent statements for author decision.

## Journal Length and Format Constraints

- Identify the venue's format requirements when visible, such as page/word/character limits, subject-classification requirements (e.g., PACS/PhySH in physics, MSC in mathematics, ACM CCS in computer science, JEL codes in economics), and abstract length limits, from a style file, submission guidelines, or existing project notes.
- Estimate whether the manuscript is near or over a known hard limit (e.g., a letters-format page limit) using page count, word count, or the journal's own counting convention when derivable.
- Check for expected arXiv metadata conventions, such as a comments field summarizing pages/figures and an appropriate primary/cross-list category.
- Report length concerns as `Should fix` or `Consider` since remedies, such as cutting content or moving material to the supplement, require author judgment.

## Figures and Tables as Source Objects

- Prefer important technical content as LaTeX/text/data rather than screenshots or image-only content. Flag image-only tables, algorithms, derivations, code/output blocks, and text-heavy diagrams when they should be source.
- Check that table sources use explicit column headers, units, variable definitions, notes, and consistent names rather than encoding meaning only through spacing or visual grouping.
- Check that figure filenames and labels describe the figure's role, not just its order.
- Check whether captions can stand alone when extracted from the PDF: they should identify the object, define nonstandard symbols or abbreviations, give units or parameter values when needed, and explain panel labels.
- Suggest alt text or equivalent accessible descriptions where the class/package supports it, especially for diagrams or figures with substantial semantic content.
- Check that figures intended for print are vector formats (PDF/EPS) rather than low-resolution raster images, except where raster is unavoidable, such as photographs or dense heatmaps.
- Check that raster figures meet reasonable resolution for print; flag visibly low-DPI or upscaled images.
- Check that multi-panel and multi-curve figures use colorblind-safe, distinguishable palettes and do not rely on color alone to convey meaning, pairing color with line style or markers.
- Check that figure text (axis labels, legends, panel labels) is legible at final print size and roughly consistent in font size across figures.

## Supporting Commands

Use available tools opportunistically; a missing tool does not fail the audit.

```bash
rg -n -g "*.tex" -o "\\b[A-Z][A-Z0-9-]{1,}\\b" | sort -t: -k3 -u   # abbreviation candidates, deduplicated
rg -n -g "*.tex" "\\$[^$]+\\$|\\\\[a-zA-Z]+|\\\\cite|\\\\ref|\\\\eqref|\\\\label"
rg -n -g "*.tex" "\\\\usepackage|\\\\RequirePackage|\\\\newcommand|\\\\renewcommand|\\\\DeclareMathOperator|\\\\def"
rg -n -g "*.tex" "\\\\label\\{(sec|eq|fig|tab|app)[0-9A-Za-z_-]*\\}|\\\\caption\\{.{0,30}\\}|TODO|FIXME|private|confidential|local path"
rg -n -g "*.tex" "\\\\hypersetup|pdfauthor|pdftitle|pdfkeywords|Data and code availability|Code availability|Data availability"
rg -n -g "*.log" -g "*.blg" "undefined|multiply defined|Citation|Reference|Overfull|Underfull|Warning"
rg -n -i -g "*.tex" "our (previous|prior|earlier) work|we (previously|earlier) (showed|reported|demonstrated)|\\\\author\\{|\\\\affiliation\\{"
chktex -q -n 1 -n 8 -n 13 <main.tex>
```

Build logs may sit in a separate build directory (latexmk `$aux_dir` or `$out_dir`); search there for the log patterns.

## Output Discipline

- Separate clear errors from editorial preferences.
- Give exact file/line references when possible.
- Include enough quoted source text to locate the issue, but keep quotes short.
- If a check could not be performed, say why.
- When asked to edit, apply minimal changes first and then rerun relevant checks.
