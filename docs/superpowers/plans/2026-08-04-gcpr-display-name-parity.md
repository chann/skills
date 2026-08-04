# GCPR Display-Name Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show the canonical `Git Commit and Push Realtime` title for `$gcpr` in Codex and make the alias-to-title relationship explicit on the website.

**Architecture:** Keep `gcpr` as a thin selector package. Change only its Codex `display_name`, pin that value to the canonical package and website title with one source-contract test, and render every website alias as a mapping to its existing canonical card title.

**Tech Stack:** Python 3.10+ `unittest`, YAML interface metadata, React 19, TypeScript 5.9, Vite 7, GitHub Pages

## Global Constraints

- `gcpr` remains an alias package; do not copy Git policy into it.
- The exact title is `Git Commit and Push Realtime`.
- `short_description` remains `Alias for verified realtime commit and push`.
- `default_prompt` continues to invoke `$gcpr` exactly.
- The website keeps one `git-commit-push-realtime` workflow card.
- The alias row renders `/gcpr, $gcpr → Git Commit and Push Realtime` without changing selectors or counts.
- Use explicit-path staging, ordinary pushes only, and prove `HEAD...@{u} = 0 0`.

---

### Task 1: Pin cross-surface title parity

**Files:**
- Modify: `tests/test_git_skill_package.py`
- Modify: `git-skill/skills/gcpr/agents/openai.yaml`
- Modify: `website/src/components/SkillExplorer.tsx`

**Interfaces:**
- Consumes: canonical `interface.display_name` from `git-skill/skills/git-commit-push-realtime/agents/openai.yaml` and canonical website title from `website/src/data/skills.ts`.
- Produces: `gcpr` interface metadata with the canonical display name and a generic website alias-to-title presentation.

- [ ] **Step 1: Write the failing metadata parity test**

Add `quoted_yaml_field()` and a focused contract to `tests/test_git_skill_package.py`:

```python
def quoted_yaml_field(path: Path, key: str) -> str:
    match = re.search(
        rf'^\s+{re.escape(key)}:\s+"([^"]+)"$',
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if match is None:
        raise AssertionError(f"{path.relative_to(ROOT)} is missing {key}")
    return match.group(1)


def test_codex_realtime_alias_uses_the_canonical_display_name(self) -> None:
    alias_interface = CODEX_REALTIME_ALIAS_SKILL / "agents" / "openai.yaml"
    canonical_interface = REALTIME_SKILL / "agents" / "openai.yaml"
    website_source = (ROOT / "website" / "src" / "data" / "skills.ts").read_text(
        encoding="utf-8"
    )
    title_match = re.search(
        rf'id: "{REALTIME_SKILL_NAME}",\s+title: "([^"]+)"',
        website_source,
    )

    self.assertIsNotNone(title_match)
    canonical_name = quoted_yaml_field(canonical_interface, "display_name")
    self.assertEqual(canonical_name, quoted_yaml_field(alias_interface, "display_name"))
    self.assertEqual(canonical_name, title_match.group(1) if title_match else "")
```

Add `import re` at the top of the test module.

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest tests/test_git_skill_package.py::GitSkillPackageTests::test_codex_realtime_alias_uses_the_canonical_display_name -q
```

Expected: FAIL because the alias value is `GCPR` while the canonical value is `Git Commit and Push Realtime`.

- [ ] **Step 3: Apply the minimal Codex metadata change**

Change only this field in `git-skill/skills/gcpr/agents/openai.yaml`:

```yaml
interface:
  display_name: "Git Commit and Push Realtime"
  short_description: "Alias for verified realtime commit and push"
  default_prompt: "Use $gcpr to commit and push each verified outcome while working."
```

- [ ] **Step 4: Make the website alias mapping explicit**

Replace the alias paragraph in `website/src/components/SkillExplorer.tsx` with:

```tsx
{selected.aliases?.length ? (
  <p className="skill-detail__alias">
    {content.aliases}: <code>{selected.aliases.join(", ")}</code>
    <span aria-hidden="true"> → </span>
    <span>{selected.title}</span>
  </p>
) : null}
```

The title comes from the existing canonical card; do not add alias-name data or a duplicate workflow definition.

- [ ] **Step 5: Verify GREEN and build the website**

Run:

```bash
/Users/channprj/.pyenv/shims/python3 -m pytest tests/test_git_skill_package.py -q
npm --prefix website run build
git diff --check
```

Expected: package tests pass, the production build exits 0, and `git diff --check` emits no output.

- [ ] **Step 6: Refresh the installed Codex alias**

Run:

```bash
npx --yes skills add . --skill gcpr --agent codex --global --yes --full-depth
cmp -s git-skill/skills/gcpr/SKILL.md /Users/channprj/.agents/skills/gcpr/SKILL.md
cmp -s git-skill/skills/gcpr/agents/openai.yaml /Users/channprj/.agents/skills/gcpr/agents/openai.yaml
```

Expected: installation succeeds and both `cmp` commands exit 0. Record that a new Codex session may be required to refresh cached picker metadata.

- [ ] **Step 7: Browser-check the local website**

Start the built preview, search for `gcpr`, and verify exactly one selected workflow card. Confirm its title is `Git Commit and Push Realtime` and its alias line exposes `/gcpr, $gcpr → Git Commit and Push Realtime` at desktop and 390px mobile widths.

- [ ] **Step 8: Commit and push the green outcome**

```bash
git add tests/test_git_skill_package.py \
  git-skill/skills/gcpr/agents/openai.yaml \
  website/src/components/SkillExplorer.tsx
git diff --cached --check
git commit -m "fix(git): show canonical name for gcpr"
git push
git rev-list --left-right --count HEAD...@{u}
```

Expected: commit succeeds, push succeeds, and parity is `0 0`.
