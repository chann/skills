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
SKILL_NAMES = ("plan-summary",)
# Variant selectors folded into `plan-summary --md` and `plan-summary --quiz`.
REMOVED_VARIANT_SKILLS = ("plan-summary-md", "plan-summary-quiz")
BASE = PLUGIN / "skills" / "plan-summary"
SHARED_FILES = (
    Path("scripts/collect_plan_evidence.py"),
    Path("scripts/generate_plan_summary.py"),
    Path("assets/summary-template.html"),
)
REPORT_TEST = ROOT / "tests" / "plan_summary" / "test_summary_report.py"


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
    def test_one_selector_package_is_complete_and_variants_are_gone(self) -> None:
        skill = PLUGIN / "skills" / "plan-summary"
        required = [
            skill / "SKILL.md",
            skill / "agents" / "openai.yaml",
            skill / "evals" / "evals.json",
            *[skill / relative for relative in SHARED_FILES],
            PLUGIN / "commands" / "plan-summary.md",
            PLUGIN / "README.md",
            PLUGIN / "README.ko.md",
        ]
        for path in required:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file(), f"missing packaged file: {path}")

        for name in REMOVED_VARIANT_SKILLS:
            with self.subTest(removed=name):
                self.assertFalse((PLUGIN / "skills" / name).exists())
                self.assertFalse((PLUGIN / "commands" / f"{name}.md").exists())
        self.assertEqual(
            sorted(path.name for path in (PLUGIN / "skills").iterdir()),
            ["plan-summary"],
        )
        self.assertEqual(
            sorted(path.name for path in (PLUGIN / "commands").iterdir()),
            ["plan-summary.md"],
        )
        for filename in ("collect_plan_evidence.py", "generate_plan_summary.py"):
            with self.subTest(filename=filename):
                self.assertEqual(len(list(PLUGIN.rglob(filename))), 1)
        self.assertEqual(list(PLUGIN.rglob("plan-summary-workflow.md")), [])

    def test_plugin_metadata_registers_the_two_point_zero_release(self) -> None:
        metadata = json.loads(
            (PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

        self.assertEqual(metadata["name"], "plan-summary")
        self.assertEqual(metadata["version"], "2.0.0")
        self.assertIn("--md", metadata["description"])
        self.assertIn("--quiz", metadata["description"])

    def test_command_routes_exact_paths_as_data_and_documents_options(self) -> None:
        command = (PLUGIN / "commands" / "plan-summary.md").read_text(encoding="utf-8")

        self.assertIn("**plan-summary** skill", command)
        self.assertIn('argument-hint: "<source-path ...> [--md] [--quiz]"', command)
        self.assertIn("explicit", command.lower())
        self.assertIn("path data", command)
        self.assertIn("Korean and English", command)
        self.assertIn("browser-open attempt", command)
        self.assertIn("Do not generate HTML", command)
        self.assertIn("## Quiz", command)
        self.assertIn("question count", command)
        self.assertNotIn("plan-summary-md", command)

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
        self.assertIn("--md", frontmatter)
        self.assertIn("--quiz", frontmatter)
        self.assertLessEqual(len(re.search(r"(?m)^description:\s*(.+)$", frontmatter).group(1)), 1024)
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

    def test_skill_documents_the_option_table_and_both_mode_contracts(self) -> None:
        text = (BASE / "SKILL.md").read_text(encoding="utf-8")
        options = re.search(r"(?ms)^## Options\n(?P<body>.*?)(?=^## )", text)
        self.assertIsNotNone(options, "the skill must have an ## Options section")
        for fragment in (
            "| `/plan-summary <path ...>` |",
            "`--md`",
            "`--quiz`",
            "`/plan-summary <path ...> --md --quiz`",
            "markdown only",
            "마크다운만",
            "퀴즈",
            "quiz me",
            "Strip only the exact tokens `--md` and `--quiz`",
            "`--md` decides that no HTML or browser is produced",
        ):
            with self.subTest(option=fragment):
                self.assertIn(fragment, options.group("body") if options else "")

        markdown = re.search(
            r"(?ms)^### Markdown only \(`--md`\)\n(?P<body>.*?)(?=^## )", text
        )
        self.assertIsNotNone(markdown, "the skill must document the --md generation step")
        markdown_text = markdown.group("body") if markdown else ""
        self.assertIn("--markdown-only", markdown_text)
        self.assertIn("--markdown-stdin --markdown-only", markdown_text)
        self.assertIn("do not attempt a browser open", markdown_text)

        quiz = re.search(
            r"(?ms)^## Quiz Contract \(`--quiz`\)\n(?P<body>.*?)(?=^## )", text
        )
        self.assertIsNotNone(quiz, "the skill must document the quiz contract")
        quiz_text = quiz.group("body") if quiz else ""
        self.assertIn("## Quiz", quiz_text)
        self.assertIn("five questions by default", quiz_text)
        self.assertIn("2 to 6", quiz_text)
        self.assertIn("exactly one", quiz_text)
        self.assertIn("same correct-option index", quiz_text)
        self.assertIn("question count", text)

    def test_skill_ends_with_a_reply_contract_and_uses_new_names(self) -> None:
        text = (BASE / "SKILL.md").read_text(encoding="utf-8")

        self.assertTrue(text.rstrip("\n").splitlines()[-1].startswith("**Reply:**"))
        self.assertIn("`unslop`", text)
        for stale in (
            "human-friendly-writing",
            "plan-summary-md",
            "plan-summary-quiz",
            "plan-summary-workflow.md",
            "synchronized",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, text)

    def test_codex_interface_uses_canonical_name_and_selector(self) -> None:
        text = (BASE / "agents" / "openai.yaml").read_text(encoding="utf-8")
        fields = re.findall(r"(?m)^  ([a-z_]+):", text)

        self.assertEqual(
            set(fields), {"display_name", "short_description", "default_prompt"}
        )
        self.assertIn('display_name: "Plan Summary"', text)
        self.assertIn(
            'short_description: "Summarize plans in aligned Korean and English"', text
        )
        self.assertIn("$plan-summary", text)

    def test_skills_cli_discovers_only_the_plan_summary_selector(self) -> None:
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
        for name in REMOVED_VARIANT_SKILLS:
            with self.subTest(removed=name):
                self.assertNotRegex(
                    result.stdout,
                    re.compile(rf"(?m)^[^A-Za-z0-9]*{re.escape(name)}\s*$"),
                )

    def test_exact_selector_installs_and_generates_every_mode(self) -> None:
        environment = os.environ.copy()
        environment.update({"NO_COLOR": "1", "FORCE_COLOR": "0"})
        fixtures = load_report_fixtures()
        name = "plan-summary"
        with tempfile.TemporaryDirectory() as target:
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
            for relative in (Path("SKILL.md"), Path("agents/openai.yaml"), *SHARED_FILES):
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
            self.assertEqual(collector_result.returncode, 0, collector_result.stderr)
            collected = json.loads(collector_result.stdout)
            self.assertEqual(
                [document["display_path"] for document in collected["documents"]],
                ["plan-summary/README.md"],
            )

            plain = (fixtures.KO_REPORT, fixtures.EN_REPORT)
            quiz = (fixtures.KO_QUIZ_REPORT, fixtures.EN_QUIZ_REPORT)
            modes = (
                ("default", plain, (), 3),
                ("md", plain, ("--markdown-only",), 2),
                ("quiz", quiz, (), 3),
                ("md-quiz", quiz, ("--markdown-only",), 2),
            )
            for mode, reports, flags, expected_count in modes:
                with self.subTest(mode=mode):
                    output_directory = Path(target) / f"artifacts-{mode}"
                    generator_result = subprocess.run(
                        [
                            sys.executable,
                            "-I",
                            str(installed / "scripts" / "generate_plan_summary.py"),
                            "--bilingual-json-stdin",
                            "--output-directory",
                            str(output_directory),
                            *flags,
                        ],
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
                    self.assertEqual(len(artifacts), expected_count)
                    self.assertTrue(all(path.is_file() for path in artifacts))
                    self.assertEqual(
                        sum(path.suffix == ".html" for path in artifacts),
                        0 if flags else 1,
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
