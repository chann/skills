# Authoring a skill

**You own every sentence the skill makes an agent read.**

1. Cut whatever you are unsure about. A sentence stays only if an agent would
   decide differently without it. Say what to do, and give the reason only
   where the rule is confusing without it.
2. Write or reshape the skill with `skill-forge` when installed; it holds the
   package contract for names, descriptions, selectors, evals, and manifests.
3. Write evals about the gates and orderings that break when the skill is
   followed sloppily, not about wording.
4. Run the contract audit (`skill-audit` when installed) and the package
   tests. The contract and the audit decide whether it ships, not how it reads
   to you.
5. A lesson a script can enforce becomes a script, a test, or an audit rule,
   not another paragraph.
6. To capture lessons from a session or a repository, use `reflect` when
   installed, and land each lesson where it will next be read.
7. Ship with the shipping playbook.

**Reply:** what the skill now does, the decisions that shaped it, the audit and test output, and what was deleted.
