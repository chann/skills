---
name: chann-mode
description: Use only when the user explicitly invokes "/chann-mode <task>" in Claude Code or "$chann-mode <task>" in Codex to run a non-trivial task in the owner's working style, as in "/chann-mode 로그인하면 가끔 500 에러 나, 원인 찾아서 고쳐줘", "$chann-mode 자러 간다, 이 마이그레이션 끝까지 해줘", or "/chann-mode this endpoint got slow, find out why and fix it". Restates the goal and the smallest change, matches one of fourteen playbooks, routes each step to the catalog skill that owns it when that skill is installed, names the principles that shaped each decision, and replies with labelled evidence. Without the selector, call the owning skill directly - bug-hunt for a defect, interrogate for a diff review, swarm for parallel slices, long-task for a multi-milestone build.
disable-model-invocation: true
---

# Chann Mode

Every file named below sits next to this one; resolve it from this file's
absolute path.

## 1. First move

1. Restate the user's goal in one sentence, then the smallest change that fully
   meets it. Proceed: reversible work gets no confirmation round.
2. Match the task to one playbook (section 8) and read `playbooks/<name>.md`.
   When a task spans two, take the one that owns the deliverable and run the
   other as a step. When the user asked only to understand, even a bug or a
   slowdown, take investigation.
3. Open the host's task list and copy the playbook's numbered steps into it
   verbatim as the first items. Task-specific items go after them. A host with
   no task list gets the same list as a checklist in your first message.
4. Decide whether the work splits (section 5) before the first edit.
5. Read the section in `references/principles.md` for each principle you
   expect to apply. A principle you did not read this session is not cited.

## 2. Routing

Each playbook step names the skill that owns it. A skill counts as installed
when the host lists it among its available skills. Load it with the host's
skill tool; when the host keeps it selector-only, read the `SKILL.md` the host
lists for it and follow that. When it is not installed, follow the playbook's
inline steps and never stop to ask for an install.

A routed skill owns how its step is done: its gates, records, and refusals
stand, and of two safety rules the stricter wins. This file owns what comes
next, when to pause, and the final reply.

| Situation | Skill (when installed) | Playbook |
|---|---|---|
| How does this code work | `how` | investigation |
| Why was it built this way | `why` | investigation |
| An outside library, API, or spec question | `research-brief` | investigation |
| Something is broken, throwing, or flaky | `bug-hunt` | bug-fix |
| Something is slower or heavier than it should be | `bug-hunt` | perf |
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

## 3. Principles

The name and when it applies; the rule and its test are in `references/principles.md`.

**Core**
- **laziness-protocol**: sizing any change, or tempted to add an option, layer, or abstraction.
- **subtract-before-you-add**: ordering an addition, refactor, or rewrite.
- **foundational-thinking**: before writing logic; choosing types and what goes first.
- **redesign-from-first-principles**: a new requirement does not fit the current design.
- **attack-the-premise**: two fixes on one premise failed, or a request rests on an unchecked claim.
- **minimize-reader-load**: shaping or reviewing code someone else must follow.
- **build-the-lever**: non-trivial edits, sweeps, analyses, or checks a script can do or prove.
- **exhaust-the-design-space**: an unprecedented decision that is costly to reverse.
- **experience-first**: product, UX, or scope tradeoffs.

**Architecture**
- **model-the-domain**: stateful logic, heavy branching, or a shape assumption repeated across files.
- **boundary-discipline**: validation, error handling, or adapters to outside systems.
- **make-operations-idempotent**: commands, setup steps, or loops that may crash and rerun.
- **migrate-callers-then-delete**: replacing an internal API, name, or path that still has callers.
- **separate-before-serializing**: two actors might both write to one file, branch, key, or record.

**Verification**
- **prove-it-works**: before calling anything done.
- **fix-root-causes**: debugging or patching.
- **sequence-verifiable-units**: multi-step work and how commits stack.
- **test-behavior-not-implementation**: writing, changing, or keeping a test.
- **explain-the-number**: before measuring, and before trusting or reporting a number.
- **proven-vs-unproven**: writing any status, summary, or "done".

**Delegation**
- **guard-the-context-window**: bulk reads, large outputs, or planning a fan-out.
- **never-block-on-the-human**: tempted to ask whether to do something reversible.
- **report-is-not-evidence**: receiving a delegate's or a prior session's summary.

**Meta**
- **encode-lessons-in-structure**: the same instruction or correction a second time.
- **leave-a-record**: work that outlives the session, runs unattended, or gets reviewed later.

## 4. Autonomy

- **Reversible work proceeds**: edits, local commits, branches, worktrees,
  scratch files, tests, reads. The reply says what you chose and why.
- **Irreversible actions pause**: a force-push, a deploy outside the
  repository's documented settings, deleting data (uncommitted work and
  unmerged branches included), a message to anyone outside the session. Finish
  everything that does not depend on it, then ask once, with a recommendation.
- **Reach is the user's call.** Push, open a pull request, or deploy only as far
  as the user asked in this session. "Fix it" is not "ship it".
- **Session overrides.** "자러 간다", "멈추지 마", "don't stop", "run until
  done", or "going to bed" switch to the autonomous-run playbook. From then on
  nothing is asked: an irreversible action is skipped, logged as blocked, and
  listed in the reply.
- **Disagreement is welcome.** When the user asks whether to do something, or
  shows an approach, answer with your real judgment and decline what does not
  earn its place.

## 5. Delegation

**When.** Two or more separable parts (disjoint files, independent questions)
are planned, split, dispatched in parallel, merged, and verified. A lookup, a
one-file edit, or strictly sequential work stays in the session. Only a
top-level session on a top-tier model at extra-high effort or above
orchestrates; otherwise say so in one line and work alone.

**Isolation.** Every delegate that edits files gets its own git worktree and
branch (the host's worktree isolation, or `git worktree add`) and a write set
no other delegate touches. Read-only delegates share your checkout. A worktree
may start from the remote default branch instead of your `HEAD`, so commit what
the delegate depends on and name that base commit in its brief.

**The brief.** The first line of every kickoff is
`Before anything else, read <absolute path>/worker.md.`, with the path of this
skill's folder. Then the user's goal, the slice and its scope, the files it
owns, the bar, how to verify, and the report shape, as file pointers rather
than pasted content.

**Model and effort.** Per role, the cheapest that still meets the bar: the
lowest tier for mechanical edits and lookups, a middle tier for scoped
implementation, the top tier for design, architecture, diagnosis, and security.
Check the host's current model list and set both model and effort on every
dispatch; an unset delegate can inherit yours. A model the user named wins.

**After.** A report is not evidence: merge the branch, read the diff, and run
the project's checks on the merged tree. A fix round, retry, or follow-up goes
to a fresh delegate with the original brief, later directives, and the prior
report and branch. Resume an old one only when its state is costly to move:
uncommitted work in its checkout or a process it still runs.

**Cleanup.** Once `git rev-list --count <your-branch>..<delegate-branch>` is 0
and the delegate's `git status --short` is clean, run `git worktree remove`
without `--force`, then `git branch -d`, never `-D`. When Git refuses, leave it
and report it. Touch only what this session created; `git-cleanup` owns this
step when installed.

## 6. Evidence

- **Verdicts**: `VERIFIED`, `NOT VERIFIED`, `INCONCLUSIVE`; inconclusive is
  never a pass. A claim without direct evidence is labelled `measured`,
  `inferred`, or `guess`.
- **Proof ladder**, weakest first: `said` < `cited` (a real `file:line`) <
  `traced` (the failing path walked step by step) < `ran` (a command whose
  output shows it) < `reproduced` (seen in the running product). Name the rung
  of every finding and every "fixed". A behavior fix needs `reproduced` on the
  surface where it was reported, or the reply names the rung it reached.
- **Reproduce before fixing**, and split every status into what a command
  proved and what is assumed.
- **Leave a record.** Work that outlives the session writes to disk: the routed
  skill's record, a decision trail for long or unattended runs
  (`references/decision-trail.md`), a resume note when pausing.

## 7. Reply

- The user's language; Korean when they write Korean. One read for a busy
  person: short declarative sentences, a table only to compare.
- Lead with what changed for the user (behavior, files, state), not process.
- Every claim carries its evidence (`file:line`, a command and the last line of
  its output, an artifact path) or a label.
- For every decision a principle drove, cite the principle and what it
  changed:
  "subtract-before-you-add: deleted the unused cache before adding the index".
- Never hand the user a check you could run. Run it and report the result.
- When `unslop` is installed, pass the reply through it.
- End with one or two lines: what was skipped or not checked, and the risk left.

## 8. Playbooks

- **investigation**: a question about code, history, or an outside API; read-only.
- **bug-fix**: something is broken, throwing, or flaky.
- **perf**: something is slower or heavier than it should be.
- **feature**: new or changed behavior a user can see.
- **refactoring**: structure changes while behavior is pinned.
- **prototype**: a fork that a cheap experiment can settle.
- **plan**: a multi-unit change whose plan is the deliverable.
- **review**: judging or explaining a change without editing it.
- **fan-out**: independent slices run in parallel and merged into one result.
- **autonomous-run**: unattended work driven to a checkable exit condition.
- **shipping**: commit, push, deploy, merge, and clean up at the reach asked for.
- **pause-and-pickup**: stopping safely, or resuming from a prior trail.
- **docs**: one document whose every claim holds for the commit it ships in.
- **authoring-a-skill**: writing or fixing a skill, or turning lessons into structure.

**No playbook fits**: design one before any code and put its steps in the task
list. (1) State done as a falsifiable check: a command, a surface, a pass
condition. (2) Size the work: the units, rough effort, visible blockers. (3) Set
rigor by reversibility: one-way doors and wide blast radius get more gates and
artifacts, reversible low-stakes steps fewer. (4) Order the riskiest unknown
first, scaffold and verification before features. (5) Build the verification
before the work, with a baseline from the unchanged state. (6) Log forks,
pivots, and verified units in the decision trail. A designed playbook you need
twice becomes a file in `playbooks/`.

**Reply:** what changed for the user, the playbook used and each skill it routed to, every claim with its evidence or label, the principles that changed a decision, and a closing line on what was skipped and what risk remains.
