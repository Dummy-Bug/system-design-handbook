# The `Map` interface

The second half of the framework begins. Everything so far has been about **individual objects**; this is about **key–value pairs**.

> **Map is not a child interface of `Collection`.**

In our collection framework movie, the first half is `Collection` and the second half is `Map`. Underline it — do not strike it through.

> **If we want to represent a group of objects as key–value pairs, then we should go for `Map`.**

```
101  →  Durga
102  →  Shiva
103  →  Ravi
104  →  Pavan
```

**Where you meet this in real work:** roll number → name, mobile number → address, domain name → IP address, parameter name → parameter value, attribute name → attribute value. Request form parameters are internally stored in map style only.

| | |
|---|---|
| Both keys and values are | **objects** |
| Duplicate **keys** | ❌ not allowed |
| Duplicate **values** | ✅ allowed |
| Each key–value pair is called | an **entry** |

> **Hence a map is considered a collection of `Entry` objects.**

> [!info] **`Entry` is a technical word, not a casual one** — there is an interface named `Entry`, and it is why the sentence above is precise rather than descriptive.

---

# `Map` interface methods

`Collection`'s methods do not apply here — **the concepts are different.** `add()` takes one object; a map needs a key **and** a value at once. So `Map` defines its own.

| Method | |
|---|---|
| `Object put(Object key, Object value)` | add **one** key–value pair |
| `void putAll(Map m)` | add a **group** of key–value pairs |
| `Object get(Object key)` | the **value** associated with this key |
| `Object remove(Object key)` | remove the **entry** for this key |
| `boolean containsKey(Object key)` | is this **key** present? |
| `boolean containsValue(Object value)` | is this **value** present? |
| `boolean isEmpty()` | is the map empty? |
| `int size()` | how many **key–value pairs**? |
| `void clear()` | remove everything |

> [!info] **`get()` on a missing key returns `null`**, not an exception — there is no key, so the corresponding value is `null`. And `remove(key)` removes the **whole entry**, because without a key there is no chance of a value.

## Why `put()` returns an `Object`

The method adds a pair — so what is there to return?

```java
m.put(101, "Durga");     // returns null — nothing was replaced
m.put(102, "Shiva");     // returns null
m.put(101, "Ravi");      // key 101 already exists
```

> **If the key is already present, the old value is replaced with the new value, and `put()` returns the old value.**

Measured on JDK 25:

```
put duplicate  = 700
after replace  = {balayya=800, chiranjeevi=1000, venkatesh=200, nagarjuna=500}
```

> [!important] **Contrast this with `Set.add()` from note `07`.** A `Set` returns **`false`** and **discards** your object. A `Map` **overwrites** and hands you back what was there before.
>
> **The difference is that a map entry has two halves.** Rejecting the whole pair would throw away the new value you were trying to store, so the key stays and the value is updated instead. Returning the old value means the replacement is not silent — you can see what you displaced.
>
> **When nothing was replaced, `put` returns `null`.** So `null` from `put` means this key is new.

---

# The three collection views

Take a map and ask for only part of it:

| Method | Returns | Why that type |
|---|---|---|
| `Set keySet()` | just the **keys** | keys cannot duplicate → a **`Set`** |
| `Collection values()` | just the **values** | values **can** duplicate, and order does not matter → the general **`Collection`** |
| `Set entrySet()` | the **entries** | each entry is unique → a **`Set`** |

Measured on JDK 25:

```
keySet()   = [balayya, chiranjeevi, venkatesh, nagarjuna]
values()   = [800, 1000, 200, 500]
entrySet() = [balayya=800, chiranjeevi=1000, venkatesh=200, nagarjuna=500]
```

> [!important] **The return type of each one is derived, not arbitrary** — and this is a fair interview question. `keySet()` returns a `Set` **because duplicate keys are impossible**. `values()` returns a `Collection` and not a `Set` **because duplicate values are possible**, so it cannot promise uniqueness.
>
> **These three are called the collection views of a map.** You call them on a map object and get collection-framework objects back — which is how the two halves of the framework connect.

---

# The `Entry` interface

> **Without an existing map object there is no chance of an existing entry object. Hence the `Entry` interface is defined inside the `Map` interface.**

```java
interface Map {
    interface Entry {
        Object getKey();
        Object getValue();
        Object setValue(Object o);
    }
}
```

Confirmed on JDK 25: `Map.Entry.class.getDeclaringClass()` is **`Map`**, and its declared methods are `getKey`, `getValue`, `setValue` (plus `equals` and `hashCode`).

> [!info] **This is `INNER-CLASSES` justifying itself in the JDK.** The whole chapter opened with without existing one type of object there is no chance of existing another — and named **Map–Entry** as one of its three examples. Here is that rule producing a nested interface in the standard library.

| Method | |
|---|---|
| `Object getKey()` | the entry's key |
| `Object getValue()` | the entry's value |
| `Object setValue(Object o)` | **replace** the value; returns the old one |

**These three apply only to an `Entry` object** — not to a map, and not to a collection.

---

# `HashMap`

| | |
|---|---|
| **Underlying data structure** | **hash table** |
| **Insertion order** | ❌ not preserved — based on **hash code of keys** |
| **Duplicate keys** | ❌ not allowed |
| **Duplicate values** | ✅ allowed |
| **Heterogeneous objects** | ✅ allowed — for **both** keys and values |
| **`null` key** | ✅ **once** |
| **`null` values** | ✅ **any number of times** |
| **Implements** | `Serializable`, `Cloneable` — not `RandomAccess` |
| **Best choice for** | **search** operations |

Measured on JDK 25:

```
{null=v2, k1=null, k2=null, k3=null}   size=4
```

**One `null` key** (the second `put(null, …)` replaced the first), and **three `null` values** happily coexisting.

> [!important] **The `null` asymmetry follows from the duplicate rules, not from a separate rule.** Keys cannot duplicate, so there can be at most one `null` key. Values can duplicate, so there can be any number of `null` values. **Every `null` question in this chapter answers itself this way.**

## The four constructors

**Identical to `HashSet`'s** — as promised in note `07`, learning them once covers every hashing class:

```java
HashMap m = new HashMap();                                  // capacity 16, fill ratio 0.75
HashMap m = new HashMap(int initialCapacity);
HashMap m = new HashMap(int initialCapacity, float fillRatio);
HashMap m = new HashMap(Map m);                             // inter-conversion
```

Confirmed on JDK 25: **4** public constructors.

> [!info] **The fourth one takes a `Map`, not a `Collection`.** Inter-conversion still exists, but only between maps — because you cannot build a map out of a collection without inventing keys. **The pattern holds; the parameter type follows the concept.**

---

# The demo — every map method in one program

```java
import java.util.*;

class HashMapDemo {
    public static void main(String[] args) {
        HashMap m = new HashMap();
        m.put("chiranjeevi", 700);
        m.put("balayya", 800);
        m.put("venkatesh", 200);
        m.put("nagarjuna", 500);
        System.out.println(m);

        System.out.println(m.put("chiranjeevi", 1000));

        Set s = m.keySet();
        System.out.println(s);

        Collection c = m.values();
        System.out.println(c);

        Set s1 = m.entrySet();
        System.out.println(s1);

        Iterator itr = s1.iterator();
        while (itr.hasNext()) {
            Map.Entry m1 = (Map.Entry) itr.next();
            System.out.println(m1.getKey() + " ... " + m1.getValue());
            if (m1.getKey().equals("nagarjuna"))
                m1.setValue(10000);
        }
        System.out.println(m);
    }
}
```

Measured on JDK 25:

```
{balayya=800, chiranjeevi=700, venkatesh=200, nagarjuna=500}
700
[balayya, chiranjeevi, venkatesh, nagarjuna]
[800, 1000, 200, 500]
[balayya=800, chiranjeevi=1000, venkatesh=200, nagarjuna=500]
  balayya ... 800
  chiranjeevi ... 1000
  venkatesh ... 200
  nagarjuna ... 500
{balayya=800, chiranjeevi=1000, venkatesh=200, nagarjuna=10000}
```

**Three things this output proves at once:**

| | |
|---|---|
| **`{...}` braces** | it is a **map** — collections print `[...]`, as note `03` established |
| the order is not insertion order | **hash code of keys** decides, and it is not predictable |
| the final line differs from the loop's | **`setValue` wrote through to the map** |

> [!important] **`setValue()` modifies the map itself, not a copy.** The loop prints `nagarjuna ... 500`, then sets it to `10000` — and the map printed afterwards shows `nagarjuna=10000`. **The entry is a live view into the map**, which is why `entrySet()` is the only safe way to modify values while iterating.
>
> Some people may ask — we changed the value to 10000, but why are we still getting 500? Because we printed before changing it. The print happens first; the write happens after.

## Walking a map with a cursor

The idiom is worth having by heart, because a map has no `iterator()` of its own:

```java
Set s1 = m.entrySet();                        // 1. get the entries as a Set
Iterator itr = s1.iterator();                 // 2. a Set has an iterator
while (itr.hasNext()) {
    Map.Entry m1 = (Map.Entry) itr.next();    // 3. each element is an Entry
    …
}
```

**`Map.Entry` is written outer-dot-inner**, exactly like `Outer.Inner` in `INNER-CLASSES/01`.

> [!info] **The modern form is one line.** Since Java 5:
> ```java
> for (Map.Entry<String,Integer> e : m.entrySet())
>     System.out.println(e.getKey() + " ... " + e.getValue());
> ```
> and since Java 8, without a cursor at all:
> ```java
> m.forEach((k, v) -> System.out.println(k + " ... " + v));
> ```
> **The explicit-iterator form is still what gets asked**, and it is what you need if you want to `remove()` during the walk.

---

# `LinkedHashMap`

> **`LinkedHashMap` is the child class of `HashMap`. It is exactly the same as `HashMap` including constructors and methods, except that insertion order is preserved.**

| | `HashMap` | `LinkedHashMap` |
|---|---|---|
| **Underlying data structure** | hash table | **hash table + linked list** |
| **Insertion order** | ❌ not preserved | ✅ **preserved** |
| **Introduced in** | **1.2** | **1.4** |

The same program with `LinkedHashMap`, measured on JDK 25:

```
{chiranjeevi=700, balayya=800, venkatesh=200, nagarjuna=500}
```

**Exactly the insertion order.** Confirmed: `LinkedHashMap`'s superclass is `HashMap`.

> [!info] **The `HashSet`/`LinkedHashSet` relationship from note `07`, repeated exactly.** Same difference, same reason, same use case — **cache-based applications**, where duplicates are not allowed and insertion order matters.

---

# What this part established

| | |
|---|---|
| `Map` is | **not** a child of `Collection` |
| When to use it | a group of objects as **key–value pairs** |
| Keys and values | both are **objects** |
| Duplicate keys / values | ❌ / ✅ |
| Each key–value pair | is an **entry** |
| A map is | a **collection of `Entry` objects** |
| Add one / many | **`put(k,v)`** · **`putAll(m)`** |
| `put()` on an existing key | **replaces** the value and **returns the old one** |
| `put()` on a new key | returns **`null`** |
| `get()` on a missing key | returns **`null`** |
| The three views | **`keySet()`** → `Set` · **`values()`** → `Collection` · **`entrySet()`** → `Set` |
| Why `values()` is not a `Set` | **duplicate values are allowed** |
| `Entry` is declared | **inside `Map`** — no map, no entry |
| `Entry`'s three methods | `getKey()` · `getValue()` · **`setValue()`** |
| `setValue()` | writes **through to the map** |
| `HashMap` data structure | **hash table**, ordered by **hash code of keys** |
| `null` key | **once** |
| `null` values | **any number** |
| `HashMap` constructors | **four** — same as `HashSet`; the fourth takes a **`Map`** |
| Default capacity / fill ratio | **16** / **0.75** |
| Walking a map | `entrySet()` → `iterator()` → cast to **`Map.Entry`** |
| `LinkedHashMap` | child of `HashMap`; **insertion order preserved**; for **caches** |
