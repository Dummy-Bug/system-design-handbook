# House Robber V (cold re-solve, original was ambiguous-clean) — Second Attempt (Cold Re-solve)

| Field | Value |
|-------|-------|
| Date | 2026-05-22 / 2026-05-23 (across two days) |
| Link | https://leetcode.com/problems/house-robber-v/description/ |
| Rating | 1619 |
| AC | Y after 4+ WAs |
| Time | ~30min day 1 + ~30min day 2 |
| Pattern | DP with same-color adjacency constraint |
| Verdict | **Soft fail** (WA-then-AC) |

---

### Thinking log (verbatim, what was going through the mind)

**Step 1 — Constraints**
- `1 <= n == nums.length == colors.length <= 10^5`
- `1 <= nums[i], colors[i] <= 10^5`
- n log n worst-case budget identified upfront.

**Step 2 — Overflow check**
- Max sum = 10^5 × 10^5 = 10^10 → overflows int → use `long`.

*Good: overflow check happened pre-code, not after WA. This is the new pre-submit checklist item 1 working as intended.*

**Step 3 — Approach choice**
- Pick / non-pick at each index → recursion shape.
- Without DP → 2^n. With DP → much less.
- Same-color constraint: if `colors[i] == colors[i-1]`, can't pick both. Pick max of the two, or skip one.
- *(Implicit gap at this step — the "skip i entirely" branch wasn't fully articulated.)*

**Step 4 — Recurrence (first version, WRONG)**
- `F(n) = max sum at index i`
- `F(n) = f(n-1) + nums[i]` OR `f(n-2) + nums[i]` — Fibonacci-shaped.

*Bug seed: this always adds `nums[i]`. The "skip i" branch is missing.*

**Step 5 — Complexity claim**
- "Depth N, branching 2, total N calls × O(1) work = O(N)."
- *(Wrong reasoning — depth N with branching 2 is 2^N without memo. With memo, it's O(N) because N distinct states. The user got the right answer for the wrong reason.)*

**Step 6 — Chose BUP without memo**
- Decision: "for such simpler problems we should get comfortable at this stage only" — practice direct tabulation.

**Step 7 — First code submission (WA)**
Recurrence written as `dp[i] = dp[i-2] + nums[i]` (same color) or `dp[i] = dp[i-1] + nums[i]` (diff color). Both branches always add `nums[i]`. WA.

Edge case patched between WA #1 and #2: `return max(dp[n-2], dp[n-1])` instead of `dp[n-1]`. Still WA.

**Step 8 — Third attempt: tracked max across all `dp[i]`.** Same broken recurrence underneath. Still WA. Three submissions, all wrong.

**Step 9 — Break taken** (RCB vs SRH match). Self-noted: "should have ran through few test or edge cases my bad."

**Step 10 — Day 2 fresh start, memoization re-defined**
- f(n) = max robbed up to index i.
- If c[i] != c[i-1]: f(n) = f(n-1) + nums[i]
- Else: f(n) = max(f(n-1), nums[i] + f(n-2))

*This finally has the "skip i" option in the same-color branch (`f(n-1)` = skip i, keep best up to i-1).*

**Step 11 — Updated recurrence in code.** Same-color branch finally has `max(dp[i-1], nums[i] + dp[i-2])` (the skip-i option surfaced). But dp[1] was left as `nums[1]` for same-color — leftover from the first (wrong) attempt. WA. Misdiagnosed as overflow first.

**Step 12 — Root cause found.** dp[1] in same-color case should be `max(nums[0], nums[1])`, not `nums[1]`. Pick the better of the two same-color houses.

**Step 13 — Final AC** with fixed base case.

**Step 14 — Space optimization.** Only need `dp[i-1]` and `dp[i-2]` → two `long` variables. O(n) time, O(1) space. AC.

---

### Bugs caught — root cause analysis

**Bug 1: Missing "skip i" branch in recurrence (first 3 WAs).**
- Initial code always added `nums[i]`. The "skip i entirely" option was absent from the diff-color branch and only partially from the same-color branch.
- *Root cause:* the recurrence for any "choose-or-skip" DP must have BOTH branches explicit. When you write `dp[i] = ... + nums[i]`, you're forcing the pick. The skip option needs `dp[i] = max(dp[i-1], ...)` to surface.
- *Fix going forward:* whenever the problem has "pick OR don't pick", literally write `dp[i] = max(pick_branch, skip_branch)` before filling in.

**Bug 2: dp[1] base case = "old code remnant after refactor" (4th WA).**
- The dp[1] line was left over from the first (wrong) attempt. When the loop body was fixed on day 2, the base case wasn't updated to match.
- Same family as 1550-1600 #5 (mirror-case copy-paste, that one was self-caught). This one was NOT self-caught — took submission feedback.
- *Fix going forward:* when refactoring a recurrence, **re-derive base cases from scratch**. Do not copy them from the previous version.

**Bug 3: Misdiagnosed WA as overflow.**
- First instinct on 4th WA was "OF but I handled it carefully." Wasted time looking at long casts.
- Actual bug was logic in dp[1].
- *Fix going forward:* on WA, **trace the failing test case first**, then hypothesize. Don't guess bug family.

**Bug 4: Did not trace examples on any of 4 submissions.**
- Self-acknowledged: "should have ran through few test or edge cases my bad."
- LC samples would have caught dp[1] immediately: `nums=[10,5], colors=[1,1]` → expected 10, code returns 5.
- *Fix going forward:* 5-step ritual step 2 (trace 1-2 given examples) is mandatory. If skipped, log it explicitly as a ritual break.

---

### Verdict on the cold re-solve

The original May 8 entry called this "AC Y, 60min, integer overflow bug" — ambiguous whether it was WA-on-submit or caught pre-submit. Under today's strict rules, the cold re-solve was **WA-then-AC = soft fail**. Whatever the historical record said, the muscle isn't reflex.

Specifically: the DP recurrence muscle for "choose-or-skip with constraint" isn't fluent. The base case re-derivation reflex isn't installed. Both should be drillable.

**WA-cause [logic-recurrence]:** recurrence missing the "skip i" branch + base case left stale after refactor — untraced before submit.

---

### Lesson to install before next cold re-solve

**New rule (informally):** before submitting any DP solution, trace it on the **smallest non-trivial test case** mentally. For House Robber V that's `n=2, same color` — that case caught the dp[1] bug instantly when finally traced. For most DPs that's `n=1, n=2, n=3` with the constraint active.

This should be added to the pre-submit checklist in `LC/CLAUDE.md` as item 14.

---
