# Security

**You own the trust boundaries: what crosses them, and what stops it.**

1. Map where data someone else wrote enters the system: requests, uploads,
   webhooks, third-party responses, queue messages, file names, the
   environment, model output. Trust follows who wrote a value, not the channel
   that delivered it.
2. Name what is worth stealing or breaking (credentials, personal data, money,
   admin actions). At each boundary ask six questions: can someone
   impersonate, alter, deny, read, exhaust, or escalate?
3. Write each abuse case as a check before the control: the request that must
   be refused, watched succeeding against the unfixed code.
4. Put the controls at the boundary: parse and validate input, parameterize
   every query, encode output, check authorization on the server for every
   object, keep secrets out of source and logs, allowlist the hosts a
   server-side fetch may reach, and rate-limit anything costly.
5. Pause for the user before changing authentication or session logic, CORS,
   permissions, upload handling, a new category of sensitive data, or a new
   outside integration. Those are decisions, not execution.
6. Run the package manager's own audit against the committed lockfile and
   triage each finding by whether the vulnerable path is reachable. Check a
   new dependency's owner, activity, and install scripts before adding it.
7. Prove each control on the real surface: the abuse case from step 3 is now
   refused, with the response shown. Review the diff with `interrogate` when
   installed.
8. Ship with the shipping playbook, and state the risk that remains.

**Reply:** the boundaries and assets, each abuse case with its before and after output, the audit findings and how each was triaged, the decisions left to the user, and the residual risk.
