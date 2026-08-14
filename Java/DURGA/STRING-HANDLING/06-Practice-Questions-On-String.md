Five certification-style questions on `String`. Every one is answered by material already covered — immutability, `trim()`, `==` versus `.equals()`. The value is in seeing how the exam **combines** two rules so that each one alone gives the wrong answer.

Work each out before reading on. All outputs are measured on JDK 25.

---

# Question 1 — chained `concat` and a discarded result

```java
public class Test {
    public static void main(String[] args) {
        String ta = "a";
        ta = ta.concat("b");
        String tb = "c";
        ta = ta.concat(tb);
        ta.replace('c', 'd');
        ta = ta.concat(tb);
        System.out.println(ta);
    }
}
```

**Options:** `abcd` · `acd` · `abcc` · `abdc`

## Walking it

The only rule needed: **a change creates a new object; whether you keep it depends on whether you assign it.**

| Line | What happens | `ta` afterwards |
|---|---|---|
| `ta = "a"` | SCP object | `a` |
| `ta = ta.concat("b")` | new object `ab`, **assigned** | `ab` |
| `tb = "c"` | SCP object | — |
| `ta = ta.concat(tb)` | new object `abc`, **assigned** | `abc` |
| `ta.replace('c','d')` | new object `abd` — **not assigned** | `abc` |
| `ta = ta.concat(tb)` | new object `abcc`, **assigned** | `abcc` |

**Line five is the trap.** `replace` genuinely produces `abd`, but the result is thrown away, so that object is immediately eligible for garbage collection and `ta` still holds `abc`. Anyone who mentally applies the replacement answers `abdc`.

Measured:

```
abcc
```

**Answer: `abcc`.**

---

# Question 2 — `trim()` on a single space

```java
public class Test {
    public static void main(String[] args) {
        String str = " ";
        str.trim();
        System.out.println(str.equals("") + " " + str.isEmpty());
    }
}
```

**Options:** `true true` · `true false` · `false true` · `false false`

## Walking it

Two rules, and you need both.

**`str` is a one-character string** — that character is a space. It is **not** empty; its length is 1.

**`str.trim()` is called and its result is discarded.** `trim()` does produce a new, empty string — but nothing is assigned, so that object is eligible for garbage collection and `str` is unchanged, still holding the single space.

So both checks run against `" "`, not `""`:

- `str.equals("")` → the contents differ (one space versus nothing) → **`false`**
- `str.isEmpty()` → length is 1, not 0 → **`false`**

Measured:

```
false false
```

**Answer: `false false`.**

> [!important] **Questions 1 and 2 are the same question wearing different clothes.** Both put a `String` method call on a line by itself with no assignment. Immutability guarantees the original is untouched, so the line is dead code. Whenever you see a bare `s.something();` with no `s =` in front of it, **the string did not change** — and that is almost always the point of the question.

---

# Question 3 — `trim()` and the middle space

```java
public class Test {
    public static void main(String[] args) {
        String s = "durga soft";
        int length = s.trim().length();
        System.out.println(length);
    }
}
```

**Options:** `10` · `9` · `8` · compilation fails

## Walking it

This time the result **is** used — `trim()` feeds straight into `length()`. So the discarded-result trap is not the point here.

The point is what `trim()` removes: **blank spaces at the beginning and at the end of the string, and never the middle.**

`"durga soft"` has no leading space and no trailing space. There is exactly one space, and it sits in the middle, which `trim()` will not touch. So `trim()` finds nothing to remove and — by the no-change-means-reuse rule — **returns the same object**.

Count: `d-u-r-g-a` is 5, the space makes 6, `s-o-f-t` takes it to **10**.

Measured:

```
10
```

**Answer: `10`.** The expected wrong answer is 9, from assuming `trim()` strips every space.

---

# Question 4 — `trim()` and `indexOf`

```java
public class Test {
    public static void main(String[] args) {
        String s = "hello world";
        s.trim();
        int i1 = s.indexOf(' ');
        System.out.println(i1);
    }
}
```

**Options:** an exception is thrown at runtime · `-1` · `5` · `0`

## Walking it

Two ways to get this wrong, and the question is built to offer both.

**The reasoning that produces `-1`:** *"`trim()` removed the spaces, so `indexOf(' ')` finds none and returns −1."* Wrong twice over — `trim()`'s result was discarded **and** the space is in the middle, so it was never a candidate for removal anyway.

The string is untouched. Index the characters:

```
h  e  l  l  o     w  o  r  l  d
0  1  2  3  4  5  6  7  8  9  10
```

The space sits at index **5**.

Measured:

```
5
```

**Answer: `5`.**

---

# Question 5 — choosing the fragment that prints `equal`

```java
public class Test {
    public static void main(String[] args) {
        String s1 = "Java";
        String s2 = new String("java");

        // insert code here — line 1

        System.out.println("equal");
        else
            System.out.println("not equal");
    }
}
```

Note the contents carefully: **`s1` has a capital `J`**, `s2` is all lowercase.

**Which fragment at line 1 makes it print `equal`?**

| | Fragment |
|---|---|
| **A** | `String s3 = s2; if (s1 == s3)` |
| **B** | `if (s1.equalsIgnoreCase(s2))` |
| **C** | `String s3 = s2; if (s1.equals(s3))` |
| **D** | `if (s1.toLowerCase() == s2.toLowerCase())` |

## The setup

`s1 = "Java"` is a literal → **SCP** object.
`s2 = new String("java")` uses `new` → **heap** object (plus an SCP copy of `"java"`, which nothing here points at).

So `s1` and `s2` are in different areas with different content — different case.

## Option A — `false`

`s3 = s2` just makes a third reference to the **same heap object**. `s1 == s3` compares a pool reference with a heap reference — different objects — so `false`, and the `else` branch prints `not equal`. Measured: `not equal`.

## Option B — `true` ✅

`equalsIgnoreCase` compares **content with case ignored**. `Java` and `java` have the same letters, and the case is exactly what is being ignored, so **`true`**. Measured: `equal`.

## Option C — `false`

`equals` compares content **with case significant**. Capital `J` against lowercase `j` → `false`. Measured: `not equal`.

## Option D — `false`, and this is the interesting one

```java
if (s1.toLowerCase() == s2.toLowerCase())
```

Both sides become `"java"`, so it *looks* like it should be true. But `==` compares references, so you have to ask what object each side actually produced — which is the reuse rule from note `05`:

- **`s1.toLowerCase()`** — `s1` is `"Java"`. Lowercasing it **changes the content**, so a **new object is created in the heap**.
- **`s2.toLowerCase()`** — `s2` is already `"java"`. **No change**, so the **existing object is reused**.

Two different objects with identical content, compared with `==` → **`false`**. Measured: `not equal`.

**Answer: B.**

> [!important] **Option D is the whole chapter in one line.** It requires you to know that `==` is reference comparison, that a content-changing method creates a new object in the heap, and that a content-preserving one returns the existing object. Miss any one of those three and you answer `true`.

---

# What these five have in common

| # | The rule being tested | The trap offered |
|---|---|---|
| 1 | a discarded result changes nothing | mentally applying `replace` |
| 2 | a discarded result changes nothing | assuming `" "` is empty |
| 3 | `trim()` ignores the middle | answering 9 |
| 4 | `trim()` ignores the middle, result discarded | answering `-1` |
| 5 | `==` is reference comparison; change → new object | answering D |

> [!important] **Two habits answer four of the five.** First, whenever a `String` method is called without assigning the result, **cross the line out** — it did nothing. Second, whenever you see `==`, stop comparing contents and ask *which object is on each side.*
