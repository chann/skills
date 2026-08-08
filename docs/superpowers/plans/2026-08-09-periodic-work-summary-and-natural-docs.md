# Periodic Work Summary And Natural Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add quarterly/yearly work-summary storage and optional, dependency-free natural Korean prose to the repository's document generators.

**Architecture:** Keep every exact selector self-contained. `work-summary` owns its calendar range and default-path table; each prose generator owns a compact fallback writing contract and may use `human-friendly-writing` only when the runtime already exposes it.

**Tech Stack:** Markdown skill packages, JSON eval fixtures, Python `unittest`/`pytest`, `npx skills`, Vite catalog build, Git.

## Global Constraints

- `human-friendly-writing` is optional and must never be installed, fetched, or required by another selector.
- Missing optional writing support must not stop, warn, reduce, or otherwise change document generation.
- Preserve facts, numbers, dates, identifiers, commands, quotes, links, parser-significant labels, and bilingual alignment.
- Current periods end now; previous quarter/year ranges cover complete local calendar periods.
- Generated work reports are never staged or committed.
- Use explicit Git staging paths and push each green checkpoint immediately.

---

### Task 1: Commit the approved design and implementation plan

**Files:**
- Create: `docs/superpowers/specs/2026-08-09-periodic-work-summary-and-natural-docs-design.md`
- Create: `docs/superpowers/plans/2026-08-09-periodic-work-summary-and-natural-docs.md`

**Interfaces:**
- Consumes: the user's quarterly storage and optional-writing requirements.
- Produces: the exact range, path, selector-scope, dependency, and verification decisions used below.

- [ ] **Step 1: Scan both documents for placeholders and contradictions**

Run:

```bash
rg -n 'T[B]D|T[O]DO|F[I]XME|implement[ ]later|fill[ ]in[ ]details' \
  docs/superpowers/specs/2026-08-09-periodic-work-summary-and-natural-docs-design.md \
  docs/superpowers/plans/2026-08-09-periodic-work-summary-and-natural-docs.md
```

Expected: no matches.

- [ ] **Step 2: Verify Markdown diff hygiene**

Run: `git diff --check -- docs/superpowers/specs/2026-08-09-periodic-work-summary-and-natural-docs-design.md docs/superpowers/plans/2026-08-09-periodic-work-summary-and-natural-docs.md`

Expected: exit 0 with no output.

- [ ] **Step 3: Commit and push the ignored, explicitly selected documents**

```bash
git add -f docs/superpowers/specs/2026-08-09-periodic-work-summary-and-natural-docs-design.md docs/superpowers/plans/2026-08-09-periodic-work-summary-and-natural-docs.md
git commit -m "docs(workflows): design periodic summaries and natural prose"
git push
```

Expected: upstream parity `0 0`.

### Task 2: Add calendar periods and classified work-summary storage

**Files:**
- Modify: `tests/test_work_summary_skill_package.py`
- Modify: `work-summary/skills/work-summary/evals/evals.json`
- Modify: `work-summary/skills/work-summary/SKILL.md`
- Modify: `work-summary/commands/work-summary.md`
- Modify: `work-summary/README.md`
- Modify: `work-summary/README.ko.md`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `USAGE.md`
- Modify: `ARCHITECTURE.md`

**Interfaces:**
- Consumes: local calendar time, requested range syntax, explicit output path, and detailed/summary depth.
- Produces: `this/last quarter`, `this/last year`, and the `daily|weekly|monthly|quarterly|yearly|custom` default path table.

- [ ] **Step 1: Write the failing package-contract test**

Extend `test_skill_defines_the_date_range_grammar` and the report contract test with literal expectations for:

```python
"`this quarter` / `last quarter`"
"`this year` / `last year`"
".work-summaries/quarterly/<YYYY>/<YYYY-Qn>[-detailed].md"
".work-summaries/yearly/<YYYY>[-detailed].md"
"explicit output path"
```

Change the eval ID expectation from `[1, 2, 3, 4]` to `[1, 2, 3, 4, 5]` and require a quarterly-save prompt.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python3 -m pytest tests/test_work_summary_skill_package.py -q`

Expected: FAIL because the current skill has no quarter/year grammar or classified path contract.

- [ ] **Step 3: Implement the minimal range and path contract**

Add calendar-quarter/year rows, explicit local boundaries, and this exact default taxonomy to `SKILL.md`:

```text
daily/<YYYY>/<YYYY-MM-DD>[-detailed].md
weekly/<ISO-week-year>/<YYYY-Www>[-detailed].md
monthly/<YYYY>/<YYYY-MM>[-detailed].md
quarterly/<YYYY>/<YYYY-Qn>[-detailed].md
yearly/<YYYY>[-detailed].md
custom/<start>--<end>[-detailed].md
```

Classification follows request syntax; an explicit output path overrides it. Update the command, package docs, root docs, and architecture without changing the privacy rules.

- [ ] **Step 4: Add the behavioral eval**

Add eval ID 5 with prompt `Save a detailed work summary for last quarter.` It must assert complete local calendar-quarter boundaries, `.work-summaries/quarterly/<YYYY>/<YYYY-Qn>-detailed.md`, and no staging/commit.

- [ ] **Step 5: Run focused verification**

Run:

```bash
python3 -m pytest tests/test_work_summary_skill_package.py tests/test_installation_docs.py -q
git diff --check
```

Expected: all tests pass and diff check is clean.

- [ ] **Step 6: Commit and push**

Stage only the Task 2 paths and commit:

```text
feat(work-summary): add periodic report storage
```

Expected: upstream parity `0 0`.

### Task 3: Add optional natural Korean prose without selector dependencies

**Files:**
- Create: `tests/test_optional_human_friendly_writing_contract.py`
- Modify: `doc-skill/skills/gen-docs/SKILL.md`
- Modify: `handoff/skills/gen-frontend-handoff/SKILL.md`
- Modify: `handoff/skills/gen-backend-handoff/SKILL.md`
- Modify: `plan-summary/skills/plan-summary/SKILL.md`
- Modify: `plan-summary/skills/plan-summary-md/references/plan-summary-workflow.md`
- Modify: `plan-summary/skills/plan-summary-quiz/references/plan-summary-workflow.md`
- Modify: `work-summary/skills/work-summary/SKILL.md`
- Modify: `work-summary/skills/work-summary/evals/evals.json`
- Modify: package `README.md` and `README.ko.md` files for doc-skill, handoff, plan-summary, and work-summary
- Modify: `README.md`, `README.ko.md`, `USAGE.md`, and `ARCHITECTURE.md`

**Interfaces:**
- Consumes: newly authored Korean prose plus optional runtime availability of `human-friendly-writing`.
- Produces: complete standalone output in all cases; when available, the optional pass changes wording only and normal validation reruns afterward.

- [ ] **Step 1: Write the failing cross-package contract test**

Create a table-driven test over the seven selector SKILL files. Each selector must state that it:

```python
required = (
    "plain, concrete Korean prose",
    "human-friendly-writing",
    "optional",
    "do not install",
    "continue",
    "normal validation",
)
```

The test must reject `REQUIRED SUB-SKILL: human-friendly-writing` and any separate package metadata dependency.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python3 -m pytest tests/test_optional_human_friendly_writing_contract.py -q`

Expected: FAIL for every current generator because none defines the optional/fallback behavior.

- [ ] **Step 3: Add the compact fallback and optional-pass contract**

In every base workflow, require natural Korean prose while preserving fixed evidence and structure. If the runtime exposes `human-friendly-writing`, apply it only to newly authored Korean prose before writing artifacts. If absent or unreadable, continue silently; do not install, fetch, or require it. Rerun each selector's normal validation.

For `plan-summary`, copy the updated authoritative body byte-for-byte into both variant references so exact-selector installation remains standalone and the existing synchronization test stays green.

- [ ] **Step 4: Add missing-support eval coverage**

Add work-summary eval ID 6: save a Korean report when `human-friendly-writing` is unavailable. Assert complete report generation, natural fallback prose, no installation attempt, and unchanged evidence.

- [ ] **Step 5: Update user-facing documentation**

Document the optional enhancement in each affected package and the root usage/architecture docs. Do not change installation commands to include `human-friendly-writing` and do not describe it as required.

- [ ] **Step 6: Run focused and standalone verification**

Run:

```bash
python3 -m pytest \
  tests/test_optional_human_friendly_writing_contract.py \
  tests/test_doc_skill_package.py \
  tests/test_handoff_skill_package.py \
  tests/test_plan_summary_skill_package.py \
  tests/test_work_summary_skill_package.py \
  tests/test_installation_docs.py -q
```

Expected: all tests pass, including the existing exact-selector installation and artifact generation for all three plan-summary selectors without `human-friendly-writing`.

- [ ] **Step 7: Commit and push**

Stage only the Task 3 paths and commit:

```text
feat(docs): add optional natural Korean prose pass
```

Expected: upstream parity `0 0`.

### Task 4: Completion audit

**Files:**
- Verify: all files changed by Tasks 1–3.

**Interfaces:**
- Consumes: the complete committed implementation.
- Produces: repository-wide proof and remote parity.

- [ ] **Step 1: Run full repository gates**

```bash
python3 -m pytest tests/ -q
npm --prefix website run build
git diff --check
```

Expected: all commands pass without warnings attributable to this change.

- [ ] **Step 2: Audit the dependency boundary**

Run searches proving no manifest or install command makes `human-friendly-writing` mandatory and every in-scope selector contains its fallback contract.

- [ ] **Step 3: Prove clean remote parity**

```bash
git log --oneline <starting-commit>..HEAD
git status --short --branch
git rev-list --left-right --count HEAD...@{u}
```

Expected: clean tree and `0 0`.
