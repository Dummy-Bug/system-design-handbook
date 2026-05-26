# Count Caesar Cipher Pairs (cold re-solve, original was clean May 11) — Second Attempt (Cold Re-solve)

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
