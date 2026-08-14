
**What happens in the moment between the collector reaching the object and the object being destroyed?** That is finalization.

---


> [!important] Just before destroying an object, the garbage collector always calls the **`finalize()`** method on it **to perform cleanup activities**. Once `finalize()` completes, the collector destroys the object.

| Question | Answer |
|---|---|
| Who calls `finalize()`? | the **garbage collector** |
| When? | **just before** destroying the object |
| Why? | to perform **cleanup activities** |
| What happens after it completes? | the collector destroys the object |

**What counts as cleanup?** Resource deallocation — closing a database connection, closing a network connection. Those are the things that need doing before the object disappears.

> [!warning] **`finalize()` is deprecated, and the JDK is actively trying to get rid of it.** Compiling any class that overrides it on JDK 25 produces:
>
> ```
> warning: [removal] finalize() in Object has been deprecated and marked for removal
> ```
>
> It has been deprecated since Java 9 and marked **for removal** since Java 18. Finalization can already be switched off with `--finalization=disabled`, and the plan is to remove the mechanism entirely in a future release.
>
> **The modern replacements** are `try`-with-resources with `AutoCloseable` for anything scope-bound — which is what you should actually be writing for connections — and `java.lang.ref.Cleaner` for the rare case where you genuinely need a safety net after an object becomes unreachable.
>
> Everything in these notes is still worth learning: it is asked constantly, and the *reasons* it was deprecated only make sense once you know the cases below. But if an interviewer asks whether you would use it, the answer is no.

---

# Where `finalize()` comes from

If the collector can call `finalize()` on *any* object, the method must be available on every object. It is:

> `finalize()` is defined in the **`Object`** class, and hence it is available to **every Java class** — because `Object` is the superclass of them all.

Its declaration, in full:

```java
protected void finalize() throws Throwable
```

Three things worth reading off that signature: it is **`protected`**, it returns **`void`**, and it declares **`throws Throwable`** — the broadest thing it is possible to throw, which matters enormously for Case 3.

And in `Object`, the body is empty. Open `Object.java` and the method is there with nothing inside it.

> [!info] **Why `Object`'s version is empty, and why that is correct.** The `Object` class cannot possibly know what cleanup *your* object needs — only you know that this object holds a database connection. So the base implementation does nothing, and **you override it in your own class** to define your own cleanup activities.

---

# Case 1 — which class's `finalize()` actually runs?

The first case, and the one that catches almost everybody.

```java
class Test {
    public static void main(String[] args) {
        String s = new String("durga");
        Test t = new Test();
        s = null;
        System.gc();
        System.out.println("End of main");
    }

    public void finalize() {
        System.out.println("finalize method called");
    }
}
```

A `String` object is created and then made eligible by nulling `s`. The collector is requested. `Test` overrides `finalize()`.

## What everyone predicts

First, a thread observation that the prediction rests on. Before `System.gc()` there is **one thread** — main. After it there are **two**: main, and the garbage collector. Main carries on to print `End of main`; the collector calls `finalize()` and destroys the object. Two threads running at once means **the order of output is not predictable**.

So the expected answer is one of these two:

```
finalize method called          End of main
End of main                     finalize method called
```

Durga Sir says that if he showed this program to a hundred students, ninety-nine would pick one of those two.

## What actually happens

Measured on JDK 25:

```
End of main
```

That is all. Run it a thousand times on a thousand machines and it is always just `End of main`. `finalize()` is never called.

There is no mistake in the program, and none in the JVM. The mistake is in the expectation.

## Why

**Which object is eligible for collection here?** The `String` object — that is the one whose reference was nulled.

So the collector calls `finalize()` **on the `String` object**. And which class's `finalize()` does that run? **`String`'s.** Not `Test`'s.

It is the same rule as any other method call, and Durga Sir makes the connection explicitly: if you call `s.m1()`, which `m1()` runs depends on what `s` actually is — `Student`'s if it is a `Student`, `Customer`'s if it is a `Customer`, `String`'s if it is a `String`. `finalize()` is not special.

`String` does not override `finalize()`, so it inherits the empty one from `Object`. Empty method, no output.

> [!important] **Case 1, stated properly.** Just before destroying an object, the collector calls `finalize()` **on the object that is eligible** — so **that object's class's** `finalize()` runs. If a `String` object is eligible, `String`'s `finalize()` runs, *not* the `Test` class's, no matter what `Test` overrides.

## Making it work

Change one thing — make the eligible object a `Test`:

```java
class Test {
    public static void main(String[] args) {
        Test t = new Test();
        t = null;
        System.gc();
        System.out.println("End of main");
    }

    public void finalize() {
        System.out.println("finalize method called");
    }
}
```

Measured on JDK 25:

```
End of main
finalize method called
```

Now the eligible object *is* a `Test`, so `Test`'s `finalize()` runs. And note the ordering — `End of main` came first on this run, which is exactly the two-thread unpredictability described above. The other order is equally legal.

> [!info] **This is why people think `finalize()` is broken.** They make a `String` or a `Student` eligible, override `finalize()` in the class holding `main`, see nothing printed, and conclude the method does not work. It works perfectly; it ran on the wrong class.

---

# Case 2 — calling `finalize()` yourself

`finalize()` is a method like any other, and it is not private. So: **can the programmer call it explicitly?**

Yes. And the consequence is the important bit.

> [!important] **If the programmer calls `finalize()`, it executes like an ordinary method call and the object is *not* destroyed.** If the **garbage collector** calls it, the object **is** destroyed once the method completes.
>
> `finalize()` does not destroy anything. It performs cleanup. Destruction is the collector's separate act, immediately afterwards — and only when the collector was the caller.

## The program

```java
class Test {
    public static void main(String[] args) {
        Test t = new Test();
        t.finalize();                  // 1 — by the programmer
        t.finalize();                  // 2 — by the programmer
        t = null;
        System.gc();                   // 3 — by the garbage collector
        System.out.println("End of main");
    }

    public void finalize() {
        System.out.println("finalize method called");
    }
}
```

**How many times does `finalize()` run?** Three. Twice by the programmer as ordinary method calls, and once by the collector just before destruction.

Measured on JDK 25:

```
finalize method called
finalize method called
End of main
finalize method called
```

The first two are the explicit calls, in order, before anything else. Then `End of main` from the main thread and the collector's call — and again, those last two could arrive in either order.

> [!example]- **Proof that the third call is the collector's** — run the same program with finalization switched off
> JDK 18 added a flag to disable finalization entirely. Running the identical program with it:
>
> ```
> java --finalization=disabled Case2
>
> finalize method called
> finalize method called
> End of main
> ```
>
> Two calls, not three. The programmer's explicit calls are unaffected — they are ordinary method calls and nothing can stop them. The collector's call is gone, because finalization is off. That cleanly separates which of the three calls came from where.

> [!important] A cleanup method called by *you* is just a method. The same method called by *the runtime* is the last thing that happens before the object is destroyed. Who calls it decides what it means 

---

# Where cases 1 and 2 leave us

| | Established |
|---|---|
| What `finalize()` is for | cleanup activities, immediately before destruction |
| Who normally calls it | the garbage collector |
| Where it is declared | `Object`, as `protected void finalize() throws Throwable`, with an empty body |
| **Case 1** | the **eligible object's own class**'s `finalize()` runs — not the class you happened to override it in |
| **Case 2** | you may call it yourself, but then it is **just a method call** and the object survives |

