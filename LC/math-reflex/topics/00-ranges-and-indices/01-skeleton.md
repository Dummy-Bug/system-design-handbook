# Ranges & Indices [1100]

Counting integers in a range, locating boundary indices, and complement
arithmetic on contiguous selections. The pre-band anchor family — these never
appear as standalone problems but are SUB-OPERATIONS inside thousands of them.
If any takes more than ~5 seconds, that's a floor leak to fix before anything
else.

This is the home for the off-by-one / index-arithmetic reflexes that were
previously only documented in `math-band-1100-1399.md` §0 (analysis layer) with
no drill home. Promoting them into the topics layer so they enter spaced rep.

## Why this exists

Two concrete triggers, same root:
1. "Keep k of n contiguous items ⟹ kept window starts at index n−k" — 12 min on
   *Maximum Points From Cards* (1550-1600 Phase-2 #15, 2026-05-30).
2. The circular-window version of the same problem: "take k from the two ends" can
   be framed as a length-k window that wraps the array, anchored k-left of the last
   element. Locating "the index k units from the last" (= n−k) and the `% n` wrap
   ate most of the time.

Both are 30-second index facts. Same class as the original `n(n-1)/2` 20-minute
leak — sub-operations that must be reflex.

## Empirical frequency

Not separately tagged — these are sub-operations, not problem types. The
range-counting pain point is called out in `math-band-1100-1399.md` §0.1 as the
user's stated weak spot. Appears inside: every sliding-window problem, every
prefix-sum range query, every "first/last k" or "middle n−k" framing,
every "multiples in [L,R]" count.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content
unpacked via Socratic drill on install.

---

## a. Integer count in a range [1100]

**Cards (2):**
- a.1 — Closed `[a, b]` holds `b − a + 1` integers (both endpoints counted)
- a.2 — The endpoint rule: baseline `b − a`, `+1` per closed endpoint, `−1` per
  open endpoint → `(a,b]` and `[a,b)` give `b−a`; `(a,b)` gives `b−a−1`

**LC anchor:** *Count Odd Numbers in an Interval Range* (LC 1523)

---

## b. Multiples of d in a range [1200]

**Depends on:** Integer count in a range [1100]

**Cards (1):**
- b.1 — Multiples of d in `[L, R]` = `floor(R/d) − floor((L−1)/d)` — the
  `L−1` (not `L`) is the off-by-one that makes it count `[L,R]` not `(L,R]`

---

## c. Complement of a contiguous selection [1300]

The 12-minute-leak card. Selecting/dropping a contiguous block from n elements.

**Cards (2):**
- c.1 — Keep k contiguous items out of n ⟹ the other part has `n − k`; the
  0-indexed start of the last-k window is `n − k`
- c.2 — Boundary map: first k = indices `[0, k−1]`; last k = indices
  `[n−k, n−1]`; a kept length-m window starting at i = `[i, i+m−1]`

**LC anchor:** *Maximum Points You Can Obtain From Cards* (LC 1423)

---

## d. Window length ↔ endpoints [1300]

**Cards (1):**
- d.1 — A window `[i, j]` (inclusive) has length `j − i + 1`; given length m and
  start i, the end is `i + m − 1` — the same `+1`/`−1` off-by-one as a.1

---

## e. Circular / wraparound window indexing [1400]

The "take k from both ends" family. The math reflex is the *index arithmetic* of
the wrap — not the choice of algorithm (that's `patterns/`).

**Cards (3):**
- e.1 — Two equivalent framings, pick one and commit:
  (i) keep a length-k window that wraps the array (anchor at n−k, grow forward), or
  (ii) drop the contiguous length-(n−k) middle window (slide a fixed window).
  Thrashing between them mid-solve is the time sink — choosing up front is the skill.
- e.2 — Anchor index: "k units left of the last element" = `n − k` (0-indexed).
  The window's logical positions are n−k, n−k+1, …, n−k+(k−1), read physically as
  `arr[pos % n]`.
- e.3 — Wrap mechanics: forward access `arr[(start + t) % n]`; if a pointer ever
  decrements, use `arr[((idx % n) + n) % n]` (Java negative-mod trap).
  Cross-ref: Modular Arithmetic c.1 (single-index cyclic access) — same `% n`,
  this card is the *moving-window* version.

**LC anchor:** *Maximum Points You Can Obtain From Cards* (LC 1423)

---

## Card count

9 atomic cards across 5 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (2) = **2 cards** |
| 1200-1299     | + b (1) = **3 cards** |
| 1300-1399     | + c (2) + d (1) = **6 cards** |
| 1400-1499     | + e (3) = **9 cards (full)** |

## Notes for Socratic drill

- This whole topic is "floor anchors" — every card should fire in <5s or it's a
  contest time leak. Install all of them early; they unlock sub-steps everywhere.
- Subtopic `a` is the root: every other card is the same `+1`/`−1` endpoint
  logic in a different costume (multiples, complements, window lengths).
- Subtopic `c.1` is the freshly-diagnosed leak — drill it against the boundary
  map in c.2 so "first k / last k / middle" indices come out instantly.
- Subtopic `e` is the circular-window leak. The cards are deliberately about index
  arithmetic only (anchor = n−k, `% n` wrap). The leak wasn't "use a window" — it
  was thrashing between two framings and hunting the anchor index. e.1 forces the
  commit-up-front habit; e.2/e.3 make the index fire in <5s. The window *algorithm*
  still trains in zerotrac, not here.
- The *sliding-window* framing of LC 1423 (circular window) is NOT a card here —
  that's algorithmic muscle (zerotrac / `patterns/`). This topic owns only the bare
  index arithmetic.
- Cross-ref: prefix-sum range index (`pre[r+1] − pre[l]`) lives in Arithmetic
  Sums §1.5 — same off-by-one family, different home.
```
