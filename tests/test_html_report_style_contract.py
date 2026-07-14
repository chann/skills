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
    "code-review-html": (
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
    "code-review-html": (":root", 'html[data-page-theme="dark"]'),
}
LEGACY_TOKENS = {
    "diff-summary": (),
    "diff-viewer": ("bg", "surface", "surface-muted", "text"),
    "code-review-html": ("bg", "surface", "surface-muted", "text"),
}
PRIMARY_CONTROL_SELECTORS = {
    "diff-viewer": (
        'button[aria-pressed="true"]',
        ".copy-md-btn",
        ".btn-comment.btn-save",
    ),
    "code-review-html": (
        '.control button[aria-pressed="true"]',
        ".copy-md-btn",
        ".diff-toggle.active",
        ".btn-comment.btn-save",
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
    "code-review-html": (
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
    "font-sans",
    "font-mono",
)
THEME_COLOR_TOKENS = TOKENS[:-3]
ROOT_TOKENS = TOKENS[-3:]
EXPECTED_LIGHT_THEME = {
    "background": "#ffffff",
    "foreground": "#09090b",
    "card": "#ffffff",
    "card-foreground": "#09090b",
    "popover": "#ffffff",
    "popover-foreground": "#09090b",
    "muted": "#f4f4f5",
    "muted-foreground": "#71717a",
    "primary": "#18181b",
    "primary-foreground": "#fafafa",
    "secondary": "#f4f4f5",
    "secondary-foreground": "#18181b",
    "accent": "#f4f4f5",
    "accent-foreground": "#18181b",
    "destructive": "#dc2626",
    "destructive-foreground": "#fafafa",
    "border": "#e4e4e7",
    "input": "#e4e4e7",
    "ring": "#18181b",
}
EXPECTED_DARK_THEME = {
    "background": "#09090b",
    "foreground": "#fafafa",
    "card": "#09090b",
    "card-foreground": "#fafafa",
    "popover": "#18181b",
    "popover-foreground": "#fafafa",
    "muted": "#27272a",
    "muted-foreground": "#a1a1aa",
    "primary": "#fafafa",
    "primary-foreground": "#18181b",
    "secondary": "#27272a",
    "secondary-foreground": "#fafafa",
    "accent": "#27272a",
    "accent-foreground": "#fafafa",
    "destructive": "#7f1d1d",
    "destructive-foreground": "#fafafa",
    "border": "#27272a",
    "input": "#27272a",
    "ring": "#d4d4d8",
}
EXPECTED_ROOT_TOKENS = {
    "radius": "0.5rem",
    "font-sans": (
        'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", '
        "sans-serif"
    ),
    "font-mono": (
        'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", '
        '"Courier New", monospace'
    ),
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


def contrast_ratio(first: str, second: str) -> float:
    def luminance(hex_color: str) -> float:
        channels = [
            int(hex_color[index : index + 2], 16) / 255
            for index in range(1, 7, 2)
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
            name: path.read_text(encoding="utf-8")
            for name, path in TEMPLATES.items()
        }
        cls.root_declarations = custom_properties(css_rule(cls.template, ":root"))
        cls.light_declarations = custom_properties(css_rule(cls.template, "body"))
        cls.dark_declarations = custom_properties(
            css_rule(cls.template, 'body[data-theme="dark"]')
        )
        cls.auto_dark_declarations = custom_properties(
            css_rule(
                cls.template,
                'body[data-default-theme="auto"]:not([data-theme])',
            )
        )

    def test_every_html_report_uses_exact_shared_light_and_dark_values(
        self,
    ) -> None:
        for name, source in self.templates.items():
            light_selector, dark_selector = THEME_SELECTORS[name]
            root_declarations = custom_properties(css_rule(source, ":root"))
            light_declarations = custom_properties(
                css_rule(source, light_selector)
            )
            dark_declarations = custom_properties(css_rule(source, dark_selector))

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

    def test_diff_summary_uses_exact_identical_explicit_and_auto_dark_values(
        self,
    ) -> None:
        explicit_dark = selected_properties(
            self.dark_declarations,
            THEME_COLOR_TOKENS,
        )
        auto_dark = selected_properties(
            self.auto_dark_declarations,
            THEME_COLOR_TOKENS,
        )

        self.assertEqual(explicit_dark, EXPECTED_DARK_THEME)
        self.assertEqual(auto_dark, EXPECTED_DARK_THEME)
        self.assertEqual(auto_dark, explicit_dark)
        self.assertEqual(self.auto_dark_declarations, self.dark_declarations)

    def test_every_html_report_declares_and_uses_shared_semantic_tokens(
        self,
    ) -> None:
        single_declaration_tokens = {"radius", "font-sans", "font-mono"}
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
        for name in ("diff-viewer", "code-review-html"):
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
                    r"border-radius:\s*calc\(var\(--radius\)\s*-\s*2px\)\s*;",
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
        for name in ("diff-viewer", "code-review-html"):
            source = self.templates[name]
            destructive_rule = css_rule(
                source,
                ".clear-comments-btn:hover:not(:disabled)",
            )

            for property_name, token in (
                ("background", "destructive"),
                ("color", "destructive-foreground"),
                ("border-color", "destructive"),
            ):
                with self.subTest(
                    template=name,
                    state="destructive",
                    property=property_name,
                ):
                    self.assertRegex(
                        destructive_rule,
                        rf"{property_name}:\s*var\(--{token}\)"
                        r"(?:\s*!important)?\s*;",
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
            self.templates["code-review-html"],
            "details.finding",
        )
        self.assertNotIn("border-radius", finding_rule)

    def test_diff_summary_small_rail_labels_use_accessible_foreground(self) -> None:
        rail_label_selectors = (
            ".rail-registration",
            ".atlas-sidebar-label",
            ".section-index-item--h3 a",
            ".comment-panel-title",
            ".rail-actions-label",
            ".comment-empty",
        )
        for selector in rail_label_selectors:
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

            for theme, selector in (
                ("light", ":root"),
                ("dark", 'html[data-page-theme="dark"]'),
            ):
                declarations = custom_properties(css_rule(source, selector))
                with self.subTest(template=name, theme=theme):
                    self.assertGreaterEqual(
                        contrast_ratio(
                            declarations["foreground"],
                            declarations["muted"],
                        ),
                        4.5,
                    )

    def test_diff_summary_high_impact_uses_distinct_accessible_status_token(
        self,
    ) -> None:
        for theme, declarations in (
            ("light", self.light_declarations),
            ("dark", self.dark_declarations),
            ("auto-dark", self.auto_dark_declarations),
        ):
            with self.subTest(theme=theme):
                self.assertIn("impact-high", declarations)
                self.assertNotEqual(declarations["impact-high"], declarations["ring"])
                self.assertNotEqual(
                    declarations["impact-high"], declarations["primary"]
                )
                self.assertGreaterEqual(
                    contrast_ratio(
                        declarations["impact-high"],
                        declarations["card"],
                    ),
                    4.5,
                )

        self.assertEqual(
            self.auto_dark_declarations["impact-high"],
            self.dark_declarations["impact-high"],
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
        self.assertRegex(high_badge_rule, r"var\(--impact-high\)")
        self.assertEqual(self.template.count("var(--ring)"), 1)


if __name__ == "__main__":
    unittest.main()
