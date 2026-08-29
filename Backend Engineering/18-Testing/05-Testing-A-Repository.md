A service test mocks the repository because the database is what makes a test slow and flaky. That reasoning collapses when the repository itself is the thing under test — mock the database and nothing is left to check.

# The repository is a different problem

> [!important] A repository has almost no logic of its own. What it has is **queries** — derived from method names, or written by hand — and a query can only be verified by running it against a database that understands it.

So the database comes back. The trick is that it is not your database.

# H2

> [!important] **H2 is a relational database written in Java that can run entirely in memory.** It starts with the JVM, holds the schema and data in RAM, and vanishes when the process exits.

```groovy
1  testImplementation 'com.h2database:h2'
```

> [!important] One dependency and nothing to install. **Because it is a Java library rather than a server**, there is no process to start, no port, and nothing for a colleague to set up before the suite runs.

# A separate configuration for tests

```text
  src/
  ├── main/resources/application.yml     ← MySQL, Flyway, validate
  └── test/resources/application.yml     ← H2, create-drop, no Flyway
```

> [!important] **The test source set has its own resources folder**, and a file there takes precedence when tests run. Nothing about the main configuration changes.

```yaml
1  # src/test/resources/application.yml
2  spring:
3    datasource:
4      url: jdbc:h2:mem:testdb
5      username: sa
6      password: ''
7      driver-class-name: org.h2.Driver
8    jpa:
9      hibernate:
10       ddl-auto: create-drop
11     show-sql: true
12   flyway:
13     enabled: false
```

Three lines carry real decisions.

> [!important] **Line 4 — `mem:testdb`** is what makes it in-memory. Nothing touches disk.

> [!important] **Line 10 — `create-drop`** builds the schema from your entities at startup and destroys it at the end. **Every run starts from an empty database**, which is what makes a test that asserts exactly one row reliable rather than accidental.

> [!important] **Line 13 — Flyway off.** Migrations are MySQL-specific and Hibernate is generating the schema here anyway. Leaving Flyway on means running MySQL DDL against H2, which fails.

> [!warning] And that is the trade this makes. **The tests run against a schema Hibernate generated, not the one Flyway builds.** They verify your queries; they do not verify that your migrations produce a matching schema. Testcontainers — running real MySQL in a container — is the answer where that gap matters.

> [!info] For a non-relational store there is no H2 equivalent. A MongoDB repository is tested against a separate test instance, flushed between runs.

# The slice annotations

```java
1  @DataJpaTest
2  @AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.ANY)
3  @Import(TestJpaConfig.class)
4  public class ProductRepositoryTest {
```

> [!important] **`@DataJpaTest` loads only the JPA parts** — entities, repositories, the entity manager, a transaction manager. No controllers, no services, no web server. A **slice** of the application rather than all of it.

> [!important] **`@AutoConfigureTestDatabase(replace = ANY)`** discards whatever `DataSource` was configured and substitutes the embedded one. Without it the test would connect to your real MySQL.

`@Import` brings in one configuration class, and the reason it is needed is worth its own section.

# The auditing problem

Auditing was switched on with `@EnableJpaAuditing` on the application class:

```java
1  @SpringBootApplication
2  @EnableJpaAuditing          // ← the problem
3  public class FakeCommerceApplication { }
```

> [!warning] **A slice test does not load the application class**, so auditing is not enabled and `createdAt` is never populated — and `created_at` is `NOT NULL`. Every insert in every repository test fails on a constraint violation.

The fix is to move the annotation somewhere a test can opt into:

```java
1  // src/main/java/com/example/FakeCommerce/config/JpaAuditingConfig.java
2  @Configuration
3  @EnableJpaAuditing
4  public class JpaAuditingConfig { }
```

```java
1  // src/test/java/com/example/FakeCommerce/config/TestJpaConfig.java
2  @Configuration
3  @EnableJpaAuditing
4  public class TestJpaConfig { }
```

Remove it from `FakeCommerceApplication`, and the test imports the test one.

> [!important] **Auditing still works in production**, because component scan finds `JpaAuditingConfig` like any other configuration. The slice test picks it up through `@Import` instead.

> [!important] The general lesson is worth more than the fix. **Cross-cutting configuration on the application class is invisible to slice tests**, and the symptom is a constraint violation that says nothing about the cause. Putting each concern in its own `@Configuration` makes it something a test can request.

# Getting data in

```java
1  @Autowired
2  private TestEntityManager testEntityManager;
3
4  @BeforeEach
5  void setUp() {
6      category = Category.builder().name("Electronics").build();
7      product = Product.builder()
8          .title("Phone")
9          .price(BigDecimal.valueOf(999.0).setScale(2, RoundingMode.HALF_UP))
10         .rating(BigDecimal.valueOf(4.5).setScale(2, RoundingMode.HALF_UP))
11         .category(category)
12         .build();
13
14     testEntityManager.persistAndFlush(category);
15     testEntityManager.persistAndFlush(product);
16     testEntityManager.clear();
17 }
```

> [!important] **`@BeforeEach` runs before every test in the class.** Where a service test arranges inside each method, a repository test usually needs the same rows every time — so the arrange step moves here and the tests themselves are act and assert only.

> [!info] `@AfterEach` is its counterpart. With `create-drop` it is rarely needed, since the schema is rebuilt anyway.

## The three entity-manager calls

| | |
|---|---|
| **`persist`** | Tells JPA this is a new entity. **Nothing reaches the database** — it sits in the persistence context |
| **`flush`** | Issues the actual `INSERT` |
| **`persistAndFlush`** | Both, which is what a test wants |
| **`clear`** | Detaches everything from the persistence context |

> [!important] **`clear` is the one that is easy to skip and matters most.** Without it the entities stay in Hibernate's first-level cache, and a subsequent `findById` may be answered from memory without a query ever running. **The test would pass without touching the database** — which is precisely what a repository test exists to do.

# The test itself

```java
1  @Test
2  void findProductWithDetailsById_whenFound_returnsProductWithCategory() {
3      // act
4      List<Product> result = productRepository.findProductWithDetailsById(product.getId());
5
6      // assert
7      assertEquals(1, result.size());
8      assertEquals(category, result.get(0).getCategory());
9      assertEquals(product.getTitle(), result.get(0).getTitle());
10     assertEquals(product.getPrice(), result.get(0).getPrice());
11     assertEquals(product.getCategory().getName(), result.get(0).getCategory().getName());
12 }
```

**Line 7 asserts exactly one row**, which is only meaningful because `create-drop` guarantees the database started empty. **Line 8 asserts the category came back with it**, which is the whole point of a query written to fetch details in one go.

## The BigDecimal trap

The first run failed with `expected 999.00 but was 999.0`.

> [!warning] **`BigDecimal.equals` compares scale as well as value.** `999.0` and `999.00` are numerically equal and not `equals`. The column is `DECIMAL(38,2)`, so what comes back from the database has scale 2 — and the object built in the test had scale 1.

```java
  BigDecimal.valueOf(999.0).setScale(2, RoundingMode.HALF_UP)
```

> [!important] **Set the scale on the expected value to match the column.** The alternative is `compareTo(...) == 0`, which ignores scale. **This is not a testing quirk** — the same comparison is wrong anywhere in application code that compares two `BigDecimal` values with `equals`.

# What this layer proves

> [!important] **That your queries actually run and return what you expect** — including derived method names and hand-written JPQL, which are strings the compiler never checks. A typo in a query is invisible until something executes it, and this is the cheapest place to find out.

> [!warning] What it does not prove is anything about MySQL. **H2 is a different engine**, and query behaviour, type mapping and index handling all differ. A query that works here can still fail in production, which is the gap Testcontainers exists to close.
