Interview questions on **Java enums**, as asked by mid-tier product companies for a backend role at 3–5 years.

> [!important] **What this tier is testing.** They have real APIs, persistence, serialization, and code reviews. The bar moves from *can you use an enum?* to **can you choose the right external representation, collection, and behavior model without creating an upgrade problem?**

> [!info] **How the ordering was decided, honestly.** There is no public dataset of interview question frequency. This ordering is my judgement from the interview-prep sources surveyed in August 2026, cross-checked with the Java SE APIs and the Java Language Specification. Treat the **bands** as reliable and the **order inside a band** as approximate.

**Coverage markers:** ✅ covered · ⚠️ partial · ❌ gap in our notes.

# Band A — the core set, expect most of these

### 1. When should an enum expose a stable `code` field instead of using `name()`?

- **Tests:** API design and separation between Java names and domain values.
- **Notes:** ❌ gap.

### 2. How would you implement `fromCode(String code)`?

- **Tests:** lookup design, invalid input, duplicate-code handling, and initialization cost.
- **Notes:** ❌ gap.

### 3. How would you handle an unknown enum value received from an API?

- **Tests:** forward compatibility between independently deployed services.
- **Notes:** ❌ gap.
- **Recency:** this is increasingly common in JSON and event-driven service interviews.

### 4. How would you persist an enum safely in a relational database?

- **Tests:** whether you know the compatibility risks of ordinal and name-based storage.
- **Notes:** ❌ gap.

### 5. How would you serialize an enum in JSON without coupling the API to the Java constant name?

- **Tests:** public contract design and versioning.
- **Notes:** ❌ gap.

### 6. What is the difference between `EnumSet` and `HashSet`?

- **Tests:** choosing a collection based on the key/value domain.
- **Notes:** ❌ gap — `EnumSet` is not covered in the ENUM notes.

### 7. What is the difference between `EnumMap` and `HashMap`?

- **Tests:** enum-specific collection choices.
- **Notes:** ❌ gap.

### 8. When would you use `EnumSet` for permissions or feature flags?

- **Tests:** practical modelling of a subset of a finite universe.
- **Notes:** ❌ gap.

### 9. How would you use an enum as a strategy instead of a large `switch`?

- **Tests:** putting behavior next to the values that own it.
- **Notes:** ⚠️ `06`, `09` show enum methods and constant-specific bodies; strategy design is not covered.

### 10. When is a constant-specific class body preferable to a `switch`?

- **Tests:** maintainability and behavior ownership.
- **Notes:** ✅ `09` for the language mechanism; ❌ production trade-offs are a gap.

# Band B — very likely once the conversation goes deeper

### 11. Why is an enum singleton protected against ordinary duplicate instantiation?

- **Tests:** enum identity, construction restrictions, and singleton reasoning.
- **Notes:** ⚠️ `04`, `07` cover the building blocks; singleton trade-offs are a gap.

### 12. How does enum serialization affect singleton identity?

- **Tests:** whether you know serialization has special enum behavior.
- **Notes:** ❌ gap.

### 13. Can reflection create another enum instance?

- **Tests:** runtime guarantees beyond the source-level constructor restriction.
- **Notes:** ❌ gap.

### 14. Can an enum constant be cloned?

- **Tests:** the identity guarantees inherited from `java.lang.Enum`.
- **Notes:** ⚠️ `04` lists `clone()`; the runtime guarantee is not developed.

### 15. What is the difference between `name()` and `toString()`?

- **Tests:** stable identity versus display representation.
- **Notes:** ✅ `02`, `08`.

### 16. What is the difference between `getClass()` and `getDeclaringClass()` for a constant with a class body?

- **Tests:** generated subclasses and reflection details.
- **Notes:** ⚠️ `09` covers the generated subclass; the API distinction is a gap.

### 17. What class files can be generated for an enum with constant-specific bodies?

- **Tests:** source syntax versus compiled class structure.
- **Notes:** ✅ `09`.

### 18. Can an enum contain an abstract method?

- **Tests:** the rule requiring concrete implementations from all constants.
- **Notes:** ⚠️ `07`, `09`.

### 19. What happens if an enum constructor accesses static state of the same enum?

- **Tests:** initialization order and circularity.
- **Notes:** ❌ gap.

### 20. What happens if an enum constructor throws an exception?

- **Tests:** class initialization failure and application startup behavior.
- **Notes:** ❌ gap.

### 21. Are nested enums implicitly static?

- **Tests:** member-type semantics.
- **Notes:** ⚠️ `02` covers modifier rules; the modern language rule is not developed.

### 22. What happens if an enum constant is added after a client has been compiled?

- **Tests:** binary compatibility and exhaustive branching.
- **Notes:** ❌ gap.

### 23. What happens if enum constants are reordered after persisted data already exists?

- **Tests:** ordinal fragility and data migration awareness.
- **Notes:** ⚠️ `05` covers ordinal; persistence consequences are a gap.

### 24. How would you test every enum constant without forgetting newly added constants?

- **Tests:** test completeness and maintenance discipline.
- **Notes:** ❌ gap.

# Band C — depth probes, asked when the interviewer is enjoying themselves

### 25. What is the internal representation of `EnumSet`?

- **Tests:** implementation reasoning and finite-domain optimization.
- **Notes:** ❌ gap.

### 26. Why can `EnumSet` be faster and more compact than `HashSet` for enum values?

- **Tests:** connecting the enum universe to collection representation.
- **Notes:** ❌ gap.

### 27. How does `EnumMap` use the enum key space?

- **Tests:** specialized map design.
- **Notes:** ❌ gap.

### 28. Why is `java.lang.Enum` declared with `E extends Enum<E>`?

- **Tests:** self-referential generic bounds.
- **Notes:** ✅ `04` shows the signature; the generic design question is a gap.

### 29. What is the difference between `Enum.valueOf(Class<T>, String)` and the generated `MyEnum.valueOf(String)`?

- **Tests:** inherited generic API versus compiler-generated enum API.
- **Notes:** ✅ `05` for the two sources; the API comparison is partial.

### 30. When is a sealed interface a better model than an enum?

- **Tests:** choosing between a closed set of instances and a closed set of subtypes.
- **Notes:** ❌ gap.

### Gaps this file exposes

| # | Missing | Why it matters here |
|---|---|---|
| 1 | Persistence and JSON compatibility | product services cannot treat enum names as free internal details |
| 2 | `EnumSet` and `EnumMap` | specialized collections are common interview follow-ups |
| 3 | Serialization and reflection guarantees | important for enum singleton and runtime questions |
| 4 | Initialization order | enum constructors can run during class initialization |
| 5 | Strategy and sealed-type design | this is where enum knowledge becomes design judgement |

The JVM-level enum notes are strong on declaration, inheritance, constructors, generated methods, switch, imports, and constant-specific bodies. This tier adds the application and library design surrounding those mechanics.

## Interview-question sources

- [Java67: Top 15 Java Enum Interview Questions for 3 to 5 Years Experienced](https://www.java67.com/2013/07/15-java-enum-interview-questions-amswers-for-experienced-programmers.html)
- [JavaInUse: Top Java Enum Frequently Asked Interview Questions](https://www.javainuse.com/misc/enum-interview-questions)
- [Baeldung: Java Collections Interview Questions](https://www.baeldung.com/java-collections-interview-questions)

## Technical fact-checking only

- [Java Language Specification: Enum Classes](https://docs.oracle.com/javase/specs/jls/se26/html/jls-8.html)
- [EnumSet API documentation](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/util/EnumSet.html)
- [Java Language Specification: Binary Compatibility](https://docs.oracle.com/en/java/javase/26/docs/specs/jls/jls-13.html)
