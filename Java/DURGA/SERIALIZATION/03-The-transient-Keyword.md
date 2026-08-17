# The `transient` keyword

> In the serialization context there is one keyword which plays a very important role. Very important for the interview room too.

## Where it can be applied

**Before the purpose, the placement.**

> **`transient` is a modifier applicable only for variables.** You cannot apply it to methods, you cannot apply it to classes. **Variables only.**

---

# Why it exists

**Serialization writes to a file, and a file is on the hard disk — permanent storage.**

> In serialization we are saving our data permanently, for future purpose. But while saving data there may be a chance of some sensitive information.

> [!info] **The mail ID and the password.** He has a valuable document he wants to share with the class. Can you please share your mail ID? — everyone in the classroom can share that. Can you please share your password also? — **no one is going to share.**
>
> Because if I know both the mail ID and the password, there may be a chance of misuse. Mail ID you can publish anywhere; password we should not publish anywhere.
>
> **Same with an ATM card.** The ATM card you can keep anywhere, but the PIN number we should not.

**So: two variables, `i` is the username and `j` is the password.** You can save the username. You must not save the password.

> **At the time of serialization, if we don't want to save the value of a particular variable — to meet security constraints — we have to declare that variable as `transient`.**

> **`transient` means: not to serialize. Don't save the value of this variable.**

---

# What actually happens

> **At the time of serialization, the JVM ignores the original value of a transient variable and saves the default value to the file.**

```java
class Dog implements Serializable {
    int i = 10;
    transient int j = 20;
}
```

Measured on JDK 25:

```
transient int i, plain int j  -> 0 20
```

**And with both transient:** both default values are saved, so the output is `0 0`.

| Declaration | Output |
|---|---|
| `int i = 10; int j = 20;` | `10 20` |
| `int i = 10; transient int j = 20;` | `10 0` |
| `transient int i = 10; transient int j = 20;` | `0 0` |

> [!important] **The default value, not `nothing`.** The variable still exists in the deserialized object — it just holds the type's default. `0` for `int`, `0.0` for `double`, `false` for `boolean`, and **`null` for any reference type.** A `transient String password` comes back **`null`**, not `""`.

---

# `static` versus `transient`

**The first of the two loopholes.**

```java
class Dog implements Serializable {
    int i = 10;
    static int j = 20;
}
```

**Which variable is created first?** `j` — static variable, at the time of class loading only.

**And when you create `new Dog()`, only the instance variable comes with the object.**

> **A static variable is class-level data, nowhere related to the object. Serialization is a concept applicable only to objects.**

> **Static variable is not part of the object state, and hence it won't participate in serialization.**

Measured on JDK 25:

```
int i, transient static int j -> 10 20
```

**The `20` still prints — but look at where it comes from:**

> [!important] **`d2.i` comes from the file. `d2.j` comes from the method area.** The static was never in the file at all; deserialization simply reads the live class-level value that was already there.
>
> **And therefore:**
>
> > **If it is not participating in serialization, declaring a static variable as `transient` has no use and no impact at all.**
>
> Measured: `static int j` and `transient static int j` produce **identical** output.

---

# `final` versus `transient`

**The second loophole, and the more interesting one.**

## The reasoning he gives

> **`final` means constant. At compile time only, every final variable will be replaced by the value. At run time a final variable is not in variable form.**

```java
final int a = 10;
int   b = 20;

System.out.println(a);      // compiler replaces this with 10
System.out.println(b);      // has to read the variable
```

> If the value of `a` is always 10, why do I have to wait until run time? At compile time only, `a` will be replaced by 10 — and the compiler is responsible for that replacement.

**So the chain of reasoning is:** the JVM checks whether a variable is `transient` **only if it is in variable form**. A final constant is not in variable form by the time the code runs. **Hence declaring a final variable `transient` has no impact.**

```java
class Dog implements Serializable {
    transient int i = 10;
    transient final int j = 20;
}
```

Measured on JDK 25:

```
transient i, transient final j -> 0 20
```

**`i` came back as 0. `j` printed 20 despite being transient.** The conclusion holds.

> [!question]- **Deep dive — the object actually holds `0`, and the bytecode shows why. Also: the rule has a boundary he doesn't mention, and it will catch you.** Open this one; the boundary is the part that shows up in real code.
>
> **The printed `20` is not coming out of the object.** Reflection on the very same deserialized object, on JDK 25:
>
> ```
> transient i, transient final j -> 0 20   <- as printed
>    reflection says j is really   : 0
> ```
>
> **And the stream itself contains no fields at all:**
> ```
> AC ED 00 05 73 72 00 03 44 33 66 ... 02 00 00 78 70
>                                            ^^^^^
>                                      field count = 0
> ```
>
> **The bytecode of the print statement settles it:**
> ```
> 65: bipush 20
> 67: invokedynamic makeConcatWithConstants
> ```
> **`bipush 20` — the literal is pushed directly. There is no `getfield` instruction.** The compiler replaced `o.j` with `20` at the call site, exactly as he says. The field was never read, so it does not matter that it holds `0`.
>
> **So the mechanism is right, but state it precisely:** `transient final` still writes nothing and the field still deserializes to its default. **What hides that is constant inlining at the read site**, not anything serialization does.
>
> ##### The boundary: this only works for **constant variables**
>
> A field is a **constant variable** only if it is `final`, of a **primitive or `String`** type, and initialized with a **compile-time constant expression**. Anything else is a normal field that is genuinely read at run time.
>
> Measured on JDK 25, all four fields `transient final`:
>
> | Field | Printed | Actually in the object |
> |---|---|---|
> | `transient final int constant = 20;` | **20** | 0 |
> | `transient final int computed = compute();` | **0** | 0 |
> | `transient final String s = "hello";` | **hello** | null |
> | `transient final Integer boxed = 42;` | **null** | null |
>
> **`computed` and `boxed` are not constant variables**, so nothing is inlined, the real field is read, and the transient default comes straight through. **`Integer boxed = 42` is the nastiest of the four** — it looks identical to the `int` case and returns `null`.
>
> **The safe form of the rule:** declaring a final variable `transient` has no visible impact when the field is a compile-time constant, because reads of it are inlined. For every other final field, `transient` behaves normally and you get the default value.

---

# The summary table

**His own table, and he treats it as the thing to memorise.**

| Declaration | Output |
|---|---|
| `int i = 10;`<br>`int j = 20;` | **`10 20`** |
| `transient int i = 10;`<br>`int j = 20;` | **`0 20`** |
| `transient int i = 10;`<br>`transient static int j = 20;` | **`0 20`** — static: no impact |
| `transient int i = 10;`<br>`transient final int j = 20;` | **`0 20`** — final constant: no impact |
| `transient static int i = 10;`<br>`transient static int j = 20;` | **`10 20`** — neither participates |

> [!important] **Read the table as one rule with two exemptions.** `transient` zeroes an instance variable. **It does nothing to a `static` (not part of the object) and nothing visible to a `final` constant (inlined before run time).** Those two are the entire content of the questions on this topic.

---

# What this part established

| | |
|---|---|
| `transient` applies to | **variables only** — not methods, not classes |
| Its purpose | **not to save the value** — security constraints |
| The examples | **password**, **PIN number** |
| At serialization time | the JVM **ignores the original value and saves the default** |
| Default for a reference type | **`null`** |
| `transient` means | **do not serialize this variable** |
| A static variable is | **class-level data, not part of object state** |
| So a static | **does not participate** in serialization |
| `transient static` | **no use, no impact** |
| After deserialization, a static's value | comes from the **method area**, never the file |
| A final constant is | **replaced by its value at compile time** |
| `transient final` (constant) | **no visible impact** — the read is inlined |
| ⚠️ But the field really holds | the **default** — `transient final Integer` prints **`null`** |
| The precise rule | inlining applies only to **primitive/`String` finals with constant initialisers** |
