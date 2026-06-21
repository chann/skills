import json
import os
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODE_REVIEW = ROOT / "code-review"


class CodeReviewSkillPackageTests(unittest.TestCase):
    def test_skills_cli_discovers_diff_viewer(self) -> None:
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
        self.assertRegex(result.stdout, re.compile(r"(?m)^[^A-Za-z0-9]*diff-viewer\s*$"))

    def test_diff_viewer_slash_command_and_skill_are_packaged(self) -> None:
        command = CODE_REVIEW / "commands" / "diff-viewer.md"
        skill = CODE_REVIEW / "skills" / "diff-viewer" / "SKILL.md"
        script = CODE_REVIEW / "skills" / "diff-viewer" / "scripts" / "generate_diff_report.py"
        template = CODE_REVIEW / "skills" / "diff-viewer" / "assets" / "diff-template.html"

        self.assertTrue(command.is_file(), "Claude slash command must be packaged")
        self.assertTrue(skill.is_file(), "Codex/skill discovery requires SKILL.md")
        self.assertTrue(script.is_file(), "diff-viewer runtime must be inside the skill folder")
        self.assertTrue(template.is_file(), "HTML template must be inside the skill folder")

        command_text = command.read_text(encoding="utf-8")
        skill_text = skill.read_text(encoding="utf-8")
        self.assertIn("Use the **diff-viewer** skill", command_text)
        self.assertIn("scripts/generate_diff_report.py", skill_text)

    def test_code_review_plugin_metadata_mentions_diff_viewer(self) -> None:
        metadata = json.loads((CODE_REVIEW / ".claude-plugin" / "plugin.json").read_text())

        self.assertEqual(metadata["version"], "2.2.0")
        self.assertIn("diff-viewer", metadata["description"])
