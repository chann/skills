import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "code-review" / "skills" / "code-review" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from generate_html_report import parse_markdown  # noqa: E402


def test_finding_actions_render_after_finding_content_with_full_markdown_label() -> None:
    markdown = """# Code Review Report

**Language:** en

## Findings

### HIGH

#### [CR-001] Fix cache invalidation
**File:** `src/cache.py` (lines 1-3)

The cache can return stale data.

**Suggested fix:**
```python
invalidate_cache()
```

---
"""

    html, _meta, _sidebar = parse_markdown(markdown)

    content_index = html.index("The cache can return stale data.")
    code_index = html.index("invalidate_cache()")
    toolbar_index = html.index('class="finding-toolbar"')
    close_index = html.index("</div></details>")

    assert content_index < code_index < toolbar_index < close_index
    assert '<span data-i18n="copyMd">Copy Markdown</span>' in html
    assert "Copy MD" not in html
