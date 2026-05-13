# Integer overflow — use long

> [!info] When summing or multiplying values that can grow beyond `Integer.MAX_VALUE` (~2.1 × 10⁹), `int` will silently overflow and produce wrong answers. Use `long` for accumulators.

---

## When to suspect it

Read the **constraints** carefully:

| Constraint pattern | Risk |
|--------------------|------|
| `n ≤ 10^5` AND `nums[i] ≤ 10^4` | Sum up to 10⁹ — borderline, use long to be safe |
| `n ≤ 10^5` AND `nums[i] ≤ 10^5` | Sum up to 10¹⁰ — **must use long** |
| `n ≤ 10^4` AND `nums[i] ≤ 10^6` | Sum up to 10¹⁰ — **must use long** |
| Product of two ints | Always check — `int * int` can overflow even when neither operand does |
| `nums[i] * nums[i]` | Squaring can hit 10¹⁸ — long required |

**Rule of thumb:** if the worst-case sum/product can exceed **2 × 10⁹**, use `long`.

`Integer.MAX_VALUE` = 2,147,483,647 ≈ 2.1 × 10⁹.

---

## The bug — concrete failing example

**Problem:** [House Robber V](https://leetcode.com/problems/house-robber-v/description/) (LC 1619)

Constraint: `nums[i] ≤ 10^4`, `n ≤ 10^5`. Worst-case total = `10^9`. The DP accumulates partial sums, which can hit `10^10`.

**Buggy code:**
```java
int[] dp = new int[n];  // BUG: int array
dp[i] = Math.max(dp[i-2] + nums[i], dp[i-1]);
// Eventually dp[n-1] overflows when the answer exceeds 2.1e9
```

**Failing test pattern:** any array where total non-adjacent sum > 2.1e9 produces a negative or wrapped result.

---

## The fix

```java
long[] dp = new long[n];  // use long
dp[i] = Math.max(dp[i-2] + nums[i], dp[i-1]);
return dp[n-1];  // return long, or check int range
```

---

## Common overflow traps

### 1. Cast operands BEFORE multiplying
```java
// WRONG — multiplication happens in int, then cast
long result = nums[i] * nums[i];  // can overflow before cast

// RIGHT — promote to long first
long result = (long) nums[i] * nums[i];
```

### 2. Cumulative sum / prefix sum arrays
```java
// WRONG
int[] prefix = new int[n];
prefix[0] = nums[0];
for (int i = 1; i < n; i++) prefix[i] = prefix[i-1] + nums[i];  // can overflow

// RIGHT
long[] prefix = new long[n];
```

### 3. Math.abs(Integer.MIN_VALUE) is itself
```java
// WRONG
int x = Integer.MIN_VALUE;
int absX = Math.abs(x);  // returns Integer.MIN_VALUE (negative!) — overflow

// RIGHT
long absX = Math.abs((long) x);
```

### 4. Subtraction wrap-around
```java
// WRONG
int diff = a - b;  // if a is very negative and b is very positive, overflows

// RIGHT
long diff = (long) a - b;
```

### 5. MOD with negative results
```java
// WRONG (in some contexts)
int result = (a - b) % MOD;  // can be negative

// RIGHT
int result = ((a - b) % MOD + MOD) % MOD;
```

---

## Template for spotting in future problems

During **constraint reading** (step 1 of the 5-step ritual):

1. Multiply the worst-case `n` by the worst-case `nums[i]`. If > 2 × 10⁹ → flag.
2. Square the worst-case `nums[i]`. If > 2 × 10⁹ → flag.
3. Note any product of two large values in the algorithm → flag.

When in doubt, **use `long` everywhere**. The performance cost is negligible (~5%), the correctness gain is enormous.

---

## Source problems

- LC 198 — House Robber (small constraints, int safe)
- LC 213 — House Robber II
- LC 740 — Delete and Earn (similar overflow risk at large n)
- LC 1043 — Partition Array for Maximum Sum
- LC 1639 — House Robber V (the one this lesson came from)

---

## Related patterns

- [[05-constraint-reading-first]] — overflow detection starts from constraints
- [[04-modular-arithmetic-negative-offsets]] — related arithmetic correctness issue
