# chann-mode

[한국어](README.ko.md) · [← back to main](../README.md)

One entry point for any non-trivial task. Type `/chann <task>` in Claude
Code or `$chann <task>` in Codex. The skill restates your goal, names the
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
npx skills add -y -g chann/skills --skill chann
```

Project-local:

```bash
npx skills add chann/skills --skill chann
```

`chann` installs all 30 playbooks with the skill. Claude Code and Codex
use the same playbook files. Steps can use installed skills, read their
listed files when a loader is unavailable, or run directly from the playbook.

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/chann <task>` | `$chann <task>` | Run the task through a playbook, routed skills, and an evidence-labelled reply |

Examples:

```text
/chann 로그인하면 가끔 500 에러가 나, 원인 찾아서 고쳐줘
$chann this endpoint got slow, find out why and fix it
/chann 자러 간다, 이 마이그레이션 테스트 전부 통과할 때까지 해줘
$chann diagnose the slowdown from captures/startup.cpuprofile
/chann babysit PR 42 until merge-ready
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
| hillclimb | Repeated experiments against one metric | A fixed benchmark and a record of each attempt |
| runtime-forensics | A symptom on a running process | A live capture and cited diagnosis |
| trace-forensics | A saved trace, profile, or heap snapshot | A diagnosis grounded in the capture |
| visual-parity | Preserve an authorized visual baseline | A reproducible image diff |
| eval | Measure skill or agent behavior | Blinded scores and observable evidence |
| autopilot | Drive a PR queue or dependency stack | A verified verdict for each PR |
| opening-a-pr | Open a requested PR | A reviewable pull request |
| babysit | Check or drive a PR to merge-ready | Current conflicts, review, and CI status |
| shipping | Commit, push, deploy, merge, cleanup | What lands and how far it reaches |
| pause-and-pickup | Stopping safely or resuming | The resume point |
| docs | One document | Every claim holding for the commit it ships in |
| authoring-a-skill | Writing or fixing a skill | Every sentence an agent reads |
| spec | An ask still too vague to plan | The statement of what gets built and how done is checked |
| api-design | An API, module boundary, or public interface | The contract a caller sees |
| ui | An interface a person operates | What a person sees, hears, and can operate |
| security | Untrusted input, auth, secrets, dependencies | The trust boundaries and their controls |
| instrumentation | Logs, metrics, traces, alerts | The questions the running system can answer |
| migration | Retiring or replacing something with consumers | The path to the new shape and the removal of the old |
| ci | A build, test, or deploy pipeline | The gates every change passes |
| launch | A production launch or staged rollout | The exposure decision and the way back |

For PRs, `babysit` can do a read-only check, handle review threads, or
drive to merge-ready. `autopilot-stack` verifies each PR and hands it
back. To land a queue, include the PRs and permission to merge in the
request. The playbook checks that the current head and base are covered
by the evidence before landing each PR.

Based on the [22 pstack playbooks at c3464c11](https://github.com/backnotprop/pstack/tree/c3464c11c60b1352d5e8f5f0428a3a6943837568/skills/poteto-mode/playbooks)
by Lauren Tan (MIT). [The upstream mapping](../tests/test_upstream_skill_disposition.py)
shows where each workflow lives in this package.

The spec, api-design, ui, security, instrumentation, migration, ci, and launch
playbooks, the `design-the-contract-first` and `hold-the-quality-bar`
principles, and `references/rationalizations.md` are based on
[agent-skills at e997ac5b](https://github.com/addyosmani/agent-skills/tree/e997ac5b9a74eab332d5e9793bb38a38c8cfdd74/skills)
by Addy Osmani (MIT). [The disposition test](../tests/test_agent_skills_disposition.py)
records, for each of its 26 skills, the file here that carries the behavior or
the skill that already owned it.

## Routing

| Situation | Skill (when installed) | Playbook |
|---|---|---|
| How does this code work | `how` | investigation |
| Why was it built this way | `why` | investigation |
| An outside library, API, or spec question | `research-brief` | investigation |
| Something is broken, throwing, or flaky | `bug-hunt` | bug-fix |
| Something is slower or heavier than it should be | `bug-hunt` | perf |
| Improve one metric over repeated, measured attempts | none, inline | hillclimb |
| Diagnose a live symptom by capturing a profile or trace | none, inline | runtime-forensics |
| Diagnose from a saved profile, trace, or heap snapshot | none, inline | trace-forensics |
| Add logs, metrics, traces, or alerts | none, inline | instrumentation |
| New or changed behavior | none, inline | feature |
| Design an API, a module boundary, or a public interface | none, inline | api-design |
| Build or change an interface a person operates | none, inline | ui |
| Match an authorized visual baseline across a migration | none, inline | visual-parity |
| Structure changes, behavior does not | none, inline | refactoring |
| Comments that narrate the code, or a request to strip them | `no-comments` | refactoring |
| Retire or replace an API, a system, or a stored-data shape | none, inline | migration |
| A page whose controls wake a bot through a webhook | `make-bot-ui` | feature |
| A fork an experiment can settle | none, inline | prototype |
| Several competing attempts at one artifact | `arena` | prototype |
| Measure the behavior of a skill, prompt, model, or agent setup | none, inline | eval |
| An ask still too vague to plan, or a spec to write first | `review-me` | spec |
| A plan or design with open decisions | `review-me`, `plan-summary` | plan |
| Review a change for defects and reach | `interrogate`, `blast-radius` | review |
| Explain a change or a plan document | `diff-summary`, `plan-summary`, `diff-viewer` | review |
| Harden code that handles untrusted input, auth, secrets, or dependencies | `interrogate` | security |
| Independent slices to run in parallel | `swarm` | fan-out |
| Multi-milestone or unattended work | `long-task` | autonomous-run |
| Run a queue or stack of PRs through independent verification | none, inline | autopilot |
| Open a pull request for verified work | none, inline | opening-a-pr |
| Check or drive an existing PR to merge-ready | none, inline | babysit |
| Set up or change a build, test, or deploy pipeline | none, inline | ci |
| Prepare a production launch, a staged rollout, or a rollback | none, inline | launch |
| Commit, push, deploy, merge, conflicts, cleanup, reinstall | `git-commit`, `git-merge`, `git-resolve-conflicts`, `git-cleanup`, `build-reinstall` | shipping |
| Stopping, resuming, catching up | `handoff`, `recall`, `catchup` | pause-and-pickup |
| Docs and prose | `gen-docs`, `unslop` | docs |
| Writing or fixing a skill, capturing lessons | `skill-forge`, `skill-audit`, `reflect` | authoring-a-skill |

## Package layout

```text
chann-mode/
├── .claude-plugin/plugin.json
├── commands/chann.md
├── skills/chann/
│   ├── SKILL.md                     # first move, routing, principles index, autonomy, delegation, evidence, reply
│   ├── worker.md                    # rules every delegate reads first
│   ├── playbooks/<name>.md          # 30 playbooks
│   ├── references/principles.md     # twenty-nine principles, each with a test
│   ├── references/rationalizations.md # the excuse for skipping a step, and the principle that answers it
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
