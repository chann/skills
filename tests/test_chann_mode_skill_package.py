import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "chann-mode"
SKILL = PACKAGE / "skills" / "chann"
PLAYBOOKS = SKILL / "playbooks"


def skill_text() -> str:
    return (SKILL / "SKILL.md").read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    """Return the body of the `## ...` section whose title contains `heading`."""
    match = re.search(rf"^## [^\n]*{re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if match is None:
        raise AssertionError(f"SKILL.md has no section titled {heading!r}")
    return match.group(1)


def bold_bullets(text: str) -> list[str]:
    return re.findall(r"^- \*\*([a-z][a-z-]*)\*\*:", text, re.M)


def routing_rows() -> list[tuple[list[str], str]]:
    rows = []
    for line in section(skill_text(), "Routing").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(cells) != 3 or cells[0] in {"Situation", "---"}:
            continue
        rows.append((re.findall(r"`([a-z][a-z-]*)`", cells[1]), cells[2]))
    return rows


def frontmatter_description(path: Path) -> str:
    match = re.search(r"^description: (.*)$", path.read_text(encoding="utf-8"), re.M)
    return match.group(1) if match else ""


class ChannModeSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = (
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "chann.md",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
            SKILL / "SKILL.md",
            SKILL / "worker.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
            SKILL / "references" / "principles.md",
            SKILL / "references" / "decision-trail.md",
        )
        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_plugin_metadata_names_the_plugin(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual("chann-mode", metadata["name"])
        self.assertEqual("0.2.0", metadata["version"])
        self.assertIn("playbooks", metadata["description"])

    def test_skill_is_explicit_only_on_both_selectors(self) -> None:
        frontmatter = skill_text().split("---\n", 2)[1]
        description = frontmatter_description(SKILL / "SKILL.md")
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        command = (PACKAGE / "commands" / "chann.md").read_text(encoding="utf-8")

        self.assertIn("name: chann\n", frontmatter)
        self.assertTrue(description.startswith("Use only when"))
        self.assertIn("disable-model-invocation: true", frontmatter)
        self.assertIn("/chann ", description)
        self.assertIn("$chann ", description)
        self.assertIn("$chann ", openai)
        self.assertIn("Use the **chann** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn('argument-hint: "<task>"', command)

    def test_every_playbook_is_listed_and_every_listed_playbook_exists(self) -> None:
        listed = set(bold_bullets(section(skill_text(), "Playbooks")))
        on_disk = {path.stem for path in PLAYBOOKS.glob("*.md")}
        self.assertEqual(14, len(on_disk))
        self.assertEqual(on_disk, listed)

    def test_routing_table_points_at_real_playbooks_and_covers_all_of_them(self) -> None:
        routed = {playbook for _, playbook in routing_rows()}
        on_disk = {path.stem for path in PLAYBOOKS.glob("*.md")}
        self.assertTrue(routed <= on_disk, sorted(routed - on_disk))
        self.assertEqual(on_disk, routed)

    def test_every_playbook_states_ownership_steps_and_a_reply_contract(self) -> None:
        for path in sorted(PLAYBOOKS.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            lines = [line for line in text.strip().splitlines() if line.strip()]
            steps = re.findall(r"^\d+\. ", text, re.M)
            with self.subTest(playbook=path.stem):
                self.assertTrue(lines[0].startswith("# "))
                self.assertRegex(text, r"(?m)^\*\*You own ")
                self.assertGreaterEqual(len(steps), 4)
                self.assertLessEqual(len(steps), 8)
                self.assertTrue(lines[-1].startswith("**Reply:**"))

    def test_skill_ends_with_a_reply_contract(self) -> None:
        last = skill_text().strip().splitlines()[-1]
        self.assertTrue(last.startswith("**Reply:**"))

    def test_principles_index_matches_the_principles_reference(self) -> None:
        indexed = bold_bullets(section(skill_text(), "Principles"))
        reference = (SKILL / "references" / "principles.md").read_text(encoding="utf-8")
        documented = re.findall(r"^### ([a-z][a-z-]*)$", reference, re.M)

        self.assertEqual(len(indexed), len(set(indexed)))
        self.assertEqual(set(indexed), set(documented))
        for name in documented:
            body = reference.split(f"### {name}\n", 1)[1].split("\n### ", 1)[0]
            with self.subTest(principle=name):
                self.assertIn("**Apply when:**", body)
                self.assertIn("**Test:**", body)

    def test_catalog_owned_principles_are_present(self) -> None:
        indexed = set(bold_bullets(section(skill_text(), "Principles")))
        for name in ("proven-vs-unproven", "report-is-not-evidence", "leave-a-record"):
            with self.subTest(principle=name):
                self.assertIn(name, indexed)

    def test_every_kickoff_points_at_worker_rules(self) -> None:
        worker = (SKILL / "worker.md").read_text(encoding="utf-8")
        self.assertIn("`Before anything else, read <absolute path>/worker.md.`", skill_text())
        for rule in ("operator", "complete bar", "force-push", "Never push", "INCONCLUSIVE"):
            with self.subTest(rule=rule):
                self.assertIn(rule, worker)

    def test_decision_trail_fixes_its_columns(self) -> None:
        text = (SKILL / "references" / "decision-trail.md").read_text(encoding="utf-8")
        self.assertIn("ts\tphase\tdecision\twhy\tevidence\tresult", text)
        self.assertIn("Append-only", text)
        self.assertIn("supersedes", text)

    def test_skill_bodies_stay_portable(self) -> None:
        # Host tool names and model ids would tie the router to one agent platform.
        forbidden = re.compile(
            r"\b(?:claude-|opus|sonnet|haiku|fable|gpt-|gemini|TodoWrite|AskUserQuestion"
            r"|spawn_agent|subagent_type|run_in_background)",
            re.IGNORECASE,
        )
        body = skill_text().split("---\n", 2)[2]
        files = {"SKILL.md": body}
        for path in SKILL.rglob("*.md"):
            if path.name != "SKILL.md":
                files[path.relative_to(SKILL).as_posix()] = path.read_text(encoding="utf-8")
        for name, text in files.items():
            with self.subTest(file=name):
                self.assertIsNone(forbidden.search(text))

    def test_evals_cover_the_routing_gates(self) -> None:
        payload = json.loads((SKILL / "evals" / "evals.json").read_text(encoding="utf-8"))
        evals = payload["evals"]
        self.assertEqual("chann", payload["skill_name"])
        self.assertGreaterEqual(len(evals), 5)
        for item in evals:
            with self.subTest(eval=item["id"]):
                self.assertGreaterEqual(len(item["assertions"]), 2)
        joined = json.dumps(evals, ensure_ascii=False)
        for gate in ("bug-hunt", "interrogate", "worker.md", "worktree", "blocked"):
            with self.subTest(gate=gate):
                self.assertIn(gate, joined)

    def test_every_routed_skill_is_packaged(self) -> None:
        # Fails until the sibling revamp branches that add these skills are merged.
        packaged = {path.parent.name for path in ROOT.glob("*/skills/*/SKILL.md")}
        routed = {name for names, _ in routing_rows() for name in names}
        self.assertEqual(26, len(routed))
        self.assertEqual(set(), routed - packaged)

    def test_every_packaged_workflow_is_routed(self) -> None:
        # A new catalog skill must be reachable from the router. Selector aliases
        # describe themselves as aliases and are reached through their canonical skill.
        routed = {name for names, _ in routing_rows() for name in names}
        workflows = {
            path.parent.name
            for path in ROOT.glob("*/skills/*/SKILL.md")
            if path.parent.name != "chann"
            and "alias" not in frontmatter_description(path).lower()
        }
        self.assertEqual(set(), workflows - routed)


if __name__ == "__main__":
    unittest.main()
