import importlib.util
import json
import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "swarm" / "skills" / "swarm" / "scripts" / "swarm.py"

SPEC = importlib.util.spec_from_file_location("swarm_helper", SCRIPT)
assert SPEC and SPEC.loader
swarm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(swarm)


def write_executable(directory: Path, name: str, body: str) -> None:
    path = directory / name
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


CLAUDE = """#!/bin/sh
if [ "$1" = "--version" ]; then echo "2.1.0"; exit 0; fi
if [ "$1" = "auth" ]; then echo '{"loggedIn":true}'; exit 0; fi
cat >/dev/null
if [ -n "$GUARD_TOUCH" ]; then echo changed > "$GUARD_TOUCH"; fi
echo '{"result":"reviewed","is_error":false,"session_id":"sess-1"}'
"""

CODEX = """#!/bin/sh
if [ "$1" = "--version" ]; then echo "codex 1.2.3"; exit 0; fi
if [ "$1" = "login" ]; then echo "Logged in using ChatGPT"; exit 0; fi
exit 0
"""

OPENCODE_OLD = """#!/bin/sh
if [ "$1" = "--version" ]; then echo "1.9.0"; exit 0; fi
exit 0
"""

OPENCODE_NEW = """#!/bin/sh
if [ "$1" = "--version" ]; then echo "2.1.0"; exit 0; fi
if [ "$1" = "auth" ]; then exit 0; fi
exit 0
"""


def step(task_id: str, route_id: str, vendor: str, **extra: object) -> dict:
    payload = {
        "task_id": task_id,
        "route_id": route_id,
        "vendor": vendor,
        "vision": False,
        "rationale": "Code review fits this authenticated model and the weekly bucket still has room.",
        "quota_note": "unknown",
        "fallbacks": [],
    }
    payload.update(extra)
    return payload


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self._path = os.environ.get("PATH")

    def tearDown(self) -> None:
        if self._path is None:
            os.environ.pop("PATH", None)
        else:
            os.environ["PATH"] = self._path

    def test_old_opencode_is_not_usable_and_one_agent_is_not_heterogeneous(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            bin_dir = Path(raw)
            write_executable(bin_dir, "claude", CLAUDE)
            write_executable(bin_dir, "opencode", OPENCODE_OLD)
            os.environ["PATH"] = str(bin_dir)
            payload = swarm.probe_agents(True)
        by_agent = {item["agent"]: item for item in payload["agents"]}
        self.assertTrue(by_agent["claude-code"]["usable"])
        self.assertTrue(by_agent["claude-code"]["auth_ok"])
        self.assertFalse(by_agent["opencode"]["usable"])
        self.assertFalse(payload["heterogeneous"])

    def test_plan_rejects_a_shared_vendor_and_an_invented_quota(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "usage.txt"
            source.write_text("Current week (all models): 12% used\n", encoding="utf-8")
            plan = {
                "task": "code_review",
                "steps": [
                    step("one", "claude-code/anthropic/claude-opus", "anthropic"),
                    step("two", "codex/openai/gpt", "anthropic"),
                ],
            }
            errors = swarm.validate_plan(plan, None)
            self.assertTrue(any("different vendors" in error for error in errors))

            invented = {
                "task": "code_review",
                "steps": [
                    step(
                        "one",
                        "claude-code/anthropic/claude-opus",
                        "anthropic",
                        quota_note="weekly 40% used",
                        quota_source=str(source),
                    )
                ],
            }
            errors = swarm.validate_plan(invented, None)
            self.assertTrue(any("quota_note" in error for error in errors))

            copied = {
                "task": "code_review",
                "steps": [
                    step(
                        "one",
                        "claude-code/anthropic/claude-opus",
                        "anthropic",
                        quota_note="weekly 12% used",
                        quota_source=str(source),
                    )
                ],
            }
            self.assertEqual([], swarm.validate_plan(copied, None))

    def test_invocation_postures_match_the_cli_contract(self) -> None:
        claude = swarm.build_invocation(
            {
                "agent": "claude-code",
                "binary": "claude",
                "model": "claude-opus",
                "provider": "anthropic",
                "sandbox": "read-only",
                "no_tools": True,
                "prompt": "review",
            }
        )
        self.assertIn("--tools", claude["argv"])
        self.assertIn("--no-session-persistence", claude["argv"])
        self.assertTrue(claude["tools_enforced"])

        codex = swarm.build_invocation(
            {
                "agent": "codex",
                "binary": "codex",
                "model": "gpt",
                "provider": "openai",
                "sandbox": "read-only",
                "prompt": "review",
                "output_file": "out.md",
            }
        )
        self.assertEqual(codex["argv"][:4], ["codex", "--no-daemon", "exec", "--ephemeral"])
        self.assertIn('sandbox_mode="read-only"', codex["argv"])
        self.assertFalse(codex["tools_enforced"])
        self.assertEqual(codex["argv"][-1], "-")

        opencode = swarm.build_invocation(
            {
                "agent": "opencode",
                "binary": "opencode",
                "model": "deepseek-flash",
                "provider": "deepseek",
                "sandbox": "read-only",
                "prompt": "review",
            }
        )
        self.assertIn("plan", opencode["argv"])
        self.assertNotIn("--auto", opencode["argv"])
        self.assertIn("OPENCODE_CONFIG_CONTENT", opencode["env"])

        agy = swarm.build_invocation(
            {
                "agent": "antigravity",
                "binary": "agy",
                "model": "gemini",
                "provider": "google",
                "sandbox": "read-only",
                "add_dirs": ["/tmp/outside"],
                "prompt": "look",
            }
        )
        self.assertEqual(agy["argv"][-2:], ["--print", ""])
        self.assertLess(agy["argv"].index("--add-dir"), agy["argv"].index("--print"))
        event = json.loads(agy["stdin"])
        self.assertEqual(event["message"]["content"], "look")

    def test_parsers_do_not_treat_the_answer_as_a_quota_failure(self) -> None:
        parsed = swarm.parse_claude(
            'warning: brace {not json}\n{"result":"first","is_error":false}\n{"result":"final answer","is_error":false,"session_id":"s"}'
        )
        self.assertEqual("final answer", parsed["text"])
        self.assertIsNone(
            swarm.classify_failure(0, "test output mentioned 429 inside the model answer", parsed)
        )
        self.assertEqual(
            "quota",
            swarm.classify_failure(1, "HTTP 429 quota exceeded", {"text": ""}),
        )
        agy = swarm.parse_agy(
            '{"event":"result","result":{"status":"SUCCESS","response":""}}',
            'jetski: no output produced — auto-denied',
        )
        self.assertEqual("permission", swarm.classify_failure(0, "jetski: auto-denied", agy))
        usage = swarm.parse_claude_usage("no table here")
        self.assertEqual("unknown", usage["status"])

    def test_run_writes_the_result_and_redacts_secrets(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bin_dir = root / "bin"
            repo = root / "repo"
            cache = root / "cache"
            bin_dir.mkdir()
            repo.mkdir()
            write_executable(bin_dir, "claude", CLAUDE)
            write_executable(bin_dir, "codex", CODEX)
            os.environ["PATH"] = str(bin_dir) + os.pathsep + (self._path or "")
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
            env = {
                **os.environ,
                "GIT_AUTHOR_NAME": "Test",
                "GIT_AUTHOR_EMAIL": "t@example.com",
                "GIT_COMMITTER_NAME": "Test",
                "GIT_COMMITTER_EMAIL": "t@example.com",
            }
            (repo / "keep.txt").write_text("a\n", encoding="utf-8")
            subprocess.run(["git", "add", "keep.txt"], cwd=repo, check=True, env=env)
            subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, env=env, capture_output=True)
            probe_code = swarm.main(["--cache-dir", str(cache), "probe", "--check-auth", "--json"])
            self.assertEqual(0, probe_code)
            plan = {
                "task": "code_review",
                "steps": [
                    step(
                        "review",
                        "claude-code/anthropic/claude-opus",
                        "anthropic",
                        rationale="Code review fits Claude and the weekly bucket still has room. api_key=supersecretvalue",
                    )
                ],
            }
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            plan_code = swarm.main(
                ["--cache-dir", str(cache), "plan", "--run-id", "run1", "--file", str(plan_path)]
            )
            self.assertEqual(0, plan_code, "plan should accept an authenticated Claude route")
            saved = (cache / "runs" / "run1" / "plan.json").read_text(encoding="utf-8")
            self.assertNotIn("supersecretvalue", saved)
            prompt = root / "task.md"
            prompt.write_text("Review keep.txt.\n", encoding="utf-8")
            dry = swarm.main(
                [
                    "--cache-dir",
                    str(cache),
                    "run",
                    "--run-id",
                    "run1",
                    "--task-id",
                    "review",
                    "--prompt-file",
                    str(prompt),
                    "--cwd",
                    str(repo),
                    "--sandbox",
                    "read-only",
                    "--dry-run",
                ]
            )
            self.assertEqual(0, dry)
            code = swarm.main(
                [
                    "--cache-dir",
                    str(cache),
                    "run",
                    "--run-id",
                    "run1",
                    "--task-id",
                    "review",
                    "--prompt-file",
                    str(prompt),
                    "--cwd",
                    str(repo),
                    "--sandbox",
                    "read-only",
                    "--write-set",
                    "keep.txt",
                ]
            )
            self.assertEqual(0, code)
            result = (cache / "runs" / "run1" / "review" / "result.md").read_text(encoding="utf-8")
            self.assertIn("reviewed", result)
            meta = json.loads((cache / "runs" / "run1" / "review" / "meta.json").read_text(encoding="utf-8"))
            self.assertEqual("ok", meta["status"])
            self.assertTrue(meta["write_set_ok"])
            self.assertEqual("Claude Code", meta["official_agent"])

            os.environ["GUARD_TOUCH"] = str(repo / "sneak.txt")
            guarded = swarm.main(
                [
                    "--cache-dir",
                    str(cache),
                    "run",
                    "--run-id",
                    "run1",
                    "--task-id",
                    "review",
                    "--prompt-file",
                    str(prompt),
                    "--cwd",
                    str(repo),
                    "--sandbox",
                    "read-only",
                    "--guard",
                ]
            )
            os.environ.pop("GUARD_TOUCH", None)
            self.assertEqual(1, guarded)
            guarded_meta = json.loads(
                (cache / "runs" / "run1" / "review" / "meta.json").read_text(encoding="utf-8")
            )
            self.assertEqual("mutated", guarded_meta["error_class"])

            mark = swarm.main(
                [
                    "--cache-dir",
                    str(cache),
                    "mark",
                    "--run-id",
                    "run1",
                    "--task-id",
                    "review",
                    "--insignificant",
                    "--outcome-summary",
                    "No actionable issues.",
                ]
            )
            self.assertEqual(0, mark)
            report = swarm.main(
                ["--cache-dir", str(cache), "report", "--run-id", "run1", "--only-significant"]
            )
            self.assertEqual(0, report)
            shown = (cache / "runs" / "run1" / "report.md").read_text(encoding="utf-8")
            self.assertIn("No tasks recorded.", shown)

    def test_new_opencode_is_usable(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            bin_dir = Path(raw)
            write_executable(bin_dir, "opencode", OPENCODE_NEW)
            write_executable(bin_dir, "codex", CODEX)
            os.environ["PATH"] = str(bin_dir)
            payload = swarm.probe_agents(True)
        self.assertTrue(payload["heterogeneous"])
        self.assertIn("opencode", payload["usable_agents"])
        self.assertIn("codex", payload["usable_agents"])


if __name__ == "__main__":
    unittest.main()
