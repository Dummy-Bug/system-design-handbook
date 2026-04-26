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
