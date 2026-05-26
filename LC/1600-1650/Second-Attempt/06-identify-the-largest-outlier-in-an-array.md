# Identify the Largest Outlier in an Array (cold re-solve, original #7 was hinted) — Second Attempt (Cold Re-solve)

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
