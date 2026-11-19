#!/usr/bin/env python3
"""Probe coding-agent CLIs, check a route plan, run one delegated task, and report the call tree.

The script never reads credential files and never sends traffic of its own.
A claimed quota figure must be copied from a command transcript on disk.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


SCHEMA_VERSION = 1
AGENTS = {
    "codex": {"binary": "codex", "official": "Codex"},
    "claude-code": {"binary": "claude", "official": "Claude Code"},
    "opencode": {"binary": "opencode", "official": "OpenCode"},
    "antigravity": {"binary": "agy", "official": "Antigravity"},
}
TASKS = {
    "code_review",
    "security_audit",
    "architecture",
    "debugging",
    "ui_debugging",
    "frontend",
    "code_generation",
    "refactoring",
    "testing",
    "prose",
    "documentation",
    "survey",
    "general",
}
SANDBOXES = {"read-only", "workspace-write", "bypass"}
SPEEDS = {"normal", "fast", "urgent"}
FALLBACK_OK = {"quota", "auth", "unavailable"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")
ROUTE_RE = re.compile(
    r"^(codex|claude-code|opencode|antigravity)/([a-z0-9][a-z0-9._-]*)/([A-Za-z0-9][A-Za-z0-9._-]*)$"
)
EFFORT_RE = re.compile(r"-(?:low|medium|high|xhigh|max)$")
SEMVER_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")
SECRET_RE = re.compile(
    r"""(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|authorization|bearer|sk-[A-Za-z0-9]{8,})\b\s*[:=]\s*[^\s"'\\,;}]+"""
)
MAX_STEPS = 4
PROMPT_WARN = 8000

__all__ = [
    "build_invocation",
    "classify_failure",
    "official_model_id",
    "parse_agy",
    "parse_claude",
    "parse_claude_usage",
    "parse_codex",
    "parse_opencode",
    "probe_agents",
    "quota_note_supported",
    "validate_plan",
]


def scrub(text: str) -> str:
    return SECRET_RE.sub(lambda match: f"{match.group(1)}=[redacted]", text)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(scrub(text), encoding="utf-8")
    temporary.replace(path)


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def cache_dir(explicit: str | None) -> Path:
    if explicit:
        root = Path(explicit).expanduser().resolve()
    elif os.name == "nt":
        local = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        root = Path(local) / "swarm"
    else:
        base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
        root = Path(base) / "swarm"
    root.mkdir(parents=True, exist_ok=True)
    return root


def check_id(value: str, label: str) -> str:
    if not ID_RE.fullmatch(value) or ".." in value:
        raise SystemExit(f"{label} must be a short safe id, not a path")
    return value


def existing_dir(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise SystemExit(f"not a directory: {path}")
    return path


def existing_file(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"not a file: {path}")
    return path


def official_model_id(model: str) -> str:
    token = model.split("/")[-1].lower()
    return EFFORT_RE.sub("", token)


def default_vendor(agent: str, provider: str) -> str:
    if agent == "codex":
        return "openai"
    if agent == "claude-code":
        return "anthropic"
    return provider


def candidates(binary: str) -> list[str]:
    found: list[str] = []
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        path = Path(directory) / binary
        if path.is_file() and os.access(path, os.X_OK):
            found.append(str(path))
    return found


def command_text(argv: list[str], timeout: int) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    return completed.returncode, scrub(((completed.stdout or "") + (completed.stderr or "")).strip())


def semver(text: str) -> tuple[int, int, int] | None:
    match = SEMVER_RE.search(text)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def probe_agents(check_auth: bool) -> dict:
    agents = []
    for agent, spec in AGENTS.items():
        paths = candidates(spec["binary"])
        record: dict = {
            "agent": agent,
            "official": spec["official"],
            "binary": spec["binary"],
            "path": paths[0] if paths else None,
            "candidates": paths,
            "version": None,
            "usable": False,
            "auth_ok": None,
            "warnings": [],
        }
        if not paths:
            record["warnings"].append("not installed")
            agents.append(record)
            continue
        code, text = command_text([paths[0], "--version"], 8)
        record["version"] = text.splitlines()[0][:200] if text else None
        parsed = semver(text)
        if agent == "opencode":
            if parsed is None or parsed < (2, 0, 0):
                record["warnings"].append("OpenCode 2.0.0 or newer is required")
                agents.append(record)
                continue
        elif code != 0 and not text:
            record["warnings"].append("version command failed")
        record["usable"] = True
        if check_auth:
            record["auth_ok"] = auth_status(agent, paths[0])
            if record["auth_ok"] is False:
                record["warnings"].append("not authenticated")
        agents.append(record)
    usable = [item["agent"] for item in agents if item["usable"] and item["auth_ok"] is not False]
    return {
        "schema_version": SCHEMA_VERSION,
        "checked_auth": check_auth,
        "agents": agents,
        "heterogeneous": len(usable) >= 2,
        "usable_agents": usable,
    }


def auth_status(agent: str, path: str) -> bool | None:
    if agent == "codex":
        code, text = command_text([path, "login", "status"], 12)
        lowered = text.lower()
        if "logged in" in lowered:
            return True
        if code != 0 or "not logged" in lowered or "login" in lowered:
            return False
        return None
    if agent == "claude-code":
        code, text = command_text([path, "auth", "status"], 12)
        try:
            start = text.find("{")
            payload = json.loads(text[start:]) if start >= 0 else {}
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict) and "loggedIn" in payload:
            return bool(payload["loggedIn"])
        return False if code != 0 else None
    if agent == "opencode":
        code, _text = command_text([path, "auth", "list"], 12)
        return True if code == 0 else None
    code, text = command_text([path, "models"], 12)
    if code == 0 and text:
        return True
    return False if code != 0 else None


def parse_claude_usage(text: str) -> dict:
    rows = []
    for line in text.splitlines():
        match = re.search(r"^(Current [^:]+):\s*(\d+)% used(?:\s*·\s*(.+))?$", line.strip())
        if not match:
            continue
        rows.append(
            {
                "bucket": match.group(1),
                "used_percent": int(match.group(2)),
                "reset": (match.group(3) or "").strip() or None,
            }
        )
    return {"status": "ok" if rows else "unknown", "buckets": rows}


def quota_note_supported(note: str, source: str | None) -> bool:
    if note == "unknown":
        return True
    if source is None:
        return False
    numbers = re.findall(r"\d+", note)
    if not numbers:
        return note.strip() in source
    return all(number in source for number in numbers)


def parse_route(route_id: str) -> tuple[str, str, str]:
    match = ROUTE_RE.fullmatch(route_id)
    if not match:
        raise ValueError(f"route_id must look like agent/provider/model: {route_id}")
    return match.group(1), match.group(2), match.group(3)


def validate_plan(plan: dict, probe: dict | None) -> list[str]:
    errors: list[str] = []
    if plan.get("task") not in TASKS:
        errors.append("task must be one of the supported categories")
    speed = plan.get("speed", "normal")
    if speed not in SPEEDS:
        errors.append("speed must be normal, fast, or urgent")
    steps = plan.get("steps")
    if not isinstance(steps, list) or not steps:
        return errors + ["steps must be a non-empty list"]
    if len(steps) > MAX_STEPS:
        errors.append(f"a plan has at most {MAX_STEPS} steps")
    if probe is not None and not probe.get("checked_auth"):
        errors.append("probe was taken without --check-auth")
    by_agent = {}
    if probe is not None:
        by_agent = {item["agent"]: item for item in probe.get("agents", [])}
    seen_ids: set[str] = set()
    seen_routes: set[str] = set()
    seen_vendors: list[str] = []
    distinct = plan.get("distinct_vendors", True)
    excluded = set(plan.get("exclude_vendors") or [])
    included = set(plan.get("include_vendors") or [])
    require_vision = bool(plan.get("require_vision"))
    pin_model = plan.get("pin_model")
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            errors.append(f"step {index} is not an object")
            continue
        task_id = str(step.get("task_id") or "")
        if not ID_RE.fullmatch(task_id):
            errors.append(f"step {index} task_id is not a safe id")
        elif task_id in seen_ids:
            errors.append(f"duplicate task_id {task_id}")
        seen_ids.add(task_id)
        try:
            agent, provider, model = parse_route(str(step.get("route_id") or ""))
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if str(step.get("route_id")) in seen_routes:
            errors.append(f"duplicate route {step.get('route_id')}")
        seen_routes.add(str(step.get("route_id")))
        vendor = str(step.get("vendor") or default_vendor(agent, provider))
        step["vendor"] = vendor
        if vendor in excluded:
            errors.append(f"{step.get('route_id')} uses excluded vendor {vendor}")
        if included and vendor not in included:
            errors.append(f"{step.get('route_id')} is outside include_vendors")
        if distinct and vendor in seen_vendors:
            errors.append(f"independent steps must use different vendors ({vendor})")
        seen_vendors.append(vendor)
        if pin_model and model != pin_model and official_model_id(model) != official_model_id(str(pin_model)):
            errors.append(f"{step.get('route_id')} does not match pin_model")
        rationale = str(step.get("rationale") or "").strip()
        if len(rationale) < 40:
            errors.append(f"{task_id or index} rationale must say why this route was chosen")
        lowered = rationale.lower()
        if require_vision and not step.get("vision"):
            errors.append(f"{task_id or index} does not have vision")
        if require_vision and "vision" not in lowered and "image" not in lowered:
            errors.append(f"{task_id or index} rationale must mention vision")
        if speed != "normal" and not any(word in lowered for word in ("speed", "fast", "urgent")):
            errors.append(f"{task_id or index} rationale must mention speed")
        note = str(step.get("quota_note") or "")
        source_text = None
        source = step.get("quota_source")
        if source:
            source_path = Path(str(source)).expanduser()
            if not source_path.is_file():
                errors.append(f"{task_id or index} quota_source is not a file")
            else:
                source_text = source_path.read_text(encoding="utf-8", errors="replace")
        if not quota_note_supported(note, source_text):
            errors.append(
                f"{task_id or index} quota_note must be unknown or copied from quota_source"
            )
        if probe is not None:
            record = by_agent.get(agent)
            if not record or not record.get("usable") or record.get("auth_ok") is False:
                errors.append(f"{agent} is not an authenticated usable agent")
            elif record.get("path"):
                step["binary"] = record["path"]
                step["official_agent"] = record["official"]
        errors.extend(validate_fallbacks(step, excluded, included, seen_routes))
    return errors


def validate_fallbacks(step: dict, excluded: set[str], included: set[str], seen_routes: set[str]) -> list[str]:
    errors = []
    primary_vendor = step["vendor"]
    for fallback in step.get("fallbacks") or []:
        try:
            agent, provider, _model = parse_route(str(fallback))
        except ValueError as exc:
            errors.append(str(exc))
            continue
        vendor = default_vendor(agent, provider)
        if fallback == step.get("route_id"):
            errors.append("a fallback repeats its primary route")
        if fallback in seen_routes and fallback != step.get("route_id"):
            errors.append(f"fallback {fallback} is already used by another step")
        if vendor in excluded or (included and vendor not in included):
            errors.append(f"fallback {fallback} escapes the plan vendor filter")
        if vendor != primary_vendor and vendor not in included:
            errors.append(f"fallback {fallback} leaves the primary vendor")
    return errors


def build_invocation(spec: dict) -> dict:
    agent = spec["agent"]
    binary = spec["binary"]
    model = spec["model"]
    provider = spec["provider"]
    sandbox = spec["sandbox"]
    if sandbox not in SANDBOXES:
        raise ValueError("sandbox must be read-only, workspace-write, or bypass")
    add_dirs = spec.get("add_dirs") or []
    keep = bool(spec.get("keep_session"))
    resume = spec.get("resume_session")
    no_tools = bool(spec.get("no_tools"))
    allow_shell = bool(spec.get("allow_shell"))
    isolate = bool(spec.get("isolate")) or no_tools
    prompt = spec["prompt"]
    env: dict[str, str] = {}
    tools_enforced = False
    if agent == "claude-code":
        argv = [binary, "-p", "--model", model, "--output-format", "json"]
        if sandbox == "bypass":
            argv.append("--dangerously-skip-permissions")
        elif sandbox == "workspace-write":
            argv.extend(["--permission-mode", "acceptEdits"])
        else:
            argv.extend(
                [
                    "--permission-mode",
                    "dontAsk",
                    "--permission-prompts",
                    "none",
                    "--disallowedTools",
                    "Edit,Write,NotebookEdit",
                ]
            )
            if no_tools:
                argv.extend(["--tools", "", "--safe-mode", "--strict-mcp-config"])
                tools_enforced = True
            elif allow_shell:
                argv.extend(["--tools", "Bash,Read,Grep,Glob", "--allowedTools", "Bash(*)"])
                tools_enforced = True
            else:
                tools_enforced = True
        if isolate and "--safe-mode" not in argv:
            argv.extend(["--safe-mode", "--strict-mcp-config"])
        if resume:
            argv.extend(["--resume", resume])
        elif not keep:
            argv.append("--no-session-persistence")
        for directory in add_dirs:
            argv.extend(["--add-dir", directory])
        stdin = prompt
    elif agent == "codex":
        argv = [binary, "--no-daemon", "exec"]
        if resume:
            argv.append("resume")
        elif not keep:
            argv.append("--ephemeral")
        argv.extend(["--skip-git-repo-check", "--json", "-m", model])
        argv.extend(["-c", 'model_reasoning_effort="high"'])
        if sandbox == "bypass":
            argv.append("--dangerously-bypass-approvals-and-sandbox")
        else:
            mode = "workspace-write" if sandbox == "workspace-write" else "read-only"
            argv.extend(["-c", f'sandbox_mode="{mode}"', "-c", "approval_policy=never"])
        if isolate:
            argv.append("--ignore-rules")
        output = spec.get("output_file")
        if output:
            argv.extend(["-o", output])
        if resume:
            argv.append(resume)
        argv.append("-")
        stdin = prompt
        tools_enforced = False
    elif agent == "opencode":
        argv = [binary, "run", "--standalone", "-m", f"{provider}/{model}", "--format", "json"]
        if resume:
            argv.extend(["-s", resume])
        if sandbox == "read-only" or no_tools:
            agent_name = "tools-off" if no_tools else "plan"
            argv.extend(["--agent", agent_name])
            env["OPENCODE_CONFIG_CONTENT"] = opencode_config(
                no_tools, allow_shell, isolate, add_dirs
            )
            tools_enforced = True
        else:
            argv.append("--auto")
            tools_enforced = False
        stdin = prompt
    elif agent == "antigravity":
        argv = [
            binary,
            "--model",
            model,
            "--input-format",
            "stream-json",
            "--output-format",
            "stream-json",
            "--disable-slash-commands",
            "--print-timeout",
            "600s",
        ]
        for directory in add_dirs:
            argv.extend(["--add-dir", directory])
        if sandbox == "bypass":
            argv.append("--dangerously-skip-permissions")
        elif sandbox == "workspace-write":
            argv.extend(["--mode", "accept-edits", "--sandbox"])
        else:
            argv.extend(["--mode", "plan", "--sandbox"])
            if allow_shell:
                argv.extend(
                    ["--settings", json.dumps({"permissions": {"allow": ["command(*)"]}})]
                )
        if resume:
            argv.extend(["--conversation", resume])
        argv.extend(["--print", ""])
        stdin = json.dumps(
            {"event": "user", "message": {"content": prompt}},
            ensure_ascii=False,
        )
        tools_enforced = False
    else:
        raise ValueError(f"unknown agent {agent}")
    return {
        "argv": argv,
        "stdin": stdin,
        "env": env,
        "tools_enforced": tools_enforced,
        "session_cleaned_up": agent != "antigravity" and not keep and not resume,
    }


def opencode_config(no_tools: bool, allow_shell: bool, isolate: bool, add_dirs: list[str]) -> str:
    denied = ["edit", "write", "patch"]
    if no_tools:
        denied.extend(["shell", "bash", "read", "glob", "grep", "webfetch", "skill", "mcp", "plugin"])
    elif not allow_shell:
        denied.extend(["shell", "bash"])
    rules = [{"action": action, "resource": "*", "effect": "deny"} for action in denied]
    if allow_shell and not no_tools:
        rules.extend(
            {"action": action, "resource": "*", "effect": "allow"} for action in ("shell", "bash")
        )
    for directory in add_dirs:
        rules.append(
            {"action": "external_directory", "resource": f"{directory}/*", "effect": "allow"}
        )
    payload: dict = {"permission": rules}
    if isolate:
        payload.update({"share": "disabled", "autoupdate": False, "snapshot": False})
    return json.dumps(payload)


def parse_claude(stdout: str) -> dict:
    decoder = json.JSONDecoder()
    last = None
    index = 0
    while index < len(stdout):
        if stdout[index] != "{":
            index += 1
            continue
        try:
            obj, end = decoder.raw_decode(stdout, index)
        except json.JSONDecodeError:
            index += 1
            continue
        if isinstance(obj, dict):
            last = obj
        index = max(end, index + 1)
    if not isinstance(last, dict):
        return {"text": "", "format_error": True}
    return {
        "text": str(last.get("result") or ""),
        "is_error": bool(last.get("is_error")),
        "session_id": last.get("session_id"),
        "usage": last.get("usage") if isinstance(last.get("usage"), dict) else None,
        "format_error": False,
    }


def parse_json_lines(stdout: str) -> list[dict]:
    rows = []
    for line in stdout.splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def parse_codex(stdout: str, output_text: str) -> dict:
    session = None
    texts = []
    for event in parse_json_lines(stdout):
        if event.get("type") == "thread.started":
            session = event.get("thread_id")
        item = event.get("item") if isinstance(event.get("item"), dict) else {}
        if event.get("type") in {"item.completed", "agent_message"} and item.get("type") in {
            None,
            "agent_message",
        }:
            text = item.get("text") or event.get("text")
            if text:
                texts.append(str(text))
        elif event.get("type") == "message" and event.get("text"):
            texts.append(str(event["text"]))
    return {
        "text": output_text or "\n".join(texts),
        "session_id": session,
        "is_error": False,
        "format_error": not (output_text or texts),
    }


def parse_opencode(stdout: str) -> dict:
    texts = []
    session = None
    error = False
    for event in parse_json_lines(stdout):
        session = session or event.get("sessionID") or event.get("session_id")
        if event.get("type") == "text":
            part = event.get("part") if isinstance(event.get("part"), dict) else {}
            texts.append(str(part.get("text") or event.get("text") or ""))
        if event.get("type") == "error":
            error = True
    return {
        "text": "\n".join(part for part in texts if part),
        "session_id": session,
        "is_error": error,
        "format_error": not texts and not error,
    }


def parse_agy(stdout: str, stderr: str) -> dict:
    text = ""
    session = None
    status = ""
    for event in parse_json_lines(stdout):
        if event.get("event") == "init":
            session = event.get("conversation_id") or session
        if event.get("event") == "result":
            result = event.get("result") if isinstance(event.get("result"), dict) else {}
            text = str(result.get("response") or "")
            status = str(result.get("status") or "")
            session = result.get("conversation_id") or session
    denied = (
        status == "SUCCESS"
        and not text.strip()
        and "jetski:" in stderr.lower()
        and "auto-denied" in stderr.lower()
    )
    return {
        "text": text,
        "session_id": session,
        "is_error": status not in {"", "SUCCESS"},
        "permission_denied": denied,
        "format_error": status == "" and not text,
    }


def classify_failure(returncode: int, stderr: str, parsed: dict) -> str | None:
    if parsed.get("permission_denied"):
        return "permission"
    if returncode == 0 and parsed.get("text") and not parsed.get("is_error"):
        return None
    err = stderr.lower()
    if "unknown option" in err or "unrecognized option" in err or "unexpected argument" in err:
        return "no_option"
    if "429" in stderr or "quota" in err or "rate limit" in err:
        return "quota"
    if "not logged" in err or "please log in" in err or "authentication" in err:
        return "auth"
    if "model" in err and ("not found" in err or "does not exist" in err or "unavailable" in err):
        return "unavailable"
    if parsed.get("format_error"):
        return "format"
    if returncode != 0 or parsed.get("is_error") or not parsed.get("text"):
        return "failed"
    return None


def git_bytes(cwd: Path, args: list[str]) -> bytes | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True,
            timeout=30,
            check=False,
            env={**os.environ, "GIT_PAGER": "cat", "GIT_TERMINAL_PROMPT": "0"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout


def git_snapshot(cwd: Path, ignored_roots: list[Path]) -> dict:
    head = git_bytes(cwd, ["rev-parse", "HEAD"])
    status = git_bytes(cwd, ["status", "--porcelain=v1", "-z"])
    if head is None or status is None:
        return {"ok": False, "reason": "git state could not be read"}
    paths = porcelain_paths(status)
    if len(paths) > 20000:
        return {"ok": False, "reason": "too many files to guard"}
    digest = hashlib.sha256()
    digest.update(head)
    digest.update(status)
    files: dict[str, str] = {}
    for rel in paths:
        path = cwd / rel
        if any(root == path or root in path.parents for root in ignored_roots):
            continue
        if path.is_symlink():
            target = os.readlink(path)
            token = "link:" + target
            digest.update(rel.encode("utf-8", "surrogateescape"))
            digest.update(token.encode("utf-8", "surrogateescape"))
            files[rel] = token
            continue
        if not path.is_file():
            digest.update(rel.encode("utf-8", "surrogateescape") + b"\0missing")
            files[rel] = "missing"
            continue
        file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        digest.update(rel.encode("utf-8", "surrogateescape"))
        digest.update(file_hash.encode("ascii"))
        files[rel] = file_hash
    return {
        "ok": True,
        "head": head.decode("utf-8", "replace").strip(),
        "digest": digest.hexdigest(),
        "files": files,
    }


def changed_files(before: dict, after: dict) -> list[str]:
    if not before.get("ok") or not after.get("ok"):
        return []
    before_files = before.get("files") or {}
    after_files = after.get("files") or {}
    keys = set(before_files) | set(after_files)
    changed = [key for key in keys if before_files.get(key) != after_files.get(key)]
    if before.get("head") != after.get("head") and "HEAD" not in changed:
        changed.append("HEAD")
    return sorted(changed)


def porcelain_paths(blob: bytes) -> list[str]:
    paths = []
    for record in blob.split(b"\0"):
        if len(record) < 4:
            continue
        path = record[3:].decode("utf-8", "surrogateescape")
        if path:
            paths.append(path)
    return paths


def load_plan(root: Path, run_id: str) -> dict:
    path = root / "runs" / run_id / "plan.json"
    if not path.is_file():
        raise SystemExit(f"missing plan: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def step_by_id(plan: dict, task_id: str) -> dict:
    for step in plan["steps"]:
        if step["task_id"] == task_id:
            return step
    raise SystemExit(f"task {task_id} is not in the plan")


def combine_prompt(common: Path | None, task: Path, references: list[str], recommend: bool) -> str:
    parts = []
    if common and common.is_file():
        parts.append(common.read_text(encoding="utf-8").rstrip())
    parts.append(task.read_text(encoding="utf-8").rstrip())
    if references:
        lines = ["", "## Sources"]
        if recommend:
            lines.append("Read these sources before answering. They are part of the task, not optional color.")
        lines.extend(f"- {item}" for item in references)
        parts.append("\n".join(lines))
    return "\n\n".join(parts).strip() + "\n"


def append_manifest(run_dir: Path, event: dict) -> None:
    path = run_dir / "manifest.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def run_attempt(spec: dict, attempt_dir: Path, timeout: int) -> dict:
    attempt_dir.mkdir(parents=True, exist_ok=True)
    if spec["agent"] == "codex":
        spec = {**spec, "output_file": str(attempt_dir / "cli-result.md")}
    invocation = build_invocation(spec)
    if spec.get("dry_run"):
        return {"dry_run": True, "invocation": {key: invocation[key] for key in ("argv", "stdin", "env", "tools_enforced")}}
    write_text(attempt_dir / "prompt.md", spec["prompt"])
    env = os.environ.copy()
    env.update(invocation["env"])
    env["SWARM_RUN_ID"] = spec["run_id"]
    env["SWARM_PARENT_TASK_ID"] = spec["task_id"]
    started = time.monotonic()
    try:
        completed = subprocess.run(
            invocation["argv"],
            input=invocation["stdin"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=spec["cwd"],
            env=env,
            check=False,
        )
        code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
        error_class = None
    except subprocess.TimeoutExpired as exc:
        code, stdout, stderr = 124, exc.stdout or "", exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", "replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", "replace")
        error_class = "timeout"
    except OSError as exc:
        code, stdout, stderr, error_class = 127, "", str(exc), "unavailable"
    duration_ms = int((time.monotonic() - started) * 1000)
    write_text(attempt_dir / "stdout.log", stdout)
    write_text(attempt_dir / "stderr.log", stderr)
    output_text = ""
    output_path = attempt_dir / "cli-result.md"
    if output_path.is_file():
        output_text = output_path.read_text(encoding="utf-8", errors="replace")
    parsed = parse_output(spec["agent"], stdout, stderr, output_text)
    if error_class is None:
        error_class = classify_failure(code, stderr, parsed)
    if parsed.get("text"):
        write_text(attempt_dir / "result.md", parsed["text"].rstrip() + "\n")
    return {
        "returncode": code,
        "duration_ms": duration_ms,
        "parsed": parsed,
        "error_class": error_class,
        "tools_enforced": invocation["tools_enforced"],
        "session_cleaned_up": invocation["session_cleaned_up"] and error_class is None,
        "argv": invocation["argv"],
    }


def parse_output(agent: str, stdout: str, stderr: str, output_text: str) -> dict:
    if agent == "claude-code":
        return parse_claude(stdout)
    if agent == "codex":
        return parse_codex(stdout, output_text)
    if agent == "opencode":
        return parse_opencode(stdout)
    return parse_agy(stdout, stderr)


def route_parts(route_id: str) -> dict:
    agent, provider, model = parse_route(route_id)
    return {
        "route_id": route_id,
        "agent": agent,
        "provider": provider,
        "model": model,
        "official_agent": AGENTS[agent]["official"],
        "official_model_id": official_model_id(model),
    }


def execute_run(args: argparse.Namespace) -> int:
    root = cache_dir(args.cache_dir)
    run_id = check_id(args.run_id, "run-id")
    task_id = check_id(args.task_id, "task-id")
    plan = load_plan(root, run_id)
    step = step_by_id(plan, task_id)
    cwd = existing_dir(args.cwd)
    prompt_path = existing_file(args.prompt_file)
    common = existing_file(args.common_prompt) if args.common_prompt else default_common()
    references = list(args.reference or [])
    prompt = combine_prompt(common, prompt_path, references, args.recommend_inspect)
    add_dirs = [str(existing_dir(item)) for item in (args.add_dir or [])]
    for item in args.context_file or []:
        parent = str(existing_file(item).parent)
        if parent not in add_dirs:
            add_dirs.append(parent)
    sandbox = args.sandbox
    if args.no_tools:
        sandbox = "read-only"
    run_dir = root / "runs" / run_id
    task_dir = run_dir / task_id
    before = git_snapshot(cwd, [root])
    if args.guard and not before.get("ok"):
        meta = base_meta(step, sandbox, prompt, "failed", "guard_failed", before.get("reason"))
        write_json(task_dir / "meta.json", meta)
        return 1
    routes = [step["route_id"], *list(step.get("fallbacks") or [])]
    resume = None
    if args.resume_task:
        sessions = json.loads((run_dir / "sessions.json").read_text(encoding="utf-8"))
        resume = sessions[args.resume_task]["session_id"]
    final = None
    started = False
    for attempt_number, route_id in enumerate(routes, start=1):
        parts = route_parts(route_id)
        binary = step.get("binary") if route_id == step["route_id"] else None
        if binary is None:
            record = next(item for item in probe_agents(True)["agents"] if item["agent"] == parts["agent"])
            if not record.get("path"):
                final = {"error_class": "unavailable", "parsed": {"text": ""}, "returncode": 127, "duration_ms": 0, "tools_enforced": False, "session_cleaned_up": False, "argv": []}
                break
            binary = record["path"]
        spec = {
            **parts,
            "binary": binary,
            "sandbox": sandbox,
            "no_tools": args.no_tools,
            "allow_shell": args.allow_shell,
            "isolate": args.isolate,
            "keep_session": args.keep_session or bool(args.resume_task),
            "resume_session": resume,
            "prompt": prompt,
            "cwd": str(cwd),
            "run_id": run_id,
            "task_id": task_id,
            "add_dirs": add_dirs,
            "dry_run": args.dry_run,
        }
        outcome = run_attempt(spec, task_dir / "attempts" / f"attempt-{attempt_number}", args.timeout)
        if outcome.get("dry_run"):
            json.dump(outcome["invocation"], sys.stdout, indent=2)
            sys.stdout.write("\n")
            return 0
        if not started:
            append_manifest(run_dir, {"event": "task_started", "run_id": run_id, "task_id": task_id})
            started = True
        final = {**outcome, **parts, "attempt": attempt_number}
        if outcome["error_class"] is None:
            break
        if outcome["error_class"] not in FALLBACK_OK:
            break
    assert final is not None
    after = git_snapshot(cwd, [root])
    changed = changed_files(before, after)
    mutated = bool(args.guard) and bool(changed)
    if mutated:
        final["error_class"] = "mutated"
    write_set = list(args.write_set or [])
    outside = [path for path in changed if write_set and path not in write_set]
    warnings = []
    if len(prompt) > PROMPT_WARN:
        warnings.append("prompt_size_warning")
    if outside:
        warnings.append("write_set_exceeded")
    status = "ok" if final.get("error_class") is None else "failed"
    meta = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "error_class": final.get("error_class"),
        "exit_code": final.get("returncode"),
        "duration_ms": final.get("duration_ms"),
        "route_id": final.get("route_id", step["route_id"]),
        "official_agent": final.get("official_agent", step.get("official_agent")),
        "official_model_id": final.get("official_model_id", official_model_id(step["route_id"].split("/")[-1])),
        "selection_rationale": step.get("rationale"),
        "sandbox": sandbox,
        "tools_enforced": final.get("tools_enforced"),
        "session_id": (final.get("parsed") or {}).get("session_id"),
        "session_cleaned_up": final.get("session_cleaned_up"),
        "significant": True,
        "warnings": warnings,
        "changed_paths": changed,
        "write_set": write_set,
        "write_set_ok": not outside,
        "attempt": final.get("attempt"),
        "denials_observed": ["permission"] if (final.get("parsed") or {}).get("permission_denied") else [],
    }
    if args.guard:
        write_json(task_dir / "attempts" / f"attempt-{final.get('attempt', 1)}" / "guard.json", {"before": before, "after": after})
    result_path = task_dir / "result.md"
    if status == "ok":
        write_text(result_path, str((final.get("parsed") or {}).get("text") or "").rstrip() + "\n")
    elif result_path.exists():
        result_path.unlink()
        if args.keep_session and meta["session_id"]:
            sessions_path = run_dir / "sessions.json"
            sessions = json.loads(sessions_path.read_text(encoding="utf-8")) if sessions_path.is_file() else {}
            sessions[task_id] = {"session_id": meta["session_id"], "route_id": meta["route_id"], "cwd": str(cwd)}
            write_json(sessions_path, sessions)
        elif step["route_id"].startswith("opencode/") and meta["session_id"] and not args.keep_session:
            delete_opencode_session(step.get("binary") or "opencode", meta["session_id"], meta)
    else:
        meta["session_cleaned_up"] = False
    write_json(task_dir / "meta.json", meta)
    append_manifest(
        run_dir,
        {
            "event": "task_finished",
            "run_id": run_id,
            "task_id": task_id,
            "status": status,
            "official_agent": meta["official_agent"],
            "official_model_id": meta["official_model_id"],
            "significant": True,
        },
    )
    write_report(run_dir)
    return 0 if status == "ok" else 1


def base_meta(step: dict, sandbox: str, prompt: str, status: str, error_class: str | None, detail: str | None) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "error_class": error_class,
        "route_id": step["route_id"],
        "selection_rationale": step.get("rationale"),
        "sandbox": sandbox,
        "warnings": [detail] if detail else [],
        "significant": True,
        "prompt_chars": len(prompt),
    }


def delete_opencode_session(binary: str, session_id: str, meta: dict) -> None:
    code, _text = command_text([binary, "session", "delete", "--standalone", session_id], 20)
    meta["session_cleaned_up"] = code == 0


def default_common() -> Path | None:
    path = Path(__file__).resolve().parents[1] / "assets" / "prompts" / "common.md"
    return path if path.is_file() else None


def write_report(run_dir: Path, only_significant: bool = False) -> str:
    lines = [f"# Run {run_dir.name}", ""]
    plan_path = run_dir / "plan.json"
    if plan_path.is_file():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        lines.append(f"Task category: {plan.get('task')}")
        lines.append("")
    entries = []
    for task_dir in sorted(path for path in run_dir.iterdir() if (path / "meta.json").is_file()):
        meta = json.loads((task_dir / "meta.json").read_text(encoding="utf-8"))
        if only_significant and not meta.get("significant", True):
            continue
        entries.append((task_dir.name, meta))
    if not entries:
        lines.append("No tasks recorded.")
    for task_id, meta in entries:
        flag = "significant" if meta.get("significant", True) else "insignificant"
        lines.append(
            f"- {task_id} — {meta.get('official_agent')} — {meta.get('official_model_id')} — {meta.get('status')} — {flag}"
        )
        if meta.get("selection_rationale"):
            lines.append(f"  Route: {meta.get('selection_rationale')}")
        if meta.get("outcome_summary"):
            lines.append(f"  Outcome: {meta['outcome_summary']}")
        if meta.get("error_class"):
            lines.append(f"  Error: {meta['error_class']}")
        if meta.get("warnings"):
            lines.append(f"  Warnings: {', '.join(meta['warnings'])}")
        if meta.get("write_set_ok") is False:
            lines.append("  The working tree changed outside the declared write set.")
    text = "\n".join(lines).rstrip() + "\n"
    write_text(run_dir / "report.md", text)
    return text


def cmd_probe(args: argparse.Namespace) -> int:
    payload = probe_agents(args.check_auth)
    root = cache_dir(args.cache_dir)
    write_json(root / "probe.json", payload)
    if args.json:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    for agent in payload["agents"]:
        state = "usable" if agent["usable"] and agent["auth_ok"] is not False else "unusable"
        print(f"{agent['official']}: {state} {agent.get('version') or 'not installed'}")
        for warning in agent["warnings"]:
            print(f"  warning: {warning}")
    print("heterogeneous:" , "yes" if payload["heterogeneous"] else "no")
    return 0


def cmd_parse_usage(args: argparse.Namespace) -> int:
    text = existing_file(args.file).read_text(encoding="utf-8", errors="replace")
    if args.agent != "claude-code":
        json.dump({"status": "unknown", "buckets": []}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    json.dump(parse_claude_usage(text), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    root = cache_dir(args.cache_dir)
    plan = json.loads(existing_file(args.file).read_text(encoding="utf-8"))
    probe_path = Path(args.probe).expanduser() if args.probe else root / "probe.json"
    if not probe_path.is_file():
        raise SystemExit("probe.json is missing; run probe --check-auth first")
    probe = json.loads(probe_path.read_text(encoding="utf-8"))
    errors = validate_plan(plan, probe)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 2
    run_id = check_id(args.run_id, "run-id")
    run_dir = root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    plan["schema_version"] = SCHEMA_VERSION
    plan["run_id"] = run_id
    write_json(run_dir / "plan.json", plan)
    print(run_dir / "plan.json")
    return 0


def cmd_mark(args: argparse.Namespace) -> int:
    root = cache_dir(args.cache_dir)
    run_id = check_id(args.run_id, "run-id")
    task_id = check_id(args.task_id, "task-id")
    meta_path = root / "runs" / run_id / task_id / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["significant"] = not args.insignificant
    meta["outcome_summary"] = args.outcome_summary
    write_json(meta_path, meta)
    write_report(root / "runs" / run_id)
    return 0


def cmd_record_native(args: argparse.Namespace) -> int:
    root = cache_dir(args.cache_dir)
    run_id = check_id(args.run_id, "run-id")
    task_id = check_id(args.task_id, "task-id")
    task_dir = root / "runs" / run_id / task_id
    meta = {
        "schema_version": SCHEMA_VERSION,
        "status": "ok",
        "native": True,
        "official_agent": args.agent,
        "official_model_id": official_model_id(args.model),
        "significant": True,
        "outcome_summary": args.outcome_summary,
        "selection_rationale": args.summary,
        "warnings": [],
        "write_set_ok": True,
    }
    write_json(task_dir / "meta.json", meta)
    write_text(task_dir / "result.md", args.outcome_summary.rstrip() + "\n")
    append_manifest(
        root / "runs" / run_id,
        {
            "event": "task_finished",
            "run_id": run_id,
            "task_id": task_id,
            "status": "ok",
            "native": True,
            "official_agent": args.agent,
            "official_model_id": meta["official_model_id"],
        },
    )
    write_report(root / "runs" / run_id)
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    root = cache_dir(args.cache_dir)
    text = write_report(root / "runs" / check_id(args.run_id, "run-id"), args.only_significant)
    sys.stdout.write(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="swarm.py",
        description="Swarm helper: probe coding-agent CLIs, check a route plan, run one delegated task, and report the call tree",)
    parser.add_argument("--cache-dir")
    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe")
    probe.add_argument("--json", action="store_true")
    probe.add_argument("--check-auth", action="store_true")
    probe.set_defaults(func=cmd_probe)

    usage = sub.add_parser("parse-usage")
    usage.add_argument("--agent", required=True)
    usage.add_argument("--file", required=True)
    usage.set_defaults(func=cmd_parse_usage)

    plan = sub.add_parser("plan")
    plan.add_argument("--run-id", required=True)
    plan.add_argument("--file", required=True)
    plan.add_argument("--probe")
    plan.set_defaults(func=cmd_plan)

    run = sub.add_parser("run")
    run.add_argument("--run-id", required=True)
    run.add_argument("--task-id", required=True)
    run.add_argument("--prompt-file", required=True)
    run.add_argument("--cwd", required=True)
    run.add_argument("--sandbox", default="workspace-write", choices=sorted(SANDBOXES))
    run.add_argument("--common-prompt")
    run.add_argument("--context-file", action="append")
    run.add_argument("--add-dir", action="append")
    run.add_argument("--reference", action="append")
    run.add_argument("--recommend-inspect", action="store_true")
    run.add_argument("--no-tools", action="store_true")
    run.add_argument("--allow-shell", action="store_true")
    run.add_argument("--isolate", action="store_true")
    run.add_argument("--keep-session", action="store_true")
    run.add_argument("--resume-task")
    run.add_argument("--guard", action="store_true")
    run.add_argument("--write-set", action="append")
    run.add_argument("--timeout", type=int, default=600)
    run.add_argument("--dry-run", action="store_true")
    run.set_defaults(func=execute_run)

    mark = sub.add_parser("mark")
    mark.add_argument("--run-id", required=True)
    mark.add_argument("--task-id", required=True)
    mark.add_argument("--insignificant", action="store_true")
    mark.add_argument("--outcome-summary", required=True)
    mark.set_defaults(func=cmd_mark)

    native = sub.add_parser("record-native")
    native.add_argument("--run-id", required=True)
    native.add_argument("--task-id", required=True)
    native.add_argument("--agent", required=True)
    native.add_argument("--model", required=True)
    native.add_argument("--summary", required=True)
    native.add_argument("--outcome-summary", required=True)
    native.set_defaults(func=cmd_record_native)

    report = sub.add_parser("report")
    report.add_argument("--run-id", required=True)
    report.add_argument("--only-significant", action="store_true")
    report.set_defaults(func=cmd_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
