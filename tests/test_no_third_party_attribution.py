"""Shipped files must not credit or link another party's skill catalog."""

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECKED_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".ts", ".tsx", ".mjs", ".py"}

# Directories that ship to users. Design notes under docs/ and local scratch
# directories are excluded on purpose.
SHIPPED_ROOTS = (
    "build-reinstall",
    "bug-hunt",
    "code-review",
    "doc-skill",
    "git-skill",
    "handoff",
    "human-friendly-writing",
    "long-task",
    "plan-summary",
    "research-brief",
    "review-me",
    "skill-forge",
    "work-summary",
    "website/src",
    "website/scripts",
)

SHIPPED_FILES = (
    "README.md",
    "README.ko.md",
    "USAGE.md",
    "ARCHITECTURE.md",
    "AGENTS.md",
    "CLAUDE.md",
    "website/README.md",
)

# Each pattern names a way a borrowed catalog leaks back into shipped text.
FORBIDDEN = (
    re.compile(r"mattpocock", re.IGNORECASE),
    re.compile(r"\binspired by\b", re.IGNORECASE),
    re.compile(r"\badapted from\b", re.IGNORECASE),
    re.compile(r"\bderived from [A-Z]", re.MULTILINE),
    re.compile(r"originally (?:from|by)\b", re.IGNORECASE),
    re.compile(r"참고했습니다"),
    re.compile(r"출처[::]"),
    re.compile(r"(?m)^#{1,6}\s*Credits\b", re.IGNORECASE),
    re.compile(r"(?m)^#{1,6}\s*크레딧"),
)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return [ROOT / name for name in result.stdout.split("\0") if name]


class NoThirdPartyAttributionTest(unittest.TestCase):
    def test_shipped_files_do_not_credit_another_catalog(self) -> None:
        checked = 0
        for path in tracked_files():
            if path.suffix not in CHECKED_SUFFIXES or not path.is_file():
                continue
            relative = path.relative_to(ROOT).as_posix()
            if relative == Path(__file__).relative_to(ROOT).as_posix():
                continue
            shipped = relative in SHIPPED_FILES or any(
                relative.startswith(f"{prefix}/") for prefix in SHIPPED_ROOTS
            )
            if not shipped:
                continue

            checked += 1
            text = path.read_text(encoding="utf-8")
            for pattern in FORBIDDEN:
                with self.subTest(path=relative, pattern=pattern.pattern):
                    self.assertIsNone(
                        pattern.search(text),
                        f"{relative} credits or links a third-party catalog",
                    )

        self.assertGreater(checked, 50, "attribution sweep scanned too few files")


if __name__ == "__main__":
    unittest.main()
