import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "understand"
SKILLS = ("how", "why")


def skill_text(name: str) -> str:
    return " ".join((PACKAGE / "skills" / name / "SKILL.md").read_text(encoding="utf-8").split())


def frontmatter(name: str) -> str:
    return (PACKAGE / "skills" / name / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)[1]


class UnderstandSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = [
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
        ]
        for name in SKILLS:
            expected += [
                PACKAGE / "commands" / f"{name}.md",
                PACKAGE / "skills" / name / "SKILL.md",
                PACKAGE / "skills" / name / "agents" / "openai.yaml",
                PACKAGE / "skills" / name / "evals" / "evals.json",
            ]

        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_plugin_metadata_is_new_and_names_both_questions(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

        self.assertEqual("understand", metadata["name"])
        self.assertEqual("0.1.0", metadata["version"])
        self.assertIn("file:line", metadata["description"])

    def test_interfaces_publish_both_selectors(self) -> None:
        for name in SKILLS:
            with self.subTest(skill=name):
                front = frontmatter(name)
                openai = (PACKAGE / "skills" / name / "agents" / "openai.yaml").read_text(
                    encoding="utf-8"
                )
                command = (PACKAGE / "commands" / f"{name}.md").read_text(encoding="utf-8")

                self.assertIn(f"name: {name}\n", front)
                self.assertIn("description: Use when", front)
                self.assertIn(f"/{name}", front)
                self.assertIn(f"${name}", front)
                self.assertNotIn("disable-model-invocation", front)
                self.assertIn(f"${name}", openai)
                self.assertIn(f"Use the **{name}** skill", command)
                self.assertIn("$ARGUMENTS", command)
                self.assertIn('argument-hint: "<question>"', command)

    def test_both_skills_are_read_only(self) -> None:
        for name in SKILLS:
            with self.subTest(skill=name):
                text = skill_text(name)
                self.assertIn("## Refusals", text)
                self.assertIn("Do not edit files", text)
                self.assertIn("read-only", text)

    def test_how_cites_every_claim_and_labels_what_it_did_not_read(self) -> None:
        text = skill_text("how")
        for contract in (
            "Every claim about the code carries `file:line`",
            "labelled `inferred`",
            "Say what you did not read",
            "ends with a recommendation and the reason",
            "one read-only explorer",
            "state the question as you understand it",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract.lower(), text.lower())

    def test_how_answer_shape_is_fixed_and_ordered(self) -> None:
        text = (PACKAGE / "skills" / "how" / "SKILL.md").read_text(encoding="utf-8")
        ordered = [
            "**Overview**",
            "**Key concepts**",
            "**Runtime flow**",
            "**Code map**",
            "**Gotchas**",
        ]
        positions = [text.find(heading) for heading in ordered]
        for heading, position in zip(ordered, positions):
            with self.subTest(heading=heading):
                self.assertNotEqual(-1, position)
        self.assertEqual(sorted(positions), positions)

    def test_why_reads_the_record_and_quotes_the_authors(self) -> None:
        text = skill_text("why")
        for contract in (
            "git log -S",
            "git log --follow",
            "git blame -w -C",
            "`gh`",
            "Quote what the authors wrote",
            "marked `inferred`",
            "Never present a guess from the code's shape as the reason",
            "What the record does not answer",
            "or post comments",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_why_timeline_has_introduced_changed_current(self) -> None:
        text = (PACKAGE / "skills" / "why" / "SKILL.md").read_text(encoding="utf-8")
        for stage in ("| introduced |", "| changed |", "| current |"):
            with self.subTest(stage=stage):
                self.assertIn(stage, text)
        self.assertIn("(`high`, `medium`, `low`)", text)

    def test_siblings_are_named_for_disambiguation(self) -> None:
        how = frontmatter("how")
        why = frontmatter("why")
        for sibling in ("why", "research-brief", "diff-summary", "bug-hunt"):
            with self.subTest(skill="how", sibling=sibling):
                self.assertIn(sibling, how)
        for sibling in ("how", "research-brief", "recall"):
            with self.subTest(skill="why", sibling=sibling):
                self.assertIn(sibling, why)

    def test_reply_contracts_close_each_skill(self) -> None:
        how = skill_text("how")
        why = skill_text("why")
        self.assertTrue(how.rstrip().split("**Reply:**")[-1].strip().startswith("the five sections"))
        self.assertIn("what was not read", how.split("**Reply:**")[-1])
        self.assertIn("the short answer with its confidence", why.split("**Reply:**")[-1])
        self.assertIn("what the record does not answer", why.split("**Reply:**")[-1])

    def test_evals_cover_happy_path_boundary_and_sibling(self) -> None:
        for name in SKILLS:
            payload = json.loads(
                (PACKAGE / "skills" / name / "evals" / "evals.json").read_text(encoding="utf-8")
            )
            with self.subTest(skill=name):
                self.assertEqual(name, payload["skill_name"])
                self.assertGreaterEqual(len(payload["evals"]), 3)
                for entry in payload["evals"]:
                    self.assertGreaterEqual(len(entry["assertions"]), 2)

    def test_openai_short_descriptions_fit(self) -> None:
        for name in SKILLS:
            text = (PACKAGE / "skills" / name / "agents" / "openai.yaml").read_text(encoding="utf-8")
            line = next(l for l in text.splitlines() if "short_description" in l)
            value = line.split(":", 1)[1].strip().strip('"')
            with self.subTest(skill=name):
                self.assertLessEqual(len(value), 90)
                self.assertFalse(value.endswith("."))


if __name__ == "__main__":
    unittest.main()
