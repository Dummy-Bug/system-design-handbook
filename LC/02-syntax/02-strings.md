## Core Operations

```java
String s = "leetcode";

s.charAt(2)              // 'e'  — returns char
s.length()               // 8
s.substring(2, 6)        // "etco" — index 2 to 5 (end is exclusive)
s.substring(4)           // "code" — index 4 to end
s.contains("leet")       // true — returns boolean
s.indexOf('e')           // 1 — first index of char, -1 if not found
s.equals("leetcode")     // true — compare content, never use ==
s.toCharArray()          // ['l','e','e','t','c','o','d','e']
String.valueOf('a')      // "a" — char → String
"hello" + "world"        // "helloworld" — avoid in loops, use StringBuilder
```

## indexOf — all variants

```java
String s = "leetcode";

s.indexOf('e')           // 1    — first occurrence of char, -1 if not found
s.indexOf('e', 2)        // 2    — first occurrence of char at or after index 2
s.indexOf("eet")         // 1    — first occurrence of substring, -1 if not found
s.indexOf("eet", 2)      // -1   — first occurrence of substring at or after index 2
s.lastIndexOf('e')       // 2    — last occurrence of char
s.lastIndexOf('e', 1)    // 1    — last occurrence of char at or before index 1
```

- Always returns `-1` if not found — always null-check before using the result
- Second argument is the **starting index** (inclusive) to search from
- Safe to pass `fromIndex > s.length()` — just returns `-1`

## substring — all variants

```java
String s = "leetcode";

s.substring(4)           // "code"  — index 4 to end
s.substring(2, 6)        // "etco"  — index 2 to 5 (end is exclusive)
s.substring(0, s.length()) // "leetcode" — full string copy
s.substring(i, i+1)      // single char as String (when you need String not char)
```

- `end` is **exclusive** — always
- `substring(i, i)` returns `""` — empty string, no exception
- `substring(s.length())` returns `""` — no exception

## split — all variants

```java
String s = "a,b,c";

s.split(",")             // ["a", "b", "c"] — split on literal char
s.split("\\.")           // split on dot — must escape regex special chars: . * + ? | ( ) [ ] { } ^ $
s.split(" ")             // ["a", "b", "c"] — split on space
s.split(" \\| ")         // split on " | " (space-pipe-space) — alternation OR
s.split("", 3)           // limit: at most 3 parts — ["a", ",b,c"] if limit=2
s.split("")              // split every char — ["a", ",", "b", ",", "c"]
```

- Returns `String[]` — iterate with for-each or index
- Special regex chars (`.`, `*`, `+`, `|`) must be escaped with `\\`
- Alternation: `"a|b"` matches `a` OR `b` — use `\\|` to escape the pipe
- For simple single-char splits, `indexOf` in a loop is faster and cleaner than `split`

## join — concatenate array/list into string

```java
String[] arr = {"a", "b", "c"};
List<String> list = Arrays.asList("x", "y", "z");

String.join(",", arr)           // "a,b,c" — join array with separator
String.join(",", list)          // "x,y,z" — join list with separator
String.join("", arr)            // "abc" — no separator
String.join(" | ", "a", "b")    // "a | b" — varargs, pass strings directly
```

- Returns `String` — the concatenated result
- Separator goes **between** elements, not at start/end
- Works with `String[]`, `List<String>`, or varargs
- Faster and cleaner than manual `StringBuilder` loops for joining collections

## String vs StringBuilder vs StringBuffer

| | Mutable | Use in LC |
|-|---------|-----------|
| `String` | No | Yes, for input/output |
| `StringBuilder` | Yes | Yes, when building in a loop |

## StringBuilder

```java
StringBuilder sb = new StringBuilder();
sb.append('a');                    // "a"
sb.append("hello");                // "ahello"
sb.append(s1).append(s2);         // chaining — "ahello" + s1 + s2
sb.insert(1, 'x');                 // "axhello" — insert at index (rare)
sb.deleteCharAt(sb.length() - 1); // remove last char — "axhell" (backtracking)
sb.delete(1, 3);                   // remove index 1 to 2 — "aell"
sb.toString();                     // "aell" — convert back to String
```

## Comparing Strings

```java
s1 == s2        // compares reference — NEVER use for strings
s1.equals(s2)   // compares content — always use this
```

**Rule:** `==` for primitives, `.equals()` for objects and strings.

## Gotchas

- `s.length()` needs parens — arrays use `s.length` without parens
- `substring(start, end)` — end is **exclusive**
- `s1 + s2` in a loop = O(n²) — use `StringBuilder.append` instead
- `sb.append` not `sb.add`
- `sb.deleteCharAt` not `sb.pop`
