Interview questions on **Java enums**, as asked by small startups and early-stage product teams for a backend role at 3–5 years.

> [!important] **What a startup is actually testing with these.** Not obscure enum trivia. They want to know whether you can model a small, closed set of domain values without falling back to fragile integers, strings, or scattered conditionals. A plain explanation plus one example from your own code is stronger than reciting the enum specification.

> [!info] **How the ordering was decided, honestly.** There is no public dataset of interview question frequency. This ordering is my judgement from the interview-prep sources surveyed in August 2026, weighted toward recent Java material. Treat the **bands** as reliable and the **order inside a band** as approximate.

**Coverage markers** point at our own notes, so a gap here is a gap in the wiki:

| Marker | Meaning |
|---|---|
| ✅ | covered in the note listed |
| ⚠️ | partly covered — the question would expose a thin spot |
| ❌ | **gap** — nothing in the notes answers this yet |

# Band A — expect these in almost every screen

### 1. What is an enum, and when would you use one?

- **Tests:** whether you understand the domain purpose rather than just the syntax.
- **Notes:** ✅ `01` — defining a small, fixed set of named values.
- **Chained follow-up:** *"When would a database table or configuration value be better than an enum?"*

### 2. How is a Java enum different from integer or string constants?

- **Tests:** type safety and domain modelling.
- **Notes:** ✅ `01` — Java enums define their own type and their constants are objects.

### 3. Are enum constants objects? What is their declared type?

- **Tests:** whether you understand what the compiler creates for the constant list.
- **Notes:** ✅ `01`, `02` — enum constants are instances of the enum type.

### 4. What is the relationship between an enum and `java.lang.Enum`?

- **Tests:** the enum inheritance model.
- **Notes:** ✅ `04` — every enum is a direct child of `java.lang.Enum`.
- **Chained follow-up:** *"Can you write an explicit `extends java.lang.Enum` clause?"*

### 5. Can an enum extend another class or enum?

- **Tests:** whether you know why the class inheritance slot is unavailable.
- **Notes:** ✅ `04`.

### 6. Can an enum implement one or more interfaces?

- **Tests:** the difference between class inheritance and interface implementation for enums.
- **Notes:** ✅ `04`.

### 7. Can you instantiate an enum with `new`?

- **Tests:** whether you understand how enum constants are created.
- **Notes:** ✅ `07`.

### 8. Can an enum contain fields, methods, and constructors?

- **Tests:** whether you know Java enums are richer than C-style enumerations.
- **Notes:** ✅ `06`, `07`.

# Band B — common once the role touches real code

### 9. When does an enum constructor run, and how many times does it run?

- **Tests:** class initialization and per-constant object creation.
- **Notes:** ✅ `07`.
- **Chained follow-up:** *"What happens if the enum class is never initialized?"*

### 10. How do you give each enum constant different data?

- **Tests:** practical enum design with constructor parameters and fields.
- **Notes:** ✅ `07`.

### 11. What are `values()` and `valueOf(String)`?

- **Tests:** the generated API every enum exposes.
- **Notes:** ✅ `05`.

### 12. Where does the `values()` method come from?

- **Tests:** compiler-generated members versus inherited API methods.
- **Notes:** ✅ `05`.

### 13. What does `ordinal()` return, and why should it not be used as a business identifier?

- **Tests:** declaration order versus domain identity.
- **Notes:** ✅ `05` for the method; ⚠️ stable business identifiers are not covered.

### 14. Can an enum be used in a `switch` statement?

- **Tests:** common control-flow usage and case-label rules.
- **Notes:** ✅ `03`.
- **Recency:** qualified enum case labels are supported in current Java versions; older notes in this chapter distinguish the pre-Java-21 rule.

### 15. Can enum constants be compared with `==`, `equals()`, or `>`?

- **Tests:** object identity versus numeric comparison.
- **Notes:** ✅ `08`.

### 16. What is the difference between `enum`, `Enum`, and `Enumeration`?

- **Tests:** vocabulary that is easy to confuse in a quick screen.
- **Notes:** ✅ `09`.

# Band C — occasional, usually as a depth probe

### 17. What is a constant-specific class body?

- **Tests:** whether you recognise per-constant behavior as generated subclasses.
- **Notes:** ✅ `09`.

### 18. Can an enum contain an abstract method?

- **Tests:** whether you know the rule for constant-specific implementations.
- **Notes:** ⚠️ `07` records the lecture rule and the modern correction; the exact language rule is not developed independently.

### 19. Can an enum be declared inside a class or inside a method?

- **Tests:** declaration context and version awareness.
- **Notes:** ⚠️ `02` covers the older rule and notes the Java 16 change allowing local enums.

### 20. Can an enum be empty or contain a `main` method?

- **Tests:** declaration and body grammar.
- **Notes:** ✅ `06`.

### 21. How would you safely parse an enum from user input?

- **Tests:** validation and boundary handling rather than calling a library method blindly.
- **Notes:** ❌ gap — parsing policy is not covered.

### 22. How would you expose a stable code or label for an enum in an API?

- **Tests:** whether you separate Java constant names from external contracts.
- **Notes:** ❌ gap — external representations are not covered.

# Gaps this file exposes

| # | Missing from the notes | Why it matters here |
|---|---|---|
| 1 | Stable enum codes for JSON, database, and messaging | `ordinal()` and `name()` are often unsafe external contracts |
| 2 | Safe parsing and unknown-value handling | boundary input is where enum failures become user-facing |
| 3 | `EnumSet` and `EnumMap` | common production collections designed specifically for enums |
| 4 | Enum singleton trade-offs | a frequent follow-up once enum identity is discussed |

The existing notes answer the language-level questions unusually well: declaration, inheritance, constructors, generated methods, switch, imports, and constant-specific bodies. The gaps begin at the application boundary.

## Interview-question sources

- [Java67: Top 15 Java Enum Interview Questions for 3 to 5 Years Experienced](https://www.java67.com/2013/07/15-java-enum-interview-questions-amswers-for-experienced-programmers.html)
- [JavaInUse: Top Java Enum Frequently Asked Interview Questions](https://www.javainuse.com/misc/enum-interview-questions)

## Technical fact-checking only

- [Java Language Specification: Enum Classes](https://docs.oracle.com/javase/specs/jls/se26/html/jls-8.html)
- [Oracle: Switch Expressions and Statements](https://docs.oracle.com/en/java/javase/26/language/switch-expressions-statements.html)
