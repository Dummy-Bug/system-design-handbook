## Primitives vs Wrapper Classes

| Primitive | Wrapper     |
|-----------|-------------|
| `int`     | `Integer`   |
| `char`    | `Character` |
| `long`    | `Long`      |
| `double`  | `Double`    |
| `float`   | `Float`     |
| `boolean` | `Boolean`   |

**Rule:** Default to primitives. Use wrapper only when a collection forces you (`List<Integer>`, `Map<Character, Integer>`).

`Char` does not exist in Java. It's `char` or `Character`.

## ASCII Quick Reference

| Char | ASCII |
|------|-------|
| `'A'` | 65 |
| `'Z'` | 90 |
| `'a'` | 97 |
| `'z'` | 122 |

Total English alphabets: **26** (a-z, A-Z each)

## char ↔ int Conversions

```java
// relative position (use this 90% of the time)
int pos = c - 'a';          // 'a'→0, 'b'→1, 'z'→25
char c = (char)(pos + 'a'); // 0→'a', 1→'b', 25→'z'

// absolute ASCII value
int ascii = (int) c;        // 'a'→97
char c = (char) ascii;      // 97→'a'
```

## long — when to use

`int` overflows at ~2 billion (2,147,483,647 ≈ 2 × 10^9).

Use `long` when:
- Multiplying two large ints
- Running sum on large array
- Problem says "answer can be very large"

```java
long result = (long) a * b;  // cast one operand, Java promotes the rest
```

## Ceiling Division

Two ways to compute `ceil(a / b)`:

```java
// Option 1 — cast to double (readable)
(int) Math.ceil((double) a / b)

// Option 2 — pure integer (faster, no floating point)
(a + b - 1) / b
```

**Why `Math.ceil(a / b)` is wrong:**
`a / b` is integer division — remainder is discarded before `ceil` even runs.
`7 / 3 = 2` → `Math.ceil(2) = 2` (wrong, should be 3).
`(double)7 / 3 = 2.333` → `Math.ceil(2.333) = 3` (correct).

Rule: `Math.ceil` is useless unless the input is already a decimal.

## Gotchas

- `Char` doesn't exist → use `char` or `Character`
- Cast one operand to `long` before multiplication, not after
