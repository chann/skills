# Prototype

**You own one decision. The code is a throwaway instrument.**

1. Write the decision the prototype exists to make in one line, such as "stream
   or page the results". No decision means no prototype: go to feature.
2. Build outside production source, in a scratch directory or a throwaway
   worktree, with the lightest stack that shows the difference. No tests, no
   abstractions, no polish.
3. Put the variants side by side behind one switch (a flag, a key, a URL
   parameter), each labelled, so a single observation compares them. When the
   space is open, add a variant nobody asked for.
4. When competing attempts at one artifact should run independently and be
   judged against each other, use `arena` when installed; otherwise build each
   variant in its own scratch directory.
5. Observe the thing being decided on its real surface: a screenshot, a
   timing, the printed output. The observation is the test.
6. Decide, then delete or archive the scratch code. The real build starts from
   the chosen direction under the feature playbook.

**Reply:** the decision, each variant with its evidence, the recommendation and its tradeoff, the scratch path, and a plain statement that the prototype code does not ship.
