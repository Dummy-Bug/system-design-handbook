# LC Training Log — 1600-1650 band — Second Attempt (Cold Re-solve)

**Why this exists:** Per audit on 2026-05-22, the original 1600-1650 run had 2 confirmed clean ACs (#4, #6), 3 WA-then-AC soft fails (#1, #2, #5), 1 hinted (#7), 1 ambiguous (#3), and skip-3 (only 7/10 done). Under tightened graduation rules in `LC/CLAUDE.md`, the band did not pass. This file logs the cold re-solve of all 7 problems plus 3 new ones on untouched patterns (monotonic stack, binary-search-on-answer, interval DP).

**Protocol per cold re-solve:**
- Close notes / `First-Attempt.md`. Blank file.
- Read problem fresh. Log thinking step by step (no hints from Claude).
- 5-step ritual must be visible in the log: constraint reading, example trace, edge cases, decomposition, code.
- First-submission AC = clean upgrade. WA-then-AC = soft fail (muscle isn't reflex).
- Debrief after AC (or stuck) — bugs, recurring patterns, lessons.

**Strict accounting target:** ≥7/10 first-submission AC, ≤1/10 hinted across the 10 problems logged here.

---

## 1 — House Robber V (cold re-solve, original was ambiguous-clean)

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

## 2 — Count Caesar Cipher Pairs (cold re-solve, original was clean May 11)

| Field | Value |
|-------|-------|
| Date | 2026-05-23 |
| Link | https://leetcode.com/problems/count-caesar-cipher-pairs/ |
| Rating | 1624 |
| AC | Y after 1 WA submit + 2 compile fixes |
| Time | ~50min total (20min on n(n-1)/2 derivation, 10min on mod-26 wraparound, rest on code) |
| Pattern | Caesar normalization (shift first char to 'a') + group-pair counting |
| Verdict | **Soft fail** (WA-then-AC) |

---

### 5-step ritual artifacts

- **Step 2 trace:** "cba" → first char shift = 2 → mod 26 → normalized = "azy". *Trace was incomplete — only covered normalization, not the full pipeline including pair counting.*
- **Step 3 edge cases:** same-char words (all reduce to "a..."), different word lengths (auto-handled by map key), n=1 (returns 0).
- **Step 3 gap:** did NOT enumerate the case `[same, same, same]` — exactly the case that broke pair counting.

---

### Approach (insight)

For each word: shift all chars so the first becomes 'a'. Same shift applied to all other chars (with mod 26 for wraparound). Group words by normalized form. Count pairs per group via n*(n-1)/2.

Two-pass version (the one that AC'd):
1. Build `Map<String, Long>` of normalized form → frequency.
2. Sum `freq * (freq-1) / 2` across all group sizes.

### Mod-26 wraparound

`normalized = (relativeValue - shift + 26) % 26`. The `+26` is needed because Java `%` preserves dividend sign — without it, negative shifts produce negative results.

### Bugs caught — root cause analysis

**Bug 1: Mixed delta and cumulative in pair counter (1 WA on submit).**

Original code computed `count = freq*(freq-1)/2` after incrementing freq, then `totalPairs += count` every iteration. For 3 identical words: `0 + 1 + 3 = 4`, expected `3`.

*Root cause:* mixed two accounting models. Either track delta per word (`totalPairs += freq - 1` after increment), OR compute once at end from final freqs. Original code did both.

*Pattern name:* **"delta vs cumulative"** — same family as the diff-array off-by-one at 1550-1600 #8. Whenever a running counter updates per iteration, ask: "am I adding the increment, or the total?"

*Fix:* two-pass refactor — build freq map fully, then compute pairs per group. Cleaner separation, no mixed accounting.

**WA-cause [logic-accounting]:** mixed delta and cumulative in the pair counter — partial trace missed the over-count.

---

## 3 — Split Array With Minimum Difference (cold re-solve)

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

## 4 — Minimum Discards to Balance Inventory (cold re-solve)

| Field | Value |
|-------|-------|
| Date | 2026-05-25 |
| Link | https://leetcode.com/problems/minimum-discards-to-balance-inventory/description/ |
| Rating | 1638 |
| Start | 12:23 |
| Note | re-solve of First-Attempt #4 (orig 60min) |

### Thinking log (verbatim)

**Step 1 — Constraints:** constraints allow up to n log n.

**Step 2 — Problem reading / disambiguation:** sample cases discard an item but feel incomplete — what if the same item appears again later with a count now below threshold? Re-read: the problem says discard an *item*, not discard an *occurrence* of an item. So once an item is discarded, all its later occurrences can be ignored — they don't contribute to the answer, it's already recorded on the first offense.

**Step 3 — Window-shrink question (self-generated edge case):** if an item is discarded, do we remove all its occurrences and shrink the window? Sample cases don't cover this. Test case: `w=5, m=2`, `[1,2,2,1,2,1]`. If discarding `2` (first offense) removes its occurrences, the window shrinks → the next `1` enters the window, its freq could exceed 2, and `1` also lands in the answer. Re-read to resolve:
- *"minimum number of arrivals to be discarded"* → we discard **arrivals**, not the whole item. So window size stays the same.
- the window represents the **last m days**, not a count of item-types kept. So if we discard on a day, nobody's count increases that day and we just shift the window right.
- this raised a worry: if we count discards for distinct arrivals, could the same item be discarded twice? Resolved by *"an item may only be discarded on its arrival day."* → once discarded (and recorded) earlier, that item can't be taken again, and the window-shrink confusion is gone — the window is the last m days regardless of what was kept.

**Step 3 (cont.) — traced answer:** for `[1,2,2,1,2,1]`, answer = 1 — from `2`'s freq exceeding the threshold; after that the window shifts right and the leftmost `1` falls out of the window.

**Step 4 — Approach (reduced form):** the whole problem reduces to a **fixed-size sliding window with counting**. Build the first window and check for discards; if an item is discarded, store it in a Set. For each next item, first check it's not already in the discarded-Set, then check its count and apply the if/else; once the window is full, keep shifting it, processing items, and eventually return the Set size. Also need a freq-count **map** alongside the Set.

**Step 4 — example/edge traces:**
- Both sample cases → working.
- `[1,1,1,1]`, m=1, w=2 → working.
- `[1]` → working.
- Max input `[10^5, …, 10^5]`: one element can hit 10^5 occurrences, m up to 10^5 — approach unchanged, already handled; no int overflow possible (counting only).

**Step 5 — First submission: WA.**

```java
public int minArrivalsToDiscard(int[] nums, int w, int m) {
    Map<Integer,Integer> map = new HashMap<>();
    Set<Integer> set = new HashSet<>();
    int n = nums.length, i = 0;
    for (int j = 0; j < n; j++) {
        int count = map.getOrDefault(nums[j], 0);
        if (count + 1 > m) {
            set.add(nums[j]);
        }
        map.put(nums[j], count + 1);
        if (j - i + 1 == w) {
            map.put(nums[i], map.get(nums[i]) - 1);
            i++;
        }
    }
    return set.size();
}
```

**Step 6 — WA diagnosis via failing case:** `[8,8,8,1,7,4,3,7,5,2]`, w=7, m=1 → my answer 2, expected 3. Re-read the statement: *"an item may only be discarded on its arrival day"* sounded like discard-the-item, but *"minimum number of arrivals to be discarded"* means discard-the-**arrival**. I'd coded the former; this case proves it's the latter. Same item can be discarded on multiple arrival days, so discards must be counted per-arrival-index, not per-item-value.

**Step 7 — Second submission: AC.** Two fixes from v1:
1. Track discards by **arrival index** (`set.add(j)`), not by item value (`set.add(nums[j])`).
2. A discarded arrival is **not kept**, so only increment the freq map in the `else` (kept) branch; and on window exit, only decrement if that index was kept (`if (!set.contains(i))`).

```java
public int minArrivalsToDiscard(int[] nums, int w, int m) {
    Map<Integer,Integer> map = new HashMap<>();
    Set<Integer> set = new HashSet<>();
    int n = nums.length, i = 0;
    for (int j = 0; j < n; j++) {
        int count = map.getOrDefault(nums[j], 0);
        if (count + 1 > m) {
            set.add(j);                       // count the arrival, not the item
        } else {
            map.put(nums[j], count + 1);      // only kept arrivals occupy a slot
        }
        if (j - i + 1 == w) {
            if (!set.contains(i)) {
                map.put(nums[i], map.get(nums[i]) - 1);
            }
            i++;
        }
    }
    return set.size();
}
```

### Outcome (Min Discards)

| Field | Value |
|-------|-------|
| Start → End | 12:23 → ~13:21 |
| Time | **58 min exact** (First-Attempt was 60 min — no speed gain on re-solve) |
| AC | Y after 1 WA |
| Verdict | **Soft fail** (WA-then-AC) |

**Root cause: problem-reading error (item vs arrival).** The entire WA was a misread of *what is being counted* — discard an *arrival/occurrence*, not a distinct *item*. This is a Step-1 ritual failure ("comprehend: what is input, output, the rule, in ONE sentence"). The one-sentence statement was wrong, so every downstream decision (`set.add(nums[j])`, unconditional count increment) inherited the error.

**WA-cause [read-error]:** misread the counted unit (item vs arrival) — wrong one-sentence rule, not an algorithm bug.

**Band tally:** 4/10 done. Clean first-submission AC: #3 only (#1, #2, #4 are WA-then-AC soft fails). Currently **1/4 clean** — below the ≥7/10 bar; the binding weakness so far is not algorithmic, it's **first submissions going out on a misread/untraced statement.**

---

## 5 — Minimum Cost Path With Alternating Directions II (cold re-solve)

| Field | Value |
|-------|-------|
| Date | 2026-05-25 |
| Link | https://leetcode.com/problems/minimum-cost-path-with-alternating-directions-ii/description/ |
| Rating | TBD |
| Start | 14:33 |

### Thinking log (verbatim)

**Step 1 — Constraints:** constraints allow an O(m·n) solution.

**Step 2 — Reading / approach scoping:** cost doesn't depend on the actual cell value, only on indices → a closed-form math solution might exist instead of normal DP. But constraints are fine, so grid DP works. Read the full problem before concluding: must **wait on even-numbered seconds and move on odd-numbered seconds**; entering any cell costs you (pay on entry). The **wait cost is given as an array** — that rules out a pure-math solution; DP it is.

**Step 2 (cont.) — tracing sample cases to nail the mechanics:** start at entrance (0,0) at second = 1 (odd). So at second 1 we entered cell (0,0) → pay the entry price, and then no wait needed? First sample is too small to disambiguate — moving on to the second example case to read the mechanics off it.

**Step 2 (cont.) — mechanics understood from the trace:** start at (0,0) at second=1 (odd) → no wait, move down or right. At second=2 we reach (0,1) or (1,0) → pay the wait cost in that cell, and since it's even we can't move, so we wait 1 second. Next second=3 (odd) → move again, then even, then odd, and so on. Net: **we pay a waiting cost at every cell except (0,0)** (we start there on an odd second).

**Step 3 — Approach (BUP chosen deliberately):** solving bottom-up because it's the harder way to implement and teaches 10x more than top-down.
- State: `f(i,j)` = minimum cost to reach cell (i,j).
- Recurrence (as written by user): `f(i,j) = f(i-1,j) + f(i,j-1) + waitCost[i][j] + getEntryCost()`.
- Base: `dp[0][0] = 1` stored directly; rest computed with their wait + entry costs.

**Step 3 (cont.) — edge case found:** at the last cell `i==m-1 && j==n-1`, do we still pay a wait? Checked the examples — none added a wait there. So **no waiting cost for (0,0) nor (m-1,n-1)**.

**Step 3 (cont.) — verification:** approach traced and working for example 1 and example 2.

**Step 3 (cont.) — edge cases:**
- min grid `m*n >= 2` → start and end cell are never the same (nice). Checked anyway: if they were equal, answer is always 1 regardless of wait cost.
- max value 10^5, `m*n <= 10^5`; worst case every wait cost = 10^5 → sum can overflow int → use **long** for the accumulation. Return type is also long.

**Step 3 (cont.) — revising after "incorrect" verdict:**
- BUP direction: moving only right/down means starting from (m-1,n-1) to reach (0,0), checking right/down on the way — but that's the same as checking left/up, so BUP direction is not the problem.
- The real issue: the entry pattern — "cannot use both" — but the recurrence had **both** wait and entry cost. Reworked: **only the starting cell pays entry cost.** After that you're constrained to wait on even seconds, so you always add the **wait cost** and move only on odd seconds — entry cost is *not* added again because the wait cost was already incurred.
- Boundary at (m-1,n-1): same pattern, lands on an even second → only the wait cost is incurred.
- Dry-ran on example cases + own cases → working perfectly.

**Time note — approach phase:** ~40 min elapsed at end of thinking, minus ~5 min spent typing thoughts into chat → **~35 min to derive the approach** (before coding).

**Step 5 — Coding revealed approach was wrong:** code fails the example test case. Investigating what's wrong (the dry-run "working perfectly" claim didn't hold once actually coded).

**Step 6 — Re-reading example 3 (`m=2,n=3, waitCost=[[6,1,4],[3,2,5]]` → 16):** the breakdown shows entry cost `(row+1)*(col+1)` is paid on entering each new cell, and wait cost is paid at each cell except the start and the final move. Corrected mental model: if at cell (i,j), you pay the **entry cost of the neighbor** you move into; you can only move on odd seconds (paying entry cost on the move); on reaching (i+1,j) or (i,j+1) the second flips to even → wait 1 sec, incurring that cell's **wait cost**; then it's odd again → move, and you again pay the **entry cost** of the next neighbor. So **both** entry cost (index-dependent, `(i+1)*(j+1)`) and wait cost are involved — the earlier "only start pays entry" model was wrong.

**Step 6 (cont.) — recurrence:** state unchanged. Whether you arrive from left or top doesn't matter since entry cost is `(i+1)*(j+1)` (direction-independent). So:
`f(i,j) = min(f(i-1,j), f(i,j-1)) + entryCost[i][j] + waitCost[i][j]` — recurrence comes out the same shape as before, just with the corrected per-cell entry cost.

**Step 7 — Final submitted code:**

```java
public long minCost(int m, int n, int[][] waitCost) {
    long[][] dp = new long[m][n];
    dp[0][0] = 1;
    for (int i = 1; i < m; i++)
        dp[i][0] = i + 1L + dp[i-1][0] + waitCost[i][0];
    for (int j = 1; j < n; j++)
        dp[0][j] = j + 1L + dp[0][j-1] + waitCost[0][j];
    for (int i = 1; i < m; i++)
        for (int j = 1; j < n; j++) {
            long cost = waitCost[i][j];
            long entryCost = ((long)i + 1) * (j + 1);
            dp[i][j] = Math.min(dp[i-1][j], dp[i][j-1]) + cost + entryCost;
        }
    return dp[m-1][n-1] - waitCost[m-1][n-1];   // destination pays no wait
}
```

Traced on example 3 → returns 16. ✓ (first/dp-col use `i+1L`/`j+1L` to dodge int overflow; final `- waitCost[m-1][n-1]` removes the wait wrongly added to the destination.)

### Outcome (Min Cost Path Alt Directions II)

| Field | Value |
|-------|-------|
| Start | 14:33 |
| Time | **80 min** |
| AC | Y (no judge WA — all misfires were caught pre-submit on the example) |
| Verdict | **Hinted** — see below |

**Why hinted, not clean:** the user asked "is my approach correct?" three times and Claude gave correctness verdicts (one **"Incorrect"** that redirected them off a wrong recurrence + double-cost model). That "Incorrect" was an external nudge before the right approach was reached → under the tightened rule this counts as **hinted**, not a clean self-derived AC. Logged honestly to avoid optimistic counting (header-integrity rule).

**The real bottleneck (and it is NOT DP):** the 80 min went almost entirely into *problem comprehension*, not algorithm. The approach was reworked twice — first the wait-vs-entry cost model, then realising entry cost is `(i+1)*(j+1)` per cell — both were **misreads of the cost mechanics**, same family as #4's item-vs-arrival read-error. Once the cost model was correct, the DP itself was a textbook min-grid recurrence written cleanly and AC'd first judge-submit.

**WA-cause [read-error]:** (pre-submit, not a judge WA) cost mechanics misread twice — what is paid, where, and that entry cost is index-dependent.

**Band tally:** 5/10 done. Clean first-submission AC: **#3 only**. #1/#2/#4 soft fail (WA-then-AC), #5 hinted. **1/5 clean, 1/5 hinted** — both below bar. Dominant failure mode across the band is now unmistakable: **problem comprehension**, not algorithm/derivation. Three of five problems lost their time to reading the statement wrong.

---

## 6 — Identify the Largest Outlier in an Array (cold re-solve, original #7 was hinted)

| Field | Value |
|-------|-------|
| Date | 2026-05-25 |
| Link | https://leetcode.com/problems/identify-the-largest-outlier-in-an-array/ |
| Rating | 1644 |
| AC | Insight reached (hinted) — implementation pending |
| Time | ~80 min total (41 min self-derivation before asking help, then ~40 min debrief + construction-by-forcing to internalize the edge case) |
| Pattern | Algebraic rearrangement + HashMap freq-count lookup |
| Verdict | **Hinted** (same recognition gap as first attempt — not a clean re-solve) |

---

### Thinking log (verbatim)

- Solved `2x + z = tSum → x = (tSum − z)/2`; noted sum is always even so odd `(tSum − z)` skips. Working on samples.
- Got hung up chasing a "multiple outliers" structural edge case for ~30 min. Tried to construct an array with two valid outliers; proved `2x + z = 3z ⇒ x = z` always, couldn't manufacture a contradiction. (This was a **red herring** — "largest" is in the prompt only because you enumerate valid candidates and take max, not because of an exotic structure.)
- At 41 min, stuck. Asked for help.

### The actual gap — recognition, NOT data-structure knowledge

The user **knows** set vs freq map cold. The miss was *seeing* that the value-based check (`is target present?`) can alias the **same physical index** as the candidate, under the prompt's `distinct indices, may share values` clause. Without seeing the collision, the freq map looks pointless — nothing to defend against. **Do not log this as a "used Set" knowledge slip** (this mislabel is what made it recur from attempt 1).

The collision fires exactly when `tSum = 3z` — and `z` here is the **loop candidate**, not the real outlier. `tSum = 3z` identifies *which single candidate self-collides* (it's the trap), not "three times the outlier." The real answer comes from a different candidate that never touches that equation.

### Breakthrough — constructing the killer array (the proof the collision is real)

The user could not believe the collision existed because they couldn't construct an array exhibiting it. Recipe derived together:
1. Pick the value you want as the **trap** (the fake candidate) → call it `z`. → chose `z = 7`.
2. `tSum` is then forced to `3z = 21`, and `7` must appear **exactly once**.
3. Plant a *real, different* outlier `o` (≠ 7). `tSum = 2s + o` ⇒ `s = (21 − o)/2` must be whole ⇒ `o` odd. → chose `o = 3`, so sum element `s = 9`.
4. The trap `7` must live among the **specials** (it's not 9, not 3); specials sum to 9 → `[7, 2]`.

```
[7, 2, 9, 3]   tSum = 21
z=7: x=(21-7)/2 = 7.  x==z, count[7]=1  → INVALID.  set false-positives → claims 7
z=3: x=(21-3)/2 = 9.  present, x≠z      → VALID, outlier 3  ✓
z=2: x=(21-2)/2 = 9.5 → skip
z=9: x=(21-9)/2 = 6.  absent           → invalid
```
Correct = **3**; naive set = `max(7,3)` = **7**. Building the array from the forcing equation IS the proof — and producing it on demand is the recognition the user was missing.

### Fix

Frequency map, with the self-collision guard:
```
if x == z:  need count[x] >= 2     // sum element & outlier same value → two distinct indices
else:       need count[x] >= 1
```
Iterate every element as candidate `z`, skip odd `tSum − z`, apply the rule, take max valid `z`. O(n) time, O(n) space.

### Verdict

**Hinted** — does not count as a clean re-solve of original #7. The same recognition gap recurred, confirming it was mislabeled the first time (as a Set-vs-Map slip). Now reframed as a recognition trigger and carded (deck Card 02). Re-test cold on a fresh value-check-under-index-constraint problem to confirm the trigger is reflexive before claiming this graduated.

**WA-cause [read-error]:** value-based validity check under an index-based constraint — `distinct indices, may share values` clause read past, never converted into "could my match alias my current index?".

**Band tally:** 6/10 done. Clean first-submission AC: **#3 only**. #1/#2/#4 soft fail, #5/#6 hinted. **1/6 clean, 2/6 hinted** — well below the ≥7 clean / ≤1 hinted bar. Comprehension/recognition remains the dominant failure mode (4 of 6 lost to reading, now including this one).

---

## 7 — Sum of Digit Differences of All Pairs (cold re-solve, original #6 was 55 min)

| Field | Value |
|-------|-------|
| Date | 2026-05-26 |
| Link | https://leetcode.com/problems/sum-of-digit-differences-of-all-pairs/ |
| Rating | ~1600 |
| AC | **Y — first submission, clean** |
| Time | **27 min end-to-end** (13 min approach + trace, rest coding) — First-Attempt was 55 min, **~2× faster** |
| Pattern | Per-digit-position contribution counting via freq map |
| Verdict | **Clean pass** (first-submission AC, self-derived, no hint) |

---

### Approach (insight)

`O(n²)` brute force is out (constraints). Key reframe: total = sum over **each digit position** of the number of pairs that *differ* at that position. Process one position at a time. Scanning left to right with a digit-frequency map, when you reach element `i`, `count` = earlier elements sharing this digit, so `(i+1) - (count+1) = i - count` = earlier elements that **differ** here. Accumulate across all `i` and all positions. `O(d·n)` time, `O(1)` space (≤10 digit buckets). Problem guarantees all numbers have equal digit length, so `digitCount` from `nums[0]` is safe.

### Step 2 / Step 3 (ritual)

Trace of `[13,23,12]→4` done on paper (not transcribed — logged as paper-only per the chat exchange). Edge cases named: all-identical (`[10,10,10,10]→0`), single number → 0 by definition.

### Review notes (no bug, but habit flags)

- **Float-cast trap [checklist #2], latent not live:** `(int)Math.pow(10, i)` for digit extraction. AC'd only because powers of 10 ≤10¹⁵ are exactly representable as doubles. Same shape as the `999`-instead-of-`1000` trap. Habit fix: integer-only digit peel (`n%10; n/=10`) or precomputed `int[] pow10`.
- **Intermediate-collection guideline:** `Map<Integer,Long>` over a fixed 0-9 digit range — an `int[10]`/`long[10]` is the natural fit (no boxing, `clear()` → `Arrays.fill`). Negligible at scale, noted for habit only.
- Clean otherwise: `getDigit` predicate extracted, no nested conditionals in main loop, orchestrator reads cleanly.

**Code:** `solutions/1600-1650/sum-of-digit-differences-of-all-pairs.java` (archive only — do NOT open during revision).

### Verdict

First clean self-derived first-submission AC of the band besides #3, and a genuine 2× speed drop (55→27) — this pattern **installed** on the first re-solve (contrast with the Outlier, whose subtle edge needed a card). No deck card: nothing cost real time.

**Band tally:** 7/10 done. Clean first-submission AC: **#3, #7**. #1/#2/#4 soft fail, #5/#6 hinted. **2/7 clean, 2/7 hinted** — still below the ≥7 clean / ≤1 hinted bar, but two cleans now and the dominant failure mode (comprehension) didn't bite here. 3 left: re-solve **Word Squares II** (orig 40 min) + 2 new on untouched patterns (monotonic stack / binary-search-on-answer / interval DP).

