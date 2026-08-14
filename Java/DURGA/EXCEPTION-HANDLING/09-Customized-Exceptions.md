
# The five keywords, one line each

| Keyword | Purpose |
|---|---|
| **`try`** | to maintain **risky** code |
| **`catch`** | to maintain **handling** code |
| **`finally`** | to maintain **cleanup** code |
| **`throw`** | to hand our created exception object to the JVM **manually** |
| **`throws`** | to **delegate** the responsibility of exception handling to the caller method |

> [!important] **Worth memorising in exactly this form.** *"What are the exception handling keywords and what does each do?"* is a warm-up question, and five crisp phrases — risky, handling, cleanup, hand over, delegate — answer it completely. The trap inside it is `throw` versus `throws`: one hands an object to the JVM *now*, the other declares that this method will not deal with one.

---

# The compile-time errors, collected

Every one of these has appeared in this chapter, and each was measured on JDK 25 where it was introduced. Having them as a set is useful because a common exam format is *"which of the following produces a compile-time error?"*

| # | Error | Cause | Where it appeared |
|---|---|---|---|
| 1 | `exception XXX has already been caught` | a catch block that can never be reached — parent listed before child | part 4 |
| 2 | `unreported exception XXX; must be caught or declared to be thrown` | a checked exception neither caught nor declared | parts 3, 7 |
| 3 | `exception XXX is never thrown in body of corresponding try statement` | catching a **fully checked** exception the `try` cannot raise | part 3 |
| 4 | `'try' without 'catch', 'finally' or resource declarations` | a `try` block on its own | part 5 |
| 5 | `'catch' without 'try'` | a `catch` with no `try`, **or one written after `finally`** | part 5 |
| 6 | `'finally' without 'try'` | a `finally` with no `try` | part 5 |
| 7 | `incompatible types: XXX cannot be converted to Throwable` | `throw` or `throws` used with a non-`Throwable` type | parts 6, 7 |
| 8 | `unreachable statement` | a statement written directly after a `throw` | part 6 |

> [!info] **Error 3 is the one that encodes a rule rather than a mistake.** The others are all "you wrote something malformed". That one is the compiler enforcing the fully-checked/partially-checked distinction — which is why `catch (Exception e)` over an empty `try` compiles and `catch (IOException e)` does not.

---

# Customized exceptions

> Sometimes we can create our own exception to meet our programming requirements. Such exceptions are called **customized exceptions** (user-defined exceptions).

Examples : `InsufficientFundsException`, `TooYoungException`, `TooOldException`

This is what `throw` was really for. A predefined exception like `ArithmeticException` is raised by the JVM when it notices something; **nothing in the JVM knows that being under eighteen is a problem in your application.** Only you can raise that, and `throw` is how.

## Defining one

An exception class is an ordinary class that extends the hierarchy. The whole of it:

```java
class TooYoungException extends RuntimeException {
    TooYoungException(String s) {
        super(s);
    }
}

class TooOldException extends RuntimeException {
    TooOldException(String s) {
        super(s);
    }
}
```

Two things are happening, and both matter.

**`extends RuntimeException`** puts the class into the hierarchy, which is what makes it throwable at all — part 6 showed that a class outside the hierarchy gives `incompatible types`.

**The constructor calls `super(s)`.** That is what makes the message appear in the stack trace. Skip it and your exception prints with no description, as the bare `T2` in part 6 did.

## Using it

```java
class CustomizedExceptionDemo {
    public static void main(String[] args) {
        int age = Integer.parseInt(args[0]);

        if (age < 18) {
            throw new TooYoungException("please wait some more time, you will get the best match");
        }
        else if (age > 60) {
            throw new TooOldException("your age has already crossed, no chance of getting married");
        }
        else {
            System.out.println("you will get match details soon by e-mail");
        }
    }
}
```

All three paths, measured on JDK 25:

```
$ java CustomizedExceptionDemo 9
Exception in thread "main" TooYoungException: please wait some more time, you will get the best match
	at CustomizedExceptionDemo.main(CustomizedExceptionDemo.java:6)

$ java CustomizedExceptionDemo 27
you will get match details soon by e-mail

$ java CustomizedExceptionDemo 61
Exception in thread "main" TooOldException: your age has already crossed, no chance of getting married
	at CustomizedExceptionDemo.main(CustomizedExceptionDemo.java:9)
```

The exception name in the trace is **your class name**, with no package prefix and no `java.lang`, and the description is whatever you passed to `super()`.

## The recommendation, and why

> It is **highly recommended** to maintain our customized exceptions as **unchecked**, by extending `RuntimeException`.

The reason follows from part 7. Extend `Exception` instead and your exception is **checked**, which means every method that might propagate it needs a `throws` clause, and every caller above that, all the way up. You would be forcing your own API's users into paperwork for a condition they usually cannot do anything about.

> [!info] "Prefer unchecked" is now mainstream — most frameworks you will use, Spring included, wrap checked exceptions into unchecked ones for exactly the propagation reason above.

> **checked** exception is the compiler forcing a caller to make a decision, which is valuable only when the caller genuinely can recover — the `FileNotFoundException` → use-a-local-file case from part 1. The usable rule: **unchecked for programming errors and conditions nobody can recover from; checked for a recoverable condition that a caller must be made to think about.** Durga Sir's advice is the right default, not an absolute.

> [!important] **One more note from the PDF, easy to miss:** we can catch **any `Throwable` type, including `Error`s**. `catch (Error e)` compiles and works — part 3's table confirms it, since `Error` is unchecked and can be caught over any `try`. That it is *possible* is not a reason to do it; the reason not to is the one from part 2 — errors are **non-recoverable**, so there is nothing useful to put in the block.

---

# What this part established

| | |
|---|---|
| The five keywords | risky / handling / cleanup / hand over / delegate |
| Compile-time errors in the chapter | **eight**, all measured |
| A customized exception is | a class extending the `Throwable` hierarchy |
| Make it throwable by | `extends RuntimeException` (or another `Throwable`) |
| Make its message appear by | calling `super(s)` in the constructor |
| Raise it with | **`throw`** — nothing else ever will |
| Checked or unchecked | **unchecked is recommended**, to avoid forcing `throws` on every caller |

