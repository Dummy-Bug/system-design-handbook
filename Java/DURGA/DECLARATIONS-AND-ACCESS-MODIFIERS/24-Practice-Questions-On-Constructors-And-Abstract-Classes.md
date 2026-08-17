# The summary quiz

The final session of the chapter is a single exam-style question — which of the following are valid? — covering everything in notes `15` to `20`. Every answer below is his.

Each one is worth reading as a claim you might be handed in an interview and asked to accept or reject.

---

## Questions 1–5 — `new` vs constructor

> [!question]- **1. The purpose of a constructor is to create an object.**
> **❌ INVALID.** The purpose of a constructor is to **initialize** an object. Creating it is the job of the **`new`** operator. (note `15`)

> [!question]- **2. The purpose of a constructor is to initialize an object, but not to create an object.** **✅ VALID.** This is the correct statement of the same fact.

> [!question]- **3. Once the constructor completes, then only object creation completes.** **❌ INVALID.** The **`new` operator** creates the object. Once `new` completes the object is **already there**; the constructor then runs to initialise it. Creation does not wait for the constructor.

> [!question]- **4. First the object will be created, and then the constructor will be executed.** **✅ VALID.** The order from note `15` — a baby has to be born; after the baby is born we will think about the naming ceremony.

> [!question]- **5. The purpose of the `new` keyword is to create an object, and the purpose of a constructor is to initialize that object.** **✅ VALID.** The full, correct statement of the distinction.

---

## Questions 6–7 — objects for an abstract class

> [!question]- **6. We can't create an object for an abstract class directly, but indirectly we can.** **❌ INVALID.** **Neither directly nor indirectly.** (note `18`)

> [!question]- **7. Either directly or indirectly we can't create an object for an abstract class, and hence the constructor concept is not applicable for an abstract class.** **❌ INVALID.** The first half is right and the second half does not follow. **An abstract class CAN contain a constructor** — to perform initialization for the instance variables required by the child class object. (notes `18`, `19`)
>
> This is the trap question of the set: a true premise with a false conclusion bolted on.

---

## Questions 8–10 — parent objects and parent constructors

> [!question]- **8. Whenever we are creating a child class object, automatically a parent class object will be created internally.** **❌ INVALID.** The parent **constructor** is executed; a parent **object** is not created. Proved by hash code in note `17`.

> [!question]- **9. Whenever we are creating a child class object, automatically the abstract class constructor will be executed.** **✅ VALID.** And that is its whole purpose — the abstract class constructor exists **for child object initialization only**. (notes `16`, `18`)

> [!question]- **10. Whenever we are creating a child class object, automatically the parent constructor will be executed, but a parent object won't be created.** **✅ VALID.** The complete and correct statement, and the one to give in an interview.

---

## Question 11 — interfaces

> [!question]- **11. An interface can contain a constructor.**
> **❌ INVALID.** The constructor concept is **not applicable** to interfaces — every interface variable is `public static final`, so no instance variables exist, so there is nothing to initialise. (note `19`)

---

# The answers at a glance

| # | Claim | |
|---|---|---|
| 1 | a constructor creates an object | ❌ |
| 2 | a constructor initialises but does not create | ✅ |
| 3 | object creation completes when the constructor completes | ❌ |
| 4 | the object is created first, then the constructor runs | ✅ |
| 5 | `new` creates, the constructor initialises | ✅ |
| 6 | an abstract class object can be created indirectly | ❌ |
| 7 | …hence an abstract class cannot have a constructor | ❌ |
| 8 | creating a child object creates a parent object | ❌ |
| 9 | creating a child object runs the abstract class constructor | ✅ |
| 10 | the parent constructor runs but no parent object is created | ✅ |
| 11 | an interface can contain a constructor | ❌ |

**Four valid, seven invalid.**

> [!important] **Every wrong answer traces back to one misunderstanding:** believing that a constructor **creates** an object. Fix that single idea and questions 1, 3, 6, 7 and 8 all answer themselves — which is exactly why he spent an hour and a half on `new` before touching anything else.

---

# What this chapter established

The loopholes series, as one argument:

| | |
|---|---|
| `15` | **`new` creates; the constructor initialises** — and `new` runs first |
| `16` | in inheritance, the parent constructor initialises the **inherited** variables |
| `17` | only **one object** exists — proved by identical hash codes |
| `18` | an abstract class needs a constructor for **code reusability** across its children |
| `19` | an interface needs none — **no instance variables exist** to initialise |
| `20` | an abstract class **can** replace an interface, but **should not** |
| `21` | eleven claims, and the four that are true |
