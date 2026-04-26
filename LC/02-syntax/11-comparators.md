# 11 — Comparators & Sorting

## Default Sort

```java
int[] nums = {3, 1, 4, 1, 5};
Arrays.sort(nums);                          // ascending — only works on primitives/wrapper
Collections.sort(list);                     // ascending — for List
```

## Custom Sort with Lambda

```java
// sort int[][] by first element ascending
Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));

// sort int[][] by first element descending
Arrays.sort(intervals, (a, b) -> Integer.compare(b[0], a[0]));

// sort String[] by length ascending
Arrays.sort(words, (a, b) -> Integer.compare(a.length(), b.length()));

// sort String[] by length descending
Arrays.sort(words, (a, b) -> Integer.compare(b.length(), a.length()));
```

## Comparator.reverseOrder() — for wrapper types only

```java
Integer[] nums = {3, 1, 4, 1, 5};
Arrays.sort(nums, Comparator.reverseOrder());   // descending — Integer[] only, not int[]
```

## Multi-field Sort

```java
// sort by first element ascending, if tied then second element descending
Arrays.sort(intervals, (a, b) -> {
    if (a[0] != b[0]) return Integer.compare(a[0], b[0]);  // first ascending
    return Integer.compare(b[1], a[1]);                      // second descending
});
```

**Rule:** multi-line lambda needs `{}` and `return`. Single-line needs neither.

## Gotchas

- Never use `a - b` for comparison — can overflow if values are near `Integer.MIN_VALUE`
- Use `Integer.compare(a, b)` instead — safe always
- `Comparator.reverseOrder()` only works with `Integer[]`, `String[]` — not `int[]`
- `Arrays.sort` on `int[]` has no comparator overload — convert to `Integer[]` first if you need custom sort on primitives
