import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "build-reinstall"
SKILL = PACKAGE / "skills" / "build-reinstall"


class BuildReinstallSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = (
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "build-reinstall.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "references" / "build-reinstall.example.yaml",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
        )

        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_interfaces_publish_both_explicit_selectors(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        command = (PACKAGE / "commands" / "build-reinstall.md").read_text(
            encoding="utf-8"
        )
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = skill.split("---\n", 2)[1]
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertEqual("build-reinstall", metadata["name"])
        self.assertEqual("0.1.0", metadata["version"])
        self.assertIn('argument-hint: "[project-root]"', command)
        self.assertIn("Use the **build-reinstall** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn("/build-reinstall", frontmatter)
        self.assertIn("$build-reinstall", frontmatter)
        self.assertIn("$build-reinstall", openai)

    def test_skill_orders_build_reinstall_and_installed_proof(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        ordered = [
            "## 1. Preflight",
            "## 2. Build",
            "## 3. Resolve the build output",
            "## 4. Reinstall",
            "## 5. Verify the installed result",
            "## 6. Report",
        ]

        positions = [text.index(heading) for heading in ordered]
        self.assertEqual(positions, sorted(positions))
        for value in (
            "SHA-256",
            "smoke",
            "installed",
            "build failure",
            ".build-reinstall.yaml",
            "references/build-reinstall.example.yaml",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_skill_refuses_unproven_or_privileged_installation(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        for value in (
            "sudo",
            "force flags",
            "broad recursive deletion",
            "ambiguous",
            "installed copy untouched",
            "artifact mismatch",
            "notarization",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_example_yaml_defines_version_one_and_explicit_targets(self) -> None:
        text = (
            SKILL / "references" / "build-reinstall.example.yaml"
        ).read_text(encoding="utf-8")

        for value in (
            "version: 1",
            'working_directory: "."',
            "build:",
            "reinstall:",
            "targets:",
            "verify:",
            "artifacts:",
            'compare: "sha256"',
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_readmes_document_exact_installs_and_selectors(self) -> None:
        for path in (PACKAGE / "README.md", PACKAGE / "README.ko.md"):
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(2, text.count("chann/skills --skill build-reinstall"))
                self.assertIn("/build-reinstall", text)
                self.assertIn("$build-reinstall", text)
                self.assertIn(".build-reinstall.yaml", text)
                self.assertIn("build-reinstall.example.yaml", text)

    def test_exact_selector_installs_for_codex_and_claude_code(self) -> None:
        environment = os.environ.copy()
        environment.update({"NO_COLOR": "1", "FORCE_COLOR": "0"})

        with tempfile.TemporaryDirectory() as target:
            install_roots = {
                "codex": Path(".agents/skills/build-reinstall"),
                "claude-code": Path(".claude/skills/build-reinstall"),
            }

            for agent, relative_install_root in install_roots.items():
                with self.subTest(agent=agent):
                    project = Path(target) / agent
                    project.mkdir()
                    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
                    result = subprocess.run(
                        [
                            "npx",
                            "--yes",
                            "skills",
                            "add",
                            str(PACKAGE),
                            "--skill",
                            "build-reinstall",
                            "--agent",
                            agent,
                            "--copy",
                            "--yes",
                            "--full-depth",
                        ],
                        cwd=project,
                        env=environment,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        timeout=60,
                        check=False,
                    )

                    self.assertEqual(result.returncode, 0, result.stdout)
                    installed = project / relative_install_root
                    self.assertEqual(
                        (SKILL / "SKILL.md").read_bytes(),
                        (installed / "SKILL.md").read_bytes(),
                    )
                    self.assertEqual(
                        (SKILL / "agents" / "openai.yaml").read_bytes(),
                        (installed / "agents" / "openai.yaml").read_bytes(),
                    )
                    self.assertEqual(
                        (
                            SKILL
                            / "references"
                            / "build-reinstall.example.yaml"
                        ).read_bytes(),
                        (
                            installed
                            / "references"
                            / "build-reinstall.example.yaml"
                        ).read_bytes(),
                    )


if __name__ == "__main__":
    unittest.main()
