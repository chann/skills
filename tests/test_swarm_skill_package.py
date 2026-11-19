import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "swarm"
SKILL = PACKAGE / "skills" / "swarm"


def normalized(path: Path) -> str:
    # Collapsed whitespace so a line wrap in the prose cannot break an assertion.
    return " ".join(path.read_text(encoding="utf-8").split())


class SwarmSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = (
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "swarm.md",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
            SKILL / "scripts" / "swarm.py",
            SKILL / "assets" / "prompts" / "common.md",
            SKILL / "references" / "routes.md",
            SKILL / "references" / "selection.md",
            SKILL / "references" / "execution.md",
        )
        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file(), path)

    def test_plugin_metadata_names_the_run_record(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual("swarm", metadata["name"])
        self.assertEqual("1.0.0", metadata["version"])
        self.assertIn("call-tree", metadata["description"])

    def test_interfaces_publish_both_selectors(self) -> None:
        frontmatter = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)[1]
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        command = (PACKAGE / "commands" / "swarm.md").read_text(encoding="utf-8")
        self.assertIn("name: swarm", frontmatter)
        self.assertIn("$swarm", openai)
        self.assertIn("Use the **swarm** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn('argument-hint: "<task>"', command)
        description = frontmatter.split("description: ", 1)[1].strip()
        self.assertTrue(description.startswith("Use when"))
        self.assertLessEqual(len(description), 1024)
        for trigger in (
            "/swarm",
            "$swarm",
            "서브에이전트로 작업해줘",
            "병렬로 나눠서 돌려줘",
            "다른 모델로 한 번 더 확인해줘",
            "쿼터 나눠서 병렬로 돌려줘",
            "use subagents",
            "spawn subagents",
            "swarm this",
            "second opinion from another model",
        ):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, description)
        for sibling in ("arena", "long-task", "research-brief", "interrogate"):
            with self.subTest(sibling=sibling):
                self.assertIn(sibling, description)

    def test_skill_orders_the_four_phases(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        ordered = [
            "## 1. Frame",
            "## 2. Fan out",
            "## 3. Aggregate",
            "## 4. Report",
            "## Refusals",
            "**Reply:**",
        ]
        positions = [text.find(heading) for heading in ordered]
        for heading, position in zip(ordered, positions, strict=True):
            with self.subTest(heading=heading):
                self.assertNotEqual(-1, position, heading)
        self.assertEqual(sorted(positions), positions)
        self.assertTrue(text.rstrip().splitlines()[-1].startswith("**Reply:**"))

    def test_frame_declares_shape_and_race_rule(self) -> None:
        text = normalized(SKILL / "SKILL.md")
        for phrase in (
            "Done predicate",
            "`partition`",
            "`race`",
            "`first pass`",
            "`rank all`",
            "`best of`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_workers_answer_with_verdict_words(self) -> None:
        skill = normalized(SKILL / "SKILL.md")
        prompt = normalized(SKILL / "assets" / "prompts" / "common.md")
        for text in (skill, prompt):
            for word in ("`PASS`", "`ISSUES`", "`BLOCKED`"):
                with self.subTest(word=word):
                    self.assertIn(word, text)
            self.assertIn("not only the first", text)
        self.assertIn("A gap is never a pass", skill)
        self.assertIn("rerun once", skill)

    def test_skill_keeps_gates_and_stops_polling(self) -> None:
        text = normalized(SKILL / "SKILL.md")
        for phrase in (
            "heterogeneous: false",
            "long-task",
            "research-brief",
            "interrogate",
            "Do not poll",
            "unknown",
            "error_class: permission",
            "error_class: mutated",
            "write_set_ok: false",
            "--context-file",
            "--guard",
            "record-native",
            "At most four steps",
            "$XDG_CACHE_HOME/swarm/runs/<run-id>/",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_reference_keeps_the_command_lines(self) -> None:
        text = (SKILL / "references" / "execution.md").read_text(encoding="utf-8")
        for phrase in ("--keep-session", "--resume-task", "--only-significant", "scripts/swarm.py mark"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_evals_cover_happy_refusal_and_sibling(self) -> None:
        data = json.loads((SKILL / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertEqual("swarm", data["skill_name"])
        self.assertGreaterEqual(len(data["evals"]), 3)
        for item in data["evals"]:
            with self.subTest(eval=item["id"]):
                self.assertGreaterEqual(len(item["assertions"]), 2)
        joined = json.dumps(data, ensure_ascii=False)
        self.assertIn("long-task", joined)
        self.assertIn("arena", joined)

    def test_readmes_note_the_rename(self) -> None:
        notes = {
            "README.md": "was renamed `swarm` in 1.0.0",
            "README.ko.md": "이름이 `swarm`으로 바뀌었습니다",
        }
        for name, note in notes.items():
            with self.subTest(readme=name):
                text = (PACKAGE / name).read_text(encoding="utf-8")
                self.assertIn(note, text)
                self.assertIn("arena", text)

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
                text = path.read_text(encoding="utf-8")
                self.assertIn('"swarm"', text)
        triggers = {
            "ko": "서브에이전트",
            "en": "subagents",
            "jp": "サブエージェント",
            "cn": "子代理",
        }
        for locale, trigger in triggers.items():
            path = ROOT / "website" / "src" / "i18n" / "content" / f"{locale}.json"
            with self.subTest(locale=locale):
                self.assertIn(trigger, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
