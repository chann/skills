# Choosing a route

The helper checks the plan. It does not rank models. Ranking is a judgment
made from the transcripts collected in `routes.md`, then recorded so the
judgment can be rejected when it breaks a rule.

## Plan file

```json
{
  "task": "code_review",
  "speed": "normal",
  "distinct_vendors": true,
  "exclude_vendors": [],
  "include_vendors": [],
  "require_vision": false,
  "steps": [
    {
      "task_id": "review",
      "route_id": "claude-code/anthropic/claude-opus",
      "vendor": "anthropic",
      "vision": true,
      "rationale": "Code review is the task. Opus is the strongest authenticated Claude model and the weekly bucket is under the cap.",
      "quota_note": "weekly all-models 40% used",
      "quota_source": "/absolute/path/usage.txt",
      "fallbacks": ["claude-code/anthropic/claude-sonnet"]
    }
  ]
}
```

`task` is one of `code_review`, `security_audit`, `architecture`, `debugging`,
`ui_debugging`, `frontend`, `code_generation`, `refactoring`, `testing`,
`prose`, `documentation`, `survey`, or `general`.

`quota_note` is either the literal `unknown` or a sentence whose numbers all
appear in `quota_source`. The rationale is at least 40 characters and has to
say why this route fits the task. When `require_vision` is set, every step
needs `"vision": true` and the rationale has to say so. When `speed` is `fast`
or `urgent`, the rationale has to say so.

## Rules that outrank a hunch

- Prefer the strongest authenticated model that fits the task and still has
  quota headroom. A tight account may remove a route. It may not silently
  replace a vendor's top model with a weaker model of the same vendor when the
  user asked for that vendor's best.
- A UI mock, a screenshot, or a browser capture requires vision. Do not send
  those tasks to a text-only model.
- `fast` and `urgent` break close calls toward the model that answers sooner.
  They do not override a clearly better fit.
- When two routes are otherwise tied, prefer the one released more recently.
  An unknown release date is a tie, not a penalty and not a bonus. Say when
  recency decided the call.
- Independent steps use different vendors. That is what makes the second step
  a check rather than a second draw from the same model. Set
  `distinct_vendors` to false only when the user required one vendor.
- A fallback handles `quota`, `auth`, or `unavailable` for that step. It does
  not replace a later planned step. It stays on the same vendor unless
  `include_vendors` lists the other vendor, and it cannot reintroduce a vendor
  in `exclude_vendors`.
- `pin_model` forces every step onto that model id. Use it when the user named
  one model, not when they asked for a second opinion.
- At most four steps. Split a larger fan-out into a later run.
- Do not dispatch a heavy task onto a pool whose remaining quota cannot finish
  it, even when the percentage still looks full because the pool itself is
  tiny. If the transcript does not show remaining capacity, say `unknown` and
  do not pretend the pool is large.

## One usable route

If probe says the machine is not heterogeneous and the user did not name an
agent or model, do not write a plan. Do the work in this session and say that
only one route was usable.

## Races

A race runs the identical brief on two to four routes. Each arm is an
independent step, so each arm sits on a different vendor unless the user
forced one. Declare the selection rule in the plan's rationale before any arm
runs:

- `first pass`: the first arm that answers `PASS` with its required evidence
  wins; later arms still get read for issues.
- `rank all`: every arm is ordered, best first, with the reason for each place.
- `best of`: every arm is scored against the brief and one is kept.

Do not change the rule after reading the arms. When the arms are attempts at
one artifact that should be merged into one design, that is `arena`, not a
race.
