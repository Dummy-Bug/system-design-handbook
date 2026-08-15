# Why `java.lang` is the most important package

> **For writing any Java program — whether simple or complex — the most commonly required classes and
> interfaces are grouped into a separate package, which is `java.lang`.**

He rates it above every other topic in the course, and the argument is a test you can run in your head:

| Package | Can you write a Java program without it? |
|---|---|
| `java.util` | ✅ yes, any number |
| `java.sql` | ✅ yes |
| `java.io` | ✅ yes |
| **`java.lang`** | ❌ **impossible** |

## The proof — the smallest program there is

```java
class Test {
    public static void main(String[] args) {
        System.out.println("hello world");
    }
}
```

**Nothing smaller can be written.** Now count the dependencies on `java.lang`:

| What you wrote | What it depends on |
|---|---|
| `class Test` | every class is a child of **`Object`** — in `java.lang` |
| `String[] args` | **`String`** — in `java.lang` |
| `System.out.println` | **`System`** — in `java.lang` |
| `"hello world"` | a **`String`** object — in `java.lang` |

> *"Without `java.lang` you can't use the `class` keyword, you can't write a `main` method, you can't
> write an SOP statement. Without these things, is it possible for a Java program to exist? **Never.**"*

## And that is why it needs no import

> **We are not required to import `java.lang` explicitly, because all classes and interfaces present in
> `java.lang` are by default available to every Java program.**

The reverse question is the one that gets asked: *why does `java.util` need an import but `java.lang`
not?* Because without `java.util` a program can still exist — without `java.lang` it cannot.

---

# The `Object` class

> **Every class in Java is a child class of `Object`, either directly or indirectly. Hence `Object` is
> considered the root of all Java classes.**

Measured on JDK 25:

```
A's parent:      class java.lang.Object
B's parent:      class java.lang.Object
String's parent: class java.lang.Object
Object's parent: null
```

**`Object` itself has no parent** — that is what being the root means.

## Why `Object` and not, say, `String`

> **For any Java class — `Student`, `Customer`, `Account`, `String`, `StringBuffer` — the most commonly
> required methods are defined in a separate class, which is `Object`.**

`hashCode()` is needed by any object. `equals()` is needed by any object. `toString()` is needed by any
object.

**And how do you make those available to every class?** Make that class the **parent**, and inheritance
does the rest.

> [!important] **Contrast it with `String`, which is the question he actually asks.** *"Why isn't
> `String` the root?"*
>
> **`String` contains methods that apply only to `String` objects.** You cannot apply `String`'s methods
> to a `Student` or a `Customer`. **`Object` contains methods applicable to any Java object** — which is
> the only kind of class that can sit at the root of everything.

## Direct vs indirect child — and the interview trap

```java
class A { }              // A's parent is Object — DIRECT child
class C extends B { }    // C's parent is B — INDIRECT child of Object
```

Measured on JDK 25:

```
A's parent: class java.lang.Object
C's parent: class B
B's parent: class java.lang.Object
```

> **If our class does not extend any other class, then only is it the DIRECT child of `Object`. If our
> class extends some other class, then our class is an INDIRECT child of `Object`.**

> [!question]- **Deep dive — the confusion an interviewer may try to create.** Worth rehearsing, because
> the setup sounds convincing.
>
> The interviewer writes:
>
> ```java
> class A extends B { }
> ```
>
> Then argues: *"`A` is a child of `B`. But every class in Java is also a child of `Object`. So `A` has
> **two** parents — therefore Java **does** support multiple inheritance with classes."*
>
> **The first thing to do is reject the premise.** That is not what is happening:
>
> ```
> A  →  B  →  Object
> ```
>
> **`A` is a child of `B`, and `B` is a child of `Object`.** `A` has exactly **one** direct parent. This
> is **multilevel inheritance**, not multiple inheritance.
>
> | | |
> |---|---|
> | **multiple** inheritance | one class, **two direct parents** — ❌ not supported for classes |
> | **multilevel** inheritance | a **chain** of single parents — ✅ what is happening here |
>
> > **Java does not provide support for multiple inheritance with respect to classes — either directly
> > or indirectly.**

---

# The methods of `Object`

> **`Object` defines 11 methods** — and the number is as examinable as the names.

| | Signature |
|---|---|
| 1 | `public String toString()` |
| 2 | `public native int hashCode()` |
| 3 | `public boolean equals(Object obj)` |
| 4 | `protected native Object clone() throws CloneNotSupportedException` |
| 5 | `protected void finalize() throws Throwable` |
| 6 | `public final Class getClass()` |
| 7 | `public final void wait() throws InterruptedException` |
| 8 | `public final void wait(long ms) throws InterruptedException` |
| 9 | `public final void wait(long ms, int ns) throws InterruptedException` |
| 10 | `public final native void notify()` |
| 11 | `public final native void notifyAll()` |

> [!info] **`wait`, `notify` and `notifyAll` belong to `Object`, not to `Thread`.** *"Even though we use
> these two in multithreading, these methods are related to the `Object` class."* That is a standard
> interview question in itself — they are on `Object` because **any** object can act as a lock.

## Counting them yourself

He verifies the number with reflection rather than asserting it:

```java
import java.lang.reflect.*;

class Count {
    public static void main(String[] args) throws Exception {
        Class c = Class.forName("java.lang.Object");
        Method[] m = c.getDeclaredMethods();
        int count = 0;
        for (Method m1 : m) { System.out.println(m1.getName()); count++; }
        System.out.println("the number of methods: " + count);
    }
}
```

> [!info] **Note the import.** `Method` lives in **`java.lang.reflect`** — a **sub-package** — so
> `java.lang` being automatic does not help. You must write `import java.lang.reflect.*;` explicitly.
> (The sub-package rule from `DECLARATIONS-AND-ACCESS-MODIFIERS/02`, and this is his own example of it.)

Measured on JDK 25:

```
finalize
wait0
equals
toString
hashCode
getClass
clone
notify
notifyAll
wait
wait
wait
the number of methods: 12
```

**Twelve, not eleven** — and he predicts exactly this:

> *"In the interview room, if the interviewer asks, you have to tell 11. But why don't we give
> importance to the 12th method? Because it is internally required for the `Object` class itself, not
> for the child classes."*

> [!important] **The 12th method is `wait0`** — a private native helper that the three public `wait`
> overloads delegate to. Measured with `javap -p`:
> ```
> public final void wait(long) throws java.lang.InterruptedException;
> private final native void wait0(long) throws java.lang.InterruptedException;
> ```
> It is internal plumbing, which is exactly why nobody counts it. **Say 11.** (Older JDKs had a
> different private helper here, `registerNatives`, so do not be surprised to see that name in older
> material — the count and the reasoning are the same either way.)

> [!warning] **`finalize()` is one of the 11, and it must never be used in new code.** It is deprecated
> **for removal** — compiling any class that overrides it produces:
> ```
> warning: [removal] finalize() in Object has been deprecated and marked for removal
> ```
> Finalizers are unpredictable, can resurrect objects, and delay collection. **`try-with-resources`
> and `java.lang.ref.Cleaner` replace it.** It is still examinable, and the garbage collection chapter
> works through why it failed.

---

# What this part established

| | |
|---|---|
| `java.lang` holds | the classes and interfaces required by **any** Java program |
| Without `java.util` / `io` / `sql` | you can still write programs |
| Without `java.lang` | **impossible** |
| Hello world depends on it | four times — `Object`, `String`, `System`, the string literal |
| Import needed? | **no** — automatically available |
| `Object` is | the **root** of all Java classes |
| Why | it holds the methods needed by **every** object |
| Why not `String` | `String`'s methods apply only to strings |
| No `extends` clause | **direct** child of `Object` |
| Has an `extends` clause | **indirect** child of `Object` |
| `A extends B` | **multilevel**, not multiple, inheritance |
| Multiple inheritance with classes | **not supported**, directly or indirectly |
| `Object` methods | **11** to quote; **12** declared |
| The 12th (his JDK) | `registerNatives` |
| The 12th (JDK 25) | **`wait0`** — private native helper |
| `wait` / `notify` / `notifyAll` | belong to **`Object`**, not `Thread` |
| ⚠️ `finalize()` | **deprecated for removal** since Java 18 |
| `java.lang.reflect` | a **sub-package** — needs its own import |
