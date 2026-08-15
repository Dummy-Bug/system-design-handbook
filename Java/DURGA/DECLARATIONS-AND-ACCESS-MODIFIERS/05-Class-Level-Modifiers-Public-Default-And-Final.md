# Why modifiers exist at all

> **Whenever we write our own classes, we have to provide some information about our class to the
> JVM.**

What kind of information?

| Question the JVM needs answered | How you answer it |
|---|---|
| Can this class be accessed from anywhere? | declare it **`public`** — or not |
| Is child class creation possible? | declare it **`final`** — or not |
| Is object creation possible? | declare it **`abstract`** — or not |

> **We specify this information by declaring the class with the appropriate modifier.** That is the
> whole job of a modifier: it is how you talk to the JVM about your class.

---

# How many modifiers a class may have

## Top-level classes — five

> **The only applicable modifiers for top-level classes are:**
> **`public`, default, `final`, `abstract`, `strictfp`.**

Measured on JDK 25 — every modifier tried on a top-level class:

| Modifier | Top-level class |
|---|---|
| `public` | ✅ |
| *(default — nothing written)* | ✅ |
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

> **For inner classes the applicable modifiers are those five, plus `private`, `protected` and
> `static`.**

Measured on JDK 25 — the same sweep, this time on a class declared inside another class:

| Extra modifier | Inner class |
|---|---|
| `private` | ✅ |
| `protected` | ✅ |
| `static` | ✅ |
| `synchronized`, `native`, `transient`, `volatile` | ❌ still rejected |

> **Top-level classes: 5. Inner classes: 8.** The three extra ones are exactly the three that need an
> enclosing class to mean anything — private *to what*, protected *from what*, static *relative to
> what*.

---

# The exam trick worth its own section

A question of the form *"is this code valid?"*:

```
11.  private class A { }
12.  static class B { }
13.
14.  public static void main(String[] args) {
15.      System.out.println("hello");
16.  }
```

> *"Most of the people are going to fail."* The instinct is: top-level classes cannot be `private` or
> `static`, therefore invalid.

**It is valid.** And the tell is in the **line numbers**.

> [!important] **Read the first line number.**
> - Starts at **1** → this is the whole program; those are **top-level** classes, and `private` /
>   `static` would be errors.
> - Starts at **11** → ten lines already came before it, so there is an **enclosing class**. These are
>   **inner** classes — and `private` and `static` are perfectly legal on inner classes.
>
> *"Who told you these are top-level classes?"* The `main` method sitting outside the two classes is
> the second clue: for `main` to be there at all, something must enclose it.

**This knowledge is the answer to the question, not the Java rule.** The rule you already know; the
skill is noticing which rule applies.

---

# Access specifiers vs access modifiers

> *"A very important confusion, especially in Ameerpet."*

**In C++ the two words mean different things:**

| Word | Members |
|---|---|
| access **specifiers** | `public`, `private`, `protected`, default |
| **modifiers** | `final`, `static`, `abstract`, … everything else |

> [!important] **In Java there is no such thing as a specifier.**
> > **All twelve are modifiers. The word "specifier" does not exist in Java.**
>
> **And the compiler proves it.** Measured on JDK 25:
> ```java
> private class Test { }
> ```
> ```
> error: modifier private not allowed here
> ```
> *"If it were a specifier, the error should say **specifier** private. But here — **modifier**
> private."* The message is the evidence.

---

# `public` classes

> **If a class is declared `public`, we can access that class from anywhere** — within the package or
> outside it.

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

**Compiling `A` is fine** — nothing depends on anything. Compiling `B` is not. And the errors arrive in
stages, which is worth watching:

**Stage 1 — no import at all.** The compiler has never heard of `A`:

```
cannot find symbol
  symbol:   class A
  location: class pack2.B
```

**Stage 2 — add `import pack1.A;`.** Now it finds the class and objects to something else — and the
error *count goes up*, because the import line itself is now wrong too:

```
pack1.A is not public in pack1; cannot be accessed from outside package
```

> *"Durga, you are using `A` — where is it available? Inside `pack1`. Now I check inside `pack1`: `A`
> is there, **but it is not public**."*

**Stage 3 — declare `A` public.** Everything compiles, and `java pack2.B` prints `hello`.

---

# default classes

> **If a class is declared default, we can access that class only within the current package. From
> outside the package we cannot.**
>
> **Hence default access is also known as package level access.**

This is the same rule as the failure above, stated from the other side.

---

# `final`

## What the word means before it means anything in Java

> [!question]- **Deep dive — the "final price" story, on why `final` means what it means.** His way in
> to the keyword, and it is worth keeping because the everyday meaning is exactly the technical one.
>
> His driver bargains at a traffic signal for a platform toy:
>
> - Vendor: **200 rupees.**
> - Driver: *"Give it for 10."* — the vendor looks him up and down.
> - Vendor: *"150."*
> - Driver: *"No. 10 rupees. **It's my final price.**"*
> - The vendor walks away, comes back: *"At least 50?"* — *"No, 10."*
> - Walks away again, comes back 30 seconds later: *"**Last final price, 20 rupees. No change.**"*
>
> They settle at 20. *(And the toy breaks in ten minutes at home — "even that 20 rupees also waste.")*
>
> **"Final" in ordinary speech means exactly what it means in Java: this decision is not open to
> revision.** Is this cost final? Is this date final? *There is no change in that.*

## `final` methods

Whatever methods a parent has are available to the child through inheritance. If the child is not
satisfied with the parent's implementation, the child may **redefine** it — that is **overriding**.

> [!question]- **Deep dive — the parent-and-child analogy he uses for overriding and `final`.** This
> example recurs in his OOP chapter too, so it is worth having in full.
>
> ```java
> class P {
>     public void property() { System.out.println("cash, land, gold"); }
>     public void marry()    { System.out.println("Subbalakshmi"); }
> }
> ```
>
> *"Every parent is very much eager to provide property to the kid"* — and *"majority of the time, the
> parent arranges the marriage also."* Both methods pass to the child.
>
> The child is **very satisfied** with `property()` and keeps it. The child is **not satisfied** with
> `marry()`, and redefines it:
>
> ```java
> class C extends P {
>     public void marry() { System.out.println("Trisha"); }
> }
> ```
>
> **That is overriding.** But sometimes the parent is strict: *"My decision is final. You are not
> allowed to redefine."* — and marks the method `final`.
>
> The child's last resort: *"then I'll remove `extends`."* To which the parent has one answer:
> **remove `extends` and the property does not come either.** *"If you want the property, if you want
> to be my kid, compulsorily you should respect my implementation."*

> **If a parent class method is declared `final`, we cannot override that method in the child class,
> because its implementation is final.**

Measured on JDK 25:

```java
public final void marry() { System.out.println("Subbalakshmi"); }
…
public void marry() { System.out.println("Trisha"); }     // in the child
```

```
error: marry() in C cannot override marry() in P
  overridden method is final
```

> [!info] **The two words in that message are worth separating.** The **parent's** method is the
> **overridden** method. The **child's** method is the **overriding** method. The error says *overridden
> method is final* — it is complaining about the parent's.

## `final` classes

> [!info] **Why `extends` is called extends.** A parent has 10 methods. Somebody needs those 10 **plus
> 5 more**. They create a child class and add the 5 — the child now has **15**. *"Extending means
> adding extra. We are extending existing functionality."* Anyone happy with the original 10 uses the
> parent; anyone needing the extended set uses the child.

> **If a class is declared `final`, we cannot extend its functionality — we cannot create a child class
> for it. That is, inheritance is not possible for final classes.**

Measured on JDK 25:

```java
final class P2 { }
class C2 extends P2 { }
```

```
error: cannot inherit from final P2
```

## The asymmetry worth memorising

> **Every method present inside a final class is always final by default.**

The reasoning is airtight: a method is overridable only in a child class; a final class **has** no
child class; therefore no method in it can ever be overridden; therefore all of them are effectively
final.

> **But every variable present inside a final class need NOT be final.**

Measured on JDK 25:

```java
final class B {
    static int x = 10;
    public static void main(String[] args) {
        x = 7777;
        System.out.println(x);
    }
}
```

```
7777
```

**The reassignment succeeded.** If `x` were final, `x = 7777` would be rejected. It is not.

> [!important] **Why the two differ.** "Final" means different things for the two: for a **method** it
> means *cannot be overridden*, and a final class removes the only place overriding could happen. For a
> **variable** it means *cannot be reassigned*, and a final class does nothing to stop reassignment
> inside its own body. The class-level `final` closes the door on inheritance only — and only methods
> depend on inheritance for their mutability.

## When to use it — and when not to

> **The main advantage of `final`: we can achieve security, and we can provide a unique implementation
> for all.** Nobody can change your implementation or extend your functionality.

**And the cost:**

| `final` on a | Kills |
|---|---|
| **class** | **inheritance** |
| **method** | **polymorphism** |

> **The main disadvantage of `final` is that we are missing the key benefits of OOP — inheritance
> (because of final classes) and polymorphism (because of final methods). Hence, if there is no
> specific requirement, it is not recommended to use `final`.**

> *"The most dangerous keyword in Java is `final`. Just for style purpose, just for fancy purpose,
> don't use `final` — a number of features we are going to miss."*

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
| `final` method | **cannot be overridden** — `overridden method is final` |
| `final` class | **cannot be extended** — `cannot inherit from final P2` |
| Every **method** in a final class | is **implicitly final** |
| Every **variable** in a final class | is **not** — reassignment still works |
| `final`'s advantage | **security**, unique implementation |
| `final`'s cost | **inheritance** and **polymorphism** |
| Recommendation | **don't use it without a specific requirement** |
