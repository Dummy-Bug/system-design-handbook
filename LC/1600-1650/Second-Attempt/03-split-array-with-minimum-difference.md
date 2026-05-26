# Split Array With Minimum Difference (cold re-solve) — Second Attempt (Cold Re-solve)

| Field | Value |
|-------|-------|
| Date | 2026-05-25 |
| Link | https://leetcode.com/problems/split-array-with-minimum-difference/description/ |
| Rating | 16xx |
| Time | ~30min |
| Pattern | prefix-valid / suffix-valid scan + split point |

### Thinking log (verbatim)

- n² ruled out by constraints.
- Problem needs strict sequences. Traverse from left, find first invalid-sequence point → left subarray can extend only up to that valid point. Same from the right side.
- While scanning, keep running `lsum` and `rsum`.
- If there's only one such point, both left and right pointers point to one element only, and that element can belong to either `lsum` or `rsum` → must remove it from one of them to get the minimum difference.
- Took ~5-7 min to work out how to reduce the sum from one of the two sides.

**Step 2/3 — example traces (self-generated):**
- `[1,3,2]` → works.
- `[1,2,3]` → l=2, r=2, works.
- `[3,2,1]` → works.
- `[1,2,1,2,1]` → fails. Conclusion: when left pointer != right pointer (more than one split candidate / gap doesn't collapse to a single shared element), return -1.
- `[1,2,3,3,2,1]` → fails the single-shared-element model. Refinement: check the gap between left and right pointers. If the gap is exactly one (two boundary elements, no shared element), answer is `abs(lsum - rsum)` directly — no element to remove since there isn't a single shared one.
- `[1,2,3,3,3,2,1]` → works; gap > 1 → return -1.

### Outcome (Split Array)

**First-submission AC.** ✅ Clean — counts as pass under tightened graduation rules.

Final case split:
- `left == right` (single shared element): answer = `min(|lSum - nums[left] - rSum|, |lSum - (rSum - nums[right])|)` — the shared element goes to whichever side minimises the gap.
- `left + 1 == right` (no shared element, clean split): `|lSum - rSum|`.
- else (gap > 1, can't form two strictly-increasing-then-decreasing halves): `-1`.

### Code-quality reflection (self-raised)

User noted the `left++` then `left--` (and the right mirror) is clumsy — the post-loop decrement undoes the last increment. Cleaner: increment only on the success path so the pointer lands on the last valid index without a correction step:

```java
while (left + 1 < n && nums[left + 1] > nums[left]) left++;   // left ends on last valid index
```

Same for the right side. Removes the two `left--` / `right++` fixups and the off-by-one risk they carry. Good self-catch — this is exactly the "sentinel / last-element init" family from the pre-submit checklist (item 8).

**Verdict: clean first-submission AC (3/10).** No ritual break, no WA.

**Bug 2: Step 2 trace was sub-step only, not full pipeline.**

The trace covered "cba" → "azy" (normalization), which verified the *interesting* sub-step. It did NOT walk the full input → return path on any example. Had `["a","a","a"]` been traced end-to-end, the over-count would have surfaced pre-submit.

*Lesson:* **Step 2 means full-pipeline trace.** Input array → all loops → final return. Not just the interesting computation. This is the step-2 enforcement contract being half-met.

**Bug 3: Java-impl reflex gaps (caught at compile, not submit).**
- `Map<String, long>` — generic requires boxed `Long`.
- `StringBuilder.add('a')` — method is `append`.
- `getOrDefault(key)` — missing second arg.
- `Map.getValues()` — method is `values()`.

Not WAs, but reflex gaps. `StringBuilder.append`, `Map.values()`, and `getOrDefault` signature should be muscle memory.

### Recurring patterns this confirms

- **Step 2 needs to be full-pipeline.** Partial trace (only the sub-step that feels interesting) doesn't catch bugs in the orchestrator. Confirmed across #1 and #2 — both had bugs the partial trace missed.
- **Delta vs cumulative** is a real bug family. Add to pre-submit checklist as item 15 candidate.
- **Derivation speed is slow on basic math.** 20 min on n(n-1)/2 is too long for a 1450-level formula.

---
