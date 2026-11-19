import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SELECTORS = {
    "gen-docs": (
        ROOT / "doc-skill",
        [ROOT / "doc-skill" / "skills" / "gen-docs" / "SKILL.md"],
    ),
    "handoff": (
        ROOT / "handoff",
        [ROOT / "handoff" / "skills" / "handoff" / "SKILL.md"],
    ),
    "plan-summary": (
        ROOT / "plan-summary",
        [ROOT / "plan-summary" / "skills" / "plan-summary" / "SKILL.md"],
    ),
    "recall": (
        ROOT / "recall",
        [ROOT / "recall" / "skills" / "recall" / "SKILL.md"],
    ),
}


class OptionalUnslopContractTests(unittest.TestCase):
    def test_every_document_generator_has_a_self_contained_optional_pass(self) -> None:
        required = (
            "plain, concrete Korean prose",
            "unslop",
            "optional",
            "do not install",
            "continue",
            "normal validation",
        )

        for selector, (_, sources) in SELECTORS.items():
            text = "\n".join(path.read_text(encoding="utf-8") for path in sources)
            normalized = " ".join(text.lower().split())
            with self.subTest(selector=selector):
                for phrase in required:
                    self.assertIn(phrase.lower(), normalized)
                self.assertNotIn("REQUIRED SUB-SKILL: unslop", text)

    def test_plugin_manifests_do_not_declare_writing_dependencies(self) -> None:
        for selector, (plugin, _) in SELECTORS.items():
            metadata = json.loads(
                (plugin / ".claude-plugin" / "plugin.json").read_text(
                    encoding="utf-8"
                )
            )
            with self.subTest(selector=selector):
                self.assertNotIn("dependencies", metadata)
                self.assertNotIn("unslop", json.dumps(metadata))

    def test_each_selector_installs_without_unslop(self) -> None:
        environment = os.environ.copy()
        environment.update({"NO_COLOR": "1", "FORCE_COLOR": "0"})

        for selector, (plugin, _) in SELECTORS.items():
            with self.subTest(selector=selector), tempfile.TemporaryDirectory() as target:
                subprocess.run(["git", "init", "-q"], cwd=target, check=True)
                result = subprocess.run(
                    [
                        "npx",
                        "--yes",
                        "skills",
                        "add",
                        str(plugin),
                        "--skill",
                        selector,
                        "--agent",
                        "codex",
                        "--copy",
                        "--yes",
                        "--full-depth",
                    ],
                    cwd=target,
                    env=environment,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=60,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout)
                installed = Path(target) / ".agents" / "skills"
                self.assertTrue((installed / selector / "SKILL.md").is_file())
                self.assertFalse((installed / "unslop").exists())


if __name__ == "__main__":
    unittest.main()
