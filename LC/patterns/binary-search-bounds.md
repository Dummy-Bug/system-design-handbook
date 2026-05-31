# Binary Search — bounds, floor, ceiling

## The one rule worth memorizing

> **lower_bound = `>=`, upper_bound = `>`.**
> They differ by exactly the **count of `x` in the array**:
> - count 0 (x absent) → `lower == upper` (they collapse to the insertion point)
> - count 1 (x present once) → differ by 1
> - count ≥2 (duplicates) → differ by the number of copies

The `>=`/`>` split only *matters* when `x` is present. Duplicates don't create the
gap — they widen it. (Common mistake: thinking it's a "duplicates only" thing.)

## It's not 4 concepts — it's 1 skeleton + 2 knobs

There's **one** operation: "first/last index where a comparison holds." Two binary knobs:

- **Side** — look *right* (smallest index that's big enough) vs look *left* (largest index that's small enough)
- **Strictness** — inclusive (`<=`,`>=`) vs strict (`<`,`>`)

2 × 2 = the four named queries. **All return an INDEX.** If you want the value, write `a[idx]`
(index-vs-value is a read-off, orthogonal to all four — floor/ceil are NOT "the value version").

```
index   0   1   2   3   4   5
value   1   3   3   3   5   7
```

| side  | strictness   | name                          | meaning (returns INDEX)        | x=3 | x=4 (absent) |
|-------|--------------|-------------------------------|--------------------------------|-----|--------------|
| right | inclusive >= | **ceiling** = **lower_bound** | smallest idx with `a[i] >= x`  | 1   | 4            |
| right | strict >     | **upper_bound** (strict ceil) | smallest idx with `a[i] >  x`  | 4   | 4            |
| left  | inclusive <= | **floor**                     | largest idx with `a[i] <= x`   | 3   | 3            |
| left  | strict <     | strict floor                  | largest idx with `a[i] <  x`   | 0   | 3            |

Key identities:
- **ceiling ≡ lower_bound** — same index, same `>=`. Two names for one query (one names the value, one the position).
- **upper_bound ≡ strict ceiling.**

## What happens when `x` is absent

`x=4` falls in the gap between `3` (idx 3) and `5` (idx 4):

- The **strictness knob stops mattering**: `lower_bound == upper_bound == 4`, and `floor == strict floor == 3`. No equal element to include/exclude → the inclusive/strict choice is moot.
- Both right-side queries → the **insertion point** (4). Both left-side queries → insertion point − 1 (3).

## The off-the-end guard (the real trap)

Every query returns an index that can be **−1** or **n**, meaning "no such element on that side":

| x              | lower_bound | ceiling value      | floor index | floor value        |
|----------------|-------------|--------------------|-------------|--------------------|
| `0` (below all)| 0           | `a[0]=1`           | **−1**      | **none** (nothing ≤ 0) |
| `100`(above all)| **6 (= n)** | **none** (off end) | 5           | `a[5]=7`           |

Always bounds-check before dereferencing `a[idx]`.

## Connection to LIS (patience / O(n log n))

The patience-sort update does a **lower_bound** (first `tails[idx] >= x`); the *value* it
overwrites is the **ceiling** of `x` — that's why it's called a "ceiling search."

- `>=` (lower_bound / ceiling) → **strict** LIS
- `>`  (upper_bound)          → **non-decreasing** LIS

One operator is the entire strict-vs-non-strict knob. See [[lis]] in `DP/lis.md`.
