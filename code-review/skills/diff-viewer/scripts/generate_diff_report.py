#!/usr/bin/env python3
"""Render the current working-tree git diff as a browser-readable HTML report."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = SCRIPT_DIR.parent / "assets" / "diff-template.html"

FILE_HEADER_RE = re.compile(r"^diff --git a/(?P<old>.+?) b/(?P<new>.+)$")
HUNK_HEADER_RE = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? "
    r"\+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@"
)
ID_TOKEN_RE = re.compile(r"[^A-Za-z0-9_-]+")
LANG_TOKEN_RE = re.compile(r"[^A-Za-z0-9_.+-]+")


@dataclass
class Line:
    kind: str
    content: str
    old_no: Optional[int] = None
    new_no: Optional[int] = None


@dataclass
class Hunk:
    header: str
    old_start: int
    new_start: int
    old_count: int = 0
    new_count: int = 0
    lines: List[Line] = field(default_factory=list)


@dataclass
class FileDiff:
    old_path: str
    new_path: str
    status: str
    hunks: List[Hunk] = field(default_factory=list)


def _strip_diff_path(path: str) -> str:
    if path == "/dev/null":
        return path
    if path.startswith(("a/", "b/")):
        return path[2:]
    return path


def _count_value(raw: Optional[str]) -> int:
    return 1 if raw is None else int(raw)


def parse_git_diff(diff_text: str) -> List[FileDiff]:
    files: List[FileDiff] = []
    lines = diff_text.splitlines()
    i = 0

    while i < len(lines):
        match = FILE_HEADER_RE.match(lines[i])
        if not match:
            i += 1
            continue

        file_diff = FileDiff(
            old_path=match.group("old"),
            new_path=match.group("new"),
            status="modified",
        )
        i += 1

        while i < len(lines) and not lines[i].startswith(("@@", "diff --git")):
            header = lines[i]
            if header.startswith("new file mode"):
                file_diff.status = "added"
            elif header.startswith("deleted file mode"):
                file_diff.status = "deleted"
            elif header.startswith("rename from "):
                file_diff.status = "renamed"
                file_diff.old_path = header[len("rename from ") :]
            elif header.startswith("rename to "):
                file_diff.status = "renamed"
                file_diff.new_path = header[len("rename to ") :]
            elif header.startswith("--- "):
                file_diff.old_path = _strip_diff_path(header[4:])
            elif header.startswith("+++ "):
                file_diff.new_path = _strip_diff_path(header[4:])
            i += 1

        if file_diff.old_path == "/dev/null":
            file_diff.status = "added"
        elif file_diff.new_path == "/dev/null":
            file_diff.status = "deleted"

        while i < len(lines) and not lines[i].startswith("diff --git"):
            if lines[i].startswith("@@"):
                hunk, i = parse_hunk(lines, i)
                file_diff.hunks.append(hunk)
            else:
                i += 1

        files.append(file_diff)

    return files


def parse_hunk(lines: List[str], start: int) -> Tuple[Hunk, int]:
    header = lines[start]
    match = HUNK_HEADER_RE.match(header)
    if not match:
        raise ValueError("Bad hunk header at line {}: {!r}".format(start + 1, header))

    old_start = int(match.group("old_start"))
    new_start = int(match.group("new_start"))
    hunk = Hunk(
        header=header,
        old_start=old_start,
        new_start=new_start,
        old_count=_count_value(match.group("old_count")),
        new_count=_count_value(match.group("new_count")),
    )

    old_no = old_start - 1
    new_no = new_start - 1
    i = start + 1

    while i < len(lines):
        raw = lines[i]
        if raw.startswith(("diff --git", "@@")):
            break
        if raw.startswith("\\"):
            i += 1
            continue
        if raw == "":
            break

        marker = raw[0]
        content = raw[1:]
        if marker == "-":
            old_no += 1
            hunk.lines.append(Line(kind="del", content=content, old_no=old_no))
        elif marker == "+":
            new_no += 1
            hunk.lines.append(Line(kind="add", content=content, new_no=new_no))
        elif marker == " ":
            old_no += 1
            new_no += 1
            hunk.lines.append(Line(kind="ctx", content=content, old_no=old_no, new_no=new_no))
        else:
            break
        i += 1

    return hunk, i


EXT_TO_LANG = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".cs": "csharp",
    ".swift": "swift",
    ".scala": "scala",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    ".fish": "bash",
    ".html": "xml",
    ".htm": "xml",
    ".xml": "xml",
    ".css": "css",
    ".scss": "scss",
    ".sass": "scss",
    ".less": "less",
    ".json": "json",
    ".jsonc": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "ini",
    ".ini": "ini",
    ".md": "markdown",
    ".mdx": "markdown",
    ".sql": "sql",
    ".graphql": "graphql",
    ".gql": "graphql",
    ".dart": "dart",
    ".lua": "lua",
    ".r": "r",
    ".pl": "perl",
    ".vue": "xml",
    ".svelte": "xml",
    ".diff": "diff",
    ".patch": "diff",
}

SPECIAL_FILENAMES = {
    ".bashrc": "bash",
    ".zshrc": "bash",
    ".profile": "bash",
    "Dockerfile": "dockerfile",
    "Containerfile": "dockerfile",
    "Makefile": "makefile",
    "GNUmakefile": "makefile",
    ".gitignore": "plaintext",
    ".gitattributes": "plaintext",
}


def detect_language(path: str) -> str:
    if path == "/dev/null":
        return "plaintext"
    name = Path(path).name
    if name in SPECIAL_FILENAMES:
        return SPECIAL_FILENAMES[name]
    return EXT_TO_LANG.get(Path(name).suffix.lower(), "plaintext")


def escape(text: str) -> str:
    return html.escape(text, quote=True)


def safe_lang(lang: str) -> str:
    return LANG_TOKEN_RE.sub("", lang)[:32] or "plaintext"


def file_display_path(file_diff: FileDiff) -> str:
    if file_diff.status == "deleted":
        return file_diff.old_path
    if file_diff.status == "renamed":
        return "{} -> {}".format(file_diff.old_path, file_diff.new_path)
    return file_diff.new_path


def file_anchor(file_diff: FileDiff, index: int) -> str:
    token = ID_TOKEN_RE.sub("-", file_display_path(file_diff)).strip("-").lower()
    return "file-{}-{}".format(index + 1, token or "diff")


def render_summary(files: List[FileDiff]) -> Dict[str, int]:
    additions = 0
    deletions = 0
    for file_diff in files:
        for hunk in file_diff.hunks:
            additions += sum(1 for line in hunk.lines if line.kind == "add")
            deletions += sum(1 for line in hunk.lines if line.kind == "del")
    return {"files": len(files), "additions": additions, "deletions": deletions}


def _line_code(
    content: str,
    language: str,
    file_index: int,
    highlight_side: str,
    highlight_line: int,
) -> str:
    escaped = escape(content) or "&nbsp;"
    return (
        '<code class="language-{}" data-highlight-file="{}" '
        'data-highlight-side="{}" data-highlight-line="{}">{}</code>'
    ).format(
        safe_lang(language),
        file_index,
        escape(highlight_side),
        highlight_line,
        escaped,
    )


def _row_class(kind: str) -> str:
    return {"add": "line-add", "del": "line-del", "ctx": "line-ctx"}.get(kind, "line-ctx")


def _sign(kind: str) -> str:
    return {"add": "+", "del": "-", "ctx": " "}.get(kind, " ")


def _highlight_refs(file_diff: FileDiff) -> Dict[Tuple[int, str], Tuple[str, int]]:
    refs: Dict[Tuple[int, str], Tuple[str, int]] = {}
    before_index = 0
    after_index = 0
    for hunk in file_diff.hunks:
        for line in hunk.lines:
            if line.kind == "del":
                refs[(id(line), "old")] = ("before", before_index)
                refs[(id(line), "unified")] = ("before", before_index)
                before_index += 1
            elif line.kind == "add":
                refs[(id(line), "new")] = ("after", after_index)
                refs[(id(line), "unified")] = ("after", after_index)
                after_index += 1
            else:
                refs[(id(line), "old")] = ("before", before_index)
                refs[(id(line), "new")] = ("after", after_index)
                refs[(id(line), "unified")] = ("after", after_index)
                before_index += 1
                after_index += 1
    return refs


def render_unified_table(
    file_diff: FileDiff,
    language: Optional[str] = None,
    file_index: int = 0,
) -> str:
    language = language or detect_language(file_diff.new_path)
    refs = _highlight_refs(file_diff)
    rows: List[str] = []
    for hunk in file_diff.hunks:
        rows.append(
            '<tr class="hunk-row"><td colspan="3">{}</td></tr>'.format(escape(hunk.header))
        )
        for line in hunk.lines:
            highlight_side, highlight_line = refs[(id(line), "unified")]
            rows.append(
                '<tr class="{}">'.format(_row_class(line.kind))
                + '<td class="line-no">{}</td>'.format("" if line.old_no is None else line.old_no)
                + '<td class="line-no">{}</td>'.format("" if line.new_no is None else line.new_no)
                + '<td class="code-line"><span class="line-sign">{}</span>{}</td>'.format(
                    escape(_sign(line.kind)),
                    _line_code(
                        line.content,
                        language,
                        file_index,
                        highlight_side,
                        highlight_line,
                    ),
                )
                + "</tr>"
            )
    return (
        '<table class="diff-table unified-table">'
        '<colgroup><col class="line-col"><col class="line-col"><col></colgroup>'
        '<tbody>{}</tbody></table>'.format("".join(rows))
    )


def _split_pairs(lines: List[Line]) -> List[Tuple[str, Optional[Line], Optional[Line]]]:
    pairs: List[Tuple[str, Optional[Line], Optional[Line]]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.kind == "ctx":
            pairs.append(("ctx", line, line))
            i += 1
            continue

        deleted: List[Line] = []
        added: List[Line] = []
        while i < len(lines) and lines[i].kind == "del":
            deleted.append(lines[i])
            i += 1
        while i < len(lines) and lines[i].kind == "add":
            added.append(lines[i])
            i += 1

        for offset in range(max(len(deleted), len(added))):
            left = deleted[offset] if offset < len(deleted) else None
            right = added[offset] if offset < len(added) else None
            pairs.append(("change", left, right))

    return pairs


def _split_cell(
    line: Optional[Line],
    language: str,
    side: str,
    refs: Dict[Tuple[int, str], Tuple[str, int]],
    file_index: int,
) -> str:
    if line is None:
        return '<td class="line-no empty"></td><td class="code-line empty"></td>'
    line_no = line.old_no if side == "old" else line.new_no
    highlight_side, highlight_line = refs[(id(line), side)]
    kind_class = _row_class(line.kind)
    return (
        '<td class="line-no {}">{}</td>'.format(kind_class, "" if line_no is None else line_no)
        + '<td class="code-line {}"><span class="line-sign">{}</span>{}</td>'.format(
            kind_class,
            escape(_sign(line.kind)),
            _line_code(
                line.content,
                language,
                file_index,
                highlight_side,
                highlight_line,
            ),
        )
    )


def render_split_table(
    file_diff: FileDiff,
    language: Optional[str] = None,
    file_index: int = 0,
) -> str:
    language = language or detect_language(file_diff.new_path)
    refs = _highlight_refs(file_diff)
    rows: List[str] = []
    for hunk in file_diff.hunks:
        rows.append(
            '<tr class="hunk-row"><td colspan="5">{}</td></tr>'.format(escape(hunk.header))
        )
        for _, left, right in _split_pairs(hunk.lines):
            classes = ["split-row"]
            rows.append(
                '<tr class="{}">'.format(" ".join(classes))
                + _split_cell(left, language, "old", refs, file_index)
                + '<td class="split-divider"></td>'
                + _split_cell(right, language, "new", refs, file_index)
                + "</tr>"
            )
    return (
        '<table class="diff-table split-table">'
        '<colgroup><col class="line-col"><col><col class="divider-col">'
        '<col class="line-col"><col></colgroup>'
        '<tbody>{}</tbody></table>'.format("".join(rows))
    )


def render_file_diff(file_diff: FileDiff, index: int) -> str:
    language = detect_language(file_diff.new_path if file_diff.new_path != "/dev/null" else file_diff.old_path)
    anchor = file_anchor(file_diff, index)
    title = file_display_path(file_diff)
    return (
        '<section class="file-diff" id="{anchor}" data-language="{language}">'.format(
            anchor=escape(anchor), language=escape(language)
        )
        + '<header class="file-header">'
        + '<div><h2>{}</h2><p>{}</p></div>'.format(escape(title), escape(file_diff.status))
        + '<span class="language-badge">{}</span>'.format(escape(language))
        + "</header>"
        + '<div class="diff-view unified-view" data-view="unified">'
        + render_unified_table(file_diff, language, index)
        + "</div>"
        + '<div class="diff-view split-view" data-view="split">'
        + render_split_table(file_diff, language, index)
        + "</div>"
        + "</section>"
    )


def build_highlight_seeds(files: List[FileDiff]) -> List[Dict[str, object]]:
    seeds: List[Dict[str, object]] = []
    for index, file_diff in enumerate(files):
        language = detect_language(file_diff.new_path if file_diff.new_path != "/dev/null" else file_diff.old_path)
        before: List[str] = []
        after: List[str] = []
        for hunk in file_diff.hunks:
            for line in hunk.lines:
                if line.kind == "del":
                    before.append(line.content)
                elif line.kind == "add":
                    after.append(line.content)
                else:
                    before.append(line.content)
                    after.append(line.content)
        seeds.append(
            {
                "file": index,
                "lang": language,
                "before": "\n".join(before),
                "after": "\n".join(after),
            }
        )
    return seeds


def render_highlight_seeds(files: List[FileDiff]) -> str:
    return json.dumps(build_highlight_seeds(files), ensure_ascii=False).replace("</", "<\\/")


def json_for_script(value: object) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def build_comment_storage_scope(root: Path, report_path: Optional[Path], created_at: datetime) -> str:
    report = str(report_path) if report_path else "unspecified-report"
    return "{}::{}::{}".format(root, report, created_at.isoformat(timespec="microseconds"))


def fill_template(template: str, replacements: Dict[str, str]) -> str:
    pattern = re.compile("|".join(re.escape(key) for key in replacements))
    return pattern.sub(lambda match: replacements[match.group(0)], template)


def render_nav(files: List[FileDiff]) -> str:
    if not files:
        return '<li><a href="#top">No changes</a></li>'
    items: List[str] = []
    for index, file_diff in enumerate(files):
        items.append(
            '<li><a href="#{}">{}</a></li>'.format(
                escape(file_anchor(file_diff, index)),
                escape(file_display_path(file_diff)),
            )
        )
    return "".join(items)


def render_body(files: List[FileDiff]) -> str:
    if not files:
        return (
            '<section class="empty-state">'
            "<h2>No working-tree diff</h2>"
            "<p>The current repository has no staged or unstaged changes against HEAD.</p>"
            "</section>"
        )
    return "".join(render_file_diff(file_diff, index) for index, file_diff in enumerate(files))


def run_git(args: List[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def repo_root(cwd: Path) -> Path:
    result = run_git(["rev-parse", "--show-toplevel"], cwd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Not a git repository")
    return Path(result.stdout.strip())


def capture_diff(root: Path) -> str:
    result = run_git(["diff", "HEAD", "--no-ext-diff"], root)
    if result.returncode != 0:
        result = run_git(["diff", "--no-ext-diff"], root)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Unable to capture git diff")
    return result.stdout


def head_short_sha(root: Path) -> str:
    result = run_git(["rev-parse", "--short", "HEAD"], root)
    if result.returncode != 0:
        return "working"
    return result.stdout.strip() or "working"


def has_working_changes(root: Path) -> bool:
    result = run_git(["status", "--porcelain"], root)
    return result.returncode == 0 and bool(result.stdout.strip())


def default_output_path(root: Path, summary: Dict[str, int]) -> Path:
    if summary["files"] == 0:
        tag = "clean"
    elif has_working_changes(root):
        tag = "working"
    else:
        tag = head_short_sha(root)
    return root / ".diffs" / "{}_{}.html".format(datetime.now().strftime("%Y-%m-%d"), tag)


def gitignore_has_diffs(root: Path) -> bool:
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        return False
    ignored = {
        line.strip()
        for line in gitignore.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    return ".diffs" in ignored or ".diffs/" in ignored


CODE_SCHEMES = (
    "github",
    "atom-one",
    "monokai",
    "dracula",
    "nord",
    "tokyo-night",
    "solarized",
    "gruvbox",
)


def assemble_html(
    files: List[FileDiff],
    root: Path,
    default_view: str = "unified",
    default_theme: str = "auto",
    default_code_scheme: str = "github",
    report_path: Optional[Path] = None,
) -> str:
    summary = render_summary(files)
    created_at = datetime.now().astimezone()
    replacements = {
        "__REPORT_TITLE__": "Working Tree Diff",
        "__REPO_PATH__": escape(str(root)),
        "__CREATED_AT__": escape(created_at.strftime("%Y-%m-%d %H:%M:%S %Z")),
        "__SUMMARY_FILES__": str(summary["files"]),
        "__SUMMARY_ADDITIONS__": str(summary["additions"]),
        "__SUMMARY_DELETIONS__": str(summary["deletions"]),
        "__FILE_NAV__": render_nav(files),
        "__REPORT_BODY__": render_body(files),
        "__HIGHLIGHT_SEEDS__": render_highlight_seeds(files),
        "__DEFAULT_VIEW__": json_for_script(default_view),
        "__DEFAULT_THEME__": json_for_script(default_theme),
        "__DEFAULT_CODE_SCHEME__": json_for_script(default_code_scheme),
        "__COMMENT_STORAGE_SCOPE__": json_for_script(
            build_comment_storage_scope(root, report_path, created_at)
        ),
    }
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    return fill_template(template, replacements)


def write_report(html_text: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_text, encoding="utf-8")
    return output_path


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, help="Output HTML path")
    parser.add_argument("--view", choices=("unified", "split"), default="unified")
    parser.add_argument("--theme", choices=("auto", "light", "dark"), default="auto")
    parser.add_argument("--code-scheme", choices=CODE_SCHEMES, default="github")
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    try:
        root = repo_root(Path.cwd())
        diff_text = capture_diff(root)
        files = parse_git_diff(diff_text)
        summary = render_summary(files)
        output_path = args.output if args.output else default_output_path(root, summary)
        if not output_path.is_absolute():
            output_path = root / output_path
        html_text = assemble_html(files, root, args.view, args.theme, args.code_scheme, output_path)
        write_report(html_text, output_path)
    except Exception as exc:  # noqa: BLE001 - CLI should report concise errors.
        print("diff-viewer: {}".format(exc), file=sys.stderr)
        return 1

    print(
        "Diff report: {files} files, +{additions}/-{deletions}, {path}".format(
            files=summary["files"],
            additions=summary["additions"],
            deletions=summary["deletions"],
            path=output_path,
        )
    )
    if not gitignore_has_diffs(root):
        print("Suggestion: add .diffs/ to .gitignore")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
