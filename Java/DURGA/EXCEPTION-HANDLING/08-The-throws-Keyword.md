
> The main objective of the **`throws`** keyword is to **delegate the responsibility of exception handling to the caller method.**

That is the whole idea. You are not handling the exception; you are declaring that you will not, and that whoever called you must.

---

# Why it exists

Back to the obligation from part 3: if there is any chance of a **checked** exception, you must handle it, or the code will not compile. Two examples of that error, both measured on JDK 25.

```java
import java.io.*;

class Test3 {
    public static void main(String[] args) {
        PrintWriter out = new PrintWriter("abc.txt");
        out.println("hello");
    }
}
```

```
error: unreported exception FileNotFoundException; must be caught or declared to be thrown
```

```java
class Test3 {
    public static void main(String[] args) {
        Thread.sleep(5000);
    }
}
```

```
S1.java:1: error: unreported exception InterruptedException; must be caught or declared to be thrown
```

The error message has been telling you the two options all along: **`must be caught or declared to be thrown`.**

## Option one — catch it

```java
class Test3 {
    public static void main(String[] args) {
        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) { }
    }
}
```

```
compiled and ran
```

## Option two — declare it

```java
class Test3 {
    public static void main(String[] args) throws InterruptedException {
        Thread.sleep(5000);
    }
}
```

```
compiled and ran
```

Both compile. Both run. **They are not equivalent**, and the difference is the point of this part.

---

# The four things to know about `throws`

> - The main objective of `throws` is to **delegate the responsibility** of exception handling to the **caller** method.
> - `throws` is required **only for checked exceptions**. Using it for an unchecked exception has **no use**.
> - `throws` is required **only to convince the compiler**.
> - Using `throws` **does not prevent abnormal termination** of the program.
> Hence **`try`-`catch` is recommended over `throws`.**

That third and fourth point together are the whole argument, and both are measurable.

## It only convinces the compiler

```java
class S8 {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("before");
        throw new InterruptedException("delegated, not handled");
    }
}
```

```
before
Exception in thread "main" java.lang.InterruptedException: delegated, not handled
	at S8.main(S8.java:4)
```

It compiled. It also **died abnormally** — stack trace, default exception handler, the lot. Exactly what part 2 described.

> [!important] **`throws` moves the responsibility; it does not discharge it.** The compiler stops objecting, and nothing else changes. If nobody up the chain actually catches the thing, you get precisely the abnormal termination you were trying to avoid — you have just moved *where* it happens.
>
> This is why `try`-`catch` is recommended. `catch` is handling. `throws` is paperwork.

## It does nothing for unchecked exceptions

```java
class S9 {
    public static void main(String[] args) throws ArithmeticException {
        System.out.println(10/0);
    }
}
```

```
compiles (but it would have compiled anyway)

Exception in thread "main" java.lang.ArithmeticException: / by zero
```

The `throws ArithmeticException` is **pure decoration**. Unchecked exceptions were never checked, so there was nothing to convince the compiler of. Remove the clause and the behaviour is identical.

> [!info] **It is not quite useless as documentation.** Declaring `throws` on an unchecked exception tells a reader "this can happen", and it appears in the Javadoc. But it changes nothing about compilation or runtime, and the lecture's judgement — *no use* — is right about its mechanical effect.

---

# It has to be declared all the way up

The delegation is not a one-step trick. Every method in the chain that passes the exception along must declare it.

```java
class Test {
    public static void main(String[] args) throws InterruptedException {
        doStuff();
    }

    public static void doStuff() throws InterruptedException {
        doMoreStuff();
    }

    public static void doMoreStuff() throws InterruptedException {
        Thread.sleep(5000);
    }
}
```

```
full chain compiles
```

> In the above program, if we remove **at least one** `throws` keyword, the program won't compile.

Confirmed — removing it from the middle method only:

```java
public static void doStuff() { doMoreStuff(); }        // throws removed
```

```
S5.java:3: error: unreported exception InterruptedException; must be caught or declared to be thrown
  public static void doStuff() { doMoreStuff(); }
```

> [!important] **`doStuff` becomes the one at fault, not `doMoreStuff`.** It calls a method that declares a checked exception, so `doStuff` now faces the same choice as everybody else: catch it or declare it. Delegation is a chain of individual obligations, and each link has to satisfy the compiler on its own.
>
> Which is also the practical cost of `throws`. Declaring it on one deep method forces the clause into every caller above it, all the way to `main`. It propagates through your API whether you wanted it to or not.

---

# Two cases on `throws` itself

## Case 1 — only `Throwable` types

Exactly as with `throw`:

```java
class Test3 {
    public static void main(String[] args) throws Test3 { }
}
```

```
S6.java:1: error: incompatible types: S6 cannot be converted to Throwable
```

And with one `extends` added:

```java
class Test3 extends RuntimeException {
    public static void main(String[] args) throws Test3 { }
}
```

```
ok
```

## Case 2 — `throw` of a checked exception needs `throws` too

This is where the two keywords meet, and it catches people:

```java
class Test3 {
    public static void main(String[] args) {
        throw new Exception();
    }
}
```

```
S10.java:1: error: unreported exception Exception; must be caught or declared to be thrown
```

You raised it yourself, deliberately, and the compiler **still** demands you declare or catch it — because `Exception` is checked, and the rule does not care who created the object.

Add the clause and it compiles:

```java
class Test3 {
    public static void main(String[] args) throws Exception {
        throw new Exception("declared");
    }
}
```

```
compiles

Exception in thread "main" java.lang.Exception: declared
```

Whereas an unchecked one needs nothing:

```java
class Test3 {
    public static void main(String[] args) {
        throw new ArithmeticException("no declaration needed");
    }
}
```

```
compiles with no throws clause at all
```

> [!important] **The two keywords side by side, since this is the confusion the whole part exists to clear up.**
>
> | | `throw` | `throws` |
> |---|---|---|
> | What it is | a **statement** | part of a **method signature** |
> | What it does | **raises** an exception now | **declares** that this method may propagate one |
> | Followed by | an exception **object** | exception **class names** |
> | How many | one object | comma-separated list |
> | Effect at runtime | the exception happens | **nothing whatsoever** |
> | Needed for unchecked | no | no — and no effect if used |

---

# What this part established

| | |
|---|---|
| Purpose of `throws` | **delegate** handling to the caller |
| Required for | **checked** exceptions only |
| What it actually achieves | **convinces the compiler**, nothing more |
| Does it prevent abnormal termination | **no** |
| Recommended over `try`-`catch`? | **no** — the reverse |
| Scope of the obligation | **every** method in the chain must declare it |
| Legal types | `Throwable` and its subclasses only |
| Throwing a checked exception yourself | still needs `catch` or `throws` |

