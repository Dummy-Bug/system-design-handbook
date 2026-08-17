# Searching the elements of a list

`Collections` is the utility class — several utility methods for collection objects (note `02`). Sorting was the previous session; this is searching.

> **Internally the search method uses the binary search algorithm.**

**Which brings the algorithm's precondition with it:** binary search only works on a **sorted** list. Sort first, then search.

---

# The two `binarySearch` methods

```java
public static int binarySearch(List l, Object target)
public static int binarySearch(List l, Object target, Comparator c)
```

| Use this one | when the list is sorted according to |
|---|---|
| `binarySearch(l, target)` | **default natural sorting order** |
| `binarySearch(l, target, c)` | **customised sorting order** — pass **the same comparator** |

---

# The return value is an `int`, not a `boolean`

Most people expect `true`/`false` — available or not. **It returns an `int`**, and the int carries two different kinds of answer:

> **Successful search returns the index.**
> **Unsuccessful search returns the insertion point.**

## What insertion point means

Take this sorted list:

```
index:      0    1    2    3    4
          [ A ][ K ][ M ][ Z ][ a ]
insertion: -1   -2   -3   -4   -5   -6
```

> **The insertion point is the location where we can place the target element in the sorted list.**

**Searching for `J`:** it is not present. If you **were** to insert it, it would go between `A` and `K` — position 1. So why is the answer **−2** rather than 1?

> [!important] **Because a plain `1` would be indistinguishable from a successful search at index 1.** The return value has to encode both answers in one `int`, so the unsuccessful case is made **negative** and shifted by one: **insertion point = −(index) − 1**.
>
> The shift by one exists because index 0 has no negative counterpart — `-0` is `0`. So the insertion points run **−1, −2, −3 …** across a list whose indices run **0, 1, 2 …**
>
> **To recover the real position from a negative result:** `int pos = -(result) - 1;`

## Measured

```java
ArrayList l = new ArrayList();
l.add("Z"); l.add("A"); l.add("M"); l.add("K"); l.add("a");
Collections.sort(l);
```

Measured on JDK 25:

```
before sort         = [Z, A, M, K, a]
after  sort         = [A, K, M, Z, a]
binarySearch(l,"K") = 1     <- successful: the index
binarySearch(l,"J") = -2    <- unsuccessful: the insertion point
binarySearch(l,"B") = -2
binarySearch(l,"b") = -6    <- would go last
```

**`b` gives −6** because lowercase sorts after every uppercase letter (note `08`), so it belongs at the very end — insertion point 5, encoded as −6.

---

# The list must be sorted first

> **Before calling `binarySearch`, compulsorily the list should be sorted. Otherwise we will get unpredictable results.**

**Not an exception — a wrong answer.** Measured on JDK 25 with the same list left unsorted:

```
list (NOT sorted)    = [Z, A, M, K, a]
binarySearch(l2,"Z") = -5     <- but Z IS at index 0
binarySearch(l2,"A") = -1     <- but A IS at index 1
```

> [!warning] **Both searches failed on elements that are present.** No compile error, no runtime exception — just a wrong answer that looks like a legitimate not found.
>
> **Why it fails:** binary search jumps to the middle and asks is my target before or after this? That question only has a meaningful answer if the list is ordered. On an unsorted list it discards the half containing the element and never looks back.
>
> **This is the most dangerous method in the chapter**, precisely because it fails silently.

---

# If the list was sorted with a comparator, search with the same one

> **If the list is sorted according to a comparator, then at the time of the search operation also we have to pass the same comparator object. Otherwise we will get unpredictable results.**

```java
ArrayList l = new ArrayList(List.of(15, 0, 20, 10, 5));
Comparator c = (o1, o2) -> ((Integer) o2).compareTo((Integer) o1);   // descending
Collections.sort(l, c);
```

Measured on JDK 25 — every element searched both ways:

```
sorted descending = [20, 15, 10, 5, 0]

  target 20   with=0    without=-6    <- DISAGREE
  target 15   with=1    without=-6    <- DISAGREE
  target 10   with=2    without=2
  target 5    with=3    without=-1    <- DISAGREE
  target 0    with=4    without=-1    <- DISAGREE
```

**Four of the five disagree.** With the comparator, every element is found at its correct index. Without it, four of five report not found for elements that are present.

> [!important] **Notice `10` gives the right answer either way — and that is the trap, not the reassurance.** It lands in the middle, where the very first probe happens to hit it, so the wrong comparison never gets a chance to mislead. **A method that is right by luck one time in five is exactly what `unpredictable` means.**
>
> **The rule in one line: search the list the same way it was sorted.** The comparator is not decoration on the search — it is how the search knows which half to discard.

---

# The demo, in full

```java
import java.util.*;

class CollectionsSearchDemo {
    public static void main(String[] args) {
        ArrayList l = new ArrayList();
        l.add("Z");
        l.add("A");
        l.add("M");
        l.add("K");
        l.add("a");
        System.out.println(l);

        Collections.sort(l);
        System.out.println(l);

        System.out.println(Collections.binarySearch(l, "K"));
        System.out.println(Collections.binarySearch(l, "J"));
    }
}
```

```
[Z, A, M, K, a]
[A, K, M, Z, a]
1
-2
```

---

# The six conclusions

Collected, because he numbers them and they are the examinable list:

| | |
|---|---|
| **1** | the search methods internally use the **binary search algorithm** |
| **2** | **successful** search returns the **index** |
| **3** | **unsuccessful** search returns the **insertion point** |
| **4** | the insertion point is **where the target would go** in the sorted list |
| **5** | before searching, the list **must be sorted** — otherwise **unpredictable results** |
| **6** | if sorted by a **comparator**, pass **the same comparator** to the search |

> [!info] **`Arrays.binarySearch` is the same method for arrays**, with the same rules and the same negative-insertion-point encoding — that is the next session's material. **Learn the contract once and it applies to both.**

---

# What this part established

| | |
|---|---|
| The utility class | **`Collections`** |
| The algorithm | **binary search** |
| Return type | **`int`**, not `boolean` |
| Successful search | the **index** |
| Unsuccessful search | the **insertion point** |
| Insertion point encoding | **−(index) − 1** — negative so it cannot be confused with a real index |
| To recover the position | `-(result) - 1` |
| The precondition | the list **must be sorted** |
| Searching an unsorted list | **wrong answers, silently** — no exception |
| Sorted with a comparator | **pass the same comparator** to `binarySearch` |
| Getting it right by accident | happens, and is why `unpredictable` is the right word |
| Two overloads | `binarySearch(l, target)` and `binarySearch(l, target, c)` |
