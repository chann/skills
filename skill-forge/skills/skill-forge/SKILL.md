---
name: skill-forge
description: Use when a skill package must be created, renamed, split, extended, or brought back into line with the repository's skill contract, including "스킬 새로 만들어줘", "스킬 패키지 만들어", "이 스킬 규칙에 맞게 고쳐줘", "add a new skill", "scaffold a skill package", "make this skill follow the contract", "/skill-forge", or "$skill-forge". Writes SKILL.md, the Codex descriptor, the slash command, evals, catalog and locale entries, published counts, and focused tests, then proves the result with skill-audit. Use skill-audit alone to inspect without changing anything.
---

# Skill Forge

Author a skill package that satisfies every rule of the repository's skill
contract in one pass — package files, Codex descriptor, slash command, evals,
website catalog, four locales, published counts, and tests.

A skill is not finished when `SKILL.md` reads well. It is finished when a user
who has never seen it can find it, invoke it from either platform, and get the
artifact its description promised. Everything below serves that.

Read [`references/skill-package-contract.md`](references/skill-package-contract.md)
completely before writing any file. Read
[`references/description-grammar.md`](references/description-grammar.md) before
writing the description.

## 1. Fix the boundary before writing anything

Answer these four, from the request and the repository, and say the answers back
to the user in two or three sentences:

1. **What request does this fire on?** Actual phrasings, in every language the
   repository serves.
2. **What does it leave behind?** A file at a path, a commit, a decision record,
   a report. A skill with no artifact and no state change is a prompt, not a
   skill — say so and stop.
3. **Which existing skill is its nearest neighbour, and what separates them?**
   Read that neighbour's `SKILL.md`. If the separation is a mode rather than a
   workflow, extend the neighbour instead of adding a package.
4. **Which plugin owns it?** An existing plugin when the subject already has
   one; a new plugin when it does not.

Stop and ask only if the answer to 3 is that the skill would duplicate an
existing one. Everything else is decidable from the repository.

## 2. Match the house style before adding to it

Read one skill from the owning plugin end to end and copy its shape: heading
depth, imperative voice, how it names artifacts, whether it ships references or
scripts, how it phrases refusals. A package that reads like the ones beside it
is cheaper to maintain than one that is individually better.

Reuse before you add. A reference or script that already exists in the plugin is
shared, not copied — unless the plugin deliberately duplicates it so each skill
stays independently installable, in which case duplicate it byte for byte and
add it to whichever test pins those copies together.

## 3. Write the package

Create, in this order, because each file constrains the next:

```
<plugin>/
├── .claude-plugin/plugin.json      # new plugins only
├── README.md, README.ko.md         # new plugins only
├── commands/<name>.md
└── skills/<name>/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── evals/evals.json
    └── references/ templates/ assets/ scripts/   # only what the skill uses
```

**`SKILL.md`.** Frontmatter first: `name` equal to the directory, `description`
per the grammar, and `disable-model-invocation: true` only when the description
opens with `Use only when`. Then the body: what the skill produces, then the
numbered steps that produce it. Write steps as gates — each one states what must
be true before the next begins. A step the agent can skip without noticing is a
step that will be skipped.

**`agents/openai.yaml`.** Title-case display name, a short description under 90
characters with no trailing period, and a default prompt containing `$<name>`.

**`commands/<name>.md`.** Frontmatter `description`, plus `argument-hint` when
the skill takes one. The body names the skill and restates the constraints that
must survive the command layer — a user who runs the command never reads
`SKILL.md`.

**`evals/evals.json`.** At least three evals, at least two assertions each.
Assert the gates, refusals, and orderings that would break under a sloppy run.
Cover the happy path, one boundary or refusal, and one request where a sibling
skill would be the wrong choice.

**Scripts.** Standard library only, no network at import time, and every path
argument validated before use. A script exists to make a step deterministic; if
it only reformats what the model already produced, drop it.

## 4. Publish it

A skill that is not in the catalog does not exist to users, and the website
build fails on the mismatch. In the same change:

- `website/src/data/skills.ts` — the id in the `SkillId` union and a definition
  with `title`, `category`, `example`, both selectors, `aliases` when the skill
  has them, and `tags` a user would search for. A new category also needs
  `categoryOrder`.
- `website/src/i18n/content/{ko,en,jp,cn}.json` — `summary`, `whenToUse`, and
  `result` for the skill, plus `categories` copy for a new category. Translate
  presentation; never invent a capability a locale's reader cannot get.
- `website/scripts/verify-catalog.mjs` — workflow and selector counts.
- `website/scripts/generate-social-cards.mjs` — the count in the footer, then
  regenerate the four PNGs and look at them.
- Root `README.md`, `README.ko.md`, `USAGE.md`, `ARCHITECTURE.md` — the skill
  table, plugin table, install links, and both counts.
- The plugin's own `README.md` and `README.ko.md`.

## 5. Prove it

```bash
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --root .
python3 -m pytest tests -q
npm --prefix website run verify:catalog
npm --prefix website run verify:locales
npm --prefix website run build
```

The audit must report no violations. A failing rule is a missing file or a
mismatched string, never a reason to relax the rule.

Add the focused package test for a new plugin — the existing
`tests/test_*_skill_package.py` files are the model — and extend the owning
plugin's test when a skill joins an existing plugin.

## Refusals

- Do not add a skill whose description would duplicate an existing one. Extend
  the existing skill or give the new one a different artifact.
- Do not weaken a contract rule to make a package pass. Change the package.
- Do not leave the catalog, locales, counts, or social cards for a later change.
  The repository treats a half-published skill as a broken build.
- Do not copy a workflow from another catalog. Read for ideas, then write the
  package from the boundary you fixed in step 1.

## Integration

**Pairs with:** `skill-audit` for the proof step, `gen-docs` for the plugin
README pair, and `git-commit-push` to publish the finished package.

**Use instead of:** editing `SKILL.md` alone, which leaves the catalog, locales,
and counts behind.
