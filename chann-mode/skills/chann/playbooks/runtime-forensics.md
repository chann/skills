# Runtime forensics

**You own the diagnosis of a live symptom and the evidence that connects it to the running code.**

1. Identify the affected process, build, symptom, and time window. Find a
   capture interface already supported by the host or project. Use only
   authorized targets and capture methods. If live access or the needed
   capture capability is missing, name it and analyze any available fixed
   artifact with the trace forensics playbook.
2. Capture the smallest signal that answers the question on the affected
   surface, such as a CPU profile for a busy process, a heap snapshot for
   unexpected retention, or a timeline for a stalled interaction. Check that
   the symptom occurred in the capture window and record the capture settings,
   build, and artifact location. Keep sensitive data out of the report.
3. Reduce the capture to the relevant frames, events, wait reason, or
   retainer chain. Cite timestamps, sample counts, or object identifiers so
   someone else can locate the evidence. Check for capture artifacts and
   comparable healthy activity before assigning a cause.
4. Map the finding to the matching revision and the source line that
   allocates, schedules, blocks, or runs the work. Test the leading
   explanation with a supported read-only observation or a controlled
   comparison on an authorized safe target. Use passive evidence for
   suspected security issues and avoid reproducing exploits.
5. State what the evidence confirms, what remains inferred, and what
   observation could settle any uncertainty. If confirmation would need
   live code changes, new production instrumentation, or unavailable access,
   report the limit. Leave fixes to a separate request.

**Reply:** affected build and window, capture method and artifact path, reduced evidence, source location, confirmation or limitation, and diagnosis.
