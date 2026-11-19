# Investigation

**You own the answer. Nothing in the repository changes.**

1. Write the question in one sentence and check its premise against the code
   before answering. When the premise is wrong ("why does X retry twice" and X
   never retries), say so first, then answer the question the user needed.
2. Route by the kind of question: how code works to `how`, why it was built
   this way to `why`, an outside library, API, or spec to `research-brief`,
   each when installed. Otherwise trace it yourself: the entry point, the data
   path, and the branch that decides the behavior; for motivation, read
   `git log` and `git blame` on those lines and what their commits cite.
3. Read the code instead of inferring behavior from names. When reading cannot
   settle it, run something (a test, a script, a REPL) with scratch files kept
   outside the tree.
4. Cite each claim with `file:line` or a commit. Label the rest `inferred` or
   `guess`.
5. Shape the answer as **Answer** (two to four sentences), **How it works**
   (the path, step by step, each step cited), **Where it lives** (the files to
   read first), **Gotchas**, and **Unverified**. For a choice between options,
   replace How it works with a table of options and tradeoffs, and recommend
   one.
6. When the answer shows a change is needed, name the playbook that would make
   it and stop. Do not start it inside this one.

**Reply:** the answer in that shape with a citation on every claim, a pushback first when the premise was wrong, and real judgment with reasons when asked "are we sure?".
