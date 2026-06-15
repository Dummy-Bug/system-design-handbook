# Stack Atom 09 — Monotonic candidate stack: farthest / widest pair ★

*2026-06-15*

> Sibling of Atom 06 (monotonic, **nearest**). Same "drop dominated elements" engine, opposite goal: the **farthest** partner / **widest** pair, optimized globally — not a per-element nearest answer.

## The problem (Maximum Width Ramp, LC 962)

A *ramp* is a pair `(i, j)` with `i < j` and `nums[i] <= nums[j]`; its width is `j - i`. Return the **maximum** ramp width (0 if none). `[6,0,8,2,1,5]` → `4` (ramp `(1,5)`: `0 <= 5`). `n <= 5·10^4`.

## ① Trigger

You want the **maximum width / distance / span of a pair `(i, j)`** satisfying an **order condition** (`nums[i] <= nums[j]`, or `>=`, …) — one *global* widest pair, NOT "for each element, its nearest X." Brute force is all O(n²) pairs. Signal phrase: *"farthest / widest two indices such that <monotone relation between their values>."* Contrast Atom 06, whose signal is *"for every element, the **nearest** greater/smaller."* **Nearest → 06; farthest/widest → here.**

## ② Motivation — why a candidate stack (break the simpler tools)

- **Brute O(n²):** every pair. Dies at `n = 5·10⁴`.
- **Sort O(n log n):** sort indices by value (ties by index), sweep tracking the min index seen → `width = i - minIndex`. *Works* (this is the index-sort solution actually submitted on #19) but the `log n` is pure overhead and it hides the structure.
- **Break it → O(n):** which left endpoints can EVER be the optimal `i`? If an earlier `a < b` has `nums[a] <= nums[b]`, then `a` **dominates** `b` — for any `j` that `b` pairs with, `a` pairs too (`nums[a] <= nums[b] <= nums[j]`) **and is wider** (`a < b`). So `b` is dead weight. Useful left endpoints therefore have **strictly decreasing values as index increases** → a monotonic stack, built in O(n).

## ③ The move

**Two passes. Name the invariant first** (like Atom 06):

**Pass 1 — build candidate stack (L→R).** Stack holds indices of strictly-decreasing values (bottom = index 0 = largest value; top = smallest value). Push `i` iff stack empty or `nums[i] < nums[top]`. *Push = a new lower left-endpoint bar; skip = dominated by an earlier candidate.*

**Pass 2 — harvest farthest partners (sweep R→L).** For `j` from `n-1` down: while stack non-empty and `nums[top] <= nums[j]`, pop and `maxWidth = max(maxWidth, j - popped)`. *Pop = this candidate just met its **farthest** right endpoint (`j` is the largest it'll ever see, since we sweep from the right) → retire it.*

```java
Deque<Integer> st = new ArrayDeque<>();
for (int i = 0; i < n; i++)
    if (st.isEmpty() || nums[i] < nums[st.peek()]) st.push(i);   // strictly-decreasing candidates
int maxWidth = 0;
for (int j = n - 1; j >= 0; j--)
    while (!st.isEmpty() && nums[st.peek()] <= nums[j])
        maxWidth = Math.max(maxWidth, j - st.pop());             // retire candidate with its farthest j
return maxWidth;
```

**Why R→L is mandatory:** you want each candidate's **largest** `j`. Sweeping from the right, the first `j` that satisfies a candidate IS its largest → pop immediately, never revisit. (L→R would find the *nearest* `j` — wrong goal.)

## ④ Costumes (one knob each)

| Knob | Ramp cell | turn it |
|---|---|---|
| order relation | `nums[i] <= nums[j]` (non-strict) | strict `<`, or `>=` for a "descending" span — flip the build AND pop comparisons together |
| read on pop | **width** `j - i` | accumulate / count instead |
| sweep end | from the **right** (farthest right partner) | mirror for "farthest left partner" |

## ⑤ Confusion matrix

| Confused with | Discriminator |
|---|---|
| **Atom 06 (monotonic, nearest)** | 06 answers *"for each element, the **nearest** greater/smaller"* in **one pass** — pop = resolve/discard a dominated element, peek = read an answer. Here the goal is **one global widest pair**: **two passes** (build candidates, then reverse-sweep), and pop = "this candidate found its **farthest** partner, retire it." Nearest + per-element + 1-pass → 06; farthest + global + 2-pass → 09. |
| **Atom 07 (min/max stack)** | 07 keeps a running min/max beside pushes for O(1) extreme queries; no candidate domination, no width objective. |

## ⑥ Reflex check

Prompt: *max width / span of a pair `(i,j)` under an order condition — move?*
Answer: *monotonic **candidate** stack, two passes. Pass 1 (L→R): keep only non-dominated left endpoints (strictly decreasing values) — an earlier index with a ≤ value dominates a later larger one. Pass 2: sweep from the FAR end, pop while the top satisfies the order condition, record `farEnd - popped` — popping at the far end gives each candidate its widest partner. O(n).*

**Status:** installed 2026-06-15 via Maximum Width Ramp (LC 962), **Socratically led → acquisition, NOT a self-derived rep.** Mono-Stack blind-spot stays **1/2**; the 2nd clean rep comes from a *fresh* problem (carried #9 max-chunks) where this reflex must fire **cold**.
