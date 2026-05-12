import os
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LONG_TASK = ROOT / "long-task"


class LongTaskSkillPackageTests(unittest.TestCase):
    def test_skills_cli_discovers_long_task(self) -> None:
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
        self.assertRegex(result.stdout, re.compile(r"(?m)^[^A-Za-z0-9]*long-task\s*$"))

    def test_long_task_runtime_is_packaged_inside_skill(self) -> None:
        helper = LONG_TASK / "skills" / "long-task" / "scripts" / "long_task.py"
        command = (LONG_TASK / "commands" / "long-task.md").read_text(encoding="utf-8")
        skill = (LONG_TASK / "skills" / "long-task" / "SKILL.md").read_text(encoding="utf-8")

        self.assertTrue(helper.is_file(), "long_task.py must be inside the installable skill folder")
        self.assertIn("$CLAUDE_PLUGIN_ROOT/skills/long-task/scripts/long_task.py", command)
        self.assertIn("scripts/long_task.py", skill)

    def test_long_task_does_not_require_separate_install_script(self) -> None:
        checked_paths = [
            LONG_TASK / "commands" / "long-task.md",
            LONG_TASK / "skills" / "long-task" / "SKILL.md",
            LONG_TASK / "README.md",
            LONG_TASK / "README.ko.md",
        ]

        for path in checked_paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("install.sh", text)

        self.assertFalse((LONG_TASK / "scripts" / "install.sh").exists())
