# Code Review UI and Writing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every HTML report in the `code-review` plugin use one shadcn-inspired design contract and make analytical skill prompts produce evidence-first prose without canned filler.

**Architecture:** Keep the three standalone templates and generators, but give each template the same semantic CSS tokens and control states so single-skill installations remain self-contained. Keep the main `code-review` skill authoritative for review prose, add a parallel evidence-first contract to `diff-summary`, and make thin wrappers and documentation defer to those contracts.

**Tech Stack:** Python 3.10+ standard library renderers, HTML/CSS/vanilla JavaScript, Markdown skill prompts, `pytest`, `unittest`, `quick_validate.py`, `npx skills`, local browser QA, Git.

---

## File Map

- Create `tests/test_html_report_style_contract.py`: shared token, state, responsive, print, and ornamental-copy contract.
- Modify `tests/diff_summary/test_summary_report.py`: generated-copy regression coverage.
- Modify the three tracked templates under `code-review/skills/{diff-summary,diff-viewer,code-review}/assets/`.
- Modify `code-review/skills/diff-summary/scripts/generate_summary_report.py`: remove the generated editorial-atlas overline.
- Modify `tests/test_code_review_skill_package.py` and `tests/test_diff_summary_skill_package.py`: evidence-first prompt contracts.
- Modify the four analytical skills and four command wrappers under `code-review/`.
- Modify `tests/test_installation_docs.py`, `code-review/README.md`, and `code-review/README.ko.md`.
- Sync the five verified tracked skills into repository-local and user-level `.agents/skills` mirrors.

## Shared CSS Contract

Use this exact light theme in all three templates:

```css
:root {
  color-scheme: light;
  --background: #ffffff;
  --foreground: #09090b;
  --card: #ffffff;
  --card-foreground: #09090b;
  --popover: #ffffff;
  --popover-foreground: #09090b;
  --muted: #f4f4f5;
  --muted-foreground: #71717a;
  --primary: #18181b;
  --primary-foreground: #fafafa;
  --secondary: #f4f4f5;
  --secondary-foreground: #18181b;
  --accent: #f4f4f5;
  --accent-foreground: #18181b;
  --destructive: #dc2626;
  --destructive-foreground: #fafafa;
  --border: #e4e4e7;
  --input: #e4e4e7;
  --ring: #18181b;
  --radius: 0.5rem;
  --font-sans: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
}
```

Use this exact dark override with each template's existing dark-theme selector:

```css
{
  color-scheme: dark;
  --background: #09090b;
  --foreground: #fafafa;
  --card: #09090b;
  --card-foreground: #fafafa;
  --popover: #18181b;
  --popover-foreground: #fafafa;
  --muted: #27272a;
  --muted-foreground: #a1a1aa;
  --primary: #fafafa;
  --primary-foreground: #18181b;
  --secondary: #27272a;
  --secondary-foreground: #fafafa;
  --accent: #27272a;
  --accent-foreground: #fafafa;
  --destructive: #7f1d1d;
  --destructive-foreground: #fafafa;
  --border: #27272a;
  --input: #27272a;
  --ring: #d4d4d8;
}
```

All templates must contain:

```css
:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}

button:disabled,
select:disabled,
textarea:disabled {
  pointer-events: none;
  opacity: 0.5;
}
```

Keep severity, diff addition/deletion, hunk, success, and syntax colors as report-specific variables.

### Task 1: Restyle `diff-summary` and remove atlas presentation

**Files:**
- Create: `tests/test_html_report_style_contract.py`
- Modify: `tests/diff_summary/test_summary_report.py:1221-1308`
- Modify: `code-review/skills/diff-summary/assets/summary-template.html`
- Modify: `code-review/skills/diff-summary/scripts/generate_summary_report.py:695-728`

- [ ] **Step 1: Write the failing style contract**

Create `tests/test_html_report_style_contract.py`:

```python
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_TEMPLATE = ROOT / "code-review/skills/diff-summary/assets/summary-template.html"
TOKENS = (
    "background", "foreground", "card", "card-foreground",
    "popover", "popover-foreground", "muted", "muted-foreground",
    "primary", "primary-foreground", "secondary", "secondary-foreground",
    "accent", "accent-foreground", "destructive", "destructive-foreground",
    "border", "input", "ring", "radius", "font-sans", "font-mono",
)
THEMED_TOKENS = TOKENS[:-3]


class HtmlReportStyleContractTests(unittest.TestCase):
    def assert_semantic_theme(self, name: str, source: str) -> None:
        declarations = set(re.findall(r"--([a-z][a-z0-9-]*):", source))
        self.assertTrue(set(TOKENS) <= declarations, name)
        for token in THEMED_TOKENS:
            with self.subTest(template=name, token=token):
                self.assertGreaterEqual(source.count(f"--{token}:"), 2)
        for token in (
            "background", "foreground", "card", "muted",
            "muted-foreground", "primary", "destructive",
            "border", "ring", "radius",
        ):
            with self.subTest(template=name, reference=token):
                self.assertIn(f"var(--{token})", source)

    def test_diff_summary_uses_shared_semantic_theme_without_legacy_palette(self) -> None:
        source = SUMMARY_TEMPLATE.read_text(encoding="utf-8")
        self.assert_semantic_theme("diff-summary", source)
        for token in (
            "paper", "paper-raised", "paper-muted", "ink", "ink-muted",
            "line", "line-strong", "cobalt", "cobalt-soft", "amber", "amber-soft",
        ):
            with self.subTest(legacy=token):
                self.assertNotIn(f"--{token}:", source)
        self.assertRegex(source, r":focus-visible[^\{]*\{[^}]*var\(--ring\)")
        self.assertIn(":disabled", source)


if __name__ == "__main__":
    unittest.main()
```

Add this method to `HtmlAssemblyTests`:

```python
    def test_generated_report_has_plain_product_copy_without_editorial_atlas_chrome(self) -> None:
        rendered = renderer.assemble_html(parse_report(REPORT), renderer.load_template())
        for phrase in (
            "Engineering change atlas",
            "Offline review plate",
            "Atlas index",
            "Portable review artifact",
            "Cobalt marks structure",
            "Amber marks impact",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, rendered)
```

- [ ] **Step 2: Run the tests and verify RED**

```bash
/opt/homebrew/bin/python3 -m pytest \
  tests/test_html_report_style_contract.py \
  tests/diff_summary/test_summary_report.py::HtmlAssemblyTests::test_generated_report_has_plain_product_copy_without_editorial_atlas_chrome \
  -q
```

Expected: FAIL because the shared tokens are absent and the six ornamental phrases remain.

- [ ] **Step 3: Replace the palette and component styling**

Insert the shared light/dark contract above. Replace every declaration and reference using this exact map:

| Remove | Replace with |
|---|---|
| `--paper` | `--background` |
| `--paper-raised` | `--card` |
| `--paper-muted` | `--muted` |
| `--ink` | `--foreground` |
| `--ink-muted` | `--muted-foreground` |
| `--line` | `--border` |
| `--line-strong` | `--input` |
| `--cobalt` | `--primary` |
| `--cobalt-soft` | `--accent` |
| `--amber` | `--ring` |
| `--amber-soft` | `--secondary` |
| `--negative` | `--destructive` |
| `--negative-soft` | `color-mix(in srgb, var(--destructive) 14%, var(--card))` |

Keep `--positive` and `--positive-soft`. Use `var(--font-sans)` for prose and `var(--font-mono)` for code. Use `var(--radius)` or `calc(var(--radius) - 2px)` on controls and ordinary cards, but keep flat left-accent summary cards.

Delete the grid backgrounds from `.atlas-rail`, the decorative `.atlas-canvas::before`, and poster-like tape/registration pseudo-elements. Replace the title rule with:

```css
.report-title {
  max-width: 52rem;
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-sans);
  font-size: clamp(1.75rem, 4vw, 2.75rem);
  font-weight: 700;
  letter-spacing: -0.035em;
  line-height: 1.08;
}
```

Add the shared focus and disabled states verbatim.

- [ ] **Step 4: Replace ornamental visible copy**

Use these exact labels while preserving data attributes and JavaScript hooks:

```html
<div class="rail-registration">Diff Summary</div>
<span class="rail-brand-kicker">Change report</span>
<div class="atlas-sidebar-label" data-atlas-index>Sections</div>
```

Delete the entire `.rail-legend` block. Replace the footer label with `<span>Generated report</span>`, change the aside label to `Report controls`, and change the English runtime string to `atlasIndex: "Sections"`. Keep the Korean `보고서 목차`.

In `generate_summary_report.py`, replace:

```python
'<div class="report-overline">Engineering change atlas</div>\n'
```

with:

```python
'<div class="report-overline">Diff Summary</div>\n'
```

- [ ] **Step 5: Run targeted tests and verify GREEN**

```bash
/opt/homebrew/bin/python3 -m pytest \
  tests/test_html_report_style_contract.py \
  tests/diff_summary/test_summary_report.py \
  tests/test_diff_summary_skill_package.py \
  -q
rg -ni 'Engineering change atlas|Offline review plate|Atlas index|Portable review artifact|Cobalt marks structure|Amber marks impact|--paper|--ink|--cobalt|--amber' \
  code-review/skills/diff-summary/assets/summary-template.html \
  code-review/skills/diff-summary/scripts/generate_summary_report.py
```

Expected: tests PASS and `rg` returns no output.

- [ ] **Step 6: Commit and push**

```bash
git add \
  tests/test_html_report_style_contract.py \
  tests/diff_summary/test_summary_report.py \
  code-review/skills/diff-summary/assets/summary-template.html \
  code-review/skills/diff-summary/scripts/generate_summary_report.py
git diff --cached --check
git commit -m "style(diff-summary): align report with shared UI"
git push
git status --short
```

Expected: commit succeeds, `origin/main` fast-forwards, and the tree is clean.

### Task 2: Apply the shared UI contract to `diff-viewer` and `code-review-html`

**Files:**
- Modify: `tests/test_html_report_style_contract.py`
- Modify: `code-review/skills/diff-viewer/assets/diff-template.html`
- Modify: `code-review/skills/code-review/assets/report-template.html`

- [ ] **Step 1: Expand the contract test to all templates**

Add:

```python
TEMPLATES = {
    "diff-summary": SUMMARY_TEMPLATE,
    "diff-viewer": ROOT / "code-review/skills/diff-viewer/assets/diff-template.html",
    "code-review-html": ROOT / "code-review/skills/code-review/assets/report-template.html",
}
LEGACY_TOKENS = {
    "diff-summary": (),
    "diff-viewer": ("bg", "surface", "surface-muted", "text"),
    "code-review-html": ("bg", "surface", "surface-muted", "text"),
}
```

Add these methods:

```python
    def test_every_html_report_uses_the_shared_semantic_theme(self) -> None:
        for name, path in TEMPLATES.items():
            with self.subTest(template=name):
                source = path.read_text(encoding="utf-8")
                self.assert_semantic_theme(name, source)
                for token in LEGACY_TOKENS[name]:
                    self.assertNotIn(f"--{token}:", source)

    def test_every_html_report_preserves_control_responsive_and_print_states(self) -> None:
        for name, path in TEMPLATES.items():
            with self.subTest(template=name):
                source = path.read_text(encoding="utf-8")
                self.assertRegex(source, r":focus-visible[^\{]*\{[^}]*var\(--ring\)")
                self.assertIn(":disabled", source)
                self.assertRegex(source, r"@media\s*\([^)]*max-width")
                self.assertIn("@media print", source)
```

- [ ] **Step 2: Run the expanded test and verify RED**

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_html_report_style_contract.py -q
```

Expected: FAIL for the two legacy token sets; `diff-viewer` also lacks print CSS.

- [ ] **Step 3: Replace legacy tokens and align controls**

Add the shared light/dark blocks to both templates. Apply:

| Role | Old | New |
|---|---|---|
| Page background | `--bg` | `--background` |
| Main surface | `--surface` | `--card` |
| Muted surface | `--surface-muted` | `--muted` |
| Main text | `--text` | `--foreground` |
| Old secondary-text references | old `--muted` | `--muted-foreground` |
| Old active-control references | old `--accent` | `--primary` |

Move secondary-text references before redefining `--muted` as a surface. Replace hard-coded white active-control text with `var(--primary-foreground)`. Preserve every severity, diff, hunk, code-scheme, and syntax variable.

Use:

```css
button,
select {
  min-height: 2rem;
  border: 1px solid var(--input);
  border-radius: calc(var(--radius) - 2px);
  background: var(--background);
  color: var(--foreground);
  font: inherit;
}

button:hover:not(:disabled),
select:hover:not(:disabled) {
  background: var(--accent);
  color: var(--accent-foreground);
}
```

Add the shared focus and disabled rules. Use `var(--radius)` for ordinary cards, editors, metrics, and comment items. Keep `details.finding` flat because it uses a left severity accent.

- [ ] **Step 4: Add the missing `diff-viewer` print behavior**

```css
@media print {
  aside,
  .sidebar-expand,
  .topbar .controls,
  .comment-thread,
  .line-comment-marker {
    display: none !important;
  }

  .layout {
    display: block;
  }

  main {
    padding: 0;
  }

  .file-diff {
    break-inside: avoid;
    border-color: #d4d4d8;
    box-shadow: none;
  }
}
```

Keep the existing `code-review-html` print contract, changing only legacy token references.

- [ ] **Step 5: Run renderer tests and verify GREEN**

```bash
/opt/homebrew/bin/python3 -m pytest \
  tests/test_html_report_style_contract.py \
  tests/diff_viewer/test_diff_report.py \
  tests/test_code_review_html_report.py \
  tests/test_code_review_skill_package.py \
  -q
```

Expected: PASS, including unified/split diff, comment scopes, bilingual review, and bottom finding actions.

- [ ] **Step 6: Commit and push**

```bash
git add \
  tests/test_html_report_style_contract.py \
  code-review/skills/diff-viewer/assets/diff-template.html \
  code-review/skills/code-review/assets/report-template.html
git diff --cached --check
git commit -m "style(code-review): unify HTML report components"
git push
git status --short
```

Expected: commit succeeds and `origin/main` fast-forwards.

### Task 3: Update bilingual docs and synchronize the UI phase

**Files:**
- Modify: `tests/test_installation_docs.py`
- Modify: `code-review/README.md`
- Modify: `code-review/README.ko.md`
- Runtime-only sync: five affected skill directories under both `.agents/skills/` roots

- [ ] **Step 1: Write the failing bilingual documentation test**

Add to the existing documentation test class:

```python
    def test_code_review_docs_describe_evidence_first_writing_and_conditional_sections(self) -> None:
        english = (ROOT / "code-review/README.md").read_text(encoding="utf-8")
        korean = (ROOT / "code-review/README.ko.md").read_text(encoding="utf-8")

        self.assertIn("Evidence-first writing", english)
        self.assertIn("Conditional sections", english)
        self.assertIn("observation → consequence → correction", english)
        self.assertIn("근거 우선 문체", korean)
        self.assertIn("조건부 섹션", korean)
        self.assertIn("관찰 → 영향 → 수정", korean)
        self.assertNotIn("Each report includes", english)
        self.assertNotIn("모든 리포트는 다음을 포함", korean)
```

- [ ] **Step 2: Run the test and verify RED**

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_installation_docs.py -q
```

Expected: only the new contract fails because the bilingual sections are absent.

- [ ] **Step 3: Replace mandatory-section docs**

Add to `README.md`:

```markdown
### Evidence-first writing

Review findings use **observation → consequence → correction**. Verified facts cite the changed path and line range; consequential inference is labeled and tied to evidence. The report does not add generic praise, a canned introduction, or findings solely to fill a template.

### Conditional sections

Metadata and actionable findings are always available. `Decision Summary`, `Positive Observations`, `Open Questions`, and `File Summary` appear only when they add distinct, decision-relevant information. Reports with no actionable findings say so directly and retain only material residual risks or verification gaps.
```

Change INFO to `Verified context that affects a decision; no code change required`.

Add to `README.ko.md`:

```markdown
### 근거 우선 문체

리뷰 발견 사항은 **관찰 → 영향 → 수정** 순서로 작성합니다. 확인된 사실에는 변경된 경로와 줄 범위를 붙이고, 중요한 추론은 추론임을 표시한 뒤 근거를 명시합니다. 형식만 채우기 위한 칭찬, 상투적인 도입부, 억지 발견 사항은 만들지 않습니다.

### 조건부 섹션

메타데이터와 실행 가능한 발견 사항은 항상 제공됩니다. `Decision Summary`, `Positive Observations`, `Open Questions`, `File Summary`는 서로 다른 의사결정 정보를 추가할 때만 표시합니다. 실행 가능한 발견 사항이 없으면 그 사실을 직접 밝히고, 중요한 잔여 위험이나 검증 공백만 남깁니다.
```

Change INFO to `의사결정에 영향을 주지만 코드 변경은 필요하지 않은 확인된 맥락`.

- [ ] **Step 4: Run docs/package tests and verify GREEN**

```bash
/opt/homebrew/bin/python3 -m pytest \
  tests/test_installation_docs.py \
  tests/test_code_review_skill_package.py \
  tests/test_diff_summary_skill_package.py \
  -q
```

Expected: PASS.

- [ ] **Step 5: Commit and push**

```bash
git add tests/test_installation_docs.py code-review/README.md code-review/README.ko.md
git diff --cached --check
git commit -m "docs(code-review): document evidence-first reports"
git push
git status --short
```

Expected: commit succeeds and `origin/main` fast-forwards.

- [ ] **Step 6: Sync both runtime mirrors safely**

Refuse symlink destinations:

```bash
for root in .agents/skills /Users/channprj/.agents/skills; do
  for skill in code-review code-review-md code-review-html diff-summary diff-viewer; do
    destination="$root/$skill"
    if [ -L "$destination" ]; then
      echo "refusing symlinked mirror: $destination" >&2
      exit 1
    fi
  done
done
```

Sync complete directories:

```bash
mkdir -p .agents/skills /Users/channprj/.agents/skills
for skill in code-review code-review-md code-review-html diff-summary diff-viewer; do
  mkdir -p ".agents/skills/$skill" "/Users/channprj/.agents/skills/$skill"
  rsync -a --delete "code-review/skills/$skill/" ".agents/skills/$skill/"
  rsync -a --delete "code-review/skills/$skill/" "/Users/channprj/.agents/skills/$skill/"
done
```

Verify byte identity:

```bash
for skill in code-review code-review-md code-review-html diff-summary diff-viewer; do
  diff -qr "code-review/skills/$skill" ".agents/skills/$skill"
  diff -qr "code-review/skills/$skill" "/Users/channprj/.agents/skills/$skill"
done
```

Expected: no output. Do not stage `.agents/`; it is ignored runtime state.

### Task 4: Render and inspect the unified HTML UI

**Files:**
- Generate only: `/tmp/code-review-ui/`
- No tracked changes expected unless verification exposes a defect

- [ ] **Step 1: Run targeted and full automated gates**

```bash
/opt/homebrew/bin/python3 -m pytest \
  tests/test_html_report_style_contract.py \
  tests/diff_summary/test_summary_report.py \
  tests/diff_viewer/test_diff_report.py \
  tests/test_code_review_html_report.py \
  tests/test_code_review_skill_package.py \
  tests/test_diff_summary_skill_package.py \
  tests/test_installation_docs.py \
  -q
/opt/homebrew/bin/python3 -m pytest -q
/opt/homebrew/bin/python3 -m unittest discover -s tests -v
```

Expected: every command exits 0.

- [ ] **Step 2: Validate skills, discovery, and whitespace**

```bash
for skill in code-review code-review-md code-review-html diff-summary diff-viewer; do
  /opt/homebrew/bin/python3 \
    /Users/channprj/.agents/skills/.system/skill-creator/scripts/quick_validate.py \
    "code-review/skills/$skill"
done
NO_COLOR=1 FORCE_COLOR=0 npx --yes skills add . -l --full-depth
git diff --check
```

Expected: five validation successes, all five skill names in discovery, and no whitespace error.

- [ ] **Step 3: Generate representative artifacts**

```bash
mkdir -p /tmp/code-review-ui/diff-summary
/opt/homebrew/bin/python3 -c 'import runpy, subprocess; report=runpy.run_path("tests/diff_summary/test_summary_report.py")["REPORT"]; subprocess.run(["/opt/homebrew/bin/python3", "-I", "code-review/skills/diff-summary/scripts/generate_summary_report.py", "--markdown-stdin", "--output-directory", "/tmp/code-review-ui/diff-summary", "--theme", "auto"], input=report, text=True, check=True)'
/opt/homebrew/bin/python3 code-review/skills/diff-viewer/scripts/generate_diff_report.py \
  --view split --theme auto --code-scheme github \
  -o /tmp/code-review-ui/diff-viewer.html
/opt/homebrew/bin/python3 code-review/skills/code-review/scripts/generate_html_report.py \
  .reviews/2026-06-17_16a2914.md \
  --alt .reviews/2026-06-17_16a2914.en.md \
  --theme auto --code-scheme github \
  -o /tmp/code-review-ui/code-review.html
```

Expected: three readable reports. Generate the viewer before the last UI commit while the tree has a representative multi-file diff. If the tree is clean, assemble `tests/diff_viewer/fixtures/multi-file.diff` through the renderer API; do not use a clean report as multi-file proof.

- [ ] **Step 4: Inspect the browser matrix with the `agent-browser` skill**

Open each generated `file://` report at `1440x1000` and `390x844`, in light and dark themes. Verify:

- No page-level horizontal overflow.
- Shared neutral page, sidebar, card, control, badge, table, and code styling.
- Visible keyboard focus ring.
- Desktop sidebar collapse/expand/resize and narrow one-column navigation.
- Theme/sidebar persistence after reload and readable print preview.
- Summary: card copy, comment add/edit/delete, feedback copy.
- Viewer: unified/split, word highlights, line-range comment, clear comments.
- Review: Korean/English toggle, finding copy/comments, feedback copy.

Expected: every interaction works. Screenshots alone do not prove interaction.

- [ ] **Step 5: Run the UI scope and remote audit**

```bash
test "$(git ls-files 'code-review/skills/**/assets/*template.html' | wc -l | tr -d ' ')" = "3"
rg -n -i 'Engineering change atlas|Offline review plate|Atlas index|Portable review artifact|Cobalt marks structure|Amber marks impact|--paper|--ink|--cobalt|--amber' \
  code-review/skills/diff-summary || true
git status --short --branch
git log -6 --oneline --decorate
git rev-parse HEAD
git rev-parse origin/main
```

Expected: exactly three templates; the UI banned search has no output; the tree is clean; `HEAD` equals `origin/main`; the log contains the design, UI, and docs commits.

- [ ] **Step 6: Fix only a defect proven by verification**

First add the narrowest failing assertion, run it RED, apply the smallest source fix, rerun the owning and full suites, then stage only exact paths. Example:

```bash
git add tests/test_html_report_style_contract.py code-review/skills/diff-viewer/assets/diff-template.html
git diff --cached --check
git commit -m "fix(diff-viewer): preserve narrow report layout"
git push
```

If no defect is found, create no extra commit.

### Task 5: Enforce evidence-first writing and complete the audit

**Files:**
- Modify: `tests/test_code_review_skill_package.py`
- Modify: `tests/test_diff_summary_skill_package.py`
- Modify: `code-review/skills/{code-review,code-review-md,code-review-html,diff-summary}/SKILL.md`
- Modify: `code-review/commands/{code-review,code-review-md,code-review-html,diff-summary}.md`

- [ ] **Step 1: Write failing review-writing tests**

Add to `CodeReviewSkillPackageTests`:

```python
    def test_main_review_prompt_is_evidence_first_without_mandatory_filler(self) -> None:
        text = (CODE_REVIEW / "skills/code-review/SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "observed behavior", "practical consequence",
            "smallest justified correction", "`Inference:`",
            "When there are no actionable findings",
            "Decision Summary", "Open Questions", "only when",
        ):
            with self.subTest(required=phrase):
                self.assertIn(phrase, text)
        for phrase in (
            "**Announce at start:**",
            "Always include the Positive Observations section",
            "Skip the Positive Observations section",
            "Default to INFO severity when uncertain",
            "top 1-3", "top 1–3",
            "[2-3 sentence summary", "overall quality",
        ):
            with self.subTest(forbidden=phrase):
                self.assertNotIn(phrase, text)

    def test_output_variants_inherit_the_authoritative_writing_contract(self) -> None:
        for name in ("code-review-md", "code-review-html"):
            with self.subTest(skill=name):
                text = (CODE_REVIEW / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("Evidence-first writing contract", text)
                self.assertIn("authoritative", text)
                self.assertIn("Do not restate or weaken", text)
                self.assertNotIn("**Announce at start:**", text)
                self.assertNotIn("top 1-3", text)
                self.assertNotIn("default to INFO", text)

    def test_analytical_commands_do_not_add_preambles_or_fixed_recaps(self) -> None:
        for name in (
            "code-review.md", "code-review-md.md",
            "code-review-html.md", "diff-summary.md",
        ):
            with self.subTest(command=name):
                text = (CODE_REVIEW / "commands" / name).read_text(encoding="utf-8")
                self.assertIn("evidence-first", text.lower())
                self.assertNotIn("Before starting", text)
                self.assertNotIn("briefly tell", text)
                self.assertNotIn("top 1", text.lower())
```

Add to `DiffSummarySkillPackageTests`:

```python
    def test_skill_enforces_evidence_first_proportionate_summary_prose(self) -> None:
        text = (DIFF_SUMMARY / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "observed change", "practical consequence", "**Evidence:**",
            "`Inference:`", "proportional to the evidence",
            "Do not repeat", "generic praise",
        ):
            with self.subTest(required=phrase):
                self.assertIn(phrase, text)
        for phrase in (
            "**Announce at start:**",
            "[Two or three evidence-based sentences",
            "key `DS-*` summaries",
        ):
            with self.subTest(forbidden=phrase):
                self.assertNotIn(phrase, text)
```

- [ ] **Step 2: Run tests and verify RED**

```bash
/opt/homebrew/bin/python3 -m pytest \
  tests/test_code_review_skill_package.py \
  tests/test_diff_summary_skill_package.py \
  -q
```

Expected: FAIL on missing evidence-first phrases and existing filler requirements.

- [ ] **Step 3: Replace the authoritative review contract**

Delete the announcement in `code-review/SKILL.md`. Replace the INFO/uncertainty and style rules with:

```markdown
| **INFO** | Verified context that materially affects a review decision but requires no code change | No action required |

Do not create an INFO finding solely to hold uncertainty or praise. If uncertainty changes severity or action, put one specific question and the missing evidence under **Open Questions**; otherwise omit it.

## Evidence-first writing contract

- Start with the finding or verified result. Do not add a skill announcement, generic review preface, congratulatory language, or a claim about overall code quality.
- For each actionable finding, write in this order: **observed behavior**, **practical consequence**, and **smallest justified correction**.
- Cite the changed path and line range before making the claim. Show only the smallest code excerpt needed to prove it; a correction may be prose when another code block would add noise.
- State verified facts directly. Prefix consequential inference with `Inference:` and name the evidence. If evidence is insufficient, ask one specific question under **Open Questions** or omit the claim.
- Keep prose proportional to the diff. Do not restate code, repeat a conclusion across sections, manufacture INFO items, or use generic praise such as "solid", "robust", "clean", or "well-structured".
- When there are no actionable findings, say so directly and list only material residual risks or verification gaps.
```

Replace the fixed report body with:

```markdown
# Code Review Report

**Date:** YYYY-MM-DD
**Reviewer:** automated review
**Scope:** [exact reviewed scope]
**Repository:** [repository name]
**Language:** en

## Findings

### HIGH

#### [CR-001] Concrete failure or risk
**File:** `path/to/file.py` (lines 42-58)
**Category:** Security | Correctness | Complexity | Maintainability | Best Practice

Observed behavior and the exact condition that triggers it.

Practical consequence for a caller, user, stored data, or operation.

**Suggested correction:** Smallest justified correction, with code only when code is clearer.
```

Follow it with:

```markdown
### Conditional sections

- **Decision Summary:** include only when a cross-cutting risk is not already clear from the first finding and metrics.
- **Positive Observations:** include only for a concrete pattern that materially lowers risk or review effort. Never add generic praise.
- **Open Questions:** include only when missing evidence changes severity or the required action.
- **File Summary:** include only when it helps navigate a multi-file review without repeating findings.

Omit every conditional section that would repeat another section or contain filler.
```

Replace Step 6 with:

```markdown
### 6. Report completion facts

In the conversation, report finding counts, overall risk, artifact paths when files were generated, fresh verification performed, and the browser-open result for HTML. Do not repeat report prose or a fixed number of findings. Mention one urgent finding inline only when the user needs it without opening the artifact.
```

Delete the mandatory-positive common mistake, red flag, and Always rule, plus the fixed top-findings handoff.

- [ ] **Step 4: Make wrappers and commands inherit the contract**

Delete wrapper announcements. Add to both:

```markdown
The main skill's **Evidence-first writing contract** and conditional-section rules are authoritative. Do not restate or weaken them here.
```

Change final handoffs to counts/risk, artifact paths, fresh verification, and HTML open status where applicable. Replace the pre-review advertisement in `commands/code-review.md` with:

```markdown
Follow the skill's evidence-first writing contract. Start with the first actionable finding or the verified no-findings result; do not add a command or skill preamble.
```

Add to the MD and HTML command wrappers:

```markdown
Follow the skill's evidence-first writing contract. In the conversation, report artifact paths, counts/risk, and fresh verification or browser-open facts without repeating report prose or a fixed number of findings.
```

- [ ] **Step 5: Add the parallel `diff-summary` contract**

Delete its announcement and add after `Verified And Unverified Claims`:

```markdown
## Evidence-first summary writing

- Start each material card with the **observed change**, then state the **practical consequence**, then cite the exact `**Evidence:**` that supports both.
- State verified facts directly. Prefix consequential inference with `Inference:` and identify the evidence that makes it plausible.
- Keep prose proportional to the evidence. Do not use generic praise, throat-clearing, code restatement, a fixed card count, or the same conclusion in the executive summary, cards, and handoff.
- Omit unsupported dimensions and decorative conclusions. A short or mechanical diff may need only one compact card.
- Do not repeat card prose in the conversation handoff. Mention a card only when it changes the immediate decision and the user may not open the artifact.
```

Replace the fixed sentence-count placeholder with:

```markdown
[Verified result and the most decision-relevant consequence, without repeating card prose.]
```

Remove the key-`DS-*` recap bullet. Add to `commands/diff-summary.md`:

```markdown
Follow the skill's evidence-first summary contract. Do not add a command preamble or repeat summary-card prose in the conversation handoff.
```

- [ ] **Step 6: Run tests and verify GREEN**

```bash
/opt/homebrew/bin/python3 -m pytest \
  tests/test_code_review_skill_package.py \
  tests/test_diff_summary_skill_package.py \
  -q
rg -n -i 'Announce at start|Always include the Positive Observations|Skip the Positive Observations|top 1-3|top 1–3|overall quality|\[2-3 sentence summary' \
  code-review/skills/code-review/SKILL.md \
  code-review/skills/code-review-md/SKILL.md \
  code-review/skills/code-review-html/SKILL.md \
  code-review/skills/diff-summary/SKILL.md \
  code-review/commands
```

Expected: tests PASS and `rg` returns no output.

- [ ] **Step 7: Commit and push**

```bash
git add \
  tests/test_code_review_skill_package.py \
  tests/test_diff_summary_skill_package.py \
  code-review/skills/code-review/SKILL.md \
  code-review/skills/code-review-md/SKILL.md \
  code-review/skills/code-review-html/SKILL.md \
  code-review/skills/diff-summary/SKILL.md \
  code-review/commands/code-review.md \
  code-review/commands/code-review-md.md \
  code-review/commands/code-review-html.md \
  code-review/commands/diff-summary.md
git diff --cached --check
git commit -m "fix(code-review): enforce evidence-first review writing"
git push
git status --short
```

Expected: commit succeeds and `origin/main` fast-forwards.

- [ ] **Step 8: Resync prompt changes into installed mirrors**

Repeat the symlink refusal and `rsync -a --delete` loop from Task 3 for `code-review`, `code-review-md`, `code-review-html`, `diff-summary`, and `diff-viewer`. Then rerun both `diff -qr` comparisons.

Expected: no comparison output; the installed prompts and templates are byte-identical to tracked sources.

- [ ] **Step 9: Run the final complete audit**

```bash
/opt/homebrew/bin/python3 -m pytest -q
/opt/homebrew/bin/python3 -m unittest discover -s tests -v
for skill in code-review code-review-md code-review-html diff-summary diff-viewer; do
  /opt/homebrew/bin/python3 \
    /Users/channprj/.agents/skills/.system/skill-creator/scripts/quick_validate.py \
    "code-review/skills/$skill"
done
NO_COLOR=1 FORCE_COLOR=0 npx --yes skills add . -l --full-depth
git diff --check
rg -n -i 'Announce at start|Always include the Positive Observations|Skip the Positive Observations|top 1-3|top 1–3|overall quality|\[2-3 sentence summary' \
  code-review/skills/code-review \
  code-review/skills/code-review-md \
  code-review/skills/code-review-html \
  code-review/skills/diff-summary \
  code-review/commands || true
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

Expected: both full test runners pass; five skills validate and appear in discovery; both mirror comparisons remain empty; the anti-slop search returns no output; the tree is clean; and `HEAD` equals `origin/main`.
