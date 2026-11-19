import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "interrogate"
SKILL = PACKAGE / "skills" / "blast-radius"
COMMAND = PACKAGE / "commands" / "blast-radius.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class BlastRadiusSkillPackageTests(unittest.TestCase):
    def test_skill_shape_is_complete(self) -> None:
        for path in (
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
            COMMAND,
            PACKAGE / ".claude-plugin" / "plugin.json",
        ):
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_interfaces_publish_both_selectors(self) -> None:
        frontmatter = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)[1]
        description = re.search(r"(?m)^description: (.*)$", frontmatter).group(1)
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        command = COMMAND.read_text(encoding="utf-8")

        self.assertIn("name: blast-radius", frontmatter)
        self.assertNotIn("disable-model-invocation", frontmatter)
        self.assertTrue(description.startswith("Use when"))
        self.assertLessEqual(len(description), 1024)
        for trigger in (
            "이거 바꾸면 뭐가 깨져?",
            "영향 범위 확인해줘",
            "blast radius of this change",
            "what could this break",
            "/blast-radius",
            "$blast-radius",
            "interrogate",
        ):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, description)
        self.assertIn("$blast-radius", openai)
        short = re.search(r'short_description: "(.*)"', openai).group(1)
        self.assertLessEqual(len(short), 90)
        self.assertFalse(short.endswith("."))
        self.assertIn("Use the **blast-radius** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn('argument-hint: "[scope]"', command)
        self.assertIn("/interrogate", command)

    def test_skill_orders_the_workflow(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        ordered = [
            "## Proof ladder",
            "## 1. Read the change",
            "## 2. Find the safety fact",
            "## 3. Look where a symbol search stops",
            "## 4. Prove the facts",
            "## 5. Weigh the risks",
            "## Refusals",
            "**Reply:**",
        ]
        positions = [text.find(heading) for heading in ordered]
        for heading, position in zip(ordered, positions):
            with self.subTest(heading=heading):
                self.assertNotEqual(-1, position)
        self.assertEqual(sorted(positions), positions)

    def test_proof_ladder_is_ordered(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        rows = [text.find(f"| `{level}` |") for level in
                ("said", "cited", "traced", "ran", "reproduced")]
        for row in rows:
            self.assertNotEqual(-1, row)
        self.assertEqual(sorted(rows), rows)

    def test_skill_looks_past_a_symbol_search(self) -> None:
        text = normalized(SKILL / "SKILL.md")
        for place in (
            "**Pinned dependencies.**",
            "**Timing and teardown.**",
            "**Serialized shapes.**",
            "**Switches.**",
            "**Distance.**",
            "another language or service reading the same bytes",
        ):
            with self.subTest(place=place):
                self.assertIn(place, text)

    def test_skill_states_read_only_and_honesty_gates(self) -> None:
        text = normalized(SKILL / "SKILL.md")
        for contract in (
            "a temporary directory outside the repository",
            "The repository stays read-only",
            "no repository content sent to the network",
            "`git status --porcelain` before and after",
            '"Searched, found nothing" is a valid result',
            "Never invent a caller, a consumer, or an API.",
            "Do not fix anything.",
            "Do not call a fact proven when its script was written but not run.",
            '"unproven"',
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_reply_contract_names_every_section(self) -> None:
        last_line = (SKILL / "SKILL.md").read_text(encoding="utf-8").rstrip().splitlines()[-1]
        self.assertTrue(last_line.startswith("**Reply:**"))
        for item in ("what the change does", "safety fact", "proof level",
                     "unproven", "risks", "`file:line`", "cleared",
                     "cheapest check"):
            with self.subTest(item=item):
                self.assertIn(item, last_line)

    def test_evals_cover_happy_path_refusal_and_sibling(self) -> None:
        data = json.loads((SKILL / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertEqual("blast-radius", data["skill_name"])
        self.assertGreaterEqual(len(data["evals"]), 3)
        for item in data["evals"]:
            with self.subTest(eval_id=item["id"]):
                self.assertGreaterEqual(len(item["assertions"]), 2)
        text = json.dumps(data, ensure_ascii=False)
        self.assertIn("interrogate", text)
        self.assertIn("No caller, consumer, or API is invented.", text)
        self.assertIn("nothing is installed into it", text)


if __name__ == "__main__":
    unittest.main()
