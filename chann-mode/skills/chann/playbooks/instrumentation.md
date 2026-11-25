# Instrumentation

**You own the questions the running system can answer about itself.**

1. Write two to four questions someone on call will ask about this feature.
   Every signal added answers one of them; a signal with no question is not
   added.
2. Pick the signal by the question: a metric for how often and how fast, a
   trace for where the time went across hops, a structured log for what
   happened in one case.
3. Emit logs as structured fields under one stable event name, through the
   logger the project already has. Carry one request id across every async
   boundary. Never log secrets or personal data.
4. Measure requests, errors, and duration at each entry point and each outside
   dependency. Keep label values few and bounded; an id is a log field, not a
   label.
5. Alert on what users feel (error rate, latency, queue age), each with a
   threshold and a duration taken from data, and a runbook of at least three
   lines: what it means, the first check, who to escalate to. Delete an alert
   whose response is to ignore it.
6. Verify the telemetry itself. Trigger the path, find the event by its id,
   confirm the fields arrive structured and the series shows sane values, and
   fire each new alert once.
7. Ship with the shipping playbook.

**Reply:** the questions, the signal that answers each, the telemetry you observed after triggering the path, the alerts with their runbooks, and what still cannot be observed.
