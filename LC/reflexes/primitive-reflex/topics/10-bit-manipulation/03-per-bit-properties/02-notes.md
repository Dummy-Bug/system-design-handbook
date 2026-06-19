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
