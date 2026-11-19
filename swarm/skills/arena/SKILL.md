---
name: arena
description: Use when the user wants several competing attempts at one artifact and the best one kept, including "arena this", "여러 안 만들어서 비교해줘", "후보 여러 개 경쟁시켜줘", "시안 몇 개 뽑아서 제일 나은 걸로 골라줘", "give me N attempts and pick the best", "try a few designs and keep the best", "/arena", or "$arena". Runs one prompt on separate candidates, has a judge from another vendor score them against a hidden rubric, picks a base, grafts the best parts of the others into it by hand, and verifies the result. For different slices of one job merged into one report use swarm, and for interviewing the user about the decisions in a plan use review-me. A mechanical task whose shape is already settled is done once, not raced.
---

# Arena

Several candidates attempt the same task. A judge from another vendor scores
them, this session picks a base, and the parts worth keeping from the others
are grafted onto it. One attempt at a non-trivial artifact locks in its first
shape; an arena shows the shapes you did not think of.

Track the six phases in the host's task list before launching anything.

## When not to run

Refuse, say why, and do the task once instead when:

- The task is mechanical and its shape is already settled: a rename, a version
  bump, a known fix, a format conversion. Competing attempts would differ only
  in noise.
- The job is different slices of one piece of work. That is `swarm`.
- The user wants to be interviewed about the decisions in a plan. That is
  `review-me`.

## 1. Frame

- Name the artifact every candidate produces, and where the real thing it
  will be checked against lives.
- Derive a rubric of three to six criteria that can be graded for this task,
  such as "the public interface has at most N entry points" or "every error
  path is tested". The rubric is for judging and stays hidden from candidates,
  so they aim at the task and not at the grader.
- Write one prompt. Every candidate gets the same one, so the prompt is the
  contract: the task, the shared context paths, the constraints, its output
  location, and what to return.
- Pick the seat count, usually three. Add a seat for each genuinely different
  design direction worth exploring; two is the minimum.

## 2. Fan out

- Give each candidate its own output location: its own Git worktree when it
  edits a repository, otherwise its own temporary directory. Candidates never
  share a write target.
- When the `swarm` skill is installed, seat the candidates through it as a
  race with the `best of` rule, so seats land on different vendors and the run
  leaves a call tree. Without it, use the host's subagent tool and say that
  the candidates share one vendor.
- Launch every seat at once and wait for completion notices; do not poll.
- Each candidate returns the artifact and a short rationale naming the
  alternatives it considered and rejected.
- A candidate that returns nothing is a dropout. Continue with the rest and
  say so. With fewer than two candidates left there is nothing to compare:
  report the dropout and treat the survivor as a single attempt.

## 3. Cross-judge

Spawn one read-only judge after every candidate has finished. Give it the
rubric and the candidates under neutral labels (`A`, `B`, `C`), never model
or vendor names. It scores each candidate on each criterion, with a reason per
score, and recommends a base.

Take the judge from a different vendor than the session running the arena
when one is available. When none is, or this session's vendor is unknown, run
the judge anyway and say that the vendor check did not run. When no judge can
run at all, say that judging was skipped.

## 4. Pick a base

Read every candidate end to end yourself, not its summary, and score it
criterion by criterion before reading the judge's scores.

- Agreement with the judge confirms the pick.
- Disagreement means one side is biased or the rubric is ambiguous. Read both
  rationales, decide, and say which reading won and why.
- Pick the base a later maintainer can extend without breaking its
  invariants. Between near ties, prefer the smaller interface.

## 5. Graft

Walk each losing candidate once more for the one or two things worth
keeping, usually not more. Fold each into the base by hand so the result
still reads as one design; never paste a block across mechanically.

- Candidates that converge on one shape are strong agreement. Ship that shape
  and graft nothing.
- Candidates that diverge wildly mean the frame was under-specified. Reframe
  and rerun; never average the divergence into one artifact.

## 6. Verify

Check the synthesized artifact against the real thing like any other output:
run its tests, build it, or exercise it, and report `VERIFIED`,
`NOT VERIFIED`, or `INCONCLUSIVE` with the evidence. When verification finds
a problem, either the frame was wrong (reframe and rerun) or a candidate had
it right and the graft missed it (go back to Graft). Do not patch over it.

## Refusals

- Do not race a mechanical task whose shape is settled.
- Do not show candidates the rubric, or the judge any model or vendor name.
- Do not let two candidates write to the same location.
- Do not pick a base from summaries or from the judge alone.
- Do not average wildly divergent candidates into one artifact.
- Do not claim cross-vendor judging when the vendor check did not run.

**Reply:** the synthesized artifact; the base and why; the judge's verdict, or that judging was skipped or ran without the vendor check; each graft with its source candidate; what was rejected and why; convergence or dropouts; the verification verdict with its evidence.
