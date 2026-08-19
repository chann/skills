---
name: skill-audit
description: Use when packaged skills must be checked against the repository's skill contract before a merge or release, including "스킬 규칙 검사해줘", "스킬 패키지 점검", "스킬 카탈로그 동기화 확인", "audit my skills", "check every skill against the contract", "which skills are missing evals", "/skill-audit", or "$skill-audit". Reports every violation with its rule, file, and fix, and exits non-zero so it works as a gate. Read-only by default; use skill-forge to author or repair a package.
---

# Skill Audit

Run the repository's skill contract over every packaged skill and report what
fails. The audit is read-only: it changes nothing unless the user asks for
repairs after seeing the report.

The contract is stated in
[`../skill-forge/references/skill-package-contract.md`](../skill-forge/references/skill-package-contract.md).
[`scripts/audit_skills.py`](scripts/audit_skills.py) is its executable form.

## 1. Run it

From the repository root:

```bash
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --root .
```

Useful variants:

| Command | Use |
|---|---|
| `--skill <name>` | One skill, before committing a change to it |
| `--format markdown` | A report to paste into a PR or an issue |
| `--format json` | Feeding another check |
| `--root <path>` | Another skills repository |

The script walks `<root>/*/skills/*/SKILL.md`, applies rules C1 through C9, and
exits `1` when anything fails. Locale, count, and plugin-manifest rules run only
on a whole-repository audit; `--skill` scopes to that package's own rules.

If the script is missing from the install, say so and stop. Do not reimplement
the rules by hand — a hand-run audit and a scripted one disagreeing is worse
than no audit.

## 2. Read the report

Each line is `<rule> <skill> <detail> (<file>)`. Group the violations before
reporting them, because they cluster by cause:

| Pattern | Usual cause |
|---|---|
| Many `C6` on one plugin | The plugin predates the evals rule |
| `C2` with `C3` on one skill | The opening clause and the invocation flag drifted apart |
| `C7` right after a rename | The catalog kept the old id |
| `C9` alone | A skill was added or removed without updating the published counts |

Report the count, the grouped causes, and the exact files. Do not paraphrase a
violation into a suggestion — the detail line already names the fix.

## 3. Repair, only when asked

The audit ends at the report. When the user asks for the fixes:

- Fix the package, never the rule. A rule that keeps failing is a signal about
  the package, and changing it silently removes the guarantee every other skill
  is holding up.
- Apply one rule at a time across all offending skills, then re-run. Mixed
  repairs make it unclear which change cleared which violation.
- For anything that touches the catalog, locales, counts, or a new package, use
  `skill-forge` — it owns the publishing steps this audit only checks.
- Re-run the audit and the test suite before reporting the repair as done:

```bash
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --root .
python3 -m pytest tests -q
```

## Refusals

- Do not edit files during an audit the user asked for as a check.
- Do not report "no violations" from a partial run. Say which scope ran.
- Do not lower `MIN_EVALS`, `MAX_DESCRIPTION`, or any other threshold in the
  script to make a repository pass.
- Do not treat a skipped rule as a passed rule. A `--skill` run does not clear
  C7 locales, C8, or C9.

## Integration

**Pairs with:** `skill-forge` for authoring and repair, and `code-review` when
the audit surfaces a package whose workflow itself looks wrong.

**Use instead of:** reading `SKILL.md` files one by one to check consistency.
