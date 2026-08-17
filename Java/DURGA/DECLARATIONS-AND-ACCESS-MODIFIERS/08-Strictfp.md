# `strictfp`

The last of the class-level modifiers, and the newest — a bit new modifier for you people.

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

> **The result of floating-point arithmetic used to vary from platform to platform**, and that is intolerable for Java specifically: I don't want a platform-dependent result, because **Java is a platform-independent language**.

`strictfp` was the fix. Declare a method `strictfp` and:

> **All floating-point calculations in that method must follow the IEEE 754 standard**, so that we get platform-independent results.

At class level it is the same rule applied wholesale — every floating-point calculation in every concrete method follows IEEE 754, which saves writing `strictfp` on all hundred methods individually.

> [!info] **What IEEE 754 says is not a Java programmer's problem.** What rules are there — not required to worry, it is not in the Java programmer's scope. The shape of it: a fixed set of rules saying how many digits to keep and how to round, applied identically **whether the processor is 16-bit, 32-bit or 64-bit**. Same rules everywhere means same answer everywhere.

## The keyword is now redundant

**Java 17 made every floating-point expression strict, everywhere, whether you ask for it or not.** The problem `strictfp` existed to solve is solved for you by default, so writing the keyword adds nothing — and `javac` says so. Measured on JDK 25:

```
warning: [strictfp] as of release 17, all floating-point expressions are evaluated strictly
         and 'strictfp' is not required
```
```java
System.out.println(10.0 / 3);   // 3.3333333333333335 — the same on every platform
```

**The keyword is still legal and every syntax rule below still holds**, so it remains examinable. It is simply decoration on modern Java.

> [!question]- **Deep dive — what the hardware was actually doing, and why the default could finally flip.** The reason a division could give different answers on different machines.
>
> On old **x87** floating-point hardware, intermediate results were held in **80-bit registers**. A calculation could therefore be carried at **more** precision than the `double` it was stored into, and so be **differently rounded** depending on how many intermediates the processor happened to keep in registers. Two machines, same source, different last digit.
>
> `strictfp` forced every intermediate down to 32/64-bit, which cost performance — which is exactly why it was opt-in rather than the default.
>
> **Modern hardware (SSE2 onward) works at 32/64-bit natively, at no cost.** Once the penalty disappeared there was no reason to keep the loophole, so JEP 306 — **Restore Always-Strict Floating-Point Semantics** — made strictness universal in Java 17 and the modifier became a no-op.

## `abstract` + `strictfp`

This pair is legal in one place and illegal in the other, and the reason is worth deriving.

> **A `strictfp` method always talks about implementation** — it is a statement about how the calculations **inside the body** behave.
> **An abstract method never talks about implementation** — it has no body.
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

> [!important] **Why the contradiction disappears at class level.** A class can hold both kinds of method. **`strictfp` takes care of the concrete methods; `abstract` takes care of the abstract ones.** The two modifiers are talking about different members, so they never meet.
>
> Contrast this with `final` + `abstract`, which is illegal at **both** levels — there the two words contradict each other about the **same** thing.

---

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
