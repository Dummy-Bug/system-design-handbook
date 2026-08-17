# Synchronization is per object, not per class

Note `07` established that the lock belongs to the **object**. This session pushes on what that means, using one program run three ways.

## The program

```java
class Display {
    public synchronized void wish(String name) {
        for (int i = 0; i < 3; i++) {
            System.out.print("Good Morning: ");
            try { Thread.sleep(300); } catch (Exception e) {}
            System.out.println(name);
        }
    }
}
```

**The `sleep` in the middle is deliberate** — it holds the thread between the two prints, so if another thread can interleave, you will see it.

| Output | Means |
|---|---|
| **regular** | `Good Morning: Dhoni` on its own line, every time |
| **irregular** | `Good Morning: Good Morning: Dhoni` — two threads interleaved mid-line |

---

# Run 1 — one object

```java
Display d = new Display();
new Thread(() -> d.wish("Dhoni")).start();
new Thread(() -> d.wish("Yuvraj")).start();
```

Measured on JDK 25:

```
Good Morning: Dhoni
Good Morning: Dhoni
Good Morning: Dhoni
Good Morning: Yuvraj
Good Morning: Yuvraj
Good Morning: Yuvraj
```

**Regular.** One object, one lock — the second thread waits for the first to finish.

---

# Run 2 — two objects, same synchronized method

```java
Display d1 = new Display();
Display d2 = new Display();
new Thread(() -> d1.wish("Dhoni")).start();
new Thread(() -> d2.wish("Yuvraj")).start();
```

Measured on JDK 25:

```
Good Morning: Good Morning: Dhoni
Good Morning: Yuvraj
Good Morning: Dhoni
Good Morning: Yuvraj
Good Morning: Dhoni
Yuvraj
```

**Irregular — even though the method is `synchronized`.**

> [!important] **This is the result people find surprising, and it follows directly from note `07`.** `T1` needs the lock **of `d1`**. `T2` needs the lock **of `d2`**. Those are two different locks, so neither thread ever waits. **`synchronized` did nothing here.**
>
> > **If multiple threads are operating on the SAME Java object, synchronization is required.** **If multiple threads are operating on MULTIPLE objects, synchronization is not required.**

> [!info] **Back to the dogs.** Three dogs, one biryani plate — synchronization required? **Yes.** Three dogs, three biryani plates — required? **No.** Each dog has its own plate; there is nothing to fight over.

## Why this is correct behaviour, not a defect

He makes the argument with the joint account from note `07`:

> **Wife and husband on the same joint account** — both operating on one object, so synchronization **is** required and one must wait.
>
> **But my account and your account are different objects.** While I am checking my account balance, no one else in the world is allowed to perform any operation on their account? **That would be absurd.** Why should you wait for me when we are touching different data?

**Locking per object is exactly right** — it makes threads wait only when they would actually collide.

---

# Run 3 — two objects, `static synchronized`

Change one word:

```java
public static synchronized void wish(String name) { … }
```

Two objects still, two threads still. Measured on JDK 25:

```
Good Morning: Dhoni
Good Morning: Dhoni
Good Morning: Dhoni
Good Morning: Yuvraj
Good Morning: Yuvraj
Good Morning: Yuvraj
```

**Regular again** — with two different objects.

> **If a thread wants to execute a `static synchronized` method, it requires the CLASS LEVEL LOCK.**

**And there is only one class-level lock per class**, so the two threads queue behind it regardless of how many objects exist. The objects are irrelevant — a `static` method does not belong to any object.

---

# Class level lock — the five rules

From the PDF, and this is the wording to memorise:

> **1.** Every class in Java has a **unique lock**. If a thread wants to execute a **static synchronized** method, it requires the **class level lock**.
>
> **2.** Once a thread gets the class level lock, it is allowed to execute **any static synchronized method** of that class.
>
> **3.** While a thread is executing any static synchronized method, the remaining threads are **not allowed to execute any static synchronized method** of that class simultaneously.
>
> **4.** But the remaining threads **are** allowed to execute **normal synchronized methods, normal static methods, and normal instance methods** simultaneously.
>
> **5.** **Class level lock and object lock are different, and there is no relationship between the two.**

> [!important] **Rule 5 is the examinable one.** Holding the class-level lock does **not** stop another thread from entering an instance `synchronized` method, and vice versa. **They are two independent locks**, so a thread holding one never blocks a thread wanting the other.

## Java has exactly two kinds of lock

> [!info] **He heads off the obvious next question.** Don't feel that next I am going to cover a variable-level lock — in Java we have only two locks: at object level, or at class level.

| Lock | Acquired by | Guards |
|---|---|---|
| **Object lock** | a `synchronized` **instance** method or block | that **one object** |
| **Class lock** | a `static synchronized` method or block | the **whole class** |

> [!info] **The class-level lock is an object lock underneath.** Every class has exactly one `Class` object — the fact `JVM-ARCHITECTURE/01` demonstrated — and the class-level lock is that object's lock. **Not a third mechanism**, just the same mechanism applied to the `Class` object.

---

# The decision table

| Threads operate on | Method is | Do they queue? |
|---|---|---|
| the **same** object | `synchronized` | ✅ **yes** |
| **different** objects | `synchronized` | ❌ **no** |
| **any** objects | `static synchronized` | ✅ **yes** — one class lock |
| the same object | not synchronized | ❌ no |

> [!warning] **Mixing the two locks is a classic bug.** Marking some methods `synchronized` and others `static synchronized` on the same class gives you **two independent locks**, and threads holding different locks can then modify the same shared state at the same time. **If a class has both static and instance state to protect, it needs a deliberate locking strategy — not one keyword sprinkled on each method.**

---

# What this part established

| | |
|---|---|
| Same object + `synchronized` | threads **queue** — regular output |
| Different objects + `synchronized` | threads **do not queue** — irregular output |
| Why | the lock is **per object**; two objects means two locks |
| The rule | synchronization is needed for the **same** object, not for **multiple** objects |
| Why that is right | why should you wait for me when we touch different accounts? |
| `static synchronized` requires | the **class level lock** |
| How many class locks | **one per class**, whatever the number of objects |
| Holding the class lock blocks | **all static synchronized** methods of that class |
| It does **not** block | normal synchronized methods · normal static methods · instance methods |
| Object lock and class lock | **completely independent** — no relationship |
| Java's locks | **exactly two** — object level and class level |
| The class lock is | the lock of the class's **`Class` object** |
