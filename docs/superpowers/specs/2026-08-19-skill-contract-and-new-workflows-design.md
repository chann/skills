# Design — Skill Package Contract and six new workflows

Date: 2026-08-19

## Goal

1. Add six new, self-authored workflows that cover gaps in this catalog. No
   external attribution anywhere; no name or feature duplicated from another
   catalog. Every new workflow adds capability this repository does not have.
2. Remove the remaining third-party attribution from `review-me`.
3. Publish all six on the website (catalog, four locales, counts, social cards).
4. Give every packaged skill one uniform contract, documented once and enforced
   by a script and a test.

## 1. Skill Package Contract

The repository already has an implicit layout. This design makes it explicit,
machine-checkable, and self-serviceable.

`docs/skill-package-contract.md` is the canonical statement. `AGENTS.md` links
it. `skill-forge` authors against it; `skill-audit` enforces it.

| ID | Rule |
|---|---|
| C1 | A skill lives at `<plugin>/skills/<name>/SKILL.md` and its frontmatter `name` equals `<name>`. |
| C2 | `description` is one paragraph that starts with `Use when` or `Use only when`, names at least one natural-language trigger, and contains both the `/<name>` and `$<name>` selectors. |
| C3 | Invocation mode is declared. A skill that only runs on an explicit selector sets `disable-model-invocation: true`; every other skill omits the key. |
| C4 | `skills/<name>/agents/openai.yaml` exists with `interface.display_name`, `interface.short_description`, and `interface.default_prompt`, and the default prompt contains `$<name>`. |
| C5 | `<plugin>/commands/<name>.md` exists with a `description` field. A command file that is a selector alias for another skill is allowed and must say which skill it invokes. |
| C6 | `skills/<name>/evals/evals.json` exists, `skill_name` equals `<name>`, and it holds at least three evals, each with `prompt`, `expected_output`, `files`, and at least two `assertions`. |
| C7 | The name appears in `website/src/data/skills.ts` as a catalog id or a declared alias, and every catalog id has `summary`, `whenToUse`, and `result` in all four locale files. |
| C8 | The owning plugin has `.claude-plugin/plugin.json` with `name`, `description`, and `version`. |
| C9 | Root `README.md`, `README.ko.md`, `USAGE.md`, and `ARCHITECTURE.md` publish the same workflow and selector counts as the catalog and the packaged tree. |

Enforcement:

- `skill-forge/skills/skill-audit/scripts/audit_skills.py` — stdlib-only walker
  that reports every violation as `<code> <skill> <detail>`, supports `--json`
  and `--markdown`, and exits non-zero when any rule fails.
- `tests/test_skill_contract.py` — runs the auditor over this repository and
  fails the suite on any violation.

Existing-skill fixes required by the contract:

- `review-me` description is rewritten into the house grammar (C2).
- `build-reinstall` and `gcpr` gain `disable-model-invocation: true` (C3); both
  already document themselves as explicit-only.
- Twenty-one skills that ship no `evals/evals.json` gain one (C6).

## 2. New workflows

31 canonical workflows, 32 packaged selectors, 13 plugins.

### `bug-hunt` — new plugin `bug-hunt`, category `engineering`

A defect diagnosis loop that ends in a pinned regression check and a written
record. Distinct from generic debugging advice: it persists state.

- Artifact `.bug-hunts/<YYYY-MM-DD>-<slug>.md`.
- **Hypothesis ledger.** Every hypothesis is written with the observation that
  would falsify it and the observed result. Falsified hypotheses stay in the
  record so the next session does not retry them.
- **Reproduce-first gate.** No edit to product code until a command reproduces
  the defect and that command is recorded.
- **Failing-check gate.** No fix is applied until a check fails for the defect's
  reason.
- **Widening rule.** After three falsified hypotheses inside one layer, the
  search must move to a different layer or assumption, and the record says which.
- **Instrumentation cleanup.** Temporary probes carry a fixed marker and the
  workflow proves removal by searching for that marker.
- **Redaction.** Captured output is scrubbed of secrets before it enters the record.
- `references/instrumentation-playbook.md` — probe patterns per ecosystem and
  the bisection ladder.

### `research-brief` — new plugin `research-brief`, category `engineering`

Answer a technical question from primary sources and leave a citable brief.

- Artifact `.research/<YYYY-MM-DD>-<slug>.md`.
- **Bottom line first** — direct answer plus confidence, before the evidence.
- **Claim table** — every claim carries source URL, source tier, the version or
  date it was verified against, and confidence.
- **Source tiers** — T1 primary (spec, official reference, first-party source
  code), T2 first-party secondary (changelog, maintainer post), T3 community.
  A T3 claim is labeled unverified and may not be written as fact.
- **Contradiction ledger** — disagreeing sources are both recorded with the
  resolution and the reason.
- **Open questions** are mandatory; an empty section must say why.
- Dispatches a background agent when one is available and falls back inline.

### `skill-forge` — new plugin `skill-forge`, category `authoring`

Author or extend a skill package so it satisfies the contract end to end:
package files, Codex descriptor, slash command, evals, catalog entry, four
locales, published counts, and focused tests. Ends by running `skill-audit`.

- `references/skill-package-contract.md` — the contract, restated for the agent.
- `references/description-grammar.md` — how a description earns reliable
  invocation: trigger vocabulary, selector tokens, sibling disambiguation, and
  the failure modes that make a skill fire on the wrong request.

### `skill-audit` — plugin `skill-forge`, category `authoring`

Run the contract over a skills repository and report every violation with the
exact file and the fix. Read-only unless the user asks for repairs.

- `scripts/audit_skills.py`.

### `git-resolve-conflicts` — plugin `git-skill`, category `git`

Finish an in-progress merge, rebase, or cherry-pick without aborting.

- **Classified inventory** first: source, lockfile, generated, binary, submodule.
  Each class has a fixed policy — lockfiles are regenerated from the merged
  manifest, generated files are re-produced by their generator, submodules are
  resolved by intent, never blind.
- **Intent recovery** for both sides before any hunk is touched.
- **Resolution ledger** naming, per hunk, which intent survived and why.
- Wholesale `--ours` / `--theirs` on a source file requires a recorded reason.
- Discovers and runs the project's own checks; never `git merge --abort`.

### `gen-session-handoff` — plugin `handoff`, category `handoff`

Compact the current session into a document a fresh agent can resume from.

- Artifact `.handoffs/<YYYY-MM-DD>-<slug>.md`.
- **Proven vs unproven** state, each proven claim carrying the command that
  proved it.
- Open decisions, known traps, ordered next actions with a done-check each.
- Suggested skills drawn from this catalog.
- A copyable resume prompt.
- References existing artifacts by path instead of restating them; redacts secrets.

## 3. Website and documentation

- `website/src/data/skills.ts` — two new categories (`engineering`, `authoring`)
  and six new definitions.
- Four locale files — six skill entries and two category entries each.
- `website/scripts/verify-catalog.mjs` — 31 workflows, 32 selectors.
- `website/scripts/generate-social-cards.mjs` — count 25 to 31; regenerate the
  four PNGs.
- `website/README.md` — count and locale-key notes.
- Root `README.md`, `README.ko.md`, `USAGE.md`, `ARCHITECTURE.md` — plugin table,
  skill table, install links, counts.
- New plugin `README.md` and `README.ko.md` for `bug-hunt`, `research-brief`,
  and `skill-forge`; updated ones for `git-skill` and `handoff`.

## 4. Attribution removal

- `review-me/README.md` and `review-me/README.ko.md` lose the third-party credit
  paragraph.
- `tests/test_review_me_skill_package.py` asserts the credit is absent.
- A repository-wide sweep confirms no other external credit remains in shipped
  files.

## Testing

- `tests/test_skill_contract.py` — the auditor over this repository.
- `tests/test_bug_hunt_skill_package.py`, `tests/test_research_brief_skill_package.py`,
  `tests/test_skill_forge_skill_package.py` — package contracts for the new plugins.
- Extended `tests/test_git_skill_package.py` and `tests/test_handoff_skill_package.py`
  for the two new skills and the new counts.
- `tests/test_installation_docs.py` gains the three new plugin README pairs.
- `npm --prefix website run verify:catalog`, `verify:locales`, `build`.
