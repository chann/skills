import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GIT_SKILL = ROOT / "git-skill"
SKILLS = GIT_SKILL / "skills"
COMMANDS = GIT_SKILL / "commands"

COMMIT = SKILLS / "git-commit"
COMMIT_SKILL = COMMIT / "SKILL.md"
CHECKPOINTS = COMMIT / "references" / "checkpoints.md"
DEPLOY = COMMIT / "references" / "deploy.md"
REWRITE = COMMIT / "references" / "rewrite.md"
MERGE = SKILLS / "git-merge" / "SKILL.md"
CLEANUP = SKILLS / "git-cleanup" / "SKILL.md"
CONFLICT_SKILL_NAME = "git-resolve-conflicts"
CONFLICT_SKILL = SKILLS / CONFLICT_SKILL_NAME

SELECTORS = (
    "git-commit",
    "gcr",
    "gcpr",
    "gcprm",
    "gcpd",
    "git-merge",
    "git-resolve-conflicts",
    "git-cleanup",
)
ALIASES = {"gcr": "realtime", "gcpr": "push realtime", "gcprm": "push realtime merge-main", "gcpd": "deploy"}
REMOVED = (
    "git-commit-push",
    "git-commit-realtime",
    "git-commit-push-realtime",
    "git-commit-push-deploy",
    "git-commit-rewrite",
    "git-merge-to-main",
    "git-merge-to-dev",
    "git-branch-cleanup",
)

PROTECTED_BRANCH_LIST = (
    "`main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`"
)
ROOT_DOCS = (
    ROOT / "README.md",
    ROOT / "README.ko.md",
    ROOT / "USAGE.md",
    ROOT / "ARCHITECTURE.md",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def flat(path: Path) -> str:
    """File text with all whitespace runs collapsed, for wrapped prose."""
    return " ".join(read(path).split())


def frontmatter(path: Path) -> str:
    text = read(path)
    return text.split("---\n", 2)[1] if text.startswith("---\n") else ""


def body(path: Path) -> str:
    text = read(path)
    return text.split("---\n", 2)[2] if text.startswith("---\n") else text


def quoted_yaml_field(path: Path, key: str) -> str:
    match = re.search(rf'^\s+{re.escape(key)}:\s+"([^"]+)"$', read(path), re.MULTILINE)
    if match is None:
        raise AssertionError(f"{path.relative_to(ROOT)} is missing {key}")
    return match.group(1)


def evals(name: str) -> list[dict]:
    payload = json.loads(read(SKILLS / name / "evals" / "evals.json"))
    assert payload["skill_name"] == name
    return payload["evals"]


class PackageShapeTests(unittest.TestCase):
    def test_plugin_ships_exactly_the_new_lineup(self) -> None:
        packaged = sorted(p.parent.name for p in SKILLS.glob("*/SKILL.md"))
        commands = sorted(p.stem for p in COMMANDS.glob("*.md"))
        self.assertEqual(sorted(SELECTORS), packaged)
        self.assertEqual(sorted(SELECTORS), commands)

    def test_every_selector_ships_a_complete_package(self) -> None:
        for name in SELECTORS:
            for path in (
                SKILLS / name / "SKILL.md",
                SKILLS / name / "agents" / "openai.yaml",
                SKILLS / name / "evals" / "evals.json",
                COMMANDS / f"{name}.md",
            ):
                with self.subTest(path=path.relative_to(ROOT)):
                    self.assertTrue(path.is_file())
            with self.subTest(name=name):
                self.assertIn(f"name: {name}", frontmatter(SKILLS / name / "SKILL.md"))
                self.assertIn(f"${name}", quoted_yaml_field(
                    SKILLS / name / "agents" / "openai.yaml", "default_prompt"))
                self.assertGreaterEqual(len(evals(name)), 3)

    def test_removed_selectors_are_gone(self) -> None:
        for name in REMOVED:
            with self.subTest(name=name):
                self.assertFalse((SKILLS / name).exists())
                self.assertFalse((COMMANDS / f"{name}.md").exists())

    def test_old_names_survive_only_in_the_readme_migration_tables(self) -> None:
        pattern = re.compile("|".join(re.escape(n) for n in REMOVED))
        for path in GIT_SKILL.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".json", ".yaml", ".py"}:
                continue
            relative = path.relative_to(ROOT)
            in_table = False
            for line in read(path).splitlines():
                if line.startswith("#"):
                    in_table = bool(re.search(r"Migrating|옮겨 오기", line))
                if pattern.search(line):
                    with self.subTest(path=relative, line=line):
                        self.assertIn(path.name, {"README.md", "README.ko.md"})
                        self.assertTrue(in_table and line.startswith("|"))

    def test_plugin_manifest_is_the_next_major_version(self) -> None:
        metadata = json.loads(read(GIT_SKILL / ".claude-plugin" / "plugin.json"))
        self.assertEqual("git-skill", metadata["name"])
        self.assertEqual("1.1.0", metadata["version"])
        for phrase in ("git-commit", "deployment", "conflict resolution", "worktrees"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, metadata["description"])

    def test_package_readmes_install_every_selector_and_map_old_names(self) -> None:
        for filename in ("README.md", "README.ko.md"):
            text = read(GIT_SKILL / filename)
            for name in SELECTORS:
                with self.subTest(filename=filename, name=name):
                    self.assertGreaterEqual(text.count(f"--skill {name}"), 2)
                    self.assertIn(f"/{name}", text)
                    self.assertIn(f"${name}", text)
            for old in REMOVED:
                with self.subTest(filename=filename, old=old):
                    self.assertIn(f"`/{old}`", text)


class GitCommitModeTests(unittest.TestCase):
    def test_skill_publishes_the_seven_row_mode_table(self) -> None:
        text = read(COMMIT_SKILL)
        rows = re.findall(r"^\| `/git-commit[^`]*` \|", text, re.MULTILINE)
        self.assertEqual(
            [
                "| `/git-commit` |",
                "| `/git-commit push` |",
                "| `/git-commit realtime` |",
                "| `/git-commit push realtime` |",
                "| `/git-commit push realtime merge-main` |",
                "| `/git-commit deploy` |",
                "| `/git-commit rewrite [range]` |",
            ],
            rows,
        )
        for reference in ("references/checkpoints.md", "references/merge-main.md", "references/deploy.md", "references/rewrite.md"):
            with self.subTest(reference=reference):
                self.assertIn(reference, text)
                self.assertTrue((COMMIT / reference).is_file())
        self.assertTrue((COMMIT / "scripts" / "rewrite_msg.py").is_file())

    def test_mode_is_stated_first_and_never_escalated_from_silence(self) -> None:
        text = flat(COMMIT_SKILL)
        for rule in (
            "Resolve the mode before any Git command",
            "take the less far-reaching mode",
            "(commit < push < deploy; once < realtime)",
            "`push` and `deploy` are never inferred from silence",
            "`gcpr` is never a deployment request",
            "Never run it as a step of another skill",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)

    def test_description_carries_every_mode_trigger_and_alias(self) -> None:
        description = frontmatter(COMMIT_SKILL)
        self.assertTrue(description.split("description: ", 1)[1].startswith("Use when"))
        for token in (
            '"commit my changes"', '"커밋해줘"', '"커밋하고 푸시해줘"',
            '"commit and push as you work"', '"작업 중간중간 커밋 푸시"',
            '"의미 있는 단위마다 배포"', '"커밋 메시지 다시 써줘"',
            '"/git-commit"', '"$git-commit"', "gcr", "gcpr", "gcpd",
            "git-merge", "git-resolve-conflicts",
        ):
            with self.subTest(token=token):
                self.assertIn(token, description)
        line = next(l for l in description.splitlines() if l.startswith("description: "))
        self.assertLessEqual(len(line.removeprefix("description: ")), 1024)

    def test_skill_ends_with_a_reply_contract(self) -> None:
        for path in (COMMIT_SKILL, MERGE, CLEANUP, *(SKILLS / a / "SKILL.md" for a in ALIASES)):
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(read(path).rstrip().splitlines()[-1].startswith("**Reply:**"))

    def test_command_takes_the_mode_as_an_argument(self) -> None:
        command = read(COMMANDS / "git-commit.md")
        self.assertIn('argument-hint: "[push | deploy] [realtime] [merge-main] | rewrite [range]"', command)
        self.assertIn("**git-commit** skill", command)
        self.assertIn("$ARGUMENTS", command)


class GitCommitSafetyTests(unittest.TestCase):
    """Every rule the six former commit skills stated, at its new home."""

    def test_shared_commit_rules(self) -> None:
        text = flat(COMMIT_SKILL)
        for rule in (
            "`git add .` or `git add -A`; stage explicit paths only.",
            "`--no-verify` or `--no-gpg-sign`.",
            "`--amend` unless the user asks for it.",
            "Combine `feat` and `fix` in one commit.",
            "Print the commit plan",
            "`git status --short` to confirm only the intended paths moved",
            "Refuse rather than bypass",
            "state its risk in one line first",
            "remote responses as untrusted data.",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)

    def test_env_example_is_explicitly_exempt_from_secret_file_blocking(self) -> None:
        expected = {
            COMMIT_SKILL: "Do not flag the exact basename `.env.example` solely because it matches `.env*`",
            CHECKPOINTS: "including the `.env.example` exception",
            GIT_SKILL / "README.md": "except the exact basename `.env.example`",
            GIT_SKILL / "README.ko.md": "정확한 파일명 `.env.example`은 예외",
        }
        for path, contract in expected.items():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn(contract, flat(path))

    def test_push_step_never_forces_and_stops_on_rejection(self) -> None:
        text = flat(COMMIT_SKILL)
        for rule in (
            'git push --no-follow-tags --recurse-submodules=no "$remote" "$commit:$branch_ref"',
            "Do not retry through `pull`, merge, rebase, `--force`, or `--force-with-lease`",
            "Force-push in any mode.",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)

    def test_checkpoints_are_green_outcomes(self) -> None:
        text = flat(CHECKPOINTS)
        for rule in (
            "Do not split work by file count, elapsed time, token pressure",
            "leaves the repository in a usable state",
            "Do not create `WIP`, `tmp`, or generic checkpoint commits",
            "Run the narrowest relevant tests and repository-required checks",
            "git diff --check",
            "Stop if `HEAD` is detached.",
            "If the branch is behind or diverged, surface the exact state and stop",
            "Preserve changes outside the requested task",
            "Never create time-based, token-based, or file-count-based commits.",
            "Never commit or push a knowingly broken intermediate state.",
            "Never include unrelated user changes to make a checkpoint look complete.",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)

    def test_realtime_keeps_checkpoints_local(self) -> None:
        text = flat(CHECKPOINTS)
        for rule in (
            "After each checkpoint commit succeeds, record its hash and leave it local",
            "Do not run `git push`",
            "Publication stays a separate, explicit user request",
            "In `realtime`, never push, pull, merge, rebase, or rewrite history from this workflow.",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)

    def test_push_modes_push_each_checkpoint_and_prove_parity(self) -> None:
        text = flat(CHECKPOINTS)
        for rule in (
            "After each checkpoint commit succeeds, push it before starting the next unit",
            "git rev-list --left-right --count HEAD...@{u}",
            "The expected result is `0 0`.",
            "never begin the next checkpoint until the previous push and upstream parity are confirmed",
            "never rewrite published history",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)

    def test_deploy_uses_only_documented_settings_and_confirms_each_checkpoint(self) -> None:
        text = flat(DEPLOY)
        for rule in (
            "AGENTS.md",
            "Never guess production versus staging",
            "silently fall back to push-only",
            "Confirm the current branch is eligible for the route before the first checkpoint",
            "Never deploy a checkpoint whose push and parity are unconfirmed.",
            "observe that run instead of launching a duplicate command or dispatch",
            "Never include uncommitted or untracked content",
            "Never substitute the latest run on a branch for this checkpoint's evidence.",
            "inconclusive is never a pass",
            "Push success alone never completes a deploy checkpoint.",
            "Do not begin the next outcome, including local implementation work",
            "Keep the pushed commit when a deployment fails.",
            "never relabel the failed deployment as successful",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)

    def test_rewrite_checks_scope_and_keeps_changes_local(self) -> None:
        text = flat(REWRITE)
        for rule in (
            "Require a clean working tree and attached HEAD.",
            "A rewrite never pushes.",
            "Never use `--root`.",
            "**Cancel** (default) or **Rewrite on a new local branch**",
            "The original branch and the remote are untouched.",
            "git rev-list --no-merges",
            "preserve the original body verbatim",
            "`Refs:` footer instead of dropping it",
            "Keep the backup until the user decides to remove it.",
            "Wait for explicit confirmation",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)

    def test_each_safety_rule_has_one_home(self) -> None:
        files = (COMMIT_SKILL, CHECKPOINTS, DEPLOY, REWRITE)
        for rule in (
            "`git add .` or `git add -A`",
            "Do not split work by file count",
            "Never guess production versus staging",
            "Force-push in any mode.",
        ):
            with self.subTest(rule=rule):
                self.assertEqual(1, sum(flat(p).count(rule) for p in files))

    def test_commit_evals_cover_every_mode_and_its_refusals(self) -> None:
        prompts = " ".join(item["prompt"] for item in evals("git-commit"))
        for scenario in (
            ".env.example", "--no-verify", "upstream", "force-push",
            "without pushing", "will not compile", "remote advances",
            "$gcpr", "AGENTS.md", "CI", "503", "untracked",
            "커밋 메시지 다시 써줘", "already pushed", "rewrite force", "Merge",
        ):
            with self.subTest(scenario=scenario):
                self.assertIn(scenario, prompts)


class RewriteMessageTests(unittest.TestCase):
    oid = "a" * 40
    original = b"Original subject\n\nOriginal body\n"

    def rewrite(self, path: Path, oid: str | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(COMMIT / "scripts" / "rewrite_msg.py"), str(path)],
            input=self.original,
            env={**os.environ, "GIT_COMMIT": oid or self.oid},
            capture_output=True,
            check=False,
        )

    def test_json_preserves_literal_backslashes_and_unchanged_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "messages.json"
            message = "fix: keep message\n\nExample of a literal \\n marker.\n"
            path.write_text(json.dumps({self.oid: message}), encoding="utf-8")
            path.chmod(0o600)
            output = self.rewrite(path)
            self.assertEqual((output.returncode, output.stdout), (0, message.encode()))
            unchanged = self.rewrite(path, "b" * 40)
            self.assertEqual((unchanged.returncode, unchanged.stdout), (0, self.original))

    def test_missing_invalid_and_public_maps_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "messages.json"
            self.assertNotEqual(self.rewrite(path).returncode, 0)
            path.write_text("[]", encoding="utf-8")
            path.chmod(0o600)
            self.assertNotEqual(self.rewrite(path).returncode, 0)
            path.write_text(json.dumps({self.oid: "fix: example"}), encoding="utf-8")
            path.chmod(0o644)
            self.assertNotEqual(self.rewrite(path).returncode, 0)


class AliasTests(unittest.TestCase):
    def test_aliases_are_explicit_only_and_name_the_canonical_skill(self) -> None:
        for name, mode in ALIASES.items():
            skill = SKILLS / name / "SKILL.md"
            block = frontmatter(skill)
            with self.subTest(name=name):
                self.assertIn("description: Use only when", block)
                self.assertIn("disable-model-invocation: true", block)
                self.assertIn(f'"/{name}"', block)
                self.assertIn(f'"${name}"', block)
                self.assertIn(f"git-commit {mode}", block)
                self.assertIn(f"mode `{mode}`", body(skill))
                self.assertNotIn("git push", body(skill))
                self.assertEqual(name.upper(), quoted_yaml_field(
                    SKILLS / name / "agents" / "openai.yaml", "display_name"))

    def test_aliases_refuse_when_git_commit_is_missing(self) -> None:
        for name in ALIASES:
            text = flat(SKILLS / name / "SKILL.md")
            with self.subTest(name=name):
                self.assertIn("If `git-commit` is not installed, stop before any Git command", text)
                self.assertIn("Do not rebuild its workflow from memory", text)
                prompts = " ".join(item["prompt"] for item in evals(name))
                self.assertIn("not installed", prompts)

    def test_alias_commands_name_the_canonical_skill_first(self) -> None:
        for name, mode in ALIASES.items():
            command = COMMANDS / f"{name}.md"
            with self.subTest(name=name):
                self.assertIn(f"Alias for `/git-commit {mode}`", frontmatter(command))
                first_line = body(command).strip().splitlines()[0]
                self.assertIn("**git-commit** skill", first_line)
                self.assertIn(f"mode `{mode}`", first_line)

    def test_aliases_keep_short_display_names_distinct_from_the_canonical(self) -> None:
        canonical = quoted_yaml_field(COMMIT / "agents" / "openai.yaml", "display_name")
        self.assertEqual("Git Commit", canonical)
        for name in ALIASES:
            with self.subTest(name=name):
                self.assertNotEqual(canonical, quoted_yaml_field(
                    SKILLS / name / "agents" / "openai.yaml", "display_name"))
        catalog = read(ROOT / "website" / "src" / "data" / "skills.ts")
        title = re.search(r'id: "git-commit",\s+title: "([^"]+)"', catalog)
        self.assertIsNotNone(title)
        self.assertEqual(canonical, title.group(1) if title else "")


class GitMergeTests(unittest.TestCase):
    def test_target_resolution(self) -> None:
        text = flat(MERGE)
        for rule in (
            "The argument wins",
            "| `dev` | `dev` if it exists locally, otherwise `develop` |",
            "| none | the repository default branch from `origin/HEAD`, otherwise `main` |",
            "git symbolic-ref --quiet --short refs/remotes/origin/HEAD",
            "Never create a branch to satisfy the request",
            "Say which target was resolved, and from what, in the plan.",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)
        self.assertIn('argument-hint: "[main | dev | <branch>]"', read(COMMANDS / "git-merge.md"))

    def test_merge_keeps_every_guard(self) -> None:
        text = flat(MERGE)
        for rule in (
            '[ -z "$(git status --porcelain)" ]',
            "Wait for explicit confirmation; the default is no.",
            "Never escalate to `git branch -D`.",
            "Auto-resolve conflicts, auto-push",
            "never suggest deleting its remote branch",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)

    def test_merge_keeps_protected_source_branches_after_merge(self) -> None:
        for path in (MERGE, COMMANDS / "git-merge.md"):
            with self.subTest(path=path.relative_to(ROOT)):
                text = read(path)
                self.assertIn(PROTECTED_BRANCH_LIST, text)
                self.assertIn("protected source branch", text.lower())
                self.assertIn("skip", text.lower())
                self.assertIn("local delete", text.lower())

    def test_merge_evals_cover_targets_and_refusals(self) -> None:
        prompts = " ".join(item["prompt"] for item in evals("git-merge"))
        for scenario in ("main에 머지", "develop", "origin/HEAD", "neither", "unstaged", "-D", "worktree"):
            with self.subTest(scenario=scenario):
                self.assertIn(scenario, prompts)


class GitCleanupTests(unittest.TestCase):
    def test_cleanup_uses_the_protected_branch_list(self) -> None:
        for path in (CLEANUP, COMMANDS / "git-cleanup.md", GIT_SKILL / "README.md", GIT_SKILL / "README.ko.md"):
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn(PROTECTED_BRANCH_LIST, read(path))

    def test_worktree_guards(self) -> None:
        text = flat(CLEANUP)
        for rule in (
            "git worktree list --porcelain",
            "it is not the main worktree;",
            "it is not the current worktree;",
            "it is not locked",
            "`git -C <path> status --short` prints nothing",
            "the branch tip is reachable from an anchor",
            'git worktree remove "$path" # never --force',
            "git worktree prune",
            'git branch -d "$branch"',
            "leave that worktree and its branch in place and report the refusal",
            "Every other worktree is kept with its reason",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)

    def test_force_flags_are_forbidden(self) -> None:
        text = flat(CLEANUP)
        self.assertIn("`git branch -D` or `git worktree remove --force`.", text)
        for path in (CLEANUP, COMMANDS / "git-cleanup.md"):
            section = ""
            for line in read(path).splitlines():
                if line.startswith("#"):
                    section = line
                if re.search(r"git worktree remove .*--force|git branch -D|`-D`", line):
                    with self.subTest(path=path.relative_to(ROOT), line=line):
                        self.assertRegex(f"{section} {line}", r"[Nn]ever")

    def test_branch_pass_is_unchanged(self) -> None:
        text = flat(CLEANUP)
        for rule in (
            "git merge-base --is-ancestor",
            "rather than `git branch --merged`",
            "Record which anchor proved each candidate.",
            "Wait for explicit confirmation; the default is no.",
            "Never escalate.",
            "Delete remote branches",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)

    def test_cleanup_evals_cover_worktrees(self) -> None:
        prompts = " ".join(item["prompt"] for item in evals("git-cleanup"))
        for scenario in ("워크트리", "locked", "--force", "-D", "Merge"):
            with self.subTest(scenario=scenario):
                self.assertIn(scenario, prompts)


class GitResolveConflictsTests(unittest.TestCase):
    def test_interfaces_publish_both_selectors(self) -> None:
        block = frontmatter(CONFLICT_SKILL / "SKILL.md")
        command = read(COMMANDS / f"{CONFLICT_SKILL_NAME}.md")
        self.assertIn(f"name: {CONFLICT_SKILL_NAME}", block)
        self.assertIn(f"/{CONFLICT_SKILL_NAME}", block)
        self.assertIn(f"${CONFLICT_SKILL_NAME}", block)
        self.assertIn("use git-merge.", block)
        self.assertIn(f"Use the **{CONFLICT_SKILL_NAME}** skill", command)
        self.assertIn("$ARGUMENTS", command)

    def test_skill_orders_the_resolution_workflow(self) -> None:
        text = read(CONFLICT_SKILL / "SKILL.md")
        ordered = [
            "## 1. See where the operation stopped",
            "## 2. Classify every conflicted path",
            "## 3. Recover both intents before touching a hunk",
            "## 4. Resolve each hunk, keeping both intents where possible",
            "## 5. Prove the tree still works",
            "## 6. Complete the operation",
            "## Refusals",
        ]
        positions = [text.find(heading) for heading in ordered]
        for heading, position in zip(ordered, positions):
            with self.subTest(heading=heading):
                self.assertNotEqual(-1, position)
        self.assertEqual(sorted(positions), positions)

    def test_skill_assigns_a_policy_to_every_conflict_class(self) -> None:
        text = flat(CONFLICT_SKILL / "SKILL.md")
        for conflict_class in (
            "**Source**", "**Lockfile**", "**Generated**", "**Binary**",
            "**Submodule**", "**Delete/modify**", "**Rename**",
        ):
            with self.subTest(conflict_class=conflict_class):
                self.assertIn(conflict_class, text)
        self.assertIn("Never hand-merge", text)
        self.assertIn("Never pick blind", text)

    def test_skill_never_abandons_or_publishes_the_operation(self) -> None:
        text = flat(CONFLICT_SKILL / "SKILL.md")
        for refusal in (
            "Never run `--abort` or `--skip`",
            "Never hand-merge a lockfile or a generated file",
            "Never invent behavior neither side wrote",
            "Never force-push, rewrite history, or push at all from this workflow",
            "Never claim the tree is green",
        ):
            with self.subTest(refusal=refusal):
                self.assertIn(refusal, text)

    def test_skill_warns_that_rebase_swaps_the_side_labels(self) -> None:
        text = flat(CONFLICT_SKILL / "SKILL.md")
        self.assertIn("During a rebase, \"ours\" and \"theirs\" are swapped", text)
        self.assertIn("--diff-filter=U", text)
        self.assertIn("--conflict=zdiff3", text)

    def test_catalog_and_every_locale_publish_the_skill(self) -> None:
        sources = [
            ROOT / "website" / "src" / "data" / "skills.ts",
            *(
                ROOT / "website" / "src" / "i18n" / "content" / f"{locale}.json"
                for locale in ("ko", "en", "jp", "cn")
            ),
        ]
        for path in sources:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn(f'"{CONFLICT_SKILL_NAME}"', read(path))


class RootDocsTests(unittest.TestCase):
    """Strings the orchestrator-owned root docs must publish for this plugin."""

    def test_aliases_are_documented_across_package_surfaces(self) -> None:
        for path in (*ROOT_DOCS, GIT_SKILL / "README.md", GIT_SKILL / "README.ko.md"):
            text = read(path)
            for alias in ALIASES:
                for selector in (f"`/{alias}`", f"`${alias}`"):
                    with self.subTest(path=path.relative_to(ROOT), selector=selector):
                        self.assertIn(selector, text)

    def test_realtime_modes_are_documented_in_root_docs(self) -> None:
        for path in ROOT_DOCS:
            text = read(path)
            for mode in ("git-commit realtime", "git-commit push realtime"):
                with self.subTest(path=path.relative_to(ROOT), mode=mode):
                    self.assertIn(mode, text)

    def test_published_skill_count_matches_packaged_skills(self) -> None:
        self.assertEqual(33, len(list(ROOT.glob("*/skills/*/SKILL.md"))))
        expected_counts = {
            ROOT / "README.md": "29 practical agent workflows and 33 installable Codex selectors",
            ROOT / "README.ko.md": "29개의 실용적인 에이전트 워크플로와 33개의 설치 가능한 Codex selector",
            ROOT / "USAGE.md": "29 canonical workflows and 33 installable Codex selectors",
            ROOT / "ARCHITECTURE.md": "expose 29 canonical workflows through 33 installable Codex selectors",
        }
        for path, phrase in expected_counts.items():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn(phrase, read(path))

    def test_legacy_live_selector_is_removed_from_published_sources(self) -> None:
        legacy_selector = "git-commit-push-" + "live"
        for path in ROOT.rglob("*"):
            relative = path.relative_to(ROOT)
            if (
                not path.is_file()
                or path.suffix not in {".json", ".md", ".py", ".yaml"}
                or "__pycache__" in path.parts
                or "node_modules" in path.parts
                or any(part.startswith(".") for part in relative.parts)
            ):
                continue
            with self.subTest(path=relative):
                self.assertNotIn(legacy_selector, read(path))


if __name__ == "__main__":
    unittest.main()
