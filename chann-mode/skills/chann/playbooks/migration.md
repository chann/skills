# Migration

**You own the path from the old shape to the new one, and the point where the old one is gone.**

1. Decide whether it should go at all: does it still give value nothing else
   gives, who depends on it (count them with a search or usage data), and does
   a replacement exist. With no replacement, build that first.
2. Sort the consumers. Callers you can change move in the same change, and the
   old path is deleted there. Consumers you cannot change get a notice with
   the replacement, a guide, and tooling. Set a removal date only when the
   risk or the upkeep justifies forcing the move.
3. Move consumers a step at a time behind one seam: an adapter or a router
   that sends one consumer or one share of traffic to the new path, each step
   verified and reversible.
4. Never change stored data in place. Expand by adding the new shape beside
   the old, write both, backfill in batches off the hot path, switch reads,
   and contract in a separate, later deploy. Old and new code are both valid
   at every step.
5. Give every step a tested way back, and run it before the step lands. The
   destructive step goes last and alone, after a search and usage data show no
   reader. Pause for the user before dropping data.
6. Prove the old shape is gone: a search for its name comes back empty, its
   usage is zero, and the flags, adapters, and dual writes that carried the
   move are removed.
7. Ship each step as its own unit with the shipping playbook.

**Reply:** the consumers found and how each moved, the steps in order with their way back, the evidence that the old shape has no reader, and what is still running in both shapes.
