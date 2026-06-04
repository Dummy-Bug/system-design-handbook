# Atom 02 — Same-direction two pointers (single array)

**Tier 1 (Pointers)**
*Derived Socratically 2026-06-03.*

## ① Trigger (the felt signal)
You must build a **valid prefix in place** in one pass — compact / dedup / filter an array, overwriting it — and you reach for a second array but aren't allowed one.

## ② The atom (derived)
Two pointers, both starting left, both moving **forward** (contrast #1 which converges):
- **`read` (fast)** — advances on **every** element, exactly once. Touches all `n`.
- **`write` (slow)** — trails behind marking the boundary of the region being built; advances **only on a qualifying element**.

The asymmetry IS the atom:
> A fast read head scans all n; a slow write head only advances when the current element qualifies.

**Invariant:** `nums[0..write)` is always the completed valid answer so far. Everything `< write` is done & correct; everything between `write` and `read` is junk being overwritten.

## ③ Two costumes derived (proves what varies vs what's fixed)
**Costume A — Remove Duplicates from Sorted Array** (overwrite):
`[1,1,2,2,2,3]` → front `[1,2,3]`, return `i+1=3`. Qualify = `nums[read] ≠ last written`. Action = `i++; nums[i]=nums[read]`.

**Costume B — Move Zeroes** (swap, unsorted):
`[0,1,0,3,12]` → `[1,3,12,0,0]`. Qualify = `nums[read] ≠ 0`. Action = `swap(nums[write++], nums[read])`.
```java
int w = 0;
for (int r = 0; r < n; r++)
    if (nums[r] != 0) swap(nums, w++, r);   // w==r early on → harmless no-op, self-positions
```

**What changes problem-to-problem:** only the **qualify condition** and the **action** (overwrite vs swap). The skeleton is fixed.

## ④ The sortedness insight (the sharp bit)
The **atom never needs a sorted array.** Sortedness was a crutch the *dedup problem* leaned on: when sorted, duplicates are adjacent, so "is this new?" = one cheap compare to the previous value. Unsorted (`[1,3,1]`) breaks that compare → you'd need a hashset. So:
> **Sortedness lives in the qualify condition, not in the atom.** Move Zeroes needs none.

## ⑤ Confusion matrix
| Confused with | Discriminator |
|---|---|
| #1 opposite-end | Both sweep **forward** building a prefix (this) vs **converge** from both ends. |
| Sliding window (#8) | A single write boundary (this) vs a **window [lo,hi] with a shrink rule** and a quantity over the window's contents. |
| #3 two-ptr over two sequences | **One** array, read/write asymmetry (this) vs **two** inputs, two read heads, no write head. |

## ⑥ Scope note
This atom = **single array, read/write, build a prefix.** The "two pointers over two sequences" shape (Is Subsequence / merge / backspace-compare) is a **separate atom #3** — different invariant, no write head. Split decided 2026-06-03.

## ⑦ Reflex check
**Prompt:** "Compact/filter an array in place, one pass — move?"
**Answer:** "Read head over all n; write head trails, advances only on a qualifying element. `nums[0..write)` is the built region. Qualify+action is the only thing that changes."

## ⑧ Status
Mechanic ✓ + 2 costumes ✓ (overwrite & swap) + sortedness-distinction ✓. **Single-array facet = covered.** A 3rd single-array rep would be redundant. Owned = drill slot (<5s, 3-day hold).
