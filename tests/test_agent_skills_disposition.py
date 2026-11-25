"""Every agent-skills workflow has exactly one disposition in this catalog.

The names are the skill directories of addyosmani/agent-skills at the pinned
commit. A workflow is either folded into a file this catalog ships, or covered
by a skill, playbook, or principle that already owned the same job. This test
reads the shipped files. It does not fetch anything.
"""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHANN = "chann-mode/skills/chann"
PINNED_COMMIT = "e997ac5b9a74eab332d5e9793bb38a38c8cfdd74"

# Snapshot of skills/ at the pinned commit.
UPSTREAM = (
    "accessibility-engineering",
    "api-and-interface-design",
    "browser-testing-with-devtools",
    "ci-cd-and-automation",
    "code-review-and-quality",
    "code-simplification",
    "constraint-driven-development",
    "context-engineering",
    "debugging-and-error-recovery",
    "deprecation-and-migration",
    "documentation-and-adrs",
    "doubt-driven-development",
    "frontend-ui-engineering",
    "git-workflow-and-versioning",
    "idea-refine",
    "incremental-implementation",
    "interview-me",
    "observability-and-instrumentation",
    "performance-optimization",
    "planning-and-task-breakdown",
    "security-and-hardening",
    "shipping-and-launch",
    "source-driven-development",
    "spec-driven-development",
    "test-driven-development",
    "using-agent-skills",
)

# Behavior this catalog did not have: the file that now carries it, and a
# phrase that file uses for it.
FOLDED = {
    "spec-driven-development": (f"{CHANN}/playbooks/spec.md", "success criteria as"),
    "interview-me": (f"{CHANN}/playbooks/spec.md", "one question at a time, each with your guess"),
    "idea-refine": (f"{CHANN}/playbooks/spec.md", "widen before narrowing"),
    "api-and-interface-design": (
        f"{CHANN}/playbooks/api-design.md",
        "Write the contract before the implementation",
    ),
    "frontend-ui-engineering": (f"{CHANN}/playbooks/ui.md", "Name the states before the layout"),
    "accessibility-engineering": (
        f"{CHANN}/playbooks/ui.md",
        "Run an accessibility audit on the rendered page",
    ),
    "browser-testing-with-devtools": (f"{CHANN}/playbooks/ui.md", "Verify in a real browser"),
    "security-and-hardening": (f"{CHANN}/playbooks/security.md", "Trust follows who wrote a value"),
    "observability-and-instrumentation": (
        f"{CHANN}/playbooks/instrumentation.md",
        "Verify the telemetry itself",
    ),
    "deprecation-and-migration": (
        f"{CHANN}/playbooks/migration.md",
        "Never change stored data in place",
    ),
    "ci-cd-and-automation": (f"{CHANN}/playbooks/ci.md", "Order the gates cheapest first"),
    "shipping-and-launch": (f"{CHANN}/playbooks/launch.md", "Write the rollback before the rollout"),
    "constraint-driven-development": (
        f"{CHANN}/references/principles.md",
        "### hold-the-quality-bar",
    ),
    "using-agent-skills": (
        f"{CHANN}/references/rationalizations.md",
        "The thought that arrives just before a step is skipped",
    ),
}

# Duplicates: the owner that already did this job, a phrase proving it, and why
# a second copy was not added.
COVERED = {
    "debugging-and-error-recovery": (
        "bug-hunt/skills/bug-hunt/SKILL.md",
        "name: bug-hunt",
        "reproduce-first root-cause diagnosis is bug-hunt",
    ),
    "code-review-and-quality": (
        "interrogate/skills/interrogate/SKILL.md",
        "name: interrogate",
        "a proof-carrying review of a diff is interrogate",
    ),
    "doubt-driven-development": (
        "interrogate/skills/interrogate/SKILL.md",
        "## 5. Optional adversary panel",
        "a fresh-context adversarial pass is the interrogate panel",
    ),
    "code-simplification": (
        f"{CHANN}/playbooks/refactoring.md",
        "Pin the behavior before moving anything",
        "behavior-preserving cleanup is the refactoring playbook",
    ),
    "context-engineering": (
        f"{CHANN}/references/principles.md",
        "### guard-the-context-window",
        "context budgeting is a chann principle plus handoff and recall",
    ),
    "git-workflow-and-versioning": (
        "git-skill/skills/git-commit/SKILL.md",
        "name: git-commit",
        "atomic commits, pushes, and merges are the git-skill package",
    ),
    "incremental-implementation": (
        f"{CHANN}/references/principles.md",
        "### sequence-verifiable-units",
        "thin verified slices are the sequence-verifiable-units principle",
    ),
    "planning-and-task-breakdown": (
        f"{CHANN}/playbooks/plan.md",
        "dependency graph",
        "ordered units with a dependency graph are the plan playbook",
    ),
    "source-driven-development": (
        "research-brief/skills/research-brief/SKILL.md",
        "## 4. Pin every claim to a version",
        "answers cited from primary sources are research-brief",
    ),
    "test-driven-development": (
        f"{CHANN}/playbooks/bug-fix.md",
        "Write the check before the fix",
        "the failing-first check is required by bug-fix and bug-hunt",
    ),
    "performance-optimization": (
        f"{CHANN}/playbooks/perf.md",
        "Measure a baseline before reading code",
        "measure, explain, and keep-or-revert is the perf playbook",
    ),
    "documentation-and-adrs": (
        "doc-skill/skills/gen-docs/SKILL.md",
        "name: gen-docs",
        "project documents are gen-docs and decision history is why",
    ),
}


class AgentSkillsDispositionTests(unittest.TestCase):
    def test_the_pinned_list_has_26_names_and_one_disposition_each(self) -> None:
        self.assertEqual(26, len(UPSTREAM))
        self.assertEqual(len(UPSTREAM), len(set(UPSTREAM)))
        self.assertEqual(set(), set(FOLDED) & set(COVERED))
        self.assertEqual(set(UPSTREAM), set(FOLDED) | set(COVERED))

    def test_folded_files_contain_the_behavior(self) -> None:
        for name, (relative, marker) in FOLDED.items():
            with self.subTest(skill=name):
                self.assertIn(marker, (ROOT / relative).read_text(encoding="utf-8"))

    def test_covered_owners_exist_and_carry_a_real_reason(self) -> None:
        for name, (relative, marker, reason) in COVERED.items():
            with self.subTest(skill=name):
                self.assertIn(marker, (ROOT / relative).read_text(encoding="utf-8"))
                self.assertGreaterEqual(len(reason.split()), 5)

    def test_no_upstream_skill_is_packaged_under_its_own_name(self) -> None:
        packaged = {path.parent.name for path in ROOT.glob("*/skills/*/SKILL.md")}
        self.assertEqual(set(), set(UPSTREAM) & packaged)

    def test_every_folded_playbook_is_routed(self) -> None:
        skill = (ROOT / CHANN / "SKILL.md").read_text(encoding="utf-8")
        playbooks = {
            Path(relative).stem
            for relative, _ in FOLDED.values()
            if "/playbooks/" in relative
        }
        self.assertEqual(
            {"spec", "api-design", "ui", "security", "instrumentation", "migration", "ci", "launch"},
            playbooks,
        )
        for name in playbooks:
            with self.subTest(playbook=name):
                self.assertIn(f"| {name} |\n", skill)
                self.assertIn(f"- **{name}**:", skill)

    def test_both_readmes_pin_the_upstream_commit(self) -> None:
        for name in ("README.md", "README.ko.md"):
            text = (ROOT / "chann-mode" / name).read_text(encoding="utf-8")
            with self.subTest(readme=name):
                self.assertIn(PINNED_COMMIT, text)
                self.assertIn("test_agent_skills_disposition.py", text)


if __name__ == "__main__":
    unittest.main()
