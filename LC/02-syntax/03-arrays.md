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
```

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
