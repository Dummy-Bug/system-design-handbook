# The interview question: `ArrayList` vs `LinkedList`

Both are `List` implementations, so almost everything is the same — and that is the trap.

> [!warning] **Do not answer with the similarities.** *"In both cases duplicates are allowed, in both
> cases insertion order is preserved"* — **those are similarities, not differences.** Heterogeneous
> objects allowed, `null` insertion possible: also both. Answering with any of these means you have
> not answered the question.

**The real difference is which operation each one is good at**, and it follows entirely from how each
stores its elements.

| | `ArrayList` | `LinkedList` |
|---|---|---|
| **1. Best choice** | frequent **retrieval** | frequent **insertion or deletion in the middle** |
| **2. Worst choice** | frequent **insertion or deletion in the middle** — several **shift** operations | frequent **retrieval** |
| **3. Memory layout** | elements **are** stored in consecutive memory locations | elements are **not** stored in consecutive memory locations |
| **4. Data structure** | **resizable array** | **doubly linked list** |

> [!important] **Row 3 causes rows 1 and 2, and that is the answer worth giving.** Consecutive storage
> means the address of element *n* is computable, so retrieval is instant but making room requires
> shifting. Non-consecutive storage means nothing has to move when you insert, but finding element *n*
> means walking there one node at a time.
>
> Give row 3 first and rows 1–2 follow as consequences. Give rows 1–2 alone and it sounds memorised.

---

# `Vector`

The third `List` implementation.

| | |
|---|---|
| **Underlying data structure** | **resizable array** — same as `ArrayList` |
| **Duplicates** | ✅ allowed |
| **Insertion order** | ✅ preserved |
| **Heterogeneous objects** | ✅ allowed |
| **`null` insertion** | ✅ possible |
| **Implements** | `Serializable`, `Cloneable`, **`RandomAccess`** |
| **Every method** | **synchronized** → the object is **thread safe** |

> **Every property is identical to `ArrayList` except the last one.** That single row — synchronized,
> and therefore thread safe, and therefore slower — is the whole difference, and it is what note `04`'s
> comparison table was about.

## The four constructors

`Vector` stores elements consecutively, so **capacity is meaningful** here — unlike `LinkedList`,
which had no capacity constructor for exactly that reason.

```java
Vector v = new Vector();                    // 1 — default initial capacity 10
Vector v = new Vector(int initialCapacity); // 2
Vector v = new Vector(int initialCapacity, int incrementalCapacity);   // 3
Vector v = new Vector(Collection c);        // 4 — inter-conversion
```

## How `Vector` grows — and it is not `ArrayList`'s rule

> **Once a `Vector` reaches its max capacity, a new object is created with
> new capacity = current capacity × 2.**

Measured on JDK 25:

```
initial capacity      = 10
after 10 elements     = 10
after 11th element    = 20
after 21 elements     = 40
```

**10 → 20 → 40 → 80.** Simple doubling.

> [!important] **Do not carry one growth formula across the whole framework.** `ArrayList` grows by
> **1.5×**; `Vector` **doubles**. *"Don't think everywhere the same formula is going to be applicable —
> the data structure differs, so the formula may change."* Two classes with the same underlying data
> structure and different growth policies is exactly the kind of detail an interviewer uses to check
> whether you have actually looked.

## The third constructor — controlling the increment

**Why it exists.** You create a `Vector` with capacity 1000, fill it, and add one more. It jumps to
**2000** — and if you only ever needed 1003, nearly a thousand slots are wasted.

```java
Vector v = new Vector(1000, 5);    // grow by 5 at a time, not by doubling
```

Measured on JDK 25 with `new Vector(10, 5)`:

```
initial  = 10
after 10 = 10
after 11 = 15
```

**15, not 20.** The increment replaced the doubling.

> [!important] **`ArrayList` has no equivalent.** It always follows its own growth rule, and there is
> no way to specify an increment. **This is a genuine `Vector`-only feature** and a fair answer to
> *"is there anything `Vector` can do that `ArrayList` cannot?"*

## `capacity()` — and why only `Vector` has it

`Vector` exposes `capacity()`, so all of the above can be printed. `ArrayList` does not, which is why
its growth had to be measured by reflection in note `03`.

> [!info] **His explanation for the asymmetry, and it is a good one.** *"Being a Java programmer we
> are never going to worry about memory-level things, because Java is a high-level programming
> language, not low level. If you want to talk with respect to memory, don't come to Java — better to
> go for C."*
>
> `Vector` came from **1.0**, when that line had not been drawn as firmly. By 1.2, the framework's
> designers decided a Java programmer should not need to think about capacity at all, so `ArrayList`
> simply does not offer it.

## Why `Vector`'s method names are so long

`Vector` has its own name for almost everything `Collection` and `List` already provide:

| Purpose | `Collection` / `List` | **`Vector`** |
|---|---|---|
| add an object | `add(o)` | **`addElement(o)`** |
| remove an object | `remove(o)` | **`removeElement(o)`** |
| remove by index | `remove(int)` | **`removeElementAt(int)`** |
| remove everything | `clear()` | **`removeAllElements()`** |
| get by index | `get(int)` | **`elementAt(int)`** |
| get the first | — | **`firstElement()`** |
| get the last | — | **`lastElement()`** |
| a cursor | `iterator()` | **`elements()`** — returns an `Enumeration` |

> [!question]- **The generational analogy he uses to explain the long names.** Not technical, and it
> makes the naming impossible to forget.
>
> **Our own names are short** — two or three syllables. Ravi, Shiva, Pavan.
>
> **Our parents' generation had longer ones** — four or five syllables.
>
> **Their parents' generation, longer still.** *"No one is going to pronounce it as Nageshwara —
> everyone is going to pronounce it as Nageshwara Rao."*
>
> And further back, in the time of kings: when a king entered the hall, the herald announced titles
> for half an hour before the actual name arrived. **A lengthy name signalled that you were a person of
> importance** — that was the trend. Old films did the same thing with their titles.
>
> **The next generation goes the other way** — down to two letters. And the one after that, to
> initials.
>
> **`Vector` is from 1.0 — 1995, the old generation — so it has old-generation names.** `addElement`,
> `removeAllElements`, `elementAt`. The collection framework arrived in 1.2, by which time the style
> had changed to `add`, `clear`, `get`.

## The capacity demo

```java
import java.util.*;

class VectorDemo {
    public static void main(String[] args) {
        Vector v = new Vector();
        System.out.println(v.capacity());          // 10
        for (int i = 1; i <= 10; i++) v.addElement(i);
        System.out.println(v.capacity());          // 10
        v.addElement("A");
        System.out.println(v.capacity());          // 20
        System.out.println(v);
    }
}
```

Measured on JDK 25:

```
10
10
20
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, A]
```

**The capacity stays at 10 for the tenth element and only grows on the eleventh** — the array is full
at ten, so the eleventh is what forces the new array.

> [!info] **`addElement(i)` takes an `Object`, and `i` is an `int`.** It works because of
> **autoboxing** — the primitive becomes an `Integer` and the `Integer` goes into the vector. That is
> `JAVA-LANG-PACKAGE/10` doing its job silently.

---

# `Stack`

> **`Stack` is the child class of `Vector`. It is a specially designed class for last-in-first-out
> (LIFO) order.**

**Every `Vector` property is inherited** — resizable array, duplicates, insertion order, heterogeneous,
`null`, synchronized, default capacity 10. Confirmed on JDK 25: a new `Stack` reports
`capacity() == 10`.

## One constructor

```java
Stack s = new Stack();
```

Confirmed on JDK 25: `Stack` has exactly **1** public constructor.

## Five specific methods

| Method | What it does |
|---|---|
| `Object push(Object o)` | insert an object onto the stack |
| `Object pop()` | **remove and return** the top of the stack |
| `Object peek()` | **return** the top of the stack **without removal** |
| `boolean empty()` | is the stack empty? |
| `int search(Object o)` | returns the **offset** if present, otherwise **−1** |

> [!important] **`empty()` and `isEmpty()` both exist and are not the same method.** `isEmpty()` comes
> from `Collection`; **`empty()` is `Stack`'s own.** They return the same answer here, but only
> `empty()` is a "stack specific method" if the question asks for the five.

## Offset is not index

**This is the point of the `search` method**, and the distinction is the examinable part.

```
push A, then B, then C

              index    offset
   C    ←top     2        1
   B             1        2
   A             0        3
```

> **Index counts from the bottom, starting at 0. Offset counts from the top of the stack, starting
> at 1.**

Measured on JDK 25:

```
println(s)   = [A, B, C]
search(A)    = 3
search(C)    = 1
search(Z)    = -1
peek()       = C
```

## The demo, and the line that catches people

```java
import java.util.*;

class StackDemo {
    public static void main(String[] args) {
        Stack s = new Stack();
        s.push("A");
        s.push("B");
        s.push("C");
        System.out.println(s);
        System.out.println(s.search("A"));
        System.out.println(s.search("Z"));
    }
}
```

Measured on JDK 25:

```
[A, B, C]
3
-1
```

> [!important] **Printing a `Stack` gives `[A, B, C]`, not `[C, B, A]`.** People expect `C, B, A`
> because a stack is last-in-first-out — but **LIFO describes the removal order, not the storage
> order.** `Stack` extends `Vector` extends `List`, so **insertion order is preserved** and `toString()`
> reports it. It is `pop()` that gives you `C`, then `B`, then `A`.

> [!warning] **Do not use `Stack` in new code.** It is legacy, it is synchronized on every method, and
> it extends `Vector` — which means it also exposes `add(int, Object)` and `get(int)`, so anyone can
> reach into the middle of your "stack". **`ArrayDeque` is the modern answer**, with `push`, `pop` and
> `peek` and no way to violate the discipline.

---

# The three cursors

> **If we want to get objects one by one from a collection, then we should go for a cursor.**

> [!info] **The box of mangoes.** *"Assume I'm giving a box of mangoes to you. Are you going to eat
> these mangoes one by one, or all mangoes simultaneously?"* — *"open your mouth, keep your head there,
> and after all the mangoes your head is coming out"* is not how anybody eats.
>
> **You take one, finish it, take the next.** The box is the collection; the mangoes are the objects;
> **the cursor is what hands you one at a time.**

> **There are three types of cursors available in Java:**
> **1.** `Enumeration`  **2.** `Iterator`  **3.** `ListIterator`

---

# Cursor 1 — `Enumeration`

## Why you need one at all

```java
Vector v = new Vector();
for (int i = 0; i <= 10; i++) v.addElement(i);
System.out.println(v);
```

```
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

**That prints everything.** But suppose you only want the even numbers. Then you must take the first
object, test it, print or ignore, take the second, test it — **one at a time.** That is the
requirement a cursor exists for.

## Getting one, and using it

`Enumeration` is obtained from `Vector`'s `elements()` method:

```java
Enumeration e = v.elements();

while (e.hasMoreElements()) {
    Integer i = (Integer) e.nextElement();
    if (i % 2 == 0)
        System.out.println(i);
}
```

Measured on JDK 25:

```
evens = 0 2 4 6 8 10
whole vector still = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

**Two methods, and that is all `Enumeration` has:**

| Method | |
|---|---|
| `boolean hasMoreElements()` | are there more? |
| `Object nextElement()` | give me the next one |

> [!info] **The cast is required because `nextElement()` returns `Object`.** `Enumeration` predates
> generics — it is from 1.0 — so everything comes back as `Object` and you cast on the way out. This
> is the type-safety problem from `GENERICS/01`, met in the wild.

> [!important] **Reading through a cursor does not consume the collection.** After the loop, the
> vector still contains all eleven elements. The cursor is a *pointer walking over* the data, not a
> queue you drain.

**The limitations of `Enumeration` — and why two more cursors exist — are the next session.**

---

# What this part established

| | |
|---|---|
| `ArrayList` vs `LinkedList` — the trap | duplicates, insertion order, heterogeneous, `null` are **similarities** |
| The real difference | **consecutive memory** vs **not**, which causes best/worst case |
| `ArrayList` | best at **retrieval**, worst at **middle insert/delete** |
| `LinkedList` | best at **middle insert/delete**, worst at **retrieval** |
| `Vector` properties | identical to `ArrayList` **except** every method is **synchronized** |
| `Vector` constructors | **four** — including `(initialCapacity, incrementalCapacity)` |
| `Vector` growth | **doubles** — 10 → 20 → 40 |
| `ArrayList` growth | **1.5×** — a different rule for the same data structure |
| The increment constructor | **`Vector` only**; `ArrayList` has no equivalent |
| `capacity()` | exists on `Vector`, **not** on `ArrayList` — Java hides memory detail by design |
| `Vector`'s long method names | `addElement`, `removeElementAt`, `removeAllElements`, `elementAt` — **1.0 naming** |
| `Stack` | child of **`Vector`**, designed for **LIFO**, **one** constructor |
| `Stack`'s five methods | `push` · `pop` · `peek` · `empty` · `search` |
| `pop` vs `peek` | **remove and return** vs **return without removal** |
| **offset** | counts from the **top**, starting at **1** — index counts from the bottom, from 0 |
| `search` returns | the **offset**, or **−1** if absent |
| Printing a `Stack` | **insertion order** `[A, B, C]` — LIFO governs removal, not storage |
| A cursor is for | getting objects **one by one** from a collection |
| The three cursors | **`Enumeration`** · **`Iterator`** · **`ListIterator`** |
| `Enumeration` is obtained from | **`Vector.elements()`** |
| `Enumeration`'s two methods | `hasMoreElements()` · `nextElement()` |
| `nextElement()` returns | **`Object`** — a cast is required |
