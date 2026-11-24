#!/usr/bin/env python3
r"""Deterministic pre-submission checks for LaTeX manuscripts.

Resolves the manuscript's main file(s), follows their \input/\include
closure, and mechanically checks what can be checked without judgment:

  corpus           : auto-detects root files (\documentclass), honors
                     latexmkrc, skips version siblings (old/backup/staging/
                     arxiv/latexdiff naming) and auxiliary documents
                     (extra/, peer_review/, response letters) with a note
  cross-references : undefined \ref/\cref/..., duplicate and unused labels
  citations        : undefined \cite keys, duplicate and unused bib entries,
                     two entries sharing one DOI (same reference twice)
  figure files     : every \includegraphics target must exist on disk with
                     exact case (case mismatches break arXiv/Linux builds);
                     bundled images no root ever includes
  packages         : deprecated packages (epsfig, subfigure, eqnarray, ...)
  PDF metadata     : hyperref pdftitle/pdfauthor present and non-empty
  semantic source  : image-only tables, bold-text pseudo-theorems,
                     $$...$$ display math, hardcoded "Fig. 2"-style
                     references, opaque label names
  draft artifacts  : \todo/tracked-change commands and packages (todonotes,
                     changes, ...), documentclass 'draft' option, lineno,
                     lipsum/lorem-ipsum placeholder text
  bundle hygiene   : absolute local paths, TODO/FIXME/private-note comments,
                     invisible pasted Unicode (NBSP, zero-width, BOM)
  build log        : embedded-PDF version conflicts, unprocessed floats,
                     missing files, overfull boxes (when a .log exists)

Two-letter font commands are triaged by mode: inside math ({\rm eff} in a
subscript) they are INFO with a \mathrm-style suggestion; in text ({\it ...})
they are WARN. Repeated occurrences are aggregated into one finding.

Usage:
  python3 check_manuscript.py [DIR_OR_FILES ...] [--main FILE] [--log-dir DIR] [--json]

Passing a .tex file (or --main) audits exactly that root. Passing a
directory auto-detects roots; every skipped sibling is reported, never
silently dropped.

Each root's build log is read from the $aux_dir (else $out_dir) set in the
nearest latexmkrc, else from beside the root; --log-dir overrides both.

Exit code is 1 if any ERROR-severity finding is reported, else 0.
Only the Python standard library is required.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REF_CMD = re.compile(
    r"\\(?:ref|eqref|pageref|autoref|vref|[cC]ref|[cC]pageref|labelcref)\*?\{([^}]*)\}"
)
LABEL_CMD = re.compile(r"\\label\{([^}]*)\}")
CITE_CMD = re.compile(
    r"\\[cC]ite[a-zA-Z]*\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}"
)
PACKAGE_CMD = re.compile(
    r"\\(?:usepackage|RequirePackage)(?:\[[^\]]*\])?\{([^}]*)\}"
)
INPUT_CMD = re.compile(r"\\(?:input|include|subfile)\{([^}]*)\}")
GRAPHICS_CMD = re.compile(r"\\includegraphics\*?(?:\[[^\]]*\])?\{([^}]*)\}")
GRAPHICSPATH_CMD = re.compile(r"\\graphicspath\{(.*)\}")
GRAPHICSPATH_DIR = re.compile(r"\{([^{}]*)\}")
BIB_RESOURCE_CMD = re.compile(r"\\(?:bibliography|addbibresource)\{([^}]*)\}")
PDFMETA = re.compile(r"pdf(title|author)\s*=\s*(\{[^{}]*\}|[^,}\]]*)")
DOCUMENTCLASS = re.compile(r"^\s*\\documentclass", re.MULTILINE)
LATEXMK_DIR = re.compile(r"\$(aux_dir|out_dir)\s*=\s*['\"]([^'\"]+)['\"]")
LATEXMKRC_NAMES = ("latexmkrc", ".latexmkrc")
# A real BibTeX entry begins with @type{key in column 0. Anchoring at the start
# of the line (no leading whitespace) keeps nested @type{ tokens from being
# mistaken for entries when they appear indented inside an @comment{...} body
# (e.g. a tool-generated metadata header that mirrors the key list), inside a
# multi-line field value, or in a wrapped @string definition. @comment/@string/
# @preamble at column 0 are recognized only so they can be explicitly skipped.
BIB_ENTRY = re.compile(r"^@(\w+)\s*[{(]\s*([^,\s})]+)", re.IGNORECASE)

# Root candidates whose name marks them as a stale version sibling. "diff"
# covers latexdiff output (main_diff.tex, diff.tex) — a generated artifact,
# never the submission source.
SIBLING_NAME = re.compile(
    r"(?:^|[_\-.])(?:old|backup|bak|staging|stage|draft|copy|orig|arxiv|"
    r"deprecated|obsolete|submitted|diff|v\d+)(?:$|[_\-.])",
    re.IGNORECASE,
)

# Path components that conventionally hold auxiliary, non-manuscript roots
# (response letters, reviewer material, scratch drafts) rather than the paper
# itself. Matched against any part of a candidate's path.
AUX_ROOT_NAME = re.compile(
    r"(?:^|[_\-.])(?:extra|scratch|response|responses|rebuttal|"
    r"peer[_\-]?review|reviews?|cover[_\-]?letter)(?:$|[_\-.])",
    re.IGNORECASE,
)

DEPRECATED_PACKAGES = {
    "epsfig": "use graphicx",
    "psfig": "use graphicx",
    "subfigure": "use subcaption (or the journal's approved alternative)",
    "subfig": "use subcaption unless the journal template requires subfig",
    "doublespace": "use setspace",
    "fancyheadings": "use fancyhdr",
    "times": "use newtxtext/newtxmath if the template allows font changes",
    "txfonts": "use newtxtext/newtxmath",
    "pslatex": "use newtxtext/newtxmath",
    "epsf": "use graphicx",
}

OLD_FONT_CMD = re.compile(r"\\(bf|it|rm|tt|sf|sc|em)\b")
MATH_FONT_SUGGESTION = {
    "rm": "\\mathrm", "bf": "\\mathbf", "it": "\\mathit",
    "tt": "\\mathtt", "sf": "\\mathsf",
}
DOUBLE_DOLLAR = re.compile(r"\$\$")
# "Fig. 2", "Eq.~(3)", "Table 1", "Sec. 4" typed as literal text instead of \ref.
# A separator (period, tilde, or space) is required so label names and file
# names like fig2_final.pdf do not match.
HARDCODED_REF = re.compile(
    r"\b(Fig|Figs|Eq|Eqs|Table|Tab|Sec|Section|Figure|Equation|Chapter|Appendix)"
    r"(?:\.\s*|\.?~|\s+)\(?\d", re.IGNORECASE
)
# {\bf Theorem 1} / \textbf{Definition 2.} style pseudo-environments
PSEUDO_THEOREM = re.compile(
    r"(?:\\textbf\{|\{\\bf(?:series)?\s)\s*"
    r"(Theorem|Lemma|Proposition|Corollary|Definition|Remark|Assumption|"
    r"Conjecture|Example|Algorithm|Claim|Proof)\b",
    re.IGNORECASE,
)
OPAQUE_LABEL = re.compile(
    r"^(?:(?:eq|fig|tab|table|sec|app|thm|lem)[:_-]?)?\d+[a-z]?$", re.IGNORECASE
)
ABSOLUTE_PATH = re.compile(
    r"\\(?:includegraphics|input|include|bibliography|lstinputlisting)"
    r"(?:\[[^\]]*\])?\{(/(?:home|Users|tmp|mnt|media)/[^}]*|[A-Za-z]:[\\/][^}]*)\}"
)
COMMENT_NOTE = re.compile(r"\b(TODO|FIXME|XXX|HACK|PRIVATE|CONFIDENTIAL)\b", re.IGNORECASE)

# Draft-mode artifacts that must not survive into a submitted version.
DRAFT_NOTE_PACKAGES = {
    "todonotes": "renders margin/inline to-do notes in the PDF",
    "fixme": "renders FiXme draft annotations in the PDF",
    "changes": "renders tracked-change markup in the PDF",
    "trackchanges": "renders tracked-change markup in the PDF",
}
DRAFT_NOTE_CMD = re.compile(
    r"\\(todo|missingfigure|fxnote|fxwarning|fxerror|fxfatal|added|deleted|replaced)\b"
)
DRAFT_CLASS_OPTION = re.compile(r"\\documentclass\s*\[[^\]]*\bdraft\b[^\]]*\]")
PLACEHOLDER_TEXT = re.compile(r"\\(?:lipsum|blindtext|Blindtext)\b|lorem ipsum", re.IGNORECASE)

# Invisible or lookalike Unicode characters that break compiles or typeset
# wrongly; they usually arrive via copy-paste from word processors or PDFs.
SUSPICIOUS_CHARS = {
    "\u00a0": "non-breaking space (U+00A0)",
    "\u00ad": "soft hyphen (U+00AD)",
    "\u200b": "zero-width space (U+200B)",
    "\u200c": "zero-width non-joiner (U+200C)",
    "\u200d": "zero-width joiner (U+200D)",
    "\u2060": "word joiner (U+2060)",
    "\ufeff": "zero-width no-break space / BOM (U+FEFF)",
}

# DOI field value, tolerating quotes/braces and a resolver-URL prefix.
BIB_DOI_FIELD = re.compile(
    r'^\s*doi\s*=\s*["{]?\s*(?:https?://(?:dx\.)?doi\.org/)?([^\s"},]+)',
    re.IGNORECASE,
)

STANDARD_LABEL_PREFIXES = "eq:, fig:, tab:, sec:, app:, thm:, alg:"

BEGIN_ENV = re.compile(r"\\begin\{(\w+\*?)\}")
END_ENV = re.compile(r"\\end\{(\w+\*?)\}")
VERBATIM_ENVS = {"verbatim", "verbatim*", "lstlisting", "minted", "comment",
                 "filecontents", "filecontents*"}
TABLE_ENVS = {"table", "table*"}
MATH_ENVS = {"equation", "equation*", "align", "align*", "gather", "gather*",
             "multline", "multline*", "alignat", "alignat*", "flalign",
             "flalign*", "eqnarray", "eqnarray*", "displaymath", "math",
             "cases", "aligned", "gathered", "split"}
IMG_EXTS = (".pdf", ".png", ".jpg", ".jpeg", ".eps", ".ps")

LOG_PDF_VERSION = re.compile(r"found PDF version <([\d.]+)>, but at most version <([\d.]+)>")
LOG_PDF_FILE = re.compile(r"\(file ([^)]+)\)")
LOG_MISSING_FILE = re.compile(r"LaTeX Error: File `([^']+)' not found")


def strip_comment(line):
    """Split a line into (code, comment) honoring escaped percent signs."""
    out = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\":
            out.append(line[i : i + 2])
            i += 2
            continue
        if ch == "%":
            return "".join(out), line[i + 1 :]
        out.append(ch)
        i += 1
    return "".join(out), None


def math_map(code, carry):
    """Per-character math-mode flags for a comment-stripped line.

    Tracks $...$, $$...$$ (single toggle per $$), and \\[ \\] / \\( \\).
    Returns (flags, carry_for_next_line). Environment-based math is layered
    on separately by the caller.
    """
    flags = [carry] * len(code)
    m = carry
    i = 0
    while i < len(code):
        if code[i] == "\\" and i + 1 < len(code):
            nxt = code[i + 1]
            if nxt in "[(":
                m = True
            elif nxt in "])":
                m = False
            else:
                flags[i] = flags[i + 1] = m
            i += 2
            continue
        if code[i] == "$":
            if i + 1 < len(code) and code[i + 1] == "$":
                m = not m
                i += 2
                continue
            m = not m
            i += 1
            continue
        flags[i] = m
        i += 1
    return flags, m


class Findings:
    SEVERITIES = ("ERROR", "WARN", "INFO")

    def __init__(self):
        self.items = []
        self._seen = set()

    def add(self, severity, category, message, path=None, line=None):
        key = (severity, category, message, str(path) if path else None, line)
        if key in self._seen:
            return
        self._seen.add(key)
        self.items.append(
            {
                "severity": severity,
                "category": category,
                "message": message,
                "file": str(path) if path else None,
                "line": line,
            }
        )

    def report_text(self):
        lines = []
        for severity in self.SEVERITIES:
            group = [f for f in self.items if f["severity"] == severity]
            if not group:
                continue
            lines.append(f"== {severity} ({len(group)}) ==")
            for f in sorted(group, key=lambda x: (x["category"], x["file"] or "", x["line"] or 0)):
                loc = f"{f['file']}:{f['line']}: " if f["file"] and f["line"] else (
                    f"{f['file']}: " if f["file"] else ""
                )
                lines.append(f"  [{f['category']}] {loc}{f['message']}")
            lines.append("")
        if not self.items:
            lines.append("No findings. All deterministic checks passed.")
        return "\n".join(lines)


class RootContext:
    """Everything collected while scanning one root's \\input closure."""

    def __init__(self, root):
        self.root = root
        self.labels = defaultdict(list)
        self.refs = defaultdict(list)
        self.cites = defaultdict(list)
        self.packages = defaultdict(list)
        self.graphics = []       # (target, path, lineno)
        self.gpaths = []         # \graphicspath entries
        self.bib_names = []      # \bibliography / \addbibresource arguments
        self.meta = {}           # pdftitle / pdfauthor values
        self.font_hits = defaultdict(list)  # (cmd, in_math) -> [(path, lineno)]


def gather_files(dirs):
    tex, bib, latexmkrc = [], [], []
    for d in dirs:
        tex.extend(sorted(d.rglob("*.tex")))
        bib.extend(sorted(d.rglob("*.bib")))
        for name in LATEXMKRC_NAMES:
            p = d / name
            if p.is_file():
                latexmkrc.append(p)
    return tex, bib, latexmkrc


def in_environment(env_stack, names):
    return any(e in names for e in env_stack)


def pop_env(env_stack, env):
    for i in range(len(env_stack) - 1, -1, -1):
        if env_stack[i] == env:
            del env_stack[i:]
            return


def scan_tex(path, findings, ctx):
    try:
        text = path.read_text(errors="replace")
    except OSError as exc:
        findings.add("WARN", "io", f"could not read file: {exc}", path)
        return

    env_stack = []
    in_display_math = False   # $$-block state for the plain-TeX warning
    math_carry = False        # $ / $$ / \[ state carried across lines
    draft_cmds = defaultdict(list)   # \todo/\added/... -> [lineno]
    char_hits = defaultdict(list)    # suspicious-char description -> [lineno]

    for lineno, raw in enumerate(text.splitlines(), start=1):
        code, comment = strip_comment(raw)

        if comment and COMMENT_NOTE.search(comment):
            findings.add(
                "WARN", "bundle",
                f"comment contains a private-note marker: %{comment.strip()[:60]}",
                path, lineno,
            )

        if in_environment(env_stack, VERBATIM_ENVS):
            for m in END_ENV.finditer(code):
                if m.group(1) in env_stack:
                    pop_env(env_stack, m.group(1))
            continue

        for m in LABEL_CMD.finditer(code):
            for key in (k.strip() for k in m.group(1).split(",")):
                if key:
                    ctx.labels[key].append((path, lineno))
                if key and OPAQUE_LABEL.match(key):
                    findings.add(
                        "INFO", "semantic",
                        f"opaque label '{key}'; prefer semantic names "
                        f"({STANDARD_LABEL_PREFIXES} + description, e.g. fig:phase-diagram)",
                        path, lineno,
                    )
        for m in REF_CMD.finditer(code):
            for key in (k.strip() for k in m.group(1).split(",")):
                if key:
                    ctx.refs[key].append((path, lineno))
        for m in CITE_CMD.finditer(code):
            for key in (k.strip() for k in m.group(1).split(",")):
                if key and key != "*":
                    ctx.cites[key].append((path, lineno))
        for m in PACKAGE_CMD.finditer(code):
            for pkg in (p.strip() for p in m.group(1).split(",")):
                if pkg:
                    ctx.packages[pkg].append((path, lineno))
        for m in GRAPHICS_CMD.finditer(code):
            ctx.graphics.append((m.group(1).strip(), path, lineno))
        for m in GRAPHICSPATH_CMD.finditer(code):
            ctx.gpaths.extend(GRAPHICSPATH_DIR.findall(m.group(1)))
        for m in BIB_RESOURCE_CMD.finditer(code):
            ctx.bib_names.extend(n.strip() for n in m.group(1).split(",") if n.strip())
        for m in PDFMETA.finditer(code):
            key = m.group(1)
            val = (m.group(2) or "").strip().strip("{}").strip().rstrip(",")
            if key not in ctx.meta or (not ctx.meta[key] and val):
                ctx.meta[key] = val

        for m in BEGIN_ENV.finditer(code):
            env = m.group(1)
            env_stack.append(env)
            if env in ("eqnarray", "eqnarray*"):
                findings.add(
                    "WARN", "semantic",
                    "eqnarray is deprecated; use align/equation from amsmath",
                    path, lineno,
                )

        if GRAPHICS_CMD.search(code) and in_environment(env_stack, TABLE_ENVS):
            findings.add(
                "WARN", "semantic",
                "table content included as an image; encode tables as LaTeX source "
                "so they can be parsed, searched, and read by assistive tools",
                path, lineno,
            )
        for _ in DOUBLE_DOLLAR.finditer(code):
            in_display_math = not in_display_math
            if in_display_math:
                findings.add(
                    "WARN", "semantic",
                    "$$...$$ display math is plain-TeX syntax; use \\[...\\] or an "
                    "equation environment (referenceable and parser-friendly)",
                    path, lineno,
                )
        m = PSEUDO_THEOREM.search(code)
        if m:
            findings.add(
                "WARN", "semantic",
                f"'{m.group(1)}' formatted with bold text instead of a theorem-style "
                "environment; use amsthm/journal environments so structure is machine-readable",
                path, lineno,
            )

        flags, math_carry = math_map(code, math_carry)
        env_math = in_environment(env_stack, MATH_ENVS)
        for m in OLD_FONT_CMD.finditer(code):
            in_math = env_math or (flags[m.start()] if m.start() < len(flags) else math_carry)
            ctx.font_hits[(m.group(1), in_math)].append((path, lineno))

        for m in DRAFT_NOTE_CMD.finditer(code):
            draft_cmds[m.group(1)].append(lineno)
        for ch, what in SUSPICIOUS_CHARS.items():
            if ch in code:
                char_hits[what].append(lineno)
        if DRAFT_CLASS_OPTION.search(code):
            findings.add(
                "WARN", "draft",
                "\\documentclass loads the 'draft' option; figures render as "
                "boxes and overfull lines are marked — remove before submission",
                path, lineno,
            )
        m = PLACEHOLDER_TEXT.search(code)
        if m:
            findings.add(
                "WARN", "draft",
                f"placeholder text '{code[m.start():m.end()]}' left in the source",
                path, lineno,
            )

        m = HARDCODED_REF.search(code)
        if m:
            findings.add(
                "WARN", "semantic",
                f"possible hardcoded cross-reference '{code[m.start():m.end()]}...'; "
                "use \\ref/\\eqref/\\cref so numbering stays correct and linked",
                path, lineno,
            )
        m = ABSOLUTE_PATH.search(code)
        if m:
            findings.add(
                "ERROR", "bundle",
                f"absolute local path '{m.group(1)}' will break any other build "
                "environment, including arXiv",
                path, lineno,
            )
        for m in END_ENV.finditer(code):
            if m.group(1) in env_stack:
                pop_env(env_stack, m.group(1))

    for cmd, lines in sorted(draft_cmds.items()):
        shown = ", ".join(str(l) for l in lines[:5])
        extra = f" ({len(lines)} occurrences; lines {shown}, ...)" if len(lines) > 5 else ""
        findings.add(
            "WARN", "draft",
            f"draft note command \\{cmd} in the source{extra}; resolve and "
            "remove before submission",
            path, lines[0],
        )
    for what, lines in sorted(char_hits.items()):
        shown = ", ".join(str(l) for l in lines[:5])
        extra = f" ({len(lines)} lines; first at {shown}, ...)" if len(lines) > 5 else (
            f" (lines {shown})" if len(lines) > 1 else ""
        )
        findings.add(
            "WARN", "hygiene",
            f"invisible/pasted Unicode character {what} in the source{extra}; "
            "usually copy-paste debris — replace with the intended LaTeX",
            path, lines[0],
        )


def resolve_closure(root, findings):
    """Follow \\input/\\include/\\subfile from the root. Returns file list."""
    closure, seen, queue = [], set(), [root]
    while queue:
        f = queue.pop(0)
        rf = f.resolve()
        if rf in seen:
            continue
        seen.add(rf)
        closure.append(f)
        try:
            text = f.read_text(errors="replace")
        except OSError:
            continue  # scan_tex reports the read failure
        for lineno, raw in enumerate(text.splitlines(), start=1):
            code, _ = strip_comment(raw)
            for m in INPUT_CMD.finditer(code):
                name = m.group(1).strip()
                if not name or name.startswith("/"):
                    continue  # absolute paths flagged in scan_tex
                candidates = [name] if name.endswith(".tex") else [name + ".tex", name]
                target = None
                for base in (root.parent, f.parent):
                    for c in candidates:
                        p = base / c
                        if p.is_file():
                            target = p
                            break
                    if target:
                        break
                if target:
                    queue.append(target)
                else:
                    findings.add(
                        "ERROR", "bundle",
                        f"\\input/\\include target '{name}' not found relative to "
                        f"{root.parent}",
                        f, lineno,
                    )
    return closure


def resolve_ci(base, rel):
    """Resolve rel under base matching each path component case-insensitively."""
    cur = base
    for part in Path(rel).parts:
        if not cur.is_dir():
            return None
        try:
            matches = [c for c in cur.iterdir() if c.name.lower() == part.lower()]
        except OSError:
            return None
        if not matches:
            return None
        cur = matches[0]
    return cur


def check_graphics(ctx, findings):
    bases = [ctx.root.parent] + [
        ctx.root.parent / g.strip() for g in ctx.gpaths if g.strip()
    ]
    for target, path, lineno in ctx.graphics:
        t = target.strip()
        if not t or t.startswith("/") or re.match(r"[A-Za-z]:[\\/]", t):
            continue  # absolute paths already flagged as ERROR
        names = [t]
        if Path(t).suffix.lower() not in IMG_EXTS:
            names += [t + e for e in IMG_EXTS]
        if any((b / n).is_file() for b in bases for n in names):
            continue
        ci_hit = None
        for b in bases:
            for n in names:
                hit = resolve_ci(b, n)
                if hit is not None and hit.is_file():
                    ci_hit = hit
                    break
            if ci_hit:
                break
        if ci_hit:
            findings.add(
                "ERROR", "figure-file",
                f"figure '{t}' does not exist with this exact case; on disk it is "
                f"'{ci_hit.name}'. Case-sensitive builds (arXiv, Linux) will fail",
                path, lineno,
            )
        else:
            searched = ", ".join(str(b) for b in bases)
            findings.add(
                "ERROR", "figure-file",
                f"figure file '{t}' not found (searched: {searched})",
                path, lineno,
            )


def check_orphan_images(dirs, all_graphics, tex_files, findings):
    """Flag bundled image files no scanned root ever includes (INFO).

    Compared by case-folded stem so a case-mismatched include (already an
    ERROR) does not double-report as an orphan. Images sharing a stem with a
    .tex file are skipped: they are compiled output, not figure assets.
    """
    referenced = set()
    for target, _, _ in all_graphics:
        t = Path(target.strip())
        referenced.add(t.stem.lower() if t.suffix.lower() in IMG_EXTS else t.name.lower())
    tex_stems = {p.stem.lower() for p in tex_files}
    for d in dirs:
        for ext in IMG_EXTS:
            for img in sorted(d.rglob(f"*{ext}")):
                if img.stem.lower() in referenced or img.stem.lower() in tex_stems:
                    continue
                findings.add(
                    "INFO", "bundle",
                    f"image file '{img.name}' is never included by any audited "
                    "root; remove it from the public bundle if it is unused",
                    img,
                )


def check_metadata(ctx, findings):
    if "hyperref" in ctx.packages:
        where, line = ctx.packages["hyperref"][0]
        for key in ("title", "author"):
            if key not in ctx.meta:
                findings.add(
                    "WARN", "metadata",
                    f"hyperref is loaded but pdf{key} is never set; PDF metadata is "
                    "how indexers, readers, and search engines identify the paper",
                    where, line,
                )
            elif not ctx.meta[key]:
                findings.add(
                    "WARN", "metadata",
                    f"pdf{key} is set but empty; populate it or remove the empty assignment",
                    where, line,
                )
    else:
        findings.add(
            "INFO", "metadata",
            "hyperref is not loaded; the compiled PDF will carry no "
            "pdftitle/pdfauthor metadata (fine only if the journal template manages it)",
            ctx.root,
        )


def report_font_hits(ctx, findings):
    for (cmd, in_math), hits in sorted(ctx.font_hits.items()):
        if in_math:
            severity = "INFO"
            suggestion = MATH_FONT_SUGGESTION.get(cmd)
            base = (
                f"\\{cmd} inside math; use {suggestion}{{...}}" if suggestion
                else f"\\{cmd} inside math; use the corresponding \\math* command"
            )
        else:
            severity = "WARN"
            base = (
                f"two-letter font command \\{cmd} in text; use \\textbf/\\textit/... "
                "or \\bfseries-style declarations"
            )
        if len(hits) <= 4:
            for path, lineno in hits:
                findings.add(severity, "hygiene", base, path, lineno)
        else:
            path, lineno = hits[0]
            uniq = list(dict.fromkeys(l for _, l in hits))
            shown = ", ".join(str(l) for l in uniq[:5])
            findings.add(
                severity, "hygiene",
                f"{base} ({len(hits)} occurrences; first at lines {shown}, ...)",
                path, lineno,
            )


def build_log(root, latexmkrc_files, log_dir=None):
    """Return where latexmk writes root's log: --log-dir, else the nearest
    latexmkrc's $aux_dir (else $out_dir), else beside the root."""
    name = root.with_suffix(".log").name
    if log_dir is not None:
        return Path(log_dir) / name
    here = root.resolve().parent
    candidates = set(latexmkrc_files) | {root.parent / n for n in LATEXMKRC_NAMES}
    for rc in sorted(candidates, key=lambda p: len(p.resolve().parts), reverse=True):
        if not rc.is_file() or not here.is_relative_to(rc.parent.resolve()):
            continue
        try:
            text = re.sub(r"#.*", "", rc.read_text(errors="replace"))
        except OSError:
            continue
        dirs = dict(LATEXMK_DIR.findall(text))
        configured = dirs.get("aux_dir") or dirs.get("out_dir")
        if configured:
            return rc.parent / configured / name
        break  # the nearest latexmkrc keeps build output beside the source
    return root.with_suffix(".log")


def scan_log(root, findings, log):
    if not log.is_file():
        findings.add(
            "INFO", "log",
            f"no build log ({log}) found; log-based checks (embedded PDF "
            "versions, stuck floats, overfull boxes) were skipped — compile first "
            "for a full preflight",
            root,
        )
        return
    try:
        text = log.read_text(errors="replace")
    except OSError as exc:
        findings.add("WARN", "io", f"could not read log: {exc}", log)
        return
    for lineno, line in enumerate(text.splitlines(), start=1):
        m = LOG_PDF_VERSION.search(line)
        if m:
            fm = LOG_PDF_FILE.search(line)
            which = f" '{fm.group(1)}'" if fm else ""
            findings.add(
                "WARN", "log",
                f"embedded figure{which} uses PDF version {m.group(1)} but the "
                f"document allows at most {m.group(2)}; re-export the figure or "
                "set \\pdfminorversion — some journals and validators reject this",
                log, lineno,
            )
        if "Too many unprocessed floats" in line:
            findings.add(
                "WARN", "log",
                "'Too many unprocessed floats' — figures/tables are piling up "
                "undelivered; check float placement before submission",
                log, lineno,
            )
        m = LOG_MISSING_FILE.search(line)
        if m:
            findings.add(
                "ERROR", "log",
                f"build log reports missing file '{m.group(1)}'",
                log, lineno,
            )
    overfull = len(re.findall(r"Overfull \\[hv]box", text))
    if overfull:
        findings.add(
            "INFO", "log",
            f"{overfull} overfull box(es) reported in the build log; check none "
            "affects the final layout",
            log,
        )


def scan_bib(path, findings, bib_keys):
    try:
        text = path.read_text(errors="replace")
    except OSError as exc:
        findings.add("WARN", "io", f"could not read file: {exc}", path)
        return
    current_key = None            # entry the scanner is inside, for DOI fields
    dois = defaultdict(list)      # normalized DOI -> [(entry key, lineno)]
    for lineno, raw in enumerate(text.splitlines(), start=1):
        m = BIB_ENTRY.match(raw)  # column-0 anchored: one entry per opening line
        if m:
            kind, key = m.group(1).lower(), m.group(2)
            current_key = None
            if kind not in ("string", "comment", "preamble"):
                bib_keys[key].append((path, lineno))
                current_key = key
            continue
        if current_key:
            dm = BIB_DOI_FIELD.match(raw)
            if dm:
                dois[dm.group(1).lower()].append((current_key, lineno))
    # Two entries sharing a DOI are almost always the same reference imported
    # twice under different keys — a duplicate the key check cannot see.
    for doi, uses in sorted(dois.items()):
        keys = sorted({k for k, _ in uses})
        if len(keys) > 1:
            findings.add(
                "WARN", "citation",
                f"entries {', '.join(keys)} share DOI '{doi}'; likely the same "
                "reference under different keys — merge them",
                path, uses[0][1],
            )


def resolve_bibs(ctx, dir_bibs, findings):
    """Bib files declared by this root, falling back to all discovered .bib."""
    if not ctx.bib_names:
        return list(dir_bibs)
    resolved = []
    by_name = {p.name: p for p in dir_bibs}
    for name in ctx.bib_names:
        fname = name if name.endswith(".bib") else name + ".bib"
        p = ctx.root.parent / fname
        if p.is_file():
            resolved.append(p)
        elif Path(fname).name in by_name:
            resolved.append(by_name[Path(fname).name])
        else:
            findings.add(
                "ERROR", "citation",
                f"bibliography file '{fname}' not found",
                ctx.root,
            )
    return resolved


def cross_check_refs(ctx, findings):
    for key, uses in sorted(ctx.refs.items()):
        if key not in ctx.labels:
            path, lineno = uses[0]
            extra = f" ({len(uses)} uses)" if len(uses) > 1 else ""
            findings.add("ERROR", "xref", f"reference to undefined label '{key}'{extra}", path, lineno)
    for key, defs in sorted(ctx.labels.items()):
        if len(defs) > 1:
            locs = ", ".join(f"{p.name}:{l}" for p, l in defs)
            findings.add("ERROR", "xref", f"label '{key}' defined {len(defs)} times ({locs})", defs[0][0], defs[0][1])
        if key not in ctx.refs:
            findings.add("INFO", "xref", f"label '{key}' is never referenced", defs[0][0], defs[0][1])


def cross_check_cites(ctx, bib_keys, have_bib, findings):
    if have_bib:
        for key, uses in sorted(ctx.cites.items()):
            if key not in bib_keys:
                path, lineno = uses[0]
                findings.add("ERROR", "citation", f"citation key '{key}' not found in any .bib file", path, lineno)
        for key, defs in sorted(bib_keys.items()):
            if len(defs) > 1:
                locs = ", ".join(f"{p.name}:{l}" for p, l in defs)
                findings.add("ERROR", "citation", f"bib key '{key}' defined {len(defs)} times ({locs})", defs[0][0], defs[0][1])
    elif ctx.cites:
        findings.add(
            "INFO", "citation",
            f"{len(ctx.cites)} citation keys found but no .bib file; skipping citation "
            "checks (bibliography may be inline via thebibliography or a .bbl)",
        )


def check_packages(ctx, findings):
    for pkg, uses in sorted(ctx.packages.items()):
        if pkg in DEPRECATED_PACKAGES:
            path, lineno = uses[0]
            findings.add(
                "WARN", "package",
                f"deprecated/discouraged package '{pkg}'; {DEPRECATED_PACKAGES[pkg]}",
                path, lineno,
            )
        if pkg in DRAFT_NOTE_PACKAGES:
            path, lineno = uses[0]
            findings.add(
                "WARN", "draft",
                f"draft-stage package '{pkg}' {DRAFT_NOTE_PACKAGES[pkg]}; "
                "remove it (and its commands) before submission",
                path, lineno,
            )
        if pkg == "lineno":
            path, lineno = uses[0]
            findings.add(
                "INFO", "draft",
                "'lineno' is loaded; line numbers are wanted for review copies "
                "but must usually be dropped for the final version — confirm "
                "which one this build is",
                path, lineno,
            )


def latexmk_roots(latexmkrc_files):
    names = []
    for p in latexmkrc_files:
        try:
            text = p.read_text(errors="replace")
        except OSError:
            continue
        names.extend(re.findall(r"['\"]([\w./-]+\.tex)['\"]", text))
    return names


def choose_roots(candidates, latexmk_names, findings):
    """Split root candidates into active roots and skipped version siblings."""
    forced = {Path(n).name for n in latexmk_names}
    active, skipped, reasons = [], [], {}
    for p in candidates:
        if p.name in forced:
            active.append(p)
        elif any(SIBLING_NAME.search(part) for part in p.parts):
            skipped.append(p)
            reasons[p] = ("a version sibling (old/backup/staging/arxiv/vN or "
                          "latexdiff *_diff naming)")
        elif any(AUX_ROOT_NAME.search(part) for part in p.parts):
            skipped.append(p)
            reasons[p] = ("an auxiliary document (response letter, reviewer "
                          "material, or scratch draft), not the submission")
        else:
            active.append(p)
    if not active and skipped:
        # Everything matched a skip pattern (e.g. an arxiv-submission/ checkout).
        # Better to audit them all than nothing.
        active, skipped = skipped, []
    for p in skipped:
        findings.add(
            "INFO", "corpus",
            f"root candidate '{p}' looks like {reasons[p]} and was skipped; "
            "remove stale/auxiliary copies from the public bundle, or pass "
            "--main to audit this file instead",
            p,
        )
    return active, skipped


def audit_root(root, dir_bibs, findings, parsed_bibs, log):
    ctx = RootContext(root)
    closure = resolve_closure(root, findings)
    for f in closure:
        scan_tex(f, findings, ctx)

    cross_check_refs(ctx, findings)
    bib_files = resolve_bibs(ctx, dir_bibs, findings)
    bib_keys = defaultdict(list)
    for p in bib_files:
        rp = p.resolve()
        if rp not in parsed_bibs:
            keys = defaultdict(list)
            scan_bib(p, findings, keys)
            parsed_bibs[rp] = keys
        for key, defs in parsed_bibs[rp].items():
            bib_keys[key].extend(defs)
    cross_check_cites(ctx, bib_keys, bool(bib_files), findings)
    check_packages(ctx, findings)
    check_graphics(ctx, findings)
    check_metadata(ctx, findings)
    report_font_hits(ctx, findings)
    scan_log(root, findings, log)
    return ctx, closure, bib_files


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("targets", nargs="*", default=["."],
                        help="directories or .tex/.bib files (default: .)")
    parser.add_argument("--main", dest="main_file",
                        help="treat FILE as the manuscript root; skips root auto-detection")
    parser.add_argument("--log-dir",
                        help="build-log directory relative to the working directory "
                             "(default: latexmkrc $aux_dir or $out_dir, else beside each root)")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = parser.parse_args(argv)

    findings = Findings()
    explicit_tex, dirs = [], []
    for target in args.targets or ["."]:
        p = Path(target)
        if p.is_dir():
            dirs.append(p)
        elif p.suffix == ".tex":
            explicit_tex.append(p)
        elif p.suffix == ".bib":
            pass  # discovered via dirs or \bibliography; accepted for compatibility
        else:
            print(f"warning: ignoring unrecognized target {target}", file=sys.stderr)
    if not dirs and not explicit_tex:
        dirs = [Path(".")]

    dir_tex, dir_bibs, latexmkrc_files = gather_files(dirs)

    if args.main_file:
        root_path = Path(args.main_file)
        if not root_path.is_file():
            print(f"error: --main file {root_path} not found", file=sys.stderr)
            return 2
        roots, skipped = [root_path], []
    elif explicit_tex:
        roots, skipped = explicit_tex, []
    else:
        candidates = []
        for p in dir_tex:
            try:
                if DOCUMENTCLASS.search(p.read_text(errors="replace")):
                    candidates.append(p)
            except OSError:
                continue
        if candidates:
            roots, skipped = choose_roots(candidates, latexmk_roots(latexmkrc_files), findings)
        else:
            roots, skipped = [], []

    parsed_bibs = {}
    scanned = set()
    all_cites = set()
    all_graphics = []
    used_bibs = {}
    if roots:
        for root in roots:
            log = build_log(root, latexmkrc_files, args.log_dir)
            ctx, closure, bib_files = audit_root(root, dir_bibs, findings, parsed_bibs, log)
            scanned.update(p.resolve() for p in closure)
            all_cites.update(ctx.cites)
            all_graphics.extend(ctx.graphics)
            for p in bib_files:
                used_bibs[p.resolve()] = p
        if dirs:
            check_orphan_images(dirs, all_graphics, dir_tex, findings)
        # Unused-entry check runs globally: an entry cited by any root counts.
        for rp, p in sorted(used_bibs.items()):
            for key, defs in sorted(parsed_bibs.get(rp, {}).items()):
                if key not in all_cites:
                    findings.add("INFO", "citation", f"bib entry '{key}' is never cited",
                                 defs[0][0], defs[0][1])
        for p in dir_tex:
            if p.resolve() not in scanned and p not in skipped:
                findings.add(
                    "INFO", "corpus",
                    "not reachable from any manuscript root; not audited "
                    "(stale file, or a root the auto-detection missed — see --main)",
                    p,
                )
    else:
        # No \documentclass anywhere (e.g. a directory of subfiles): fall back
        # to scanning everything as one corpus.
        if not dir_tex:
            print("No .tex files found.", file=sys.stderr)
            return 2
        findings.add(
            "INFO", "corpus",
            "no \\documentclass found in any .tex file; scanning all files as one corpus",
        )
        ctx = RootContext(dir_tex[0])
        for f in dir_tex:
            scan_tex(f, findings, ctx)
        scanned.update(p.resolve() for p in dir_tex)
        cross_check_refs(ctx, findings)
        bib_keys = defaultdict(list)
        for p in dir_bibs:
            scan_bib(p, findings, bib_keys)
        cross_check_cites(ctx, bib_keys, bool(dir_bibs), findings)
        for key, defs in sorted(bib_keys.items()):
            if key not in ctx.cites:
                findings.add("INFO", "citation", f"bib entry '{key}' is never cited",
                             defs[0][0], defs[0][1])
        check_packages(ctx, findings)
        check_graphics(ctx, findings)
        if dirs:
            check_orphan_images(dirs, ctx.graphics, dir_tex, findings)
        report_font_hits(ctx, findings)

    result = {
        "roots": [str(r) for r in roots],
        "skipped_roots": [str(p) for p in skipped],
        "files_scanned": sorted(str(p) for p in scanned),
        "findings": findings.items,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        root_names = ", ".join(str(r) for r in roots) if roots else "(none detected)"
        print(f"Roots: {root_names}")
        if skipped:
            print(f"Skipped version siblings: {', '.join(str(p) for p in skipped)}")
        print(f"Scanned {len(scanned)} .tex file(s).\n")
        print(findings.report_text())

    return 1 if any(f["severity"] == "ERROR" for f in findings.items) else 0


if __name__ == "__main__":
    sys.exit(main())
