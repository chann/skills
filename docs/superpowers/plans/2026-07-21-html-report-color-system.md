# HTML Report Color System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the shared zinc report palette with the approved Cool editorial light/dark system across code review, diff summary, and diff viewer HTML artifacts.

**Architecture:** Keep each skill independently installable by duplicating the exact core and semantic token declarations in its own HTML template. Enforce consistency through one style-contract test module, map report-specific severity/impact/diff tokens onto shared `--status-*` tokens, and keep the three diff-summary package templates byte-identical.

**Tech Stack:** Python 3.12+, unittest/pytest, self-contained HTML, CSS custom properties, stdlib report generators

---

## File Map

- Modify `tests/test_html_report_style_contract.py`: authoritative exact palette,
  semantic alias, contrast, print, and legacy-zinc contracts.
- Modify `code-review/skills/code-review/assets/report-template.html`: Cool
  editorial core palette, semantic status aliases, severity badges, code/diff
  colors, and print palette.
- Modify `code-review/skills/diff-viewer/assets/diff-template.html`: Cool
  editorial core palette, semantic diff aliases, code/diff colors, and print
  palette.
- Modify `code-review/skills/diff-summary/assets/summary-template.html`:
  canonical summary/quiz core palette, semantic aliases, auto-dark values, and
  print palette.
- Modify
  `code-review/skills/diff-summary-md/assets/summary-template.html`: byte copy
  of the canonical summary template.
- Modify
  `code-review/skills/diff-summary-quiz/assets/summary-template.html`: byte
  copy of the canonical summary template.
- Verify `tests/test_diff_summary_skill_package.py`: exact-selector runtime and
  byte-parity enforcement.
- Verify `tests/diff_summary/test_summary_report.py`: summary renderer,
  self-contained artifact, theme, quiz, print, and runtime behavior.
- Verify `tests/test_code_review_html_report.py`: code-review renderer and
  style behavior.
- Verify `tests/diff_viewer/test_diff_report.py`: diff-viewer renderer and
  interaction behavior.

### Task 1: Lock The Cool Editorial Core Palette In Tests

**Files:**
- Modify: `tests/test_html_report_style_contract.py:83-141`
- Modify: `tests/test_html_report_style_contract.py:262-310`
- Modify: `tests/test_html_report_style_contract.py:1193-1214`

- [ ] **Step 1: Replace the expected light and dark maps**

Use these exact constants:

```python
EXPECTED_LIGHT_THEME = {
    "background": "#f5f7fa",
    "foreground": "#1e293b",
    "card": "#ffffff",
    "card-foreground": "#1e293b",
    "popover": "#ffffff",
    "popover-foreground": "#1e293b",
    "muted": "#eef2f6",
    "muted-foreground": "#5f6b7a",
    "primary": "#2f5d8c",
    "primary-foreground": "#ffffff",
    "secondary": "#e8eef5",
    "secondary-foreground": "#26384d",
    "accent": "#e3edf7",
    "accent-foreground": "#244f7a",
    "destructive": "#b4233a",
    "destructive-foreground": "#ffffff",
    "border": "#d6dee8",
    "input": "#c8d3e0",
    "ring": "#3d6f9e",
}
EXPECTED_DARK_THEME = {
    "background": "#10151c",
    "foreground": "#e7edf5",
    "card": "#151c25",
    "card-foreground": "#e7edf5",
    "popover": "#1a222d",
    "popover-foreground": "#e7edf5",
    "muted": "#202a36",
    "muted-foreground": "#a8b3c2",
    "primary": "#8fb7de",
    "primary-foreground": "#102235",
    "secondary": "#202a36",
    "secondary-foreground": "#dce5ef",
    "accent": "#24364a",
    "accent-foreground": "#dcebfa",
    "destructive": "#8e2f3d",
    "destructive-foreground": "#ffd9de",
    "border": "#2d3948",
    "input": "#39485a",
    "ring": "#91b9e0",
}
EXPECTED_LIGHT_SHADOW = "0 1px 2px rgba(15, 34, 58, 0.08)"
EXPECTED_DARK_SHADOW = "none"
EXPECTED_PRINT_THEME = {
    **EXPECTED_LIGHT_THEME,
    "background": "#ffffff",
}
```

- [ ] **Step 2: Extend the shared theme test with surface and shadow contracts**

After each light/dark exact-map assertion, assert the shadow value. Add a
separate test:

```python
def test_cool_editorial_palette_separates_report_surfaces(self) -> None:
    for name, source in self.templates.items():
        light_selector, dark_selector = THEME_SELECTORS[name]
        light = custom_properties(css_rule(source, light_selector))
        dark = custom_properties(css_rule(source, dark_selector))

        with self.subTest(template=name, theme="light"):
            self.assertNotEqual(light["background"], light["card"])
            self.assertNotEqual(light["muted"], light["secondary"])
            self.assertNotEqual(light["secondary"], light["accent"])
            self.assertNotEqual(light["border"], light["input"])
            self.assertEqual(light["shadow"], EXPECTED_LIGHT_SHADOW)

        with self.subTest(template=name, theme="dark"):
            self.assertNotEqual(dark["background"], dark["card"])
            self.assertNotEqual(dark["card"], dark["popover"])
            self.assertNotEqual(dark["border"], dark["input"])
            self.assertEqual(dark["shadow"], EXPECTED_DARK_SHADOW)
```

- [ ] **Step 3: Generalize the print palette contract to all three reports**

Add selectors:

```python
PRINT_THEME_SELECTORS = {
    "diff-summary": (
        "body,\n"
        '      body[data-default-theme="dark"]:not([data-theme]),\n'
        '      body[data-theme="dark"],\n'
        '      body[data-default-theme="auto"]:not([data-theme])'
    ),
    "diff-viewer": ':root,\n      html[data-page-theme="dark"]',
    "code-review-html": ':root,\n      html[data-page-theme="dark"]',
}
```

Replace the summary-only print-map assertion with:

```python
def test_every_html_report_prints_with_cool_editorial_light_palette(
    self,
) -> None:
    for name, source in self.templates.items():
        printed = css_rule(source, "@media print")
        palette = css_rule(printed, PRINT_THEME_SELECTORS[name])
        declarations = custom_properties(palette)

        with self.subTest(template=name):
            self.assertEqual(
                selected_properties(declarations, THEME_COLOR_TOKENS),
                EXPECTED_PRINT_THEME,
            )
            self.assertEqual(declarations["shadow"], "none")
            self.assertRegex(palette, r"color-scheme:\s*light\s*;")
```

- [ ] **Step 4: Run the focused style contract and confirm the red state**

Run:

```bash
uv run --python 3.12 --with pytest \
  pytest -q tests/test_html_report_style_contract.py
```

Expected: failures show the existing `#ffffff/#09090b/#f4f4f5` zinc values,
missing print palette rules in code-review/diff-viewer, and missing surface
separation.

### Task 2: Apply Core Surface Tokens To All Canonical Templates

**Files:**
- Modify: `code-review/skills/code-review/assets/report-template.html:16-88`
- Modify: `code-review/skills/code-review/assets/report-template.html:785-796`
- Modify: `code-review/skills/diff-viewer/assets/diff-template.html:16-91`
- Modify: `code-review/skills/diff-viewer/assets/diff-template.html:748-770`
- Modify: `code-review/skills/diff-summary/assets/summary-template.html:26-120`
- Modify: `code-review/skills/diff-summary/assets/summary-template.html:1307-1341`
- Modify: `code-review/skills/diff-summary-md/assets/summary-template.html`
- Modify: `code-review/skills/diff-summary-quiz/assets/summary-template.html`

- [ ] **Step 1: Replace the shared light declaration block**

Keep each template's existing selector and report-specific declarations, but
replace the core declarations with:

```css
--background: #f5f7fa;
--foreground: #1e293b;
--card: #ffffff;
--card-foreground: #1e293b;
--popover: #ffffff;
--popover-foreground: #1e293b;
--muted: #eef2f6;
--muted-foreground: #5f6b7a;
--primary: #2f5d8c;
--primary-foreground: #ffffff;
--secondary: #e8eef5;
--secondary-foreground: #26384d;
--accent: #e3edf7;
--accent-foreground: #244f7a;
--destructive: #b4233a;
--destructive-foreground: #ffffff;
--border: #d6dee8;
--input: #c8d3e0;
--ring: #3d6f9e;
--shadow: 0 1px 2px rgba(15, 34, 58, 0.08);
```

- [ ] **Step 2: Replace the shared dark declaration block**

Use:

```css
--background: #10151c;
--foreground: #e7edf5;
--card: #151c25;
--card-foreground: #e7edf5;
--popover: #1a222d;
--popover-foreground: #e7edf5;
--muted: #202a36;
--muted-foreground: #a8b3c2;
--primary: #8fb7de;
--primary-foreground: #102235;
--secondary: #202a36;
--secondary-foreground: #dce5ef;
--accent: #24364a;
--accent-foreground: #dcebfa;
--destructive: #8e2f3d;
--destructive-foreground: #ffd9de;
--border: #2d3948;
--input: #39485a;
--ring: #91b9e0;
--shadow: none;
```

Apply the identical dark values to the diff-summary explicit-dark and
auto-dark blocks.

- [ ] **Step 3: Add a light print reset to code-review and diff-viewer**

At the start of each `@media print` block add:

```css
:root,
html[data-page-theme="dark"] {
  --background: #ffffff;
  --foreground: #1e293b;
  --card: #ffffff;
  --card-foreground: #1e293b;
  --popover: #ffffff;
  --popover-foreground: #1e293b;
  --muted: #eef2f6;
  --muted-foreground: #5f6b7a;
  --primary: #2f5d8c;
  --primary-foreground: #ffffff;
  --secondary: #e8eef5;
  --secondary-foreground: #26384d;
  --accent: #e3edf7;
  --accent-foreground: #244f7a;
  --destructive: #b4233a;
  --destructive-foreground: #ffffff;
  --border: #d6dee8;
  --input: #c8d3e0;
  --ring: #3d6f9e;
  --shadow: none;
  color-scheme: light;
}
```

Update the diff-summary print declaration with the same values. Its print
background remains `#ffffff`, not the screen `#f5f7fa`.

- [ ] **Step 4: Align the default light code canvas**

In code-review and diff-viewer set:

```css
--code-bg: #f8fafc;
--code-fg: #1e293b;
--code-muted: #728095;
--selection-bg: rgba(47, 93, 140, 0.18);
```

Do not change the Highlight.js scheme switcher or `data-code-tone` runtime.

- [ ] **Step 5: Synchronize the diff-summary exact-selector copies**

Run:

```bash
cp code-review/skills/diff-summary/assets/summary-template.html \
  code-review/skills/diff-summary-md/assets/summary-template.html
cp code-review/skills/diff-summary/assets/summary-template.html \
  code-review/skills/diff-summary-quiz/assets/summary-template.html
```

- [ ] **Step 6: Run the focused style contract**

Run:

```bash
uv run --python 3.12 --with pytest \
  pytest -q tests/test_html_report_style_contract.py
```

Expected: core palette, surface hierarchy, auto-dark, and print tests pass.
Existing report-specific status assertions may still use the old colors until
Task 4.

- [ ] **Step 7: Commit the core palette**

```bash
git add \
  tests/test_html_report_style_contract.py \
  code-review/skills/code-review/assets/report-template.html \
  code-review/skills/diff-viewer/assets/diff-template.html \
  code-review/skills/diff-summary/assets/summary-template.html \
  code-review/skills/diff-summary-md/assets/summary-template.html \
  code-review/skills/diff-summary-quiz/assets/summary-template.html
git commit -m "style: adopt cool editorial report palette"
```

### Task 3: Lock Shared Semantic Status Colors In Tests

**Files:**
- Modify: `tests/test_html_report_style_contract.py:83-155`
- Modify: `tests/test_html_report_style_contract.py:312-352`
- Modify: `tests/test_html_report_style_contract.py:690-756`
- Modify: `tests/test_html_report_style_contract.py:1219-1243`

- [ ] **Step 1: Add exact shared semantic maps**

```python
STATUS_TOKENS = (
    "status-success",
    "status-success-soft",
    "status-warning",
    "status-warning-soft",
    "status-danger",
    "status-danger-soft",
    "status-info",
    "status-info-soft",
)
EXPECTED_LIGHT_STATUS = {
    "status-success": "#24734d",
    "status-success-soft": "#ddf3e7",
    "status-warning": "#7a5900",
    "status-warning-soft": "#f7ebc6",
    "status-danger": "#b4233a",
    "status-danger-soft": "#fce4e7",
    "status-info": "#2f5d8c",
    "status-info-soft": "#e3edf7",
}
EXPECTED_DARK_STATUS = {
    "status-success": "#74c69d",
    "status-success-soft": "#183b2d",
    "status-warning": "#e9c46a",
    "status-warning-soft": "#3f3416",
    "status-danger": "#ff8a99",
    "status-danger-soft": "#4a2028",
    "status-info": "#9cc4ea",
    "status-info-soft": "#21364b",
}
```

- [ ] **Step 2: Add a recursive token resolver**

```python
def resolve_token(value: str, declarations: dict[str, str]) -> str:
    seen: set[str] = set()
    current = value
    while True:
        token_match = re.fullmatch(r"var\(--([\w-]+)\)", current)
        if token_match is None:
            return current
        token = token_match.group(1)
        if token in seen:
            raise AssertionError(f"cyclic CSS token alias: {token}")
        seen.add(token)
        current = declarations[token]
```

- [ ] **Step 3: Assert exact status maps and accessible soft surfaces**

```python
def test_every_html_report_uses_exact_shared_status_palette(self) -> None:
    for name, source in self.templates.items():
        light_selector, dark_selector = THEME_SELECTORS[name]
        for theme, selector, expected in (
            ("light", light_selector, EXPECTED_LIGHT_STATUS),
            ("dark", dark_selector, EXPECTED_DARK_STATUS),
        ):
            declarations = custom_properties(css_rule(source, selector))
            with self.subTest(template=name, theme=theme):
                self.assertEqual(
                    selected_properties(declarations, STATUS_TOKENS),
                    expected,
                )
                for base, soft in (
                    ("status-success", "status-success-soft"),
                    ("status-warning", "status-warning-soft"),
                    ("status-danger", "status-danger-soft"),
                    ("status-info", "status-info-soft"),
                ):
                    self.assertGreaterEqual(
                        contrast_ratio(
                            declarations[base],
                            declarations[soft],
                        ),
                        4.5,
                    )
```

- [ ] **Step 4: Assert each report uses semantic aliases**

```python
REPORT_STATUS_ALIASES = {
    "code-review-html": {
        "critical": "status-danger",
        "medium": "status-warning",
        "low": "status-info",
        "info": "muted-foreground",
    },
    "diff-summary": {
        "impact-high": "status-warning",
        "positive": "status-success",
        "positive-soft": "status-success-soft",
    },
    "diff-viewer": {
        "add-text": "status-success",
        "add-line": "status-success-soft",
        "del-text": "status-danger",
        "del-line": "status-danger-soft",
        "hunk-hue": "status-info",
    },
}

def test_report_specific_colors_alias_the_shared_status_palette(self) -> None:
    for name, aliases in REPORT_STATUS_ALIASES.items():
        source = self.templates[name]
        light_selector, dark_selector = THEME_SELECTORS[name]
        root_declarations = custom_properties(css_rule(source, ":root"))
        for theme, selector in (
            ("light", light_selector),
            ("dark", dark_selector),
        ):
            declarations = {
                **root_declarations,
                **custom_properties(css_rule(source, selector)),
            }
            for alias, target in aliases.items():
                with self.subTest(
                    template=name,
                    theme=theme,
                    alias=alias,
                ):
                    self.assertEqual(
                        declarations[alias],
                        f"var(--{target})",
                    )
                    self.assertEqual(
                        resolve_token(declarations[alias], declarations),
                        declarations[target],
                    )
```

- [ ] **Step 5: Add explicit code-review severity badge contracts**

Assert that each severity badge uses a soft semantic background and matching
text rather than white text on a light dark-theme status color:

```python
def test_code_review_severity_badges_use_accessible_soft_status_pairs(
    self,
) -> None:
    source = self.templates["code-review-html"]
    expected = {
        "critical": ("status-danger", "status-danger-soft"),
        "medium": ("status-warning", "status-warning-soft"),
        "low": ("status-info", "status-info-soft"),
        "info": ("muted-foreground", "muted"),
    }
    for severity, (foreground, background) in expected.items():
        rule = css_rule(source, f".badge-{severity}")
        self.assertRegex(rule, rf"color:\s*var\(--{foreground}\)\s*;")
        self.assertRegex(rule, rf"background:\s*var\(--{background}\)\s*;")
```

Keep high severity distinct by asserting `--high` and `--high-soft` equal
`#a84413/#f8e7dd` in light and `#f5a367/#472919` in dark.

- [ ] **Step 6: Run the style contract and confirm the semantic red state**

Run:

```bash
uv run --python 3.12 --with pytest \
  pytest -q tests/test_html_report_style_contract.py
```

Expected: failures report missing `--status-*` declarations, old
report-specific literal values, and solid severity badge backgrounds.

### Task 4: Implement Shared Semantic Status Aliases

**Files:**
- Modify: `code-review/skills/code-review/assets/report-template.html:37-57`
- Modify: `code-review/skills/code-review/assets/report-template.html:82-88`
- Modify: `code-review/skills/code-review/assets/report-template.html:423-448`
- Modify: `code-review/skills/diff-viewer/assets/diff-template.html:38-56`
- Modify: `code-review/skills/diff-viewer/assets/diff-template.html:83-88`
- Modify: `code-review/skills/diff-summary/assets/summary-template.html:46-49`
- Modify: `code-review/skills/diff-summary/assets/summary-template.html:82-85`
- Modify: `code-review/skills/diff-summary/assets/summary-template.html:115-118`
- Modify: `code-review/skills/diff-summary/assets/summary-template.html:1335-1338`
- Modify: `code-review/skills/diff-summary-md/assets/summary-template.html`
- Modify: `code-review/skills/diff-summary-quiz/assets/summary-template.html`

- [ ] **Step 1: Declare the shared status palette in every light block**

```css
--status-success: #24734d;
--status-success-soft: #ddf3e7;
--status-warning: #7a5900;
--status-warning-soft: #f7ebc6;
--status-danger: #b4233a;
--status-danger-soft: #fce4e7;
--status-info: #2f5d8c;
--status-info-soft: #e3edf7;
```

- [ ] **Step 2: Declare the shared status palette in every dark block**

```css
--status-success: #74c69d;
--status-success-soft: #183b2d;
--status-warning: #e9c46a;
--status-warning-soft: #3f3416;
--status-danger: #ff8a99;
--status-danger-soft: #4a2028;
--status-info: #9cc4ea;
--status-info-soft: #21364b;
```

Repeat the dark values in the diff-summary auto-dark block. Repeat the light
values in every report's print-light block so printing a dark on-screen theme
cannot retain dark status colors.

- [ ] **Step 3: Map code-review severity and diff tokens**

Use:

```css
--critical: var(--status-danger);
--high: #a84413;
--high-soft: #f8e7dd;
--medium: var(--status-warning);
--low: var(--status-info);
--info: var(--muted-foreground);
--add-hue: var(--status-success);
--del-hue: var(--status-danger);
--hunk-hue: var(--status-info);
--code-add-text: var(--status-success);
--code-del-text: var(--status-danger);
--code-hunk-text: var(--status-info);
```

In dark mode override only:

```css
--high: #f5a367;
--high-soft: #472919;
```

Replace the severity badge rules with:

```css
.badge-critical {
  color: var(--status-danger);
  background: var(--status-danger-soft);
}
.badge-high {
  color: var(--high);
  background: var(--high-soft);
}
.badge-medium {
  color: var(--status-warning);
  background: var(--status-warning-soft);
}
.badge-low {
  color: var(--status-info);
  background: var(--status-info-soft);
}
.badge-info {
  color: var(--muted-foreground);
  background: var(--muted);
}
```

Remove the global `.badge { color: #fff; }` declaration.

- [ ] **Step 4: Map diff-viewer diff tokens**

```css
--add-text: var(--status-success);
--add-line: var(--status-success-soft);
--del-text: var(--status-danger);
--del-line: var(--status-danger-soft);
--add-hue: var(--status-success);
--del-hue: var(--status-danger);
--hunk-hue: var(--status-info);
--code-add-text: var(--status-success);
--code-del-text: var(--status-danger);
--code-hunk-text: var(--status-info);
```

Keep the existing `data-code-tone="dark"` overrides because they belong to the
selected syntax scheme rather than the page-theme palette.

- [ ] **Step 5: Map diff-summary status tokens**

Use in light, dark, auto-dark, and print-light declarations:

```css
--impact-high: var(--status-warning);
--positive: var(--status-success);
--positive-soft: var(--status-success-soft);
--destructive-soft: var(--status-danger-soft);
```

- [ ] **Step 6: Synchronize summary package copies**

```bash
cp code-review/skills/diff-summary/assets/summary-template.html \
  code-review/skills/diff-summary-md/assets/summary-template.html
cp code-review/skills/diff-summary/assets/summary-template.html \
  code-review/skills/diff-summary-quiz/assets/summary-template.html
```

- [ ] **Step 7: Run style and renderer tests**

```bash
uv run --python 3.12 --with pytest pytest -q \
  tests/test_html_report_style_contract.py \
  tests/test_code_review_html_report.py \
  tests/diff_summary/test_summary_report.py \
  tests/diff_viewer/test_diff_report.py
```

Expected: all selected tests pass with no contrast, renderer, theme, print, or
interaction regression.

- [ ] **Step 8: Commit the shared semantic palette**

```bash
git add \
  tests/test_html_report_style_contract.py \
  code-review/skills/code-review/assets/report-template.html \
  code-review/skills/diff-viewer/assets/diff-template.html \
  code-review/skills/diff-summary/assets/summary-template.html \
  code-review/skills/diff-summary-md/assets/summary-template.html \
  code-review/skills/diff-summary-quiz/assets/summary-template.html
git commit -m "style: unify HTML report status colors"
```

### Task 5: Verify Package Parity And The Full Repository

**Files:**
- Verify: `tests/test_diff_summary_skill_package.py`
- Verify: `tests/test_code_review_skill_package.py`
- Verify: `tests/test_installation_docs.py`
- Verify: all `tests/**/*.py`

- [ ] **Step 1: Prove the three summary templates are byte-identical**

Run:

```bash
cmp \
  code-review/skills/diff-summary/assets/summary-template.html \
  code-review/skills/diff-summary-md/assets/summary-template.html
cmp \
  code-review/skills/diff-summary/assets/summary-template.html \
  code-review/skills/diff-summary-quiz/assets/summary-template.html
```

Expected: both commands exit `0` with no output.

- [ ] **Step 2: Run package and exact-selector tests**

```bash
uv run --python 3.12 --with pytest pytest -q \
  tests/test_diff_summary_skill_package.py \
  tests/test_code_review_skill_package.py
```

Expected: all tests pass, including standalone runtime byte parity and
exact-selector forward installation.

- [ ] **Step 3: Run the complete repository suite**

```bash
uv run --python 3.12 --with pytest pytest -q
```

Expected: the complete collected suite passes with zero failures.

- [ ] **Step 4: Check patch hygiene**

```bash
git diff --check
git status --short
```

Expected: no whitespace errors; status contains only intentional palette,
test, and plan/spec changes not yet committed.

### Task 6: Generate And Inspect Real HTML Artifacts

**Files:**
- Read: `.reviews/2026-06-17_16a2914.md`
- Read: `.diff-summaries/2026-07-20_head-1-month-ago-dot2-head-d6912c8c3adc.md`
- Generate: `/tmp/html-report-palette-qa/code-review.html`
- Generate: `/tmp/html-report-palette-qa/diff-summary.html`
- Generate: `/tmp/html-report-palette-qa/diff-summary-dark.html`
- Generate: `/tmp/html-report-palette-qa/diff-summary-quiz.html`
- Generate: `/tmp/html-report-palette-qa/diff-viewer.html`

- [ ] **Step 1: Generate representative reports**

```bash
mkdir -p /tmp/html-report-palette-qa
/opt/homebrew/bin/python3 -I \
  code-review/skills/code-review/scripts/generate_html_report.py \
  .reviews/2026-06-17_16a2914.md \
  -o /tmp/html-report-palette-qa/code-review.html \
  --theme light
/opt/homebrew/bin/python3 -I \
  code-review/skills/diff-summary/scripts/generate_summary_report.py \
  .diff-summaries/2026-07-20_head-1-month-ago-dot2-head-d6912c8c3adc.md \
  -o /tmp/html-report-palette-qa/diff-summary.html \
  --theme light
/opt/homebrew/bin/python3 -I \
  code-review/skills/diff-summary/scripts/generate_summary_report.py \
  .diff-summaries/2026-07-20_head-1-month-ago-dot2-head-d6912c8c3adc.md \
  -o /tmp/html-report-palette-qa/diff-summary-dark.html \
  --theme dark
uv run --python 3.12 --with pytest python -c '
from pathlib import Path
import runpy
namespace = runpy.run_path("tests/diff_summary/test_summary_report.py")
namespace["renderer"].generate_report_from_markdown(
    namespace["QUIZ_REPORT"],
    Path("/tmp/html-report-palette-qa/diff-summary-quiz.md"),
    Path("/tmp/html-report-palette-qa/diff-summary-quiz.html"),
    theme="light",
)
'
uv run --python 3.12 --with pytest python -c '
import importlib.util
import sys
from pathlib import Path
root = Path.cwd()
script = root / "code-review/skills/diff-viewer/scripts/generate_diff_report.py"
spec = importlib.util.spec_from_file_location("palette_diff_viewer", script)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
diff_text = (root / "tests/diff_viewer/fixtures/multi-file.diff").read_text()
files = module.parse_git_diff(diff_text)
output = Path("/tmp/html-report-palette-qa/diff-viewer.html")
module.write_report(
    module.assemble_html(
        files,
        root,
        "unified",
        "light",
        "github",
        output,
    ),
    output,
)
'
```

Expected: five HTML files are created and every generator exits `0`.

- [ ] **Step 2: Inspect light themes at desktop and 320px**

Open the three light reports in a real Chromium browser. At desktop and 320px
width verify:

- page `#f5f7fa` is visibly distinct from white cards;
- muted/sidebar, secondary, accent, input, and border surfaces are distinct;
- body and muted text remain readable;
- focus rings and selected controls use steel blue;
- severity, impact, add/delete, and hunk colors share the same semantic family;
- no horizontal overflow or layout change was introduced.

- [ ] **Step 3: Inspect dark themes and theme toggles**

Toggle each report to dark and verify:

- page, card, and popover surfaces remain visibly distinct;
- status colors remain legible and do not become neon decoration;
- code-scheme selection still controls syntax colors independently;
- summary quiz correct/incorrect states, review badges, and diff lines retain
  text or structural cues in addition to color.

- [ ] **Step 4: Inspect print output**

Use browser print preview for one artifact from each report type. Verify white
page background, Cool editorial text/border/status colors, no dark-mode
surface leakage, and no decorative shadow.

- [ ] **Step 5: Run the completion audit**

Map each acceptance criterion from
`docs/superpowers/specs/2026-07-21-html-report-color-system-design.md` to:

- exact token assertions in `tests/test_html_report_style_contract.py`;
- package parity output;
- full-suite output;
- generated desktop/mobile light/dark/print artifact observations.

Do not declare completion if any criterion lacks direct evidence.
