import json
import os
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "handoff"
FRONTEND_SKILL = HANDOFF / "skills" / "gen-frontend-handoff" / "SKILL.md"
BACKEND_SKILL = HANDOFF / "skills" / "gen-backend-handoff" / "SKILL.md"


class HandoffSkillPackageTests(unittest.TestCase):
    def test_skills_cli_discovers_handoff_skills(self) -> None:
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
        self.assertRegex(result.stdout, re.compile(r"(?m)^[^A-Za-z0-9]*gen-frontend-handoff\s*$"))
        self.assertRegex(result.stdout, re.compile(r"(?m)^[^A-Za-z0-9]*gen-backend-handoff\s*$"))

    def test_handoff_plugin_shape_is_packaged(self) -> None:
        self.assertTrue((HANDOFF / ".claude-plugin" / "plugin.json").is_file())
        self.assertTrue((HANDOFF / "commands" / "gen-frontend-handoff.md").is_file())
        self.assertTrue((HANDOFF / "commands" / "gen-backend-handoff.md").is_file())
        self.assertTrue(FRONTEND_SKILL.is_file())
        self.assertTrue(BACKEND_SKILL.is_file())

    def test_handoff_metadata_and_commands_route_to_skills(self) -> None:
        metadata = json.loads((HANDOFF / ".claude-plugin" / "plugin.json").read_text())
        frontend_command = (HANDOFF / "commands" / "gen-frontend-handoff.md").read_text(encoding="utf-8")
        backend_command = (HANDOFF / "commands" / "gen-backend-handoff.md").read_text(encoding="utf-8")

        self.assertEqual(metadata["name"], "handoff")
        self.assertEqual(metadata["version"], "0.1.0")
        self.assertIn("handoff", metadata["description"].lower())
        self.assertIn("Use the **gen-frontend-handoff** skill", frontend_command)
        self.assertIn("Use the **gen-backend-handoff** skill", backend_command)

    def test_frontend_handoff_enforces_client_contract_and_scope(self) -> None:
        text = FRONTEND_SKILL.read_text(encoding="utf-8")

        required_phrases = [
            "API response fields",
            "type updates",
            "rendering impact",
            "loading, empty, and error states",
            "client action 없음",
            "DB-only",
            "main...feature",
            "user-specified scope",
            "Do not claim unverified tests, deploys, or runtime behavior",
            "Continuation Prompt",
            "Evidence",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_backend_handoff_enforces_server_contract_and_scope(self) -> None:
        text = BACKEND_SKILL.read_text(encoding="utf-8")

        required_phrases = [
            "API contract",
            "database migrations",
            "jobs, queues, and scheduled tasks",
            "backward compatibility",
            "frontend/client action",
            "main...feature",
            "user-specified scope",
            "Do not claim unverified tests, deploys, or runtime behavior",
            "Continuation Prompt",
            "Evidence",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_installation_docs_use_handoff_skill_selectors(self) -> None:
        docs = [
            ROOT / "README.md",
            ROOT / "README.ko.md",
            ROOT / "USAGE.md",
            HANDOFF / "README.md",
            HANDOFF / "README.ko.md",
        ]

        for path in docs:
            with self.subTest(doc=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("chann/skills@handoff", text)
                self.assertIn("chann/skills --skill gen-frontend-handoff", text)
                self.assertIn("chann/skills --skill gen-backend-handoff", text)
