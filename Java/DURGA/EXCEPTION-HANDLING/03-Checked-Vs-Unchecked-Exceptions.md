# The definitions

> **Checked exceptions:** the exceptions which are **checked by the compiler**, whether the programmer is handling them or not, **for smooth execution of the program at runtime**.
> Examples: `FileNotFoundException`

> **Unchecked exceptions:** the exceptions which are **not checked by the compiler**, whether the programmer is handling them or not.
> Examples: `ArithmeticException`, `NullPointerException`


> [!important] **Whether an exception is checked or unchecked, it must occur at *runtime* only. There is no chance of any exception occurring at compile time.**
>
> What you get at compile time are **syntactical mistakes** — and those are not exceptions at all. Nothing about the checked/unchecked split has anything to do with *when the exception happens*. It is entirely about **who checks whether you have prepared for it.**


> [!important] **The obligation that comes with "checked".** In your program, if there is **any chance** of a checked exception being raised, you **must** handle it — either with **`try`/`catch`** or with the **`throws`** keyword — otherwise **the code will not compile.**

And the rule that decides which is which, for real Java types:

> **`RuntimeException` and its child classes, and `Error` and its child classes, are unchecked.** All the remaining are **checked**.

> [!info] **A useful shortcut he gives.** Wherever a JDK method declares `throws SomethingException` in its signature, that exception is a checked one — `CertificateException`, `RemoteException`, `SQLException`, `FileNotFoundException`. The `throws` clause exists *because* the compiler is going to insist.

---

# Measured: what the compiler actually does

## A checked exception, unhandled

```java
import java.io.*;

class Checked {
    public static void main(String[] args) {
        PrintWriter pw = new PrintWriter("abc.txt");
        pw.println("hello");
    }
}
```

`javac` on JDK 25:

```
Checked.java:5: error: unreported exception FileNotFoundException; must be caught or declared to be thrown
        PrintWriter pw = new PrintWriter("abc.txt");
                         ^
1 error

exit code: 1
```

Word for word what the lecture quotes. And read it carefully, because this is where the wrong answer at the top of this note comes from:

> [!warning] **This error does not say the exception occurred.** It says **`unreported`**. The compiler is saying: *there is a possibility of `FileNotFoundException` here, and you have not told me what you would do about it. Show me — then I will compile.* The file may well exist and the exception may never happen. That is irrelevant to the compiler.
>
> **`must be caught or declared to be thrown`** is the compiler naming your two options: `catch` it, or declare `throws`.

## An unchecked exception

```java
class Unchecked {
    public static void main(String[] args) {
        System.out.println(10/0);
    }
}
```

```
compile exit code: 0

Exception in thread "main" java.lang.ArithmeticException: / by zero
	at Unchecked.main(Unchecked.java:3)
```

**Compiles perfectly.** The compiler has nothing to say about a guaranteed division by zero sitting in plain sight — because `ArithmeticException` is unchecked.

## Both at once — the demonstration that settles it

```java
import java.io.*;

class Both {
    public static void main(String[] args) throws FileNotFoundException {
        PrintWriter pw = new PrintWriter("abc.txt");
        pw.println("hello");
        System.out.println(10/0);
    }
}
```

```
compile exit code: 0

Exception in thread "main" java.lang.ArithmeticException: / by zero
	at Both.main(Both.java:7)
```

Adding `throws FileNotFoundException` satisfies the compiler about the checked exception, and it **compiles cleanly** — while a `10/0` two lines later goes completely unremarked.

> [!important] **One program, both kinds, and the compiler polices exactly one of them.** That is the difference, demonstrated rather than asserted: the compiler checks `FileNotFoundException` and says nothing whatsoever about `ArithmeticException`.

---

# Fully checked versus partially checked


> A checked exception is **fully checked** if and only if **all its child classes are also checked**.
> Examples: `IOException`, `InterruptedException`

> A checked exception is **partially checked** if and only if **some of its child classes are unchecked**.
> Example: `Exception`

> [!important] **There are exactly two partially checked exceptions in Java: `Throwable` and `Exception`.**
>
> The reason falls straight out of the hierarchy from the previous note. `Exception` is checked — but `RuntimeException` is one of its children and is unchecked. `Throwable` is checked — but `Error` is one of its children and is unchecked. Nothing else in the hierarchy has that shape.

## Measured: partially checked is visible in the compiler

There is a rule that makes this observable. You may not `catch` a **fully checked** exception over a `try` block that cannot throw it — but you may always catch a **partially checked** one, because an unchecked descendant could arise anywhere.

Each of these is `try { System.out.println("hello"); } catch (X e) { }` — a `try` block that throws nothing at all:

| `catch (X)` | Result on JDK 25 |
|---|---|
| `Exception` | **compiles** |
| `Throwable` | **compiles** |
| `RuntimeException` | compiles *(unchecked)* |
| `ArithmeticException` | compiles *(unchecked)* |
| `Error` | compiles *(unchecked)* |
| `IOException` | ❌ `exception IOException is never thrown in body of corresponding try statement` |
| `FileNotFoundException` | ❌ `exception FileNotFoundException is never thrown in body of corresponding try statement` |
| `InterruptedException` | ❌ `exception InterruptedException is never thrown in body of corresponding try statement` |

> [!important] **The two that compile where the fully checked ones fail are exactly `Throwable` and `Exception`.** That is the partially-checked rule showing up as compiler behaviour rather than as a definition to memorise — and it is why `catch (Exception e)` is always legal while `catch (IOException e)` is not.

## The behaviour table

Straight from the chapter PDF as a question, and worth being able to answer instantly:

| Exception | Behaviour |
|---|---|
| `RuntimeException` | unchecked |
| `Error` | unchecked |
| `IOException` | **fully** checked |
| `Exception` | **partially** checked |
| `InterruptedException` | **fully** checked |
| `Throwable` | **partially** checked |
| `ArithmeticException` | unchecked |
| `NullPointerException` | unchecked |
| `FileNotFoundException` | **fully** checked |

---

# The whole distinction, assembled

| | Checked | Unchecked |
|---|---|---|
| Checked by the compiler | **yes** | no |
| Must you handle it | **yes** — `try`/`catch` or `throws`, else compile error | no |
| When does it occur | **runtime** | **runtime** |
| Why the compiler cares | common problems; checking makes the run smooth | too rare to be worth the cost of checking |
| The rule | everything not below `RuntimeException` or `Error` | `RuntimeException` + children, `Error` + children |
| Analogy | hall ticket, spare pen, diesel, spare tyre | bomb blast, fatal accident |

> [!important] **If you say only one sentence, say this one:** *checked exceptions are checked by the compiler for smooth execution at runtime, so you must handle them or declare them; unchecked exceptions are not checked by the compiler at all — and **both** occur only at runtime.* The last clause is what separates a correct answer from the common wrong one.
