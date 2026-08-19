#!/usr/bin/env python3
"""Audit every packaged skill in a skills repository against one contract.

The contract is stated in
`skill-forge/skills/skill-forge/references/skill-package-contract.md`.
This script is its executable form: it walks `<root>/*/skills/*/SKILL.md`,
applies rules C1 through C9, and reports every violation with the file to fix.

Standard library only. Read-only: it never edits the repository.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RULES = {
    "C1": "Skill directory name, path, and frontmatter name agree",
    "C2": "Description follows the invocation grammar",
    "C3": "Invocation mode is declared consistently",
    "C4": "Codex descriptor is complete",
    "C5": "Slash command exists for the skill",
    "C6": "Evals file is present and substantive",
    "C7": "Website catalog and every locale carry the skill",
    "C8": "Owning plugin manifest is complete",
    "C9": "Published counts match the packaged tree",
}

LOCALES = ("ko", "en", "jp", "cn")

MIN_EVALS = 3
MIN_ASSERTIONS = 2
MAX_DESCRIPTION = 1024
MAX_SHORT_DESCRIPTION = 90

COUNT_PATTERNS = {
    "workflows": (
        re.compile(r"(\d+)\s+(?:practical agent workflows|canonical workflows)"),
        re.compile(r"(\d+)개의?\s*(?:실용적인 에이전트 워크플로|정규 워크플로)"),
        re.compile(r"(\d+)\s*(?:個のワークフロー|个工作流)"),
    ),
    "selectors": (
        re.compile(r"(\d+)\s+(?:installable Codex selectors|packaged selectors)"),
        re.compile(r"(\d+)개의?\s*설치 가능한 Codex selector"),
        re.compile(r"(\d+)\s*(?:個のCodexセレクター|个可安装的 Codex 选择器)"),
    ),
}

COUNT_DOCS = ("README.md", "README.ko.md", "USAGE.md", "ARCHITECTURE.md")


@dataclass
class Violation:
    rule: str
    skill: str
    detail: str
    path: str

    def as_dict(self) -> dict[str, str]:
        return {
            "rule": self.rule,
            "title": RULES[self.rule],
            "skill": self.skill,
            "detail": self.detail,
            "path": self.path,
        }


@dataclass
class Skill:
    name: str
    plugin: str
    directory: Path
    frontmatter: dict[str, str]
    body: str
    root: Path

    @property
    def relative(self) -> str:
        return (self.directory / "SKILL.md").relative_to(self.root).as_posix()


@dataclass
class Report:
    root: Path
    skills: list[Skill] = field(default_factory=list)
    violations: list[Violation] = field(default_factory=list)
    catalog_ids: list[str] = field(default_factory=list)
    catalog_aliases: list[str] = field(default_factory=list)

    def add(self, rule: str, skill: str, detail: str, path: str) -> None:
        self.violations.append(Violation(rule, skill, detail, path))


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse the flat `key: value` frontmatter block a SKILL.md uses."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end]
    body = text[end + 4 :]
    fields: dict[str, str] = {}
    key: str | None = None
    for line in block.splitlines():
        if not line.strip():
            continue
        match = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if match:
            key = match.group(1)
            fields[key] = match.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fields[key] = f"{fields[key]} {line.strip()}".strip()
    for key, value in fields.items():
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            fields[key] = value[1:-1]
    return fields, body


def parse_yaml_interface(text: str) -> dict[str, str]:
    """Read the two-level `interface:` mapping from a Codex descriptor."""
    values: dict[str, str] = {}
    inside = False
    for line in text.splitlines():
        if re.match(r"^interface:\s*$", line):
            inside = True
            continue
        if inside:
            if line.strip() and not line.startswith((" ", "\t")):
                break
            match = re.match(r"^\s+([\w_]+):\s*(.*)$", line)
            if match:
                value = match.group(2).strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                values[match.group(1)] = value
    return values


def discover(root: Path) -> list[Skill]:
    skills: list[Skill] = []
    for skill_md in sorted(root.glob("*/skills/*/SKILL.md")):
        directory = skill_md.parent
        plugin = skill_md.relative_to(root).parts[0]
        frontmatter, body = parse_frontmatter(
            skill_md.read_text(encoding="utf-8")
        )
        skills.append(
            Skill(
                name=frontmatter.get("name", directory.name),
                plugin=plugin,
                directory=directory,
                frontmatter=frontmatter,
                body=body,
                root=root,
            )
        )
    return skills


def read_catalog(root: Path) -> tuple[list[str], list[str]]:
    catalog = root / "website" / "src" / "data" / "skills.ts"
    if not catalog.is_file():
        return [], []
    source = catalog.read_text(encoding="utf-8")
    ids = [m.group(1) for m in re.finditer(r'^\s*id:\s*"([^"]+)",\s*$', source, re.M)]
    aliases = [
        token.group(1).lstrip("/$")
        for block in re.finditer(r"^\s*aliases:\s*\[([^\]]*)\],\s*$", source, re.M)
        for token in re.finditer(r'"([/$][^"]+)"', block.group(1))
    ]
    return ids, sorted(set(aliases))


def check_c1(skill: Skill, report: Report) -> None:
    if skill.frontmatter.get("name") != skill.directory.name:
        report.add(
            "C1",
            skill.directory.name,
            f"frontmatter name {skill.frontmatter.get('name')!r} "
            f"does not match directory {skill.directory.name!r}",
            skill.relative,
        )


def check_c2(skill: Skill, report: Report) -> None:
    description = skill.frontmatter.get("description", "").strip()
    path = skill.relative
    if not description:
        report.add("C2", skill.name, "description is missing", path)
        return
    if not description.startswith(("Use when", "Use only when")):
        report.add(
            "C2",
            skill.name,
            "description must open with 'Use when' or 'Use only when'",
            path,
        )
    for selector in (f"/{skill.name}", f"${skill.name}"):
        if selector not in description:
            report.add(
                "C2", skill.name, f"description omits the {selector} selector", path
            )
    if len(description) > MAX_DESCRIPTION:
        report.add(
            "C2",
            skill.name,
            f"description is {len(description)} characters, over {MAX_DESCRIPTION}",
            path,
        )


def check_c3(skill: Skill, report: Report) -> None:
    """The opening clause and the frontmatter flag must agree.

    `Use only when` promises the skill fires on its selectors alone, so it must
    also switch model invocation off. `Use when` promises the opposite.
    """
    declared = skill.frontmatter.get("disable-model-invocation", "").lower() == "true"
    selector_only = skill.frontmatter.get("description", "").startswith("Use only when")
    if selector_only and not declared:
        report.add(
            "C3",
            skill.name,
            "description opens with 'Use only when' but "
            "disable-model-invocation is not set",
            skill.relative,
        )
    if declared and not selector_only:
        report.add(
            "C3",
            skill.name,
            "disable-model-invocation is set but the description does not "
            "open with 'Use only when'",
            skill.relative,
        )


def check_c4(skill: Skill, report: Report) -> None:
    descriptor = skill.directory / "agents" / "openai.yaml"
    relative = descriptor.relative_to(skill.root).as_posix()
    if not descriptor.is_file():
        report.add("C4", skill.name, "agents/openai.yaml is missing", relative)
        return
    interface = parse_yaml_interface(descriptor.read_text(encoding="utf-8"))
    for key in ("display_name", "short_description", "default_prompt"):
        if not interface.get(key):
            report.add("C4", skill.name, f"interface.{key} is missing", relative)
    prompt = interface.get("default_prompt", "")
    if prompt and f"${skill.name}" not in prompt:
        report.add(
            "C4",
            skill.name,
            f"interface.default_prompt does not invoke ${skill.name}",
            relative,
        )
    short = interface.get("short_description", "")
    if len(short) > MAX_SHORT_DESCRIPTION:
        report.add(
            "C4",
            skill.name,
            f"interface.short_description is {len(short)} characters, "
            f"over {MAX_SHORT_DESCRIPTION}",
            relative,
        )
    if short.endswith("."):
        report.add(
            "C4",
            skill.name,
            "interface.short_description must not end with a period",
            relative,
        )


def check_c5(skill: Skill, report: Report) -> None:
    command = skill.root / skill.plugin / "commands" / f"{skill.name}.md"
    relative = command.relative_to(skill.root).as_posix()
    if not command.is_file():
        report.add("C5", skill.name, "slash command file is missing", relative)
        return
    frontmatter, _ = parse_frontmatter(command.read_text(encoding="utf-8"))
    if not frontmatter.get("description"):
        report.add("C5", skill.name, "command frontmatter has no description", relative)


def check_c6(skill: Skill, report: Report) -> None:
    evals = skill.directory / "evals" / "evals.json"
    relative = evals.relative_to(skill.root).as_posix()
    if not evals.is_file():
        report.add("C6", skill.name, "evals/evals.json is missing", relative)
        return
    try:
        payload = json.loads(evals.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        report.add("C6", skill.name, f"evals/evals.json is not valid JSON: {error}", relative)
        return
    if payload.get("skill_name") != skill.name:
        report.add(
            "C6",
            skill.name,
            f"skill_name is {payload.get('skill_name')!r}, expected {skill.name!r}",
            relative,
        )
    items = payload.get("evals")
    if not isinstance(items, list) or len(items) < MIN_EVALS:
        count = len(items) if isinstance(items, list) else 0
        report.add(
            "C6", skill.name, f"holds {count} evals, expected at least {MIN_EVALS}", relative
        )
        return
    for index, item in enumerate(items, start=1):
        for key in ("prompt", "expected_output", "files", "assertions"):
            if key not in item:
                report.add("C6", skill.name, f"eval {index} has no {key}", relative)
        assertions = item.get("assertions", [])
        if len(assertions) < MIN_ASSERTIONS:
            report.add(
                "C6",
                skill.name,
                f"eval {index} has {len(assertions)} assertions, "
                f"expected at least {MIN_ASSERTIONS}",
                relative,
            )


def check_c7(skill: Skill, report: Report) -> None:
    catalog = skill.root / "website" / "src" / "data" / "skills.ts"
    if not catalog.is_file():
        return
    if skill.name in report.catalog_ids:
        return
    if skill.name in report.catalog_aliases:
        return
    report.add(
        "C7",
        skill.name,
        "skill is neither a catalog id nor a declared catalog alias",
        catalog.relative_to(skill.root).as_posix(),
    )


def check_c7_locales(report: Report) -> None:
    content = report.root / "website" / "src" / "i18n" / "content"
    if not content.is_dir():
        return
    for locale in LOCALES:
        path = content / f"{locale}.json"
        relative = path.relative_to(report.root).as_posix()
        if not path.is_file():
            report.add("C7", "-", f"locale file {locale}.json is missing", relative)
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        copy = payload.get("skills", {})
        for skill_id in report.catalog_ids:
            entry = copy.get(skill_id)
            if entry is None:
                report.add("C7", skill_id, f"{locale}.json has no copy", relative)
                continue
            for key in ("summary", "whenToUse", "result"):
                if not entry.get(key):
                    report.add(
                        "C7", skill_id, f"{locale}.json copy has no {key}", relative
                    )


def check_c8(root: Path, plugins: set[str], report: Report) -> None:
    for plugin in sorted(plugins):
        manifest = root / plugin / ".claude-plugin" / "plugin.json"
        relative = manifest.relative_to(root).as_posix()
        if not manifest.is_file():
            report.add("C8", plugin, "plugin.json is missing", relative)
            continue
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            report.add("C8", plugin, f"plugin.json is not valid JSON: {error}", relative)
            continue
        for key in ("name", "description", "version"):
            if not payload.get(key):
                report.add("C8", plugin, f"plugin.json has no {key}", relative)
        if payload.get("name") not in (None, plugin):
            report.add(
                "C8",
                plugin,
                f"plugin.json name is {payload['name']!r}, expected {plugin!r}",
                relative,
            )


def check_c9(report: Report) -> None:
    expected = {
        "workflows": len(report.catalog_ids) or len(report.skills),
        "selectors": len(report.skills),
    }
    for name in COUNT_DOCS:
        path = report.root / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.name
        for kind, patterns in COUNT_PATTERNS.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    found = int(match.group(1))
                    if found != expected[kind]:
                        report.add(
                            "C9",
                            "-",
                            f"publishes {found} {kind}, packaged tree has "
                            f"{expected[kind]}",
                            relative,
                        )


def audit(root: Path, only: str | None = None) -> Report:
    report = Report(root=root)
    report.skills = discover(root)
    report.catalog_ids, report.catalog_aliases = read_catalog(root)
    selected = [s for s in report.skills if only in (None, s.name)]
    if only and not selected:
        raise SystemExit(f"No packaged skill named {only!r} under {root}")

    for skill in selected:
        check_c1(skill, report)
        check_c2(skill, report)
        check_c3(skill, report)
        check_c4(skill, report)
        check_c5(skill, report)
        check_c6(skill, report)
        check_c7(skill, report)

    if only is None:
        check_c7_locales(report)
        check_c8(root, {s.plugin for s in report.skills}, report)
        check_c9(report)

    report.violations.sort(key=lambda v: (v.rule, v.skill, v.detail))
    return report


def render_text(report: Report) -> str:
    lines = [
        f"Audited {len(report.skills)} packaged skills "
        f"and {len(report.catalog_ids)} catalog workflows under {report.root}."
    ]
    if not report.violations:
        lines.append("Contract satisfied: no violations.")
        return "\n".join(lines)
    lines.append(f"{len(report.violations)} violations:")
    width = max(len(v.skill) for v in report.violations)
    for violation in report.violations:
        lines.append(
            f"  {violation.rule}  {violation.skill:<{width}}  "
            f"{violation.detail}  ({violation.path})"
        )
    lines.append("")
    for rule in sorted({v.rule for v in report.violations}):
        lines.append(f"  {rule} — {RULES[rule]}")
    return "\n".join(lines)


def render_markdown(report: Report) -> str:
    lines = [
        "# Skill contract audit",
        "",
        f"- Root: `{report.root}`",
        f"- Packaged skills: {len(report.skills)}",
        f"- Catalog workflows: {len(report.catalog_ids)}",
        f"- Violations: {len(report.violations)}",
        "",
    ]
    if not report.violations:
        lines.append("Contract satisfied: no violations.")
        return "\n".join(lines)
    lines += ["| Rule | Skill | Violation | File |", "| --- | --- | --- | --- |"]
    for violation in report.violations:
        lines.append(
            f"| {violation.rule} | `{violation.skill}` | {violation.detail} "
            f"| `{violation.path}` |"
        )
    lines += ["", "## Rules referenced", ""]
    for rule in sorted({v.rule for v in report.violations}):
        lines.append(f"- **{rule}** — {RULES[rule]}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root", default=".", help="repository root to audit (default: current directory)"
    )
    parser.add_argument("--skill", help="audit a single skill by name")
    parser.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="output format (default: text)",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        parser.error(f"root {root} is not a directory")

    report = audit(root, args.skill)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "root": str(report.root),
                    "packaged_skills": len(report.skills),
                    "catalog_workflows": len(report.catalog_ids),
                    "violations": [v.as_dict() for v in report.violations],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif args.format == "markdown":
        print(render_markdown(report))
    else:
        print(render_text(report))

    return 1 if report.violations else 0


if __name__ == "__main__":
    sys.exit(main())
