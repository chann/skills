import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

INSTALL_DOCS = [
    ROOT / "USAGE.md",
    ROOT / "code-review" / "README.md",
    ROOT / "code-review" / "README.ko.md",
    ROOT / "doc-skill" / "README.md",
    ROOT / "doc-skill" / "README.ko.md",
    ROOT / "doc-skill" / "USAGE.md",
    ROOT / "git-skill" / "README.md",
    ROOT / "git-skill" / "README.ko.md",
    ROOT / "handoff" / "README.md",
    ROOT / "handoff" / "README.ko.md",
    ROOT / "long-task" / "README.md",
    ROOT / "long-task" / "README.ko.md",
]


class InstallationDocsTests(unittest.TestCase):
    def test_npx_install_examples_use_skill_option_not_at_selector(self) -> None:
        invalid_selector = re.compile(r"npx skills add[^\n`]*chann/skills@")

        for path in INSTALL_DOCS:
            with self.subTest(doc=path.relative_to(ROOT)):
                self.assertIsNone(invalid_selector.search(path.read_text(encoding="utf-8")))
