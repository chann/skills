# Visual parity

**You own the image comparison against an authorized, pre-change reference.**

1. Identify the authorized reference, components, and states. Before editing,
   capture the current implementation and, if distinct, the reference
   implementation. Use the project screenshot harness or an available
   host-native driver. If the required reference or baseline cannot be
   captured, report the missing prerequisite before editing.
2. Fix the capture conditions for both sides: viewport and device scale,
   browser and platform, fonts, theme, data, interaction state, and render
   readiness. Store the baseline and record the capture command or steps.
   Compare repeat captures before editing and stabilize any unexpected drift.
3. Record the existing visual comparison policy if the project has one.
   Otherwise require zero differing pixels. Keep the reference, baseline,
   comparison settings, and tests fixed through the migration. Never update
   the reference, add masks, or alter the test to make a difference disappear.
4. Change one component or coherent batch at a time. Recapture every covered
   state with the fixed procedure and compare against the reference. Inspect
   the diff image for failures, correct the implementation, and repeat the
   comparison under the same conditions.
5. Run the project checks and recompare all covered states on the final
   result. If capture or comparison is unavailable, mark parity unverified.
   If differences remain above the threshold, report the states and measured
   differences as failures.

**Reply:** reference and baseline paths, capture conditions and comparison rule, per-state results and diff artifacts, and any failed or unverified states.
