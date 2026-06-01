### #30 — Count Collisions on a Road

**Link:** https://leetcode.com/problems/count-collisions-on-a-road/
**Date attempted:** 2026-06-01
**Rating:** 1550–1600 band (Phase 2 — sealed queue, deal-list #3)
**Resolved at:** 2026-06-01 _(editorial / Socratic walkthrough after 3 WAs)_
**Time:** ~1h 2m to the 3 WAs, then editorial.
**Status:** ❌ **EDITORIAL-RESOLVED (3 WA). HARD FAIL — does NOT count toward ownership.** (3 self-derived WA attempts, then hint/editorial.)
**Pattern (debrief):** **Stack** (Q2, AR 58.1%) — but really an **insight-gated brain-teaser**.
Credits two buckets: `Stack` (the filed mechanism) **+ `Invariant/Reframe` ✦** (the non-standard
cross-cutting derivation axis — [[lc-invariant-reframe-bucket]]). This is the **seed member** of that bucket.

---

## Why it was hard (the real lesson)

All 3 WAs were **simulation attempts** — tracking who hits whom, chains converting to `S`, etc.
That is exactly the trap. The problem is not a Stack-mechanics problem; the Stack tag is almost a
red herring. The win is an **invariant reframe**: *don't simulate the process — find a quantity that's
additive and count it directly.* That reframe is the transferable skill; the specific observation is
disposable. (See the `Invariant/Reframe` bucket rationale in `patterns/master-taxonomy.md`.)

---

## Attempt 1 (WA) — next-L/S/R lookup arrays + last-seen tracking

Built suffix arrays `s[i]/l[i]/r[i]` = next index of each type, plus `lastS/L/R` running indices,
then case-analysed per car. Too much bookkeeping; wrong on the collision accounting.

```java
class Solution {
    public int countCollisions(String directions) {
        int n = directions.length();
        int [] s = new int[n];
        int [] l = new int[n];
        int [] r = new int[n];
        s[n-1] = n; l[n-1] = n; r[n-1] = n;
        if (directions.charAt(n-1) == 'L') l[n-1] = n - 1;
        else if (directions.charAt(n-1) == 'S') s[n-1] = n - 1;
        else r[n-1] = n - 1;
        for (int i = n - 2; i >= 0; i--){
            char c = directions.charAt(i);
            if (c == 'L'){ l[i] = i; s[i] = s[i+1]; r[i] = r[i+1]; }
            else if (c == 'S'){ s[i] = i; l[i] = l[i+1]; r[i] = r[i+1]; }
            else { r[i] = i; s[i] = s[i+1]; l[i] = l[i+1]; }
        }
        int count = 0, lastSIndex = -1, lastLIndex = -1, lastRIndex = -1;
        if (directions.charAt(0) == 'S') lastSIndex = 0;
        else if (directions.charAt(0) == 'R') lastRIndex = 0;
        else lastLIndex = 0;
        for (int i = 0; i < n; i++){
            char c = directions.charAt(i);
            if (c == 'R'){
                int sIndex = s[i], lIndex = l[i];
                if (sIndex == n && lIndex == n) continue;
                else if (sIndex < lIndex) count = count + 1;
                else count = count + 2;
            } else if (c == 'S'){
                int lIndex = l[i], rIndex = r[i];
                if (rIndex <= lIndex) continue;
                else count = count + 1;
            } else {
                if (lastLIndex > lastSIndex && lastLIndex > lastRIndex){
                    if (lastRIndex > lastSIndex) count = count + 2;
                    else if (lastSIndex > lastRIndex) count = count + 1;
                }
            }
            if (c == 'S') lastSIndex = i;
            else if (c == 'R') lastRIndex = i;
            else lastLIndex = i;
        }
        return count;
    }
}
```

## Attempt 2 (WA) — L-chain precompute + R-chain sweep

`lChain[i]` = length of L-run starting at `i`; sweep adding `length*2` for an `R` and
`length + rChain` for an `S`. **WA on `"LLRLRLLSLRLLSLSSSS"` → got 12, expected 10.**

```java
class Solution {
    public int countCollisions(String directions) {
        int n = directions.length();
        int [] lChain = new int [n];
        if (directions.charAt(n-1) == 'L') lChain[n-1] = 1;
        for (int i = n-2; i >= 0; i--){
            if (directions.charAt(i) == 'L') lChain[i] = 1 + lChain[i + 1];
        }
        int rChain = 0, count = 0;
        for (int i = 0; i < n - 1; i++){
            char c = directions.charAt(i);
            int length = lChain[i + 1];
            if (c == 'R'){ count = count + length*2; rChain++; continue; }
            else if (c == 'S'){ count = count + length; count = count + rChain; }
            rChain = 0;
        }
        return count;
    }
}
```

## Attempt 3 (WA) — patched Attempt 1 (edge guards + debug prints)

Added an `i==0 && c!='R'` skip and recomputed the R case off `r[i+1]`. Still WA. After this the
user pulled the LC hint; even the hint didn't land, so we walked it Socratically.

**WA-cause [wrong-model]:** all three tried to *simulate* collisions and chain-conversions to `S`.
The double-counting the user self-diagnosed ("once a collision happens, moving cars become S — I
didn't account for that") is an artifact of simulating; it vanishes entirely under the invariant view.

---

## The resolution — three views of one idea

### View A — closed-form invariant (THE ONE TO OWN)

Reframe the scoring: **in every collision, the score added = the number of cars that newly come to
rest.** (Head-on `R`+`L` stops 2 cars, scores 2. Moving car into a parked car stops 1, scores 1.)
A car comes to rest at most once → **total score = number of moving cars that ever stop.**
A moving car escapes (never stops) iff it's in the **leading run of `L`'s** or the **trailing run of `R`'s**.

> **answer = (#L + #R) − (leading L's) − (trailing R's)**
> i.e. chop leading `L`'s and trailing `R`'s, count the `L`/`R` that remain.

Check `LLRLRLLSLRLLSLSSSS`: chop 2 leading L's, 0 trailing R's (ends in `S`), 10 L/R remain → **10** ✓.

```java
class Solution {
    public int countCollisions(String directions) {
        String s = directions;
        int i = 0, n = s.length();
        while (i < n && s.charAt(i) == 'L') i++;          // skip leading L run (escapes left)
        int j = n - 1;
        while (j >= 0 && s.charAt(j) == 'R') j--;          // skip trailing R run (escapes right)
        int count = 0;
        for (int k = i; k <= j; k++) if (s.charAt(k) != 'S') count++;  // every L/R left is doomed
        return count;
    }
}
```

### View B — stack simulation (the "Stack" tag; backup recognition only)

Stack holds "things to my left I might interact with": `R` = pending right-mover, `S` = permanent
wall. Each car that stops does `count++` — same invariant, paid one pop at a time.

```java
class Solution {
    public int countCollisions(String directions) {
        Deque<Character> st = new ArrayDeque<>();
        int count = 0;
        for (char c : directions.toCharArray()) {
            if (c == 'R') st.push('R');
            else if (c == 'S') {
                while (!st.isEmpty() && st.peek() == 'R') { st.pop(); count++; }
                st.push('S');
            } else { // 'L'
                if (st.isEmpty()) continue;               // leading L escapes
                count++;                                   // the L stops
                while (!st.isEmpty() && st.peek() == 'R') { st.pop(); count++; }
                st.push('S');
            }
        }
        return count;
    }
}
```

### View C — O(1) flag (the stack collapsed; just know it exists)

The stack is only ever `[maybe one wall S][run of R's]`, so track one number `flag`:
`-1` = empty/escaped, `0` = wall present no pending R's, `k>0` = k pending R's.
`res += flag + 1` on an `L` = "the L stops (+1) and these flag R's stop (+flag)".

```java
class Solution {
    public int countCollisions(String directions) {
        int res = 0, flag = -1;
        for (char c : directions.toCharArray()) {
            if (c == 'L') { if (flag >= 0) { res += flag + 1; flag = 0; } }
            else if (c == 'S') { if (flag > 0) res += flag; flag = 0; }
            else { flag = (flag >= 0) ? flag + 1 : 1; }
        }
        return res;
    }
}
```

---

**Which to own:** View A (closed-form invariant). Know View B exists (the "Stack" classification);
ignore View C beyond "it's the stack collapsed."

**Invariant/Reframe deck entry:**
- **Trap:** simulate the cars, track chain-conversions to `S` → double-counting (all 3 WAs died here).
- **Reframe:** every car that stops = +1 → answer = moving cars − (leading L run) − (trailing R run).

> **⏳ REVISION TARGET:** re-derive View A cold — the scoring reframe ("score = cars newly at rest")
> and the escape condition (leading-L / trailing-R). Do NOT reproduce any simulation.
