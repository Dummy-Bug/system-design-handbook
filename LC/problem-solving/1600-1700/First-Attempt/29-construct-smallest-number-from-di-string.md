# 29 — Construct Smallest Number From DI String

- **Link:** https://leetcode.com/problems/construct-smallest-number-from-di-string/ (LC 2375)
- **Dealt:** 2026-06-25 (replenishment deal #30) · solved morning 2026-06-26
- **Result:** ❌ **Socratic walk-through (rule given) + WA-then-AC → NO REP**
- **Bucket (target):** **Stack** → stays **0/2**
- **AR / slot:** ~76% / Q3 (rating 1641, WC 306 Q3)

## Clean-status note
Two independent rep-killers: (1) stuck >30m on 2026-06-25, the block-reversal **rule was taught Socratically**
(I gave the DDI→3214 / IDD→1432 insight, user didn't self-derive it); (2) the morning first submission was a
**WA** (trailing-flush bug below), fixed on 2nd attempt → WA-then-AC. Either alone forfeits the rep.
**Stack stays 0/2** — still owes 2 fresh self-derived clean reps. Band clean-rate: **17/26** (non-clean).

## The insight (greedy construction, O(n) / O(1) extra)
Start from the sorted ascending string `1 2 3 … n+1` (already satisfies all-`I`). Then **reverse each maximal
run of `D`s**: a run of `k` consecutive `D`s spans `k+1` slots; reversing that block makes those slots strictly
decreasing while keeping every digit as small as possible (we never borrow a digit from later than the block).
The ascending base guarantees lexicographically smallest; local reversal is the minimal edit to honor each `D`-run.

- `DDI` → base `1234`, reverse [0,2] → `3214`
- `IDD` → base `1234`, reverse [1,3] → `1432`
- `DDID` → base `12345`, reverse [0,2] then [3,4] → `32154`

## WA-cause [stale-default] — trailing flush fired on an empty stack
First submission stored each D-index on a stack and flushed the run on every `I`; a final flush after the loop
handled a **trailing** D-run. Bug = the flush ran unconditionally:
```java
int j = 0;                       // ← default 0 is the trap
while (!stack.isEmpty()) j = stack.pop();
reverse(ans, j, n);              // executes even when stack was empty
```
When the pattern **ends in `I`**, the stack is already empty after the loop, `j` keeps its default `0`, and
`reverse(ans, 0, n)` reverses the **whole array** for no reason. It "worked" mentally only because the cases
hand-traced (`ID`, `IDD`) all end in `D`, where a pop sets `j` correctly.
- Failing case `"DI"`: loop builds `213` correctly, then the spurious `reverse(0,2)` → `312` (exp `213`).
- **Fix attempt 2:** `int j = -1; … if (j != -1) reverse(ans, j, n);` — guard the flush. AC.
- **Canonical (attempt 3):** drop the stack entirely, track the run start in one var (`prevD`) or look ahead
  with an inner `while`. No trailing-flush special case to forget.

## Step 2 / Step 3
- **Worked example:** `DDID` → `12345` → rev[0,2]=`321`·`45` → rev[3,4] → `32154`. ✓
- **Edges:** pattern ends in `I` (the WA — empty trailing stack); pattern ends in `D` (real trailing run must
  flush); all `I` (output = base, no reversal); all `D` (one big reverse → `n+1 … 1`); lone `I` between D-runs
  (zero-width reverse, must still step the pointer forward — the `Math.max(j, i+1)` / `prevD=-1` reset).

## Mis-pick note (same disease as #27 car-fleet)
Queue tagged this **Stack** ("push `1..9`, pop run on each `I`"), but the honest optimal solution is **greedy
block-reversal** — the stack is incidental and collapses to "reverse the block." So even a clean solo AC here
would credit Greedy/construction, **not Stack**. Stack's queue picks keep being mechanic-mismatches
[[lc-buckets-are-accounting-not-solving]] — Stack (0/2) needs **2 fresh non-queue picks** with a load-bearing stack.

## Canonical (cleanest, [[lc-revise-to-cleanest-form]])
```java
public String smallestNumber(String pattern) {
    int n = pattern.length();
    char[] res = new char[n + 1];
    for (int i = 0; i <= n; i++) res[i] = (char) ('1' + i);
    int i = 0;
    while (i < n) {
        int j = i;
        while (j < n && pattern.charAt(j) == 'D') j++;   // grab whole D-run
        reverse(res, i, j);
        i = Math.max(j, i + 1);                          // jump past run, or step over lone I
    }
    return new String(res);
}
```

## Credit
Stack **stays 0/2** (rule taught + WA-then-AC). Band clean-rate: **17/26**. Retire from queue; do not re-deal.
