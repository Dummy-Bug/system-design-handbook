# The `Arrays` class

The second utility class, and the last topic in the chapter.

> **`Arrays` is a utility class to define several utility methods for array objects.**

**Compare it with `Collections`:**

| Class | Utility methods for |
|---|---|
| `Collections` | **collection** objects |
| **`Arrays`** | **array** objects |

> [!info] **This class exists to patch note `01`'s third limitation.** Arrays have no underlying data
> structure, so *"for every requirement we have to write the code explicitly"* — you write the search
> logic, you write the sort logic. **`Arrays` fills that gap.** *"Most of the people don't know about
> this class, that's why whenever array sorting is required they are writing the sort logic manually."*

**Three utilities to cover:** sorting, searching, and converting an array to a list.

---

# Sorting the elements of an array

## Three `sort` methods

```java
public static void sort(primitive[] p)               // 1
public static void sort(Object[] o)                  // 2
public static void sort(Object[] o, Comparator c)    // 3
```

| | Sorts | According to |
|---|---|---|
| **1** | a **primitive** array | **default natural** sorting order |
| **2** | an **object** array | **default natural** sorting order |
| **3** | an **object** array | **customised** sorting order |

> [!important] **There is no `sort(primitive[], Comparator)` — and the reason is worth knowing.**
> `Comparator`'s method is `compare(Object, Object)`, so **it can only receive objects.** A primitive
> cannot be passed where an `Object` is expected, so customised sorting is structurally impossible for
> a primitive array.
>
> > **We can sort primitive arrays only based on default natural sorting order, whereas we can sort
> > object arrays either based on default natural sorting order or based on customised sorting
> > order.**
>
> **The workaround, if you need it:** use `Integer[]` instead of `int[]`, and the third method applies.

## The demo

```java
import java.util.*;

class ArraysSortDemo {
    public static void main(String[] args) {
        int[] a = {10, 5, 20, 11, 6};
        Arrays.sort(a);

        String[] s = {"A", "Z", "B"};
        Arrays.sort(s);
        Arrays.sort(s, new MyComparator());
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
primitive before = [10, 5, 20, 11, 6]
primitive after  = [5, 6, 10, 11, 20]
object after     = [A, B, Z]
object w/ comp   = [Z, B, A]
```

> [!info] **Printing an array needs help.** `System.out.println(a)` on an array prints something like
> `[I@1b6d3586` — arrays do not override `toString()`. Use a **for-each loop**, or
> **`Arrays.toString(a)`**, which is another of this class's utility methods.

---

# Searching the elements of an array

## Three `binarySearch` methods

```java
public static int binarySearch(primitive[] p, primitive target)
public static int binarySearch(Object[] o, Object target)
public static int binarySearch(Object[] o, Object target, Comparator c)
```

**The same three-way split as `sort`, for the same reason.**

> **All rules of the `Arrays` class binary search methods are exactly the same as the `Collections`
> class binary search methods.**

Which means everything from note `17` applies unchanged:

| | |
|---|---|
| Algorithm | **binary search** |
| Successful search | returns the **index** |
| Unsuccessful search | returns the **insertion point** — `−(index) − 1` |
| Before searching | the array **must be sorted**, else **unpredictable results** |
| If sorted by a comparator | pass **the same comparator** |

Measured on JDK 25 with `[5, 6, 10, 11, 20]`:

```
binarySearch(6)  = 1     <- successful: the index
binarySearch(14) = -5    <- unsuccessful: 14 would go at index 4
```

**`-5` decodes as `-(-5) - 1 = 4`** — and index 4 is indeed where 14 belongs, between 11 and 20.

---

# Converting an array to a list

## Why the method is called `asList`, not `toList`

**The naming is deliberate**, and the reason is the whole point of this section.

```java
public static List asList(Object[] a)
```

> **Strictly speaking, this method won't create an independent list object. For the existing array we
> are getting a list VIEW.**

> [!info] **The database analogy he uses.** *"In your database somewhere you may have a table and a
> view. A view is a logical thing; a table is physical."* One table can have many views, and a view
> holds no data of its own — it is a way of looking at the table.
>
> **`asList` is the same idea.** The underlying object is still the **array**. You are given a `List`
> reference through which to look at it. **Nothing was copied.**
>
> Contrast the other direction: `Collection.toArray()` (note `03`) really does build a new array —
> hence `to`, not `as`.

## The view goes both ways

```java
String[] arr = {"A", "Z", "B"};
List l = Arrays.asList(arr);
```

Measured on JDK 25:

```
list              = [A, Z, B]
arr[0] = "CHANGED-VIA-ARRAY";
after array write = [CHANGED-VIA-ARRAY, Z, B]      ← seen through the LIST

l.set(1, "CHANGED-VIA-LIST");
after list write  = [CHANGED-VIA-ARRAY, CHANGED-VIA-LIST, B]   ← seen in the ARRAY
```

> **By using the array reference, if we perform any change, that change will be reflected in the list.
> And by using the list reference, if we perform any change, that change will be reflected in the
> array.**

**There is only one collection of data here** — the array — with two references pointing at it.

## The view is fixed-size

The consequence people trip over. Measured on JDK 25:

```
add()    on asList -> UnsupportedOperationException
remove() on asList -> UnsupportedOperationException
set()    on asList -> OK
```

> [!warning] **`Arrays.asList()` gives you a list you cannot grow or shrink.** `set()` works because
> writing to a slot is something an array can do. **`add()` and `remove()` throw
> `UnsupportedOperationException`**, because an array is fixed in size — note `01`'s very first
> limitation, showing through the `List` interface.
>
> The class you get back is **`java.util.Arrays$ArrayList`** — an inner class of `Arrays`, **not
> `java.util.ArrayList`.** They share a name and nothing else.
>
> **To get a real, growable list:**
> ```java
> List<String> real = new ArrayList<>(Arrays.asList(arr));
> ```
> That is the inter-conversion constructor from note `03`, and it **copies** — so the two are then
> independent.

---

# `Collections` and `Arrays` side by side

The two utility classes, which is how the chapter ends:

| | `Collections` | `Arrays` |
|---|---|---|
| Utility methods for | **collection** objects | **array** objects |
| Sorting | `sort(List)` · `sort(List, Comparator)` | `sort(prim[])` · `sort(Object[])` · `sort(Object[], Comparator)` |
| Searching | `binarySearch(List, target)` · `+ Comparator` | `binarySearch(prim[], t)` · `(Object[], t)` · `+ Comparator` |
| Conversion | — | **`asList(Object[])`** |
| Customised sorting on primitives | n/a | ❌ **impossible** |

---

# What this part established

| | |
|---|---|
| `Arrays` is | a **utility class for array objects** |
| Why it exists | arrays have **no ready-made method support** of their own |
| Three `sort` methods | primitive · object · object + `Comparator` |
| Customised sorting on a **primitive** array | ❌ — `Comparator` takes **objects** |
| Workaround | use a **wrapper array** (`Integer[]`) |
| Printing an array | needs a for-each loop or **`Arrays.toString()`** |
| Three `binarySearch` methods | same three-way split |
| Their rules | **identical** to `Collections.binarySearch` |
| Successful / unsuccessful | **index** / **insertion point** `−(index) − 1` |
| Must be sorted first | ✅ else **unpredictable results** |
| `asList()` returns | a **view**, not a copy |
| Why `as` and not `to` | nothing is copied — the array **is** the data |
| Changes through either reference | **visible through the other** |
| `add()` / `remove()` on the view | ❌ **`UnsupportedOperationException`** — an array is fixed size |
| `set()` on the view | ✅ works |
| The class you get | **`java.util.Arrays$ArrayList`** — not `java.util.ArrayList` |
| To get a real list | `new ArrayList<>(Arrays.asList(arr))` |
