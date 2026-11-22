import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "no-comments"
SKILL = PACKAGE / "skills" / "no-comments"

CURSOR_ONLY = (
    "update_state",
    "SendToUser",
    "api2.cursor.sh",
    "subagent_type: comment-sicko",
    "subagent_type: \"comment-sicko\"",
    "~/.cursor/rules",
    "Bugbot",
    "cursor-team-kit",
    "the Task tool",
    "pstack",
    "poteto",
    "backnotprop",
    "mattpocock",
    "cursor/plugins",
)

GATES = (
    "references/comment-review.md",
    "general-purpose",
    "spawn_agent",
    "no subagent tool",
    "A rejected review does not abort accepted findings.",
    "A comment about an outside rule that cannot be checked is kept and marked for review.",
    "does not edit application code",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def flat(text: str) -> str:
    return " ".join(text.split())


class NoCommentsSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = (
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
            PACKAGE / "commands" / "no-comments.md",
            SKILL / "SKILL.md",
            SKILL / "references" / "comment-review.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
        )
        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_plugin_metadata(self) -> None:
        metadata = json.loads(read(PACKAGE / ".claude-plugin" / "plugin.json"))
        self.assertEqual("no-comments", metadata["name"])
        self.assertEqual("0.1.0", metadata["version"])

    def test_interfaces_publish_both_selectors(self) -> None:
        front = read(SKILL / "SKILL.md").split("---\n", 2)[1]
        openai = read(SKILL / "agents" / "openai.yaml")
        command = read(PACKAGE / "commands" / "no-comments.md")
        self.assertIn("name: no-comments\n", front)
        self.assertIn("description: Use when", front)
        self.assertIn("/no-comments", front)
        self.assertIn("$no-comments", front)
        self.assertNotIn("disable-model-invocation", front)
        self.assertIn("$no-comments", openai)
        self.assertIn("Use the **no-comments** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn('argument-hint: "[files or diff]"', command)

    def test_skill_and_command_state_the_review_gates_without_cursor_calls(self) -> None:
        skill = flat(read(SKILL / "SKILL.md"))
        command = flat(read(PACKAGE / "commands" / "no-comments.md"))
        review = flat(read(SKILL / "references" / "comment-review.md"))
        for gate in GATES:
            with self.subTest(gate=gate):
                self.assertIn(gate, skill)
                self.assertIn(gate, command)
        self.assertIn("Do not edit application code.", review)
        self.assertIn("marked for review", review)
        shipped = "\n".join(
            path.read_text(encoding="utf-8")
            for path in PACKAGE.rglob("*")
            if path.is_file() and path.suffix in {".md", ".json", ".yaml", ".py"}
        )
        for token in CURSOR_ONLY:
            with self.subTest(token=token):
                self.assertNotIn(token, shipped)

    def test_evals_cover_the_gates(self) -> None:
        payload = json.loads(read(SKILL / "evals" / "evals.json"))
        evals = payload["evals"]
        self.assertEqual("no-comments", payload["skill_name"])
        self.assertGreaterEqual(len(evals), 3)
        for item in evals:
            with self.subTest(eval=item["id"]):
                self.assertGreaterEqual(len(item["assertions"]), 2)
        joined = json.dumps(evals, ensure_ascii=False)
        for gate in ("interrogate", "outside rule", "accepted findings"):
            with self.subTest(gate=gate):
                self.assertIn(gate, joined)

    def test_chann_routes_comment_cleanup_as_an_edit(self) -> None:
        text = read(ROOT / "chann-mode" / "skills" / "chann" / "SKILL.md")
        routing = text.split("## 2. Routing", 1)[1].split("## 3. Principles", 1)[0]
        self.assertIn("`no-comments`", routing)
        self.assertIn("| refactoring |", routing)
        review = routing.split("Review a change", 1)[1].split("\n", 1)[0]
        self.assertNotIn("no-comments", review)


if __name__ == "__main__":
    unittest.main()
