from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "code-review" / "skills" / "diff-summary" / "scripts"
SCRIPT_PATH = SCRIPTS_DIR / "collect_diff_evidence.py"
sys.path.insert(0, str(SCRIPTS_DIR))

import collect_diff_evidence as collector  # noqa: E402


def run(
    *arguments: str, cwd: Path, check: bool = True
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        list(arguments),
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def initialize_repository(repository: Path, attributes: str = "") -> str:
    run("git", "init", "-q", cwd=repository)
    (repository / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    if attributes:
        (repository / ".gitattributes").write_text(attributes, encoding="utf-8")
    run("git", "add", ".", cwd=repository)
    run(
        "git",
        "-c",
        "user.name=Evidence Tests",
        "-c",
        "user.email=evidence@example.invalid",
        "commit",
        "-qm",
        "baseline",
        cwd=repository,
    )
    return run("git", "rev-parse", "HEAD", cwd=repository).stdout.decode().strip()


def commit_all(repository: Path, message: str) -> str:
    run("git", "add", ".", cwd=repository)
    run(
        "git",
        "-c",
        "user.name=Evidence Tests",
        "-c",
        "user.email=evidence@example.invalid",
        "commit",
        "-qm",
        message,
        cwd=repository,
    )
    return run("git", "rev-parse", "HEAD", cwd=repository).stdout.decode().strip()


def write_marker_script(path: Path, body: str) -> Path:
    marker = Path(f"{path}.marker")
    path.write_text(f'#!/bin/sh\n: > "{marker}"\n{body}\n', encoding="utf-8")
    path.chmod(0o755)
    return marker


class EvidenceCollectorTests(unittest.TestCase):
    def test_relative_or_empty_path_entries_cannot_hijack_git_from_repository(
        self,
    ) -> None:
        trusted_git = Path(shutil.which("git") or "").resolve(strict=True)
        for unsafe_component in (".", ""):
            with self.subTest(path_component=unsafe_component or "empty"):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    repository = Path(temporary_directory)
                    initialize_repository(repository)
                    (repository / "tracked.txt").write_text(
                        "changed\n", encoding="utf-8"
                    )
                    local_git = repository / "git"
                    marker = write_marker_script(
                        local_git,
                        f'exec "{trusted_git}" "$@"',
                    )
                    unsafe_path = os.pathsep.join(
                        (unsafe_component, os.environ["PATH"])
                    )

                    with mock.patch.dict(os.environ, {"PATH": unsafe_path}):
                        evidence = collector.collect_evidence(
                            {"kind": "current"}, repository=repository
                        )

                    self.assertFalse(marker.exists())
                    self.assertEqual(Path(evidence["command_argv"][0]), trusted_git)
                    self.assertEqual(evidence["command_argv"][1], "--no-lazy-fetch")
                    self.assertTrue(
                        all(
                            Path(component).is_absolute()
                            for component in evidence["command_environment"][
                                "PATH"
                            ].split(os.pathsep)
                        )
                    )

    def test_absolute_repository_path_entry_cannot_hijack_git(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)
            (repository / "tracked.txt").write_text("changed\n", encoding="utf-8")
            trusted_git = Path(shutil.which("git") or "").resolve(strict=True)
            local_bin = repository / "bin"
            local_bin.mkdir()
            marker = write_marker_script(
                local_bin / "git",
                f'exec "{trusted_git}" "$@"',
            )
            unsafe_path = os.pathsep.join(
                (str(local_bin), str(trusted_git.parent), os.environ["PATH"])
            )

            with mock.patch.dict(os.environ, {"PATH": unsafe_path}):
                evidence = collector.collect_evidence(
                    {"kind": "current"}, repository=repository
                )

        self.assertFalse(marker.exists())
        self.assertEqual(Path(evidence["command_argv"][0]), trusted_git)

    def test_relative_path_cannot_hijack_gh_and_gh_receives_sanitized_routing_env(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            repository = root / "repository"
            repository.mkdir()
            initialize_repository(repository)
            trusted_directory = root / "trusted-bin"
            trusted_directory.mkdir()
            trusted_gh = trusted_directory / "gh"
            trusted_gh.write_text(
                "#!/bin/sh\n"
                'if [ "$2" = diff ]; then\n'
                "  printf 'diff --git a/a.txt b/a.txt\\n'\n"
                "else\n"
                '  printf \'{"files":[],"additions":0,"deletions":0}\'\n'
                "fi\n",
                encoding="utf-8",
            )
            trusted_gh.chmod(0o755)
            local_gh = repository / "gh"
            marker = write_marker_script(local_gh, f'exec "{trusted_gh}" "$@"')
            trusted_git = Path(shutil.which("git") or "").resolve(strict=True)
            unsafe_path = os.pathsep.join(
                (".", str(trusted_directory), str(trusted_git.parent))
            )

            with mock.patch.dict(
                os.environ,
                {
                    "PATH": unsafe_path,
                    "GH_REPO": "attacker/foreign",
                    "GH_FORCE_TTY": "999",
                    "GH_CONFIG_DIR": str(repository),
                },
            ):
                evidence = collector.collect_evidence(
                    {"kind": "pr", "value": 42}, repository=repository
                )

            self.assertFalse(marker.exists())
            self.assertEqual(Path(evidence["command_argv"][0]), trusted_gh.resolve())
            command_environment = evidence["command_environment"]
            self.assertNotIn("GH_REPO", command_environment)
            self.assertNotIn("GH_FORCE_TTY", command_environment)
            self.assertNotIn("GH_CONFIG_DIR", command_environment)
            self.assertEqual(command_environment["GH_PROMPT_DISABLED"], "1")
            self.assertTrue(
                all(
                    Path(component).is_absolute()
                    for component in command_environment["PATH"].split(os.pathsep)
                )
            )

    def test_inherited_git_routing_environment_cannot_redirect_repository_a_to_b(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            repository_a = root / "a"
            repository_b = root / "b"
            repository_a.mkdir()
            repository_b.mkdir()
            initialize_repository(repository_a)
            initialize_repository(repository_b)
            (repository_a / "tracked.txt").write_text("change in A\n", encoding="utf-8")
            (repository_b / "tracked.txt").write_text("foreign B\n", encoding="utf-8")

            with mock.patch.dict(
                os.environ,
                {
                    "GIT_DIR": str(repository_b / ".git"),
                    "GIT_WORK_TREE": str(repository_b),
                    "GIT_COMMON_DIR": str(repository_b / ".git"),
                    "GIT_INDEX_FILE": str(repository_b / ".git" / "index"),
                },
            ):
                evidence = collector.collect_evidence(
                    {"kind": "current"}, repository=repository_a
                )

            self.assertEqual(evidence["repository_root"], str(repository_a.resolve()))
            self.assertIn("change in A", evidence["diff"])
            self.assertNotIn("foreign B", evidence["diff"])

    def test_rejects_foreign_gitdir_indirection_before_collecting_diff(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            victim = root / "victim"
            victim.mkdir()
            initialize_repository(victim)
            attacker = root / "attacker"
            attacker.mkdir()
            (attacker / ".git").write_text(
                f"gitdir: {victim / '.git'}\n",
                encoding="utf-8",
            )

            with self.assertRaises(collector.UnsafeRepositoryError):
                collector.collect_evidence({"kind": "current"}, repository=attacker)

    def test_accepts_a_legitimate_linked_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            primary = root / "primary"
            primary.mkdir()
            initialize_repository(primary)
            linked = root / "linked"
            run(
                "git",
                "worktree",
                "add",
                "-q",
                "-b",
                "linked-test",
                str(linked),
                cwd=primary,
            )
            (linked / "tracked.txt").write_text("linked change\n", encoding="utf-8")

            evidence = collector.collect_evidence(
                {"kind": "current"}, repository=linked
            )

        self.assertEqual(evidence["repository_root"], str(linked.resolve()))
        self.assertIn("linked change", evidence["diff"])

    def test_accepts_a_legitimate_absorbed_submodule_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            source.mkdir()
            initialize_repository(source)
            superproject = root / "superproject"
            superproject.mkdir()
            initialize_repository(superproject)
            run(
                "git",
                "-c",
                "protocol.file.allow=always",
                "submodule",
                "add",
                "-q",
                str(source),
                "module",
                cwd=superproject,
            )
            commit_all(superproject, "add submodule")
            submodule = superproject / "module"
            (submodule / "tracked.txt").write_text(
                "submodule change\n",
                encoding="utf-8",
            )

            evidence = collector.collect_evidence(
                {"kind": "current"}, repository=submodule
            )

        self.assertEqual(evidence["repository_root"], str(submodule.resolve()))
        self.assertIn("submodule change", evidence["diff"])

    def test_rejects_linked_worktree_with_foreign_admin_backlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            primary = root / "primary"
            primary.mkdir()
            initialize_repository(primary)
            linked = root / "linked"
            run(
                "git",
                "worktree",
                "add",
                "-q",
                "-b",
                "linked-test",
                str(linked),
                cwd=primary,
            )
            gitdir_line = (linked / ".git").read_text(encoding="utf-8").strip()
            admin_directory = Path(gitdir_line.removeprefix("gitdir: "))
            (admin_directory / "gitdir").write_text(
                f"{primary / '.git'}\n",
                encoding="utf-8",
            )

            with self.assertRaises(collector.UnsafeRepositoryError):
                collector.collect_evidence({"kind": "current"}, repository=linked)

    def test_rejects_symlinked_object_store_and_ref_inside_ordinary_git_directory(
        self,
    ) -> None:
        for attack in ("objects", "ref"):
            with self.subTest(attack=attack):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    root = Path(temporary_directory)
                    victim = root / "victim"
                    victim.mkdir()
                    initialize_repository(victim)
                    repository = root / "repository"
                    run(
                        "git",
                        "clone",
                        "-q",
                        str(victim),
                        str(repository),
                        cwd=root,
                    )
                    if attack == "objects":
                        shutil.rmtree(repository / ".git" / "objects")
                        (repository / ".git" / "objects").symlink_to(
                            victim / ".git" / "objects",
                            target_is_directory=True,
                        )
                    else:
                        branch = (
                            run(
                                "git",
                                "symbolic-ref",
                                "--short",
                                "HEAD",
                                cwd=repository,
                            )
                            .stdout.decode()
                            .strip()
                        )
                        local_ref = repository / ".git" / "refs" / "heads" / branch
                        victim_ref = victim / ".git" / "refs" / "heads" / branch
                        local_ref.unlink()
                        local_ref.symlink_to(victim_ref)

                    with self.assertRaises(collector.UnsafeRepositoryError):
                        collector.collect_evidence(
                            {"kind": "current"}, repository=repository
                        )

    def test_rejects_nonempty_object_alternates_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            victim = root / "victim"
            victim.mkdir()
            initialize_repository(victim)
            repository = root / "repository"
            repository.mkdir()
            initialize_repository(repository)
            alternates = repository / ".git" / "objects" / "info" / "alternates"
            alternates.parent.mkdir(parents=True, exist_ok=True)
            alternates.write_text(
                f"{victim / '.git' / 'objects'}\n",
                encoding="utf-8",
            )

            with self.assertRaises(collector.UnsafeRepositoryError):
                collector.collect_evidence({"kind": "current"}, repository=repository)

    def test_replace_refs_cannot_forge_commit_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            base = initialize_repository(repository)
            branch = (
                run("git", "symbolic-ref", "--short", "HEAD", cwd=repository)
                .stdout.decode()
                .strip()
            )
            (repository / "tracked.txt").write_text(
                "dangerous_change\n",
                encoding="utf-8",
            )
            real_commit = commit_all(repository, "real change")
            run("git", "checkout", "-qb", "replacement-fixture", base, cwd=repository)
            (repository / "tracked.txt").write_text(
                "benign_change\n",
                encoding="utf-8",
            )
            replacement_commit = commit_all(repository, "replacement change")
            run("git", "checkout", "-q", branch, cwd=repository)
            run("git", "replace", real_commit, replacement_commit, cwd=repository)

            evidence = collector.collect_evidence(
                {"kind": "commit", "value": real_commit},
                repository=repository,
            )

        self.assertIn("dangerous_change", evidence["diff"])
        self.assertNotIn("benign_change", evidence["diff"])
        self.assertIn("--no-replace-objects", evidence["command_argv"])
        self.assertEqual(
            evidence["command_environment"]["GIT_NO_REPLACE_OBJECTS"],
            "1",
        )

    def test_nonempty_legacy_grafts_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            head = initialize_repository(repository)
            grafts = repository / ".git" / "info" / "grafts"
            grafts.write_text(f"{head}\n", encoding="ascii")

            with self.assertRaisesRegex(
                collector.UnsafeRepositoryError,
                "grafts",
            ):
                collector.collect_evidence(
                    {"kind": "commit", "value": head},
                    repository=repository,
                )

    def test_current_scope_collects_exact_views_and_untracked_metadata_only_by_default(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            head = initialize_repository(repository)
            (repository / "tracked.txt").write_text("changed\n", encoding="utf-8")
            (repository / "new feature.txt").write_text(
                "untracked evidence\n", encoding="utf-8"
            )

            evidence = collector.collect_evidence(
                {"kind": "current"}, repository=repository
            )

        self.assertEqual(evidence["scope"], "working")
        self.assertEqual(evidence["repository_root"], str(repository.resolve()))
        self.assertEqual(evidence["head"], head)
        self.assertIn("-baseline", evidence["diff"])
        self.assertIn("+changed", evidence["diff"])
        self.assertIn("tracked.txt", evidence["stat"])
        self.assertRegex(evidence["numstat"], r"(?m)^1\s+1\s+tracked\.txt$")
        self.assertIn("M\ttracked.txt", evidence["name_status"])
        self.assertEqual(
            evidence["untracked"],
            [
                {
                    "path": "new feature.txt",
                    "size": len("untracked evidence\n".encode()),
                    "status": "listed",
                }
            ],
        )
        self.assertEqual(evidence["command_environment"]["GIT_NO_LAZY_FETCH"], "1")
        self.assertEqual(evidence["command_environment"]["GIT_NO_REPLACE_OBJECTS"], "1")
        self.assertEqual(evidence["command_environment"]["GIT_OPTIONAL_LOCKS"], "0")
        self.assertTrue(
            all(
                Path(component).is_absolute()
                for component in evidence["command_environment"]["PATH"].split(
                    os.pathsep
                )
            )
        )
        self.assertTrue(Path(evidence["command_argv"][0]).is_absolute())
        self.assertEqual(Path(evidence["command_argv"][0]).name, "git")
        self.assertEqual(
            evidence["command_argv"][1:7],
            [
                "--no-lazy-fetch",
                "--no-replace-objects",
                "-c",
                "core.fsmonitor=false",
                "--no-pager",
                "diff",
            ],
        )
        for flag in (
            "--no-ext-diff",
            "--no-textconv",
            "--no-color",
            "--submodule=short",
            "--ignore-submodules=dirty",
        ):
            self.assertIn(flag, evidence["command_argv"])
        self.assertIn("GIT_NO_LAZY_FETCH=1", evidence["command"])

    def test_unborn_repository_supports_untracked_current_and_staged_content(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            run("git", "init", "-q", cwd=repository)
            new_file = repository / "new.txt"
            new_file.write_text("untracked\n", encoding="utf-8")

            current = collector.collect_evidence(
                {"kind": "current"}, repository=repository
            )
            self.assertEqual(current["head"], "(unborn)")
            self.assertEqual(current["diff"], "")
            self.assertEqual(current["untracked"][0]["path"], "new.txt")

            run("git", "add", "new.txt", cwd=repository)
            staged = collector.collect_evidence(
                {"kind": "staged"}, repository=repository
            )

        self.assertEqual(staged["head"], "(unborn)")
        self.assertIn("+untracked", staged["diff"])
        self.assertIn("A\tnew.txt", staged["name_status"])

    def test_sha256_unborn_repository_uses_its_native_empty_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialized = run(
                "git",
                "init",
                "-q",
                "--object-format=sha256",
                cwd=repository,
                check=False,
            )
            if initialized.returncode != 0:
                self.skipTest("installed Git does not support SHA-256 repositories")
            (repository / "new.txt").write_text("sha256 unborn\n", encoding="utf-8")
            run("git", "add", "new.txt", cwd=repository)

            current = collector.collect_evidence(
                {"kind": "current"}, repository=repository
            )
            staged = collector.collect_evidence(
                {"kind": "staged"}, repository=repository
            )

        self.assertEqual(current["head"], "(unborn)")
        self.assertEqual(staged["head"], "(unborn)")
        self.assertIn("+sha256 unborn", current["diff"])
        self.assertIn("+sha256 unborn", staged["diff"])
        baseline = current["commands"]["diff"]["command_argv"][-1]
        self.assertRegex(baseline, r"^[0-9a-f]{64}$")

    def test_shared_index_root_enumeration_has_a_count_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            admin = Path(temporary_directory)
            (admin / "one").write_text("one", encoding="utf-8")
            (admin / "two").write_text("two", encoding="utf-8")

            with mock.patch.object(collector, "MAX_ADMIN_TREE_ENTRIES", 1):
                with self.assertRaisesRegex(
                    collector.UnsafeRepositoryError,
                    "administrative scan limit",
                ):
                    collector._validate_matching_admin_files(
                        admin,
                        "sharedindex.",
                        "Git shared index",
                    )

    def test_tree_scopes_override_ignore_submodules_all(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            source.mkdir()
            initialize_repository(source)
            superproject = root / "superproject"
            superproject.mkdir()
            initialize_repository(superproject)
            run(
                "git",
                "-c",
                "protocol.file.allow=always",
                "submodule",
                "add",
                "-q",
                str(source),
                "module",
                cwd=superproject,
            )
            commit_all(superproject, "add submodule")
            (source / "tracked.txt").write_text("next revision\n", encoding="utf-8")
            next_revision = commit_all(source, "advance submodule")
            submodule = superproject / "module"
            run(
                "git",
                "-c",
                "protocol.file.allow=always",
                "fetch",
                "-q",
                "origin",
                cwd=submodule,
            )
            run("git", "checkout", "-q", next_revision, cwd=submodule)
            run("git", "add", "module", cwd=superproject)
            run("git", "config", "diff.ignoreSubmodules", "all", cwd=superproject)

            evidence = collector.collect_evidence(
                {"kind": "staged"}, repository=superproject
            )

        self.assertIn("Subproject commit", evidence["diff"])
        self.assertIn("M\tmodule", evidence["name_status"])
        self.assertIn("--ignore-submodules=none", evidence["command_argv"])

    def test_range_commit_last_n_and_fixed_scopes_use_exact_argv(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            first = initialize_repository(repository)
            (repository / "tracked.txt").write_text("second\n", encoding="utf-8")
            second = commit_all(repository, "second")
            (repository / "tracked.txt").write_text("staged\n", encoding="utf-8")
            run("git", "add", "tracked.txt", cwd=repository)
            (repository / "tracked.txt").write_text("unstaged\n", encoding="utf-8")

            cases = (
                ({"kind": "staged"}, "staged", "diff", "--staged"),
                ({"kind": "unstaged"}, "unstaged", "diff", None),
                ({"kind": "last_commit"}, "HEAD~1..HEAD", "diff", "HEAD~1..HEAD"),
                (
                    {"kind": "last_n", "value": 1},
                    "HEAD~1..HEAD",
                    "diff",
                    "HEAD~1..HEAD",
                ),
                (
                    {"kind": "range", "value": "HEAD~1..HEAD"},
                    "HEAD~1..HEAD",
                    "diff",
                    "HEAD~1..HEAD",
                ),
                (
                    {"kind": "range", "value": "HEAD~1...HEAD"},
                    "HEAD~1...HEAD",
                    "diff",
                    "HEAD~1...HEAD",
                ),
                ({"kind": "commit", "value": second}, second, "show", second),
            )
            for request, expected_scope, subcommand, terminal in cases:
                with self.subTest(request=request):
                    evidence = collector.collect_evidence(
                        request, repository=repository
                    )
                    self.assertEqual(evidence["scope"], expected_scope)
                    self.assertEqual(evidence["command_argv"][6], subcommand)
                    if terminal is not None:
                        self.assertEqual(evidence["command_argv"][-1], terminal)
                    self.assertEqual(evidence["head"], second)
                    self.assertIn(
                        "tracked.txt", evidence["diff"] or evidence["name_status"]
                    )

            commit_evidence = collector.collect_evidence(
                {"kind": "commit", "value": first}, repository=repository
            )
            self.assertIn("baseline", commit_evidence["diff"])
            for flag in ("--raw", "-z", "--patch"):
                self.assertIn(flag, commit_evidence["commands"]["diff"]["command_argv"])
            self.assertIn(
                "--format=fuller",
                commit_evidence["commands"]["commit_metadata"]["command_argv"],
            )
            for metadata_view in ("stat", "numstat", "name_status"):
                metadata_command = commit_evidence["commands"][metadata_view][
                    "command_argv"
                ]
                self.assertIn("--format=", metadata_command)
                self.assertNotIn("--format=fuller", metadata_command)
                self.assertNotIn("commit ", commit_evidence[metadata_view])

    def test_rejects_option_like_control_character_and_invalid_last_n_scopes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)

            invalid_requests = (
                {"kind": "range", "value": "--stat..HEAD"},
                {"kind": "range", "value": "HEAD..bad\nref"},
                {"kind": "range", "value": "HEAD.."},
                {"kind": "commit", "value": "-p"},
                {"kind": "last_n", "value": 0},
                {"kind": "last_n", "value": True},
                {"kind": "last_n", "value": "1;touch-pwn"},
                {"kind": "pr", "value": "1;touch-pwn"},
            )
            for request in invalid_requests:
                with self.subTest(request=request):
                    with self.assertRaises(collector.EvidenceRequestError):
                        collector.collect_evidence(request, repository=repository)

    def test_filter_preflight_rejects_every_filter_triple_before_any_diff_view(
        self,
    ) -> None:
        cases = (
            "tracked.txt filter=attack\n",
            "tracked.txt filter=unspecified\n",
            "tracked.txt filter=unset\n",
            "tracked.txt -filter\n",
        )
        for attributes in cases:
            with self.subTest(attributes=attributes.strip()):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    repository = Path(temporary_directory)
                    initialize_repository(repository, attributes)
                    driver = (
                        attributes.split("=", 1)[1].strip()
                        if "=" in attributes
                        else None
                    )
                    marker = None
                    if driver:
                        script = repository / "filter.sh"
                        marker = write_marker_script(script, "cat")
                        run(
                            "git",
                            "config",
                            f"filter.{driver}.clean",
                            str(script),
                            cwd=repository,
                        )
                    (repository / "tracked.txt").write_text(
                        "changed\n", encoding="utf-8"
                    )
                    calls: list[list[str]] = []
                    original_run = collector._run_process

                    def recording_run(arguments, **kwargs):
                        calls.append([os.fspath(argument) for argument in arguments])
                        return original_run(arguments, **kwargs)

                    with mock.patch.object(
                        collector, "_run_process", side_effect=recording_run
                    ):
                        with self.assertRaises(collector.UnsafeRepositoryError):
                            collector.collect_evidence(
                                {"kind": "current"}, repository=repository
                            )

                    subcommands = [
                        argv[6]
                        for argv in calls
                        if len(argv) > 6 and Path(argv[0]).name == "git"
                    ]
                    self.assertNotIn("status", subcommands)
                    self.assertNotIn("diff", subcommands)
                    self.assertEqual(
                        subcommands,
                        [
                            "rev-parse",
                            "rev-parse",
                            "rev-parse",
                            "rev-parse",
                            "ls-files",
                            "check-attr",
                        ],
                    )
                    if marker is not None:
                        self.assertFalse(marker.exists())

    def test_actual_collector_blocks_external_diff_textconv_and_fsmonitor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository, "tracked.txt diff=attack\n")
            external = repository / "external.sh"
            external_marker = write_marker_script(external, "exit 0")
            textconv = repository / "textconv.sh"
            textconv_marker = write_marker_script(textconv, 'cat "$1"')
            fsmonitor = repository / "fsmonitor.sh"
            fsmonitor_marker = write_marker_script(fsmonitor, "printf 'token\\n'")
            run("git", "config", "diff.external", str(external), cwd=repository)
            run("git", "config", "diff.attack.textconv", str(textconv), cwd=repository)
            run("git", "config", "core.fsmonitor", str(fsmonitor), cwd=repository)
            (repository / "tracked.txt").write_text("changed\n", encoding="utf-8")

            evidence = collector.collect_evidence(
                {"kind": "current"}, repository=repository
            )

            self.assertIn("tracked.txt", evidence["diff"])
            for marker in (external_marker, textconv_marker, fsmonitor_marker):
                with self.subTest(marker=marker.name):
                    self.assertFalse(marker.exists())

    def test_sensitive_tracked_path_is_blocked_by_name_only_scan_before_content_diff(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)
            (repository / ".env.local").write_text(
                "TOKEN=committed-secret\n",
                encoding="utf-8",
            )
            secret_commit = commit_all(repository, "add secret store")
            (repository / ".env.local").write_text(
                "TOKEN=working-secret\n",
                encoding="utf-8",
            )
            run("git", "add", ".env.local", cwd=repository)

            requests = (
                {"kind": "current"},
                {"kind": "staged"},
                {"kind": "last_commit"},
                {"kind": "range", "value": "HEAD~1..HEAD"},
                {"kind": "commit", "value": secret_commit},
            )
            original_run = collector._run_recorded_git
            for request in requests:
                with self.subTest(request=request):
                    calls: list[list[str]] = []

                    def recording_run(execution, root, arguments):
                        calls.append(list(arguments))
                        return original_run(execution, root, arguments)

                    with mock.patch.object(
                        collector,
                        "_run_recorded_git",
                        side_effect=recording_run,
                    ):
                        with self.assertRaises(
                            collector.UnsafeRepositoryError
                        ) as raised:
                            collector.collect_evidence(request, repository=repository)

                    self.assertNotIn("committed-secret", str(raised.exception))
                    self.assertNotIn("working-secret", str(raised.exception))
                    self.assertEqual(len(calls), 1)
                    self.assertIn("--name-only", calls[0])
                    self.assertIn("-z", calls[0])

    def test_tracked_env_example_diff_is_collected_as_public_template(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)
            (repository / ".env.example").write_text(
                "API_TOKEN=replace-me\n",
                encoding="utf-8",
            )
            run("git", "add", ".env.example", cwd=repository)

            evidence = collector.collect_evidence(
                {"kind": "current"}, repository=repository
            )

        self.assertIn(".env.example", evidence["diff"])
        self.assertIn("API_TOKEN=replace-me", evidence["diff"])

    def test_env_example_exception_preserves_other_sensitive_path_rules(self) -> None:
        for safe_path in (".env.example", "deploy/.ENV.EXAMPLE"):
            with self.subTest(path=safe_path):
                self.assertFalse(collector._is_sensitive_path(safe_path))

        for sensitive_path in (
            ".env",
            ".env.local",
            ".envrc",
            ".env.example.local",
            ".env.example/actual.env",
            "secrets/.env.example",
        ):
            with self.subTest(path=sensitive_path):
                self.assertTrue(collector._is_sensitive_path(sensitive_path))

    def test_sensitive_rename_source_is_blocked_for_worktree_range_and_commit_scopes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)
            (repository / ".env").write_text(
                "SECRET=committed-secret\n",
                encoding="utf-8",
            )
            before_rename = commit_all(repository, "add sensitive source")
            run("git", "mv", ".env", "safe.txt", cwd=repository)
            (repository / "safe.txt").write_text(
                "PUBLIC=renamed\n",
                encoding="utf-8",
            )
            run("git", "add", "safe.txt", cwd=repository)

            for request in ({"kind": "current"}, {"kind": "staged"}):
                with self.subTest(request=request):
                    with self.assertRaisesRegex(
                        collector.UnsafeRepositoryError,
                        "sensitive",
                    ) as raised:
                        collector.collect_evidence(request, repository=repository)
                    self.assertNotIn("committed-secret", str(raised.exception))

            after_rename = commit_all(repository, "rename sensitive source")
            for request in (
                {"kind": "range", "value": f"{before_rename}..{after_rename}"},
                {"kind": "commit", "value": after_rename},
            ):
                with self.subTest(request=request):
                    with self.assertRaisesRegex(
                        collector.UnsafeRepositoryError,
                        "sensitive",
                    ) as raised:
                        collector.collect_evidence(request, repository=repository)
                    self.assertNotIn("committed-secret", str(raised.exception))

    def test_captured_patch_paths_are_rechecked_after_name_preflight(self) -> None:
        repository = Path("/tmp/repository")
        safe_scan = "safe.txt\0"
        sensitive_raw_patch = (
            b":100644 100644 aaaaaaa bbbbbbb R090\0.env\0safe.txt\0\0"
            b"diff --git a/.env b/safe.txt\n"
            b"--- a/.env\n"
            b"+++ b/safe.txt\n"
            b"@@ -1 +1 @@\n"
            b"-SECRET=must-not-escape\n"
            b"+PUBLIC=safe\n"
        )

        def changing_git(execution, root, arguments):
            if "--name-only" in arguments:
                return safe_scan
            return ""

        execution = collector.ExecutionContext(
            git="/usr/bin/git",
            gh=None,
            path="/usr/bin",
        )
        with (
            mock.patch.object(
                collector,
                "_run_recorded_git",
                side_effect=changing_git,
            ),
            mock.patch.object(
                collector,
                "_run_recorded_git_bytes",
                return_value=sensitive_raw_patch,
            ),
        ):
            with self.assertRaisesRegex(
                collector.UnsafeRepositoryError,
                "sensitive",
            ) as raised:
                collector._collect_git_scope(
                    execution=execution,
                    repository=repository,
                    head="a" * 40,
                    scope="staged",
                    terminal_arguments=("--staged",),
                    reads_worktree=False,
                )

        self.assertNotIn("must-not-escape", str(raised.exception))

    def test_default_prefix_and_raw_paths_support_spaces_despite_repository_config(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)
            spaced = repository / "space name.txt"
            spaced.write_text("before\n", encoding="utf-8")
            commit_all(repository, "add spaced path")
            run("git", "config", "diff.noprefix", "true", cwd=repository)
            run("git", "config", "diff.srcPrefix", "hostile-old/", cwd=repository)
            run("git", "config", "diff.dstPrefix", "hostile-new/", cwd=repository)
            spaced.write_text("after\n", encoding="utf-8")

            evidence = collector.collect_evidence(
                {"kind": "current"}, repository=repository
            )

        self.assertIn("diff --git a/space name.txt b/space name.txt", evidence["diff"])
        self.assertIn("-before", evidence["diff"])
        self.assertIn("+after", evidence["diff"])
        self.assertIn("--default-prefix", evidence["commands"]["diff"]["command_argv"])

    def test_process_timeout_and_output_caps_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable_path = collector._sanitized_executable_path()
            timeout_script = root / "timeout.sh"
            write_marker_script(timeout_script, "sleep 1")
            with mock.patch.object(
                collector,
                "COMMAND_TIMEOUT_SECONDS",
                0.05,
                create=True,
            ):
                with self.assertRaisesRegex(
                    collector.EvidenceCommandError,
                    "timed out",
                ):
                    collector._run_process(
                        [str(timeout_script)],
                        cwd=root,
                        environment={},
                        executable_path=executable_path,
                    )

            for stream in ("stdout", "stderr"):
                with self.subTest(stream=stream):
                    output_script = root / f"{stream}.sh"
                    redirection = "" if stream == "stdout" else " >&2"
                    write_marker_script(
                        output_script,
                        f"i=0; while [ $i -lt 1024 ]; do printf x{redirection}; "
                        "i=$((i + 1)); done",
                    )
                    attempts = 50 if stream == "stdout" else 1
                    for attempt in range(attempts):
                        with self.subTest(stream=stream, attempt=attempt):
                            with mock.patch.object(
                                collector,
                                "MAX_STDOUT_BYTES"
                                if stream == "stdout"
                                else "MAX_STDERR_BYTES",
                                128,
                                create=True,
                            ):
                                with self.assertRaisesRegex(
                                    collector.EvidenceCommandError,
                                    f"{stream} limit",
                                ):
                                    collector._run_process(
                                        [str(output_script)],
                                        cwd=root,
                                        environment={},
                                        executable_path=executable_path,
                                    )

    def test_actual_collector_rejects_diff_larger_than_stdout_cap(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)
            (repository / "tracked.txt").write_text("x" * 4096, encoding="utf-8")

            with mock.patch.object(
                collector,
                "MAX_STDOUT_BYTES",
                512,
                create=True,
            ):
                with self.assertRaisesRegex(
                    collector.EvidenceCommandError,
                    "stdout limit",
                ):
                    collector.collect_evidence(
                        {"kind": "current"}, repository=repository
                    )

    def test_actual_collector_fails_closed_without_invoking_lazy_fetch_remote_helper(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            source.mkdir()
            initialize_repository(source)
            origin = root / "origin.git"
            run("git", "clone", "-q", "--bare", str(source), str(origin), cwd=root)
            run("git", "config", "uploadpack.allowFilter", "true", cwd=origin)
            repository = root / "partial"
            run(
                "git",
                "clone",
                "-q",
                "--filter=blob:none",
                "--no-checkout",
                f"file://{origin}",
                str(repository),
                cwd=root,
            )

            helper_directory = root / "bin"
            helper_directory.mkdir()
            helper = helper_directory / "git-remote-attack"
            marker = write_marker_script(helper, "exit 1")
            run("git", "config", "remote.origin.url", "attack::missing", cwd=repository)

            with mock.patch.dict(
                os.environ,
                {"PATH": f"{helper_directory}{os.pathsep}{os.environ['PATH']}"},
            ):
                with self.assertRaises(collector.EvidenceCommandError):
                    collector.collect_evidence(
                        {"kind": "commit", "value": "HEAD"},
                        repository=repository,
                    )

            self.assertFalse(marker.exists())

    def test_pr_diff_survives_metadata_lookup_failure_with_a_recorded_limitation(
        self,
    ) -> None:
        repository = Path("/tmp/repository")
        diff = b"diff --git a/a.txt b/a.txt\n"

        def fake_process(arguments, **kwargs):
            if Path(arguments[0]).name == "gh" and list(arguments[1:3]) == [
                "pr",
                "diff",
            ]:
                if "--name-only" in arguments:
                    return subprocess.CompletedProcess(arguments, 0, b"a.txt\n", b"")
                return subprocess.CompletedProcess(arguments, 0, diff, b"")
            if Path(arguments[0]).name == "gh" and list(arguments[1:3]) == [
                "pr",
                "view",
            ]:
                return subprocess.CompletedProcess(
                    arguments,
                    1,
                    b"",
                    b"metadata unavailable\n",
                )
            self.fail(f"unexpected process: {arguments}")

        with (
            mock.patch.object(
                collector,
                "_repository_context",
                return_value=(repository, "a" * 40),
            ),
            mock.patch.object(collector, "_run_process", side_effect=fake_process),
        ):
            evidence = collector.collect_evidence(
                {"kind": "pr", "value": 42}, repository=repository
            )

        self.assertEqual(evidence["diff"], diff.decode())
        self.assertEqual(evidence["pr_metadata"], None)
        self.assertEqual(evidence["stat"], "")
        self.assertEqual(evidence["numstat"], "")
        self.assertEqual(evidence["name_status"], "")
        self.assertEqual(len(evidence["limitations"]), 1)
        self.assertIn("metadata unavailable", evidence["limitations"][0])

    def test_pr_sensitive_path_is_blocked_before_patch_download(self) -> None:
        repository = Path("/tmp/repository")
        calls: list[list[str]] = []

        def fake_process(arguments, **kwargs):
            calls.append(list(arguments))
            if "--name-only" in arguments:
                return subprocess.CompletedProcess(
                    arguments, 0, b".env.production\n", b""
                )
            self.fail(
                f"collector downloaded PR content before path safety: {arguments}"
            )

        with (
            mock.patch.object(
                collector,
                "_repository_context",
                return_value=(repository, "a" * 40),
            ),
            mock.patch.object(collector, "_run_process", side_effect=fake_process),
        ):
            with self.assertRaisesRegex(
                collector.UnsafeRepositoryError,
                "sensitive",
            ):
                collector.collect_evidence(
                    {"kind": "pr", "value": 42}, repository=repository
                )

        self.assertEqual(len(calls), 1)
        self.assertIn("--name-only", calls[0])

    def test_pr_sensitive_rename_source_is_blocked_from_the_captured_patch(
        self,
    ) -> None:
        repository = Path("/tmp/repository")
        calls: list[list[str]] = []
        patch = (
            b"diff --git a/.env b/safe.txt\n"
            b"similarity index 90%\n"
            b"rename from .env\n"
            b"rename to safe.txt\n"
            b"--- a/.env\n"
            b"+++ b/safe.txt\n"
            b"@@ -1 +1 @@\n"
            b"-SECRET=must-not-escape\n"
            b"+PUBLIC=safe\n"
        )

        def fake_process(arguments, **kwargs):
            calls.append(list(arguments))
            if "--name-only" in arguments:
                return subprocess.CompletedProcess(arguments, 0, b"safe.txt\n", b"")
            if list(arguments[1:3]) == ["pr", "diff"]:
                return subprocess.CompletedProcess(arguments, 0, patch, b"")
            self.fail(f"metadata must not run after a sensitive patch: {arguments}")

        with (
            mock.patch.object(
                collector,
                "_repository_context",
                return_value=(repository, "a" * 40),
            ),
            mock.patch.object(collector, "_run_process", side_effect=fake_process),
        ):
            with self.assertRaisesRegex(
                collector.UnsafeRepositoryError,
                "sensitive",
            ) as raised:
                collector.collect_evidence(
                    {"kind": "pr", "value": 42}, repository=repository
                )

        self.assertEqual(len(calls), 2)
        self.assertNotIn("must-not-escape", str(raised.exception))

    def test_pr_diff_header_paths_cover_mode_only_changes_and_reject_bad_escapes(
        self,
    ) -> None:
        paths = collector._pr_patch_paths(
            b"diff --git a/.env b/.env\nold mode 100644\nnew mode 100755\n"
        )
        self.assertEqual(paths, [".env", ".env"])
        with self.assertRaisesRegex(
            collector.UnsafeRepositoryError,
            "sensitive",
        ):
            collector._reject_sensitive_paths(paths, "PR patch")

        with self.assertRaisesRegex(
            collector.EvidenceCommandError,
            "invalid octal escape",
        ):
            collector._pr_patch_paths(b'diff --git "a/\\777.env" "b/\\777.env"\n')

    def test_every_git_process_uses_hardened_environment_prefix_and_no_shell(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)
            (repository / "tracked.txt").write_text("changed\n", encoding="utf-8")
            original_popen = collector.subprocess.Popen
            calls: list[tuple[list[str], dict]] = []

            def recording_popen(arguments, **kwargs):
                calls.append(([os.fspath(argument) for argument in arguments], kwargs))
                return original_popen(arguments, **kwargs)

            with (
                mock.patch.dict(
                    os.environ,
                    {
                        "GIT_TRACE": str(repository / "trace.log"),
                        "GIT_EXTERNAL_DIFF": str(repository / "external-diff"),
                    },
                ),
                mock.patch.object(
                    collector.subprocess,
                    "Popen",
                    side_effect=recording_popen,
                ),
            ):
                collector.collect_evidence({"kind": "current"}, repository=repository)

            self.assertFalse((repository / "trace.log").exists())

        self.assertTrue(calls)
        for argv, kwargs in calls:
            with self.subTest(argv=argv):
                self.assertEqual(
                    argv[1:6],
                    [
                        "--no-lazy-fetch",
                        "--no-replace-objects",
                        "-c",
                        "core.fsmonitor=false",
                        "--no-pager",
                    ],
                )
                self.assertTrue(Path(argv[0]).is_absolute())
                self.assertEqual(Path(argv[0]).name, "git")
                self.assertEqual(kwargs["env"]["GIT_NO_LAZY_FETCH"], "1")
                self.assertEqual(kwargs["env"]["GIT_NO_REPLACE_OBJECTS"], "1")
                self.assertEqual(kwargs["env"]["GIT_OPTIONAL_LOCKS"], "0")
                for removed in (
                    "GIT_DIR",
                    "GIT_WORK_TREE",
                    "GIT_COMMON_DIR",
                    "GIT_INDEX_FILE",
                    "GIT_OBJECT_DIRECTORY",
                    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                    "GIT_NAMESPACE",
                    "GIT_CONFIG_COUNT",
                    "GIT_CONFIG_PARAMETERS",
                    "GIT_TRACE",
                    "GIT_EXTERNAL_DIFF",
                ):
                    self.assertNotIn(removed, kwargs["env"])
                self.assertTrue(
                    all(
                        Path(component).is_absolute()
                        for component in kwargs["env"]["PATH"].split(os.pathsep)
                    )
                )
                self.assertFalse(kwargs.get("shell", False))
        self.assertNotIn("status", [argv[6] for argv, _ in calls])

    def test_untracked_inspection_skips_sensitive_binary_oversized_and_symlink_paths(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)
            (repository / ".env.example").write_text(
                "API_TOKEN=replace-me\n",
                encoding="utf-8",
            )
            (repository / ".env.local").write_text("TOKEN=secret\n", encoding="utf-8")
            (repository / ".envrc").write_text("TOKEN=secret\n", encoding="utf-8")
            (repository / "binary.dat").write_bytes(b"prefix\0binary")
            (repository / "large.txt").write_bytes(b"x" * (256 * 1024 + 1))
            (repository / "safe.txt").write_text("safe\n", encoding="utf-8")
            (repository / ".docker").mkdir()
            (repository / ".docker" / "config.json").write_text(
                '{"auths":{"registry":{"auth":"secret"}}}\n',
                encoding="utf-8",
            )
            (repository / ".kube").mkdir()
            (repository / ".kube" / "config").write_text(
                "users:\n- token: secret\n",
                encoding="utf-8",
            )
            (repository / "terraform.tfstate").write_text(
                '{"resources":[{"secret":"value"}]}\n',
                encoding="utf-8",
            )
            if hasattr(os, "symlink"):
                (repository / "linked.txt").symlink_to("safe.txt")

            evidence = collector.collect_evidence(
                {
                    "kind": "current",
                    "include_untracked": [
                        ".env.example",
                        ".env.local",
                        ".envrc",
                        "binary.dat",
                        "large.txt",
                        "safe.txt",
                        ".docker/config.json",
                        ".kube/config",
                        "terraform.tfstate",
                        "linked.txt",
                    ],
                },
                repository=repository,
            )

        by_path = {entry["path"]: entry for entry in evidence["untracked"]}
        self.assertEqual(by_path["safe.txt"]["content"], "safe\n")
        self.assertEqual(
            by_path[".env.example"]["content"],
            "API_TOKEN=replace-me\n",
        )
        self.assertEqual(by_path[".env.local"]["status"], "skipped")
        self.assertEqual(by_path[".env.local"]["reason"], "sensitive path")
        self.assertEqual(by_path[".envrc"]["reason"], "sensitive path")
        self.assertEqual(by_path["binary.dat"]["reason"], "binary content")
        self.assertEqual(by_path["large.txt"]["reason"], "file exceeds 256 KiB")
        for path in (
            ".docker/config.json",
            ".kube/config",
            "terraform.tfstate",
        ):
            self.assertEqual(by_path[path]["status"], "skipped")
            self.assertEqual(by_path[path]["reason"], "sensitive path")

        if "linked.txt" in by_path:
            self.assertEqual(by_path["linked.txt"]["reason"], "symlink")
        for path in (
            ".env.local",
            ".envrc",
            "binary.dat",
            "large.txt",
            ".docker/config.json",
            ".kube/config",
            "terraform.tfstate",
            "linked.txt",
        ):
            if path in by_path:
                self.assertNotIn("content", by_path[path])

    def test_untracked_path_count_is_bounded_before_filesystem_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)
            (repository / "one.txt").write_text("one\n", encoding="utf-8")
            (repository / "two.txt").write_text("two\n", encoding="utf-8")

            with mock.patch.object(collector, "MAX_UNTRACKED_PATHS", 1):
                with self.assertRaisesRegex(
                    collector.UnsafeRepositoryError,
                    "path limit",
                ):
                    collector.collect_evidence(
                        {"kind": "current"}, repository=repository
                    )

    def test_include_untracked_requires_an_exact_present_path_and_worktree_scope(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)
            (repository / "safe.txt").write_text("safe\n", encoding="utf-8")

            invalid_requests = (
                {"kind": "current", "include_untracked": "safe.txt"},
                {"kind": "current", "include_untracked": ["missing.txt"]},
                {"kind": "current", "include_untracked": ["../safe.txt"]},
                {"kind": "staged", "include_untracked": ["safe.txt"]},
            )
            for request in invalid_requests:
                with self.subTest(request=request):
                    with self.assertRaises(collector.EvidenceRequestError):
                        collector.collect_evidence(request, repository=repository)

    def test_include_untracked_has_linear_count_and_aggregate_content_bounds(
        self,
    ) -> None:
        with mock.patch.object(collector, "MAX_INCLUDED_UNTRACKED_PATHS", 1):
            with self.assertRaisesRegex(
                collector.EvidenceRequestError,
                "path limit",
            ):
                collector._validate_include_untracked(
                    {"include_untracked": ["one.txt", "two.txt"]},
                    "current",
                )

        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)
            (repository / "one.txt").write_text("123456\n", encoding="utf-8")
            (repository / "two.txt").write_text("abcdef\n", encoding="utf-8")
            with mock.patch.object(collector, "MAX_INCLUDED_UNTRACKED_BYTES", 10):
                with self.assertRaisesRegex(
                    collector.UnsafeRepositoryError,
                    "aggregate byte limit",
                ):
                    collector.collect_evidence(
                        {
                            "kind": "current",
                            "include_untracked": ["one.txt", "two.txt"],
                        },
                        repository=repository,
                    )

    def test_cli_reads_dynamic_request_from_json_stdin_and_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            initialize_repository(repository)
            (repository / "tracked.txt").write_text("changed\n", encoding="utf-8")
            commit_all(repository, "changed")
            request = {
                "repository": str(repository),
                "scope": {"kind": "range", "value": "HEAD~1..HEAD"},
            }
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH)],
                input=json.dumps(request),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        evidence = json.loads(result.stdout)
        self.assertEqual(evidence["scope"], "HEAD~1..HEAD")
        self.assertEqual(evidence["command_argv"][-1], "HEAD~1..HEAD")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
