# `SortedMap`

> **`SortedMap` is the child interface of `Map`. If we want to represent a group of key–value pairs
> according to some sorting order of keys, then we should go for `SortedMap`.**

> [!important] **Sorting is based on the key, never on the value.** This is the same rule as
> `SortedSet` in note `07`, and it is the one people forget. The values are along for the ride.

## The six specific methods

**Exactly the `SortedSet` methods from note `07`, renamed for maps.** Take this sorted map:

```
{101=A, 103=B, 104=C, 107=D, 125=E, 136=F}
```

| Method | Returns | On this map |
|---|---|---|
| `Object firstKey()` | the **first key** | `101` |
| `Object lastKey()` | the **last key** | `136` |
| `SortedMap headMap(Object key)` | entries whose keys are **less than** `key` | `headMap(107)` → `{101=A, 103=B, 104=C}` |
| `SortedMap tailMap(Object key)` | entries whose keys are **≥** `key` | `tailMap(107)` → `{107=D, 125=E, 136=F}` |
| `SortedMap subMap(Object k1, Object k2)` | keys **≥ `k1` and < `k2`** | `subMap(103, 125)` → `{103=B, 104=C, 107=D}` |
| `Comparator comparator()` | the underlying sorting technique | `null` for default natural order |

All measured on JDK 25.

> [!important] **The same boundary rules as `SortedSet`, and they are still asymmetric.**
> **`headMap` excludes** its argument, **`tailMap` includes** it, and **`subMap` includes the start and
> excludes the end.** If you learned them for `SortedSet`, you already know them here — only the method
> names gained `Map` instead of `Set`.

> [!info] **`firstKey()` / `lastKey()` rather than `first()` / `last()`.** The name says *key* because
> that is what is returned — not the entry, and not the value. To get the value you still have to
> `get()` it.

---

# `TreeMap`

| | |
|---|---|
| **Underlying data structure** | **red-black tree** |
| **Insertion order** | ❌ not preserved — by **sorting order of keys** |
| **Duplicate keys** | ❌ not allowed |
| **Duplicate values** | ✅ allowed |
| **Sorting** | **default natural** or **customised** |

> [!info] **A red-black tree is a self-balancing binary search tree.** "Balanced tree" was the answer
> given for `TreeSet` in note `08`; red-black is the specific kind. The colouring is a bookkeeping
> trick that keeps the tree from degenerating into a list, guaranteeing **O(log n)** lookup, insert and
> delete. **`TreeSet` is implemented on top of `TreeMap`**, which is why the two chapters read the same.

## Keys are restricted; values are not

> **If we are depending on default natural sorting order, the keys should be homogeneous and
> comparable, otherwise we will get a `ClassCastException`.**
>
> **If we are defining our own sorting by `Comparator`, then the keys need not be homogeneous and
> comparable** — we can take heterogeneous, non-comparable objects.

> **Whether we are depending on default natural sorting order or customised sorting order, there are
> no restrictions for values.** Heterogeneous, non-comparable — no problem at all.

Measured on JDK 25:

```
heterogeneous keys    -> ClassCastException
heterogeneous VALUES  -> OK
```

> [!important] **The asymmetry has one cause: only keys are sorted.** A key has to be compared against
> other keys to find its place in the tree, so it must be comparable. **A value is never compared with
> anything** — it is just carried along — so nothing is required of it. Every restriction in this class
> falls out of that one sentence.

---

# `null` acceptance

**The same story as `TreeSet` in note `08`**, and the same modern answer.

Measured on JDK 25:

| | Result |
|---|---|
| non-empty `TreeMap`, `put(null, v)` | ❌ `NullPointerException` |
| **empty** `TreeMap`, `put(null, v)` as the first entry | ❌ `NullPointerException` |

> **`null` is not allowed as a key in a `TreeMap` — not even as the first entry.**

**The reasoning is unchanged:** inserting a key means comparing it against the keys already there to
decide where it goes, and comparing anything with `null` throws.

> [!important] **Older material makes the first entry a special case, and it was true through Java 6.**
> With nothing to compare against, `null` used to slip in as the first key. **Java 7 closed it**, using
> the same `compare(key, key)` type-and-null check in `TreeMap` that note `08` quoted from the source.
> From 1.7 onward, *"`null` — such a type of story is not applicable for a `TreeMap`."*

> [!info] **`null` *values* are fine**, at any time. Only keys participate in comparison — the same
> asymmetry as above. Measured on JDK 25, a `TreeMap` accepts `put(3, null)` without complaint.

---

# The four constructors

**Identical in shape to `TreeSet`'s** — which is exactly what note `08` promised: *"same terminology,
copy paste."*

```java
TreeMap t = new TreeMap();                  // 1 — default natural sorting order
TreeMap t = new TreeMap(Comparator c);      // 2 — customised sorting order
TreeMap t = new TreeMap(Map m);             // 3 — from any map
TreeMap t = new TreeMap(SortedMap m);       // 4 — carries the source's sorting across
```

Confirmed on JDK 25: **4** public constructors.

> [!important] **The same thumb rule, still doing the work:**
> **no argument → default natural sorting order. `Comparator` argument → customised sorting order.**

---

# Demo 1 — default natural sorting order

```java
import java.util.*;

class TreeMapDemo {
    public static void main(String[] args) {
        TreeMap m = new TreeMap();
        m.put(100, "Z");
        m.put(103, "Y");
        m.put(101, "X");
        m.put(104, 106);
        System.out.println(m);
    }
}
```

Measured on JDK 25:

```
{100=Z, 101=X, 103=Y, 104=106}
```

**Keys ascending**, which is default natural sorting order for numbers. Note the last entry: the key
is an `Integer` and the value is also an `Integer` — **values have no type restriction**, so mixing
`String` and `Integer` values is fine.

**Adding a `String` key to this map:**

```
ClassCastException
```

---

# Demo 2 — customised sorting order

```java
import java.util.*;

class TreeMapDemo2 {
    public static void main(String[] args) {
        TreeMap m = new TreeMap(new MyComparator());
        m.put("XXX", 10);
        m.put("AAA", 20);
        m.put("ZZZ", 30);
        m.put("LLL", 40);
        System.out.println(m);
    }
}

class MyComparator implements Comparator {
    public int compare(Object obj1, Object obj2) {
        String s1 = obj1.toString();
        String s2 = obj2.toString();
        return s2.compareTo(s1);
    }
}
```

Measured on JDK 25:

```
{ZZZ=30, XXX=10, LLL=40, AAA=20}
```

**Reverse alphabetical**, because `s2.compareTo(s1)` swaps the arguments — variant 5 from note `09`'s
table.

> [!info] **`comparator()` now returns an object, not `null`.** Measured on JDK 25: the default-order
> map returns `null` from `comparator()`, and this one returns **a `Comparator` object**. That is how
> you interrogate a map you did not build to find out whether it carries a custom ordering.

---

# What this part established

| | |
|---|---|
| `SortedMap` | key–value pairs **sorted by key** |
| Sorting is on | the **key**, never the value |
| The six methods | `firstKey` · `lastKey` · `headMap` · `tailMap` · `subMap` · `comparator` |
| `headMap(k)` | **excludes** `k` |
| `tailMap(k)` | **includes** `k` |
| `subMap(a,b)` | **includes `a`, excludes `b`** |
| `TreeMap` data structure | **red-black tree** — a self-balancing BST, O(log n) |
| `TreeSet` is built on | **`TreeMap`** |
| Keys, default sorting | must be **homogeneous and comparable** — else `ClassCastException` |
| Keys, custom sorting | **no restriction** — a comparator supplies the order |
| **Values** | **never restricted** — heterogeneous, non-comparable, `null`, all fine |
| Why the asymmetry | **only keys are compared** |
| `null` key | ❌ **never**, not even the first entry |
| `null` value | ✅ always |
| The four constructors | no-arg · **`Comparator`** · `Map` · `SortedMap` |
| The thumb rule | **no argument → default natural · `Comparator` → customised** |
| `comparator()` returns | **`null`** for default order, **an object** for custom order |
