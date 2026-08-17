# `final`

## What the word means before it means anything in Java

> [!question]- **Deep dive — the final price story, on why `final` means what it means.** His way in to the keyword, and it is worth keeping because the everyday meaning is exactly the technical one.
>
> His driver bargains at a traffic signal for a platform toy:
>
> - Vendor: **200 rupees.**
> - Driver: give it for 10 — the vendor looks him up and down.
> - Vendor: 150.
> - Driver: no. 10 rupees. **It's my final price.**
> - The vendor walks away, comes back: at least 50? — no, 10.
> - Walks away again, comes back 30 seconds later: **last final price, 20 rupees. No change.**
>
> They settle at 20. (And the toy breaks in ten minutes at home — even that 20 rupees also waste.)
>
> **Final in ordinary speech means exactly what it means in Java: this decision is not open to revision.** Is this cost final? Is this date final? There is no change in that.

## `final` methods

Whatever methods a parent has are available to the child through inheritance. If the child is not satisfied with the parent's implementation, the child may **redefine** it — that is **overriding**.

> **If a parent class method is declared `final`, we cannot override that method in the child class, because its implementation is final.**

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

> [!info] **The two words in that message are worth separating.** The **parent's** method is the **overridden** method. The **child's** method is the **overriding** method. The error says `overridden method is final` — it is complaining about the parent's.

## `final` classes

> [!info] **Why `extends` is called extends.** A parent has 10 methods. Somebody needs those 10 **plus 5 more**. They create a child class and add the 5 — the child now has **15**. Extending means adding extra. We are extending existing functionality. Anyone happy with the original 10 uses the parent; anyone needing the extended set uses the child.

> **If a class is declared `final`, we cannot extend its functionality — we cannot create a child class for it. That is, inheritance is not possible for final classes.**

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

The reasoning is airtight: a method is overridable only in a child class; a final class **has** no child class; therefore no method in it can ever be overridden; therefore all of them are effectively final.

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

> [!important] **Why the two differ.** Final means different things for the two: for a **method** it means **cannot be overridden**, and a final class removes the only place overriding could happen. For a **variable** it means **cannot be reassigned**, and a final class does nothing to stop reassignment inside its own body. The class-level `final` closes the door on inheritance only — and only methods depend on inheritance for their mutability.

## When to use it — and when not to

> **The main advantage of `final`: we can achieve security, and we can provide a unique implementation for all.** Nobody can change your implementation or extend your functionality.

**And the cost:**

| `final` on a | Kills |
|---|---|
| **class** | **inheritance** |
| **method** | **polymorphism** |

> **The main disadvantage of `final` is that we are missing the key benefits of OOP — inheritance (because of final classes) and polymorphism (because of final methods). Hence, if there is no specific requirement, it is not recommended to use `final`.**

> The most dangerous keyword in Java is `final`. Just for style purpose, just for fancy purpose, don't use `final` — a number of features we are going to miss.

---

---

# What this part established

| | |
|---|---|
| `final` method | **cannot be overridden** — `overridden method is final` |
| `final` class | **cannot be extended** — `cannot inherit from final P2` |
| Every **method** in a final class | is **implicitly final** |
| Every **variable** in a final class | is **not** — reassignment still works |
| `final`'s advantage | **security**, unique implementation |
| `final`'s cost | **inheritance** and **polymorphism** |
| Recommendation | **don't use it without a specific requirement** |
