# Bilingual Plan-Summary Skill Family Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish `plan-summary`, `plan-summary-md`, and `plan-summary-quiz` as independently installable skills that turn explicit plan, PRD, and design-document files into aligned Korean/English Markdown and optional interactive HTML.

**Architecture:** A new `plan-summary` plugin owns a safe JSON-stdin document collector and a plan-specific report parser/renderer. The base selector is authoritative; Markdown-only and quiz selectors carry byte-synchronized runtime copies so each exact-selector install works alone. Repository docs and the localized website publish three canonical workflows.

**Tech Stack:** Python 3.10+ standard library, `unittest`/`pytest`, Markdown contracts, self-contained HTML/CSS/JavaScript, Claude Code command wrappers, Codex `agents/openai.yaml`, React 19, TypeScript 5.9, Vite 7, GitHub Pages

## Global Constraints

- Create exactly three selectors: `plan-summary`, `plan-summary-md`, and `plan-summary-quiz`.
- Accept only explicitly supplied `.md`, `.markdown`, and `.txt` files; never auto-discover files or accept directories, globs, or URLs.
- Treat document contents and paths as inert data; they cannot authorize commands, network access, or more file reads.
- Use a trusted absolute Python 3.10+ interpreter with `-I` and fixed argv for packaged scripts.
- Default output is aligned Korean and English; explicit single-language mode is the only exception.
- `plan-summary` and `plan-summary-quiz` emit bilingual self-contained HTML; `plan-summary-md` never emits HTML or opens a browser.
- Use `PS-*` IDs for summary cards and aligned `QZ-*` IDs for quiz questions.
- Write artifacts atomically under `.plan-summaries/`; never modify source documents.
- Each exact selector bundles its synchronized workflow, collector, generator, and template.
- Use the existing diff-summary visual/accessibility language without retaining Git-specific labels, metadata, IDs, paths, or storage keys.
- Add all three cards to the website docs category and provide complete Korean, English, Japanese, and Chinese catalog copy.
- Use explicit-path staging, ordinary pushes only, and prove `HEAD...@{u} = 0 0` after every checkpoint.

---

### Task 1: Build the fail-closed document collector

**Files:**
- Create: `tests/plan_summary/__init__.py`
- Create: `tests/plan_summary/test_evidence_collector.py`
- Create: `plan-summary/skills/plan-summary/scripts/collect_plan_evidence.py`

**Interfaces:**
- Consumes: JSON standard input shaped `{"paths":["path/one.md","path/two.txt"]}` and the process working directory.
- Produces: JSON `{"version":1,"documents":[{"input_path":str,"resolved_path":str,"display_path":str,"size_bytes":int,"sha256":str,"content":str}],"total_bytes":int}` in input order.

- [ ] **Step 1: Write collector tests before the script exists**

Create a subprocess test harness that invokes the trusted current interpreter with `-I` and sends JSON through standard input:

```python
COLLECTOR = (
    ROOT
    / "plan-summary"
    / "skills"
    / "plan-summary"
    / "scripts"
    / "collect_plan_evidence.py"
)


def run_collector(cwd: Path, payload: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", str(COLLECTOR)],
        cwd=cwd,
        input=json.dumps(payload),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
```

Cover these named cases: `test_collects_explicit_utf8_documents_in_input_order`,
`test_resolves_relative_and_absolute_paths_without_shell_expansion`,
`test_rejects_empty_or_malformed_requests`,
`test_rejects_duplicate_resolved_files`,
`test_rejects_missing_files_directories_and_final_symlinks`,
`test_rejects_unsupported_extensions_binary_and_invalid_utf8`,
`test_enforces_file_count_per_file_and_aggregate_byte_limits`, and
`test_returns_prompt_like_document_text_without_executing_it`.

The success assertion must verify exact SHA-256 values and source order. Failure assertions require non-zero exit, empty stdout, a concise stderr reason, and no artifacts.

- [ ] **Step 2: Run collector tests and verify RED**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest tests/plan_summary/test_evidence_collector.py -q
```

Expected: FAIL because `collect_plan_evidence.py` does not exist.

- [ ] **Step 3: Implement the bounded collector**

Use these constants in `collect_plan_evidence.py`:

```python
ALLOWED_SUFFIXES = frozenset({".md", ".markdown", ".txt"})
MAX_FILES = 16
MAX_FILE_BYTES = 1 * 1024 * 1024
MAX_TOTAL_BYTES = 4 * 1024 * 1024


class CollectionError(ValueError):
    pass
```

Define the exact signatures `parse_request(raw: bytes) -> list[str]`,
`collect_document(raw_path: str, cwd: Path) -> dict[str, object]`,
`collect_documents(paths: list[str], cwd: Path) -> dict[str, object]`, and
`main() -> int`.

Implementation rules:

```python
candidate = Path(raw_path)
lexical = candidate if candidate.is_absolute() else cwd / candidate
metadata = lexical.lstat()
if stat.S_ISLNK(metadata.st_mode):
    raise CollectionError("source must not be a symbolic link")
if not stat.S_ISREG(metadata.st_mode):
    raise CollectionError("source must be a regular file")
resolved = lexical.resolve(strict=True)
payload = resolved.read_bytes()
content = payload.decode("utf-8", errors="strict")
digest = hashlib.sha256(payload).hexdigest()
```

Reject NUL bytes as binary before UTF-8 decoding. Use the relative path from `cwd` as `display_path` when possible; otherwise use the absolute resolved path. Validate all inputs and aggregate limits before emitting one JSON object. On `CollectionError`, write one `plan-summary collector: <reason>` line to stderr and return 2 with empty stdout.

- [ ] **Step 4: Verify collector GREEN**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest tests/plan_summary/test_evidence_collector.py -q
git diff --check
```

Expected: every collector test passes and the diff check is silent.

- [ ] **Step 5: Commit and push the collector checkpoint**

```bash
git add tests/plan_summary/__init__.py \
  tests/plan_summary/test_evidence_collector.py \
  plan-summary/skills/plan-summary/scripts/collect_plan_evidence.py
git diff --cached --check
git commit -m "feat(plan-summary): collect explicit document evidence"
git push
git rev-list --left-right --count HEAD...@{u}
```

Expected: `0 0` after the push.

---

### Task 2: Parse and validate plan-summary Markdown

**Files:**
- Create: `tests/plan_summary/test_summary_report.py`
- Create: `plan-summary/skills/plan-summary/scripts/generate_plan_summary.py`

**Interfaces:**
- Consumes: complete Korean or English Markdown containing `Date`, `Sources`, `Source Digests`, `Language`, sequential `PS-*` cards, and an optional final `## Quiz`.
- Produces: `PlanSummaryReport` objects, aligned bilingual validation, Markdown files, and later HTML template context.

- [ ] **Step 1: Define canonical report fixtures and failing parser tests**

Create aligned `KO_REPORT`, `EN_REPORT`, `KO_QUIZ_REPORT`, and `EN_QUIZ_REPORT`
fixtures. Use two source paths/digests, two `PS-*` cards, and two `QZ-*`
questions. Add tests named `test_parses_metadata_cards_and_source_references`,
`test_rejects_missing_duplicate_or_malformed_metadata`,
`test_rejects_nonsequential_duplicate_or_malformed_ps_ids`,
`test_rejects_unknown_categories_and_empty_sources`,
`test_requires_summary_why_it_matters_and_source_basis_once`,
`test_ignores_card_like_text_inside_fenced_code`,
`test_bilingual_reports_require_matching_metadata_ids_categories_and_sources`,
`test_parses_quiz_questions_and_rejects_invalid_options_or_explanations`, and
`test_bilingual_quizzes_align_ids_option_counts_and_correct_indexes`.

The canonical card fixture is:

```markdown
#### [PS-001] 첫 출시 범위 확정

**Category:** Scope
**Sources:** `docs/plan.md#release-scope`

**Summary:** 첫 출시에는 문서 요약과 퀴즈가 포함됩니다.

**Why it matters:** 설치 가능한 결과물의 경계를 고정합니다.

**Source basis:** `Release scope` 절의 필수 기능 목록.
```

- [ ] **Step 2: Run parser tests and verify RED**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest tests/plan_summary/test_summary_report.py -q
```

Expected: import/file-not-found failure because the generator module does not exist.

- [ ] **Step 3: Implement the plan-specific report model and parser**

Define these public types and functions:

```python
@dataclass(frozen=True)
class SummaryCard:
    id: str
    title: str
    category: str
    sources: tuple[str, ...]
    summary: str
    why_it_matters: str
    source_basis: str
    markdown: str


@dataclass(frozen=True)
class QuizQuestion:
    id: str
    title: str
    options: tuple[str, ...]
    correct_index: int
    explanation: str
    markdown: str


@dataclass(frozen=True)
class PlanSummaryReport:
    date: str
    sources: tuple[str, ...]
    source_digests: tuple[str, ...]
    language: str
    executive_summary: str
    cards: tuple[SummaryCard, ...]
    quiz: tuple[QuizQuestion, ...]
    markdown: str
```

Define `parse_report(markdown: str) -> PlanSummaryReport` and
`validate_bilingual_alignment(primary: PlanSummaryReport, alternate:
PlanSummaryReport) -> None` with the model above.

Use exact parser-significant English keys. Normalize visible inline Markdown before testing empty or duplicate option text. Require ISO `YYYY-MM-DD`, one source digest per source, languages `ko`/`en`, at least one `PS-*` card, sequential IDs, supported categories, and `## Quiz` only as the final level-two section.

- [ ] **Step 4: Verify parser GREEN**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest tests/plan_summary/test_summary_report.py -q
```

Expected: parser and bilingual-alignment tests pass.

- [ ] **Step 5: Add collision-safe atomic Markdown generation tests**

Add tests named
`test_bilingual_directory_mode_writes_korean_and_english_markdown_atomically`,
`test_source_order_changes_the_collision_safe_output_stem`,
`test_rejects_symlinked_output_parent_and_existing_output_symlink`,
`test_markdown_only_writes_no_html`, and
`test_single_language_mode_requires_an_explicit_report`.

Define the stem as `<date>_<readable-source-stems>-<sha256-prefix>`, where the 12-character digest covers ordered `(source, digest)` pairs encoded as UTF-8 JSON.

- [ ] **Step 6: Implement output helpers and CLI input modes**

Add exact public helpers `source_tag(report: PlanSummaryReport) -> str`,
`validate_output_directory(path: Path) -> Path`,
`atomic_write_text(path: Path, content: str) -> None`, and
`generate_bilingual_report_in_directory(korean_markdown: str,
english_markdown: str, output_directory: Path, *, markdown_only: bool = False,
theme: str = "auto") -> tuple[Path, Path, Path | None]`.

CLI modes:

```text
--bilingual-json-stdin --output-directory PATH [--markdown-only] [--theme auto|light|dark]
--markdown-stdin --output-directory PATH [--markdown-only] [--theme auto|light|dark]
```

Read one JSON object `{"ko":"<complete Korean Markdown>","en":"<complete English Markdown>"}` for bilingual mode. Validate everything before writing. Use same-directory temporary regular files plus `os.replace` for atomic output.

- [ ] **Step 7: Verify parser and Markdown output GREEN**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest tests/plan_summary/test_summary_report.py -q
git diff --check
```

Expected: all report tests pass and the diff check is silent.

- [ ] **Step 8: Commit and push the report-contract checkpoint**

```bash
git add tests/plan_summary/test_summary_report.py \
  plan-summary/skills/plan-summary/scripts/generate_plan_summary.py
git diff --cached --check
git commit -m "feat(plan-summary): validate bilingual report contracts"
git push
git rev-list --left-right --count HEAD...@{u}
```

Expected: `0 0` after the push.

---

### Task 3: Render self-contained bilingual HTML and interactive quizzes

**Files:**
- Create: `plan-summary/skills/plan-summary/assets/summary-template.html`
- Modify: `plan-summary/skills/plan-summary/scripts/generate_plan_summary.py`
- Modify: `tests/plan_summary/test_summary_report.py`
- Modify: `tests/test_html_report_style_contract.py`

**Interfaces:**
- Consumes: one validated `PlanSummaryReport` plus an optional aligned translation.
- Produces: one self-contained HTML document with complete Korean/English view switching, accessible summary cards, optional interactive quizzes, theme support, and print answer-key behavior.

- [ ] **Step 1: Add failing HTML assembly and browser-runtime tests**

Test these outcomes before creating the template:
`test_renders_plan_cards_without_git_specific_labels`,
`test_bilingual_html_defaults_to_korean_and_switches_the_whole_page`,
`test_html_is_self_contained_and_escapes_document_content`,
`test_quiz_options_are_accessible_buttons_with_one_shot_answer_behavior`,
`test_print_styles_reveal_the_quiz_answer_key`,
`test_runtime_uses_plan_summary_storage_keys`, and
`test_template_matches_shared_report_color_and_focus_contracts`.

Assert absence of `Diff Summary`, `.diff-summaries`, `DS-`, `diff-summary:`, `Git`, `Scope`, `Command`, and `HEAD` in plan-specific UI chrome or runtime identifiers.

- [ ] **Step 2: Run focused HTML tests and verify RED**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest \
  tests/plan_summary/test_summary_report.py \
  tests/test_html_report_style_contract.py -q
```

Expected: FAIL because the plan template and HTML generation path are missing.

- [ ] **Step 3: Adapt the established summary template mechanically**

Start from `code-review/skills/diff-summary/assets/summary-template.html`, preserving semantic tokens, responsive layout, focus-visible rules, reduced-motion behavior, theme behavior, print layout, icons, language switching, and quiz controls. Apply these exact identity mappings before plan-specific cleanup:

| Diff identity | Plan identity |
|---|---|
| `Diff Summary` | `Plan Summary` |
| `diff-summary` | `plan-summary` |
| `DS-` | `PS-` |
| `.diff-summaries` | `.plan-summaries` |
| change/card labels | plan/summary labels |
| scope/command/HEAD facts | sources/source-digests facts |

Remove Git change metrics and file-change language. Render `Plan Map` and source references instead. Keep natural-language Korean and English UI strings aligned and keep code/path wrapping safe.

- [ ] **Step 4: Connect parsed reports to the template**

Add `build_template_context(primary: PlanSummaryReport, alternate:
PlanSummaryReport | None, *, theme: str) -> dict[str, str]` and
`render_html_report(primary: PlanSummaryReport, alternate: PlanSummaryReport |
None = None, *, theme: str = "auto") -> str`.

Embed user-derived JSON with `<`, `>`, `&`, U+2028, and U+2029 escaped. Use `data-plan-summary-runtime` and `plan-summary:*` local-storage keys. The active language determines every displayed prose field; source paths and IDs remain invariant.

- [ ] **Step 5: Verify HTML and quiz GREEN**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest \
  tests/plan_summary/test_summary_report.py \
  tests/test_html_report_style_contract.py -q
git diff --check
```

Expected: plan renderer tests and shared style/accessibility contracts pass.

- [ ] **Step 6: Commit and push the HTML checkpoint**

```bash
git add plan-summary/skills/plan-summary/assets/summary-template.html \
  plan-summary/skills/plan-summary/scripts/generate_plan_summary.py \
  tests/plan_summary/test_summary_report.py \
  tests/test_html_report_style_contract.py
git diff --cached --check
git commit -m "feat(plan-summary): render bilingual interactive reports"
git push
git rev-list --left-right --count HEAD...@{u}
```

Expected: `0 0` after the push.

---

### Task 4: Package three independently executable selectors

**Files:**
- Create: `tests/test_plan_summary_skill_package.py`
- Create: `plan-summary/.claude-plugin/plugin.json`
- Create: `plan-summary/commands/plan-summary.md`
- Create: `plan-summary/commands/plan-summary-md.md`
- Create: `plan-summary/commands/plan-summary-quiz.md`
- Create: `plan-summary/skills/plan-summary/SKILL.md`
- Create: `plan-summary/skills/plan-summary/agents/openai.yaml`
- Create: `plan-summary/skills/plan-summary-md/SKILL.md`
- Create: `plan-summary/skills/plan-summary-md/agents/openai.yaml`
- Create: `plan-summary/skills/plan-summary-md/references/plan-summary-workflow.md`
- Create: `plan-summary/skills/plan-summary-md/scripts/collect_plan_evidence.py`
- Create: `plan-summary/skills/plan-summary-md/scripts/generate_plan_summary.py`
- Create: `plan-summary/skills/plan-summary-md/assets/summary-template.html`
- Create: `plan-summary/skills/plan-summary-quiz/SKILL.md`
- Create: `plan-summary/skills/plan-summary-quiz/agents/openai.yaml`
- Create: `plan-summary/skills/plan-summary-quiz/references/plan-summary-workflow.md`
- Create: `plan-summary/skills/plan-summary-quiz/scripts/collect_plan_evidence.py`
- Create: `plan-summary/skills/plan-summary-quiz/scripts/generate_plan_summary.py`
- Create: `plan-summary/skills/plan-summary-quiz/assets/summary-template.html`

**Interfaces:**
- Consumes: authoritative base workflow and runtime from Tasks 1-3.
- Produces: three discoverable Claude Code/Codex selectors whose exact-selector installations remain executable.

- [ ] **Step 1: Write failing package and synchronization tests**

Pin:

```python
SKILL_NAMES = ("plan-summary", "plan-summary-md", "plan-summary-quiz")
SHARED_FILES = (
    Path("scripts/collect_plan_evidence.py"),
    Path("scripts/generate_plan_summary.py"),
    Path("assets/summary-template.html"),
)
```

Test all required files, plugin version `1.0.0`, exact command routing, `/name` and `$name` triggers, Codex interface fields, synchronized runtime bytes, Markdown-only behavior, quiz contract, `npx skills add plan-summary -l --full-depth`, and exact-selector installation into a temporary Codex target.

- [ ] **Step 2: Run package tests and verify RED**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest tests/test_plan_summary_skill_package.py -q
```

Expected: FAIL because plugin metadata, wrappers, skills, and variants do not exist.

- [ ] **Step 3: Write the authoritative base skill and command**

The base `SKILL.md` owns the exact collector invocation, untrusted-document boundary, analysis dimensions, report contract, bilingual generation, browser attempt, invalid-input behavior, and fact-only handoff. Its frontmatter includes Korean and English plan/PRD/design triggers plus `/plan-summary` and `$plan-summary`.

The command accepts `[source-path ...]`, routes internally without a user-visible preamble, preserves each explicit argument as path data, and completes only after two Markdown files, one HTML file, validation, and a browser-open attempt.

- [ ] **Step 4: Write the Markdown-only and quiz variants**

Each variant loads `references/plan-summary-workflow.md`, a body-only synchronized copy of the base skill. `plan-summary-md` adds `--markdown-only` and prohibits HTML/browser opening. `plan-summary-quiz` appends the aligned final `## Quiz` contract and reports the question count.

Use these Codex interfaces:

```yaml
# plan-summary
interface:
  display_name: "Plan Summary"
  short_description: "Summarize plans in aligned Korean and English"
  default_prompt: "Use $plan-summary to summarize the selected plan documents in Korean and English."

# plan-summary-md
interface:
  display_name: "Plan Summary Markdown"
  short_description: "Write bilingual plan summaries as Markdown only"
  default_prompt: "Use $plan-summary-md to summarize the selected plan documents as Korean and English Markdown."

# plan-summary-quiz
interface:
  display_name: "Plan Summary Quiz"
  short_description: "Summarize plans with a comprehension quiz"
  default_prompt: "Use $plan-summary-quiz to summarize the selected plan documents and add a bilingual quiz."
```

- [ ] **Step 5: Synchronize standalone runtime copies**

Copy the base workflow body to both variant references and copy all three shared runtime files byte-for-byte. Do not import from a sibling skill. Verify with `cmp -s` for every copy.

- [ ] **Step 6: Verify package GREEN and exact-selector installs**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest tests/test_plan_summary_skill_package.py -q
npx --yes skills add plan-summary -l --full-depth
git diff --check
```

Expected: tests pass and CLI output lists exactly the three new selectors for this plugin.

- [ ] **Step 7: Commit and push the packaging checkpoint**

Stage only the new plugin package and its focused package test, then:

```bash
git diff --cached --check
git commit -m "feat(plan-summary): package three summary selectors"
git push
git rev-list --left-right --count HEAD...@{u}
```

Expected: `0 0` after the push.

---

### Task 5: Publish bilingual docs and root architecture

**Files:**
- Create: `plan-summary/README.md`
- Create: `plan-summary/README.ko.md`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `USAGE.md`
- Modify: `ARCHITECTURE.md`
- Modify: `.gitignore`
- Modify: `tests/test_installation_docs.py`

**Interfaces:**
- Consumes: the three exact selectors and their output/runtime contracts.
- Produces: consistent English/Korean installation and usage documentation, eight-plugin architecture, 23 canonical workflows, 24 Codex selector packages, and ignored `.plan-summaries/` artifacts.

- [ ] **Step 1: Write failing documentation/count assertions**

Update the expected total skill count from 21 to 24 and assert all root/package docs expose `/plan-summary*`, `$plan-summary*`, `.plan-summaries/`, explicit-file-only input, aligned Korean/English output, Markdown-only behavior, and quiz behavior. Require `--skill <selector>` at least twice in each new package README.

- [ ] **Step 2: Run documentation tests and verify RED**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest tests/test_installation_docs.py -q
```

Expected: FAIL on missing docs, selector text, count, and artifact ignore rule.

- [ ] **Step 3: Write package and root documentation**

Document:

```text
23 canonical workflows · 24 installable Codex selectors · 8 plugins
```

Add selector tables, natural-language examples, separate exact-install commands, requirements (Python 3.10+, standard library only), artifact matrix, collector JSON boundary, report/quiz alignment, and no-auto-discovery behavior. Add `.plan-summaries/` to `.gitignore` without changing `.diff-summaries/`.

- [ ] **Step 4: Verify documentation GREEN**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest \
  tests/test_installation_docs.py \
  tests/test_plan_summary_skill_package.py -q
git diff --check
```

Expected: all documentation/package tests pass.

- [ ] **Step 5: Commit and push the documentation checkpoint**

```bash
git add plan-summary/README.md plan-summary/README.ko.md \
  README.md README.ko.md USAGE.md ARCHITECTURE.md .gitignore \
  tests/test_installation_docs.py
git diff --cached --check
git commit -m "docs(plan-summary): publish bilingual usage"
git push
git rev-list --left-right --count HEAD...@{u}
```

Expected: `0 0` after the push.

---

### Task 6: Add all three workflows to the localized website

**Files:**
- Modify: `website/src/data/skills.ts`
- Modify: `website/src/i18n/content/ko.json`
- Modify: `website/src/i18n/content/en.json`
- Modify: `website/src/i18n/content/jp.json`
- Modify: `website/src/i18n/content/cn.json`
- Modify: `website/scripts/verify-catalog.mjs`
- Modify: `website/scripts/verify-locales.mjs`

**Interfaces:**
- Consumes: three canonical selectors and the root count contract.
- Produces: docs-category catalog cards, locale-complete copy, search/discovery, and verifier output for 23 workflows/24 selector packages.

- [ ] **Step 1: Extend catalog verification first and verify RED**

Pin the expected card IDs and counts:

```text
plan-summary
plan-summary-md
plan-summary-quiz
Catalog matches 23 workflows and 24 packaged selectors.
```

Require each locale to contain the same 23 skill keys.

- [ ] **Step 2: Run the website verifiers and verify RED**

Run:

```bash
npm --prefix website run verify:catalog
npm --prefix website run verify:locales
```

Expected: FAIL because the definitions and locale records are missing.

- [ ] **Step 3: Add invariant catalog definitions**

Add these docs-category entries:

```typescript
{
  id: "plan-summary",
  title: "Plan Summary",
  category: "docs",
  example: "$plan-summary docs/plan.md docs/design.md",
  claudeSelector: "/plan-summary",
  codexSelector: "$plan-summary",
  tags: ["plan", "prd", "design", "spec", "summary", "bilingual"],
},
{
  id: "plan-summary-md",
  title: "Plan Summary Markdown",
  category: "docs",
  example: "$plan-summary-md docs/plan.md",
  claudeSelector: "/plan-summary-md",
  codexSelector: "$plan-summary-md",
  tags: ["plan", "prd", "design", "markdown", "summary", "bilingual"],
},
{
  id: "plan-summary-quiz",
  title: "Plan Summary Quiz",
  category: "docs",
  example: "$plan-summary-quiz docs/prd.md",
  claudeSelector: "/plan-summary-quiz",
  codexSelector: "$plan-summary-quiz",
  tags: ["plan", "prd", "design", "quiz", "summary", "bilingual"],
},
```

- [ ] **Step 4: Add complete four-locale copy**

For each ID, add `summary`, `whenToUse`, and `result` in Korean, English, Japanese, and Chinese. Preserve source contracts: selectors, paths, IDs, English titles, `PS-*`, and `QZ-*` remain untranslated.

- [ ] **Step 5: Verify website GREEN and build**

Run:

```bash
npm --prefix website run verify:catalog
npm --prefix website run verify:locales
npm --prefix website run typecheck
npm --prefix website run build
git diff --check
```

Expected: all checks exit 0 and the build emits localized pages.

- [ ] **Step 6: Browser-check local catalog behavior**

Search independently for `plan`, `prd`, `plan-summary-md`, and `plan-summary-quiz`. Verify all three titles/selectors, docs-category count, selector copy, four locale routes, dark/light themes, keyboard focus, reduced motion, 390px layout, and no horizontal overflow.

- [ ] **Step 7: Commit and push the website checkpoint**

```bash
git add website/src/data/skills.ts \
  website/src/i18n/content/ko.json \
  website/src/i18n/content/en.json \
  website/src/i18n/content/jp.json \
  website/src/i18n/content/cn.json \
  website/scripts/verify-catalog.mjs \
  website/scripts/verify-locales.mjs
git diff --cached --check
git commit -m "feat(site): publish plan-summary workflows"
git push
git rev-list --left-right --count HEAD...@{u}
```

Expected: `0 0` after the push.

---

### Task 7: Forward-use, full verification, installation, and deployment

**Files:**
- Modify if verification finds a defect: only the smallest affected source and its regression test
- Install outside repository: `/Users/channprj/.agents/skills/plan-summary/`
- Install outside repository: `/Users/channprj/.agents/skills/plan-summary-md/`
- Install outside repository: `/Users/channprj/.agents/skills/plan-summary-quiz/`

**Interfaces:**
- Consumes: every implemented package, test, document, and website surface.
- Produces: real bilingual artifacts from an approved fixture, globally installed Codex selectors, a green full suite/build, deployed Pages output, and final local/upstream/live parity evidence.

- [ ] **Step 1: Validate every new skill folder**

Run the system skill validator against all three folders and require zero errors:

```bash
/Users/channprj/.pyenv/shims/python3 \
  /Volumes/990EVO+/system/dotfiles/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plan-summary/skills/plan-summary
/Users/channprj/.pyenv/shims/python3 \
  /Volumes/990EVO+/system/dotfiles/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plan-summary/skills/plan-summary-md
/Users/channprj/.pyenv/shims/python3 \
  /Volumes/990EVO+/system/dotfiles/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plan-summary/skills/plan-summary-quiz
```

- [ ] **Step 2: Run exact-selector forward-use installs**

For each selector, initialize a temporary Git directory, install only that selector for Codex with `--copy --yes --full-depth`, and verify its `SKILL.md`, `agents/openai.yaml`, collector, generator, template, and variant reference where applicable. Execute the collector and generator against one bounded fixture plan.

Expected artifacts:

```text
plan-summary      -> ko.md + en.md + html
plan-summary-md   -> ko.md + en.md only
plan-summary-quiz -> ko.md + en.md + interactive quiz html
```

- [ ] **Step 3: Install all three selectors globally for Codex**

Run:

```bash
npx --yes skills add plan-summary \
  --skill plan-summary \
  --skill plan-summary-md \
  --skill plan-summary-quiz \
  --agent codex --global --yes --full-depth
```

Compare every installed file byte-for-byte with its repository source. Record that a fresh Codex session may be required for cached skill discovery.

- [ ] **Step 4: Run the complete repository and website gates**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest tests -q --tb=short
npm --prefix website run build
git diff --check
git status --short
```

Expected: zero test failures, a successful production build, no diff-check output, and no unexpected files.

- [ ] **Step 5: Verify GitHub Pages deployment and live behavior**

Wait for the Pages workflow associated with the final website commit. Require a successful workflow conclusion, `curl --fail --silent --show-error https://chann.github.io/skills/`, and live browser checks for:

```text
gcpr -> one canonical Git Commit and Push Realtime card with explicit alias mapping
plan-summary -> visible and searchable
plan-summary-md -> visible and searchable
plan-summary-quiz -> visible and searchable
```

Repeat desktop and 390px checks on the live site.

- [ ] **Step 6: Commit any verification fix as a new green checkpoint**

If a defect appears, add a failing regression test, verify RED, apply the smallest fix, rerun the affected and full gates, stage explicit paths, commit with the appropriate Conventional Commit type, push, and reverify Pages. Do not rewrite an already pushed checkpoint.

- [ ] **Step 7: Prove final completion and parity**

Run:

```bash
git status --short --branch
git log --oneline 1f0f320..HEAD
git rev-list --left-right --count HEAD...@{u}
git ls-remote origin refs/heads/main
git rev-parse HEAD
```

Expected: clean worktree, every planned checkpoint listed, local/upstream parity `0 0`, and live remote `main` equal to local `HEAD`.
