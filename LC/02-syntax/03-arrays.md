## Declaration

```java
int[] nums = new int[5];          // default: 0
char[] chars = new char[5];       // default: '\0'
boolean[] seen = new boolean[5];  // default: false

int[] nums = {1, 2, 3};           // inline init — no size needed
int[] nums = new int[]{1, 2, 3};  // inline init — when not at declaration
```

## Access and Update

```java
int[] nums = {10, 20, 30, 40, 50};
nums[2]       // 30 — get value at index 2
nums[2] = 99; // nums = {10, 20, 99, 40, 50}
nums.length   // 5 — property, no parens (unlike String)
```

**Note:** Arrays are fixed size — you cannot delete. Either overwrite with 0 or use `ArrayList`.

## Iteration

```java
// index-based
for (int i = 0; i < nums.length; i++) { }

// for-each
for (int n : nums) { }
for (char c : chars) { }          // works directly on char[]
for (char c : s.toCharArray()) { } // String needs toCharArray() first
```

## Arrays Utility Methods

```java
Arrays.sort(nums);                    // sort ascending in-place
Arrays.fill(nums, 0);                 // fill entire array with value
Arrays.copyOf(nums, n);               // copy first n elements
Arrays.copyOfRange(nums, 2, 5);       // copy index 2 to 4 (end exclusive)
Arrays.binarySearch(nums, key);       // see section below — return value is weird
```

## `Arrays.binarySearch` — and Java's missing lower_bound

Java has **no built-in `lower_bound` / `upper_bound`** (C++ does). The only array binary search is `Arrays.binarySearch`, and its **return contract** is the thing to memorize.

```java
Arrays.binarySearch(int[] a, int key)                              // whole array
Arrays.binarySearch(int[] a, int fromIndex, int toIndex, int key)  // range [from, to) — to is exclusive
```

The array (or the searched range) must already be **sorted** — result is undefined otherwise.

```
found      → returns a matching index   (>= 0)
not found  → returns  -(insertionPoint) - 1   (always <= -1)
```

Decode the not-found case to get where the key *would* go:

```java
int idx = Arrays.binarySearch(a, 0, len, key);
if (idx < 0) idx = -idx - 1;   // recover insertion point (= lower_bound when no dupes of key)
```

**Why `-(ip) - 1` and not just `-ip`:** the insertion point can be `0`, and `-0 == 0` would be indistinguishable from "found at index 0". The `-1` shift pushes every not-found result strictly negative, so the two cases never collide:

```
insertion point   0    1    2    3
encoded          -1   -2   -3   -4
```

> [!warning] It's a true lower_bound **only when the array has no duplicate of the key.** If the key is present multiple times, `binarySearch` returns *some* matching index — **unspecified which one**. So the decoded insertion point equals lower_bound only for absent keys (or arrays with no dupes of that key). For a real index-returning lower_bound on an array with duplicates, **hand-roll the `lo <= hi` loop**. It works cleanly for LIS because the `tails` array is strictly increasing — no dupes (see `DP/lis.md`).

For floor/ceiling on the **values** (not an array index), use `TreeSet.floor/ceiling/lower/higher` — see `08-treeset.md`. Full bounds mental model: `patterns/binary-search-bounds.md`.

## 2D Arrays

```java
int[][] grid = new int[3][4];         // 3 rows, 4 columns

grid[1][2]                            // access row 1, col 2
grid.length                           // row count
grid[0].length                        // column count

for (int i = 0; i < grid.length; i++) {
    for (int j = 0; j < grid[0].length; j++) {
        System.out.println(grid[i][j]);
    }
}
```

## int[] ↔ List Conversions (the only stream use case worth memorizing)

```java
// int[] → List<Integer>
List<Integer> list = Arrays.stream(nums)
                           .boxed()
                           .collect(Collectors.toList());

// Integer[] → List<Integer>
List<Integer> list = Arrays.asList(nums);

// List<Integer> → int[]
int[] arr = list.stream()
                .mapToInt(Integer::intValue)
                .toArray();
```

## Default Values

| Type      | Default  |
|-----------|----------|
| `int`     | `0`      |
| `char`    | `'\0'`   |
| `boolean` | `false`  |
| `Object`  | `null`   |

## Gotchas

- `nums.length` — no parens (property), `s.length()` — parens (method)
- `grid[0].length` for column count, not `grid.length`
- Inline init without `new int[]{}` only works at declaration
- `Arrays.sort` on `int[]` sorts ascending only — for descending, convert to `Integer[]` first
- `Arrays.asList` returns fixed-size list — can't add/remove from it
- `Arrays.binarySearch` needs a **sorted** array — undefined result otherwise
- not-found returns `-(insertionPoint) - 1` — decode with `-idx - 1`, never use the raw negative as an index
- it's a true lower_bound only when there's **no duplicate of the key** — hand-roll the loop for arrays with dupes
