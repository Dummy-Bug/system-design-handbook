# Ranges & Indices — notes

> Derived end-to-end in a Socratic session **2026-06-07** (a→f all self-derived). These
> are floor-anchors: each must fire in <5s or it's a contest time-leak. Read this to
> *re-derive*, never to memorize — the whole point is that a derived fact regenerates
> while a memorized string decays.

## The master lens: nodes vs edges

One idea unifies every card here. Lay the integers of `[a, b]` out like a graph:

```
3   4   5   6   7
 └─┘ └─┘ └─┘ └─┘     ← edges (gaps)
 ●   ●   ●   ●   ●    ← nodes (the integers)
```

`b − a` counts the **edges** (the jumps): `7 − 3 = 4`. But you almost always want the
**nodes** (the integers themselves): `5`. To span `k` nodes you cross `k − 1` edges — so
nodes = edges + 1. **That `+1` is the single most common off-by-one in the whole topic,**
and every card below is this same node/edge bookkeeping in a different costume. (User's own
framing: it's exactly nodes-vs-edges in a tree/graph.)

---

## a. Integer count in a range

Closed `[a, b]` holds `b − a + 1` integers. The `+1` converts edges→nodes (both endpoints
included). Forgetting it is the classic "I miscounted by one" bug.

**Open/closed endpoints** — derive from the lens, don't memorize a table: start from the
full-closed node count `b − a + 1`, then **drop one node per *open* endpoint**:

| range | open ends | count |
|---|---|---|
| `[a, b]` | 0 | `b − a + 1` |
| `[a, b)` or `(a, b]` | 1 | `b − a` |
| `(a, b)` | 2 | `b − a − 1` |

---

## b. Multiples of `d` in a range — and the L−1 trap

You can't use the contiguous node/edge count here, because multiples of `d` aren't
contiguous — they're spaced `d` apart. The right building block is the **prefix count**:
"multiples of `d` in `[1, N]` = `floor(N/d)`". Then subtract:

```
multiples of d in [L, R] = floor(R/d) − floor((L−1)/d)
```

**The trap (fall into it once so it sticks):** the natural instinct `floor(R/d) − floor(L/d)`
is *wrong*. On `[6, 12], d=3` the true count is `6, 9, 12 → 3`, but `floor(12/3) − floor(6/3)
= 4 − 2 = 2`. Using `L` subtracts away the multiple sitting *on* `L` (the 6). You want to
remove everything **strictly below** `L`, i.e. up to `L − 1`: `floor(5/3) = 1`, `4 − 1 = 3` ✓.

The `L − 1` is the **same left-boundary-inclusion decision as card `a`** — "do I keep the left
endpoint?" Every off-by-one in this topic is a left-boundary question. Write it
`floor((L−1)/d)` *with parens* — `floor(L − 1/d)` parses as `L − (1/d)`, a different, wrong
thing. In an off-by-one topic the parens *are* the correctness.

---

## c. First-k / last-k / window span — the length formula is the one true tool

The reliable, never-fails tool is the **length formula** `b − a + 1 = count` (it's just card
`a` solved for an endpoint). Everything else is a precomputed shortcut of it:

| Want | Span | from `b − a + 1 = count` |
|---|---|---|
| first `k` | `[0, k − 1]` | start 0, length `k` (no `n` needed) |
| last `k` | `[n − k, n − 1]` | end `n−1`, length `k` |
| window length `m` from `i` | `[i, i + m − 1]` | start `i`, length `m` |
| leftover / complement of a kept block | size `n − k` | total − kept |

**Why `last k` starts at `n − k` (the cancellation worth seeing):** build the start honestly
as "last index, then step back to cover `k` items." The last index is `n − 1` (n items, but
0-indexed, so the last is `n−1`). To cover `k` items you step back `k − 1` (nodes/edges again:
`k` nodes span `k−1` edges). So `start = (n−1) − (k−1) = n − k` — **the two `−1`s cancel.** The
clean `n − k` isn't ignoring the `k−1`; it's its simplified form.

**The double-correction warning:** don't apply the inclusive `+1` *and* the `k−1`. Inclusivity
gets handled exactly once. Two equivalent derivations, each handling it once:
- step-back framing: `(n−1) − (k−1) = n − k`  (uses `k−1`, no `+1`)
- length framing: `(n−1) − k + 1 = n − k`  (uses `k`, has the `+1`)

Mixing them — `(n−1) − (k−1) + 1` — corrects twice and drifts to the wrong index. Rule of
thumb: when you **count**, edges→nodes needs `+1`; when you **locate a start by stepping**, the
`k−1` already *is* the `+1`.

---

## d. Window length ↔ endpoints

Nothing new — this *is* the length formula from `c`: a window `[i, j]` (inclusive) has length
`j − i + 1`; given start `i` and length `m`, the end is `i + m − 1`. Already owned the moment
`c` was.

---

## e. Circular / wraparound window — the Max-Points-From-Cards reflex

**The 12-minute leak, and its actual cause.** *Maximum Points You Can Obtain From Cards (LC
1423):* take exactly `k` cards, each from one of the two **ends** of the row, maximize their
sum.

The leak was **not** the algorithm — it was **thrashing between two framings**:

- **(messy) window of the cards you TAKE** — size `k`, but it *wraps* (some from the right end,
  some from the left), so it needs `%n` and a start that dips below 0. "Tricky and messy" — the
  exact words, and the exact symptom.
- **(clean) window of the cards you LEAVE** — whatever split you take from the ends, the
  untouched cards are always **one contiguous block of size `n − k` in the middle**. No wrap, no
  mod, plain fixed-size window `[i, i + (n−k) − 1]`.

So the solution falls out: maximize what you take ⟺ **minimize what you leave** ⟺

```
answer = total − (minimum-sum contiguous window of size n − k)
```

**The reflex to install:** see *"take `k` from both ends"* → **immediately** reframe as
*"min-sum contiguous window of size `n − k`."* Commit to the complement up front. The skill
isn't the sliding window — it's refusing to fight the wrapping framing.

**Index facts of the genuinely-circular case** (when you *do* need a wrap, e.g. cyclic array
access): the last `k` window logical positions are `n−k … n−1`, read physically as
`arr[pos % n]`; if a pointer ever decrements use `arr[((idx % n) + n) % n]` (Java negative-mod
trap). But for problems with a complement, prefer the complement and avoid all of this.

---

## f. Ceiling / block-count division

**Trigger:** "min count of size-`k` blocks to cover `T`" (the last block may hang over). E.g.
cover `T=7` with size-`k=3` blocks → `3` blocks (`3+3+1`). Plain `7/3 = 2` strands a unit.

**Derive it (full blocks + a correction):**

```
ceil(T/k) = T/k + (T%k != 0 ? 1 : 0)      // parens required: + binds tighter than ?:
```

`T/k` is the full blocks; you need **one** more block iff anything is stranded. **The bug to
avoid (hit it once):** don't add the *remainder* — `T/k + T%k` over-counts (`8/3 + 8%3 = 2+2 =
4`, but `8` needs only `3` blocks). A leftover of *any* size needs exactly **one** extra block,
because one block of size `k` mops up to `k` stranded units.

**The canonical one-liner:**

```
ceil(T/k) = (T + k − 1) / k        // integer-only
```

Why it works: adding `k − 1` is the *largest* nudge that still leaves exact multiples alone. If
`T % k == 0`, `k−1 < k` can't reach the next multiple → quotient unchanged. If `T % k ≥ 1`, the
nudge pushes past the next multiple → `+1`, and never `+2` (because `k−1 < k`). Mnemonic:
**"round up = pre-pay almost a full block (`k−1`), then floor."**

**Integer-safe — avoid `Math.ceil`.** `(int)Math.ceil(T/(double)k)` works but invites the
float-precision trap near `10⁹` (the only reason Biweekly 184's code survived was a `double`
cast). The integer `(T + k − 1)/k` has no float at all.

**Regenerate, don't memorize.** If the one-liner slips, fall back to `T/k + (T%k!=0?1:0)` — its
logic ("full blocks + 1 if leftover") is unforgettable, and you can rebuild the one-liner from
it in seconds. That regeneration ability is what this session bought.

**Anchor:** Biweekly 184 Q2 — cover `brightness` with bulbs of reach 3 → `ceil(brightness/3) =
(brightness + 2)/3`. Cross-ref: parity `oddCount(k) = (k+1)/2` is the `k=2` special case.

---

## Two meta-lessons (the load-bearing takeaways)

1. **`e` — commit to the easy framing up front.** When a problem has a complement, the
   complement is usually the non-wrapping, no-mod view. Thrashing between framings *is* the time
   sink; the algorithm rarely is.
2. **`f` — regenerate over memorize.** A derived fact (full-blocks + correction) survives months;
   a memorized magic string (`(T+k−1)/k`) decays. Own the derivation and the string is free.
