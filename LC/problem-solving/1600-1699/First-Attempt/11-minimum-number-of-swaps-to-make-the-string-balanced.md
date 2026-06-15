# 11 — Minimum Number of Swaps to Make the String Balanced

- **Link:** https://leetcode.com/problems/minimum-number-of-swaps-to-make-the-string-balanced/
- **Band:** 1600–1699 · sealed queue · blind deal #11 · Q3 (AR 78.1%) · **Stack / Reframe ✦** (Set B — reframe/derivation)
- **Bucket:** answer key = **Stack ✦ Reframe**. OUR code = a single-pass **balance counter** (stack collapsed to one int) + a greedy `⌈k/2⌉` close. Mechanic = bracket-matching counter + greedy rate argument. Greedy is already OWNED ●, Stack is a blind-spot-adjacent reframe → tracked under [[lc-invariant-reframe-bucket]], not a clean-gated rep here anyway (see Result).
- **Dealt:** 2026-06-12
- **AC:** 2026-06-12 (**33m OVER-CAP**, **EDITORIAL-level help**, first submission AC)
- **Result:** ❌ **HARD FAIL — editorial, NOT just a hint.** Stuck ~30m, then was **walked through essentially the whole approach across several turns**: the noise-removal reduction, the `]]]…[[[` canonical leftover, the per-swap-kills-2 greedy argument, AND the final `⌈count/2⌉` formula confirmed. This is well past a "directional nudge" — it's an editorial. Per **rule 6C / rule 3**, AC-after-editorial = fail → **no ownership credit**. Implementation was trivial (3m once the idea was handed over); the 30m of genuine cold work produced *nothing*. **Net new debt closed: ZERO.** Clean-rate now **8/10 (80%)**; clean streak BROKEN at 7 (#03–#09).

---

## The problem
String `s` of even length `n`, exactly `n/2` `'['` and `n/2` `']'`. One operation = swap the characters at any two indices (any positions, not adjacent). Return the **minimum number of swaps** to make `s` balanced (every prefix has `#'[' ≥ #']'` and it's a valid bracket string).

## Approach (HINTED) — reduce to the irreducible core, then greedy rate
- **Noise removal (THE step I missed cold):** any already-matched `[...]` pair contributes nothing to the answer. Cancel them all. Track with one counter `open` = openers currently waiting:
  - `'['` → `open++` (an opener now waits).
  - `']'` with `open > 0` → pairs/cancels → `open--`.
  - `']'` with `open == 0` → **stranded** (`count++`); nothing to its left can ever match it.
- **Canonical leftover shape:** after cancellation the string is always `]]]…[[[` — `count` stranded closers followed by `count` un-paired openers (equal by the equal-count guarantee). One variable `k = count` fully describes the residual problem.
- **Per-operation rate (greedy):** one swap takes the **outermost** stranded `]` and the **outermost** un-paired `[` and swaps them → the two ends self-cancel, killing **2** strays per swap. So `k` strays / 2 per swap = `⌈k/2⌉`. The `ceil` = the last lonely stray still costs a full swap. Greedy is valid because each swap independently grabs the 2 best targets — no coupling.
- **Closed form:** `(count + 1) / 2` (integer division) `= ⌈count/2⌉`.

## Where the 33m went (the honest post-mortem)
- **0–30m:** simulated swaps, tried to track positions, tried two-pointer on the raw string — never asked *"what part of the input is noise?"* The whole block was the missing **reduction** instinct. Produced **nothing usable** cold.
- **editorial-level help (NOT a one-line nudge):** got walked through, across turns, the reduction ("cancel matched pairs"), the canonical leftover shape `]]]…[[[`, the per-swap-kills-2 greedy rate, and the `⌈k/2⌉` formula was confirmed. The "self-derived rest" was minimal — most of the chain was handed over.
- **30–33m:** coded the (now fully-explained) idea in ~3m.
- **Diagnosis:** failure to *fire the reduction question cold*, then the gap got papered over with too much help instead of a single nudge. Exactly the [[lc-derivation-budget-chunking]] thesis — the novel assembly is tiny once "throw away matched pairs" fires; the rep is worthless because I didn't fire it and then didn't get the chance to (the whole approach was spelled out). **Owes a clean cold re-solve.**

## Step 2 — worked example reproduced
`s = "]]][[["` (already the canonical worst case). Walk with `open`, `count`:

| char | open before | branch | open after | count |
|---|---|---|---|---|
| `]` | 0 | open==0 → stranded | 0 | 1 |
| `]` | 0 | open==0 → stranded | 0 | 2 |
| `]` | 0 | open==0 → stranded | 0 | 3 |
| `[` | 0 | opener waits | 1 | 3 |
| `[` | 1 | opener waits | 2 | 3 |
| `[` | 2 | opener waits | 3 | 3 |

`count = 3` → `(3+1)/2 = 2`. Check by hand: `]]][[[` —swap ends→ `[]][]` …→ balanced in **2** swaps. ✅

Second example `s = "][]["` → `]`(stranded,count1) `[`(open1) `]`(open→0, cancels) `[`(open1) → `count=1` → `(1+1)/2 = 1`. One swap of the two ends → `[][]`. ✅
Already-balanced `s = "[[[]]]"` → all cancel, `count=0` → `0`. ✅

## Step 3 — named edge cases
1. **Already balanced** (`[[]]`, `[][]`) → `count=0` → `0` swaps. The `(0+1)/2 = 0` handles it.
2. **Fully reversed** (`]]][[[`) → `count = n/2` → `⌈(n/2)/2⌉`, the maximum.
3. **Odd stray count** (`count` odd, e.g. `count=3`) → `ceil` matters: `(3+1)/2 = 2`, NOT `1`. Plain `count/2` would under-count.
4. **`open` must not leak into the answer** — only `count` (stranded closers) drives it; `open` is just the matcher.
5. **Single pair `"[]"` / `"]["`** → `[]`→0, `][`→ count1 → 1. Smallest non-trivial cases.

## As-submitted solution (AC — but hinted)
```java
class Solution {
    public int minSwaps(String s) {
        int count = 0;
        int open = 0;
        for (char ch : s.toCharArray()) {
            if (ch == '[') {
                open++;
            } else if (open == 0) {
                count++;       // stranded closer
            } else {
                open--;        // cancels a waiting opener
            }
        }
        return (count + 1) / 2;   // ⌈count/2⌉
    }
}
```
Already canonical — one pass, O(n) time, O(1) space, no allocation beyond `toCharArray`. Nothing to collapse on revision; the *idea* is the lesson, not the code.

## Bucket accounting
| Bucket | Used? | Load-bearing? | Credit |
|---|---|---|---|
| Greedy (per-op rate `⌈k/2⌉`) | yes | yes | already OWNED ● — ride-along, no new counter |
| Stack/balance-counter (reduction) | yes | yes | the reframe; **HINTED → not credited** |
| Invariant/Reframe | yes | yes | tracked for revision sweep [[lc-invariant-reframe-bucket]], never gates graduation |

**No ownership counter moves** — hinted solve. Recorded for the *lesson*, not the rep.

## Lesson — the transferable interrogation (this is the real takeaway)
For the family **{string/array + an operation + "minimum number of moves"}**, fire three questions COLD, in order:
1. **"What part of the input is noise?"** — delete anything that can't change the answer (here: already-matched pairs). Highest-value move; this is the one I failed to fire.
2. **"What's the reduced shape?"** — after stripping noise the core usually collapses to ONE canonical form describable by a single variable (here `]]]…[[[`, variable `k`). If many shapes remain, reduce more.
3. **"What's the best a single operation buys?"** — make it a *rate*. One swap kills 2 strays → `⌈k/2⌉`. This rate question is the engine behind nearly every "minimum operations" problem; greedy is justified when moves don't couple.
> Mnemonic: **noise → reduced shape → per-op rate.** I had steps 2 and 3 in me instantly once step 1 was handed over. The grind target is making step 1 reflexive.

## Perturbation debrief — DONE 2026-06-12 (one keeper; the rest was a tangent, trimmed)

**Keeper meta-pattern:** *a suspiciously clean closed-form answer (like `⌈k/2⌉`) usually hides a "the operation is free / unconstrained" assumption — here, "a swap has zero distance cost." When you spot such a formula, the natural perturbation is "what if the operation has a cost?"* (Confirmed: restricting to adjacent-only swaps breaks `⌈k/2⌉` entirely — it becomes an inversion/displacement count. Detail not banked; it's an above-band cousin.)

**Calibration note for future debriefs:** point the perturbation at the axis where the solve actually *broke*. #11 broke on *recognising the reduction*, not on the formula's assumptions — so the operation-cost probe was tangential here. Better probe would've drilled the reflex I missed ("what other 'minimum operations' problems open with a noise-cancellation reduction?").

## PENDING
- **Day+14 revision (owed cold re-solve, rule 2: editorial ⇒ cold re-solve [[lc-cold-resolve-scope]]):** re-derive COLD; the rep only counts if the **reduction question — "what part of the input is noise?" — fires WITHOUT help this time.** This was an editorial-level fail; the entire value is making step-1 (cancel matched pairs) reflexive.
