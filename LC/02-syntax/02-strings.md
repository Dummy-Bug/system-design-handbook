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
