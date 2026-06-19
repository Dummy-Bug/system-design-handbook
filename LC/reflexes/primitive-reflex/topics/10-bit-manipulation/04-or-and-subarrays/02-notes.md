# Module 4 — OR / AND over subarrays (notes)

> **STATUS (2026-06-19):** 4.1 (range AND → common prefix) ✅ owned (coded). 4.2 bit-count-in-window ◑ derived,
> holdout-pending (LC 3095 install / LC 3097-II stretch queued). 4.3 no-shared-bits window ◑ derived-with-help,
> holdout-pending (LC 2401 queued — *understood, not yet derived cold*; one trace already caught a careless
> bit-drop). 4.4 LogTrick ◑ derived-with-help, holdout-pending (LC 898 / 1521 queued). **All four atoms derived;
> Module 4 derivations COMPLETE — only the deferred problem block remains.**
>
> **Problems deferred by design:** all classics parked in the holdout queue; concepts derived first, problem block
> after the module. An atom flips ◑→✅ only when the user drives its classic cold ([[lc-retrieval-not-reread]]).

## 1. AND / OR over a contiguous integer range — the common-prefix reflex (LC 201)

**Setup.** Asked for `m & (m+1) & … & n` (or the OR) over a **contiguous range of integers**. Naive = loop every
number `m..n` and fold. At `n` up to ~10⁹ with `n − m` up to ~10⁹ that's ~10⁹ iterations → TLE. So the loop has to go.

**The property (the foundation of the whole module).** As a window/range grows, bits move **one way only**:
- **OR** can only turn bits **on** → OR is **non-decreasing**.
- **AND** can only turn bits **off** → AND is **non-increasing**.
- Neither is reversible inside the running fold (you can't "un-OR" or "un-AND" a value).

**The move (for the range AND).** Stack `m` and `n` in binary and read left→right. They share a top **prefix**, then
at some column first **differ**. The answer is: **keep the matching prefix, zero out that differing bit and
everything below it.**

```
m = 1 0 1 0   (10)
n = 1 1 1 1   (15)
    │ │
   same  ← first differ at this column → kill it + everything to the right
answer = 1 0 0 0   (8)
```

**Why everything below the first differing bit dies.** If `m` and `n` differ at bit `k`, then climbing from `m` to
`n` you must flip bit `k` from `0→1`, and a carry resets **every** lower bit to 0 in the process (`…0111 → …1000`).
So the range is *forced* to contain a number of the form `prefix‑1‑0‑0…0` (a multiple of `2^k`) whose low bits are
all 0 — ANDing with it clears them. Concretely for `10..15`, that number is `12 = 1100`, which kills bit 1 even
though both endpoints `10` and `15` have bit 1 set. **⚠ This is why "shared set bits of `m` and `n`" is WRONG** —
it's the matching *prefix*, not the per-bit AND of the two endpoints. A `1` that sits below the first disagreement
is already dead.

> **Trigger:** *"AND (or OR) over a contiguous integer range `[m..n]`"* → **common binary prefix of `m` and `n`**
> (shift both ends right until equal, then pad the tail with zeros). Felt-reason: a higher bit can't change without
> sweeping all lower bits through 0.

### The shift implementation (chop columns until equal, then refill with zeros)
"Delete the rightmost column from both (`>> 1`) until the two numbers look identical — what's left is the shared
prefix; the number of chops = how many zero columns to put back (`<< shift`)."

```java
class Solution {
    public int rangeBitwiseAnd(int left, int right) {
        int shift = 0;
        while ((left >> shift) != (right >> shift)) {   // chop low columns until they agree
            shift++;
        }
        return (left >> shift) << shift;   // shared prefix, tail refilled with zeros
    }
}
```
Trace `12,15`: `12>>0≠15>>0`, `6≠7`, then `12>>2 = 3 == 15>>2 = 3` → stop, `shift=2` → `3 << 2 = 12`. ✓
Cost O(31). (Equivalent: shrink `left`/`right` themselves and loop `while (left != right)`, return `left << shift`.)

> **WA-cause [bit-isolation] (this session):** first attempt scanned MSB→LSB correctly but accumulated
> `ans += (left>>i) * (1<<i)` — the **whole** shifted prefix at every matching bit, double-counting prefixes ≥2
> bits (`12,15 → 20` instead of `12`). Fix = isolate one bit: `ans += ((left>>i) & 1) << i`. Step-2 (recompute a
> 2-bit-prefix example before submit) catches this. `x` vs `x & 1` is the recurring shape.

### Why this transfers (the module's foundation)
The one-way monotonicity (OR up / AND down, irreversible) is the lever for the rest of Module 4: it's *why* a
sliding window can decide OR/AND-vs-threshold by length (4.2/4.3) and *why* a fixed endpoint sees ≤31 distinct
OR/AND values (4.4 LogTrick). The range-AND is the smallest instance: "monotone fold over a contiguous range →
look at where the bits stop agreeing."

### Status
✅ Atom 4.1 owned (2026-06-19) — property derived (OR↑/AND↓, irreversible), common-prefix rule self-derived
(incl. *why* sub-prefix bits die), shift code working after fixing the bit-isolation overcount.

---

## 2. bit-count-in-window — sliding OR/AND when the fold isn't invertible (LC 3097/3095)

**The break.** Sliding windows usually maintain a running aggregate: expand → `agg += a[r]`, shrink → `agg -= a[l]`.
That works because `+` has an inverse. **OR and AND do not.** Concretely: window `[6,1,4]` has `OR = 111`; the `6`
leaves and the true OR of `[1,4]` is `101` — but **no operation on `(111, 110)` recovers `101`**, because OR discarded
*how many* elements contributed each bit. So a single accumulator can't track a shrinking window.

**The move.** Keep the missing information yourself — **a count per bit column**, `int[] cnt = new int[31]` over the
current window. OR/AND are then *derived from `cnt[]` on demand*, never tracked incrementally:

| operation | update |
|---|---|
| expand `r` (add `x`) | for each set bit `b` of `x`: `cnt[b]++` |
| shrink `l` (remove `x`) | for each set bit `b` of `x`: `cnt[b]--` |
| window **OR**, bit `b` | set ⟺ `cnt[b] > 0` |
| window **AND**, bit `b` | set ⟺ `cnt[b] == len` (`len = r-l+1`) |

> **`cnt[]` is the single source of truth; OR/AND are read off it.** Don't chase "did this bit just become set?"
> incrementally — when an element leaves, `len` also changes, so the AND condition is a moving target. Recompute
> from `cnt[]` whenever you need the value.

> **Trigger:** *"OR or AND of a sliding/contiguous window, with a threshold (≥K / =K) and add+remove of elements"* →
> 31 column counters; OR=`cnt>0`, AND=`cnt==len`.

**When does a plain two-pointer window even apply?** From 4.1's monotonicity: extending the window only *grows* OR
and only *shrinks* AND. So the validity direction must match the inequality:
- **OR ≥ k** (LC 3097): OR grows with length → once a window qualifies, shrink from the left while still `≥ k`,
  recording the shortest. ✅ standard shrinkable window.
- **AND ≥ k**: AND *shrinks* with length → adding elements only hurts; the "valid" direction inverts. Trap — handle
  in its own classic, don't assume the OR template.

```java
// LC 3097 — shortest subarray with OR >= k  (O(n·31))
public int minimumSubarrayLength(int[] nums, int k) {
    int n = nums.length, best = Integer.MAX_VALUE, l = 0;
    int[] cnt = new int[31];
    for (int r = 0; r < n; r++) {
        for (int b = 0; b < 31; b++) if (((nums[r] >> b) & 1) == 1) cnt[b]++;
        while (l <= r && windowOr(cnt) >= k) {        // shrink while still valid
            best = Math.min(best, r - l + 1);
            for (int b = 0; b < 31; b++) if (((nums[l] >> b) & 1) == 1) cnt[b]--;
            l++;
        }
    }
    return best == Integer.MAX_VALUE ? -1 : best;
}
private int windowOr(int[] cnt) { int or = 0; for (int b = 0; b < 31; b++) if (cnt[b] > 0) or |= (1 << b); return or; }
```

### Status & holdouts
◑ derived (2026-06-19), holdout-pending. **Install:** LC 3095 (OR≥K I, ~1370, in-band). **Stretch holdout:** LC 3097
(OR≥K II, **1891** verified zerotrac — proves the reflex chunks an above-band problem). Both deferred to the problem block.

---

## 3. no-shared-bits window — the OR-mask collapse (LC 2401)

**Problem.** Longest subarray where **every pair** has `AND == 0` (no two elements share a set bit) — a "nice"
subarray. Brute = test all `C(w,2)` pairs per window → O(n²·…), TLE at `n≈10⁵`.

**Compression 1 — check against one number, not all.** A new `x` shares a bit with *someone* in the window ⟺ it
shares a bit with the window's **OR**. So one `&` against the running OR replaces scanning every element.

**Compression 2 — counts collapse to a single mask.** This is the lighter-than-4.2 payoff: because we *maintain*
the window nice, `cnt[b]` can never exceed **1** (two elements sharing bit `b` would be a non-nice pair). Every
column is 0/1 → the whole `cnt[]` array degenerates into **one integer, the OR-mask** of the window.

| op | with mask | why exact |
|---|---|---|
| **detect** collision | `mask & x != 0` | x shares a bit with the window iff it shares with the OR |
| **add** x | `mask |= x` | — |
| **remove** left `a[l]` | `mask ^= a[l]` (or `mask &= ~a[l]`) | a[l]'s bits are all in mask **and** exclusive to it (nice ⇒ no other element holds them), so XOR clears exactly them |

> **AND to detect, OR to add, XOR/`&~` to remove.** Why not "running XOR" for everything? Inside a nice window
> `OR==XOR==SUM` (all disjoint), so XOR-remove is exact — but you can't XOR a *new* element in, because at the moment
> of collision it's *not* disjoint, so XOR would silently toggle the shared bit off instead of flagging the conflict.
> (Connects to Module 3.3: `a&b==0 ⟺ a+b==a^b==a|b`.)

```java
public int longestNiceSubarray(int[] nums) {
    int mask = 0, left = 0, best = 0;
    for (int right = 0; right < nums.length; right++) {
        while ((mask & nums[right]) != 0) {   // collision → shrink from left
            mask ^= nums[left];
            left++;
        }
        mask |= nums[right];
        best = Math.max(best, right - left + 1);
    }
    return best;
}
```
Edge: if shrinking exhausts the window, `mask` collapses to just `nums[right]` (window `[right]`).

> **Trigger:** *"subarray/window where elements must be pairwise bit-disjoint (every pair AND 0 / no shared bits)"*
> → maintain a running OR-mask; `mask & x` detects, shrink-via-XOR until clean. The "nice" invariant is what lets
> the 31-counter degenerate to one mask.

### Status & holdouts
◑ **derived-with-help**, holdout-pending — mechanic understood but **not derived cold** (Claude walked the
mask-collapse + XOR-remove). Classic LC 2401 (**1750** verified, in-band) queued.
**⚠ Execution note:** the verification trace exposed a careless **bit-drop** (`3` mis-binarized as `10`, dropping
bit 0) that propagated through every mask — answer survived by luck. Mechanic ≠ execution; this is the documented
carelessness failure mode, caught precisely *because* we ran the retrieval trace instead of skipping it.

---

## 4. LogTrick — distinct OR/AND over ALL subarrays (LC 898 / LC 1521)

**Problem.** Aggregate something over **every** subarray's OR (or AND) — e.g. count distinct OR values (LC 898),
or find the OR/AND value closest to a target (LC 1521). Brute = OR of all `O(n²)` subarrays → TLE at `n ≈ 5·10⁴`.

**The bound (the load-bearing fact).** Fix the **right** endpoint `r` and slide the left end outward. The sequence
`OR(r..r), OR(r-1..r), …, OR(0..r)` is **non-decreasing** (4.1: extending only turns bits on). Treated as a 31-bit
number it only ever *gains* bits, and a bit once on stays on. So every time the value **changes**, it spends ≥1
fresh bit — and there are only `log₂(V) ≈ 31` bits to spend. ⇒ **at most ~31 distinct OR values among ALL subarrays
ending at `r`**, no matter how many subarrays (could be `r+1`) actually end there. (AND is symmetric: only *loses*
bits → same ≤31 bound. GCD too: each change at least halves → ≤log V.)

**The move (carry the ≤log-V frontier).** Let `S_r` = the set of distinct ORs of subarrays ending at `r`
(`|S_r| ≤ 31`). Recurrence — every subarray ending at `r` is either the singleton `[r]`, or a subarray ending at
`r-1` with `nums[r]` glued on (and `OR(l..r) = OR(l..r-1) | nums[r]`):
```
S_r = { nums[r] }  ∪  { v | nums[r]  :  v ∈ S_{r-1} }
```
Carry only `S_{r-1}` (≤31 entries) forward; fold each `S_r` into the global answer.

> **Trigger:** *"aggregate (count distinct / closest-to-target / sum) over the OR / AND / GCD of ALL subarrays"* →
> LogTrick: per endpoint keep the ≤log-V frontier of distinct values, extend it by the new element, O(n·log V).
> The felt-signal: *the operation only moves one way as the window grows (OR↑/AND↓/GCD↓), so duplicates pile up and
> the distinct frontier is tiny.*

```java
class Solution {
    public int subarrayBitwiseORs(int[] nums) {
        Set<Integer> allDistinctORs = new HashSet<>();
        Set<Integer> orsEndingAtPrev = new HashSet<>();   // S_{r-1}, ≤31 entries
        for (int num : nums) {
            Set<Integer> orsEndingHere = new HashSet<>();  // S_r
            orsEndingHere.add(num);                        // singleton [r]
            for (int prevOR : orsEndingAtPrev) orsEndingHere.add(prevOR | num); // extend each by num
            orsEndingAtPrev = orsEndingHere;
            allDistinctORs.addAll(orsEndingHere);
        }
        return allDistinctORs.size();
    }
}
```
Trace `[1,2,4]`: `S_0={1}`, `S_1={2,3}`, `S_2={4,6,7}` → union `{1,2,3,4,6,7}` → **6**.

**Complexity.** Outer loop `n`; inner loop = `|orsEndingAtPrev| ≤ 31`; HashSet ops O(1) amortized →
**O(n·log V) ≈ O(31n)**. Space O(n·log V) for the global set. The entire win is that the inner loop is bounded by
the **bit-count (31)**, not the **subarray-count (n)** — duplicates merge away. AND/closest-target version: swap
`|`→`&` and track the running best vs target (LC 1521).

### Status & holdouts
◑ **derived-with-help** (2026-06-19), holdout-pending — Claude walked the `S_r` recurrence + the ≤31 bound; user
closed the bound ("each distinct value = one fresh set bit, only 31 to spend"). Classics LC 898 + LC 1521 queued
(verify ratings at solve time).
