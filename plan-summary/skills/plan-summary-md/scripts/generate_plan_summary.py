#!/usr/bin/env python3
"""Validate and generate plan-summary Markdown and HTML artifacts."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import stat
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import date as calendar_date
from hashlib import sha256
from pathlib import Path
from typing import TypeAlias


METADATA_FIELDS = ("Date", "Sources", "Source Digests", "Language")
SUPPORTED_CATEGORIES = (
    "Overview",
    "Goal",
    "Scope",
    "Requirement",
    "Decision",
    "Architecture",
    "Flow",
    "Milestone",
    "Dependency",
    "Risk",
    "Acceptance",
    "Open Question",
)
MAX_REPORT_BYTES = 16 * 1024 * 1024
MAX_BILINGUAL_BYTES = (2 * MAX_REPORT_BYTES) + (64 * 1024)
QUIZ_MIN_OPTIONS = 2
QUIZ_MAX_OPTIONS = 6

_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_DIGEST_RE = re.compile(r"[0-9a-f]{64}")
_FENCE_RE = re.compile(r"^ {0,3}(?P<mark>`{3,}|~{3,})")
_HEADING_RE = re.compile(
    r"^ {0,3}(?P<marks>#{1,6})(?:[ \t]+(?P<title>.*?))?[ \t]*(?:\r?\n)?$"
)
_CARD_RE = re.compile(
    r"^ {0,3}#### \[(?P<id>PS-[0-9]{3})\] "
    r"(?P<title>\S(?:.*?\S)?)[ \t]*(?:\r?\n)?$"
)
_CARD_LIKE_RE = re.compile(r"^ {0,3}#### \[(?P<id>PS-[^\]]*)\]")
_QUESTION_RE = re.compile(
    r"^ {0,3}#### \[(?P<id>QZ-[0-9]{3})\] "
    r"(?P<title>\S(?:.*?\S)?)[ \t]*(?:\r?\n)?$"
)
_QUESTION_LIKE_RE = re.compile(r"^ {0,3}#### \[(?P<id>QZ-[^\]]*)\]")
_METADATA_RE = re.compile(
    r"^\*\*(?P<field>Date|Sources|Source Digests|Language):\*\*"
    r"[ \t]*(?P<value>.*?)[ \t]*(?:\r?\n)?$"
)
_CARD_FIELD_RE = re.compile(
    r"^\*\*(?P<field>Category|Sources|Summary|Why it matters|Source basis):\*\*"
    r"[ \t]*(?P<value>.*?)[ \t]*(?:\r?\n)?$"
)
_OPTION_RE = re.compile(
    r"^ {0,3}- \[(?P<mark>[ xX])\][ \t]+(?P<text>\S.*?)[ \t]*(?:\r?\n)?$"
)
_EXPLANATION_RE = re.compile(
    r"^\*\*Explanation:\*\*[ \t]*(?P<value>.*?)[ \t]*(?:\r?\n)?$"
)

JsonValue: TypeAlias = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)


class ReportFormatError(ValueError):
    """Raised when a plan-summary report violates the stable contract."""


@dataclass(frozen=True)
class SummaryCard:
    id: str
    title: str
    category: str
    sources: tuple[str, ...]
    summary: str
    why_it_matters: str
    source_basis: str
    markdown: str


@dataclass(frozen=True)
class QuizQuestion:
    id: str
    title: str
    options: tuple[str, ...]
    correct_index: int
    explanation: str
    markdown: str


@dataclass(frozen=True)
class PlanSummaryReport:
    date: str
    sources: tuple[str, ...]
    source_digests: tuple[str, ...]
    language: str
    executive_summary: str
    cards: tuple[SummaryCard, ...]
    quiz: tuple[QuizQuestion, ...]
    markdown: str


@dataclass(frozen=True)
class _SourceLine:
    text: str
    start: int
    end: int
    fenced: bool


def _source_lines(markdown: str) -> tuple[_SourceLine, ...]:
    lines: list[_SourceLine] = []
    offset = 0
    fence_mark: str | None = None
    for text in markdown.splitlines(keepends=True):
        match = _FENCE_RE.match(text)
        fenced = fence_mark is not None
        if match is not None:
            mark = match.group("mark")
            if fence_mark is None:
                fence_mark = mark[0] * len(mark)
                fenced = True
            elif mark[0] == fence_mark[0] and len(mark) >= len(fence_mark):
                fenced = True
                fence_mark = None
        lines.append(_SourceLine(text, offset, offset + len(text), fenced))
        offset += len(text)
    if not markdown.endswith(("\n", "\r")) and not lines and markdown:
        lines.append(_SourceLine(markdown, 0, len(markdown), False))
    return tuple(lines)


def _outside(lines: tuple[_SourceLine, ...]):
    return ((index, line) for index, line in enumerate(lines) if not line.fenced)


def _code_values(value: str, field: str) -> tuple[str, ...]:
    if not value.strip():
        raise ReportFormatError(f"metadata field {field} must be non-empty")
    parts = [part.strip() for part in value.split(",")]
    values: list[str] = []
    for part in parts:
        if len(part) < 3 or not (part.startswith("`") and part.endswith("`")):
            raise ReportFormatError(
                f"metadata field {field} must be a comma-separated backtick list"
            )
        item = part[1:-1]
        if not item:
            raise ReportFormatError(f"metadata field {field} contains an empty item")
        values.append(item)
    if len(values) != len(set(values)):
        raise ReportFormatError(f"metadata field {field} contains a duplicate item")
    return tuple(values)


def _validate_date(value: str) -> str:
    if _DATE_RE.fullmatch(value) is None:
        raise ReportFormatError("metadata field Date must use YYYY-MM-DD")
    try:
        parsed = calendar_date.fromisoformat(value)
    except ValueError as error:
        raise ReportFormatError("metadata field Date must be a real calendar date") from error
    if parsed.isoformat() != value:
        raise ReportFormatError("metadata field Date must use canonical YYYY-MM-DD")
    return value


def _metadata(lines: tuple[_SourceLine, ...]) -> dict[str, str]:
    found: dict[str, list[str]] = {field: [] for field in METADATA_FIELDS}
    for _, line in _outside(lines):
        heading = _HEADING_RE.match(line.text)
        if heading is not None and len(heading.group("marks")) == 2:
            break
        match = _METADATA_RE.match(line.text)
        if match is not None:
            found[match.group("field")].append(match.group("value"))
    for field, values in found.items():
        if len(values) != 1:
            raise ReportFormatError(
                f"metadata field {field} must appear exactly once; found {len(values)}"
            )
        if not values[0].strip():
            raise ReportFormatError(f"metadata field {field} must be non-empty")
    return {field: values[0].strip() for field, values in found.items()}


def _section_bounds(
    lines: tuple[_SourceLine, ...], title: str
) -> tuple[int, int] | None:
    headings: list[tuple[int, int, str]] = []
    for index, line in _outside(lines):
        match = _HEADING_RE.match(line.text)
        if match is not None:
            headings.append((index, len(match.group("marks")), (match.group("title") or "").strip()))
    matching = [entry for entry in headings if entry[1] == 2 and entry[2] == title]
    if not matching:
        return None
    if len(matching) != 1:
        raise ReportFormatError(f"## {title} must appear exactly once")
    start = matching[0][0]
    end = len(lines)
    for index, level, _ in headings:
        if index > start and level == 2:
            end = index
            break
    return start, end


def _field_values(
    lines: tuple[_SourceLine, ...], start: int, end: int, card_id: str
) -> dict[str, str]:
    found: dict[str, list[str]] = {
        field: []
        for field in ("Category", "Sources", "Summary", "Why it matters", "Source basis")
    }
    for index in range(start, end):
        line = lines[index]
        if line.fenced:
            continue
        match = _CARD_FIELD_RE.match(line.text)
        if match is not None:
            found[match.group("field")].append(match.group("value").strip())
    values: dict[str, str] = {}
    for field, matches in found.items():
        if len(matches) != 1:
            raise ReportFormatError(
                f"{card_id} field {field} must appear exactly once; found {len(matches)}"
            )
        if not matches[0]:
            raise ReportFormatError(f"{card_id} field {field} must be non-empty")
        values[field] = matches[0]
    return values


def _card_sources(value: str, card_id: str) -> tuple[str, ...]:
    try:
        sources = _code_values(value, "Sources")
    except ReportFormatError as error:
        raise ReportFormatError(f"{card_id} field Sources is invalid: {error}") from error
    return sources


def _parse_cards(
    markdown: str,
    lines: tuple[_SourceLine, ...],
    report_sources: tuple[str, ...],
) -> tuple[SummaryCard, ...]:
    headings: list[tuple[int, re.Match[str]]] = []
    for index, line in _outside(lines):
        match = _CARD_RE.match(line.text)
        if match is not None:
            headings.append((index, match))
            continue
        malformed = _CARD_LIKE_RE.match(line.text)
        if malformed is not None:
            raise ReportFormatError(
                f"malformed PS card heading: {malformed.group('id')}"
            )
    if not headings:
        raise ReportFormatError("report must contain at least one PS card")

    cards: list[SummaryCard] = []
    for position, (start, match) in enumerate(headings):
        expected = f"PS-{position + 1:03d}"
        card_id = match.group("id")
        if card_id != expected:
            raise ReportFormatError(
                f"PS card IDs must be unique and sequential; expected {expected}, found {card_id}"
            )
        end = len(lines)
        if position + 1 < len(headings):
            end = headings[position + 1][0]
        for index in range(start + 1, end):
            if lines[index].fenced:
                continue
            heading = _HEADING_RE.match(lines[index].text)
            if heading is not None and len(heading.group("marks")) <= 3:
                end = index
                break
        fields = _field_values(lines, start + 1, end, card_id)
        category = fields["Category"]
        if category not in SUPPORTED_CATEGORIES:
            raise ReportFormatError(f"{card_id} field Category is unsupported: {category}")
        sources = _card_sources(fields["Sources"], card_id)
        unknown = [source for source in sources if source.split("#", 1)[0] not in report_sources]
        if unknown:
            raise ReportFormatError(
                f"{card_id} field Sources references an undeclared source: {unknown[0]}"
            )
        start_offset = lines[start].start
        end_offset = lines[end].start if end < len(lines) else len(markdown)
        cards.append(
            SummaryCard(
                id=card_id,
                title=match.group("title"),
                category=category,
                sources=sources,
                summary=fields["Summary"],
                why_it_matters=fields["Why it matters"],
                source_basis=fields["Source basis"],
                markdown=markdown[start_offset:end_offset],
            )
        )
    return tuple(cards)


def _visible_text(markdown: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", markdown)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*_~]", "", text)
    text = html.unescape(text)
    return " ".join(text.split()).casefold()


def _parse_quiz(
    markdown: str, lines: tuple[_SourceLine, ...]
) -> tuple[QuizQuestion, ...]:
    bounds = _section_bounds(lines, "Quiz")
    for _, line in _outside(lines):
        malformed = _QUESTION_LIKE_RE.match(line.text)
        if malformed is not None and _QUESTION_RE.match(line.text) is None:
            raise ReportFormatError(
                f"malformed QZ question heading: {malformed.group('id')}"
            )
    if bounds is None:
        if any(_QUESTION_RE.match(line.text) for _, line in _outside(lines)):
            raise ReportFormatError("QZ questions require a final ## Quiz section")
        return ()
    start_section, end_section = bounds
    if end_section != len(lines):
        raise ReportFormatError("## Quiz must be the final level-two section")

    headings: list[tuple[int, re.Match[str]]] = []
    for index in range(start_section + 1, end_section):
        if lines[index].fenced:
            continue
        match = _QUESTION_RE.match(lines[index].text)
        if match is not None:
            headings.append((index, match))
    if not headings:
        raise ReportFormatError("## Quiz must contain at least one QZ question")

    questions: list[QuizQuestion] = []
    for position, (start, match) in enumerate(headings):
        question_id = match.group("id")
        expected = f"QZ-{position + 1:03d}"
        if question_id != expected:
            raise ReportFormatError(
                f"QZ question IDs must be unique and sequential; expected {expected}, found {question_id}"
            )
        end = headings[position + 1][0] if position + 1 < len(headings) else end_section
        options: list[str] = []
        correct: list[int] = []
        explanations: list[str] = []
        for index in range(start + 1, end):
            line = lines[index]
            if line.fenced:
                continue
            option = _OPTION_RE.match(line.text)
            if option is not None:
                options.append(option.group("text").strip())
                if option.group("mark").lower() == "x":
                    correct.append(len(options) - 1)
                continue
            explanation = _EXPLANATION_RE.match(line.text)
            if explanation is not None:
                explanations.append(explanation.group("value").strip())
        if not QUIZ_MIN_OPTIONS <= len(options) <= QUIZ_MAX_OPTIONS:
            raise ReportFormatError(
                f"{question_id} must contain {QUIZ_MIN_OPTIONS} to {QUIZ_MAX_OPTIONS} options"
            )
        if len(correct) != 1:
            raise ReportFormatError(f"{question_id} must have exactly one correct option")
        visible = [_visible_text(option) for option in options]
        if any(not value for value in visible):
            raise ReportFormatError(f"{question_id} contains an empty visible option")
        if len(visible) != len(set(visible)):
            raise ReportFormatError(f"{question_id} contains a duplicate option")
        if len(explanations) != 1 or not explanations[0]:
            raise ReportFormatError(
                f"{question_id} field Explanation must appear exactly once and be non-empty"
            )
        start_offset = lines[start].start
        end_offset = lines[end].start if end < len(lines) else len(markdown)
        questions.append(
            QuizQuestion(
                id=question_id,
                title=match.group("title"),
                options=tuple(options),
                correct_index=correct[0],
                explanation=explanations[0],
                markdown=markdown[start_offset:end_offset],
            )
        )
    return tuple(questions)


def parse_report(markdown: str) -> PlanSummaryReport:
    """Parse one complete plan-summary Markdown source."""
    if not isinstance(markdown, str) or not markdown.strip():
        raise ReportFormatError("report must be a non-empty string")
    if len(markdown.encode("utf-8")) > MAX_REPORT_BYTES:
        raise ReportFormatError(f"report exceeds {MAX_REPORT_BYTES} bytes")
    lines = _source_lines(markdown)
    metadata = _metadata(lines)
    sources = _code_values(metadata["Sources"], "Sources")
    digests = _code_values(metadata["Source Digests"], "Source Digests")
    if len(sources) != len(digests):
        raise ReportFormatError("metadata requires one digest per source")
    if any(_DIGEST_RE.fullmatch(digest) is None for digest in digests):
        raise ReportFormatError(
            "metadata field Source Digests must contain lowercase SHA-256 values"
        )
    language = metadata["Language"].lower()
    if language not in {"ko", "en"}:
        raise ReportFormatError("metadata field Language must be ko or en")

    executive_bounds = _section_bounds(lines, "Executive Summary")
    if executive_bounds is None:
        raise ReportFormatError("## Executive Summary must appear exactly once")
    executive_start, executive_end = executive_bounds
    start_offset = lines[executive_start].end
    end_offset = lines[executive_end].start if executive_end < len(lines) else len(markdown)
    executive_summary = markdown[start_offset:end_offset].strip()
    if not executive_summary:
        raise ReportFormatError("Executive Summary must be non-empty")

    cards = _parse_cards(markdown, lines, sources)
    quiz = _parse_quiz(markdown, lines)
    return PlanSummaryReport(
        date=_validate_date(metadata["Date"]),
        sources=sources,
        source_digests=digests,
        language=language,
        executive_summary=executive_summary,
        cards=cards,
        quiz=quiz,
        markdown=markdown,
    )


def validate_bilingual_alignment(
    primary: PlanSummaryReport, alternate: PlanSummaryReport
) -> None:
    """Require Korean and English reports to describe the same evidence map."""
    if {primary.language, alternate.language} != {"ko", "en"}:
        raise ReportFormatError("bilingual reports must contain one ko and one en report")
    comparisons = (
        ("Date", primary.date, alternate.date),
        ("sources", primary.sources, alternate.sources),
        ("source digests", primary.source_digests, alternate.source_digests),
        ("PS IDs", tuple(card.id for card in primary.cards), tuple(card.id for card in alternate.cards)),
        ("categories", tuple(card.category for card in primary.cards), tuple(card.category for card in alternate.cards)),
        ("source references", tuple(card.sources for card in primary.cards), tuple(card.sources for card in alternate.cards)),
        ("QZ IDs", tuple(question.id for question in primary.quiz), tuple(question.id for question in alternate.quiz)),
        ("quiz option counts", tuple(len(question.options) for question in primary.quiz), tuple(len(question.options) for question in alternate.quiz)),
        ("quiz correct-answer indexes", tuple(question.correct_index for question in primary.quiz), tuple(question.correct_index for question in alternate.quiz)),
    )
    for label, left, right in comparisons:
        if left != right:
            raise ReportFormatError(f"bilingual {label} must align")


def source_tag(report: PlanSummaryReport) -> str:
    """Return a readable, collision-safe tag for the ordered source identity."""
    stems: list[str] = []
    for source in report.sources[:4]:
        stem = Path(source).stem
        readable = unicodedata.normalize("NFKC", stem)
        readable = re.sub(r"[^\w]+", "-", readable, flags=re.UNICODE)
        readable = re.sub(r"[-_]+", "-", readable).strip("-").lower()
        stems.append(readable or "source")
    prefix = "-".join(stems)[:80].rstrip("-") or "sources"
    identity = json.dumps(
        list(zip(report.sources, report.source_digests, strict=True)),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"{prefix}-{sha256(identity).hexdigest()[:12]}"


def validate_output_directory(path: Path) -> Path:
    """Create or validate a real artifact directory without following a final symlink."""
    path = Path(path)
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        try:
            path.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            metadata = path.lstat()
        else:
            metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode):
        raise ReportFormatError("output directory must not be a symbolic link")
    if not stat.S_ISDIR(metadata.st_mode):
        raise ReportFormatError("output path must be a directory")
    return path.resolve(strict=True)


def _path_exists(path: Path) -> bool:
    return os.path.lexists(path)


def atomic_write_text(path: Path, content: str) -> None:
    """Atomically publish one new UTF-8 file without overwriting any path."""
    if _path_exists(path):
        raise ReportFormatError(f"output already exists: {path.name}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as error:
            raise ReportFormatError(f"output already exists: {path.name}") from error
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _atomic_write_bundle(items: tuple[tuple[Path, str], ...]) -> None:
    for path, _ in items:
        if _path_exists(path):
            raise ReportFormatError(f"output already exists: {path.name}")
    created: list[Path] = []
    try:
        for path, content in items:
            atomic_write_text(path, content)
            created.append(path)
    except Exception:
        for path in reversed(created):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        raise


def _json_for_script(value: JsonValue) -> str:
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


_INLINE_RE = re.compile(r"`([^`\n]+)`|\*\*(.+?)\*\*")


def _render_inline(value: str) -> str:
    parts: list[str] = []
    cursor = 0
    for match in _INLINE_RE.finditer(value):
        parts.append(html.escape(value[cursor : match.start()], quote=True))
        code, bold = match.groups()
        if code is not None:
            parts.append(f"<code>{html.escape(code, quote=True)}</code>")
        else:
            parts.append(f"<strong>{html.escape(bold, quote=True)}</strong>")
        cursor = match.end()
    parts.append(html.escape(value[cursor:], quote=True))
    return "".join(parts)


def _split_table_row(line: str) -> list[str]:
    row = line.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [cell.strip() for cell in row.split("|")]


def _is_table_delimiter(line: str) -> bool:
    cells = _split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _render_blocks(markdown: str) -> str:
    lines = markdown.splitlines()
    parts: list[str] = []
    cursor = 0
    while cursor < len(lines):
        raw = lines[cursor].strip()
        if not raw:
            cursor += 1
            continue
        if (
            cursor + 1 < len(lines)
            and "|" in lines[cursor]
            and _is_table_delimiter(lines[cursor + 1])
        ):
            headings = _split_table_row(lines[cursor])
            cursor += 2
            rows: list[list[str]] = []
            while cursor < len(lines) and "|" in lines[cursor] and lines[cursor].strip():
                cells = _split_table_row(lines[cursor])
                if len(cells) != len(headings):
                    break
                rows.append(cells)
                cursor += 1
            header = "".join(
                f'<th scope="col">{_render_inline(cell)}</th>' for cell in headings
            )
            body = "".join(
                "<tr>"
                + "".join(f"<td>{_render_inline(cell)}</td>" for cell in row)
                + "</tr>"
                for row in rows
            )
            parts.append(
                '<div class="table-scroll" role="region" aria-label="Plan map" '
                f'tabindex="0"><table><thead><tr>{header}</tr></thead>'
                f"<tbody>{body}</tbody></table></div>"
            )
            continue
        unordered = re.match(r"^[-+*]\s+(\S.*)$", raw)
        ordered = re.match(r"^\d+[.)]\s+(\S.*)$", raw)
        if unordered is not None or ordered is not None:
            expression = r"^[-+*]\s+(\S.*)$" if unordered is not None else r"^\d+[.)]\s+(\S.*)$"
            tag = "ul" if unordered is not None else "ol"
            items: list[str] = []
            while cursor < len(lines):
                match = re.match(expression, lines[cursor].strip())
                if match is None:
                    break
                items.append(f"<li>{_render_inline(match.group(1))}</li>")
                cursor += 1
            parts.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        paragraph: list[str] = [raw]
        cursor += 1
        while cursor < len(lines) and lines[cursor].strip():
            candidate = lines[cursor].strip()
            if re.match(r"^(?:[-+*]|\d+[.)])\s+", candidate):
                break
            if cursor + 1 < len(lines) and _is_table_delimiter(lines[cursor + 1]):
                break
            paragraph.append(candidate)
            cursor += 1
        parts.append(f"<p>{_render_inline(' '.join(paragraph))}</p>")
    return "\n".join(parts)


def _section_markdown(report: PlanSummaryReport, title: str) -> str:
    lines = _source_lines(report.markdown)
    bounds = _section_bounds(lines, title)
    if bounds is None:
        return ""
    start, end = bounds
    start_offset = lines[start].end
    end_offset = lines[end].start if end < len(lines) else len(report.markdown)
    return report.markdown[start_offset:end_offset].strip()


def _language_labels(language: str) -> dict[str, str]:
    if language == "ko":
        return {
            "executive": "핵심 요약",
            "summary": "요약",
            "plan_map": "계획 지도",
            "risks": "위험, 모순 및 미결 질문",
            "quiz": "이해도 퀴즈",
            "sources": "출처",
            "summary_field": "요약",
            "why": "중요한 이유",
            "basis": "출처 근거",
            "explanation": "해설",
        }
    return {
        "executive": "Executive Summary",
        "summary": "Summary",
        "plan_map": "Plan Map",
        "risks": "Risks, Contradictions, and Open Questions",
        "quiz": "Comprehension Quiz",
        "sources": "Sources",
        "summary_field": "Summary",
        "why": "Why it matters",
        "basis": "Source basis",
        "explanation": "Explanation",
    }


def _render_card(card: SummaryCard, labels: dict[str, str]) -> str:
    source_items = "".join(
        f"<li><code>{html.escape(source, quote=True)}</code></li>"
        for source in card.sources
    )
    return (
        f'<details class="summary-card" data-summary-id="{html.escape(card.id, quote=True)}" open>'
        '<summary class="card-summary"><span class="card-heading">'
        f'<span class="summary-id">{html.escape(card.id)}</span>'
        f'<span class="summary-title">{html.escape(card.title)}</span>'
        "</span>"
        f'<span class="badge">{html.escape(card.category)}</span></summary>'
        '<div class="card-panel">'
        '<div class="card-field"><span class="field-label">'
        f'{html.escape(labels["sources"])}</span><ul class="source-chips">{source_items}</ul></div>'
        '<div class="card-field"><span class="field-label">'
        f'{html.escape(labels["summary_field"])}</span><p class="field-value">'
        f"{_render_inline(card.summary)}</p></div>"
        '<div class="card-field"><span class="field-label">'
        f'{html.escape(labels["why"])}</span><p class="field-value">'
        f"{_render_inline(card.why_it_matters)}</p></div>"
        '<div class="card-field"><span class="field-label">Source basis</span>'
        f'<p class="field-value">{_render_inline(card.source_basis)}</p></div>'
        "</div></details>"
    )


def _render_quiz_question(question: QuizQuestion, labels: dict[str, str]) -> str:
    options: list[str] = []
    for index, option in enumerate(question.options):
        letter = chr(ord("A") + index)
        correct = ' data-quiz-correct="true"' if index == question.correct_index else ""
        visible = html.escape(_visible_text(option), quote=True)
        options.append(
            '<li><button type="button" class="quiz-option" '
            f'data-quiz-option="{index}"{correct} aria-pressed="false" '
            f'aria-label="{html.escape(question.id)} {letter}: {visible}">'
            f'<span class="quiz-option-marker" aria-hidden="true">{letter}</span>'
            f'<span class="quiz-option-text">{_render_inline(option)}</span>'
            "</button></li>"
        )
    question_id = html.escape(question.id, quote=True)
    return (
        f'<section class="quiz-question" data-quiz-id="{question_id}">'
        '<h3 class="quiz-question-heading">'
        f'<span class="quiz-id">{question_id}</span>'
        f'<span class="quiz-question-title">{html.escape(question.title)}</span></h3>'
        f'<ol class="quiz-options">{"".join(options)}</ol>'
        '<p class="quiz-status" role="status" data-quiz-status hidden></p>'
        '<details class="quiz-explanation"><summary>'
        f'{html.escape(labels["explanation"])}</summary>'
        f"<p>{_render_inline(question.explanation)}</p></details></section>"
    )


def _render_report_part(report: PlanSummaryReport, *, active: bool) -> str:
    labels = _language_labels(report.language)
    source_items = "".join(
        f"<li><code>{html.escape(source, quote=True)}</code></li>"
        for source in report.sources
    )
    digest_items = "".join(
        f"<li><code>{html.escape(digest, quote=True)}</code></li>"
        for digest in report.source_digests
    )
    cards = "".join(_render_card(card, labels) for card in report.cards)
    sections = [
        '<section class="report-section"><h2 class="section-title">'
        f'{html.escape(labels["executive"])}</h2><div class="executive-summary">'
        f"{_render_blocks(report.executive_summary)}</div></section>",
        '<section class="report-section"><h2 class="section-title">'
        f'{html.escape(labels["summary"])}</h2><div class="card-list">{cards}</div></section>',
    ]
    plan_map = _section_markdown(report, "Plan Map")
    if plan_map:
        sections.append(
            '<section class="report-section"><h2 class="section-title">'
            f'{html.escape(labels["plan_map"])}</h2><div class="generic-block">'
            f"{_render_blocks(plan_map)}</div></section>"
        )
    risks = _section_markdown(report, "Risks, Contradictions, and Open Questions")
    if risks:
        sections.append(
            '<section class="report-section"><h2 class="section-title">'
            f'{html.escape(labels["risks"])}</h2><div class="generic-block">'
            f"{_render_blocks(risks)}</div></section>"
        )
    if report.quiz:
        questions = "".join(
            _render_quiz_question(question, labels) for question in report.quiz
        )
        sections.append(
            '<section class="report-section"><h2 class="section-title">'
            f'{html.escape(labels["quiz"])}</h2><div class="quiz-list">{questions}</div></section>'
        )
    active_class = "language-part is-active" if active else "language-part"
    hidden = "" if active else " hidden"
    return (
        f'<article data-language-part="{report.language}" class="{active_class}" '
        f'{hidden.strip()} data-report-title="Plan Summary Report">'
        '<header class="report-header"><p class="report-overline">Plan Summary</p>'
        '<h1 class="report-title">Plan Summary Report</h1><dl class="metadata">'
        f'<div><dt>Date</dt><dd>{html.escape(report.date)}</dd></div>'
        f'<div><dt>Language</dt><dd>{html.escape(report.language)}</dd></div>'
        f'<div><dt>Sources</dt><dd><ul class="metadata-list">{source_items}</ul></dd></div>'
        f'<div><dt>Source Digests</dt><dd><ul class="metadata-list">{digest_items}</ul></dd></div>'
        "</dl></header>"
        + "".join(sections)
        + "</article>"
    )


def _load_template() -> str:
    path = Path(__file__).resolve().parent.parent / "assets" / "summary-template.html"
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ReportFormatError(f"HTML template could not be read: {error}") from error


def render_html_report(
    primary: PlanSummaryReport,
    alternate: PlanSummaryReport | None = None,
    *,
    theme: str = "auto",
) -> str:
    """Render a self-contained, optionally bilingual plan-summary report."""
    if theme not in {"auto", "light", "dark"}:
        raise ReportFormatError("theme must be one of: auto, light, dark")
    reports = [primary]
    if alternate is not None:
        validate_bilingual_alignment(primary, alternate)
        reports.append(alternate)
        reports.sort(key=lambda report: 0 if report.language == "ko" else 1)
    default = reports[0]
    parts = "\n".join(
        _render_report_part(report, active=index == 0)
        for index, report in enumerate(reports)
    )
    if len(reports) > 1:
        language_buttons = "".join(
            '<button type="button" '
            f'data-set-lang="{report.language}" '
            f'aria-pressed="{"true" if index == 0 else "false"}">'
            f'{"한국어" if report.language == "ko" else "English"}</button>'
            for index, report in enumerate(reports)
        )
        language_control = (
            '<div class="control control--language" role="group" aria-label="Language">'
            f"{language_buttons}</div>"
        )
    else:
        language_control = ""
    sidebar_sources = "<ul class=\"source-list\">" + "".join(
        f"<li><code>{html.escape(source, quote=True)}</code></li>"
        for source in default.sources
    ) + "</ul>"
    payload: JsonValue = {
        report.language: {
            "markdown": report.markdown,
            "cards": [
                {
                    "id": card.id,
                    "title": card.title,
                    "category": card.category,
                    "sources": list(card.sources),
                }
                for card in report.cards
            ],
        }
        for report in reports
    }
    replacements = {
        "__REPORT_LANGUAGE__": default.language,
        "__REPORT_TITLE__": "Plan Summary Report",
        "__DEFAULT_THEME__": theme,
        "__SIDEBAR_SOURCES__": sidebar_sources,
        "__LANGUAGE_CONTROL__": language_control,
        "__REPORT_PARTS__": parts,
        "__SUMMARY_DATA__": _json_for_script(payload),
    }
    template = _load_template()
    for placeholder, replacement in replacements.items():
        count = template.count(placeholder)
        if count != 1:
            raise ReportFormatError(
                f"template placeholder {placeholder} must appear exactly once; found {count}"
            )
        template = template.replace(placeholder, replacement)
    if re.search(r"__[A-Z][A-Z0-9_]+__", template):
        raise ReportFormatError("HTML template contains an unresolved placeholder")
    return template


def generate_bilingual_report_in_directory(
    korean_markdown: str,
    english_markdown: str,
    output_directory: Path,
    *,
    markdown_only: bool = False,
    theme: str = "auto",
) -> tuple[Path, Path, Path | None]:
    """Validate aligned reports and atomically publish their artifacts."""
    korean = parse_report(korean_markdown)
    english = parse_report(english_markdown)
    if korean.language != "ko" or english.language != "en":
        raise ReportFormatError("arguments must be Korean then English reports")
    validate_bilingual_alignment(korean, english)
    directory = validate_output_directory(output_directory)
    stem = f"{korean.date}_{source_tag(korean)}"
    korean_path = directory / f"{stem}.md"
    english_path = directory / f"{stem}.en.md"
    html_path = None if markdown_only else directory / f"{stem}.html"
    items: list[tuple[Path, str]] = [
        (korean_path, korean.markdown),
        (english_path, english.markdown),
    ]
    if html_path is not None:
        items.append((html_path, render_html_report(korean, english, theme=theme)))
    _atomic_write_bundle(tuple(items))
    return korean_path, english_path, html_path


def generate_single_report_in_directory(
    markdown: str,
    output_directory: Path,
    *,
    markdown_only: bool = False,
    theme: str = "auto",
) -> tuple[Path, Path | None]:
    """Publish one explicitly requested language without synthesizing another."""
    report = parse_report(markdown)
    directory = validate_output_directory(output_directory)
    stem = f"{report.date}_{source_tag(report)}"
    suffix = ".en.md" if report.language == "en" else ".md"
    markdown_path = directory / f"{stem}{suffix}"
    html_path = None if markdown_only else directory / f"{stem}.html"
    items: list[tuple[Path, str]] = [(markdown_path, report.markdown)]
    if html_path is not None:
        items.append((html_path, render_html_report(report, theme=theme)))
    _atomic_write_bundle(tuple(items))
    return markdown_path, html_path


def _read_stdin(limit: int) -> str:
    raw = sys.stdin.buffer.read(limit + 1)
    if not raw:
        raise ReportFormatError("standard input must be non-empty")
    if len(raw) > limit:
        raise ReportFormatError(f"standard input exceeds {limit} bytes")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ReportFormatError("standard input must be valid UTF-8") from error


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--bilingual-json-stdin", action="store_true")
    modes.add_argument("--markdown-stdin", action="store_true")
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--markdown-only", action="store_true")
    parser.add_argument("--theme", choices=("auto", "light", "dark"), default="auto")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.bilingual_json_stdin:
            raw = _read_stdin(MAX_BILINGUAL_BYTES)
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as error:
                raise ReportFormatError("bilingual input must be one JSON object") from error
            if not isinstance(payload, dict) or set(payload) != {"ko", "en"}:
                raise ReportFormatError("bilingual input must contain exactly ko and en")
            if not all(isinstance(payload[key], str) for key in ("ko", "en")):
                raise ReportFormatError("bilingual ko and en values must be strings")
            paths = generate_bilingual_report_in_directory(
                payload["ko"],
                payload["en"],
                args.output_directory,
                markdown_only=args.markdown_only,
                theme=args.theme,
            )
        else:
            markdown = _read_stdin(MAX_REPORT_BYTES)
            paths = generate_single_report_in_directory(
                markdown,
                args.output_directory,
                markdown_only=args.markdown_only,
                theme=args.theme,
            )
    except ReportFormatError as error:
        sys.stderr.write(f"plan-summary generator: {error}\n")
        return 2
    except BrokenPipeError:
        return 1

    artifacts = [str(path) for path in paths if path is not None]
    try:
        sys.stdout.write(json.dumps({"artifacts": artifacts}, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    except BrokenPipeError:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
