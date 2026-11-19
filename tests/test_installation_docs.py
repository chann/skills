import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def published_counts() -> tuple[int, int, int]:
    """Workflow, selector, and plugin counts derived from the packaged tree."""
    selectors = len(list(ROOT.glob("*/skills/*/SKILL.md")))
    catalog = (ROOT / "website" / "src" / "data" / "skills.ts").read_text(
        encoding="utf-8"
    )
    workflows = len(re.findall(r'^\s*id: "([^"]+)",$', catalog, re.MULTILINE))
    plugins = len(list(ROOT.glob("*/.claude-plugin/plugin.json")))
    return workflows, selectors, plugins


def documented_selector_count() -> int:
    """The selector count published in USAGE.md."""
    text = (ROOT / "USAGE.md").read_text(encoding="utf-8")
    match = re.search(r"(\d+) installable Codex selectors", text)
    assert match, "USAGE.md must publish an installable Codex selector count"
    return int(match.group(1))

PLUGIN_READMES = [
    ROOT / plugin / name
    for plugin in (
        "chann-mode",
        "understand",
        "research-brief",
        "recall",
        "diff-summary",
        "plan-summary",
        "review-me",
        "swarm",
        "bug-hunt",
        "doc-skill",
        "unslop",
        "build-reinstall",
        "interrogate",
        "git-skill",
        "long-task",
        "handoff",
        "skill-forge",
    )
    for name in ("README.md", "README.ko.md")
]

INSTALL_DOCS = [
    ROOT / "README.md",
    ROOT / "README.ko.md",
    ROOT / "USAGE.md",
    *PLUGIN_READMES,
    ROOT / "doc-skill" / "USAGE.md",
]

INTERROGATE_READMES = [
    ROOT / "interrogate" / "README.md",
    ROOT / "interrogate" / "README.ko.md",
]

DIFF_SUMMARY_READMES = [
    ROOT / "diff-summary" / "README.md",
    ROOT / "diff-summary" / "README.ko.md",
]

ROOT_DIFF_SUMMARY_DOCS = [
    ROOT / "README.md",
    ROOT / "README.ko.md",
    ROOT / "USAGE.md",
    ROOT / "ARCHITECTURE.md",
]

ROOT_SELECTOR_DOCS = [
    ROOT / "README.md",
    ROOT / "README.ko.md",
    ROOT / "USAGE.md",
]

PLAN_SUMMARY_READMES = [
    ROOT / "plan-summary" / "README.md",
    ROOT / "plan-summary" / "README.ko.md",
]

ROOT_PLAN_SUMMARY_DOCS = [
    ROOT / "README.md",
    ROOT / "README.ko.md",
    ROOT / "USAGE.md",
    ROOT / "ARCHITECTURE.md",
]

ROOT_COUNT_DOCS = ROOT_PLAN_SUMMARY_DOCS

# Names that no longer exist as selectors. Root docs may spell them only inside
# a migration table row or the command that removes them;
# `samples/code-review/` is a real directory.
RETIRED_NAMES = re.compile(
    r"code-review|diff-summary-(?:md|quiz)|plan-summary-(?:md|quiz)"
    r"|human-friendly-writing|git-commit-(?:push|realtime|rewrite)"
    r"|git-merge-to-|git-branch-cleanup|gen-(?:frontend|backend|session)-handoff"
    r"|all-subagents|work-summary|ketchup"
)
REMOVE_COMMAND = "npx skills remove"
# Every retired selector, so the documented removal command cannot miss one.
# `chann-mode` is still the plugin directory, so it cannot be in the pattern above.
RETIRED_SELECTORS = (
    "code-review", "code-review-md", "diff-summary-md", "diff-summary-quiz",
    "plan-summary-md", "plan-summary-quiz", "human-friendly-writing",
    "git-commit-push", "git-commit-realtime", "git-commit-push-realtime",
    "git-commit-push-deploy", "git-commit-rewrite", "git-merge-to-main",
    "git-merge-to-dev", "git-branch-cleanup", "gen-frontend-handoff",
    "gen-backend-handoff", "gen-session-handoff", "all-subagents",
    "work-summary", "chann-mode", "ketchup",
)


def removal_command(text: str) -> str:
    """The fenced block that starts with the removal command, or an empty string."""
    for block in re.findall(r"```bash\n(.*?)```", text, re.DOTALL):
        if block.lstrip().startswith(REMOVE_COMMAND):
            return block
    return ""


def frontmatter_value(skill_path: Path, key: str) -> str:
    text = skill_path.read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)[1]
    prefix = f"{key}: "
    for line in frontmatter.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix)
    raise AssertionError(f"{skill_path.relative_to(ROOT)} is missing {key}")


class InstallationDocsTests(unittest.TestCase):
    def test_npx_install_examples_use_skill_option_not_at_selector(self) -> None:
        invalid_selector = re.compile(r"npx skills add[^\n`]*chann/skills@")

        for path in INSTALL_DOCS:
            with self.subTest(doc=path.relative_to(ROOT)):
                self.assertIsNone(invalid_selector.search(path.read_text(encoding="utf-8")))

    def test_plugin_readmes_install_every_packaged_skill_by_exact_selector(self) -> None:
        for plugin_readmes, plugin in (
            (INTERROGATE_READMES, "interrogate"),
            (DIFF_SUMMARY_READMES, "diff-summary"),
        ):
            skills_root = ROOT / plugin / "skills"
            expected_selectors = tuple(
                sorted(
                    path.name
                    for path in skills_root.iterdir()
                    if (path / "SKILL.md").is_file()
                )
            )
            self.assertIn(plugin, expected_selectors)
            self._assert_exact_selector_installs(plugin_readmes, expected_selectors)

    def _assert_exact_selector_installs(
        self, readmes: list[Path], expected_selectors: tuple[str, ...]
    ) -> None:
        for path in readmes:
            text = path.read_text(encoding="utf-8")
            with self.subTest(doc=path.relative_to(ROOT)):
                for selector in expected_selectors:
                    self.assertGreaterEqual(
                        text.count(f"--skill {selector}"),
                        2,
                        f"{path.relative_to(ROOT)} must include {selector} in global and local installs",
                    )

    def test_every_skill_declares_claude_code_and_codex_interfaces(self) -> None:
        skill_paths = sorted(ROOT.glob("*/skills/*/SKILL.md"))
        # The packaged tree, not a hand-maintained number, is the source of
        # truth; the docs must follow it.
        self.assertEqual(documented_selector_count(), len(skill_paths))

        for skill_path in skill_paths:
            selector = skill_path.parent.name
            plugin_root = skill_path.parents[2]
            command_path = plugin_root / "commands" / f"{selector}.md"
            openai_interface_path = skill_path.parent / "agents" / "openai.yaml"
            description = frontmatter_value(skill_path, "description")

            with self.subTest(skill=selector):
                self.assertEqual(selector, frontmatter_value(skill_path, "name"))
                self.assertTrue(
                    command_path.is_file(),
                    f"missing Claude Code command wrapper: {command_path.relative_to(ROOT)}",
                )
                self.assertIn(f"/{selector}", description)
                self.assertIn(f"${selector}", description)
                self.assertTrue(
                    openai_interface_path.is_file(),
                    "missing Codex interface metadata: "
                    f"{openai_interface_path.relative_to(ROOT)}",
                )
                openai_interface = openai_interface_path.read_text(encoding="utf-8")
                interface_lines = [
                    line for line in openai_interface.splitlines() if line.strip()
                ]
                self.assertEqual("interface:", interface_lines[0])
                fields = set()
                for line in interface_lines[1:]:
                    match = re.fullmatch(r'  ([a-z_]+): ".+"', line)
                    self.assertIsNotNone(
                        match,
                        f"invalid Codex interface entry: {line}",
                    )
                    if match:
                        fields.add(match.group(1))
                self.assertEqual(
                    {"display_name", "short_description", "default_prompt"},
                    fields,
                )
                self.assertIn(f"${selector}", openai_interface)

    def test_root_and_package_readmes_publish_both_platform_selectors(self) -> None:
        for skill_path in sorted(ROOT.glob("*/skills/*/SKILL.md")):
            selector = skill_path.parent.name
            plugin_root = skill_path.parents[2]
            docs = [
                *ROOT_SELECTOR_DOCS,
                plugin_root / "README.md",
                plugin_root / "README.ko.md",
            ]

            for path in docs:
                text = path.read_text(encoding="utf-8")
                with self.subTest(skill=selector, doc=path.relative_to(ROOT)):
                    self.assertIn(f"/{selector}", text)
                    self.assertIn(f"${selector}", text)

    def test_root_docs_publish_diff_summary_command_and_generated_path(self) -> None:
        for path in ROOT_DIFF_SUMMARY_DOCS:
            text = path.read_text(encoding="utf-8")
            with self.subTest(doc=path.relative_to(ROOT)):
                self.assertIn("/diff-summary", text)
                self.assertIn(".diff-summaries/", text)

    def test_root_docs_publish_plan_summary_options_and_counts(self) -> None:
        for path in ROOT_PLAN_SUMMARY_DOCS:
            text = path.read_text(encoding="utf-8")
            with self.subTest(doc=path.relative_to(ROOT)):
                self.assertIn("/plan-summary", text)
                self.assertIn("$plan-summary", text)
                self.assertIn("--md", text)
                self.assertIn("--quiz", text)
                self.assertIn(".plan-summaries/", text)
                for count in published_counts():
                    self.assertIn(str(count), text)

    def test_root_docs_publish_diff_summary_options(self) -> None:
        for path in ROOT_DIFF_SUMMARY_DOCS:
            text = path.read_text(encoding="utf-8")
            with self.subTest(doc=path.relative_to(ROOT)):
                self.assertIn("--md", text)
                self.assertIn("--quiz", text)

    def test_root_docs_name_retired_selectors_only_in_migration_tables(self) -> None:
        for path in ROOT_COUNT_DOCS:
            text = path.read_text(encoding="utf-8")
            removal_lines = set(removal_command(text).splitlines())
            with self.subTest(doc=path.relative_to(ROOT)):
                for number, line in enumerate(text.splitlines(), start=1):
                    checked = line.replace("samples/code-review", "")
                    if RETIRED_NAMES.search(checked):
                        self.assertTrue(
                            line.lstrip().startswith("|") or line in removal_lines,
                            f"{path.name}:{number} names a retired selector outside "
                            f"a table or the removal command: {line}",
                        )

    def test_install_docs_remove_every_retired_selector_in_one_command(self) -> None:
        for path in (ROOT / "README.md", ROOT / "README.ko.md", ROOT / "USAGE.md"):
            command = removal_command(path.read_text(encoding="utf-8"))
            with self.subTest(doc=path.relative_to(ROOT)):
                self.assertTrue(command, "no removal command block")
                self.assertIn("--global", command)
                self.assertIn("--yes", command)
                listed = set(command.replace("\\", " ").split())
                self.assertEqual(set(), set(RETIRED_SELECTORS) - listed)
                packaged = {skill.parent.name for skill in ROOT.glob("*/skills/*/SKILL.md")}
                self.assertEqual(set(), listed & packaged, "the command would remove a current skill")

    def test_plan_summary_readmes_publish_exact_installs_and_boundaries(self) -> None:
        for path in PLAN_SUMMARY_READMES:
            text = path.read_text(encoding="utf-8")
            with self.subTest(doc=path.relative_to(ROOT)):
                self.assertGreaterEqual(text.count("--skill plan-summary"), 2)
                self.assertIn("/plan-summary", text)
                self.assertIn("$plan-summary", text)
                self.assertIn("--md", text)
                self.assertIn("--quiz", text)
                self.assertIn(".plan-summaries/", text)
                self.assertIn("Python 3.10+", text)
                self.assertIn("UTF-8", text)
                self.assertIn(".md", text)
                self.assertIn(".markdown", text)
                self.assertIn(".txt", text)
                self.assertIn("PS-*", text)
                self.assertIn("QZ-*", text)

    def test_plan_summary_artifacts_are_ignored(self) -> None:
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

        self.assertIn(".plan-summaries/", ignore)

    def test_diff_summary_architecture_and_usage_document_the_collector_boundary(self) -> None:
        architecture = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        usage = (ROOT / "USAGE.md").read_text(encoding="utf-8")

        for text in (architecture, usage):
            self.assertIn("collect_diff_evidence.py", text)
            self.assertIn("generate_summary_report.py", text)
        self.assertIn("argv", architecture)
        self.assertIn("JSON", architecture)

    def test_diff_summary_readmes_show_natural_summary_prompts_and_scope_examples(self) -> None:
        english = DIFF_SUMMARY_READMES[0].read_text(encoding="utf-8")
        korean = DIFF_SUMMARY_READMES[1].read_text(encoding="utf-8")

        for phrase in ("summarize the code changes", "main..dev", "last commit", "PR"):
            with self.subTest(language="en", phrase=phrase):
                self.assertIn(phrase, english)
        for phrase in ("코드를 요약해줘", "main..dev", "마지막 커밋", "PR"):
            with self.subTest(language="ko", phrase=phrase):
                self.assertIn(phrase, korean)

    def test_interrogate_readmes_document_proof_graded_conditional_reports(self) -> None:
        # Collapse line wraps and bold markers so a phrase may span lines.
        def flat(path: Path) -> str:
            return " ".join(path.read_text(encoding="utf-8").replace("**", "").split())

        english = flat(INTERROGATE_READMES[0])
        korean = flat(INTERROGATE_READMES[1])

        for phrase in (
            "observed behavior → practical consequence → smallest justified correction",
            "appear only when they add distinct, decision-relevant",
            "Verified context that affects a decision; no code change required",
            "`Dropped:`",
        ):
            with self.subTest(language="en", phrase=phrase):
                self.assertIn(phrase, english)

        for phrase in (
            "관찰한 동작 → 실제 결과 → 근거가 허락하는 가장 작은 수정",
            "판단에 꼭 필요할 때만 넣습니다",
            "판단에 영향을 주는 확인된 사실. 코드 수정은 필요 없습니다",
            "`Dropped:`",
        ):
            with self.subTest(language="ko", phrase=phrase):
                self.assertIn(phrase, korean)

        for text in (english, korean):
            for level in ("said", "cited", "traced", "ran", "reproduced"):
                self.assertIn(f"`{level}`", text)

        self.assertNotIn("Each `/code-review*` report includes:", english)
        self.assertNotIn("각 `/code-review*` 리포트에는 다음이 포함됩니다:", korean)
        self.assertNotIn("Positive observation or contextual note", english)
        self.assertNotIn("긍정적 관찰 또는 참고 사항", korean)
