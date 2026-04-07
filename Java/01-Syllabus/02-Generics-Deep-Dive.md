## Phase 2 — Generics Deep Dive

> Interview relevance: Generics separate "I use Java" from "I understand Java's type system."
> SDE-2 candidates get asked about type erasure, wildcards, and PECS — not as trivia, but because
> writing a generic cache, repository, or event system requires this knowledge.

> **Note**: LLD Phase 1 covers basic generics usage (`List<Vehicle>`, bounded generics). This phase goes into the mechanics that break people in interviews.

---

### 2.1 Why Generics Exist
- Before generics (pre-Java 5): `List list = new ArrayList(); list.add("hello"); String s = (String) list.get(0);` — casts everywhere, `ClassCastException` at runtime if you put the wrong type in
- With generics: `List<String> list = new ArrayList<>(); list.add("hello"); String s = list.get(0);` — type checked at compile time, no cast needed, wrong type = compile error
- **The principle**: catch type errors at compile time, not runtime. Move the bug from production to the IDE.

### 2.2 Type Erasure — What Happens at Runtime
- **The shocking truth**: generics only exist at compile time. At runtime, `List<String>` and `List<Integer>` are both just `List`. The JVM has no idea about the generic type.
- The compiler checks types, then **erases** all generic information and inserts casts where needed.
- Before compilation: `List<String> list; String s = list.get(0);`
- After erasure: `List list; String s = (String) list.get(0);` — the compiler inserted the cast
- **Why this matters in practice**:
  - `list instanceof List<String>` → compile error. You can't check generic type at runtime.
  - `new T()` → impossible. The runtime doesn't know what `T` is.
  - `new T[]` → impossible. Same reason.
  - `List<String>.class` → doesn't exist. Only `List.class`.
- **Why Java did this**: backward compatibility. Generic code needed to work with pre-Java-5 libraries that used raw types.
- **Interview question**: "Can you check if a List is a List<String> at runtime?" → No, due to type erasure. The generic type is erased at compile time.

### 2.3 Wildcards — `?`, `extends`, `super`
- **Unbounded wildcard `?`** — `List<?>` means "list of something, I don't know what." You can read from it (get `Object`) but can't write to it (compiler doesn't know what type is safe to add).
- **Upper bounded `? extends T`** — `List<? extends Number>` means "list of Number or any subclass (Integer, Double, etc.)." You can **read** as Number, but **can't write** (might be a `List<Integer>`, adding a `Double` would be wrong).
- **Lower bounded `? super T`** — `List<? super Integer>` means "list of Integer or any superclass (Number, Object)." You can **write** Integers, but reading gives you `Object` (might be a `List<Object>`).
- **Why this exists**: enables writing flexible methods that work with class hierarchies without casting.

### 2.4 PECS — Producer Extends, Consumer Super
- The rule that makes wildcards click:
  - If you're **reading from** a generic structure (it produces values) → use `extends`
  - If you're **writing to** a generic structure (it consumes values) → use `super`
- **Example — copy method**:
  ```
  void copy(List<? extends T> source, List<? super T> dest) {
      for (T item : source) {  // reading from source → extends
          dest.add(item);       // writing to dest → super
      }
  }
  ```
- **Real-world use**: `Collections.sort(List<T>)` internally uses PECS. `Comparator<? super T>` — the comparator consumes T values to compare them.
- **Interview mnemonic**: "PE-CS" — Producer Extends, Consumer Super. If you only need to read → extends. If you only need to write → super. If both → don't use wildcards, use a concrete type.

### 2.5 Bounded Type Parameters
- `<T extends Comparable<T>>` — T must implement Comparable. Now you can call `t.compareTo()` inside the method.
- `<T extends Number & Serializable>` — T must be a Number AND implement Serializable. Multiple bounds with `&`.
- The bound on a type parameter is different from a wildcard: the type parameter gives you a name `T` you can use throughout the class/method. Wildcards are anonymous.
- **When to use**: When you need to use the type in multiple places (return type, multiple parameters, field type) → type parameter. When you just need to accept a range of types in one place → wildcard.

### 2.6 Generic Methods
- A method can have its own type parameter independent of the class:
  ```
  public <T> T firstOrNull(List<T> list) {
      return list.isEmpty() ? null : list.get(0);
  }
  ```
- The compiler infers `T` from the argument: `firstOrNull(listOfStrings)` → `T` is `String`.
- **Static generic methods** — static methods can't use the class's type parameter (there's no instance). They must declare their own: `public static <T> List<T> of(T... elements)`.

### 2.7 Limitations You Must Know
- `new T()` — illegal. Workaround: pass a `Supplier<T>` or `Class<T>` and call `.newInstance()`.
- `new T[]` — illegal. Workaround: `(T[]) new Object[size]` with `@SuppressWarnings("unchecked")`.
- `instanceof T` — illegal at runtime (type erasure).
- Primitives — `List<int>` is illegal. Must use `List<Integer>`. This is why `IntStream`, `LongStream` exist — to avoid boxing overhead for primitives.
- **Static fields can't use the class type parameter** — `static T instance;` is illegal. `T` is per-instance, static is per-class.
- **Exception classes can't be generic** — `class MyException<T> extends Exception` is illegal.
- Overloading by generic type — `void process(List<String> list)` and `void process(List<Integer> list)` have the same erasure → compile error.
