# Why blocks exist

`synchronized` on a method locks **the whole method**. Often that is far more than you need.

> [!question]- **The Dilsukhnagar bomb blast, and the flights out of New York.** His argument for why
> locking a whole method is absurd when only part of it needs it.
>
> A bomb goes off in **Dilsukhnagar**, an area of Hyderabad. In response:
>
> - **no flight is allowed to depart from New York**
> - **no city bus is allowed to run in London**
> - **no local train is allowed to leave Sydney**
>
> The people in each city ask why. *"There was a bomb blast in Dilsukhnagar."*
>
> **If you wrote code that behaved like this, people would laugh at you.** Block Dilsukhnagar. Perhaps
> block Hyderabad. **There is no reason to stop flights in New York.**
>
> > *"Very unfortunately, most programmers are doing exactly this type of programming."*

## The situation

A method with **10,000 lines**, of which about **10** touch shared state — a database update, say.

**What most people do:** declare the entire method `synchronized`.

**What that costs:** every thread wanting *any* of those 10,000 lines waits for whoever is inside,
even though 9,990 of them were never a problem.

> **If very few lines of the code require synchronization, then it is not recommended to declare the
> entire method as synchronized. We have to enclose those few lines of the code using a synchronized
> block.**

> **The main advantage of a synchronized block over a synchronized method is that it reduces the
> waiting time of threads and improves the performance of the system.**

> [!question]- **The narrow bridge at Kodada.** The same point measured in hours, and it is the
> sharper version.
>
> Hyderabad to Vijayawada is about **300 km — 6 hours**. Somewhere in the middle, at Kodada, there is
> a **narrow bridge where only one vehicle can cross at a time.**
>
> **The bad solution:** allow only one vehicle on the whole Hyderabad–Vijayawada route. The next
> vehicle cannot start until the previous one arrives — **6 hours per vehicle**, so about **four
> vehicles per day**.
>
> *"If my life's goal is to reach Vijayawada, I may not reach it in my lifetime"* — at four a day, your
> vehicle might be 40,000 places back in the queue.
>
> **The good solution:** let everyone drive the 300 km freely, and **synchronize only the bridge.**
> Multiple vehicles travel at once; at the bridge, one at a time.
>
> | | Wait |
> |---|---|
> | Lock the whole route | **6 hours** |
> | Lock only the bridge | **about 1 minute** |
>
> **Same safety, and the difference is the whole point of a block.**

---

# The three forms

## 1 — Lock of the current object

```java
synchronized (this) {
    // …
}
```

> **If a thread gets the lock of the current object, then only it is allowed to execute this area.**

**Equivalent to a `synchronized` instance method**, but scoped to the lines that need it.

## 2 — Lock of a particular object

```java
synchronized (b) {
    // …
}
```

> **If a thread gets the lock of the particular object `b`, then only it is allowed to execute this
> area.**

## 3 — Class level lock

```java
synchronized (Display.class) {
    // …
}
```

> **If a thread gets the class level lock of `Display`, then only it is allowed to execute this
> area.**

`Display.class` is the **`Class` object** of `Display`, and its lock is the class-level lock from note
`08` — confirming that the class lock really is just an object lock on the `Class` object.

---

# All three, measured

```java
class D2 {
    public void wish(String name) {
        // one lakh lines that need no synchronization
        synchronized (this) {
            for (int i = 0; i < 3; i++) {
                System.out.print("Good Morning: ");
                Thread.sleep(300);
                System.out.println(name);
            }
        }
        // another one lakh lines
    }
}
```

Measured on JDK 25:

| Setup | Output | Why |
|---|---|---|
| `synchronized(this)`, **one** object | **regular** | one object, one lock |
| `synchronized(this)`, **two** objects | **irregular** | two objects, two locks |
| `synchronized(B)` — `B` **shared static**, two objects | **regular** | one lock, shared deliberately |
| `synchronized(D4.class)`, two objects | **regular** | one class lock |

```
=== synchronized(this), TWO objects ===
Good Morning: Good Morning: Dhoni
Good Morning: Yuvraj
Good Morning: Yuvraj
Good Morning: Dhoni
...
```

> [!important] **Row 3 is why form 2 exists.** With `synchronized(this)` the two objects have separate
> locks and interleave. Point both at **one shared object `B`** and they serialise — **without making
> the objects related in any other way.**
>
> **This is the tool for guarding shared state that does not live in either object**: a static
> counter, a shared file, a connection. You create a private lock object and every thread that touches
> that state synchronizes on it.

> [!warning] **Never synchronize on a `String` literal or a boxed primitive.** `synchronized("lock")`
> compiles and appears to work, but string literals are interned (`STRING-HANDLING/02`) and small
> `Integer`s are cached (note `12` of Collections) — so **unrelated code elsewhere can end up sharing
> your lock** and block you for reasons you will never find.
>
> The safe idiom is a dedicated object nobody else can reach:
> ```java
> private final Object lock = new Object();
> ```

---

# Method versus block

| | Use |
|---|---|
| The **whole method** needs synchronization | **`synchronized` method** |
| Only **a few lines** need it | **`synchronized` block** |

> [!info] **He puts the distinction as global versus local.** Declaring a method `synchronized` is a
> *global* decision about every line in it; a block is a *local* decision about the lines that
> actually share state. **Prefer the smallest region that is still correct** — but no smaller, because
> a lock that does not cover the whole critical section is worse than no lock, since it looks safe.

---

# What this part established

| | |
|---|---|
| The problem | a whole method locked when **a few lines** need it |
| The image | a bomb in Dilsukhnagar grounding flights in **New York** |
| The measurable version | the **Kodada bridge** — 6 hours' wait vs 1 minute |
| The rule | few lines → **synchronized block**, never the whole method |
| The advantage | **reduces waiting time**, improves performance |
| `synchronized (this)` | lock of the **current object** |
| `synchronized (b)` | lock of a **particular object** |
| `synchronized (Display.class)` | the **class level lock** |
| `Display.class` | the class's **`Class` object** — so the class lock is an object lock |
| Two objects, `synchronized(this)` | **irregular** — two separate locks |
| Two objects, shared lock object | **regular** — one lock by design |
| Use a shared lock object when | the state guarded **belongs to neither object** |
| Never lock on | a **`String` literal** or a **boxed primitive** — they are shared globally |
| The safe idiom | `private final Object lock = new Object();` |
| Method vs block | **global** decision vs **local** one |
