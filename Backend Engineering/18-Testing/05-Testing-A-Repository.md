A service test mocks the repository because the database is what makes a test slow and flaky. That reasoning collapses when the repository itself is the thing under test — mock the database and nothing is left to check.

# The repository is a different problem

> [!important] A repository has almost no logic of its own. What it has is **queries** — derived from method names, or written by hand — and a query can only be verified by running it against a database that understands it.

## Mocking it proves nothing

A service test uses no Spring at all:

```java
1  @ExtendWith(MockitoExtension.class)
2  class CategoryServiceTest {
3      @Mock        CategoryRepository categoryRepository;
4      @InjectMocks CategoryService    categoryService;
```

`MockitoExtension` is JUnit and Mockito and nothing else. Mockito builds a fake `CategoryRepository`, hands it to a real `CategoryService` through the constructor, and Spring never starts — no context, no beans, no database, and a suite that finishes in well under a second.

Now write the same shape for a repository:

```java
1  @ExtendWith(MockitoExtension.class)
2  class ProductRepositoryTest {
3      @Mock ProductRepository productRepository;   // and then what?
```

The thing the test came to examine has been replaced by a fake. Stubbing `findProductWithDetailsById` to return a product and then asserting it returns that product is a test of Mockito.

And it cannot be arranged otherwise, because of what a repository holds:

```java
1  @Query("SELECT p FROM Product p JOIN FETCH p.category WHERE p.id = :id")
2  List<Product> findProductWithDetailsById(Long id);
```

> [!important] That is a **string**. No Java executes it — a database parses it, plans it and runs it. Mockito cannot run a query, so the only way to find out whether this one is correct is to let a database try.

## Starting everything is too much

A real database means somebody has to build a `DataSource`, read the `@Entity` classes, create tables from them, start an `EntityManager` and hand back a working repository. That is Spring's work, so Spring has to start.

The blunt way to start it:

```java
1  @SpringBootTest
2  class ProductRepositoryTest {
3      @Autowired ProductRepository productRepository;
```

This works, and to run one query it builds every bean in the application:

| what starts | what it needs |
|---|---|
| every controller, service and adapter | nothing, but all of them are instantiated |
| the Redis cache and its connection factory | **Redis running** |
| Flyway | every migration applied in order |
| the `DataSource` | **the real development database** |

Three problems fall out of that, and only one of them is speed.

> [!warning] **The repository test now fails when Redis is down.** The context cannot be built, so the test errors before reaching the query — and the failure names Redis, which has nothing to do with what is being tested.

> [!warning] **It runs against the actual development database.** A test insert lands in the same schema being browsed in a database client.

> [!warning] **It is slow enough to change how you work.** A full context per test class is the difference between running tests while writing them and not bothering.

> [!important] So the requirement is precise. **Spring has to start, and about a fifth of it is needed.** That is what a slice is.

And the database it starts against should not be the development one either.

# H2

> [!important] **H2 is a relational database written in Java that can run entirely in memory.** It starts with the JVM, holds the schema and data in RAM, and vanishes when the process exits.

```groovy
  testImplementation 'com.h2database:h2'
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

> [!important] **Line 4 — `mem:testdb`** names an in-memory database rather than a file on disk.

> [!important] **Line 10 — `create-drop`** builds the schema from your entities at startup and destroys it at the end. **Every run starts from an empty database**, which is what makes a test that asserts exactly one row reliable rather than accidental.

> [!important] **Line 13 — Flyway off.** Migrations are MySQL-specific and Hibernate is generating the schema here anyway. Leaving Flyway on means running MySQL DDL against H2, which fails.

> [!warning] Whether all three take effect is a separate question, settled under the slice annotations below. **One of them does not.**

> [!warning] And that is the trade this makes. **The tests run against a schema Hibernate generated, not the one Flyway builds.** They verify your queries; they do not verify that your migrations produce a matching schema. Testcontainers — running real MySQL in a container — is the answer where that gap matters.

> [!info] For a non-relational store there is no H2 equivalent. A MongoDB repository is tested against a separate test instance, flushed between runs.

# The slice annotations

```java
1  @DataJpaTest
2  @AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.ANY)
3  @Import(JpaAuditingConfig.class)
4  public class ProductRepositoryTest {
```

Three separate decisions, and each is taken up below.

## What `@DataJpaTest` loads

The natural assumption is everything except the web layer. It is not that. **A slice is a whitelist** — a fixed set of auto-configurations, plus a component scan filtered down to two kinds of class.

```java
1  @DataJpaTest
2  class ProductRepositoryTest {
3
4      @Autowired ProductRepository productRepository;   // fine
5      @Autowired ProductService    productService;      // context fails to start
6  }
```

Line 5 kills the test with a `NoSuchBeanDefinitionException` naming `ProductService`. Not because services are forbidden, but because **the scan never looked for them.**

| in the context | not in the context |
|---|---|
| `@Entity` classes | `@Service` |
| Spring Data repositories | `@Component` |
| the entity manager | `@RestController` |
| a transaction manager | your own `@Configuration` classes |
| a `DataSource` | anything else you wrote |

> [!warning] Read the right-hand column carefully. **Your own configuration classes are not loaded either**, which becomes a problem further down.

The slice also contributes beans of its own — `TestEntityManager`, met below, is one you never declared anywhere.

## Every test is rolled back

Each test method runs inside a transaction that is **never committed**.

```java
1  @Test
2  void one() {
3      testEntityManager.persistAndFlush(product);   // inserts a row
4  }
5
6  @Test
7  void two() {
8      assertEquals(0, productRepository.count());   // passes
9  }
```

Test `one` inserted a product and test `two` sees an empty table. Nothing cleaned up between them; the transaction wrapping `one` was simply rolled back when the method ended.

> [!important] This is a **different mechanism from `create-drop`**, and the two cover different gaps.

| | scope | what it gives |
|---|---|---|
| `ddl-auto: create-drop` | once per JVM | a fresh **schema** for the run |
| the slice's rollback | once per test method | a fresh **state** for each test |

> [!warning] Spring caches a test context and **reuses it across test classes** in the same run, so two repository test classes share one schema and one database. Without the rollback, whatever the first class inserted would still be sitting there when the second one started, and the order the classes happened to run in would decide whether they passed.

Nothing has to be written to get any of this — the rollback is automatic.

## What a `DataSource` is

Running a query needs a connection to the database — a socket, opened and authenticated. Opening one takes a few milliseconds, so doing it per query would mean paying that cost on every request. Instead a handful of connections are opened at startup and **kept open**, handed out and taken back.

> [!important] A **`DataSource`** is the object that owns that pool.

```java
1  Connection c = dataSource.getConnection();   // borrow one from the pool
2  c.close();                                   // not closed — returned to the pool
```

Which is what a line like this in a test run is reporting, and why it needs a shutdown at all — there are real open sockets to close:

```text
  com.zaxxer.hikari.HikariDataSource : HikariPool-1 - Shutdown initiated...
```

> [!important] In Spring that object is **a bean**: built once at startup, kept in the context, and handed to everything that needs it — Hibernate, Flyway, the repositories. Nothing creates its own.

And it is built from four lines of configuration:

```yaml
1  spring:
2    datasource:
3      url: jdbc:h2:mem:testdb
4      username: sa
5      password: ''
6      driver-class-name: org.h2.Driver
```

Spring reads those, constructs a connection pool from them, and registers it as the `DataSource` bean. **They are constructor arguments written as yaml.**

## Which database the test actually gets

So the natural reading of that file is that those four lines are the connection the test uses. They are not. Follow the startup in order.

**Spring builds your pool.** It reads `test/resources/application.yml`, sees the four `datasource:` lines and constructs a connection pool from them pointing at `jdbc:h2:mem:testdb`. Call it **pool A**, registered as the `DataSource` bean exactly as above.

**The slice has an opinion.** `@DataJpaTest` exists to guarantee one thing — that the test runs against a throwaway database rather than a development or production one.

> [!important] **It does not check, it replaces.** Pool A is not inspected to see whether it is already disposable, and its URL is not examined. The bean is discarded and a different one registered in its place. **Pool A is built and then never used by anything.**

**What goes in its place.** Spring looks on the test classpath for an embedded database it recognises — it knows H2, HSQLDB and Derby. One dependency puts H2 there:

```groovy
1  testImplementation 'com.h2database:h2'
```

So it builds an in-memory H2 of its own, **pool B**, under a name it picks itself rather than the `testdb` that was written.

| | built from | actually used |
|---|---|---|
| **pool A** | the four yaml lines | no, discarded |
| **pool B** | Spring, from H2 on the classpath | **yes** |

> [!warning] Which is why this goes unnoticed. **Both are H2, both are in memory, and both work.** The tests pass, the queries run, the schema is created. The substitution is invisible because the replacement happens to be the same engine that was asked for.

The only way to see it is to look at the URL:

```java
1  @Autowired DataSource dataSource;
2
3  @Test
4  void whichDatabase() throws Exception {
5      System.out.println(dataSource.getConnection().getMetaData().getURL());
6  }
```

If the yaml were in effect that prints `jdbc:h2:mem:testdb`.

## Why the rest of the file still works

If that file's datasource block was thrown away, why does anything else in it survive?

> [!important] Because a yaml file is not one instruction to one object. **It is instructions to several different beans that happen to share a file.**

| yaml section | which bean it configures | replaced |
|---|---|---|
| `spring.datasource.*` | **the `DataSource`**, the pool | **yes** |
| `spring.jpa.hibernate.ddl-auto` | Hibernate's entity manager factory | no |
| `spring.jpa.show-sql` | the same | no |
| `spring.flyway.enabled` | the Flyway bean | no |

> [!important] **Replacement is per bean, not per file.** `@AutoConfigureTestDatabase` replaces the `DataSource`. It has no opinion about Hibernate and none about Flyway, so their settings are read and applied exactly as written.

Which leads somewhere worth pausing on: `create-drop` still builds the schema, and it builds it **in pool B**. Hibernate holds no URL of its own — it is handed the `DataSource` bean, whichever bean that turns out to be, and creates its tables through it. By the time Hibernate runs, that bean is the substitute.

`show-sql: true` survives the same way, which is why Hibernate's SQL appears in test output at all. So does `flyway.enabled: false`, and it still matters — left on, Flyway would run MySQL migrations against H2 and fail.

> [!important] The settings and the connection are independent. **The connection was lost and every instruction about what to do with it was kept.**

## Why replace at all

If the file already configures a disposable H2, replacing it looks like the thing causing all this confusion. The answer is that **most projects have no `test/resources/application.yml`.** Writing one is the exception, and without it the pool is built from `main/resources/application.yml` instead:

```yaml
1  spring:
2    datasource:
3      url: jdbc:mysql://localhost:3306/lab     # the actual database
4    jpa:
5      hibernate:
6        ddl-auto: create-drop                  # read that again
```

> [!warning] `create-drop` **drops every table at the end of the run.** Pointed at a development database, the schema and all its data are gone — because a file was missing.

That is the failure being prevented. Not a slow test: **a database deleted, silently, by running the test suite.**

> [!important] So the annotation does not ask whether the configured database looks disposable. **It guarantees one by substituting one.** A guarantee that depends on configuration being present is not a guarantee.

| approach | configured correctly | file missing |
|---|---|---|
| use what is configured | works | **the development database is dropped** |
| replace unconditionally | works, under a different H2 name | works |

What is lost is a URL that is not the one you wrote — confusing for an afternoon and harmless afterwards. What it prevents is unrecoverable.

> [!info] A consequence worth noticing: since the `datasource:` block is discarded either way, those four lines contribute nothing. The file behaves identically with only the `jpa:` and `flyway:` sections in it.

## When replacing is the wrong thing to do

The rule above is to substitute a disposable database, because a configured one cannot be trusted to be disposable. There is one case where that rule is wrong: **when the test deliberately supplied a database, and a better one.**

Recall why H2 is here at all. Real MySQL is inconvenient for tests — installed, kept running, cleaned out between runs so one test does not see another's rows. H2 sidesteps that by appearing and disappearing with the test run. And it costs something: H2 is not MySQL, so a query can pass here and fail in production.

> [!important] **Testcontainers** starts a real, empty MySQL for the test run and destroys it afterwards. Nothing installed, nothing left behind. The same disposability as H2, on the engine actually deployed on — so a query that passes has proved something about production.

Which puts two things in charge of the same decision. Testcontainers has started a MySQL and says use this one; `@AutoConfigureTestDatabase` says always substitute an embedded database.

> [!warning] If the substitution happens regardless, **the MySQL that was just started is discarded** and the test runs on H2. It still passes. The effort of testing against real MySQL was spent, the tests are still on H2, and nothing anywhere says so.

So the annotation has a setting:

| `replace` | behaviour |
|---|---|
| the default | substitute — **unless the test explicitly supplied a database**, in which case leave it alone |
| `ANY` | substitute regardless of where the database came from |

An ordinary `jdbc:h2:mem:testdb` in a configuration file is not explicitly supplied, so **both values replace it.** Writing `ANY` changes nothing today, and removing that line changes nothing either.

| | with the default | with `ANY` |
|---|---|---|
| an H2 url in configuration | replaced | replaced, no difference |
| a Testcontainers database | **kept** | **discarded, H2 used instead** |

> [!important] The default exists to protect exactly the case this note points toward. **Writing `ANY` opts out of that protection in exchange for nothing.**

## The two shapes, side by side

Against H2:

```groovy
1  // build.gradle
2  testImplementation 'com.h2database:h2'
```

```java
1  @DataJpaTest
2  @AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.ANY)
3  @Import(JpaAuditingConfig.class)
4  class ProductRepositoryTest {
5
6      @Autowired private TestEntityManager testEntityManager;
7      @Autowired private ProductRepository productRepository;
```

Against a real MySQL started for the run:

```groovy
1  // build.gradle
2  testImplementation 'org.springframework.boot:spring-boot-testcontainers'
3  testImplementation 'org.testcontainers:mysql'
4  testImplementation 'org.testcontainers:junit-jupiter'
```

```java
1  @DataJpaTest
2  @Import(JpaAuditingConfig.class)
3  @Testcontainers
4  class ProductRepositoryTest {
5
6      @Container
7      @ServiceConnection
8      static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:9.5");
9
10     @Autowired private TestEntityManager testEntityManager;
11     @Autowired private ProductRepository productRepository;
```

| | H2 | Testcontainers |
|---|---|---|
| `@AutoConfigureTestDatabase` | present, `ANY` | **absent** |
| the database | H2, from the classpath | MySQL, started for the run |
| added annotations | none | `@Testcontainers`, `@Container`, `@ServiceConnection` |

> [!important] **The `replace` line is deleted rather than changed.** Leaving the default is what allows the MySQL to survive.

> [!important] **`@ServiceConnection` does the real work.** It declares the container as the datasource, and marks the database as explicitly supplied so the default leaves it alone. Without it the url, username and password would have to be wired across by hand.

> [!warning] **`static` matters.** One database is started for the whole class. Non-static starts a fresh one per test method, which is slow enough to change how the suite feels.

> [!warning] Docker has to be running, which is the price of the second shape and the reason the first stays attractive for a fast local loop.

> [!info] Once the tests run on real MySQL, `flyway.enabled: false` and `ddl-auto: create-drop` are worth revisiting. Flyway can be turned **on**, and the tests then run against the schema the migrations actually build — which closes the gap this whole arrangement was working around.

> [!info] **Unverified** — the Testcontainers shape is from the Spring Boot and Testcontainers documentation and was not run, so the dependency coordinates need a build to confirm.

`@Import` brings in one configuration class, and the reason it is needed is worth its own section.

# The auditing problem

Three facts already established collide here, and the result is that nothing can be inserted at all.

**One.** A slice does not load your own `@Configuration` classes, and does not load the application class.

**Two.** Auditing is switched on by an annotation on that application class:

```java
1  // src/main/java/com/example/FakeCommerce/FakeCommerceApplication.java
2  @SpringBootApplication
3  @EnableJpaAuditing          // <- the problem
4  public class FakeCommerceApplication { }
```

**Three.** The audited column is mandatory:

```java
1  // src/main/java/com/example/FakeCommerce/schema/BaseEntity.java
2  @CreatedDate
3  @Column(name = "created_at", nullable = false, updatable = false)
4  private LocalDateTime createdAt;
```

Put those together. The slice never loads the application class, so `@EnableJpaAuditing` never takes effect, so nothing populates `createdAt`, so it reaches the database as null — into a column that forbids null.

> [!warning] **Every insert in every repository test fails**, including the ones in `@BeforeEach`, so no test reaches an assertion.

And the error names the wrong thing entirely:

```text
  could not execute statement
  NULL not allowed for column "CREATED_AT"
```

> [!warning] Nothing in that message mentions auditing, the annotation, or the application class not being loaded. The entity, the test data and the schema are all correct, and all three are where the search starts.

## The fix

Move the switch somewhere a test can reach:

```java
1  // src/main/java/com/example/FakeCommerce/config/JpaAuditingConfig.java
2  @Configuration
3  @EnableJpaAuditing
4  public class JpaAuditingConfig { }
```

Then remove `@EnableJpaAuditing` from the application class, and ask for the configuration by name in the test:

```java
1  @DataJpaTest
2  @Import(JpaAuditingConfig.class)
3  class ProductRepositoryTest {
```

> [!important] **`@Import` loads one named class on top of the slice.** Not a scan, not a package — one thing, requested explicitly.

> [!important] **Auditing still works in production**, because component scan finds `JpaAuditingConfig` like any other configuration class. Nothing about the running application changes.

> [!info] A second, identical configuration class under `src/test` is a common variant, with the test importing that one instead. It is unnecessary — importing the production `JpaAuditingConfig` works and has the advantage of exercising the real configuration rather than a copy that can drift away from it.

> [!important] The general lesson is worth more than the fix. **Anything switched on by an annotation on the application class is invisible to every slice test** — auditing, scheduling, caching, async. Each belongs in its own `@Configuration` so a test can request it, and the symptom when one does not is a failure that names something else.

# Getting data in

A `Product` object in Java is not a row. Between application code and the database sits a staging area, and JPA calls it the **persistence context**. The **entity manager** is the object that owns it.

```text
  your code  ->  entity manager  ->  [ persistence context ]  ->  database
                                      objects live here until
                                      something flushes them
```

Three operations do genuinely different things.

> [!important] **`persist(product)`** puts the object into the staging area and marks it new. **No SQL runs.** Nothing is in the database yet.

> [!important] **`flush()`** sends everything pending in the staging area to the database. **Now the `INSERT` runs.**

> [!important] **`clear()`** empties the staging area. The objects survive in your Java variables, but the entity manager has forgotten it was managing them.

> [!warning] **`clear` is the easiest to skip and matters most.** Without it the entities stay in the staging area, and a later `findById` may be answered from memory with no query ever running. **The test would pass without touching the database** — which is precisely the one thing a repository test exists to do.

Holding inserts back is deliberate: JPA collects changes so it can write them together, batching many inserts into one round trip and reordering them to satisfy foreign keys. None of that is possible if every `persist` went straight out.

> [!important] **`TestEntityManager`** is the wrapper the slice provides. `persistAndFlush(product)` is `persist` then `flush` in one call, because a test setting up rows always wants both.

> [!warning] **Do not arrange test data with the repository under test.** Calling `productRepository.save(...)` to set up rows means a broken `save` breaks the arrange step too, and the failure says nothing about which half is at fault. The entity manager gets rows in by a different route, so the setup stays independent of the thing being examined.

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

> [!important] **`@BeforeEach` runs before every test in the class.** 
> Where a service test arranges inside each method, a repository test usually needs the same rows every time — so the arrange step moves here and the tests themselves are act and assert only.

> [!info] `@AfterEach` is its counterpart. With `create-drop` it is rarely needed, since the schema is rebuilt anyway.

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
