import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GIT_SKILL = ROOT / "git-skill"
REALTIME_SKILL_NAME = "git-commit-push-realtime"
REALTIME_SKILL = GIT_SKILL / "skills" / REALTIME_SKILL_NAME

PROTECTED_BRANCH_LIST = (
    "`main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`"
)


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
                self.assertEqual(2, text.count(f"--skill {REALTIME_SKILL_NAME}"))
                self.assertIn(f"/{REALTIME_SKILL_NAME}", text)
                self.assertIn(f"${REALTIME_SKILL_NAME}", text)

        for path in command_docs:
            with self.subTest(path=path):
                self.assertIn(
                    REALTIME_SKILL_NAME,
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
        self.assertEqual(17, len(packaged_skills))

        expected_counts = {
            ROOT / "README.md": "17 practical agent skills",
            ROOT / "README.ko.md": "17개의 실용적인 에이전트 스킬",
            ROOT / "USAGE.md": "17 independently discoverable skills",
            ROOT / "ARCHITECTURE.md": "expose 17 skills",
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
        self.assertEqual("0.5.0", metadata["version"])
        self.assertIn("realtime checkpoint pushes", metadata["description"])

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
