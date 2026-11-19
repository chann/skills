import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "swarm"
SKILL = PACKAGE / "skills" / "arena"


def normalized(path: Path) -> str:
    # Collapsed whitespace so a line wrap in the prose cannot break an assertion.
    return " ".join(path.read_text(encoding="utf-8").split())


class ArenaSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = (
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "arena.md",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
        )
        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file(), path)

    def test_interfaces_publish_both_selectors(self) -> None:
        frontmatter = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)[1]
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        command = (PACKAGE / "commands" / "arena.md").read_text(encoding="utf-8")
        self.assertIn("name: arena", frontmatter)
        self.assertNotIn("disable-model-invocation", frontmatter)
        self.assertIn("$arena", openai)
        self.assertIn("Use the **arena** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn('argument-hint: "<task>"', command)
        description = frontmatter.split("description: ", 1)[1].strip()
        self.assertTrue(description.startswith("Use when"))
        self.assertLessEqual(len(description), 1024)
        for trigger in (
            "/arena",
            "$arena",
            "arena this",
            "여러 안 만들어서 비교해줘",
            "후보 여러 개 경쟁시켜줘",
            "give me N attempts and pick the best",
            "swarm",
            "review-me",
        ):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, description)

    def test_skill_orders_the_six_phases(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        ordered = [
            "## When not to run",
            "## 1. Frame",
            "## 2. Fan out",
            "## 3. Cross-judge",
            "## 4. Pick a base",
            "## 5. Graft",
            "## 6. Verify",
            "## Refusals",
            "**Reply:**",
        ]
        positions = [text.find(heading) for heading in ordered]
        for heading, position in zip(ordered, positions, strict=True):
            with self.subTest(heading=heading):
                self.assertNotEqual(-1, position, heading)
        self.assertEqual(sorted(positions), positions)
        self.assertTrue(text.rstrip().splitlines()[-1].startswith("**Reply:**"))

    def test_skill_states_the_judging_contract(self) -> None:
        text = normalized(SKILL / "SKILL.md")
        for contract in (
            "three to six criteria",
            "hidden from candidates",
            "the prompt is the contract",
            "its own Git worktree",
            "the candidates share one vendor",
            "dropout",
            "read-only judge",
            "neutral labels",
            "the vendor check did not run",
            "Read every candidate end to end yourself",
            "prefer the smaller interface",
            "Reframe and rerun",
            "graft nothing",
            "`VERIFIED`",
            "`INCONCLUSIVE`",
            "Do not race a mechanical task",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_swarm_is_optional(self) -> None:
        text = normalized(SKILL / "SKILL.md")
        self.assertIn("When the `swarm` skill is installed", text)
        self.assertIn("Without it, use the host's subagent tool", text)

    def test_evals_cover_happy_refusal_and_sibling(self) -> None:
        data = json.loads((SKILL / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertEqual("arena", data["skill_name"])
        self.assertGreaterEqual(len(data["evals"]), 3)
        for item in data["evals"]:
            with self.subTest(eval=item["id"]):
                self.assertGreaterEqual(len(item["assertions"]), 2)
        joined = json.dumps(data, ensure_ascii=False)
        self.assertIn("Selects swarm instead of arena", joined)
        self.assertIn("mechanical", joined)

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
                self.assertIn('"arena"', path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
