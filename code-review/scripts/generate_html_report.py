#!/usr/bin/env python3
"""Convert a code review markdown report into a styled, self-contained HTML file.

Usage:
    python generate_html_report.py path/to/report.md [-o output.html]

If -o is not specified, output goes to the same path with .html extension.
Reads the HTML template from ../assets/report-template.html (relative to this script).
"""

import argparse
import html
import re
import sys
from pathlib import Path

SEVERITY_LEVELS = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
SEVERITY_LOWER = {s: s.lower() for s in SEVERITY_LEVELS}


def escape(text: str) -> str:
    return html.escape(text, quote=False)


def convert_inline(text: str) -> str:
    """Convert inline markdown (bold, inline code) to HTML."""
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    return text


def slugify(text: str) -> str:
    """Create a URL-safe ID from heading text."""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[\s]+', '-', text).strip('-')


def parse_table(lines: list[str]) -> str:
    """Convert markdown table lines to an HTML table."""
    if len(lines) < 2:
        return ""
    out = ['<table>', '<thead><tr>']
    headers = [c.strip() for c in lines[0].strip('|').split('|')]
    for h in headers:
        out.append(f'  <th>{convert_inline(escape(h))}</th>')
    out.append('</tr></thead><tbody>')

    for row_line in lines[2:]:
        cells = [c.strip() for c in row_line.strip('|').split('|')]
        out.append('<tr>')
        for idx, cell in enumerate(cells):
            cell_html = convert_inline(escape(cell))
            css = ""
            if idx == len(headers) - 1 and headers[-1].lower() in ("risk", "overall risk"):
                for sev in SEVERITY_LEVELS:
                    if sev in cell.upper():
                        css = f' class="risk-{SEVERITY_LOWER[sev]}"'
                        break
            out.append(f'  <td{css}>{cell_html}</td>')
        out.append('</tr>')
    out.append('</tbody></table>')
    return '\n'.join(out)


def wrap_code_block(code: str, lang: str) -> str:
    """Wrap escaped code in a pre/code block with a Copy button."""
    lang_attr = f' class="language-{escape(lang)}"' if lang else ''
    return (
        '<div class="code-block-wrapper">'
        f'<button class="copy-btn" type="button">Copy</button>'
        f'<pre><code{lang_attr}>{code}</code></pre>'
        '</div>'
    )


class ReportMetadata:
    """Metadata parsed from the report header."""

    def __init__(self) -> None:
        self.title: str = "Code Review Report"
        self.date: str = ""
        self.reviewer: str = ""
        self.scope: str = ""
        self.repository: str = ""

    def parse_line(self, line: str) -> bool:
        """Try to extract a metadata field. Return True if consumed."""
        for key, attr in (
            ("Date:", "date"), ("Reviewer:", "reviewer"),
            ("Scope:", "scope"), ("Repository:", "repository"),
        ):
            pattern = f"**{key}**"
            if pattern in line:
                self.__dict__[attr] = line.split(pattern, 1)[1].strip()
                return True
        return False


class SidebarEntry:
    """A sidebar navigation entry."""

    def __init__(self, text: str, anchor: str, *, indent: bool = False) -> None:
        self.text = text
        self.anchor = anchor
        self.indent = indent


def detect_severity(heading_text: str) -> str | None:
    upper = heading_text.strip().upper()
    for sev in SEVERITY_LEVELS:
        if upper == sev:
            return sev
    return None


def parse_markdown(md: str) -> tuple[str, ReportMetadata, list[SidebarEntry]]:
    """Parse the markdown report and return (html_content, metadata, sidebar_entries)."""
    lines = md.split('\n')
    meta = ReportMetadata()
    sidebar: list[SidebarEntry] = []
    out: list[str] = []
    i, total = 0, len(lines)
    current_severity: str | None = None
    in_finding_body = False
    list_items: list[str] = []

    def close_finding() -> None:
        nonlocal in_finding_body
        if in_finding_body:
            out.append('</div></details>')
            in_finding_body = False

    def flush_list(items: list[str]) -> None:
        if items:
            out.append('<ul>')
            for item in items:
                out.append(f'<li>{convert_inline(escape(item))}</li>')
            out.append('</ul>')
            items.clear()

    while i < total:
        line = lines[i]
        stripped = line.strip()

        # Fenced code block
        if stripped.startswith('```'):
            flush_list(list_items)
            lang = stripped[3:].strip()
            code_lines: list[str] = []
            i += 1
            while i < total and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            out.append(wrap_code_block(escape('\n'.join(code_lines)), lang))
            i += 1
            continue

        # Table (header row followed by separator row)
        if stripped.startswith('|') and i + 1 < total:
            next_stripped = lines[i + 1].strip()
            if re.match(r'^\|[\s\-:|]+\|$', next_stripped):
                flush_list(list_items)
                table_lines = [stripped, next_stripped]
                i += 2
                while i < total and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i].strip())
                    i += 1
                out.append(parse_table(table_lines))
                continue

        # Horizontal rule
        if re.match(r'^-{3,}$', stripped):
            flush_list(list_items)
            out.append('<hr>')
            i += 1
            continue

        # H1
        if stripped.startswith('# ') and not stripped.startswith('## '):
            flush_list(list_items)
            text = stripped[2:].strip()
            meta.title = text
            out.append(f'<h1>{escape(text)}</h1>')
            i += 1
            continue

        # H2
        if stripped.startswith('## '):
            flush_list(list_items)
            close_finding()
            current_severity = None
            text = stripped[3:].strip()
            anchor = slugify(text)
            sidebar.append(SidebarEntry(text, anchor))
            out.append(f'<h2 id="{anchor}">{escape(text)}</h2>')
            i += 1
            continue

        # H3 (severity headers inside Findings)
        if stripped.startswith('### '):
            flush_list(list_items)
            close_finding()
            text = stripped[4:].strip()
            sev = detect_severity(text)
            anchor = slugify(text)
            if sev:
                current_severity = sev
                sl = SEVERITY_LOWER[sev]
                sidebar.append(SidebarEntry(text, anchor, indent=True))
                out.append(
                    f'<h3 id="{anchor}" class="severity-{sl}">'
                    f'{escape(text)} <span class="badge badge-{sl}">{sev}</span></h3>'
                )
            else:
                current_severity = None
                out.append(f'<h3 id="{anchor}">{escape(text)}</h3>')
            i += 1
            continue

        # H4 (individual findings)
        if stripped.startswith('#### '):
            flush_list(list_items)
            close_finding()
            text = stripped[5:].strip()
            anchor = slugify(text)
            sl = SEVERITY_LOWER.get(current_severity, "") if current_severity else ""
            finding_cls = f" finding-{sl}" if sl else ""
            open_attr = " open" if current_severity in ("CRITICAL", "HIGH") else ""
            badge = f'<span class="badge badge-{sl}">{current_severity}</span>' if sl else ""
            out.append(
                f'<details class="finding{finding_cls}"{open_attr} id="{anchor}">'
                f'<summary>{badge}{escape(text)}</summary>'
                f'<div class="finding-body">'
            )
            in_finding_body = True
            i += 1
            continue

        # Metadata lines (bold key-value in header)
        if stripped.startswith('**') and meta.parse_line(stripped):
            out.append(f'<p>{convert_inline(escape(stripped))}</p>')
            i += 1
            continue

        # List items
        if re.match(r'^[-*]\s', stripped):
            list_items.append(re.sub(r'^[-*]\s+', '', stripped))
            i += 1
            continue

        flush_list(list_items)

        # Italic footer line
        if stripped.startswith('_') and stripped.endswith('_') and len(stripped) > 2:
            out.append(
                f'<div class="report-footer">{convert_inline(escape(stripped[1:-1]))}</div>'
            )
            i += 1
            continue

        # Empty line
        if not stripped:
            i += 1
            continue

        # Regular paragraph (collect consecutive non-special lines)
        para_lines = [stripped]
        i += 1
        while i < total:
            ns = lines[i].strip()
            if not ns or ns[0] in '#|_' or ns.startswith('```') or ns.startswith('---') \
                    or re.match(r'^[-*]\s', ns):
                break
            para_lines.append(ns)
            i += 1
        out.append(f'<p>{convert_inline(escape(" ".join(para_lines)))}</p>')

    flush_list(list_items)
    close_finding()
    return '\n'.join(out), meta, sidebar


def build_sidebar_html(entries: list[SidebarEntry]) -> str:
    if not entries:
        return '<ul></ul>'
    parts = ['<ul>']
    for entry in entries:
        css = ' class="nav-severity"' if entry.indent else ''
        parts.append(f'<li{css}><a href="#{entry.anchor}">{escape(entry.text)}</a></li>')
    parts.append('</ul>')
    return '\n'.join(parts)


def load_template() -> str:
    """Load the HTML template from ../assets/report-template.html."""
    script_dir = Path(__file__).resolve().parent
    template_path = script_dir.parent / "assets" / "report-template.html"
    if not template_path.exists():
        print(f"Error: template not found at {template_path}", file=sys.stderr)
        sys.exit(1)
    return template_path.read_text(encoding="utf-8")


def assemble(template: str, content: str, meta: ReportMetadata,
             sidebar_html: str) -> str:
    """Replace placeholders in the template with generated content."""
    result = template
    result = result.replace("__REPORT_TITLE__", escape(meta.title))
    result = result.replace("__REPORT_DATE__", escape(meta.date))
    result = result.replace("__REPORT_CONTENT__", content)
    result = result.replace("__SIDEBAR_CONTENT__", sidebar_html)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a code review markdown report to a self-contained HTML file."
    )
    parser.add_argument("input", help="Path to the markdown report file")
    parser.add_argument(
        "-o", "--output",
        help="Output HTML file path (default: same name with .html extension)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_suffix(".html")
    md_text = input_path.read_text(encoding="utf-8")
    template = load_template()

    content_html, meta, sidebar_entries = parse_markdown(md_text)
    sidebar_html = build_sidebar_html(sidebar_entries)
    final_html = assemble(template, content_html, meta, sidebar_html)

    output_path.write_text(final_html, encoding="utf-8")
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
