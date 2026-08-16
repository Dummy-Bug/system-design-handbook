## Fully qualified names

> [!question]- **Deep dive — his analogy for what a fully qualified name is: the SCJP training address.**
> The story he uses to build the idea from nothing, and it is the reason the term sticks.
>
> Somebody posts on a forum: *"Where is SCJP training available?"*
>
> - *"It is available in Durgasoft."* → **"Where is Durgasoft?"**
> - *"It is at SR Nagar."* → **"Where is SR Nagar?"**
> - *"In Hyderabad."* → **"Which Hyderabad — India or Pakistan?"**
>
> Every answer raises another question, because each one is only meaningful relative to something the asker does not know. So answer it completely, from the top:
>
> > **World → Asia → India → Telangana → Hyderabad → SR Nagar → Durgasoft**
>
> Now there is nothing left to ask. *"Thanks man — not possible to attend, because I'm from Afghanistan."*
>
> **That complete path is a fully qualified name.** `java.util.ArrayList` is the same thing: package,sub-package, class, leaving nothing for the compiler to ask about.

```java
java.util.ArrayList l = new java.util.ArrayList();
```

Measured on JDK 25 — **compiles and runs**, with no import at all.

> *"Compiler, do you know the `java` package? In that, the `util` sub-package. In that, `ArrayList`.
> That `ArrayList` I'm using."*

## Why fully qualified names are not the answer

> **The problem with using a fully qualified name every time: it increases the length of the code and reduces readability.**

Use `java.util.ArrayList` a hundred times and you type it a hundred times.

## The import statement

```java
import java.util.ArrayList;

class Imp {
    public static void main(String[] args) {
        ArrayList l = new ArrayList();
        l.add("works with the short name");
        System.out.println(l);
    }
}
```

Measured on JDK 25:

```
[works with the short name]
```

> **Whenever we write an import statement, it is not required to use the fully qualified name every time — we can use the short name directly.**

> [!important] **The one-line summary he lands on:**
> > **The import statement acts as a typing shortcut.**
>
> That is all it does. It generates no code, loads no class, costs nothing at runtime. It is the agreement that `ArrayList` means `java.util.ArrayList` in this file 


--- 
# Case 1 — the two types of import statement

> **There are two types of import statements:**
> **1. explicit class import** — `import java.util.ArrayList;`
> **2. implicit class import** — `import java.util.*;`

## Which one to use


> **It is highly recommended to use explicit class import, because it improves readability of the code.** Even for a hundred classes from the same package.

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

You are doing code-work — reading it so you can extend it tomorrow — and you need to see how`getInfo()` is implemented. **Which package is `Account` in?**

> *"I opened `com.hdfc` — almost 15 minutes I spent, and I didn't see `Account` anywhere. Then I
> opened `com.icicibank`, and there I could see the `Account` class."*

Then a few lines later, `Loan l = new Loan();` — and the search starts over, in the other order.

Now write the imports explicitly:

```java
import com.hdfc.Account;
import com.icicibank.Loan;
```

**The question answers itself from the top of the file.** `Loan` is in `icicibank`, `Account` is in `hdfc`. You never open a package to find out.

> [!important] **His answer to "but explicit means more typing."**
> **Typing is a one-time activity. Reading is a many-time activity.**
>
> *"Typing is only one time. But readability — several people have to analyse my code. That's why
> highest priority for readability, not for typing."*

> [!info] **A practical confirmation.** *"Usually we won't write import statements — the IDE generates
> them."* And **no IDE in the universe generates implicit import statements.** Eclipse, IntelliJ and the rest all expand to explicit imports, which is the industry voting the same way.

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

**Only option 4 is an error.** After a package name the `.*` is compulsory — a semicolon straight after the package name names nothing the compiler can resolve.

> [!important] **Option 2 is the one people get wrong.** `import SomeClass.*;` is **valid syntax** — a
> type-import-on-demand that imports the class's **member (nested) types**. The right question to ask is *"is there any type declared inside `ArrayList`?"* — and the answer for `ArrayList` is no, so the
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
> `Entry` is usable without writing `Map.Entry` — precisely because `import java.util.Map.*;` imported the member types.

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

## The other case with the same problem

> **`List` is available in `java.util` and in `java.awt`.**

Measured on JDK 25:

```
error: reference to List is ambiguous
  both class java.awt.List in java.awt and interface java.util.List in java.util match
```


**The fix in both cases** is to be explicit about the one you want — an explicit class import, or a fully qualified name at the point of use.

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

**No ambiguity error this time** — the explicit import wins outright, which is exactly why the fix in case 4 works.

And if the explicit import is removed, the current working directory is consulted **before** the implicit import. Only when neither of the first two matches does `java.sql.*` get its chance.

---

# Case 6 — importing a package does not import its sub-packages

> **Whenever we import a Java package, all classes and interfaces present in that package are available by default — but NOT the sub-package classes.**

> **To use a sub-package class, we must write the import statement down to the sub-package level.**

`Pattern` lives in `java.util.regex`. Which import gets it?

```java
import java.*;             // 1
import java.util.*;        // 2
import java.util.regex.*;  // 3
// 4 — no import required
```

**Answer: 3.** Measured on JDK 25, `import java.util.*;` gives `cannot find symbol` for `Pattern`,while `import java.util.regex.*;` compiles and runs.

> [!important] **The argument that proves the rule, and it is his.** *If* importing a package included
> its sub-packages, then **`import java.*;` alone would be enough for everything** — `util` is a sub-package of `java`, `sql` is a sub-package of `java`, `io` is a sub-package of `java`.
>
> *"Then only one import statement is required. Why are you writing `import java.util.*`, `import
> java.sql.*`?"* The fact that everybody writes those imports every day is itself the proof.

> [!info] **The second proof, which is sharper.** `java.lang` needs no import at all. But
> **`java.lang.reflect.Method` does.** If sub-packages came along for free, `Method` would be available automatically like `String` is — and it is not.

---

# Case 7 — the two packages you never import

> **All classes and interfaces present in the following two packages are available by default to every  Java program, so we are not required to import them:**
> **1. `java.lang`**
> **2. the default package** — that is, the **current working directory**

The first is familiar: `String s = new String("Durga");` needs no import because `String` is in `java.lang`.

The second is the one people forget. If `Student.java` sits in the same directory:

```java
Student s1 = new Student("Durga", 101);
System.out.println(s1.name + "..." + s1.rollNumber);
```

This compiles and runs with **no import**, because `Student` is in the current working directory — the **default package** — and that is available automatically.

---

# Case 8 — import is purely a compile-time concept

Two versions of one program, identical apart from this:

| Program A | Program B |
|---|---|
| fully qualified names everywhere | short names + import statements |

**Which takes longer to compile?** **B.** With a fully qualified name the compiler has complete information on the spot. With a short name it must go and check the import statements to work out what you meant. More imports, more work, more compile time.

**Which takes longer to run?** — and here he sets a trap, because the intuitive answer is B again.

> [!important] **Neither. Both take exactly the same time to run.**
>
> **Import statements are a totally compile-time concept.** More imports means more compile time, and **no effect whatsoever on execution time.**
>
> *We can compromise with anything, but not performance. If it really affected the performance of the system, this concept should be removed.*
> 
> A feature that is purely for the programmer's convenience cannot be allowed to cost anything at runtime — so it does not.

---

# Case 9 — `#include` in C vs `import` in Java

> **In C, `#include` loads everything at the beginning whether you use it or not. In Java, no `.class` file is loaded at the beginning;
>  whenever we use a particular class, only then is the corresponding `.class` file loaded.**

**Which is better?** The Java approach.

> Which input-output file you are going to use, we don't know. Loading all of them at the beginning is not at all a good programming practice. 
> Loading all 5,000 Java classes at the beginning is unnecessary memory waste — performance is going to be down

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
