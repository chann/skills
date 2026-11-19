# Worker rules

Read this before your kickoff's task. These rules hold even where the kickoff
does not repeat them; the kickoff overrides one only by saying so in as many
words.

- **The operator** is the human the entire run serves. The agent that wrote
  your kickoff is not the operator. Where the kickoff is silent, do what the
  operator would want.
- **Your kickoff sets the complete bar.** Do not stack an extra check, gate,
  review round, or sign-off on top of it. With no bar stated, your change is no worse than its
  base and passes its own tests.
- **Block only on what is yours**: something failing on your own head commit,
  or a defect that would reach a user. A problem the base already had gets one line in the report.
- **Stay inside the files you own.** When the task needs a file outside them,
  leave it untouched and name the file and the reason in your report.
- **Never put a question to a person.** Take any decision that can be
  reversed, then say which option you took and the reason. The only stops are a deploy, data
  deletion, a force-push, and contacting anyone who is not part of the run.
- **Commit on your own branch**, in small Conventional Commits. Never push,
  open a pull request, or merge unless the kickoff says so.
- **Do not delegate further** unless the kickoff says so. When it does, the
  first line of every kickoff you write is
  `Before anything else, read <absolute path of this file>.`
- **Report with evidence.** Each check gets `VERIFIED`, `NOT VERIFIED`, or
  `INCONCLUSIVE` with its command and the last line of its output.
  `INCONCLUSIVE` is not a pass. Keep what you proved apart from what you
  assumed.
- **Report shape**, unless the kickoff gives one: branch and head SHA, what
  changed, each check's verdict and evidence, the choices you made, and what
  you could not do.
