# TLE / MLE — Operation & Memory Budgets

A reference for predicting whether your code will pass on LeetCode before you submit. Calibration errors here cost contest problems — and they're entirely preventable with a 5-second mental check.

---

## The core ceiling — memorize this

**Java on LeetCode: ~10⁸ simple operations per second.**

LC typical time limit: 1–2 seconds → effective budget is ~2×10⁸ ops total.

If your estimated total operations exceed this → **TLE is guaranteed** 

---

## Ops/sec table by operation type (Java)

| Operation | Ops/sec | Notes |
|---|---|---|
| Simple int ops (`+`, `-`, `*`, `<`, array access) | ~10⁸ | The baseline ceiling |
| Long ops | ~10⁸ | Slightly slower than int on some JVMs but treat as same |
| `HashMap` / `HashSet` `put`/`get` | ~10⁷ | Hashing + autoboxing |
| `TreeMap` / `TreeSet` ops | ~10⁶ | Red-black tree rebalancing |
| String concatenation (`+`) | ~10⁶ | Creates new String each time |
| `StringBuilder.append` | ~10⁷ | Use this instead of `+=` |
| Regex matching | ~10⁶ | Pre-compile if reused |
| Heavy recursion (boxing, deep stack) | ~10⁶ | GC pressure from autoboxing |
| `Math.pow`, `Math.sqrt`, `Math.log` | ~10⁷ | Floating-point + safety overhead |

**Python:** divide all of these by ~10.
**C++:** multiply by ~2–3 (so ~3×10⁸ simple ops/sec).

---

## n → complexity reverse engineering (read this BEFORE coding)

When you see the constraints, your brain should *immediately* produce a target complexity. This is the single most important skill for contests.

| Max input `n` | Target complexity | Why |
|---|---|---|
| `10⁹` | O(1) or O(log n) | n itself is too large to even iterate |
| `10⁶ – 10⁸` | O(n) or O(n log n) | Linear barely fits |
| `10⁴ – 10⁵` | O(n log n) or O(n √n) | n² = 10¹⁰ → TLE |
| `10³` | O(n²) | n² = 10⁶ — fits |
| `500` | O(n³) | n³ ≈ 10⁸ — borderline, fits |
| `40` | O(2^(n/2)) — **MITM** | 2⁴⁰ too big; 2²⁰ ≈ 10⁶ fits |
| `20` | O(2ⁿ) — **bitmask DP** | 2²⁰ ≈ 10⁶ fits |
| `12` | O(n!) — **permutations** | 12! ≈ 5×10⁸ borderline |
| `8` | O(n!) freely | 8! = 40320 |

**How to apply during a contest:**

1. Read the constraint on `n` (or `r`, `m`, etc.) first.
2. Match it to the row above → that's your target complexity.
3. Only THEN start designing the algorithm.

**Reflex to build:** when you see `n ≤ 10⁹`, your hand should refuse to type `for (int i = 0; i < n; i++)`. The constraint is telling you "don't enumerate the range — enumerate candidates derived from it."

---

## How to spot TLE in your own code BEFORE submitting

**The procedure:**

1. List every loop in your code.
2. For each loop, write `<size> × <body cost>`.
3. Sum everything.
4. Compare to ~2×10⁸.

**Example — the Weekly Contest 502 Q2 TLE I just shipped:**

```java
for (int i = 1; (int)Math.pow(i, k) <= r; i++) {      // loop A: ~31623 iters × Math.pow ~10⁷ = ~3×10⁵
    set.add((int)Math.pow(i, k));
}
for (int i = l; i <= r; i++) {                         // loop B: 10⁹ iters × O(1) lookup = 10⁹  ← TLE
    if (set.contains(i)) count++;
}
```

Loop A is fine. Loop B is 10⁹ → 5× over budget. Catching this **before submitting** requires summing both loops, not just analyzing whichever one feels harder.

---

## The classic TLE traps (Java-specific)

### Trap 1 — Scanning the range `[l, r]` when `r` is large

```java
for (int i = l; i <= r; i++) { ... }
```

If `r ≤ 10⁹`, this is automatically TLE. Replace with: enumerate candidates only.

### Trap 2 — Recomputing inside a loop

```java
for (int i = 1; Math.pow(i, k) <= r; i++) {
    int p = (int) Math.pow(i, k);       // Math.pow called TWICE per iter
}
```

Compute once, store. Also: `Math.pow` is ~10× slower than integer multiplication.

### Trap 3 — Using `ArrayList<Integer>` when `int[]` works

```java
ArrayList<Integer> arr = new ArrayList<>();  // autoboxing on every access
```

Replace with `int[]`. Autoboxing costs ~5–10× in tight loops.

### Trap 4 — `String +=` in a loop

```java
String s = "";
for (...) s += ch;     // O(n²) — each += copies the entire string
```

Use `StringBuilder`.

### Trap 5 — HashMap when array works

If keys are bounded small integers (e.g., 0–1000), use `int[]` instead of `HashMap<Integer, Integer>`. 10× faster.

### Trap 6 — Recursion without memoization where state is small

Pure recursion: O(2ⁿ). With memo: O(states × transitions). Always check if state space is small enough to memo.

---

## MLE — Memory Limit Exceeded

**LC Java heap:** typically ~256 MB.

Memory budget guide:

| Data structure | Memory per element (Java) | Max safe count |
|---|---|---|
| `int[]` | 4 bytes | ~6×10⁷ |
| `long[]` | 8 bytes | ~3×10⁷ |
| `Integer[]` (boxed) | ~16 bytes | ~10⁷ |
| `HashMap<Integer, Integer>` entry | ~50 bytes | ~5×10⁶ |
| `HashSet<Integer>` entry | ~40 bytes | ~6×10⁶ |
| `String` (per char) | ~2 bytes | ~10⁸ chars total |
| 2D `int[n][n]` | 4·n² bytes | n ≤ ~8000 |
| Recursion stack frame | ~100 bytes | depth ≤ ~10⁶ |

**Common MLE traps:**

### MLE Trap 1 — Boolean array vs HashSet for huge range

```java
boolean[] seen = new boolean[r + 1];     // r = 10⁹ → 1 GB → MLE
```

Use `HashSet<Integer>` instead, OR — better — restructure so you don't need to mark every index.

### MLE Trap 2 — 2D DP that should be 1D rolling

```java
int[][] dp = new int[n][m];     // n=m=10⁴ → 4×10⁸ bytes = 400 MB → MLE
```

If `dp[i]` only depends on `dp[i-1]`, use two 1D arrays and swap.

### MLE Trap 3 — Storing all intermediate states

```java
List<int[]> states = new ArrayList<>();   // appending 10⁷ snapshots → MLE
```

Often you only need the latest state, not the full history.

### MLE Trap 4 — Auto-boxing in `Set<Integer>` for large counts

Each boxed `Integer` is ~16 bytes vs 4 for `int`. If you're storing 10⁷+ small ints, switch to `int[]` or use a bitset.

