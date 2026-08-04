from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_TEMPLATE = (
    ROOT
    / "code-review"
    / "skills"
    / "diff-summary"
    / "assets"
    / "summary-template.html"
)
PLAN_SUMMARY_TEMPLATE = (
    ROOT
    / "plan-summary"
    / "skills"
    / "plan-summary"
    / "assets"
    / "summary-template.html"
)
TEMPLATES = {
    "diff-summary": SUMMARY_TEMPLATE,
    "diff-viewer": (
        ROOT
        / "code-review"
        / "skills"
        / "diff-viewer"
        / "assets"
        / "diff-template.html"
    ),
    "code-review": (
        ROOT
        / "code-review"
        / "skills"
        / "code-review"
        / "assets"
        / "report-template.html"
    ),
}
THEME_SELECTORS = {
    "diff-summary": ("body", 'body[data-theme="dark"]'),
    "diff-viewer": (":root", 'html[data-page-theme="dark"]'),
    "code-review": (":root", 'html[data-page-theme="dark"]'),
}
LEGACY_TOKENS = {
    "diff-summary": (),
    "diff-viewer": ("bg", "surface", "surface-muted", "text"),
    "code-review": ("bg", "surface", "surface-muted", "text"),
}
PRIMARY_CONTROL_SELECTORS = {
    "diff-viewer": (
        'button[aria-pressed="true"]',
        ".copy-md-btn",
        ".btn-comment.btn-save",
    ),
    "code-review": (
        '.control button[aria-pressed="true"]',
        ".copy-md-btn",
        ".diff-toggle.active",
        ".btn-comment.btn-save",
    ),
}
PRESSED_CONTROL_SELECTORS = {
    "diff-summary": '.control button[aria-pressed="true"]',
    "diff-viewer": 'button[aria-pressed="true"]',
    "code-review": '.control button[aria-pressed="true"]',
}
DESTRUCTIVE_CONTROL_SELECTORS = {
    "diff-viewer": (
        ".clear-comments-btn:hover:not(:disabled)",
        ".btn-comment.btn-delete:hover",
    ),
    "code-review": (
        ".clear-comments-btn:hover:not(:disabled)",
        ".btn-comment.btn-delete:hover",
    ),
}
SMALL_SIDEBAR_TEXT_SELECTORS = {
    "diff-viewer": (
        ".icon-btn",
        ".brand",
        ".repo",
        ".nav-list a",
        ".comment-panel-title",
        ".comment-list button",
        ".comment-list .comment-empty",
    ),
    "code-review": (
        ".icon-btn",
        ".brand",
        ".repo",
        ".nav-lang a",
        ".comment-panel-title",
        ".comment-list button",
        ".comment-list .comment-empty",
        ".copy-md-btn.secondary",
    ),
}
TOKENS = (
    "background",
    "foreground",
    "card",
    "card-foreground",
    "popover",
    "popover-foreground",
    "muted",
    "muted-foreground",
    "primary",
    "primary-foreground",
    "secondary",
    "secondary-foreground",
    "accent",
    "accent-foreground",
    "destructive",
    "destructive-foreground",
    "border",
    "input",
    "ring",
    "radius",
    "radius-control",
    "font-sans",
    "font-mono",
)
THEME_COLOR_TOKENS = TOKENS[:-4]
ROOT_TOKENS = TOKENS[-4:]
# One row per token, (light, dark). Templates declare the pair once through
# CSS light-dark(), so these are the only two values that can ever apply.
EXPECTED_THEME = {
    "background": ("#fdfcfc", "#201d1d"),
    "foreground": ("#201d1d", "#fdfcfc"),
    "card": ("#fdfcfc", "#201d1d"),
    "card-foreground": ("#201d1d", "#fdfcfc"),
    "popover": ("#fdfcfc", "#302c2c"),
    "popover-foreground": ("#201d1d", "#fdfcfc"),
    "muted": ("#f8f7f7", "#302c2c"),
    "muted-foreground": ("#646262", "#9a9898"),
    "primary": ("#201d1d", "#fdfcfc"),
    "primary-foreground": ("#fdfcfc", "#201d1d"),
    "secondary": ("#f1eeee", "#302c2c"),
    "secondary-foreground": ("#302c2c", "#fdfcfc"),
    "accent": ("#f1eeee", "#302c2c"),
    "accent-foreground": ("#201d1d", "#fdfcfc"),
    "destructive": ("#d70015", "#ff3b30"),
    "destructive-foreground": ("#fdfcfc", "#201d1d"),
    "border": ("#e0dede", "#3f3c3c"),
    "input": ("#646262", "#646262"),
    "ring": ("#201d1d", "#fdfcfc"),
}
EXPECTED_LIGHT_THEME = {name: pair[0] for name, pair in EXPECTED_THEME.items()}
EXPECTED_DARK_THEME = {name: pair[1] for name, pair in EXPECTED_THEME.items()}
EXPECTED_LIGHT_SHADOW = "none"
EXPECTED_DARK_SHADOW = "none"
EXPECTED_PRINT_THEME = {
    **EXPECTED_LIGHT_THEME,
    "background": "#ffffff",
}
PRINT_THEME_SELECTORS = {
    "diff-summary": (
        "body,\n"
        '      body[data-default-theme="dark"]:not([data-theme]),\n'
        '      body[data-theme="dark"],\n'
        '      body[data-default-theme="auto"]:not([data-theme])'
    ),
    "diff-viewer": ':root,\n      html[data-page-theme="dark"]',
    "code-review": ':root,\n      html[data-page-theme="dark"]',
}
STATUS_TOKENS = (
    "status-success",
    "status-success-soft",
    "status-warning",
    "status-warning-soft",
    "status-danger",
    "status-danger-soft",
    "status-info",
    "status-info-soft",
)
# Tailwind palette steps, following the shadcn badge custom-colors recipe:
# light is text-{family}-700 on bg-{family}-50, dark is -300 on -950.
EXPECTED_STATUS = {
    "status-success": ("#008236", "#7bf1a8"),
    "status-success-soft": ("#f0fdf4", "#032e15"),
    "status-warning": ("#a65f00", "#ffdf20"),
    "status-warning-soft": ("#fefce8", "#432004"),
    "status-danger": ("#c10007", "#ffa2a2"),
    "status-danger-soft": ("#fef2f2", "#460809"),
    "status-info": ("#1447e6", "#8ec5ff"),
    "status-info-soft": ("#eff6ff", "#162456"),
}
EXPECTED_LIGHT_STATUS = {name: pair[0] for name, pair in EXPECTED_STATUS.items()}
EXPECTED_DARK_STATUS = {name: pair[1] for name, pair in EXPECTED_STATUS.items()}
STATUS_FOREGROUNDS = (
    "status-success",
    "status-warning",
    "status-danger",
    "status-info",
)
CODE_DIFF_TEXT_TOKENS = (
    "code-add-text",
    "code-del-text",
    "code-hunk-text",
)
EXPECTED_LIGHT_CODE_DIFF_TEXT = {
    "code-add-text": "var(--status-success)",
    "code-del-text": "var(--status-danger)",
    "code-hunk-text": "var(--status-info)",
}
EXPECTED_DARK_CODE_DIFF_TEXT = {
    "code-add-text": "#8fe3a7",
    "code-del-text": "#ffb3ba",
    "code-hunk-text": "#a9c2ff",
}
# diff-summary has no code-scheme picker, so its dark diff text follows the page
# theme (None — read the light-dark() pair); the other two follow whichever
# Highlight.js tone the reader selected.
DARK_CODE_TONE_SELECTORS = {
    "diff-summary": None,
    "diff-viewer": 'html[data-code-tone="dark"]',
    "code-review": 'html[data-code-tone="dark"]',
}
SOFT_STATUS_PAIRS = (
    ("status-success", "status-success-soft"),
    ("status-warning", "status-warning-soft"),
    ("status-danger", "status-danger-soft"),
    ("status-info", "status-info-soft"),
)
REPORT_STATUS_ALIASES = {
    "code-review": {
        "critical": "status-danger",
        "medium": "status-warning",
        "low": "status-info",
        "info": "muted-foreground",
        "add-hue": "status-success",
        "del-hue": "status-danger",
        "hunk-hue": "status-info",
    },
    "diff-summary": {
        "impact-high": "status-warning",
        "impact-high-soft": "status-warning-soft",
        "positive": "status-success",
        "positive-soft": "status-success-soft",
        "destructive-soft": "status-danger-soft",
        "add-hue": "status-success",
        "del-hue": "status-danger",
        "hunk-hue": "status-info",
    },
    "diff-viewer": {
        "add-text": "status-success",
        "add-line": "status-success-soft",
        "del-text": "status-danger",
        "del-line": "status-danger-soft",
        "add-hue": "status-success",
        "del-hue": "status-danger",
        "hunk-hue": "status-info",
    },
}
EXPECTED_HIGH_SEVERITY = {
    "light": {"high": "#ca3500", "high-soft": "#fff7ed"},
    "dark": {"high": "#ffb86a", "high-soft": "#441306"},
}
SEVERITY_BADGE_PAIRS = {
    "critical": ("status-danger", "status-danger-soft"),
    "high": ("high", "high-soft"),
    "medium": ("status-warning", "status-warning-soft"),
    "low": ("status-info", "status-info-soft"),
    "info": ("muted-foreground", "muted"),
}
LEGACY_ZINC_VALUES = (
    "#09090b",
    "#f4f4f5",
    "#71717a",
    "#18181b",
    "#fafafa",
    "#e4e4e7",
    "#27272a",
    "#a1a1aa",
    "#d4d4d8",
    "#dc2626",
    "#7f1d1d",
)
EXPECTED_ROOT_TOKENS = {
    # Two radii and no third: containers are sharp, interactive elements are 4px.
    "radius": "0px",
    "radius-control": "4px",
    # One monospaced face carries every text role. The Latin mono faces have no
    # Hangul, so per-glyph fallback reaches the Korean mono faces for prose
    # while Latin keeps its mono metrics.
    "font-sans": (
        '"Berkeley Mono", "JetBrains Mono", "IBM Plex Mono", ui-monospace, '
        "SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", "
        'D2Coding, "Nanum Gothic Coding", "Courier New", monospace'
    ),
    "font-mono": (
        '"Berkeley Mono", "JetBrains Mono", "IBM Plex Mono", ui-monospace, '
        "SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", "
        'D2Coding, "Nanum Gothic Coding", "Courier New", monospace'
    ),
}
KOREAN_FACES = ("D2Coding", '"Nanum Gothic Coding"')
PROSE_KEEP_ALL_SELECTORS = {
    "diff-summary": (
        "#report-main > h2",
        "#report-main > p",
        ".summary-title",
        ".comment-text",
        ".quiz-option-text",
    ),
    "diff-viewer": (
        "h1",
        ".metric span",
        ".comment-body",
        ".empty-state h2",
    ),
    "code-review": (
        "h2",
        "p",
        ".finding-summary-text",
        ".comment-body",
    ),
}
# keep-all must never reach code: a broken identifier is worse than an overflow.
CODE_SELECTOR_MARKERS = (
    "pre",
    "code",
    ".diff-line",
    ".code-line",
    ".diff-code",
    ".repo",
    ".language-badge",
)
TABULAR_NUMERAL_SELECTORS = {
    "diff-summary": (".align-right",),
    "diff-viewer": (".line-no", ".metric strong"),
    "code-review": (".diff-ln",),
}


def css_rule(source: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{", source)
    if match is None:
        raise AssertionError(f"CSS rule not found: {selector}")
    opening_brace = source.index("{", match.start())
    depth = 1
    cursor = opening_brace + 1
    while cursor < len(source) and depth:
        if source[cursor] == "{":
            depth += 1
        elif source[cursor] == "}":
            depth -= 1
        cursor += 1
    if depth:
        raise AssertionError(f"unterminated CSS rule: {selector}")
    return source[opening_brace + 1 : cursor - 1]


def css_rule_containing_selector(source: str, selector: str) -> str:
    for match in re.finditer(
        rf"[^{{}}]*{re.escape(selector)}[^{{}}]*\{{",
        source,
    ):
        opening_brace = source.index("{", match.start())
        depth = 1
        cursor = opening_brace + 1
        while cursor < len(source) and depth:
            if source[cursor] == "{":
                depth += 1
            elif source[cursor] == "}":
                depth -= 1
            cursor += 1
        if depth:
            raise AssertionError(f"unterminated CSS rule: {selector}")
        rule = source[opening_brace + 1 : cursor - 1]
        if "color:" in rule:
            return rule
    raise AssertionError(f"CSS color rule not found: {selector}")


def custom_properties(rule: str) -> dict[str, str]:
    return {
        name: value.strip()
        for name, value in re.findall(r"--([\w-]+)\s*:\s*([^;{}]+);", rule)
    }


def selected_properties(
    declarations: dict[str, str],
    names: tuple[str, ...],
) -> dict[str, str]:
    return {name: value for name, value in declarations.items() if name in names}


def resolve_scheme(value: str, theme: str) -> str:
    """Pick one side of a light-dark() pair; pass every other value through."""
    if not value.startswith("light-dark(") or not value.endswith(")"):
        return value
    inner = value[len("light-dark(") : -1]
    depth = 0
    for index, character in enumerate(inner):
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
        elif character == "," and depth == 0:
            side = inner[:index] if theme == "light" else inner[index + 1 :]
            return side.strip()
    raise AssertionError(f"malformed light-dark(): {value}")


def theme_declarations(source: str, template: str, theme: str) -> dict[str, str]:
    """Every token a template applies in one theme.

    Colour tokens live at a single light-dark() site on the base rule; the mode
    rule carries only what light-dark() cannot express.
    """
    base, mode = THEME_SELECTORS[template]
    declared = {
        name: resolve_scheme(value, theme)
        for name, value in custom_properties(css_rule(source, base)).items()
    }
    if theme == "dark":
        declared.update(custom_properties(css_rule(source, mode)))
    return declared


def css_rule_containing_declaration(source: str, declaration: str) -> dict[str, str]:
    """Return the selector list and body of the rule declaring ``declaration``."""
    match = re.search(
        rf"([^{{}}]*)\{{([^{{}}]*{re.escape(declaration)}[^{{}}]*)\}}",
        source,
    )
    if match is None:
        raise AssertionError(f"no CSS rule declares: {declaration}")
    return {"selector": match.group(1).strip(), "body": match.group(2)}


def color_mix_expressions(source: str) -> list[str]:
    """Extract every complete color-mix(...) expression, nested parens included."""
    expressions: list[str] = []
    for match in re.finditer(r"color-mix\(", source):
        depth = 0
        cursor = match.end() - 1
        while cursor < len(source):
            if source[cursor] == "(":
                depth += 1
            elif source[cursor] == ")":
                depth -= 1
                if depth == 0:
                    expressions.append(source[match.start() : cursor + 1])
                    break
            cursor += 1
        else:
            raise AssertionError(f"unterminated color-mix at offset {match.start()}")
    return expressions


def resolve_token(value: str, declarations: dict[str, str]) -> str:
    seen: set[str] = set()
    current = value
    while True:
        token_match = re.fullmatch(r"var\(--([\w-]+)\)", current)
        if token_match is None:
            return current
        token = token_match.group(1)
        if token in seen:
            raise AssertionError(f"cyclic CSS token alias: {token}")
        seen.add(token)
        current = declarations[token]


def contrast_ratio(first: str, second: str) -> float:
    def luminance(hex_color: str) -> float:
        channels = [
            int(hex_color[index : index + 2], 16) / 255 for index in range(1, 7, 2)
        ]
        linear = [
            channel / 12.92
            if channel <= 0.04045
            else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        ]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class HtmlReportStyleContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.template = SUMMARY_TEMPLATE.read_text(encoding="utf-8")
        cls.templates = {
            name: path.read_text(encoding="utf-8") for name, path in TEMPLATES.items()
        }
        cls.root_declarations = custom_properties(css_rule(cls.template, ":root"))
        cls.light_declarations = theme_declarations(cls.template, "diff-summary", "light")
        cls.dark_declarations = theme_declarations(cls.template, "diff-summary", "dark")

    def test_every_html_report_uses_exact_shared_light_and_dark_values(
        self,
    ) -> None:
        for name, source in self.templates.items():
            root_declarations = custom_properties(css_rule(source, ":root"))
            light_declarations = theme_declarations(source, name, "light")
            dark_declarations = theme_declarations(source, name, "dark")

            with self.subTest(template=name, theme="root"):
                self.assertEqual(
                    selected_properties(root_declarations, ROOT_TOKENS),
                    EXPECTED_ROOT_TOKENS,
                )
            with self.subTest(template=name, theme="light"):
                self.assertEqual(
                    selected_properties(
                        light_declarations,
                        THEME_COLOR_TOKENS,
                    ),
                    EXPECTED_LIGHT_THEME,
                )
            with self.subTest(template=name, theme="dark"):
                self.assertEqual(
                    selected_properties(
                        dark_declarations,
                        THEME_COLOR_TOKENS,
                    ),
                    EXPECTED_DARK_THEME,
                )

    def test_plan_summary_template_matches_shared_color_and_focus_contracts(
        self,
    ) -> None:
        source = PLAN_SUMMARY_TEMPLATE.read_text(encoding="utf-8")

        for token, (light, dark) in EXPECTED_THEME.items():
            with self.subTest(token=token):
                self.assertIn(f"--{token}: light-dark({light}, {dark});", source)
        for token, value in EXPECTED_ROOT_TOKENS.items():
            with self.subTest(root_token=token):
                self.assertIn(f"--{token}: {value};", source)
        self.assertRegex(source, r":focus-visible\s*\{[^}]*outline:")
        self.assertIn("@media (prefers-reduced-motion: reduce)", source)
        self.assertIn("@media print", source)
        self.assertIn("word-break: keep-all", source)
        self.assertIn("overflow-wrap: anywhere", source)

    def test_theme_switches_through_one_segmented_control_idiom(self) -> None:
        """A menu hides the active mode; a segmented group shows it at a glance."""
        for name, source in self.templates.items():
            with self.subTest(template=name, contract="group"):
                self.assertRegex(
                    source,
                    r'<div class="control control--theme" role="group"'
                    r'[^>]*aria-label="Theme">',
                )
            for mode in ("auto", "light", "dark"):
                with self.subTest(template=name, mode=mode):
                    self.assertRegex(
                        source,
                        rf'<button type="button" data-set-theme="{mode}"',
                    )
            with self.subTest(template=name, contract="no-menu-or-cycle"):
                self.assertNotIn("data-theme-select", source)
                self.assertNotIn("data-theme-toggle", source)
            with self.subTest(template=name, contract="pressed"):
                # diff-viewer styles every pressed button; the other two scope to
                # .control. Either way exactly one segment reads as selected.
                rule = css_rule(source, PRESSED_CONTROL_SELECTORS[name])
                self.assertRegex(rule, r"background:\s*var\(--primary\)\s*;")
                self.assertRegex(rule, r"color:\s*var\(--primary-foreground\)\s*;")
            with self.subTest(template=name, contract="icon-and-label"):
                self.assertRegex(
                    css_rule(source, ".control--theme button"),
                    r"display:\s*inline-flex\s*;",
                )
                self.assertEqual(source.count('class="control-text"'), 3)

    def test_every_translation_key_in_markup_exists_in_both_tables(self) -> None:
        """A key with no entry renders as the key itself — e.g. a "themeAuto" button."""
        for name in ("diff-viewer", "code-review"):
            source = self.templates[name]
            keys = set(
                re.findall(
                    r'data-i18n(?:-label|-placeholder)?="([\w.]+)"',
                    source,
                )
            )
            with self.subTest(template=name, contract="keys-found"):
                self.assertTrue(keys)
            for key in sorted(keys):
                with self.subTest(template=name, key=key):
                    # One declaration per language table, at minimum.
                    self.assertGreaterEqual(
                        len(re.findall(rf"\b{re.escape(key)}:", source)),
                        2,
                        f"{key} is not declared in both I18N tables",
                    )

    def test_every_report_runtime_marks_exactly_one_pressed_theme(self) -> None:
        for name, source in self.templates.items():
            with self.subTest(template=name):
                self.assertRegex(
                    source,
                    r'"aria-pressed",\s*\n?\s*String\(\s*\n?\s*'
                    r'(?:button|mode)[^)]*\)',
                )
                self.assertIn("[data-set-theme]", source)

    def test_every_html_report_ships_the_shared_accessibility_shell(self) -> None:
        skip_targets = {
            "diff-summary": "#report-main",
            "diff-viewer": "#top",
            "code-review": "#top",
        }
        for name, source in self.templates.items():
            with self.subTest(template=name, contract="skip-link"):
                self.assertRegex(
                    source,
                    rf'<a class="skip-link" href="{re.escape(skip_targets[name])}"',
                )
                rule = css_rule(source, ".skip-link")
                self.assertRegex(rule, r"position:\s*fixed\s*;")
                self.assertRegex(rule, r"transform:\s*translateY\(-200%\)\s*;")
                self.assertRegex(
                    css_rule(source, ".skip-link:focus"),
                    r"transform:\s*translateY\(0\)\s*;",
                )
            with self.subTest(template=name, contract="live-region"):
                self.assertEqual(source.count('role="status"'), 1)
                self.assertIn('aria-live="polite"', source)
                self.assertIn('aria-atomic="true"', source)
                self.assertRegex(
                    css_rule(source, ".status-region"),
                    r"position:\s*fixed\s*;",
                )
            with self.subTest(template=name, contract="reduced-motion"):
                self.assertIn("@media (prefers-reduced-motion: reduce)", source)
                reduced = css_rule(source, "@media (prefers-reduced-motion: reduce)")
                self.assertRegex(reduced, r"scroll-behavior:\s*auto\s*!important\s*;")
                self.assertRegex(
                    reduced,
                    r"transition-duration:\s*0\.01ms\s*!important\s*;",
                )
            with self.subTest(template=name, contract="print"):
                printed = css_rule(source, "@media print")
                self.assertIn(".status-region", printed)
            with self.subTest(template=name, contract="ring-reserved-for-focus"):
                self.assertEqual(source.count("var(--ring)"), 1)

    def test_every_report_runtime_announces_outcomes_to_the_live_region(self) -> None:
        for name, source in self.templates.items():
            with self.subTest(template=name):
                self.assertRegex(source, r"function\s+announce\s*\(")
                self.assertIn('getElementById("report-status")', source)

    def test_no_html_report_uses_a_placeholder_glyph_as_an_affordance(self) -> None:
        """Code points inherit text metrics and render per platform; icons do not."""
        for name, source in self.templates.items():
            for glyph in ("&#9776;", "&#x276E;", "&#x276F;", "▶", "&#9660;"):
                with self.subTest(template=name, glyph=glyph):
                    self.assertNotIn(glyph, source)

    def test_no_html_report_ships_a_vector_icon(self) -> None:
        """Brackets are the icon set, so no <svg> may appear in any report."""
        for name, source in self.templates.items():
            with self.subTest(template=name):
                self.assertNotIn("<svg", source)

    def test_every_bracket_affordance_is_decorative_text(self) -> None:
        """The two icon-only sidebar toggles carry a bracket, not a glyph asset.

        Every other control already names itself in text, so it needs no mark at
        all. The bracket is hidden from assistive tech because the button's own
        aria-label already says what it does.
        """
        for name, source in self.templates.items():
            for marker, bracket in (
                ("data-sidebar-expand", "[&gt;]"),
                ("data-sidebar-toggle", "[&lt;]"),
            ):
                with self.subTest(template=name, marker=marker):
                    self.assertIn(
                        f'<span class="icon" aria-hidden="true">{bracket}</span>',
                        source,
                    )
            with self.subTest(template=name, contract="count"):
                self.assertEqual(source.count('class="icon"'), 2)
            with self.subTest(template=name, contract="sized-by-text"):
                rule = css_rule(source, ".icon")
                self.assertNotRegex(rule, r"width:")
                self.assertNotRegex(rule, r"height:")

    def test_disclosure_indicators_stay_css_only(self) -> None:
        """<details> must open without JavaScript, so the marker is drawn in CSS.

        A bracket pair also states the state in the report's own vocabulary:
        [+] is closed, [-] is open, and both are plain text in the one face.
        """
        for name, selector, open_selector in (
            (
                "diff-summary",
                ".card-summary::before",
                ".summary-card[open] .card-summary::before",
            ),
            (
                "code-review",
                ".finding-summary-text::before",
                "details.finding[open] > summary .finding-summary-text::before",
            ),
        ):
            source = self.templates[name]
            with self.subTest(template=name, contract="closed"):
                self.assertRegex(css_rule(source, selector), r'content:\s*"\[\+\]"\s*;')
            with self.subTest(template=name, contract="open"):
                self.assertRegex(
                    css_rule(source, open_selector),
                    r'content:\s*"\[-\]"\s*;',
                )
            with self.subTest(template=name, contract="no-drawn-angle"):
                self.assertNotRegex(css_rule(source, selector), r"transform:\s*rotate")

    def test_every_details_element_uses_the_shared_disclosure_marker(self) -> None:
        """One expand affordance per report — no native triangle beside a custom one."""
        for name, selectors in (
            ("diff-summary", (".card-summary", ".quiz-explanation summary")),
            ("code-review", ("details.finding > summary",)),
        ):
            source = self.templates[name]
            for selector in selectors:
                with self.subTest(template=name, selector=selector):
                    rule = css_rule(source, selector)
                    self.assertRegex(rule, r"list-style:\s*none\s*;")
                    self.assertRegex(
                        source,
                        rf"{re.escape(selector)}::-webkit-details-marker\s*\{{"
                        r"[^}]*display:\s*none",
                    )
        self.assertRegex(
            css_rule(
                self.templates["diff-summary"],
                ".quiz-explanation summary::before",
            ),
            r'content:\s*"\[\+\]"\s*;',
        )
        self.assertRegex(
            css_rule(
                self.templates["diff-summary"],
                ".quiz-explanation[open] summary::before",
            ),
            r'content:\s*"\[-\]"\s*;',
        )

    def test_no_html_report_stylesheet_references_an_external_resource(self) -> None:
        """Every report must render identically with no network access."""
        for name, source in self.templates.items():
            with self.subTest(template=name):
                self.assertNotIn("url(", source)

    def test_every_html_report_declares_the_korean_aware_font_stacks(self) -> None:
        for name, source in self.templates.items():
            declarations = custom_properties(css_rule(source, ":root"))
            with self.subTest(template=name, contract="exact"):
                self.assertEqual(
                    selected_properties(declarations, ROOT_TOKENS),
                    EXPECTED_ROOT_TOKENS,
                )
            for face in KOREAN_FACES:
                with self.subTest(template=name, face=face):
                    self.assertIn(face, declarations["font-sans"])
            with self.subTest(template=name, contract="latin-first"):
                stack = declarations["font-sans"]
                self.assertLess(
                    stack.index("ui-monospace"),
                    stack.index("D2Coding"),
                )
            with self.subTest(template=name, contract="one-face"):
                self.assertEqual(
                    declarations["font-sans"],
                    declarations["font-mono"],
                )

    def test_every_html_report_breaks_korean_prose_on_word_boundaries(self) -> None:
        for name, selectors in PROSE_KEEP_ALL_SELECTORS.items():
            source = self.templates[name]
            prose_rule = css_rule_containing_declaration(
                source,
                "word-break: keep-all",
            )
            for selector in selectors:
                with self.subTest(template=name, selector=selector):
                    self.assertIn(selector, prose_rule["selector"])
            with self.subTest(template=name, contract="escape-hatch"):
                self.assertRegex(
                    prose_rule["body"],
                    r"overflow-wrap:\s*break-word\s*;",
                )

    def test_korean_word_breaking_never_reaches_code(self) -> None:
        for name, source in self.templates.items():
            for rule_selector in re.findall(
                r"([^{}]*)\{[^{}]*word-break:\s*keep-all",
                source,
            ):
                selectors = [part.strip() for part in rule_selector.split(",")]
                for selector in selectors:
                    for marker in CODE_SELECTOR_MARKERS:
                        with self.subTest(
                            template=name,
                            selector=selector,
                            marker=marker,
                        ):
                            self.assertNotEqual(selector, marker)
                            self.assertFalse(
                                selector.endswith(" " + marker),
                                f"{selector} applies keep-all to code",
                            )

    def test_numeric_report_surfaces_use_tabular_numerals(self) -> None:
        for name, selectors in TABULAR_NUMERAL_SELECTORS.items():
            source = self.templates[name]
            for selector in selectors:
                with self.subTest(template=name, selector=selector):
                    self.assertRegex(
                        css_rule(source, selector),
                        r"font-variant-numeric:\s*tabular-nums\s*;",
                    )

    def test_radius_vocabulary_is_exactly_two_tokens(self) -> None:
        """Sharp containers, 4px interactive elements, and nothing in between.

        A literal radius is how a third shape sneaks in, so every rule has to
        name one of the two tokens.
        """
        allowed = {"var(--radius)", "var(--radius-control)", "0"}
        for name, source in self.templates.items():
            for value in re.findall(r"border-radius:\s*([^;]+);", source):
                with self.subTest(template=name, value=value.strip()):
                    self.assertIn(value.strip(), allowed)

    def test_no_html_report_paints_a_shadow_or_a_glow(self) -> None:
        """Nothing lifts and nothing haloes; focus is carried by an ink border."""
        for name, source in self.templates.items():
            for value in re.findall(r"box-shadow:\s*([^;]+);", source):
                with self.subTest(template=name, value=value.strip()):
                    self.assertIn(value.strip(), {"none", "var(--shadow)"})

    def test_every_html_report_sits_flat_on_one_canvas(self) -> None:
        """Cards are hairline-bordered blocks on the canvas, not raised surfaces.

        Nothing in the system lifts: the card fill equals the page fill and the
        only separation is the border, so no shadow may exist in either theme.
        """
        for name, source in self.templates.items():
            for theme, expected_shadow in (
                ("light", EXPECTED_LIGHT_SHADOW),
                ("dark", EXPECTED_DARK_SHADOW),
            ):
                declarations = theme_declarations(source, name, theme)
                with self.subTest(template=name, theme=theme, contract="one-canvas"):
                    self.assertEqual(
                        declarations["card"],
                        declarations["background"],
                    )
                with self.subTest(template=name, theme=theme, contract="tints-read"):
                    self.assertNotEqual(
                        declarations["muted"],
                        declarations["background"],
                    )
                    self.assertNotEqual(declarations["border"], declarations["input"])
                with self.subTest(template=name, theme=theme, contract="no-elevation"):
                    self.assertEqual(declarations["shadow"], expected_shadow)

    def test_every_html_report_prints_with_cool_editorial_light_palette(
        self,
    ) -> None:
        for name, source in self.templates.items():
            printed = css_rule(source, "@media print")
            palette = css_rule(printed, PRINT_THEME_SELECTORS[name])
            declarations = custom_properties(palette)

            with self.subTest(template=name):
                self.assertEqual(
                    selected_properties(declarations, THEME_COLOR_TOKENS),
                    EXPECTED_PRINT_THEME,
                )
                self.assertEqual(declarations["shadow"], "none")
                self.assertRegex(palette, r"color-scheme:\s*light\s*;")

    def test_no_core_theme_token_declares_a_legacy_zinc_value(self) -> None:
        for name, source in self.templates.items():
            printed = css_rule(source, "@media print")
            themes = {
                "light": theme_declarations(source, name, "light"),
                "dark": theme_declarations(source, name, "dark"),
                "print": custom_properties(
                    css_rule(printed, PRINT_THEME_SELECTORS[name])
                ),
            }
            for theme, declarations in themes.items():
                core = selected_properties(declarations, THEME_COLOR_TOKENS)
                for token, value in core.items():
                    with self.subTest(template=name, theme=theme, token=token):
                        self.assertNotIn(value, LEGACY_ZINC_VALUES)
                with self.subTest(template=name, theme=theme, token="shadow"):
                    self.assertNotIn(
                        "rgba(16, 24, 40, 0.06)",
                        declarations["shadow"],
                    )

    def test_every_html_report_uses_exact_shared_status_palette(self) -> None:
        for name, source in self.templates.items():
            for theme, expected in (
                ("light", EXPECTED_LIGHT_STATUS),
                ("dark", EXPECTED_DARK_STATUS),
            ):
                declarations = theme_declarations(source, name, theme)
                with self.subTest(template=name, theme=theme, contract="exact"):
                    self.assertEqual(
                        selected_properties(declarations, STATUS_TOKENS),
                        expected,
                    )
                for base, soft in SOFT_STATUS_PAIRS:
                    with self.subTest(
                        template=name,
                        theme=theme,
                        contract="soft-contrast",
                        pair=base,
                    ):
                        self.assertGreaterEqual(
                            contrast_ratio(
                                declarations[base],
                                declarations[soft],
                            ),
                            4.5,
                        )

    def test_every_html_report_prints_the_light_status_palette(self) -> None:
        for name, source in self.templates.items():
            printed = css_rule(source, "@media print")
            declarations = custom_properties(
                css_rule(printed, PRINT_THEME_SELECTORS[name])
            )
            with self.subTest(template=name):
                self.assertEqual(
                    selected_properties(declarations, STATUS_TOKENS),
                    EXPECTED_LIGHT_STATUS,
                )

    def test_every_status_foreground_stays_legible_on_report_surfaces(self) -> None:
        """Status hues are painted as text, so they answer to the surfaces below.

        The soft-pair contract only proves a badge is readable against its own
        tint. Severity headings, risk cells, and metric numbers put the same
        hue straight onto the card and the page.
        """
        for name, source in self.templates.items():
            printed = css_rule(source, "@media print")
            themes = {
                "light": theme_declarations(source, name, "light"),
                "dark": theme_declarations(source, name, "dark"),
                "print": custom_properties(
                    css_rule(printed, PRINT_THEME_SELECTORS[name])
                ),
            }
            for theme, declarations in themes.items():
                foregrounds = [*STATUS_FOREGROUNDS]
                if "high" in declarations:
                    foregrounds.append("high")
                for token in foregrounds:
                    for surface in ("card", "background"):
                        with self.subTest(
                            template=name,
                            theme=theme,
                            token=token,
                            surface=surface,
                        ):
                            self.assertGreaterEqual(
                                contrast_ratio(
                                    declarations[token],
                                    declarations[surface],
                                ),
                                4.5,
                            )

    def test_report_specific_colors_alias_the_shared_status_palette(self) -> None:
        for name, aliases in REPORT_STATUS_ALIASES.items():
            source = self.templates[name]
            root_declarations = custom_properties(css_rule(source, ":root"))
            for theme in ("light", "dark"):
                declarations = {
                    **root_declarations,
                    **theme_declarations(source, name, theme),
                }
                for alias, target in aliases.items():
                    with self.subTest(template=name, theme=theme, alias=alias):
                        self.assertEqual(
                            declarations[alias],
                            f"var(--{target})",
                        )
                        self.assertEqual(
                            resolve_token(declarations[alias], declarations),
                            declarations[target],
                        )

    def test_code_review_high_severity_stays_a_distinct_accessible_family(
        self,
    ) -> None:
        source = self.templates["code-review"]
        for theme in ("light", "dark"):
            declarations = theme_declarations(source, "code-review", theme)
            expected = EXPECTED_HIGH_SEVERITY[theme]
            with self.subTest(theme=theme, contract="exact"):
                self.assertEqual(
                    selected_properties(declarations, ("high", "high-soft")),
                    expected,
                )
            with self.subTest(theme=theme, contract="distinct"):
                self.assertNotEqual(
                    declarations["high"],
                    declarations["status-warning"],
                )
                self.assertNotEqual(
                    declarations["high"],
                    declarations["status-danger"],
                )
            with self.subTest(theme=theme, contract="contrast"):
                self.assertGreaterEqual(
                    contrast_ratio(
                        declarations["high"],
                        declarations["high-soft"],
                    ),
                    4.5,
                )

    def test_code_review_severity_badges_use_accessible_soft_status_pairs(
        self,
    ) -> None:
        source = self.templates["code-review"]
        self.assertNotRegex(
            css_rule(source, ".badge"),
            r"color:\s*#fff(?:fff)?\s*;",
        )
        for severity, (foreground, background) in SEVERITY_BADGE_PAIRS.items():
            rule = css_rule(source, f".badge-{severity}")
            with self.subTest(severity=severity, contract="tokens"):
                self.assertRegex(rule, rf"color:\s*var\(--{foreground}\)\s*;")
                self.assertRegex(rule, rf"background:\s*var\(--{background}\)\s*;")
            for theme in ("light", "dark"):
                declarations = theme_declarations(source, "code-review", theme)
                with self.subTest(severity=severity, theme=theme, contract="contrast"):
                    self.assertGreaterEqual(
                        contrast_ratio(
                            resolve_token(declarations[foreground], declarations),
                            resolve_token(declarations[background], declarations),
                        ),
                        4.5,
                    )

    def test_every_html_report_shares_one_diff_text_family(self) -> None:
        """Added, removed, and hunk text is one family across the three reports.

        The overlays behind that text already mix shared hue tokens, so a
        template that hard-codes its own green, red, and blue drifts away from
        the palette the moment the palette moves.
        """
        for name, source in self.templates.items():
            with self.subTest(template=name, theme="light"):
                self.assertEqual(
                    selected_properties(
                        theme_declarations(source, name, "light"),
                        CODE_DIFF_TEXT_TOKENS,
                    ),
                    EXPECTED_LIGHT_CODE_DIFF_TEXT,
                )
            # diff-summary has no scheme picker, so its dark family rides the
            # page theme; the other two hang it off the selected code tone.
            selector = DARK_CODE_TONE_SELECTORS[name]
            dark = (
                theme_declarations(source, name, "dark")
                if selector is None
                else custom_properties(css_rule(source, selector))
            )
            with self.subTest(template=name, theme="dark"):
                self.assertEqual(
                    selected_properties(dark, CODE_DIFF_TEXT_TOKENS),
                    EXPECTED_DARK_CODE_DIFF_TEXT,
                )

    def test_every_diff_overlay_derives_from_a_shared_hue_token(self) -> None:
        """Diff add/delete/hunk overlays must mix a token, never a raw literal.

        A literal inside color-mix() would silently introduce a second green,
        red, or blue family that no theme or print override can reach.
        """
        for name, source in self.templates.items():
            expressions = color_mix_expressions(source)
            with self.subTest(template=name, contract="present"):
                self.assertTrue(expressions)
            for expression in expressions:
                with self.subTest(template=name, expression=expression):
                    self.assertNotRegex(expression, r"#[0-9A-Fa-f]{3,8}\b")

    def test_every_html_report_binds_diff_overlays_to_hue_tokens(self) -> None:
        for name, source in self.templates.items():
            expressions = color_mix_expressions(source)
            for token in ("add-hue", "del-hue", "hunk-hue"):
                with self.subTest(template=name, token=token):
                    self.assertTrue(
                        any(f"var(--{token})" in expr for expr in expressions),
                        f"no color-mix() in {name} mixes var(--{token})",
                    )

    def test_every_theme_colour_is_declared_at_exactly_one_site(self) -> None:
        """Both sides of a token live in one light-dark() pair.

        Repeating the token set per mode is what lets explicit dark and auto
        dark disagree. A mode rule may only carry what light-dark() cannot
        express — a shadow list — and the scheme it selects.
        """
        for name, source in self.templates.items():
            base = custom_properties(css_rule(source, THEME_SELECTORS[name][0]))
            mode_rule = css_rule(source, THEME_SELECTORS[name][1])
            mode = custom_properties(mode_rule)
            for token in (*THEME_COLOR_TOKENS, *STATUS_TOKENS):
                with self.subTest(template=name, token=token, contract="paired"):
                    self.assertTrue(
                        base[token].startswith("light-dark("),
                        f"{token} is not a light-dark() pair: {base[token]}",
                    )
                with self.subTest(template=name, token=token, contract="single-site"):
                    self.assertNotIn(token, mode)
            with self.subTest(template=name, contract="mode-carries-scheme"):
                self.assertRegex(mode_rule, r"color-scheme:\s*dark\s*;")
                self.assertLessEqual(set(mode), {"shadow"})

    def test_diff_summary_auto_theme_declares_no_colour_of_its_own(self) -> None:
        """Auto resolves through color-scheme, not through a duplicated palette."""
        auto_rule = css_rule(
            self.template,
            'body[data-default-theme="auto"]:not([data-theme])',
        )
        self.assertRegex(auto_rule, r"color-scheme:\s*light dark\s*;")
        self.assertEqual(custom_properties(auto_rule), {})
        preference_rule = css_rule(
            css_rule(self.template, "@media (prefers-color-scheme: dark)"),
            'body[data-default-theme="auto"]:not([data-theme])',
        )
        self.assertLessEqual(set(custom_properties(preference_rule)), {"shadow"})

    def test_every_html_report_declares_and_uses_shared_semantic_tokens(
        self,
    ) -> None:
        single_declaration_tokens = {
            "radius",
            "radius-control",
            "font-sans",
            "font-mono",
        }
        referenced_tokens = (
            "background",
            "foreground",
            "card",
            "muted",
            "muted-foreground",
            "primary",
            "destructive",
            "border",
            "ring",
            "radius",
        )
        for name, source in self.templates.items():
            for token in TOKENS:
                with self.subTest(
                    template=name,
                    token=token,
                    contract="declaration",
                ):
                    declaration_count = len(
                        re.findall(rf"--{re.escape(token)}\s*:", source)
                    )
                    self.assertGreaterEqual(declaration_count, 1)
                    if token not in single_declaration_tokens:
                        self.assertGreaterEqual(declaration_count, 2)

            for token in referenced_tokens:
                with self.subTest(
                    template=name,
                    token=token,
                    contract="reference",
                ):
                    self.assertRegex(
                        source,
                        rf"var\(\s*--{re.escape(token)}\s*\)",
                    )

    def test_every_html_report_omits_legacy_palette_declarations(self) -> None:
        for name, tokens in LEGACY_TOKENS.items():
            source = self.templates[name]
            for token in tokens:
                with self.subTest(template=name, token=token):
                    self.assertNotRegex(source, rf"--{re.escape(token)}\s*:")

    def test_diff_summary_omits_legacy_palette_declarations(self) -> None:
        legacy_tokens = (
            "paper",
            "paper-raised",
            "paper-muted",
            "ink",
            "ink-muted",
            "line",
            "line-strong",
            "cobalt",
            "cobalt-soft",
            "amber",
            "amber-soft",
        )
        for token in legacy_tokens:
            with self.subTest(token=token):
                self.assertNotRegex(self.template, rf"--{re.escape(token)}\s*:")

    def test_every_html_report_preserves_control_responsive_and_print_states(
        self,
    ) -> None:
        for name, source in self.templates.items():
            focus_rules = re.findall(
                r"[^{}]*:focus-visible[^{}]*\{(?P<body>.*?)\}",
                source,
                re.DOTALL,
            )
            disabled_rules = re.findall(
                r"[^{}]*:disabled[^{}]*\{(?P<body>.*?)\}",
                source,
                re.DOTALL,
            )

            with self.subTest(template=name, state="focus-visible"):
                self.assertTrue(
                    any(
                        re.search(
                            r"outline:\s*2px\s+solid\s+var\(\s*--ring\s*\)",
                            rule,
                        )
                        for rule in focus_rules
                    )
                )
            with self.subTest(template=name, state="disabled"):
                self.assertTrue(
                    any(
                        re.search(r"opacity:\s*0\.5\s*;", rule)
                        and re.search(r"pointer-events:\s*none\s*;", rule)
                        for rule in disabled_rules
                    )
                )
            with self.subTest(template=name, state="narrow"):
                self.assertRegex(source, r"@media\s*\([^)]*max-width")
            with self.subTest(template=name, state="print"):
                self.assertIn("@media print", source)

    def test_viewer_and_review_share_control_component_states(self) -> None:
        for name in ("diff-viewer", "code-review"):
            source = self.templates[name]
            control_rule = re.search(
                r"button\s*,\s*select\s*\{(?P<body>.*?)\}",
                source,
                re.DOTALL,
            )
            hover_rule = re.search(
                r"button:where\(\s*:hover:not\(:disabled\)\s*\)\s*,\s*"
                r"select:where\(\s*:hover:not\(:disabled\)\s*\)\s*"
                r"\{(?P<body>.*?)\}",
                source,
                re.DOTALL,
            )

            with self.subTest(template=name, component="control"):
                self.assertIsNotNone(control_rule)
                declarations = control_rule.group("body")
                self.assertRegex(declarations, r"min-height:\s*2rem\s*;")
                self.assertRegex(
                    declarations,
                    r"border:\s*1px\s+solid\s+var\(--input\)\s*;",
                )
                self.assertRegex(
                    declarations,
                    r"border-radius:\s*var\(--radius-control\)\s*;",
                )
                self.assertRegex(
                    declarations,
                    r"background:\s*var\(--background\)\s*;",
                )
                self.assertRegex(
                    declarations,
                    r"color:\s*var\(--foreground\)\s*;",
                )
            with self.subTest(template=name, component="control-hover"):
                self.assertIsNotNone(hover_rule)
                self.assertNotRegex(
                    source,
                    r"button:hover:not\(:disabled\)\s*,\s*"
                    r"select:hover:not\(:disabled\)\s*\{",
                )
                declarations = hover_rule.group("body")
                self.assertRegex(
                    declarations,
                    r"background:\s*var\(--accent\)\s*;",
                )
                self.assertRegex(
                    declarations,
                    r"color:\s*var\(--accent-foreground\)\s*;",
                )

    def test_viewer_and_review_preserve_complete_control_state_pairs(self) -> None:
        for name, destructive_selectors in DESTRUCTIVE_CONTROL_SELECTORS.items():
            source = self.templates[name]

            for destructive_selector in destructive_selectors:
                destructive_rule = css_rule(source, destructive_selector)

                for property_name, token in (
                    ("background", "destructive"),
                    ("color", "destructive-foreground"),
                    ("border-color", "destructive"),
                ):
                    with self.subTest(
                        template=name,
                        state="destructive",
                        selector=destructive_selector,
                        property=property_name,
                    ):
                        self.assertRegex(
                            destructive_rule,
                            rf"{property_name}:\s*var\(--{token}\)"
                            r"(?:\s*!important)?\s*;",
                        )

                for theme in ("light", "dark"):
                    declarations = theme_declarations(source, name, theme)
                    with self.subTest(
                        template=name,
                        state="destructive-contrast",
                        selector=destructive_selector,
                        theme=theme,
                    ):
                        self.assertGreaterEqual(
                            contrast_ratio(
                                declarations["destructive"],
                                declarations["destructive-foreground"],
                            ),
                            4.5,
                        )

            for selector in PRIMARY_CONTROL_SELECTORS[name]:
                state_rule = css_rule(source, selector)
                with self.subTest(
                    template=name,
                    state="primary",
                    selector=selector,
                ):
                    self.assertRegex(
                        state_rule,
                        r"background:\s*var\(--primary\)\s*;",
                    )
                    self.assertRegex(
                        state_rule,
                        r"color:\s*var\(--primary-foreground\)\s*;",
                    )

            copied_rule = css_rule(source, ".copy-md-btn.copied")
            with self.subTest(template=name, state="copied"):
                self.assertRegex(copied_rule, r"background:\s*[^;]+;")
                self.assertNotRegex(
                    copied_rule,
                    r"var\(--accent(?:-foreground)?\)",
                )

    def test_code_review_control_group_declares_effective_neutral_hover_states(
        self,
    ) -> None:
        source = self.templates["code-review"]
        hover_rule = re.search(
            r'\.control button:not\(\[aria-pressed="true"\]\)'
            r":where\(\s*:hover:not\(:disabled\)\s*\)\s*,\s*"
            r"\.control select:where\(\s*:hover:not\(:disabled\)\s*\)\s*"
            r"\{(?P<body>.*?)\}",
            source,
            re.DOTALL,
        )

        self.assertIsNotNone(hover_rule)
        declarations = hover_rule.group("body")
        self.assertRegex(declarations, r"background:\s*var\(--accent\)\s*;")
        self.assertRegex(
            declarations,
            r"color:\s*var\(--accent-foreground\)\s*;",
        )

        base_position = source.index(".control button, .control select {")
        pressed_position = source.index('.control button[aria-pressed="true"] {')
        self.assertLess(base_position, hover_rule.start())
        self.assertLess(hover_rule.start(), pressed_position)

        pressed_rule = css_rule(
            source,
            '.control button[aria-pressed="true"]',
        )
        self.assertRegex(pressed_rule, r"background:\s*var\(--primary\)\s*;")
        self.assertRegex(
            pressed_rule,
            r"color:\s*var\(--primary-foreground\)\s*;",
        )

    def test_diff_viewer_has_print_layout_contract(self) -> None:
        print_rule = css_rule(self.templates["diff-viewer"], "@media print")
        for selector in (
            "aside",
            ".sidebar-expand",
            ".topbar .controls",
            ".comment-row",
            ".comment-input-row",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, print_rule)
        self.assertNotIn(".line-comment-marker", print_rule)
        self.assertIn(
            'tr.className = "comment-row";',
            self.templates["diff-viewer"],
        )
        self.assertIn(
            'tr.className = "comment-input-row";',
            self.templates["diff-viewer"],
        )
        self.assertRegex(print_rule, r"\.layout\s*\{[^}]*display:\s*block\s*;")
        self.assertRegex(print_rule, r"main\s*\{[^}]*padding:\s*0\s*;")
        self.assertRegex(
            print_rule,
            r"\.file-diff\s*\{[^}]*break-inside:\s*avoid\s*;"
            r"[^}]*border-color:\s*#d4d4d8\s*;"
            r"[^}]*box-shadow:\s*none\s*;",
        )

    def test_code_review_finding_accent_cards_remain_flat(self) -> None:
        finding_rule = css_rule(
            self.templates["code-review"],
            "details.finding",
        )
        self.assertNotIn("border-radius", finding_rule)

    def test_code_review_narrow_report_tables_scroll_without_expanding_page(
        self,
    ) -> None:
        source = self.templates["code-review"]
        narrow_rule = css_rule(source, "@media (max-width: 860px)")
        table_scroll_rule = css_rule(source, ".table-scroll")
        table_scroll_declarations = {
            name: value.strip()
            for name, value in re.findall(
                r"([\w-]+)\s*:\s*([^;{}]+);",
                table_scroll_rule,
            )
        }

        self.assertEqual(
            table_scroll_declarations,
            {
                "margin-bottom": "20px",
                "max-width": "100%",
                "overflow-x": "auto",
            },
        )
        self.assertLess(
            source.index(".table-scroll {"),
            source.index("@media (max-width: 860px)"),
        )
        self.assertNotIn(".table-scroll", narrow_rule)
        report_table_rule = css_rule(source, "table:not(.diff-table)")
        self.assertNotRegex(
            report_table_rule,
            r"(?:display:\s*block|margin-bottom:\s*20px|overflow-x:\s*auto)\s*;",
        )
        self.assertNotIn("table:not(.diff-table)", narrow_rule)
        self.assertRegex(
            css_rule(source, ".diff-body"),
            r"overflow-x:\s*auto\s*;",
        )
        self.assertNotRegex(
            css_rule(narrow_rule, ".diff-table"),
            r"display:\s*block\s*;",
        )
        self.assertRegex(
            css_rule(css_rule(source, "@media print"), ".table-scroll"),
            r"overflow-x:\s*visible\s*;",
        )

    def test_code_review_muted_microcopy_binds_accessible_token_pairs(
        self,
    ) -> None:
        source = self.templates["code-review"]
        selector_pairs = (
            ("table:not(.diff-table) th", "table:not(.diff-table) th"),
            (".finding-tool-btn", ".finding-tool-btn"),
            (".comment-meta", ".comment"),
        )

        for text_selector, surface_selector in selector_pairs:
            text_rule = css_rule(source, text_selector)
            surface_rule = css_rule(source, surface_selector)
            color_match = re.search(
                r"color:\s*var\(--([\w-]+)\)\s*;",
                text_rule,
            )
            background_match = re.search(
                r"background:\s*var\(--([\w-]+)\)\s*;",
                surface_rule,
            )

            with self.subTest(selector=text_selector, contract="tokens"):
                self.assertIsNotNone(color_match)
                self.assertIsNotNone(background_match)
                self.assertEqual(color_match.group(1), "foreground")
                self.assertEqual(background_match.group(1), "muted")

            for theme in ("light", "dark"):
                declarations = theme_declarations(source, "code-review", theme)
                with self.subTest(selector=text_selector, theme=theme):
                    self.assertGreaterEqual(
                        contrast_ratio(
                            declarations[color_match.group(1)],
                            declarations[background_match.group(1)],
                        ),
                        4.5,
                    )

    def test_code_review_finding_tool_copied_state_uses_monochrome_pair(
        self,
    ) -> None:
        source = self.templates["code-review"]
        copied_declarations = {
            name: value.strip()
            for name, value in re.findall(
                r"([\w-]+)\s*:\s*([^;{}]+);",
                css_rule(source, ".finding-tool-btn.copied"),
            )
        }
        surface_declarations = {
            name: value.strip()
            for name, value in re.findall(
                r"([\w-]+)\s*:\s*([^;{}]+);",
                css_rule(source, ".finding-tool-btn"),
            )
        }

        for property_name in ("color", "border-color"):
            with self.subTest(property=property_name):
                self.assertEqual(
                    copied_declarations[property_name],
                    "var(--foreground)",
                )
        self.assertEqual(
            surface_declarations["background"],
            "var(--muted)",
        )

        for theme in ("light", "dark"):
            declarations = theme_declarations(source, "code-review", theme)

            def resolve_color(value: str) -> str:
                token_match = re.fullmatch(r"var\(--([\w-]+)\)", value)
                return (
                    declarations[token_match.group(1)]
                    if token_match is not None
                    else value
                )

            with self.subTest(theme=theme):
                self.assertGreaterEqual(
                    contrast_ratio(
                        resolve_color(copied_declarations["color"]),
                        resolve_color(surface_declarations["background"]),
                    ),
                    4.5,
                )

    def test_diff_summary_uses_shared_compact_report_shell(self) -> None:
        self.assertEqual(self.root_declarations["sidebar-width"], "220px")
        self.assertRegex(
            css_rule(self.template, ".layout"),
            r"grid-template-columns:\s*var\(--sidebar-width\)\s+"
            r"minmax\(0,\s*1fr\)\s*;",
        )
        self.assertRegex(
            css_rule(
                self.template,
                'html[data-sidebar-collapsed="true"] aside',
            ),
            r"display:\s*none\s*;",
        )

        for selector in (
            ".sidebar-header",
            ".sidebar-body",
            ".sidebar-footer",
            ".sidebar-expand",
            ".topbar",
            ".controls",
            ".control",
            ".main-column",
        ):
            with self.subTest(selector=selector):
                css_rule(self.template, selector)

        for legacy_selector in (
            ".atlas-shell",
            ".atlas-rail",
            ".atlas-canvas",
            ".rail-controls",
            ".rail-control",
            ".rail-actions",
            ".report-stage",
            "data-atlas-",
            "data-rail-",
            "atlasIndex",
        ):
            with self.subTest(legacy_selector=legacy_selector):
                self.assertNotIn(legacy_selector, self.template)
        self.assertNotRegex(self.template, r"\.atlas-[\w-]+")
        self.assertNotIn("@keyframes atlas-reveal", self.template)

    def test_diff_summary_collapsed_layout_removes_sidebar_column(self) -> None:
        self.assertRegex(
            css_rule(
                self.template,
                'html[data-sidebar-collapsed="true"] .layout',
            ),
            r"grid-template-columns:\s*minmax\(0,\s*1fr\)\s*;",
        )

    def test_diff_summary_main_column_matches_shared_report_width(self) -> None:
        self.assertRegex(
            css_rule(self.template, ".main-column"),
            r"padding:\s*24px\s+32px\s+64px\s*;",
        )
        self.assertRegex(
            css_rule(self.template, "#report-main"),
            r"max-width:\s*980px\s*;",
        )

    def test_report_body_and_controls_share_one_centered_measure(self) -> None:
        """Controls must sit above the text column, not float off at the viewport edge."""
        for name, selectors in (
            ("diff-summary", ("#report-main", ".topbar", ".report-footer")),
            ("code-review", (".lang-body", ".controls")),
        ):
            source = self.templates[name]
            for selector in selectors:
                rule = css_rule(source, selector)
                with self.subTest(template=name, selector=selector):
                    self.assertRegex(rule, r"max-width:\s*980px\s*;")
                    self.assertRegex(
                        rule,
                        r"margin(?:-inline)?:[^;]*auto[^;]*;",
                    )

    def test_diff_summary_small_sidebar_labels_use_accessible_foreground(self) -> None:
        sidebar_label_selectors = (
            ".brand",
            ".repo",
            ".sidebar-label",
            ".section-index-item--h3 a",
            ".comment-panel-title",
            ".sidebar-footer-label",
            ".comment-empty",
        )
        for selector in sidebar_label_selectors:
            with self.subTest(selector=selector):
                rule = css_rule_containing_selector(self.template, selector)
                self.assertRegex(rule, r"color:\s*var\(--foreground\)\s*;")

    def test_viewer_and_review_small_sidebar_text_is_accessible(self) -> None:
        for name, selectors in SMALL_SIDEBAR_TEXT_SELECTORS.items():
            source = self.templates[name]

            for selector in selectors:
                with self.subTest(template=name, selector=selector):
                    rule = css_rule_containing_selector(source, selector)
                    self.assertRegex(
                        rule,
                        r"color:\s*var\(--foreground\)\s*;",
                    )

            for theme in ("light", "dark"):
                declarations = theme_declarations(source, name, theme)
                with self.subTest(template=name, theme=theme):
                    self.assertGreaterEqual(
                        contrast_ratio(
                            declarations["foreground"],
                            declarations["muted"],
                        ),
                        4.5,
                    )

    def test_diff_summary_cards_use_code_review_finding_skin(self) -> None:
        card = css_rule(self.template, ".summary-card")
        self.assertRegex(card, r"background:\s*var\(--card\)\s*;")
        self.assertRegex(card, r"color:\s*var\(--card-foreground\)\s*;")
        self.assertRegex(card, r"border:\s*1px\s+solid\s+var\(--border\)\s*;")
        self.assertRegex(
            card,
            r"border-left:\s*4px\s+solid\s+var\(--primary\)\s*;",
        )
        self.assertRegex(card, r"box-shadow:\s*var\(--shadow\)\s*;")
        self.assertRegex(card, r"overflow:\s*hidden\s*;")
        self.assertNotIn("border-radius", card)

        summary = css_rule(self.template, ".card-summary")
        self.assertRegex(summary, r"padding:\s*12px\s+16px\s*;")
        self.assertRegex(summary, r"min-width:\s*0\s*;")
        self.assertRegex(summary, r"min-height:\s*0\s*;")
        marker = css_rule(self.template, ".card-summary::before")
        self.assertRegex(marker, r'content:\s*"\[\+\]"\s*;')
        self.assertRegex(marker, r"color:\s*var\(--muted-foreground\)\s*;")
        self.assertRegex(
            css_rule(self.template, ".summary-card[open] .card-summary::before"),
            r'content:\s*"\[-\]"\s*;',
        )

    def test_diff_summary_card_tools_use_shared_muted_control_skin(self) -> None:
        self.assertEqual(self.template.count(".card-action {"), 1)
        base = css_rule(self.template, ".card-action")
        self.assertRegex(base, r"background:\s*var\(--muted\)\s*;")
        self.assertRegex(base, r"color:\s*var\(--foreground\)\s*;")
        self.assertRegex(base, r"border:\s*1px\s+solid\s+var\(--border\)\s*;")
        self.assertRegex(
            base,
            r"border-radius:\s*var\(--radius-control\)\s*;",
        )
        self.assertRegex(base, r"padding:\s*4px\s+8px\s*;")
        self.assertRegex(base, r"font-size:\s*12px\s*;")
        self.assertRegex(base, r"font-weight:\s*500\s*;")
        self.assertRegex(base, r"letter-spacing:\s*0\s*;")
        self.assertRegex(base, r"text-transform:\s*none\s*;")

        hover = css_rule(self.template, ".card-action:hover")
        self.assertRegex(hover, r"border-color:\s*var\(--input\)\s*;")
        self.assertRegex(hover, r"background:\s*var\(--accent\)\s*;")
        self.assertRegex(hover, r"color:\s*var\(--accent-foreground\)\s*;")
        self.assertNotIn("transform", hover)
        self.assertNotRegex(self.template, r"\.card-action--accent\s*\{")

    def test_diff_summary_card_body_uses_compact_finding_padding(self) -> None:
        panel = css_rule(self.template, ".card-panel")
        self.assertRegex(panel, r"padding:\s*2px\s+16px\s+16px\s*;")
        self.assertRegex(panel, r"border-top:\s*0\s*;")
        self.assertRegex(panel, r"animation:\s*none\s*;")
        self.assertRegex(
            css_rule(self.template, ".card-content"),
            r"padding-top:\s*0\s*;",
        )

    def test_diff_summary_header_uses_compact_report_scale(self) -> None:
        body = css_rule(self.template, "body")
        self.assertRegex(body, r"font-size:\s*14px\s*;")
        self.assertRegex(body, r"line-height:\s*1\.5\s*;")

        report_main = css_rule(self.template, "#report-main")
        self.assertRegex(report_main, r"width:\s*100%\s*;")
        self.assertRegex(report_main, r"max-width:\s*980px\s*;")

        header = css_rule(self.template, ".report-header")
        self.assertRegex(header, r"margin:\s*0\s+0\s+24px\s*;")
        self.assertRegex(header, r"padding:\s*0\s*;")
        self.assertRegex(header, r"border:\s*0\s*;")
        self.assertRegex(header, r"background:\s*transparent\s*;")

        title = css_rule(self.template, "#report-title")
        self.assertRegex(title, r"margin:\s*0\s+0\s+16px\s*;")
        self.assertRegex(title, r"font-size:\s*27px\s*;")
        self.assertRegex(title, r"line-height:\s*1\.2\s*;")

        section_heading = css_rule(self.template, "#report-main > h2")
        self.assertRegex(section_heading, r"font-size:\s*21px\s*;")
        self.assertNotRegex(
            self.template,
            r"font-size:\s*clamp\([^;]*3(?:\.\d+)?rem",
        )

    def test_diff_summary_metadata_uses_compact_shared_chips(self) -> None:
        metadata = css_rule(self.template, ".report-metadata")
        self.assertRegex(metadata, r"display:\s*flex\s*;")
        self.assertRegex(metadata, r"flex-wrap:\s*wrap\s*;")
        self.assertRegex(metadata, r"gap:\s*8px\s*;")
        self.assertRegex(metadata, r"margin:\s*0\s*;")

        cell = css_rule(self.template, ".metadata-cell")
        self.assertRegex(cell, r"min-width:\s*0\s*;")
        self.assertRegex(cell, r"padding:\s*8px\s+10px\s*;")
        self.assertRegex(cell, r"border:\s*1px\s+solid\s+var\(--border\)\s*;")
        self.assertRegex(cell, r"border-radius:\s*var\(--radius\)\s*;")
        self.assertRegex(cell, r"background:\s*var\(--card\)\s*;")
        self.assertRegex(cell, r"box-shadow:\s*var\(--shadow\)\s*;")
        self.assertRegex(
            css_rule(self.template, ".metadata-cell dd"),
            r"overflow-wrap:\s*anywhere\s*;",
        )

    def test_diff_summary_comments_use_shared_surfaces_and_controls(self) -> None:
        thread = css_rule(self.template, ".comment-thread")
        self.assertRegex(thread, r"margin-top:\s*12px\s*;")
        self.assertRegex(thread, r"padding:\s*12px\s*;")
        self.assertRegex(thread, r"border:\s*1px\s+solid\s+var\(--border\)\s*;")
        self.assertRegex(thread, r"background:\s*var\(--muted\)\s*;")

        comment = css_rule(self.template, ".review-comment")
        self.assertRegex(comment, r"padding:\s*10px\s*;")
        self.assertRegex(comment, r"border:\s*1px\s+solid\s+var\(--border\)\s*;")
        self.assertRegex(
            comment,
            r"border-radius:\s*var\(--radius-control\)\s*;",
        )
        self.assertRegex(comment, r"background:\s*var\(--card\)\s*;")

        meta = css_rule(self.template, ".comment-meta")
        self.assertRegex(meta, r"color:\s*var\(--foreground\)\s*;")
        self.assertRegex(meta, r"font-size:\s*11px\s*;")

        editor = css_rule(self.template, ".comment-editor")
        self.assertRegex(editor, r"margin-top:\s*12px\s*;")
        self.assertRegex(editor, r"padding:\s*12px\s*;")
        self.assertRegex(editor, r"border:\s*1px\s+solid\s+var\(--border\)\s*;")
        self.assertRegex(editor, r"background:\s*var\(--muted\)\s*;")

        textarea = css_rule(self.template, ".comment-editor textarea")
        self.assertRegex(textarea, r"border:\s*1px\s+solid\s+var\(--input\)\s*;")
        self.assertRegex(
            textarea,
            r"border-radius:\s*var\(--radius-control\)\s*;",
        )
        self.assertRegex(textarea, r"background:\s*var\(--card\)\s*;")
        self.assertRegex(textarea, r"color:\s*var\(--foreground\)\s*;")

        action = css_rule(self.template, ".comment-editor-action")
        self.assertRegex(action, r"min-height:\s*2rem\s*;")
        self.assertRegex(action, r"border:\s*1px\s+solid\s+var\(--input\)\s*;")
        self.assertRegex(
            action,
            r"border-radius:\s*var\(--radius-control\)\s*;",
        )
        self.assertRegex(action, r"background:\s*var\(--card\)\s*;")
        self.assertRegex(action, r"color:\s*var\(--foreground\)\s*;")

        for selector in (
            ".comment-delete:hover",
            ".sidebar-action--danger:hover:not(:disabled)",
        ):
            hover = css_rule(self.template, selector)
            with self.subTest(selector=selector):
                self.assertRegex(
                    hover,
                    r"border-color:\s*var\(--destructive\)\s*;",
                )
                self.assertRegex(
                    hover,
                    r"background:\s*var\(--destructive\)\s*;",
                )
                self.assertRegex(
                    hover,
                    r"color:\s*var\(--destructive-foreground\)\s*;",
                )

    def test_diff_summary_quiz_uses_shared_card_and_input_skin(self) -> None:
        question = css_rule(self.template, ".quiz-question")
        self.assertRegex(question, r"background:\s*var\(--card\)\s*;")
        self.assertRegex(question, r"border:\s*1px\s+solid\s+var\(--border\)\s*;")
        self.assertRegex(question, r"border-radius:\s*var\(--radius\)\s*;")

        option = css_rule(self.template, ".quiz-option")
        self.assertRegex(option, r"min-width:\s*0\s*;")
        self.assertRegex(option, r"width:\s*100%\s*;")
        self.assertRegex(option, r"border:\s*1px\s+solid\s+var\(--input\)\s*;")
        self.assertRegex(
            option,
            r"border-radius:\s*var\(--radius-control\)\s*;",
        )
        self.assertRegex(option, r"background:\s*var\(--background\)\s*;")
        self.assertRegex(option, r"color:\s*var\(--foreground\)\s*;")

        hover = css_rule(self.template, ".quiz-option:hover:not(:disabled)")
        self.assertRegex(hover, r"border-color:\s*var\(--input\)\s*;")
        self.assertRegex(hover, r"background:\s*var\(--accent\)\s*;")
        self.assertRegex(hover, r"color:\s*var\(--accent-foreground\)\s*;")

    def test_diff_summary_quiz_long_text_wraps_inside_cards(self) -> None:
        for selector in (
            ".quiz-question-heading",
            ".quiz-question-title",
            ".quiz-option-text",
            ".quiz-explanation",
        ):
            with self.subTest(selector=selector):
                rule = css_rule(self.template, selector)
                self.assertRegex(rule, r"min-width:\s*0\s*;")
                self.assertRegex(rule, r"overflow-wrap:\s*anywhere\s*;")
        self.assertRegex(
            css_rule(self.template, ".quiz-option"),
            r"min-width:\s*0\s*;",
        )

    def test_diff_summary_responsive_uses_one_shared_narrow_layout_contract(
        self,
    ) -> None:
        self.assertEqual(self.template.count("@media (max-width: 860px)"), 1)
        for legacy_breakpoint in (
            "@media (max-width: 68rem)",
            "@media (max-width: 46rem)",
            "@media (max-width: 30rem)",
        ):
            with self.subTest(legacy_breakpoint=legacy_breakpoint):
                self.assertNotIn(legacy_breakpoint, self.template)

        narrow = css_rule(self.template, "@media (max-width: 860px)")
        self.assertRegex(css_rule(narrow, ".layout"), r"display:\s*block\s*;")

        aside = css_rule(narrow, "aside")
        self.assertRegex(aside, r"position:\s*static\s*;")
        self.assertRegex(aside, r"height:\s*auto\s*;")
        self.assertRegex(aside, r"max-height:\s*40vh\s*;")
        self.assertRegex(aside, r"border-right:\s*0\s*;")
        self.assertRegex(
            aside,
            r"border-bottom:\s*1px\s+solid\s+var\(--border\)\s*;",
        )

        self.assertRegex(
            css_rule(narrow, ".sidebar-resizer"),
            r"display:\s*none\s*;",
        )
        self.assertRegex(
            css_rule(narrow, ".main-column"),
            r"padding:\s*20px\s+16px\s+48px\s*;",
        )
        self.assertRegex(css_rule(narrow, ".topbar"), r"display:\s*block\s*;")

        controls = css_rule(narrow, ".controls")
        self.assertRegex(controls, r"justify-content:\s*flex-start\s*;")
        self.assertRegex(controls, r"margin-bottom:\s*16px\s*;")

        metadata = css_rule(narrow, ".report-metadata")
        self.assertRegex(metadata, r"display:\s*grid\s*;")
        self.assertRegex(
            metadata,
            r"grid-template-columns:\s*minmax\(0,\s*1fr\)\s*;",
        )
        self.assertRegex(
            css_rule(narrow, ".card-summary"),
            r"grid-template-columns:\s*auto\s+minmax\(0,\s*1fr\)\s*;",
        )
        badges = css_rule(narrow, ".card-badges")
        self.assertRegex(badges, r"grid-column:\s*2\s*;")
        self.assertRegex(badges, r"grid-row:\s*2\s*;")
        self.assertRegex(badges, r"justify-content:\s*flex-start\s*;")

    def test_diff_summary_non_quiz_long_content_wraps_within_report_and_nav(
        self,
    ) -> None:
        self.assertRegex(
            css_rule(self.template, "#report-main"),
            r"overflow-wrap:\s*anywhere\s*;",
        )

        navigation_link = css_rule(self.template, ".section-index-item a")
        self.assertRegex(
            navigation_link,
            r"grid-template-columns:\s*1\.2rem\s+minmax\(0,\s*1fr\)\s*;",
        )
        self.assertRegex(navigation_link, r"min-width:\s*0\s*;")
        self.assertRegex(navigation_link, r"overflow-wrap:\s*anywhere\s*;")

    def test_diff_summary_print_uses_shared_report_contract(self) -> None:
        printed = css_rule(self.template, "@media print")
        for selector in (
            "aside",
            ".sidebar-expand",
            ".topbar .controls",
            ".card-toolbar",
            ".comment-thread",
            ".comment-editor",
            ".status-region",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, printed)
        self.assertRegex(
            css_rule(printed, ".status-region"),
            r"display:\s*none\s*!important\s*;",
        )

        self.assertRegex(
            css_rule(printed, ".layout"),
            r"display:\s*block\s*;",
        )
        self.assertRegex(
            css_rule(printed, ".main-column"),
            r"padding:\s*0\s*;",
        )

        card = css_rule(printed, ".summary-card")
        self.assertRegex(card, r"break-inside:\s*avoid\s*;")
        self.assertRegex(card, r"box-shadow:\s*none\s*;")
        self.assertRegex(
            css_rule(printed, ".summary-card:not([open]) > :not(summary)"),
            r"display:\s*block\s*;",
        )
        self.assertRegex(
            printed,
            r"\.quiz-question\s*,\s*\.quiz-explanation\s*\{[^}]*"
            r"break-inside:\s*avoid\s*;[^}]*box-shadow:\s*none\s*;",
        )
        self.assertRegex(
            css_rule(printed, ".quiz-option[data-quiz-correct]::after"),
            r'content:\s*"\s*✓"\s*;',
        )
        self.assertRegex(
            css_rule(printed, ".quiz-status"),
            r"display:\s*none\s*!important\s*;",
        )

        self.assertNotRegex(
            printed,
            r"\.report-header\s*\{[^}]*padding:\s*8mm\s*;",
        )
        self.assertNotRegex(
            printed,
            r"#report-title\s*\{[^}]*font-size:\s*32pt\s*;",
        )

    def test_diff_summary_print_palette_overrides_dark_theme_specificity(
        self,
    ) -> None:
        printed = css_rule(self.template, "@media print")
        print_palette_selector = (
            "body,\n"
            '      body[data-default-theme="dark"]:not([data-theme]),\n'
            '      body[data-theme="dark"],\n'
            '      body[data-default-theme="auto"]:not([data-theme])'
        )
        palette = css_rule(printed, print_palette_selector)
        declarations = custom_properties(palette)

        self.assertEqual(
            selected_properties(declarations, THEME_COLOR_TOKENS),
            EXPECTED_PRINT_THEME,
        )
        self.assertEqual(declarations["shadow"], "none")
        self.assertRegex(palette, r"color-scheme:\s*light\s*;")

    def test_diff_summary_high_impact_uses_distinct_accessible_status_token(
        self,
    ) -> None:
        for theme, declarations in (
            ("light", self.light_declarations),
            ("dark", self.dark_declarations),
        ):
            with self.subTest(theme=theme):
                self.assertIn("impact-high", declarations)
                impact_high = resolve_token(
                    declarations["impact-high"],
                    declarations,
                )
                self.assertNotEqual(impact_high, declarations["ring"])
                self.assertNotEqual(impact_high, declarations["primary"])
                self.assertGreaterEqual(
                    contrast_ratio(impact_high, declarations["card"]),
                    4.5,
                )

        high_card_rule = css_rule(self.template, ".summary-card.impact-high")
        self.assertRegex(
            high_card_rule,
            r"border-left-color:\s*var\(--impact-high\)\s*;",
        )
        high_badge_rule = css_rule(
            self.template,
            ".summary-card.impact-high .badge--impact",
        )
        # Same soft-tint recipe as the code-review severity badges, so the hue
        # carries the meaning instead of a solid slab of it.
        self.assertRegex(high_badge_rule, r"color:\s*var\(--impact-high\)\s*;")
        self.assertRegex(
            high_badge_rule,
            r"background:\s*var\(--impact-high-soft\)\s*;",
        )
        self.assertEqual(self.template.count("var(--ring)"), 1)


if __name__ == "__main__":
    unittest.main()
