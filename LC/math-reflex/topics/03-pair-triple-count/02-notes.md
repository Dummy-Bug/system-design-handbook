## The pair count atom

You have `n` distinct elements. How many unordered pairs `(i, j)` with `i < j` can you form?

The answer is `n × (n-1) / 2`. But the formula is useless if you can only memorise it — you need three ways to arrive at it so that if you ever forget the closed form, the derivation muscle still produces it cold.

### Framing 1 — pair-with-others

Pick any element. It can pair with `n - 1` other elements (everyone except itself). Do this for all `n` elements: `n × (n - 1)` pairs.

But each pair has been counted twice. The pair `{a, b}` was counted once when `a` paired with `b`, and once when `b` paired with `a`. So divide by 2: `n(n - 1) / 2`.

### Framing 2 — sequential-pick

You need to choose 2 elements. Pick the first: `n` options. Pick the second: `n - 1` options (anyone except the first). Total ordered picks: `n × (n - 1)`.

Same overcounting — `(a, b)` and `(b, a)` are the same unordered pair. Divide by 2.

### Framing 3 — `C(n, 2)` notation

The formal name for "unordered selections of 2 from `n`" is `C(n, 2)`, also written `nC2` or `(n 2)`. Its closed form is:

```
C(n, 2) = n! / (2! × (n - 2)!) = n(n - 1) / 2
```

The three framings are the same fact viewed from three angles. Each one will be more natural depending on the problem you face — pair-with-others is intuitive for graph degree arguments, sequential-pick maps cleanly to nested loops, and `C(n, k)` is the version that generalises beyond pairs.

### Why divide by 2 — the deeper rule

The "÷ 2" isn't arbitrary. When you go from ordered to unordered for a group of size `k`, you always divide by `k!`. The reason: `k!` is exactly the number of ways to arrange `k` items in a row, and every unordered group of size `k` shows up exactly `k!` times in the ordered count.

For pairs: `2! = 2` arrangements per pair (`(a,b)` and `(b,a)`), so ÷ 2.
For triples: `3! = 6` arrangements per triple, so ÷ 6.
For quadruples: `4! = 24` arrangements, so ÷ 24.

This is the heartbeat behind `C(n, k) = n! / (k! × (n-k)!)` — the `k!` in the denominator kills the ordering.

---

## Concrete recall — these numbers should fire in 5 seconds

| n | `n(n-1)/2` |
|---|------------|
| 5 | 10 |
| 10 | 45 |
| 20 | 190 |
| 100 | 4,950 |
| 1,000 | 499,500 |

The growth is roughly `n²/2`. It sneaks up fast. At `n = 1000` you're already at half a million pairs — which is why brute-force `O(n²)` over `n = 10⁵` is 5 × 10⁹ operations and TLEs in any contest.

---

## Overflow boundary — n² ≥ Integer.MAX_VALUE around n ≈ 46,340

Integer max in Java is roughly `2.1 × 10⁹`. The square root of that is `~46,340`. So:

```
n = 46,340  →  n² ≈ 2.1 × 10⁹   (just fits int)
n = 46,341  →  n² overflows int
```

For pair counting at LC scale (n up to 10⁵), `n × (n - 1) ≈ 10¹⁰` — comfortably overflowing int. Always cast to long before multiplying:

```java
long pairs = (long) n * (n - 1) / 2;
```

Note the cast goes on the **first operand**, not the whole expression. Writing `(long)(n * (n - 1) / 2)` is the same bug — the int multiplication happens first and overflows before the cast. This is CLAUDE.md pre-submit checklist item #1.

---

## The triple count atom

You have `n` distinct elements. How many unordered triples `(i, j, k)` with `i < j < k`?

Same machinery as pairs.

Sequential pick: 1st from `n`, 2nd from `n - 1`, 3rd from `n - 2` → `n × (n - 1) × (n - 2)` ordered triples.

Each unordered triple `{a, b, c}` shows up as `3! = 6` orderings in that count:

```
(a, b, c)   (a, c, b)
(b, a, c)   (b, c, a)
(c, a, b)   (c, b, a)
```

So divide by 6:

```
C(n, 3) = n(n - 1)(n - 2) / 6
```

### Concrete check

n = 5 → `5 × 4 × 3 / 6 = 60 / 6 = 10` triples.

### Overflow boundary for triples — n ≈ 1,290

The cube root of `2.1 × 10⁹` is roughly 1281. So:

```
n = 1,000  →  n³ = 10⁹        (fits int)
n = 1,290  →  n³ ≈ 2.1 × 10⁹  (boundary)
n = 1,300  →  n³ ≈ 2.2 × 10⁹  (overflows int)
```

| Operation | Overflow boundary (int) |
|-----------|--------------------------|
| `n²`      | n > ~46,340 (`√(2.1×10⁹)`) |
| `n³`      | n > ~1,290 (`∛(2.1×10⁹)`) |
| `n⁴`      | n > ~215 |

For LC triple count at `n = 10⁵`, the product is `~10¹⁵` — overflows int by orders of magnitude. Cast the first operand to long:

```java
long triples = (long) n * (n - 1) * (n - 2) / 6;
```

Same trap as pairs: cast the first operand, not the whole expression. `(long)(n * (n-1) * (n-2))` still overflows before the cast applies.

---

## The general `C(n, k)` — derivation

Same shape generalises to picking `k` elements from `n`.

Sequential pick: 1st from `n`, 2nd from `n - 1`, 3rd from `n - 2`, ..., `k`-th from `n - k + 1`. That's `k` descending terms in the numerator:

```
n × (n - 1) × (n - 2) × ... × (n - k + 1)
```

Each unordered group of `k` shows up `k!` times in that ordered count (every permutation of the group is one ordering). Divide by `k!`:

```
C(n, k) = n × (n - 1) × (n - 2) × ... × (n - k + 1)
         ─────────────────────────────────────────
                          k!
```

Equivalent formal form (multiply top and bottom by `(n - k)!`):

```
C(n, k) = n! / (k! × (n - k)!)
```

Quick mental check: substitute `k = 2` → `n(n-1)/2`. Substitute `k = 3` → `n(n-1)(n-2)/6`. The general form reduces correctly.

Deeper machinery — Pascal's identity, modular factorial precomputation, `C(n, k) mod p` via modular inverse, Lucas' theorem — lives in [[10-permutations-combinations]]. This file locks the atomic recall; the theory is built on top there.

---

## The unordered convention in LeetCode problems

LC frequently writes "count pairs `(i, j)` with `i < j` such that ...". The `i < j` constraint is **linguistic**, not algorithmic — it's how LC says *unordered*. The constraint forces a single canonical ordering per pair so each pair is counted exactly once.

If the problem says **"pairs `(i, j)`"** without the `i < j` constraint, it usually means *ordered* — every `(a, b)` and `(b, a)` is a distinct pair, and the count is `n × (n - 1)`, not `n(n-1)/2`.

A 2× factor lives in this one phrase. Read the problem statement carefully — misreading "i < j" as ordered, or missing its absence, is a classic contest WA.

---

## Bucket pairs — counting pairs with the same value

Concrete problem: array `[1, 2, 2, 3, 2, 1]`. Count pairs `(i, j)` with `i < j` and `arr[i] == arr[j]`.

The naive approach is `O(n²)` — check every pair, compare values. At `n = 10⁵` that's `10¹⁰` operations. TLE.

The insight: every matching pair must come from elements with the **same value**. Group elements by value; count pairs within each group.

For each value `v` that appears `k` times, the number of unordered pairs you can form within that group is `C(k, 2) = k(k - 1) / 2`. Sum that across all values.

### Walkthrough on `[1, 2, 2, 3, 2, 1]`

Frequencies: `{1: 2, 2: 3, 3: 1}`.

| Value | Count `k` | `k(k-1)/2` |
|-------|-----------|------------|
| 1 | 2 | 1 |
| 2 | 3 | 3 |
| 3 | 1 | 0 |

Total: `1 + 3 + 0 = 4` pairs.

Verify by hand: matching index pairs are `(0, 5)` for the 1s, and `(1, 2), (1, 4), (2, 4)` for the 2s. That's 4 pairs. ✓

### Java code

```java
Map<Integer, Integer> freq = new HashMap<>();
for (int x : arr) {
    freq.put(x, freq.getOrDefault(x, 0) + 1);
}

long pairs = 0;
for (int k : freq.values()) {
    pairs += (long) k * (k - 1) / 2;
}
```

### The overflow trap

At LC scale `n = 10⁵`, a single bucket can contain all `n` elements (if the array is `[7, 7, 7, ..., 7]`). Then `k = 10⁵` and `k(k-1)/2 ≈ 5 × 10⁹` — overflows int. Cast to long before the multiplication, just like with pure pair count.

### LC anchor

*Number of Good Pairs* (LC 1512, rated ~1200) is literally this exact problem.

---

## Running pair count — d.1

A harder shape: values arrive one at a time. After each arrival, report the running total of same-value pairs formed so far.

The naive approach is to recompute the bucket-pair sum after every arrival — `O(n)` per arrival, `O(n²)` total. Still TLE at scale.

The insight: when a new element arrives, we only need to count **new pairs**, not recompute old ones. If the value `v` arrives and there were already `f` copies of `v` stored, this new element forms exactly `f` new pairs — one with each existing copy. So the delta is `f`, the current frequency of `v` **before** incrementing.

### Walkthrough on `[1, 2, 2, 3, 2, 1]`

| Step | Value | freq before | delta | running total |
|------|-------|-------------|-------|---------------|
| 1 | 1 | 0 | 0 | 0 |
| 2 | 2 | 0 | 0 | 0 |
| 3 | 2 | 1 | +1 | 1 |
| 4 | 3 | 0 | 0 | 1 |
| 5 | 2 | 2 | +2 | 3 |
| 6 | 1 | 1 | +1 | 4 |

Final = 4, matching the bucket-sum from earlier. ✓

### The algorithm in three lines

1. Read the current count for this value from the freq map — call it `prev`.
2. Add `prev` to the running total.
3. Increment the freq map entry for this value.

```java
long total = 0;
Map<Integer, Integer> freq = new HashMap<>();
for (int x : arr) {
    int prev = freq.getOrDefault(x, 0);   // freq BEFORE increment
    total += prev;                         // delta = prev
    freq.put(x, prev + 1);                 // then increment
    // report(total);
}
```

### The order-of-operations trap

If you increment first and then read, you'd count this new element itself as part of its own bucket — an off-by-one that gives one extra pair per arrival. The variable `prev` makes the correct order syntactically obvious, which is why this form is safer than chaining `put` and `get`.

### Why delta = freq-before (algebraic check)

The delta from adding one more element to a bucket is:

```
C(k, 2) - C(k - 1, 2)
= k(k-1)/2 - (k-1)(k-2)/2
= (k - 1) × [k - (k - 2)] / 2
= (k - 1) × 2 / 2
= k - 1
```

So adding the `k`-th element of a value bumps the pair count by `k - 1`, which equals the previous frequency. The algorithm and the formula agree.

---

## Derived-key bucketing — d.2

The final generalisation: the "match" isn't equality between values, it's some derived condition. Example:

> Count pairs `(i, j)` with `i < j` such that `(arr[i] + arr[j]) % k == 0`.

The naive approach is `O(n²)` again. The smart approach reuses the bucket idea, but the bucket key changes.

### What to bucket by

In the same-value problem, two elements match iff their values are equal — so we bucketed by value. Here, two elements match iff their **sum is divisible by k** — equivalently, iff their **remainders mod k sum to 0 or k**. So we bucket by remainder: every element with `value % k = r` goes into bucket `r`.

### Walkthrough on `[1, 2, 3, 4, 6]` with k = 5

Remainders:
- `1 % 5 = 1`
- `2 % 5 = 2`
- `3 % 5 = 3`
- `4 % 5 = 4`
- `6 % 5 = 1`

Buckets:
- bucket 0: empty
- bucket 1: `[1, 6]`
- bucket 2: `[2]`
- bucket 3: `[3]`
- bucket 4: `[4]`

For two elements to sum to a multiple of 5, their remainders must sum to 0 or 5:
- bucket 0 pairs within itself (`0 + 0 = 0`)
- bucket 1 pairs with bucket 4 (`1 + 4 = 5`)
- bucket 2 pairs with bucket 3 (`2 + 3 = 5`)

Cross-bucket pair count is `|bucket 1| × |bucket 4| = 2 × 1 = 2` and `|bucket 2| × |bucket 3| = 1 × 1 = 1`. Total = 3.

Verify by enumeration: `(1, 4)`, `(6, 4)`, `(2, 3)`. Three pairs. ✓

### The complement formula

For a bucket with remainder `r`, its complement bucket has remainder `(k - r) % k`. The outer `% k` handles the case `r = 0` — the complement of 0 is 0, not k.

| `r` | complement |
|-----|------------|
| 0 | 0 (self-pair) |
| 1 | k - 1 |
| 2 | k - 2 |
| ... | ... |
| k - 1 | 1 |

### Why it works — the modular addition identity

The proof relies on `(a + b) % k = (a % k + b % k) % k`. Every number can be written as `(some multiple of k) + (remainder)`. The "multiple of k" parts contribute nothing to `(a + b) % k`, so only the remainders matter. Full derivation lives in [[06-modular-arithmetic]] — it's the central identity of that topic.

### Streaming version — combining d.1 and d.2

If the values arrive one at a time and we report the running total, the same "read before write" pattern applies — but you read from the **complement bucket**, write to **your own bucket**.

```java
long total = 0;
Map<Integer, Integer> freq = new HashMap<>();
for (int x : arr) {
    int r = ((x % k) + k) % k;     // safe positive remainder
    int c = (k - r) % k;           // complement bucket
    total += freq.getOrDefault(c, 0);
    freq.put(r, freq.getOrDefault(r, 0) + 1);
    // report(total);
}
```

The `((x % k) + k) % k` instead of bare `x % k` handles negative inputs — Java's `%` can return negative for negative operands. That trap lives in [[06-modular-arithmetic]] too.

### The general pattern

> For "count pairs where condition F(arr[i], arr[j]) holds":
>
> 1. Identify the **derived key** `K` such that F can be rewritten as "key[i] matches some function `g(key[j])`".
> 2. Bucket every element by its key.
> 3. For each arrival (or each element in a single pass), look up `g(key)` in the freq map — that's your delta.
> 4. Then increment `freq[key]`.
> 5. Read before write, always.

Examples of this pattern:
- Pairs with equal values: key = value, `g(k) = k` (same bucket pairs with itself — the d.1 form)
- Pairs with sum divisible by k: key = `value % k`, `g(r) = (k - r) % k`
- Pairs with XOR equal to K: key = value, `g(v) = v ^ K`
- Pairs with difference equal to K: key = value, `g(v) = v - K`
- Pairs whose product is a perfect square: key = "square-free part of value", `g(s) = s`

### LC anchors

- *Subarray Sums Divisible by K* (LC 974, rated ~1450) — bucket prefix sums by remainder mod k. Two prefix sums with the same remainder differ by a multiple of k.
- *Find the Number of Good Pairs II* — derived-key variants.
- XOR-pair and diff-pair problems use the same key+complement skeleton with different `g`.
