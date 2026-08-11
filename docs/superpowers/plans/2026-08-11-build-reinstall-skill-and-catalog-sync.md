# Build Reinstall Skill And Catalog Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one explicitly invoked, Claude Code/Codex-compatible workflow that builds a project, reinstalls the new result, verifies the installed copy, and remains synchronized with the multilingual website.

**Architecture:** Package `build-reinstall` as an independent repository plugin whose portable `SKILL.md` discovers project-owned commands or reads optional `.build-reinstall.yaml`. Keep the website catalog manually authored for useful localized copy, enforce package/catalog shape with existing verifiers, and add a root `AGENTS.md` rule for semantic lifecycle updates.

**Tech Stack:** Markdown skill packages, YAML reference data, Claude Code plugin metadata, Codex `agents/openai.yaml`, Python `unittest`/`pytest`, `npx skills`, TypeScript/Vite, GitHub Pages, Git.

## Global Constraints

- Run only after explicit `/build-reinstall` or `$build-reinstall` invocation; do not add a completion hook.
- Treat `.build-reinstall.yaml` as optional and support only `version: 1`.
- Prefer project-owned instructions and commands; never guess a reinstall command from a framework name alone.
- Show exact build, reinstall, target, verification, and artifact-comparison values before execution.
- Never add `sudo`, force flags, broad recursive deletion, a release, a deployment, a commit, or a push without a separate user request.
- Stop before reinstall on build failure, missing build output, ambiguous target, or unresolved privilege requirement.
- Do not report success until configured smoke checks and SHA-256 artifact comparisons pass.
- Preserve explicit `/build-reinstall` and `$build-reinstall` selectors across package docs, root docs, and the website.
- Use explicit Git staging paths and immediately push every green Conventional Commit checkpoint.
- Work sequentially in the main thread because the repository `AGENTS.md` compatibility instructions disallow subagent dispatch.

---

### Task 1: Commit the approved implementation plan

**Files:**
- Existing: `docs/superpowers/specs/2026-08-11-build-reinstall-skill-and-catalog-sync-design.md`
- Create: `docs/superpowers/plans/2026-08-11-build-reinstall-skill-and-catalog-sync.md`

**Interfaces:**
- Consumes: the approved design and the user's request for a reference YAML file.
- Produces: exact package, configuration, website, maintenance, testing, and publication steps for Tasks 2–4.

- [ ] **Step 1: Check design-to-plan coverage**

Confirm the plan covers all five design goals, both platform selectors, the
optional YAML schema, preflight/build/reinstall/verify ordering, safety rules,
all four website locales, `AGENTS.md`, exact-selector installation, and live
Pages verification.

- [ ] **Step 2: Scan for incomplete instructions**

Run:

```bash
rg -n 'T[B]D|T[O]DO|F[I]XME|implement[ ]later|fill[ ]in[ ]details' \
  docs/superpowers/specs/2026-08-11-build-reinstall-skill-and-catalog-sync-design.md \
  docs/superpowers/plans/2026-08-11-build-reinstall-skill-and-catalog-sync.md
```

Expected: no matches.

- [ ] **Step 3: Verify Markdown diff hygiene**

Run:

```bash
git diff --check -- \
  docs/superpowers/plans/2026-08-11-build-reinstall-skill-and-catalog-sync.md
```

Expected: exit 0 with no output.

- [ ] **Step 4: Commit and push the ignored plan explicitly**

```bash
git add -f -- docs/superpowers/plans/2026-08-11-build-reinstall-skill-and-catalog-sync.md
git commit -m "docs(build-reinstall): plan skill and catalog rollout"
git push
git rev-list --left-right --count HEAD...@{u}
```

Expected: the pushed plan commit and parity `0 0`.

### Task 2: Package the portable build-reinstall workflow

**Files:**
- Create: `tests/test_build_reinstall_skill_package.py`
- Create: `build-reinstall/.claude-plugin/plugin.json`
- Create: `build-reinstall/commands/build-reinstall.md`
- Create: `build-reinstall/skills/build-reinstall/SKILL.md`
- Create: `build-reinstall/skills/build-reinstall/agents/openai.yaml`
- Create: `build-reinstall/skills/build-reinstall/references/build-reinstall.example.yaml`
- Create: `build-reinstall/README.md`
- Create: `build-reinstall/README.ko.md`
- Modify: `tests/test_installation_docs.py`
- Modify: `tests/test_git_skill_package.py`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `USAGE.md`
- Modify: `ARCHITECTURE.md`

**Interfaces:**
- Consumes: repository instructions, optional root `.build-reinstall.yaml`, project-owned commands, built artifact paths, installed target paths.
- Produces: a displayed execution plan followed by ordered build, output proof, reinstall, smoke checks, SHA-256 comparisons, and an evidence-separated result report.

- [ ] **Step 1: Write the failing package test**

Create `tests/test_build_reinstall_skill_package.py` with these concrete checks:

```python
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "build-reinstall"
SKILL = PACKAGE / "skills" / "build-reinstall"


class BuildReinstallSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = (
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "build-reinstall.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "references" / "build-reinstall.example.yaml",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
        )
        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_interfaces_publish_both_explicit_selectors(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        command = (PACKAGE / "commands" / "build-reinstall.md").read_text(encoding="utf-8")
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertEqual("build-reinstall", metadata["name"])
        self.assertEqual("0.1.0", metadata["version"])
        self.assertIn("Use the **build-reinstall** skill", command)
        self.assertIn("/build-reinstall", skill.split("---\n", 2)[1])
        self.assertIn("$build-reinstall", skill.split("---\n", 2)[1])
        self.assertIn("$build-reinstall", openai)

    def test_skill_orders_build_reinstall_and_installed_proof(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        ordered = [
            "## 1. Preflight",
            "## 2. Build",
            "## 3. Resolve the build output",
            "## 4. Reinstall",
            "## 5. Verify the installed result",
            "## 6. Report",
        ]
        positions = [text.index(heading) for heading in ordered]
        self.assertEqual(positions, sorted(positions))
        for value in ("SHA-256", "smoke", "installed", "build failure"):
            self.assertIn(value, text)

    def test_example_yaml_defines_version_one_and_explicit_targets(self) -> None:
        text = (SKILL / "references" / "build-reinstall.example.yaml").read_text(
            encoding="utf-8"
        )
        for value in (
            "version: 1",
            'working_directory: "."',
            "build:",
            "reinstall:",
            "targets:",
            "verify:",
            "artifacts:",
            'compare: "sha256"',
        ):
            self.assertIn(value, text)

    def test_exact_selector_installs_for_codex(self) -> None:
        environment = os.environ.copy()
        environment.update({"NO_COLOR": "1", "FORCE_COLOR": "0"})
        with tempfile.TemporaryDirectory() as target:
            subprocess.run(["git", "init", "-q"], cwd=target, check=True)
            result = subprocess.run(
                [
                    "npx", "--yes", "skills", "add", str(PACKAGE),
                    "--skill", "build-reinstall", "--agent", "codex",
                    "--copy", "--yes", "--full-depth",
                ],
                cwd=target,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=60,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            installed = Path(target) / ".agents" / "skills" / "build-reinstall"
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertTrue(
                (installed / "references" / "build-reinstall.example.yaml").is_file()
            )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python3 -m pytest tests/test_build_reinstall_skill_package.py -q
```

Expected: FAIL because the `build-reinstall` package does not exist.

- [ ] **Step 3: Initialize the skill skeleton with Codex metadata**

Create only the parent directories needed by the repository plugin layout,
then run the required skill creator:

```bash
mkdir -p build-reinstall/skills
python3 /Volumes/990EVO+/system/dotfiles/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  build-reinstall \
  --path build-reinstall/skills \
  --resources references \
  --interface 'display_name=Build and Reinstall' \
  --interface 'short_description=Build, reinstall, and verify a local project artifact' \
  --interface 'default_prompt=Use $build-reinstall to build this project, reinstall the new result, and verify the installed copy.'
```

Expected: generated `SKILL.md`, `agents/openai.yaml`, and `references/` under
`build-reinstall/skills/build-reinstall/`, with no example placeholders kept.

- [ ] **Step 4: Implement the portable workflow and example YAML**

Write `SKILL.md` with only `name` and `description` in frontmatter. The
description must name `/build-reinstall`, `$build-reinstall`, explicit
invocation, build, reinstall, and installed-copy verification. The body must:

1. resolve the repository root and applicable instructions;
2. read `.build-reinstall.yaml` first when present;
3. otherwise inspect project docs, manifests, task runners, scripts, and CI;
4. show exact commands, targets, and checks before execution;
5. follow the six ordered headings tested in Step 1;
6. stop on build failure before changing the installed copy;
7. reject unresolved targets, `sudo`, force flags, broad deletion, releases,
   deployments, commits, and pushes outside separate authorization;
8. verify smoke commands and built/installed SHA-256 equality;
9. report unavailable GUI, device, signing, notarization, and permission proof
   separately.

Write the packaged YAML with these exact values:

```yaml
version: 1
working_directory: "."

build:
  commands:
    - "pnpm build"

reinstall:
  commands:
    - "pnpm install:app"
  targets:
    - "/Applications/Example.app"

verify:
  commands:
    - "pnpm smoke:app"
  artifacts:
    - built: "src-tauri/target/release/bundle/macos/Example.app/Contents/MacOS/Example"
      installed: "/Applications/Example.app/Contents/MacOS/Example"
      compare: "sha256"
```

- [ ] **Step 5: Add Claude wrapper, plugin metadata, and bilingual package docs**

Set `.claude-plugin/plugin.json` to name `build-reinstall`, version `0.1.0`,
and a factual build/reinstall/verification description. Make
`commands/build-reinstall.md` a thin router with `argument-hint:
"[project-root]"`, `$ARGUMENTS`, and no duplicated workflow.

Both package READMEs must show exactly these global and project-local installs:

```bash
npx skills add -y -g chann/skills --skill build-reinstall
npx skills add chann/skills --skill build-reinstall
```

Document `/build-reinstall [project-root]`, `$build-reinstall [project-root]`,
the optional copy from
`references/build-reinstall.example.yaml` to `.build-reinstall.yaml`, the six
execution stages, safety boundaries, and verification result.

- [ ] **Step 6: Update root package documentation and pinned package tests**

Change the public totals from 24 workflows, 25 selectors, 9 plugins to 25
workflows, 26 selectors, 10 plugins in `README.md`, `README.ko.md`, `USAGE.md`,
and `ARCHITECTURE.md`. Add `build-reinstall` to each plugin table/list,
installation list, exact selector table, quick reference, command reference,
architecture tree, plugin internals, and invocation output description.

In `tests/test_installation_docs.py`, add both build-reinstall READMEs to
`INSTALL_DOCS`, change the expected skill count to 26, and change the root-doc
count checks to 25/26/10. In `tests/test_git_skill_package.py`, change the
packaged count to 26 and the four exact count phrases to 25 workflows and 26
selectors.

- [ ] **Step 7: Validate the package and exact-selector installation**

Run:

```bash
python3 /Volumes/990EVO+/system/dotfiles/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  build-reinstall/skills/build-reinstall
python3 -m pytest \
  tests/test_build_reinstall_skill_package.py \
  tests/test_installation_docs.py \
  tests/test_git_skill_package.py -q
git diff --check
```

Expected: skill validation succeeds, all focused tests pass, the exact Codex
selector installation contains its YAML reference, and the diff is clean.

- [ ] **Step 8: Commit and push the complete package**

Stage only Task 2 paths and commit:

```text
feat(build-reinstall): package verified reinstall workflow
```

Push normally and require `git rev-list --left-right --count HEAD...@{u}` to
return `0 0` before starting Task 3.

### Task 3: Publish the website entry and skill lifecycle instructions

**Files:**
- Create: `AGENTS.md`
- Create: `tests/test_skill_website_sync_contract.py`
- Modify: `website/src/data/skills.ts`
- Modify: `website/src/i18n/content/ko.json`
- Modify: `website/src/i18n/content/en.json`
- Modify: `website/src/i18n/content/jp.json`
- Modify: `website/src/i18n/content/cn.json`
- Modify: `website/scripts/verify-catalog.mjs`
- Modify: `website/scripts/verify-locales.mjs`
- Modify: `website/scripts/generate-social-cards.mjs`
- Modify: `website/public/assets/skills-social-card-ko.png`
- Modify: `website/public/assets/skills-social-card-en.png`
- Modify: `website/public/assets/skills-social-card-jp.png`
- Modify: `website/public/assets/skills-social-card-cn.png`
- Modify: `website/README.md`

**Interfaces:**
- Consumes: packaged `SKILL.md` frontmatter names and manually authored localized descriptions.
- Produces: one automation-category catalog row, four matching locale entries, 25-workflow/26-selector structural checks, updated social cards, and repository instructions covering every skill lifecycle operation.

- [ ] **Step 1: Prove the current website rejects the new package**

Run after Task 2:

```bash
npm --prefix website run verify:catalog
npm --prefix website run verify:locales
```

Expected: `verify:catalog` fails because `build-reinstall` is missing from the
catalog and totals remain 24/25. `verify:locales` still passes before the
catalog entry is added.

- [ ] **Step 2: Write the failing lifecycle-instruction test**

Create `tests/test_skill_website_sync_contract.py`:

```python
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillWebsiteSyncContractTests(unittest.TestCase):
    def test_agents_instructions_cover_every_skill_lifecycle_change(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for phrase in (
            "add",
            "modify",
            "delete",
            "website/src/data/skills.ts",
            "website/src/i18n/content/ko.json",
            "website/src/i18n/content/en.json",
            "website/src/i18n/content/jp.json",
            "website/src/i18n/content/cn.json",
            "npm --prefix website run verify:catalog",
            "npm --prefix website run verify:locales",
            "npm --prefix website run build",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
```

Run: `python3 -m pytest tests/test_skill_website_sync_contract.py -q`

Expected: FAIL because root `AGENTS.md` does not exist.

- [ ] **Step 3: Add the catalog definition and four localized entries**

Add `build-reinstall` to `SkillId` and to `skillDefinitions` after
`long-task`, using:

```ts
{
  id: "build-reinstall",
  title: "Build and Reinstall",
  category: "automation",
  example: "$build-reinstall",
  claudeSelector: "/build-reinstall",
  codexSelector: "$build-reinstall",
  tags: ["build", "install", "reinstall", "artifact", "verification"],
}
```

Add these exact localized meanings:

```text
ko.summary: 프로젝트가 정한 명령으로 새 빌드를 만들고 다시 설치한 뒤 설치 결과가 새 빌드와 같은지 확인합니다.
ko.whenToUse: 코드 작업을 마친 뒤 로컬 앱이나 CLI를 새 빌드로 교체해야 할 때
ko.result: 빌드·재설치·스모크 검사 결과와 SHA-256으로 확인한 설치 파일

en.summary: Build the current project, reinstall it with project-owned commands, and verify that the installed result matches the new build.
en.whenToUse: After code work is complete and a local app or CLI must be replaced with the new build
en.result: Build, reinstall, smoke-check, and SHA-256 installed-artifact evidence

jp.summary: プロジェクト所定のコマンドでビルドして再インストールし、インストール結果が新しいビルドと一致することを確認します。
jp.whenToUse: コード作業の完了後、ローカルのアプリやCLIを新しいビルドへ入れ替えるとき
jp.result: ビルド、再インストール、スモークチェックの結果と、SHA-256で確認したインストール済みファイル

cn.summary: 使用项目规定的命令构建并重新安装，然后验证已安装结果与新构建一致。
cn.whenToUse: 完成代码工作后，需要用新构建替换本地应用或CLI时
cn.result: 构建、重新安装、冒烟检查结果，以及通过SHA-256确认的已安装文件
```

Change catalog and locale fixed totals from 24 workflows/25 selectors to 25
workflows/26 selectors.

- [ ] **Step 4: Add root AGENTS.md lifecycle instructions**

Write one concise section that requires the same change to update the website
when a packaged `*/skills/*/SKILL.md` is added, modified, renamed, or deleted.
Name all five catalog/locale files explicitly. Require semantic review when
purpose, selector, alias, example, category, or user-visible behavior changes;
require stale entries to be removed; require public counts, root docs, website
README, social-card copy, and pinned tests to be adjusted; and require the
three exact website verification commands tested in Step 2.

State that these instructions maintain the catalog only and do not cause
`build-reinstall` to run automatically.

- [ ] **Step 5: Update website documentation and social cards**

Change `website/README.md` from 24 to 25 workflows and locale skill IDs. Change
all four `generate-social-cards.mjs` footers from 24 to 25, then run:

```bash
node website/scripts/generate-social-cards.mjs
npm --prefix website run verify:social-cards
```

Inspect all four 1200×630 PNGs before staging them. The only intended visual
content change is the footer count.

- [ ] **Step 6: Run site and lifecycle verification**

```bash
python3 -m pytest \
  tests/test_skill_website_sync_contract.py \
  tests/test_build_reinstall_skill_package.py \
  tests/test_installation_docs.py \
  tests/test_git_skill_package.py -q
npm --prefix website run verify:catalog
npm --prefix website run verify:locales
npm --prefix website run build
git diff --check
```

Expected: all tests pass, the catalog reports 25 workflows and 26 packaged
selectors, all four locale shapes match, the production site builds, and the
diff is clean.

- [ ] **Step 7: Commit and push the website lifecycle outcome**

Stage only Task 3 paths and commit:

```text
feat(site): publish build-reinstall workflow
```

Push normally and require upstream parity `0 0`.

### Task 4: Review, installation proof, deployment proof, and completion audit

**Files:**
- Verify: every file changed in Tasks 1–3.
- Installed test copy: a temporary Git repository under a temporary directory.
- Live site: `https://chann.github.io/skills/` and locale paths `/en/`, `/jp/`, `/cn/`.

**Interfaces:**
- Consumes: the complete pushed implementation and GitHub Pages run triggered by Task 3.
- Produces: independent diff review, full repository proof, exact-selector installation proof, live catalog proof, clean worktree, and local/tracking/live-remote equality.

- [ ] **Step 1: Review the complete implementation diff**

Review `2e0c728..HEAD` for correctness, safety, maintainability, tests, project
standards, and stale public counts. Resolve every actionable finding in a new
green corrective commit; do not rewrite already pushed history.

- [ ] **Step 2: Run full repository gates**

```bash
python3 -m pytest tests/ -q
npm --prefix website run build
python3 /Volumes/990EVO+/system/dotfiles/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  build-reinstall/skills/build-reinstall
git diff --check
```

Expected: the complete suite, production build, skill validator, and diff check
all pass.

- [ ] **Step 3: Prove both discovery and exact-selector installation**

Run:

```bash
npx --yes skills add . -l --full-depth
```

Expected: one discoverable `build-reinstall` selector. Then use a temporary Git
repository and the exact installation command from Task 2 for `--agent codex
--copy`; inspect the installed `SKILL.md`, `agents/openai.yaml`, and example
YAML. Repeat with `--agent claude-code --copy` and prove the command wrapper is
available through the plugin package source.

- [ ] **Step 4: Verify GitHub Pages and the live localized catalog**

```bash
gh run list --workflow pages.yml --limit 1
curl --fail --silent --show-error https://chann.github.io/skills/
curl --fail --silent --show-error https://chann.github.io/skills/en/
curl --fail --silent --show-error https://chann.github.io/skills/jp/
curl --fail --silent --show-error https://chann.github.io/skills/cn/
```

Wait for the run whose head SHA equals current `HEAD` to finish successfully.
In a browser, verify that searching `build reinstall` selects the new row, the
detail panel shows the correct Claude Code and Codex selectors, the copy control
works, all four locales contain the entry, browser console errors are zero,
horizontal overflow is zero at 320px and desktop width, and Axe reports zero
violations. Keep automated accessibility `incomplete` findings separate from
violations.

- [ ] **Step 5: Audit every user requirement and remote state**

Confirm with direct evidence:

1. explicit-only invocation;
2. build before reinstall;
3. installed-copy verification;
4. Claude Code and Codex selectors;
5. copyable example YAML;
6. multilingual website entry;
7. `AGENTS.md` add/modify/delete sync rule;
8. successful repository and live-site checks;
9. all requested commits pushed.

Finish with:

```bash
git log --oneline 351e50a..HEAD
git status --short --branch
git rev-list --left-right --count HEAD...@{u}
git ls-remote origin refs/heads/main
git rev-parse HEAD
```

Expected: clean worktree, `0 0`, and identical live-remote/local commit IDs.
