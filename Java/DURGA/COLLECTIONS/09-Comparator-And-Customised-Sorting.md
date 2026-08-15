# The `Comparator` interface

| | `Comparable` | **`Comparator`** |
|---|---|---|
| **Package** | `java.lang` | **`java.util`** |
| **Methods** | **1** — `compareTo()` | **2** — `compare()` and `equals()` |
| **Meant for** | **default natural** sorting order | **customised** sorting order |

Confirmed on JDK 25: `Comparator` is in `java.util` and declares `compare` and `equals`.

## The two methods

```java
public int compare(Object obj1, Object obj2)
public boolean equals(Object obj)
```

**`compare()` has exactly the same three-way contract as `compareTo()`** — which is why note `08`
spent so long on it:

| Returns | Meaning |
|---|---|
| **negative** | `obj1` has to come **before** `obj2` |
| **positive** | `obj1` has to come **after** `obj2` |
| **zero** | `obj1` and `obj2` are **equal** |

## You only implement one of them

```java
class MyComparator implements Comparator {
    public int compare(Object obj1, Object obj2) { … }
    // no equals() — and that is legal
}
```

Normally implementing an interface means implementing **every** method. Here you implement only
`compare()`.

> **We are not required to provide an implementation for `equals()` because it is already available to
> our class from the `Object` class, through inheritance.**

**No rule is being violated.** `MyComparator` is a child of `Object`, `Object` already has `equals()`,
so the inherited version satisfies the interface. The only method genuinely left unimplemented is
`compare()`.

> [!info] **This is the marker-interface reasoning from `DECLARATIONS-AND-ACCESS-MODIFIERS/13` in
> reverse.** There, an interface declared nothing and a class satisfied it trivially. Here, an
> interface declares something that `Object` already provides — so the class satisfies half of it
> without writing a line. **Declaring `equals()` in `Comparator` is documentation**, telling
> implementers that equality matters for consistency; it imposes no work.

> [!important] **`Comparator` is a functional interface.** Confirmed on JDK 25 — it carries
> `@FunctionalInterface`, precisely because `equals()` is inherited from `Object` and therefore does
> not count towards the single-abstract-method rule. **That is exactly the "non-overriding abstract
> method" wording from `JAVA-8-FEATURES/02`**, and it means every comparator in this note can be
> written as a lambda:
> ```java
> new TreeSet<>((i1, i2) -> i2.compareTo(i1));
> ```

---

# The worked example

> **Write a program to insert integer objects into a `TreeSet` where the sorting order is descending
> order.**

Default natural sorting order for numbers is **ascending**. We want the opposite.

```java
import java.util.*;

class TreeSetDemo3 {
    public static void main(String[] args) {
        TreeSet t = new TreeSet(new MyComparator());     // ← line 1
        t.add(10);
        t.add(0);
        t.add(15);
        t.add(5);
        t.add(20);
        t.add(20);
        System.out.println(t);
    }
}

class MyComparator implements Comparator {
    public int compare(Object obj1, Object obj2) {
        Integer i1 = (Integer) obj1;
        Integer i2 = (Integer) obj2;
        if (i1 < i2)       return +1;
        else if (i1 > i2)  return -1;
        else               return 0;
    }
}
```

Measured on JDK 25:

```
[20, 15, 10, 5, 0]
```

## Line 1 is the whole switch

| At line 1 | The JVM calls | Which means | Output |
|---|---|---|---|
| **no comparator object** | **`compareTo()`** | default natural sorting order | `[0, 5, 10, 15, 20]` |
| **a comparator object** | **`compare()`** | customised sorting order | `[20, 15, 10, 5, 0]` |

> [!important] **Passing a `Comparator` redirects which method the JVM calls.** That is the entire
> mechanism. `compareTo()` lives on the *element* and gives one fixed order; `compare()` lives on a
> *separate object you supply* and gives whatever order you write. **You cannot change `Integer`'s
> `compareTo`, but you can always supply a comparator.**

## Why the logic is "backwards"

The body reads oddly at first — `if (i1 < i2) return +1`.

**Work it through.** We want descending order. If `i1` is **smaller** than `i2`, then in descending
order the smaller one must come **later**. "Later" means **positive**. So a smaller value returns a
positive number.

> [!question]- **Deep dive — the full insertion trace, element by element.** Follow this once and the
> mechanism stops being mysterious.
>
> Inserting `10, 0, 15, 5, 20, 20` with the comparator above:
>
> **`add(10)`** — first element, nothing to compare against, inserted.
>
> **`add(0)`** → `compare(0, 10)`. `i1=0`, `i2=10`. `0 < 10` → **return +1** → positive → **0 goes
> after 10**.
> ```
> 10 → 0
> ```
>
> **`add(15)`** → `compare(15, 10)`. `15 > 10` → **return −1** → negative → **15 goes before 10**.
> ```
> 15 → 10 → 0
> ```
>
> **`add(5)`** → `compare(5, 10)`. `5 < 10` → **+1** → after 10. But 0 is already there, so compare
> again: `compare(5, 0)`. `5 > 0` → **−1** → before 0.
> ```
> 15 → 10 → 5 → 0
> ```
>
> **`add(20)`** → `compare(20, 10)` → `20 > 10` → **−1** → before 10. 15 is there, so
> `compare(20, 15)` → **−1** → before 15.
> ```
> 20 → 15 → 10 → 5 → 0
> ```
>
> **`add(20)` again** → `compare(20, 10)` → −1 → before. `compare(20, 15)` → −1 → before.
> `compare(20, 20)` → **0** → **duplicate, rejected.**
>
> **Reading the balanced tree left-root-right (in-order traversal) gives `20 15 10 5 0`.**
>
> Note that the comparator is consulted **repeatedly** for a single insertion — once per level of the
> tree — which is why an expensive `compare()` costs more than you might expect.

---

# The JVM is a blind person

The single most useful idea in this session:

> **The JVM is a blind person. Whatever you return, it acts on. If your `compare()` returns negative,
> it places your element before. If positive, after. If zero, it treats it as a duplicate and does not
> insert. Whether the elements are *really* duplicates or *really* greater is not its concern — that is
> your job.**

**This is why the pathological implementations below behave the way they do**, and why they are worth
running.

---

# Various possible implementations of `compare()`

All measured on JDK 25, inserting `10, 0, 15, 5, 20, 20` every time.

| # | `compare()` body | Output |
|---|---|---|
| 1 | *no comparator at all* | `[0, 5, 10, 15, 20]` |
| 2 | `if (i1<i2) +1; else if (i1>i2) -1; else 0` | `[20, 15, 10, 5, 0]` |
| 3 | `return i1.compareTo(i2);` | `[0, 5, 10, 15, 20]` |
| 4 | `return -i1.compareTo(i2);` | `[20, 15, 10, 5, 0]` |
| 5 | `return i2.compareTo(i1);` | `[20, 15, 10, 5, 0]` |
| 6 | `return -i2.compareTo(i1);` | `[0, 5, 10, 15, 20]` |
| 7 | `return +1;` | `[10, 0, 15, 5, 20, 20]` |
| 8 | `return -1;` | `[20, 20, 5, 15, 0, 10]` |
| 9 | `return 0;` | `[10]` |

## Rows 3 to 6 — the two ways to reverse

**Row 3** does by hand exactly what the JVM would have done anyway, so it gives the default order.

**There are two independent ways to flip it, and they cancel:**

- **Row 4** — negate the result. Every `before` becomes `after`.
- **Row 5** — swap the arguments. Asking "where does `i2` go relative to `i1`" is the mirror question.
- **Row 6** — do **both**, and you are back where you started. **Two reversals = the original order.**

> [!important] **Row 4 is the idiom worth remembering: `return -i1.compareTo(i2);`** It is one line,
> it works for any comparable type, and it reads as *"the opposite of natural order."* Compare it with
> row 2 — six lines of `if`/`else` for the identical result.
>
> Modern Java has an even shorter form: **`Comparator.reverseOrder()`**, or `c.reversed()` on any
> existing comparator.

## Rows 7 to 9 — the dangerous ones

These are what "the JVM is blind" actually means.

**Row 7 — `return +1`.** Every new element is reported as belonging *after* everything. Nothing is ever
equal, so **nothing is ever rejected as a duplicate**:

```
[10, 0, 15, 5, 20, 20]
```

**Both 20s are present, and the order is insertion order.** A `TreeSet` that keeps duplicates and does
not sort — because you told it to.

**Row 8 — `return -1`.** Every element goes *before* everything:

```
[20, 20, 5, 15, 0, 10]
```

**Reverse of insertion order**, duplicates again preserved.

**Row 9 — `return 0`.** Every element after the first is reported as equal to what is already there:

```
[10]
```

**Only the first element survives. Everything else is discarded as a duplicate.**

> [!warning] **A `Comparator` inconsistent with `equals()` breaks the collection's guarantees, and you
> get no warning.** Rows 7–9 are not errors — they compile, they run, and they silently produce a
> `TreeSet` that violates the two things a `TreeSet` promises: no duplicates, and sorted order.
>
> **The requirement the JDK documents is that `compare()` must be a *total order*:** consistent
> (`compare(a,b)` always gives the same answer), antisymmetric (`compare(a,b)` and `compare(b,a)` have
> opposite signs), and transitive. Rows 7 and 8 fail antisymmetry — `compare(a,b)` and `compare(b,a)`
> both return `+1`. Row 9 claims everything is equal.
>
> **This is a real bug in production code**, usually written as a `compare()` that forgets a case and
> returns a constant on the fallthrough path.

---

# `Comparable` vs `Comparator` — the comparison table

The interview question this session exists to answer:

| | `Comparable` | `Comparator` |
|---|---|---|
| **Package** | `java.lang` | `java.util` |
| **Meant for** | **default natural** sorting order | **customised** sorting order |
| **Methods** | **1** — `compareTo(obj)` | **2** — `compare(obj1, obj2)` and `equals(obj)` |
| **Must implement** | `compareTo()` | **only `compare()`** — `equals()` comes from `Object` |
| **Who implements it** | **the element class itself** | **a separate class** you write |
| **How many orderings** | **one** per class | **as many as you like** |
| **How the JVM uses it** | called when **no** comparator is supplied | called when a comparator **is** supplied |

> [!important] **The deepest difference is the last-but-one row.** `Comparable` is baked into the
> element's own class — one class, one ordering, and you cannot have two. `Comparator` is a separate
> object, so **you can write ten of them for the same class** and choose per collection: sort employees
> by name here, by salary there, by joining date somewhere else.
>
> That is also why you cannot make `String` sort case-insensitively by changing `Comparable` — you
> would have to modify `java.lang.String`. You supply a comparator instead, and the JDK ships one:
> `String.CASE_INSENSITIVE_ORDER`.

---

# What this part established

| | |
|---|---|
| `Comparator` package | **`java.util`** (`Comparable` is `java.lang`) |
| `Comparator` methods | **`compare()`** and **`equals()`** |
| You implement | **only `compare()`** |
| Why `equals()` is free | inherited from **`Object`** |
| `Comparator` is a | **functional interface** — usable as a lambda |
| `compare()` contract | negative → **before** · positive → **after** · zero → **equal** |
| Passing a comparator | switches the JVM from `compareTo()` to **`compare()`** |
| No comparator | **default natural** order — ascending for numbers |
| **The JVM is blind** | it acts on your return value; correctness is **your** job |
| `-i1.compareTo(i2)` | **reverses** the order — the one-line idiom |
| `i2.compareTo(i1)` | also reverses — **swapping arguments** is the other way |
| Doing both | **cancels** — back to the original order |
| `return +1` | insertion order, **duplicates kept** |
| `return -1` | **reverse** insertion order, duplicates kept |
| `return 0` | **only the first element** survives |
| Why those three are dangerous | they break **antisymmetry / totality** with no warning |
| `Comparable` | **one** ordering, in the element's own class |
| `Comparator` | **many** orderings, in separate classes |
