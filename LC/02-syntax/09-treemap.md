# 09 — TreeMap

## Declaration

```java
TreeMap<Integer, Integer> tm = new TreeMap<>();                          // ascending by key (default)
TreeMap<Integer, Integer> tm = new TreeMap<>(Comparator.reverseOrder()); // descending by key
```

## Core Operations (same as HashMap)

```java
tm.put(3, 10);
tm.get(3);           // 10
tm.containsKey(3);
tm.remove(3);
tm.size();
```

## Navigation Methods (sorted-only extras)

```java
TreeMap<Integer, Integer> tm = new TreeMap<>();
tm.put(1, 'a'); tm.put(3, 'b'); tm.put(5, 'c'); tm.put(7, 'd');

tm.firstKey();     // 1 — smallest key
tm.lastKey();      // 7 — largest key
tm.floorKey(4);    // 3 — largest key ≤ 4
tm.ceilingKey(4);  // 5 — smallest key ≥ 4
```

## Iteration

```java
for (Map.Entry<Integer, Integer> entry : tm.entrySet()) {
    int key = entry.getKey();
    int val = entry.getValue();
}
// iterates in sorted key order
```

## Gotchas

- Sorts by **key only** — cannot sort by value
- `floorKey` / `ceilingKey` return `null` if no such key — always null-check
- All ops are O(log n) — uses Red-Black Tree under the hood
- Same `Key` suffix pattern: `firstKey`, `lastKey`, `floorKey`, `ceilingKey`

## When to use

- Need a map where keys are always sorted
- Range queries: "find closest price to X", "find all keys between A and B"
- Problems involving sorted intervals or ordered frequencies
