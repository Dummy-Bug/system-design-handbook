# Three small variations on `HashMap`

`LinkedHashMap`, `IdentityHashMap` and `WeakHashMap` are each **exactly the same as `HashMap`, including methods and constructors, except for one difference.** Learn `HashMap` and each of these costs you one fact.

---

# `LinkedHashMap`

| | `HashMap` | `LinkedHashMap` |
|---|---|---|
| **Underlying data structure** | hash table | **linked list + hash table** (hybrid) |
| **Insertion order** | ❌ not preserved — based on **hash code of keys** | ✅ **preserved** |
| **Introduced in** | 1.2 | 1.4 |

**The same program from note `11`, with one word changed.** Measured on JDK 25:

```java
HashMap m = new HashMap();
```
```
{balayya=800, chiranjeevi=700, venkatesh=200, nagarjuna=500}
```

```java
LinkedHashMap m = new LinkedHashMap();
```
```
{chiranjeevi=700, balayya=800, venkatesh=200, nagarjuna=500}
```

**The second is exactly the insertion order.**

> [!info] **This is the `HashSet` / `LinkedHashSet` difference from note `07`, repeated verbatim** — same hybrid data structure, same reason, same version gap of 1.2 → 1.4.

> **`LinkedHashSet` and `LinkedHashMap` are commonly used for developing cache-based applications**, where duplicates are not allowed and insertion order must be preserved.

---

# `==` versus `equals()` — the groundwork

`IdentityHashMap` cannot be understood without this, so it comes first.

| | Meant for |
|---|---|
| **`==`** | **reference comparison** (address comparison) |
| **`.equals()`** | **content comparison** |

```java
Integer i1 = Integer.valueOf(10000);
Integer i2 = Integer.valueOf(10000);

System.out.println(i1 == i2);        // false
System.out.println(i1.equals(i2));   // true
```

Measured on JDK 25:

```
i1 == i2      : false
i1.equals(i2) : true
```

**Two separate objects** — so `==` says no. **Identical content** — so `equals()` says yes. This is the `JAVA-LANG-PACKAGE/12` material being put to work.

> [!warning] **Use a value outside −128 to 127 for this demo, or it will not work.**
> `Integer.valueOf()` returns a **cached** object for small values, so `valueOf(10) == valueOf(10)` is **`true`** — both references point at the same cached object, and the whole demonstration collapses. Measured on JDK 25:
> ```
> valueOf(10)    == valueOf(10)    : true    <- inside the cache
> valueOf(10000) == valueOf(10000) : false   <- outside the cache
> ```
> Older material writes `new Integer(10)`, which always allocated a fresh object and so was safe at any value. **`new Integer(...)` is deprecated** (note `08` of `JAVA-LANG-PACKAGE`), so the modern way to get two distinct `Integer`s is `valueOf` with a value **outside the cache** — or any object of your own class.

---

# `IdentityHashMap`

> **It is exactly the same as `HashMap` including methods and constructors, except for the following difference.**

| | `HashMap` | `IdentityHashMap` |
|---|---|---|
| **To identify duplicate keys the JVM uses** | **`equals()`** | **`==`** |
| **which means** | **content** comparison | **reference** comparison |

## The demo

```java
import java.util.*;

class IdentityHashMapDemo {
    public static void main(String[] args) {
        HashMap m = new HashMap();
        Integer i1 = Integer.valueOf(10000);
        Integer i2 = Integer.valueOf(10000);
        m.put(i1, "Pawan");
        m.put(i2, "Kalyan");
        System.out.println(m);
    }
}
```

Measured on JDK 25:

```
HashMap         : {10000=Kalyan}   size=1
IdentityHashMap : {10000=Pawan, 10000=Kalyan}   size=2
```

**Read both lines against the rule:**

| Map | Are `i1` and `i2` duplicate keys? | Why | Entries |
|---|---|---|---|
| **`HashMap`** | **yes** | `i1.equals(i2)` → **true** | **1** — the second `put` replaced the first value |
| **`IdentityHashMap`** | **no** | `i1 == i2` → **false** | **2** — two separate entries |

> [!important] **The `IdentityHashMap` output looks wrong and is not.** Two entries printed as `10000=Pawan, 10000=Kalyan` — the same key twice. **They are not the same key**; they are two different objects that happen to have the same content, and `IdentityHashMap` was asked to distinguish objects, not contents.
>
> **When you would want this:** tracking objects by identity — a serialization library recording which objects it has already written, or a graph walker marking visited nodes. Content equality would wrongly merge two distinct-but-equal nodes.

---

# `WeakHashMap`

> The `HashMap` which is very weak is called `WeakHashMap`.

He says it with a straight face and expects you not to believe him yet. **The name is literal**, and the demonstration is about garbage collection.

## The garbage collection recap

> [!question]- **The garbage collector and the object's last wish.** His retelling of the finalization story, which the `WeakHashMap` demo builds on directly.
>
> An object has **no references** pointing at it, so it is **eligible for garbage collection**.
>
> The garbage collector arrives and is **very happy** — useless objects are its food. It stands in front of the object and dances: I am going to kill you. The object **starts shivering and crying**.
>
> But the collector is not entirely cruel. It approaches and says: Definitely I am going to destroy you — that is my job. But I will give you one small chance. **Do you have any last wish?**
>
> The object replies: One database connection is associated with me, one network connection is associated with me. **Can you please close them**, and then you can destroy me.
>
> **To fulfil that last wish, the garbage collector calls `finalize()`** — the cleanup method. Once `finalize()` completes, the collector destroys the object.
>
> | | |
> |---|---|
> | Who calls `finalize()`? | the **garbage collector** |
> | When? | **just before** destroying the object |
> | Why? | to perform **cleanup activities** |
>
> This is `GARBAGE-COLLECTION/04` in story form, and the `finalize()` print is how the next demo proves whether an object was actually destroyed.

## The test class

```java
class Temp {
    public String toString() { return "temp"; }
    public void finalize() { System.out.println("finalize method called"); }
}
```

**`finalize()` is the instrument.** If that line appears, the object was destroyed. If it does not, the object survived.

## With a normal `HashMap`

```java
import java.util.*;

class WeakHashMapDemo {
    public static void main(String[] args) throws Exception {
        HashMap m = new HashMap();
        Temp t = new Temp();
        m.put(t, "durga");
        System.out.println(m);

        t = null;
        System.gc();
        Thread.sleep(5000);

        System.out.println(m);
    }
}
```

Measured on JDK 25:

```
{temp=durga}
{temp=durga}
```

**`finalize()` was never called, and the entry is still there.** The only reference `t` was set to `null`, the collector was requested, and still the object survived.

> **Even though an object doesn't have any reference, it is not eligible for GC if it is associated with a `HashMap`. That is, the `HashMap` dominates the garbage collector.**

> [!question]- **The argument between the map and the collector.** His dramatisation of why the object survives — and the punchline names the class.
>
> `t = null`, so the `Temp` object has no external reference. **The collector arrives and dances in front of it.** The object starts crying.
>
> **The `HashMap` hears a key crying** and comes over. Why are you crying? — The garbage collector came, it says it is going to destroy me. — Where is the garbage collector? The object points.
>
> **The `HashMap` goes over and gives the collector left and right.** Why are you here? Why are you in this location? The collector protests: This object doesn't have any reference, that is why I came. The `HashMap` answers: **Have you not seen — this object is associated with ME. How can you destroy it?**
>
> The collector goes crying to the **JVM**. The JVM's ruling: **`HashMap` is stronger than you. Don't go that side once again.**

## With a `WeakHashMap`

**One word changed:**

```java
WeakHashMap m = new WeakHashMap();
```

Measured on JDK 25:

```
{temp=durga}
finalize method called
{}
```

**`finalize()` ran and the map is now empty.** The object was destroyed, and its entry went with it.

> **In the case of `WeakHashMap`, if the object doesn't contain any references it is eligible for GC even though it is associated with the `WeakHashMap`. That is, the garbage collector dominates the `WeakHashMap`.**

> [!question]- **The same argument, with the opposite ending.** Why the name turns out to be accurate.
>
> Same setup. The collector dances in front of the object; the object cries; **the `WeakHashMap` comes over** and asks the collector why it is there.
>
> **The collector's reply:** Oh `WeakHashMap` — **you are already weak.** Don't open your mouth, let me complete my job.
>
> The `WeakHashMap` realises it is weak, comes back and stands aside. The collector calls `finalize()`, destroys the object — **and the value goes too, because without a key there is no entry.**
>
> Can I use the term: the `HashMap` which is very weak is called `WeakHashMap`? Correct or not? — and by this point, yes.

> [!important] **What `weak` actually means, in one sentence.** A `HashMap` holds a **strong** reference to its keys, and a strong reference is enough to keep an object alive. A `WeakHashMap` holds a **weak** reference, which the collector is permitted to ignore. So being a key in a `WeakHashMap` does not keep an object alive.
>
> **The practical use is caches and metadata.** If you want to attach information to objects without preventing those objects from ever being collected, a `WeakHashMap` is exactly the tool — the entry disappears on its own when the key becomes garbage, with no cleanup code from you.
>
> This is the same `java.lang.ref` machinery that `Cleaner` uses (`GARBAGE-COLLECTION/04`), exposed as a map.

---

# What this part established

| | |
|---|---|
| All three are | **exactly `HashMap`** except for one difference each |
| `LinkedHashMap` | **insertion order preserved**; hybrid **linked list + hash table**; 1.4 |
| Its use case | **cache-based applications**, like `LinkedHashSet` |
| `==` | **reference** comparison |
| `.equals()` | **content** comparison |
| `IdentityHashMap` uses | **`==`** to identify duplicate keys |
| `HashMap` uses | **`equals()`** to identify duplicate keys |
| Two equal-content `Integer`s | **1 entry** in a `HashMap`, **2 entries** in an `IdentityHashMap` |
| Demo caveat | use a value **outside −128…127** — `Integer.valueOf` caches small values |
| `HashMap` vs the collector | **`HashMap` dominates** — a key is never collected |
| `WeakHashMap` vs the collector | **the collector dominates** — a key with no other reference is collected |
| The proof | **`finalize()` runs**, and the entry vanishes |
| Why | a `WeakHashMap` holds only a **weak reference** to its keys |
| Use case | attaching data to objects **without keeping them alive** |
