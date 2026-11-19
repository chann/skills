import json
import os
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "work-summary"
SKILL = PACKAGE / "skills" / "work-summary"


class WorkSummarySkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = [
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "work-summary.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
            SKILL / "references" / "agent-history-stores.md",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
        ]

        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_plugin_metadata_and_interfaces_publish_work_summary(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        command = (PACKAGE / "commands" / "work-summary.md").read_text(
            encoding="utf-8"
        )
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertEqual("work-summary", metadata["name"])
        self.assertEqual("0.1.0", metadata["version"])
        self.assertIn("date", metadata["description"].lower())
        self.assertIn('argument-hint: "[range]"', command)
        self.assertIn("Use the **work-summary** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn("$work-summary", openai)

    def test_skill_publishes_both_selectors_and_reference(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---\n", 2)[1]

        self.assertIn("name: work-summary", frontmatter)
        self.assertIn("/work-summary", frontmatter)
        self.assertIn("$work-summary", frontmatter)
        self.assertIn("references/agent-history-stores.md", text)

    def test_skill_defines_the_date_range_grammar(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        for contract in (
            "default to `today`",
            "`yesterday`",
            "`this week` / `last week`",
            "`this month` / `last month`",
            "`this quarter` / `last quarter`",
            "`this year` / `last year`",
            "`YYYY-MM-DD..YYYY-MM-DD`",
            "user's local timezone",
            "Monday-start",
            "detailed",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_skill_classifies_default_save_paths_by_requested_period(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        for path_contract in (
            ".work-summaries/daily/<YYYY>/<YYYY-MM-DD>[-detailed].md",
            ".work-summaries/weekly/<ISO-week-year>/<YYYY-Www>[-detailed].md",
            ".work-summaries/monthly/<YYYY>/<YYYY-MM>[-detailed].md",
            ".work-summaries/quarterly/<YYYY>/<YYYY-Qn>[-detailed].md",
            ".work-summaries/yearly/<YYYY>[-detailed].md",
            ".work-summaries/custom/<start>--<end>[-detailed].md",
            "explicit output path",
        ):
            with self.subTest(path_contract=path_contract):
                self.assertIn(path_contract, text)

    def test_skill_mines_stores_read_only_and_locally(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        for contract in (
            "Claude Code",
            "Codex",
            "opencode",
            "agy",
            "`isMeta`",
            "`isSidechain`",
            "`is_internal`",
            "Silently skip stores that are absent",
            "read-only",
            "never send it to an external service",
            "Never stage or commit",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_skill_pins_the_markdown_report_contract(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        for contract in (
            "## Overview",
            "## By project",
            "## By agent",
            "no recorded activity",
            ".work-summaries/",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_reference_maps_every_first_tier_store(self) -> None:
        stores = (
            SKILL / "references" / "agent-history-stores.md"
        ).read_text(encoding="utf-8")

        for heading in (
            "Claude Code",
            "Codex CLI",
            "opencode",
            "agy (Antigravity CLI)",
            "Other stores worth probing",
            "Date bucketing rules",
        ):
            with self.subTest(heading=heading):
                self.assertIn(f"## {heading}", stores)

    def test_evals_cover_reporting_failure_modes(self) -> None:
        payload = json.loads(
            (SKILL / "evals" / "evals.json").read_text(encoding="utf-8")
        )

        self.assertEqual("work-summary", payload["skill_name"])
        self.assertEqual(
            [1, 2, 3, 4, 5, 6], [item["id"] for item in payload["evals"]]
        )
        prompts = " ".join(item["prompt"] for item in payload["evals"])
        assertions = " ".join(
            assertion
            for item in payload["evals"]
            for assertion in item["assertions"]
        )
        self.assertIn("today", prompts)
        self.assertIn("this week", prompts)
        self.assertIn("last quarter", prompts)
        self.assertIn("human-friendly-writing is unavailable", prompts)
        self.assertIn("no recorded activity", assertions)
        self.assertIn("local timezone", assertions)
        self.assertIn("read-only", assertions)
        self.assertIn("quarterly", assertions)
        self.assertIn("does not install", assertions)

    def test_readmes_document_installation_and_selectors(self) -> None:
        for path in (PACKAGE / "README.md", PACKAGE / "README.ko.md"):
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(
                    2, text.count("chann/skills --skill work-summary")
                )
                self.assertIn("/work-summary", text)
                self.assertIn("$work-summary", text)

    def test_skills_cli_discovers_work_summary(self) -> None:
        env = os.environ.copy()
        env.update({"NO_COLOR": "1", "FORCE_COLOR": "0"})
        result = subprocess.run(
            ["npx", "--yes", "skills", "add", ".", "-l", "--full-depth"],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertRegex(
            result.stdout, re.compile(r"(?m)^[^A-Za-z0-9]*work-summary\s*$")
        )


if __name__ == "__main__":
    unittest.main()
