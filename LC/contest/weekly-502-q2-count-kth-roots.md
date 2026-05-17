# Weekly Contest 502 Q2 — Count K-th Roots in a Range

**Link:** https://leetcode.com/problems/count-k-th-roots-in-a-range/
**Date:** 2026-05-17
**Contest result:** N (TLE → MLE → TLE → AC post-contest)
**13k+ AC during contest — felt cooked. Was actually a single architectural bug + a complexity misconception.**

---

## Problem

Given `l, r, k`, count integers `y` in `[l, r]` such that `y = x^k` for some non-negative integer `x`.

**Constraints:**
- `0 ≤ l ≤ r ≤ 10⁹`
- `1 ≤ k ≤ 30`

---

## What I wrote in-contest (TLE)

```java
public int countKthRoots(int l, int r, int k) {
    if (k == 1) return r - l + 1;

    Set<Integer> set = new HashSet<>();
    for (int i = 1; (int)Math.pow(i, k) <= r; i++) {
        int power = (int)Math.pow(i, k);
        set.add(power);
    }

    int count = 0;
    if (l == 0) set.add(0);
    for (int i = l; i <= r; i++) {              // <-- THE TLE SOURCE
        if (set.contains(i)) count++;
    }
    return count;
}
```

**Why it TLE'd:** With `l = 0, r = 10⁹`, the final loop runs **1 billion iterations**. Java handles only ~10⁸ ops/sec → guaranteed TLE.

---

## The misconception that caused it

> "I thought 10⁹ iterations would get accepted and 10¹⁰ would give TLE."

**Wrong.** Java's effective ceiling on LC is **~10⁸ simple ops in 1 second.** 10⁹ TLEs every time. With HashMap/HashSet ops, drop to ~10⁷.

---

## The deeper bug — confused-scope analysis

The code had **two loops**:

1. **Generation loop:** `for (int i = 1; i^k ≤ r; i++)` — bounded by `r^(1/k)` ≤ 31623 for k=2. ✅
2. **Counting loop:** `for (int i = l; i ≤ r; i++)` — bounded by `r - l + 1` ≤ 10⁹. ❌

I correctly analyzed loop 1 in my head. I forgot loop 2 even existed in my complexity analysis. Under contest pressure I patched local bugs (`getPower` → `Math.pow`) without ever questioning whether loop 2 should exist at all.

**Lesson:** Always sum the ops across ALL loops in your code, then compare to 10⁸. A correct sub-loop next to a billion-op sibling is still TLE.

---

## The fix — merge counting INTO generation

```java
public int countKthRoots(int l, int r, int k) {
    if (k == 1) return r - l + 1;

    int count = 0;
    if (l == 0) count++;  // 0^k = 0

    for (long x = 1; ; x++) {
        long power = 1;
        boolean overflow = false;
        for (int i = 0; i < k; i++) {
            power *= x;
            if (power > r) { overflow = true; break; }
        }
        if (overflow) break;
        if (power >= l) count++;
    }
    return count;
}
```

**Why this works:**
- One loop, bounded by `r^(1/k)` — at most ~31623 outer iterations
- Inner multiplication bounded by `k ≤ 30`, broken early on overflow
- Total: ~1M ops worst case
- Uses `long` to avoid `int` overflow during multiplication
- No set, no re-scan — count while you generate

---

## Math.pow trap — never use for integer powers

```java
(int) Math.pow(1000, 3)   // might return 999999999, not 10⁹
```

`Math.pow` returns `double`. For values near `10⁹`, floating-point error rounds the wrong way after cast to int.

**Rule:** For integer powers, always use integer multiplication with overflow check in `long`.

---

## The big lesson — n → complexity reverse engineering

When you see the constraints, your brain should *immediately* produce a target complexity:

| n is at most | Target complexity | Why |
|---|---|---|
| 10⁹ | O(1) or O(log n) | n itself is too large to iterate |
| 10⁶ – 10⁸ | O(n) or O(n log n) | Linear barely fits |
| 10⁴ – 10⁵ | O(n log n) or O(n √n) | n² is 10¹⁰ → TLE |
| 10³ | O(n²) | n² = 10⁶ fits |
| 500 | O(n³) | n³ ≈ 10⁸ fits |
| 40 | O(2^(n/2)) — MITM | 2⁴⁰ too big, 2²⁰ ≈ 10⁶ |
| 20 | O(2ⁿ) — bitmask | 2²⁰ ≈ 10⁶ fits |
| 12 | O(n!) — permutations | 12! ≈ 5×10⁸ |

**Application to this problem:** `r ≤ 10⁹` means you CANNOT loop over `[0, r]`. You must iterate over something smaller — the candidate set (perfect powers), which is at most `r^(1/k)` ≤ 31623 for k=2.

When you see `r ≤ 10⁹`, your brain should reflexively say: **"I will not enumerate the range. I will enumerate candidates."**

---

## Java ops/sec cheat-sheet

| Operation | Ops/sec ceiling |
|---|---|
| Simple int ops (`+`, `*`, `<`, array access) | ~10⁸ |
| HashMap / HashSet `put`/`get` | ~10⁷ |
| TreeMap / TreeSet ops | ~10⁶ |
| String concatenation, regex | ~10⁶ |
| Heavy recursion (boxing, GC) | ~10⁶ |

**LC Java time limit:** typically 1-2 sec. So if `ops > 2 × 10⁸`, expect TLE.

Python is ~10× slower — apply mental factor of /10.

---

## The contest meta-lesson

This was NOT a knowledge gap. It was:

1. **Misconception about op budget** (10⁹ vs 10⁸) — calibration error
2. **Confused-scope analysis** — patched bugs locally instead of zooming out to the architecture
3. **Lack of confidence in own work** — generated correct candidates, then re-scanned the range "to make sure"

All three are pressure-induced. Fix is: build the n → complexity reflex so hard that when you see `10⁹`, your hand refuses to type `for (int i = l; i <= r; i++)`.

**Next contest:** before submitting, count ops across ALL loops in the code, compare to 10⁸. If anything exceeds, refactor before submitting.
