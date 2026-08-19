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
        self.assertEqual(metadata["version"], "0.3.0")
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


SESSION_SKILL_NAME = "gen-session-handoff"
SESSION_SKILL = HANDOFF / "skills" / SESSION_SKILL_NAME


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class GenSessionHandoffTests(unittest.TestCase):
    def test_package_shape_is_complete(self) -> None:
        expected = (
            SESSION_SKILL / "SKILL.md",
            SESSION_SKILL / "agents" / "openai.yaml",
            SESSION_SKILL / "evals" / "evals.json",
            HANDOFF / "commands" / f"{SESSION_SKILL_NAME}.md",
        )

        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_plugin_metadata_publishes_the_session_handoff(self) -> None:
        metadata = json.loads(
            (HANDOFF / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

        self.assertEqual("handoff", metadata["name"])
        self.assertEqual("0.3.0", metadata["version"])
        self.assertIn("session-to-session", metadata["description"])

    def test_interfaces_publish_both_selectors(self) -> None:
        block = (SESSION_SKILL / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)[1]
        openai = (SESSION_SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        command = (HANDOFF / "commands" / f"{SESSION_SKILL_NAME}.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(f"name: {SESSION_SKILL_NAME}", block)
        self.assertIn(f"/{SESSION_SKILL_NAME}", block)
        self.assertIn(f"${SESSION_SKILL_NAME}", block)
        self.assertIn(f"${SESSION_SKILL_NAME}", openai)
        self.assertIn(f"Use the **{SESSION_SKILL_NAME}** skill", command)
        self.assertIn("$ARGUMENTS", command)

    def test_skill_orders_the_handoff_workflow(self) -> None:
        text = (SESSION_SKILL / "SKILL.md").read_text(encoding="utf-8")
        ordered = [
            "## Output",
            "## 1. Separate what is proven from what is not",
            "## 2. Say where the work is",
            "## 3. Record the decisions and the traps",
            "## 4. Write the next actions as checkable steps",
            "## 5. End with a resume prompt",
            "## 6. Redact before saving",
            "## Refusals",
        ]

        positions = [text.find(heading) for heading in ordered]
        for heading, position in zip(ordered, positions):
            with self.subTest(heading=heading):
                self.assertNotEqual(-1, position)
        self.assertEqual(sorted(positions), positions)

    def test_skill_separates_proven_state_from_unproven(self) -> None:
        text = normalized(SESSION_SKILL / "SKILL.md")
        for contract in (
            ".handoffs/<YYYY-MM-DD>_<slug>_session.md",
            "### Proven",
            "### Unproven",
            '"I implemented X" is not a proven claim.',
            "Do not claim anything works without the command that proved it",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_skill_references_artifacts_instead_of_restating_them(self) -> None:
        text = normalized(SESSION_SKILL / "SKILL.md")
        self.assertIn("references artifacts instead of restating them", text)
        self.assertIn(
            "Do not copy a plan, spec, diff, or issue into the handoff", text
        )

    def test_skill_requires_done_checks_and_a_resume_prompt(self) -> None:
        text = normalized(SESSION_SKILL / "SKILL.md")
        self.assertIn("Do not write next actions without a done-check", text)
        self.assertIn("**Suggested skills**", text)
        self.assertIn("It is a pointer, not a second copy of the handoff", text)

    def test_skill_stays_out_of_the_cross_team_handoffs(self) -> None:
        text = normalized(SESSION_SKILL / "SKILL.md")
        self.assertIn("gen-frontend-handoff", text)
        self.assertIn("gen-backend-handoff", text)
        self.assertIn("Do not commit or push as part of writing the handoff", text)

    def test_catalog_and_every_locale_publish_the_skill(self) -> None:
        sources = [
            ROOT / "website" / "src" / "data" / "skills.ts",
            *(
                ROOT / "website" / "src" / "i18n" / "content" / f"{locale}.json"
                for locale in ("ko", "en", "jp", "cn")
            ),
        ]

        for path in sources:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn(f'"{SESSION_SKILL_NAME}"', path.read_text(encoding="utf-8"))

    def test_installation_docs_use_the_session_selector(self) -> None:
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
                self.assertIn(f"/{SESSION_SKILL_NAME}", text)
                self.assertIn(f"${SESSION_SKILL_NAME}", text)
