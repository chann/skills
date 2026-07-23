import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GIT_SKILL = ROOT / "git-skill"

PROTECTED_BRANCH_LIST = (
    "`main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`"
)


class GitSkillPackageTests(unittest.TestCase):
    def test_live_commit_push_skill_is_packaged_with_command(self) -> None:
        skill = (
            GIT_SKILL
            / "skills"
            / "git-commit-push-live"
            / "SKILL.md"
        )
        command = GIT_SKILL / "commands" / "git-commit-push-live.md"

        self.assertTrue(skill.is_file())
        self.assertTrue(command.is_file())

        skill_text = skill.read_text(encoding="utf-8")
        command_text = command.read_text(encoding="utf-8")
        self.assertIn("name: git-commit-push-live", skill_text)
        self.assertIn("<plugin-root>/skills/git-commit/SKILL.md", skill_text)
        self.assertIn("<plugin-root>/skills/git-commit-push/SKILL.md", skill_text)
        self.assertIn("**git-commit-push-live** skill", command_text)

    def test_live_commit_push_uses_green_outcome_checkpoints(self) -> None:
        skill = (
            GIT_SKILL
            / "skills"
            / "git-commit-push-live"
            / "SKILL.md"
        ).read_text(encoding="utf-8")

        for contract in (
            "Do not split work by file count, elapsed time, token pressure",
            "leaves the repository in a usable state",
            "Do not create `WIP`, `tmp`, or generic checkpoint commits",
            "Run the narrowest relevant tests and repository-required checks",
            "git diff --check",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, skill)

    def test_live_commit_push_pushes_each_checkpoint_and_stops_on_drift(self) -> None:
        skill = (
            GIT_SKILL
            / "skills"
            / "git-commit-push-live"
            / "SKILL.md"
        ).read_text(encoding="utf-8")

        for contract in (
            "After each checkpoint commit succeeds, push it before starting the next unit",
            'git push -u origin "$(git branch --show-current)"',
            "git rev-list --left-right --count HEAD...@{u}",
            "do not retry through `pull`, merge, rebase, `--force`, or",
            "Never begin the next checkpoint until the previous push and upstream parity",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, skill)

    def test_live_commit_push_evals_cover_checkpoint_safety(self) -> None:
        eval_path = (
            GIT_SKILL
            / "skills"
            / "git-commit-push-live"
            / "evals"
            / "evals.json"
        )
        payload = json.loads(eval_path.read_text(encoding="utf-8"))

        self.assertEqual("git-commit-push-live", payload["skill_name"])
        self.assertEqual([1, 2, 3], [item["id"] for item in payload["evals"]])
        prompts = " ".join(item["prompt"] for item in payload["evals"])
        self.assertIn("will not compile", prompts)
        self.assertIn("remote advances", prompts)

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
