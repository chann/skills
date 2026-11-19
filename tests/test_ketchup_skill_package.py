import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "recall"
SKILL = PACKAGE / "skills" / "ketchup"


class KetchupSkillPackageTests(unittest.TestCase):
    def test_package_shape_is_complete(self) -> None:
        expected = [
            PACKAGE / "commands" / "ketchup.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
        ]

        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_description_publishes_triggers_and_neighbours(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        description = text.split("---\n", 2)[1].split("description: ", 1)[1].strip()

        self.assertIn("name: ketchup", text.split("---\n", 2)[1])
        self.assertTrue(description.startswith("Use when"))
        self.assertLessEqual(len(description), 1024)
        for trigger in (
            "지금까지 뭐 바뀌었어?",
            "자리 비운 동안 뭐 했는지 알려줘",
            "catch me up on this chat",
            "what changed since my last message",
            "/ketchup",
            "$ketchup",
            "recall",
            "handoff session",
        ):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, description)

    def test_skill_pins_window_read_only_and_reply_contract(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        for contract in (
            "user's most recent message",
            "Notifications, subagent results",
            "remember that last message and nothing after it",
            "The turn is read-only",
            "Check live state before reporting",
            "one opening sentence",
            "under about 100 words",
            "finished, in progress, failed, or unverified",
            "decidable from the reply alone",
            "what it changes for users",
            "the evidence behind the pick",
            "its risk",
            "Never invent a call",
            "never shrink or drop items",
            "work you can still do yourself",
            "no commit hashes, paths, shell commands, build numbers, or counts of tests",
            "Korean when they write Korean",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract.lower(), " ".join(text.lower().split()))
        self.assertIn("\n**Reply:**", text)

    def test_skill_is_prose_only(self) -> None:
        self.assertFalse((SKILL / "scripts").exists())

    def test_interfaces_and_evals(self) -> None:
        command = (PACKAGE / "commands" / "ketchup.md").read_text(encoding="utf-8")
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        payload = json.loads((SKILL / "evals" / "evals.json").read_text(encoding="utf-8"))

        self.assertIn("Use the **ketchup** skill", command)
        self.assertNotIn("argument-hint", command)
        self.assertIn("$ketchup", openai)
        self.assertEqual("ketchup", payload["skill_name"])
        self.assertGreaterEqual(len(payload["evals"]), 3)
        for item in payload["evals"]:
            with self.subTest(eval=item["id"]):
                self.assertGreaterEqual(len(item["assertions"]), 2)
        assertions = " ".join(a for i in payload["evals"] for a in i["assertions"])
        self.assertIn("recall", assertions)

    def test_readmes_document_ketchup(self) -> None:
        for path in (PACKAGE / "README.md", PACKAGE / "README.ko.md"):
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(2, text.count("chann/skills --skill ketchup"))
                self.assertIn("/ketchup", text)
                self.assertIn("$ketchup", text)


if __name__ == "__main__":
    unittest.main()
