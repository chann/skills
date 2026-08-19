# Repository instructions

## Follow one skill contract

Every packaged skill obeys the same nine rules — name parity, description
grammar, invocation-mode declaration, Codex descriptor, slash command, evals,
catalog and locale parity, plugin manifest, and published counts. The rules are
stated once, in
[`skill-forge/skills/skill-forge/references/skill-package-contract.md`](skill-forge/skills/skill-forge/references/skill-package-contract.md).

Two of them are easy to get wrong and worth restating here:

- A description opens with `Use when` or `Use only when`, names real triggers,
  and carries both the `/<name>` and `$<name>` selectors.
- `Use only when` and `disable-model-invocation: true` imply each other. Use
  that pair only for selector aliases and workflows that must never start on
  their own.

Run the audit before finishing any skill change:

```bash
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --root .
```

A failing rule is a missing file or a mismatched string. Fix the package, never
the rule — `tests/test_skill_contract.py` and every other skill depend on the
guarantee holding. Use `skill-forge` when adding or repairing a package; it owns
the publishing steps the audit only checks.

## Keep skills and the website in sync

Whenever you `add`, `modify`, or `delete` an installable skill, command, or
selector, update every public website surface in the same change. Do not leave
the package and catalog out of sync.

- Update canonical IDs, selectors, examples, aliases, categories, and tags in
  `website/src/data/skills.ts`.
- Update the matching `summary`, `whenToUse`, and `result` entries in all four
  locale files: `website/src/i18n/content/ko.json`,
  `website/src/i18n/content/en.json`, `website/src/i18n/content/jp.json`, and
  `website/src/i18n/content/cn.json`.
- When a skill's name, purpose, selector, alias, example, category, or
  user-visible behavior changes, review the matching metadata and localized
  copy even when its ID stays the same.
- When deleting a skill, remove its canonical catalog entry and every locale
  entry; do not leave a hidden or stale website route to the removed workflow.
- Keep public workflow and selector counts current in root documentation,
  `website/README.md`, and website verification scripts.
- If the public workflow count changes, update
  `website/scripts/generate-social-cards.mjs`, regenerate all four committed
  social-card PNGs, and inspect the rendered images.
- Preserve the skill's actual behavior across locales. Translate presentation
  copy, but do not invent different capabilities or invocation rules.

Before finishing, run at least:

```bash
npm --prefix website run verify:catalog
npm --prefix website run verify:locales
npm --prefix website run build
```

Also run the focused package tests for the changed skill. A skill change is not
complete while its package, catalog, localized copy, generated assets, docs,
or verification counts disagree.

`build-reinstall` is explicit-only. Do not turn it into an automatic
post-completion hook when editing its package or website copy.
