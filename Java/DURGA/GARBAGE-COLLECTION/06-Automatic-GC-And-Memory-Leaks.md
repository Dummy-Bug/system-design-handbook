
Every program so far has requested collection explicitly, with `System.gc()` or `Runtime.getRuntime().gc()`. Drop that, and the question becomes:

**If the program is running low on memory and nobody asks, does the JVM run the collector by itself?**

---

# Case 5 — the JVM decides on its own

The way to answer it is to count. Create objects in a loop, make each one eligible immediately, and have `finalize()` increment a counter — so the counter tells you exactly how many objects the collector actually got to.

```java
class Test {
    static int count = 0;

    public static void main(String[] args) {
        for (int i = 0; i < 10; i++) {
            Test t = new Test();
            t = null;                    // eligible immediately
        }
    }

    public void finalize() {
        count++;
        System.out.println("finalize method called " + count);
    }
}
```

No `System.gc()` anywhere. If `finalize()` never runs, the collector never came.

**Ten objects: no output.** Ten objects is nothing; there is no memory pressure, so the JVM has no reason to collect.

Raise it. A hundred — nothing. A thousand — nothing. Ten thousand — nothing. Then at **one lakh** in the lecture, output suddenly appears: 41 objects finalized. Run it again: 71. Again: 81. Then 142, then 145.

## Measured on JDK 25

The demo still works, but the threshold has moved a long way, because a default heap in 2026 is vastly larger than one in 2016:

```
created         10  ->  finalize() ran        0 times
created        100  ->  finalize() ran        0 times
created      1,000  ->  finalize() ran        0 times
created     10,000  ->  finalize() ran        0 times
created    100,000  ->  finalize() ran        0 times     ← fired in the lecture, not here

created  1,000,000  ->  finalize() ran    9,814 times      ← first sign of the collector

created 10,000,000  ->  finalize() ran 3,875,064 times
```

One lakh — the number that triggered it on his machine — does nothing on mine. It takes a million.

And the run-to-run variation he demonstrates is just as visible. **Same command, five consecutive runs:**

```
created 1000000  ->  finalize() ran 20,487 times
created 1000000  ->  finalize() ran 10,489 times
created 1000000  ->  finalize() ran 15,387 times
created 1000000  ->  finalize() ran 12,429 times
created 1000000  ->  finalize() ran 11,172 times
```

Five runs, five different answers, nothing changed between them.

> [!important] **Two conclusions, and they are the point of the whole exercise.** The collector **did** run without being asked — so yes, the JVM triggers collection on its own when memory gets tight. And the number of objects it collected is **different every single time**, so there is nothing here you can predict or depend on.

> [!info] **The exact threshold is a property of the machine, not of Java.** On his system the problem started at one lakh objects; on mine it takes a million; on another machine it might take a crore. Some JVMs collect when free memory drops below about 10%. None of this is specified.

## The five questions with no answer


> The behaviour of the GC is **vendor dependent** and varies from JVM to JVM, hence we can't expect an exact answer for the following:

> 1. What is the **algorithm** followed by GC?
> 2. Exactly at **what time** does the JVM run GC?
> 3. In which **order** does GC identify the eligible objects?
> 4. In which **order** does GC destroy the objects?
> 5. Whether GC destroys **all** eligible objects or not.

Question 5 is answered by the measurement above: a million objects were eligible and roughly ten to twenty thousand were collected. **No, it does not destroy all of them.**

> [!important] **If an interviewer asks any of those five, the correct answer starts with "it is not guaranteed."** Then say what *is* true. Confidently naming a specific behaviour is the wrong answer, because the specification deliberately does not require one.

## The two things you *can* say

**1 — When the program runs low on memory, the JVM runs the collector automatically.** Not at a stated moment, but reliably enough to state as a general rule.

**2 — Most collectors follow the mark-and-sweep algorithm.** Ninety to ninety-five percent of them, in his estimate — not all. The algorithm in one line: **if the object has a reference, mark it; if it does not, sweep it.**

> [!warning] **"Mark and sweep" is the right vocabulary and an incomplete picture on a modern JVM.** Marking live objects and reclaiming the rest is still the foundation, but no production collector today is a plain mark-and-sweep. They are **generational** — the heap is split so that short-lived objects are collected cheaply and often — and they combine marking with copying and compaction to avoid fragmentation. G1 has been the default since Java 9; ZGC and Shenandoah do most of their marking concurrently with your application running.
>
> None of that is in this course, and it is a known gap in these notes rather than something Durga Sir gets wrong — he is careful to say the algorithm is vendor dependent, which remains exactly right.

---

# Memory leaks — when the collector cannot help

## The collector cries

Throughout this chapter the object has been the one crying — the collector turns up dancing, announcing it is going to destroy you. But heroes do not only laugh, as Durga Sir puts it. **Sometimes the collector cries.**

Here is when.

```java
Student s1  = new Student();
Student s2  = new Student();
Student s3  = new Student();
// … one crore of them, every single one held by a live reference
```

Ten million objects, and **every one still has a reference variable pointing at it.**

Memory pressure begins, so the JVM runs the collector. The collector arrives in the heap area and starts checking. Is this one eligible? No — it has a reference. This one? No — it has a reference. This one? No. It keeps roaming the heap looking for something, anything, it is allowed to destroy.

Meanwhile the program reaches a critical stage. The JVM turns up and lays into the collector: *I sent you half an hour ago and you have not freed a single bit of memory. What have you been doing?*

The collector cries. Then, after a few minutes, it explains:

*What can I do? **No object is eligible.** Every object in the heap has a reference variable. There is nothing for me to destroy.*

And the JVM has to accept it: *sorry — if no object is eligible, you can do nothing and I can do nothing.*

The program fails with **`OutOfMemoryError`**. The collector is present, the JVM is present, and neither is of any use.

## Whose fault?

Not the JVM's. Not the collector's. **The programmer's, one hundred percent.**

Ten million objects were created, and the programmer is not genuinely using ten million objects — but references were kept to all of them. Had any been made eligible, the collector would have freed the space and the program would have carried on.

> [!important] **Definition.** An object which is **not being used** in the application and is **not eligible for GC** is a **memory leak**.
>
> Both halves are required. Not used, so it is waste. Not eligible, so the collector cannot touch it. If memory leaks are present, the application will at some point go down with `OutOfMemoryError` — and the fix is the practice from the very beginning of this chapter: **if an object is no longer required, make it eligible.**

> [!warning] **The PDF says `OutOfMemoryException`. There is no such type — it is `OutOfMemoryError`.** That matters more than a typo normally would, because the distinction is itself an interview question: `OutOfMemoryError` extends `Error`, not `Exception`. You are not expected to catch it and you generally cannot recover from it, which is exactly the distinction Durga Sir drew in the previous note — exceptions are recoverable, errors are not.

## Finding them

The lecture names third-party memory management tools that attach to a running Java program and show, on a GUI, how many objects were created, how many are in use, and how many are not — with suspected leaks highlighted in red. The ones listed are **HP OVO**, **IBM Tivoli**, **JProbe** and **Patrol**.

> [!warning] **That tool list is the most dated thing in the chapter — every one of those is legacy or discontinued.** Nobody reaches for them in 2026, and naming them in an interview would be actively strange.
>
> What is used now: **Eclipse MAT** for heap dump analysis, **VisualVM** and **JDK Mission Control** for live monitoring, **Java Flight Recorder** for low-overhead production profiling, and `jcmd` / `jmap` to capture a heap dump in the first place. The typical workflow is to run with `-XX:+HeapDumpOnOutOfMemoryError`, then open the resulting dump in MAT and read the dominator tree to find what is retaining the memory.
>
> **This is a known gap in these notes**, and a deliberate one — the tooling is not taught anywhere in this course, and closing it properly is a separate piece of work.

> [!important] **This is an interview question at your level, and Durga Sir says so explicitly.** For candidates with two or three years upwards, *"what is a memory leak?"* is fair game. The answer, complete: **objects that the application is no longer using but which are not eligible for garbage collection, because references to them are still being held. They accumulate, the collector cannot reclaim them, and eventually the application dies with `OutOfMemoryError`.** Then give an example — a static collection that only ever grows is the classic one.

---

# The chapter, end to end

Thirteen videos, and this is the whole of it:

| Module | What it settled |
|---|---|
| **Introduction** | the collector is a daemon thread inside the JVM whose job is to destroy useless objects — which is why Java has no `delete` keyword |
| **Eligibility** | four ways: nullifying, reassigning, objects created inside a method, Island of Isolation |
| **Requesting** | `System.gc()` and `Runtime.getRuntime().gc()` — a request, never a command |
| **Finalization** | five cases: whose `finalize()` runs, calling it yourself, exceptions inside it, why it runs only once, and when the JVM collects unprompted |
| **Memory leaks** | objects unused but not eligible — the one failure the collector cannot save you from |

And the thread running through all of it: **almost nothing about the collector is guaranteed.** Not when it runs, not what algorithm it uses, not what order it works in, not whether it finishes the job. What *is* guaranteed is the part you control — an object with no reachable reference is eligible, and making objects eligible when you are done with them is the only lever you actually have.

> [!info] **What this chapter does not cover, so you know where you stand.** Generational heap layout (Eden, survivor spaces, old generation), the specific collectors and how to choose between them, GC logs, heap dump analysis, and reference types beyond the ordinary strong reference — soft, weak and phantom. None of that is in Durga Sir's course. It is the material the interview-QA files in `JVM-ARCHITECTURE/` flag as gaps, and it is the next thing to pick up.
