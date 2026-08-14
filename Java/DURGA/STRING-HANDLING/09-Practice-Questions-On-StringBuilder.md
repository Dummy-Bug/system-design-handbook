Five certification-style questions on `StringBuilder`. These lean on the parts of the chapter that are easiest to half-remember — `equals()` not being overridden outside `String`, where an object gets created, and what `toString()` does when you have not written one.

All outputs measured on JDK 25.

---

# Question 1 — `equals()` on a `StringBuilder`

```java
public class Test {
    public static void main(String[] args) {
        StringBuilder sb = new StringBuilder(5);
        String s = "";

        if (sb.equals(s))
            System.out.println("match one");
        else if (sb.toString().equals(s.toString()))
            System.out.println("match two");
        else
            System.out.println("no match");
    }
}
```

**Options:** `match one` · `match two` · `no match` · a `NullPointerException` is thrown at runtime

## The knowledge needed

Straight from note `01`: **`equals()` is overridden for content comparison in `String` and nowhere else.** `StringBuffer` did not override it, and since `StringBuilder` is `StringBuffer` with `synchronized` removed, **`StringBuilder` did not either**. So calling `equals()` on a builder runs **`Object`'s** version — reference comparison.

One more detail about `Object.equals()`: if the two arguments are of **different types** it can only return `false`, because they cannot possibly be the same object.

## Walking it

`new StringBuilder(5)` creates an **empty** builder — the `5` is a capacity, not content. `s` is an empty `String`.

**First condition** — `sb.equals(s)`. `sb` is a `StringBuilder`, which has no `equals()` of its own, so `Object.equals()` runs. A `StringBuilder` and a `String` are different objects of different types → **`false`**. The `if` branch is skipped.

**Second condition** — `sb.toString().equals(s.toString())`.
`sb.toString()` produces an empty **`String`**. `s.toString()` on a `String` returns the same object. Now `equals()` is being called **on a `String`**, so **`String`'s** overridden version runs — content comparison. Empty content against empty content → **`true`**.

Measured:

```
false        (sb.equals(s))
true         (sb.toString().equals(s.toString()))
```

**Answer: `match two`.**

> [!important] **The one-line takeaway.** `.equals()` does content comparison **only when the object on the left is a `String`.** Left-hand side is a `StringBuilder` or `StringBuffer` → reference comparison, and almost always `false`. Calling `.toString()` first is what switches it back on.

---

# Question 2 — making `==` print `true`

```java
public class Test {
    public static void main(String[] args) {
        StringBuilder sb1 = new StringBuilder("durga");
        String str1 = sb1.toString();

        // insert code here — line 1

        System.out.println(str1 == str2);
    }
}
```

**Which fragment at line 1 makes it print `true`?**

| | Fragment |
|---|---|
| **A** | `String str2 = str1;` |
| **B** | `String str2 = new String(str1);` |
| **C** | `String str2 = sb1.toString();` |
| **D** | `String str2 = "durga";` |

## The setup

`sb1.toString()` is a **runtime operation** that produces a new object — and by the rule from note `02`, a runtime operation's result goes **in the heap**, never the SCP. So `str1` points to a **heap** object holding `durga`.

`==` is reference comparison, so the question is only ever: **does `str2` end up pointing at that same heap object?**

## Option A — `true` ✅

`String str2 = str1;` copies the **reference**. No new object; `str2` points at the very object `str1` points at. Measured: `true`.

## Option B — `false`

`new` **always** creates a new heap object. Same content, different object. Measured: `false`.

## Option C — `false`

Calling `sb1.toString()` a **second time** runs the operation again, producing **another** new heap object. Two `toString()` calls give two objects. Measured: `false`.

## Option D — `false`

`"durga"` is a literal, so `str2` points into the **SCP**. `str1` points into the **heap**. Different areas, different objects. Measured: `false`.

**Answer: A.**

> [!important] **Three of the four options create a new object, and only one copies a reference.** That is the entire question. When you see `==` between two `String` references, trace where each object came from — `new`, a method call, and a literal all land in different places.

---

# Question 3 — emptying a `StringBuilder`

**Which statement empties a `StringBuilder` variable named `sb`?**

| | Statement |
|---|---|
| **A** | `sb.deleteAll();` |
| **B** | `sb.delete(0, sb.size());` |
| **C** | `sb.delete(0, sb.length());` |
| **D** | `sb.removeAll();` |

## Eliminating three of them

This is really an API-recall question, and three options name methods that do not exist. Measured on JDK 25:

```
sb.deleteAll()            error: cannot find symbol   symbol: method deleteAll()
sb.delete(0, sb.size())   error: cannot find symbol   symbol: method size()
sb.removeAll()            error: cannot find symbol   symbol: method removeAll()
```

- **A** — there is no `deleteAll()`.
- **B** — `delete()` is fine, but **`size()` is not a `StringBuilder` method.** It has `length()` and `capacity()`. `size()` belongs to **collections**.
- **D** — `removeAll()` is also a collections method, not a `StringBuilder` one.

## Why C works

`delete(begin, end)` removes from `begin` to **`end − 1`**.

Take `durga` — five characters, so `sb.length()` is 5. The call becomes `delete(0, 5)`, which removes indices 0 to **4** — every character.

```
d  u  r  g  a
0  1  2  3  4     ← all removed
```

Measured afterwards: `sb.length()` is `0`. The builder is genuinely empty.

**Answer: C.**

> [!info] **The `size()` versus `length()` confusion is deliberate.** `size()` is the method on collections, `length` is the *variable* on arrays, and `length()` is the *method* on `String`, `StringBuffer` and `StringBuilder`. Three similar names across three families, and exams mix them on purpose. Note `04` covers the array-versus-`String` half of the same trap.

---

# Question 4 — `toString()` and what happens without it

```java
class MyString {
    String msg;
    MyString(String msg) {
        this.msg = msg;
    }
}

public class Test {
    public static void main(String[] args) {
        System.out.println("hello " + new StringBuilder("JavaSE8"));
        System.out.println("hello " + new MyString("JavaSE8"));
    }
}
```

**Options include:** both lines printing `hello JavaSE8` · the first meaningful and the second showing a class name and hash code · compilation fails

## The knowledge needed

> Whenever we try to print any **object reference**, `toString()` is called internally.

So `System.out.println(t1)` becomes `System.out.println(t1.toString())`. Then:

- If **your class defines `toString()`**, yours runs.
- If it does **not**, **`Object`'s** runs — and that one always prints **`classname@hashcode`**, with the hash code in hexadecimal.

**And the same applies to concatenation.** `"hello " + t1` is `String + Object`, so `toString()` is called on the object and the two strings are joined.

## Walking it

**Line 1** — `new StringBuilder("JavaSE8")`. In `String`, `StringBuffer`, `StringBuilder`, all wrapper classes and all collection classes, **`toString()` is already overridden** for a meaningful representation. So the builder's own version runs and returns its content.

**Line 2** — `new MyString("JavaSE8")`. Look at `MyString`: it has a field and a constructor and **no `toString()`**. So `Object`'s runs, giving the class name and hash code.

Measured on JDK 25:

```
hello JavaSE8
hello MyString@7ad041f3
```

**Answer: the first line meaningful, the second `classname@hashcode`.** The hash code differs from run to run; only its shape matters.

## Fixing `MyString`

Adding the method changes the second line completely:

```java
class MyString {
    String msg;
    MyString(String msg) {
        this.msg = msg;
    }

    public String toString() {
        return msg;
    }
}
```

Measured after the change:

```
hello JavaSE8
hello JavaSE8
```

> [!important] **The general recommendation.** For a meaningful string representation it is **highly recommended to override `toString()` in your own classes.** Every JDK class you print happily already does — `String`, `StringBuffer`, `StringBuilder`, the wrappers, the collections. When your own class prints as `MyString@7ad041f3`, that is `Object`'s version telling you nobody wrote one.

---

# Question 5 — masking a credit card number

A banking use case, and the most realistic question in the chapter.

```java
class MaskTest {
    public static String mask(String creditCard) {
        String x = "xxxx-xxxx-xxxx-";

        // insert code here — line 1
    }

    public static void main(String[] args) {
        System.out.println(mask("1234-5678-9101-5979"));
    }
}
```

**The requirement:** hide every digit **except the last four**, keeping the hyphens that separate each group.

So `1234-5678-9101-5979` must come out as `xxxx-xxxx-xxxx-5979`.

**Which two fragments at line 1 achieve this?**

| | Fragment |
|---|---|
| **A** | `StringBuilder sb = new StringBuilder(creditCard);`<br/>`sb.substring(15, 19);`<br/>`return x + sb;` |
| **B** | `return x + creditCard.substring(15, 19);` |
| **C** | `StringBuilder sb = new StringBuilder(x);`<br/>`sb.append(creditCard, 15, 19);`<br/>`return sb.toString();` |
| **D** | `StringBuilder sb = new StringBuilder(creditCard);`<br/>`StringBuilder s = sb.insert(0, x);`<br/>`return s.toString();` |

Note the indices: in `1234-5678-9101-5979`, positions 15 to 18 are the final `5979`, so `substring(15, 19)` selects exactly the last four digits.

## Option A — fails

`sb.substring(15, 19)` **does** extract `5979` — but the result is **assigned to nothing**. That object is discarded and eligible for garbage collection, while `sb` still holds the complete card number. So `x + sb` produces the mask *followed by every digit*.

Measured:

```
xxxx-xxxx-xxxx-1234-5678-9101-5979
```

This is the discarded-result trap from note `06`, transplanted into a realistic-looking method.

## Option B — works ✅

```java
return x + creditCard.substring(15, 19);
```

`creditCard.substring(15, 19)` returns `5979`, and the result **is used** — it goes straight into the concatenation. Measured:

```
xxxx-xxxx-xxxx-5979
```

## Option C — works ✅

Builds from the other end: start a `StringBuilder` holding the mask, then append only the wanted slice.

`append(CharSequence, int start, int end)` appends characters from `start` to `end − 1` — the same exclusive-end convention.

Measured:

```
xxxx-xxxx-xxxx-5979
```

## Option D — fails

`sb.insert(0, x)` puts the mask at the **front** of the full card number rather than replacing anything. Nothing is hidden. Measured:

```
xxxx-xxxx-xxxx-1234-5678-9101-5979
```

Same output as A, by a different mistake.

**Answer: B and C.**

> [!important] **A and D fail for opposite reasons, and both are instructive.** **A** does the right extraction and throws it away. **D** keeps everything and merely prefixes it. Only B and C ever discard the digits that were supposed to be hidden — and in a real masking function, "the sensitive data is still in the returned string" is precisely the bug that matters.

---

# What these five have in common

| # | The rule being tested | The trap offered |
|---|---|---|
| 1 | `equals()` is overridden only in `String` | assuming content comparison everywhere |
| 2 | `==` is reference comparison; `new` and method calls create objects | assuming equal content means equal reference |
| 3 | `length()` versus `size()` | reaching for the collections method |
| 4 | `toString()` is called when printing; `Object`'s prints `classname@hashcode` | expecting a meaningful output without writing one |
| 5 | a discarded result changes nothing | option A looking like it does the work |

> [!important] **Question 5 is question 1 of note `06` in a suit.** `sb.substring(15, 19);` on its own line is the same dead statement as `ta.replace('c','d');` — the operation runs, produces the right value, and nobody catches it. Across both practice files that single pattern accounts for three of the ten questions, which makes it the single most valuable habit in the chapter: **if the result is not assigned or used, cross the line out.**
