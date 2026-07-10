# 24 — Move Pieces to Obtain a String

- **Link:** https://leetcode.com/problems/move-pieces-to-obtain-a-string/ (LC 2337)
- **Dealt:** 2026-06-23 (replenishment deal #25)
- **Result:** ⚠️❌ **WA-then-AC (soft fail) + reframe given earlier → NO REP**
- **Bucket (target):** **Two-Pointers** → stays **0/2**
- **AR / slot:** 54.6% / Q2

## Clean-status note
Two strikes against a rep: (1) I gave the two-pointer reframe before the solve (help → not self-derived);
(2) v1 was a WA, v2 the AC → **WA-then-AC = soft fail** even setting the help aside. Two-Pointers **stays 0/2**;
needs 2 fresh self-derived picks (#29 expressive-words is the next two-ptr shot).

## WA-cause [incomplete-validation]
v1 walked `target`→`start` matching every target piece to a start piece with the right letter/order/position,
but **never checked that every START piece got consumed.** On
`start="_L__R__R_L"`, `target="L______RR_"` start has 4 pieces (L,R,R,L), target 3 (L,R,R) — the dangling
`L@9` in start was never reached by the hunt loop, so counts matched and v1 returned `true` (expected `false`).
**v2 fix:** trailing `while (j<n){ if (start.charAt(j)!='_') return false; }` sweeps the tail and catches the
leftover piece. The two strings must be the **same multiset of pieces in the same order** — checking one
direction silently allows the other to carry extras.

## Canonical (the clean two-pointer form — makes the bug impossible)
Walk BOTH pointers over non-blank chars simultaneously; the **end-symmetry** (both must exhaust) is exactly
what v1 lacked:
```java
int i = 0, j = 0, n = start.length();
while (i < n || j < n) {
    while (i < n && start.charAt(i) == '_') i++;
    while (j < n && target.charAt(j) == '_') j++;
    if (i == n || j == n) return i == n && j == n;   // both must run out together
    if (start.charAt(i) != target.charAt(j)) return false;  // same piece, same order
    char c = start.charAt(i);
    if (c == 'L' && i < j) return false;   // L moves left only  ⇒ start idx ≥ target idx
    if (c == 'R' && i > j) return false;   // R moves right only ⇒ start idx ≤ target idx
    i++; j++;
}
return true;
```

## Step 2 / Step 3
- **Worked example:** `start=_L__R__R_L`, `target=L______RR_` → pieces start[L,R,R,L] vs target[L,R,R] → 4≠3,
  symmetry check fails → `false` ✓ (the exact WA case v1 missed).
- **Edges:** different piece **counts** (the v1 killer); same counts but **order** differs (L/R swapped) →
  letter-mismatch returns false; an `L` that would need to move **right** (`i<j`); leading/trailing blanks;
  all blanks both → true.

## Meta-finding (saved as memory [[lc-buckets-are-accounting-not-solving]])
User noted a **queue** solution exists but he didn't consider it "because Queue isn't a tracked bucket." That's
a blind-deal leak — solving toward the ledger, mirror of the over-model habit [[lc-index-bookkeeping-overmodel]].
The queue form is the SAME mechanic (two queues of piece-positions polled in lockstep) → still the Two-Pointers
rep, not a "Queue" rep → suppressing it cost a real derivation for zero algorithmic gain. Buckets are post-hoc
accounting; keep them out of the head mid-solve.

## Credit
Two-Pointers **stays 0/2** (help + WA-then-AC). Band clean-rate: **16/22** (this counts as a non-clean solve).
