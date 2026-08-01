import json
import os
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "review-me"
SKILL = PACKAGE / "skills" / "review-me"


class ReviewMeSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = [
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "review-me.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
            SKILL / "references" / "review-lenses.md",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
        ]

        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_plugin_metadata_and_interfaces_publish_review_me(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        command = (PACKAGE / "commands" / "review-me.md").read_text(
            encoding="utf-8"
        )
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertEqual("review-me", metadata["name"])
        self.assertEqual("0.1.0", metadata["version"])
        self.assertIn("leaf", metadata["description"].lower())
        self.assertIn('argument-hint: "[topic]"', command)
        self.assertIn("Use the **review-me** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn("$review-me", openai)

    def test_skill_is_explicit_and_self_contained(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---\n", 2)[1]

        self.assertIn("name: review-me", frontmatter)
        self.assertIn("disable-model-invocation: true", frontmatter)
        self.assertIn("/review-me", frontmatter)
        self.assertIn("$review-me", frontmatter)
        self.assertNotIn("Run a `/grilling` session", text)
        self.assertIn("references/review-lenses.md", text)

    def test_skill_enforces_recursive_one_question_traversal(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        for contract in (
            "Keep exactly one decision question active",
            "Give a specific recommended answer",
            "Because this is now true, what else must be decided?",
            "Reopen descendants whose assumptions changed",
            "dependency first, then by blast radius",
            "newly implied",
            "children have been added before another branch",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_skill_requires_leaf_level_completion(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        for contract in (
            "all five closure tests pass",
            "**Choice**",
            "**Boundary**",
            "**Variants**",
            "**Consequences**",
            "**Proof**",
            "one concrete boundary example and one hostile",
            "owner, decision",
            "trigger, safe interim default",
            "every applicable lens is accounted for",
            "user confirms the closure record",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_review_lenses_cover_cross_cutting_decisions(self) -> None:
        lenses = (SKILL / "references" / "review-lenses.md").read_text(
            encoding="utf-8"
        )

        for heading in (
            "Intent and success",
            "People and authority",
            "Scope and boundaries",
            "Behavior and states",
            "Proof",
            "Data and identity",
            "Dependencies and contracts",
            "Concurrency and repetition",
            "Security, privacy, and abuse",
            "Human interface",
            "Capacity and operations",
            "Evolution",
            "Leaf-splitting signals",
        ):
            with self.subTest(heading=heading):
                level = "##" if heading == "Leaf-splitting signals" else "###"
                self.assertIn(f"{level} {heading}", lenses)

    def test_evals_cover_leaf_completion_failure_modes(self) -> None:
        payload = json.loads(
            (SKILL / "evals" / "evals.json").read_text(encoding="utf-8")
        )

        self.assertEqual("review-me", payload["skill_name"])
        self.assertEqual([1, 2, 3, 4], [item["id"] for item in payload["evals"]])
        prompts = " ".join(item["prompt"] for item in payload["evals"])
        assertions = " ".join(
            assertion
            for item in payload["evals"]
            for assertion in item["assertions"]
        )
        self.assertIn("fast, simple", prompts)
        self.assertIn("change the rollout", prompts)
        self.assertIn("Repository facts", assertions)
        self.assertIn("reopens every descendant", assertions)
        self.assertIn("Final completion requires", assertions)

    def test_readmes_document_installation_and_inspiration(self) -> None:
        for path in (PACKAGE / "README.md", PACKAGE / "README.ko.md"):
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(2, text.count("chann/skills --skill review-me"))
                self.assertIn("/review-me", text)
                self.assertIn("$review-me", text)
                self.assertIn("mattpocock/skills", text)

    def test_skills_cli_discovers_review_me(self) -> None:
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
        self.assertRegex(result.stdout, re.compile(r"(?m)^[^A-Za-z0-9]*review-me\s*$"))


if __name__ == "__main__":
    unittest.main()
