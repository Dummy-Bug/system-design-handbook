# Why modifiers exist at all

> **Whenever we write our own classes, we have to provide some information about our class to the JVM.**

What kind of information?

| Question the JVM needs answered | How you answer it |
|---|---|
| Can this class be accessed from anywhere? | declare it **`public`** — or not |
| Is child class creation possible? | declare it **`final`** — or not |
| Is object creation possible? | declare it **`abstract`** — or not |

> **We specify this information by declaring the class with the appropriate modifier.** That is the whole job of a modifier: it is how you talk to the JVM about your class.

---

# How many modifiers a class may have

## Top-level classes — five

> **The only applicable modifiers for top-level classes are:**
> **`public`, default, `final`, `abstract`, `strictfp`.**

Measured on JDK 25 — every modifier tried on a top-level class:

| Modifier | Top-level class |
|---|---|
| `public` | ✅ |
| (default — nothing written) | ✅ |
| `final` | ✅ |
| `abstract` | ✅ |
| `strictfp` | ✅ |
| `private` | ❌ `modifier private not allowed here` |
| `protected` | ❌ `modifier protected not allowed here` |
| `static` | ❌ `modifier static not allowed here` |
| `synchronized` | ❌ `modifier synchronized not allowed here` |
| `native` | ❌ `modifier native not allowed here` |
| `transient` | ❌ `modifier transient not allowed here` |
| `volatile` | ❌ `modifier volatile not allowed here` |

## Inner classes — eight

> **For inner classes the applicable modifiers are those five, plus `private`, `protected` and `static`.**

Measured on JDK 25 — the same sweep, this time on a class declared inside another class:

| Extra modifier | Inner class |
|---|---|
| `private` | ✅ |
| `protected` | ✅ |
| `static` | ✅ |
| `synchronized`, `native`, `transient`, `volatile` | ❌ still rejected |

> **Top-level classes: 5. Inner classes: 8.** The three extra ones are exactly the three that need an enclosing class to mean anything — private **to what**, protected **from what**, static **relative to what**.

---

# The exam trick worth its own section

A question of the form — is this code valid?

```
11.  private class A { }
12.  static class B { }
13.
14.  public static void main(String[] args) {
15.      System.out.println("hello");
16.  }
```

> Most of the people are going to fail. The instinct is: top-level classes cannot be `private` or `static`, therefore invalid.

**It is valid.** And the tell is in the **line numbers**.

> [!important] **Read the first line number.**
> - Starts at **1** → this is the whole program; those are **top-level** classes, and `private` / `static` would be errors.
> - Starts at **11** → ten lines already came before it, so there is an **enclosing class**. These are **inner** classes — and `private` and `static` are perfectly legal on inner classes.
>
> Who told you these are top-level classes? The `main` method sitting outside the two classes is the second clue: for `main` to be there at all, something must enclose it.

**This knowledge is the answer to the question, not the Java rule.** The rule you already know; the skill is noticing which rule applies.

---

# Access specifiers vs access modifiers

> A very important confusion, especially in Ameerpet.

**In C++ the two words mean different things:**

| Word | Members |
|---|---|
| access **specifiers** | `public`, `private`, `protected`, default |
| **modifiers** | `final`, `static`, `abstract`, … everything else |

> [!important] **In Java there is no such thing as a specifier.**
> > **All twelve are modifiers. The word specifier does not exist in Java.**
>
> **And the compiler proves it.** Measured on JDK 25:
> ```java
> private class Test { }
> ```
> ```
> error: modifier private not allowed here
> ```
> If it were a specifier, the error should say **specifier** private. But here — **modifier** private. The message is the evidence.

---

# `public` classes

> **If a class is declared `public`, we can access that class from anywhere** — within the package or outside it.

## What happens when it is not

```java
package pack1;

class A {                              // not public
    public void m1() { System.out.println("hello"); }
}
```

```java
package pack2;

class B {
    public static void main(String[] args) {
        A a = new A();
        a.m1();
    }
}
```

**Compiling `A` is fine** — nothing depends on anything. Compiling `B` is not. And the errors arrive in stages, which is worth watching:

**Stage 1 — no import at all.** The compiler has never heard of `A`:

```
cannot find symbol
  symbol:   class A
  location: class pack2.B
```

**Stage 2 — add `import pack1.A;`.** Now it finds the class and objects to something else — and the error **count goes up**, because the import line itself is now wrong too:

```
pack1.A is not public in pack1; cannot be accessed from outside package
```

> Durga, you are using `A` — where is it available? Inside `pack1`. Now I check inside `pack1`: `A` is there, **but it is not public**.

**Stage 3 — declare `A` public.** Everything compiles, and `java pack2.B` prints `hello`.

---

# default classes

> **If a class is declared default, we can access that class only within the current package. From outside the package we cannot.**

> **Hence default access is also known as package level access.**

This is the same rule as the failure above, stated from the other side.

---

# What this part established

| | |
|---|---|
| A modifier is | how you tell the **JVM** about your class's behaviour |
| Top-level class modifiers | **5** — `public`, default, `final`, `abstract`, `strictfp` |
| Inner class modifiers | **8** — those plus `private`, `protected`, `static` |
| Everything else | `modifier X not allowed here` |
| The exam trick | **read the first line number** — starting at 11 means these are **inner** classes |
| Access specifiers | do **not** exist in Java — all twelve are **modifiers** |
| The proof | the compiler says `modifier private not allowed here` |
| `public` class | accessible from anywhere |
| Non-public class from outside | `pack1.A is not public in pack1; cannot be accessed from outside package` |
| default class | **package level access** |
