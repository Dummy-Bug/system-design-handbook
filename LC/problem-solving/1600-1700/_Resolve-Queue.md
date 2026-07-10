# 1600-1699 — Re-Solve Queue (flow-fix validation)

**Created 2026-06-26.** Built after the folder-wide audit found we keep *solving* non-clean and never
*learning* from it: the cold re-solve (rule 2) was silently dropped after `1600-1650-Old` (the only band
with a `Second-Attempt/`), and the same 4 bug-families recur across bands while their counter-habits sit
scattered across 28 First-Attempt logs, never consolidated.

## What this queue is — and is NOT
- **IS:** the *validation harness* for the flow-fix. Phase A promoted the recurring families to the
  pre-submit checklist (`extendedClaude.md` items 14-16 + the minimal-tool prompt). These re-solves **test
  whether that fix holds.** Clean first-try = habit installed; still buggy = that checklist line isn't
  reflexive yet → more drilling.
- **IS NOT:** ownership progress. **Rule 6 gives NO rep for re-solving an already-AC'd problem** (even an
  editorial one). Two-Pointers (0/2), Stack (0/2), DP-Linear (1/2), DP-String (1/2-rolls), Mono-Stack (1/2)
  **still need FRESH picks** after the flow is fixed. This queue does not move the graduation needle — it
  stops the band from bleeding clean-rate.

## How to run it
- **Track 1 (snippet drills):** re-write *only the relevant function* cold, then run the mapped checklist
  item against your own code — did you avoid the family this time? ~5-10 min each. Do NOT re-read the
  First-Attempt log first (that's fluency-illusion [[lc-retrieval-not-reread]]); attempt cold, then check.
- **Track 2 (whole-problem cold re-derive):** blank file, full 30-min cap, no notes. These were never owned
  (editorial/hinted/Socratic) so "recall" = recalling the editorial = memorization. Re-*derive*. If you
  can't, that's a real signal, not a timing miss.
- Re-solve logs land in **`1600-1700/Second-Attempt/`** (restoring the dropped structure). Tag each
  `**Re-solve [clean | family-recurred]:**` so we can grep whether the flow-fix is working.

---

## Track 1 — snippet micro-drills (you HAD the approach, botched execution)

| # | Problem | Family / tag | Checklist item | Drill = avoid this cold |
|---|---------|--------------|----------------|--------------------------|
| 24 | move-pieces-to-obtain-a-string | `[incomplete-validation]` | **15** | accept test must assert BOTH endpoints exhaust (dangling `L`) |
| 28 | expressive-words | `[incomplete-validation]` | **15** | same — `j == n2` too (trailing `"world"`) |
| 27 | count-ways-to-build-good-strings | `[stale-memo]` + `[mod-underflow]` | **16, 14** | INVOKE `helper(low-1)` not `dp[low-1]`; `((a-b)%M+M)%M` |
| 29 | construct-smallest-number-from-di-string | `[stale-default]` | **16** | guard the flush; `int j=0` default fired on empty stack |
| 12 | minimum-seconds-to-make-mountain-height-zero | `[stale-derived-field]` | **16** | carry the cumulative incrementally, don't desync from its count |
| 02 | count-number-of-ways-to-place-houses | `[overflow]` | **14** | mod INSIDE the loop, not just at the end |

**Cross-band reps (stale-read family is thin in-band → 2 representatives):**
| Band | Problem | Family | Checklist item |
|------|---------|--------|----------------|
| 1500-1550 #10 | boats-to-save-people | `[stale-read]` | 16 |
| 1550-1600 #12 | groups-of-special-equivalent-strings | `[stale-read]` | 16 |

> overflow & incomplete-validation already have ≥2 in-band instances; over-model is covered in Track 2.
> No need to widen further — scope is current-band + still-recurring-family reps only.

---

## Track 2 — whole-problem cold re-derive (you NEVER owned it)

| # | Problem | Why non-clean | Bucket (no rep on re-solve) | Special constraint |
|---|---------|---------------|------------------------------|--------------------|
| 11 | minimum-swaps-to-make-string-balanced | editorial (hard fail) | Stack | derive the `⌈count/2⌉` greedy cold |
| 21 | flip-string-to-monotone-increasing | editorial | DP-String | derive the prefix-DP cold |
| 15 | count-number-of-bad-pairs | hinted (count-complement) | Hashing | reach "count NOT-bad pairs" yourself |
| 18 | apply-bitwise-ops-to-make-strings-equal | hinted (invariant) | Invariant/Reframe | find the single global property |
| 26 | car-fleet | Socratic (whole approach) | over-model | **NO Map/stack** — running-max scan, 1 var |
| 02 | count-number-of-ways-to-place-houses | hinted derivation (axis-switch) | DP-Linear | derive the per-side-then-square framing cold |

**Over-model no-Map drills (these ACed CLEAN but dodged the target mechanic — drill the modeling reflex):**
| # | Problem | Dodged | Constraint |
|---|---------|--------|------------|
| 03 | push-dominoes | two-pointer | no `Map<char,index>` — gap-sweep / two passes |
| 17 | advantage-shuffle | two-pointer | (TreeMap-greedy works, but) try the sort + two-pointer |
| 19 | maximum-width-ramp | monotonic-stack | no sort + `Map<value,Deque>` — the actual mono-stack |

> Run #19 + #11 with the minimal-tool prompt live — they're the closest things to the Stack / Mono-Stack
> blind-spots, so a clean *fresh* version later (different problem) is what actually closes those buckets.

---

## Order
1. **Track 1 first** (fast, builds the pre-submit reflex the checklist now names).
2. **Track 2 next** (the cold re-derivations — slower, higher derivation value).
3. **Then** the overdue Jun 10-15 revision batch (rule 5), **then** resume forward motion with fresh
   mechanic-matched picks for the open buckets.

**Validation metric:** of the Track-1 drills, what fraction come out clean first-try? That number — not the
backlog count — tells us whether the generator is fixed.
