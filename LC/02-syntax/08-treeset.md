# 08 — TreeSet

## Declaration

```java
TreeSet<Integer> ts = new TreeSet<>();       // ascending (default)
TreeSet<Integer> ts = new TreeSet<>(Comparator.reverseOrder());  // descending
```

## Core Operations (same as HashSet)

```java
ts.add(5);
ts.contains(5);
ts.remove(5);
ts.size();
ts.isEmpty();
```

## Navigation Methods (sorted-only extras)

```java
TreeSet<Integer> ts = new TreeSet<>(Arrays.asList(1, 3, 5, 7, 9));

ts.first();       // 1 — smallest
ts.last();        // 9 — largest
ts.floor(6);      // 5 — largest element ≤ 6  (inclusive)
ts.ceiling(6);    // 7 — smallest element ≥ 6 (inclusive)
ts.lower(6);      // 5 — largest element < 6  (exclusive)
ts.higher(6);     // 7 — smallest element > 6 (exclusive)
```

## Iteration

```java
for (int val : ts) { }  // iterates in sorted order
```

## Gotchas

- `floor` / `ceiling` return `null` if no such element — always null-check before using
- Iteration order is sorted, unlike HashSet which is unordered
- All ops (`add`, `remove`, `contains`) are O(log n) — HashSet is O(1) but unordered

## When to use

- Need sorted order + fast floor/ceiling lookups
- Sliding window problems where you need closest value
- Any problem asking for "next greater" or "next smaller" element
