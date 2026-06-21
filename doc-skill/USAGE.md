# doc-skill Usage

## Installation

Install the plugin globally:

```bash
npx skills add -y -g chann/skills@doc-skill
```

Install into the current project:

```bash
npx skills add chann/skills@doc-skill
```

Manual installation for agents that load raw skill folders:

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/doc-skill/skills/gendoc" ~/.claude/skills/gendoc
```

## Quick start

Generate or update docs for the current project:

```text
> /gen-docs
```

Generate or update docs for a different project:

```text
> /gen-docs ../my-project
```

## Command reference

| Command | Effect |
|---|---|
| `/gen-docs` | Use the current working directory as the target project root |
| `/gen-docs <project-root>` | Use `<project-root>` as the target project root |

The command always targets this documentation set:

- `README.md`
- `README.ko.md`
- `ARCHITECTURE.md`
- `USAGE.md`

## Workflow

1. Resolve the target root.
2. Detect existing and missing docs.
3. Confirm the target set.
4. Analyze project manifests, tree shape, existing docs, license, CI, and remote metadata.
5. Use parallel Explore subagents for large projects; stay inline for small projects.
6. Build a project model.
7. Render candidates from templates.
8. Merge existing docs by heading.
9. Show per-file diffs.
10. Write only confirmed files.

## Update-in-place rules

- Replace derivable sections such as install, quick start, command reference, configuration, directory structure, version, and badges.
- Preserve unknown custom prose verbatim.
- Preserve sections containing `<!-- doc-skill:keep -->`.
- Insert missing canonical sections in template order.
- Never delete a target doc.
- Never modify files outside the four target docs.

## Examples

Create the full doc set for a small CLI:

```text
> /gen-docs ~/src/my-cli
```

Refresh only after reviewing diffs:

```text
> Update this repo's docs with gendoc, but preserve custom roadmap prose.
```

Freeze a section:

```markdown
## Product Philosophy
<!-- doc-skill:keep -->

This section stays exactly as written.
```

## Troubleshooting

| Symptom | Action |
|---|---|
| README becomes too long | Move detailed reference content into `USAGE.md` or `ARCHITECTURE.md` |
| A custom section should never change | Add `<!-- doc-skill:keep -->` inside that section |
| The agent guesses unsupported commands | Ask it to cite the manifest, tests, or existing docs that prove each command |
| The diff includes unrelated files | Stop and restrict the write set to the four target docs |
| Korean README translates flags or commands | Keep commands, flags, paths, and proper nouns verbatim |
