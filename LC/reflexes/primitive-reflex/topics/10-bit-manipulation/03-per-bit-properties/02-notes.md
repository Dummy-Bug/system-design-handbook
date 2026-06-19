# Module 3 — Per-bit thinking & properties (notes)

> ✅ **STATUS (2026-06-19):** **Hamming (LC 477)** and **AND-pairs** now TRULY owned — the
> value-decomposition / order-swap intuition is installed (re-derived cold via the carry-conservation argument
> below). **OR, XOR, LC 1835 still to be solved cold** (the hard part — the intuition — is now done; these are
> just new per-column counts on the same machinery).
>
> **The intuition that finally landed (2026-06-19) — carry-conservation:**
> - A **carry is a relabel, not a value change**: two ones in column `b` (worth `2·2^b`) become one in column
>   `b+1` (worth `2^{b+1}`) — *same value*. Proof: splitting `sum` ones as `(sum%2)` here + `(sum/2)` carried up
>   gives `(sum%2)·2^b + (sum/2)·2^{b+1} = sum·2^b`. So however far carries cascade, total value is conserved.
> - Therefore **carrying only exists to write the answer in binary.** If you only want the decimal *value*, skip
>   it: `total = Σ_b (count of ones in column b) · 2^b`. Counting "four ones" is *already decimal*; `%2`/carry is
>   purely a representation step.
> - This is exactly the **order-swap**: `Σ_items (item value)` = `Σ_items Σ_b 2^b·[bit set]`
>   → `Σ_b 2^b·(# items with bit b set)`. Works for a list of numbers AND for a list of pair-ANDs (a pair-AND is
>   just a number).
> - **No double-count worry:** one pair can land in several columns — that just peels off its AND's separate bits
>   (`AND=5=4+1` ⇒ counted in col2 and col0), reconstructing its value. No column ever counts the same bit twice.

## 1. Per-bit contribution — the column-decomposition reflex

**Setup.** A quantity is a **sum over all pairs** `(i, j)`, `i < j`, and each pair's value is **defined bit-by-bit**
(Hamming distance, AND, OR, XOR of the two numbers). Naive = enumerate all `C(n,2)` pairs → O(n²). At `n = 10^5`
that's ~10^10 ops → TLE.

**The move.** Bits never interact across columns. So the total sum splits into **independent per-column sums**:
```
answer = Σ over bit-columns b   of   (column b's contribution)
```
Iterate the ~31 columns. In each column you only need **`c` = how many numbers have bit `b` set**. Then a closed
form per operator. Cost: O(31 · n) = O(n).

> **Trigger:** *"answer is a SUM over all pairs/subsets, each pair's value is per-bit"* → **think in columns, count
> set bits, plug a closed form.** Don't enumerate pairs.

### The four closed forms (re-derive, don't memorize)
For column `b`: `c` numbers have the bit set, `n − c` don't, `n` total.

| Problem | Column fires for a pair when… | # such pairs | Column term |
|---|---|---|---|
| **Hamming** (LC 477) | bits **differ** (one set, one unset) | `c·(n−c)` | `c·(n−c)` |
| **AND** sum | **both** set | `C(c,2) = c(c−1)/2` | `2^b · c(c−1)/2` |
| **OR** sum | **at least one** set | `C(n,2) − C(n−c,2)` | `2^b · (totalPairs − bothUnset)` |
| **XOR** sum | **exactly one** set | `c·(n−c)` | `2^b · c(n−c)` |

The unifying question: *what does this operator need from the two bits in one column for that column to land in
the result?* AND needs both 1; OR needs ≥one 1; XOR needs exactly one 1; Hamming needs them different.

### 1a. Total Hamming Distance — LC 477
Differing pair = one set + one unset → `c·(n−c)` per column. No `2^b` weight (Hamming counts *positions*, not value).
```java
public int totalHammingDistance(int[] nums) {
    int ans = 0, n = nums.length;
    for (int b = 0; b <= 30; b++) {
        int c = 0;
        for (int num : nums) if (((num >> b) & 1) == 1) c++;
        ans += c * (n - c);
    }
    return ans;
}
```

### 1b. Sum of AND of all pairs — [GfG](https://www.geeksforgeeks.org/dsa/calculate-sum-of-bitwise-and-of-all-pairs/)
Column lands in a pair's AND only when **both** picked numbers have it → `C(c,2)` pairs, weighted `2^b`.
```java
public long sumAND(int[] arr) {
    long ans = 0;
    for (int b = 0; b <= 30; b++) {
        long c = 0;
        for (int x : arr) if (((x >> b) & 1) == 1) c++;
        ans += (1L << b) * (c * (c - 1) / 2);
    }
    return ans;
}
```

### 1c. Sum of OR of all pairs — [GfG](https://www.geeksforgeeks.org/dsa/sum-of-bitwise-or-of-all-pairs-in-a-given-array/) ✅ *(self-derived 2026-06-19)*
OR has the bit when **≥ one** is set. **Two equivalent counts:**
- **Direct (self-derived):** ≥one = both-set + exactly-one = `C(c,2) + c·(n−c)`.
- **Complement:** `totalPairs − bothUnset = C(n,2) − C(n−c,2)`.

Both give the same number; the direct split (both + exactly-one) is the clearer one to reach for.
```java
public long sumOR(int[] arr) {
    int n = arr.length;
    long totalPairs = (long) n * (n - 1) / 2;
    long ans = 0;
    for (int b = 0; b <= 30; b++) {
        int c = 0;
        for (int x : arr) if (((x >> b) & 1) == 1) c++;
        long bothUnset = (long) (n - c) * (n - c - 1) / 2;
        ans += (1L << b) * (totalPairs - bothUnset);
    }
    return ans;
}
```

### 1d. Sum of XOR of all pairs — [GfG](https://www.geeksforgeeks.org/dsa/sum-xor-pairs-array/) ✅ *(self-derived 2026-06-19)*
XOR fires when **exactly one** of the two is set → same `c·(n−c)` count as Hamming, but **weighted `2^b`**
(Hamming counts positions = weight 1; XOR sums values = weight `2^b`).
```java
public long sumXOR(int[] arr) {
    int n = arr.length;
    long ans = 0;
    for (int b = 0; b <= 30; b++) {
        long c = 0;
        for (int x : arr) if (((x >> b) & 1) == 1) c++;
        ans += (1L << b) * c * (n - c);
    }
    return ans;
}
```

### Why this transfers (the generative payoff)
This is the opposite of a one-trick formula. The *reasoning pattern* — "all-pairs/all-subsets + per-bit-defined →
decompose into independent columns" — fires on unseen problems (subset XOR sums, "sum of f(bit) over a range",
contribution counting in general). On a novel contest Q2 you skip the 20-min "how do I avoid O(n²)" and go straight
to "column by column, count `c`, find the per-column count." That chunk *is* the speed.

---

## 2. Greedy bit construction — build the answer MSB → LSB

**The lemma (the engine).** A single high bit outweighs **all** lower bits combined: `2^k = (2^{k-1}+…+2^0) + 1`,
so `1000 (=8) > 0111 (=7)`. Consequence: when constructing a number to be **as large as possible**, *always secure
the highest bit you can first* — no combination of lower bits can ever compensate for giving up a higher one.

**The reflex.** Decide bits **top-down (MSB→LSB)**. At each bit: *try to set it*; keep it set only if doing so
stays **feasible** (enough candidates / set-bit budget remaining). A greedy high commitment is never regretted.
When you commit a bit, **shrink the candidate set** to those still consistent with everything committed so far —
that makes every lower-bit decision automatically restricted to numbers that already agree on the higher bits.

> **Trigger:** *"maximize/construct a number under a feasibility constraint"* → build MSB→LSB, greedily set each
> bit if it stays feasible, narrow candidates on commit.

### 2a. Max AND pair — ✅ *(self-derived + coded, 2026-06-19)*
> Given `arr`, pick two distinct indices `i ≠ j` maximizing `A[i] & A[j]`. Return the max AND value.
Brute = O(n²) pairs → TLE at `n=10^5`. Greedy: at bit `b` (high→low), if **≥ 2** current candidates have bit `b`
set, the answer *can* keep this bit → commit it and **narrow the pool to exactly those**. If ≤ 1 candidate has it,
the bit stays 0 and the pool is untouched (need a *pair* to realize a bit). The narrowing guarantees the final
survivors all share every committed bit, so a real pair achieving `ans` exists.

```java
// candidate-mask form (no list rebuilding): a number is consistent if it has ALL committed bits.
public int maxAndPair(int[] arr) {
    int ans = 0;
    for (int b = 30; b >= 0; b--) {
        int candidate = ans | (1 << b);
        int count = 0;
        for (int x : arr) if ((x & candidate) == candidate) count++;
        if (count >= 2) ans = candidate;   // commit bit b only if ≥2 numbers carry all committed bits
    }
    return ans;
}
```
Equivalent pool-narrowing form (matches the derivation literally): keep a `candidates` list; at each bit collect
those with the bit set; if `size ≥ 2`, `ans |= 1<<b` and replace `candidates` with that sublist; else leave it.

### 2b. Smallest XOR with exactly B set bits — ▢ *(to re-derive cold — claimed prior, NOT re-derived this session)*
> Given `A`, `B`: find `X` with exactly `B` set bits minimizing `A ^ X`.
Idea (to verify by cold re-derivation): match `A`'s set bits high→low to zero out high XOR bits (each match spends
one of the `B` ones); if `B` exceeds `popcount(A)`, spill the leftover ones into the **lowest** zero positions
(cheapest damage); if `B < popcount(A)`, cover only `A`'s **highest** `B` set bits. **Not counted as owned yet.**

### Atom 3.2 rep ledger (honest)
- ✅ Max AND pair — self-derived + coded (2026-06-19).
- ▢ Smallest XOR with B set bits — re-derive cold for a 2nd clean rep.
- ⏸ LC 421 (Max XOR pair) — trie / greedy-prefix variant; to brainstorm separately.

---

## 3. Bit-algebra identities — regenerate from one 2-bit table (don't memorize)

**The reflex: never recall these formulas — rebuild them in 30s from the single-bit truth table.** For two single
bits `x, y`:

```
 x   y  | x^y   x&y   x|y | x+y
--------|-------------------|----
 0   0  |  0     0     0   |  0
 0   1  |  1     0     1   |  1
 1   0  |  1     0     1   |  1
 1   1  |  0     1     1   |  2
```

**Key observation — `x^y` and `x&y` are MUTUALLY EXCLUSIVE** (never both 1 in a bit: `&` fires only on the `(1,1)`
row, where `^=0`). So adding `(a^b)+(a&b)` never makes two 1's collide in a column → **no carry** → per-bit
identities lift to full integers exactly.

**The identity set (all read off the table):**
- **`a | b = (a^b) + (a&b)`** — `|`-column = `^`-column + `&`-column; exact (no carry, by mutual exclusivity).
- **`a + b = (a|b) + (a&b)`** — `+`-column = `|`-column + `&`-column.
- **`a + b = (a^b) + 2·(a&b)`** — substitute the first into the second. *(= Module 1.5 add-via-XOR+carry:
  `^` is the carry-less sum, `&` is the carries, `2·` shifts them up one place.)*
- **`a − b = a + (~b + 1)`** — two's-complement negation (from Foundations).

**The contest trigger (the payload):** from `a+b = (a^b) + 2(a&b)`,
```
a + b == a ^ b   ⟺   2·(a&b) == 0   ⟺   a & b == 0   (a, b share NO set bit)
```
and when `a & b == 0`, everything collapses:
```
a & b == 0   ⟺   a + b  ==  a | b  ==  a ^ b
```
(no shared bits ⇒ nothing carries ⇒ `+`, `|`, `^` all just lay disjoint bits side by side.)

> **Felt-signal:** a problem says *"`x + y = x ^ y`"*, or *"partition / distribute a number's set bits into
> groups"*, or *"`a + b = n` with `a, b` submasks of `n`"* → that's the disguised condition **`a & b == 0`**, and
> you may freely swap `+ / | / ^` on those disjoint parts.

**Why it transfers (vs. memorizing 5 formulas):** the whole family is *one* 2-bit case table + the mutual-exclusion
note. Regenerating beats recalling — a year from now the table is trivial to rebuild, the formulas would have rotted.

### Status
✅ Atom 3.3 owned (2026-06-19) — derived the full identity set + `a&b==0` trigger from the truth table, self-driven.
