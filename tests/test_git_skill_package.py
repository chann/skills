import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GIT_SKILL = ROOT / "git-skill"

PROTECTED_BRANCH_LIST = (
    "`main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`"
)


class GitSkillPackageTests(unittest.TestCase):
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
