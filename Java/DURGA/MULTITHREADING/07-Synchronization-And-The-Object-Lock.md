# Synchronization

> The most valuable concept in all of multithreading.

He opens by naming the pattern he sees constantly: a student says I know multithreading, but I'm not that perfect with synchronization. **This is the topic people skip and then need.**

## Where the keyword can go

> **`synchronized` is a modifier applicable only for methods and blocks, but NOT for classes and variables.**

| | |
|---|---|
| synchronized **method** | ✅ |
| synchronized **block** | ✅ |
| synchronized **class** | ❌ |
| synchronized **variable** | ❌ |

---

# The problem it solves

> [!question]- **The biryani plate and the four dogs.** His story for data inconsistency, and it is the image the whole chapter runs on.
>
> He throws out a plate of biryani. **A dog finds it** and is delighted — biryani is not something a street dog gets often. It pauses, working out which side to start from.
>
> **A second dog arrives.** A fight starts immediately. The most believable animal is a dog. The most selfish animal is also a dog. Each one's plan is the same: **if the other leaves, I get the whole plate.**
>
> **A third dog arrives**, and now all three are fighting each other, each hoping the other two leave.
>
> **While the three are locked in the fight, a fourth dog walks up and starts eating.** The other three realise the fight is pointless — so each grabs the plate and **pulls it towards their own side.**
>
> **The biryani ends up on the ground and is useless to everybody.**
>
> > **That is data inconsistency.** The plate is a Java object, each dog is a thread, and four threads operating on one object at the same time leaves the object in a state nobody wanted.

> **If multiple threads are trying to operate simultaneously on the same Java object, then there may be a chance of a data inconsistency problem.**

## The technical versions

**Online booking.** The system shows **4 seats available**. One user requests **3 tickets**; another simultaneously requests **2**. Each request, read on its own, is satisfiable. Processed simultaneously, they are not.

**A joint account.** ₹10,000 in the account. The husband pays a ₹9,000 bill online at the same moment the wife spends ₹7,000 on a card at a shop. **Same account object, two operations, at once.**

## Measured

Four threads, each incrementing a shared counter 50,000 times — 200,000 expected. Measured on JDK 25:

```
unsynchronized run 1: expected 200000, got  59420
unsynchronized run 2: expected 200000, got  62708
unsynchronized run 3: expected 200000, got  94178
SYNCHRONIZED        : expected 200000, got 200000
```

> [!warning] **Two-thirds of the increments simply vanished, and the number is different every run.** `n++` is not one operation — it is **read n**, **add 1**, **write n back**. Two threads reading the same value before either writes means one increment is lost.
>
> **Nothing crashed and no exception was thrown.** That is what makes data inconsistency the worst class of bug: the program runs, and the answer is quietly wrong.

---

# What `synchronized` does

> [!question]- **The security guard at the biryani plate.** The fix, in the same story.
>
> Put a **security guard** next to the plate.
>
> **First dog:** I want to eat. — Nobody else is here. Go ahead.
> **Second dog arrives:** I want to eat. — One dog is already eating. **Please wait.**
>
> The second dog waits. When the first finishes, the second gets its turn. Then the third.
>
> **If the dogs eat one by one, is there any chance of inconsistency? No.**

> **If a method or block is declared `synchronized`, then at a time only one thread is allowed to execute that method or block on the given object — so the data inconsistency problem is resolved.**

## The cost

> **The main advantage of `synchronized` is that we can resolve data inconsistency problems. The main disadvantage is that it increases the waiting time of threads and creates performance problems.**

In a web application handling thousands of requests, thread 2 waits for thread 1, thread 3 waits for both, thread 4 waits for all three.

> **Hence, if there is no specific requirement, it is not recommended to use the `synchronized` keyword.**

> [!important] **He goes further, and it is worth quoting.** The worst keyword in Java is `synchronized`. Then immediately: Luckily `java.util.concurrent` has a solution for the `synchronized` keyword. For now treat `synchronized` as the hero — but after a few classes it will become zero.
>
> **That is the arc of this chapter**, and the enhancements sessions are where the replacement arrives. Do not use `synchronized` for style or out of caution — it is harmful when unnecessary.

---

# The lock

The mechanism underneath, and the part that gets asked.

> [!question]- **The public telephone booth.** How the lock actually works.
>
> A public telephone booth inside a cabin, with a **lock** on the door.
>
> **First person arrives:** I want to make a call. Nobody is inside, so they **take the lock**, go in, and use the phone.
>
> **Second person arrives** and cannot get in — the lock is taken. They **wait**.
>
> When the first person finishes and comes out, they **release the lock**, and the second person takes it.
>
> **Every Java object has exactly one such lock.**

## The rule that follows

> **Lock concept is implemented based on the OBJECT, but not based on the METHOD.**

**This one sentence answers every question in this section.**

```java
class X {
    public synchronized void m1() { … }
    public synchronized void m2() { … }
    public void m3()              { … }     // not synchronized
}
```

One `X` object. `T1` is executing `m1()`.

| Thread | Wants | Gets in? | Why |
|---|---|---|---|
| **T2** | `m1()` | ❌ **waits** | needs the lock of this object — `T1` has it |
| **T3** | `m2()` | ❌ **waits** | **a different method, but the same object's lock** |
| **T4** | `m3()` | ✅ **immediately** | `m3()` is **not synchronized** — no lock needed |

Measured on JDK 25:

```
ENTER m1 (synchronized)      by T1
ENTER m3 (NOT synchronized)  by T4      ← walks straight in
EXIT  m1 (synchronized)      by T1
ENTER m1 (synchronized)      by T2      ← only now
EXIT  m3 (NOT synchronized)  by T4
EXIT  m1 (synchronized)      by T2
ENTER m2 (synchronized)      by T3
EXIT  m2 (synchronized)      by T3
```

> [!important] **T3 is the row people get wrong.** Most people feel it is a different method, that's why it will get the chance. **It does not.** `m1` and `m2` are different methods but the **same object**, and there is only **one lock per object** — not one per method.

> **While a thread is executing a synchronized method on a given object, the remaining threads are not allowed to execute ANY synchronized method simultaneously on the same object. But the remaining threads ARE allowed to execute non-synchronized methods simultaneously.**

## Why T4 gets in at all

The follow-up doubt he anticipates: the object is already locked by T1 — how does T4 get in?

> [!info] **Think of every object as having two areas.**
>
> | | |
> |---|---|
> | **Synchronized area** | where **update** operations happen — modify, delete, change state. **One thread at a time.** |
> | **Non-synchronized area** | where **read** operations happen. **Any number of threads simultaneously.** |
>
> **The lock only guards the synchronized area.** T4 never asks for the lock, so the lock being held is irrelevant to it.
>
> This is also the design principle: **synchronize what mutates state, leave reads alone.** Every method you mark `synchronized` unnecessarily is waiting time you have added for nothing.

---

# What this part established

| | |
|---|---|
| `synchronized` applies to | **methods and blocks** only |
| Not to | **classes and variables** |
| The problem | **data inconsistency** — many threads, one object, at once |
| Measured | 4 threads × 50,000 increments gave **59,420** instead of 200,000 |
| Why | `n++` is **read, add, write** — not atomic |
| Nothing crashes | the answer is just **quietly wrong** |
| `synchronized` guarantees | **one thread at a time** on that method/block **for that object** |
| Advantage | resolves **data inconsistency** |
| Disadvantage | **increases waiting time**, creates **performance problems** |
| Therefore | don't use it **without a specific requirement** |
| Every object has | **one lock** |
| The key rule | **the lock is per OBJECT, not per METHOD** |
| While a thread holds it | no other thread may enter **any** synchronized method **on that object** |
| Non-synchronized methods | **always** available, lock or no lock |
| The design principle | synchronize **state changes**, not reads |
