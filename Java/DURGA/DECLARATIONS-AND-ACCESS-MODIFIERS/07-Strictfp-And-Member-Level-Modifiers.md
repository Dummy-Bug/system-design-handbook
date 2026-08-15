# `strictfp`

The last of the class-level modifiers, and the newest — *"a bit new modifier for you people."*

| | |
|---|---|
| Full name | **strict floating point** (`f` and `p` lowercase) |
| Introduced in | **Java 1.2** — not there from 1.0 |
| Applicable to | **classes and methods** |
| **Not** applicable to | **variables** |
| Status | **redundant since Java 17** — all floating point is strict by default |

That last row mirrors `abstract`: both apply to classes and methods, neither applies to variables.

Measured on JDK 25:

```java
class SFPvar { strictfp int x = 10; }
```

```
error: modifier strictfp not allowed here
```

## What problem it was invented for

```java
System.out.println(10.0 / 3);
```

What is the answer? `3.333333…` — **and how many threes?**

> **The result of floating-point arithmetic used to vary from platform to platform**, and that is
> intolerable for Java specifically: *"I don't want a platform-dependent result, because **Java is a
> platform-independent language**."*

`strictfp` was the fix. Declare a method `strictfp` and:

> **All floating-point calculations in that method must follow the IEEE 754 standard**, so that we get
> platform-independent results.

At class level it is the same rule applied wholesale — every floating-point calculation in every
concrete method follows IEEE 754, which saves writing `strictfp` on all hundred methods individually.

> [!info] **What IEEE 754 says is not a Java programmer's problem.** *"What rules are there — not
> required to worry, it is not in the Java programmer's scope."* The shape of it: a fixed set of rules
> saying how many digits to keep and how to round, applied identically **whether the processor is
> 16-bit, 32-bit or 64-bit**. Same rules everywhere means same answer everywhere.

## The keyword is now redundant

**Java 17 made every floating-point expression strict, everywhere, whether you ask for it or not.**
The problem `strictfp` existed to solve is solved for you by default, so writing the keyword adds
nothing — and `javac` says so. Measured on JDK 25:

```
warning: [strictfp] as of release 17, all floating-point expressions are evaluated strictly
         and 'strictfp' is not required
```
```java
System.out.println(10.0 / 3);   // 3.3333333333333335 — the same on every platform
```

**The keyword is still legal and every syntax rule below still holds**, so it remains examinable. It
is simply decoration on modern Java.

> [!question]- **Deep dive — what the hardware was actually doing, and why the default could finally
> flip.** The reason a division could give different answers on different machines.
>
> On old **x87** floating-point hardware, intermediate results were held in **80-bit registers**. A
> calculation could therefore be carried at *more* precision than the `double` it was stored into, and
> so be **differently rounded** depending on how many intermediates the processor happened to keep in
> registers. Two machines, same source, different last digit.
>
> `strictfp` forced every intermediate down to 32/64-bit, which cost performance — which is exactly why
> it was opt-in rather than the default.
>
> **Modern hardware (SSE2 onward) works at 32/64-bit natively, at no cost.** Once the penalty
> disappeared there was no reason to keep the loophole, so JEP 306 — *Restore Always-Strict
> Floating-Point Semantics* — made strictness universal in Java 17 and the modifier became a no-op.

## `abstract` + `strictfp`

This pair is legal in one place and illegal in the other, and the reason is worth deriving.

> **A `strictfp` method always talks about implementation** — it is a statement about how the
> calculations *inside the body* behave.
> **An abstract method never talks about implementation** — it has no body.
>
> Hence **`abstract strictfp` is an illegal combination for methods.**

Measured on JDK 25:

```java
abstract class AbsM { abstract strictfp void m1(); }
```
```
error: illegal combination of modifiers: abstract and strictfp
```

**But at class level it is fine:**

```java
abstract strictfp class AbsC { }
```

Compiles.

> [!important] **Why the contradiction disappears at class level.** A class can hold both kinds of
> method. **`strictfp` takes care of the concrete methods; `abstract` takes care of the abstract ones.**
> The two modifiers are talking about different members, so they never meet.
>
> Contrast this with `final` + `abstract`, which is illegal at **both** levels — there the two words
> contradict each other about the *same* thing.

---

# Member level modifiers

*Member* means **method or variable**. Four access modifiers, in order of increasing reach.

---

## `public`

> **If a member is declared `public`, we can access that member from anywhere.**

And then the twist he warns about before anyone gets comfortable.

```java
package pack1;

class A {                                  // NOT public
    public void m1() { … }                 // public
}
```

From another package, `m1` is `public` — so it should be reachable. Measured on JDK 25:

```
error: A is not public in pack1; cannot be accessed from outside package
```

> [!important] **The rule to take away:**
> > **Before checking member visibility, we have to check class visibility.**
>
> *"Even though the method is public, the class is not public — that's why it is useless."* **Both the
> class and the member must be public** before anything outside the package can reach it.

And the mirror case — public class, default method. Measured on JDK 25:

```
error: m1() is not public in A2; cannot be accessed from outside package
```

Two different messages for the two different failures: the first names the **class**, the second names
the **method**.

---

## default

> **If a member is declared default** (no modifier written) **we can access it only within the current
> package.** From outside the package, we cannot.
>
> **Hence default access is also known as package level access.**

---

## `private`

> **If a member is `private`, we can access it only within the class.** From outside the class, we
> cannot — not even from a subclass.

**And `private abstract` is illegal**, for a reason that is pure logic:

> **An abstract method must be available to the child classes so they can provide the implementation.
> Private methods are not available to the child classes. Hence `private abstract` is an illegal
> combination for methods.**

Measured on JDK 25:

```
error: illegal combination of modifiers: abstract and private
```

> [!info] **Three illegal pairs, one pattern.** `final abstract`, `strictfp abstract`, `private
> abstract` — every one of them pairs `abstract` with something that contradicts *"a child will
> implement this later."* `final` says nobody may override it, `strictfp` says the body behaves a
> certain way, `private` says nobody can see it.

---

## `protected` — the most misunderstood modifier in Java

He names it that before explaining it, and the rest of the session earns the label.

> **If a member is declared `protected`, we can access it:**
> - **anywhere within the current package**, and
> - **outside the package, only in child classes.**

Or as a formula:

> **protected = default + kids**

## Within the same package — all three forms work

```java
package pack1;

public class A {
    protected void m1() { System.out.println("the most misunderstood modifier"); }
}
```

```java
package pack1;

public class B extends A {
    public static void main(String[] args) {
        A a = new A();   a.m1();     // parent reference, parent object
        B b = new B();   b.m1();     // child reference, child object
        A a1 = new B();  a1.m1();    // parent reference, child object
    }
}
```

Measured on JDK 25:

```
the most misunderstood modifier
the most misunderstood modifier
the most misunderstood modifier
```

**All three.** Inside the package, a protected member behaves exactly like a default one — parent
reference or child reference, it does not matter.

## Outside the package — only one form works

Same three shapes, now from `pack2`, in a class `C extends A`. Measured on JDK 25:

| | Code | Result |
|---|---|---|
| 1 | `A a = new A(); a.m1();` | ❌ `m1() has protected access in A` |
| 2 | `C c = new C(); c.m1();` | ✅ **valid** |
| 3 | `A a1 = new C(); a1.m1();` | ❌ `m1() has protected access in A` |

**Look at what 1 and 3 have in common: the reference type is `A`.** 2 is the only one whose reference
type is the child.

> **Outside the package we can access protected members only in child classes, and we must use the
> child reference. A parent reference cannot be used to access protected members from outside the
> package.**

## The six-case puzzle

Now three levels: `A` in `pack1`; `C extends A` and `D extends C` in `pack2`. `main` is in **`D`**.

Measured on JDK 25:

| | Code | Result |
|---|---|---|
| 1 | `A a = new A(); a.m1();` | ❌ |
| 2 | `C c = new C(); c.m1();` | ❌ |
| 3 | `D d = new D(); d.m1();` | ✅ **valid** |
| 4 | `A a1 = new C(); a1.m1();` | ❌ |
| 5 | `A a1 = new D(); a1.m1();` | ❌ |
| 6 | `C c1 = new D(); c1.m1();` | ❌ |

**Exactly one of the six compiles.** Every failure is `error: m1() has protected access in A`.

> [!important] **The rule, in its full and final form:**
> > **Outside the package, we can access protected members only in child classes, and we must use
> > *that particular child class's* reference.**
>
> *"From `D` class, if we want to access, we should use `D` class reference only."*
>
> Case 2 is the one that catches everybody — `C` **is** a child of `A`, and `c` **is** a child
> reference. But the access is happening **inside `D`**, and from inside `D` the only reference type
> that works is `D`. Case 6 catches the rest: `new D()` is a `D` object, but the *reference* is `C`, and
> the reference type is what the compiler checks.
>
> When he ran this live the class first answered "three valid", then "two", then "one" — and the
> answer is one.

> [!question]- **Deep dive — why the rule is about the reference type and not the object.** The reason
> the JLS gives, and it makes the six cases obvious rather than arbitrary.
>
> The purpose of `protected` is to let a subclass work on **its own inherited state** — not to give it
> a general key to every instance of the parent. If `D` could call `a.m1()` on any `A`, then any class
> anywhere could reach a protected member just by declaring itself a subclass and then handling other
> people's objects. The subclass would become a loophole in the parent's encapsulation.
>
> So the language restricts it: from inside `D`, a protected member of `A` is accessible only through a
> reference **of type `D` or a subtype** — that is, only on objects that are *"me or my kind"*. Since
> the compiler works from the **static** reference type, `C c1 = new D()` fails even though the object
> really is a `D`.

---

# The visibility summary table

| Accessed from | `private` | default | `protected` | `public` |
|---|:---:|:---:|:---:|:---:|
| within the **same class** | ✅ | ✅ | ✅ | ✅ |
| **child** class of the **same package** | ❌ | ✅ | ✅ | ✅ |
| **non-child** class of the **same package** | ❌ | ✅ | ✅ | ✅ |
| **child** class **outside** the package | ❌ | ❌ | ✅ ***child reference only*** | ✅ |
| **non-child** class **outside** the package | ❌ | ❌ | ❌ | ✅ |

**Two conclusions read straight off it:**

> **The most restricted access modifier is `private`. The most accessible is `public`.**
>
> **`private` < default < `protected` < `public`**

---

# Which to use

> **Recommended modifier for a data member (variable): `private`.**
> **Recommended modifier for a method: `public`.**

The reasoning is one sentence each:

- **Variables private** — because of **data hiding**, the OOP principle. *"In C the default modifier
  for a variable is private only."*
- **Methods public** — *"a method is my service, and my service should be accessible to several
  people."*

Data in, behaviour out.

---

# What this part established

| | |
|---|---|
| `strictfp` | **strict floating point**, introduced in **1.2** |
| Applies to | classes and methods — **not** variables |
| Its purpose | **platform-independent** floating-point results via **IEEE 754** |
| Since **Java 17** | **redundant** — all floating point is strict by default (JEP 306), and javac warns |
| `abstract strictfp` method | ❌ `illegal combination of modifiers` |
| `abstract strictfp` class | ✅ legal — the two modifiers govern different members |
| `public` member | reachable from anywhere — **but the class must be public too** |
| The rule | **check class visibility before member visibility** |
| default | **package level access** |
| `private` | within the class only |
| `private abstract` | ❌ — abstract needs a child to implement it; private hides it from children |
| `protected` = | **default + kids** |
| Inside the package | parent **or** child reference, both fine |
| Outside the package | **only in child classes**, and **only through that child's own reference** |
| The six-case puzzle | exactly **one** of six compiles |
| Why reference type, not object | otherwise any subclass would be a loophole in the parent's encapsulation |
| Most restricted → most accessible | `private` < default < `protected` < `public` |
| Recommended for variables | **`private`** — data hiding |
| Recommended for methods | **`public`** — a method is a service |
