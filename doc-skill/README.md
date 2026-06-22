# doc-skill

[한국어](README.ko.md) · [← back to main](../README.md)

Generate or update a clean four-file documentation set for any software project: `README.md`, `README.ko.md`, `ARCHITECTURE.md`, and `USAGE.md`.

## Highlights

- Keeps `README.md` as a concise front door instead of mixing overview, usage, and architecture in one file
- Keeps `README.ko.md` in sync as a faithful Korean mirror of the English README
- Moves detailed commands, options, configuration, examples, and troubleshooting to `USAGE.md`
- Moves components, data flow, directory structure, and design decisions to `ARCHITECTURE.md`
- Preserves hand-written sections with heading-aware update-in-place rules and `<!-- doc-skill:keep -->`
- Requires per-file diffs and confirmation before writing

## Installation

**Recommended (global, one shot):**

```bash
npx skills add -y -g chann/skills@doc-skill
```

**Project-local:**

```bash
npx skills add chann/skills@doc-skill
```

**Manual:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/doc-skill/skills/gen-docs" ~/.claude/skills/gen-docs
```

## Quick start

From a project root:

```text
> /gen-docs
```

For another project:

```text
> /gen-docs ../my-project
```

The skill analyzes the project, renders candidate docs, shows the diffs, and writes only after confirmation.

## More documentation

- [Usage](USAGE.md) - invocation forms, workflow, update rules, and safety notes
- [Architecture](ARCHITECTURE.md) - plugin structure, skill boundaries, and design decisions

## License

MIT
