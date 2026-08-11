import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GIT_SKILL = ROOT / "git-skill"
REALTIME_SKILL_NAME = "git-commit-push-realtime"
REALTIME_SKILL = GIT_SKILL / "skills" / REALTIME_SKILL_NAME
REALTIME_ALIAS = "gcpr"
CODEX_REALTIME_ALIAS_SKILL = GIT_SKILL / "skills" / REALTIME_ALIAS
LOCAL_REALTIME_SKILL_NAME = "git-commit-realtime"
LOCAL_REALTIME_SKILL = GIT_SKILL / "skills" / LOCAL_REALTIME_SKILL_NAME
LOCAL_REALTIME_ALIAS = "gcr"

PROTECTED_BRANCH_LIST = (
    "`main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`"
)


def frontmatter(path: Path) -> str:
    """Return the YAML frontmatter block of a Markdown file."""
    text = path.read_text(encoding="utf-8")
    return text.split("---\n", 2)[1] if text.startswith("---\n") else ""


def body(path: Path) -> str:
    """Return a Markdown file's content with its YAML frontmatter removed."""
    text = path.read_text(encoding="utf-8")
    return text.split("---\n", 2)[2] if text.startswith("---\n") else text


def quoted_yaml_field(path: Path, key: str) -> str:
    """Return one quoted field from an agents/openai.yaml interface."""
    match = re.search(
        rf'^\s+{re.escape(key)}:\s+"([^"]+)"$',
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if match is None:
        raise AssertionError(f"{path.relative_to(ROOT)} is missing {key}")
    return match.group(1)


class GitSkillPackageTests(unittest.TestCase):
    def test_realtime_commit_push_skill_is_packaged_with_command(self) -> None:
        skill = REALTIME_SKILL / "SKILL.md"
        command = GIT_SKILL / "commands" / f"{REALTIME_SKILL_NAME}.md"

        self.assertTrue(skill.is_file())
        self.assertTrue(command.is_file())

        skill_text = skill.read_text(encoding="utf-8")
        command_text = command.read_text(encoding="utf-8")
        self.assertIn(f"name: {REALTIME_SKILL_NAME}", skill_text)
        self.assertIn("<plugin-root>/skills/git-commit/SKILL.md", skill_text)
        self.assertIn("<plugin-root>/skills/git-commit-push/SKILL.md", skill_text)
        self.assertIn(f"**{REALTIME_SKILL_NAME}** skill", command_text)

    def test_realtime_commit_push_publishes_a_short_alias_command(self) -> None:
        alias = GIT_SKILL / "commands" / f"{REALTIME_ALIAS}.md"

        self.assertTrue(alias.is_file())

        alias_text = alias.read_text(encoding="utf-8")
        self.assertIn(f"**{REALTIME_SKILL_NAME}** skill", alias_text)
        self.assertIn(f"Alias for `/{REALTIME_SKILL_NAME}`", frontmatter(alias))

    def test_short_alias_command_body_matches_the_canonical_command(self) -> None:
        canonical = GIT_SKILL / "commands" / f"{REALTIME_SKILL_NAME}.md"
        alias = GIT_SKILL / "commands" / f"{REALTIME_ALIAS}.md"

        self.assertEqual(body(canonical), body(alias))

    def test_short_alias_is_discoverable_from_the_skill_description(self) -> None:
        description = frontmatter(REALTIME_SKILL / "SKILL.md")

        for token in (f'"/{REALTIME_ALIAS}"', f'"${REALTIME_ALIAS}"'):
            with self.subTest(token=token):
                self.assertIn(token, description)

    def test_codex_realtime_alias_is_a_thin_skill_package(self) -> None:
        skill = CODEX_REALTIME_ALIAS_SKILL / "SKILL.md"
        interface = CODEX_REALTIME_ALIAS_SKILL / "agents" / "openai.yaml"

        self.assertTrue(skill.is_file())
        self.assertTrue(interface.is_file())
        self.assertIn(f"name: {REALTIME_ALIAS}", frontmatter(skill))
        self.assertIn(f"${REALTIME_ALIAS}", frontmatter(skill))

        skill_text = skill.read_text(encoding="utf-8")
        self.assertIn(REALTIME_SKILL_NAME, skill_text)
        self.assertNotIn("git push", body(skill))
        self.assertIn(
            f"${REALTIME_ALIAS}",
            interface.read_text(encoding="utf-8"),
        )

    def test_codex_realtime_alias_keeps_its_short_display_name(self) -> None:
        alias_interface = CODEX_REALTIME_ALIAS_SKILL / "agents" / "openai.yaml"
        canonical_interface = REALTIME_SKILL / "agents" / "openai.yaml"
        website_source = (
            ROOT / "website" / "src" / "data" / "skills.ts"
        ).read_text(encoding="utf-8")
        title_match = re.search(
            rf'id: "{REALTIME_SKILL_NAME}",\s+title: "([^"]+)"',
            website_source,
        )

        self.assertIsNotNone(title_match)
        canonical_name = quoted_yaml_field(canonical_interface, "display_name")
        alias_name = quoted_yaml_field(alias_interface, "display_name")
        self.assertEqual("GCPR", alias_name)
        self.assertEqual("Git Commit and Push Realtime", canonical_name)
        self.assertNotEqual(alias_name, canonical_name)
        self.assertEqual(
            canonical_name,
            title_match.group(1) if title_match else "",
        )

    def test_short_alias_is_documented_across_package_surfaces(self) -> None:
        documented = [
            ROOT / "README.md",
            ROOT / "README.ko.md",
            ROOT / "USAGE.md",
            ROOT / "ARCHITECTURE.md",
            GIT_SKILL / "README.md",
            GIT_SKILL / "README.ko.md",
        ]

        for path in documented:
            for selector in (f"`/{REALTIME_ALIAS}`", f"`${REALTIME_ALIAS}`"):
                with self.subTest(path=path, selector=selector):
                    self.assertIn(selector, path.read_text(encoding="utf-8"))

    def test_realtime_commit_push_uses_green_outcome_checkpoints(self) -> None:
        skill = (REALTIME_SKILL / "SKILL.md").read_text(encoding="utf-8")

        for contract in (
            "Do not split work by file count, elapsed time, token pressure",
            "leaves the repository in a usable state",
            "Do not create `WIP`, `tmp`, or generic checkpoint commits",
            "Run the narrowest relevant tests and repository-required checks",
            "git diff --check",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, skill)

    def test_realtime_commit_push_pushes_each_checkpoint_and_stops_on_drift(self) -> None:
        skill = (REALTIME_SKILL / "SKILL.md").read_text(encoding="utf-8")

        for contract in (
            "After each checkpoint commit succeeds, push it before starting the next unit",
            'git push -u origin "$(git branch --show-current)"',
            "git rev-list --left-right --count HEAD...@{u}",
            "do not retry through `pull`, merge, rebase, `--force`, or",
            "Never begin the next checkpoint until the previous push and upstream parity",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, skill)

    def test_realtime_commit_push_evals_cover_checkpoint_safety(self) -> None:
        eval_path = REALTIME_SKILL / "evals" / "evals.json"
        payload = json.loads(eval_path.read_text(encoding="utf-8"))

        self.assertEqual(REALTIME_SKILL_NAME, payload["skill_name"])
        self.assertEqual([1, 2, 3], [item["id"] for item in payload["evals"]])
        prompts = " ".join(item["prompt"] for item in payload["evals"])
        self.assertIn("will not compile", prompts)
        self.assertIn("remote advances", prompts)

    def test_realtime_commit_push_is_documented_across_package_surfaces(self) -> None:
        package_readmes = [
            GIT_SKILL / "README.md",
            GIT_SKILL / "README.ko.md",
        ]
        command_docs = [
            ROOT / "README.md",
            ROOT / "README.ko.md",
            ROOT / "USAGE.md",
            ROOT / "ARCHITECTURE.md",
        ]

        for path in package_readmes:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(3, text.count(f"--skill {REALTIME_SKILL_NAME}"))
                self.assertEqual(3, text.count(f"--skill {REALTIME_ALIAS}"))
                self.assertIn(f"/{REALTIME_SKILL_NAME}", text)
                self.assertIn(f"${REALTIME_SKILL_NAME}", text)

        for path in command_docs:
            with self.subTest(path=path):
                self.assertIn(
                    REALTIME_SKILL_NAME,
                    path.read_text(encoding="utf-8"),
                )

    def test_local_realtime_commit_skill_is_packaged_with_command(self) -> None:
        skill = LOCAL_REALTIME_SKILL / "SKILL.md"
        command = GIT_SKILL / "commands" / f"{LOCAL_REALTIME_SKILL_NAME}.md"

        self.assertTrue(skill.is_file())
        self.assertTrue(command.is_file())

        skill_text = skill.read_text(encoding="utf-8")
        command_text = command.read_text(encoding="utf-8")
        self.assertIn(f"name: {LOCAL_REALTIME_SKILL_NAME}", skill_text)
        self.assertIn("<plugin-root>/skills/git-commit/SKILL.md", skill_text)
        self.assertNotIn("<plugin-root>/skills/git-commit-push/SKILL.md", skill_text)
        self.assertIn(f"**{LOCAL_REALTIME_SKILL_NAME}** skill", command_text)

    def test_local_realtime_commit_publishes_a_short_alias_command(self) -> None:
        alias = GIT_SKILL / "commands" / f"{LOCAL_REALTIME_ALIAS}.md"

        self.assertTrue(alias.is_file())

        alias_text = alias.read_text(encoding="utf-8")
        self.assertIn(f"**{LOCAL_REALTIME_SKILL_NAME}** skill", alias_text)
        self.assertIn(f"Alias for `/{LOCAL_REALTIME_SKILL_NAME}`", frontmatter(alias))

    def test_local_alias_command_body_matches_the_canonical_command(self) -> None:
        canonical = GIT_SKILL / "commands" / f"{LOCAL_REALTIME_SKILL_NAME}.md"
        alias = GIT_SKILL / "commands" / f"{LOCAL_REALTIME_ALIAS}.md"

        self.assertEqual(body(canonical), body(alias))

    def test_local_alias_is_discoverable_from_the_skill_description(self) -> None:
        description = frontmatter(LOCAL_REALTIME_SKILL / "SKILL.md")

        for token in (f'"/{LOCAL_REALTIME_ALIAS}"', f'"${LOCAL_REALTIME_ALIAS}"'):
            with self.subTest(token=token):
                self.assertIn(token, description)

    def test_local_alias_is_documented_across_package_surfaces(self) -> None:
        documented = [
            ROOT / "README.md",
            ROOT / "README.ko.md",
            ROOT / "USAGE.md",
            ROOT / "ARCHITECTURE.md",
            GIT_SKILL / "README.md",
            GIT_SKILL / "README.ko.md",
        ]

        for path in documented:
            with self.subTest(path=path):
                self.assertIn(
                    f"`/{LOCAL_REALTIME_ALIAS}`",
                    path.read_text(encoding="utf-8"),
                )

    def test_local_realtime_commit_uses_green_outcome_checkpoints(self) -> None:
        skill = (LOCAL_REALTIME_SKILL / "SKILL.md").read_text(encoding="utf-8")

        for contract in (
            "Do not split work by file count, elapsed time, token pressure",
            "leaves the repository in a usable state",
            "Do not create `WIP`, `tmp`, or generic checkpoint commits",
            "Run the narrowest relevant tests and repository-required checks",
            "git diff --check",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, skill)

    def test_local_realtime_commit_keeps_checkpoints_local(self) -> None:
        skill = (LOCAL_REALTIME_SKILL / "SKILL.md").read_text(encoding="utf-8")

        for contract in (
            "After each checkpoint commit succeeds, record its hash and leave it local",
            "Do not run `git push`",
            "Publication stays a separate, explicit user request",
            "Never push, pull, merge, rebase, or rewrite history from this workflow",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, skill)

    def test_local_realtime_commit_evals_cover_checkpoint_safety(self) -> None:
        eval_path = LOCAL_REALTIME_SKILL / "evals" / "evals.json"
        payload = json.loads(eval_path.read_text(encoding="utf-8"))

        self.assertEqual(LOCAL_REALTIME_SKILL_NAME, payload["skill_name"])
        self.assertEqual([1, 2, 3], [item["id"] for item in payload["evals"]])
        prompts = " ".join(item["prompt"] for item in payload["evals"])
        self.assertIn("will not compile", prompts)
        self.assertIn("without pushing", prompts)

    def test_local_realtime_commit_is_documented_across_package_surfaces(self) -> None:
        package_readmes = [
            GIT_SKILL / "README.md",
            GIT_SKILL / "README.ko.md",
        ]
        command_docs = [
            ROOT / "README.md",
            ROOT / "README.ko.md",
            ROOT / "USAGE.md",
            ROOT / "ARCHITECTURE.md",
        ]

        for path in package_readmes:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(2, text.count(f"--skill {LOCAL_REALTIME_SKILL_NAME}"))
                self.assertIn(f"/{LOCAL_REALTIME_SKILL_NAME}", text)
                self.assertIn(f"${LOCAL_REALTIME_SKILL_NAME}", text)

        for path in command_docs:
            with self.subTest(path=path):
                self.assertIn(
                    LOCAL_REALTIME_SKILL_NAME,
                    path.read_text(encoding="utf-8"),
                )

    def test_legacy_live_selector_is_removed_from_published_sources(self) -> None:
        legacy_selector = "git-commit-push-" + "live"
        checked_suffixes = {".json", ".md", ".py", ".yaml"}

        for path in ROOT.rglob("*"):
            relative_path = path.relative_to(ROOT)
            if (
                not path.is_file()
                or path.suffix not in checked_suffixes
                or ".git" in path.parts
                or "__pycache__" in path.parts
                or any(part.startswith(".") for part in relative_path.parts)
            ):
                continue
            with self.subTest(path=relative_path):
                self.assertNotIn(
                    legacy_selector,
                    path.read_text(encoding="utf-8"),
                )

    def test_published_skill_count_matches_packaged_skills(self) -> None:
        packaged_skills = list(ROOT.glob("*/skills/*/SKILL.md"))
        self.assertEqual(26, len(packaged_skills))

        expected_counts = {
            ROOT / "README.md": "25 practical agent workflows and 26 installable Codex selectors",
            ROOT / "README.ko.md": "25개의 실용적인 에이전트 워크플로와 26개의 설치 가능한 Codex selector",
            ROOT / "USAGE.md": "25 canonical workflows and 26 installable Codex selectors",
            ROOT / "ARCHITECTURE.md": "expose 25 canonical workflows through 26 installable Codex selectors",
        }
        for path, phrase in expected_counts.items():
            with self.subTest(path=path):
                self.assertIn(phrase, path.read_text(encoding="utf-8"))

    def test_plugin_metadata_publishes_realtime_checkpoint_support(self) -> None:
        metadata = json.loads(
            (GIT_SKILL / ".claude-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual("git-skill", metadata["name"])
        self.assertEqual("0.8.0", metadata["version"])
        self.assertIn("realtime checkpoint commits and pushes", metadata["description"])

    def test_env_example_is_explicitly_exempt_from_secret_file_blocking(self) -> None:
        expected_contracts = {
            GIT_SKILL
            / "skills"
            / "git-commit"
            / "SKILL.md": "Do not flag the exact basename `.env.example` solely because it matches `.env*`",
            GIT_SKILL
            / "skills"
            / "git-commit-push"
            / "SKILL.md": "The exact basename `.env.example` is a public template",
            GIT_SKILL
            / "README.md": "except the exact basename `.env.example`",
            GIT_SKILL
            / "README.ko.md": "정확한 파일명 `.env.example`은 예외",
        }

        for path, contract in expected_contracts.items():
            with self.subTest(path=path):
                self.assertIn(contract, path.read_text(encoding="utf-8"))

    def test_merge_skills_keep_protected_source_branches_after_merge(self) -> None:
        checked_paths = [
            GIT_SKILL / "skills" / "git-merge-to-main" / "SKILL.md",
            GIT_SKILL / "skills" / "git-merge-to-dev" / "SKILL.md",
            GIT_SKILL / "commands" / "git-merge-to-main.md",
            GIT_SKILL / "commands" / "git-merge-to-dev.md",
        ]

        for path in checked_paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn(PROTECTED_BRANCH_LIST, text)
                self.assertIn("protected source branch", text.lower())
                self.assertIn("skip the local delete", text.lower())

    def test_branch_cleanup_uses_same_protected_branch_list(self) -> None:
        checked_paths = [
            GIT_SKILL / "skills" / "git-branch-cleanup" / "SKILL.md",
            GIT_SKILL / "commands" / "git-branch-cleanup.md",
            GIT_SKILL / "README.md",
            GIT_SKILL / "README.ko.md",
        ]

        for path in checked_paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn(PROTECTED_BRANCH_LIST, text)
