---
name: plan-summary-md
description: Use when the user wants an explicit plan, PRD, requirements, specification, or design document summarized into Korean and English Markdown files only, including "plan 요약을 마크다운으로", "PRD 요약 파일", "설계문서 마크다운 요약", "markdown-only plan summary", "summarize this PRD as Markdown", "/plan-summary-md", or "$plan-summary-md". For bilingual HTML use plan-summary; for a quiz use plan-summary-quiz.
---

# Plan Summary Markdown

## Workflow

Before starting, read the bundled base workflow at `<skill-path>/references/plan-summary-workflow.md`. It is the authoritative `plan-summary` body. Follow its explicit-file collector, untrusted-document boundary, evidence analysis, bilingual alignment, report contract, failure handling, and factual handoff without weakening them.

This variant writes aligned Korean and English Markdown only. It never generates HTML and never attempts a browser open.

After authoring the aligned pair, invoke the bundled generator with fixed argv and standard input:

```text
/absolute/trusted/python3 -I <skill-path>/scripts/generate_plan_summary.py \
  --bilingual-json-stdin \
  --output-directory ".plan-summaries" \
  --markdown-only
```

Require a zero exit and verify both returned Markdown files. Do not create an HTML file through another mechanism. Use `--markdown-stdin --markdown-only` only when the user explicitly requests one language.

This exact selector includes synchronized copies of the reference, collector, generator, and template so standalone installation remains executable.
