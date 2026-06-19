# Module 4 — OR / AND over subarrays

> The **monotonicity** corner of the bit family. One property does all the work: as a subarray grows, its
> **OR only gains bits (non-decreasing)** and its **AND only loses bits (non-increasing)**. Two consequences fall
> out — (a) OR/AND-vs-threshold is *monotone in window length* (⇒ sliding window / two-pointer), and (b) for a fixed
> endpoint the running OR/AND takes **≤ 31 distinct values** (⇒ LogTrick over all subarrays). The mechanical catch:
> OR and AND are **not invertible** — you can't "un-OR" the element leaving a window — so windowed OR/AND needs a
> per-column bit-count, not a single accumulator.

## Atoms (derivation order)

| # | Atom | Core idea | Classic |
|---|------|-----------|---------|
| 4.1 | **OR/AND window monotonicity** (the foundational property) | extend window → OR is non-decreasing, AND is non-increasing (bits are one-way: OR only turns on, AND only turns off) ⇒ threshold tests are monotone in length, and #distinct values per endpoint ≤ 31 | LC 201 (Range Bitwise AND → common prefix) |
| 4.2 | **bit-count-in-window** (sliding window; OR/AND aren't invertible) | can't subtract a leaving element from an OR/AND, so keep **31 column counters**; bit ∈ window-OR iff `count>0`, bit ∈ window-AND iff `count == len`; add on expand, decrement on shrink | LC 3097 (Shortest Subarray With OR ≥ K II) |
| 4.3 | **no-shared-bits window** | longest subarray whose elements are pairwise bit-disjoint ⟺ maintain running OR `mask`; on new `x`, while `mask & x` shrink from left | LC 2401 (Longest Nice Subarray) |
| 4.4 | **LogTrick** (distinct OR/AND over ALL subarrays) | fix right end `r`: the multiset `{ f(l..r) : l ≤ r }` has **≤ 31 distinct values**; carry that frontier set forward, fold the new element into each (OR/AND in place), dedup → O(n·31) over all subarrays | LC 898 (ORs of Subarrays) + LC 1521 (AND closest to target) |

## Discriminator (where this sits in the bit confusion matrix)
This is the **"exploiting OR/AND monotonicity over a subarray"** corner. Felt-signal: *"the problem is about the
OR or AND of a **contiguous range/subarray**, with a threshold (≥K / =K / closest-to-target) or a 'count distinct
OR values' ask."* Two forks:
- **One window, threshold monotone in length** (longest/shortest subarray s.t. OR/AND meets a bound) → **sliding
  window + 31 column counters** (4.2 / 4.3).
- **All subarrays, aggregate over OR/AND values** (count distinct, value closest to target, sum) → **LogTrick**,
  the ≤31-frontier trick (4.4).

Contrast with the other corners: this is *not* cancellation (XOR/Module 2) and *not* per-pair column-summing
(Module 3) — here the columns give a **monotone/bounded structure along the array index**, which is what we exploit.

## Transfer payload — the bit-count-in-window invariant (4.2)
Maintain `int[] cnt = new int[31]` over the current window `[l..r]`, `len = r-l+1`:

| Operation | Update |
|---|---|
| expand `r` (add `x`) | for each set bit `b` of `x`: `cnt[b]++` |
| shrink `l` (remove `x`) | for each set bit `b` of `x`: `cnt[b]--` |
| reconstruct **OR** | bit `b` set iff `cnt[b] > 0` |
| reconstruct **AND** | bit `b` set iff `cnt[b] == len` |

> The reflex is the *reason* you keep counters: **OR/AND have no inverse**, so a single accumulator can't track a
> shrinking window — only a per-column tally can. Re-derive the table from that sentence.

## LogTrick skeleton (4.4)
```
prev = set/list of distinct values of f(l..r-1)   // ≤ 31 entries
cur  = {}                                          // distinct values of f(l..r)
add a[r] to cur
for v in prev:  add (v OP a[r]) to cur             // OP = | or &
prev = cur                                         // carry forward; consume cur for the answer
```
Each value can only change ≤ 31 times as `l` moves (one bit flip per change) ⇒ total work O(n·31).

## Install loop (per atom)
Socratic derivation → notes written **only after** deriving (`02-notes.md`) → blind classic to verify mapping.
Holdout = a blind 1700-1800 sealed-queue problem mapped < 30 min self-derived = installed; else not.

## Status
◑ **MODULE 4 — IN PROGRESS.** Notes in `02-notes.md`. Problems deferred → holdout queue (below).
- 4.1 OR/AND window monotonicity — ✅ (2026-06-19) — property (OR↑/AND↓, irreversible) + common-prefix rule + shift code; LC 201 solved (1 WA: bit-isolation overcount, fixed).
- 4.2 bit-count-in-window — ◑ derived (2026-06-19), holdout-pending.
- 4.3 no-shared-bits window — ◑ derived-with-help (2026-06-19), holdout-pending (understood, not cold; trace caught a careless bit-drop).
- 4.4 LogTrick (distinct OR/AND over all subarrays) — ◑ derived-with-help (2026-06-19), holdout-pending.

**All four derivations COMPLETE (2026-06-19).** Remaining Module-4 work = the deferred problem block only.

## Holdout queue (deferred problems — atom flips ◑→✅ only when driven cold)
| Atom | Install (in-band) | Stretch holdout | Verified rating |
|------|-------------------|-----------------|-----------------|
| 4.2 | LC 3095 (OR≥K I, ~1370) | LC 3097 (OR≥K II) | 3097 = **1891** |
| 4.3 | LC 2401 (Longest Nice Subarray) | — | 2401 = **1750** |
| 4.4 | LC 898 (ORs of Subarrays) | LC 1521 (AND closest to target) | (verify at solve time) |

## Carries inherited (from Module 3 — fold in or schedule at this module's revision)
Not Module-4 atoms; parked here so they aren't lost (full context in `../03-per-bit-properties/00-syllabus.md`):
1. **3.2 Smallest-XOR** — 2nd cold rep owed.
2. **LC 421** Max XOR pair (greedy-MSB + prefix-set/trie).
3. **LC 1835** XOR of all pair-ANDs; **LC 1442** count triplets equal XOR, O(n) clean.
