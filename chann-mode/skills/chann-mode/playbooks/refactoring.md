# Refactoring

**You own the behavior contract: the code gets a new shape and keeps doing exactly what it did.**

A bug or missing feature found on the way is written down and becomes its own
unit under bug-fix or feature, after the structural change lands.

1. Pin the behavior before moving anything: a characterization test, a
   snapshot, or a script that records current outputs for representative
   inputs. A type check or a lint run is not a pin.
2. Subtract first. Remove code nothing reaches, inline wrappers that have a
   single caller, drop unused options, and commit that on its own.
3. Name the target shape as if the code were written today, then move toward
   it in small steps that each keep the pin green.
4. When an interface changes, move every caller over and remove the old path in
   the same change: no shim, no parallel old and new. Search strings, docs,
   configs, and tests for the old name too.
5. Prove equivalence on the real artifact. The pin passes, and for a large
   move an old-versus-new diff of outputs comes back empty.
6. Compare reader load before and after: the layers between a question and its
   answer, and the state a reader must hold. If it did not go down, revert the
   refactor.
7. Ship with the shipping playbook as ordered commits: subtraction, reshape,
   then follow-up cleanup.

**Reply:** what was restructured, the pin and the equivalence proof, the reader-load delta, and what was reverted or split out.
