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
DESTRUCTIVE_CONTROL_SELECTORS = {
    "diff-viewer": (
        ".clear-comments-btn:hover:not(:disabled)",
    ),
    "code-review-html": (
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

                for theme, theme_selector in (
                    ("light", ":root"),
                    ("dark", 'html[data-page-theme="dark"]'),
                ):
                    declarations = custom_properties(
                        css_rule(source, theme_selector)
                    )
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
        source = self.templates["code-review-html"]
        hover_rule = re.search(
            r'\.control button:not\(\[aria-pressed="true"\]\)'
            r':where\(\s*:hover:not\(:disabled\)\s*\)\s*,\s*'
            r'\.control select:where\(\s*:hover:not\(:disabled\)\s*\)\s*'
            r'\{(?P<body>.*?)\}',
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
        pressed_position = source.index(
            '.control button[aria-pressed="true"] {'
        )
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
            self.templates["code-review-html"],
            "details.finding",
        )
        self.assertNotIn("border-radius", finding_rule)

    def test_code_review_narrow_report_tables_scroll_without_expanding_page(
        self,
    ) -> None:
        source = self.templates["code-review-html"]
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
        source = self.templates["code-review-html"]
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

            for theme, theme_selector in (
                ("light", ":root"),
                ("dark", 'html[data-page-theme="dark"]'),
            ):
                declarations = custom_properties(
                    css_rule(source, theme_selector)
                )
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
        source = self.templates["code-review-html"]
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

        for theme, theme_selector in (
            ("light", ":root"),
            ("dark", 'html[data-page-theme="dark"]'),
        ):
            declarations = custom_properties(css_rule(source, theme_selector))

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
        chevron = css_rule(self.template, ".card-summary::before")
        self.assertRegex(chevron, r'content:\s*"▶"\s*;')
        self.assertRegex(chevron, r"transition:\s*transform")
        self.assertRegex(
            css_rule(self.template, ".summary-card[open] .card-summary::before"),
            r"transform:\s*rotate\(90deg\)\s*;",
        )

    def test_diff_summary_card_tools_use_shared_muted_control_skin(self) -> None:
        self.assertEqual(self.template.count(".card-action {"), 1)
        base = css_rule(self.template, ".card-action")
        self.assertRegex(base, r"background:\s*var\(--muted\)\s*;")
        self.assertRegex(base, r"color:\s*var\(--foreground\)\s*;")
        self.assertRegex(base, r"border:\s*1px\s+solid\s+var\(--border\)\s*;")
        self.assertRegex(
            base,
            r"border-radius:\s*calc\(var\(--radius\)\s*-\s*2px\)\s*;",
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
        self.assertRegex(body, r"line-height:\s*1\.6\s*;")

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
            r"border-radius:\s*calc\(var\(--radius\)\s*-\s*2px\)\s*;",
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
            r"border-radius:\s*calc\(var\(--radius\)\s*-\s*2px\)\s*;",
        )
        self.assertRegex(textarea, r"background:\s*var\(--card\)\s*;")
        self.assertRegex(textarea, r"color:\s*var\(--foreground\)\s*;")

        action = css_rule(self.template, ".comment-editor-action")
        self.assertRegex(action, r"min-height:\s*2rem\s*;")
        self.assertRegex(action, r"border:\s*1px\s+solid\s+var\(--input\)\s*;")
        self.assertRegex(
            action,
            r"border-radius:\s*calc\(var\(--radius\)\s*-\s*2px\)\s*;",
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
            r"border-radius:\s*calc\(var\(--radius\)\s*-\s*2px\)\s*;",
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
            css_rule(printed, '.quiz-option[data-quiz-correct]::after'),
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
            EXPECTED_LIGHT_THEME,
        )
        self.assertEqual(declarations["impact-high"], "#92400e")
        self.assertEqual(declarations["positive"], "#216849")
        self.assertEqual(declarations["positive-soft"], "#d9eee3")
        self.assertEqual(declarations["shadow"], "none")
        self.assertRegex(palette, r"color-scheme:\s*light\s*;")

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
