import json
import os
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_SKILL = ROOT / "doc-skill"
SKILL = DOC_SKILL / "skills" / "gendoc" / "SKILL.md"


class DocSkillPackageTests(unittest.TestCase):
    def test_skills_cli_discovers_gendoc(self) -> None:
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
        self.assertRegex(result.stdout, re.compile(r"(?m)^[^A-Za-z0-9]*gendoc\s*$"))

    def test_doc_skill_plugin_shape_is_packaged(self) -> None:
        self.assertTrue((DOC_SKILL / ".claude-plugin" / "plugin.json").is_file())
        self.assertTrue((DOC_SKILL / "commands" / "gen-docs.md").is_file())
        self.assertTrue(SKILL.is_file())

        for name in [
            "README.md.tmpl",
            "README.ko.md.tmpl",
            "ARCHITECTURE.md.tmpl",
            "USAGE.md.tmpl",
        ]:
            with self.subTest(template=name):
                self.assertTrue((DOC_SKILL / "skills" / "gendoc" / "templates" / name).is_file())

        for name in ["README.md", "README.ko.md", "ARCHITECTURE.md", "USAGE.md"]:
            with self.subTest(doc=name):
                self.assertTrue((DOC_SKILL / name).is_file())

    def test_doc_skill_metadata_and_command_route_to_gendoc(self) -> None:
        metadata = json.loads((DOC_SKILL / ".claude-plugin" / "plugin.json").read_text())
        command = (DOC_SKILL / "commands" / "gen-docs.md").read_text(encoding="utf-8")

        self.assertEqual(metadata["name"], "doc-skill")
        self.assertEqual(metadata["version"], "0.1.0")
        self.assertIn("documentation", metadata["description"].lower())
        self.assertIn("Use the **gendoc** skill", command)
        self.assertIn("README.md", command)
        self.assertIn("ARCHITECTURE.md", command)
        self.assertIn("USAGE.md", command)

    def test_gendoc_skill_enforces_document_contracts_and_safety(self) -> None:
        text = SKILL.read_text(encoding="utf-8")

        required_phrases = [
            "README.md",
            "README.ko.md",
            "ARCHITECTURE.md",
            "USAGE.md",
            "front door",
            "diff",
            "confirmation",
            "doc-skill:keep",
            "Never modify files outside",
            "REQUIRED BACKGROUND: Use writing-skills",
            "baseline failures",
            "hybrid analysis",
            "parallel Explore subagents",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_templates_encode_the_four_doc_roles(self) -> None:
        templates = DOC_SKILL / "skills" / "gendoc" / "templates"
        readme = (templates / "README.md.tmpl").read_text(encoding="utf-8")
        readme_ko = (templates / "README.ko.md.tmpl").read_text(encoding="utf-8")
        architecture = (templates / "ARCHITECTURE.md.tmpl").read_text(encoding="utf-8")
        usage = (templates / "USAGE.md.tmpl").read_text(encoding="utf-8")

        self.assertIn("Quick start", readme)
        self.assertIn("ARCHITECTURE.md", readme)
        self.assertIn("USAGE.md", readme)
        self.assertIn("빠른 시작", readme_ko)
        self.assertIn("Components", architecture)
        self.assertIn("Data flow", architecture)
        self.assertIn("Command reference", usage)
        self.assertIn("Troubleshooting", usage)
