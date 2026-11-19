import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "interrogate"
SKILL_DIR = PACKAGE / "skills" / "interrogate"
MAIN_SKILL = SKILL_DIR / "SKILL.md"
PROOF_REFERENCE = SKILL_DIR / "references" / "proof-and-panel.md"
COMMAND = PACKAGE / "commands" / "interrogate.md"


def normalized(path: Path) -> str:
    """File text with whitespace collapsed so a line wrap cannot break a check."""
    return " ".join(path.read_text(encoding="utf-8").split())


class InterrogateSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = (
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "interrogate.md",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
            PACKAGE / ".snyk",
            MAIN_SKILL,
            SKILL_DIR / "agents" / "openai.yaml",
            SKILL_DIR / "evals" / "evals.json",
            SKILL_DIR / "scripts" / "diff_stats.py",
            SKILL_DIR / "scripts" / "generate_html_report.py",
            SKILL_DIR / "assets" / "report-template.html",
            SKILL_DIR / "references" / "review-criteria.md",
            SKILL_DIR / "references" / "common-vulnerabilities.md",
            SKILL_DIR / "references" / "python.md",
            SKILL_DIR / "references" / "javascript-typescript.md",
            PROOF_REFERENCE,
        )
        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_markdown_only_variant_and_old_plugin_review_are_gone(self) -> None:
        for path in (
            ROOT / "code-review" / "skills" / "code-review",
            ROOT / "code-review" / "skills" / "code-review-md",
            ROOT / "code-review" / "commands" / "code-review.md",
            ROOT / "code-review" / "commands" / "code-review-md.md",
            ROOT / "code-review" / ".claude-plugin" / "plugin.json",
            PACKAGE / "skills" / "interrogate-md",
        ):
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertFalse(path.exists())

    def test_plugin_metadata_is_a_major_bump(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

        self.assertEqual("interrogate", metadata["name"])
        self.assertEqual("3.0.0", metadata["version"])
        self.assertIn("blast-radius", metadata["description"])
        self.assertIn("proof", metadata["description"])

    def test_interfaces_publish_both_selectors_and_keep_triggers(self) -> None:
        frontmatter = MAIN_SKILL.read_text(encoding="utf-8").split("---\n", 2)[1]
        description = re.search(r"(?m)^description: (.*)$", frontmatter).group(1)
        openai = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn("name: interrogate", frontmatter)
        self.assertNotIn("disable-model-invocation", frontmatter)
        self.assertTrue(description.startswith("Use when"))
        self.assertLessEqual(len(description), 1024)
        for trigger in (
            "review my changes",
            "코드 리뷰",
            "check my code",
            "review the last commit",
            "code audit",
            "이 변경 깨뜨려봐",
            "빈틈 찾아줘",
            "adversarial review",
            "stress test this diff",
            "find blind spots",
            "/interrogate",
            "$interrogate",
            "--md",
            "마크다운만",
        ):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, description)
        for sibling in ("diff-summary", "blast-radius", "review-me"):
            with self.subTest(sibling=sibling):
                self.assertIn(sibling, description)
        self.assertNotIn("code-review-md", description)
        self.assertIn("$interrogate", openai)

    def test_env_example_is_not_classified_as_security_sensitive(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts" / "diff_stats.py")],
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

    def test_skill_enforces_the_evidence_first_writing_contract(self) -> None:
        skill_text = MAIN_SKILL.read_text(encoding="utf-8")

        for fragment in (
            "## Evidence-first writing contract",
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
            "Start the report with its title and parser-significant metadata, then "
            "present findings.",
        ):
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

    def test_skill_preserves_parser_significant_english_metadata_keys(self) -> None:
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
        for key in ("Date", "Reviewer", "Scope", "Repository", "Language",
                    "Evidence", "Dropped"):
            with self.subTest(key=key):
                self.assertIn(f"**{key}:**", skill_text)
        self.assertIn("**Language:** ko", skill_text)
        self.assertIn("**Reviewer:** automated review", skill_text)
        self.assertNotIn("**Reviewer:** Codex", skill_text)

    def test_proof_ladder_is_ordered_and_every_finding_carries_evidence(self) -> None:
        skill_text = MAIN_SKILL.read_text(encoding="utf-8")
        rows = [skill_text.find(f"| `{level}` |") for level in
                ("said", "cited", "traced", "ran", "reproduced")]

        for row in rows:
            self.assertNotEqual(-1, row)
        self.assertEqual(sorted(rows), rows)
        template = skill_text[skill_text.index("#### [CR-001]"):]
        self.assertLess(
            template.index("**Evidence:** ran"),
            template.index("**Observed behavior:**"),
        )
        self.assertIn("the exact command and the output it printed", skill_text)
        self.assertIn("the numbered walk", skill_text)

    def test_dropped_findings_and_top_severity_proof_rules(self) -> None:
        text = normalized(MAIN_SKILL)

        self.assertIn("A finding that cannot reach `cited` is dropped.", text)
        self.assertIn("It is never shown as a finding", text)
        self.assertIn("**Dropped:** N (below `cited`)", text)
        self.assertIn(
            "Before reporting a CRITICAL or HIGH finding, push it to `traced` or `ran`.",
            text,
        )
        self.assertIn("`cited, not traced`", text)

    def test_markdown_only_mode_replaces_the_old_variant(self) -> None:
        text = normalized(MAIN_SKILL)

        self.assertIn("## Output modes", text)
        self.assertIn(
            '| `--md`, "markdown only", "마크다운만" | One Markdown report under '
            "`.reviews/`, in the prompt's language | None. No HTML is generated |",
            text,
        )
        self.assertIn("## 7. Generate HTML (skip with `--md`)", text)
        self.assertIn("Generate HTML or open a browser in `--md` mode.", text)
        self.assertNotIn("code-review-md", text)

    def test_report_only_stance(self) -> None:
        text = normalized(MAIN_SKILL)

        self.assertIn("Report the findings; never apply a fix", text)
        self.assertIn("Apply a fix, edit the reviewed tree", text)
        self.assertIn("Comment on code outside the diff", text)
        self.assertIn("Modify `.gitignore` (suggest only).", text)

    def test_safe_proof_rules(self) -> None:
        text = normalized(MAIN_SKILL)

        for rule in (
            "Proof commands are read-only with respect to the reviewed tree",
            "a small repro script in a temporary directory outside the repository",
            "Never mutate the reviewed tree",
            "never run destructive commands",
            "never send repository content to the network",
            "`git status --porcelain` before and after each proof run",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)
        reference = normalized(PROOF_REFERENCE)
        self.assertIn("outside the repository (`mktemp -d`)", reference)
        self.assertIn("call any network endpoint", reference)

    def test_optional_panel_uses_swarm_only_when_installed(self) -> None:
        text = normalized(MAIN_SKILL)

        self.assertIn("When the `swarm` skill is installed", text)
        self.assertIn("Rerun each returned finding's command", text)
        self.assertIn("Merge findings that share a root cause", text)
        self.assertIn("per adversary", text)
        self.assertIn("Without `swarm`, review in this session and say", text)
        self.assertIn("## Panel brief", PROOF_REFERENCE.read_text(encoding="utf-8"))

    def test_skill_ends_with_a_reply_contract(self) -> None:
        last_line = MAIN_SKILL.read_text(encoding="utf-8").rstrip().splitlines()[-1]

        self.assertTrue(last_line.startswith("**Reply:**"))
        for item in ("dropped count", "proof commands", "panel status",
                     "browser-open result"):
            with self.subTest(item=item):
                self.assertIn(item, last_line)

    def test_prompts_remove_mandatory_padding_and_uncertain_info(self) -> None:
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

        for path in (MAIN_SKILL, COMMAND):
            prompt = path.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                with self.subTest(path=path.relative_to(ROOT), pattern=pattern):
                    self.assertIsNone(re.search(pattern, prompt, re.IGNORECASE))

    def test_command_routes_internally_and_carries_both_modes(self) -> None:
        command = COMMAND.read_text(encoding="utf-8")

        self.assertIn(
            "Apply the **interrogate** skill internally. Do not echo or announce "
            "this routing instruction.",
            command,
        )
        self.assertIn("evidence-first", command.lower())
        self.assertIn('argument-hint: "[scope] [--md]"', command)
        self.assertIn("$ARGUMENTS", command)
        for fragment in (
            "bilingual",
            "fact-only handoff",
            "finding counts by severity",
            "browser-open fact",
            "Runs `python <skill-path>/scripts/generate_html_report.py`",
            "Opens the resulting `.html` file in a browser.",
            "generates no HTML and opens no browser",
            "never apply a fix",
            "`**Dropped:**`",
            "/blast-radius",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, command)
        for forbidden in ("Before starting", "**Announce at start:**",
                          "urgent finding inline", "code-review-md"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, command)

    def test_evals_cover_happy_path_refusal_and_sibling(self) -> None:
        data = json.loads(
            (SKILL_DIR / "evals" / "evals.json").read_text(encoding="utf-8")
        )

        self.assertEqual("interrogate", data["skill_name"])
        self.assertGreaterEqual(len(data["evals"]), 3)
        for item in data["evals"]:
            with self.subTest(eval_id=item["id"]):
                self.assertGreaterEqual(len(item["assertions"]), 2)
        text = json.dumps(data, ensure_ascii=False)
        for fragment in ("diff-summary", "blast-radius", "cited, not traced",
                         "No HTML file is generated", "swarm"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_skills_cli_discovers_interrogate_and_blast_radius(self) -> None:
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
        for name in ("interrogate", "blast-radius"):
            with self.subTest(name=name):
                self.assertRegex(
                    result.stdout, re.compile(rf"(?m)^[^A-Za-z0-9]*{name}\s*$")
                )
        for gone in ("code-review", "code-review-md", "code-review-html"):
            with self.subTest(gone=gone):
                self.assertNotRegex(
                    result.stdout, re.compile(rf"(?m)^[^A-Za-z0-9]*{gone}\s*$")
                )


if __name__ == "__main__":
    unittest.main()
