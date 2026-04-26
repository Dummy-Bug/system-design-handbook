# 12 — Priority Queue

## Declaration

```java
// min-heap (default) — smallest element comes out first
PriorityQueue<Integer> pq = new PriorityQueue<>();

// max-heap — largest element comes out first
PriorityQueue<Integer> pq = new PriorityQueue<>(Comparator.reverseOrder());
```

## Core Operations

```java
pq.offer(5);    // add element
pq.poll();      // remove and return top (min or max)
pq.peek();      // look at top without removing
pq.isEmpty();
pq.size();
```

## Custom Comparator

```java
// min-heap by first element of int[]
Comparator<int[]> byFirst = (a, b) -> Integer.compare(a[0], b[0]);
PriorityQueue<int[]> pq = new PriorityQueue<>(byFirst);

// max-heap by first element of int[]
Comparator<int[]> byFirstDesc = (a, b) -> Integer.compare(b[0], a[0]);
PriorityQueue<int[]> pq = new PriorityQueue<>(byFirstDesc);
```

## Multi-field Comparator

```java
// min-heap: sort by first element ascending, if tied then second element descending
Comparator<int[]> custom = (a, b) -> {
    if (a[0] != b[0]) return Integer.compare(a[0], b[0]);
    return Integer.compare(b[1], a[1]);
};
PriorityQueue<int[]> pq = new PriorityQueue<>(custom);
```

## Top-K Smallest Elements (max-heap of size K)

```java
// max-heap of size K — always holds the K smallest seen so far
Comparator<Integer> maxOrder = (a, b) -> Integer.compare(b, a);
PriorityQueue<Integer> pq = new PriorityQueue<>(maxOrder);

for (int n : nums) {
    if (pq.size() < k) {
        pq.offer(n);
    } else if (n < pq.peek()) {
        pq.poll();
        pq.offer(n);
    }
}
// pq now contains K smallest elements
```

## Top-K Largest Elements (min-heap of size K)

```java
// min-heap of size K — always holds the K largest seen so far
PriorityQueue<Integer> pq = new PriorityQueue<>();

for (int n : nums) {
    if (pq.size() < k) {
        pq.offer(n);
    } else if (n > pq.peek()) {
        pq.poll();
        pq.offer(n);
    }
}
// pq now contains K largest elements
```

## Drain in Sorted Order

```java
while (!pq.isEmpty()) {
    int val = pq.poll();   // each poll gives next smallest (min-heap) or largest (max-heap)
}
```

## Gotchas

- Default is **min-heap** — `poll()` returns smallest, not largest
- Use max-heap (size K) for top-K smallest; use min-heap (size K) for top-K largest
- Never use `a - b` in comparator — use `Integer.compare(a, b)` to avoid overflow
- `Comparator.reverseOrder()` only works for wrapper types (`Integer`, `String`) — use lambda for `int[]`
- `poll()` returns `null` if empty — check `isEmpty()` first
