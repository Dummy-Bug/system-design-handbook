## Phase 8 — Modern Java Features (8 → 21)

> Interview relevance: Java moves fast now. Candidates stuck on Java 8 syntax signal they haven't
> kept up. SDE-2 at Google is expected to know records, sealed classes, and virtual threads at minimum.
> Modern features also make coding rounds faster — less boilerplate, more expressive code.

> **Note**: Java 8 features (lambdas, streams, Optional) are covered in Phase 6.
> This phase covers what's new from Java 9 onward.

---

### 8.1 Java 9 — Modules & Collection Factories
- **Modules (JPMS)** — the Java Platform Module System. Allows you to declare which packages a module exports and which modules it requires. Know it exists, know it's why you see `module-info.java`, don't need deep knowledge for interviews.
- **Collection factory methods** — immutable collections in one line:
  ```
  List<String> list = List.of("a", "b", "c");         // immutable
  Set<Integer> set = Set.of(1, 2, 3);                  // immutable, no duplicates
  Map<String, Integer> map = Map.of("a", 1, "b", 2);  // immutable
  ```
  - Throw `UnsupportedOperationException` on modification
  - Do not allow null elements (unlike ArrayList)
  - Preferred over `Arrays.asList()` (which returns a fixed-size list backed by the array — confusing)
- **Private interface methods** — interfaces can now have `private` helper methods. Keeps default methods clean.
- **`Stream.ofNullable()`** — creates a stream of 0 or 1 elements. Replaces `Optional.stream()` pattern.
- **`Stream.takeWhile()` / `dropWhile()`** — take or skip elements while predicate is true (short-circuiting).

### 8.2 Java 10 — `var` (Local Variable Type Inference)
- **What**: compiler infers the type from the right-hand side: `var list = new ArrayList<String>();` → type is `ArrayList<String>`.
- **Where it works**: local variables only. Not fields, not method parameters, not return types.
- **When to use**: when the type is obvious from context: `var reader = new BufferedReader(...)` — clear.
- **When NOT to use**: when the type isn't obvious: `var result = service.process(data)` — what type is result? Use explicit type for clarity.
- **`var` is not `Object`** — the compiler infers the actual type at compile time. `var x = "hello"; x.length()` works because `x` is `String`, not `Object`.
- **`var` with diamond**: `var list = new ArrayList<>();` → type is `ArrayList<Object>`, not what you want. Use `var list = new ArrayList<String>();`

### 8.3 Java 11 — String Methods & HTTP Client
- **New String methods**:
  - `isBlank()` — true if empty or only whitespace (unlike `isEmpty()` which is just `length() == 0`)
  - `strip()` — removes leading and trailing whitespace (Unicode-aware, unlike `trim()`)
  - `lines()` — returns `Stream<String>` split by line terminators
  - `repeat(n)` — `"abc".repeat(3)` → `"abcabcabc"`
- **`Files.readString(path)` / `Files.writeString(path, content)`** — read/write entire file as String in one line
- **HTTP Client API** — modern replacement for `HttpURLConnection`. Supports HTTP/2, async, WebSocket:
  ```
  HttpClient client = HttpClient.newHttpClient();
  HttpRequest request = HttpRequest.newBuilder().uri(URI.create("https://api.example.com")).build();
  HttpResponse<String> response = client.send(request, BodyHandlers.ofString());
  ```
- **`var` in lambda parameters**: `(var x, var y) -> x + y` — allows adding annotations to lambda params

### 8.4 Java 14 — Switch Expressions & Helpful NPE
- **Switch expressions** — switch returns a value, no fall-through, no break needed:
  ```
  // Old
  String result;
  switch (day) {
      case MONDAY: result = "Start"; break;
      case FRIDAY: result = "End"; break;
      default: result = "Middle"; break;
  }

  // New
  String result = switch (day) {
      case MONDAY -> "Start";
      case FRIDAY -> "End";
      default -> "Middle";
  };
  ```
  - Arrow syntax `->` = no fall-through
  - Can use blocks: `case MONDAY -> { yield "Start"; }` — `yield` returns the value from a block
  - Exhaustiveness: compiler ensures all cases are covered (especially useful with sealed classes)
- **Helpful NullPointerException**: instead of `Cannot invoke method on null`, Java now tells you exactly which variable was null: `Cannot invoke "String.length()" because "user.getName()" is null`. Saves debugging time.

### 8.5 Java 16 — Records & Pattern Matching instanceof
- **Records** — immutable data carriers with zero boilerplate:
  ```
  record Point(int x, int y) {}
  // Automatically generates: constructor, getters (x(), y()), equals(), hashCode(), toString()
  ```
  - All fields are `final` — immutable by design
  - Can have additional methods, static fields, and compact constructors (for validation)
  - Cannot extend another class (implicitly extends `Record`)
  - Can implement interfaces
  - **When to use**: DTOs, value objects, API responses, event payloads — anywhere you'd write a class with just fields, constructor, getters, equals, hashCode, toString
  - **When NOT to use**: mutable entities, classes with complex behavior, JPA entities (need no-arg constructor and mutable setters)

- **Pattern matching for `instanceof`**:
  ```
  // Old
  if (obj instanceof String) {
      String s = (String) obj;
      System.out.println(s.length());
  }

  // New
  if (obj instanceof String s) {
      System.out.println(s.length());  // s is already cast and scoped
  }
  ```
  - No separate cast needed — the variable is bound and typed in one step
  - Scoping: `s` is only in scope where the instanceof is guaranteed true

### 8.6 Java 17 — Sealed Classes
- **What**: restrict which classes can extend or implement a type. You control the complete hierarchy.
  ```
  sealed interface Shape permits Circle, Rectangle, Triangle {}
  record Circle(double radius) implements Shape {}
  record Rectangle(double width, double height) implements Shape {}
  final class Triangle implements Shape { ... }
  ```
- **Permitted subclasses must be**: `final`, `sealed` (further restricted), or `non-sealed` (open for extension)
- **Why it matters**: the compiler knows ALL possible subtypes. This enables exhaustive switch (no default needed):
  ```
  double area = switch (shape) {
      case Circle c -> Math.PI * c.radius() * c.radius();
      case Rectangle r -> r.width() * r.height();
      case Triangle t -> calculateTriangleArea(t);
      // no default needed — compiler knows these are all cases
  };
  ```
- **When to use**: domain types with a fixed set of variants (payment types, event types, AST nodes, state machine states). Replaces the "enum + visitor" pattern with something more natural.
- **Interview signal**: sealed classes + records + pattern matching switch is the modern Java way to model algebraic data types. Mentioning this shows you know post-Java-8 Java.

### 8.7 Java 21 — Virtual Threads, Pattern Matching Switch, Sequenced Collections
- **Virtual Threads** — covered in Phase 5 (Concurrency). The headline feature of modern Java.
- **Pattern matching for switch** (finalized):
  ```
  String describe(Object obj) {
      return switch (obj) {
          case Integer i when i > 0 -> "positive integer: " + i;
          case Integer i -> "non-positive integer: " + i;
          case String s -> "string of length " + s.length();
          case null -> "null";
          default -> "unknown: " + obj;
      };
  }
  ```
  - Type patterns: `case Integer i ->` matches and binds
  - Guarded patterns: `case Integer i when i > 0 ->` adds a condition
  - Null handling: `case null ->` instead of NPE
  - Exhaustiveness: compiler checks coverage
- **Sequenced Collections** — new interfaces for collections with a defined encounter order:
  - `SequencedCollection<E>` — `getFirst()`, `getLast()`, `reversed()`
  - `SequencedSet<E>` — ordered set with first/last access
  - `SequencedMap<K,V>` — `firstEntry()`, `lastEntry()`, `reversed()`
  - Fixes the awkwardness of `list.get(list.size() - 1)` → now just `list.getLast()`
  - `LinkedHashSet`, `TreeSet`, `LinkedHashMap`, `TreeMap` all implement these

### 8.8 Feature Summary — What to Know per Version

| Version | Key Features | Interview Priority |
|---------|-------------|-------------------|
| Java 8 | Lambdas, Streams, Optional, default methods, CompletableFuture, Date/Time API | Must know |
| Java 9 | `List.of()`, `Set.of()`, `Map.of()`, modules, private interface methods | Must know collection factories |
| Java 10 | `var` | Must know |
| Java 11 | `String.isBlank()`, `strip()`, `lines()`, `Files.readString()`, HTTP Client | Must know |
| Java 14 | Switch expressions, helpful NPE | Must know switch expressions |
| Java 16 | Records, pattern matching instanceof | Must know |
| Java 17 | Sealed classes | Must know |
| Java 21 | Virtual threads, pattern matching switch, sequenced collections | Must know virtual threads |
