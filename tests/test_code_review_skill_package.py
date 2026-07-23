import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODE_REVIEW = ROOT / "code-review"
MAIN_SKILL = CODE_REVIEW / "skills" / "code-review" / "SKILL.md"
WRAPPER_SKILLS = (CODE_REVIEW / "skills" / "code-review-md" / "SKILL.md",)
COMMANDS = (
    CODE_REVIEW / "commands" / "code-review.md",
    CODE_REVIEW / "commands" / "code-review-md.md",
    CODE_REVIEW / "commands" / "diff-summary.md",
)


class CodeReviewSkillPackageTests(unittest.TestCase):
    def test_env_example_is_not_classified_as_security_sensitive(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(
                    CODE_REVIEW
                    / "skills"
                    / "code-review"
                    / "scripts"
                    / "diff_stats.py"
                ),
            ],
            input=(
                "1\t0\t.env.example\n"
                "1\t0\t.env.local\n"
                "1\t0\tauth/.env.example\n"
            ),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        by_path = {entry["path"]: entry for entry in report["files"]}
        self.assertFalse(by_path[".env.example"]["security_sensitive"])
        self.assertTrue(by_path[".env.local"]["security_sensitive"])
        self.assertTrue(by_path["auth/.env.example"]["security_sensitive"])

    def test_main_skill_enforces_the_evidence_first_writing_contract(self) -> None:
        skill_text = MAIN_SKILL.read_text(encoding="utf-8")

        required_fragments = (
            "### Evidence-first writing contract",
            "observed behavior",
            "practical consequence",
            "smallest justified correction",
            "`Inference:`",
            "When there are no actionable findings",
            "### Conditional sections",
            "Decision Summary",
            "Open Questions",
            "only when",
            "**Observed behavior:**",
            "**Practical consequence:**",
            "**Smallest justified correction:**",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, skill_text)

        self.assertIn(
            "| **INFO** | Verified context that materially affects a review "
            "decision but requires no code change | No action needed |",
            skill_text,
        )
        self.assertIn("Never use INFO solely for uncertainty or praise.", skill_text)
        self.assertIn(
            "Missing evidence belongs under one specific **Open Questions** item "
            "only when it changes severity or action; otherwise omit it.",
            skill_text,
        )
        self.assertIn(
            "When there are no actionable findings, state that directly and include "
            "only material residual risks or verification gaps.",
            skill_text,
        )

        observed = skill_text.index("**Observed behavior:**")
        consequence = skill_text.index("**Practical consequence:**")
        correction = skill_text.index("**Smallest justified correction:**")
        self.assertLess(observed, consequence)
        self.assertLess(consequence, correction)

        for section, condition in (
            ("Decision Summary", "cross-cutting"),
            ("Positive Observations", "risk or review effort"),
            ("Open Questions", "severity or action"),
            ("File Summary", "multi-file"),
        ):
            with self.subTest(section=section):
                self.assertRegex(
                    skill_text,
                    rf"(?m)^- \*\*{re.escape(section)}:\*\* .*only when.*{condition}",
                )

        self.assertNotIn("## Executive Summary", skill_text)
        self.assertIn("fresh verification", skill_text)
        self.assertIn("browser-open result", skill_text)

    def test_main_skill_preserves_parser_significant_english_metadata_keys(
        self,
    ) -> None:
        skill_text = MAIN_SKILL.read_text(encoding="utf-8")

        self.assertIn(
            "Keep these parser-significant metadata keys exactly in English: "
            "`Date`, `Reviewer`, `Scope`, `Repository`, and `Language`.",
            skill_text,
        )
        self.assertIn(
            "Translate narrative headings, finding descriptions, conditional prose, "
            "and table headers or values when appropriate.",
            skill_text,
        )
        for key in ("Date", "Reviewer", "Scope", "Repository", "Language"):
            with self.subTest(key=key):
                self.assertIn(f"**{key}:**", skill_text)
        self.assertIn("**Language:** ko", skill_text)
        self.assertNotIn("Table headers and metadata labels", skill_text)

    def test_persisted_report_example_uses_vendor_neutral_reviewer(self) -> None:
        skill_text = MAIN_SKILL.read_text(encoding="utf-8")

        self.assertIn("**Reviewer:** automated review", skill_text)
        self.assertNotIn("**Reviewer:** Codex", skill_text)

    def test_main_skill_makes_html_default_and_markdown_only_explicit(self) -> None:
        skill_text = MAIN_SKILL.read_text(encoding="utf-8")
        persisted_heading = (
            "#### Persisted report modes (`/code-review` and `/code-review-md`)"
        )
        persisted_index = skill_text.index(persisted_heading)
        persisted_contract = skill_text[persisted_index:]

        self.assertIn(
            "Start the report with its title and parser-significant metadata, then "
            "present findings.",
            persisted_contract,
        )
        self.assertIn("Use a fact-only handoff after generation", persisted_contract)
        self.assertIn(
            "The `.reviews/` ignore suggestion is allowed in this handoff only when "
            "persisted artifacts were generated and `.reviews/` is not ignored.",
            persisted_contract,
        )
        self.assertIn("### 6. Finish by output mode", skill_text)
        self.assertIn(
            "### 5. Generate HTML (default; skip for `/code-review-md`)",
            skill_text,
        )
        self.assertIn(
            "**Markdown + HTML (`/code-review`):**",
            skill_text,
        )
        self.assertIn(
            "**Markdown only (`/code-review-md`):**",
            skill_text,
        )
        self.assertNotIn("Conversation-only mode", skill_text)
        self.assertNotIn(
            "- Start with the first actionable finding or the verified result.",
            skill_text,
        )
        self.assertNotIn("at most one urgent finding inline", skill_text)

    def test_code_review_prompts_remove_mandatory_padding_and_uncertain_info(
        self,
    ) -> None:
        prompt_paths = (MAIN_SKILL, *WRAPPER_SKILLS, *COMMANDS)
        forbidden_patterns = (
            r"\*\*Announce at start:\*\*",
            r"Always include the Positive Observations section",
            r"Skip the Positive Observations section",
            r"default to INFO severity when uncertain",
            r"top 1[-–]3",
            r"overall quality",
            r"\[2-3 sentence summary",
            r"Print a brief conversation summary",
            r"Present a brief summary in the conversation",
        )

        for path in prompt_paths:
            prompt = path.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                with self.subTest(path=path.relative_to(ROOT), pattern=pattern):
                    self.assertIsNone(re.search(pattern, prompt, re.IGNORECASE))

    def test_markdown_wrapper_defers_to_the_authoritative_writing_contract(
        self,
    ) -> None:
        authority = (
            "The main skill's **Evidence-first writing contract** and "
            "conditional-section rules are authoritative. Do not restate or weaken "
            "them here."
        )

        for path in WRAPPER_SKILLS:
            wrapper = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn(authority, wrapper)
                self.assertIn("finding counts by severity", wrapper)
                self.assertIn("overall risk", wrapper)
                self.assertIn("artifact path", wrapper)
                self.assertIn("fresh verification", wrapper)
                self.assertIn("Do not repeat report prose", wrapper)
                self.assertIn("persisted", wrapper.lower())
                self.assertIn(
                    "Include a `.reviews/` ignore suggestion in this handoff only when "
                    "artifacts were generated and `.reviews/` is not ignored.",
                    wrapper,
                )
                self.assertNotIn("urgent finding inline", wrapper)
                self.assertIn("no HTML report and no browser open", wrapper)
                self.assertIn("Skip step 5 (HTML).", wrapper)

    def test_all_review_commands_route_internally_without_user_visible_preambles(
        self,
    ) -> None:
        routing = {
            "code-review.md": "code-review",
            "code-review-md.md": "code-review-md",
            "diff-summary.md": "diff-summary",
        }
        expected_fragments = {
            "code-review.md": (
                "bilingual",
                "fact-only handoff",
                "finding counts by severity",
                "browser-open fact",
            ),
            "code-review-md.md": (
                "fact-only handoff",
                "finding counts by severity",
                "fresh verification",
            ),
            "diff-summary.md": (
                "packaged evidence collector",
                "artifact and verification facts only",
                "Do not repeat card or Executive Summary prose",
            ),
        }

        for path in COMMANDS:
            command = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn("evidence-first", command.lower())
                self.assertIn(
                    f"Apply the **{routing[path.name]}** skill internally. Do not "
                    "echo or announce this routing instruction.",
                    command,
                )
                self.assertNotIn("Before starting", command)
                self.assertNotIn("briefly tell", command.lower())
                self.assertNotIn("**Announce at start:**", command)
                self.assertNotIn("brief summary", command.lower())
                self.assertNotRegex(command, r"top 1[-–]3")
                self.assertNotIn("urgent finding inline", command)
                self.assertIn('argument-hint: "[scope]"', command)
                self.assertIn("$ARGUMENTS", command)
                for fragment in expected_fragments[path.name]:
                    self.assertIn(fragment, command)

    def test_default_command_owns_html_and_legacy_variant_is_removed(self) -> None:
        legacy_command = CODE_REVIEW / "commands" / "code-review-html.md"
        legacy_skill = CODE_REVIEW / "skills" / "code-review-html" / "SKILL.md"
        default_command = (CODE_REVIEW / "commands" / "code-review.md").read_text(
            encoding="utf-8"
        )

        self.assertFalse(legacy_command.exists())
        self.assertFalse(legacy_skill.exists())
        self.assertIn("**Output mode: Markdown + HTML.**", default_command)
        self.assertIn(
            "Runs `python <skill-path>/scripts/generate_html_report.py`",
            default_command,
        )
        self.assertIn("Opens the resulting `.html` file in a browser.", default_command)

    def test_skills_cli_discovers_default_review_and_diff_viewer(self) -> None:
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
            result.stdout,
            re.compile(r"(?m)^[^A-Za-z0-9]*code-review\s*$"),
        )
        self.assertRegex(
            result.stdout,
            re.compile(r"(?m)^[^A-Za-z0-9]*diff-viewer\s*$"),
        )
        self.assertNotRegex(
            result.stdout,
            re.compile(r"(?m)^[^A-Za-z0-9]*code-review-html\s*$"),
        )

    def test_diff_viewer_slash_command_and_skill_are_packaged(self) -> None:
        command = CODE_REVIEW / "commands" / "diff-viewer.md"
        skill = CODE_REVIEW / "skills" / "diff-viewer" / "SKILL.md"
        script = (
            CODE_REVIEW
            / "skills"
            / "diff-viewer"
            / "scripts"
            / "generate_diff_report.py"
        )
        template = (
            CODE_REVIEW / "skills" / "diff-viewer" / "assets" / "diff-template.html"
        )

        self.assertTrue(command.is_file(), "Claude slash command must be packaged")
        self.assertTrue(skill.is_file(), "Codex/skill discovery requires SKILL.md")
        self.assertTrue(
            script.is_file(), "diff-viewer runtime must be inside the skill folder"
        )
        self.assertTrue(
            template.is_file(), "HTML template must be inside the skill folder"
        )

        command_text = command.read_text(encoding="utf-8")
        skill_text = skill.read_text(encoding="utf-8")
        self.assertIn("Use the **diff-viewer** skill", command_text)
        self.assertIn("scripts/generate_diff_report.py", skill_text)

    def test_code_review_plugin_metadata_mentions_diff_viewer_and_diff_summary(
        self,
    ) -> None:
        metadata = json.loads(
            (CODE_REVIEW / ".claude-plugin" / "plugin.json").read_text()
        )

        self.assertEqual(metadata["version"], "2.4.0")
        self.assertIn("diff-viewer", metadata["description"])
        self.assertIn("diff-summary", metadata["description"])
