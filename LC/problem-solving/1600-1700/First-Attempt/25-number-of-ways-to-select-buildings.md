# 25 — Number of Ways to Select Buildings

- **Link:** https://leetcode.com/problems/number-of-ways-to-select-buildings/ (LC 2222)
- **Dealt:** 2026-06-23 (replenishment deal #26)
- **Result:** ✅ **CLEAN first-submission AC, self-derived** (over/under-cap time not recorded)
- **Bucket (credit by our code):** **DP » String** (subsequence-count DP) → **0/2 → 1/2**
- **AR / slot:** ~50% / Q2

## Clean-status note
Early versions failed only on LC's **Run** sample tests (pre-submission dev feedback, same class as knight-dialer
#23) — **no WA submission**, **first Submit was the AC**, no hint (Claude stayed silent through the solve).
User framed it as plain "pick / non-pick DP," not consciously as "subsequence" — irrelevant: the mechanic in the
code is subsequence-count DP, credited by [[lc-classify-by-own-solution]]. → clean self-derived rep.

## The bug that was killed (memo-key discipline)
v2 cached on `dp[building][count][prev]` — **omitting `i`**. The subanswer depends on the **position**, and many
positions share the same `building` char, so the cache returned values computed at a *different* index → wrong.
Fix = `dp[i][count][prev]`.
> **Reflex:** the memo key must be exactly the arguments the answer depends on. `building = s.charAt(i)` is
> *derived from* `i` → redundant **given** `i`, never a **substitute for** `i`.
Other clean touches: `prev=2` sentinel for "none yet" (fits fixed `[3]` dim), `Long`/`null` instead of fill-`-1`.

```java
private long helper(int i, int prev, String s, int count) {
    if (count == 0) return 1L;
    if (i >= s.length()) return 0L;
    if (dp[i][count][prev] != null) return dp[i][count][prev];
    long skip = helper(i + 1, prev, s, count);
    long take = 0L;
    int building = s.charAt(i) - '0';
    if (prev == 2 || building != prev) take = helper(i + 1, building, s, count - 1);
    return dp[i][count][prev] = skip + take;
}
// call: helper(0, 2, s, 3);  dp = new Long[n][4][3]
```

## Step 2 / Step 3
- **Worked example:** binary alphabet + "no two adjacent picks equal" + length 3 ⇒ only `010`/`101` survive;
  `take` allowed iff `prev==2 || building!=prev`; `count==0` base returns 1 per completed alternation.
- **Edges:** `prev=2` sentinel (first pick, any char allowed); `count==0` returns before memo touch (index 0 unused);
  `i>=n` with `count>0` → 0 (ran out); `Long` to avoid overflow before the count can be large.

## Perturbation (debrief — OPEN, working Socratically in chat per [[lc-perturbation-before-write]])
Suspicious specifics to probe: the **3** (length), the **binary** alphabet, the **"adjacent in selection"** vs
"adjacent in string" constraint. First probe posed: *3 building types instead of 2* — general `helper` survives
(just widen `prev` sentinel), but the editorial's O(n) count-`0`s/`1`s-around-each-middle trick dies. → resolve
remaining probes in chat, then write conclusions here.

## Credit
DP » String **1/2** (2nd rep has **no clean in-band supply** → rolls cross-band per queue note, rule 6B).
Band clean-rate: **17/23**.
