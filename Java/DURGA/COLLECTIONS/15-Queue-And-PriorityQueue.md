# The `Queue` interface

Back to `Collection` — no more keys and values.

> **`Queue` is the child interface of `Collection`. If we want to represent a group of individual objects prior to processing, then we should go for the `Queue` concept.**

**The examples are the ones from note `02`, now with the machinery to build them.** To send an SMS alert to a lakh of members, all one lakh mobile numbers must be stored somewhere first. Read the first, send; read the second, send. **The order added is the order delivered** — first-in-first-out.

> [!info] **Where you meet this professionally: JMS — Java Message Service.** In that, everything we have to talk in terms of queues only, because messages are stored in a queue before being published. Any store now, process later design is a queue.

## `LinkedList` is also a queue

> **From 1.5 onwards, the `LinkedList` class also implements the `Queue` interface.**

Confirmed on JDK 25: `Queue.class.isAssignableFrom(LinkedList.class)` → **`true`**, and using one as a queue gives `A B C` — insertion order out.

> **`LinkedList`-based implementation of `Queue` always follows first-in-first-out order.**

**That is `LinkedList` earning its place again.** Note `04` showed it is good at adding and removing at the ends, which is exactly what a queue needs.

---

# The five specific methods

> [!question]- **The ticket counter, which names every method.** His image for what a queue **is**, and the method names fall out of it.
>
> People are standing in a queue at a cinema ticket counter. **The counter offers a service**; the people are there to receive it.
>
> - **Another person arrives** wanting the service. You tell them: please stand in the queue — you are **offering** them the service. → **`offer()`**
> - **The person at the front** is the **head element** — the one who gets served first.
> - **Serve them and send them away** → **`poll()`**
> - **Just look at who is next, without serving them** → **`peek()`**
>
> Why are the people standing in the queue? To get some service. Adding to a queue is offering service to one more person.

| Method | |
|---|---|
| `boolean offer(Object o)` | **add** an object to the queue |
| `Object poll()` | **remove and return** the head element |
| `Object remove()` | **remove and return** the head element |
| `Object peek()` | **return** the head element **without removal** |
| `Object element()` | **return** the head element **without removal** |

## Why there are two of each

`poll()` and `remove()` do the same job. So do `peek()` and `element()`. **The difference is only visible when the queue is empty.**

Measured on JDK 25:

```
poll()    on empty = null
peek()    on empty = null
remove()  on empty -> NoSuchElementException
element() on empty -> NoSuchElementException
```

| | Empty queue |
|---|---|
| **`poll()` / `peek()`** | return **`null`** |
| **`remove()` / `element()`** | throw **`NoSuchElementException`** |

> [!important] **Choose by what an empty queue means in your code.**
>
> - **The queue may legitimately be empty** → use **`poll()` / `peek()`** and check for `null`.
> - **The queue should never be empty, and something is wrong if it is** → use **`remove()` / `element()`** and let the exception surface the bug.
>
> **This is a deliberate API pairing, not redundancy** — the same idea as `getFirst()` versus `peekFirst()` on `Deque` from note `04`. Picking the throwing version when you mean this must not happen is how you avoid a `null` silently flowing onward.

---

# `PriorityQueue`

> **If we want to represent a group of individual objects prior to processing according to some priority, then we should go for `PriorityQueue`.**

> [!question]- **The SMS that never arrived.** His story for why a queue is not always first-in-first-out — and it is a real production failure.
>
> A class is cancelled at short notice, so at **4 p.m.** they send an SMS to every student saying the 6 p.m. class is off. **At 6 p.m. all the students turn up anyway.** Nobody received the message.
>
> They call the SMS service provider. He checks the back-end queue: Sir, with your user ID there are **300 messages** — but they are in the queue. **Before them there are about 1.5 crore messages waiting**, because an election campaign is running. Those have to be delivered first, then yours.
>
> **The queue was strictly first-in-first-out, and that was the problem.** Two hours' notice was useless behind 15 million election messages.
>
> **What was needed was priority**, not arrival order — which is exactly what `PriorityQueue` provides.

| | |
|---|---|
| **Priority** | **default natural** sorting order, or **customised** via `Comparator` |
| **Insertion order** | ❌ not preserved — based on **priority** |
| **Heterogeneous objects** | ❌ under default sorting (must be homogeneous **and** comparable) · ✅ with a comparator |
| **`null`** | ❌ **not allowed**, not even as the first element |

**The homogeneous-and-comparable rule is identical to `TreeSet`'s**, and for the identical reason: ordering requires comparison.

## Constructors

```java
PriorityQueue q = new PriorityQueue();                                  // capacity 11, natural order
PriorityQueue q = new PriorityQueue(int initialCapacity);
PriorityQueue q = new PriorityQueue(int initialCapacity, Comparator c);
PriorityQueue q = new PriorityQueue(SortedSet s);
```

> [!important] **There is no constructor taking a `Comparator` alone in this set** — if you want to customise the priority, compulsorily you must customise the initial capacity also. Default initial capacity is **11**, like `Hashtable`.
>
> **On JDK 25 there are 7 constructors**, and one of them **is** `PriorityQueue(Comparator)` — added in Java 8. So `new PriorityQueue<>(comparator)` compiles today. The four above are the ones the exam asks for.

## The demo

```java
import java.util.*;

class PriorityQueueDemo {
    public static void main(String[] args) {
        PriorityQueue q = new PriorityQueue();
        for (int i : new int[]{15, 10, 30, 20, 5})
            q.offer(i);

        System.out.println(q);

        while (!q.isEmpty())
            System.out.print(q.poll() + " ");
    }
}
```

Measured on JDK 25:

```
queue as printed = [5, 10, 30, 20, 15]
polled in order  : 5 10 15 20 30
```

> [!warning] **Printing a `PriorityQueue` does NOT show priority order — and this catches everybody.** The printed form is `[5, 10, 30, 20, 15]`, which is neither insertion order nor sorted order. **It is the raw heap array.**
>
> **A `PriorityQueue` only guarantees that the HEAD is the highest-priority element.** The rest of the array satisfies the weaker heap property — each parent outranks its children — and that is all it ever promises. **The ordering is only observable by removing elements**, and `poll()` in a loop gives the fully sorted `5 10 15 20 30`.
>
> **Never write a test that asserts on a `PriorityQueue`'s `toString()`**, and never iterate one expecting sorted order — `for (Object o : q)` walks the array, not the priority order.

## With a comparator

```java
PriorityQueue q = new PriorityQueue(11, (o1, o2) -> ((Integer) o2).compareTo((Integer) o1));
```

Polled order, measured on JDK 25:

```
30 20 15 10 5
```

**Reverse priority** — the same comparator machinery as note `09`, now deciding who gets served first rather than where an element sits in a set.

---

# Duplicates ARE allowed

> [!important] **`PriorityQueue` permits duplicates.** Measured on JDK 25:
> ```java
> q.offer(10); q.offer(10); q.offer(10);
> ```
> ```
> size 3   [10, 10, 10]
> ```
>
> **Older material says duplicates are not allowed here** — reasoning that a service should be offered to unique people, and the same person should not stand in the queue twice. **That reasoning does not hold for a queue.** `PriorityQueue` implements `Collection`, not `Set`, and nothing about it rejects equal elements.
>
> **Why it must allow them:** a queue holds **work items**, not **members**. Two identical SMS messages to the same number are two pieces of work and both must be delivered. **Rejecting duplicates would silently drop jobs** — which is the opposite of what a job queue is for.
>
> `TreeSet` rejects duplicates because it is a **`Set`**. `PriorityQueue` keeps them because it is a **`Queue`**. The `compare()` returning zero means same priority here, not same element.

---

# What this part established

| | |
|---|---|
| `Queue` | a group of individual objects **prior to processing** |
| Usually | **first-in-first-out** |
| Where you meet it | **JMS**, and any store-now-process-later design |
| `LinkedList` implements `Queue` | **since 1.5** — and is always FIFO |
| The five methods | `offer` · `poll` · `remove` · `peek` · `element` |
| `offer` | add to the queue |
| `poll` / `remove` | **remove and return** the head |
| `peek` / `element` | **return** the head, no removal |
| On an **empty** queue | `poll`/`peek` → **`null`** · `remove`/`element` → **`NoSuchElementException`** |
| Choose the throwing pair when | an empty queue means **something is wrong** |
| `PriorityQueue` | objects served **by priority**, not arrival |
| Priority comes from | **default natural** order or a **`Comparator`** |
| Default sorting requires | **homogeneous and comparable** elements |
| `null` | ❌ never |
| Default initial capacity | **11** |
| **Printing a `PriorityQueue`** | shows the **raw heap array** — not priority order |
| Only guaranteed | that the **head** is highest priority |
| To see the order | **`poll()` repeatedly** |
| **Duplicates** | ✅ **allowed** — it is a `Queue`, not a `Set` |
