# Trace forensics

**You own the diagnosis supported by an existing capture.**

1. Identify the format, build, capture window, and reported symptom. Keep the
   supplied artifact intact and treat it as a fixed dataset. Use a project
   parser, host viewer, or a compatible local reader. If none can read the
   file, report the exact missing capability or invalid input.
2. Inspect the relevant time window, threads, frames, or objects. If the
   artifact is too large for direct inspection, extract an indexed view in
   scratch space and retain the original timestamps and identifiers. Record
   the command or viewer filters so the reduction can be repeated.
3. Follow the evidence to an expensive call path, a blocked thread and its
   wait reason, or a retaining path to a garbage-collection root. Check
   units, attribution, and missing samples. Keep security analysis passive
   and avoid reproducing exploits.
4. Resolve frames against symbols or source maps for the captured build and
   cite the source revision, file, symbol, and line where available. When
   symbols or build information are missing, give the raw frame identifiers
   and qualify the attribution.
5. Compare a supplied paired capture only if the workloads and capture
   settings are comparable. State what the record shows directly and what
   remains a causal hypothesis. Report gaps in coverage or missing comparison
   data. Leave live capture and fixes to separate requests.

**Reply:** artifact path and format, reproducible reduction, cited finding and source mapping, comparison result if available, and unresolved questions.
