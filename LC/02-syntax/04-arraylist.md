
## How to Read Generic Types (inside → out)

```
List<Integer>
     ↑ inner: a list of integers

List<List<Integer>>
          ↑ inner: a list of integers
     ↑ outer: a list where each element is itself a list of integers

ArrayList<Integer>[]
          ↑ inner: a list of integers
↑ outer: an array where each slot holds a list of integers
```

**Rule:** Read from the innermost type outward. Each wrapper tells you what contains what.

## Declaration

```java
// empty
List<Integer> al = new ArrayList<>();

// with initial capacity (pre-allocated but still empty — not fixed size)
List<Integer> al = new ArrayList<>(10);

// from existing values
List<Integer> al = new ArrayList<>(Arrays.asList(1, 2, 3));

// 2D — list of lists (dynamic, size unknown upfront)
List<List<Integer>> al = new ArrayList<>();
al.add(new ArrayList<>());    // add inner list
al.get(0).add(5);             // add to inner list

// array of ArrayLists (fixed outer size, use when n is known — e.g. graphs)
ArrayList<Integer>[] graph = new ArrayList[n];
for (int i = 0; i < n; i++)
    graph[i] = new ArrayList<>();  // must initialize each slot manually
graph[0].add(5);
graph[0].get(0);
```

## When to Use Which

| | `List<List<Integer>>` | `ArrayList<Integer>[]` |
|-|-----------------------|------------------------|
| Outer size | dynamic, can grow | fixed at declaration |
| Use case | size unknown upfront | size known (e.g. n nodes in graph) |

## Core Operations

```java
List<Integer> al = new ArrayList<>(Arrays.asList(10, 20, 30, 40));

al.add(50);                      // [10, 20, 30, 40, 50]
al.add(2, 99);                   // [10, 20, 99, 30, 40, 50] — insert at index 2
al.get(2);                       // 99
al.set(2, 77);                   // [10, 20, 77, 30, 40, 50]
al.remove(2);                    // removes index 2 → [10, 20, 30, 40, 50]
al.remove(Integer.valueOf(20));  // removes value 20 → [10, 30, 40, 50]
al.size();                       // 4
al.contains(30);                 // true
al.isEmpty();                    // false
```

## Iteration

```java
// index-based
for (int i = 0; i < al.size(); i++) {
    int val = al.get(i);
}

// for-each
for (int val : al) { }
```

## Gotchas

- `al.remove(2)` removes by **index** — use `al.remove(Integer.valueOf(2))` to remove by **value**
- `Arrays.asList(...)` returns a **fixed-size** list — can't add/remove from it. Wrap in `new ArrayList<>()` if you need to modify
- Array of ArrayLists needs manual initialization in a loop — slots are `null` by default
- `al.size()` not `al.length` — length is for arrays only
