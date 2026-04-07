## Phase 1 — Java Language Foundations

> Interview relevance: These are the "gotcha" questions interviewers use to separate people who write Java
> from people who understand Java. Every SDE-2 candidate is expected to know these cold — not as trivia,
> but because misunderstanding them causes real bugs in production code.

> **Note**: OOP fundamentals (classes, objects, encapsulation, abstraction, inheritance, polymorphism, composition, enums, generics basics, equals/hashCode) are covered in the LLD syllabus Phase 1. This phase covers language mechanics that go deeper.

---

### 1.1 Primitives, Wrappers & Autoboxing
- 8 primitives — `byte`, `short`, `int`, `long`, `float`, `double`, `char`, `boolean`
- Each has a wrapper class — `Integer`, `Long`, `Double`, `Boolean`, etc.
- **Autoboxing** — compiler automatically converts `int` → `Integer` and vice versa
- **The trap**: `Integer a = 127; Integer b = 127; a == b` → true (cached). `Integer a = 128; Integer b = 128; a == b` → false (new objects). Java caches Integer values -128 to 127.
- **Null danger**: `Integer x = null; int y = x;` → NullPointerException at runtime (unboxing null)
- **Performance trap**: `Long sum = 0L; for (...) sum += i;` → creates a new Long object on every iteration. Use `long` (primitive) in tight loops.
- **Why wrappers exist**: generics require objects (`List<int>` is illegal, `List<Integer>` is required), null representation (a primitive can't be null)

### 1.2 Strings — Immutability, Pool & StringBuilder
- **Strings are immutable** — every "modification" creates a new String object. `s = s + "world"` creates a new object, the old one becomes garbage.
- **String Pool** — string literals are interned in a special pool in the heap. `"hello" == "hello"` → true (same reference). `new String("hello") == "hello"` → false (different reference, heap vs pool).
- **Why immutability matters**: thread-safe (no synchronization needed), safe as HashMap keys (hashCode never changes), security (connection strings, class names can't be tampered with after creation)
- **StringBuilder** — mutable, not thread-safe, use when building strings in a loop. `new StringBuilder().append("a").append("b").toString()`.
- **StringBuffer** — same as StringBuilder but synchronized (thread-safe). Almost never needed — prefer StringBuilder.
- **Interview question**: "Why is String immutable in Java?" — thread safety, string pool, security, caching hashCode.
- **Performance**: concatenating 10,000 strings in a loop with `+=` creates 10,000 intermediate objects. StringBuilder does it with one buffer.

### 1.3 Pass by Value — The Java Truth
- **Java is always pass by value.** There is no pass by reference in Java. Period.
- For primitives — the value is copied. Changing the parameter doesn't affect the original.
- For objects — the **reference is copied by value**. You can modify the object through the reference, but you cannot make the original variable point to a different object.
  ```
  void change(StringBuilder sb) {
      sb.append("world");  // modifies the original object ✓
      sb = new StringBuilder("new");  // does NOT affect the caller's variable
  }
  ```
- **The interview trap**: "Is Java pass by reference?" → No. Java passes object references by value. You can mutate the object, but you can't reassign the caller's variable.

### 1.4 The `final` Keyword
- **`final` variable** — can't be reassigned after initialization. For objects, the reference is fixed but the object's internal state can still change. `final List<String> list = new ArrayList<>(); list.add("hello");` → works. `list = new ArrayList<>();` → compile error.
- **`final` method** — can't be overridden by subclasses. Used when a method's behavior must not change in subclasses.
- **`final` class** — can't be extended. `String`, `Integer`, `Math` are all final classes.
- **`final` parameter** — can't be reassigned inside the method. Good practice for clarity.
- **Effectively final** — a variable that isn't declared final but is never reassigned. Required for lambda captures (covered in Phase 6).
- **`final` ≠ immutable** — `final` only prevents reassignment of the reference. The object itself can still be mutable.

### 1.5 The `static` Keyword
- **`static` field** — shared across all instances of the class. One copy in memory, lives in the method area (metaspace), not per-object on the heap.
- **`static` method** — belongs to the class, not to an instance. Can't access `this` or instance fields. Use for utility methods (`Math.max()`, `Collections.sort()`).
- **`static` block** — runs once when the class is loaded, before any instance is created. Used for complex static initialization.
- **`static` inner class** — nested class that doesn't hold a reference to the outer class. Preferred over non-static inner class in most cases (avoids memory leak from implicit outer reference).
- **Why `main` is static** — JVM needs to call it without creating an instance of the class first.
- **The memory implication**: static fields are never garbage collected while the class is loaded — they can cause memory leaks if they hold large collections that grow forever.

### 1.6 Inner Classes
- **Static nested class** — `static class Inner` — no reference to outer instance. Use when the inner class doesn't need the outer object. Most common and preferred.
- **Inner class (non-static)** — holds an implicit reference to the enclosing instance. `Outer.this` is accessible. Each inner object keeps its outer object alive → can cause memory leaks.
- **Anonymous class** — `new Runnable() { public void run() { ... } }` — inline implementation of an interface. Largely replaced by lambdas since Java 8, but still used when you need state.
- **Local class** — defined inside a method. Rare, almost never seen in practice.
- **Interview trap**: non-static inner class holds a hidden reference to the outer instance — if the inner class outlives the outer (e.g., registered as a listener), the outer object can't be garbage collected.

### 1.7 Type Casting & `instanceof`
- **Upcasting** — child to parent. Always safe, implicit. `Vehicle v = new Car();`
- **Downcasting** — parent to child. Needs explicit cast, can throw `ClassCastException`. `Car c = (Car) v;`
- **`instanceof` check** — always check before downcasting: `if (v instanceof Car) { Car c = (Car) v; }`
- **Pattern matching `instanceof`** (Java 16+) — `if (v instanceof Car c) { c.drive(); }` — cast and assign in one step.
- **Generics and casting** — due to type erasure, `(List<String>) obj` produces an unchecked cast warning. The runtime can't verify the generic type.

### 1.8 Annotations
- **What they are** — metadata about code. Don't change behavior directly but influence the compiler, tools, or frameworks.
- **Built-in annotations**:
  - `@Override` — compiler error if method doesn't actually override. Always use it.
  - `@Deprecated` — marks API as no longer recommended
  - `@SuppressWarnings` — suppresses compiler warnings (use sparingly)
  - `@FunctionalInterface` — compiler enforces exactly one abstract method
- **Framework annotations** (know these exist):
  - Spring: `@Autowired`, `@Component`, `@Service`, `@RestController`
  - JPA: `@Entity`, `@Table`, `@Column`, `@Id`
  - JUnit: `@Test`, `@BeforeEach`, `@Mock`
- **Custom annotations** — you can create your own. Know this is possible, don't need to know the syntax deeply.
- **Retention levels** — `SOURCE` (compile-time only), `CLASS` (in bytecode, not runtime), `RUNTIME` (available via reflection) — `RUNTIME` is most common for frameworks.

### 1.9 `==` vs `.equals()` — Deep Dive
- **`==`** compares references (are these the exact same object in memory?). For primitives, compares values.
- **`.equals()`** compares logical equality (do these objects represent the same thing?). Must be overridden to be useful — default `Object.equals()` does `==`.
- **String trap**: `"hello" == "hello"` → true (both from pool). `new String("hello") == new String("hello")` → false (different heap objects). `new String("hello").equals(new String("hello"))` → true.
- **The equals contract** — reflexive, symmetric, transitive, consistent, `x.equals(null)` returns false.
- **hashCode contract** — if `a.equals(b)` is true, then `a.hashCode() == b.hashCode()` must be true. Violating this breaks HashMap/HashSet silently.
- Covered at a basic level in LLD Phase 1. This section emphasizes the traps at scale — Integer caching, String pool, HashMap breakage.
