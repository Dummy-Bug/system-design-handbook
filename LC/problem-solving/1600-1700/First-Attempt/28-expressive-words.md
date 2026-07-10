# 28 — Expressive Words

- **Link:** https://leetcode.com/problems/expressive-words/ (LC 809)
- **Dealt:** 2026-06-25 (replenishment deal #29)
- **Result:** ⚠️❌ **WA-then-AC (soft fail), 44m OVER-CAP → NO REP**
- **Bucket (target):** **Two-Pointers** → stays **0/2**
- **AR / slot:** ~46% / Q2

## Clean-status note
44 min (over the 30-cap — derivation clause exempts *time*, not implementation). First submit **WA on 1 case**
(34/36), fixed, resubmit AC → **WA-then-AC = soft fail**, no rep. **Two-Pointers stays 0/2** (still 0 clean reps:
#03 over-model, #17 TreeMap-greedy, #24 WA+reframe, now #29 WA). A 44m WA-then-AC is also a Q2 miss in a real
contest [[lc-contest-bottleneck-q2-speed]].

## The approach (run-length two-pointer, correct shape)
Group both strings into runs `(char, count)` via `getCount`. Walk run-by-run with two pointers (`i` over `s`,
`j` over `word`). For aligned runs of the **same char** with counts `c1` (in `s`), `c2` (in `word`):
- `c2 > c1` → word has more than s, can't shrink → **invalid**.
- `c1 > c2 && c1 < 3` → s stretched but final group `< 3`, illegal stretch → **invalid**.
- else → matchable; advance `i += c1`, `j += c2`.
Accept iff **both** strings fully consumed.

## WA-cause [incomplete-validation] — only one endpoint checked
**The bug = the accept condition checked the s-side exhausted but not the word-side.**
- **v1 (WA):** `if (sb.toString().equals(s)) count++;`
- **v2 (AC):** `if ((j == n2) && sb.toString().equals(s)) count++;`  ← added `j == n2`

Failing case `s = "heeellooo", word = "heeelloooworld"` (expected 0, v1 gave 1):
the loop `while (i < n1 && j < n2)` exits as soon as **either** pointer maxes. It matched `h,eee,ll,ooo`,
`i` hit `n1=9` → loop exits on the `i` condition while `j` still had `"world"` left. `sb.equals(s)` was true
(s-side fully built) so v1 counted it — but `word` had **unmatched trailing groups**. Adding `j == n2` asserts
the word side also ran out. **Both endpoints must exhaust.**

## Recurring pattern — same miss as #24 move-pieces
Identical family: validating **one** direction silently lets the **other** carry extras. #24 matched
`target→start` but never checked every START piece was consumed (dangling `L`); here `sb.equals(s)` confirmed
s was built but not that `word` was finished. **Counter-habit:** when two sequences must correspond 1-1,
the accept test is "**both** ran out together," never just one side. (Mirror of the move-pieces fix
`while(j<n) if(start[j]!='_') return false;`.)

## Step 2 / Step 3
- **Worked example (the WA case):** `s="heeellooo"` groups `h1 e3 l2 o3`; `word="heeelloooworld"` groups
  `h1 e3 l2 o3 w1 o1 r1 l1 d1`. After `o3`, `i=n1` but `j` points at `w` → word not exhausted → **0**. ✓
- **Edges:** word longer than s (trailing groups — the WA); s longer than word (s leftover, `sb!=s`);
  `c1 > c2` but `c1 < 3` (illegal stretch, e.g. `s="aa",word="a"` → 0); `c2 > c1` (word bigger → invalid);
  exact equal groups (`c1==c2`, valid passthrough); char mismatch caught by `sb.equals(s)`.

## Canonical (the clean accept test)
Track only counts and require both pointers to finish:
```java
boolean ok = (i == n1 && j == n2);   // both sequences exhausted — the load-bearing check
```
(`sb.equals(s)` also works because it can only be true when `i==n1` AND every char matched, but the explicit
`i==n1 && j==n2` makes the "both exhaust" invariant obvious and drops the StringBuilder entirely.)

## Credit
Two-Pointers **stays 0/2** (WA-then-AC). Band clean-rate: **17/25** (non-clean solve). Retire from queue; do not re-deal.
