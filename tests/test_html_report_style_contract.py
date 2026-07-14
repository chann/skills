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


class HtmlReportStyleContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.template = SUMMARY_TEMPLATE.read_text(encoding="utf-8")

    def test_diff_summary_declares_and_uses_shared_semantic_tokens(self) -> None:
        single_declaration_tokens = {"radius", "font-sans", "font-mono"}
        for token in TOKENS:
            with self.subTest(token=token, contract="declaration"):
                declaration_count = len(
                    re.findall(rf"--{re.escape(token)}\s*:", self.template)
                )
                self.assertGreaterEqual(declaration_count, 1)
                if token not in single_declaration_tokens:
                    self.assertGreaterEqual(declaration_count, 2)

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
        for token in referenced_tokens:
            with self.subTest(token=token, contract="reference"):
                self.assertRegex(self.template, rf"var\(\s*--{re.escape(token)}\s*\)")

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

    def test_diff_summary_has_shared_focus_and_disabled_states(self) -> None:
        focus_rule = re.search(
            r":focus-visible\s*\{(?P<body>.*?)\}",
            self.template,
            re.DOTALL,
        )
        self.assertIsNotNone(focus_rule)
        self.assertRegex(
            focus_rule.group("body"),
            r"outline:\s*2px\s+solid\s+var\(\s*--ring\s*\)",
        )

        disabled_rule = re.search(
            r":disabled\s*,\s*\[aria-disabled=[\"']true[\"']\]\s*"
            r"\{(?P<body>.*?)\}",
            self.template,
            re.DOTALL,
        )
        self.assertIsNotNone(disabled_rule)
        self.assertRegex(disabled_rule.group("body"), r"opacity:\s*0\.5\s*;")
        self.assertRegex(
            disabled_rule.group("body"), r"pointer-events:\s*none\s*;"
        )


if __name__ == "__main__":
    unittest.main()
