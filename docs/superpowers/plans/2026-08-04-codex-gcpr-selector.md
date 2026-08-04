# Codex `$gcpr` Selector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish `$gcpr` as an actual Codex selector that delegates to the canonical `git-commit-push-realtime` workflow.

**Architecture:** Add one minimal alias skill package with Codex metadata and no copied Git policy. Keep 20 canonical website workflows while package discovery exposes 21 Codex selector packages, mapping `gcpr` back to the canonical catalog card.

**Tech Stack:** Markdown skill packages, YAML Codex interface metadata, Python unittest/pytest, TypeScript catalog data, Node verification scripts, `npx skills` installer.

## Global Constraints

- `git-commit-push-realtime` remains the only source of workflow and safety rules.
- `$git-commit-push-realtime` and `/gcpr` remain supported.
- `$gcr` is out of scope.
- Missing canonical workflow must stop `$gcpr` before any Git inspection or mutation.
- The catalog exposes 20 canonical workflows and 21 installable Codex selector packages.
- Do not update the root `VERSION` or publish a release.

---

### Task 1: Pin the alias package contract

**Files:**
- Modify: `tests/test_git_skill_package.py`
- Modify: `tests/test_installation_docs.py`

**Interfaces:**
- Consumes: `frontmatter(path: Path) -> str` and `body(path: Path) -> str` test helpers.
- Produces: package assertions for `git-skill/skills/gcpr/SKILL.md` and `agents/openai.yaml`.

- [ ] **Step 1: Write failing package tests**

Add constants and assertions equivalent to:

```python
CODEX_ALIAS_SKILL = GIT_SKILL / "skills" / REALTIME_ALIAS

def test_codex_realtime_alias_is_a_thin_skill_package(self) -> None:
    skill = CODEX_ALIAS_SKILL / "SKILL.md"
    interface = CODEX_ALIAS_SKILL / "agents" / "openai.yaml"
    self.assertTrue(skill.is_file())
    self.assertTrue(interface.is_file())
    self.assertIn("name: gcpr", frontmatter(skill))
    self.assertIn("$gcpr", frontmatter(skill))
    self.assertIn("git-commit-push-realtime", skill.read_text(encoding="utf-8"))
    self.assertNotIn("git push", body(skill))
    self.assertIn("$gcpr", interface.read_text(encoding="utf-8"))
```

Change the published count test to assert 21 packaged selector `SKILL.md` files while retaining the documented 20 canonical workflows. Keep the generic interface test responsible for checking that every discovered selector has a matching command wrapper and `agents/openai.yaml`.

- [ ] **Step 2: Run the narrow tests and confirm the intended failure**

Run:

```bash
python3 -m pytest tests/test_git_skill_package.py tests/test_installation_docs.py -q
```

Expected: failure because `git-skill/skills/gcpr/` does not exist and the packaged selector count is still pinned to 20.

### Task 2: Add the thin Codex alias package

**Files:**
- Create: `git-skill/skills/gcpr/SKILL.md`
- Create: `git-skill/skills/gcpr/agents/openai.yaml`
- Modify: `git-skill/.claude-plugin/plugin.json`

**Interfaces:**
- Consumes: installed `git-commit-push-realtime` skill and its shared `git-commit` / `git-commit-push` dependencies.
- Produces: exact selector `$gcpr` and Codex interface metadata.

- [ ] **Step 1: Create the minimal alias workflow**

Use this behavior in `SKILL.md`:

```markdown
---
name: gcpr
description: Use when the user explicitly invokes /gcpr or $gcpr as the short alias for /git-commit-push-realtime or $git-commit-push-realtime.
---

# GCPR

This skill is only a selector alias for `git-commit-push-realtime`.

Before inspecting or mutating any Git repository, locate the installed
`git-commit-push-realtime` skill, read its `SKILL.md` completely, and follow it
exactly, including every required shared workflow.

If the canonical skill is unavailable, stop before any Git command and report
that `git-commit-push-realtime` must also be installed. Do not recreate,
summarize, or weaken the canonical workflow in this alias.
```

- [ ] **Step 2: Add Codex interface metadata**

Create `agents/openai.yaml` with exactly these fields:

```yaml
interface:
  display_name: "GCPR"
  short_description: "Alias for verified realtime commit and push"
  default_prompt: "Use $gcpr to commit and push each verified outcome while working."
```

- [ ] **Step 3: Bump the git plugin minor version**

Change `git-skill/.claude-plugin/plugin.json` from `0.7.0` to `0.8.0`, then update the pinned version assertion in `tests/test_git_skill_package.py`.

- [ ] **Step 4: Run the package tests**

Run:

```bash
python3 -m pytest tests/test_git_skill_package.py tests/test_installation_docs.py -q
```

Expected: alias-package assertions pass; documentation/count assertions may remain red until Task 3.

### Task 3: Represent the alias without duplicating the workflow catalog

**Files:**
- Modify: `website/src/data/skills.ts`
- Modify: `website/scripts/verify-catalog.mjs`
- Modify: `website/src/i18n/content/ko.json`
- Modify: `website/src/i18n/content/en.json`
- Modify: `website/src/i18n/content/jp.json`
- Modify: `website/src/i18n/content/cn.json`

**Interfaces:**
- Consumes: `SkillDefinition.aliases?: string[]` and repository skill frontmatter names.
- Produces: one canonical realtime card searchable by `/gcpr` and `$gcpr`, plus verification of 20 workflows against 21 selector packages.

- [ ] **Step 1: Extend the canonical card aliases**

Change the realtime definition to:

```ts
aliases: ["/gcpr", "$gcpr"],
```

Do not add `gcpr` to `SkillId` or add a second catalog definition.

- [ ] **Step 2: Teach catalog verification about selector aliases**

Parse every `aliases: [...]` entry, normalize leading `/` and `$`, and build a unique represented-name set from canonical IDs plus aliases. Verify:

```js
const represented = new Set([...catalog, ...catalogAliases(catalogSource)]);
const missingFromCatalog = packaged.filter((name) => !represented.has(name));
const missingFromPackages = catalog.filter((name) => !packaged.includes(name));
```

Reject duplicate aliases and aliases that collide with a different canonical ID. Finish with `Catalog matches 20 workflows and 21 packaged selectors.`

- [ ] **Step 3: Correct user-facing count terminology**

In all four locale files, change hero proof wording from “packaged skills” to the locale-equivalent of “canonical workflows.” Keep the dynamic `{count}` value at 20 and do not add a duplicate localized `gcpr` skill record.

- [ ] **Step 4: Verify the catalog and locales**

Run:

```bash
npm --prefix website run verify:catalog
npm --prefix website run verify:locales
```

Expected: `Catalog matches 20 workflows and 21 packaged selectors.` and locale verification passes.

### Task 4: Update package documentation and architecture

**Files:**
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `USAGE.md`
- Modify: `ARCHITECTURE.md`
- Modify: `git-skill/README.md`
- Modify: `git-skill/README.ko.md`

**Interfaces:**
- Consumes: the canonical workflow name and the new `gcpr` selector package.
- Produces: install and invocation instructions that distinguish workflows from selectors.

- [ ] **Step 1: Publish both Codex selectors**

Change every relevant Git selector table cell to:

```text
$git-commit-push-realtime · $gcpr
```

Keep `/git-commit-push-realtime · /gcpr` in the Claude Code column.

- [ ] **Step 2: Document installation dependencies**

Add `--skill gcpr` to both complete git-skill install commands. Add an alias-only setup example that selects `gcpr`, `git-commit-push-realtime`, `git-commit`, and `git-commit-push` together.

- [ ] **Step 3: Update architecture and counts**

Describe 20 canonical workflows and 21 Codex selector packages. Add `gcpr` to the git-skill tree as a thin selector wrapper and update the plugin table to `0.8.0` without calling the alias a new workflow.

- [ ] **Step 4: Run documentation/package verification**

Run:

```bash
python3 -m pytest tests/test_git_skill_package.py tests/test_installation_docs.py -q
npm --prefix website run verify:catalog
git diff --check
```

Expected: all commands pass.

### Task 5: Prove installation and activate locally

**Files:**
- Verify only: temporary directory created with `mktemp -d`
- Install: `/Users/channprj/.agents/skills/gcpr/`

**Interfaces:**
- Consumes: local repository package through `npx skills add .`.
- Produces: installed Codex selector `$gcpr`; a fresh session is required for discovery.

- [ ] **Step 1: Verify repository discovery**

Run:

```bash
npx --yes skills add . --list --full-depth
```

Expected: `Found 21 skills` and a `gcpr` entry.

- [ ] **Step 2: Verify an isolated Codex installation**

Run:

```bash
gcpr_test_dir=$(mktemp -d)
cd "$gcpr_test_dir"
npx --yes skills add /Volumes/990EVO+/workspace/chann/skills \
  --skill gcpr \
  --skill git-commit-push-realtime \
  --skill git-commit \
  --skill git-commit-push \
  --agent codex \
  --yes \
  --full-depth
test -f .agents/skills/gcpr/SKILL.md
test -f .agents/skills/git-commit-push-realtime/SKILL.md
test -f .agents/skills/git-commit/SKILL.md
test -f .agents/skills/git-commit-push/SKILL.md
```

Expected: installation succeeds and all four assertions return zero.

- [ ] **Step 3: Install the new selector globally**

Run:

```bash
npx --yes skills add . --skill gcpr --agent codex --global --yes --full-depth
```

Then compare the installed `gcpr/SKILL.md` and `agents/openai.yaml` byte-for-byte with the repository sources.

- [ ] **Step 4: Commit and push the verified selector outcome**

Stage only the alias, tests, catalog, and related documentation paths. Commit:

```bash
git commit -m "feat(git): add Codex gcpr selector"
git push
```

Verify `git rev-list --left-right --count HEAD...@{u}` returns `0 0`.
