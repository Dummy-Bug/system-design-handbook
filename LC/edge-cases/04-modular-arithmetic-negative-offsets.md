# Modular arithmetic with negative offsets

> [!info] When computing `(a - b) % MOD` and `a < b` is possible, the result in Java/C++ will be negative. Always normalize with `((a - b) % MOD + MOD) % MOD`.

---

## When to suspect it

Trigger conditions:

- Cyclic / wraparound logic (Caesar ciphers, clock arithmetic, ring buffers)
- Difference of two values that can go negative
- Sliding window with cyclic indices
- DP with subtraction inside a MOD expression
- Any expression like `(x - y) % m` where `x < y` is reachable

**Language note:** Python's `%` returns a non-negative result by default for positive modulus. Java/C++/C# do NOT — they preserve the sign of the dividend. This is a frequent bug for Pythonistas switching languages.

---

## The bug — concrete failing example

**Problem:** [Count Caesar Cipher Pairs](https://leetcode.com/problems/count-caesar-cipher-pairs/) (LC 1624)

To detect words that are Caesar shifts of each other, normalize each word relative to its first character:

```
shift[j] = (word[j] - word[0]) % 26
```

**Buggy code:**
```java
int shift = (word.charAt(j) - word.charAt(0)) % 26;
// If word[j] < word[0], shift is negative
// Example: word = "az" → shift[1] = (a - a) % 26 = 0
//          word = "ba" → shift[1] = (a - b) % 26 = -1  (WRONG; should be 25)
```

This breaks the normalization — `"ba"` and `"az"` should produce the same signature (both shift sequences `[0, 25]`), but the buggy code gives `[0, -1]` for `"ba"`.

---

## The fix

```java
int MOD = 26;
int shift = ((word.charAt(j) - word.charAt(0)) % MOD + MOD) % MOD;
```

Breakdown:
1. `(a - b) % MOD` → may be negative (range: `-(MOD-1)` to `MOD-1`)
2. `+ MOD` → shifts to positive (range: `1` to `2*MOD - 1`)
3. `% MOD` → normalizes to `[0, MOD-1]`

**Why two MODs?** The first one handles the possibly-negative result. The second one brings the now-positive (but possibly > MOD) result back into range.

---

## Visual: the number line

```
Without normalization:
   -25 -20 -15 -10 -5  0  5  10  15  20  25
    |   |   |   |   |  |  |  |   |   |   |
    [---- negative ----][- pos -]
    (bug zone)            (ok)

After (% MOD + MOD) % MOD:
                       0  5  10  15  20  25
                       |  |  |   |   |   |
                       [-- all in [0, 25] --]
```

---

## Common variants

### Cyclic distance
```java
// distance between i and j on a circular array of size n
int dist = ((j - i) % n + n) % n;  // always in [0, n-1]
```

### Negative DP transitions
```java
// dp[i] = (dp[i-1] - dp[i-k] + MOD) % MOD;  // ensures non-negative
```

### String hash with MOD subtraction
```java
// rolling hash: removing leading character
long newHash = ((oldHash - leadChar * pow[len-1]) % MOD + MOD) % MOD;
```

### Java BigInteger note
`BigInteger.mod()` (lowercase) always returns non-negative. `BigInteger.remainder()` keeps sign.

---

## Template for spotting in future problems

When you see any expression of the form `(a - b) % MOD`:

1. **Ask: can `a < b`?** If yes → wrap with `((... % MOD + MOD) % MOD)`.
2. **In cyclic contexts:** if any indexing involves subtraction, always normalize.
3. **In DP with subtraction:** add MOD before applying the outer MOD.

Pre-coding check: "Is my MOD expression guaranteed non-negative? If not, fix the formula before writing tests."

---

## Source problems

- LC ??? — [Count Caesar Cipher Pairs](https://leetcode.com/problems/count-caesar-cipher-pairs/) (1624)
- LC 1031 — Maximum Sum of Two Non-Overlapping Subarrays (uses prefix sum diffs)
- LC 1015 — Smallest Integer Divisible by K (modular state machine)
- LC 1442 — Number of Subarrays with Total XOR (XOR is its own inverse, but related)

---

## Related patterns

- [[03-integer-overflow-use-long]] — related arithmetic correctness issue
- [[10-category-checklists]] — see "Math/Number" row for full modular checklist
