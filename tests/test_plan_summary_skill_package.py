from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plan-summary"
SKILL_NAMES = ("plan-summary", "plan-summary-md", "plan-summary-quiz")
BASE = PLUGIN / "skills" / "plan-summary"
SHARED_FILES = (
    Path("scripts/collect_plan_evidence.py"),
    Path("scripts/generate_plan_summary.py"),
    Path("assets/summary-template.html"),
)
REPORT_TEST = ROOT / "tests" / "plan_summary" / "test_summary_report.py"


def skill_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.split("---\n", 2)[2].lstrip("\n")


def load_report_fixtures():
    spec = importlib.util.spec_from_file_location(
        "_plan_summary_report_fixtures", REPORT_TEST
    )
    if spec is None or spec.loader is None:
        raise AssertionError("plan-summary report fixtures could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PlanSummarySkillPackageTests(unittest.TestCase):
    def test_three_exact_selector_packages_are_complete(self) -> None:
        for name in SKILL_NAMES:
            skill = PLUGIN / "skills" / name
            required = [
                skill / "SKILL.md",
                skill / "agents" / "openai.yaml",
                *[skill / relative for relative in SHARED_FILES],
                PLUGIN / "commands" / f"{name}.md",
            ]
            if name != "plan-summary":
                required.append(skill / "references" / "plan-summary-workflow.md")
            for path in required:
                with self.subTest(skill=name, path=path.relative_to(ROOT)):
                    self.assertTrue(path.is_file(), f"missing packaged file: {path}")

    def test_plugin_metadata_registers_one_point_zero_release(self) -> None:
        metadata = json.loads(
            (PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

        self.assertEqual(metadata["name"], "plan-summary")
        self.assertEqual(metadata["version"], "1.0.0")
        for name in SKILL_NAMES:
            self.assertIn(name, metadata["description"])

    def test_commands_route_exact_paths_as_data_and_pin_output_modes(self) -> None:
        for name in SKILL_NAMES:
            command = (PLUGIN / "commands" / f"{name}.md").read_text(encoding="utf-8")
            with self.subTest(skill=name):
                self.assertIn(f"**{name}** skill", command)
                self.assertIn('argument-hint: "[source-path ...]"', command)
                self.assertIn("explicit", command.lower())
                self.assertIn("path data", command)
                self.assertIn("Korean and English", command)
        markdown = (PLUGIN / "commands" / "plan-summary-md.md").read_text(encoding="utf-8")
        quiz = (PLUGIN / "commands" / "plan-summary-quiz.md").read_text(encoding="utf-8")
        self.assertIn("Do not generate HTML", markdown)
        self.assertNotIn("browser-open attempt", markdown)
        self.assertIn("## Quiz", quiz)
        self.assertIn("question count", quiz)

    def test_base_skill_documents_triggers_and_fail_closed_boundaries(self) -> None:
        text = (BASE / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        for trigger in (
            "plan 요약",
            "PRD 요약",
            "설계문서 요약",
            "summarize this plan",
            "summarize this PRD",
            "design document summary",
            "/plan-summary",
            "$plan-summary",
        ):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, frontmatter)
        for contract in (
            "Do not scan",
            "untrusted data",
            "collect_plan_evidence.py",
            "generate_plan_summary.py",
            "--bilingual-json-stdin",
            ".plan-summaries/",
            "PS-001",
            "Source Digests",
            "browser-open attempt",
            "Do not critique",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_variant_skills_pin_markdown_and_quiz_contracts(self) -> None:
        markdown = (PLUGIN / "skills" / "plan-summary-md" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        quiz = (PLUGIN / "skills" / "plan-summary-quiz" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("--markdown-only", markdown)
        self.assertIn("never generates HTML", markdown)
        self.assertIn("never attempts a browser open", markdown)
        self.assertIn("## Quiz", quiz)
        self.assertIn("five questions by default", quiz)
        self.assertIn("2 to 6", quiz)
        self.assertIn("exactly one", quiz)
        self.assertIn("same correct-option index", quiz)

    def test_codex_interfaces_use_canonical_names_and_selectors(self) -> None:
        expected = {
            "plan-summary": (
                "Plan Summary",
                "Summarize plans in aligned Korean and English",
            ),
            "plan-summary-md": (
                "Plan Summary Markdown",
                "Write bilingual plan summaries as Markdown only",
            ),
            "plan-summary-quiz": (
                "Plan Summary Quiz",
                "Summarize plans with a comprehension quiz",
            ),
        }
        for name, (display_name, description) in expected.items():
            text = (
                PLUGIN / "skills" / name / "agents" / "openai.yaml"
            ).read_text(encoding="utf-8")
            fields = re.findall(r"(?m)^  ([a-z_]+):", text)
            with self.subTest(skill=name):
                self.assertEqual(
                    set(fields), {"display_name", "short_description", "default_prompt"}
                )
                self.assertIn(f'display_name: "{display_name}"', text)
                self.assertIn(f'short_description: "{description}"', text)
                self.assertIn(f"${name}", text)

    def test_variants_bundle_byte_synchronized_standalone_runtime(self) -> None:
        workflow = skill_body(BASE / "SKILL.md")
        for name in ("plan-summary-md", "plan-summary-quiz"):
            variant = PLUGIN / "skills" / name
            with self.subTest(skill=name):
                self.assertEqual(
                    (variant / "references" / "plan-summary-workflow.md").read_text(
                        encoding="utf-8"
                    ),
                    workflow,
                )
                for relative in SHARED_FILES:
                    self.assertEqual(
                        (variant / relative).read_bytes(),
                        (BASE / relative).read_bytes(),
                        f"standalone runtime drifted: {name}/{relative}",
                    )

    def test_skills_cli_discovers_all_three_exact_selectors(self) -> None:
        environment = os.environ.copy()
        environment.update({"NO_COLOR": "1", "FORCE_COLOR": "0"})
        result = subprocess.run(
            ["npx", "--yes", "skills", "add", str(PLUGIN), "-l", "--full-depth"],
            cwd=ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        for name in SKILL_NAMES:
            with self.subTest(skill=name):
                self.assertRegex(
                    result.stdout,
                    re.compile(rf"(?m)^[^A-Za-z0-9]*{re.escape(name)}\s*$"),
                )

    def test_exact_selector_installs_and_generates_expected_artifacts(self) -> None:
        environment = os.environ.copy()
        environment.update({"NO_COLOR": "1", "FORCE_COLOR": "0"})
        fixtures = load_report_fixtures()
        for name in SKILL_NAMES:
            with self.subTest(skill=name), tempfile.TemporaryDirectory() as target:
                subprocess.run(["git", "init", "-q"], cwd=target, check=True)
                result = subprocess.run(
                    [
                        "npx",
                        "--yes",
                        "skills",
                        "add",
                        str(PLUGIN),
                        "--skill",
                        name,
                        "--agent",
                        "codex",
                        "--copy",
                        "--yes",
                        "--full-depth",
                    ],
                    cwd=target,
                    env=environment,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=60,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout)
                installed = Path(target) / ".agents" / "skills" / name
                required = [
                    Path("SKILL.md"),
                    Path("agents/openai.yaml"),
                    *SHARED_FILES,
                ]
                if name != "plan-summary":
                    required.append(Path("references/plan-summary-workflow.md"))
                for relative in required:
                    self.assertTrue((installed / relative).is_file(), relative)

                collector_result = subprocess.run(
                    [
                        sys.executable,
                        "-I",
                        str(installed / "scripts" / "collect_plan_evidence.py"),
                    ],
                    cwd=ROOT,
                    input=json.dumps({"paths": ["plan-summary/README.md"]}),
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(
                    collector_result.returncode, 0, collector_result.stderr
                )
                collected = json.loads(collector_result.stdout)
                self.assertEqual(
                    [document["display_path"] for document in collected["documents"]],
                    ["plan-summary/README.md"],
                )

                reports = (
                    (fixtures.KO_QUIZ_REPORT, fixtures.EN_QUIZ_REPORT)
                    if name == "plan-summary-quiz"
                    else (fixtures.KO_REPORT, fixtures.EN_REPORT)
                )
                output_directory = Path(target) / "artifacts"
                command = [
                    sys.executable,
                    "-I",
                    str(installed / "scripts" / "generate_plan_summary.py"),
                    "--bilingual-json-stdin",
                    "--output-directory",
                    str(output_directory),
                ]
                if name == "plan-summary-md":
                    command.append("--markdown-only")
                generator_result = subprocess.run(
                    command,
                    input=json.dumps({"ko": reports[0], "en": reports[1]}),
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(
                    generator_result.returncode, 0, generator_result.stderr
                )
                artifacts = [
                    Path(path)
                    for path in json.loads(generator_result.stdout)["artifacts"]
                ]
                self.assertEqual(
                    len(artifacts), 2 if name == "plan-summary-md" else 3
                )
                self.assertTrue(all(path.is_file() for path in artifacts))
                self.assertEqual(
                    sum(path.suffix == ".html" for path in artifacts),
                    0 if name == "plan-summary-md" else 1,
                )

                help_result = subprocess.run(
                    [
                        sys.executable,
                        "-I",
                        str(installed / "scripts" / "generate_plan_summary.py"),
                        "--help",
                    ],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(help_result.returncode, 0, help_result.stderr)
                self.assertIn("--markdown-only", help_result.stdout)


if __name__ == "__main__":
    unittest.main()
