#!/usr/bin/env python3
"""Render validated diff-summary Markdown as a self-contained HTML report."""

import argparse
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import traceback
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date as calendar_date
from hashlib import sha256
from html import escape
from pathlib import Path
from typing import TypeAlias

_METADATA_FIELDS = ("Date", "Repository", "Scope", "Command", "HEAD", "Language")
_CATEGORIES = (
    "Overview",
    "Behavior",
    "Architecture",
    "Pattern",
    "API",
    "Data",
    "Dependency",
    "Security",
    "Performance",
    "Test",
    "Operations",
    "Compatibility",
)
_IMPACTS = ("High", "Medium", "Low", "Informational")
_MAX_STDIN_REPORT_SIZE = 16 * 1024 * 1024
_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_FIXED_SCOPE_TAGS = {
    "working": "working",
    "staged": "staged",
    "unstaged": "unstaged",
    "HEAD~1..HEAD": "last-commit",
}

_FENCE_OPEN_RE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
_HEADING_RE = re.compile(
    r"^ {0,3}(?P<marks>#{1,6})(?:[ \t]+(?P<title>.*?))?[ \t]*(?:\r?\n)?$"
)
_CARD_HEADING_RE = re.compile(
    r"^ {0,3}#### \[(?P<id>DS-[0-9]{3})\] "
    r"(?P<title>\S(?:.*?\S)?)[ \t]*(?:\r?\n)?$"
)
_INDENTED_CARD_LIKE_RE = re.compile(
    r"^(?P<indent>[ \t]+)#### \[DS-[0-9]{3}\](?:[ \t]+.*)?$"
)
_METADATA_RE = re.compile(
    r"^\*\*(?P<field>Date|Repository|Scope|Command|HEAD|Language):\*\*"
    r"[ \t]*(?P<value>.*?)[ \t]*(?:\r?\n)?$"
)
_CARD_FIELD_RE = re.compile(
    r"^\*\*(?P<field>Category|Impact|Files):\*\*"
    r"[ \t]*(?P<value>.*?)[ \t]*(?:\r?\n)?$"
)
_SAFE_FENCE_LANGUAGE_RE = re.compile(r"[A-Za-z0-9_.+\-]+")
_INLINE_RE = re.compile(r"`([^`\n]+)`|\*\*(.+?)\*\*")
_UNORDERED_LIST_RE = re.compile(r"^ {0,3}[-+*][ \t]+(?P<text>\S.*)$")
_ORDERED_LIST_RE = re.compile(r"^ {0,3}(?P<number>\d+)[.)][ \t]+(?P<text>\S.*)$")
_TABLE_DELIMITER_RE = re.compile(r"^:?-{3,}:?$")
_RESERVED_DOM_IDS = {
    "comment-scope",
    "raw-markdown",
    "report-main",
    "report-sections",
    "report-status",
    "report-title",
    "summary-data",
}
_TEMPLATE_PLACEHOLDERS = (
    "__REPORT_TITLE__",
    "__REPORT_LANGUAGE__",
    "__REPORT_METADATA__",
    "__REPORT_BODY__",
    "__SIDEBAR_NAV__",
    "__SUMMARY_DATA__",
    "__RAW_MARKDOWN__",
    "__COMMENT_SCOPE__",
    "__DEFAULT_THEME__",
)
_PLACEHOLDER_RE = re.compile(
    "|".join(re.escape(placeholder) for placeholder in _TEMPLATE_PLACEHOLDERS)
)

_JsonValue: TypeAlias = (
    None | bool | int | float | str | list["_JsonValue"] | dict[str, "_JsonValue"]
)


class ReportFormatError(ValueError):
    """Raised when a diff-summary Markdown report violates the report contract."""


@dataclass(frozen=True)
class ReportMetadata:
    """Required top-level report metadata."""

    title: str
    date: str
    repository: str
    scope: str
    command: str
    head: str
    language: str


@dataclass(frozen=True)
class SummaryCard:
    """One validated diff-summary card and its exact source Markdown."""

    id: str
    title: str
    section: str
    category: str
    impact: str
    files: tuple[str, ...]
    markdown: str


@dataclass(frozen=True)
class ParsedReport:
    """A validated report, including the unchanged original Markdown."""

    metadata: ReportMetadata
    cards: tuple[SummaryCard, ...]
    markdown: str


def json_for_script(value: _JsonValue) -> str:
    """Serialize JSON for safe embedding in an application/json script element."""
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    )
    return (
        serialized.replace("&", r"\u0026")
        .replace("<", r"\u003c")
        .replace(">", r"\u003e")
        .replace("\u2028", r"\u2028")
        .replace("\u2029", r"\u2029")
    )


def _normalize_comment_markdown(markdown: str) -> str:
    normalized = markdown.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip(" \t") for line in normalized.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def stable_comment_scope(report: ParsedReport) -> str:
    """Return the deterministic persistence scope for report comments."""
    identity = {
        "repository": report.metadata.repository,
        "scope": report.metadata.scope,
        "command": report.metadata.command,
        "head": report.metadata.head,
        "cards": [
            {"id": card.id, "markdown": _normalize_comment_markdown(card.markdown)}
            for card in report.cards
        ],
    }
    canonical = json.dumps(
        identity,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = sha256(canonical).hexdigest()[:20]
    return f"{report.metadata.repository}::{report.metadata.scope}::{digest}"


def scope_tag(scope: str) -> str:
    """Return a collision-safe, filesystem-safe tag for an exact report scope."""
    if not isinstance(scope, str):
        raise TypeError("scope must be a string")
    if not scope or any(
        ord(character) < 32 or ord(character) == 127 for character in scope
    ):
        raise ReportFormatError(
            "scope must be non-empty and contain no control characters"
        )
    fixed = _FIXED_SCOPE_TAGS.get(scope)
    if fixed is not None:
        return fixed
    pr_match = re.fullmatch(r"PR #([0-9]+)", scope)
    if pr_match is not None:
        return f"pr-{pr_match.group(1)}"
    commit_match = re.fullmatch(r"[0-9A-Fa-f]{7,64}", scope)
    if commit_match is not None:
        return f"commit-{scope[:12].lower()}"

    readable = unicodedata.normalize("NFKC", scope)
    readable = readable.replace("...", "-dot3-").replace("..", "-dot2-")
    readable = re.sub(r"[^\w]+", "-", readable, flags=re.UNICODE)
    readable = re.sub(r"[-_]+", "-", readable).strip("-").lower() or "scope"
    readable = readable[:60].rstrip("-") or "scope"
    while len(readable.encode("utf-8")) > 180:
        readable = readable[:-1].rstrip("-") or "scope"
    digest = sha256(scope.encode("utf-8")).hexdigest()[:12]
    return f"{readable}-{digest}"


def report_artifact_stem(metadata: ReportMetadata) -> str:
    """Derive the Markdown/HTML artifact stem from validated report metadata."""
    if _DATE_RE.fullmatch(metadata.date) is None:
        raise ReportFormatError("metadata field Date must use YYYY-MM-DD")
    try:
        parsed_date = calendar_date.fromisoformat(metadata.date)
    except ValueError as error:
        raise ReportFormatError(
            "metadata field Date must be a real calendar date"
        ) from error
    if parsed_date.isoformat() != metadata.date:
        raise ReportFormatError("metadata field Date must use canonical YYYY-MM-DD")
    return f"{metadata.date}_{scope_tag(metadata.scope)}"


def render_report_body(report: ParsedReport) -> str:
    """Render validated report Markdown into safe semantic HTML."""
    return _render_report(report)[0]


def load_template() -> str:
    """Load the self-contained HTML template bundled beside this script."""
    template_path = (
        Path(__file__).resolve().parent.parent / "assets" / "summary-template.html"
    )
    return template_path.read_text(encoding="utf-8")


def replace_placeholders(template: str, mapping: dict[str, str]) -> str:
    """Replace each required template placeholder exactly once in one pass."""
    for placeholder in _TEMPLATE_PLACEHOLDERS:
        count = template.count(placeholder)
        if count != 1:
            raise ReportFormatError(
                f"template placeholder {placeholder} must appear exactly once; found {count}"
            )
        if placeholder not in mapping:
            raise ReportFormatError(
                f"missing replacement for template placeholder {placeholder}"
            )
    unexpected = set(mapping).difference(_TEMPLATE_PLACEHOLDERS)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ReportFormatError(
            f"unexpected template placeholder replacements: {names}"
        )
    return _PLACEHOLDER_RE.sub(lambda match: mapping[match.group(0)], template)


def assemble_html(
    report: ParsedReport,
    template: str,
    default_theme: str = "auto",
) -> str:
    """Assemble a complete self-contained diff-summary HTML report."""
    if default_theme not in {"auto", "light", "dark"}:
        raise ReportFormatError("default theme must be one of: auto, light, dark")

    body, navigation = _render_report(report)
    summary_data: list[_JsonValue] = [
        {
            "id": card.id,
            "title": card.title,
            "section": card.section,
            "category": card.category,
            "impact": card.impact,
            "files": list(card.files),
            "markdown": card.markdown,
        }
        for card in report.cards
    ]
    mapping = {
        "__REPORT_TITLE__": escape(report.metadata.title, quote=True),
        "__REPORT_LANGUAGE__": escape(report.metadata.language, quote=True),
        "__REPORT_METADATA__": _render_metadata(report.metadata),
        "__REPORT_BODY__": body,
        "__SIDEBAR_NAV__": _render_navigation(navigation),
        "__SUMMARY_DATA__": json_for_script(summary_data),
        "__RAW_MARKDOWN__": json_for_script(report.markdown),
        "__COMMENT_SCOPE__": json_for_script(stable_comment_scope(report)),
        "__DEFAULT_THEME__": default_theme,
    }
    return replace_placeholders(template, mapping)


@dataclass(frozen=True)
class _NavigationItem:
    level: int
    title: str
    anchor: str


class _HeadingIndex:
    """Allocate deterministic document anchors without duplicate DOM IDs."""

    def __init__(self) -> None:
        self._used = set(_RESERVED_DOM_IDS)
        self.navigation: list[_NavigationItem] = []

    def add(self, level: int, title: str) -> str:
        normalized = unicodedata.normalize("NFKC", title).lower()
        normalized = re.sub(r"[`*_]", "", normalized)
        base = re.sub(r"[^\w-]+", "-", normalized, flags=re.UNICODE)
        base = base.replace("_", "-").strip("-") or "section"
        if not base[0].isalpha():
            base = f"section-{base}"

        anchor = base
        suffix = 2
        while anchor in self._used:
            anchor = f"{base}-{suffix}"
            suffix += 1
        self._used.add(anchor)
        if level in (2, 3):
            self.navigation.append(_NavigationItem(level, title, anchor))
        return anchor


def _render_inline(value: str) -> str:
    rendered: list[str] = []
    cursor = 0
    for match in _INLINE_RE.finditer(value):
        rendered.append(escape(value[cursor : match.start()], quote=True))
        code, bold = match.groups()
        if code is not None:
            rendered.append(f"<code>{escape(code, quote=True)}</code>")
        else:
            rendered.append(f"<strong>{escape(bold, quote=True)}</strong>")
        cursor = match.end()
    rendered.append(escape(value[cursor:], quote=True))
    return "".join(rendered)


def _split_table_row(line: str) -> list[str]:
    row = line.strip()
    cells: list[str] = []
    current: list[str] = []
    active_code_run: int | None = None
    last_was_delimiter = False
    cursor = 0

    while cursor < len(row):
        character = row[cursor]
        if character == "\\" and cursor + 1 < len(row) and row[cursor + 1] == "|":
            current.append("|")
            last_was_delimiter = False
            cursor += 2
            continue

        if character == "`":
            run_end = cursor + 1
            while run_end < len(row) and row[run_end] == "`":
                run_end += 1
            run_length = run_end - cursor
            current.append(row[cursor:run_end])
            if active_code_run is None:
                active_code_run = run_length
            elif active_code_run == run_length:
                active_code_run = None
            last_was_delimiter = False
            cursor = run_end
            continue

        if character == "|" and active_code_run is None:
            cells.append("".join(current).strip())
            current.clear()
            last_was_delimiter = True
            cursor += 1
            continue

        current.append(character)
        last_was_delimiter = False
        cursor += 1

    cells.append("".join(current).strip())
    if row.startswith("|"):
        cells.pop(0)
    if last_was_delimiter:
        cells.pop()
    return cells


def _table_alignments(line: str) -> list[str] | None:
    cells = _split_table_row(line)
    if not cells or any(_TABLE_DELIMITER_RE.fullmatch(cell) is None for cell in cells):
        return None
    alignments: list[str] = []
    for cell in cells:
        if cell.startswith(":") and cell.endswith(":"):
            alignments.append("center")
        elif cell.endswith(":"):
            alignments.append("right")
        else:
            alignments.append("left")
    return alignments


def _render_table(
    lines: Sequence[str],
    start: int,
) -> tuple[str, int] | None:
    if start + 1 >= len(lines) or "|" not in lines[start]:
        return None
    headings = _split_table_row(lines[start].rstrip("\r\n"))
    alignments = _table_alignments(lines[start + 1].rstrip("\r\n"))
    if alignments is None or len(headings) != len(alignments):
        return None

    rows: list[list[str]] = []
    cursor = start + 2
    while cursor < len(lines):
        raw = lines[cursor].rstrip("\r\n")
        if not raw.strip() or "|" not in raw:
            break
        cells = _split_table_row(raw)
        if len(cells) != len(headings):
            return None
        rows.append(cells)
        cursor += 1

    header_cells = "".join(
        f'<th scope="col" class="align-{alignment}">{_render_inline(cell)}</th>'
        for cell, alignment in zip(headings, alignments, strict=True)
    )
    body_rows = "\n".join(
        "<tr>"
        + "".join(
            f'<td class="align-{alignment}">{_render_inline(cell)}</td>'
            for cell, alignment in zip(row, alignments, strict=True)
        )
        + "</tr>"
        for row in rows
    )
    return (
        '<div class="table-scroll" role="region" '
        'aria-label="Summary metrics" tabindex="0">\n'
        "<table>\n"
        f"<thead><tr>{header_cells}</tr></thead>\n"
        f"<tbody>\n{body_rows}\n</tbody>\n"
        "</table>\n"
        "</div>",
        cursor,
    )


def _fence_end(lines: Sequence[str], start: int, fence: str) -> int:
    character = fence[0]
    minimum = len(fence)
    for cursor in range(start + 1, len(lines)):
        raw = lines[cursor].rstrip("\r\n")
        stripped = raw.lstrip(" ")
        indent = len(raw) - len(stripped)
        run_length = len(stripped) - len(stripped.lstrip(character))
        if (
            indent <= 3
            and run_length >= minimum
            and stripped[run_length:].strip(" \t") == ""
        ):
            return cursor
    raise ReportFormatError("unclosed fenced code block")


def _render_diff_code(lines: Sequence[str]) -> str:
    rendered: list[str] = []
    for line in lines:
        if line.startswith("@@"):
            kind = "hunk"
        elif line.startswith("+++") or line.startswith("---"):
            kind = "meta"
        elif line.startswith("+"):
            kind = "add"
        elif line.startswith("-"):
            kind = "delete"
        else:
            kind = "context"
        rendered.append(
            f'<span class="diff-line diff-line--{kind}">'
            f"{escape(line, quote=True)}</span>"
        )
    return "\n".join(rendered)


def _render_fence(
    lines: Sequence[str],
    start: int,
) -> tuple[str, int]:
    opening = _FENCE_OPEN_RE.fullmatch(lines[start].rstrip("\r\n"))
    if opening is None:
        raise AssertionError("fence renderer called for a non-fence line")
    fence = opening.group("fence")
    end = _fence_end(lines, start, fence)
    language = safe_fence_language(opening.group("info"))
    code_lines = [line.rstrip("\r\n") for line in lines[start + 1 : end]]
    if language.lower() == "diff":
        content = _render_diff_code(code_lines)
    else:
        content = escape("\n".join(code_lines), quote=True)
    class_attribute = (
        f' class="language-{escape(language, quote=True)}"' if language else ""
    )
    return (
        f'<pre class="code-block"><code{class_attribute}>{content}</code></pre>',
        end + 1,
    )


def _block_starts(lines: Sequence[str], index: int) -> bool:
    raw = lines[index].rstrip("\r\n")
    if not raw.strip():
        return True
    heading = _heading(lines[index])
    if heading is not None and heading[0] <= 3:
        return True
    if _FENCE_OPEN_RE.fullmatch(raw) is not None:
        return True
    if _UNORDERED_LIST_RE.fullmatch(raw) is not None:
        return True
    if _ORDERED_LIST_RE.fullmatch(raw) is not None:
        return True
    return _render_table(lines, index) is not None


def _render_blocks(lines: Sequence[str], headings: _HeadingIndex) -> str:
    parts: list[str] = []
    cursor = 0
    while cursor < len(lines):
        raw = lines[cursor].rstrip("\r\n")
        if not raw.strip():
            cursor += 1
            continue

        heading = _heading(lines[cursor])
        if heading is not None and heading[0] <= 3:
            level, title = heading
            anchor = headings.add(level, title)
            parts.append(
                f'<h{level} id="{escape(anchor, quote=True)}">'
                f"{_render_inline(title)}</h{level}>"
            )
            cursor += 1
            continue

        if _FENCE_OPEN_RE.fullmatch(raw) is not None:
            rendered_fence, cursor = _render_fence(lines, cursor)
            parts.append(rendered_fence)
            continue

        rendered_table = _render_table(lines, cursor)
        if rendered_table is not None:
            table, cursor = rendered_table
            parts.append(table)
            continue

        unordered = _UNORDERED_LIST_RE.fullmatch(raw)
        ordered = _ORDERED_LIST_RE.fullmatch(raw)
        if unordered is not None or ordered is not None:
            expression = (
                _UNORDERED_LIST_RE if unordered is not None else _ORDERED_LIST_RE
            )
            tag = "ul" if unordered is not None else "ol"
            start_attribute = (
                f' start="{int(ordered.group("number"))}"'
                if ordered is not None and ordered.group("number") != "1"
                else ""
            )
            items: list[str] = []
            while cursor < len(lines):
                item = expression.fullmatch(lines[cursor].rstrip("\r\n"))
                if item is None:
                    break
                items.append(f"<li>{_render_inline(item.group('text'))}</li>")
                cursor += 1
            parts.append(
                f"<{tag}{start_attribute}>\n" + "\n".join(items) + f"\n</{tag}>"
            )
            continue

        paragraph: list[str] = []
        while cursor < len(lines):
            if paragraph and _block_starts(lines, cursor):
                break
            paragraph_raw = lines[cursor].rstrip("\r\n")
            if not paragraph_raw.strip():
                break
            paragraph.append(paragraph_raw.strip())
            cursor += 1
        parts.append(f"<p>{_render_inline(' '.join(paragraph))}</p>")

    return "\n".join(parts)


def _card_body_lines(card: SummaryCard) -> tuple[str, ...]:
    scan = _scan_fences(card.markdown)
    body: list[str] = []
    for index, line in enumerate(scan.lines[1:], start=1):
        if scan.outside_fence[index] and _CARD_FIELD_RE.fullmatch(line) is not None:
            continue
        body.append(line)
    return tuple(body)


def _css_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _render_card(card: SummaryCard, headings: _HeadingIndex) -> str:
    card_id = escape(card.id, quote=True)
    title = escape(card.title, quote=True)
    category = escape(card.category, quote=True)
    impact = escape(card.impact, quote=True)
    category_token = _css_token(card.category)
    impact_token = _css_token(card.impact)
    open_attribute = " open" if card.impact == "High" else ""
    card_content = _render_blocks(_card_body_lines(card), headings)
    file_items = "\n".join(
        f"<li><code>{escape(path, quote=True)}</code></li>" for path in card.files
    )
    return (
        f'<details class="summary-card category-{category_token} impact-{impact_token}" '
        f'data-summary-id="{card_id}"{open_attribute}>\n'
        '<summary class="card-summary">\n'
        '<span class="card-heading">'
        f'<span class="summary-id">{card_id}</span>'
        f'<span class="summary-title">{title}</span>'
        "</span>\n"
        '<span class="card-badges">'
        f'<span class="badge badge--category" data-category="{category}">{category}</span>'
        f'<span class="badge badge--impact" data-impact="{impact}">{impact}</span>'
        f'<span class="comment-count" data-comment-count="{card_id}" '
        'aria-label="0 comments">0</span>'
        "</span>\n"
        "</summary>\n"
        '<div class="card-panel">\n'
        f'<div class="card-content">\n{card_content}\n</div>\n'
        '<section class="card-files" aria-label="Files changed">\n'
        '<h4 class="card-files-title">Files</h4>\n'
        f'<ul class="file-list">\n{file_items}\n</ul>\n'
        "</section>\n"
        f'<div class="card-toolbar" role="toolbar" aria-label="Actions for {card_id}">\n'
        f'<button type="button" class="card-action" data-copy-summary="{card_id}" '
        f'aria-label="Copy {card_id} Markdown">Copy Markdown</button>\n'
        f'<button type="button" class="card-action card-action--accent" '
        f'data-add-comment="{card_id}" aria-label="Add comment to {card_id}">'
        "Add comment</button>\n"
        "</div>\n"
        "</div>\n"
        "</details>"
    )


def _render_report(report: ParsedReport) -> tuple[str, tuple[_NavigationItem, ...]]:
    scan = _scan_fences(report.markdown)
    headings = _HeadingIndex()
    parts: list[str] = []
    pending: list[str] = []
    card_index = 0
    cursor = _header_end(scan)

    def flush_pending() -> None:
        if pending:
            rendered = _render_blocks(tuple(pending), headings)
            if rendered:
                parts.append(rendered)
            pending.clear()

    while cursor < len(scan.lines):
        card_match = (
            _CARD_HEADING_RE.fullmatch(scan.lines[cursor])
            if scan.outside_fence[cursor]
            else None
        )
        if card_match is None:
            pending.append(scan.lines[cursor])
            cursor += 1
            continue

        flush_pending()
        if card_index >= len(report.cards):
            raise ReportFormatError("renderer found an unexpected summary card")
        card = report.cards[card_index]
        if card.id != card_match.group("id"):
            raise ReportFormatError("renderer card order does not match parsed report")
        parts.append(_render_card(card, headings))
        card_index += 1
        cursor = _next_card_boundary(scan, cursor)

    flush_pending()
    if card_index != len(report.cards):
        raise ReportFormatError("renderer did not consume every parsed summary card")
    return "\n".join(parts), tuple(headings.navigation)


def _render_metadata(metadata: ReportMetadata) -> str:
    repository_attribute = escape(metadata.repository, quote=True)
    scope_attribute = escape(metadata.scope, quote=True)
    return (
        f'<header class="report-header" data-repository="{repository_attribute}" '
        f'data-scope="{scope_attribute}">\n'
        '<div class="report-overline">Diff Summary</div>\n'
        f'<h1 id="report-title">{escape(metadata.title, quote=True)}</h1>\n'
        '<dl class="report-metadata">\n'
        '<div class="metadata-cell"><dt>Date</dt>'
        f"<dd>{escape(metadata.date, quote=True)}</dd></div>\n"
        '<div class="metadata-cell"><dt>Repository</dt>'
        f"<dd>{escape(metadata.repository, quote=True)}</dd></div>\n"
        '<div class="metadata-cell"><dt>Scope</dt>'
        f"<dd><code>{escape(metadata.scope, quote=True)}</code></dd></div>\n"
        '<div class="metadata-cell metadata-cell--wide"><dt>Command</dt>'
        f"<dd><code>{escape(metadata.command, quote=True)}</code></dd></div>\n"
        '<div class="metadata-cell"><dt>HEAD</dt>'
        f"<dd><code>{escape(metadata.head, quote=True)}</code></dd></div>\n"
        '<div class="metadata-cell"><dt>Language</dt>'
        f"<dd>{escape(metadata.language.upper(), quote=True)}</dd></div>\n"
        "</dl>\n"
        "</header>"
    )


def _render_navigation(items: Sequence[_NavigationItem]) -> str:
    links = "\n".join(
        f'<li class="section-index-item section-index-item--h{item.level}">'
        f'<a href="#{escape(item.anchor, quote=True)}" data-heading-level="{item.level}">'
        f'<span class="index-mark" aria-hidden="true">'
        f"{'—' if item.level == 2 else '·'}</span>"
        f"{_render_inline(item.title)}</a></li>"
        for item in items
    )
    return f'<ol class="section-index">\n{links}\n</ol>'


@dataclass(frozen=True)
class _FenceScan:
    """Fence-aware line data shared by each parsing stage."""

    lines: tuple[str, ...]
    starts: tuple[int, ...]
    outside_fence: tuple[bool, ...]


@dataclass(frozen=True)
class _CardHeading:
    """A parsed card heading and the section active at that line."""

    line_index: int
    id: str
    title: str
    section: str


def safe_fence_language(value: str) -> str:
    """Return a safe, bounded code-fence language token or an empty string."""
    if not isinstance(value, str):
        return ""
    candidate = value.strip()
    if not candidate or _SAFE_FENCE_LANGUAGE_RE.fullmatch(candidate) is None:
        return ""
    return candidate[:32]


def _scan_fences(markdown: str) -> _FenceScan:
    lines = tuple(markdown.splitlines(keepends=True))
    starts: list[int] = []
    outside_fence: list[bool] = []
    offset = 0
    active_character: str | None = None
    active_length = 0

    for line in lines:
        starts.append(offset)
        offset += len(line)
        raw_line = line.rstrip("\r\n")

        if active_character is not None:
            outside_fence.append(False)
            stripped = raw_line.lstrip(" ")
            indent = len(raw_line) - len(stripped)
            run_length = len(stripped) - len(stripped.lstrip(active_character))
            if (
                indent <= 3
                and run_length >= active_length
                and stripped[run_length:].strip(" \t") == ""
            ):
                active_character = None
                active_length = 0
            continue

        opening = _FENCE_OPEN_RE.fullmatch(raw_line)
        if opening is None:
            outside_fence.append(True)
            continue

        fence = opening.group("fence")
        outside_fence.append(False)
        active_character = fence[0]
        active_length = len(fence)

    if active_character is not None:
        raise ReportFormatError("unclosed fenced code block")

    return _FenceScan(lines, tuple(starts), tuple(outside_fence))


def _heading(line: str) -> tuple[int, str] | None:
    match = _HEADING_RE.fullmatch(line)
    if match is None:
        return None
    return len(match.group("marks")), (match.group("title") or "").strip()


def _indent_columns(indent: str) -> int:
    columns = 0
    for character in indent:
        if character == "\t":
            columns += 4 - (columns % 4)
        else:
            columns += 1
    return columns


def _header_end(scan: _FenceScan) -> int:
    for index, line in enumerate(scan.lines):
        if not scan.outside_fence[index]:
            continue
        heading = _heading(line)
        if heading is not None and heading[0] in (2, 3, 4):
            return index
    return len(scan.lines)


def _single_metadata_value(values: dict[str, list[str]], field: str) -> str:
    matches = values[field]
    if not matches:
        raise ReportFormatError(f"missing metadata field: {field}")
    if len(matches) > 1:
        raise ReportFormatError(f"duplicate metadata field: {field}")
    value = matches[0].strip(" \t")
    if not value:
        raise ReportFormatError(f"metadata field {field} is empty")
    return value


def _parse_metadata(scan: _FenceScan) -> ReportMetadata:
    values = {field: [] for field in ("Title", *_METADATA_FIELDS)}
    header_values = {field: [] for field in ("Title", *_METADATA_FIELDS)}
    header_end = _header_end(scan)

    for index, line in enumerate(scan.lines):
        if not scan.outside_fence[index]:
            continue
        heading = _heading(line)
        if heading is not None and heading[0] == 1:
            values["Title"].append(heading[1])
            if index < header_end:
                header_values["Title"].append(heading[1])
            continue
        match = _METADATA_RE.fullmatch(line)
        if match is not None:
            values[match.group("field")].append(match.group("value"))
            if index < header_end:
                header_values[match.group("field")].append(match.group("value"))

    for field in values:
        _single_metadata_value(values, field)
        if len(header_values[field]) != 1:
            raise ReportFormatError(
                f"metadata field {field} must appear before the first section"
            )

    title = _single_metadata_value(values, "Title")
    date = _single_metadata_value(values, "Date")
    repository = _single_metadata_value(values, "Repository")
    scope = _single_metadata_value(values, "Scope")
    command = _single_metadata_value(values, "Command")
    head = _single_metadata_value(values, "HEAD")
    language = _single_metadata_value(values, "Language")

    if command.startswith("`") and command.endswith("`") and len(command) >= 2:
        command = command[1:-1]
        if not command.strip():
            raise ReportFormatError("metadata field Command is empty")

    return ReportMetadata(
        title=title,
        date=date,
        repository=repository,
        scope=scope,
        command=command,
        head=head,
        language=language.lower(),
    )


def _parse_card_headings(scan: _FenceScan) -> tuple[_CardHeading, ...]:
    headings: list[_CardHeading] = []
    current_section = ""

    for index, line in enumerate(scan.lines):
        if not scan.outside_fence[index]:
            continue
        display = line.rstrip("\r\n")
        indented_card = _INDENTED_CARD_LIKE_RE.fullmatch(display)
        if (
            indented_card is not None
            and _indent_columns(indented_card.group("indent")) >= 4
        ):
            raise ReportFormatError(
                f"over-indented card heading at line {index + 1} is malformed: "
                f"{display}; use at most 3 leading spaces"
            )
        heading = _heading(line)
        if heading is None:
            continue
        level, title = heading
        if level == 2:
            current_section = ""
            continue
        if level == 3:
            current_section = title
            continue
        if level != 4:
            continue

        card_match = _CARD_HEADING_RE.fullmatch(line)
        if card_match is None:
            raise ReportFormatError(
                f"malformed card heading at line {index + 1}: {display}"
            )
        headings.append(
            _CardHeading(
                line_index=index,
                id=card_match.group("id"),
                title=card_match.group("title"),
                section=current_section,
            )
        )

    if not headings:
        raise ReportFormatError("report contains no cards")

    seen: set[str] = set()
    for heading in headings:
        if heading.id in seen:
            raise ReportFormatError(f"duplicate card ID: {heading.id}")
        seen.add(heading.id)

    for number, heading in enumerate(headings, start=1):
        expected = f"DS-{number:03d}"
        if heading.id != expected:
            raise ReportFormatError(
                f"card IDs must be sequential: expected {expected} but found {heading.id}"
            )

    return tuple(headings)


def _next_card_boundary(scan: _FenceScan, start: int) -> int:
    for index in range(start + 1, len(scan.lines)):
        if not scan.outside_fence[index]:
            continue
        heading = _heading(scan.lines[index])
        if heading is not None and heading[0] in (2, 3, 4):
            return index
    return len(scan.lines)


def _required_card_fields(
    scan: _FenceScan, heading: _CardHeading, boundary: int
) -> dict[str, str]:
    matches: dict[str, list[str]] = {
        "Category": [],
        "Impact": [],
        "Files": [],
    }
    for index in range(heading.line_index + 1, boundary):
        if not scan.outside_fence[index]:
            continue
        match = _CARD_FIELD_RE.fullmatch(scan.lines[index])
        if match is not None:
            matches[match.group("field")].append(match.group("value").strip(" \t"))

    values: dict[str, str] = {}
    context = _card_context(heading)
    for field, field_matches in matches.items():
        if not field_matches:
            raise ReportFormatError(f"{context} is missing required {field} field")
        if len(field_matches) > 1:
            raise ReportFormatError(f"{context} has duplicate {field} fields")
        values[field] = field_matches[0]
    return values


def _card_context(heading: _CardHeading) -> str:
    return f"card {heading.id} (heading line {heading.line_index + 1})"


def _controlled_value(
    heading: _CardHeading,
    field: str,
    value: str,
    allowed_values: tuple[str, ...],
) -> str:
    if value in allowed_values:
        return value
    raise ReportFormatError(
        f"{_card_context(heading)} has unsupported {field} value: {value or '<empty>'}"
    )


def _parse_files(heading: _CardHeading, value: str) -> tuple[str, ...]:
    paths: list[str] = []
    cursor = 0
    length = len(value)
    context = _card_context(heading)

    while cursor < length:
        while cursor < length and value[cursor] in " \t":
            cursor += 1
        if cursor >= length or value[cursor] != "`":
            raise ReportFormatError(f"{context} has malformed Files field")
        closing = value.find("`", cursor + 1)
        if closing == -1:
            raise ReportFormatError(f"{context} has malformed Files field")
        path = value[cursor + 1 : closing]
        if not path or path != path.strip():
            raise ReportFormatError(f"{context} has malformed Files field")
        paths.append(path)
        cursor = closing + 1

        while cursor < length and value[cursor] in " \t":
            cursor += 1
        if cursor == length:
            break
        if value[cursor] != ",":
            raise ReportFormatError(f"{context} has malformed Files field")
        cursor += 1
        while cursor < length and value[cursor] in " \t":
            cursor += 1
        if cursor == length:
            raise ReportFormatError(f"{context} has malformed Files field")

    if not paths:
        raise ReportFormatError(f"{context} has malformed Files field")
    if len(paths) != len(set(paths)):
        raise ReportFormatError(f"{context} Files field contains duplicate paths")
    return tuple(paths)


def _parse_cards(markdown: str, scan: _FenceScan) -> tuple[SummaryCard, ...]:
    cards: list[SummaryCard] = []
    for heading in _parse_card_headings(scan):
        boundary = _next_card_boundary(scan, heading.line_index)
        fields = _required_card_fields(scan, heading, boundary)
        category = _controlled_value(
            heading,
            "Category",
            fields["Category"],
            _CATEGORIES,
        )
        impact = _controlled_value(
            heading,
            "Impact",
            fields["Impact"],
            _IMPACTS,
        )
        files = _parse_files(heading, fields["Files"])
        start_offset = scan.starts[heading.line_index]
        end_offset = (
            scan.starts[boundary] if boundary < len(scan.lines) else len(markdown)
        )
        cards.append(
            SummaryCard(
                id=heading.id,
                title=heading.title,
                section=heading.section,
                category=category,
                impact=impact,
                files=files,
                markdown=markdown[start_offset:end_offset],
            )
        )
    return tuple(cards)


def parse_report(markdown: str) -> ParsedReport:
    """Parse and validate one diff-summary Markdown report."""
    if not isinstance(markdown, str):
        raise TypeError("markdown must be a string")
    scan = _scan_fences(markdown)
    metadata = _parse_metadata(scan)
    cards = _parse_cards(markdown, scan)
    return ParsedReport(metadata=metadata, cards=cards, markdown=markdown)


@dataclass(frozen=True)
class _GenerationResult:
    """Internal generation facts used by the command-line handoff."""

    path: Path
    markdown_path: Path
    report: ParsedReport
    comment_scope: str


def _atomic_write_text(output_path: Path, content: str) -> None:
    """Replace an output file only after its complete sibling temp file is written."""
    _validate_output_parent(output_path)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            delete=False,
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        temporary_path.replace(output_path)
    except BaseException:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def _warn_open_failure(output_path: Path, detail: str) -> None:
    print(
        f"warning: generated report was retained at {output_path}, "
        f"but the browser could not be opened ({detail})",
        file=sys.stderr,
    )


def _open_generated_report(output_path: Path) -> None:
    """Best-effort opening through a fixed system launcher, never ambient BROWSER."""
    uri = output_path.as_uri()
    try:
        if os.name == "nt":
            startfile = getattr(os, "startfile", None)
            if startfile is None:
                raise OSError("os.startfile is unavailable")
            startfile(uri)
            return
        candidates = (
            (Path("/usr/bin/open"), (uri,))
            if sys.platform == "darwin"
            else (Path("/usr/bin/xdg-open"), (uri,))
        )
        opener, arguments = candidates
        metadata = opener.lstat()
        if not stat.S_ISREG(metadata.st_mode) or not os.access(opener, os.X_OK):
            raise OSError(f"trusted system opener is not executable: {opener}")
        environment = {
            key: value
            for key, value in os.environ.items()
            if key not in {"BROWSER", "PYTHONHOME", "PYTHONPATH"}
            and not key.startswith("PYTHON")
        }
        environment["PATH"] = os.pathsep.join(
            path
            for path in ("/usr/bin", "/bin", "/usr/local/bin")
            if Path(path).is_dir()
        )
        result = subprocess.run(
            [str(opener), *arguments],
            cwd=Path("/"),
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.decode("utf-8", errors="backslashreplace")[
                :300
            ].strip()
            raise OSError(detail or f"system opener exited with {result.returncode}")
    except (OSError, subprocess.SubprocessError) as error:
        _warn_open_failure(output_path, str(error) or type(error).__name__)


def _absolute_lexical_path(value: str | Path) -> Path:
    """Return an absolute path without resolving its final symlink target."""
    return Path(os.path.abspath(os.fspath(Path(value).expanduser())))


def _validate_output_parent(output_path: Path, *, create: bool = False) -> None:
    """Reject a missing, non-directory, or symlinked immediate output parent."""
    parent = output_path.parent
    try:
        metadata = parent.lstat()
    except FileNotFoundError as error:
        if not create:
            raise ReportFormatError(
                f"output parent is unavailable: {parent}: {error}"
            ) from error
        grandparent = parent.parent
        try:
            grandparent_metadata = grandparent.lstat()
        except OSError as parent_error:
            raise ReportFormatError(
                f"output parent cannot be created below {grandparent}: {parent_error}"
            ) from parent_error
        if stat.S_ISLNK(grandparent_metadata.st_mode) or not stat.S_ISDIR(
            grandparent_metadata.st_mode
        ):
            raise ReportFormatError(
                f"output parent cannot be created below a symlink or non-directory: {grandparent}"
            )
        try:
            parent.mkdir(mode=0o700)
            metadata = parent.lstat()
        except OSError as parent_error:
            raise ReportFormatError(
                f"output parent could not be created: {parent}: {parent_error}"
            ) from parent_error
    except OSError as error:
        raise ReportFormatError(
            f"output parent is unavailable: {parent}: {error}"
        ) from error
    if stat.S_ISLNK(metadata.st_mode):
        raise ReportFormatError(f"output parent must not be a symlink: {parent}")
    if not stat.S_ISDIR(metadata.st_mode):
        raise ReportFormatError(f"output parent must be a directory: {parent}")


def _validate_regular_input(input_path: Path) -> None:
    """Require a real regular Markdown file rather than a symlink or device."""
    try:
        parent_metadata = input_path.parent.lstat()
    except OSError as error:
        raise ReportFormatError(
            f"input parent is unavailable: {input_path.parent}: {error}"
        ) from error
    if stat.S_ISLNK(parent_metadata.st_mode):
        raise ReportFormatError(
            f"input parent must not be a symlink: {input_path.parent}"
        )
    if not stat.S_ISDIR(parent_metadata.st_mode):
        raise ReportFormatError(
            f"input parent must be a directory: {input_path.parent}"
        )
    try:
        metadata = input_path.lstat()
    except OSError as error:
        raise ReportFormatError(
            f"input Markdown is unavailable: {input_path}: {error}"
        ) from error
    if not stat.S_ISREG(metadata.st_mode):
        raise ReportFormatError(
            f"input Markdown must be a regular file, not a symlink or device: {input_path}"
        )


def _aliases_source(source_path: Path, destination_path: Path) -> bool:
    """Detect lexical, symlink, and hardlink aliases of the Markdown source."""
    try:
        return source_path.samefile(destination_path)
    except OSError:
        return source_path == destination_path.resolve(strict=False)


def _generate_report(
    input_path: str | Path,
    output_path: str | Path | None = None,
    theme: str = "auto",
    open_report: bool = False,
) -> _GenerationResult:
    source_lexical_path = _absolute_lexical_path(input_path)
    _validate_regular_input(source_lexical_path)
    source_path = source_lexical_path.resolve(strict=True)
    destination_path = (
        source_lexical_path.with_suffix(".html")
        if output_path is None
        else _absolute_lexical_path(output_path)
    )
    if _aliases_source(source_path, destination_path):
        raise ReportFormatError("output path must differ from the input Markdown path")

    markdown = source_path.read_text(encoding="utf-8")
    report = parse_report(markdown)
    html = assemble_html(report, load_template(), default_theme=theme)
    _atomic_write_text(destination_path, html)

    if open_report:
        _open_generated_report(destination_path)

    return _GenerationResult(
        path=destination_path,
        markdown_path=source_path,
        report=report,
        comment_scope=stable_comment_scope(report),
    )


def _generate_report_from_markdown(
    markdown: str,
    markdown_path: str | Path,
    output_path: str | Path | None = None,
    theme: str = "auto",
    open_report: bool = False,
) -> _GenerationResult:
    """Validate Markdown, atomically write its source, and render sibling HTML."""
    if not isinstance(markdown, str):
        raise TypeError("markdown must be a string")
    source_path = _absolute_lexical_path(markdown_path)
    destination_path = (
        source_path.with_suffix(".html")
        if output_path is None
        else _absolute_lexical_path(output_path)
    )
    _validate_output_parent(source_path, create=True)
    _validate_output_parent(destination_path)
    if source_path == destination_path:
        raise ReportFormatError("output path must differ from the input Markdown path")

    report = parse_report(markdown)
    html = assemble_html(report, load_template(), default_theme=theme)
    _atomic_write_text(source_path, markdown)
    _atomic_write_text(destination_path, html)

    if open_report:
        _open_generated_report(destination_path)

    return _GenerationResult(
        path=destination_path,
        markdown_path=source_path,
        report=report,
        comment_scope=stable_comment_scope(report),
    )


def _generate_report_in_directory(
    markdown: str,
    output_directory: str | Path,
    theme: str = "auto",
    open_report: bool = False,
) -> _GenerationResult:
    """Derive collision-safe artifact names, then atomically write both files."""
    if not isinstance(markdown, str):
        raise TypeError("markdown must be a string")
    report = parse_report(markdown)
    stem = report_artifact_stem(report.metadata)
    html = assemble_html(report, load_template(), default_theme=theme)
    directory = _absolute_lexical_path(output_directory)
    _validate_output_parent(directory / ".artifact-parent-check", create=True)
    source_path = directory / f"{stem}.md"
    destination_path = directory / f"{stem}.html"
    _atomic_write_text(source_path, markdown)
    _atomic_write_text(destination_path, html)

    if open_report:
        _open_generated_report(destination_path)

    return _GenerationResult(
        path=destination_path,
        markdown_path=source_path,
        report=report,
        comment_scope=stable_comment_scope(report),
    )


def generate_report(
    input_path: str | Path,
    output_path: str | Path | None = None,
    theme: str = "auto",
    open_report: bool = False,
) -> Path:
    """Generate an atomic HTML report and return its absolute output path."""
    return _generate_report(input_path, output_path, theme, open_report).path


def generate_report_from_markdown(
    markdown: str,
    markdown_path: str | Path,
    output_path: str | Path | None = None,
    theme: str = "auto",
    open_report: bool = False,
) -> Path:
    """Atomically write Markdown and render its self-contained HTML sibling."""
    return _generate_report_from_markdown(
        markdown, markdown_path, output_path, theme, open_report
    ).path


def generate_report_in_directory(
    markdown: str,
    output_directory: str | Path,
    theme: str = "auto",
    open_report: bool = False,
) -> Path:
    """Derive collision-safe names and return the absolute HTML output path."""
    return _generate_report_in_directory(
        markdown, output_directory, theme, open_report
    ).path


def build_parser() -> argparse.ArgumentParser:
    """Build the diff-summary report generator command-line interface."""
    parser = argparse.ArgumentParser(
        description="Render a diff-summary Markdown report as self-contained HTML."
    )
    parser.add_argument(
        "markdown_report",
        nargs="?",
        help="Markdown report to render (omit with --output-directory)",
    )
    parser.add_argument(
        "--markdown-stdin",
        action="store_true",
        help=(
            "read Markdown from standard input and atomically write "
            "markdown_report before rendering"
        ),
    )
    parser.add_argument(
        "-o", "--output", help="HTML output path (default: input with .html)"
    )
    parser.add_argument(
        "--output-directory",
        help=(
            "derive a collision-safe Markdown/HTML filename from stdin report metadata "
            "and write both files below this directory"
        ),
    )
    parser.add_argument(
        "--theme",
        choices=("auto", "light", "dark"),
        default="auto",
        help="initial report theme (default: auto)",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        dest="open_report",
        help="open the generated local HTML report in a browser",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="show a traceback for unexpected generator failures",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Generate one report and print facts needed for the skill handoff."""
    arguments = build_parser().parse_args(argv)
    try:
        if arguments.output_directory is not None:
            if not arguments.markdown_stdin:
                raise ReportFormatError("--output-directory requires --markdown-stdin")
            if arguments.markdown_report is not None or arguments.output is not None:
                raise ReportFormatError(
                    "--output-directory cannot be combined with markdown_report or --output"
                )
        elif arguments.markdown_report is None:
            raise ReportFormatError(
                "markdown_report is required unless --output-directory is used"
            )
        if arguments.markdown_stdin:
            markdown_bytes = sys.stdin.buffer.read(_MAX_STDIN_REPORT_SIZE + 1)
            if len(markdown_bytes) > _MAX_STDIN_REPORT_SIZE:
                raise ReportFormatError("Markdown from standard input exceeds 16 MiB")
            markdown = markdown_bytes.decode("utf-8")
            if arguments.output_directory is not None:
                result = _generate_report_in_directory(
                    markdown,
                    arguments.output_directory,
                    theme=arguments.theme,
                    open_report=arguments.open_report,
                )
            else:
                result = _generate_report_from_markdown(
                    markdown,
                    arguments.markdown_report,
                    output_path=arguments.output,
                    theme=arguments.theme,
                    open_report=arguments.open_report,
                )
        else:
            result = _generate_report(
                arguments.markdown_report,
                output_path=arguments.output,
                theme=arguments.theme,
                open_report=arguments.open_report,
            )
    except ReportFormatError as error:
        print(f"error: invalid diff-summary report: {error}", file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except Exception as error:  # noqa: BLE001 - keep default CLI errors concise.
        if arguments.debug:
            traceback.print_exc()
        else:
            print(f"error: {error}", file=sys.stderr)
        return 1

    card_count = len(result.report.cards)
    card_label = "summary card" if card_count == 1 else "summary cards"
    print(f"Generated {card_count} {card_label}")
    print(f"Language: {result.report.metadata.language}")
    print(f"Comment scope: {result.comment_scope}")
    if arguments.markdown_stdin:
        print(f"Markdown: {result.markdown_path}")
    print(f"HTML: {result.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
