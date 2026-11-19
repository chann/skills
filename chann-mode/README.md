# chann-mode

[한국어](README.ko.md) · [← back to main](../README.md)

One entry point for any non-trivial task. Type `/chann-mode <task>` in Claude
Code or `$chann-mode <task>` in Codex. The skill restates your goal, names the
least change that satisfies it, matches the task to a playbook, hands each step
to the catalog skill that owns it, and ends with a reply that labels its
evidence. The other catalog workflows still work on their own; this is how
they get reached without remembering their names.

## What it decides for you

- **Size.** The smallest change that fully solves the task. Deletion before
  addition, reuse before new code, and every caller, test, and doc the change
  touches gets finished.
- **Delegation.** Work with two or more separable parts is split across
  delegates, each writer in its own worktree and branch with its own files.
  Their branches are merged and the project's checks run on the merged tree;
  a delegate's report alone is never the proof.
- **Autonomy.** Reversible work proceeds without asking. A force-push, a deploy
  outside the documented settings, deleting data, or contacting anyone beyond
  the session pauses. "자러 간다" or "don't stop" switches to an
  unattended run that asks nothing and logs every decision.
- **Evidence.** Verdicts are `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE`.
  Claims without direct evidence are labelled `measured`, `inferred`, or
  `guess`.
- **Reply.** In your language, leading with what changed for you, citing the
  principles that changed a decision, and closing with what was skipped and
  the risk that remains.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill chann-mode
```

Project-local:

```bash
npx skills add chann/skills --skill chann-mode
```

`chann-mode` works when installed alone: each playbook carries inline steps.
Install more of the catalog and each step routes to the skill that owns it.

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/chann-mode <task>` | `$chann-mode <task>` | Run the task through a playbook, routed skills, and an evidence-labelled reply |

Examples:

```text
/chann-mode 로그인하면 가끔 500 에러가 나, 원인 찾아서 고쳐줘
$chann-mode this endpoint got slow, find out why and fix it
/chann-mode 자러 간다, 이 마이그레이션 테스트 전부 통과할 때까지 해줘
```

It runs only on its selector. A request phrased without it goes straight to
the skill that owns that kind of work.

## Playbooks

| Playbook | For | You own |
|---|---|---|
| investigation | A question about code, history, or an outside API | The answer; nothing changes |
| bug-fix | Something broken, throwing, or flaky | The root cause and the proof it is gone |
| perf | Something measurably slower than it should be | Baseline, limiter, remedy, proof |
| feature | New or changed behavior | The design and what a user sees |
| refactoring | Structure changes, behavior is pinned | The contract |
| prototype | A fork an experiment can settle | One decision |
| plan | A multi-unit change whose plan is the deliverable | The plan, not the code |
| review | Judging or explaining a change | The findings and their proof |
| fan-out | Independent slices run in parallel | The done check and the merged result |
| autonomous-run | Unattended work | The exit condition |
| shipping | Commit, push, deploy, merge, cleanup | What lands and how far it reaches |
| pause-and-pickup | Stopping safely or resuming | The resume point |
| docs | One document | Every claim holding for the commit it ships in |
| authoring-a-skill | Writing or fixing a skill | Every sentence an agent reads |

## Routing

| Situation | Skill (when installed) | Playbook |
|---|---|---|
| How does this code work | `how` | investigation |
| Why was it built this way | `why` | investigation |
| An outside library, API, or spec question | `research-brief` | investigation |
| Something is broken, throwing, or flaky | `bug-hunt` | bug-fix |
| Something got measurably slower | `bug-hunt` | perf |
| New or changed behavior | none, inline | feature |
| Structure changes, behavior does not | none, inline | refactoring |
| A fork an experiment can settle | none, inline | prototype |
| Several competing attempts at one artifact | `arena` | prototype |
| A plan or design with open decisions | `review-me`, `plan-summary` | plan |
| Review a change for defects and reach | `interrogate`, `blast-radius` | review |
| Explain a change or a plan document | `diff-summary`, `plan-summary`, `diff-viewer` | review |
| Independent slices to run in parallel | `swarm` | fan-out |
| Multi-milestone or unattended work | `long-task` | autonomous-run |
| Commit, push, deploy, merge, conflicts, cleanup, reinstall | `git-commit`, `git-merge`, `git-resolve-conflicts`, `git-cleanup`, `build-reinstall` | shipping |
| Stopping, resuming, catching up | `handoff`, `recall`, `ketchup` | pause-and-pickup |
| Docs and prose | `gen-docs`, `unslop` | docs |
| Writing or fixing a skill, capturing lessons | `skill-forge`, `skill-audit`, `reflect` | authoring-a-skill |

## Package layout

```text
chann-mode/
├── .claude-plugin/plugin.json
├── commands/chann-mode.md
├── skills/chann-mode/
│   ├── SKILL.md                     # first move, routing, principles index, autonomy, delegation, evidence, reply
│   ├── worker.md                    # rules every delegate reads first
│   ├── playbooks/<name>.md          # fourteen playbooks
│   ├── references/principles.md     # twenty-five principles, each with a test
│   ├── references/decision-trail.md # the log format for long or unattended runs
│   ├── agents/openai.yaml
│   └── evals/evals.json
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills
- Git, for worktree isolation and the decision trail

## License

MIT
