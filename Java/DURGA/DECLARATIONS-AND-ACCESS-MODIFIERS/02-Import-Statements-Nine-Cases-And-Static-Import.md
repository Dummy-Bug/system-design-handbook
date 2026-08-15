# Case 1 — the two types of import statement

> **There are two types of import statements:**
> **1. explicit class import** — `import java.util.ArrayList;`
> **2. implicit class import** — `import java.util.*;`

## Which one to use

Asked to the class, and the popular answer is *"depends on the requirement — one or two classes,
explicit; twenty classes, implicit."* He rejects it.

> **It is highly recommended to use explicit class import, because it improves readability of the
> code.** Even for a hundred classes from the same package.
>
> **Implicit class import is not recommended.**

## The story that makes the case

A program that begins:

```java
import com.hdfc.*;
import com.icicibank.*;
```

Somewhere inside it:

```java
Account a = new Account();
a.getInfo();
```

You are doing code-work — reading it so you can extend it tomorrow — and you need to see how
`getInfo()` is implemented. **Which package is `Account` in?**

> *"I opened `com.hdfc` — almost 15 minutes I spent, and I didn't see `Account` anywhere. Then I
> opened `com.icicibank`, and there I could see the `Account` class."*

Then a few lines later, `Loan l = new Loan();` — and the search starts over, in the other order.

Now write the imports explicitly:

```java
import com.hdfc.Account;
import com.icicibank.Loan;
```

**The question answers itself from the top of the file.** `Loan` is in `icicibank`, `Account` is in
`hdfc`. You never open a package to find out.

> [!important] **His answer to "but explicit means more typing."**
> **Typing is a one-time activity. Reading is a many-time activity.**
>
> *"Typing is only one time. But readability — several people have to analyse my code. That's why
> highest priority for readability, not for typing."*

> [!info] **The joke he builds on it.** Explicit import is *"best suitable for Hitech City, where
> readability is important."* Implicit import is *"best suitable for Ameerpet, where typing is
> important — because I'm not going to deliver this to any person."* (Hitech City is Hyderabad's
> corporate district; Ameerpet is its training-institute district.)

> [!info] **A practical confirmation.** *"Usually we won't write import statements — the IDE generates
> them."* And **no IDE in the universe generates implicit import statements.** Eclipse, IntelliJ and
> the rest all expand to explicit imports, which is the industry voting the same way.

---

# Case 2 — which import statements are meaningful

An exam-shaped question. Four candidates:

```java
import java.util.ArrayList;      // 1
import java.util.ArrayList.*;    // 2
import java.util.*;              // 3
import java.util;                // 4
```

Measured on JDK 25:

| | Statement | Result |
|---|---|---|
| 1 | `import java.util.ArrayList;` | ✅ compiles |
| 2 | `import java.util.ArrayList.*;` | ✅ compiles |
| 3 | `import java.util.*;` | ✅ compiles |
| 4 | `import java.util;` | ❌ `cannot find symbol` |

**Only option 4 is an error.** After a package name the `.*` is compulsory — a semicolon straight
after the package name names nothing the compiler can resolve.

> [!important] **Option 2 is the one people get wrong.** `import SomeClass.*;` is **valid syntax** — a
> type-import-on-demand that imports the class's **member (nested) types**. The right question to ask
> is *"is there any type declared inside `ArrayList`?"* — and the answer for `ArrayList` is no, so the
> statement is **useless but perfectly legal**. It imports nothing and compiles fine.

> [!example]- **Deep dive — the same statement doing real work, on a class that does have nested
> types.** `Map` is the proof that `.*` after a class name is meaningful syntax.
>
> Measured on JDK 25:
> ```java
> import java.util.Map.*;
> import java.util.*;
>
> Map<String,String> m = new HashMap<>();
> m.put("a", "b");
> for (Entry<String,String> e : m.entrySet())      // Entry, unqualified
>     System.out.println(e.getKey() + " = " + e.getValue());
> ```
> ```
> a = b
> ```
> `Entry` is usable without writing `Map.Entry` — precisely because `import java.util.Map.*;` imported
> the member types.

---

# Case 3 — fully qualified names and imports are alternatives

```java
class MyObject extends java.rmi.server.UnicastRemoteObject { }
```

**No import statement anywhere. Does it compile?** Yes.

> **Whenever we are using a fully qualified name, it is not required to write an import statement.**
> **Whenever we are writing an import statement, it is not required to use the fully qualified name.**

They are two ways to say the same thing, and you need exactly one of them.

> *"Why did the import statement come? Because we don't want to use the fully qualified name."*

---

# Case 4 — ambiguity

The dangerous one.

```java
import java.util.*;
import java.sql.*;

class Amb {
    public static void main(String[] args) {
        Date d = new Date();
    }
}
```

**`Date` exists in `java.util` and in `java.sql`.** Measured on JDK 25:

```
error: reference to Date is ambiguous
  both class java.sql.Date in java.sql and class java.util.Date in java.util match
```

> [!question]- **Deep dive — his story about the compiler, told over three visits to three rooms.** It
> is long and it is the reason the rule sticks, so here it is.
>
> **Visit one.** *"Compiler, can you please compile my code?"* — *"Compiled."* Then I asked: which
> `Date` did you consider? *"The `util` package `Date`."* So I called the compiler to room number 22
> and gave it left and right: **who told you to consider `util`? My requirement was the SQL `Date`.
> Don't take the decision on your own. If you repeat this mistake I will kill you.** The compiler left
> the room crying.
>
> **Visit two.** A few days later — *"Compiler, compile my code."* Half a minute later: *"Compiled."*
> Which `Date`? *"SQL."* Room number 302, left and right again: **who told you to consider SQL?** —
> *"Sir, you only told me last time."* — **That was my last-time requirement. Now my requirement is
> `util`.** The compiler left crying again.
>
> **Visit three.** *"Compiler, compile my code."* This time the compiler says: *"You come to room
> number 42."* And when I get there:
>
> > *"If I give the chance to `util`, your requirement is SQL. If I give the chance to SQL, your
> > requirement is `util`. **I don't want to take any risk for stupid programmers like you.** First let
> > me know which `Date` you want — then only I can compile."*
>
> That is the compile-time error. The compiler is not failing to decide; it is **refusing** to, because
> either choice can be silently wrong.

## The other case with the same problem

> **`List` is available in `java.util` and in `java.awt`.**

Measured on JDK 25:

```
error: reference to List is ambiguous
  both class java.awt.List in java.awt and interface java.util.List in java.util match
```

He asks the class whether any case besides `Date` exists, and this is it. `java.awt.List` is the GUI
list component, alongside `Frame` and `Panel`.

**The fix in both cases** is to be explicit about the one you want — an explicit class import, or a
fully qualified name at the point of use.

---

# Case 5 — the resolution order

If a name could come from several places, the compiler has a fixed order of preference.

> **While resolving class names, the compiler always gives precedence in the following order:**
> **1. explicit class import**
> **2. classes present in the current working directory** (the **default package**)
> **3. implicit class import**

```java
import java.util.Date;   // explicit
import java.sql.*;       // implicit

Date d = new Date();
System.out.println(d.getClass().getName());
```

Measured on JDK 25:

```
java.util.Date
```

**No ambiguity error this time** — the explicit import wins outright, which is exactly why the fix in
case 4 works.

And if the explicit import is removed, the current working directory is consulted **before** the
implicit import. Only when neither of the first two matches does `java.sql.*` get its chance.

---

# Case 6 — importing a package does not import its sub-packages

> **Whenever we import a Java package, all classes and interfaces present in that package are available
> by default — but NOT the sub-package classes.**
>
> **To use a sub-package class, we must write the import statement down to the sub-package level.**

`Pattern` lives in `java.util.regex`. Which import gets it?

```java
import java.*;             // 1
import java.util.*;        // 2
import java.util.regex.*;  // 3
// 4 — no import required
```

**Answer: 3.** Measured on JDK 25, `import java.util.*;` gives `cannot find symbol` for `Pattern`,
while `import java.util.regex.*;` compiles and runs.

> [!important] **The argument that proves the rule, and it is his.** *If* importing a package included
> its sub-packages, then **`import java.*;` alone would be enough for everything** — `util` is a
> sub-package of `java`, `sql` is a sub-package of `java`, `io` is a sub-package of `java`.
>
> *"Then only one import statement is required. Why are you writing `import java.util.*`, `import
> java.sql.*`?"* The fact that everybody writes those imports every day is itself the proof.

> [!info] **The second proof, which is sharper.** `java.lang` needs no import at all. But
> **`java.lang.reflect.Method` does.** If sub-packages came along for free, `Method` would be available
> automatically like `String` is — and it is not.

---

# Case 7 — the two packages you never import

> **All classes and interfaces present in the following two packages are available by default to every
> Java program, so we are not required to import them:**
> **1. `java.lang`**
> **2. the default package** — that is, the **current working directory**

The first is familiar: `String s = new String("Durga");` needs no import because `String` is in
`java.lang`.

The second is the one people forget. If `Student.java` sits in the same directory:

```java
Student s1 = new Student("Durga", 101);
System.out.println(s1.name + "..." + s1.rollNumber);
```

This compiles and runs with **no import**, because `Student` is in the current working directory —
the **default package** — and that is available automatically.

---

# Case 8 — import is purely a compile-time concept

Two versions of one program, identical apart from this:

| Program A | Program B |
|---|---|
| fully qualified names everywhere | short names + import statements |

**Which takes longer to compile?** **B.** With a fully qualified name the compiler has complete
information on the spot. With a short name it must go and check the import statements to work out what
you meant. More imports, more work, more compile time.

**Which takes longer to run?** — and here he sets a trap, because the intuitive answer is B again.

> [!important] **Neither. Both take exactly the same time to run.**
>
> **Import statements are a totally compile-time concept.** More imports means more compile time, and
> **no effect whatsoever on execution time.**
>
> His reasoning for why it *must* be this way: *"We can compromise with anything, but not performance.
> If it really affected the performance of the system, this concept should be removed."* A feature that
> is purely for the programmer's convenience cannot be allowed to cost anything at runtime — so it does
> not.

---

# Case 9 — `#include` in C vs `import` in Java

A likely fresher interview question, and the answer people usually give is wrong.

> *"Most people — even faculty members, even books — say Java's import statement is nothing but C's
> `#include`. But functionality-wise there is a big difference."*

| | C — `#include <stdio.h>` | Java — `import java.io.*;` |
|---|---|---|
| When | at **translation time**, the beginning | at **runtime**, on use |
| What | **all** the header's contents are loaded | **no** `.class` file is loaded at the beginning |
| On use | already there | **that** class's `.class` file is loaded then |
| Name | **static include** | **dynamic include**, **load on demand** / **load on the fly** |

> **In C, `#include` loads everything at the beginning whether you use it or not. In Java, no `.class`
> file is loaded at the beginning; whenever we use a particular class, only then is the corresponding
> `.class` file loaded.**

**Which is better?** The Java approach.

> *"Which input-output file you are going to use, we don't know. Loading all of them at the beginning
> is not at all a good programming practice. Loading all 5,000 Java classes at the beginning is
> unnecessary memory waste — performance is going to be down."*

---

# Static import

## The Java 1.5 context

Before explaining it, he places it among its siblings — everything that arrived in **Java 1.5**:

| |
|---|
| for-each loop |
| var-arg methods |
| autoboxing / auto-unboxing |
| generics |
| covariant return types |
| `Queue` (collections) |
| annotations |
| enum |
| **static import** |

> [!question]- **Deep dive — the movie analogy, and why he calls static import the flop of 1.5.** Kept
> because it is how he frames the whole feature, and because the verdict is still the industry's.
>
> Before any film is released, the producer and director hold an audio function and promise it will
> *"break Tollywood records, Bollywood records, world records."* Then one fine day the movie releases —
> **and the audience decides whether it is a hit or a flop.** He remembers one such function for a film
> called *Orange*, where a speaker promised it would be huge. *"How much hit was that movie? You can
> decide — it is nothing but a flop movie."*
>
> **The same publicity happened for Java 1.5.** *"Some people conducted a press meet saying: after
> releasing 1.5, all the remaining languages are going to be packed, because we are redefining total
> Java once again."* Then the release came, and worldwide programmers — the audience — judged the
> features. Most were genuinely excellent, *"each and every feature's target is to simplify the
> programmer's life."*
>
> **But not every new concept is a hit.** *"There is one concept which is a flop concept in the 1.5
> version — static import."* And by 1.6 the message had changed: *"if there is no specific requirement,
> it is not recommended to use static import."*

> **According to Sun, static import reduces the length of the code and improves readability.**
> **According to worldwide programming experts, static import creates confusion and reduces
> readability. Hence, if there is no specific requirement, it is not recommended.**

## What it actually does

**Without static import** — static members are accessed through the class name, as always:

```java
System.out.println(Math.sqrt(4));
System.out.println(Math.max(10, 20));
System.out.println(Math.random());
```

Write `Math.sqrt` twenty times and you type `Math` twenty times. *"Why don't you remove that class name
from the static method?"*

**Drop the class name and it breaks.** Measured on JDK 25:

```
error: cannot find symbol   symbol: method sqrt(int)
error: cannot find symbol   symbol: method max(int,int)
error: cannot find symbol   symbol: method random()
3 errors
```

**Now add a static import for one of them:**

```java
import static java.lang.Math.sqrt;
```

Measured on JDK 25 — **2 errors.** `sqrt` is fixed; `max` and `random` are not. The count dropping from
3 to 2 is the demonstration.

**And for all of them:**

```java
import static java.lang.Math.*;

class SI2 {
    public static void main(String[] args) {
        System.out.println(sqrt(4));
        System.out.println(max(10, 20));
        System.out.println(random());
    }
}
```

Measured on JDK 25, run twice:

```
2.0
20
0.3957307810140398
```
```
2.0
20
0.6260858894147701
```

`sqrt(4)` prints `2.0` rather than `2` because `Math.sqrt` returns `double`, and `random()` changes on
every run.

> **Usually we access static members using the class name. Whenever we write a static import, we can
> access static members directly, without the class name.**

> [!important] **The spelling trap.** The concept is called **static import**, but what you write is
> **`import static`** — in that order. *"While writing we have to write `import static`, but while
> pronouncing, `static import` is the popular one."* Note also: import the **name only** — `sqrt`, not
> `sqrt()`.

---

# What this part established

| | |
|---|---|
| Two types of import | **explicit** (`java.util.ArrayList`) and **implicit** (`java.util.*`) |
| Recommended | **explicit** — it improves readability |
| Why, despite more typing | typing is **one-time**; reading is **many-time** |
| IDEs | generate explicit imports, never implicit |
| `import java.util;` | ❌ the only genuinely invalid form of the four |
| `import SomeClass.*;` | ✅ **legal** — imports the class's nested types (correction to his case 2) |
| Fully qualified name and import | **alternatives** — you need exactly one |
| `Date` | in **both** `java.util` and `java.sql` → `reference to Date is ambiguous` |
| `List` | in **both** `java.util` and `java.awt` → same problem |
| Resolution order | **explicit import → current working directory → implicit import** |
| Importing a package | does **not** import its **sub-packages** |
| Proof | otherwise `import java.*;` alone would suffice; and `java.lang.reflect.Method` needs an import |
| Never need importing | **`java.lang`** and the **default package** (current working directory) |
| Import statements are | **purely compile-time** — more imports, more compile time, **zero** runtime effect |
| C `#include` | **static include** — everything, at translation time |
| Java `import` | **dynamic include / load on demand** — nothing until the class is used |
| Static import syntax | **`import static java.lang.Math.sqrt;`** — written `import static`, called static import |
| Its effect | access static members **without the class name** |
| Its verdict | Sun: shorter and more readable. Experts: **confusing** — not recommended |
