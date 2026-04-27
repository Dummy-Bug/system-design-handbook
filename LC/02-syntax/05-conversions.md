
## String ↔ int

```java
int x = Integer.parseInt("123");   // "123" → 123
String s = String.valueOf(123);    // 123 → "123"
```

## String ↔ char[]

```java
char[] chars = "hello".toCharArray();   // "hello" → ['h','e','l','l','o']
String s = new String(chars);           // ['h','e','l','l','o'] → "hello"
String s = String.valueOf(chars);       // same — both work

// ⚠️ DO NOT do this — silent bug, returns "[C@1540e19d"
String wrong = chars.toString();        // Object.toString() — NOT the string content
```

## char ↔ String

```java
String s = String.valueOf('a');   // 'a' → "a"
char c = "a".charAt(0);          // "a" → 'a'
```

## int ↔ char (cast)

```java
char c = (char) 97;    // 97 → 'a'
int x = (int) 'a';     // 'a' → 97

// relative position (0-25)
int pos = 'c' - 'a';          // 'c' → 2
char c = (char)(2 + 'a');     // 2 → 'c'
```

## int[] ↔ List\<Integer\>

```java
// int[] → List<Integer>
int[] nums = {1, 2, 3};
List<Integer> list = Arrays.stream(nums)
                           .boxed()                        // int → Integer
                           .collect(Collectors.toList());  // [1, 2, 3]

// List<Integer> → int[]
int[] arr = list.stream()
                .mapToInt(Integer::intValue)
                .toArray();                                // {1, 2, 3}
```

## int[] ↔ Integer[]

```java
// int[] → Integer[]
Integer[] boxed = Arrays.stream(nums)
                        .boxed()
                        .toArray(Integer[]::new);

// Integer[] → int[]
int[] unboxed = Arrays.stream(boxed)
                      .mapToInt(Integer::intValue)
                      .toArray();
```

## Integer[] ↔ List\<Integer\>

```java
// Integer[] → List<Integer>
List<Integer> list = Arrays.asList(boxed);   // fixed-size, can't add/remove

// List<Integer> → Integer[]
Integer[] arr = list.toArray(new Integer[0]);
```

## Integer Utility Constants

```java
Integer.MAX_VALUE   // 2147483647  (~2 × 10^9) — use to init min variable
Integer.MIN_VALUE   // -2147483648 (~-2 × 10^9) — use to init max variable
Integer.valueOf(2)  // int → Integer (boxing) — needed for al.remove(Integer.valueOf(2))
```

**Common LC pattern:**
```java
int min = Integer.MAX_VALUE;
int max = Integer.MIN_VALUE;
for (int n : nums) {
    min = Math.min(min, n);
    max = Math.max(max, n);
}
```

## Character Utility Methods

```java
Character.isDigit('5')          // true  — '0'–'9'
Character.isLetter('a')         // true  — letters only
Character.isLetterOrDigit('_')  // false — alphanumeric check
Character.isUpperCase('A')      // true
Character.isLowerCase('a')      // true
Character.isWhitespace(' ')     // true  — space, tab, newline

Character.toLowerCase('A')      // 'a'
Character.toUpperCase('a')      // 'A'

Character.getNumericValue('5')  // 5    — char digit → int (only for digits)
// for plain digit chars, c - '0' is faster and idiomatic:
int d = '5' - '0';              // 5
```

**Common LC pattern — clean a string to alphanumeric lowercase:**
```java
StringBuilder sb = new StringBuilder();
for (char c : s.toCharArray()) {
    if (Character.isLetterOrDigit(c)) {
        sb.append(Character.toLowerCase(c));
    }
}
```

## Quick Reference Table

| From | To | Method |
|------|----|--------|
| `String` | `int` | `Integer.parseInt(s)` |
| `int` | `String` | `String.valueOf(n)` |
| `String` | `char[]` | `s.toCharArray()` |
| `char[]` | `String` | `new String(chars)` |
| `char` | `String` | `String.valueOf(c)` |
| `char` | `int` (ASCII) | `(int) c` |
| `int` | `char` | `(char) n` |
| `char` | `int` (relative) | `c - 'a'` |
| `int` | `char` (relative) | `(char)(n + 'a')` |
| `int[]` | `List<Integer>` | `Arrays.stream(arr).boxed().collect(...)` |
| `List<Integer>` | `int[]` | `list.stream().mapToInt(...).toArray()` |
| `int[]` | `Integer[]` | `Arrays.stream(arr).boxed().toArray(Integer[]::new)` |
| `Integer[]` | `int[]` | `Arrays.stream(arr).mapToInt(...).toArray()` |

## Math Utilities

```java
Math.min(a, b)       // smaller of two
Math.max(a, b)       // larger of two
Math.abs(-5)         // 5 — absolute value
Math.pow(2, 10)      // 1024.0 — returns double
Math.sqrt(16)        // 4.0 — returns double
Math.floor(3.7)      // 3.0 — round down
Math.ceil(3.2)       // 4.0 — round up
```

**Common pattern — cast back to int:**
```java
int result = (int) Math.pow(2, 10);   // 1024
int root = (int) Math.sqrt(n);        // floor of square root
```

## Modulo

```java
7 % 3    // 1
4 % 8    // 4 — dividend smaller than divisor, result is dividend
-7 % 3   // -1 — sign follows dividend, same as -(7 % 3)
```

**Safe positive modulo (circular indexing):**
```java
((n % m) + m) % m       // always positive, even if n is negative

int next = (i + 1) % n; // circular next index
```

## Long Constants

```java
Long.MAX_VALUE   // 9223372036854775807 (~9.2 × 10^18)
Long.MIN_VALUE   // -9223372036854775808
```

## Gotchas

- `Integer.parseInt` not `Integer.valueOf` for String → int (valueOf returns `Integer` object)
- `new String(chars)` and `String.valueOf(chars)` both work for char[] → String
- **Never call `.toString()` on a `char[]`** — it returns the Object hash (e.g. `[C@1540e19d`), not the string. Silent bug, no compile error. Use `new String(chars)`.
- `Arrays.asList` returns fixed-size list — wrap in `new ArrayList<>()` if you need to modify
- Always use `Integer.MAX_VALUE` / `Integer.MIN_VALUE` to init min/max, never hardcode
- `Math.pow` and `Math.sqrt` return `double` — cast to `int` if needed
