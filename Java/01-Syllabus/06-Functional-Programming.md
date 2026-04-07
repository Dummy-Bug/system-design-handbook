## Phase 6 — Functional Programming in Java

> Interview relevance: Modern Java codebases are full of lambdas, streams, and Optional. SDE-2 candidates
> are expected to write fluent stream pipelines and explain lazy evaluation. Google and Amazon coding rounds
> frequently involve stream-based solutions, and code reviews at this level penalize verbose imperative code
> where a clean stream pipeline would do.

---

### 6.1 Lambda Expressions
- **What**: anonymous functions passed as arguments. Replaced verbose anonymous inner classes.
  ```
  // Before (anonymous class)
  Runnable r = new Runnable() {
      public void run() { System.out.println("hello"); }
  };

  // After (lambda)
  Runnable r = () -> System.out.println("hello");
  ```
- **Syntax**: `(parameters) -> expression` or `(parameters) -> { statements; }`
- **Type inference**: compiler infers parameter types from context. `(String s) -> s.length()` can be `s -> s.length()`.
- **Effectively final**: lambdas can capture variables from the enclosing scope, but those variables must be effectively final (never reassigned). This is because the lambda may execute later, on a different thread — if the variable changed, which value should the lambda see?
  ```
  int x = 10;
  Runnable r = () -> System.out.println(x); // OK — x is effectively final
  x = 20; // Compile error — x is no longer effectively final
  ```
- **`this` in lambdas**: `this` refers to the enclosing class, not the lambda itself. Unlike anonymous inner classes where `this` refers to the anonymous class.

### 6.2 Functional Interfaces
- **Definition**: an interface with exactly one abstract method. Lambdas can only be assigned to functional interfaces. `@FunctionalInterface` annotation makes this explicit.
- **Core functional interfaces** (java.util.function — know these cold):

  | Interface | Method | Signature | Use |
  |-----------|--------|-----------|-----|
  | `Predicate<T>` | `test(T)` | `T → boolean` | Filtering, conditions |
  | `Function<T,R>` | `apply(T)` | `T → R` | Transformation, mapping |
  | `Consumer<T>` | `accept(T)` | `T → void` | Side effects (print, log, save) |
  | `Supplier<T>` | `get()` | `() → T` | Lazy creation, factory |
  | `UnaryOperator<T>` | `apply(T)` | `T → T` | Same-type transformation |
  | `BinaryOperator<T>` | `apply(T,T)` | `(T,T) → T` | Reducing, combining |
  | `BiFunction<T,U,R>` | `apply(T,U)` | `(T,U) → R` | Two-input transformation |
  | `BiPredicate<T,U>` | `test(T,U)` | `(T,U) → boolean` | Two-input condition |

- **Composition**: `predicate1.and(predicate2)`, `function1.andThen(function2)`, `function1.compose(function2)`
- **Primitive variants**: `IntPredicate`, `LongFunction`, `ToIntFunction` — avoid autoboxing overhead

### 6.3 Method References
- Shorthand for lambdas that just call an existing method.
- **Four kinds**:
  | Kind | Lambda | Method Reference |
  |------|--------|-----------------|
  | Static method | `s -> Integer.parseInt(s)` | `Integer::parseInt` |
  | Instance method of a parameter | `s -> s.toUpperCase()` | `String::toUpperCase` |
  | Instance method of a specific object | `s -> printer.print(s)` | `printer::print` |
  | Constructor | `s -> new ArrayList<>(s)` | `ArrayList::new` |
- **When to use**: when the lambda body is just a method call with no additional logic. Improves readability.

### 6.4 Streams API
- **What**: a pipeline for processing sequences of elements. Declarative (what, not how), lazy (intermediate operations are not executed until a terminal operation is called), single-use (can't reuse a stream after terminal operation).
- **Three stages**: source → intermediate operations → terminal operation

#### Source creation
- `collection.stream()` — from any Collection
- `Stream.of("a", "b", "c")` — from values
- `Arrays.stream(array)` — from array
- `IntStream.range(0, 10)` — primitive stream, 0 to 9
- `Stream.generate(() -> Math.random())` — infinite stream
- `Stream.iterate(0, n -> n + 1)` — infinite sequence
- `Files.lines(path)` — stream of lines from a file

#### Intermediate operations (lazy — nothing happens until terminal)
- `filter(predicate)` — keep elements matching condition
- `map(function)` — transform each element
- `flatMap(function)` — transform + flatten (each element → stream → merged into one stream)
- `sorted()` / `sorted(comparator)` — sort
- `distinct()` — remove duplicates (uses equals/hashCode)
- `peek(consumer)` — side effect without modifying (debugging only — don't use for business logic)
- `limit(n)` — take first n elements
- `skip(n)` — skip first n elements

#### Terminal operations (trigger execution)
- `collect(collector)` — gather into a collection
- `reduce(identity, accumulator)` — combine all elements into one: `reduce(0, Integer::sum)`
- `forEach(consumer)` — apply side effect to each element
- `count()` — count elements
- `findFirst()` / `findAny()` — return Optional
- `anyMatch(predicate)` / `allMatch()` / `noneMatch()` — boolean check
- `toArray()` — collect to array
- `min(comparator)` / `max(comparator)` — return Optional

#### Collectors (used with `.collect()`)
- `Collectors.toList()` — collect to List
- `Collectors.toSet()` — collect to Set
- `Collectors.toMap(keyMapper, valueMapper)` — collect to Map
- `Collectors.groupingBy(classifier)` — group into Map<K, List<V>> (like SQL GROUP BY)
- `Collectors.partitioningBy(predicate)` — split into Map<Boolean, List<V>>
- `Collectors.joining(", ")` — concatenate strings with delimiter
- `Collectors.counting()` — count per group (used inside groupingBy)
- `Collectors.summarizingInt(mapper)` — count, sum, min, max, avg in one pass

### 6.5 Parallel Streams
- `collection.parallelStream()` or `stream.parallel()` — splits work across ForkJoinPool.commonPool()
- **When safe**: stateless operations, no shared mutable state, no ordering requirement, CPU-bound work on large datasets
- **When dangerous**:
  - Shared mutable state → race conditions
  - Small collections → overhead of parallelism > benefit
  - I/O operations → threads block, starves the common pool (use CompletableFuture instead)
  - Operations requiring ordering → parallel may change encounter order
  - Side-effecting operations in `forEach` → non-deterministic order
- **Common pool size**: defaults to `Runtime.getRuntime().availableProcessors() - 1`. Shared across the entire JVM — one bad parallel stream can starve all others.
- **Interview answer**: "I'd avoid parallel streams unless the dataset is large (10K+ elements), the operation is CPU-bound, stateless, and order-independent. For I/O-bound work, CompletableFuture gives better control."

### 6.6 Optional — Replacing Null
- **What**: a container that may or may not hold a value. Forces you to handle the absent case explicitly instead of returning null and hoping the caller checks.
- **Creating**: `Optional.of(value)` (throws if null), `Optional.ofNullable(value)` (empty if null), `Optional.empty()`
- **Consuming**:
  - `isPresent()` / `isEmpty()` — check (avoid these — they defeat the purpose)
  - `ifPresent(consumer)` — execute only if present
  - `orElse(default)` — return value or default. **Warning**: default is always evaluated even if value is present.
  - `orElseGet(supplier)` — return value or lazily compute default. Preferred over `orElse()` when default is expensive.
  - `orElseThrow()` — return value or throw NoSuchElementException
  - `orElseThrow(exceptionSupplier)` — return value or throw custom exception
- **Transforming**:
  - `map(function)` — transform the value if present, return Optional
  - `flatMap(function)` — transform when function returns Optional (avoids Optional<Optional<T>>)
  - `filter(predicate)` — keep value only if predicate matches
- **Anti-patterns**:
  - `if (optional.isPresent()) return optional.get()` — just use `orElse()` or `map()`
  - `Optional` as a method parameter — bad, makes API awkward. Use overloading or nullable instead.
  - `Optional` as a field — bad, not serializable, adds overhead. Use null with a clear contract.
  - `Optional<Collection>` — return an empty collection instead of Optional
- **Where to use**: method return types when the result may not exist. `Optional<User> findByEmail(String email)`
