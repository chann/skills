import json
import os
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "handoff"
SKILL_NAME = "handoff"
SKILL_DIR = HANDOFF / "skills" / SKILL_NAME
SKILL = SKILL_DIR / "SKILL.md"
FRONTEND_REF = SKILL_DIR / "references" / "frontend.md"
BACKEND_REF = SKILL_DIR / "references" / "backend.md"
SESSION_REF = SKILL_DIR / "references" / "session.md"
OLD_NAMES = ("gen-frontend-handoff", "gen-backend-handoff", "gen-session-handoff")


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def frontmatter(path: Path) -> str:
    return path.read_text(encoding="utf-8").split("---\n", 2)[1]


class HandoffSkillPackageTests(unittest.TestCase):
    def test_skills_cli_discovers_the_handoff_skill(self) -> None:
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
        self.assertRegex(result.stdout, re.compile(r"(?m)^[^A-Za-z0-9]*handoff\s*$"))
        for old in OLD_NAMES:
            with self.subTest(old=old):
                self.assertNotRegex(result.stdout, re.compile(rf"(?m)^[^A-Za-z0-9]*{old}\s*$"))

    def test_package_shape_is_complete(self) -> None:
        expected = (
            HANDOFF / ".claude-plugin" / "plugin.json",
            HANDOFF / "commands" / f"{SKILL_NAME}.md",
            SKILL,
            SKILL_DIR / "agents" / "openai.yaml",
            SKILL_DIR / "evals" / "evals.json",
            FRONTEND_REF,
            BACKEND_REF,
            SESSION_REF,
        )
        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_the_three_old_packages_are_gone(self) -> None:
        for old in OLD_NAMES:
            with self.subTest(old=old):
                self.assertFalse((HANDOFF / "skills" / old).exists())
                self.assertFalse((HANDOFF / "commands" / f"{old}.md").exists())
        self.assertEqual([SKILL_NAME], sorted(p.name for p in (HANDOFF / "skills").iterdir()))

    def test_plugin_metadata_and_command_route_to_the_skill(self) -> None:
        metadata = json.loads(
            (HANDOFF / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        command = (HANDOFF / "commands" / f"{SKILL_NAME}.md").read_text(encoding="utf-8")

        self.assertEqual("handoff", metadata["name"])
        self.assertEqual("1.0.0", metadata["version"])
        self.assertIn("handoff", metadata["description"].lower())
        self.assertIn("session-to-session", metadata["description"])
        self.assertIn("Use the **handoff** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn("argument-hint:", command)
        self.assertIn("frontend | backend | session", command)

    def test_interfaces_publish_both_selectors(self) -> None:
        block = frontmatter(SKILL)
        openai = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn(f"name: {SKILL_NAME}", block)
        self.assertIn(f"/{SKILL_NAME}", block)
        self.assertIn(f"${SKILL_NAME}", block)
        self.assertIn(f"${SKILL_NAME}", openai)

    def test_description_covers_three_audiences_and_siblings(self) -> None:
        match = re.search(r"(?m)^description: (.*)$", frontmatter(SKILL))
        self.assertIsNotNone(match)
        description = match.group(1)

        self.assertLessEqual(len(description), 1024)
        self.assertTrue(description.startswith("Use when"))
        self.assertNotIn("disable-model-invocation", frontmatter(SKILL))
        for trigger in (
            "프론트 인수인계",
            "백엔드에 넘길 문서",
            "다음 세션에서 이어갈 수 있게",
            "handoff for the client team",
            "hand this session off",
            "frontend",
            "backend",
            "session",
        ):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, description)
        self.assertIn("recall", description)
        self.assertIn("diff-summary", description)

    def test_audience_resolution_is_stated_once_and_never_silent(self) -> None:
        text = normalized(SKILL)

        self.assertIn("## 1. Resolve the audience", text)
        self.assertIn("**The argument.**", text)
        self.assertIn("**The request's wording.**", text)
        self.assertIn("**Inference.**", text)
        self.assertIn("State the resolved audience and the reason in the first line", text)
        self.assertIn("Never pick silently", text)
        self.assertIn('asked for "the handoff", write both and say so', text)

    def test_skill_loads_exactly_the_reference_for_each_audience(self) -> None:
        text = normalized(SKILL)

        self.assertIn("load exactly the reference for each resolved audience", text)
        for reference in ("frontend", "backend", "session"):
            with self.subTest(reference=reference):
                self.assertIn(f"references/{reference}.md", text)
        for output in (
            ".handoffs/<YYYY-MM-DD>_<scope>_frontend.md",
            ".handoffs/<YYYY-MM-DD>_<scope>_backend.md",
            ".handoffs/<YYYY-MM-DD>_<slug>_session.md",
        ):
            with self.subTest(output=output):
                self.assertIn(output, text)

    def test_shared_rules_live_in_the_skill_body_once(self) -> None:
        text = normalized(SKILL)

        for phrase in (
            "main...feature",
            "user-specified scope",
            "Do not claim unverified tests, deploys, or runtime behavior",
            "do not claim anything works without the command that proved it",
            "Not verified in this handoff",
            "User-provided session context",
            "Never include secrets from `.env`",
            "Do not commit or push",
            "`unslop`",
            "Do not install, fetch, or require it",
            "Evidence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        self.assertNotIn("human-friendly-writing", text)
        for name in OLD_NAMES:
            self.assertNotIn(name, text)

    def test_frontend_reference_enforces_client_contract(self) -> None:
        text = normalized(FRONTEND_REF)

        for phrase in (
            "API response fields",
            "type updates",
            "rendering impact",
            "loading, empty, and error states",
            "client action 없음",
            "DB-only",
            "Open Questions",
            "Continuation Prompt",
            "Evidence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_backend_reference_enforces_server_contract(self) -> None:
        text = normalized(BACKEND_REF)

        for phrase in (
            "API contract",
            "database migrations",
            "jobs, queues, and scheduled tasks",
            "backward compatibility",
            "frontend/client action",
            "No external action found",
            "Continuation Prompt",
            "Evidence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_session_reference_orders_the_handoff_workflow(self) -> None:
        text = SESSION_REF.read_text(encoding="utf-8")
        ordered = [
            "## 1. Separate what is proven from what is not",
            "## 2. Say where the work is",
            "## 3. Record the decisions and the traps",
            "## 4. Write the next actions as checkable steps",
            "## 5. End with a resume prompt",
            "## Refusals",
        ]

        positions = [text.find(heading) for heading in ordered]
        for heading, position in zip(ordered, positions):
            with self.subTest(heading=heading):
                self.assertNotEqual(-1, position)
        self.assertEqual(sorted(positions), positions)

    def test_session_reference_separates_proven_state_from_unproven(self) -> None:
        text = normalized(SESSION_REF)
        for contract in (
            ".handoffs/<YYYY-MM-DD>_<slug>_session.md",
            "### Proven",
            "### Unproven",
            '"I implemented X" is not a proven claim.',
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_session_reference_references_artifacts_instead_of_restating_them(self) -> None:
        text = normalized(SESSION_REF)
        self.assertIn("references artifacts instead of restating them", text)
        self.assertIn("Do not copy a plan, spec, diff, or issue into the handoff", text)
        self.assertIn("diagnosis record", text)

    def test_session_reference_records_decisions_and_ruled_out_approaches(self) -> None:
        text = normalized(SESSION_REF)
        for phrase in ("**Decisions made**", "**Ruled out**", "**Traps**", "**Decisions still open**"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_session_reference_requires_done_checks_and_a_resume_prompt(self) -> None:
        text = normalized(SESSION_REF)
        self.assertIn("Do not write next actions without a done-check", text)
        self.assertIn("**Suggested skills**", text)
        self.assertIn("It is a pointer, not a second copy of the handoff", text)
        self.assertIn("Do not summarize the conversation turn by turn", text)

    def test_session_reference_hands_cross_team_work_to_the_other_audiences(self) -> None:
        text = normalized(SESSION_REF)
        self.assertIn("`frontend` or `backend`", text)
        for name in OLD_NAMES:
            self.assertNotIn(name, text)

    def test_skill_ends_with_a_reply_contract(self) -> None:
        last = SKILL.read_text(encoding="utf-8").rstrip().splitlines()[-1]

        self.assertTrue(last.startswith("**Reply:**"), last)
        for item in ("audience", "path", "proven", "open questions", "refusal"):
            with self.subTest(item=item):
                self.assertIn(item, last)

    def test_evals_cover_audiences_refusals_and_siblings(self) -> None:
        data = json.loads((SKILL_DIR / "evals" / "evals.json").read_text(encoding="utf-8"))

        self.assertEqual(SKILL_NAME, data["skill_name"])
        self.assertGreaterEqual(len(data["evals"]), 3)
        for item in data["evals"]:
            with self.subTest(eval=item["id"]):
                self.assertGreaterEqual(len(item["assertions"]), 2)
        prompts = " ".join(item["prompt"] for item in data["evals"])
        for needle in ("frontend", "backend", "session", "recall", "staging token"):
            with self.subTest(needle=needle):
                self.assertIn(needle, prompts + " ".join(i["expected_output"] for i in data["evals"]))

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
                self.assertIn(f'"{SKILL_NAME}"', path.read_text(encoding="utf-8"))

    def test_installation_docs_use_the_handoff_selector(self) -> None:
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
                self.assertIn("chann/skills --skill handoff", text)
                self.assertIn(f"/{SKILL_NAME}", text)
                self.assertIn(f"${SKILL_NAME}", text)

    def test_plugin_readmes_carry_the_migration_table(self) -> None:
        for path in (HANDOFF / "README.md", HANDOFF / "README.ko.md"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(doc=path.relative_to(ROOT)):
                for old, new in (
                    ("/gen-frontend-handoff", "/handoff frontend"),
                    ("/gen-backend-handoff", "/handoff backend"),
                    ("/gen-session-handoff", "/handoff session"),
                ):
                    self.assertIn(old, text)
                    self.assertIn(new, text)
                self.assertIn("unslop", text)
                self.assertNotIn("human-friendly-writing", text)


if __name__ == "__main__":
    unittest.main()
