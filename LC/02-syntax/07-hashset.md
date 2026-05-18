# 07 — HashSet

## Declaration

```java
Set<Integer> st = new HashSet<>();
Set<Long> st = new HashSet<>();
Set<String> st = new HashSet<>();
```

## Core Operations

```java
Set<Integer> st = new HashSet<>();

st.add(5);          // adds 5 — returns false if already exists
st.contains(5);     // true
st.remove(5);       // removes 5
st.size();          // number of elements
st.isEmpty();       // true if empty
```

## Iteration

```java
// for-each — no entrySet, no keySet, just elements directly
for (int val : st) { }
```

## Deduplication Pattern (most common in LC)

```java
int[] nums = {1, 2, 2, 3, 3, 3};

Set<Integer> st = new HashSet<>();
for (int n : nums) st.add(n);
// st = {1, 2, 3} — duplicates gone
```

## Gotchas

- No `containsKey` — that's HashMap. Use `contains` directly
- No `values()` or `entrySet()` — just elements, no keys or values
- `st.add(x)` returns `false` if x already in set — sometimes useful to detect duplicate on the fly
- HashSet is unordered — iteration order is not guaranteed

## Critical trap — `int[]` in a HashSet does NOT deduplicate

```java
Set<int[]> set = new HashSet<>();
set.add(new int[]{1, 2});
set.add(new int[]{1, 2});
set.size(); // 2 — NOT 1
```

`HashSet` uses `hashCode()` and `equals()` for dedup. Java arrays inherit both from `Object` — `hashCode()` is based on **memory address**, not values. Two `new int[]{1, 2}` are different objects → different hash codes → different buckets → both inserted.

**The fix: encode the pair into a type with value-based `hashCode()`.**

Three options for `(int x, int y)` pairs:

**1. String key (simplest, slowest):**
```java
set.add(x + "," + y);   // Set<String>
```
Comma is mandatory — without it, `(1, 23)` and `(12, 3)` both become `"123"`.

**2. Multiplication offset (fast, needs range):**
```java
set.add((long) x * 200001 + y);   // Set<Long>
```
Works like flattening a 2D grid: `row * numCols + col`. Each x gets its own chunk of 200001 slots; y picks a slot inside. Unique as long as `|y| < 200001`. Pick the constant ≥ range of y.

**3. Bit packing (fastest, zero constants):**
```java
set.add(((long) x << 32) | Integer.toUnsignedLong(y));   // Set<Long>
```
Top 32 bits = x, bottom 32 bits = y. `Integer.toUnsignedLong(y)` widens y to long without sign extension — critical, because Java's default widening copies the sign bit into the upper 32 bits, which would collide with x when y is negative.

Equivalent forms of the same trick (in case you see them elsewhere):
```java
((long) x << 32) | ((long) y & ((1L << 32) - 1))   // computed mask
((long) x << 32) | ((long) y & 0xFFFFFFFFL)        // hex mask
```

See `02-syntax/13-bit-manipulation.md` for the full derivation (sign extension, why `(long)` cast is needed before the shift).

**Rule of thumb:** String for "don't think", multiplication for "know the range", bit-pack for "any int range, no constants".
