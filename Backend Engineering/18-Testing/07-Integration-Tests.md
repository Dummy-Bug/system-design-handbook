Every test so far has been a unit test with something mocked out — the repository, the service, the database. The point of each was that only one thing was real. An integration test inverts that: nothing is mocked, and what is being checked is whether the pieces fit.

# What is being replaced

Without automation, testing a full flow means a person doing it.

```mermaid
flowchart LR
    C["A person, with Postman"] --> S["Server"]
    S --> D[("Production database")]
```

The automated version changes two things and nothing else:

```mermaid
flowchart LR
    T["A test script"] --> CO["Controller"]
    CO --> SE["Service"]
    SE --> RE["Repository"]
    RE --> H[("Test database — H2")]
```

> [!important] **The person becomes a script, and the real database becomes the test database.** Every layer in between runs for real. That is the entire idea, and everything below is mechanics.

> [!info] The script can be in any language — Python, JavaScript, Ruby — since it only makes HTTP calls. Writing it in Java keeps it in one ecosystem and one build, which is usually reason enough.

# `MockMvc` again, used differently

The controller test already had something that makes HTTP calls in Java.

> [!important] **The same `MockMvc`, with one change: the service is not mocked.** The controller calls the real service, which calls the real repository, which reaches H2. `MockMvc` is the entry point rather than the whole scope.

# The annotations

```java
1  @SpringBootTest(
2      webEnvironment = SpringBootTest.WebEnvironment.MOCK,
3      properties = { "spring.autoconfigure.exclude=..." }
4  )
5  @AutoConfigureMockMvc
6  public class EcomFlowIntegrationTest {
```

> [!important] **`@SpringBootTest` loads the entire application context** — every controller, service, repository and configuration. Not a slice. That is required, because the flow passes through all of them.

> [!important] **`webEnvironment = MOCK` means no real HTTP server.** The servlet environment is simulated, so nothing binds to port 8080 and the test cannot collide with a running application.

It is a choice among three, and the other two are worth knowing:

| Value | |
|---|---|
| **`MOCK`** | A simulated servlet environment, no port bound. What `MockMvc` needs |
| `NONE` | No web environment at all — for a context that has no web layer to exercise |
| `RANDOM_PORT` | **A real server on a free port.** Required when the test drives the application over actual HTTP with a real client |

> [!info] `RANDOM_PORT` rather than a fixed one because a fixed port is a machine-wide resource — two test runs, or a running application, would collide. The port chosen is injectable into the test so the client knows where to connect.

> [!warning] **`@AutoConfigureMockMvc` is easy to forget.** `@WebMvcTest` configures `MockMvc` for you; `@SpringBootTest` does not, because it has no idea you intend to make web calls. Without this line the `MockMvc` injection fails.

# What is still mocked, and why

Not everything can run for real.

```java
1  @Autowired
2  private ObjectMapper objectMapper;
3
4  @MockitoBean
5  private ProductRedisCache productRedisCache;
6
7  @BeforeEach
8  void setUp() {
9      when(productRedisCache.getSummary(anyLong())).thenReturn(Optional.empty());
10 }
```

> [!info] **`ObjectMapper` is injected rather than constructed** because it is a bean the context already provides, and because `ProductRedisCache` depends on one itself — the cache serialises what it stores. Taking the container's instance means the test serialises requests exactly the way the application does, rather than with a separately configured mapper that might differ on dates or nulls.

> [!important] **There is no test Redis, so the cache is mocked to always miss.** `Optional.empty()` is a cache miss, which sends every read down the path that queries the database — the path the test exists to exercise.

That is a deliberate choice with a clear justification:

> [!important] **Mocking the cache tests the slower, more interesting path every time.** A real cache would make the second request skip the database, so the test would exercise less on each run and depend on ordering. **Forcing a miss makes it deterministic.**

> [!info] The alternative is a test Redis instance, the same way H2 is a test database. Reasonable, and more setup — an embedded Redis or a container, plus flushing between runs. **Worth doing as an exercise**: stand one up, point the test configuration at it, drop the mock, and the cache path becomes real too. The interesting part is what it forces you to confront — that a cache which persists between tests makes them order-dependent unless something clears it.

## The exclusion list, and a bug in it

Alongside the mock, the source excludes Redis auto-configuration:

```java
1  properties = {
2      "spring.autoconfigure.exclude=" +
3          "org.springframeframework.boot.data.redis.autoconfigure.DataRedisAutoConfiguration," +
4          "org.springframework.boot.autoconfigure.data.redis.DataRedisReactiveAutoConfiguration," +
5          "org.springframework.boot.autoconfigure.data.redis.DataRedisRepositoriesAutoConfiguration"
6  }
```

> [!warning] **None of those three names is correct**, so nothing is excluded. Line 3 reads `springframeframework` — a typo. Lines 4 and 5 use the Spring Boot 3 package layout, `boot.autoconfigure.data.redis`, which does not exist in Boot 4.

Reading the class names straight out of `spring-boot-data-redis-4.0.2.jar`:

```text
  org/springframework/boot/data/redis/autoconfigure/DataRedisAutoConfiguration.class
  org/springframework/boot/data/redis/autoconfigure/DataRedisReactiveAutoConfiguration.class
  org/springframework/boot/data/redis/autoconfigure/DataRedisRepositoriesAutoConfiguration.class
```

So the working form is:

```java
1  "spring.autoconfigure.exclude=" +
2      "org.springframework.boot.data.redis.autoconfigure.DataRedisAutoConfiguration," +
3      "org.springframework.boot.data.redis.autoconfigure.DataRedisReactiveAutoConfiguration," +
4      "org.springframework.boot.data.redis.autoconfigure.DataRedisRepositoriesAutoConfiguration"
```

> [!warning] **The test passes either way**, which is why the bug survives. `@MockitoBean` replaces the cache regardless, and the Lettuce client connects lazily — so nothing ever reaches Redis and no connection is attempted. **A name that matches no class on the classpath is skipped rather than reported.**

> [!important] Which is the fourth instance of one shape in these notes, after the annotation that generated no index, `spring.redis.host`, and the text index that was never used. **Configuration that names something wrongly fails silently far more often than it fails loudly** — and the only way to know a setting works is to observe it doing something.

# The flow

One test, one journey, in order:

```mermaid
flowchart TB
    A["Create a category"] --> B["Retrieve it — verify"]
    B --> C["Create three products in it"]
    C --> D["Retrieve them — verify"]
    D --> E["Create an order with varying quantities"]
    E --> F["Retrieve the order — verify"]
    F --> G["Fetch the order summary"]
    G --> H["Update the order status"]
    H --> I["Fetch the summary again — verify the change"]
    I --> J["Delete order, products, category"]
```

> [!important] **Each step's output feeds the next.** The category id is read out of the creation response and used to create products; the product ids are used to build the order. That chaining is what makes it an integration test — a broken link anywhere fails the whole thing, which is exactly the failure unit tests structurally cannot see.

```java
1  private Long extractId(MvcResult result) throws Exception {
2      String json = result.getResponse().getContentAsString();
3      return ((Number) JsonPath.read(json, "$.data.id")).longValue();
4  }
```

> [!info] A small helper pulling the id out of each response. Its existence is a sign the test is doing the right thing — **reading what the API returned rather than assuming what the database assigned.**

> [!important] Ending with the deletions is deliberate. It **tests the delete endpoints** and leaves the database as it was found, so the test does not depend on running first or alone.

## Generating it, and reading what came back

A test of this shape is eleven near-identical `MockMvc` calls differing in verb, path and body — mechanical work of exactly the kind worth handing to an assistant. Two things about doing that are worth recording.

> [!important] **For anything this long, ask for the plan before the code.** A short prompt describing a nine-step journey leaves most of the decisions unstated; a planning pass turns it into an explicit list — create the category, verify by retrieval, create three products, and so on — that you read and correct **before** any code exists. The plan is largely the assistant expanding your prompt into the detailed one you should have written, and approving it is cheaper than reviewing the result.

> [!warning] Planning writes its working out to files as it goes. **Those belong in `.gitignore`.** They are scratch notes for one task, and committing them bloats the repository with documents nobody will read again.

And then read the output as a review, because a passing test is not evidence it tested what you meant:

> [!warning] **The first version created products by calling the service directly** rather than going through the controller, while using the controller for everything else. The test passed. It was also no longer end to end at that step — the layer under test had been skipped for convenience, which is precisely the thing an integration test exists to not do.

> [!info] Worth noting how it looked once corrected: the fix extracted a `createProduct` helper that goes through `MockMvc`, called three times. **A helper is not the same as a shortcut** — the distinction is whether it still passes through every layer, and that is what to check rather than the presence of a private method.

> [!info] **`MockMvc` is not the only way to drive this.** It calls into the application without going over the network, which keeps the test fast and in-process. The alternative is to start the application for real — `webEnvironment = RANDOM_PORT` — and hit it with an HTTP client: Spring's own `WebClient`, a library like Retrofit, a script in another language entirely, or, at most companies of any size, an internal library built for the purpose. **The choice of client changes nothing about the logic**: exercise the flow end to end, point it at a test database rather than a real one, and clean up whatever you created. What an external client buys you is that the network and the serialisation are real too; what it costs is a running application and a slower test.

# What this looks like at scale

The test above drives one Spring application through `MockMvc`. That is the small end of a range worth seeing the far end of, because the shape stays the same and only the surface area grows.

**A payments team at Google tested Google Pay this way.** The integration test began by starting **mobile simulators, one Android and one iOS**, because the application behaves differently across devices and operating systems — that half built and maintained by the mobile team rather than the backend one. From there the script ran the whole journey:

```mermaid
flowchart TB
    A["Start a simulator<br/>Android and iOS"] --> B["Boot the OS"]
    B --> C["Sign in with an account"]
    C --> D["Install the build about to go live"]
    D --> E["Set up a payments account<br/>against an internal fake bank"]
    E --> F["Send a payment to another fake account"]
    F --> G["Verify every step of the flow"]
```

> [!important] **The fake bank is the piece worth noticing.** A real payment cannot be part of an automated test, so the organisation built a bank internally — registered numbers, accounts, the lot — that behaves like the real one and moves no money. It is the same move as H2 standing in for MySQL, at the scale of an entire external institution.

> [!warning] **And manual testing continued regardless.** Google Pay is critical infrastructure in the Indian payments ecosystem, and no amount of automation was considered sufficient on its own. **An integration test suite reduces manual testing; on a system where being wrong is unacceptable, it does not replace it.**

The other end of the range is just as real. At a small startup, updating the integration tests was **not even mandatory** — the cost of maintaining them was judged higher than the risk they covered. Both positions are defensible, and which one applies is a question about consequences rather than about testing.

# Where each kind of test loads

The whole progression, in one place:

| | Loads | Real | Mocked |
|---|---|---|---|
| **`@ExtendWith(MockitoExtension)`** | **Nothing** | The service | Repository |
| **`@DataJpaTest`** | JPA slice | Repository, H2 | — |
| **`@WebMvcTest`** | Web slice | Controller, routing, JSON | Service |
| **`@SpringBootTest`** | **Everything** | **All layers, H2** | Only what cannot run |

> [!important] Reading down that table is reading the cost. **The first runs in milliseconds and the last takes seconds**, and the reason is exactly how much of Spring has to be built before anything is checked.

> [!important] Which is why the shape from `03-Beyond-Unit-Tests` holds: **many unit tests, few integration tests.** An integration test is worth having for each important journey and is the wrong tool for a branch, because it costs seconds to check something a unit test settles in a millisecond — and when it fails, it tells you the flow is broken without telling you where.
