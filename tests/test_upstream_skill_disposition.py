"""Every upstream skill name has exactly one disposition in this catalog.

The names are the skill directories pinned by the plan. This test reads the
shipped files. It does not fetch anything.
"""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRINCIPLES = ROOT / "chann-mode" / "skills" / "chann" / "references" / "principles.md"

UPSTREAM = (
    "architect",
    "arena",
    "automate-me",
    "benchmark-checklist",
    "blast-radius",
    "bro",
    "correct",
    "create-formal-verification-skill",
    "create-verification-skill",
    "figure-it-out",
    "how",
    "in-your-own-words",
    "interrogate",
    "ketchup",
    "ketchup-video",
    "maintain-formal-verification-skill",
    "maintain-verification-skill",
    "make-bot-ui",
    "no-comments",
    "poteto-help",
    "poteto-mode",
    "principle-attack-the-premise",
    "principle-boundary-discipline",
    "principle-build-the-lever",
    "principle-encode-lessons-in-structure",
    "principle-exhaust-the-design-space",
    "principle-experience-first",
    "principle-explain-the-number",
    "principle-fix-root-causes",
    "principle-foundational-thinking",
    "principle-guard-the-context-window",
    "principle-laziness-protocol",
    "principle-make-operations-idempotent",
    "principle-migrate-callers-then-delete-legacy-apis",
    "principle-minimize-reader-load",
    "principle-model-the-domain",
    "principle-never-block-on-the-human",
    "principle-outcome-oriented-execution",
    "principle-prove-it-works",
    "principle-redesign-from-first-principles",
    "principle-separate-before-serializing-shared-state",
    "principle-sequence-verifiable-units",
    "principle-subtract-before-you-add",
    "principle-test-behavior-not-implementation",
    "principle-type-system-discipline",
    "recall",
    "reflect",
    "setup-pstack",
    "sharpen",
    "show-me-your-work",
    "statechart",
    "swarm",
    "tdd",
    "teach",
    "technical-writing",
    "typescript-best-practices",
    "unslop",
    "why",
)

PACKAGED = {
    "how": "understand/skills/how/SKILL.md",
    "why": "understand/skills/why/SKILL.md",
    "recall": "recall/skills/recall/SKILL.md",
    "unslop": "unslop/skills/unslop/SKILL.md",
    "arena": "swarm/skills/arena/SKILL.md",
    "swarm": "swarm/skills/swarm/SKILL.md",
    "interrogate": "interrogate/skills/interrogate/SKILL.md",
    "blast-radius": "interrogate/skills/blast-radius/SKILL.md",
    "reflect": "skill-forge/skills/reflect/SKILL.md",
}

PORTED = {
    "no-comments": "no-comments/skills/no-comments/SKILL.md",
    "make-bot-ui": "make-bot-ui/skills/make-bot-ui/SKILL.md",
}

# One file, and a phrase that file already uses for that behavior.
FOLDED = {
    "poteto-mode": ("chann-mode/skills/chann/SKILL.md", "## 2. Routing"),
    "ketchup": ("recall/skills/catchup/SKILL.md", "while they were away"),
    "figure-it-out": ("chann-mode/skills/chann/SKILL.md", "**No playbook fits**"),
    "show-me-your-work": (
        "chann-mode/skills/chann/references/decision-trail.md",
        "ts\tphase\tdecision\twhy\tevidence\tresult",
    ),
}

# Host model selection replaces a settings file. All three files have to say so.
SETUP_MODEL_SELECTION = (
    ("chann-mode/skills/chann/SKILL.md", "Check the host's current model list"),
    ("swarm/skills/swarm/SKILL.md", "A route is `(agent, provider, model)`"),
    ("swarm/skills/arena/SKILL.md", "land on different vendors"),
)

PRINCIPLE_RENAMES = {
    "principle-migrate-callers-then-delete-legacy-apis": "migrate-callers-then-delete",
    "principle-separate-before-serializing-shared-state": "separate-before-serializing",
}

DEFERRED = {
    "architect": "open design decisions are already review-me and plan-summary",
    "automate-me": "unattended work in a session is long-task; hosted automations are out of scope",
    "benchmark-checklist": "a slowdown is bug-hunt, and a generic checklist is not its own workflow",
    "bro": "a tone of voice leaves no artifact this catalog ships",
    "correct": "fixing a known defect is bug-hunt",
    "create-formal-verification-skill": "authoring a skill package is skill-forge",
    "create-verification-skill": "authoring a skill package is skill-forge",
    "in-your-own-words": "explaining a change is diff-summary",
    "ketchup-video": "catchup is the text catch-up, and a video recap is out of scope",
    "maintain-formal-verification-skill": "no proof-assistant workflow is packaged here",
    "maintain-verification-skill": "keeping a skill in contract is skill-audit and reflect",
    "poteto-help": "the router help surface is chann",
    "sharpen": "tightening prose that is not a code comment is unslop",
    "statechart": "domain modeling stays the model-the-domain principle inside chann",
    "tdd": "a failing-first check is already required by bug-hunt and the chann verification principles",
    "teach": "explaining code is how, and a separate lesson artifact is not packaged",
    "technical-writing": "project docs are gen-docs and prose cleanup is unslop",
    "typescript-best-practices": "type rules this catalog keeps live in the chann principles",
}


def principle_section(name: str) -> str:
    return PRINCIPLE_RENAMES.get(name, name.removeprefix("principle-"))


class UpstreamSkillDispositionTests(unittest.TestCase):
    def test_the_pinned_list_has_58_names_and_one_disposition_each(self) -> None:
        self.assertEqual(58, len(UPSTREAM))
        self.assertEqual(len(UPSTREAM), len(set(UPSTREAM)))

        classified = (
            set(PACKAGED) | set(PORTED) | set(FOLDED) | set(DEFERRED) | {"setup-pstack"}
            | {name for name in UPSTREAM if name.startswith("principle-")}
        )
        self.assertEqual(set(UPSTREAM), classified)

        overlap = (
            set(PACKAGED) & set(PORTED)
            | set(PACKAGED) & set(FOLDED)
            | set(PACKAGED) & set(DEFERRED)
            | set(PORTED) & set(FOLDED)
            | set(PORTED) & set(DEFERRED)
            | set(FOLDED) & set(DEFERRED)
        )
        self.assertEqual(set(), overlap)

    def test_packaged_and_ported_skills_exist_on_disk(self) -> None:
        for name, relative in {**PACKAGED, **PORTED}.items():
            path = ROOT / relative
            with self.subTest(skill=name):
                text = path.read_text(encoding="utf-8")
                self.assertIn(f"name: {name}\n", text.split("---\n", 2)[1])

    def test_folded_files_contain_the_behavior(self) -> None:
        for name, (relative, marker) in FOLDED.items():
            with self.subTest(skill=name):
                self.assertIn(marker, (ROOT / relative).read_text(encoding="utf-8"))

        for relative, marker in SETUP_MODEL_SELECTION:
            text = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(file=relative):
                self.assertIn(marker, text)

    def test_every_principle_is_a_section_with_an_apply_when_and_a_test(self) -> None:
        text = PRINCIPLES.read_text(encoding="utf-8")
        names = [name for name in UPSTREAM if name.startswith("principle-")]
        self.assertEqual(24, len(names))
        for name in names:
            section = principle_section(name)
            with self.subTest(principle=name):
                self.assertIn(f"### {section}\n", text)
                body = text.split(f"### {section}\n", 1)[1].split("\n### ", 1)[0]
                self.assertIn("**Apply when:**", body)
                self.assertIn("**Test:**", body)
        for added in ("outcome-oriented-execution", "type-system-discipline"):
            self.assertIn(f"### {added}\n", text)

    def test_deferred_reasons_are_real_and_not_cursor_only(self) -> None:
        packaged = {path.parent.name for path in ROOT.glob("*/skills/*/SKILL.md")}
        for name, reason in DEFERRED.items():
            with self.subTest(skill=name):
                self.assertGreaterEqual(len(reason.split()), 5)
                self.assertNotIn("cursor-only", reason.lower())
                self.assertNotIn("cursor only", reason.lower())
                self.assertNotIn(name, packaged)

    def test_nothing_outside_the_four_dispositions_is_unclassified(self) -> None:
        kinds = {}
        for name in PACKAGED:
            kinds[name] = "packaged"
        for name in PORTED:
            kinds[name] = "ported"
        for name in FOLDED:
            kinds[name] = "folded"
        kinds["setup-pstack"] = "folded"
        for name in UPSTREAM:
            if name.startswith("principle-"):
                kinds[name] = "folded"
        for name in DEFERRED:
            kinds[name] = "deferred"
        self.assertEqual(set(UPSTREAM), set(kinds))
        self.assertTrue(all(kind in {"packaged", "folded", "deferred", "ported"} for kind in kinds.values()))


if __name__ == "__main__":
    unittest.main()
